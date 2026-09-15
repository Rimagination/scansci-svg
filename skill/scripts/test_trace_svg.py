"""Integration checks: python skill/scripts/test_trace_svg.py (Pillow + VTracer)."""
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw

from trace_svg import trace, NS
from edit_svg import edit


class TraceTest(unittest.TestCase):
    def test_binary_transparent_background_matches_white_paper(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            paths = []
            for name, background in [('transparent',(0,0,0,0)), ('paper','white')]:
                image = Image.new('RGBA',(64,64),background)
                ImageDraw.Draw(image).rectangle((20,20,43,43),fill='black')
                source, output = folder/f'{name}.png', folder/f'{name}.svg'
                image.save(source)
                trace(source,output,colormode='binary',mode='none',filter_speckle=0)
                paths.append([dict(n.attrib) for n in ET.parse(output).iter(NS+'path')])
            self.assertTrue(paths[0])
            self.assertEqual(paths[0],paths[1], 'Transparent surroundings must behave as empty white space')

    def test_non_square_transparent_part_and_existing_edit_tool(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            source, output = folder/'input.png', folder/'out.svg'
            image = Image.new('RGBA', (160, 90))
            draw = ImageDraw.Draw(image)
            draw.ellipse((20, 15, 120, 75), fill='#729460')
            draw.ellipse((45, 30, 95, 60), fill=(0, 0, 0, 0))
            image.save(source)
            original = source.read_bytes()
            result = trace(source, output, group_id='specimen', filter_speckle=0)
            self.assertEqual(result['oriented_size'], [160, 90])
            self.assertGreater(result['paths'], 0)
            self.assertGreaterEqual(result['processing_seconds'], result['conversion_seconds'])
            root = ET.parse(output).getroot()
            self.assertEqual(root.get('viewBox'), '0 0 160 90')
            self.assertFalse(list(root.iter(NS+'image')))
            self.assertEqual(source.read_bytes(), original)
            moved = folder/'moved.svg'
            changes = edit(output, [{'id':'specimen','attributes':{'transform':'translate(8 0)'}}], moved)
            self.assertTrue(changes['scope_check_passed'])
            self.assertTrue(changes['target_changed']['specimen'])
            before = output.read_bytes()
            with self.assertRaises(FileExistsError):
                trace(source, output)
            self.assertEqual(output.read_bytes(), before)

    def test_orientation_and_invalid_or_empty_input(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            source = folder/'rotated.jpg'
            image = Image.new('RGB', (80, 40), 'white')
            ImageDraw.Draw(image).rectangle((4, 5, 25, 35), fill='black')
            exif = image.getexif(); exif[274] = 6
            image.save(source, exif=exif)
            result = trace(source, folder/'rotated.svg')
            self.assertEqual(result['input_size'], [80, 40])
            self.assertEqual(result['oriented_size'], [40, 80])
            bad = folder/'invalid.svg'
            for kwargs in [{'filter_speckle':-1}, {'color_precision':9},
                           {'layer_difference':256}, {'group_id':'bad id'}, {'mode':'unknown'}]:
                with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                    trace(source, bad, **kwargs)
                self.assertFalse(bad.exists())
            empty = folder/'empty.png';Image.new('RGBA',(20,20)).save(empty)
            with self.assertRaisesRegex(ValueError,'no visible pixels'):
                trace(empty,bad)
            self.assertFalse(bad.exists())


if __name__ == '__main__':
    unittest.main()
