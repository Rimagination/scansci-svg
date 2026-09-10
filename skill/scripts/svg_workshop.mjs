/** Export sampled design paths and an offline, interactive layered SVG view. */
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {resolve,join} from 'node:path';
import {pathToFileURL} from 'node:url';
import {loadSvg} from './svg_browser.mjs';

const [input,configFile,output]=process.argv.slice(2);
if(!output){console.log('node svg_workshop.mjs input.svg config.json new-output-directory (PLAYWRIGHT_MODULE, CHROME_PATH supported)');process.exit(1);}
const config=JSON.parse(await readFile(configFile,'utf8')),source=await readFile(input,'utf8');
if(!Number.isFinite(config.width_mm)||config.width_mm<=0||config.width_mm>1000)throw Error('Explicit design width_mm must be 0–1000.');
const step=config.sample_mm??.25;
if(!Number.isFinite(step)||step<.05||step>2)throw Error('sample_mm must be .05–2.');
const {chromium}=await import(process.env.PLAYWRIGHT_MODULE?pathToFileURL(resolve(process.env.PLAYWRIGHT_MODULE)).href:'playwright');
const browser=await chromium.launch({headless:true,...(process.env.CHROME_PATH?{executablePath:process.env.CHROME_PATH}:{})});
let result;
try{
  const page=await browser.newPage();await loadSvg(page,source,800);
  result=await page.evaluate(({config,step})=>{
    const svg=document.querySelector('svg'),box=svg.viewBox.baseVal,scale=config.width_mm/box.width;
    const nodes=[...svg.querySelectorAll('[id]')],index=new Map(nodes.map(n=>[n.id,n]));
    if(index.size!==nodes.length)throw Error('Duplicate SVG IDs.');
    const rootMatrix=svg.getScreenCTM().inverse();
    const paths=(config.paths||[]).map(id=>{
      const node=index.get(id);
      if(!node||typeof node.getTotalLength!=='function')throw Error('Select geometry IDs: '+id);
      const d=node.getAttribute('d')||'';
      if(node.localName==='path'&&(d.match(/[Mm]/g)||[]).length!==1)throw Error('Split compound paths into explicit contours: '+id);
      for(let n=node;n&&n!==svg.parentElement;n=n.parentElement){
        const s=getComputedStyle(n);
        if(s.clipPath!=='none'||s.maskImage!=='none'||s.display==='none'||s.visibility!=='visible')throw Error('Resolve clipping, masking or visibility before geometry export: '+id);
        if(n!==svg&&n.localName==='svg'&&s.overflow!=='visible')throw Error('Flatten nested SVG viewport clipping before geometry export: '+id);
      }
      const closed=['rect','circle','ellipse','polygon'].includes(node.localName)||(/[zZ]\s*$/.test(d)&&(d.match(/[zZ]/g)||[]).length===1);
      const matrix=rootMatrix.multiply(node.getScreenCTM()),length=node.getTotalLength();
      // Frobenius norm bounds transformed segment lengths, including skew/nonuniform scale.
      const stretch=Math.hypot(matrix.a,matrix.b,matrix.c,matrix.d);
      const count=Math.max(4,Math.ceil(length*stretch*scale/step));
      if(!length||count>20000)throw Error('Geometry is empty or sampling exceeds 20000 segments: '+id);
      const points=Array.from({length:count+1},(_,i)=>{const q=node.getPointAtLength(i/count*length).matrixTransform(matrix);return [(q.x-box.x)*scale,(q.y-box.y)*scale];});
      if(closed)points[points.length-1]=[...points[0]];
      if(points.some(p=>!p.every(Number.isFinite)))throw Error('Invalid sampled geometry.');
      return {id,closed,points};
    });
    const layers=(config.layers||[]).map(item=>{
      const target=index.get(item.id);if(!target||target.closest('defs'))throw Error('Unknown visible layer: '+item.id);
      if(!['g','path','rect','circle','ellipse','line','polyline','polygon','text','use'].includes(target.localName))throw Error('Select an editable group or drawable layer: '+item.id);
      for(const use of [target,...target.querySelectorAll('use')].filter(n=>n.localName==='use')){
        const href=use.getAttribute('href')||use.getAttributeNS('http://www.w3.org/1999/xlink','href');
        const reference=index.get(href?.slice(1));
        if(!reference||(!reference.closest('defs,symbol')&&!target.contains(reference)))throw Error('Move cross-layer use references into defs before layer export: '+item.id);
      }
      const clone=svg.cloneNode(true);
      for(const node of clone.querySelectorAll('path,rect,circle,ellipse,line,polyline,polygon,text,use')){
        if(node.closest('defs,clipPath,mask,marker,pattern,symbol'))continue;
        const belongs=node.id===item.id||[...ancestors(node)].some(n=>n.id===item.id);
        if(!belongs)node.style.setProperty('display','none','important');
      }
      return {id:item.id,label:String(item.label||item.id),svg:new XMLSerializer().serializeToString(clone)};
    });
    function* ancestors(node){while(node.parentElement){node=node.parentElement;yield node;}}
    return {width_mm:config.width_mm,height_mm:box.height*scale,sample_mm:step,paths,layers,aspect:box.width/box.height};
  },{config,step});
}finally{await browser.close();}
const out=resolve(output);await mkdir(out);
await writeFile(join(out,'geometry.json'),JSON.stringify({width_mm:result.width_mm,height_mm:result.height_mm,sample_mm:step,paths:result.paths},null,2));
if(result.layers.length){
  const escape=s=>s.replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const layers=result.layers.map((l,i)=>`<img alt="${escape(l.label)}" data-layer="${i}" src="data:image/svg+xml;base64,${Buffer.from(l.svg).toString('base64')}">`).join('');
  const list=result.layers.map((l,i)=>`<label><input type="checkbox" data-toggle="${i}" checked> ${escape(l.label)}</label>`).join('');
  await writeFile(join(out,'layers.html'),`<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ScanSci · 分层立体展示</title>
<style>*{box-sizing:border-box}body{margin:0;background:#f3f5ee;color:#193e36;font:16px system-ui}header{padding:28px 5vw}h1{margin:0 0 8px;font-size:28px}p{color:#61736a}main{display:grid;grid-template-columns:1fr 270px;gap:20px;padding:0 5vw 40px}.stage{height:620px;display:grid;place-items:center;perspective:1300px;overflow:hidden;background:radial-gradient(ellipse,#fff,#e5ecdf);border-radius:24px}.stack{width:min(430px,58vw);aspect-ratio:${result.aspect};position:relative;transform-style:preserve-3d}.stack img{position:absolute;width:100%;height:100%;object-fit:contain;backface-visibility:visible;filter:drop-shadow(0 5px 5px #16382a18)}aside{padding:24px;border-radius:24px;background:#fff}aside label{display:block;margin:18px 0}input[type=range]{width:100%}button{border:0;border-radius:8px;background:#236c58;color:#fff;padding:10px 18px;cursor:pointer}@media(max-width:700px){main{grid-template-columns:1fr}.stage{height:450px}.stack{width:65vw}}</style>
<header><h1>分层立体展示</h1><p>同一 SVG 的部件可分开观察；层间距离与视角用于展示。</p></header><main><div class="stage"><div class="stack">${layers}</div></div><aside><label>层间距离 <input id="gap" type="range" min="0" max="95" value="48"></label><label>俯视角 <input id="tilt" type="range" min="0" max="75" value="48"></label><label>旋转角 <input id="turn" type="range" min="-90" max="90" value="-25"></label>${list}<button id="reset">合拢正视</button><p>源图和部件仍为矢量；此页面展示图层空间，实体厚度由制作配置指定。</p></aside></main>
<script>const layers=[...document.querySelectorAll('[data-layer]')],gap=document.querySelector('#gap'),tilt=document.querySelector('#tilt'),turn=document.querySelector('#turn');function draw(){document.querySelector('.stack').style.transform='rotateX('+tilt.value+'deg) rotateZ('+turn.value+'deg)';layers.forEach((el,i)=>el.style.transform='translateZ('+((i-(layers.length-1)/2)*gap.value)+'px)')}document.querySelectorAll('input[type=range]').forEach(el=>el.oninput=draw);document.querySelectorAll('[data-toggle]').forEach(el=>el.onchange=()=>layers[Number(el.dataset.toggle)].style.visibility=el.checked?'visible':'hidden');document.querySelector('#reset').onclick=()=>{gap.value=tilt.value=turn.value=0;draw()};draw();</script></html>`);
}
console.log(JSON.stringify({directory:out,paths:result.paths.length,layers:result.layers.length}));
