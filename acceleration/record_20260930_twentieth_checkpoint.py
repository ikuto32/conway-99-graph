"""Freeze twentieth claims and completed runs; no solver or ledger mutation."""
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
import hashlib,json,subprocess,sys,yaml
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';I=B+'independent_review/'
REG=[B+'twentieth_'+s+'_registration' for s in ['encoding','balanced_exclusion','margin']]
def h(p):
    with(ROOT/p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def save(p,obj):
    with(ROOT/p).open('x',encoding='utf8',newline='\n')as f:json.dump(obj,f,indent=2);f.write('\n')
def main():
    raw=(ROOT/'CLAIMS.yaml').read_bytes();ledger=yaml.safe_load(raw);artifacts={a['id']:a for a in ledger['artifacts']}
    ids=[cid for directory in REG for cid in read(directory+'/summary.json')['new_claim_ids']]
    claims=[c for cid in ids for c in ledger['claims'] if c['id']==cid]
    assert len(ids)==len(set(ids))==len(claims)==6 and len(ledger['claims'])==194
    assert all(c['review_state']=='CLEAR' and c['revision']==1 for c in claims)
    assert Counter(c['status']for c in claims)=={'VERIFIED':5,'REFUTED':1}
    assert (ROOT/REG[-1]/'CLAIMS.after.yaml').read_bytes()==raw
    proofpath=I+'hadamard_balanced_gram_unsat_v2/summary.json';proof=read(proofpath)
    transportpath=I+'hadamard_balanced_proof_packages/summary.json';transport=read(transportpath)
    assert proof['status']=='INDEPENDENT_FIXED_HADAMARD_BALANCED_GRAM_UNSAT_PASS'
    assert proof['proof']['complete_independent_replay'] and transport['status']=='INDEPENDENT_BALANCED_GRAM_PROOF_TRANSPORT_PASS'
    evidence={artifacts[aid]['path']for c in claims for aid in c['evidence']}
    evidence.update([proofpath,transportpath,B+'twentieth_packaging_preparation/summary.json',B+'hadamard_balanced_caps_cancellation/cancellation.json'])
    evidence.update(d+'/summary.json'for d in REG)
    now=datetime.now(timezone.utc).isoformat();source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    snapshot=B+'resume/claims_at_twentieth_milestone.yaml';checkpoint=B+'resume/twentieth_milestone_checkpoint.json';report='docs/RESEARCH_20260930_TWENTIETH_WAVE.md'
    for p in[snapshot,checkpoint,report]:assert not(ROOT/p).exists()
    command=['wsl.exe','-d','Ubuntu-24.04','--','ps','-C','cadical','-o','pid,etime,pcpu,rss,args']
    observed=datetime.now(timezone.utc).isoformat();process=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=15)
    state='CADICAL_PROCESS_OBSERVED'if process.returncode==0 else'NO_CADICAL_PROCESS_OBSERVED'if process.returncode==1 else'UNKNOWN_OBSERVATION_ERROR'
    for channel,content in[('stdout',process.stdout),('stderr',process.stderr)]:
        with(ROOT/(B+'resume/twentieth_process_snapshot.'+channel+'.log')).open('xb')as f:f.write(content)
    with(ROOT/snapshot).open('xb')as f:f.write(raw)
    statuses=Counter(c['status']for c in ledger['claims']);reviews=Counter(c['review_state']for c in ledger['claims'])
    assert statuses=={'VERIFIED':191,'CANDIDATE':2,'REFUTED':1}and reviews=={'CLEAR':194}
    next_action='Use full-Gram marginal identities to bound unbalanced groups, then enumerate exact local deviation profiles for the surviving four-group circuits and screen their compatibility before further native search.'
    record=dict(timestamp=now,source_commit=source,command=[sys.executable,*sys.argv],cwd=str(ROOT),
      previous_report='docs/RESEARCH_20260930_NINETEENTH_WAVE.md',previous_checkpoint_sha256=h(B+'resume/nineteenth_milestone_checkpoint.json'),
      claim_population=194,verified_clear=191,candidate_clear=2,refuted_clear=1,claim_status_counts=dict(statuses),claim_review_counts=dict(reviews),
      new_verified_ids=[c['id']for c in claims if c['status']=='VERIFIED'],new_refuted_ids=[c['id']for c in claims if c['status']=='REFUTED'],evidence_only_revision_changes=[],
      target_resolution='UNKNOWN',external_review=None,external_review_null_reason='No target resolution artifact exists.',
      native_attempts=dict(attempted=2,completed=2,sat=0,unsat=1,unknown=1,errors=0),
      balanced_encoding=dict(variables=10480,clauses=74200,groups=20,normalized_choices_per_group=150),
      balanced_proof=dict(raw_sha256=proof['proof']['sha256'],raw_bytes=proof['proof']['bytes'],complete_independent_replay=True,independent_gate=proofpath,native_conflicts=248698,native_wall_seconds=22.19),
      proof_transport=dict(parts=transport['parts'],compressed_bytes=transport['recovery']['compressed_bytes'],raw_bytes=transport['recovery']['raw_bytes'],independent_gate=transportpath),
      oriented_outcome=dict(status='UNKNOWN',conflicts=1000000,incomplete_trace_bytes=331620166,trace_availability='LOCAL_ONLY'),
      cancelled_cap_preparation=dict(build_completed=True,independent_encoding_approval=False,native_attempts=0),
      new_full_factors=0,complete99_graphs=0,new_whole_support_exclusions=0,new_core_exclusions=0,new_unrestricted_exclusions=0,
      new_balanced_fixed_support_family_exclusions=1,coverage='Overall search coverage: UNKNOWN; no validated denominator.',
      ledger_snapshot_sha256=h(snapshot),evidence_sha256={p:h(p)for p in sorted(evidence)},next_experiment=next_action,
      later_cohort='Few-exception and four-group circuit derivations and local-profile screening belong to wave21 and are excluded from this frozen ledger.',
      execution=dict(observed_at=observed,command=command,exit_code=process.returncode,state=state,stdout_sha256=h(B+'resume/twentieth_process_snapshot.stdout.log'),stderr_sha256=h(B+'resume/twentieth_process_snapshot.stderr.log'),scope='Fresh targeted native census; completed wave20 runs recorded separately.'))
    save(checkpoint,record)
    table='\n'.join('| '+c['status']+' | '+c['id']+' r1 | '+c['scope']['description']+' [Evidence](../'+artifacts[c['evidence'][0]]['path']+'). |'for c in claims)
    text=f'''# Twentieth resumed milestone, 2026-09-30 JST

Five verified claims and one refuted claim were added since the [nineteenth milestone](RESEARCH_20260930_NINETEENTH_WAVE.md). A complete independently replayed proof excludes all balanced factors on the fixed six-prism support. Unbalanced factors and Conway-99 remain unresolved.

**As of:** {now}; source commit {source}. [Checkpoint](../{checkpoint}), [frozen ledger](../{snapshot}); previous report: nineteenth milestone.

**Verdict:** target resolution UNKNOWN. This repository has no independently validated target graph or general nonexistence proof. No target-resolution artifact is under external review. This is not a worldwide literature verdict; draft PR3 remains unmerged.

**Claim and verification changes:**

| Status | Claim | Exact scope and evidence |
| --- | --- | --- |
{table}

**Work completed:** two distinct native instances were attempted and completed: one oriented projection ended UNKNOWN at 1,000,000 conflicts, and one full balanced-Gram formula returned UNSAT after 248,698 conflicts. The latter has 10,480 variables and 74,200 clauses covering all 150 normalized local choices per group, including constants and mixed choices. Its complete 227,098,316-byte trace passed independent DRAT checking. Six public-size compressed parts recover exactly those bytes; an independent transport check verified the full stream, literal original comparison and ten corrupted controls. The capped extension was built but never independently approved or searched.

**Coverage:** exactly one balanced fixed-support family is newly excluded. Zero new whole-support, core or unrestricted exclusions. Overall search coverage: UNKNOWN; no validated denominator. The ledger contains194 claims:191 VERIFIED/CLEAR,2 CANDIDATE/CLEAR and1 REFUTED/CLEAR. Claim counts do not measure target coverage.

**Best result:** exact nonexistence of balanced binary36×60 factors with this literal support and prescribed integer Gram, without assuming outside-column caps. The three-column balance restriction is essential to the recorded scope.

**Problems:** the oriented result is UNKNOWN and its incomplete trace remains LOCAL_ONLY. The first encoding checker used an incorrect channel-count assumption; the first proof wrapper misparsed portability-patch context. Both original failures and corrected checkers are preserved. A guessed support-intersection restriction is refuted by a size-two intersection. The private broad process snapshot is omitted from public payloads; a narrow observation and hash-only availability record are retained. Four older learned traces remain MISSING; no proof depends on them.

**Execution:** both wave20 native calls and proof replay completed. Targeted census at {observed}: {state}. Later wave21 mathematical work has separate records. This checkpoint does not assert continuing native execution.

**Next experiment:** {next_action}

**References:** [source commit](https://github.com/ikuto32/conway-99-graph/commit/{source}), [draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3), [catalog](../{B}twentieth_artifact_packaging/catalog.json), [replay guide](REPRODUCING_20260930_TWENTIETH_WAVE.md). Immutable publication pointers follow remote confirmation.
'''
    with(ROOT/report).open('x',encoding='utf8',newline='\n')as f:f.write(text)
    print(json.dumps(dict(checkpoint=checkpoint,sha256=h(checkpoint),claim_population=194,verified_clear=191,execution=state)))
if __name__=='__main__':main()

