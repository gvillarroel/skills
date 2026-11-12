// The native XY export remains intact on disk and in downloads. Only this
// sandboxed preview receives the compact toolbar and readiness bridge.
export const COMPACT_PREVIEW_SHIM='<style id="xy-compact-preview-style" data-xy-compact-preview>.xy [data-xy-slot="modebar"]{display:none!important}</style><script data-xy-compact-preview-bridge>window.addEventListener("message",function(event){if(event.source!==window.parent||!event.data||event.data.type!=="reflex-xy-preview-tools"||typeof event.data.visible!=="boolean")return;var style=document.getElementById("xy-compact-preview-style");if(style)style.disabled=event.data.visible;});(function ready(){var canvas=document.querySelector(".xy canvas");if(canvas&&canvas.width>0&&canvas.height>0){window.parent.postMessage({type:"reflex-xy-preview-ready"},"*");return;}setTimeout(ready,100);})();</script>';

export function embeddedPreviewHtml(html:string):string {
  if(!/<\/head>/i.test(html))throw new Error("The native chart HTML has no document head.");
  return html.replace(/<\/head>/i,()=>`${COMPACT_PREVIEW_SHIM}</head>`);
}
