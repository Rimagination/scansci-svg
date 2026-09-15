"""Small integration check for replay rendering and unsupported input handling.

Requires node, ffmpeg, ffprobe; PLAYWRIGHT_MODULE and CHROME_PATH may locate
the existing browser runtime. No package installation is performed.
"""
from pathlib import Path
import json
import subprocess
import tempfile
import unittest

SCRIPT=Path(__file__).with_name('replay_svg.mjs')
FIXTURE='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0&#9;0&#10;200 120">
<defs><linearGradient id="shade"><stop stop-color="#128070"/><stop offset="1" stop-color="#b4d4a0"/></linearGradient></defs>
<g id="leaf" transform="translate(8 4) rotate(5 60 55)" opacity=".8">
<path d="M20 70 Q40 10 100 25 Q92 85 20 70Z" fill="url(#shade)"/>
<path d="M20 70 Q53 43 100 25" fill="none" stroke="#265947" stroke-width="2" stroke-dasharray="4 2"/>
</g><g id="label"><text x="105" y="90" font-size="14" font-family="Arial">Leaf 1</text></g></svg>'''

def run(*args):
    return subprocess.run(['node',str(SCRIPT),*map(str,args)],capture_output=True,text=True,encoding='utf-8',timeout=90)

class ReplayTests(unittest.TestCase):
    def test_html_steps_do_not_require_encoder(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=root/'source.svg';source.write_text(FIXTURE.replace('font-family="Arial"', 'fill="currentColor"'),encoding='utf-8')
            result=run(source,root/'output','--format','html','--ffmpeg','missing-encoder-for-this-test')
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertTrue((root/'output'/'replay.html').exists())
            self.assertFalse((root/'output'/'frames').exists())
            self.assertTrue(json.loads((root/'output'/'replay.json').read_text(encoding='utf-8'))['final_frame_matches_reference'])

    def test_process_samples_final_endpoint(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=root/'source.svg';source.write_text(FIXTURE,encoding='utf-8')
            timeline=root/'process.json'
            timeline.write_text(json.dumps({'tracks':[{'type':'translate','id':'leaf','start':0,'end':3,'from':[0,0],'to':[10,0]}]}))
            result=run(source,root/'output','--seconds','3','--fps','5','--width','200','--timeline',timeline)
            self.assertEqual(result.returncode,0,result.stderr)
            data=json.loads((root/'output'/'replay.json').read_text())
            self.assertEqual(data['final_timeline_state'][0]['value'],[10,0])
            self.assertTrue((root/'output'/'process.mp4').exists())

    def test_render_encode_and_protect_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=root/'source.svg';source.write_text(FIXTURE,encoding='utf-8')
            original=source.read_bytes();out=root/'replay'
            result=run(source,out,'--seconds','3','--fps','10','--width','200','--format','both')
            self.assertEqual(result.returncode,0,result.stderr)
            data=json.loads((out/'replay.json').read_text())
            self.assertTrue(data['final_frame_matches_reference'])
            self.assertEqual(data['drawables'],3)
            self.assertEqual([s['id'] for s in data['stages']],['leaf','label'])
            self.assertEqual(source.read_bytes(),original)
            for ext in ['mp4','gif']:
                probe=subprocess.run(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=width,height,nb_read_frames:format=duration','-of','json',str(out/f'replay.{ext}')],capture_output=True,text=True,check=True)
                meta=json.loads(probe.stdout);stream=meta['streams'][0]
                self.assertEqual((stream['width'],stream['height']),(200,120))
                self.assertAlmostEqual(float(meta['format']['duration']),3,places=1)
                self.assertGreater(int(stream['nb_read_frames']),1)
            retry=run(source,out)
            self.assertNotEqual(retry.returncode,0)
            self.assertIn('EEXIST',retry.stderr)

    def test_root_viewport_style_stops_before_capture(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=root/'oversized.svg'
            source.write_text(FIXTURE.replace('<svg ', '<svg style="width:1200px;height:1600px" ',1),encoding='utf-8')
            result=run(source,root/'output')
            self.assertNotEqual(result.returncode,0)
            self.assertIn('Normalize root viewport style first',result.stderr)
            self.assertFalse((root/'output'/'reference.png').exists())

    def test_invalid_input_stops(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=root/'bad.svg'
            source.write_text('<!DOCTYPE svg><svg/>',encoding='utf-8')
            result=run(source,root/'output')
            self.assertNotEqual(result.returncode,0)
            self.assertIn('DTD/entities',result.stderr)
            self.assertFalse((root/'output').exists())

    def test_foreign_namespace_cannot_create_active_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=root/'foreign.svg'
            source.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 120"><iframe xmlns="http://www.w3.org/1999/xhtml" srcdoc="&lt;script&gt;document.body.textContent=123&lt;/script&gt;"/></svg>',encoding='utf-8')
            result=run(source,root/'output')
            self.assertNotEqual(result.returncode,0)
            self.assertIn('unsupported element first: iframe',result.stderr)
            self.assertFalse((root/'output'/'reference.png').exists())

if __name__=='__main__':unittest.main()
