"""Append-only cancellation record; the completed candidate build is retained."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, subprocess, sys

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'acceleration/results/20260930_hadamard_balanced_caps_cancellation'
def sha(p):
    with p.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
def key(p): return p.relative_to(ROOT).as_posix()
def main():
    base=ROOT/'acceleration/results/20260930_independent_review/hadamard_balanced_gram_unsat_v2/summary.json'
    caps=ROOT/'acceleration/results/20260930_hadamard_balanced_gram_caps/summary.json'
    assert sha(base)=='edbbda720ea38ca5c565837bc39b5083eb145a64386c9e070fe89dfe5d6cebc5'
    assert sha(caps)=='dca108814a99a181df0c75f32e70794c625c44ec3317b38c635f793474177162'
    OUT.mkdir(exist_ok=False)
    paths=[base,caps,Path(__file__),ROOT/'acceleration/theory_20260930_hadamard_balanced_gram_caps.py',ROOT/'acceleration/theory_20260930_hadamard_balanced_gram_caps_spec.md']
    data=dict(status='COMPLETED_BUILD_RETAINED_SUBSEQUENT_SEARCH_CANCELLED',timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),
        inputs_sha256={key(p):sha(p) for p in paths},native_cap_solver_calls=0,cap_encoding_independently_approved=False,
        reason='The independently checked complete UNSAT proof excludes the same balanced fixed-support Gram family before imposing caps; the extra cap search is unnecessary.',
        preservation='Completed producer source/spec/build/clauses remain unchanged. Cap artifacts are candidate engineering output, not independently promoted.',
        scope='One fixed six-prism Hadamard support and balanced local triples only; no unbalanced-support or target exclusion.',artifact_availability='LOCAL_ONLY')
    with (OUT/'cancellation.json').open('x',encoding='utf-8',newline='\n') as f: json.dump(data,f,indent=2);f.write('\n')
    print(json.dumps({'path':key(OUT/'cancellation.json'),'sha256':sha(OUT/'cancellation.json')}))
if __name__=='__main__': main()
