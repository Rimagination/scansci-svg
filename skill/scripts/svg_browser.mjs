/** Shared static SVG loader: inert parsing, explicit elements, no network. */
export async function loadSvg(page,source,width){
  if(/<!DOCTYPE|<!ENTITY/i.test(source))throw Error('SVG with DTD/entities is unsupported.');
  await page.route('**/*',route=>route.abort());
  await page.setContent('<!doctype html><html><head><style>html,body{margin:0;padding:0;background:#fff;overflow:hidden}svg{display:block}</style></head><body></body></html>');
  const dimensions=await page.evaluate(({source,width})=>{
    const doc=new DOMParser().parseFromString(source,'image/svg+xml');
    if(doc.querySelector('parsererror'))throw Error('Invalid SVG XML.');
    const svg=doc.documentElement;
    if(svg.localName!=='svg'||svg.namespaceURI!=='http://www.w3.org/2000/svg')throw Error('Missing SVG namespace.');
    const supported=new Set(['svg','g','defs','title','desc','path','rect','circle','ellipse','line','polyline','polygon','text','tspan','textPath','linearGradient','radialGradient','stop','clipPath','mask','marker','pattern','symbol','use']);
    for(const node of doc.querySelectorAll('*')){
      if(node.namespaceURI!==svg.namespaceURI||!supported.has(node.localName))throw Error('Normalize unsupported element first: '+node.localName);
      for(const attr of node.attributes){
        if(/^on/i.test(attr.localName))throw Error('Event attributes unsupported.');
        if(attr.localName==='base'&&attr.namespaceURI==='http://www.w3.org/XML/1998/namespace')throw Error('External base URI unsupported.');
        if(attr.localName==='href'&&!attr.value.startsWith('#'))throw Error('External references unsupported.');
        for(const match of attr.value.matchAll(/url\((.*?)\)/gi))if(!/^['"]?#/.test(match[1].trim()))throw Error('External style URL unsupported.');
        if(/@import|animation\s*:|transition\s*:/i.test(attr.value))throw Error('Animated/imported styles unsupported.');
      }
      if(node.style&&[...node.style].some(p=>/^(?:-webkit-)?(?:animation|transition)(?:-|$)/.test(p)))throw Error('Animated/imported styles unsupported.');
      // CSSOM resolves escaped function names before checking resource references.
      if(node.style)for(const match of node.style.cssText.matchAll(/url\((.*?)\)/gi))if(!/^['"]?#/.test(match[1].trim()))throw Error('External style URL unsupported.');
    }
    for(const property of ['all','width','height','min-width','max-width','min-height','max-height','inline-size','block-size','min-inline-size','max-inline-size','min-block-size','max-block-size']) {
      if(svg.style.getPropertyValue(property))throw Error(`Normalize root viewport style first: ${property}`);
    }
    const box=svg.getAttribute('viewBox')?.trim().split(/[\s,]+/).map(Number);
    if(!box||box.length!==4||!box.every(Number.isFinite)||box[2]<=0||box[3]<=0)throw Error('A positive viewBox is required.');
    const height=2*Math.round(width*box[3]/box[2]/2);
    if(height<2||height>3840)throw Error('Output height outside supported range.');
    svg.setAttribute('width',width);svg.setAttribute('height',height);
    document.body.append(document.importNode(svg,true));
    return {width,height};
  },{source,width});
  await page.setViewportSize(dimensions);
  await page.evaluate(()=>document.fonts.ready);
  return dimensions;
}
