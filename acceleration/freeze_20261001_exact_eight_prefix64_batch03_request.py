"""Freeze one explicit next64 request after authenticating batch02 completion."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
OLD='acceleration/results/20261001_exact_eight_prefix64_batch02_request/request.json'
OLD_SHA='c747cb087ba25ccfe89e464e9d200f49f1a16f455c6d0e47dc6a5173e3de7d78'
GATE='acceleration/results/20261001_independent_review/exact_eight_prefix64_batch02_proofs/summary.json'
PLAN='acceleration/theory_20261001_exact_eight_prefix64_batch03_plan.md'
OUT='acceleration/results/20261001_exact_eight_prefix64_batch03_request'
def h(path):
    with(ROOT/path).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(path,obj):
    with path.open('x',encoding='utf8',newline='\n')as f:json.dump(obj,f,indent=2);f.write('\n')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--completed-gate-sha256',required=True);a=ap.parse_args()
    assert h(OLD)==OLD_SHA and h(GATE)==a.completed_gate_sha256
    request=json.loads((ROOT/OLD).read_bytes());q=json.loads((ROOT/GATE).read_bytes())
    assert q['status']=='INDEPENDENT_EXACT_EIGHT_EXPLICIT_BATCH_LITERAL_PROOFS_PASS'
    assert q['completed_attempts']==q['completed_proof_replays']==len(q['case_records'])==64 and q['SAT_verified']==q['UNKNOWN']==0 and q['pending_case_ids']==[]
    assert all(r['outcome']=='UNSAT_VERIFIED'and r['trace']['complete_proof']and r['replay']['accepted']and r['replay']['actual_exit_code']==0 for r in q['case_records'])
    assert q['prior_literal_overlap']['overlap_with_skipped_cases']==[]
    request['completed_proof_gates'].append(dict(path=GATE,sha256=a.completed_gate_sha256,completed_cases=64))
    assert sum(g['completed_cases']for g in request['completed_proof_gates'])==188
    request['authorization_record_path']=PLAN;request['authorization_record_sha256']=h(PLAN)
    request['selection_reason']='Third64-case manifest prefix after removing exactly188 independently proved literal cases in five disjoint batches; no historical or orbit exclusions added.'
    request['build_allocations']=[dict(attempt_id=f'prefix64-batch03-part{i:02d}-build-attempt01',out=f'acceleration/results/20261001_exact_eight_prefix64_batch03_cnfs_part{i:02d}')for i in range(4)]
    request['recorded_source_commit']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    out=ROOT/OUT;out.mkdir(exist_ok=False);save(out/'request.json',request)
    save(out/'preparation.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=request['recorded_source_commit'],command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256={OLD:OLD_SHA,GATE:a.completed_gate_sha256,PLAN:h(PLAN),Path(__file__).relative_to(ROOT).as_posix():h(Path(__file__).relative_to(ROOT))},request_sha256=h(OUT+'/request.json'),selection_executed=False,native_calls=0,scope='One explicit bounded allocation. Selector and independent prebuild checker must authenticate all raw identities before build.'))
    print(json.dumps(dict(request_sha256=h(OUT+'/request.json'),plan_sha256=h(PLAN))))
if __name__=='__main__':main()
