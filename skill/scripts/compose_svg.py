"""Assemble local, reviewed SVGs into editable panels using Python's stdlib."""
import argparse
import json
import math
import re
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from check_svg import check

NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)
ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")
URL = re.compile(r"url\(\s*(['\"]?)#([^\s)'\"]+)\1\s*\)", re.I)


def number(value, positive=False):
    if isinstance(value, bool):
        raise ValueError("Coordinates must be numbers")
    value = float(value)
    if not math.isfinite(value) or (positive and value <= 0):
        raise ValueError("Dimensions must be positive; coordinates must be finite")
    return value


def isolate(root, prefix):
    """Rewrite references without treating hex colors as ID references."""
    names = {node.get("id"): prefix + node.get("id")
             for node in root.iter() if node.get("id")}
    for node in root.iter():
        if node.tag == f"{{{NS}}}style":
            raise ValueError("Resolve stylesheet rules to element styles before composition")
        for key, value in list(node.attrib.items()):
            local = key.rsplit("}", 1)[-1]
            if local == "id":
                value = names[value]
            elif local == "href" and value.startswith("#"):
                value = "#" + names[value[1:]]
            elif local in {"aria-labelledby", "aria-describedby"}:
                value = " ".join(names[token] for token in value.split())
            else:
                value = URL.sub(lambda match: "url(#" + names[match[2]] + ")", value)
            node.set(key, value)


def compose(layout_file, output_file):
    layout_file, output_file = Path(layout_file), Path(output_file)
    layout = json.loads(layout_file.read_text(encoding="utf-8-sig"))
    width, height = (number(layout[key], True) for key in ("width", "height"))
    panels = layout["panels"]
    if not isinstance(panels, list) or not panels:
        raise ValueError("Provide at least one panel")
    root = ET.Element(f"{{{NS}}}svg", {
        "width": f"{width:g}", "height": f"{height:g}",
        "viewBox": f"0 0 {width:g} {height:g}",
    })
    if 'width_mm' in layout:
        physical_width = number(layout['width_mm'], True)
        root.set('width', f'{physical_width:g}mm')
        root.set('height', f'{physical_width * height / width:g}mm')
    ET.SubElement(root, f"{{{NS}}}title").text = str(layout.get("title", "Scientific figure"))
    used = set()
    for panel in panels:
        ident = panel["id"]
        if not isinstance(ident, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", ident) or ident in used:
            raise ValueError("Panel IDs must be unique ASCII names starting with a letter")
        used.add(ident)
        x, y = (number(panel[key]) for key in ("x", "y"))
        pw, ph = (number(panel[key], True) for key in ("width", "height"))
        if x < 0 or y < 0 or x + pw > width or y + ph > height:
            raise ValueError(f"Panel {ident} extends outside the canvas")
        source = layout_file.parent / panel["file"]
        result = check(source)
        if not result["valid_structure"]:
            raise ValueError(f"{source}: {result['errors']}")
        node = ET.parse(source).getroot()
        if re.search(r"(?:^|;)\s*(?:(?:min-|max-)?(?:width|height)|x|y)\s*:", node.get("style", ""), re.I):
            raise ValueError("Move root viewport dimensions from inline style to SVG attributes before composition")
        isolate(node, f"panel-{ident}--")
        # Keep the source coordinate system, inherited styles, and defs intact.
        for key, value in {"x": x, "y": y, "width": pw, "height": ph}.items():
            node.set(key, f"{value:g}")
        node.set("preserveAspectRatio", "xMidYMid meet")
        group = ET.SubElement(root, f"{{{NS}}}g", {"id": f"panel-{ident}"})
        group.append(node)
    labels = ET.SubElement(root, f"{{{NS}}}g", {
        "id": "figure-labels", "font-family": "Arial, Microsoft YaHei, sans-serif", "fill": "#243e42",
    })
    for ordinal, label in enumerate(layout.get("labels", []), 1):
        attrs = {key: f"{number(label[key]):g}" for key in ("x", "y")}
        ident = label.get("id", f"figure-label-{ordinal}")
        if not isinstance(ident, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", ident):
            raise ValueError("Label IDs must be ASCII names starting with a letter")
        attrs["id"] = ident
        attrs["font-size"] = f"{number(label.get('size', 18), True):g}"
        ET.SubElement(labels, f"{{{NS}}}text", attrs).text = str(label["text"])
    data = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    # Validate combined IDs/references before creating the requested output.
    with tempfile.TemporaryDirectory() as temp:
        candidate = Path(temp) / "figure.svg"
        candidate.write_bytes(data)
        result = check(candidate)
        if not result["valid_structure"]:
            raise ValueError(str(result["errors"]))
    with output_file.open("xb") as stream:
        stream.write(data)
    return output_file


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("layout", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    try:
        print(compose(args.layout, args.output))
    except (OSError, ValueError, KeyError, TypeError, ET.ParseError) as error:
        parser.exit(1, f"Composition failed: {error}\n")
