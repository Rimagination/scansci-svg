"""Run with: python skill/scripts/test_compose_svg.py"""
import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from compose_svg import compose, NS
from check_edit_scope import compare


class CompositionTest(unittest.TestCase):
    def test_label_repair_preserves_panels_and_other_labels(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            (folder / "asset.svg").write_text(
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">'
                '<g id="body"><circle cx="5" cy="5" r="4"/></g></svg>', encoding="utf-8")
            spec = {"width": 100, "height": 100, "panels": [
                {"id": "a", "file": "asset.svg", "x": 0, "y": 30, "width": 60, "height": 60}
            ], "labels": [{"id": "panel-a-title", "text": "A", "x": 0, "y": 20},
                           {"text": "Schematic", "x": 0, "y": 95}]}
            layout, before, after = [folder / name for name in ("layout.json", "before.svg", "after.svg")]
            layout.write_text(json.dumps(spec), encoding="utf-8")
            compose(layout, before)
            tree = ET.parse(before)
            title = next(n for n in tree.getroot().iter() if n.get("id") == "panel-a-title")
            title.text = "A  Revised"
            tree.write(after, encoding="utf-8")
            result = compare(before, after, ["panel-a-title"])
            self.assertTrue(result["scope_check_passed"], result)
            self.assertTrue(result["target_changed"]["panel-a-title"])
            self.assertIsNotNone(tree.find(f".//*[@id='figure-label-2']"))
            for ident in ["panel-a", "panel-a--body", "figure-labels", "figure-label-2", "has space"]:
                spec["labels"][0]["id"] = ident
                layout.write_text(json.dumps(spec), encoding="utf-8")
                with self.assertRaises(ValueError):
                    compose(layout, folder / "invalid.svg")
                self.assertFalse((folder / "invalid.svg").exists())

    def test_repeated_asset_isolation_and_invalid_layout(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            source = folder / "asset.svg"
            original = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="-10 5 100 200">
              <title id="caption">Original</title>
              <defs><linearGradient id="paint"><stop stop-color="#fff"/></linearGradient></defs>
              <g id="body" aria-labelledby="caption"><path id="shape" d="M0 0L10 20L20 0Z" fill="url('#paint')"/>
              <use href="#shape" x="30"/><path d="M2 2L4 4" style="stroke:url(#paint)" fill="#abcdef"/></g></svg>'''
            source.write_text(original, encoding="utf-8")
            spec = {"width": 400, "height": 300, "width_mm": 180, "panels": [
                {"id": key, "file": "asset.svg", "x": x, "y": 40, "width": 180, "height": 240}
                for key, x in [("a", 0), ("b", 200)]
            ], "labels": [{"text": "A & B", "x": 12, "y": 24}]}
            layout, output = folder / "layout.json", folder / "figure.svg"
            layout.write_text(json.dumps(spec), encoding="utf-8")
            compose(layout, output)
            root = ET.parse(output).getroot()
            self.assertEqual(root.get('width'), '180mm')
            self.assertEqual(root.get('height'), '135mm')
            self.assertEqual(root.get('viewBox'), '0 0 400 300')
            by_id = {n.get("id"): n for n in root.iter() if n.get("id")}
            self.assertEqual(by_id["panel-b--shape"].get("fill"), "url(#panel-b--paint)")
            self.assertEqual(by_id["panel-a--body"].get("aria-labelledby"), "panel-a--caption")
            self.assertEqual(root.find(f".//{{{NS}}}use").get("href"), "#panel-a--shape")
            nested = root.find(f".//{{{NS}}}svg")
            self.assertEqual(nested.get("viewBox"), "-10 5 100 200")
            self.assertEqual(nested.get("preserveAspectRatio"), "xMidYMid meet")
            by_id["panel-a--shape"].set("fill", "red")
            self.assertEqual(by_id["panel-b--shape"].get("fill"), "url(#panel-b--paint)")
            self.assertEqual(source.read_text(encoding="utf-8"), original)
            with self.assertRaises(FileExistsError):
                compose(layout, output)
            for field, value in [("id", "a"), ("width", -1), ("x", 390)]:
                bad = json.loads(json.dumps(spec))
                bad["panels"][1][field] = value
                layout.write_text(json.dumps(bad), encoding="utf-8")
                with self.assertRaises(ValueError):
                    compose(layout, folder / "invalid.svg")
                self.assertFalse((folder / "invalid.svg").exists())
            layout.write_text(json.dumps(spec), encoding="utf-8")
            for changed in [original.replace("#paint", "#missing"),
                            original.replace("<defs>", "<style>path{fill:red}</style><defs>"),
                            original.replace('viewBox=', 'style="width:40px;height:40px" viewBox=')]:
                source.write_text(changed, encoding="utf-8")
                with self.assertRaises(ValueError):
                    compose(layout, folder / "invalid.svg")


if __name__ == "__main__":
    unittest.main()
