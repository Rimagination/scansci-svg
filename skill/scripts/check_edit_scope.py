"""Conservative source-scope comparison, NOT visual/anatomical acceptance or a sanitizer."""
import argparse
import json
import re
import xml.etree.ElementTree as ET
from check_svg import check

NS = '{http://www.w3.org/2000/svg}'


def signature(node, allowed=(), preserve_text=False):
    if node.get('id') in allowed:
        return ('allowed-slot', node.tag, node.get('id'))
    preserve_text = preserve_text or node.tag in {NS+'text', NS+'tspan', NS+'textPath'}
    preserve_text = preserve_text or node.get('{http://www.w3.org/XML/1998/namespace}space') == 'preserve'
    def text(value):
        return value if preserve_text or (value and value.strip()) else None
    return (node.tag, tuple(sorted(node.attrib.items())), text(node.text),
            tuple((signature(c, allowed, preserve_text), text(c.tail)) for c in node))


def compare(before, after, allowed):
    result = {'scope_check_passed': False, 'target_verified': None,
              'target_changed': {}, 'issues': [],
              'unchecked': ['target correctness', 'rendered appearance/alpha', 'anatomy', 'complete SVG safety']}
    try:
        for path in (before, after):
            checked = check(path)
            if not checked['valid_structure']:
                result['issues'].extend(checked['errors'])
                return result
        roots = [ET.parse(p).getroot() for p in (before, after)]
        indexes = [{n.get('id'): n for n in root.iter() if n.get('id')} for root in roots]
        if not allowed or len(set(allowed)) != len(allowed):
            raise ValueError('Supply one or more distinct --allow IDs')
        for ident in allowed:
            if any(ident not in index for index in indexes):
                raise ValueError(f'Allowed ID missing: {ident}')
            for root, index in zip(roots, indexes):
                node = index[ident]
                if node is root or node.tag in {NS+'defs', NS+'style'}:
                    raise ValueError('Cannot exempt root, defs or style')
                if any(n is not node and n.get('id') in allowed for n in node.iter()):
                    raise ValueError('Nested allowed IDs are ambiguous; select the smallest scopes')
            result['target_changed'][ident] = signature(indexes[0][ident]) != signature(indexes[1][ident])
        result['protected_source_unchanged'] = signature(roots[0], allowed) == signature(roots[1], allowed)
        if not result['protected_source_unchanged']:
            result['issues'].append('Protected source changed (including ancestor attributes/order/text)')
        # Shared definitions/styles stay protected even inside an allowed subtree.
        shared = [[signature(n) for n in r.iter() if n.tag in {NS+'defs', NS+'style'}] for r in roots]
        if shared[0] != shared[1]:
            result['issues'].append('Shared defs/style changed; requires explicit dependency review')
        if any(result['target_changed'].values()):
            for root, index in zip(roots, indexes):
                local_nodes = {n for ident in allowed for n in index[ident].iter()}
                local_ids = {n.get('id') for n in local_nodes if n.get('id')}
                if any(n.tag == NS+'style' for n in root.iter()):
                    result['issues'].append('CSS may couple objects; rendered dependency review required')
                for n in root.iter():
                    if n in local_nodes:
                        continue
                    for key, value in n.attrib.items():
                        refs = set(re.findall(r'url\(\s*[\"\x27]?#([^\s)\"\x27]+)', value))
                        if key.rsplit('}', 1)[-1] == 'href' and value.startswith('#'):
                            refs.add(value[1:])
                        if refs & local_ids:
                            result['issues'].append('Protected object references allowed subtree; dependency review required')
        result['issues'] = list(dict.fromkeys(result['issues']))
        result['scope_check_passed'] = not result['issues']
    except (OSError, ValueError, ET.ParseError) as exc:
        result['issues'].append(str(exc))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('before')
    parser.add_argument('after')
    parser.add_argument('--allow', action='append', required=True, help='ID of a permitted local-edit subtree')
    args = parser.parse_args()
    report = compare(args.before, args.after, args.allow)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report['scope_check_passed'] else 1)
