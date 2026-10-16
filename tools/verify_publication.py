"""Verify all published question text and trace hashes. No inference required."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
catalog=json.loads((ROOT/'docs/data/catalog.json').read_text('utf-8'))
rows=catalog['questions'];assert len(rows)==1800
assert len({r['id'] for r in rows})==1800
counts={d['id']:0 for d in catalog['domains']};traces=0
for row in rows:
    q=json.loads((ROOT/'docs/data/questions'/f"{row['id']}.json").read_text('utf-8'))
    counts[q['domain']]+=1
    assert q['audit']['complete'] and q['prompt_en'] and q['answer_en']
    assert sha(q['prompt'].encode())==q['prompt_sha256']
    assert sha(q['text'].encode())==q['answer_sha256']
    assert sha(q['answer_en'].encode())==q['answer_translation']['sha256']
    assert q['answer_translation']['used_for_inference'] is False
    for phase,m in q['trace_manifest'].items():
        p=ROOT/'data/traces'/q['id']/f'{phase}.fnr.gz'
        assert p.stat().st_size==m['gzip_bytes']
        assert sha(p.read_bytes())==m['gzip_sha256'];traces+=1
assert set(counts.values())=={150};assert traces==3600
print(json.dumps(dict(questions=len(rows),traces=traces,domains=counts,original_and_english_hashes='verified',compressed_trace_hashes='verified')))
