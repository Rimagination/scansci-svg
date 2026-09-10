"""Run with: python skill/scripts/test_edit_svg.py"""
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from edit_svg import edit


class EditTest(unittest.TestCase):
    def test_inline_style_cannot_silently_override_edit(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)
            for i,(style,attribute) in enumerate([
                ('fill:red','fill'), ('/* note */ FILL : red !important','fill'),
                ('opacity:.2','opacity'), ('transform:rotate(5deg)','transform'),
                ('font:italic 12px serif','font-size'), ('all:initial','stroke')]):
                source=folder/f'source-{i}.svg'
                source.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">'
                                  f'<g id="part" style="{style}"><circle r="2"/></g></svg>',encoding='utf-8')
                with self.assertRaisesRegex(ValueError,'Inline style overrides'):
                    edit(source,[{'id':'part','attributes':{attribute:'1'}}],folder/'invalid.svg')
                self.assertFalse((folder/'invalid.svg').exists())

    def test_target_and_dependency_protection(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            source, output = folder/'source.svg', folder/'output.svg'
            text = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
                    '<g id="leaf"><path id="blade" d="M0 0L20 0L10 10Z" fill="green"/>'
                    '<path d="M0 0L10 10" stroke="yellow"/></g>'
                    '<text id="label" x="5" y="80">Old</text></svg>')
            source.write_text(text, encoding='utf-8')
            result=edit(source,[{'id':'leaf','attributes':{'transform':'rotate(12 0 0)'}},
                                {'id':'label','text':'Revised'}],output)
            self.assertTrue(result['scope_check_passed'])
            self.assertTrue(all(result['target_changed'].values()))
            self.assertEqual(source.read_text(encoding='utf-8'),text)
            self.assertEqual(ET.parse(output).find(".//*[@id='label']").text,'Revised')
            with self.assertRaises(FileExistsError):
                edit(source,[{'id':'label','text':'Again'}],output)
            for changes in [[], [{'id':'missing','text':'No'}], [{'id':'leaf','attributes':{'id':'new'}}],
                            [{'id':'leaf','text':'No'}], [{'id':'label'}],
                            [{'id':'leaf','attributes':{'opacity':'0.5'}},{'id':'blade','attributes':{'fill':'red'}}]]:
                with self.assertRaises(ValueError):
                    edit(source,changes,folder/'invalid.svg')
                self.assertFalse((folder/'invalid.svg').exists())
            source.write_text(text.replace('</svg>','<use href="#blade" x="40"/></svg>'),encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'references allowed subtree'):
                edit(source,[{'id':'blade','attributes':{'fill':'red'}}],folder/'invalid.svg')
            self.assertFalse((folder/'invalid.svg').exists())


if __name__=='__main__':
    unittest.main()
