import {cuts,frame,mean} from './math.js';
import {json,compressedJSON,trace as loadTrace} from './data.js';
const $=id=>document.getElementById(id),fmt=(x,n=2)=>Number(x).toLocaleString('en-US',{minimumFractionDigits:n,maximumFractionDigits:n});
const state={catalog:null,question:null,phase:'prefill',scope:'token',weighting:'question',token:0,trace:null,matrix:null,domain:'codice',qid:null,hotlists:[],zoom:512,pan:0,threshold:0,layer:0,expert:0,textTab:'prompt',language:'en',timer:null,version:0,loading:false,filterMode:'manual',filterLimit:.1,filterBusy:false};
let geometry=null,traceCache={},matrixCache=new Map(),filterSequence=0,filterTimer=null,worker=null,selectionAbort=null;
function stop(){if(state.timer)clearInterval(state.timer);state.timer=null;$('play').textContent='▶';$('play').setAttribute('aria-label','Play token animation');}
function fail(e){if(e.name==='AbortError')return;$('error').hidden=false;$('error').textContent=e.message||String(e);$('loading').hidden=true;state.loading=false;stop();}
function protect(fn){return (...args)=>Promise.resolve(fn(...args)).catch(fail);}
function option(value,text){const e=document.createElement('option');e.value=value;e.textContent=text;return e;}
function active(id,value){for(const b of $(id).querySelectorAll('button')){b.classList.toggle('active',b.dataset.value===value);b.setAttribute('aria-pressed',b.dataset.value===value);}}
function cancelFilter(){++filterSequence;clearTimeout(filterTimer);state.filterBusy=false;document.body.classList.remove('filter-pending');}
function resetWorker(){worker?.terminate();worker=null;cancelFilter();}
async function start(){
  const [c,h]=await Promise.all([json('data/catalog.json'),json('data/hotlists.json')]);state.catalog=c;state.hotlists=h.profiles;
  $('status').textContent='Verified collection';$('progress').textContent=c.questions.length.toLocaleString('en-US');$('allocation-note').textContent=c.allocation_note;
  const hash=new URLSearchParams(location.hash.slice(1)),id=hash.get('q'),row=c.questions.find(x=>x.id===id);
  if(row){state.domain=row.domain;state.qid=id;}if(hash.get('phase')==='generation')state.phase='generation';
  $('domain').replaceChildren(...c.domains.map(d=>option(d.id,`${d.name} (150)`)));$('domain').value=state.domain;
  await selectDomain(false);
}
async function selectDomain(reset=true){
  stop();state.domain=$('domain').value;$('search').value='';const qs=state.catalog.questions.filter(q=>q.domain===state.domain);
  $('question').replaceChildren(...qs.map(q=>option(q.id,q.title)));$('question-list').replaceChildren();
  for(const q of qs){const b=document.createElement('button');b.className='question-card';b.dataset.id=q.id;
    const title=document.createElement('span');title.textContent=q.title;const detail=document.createElement('small');detail.textContent=`${q.prefill_tokens} input · ${q.generation_tokens} output · ${q.split}`;b.append(title,detail);
    b.onclick=protect(async()=>{$('question').value=q.id;await selectQuestion();});$('question-list').append(b);
  }
  $('question').value=!reset&&qs.some(q=>q.id===state.qid)?state.qid:qs[0].id;await selectQuestion();
}
function showHotlist(){
  const h=state.hotlists.find(h=>h.domain===state.domain&&h.phase===state.phase&&h.weighting===state.weighting);if(!h)return;
  const range=[Math.min(...h.experts_per_layer),Math.max(...h.experts_per_layer)];
  $('hotlist-note').textContent=`${h.train_questions} training questions · ${h.holdout_questions} held-out questions. ${h.experts_per_layer.reduce((a,b)=>a+b,0).toLocaleString('en-US')} layer–expert pairs, ${range[0]}–${range[1]} per layer. Held-out router mass covered: ${fmt(h.holdout_mass*100)}%; original global profile: ${fmt(h.baseline_holdout_mass*100)}%.`;
  $('hotlist-download').href='data/hotlists/'+h.id+'.json';
}
async function selectQuestion(){
  stop();resetWorker();selectionAbort?.abort();selectionAbort=new AbortController();const v=++state.version;state.loading=true;state.qid=$('question').value;
  $('error').hidden=true;$('workspace').hidden=true;$('loading').hidden=false;$('loading').textContent='Loading question and original trace…';
  const q=await json('data/questions/'+state.qid+'.json',selectionAbort.signal);if(v!==state.version)return;
  state.question=q;state.token=0;traceCache={};for(const b of $('question-list').children)b.classList.toggle('active',b.dataset.id===q.id);
  $('title').textContent=q.title;$('breadcrumb').textContent=state.catalog.domains.find(d=>d.id===q.domain).name;
  $('question-meta').textContent=`${q.id} · ${q.split} · collection #${q.collection_index} · ${q.input_ids.length} input tokens`;
  $('gen-speed').textContent=fmt(q.metrics.generation_tps);$('pre-speed').textContent=fmt(q.metrics.prefill_tps);$('response-time').textContent=fmt(q.metrics.response_seconds)+' s';$('ttft').textContent=fmt(q.metrics.ttft_seconds);
  $('output-count').textContent=q.output_ids.length+' tokens · '+(q.finish==='length'?'generation cap reached':'response ended');
  $('audit-note').textContent=`Verified original trace: ${q.audit.rows.toLocaleString('en-US')} complete token/layer rows; maximum row-sum error ${q.audit.row_sum_max_error.toExponential(2)}. Rejected draft inputs excluded: ${q.audit.rejected_draft_inputs}. Final diagnostic pass: ${fmt(q.terminal_capture_seconds,3)} s, excluded from generation time.`;
  renderText();await loadPhase(v);
}
async function loadPhase(v=++state.version){
  stop();resetWorker();state.loading=true;$('loading').hidden=false;$('loading').textContent='Loading and verifying the selected trace…';const phase=state.phase,q=state.question;
  if(!traceCache[phase]){const t=await loadTrace(q.id,phase,q.trace_manifest[phase],selectionAbort?.signal);if(v!==state.version)return;traceCache[phase]=t;}
  state.trace=traceCache[phase];state.token=Math.min(state.token,state.trace.count-1);state.loading=false;$('loading').hidden=true;$('workspace').hidden=false;
  $('seek').max=state.trace.count-1;$('token-number').max=state.trace.count-1+1;$('token-total').textContent='/ '+state.trace.count;
  history.replaceState(null,'','#'+new URLSearchParams({q:q.id,phase}));await updateMatrix(v);renderText();
}
async function updateMatrix(v=state.version){
  if(!state.trace)return;cancelFilter();showHotlist();active('phase',state.phase);active('scope',state.scope);$('playback').hidden=state.scope!=='token';$('weighting').disabled=state.scope!=='domain';
  $('formula').textContent=state.scope==='domain'?(state.weighting==='question'?'Mean of question means: every question contributes equally.':'Mean of all tokens: longer questions contribute more.'):(state.scope==='token'?'Effective weights for the selected original token.':'Every token in this question’s selected phase has equal weight.');
  if(state.scope==='token')state.matrix=frame(state.trace,state.token);else if(state.scope==='question')state.matrix=mean(state.trace);else{
    const key=`${state.domain}-${state.phase}-${state.weighting}`;
    if(!matrixCache.has(key))matrixCache.set(key,await compressedJSON(`data/matrices/${key}.json.gz`));if(v!==state.version)return;
    state.aggregate=matrixCache.get(key);state.matrix=new Float64Array(state.aggregate.matrix);
  }
  updateToken();draw();inspect();scheduleFilter();
}
function tokenText(){return state.phase==='prefill'?state.question.input_tokens:state.question.output_token_text;}
function updateToken(){
  $('seek').value=state.token;$('token-number').value=state.token+1;
  if(state.scope==='token'){
    const token=tokenText()[state.token],id=(state.phase==='prefill'?state.question.input_ids:state.question.output_ids)[state.token];
    $('token-label').textContent='PROCESSED TOKEN';$('token-text').textContent=token.replaceAll(' ','␠').replaceAll('\n','↵\n')||'∅';let meta=`ID ${id} · position ${state.token+1} / ${state.trace.count}`;
    if(state.phase==='generation'){const ts=state.question.token_seconds,dt=state.token?ts[state.token]-ts[state.token-1]:ts[0];meta+=` · arrival ${fmt(ts[state.token],3)} s · Δ ${fmt(dt*1000,1)} ms`;if(state.question.audit.terminal_diagnostic_positions.includes(state.question.input_ids.length+state.token))meta+=' · final diagnostic capture';}
    $('token-meta').textContent=meta;
  }else{$('token-label').textContent=state.scope==='question'?'QUESTION MEAN':'DOMAIN MEAN';$('token-text').textContent=state.phase==='prefill'?'Prefill':'Generation';$('token-meta').textContent=state.scope==='domain'?`${state.aggregate.questions} questions · ${state.aggregate.tokens.toLocaleString('en-US')} tokens · equal weight per ${state.weighting}`:`${state.trace.count} equally weighted tokens`;}
  for(const b of $('text-content').querySelectorAll('.text-token.current'))b.classList.remove('current');$('text-content').querySelector(`[data-token="${state.token}"]`)?.classList.add('current');
}
function renderText(){
  if(!state.question)return;active('text-tab',state.textTab);$('text-content').replaceChildren();$('language-control').hidden=state.textTab==='tokens';
  if(state.textTab==='tokens'){
    $('translation-note').textContent='Original token stream used for these traces. Click a token to inspect it.';
    tokenText().forEach((text,i)=>{const b=document.createElement('button');b.className='text-token'+(i===state.token?' current':'');b.dataset.token=i;b.textContent=text||'∅';b.title=`Token ${i+1}`;b.onclick=()=>{stop();setToken(i);};$('text-content').append(b);});return;
  }
  const q=state.question,english=state.language==='en',prompt=state.textTab==='prompt';
  $('text-content').textContent=english?(prompt?q.prompt_en:q.answer_en):(prompt?q.prompt:q.text);
  if(english&&!prompt&&q.answer_literal_glossary?.length){
    const glossary=document.createElement('details');glossary.className='literal-glossary';
    const label=document.createElement('summary');label.textContent='English glossary for preserved code and data';glossary.append(label);
    const list=document.createElement('dl');
    q.answer_literal_glossary.forEach(row=>{const source=document.createElement('dt'),translation=document.createElement('dd');source.textContent=row.original;translation.textContent=row.english;list.append(source,translation);});
    glossary.append(list);$('text-content').append(glossary);
  }
  $('translation-note').textContent=english?(prompt?'English reading translation. The routing experiment used the original Italian prompt.':'English reading translation; errors are possible. Fenced code and mathematical notation remain original, with a glossary for comments and data labels. Numeric values are checked against the source.'):'Original recorded text. Routing and timing measurements correspond to this version.';
  if(!prompt&&q.finish==='length')$('translation-note').textContent+=' This answer reached the original 384-token cap.';
}
function setToken(n){if(!state.trace||state.loading||(state.timer&&state.filterBusy))return;state.token=Math.max(0,Math.min(state.trace.count-1,Number(n)||0));state.scope='token';updateMatrix().catch(fail);}
function play(){if(state.timer){stop();return;}if(!state.trace||state.loading)return;if(state.token===state.trace.count-1)setToken(0);$('play').textContent='Ⅱ';$('play').setAttribute('aria-label','Pause token animation');state.timer=setInterval(()=>{if(state.token>=state.trace.count-1)stop();else setToken(state.token+1);},1000/Number($('fps').value));}
function threshold(v){state.threshold=Math.max(0,Math.min(100,Number(v)||0))/100;$('threshold').value=state.threshold*100;$('threshold-slider').value=state.threshold*100;draw();inspect();scheduleFilter();}
function scheduleFilter(){
  if(!state.matrix||!state.trace)return;clearTimeout(filterTimer);const sequence=++filterSequence;state.filterBusy=true;document.body.classList.add('filter-pending');
  $('max-question').textContent='—';$('max-token').textContent='—';$('max-question-detail').textContent='Checking every layer…';$('max-token-detail').textContent='Checking original tokens…';$('filter-status').textContent='Verifying the display mask against recorded traces…';
  const auto=state.filterMode!=='manual';$('threshold').disabled=auto;$('threshold-slider').disabled=auto;$('filter-budget-label').hidden=!auto;
  if(auto){state.threshold=0;$('threshold').value=0;$('threshold-slider').value=0;draw();inspect();}
  filterTimer=setTimeout(()=>{
    if(!worker){worker=new Worker('filter-worker.js',{type:'module'});worker.onmessage=({data:m})=>{if(m.sequence!==filterSequence)return;if(m.error){$('filter-status').textContent='Filter verification failed: '+m.error;stop();}else{const r=m.result;state.threshold=r.threshold;$('threshold').value=Number((r.threshold*100).toPrecision(12));$('threshold').title=`Exact threshold: ${r.threshold*100}%`;$('threshold-slider').value=r.threshold*100;
      for(const [id,x] of [['question',r.maximum_question],['token',r.maximum_token]]){$('max-'+id).textContent=fmt(x.fraction*100)+'%';$('max-'+id+'-detail').textContent=x.question?`${x.question} · layer ${x.layer}${x.token===null?'':` · token ${x.token}`}`:'No weight excluded';}
      $('filter-status').textContent=`Verified across ${r.questions} question${r.questions===1?'':'s'} and ${r.tokens.toLocaleString('en-US')} ${state.phase} tokens. `+(r.mode==='manual'?'One mask applied to every original trace in scope.':`The ${fmt(r.limit*100)}% cap holds in every layer of ${r.mode==='question'?'each question mean':'every token'}.`);draw();inspect();}
      state.filterBusy=false;document.body.classList.remove('filter-pending');};worker.onerror=e=>{$('filter-status').textContent='Filter worker error: '+e.message;state.filterBusy=false;document.body.classList.remove('filter-pending');stop();};}
    const key=`${state.scope}-${state.qid}-${state.domain}-${state.phase}-${state.weighting}-${state.scope==='token'?state.token:0}`;
    worker.postMessage({sequence,key,qid:state.qid,matrix:state.matrix,trace:state.scope==='domain'?null:state.trace,domainPath:state.scope==='domain'?`data/curves/${state.domain}-${state.phase}-${state.weighting}.json.gz`:null,threshold:state.threshold,mode:state.filterMode,limit:state.filterLimit});
  },80);
}

const colors=[[24,37,60],[34,104,134],[86,189,200],[240,212,123],[251,121,59]];
function color(v,max){const t=Math.max(0,Math.min(1,v/max))*4,i=Math.min(3,Math.floor(t)),f=t-i;
  return `rgb(${colors[i].map((x,j)=>Math.round(x*(1-f)+colors[i+1][j]*f)).join(',')})`}
function draw(){
  if(!state.matrix)return;const c=$('matrix'),r=c.getBoundingClientRect(),dpr=devicePixelRatio||1;
  c.width=Math.round(r.width*dpr);c.height=Math.round(r.height*dpr);const ctx=c.getContext('2d');ctx.scale(dpr,dpr);
  const left=35,top=23,right=5,bottom=2,w=r.width-left-right,h=r.height-top-bottom,cw=w/state.zoom,rh=h/48;
  geometry={left,top,w,h,cw,rh};ctx.fillStyle='#0d1521';ctx.fillRect(left,top,w,h);
  let max=0;for(const v of state.matrix)if(v>max)max=v;max=$('scale').value==='fixed'?1:Math.max(max,1e-8);
  $('scale-max').textContent=fmt(max*100,max<.01?3:1)+'%';
  for(let l=0;l<48;l++){
    for(let j=0;j<state.zoom;j++){
      const e=state.pan+j,v=state.matrix[l*512+e];if(v<=0||v<state.threshold)continue;
      ctx.fillStyle=color(v,max);ctx.fillRect(left+j*cw,top+l*rh,Math.max(cw-.2,.8),Math.max(rh-1,1));
      if(state.zoom<=32&&$('values').checked&&cw>=17){ctx.fillStyle=v/max>.55?'#102030':'#ecf6ff';ctx.font=(cw<22?'7':'9')+'px Consolas, monospace';ctx.textAlign='center';ctx.fillText((v*100).toFixed(v<.01?2:1),left+(j+.5)*cw,top+(l+.7)*rh);}
    }
    ctx.fillStyle='#899db6';ctx.font='10px Segoe UI';ctx.textAlign='right';ctx.fillText(l,left-8,top+(l+.73)*rh);
  }
  const step=state.zoom===512?32:state.zoom===64?4:2;ctx.textAlign='center';
  for(let j=0;j<state.zoom;j+=step){ctx.fillStyle='#899db6';ctx.fillText(state.pan+j,left+(j+.5)*cw,14);}
  if(state.expert>=state.pan&&state.expert<state.pan+state.zoom){ctx.strokeStyle='#fff';ctx.lineWidth=1;ctx.strokeRect(left+(state.expert-state.pan)*cw,top+state.layer*rh,cw,rh);}
  const cut=cuts(state.matrix,state.threshold);$('cut').textContent=fmt(cut.fraction*100)+'%';$('retained').textContent=fmt((1-cut.fraction)*100)+'% retained';
  $('cells-cut').textContent=`${cut.hidden.toLocaleString('en-US')} / ${cut.active.toLocaleString('en-US')}`;
  const worst=Math.max(...cut.layers),layer=cut.layers.indexOf(worst);$('worst-layer').textContent=worst?`Layer ${layer}: ${fmt(worst*100)}% hidden`:'No weight excluded';
  $('matrix-caption').textContent=state.zoom<=32?'Cell values are percentages. Hover for full precision. Weights are not renormalized by filtering.':'Effective normalized weights per layer. Hover for values or zoom to 16 experts.';
}
function cell(event){if(!geometry)return null;const r=$('matrix').getBoundingClientRect(),g=geometry;
  const e=Math.floor((event.clientX-r.left-g.left)/g.cw)+state.pan,l=Math.floor((event.clientY-r.top-g.top)/g.rh);
  return l>=0&&l<48&&e>=state.pan&&e<state.pan+state.zoom?{l,e}:null}
function inspect(){if(!state.matrix)return;const l=state.layer,e=state.expert,v=state.matrix[l*512+e];
  $('inspect-layer').value=l;$('inspect-expert').value=e;
  $('cell-title').textContent=`Layer ${l} · expert ${e}`;
  $('cell-detail').textContent=`Weight ${fmt(v*100,6)}% (${v.toPrecision(8)}). ${v>0&&v<state.threshold?'Hidden by the threshold.':v?'Visible on the map.':'Zero weight in this selection.'}`;
  const pairs=Array.from({length:512},(_,e)=>({e,v:state.matrix[l*512+e]})).filter(x=>x.v>0).sort((a,b)=>b.v-a.v).slice(0,10);
  $('top-experts').replaceChildren();for(const x of pairs){const row=document.createElement('div');row.className='expert-row'+(x.v<state.threshold?' masked':'');
    const a=document.createElement('span');a.textContent='Expert '+x.e;const bar=document.createElement('i');bar.style.width=100*x.v/pairs[0].v+'%';const b=document.createElement('span');b.textContent=fmt(x.v*100,2)+'%';row.append(a,bar,b);$('top-experts').append(row)}
}
// Controls operate on recorded data only.
$('domain').onchange=protect(()=>selectDomain());$('question').onchange=protect(selectQuestion);
$('search').oninput=()=>{const term=$('search').value.toLowerCase();for(const b of $('question-list').children)b.hidden=!(`${b.textContent} ${b.dataset.id}`.toLowerCase().includes(term));};
$('phase').onclick=protect(async e=>{if(!e.target.dataset.value||state.loading)return;state.phase=e.target.dataset.value;state.token=0;await loadPhase();});
$('scope').onclick=protect(async e=>{if(!e.target.dataset.value||state.loading)return;stop();state.scope=e.target.dataset.value;await updateMatrix(++state.version);});
$('weighting').onchange=protect(async()=>{stop();state.weighting=$('weighting').value;await updateMatrix(++state.version);});
$('seek').oninput=()=>{stop();setToken($('seek').value);};$('token-number').onchange=()=>{stop();setToken(Number($('token-number').value)-1);};
$('first').onclick=()=>{stop();setToken(0);};$('last').onclick=()=>{stop();setToken(state.trace.count-1);};$('prev').onclick=()=>{stop();setToken(state.token-1);};$('next').onclick=()=>{stop();setToken(state.token+1);};$('play').onclick=play;
$('fps').onchange=()=>{if(state.timer){stop();play();}};
$('zoom').onchange=()=>{state.zoom=Number($('zoom').value);state.pan=Math.min(state.pan,512-state.zoom);$('pan').max=512-state.zoom;$('pan').value=state.pan;$('pan-label').hidden=state.zoom===512;$('pan-value').textContent=state.pan;draw();};
$('pan').oninput=()=>{state.pan=Number($('pan').value);$('pan-value').textContent=state.pan;draw();};$('values').onchange=draw;$('scale').onchange=draw;
$('threshold').oninput=()=>threshold($('threshold').value);$('threshold-slider').oninput=()=>threshold($('threshold-slider').value);$('reset-threshold').onclick=()=>{state.filterMode='manual';$('filter-mode').value='manual';threshold(0);};
$('filter-mode').onchange=()=>{stop();state.filterMode=$('filter-mode').value;scheduleFilter();};$('filter-budget').oninput=()=>{stop();state.filterLimit=Math.max(0,Math.min(100,Number($('filter-budget').value)||0))/100;scheduleFilter();};$('filter-budget').onblur=()=>{$('filter-budget').value=state.filterLimit*100;};
$('matrix').onmousemove=e=>{const x=cell(e);if(!x||!state.matrix){$('tooltip').hidden=true;return;}const v=state.matrix[x.l*512+x.e],r=$('matrix').getBoundingClientRect();$('tooltip').hidden=false;$('tooltip').textContent=`Layer ${x.l} · Expert ${x.e}\nWeight ${fmt(v*100,6)}%${v>0&&v<state.threshold?'\nHidden by threshold':''}`;$('tooltip').style.left=Math.max(0,Math.min(e.clientX-r.left+12,r.width-205))+'px';$('tooltip').style.top=Math.max(0,e.clientY-r.top-64)+'px';};
$('matrix').onmouseleave=()=>{$('tooltip').hidden=true;};$('matrix').onclick=e=>{const x=cell(e);if(x){state.layer=x.l;state.expert=x.e;inspect();draw();}};
for(const id of ['inspect-layer','inspect-expert'])$(id).oninput=()=>{state.layer=Math.max(0,Math.min(47,Number($('inspect-layer').value)||0));state.expert=Math.max(0,Math.min(511,Number($('inspect-expert').value)||0));inspect();draw();};
$('text-tab').onclick=e=>{if(e.target.dataset.value){state.textTab=e.target.dataset.value;renderText();}};$('language').onchange=()=>{state.language=$('language').value;renderText();};
$('export').onclick=()=>{if(!state.matrix)return;const lines=['layer,expert,weight'];for(let l=0;l<48;l++)for(let e=0;e<512;e++)lines.push(`${l},${e},${state.matrix[l*512+e]}`);const url=URL.createObjectURL(new Blob([lines.join('\n')+'\n'],{type:'text/csv;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download=`fnmr-${state.scope==='domain'?state.domain:state.qid}-${state.phase}-${state.scope}${state.scope==='token'?'-'+(state.token+1):state.scope==='domain'?'-'+state.weighting:''}.csv`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
document.addEventListener('keydown',e=>{if(['INPUT','SELECT','TEXTAREA','BUTTON'].includes(document.activeElement.tagName))return;if(e.key==='ArrowRight'){e.preventDefault();stop();setToken(state.token+1);}if(e.key==='ArrowLeft'){e.preventDefault();stop();setToken(state.token-1);}});
new ResizeObserver(draw).observe($('matrix'));window.addEventListener('pagehide',()=>{stop();resetWorker();selectionAbort?.abort();});
start().catch(fail);
