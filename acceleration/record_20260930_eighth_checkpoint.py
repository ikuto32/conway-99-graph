"""Freeze six ledger-derived local/core results without target-coverage inflation."""
from collections import Counter
from datetime import datetime,timezone
import hashlib,json,subprocess,sys
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'
OUT=ROOT/(B+'resume')
def read(p):return json.loads((ROOT/p).read_bytes())
def digest(p):
    with(ROOT/p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,obj):
    with(ROOT/p).open('x',encoding='utf-8',newline='\n')as f:json.dump(obj,f,indent=2);f.write('\n')
def main():
    now=datetime.now(timezone.utc).isoformat();source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    raw=(ROOT/'CLAIMS.yaml').read_bytes();ledger=yaml.safe_load(raw)
    ids=read(B+'eighth_registration/summary.json')['new_claim_ids']+read(B+'identity_corollary_registration/summary.json')['new_claim_ids']
    claims=[c for c in ledger['claims']if c['id']in ids];assert len(claims)==6
    assert all(c['status']=='VERIFIED'and c['review_state']=='CLEAR'for c in claims)
    snapshot=B+'resume/claims_at_eighth_milestone.yaml'
    with(ROOT/snapshot).open('xb')as f:f.write(raw)
    pair=read(B+'independent_review/triangle_matching_pair_census/summary.json')
    perm=read(B+'independent_review/triangle_core_permutation_census_v2/summary.json')
    row=read(B+'independent_review/triangle_wave154_row29_obstruction/summary.json')
    gram=read(B+'independent_review/triangle39_gram_sos/summary.json')
    identity=read(B+'independent_review/triangle_core_identity/summary.json')
    command=['wsl.exe','-d','Ubuntu-24.04','--','ps','-C','cadical','-o','pid,etime,pcpu,rss,args']
    observed=datetime.now(timezone.utc).isoformat();process=subprocess.run(command,cwd=ROOT,capture_output=True)
    for suffix,content in [('stdout',process.stdout),('stderr',process.stderr)]:
        (OUT/('eighth_process_snapshot.'+suffix+'.log')).write_bytes(content)
    state='CADICAL_PROCESS_OBSERVED'if process.returncode==0 else'NO_CADICAL_PROCESS_OBSERVED'if process.returncode==1 else'UNKNOWN_OBSERVATION_ERROR'
    artifacts={a['id']:a for a in ledger['artifacts']};paths={artifacts[aid]['path']for c in claims for aid in c['evidence']}
    paths.update([snapshot,B+'eighth_registration/summary.json',B+'identity_corollary_registration/summary.json',B+'eighth_artifact_packaging/catalog.json'])
    counts={k:perm[k]for k in ['completed_matching_pair_cases','independently_checked_raw39_witnesses','unique_recorded_P_arrays','zero_domains','minimum_labelled_P_count','maximum_labelled_P_count','restored_labelled_matching_pairs','weighted_cap_compatible_labelled_triples','labelled_triple_population']}
    record=dict(timestamp=now,source_commit=source,command=[sys.executable,*sys.argv],cwd=str(ROOT),previous_report='docs/RESEARCH_20260930_SEVENTH_WAVE.md',
        previous_checkpoint_sha256=digest(B+'resume/seventh_milestone_checkpoint.json'),target_resolution='UNKNOWN',external_review=None,
        external_review_reason='No internally validated target graph or general nonexistence proof; no candidate resolution submitted for external review.',
        claim_population=len(ledger['claims']),verified_clear=sum(c['status']=='VERIFIED'and c['review_state']=='CLEAR'for c in ledger['claims']),
        claim_status_counts=dict(Counter(c['status']for c in ledger['claims'])),claim_review_counts=dict(Counter(c['review_state']for c in ledger['claims'])),
        new_verified_ids=ids,matching_pair_population=pair['counts'],permutation_population=counts,row_certificate=dict(constraints=row['constraints'],tree=row['tree']),
        gram_controls=gram['checks'],identity_controls=identity['checks'],new_solver_attempts_in_this_six_claim_milestone=0,
        newly_excluded_unrestricted_branches=0,coverage='Overall search coverage: UNKNOWN; no validated denominator.',
        execution=dict(observed_at=observed,command=command,exit_code=process.returncode,state=state,
            stdout_sha256=digest(B+'resume/eighth_process_snapshot.stdout.log'),stderr_sha256=digest(B+'resume/eighth_process_snapshot.stderr.log'),
            scope='Fresh observation only; any observed native process belongs to separate subsequent joint-factor work, not the six completed claims.'),
        next_experiment='Gated compact joint binary-incidence solve for one fixed39core, with both remaining incidence blocks free; independently replay any UNSAT proof or check any raw36x60 factor.',
        evidence_sha256={p:digest(p)for p in sorted(paths)})
    save(B+'resume/eighth_milestone_checkpoint.json',record)
    rows='\n'.join('| `'+c['id']+'` | '+c['scope']['description']+' [Audit](../'+artifacts[c['evidence'][0]]['path']+'). |'for c in claims)
    report=f'''# Eighth resumed milestone, 2026-09-30 JST

Six independently checked claims were added since the [seventh milestone](RESEARCH_20260930_SEVENTH_WAVE.md). They establish a complete matching-pair census, exact local permutation counts, two universal local-test limitations, and a small direct proof for the already excluded fixed Wave154 configuration.

**As of:** {now}; source commit `{source}`. [Checkpoint](../{B}resume/eighth_milestone_checkpoint.json), [ledger snapshot](../{snapshot}); previous report: seventh milestone.

**Verdict:** target resolution UNKNOWN. No independently validated 99-vertex target or general nonexistence proof is available in this repository. No candidate target resolution is under external review. Draft [PR3](https://github.com/ikuto32/conway-99-graph/pull/3) remains unmerged. This is a repository statement, not a worldwide literature verdict.

**Verified changes:** all six records are revision1.

| Claim | Exact scope and evidence |
| --- | --- |
{rows}

**Work completed:** the finite action on all 10,395 perfect matchings of twelve labels gives 11 first matching types and 3,580 ordered-pair orbits under the 46,080-element centralizer of a fixed matching. Exact orbit sizes cover 108,056,025 labelled ordered matching pairs. Of the 3,580 orbits, 1,701 have trivial joint stabilizer; no target automorphism is inferred.

All 3,580 labelled permutation-domain counts were independently recomputed, and all 3,580 saved local witnesses checked. The saved witnesses use {counts['unique_recorded_P_arrays']} distinct permutation arrays across different matching-pair cases; they are not 3,580 distinct permutations. Every domain is nonempty. Counts range from {counts['minimum_labelled_P_count']:,} to {counts['maximum_labelled_P_count']:,}. The exactly defined local labelled-triple population has {counts['weighted_cap_compatible_labelled_triples']:,} cap-compatible triples out of {counts['labelled_triple_population']:,}. This is not a population of target graphs or canonical full cores.

The identity permutation supplies a local cap-compatible construction for every triple of perfect matchings of every positive even order. It is not a valid normalization of an arbitrary target permutation. Separately, exact SOS identities show that both target Gram PSD tests automatically pass every explicitly defined 39-vertex core: ranks are 37-c and37, where c is the number of inner components. These statements explain why these local tests cannot settle the remaining binary incidence problem.

The direct Wave154 row29 certificate checks 38 binary entries through 139 nodes, 69 exhaustive splits and70 contradictory leaves. It gives a smaller independently checked explanation of the same fixed-family exclusion already certified in the seventh milestone. It adds no exclusion coverage. Its verifier reconstructs the constraints from the raw partial graph and does not rely on the SAT proof core.

**Coverage:** Overall search coverage: UNKNOWN; no validated denominator. The matching and permutation populations are explicitly defined finite local universes. Their fractions must not be reported as fractions of Conway-99 solved. No unrestricted branch is closed. Ledger population: {len(ledger['claims'])} claims, {record['verified_clear']} VERIFIED/CLEAR and2 CANDIDATE/CLEAR.

**Best result:** exact structural limits on two proposed core filters, complete finite local counts, and a139-node direct conditional proof. There is no full target witness, new general exclusion, or target-wide numerical bound.

**Problems:** the initial matching census completed its mathematical stages but failed while formatting output paths; its original artifacts and byte-identical corrected stages are preserved. The first permutation recount wrapper rejected a mismatched status string before counting; its corrected separately frozen version completed. Prior archive material already contains the related36-factor Gram mechanism, so no novelty claim or repeated exhaustive PSD search is made. Additional Q1 scouts and the new joint-factor encoding belong to the following wave and are outside these six claims.

**Execution:** the six recorded claims are complete and required no new SAT solver attempt. A fresh native-process observation at {observed} returned `{state}`. See its raw receipt for any separately running next-wave solver; this saved report is not a live status promise. The user's continuation instruction remains active.

**Next experiment:** solve the independently gated compact joint binary-incidence model for the fixed39core with both unknown factor blocks free, then independently check the raw factor or complete proof. This is broader than fixing one Q1 factor and remains conditional on the chosen core.

**References:** [source commit](https://github.com/ikuto32/conway-99-graph/commit/{source}), [draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3), [artifact catalog](../{B}eighth_artifact_packaging/catalog.json), [reproduction guide](REPRODUCING_20260930_EIGHTH_WAVE.md). PUBLIC pointers require exact immutable publication confirmation.
'''
    with(ROOT/'docs/RESEARCH_20260930_EIGHTH_WAVE.md').open('x',encoding='utf-8',newline='\n')as f:f.write(report)
    print(json.dumps({'timestamp':now,'claims':len(ledger['claims']),'verified_clear':record['verified_clear'],'native_observation':state,'target_resolution':'UNKNOWN'}))
if __name__=='__main__':main()
