"""Build all 1,800 English prompt translations from the frozen templates."""
from pathlib import Path
import argparse, json, random, sys, hashlib
import prompts_en as en
ROOT=Path(__file__).resolve().parents[1]
def families(raw):
    result=[]
    for line in raw.splitlines():
        if '|' in line:result.append(line.split('|',1))
        else:result[-1][1]+='\n'+line
    assert len(result)==20
    return result
def context(domain,rng,v,a,b,c,original):
    n=[4,10,22][v%3];rs=original.rows(rng,n,v)
    if domain in ('dati','estrazione'):
        result=en.GLOSSARY+'\nRegister:\n'+json.dumps(rs,ensure_ascii=False)
        return result+'\nMeasurement series: '+str([rng.randrange(0,90) for _ in range(n)]) if domain=='dati' else result
    if domain=='documenti':
        departments=dict(impianti='building services',strutture='structures',edilizia='construction')
        statuses={'approvato':'approved','sospeso':'suspended','in revisione':'under review'}
        return 'Document (fictional data):\n'+'\n'.join(f'Line {i+1}. {r["responsabile"]}, responsible for the {departments[r["reparto"]]} department, reports case {r["id"]}, status {statuses[r["stato"]]}, budget '+('not specified' if r['importo'] is None else str(r['importo'])+' euros')+', deadline '+(r['data'] or 'to be defined')+'. The review depends on the availability of the updated drawing.' for i,r in enumerate(rs))+f'\nLine {n+1}. The proposal to bring all deadlines forward has not been approved. The stated amounts are estimates, not actual costs.'
    if domain=='traduzione':
        it=f'{original.NAMES[v]} coordinates the project review at the {en.PLACES[v]}. Delivery of {a} drawings is scheduled for November {v+1}, 2026. The available budget is {c} euros. There are still {b} checks to complete. The date remains conditional on receipt of the documents; it is not a final confirmation.'
        source_en=f'{original.NAMES[v]} coordinate the project review at a local workshop. We has {a} drawings to check before November {v+1}, 2026. The available budget is EUR {c}. The delivery date depends on the missing documents and is not yet confirmed.'
        return 'Italian source (English reading translation): '+it+'\nEnglish source (for tasks that require it; original grammar retained): '+source_en
    if domain=='professionale':return f'Context: {en.PLACES[v]} project, contact {original.NAMES[v]}, {a} planned documents and {b} still to check, budget {c} euros, meeting on November {v+1}, 2026. The supplier drawings are missing. The proposed delivery has not been confirmed. Do not invent additional agreements.'
    if domain=='creativa':return f'Situation: {original.NAMES[v]} arrives at a {en.PLACES[v]} and finds an object that recalls a forgotten commitment. Include the number {a} naturally. '+['Restrained tone, no magical elements.','Fantastic tone, precise material details.','Intimate tone, no final explanation.'][v%3]
    if domain=='codice':return f'Application: internal tools for a {en.PLACES[v]}. Example data, if relevant: '+str([rng.randrange(-a,b+1) for _ in range([5,12,25][v%3])])+'. Handle empty input, duplicates and errors. Return code and a small example call.'
    if domain=='debug':return f'The fix is for a {en.AUDIENCES[v%5]}. Show the cause, a minimal change and '+str(1+v%3)+' tests, including boundary cases. Do not replace the problem with an unrelated rewrite.'
    if domain in ('scienze','ingegneria'):return f'Audience: {en.AUDIENCES[v%5]}. '+['Use a numerical example and check units.','Explain assumptions and one limitation of the model.','Distinguish known data from assumptions, with a concrete example.'][v%3]
    return f'Audience: {en.AUDIENCES[v%5]}. '+['Show the essential steps and an independent check.','Present the result before the steps and state assumptions.','Explain the reasoning to a nonspecialist reader without omitting the check.'][v%3]
def main():
    p=argparse.ArgumentParser();p.add_argument('--lab',type=Path,required=True);args=p.parse_args();sys.path.insert(0,str(args.lab.resolve()));import corpus
    originals={q['id']:q for q in corpus.requests()}
    catalog=json.loads((ROOT/'docs/data/catalog.json').read_text('utf-8'))
    count=0
    for row in catalog['questions']:
        path=ROOT/'docs/data/questions'/(row['id']+'.json');q=json.loads(path.read_text('utf-8'));orig=originals[q['id']]
        assert q['prompt']==orig['prompt'] and q['prompt_sha256']==orig['prompt_sha256']
        rng=random.Random(q['seed']);a=rng.randrange(3,15);b=rng.randrange(3,12);c=rng.randrange(120,900);d=c+rng.randrange(-80,90)
        title,task=families(en.TASKS[q['domain']])[q['family']]
        english=task.format(a=a,b=b,c=c,d=d,odd=2*a+1)+'\n\n'+context(q['domain'],rng,q['variant'],a,b,c,corpus)
        english+='\n\nKeep the answer concise: at most about 120 words, or the requested code or data. Do not include internal reasoning.'
        q['prompt_en']=english;q['title_original']=q['title'];q['title']=f'{title} · scenario {q["variant"]+1:02d}'
        q['prompt_translation']=dict(method='English task templates and deterministic context translation',sha256=hashlib.sha256(english.encode()).hexdigest(),used_for_inference=False)
        path.write_text(json.dumps(q,ensure_ascii=False,separators=(',',':')),encoding='utf-8');row['title']=q['title'];count+=1
    (ROOT/'docs/data/catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    print('Original prompts reconstructed exactly and English translations written:',count)
if __name__=='__main__':main()
