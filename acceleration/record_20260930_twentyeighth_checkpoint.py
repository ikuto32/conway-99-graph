"""Freeze six scoped verified additions and two unused-launcher refutations."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import hashlib,json,subprocess,sys,yaml
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';I=B+'independent_review/'
REG=[B+'twentyeighth_'+s for s in ['initial_registration','kernel_sizeclass_registration','sizeclass_proof_registration','launcher_refutation_registration']]
def h(p):
    with(ROOT/p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def save(p,x):
    with(ROOT/p).open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def main():
    raw=(ROOT/'CLAIMS.yaml').read_bytes();assert hashlib.sha256(raw).hexdigest()=='c2889537ea68b90736a5d51e13b6aafd6163b9a1e98d2f05eb1bd6e4331cf441'
    ledger=yaml.safe_load(raw);counts=Counter(c['status']for c in ledger['claims']);assert len(ledger['claims'])==294 and counts==dict(VERIFIED=287,CANDIDATE=3,REFUTED=4)
    previous=None;ids=[];evidence=set()
    for d in REG:
        r=read(d+'/summary.json');before=(ROOT/d/'CLAIMS.before.yaml').read_bytes();after=(ROOT/d/'CLAIMS.after.yaml').read_bytes()
        assert hashlib.sha256(before).hexdigest()==r['previous_ledger_sha256']and hashlib.sha256(after).hexdigest()==r['ledger_sha256']
        assert previous is None or previous==before;previous=after;ids+=r['new_claim_ids'];evidence.add(d+'/summary.json')
    assert previous==raw and len(ids)==len(set(ids))==8
    claims=[c for c in ledger['claims']if c['id']in ids];assert Counter((c['status'],c['review_state'])for c in claims)=={('VERIFIED','CLEAR'):6,('REFUTED','CLEAR'):2}
    artifacts={a['id']:a for a in ledger['artifacts']}
    for c in claims:
        for aid in c['evidence']:
            a=artifacts[aid];assert h(a['path'])==a['sha256'];evidence.add(a['path'])
    batches=[];caseids=[]
    for name,n in [('exact_eight_first12_proofs',12),('exact_eight_next32_proofs',32),('exact_eight_sizeclass16_proofs',16)]:
        p=I+name+'/summary.json';q=read(p);rs=q['case_records'];assert len(rs)==q['completed_proof_replays']==n and all(r['outcome']=='UNSAT_VERIFIED'for r in rs)
        assert not q['pending_case_ids']and not q['UNKNOWN']and not q.get('SAT_verified',q.get('SAT_pending'));caseids += [r['case_id']for r in rs]
        batches.append(dict(name=name,selected=n,attempted=n,completed=n,UNSAT=n,SAT=0,UNKNOWN=0,errors=0,independent_complete_proof_replays=n,proof_bytes=q['proof_bytes'],summary_path=p,summary_sha256=h(p)))
    assert len(caseids)==len(set(caseids))==60
    union=read(I+'exact_eight_first12_union_v2/summary.json');kernel=read(I+'exact_eight_kernel_redundancy/summary.json')
    assert union['canonical_profiles_excluded']==12 and union['labelled_profiles_excluded']==72 and kernel['profiles']==792 and kernel['initial_options']==1687356 and kernel['removed_options']==0
    now=datetime.now(timezone.utc).isoformat();source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    cmd=['wsl.exe','--distribution','Ubuntu-24.04','--exec','/usr/bin/ps','-C','cadical','-o','pid,ppid,comm,pcpu,rss,args'];observed=datetime.now(timezone.utc).isoformat();p=subprocess.run(cmd,cwd=ROOT,capture_output=True,timeout=15)
    state='CADICAL_PROCESS_OBSERVED'if p.returncode==0 else'NO_CADICAL_PROCESS_OBSERVED'if p.returncode==1 and len(p.stdout.splitlines())<=1 else'UNKNOWN_OBSERVATION_ERROR'
    for name,value in [('stdout',p.stdout),('stderr',p.stderr)]:
        with(ROOT/(B+'resume/twentyeighth_process_snapshot.'+name+'.log')).open('xb')as f:f.write(value)
    snapshot=B+'resume/claims_at_twentyeighth_milestone.yaml';checkpoint=B+'resume/twentyeighth_milestone_checkpoint.json'
    with(ROOT/snapshot).open('xb')as f:f.write(raw)
    next_action='Use the independently calibrated suspended-launch wrapper to build the frozen next64 selection, reconstruct every formula independently, then run and independently check the gated native batch.'
    result=dict(timestamp=now,source_commit=source,writer_sha256=h(Path(__file__).relative_to(ROOT)),command=[sys.executable,*sys.argv],cwd=str(ROOT),previous_report='docs/RESEARCH_20260930_TWENTYSEVENTH_WAVE.md',previous_checkpoint_sha256=h(B+'resume/twentyseventh_milestone_checkpoint.json'),registration_chain=REG,claim_population=len(ledger['claims']),claim_status_counts=dict(counts),claim_review_counts=dict(Counter(c['review_state']for c in ledger['claims'])),new_verified_ids=[c['id']for c in claims if c['status']=='VERIFIED'],new_refuted_ids=[c['id']for c in claims if c['status']=='REFUTED'],new_candidate_ids=[],target_resolution='UNKNOWN',external_review=None,external_review_null_reason='No target-resolution artifact exists; no external review asserted.',ledger_snapshot_sha256=h(snapshot),evidence_sha256={q:h(q)for q in sorted(evidence)},literal_batches=batches,literal_campaign=dict(population=792,distinct_literal_exclusions=60,unresolved=732,new_literal_exclusions=48,excluded_case_ids=caseids,scope='Three disjoint literal batches only. No unreviewed orbit union is inferred.'),first12_fibre_union=dict(canonical_cases=12,distinct_labelled_images=72,new_DRAT_replays=0,overlap_with_prior_pilot=1,scope='Checked first12 six-image union only; the later48 literal cases are not included in this orbit count.'),common_kernel=dict(profiles=792,kernel_dimension=14,initial_options=1687356,removed_options=0,scope='Exact residual-kernel and local-projection diagnostic on these792 tables only.'),new_complete99_graphs=0,new_unrestricted_exclusions=0,new_whole_support_exclusions=0,coverage='Overall search coverage: UNKNOWN; no validated denominator.',best_result='Prior fixed-support lower bound of eight unbalanced groups unchanged;60 distinct canonical literal Gram cases excluded in the frozen792-case campaign.',next_experiment=next_action,excluded_future_cohort=['exact_eight_next64','four_chunk_suspended_launcher'],execution=dict(observed_at=observed,command=cmd,exit_code=p.returncode,state=state,scope='Fresh native-process observation only. Python/other process state UNKNOWN; next64 preparation is outside the frozen milestone.',stdout_sha256=h(B+'resume/twentyeighth_process_snapshot.stdout.log'),stderr_sha256=h(B+'resume/twentyeighth_process_snapshot.stderr.log')))
    save(checkpoint,result)
    table='\n'.join('| '+c['id']+' r'+str(c['revision'])+' | '+c['status']+' | '+c['scope']['description']+' [Evidence](../'+artifacts[c['evidence'][0]]['path']+'). |'for c in claims)
    report=f'''# Twenty-eighth research milestone, 2026-09-30

Six scoped claims are newly VERIFIED/CLEAR and two unused-launcher guarantees are REFUTED/CLEAR since the [twenty-seventh report](RESEARCH_20260930_TWENTYSEVENTH_WAVE.md). The next32 and sizeclass16 literal batches add48 distinct exclusions, each supported by a complete independently replayed proof.

**As of:** {now}; source commit {source}; [checkpoint](../{checkpoint}), [frozen ledger](../{snapshot}). Full commands, hashes, versions and controls remain in the bound run records.

**Verdict:** target resolution UNKNOWN. This repository has no independently validated99-vertex target graph or general nonexistence proof. No target-resolution artifact is under external review. This is not a worldwide literature verdict. PR3 remains draft and unmerged.

**Claim changes:** all eight additions are revision1; earlier claim statements and verification records remain unchanged.

| Claim | Status | Exact scope and evidence |
| --- | --- | --- |
{table}

**Work completed:** next32 selected32 distinct cases, completed32 native attempts and32 full independent proof replays; sizeclass16 selected16 different cases, completed16 native attempts and16 full independent proof replays. Both batches have zero SAT, UNKNOWN, errors or pending cases. Their complete traces contain105,031,599 and37,502,220 bytes respectively. The sizeclass selection samples one member from each of16 domain-size classes; it excludes those literal members only. The initial next32 build completed22 formulas within its allocation, then a separately authorized ten-case continuation completed the remaining formulas. The original partial record is preserved.

Together with the preceding first12 batch, the checked disjoint literal union contains60 of the frozen792 canonical campaign cases;732 remain unresolved. The separate first12 fibre-union audit establishes72 distinct labelled count-table exclusions from twelve disjoint six-image orbits. It authenticates the prior complete proofs and checked domain transports without repeating DRAT replay. The later48 literal cases are not included in that image-union count, and historical exclusions are not added without a checked union.

The complete792 common-kernel audit establishes the same14-dimensional residual kernel for every table, using the prior exact rank22 certificates and independent integer annihilation checks. The associated necessary local-projection test removes zero of1,687,356 initial options. This diagnostic supplies no new factor or exclusion.

**Coverage:**294 ledger claims:287 VERIFIED/CLEAR, three CANDIDATE/CLEAR and four REFUTED/CLEAR. Overall search coverage: UNKNOWN; no validated denominator. The60/792 count is a frozen literal-instance population, not equal fractions of graphs, computational difficulty or time remaining.

**Best result:** the prior fixed-support lower bound of eight unbalanced groups is unchanged. Sixty literal canonical Gram cases are excluded; neither whole-support nonexistence nor unrestricted nonexistence follows.

**Problems:** the unused parallel v1 scheduler can delay another child's deadline cancellation during blocking cleanup. Its Popen-then-Job-assignment protocol also permits a real pre-assignment interpreter to remain outside the Job; a harmless controlled tree demonstrated continued descendant writes after Job termination. Every owned test process was cleaned up. These refutations concern exact engineering guarantees, not escaped historical research runs or invalid mathematical proofs. Earlier finite backend successes remain evidence but never establish universal containment. Failed selector, sidecar-binding, union and registration preparations are preserved with fresh corrected versions; missing keys and invalid preparations are not mathematical refutations. Earlier artifact/privacy limitations remain recorded.

**Execution:** all research batches and mathematical audits counted here completed. Targeted native observation at {observed}: {state}. Next64 selection and replacement suspended-launch preparation are outside this checkpoint. This milestone does not stop research.

**Next experiment:** {next_action}

**References:** [source commit](https://github.com/ikuto32/conway-99-graph/commit/{source}), [draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3). Immutable evidence publication and replay instructions follow packaging.
'''
    with(ROOT/'docs/RESEARCH_20260930_TWENTYEIGHTH_WAVE.md').open('x',encoding='utf8',newline='\n')as f:f.write(report)
    print(json.dumps(dict(checkpoint=checkpoint,sha256=h(checkpoint),claim_population=294,execution=state)))
if __name__=='__main__':main()
