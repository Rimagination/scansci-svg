"""Trace a raster or an already isolated part with the optional VTracer backend."""
import argparse
from datetime import datetime, timezone
from importlib.metadata import version
import json
from pathlib import Path
import re
import tempfile
import time
import xml.etree.ElementTree as ET

from check_svg import check

NS = '{http://www.w3.org/2000/svg}'
ET.register_namespace('', NS[1:-1])


def trace(source, output, *, group_id='trace', colormode='color', mode='spline',
          filter_speckle=4, color_precision=6, layer_difference=16):
    started_at = datetime.now(timezone.utc).isoformat()
    start = time.perf_counter()
    source, output = Path(source).resolve(), Path(output).resolve()
    if not source.is_file():
        raise ValueError(f'Input image not found: {source}')
    if output.exists():
        raise FileExistsError(f'Choose a new SVG output; existing file retained: {output}')
    if output.suffix.lower() != '.svg':
        raise ValueError('Output filename must end in .svg')
    if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_.-]*', group_id):
        raise ValueError('group_id must start with a letter/underscore and use letters, digits, _, . or -')
    if colormode not in {'color', 'binary'} or mode not in {'spline', 'polygon', 'none'}:
        raise ValueError('Choose colormode color/binary and mode spline/polygon/none')
    for name, value, lower, upper in [('filter_speckle', filter_speckle, 0, 128),
                                     ('color_precision', color_precision, 1, 8),
                                     ('layer_difference', layer_difference, 0, 255)]:
        if type(value) is not int or not lower <= value <= upper:
            raise ValueError(f'{name} must be an integer in {lower}..{upper}')
    try:
        from PIL import Image, ImageOps
        import vtracer
    except ImportError as exc:
        raise ValueError('Install optional tracing dependencies in this Python environment: '
                         'python -m pip install Pillow vtracer==0.6.15') from exc
    if not callable(getattr(vtracer, 'convert_image_to_svg_py', None)):
        raise ValueError('This entry uses convert_image_to_svg_py; tested backend: vtracer==0.6.15')

    params = dict(colormode=colormode, hierarchical='stacked', mode=mode,
                  filter_speckle=filter_speckle, color_precision=color_precision,
                  layer_difference=layer_difference, corner_threshold=60,
                  length_threshold=4.0, max_iterations=10, splice_threshold=45, path_precision=3)
    with Image.open(source) as image:
        if getattr(image, 'n_frames', 1) > 1:
            raise ValueError('Select one frame/page before tracing a multi-frame image')
        input_size = image.size
        orientation = image.getexif().get(274, 1)
        rgba = ImageOps.exif_transpose(image).convert('RGBA')
    if rgba.getchannel('A').getextrema()[1] == 0:
        raise ValueError('Input image has no visible pixels')
    # VTracer's binary backend reads RGB and ignores alpha; white denotes empty space.
    prepared = (Image.alpha_composite(Image.new('RGBA', rgba.size, 'white'), rgba).convert('RGB')
                if colormode == 'binary' else rgba)
    with tempfile.TemporaryDirectory(prefix='scansci-trace-') as temp:
        normalized, candidate = Path(temp)/'input.png', Path(temp)/'trace.svg'
        prepared.save(normalized)
        convert_start = time.perf_counter()
        vtracer.convert_image_to_svg_py(str(normalized), str(candidate), **params)
        conversion_seconds = time.perf_counter() - convert_start
        root = ET.parse(candidate).getroot()
        width, height = rgba.size
        root.set('viewBox', f'0 0 {width} {height}')
        root.set('width', str(width))
        root.set('height', str(height))
        group = ET.Element(NS+'g', {'id': group_id})
        for node in list(root):
            root.remove(node)
            group.append(node)
        root.append(group)
        for index, node in enumerate(root.iter(NS+'path'), 1):
            node.set('id', f'{group_id}-path-{index:04d}')
        ET.ElementTree(root).write(candidate, encoding='utf-8', xml_declaration=True)
        structure = check(candidate)
        if not structure['valid_structure']:
            raise ValueError('Trace structure: ' + '; '.join(structure['errors']))
        data = candidate.read_bytes()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('xb') as stream:
        stream.write(data)
    return {'input': str(source), 'output': str(output), 'started_at': started_at,
            'input_size': list(input_size), 'oriented_size': [width, height],
            'input_exif_orientation': orientation, 'vtracer_version': version('vtracer'),
            'parameters': params, 'group_id': group_id, 'paths': structure['paths'],
            'alpha_preparation': 'composite onto white' if colormode == 'binary' else 'RGBA input',
            'bytes': len(data), 'conversion_seconds': conversion_seconds,
            'processing_seconds': time.perf_counter() - start,
            'grouping': 'whole traced image or supplied isolated region',
            'text_representation': 'traced outlines',
            'review': ['rendered fidelity and transparency', 'complete part membership',
                       'editable text and connections required by the task'],
            'timing_scope': 'processing includes input preparation, conversion, structural check and write; '
                            'host setup, model authoring and visual review are separate'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--group-id', default='trace', help='Name for the whole supplied image/isolated part')
    parser.add_argument('--colormode', choices=['color', 'binary'], default='color')
    parser.add_argument('--mode', choices=['spline', 'polygon', 'none'], default='spline')
    parser.add_argument('--filter-speckle', type=int, default=4)
    parser.add_argument('--color-precision', type=int, default=6)
    parser.add_argument('--layer-difference', type=int, default=16)
    args = vars(parser.parse_args())
    try:
        print(json.dumps(trace(**args), ensure_ascii=True, indent=2))
    except (OSError, ValueError, ET.ParseError) as exc:
        parser.exit(1, f'Trace failed: {exc}\n')


if __name__ == '__main__':
    main()
