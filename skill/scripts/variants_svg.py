"""Generate SVG variants from an XML template and typed, bounded parameters."""
import argparse
import copy
import json
import math
import re
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from check_svg import check

TOKEN = re.compile(r'\{\{([A-Za-z][A-Za-z0-9_]*)\}\}')
ET.register_namespace('', 'http://www.w3.org/2000/svg')


def generate(recipe_file, output):
    recipe_file, output = Path(recipe_file), Path(output)
    recipe = json.loads(recipe_file.read_text(encoding='utf-8-sig'))
    source = (recipe_file.parent / recipe['template']).read_text(encoding='utf-8-sig')
    if re.search(r'<!DOCTYPE|<!ENTITY', source, re.I):
        raise ValueError('DTD/entities unsupported')
    root = ET.fromstring(source)
    schema = recipe['parameters']
    if not schema or not recipe['variants']:
        raise ValueError('Provide parameters and explicit variants')
    used = set(TOKEN.findall(source))
    if used != set(schema):
        raise ValueError('Template parameters and schema must match')
    for node in root.iter():
        if TOKEN.search(node.get('id', '')):
            raise ValueError('Keep part IDs stable across variants')
    files = {}; manifest = []; filenames = set()
    with tempfile.TemporaryDirectory() as tmp:
        for variant in recipe['variants']:
            name, values = variant['name'], variant['values']
            if not isinstance(name,str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*', name) or name.casefold() in filenames or re.fullmatch(r'CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9]',name,re.I):
                raise ValueError('Use unique variant names')
            filenames.add(name.casefold())
            if set(values) != set(schema):
                raise ValueError('Each variant must provide every declared parameter')
            for key, rule in schema.items():
                value = values[key]
                if rule['type'] == 'number':
                    if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
                        raise ValueError(f'{key} must be finite numeric')
                    if not rule['min'] <= value <= rule['max']:
                        raise ValueError(f'{key} outside declared range')
                elif rule['type'] == 'choice':
                    if not isinstance(value, str) or value not in rule['values']:
                        raise ValueError(f'{key} outside declared choices')
                else:
                    raise ValueError('Parameter type must be number or choice')
            def substitute(text):
                return TOKEN.sub(lambda m: str(values[m[1]]), text) if text else text
            result = copy.deepcopy(root)
            for node in result.iter():
                node.attrib.update({k: substitute(v) for k, v in node.attrib.items()})
                node.text, node.tail = substitute(node.text), substitute(node.tail)
            candidate = Path(tmp) / (name + '.svg')
            ET.ElementTree(result).write(candidate, encoding='utf-8', xml_declaration=True)
            report = check(candidate)
            if not report['valid_structure']:
                raise ValueError(str(report['errors']))
            files[name] = candidate.read_bytes()
            manifest.append({'name': name, 'file': name+'.svg', 'values': values})
    output.mkdir()  # Exclusive; all variants validated before creating the batch.
    for name, data in files.items():
        (output/(name+'.svg')).write_bytes(data)
    (output/'variants.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('recipe', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(generate(args.recipe, args.output), ensure_ascii=False, indent=2))
    except (ValueError, OSError, KeyError, TypeError, ET.ParseError) as error:
        parser.exit(1, f'Variant generation failed: {error}\n')
