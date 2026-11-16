#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Shared browser check for the video's red/gray-first, black-last default."""

BROWSER_CHECK=r"""() => {
 const stage=document.querySelector('#stage'),frame=stage.getBoundingClientRect(),darkBlocks=[],pinkSurfaces=[];
 const rgb=s=>{const m=s.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);return m?m.slice(1).map(Number):null};
 const dark=s=>{const c=rgb(s);return c&&Math.max(...c)-Math.min(...c)<30&&Math.max(...c)<115};
 const visible=e=>{for(let p=e;p&&p!==stage.parentNode;p=p.parentElement){const s=getComputedStyle(p);if(s.display==='none'||s.visibility==='hidden'||+s.opacity<.01)return false}return true};
 for(const e of stage.querySelectorAll('rect,circle,ellipse,path,polygon')){
  if(!visible(e))continue;const s=getComputedStyle(e),b=e.getBoundingClientRect();
  const width=Math.max(0,Math.min(b.right,frame.right)-Math.max(b.x,frame.x)),height=Math.max(0,Math.min(b.bottom,frame.bottom)-Math.max(b.y,frame.y));
  const c=rgb(s.fill),alpha=Number(s.fillOpacity)*Number(s.opacity),paint=c?.map(v=>Math.round(255+(v-255)*alpha));
  if(width>4&&height>4&&paint&&paint[0]>=220&&paint[1]>=150&&paint[2]>=150&&paint[0]-paint[1]>=20&&paint[2]>paint[1]&&alpha>.01)pinkSurfaces.push({tag:e.tagName,id:e.id,fill:s.fill,fillOpacity:s.fillOpacity});
  if(width*height<=frame.width*frame.height*.02)continue;
  const secondary=e.tagName.toLowerCase()==='rect'&&e.dataset.colorRole==='secondary-highlight'&&e.dataset.encoding==='quantity'&&Number.isFinite(+e.dataset.value)&&+e.dataset.value>0&&s.fill==='rgb(105, 105, 105)'&&width*height<=frame.width*frame.height*.12;
  if(dark(s.fill)&&+s.fillOpacity>.15&&!secondary||dark(s.stroke)&&parseFloat(s.strokeWidth)>6&&+s.strokeOpacity>.15)darkBlocks.push({tag:e.tagName,id:e.id,fill:s.fill,stroke:s.stroke,width,height});
 }
 return {ok:!darkBlocks.length&&!pinkSurfaces.length,darkBlocks,pinkSurfaces,primary:STORY.colorSequence[0],blackIndex:STORY.colorSequence.indexOf('#000000'),sequenceLength:STORY.colorSequence.length};
}"""
