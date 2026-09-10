/** Render a reconstructed drawing replay from an existing static SVG. */
import {readFile, writeFile, mkdir, stat} from 'node:fs/promises';
import {resolve, join} from 'node:path';
import {pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';
import {loadSvg} from './svg_browser.mjs';
import {installTimeline} from './svg_timeline.mjs';
import {setupDrawingSteps,drawingHtml} from './drawing_steps.mjs';

const args=process.argv.slice(2);
if(args.includes('--help')||args.length<2){
  console.log('node replay_svg.mjs input.svg output-directory [--format mp4|gif|both|html] [--style smooth|steps] [--steps drawing.json] [--seconds 9] [--fps 20] [--width 640] [--order group-id,group-id] [--timeline process.json] [--chrome executable] [--playwright module-path] [--ffmpeg executable]');
  process.exit(args.includes('--help')?0:1);
}
const [input,output,...rest]=args;
const options={format:'mp4',seconds:'9',fps:'20',width:'640',order:'',ffmpeg:'ffmpeg',style:'smooth'};
const keys=new Set([...Object.keys(options),'chrome','playwright','timeline','steps']);
for(let i=0;i<rest.length;i+=2){
  const key=rest[i].replace(/^--/,'');
  if(!rest[i].startsWith('--')||!keys.has(key)||rest[i+1]===undefined)throw Error('Unknown/missing option '+rest[i]);
  options[key]=rest[i+1];
}
const seconds=Number(options.seconds),fps=Number(options.fps),width=Number(options.width);
if(!['mp4','gif','both','html'].includes(options.format)||!['smooth','steps'].includes(options.style)||!Number.isFinite(seconds)||seconds<3||seconds>60||!Number.isInteger(fps)||fps<5||fps>60||!Number.isInteger(width)||width<128||width>1920||width%2)throw Error('Use 3–60 seconds, 5–60 integer fps, even width 128–1920, and mp4/gif/both/html.');
const timeline=options.timeline?JSON.parse(await readFile(resolve(options.timeline),'utf8')):null;
const steps=options.steps?JSON.parse(await readFile(resolve(options.steps),'utf8')):null;
const discrete=options.style==='steps'||options.format==='html'||!!steps;
if(timeline&&discrete)throw Error('Choose a scientific timeline or a discrete drawing replay.');
const started=Date.now(),out=resolve(output),source=await readFile(resolve(input),'utf8');
// Read into an inert XML document, and block all browser networking as well.
if(/<!DOCTYPE|<!ENTITY/i.test(source))throw Error('SVG with DTD/entities is unsupported.');
const modulePath=options.playwright||process.env.PLAYWRIGHT_MODULE;
const {chromium}=await import(modulePath?pathToFileURL(resolve(modulePath)).href:'playwright');
if(options.format!=='html'){
  const enc=spawnSync(options.ffmpeg,['-version'],{windowsHide:true,encoding:'utf8'});
  if(enc.error||enc.status!==0)throw Error('FFmpeg executable unavailable.');
}
// An exclusive directory keeps the source and previous replays intact.
await mkdir(out,{recursive:false});
if(options.format!=='html')await mkdir(join(out,'frames'));
const browser=await chromium.launch({headless:true,...((options.chrome||process.env.CHROME_PATH)?{executablePath:options.chrome||process.env.CHROME_PATH}:{})});
let report;
try{
  const page=await browser.newPage({deviceScaleFactor:1});
  const dimensions=await loadSvg(page,source,width);
  const baseline=await page.screenshot({path:join(out,'reference.png')});
  const serialized=options.format==='html'?await page.evaluate(()=>new XMLSerializer().serializeToString(document.querySelector('svg'))):null;
  const plan=timeline?await installTimeline(page,timeline,seconds):discrete?await page.evaluate(setupDrawingSteps,steps):await page.evaluate(({order})=>{
    const svg=document.querySelector('svg'),ns=svg.namespaceURI;
    const requested=order.split(',').map(v=>v.trim()).filter(Boolean);
    const ids=new Map([...svg.querySelectorAll('[id]')].map(n=>[n.id,n]));
    for(const id of requested)if(!ids.has(id)||ids.get(id).localName!=='g')throw Error('Order requires an existing group: '+id);
    if(new Set(requested).size!==requested.length)throw Error('Duplicate order group.');
    const nodes=[...svg.querySelectorAll('path,rect,circle,ellipse,line,polyline,polygon,text,use')].filter(n=>!n.closest('defs,clipPath,mask,marker,pattern,symbol')&&!n.closest('textPath'));
    const records=[];
    for(const node of nodes){
      const cs=getComputedStyle(node);
      if(cs.display==='none'||cs.visibility==='hidden')continue;
      const parent=node.parentElement.closest('g[id]');
      const owners=requested.filter(id=>ids.get(id).contains(node));
      const unit=owners[0]||parent?.id||'ungrouped';
      let length=0;
      if(typeof node.getTotalLength==='function')try{length=node.getTotalLength();}catch{}
      const originalStyle=node.getAttribute('style');
      let outline=null;
      if(length>0){
        outline=node.cloneNode(false);outline.removeAttribute('id');
        const paint=cs.stroke!=='none'?cs.stroke:(cs.fill.startsWith('url(')?'#72856b':cs.fill==='none'?'#72856b':cs.fill);
        const set=(k,v)=>outline.style.setProperty(k,String(v),'important');
        set('fill','none');set('stroke',paint);set('stroke-width',cs.stroke!=='none'?cs.strokeWidth:1.25);
        set('stroke-linecap','round');set('stroke-linejoin','round');
        set('stroke-opacity',cs.stroke!=='none'?cs.strokeOpacity:1);
        set('stroke-dasharray',`${length} ${length}`);set('stroke-dashoffset',length);
        for(const key of ['marker-start','marker-mid','marker-end'])set(key,'none');
        outline.removeAttribute('pathLength');
        node.after(outline);
      }
      records.push({node,outline,length,originalStyle,opacity:Number(cs.opacity),unit,filled:cs.fill!=='none'&&Number(cs.fillOpacity)>0});
    }
    if(!records.length)throw Error('No visible drawable objects.');
    const units=[...new Set(records.map(r=>r.unit))];
    units.sort((a,b)=>{const ai=requested.indexOf(a),bi=requested.indexOf(b);return (ai<0?requested.length:ai)-(bi<0?requested.length:bi);});
    const weights=units.map(u=>Math.sqrt(records.filter(r=>r.unit===u).reduce((s,r)=>s+Math.sqrt(Math.max(16,Math.min(r.length,2000))),0)));
    const total=weights.reduce((a,b)=>a+b,0);let start=0;
    const stages=units.map((id,i)=>{const stage={id,start,end:start+weights[i]/total};start=stage.end;return stage;});
    const lookup=new Map(stages.map(s=>[s.id,s]));
    window.replayAt=(progress)=>{
      for(const r of records){
        if(progress>=1){
          if(r.originalStyle===null)r.node.removeAttribute('style');else r.node.setAttribute('style',r.originalStyle);
          if(r.outline)r.outline.style.setProperty('display','none','important');
          continue;
        }
        const stage=lookup.get(r.unit),p=Math.max(0,Math.min(1,(progress-stage.start)/(stage.end-stage.start)));
        const fill=r.outline?(r.filled?Math.max(0,(p-.62)/.38):(p>=1?1:0)):p;
        r.node.style.setProperty('opacity',String(r.opacity*fill),'important');
        if(r.outline){
          r.outline.style.setProperty('display',p>0&&p<1?'inline':'none','important');
          r.outline.style.setProperty('stroke-dashoffset',String(r.length*(1-Math.min(1,p/.78))),'important');
          r.outline.style.setProperty('opacity',String(r.opacity*(r.filled?1-fill:1)),'important');
        }
      }
    };
    return {drawables:records.length,stages,method:'Semantic groups progressively outlined and filled; reconstructed from final SVG.'};
  },{order:options.order});
  if(options.format==='html'){
    await page.evaluate(()=>window.replayAt(1));
    if(!baseline.equals(await page.screenshot()))throw Error('Final step frame differs from source.');
    const file=join(out,'replay.html');await writeFile(file,drawingHtml(serialized,steps,seconds));
    const exported=await browser.newPage({viewport:dimensions,deviceScaleFactor:1});
    await exported.goto(pathToFileURL(file).href);
    await exported.evaluate(({width,height})=>{
      window.replayAt(1);
      const svg=document.querySelector('.canvas > svg');
      // Match only viewport framing; keep the exported drawing's inherited paint/font styles.
      Object.assign(svg.style,{width:width+'px',height:height+'px',maxWidth:'none',maxHeight:'none'});
      Object.assign(svg.parentElement.style,{position:'fixed',left:'0',top:'0',padding:'0',border:'0',borderRadius:'0',display:'block'});
      return document.fonts.ready;
    },dimensions);
    if(!baseline.equals(await exported.locator('.canvas > svg').screenshot()))throw Error('Exported HTML final frame differs from source.');
    await exported.close();
    report={...dimensions,...plan,seconds,final_frame_matches_reference:true,files:{html:{file,bytes:(await stat(file)).size}}};
  }else{
  const count=Math.round(seconds*fps),drawingSeconds=seconds-1.2;
  for(let i=0;i<count;i++){
    const t=timeline&&i===count-1?seconds:i/fps,p=Math.max(0,Math.min(1,(t-.2)/drawingSeconds));
    if(timeline)await page.evaluate(t=>window.timelineAt(t),t);
    else await page.evaluate(p=>window.replayAt(p),p);
    await page.screenshot({path:join(out,'frames',`${String(i).padStart(5,'0')}.png`)});
    if(i===0||i===Math.floor(count/2)||i===count-1)console.log(`Rendered frame ${i+1}/${count}`);
  }
  const last=await readFile(join(out,'frames',`${String(count-1).padStart(5,'0')}.png`));
  if(!timeline&&!baseline.equals(last))throw Error('Final replay frame differs from static browser render.');
  report={source:resolve(input),...dimensions,fps,seconds:count/fps,frames:count,background:'white',final_frame_matches_reference:baseline.equals(last),...plan,files:{}};
  if(timeline)report.final_timeline_state=await page.evaluate(()=>window.timelineState);
  }
}finally{await browser.close();}

function ffmpeg(args){
  const p=spawnSync(options.ffmpeg,['-hide_banner','-loglevel','error','-n',...args],{encoding:'utf8',windowsHide:true});
  if(p.error||p.status!==0)throw Error(p.stderr||String(p.error));
}
const sequence=join(out,'frames','%05d.png'),stem=timeline?'process':'replay';
if(['mp4','both'].includes(options.format)){
  const file=join(out,stem+'.mp4');
  ffmpeg(['-framerate',String(fps),'-i',sequence,'-c:v','libx264','-crf','20','-preset','medium','-pix_fmt','yuv420p','-movflags','+faststart',file]);
  report.files.mp4={file,bytes:(await stat(file)).size,encoding:'H.264 CRF20 yuv420p'};
}
if(['gif','both'].includes(options.format)){
  const file=join(out,stem+'.gif');
  ffmpeg(['-framerate',String(fps),'-i',sequence,'-filter_complex','[0:v]split[a][b];[a]palettegen=stats_mode=diff[p];[b][p]paletteuse=dither=sierra2_4a','-loop','0',file]);
  report.files.gif={file,bytes:(await stat(file)).size,encoding:'Global 256-color palette, Sierra dithering'};
}
report.elapsed_seconds=(Date.now()-started)/1000;
await writeFile(join(out,'replay.json'),JSON.stringify(report,null,2));
console.log(JSON.stringify({files:report.files,elapsed_seconds:report.elapsed_seconds,final_frame_matches_reference:report.final_frame_matches_reference}));
