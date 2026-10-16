import {traceBase} from './config.js';
export async function request(url,signal){const r=await fetch(url,{signal});if(!r.ok)throw new Error(`Could not load ${url.split('/').slice(-2).join('/')} (${r.status}). Retry this selection.`);return r;}
export async function json(url,signal){return (await request(url,signal)).json();}
export async function compressed(url,signal){
  const r=await request(url,signal);
  if(!globalThis.DecompressionStream)throw new Error('This viewer needs a modern browser with gzip decompression support.');
  return new Response(r.body.pipeThrough(new DecompressionStream('gzip'))).arrayBuffer();
}
export async function compressedJSON(url,signal){return JSON.parse(new TextDecoder().decode(await compressed(url,signal)));}
export function decodeTrace(buffer){
  const h=new DataView(buffer);if(h.getUint32(0,true)!==0x31524e46||h.getUint32(8,true)!==48||h.getUint32(12,true)!==10)throw new Error('Invalid FNR1 trace header');
  const count=h.getUint32(4,true),n=count*480;
  if(buffer.byteLength!==16+n*6)throw new Error('Incomplete trace download');
  const source=new Uint8Array(buffer),idBytes=new Uint8Array(n*2),weightBytes=new Uint8Array(n*4);
  for(let byte=0;byte<2;byte++)for(let i=0;i<n;i++)idBytes[i*2+byte]=source[16+byte*n+i];
  for(let byte=0;byte<4;byte++)for(let i=0;i<n;i++)weightBytes[i*4+byte]=source[16+n*2+byte*n+i];
  return {count,ids:new Uint16Array(idBytes.buffer),weights:new Float32Array(weightBytes.buffer)};
}
export async function trace(id,phase,manifest,signal){
  const buffer=await compressed(`${traceBase}${encodeURIComponent(id)}/${phase}.fnr.gz`,signal);
  if(manifest && globalThis.crypto?.subtle){
    const sha=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',buffer)),x=>x.toString(16).padStart(2,'0')).join('');
    if(sha!==manifest.packed_sha256)throw new Error('Trace checksum mismatch. Reload before inspecting this data.');
  }
  return decodeTrace(buffer);
}
