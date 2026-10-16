"""Global layer/expert rankings. Offline coverage is not an inference speed gain."""
from pathlib import Path
import csv,io,json,struct
import numpy as np
from data_model import save,read,replace_snapshot,DOMAINS,LAYERS,EXPERTS

def empty():
    return {f'{split}_{phase}_{field}':(np.zeros((48,512),dtype=np.float64) if field in ('sum','means') else np.array(0,dtype=np.int64))
            for split in ('all','train','holdout') for phase in ('prefill','generation') for field in ('sum','means','tokens','questions')}
def add(acc,item,split):
    for group in ('all',split):
        for phase in ('prefill','generation'):
            n=int(item[phase+'_count'])
            if not n:continue
            key=f'{group}_{phase}_';s=item[phase+'_sum']
            acc[key+'sum']+=s;acc[key+'means']+=s/n;acc[key+'tokens']+=n;acc[key+'questions']+=1
def mean(acc,phase,weighting,split='all'):
    key=f'{split}_{phase}_';q=int(acc[key+'questions']);n=int(acc[key+'tokens'])
    return (acc[key+'means']/q if weighting=='question' else acc[key+'sum']/n) if q and n else None,q,n
def save_acc(path,acc):
    temp=Path(str(path)+'.tmp')
    with temp.open('wb') as f:np.savez_compressed(f,**acc)
    replace_snapshot(temp,path)
def load_acc(path):
    # Close the file before ZIP decompression so WebUI readers do not block
    # atomic replacement for the duration of NumPy's lazy array loading.
    snapshot=Path(path).read_bytes()
    with np.load(io.BytesIO(snapshot),allow_pickle=False) as z:return {k:z[k] for k in z.files}
def ranking(matrix,count):
    flat=matrix.ravel();indices=np.lexsort((np.arange(flat.size),-flat))[:count]
    return [(int(i//512),int(i%512)) for i in indices]
def mask(pairs):
    m=np.zeros((48,512),dtype=bool)
    for l,e in pairs:m[l,e]=True
    return m
def coverage(matrix,pairs):return float(matrix[mask(pairs)].sum()/48) if matrix is not None else None
def publish(run,final=False):
    run=Path(run);data=run/'data';catalog=read(data/'catalog.json');count=catalog['resident_experts']
    profile=Path(read(run/'protocol.json')['config']['profile']).read_bytes()
    magic,version,l,e,n,total=struct.unpack_from('<4s5I',profile);assert magic==b'STRP' and (l,e,n)==(48,512,count)
    baseline=[struct.unpack_from('<HH',profile,24+i*4) for i in range(n)]
    result=dict(status='final' if final else 'provisional',questions=len(catalog['questions']),residents=count,
        note='Classifica globale per massa del router: nessuna quota per layer. Profili sperimentali non applicati al modello. Copertura offline, non velocità misurata con la nuova hotlist.',profiles=[])
    dest=data/'hotlists';dest.mkdir(exist_ok=True)
    for domain,label in DOMAINS:
        path=data/'aggregates'/(domain+'.npz')
        if not path.exists():continue
        acc=load_acc(path)
        for phase in ('prefill','generation'):
            for weighting in ('question','token'):
                train,q,n=mean(acc,phase,weighting,'train')
                if train is None:continue
                held,hq,hn=mean(acc,phase,weighting,'holdout');allmean,aq,an=mean(acc,phase,weighting)
                pairs=ranking(train,count);fullpairs=ranking(allmean,count)
                summary=dict(domain=domain,name=label,phase=phase,weighting=weighting,train_questions=q,holdout_questions=hq,
                    all_questions=aq,train_tokens=n,holdout_tokens=hn,all_tokens=an,
                    train_mass=coverage(train,pairs),holdout_mass=coverage(held,pairs),baseline_holdout_mass=coverage(held,baseline),
                    overlap_with_baseline=len(set(pairs)&set(baseline))/count,
                    experts_per_layer=np.bincount([l for l,e in pairs],minlength=48).tolist())
                ident=f'{domain}-{phase}-{weighting}';summary['id']=ident
                save(dest/(ident+'.json'),dict(**summary,selection='train-only; entire held-out task families excluded',
                    ranked_pairs=[dict(layer=l,expert=e,weight=float(train[l,e])) for l,e in pairs],
                    descriptive_all_questions_pairs=[dict(layer=l,expert=e,weight=float(allmean[l,e])) for l,e in fullpairs]))
                result['profiles'].append(summary)
                if final:
                    # Full descriptive ranking is separate: never report its fit to held-out data as validation.
                    for label2,rank,mat in [('train',pairs,train),('all',fullpairs,allmean)]:
                        p=dest/(ident+'-'+label2+'.bin');p.write_bytes(struct.pack('<4s5I',b'STRP',1,48,512,count,count)+b''.join(struct.pack('<HH',*x) for x in rank))
                    with (dest/(ident+'.csv')).open('w',newline='',encoding='utf-8') as f:
                        writer=csv.writer(f);writer.writerow(['rank','layer','expert','train_mean_weight'])
                        writer.writerows((i+1,l,e,format(float(train[l,e]),'.17g')) for i,(l,e) in enumerate(pairs))
    save(data/'hotlists.json',result)
    return result
