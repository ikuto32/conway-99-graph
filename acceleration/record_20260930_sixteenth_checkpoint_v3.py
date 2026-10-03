"""Freeze the registered sixteenth cohort without promoting the later cyclic search."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import yaml

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'
I=B+'independent_review/'


def h(p):
    with (ROOT/p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def save(p,o):
    with(ROOT/p).open('x',encoding='utf-8',newline='\n')as f:json.dump(o,f,indent=2);f.write('\n')


def main():
    now=datetime.now(timezone.utc).isoformat();source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    raw=(ROOT/'CLAIMS.yaml').read_bytes();ledger=yaml.safe_load(raw)
    names=['preparation','cyclic','contraction','hadamard','farkas','prism_lp_order','compressed']
    registrations=[B+'sixteenth_'+name+'_registration/summary.json'for name in names]
    receipts=[read(p)for p in registrations];ids=[cid for r in receipts for cid in r['new_claim_ids']]
    claims=[c for cid in ids for c in ledger['claims']if c['id']==cid];artifacts={a['id']:a for a in ledger['artifacts']}
    assert len(ledger['claims'])==165 and len(set(ids))==len(ids)==len(claims)==17
    assert all(c['status']=='VERIFIED'and c['review_state']=='CLEAR'for c in claims)
    revised=[c['id']for c in claims if c['revision']!=1]
    assert revised==['C-FIXED-HADAMARD-CONNECTED01-SUPPORT-EXCLUSION']
    assert next(c for c in claims if c['id']==revised[0])['revision']==2
    assert (ROOT/(B+'sixteenth_compressed_registration/CLAIMS.after.yaml')).read_bytes()==raw
    native=read(B+'prism_coarse60_bitflip_native_pilot/summary.json')
    audit=read(I+'prism_coarse60_bitflip_native_outcome/summary.json')
    assert native['actual_exit_code']==0 and native['research_calls']==1
    assert audit['outcome']['recorded_outcome']=='UNKNOWN_NATIVE_CONFLICT_CAP'and audit['actual_attempts']==1
    assert audit['outcome']['observed_final_conflicts']==2000001
    assert audit['checked_UNSAT_proofs']==audit['checked_SAT_objects']==0
    farkas=read(I+'hadamard_support_farkas/summary.json');assert farkas['excluded_fixed_supports']==3 and farkas['excluded_cores']==0
    assert [r['core']for r in farkas['cases']]==['connected_01','connected_02','connected_03']
    uniform=read(I+'hadamard_six_prism_uniform_lp/summary.json');ordering=read(I+'hadamard_six_prism_column_order/summary.json')
    assert uniform['status'].endswith('_PASS')and ordering['status'].endswith('_PASS')
    lpfirst=read(B+'hadamard_support_lp/summary.json');lprest=read(B+'hadamard_support_remaining_lp/summary.json')
    assert lpfirst['research_calls']==1 and lprest['attempted_cases']==lprest['completed_cases']==3
    lpstatuses=[lpfirst['model_status']]+[r['model_status']for r in lprest['records']]
    assert Counter(lpstatuses)=={'HighsModelStatus.kInfeasible':3,'HighsModelStatus.kOptimal':1}
    arc=read(I+'prism_coarse60_arc_v2/summary.json');cover=read(I+'prism_coarse60_triangle_cover/summary.json')
    assert arc['counts']['conditioned_values']==2040 and arc['counts']['AC_removed_values']==0
    assert cover['counts']['triples']==34220 and cover['counts']['Gram_mismatches']==900
    catalog_path=B+'sixteenth_artifact_packaging/catalog.json';packaging=read(B+'sixteenth_artifact_packaging/summary.json')
    assert packaging['status'].endswith('_PASS')
    evidence={artifacts[aid]['path']for c in claims for aid in c['evidence']}
    evidence.update(registrations+[catalog_path,B+'sixteenth_artifact_packaging/summary.json',
        B+'prism_coarse60_bitflip_native_pilot/summary.json',I+'prism_coarse60_bitflip_native_outcome/summary.json',
        I+'hadamard_support_farkas/summary.json',I+'hadamard_six_prism_uniform_lp/summary.json',I+'hadamard_six_prism_column_order/summary.json',
        B+'hadamard_support_lp/summary.json',B+'hadamard_support_remaining_lp/summary.json',I+'prism_coarse60_arc_v2/summary.json',I+'prism_coarse60_triangle_cover/summary.json'])
    pins={p:h(p)for p in sorted(evidence)}
    snapshot=B+'resume/claims_at_sixteenth_milestone.yaml'
    outputs=[snapshot,B+'resume/sixteenth_milestone_checkpoint.json',B+'resume/sixteenth_process_snapshot.stdout.log',
        B+'resume/sixteenth_process_snapshot.stderr.log','docs/RESEARCH_20260930_SIXTEENTH_WAVE.md']
    assert all(not(ROOT/p).exists()for p in outputs)
    cmd=['wsl.exe','-d','Ubuntu-24.04','--','ps','-C','cadical','-o','pid,etime,pcpu,rss,args']
    observed=datetime.now(timezone.utc).isoformat();process=subprocess.run(cmd,cwd=ROOT,capture_output=True)
    state='CADICAL_PROCESS_OBSERVED'if process.returncode==0 else'NO_CADICAL_PROCESS_OBSERVED'if process.returncode==1 else'UNKNOWN_OBSERVATION_ERROR'
    for suffix,content in [('stdout',process.stdout),('stderr',process.stderr)]:
        with(ROOT/(B+'resume/sixteenth_process_snapshot.'+suffix+'.log')).open('xb')as f:f.write(content)
    with(ROOT/snapshot).open('xb')as f:f.write(raw)
    record=dict(timestamp=now,source_commit=source,command=[sys.executable,*sys.argv],cwd=str(ROOT),
        previous_report='docs/RESEARCH_20260930_FIFTEENTH_WAVE_CORRECTED.md',previous_checkpoint_sha256=h(B+'resume/fifteenth_milestone_checkpoint.json'),
        target_resolution='UNKNOWN',external_review=None,external_review_null_reason='No internally validated target graph or general nonexistence proof.',
        claim_population=165,verified_clear=163,candidate_clear=2,claim_status_counts=dict(Counter(c['status']for c in ledger['claims'])),
        claim_review_counts=dict(Counter(c['review_state']for c in ledger['claims'])),new_verified_ids=ids,
        evidence_only_revision_changes=[dict(id=revised[0],from_revision=1,to_revision=2)],
        native=dict(completed_attempts=1,SAT=0,UNSAT=0,UNKNOWN=1,outcome=audit['outcome'],trace=audit['trace'],
            scope='Bit-normalized fixed coarse60 template; no exclusion.'),
        propagation=dict(initial_local_values=2448,unit_conditioned_values=2040,unit_removed_values=408,AC_removed_values=0),
        coarse_triples=cover['counts'],
        hadamard=dict(selected_supports=5,local_pigeonhole_exclusions=1,integer_Farkas_exclusions=3,distinct_fixed_supports_excluded=4,
            excluded_cores=0,remaining_supports=1,exact_fractional_witnesses=1,full_integer_factors=0,
            completed_LP_attempts=4,numerical_statuses=lpstatuses,Farkas_cases=farkas['cases'],
            note='Projection screens, LP attempts and certificates are overlapping pipeline stages, not additive populations.'),
        complete99_graphs=0,new_full_factors=0,new_complete_UNSAT_proofs=0,new_unrestricted_exclusions=0,
        coverage='Overall search coverage: UNKNOWN; no validated denominator.',
        execution=dict(observed_at=observed,command=cmd,exit_code=process.returncode,state=state,
            stdout_sha256=h(B+'resume/sixteenth_process_snapshot.stdout.log'),stderr_sha256=h(B+'resume/sixteenth_process_snapshot.stderr.log'),
            scope='All sixteenth-cohort computations completed. Any later cyclic-factor native attempt is outside this cohort.'),
        next_experiment='Prepare and independently audit the broader ordered coloring model for the remaining fixed Hadamard support, then run its exact factor search; this belongs to the next cohort.',
        evidence_sha256=pins,ledger_snapshot_sha256=h(snapshot))
    save(B+'resume/sixteenth_milestone_checkpoint.json',record)
    rows='\n'.join('| `'+c['id']+'` r'+str(c['revision'])+' | '+c['scope']['description']+' [Evidence](../'+artifacts[c['evidence'][0]]['path']+'). |'for c in claims)
    report=f'''# Sixteenth resumed milestone, 2026-09-30 JST

Seventeen independently checked claims were added since the [corrected fifteenth milestone](RESEARCH_20260930_FIFTEENTH_WAVE_CORRECTED.md). Four of five selected Hadamard support matrices are excluded, one by a local pigeonhole argument and three by exact integer Farkas certificates. The remaining support has an exact fractional witness. No core family, full factor or target graph was obtained or excluded.

**As of:** {now}; source commit `{source}`. [Checkpoint](../{B}resume/sixteenth_milestone_checkpoint.json), [ledger snapshot](../{snapshot}); previous report: corrected fifteenth milestone.

**Verdict:** target resolution UNKNOWN. The repository has neither an independently validated99-vertex graph nor a general nonexistence proof. No target resolution is under external review. [Draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3) remains unmerged. This is not a worldwide literature verdict.

**Verified changes:** the seventeen new claims have the exact scopes below. The connected01 exclusion is revision2 solely to add independently checked compressed evidence; its statement, assumptions, scope and dependencies are unchanged. All original evidence and verification records remain preserved.

| Claim | Exact scope and evidence |
| --- | --- |
{rows}

**Work completed:** the independent64-action normalization preserves the fixed coarse60 model. Its one native attempt ended UNKNOWN after2,000,001 observed conflicts, under a2,000,000-conflict/300-second configuration. The independent execution audit found no SAT object or complete UNSAT proof. Its2,055,785,844-byte partial trace remains LOCAL_ONLY and is not a certificate.

After six explicit bit conditions,2,040 of2,448 local domain values remain; complete bidirectional arc checking removes no additional value. This does not establish a jointly compatible factor. The separate complete census of34,220 coarse-column triples finds18,440 admissible triples and15,780 rejected triples. Its saved20-triple cover has all60 within-triple pairs disjoint, but900 of1,296 ordered Gram entries are wrong. An independent universal cyclic-fibre cover argument shows the proposed cover-only strengthening is redundant for all raw bit assignments of this particular coarse60 template. Actual residual-D equations remain necessary.

The identity-P lemmas are conditional: any actual completion in that family has a33-triangle vertex partition. The residual contraction equations and the redundant individual row-capacity test are independently derived, with nonempty243-vertex and exact margin controls. Identity-P is not assumed for the unrestricted target, and a chosen cyclic partition is not asserted without loss of generality.

The Hadamard construction supplies only a12x60 aggregate support L. All five literal supports passed their aggregate identities; all27,000 local coloring candidates,8,850 pair projections and15 separate fibre projections were checked. The connected00 support is impossible because column41 requires at least three entries in a fibre with quota two. The four other supports underwent four continuous LP attempts. Three numerical infeasibility outcomes led to independently checked integer certificates for the exact connected01/02/03 supports; the numerical outputs themselves are not proofs. The surviving six-prism relaxation has5,400 selectors and726 equalities, satisfied exactly by uniform weights1/90. This fractional witness does not establish an integer factor or feasibility of the omitted column caps.

**Coverage:** four of the five frozen selected support matrices are excluded; this is a count of those exact matrices only. No core family or unrestricted branch was excluded. Overall search coverage: UNKNOWN; no validated denominator. The ledger contains165 claims:163 VERIFIED/CLEAR and2 CANDIDATE/CLEAR. The projection, LP and certificate stages overlap and are not summed.

**Best result:** four exact fixed-support exclusions and one exact fractional feasibility witness. Integer Farkas products are certificate identities, not comparable search objectives. No new full36x60 factor is available.

**Problems:** the native attempt was UNKNOWN. The original AC checker imposed an irrelevant ordering, and the first Hadamard checker had a transcribed gate hash; both failed records and corrected checks are preserved. Numerical bounded-denominator reconstructions failed before separate exact certificate repair or the literal uniform witness. A registration attempt was rejected for adding evidence without increasing its revision and for shared in-memory list propagation; it wrote no ledger. Independent revision2 impact review and a corrected registrar preserve all unrelated claims. The large connected01 CNF was built but never searched or independently approved, because a cheaper exact LP certificate excluded its fixed support. Its artifact status remains distinct from the verified LP exclusion. Large raw records have lossless packages; native binaries and the incomplete trace remain LOCAL_ONLY.

**Execution:** all cohort computations completed. Fresh native observation at {observed}: `{state}`. Exact observation logs are bound in the checkpoint; any later cyclic-factor attempt is separate. The user's continuation instruction remains active.

**Next experiment:** prepare and independently audit the broader coloring model on the remaining fixed Hadamard support, then test it with independently justified ordering of identical-support columns. The later run and its verification belong to the seventeenth cohort and do not alter this checkpoint's completed-work counts. Its restricted native outcome is not a target resolution. A future factor still needs residual completion and independent full99-vertex validation.

**References:** [source commit](https://github.com/ikuto32/conway-99-graph/commit/{source}), [draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3), [catalog](../{catalog_path}), [replay guide](REPRODUCING_20260930_SIXTEENTH_WAVE.md). Immutable publication pointers follow remote confirmation.
'''
    with(ROOT/'docs/RESEARCH_20260930_SIXTEENTH_WAVE.md').open('x',encoding='utf-8',newline='\n')as f:f.write(report)
    print(json.dumps(dict(claims=165,new_claims=17,evidence_only_revision_changes=1,native_state=state,target_resolution='UNKNOWN')))


if __name__=='__main__':main()
