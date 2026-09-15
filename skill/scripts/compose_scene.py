"""Find packaged components and assemble editable SVG scenes from a local recipe."""
import argparse
import copy
import json
import math
import re
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from check_svg import check
from compose_svg import NS, isolate, number

N = "{" + NS + "}"
SKILL = Path(__file__).resolve().parents[1]


def components(skill_root=SKILL):
    """Read component metadata from existing asset catalogs; no second registry."""
    result = {}
    for catalog in sorted(Path(skill_root).glob("assets/*/catalog.json")):
        for asset in json.loads(catalog.read_text(encoding="utf-8-sig")):
            for component in asset.get("components", []):
                ident = component["id"]
                if ident in result:
                    raise ValueError(f"Duplicate component: {ident}")
                source = (catalog.parent / asset["file"]).resolve()
                if not source.is_relative_to(Path(skill_root).resolve()):
                    raise ValueError(f"Packaged source outside skill: {source}")
                result[ident] = dict(component, source=source, asset=asset)
    return result


def find_components(query, skill_root=SKILL):
    terms = query.casefold().split()
    matches = []
    for ident, item in components(skill_root).items():
        if all(term in json.dumps(item, ensure_ascii=False, default=str).casefold() for term in terms):
            match = {key: item[key] for key in
                     ("id", "label", "selector", "bounds", "anchors", "view", "style", "scenes")}
            match.update(file=str(item["source"]), description=item["asset"].get("description", ""),
                         source_url=item["asset"].get("source_url", ""),
                         author=item["asset"].get("author", ""), license=item["asset"].get("license", ""))
            matches.append(match)
    return matches


def read_svg(path):
    result = check(path)
    if not result["valid_structure"]:
        raise ValueError(f"{path}: {result['errors']}")
    return ET.parse(path).getroot()


def select_component(root, selector):
    if selector is None:
        return copy.deepcopy(root)
    matches = [node for node in root.iter() if node.get("id") == selector]
    if len(matches) != 1 or matches[0].tag != N + "g":
        raise ValueError(f"Component selector must name one group: {selector}")
    parents = {child: parent for parent in root.iter() for child in parent}
    ancestors = set()
    ancestor = matches[0]
    while ancestor in parents:
        ancestor = parents[ancestor]
        ancestors.add(ancestor)

    def keep(node):
        if node.get("id") == selector or node.tag in {N + "defs", N + "title", N + "desc"}:
            return copy.deepcopy(node)
        children = [part for child in node if (part := keep(child)) is not None]
        if children:
            saved = ET.Element(node.tag, node.attrib)
            # A retained resource container is not the removed visible object.
            # Do not let href resolve to a now-empty sibling with the same ID.
            if node not in ancestors:
                saved.attrib.pop("id", None)
            saved.extend(children)
            return saved
        return None

    # Preserve ancestor transforms/styles and definitions in their original context.
    # ponytail: sibling artwork used via href must first be placed in defs; do not
    # guess a dependency's rendering context by moving arbitrary visible siblings.
    return keep(root)


def pair(value):
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError("Coordinates must be a two-number array")
    return [number(v) for v in value]


def name(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", value):
        raise ValueError("Object IDs must be ASCII names starting with a letter")
    return value


IDENTITY = (1, 0, 0, 1, 0, 0)


def multiply(left, right):
    a, b, c, d, e, f = left
    g, h, i, j, k, l = right
    return tuple(number(v) for v in (a*g+c*h, b*g+d*h, a*i+c*j, b*i+d*j,
                                      a*k+c*l+e, b*k+d*l+f))


def transform_matrix(value):
    """SVG attribute transforms only; CSS transforms need prior normalization."""
    matrix, end = IDENTITY, 0
    numeric = r"[+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?"
    for match in re.finditer(r"([A-Za-z]+)\s*\(([^()]*)\)", value):
        if value[end:match.start()].strip(' ,\t\r\n'):
            raise ValueError(f"Unsupported transform: {value}")
        args, cursor = [], 0
        for token in re.finditer(numeric, match[2]):
            if match[2][cursor:token.start()].strip(' ,\t\r\n'):
                raise ValueError(f"Invalid transform arguments: {value}")
            args.append(number(token[0])); cursor = token.end()
        if match[2][cursor:].strip(' ,\t\r\n'):
            raise ValueError(f"Invalid transform arguments: {value}")
        kind = match[1]
        if kind == 'matrix' and len(args) == 6:
            local = tuple(args)
        elif kind == 'translate' and len(args) in {1, 2}:
            local = (1, 0, 0, 1, args[0], args[1] if len(args) == 2 else 0)
        elif kind == 'scale' and len(args) in {1, 2}:
            local = (args[0], 0, 0, args[-1], 0, 0)
        elif kind == 'rotate' and len(args) in {1, 3}:
            angle = math.radians(args[0]); c, s = math.cos(angle), math.sin(angle)
            local = (c, s, -s, c, 0, 0)
            if len(args) == 3:
                x, y = args[1:]
                local = multiply(multiply((1, 0, 0, 1, x, y), local), (1, 0, 0, 1, -x, -y))
        elif kind in {'skewX', 'skewY'} and len(args) == 1:
            t = number(math.tan(math.radians(args[0])))
            local = (1, 0, t, 1, 0, 0) if kind == 'skewX' else (1, t, 0, 1, 0, 0)
        else:
            raise ValueError(f"Unsupported transform: {value}")
        matrix = multiply(matrix, local); end = match.end()
    if value[end:].strip(' ,\t\r\n'):
        raise ValueError(f"Unsupported transform: {value}")
    return matrix


def to_root(node, parents, root):
    matrix = IDENTITY
    while node is not root:
        if node.tag != N + 'g':
            raise ValueError('Normalize nested template viewports to groups before linking objects')
        style = re.sub(r'/\*.*?\*/', '', node.get('style', ''), flags=re.S)
        if any(key in node.attrib for key in ('transform-origin', 'transform-box')) or re.search(
                r'(?:^|;)\s*(?:all|(?:-webkit-)?transform(?:-origin|-box)?|translate|rotate|scale)\s*:', style, re.I):
            raise ValueError('Normalize CSS transforms to SVG attributes before linking objects')
        matrix = multiply(transform_matrix(node.get('transform', '')), matrix)
        node = parents[node]
    return matrix


def map_point(matrix, point):
    a, b, c, d, e, f = matrix
    x, y = point
    return [number(a*x+c*y+e), number(b*x+d*y+f)]


def inverse(matrix):
    a, b, c, d, e, f = matrix
    determinant = number(a*d-b*c)
    if determinant == 0:
        raise ValueError('Connection coordinates require an invertible parent transform')
    return tuple(number(v) for v in (d/determinant, -b/determinant, -c/determinant,
                                    a/determinant, (c*f-d*e)/determinant, (b*e-a*f)/determinant))


def insert(root, node, template):
    ident = node.get('id')
    slots = [n for n in root.iter() if n.get('id') == ident]
    if slots:
        slot = slots[0]
        if slot.tag != N + 'g' or len(slot) or (slot.text or '').strip() or set(slot.attrib) != {'id'}:
            raise ValueError(f'{ident}: template slot must be an empty group with only an id')
        parent = next(n for n in root.iter() if slot in list(n))
        position = list(parent).index(slot)
        parent.remove(slot); parent.insert(position, node)
    elif template:
        raise ValueError(f'Missing template slot: {ident}')
    else:
        root.append(node)


def add_connections(root, recipe, instances, catalog):
    connections = recipe.get('connections', [])
    if not isinstance(connections, list):
        raise ValueError('Connections must be a list')
    used = set(instances)
    for spec in connections:
        ident = name(spec['id'])
        if ident in used:
            raise ValueError(f'Duplicate object/connection ID: {ident}')
        used.add(ident)
        group = ET.Element(N + 'g', {'id': ident})
        insert(root, group, 'template' in recipe)
        parents = {child: parent for parent in root.iter() for child in parent}
        into_link = inverse(to_root(group, parents, root))

        def endpoint(endpoint_spec):
            object_id = endpoint_spec['object']
            if object_id not in instances:
                raise ValueError(f'Unknown endpoint object: {object_id}')
            node, object_spec = instances[object_id]
            item = catalog[object_spec['component']]
            if ('point' in endpoint_spec) == ('anchor' in endpoint_spec):
                raise ValueError('Each endpoint needs exactly one source point or named anchor')
            point = pair(endpoint_spec['point'] if 'point' in endpoint_spec else item['anchors'][endpoint_spec['anchor']])
            geometry = node.find("./*[@id='" + object_id + "-geometry']")
            matrix = multiply(into_link, to_root(geometry, parents, root))
            return map_point(matrix, point)

        start, finish = endpoint(spec['from']), endpoint(spec['to'])
        group.set('data-from', spec['from']['object']); group.set('data-to', spec['to']['object'])
        # Keep the explicit endpoint binding with the editable relation.
        ET.SubElement(group, N + 'desc').text = json.dumps({'from': spec['from'], 'to': spec['to']}, ensure_ascii=False)
        sx, sy = start; tx, ty = finish
        route = spec.get('route', 'straight')
        if route == 'straight':
            points = [start, finish]
        elif route == 'horizontal':
            mid = (sx+tx)/2
            points = [start, [mid, sy], [mid, ty], finish]
        elif route == 'vertical':
            mid = (sy+ty)/2
            points = [start, [sx, mid], [tx, mid], finish]
        else:
            raise ValueError('Connection route must be straight, horizontal, or vertical')
        # Consecutive zero-length segments make arrow orientation ambiguous.
        points = [p for i, p in enumerate(points) if i == 0 or p != points[i-1]]
        if len(points) < 2:
            raise ValueError('Connection endpoints coincide; choose distinct attachment points')
        color = spec.get('color', '#527567')
        if not isinstance(color, str) or not re.fullmatch(r'#[0-9a-fA-F]{6}', color):
            raise ValueError('Connection color must be a six-digit hex color')
        arrow = spec.get('arrow', 'none')
        if arrow not in {'none', 'end', 'both'}:
            raise ValueError('Connection arrow must be none, end, or both')
        attrs = {'id': ident + '-line', 'points': ' '.join(f'{x:.12g},{y:.12g}' for x, y in points),
                 'fill': 'none', 'stroke': color, 'stroke-width': f"{number(spec.get('stroke_width', 2), True):g}",
                 'stroke-linejoin': 'round'}
        if arrow != 'none':
            defs = ET.SubElement(group, N + 'defs')
            marker = ET.SubElement(defs, N + 'marker', {'id': ident + '-arrow', 'viewBox': '0 0 10 10',
                'refX': '10', 'refY': '5', 'markerWidth': '5', 'markerHeight': '5', 'orient': 'auto-start-reverse'})
            ET.SubElement(marker, N + 'path', {'d': 'M0 0L10 5L0 10Z', 'fill': color})
            attrs['marker-end'] = f'url(#{ident}-arrow)'
            if arrow == 'both':
                attrs['marker-start'] = f'url(#{ident}-arrow)'
        ET.SubElement(group, N + 'polyline', attrs)
        if 'label' in spec:
            label = spec['label']; dx, dy = pair(label.get('offset', [0, -12]))
            ET.SubElement(group, N + 'text', {'id': ident + '-label',
                'x': f'{(sx+tx)/2+dx:.12g}', 'y': f'{(sy+ty)/2+dy:.12g}', 'text-anchor': 'middle',
                'font-family': 'Arial, Microsoft YaHei, sans-serif', 'font-size': f"{number(label.get('size', 16), True):g}",
                'fill': color}).text = str(label['text'])


def instance(spec, item):
    ident = name(spec["id"])
    bounds = item["bounds"]
    if not isinstance(bounds, list) or len(bounds) != 4:
        raise ValueError(f"Component {item['id']} needs bounds [x,y,width,height]")
    bx, by = (number(v) for v in bounds[:2])
    bw, _ = (number(v, True) for v in bounds[2:])
    anchor = spec.get("anchor", "top-left")
    ax, ay = [bx, by] if anchor == "top-left" else pair(item["anchors"][anchor])
    x, y = pair(spec["at"])
    scale = number(spec["width"], True) / bw
    opacity = number(spec.get("opacity", 1))
    if not 0 <= opacity <= 1:
        raise ValueError("Opacity must be between zero and one")
    source = select_component(read_svg(item["source"]), item.get("selector"))
    if any(key in source.attrib for key in ('transform', 'transform-origin', 'transform-box')) or re.search(
            r"(?:^|;)\s*(?:(?:-webkit-)?transform(?:-origin|-box)?|translate|rotate|scale|all|(?:min-|max-)?(?:width|height|inline-size|block-size)|x|y)\s*:",
            re.sub(r'/\*.*?\*/', '', source.get("style", ""), flags=re.S), re.I):
        raise ValueError("Normalize source root transforms and viewport styles before measuring bounds")
    try:
        isolate(source, ident + "--")
    except KeyError as error:
        raise ValueError(f"{ident}: selected group references a removed sibling {error}; prepare its definitions first") from error
    box = [number(v) for v in re.split(r"[\s,]+", source.get("viewBox").strip())]
    # A nested viewport with a 1:1 viewBox mapping retains percentage geometry.
    for key, value in zip(("x", "y", "width", "height"), box):
        source.set(key, f"{value:.12g}")
    source.set("preserveAspectRatio", "xMidYMid meet")
    owner = ET.Element(N + "g", {
        "id": ident, "data-component": item["id"], "data-asset": item["asset"]["id"],
        "data-label": str(spec.get("label", item["label"])),
        "data-anchor": anchor, "transform": f"translate({x:.12g} {y:.12g})",
    })
    provenance = {key: item["asset"].get(key, "") for key in
                  ("id", "title", "author", "license", "source_url", "description")}
    ET.SubElement(owner, N + "desc").text = json.dumps(provenance, ensure_ascii=False)
    geometry = ET.SubElement(owner, N + "g", {
        "id": ident + "-geometry", "opacity": f"{opacity:g}",
        "transform": f"scale({scale:.12g}) translate({-ax:.12g} {-ay:.12g})",
    })
    geometry.append(source)
    for ordinal, label in enumerate(spec.get("labels", []), 1):
        annotation = ET.SubElement(owner, N + "g", {"id": f"{ident}-annotation-{ordinal}"})
        if "leader" in label:
            points = [pair(point) for point in label["leader"]]
            if len(points) < 2:
                raise ValueError("A label leader needs at least two points")
            ET.SubElement(annotation, N + "polyline", {
                "points": " ".join(f"{a:g},{b:g}" for a, b in points),
                "fill": "none", "stroke": "#9cac97", "stroke-width": "1.3",
            })
        lx, ly = pair(label["at"])
        align = label.get("align", "start")
        if align not in {"start", "middle", "end"}:
            raise ValueError("Label align must be start, middle, or end")
        ET.SubElement(annotation, N + "text", {
            "id": f"{ident}-label-{ordinal}", "x": f"{lx:g}", "y": f"{ly:g}",
            "font-size": f"{number(label.get('size', 16), True):g}", "text-anchor": align,
            "font-family": "Arial, Microsoft YaHei, sans-serif", "fill": "#506c5c",
        }).text = str(label["text"])
    return owner


def compose_scene(recipe_file, output_file, skill_root=SKILL):
    recipe_file, output_file = Path(recipe_file), Path(output_file)
    if output_file.exists():
        raise FileExistsError(output_file)
    recipe = json.loads(recipe_file.read_text(encoding="utf-8-sig"))
    catalog = components(skill_root)
    if "template" in recipe:
        root = read_svg(recipe_file.parent / recipe["template"])
        # Catch stylesheets and malformed ARIA references without renaming IDs.
        isolate(root, "")
    else:
        width, height = (number(recipe[key], True) for key in ("width", "height"))
        root = ET.Element(N + "svg", {"viewBox": f"0 0 {width:g} {height:g}",
                                     "width": f"{width:g}", "height": f"{height:g}"})
        ET.SubElement(root, N + "title").text = str(recipe.get("title", "Composed scene"))
    objects = recipe["objects"]
    if not isinstance(objects, list) or not objects:
        raise ValueError("Provide at least one scene object")
    instances = {}
    for spec in objects:
        ident = name(spec["id"])
        if ident in instances:
            raise ValueError(f"Duplicate object ID: {ident}")
        node = instance(spec, catalog[spec["component"]])
        insert(root, node, 'template' in recipe)
        instances[ident] = node, spec
    add_connections(root, recipe, instances, catalog)
    data = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    with tempfile.TemporaryDirectory() as temp:
        candidate = Path(temp) / "scene.svg"
        candidate.write_bytes(data)
        read_svg(candidate)
    with output_file.open("xb") as stream:
        stream.write(data)
    return output_file


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("recipe", type=Path, nargs="?")
    parser.add_argument("output", type=Path, nargs="?")
    parser.add_argument("--find", metavar="WORDS", help="Search indexed components; use an empty string to list all")
    args = parser.parse_args()
    try:
        if args.find is not None:
            if args.recipe or args.output:
                parser.error("Use --find without recipe/output")
            print(json.dumps(find_components(args.find), ensure_ascii=True, indent=2))
        else:
            if args.recipe is None or args.output is None:
                parser.error("Provide recipe and output")
            print(compose_scene(args.recipe, args.output))
    except (OSError, ValueError, KeyError, TypeError, ET.ParseError) as error:
        parser.exit(1, f"Scene composition failed: {error}\n")
