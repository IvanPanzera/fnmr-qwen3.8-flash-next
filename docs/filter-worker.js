import {buildCurves,result} from './filter.js';
import {compressedJSON} from './data.js';
let cachedKey='',cached=null;
self.onmessage=async({data:m})=>{try{
  let c;if(cachedKey===m.key)c=cached;else{
    c=m.domainPath?await compressedJSON(m.domainPath):buildCurves(m.matrix,m.trace,m.qid);
    cachedKey=m.key;cached=c;
  }
  self.postMessage({sequence:m.sequence,result:result(c,m.threshold,m.mode,m.limit)});
}catch(e){self.postMessage({sequence:m.sequence,error:e.message});}};
