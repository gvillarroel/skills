/* Shared semantic surfaces and reversible parent-clock focus. No timer or network. */
(()=>{'use strict';
 const fallback={ink:'#333e48',red:'#9e1b32',accent:'#e8002a',muted:'#696969',line:'#828282',quiet:'#e7e7e7',white:'#ffffff',secondary:'#696969'};
 function colors(root=document.documentElement){const css=getComputedStyle(root),roles={ink:'ink',red:'primary',muted:'muted',line:'line',quiet:'quiet',white:'surface',secondary:'secondary-highlight'};return Object.fromEntries(Object.entries(fallback).map(([k,v])=>[k,roles[k]?css.getPropertyValue('--lw-'+roles[k]).trim()||v:v]));}
 const fontScale=(root=document.documentElement)=>parseFloat(getComputedStyle(root).getPropertyValue('--lw-font-scale'))||1;
 const lineWidth=(root=document.documentElement)=>parseFloat(getComputedStyle(root).getPropertyValue('--lw-line-width'))||2;
 const tag=e=>e.tagName?.toLowerCase(),shape=e=>['rect','circle','ellipse','polygon','path'].includes(tag(e));
 const preserve=e=>e.hasAttribute('data-encoding')||e.dataset.lwPreserve==='paint'||e.hasAttribute('data-color-role');
 const bounds=e=>e.getBoundingClientRect();
 function inside(text,face){const a=bounds(text),b=bounds(face);return a.width+a.height>0&&b.width>0&&a.left>=b.left-1&&a.right<=b.right+1&&a.top>=b.top-1&&a.bottom<=b.bottom+1;}
 function textColor(fill,c){const rgb=fill.match(/\d+(?:\.\d+)?/g)?.slice(0,3).map(Number);if(!rgb)return c.ink;const lum=a=>a.map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((v,x,i)=>v+x*[.2126,.7152,.0722][i],0),a=lum(rgb),contrast=b=>(Math.max(a,b)+.05)/(Math.min(a,b)+.05),ink=lum(c.ink.match(/[0-9a-f]{2}/gi).map(v=>parseInt(v,16)));return contrast(ink)>=4.5?c.ink:contrast(1)>=4.5?c.white:'#000000';}
 const labelSelector='text,tspan,foreignObject p,foreignObject span';
 const labelProperty=e=>['text','tspan'].includes(tag(e))?'fill':'color';
 const iconSelector='[data-lw-icon="monochrome"],[data-lw-icon="true"]';
 const iconPart=e=>e.closest?.(iconSelector);
 const glyphs=root=>[...(root.matches?.(iconSelector)?[root]:[]),...root.querySelectorAll(iconSelector)].filter(e=>!e.closest('defs')&&e.dataset.lwPreserve!=='paint');
 const area=e=>bounds(e).width*bounds(e).height;
 const faces=root=>[...root.querySelectorAll('[data-lw-surface]')].filter(e=>shape(e)&&!iconPart(e)).sort((a,b)=>area(a)-area(b));
 const parentFace=(element,items)=>items.find(e=>!element.contains(e)&&inside(element,e));
 const rgb=value=>{const hex=String(value).match(/^#([\da-f]{6})$/i);return hex?[0,2,4].map(i=>parseInt(hex[1].slice(i,i+2),16)):String(value).match(/[\d.]+/g)?.slice(0,3).map(Number);};
 const sameColor=(a,b)=>JSON.stringify(rgb(a))===JSON.stringify(rgb(b));
 const foreground=(face,c)=>sameColor(getComputedStyle(face).fill,c.red)?c.white:textColor(getComputedStyle(face).fill,c);
 let serial=0;
 const filterRoots=new WeakMap(),filterColors=new Map(),centerBases=new WeakMap();
 function inkFilter(root,color,icon){
  const svg=tag(root)==='svg'?root:root.ownerSVGElement;if(!svg)return null;
  let entries=filterRoots.get(icon);if(!entries){entries=new Map();filterRoots.set(icon,entries);}
  const box=icon.getBBox?.(),key=color+':'+(box?[box.x,box.y,box.width,box.height].join(','):'css');if(entries.has(key))return entries.get(key);
  let defs=svg.querySelector(':scope > defs');if(!defs){defs=document.createElementNS('http://www.w3.org/2000/svg','defs');svg.prepend(defs);}
  const id='lw-ink-'+(++serial),filter=document.createElementNS(svg.namespaceURI,'filter'),matrix=document.createElementNS(svg.namespaceURI,'feColorMatrix'),channels=rgb(color).map(v=>v/255);
  filter.setAttribute('id',id);filter.setAttribute('color-interpolation-filters','sRGB');
  if(box&&(!box.width||!box.height)){const padding=Math.max(8,box.width*.25,box.height*.25),x=box.x-(tag(icon)==='use'?icon.x.baseVal.value:0),y=box.y-(tag(icon)==='use'?icon.y.baseVal.value:0);filter.setAttribute('filterUnits','userSpaceOnUse');filter.setAttribute('x',x-padding);filter.setAttribute('y',y-padding);filter.setAttribute('width',box.width+padding*2);filter.setAttribute('height',box.height+padding*2);}
  else{filter.setAttribute('x','-25%');filter.setAttribute('y','-25%');filter.setAttribute('width','150%');filter.setAttribute('height','150%');}
  matrix.setAttribute('type','matrix');matrix.setAttribute('values',`0 0 0 0 ${channels[0]} 0 0 0 0 ${channels[1]} 0 0 0 0 ${channels[2]} 0 0 0 1 0`);filter.append(matrix);defs.append(filter);entries.set(key,id);filterColors.set(id,color);return id;
 }
 function iconContrast(root,set=(e,k,v)=>e.style.setProperty(k,v,'important')){
  const c=colors(root),items=faces(root);for(const icon of glyphs(root)){
   const face=parentFace(icon,items),ink=face?foreground(face,c):c.ink,id=inkFilter(root,ink,icon);if(!id)continue;
   set(icon,'filter',`url("#${id}")`);set(icon,'color',ink);
  }
 }
 function contentFace(root,content){
  const id=content.dataset.lwFor;if(id){const face=root.ownerDocument.getElementById(id);return face&&root.contains(face)?face:null;}
  const candidates=[...content.parentElement.children].filter(e=>shape(e)&&e.hasAttribute('data-lw-surface')&&!iconPart(e));return candidates.length===1?candidates[0]:null;
 }
 function adoptContent(root){
  for(const face of faces(root)){
   if(face.dataset.lwSurface!=='item'||preserve(face)||face.dataset.lwAlign==='preserve')continue;
   if([...root.querySelectorAll('[data-lw-content]')].some(e=>contentFace(root,e)===face))continue;
   const parent=face.parentElement,candidates=[...parent.children].filter(e=>e!==face&&!e.matches('[data-lw-content]')&&(e.matches('text,foreignObject,g.label')||e.matches(iconSelector))&&inside(e,face)&&!e.querySelector('[data-lw-surface]'));
   if(!candidates.length)continue;
   if(!face.id)face.id='lw-face-'+(++serial);
   const group=document.createElementNS('http://www.w3.org/2000/svg','g');group.setAttribute('data-lw-content','');group.setAttribute('data-lw-for',face.id);parent.insertBefore(group,candidates[0]);for(const child of candidates)group.append(child);
  }
 }
 function center(root){
  adoptContent(root);const results=[];
  for(const content of root.querySelectorAll('[data-lw-content]')){
   const face=contentFace(root,content);if(!face||!content.getScreenCTM||content.contains(face))continue;
   let a=bounds(content),b=bounds(face);if(a.width+a.height<=0||!b.width||!b.height)continue;
   if(!centerBases.has(content))centerBases.set(content,content.getAttribute('transform'));
   const base=centerBases.get(content);if(base===null)content.removeAttribute('transform');else content.setAttribute('transform',base);
   a=bounds(content);b=bounds(face);const dx=(b.left+b.right-a.left-a.right)/2,dy=(b.top+b.bottom-a.top-a.bottom)/2,inverse=content.parentElement.getScreenCTM()?.inverse();if(!inverse)continue;
   const origin=new DOMPoint(0,0).matrixTransform(inverse),delta=new DOMPoint(dx,dy).matrixTransform(inverse),x=delta.x-origin.x,y=delta.y-origin.y;
   content.setAttribute('transform',`translate(${+x.toFixed(6)} ${+y.toFixed(6)})${base?' '+base:''}`);results.push({id:face.id,dx,dy});
  }
  return results;
 }
 function contrast(root){const c=colors(root),items=faces(root).filter(e=>e.dataset.lwSurface==='item');for(const t of root.querySelectorAll(labelSelector)){const face=parentFace(t,items);if(face)t.style.setProperty(labelProperty(t),foreground(face,c),'important');}iconContrast(root);}
 const previous=new WeakMap();
 function restore(root){for(const[e,properties,hadStyle]of previous.get(root)||[]){for(const[name,value,priority]of properties){if(value)e.style.setProperty(name,value,priority);else e.style.removeProperty(name)}if(!hadStyle&&!e.getAttribute('style'))e.removeAttribute('style');}previous.delete(root);for(const e of root.querySelectorAll('[data-lw-focus]'))e.removeAttribute('data-lw-focus');root.removeAttribute?.('data-lw-focus');}
 function finish(root){
  if(!root?.querySelectorAll)throw Error('A surface root is required.');restore(root);const c=colors(root),faces=[...root.querySelectorAll('[data-lw-surface]')].filter(e=>shape(e)&&!iconPart(e));
  for(const e of faces){const kind=e.dataset.lwSurface,s=getComputedStyle(e);if(kind==='group'){e.style.setProperty('fill',c.white,'important');e.style.setProperty('stroke',c.line,'important');e.style.setProperty('stroke-width','2px','important');}
   else if(kind==='item'){if(!preserve(e)&&(s.fill==='rgb(255, 255, 255)'||s.fill==='none'))e.style.setProperty('fill',c.quiet,'important');e.style.setProperty('stroke','none','important');e.style.setProperty('stroke-width','0px','important');}}
  center(root);contrast(root);
 }
 function focus(root,target,role='primary'){
  if(!root?.querySelectorAll)throw Error('A focus root is required.');const targets=(Array.isArray(target)?target:[target]).filter(Boolean);
  if(targets.some(t=>!root.contains(t)))throw Error('The focus target must belong to its root.');if(!['primary','secondary'].includes(role))throw Error('Use primary or secondary emphasis.');
  restore(root);if(!targets.length)return;const c=colors(root),color=role==='primary'?c.red:c.secondary,saved=new Map(),elements=new Set(),groups=targets.some(t=>t.dataset.lwFocusMode==='group'||t.querySelector('[data-lw-surface="group"]'));
  for(const t of targets){t.setAttribute('data-lw-focus',role);elements.add(t);for(const e of t.querySelectorAll('rect,circle,ellipse,polygon,path,'+labelSelector))elements.add(e);}
  const allItems=[...root.querySelectorAll('[data-lw-surface="item"]')].filter(e=>shape(e)&&!iconPart(e));
  for(const t of targets.filter(e=>['text','tspan'].includes(tag(e))||e.matches(iconSelector))){const face=allItems.filter(e=>inside(t,e)).sort((a,b)=>bounds(a).width*bounds(a).height-bounds(b).width*bounds(b).height)[0];if(face){elements.add(face);for(const label of root.querySelectorAll('text'))if(inside(label,face))elements.add(label);}}
  for(const face of [...elements].filter(e=>shape(e)&&e.dataset.lwSurface!=='group'&&e.dataset.focusFill!=='outline'))for(const label of root.querySelectorAll(labelSelector))if(inside(label,face))elements.add(label);
  const set=(e,name,value)=>{if(!saved.has(e))saved.set(e,{properties:[],hadStyle:e.hasAttribute('style')});saved.get(e).properties.push([name,e.style.getPropertyValue(name),e.style.getPropertyPriority(name)]);e.style.setProperty(name,value,'important');};
  const faces=[];
  for(const e of elements){if(!shape(e)||e.closest('defs')||iconPart(e))continue;const kind=e.dataset.lwSurface,plain=['rect','circle','ellipse','polygon'].includes(tag(e));if(kind==='group'||e.dataset.focusFill==='outline'){set(e,'fill',c.white);set(e,'stroke',color);set(e,'stroke-width','2px');}
   else if(kind==='item'||e.dataset.focusFill==='solid'||plain){if(!groups&&!preserve(e)&&(kind==='item'||e.dataset.focusFill==='solid'||getComputedStyle(e).fill==='rgb(255, 255, 255)'))set(e,'fill',color);set(e,'stroke','none');set(e,'stroke-width','0px');faces.push(e);}}
  for(const e of elements){if(!e.matches(labelSelector))continue;const face=faces.find(f=>inside(e,f)),onFill=e.closest('[data-focus-on-fill]');set(e,labelProperty(e),face?foreground(face,c):onFill&&faces.some(f=>getComputedStyle(f).fill!=='none')?c.white:color);}
  iconContrast(root,set);previous.set(root,[...saved].map(([e,s])=>[e,s.properties,s.hadStyle]));
 }
 function audit(root){const violations=[];let items=0,groups=0;const frame=root.getBoundingClientRect();for(const e of root.querySelectorAll('[data-lw-surface]')){if(!shape(e)||e.closest('defs')||iconPart(e))continue;const s=getComputedStyle(e),b=bounds(e);let shown=b.width>0&&b.height>0&&b.right>frame.left&&b.left<frame.right&&b.bottom>frame.top&&b.top<frame.bottom;for(let p=e;p&&p!==root.parentElement;p=p.parentElement){const q=getComputedStyle(p);if(q.display==='none'||q.visibility==='hidden'||+q.opacity<.01)shown=false;}if(!shown)continue;const kind=e.dataset.lwSurface;if(kind==='item'){items++;if(s.stroke!=='none'&&parseFloat(s.strokeWidth)>0)violations.push({kind:'item-border',id:e.id,stroke:s.stroke});}if(kind==='group'){groups++;if(s.fill!=='rgb(255, 255, 255)')violations.push({kind:'group-filled',id:e.id,fill:s.fill});}}return{ok:!violations.length,items,groups,violations};}
 const baseAudit=audit;
 function auditContent(root){
  const result=baseAudit(root),c=colors(root),items=faces(root),frame=bounds(root);let icons=0,centered=0,whiteIcons=0;
  const shown=e=>{const b=bounds(e);if(b.width+b.height<=0||b.right<frame.left||b.left>frame.right||b.bottom<frame.top||b.top>frame.bottom)return false;for(let p=e;p&&p!==root.parentElement;p=p.parentElement){const s=getComputedStyle(p);if(s.display==='none'||s.visibility==='hidden'||+s.opacity<.01)return false;}return true;};
  for(const icon of glyphs(root)){if(!shown(icon))continue;const face=parentFace(icon,items);if(!face)continue;icons++;const expected=foreground(face,c),id=getComputedStyle(icon).filter.match(/#([^"')]+)/)?.[1],actual=filterColors.get(id);
   if(actual&&sameColor(actual,c.white))whiteIcons++;if(!actual||!sameColor(actual,expected))result.violations.push({kind:'icon-contrast',id:icon.id,expected,actual:actual||'unverified paint'});
  }
  for(const content of root.querySelectorAll('[data-lw-content]')){if(!shown(content))continue;const face=contentFace(root,content);if(!face)continue;centered++;const a=bounds(content),b=bounds(face),dx=(a.left+a.right-b.left-b.right)/2,dy=(a.top+a.bottom-b.top-b.bottom)/2;
   if(Math.abs(dx)>2||Math.abs(dy)>2)result.violations.push({kind:'content-not-centered',id:face.id,dx:+dx.toFixed(3),dy:+dy.toFixed(3)});
   if(!inside(content,face))result.violations.push({kind:'content-overflow',id:face.id});
  }
  return {...result,ok:!result.violations.length,icons,whiteIcons,centered};
 }
 globalThis.LineWorldTheme=Object.freeze({colors,fontScale,lineWidth,finish,focus,contrast,center,audit:auditContent});
})();
