"""Independent wave17 ledger/report coherence; no producer execution."""
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import argparse, hashlib, json, platform, re, subprocess, sys
from audit_20260930_sixteenth_checkpoint import read_ledger, require, sha, write

ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';I=B+'independent_review/'
GEN='acceleration/record_20260930_seventeenth_checkpoint.py'

def counts(cp,ledger,ids,proof,outcome,census):
    require(cp['claim_population']==len(ledger['claims'])==171,'claim population')
    require(cp['claim_status_counts']==dict(Counter(c['status'] for c in ledger['claims']))=={'VERIFIED':169,'CANDIDATE':2},'status counts')
    require(cp['claim_review_counts']=={'CLEAR':171} and cp['verified_clear']==169 and cp['candidate_clear']==2,'clear counts')
    require(cp['new_verified_ids']==ids and len(ids)==len(set(ids))==6 and cp['evidence_only_revision_changes']==[],'six new revision1 claims')
    require(cp['target_resolution']=='UNKNOWN' and cp['external_review'] is None and cp['coverage']=='Overall search coverage: UNKNOWN; no validated denominator.','target scope')
    for k in ['new_full_factors','complete99_graphs','new_whole_support_exclusions','new_core_exclusions','new_unrestricted_exclusions']:require(cp[k]==0,'no scope inflation '+k)
    n=cp['native'];require([n[k] for k in ['distinct_models','attempts','completed_attempts','SAT','UNSAT','UNKNOWN','checked_complete_proofs']]==[2,2,2,0,1,1,1],'two native outcomes')
    require(n['cyclic']==proof['native_outcome'] and n['cyclic_proof']==proof['proof'],'restricted proof identity')
    require(n['broader']==outcome['outcome'] and n['broader_trace']==outcome['trace'],'broader UNKNOWN identity')
    require(cp['projection']==census['counts'],'exact complete projection counts')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['precheck','final']);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={}
    def pin(p,h=None):
        v=sha(ROOT/p);require(h is None or h==v,'hash '+p);pins[p]=v;return v
    def load(p,h=None):pin(p,h);return json.loads((ROOT/p).read_bytes())
    try:
        ids=[];chain=[];last=None
        for name in ['cyclic','model_projection']:
            prefix=B+'seventeenth_'+name+'_registration/';r=load(prefix+'summary.json')
            before=prefix+'CLAIMS.before.yaml';after=prefix+'CLAIMS.after.yaml'
            pin(before,r['previous_ledger_sha256']);pin(after,r['ledger_sha256'])
            old,new=read_ledger(ROOT/before),read_ledger(ROOT/after)
            if last is not None:require((ROOT/before).read_bytes()==last,'continuous registration chain')
            last=(ROOT/after).read_bytes();aa={c['id']:c for c in old['claims']};bb={c['id']:c for c in new['claims']}
            require(all(bb[k]==v for k,v in aa.items()),'existing claim records unchanged')
            added=[c['id'] for c in new['claims'] if c['id'] not in aa];require(added==r['new_claim_ids'],'exact additions')
            require(r['registrar_performs_mathematical_verification'] is False,'registrar not verifier')
            ids+=added;chain.append(dict(name=name,before_sha256=sha(ROOT/before),after_sha256=sha(ROOT/after),added=added))
        ledger=new;claims={c['id']:c for c in ledger['claims']};arts={x['id']:x for x in ledger['artifacts']}
        for cid in ids:
            c=claims[cid];require(c['revision']==1 and c['status']=='VERIFIED' and c['review_state']=='CLEAR' and c['scope']['target_resolution']=='NONE','scoped verified claim')
            for d in c['dependencies']:require(d['id'] in claims and claims[d['id']]['revision']==d['revision'],'dependency revision')
            for eid in c['evidence']:pin(arts[eid]['path'],arts[eid]['sha256'])
            for v in c['verification']:
                require(v['claim_revision']==1 and v['outcome']=='PASS','claim revision check')
                for eid,h in v['artifact_hashes'].items():require(arts[eid]['sha256']==h,'verification binding')
        proof=load(I+'hadamard_cyclic_unsat/summary.json','83029350b25523c015dfe916d8056324c0970021d2b024d68941dd41fb8c2b70')
        unknown=load(I+'hadamard_prism_ordered_native_outcome/summary.json')
        census=load(I+'hadamard_triplicate_counts_v2/summary.json','cb9f1c7f8cfe0db557f554ded5427a9cba46dda10dcd9b5df9968e1d3b776f88')
        encoding=load(I+'hadamard_prism_ordered_cnf/summary.json')
        require(proof['proof']['complete_independent_replay'] and proof['native_outcome']['result']=='UNSAT' and proof['proof']['bytes']==29697087,'one complete scoped proof')
        require((proof['variables'],proof['clauses'])==(26360,122394),'cyclic encoding counts')
        require(unknown['outcome']['recorded_outcome']=='UNKNOWN_GNU_TIMEOUT_SIGTERM' and unknown['outcome']['observed_final_conflicts']==525037 and unknown['outcome']['wrapper_exit_code']==124,'broader timeout')
        require(unknown['trace']['bytes']==350457856 and not unknown['trace']['complete_independent_UNSAT_replay'],'partial trace not proof')
        require([encoding['counts'][k] for k in ['variables','clauses','ordered_suffix_clauses']]==[595464,3336642,163800],'broader encoding counts')
        require(census['counts']==dict(local_universe=117480,local_survivors=31110,balanced=150,cyclic=30,marginal_cases=12,ranks=[6]*12,separate_local_witnesses=120),'finite census scope')
        for name,exit_code in [('hadamard_cyclic_native_pilot',20),('hadamard_prism_ordered_native_pilot',124)]:
            run=load(B+name+'/summary.json');require(run['research_calls']==1 and run['actual_exit_code']==exit_code,'one actual call per model')
            receipt=run['receipt']
            for channel in ['stdout','stderr']:pin(receipt[channel],receipt[channel+'_sha256'])
            log=(ROOT/receipt['stdout']).read_text()
            if exit_code==20:require(re.search(r'^s UNSATISFIABLE$',log,re.M) is not None,'native UNSAT text')
            else:require(not re.search(r'^s (?:SATISFIABLE|UNSATISFIABLE)$',log,re.M),'no decisive broader result')
        pin(GEN);template=(ROOT/GEN).read_text()
        require("ap.add_argument('--next-experiment',required=True)" in template,'next action is explicit runtime input')
        cp=dict(claim_population=171,claim_status_counts={'VERIFIED':169,'CANDIDATE':2},claim_review_counts={'CLEAR':171},verified_clear=169,candidate_clear=2,new_verified_ids=ids,evidence_only_revision_changes=[],target_resolution='UNKNOWN',external_review=None,coverage='Overall search coverage: UNKNOWN; no validated denominator.',new_full_factors=0,complete99_graphs=0,new_whole_support_exclusions=0,new_core_exclusions=0,new_unrestricted_exclusions=0,native=dict(distinct_models=2,attempts=2,completed_attempts=2,SAT=0,UNSAT=1,UNKNOWN=1,checked_complete_proofs=1,cyclic=proof['native_outcome'],cyclic_proof=proof['proof'],broader=unknown['outcome'],broader_trace=unknown['trace']),projection=census['counts'])
        counts(cp,ledger,ids,proof,unknown,census);controls=[]
        for label,path,value in [('claim_count',['claim_population'],172),('support_exclusion',['new_whole_support_exclusions'],1),('two_proofs',['native','checked_complete_proofs'],2),('SAT',['native','SAT'],1),('all_balanced',['projection','balanced'],31110),('global_witness',['new_full_factors'],1)]:
            bad=deepcopy(cp);p=bad
            for k in path[:-1]:p=p[k]
            p[path[-1]]=value
            try:counts(bad,ledger,ids,proof,unknown,census)
            except ValueError:controls.append(label)
            else:raise ValueError('bad control accepted '+label)
        final=None
        if a.mode=='final':
            path=B+'resume/seventeenth_milestone_checkpoint.json';cp=load(path);counts(cp,ledger,ids,proof,unknown,census)
            snap=B+'resume/claims_at_seventeenth_milestone.yaml';pin(snap,cp['ledger_snapshot_sha256']);require((ROOT/snap).read_bytes()==last,'frozen final ledger bytes')
            for p,h in cp['evidence_sha256'].items():pin(p,h)
            previous=load(B+'resume/sixteenth_milestone_checkpoint.json',cp['previous_checkpoint_sha256']);require(previous['claim_population']==165,'previous cohort')
            reportpath='docs/RESEARCH_20260930_SEVENTEENTH_WAVE.md';pin(reportpath);report=(ROOT/reportpath).read_text()
            for cid in ids:require(report.count('`'+cid+'`')==1 and claims[cid]['scope']['description'] in report,'exact table scope')
            for token in ['171 claims: 169 VERIFIED/CLEAR and 2 CANDIDATE/CLEAR','26,360','122,394','29,697,087','595,464','3,336,642','163,800','525,037','350,457,856','117,480','31,110','150','120 separately checked','one cyclic subclass excluded; zero new whole-support','Whether full Gram feasibility forces balanced triplets remains UNKNOWN.']:
                require(token in report,'report token '+token)
            require(cp['next_experiment'] in report and cp['timestamp'] in report and cp['source_commit'] in report,'report provenance/explicit next action')
            require(cp['command'][1]==GEN and '--next-experiment' in cp['command'],'actual recorder invocation')
            ex=cp['execution'];logs={}
            for channel in ['stdout','stderr']:
                p=B+'resume/seventeenth_process_snapshot.'+channel+'.log';pin(p,ex[channel+'_sha256']);logs[channel]=(ROOT/p).read_text()
            if ex['exit_code']==1:require(ex['state']=='NO_CADICAL_PROCESS_OBSERVED' and len(logs['stdout'].splitlines())<=1,'historical empty process snapshot')
            elif ex['exit_code']==0:require(ex['state']=='CADICAL_PROCESS_OBSERVED' and len(logs['stdout'].splitlines())>1,'historical process snapshot')
            else:require(ex['state']=='UNKNOWN_OBSERVATION_ERROR','historical observation error')
            require(not any(name+'/instance.cnf' in logs['stdout'] for name in ['20260930_hadamard_six_prism_cyclic_cnf','20260930_hadamard_prism_ordered_cnf']),'completed cohort not reported live')
            pack=load(B+'seventeenth_artifact_packaging/summary.json');require(pack['claim_ids']==ids and pack['status'].endswith('_PASS'),'catalog population')
            for p,h in pack['output_hashes'].items():pin(p,h)
            pin('docs/REPRODUCING_20260930_SEVENTEENTH_WAVE.md')
            final=dict(checkpoint_sha256=sha(ROOT/path),report_sha256=sha(ROOT/reportpath),snapshot_sha256=sha(ROOT/snap),saved_execution=ex,next_experiment=cp['next_experiment'])
        for p in ['acceleration/audit_20260930_seventeenth_checkpoint.py','acceleration/audit_20260930_sixteenth_checkpoint.py','uv.lock','pyproject.toml']:pin(p)
        summary=dict(status='INDEPENDENT_SEVENTEENTH_CHECKPOINT_REPORT_CONSISTENCY_PASS' if a.mode=='final' else 'INDEPENDENT_SEVENTEENTH_CHECKPOINT_PRECHECK_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),mode=a.mode,inputs_sha256=pins,registrar_chain=chain,new_claim_ids=ids,counts=dict(claims=171,verified_clear=169,candidate_clear=2,new_claims=6,native_attempts=2,restricted_UNSAT_proofs=1,UNKNOWN=1,new_whole_support_exclusions=0),corruptions=controls,final_checks=final,verifier='/root/eight_domain_audit',scope='Only registration/checkpoint/report and saved outcome coherence; not new mathematical verification.',shared_components=['Frozen independently authored sixteenth-checkpoint YAML/hash helpers reused. No recorder/registrar imports.','Earlier independent proof, encoding, census and native audits authenticated rather than rerun.'],limitations=['No new mathematical claim promotion; existing complete DRAT replay is referenced, not repeated.','Partial trace is not rehashed again and no current process observation is made.','Catalog closure is not rerun; its saved output hashes and population are bound.'],ledger_changed=False,git_changed=False,target_resolution='UNKNOWN')
        write(out/'summary.json',summary);print(json.dumps(dict(status=summary['status'],sha256=sha(out/'summary.json'))))
    except BaseException as exc:write(out/'failure.json',dict(error=repr(exc)));raise
if __name__=='__main__':main()
