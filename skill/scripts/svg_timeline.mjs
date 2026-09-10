/** Explicit process tracks; times are seconds and motion coordinates are SVG units. */
export async function installTimeline(page,timeline,seconds){
  return page.evaluate(({timeline,seconds})=>{
    if(!timeline||!Array.isArray(timeline.tracks)||!timeline.tracks.length)throw Error('Provide timeline tracks.');
    const svg=document.querySelector('svg'),ns=svg.namespaceURI;
    const ids=new Map();
    for(const node of svg.querySelectorAll('[id]')){
      if(ids.has(node.id))throw Error('Duplicate SVG ID: '+node.id);
      ids.set(node.id,node);
    }
    const finite=(v)=>typeof v==='number'&&Number.isFinite(v);
    const tracks=timeline.tracks.map(track=>{
      const {type,start,end}=track;
      if(!finite(start)||!finite(end)||start<0||end<=start||end>seconds)throw Error('Track interval outside duration.');
      const node=ids.get(track.id);
      if(!node)throw Error('Unknown track ID: '+track.id);
      if(type==='flow'){
        if(typeof node.getTotalLength!=='function'||!node.getTotalLength())throw Error('Flow requires a nonempty geometry path.');
        if(!Number.isInteger(track.count)||track.count<1||track.count>100||!finite(track.radius)||track.radius<=0)throw Error('Flow requires count 1–100 and positive radius.');
        if(!/^#[0-9a-f]{6}$/i.test(track.color||''))throw Error('Use a six-digit flow color.');
        const group=document.createElementNS(ns,'g');group.setAttribute('data-flow',track.id);svg.append(group);
        const dots=Array.from({length:track.count},()=>{const dot=document.createElementNS(ns,'circle');dot.setAttribute('r',track.radius);dot.setAttribute('fill',track.color);group.append(dot);return dot;});
        return {...track,node,group,dots,length:node.getTotalLength()};
      }
      if(!['opacity','translate','rotate'].includes(type))throw Error('Unknown track type: '+type);
      if(type!=='opacity'&&['all','transform','translate','rotate','scale'].some(p=>node.style.getPropertyValue(p)))throw Error('Normalize inline CSS transforms before animating: '+track.id);
      if(type==='translate'&&(!Array.isArray(track.from)||!Array.isArray(track.to)||track.from.length!==2||track.to.length!==2||![...track.from,...track.to].every(finite)))throw Error('Translate requires two coordinate pairs.');
      if(type==='opacity'&&(![track.from,track.to].every(v=>finite(v)&&v>=0&&v<=1)))throw Error('Opacity endpoints must be 0–1.');
      if(type==='rotate'&&(![track.from,track.to].every(finite)||!Array.isArray(track.center)||track.center.length!==2||!track.center.every(finite)))throw Error('Rotate requires angles and center.');
      return {...track,node,base:node.getAttribute('transform')||''};
    });
    const controlled=new Set();
    for(const t of tracks){if(t.type==='flow')continue;const key=t.id+':'+(t.type==='opacity'?'opacity':'transform');if(controlled.has(key))throw Error('Combine conflicting tracks for '+t.id);controlled.add(key);}
    window.timelineAt=t=>{
      const states=[];
      // Update geometry before sampling flows, independent of track declaration order.
      for(const r of [...tracks.filter(r=>r.type!=='flow'),...tracks.filter(r=>r.type==='flow')]){
        const ordinal=tracks.indexOf(r);
        const p=Math.max(0,Math.min(1,(t-r.start)/(r.end-r.start))),mix=(a,b)=>a+(b-a)*p;
        if(r.type==='flow'){
          const active=t>=r.start&&t<r.end;r.group.style.display=active?'':'none';
          const matrix=svg.getScreenCTM().inverse().multiply(r.node.getScreenCTM());
          r.dots.forEach((dot,i)=>{const q=r.node.getPointAtLength(((p+i/r.count)%1)*r.length).matrixTransform(matrix);dot.setAttribute('cx',q.x);dot.setAttribute('cy',q.y);});
          states[ordinal]={id:r.id,type:r.type,active};
        } else if(r.type==='opacity'){
          const value=mix(r.from,r.to);r.node.style.setProperty('opacity',value,'important');states[ordinal]={id:r.id,type:r.type,value};
        } else {
          const value=r.type==='translate'?r.from.map((v,i)=>mix(v,r.to[i])):mix(r.from,r.to);
          const transform=r.type==='translate'?`translate(${value.join(' ')})`:`rotate(${value} ${r.center.join(' ')})`;
          r.node.setAttribute('transform',`${r.base} ${transform}`);states[ordinal]={id:r.id,type:r.type,value};
        }
      }
      window.timelineState=states;return states;
    };
    window.timelineAt(0);
    return {method:'Explicit scientific process timeline',tracks:timeline.tracks,description:timeline.description||'',time_scale:timeline.time_scale||'illustrative'};
  },{timeline,seconds});
}
