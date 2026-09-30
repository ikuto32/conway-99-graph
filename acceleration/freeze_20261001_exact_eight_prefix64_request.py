"""Freeze one explicitly planned prefix64 allocation; never run it automatically."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
def need(x,s):
    if not x:raise ValueError(s)
def safe(p):
    q=(ROOT/p).resolve();need(q.is_relative_to(ROOT)and not q.relative_to(ROOT).as_posix().startswith('tools/'),'contained research path');return q
def h(p):
    with safe(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,x):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--batch-number',type=int,required=True)
    for label in ['previous-request','completed-gate','plan']:
        ap.add_argument('--'+label,required=True);ap.add_argument('--'+label+'-sha256',required=True)
    a=ap.parse_args();need(4<=a.batch_number<=11,'only the individually planned full64 continuation batches4..11')
    pins={}
    for label in ['previous_request','completed_gate','plan']:
        p=getattr(a,label);expected=getattr(a,label+'_sha256');need(h(p)==expected,'explicit input hash');pins[p]=expected
    tag=f'batch{a.batch_number:02d}';prior=f'batch{a.batch_number-1:02d}';base='acceleration/results/20261001_exact_eight_prefix64_'
    need(a.previous_request==base+prior+'_request/request.json'and a.completed_gate=='acceleration/results/20261001_independent_review/exact_eight_prefix64_'+prior+'_proofs/summary.json','exact preceding batch paths')
    need(a.plan=='acceleration/theory_20261001_exact_eight_prefix64_'+tag+'_plan.md','specific root-authored allocation plan')
    request=json.loads(safe(a.previous_request).read_bytes());gate=json.loads(safe(a.completed_gate).read_bytes())
    need(request['schema']=='EXACT_EIGHT_PREFIX64_REQUEST_V1'and gate['status']=='INDEPENDENT_EXACT_EIGHT_EXPLICIT_BATCH_LITERAL_PROOFS_PASS','request/proof schemas')
    rows=gate['case_records'];need(gate['completed_attempts']==gate['completed_proof_replays']==len(rows)==len({r['case_id']for r in rows})==64,'complete distinct64')
    need(gate['SAT_verified']==gate['UNKNOWN']==0 and gate['pending_case_ids']==[] and gate['prior_literal_overlap']['overlap_with_skipped_cases']==[],'all accepted literal outcomes')
    need(all(r['outcome']=='UNSAT_VERIFIED'and r['trace']['complete_proof']and r['replay']['accepted']and r['replay']['actual_exit_code']==0 for r in rows),'every complete proof replay')
    need(a.completed_gate not in{g['path']for g in request['completed_proof_gates']},'new proof gate')
    request['completed_proof_gates'].append(dict(path=a.completed_gate,sha256=a.completed_gate_sha256,completed_cases=64))
    total=sum(g['completed_cases']for g in request['completed_proof_gates']);need(total==60+64*(a.batch_number-1)and total+64<=792,'specific next allocation size')
    request['authorization_record_path']=a.plan;request['authorization_record_sha256']=a.plan_sha256
    request['selection_reason']=f'Explicit {tag}: first64 manifest records after removing exactly{total} independently proved literal cases. No historical or orbit exclusions added.'
    request['build_allocations']=[dict(attempt_id=f'prefix64-{tag}-part{i:02d}-build-attempt01',out=base+tag+f'_cnfs_part{i:02d}')for i in range(4)]
    request['recorded_source_commit']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    out=safe(base+tag+'_request');need(not out.exists(),'fresh request');out.mkdir()
    save(out/'request.json',request);pins[Path(__file__).relative_to(ROOT).as_posix()]=h(Path(__file__).relative_to(ROOT))
    save(out/'preparation.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=request['recorded_source_commit'],command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256=pins,request_sha256=h(out/'request.json'),prior_proved_literals=total,selection_executed=False,native_calls=0,scope='One separately planned allocation. The selector and independent prebuild audit must reconstruct every prior raw identity before any build.'))
    print(json.dumps(dict(request_path=(out/'request.json').relative_to(ROOT).as_posix(),request_sha256=h(out/'request.json'),prior_proved_literals=total)))
if __name__=='__main__':main()
