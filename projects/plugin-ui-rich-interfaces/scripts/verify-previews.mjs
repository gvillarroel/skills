// Run: node projects/plugin-ui-rich-interfaces/scripts/verify-previews.mjs
import fs from "node:fs/promises";
import path from "node:path";
import {createRequire} from "node:module";
import {fileURLToPath} from "node:url";
const project=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"..");
let require=createRequire(path.join(project,"package.json"));try{require.resolve("playwright");}catch{require=createRequire(path.resolve(project,"../desktop-plugin-ui/mcp-probe/package.json"));}
const {chromium}=require("playwright"),browser=await chromium.launch({headless:true,channel:"msedge"});
const output=path.join(project,"artifacts/reviews/previews");await fs.mkdir(output,{recursive:true});
const checks=[],errors=[];function check(name,passed,detail){checks.push({name,passed:Boolean(passed),detail});if(!passed)throw new Error(name);}
let failure;
try{
  const page=await browser.newPage({viewport:{width:1440,height:1000},reducedMotion:"reduce"});page.on("pageerror",error=>errors.push(error.message));
  const origin="http://127.0.0.1:8872/";
  await page.goto(origin+"index.html");check("Six host routes are visible",await page.locator(".card").count()===6);
  for(const width of [1440,390]){
    await page.setViewportSize({width,height:1000});check(`Preview index fits ${width}px`,await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));await page.screenshot({path:path.join(output,`index-${width}.png`),fullPage:true});
  }
  await page.setViewportSize({width:1280,height:900});await page.goto(origin+"artifacts/previews/native.html");
  await page.locator("#view").selectOption("metrics");check("Native SVG artifact changes view",(await page.locator("#image").getAttribute("src")).endsWith("payments-metrics.svg"));
  await page.locator("#image").evaluate(async image=>{if(!image.complete)await new Promise(resolve=>image.onload=resolve);});
  check("Native SVG bytes paint",await page.locator("#image").evaluate(image=>image.naturalWidth>0));await page.screenshot({path:path.join(output,"native-metrics.png"),fullPage:true});
  await page.goto(origin+"artifacts/previews/pi.html");await page.locator("#view").selectOption("values");
  check("Pi preview includes all 24 exact values",((await page.locator("#terminal").innerText()).match(/\d\d:00/g)??[]).length===24);await page.screenshot({path:path.join(output,"pi-values.png"),fullPage:true});
  await page.goto(origin+"artifacts/previews/gemini.html");check("Canvas alternative starts collapsed",!await page.locator("iframe").isVisible());await page.locator("#open").click();
  const frame=page.frameLocator("iframe");await frame.locator("g.graph-node").first().waitFor({state:"attached"});
  check("Exact Gemini embed payload paints locally",await frame.locator("#selected-name").innerText()==="Payments");
  check("Unsupported live actions are not simulated",!await frame.locator("#refresh").isVisible()&&!await frame.locator("#export").isVisible());
  await frame.locator("#search").fill("Orders");check("Embedded local inspection works",await frame.locator("g.graph-node").count()===1);await frame.locator("#search").fill("");
  await page.screenshot({path:path.join(output,"gemini-embed.png"),fullPage:true});
  const violation=await frame.locator("body").evaluate(async()=>{
    const observed=new Promise(resolve=>document.addEventListener("securitypolicyviolation",event=>resolve({directive:event.effectiveDirective,uri:event.blockedURI}),{once:true}));
    try{await fetch("https://example.com/network-probe");}catch{}
    return Promise.race([observed,new Promise(resolve=>setTimeout(()=>resolve(null),500))]);
  });
  check("Documented connect-src policy blocks the probe in this fixture",violation?.directive==="connect-src",violation);
  check("No preview JavaScript exceptions",!errors.length,errors);await page.close();
}catch(error){failure=String(error);}finally{
  await browser.close();const report={passed:!failure,checks,errors,failure,scope:"Local authored preview pages and original embedded/SVG payloads; not native host paint."};await fs.writeFile(path.join(output,"review.json"),JSON.stringify(report,null,2));console.log(JSON.stringify(report));if(!report.passed)process.exitCode=1;
}
