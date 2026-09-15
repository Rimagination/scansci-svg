"""Exercise component extraction, owned edits and portable scene recipes."""
import copy
import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from compose_scene import compose_scene, find_components, N, SKILL, transform_matrix, map_point, inverse
from check_edit_scope import compare


class SceneTest(unittest.TestCase):
    def test_connections_cross_groups_and_preserve_other_objects(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp); assets = folder / 'assets/test'; assets.mkdir(parents=True)
            (assets / 'source.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">'
                '<g id="body"><rect width="20" height="20" fill="#345678"/></g></svg>', encoding='utf-8')
            catalog = [{'id':'test', 'file':'source.svg', 'components':[{'id':'box','label':'Box',
                'selector':None,'bounds':[0,0,20,20],'anchors':{'out':[20,10],'in':[0,10]}}]}]
            (assets/'catalog.json').write_text(json.dumps(catalog),encoding='utf-8')
            template = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">' \
                '<g id="back"><rect width="400" height="300" fill="white"/></g>' \
                '<g id="left" transform="translate(10 20) scale(2)"><g id="a"/></g>' \
                '<g id="right" transform="translate(200 30) rotate(90)"><g id="b"/></g>' \
                '<g id="links" transform="translate(5 7) scale(0.5)"><g id="ab"/></g></svg>'
            (folder/'template.svg').write_text(template, encoding='utf-8')
            recipe = {'template':'template.svg','objects':[
                {'id':'a','component':'box','at':[10,15],'width':40},
                {'id':'b','component':'box','at':[20,10],'width':20}],
                'connections':[{'id':'ab','from':{'object':'a','anchor':'out'},
                    'to':{'object':'b','point':[0,10]},'route':'horizontal','arrow':'end',
                    'label':{'text':'A to B','offset':[0,-10]}}]}
            layout=folder/'scene.json'; before=folder/'before.svg';after=folder/'after.svg'
            layout.write_text(json.dumps(recipe),encoding='utf-8');compose_scene(layout,before,folder)
            def read(path):
                root=ET.parse(path).getroot()
                line=root.find(".//*[@id='ab-line']")
                points=[[float(v) for v in p.split(',')] for p in line.get('points').split()]
                return root,points
            root,points=read(before)
            # Independently worked endpoint coordinates: A world=(110,90), B=(180,50).
            self.assertEqual(points,[[210,166],[280,166],[280,86],[350,86]])
            self.assertEqual(root.find(".//*[@id='ab-line']").get('marker-end'),'url(#ab-arrow)')
            self.assertEqual(root.find(".//*[@id='ab-label']").get('x'),'280')
            recipe['objects'][0]['at'][0]+=10
            recipe['objects'][0]['width']=60
            layout.write_text(json.dumps(recipe),encoding='utf-8');compose_scene(layout,after,folder)
            _,changed=read(after)
            self.assertEqual(changed[0],[330,206]);self.assertEqual(changed[-1],points[-1])
            scope=compare(before,after,['a','ab'])
            self.assertTrue(scope['scope_check_passed'],scope)
            self.assertTrue(all(scope['target_changed'].values()))
            for endpoint in ({'object':'missing','point':[0,0]}, {'object':'a'},
                             {'object':'a','anchor':'out','point':[0,0]}):
                bad=copy.deepcopy(recipe);bad['connections'][0]['from']=endpoint
                layout.write_text(json.dumps(bad),encoding='utf-8')
                with self.assertRaises(ValueError):compose_scene(layout,folder/'bad.svg',folder)
                self.assertFalse((folder/'bad.svg').exists())
            layout.write_text(json.dumps(recipe),encoding='utf-8')
            (folder/'template.svg').write_text(template.replace('scale(0.5)','scale(0)'),encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'invertible'):compose_scene(layout,folder/'bad.svg',folder)
            for extra in ['style="transform:translateX(20px)"', 'transform-origin="10 20"',
                          'style="/* exporter */ -webkit-transform:translateX(20px)"']:
                (folder/'template.svg').write_text(template.replace('id="left"','id="left" '+extra),encoding='utf-8')
                with self.assertRaisesRegex(ValueError,'CSS transforms'):compose_scene(layout,folder/'bad.svg',folder)
            (folder/'template.svg').write_text(template,encoding='utf-8')
            source=assets/'source.svg';original=source.read_text(encoding='utf-8')
            for extra in ['transform-origin="10 20"','style="-webkit-transform:translateX(20px)"']:
                source.write_text(original.replace('viewBox=',extra+' viewBox='),encoding='utf-8')
                with self.assertRaisesRegex(ValueError,'root transforms'):compose_scene(layout,folder/'bad.svg',folder)

    def test_transform_attribute_coordinates(self):
        for transform,point,expected in [
            ('translate(10-20) scale(2,3)',[4,5],[18,-5]),
            ('rotate(90 10 20)',[20,20],[10,30]),
            ('matrix(1 0 0 1 12 15) skewX(45)',[2,3],[17,18]),
            ('skewY(45)',[2,3],[2,5])]:
            matrix=transform_matrix(transform)
            actual=map_point(matrix,point)
            for a,b in zip(actual,expected):self.assertAlmostEqual(a,b)
            for a,b in zip(map_point(inverse(matrix),actual),point):self.assertAlmostEqual(a,b)
        for value in ['translate(10px)', 'scale(NaN)', 'rotate(1,2)', 'garbage', 'scale(2) bad']:
            with self.assertRaises(ValueError):transform_matrix(value)

    def test_extraction_references_anchor_and_owned_edit(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            assets = folder / "assets/test"
            assets.mkdir(parents=True)
            svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
              <defs><linearGradient id="ink"><stop stop-color="#123456"/></linearGradient></defs>
              <g id="plant" transform="translate(10 5)" fill="url(#ink)">
                <g id="leaf"><title id="caption">Leaf</title><path aria-labelledby="caption" d="M0 0L20 0L10 20Z"/></g>
                <g id="sibling"><title>Sibling</title><circle r="2"/></g>
              </g></svg>'''
            source = assets / "source.svg"
            source.write_text(svg, encoding="utf-8")
            catalog = [{"id": "test-plant", "title": "Plant", "file": "source.svg", "license": "",
                        "components": [{"id": "leaf", "label": "Leaf", "selector": "leaf",
                                        "bounds": [10, 5, 20, 20], "anchors": {"tip": [20, 25]},
                                        "view": "side", "style": "flat", "scenes": ["botany"]}]}]
            (assets / "catalog.json").write_text(json.dumps(catalog), encoding="utf-8")
            self.assertEqual([v['id'] for v in find_components('botany leaf', folder)], ['leaf'])
            recipe = {"width": 200, "height": 120, "objects": [
                {"id": "a", "component": "leaf", "at": [60, 75], "anchor": "tip", "width": 40,
                 "labels": [{"at": [0, 18], "text": "A", "leader": [[0, 0], [0, 12]]}]},
                {"id": "b", "component": "leaf", "at": [140, 75], "anchor": "tip", "width": 40}]}
            layout, before, after = (folder / n for n in ('scene.json', 'before.svg', 'after.svg'))
            layout.write_text(json.dumps(recipe), encoding="utf-8")
            compose_scene(layout, before, folder)
            root = ET.parse(before).getroot()
            ids = {n.get('id'): n for n in root.iter() if n.get('id')}
            self.assertNotIn('a--sibling', ids)
            self.assertEqual(ids['a--plant'].get('transform'), 'translate(10 5)')
            self.assertEqual(ids['a--plant'].get('fill'), 'url(#a--ink)')
            self.assertEqual(ids['b--plant'].get('fill'), 'url(#b--ink)')
            self.assertEqual(ids['a-geometry'].get('transform'), 'scale(2) translate(-20 -25)')
            self.assertIn(ids['a-label-1'], list(ids['a'].iter()))
            self.assertEqual(ids['a-label-1'].get('y'), '18')
            recipe['objects'][0]['at'] = [80, 75]
            layout.write_text(json.dumps(recipe), encoding="utf-8")
            compose_scene(layout, after, folder)
            result = compare(before, after, ['a'])
            self.assertTrue(result['scope_check_passed'], result)
            self.assertTrue(result['target_changed']['a'])
            self.assertEqual(source.read_text(encoding="utf-8"), svg)
            with self.assertRaises(FileExistsError):
                compose_scene(layout, after, folder)
            for change in ({'anchor': 'missing'}, {'at': [0, float('nan')]}, {'opacity': 2}, {'width': 0}):
                bad = copy.deepcopy(recipe)
                bad['objects'][0].update(change)
                layout.write_text(json.dumps(bad), encoding="utf-8")
                with self.assertRaises((ValueError, KeyError)):
                    compose_scene(layout, folder / 'bad.svg', folder)
                self.assertFalse((folder / 'bad.svg').exists())
            # A visible sibling referenced by the chosen group needs explicit defs.
            source.write_text(svg.replace('<title id="caption">', '<use href="#sibling"/><title id="caption">'), encoding='utf-8')
            layout.write_text(json.dumps(recipe), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'removed sibling'):
                compose_scene(layout, folder / 'bad.svg', folder)

    def test_packaged_scene_and_template_ownership(self):
        recipe = SKILL / 'assets/scenes/riverbank/scene.json'
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / 'scene.svg'
            compose_scene(recipe, output)
            root = ET.parse(output).getroot()
            owners = [n for n in root.iter() if n.get('data-component')]
            self.assertEqual(len(owners), 18)
            perch = root.find(".//*[@id='perch-assembly']")
            self.assertIsNotNone(perch.find(".//*[@id='kingfisher']"))
            self.assertIsNotNone(perch.find(".//*[@id='perch-branch']"))
            water = root.find(".//*[@id='aquatic-life']")
            self.assertIsNotNone(water.find(".//*[@id='fish-near']"))
            self.assertEqual(water.get('clip-path'), 'url(#pond-boundary)')
            self.assertTrue({'kingfisher','cattail','tree','buoy'}.issubset(
                {component['id'] for component in find_components('', SKILL)}))
            # A stale slot must fail instead of silently adding the object on top.
            spec = json.loads(recipe.read_text(encoding='utf-8'))
            spec['template'] = str(recipe.parent / spec['template'])
            spec['objects'][0]['id'] = 'missing-slot'
            invalid = Path(temp) / 'invalid.json'
            invalid.write_text(json.dumps(spec), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'Missing template slot'):
                compose_scene(invalid, Path(temp) / 'invalid.svg')


if __name__ == '__main__':
    unittest.main()
