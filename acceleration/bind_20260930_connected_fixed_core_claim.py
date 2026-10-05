"""Append-only correction of one dependency alias in a frozen audit receipt."""
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/'acceleration/results/20260930_independent_review/connected_fixed_core_cnf/summary.json'
REPORT_SHA='3ab0a89b8ab4f7043b0bca8d3c66bdb6cbfc7b52a5f4e949de2602feabcf7d3b'
def digest(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=False)
    if digest(REPORT)!=REPORT_SHA:raise ValueError('frozen audit changed')
    report=json.loads(REPORT.read_bytes());old='C-UNRESTRICTED-VARIABLE-CORE-FACTOR-CNF'
    new='C-UNRESTRICTED-TRIANGLE-NECESSARY-FACTOR-CNF-ENCODING'
    if report['dependencies'][1]!=dict(id=old,revision=1,relation='encoding_equivalence'):raise ValueError('exact typo record')
    now=datetime.now(timezone.utc).isoformat()
    result={k:report[k] for k in ['claim_id','claim_revision','statement','kind','basis','recommendation','review_state',
                                 'scope','assumptions','verifier','method','shared_components','limitations']}
    result.update(status='INDEPENDENT_CONNECTED_FIXED_CORE_CLAIM_BINDING_CORRECTED_METADATA',timestamp=now,
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv],cwd=str(ROOT),
        inputs_sha256={key(REPORT):REPORT_SHA,key(Path(__file__)):digest(Path(__file__))},
        correction=dict(field='dependencies[1].id',old=old,new=new,reason='The initial audit used an invented shorthand instead of the existing authoritative claim ID. The exact mathematical premise was always the pinned independent base encoding gate ecc6c2ee488e68826e790360f3d47d6b029ac33953806bdab530ba50394a6ea0.',mathematical_scope_changed=False),
        dependencies=[report['dependencies'][0],dict(id=new,revision=1,relation='encoding_equivalence')],
        evidence=[dict(path=key(REPORT),sha256=REPORT_SHA,availability='LOCAL_ONLY')],
        verification=[dict(claim_revision=1,verifier=report['verifier'],method=report['method'],
            command_or_audit=key(REPORT),timestamp=report['timestamp'],outcome='PASS',scope=report['scope'],
            artifact_hashes={key(REPORT):REPORT_SHA},shared_components=report['shared_components'])],
        artifact_availability='LOCAL_ONLY',original_report_preserved=True,ledger_changed=False,created_at=now,updated_at=now)
    path=args.out/'claim_binding.json'
    with path.open('x',encoding='utf-8',newline='\n') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(dict(path=key(path),sha256=digest(path))))
if __name__=='__main__':main()
