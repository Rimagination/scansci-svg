"""Check explicitly specified SVG edit-unit membership; does not infer anatomy."""
import argparse
import json
import xml.etree.ElementTree as ET
from check_svg import check


def check_units(path, units):
    structure = check(path)
    errors = list(structure['errors'])
    root = ET.parse(path).getroot()
    index = {n.get('id'): n for n in root.iter() if n.get('id')}
    if not units:
        errors.append('No edit units specified')
    for owner, members in units.items():
        group = index.get(owner)
        if group is None or group.tag != '{http://www.w3.org/2000/svg}g':
            errors.append(f'Missing group: {owner}')
            continue
        if not members:
            errors.append(f'Empty membership requirement: {owner}')
        descendants = {n.get('id') for n in group.iter() if n is not group}
        for member in members:
            if member not in descendants:
                errors.append(f'{member} must be inside {owner}')
    return {'passed': not errors, 'errors': errors,
            'unchecked': ['attachment geometry', 'biological ownership', 'editor import behavior']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('svg')
    parser.add_argument('--unit', action='append', required=True, help='group=member1,member2')
    args = parser.parse_args()
    try:
        units = {}
        for spec in args.unit:
            owner, members = spec.split('=', 1)
            if not owner or owner in units or not members or any(not m for m in members.split(',')):
                raise ValueError('Require distinct nonempty group=member1,member2 specifications')
            units[owner] = members.split(',')
        report = check_units(args.svg, units)
    except (OSError, ValueError, ET.ParseError) as exc:
        report = {'passed': False, 'errors': [str(exc)]}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report['passed'] else 1)
