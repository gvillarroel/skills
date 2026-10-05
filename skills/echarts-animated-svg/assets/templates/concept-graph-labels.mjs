// Reflow existing native Line captions on the qualified display route.
// Call after native arrow insetting; no replacement marks or overlays are added.
export function settleConceptGraphCaptions(chart) {
  chart.getModel().eachSeriesByType('graph',series=>series.getGraph().eachEdge(edge=>{
    const element=edge.getGraphicEl(),text=element.getTextContent();
    if (!text || text.ignore) return;
    const line=element.childOfName('line');
    const source=edge.node1.getGraphicEl().getSymbolPath(),box=source.getBoundingRect().clone();
    box.applyTransform(source.getComputedTransform());
    let visibleStart=0;
    for(let t=0;t<=1;t+=.005){const p=line.pointAt(t);if(p[0]<box.x-4||p[0]>box.x+box.width+4||p[1]<box.y-4||p[1]>box.y+box.height+4){visibleStart=t;break;}}
    const position=(visibleStart+1)/2,middle=line.pointAt(position),tangent=line.tangentAt(position);
    const start=line.pointAt(0),end=line.pointAt(1),distance=8;
    text.x=middle[0];text.y=middle[1]-distance;
    text.originX=0;text.originY=distance;
    text.rotation=-Math.atan2(tangent[1],tangent[0])+(end[0]<start[0]?Math.PI:0);
    text.scaleX=text.scaleY=1;
    text.setStyle({align:'center',verticalAlign:'bottom'});
    text.markRedraw();
  }));
  chart.getZr().flush();
}
