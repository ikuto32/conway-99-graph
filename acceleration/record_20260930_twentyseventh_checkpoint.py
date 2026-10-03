"""Freeze wave27's eight scoped verified additions; later batches stay separate."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import hashlib,json,subprocess,sys,yaml
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';I=B+'independent_review/'
REG=[B+'twentyseventh_'+s for s in ['pilot_registration','psd_candidate_registration','campaign_gates_registration','psd_promotion','first12_proof_registration','inventory_registration']]
def sha(p):
    with(ROOT/p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def save(p,x):
    with(ROOT/p).open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def main():
    raw=(ROOT/'CLAIMS.yaml').read_bytes();assert hashlib.sha256(raw).hexdigest()=='5ea04f21e5964b6f987d00a600a69d4472bfebdd0fea7f564e4dfec1af5cb237'
    ledger=yaml.safe_load(raw);counts=Counter(c['status']for c in ledger['claims']);assert len(ledger['claims'])==286 and counts==dict(VERIFIED=281,CANDIDATE=3,REFUTED=2)
    previous=None;ids=[];evidence=set()
    for d in REG:
        r=read(d+'/summary.json');before=(ROOT/d/'CLAIMS.before.yaml').read_bytes();after=(ROOT/d/'CLAIMS.after.yaml').read_bytes()
        assert hashlib.sha256(before).hexdigest()==r['previous_ledger_sha256'] and hashlib.sha256(after).hexdigest()==r['ledger_sha256']
        assert previous is None or previous==before
        previous=after;ids+=r.get('new_claim_ids',[]);evidence.add(d+'/summary.json')
    assert previous==raw and len(ids)==len(set(ids))==8
    claims=[c for c in ledger['claims']if c['id']in ids];assert all(c['status']=='VERIFIED'and c['review_state']=='CLEAR'for c in claims)
    artifacts={a['id']:a for a in ledger['artifacts']}
    for c in claims:
        for aid in c['evidence']:
            a=artifacts[aid];assert sha(a['path'])==a['sha256'];evidence.add(a['path'])
    proof=read(I+'exact_eight_first12_proofs/summary.json');assert proof['status']=='INDEPENDENT_EXACT_EIGHT_FIRST12_LITERAL_PROOFS_PASS'
    prs=proof['case_records'];assert len(prs)==12 and len({r['case_id']for r in prs})==12 and all(r['outcome']=='UNSAT_VERIFIED'for r in prs)
    psd=read(I+'exact_eight_psd_screen/summary.json');inventory=read(I+'exact_eight_campaign_inventory/summary.json')
    assert inventory['cases']==792 and inventory['initial_domains']==15840 and inventory['actual_formula_measurements']==16
    now=datetime.now(timezone.utc).isoformat();source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    cmd=['wsl.exe','--distribution','Ubuntu-24.04','--exec','/usr/bin/ps','-C','cadical','-o','pid,ppid,comm,pcpu,rss,args'];observed=datetime.now(timezone.utc).isoformat();p=subprocess.run(cmd,cwd=ROOT,capture_output=True,timeout=15)
    state='CADICAL_PROCESS_OBSERVED'if p.returncode==0 else'NO_CADICAL_PROCESS_OBSERVED'if p.returncode==1 and len(p.stdout.splitlines())<=1 else'UNKNOWN_OBSERVATION_ERROR'
    for name,value in [('stdout',p.stdout),('stderr',p.stderr)]:
        with(ROOT/(B+'resume/twentyseventh_process_snapshot.'+name+'.log')).open('xb')as f:f.write(value)
    snapshot=B+'resume/claims_at_twentyseventh_milestone.yaml';checkpoint=B+'resume/twentyseventh_milestone_checkpoint.json'
    with(ROOT/snapshot).open('xb')as f:f.write(raw)
    next_action='Build and independently reconstruct the next32 explicitly selected unresolved literal Gram instances, then run the gated bounded native batch and independently check every outcome.'
    result=dict(timestamp=now,source_commit=source,writer_sha256=sha(Path(__file__).relative_to(ROOT)),command=[sys.executable,*sys.argv],cwd=str(ROOT),previous_report='docs/RESEARCH_20260930_TWENTYSIXTH_WAVE_CORRECTED.md',previous_checkpoint_sha256=sha(B+'resume/twentysixth_milestone_checkpoint.json'),claim_population=286,claim_status_counts=dict(counts),claim_review_counts=dict(Counter(c['review_state']for c in ledger['claims'])),new_verified_ids=ids,new_candidate_ids=[],new_refuted_ids=[],promoted_revisions={'C-FIXED-HADAMARD-EXACT-EIGHT-SURVIVOR-PSD-SCREEN':{'from':1,'to':2}},target_resolution='UNKNOWN',external_review=None,external_review_null_reason='No target-resolution artifact exists; no external review asserted.',ledger_snapshot_sha256=sha(snapshot),evidence_sha256={q:sha(q)for q in sorted(evidence)},literal_campaign=dict(selected=12,attempted=12,completed=12,UNSAT=12,UNKNOWN=0,SAT=0,errors=0,complete_independent_proof_replays=12,proof_bytes=56815018,distinct_literal_cases=12,overlap_with_preceding_single_pilot=1,additional_beyond_single_pilot=11,scope='Literal full-Gram instances only. No orbit or historical-profile union exclusion is inferred.'),psd=dict(canonical_profiles=792,PSD=792,rank=22,excluded=0,exact_arithmetic='rational certificates independently checked by integer congruences'),inventory=dict(canonical_profiles=792,initial_domains=15840,size_classes=16,actual_saved_formulas=16,actual_campaign_formulas=12,historical_formula_controls=4,unbuilt_dimensions='Conditional recipe estimates only'),new_complete99_graphs=0,new_unrestricted_exclusions=0,new_whole_support_exclusions=0,coverage='Overall search coverage: UNKNOWN; no validated denominator.',best_result='Prior fixed-support lower bound of eight unbalanced groups unchanged; twelve distinct canonical literal Gram instances now independently excluded in the campaign.',next_experiment=next_action,excluded_future_cohort=['exact_eight_next32','first12_orbit_union'],execution=dict(observed_at=observed,command=cmd,exit_code=p.returncode,state=state,scope='Fresh native-process observation only. Python/other process state UNKNOWN in this checkpoint; later batch work is outside the frozen milestone.',stdout_sha256=sha(B+'resume/twentyseventh_process_snapshot.stdout.log'),stderr_sha256=sha(B+'resume/twentyseventh_process_snapshot.stderr.log')))
    save(checkpoint,result)
    table='\n'.join('| '+c['id']+' r'+str(c['revision'])+' | '+c['scope']['description']+' [Evidence](../'+artifacts[c['evidence'][0]]['path']+'). |'for c in claims)
    report=f'''# Twenty-seventh research milestone, 2026-09-30

Eight scoped claims are newly VERIFIED/CLEAR since the [corrected twenty-sixth report](RESEARCH_20260930_TWENTYSIXTH_WAVE_CORRECTED.md). The first12 literal campaign instances have complete independently replayed UNSAT proofs. All792 canonical count survivors pass the exact PSD test, so that test supplies no further exclusion.

**As of:** {now}; source commit {source}; [checkpoint](../{checkpoint}), [frozen ledger](../{snapshot}). Actual commands, environment and source hashes remain in each run record.

**Verdict:** target resolution UNKNOWN. This repository has no independently validated99-vertex target graph or general nonexistence proof. No target-resolution artifact is under external review. This is not a worldwide literature verdict. PR3 remains draft and unmerged.

**Verified changes:** PSD screening was first registered CANDIDATE at revision1 and promoted only after independent checking at revision2. The seven other new claims are revision1.

| Claim | Exact scope and evidence |
| --- | --- |
{table}

**Work completed:** the first12 campaign selected12 distinct canonical count tables and completed12 native attempts:12 UNSAT, zero SAT, UNKNOWN or errors. All56,815,018 proof bytes are retained and all12 complete proofs passed independent replay. Case0 repeats the preceding single literal pilot, yielding11 additional distinct exclusions beyond that pilot. No historical orbit exclusions are added without a checked union. The preceding single pilot and the batch overlap and must not be summed as13 distinct cases.

Independent exact PSD checking covers all792 canonical scalar/block survivors. Every matrix R=3G-NN^T is positive semidefinite of rank22 over the rationals; no profile is excluded and no factor is established. This expands the previous three-profile PSD test to the complete792 survivor population. The separately checked kernel-option redundancy concerns only three historical profiles: it removes zero of their6,444 initial options and is not promoted to all792 profiles.

The full campaign coverage audit checks792 canonical tables and4,752 distinct global-fibre images, including complete local-domain transport. It supplies a conditional relabelling argument, not an exclusion by itself. The independent inventory checks15,840 initial domains across all792 profiles and identifies16 selector-size classes. Formula dimensions for unbuilt cases are conditional recipe estimates. The12 saved campaign formulas and four historical controls have actual measured dimensions; these populations overlap other experiments and are not added as new scientific cases.

**Coverage:**286 ledger claims:281 VERIFIED/CLEAR, three CANDIDATE/CLEAR, two REFUTED/CLEAR. Overall search coverage: UNKNOWN; no validated denominator. No whole-support or unrestricted exclusion was added.

**Best result:** the prior fixed-support lower bound of eight unbalanced groups is unchanged. Twelve literal canonical cases in the frozen792-case Gram campaign are excluded. This is a count of instances, not equal fractions of graphs, difficulty or time remaining.

**Problems:** PSD positivity and the three-profile kernel test provide no additional obstruction. Initial inventory and fibre-coverage checker preparations omitted the local Gram bound in a reconstructed catalogue; both failed before approval. Their original sources/failures remain, and fresh corrected versions use the full predicate and reject cap-only extras. A native driver control exposed a status-label problem; the failed preparation, correction setup failure and fresh v2 are preserved. No failed attempt is a nonexistence proof. Earlier unavailable artifacts and privacy omissions remain as previously recorded.

**Execution:** the single pilot, first12 batch and all audits counted here completed. Targeted native observation at {observed}: {state}. Next32 preparation and the first12 orbit-union audit are later-wave work, outside these counts. This milestone does not stop research.

**Next experiment:** {next_action}

**References:** [source commit](https://github.com/ikuto32/conway-99-graph/commit/{source}), [draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3). Evidence links above lead to full reports and bound artifacts; immutable publication and replay instructions follow packaging.
'''
    with(ROOT/'docs/RESEARCH_20260930_TWENTYSEVENTH_WAVE.md').open('x',encoding='utf8',newline='\n')as f:f.write(report)
    print(json.dumps(dict(checkpoint=checkpoint,sha256=sha(checkpoint),claim_population=286,execution=state)))
if __name__=='__main__':main()
