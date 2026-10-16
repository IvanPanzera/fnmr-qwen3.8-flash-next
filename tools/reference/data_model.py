"""Lossless sparse router traces and explicitly defined aggregation semantics."""
from pathlib import Path
import json,struct,time
import numpy as np

LAYERS,EXPERTS,K=48,512,10
DOMAINS=[('codice','Generazione di codice'),('debug','Correzione e test'),('dati','SQL e analisi di dati'),
 ('matematica','Calcoli e matematica'),('logica','Ragionamento logico'),('ingegneria','Ingegneria e tecnica'),
 ('scienze','Spiegazioni scientifiche'),('documenti','Lettura e sintesi'),('estrazione','Estrazione e JSON'),
 ('traduzione','Traduzione e lingue'),('professionale','Scrittura professionale'),('creativa','Scrittura creativa')]

def _retry_windows_sharing(operation,timeout):
    deadline=time.monotonic()+timeout;delay=0.025
    while True:
        try:
            operation()
            return
        except OSError as exc:
            remaining=deadline-time.monotonic()
            # Access/sharing/lock violations can be transient on Windows.
            # Other errors are not retried; a failed temp remains recoverable.
            if getattr(exc,'winerror',None) not in (5,32,33) or remaining<=0:raise
            time.sleep(min(delay,remaining));delay=min(delay*2,0.25)

def replace_snapshot(temp,path,timeout=5.0):
    """Keep the previous snapshot intact while Windows readers briefly hold it."""
    _retry_windows_sharing(lambda:Path(temp).replace(path),timeout)

def publish_directory(staging,destination,timeout=5.0):
    """Publish a complete response without overwriting any existing response.

    A Windows handle on a staging file can briefly prevent its parent rename.
    On persistent failure the entire staging directory remains recoverable.
    """
    staging,destination=Path(staging),Path(destination)
    def rename():
        if destination.exists():raise FileExistsError(str(destination))
        staging.rename(destination)
    _retry_windows_sharing(rename,timeout)

def save(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix(path.suffix+'.tmp')
    temp.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    replace_snapshot(temp,path)

def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))

def sparse_sum(ids,weights):
    result=np.zeros((LAYERS,EXPERTS),dtype=np.float64)
    for layer in range(LAYERS):
        np.add.at(result[layer],ids[:,layer,:].ravel(),weights[:,layer,:].ravel())
    return result

def aggregate(items,phase,weighting):
    """Items contain phase sums and token counts; empty phases never add zero votes."""
    if phase not in ('prefill','generation','all'):raise ValueError('Invalid phase')
    if weighting not in ('question','token'):raise ValueError('Invalid weighting')
    means=[];sums=[];counts=[]
    for item in items:
        phases=('prefill','generation') if phase=='all' else (phase,)
        n=sum(int(item[p+'_count']) for p in phases)
        if not n:continue
        total=sum((item[p+'_sum'] for p in phases),np.zeros((LAYERS,EXPERTS),dtype=np.float64))
        means.append(total/n);sums.append(total);counts.append(n)
    if not counts:return None,0,0
    matrix=np.mean(means,axis=0) if weighting=='question' else np.sum(sums,axis=0)/sum(counts)
    return matrix,len(counts),sum(counts)

def parse_trace(path,input_ids,output_ids):
    """Keep committed target inputs only; rejected drafts are retained in the raw file."""
    raw=Path(path).read_bytes();assert raw[:8]==b'NBRTRC01','Wrong trace version'
    offset=8;windows={};records=[];commits={};emitted=[];complete=False;prompt=None;tail=[]
    while offset<len(raw):
        assert len(raw)-offset>=32,'Truncated record header'
        kind,a,b,c,d,e,pos=struct.unpack_from('<6iq',raw,offset);offset+=32
        if kind==1:
            assert prompt is None and (c,d,e)==(LAYERS,EXPERTS,K)
            prompt=b
        elif kind==2:
            assert b>0 and a not in windows
            tokens=np.frombuffer(raw,dtype='<i4',count=b,offset=offset).copy();offset+=b*4
            windows[a]={'pos':pos,'tokens':tokens,'tail':bool(c)}
        elif kind==3:
            assert 0<=b<LAYERS and c>0 and d==K and e in (0,1)
            count=c*d
            ids=np.frombuffer(raw,dtype='<i4',count=count,offset=offset).reshape(c,d).copy();offset+=count*4
            weights=np.frombuffer(raw,dtype='<f4',count=count,offset=offset).reshape(c,d).copy();offset+=count*4
            assert (ids>=0).all() and (ids<EXPERTS).all()
            assert np.isfinite(weights).all() and (weights>=0).all()
            assert np.allclose(weights.sum(axis=1),1,rtol=0,atol=2e-5),'Router rows must sum to one'
            assert np.all(np.diff(np.sort(ids,axis=1),axis=1)>0),'Duplicate expert ids'
            records.append((a,b,pos,ids,weights))
        elif kind==4:
            assert a in windows and a not in commits
            assert 1<=b<=len(windows[a]['tokens'])
            commits[a]=b
            if c:tail.extend(range(pos,pos+b))
        elif kind==5:
            assert b==len(emitted) and pos==prompt+b
            emitted.append(a)
        elif kind==6:
            assert b==len(emitted);complete=True;assert offset==len(raw)
        else:raise AssertionError('Unknown trace record '+str(kind))
    assert complete and prompt==len(input_ids) and emitted==output_ids
    tokens=np.array(input_ids+output_ids,dtype=np.int32);N=len(tokens)
    ids=np.zeros((N,LAYERS,K),dtype=np.uint16)
    weights=np.zeros((N,LAYERS,K),dtype=np.float32);seen=np.zeros((N,LAYERS),dtype=bool)
    for window,layer,pos,ri,rw in records:
        # A final accepted speculative window can extend past EOS/max_new.
        # Those unexposed positions are not part of the displayed response.
        if pos>=N:continue
        keep=len(ri)
        if window:
            assert window in windows
            w=windows[window];start=pos-w['pos']
            keep=max(0,min(keep,commits.get(window,0)-start))
            end=min(pos+keep,N)
            assert np.array_equal(w['tokens'][start:start+end-pos],tokens[pos:end]),'Committed token alignment error'
        keep=max(0,min(keep,N-pos))
        if not keep:continue
        assert not seen[pos:pos+keep,layer].any(),'Duplicate committed trace row'
        seen[pos:pos+keep,layer]=True
        ids[pos:pos+keep,layer]=ri[:keep];weights[pos:pos+keep,layer]=rw[:keep]
    assert seen.all(),f'Missing {np.count_nonzero(~seen)} token/layer rows'
    return ids,weights,dict(tokens=N,rows=N*LAYERS,dimensions=[LAYERS,EXPERTS],top_k=K,
        row_sum_max_error=float(np.max(np.abs(weights.sum(axis=2)-1))),
        speculative_windows=len(windows),rejected_draft_inputs=sum(len(w['tokens'])-commits.get(i,0) for i,w in windows.items()),
        terminal_diagnostic_positions=tail,complete=True)

def write_question(folder,question,ids,weights):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=False)
    n=len(question['input_ids']);summaries={}
    for phase,sl in [('prefill',slice(0,n)),('generation',slice(n,None))]:
        pi,pw=ids[sl],weights[sl];pi.astype('<u2').tofile(folder/(phase+'.ids'))
        pw.astype('<f4').tofile(folder/(phase+'.weights'))
        summaries[phase+'_sum']=sparse_sum(pi,pw);summaries[phase+'_count']=len(pi)
    np.savez_compressed(folder/'sums.npz',**summaries)
    save(folder/'question.json',question)
