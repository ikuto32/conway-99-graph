"""Generate one wave30 milestone from the registered claims and exact saved gates."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import argparse,hashlib,json,subprocess,sys,yaml
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/';R=B+'20261001_resume/'
def need(q,m):
    if not q:raise ValueError(m)
def h(p):
    with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def save(p,x):
    with (ROOT/p).open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--ledger-sha256',required=True);args=ap.parse_args()
    lp=ROOT/'CLAIMS.yaml';need(h(lp)==args.ledger_sha256,'exact intended ledger');raw=lp.read_bytes();d=yaml.safe_load(raw)
    need(len(d['claims'])==308 and Counter(c['status']for c in d['claims'])==dict(VERIFIED=301,CANDIDATE=3,REFUTED=4),'exact308 population')
    need(all(c['review_state']=='CLEAR'for c in d['claims']),'all claims clear')
    need(d['target']['status']=='UNKNOWN' and not d['target']['supporting_claims'],'no target resolution')
    arts={a['id']:a for a in d['artifacts']};claims={c['id']:c for c in d['claims']}
    regs=[];newids=[];before=None
    for name in ('thirtieth_initial_registration','thirtieth_followup_registration'):
        p=B+'20261001_'+name+'/summary.json';r=read(p);dr=Path(p).parent
        pre=(ROOT/dr/'CLAIMS.before.yaml').read_bytes();post=(ROOT/dr/'CLAIMS.after.yaml').read_bytes()
        need(hashlib.sha256(pre).hexdigest()==r['previous_ledger_sha256'] and hashlib.sha256(post).hexdigest()==r['ledger_sha256'],'registered snapshots')
        need(before is None or before==pre,'ordered registration chain');before=post;newids+=r['new_claim_ids']
        regs.append(dict(path=p,sha256=h(ROOT/p),before_sha256=r['previous_ledger_sha256'],after_sha256=r['ledger_sha256'],new_claim_ids=r['new_claim_ids']))
    need(before==raw and len(newids)==len(set(newids))==8,'exact eight new claims')
    need(all(claims[i]['status']=='VERIFIED' and claims[i]['review_state']=='CLEAR'for i in newids),'new verified scopes')
    gates=[('20260930','exact_eight_first12_proofs'),('20260930','exact_eight_next32_proofs'),('20260930','exact_eight_sizeclass16_proofs'),('20260930','exact_eight_next64_proofs')]+[('20261001',f'exact_eight_prefix64_batch{b:02d}_proofs')for b in range(2,6)]
    batches=[];ids=[];trace_bytes=0
    for day,name in gates:
        p=B+day+'_independent_review/'+name+'/summary.json';digest=h(ROOT/p)
        aa=[a for a in d['artifacts']if a['path']==p and a['sha256']==digest]
        need(aa,'gate hash registered')
        owners=[c for c in d['claims']if any(a['id']in c['evidence']for a in aa) and c['status']=='VERIFIED' and c['review_state']=='CLEAR']
        need(owners,'gate belongs to current verified claim')
        r=read(p);caseids=[x['case_id']for x in r['case_records']]
        need(len(caseids)==len(set(caseids))==r['completed_proof_replays'] and set(caseids).isdisjoint(ids),'literal union disjoint and complete')
        need(all(x['outcome']=='UNSAT_VERIFIED' and x['trace']['complete_proof'] and x['replay']['accepted'] and x['replay']['actual_exit_code']==0 for x in r['case_records']),'complete checked proof metadata')
        ids+=caseids;nbytes=sum(x['trace']['bytes']for x in r['case_records']);trace_bytes+=nbytes
        batches.append(dict(path=p,sha256=digest,registered_claim_ids=[c['id']for c in owners],distinct_cases=len(caseids),complete_trace_bytes=nbytes))
    need(len(ids)==380,'exact380 literal union')
    now=datetime.now(timezone.utc).isoformat();snapshot=R+'claims_at_thirtieth_milestone.yaml'
    with(ROOT/snapshot).open('xb')as f:f.write(raw)
    record=dict(timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),source_sha256=h(Path(__file__)),status='RECORDED_THIRTIETH_MILESTONE',previous_report='docs/RESEARCH_20261001_TWENTYNINTH_WAVE.md',previous_published_checkpoint=R+'twentyninth_milestone_checkpoint.json',public_previous_evidence_commit='d43ab1ca6638b565d555b0765044668761de6a64',public_previous_pointer_commit='cc55ad8bd7ad3ef35d33cae35232f9cc8eb264e5',claim_population=308,claim_status_counts=dict(Counter(c['status']for c in d['claims'])),review_counts=dict(Counter(c['review_state']for c in d['claims'])),ledger_snapshot=snapshot,ledger_snapshot_sha256=h(ROOT/snapshot),registration_chain=regs,new_verified_ids=newids,completed_literal_batches=batches,distinct_proved_literal_cases=380,frozen_literal_population=792,remaining_literal_cases=412,new_literal_exclusions=192,complete_trace_bytes=trace_bytes,new_complete_trace_bytes=sum(x['complete_trace_bytes']for x in batches[-3:]),core_footprint_additional_exclusions=0,literature_identity_additional_exclusions=0,fresh_mathematical_replays=0,scope='Eight scoped additions since the published300-claim wave29 cutoff. Metadata aggregation of registered independent gates only.',target_resolution='UNKNOWN',external_target_review='No target-resolution artifact exists in this repository.',overall_search_coverage='UNKNOWN; no validated denominator.',best_result='The previously checked fixed-support lower bound of eight unbalanced groups is unchanged.',execution=dict(batch03='Completed and independently checked.',batch04='Completed after explicit checkpoint continuation; original deadline stops and four repeated producer calls preserved.',batch05='Completed and independently checked.',batch06_and_later='Outside this frozen milestone.',live_process_state='UNKNOWN; this recorder does not inspect running processes.'),problems=['Batch04 original four120-second builds stopped with56 accepted checkpoint records;60 producer calls occurred, four additional outputs were not checkpoint-accepted. Explicit continuation made8 new calls, giving64 accepted formulas after68 actual calls.','The core producer v1 mapping failed after proof extraction; v2 mapping and separate complete root audit preserved that history.','The selected literature producer v1 required nonexistent positive N3 controls in the243 fixture; v2 records vacuity and uses an explicitly incomplete synthetic local fixture.','Registrar and wave29 pointer source-review/correction histories remain immutable; no mathematical conclusion was inferred from a failed engineering run.'],limitations=['No target automorphism assumption.','No blanket sixfold fibre-image expansion or whole-eight/fixed-support/unrestricted exclusion.','The Z82 identity adds no restriction to the inspected archived row families.','No performance comparison or new heuristic objective is claimed.'],next_experiment='Continue the next64 literal allocation through its independent gates while testing a concrete three-center compatibility condition beyond the archived two-center model.')
    out=R+'thirtieth_milestone_checkpoint.json';save(out,record)
    need(lp.read_bytes()==raw,'ledger unchanged by recorder')
    print(json.dumps(dict(path=out,sha256=h(ROOT/out),claims=308,distinct_literal_cases=380,remaining_literal_cases=412,complete_trace_bytes=trace_bytes)))
if __name__=='__main__':main()
