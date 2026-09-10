/** Discrete drawing events shared by browser export and the offline player. */
export function setupDrawingSteps(plan){
  const svg=document.querySelector('svg'),ns=svg.namespaceURI,index=new Map();
  for(const n of svg.querySelectorAll('[id]')){if(index.has(n.id))throw Error('Duplicate SVG ID: '+n.id);index.set(n.id,n);}
  const definitions='defs,clipPath,mask,marker,pattern,symbol';
  const nodes=[...svg.querySelectorAll('path,rect,circle,ellipse,line,polyline,polygon,text,use')].filter(n=>!n.closest(definitions));
  for(const use of nodes.filter(n=>n.localName==='use')){
    const ref=index.get((use.getAttribute('href')||use.getAttributeNS('http://www.w3.org/1999/xlink','href')||'').slice(1));
    if(!ref?.closest(definitions))throw Error('Move use definitions into defs before step replay.');
  }
  const originals=new Map(nodes.map(n=>[n,n.getAttribute('style')]));
  const restore=n=>{const value=originals.get(n);if(value===null)n.removeAttribute('style');else n.setAttribute('style',value);};
  let steps=plan?.steps;
  if(!steps){
    const groups=[...new Set(nodes.map(n=>n.closest('g[id]')?.id||n.id).filter(Boolean))];
    steps=groups.flatMap(id=>[{label:id+' · 轮廓',ids:[id],mode:'outline'},{label:id+' · 成形',ids:[id],mode:'show'}]);
  }
  if(!Array.isArray(steps)||!steps.length)throw Error('Provide at least one drawing step.');
  const outlines=new Map();
  const events=steps.map(step=>{
    if(!Array.isArray(step.ids)||!step.ids.length||!['outline','show'].includes(step.mode))throw Error('Each drawing step needs ids and outline/show mode.');
    const targets=step.ids.map(id=>{if(!index.has(id))throw Error('Unknown drawing step ID: '+id);return index.get(id);});
    const members=nodes.filter(n=>targets.some(t=>t===n||t.contains(n)));
    if(!members.length)throw Error('Drawing step has no visible objects: '+step.ids.join(','));
    if(step.mode==='outline')for(const node of members){
      if(outlines.has(node)||typeof node.getTotalLength!=='function')continue;
      const clone=node.cloneNode(false),cs=getComputedStyle(node);clone.removeAttribute('id');
      const set=(k,v)=>clone.style.setProperty(k,v,'important');
      set('fill','none');set('stroke',cs.stroke!=='none'?cs.stroke:(cs.fill.startsWith('url(')||cs.fill==='none'?'#6a806a':cs.fill));
      set('stroke-width',cs.stroke!=='none'?cs.strokeWidth:'1.25');
      for(const prop of ['marker-start','marker-mid','marker-end'])set(prop,'none');
      clone.setAttribute('data-drawing-outline','');node.after(clone);outlines.set(node,clone);
    }
    return {label:String(step.label||step.ids.join(', ')),mode:step.mode,members};
  });
  // Unassigned objects appear at completion; the final state always restores the full source.
  events.push({label:'完成',mode:'complete',members:nodes});
  const apply=count=>{
    count=Math.max(0,Math.min(events.length,Math.floor(count)));
    for(const n of nodes){restore(n);n.style.setProperty('visibility','hidden','important');}
    for(const outline of outlines.values())outline.style.setProperty('display','none','important');
    for(const event of events.slice(0,count)){
      for(const n of event.members){
        if(event.mode==='outline')outlines.get(n)?.style.setProperty('display','inline','important');
        else{restore(n);outlines.get(n)?.style.setProperty('display','none','important');}
      }
    }
    const state={step:count,total:events.length,label:count?events[count-1].label:'准备绘制'};
    window.drawingStepState=state;return state;
  };
  window.setDrawingStep=apply;
  window.replayAt=p=>apply(p>=1?events.length:Math.floor(Math.max(0,p)*events.length));
  apply(0);
  return {drawables:nodes.length,stages:events.map((e,i)=>({id:i,label:e.label,mode:e.mode})),method:'Discrete semantic drawing steps; no temporal interpolation.'};
}

export function drawingHtml(svg,plan,seconds){
  const json=value=>JSON.stringify(value).replace(/</g,'\\u003c');
  return `<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ScanSci · 绘制回放</title>
<style>*{box-sizing:border-box}body{margin:0;background:#f1f4ec;color:#24483a;font:16px system-ui,"Microsoft YaHei",sans-serif}main{max-width:1050px;margin:32px auto;padding:24px}h1{font-size:27px}.canvas{color:initial;font:initial;background:white;border:1px solid #d7e0d0;border-radius:16px;padding:16px;display:flex;justify-content:center}.canvas>svg{max-width:100%;width:auto;height:auto;max-height:65vh}.controls{display:flex;gap:14px;align-items:center;flex-wrap:wrap;margin:22px 0}button,select{font:inherit;padding:8px 16px;border-radius:8px;border:1px solid #c6d5c1;background:white;color:#24483a}button{cursor:pointer}.controls input{flex:1;min-width:150px}p{color:#6c7f71}.step-label{font-weight:650}</style>
<main><h1>绘制回放</h1><p>按对象与绘画阶段重建步骤；每一步直接落下，原图中的色彩和明暗保留。</p><div class="canvas">${svg}</div><div class="controls"><button data-replay="play">播放</button><button data-replay="reset">重播</button><input data-replay="seek" aria-label="绘制步骤" type="range" min="0" value="0" step="1"><select data-replay="speed" aria-label="播放速度"><option value="0.5">0.5×</option><option value="1" selected>1×</option><option value="2">2×</option></select></div><div class="step-label" aria-live="polite"></div></main>
<script>(${setupDrawingSteps.toString()})(${json(plan)});
const controls=document.querySelector('main > .controls'),total=window.drawingStepState.total,seek=controls.querySelector('[data-replay=seek]'),play=controls.querySelector('[data-replay=play]'),speed=controls.querySelector('[data-replay=speed]');seek.max=total;let playing=false,position=0,last=0,generation=0;
function show(step){const state=window.setDrawingStep(step);seek.value=state.step;document.querySelector('main > .step-label').textContent=state.step+' / '+total+' · '+state.label;}
function pause(){playing=false;generation++;play.textContent='播放'}
function tick(now,token){if(!playing||token!==generation)return;position+=Math.max(0,now-last)/1000*Number(speed.value)*total/${seconds};last=now;show(Math.floor(position));if(position>=total){pause();return}requestAnimationFrame(now=>tick(now,token))}
function start(){if(position>=total)position=0;playing=true;const token=++generation;play.textContent='暂停';last=performance.now();requestAnimationFrame(now=>tick(now,token))}
play.onclick=()=>playing?pause():start();controls.querySelector('[data-replay=reset]').onclick=()=>{pause();position=0;show(0);start()};seek.oninput=()=>{pause();position=Number(seek.value);show(position)};show(0);
</script></html>`;
}
