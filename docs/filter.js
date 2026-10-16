import {mean} from './math.js';
export function upperBound(a,x){let l=0,r=a.length;while(l<r){const m=(l+r)>>>1;if(a[m]<=x)l=m+1;else r=m;}return l;}
export function nextUp(x){if(x===0)return Number.MIN_VALUE;if(x===Infinity)return x;const b=new ArrayBuffer(8),d=new DataView(b);d.setFloat64(0,x);d.setBigUint64(0,d.getBigUint64(0)+1n);return d.getFloat64(0);}
function curve(n){const q=new Int32Array(n),u=new Int32Array(n);q.fill(-1);u.fill(-1);return {loss:new Float64Array(n),question:q,unit:u};}
function addUnit(c,thresholds,scores,weights,unit){
  const order=Array.from({length:scores.length},(_,i)=>i).sort((a,b)=>scores[a]-scores[b]);let total=0,cum=0;for(const i of order)total+=weights[i];
  for(const i of order){cum+=weights[i];const event=upperBound(thresholds,scores[i]);if(event>=thresholds.length)continue;const value=total?Math.min(cum/total,1):0;
    if(value>c.loss[event]||(value===c.loss[event]&&value>0&&unit>c.unit[event])){c.loss[event]=value;c.question[event]=0;c.unit[event]=unit;}
  }
}
function finish(c){let max=0,qi=-1,unit=-1;for(let i=0;i<c.loss.length;i++){if(c.loss[i]>max){max=c.loss[i];qi=c.question[i];unit=c.unit[i];}c.loss[i]=max;c.question[i]=qi;c.unit[i]=unit;}return c;}
export function buildCurves(matrix,trace,qid){
  const positive=Array.from(matrix).filter(x=>x>0).map(nextUp).filter(x=>x<=1),thresholds=Array.from(new Set([0,Number.MIN_VALUE,...positive,1])).sort((a,b)=>a-b);
  const question=curve(thresholds.length),token=curve(thresholds.length),m=mean(trace),scores=new Float64Array(10),weights=new Float64Array(10);
  for(let l=0;l<48;l++)addUnit(question,thresholds,matrix.slice(l*512,(l+1)*512),m.slice(l*512,(l+1)*512),l);
  for(let t=0;t<trace.count;t++)for(let l=0;l<48;l++){const start=t*480+l*10;for(let k=0;k<10;k++){scores[k]=matrix[l*512+trace.ids[start+k]];weights[k]=trace.weights[start+k];}addUnit(token,thresholds,scores,weights,t*48+l);}
  return {thresholds,question:finish(question),token:finish(token),question_ids:[qid],tokens:trace.count};
}
export function result(curves,threshold,mode,limit){
  if(mode!=='manual'){const c=curves[mode];let i=c.loss.length-1;while(i>0&&c.loss[i]>limit)i--;threshold=curves.thresholds[i];}
  const index=Math.max(0,upperBound(curves.thresholds,threshold)-1);
  function maximum(name){const c=curves[name],q=c.question[index],u=c.unit[index];return {fraction:c.loss[index],question:q<0?null:curves.question_ids[q],layer:u<0?null:u%48,token:name==='token'&&u>=0?Math.floor(u/48)+1:null};}
  return {threshold,mode,limit,questions:curves.question_ids.length,tokens:curves.tokens,maximum_question:maximum('question'),maximum_token:maximum('token')};
}
