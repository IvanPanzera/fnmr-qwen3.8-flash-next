export function cuts(matrix,threshold){
  let total=0,cut=0,active=0,hidden=0;const layers=[];
  for(let l=0;l<48;l++){let row=0,lost=0;
    for(let e=0;e<512;e++){const v=matrix[l*512+e];total+=v;row+=v;if(v>0){active++;if(v<threshold){cut+=v;lost+=v;hidden++;}}}
    layers.push(row?lost/row:0);
  }
  return {total,cut,fraction:total?cut/total:0,active,hidden,layers};
}
export function frame(trace,t){
  const matrix=new Float64Array(48*512);let at=t*48*10;
  for(let l=0;l<48;l++)for(let k=0;k<10;k++,at++)matrix[l*512+trace.ids[at]]=trace.weights[at];
  return matrix;
}
export function mean(trace){
  const matrix=new Float64Array(48*512);
  for(let t=0;t<trace.count;t++){let at=t*480;for(let l=0;l<48;l++)for(let k=0;k<10;k++,at++)matrix[l*512+trace.ids[at]]+=trace.weights[at];}
  for(let i=0;i<matrix.length;i++)matrix[i]/=trace.count;
  return matrix;
}
