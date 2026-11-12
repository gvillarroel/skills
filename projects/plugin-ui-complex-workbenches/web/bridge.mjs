import {App} from '@modelcontextprotocol/ext-apps';
const app=new App({name:'Incident Analysis',version:'1.0.0'},{},{strict:true});
const ui=window.Workbench;
for(const id of ['plan-form','compete','inspect-state'])document.getElementById(id).hidden=true;
async function tool(name,args={}){const result=await app.callServerTool({name,arguments:args});if(result.isError||!result.structuredContent)throw Error('Sandbox tool unavailable');return result.structuredContent;}
app.connect().then(async()=>{if(!app.getHostCapabilities()?.serverTools){ui.setConnection('Snapshot · server actions unavailable');document.body.dataset.bridge='unavailable';return;}await ui.setBackend({state:()=>tool('sandbox_state'),compete:()=>tool('simulate_competing_edit'),apply:draft=>tool('apply_simulated_plan',draft)});for(const id of ['plan-form','compete','inspect-state'])document.getElementById(id).hidden=false;ui.setConnection('MCP App · synthetic server');document.body.dataset.bridge='ready';}).catch(()=>{ui.setConnection('Host connection unavailable');document.body.dataset.bridge='failed';});
