"""Freeze ledger-derived milestone and completed native outcomes; no promotion."""
from collections import Counter
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import json
import re
import subprocess
import sys
import yaml

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'
OUT=ROOT/(B+'resume')
def digest(path):
    h=sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1<<20),b''):h.update(block)
    return h.hexdigest()
def read(path):return json.loads((ROOT/path).read_bytes())
def save(path,value):
    with Path(path).open('x',encoding='utf-8',newline='\n') as f:json.dump(value,f,indent=2);f.write('\n')
def main():
    now=datetime.now(timezone.utc).isoformat();source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    raw=(ROOT/'CLAIMS.yaml').read_bytes();ledger=yaml.safe_load(raw)
    registration=read(B+'sixth_registration/summary.json');ids=registration['new_claim_ids']
    claims=[c for c in ledger['claims'] if c['id'] in ids];assert len(claims)==7
    snapshot=OUT/'claims_at_sixth_milestone.yaml'
    with snapshot.open('xb') as f:f.write(raw)
    process_command=['wsl.exe','-d','Ubuntu-24.04','--','ps','-C','cadical','-o','pid,etime,pcpu,rss,args']
    process=subprocess.run(process_command,capture_output=True)
    assert process.returncode==1 and b'cadical --' not in process.stdout, 'unexpected live solver; do not record stopped'
    (OUT/'sixth_native_process_snapshot.stdout.log').write_bytes(process.stdout)
    (OUT/'sixth_native_process_snapshot.stderr.log').write_bytes(process.stderr)
    wave=read(B+'strengthened_four_branch_native_pilot/summary.json')
    assert wave['attempted_solver_calls']==4 and len(wave['branches'])==4
    results=[];partials=[]
    for row in wave['branches']:
        folder=ROOT/(B+'strengthened_four_branch_native_pilot')/row['branch']
        receipt=row['native_receipt'];assert receipt['actual_exit_code']==124 and not receipt['outer_windows_guard_expired']
        assert not row['raw_sat_status'] and not row['independently_verified_target_resolution']
        log=(folder/'solver.stdout.log').read_text();assert '\ns SATISFIABLE\n' not in log and '\ns UNSATISFIABLE\n' not in log
        conflicts=int(re.search(r'c conflicts:\s+(\d+)',log).group(1))
        results.append(dict(branch=row['branch'],result='UNKNOWN_TIMEOUT',actual_exit_code=124,wrapped_seconds=receipt['wall_seconds'],conflicts=conflicts,receipt=(folder/'solver.receipt.json').relative_to(ROOT).as_posix(),stdout_sha256=digest(folder/'solver.stdout.log')))
        proof=folder/'proof.drat'
        partials.append(dict(path=proof.relative_to(ROOT).as_posix(),sha256=digest(proof),bytes=proof.stat().st_size,availability='LOCAL_ONLY',retrieval='Retained at the stated workspace path and at the exact copied ext4 path in the run transfer receipt.',unavailable_reason='Incomplete timeout trace, not needed for any mathematical proof claim; large raw bytes are not published.',is_unsat_certificate=False))
    oldproof=ROOT/(B+'unrestricted_native_pilot/main/proof.drat')
    partials.append(dict(path=oldproof.relative_to(ROOT).as_posix(),sha256=digest(oldproof),bytes=oldproof.stat().st_size,availability='LOCAL_ONLY',retrieval='Retained at the stated workspace path.',unavailable_reason='Incomplete timeout trace; not a mathematical certificate and not published.',is_unsat_certificate=False))
    catalog=OUT/'sixth_native_partial_trace_catalog.json';save(catalog,dict(timestamp=now,scope='Five completed native timeout attempts, one unbranched and four strengthened branch instances; no complete proof.',entries=partials))
    artifacts={a['id']:a for a in ledger['artifacts']};paths={artifacts[aid]['path'] for c in claims for aid in c['evidence']}
    paths.update([B+'sixth_registration/summary.json',B+'editorial_migration_applied/summary.json',B+'independent_review/editorial_migration_applied/summary.json',B+'strengthened_four_branch_native_pilot/manifest.json',B+'strengthened_four_branch_native_pilot/summary.json',B+'unrestricted_native_pilot/manifest.json',B+'unrestricted_native_pilot/summary.json',B+'sixth_artifact_packaging/catalog.json',snapshot.relative_to(ROOT).as_posix(),catalog.relative_to(ROOT).as_posix()])
    record=dict(timestamp=now,source_commit=source,command=[sys.executable,*sys.argv],cwd=str(ROOT),previous_report='docs/RESEARCH_20260930_FIFTH_WAVE.md',previous_checkpoint_sha256=digest(OUT/'fifth_milestone_checkpoint.json'),target_resolution='UNKNOWN',external_review=None,external_review_reason='No internally validated target graph or unrestricted nonexistence proof exists in this repository.',claim_population=len(ledger['claims']),claim_status_counts=dict(Counter(c['status'] for c in ledger['claims'])),claim_review_counts=dict(Counter(c['review_state'] for c in ledger['claims'])),verified_clear=sum(c['status']=='VERIFIED' and c['review_state']=='CLEAR' for c in ledger['claims']),new_verified_ids=ids,editorial_changes=dict(claims_revised=19,wording_clarifications=17,separate_dependent_impact_reviews=2,new_mathematical_claims=0),branch_wave=dict(selected_instances=4,attempted_evaluations=4,completed_evaluations=4,unknown_timeouts=4,sat_candidates=0,complete_unsat_certificates=0,independently_verified_target_outcomes=0,results=results),unbranched_native_pilot=dict(attempted_evaluations=1,completed_evaluations=1,result='UNKNOWN_TIMEOUT',complete_unsat_certificates=0,sat_candidates=0),coverage='Overall search coverage: UNKNOWN; no validated denominator.',execution=dict(solver_state='NO_CADICAL_PROCESS_OBSERVED',observed_at=now,command=process_command,exit_code=process.returncode,stdout_sha256=digest(OUT/'sixth_native_process_snapshot.stdout.log'),stderr_sha256=digest(OUT/'sixth_native_process_snapshot.stderr.log'),ongoing_work='Separate bounded structural candidate derivation and triangle-factor modular falsification; not a claim of an active solver process.'),next_experiment='Independently reconstruct and test archived fixed triangle-factor row images over finite fields for exact left-kernel contradictions; in parallel test compatibility of two complete quota stars. Neither assumes a target automorphism.',evidence_sha256={p:digest(ROOT/p) for p in sorted(paths)})
    save(OUT/'sixth_milestone_checkpoint.json',record)
    rows='\n'.join('| `'+c['id']+'` | '+c['scope']['description']+' [Audit](../'+artifacts[c['evidence'][0]]['path']+'). |' for c in claims)
    report=f'''# Sixth resumed milestone, 2026-09-30 JST

Seven independently checked records were added since the [fifth milestone](RESEARCH_20260930_FIFTH_WAVE.md): six mathematical, encoding, or scoped empirical results and one registry engineering result. A separate exact editorial migration revised19 existing claims without changing their mathematics. The unrestricted native pilot and all four strengthened branch attempts completed UNKNOWN; none excludes a branch.

**As of:** {now}; source commit `{source}`. [Checkpoint](../{B}resume/sixth_milestone_checkpoint.json), [ledger snapshot](../{B}resume/claims_at_sixth_milestone.yaml). Previous report: fifth milestone; previous public evidence milestone: fourth.

**Verdict:** target resolution UNKNOWN. This repository has no independently validated target graph or unrestricted nonexistence proof and no candidate resolution under external review. Draft [PR3](https://github.com/ikuto32/conway-99-graph/pull/3) remains unmerged.

**Verified changes:** all seven new records are revision1.

| Claim | Exact scope and evidence |
| --- | --- |
{rows}

The finite map census checks all18,432 proposed signed-pair maps of one fixed family: only identity preserves it, yielding zero additional unique clauses. The22 exact modular minors provide an alternative obstruction for11 already Gram-excluded local59 graphs, not11 newly excluded graphs. Full local ranks from the producer were not promoted.

The four-branch cover uses proved relabeling of arbitrary targets, not a target automorphism. All4,662 added units are consequences of the base CNF. Each strengthened branch has1,186,500 variables and4,141,120 clauses; its complete body and suffix bytes passed independent checks. Encoding/coverage verification does not decide satisfiability.

**Work completed:** four selected branch instances, four attempted and four completed native evaluations, four UNKNOWN timeouts, zero SAT candidates and zero complete UNSAT certificates. Separately, one unbranched native evaluation timed out. The conditional eight-family pilot in the fifth checkpoint is a different earlier experiment. Partial DRAT traces are retained locally and explicitly are not certificates. Exact commands, limits, conflicts, versions and hashes are in the receipts and [trace catalog](../{B}resume/sixth_native_partial_trace_catalog.json).

**Claim migration:** seventeen ambiguous phrases now explicitly say no nontrivial target automorphism is assumed. Two dependent exclusions received separate exact impact reviews. All79 original verification records and370 original artifacts were preserved; the independent actual-transition check inspected99 dependency edges and18 changed revision pins. This added no mathematical result. Ledger population: {len(ledger['claims'])} records, {record['verified_clear']} VERIFIED/CLEAR and2 CANDIDATE/CLEAR.

**Coverage:** Overall search coverage: UNKNOWN; no validated denominator. Four canonical branches can overlap under different labelings and are not equal graph populations or work units. No branch was closed by these timed runs.

**Best result:** an independently verified unrestricted satisfiability equivalence, now expressed as four exact strengthened instances. There is no new numerical mathematical bound or target witness.

**Problems:** the first registry migration checker accepted an unrelated limitations edit in standalone mode. Root vetoed it before ledger application; original sources and the failing audit survive. The corrected checker passed ten independently authored adversarial controls and56 saved suite tests, followed by a separate actual-ledger comparison. Schema/CI success is bookkeeping, not mathematical verification. The old equality checker metadata-tag failure and original candidate wording corrections remain preserved. Large partial traces and native binaries remain LOCAL_ONLY with explicit reasons; exact mathematical inputs recover from public-ready parts and recipes.

**Execution:** all five stated native attempts have ended; a fresh process observation at the checkpoint found no CaDiCaL process. This static report does not imply later searches continue running. Structural derivation and cheap exact tests are separate ongoing work. The prior stop remains superseded by the user's explicit resume.

**Next experiment:** reconstruct the archived fixed triangle-factor row-incidence systems and test exact finite-field image membership for a short obstruction; also test joint compatibility of two complete quota stars. A newly proposed single-star redundancy theorem is pending independent review and is not included in these verified totals.

**References:** [source base](https://github.com/ikuto32/conway-99-graph/commit/{source}), [draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3), [artifact recovery catalog](../{B}sixth_artifact_packaging/catalog.json), [actual migration audit](../{B}independent_review/editorial_migration_applied/summary.json), [reproduction guide](REPRODUCING_20260930_SIXTH_WAVE.md). PUBLIC labels are updated only after exact immutable publication is confirmed.
'''
    with (ROOT/'docs/RESEARCH_20260930_SIXTH_WAVE.md').open('x',encoding='utf-8',newline='\n') as f:f.write(report)
    print(json.dumps(dict(claim_population=len(ledger['claims']),verified_clear=record['verified_clear'],branch_timeouts=4,target_resolution='UNKNOWN',timestamp=now)))
if __name__=='__main__':main()
