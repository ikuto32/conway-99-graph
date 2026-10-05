"""Freeze four independently checked claims and two completed normalized attempts."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
import yaml

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'
def read(p):return json.loads((ROOT/p).read_bytes())
def h(p):
    with (ROOT/p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,x):
    with (ROOT/p).open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')

def main():
    now=datetime.now(timezone.utc).isoformat();source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    raw=(ROOT/'CLAIMS.yaml').read_bytes();ledger=yaml.safe_load(raw)
    registration=B+'thirteenth_preparation_registration/summary.json';ids=read(registration)['new_claim_ids']
    claims=[c for c in ledger['claims'] if c['id'] in ids]
    assert len(claims)==4 and all(c['status']=='VERIFIED' and c['review_state']=='CLEAR' for c in claims)
    artifacts={a['id']:a for a in ledger['artifacts']};runs=[]
    for name,code,outcome in [('variable_core_m1_orbits',0,'UNKNOWN_CONFLICT_LIMIT'),('prism_first_choice',124,'UNKNOWN_TIMEOUT')]:
        path=B+name+'_native_pilot/summary.json';r=read(path);assert r['actual_exit_code']==code and r['research_calls']==1
        text=(ROOT/r['receipt']['stdout']).read_text();conflicts=re.findall(r'^c conflicts:\s+(\d+)\s',text,re.M);assert len(conflicts)==1
        audit=B+'independent_review/'+name+'_unknown/summary.json'
        runs.append(dict(name=name,result=outcome,attempts=1,exit_code=code,summary=path,summary_sha256=h(path),audit=audit,audit_sha256=h(audit),
            observed_conflicts=int(conflicts[0]),configured_conflicts=5000000,configured_seconds=900,wrapper_wall_seconds=r['receipt']['wall_seconds'],
            incomplete_trace_bytes=r['proof_copy']['bytes'],incomplete_trace_sha256=r['proof_copy']['sha256']))
    command=['wsl.exe','-d','Ubuntu-24.04','--','ps','-C','cadical','-o','pid,etime,pcpu,rss,args']
    observed=datetime.now(timezone.utc).isoformat();ps=subprocess.run(command,cwd=ROOT,capture_output=True)
    for channel,content in [('stdout',ps.stdout),('stderr',ps.stderr)]:
        with (ROOT/(B+'resume/thirteenth_process_snapshot.'+channel+'.log')).open('xb') as f:f.write(content)
    state='CADICAL_PROCESS_OBSERVED' if ps.returncode==0 else 'NO_CADICAL_PROCESS_OBSERVED' if ps.returncode==1 else 'UNKNOWN_OBSERVATION_ERROR'
    snapshot=B+'resume/claims_at_thirteenth_milestone.yaml'
    with (ROOT/snapshot).open('xb') as f:f.write(raw)
    paths={artifacts[aid]['path'] for c in claims for aid in c['evidence']}
    paths.update([registration,snapshot,B+'thirteenth_artifact_packaging/catalog.json'])
    paths.update(p for r in runs for p in (r['summary'],r['audit']))
    record=dict(timestamp=now,source_commit=source,command=[sys.executable,*sys.argv],cwd=str(ROOT),
        previous_report='docs/RESEARCH_20260930_TWELFTH_WAVE.md',previous_checkpoint_sha256=h(B+'resume/twelfth_milestone_checkpoint.json'),
        target_resolution='UNKNOWN',external_review=None,external_review_null_reason='No validated target graph or general nonexistence proof in this repository.',
        claim_population=len(ledger['claims']),verified_clear=sum(c['status']=='VERIFIED' and c['review_state']=='CLEAR' for c in ledger['claims']),
        claim_status_counts=dict(Counter(c['status'] for c in ledger['claims'])),claim_review_counts=dict(Counter(c['review_state'] for c in ledger['claims'])),new_verified_ids=ids,
        native_runs=runs,completed_native_attempts=2,native_SAT_results=0,native_UNSAT_results=0,native_UNKNOWN_results=2,
        independently_validated_new_target_factors=0,complete99_graphs=0,new_complete_unsat_traces=0,newly_closed_unrestricted_branches=0,
        positive_control=dict(vertices=243,degree=22,lambda_parameter=1,mu_parameter=2,target99_candidate=False),
        coverage='Overall search coverage: UNKNOWN; no validated denominator.',
        execution=dict(observed_at=observed,command=command,exit_code=ps.returncode,state=state,
            stdout_sha256=h(B+'resume/thirteenth_process_snapshot.stdout.log'),stderr_sha256=h(B+'resume/thirteenth_process_snapshot.stderr.log'),
            scope='Both named normalized pilots completed. An observed ordered-pair run is a separate later experiment.'),
        next_experiment='Run the independently gated 3580 ordered-matching-pair normalization with P arbitrary; separately evaluate exact-score permutation construction attempts.',
        evidence_sha256={p:h(p) for p in sorted(paths)})
    save(B+'resume/thirteenth_milestone_checkpoint.json',record)
    rows='\n'.join('| `'+c['id']+'` | '+c['scope']['description']+' [Audit](../'+artifacts[c['evidence'][0]]['path']+'). |' for c in claims)
    runrows='\n'.join('| '+r['name']+' | '+r['result']+' | '+str(r['observed_conflicts'])+' | '+f"{r['wrapper_wall_seconds']:.3f}"+' |' for r in runs)
    report=f'''# Thirteenth resumed milestone, 2026-09-30 JST

Four verified claims were added since the [twelfth milestone](RESEARCH_20260930_TWELFTH_WAVE.md): a nonempty independent validation fixture, a necessary residual screen, and two coordinate relabelling reductions. Both normalized SAT attempts ended UNKNOWN.

**As of:** {now}; source commit `{source}`. [Checkpoint](../{B}resume/thirteenth_milestone_checkpoint.json), [ledger snapshot](../{snapshot}); previous report: twelfth milestone.

**Verdict:** target resolution UNKNOWN. This repository has no independently validated target graph or general nonexistence proof. No target resolution is under external review. [Draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3) remains unmerged. This is not a worldwide literature verdict.

**Verified changes:** all four claims are revision 1.

| Claim | Exact scope and evidence |
| --- | --- |
{rows}

**Work completed:** the 243-vertex raw graph passed all 59,049 full adjacency-square entries, its triangle-factor/residual block equations and seven corruption controls. It is a different-parameter validation fixture. The dynamic screen passed independent exact edge/quota checks, including this nonempty fixture; no research factor was supplied or excluded.

The six-prism reduction checked all 384 relabellings, 96 first-choice transports, 207,360 equation images and 147,456 compositions. The arbitrary-core reduction checked all 10,395 M1 transports and 623,700 C0 column images to eleven representatives. These are distinct finite populations, not counts of excluded graphs. M2 and P stay arbitrary in the latter model. Neither reduction assumes an automorphism of a target graph. Full native-assignment and raw-factor checking paths were separately calibrated.

| Completed native attempt | Result | Observed conflicts | Wrapper seconds |
| --- | --- | ---: | ---: |
{runrows}

Each had one attempt with 900 seconds and five million configured conflicts, plus memory/file guards. Independent engineering audits authenticated exact inputs, logs, receipts and all retained incomplete trace bytes, with six altered-outcome controls per attempt. No trace is a complete checked UNSAT proof. Different formulas and stopping conditions do not establish a performance comparison.

**Coverage:** Overall search coverage: UNKNOWN; no validated denominator. No unrestricted branch or fixed-core family was excluded. Ledger population: {len(ledger['claims'])} claims, {record['verified_clear']} VERIFIED/CLEAR and two CANDIDATE/CLEAR.

**Best result:** independently checked relabelling reductions preserve their stated model coverage, and nonempty controls strengthen residual validation. No complete target factor, target graph or target-wide mathematical bound was obtained in this cohort.

**Problems:** both searches are UNKNOWN. Preserved failures include the initial fixture syntax error, the unavailable-psutil preflight import, and two publication-catalog bookkeeping omissions. Corrected runs and explicit control exceptions are recorded without overwriting failed sources. The first-choice raw formula has public gzip recovery; the two incomplete traces remain LOCAL_ONLY. The GPU and full ordered-pair work belong to later cohorts and are excluded from these claim totals and run counts.

**Execution:** both named attempts completed. Fresh observation at {observed}: `{state}`. Exact command and process logs are in the checkpoint; any observed ordered-pair attempt is separate. The user's continuation instruction remains active.

**Next experiment:** test the independently gated 3,580 ordered-matching-pair normalization while leaving P arbitrary, and continue independently checked permutation construction attempts. A factor would still require residual completion and full exact graph verification.

**References:** [source commit](https://github.com/ikuto32/conway-99-graph/commit/{source}), [draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3), [catalog](../{B}thirteenth_artifact_packaging/catalog.json), [replay guide](REPRODUCING_20260930_THIRTEENTH_WAVE.md). Immutable publication pointers follow remote confirmation.
'''
    with (ROOT/'docs/RESEARCH_20260930_THIRTEENTH_WAVE.md').open('x',encoding='utf-8',newline='\n') as f:f.write(report)
    print(json.dumps(dict(claims=len(ledger['claims']),verified_clear=record['verified_clear'],native_state=state,target_resolution='UNKNOWN')))

if __name__=='__main__':main()
