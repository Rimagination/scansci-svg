import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
import {resolve} from 'node:path';
import {loadSvg} from './svg_browser.mjs';
import {installTimeline} from './svg_timeline.mjs';
const {chromium}=await import(process.env.PLAYWRIGHT_MODULE?pathToFileURL(resolve(process.env.PLAYWRIGHT_MODULE)).href:'playwright');
const browser=await chromium.launch({headless:true,...(process.env.CHROME_PATH?{executablePath:process.env.CHROME_PATH}:{})});
try{
  const page=await browser.newPage();
  const source='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 100"><g transform="translate(20 10) scale(2)"><path id="route" d="M0 0L50 0" fill="none" stroke="blue"/></g><g id="object"><circle r="8" cx="80" cy="60"/></g><text id="label" x="20" y="80">Label</text></svg>';
  await loadSvg(page,source,400);
  const tracks=[{type:'flow',id:'route',start:0,end:4,count:1,radius:2,color:'#abcdef'},{type:'translate',id:'object',start:0,end:4,from:[0,0],to:[40,0]},{type:'opacity',id:'label',start:1,end:3,from:0,to:1}];
  await installTimeline(page,{tracks},4);
  const mid=await page.evaluate(()=>{const states=window.timelineAt(2),dot=document.querySelector('[data-flow] circle');return {x:Number(dot.getAttribute('cx')),y:Number(dot.getAttribute('cy')),states};});
  assert.equal(mid.x,70);assert.equal(mid.y,10);assert.deepEqual(mid.states[1].value,[20,0]);assert.equal(mid.states[2].value,.5);
  const end=await page.evaluate(()=>window.timelineAt(4));assert.equal(end[0].active,false);assert.deepEqual(end[1].value,[40,0]);assert.equal(end[2].value,1);
  await loadSvg(page,source.replace('<g transform=', '<g id="moving" transform='),400);
  await installTimeline(page,{tracks:[tracks[0],{type:'translate',id:'moving',start:0,end:4,from:[0,0],to:[20,0]}]},4);
  const moved=await page.evaluate(()=>{window.timelineAt(2);return Number(document.querySelector('[data-flow] circle').getAttribute('cx'));});
  assert.equal(moved,90); // Halfway shift is 10 local units, scaled by the ancestor's 2×.
  await loadSvg(page,source.replace('id="object"','id="object" style="transform:translateX(10px)"'),400);
  await assert.rejects(installTimeline(page,{tracks:[tracks[1]]},4),/Normalize inline CSS transforms/);
  await assert.rejects(installTimeline(page,{tracks:[{...tracks[0],id:'missing'}]},4),/Unknown track ID/);
  await assert.rejects(installTimeline(page,{tracks:[{...tracks[0],end:9}]},4),/outside duration/);
  await assert.rejects(loadSvg(page,'<svg xmlns="http://www.w3.org/2000/svg"><foreignObject/></svg>',400),/unsupported element/);
  await assert.rejects(loadSvg(page,source.replace('id="object"','id="object" style="transition-property:opacity;transition-duration:30s"'),400),/Animated\/imported styles/);
  console.log('Timeline: transformed route, endpoints, opacity, missing ID, duration and SVG loading passed.');
}finally{await browser.close();}
