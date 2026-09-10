import assert from 'node:assert/strict';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import {loadSvg} from './svg_browser.mjs';
import {setupDrawingSteps,drawingHtml} from './drawing_steps.mjs';
const {chromium}=await import(process.env.PLAYWRIGHT_MODULE?pathToFileURL(resolve(process.env.PLAYWRIGHT_MODULE)).href:'playwright');
const browser=await chromium.launch({headless:true,...(process.env.CHROME_PATH?{executablePath:process.env.CHROME_PATH}:{})});
try{
  const page=await browser.newPage();
  const source='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 150"><defs><linearGradient id="green"><stop stop-color="#396a38"/><stop offset="1" stop-color="#abbe65"/></linearGradient></defs><g id="body"><path id="base" d="M20 120Q10 20 160 20Q160 120 20 120Z" fill="url(#green)"/><path id="vein" d="M20 120L160 20" fill="none" stroke="#fff" stroke-width="2"/><text id="label" x="20" y="140">Leaf</text></g></svg>';
  const plan={steps:[{label:'线稿',mode:'outline',ids:['base']},{label:'固有色',mode:'show',ids:['base']},{label:'叶脉',mode:'show',ids:['vein']},{label:'标签',mode:'show',ids:['label']}]};
  await loadSvg(page,source,400);const before=await page.screenshot();
  await page.evaluate(setupDrawingSteps,plan);
  await page.evaluate(()=>window.setDrawingStep(1));
  assert.equal(await page.locator('#base').evaluate(n=>getComputedStyle(n).visibility),'hidden');
  assert.equal(await page.locator('[data-drawing-outline]').evaluate(n=>getComputedStyle(n).display),'inline');
  await page.evaluate(()=>window.replayAt(.42));const stateA=await page.screenshot();
  await page.evaluate(()=>window.replayAt(.48));assert.deepEqual(await page.screenshot(),stateA); // Same discrete event, no interpolation.
  assert.equal(await page.locator('#base').evaluate(n=>getComputedStyle(n).opacity),'1');
  assert.match(await page.locator('#base').getAttribute('fill'),/green/);
  await page.evaluate(()=>window.replayAt(1));assert.deepEqual(await page.screenshot(),before);
  let requests=0;page.on('request',()=>requests++);
  await page.setContent(drawingHtml(source,plan,3));
  assert.equal(await page.locator('canvas,image,script[src],link').count(),0);
  await page.locator('[data-replay=play]').click();await page.waitForFunction(()=>window.drawingStepState.step>0);
  await page.locator('[data-replay=play]').click();const paused=await page.evaluate(()=>window.drawingStepState.step);
  await page.waitForTimeout(180);assert.equal(await page.evaluate(()=>window.drawingStepState.step),paused);
  await page.locator('[data-replay=seek]').evaluate(n=>{n.value='5';n.dispatchEvent(new Event('input'));});assert.equal(await page.evaluate(()=>window.drawingStepState.step),5);
  assert.equal(await page.locator('svg #label').textContent(),'Leaf');
  assert.equal(await page.locator('svg #label').evaluate(n=>getComputedStyle(n).fontFamily),'"Times New Roman"');
  assert.equal(await page.locator('svg #label').evaluate(n=>getComputedStyle(n).color),'rgb(0, 0, 0)');
  await page.locator('[data-replay=reset]').click();assert.equal(await page.evaluate(()=>window.drawingStepState.step),0);
  assert.equal(requests,0);
  await assert.rejects(loadSvg(page,String.raw`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 150"><path id="x" style="fill:u\72l(https://example.com/paint.svg#p)" d="M0 0h100v100z"/></svg>`,400),/External style URL/);
  console.log('Discrete frames, source gradients, exact final render, offline HTML and playback controls passed.');
}finally{await browser.close();}
