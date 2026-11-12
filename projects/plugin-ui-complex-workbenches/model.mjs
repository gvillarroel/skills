// Shared synthetic model. No external data, credentials, or production actions.
export const START=Date.UTC(2026,10,11), STEP=15*60*1000, OBJECTIVE=250;
const domains=['Edge','Identity','Orders','Payments','Fulfillment','Catalog','Analytics','Platform'];
const roles=['API','Worker','Queue','Gateway','Ledger','Cache','Search','Events','Batch','Router','Store','Sync'];
export const services=Array.from({length:96},(_,i)=>({
  id:`svc-${String(i+1).padStart(3,'0')}`,name:`${domains[Math.floor(i/12)]} ${roles[i%12]}`,
  domain:domains[Math.floor(i/12)],owner:`${domains[Math.floor(i/12)]} team`,
  points:Array.from({length:96},(_,t)=>{const incident=(i===36||i===37||i===48)&&t>=64&&t<=78?260*Math.sin((t-63)/16*Math.PI):0;
    const missing=(i===36&&[27,28,70,71].includes(t))||(i%17===0&&t===12);
    return {time:START+t*STEP,p95:missing?null:Math.round(95+i*13%90+22*Math.sin(t/6+i)+incident),error:missing?null:Number((.12+Math.abs(Math.sin(t/8+i))*.25+incident/100).toFixed(2))};})
}));
const pairs=new Map();
for(let i=0;i<96;i++)for(const offset of [12,25]){const j=(i+offset)%96;pairs.set(`${i}-${j}`,{id:`edge-${i}-${j}`,source:services[i].id,target:services[j].id,kind:offset===12?'request':'event',rate:120+i*17%850});}
for(let i=40;i<54;i++)pairs.set(`36-${i}`,{id:`edge-36-${i}`,source:services[36].id,target:services[i].id,kind:'request',rate:60+i*9});
export const edges=[...pairs.values()];
export const byId=id=>services.find(s=>s.id===id);
export const windowPoints=(s,range)=>s.points.filter(p=>p.time>=START+range[0]*3600000&&p.time<START+range[1]*3600000);
export const maximum=(s,range)=>{const valid=windowPoints(s,range).filter(p=>p.p95!==null);return valid.length?Math.max(...valid.map(p=>p.p95)):null;};
export const data={schemaVersion:1,synthetic:true,timezone:'UTC',start:START,step:STEP,objective:OBJECTIVE,services,edges};
export function createBackend(){
  let revision=1;const records=[],receipts=new Map();
  return {
    state:()=>({revision,records:structuredClone(records),synthetic:true}),
    compete:()=>({revision:++revision,synthetic:true}),
    async apply(draft){
      const fingerprint=JSON.stringify([draft.targetId,draft.percent,typeof draft.reason==='string'?draft.reason.trim():draft.reason,draft.expectedRevision,draft.range??[]]);
      const replay=()=>{const stored=receipts.get(draft.requestId);return stored?.fingerprint===fingerprint?stored.result:{ok:false,error:'Request ID already used for a different plan',revision};};
      if(receipts.has(draft.requestId))return replay();
      await new Promise(r=>setTimeout(r,650));
      // Recheck idempotency after the asynchronous boundary as well.
      if(receipts.has(draft.requestId))return replay();
      if(draft.expectedRevision!==revision)return {ok:false,conflict:true,revision,expectedRevision:draft.expectedRevision};
      if(!byId(draft.targetId)||!Number.isInteger(draft.percent)||draft.percent<10||draft.percent>50||typeof draft.reason!=='string'||draft.reason.trim().length<8||typeof draft.requestId!=='string'||!draft.requestId)return {ok:false,error:'Invalid synthetic plan',revision};
      const record={id:`plan-${records.length+1}`,targetId:draft.targetId,percent:draft.percent,reason:draft.reason.trim(),revision:++revision,requestId:draft.requestId,range:structuredClone(draft.range??[])};
      records.push(record);const result={ok:true,record,revision,synthetic:true};receipts.set(draft.requestId,{fingerprint,result});return result;
    }
  };
}
