"""Read-only loss bounds for one common layer/expert mask, including raw tokens."""
from collections import OrderedDict
import threading
import numpy as np
from data_model import aggregate
from hotlists import load_acc

class LossCurve:
    def __init__(self,thresholds):
        self.thresholds=thresholds
        self.loss=np.zeros(len(thresholds))
        self.question=np.full(len(thresholds),-1,dtype=np.int32)
        self.unit=np.full(len(thresholds),-1,dtype=np.int32)

    def add(self,scores,weights,question):
        # A unit is one layer of a question mean, or one layer of one token.
        # Tied mask scores disappear together; no arbitrary tie-breaking.
        order=np.argsort(scores,axis=1,kind='stable')
        sorted_scores=np.take_along_axis(scores,order,axis=1)
        sorted_weights=np.take_along_axis(weights,order,axis=1)
        totals=sorted_weights.sum(axis=1,keepdims=True)
        cumulative=np.divide(np.cumsum(sorted_weights,axis=1),totals,
                             out=np.zeros_like(sorted_weights,dtype=np.float64),where=totals>0)
        cumulative=np.minimum(cumulative,1)
        events=np.searchsorted(self.thresholds,sorted_scores.ravel(),side='right')
        values=cumulative.ravel();valid=events<len(self.loss)
        events,values,positions=events[valid],values[valid],np.flatnonzero(valid)
        local=np.zeros_like(self.loss);np.maximum.at(local,events,values)
        winners=(values==local[events])&(values>self.loss[events])
        witness=np.full(len(self.loss),-1,dtype=np.int64)
        np.maximum.at(witness,events[winners],positions[winners])
        changed=witness>=0
        self.loss[changed]=local[changed];self.question[changed]=question
        self.unit[changed]=witness[changed]//scores.shape[1]

    def finish(self):
        maximum=np.maximum.accumulate(self.loss)
        changed=self.loss>np.r_[0,maximum[:-1]]
        source=np.maximum.accumulate(np.where(changed,np.arange(len(maximum)),-1))
        valid=source>=0
        self.question[valid]=self.question[source[valid]]
        self.unit[valid]=self.unit[source[valid]]
        self.loss=maximum

    def index(self,threshold):
        return max(0,int(np.searchsorted(self.thresholds,threshold,side='right')-1))

class Analysis:
    def __init__(self,matrix,items,traces):
        self.matrix=np.asarray(matrix,dtype=np.float64)
        # Candidate thresholds just above a distinct score preserve the strict
        # '< threshold' rule. Equal scores are never split to fit the budget.
        values=np.nextafter(np.unique(self.matrix[self.matrix>0]),np.inf)
        self.thresholds=np.unique(np.r_[0.,np.nextafter(0.,np.inf),values[values<=1],1.])
        self.items=items;self.question=LossCurve(self.thresholds);self.token=LossCurve(self.thresholds)
        self.tokens=0
        for qi,(item,trace) in enumerate(zip(items,traces)):
            ids,weights=trace;self.tokens+=len(ids)
            weights=np.asarray(weights,dtype=np.float64)
            self.question.add(self.matrix,item['matrix'],qi)
            scores=self.matrix[np.arange(48)[None,:,None],ids]
            self.token.add(scores.reshape(-1,10),weights.reshape(-1,10),qi)
        self.question.finish();self.token.finish()

    def result(self,threshold,mode,limit):
        if mode!='manual':
            curve=self.question if mode=='question' else self.token
            allowed=np.flatnonzero(curve.loss<=limit)
            threshold=float(self.thresholds[allowed[-1]])
        index=self.question.index(threshold)
        def maximum(curve,token=False):
            qi=int(curve.question[index]);unit=int(curve.unit[index])
            return dict(fraction=float(curve.loss[index]),question=None if qi<0 else self.items[qi]['id'],
                        layer=None if unit<0 else unit%48,
                        token=None if not token or unit<0 else unit//48+1)
        return dict(threshold=threshold,mode=mode,limit=limit,questions=len(self.items),tokens=self.tokens,
                    maximum_question=maximum(self.question),maximum_token=maximum(self.token,True),
                    matrix=self.matrix.ravel().tolist(),bound_per_layer=True)

_cache=OrderedDict()
_lock=threading.Lock()

def analyze(data,catalog,query):
    phase=query.get('phase','prefill');scope=query.get('scope','question');weighting=query.get('weighting','question')
    mode=query.get('mode','manual');threshold=float(query.get('threshold',0));limit=float(query.get('limit',.1))
    if phase not in ('prefill','generation') or scope not in ('token','question','domain') or weighting not in ('question','token') or mode not in ('manual','question','token'):
        raise ValueError('Modalità del filtro non valida')
    if not np.isfinite(threshold) or not 0<=threshold<=1 or not np.isfinite(limit) or not 0<=limit<=1:
        raise ValueError('Le percentuali devono essere comprese tra 0 e 100')
    rows=catalog['questions'];through=query.get('through')
    if through:
        positions={r['id']:i for i,r in enumerate(rows)}
        if through not in positions:raise ValueError('Snapshot non disponibile')
        rows=rows[:positions[through]+1]
    rows=[r for r in rows if (r['domain']==query.get('domain') if scope=='domain' else r['id']==query.get('question'))]
    if not rows:raise ValueError('Nessuna domanda disponibile')
    token=int(query.get('token',0)) if scope=='token' else 0
    key=(str(data),tuple(r['id'] for r in rows),phase,scope,weighting,token)
    with _lock:
        analysis=_cache.get(key)
        if analysis is None:
            summaries=[load_acc(data/r['id']/'sums.npz') for r in rows]
            items=[dict(id=r['id'],matrix=s[phase+'_sum']/int(s[phase+'_count'])) for r,s in zip(rows,summaries)]
            if scope=='domain':matrix=aggregate(summaries,phase,weighting)[0]
            elif scope=='question':matrix=items[0]['matrix']
            else:
                folder=data/rows[0]['id']
                count=int(summaries[0][phase+'_count'])
                if not 0<=token<count:raise ValueError('Token fuori intervallo')
                with (folder/(phase+'.ids')).open('rb') as f:
                    f.seek(token*480*2);ids=np.frombuffer(f.read(480*2),dtype='<u2').reshape(48,10)
                with (folder/(phase+'.weights')).open('rb') as f:
                    f.seek(token*480*4);weights=np.frombuffer(f.read(480*4),dtype='<f4').reshape(48,10)
                matrix=np.zeros((48,512));matrix[np.arange(48)[:,None],ids]=weights
            def traces():
                for r,s in zip(rows,summaries):
                    folder=data/r['id'];count=int(s[phase+'_count'])
                    ids=np.fromfile(folder/(phase+'.ids'),dtype='<u2').reshape(count,48,10)
                    weights=np.fromfile(folder/(phase+'.weights'),dtype='<f4').reshape(count,48,10)
                    yield ids,weights
            analysis=Analysis(matrix,items,traces());_cache[key]=analysis
            while len(_cache)>2:_cache.popitem(last=False)
        _cache.move_to_end(key)
        return analysis.result(threshold,mode,limit)
