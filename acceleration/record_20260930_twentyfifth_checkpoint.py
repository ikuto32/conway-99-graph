"""Freeze wave25 claims/run counts; newer third-lift/min-envelope work is separate."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import hashlib,json,subprocess,sys,yaml
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';I=B+'independent_review/'
REG=[B+'twentyfifth_'+n+'_registration'for n in ['profile','scalar','direct_encoding','unknown','lex_cuts','final']]
GATES={
'second_count':('count_master_eight_orbit_cut_sat_outcome','7c80d3e4daef0f259bd354e6e6b28188b660edaaf17c7a20f9c54cfb3abc4c3c'),
'second_profile_proof':('second_eight_count_profile_unsat','54525e34e879ec10c60c62172e4394b90cf12e8876d0f684e7306f7c61f6e010'),
'second_profile_scalar':('second_count_scalar_obstruction','b10f6ae68f711f299ea34b67613f85c84f2904e64612019696ac7819f40af92c'),
'direct_standalone':('direct_cell_standalone_unknown_v2','7a97722db1ede1df9f01004af8e00f6ff3503dcdf16618e893bf5d6a70f0b1fd'),
'direct_coupled':('direct_cell_count_coupled_unknown_v2','677cd12aa5096097311538a894ed0cf885007daa13242a21cf9b7be57215bb95'),
'lex_standalone':('direct_cell_lex_standalone_unknown','f56257086586c6cad43bcab89da071551ca6d67e30196749827bb10dda280233'),
'lex_coupled':('direct_cell_lex_coupled_unknown','dde2093be28b749c4bd27e9be06158cce19d84d65aadb1123bc4cfa4d4191e8a'),
'partial_cuts':('second_count_partial_cut','727f9aa9aec1b3fe3f0f422e440dd0fb6fb5bfc63602c3aeee28ba3082bccfc8'),
'third_count':('count_master_partial_cut_sat_outcome','736ccbcda81ee34c21ede2a80253d5b224fabb96a2e83d0a2c1c76dba435d071'),
'gf2':('gf2_alternating_completion_v2','a18dbc2aff1e98a881226e04432e3db08a0b827741dc615eaf00c1c06ca0d093'),
'gf2_scope':('gf2_alternating_completion_scope_addendum','c7e030dc5021fd018ab90371e8c9f82c72c116f40bf6f2a1e9b900f67b85e44a'),
'direct_transport':('direct_cell_unknown_trace_transport','58905474aeed1bac31b58f30645b95019607cd10af7bab6542fb4712870503e5'),
'lex_transport':('lex_unknown_trace_transport','56b004dc3c72cb818610575febea7ef1a648e7c22d79bd0b28f6a0cd697c425c')}
def sha(p):
    with(ROOT/p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def save(p,x):
    with(ROOT/p).open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def main():
    raw=(ROOT/'CLAIMS.yaml').read_bytes();assert hashlib.sha256(raw).hexdigest()=='82e03975b3e6eb109a0fb9c82746475a253763d1620d543e8938fec561d3cd77';ledger=yaml.safe_load(raw)
    assert len(ledger['claims'])==267;counts=Counter(c['status']for c in ledger['claims']);assert counts==dict(VERIFIED=262,CANDIDATE=3,REFUTED=2)
    ids=[];previous=None
    for directory in REG:
        receipt=read(directory+'/summary.json');before=(ROOT/directory/'CLAIMS.before.yaml').read_bytes();after=(ROOT/directory/'CLAIMS.after.yaml').read_bytes()
        assert hashlib.sha256(before).hexdigest()==receipt['previous_ledger_sha256'] and hashlib.sha256(after).hexdigest()==receipt['ledger_sha256'];assert previous is None or before==previous;previous=after;ids+=receipt['new_claim_ids']
    assert previous==raw and len(ids)==len(set(ids))==19
    claims=[c for c in ledger['claims']if c['id']in ids];assert Counter(c['status']for c in claims)==dict(VERIFIED=18,CANDIDATE=1);assert all(c['revision']==1 and c['review_state']=='CLEAR'for c in claims)
    artifacts={a['id']:a for a in ledger['artifacts']};paths={k:I+d+'/summary.json'for k,(d,h)in GATES.items()}
    for k,(d,h)in GATES.items():assert sha(paths[k])==h
    records={k:read(p)for k,p in paths.items()};third=records['third_count'];gf=records['gf2']
    assert third['variables_checked']==155939 and third['actual_clauses_checked']==705845 and third['exception_count']==8 and third['universal_upper_bounds_checked']==540 and third['upper_bound_failures']==0
    unknowns=[records[k]for k in ['direct_standalone','direct_coupled','lex_standalone','lex_coupled']];assert all(r['interpreted_result']=='UNKNOWN'and r['actual_research_calls']==1 for r in unknowns)
    assert gf['exact_completion_pairs']==4096 and gf['direct_D_systems']==8192 and gf['saved_core_diagnostics']==70
    assert records['direct_transport']['raw_bytes']==1148777487 and records['direct_transport']['gzip_parts']==138
    assert records['lex_transport']['raw_bytes']==699879424 and records['lex_transport']['gzip_parts']==84
    now=datetime.now(timezone.utc).isoformat();source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    checkpoint=B+'resume/twentyfifth_milestone_checkpoint.json';snapshot=B+'resume/claims_at_twentyfifth_milestone.yaml';report='docs/RESEARCH_20260930_TWENTYFIFTH_WAVE.md'
    assert all(not(ROOT/p).exists()for p in [checkpoint,snapshot,report])
    cmd=['wsl.exe','--distribution','Ubuntu-24.04','--exec','/usr/bin/ps','-C','cadical','-o','pid,ppid,comm,pcpu,rss,args'];observed=datetime.now(timezone.utc).isoformat();process=subprocess.run(cmd,cwd=ROOT,capture_output=True,timeout=15)
    state='CADICAL_PROCESS_OBSERVED'if process.returncode==0 else'NO_CADICAL_PROCESS_OBSERVED'if process.returncode==1 and len(process.stdout.splitlines())<=1 else'UNKNOWN_OBSERVATION_ERROR'
    for name,b in [('stdout',process.stdout),('stderr',process.stderr)]:
        with(ROOT/(B+'resume/twentyfifth_process_snapshot.'+name+'.log')).open('xb')as f:f.write(b)
    with(ROOT/snapshot).open('xb')as f:f.write(raw)
    evidence=set(paths.values())|{d+'/summary.json'for d in REG}|{artifacts[aid]['path']for c in claims for aid in c['evidence']}
    next_action='Test the third count witness against exact local Gram domains and then its full simultaneous Gram lift; use an independent encoding/object gate and replay any complete UNSAT proof.'
    result=dict(timestamp=now,source_commit=source,writer_sha256=sha(Path(__file__).relative_to(ROOT)),command=[sys.executable,*sys.argv],cwd=str(ROOT),previous_report='docs/RESEARCH_20260930_TWENTYFOURTH_WAVE.md',previous_checkpoint_sha256=sha(B+'resume/twentyfourth_milestone_checkpoint.json'),claim_population=267,claim_status_counts=dict(counts),claim_review_counts=dict(Counter(c['review_state']for c in ledger['claims'])),new_verified_ids=[c['id']for c in claims if c['status']=='VERIFIED'],new_candidate_ids=[c['id']for c in claims if c['status']=='CANDIDATE'],new_refuted_ids=[],target_resolution='UNKNOWN',external_review=None,external_review_null_reason='No target-resolution artifact exists; no external review asserted.',count_search=dict(selected_instances=2,attempted=2,completed=2,SAT=2,independently_checked_count_witnesses=2,unique_profile_digests=[records['second_count']['profile_sha256'],third['profile_sha256']],full_factors=0),literal_gram_lift=dict(selected=1,attempted=1,UNSAT=1,complete_independent_proof_replays=1,proof_bytes=1269209,scope='Second literal eight-count profile only; scalar argument excludes the same profile, not an additional disjoint case.'),direct_cell_search=dict(selected_formulas=4,attempted=4,completed=4,UNKNOWN=4,SAT=0,UNSAT=0,scope='Two fixed-support direct-cell variants, each unordered and lex-normalized; these search spaces overlap.'),third_count=dict(profile_sha256=third['profile_sha256'],variables=155939,actual_clauses_checked=705845,exception_count=8,upper_envelope_entries=540,upper_envelope_failures=0,full_factor=False),gf2=dict(exact_completion_pairs=4096,direct_D_systems=8192,saved_core_diagnostics=70,scope='General algebraic statements with stated field/triangle assumptions; finite diagnostics are not target coverage.'),partial_trace_transport=dict(host_streams=4,raw_bytes=1848656911,gzip_parts=222,complete_unsat_proofs=0),new_full_factors=0,new_complete99_graphs=0,new_whole_support_exclusions=0,new_unrestricted_exclusions=0,coverage='Overall search coverage: UNKNOWN; no validated denominator.',best_result='Prior conditional at-least-eight unbalanced groups bound unchanged. New third count witness passes540 necessary universal upper bounds; it is not a factor.',ledger_snapshot_sha256=sha(snapshot),evidence_sha256={p:sha(p)for p in sorted(evidence)},next_experiment=next_action,excluded_future_cohort=['third_count_profile_gram_diagnostic','eight_count_profile_lift_third','count_min_upper_inventory','count_min_upper_inventory_controls'],execution=dict(observed_at=observed,command=cmd,exit_code=process.returncode,state=state,stdout_sha256=sha(B+'resume/twentyfifth_process_snapshot.stdout.log'),stderr_sha256=sha(B+'resume/twentyfifth_process_snapshot.stderr.log'),scope='Fresh exact-named native process observation only; other process states UNKNOWN. This is a milestone checkpoint, not a user stop.'))
    save(checkpoint,result)
    table='\n'.join('| '+c['id']+' r1 | '+c['status']+' | '+c['scope']['description']+' [Evidence](../'+artifacts[c['evidence'][0]]['path']+'). |'for c in claims)
    content=f'''# Twenty-fifth research milestone, 2026-09-30

Eighteen VERIFIED claims and one CANDIDATE engineering inventory were added since the [twenty-fourth milestone](RESEARCH_20260930_TWENTYFOURTH_WAVE.md). One further literal eight-count profile is excluded by a complete checked proof and a simpler scalar argument. Six broader necessary scalar cuts led to a third checked count witness. Conway-99 remains unresolved.

**As of:** {now}; source commit {source}; [checkpoint](../{checkpoint}), [frozen ledger](../{snapshot}). Previous report: twenty-fourth milestone. Each run retains its own actual source commit and environment; the checkpoint source is not substituted for those records.

**Verdict:** target resolution UNKNOWN. This repository has neither an independently validated99-vertex target adjacency matrix nor a general nonexistence proof. No target-resolution artifact is under external review. This is not a worldwide literature verdict. PR3 remains draft and unmerged.

**Verified and candidate changes:**

| Claim | Status | Exact scope and evidence |
| --- | --- | --- |
{table}

**Work completed:** two selected count instances were each attempted once and returned SAT. Separate implementations checked both complete count witnesses. The second witness's literal full-Gram lift returned UNSAT; all1,269,209 proof bytes passed independent replay. A separate exact scalar proof excludes the same count profile: one prescribed intersection must be2 but its maximum is1. These are two checking paths for overlapping scope, not two disjoint exclusions.

Six25-literal necessary count clauses follow from five raw incidences, with no local-cap or automorphism premise. Every one of the294,000 local channel choices across the six clauses was checked; this is not a global count-solution census. The third witness satisfies all705,845 clauses, the six old full-profile cuts, the six new scalar cuts, and all540 universal overlap upper bounds. It has eight unbalanced groups. No simultaneous Gram factor follows.

The direct binary-cell full-Gram/all-column-cap formulation and its >=7 count-coupled variant were independently reconstructed. Equal-support column sorting adds160 variables and1,200 clauses to each formula while preserving existence under column relabelling; no target automorphism is assumed. Four selected native attempts completed with UNKNOWN, with no SAT or UNSAT conclusion. Their four saved host partial traces were independently preserved by222 gzip parts totaling1,848,656,911 raw bytes. These partial traces are not contradiction proofs; later audits found the original ext4 copies missing.

Independent algebraic review established an alternating mixed-completion criterion overGF(2), its explicitly conditional triangle specialization, and a symmetric block-rank inequality over arbitrary fields. The binary triangle consequence is conditional on the recorded margins and, for the vacuity statement, rank(B)>=18. No universal rank premise, integer residual D, or target exclusion is inferred. Finite controls included4,096 F/H pairs,8,192 direct unknown-D systems and70 saved core diagnostics; those populations are not Conway-99 coverage.

**Coverage:** 267 ledger claims:262 VERIFIED/CLEAR, three CANDIDATE/CLEAR, two REFUTED/CLEAR. Nineteen new records comprise18 verified scoped results and one unreviewed design estimate. No whole-support or unrestricted exclusion was added. Overall search coverage: UNKNOWN; no validated denominator.

**Best result:** the prior conditional lower bound of eight unbalanced groups on the fixed support is unchanged. The third count witness passes540 necessary universal upper bounds and awaits full-Gram realization testing. No score is treated as an existence certificate.

**Problems:** the direct-cell attempts remain UNKNOWN. The all-triple/count proposal's31,254,053-clause estimate is CANDIDATE and was not built; it is not a measured solver comparison. Its initial order failure and corrected memory probe are preserved. A GF(2) checker incorrectly compared images of different preimages before checking kernel compatibility; v1 failed, and a fresh v2 independently rechecked the corrected condition. A later append-only clarification states the field and H=(I+C)F assumptions explicitly. No failed evidence was overwritten. Earlier missing artifacts and privacy omissions remain unchanged.

**Execution:** this milestone's seven native attempts completed: two count SATs, one literal Gram UNSAT and four direct-cell UNKNOWNs. Their units and overlapping scopes are kept separate. Targeted observation at{observed}: {state}. New third-lift work and the small universal-envelope design inventory belong to the next wave and are excluded from these counts. This checkpoint does not stop the research.

**Next experiment:** {next_action}

**References:** [source commit](https://github.com/ikuto32/conway-99-graph/commit/{source}), [draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3), [replay guide](REPRODUCING_20260930_TWENTYFIFTH_WAVE.md). Immutable publication pointers are added only after remote confirmation.
'''
    with(ROOT/report).open('x',encoding='utf8',newline='\n')as f:f.write(content)
    print(json.dumps(dict(checkpoint=checkpoint,sha256=sha(checkpoint),claim_population=267,execution=state)))
if __name__=='__main__':main()
