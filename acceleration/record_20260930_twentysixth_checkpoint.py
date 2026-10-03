"""Freeze eleven reviewed wave26 claims; next-lift/kernel work is a later wave."""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import hashlib, json, subprocess, sys, yaml

ROOT = Path(__file__).resolve().parents[1]
B = 'acceleration/results/20260930_'
I = B + 'independent_review/'
REG = [B+'twentysixth_'+n+'_registration' for n in
       ['profile','upper','block','eight_reduction','census_algebra','psd','scalar','block_screen']]
GATES = {
'preflight': ('exact_eight_profile_preflight','1a120763c8d97677e0339828abf14cba2394e71f5d6459f153e29f42c534541f'),
'join': ('exact_eight_profile_join','2538bf724a3938b14ffd1856fc4e9a8a6a294a6905ddc7000d19cf72f93b217c'),
'scalar': ('exact_eight_scalar_screen','52b2818cdad6a3e90d7685442ad9f1cb717eba7fe81ce07338a1bcc0bd8adf11'),
'blocks': ('exact_eight_block_screen','6c21ef6951f72fbeabab8be0a649f178ca8b17eb91edcc35c3291d6790f6256a'),
'third_proof': ('third_eight_count_profile_unsat','b7a7c19c59e456ce574fb6b8aa89cff55b5943e0a29ddcd7e49ba53c6c61a49c'),
'psd': ('triplicate_count_psd','1217ea22d037c24be3039c29687e8e0b126f3fe122186687ecaee8065351a4f4'),
'gf3': ('gf3_hollow_residual','5f234e9d726ce39555ff6649f0050481ee5c445a627aa2c27e7c730c7b8de220'),
'upper': ('count_min_upper_cnf','65624096b816cccec2f497f99b3ea099a03b7f9235862c86c2f480ca7909942f')}

def sha(p):
    with (ROOT/p).open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
def read(p): return json.loads((ROOT/p).read_bytes())
def save(p,obj):
    with (ROOT/p).open('x',encoding='utf8',newline='\n') as f:
        json.dump(obj,f,indent=2);f.write('\n')

def main():
    raw=(ROOT/'CLAIMS.yaml').read_bytes()
    assert hashlib.sha256(raw).hexdigest()=='8bcdad8f4b2e871b6c0bdf6ef72736033a8d84624af029e1b01c2951bc4b8146'
    ledger=yaml.safe_load(raw);counts=Counter(c['status'] for c in ledger['claims'])
    assert len(ledger['claims'])==278 and counts==dict(VERIFIED=273,CANDIDATE=3,REFUTED=2)
    ids=[];previous=None
    for directory in REG:
        r=read(directory+'/summary.json')
        before=(ROOT/directory/'CLAIMS.before.yaml').read_bytes();after=(ROOT/directory/'CLAIMS.after.yaml').read_bytes()
        assert hashlib.sha256(before).hexdigest()==r['previous_ledger_sha256']
        assert hashlib.sha256(after).hexdigest()==r['ledger_sha256']
        assert previous is None or previous==before
        previous=after;ids+=r['new_claim_ids']
    assert previous==raw and len(ids)==len(set(ids))==11
    claims=[c for c in ledger['claims'] if c['id'] in ids]
    assert all(c['status']=='VERIFIED' and c['review_state']=='CLEAR' and c['revision']==1 for c in claims)
    artifacts={a['id']:a for a in ledger['artifacts']}
    paths={k:I+d+'/summary.json' for k,(d,h) in GATES.items()}
    for k,(d,h) in GATES.items(): assert sha(paths[k])==h
    records={k:read(p) for k,p in paths.items()}
    assert records['join']['labelled_profiles']==9288 and records['join']['complete_fibre_orbits']==1548
    assert records['scalar']['representatives_excluded']==756 and records['scalar']['representatives_surviving']==792
    assert records['blocks']['profile_pair_tests']==47520 and records['blocks']['representatives_excluded']==0
    assert records['blocks']['representatives_surviving']==792
    now=datetime.now(timezone.utc).isoformat();source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    checkpoint=B+'resume/twentysixth_milestone_checkpoint.json';snapshot=B+'resume/claims_at_twentysixth_milestone.yaml'
    report='docs/RESEARCH_20260930_TWENTYSIXTH_WAVE.md'
    assert all(not (ROOT/p).exists() for p in [checkpoint,snapshot,report])
    cmd=['wsl.exe','--distribution','Ubuntu-24.04','--exec','/usr/bin/ps','-C','cadical','-o','pid,ppid,comm,pcpu,rss,args']
    observed=datetime.now(timezone.utc).isoformat();p=subprocess.run(cmd,cwd=ROOT,capture_output=True,timeout=15)
    state='CADICAL_PROCESS_OBSERVED' if p.returncode==0 else 'NO_CADICAL_PROCESS_OBSERVED' if p.returncode==1 and len(p.stdout.splitlines())<=1 else 'UNKNOWN_OBSERVATION_ERROR'
    for name,b in [('stdout',p.stdout),('stderr',p.stderr)]:
        with (ROOT/(B+'resume/twentysixth_process_snapshot.'+name+'.log')).open('xb') as f:f.write(b)
    with (ROOT/snapshot).open('xb') as f:f.write(raw)
    evidence=set(paths.values())|{d+'/summary.json' for d in REG}|{artifacts[aid]['path'] for c in claims for aid in c['evidence']}
    metrics={k:{key:value for key,value in r.items() if isinstance(value,(int,float,bool))} for k,r in records.items()}
    next_action='Run the first canonical block survivor outside the three previously tested fibre orbits through a full-Gram literal lift, after independent encoding/object gates; independently validate any decoded factor or complete UNSAT proof.'
    result=dict(timestamp=now,source_commit=source,writer_sha256=sha(Path(__file__).relative_to(ROOT)),command=[sys.executable,*sys.argv],cwd=str(ROOT),
        previous_report='docs/RESEARCH_20260930_TWENTYFIFTH_WAVE.md',previous_checkpoint_sha256=sha(B+'resume/twentyfifth_milestone_checkpoint.json'),
        claim_population=278,claim_status_counts=dict(counts),claim_review_counts=dict(Counter(c['review_state'] for c in ledger['claims'])),new_verified_ids=ids,new_candidate_ids=[],new_refuted_ids=[],
        target_resolution='UNKNOWN',external_review=None,external_review_null_reason='No target-resolution artifact exists; no external review asserted.',
        exact_audit_metrics=metrics,literal_gram_lift=dict(selected=1,attempted=1,completed=1,UNSAT=1,complete_independent_proof_replays=1,proof_bytes=5549451,scope='Third literal profile only; no orbit exclusion is inferred.'),
        count_pipeline=dict(kernel_retained_subsets_tested=4184,nonempty_subsets=67,labelled_profiles=9288,global_fibre_classes=1548,scalar_excluded_classes=756,scalar_surviving_classes=792,separate_block_tests=47520,block_excluded_classes=0,block_surviving_classes=792,scope='Literal six-prism support with exactly eight unbalanced triplicates, necessary count constraints and within-triplicate caps. Stages overlap and are not summed.'),
        new_full_factors=0,new_complete99_graphs=0,new_whole_support_exclusions=0,new_unrestricted_exclusions=0,coverage='Overall search coverage: UNKNOWN; no validated denominator.',
        best_result='Prior fixed-support conditional at-least-eight bound unchanged; a complete exactly-eight count census has1548 classes,756 excluded by scalar bounds. Survivors need simultaneous Gram realization.',
        ledger_snapshot_sha256=sha(snapshot),evidence_sha256={q:sha(q) for q in sorted(evidence)},next_experiment=next_action,
        excluded_future_cohort=['exact_eight_next_lift','triplicate_psd_kernel_options'],
        execution=dict(observed_at=observed,command=cmd,exit_code=p.returncode,state=state,stdout_sha256=sha(B+'resume/twentysixth_process_snapshot.stdout.log'),stderr_sha256=sha(B+'resume/twentysixth_process_snapshot.stderr.log'),scope='Fresh exact-named native process observation only; other process states UNKNOWN. Milestone, not a user stop.'))
    save(checkpoint,result)
    table='\n'.join('| '+c['id']+' r1 | '+c['scope']['description']+' [Evidence](../'+artifacts[c['evidence'][0]]['path']+'). |' for c in claims)
    content=f'''# Twenty-sixth research milestone, 2026-09-30

Eleven VERIFIED scoped claims were added since the [twenty-fifth milestone](RESEARCH_20260930_TWENTYFIFTH_WAVE.md). A complete count census on the fixed support gives 1,548 global fibre classes; scalar bounds exclude 756, and all 792 survivors pass separate block tests. One further literal profile has a complete independently checked UNSAT proof. Conway-99 remains unresolved.

**As of:** {now}; source commit {source}; [checkpoint](../{checkpoint}), [frozen ledger](../{snapshot}). Each run preserves its actual source and environment.

**Verdict:** target resolution UNKNOWN. No independently validated target graph or general nonexistence proof exists in this repository. No target-resolution artifact is under external review. This is not a worldwide literature verdict. PR3 remains draft and unmerged.

**Verified changes:** all entries below are VERIFIED/CLEAR at revision 1.

| Claim | Exact scope and evidence |
| --- | --- |
{table}

**Work completed:** the exact-eight preflight checked all 4,184 prior kernel-retained subsets and retained 67. Independent mixed-radix enumeration checked all 7,122,626 remaining Cartesian assignments, yielding 9,288 labelled count profiles in 1,548 six-member fibre orbits. All profiles and all six images were checked. These are count tables, not graph factors.

The complete scalar screen independently excluded 756 classes (4,536 labelled profiles), leaving 792 (4,752 labelled profiles). The separate block screen checked all 47,520 profile/block pairs and excludes zero further classes. Independent checking used complete two-plus-three Cartesian sum sets for all 2,527 distinct block problems. Separate block witnesses need not share compatible local choices. Historical literal exclusions are not added to these counts without a checked union.

The third literal count profile passes all 540 scalar and 60 separate block diagnostics, but its full simultaneous Gram formula returned UNSAT in one native attempt. The entire 5,549,451-byte DRAT trace passed independent replay with corruption controls. This excludes only that literal profile; no orbit or whole-support conclusion is inferred here. An exact forced-block identity was also independently established for the first and third literal profiles.

A shared-threshold upper-envelope builder adds 5,220 variables and 20,640 clauses to the count formula. Its 161,159-variable, 726,485-clause output and an extension of the existing third count assignment were checked; no new count solution or native search is claimed. A GF(3) symmetric/hollow mixed-completion criterion was independently derived and checked, with 7,290 direct small systems and a genuine 243-vertex fixture. It does not impose binary, integer or quadratic residual completion. Three literal count profiles also pass the exact rational necessary triplicate PSD test at rank 22; this establishes no factor feasibility.

**Coverage:** 278 ledger claims: 273 VERIFIED/CLEAR, three CANDIDATE/CLEAR, two REFUTED/CLEAR. Eleven newly verified records include encodings, finite diagnostics, a conditional exclusion, a complete fixed-support count census and algebraic criteria. No whole-support or unrestricted exclusion was added. Overall search coverage: UNKNOWN; no validated denominator.

**Best result:** the prior fixed-support lower bound of eight unbalanced groups is unchanged. The complete exactly-eight count population is now explicit, and 792 of its 1,548 classes survive the scalar screen. This fraction concerns count classes only; it is not a fraction of graphs or remaining computational difficulty.

**Problems:** separate block feasibility and PSD positivity did not exclude the remaining classes. Producer proof-core, singleton and floating-point LP diagnostics remain unverified exploratory evidence; the LP rational recovery failed and supplies no exact feasibility certificate. A registrar first failed on a timestamp field before any ledger write; its source and failure receipt are retained, and a fresh v2 completed registration. No failed evidence was overwritten. Earlier missing artifacts and privacy omissions remain unchanged.

**Execution:** the third literal native attempt completed UNSAT; all count census/screen computations completed and were independently checked. Targeted observation at {observed}: {state}. The next literal lift and PSD-kernel scout belong to the next wave and are excluded from these milestone counts. This checkpoint does not stop research.

**Next experiment:** {next_action}

**References:** [source commit](https://github.com/ikuto32/conway-99-graph/commit/{source}), [draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3), [replay guide](REPRODUCING_20260930_TWENTYSIXTH_WAVE.md). Immutable publication pointers follow remote confirmation.
'''
    with (ROOT/report).open('x',encoding='utf8',newline='\n') as f:f.write(content)
    print(json.dumps(dict(checkpoint=checkpoint,sha256=sha(checkpoint),claim_population=278,execution=state)))

if __name__=='__main__':main()
