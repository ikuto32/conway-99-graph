"""Record the ledger-derived initial wave30 state without claiming a completed later batch."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import hashlib,json,subprocess,sys,yaml
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/'
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ledger=ROOT/'CLAIMS.yaml';assert h(ledger)=='0fd27c9fe019247eded6509f4c228141ce350e3cf387d98314742c89ecc1d56d'
    data=yaml.safe_load(ledger.read_bytes());claims=data['claims'];counts=Counter(c['status']for c in claims)
    assert len(claims)==303 and counts==dict(VERIFIED=296,CANDIDATE=3,REFUTED=4) and all(c['review_state']=='CLEAR'for c in claims)
    registration=ROOT/(B+'20261001_thirtieth_initial_registration/summary.json');reg=json.loads(registration.read_bytes())
    assert reg['ledger_sha256']==h(ledger)and reg['claim_population']==303
    gates=[('20260930','exact_eight_first12_proofs'),('20260930','exact_eight_next32_proofs'),
        ('20260930','exact_eight_sizeclass16_proofs'),('20260930','exact_eight_next64_proofs'),
        ('20261001','exact_eight_prefix64_batch02_proofs'),('20261001','exact_eight_prefix64_batch03_proofs')]
    batch=[];allids=[];trace_bytes=0
    for day,name in gates:
        p=ROOT/(B+day+'_independent_review/'+name+'/summary.json');r=json.loads(p.read_bytes());ids=[c['case_id']for c in r['case_records']]
        assert len(ids)==len(set(ids))==r['completed_proof_replays']and set(ids).isdisjoint(allids)
        assert all(c['outcome']=='UNSAT_VERIFIED'and c['trace']['complete_proof']and c['replay']['accepted']for c in r['case_records'])
        allids+=ids;total=sum(c['trace']['bytes']for c in r['case_records']);trace_bytes+=total
        batch.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=h(p),distinct_cases=len(ids),complete_trace_bytes=total))
    assert len(allids)==252
    now=datetime.now(timezone.utc).isoformat();out=ROOT/(B+'20261001_resume/thirtieth_initial_checkpoint.json')
    record=dict(timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv],cwd=str(ROOT),source_sha256=h(Path(__file__)),status='RECORDED_INITIAL_WAVE30_STATE',
        previous_published_checkpoint=B+'20261001_resume/twentyninth_milestone_checkpoint.json',
        public_evidence_commit='d43ab1ca6638b565d555b0765044668761de6a64',public_pointer_commit='cc55ad8bd7ad3ef35d33cae35232f9cc8eb264e5',
        ledger_sha256=h(ledger),claim_population=len(claims),status_counts=dict(counts),review_counts=dict(Counter(c['review_state']for c in claims)),
        registration=dict(path=registration.relative_to(ROOT).as_posix(),sha256=h(registration)),new_claim_ids=reg['new_claim_ids'],
        completed_literal_batches=batch,distinct_proved_literal_cases=252,frozen_literal_population=792,remaining_literal_cases=540,complete_trace_bytes=trace_bytes,
        fresh_proof_replays_in_this_recorder=0,source_of_math_approval='Previously completed independent reports bound by the ledger; this recorder only checks metadata identities/counts.',
        core_footprint_additional_exclusions=0,target_resolution='UNKNOWN',external_target_review='No target-resolution artifact exists in this repository.',
        overall_search_coverage='UNKNOWN; no validated denominator.',best_result='The prior fixed-support lower bound of eight unbalanced groups is unchanged.',
        execution=dict(batch03='Completed and independently checked.',core_footprint='Completed and independently checked.',
            batch04='Not counted as excluded. Original builds stopped; continuation records await complete64 scientific checking and native/proof gates.',
            batch05='Contingent only; requires complete batch04 proof gate.',live_process_state='UNKNOWN; this metadata recorder does not observe live processes.'),
        limitations=['No blanket sixfold fibre-image expansion or general fixed-support exclusion.','Publication checkpoint remains wave29; these three new claim evidence pairs are currently LOCAL_ONLY.'],
        next_experiment='Complete batch04 checkpoint continuation, independently check all64 formulas and objects, then run the bounded native batch and replay each complete proof.')
    with out.open('x',encoding='utf8',newline='\n')as f:json.dump(record,f,indent=2);f.write('\n')
    print(json.dumps(dict(path=out.relative_to(ROOT).as_posix(),sha256=h(out),claims=303,distinct_literal_cases=252,remaining_literal_cases=540,complete_trace_bytes=trace_bytes)))
if __name__=='__main__':main()
