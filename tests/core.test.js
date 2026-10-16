import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import {frame,mean,cuts} from '../docs/math.js';
import {nextUp,buildCurves,result} from '../docs/filter.js';
globalThis.location={hostname:'localhost'};
const {decodeTrace}=await import('../docs/data.js');
const root=new URL('../',import.meta.url),read=p=>readFileSync(new URL(p,root));
const refs=JSON.parse(read('tests/reference.json'));
const close=(a,b,tol=2e-13)=>assert.ok(Math.abs(a-b)<=tol,`${a} differs from ${b}`);
test('strict thresholds retain ties and correctly advance doubles',()=>{assert.equal(nextUp(0),Number.MIN_VALUE);assert.ok(nextUp(.1)>.1);assert.equal(nextUp(1),1+Number.EPSILON);const m=new Float64Array(48*512);m[0]=.1;m[1]=.1;m[2]=.8;assert.equal(cuts(m,.1).hidden,0);assert.equal(cuts(m,nextUp(.1)).hidden,2);});
test('domain filter curves preserve bounds, monotonicity and complete scope',()=>{const c=JSON.parse(read('docs/data/catalog.json'));for(const d of c.domains)for(const phase of ['prefill','generation'])for(const weighting of ['question','token']){const curve=JSON.parse(gunzipSync(read(`docs/data/curves/${d.id}-${phase}-${weighting}.json.gz`)));assert.equal(curve.question_ids.length,150);for(const mode of ['question','token']){let last=0;for(const loss of curve[mode].loss){assert.ok(loss>=last&&loss<=1);last=loss;}for(const limit of [0,.1,1])assert.ok(result(curve,0,mode,limit)['maximum_'+mode].fraction<=limit);}}});
for(const ref of refs)test(`${ref.phase} ${ref.scope}: lossless trace, means and Python filter agreement`,()=>{
  const compressed=read(`data/traces/${ref.id}/${ref.phase}.fnr.gz`),packed=gunzipSync(compressed),buffer=packed.buffer.slice(packed.byteOffset,packed.byteOffset+packed.byteLength),trace=decodeTrace(buffer);
  const q=JSON.parse(read(`docs/data/questions/${ref.id}.json`)),manifest=q.trace_manifest[ref.phase];
  assert.equal(createHash('sha256').update(packed).digest('hex'),manifest.packed_sha256);
  assert.equal(createHash('sha256').update(new Uint8Array(trace.ids.buffer)).digest('hex'),manifest.ids_sha256);
  assert.equal(createHash('sha256').update(new Uint8Array(trace.weights.buffer)).digest('hex'),manifest.weights_sha256);
  const avg=mean(trace);for(let i=0;i<avg.length;i++)close(avg[i],ref.mean[i]);
  const matrix=ref.scope==='question'?avg:frame(trace,ref.token),curves=buildCurves(matrix,trace,ref.id);
  for(const expected of ref.expected){const got=result(curves,expected.mode==='manual'?expected.threshold:0,expected.mode,expected.limit);close(got.threshold,expected.threshold);for(const k of ['maximum_question','maximum_token']){close(got[k].fraction,expected[k].fraction);assert.equal(got[k].question,expected[k].question);assert.equal(got[k].layer,expected[k].layer);assert.equal(got[k].token,expected[k].token);}assert.equal(got.tokens,expected.tokens);assert.equal(got.questions,1);}
});
test('collection contains 1,800 unique, complete original questions',()=>{const c=JSON.parse(read('docs/data/catalog.json'));assert.equal(c.questions.length,1800);assert.equal(new Set(c.questions.map(q=>q.id)).size,1800);for(const d of c.domains)assert.equal(c.questions.filter(q=>q.domain===d.id).length,150);for(const row of c.questions){const q=JSON.parse(read(`docs/data/questions/${row.id}.json`));assert.equal(createHash('sha256').update(q.prompt).digest('hex'),q.prompt_sha256);assert.equal(createHash('sha256').update(q.text).digest('hex'),q.answer_sha256);assert.ok(q.prompt_en);assert.equal(q.input_ids.length,q.input_tokens.length);assert.equal(q.output_ids.length,q.output_token_text.length);assert.equal(q.audit.complete,true);}});
