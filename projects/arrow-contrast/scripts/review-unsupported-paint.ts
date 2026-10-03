// Run: node --experimental-strip-types projects/arrow-contrast/scripts/review-unsupported-paint.ts --phase before|final
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
const phase=process.argv[process.argv.indexOf('--phase')+1];
if(!['before','final'].includes(phase))throw Error('Specify evidence phase');
const helper=new URL(phase==='before'?'../../../evaluations/runs/20261003-arrow-echarts-animated-svg-final-4/workspace/echarts-colorsets.mjs':'../../../skills/echarts-animated-svg/assets/templates/echarts-colorsets.mjs',import.meta.url);
const {contrastSafeArrowStyle:safe,prepareColorsetOption:prepare}=await import(helper.href);
const cases=[{id:'gradient-arrow',style:{color:{type:'linear',colorStops:[{offset:0,color:'#ffffff'},{offset:1,color:'#cfcfcf'}]}}},
 {id:'unresolved-css-paint',style:{color:'var(--arrow-color)'}},
 {id:'percentage-alpha',style:{color:'rgba(0,0,0,25%)'}}];
const rows=cases.map(({id,style})=>{try{return{id,input:style,output:safe(style,'colorset1','#ffffff'),rejected:false};}catch(error){return{id,input:style,rejected:true,message:error.message};}});
let gradientBackingRejected=false;try{safe({color:'#000000'},'colorset1',{type:'linear',colorStops:[]});}catch{gradientBackingRejected=true;}
const passed=rows[0].rejected&&rows[1].rejected&&!rows[2].rejected&&rows[2].output.opacity===1&&rows[2].output.color==='#000000'&&gradientBackingRejected;
let preparedGradientRejected=false;try{prepare({backgroundColor:{type:'linear',colorStops:[{offset:0,color:'#000000'},{offset:1,color:'#ffffff'}]},series:[{type:'graph',edgeSymbol:['none','arrow'],data:[],links:[]}]});}catch{preparedGradientRejected=true;}
const report={phase,passed,rows,gradientBackingRejected,helperSha256:createHash('sha256').update(readFileSync(helper)).digest('hex'),helperSource:phase==='before'?'Sealed final-4 workspace helper, superseded by these counterexamples':'Current canonical runtime helper',scope:'Concrete helper counterexamples: unknown paint must not be qualified using fallback gray; percentage color alpha must be parsed and composited.'};
writeFileSync(new URL(`../../../evaluations/arrow-contrast/echarts-unsupported-paint-${phase}-20261003.json`,import.meta.url),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));if(phase==='final'&&!passed)process.exitCode=1;
const preparedReport={phase,passed:preparedGradientRejected,preparedGradientRejected,scope:'The normal prepareColorsetOption path must pass the actual declared backing into arrow qualification rather than its rounded label backing.'};
writeFileSync(new URL(`../../../evaluations/arrow-contrast/echarts-prepared-backing-${phase}-20261003.json`,import.meta.url),JSON.stringify(preparedReport,null,2)+'\n');
if(phase==='final'&&!preparedGradientRejected)process.exitCode=1;
