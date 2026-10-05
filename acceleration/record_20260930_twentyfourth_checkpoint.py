"""Freeze wave24 scientific state; later wave25 experiments stay outside."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import hashlib, json, subprocess, sys, yaml
ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'
I=B+'independent_review/'
REG=[B+'twentyfourth_'+name+'_registration' for name in ['base','count','gram','final']]
GATES={
    'proofs':('hadamard_twohundredfifteen_profile_proofs','14d5064f7d09f491899f25113844df53b0b49658abc549ed784ed0b92ad55210'),
    'union':('hadamard_seven_profile_union','fe1108f78c2b925ee6a79a55cff53ee9abe6d292965fd2550a1e6a9d34881df4'),
    'intervals':('count_gram_intervals','ebace5fc527bded41f3c31fb66455e78b0eb133c8575508d4426eff912e6ae33'),
    'refutation':('local_frechet_equality','f888dae9caee35f174c424169bc4784b5404ef783b0943f04a444bf6b3b558af'),
    'count_witness':('count_master_sat_outcome','61e7eb9643902c866617a270d856a521f71f5b2723c0e731edae3896baba484d'),
    'interval_witness':('count_interval_constructed_object','7deae0325b9acb8f97c3941503bc49dec9a2b0eb94c5f805411085ceb5e6e27a'),
    'eight_exclusion':('eight_count_profile_unsat','c846d32c668910bb1254b840ca3bff6b97ec8bb5878e3092e48575e5bbe3e1ed'),
    'six_cuts':('count_master_eight_orbit_cuts','4c919b9b48d4c9d6bf085480f9ae166172f33b457e85713c50c109c29bc57493'),
    'blocks':('count_profile_gram_blocks','08b283144dd95ce250a0689ae6884a93313fe596571bdb3f8085df7328d13e6b'),
    'affine':('hadamard_gram_affine_gf2','d581cc37dc751f6aa96be2b016ac33084d466d7497982002506bf7091178dcfa'),
    'transport':('hadamard_twohundredfifteen_proof_transport','4a893e6636a102e6ab0ba32e69674bae96288e320e24d0242cd974017db645f6')}
def sha(path):
    with (ROOT/path).open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()
def read(path):
    return json.loads((ROOT/path).read_bytes())
def save(path,value):
    with (ROOT/path).open('x',encoding='utf8',newline='\n') as stream:
        json.dump(value,stream,indent=2)
        stream.write('\n')
def main():
    raw=(ROOT/'CLAIMS.yaml').read_bytes()
    assert hashlib.sha256(raw).hexdigest()=='ee94a175838c99a0021ec409dbf6a43c326008f8ca8d8223867f56f4ece2707a'
    ledger=yaml.safe_load(raw)
    artifacts={a['id']:a for a in ledger['artifacts']}
    ids=[cid for directory in REG for cid in read(directory+'/summary.json')['new_claim_ids']]
    claims=[next(c for c in ledger['claims'] if c['id']==cid) for cid in ids]
    counts=Counter(c['status'] for c in ledger['claims'])
    assert len(ledger['claims'])==248 and len(ids)==len(set(ids))==19
    assert counts==dict(VERIFIED=244,CANDIDATE=2,REFUTED=2)
    assert Counter(c['status'] for c in claims)==dict(VERIFIED=18,REFUTED=1)
    assert all(c['review_state']=='CLEAR' and c['revision']==1 for c in claims)
    assert (ROOT/REG[-1]/'CLAIMS.after.yaml').read_bytes()==raw
    paths={key:I+directory+'/summary.json' for key,(directory,_) in GATES.items()}
    for key,(_,digest) in GATES.items():
        assert sha(paths[key])==digest
    paths['native']=B+'hadamard_seven_profile_batch_native/summary.json'
    assert sha(paths['native'])=='02520b91d50c0f448fc966b61348da0215d520a5f2082767d09918632b0b0b46'
    records={key:read(path) for key,path in paths.items()}
    union=records['union'];proof=records['proofs'];native=records['native']
    assert union['profile_population']==1608 and union['AC_exclusions']==312 and union['nonempty_profile_members']==1296
    assert union['authenticated_complete_proofs']==216 and union['authenticated_complete_proof_bytes']==584922543
    assert union['duplicate_coverage']==union['missing_profiles']==0
    assert proof['completed_proof_replays']==215 and proof['proof_bytes']==577482170 and proof['UNKNOWN']==proof['SAT_pending_separate_review']==0
    assert native['completed_attempts']==215 and native['unattempted_profiles']==[] and native['stop_reason']=='ALL_SELECTED_PROFILES_ATTEMPTED'
    assert records['interval_witness']['actual_clauses_checked']==7659287 and records['blocks']['feasible_pairs']==60
    assert records['affine']['models']==records['affine']['positive_XOR_certificates']==217
    assert records['refutation']['claim_status']=='REFUTED' and not records['refutation']['loose_bounds_refuted']
    evidence=set(paths.values())|{artifacts[aid]['path'] for claim in claims for aid in claim['evidence']}|{d+'/summary.json' for d in REG}
    now=datetime.now(timezone.utc).isoformat()
    source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    snapshot=B+'resume/claims_at_twentyfourth_milestone.yaml'
    checkpoint=B+'resume/twentyfourth_milestone_checkpoint.json'
    report='docs/RESEARCH_20260930_TWENTYFOURTH_WAVE.md'
    for path in [snapshot,checkpoint,report]:
        assert not (ROOT/path).exists()
    command=['wsl.exe','--distribution','Ubuntu-24.04','--exec','/usr/bin/ps','-C','cadical','-o','pid,ppid,comm,pcpu,rss,args']
    observed=datetime.now(timezone.utc).isoformat()
    process=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=15)
    state='CADICAL_PROCESS_OBSERVED' if process.returncode==0 else 'NO_CADICAL_PROCESS_OBSERVED' if process.returncode==1 else 'UNKNOWN_OBSERVATION_ERROR'
    for name,data in [('stdout',process.stdout),('stderr',process.stderr)]:
        with (ROOT/(B+'resume/twentyfourth_process_snapshot.'+name+'.log')).open('xb') as stream:
            stream.write(data)
    with (ROOT/snapshot).open('xb') as stream:
        stream.write(raw)
    next_action='Independently review the next count witness after the six exact cuts, then build and test its literal full-Gram lift; separately inventory a joint all-triple/count formulation before a large build.'
    result=dict(timestamp=now,source_commit=source,command=[sys.executable,*sys.argv],cwd=str(ROOT),writer_sha256=sha(Path(__file__).relative_to(ROOT)),previous_report='docs/RESEARCH_20260930_TWENTYTHIRD_WAVE.md',previous_checkpoint_sha256=sha(B+'resume/twentythird_milestone_checkpoint.json'),claim_population=248,verified_clear=244,candidate_clear=2,refuted_clear=2,new_verified_ids=[c['id'] for c in claims if c['status']=='VERIFIED'],new_refuted_ids=[c['id'] for c in claims if c['status']=='REFUTED'],claim_status_counts=dict(counts),claim_review_counts=dict(Counter(c['review_state'] for c in ledger['claims'])),target_resolution='UNKNOWN',external_review=None,external_review_null_reason='No target-resolution artifact exists.',necessary_unbalanced_counts=dict(at_least=8,scope='Literal fixed support, prescribed full integer Gram and all outside-column overlap caps.'),seven_profile_union={k:union[k] for k in ['profile_population','AC_exclusions','nonempty_profile_members','authenticated_complete_proofs','authenticated_complete_proof_bytes','duplicate_coverage','missing_profiles']},native_batch=dict(selected=215,attempted=215,completed=215,UNSAT=215,SAT=0,UNKNOWN=0,complete_independent_proof_replays=215,proof_bytes=577482170,wrapped_solver_wall_seconds=native['wrapped_solver_wall_seconds'],end_to_end_wall_seconds=native['end_to_end_wall_seconds']),separate_seven_pilot=dict(complete_independent_proof_replays=1,proof_bytes=7440373),separate_eight_literal=dict(complete_independent_proof_replays=1,proof_bytes=7811117,excluded_fibre_images=6,scope='One literal count profile and its six exact global fibre images only.'),interval_witness=dict(variables=185963,clauses_checked=7659287,exceptional_groups=8,scalar_cells=540,constructed_without_new_solver=True,full_factor=False),separate_block_witnesses=dict(pairs=60,feasible=60,simultaneous_choice=False),affine_relaxations=dict(models=217,consistent=217,full_catalogue_rank=323,fixed_count_rank=193,full_factor=False),new_full_factors=0,complete99_graphs=0,new_whole_support_exclusions=0,new_core_exclusions=0,new_unrestricted_exclusions=0,coverage='Overall search coverage: UNKNOWN; no validated denominator.',ledger_snapshot_sha256=sha(snapshot),evidence_sha256={path:sha(path) for path in sorted(evidence)},next_experiment=next_action,later_cohort='The subsequent six-cut native count pilot, its object/outcome review and joint all-triple inventory are wave25 continuation, outside this frozen milestone.',execution=dict(observed_at=observed,command=command,exit_code=process.returncode,state=state,stdout_sha256=sha(B+'resume/twentyfourth_process_snapshot.stdout.log'),stderr_sha256=sha(B+'resume/twentyfourth_process_snapshot.stderr.log'),scope='Fresh targeted CaDiCaL observation only; other process states UNKNOWN.'))
    save(checkpoint,result)
    table='\n'.join('| '+c['id']+' r1 | '+c['status']+' | '+c['scope']['description']+' [Evidence](../'+artifacts[c['evidence'][0]]['path']+'). |' for c in claims)
    text=f'''# Twenty-fourth resumed milestone, 2026-09-30 JST

Eighteen VERIFIED claims and one REFUTED formula claim were added since the [twenty-third milestone](RESEARCH_20260930_TWENTYTHIRD_WAVE.md). Complete proof replay and disjoint profile coverage now exclude exactly seven unbalanced groups on the literal support. Together with prior exclusions, this fixed-support Gram-plus-column-cap family needs at least eight unbalanced groups. Conway-99 remains unresolved.

**As of:** {now}; source commit {source}. [Checkpoint](../{checkpoint}), [frozen ledger](../{snapshot}); previous report: twenty-third milestone.

**Verdict:** target resolution UNKNOWN. This repository has neither an independently validated99-vertex target graph nor a general nonexistence proof. No target-resolution artifact is under external review. This is not a worldwide literature verdict. PR3 remains draft and unmerged.

**Claim changes:**

| Claim | Status | Exact scope and evidence |
| --- | --- | --- |
{table}

**Work completed:** all215 selected seven-profile formulas were independently reconstructed and attempted once. All215 returned UNSAT and all577,482,170 complete proof bytes passed independent replay, with no SAT, UNKNOWN or unattempted case. The separate seven-profile pilot adds one checked7,440,373-byte proof. The exact union covers1,608 necessary profiles:312 pair-screen exclusions and1,296 disjoint fibre images of216 proved representatives, without gaps or duplicate coverage. No target automorphism is assumed.

The exact count master has a checked eight-group count witness. Its constructed interval extension satisfies all7,659,287 clauses and540 scalar bounds. Every one of60 separate3x3Gram blocks also has a checked local witness. Nevertheless the complete literal full-Gram lift is UNSAT by a separately replayed7,811,117-byte proof. The exclusion transfers to six explicit fibre images, giving six exact20-literal cuts. These weaker-model positive records remain valid; they do not imply a global factor.

All6,061 local count classes have exact extrema for135 coefficients:818,235 coefficient records and1,636,470 attaining witnesses were independently checked. On984 previously excluded six-group profiles the scalar screen rejects546 and retains438; it adds no new coverage to that already closed family. The proposed equality with loose Frechet bounds is REFUTED by one independently exhaustive local counterexample. The loose inequalities themselves remain valid; the producer's aggregate mismatch count was not independently certified.

An exact affine screen modulo2 gives valid XOR certificates for217 specified domain models. The complete local-catalogue model has difference-span rank323; each of216 fixed-count models has rank193. This necessary affine relaxation finds no obstruction and does not choose a single valid local option per group.

**Coverage:** no new whole-support, core or unrestricted exclusion. Overall search coverage: UNKNOWN; no validated denominator. The ledger has248 claims:244 VERIFIED/CLEAR, two CANDIDATE/CLEAR and two REFUTED/CLEAR. These counts are not a percentage of Conway-99 solved.

**Best result:** the conditional lower bound of eight unbalanced groups on one fixed support, under its prescribed integer Gram and all outside-column overlap caps. No complete factor was produced. The earlier heuristic full squared Frobenius Gram error296 is unchanged and is not an exact existence certificate.

**Problems:** the first215-formula audit encountered an ordering mismatch between numeric census order and lexicographic profile IDs; corrected v2 reran all formulas. A scalar-screen checker expected absent witness fields, and registrar metadata/schema checks rejected receipt-status and kind mismatches before ledger writes; corrected versions and failure evidence are preserved. The Frechet exact-extrema conjecture is refuted. Raw artifact identity recovery does not replace mathematical checking. Earlier missing traces and privacy omissions remain unchanged.

**Execution:** the215-call campaign and both literal full-Gram pilots completed, as did independent proof replay. This campaign took{native['wrapped_solver_wall_seconds']:.3f} wrapped-solver seconds and{native['end_to_end_wall_seconds']:.3f} seconds end to end; these are measurements of this one campaign. Targeted observation at{observed}: {state}. Later six-cut count searching and the joint-model inventory are outside this frozen scientific report.

**Next experiment:** {next_action}

**References:** [source commit](https://github.com/ikuto32/conway-99-graph/commit/{source}), [draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3), [catalog](../{B}twentyfourth_artifact_packaging/catalog.json), [replay guide](REPRODUCING_20260930_TWENTYFOURTH_WAVE.md). Immutable publication pointers follow remote confirmation.
'''
    with (ROOT/report).open('x',encoding='utf8',newline='\n') as stream:
        stream.write(text)
    print(json.dumps(dict(checkpoint=checkpoint,sha256=sha(checkpoint),claim_population=248,execution=state)))
if __name__=='__main__':
    main()
