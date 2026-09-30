"""Freeze the ten-claim fifteenth cohort from ledger and independently audited records."""
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
I=B+'independent_review/'
def read(p): return json.loads((ROOT/p).read_bytes())
def h(p):
    with (ROOT/p).open('rb') as stream: return hashlib.file_digest(stream,'sha256').hexdigest()
def save(p,obj):
    with (ROOT/p).open('x',encoding='utf-8',newline='\n') as stream: json.dump(obj,stream,indent=2);stream.write('\n')


def main():
    now=datetime.now(timezone.utc).isoformat()
    source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    raw=(ROOT/'CLAIMS.yaml').read_bytes();ledger=yaml.safe_load(raw)
    registrations=[B+'fifteenth_'+name+'_registration/summary.json' for name in ['preparation','modular','coarse','bitlift']]
    ids=[cid for p in registrations for cid in read(p)['new_claim_ids']]
    claims=[c for c in ledger['claims'] if c['id'] in ids]
    assert len(ledger['claims'])==148 and len(claims)==len(set(ids))==10
    assert all(c['status']=='VERIFIED' and c['review_state']=='CLEAR' and c['revision']==1 for c in claims)
    artifacts={a['id']:a for a in ledger['artifacts']}
    names=[(f'connected_fixed_core_native_{i:02d}',I+f'connected_fixed_core_native_{i:02d}_v2/summary.json') for i in range(4)]
    names.append(('prism_coarse60_native_pilot',I+'prism_coarse60_native_outcome/summary.json'))
    runs=[]
    for name,audit in names:
        path=B+name+'/summary.json';r=read(path);a=read(audit)
        assert r['actual_exit_code']==0 and r['research_calls']==1 and a['status'].endswith('_PASS')
        log=(ROOT/r['receipt']['stdout']).read_text()
        assert 's UNKNOWN' in log and not re.search(r'^s (?:SATISFIABLE|UNSATISFIABLE)$',log,re.M)
        conflicts=re.findall(r'^c conflicts:\s+(\d+)\s',log,re.M);assert len(conflicts)==1
        runs.append(dict(name=name,result='UNKNOWN_CONFLICT_LIMIT',attempts=1,exit_code=0,
            summary=path,summary_sha256=h(path),audit=audit,audit_sha256=h(audit),
            observed_conflicts=int(conflicts[0]),configured_conflicts=2000000,configured_seconds=300,
            wrapper_wall_seconds=r['receipt']['wall_seconds'],incomplete_trace_bytes=r['proof_copy']['bytes'],
            incomplete_trace_sha256=r['proof_copy']['sha256'],incomplete_trace_availability='LOCAL_ONLY'))
    gp=I+'connected_core_portfolio_states/summary.json';gpu=read(gp)
    assert len(gpu['cases'])==12 and gpu['new_saved_proposal_records']==1572864
    gpurun=read(B+'connected_core_portfolio_pilot/summary.json')
    minima=[dict(core=f'connected_{i:02d}',phase_minima=[c['final_best_score'] for c in gpu['cases'] if c['case']['core_index']==i]) for i in range(4)]
    command=['wsl.exe','-d','Ubuntu-24.04','--','ps','-C','cadical','-o','pid,etime,pcpu,rss,args']
    observed=datetime.now(timezone.utc).isoformat();ps=subprocess.run(command,cwd=ROOT,capture_output=True)
    for channel,content in [('stdout',ps.stdout),('stderr',ps.stderr)]:
        with (ROOT/(B+'resume/fifteenth_process_snapshot.'+channel+'.log')).open('xb') as stream:stream.write(content)
    state='CADICAL_PROCESS_OBSERVED' if ps.returncode==0 else 'NO_CADICAL_PROCESS_OBSERVED' if ps.returncode==1 else 'UNKNOWN_OBSERVATION_ERROR'
    snapshot=B+'resume/claims_at_fifteenth_milestone.yaml'
    with (ROOT/snapshot).open('xb') as stream:stream.write(raw)
    paths={artifacts[aid]['path'] for c in claims for aid in c['evidence']}
    paths.update(registrations+[snapshot,gp,B+'connected_core_portfolio_pilot/summary.json',B+'fifteenth_artifact_packaging/catalog.json'])
    paths.update(p for r in runs for p in [r['summary'],r['audit']])
    record=dict(timestamp=now,source_commit=source,command=[sys.executable,*sys.argv],cwd=str(ROOT),
        previous_report='docs/RESEARCH_20260930_FOURTEENTH_WAVE.md',previous_checkpoint_sha256=h(B+'resume/fourteenth_milestone_checkpoint.json'),
        target_resolution='UNKNOWN',external_review=None,external_review_null_reason='No internally validated target graph or general nonexistence proof.',
        claim_population=len(ledger['claims']),verified_clear=sum(c['status']=='VERIFIED' and c['review_state']=='CLEAR' for c in ledger['claims']),
        claim_status_counts=dict(Counter(c['status'] for c in ledger['claims'])),claim_review_counts=dict(Counter(c['review_state'] for c in ledger['claims'])),new_verified_ids=ids,
        native_runs=runs,completed_native_attempts=5,native_SAT_results=0,native_UNSAT_results=0,native_UNKNOWN_results=5,
        gpu=dict(completed_phases=12,new_saved_proposal_records=gpu['new_saved_proposal_records'],distinct_initialized_chains=gpu['distinct_initialized_chains'],
            phase_chain_endpoints=gpu['phase_chain_endpoints'],chunk_best_states=gpu['chunk_best_states'],phase_final_current_states=gpu['phase_final_current_states'],
            phase_final_best_states=gpu['phase_final_best_states'],checkpoint_current_scores_checked=gpu['checkpoint_current_scores_checked'],
            checkpoint_best_scores_checked=gpu['checkpoint_best_scores_checked'],minima=minima,objective_version='TRIANGLE_FACTOR_CROSS_GRAM_SQUARED_V1',
            individual_campaign_transitions_replayed=False,producer_stage_result=gpurun['status']),
        complete99_graphs=0,independently_validated_new_target_factors=0,new_complete_unsat_traces=0,newly_closed_unrestricted_branches=0,
        coverage='Overall search coverage: UNKNOWN; no validated denominator.',
        execution=dict(observed_at=observed,command=command,exit_code=ps.returncode,state=state,
            stdout_sha256=h(B+'resume/fifteenth_process_snapshot.stdout.log'),stderr_sha256=h(B+'resume/fifteenth_process_snapshot.stderr.log'),
            scope='All five cohort native attempts completed. A later bit-normalized run, if observed, is separate.'),
        next_experiment='Complete the separate six-unit-normalized coarse60 native attempt admitted by independent normalization and object-checker gates, then independently audit its exact outcome.',
        evidence_sha256={p:h(p) for p in sorted(paths)})
    save(B+'resume/fifteenth_milestone_checkpoint.json',record)
    claimrows='\n'.join('| `'+c['id']+'` | '+c['scope']['description']+' [Evidence](../'+artifacts[c['evidence'][0]]['path']+'). |' for c in claims)
    runrows='\n'.join('| '+r['name']+' | '+r['result']+' | '+str(r['observed_conflicts'])+' | '+f"{r['wrapper_wall_seconds']:.3f}"+' |' for r in runs)
    gpurows='\n'.join('| '+r['core']+' | '+' → '.join(map(str,r['phase_minima']))+' |' for r in minima)
    report=f'''# Fifteenth resumed milestone, 2026-09-30 JST

Ten verified claims were added since the [fourteenth milestone](RESEARCH_20260930_FOURTEENTH_WAVE.md): four connected construction domains and their finite GPU/SAT checks, conditional modular results, and a distinct 60-pattern six-prism construction model. All five native attempts ended UNKNOWN. No target resolution or new exclusion was obtained.

**As of:** {now}; source commit `{source}`. [Checkpoint](../{B}resume/fifteenth_milestone_checkpoint.json), [ledger snapshot](../{snapshot}); previous report: fourteenth milestone.

**Verdict:** target resolution UNKNOWN. This repository has no independently validated 99-vertex graph or general nonexistence proof. No target resolution is under external review. [Draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3) remains unmerged. This is not a worldwide literature verdict.

**Verified changes:** all ten claims are revision 1, restricted to their exact statements.

| Claim | Exact scope and evidence |
| --- | --- |
{claimrows}

**Work completed:** deterministic selection inspected all 3,580 ordered-matching-pair representatives with chosen P=I, finding 2,806 connected cores and selecting the first qualifying core in each of the first four qualifying stages. The four selected cores are construction restrictions, not a cover of the target. Their GPU admission and actual public-checkpoint continuation passed independent finite calibration. The pilot completed 12 phases, 96 chunks and 1,572,864 proposal records across 64 continuing chains; 192 phase-chain endpoints are overlapping stages. Independent checking covered 96 chunk-best, 192 phase-final-current and 192 phase-final-best raw factors, all 1,536 current and 1,536 best checkpoint scores, and carry between checkpoints. Campaign transition deltas and acceptance trajectories were not all replayed.

Each of the four fixed-core CNFs appends exactly 24 units to the audited original variable-core encoding. All four complete clause bodies and semantic units were checked, and a separate native/raw-object checker was calibrated. Each formula has 110,904 variables and 518,184 clauses.

The alternative six-prism template uses all 90 balanced component-to-fibre patterns except the prior 30-pattern support, leaving 60 distinct patterns. Independent enumeration checks all 18 local bit domains: 136 survivors among 184,756 balanced words per domain. These 2,448 local survivors are not full factors. The joint model includes all 2,496,960 pairwise domain compatibility tests and all 1,770 Y-column caps. Its 5,238 variables and 85,698 clauses were fully independently reconstructed before native search; no complement-column pairing or target automorphism was imposed.

| Completed native attempt | Result | Observed conflicts | Wrapper seconds |
| --- | --- | ---: | ---: |
{runrows}

All five attempts had 300-second and two-million-conflict limits plus memory/file guards. Each ended at its conflict limit and received a separate execution audit including all retained partial-trace bytes. These are not complete UNSAT proofs; no decoded factor was produced. Timings on different inputs are not performance comparisons.

**Mathematical findings:** a conditional maximal-rank GF(2) lemma and a more general scalar-kernel-action lemma establish only field-valued linear residual consistency. Exact rank/action certificates for four selected cores and the known 243-vertex fixture show that the tested GF(2) sufficient premises fail in all five cases; this supplies no incompatible factor. For connected cores 01, 02 and 03, every actual integer factor would automatically admit some GF(3) solution of FD=H. Therefore this modular linear test cannot prune those factors. Symmetry, zero diagonal, binary entries and the quadratic residual equation remain unproved requirements on D.

**Coverage:** Overall search coverage: UNKNOWN; no validated denominator. No unrestricted branch or fixed core was excluded. Ledger population: 148 claims, 146 VERIFIED/CLEAR and 2 CANDIDATE/CLEAR.

**Best result:** exact saved minima under `TRIANGLE_FACTOR_CROSS_GRAM_SQUARED_V1` were:

| Chosen core | T=1 → T=0.25 → T=0 |
| --- | --- |
{gpurows}

This objective is the sum of squared integer residuals of the three cross-fibre Gram blocks on each fixed permutation domain, minimized by a heuristic using floating acceptance probabilities. Positive values are not bounds, exclusions or factors. No complete target factor was obtained.

**Problems:** all five native attempts were UNKNOWN. The initial outcome parser rejected an authentic conflict-limit annotation; its source, failed audit and corrected calibration remain preserved. A misspelled dependency ID in the original fixed-core audit is corrected by a bound append-only record. Raw GPU checkpoint/trace JSON has lossless recovery packages; native binaries and incomplete solver traces remain LOCAL_ONLY. Later component-bit normalization and identity-P completion lemmas are outside this cohort.

**Execution:** all cohort searches completed. Fresh native observation at {observed}: `{state}`. Exact logs are in the checkpoint; any later normalized attempt is separate. The user's continuation instruction remains active.

**Next experiment:** complete the separate coarse60 attempt with its first column's six bits normalized. Its normalization and complete-object gates passed independent checking after this cohort was frozen; the later experiment will receive its own outcome audit. A factor still requires residual completion and full graph validation.

**References:** [source commit](https://github.com/ikuto32/conway-99-graph/commit/{source}), [draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3), [catalog](../{B}fifteenth_artifact_packaging/catalog.json), [replay guide](REPRODUCING_20260930_FIFTEENTH_WAVE.md). Immutable publication pointers follow remote confirmation.
'''
    with (ROOT/'docs/RESEARCH_20260930_FIFTEENTH_WAVE.md').open('x',encoding='utf-8',newline='\n') as stream:stream.write(report)
    print(json.dumps(dict(claims=148,verified_clear=record['verified_clear'],native_state=state,target_resolution='UNKNOWN')))


if __name__=='__main__':main()
