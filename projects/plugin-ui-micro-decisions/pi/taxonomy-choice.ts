// Run: pi --offline --no-session -e ./taxonomy-choice.ts
import type {ExtensionAPI} from '@earendil-works/pi-coding-agent';
const options=[{id:'knowledge-modeling',label:'Knowledge modeling',sibling:'Concept definition'},{id:'data-integration',label:'Data integration',sibling:'Schema mapping'}];
export default function(pi:ExtensionAPI){
 pi.registerMessageRenderer('taxonomy-choice',(message,options,theme)=>({render:width=>{const words=String(message.content).split(' '),lines:string[]=[];let line='';for(const word of words){if((line+' '+word).length>width-4&&line){lines.push(line);line='';}line+=(line?' ':'')+word;}if(line)lines.push(line);return lines.map(s=>theme.fg((message.details as any)?.outcome==='selected'?'success':'muted',theme.bold(s)));},invalidate(){}}));
 pi.registerCommand('taxonomy-choice',{description:'Resolve one primary-parent ambiguity. [knowledge-modeling|data-integration|defer]',handler:async(args,ctx)=>{
  let answer:string|undefined;
  if(args.trim()){if(!['knowledge-modeling','data-integration','defer'].includes(args.trim())){if(ctx.hasUI)ctx.ui.notify('Use knowledge-modeling, data-integration or defer.','warning');return;}answer=args.trim();}
  else if(ctx.mode==='tui'){
   const {Key,matchesKey,truncateToWidth}=await import('@earendil-works/pi-tui');let cursor=0,evidence=false;
   answer=await ctx.ui.custom<string|undefined>((tui,theme,keys,done)=>({
    render:width=>{const line=theme.fg('border','─'.repeat(Math.min(54,width-4))),rows=[theme.bold('Where does Ontology alignment belong?'),theme.fg('muted','Choose one primary parent.'),line];
      if(evidence){rows.push(theme.bold('A  Knowledge modeling'),theme.fg('muted','   Relates equivalent, broader and narrower concepts.'),theme.bold('B  Data integration'),theme.fg('muted','   Connects independently described datasets.'),line,theme.fg('muted','E / Esc: return to the same choice'));}
      else{options.forEach((o,i)=>{rows.push(theme.fg(i===cursor?'accent':'text',`${i===cursor?'●':'○'} ${String.fromCharCode(65+i)}  ${theme.bold(o.label)}`),theme.fg('dim',`     ├─ ${o.sibling}`),`     ${theme.fg('dim','└─ ')}${theme.fg('warning','Ontology alignment')}`);});rows.push(line,theme.fg('muted','↑/↓ choose · E evidence · Enter use · Esc defer'));}return rows.map(s=>truncateToWidth('  '+s,width));},invalidate(){},handleInput(input){if(matchesKey(input,'e')){evidence=!evidence;tui.requestRender();return;}if(matchesKey(input,Key.escape)){if(evidence){evidence=false;tui.requestRender();}else done(undefined);return;}if(evidence)return;if(matchesKey(input,Key.enter)){done(options[cursor].id);return;}if(matchesKey(input,Key.up)||matchesKey(input,Key.down)||matchesKey(input,Key.left)||matchesKey(input,Key.right)){cursor=1-cursor;tui.requestRender();}}
   }));
  }else if(ctx.hasUI){const value=await ctx.ui.select('Where should Ontology alignment belong?',['Knowledge modeling — beside Concept definition','Data integration — beside Schema mapping','Defer to the agent']);answer=value?.startsWith('Knowledge')?'knowledge-modeling':value?.startsWith('Data')?'data-integration':undefined;}
  else {pi.sendMessage({customType:'taxonomy-choice',content:'Choose one primary parent for Ontology alignment: knowledge-modeling or data-integration. Use /taxonomy-choice <option>, or defer.',display:true},{triggerTurn:false});return;}
  const chosen=options.find(o=>o.id===answer);const content=chosen?`✓ Placement chosen: Ontology alignment → ${chosen.label}`:'Decision deferred; no placement chosen.';
  pi.sendMessage({customType:'taxonomy-choice',content,details:{decisionId:'ontology-alignment-parent',optionId:chosen?.id??null,outcome:chosen?'selected':'deferred'},display:true},{triggerTurn:false});
 }});
}
