/* Pure parser for fresh CUA AX text. No UI actions, file access or cached indices. */
(function(root){
  function summarize(ax){
    const lines=String(ax).split('\n');
    const doc=lines.find(l=>/\d+ document .*Value: /.test(l));
    const url=doc?.match(/Value: (\S+)/)?.[1];
    if(!url||!/^https:\/\/docs\.google\.com\/videos\//.test(url))return {recognized:false,reason:'The active document is not a verified Google Vids page.'};
    const controls={};
    const wanted=/^(New scene|Go to beginning|Zoom to fit timeline|Edit script|Insert voiceover|Update voiceover|Update all voiceovers|Generate all voiceovers|Change the voice|Upload\b|Replace video|MP4 video \(\.mp4\)|Export to Drive$|Download$|Export status:|File$|Insert$|Close$)/;
    for(const l of lines){
      const m=l.match(/^\s*(\d+) (?:button|menu item) (.*)/);if(!m)continue;
      const label=m[2].replace(/\((?:botón de activación|toggle button)\)\s*/g,'').split(' ID:')[0].trim();
      if(!m[2].includes('(disabled)')&&wanted.test(label))controls[label]=+m[1];
    }
    const sceneLines=lines.filter(l=>/^\s*\d+ text Scene \d+ of \d+, duration /.test(l));
    const scripts=lines.findIndex(l=>/group \(formulario\) Scripts|group \(form\) Scripts/.test(l));
    let script='';
    if(scripts>=0){const end=lines.findIndex((l,i)=>i>scripts&&/text \(heading\) Voiceover/.test(l));script=lines.slice(scripts+1,end<0?scripts+200:end).map(l=>l.match(/^\s*\d+ text (.*)/)?.[1]||'').filter(Boolean).join(' ')}
    const timers=lines.filter(l=>/^\s*\d+ text \d{2}:\d{2}\.\d/.test(l)).map(l=>l.trim().replace(/^\d+ text /,''));
    const media=[...new Set(lines.flatMap(l=>[...l.matchAll(/(?:Description: |Alt text title:\s*)([^\r\n]*?\.(?:mp4|webm|mov))(?=\s|$)/gi)].map(m=>m[1].trim())))];
    const scenes=lines.map(l=>l.match(/^\s*(\d+) button Scene (\d+) of (\d+)\b/)).filter(Boolean).map(m=>({index:+m[1],order:+m[2],total:+m[3]}));
    const tabs=Object.fromEntries(lines.map(l=>l.match(/^\s*(\d+) tab item .*?(Current scene|All scenes)\b/)).filter(Boolean).map(m=>[m[2],+m[1]]));
    const scene=sceneLines.at(-1)?.trim().replace(/^\d+ text /,'')||null;
    const selected=scene?.includes('Selected')?scene.match(/^Scene (\d+) of (\d+),/):null;
    const selectedMedia=scene?.match(/Alt text title:\s*([^\r\n]*?\.(?:mp4|webm|mov))(?=\s|$)/i)?.[1]?.trim()||null;
    return {recognized:true,url,saved:lines.some(l=>/Document status: Saved to Drive/.test(l)),scene,selectedOrder:selected?+selected[1]:null,selectedMedia,scenes,tabs,timers,media,script,controls};
  }
  // Return one recommendation. The caller executes it with the documented CUA API.
  // Every invocation needs a new full observation; no indices survive an action.
  function uploadNext(input){
    const action=(kind,detail={})=>({kind,...detail});
    if(input.policyStopped)return action('stop',{reason:'Follow the host handoff; do not retry through another transport.'});
    if(input.fullState!==true)return action('read-full-state',{reason:'Diff-only text can omit unchanged controls. Obtain a fresh full AX state.'});
    const state=summarize(input.ax);
    const project=url=>String(url||'').match(/^https:\/\/docs\.google\.com\/videos\/d\/([\w-]+)(?:\/|$)/)?.[1];
    const expected=project(input.target?.projectUrl);
    if(!state.recognized||!expected||project(state.url)!==expected)return action('verify-project',{reason:'Observe the intended Vids project before any upload action.'});
    const phase=input.phase||'select';
    const name=String(input.target?.file||'').split(/[\\/]/).at(-1);
    const order=input.target?.sceneOrder;
    if(!name||!Number.isInteger(order)||order<1)return action('verify-target',{reason:'Supply the exact file and positive scene ordinal from the current queue.'});
    if(phase==='await-dialog'&&input.nativeOpenDialogObserved===true)return action('fill-native-filename',{file:input.target.file,keys:['Alt_L+n','paste exact path','Return'],then:'Observe insertion before any retry. Owned-dialog AX indices may be unavailable.'});
    if(phase==='await-dialog'||phase==='await-insertion'){
      if(state.selectedOrder===order&&state.selectedMedia===name)return action('verify-inserted-scene',{sceneOrder:order,file:name,checks:['Correct replacement pixels','One video object and retained narration','Measured duration, normal speed and current scene count']});
      if(input.foreground===false)return action('foreground-tab',{then:'Observe the intended tab and any native Open dialog; do not click Upload again.'});
      return action('observe-upload-result',{reason:'The dialog or inserted media can appear one observation late. Inspect fresh state/screenshot before retrying.'});
    }
    if(input.foreground!==true)return action('foreground-tab',{then:'Verify the visible intended project and selected scene before opening Upload.'});
    if(state.selectedOrder!==order){
      const target=state.scenes.find(s=>s.order===order);
      return target?action('select-scene',{index:target.index,sceneOrder:order,then:'Read fresh full state and verify selection.'}):action('read-full-state',{reason:'Target scene is absent; inspect the current timeline count.'});
    }
    return action('open-upload',{controls:state.controls,then:'Use the observed Insert > Upload or Replace video > Upload path; reobserve before selecting a file.'});
  }
  root.LineWorldVidsUI={summarize,uploadNext};
  if(typeof module!=='undefined')module.exports=root.LineWorldVidsUI;
})(globalThis);
