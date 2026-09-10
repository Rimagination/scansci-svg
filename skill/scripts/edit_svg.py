"""Apply explicit local SVG edits by ID, preserving the source and checking scope."""
import argparse
import json
import re
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from check_edit_scope import compare, NS

ET.register_namespace('', NS[1:-1])
ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')
ATTRIBUTES = {'fill', 'stroke', 'stroke-width', 'opacity', 'fill-opacity', 'stroke-opacity',
              'transform', 'x', 'y', 'dx', 'dy', 'font-size', 'font-family', 'font-weight', 'text-anchor'}


def edit(source, edits, output):
    source, output = Path(source), Path(output)
    if output.exists():
        raise FileExistsError(output)
    if not isinstance(edits, list) or not edits:
        raise ValueError('Provide a nonempty edits list')
    # Read-only XML parse; source/output validation and dependency checks are shared with compare.
    tree = ET.parse(source)
    index = {n.get('id'): n for n in tree.getroot().iter() if n.get('id')}
    allowed = []
    for change in edits:
        if not isinstance(change, dict) or set(change) - {'id', 'attributes', 'text'}:
            raise ValueError('Each edit accepts id, attributes and/or text')
        ident = change.get('id')
        if not isinstance(ident, str) or ident not in index:
            raise ValueError(f'Unknown target ID: {ident}')
        node = index[ident]
        attrs = change.get('attributes', {})
        if not isinstance(attrs, dict) or not all(k in ATTRIBUTES and isinstance(v, str) for k, v in attrs.items()):
            raise ValueError('Use supported attribute names and string values')
        if not attrs and 'text' not in change:
            raise ValueError(f'Empty edit: {ident}')
        inline = re.sub(r'/\*.*?\*/', '', node.get('style', ''), flags=re.S)
        properties = set(re.findall(r'(?:^|;)\s*([\w-]+)\s*:', inline.lower()))
        conflicts = set(attrs) & properties
        if 'all' in properties:
            conflicts.update(attrs)
        if 'font' in properties:
            conflicts.update(k for k in attrs if k.startswith('font-'))
        if conflicts:
            raise ValueError('Inline style overrides ' + ', '.join(sorted(conflicts)) + '; edit those declarations in the source')
        if 'text' in change:
            if node.tag not in {NS+'text', NS+'tspan', NS+'title', NS+'desc'} or len(node) or not isinstance(change['text'], str):
                raise ValueError('Text edits require a leaf text/tspan/title/desc node; retain nested text in the source editor')
            node.text = change['text']
        node.attrib.update(attrs)
        allowed.append(ident)
    with tempfile.TemporaryDirectory() as folder:
        candidate = Path(folder) / 'candidate.svg'
        tree.write(candidate, encoding='utf-8', xml_declaration=True)
        result = compare(source, candidate, allowed)
        if not result['scope_check_passed']:
            raise ValueError('; '.join(result['issues']))
        data = candidate.read_bytes()
    with output.open('xb') as stream:
        stream.write(data)
    return {'file': str(output), **result}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('edits', type=Path, help='JSON array of edits by ID')
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    try:
        changes = json.loads(args.edits.read_text(encoding='utf-8-sig'))
        print(json.dumps(edit(args.source, changes, args.output), ensure_ascii=False, indent=2))
    except (OSError, ValueError, TypeError, ET.ParseError) as error:
        parser.exit(1, f'Edit failed: {error}\n')
