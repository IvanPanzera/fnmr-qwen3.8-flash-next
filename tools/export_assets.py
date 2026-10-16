"""Export a completed Router Lab collection. Never runs the language model.

python tools/export_assets.py --source path/to/campaign/data --lab path/to/router-lab
The source is read-only. Sparse ids/weights are byte-shuffled and gzip-compressed
losslessly. Every exported stream is reconstructed and compared with its source.
"""
from pathlib import Path
import argparse, concurrent.futures, gzip, hashlib, json, struct, sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
DOMAINS=dict(codice='Code generation',debug='Debugging and tests',dati='SQL and data analysis',matematica='Mathematics',logica='Logical reasoning',ingegneria='Engineering',scienze='Science explanations',documenti='Document analysis',estrazione='Extraction and JSON',traduzione='Translation and languages',professionale='Professional writing',creativa='Creative writing')
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def digest(b):return hashlib.sha256(b).hexdigest()
def write_json(p,x,compress=False):
    p.parent.mkdir(parents=True,exist_ok=True)
    b=json.dumps(x,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode('utf-8')
    p.write_bytes(gzip.compress(b,compresslevel=6,mtime=0) if compress else b)
def export_question(pair):
    ordinal,row=pair;q=read(SOURCE/row['id']/'question.json');ident=q['id']
    assert digest(q['prompt'].encode())==q['prompt_sha256']
    assert q['audit']['complete']
    keys='id domain title family variant seed split prompt max_new prompt_sha256 input_ids rendered input_sha256 started_utc ordinal output_tokens prompt_tokens prefill_seconds decode_seconds finish draft_accepted draft_offered reused hits lookups output_ids token_seconds wall_seconds terminal_capture_seconds text finished_utc input_tokens output_token_text metrics audit raw_trace_sha256'.split()
    public={k:q[k] for k in keys if k in q};public['collection_index']=ordinal+1
    public['answer_sha256']=digest(q['text'].encode());public['trace_manifest']={}
    for phase in ('prefill','generation'):
        ids=(SOURCE/ident/(phase+'.ids')).read_bytes();weights=(SOURCE/ident/(phase+'.weights')).read_bytes()
        count=len(ids)//960;assert len(ids)==count*960 and len(weights)==count*1920
        assert count==len(q['input_ids' if phase=='prefill' else 'output_ids'])
        si=np.frombuffer(ids,dtype='u1').reshape(-1,2).T.copy().tobytes()
        sw=np.frombuffer(weights,dtype='u1').reshape(-1,4).T.copy().tobytes()
        packed=struct.pack('<4sIII',b'FNR1',count,48,10)+si+sw
        compressed=gzip.compress(packed,compresslevel=6,mtime=0)
        dest=ROOT/'data/traces'/ident/(phase+'.fnr.gz');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(compressed)
        decoded=gzip.decompress(compressed);n=count*480
        ri=np.frombuffer(decoded[16:16+n*2],dtype='u1').reshape(2,-1).T.copy().tobytes()
        rw=np.frombuffer(decoded[16+n*2:],dtype='u1').reshape(4,-1).T.copy().tobytes()
        assert ri==ids and rw==weights
        public['trace_manifest'][phase]=dict(tokens=count,ids_sha256=digest(ids),weights_sha256=digest(weights),packed_sha256=digest(packed),gzip_sha256=digest(compressed),gzip_bytes=len(compressed),format='FNR1')
    write_json(ROOT/'docs/data/questions'/(ident+'.json'),public)
    return dict(id=ident,source_question_sha256=digest((SOURCE/ident/'question.json').read_bytes()),prompt_sha256=q['prompt_sha256'],answer_sha256=public['answer_sha256'],traces=public['trace_manifest'])
def export_curves():
    from filter_analysis import Analysis
    from data_model import aggregate
    from hotlists import load_acc
    for domain in DOMAINS:
        rows=[r for r in CATALOG['questions'] if r['domain']==domain]
        summaries=[load_acc(SOURCE/r['id']/'sums.npz') for r in rows]
        for phase in ('prefill','generation'):
            items=[dict(id=r['id'],matrix=s[phase+'_sum']/int(s[phase+'_count'])) for r,s in zip(rows,summaries)]
            def traces():
                for r,s in zip(rows,summaries):
                    count=int(s[phase+'_count']);folder=SOURCE/r['id']
                    yield np.fromfile(folder/(phase+'.ids'),dtype='<u2').reshape(count,48,10),np.fromfile(folder/(phase+'.weights'),dtype='<f4').reshape(count,48,10)
            for weighting in ('question','token'):
                matrix,n,tokens=aggregate(summaries,phase,weighting)
                write_json(ROOT/'docs/data/matrices'/f'{domain}-{phase}-{weighting}.json.gz',dict(matrix=matrix.ravel().tolist(),questions=n,tokens=tokens),True)
                analysis=Analysis(matrix,items,traces())
                curves=dict(thresholds=analysis.thresholds.tolist(),question_ids=[r['id'] for r in rows],tokens=tokens)
                for name,curve in [('question',analysis.question),('token',analysis.token)]:
                    curves[name]=dict(loss=curve.loss.tolist(),question=curve.question.tolist(),unit=curve.unit.tolist())
                write_json(ROOT/'docs/data/curves'/f'{domain}-{phase}-{weighting}.json.gz',curves,True)
                print('curves',domain,phase,weighting,flush=True)
def main():
    global SOURCE,CATALOG
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--lab',type=Path,required=True);p.add_argument('--curves-only',action='store_true');args=p.parse_args()
    SOURCE=args.source;sys.path.insert(0,str(args.lab.resolve()));CATALOG=read(SOURCE/'catalog.json')
    assert len(CATALOG['questions'])==1800
    if not args.curves_only:
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            manifest=[]
            for i,x in enumerate(pool.map(export_question,enumerate(CATALOG['questions']))):
                manifest.append(x)
                if (i+1)%100==0:print('exported',i+1,flush=True)
        write_json(ROOT/'docs/data/provenance.json',dict(schema=1,source_catalog_sha256=digest((SOURCE/'catalog.json').read_bytes()),questions=manifest,lossless_roundtrip_verified=1800))
        public={k:CATALOG[k] for k in ('title','layers','experts','top_k','resident_experts','questions')}
        public.update(title='fnMR · Qwen3.8-Flash-Next',version='1.0',status='complete',planned_total=1800,planned_per_domain=150,completed_utc='2026-10-08T22:18:44.872413+00:00',domains=[dict(id=k,name=v) for k,v in DOMAINS.items()],allocation_note='1,504 layer–expert pairs resident on GPU; remaining experts computed on CPU. No expert omission. Fixed global residency profile during collection.')
        write_json(ROOT/'docs/data/catalog.json',public)
        hot=read(SOURCE/'hotlists.json');hot['note']='Offline router-mass coverage. Profiles were not applied during this collection.'
        for x in hot['profiles']:x['name']=DOMAINS[x['domain']]
        write_json(ROOT/'docs/data/hotlists.json',hot)
        for file in (SOURCE/'hotlists').iterdir():
            dest=ROOT/'docs/data/hotlists'/file.name;dest.parent.mkdir(parents=True,exist_ok=True)
            if file.suffix=='.json':
                obj=read(file);obj['name']=DOMAINS[obj['domain']];write_json(dest,obj)
            else:dest.write_bytes(file.read_bytes())
        report=read(SOURCE.parent/'completion/report.json')
        write_json(ROOT/'docs/data/summary.json',{k:report[k] for k in ('completed_utc','elapsed_wall_seconds','questions','questions_per_domain','train_questions','holdout_questions','totals','domains')})
    export_curves()
if __name__=='__main__':main()
