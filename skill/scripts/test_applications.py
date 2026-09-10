"""Checks for parameter propagation and fabrication geometry/format correctness."""
import json
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from variants_svg import generate
from fabricate_svg import fabricate, extrude


class ApplicationsTests(unittest.TestCase):
    def test_workshop_coordinates_and_unsupported_clipping(self):
        script=Path(__file__).with_name('svg_workshop.mjs')
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);source=p/'source.svg';config=p/'config.json'
            fixtures=[
                ('<g transform="translate(10 5) scale(2)"><rect id="shape" width="10" height="10"/></g>',{'paths':['shape']},None),
                ('<svg width="20" height="20"><rect id="shape" width="40" height="10"/></svg>',{'paths':['shape']},'nested SVG viewport'),
                ('<path id="origin" d="M0 0L10 0L10 10Z"/><g id="copy"><use href="#origin"/></g>',{'layers':[{'id':'copy'}]},'cross-layer use'),
            ]
            for i,(body,options,error) in enumerate(fixtures):
                source.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'+body+'</svg>')
                config.write_text(json.dumps({'width_mm':100,'sample_mm':1,**options}))
                out=p/f'out-{i}'
                result=subprocess.run(['node',str(script),str(source),str(config),str(out)],capture_output=True,text=True,encoding='utf-8',timeout=30)
                if error:
                    self.assertNotEqual(result.returncode,0)
                    self.assertIn(error,result.stderr)
                    self.assertFalse(out.exists())
                else:
                    self.assertEqual(result.returncode,0,result.stderr)
                    points=json.loads((out/'geometry.json').read_text())['paths'][0]['points']
                    self.assertAlmostEqual(min(x for x,y in points),10)
                    self.assertAlmostEqual(max(x for x,y in points),30)
                    self.assertAlmostEqual(min(y for x,y in points),5)
                    self.assertTrue(points[0]==points[-1])

    def test_parameters_move_connected_endpoints_and_preserve_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)
            template='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><g id="body"><rect id="box" width="{{w}}" height="20"/><g id="port" transform="translate({{w}} 0)"><circle r="2"/></g><text id="label">{{label}}</text></g></svg>'
            (p/'template.svg').write_text(template)
            recipe={'template':'template.svg','parameters':{'w':{'type':'number','min':10,'max':80},'label':{'type':'choice','values':['A & B','C']}},'variants':[{'name':'short','values':{'w':20,'label':'A & B'}},{'name':'long','values':{'w':70,'label':'C'}}]}
            (p/'recipe.json').write_text(json.dumps(recipe))
            generate(p/'recipe.json',p/'out')
            for name,w in [('short',20),('long',70)]:
                root=ET.parse(p/'out'/f'{name}.svg').getroot();index={n.get('id'):n for n in root.iter() if n.get('id')}
                self.assertEqual(set(index),{'body','box','port','label'})
                self.assertEqual(index['box'].get('width'),str(w))
                self.assertEqual(index['port'].get('transform'),f'translate({w} 0)')
            self.assertEqual((p/'template.svg').read_text(),template)
            with self.assertRaises(FileExistsError):generate(p/'recipe.json',p/'out')
            recipe['variants'][0]['values']['w']=100
            (p/'recipe.json').write_text(json.dumps(recipe))
            with self.assertRaises(ValueError):generate(p/'recipe.json',p/'invalid')
            self.assertFalse((p/'invalid').exists())
            recipe['variants'][0]['values']['w']=20
            for names in [('A','a'),('CON','valid')]:
                for item,name in zip(recipe['variants'],names):item['name']=name
                (p/'recipe.json').write_text(json.dumps(recipe))
                with self.assertRaises(ValueError):generate(p/'recipe.json',p/'invalid-name')
                self.assertFalse((p/'invalid-name').exists())

    def test_concave_extrusion_volume_and_mesh(self):
        # Concavity exposes triangulation that fills outside the profile.
        mesh,report=extrude([[0,0],[10,0],[10,3],[3,3],[3,10],[0,10],[0,0]],2)
        self.assertAlmostEqual(report['volume_mm3'],102)
        self.assertTrue(report['closed_mesh'])
        self.assertEqual(mesh.count('facet normal'),report['triangles'])

    def test_physical_units_stitch_readback_and_source_protection(self):
        from pyembroidery import EmbPattern, STITCH, COMMAND_MASK
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);geometry=p/'geometry.json'
            geometry.write_text(json.dumps({'width_mm':20,'height_mm':10,'paths':[{'id':'outline','closed':True,'points':[[1,1],[19,1],[19,9],[1,9],[1,1]]},{'id':'vein','closed':False,'points':[[2,5],[18,5]]}]}))
            original=geometry.read_bytes()
            report=fabricate(geometry,p/'out',solid_id='outline',embroidery=True,stitch_mm=2)
            self.assertEqual(report['cut_contours'],1)
            self.assertEqual(ET.parse(p/'out'/'cut.svg').getroot().get('width'),'20mm')
            self.assertAlmostEqual(report['stl']['volume_mm3'],288)
            for ext,reader in [('dst',EmbPattern.read_dst),('pes',EmbPattern.read_pes)]:
                loaded=reader(str(p/'out'/f'running-stitch.{ext}'))
                stitches=[s for s in loaded.stitches if (s[2]&COMMAND_MASK)==STITCH]
                self.assertGreater(len(stitches),25)
                # Embroidery stores tenths of mm, centered around the design center.
                self.assertAlmostEqual(max(s[0] for s in stitches)-min(s[0] for s in stitches),180,delta=1)
            self.assertEqual(geometry.read_bytes(),original)
            with self.assertRaises(FileExistsError):fabricate(geometry,p/'out')

    def test_invalid_contour_and_hoop(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);source=p/'geometry.json'
            base={'width_mm':20,'height_mm':10,'paths':[{'id':'bad','closed':True,'points':[[0,0],[10,10],[0,10],[10,0],[0,0]]}]}
            source.write_text(json.dumps(base))
            with self.assertRaises(ValueError):fabricate(source,p/'invalid')
            base['paths'][0]['points']=[[0,0],[20,0],[20,10],[0,10],[0,0]]
            source.write_text(json.dumps(base))
            with self.assertRaises(ValueError):fabricate(source,p/'small',embroidery=True,hoop_mm=5)
            self.assertFalse((p/'small').exists())


if __name__=='__main__':unittest.main()
