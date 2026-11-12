import {joinSession} from '@github/copilot-sdk/extension';
import fs from 'node:fs';
import path from 'node:path';

const output=path.join(process.env.COPILOT_HOME,'ui-extension-result.json');
const result={timestampUtc:new Date().toISOString(),layer:'real-copilot-cli-tui-extension',modelPrompts:0,rows:[]};
function save(){fs.writeFileSync(output,JSON.stringify(result,null,2));}
try {
  const session=await joinSession();
  result.capabilities=session.capabilities;
  result.rows.push({name:'join-extension-session',status:'observed-working'});
  save();
  if(session.capabilities.ui?.elicitation){
    result.rows.push({name:'native-cli-confirm',status:'pending'});save();
    const accepted=await session.ui.confirm('UI evidence probe: accept this synthetic confirmation?');
    result.rows[result.rows.length-1]={name:'native-cli-confirm',status:'observed-working',accepted};
    save();
    const selected=await session.ui.select('UI evidence probe: select Beta',['Alpha','Beta']);
    result.rows.push({name:'native-cli-select',status:selected==='Beta'?'observed-working':'observed-failed',selected});save();
    const input=await session.ui.input('UI evidence probe: type synthetic',{maxLength:12});
    result.rows.push({name:'native-cli-input',status:input==='synthetic'?'observed-working':'observed-failed',input});save();
    const cancelled=await session.ui.input('UI evidence probe: cancel this input with Escape');
    result.rows.push({name:'native-cli-cancel',status:cancelled===null?'observed-working':'observed-failed',returned:cancelled});save();
    session.log('UI_EVIDENCE_PROBE_COMPLETE: confirmation, selection, input and cancel finished',{level:'info'});
  } else {
    result.rows.push({name:'native-cli-confirm',status:'capability-absent'});save();
    session.log('UI_EVIDENCE_PROBE_COMPLETE: elicitation capability absent',{level:'info'});
  }
}catch(error){result.rows.push({name:'extension-probe',status:'observed-failed',error:String(error)});save();}
