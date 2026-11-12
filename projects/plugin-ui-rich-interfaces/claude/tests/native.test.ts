// Run: claude plugin test projects/plugin-ui-rich-interfaces/claude
import {expect,test} from "claude-code/testing";
const PANE={plugin:"service-observatory",component:"Pane",requestId:"service-observatory",viewport:{columns:100,rows:30},props:{title:"Service Observatory",isFocused:true,bodyColumns:80,placement:"inline",scroll:{offset:0,bodyRows:20},view:{}}}as const;
test("direct details retain exact values without pane or inference",async($,on)=>{
  let opens=0;on("ui.open",()=>{opens++;return {value:{isPlaced:true}};});
  const answer=await $.command.run({command:"service-observatory",args:"payments"});
  expect(answer.text).toContain("P95 268 ms");expect(answer.text).toContain("Called by Orders: 920 req/s");expect(opens).toBe(0);
});
test("invalid input recovers and unrelated commands pass through",async($,on)=>{
  on("command.run",()=>({text:"HOST"}));
  expect((await $.command.run({command:"service-observatory",args:"invalid"})).text).toContain("/service-observatory all");
  expect((await $.command.run({command:"other",args:""})).text).toBe("HOST");
});
test("pane denial provides exact selected snapshot",async($,on)=>{
  on("ui.open",()=>({deny:"No placement"}));
  const answer=await $.command.run({command:"service-observatory",args:""});
  expect(answer.text).toContain("268 ms");expect(answer.text).toContain("pane is unavailable");
});
for(const surface of ["desktop","vscode","terminal"])for(const columns of [32,80])test(`${surface} ${columns}: select, metric, options and close`,async($,on)=>{
  let closes=0;on("ui.open",()=>({value:{isPlaced:true}}));on("ui.close",()=>{closes++;return {value:undefined};});
  await $.command.run({command:"service-observatory",args:""});
  const ui=await $.ui.mount({...PANE,surface,viewport:{columns,rows:30},props:{...PANE.props,bodyColumns:columns}});
  expect(await ui.find({type:"Text",text:"Payments · degraded · Commerce on-call\nP95 268 ms · Error 0.84% · 920 req/s\nCalled by Orders: 920 req/s\nCalls Primary DB: 920 req/s"})).toBeDefined();
  await ui.select({key:"service",value:"orders"});
  await ui.select({key:"view",value:"metrics"});
  expect(await ui.find({type:"Text",text:/Orders · P95 142 ms/})).toBeDefined();
  await ui.press({key:"options"});
  expect(await ui.find({type:"Text",text:/Native SVG is an image preview/})).toBeDefined();
  await ui.select({key:"view",value:"records"});
  expect(await ui.find({type:"Text",text:/Gateway: healthy; P95 74 ms/})).toBeDefined();
  await ui.press({key:"close"});expect(closes).toBe(1);await ui.unmount();
});
test("other native pane keeps the host renderer",async($,on)=>{
  on("ui.render",()=>({type:"Text",props:{},children:["HOST"]}));
  const ui=await $.ui.mount({...PANE,requestId:"other",surface:"desktop"});expect(await ui.find({type:"Text",text:"HOST"})).toBeDefined();await ui.unmount();
});
