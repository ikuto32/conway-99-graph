"""Generate wave29 report from registered claims and complete literal proof records."""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import argparse, hashlib, json, subprocess, sys, yaml

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'; N='acceleration/results/20261001_'
I=B+'independent_review/'; O=N+'resume/'
REG=[B+'twentyninth_initial_registration',N+'twentyninth_followup_registration']
OLD=B+'resume/twentyeighth_milestone_checkpoint.json'
BASE_PROOFS=[
('exact_eight_first12_proofs',12,'a47da7d0e2e70d61c51679477de5257c676a201e59cc8977b250ed75e8c05ef9'),
('exact_eight_next32_proofs',32,'21ee1b189c8b250eabcaedad43a79b9025978d540a1480f1c03eaeb446acee4c'),
('exact_eight_sizeclass16_proofs',16,'04d47a627081f42def048826f08bdf2574eff67479275d46112033bf994e4494'),
('exact_eight_next64_proofs',64,'7e2cab83b264a30e35a5797137b4948fb59d30e1b1b234ed5ab54e517c13881f')]

def need(value,message):
    if not value: raise ValueError(message)

def h(path):
    with (ROOT/path).open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()

def read(path): return json.loads((ROOT/path).read_bytes())

def save(path,value):
    with (ROOT/path).open('x',encoding='utf8',newline='\n') as f: json.dump(value,f,indent=2); f.write('\n')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--expected-ledger-sha256',required=True); args=ap.parse_args()
    raw=(ROOT/'CLAIMS.yaml').read_bytes(); need(hashlib.sha256(raw).hexdigest()==args.expected_ledger_sha256,'frozen current ledger')
    ledger=yaml.safe_load(raw); counts=Counter(c['status'] for c in ledger['claims'])
    need(len(ledger['claims'])==300 and counts==dict(VERIFIED=293,CANDIDATE=3,REFUTED=4),'registered300 population')
    evidence={}; ids=[]; prior=None; registration_chain=[]
    for directory in REG:
        r=read(directory+'/summary.json'); before=(ROOT/directory/'CLAIMS.before.yaml').read_bytes(); after=(ROOT/directory/'CLAIMS.after.yaml').read_bytes()
        need(hashlib.sha256(before).hexdigest()==r['previous_ledger_sha256'] and hashlib.sha256(after).hexdigest()==r['ledger_sha256'],'registration bytes')
        need(prior is None or prior==before,'continuous registration chain'); prior=after; ids.extend(r['new_claim_ids'])
        evidence[directory+'/summary.json']=h(directory+'/summary.json'); registration_chain.append(dict(directory=directory,summary_sha256=h(directory+'/summary.json')))
    need(prior==raw and len(ids)==len(set(ids))==6,'exact six registered additions')
    claims=[c for c in ledger['claims'] if c['id'] in ids]; artifacts={a['id']:a for a in ledger['artifacts']}
    need(all(c['status']=='VERIFIED' and c['review_state']=='CLEAR' for c in claims),'six current verified additions')
    for c in claims:
        for aid in c['evidence']:
            a=artifacts[aid]; need(h(a['path'])==a['sha256'],'claim evidence identity'); evidence[a['path']]=a['sha256']
    second=next(c for c in claims if c['id']=='C-FIXED-HADAMARD-EXACT-EIGHT-PREFIX64-BATCH02-LITERAL-PROFILE-EXCLUSIONS')
    second_art=artifacts[second['evidence'][0]]
    proof_inputs=[(name,I+name+'/summary.json',n,pin) for name,n,pin in BASE_PROOFS]+[('exact_eight_prefix64_batch02_proofs',second_art['path'],64,second_art['sha256'])]
    batches=[]; allids=[]
    manifest_path=B+'exact_eight_campaign_preparation/campaign_manifest.json'; need(h(manifest_path)=='e7b07ea2f7c6b9f6738641afc22779a503841d5ac3da58d3873ebb0fa4b784ba','frozen campaign manifest')
    universe={r['case_id']:r for r in read(manifest_path)['records']}; need(len(universe)==792,'manifest population')
    for name,p,n,pin in proof_inputs:
        need(h(p)==pin,'proof report identity'); q=read(p); rows=q['case_records']
        need(len(rows)==q['completed_proof_replays']==n and not q['pending_case_ids'] and q['UNKNOWN']==q.get('SAT_verified',q.get('SAT_pending'))==0,'complete literal outcomes')
        for r in rows:
            need(r['outcome']=='UNSAT_VERIFIED' and r['trace']['complete_proof'] and r['replay']['accepted'] and r['replay']['actual_exit_code']==0,'complete accepted replay')
            u=universe[r['case_id']]; need(u['full_count_profile_sha256']==r['full_count_profile_sha256'],'same literal raw identity'); allids.append(r['case_id'])
        need(q['proof_bytes']==sum(r['trace']['bytes'] for r in rows),'complete trace byte count')
        batches.append(dict(name=name,selected=n,attempted=n,completed=n,independent_complete_proof_replays=n,UNSAT=n,SAT=0,UNKNOWN=0,errors=0,proof_bytes=q['proof_bytes'],summary_path=p,summary_sha256=pin))
    need(len(allids)==len(set(allids))==188,'five disjoint literal populations')
    previous=read(OLD); need(previous['literal_campaign']['distinct_literal_exclusions']==60,'previous milestone count')
    need(set(previous['literal_campaign']['excluded_case_ids'])==set(allids[:60]),'same previous60 cases')
    gf3=read(I+'sizeclass16_gf3_affine_weights/summary.json'); need(gf3['cases']==16 and gf3['residue_entries']==20736 and gf3['affine_normalizations']==320,'exact GF3 witness counts')
    uniform_path=N+'exact_eight_uniform_gram/summary.json'; need(h(uniform_path)=='1b43daf9265afe524d2efb4f10ab0ee7cdf18b255bec47e8826e495db1898344','producer uniform diagnostic identity')
    uniform=read(uniform_path); need(uniform['population']==uniform['completed']==uniform['uniform_failures']==792 and uniform['uniform_witnesses']==0,'uniform diagnostic population')
    uniform_audit_path=N+'independent_review/exact_eight_uniform_gram/summary.json'; need(h(uniform_audit_path)=='c911f7a0d9156c12e91491061f96eb691e1f7d8360f862e5cf45bd7114cff38e','independent uniform counterexample report')
    uniform_audit=read(uniform_audit_path); need(uniform_audit['status']=='INDEPENDENT_EXACT_EIGHT_UNIFORM_GRAM_FAILURES_PASS' and uniform_audit['profiles']==uniform_audit['independent_nonzero_entries']==792 and uniform_audit['uniform_witnesses']==0 and uniform_audit['arbitrary_convex_feasibility']=='UNKNOWN','independent uniform-only scope')
    need(any(c['id']=='C-FIXED-HADAMARD-EXACT-EIGHT-UNIFORM-GRAM-MIXTURE-FAILURES' for c in claims),'independent uniform counterexample binding registered')
    now=datetime.now(timezone.utc).isoformat(); source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(); (ROOT/O).mkdir(exist_ok=True)
    command=['wsl.exe','--distribution','Ubuntu-24.04','--exec','/usr/bin/ps','-C','cadical','-o','pid,ppid,comm,pcpu,rss,args']; observed=datetime.now(timezone.utc).isoformat()
    p=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=15)
    state='CADICAL_PROCESS_OBSERVED' if p.returncode==0 else 'NO_CADICAL_PROCESS_OBSERVED' if p.returncode==1 and len(p.stdout.splitlines())<=1 else 'UNKNOWN_OBSERVATION_ERROR'
    for label,content in [('stdout',p.stdout),('stderr',p.stderr)]:
        with (ROOT/(O+'twentyninth_process_snapshot.'+label+'.log')).open('xb') as f: f.write(content)
    ci_command=['gh','run','list','--commit','fcc2347feb9728344f474a73dced33293e783d68','--limit','8','--json','databaseId,workflowName,status,conclusion,headSha,url']
    ci_observed=datetime.now(timezone.utc).isoformat(); ci=subprocess.run(ci_command,cwd=ROOT,capture_output=True,timeout=30)
    save(O+'twentyeighth_publication_ci_observation.json',dict(observed_at=ci_observed,command=ci_command,exit_code=ci.returncode,rows=json.loads(ci.stdout) if ci.returncode==0 else None,rows_null_reason=None if ci.returncode==0 else 'GitHub query failed; no inferred workflow state.',stderr=ci.stderr.decode(errors='replace'),scope='Actual wave28 publication commit workflows only; no claim about later unpushed work or mathematical verification.'))
    snapshot=O+'claims_at_twentyninth_milestone.yaml'; checkpoint=O+'twentyninth_milestone_checkpoint.json'
    with (ROOT/snapshot).open('xb') as f: f.write(raw)
    next_action='Build and independently audit the next explicitly allocated 64 unproved manifest cases, then run the gated native batch and replay every complete proof.'
    result=dict(timestamp=now,source_commit=source,writer_sha256=h(Path(__file__).relative_to(ROOT)),command=[sys.executable,*sys.argv],cwd=str(ROOT),previous_report='docs/RESEARCH_20260930_TWENTYEIGHTH_WAVE.md',previous_checkpoint_sha256=h(OLD),registration_chain=registration_chain,claim_population=len(ledger['claims']),claim_status_counts=dict(counts),claim_review_counts=dict(Counter(c['review_state'] for c in ledger['claims'])),new_verified_ids=ids,new_refuted_ids=[],new_candidate_ids=[],target_resolution='UNKNOWN',external_review=None,external_review_null_reason='No target-resolution artifact exists; no external review asserted.',ledger_snapshot_sha256=h(snapshot),evidence_sha256=evidence,literal_batches=batches,literal_campaign=dict(population=792,distinct_literal_exclusions=len(allids),unresolved=792-len(allids),new_literal_exclusions=len(allids)-60,excluded_case_ids=allids,scope='Five disjoint literal batches only; no unchecked labelled-image union inferred.'),gf3_witnesses=dict(profiles=gf3['cases'],residue_entries=gf3['residue_entries'],affine_normalizations=gf3['affine_normalizations'],rank_checked=False,scope='Witnesses over GF3 only; no integral factor.'),uniform_diagnostic=dict(profiles=792,uniform_witnesses=0,uniform_counterexamples=792,scope='Each profile has an independently checked differing entry. Unequal convex weights and LP infeasibility are not adjudicated.'),new_complete99_graphs=0,new_unrestricted_exclusions=0,new_whole_support_exclusions=0,coverage='Overall search coverage: UNKNOWN; no validated denominator.',best_result='Fixed-support lower bound of eight unbalanced groups unchanged; 188 literal canonical Gram cases excluded in the frozen792-case campaign.',next_experiment=next_action,excluded_future_cohort=['exact_eight_prefix64_batch03'],execution=dict(observed_at=observed,command=command,exit_code=p.returncode,state=state,scope='Targeted native-process observation only. Python and other process state UNKNOWN.',stdout_sha256=h(O+'twentyninth_process_snapshot.stdout.log'),stderr_sha256=h(O+'twentyninth_process_snapshot.stderr.log')))
    save(checkpoint,result)
    table='\n'.join('| '+c['id']+' r'+str(c['revision'])+' | '+c['scope']['description']+' [Evidence](../'+artifacts[c['evidence'][0]]['path']+'). |' for c in claims)
    report=f'''# Twenty-ninth research milestone, 2026-10-01

Six scoped claims are newly VERIFIED/CLEAR since the [previous milestone](RESEARCH_20260930_TWENTYEIGHTH_WAVE.md). Two new 64-case batches add 128 distinct literal exclusions with complete independently replayed proofs. The two algebraic diagnostics add no exclusions.

**As of:** {now}; source commit `{source}`; [checkpoint](../{checkpoint}); [frozen ledger](../{snapshot}). Commands, versions, raw artifacts and exact hashes are preserved in the linked reports.

**Verdict:** target resolution UNKNOWN. This repository has no independently validated 99-vertex target graph or general nonexistence proof. No target-resolution artifact is under external review. This is not a worldwide literature verdict. PR3 remains draft and unmerged.

**Verified changes:** all six additions are revision 1. Earlier claim records remain unchanged.

| Claim | Exact scope and evidence |
| --- | --- |
{table}

**Work completed:** each new batch selected 64 distinct cases, built all 64 formulas, completed 64 native attempts and passed 64 independent complete-proof replays. All 128 outcomes are UNSAT within their encoded literal scopes; there are zero SAT, UNKNOWN, errors or pending cases in these two completed batches. Their complete traces contain {sum(b['proof_bytes'] for b in batches[-2:]):,} bytes. The two new encoding audits reconstructed every raw clause and complete initial domain. Both batches used four separately allocated 16-case builds through the independently calibrated suspended-process launcher; finite launcher controls are not a universal operating-system guarantee.

The five checked literal batches have a disjoint union of 188 cases from the frozen 792-case campaign; 604 remain unresolved. The prior first-12 image union remains 72 explicitly checked labelled tables. No sixfold expansion is applied to the later cases, and historical overlapping exclusions are not added.

The GF(3) audit verifies explicit affine weights for 16 size-class representatives, checking 20,736 residues and 320 group normalizations. It does not verify the producer's rank claim or produce integral factors. The independent uniform-mixture audit checks a concrete differing Gram entry for every one of the 792 profiles. These are complete counterexamples to equal local weights, not complete matrix rechecks; unequal convex weights can still be possible.

**Coverage:** the ledger contains 300 claims: 293 VERIFIED/CLEAR, three CANDIDATE/CLEAR and four REFUTED/CLEAR. Overall search coverage: UNKNOWN; no validated denominator. The 188/792 literal-instance count does not measure fractions of graphs, computational difficulty or remaining runtime.

**Best result:** the prior fixed-support lower bound of eight unbalanced groups is unchanged. No whole-support or unrestricted nonexistence follows.

**Problems:** the affine witnesses and uniform counterexamples do not settle continuous or integral feasibility generally. Prior launcher counterexamples, failed preparations, missing historical artifacts and privacy omissions remain preserved. Later batch03 work is outside this cutoff.

**Execution:** all research runs counted in this checkpoint completed. Targeted native observation at {observed}: `{state}`. Other processes are outside that observation. This checkpoint does not stop research.

**Next experiment:** {next_action}

**References:** [source commit](https://github.com/ikuto32/conway-99-graph/commit/{source}), [draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3). Immutable evidence publication and recovery instructions follow packaging.
'''
    with (ROOT/'docs/RESEARCH_20261001_TWENTYNINTH_WAVE.md').open('x',encoding='utf8',newline='\n') as f: f.write(report)
    print(json.dumps(dict(checkpoint=checkpoint,sha256=h(checkpoint),claims=len(ledger['claims']),literal_exclusions=len(allids),execution=state)))

if __name__=='__main__': main()
