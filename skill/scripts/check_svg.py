"""Dependency-free structural checks; not a sanitizer or visual/anatomical QA."""
import json
import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def check(path):
    source = Path(path).read_text(encoding="utf-8-sig")
    errors = []
    if re.search(r"<!DOCTYPE|<!ENTITY", source, re.I):
        raise ValueError("DTD/entity declarations are not allowed")
    root = ET.fromstring(source)
    ns = "{http://www.w3.org/2000/svg}"
    if root.tag != ns + "svg":
        errors.append("Missing SVG root namespace")
    try:
        box = [float(v) for v in re.split(r"[\s,]+", root.get("viewBox", "").strip())]
        if len(box) != 4 or not all(map(math.isfinite, box)) or box[2] <= 0 or box[3] <= 0:
            raise ValueError()
    except ValueError:
        errors.append("Invalid viewBox")
    ids, refs, groups, paths = set(), set(), 0, 0
    for node in root.iter():
        tag = node.tag.removeprefix(ns)
        if tag in {"image", "script", "foreignObject", "animate", "animateTransform", "set"}:
            errors.append(f"Unsupported element: {tag}")
        ident = node.get("id")
        if ident:
            if ident in ids:
                errors.append(f"Duplicate ID: {ident}")
            ids.add(ident)
        groups += tag == "g" and bool(ident)
        paths += tag == "path"
        for key, value in node.attrib.items():
            local = key.rsplit("}", 1)[-1]
            if local.lower().startswith("on"):
                errors.append(f"Event handler: {local}")
            if local == "href":
                if not value.startswith("#"):
                    errors.append("External/embedded href")
                else:
                    refs.add(value[1:])
            for match in re.finditer(r"url\((.*?)\)", value, re.I):
                target = match[1].strip(" \t\"'")
                if not target.startswith("#"):
                    errors.append("External URL reference")
                else:
                    refs.add(target[1:])
    if not groups:
        errors.append("No named editable group")
    if not any(n.tag.removeprefix(ns) in {"path", "rect", "circle", "ellipse", "line", "polyline", "polygon", "text"} for n in root.iter()):
        errors.append("No drawable elements")
    for missing in sorted(refs - ids):
        errors.append(f"Unresolved local reference: {missing}")
    return {"file": str(path), "valid_structure": not errors, "named_groups": groups,
            "paths": paths, "errors": errors,
            "unchecked": ["rendered transparency", "visual fidelity", "anatomy", "complete SVG safety"]}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python check_svg.py drawing.svg")
    try:
        result = check(sys.argv[1])
    except (OSError, ValueError, ET.ParseError) as exc:
        print(json.dumps({"valid_structure": False, "error": str(exc)}, ensure_ascii=True))
        raise SystemExit(1)
    print(json.dumps(result, ensure_ascii=True, indent=2))
    raise SystemExit(0 if result["valid_structure"] else 1)
