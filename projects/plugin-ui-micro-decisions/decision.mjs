// Synthetic ambiguity. The result records one decision; it does not edit a taxonomy.
export const decision={
  id:'ontology-alignment-parent',revision:1,term:'Ontology alignment',
  question:'Where should Ontology alignment belong?',
  constraint:'Choose one primary parent in this taxonomy of technical work.',
  definition:'Match concepts across ontologies while preserving their meaning.',
  options:[
    {id:'knowledge-modeling',label:'Knowledge modeling',sibling:'Concept definition',reason:'Keep methods for defining and relating meaning together.',evidence:'The work identifies equivalence and broader or narrower relations between concepts.',source:'Scope note A'},
    {id:'data-integration',label:'Data integration',sibling:'Schema mapping',reason:'Keep methods for connecting independent information sources together.',evidence:'The work makes independently described datasets usable together across systems.',source:'Scope note B'}
  ]
};
export function createDecisionStore(){let receipt=null;return {
  state:()=>({decision:structuredClone(decision),receipt:structuredClone(receipt)}),
  async choose(input){
    if(input.decisionId!==decision.id||input.expectedRevision!==decision.revision)return {ok:false,error:'The question changed. Reopen it before choosing.'};
    if(input.optionId!==null&&!decision.options.some(o=>o.id===input.optionId))return {ok:false,error:'Choose one of the offered placements.'};
    await new Promise(r=>setTimeout(r,250));
    if(receipt){if(receipt.requestId===input.requestId&&receipt.optionId===input.optionId)return {ok:true,receipt};return {ok:false,error:'A decision has already been recorded for this question.'};}
    receipt={decisionId:decision.id,questionRevision:decision.revision,optionId:input.optionId,outcome:input.optionId===null?'deferred':'selected',requestId:input.requestId};return {ok:true,receipt};
  }
};}
