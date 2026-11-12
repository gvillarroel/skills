import {readFile} from "node:fs/promises";
import {fileURLToPath} from "node:url";
import path from "node:path";
import {McpServer} from "@modelcontextprotocol/sdk/server/mcp.js";
import {StdioServerTransport} from "@modelcontextprotocol/sdk/server/stdio.js";
import {registerAppTool,registerAppResource,RESOURCE_MIME_TYPE} from "@modelcontextprotocol/ext-apps/server";

const directory=path.dirname(fileURLToPath(import.meta.url));
const uri="ui://service-observatory/workspace.html";
const snapshot=JSON.parse(await readFile(path.join(directory,"observatory.json"),"utf8"));
const html=await readFile(path.join(directory,"workspace.html"),"utf8");
let revision=1;
const server=new McpServer({name:"service-observatory",version:"1.0.0"});
const result=()=>({content:[{type:"text",text:`Synthetic service snapshot ${revision}: 12 services, 13 directed relationships. Payments P95 268 ms exceeds the 250 ms objective; Orders 142 ms. Use the linked workspace to inspect dependencies, metrics and exact values. No production systems are connected.`}],structuredContent:{snapshot:{...snapshot,revision}}});
registerAppResource(server,"workspace",uri,{},async()=>({contents:[{uri,mimeType:RESOURCE_MIME_TYPE,text:html,_meta:{ui:{csp:{connectDomains:[],resourceDomains:[]},prefersBorder:false}}}]}));
registerAppTool(server,"open_observatory",{description:"Open a read-only synthetic service graph, metrics, table and linked inspector.",inputSchema:{},annotations:{readOnlyHint:true,destructiveHint:false,openWorldHint:false},_meta:{ui:{resourceUri:uri}}},async()=>result());
registerAppTool(server,"refresh_observatory",{description:"Refresh the synthetic service snapshot without changing production data.",inputSchema:{},annotations:{readOnlyHint:true,destructiveHint:false,openWorldHint:false},_meta:{ui:{resourceUri:uri,visibility:["app"]}}},async()=>{revision++;return result();});
await server.connect(new StdioServerTransport());
