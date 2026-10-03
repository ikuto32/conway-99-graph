"""Independent wave21 metadata/availability consistency, not mathematical replay."""
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import argparse, gzip, hashlib, json, platform, subprocess, sys
from audit_20260930_sixteenth_checkpoint import read_ledger, require, sha, write

ROOT = Path(__file__).resolve().parents[1]
B = 'acceleration/results/20260930_'; I = B + 'independent_review/'
CP = B + 'resume/twentyfirst_milestone_checkpoint.json'
SNAP = B + 'resume/claims_at_twentyfirst_milestone.yaml'
PACK = B + 'twentyfirst_artifact_packaging/'
REPORT = 'docs/RESEARCH_20260930_TWENTYFIRST_WAVE.md'
GUIDE = 'docs/REPRODUCING_20260930_TWENTYFIRST_WAVE.md'
GEN = 'acceleration/record_20260930_twentyfirst_checkpoint.py'
PRIVATE = I + 'hadamard_oriented_unknown/process.stdout.log'
MODEL = B + 'hadamard_case0_profile_cnf/model.json'
CNF = B + 'hadamard_case0_profile_cnf/instance.cnf'
PROOF = B + 'hadamard_case0_profile_native_pilot/main/proof.drat'
MH = '6705e33a26c332d093e3a2bff6dcd5dca276c6b50da2b24c61c7cbf891e0629c'
CH = '2e949832491635b794e02b525ac983c0920d66cf91ee4e039564c5920008b22e'
PH = '01ee3198778714f32bf0e7e0c4a89ab3d29ecceb088ccf392ee0e2749418d07d'
LH = 'da8f41f3da708089b30cd3dff4299e0d104f71765d2a8381f0401182de1daa6f'
REG = ['structural', 'normalization', 'joint_and_five', 'six_and_case0', 'proof_and_marginals']
IDS = ['C-FIXED-HADAMARD-' + s for s in [
    'AT-MOST-THREE-EXCEPTIONS-IMPLIES-BALANCED', 'AT-MOST-THREE-UNBALANCED-GROUPS-EXCLUSION',
    'FOUR-GROUP-CIRCUIT-NECESSITY', 'FOUR-EXCEPTION-LOCAL-PROFILE-SCREEN',
    'FOUR-EXCEPTION-GLOBAL-FIBRE-NORMALIZATION', 'EXACTLY-FIVE-UNBALANCED-GROUPS-EXCLUSION',
    'FOUR-EXCEPTION-PARTIAL12-CENSUS', 'FIRST-PARTIAL12-RESIDUAL-PSD',
    'SIX-EXCEPTION-KERNEL-CENSUS', 'FOUR-EXCEPTION-CASE0-GRAM-ENCODING',
    'FOUR-EXCEPTION-CASE0-EXCLUSION', 'SIX-EXCEPTION-INTEGER-MARGINAL-CENSUS']]
EXCLUDED = ['four_profile_cnfs', 'four_profile_native', 'six_profile_local_domains', 'input_relabeling']

def check_counts(cp, ledger):
    require(cp['claim_population'] == len(ledger['claims']) == 206, '206 claim records')
    require(cp['claim_status_counts'] == dict(Counter(c['status'] for c in ledger['claims'])) == dict(VERIFIED=203,CANDIDATE=2,REFUTED=1), 'status populations')
    require(cp['claim_review_counts'] == dict(Counter(c['review_state'] for c in ledger['claims'])) == dict(CLEAR=206), 'review populations')
    require((cp['verified_clear'],cp['candidate_clear'],cp['refuted_clear']) == (203,2,1), 'current clear counts')
    require(cp['new_verified_ids'] == IDS and cp['evidence_only_revision_changes'] == [], 'twelve exact additions')
    require(cp['target_resolution'] == 'UNKNOWN' and cp['external_review'] is None and cp['external_review_null_reason'], 'target and external review')
    require(cp['coverage'] == 'Overall search coverage: UNKNOWN; no validated denominator.', 'coverage statement')
    require(cp['necessary_unbalanced_counts'] == dict(at_least=4,exactly_five_excluded=True,scope='Literal fixed support and prescribed Gram only.'), 'fixed-support marginal implications')
    require(cp['four_group_screen'] == dict(global_quartets=4845,necessary_quartets=14,labelled_profiles=108,locally_excluded_profiles=12,nonempty_AC_profiles=96,fibre_orbits=18,nonempty_fibre_orbits=16,scope='Exactly four exceptional groups, prescribed Gram plus column caps.'), 'profile and orbit populations')
    require(cp['partial_enumeration'] == dict(selected_profiles=96,complete_profiles=35,partial_profiles=1,unattempted_profiles=60,checked_intervals=1263,checked_tuples=7335060,raw_witnesses=36,independent_gate=I+'four_group_joint_v2/summary.json'), 'bounded enumeration distinctions')
    require(cp['first_residual_psd'] == dict(rank=29,nullity=7,remaining_columns_constructed=0,scope='One exact saved twelve-column partial object.'), 'PSD scope')
    require(cp['six_group_screen'] == dict(subsets=38760,rank_counts={'6':35587,'5':3164,'4':9},retained_rank4_subsets=9,independently_enumerated_coordinate_sequences=121869,DP_layers=108,excluded_rank4_cases=[2,6,7],remaining_group_subsets=6,labelled_marginal_profiles=984,scope='Full-Gram necessary marginals only; no quadratic Gram or Y-cap feasibility.'), 'necessary integer marginal populations')
    require(cp['case0_native'] == dict(attempted=1,completed=1,outcome='UNSAT',variables=10564,clauses=187408,conflicts=12232,native_wall_seconds=1.82,native_cpu_seconds=1.08,complete_independent_proof_replay=True,proof_bytes=9139513,proof_sha256=PH,independent_gate=I+'hadamard_case0_profile_unsat/summary.json',scope='Literal case0 profile with within-group caps; cross-group caps and D omitted.'), 'one complete literal-profile proof')
    for key in ['new_full_factors','complete99_graphs','new_whole_support_exclusions','new_core_exclusions','new_unrestricted_exclusions']:
        require(cp[key] == 0, 'no broader result '+key)

def check_payload(entries, stage):
    bypath = {r['path']:r for r in entries}
    require(len(bypath) == len(entries), 'unique payload paths')
    require({p for p,r in bypath.items() if r['availability']=='LOCAL_ONLY'} == {MODEL}, 'one recoverable local raw model')
    require('recovery available' in bypath[MODEL]['limitation'], 'local model recovery described')
    require(MODEL not in stage and PRIVATE not in stage and PRIVATE not in bypath, 'private and oversize raw files omitted')
    require(bypath[PROOF]['availability']=='READY_FOR_PUBLICATION' and bypath[PROOF]['bytes']==9139513 and bypath[PROOF]['sha256']==PH, 'complete raw proof public payload')
    for p in set(bypath) | set(stage):
        require(not any(t in p for t in EXCLUDED), 'wave22 not in wave21 '+p)
    require(all(r['availability'] in ['LOCAL_ONLY','READY_FOR_PUBLICATION'] for r in entries), 'publication readiness not unsupported public claim')

def check_proof(report):
    require(report['status']=='INDEPENDENT_FIXED_HADAMARD_CASE0_PROFILE_UNSAT_PASS' and report['claim_id']==IDS[10] and report['claim_revision']==1, 'case0 independent gate')
    require(report['proof']['complete_independent_replay'] is True and report['proof']['sha256']==PH and report['proof']['bytes']==9139513, 'complete proof identity')
    require(report['inputs_sha256'][CNF]==CH and report['inputs_sha256'][PROOF]==PH, 'exact input/proof binding')
    replay = next(r for r in report['replays'] if r['name']=='complete_case0_proof')
    require(replay['actual_exit_code']==0 and replay['accepted'] is True and replay['cnf_sha256']==CH and replay['proof_sha256']==PH, 'accepted full trace replay')
    controls = [r for r in report['replays'] if r is not replay]
    require(len(controls)==5 and sum(r['accepted'] for r in controls)==1 and all(r['accepted']==r['expected_acceptance'] for r in controls), 'one positive and four negative proof controls')
    require(len(report['native_receipt_corruptions_rejected'])==6 and report['new_solver_calls']==0, 'receipt calibration and no new solve')
    require(report['native_outcome']==dict(conflicts=12232,native_cpu_seconds=1.08,native_wall_seconds=1.82,trace_bytes=9139513,wrapper_wall_seconds=1.875), 'actual native execution metrics')

def recover(m, parts):
    require(m['raw_path']==MODEL and m['raw_sha256']==MH and m['raw_bytes']==13208093, 'raw model binding')
    require(len(parts)==len(m['parts'])==1, 'one ordered part')
    for raw,p in zip(parts,m['parts'],strict=True):
        require(len(raw)==p['bytes'] and hashlib.sha256(raw).hexdigest()==p['sha256'], 'part size/hash')
    compressed=b''.join(parts)
    require(len(compressed)==m['compressed_bytes']==576941 and hashlib.sha256(compressed).hexdigest()==m['compressed_sha256'], 'gzip identity')
    raw=gzip.decompress(compressed)
    require(len(raw)==m['raw_bytes'] and hashlib.sha256(raw).hexdigest()==MH, 'recovered model identity')
    return raw

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--checkpoint-sha256',required=True);ap.add_argument('--catalog-summary-sha256',required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};cache={}
    def pin(p,expected=None):
        if p not in cache: cache[p]=sha(ROOT/p)
        h=cache[p];require(expected is None or h==expected,'artifact hash '+p);pins[p]=h;return h
    def load(p,expected=None):pin(p,expected);return json.loads((ROOT/p).read_bytes())
    try:
        additions=[];chain=[];last=None
        for name in REG:
            d=B+'twentyfirst_'+name+'_registration/';rec=load(d+'summary.json');before=d+'CLAIMS.before.yaml';after=d+'CLAIMS.after.yaml'
            pin(before,rec['previous_ledger_sha256']);pin(after,rec['ledger_sha256']);old,new=read_ledger(ROOT/before),read_ledger(ROOT/after)
            if last is not None:require((ROOT/before).read_bytes()==last,'contiguous registration snapshots')
            else:
                pub=load(B+'resume/twentieth_publication_pointer_receipt.json');priorpath=B+'resume/claims_at_twentieth_milestone.yaml';pin(priorpath)
                require(len(old['claims'])==194 and sha(ROOT/before)==pub['ledger_sha256'],'published wave20 starting ledger')
                prior=read_ledger(ROOT/priorpath);require(prior['claims']==old['claims'],'publication preserved historical claims')
                require(all(prior[k]==old[k] for k in prior if k not in ['updated_at','artifacts']),'publication only artifact metadata')
                pa,pb={r['id']:r for r in prior['artifacts']},{r['id']:r for r in old['artifacts']};require(set(pa)==set(pb),'prior artifact population')
                changed={k for k in pa if pa[k]!=pb[k]};require(changed==set(pub['new_public_artifact_ids']),'exact availability transitions')
                for k in changed:
                    require(all(pa[k].get(f)==pb[k].get(f) for f in set(pa[k])|set(pb[k]) if f not in ['availability','retrieval','unavailable_reason']),'unchanged published identity')
                    require(pa[k]['availability']=='LOCAL_ONLY' and pb[k]['availability']=='PUBLIC' and pub['published_commit'] in pb[k]['retrieval'],'publication pointers')
                require(pub['mathematical_claim_changes']==[] and pub['published_commit']==pub['confirmed_remote_ref'],'published evidence confirmed')
            aa,bb={c['id']:c for c in old['claims']},{c['id']:c for c in new['claims']}
            require(all(bb[k]==v for k,v in aa.items()),'existing claims unchanged')
            oa,na={a['id']:a for a in old['artifacts']},{a['id']:a for a in new['artifacts']};require(all(na[k]==v for k,v in oa.items()),'existing artifacts unchanged')
            added=[c['id'] for c in new['claims'] if c['id'] not in aa];require(added==rec['new_claim_ids'],'recorded additions')
            require(rec['registrar_performs_mathematical_verification'] is False and rec['validation']['valid'] and rec['validation']['errors']==[],'registrar only validated bookkeeping')
            additions+=added;last=(ROOT/after).read_bytes();chain.append(dict(name=name,before=sha(ROOT/before),after=sha(ROOT/after),added=added))
        require(additions==IDS and hashlib.sha256(last).hexdigest()==LH,'frozen twelve-claim cohort')
        ledger=new;claims={c['id']:c for c in ledger['claims']};artifacts={a['id']:a for a in ledger['artifacts']}
        for cid in IDS:
            c=claims[cid];require(c['revision']==1 and c['status']=='VERIFIED' and c['review_state']=='CLEAR','exact current verified revision')
            require(c['scope']['target_resolution']=='NONE' and c['scope']['unrestricted_target'] is False,'limited exact scope')
            for dep in c['dependencies']:require(claims[dep['id']]['revision']==dep['revision'],'dependency revision')
            for eid in c['evidence']:pin(artifacts[eid]['path'],artifacts[eid]['sha256'])
            for v in c['verification']:
                require(v['claim_revision']==1 and v['outcome']=='PASS','recorded independent result')
                for aid,h in v['artifact_hashes'].items():require(artifacts[aid]['sha256']==h,'verification artifact binding')
        cp=load(CP,args.checkpoint_sha256);check_counts(cp,ledger);pin(SNAP,LH)
        require(cp['ledger_snapshot_sha256']==LH and (ROOT/SNAP).read_bytes()==last==(ROOT/'CLAIMS.yaml').read_bytes(),'frozen/current ledger equality')
        require(subprocess.check_output(['git','show',cp['source_commit']+':CLAIMS.yaml'],cwd=ROOT)==(ROOT/(B+'twentyfirst_structural_registration/CLAIMS.before.yaml')).read_bytes(),'immutable public starting ledger')
        prior=load(B+'resume/twentieth_milestone_checkpoint.json',cp['previous_checkpoint_sha256']);require(prior['claim_population']==194,'prior checkpoint')
        for p,h in cp['evidence_sha256'].items():pin(p,h)
        proof=load(I+'hadamard_case0_profile_unsat/summary.json','355b0b6dbc9707cc86dda748ad5dd0f05bfa6eb7090ab5dd8c30db3df91ebba9');check_proof(proof)
        joint=load(I+'four_group_joint_v2/summary.json','6b226d3a4c63ed3b6a132ea510bc5bd525ff0fa53ca71c697f66f50a22f207bc')
        require([joint[k] for k in ['completed_profiles','partially_completed_profiles','unattempted_profiles','completed_intervals','raw_partial_objects','raw_first_witnesses']]==[35,1,60,1263,7335060,36],'saved complete partial census counts')
        marginal=load(I+'hadamard_six_rank4_profiles/summary.json','0430355de5159a5223c464d3766ec54206a37177b90e18cf92364d276dd483e3')
        require(marginal['exact_counts']==[96,108,0,96,96,24,0,0,564] and marginal['zero_cases']==[2,6,7] and marginal['labelled_feasible_marginal_profiles']==984,'saved marginal counts')
        require(marginal['complete_profile_sequences']==121869 and marginal['saved_layers_checked']==108 and marginal['saved_state_witnesses_checked']==19819,'full independent enumeration scope')
        orbit=load(I+'hadamard_fibre_profile_orbits/summary.json');require((orbit['profiles'],orbit['orbits'],orbit['excluded_orbits'],orbit['unresolved_orbits'])==(108,18,2,16),'orbit and screen distinction')
        require('no orbit transfer' in claims[IDS[10]]['scope']['description'],'no implicit new orbit exclusion')
        for r in [proof,joint,marginal,orbit]:
            for p,h in r['outputs_sha256'].items():pin(p,h)
        summary=load(PACK+'summary.json',args.catalog_summary_sha256)
        require(summary['status']=='TWENTYFIRST_EXPLICIT_PUBLICATION_INVENTORY_PASS' and summary['claim_ids']==IDS,'final catalog exact cohort')
        for p,h in summary['output_hashes'].items():pin(p,h)
        catalog=load(PACK+'catalog.json');inventory=load(PACK+'stage_inventory.json');entries=catalog['entries'];check_payload(entries,inventory['paths'])
        public=[r for r in entries if r['availability']=='READY_FOR_PUBLICATION'];pubpaths={r['path'] for r in public}
        require(len(entries)==summary['selected_files'] and len(public)==summary['public_research_files'] and sum(r['bytes'] for r in public)==summary['public_research_bytes'],'public payload populations')
        require(summary['new_local_only_research_artifacts']==1 and summary['new_gzip_streams']==1,'single oversize model')
        for r in entries:
            pin(r['path'],r['sha256']);require((ROOT/r['path']).stat().st_size==r['bytes'],'actual payload byte length')
            if r['availability']=='READY_FOR_PUBLICATION':require(r['bytes']<=10*1024*1024,'public size ceiling')
        require(pubpaths<=set(inventory['paths']),'complete public staging allowlist')
        for r in inventory['entries']:pin(r['path'],r['sha256'])
        for p in [B+'hadamard_four_group_joint/failure.json',B+'hadamard_four_group_joint/failed_source.py']:
            require(p in pubpaths,'v1 failed positive calibration preserved')
        refs=load(PACK+'reference_checks.json');require(refs['status']=='EXACT_HASH_CLOSURE_AND_GZIP_RECOVERY_PASS','closure gate')
        require(len(refs['records'])==summary['reference_bindings'] and len({r['path'] for r in refs['records']})==summary['unique_referenced_files'],'closure populations')
        require(load(PACK+'reference_diagnostics.json')==dict(errors=[],count=0),'no unhandled bad reference')
        for r in refs['records']:
            require(r['path']!=PRIVATE,'private snapshot absent from new closure')
            pin(r['path'],r['sha256']);require((ROOT/r['path']).stat().st_size==r['bytes'],'referenced identity')
        gitrows=load(PACK+'git_byte_checks.json');require(gitrows['status']=='CURRENT_GIT_FILTER_BYTES_PASS','saved Git-filter pass')
        for r in gitrows['records']:
            require(r['path'] in pubpaths,'Git payload public only');raw=(ROOT/r['path']).read_bytes()
            require(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==r['git_blob_sha1'],'literal Git payload')
        modelpackage=load(B+'hadamard_case0_model_package/artifact_packages.json','f5808a5c30b751e23144fd0c9a107ba6fd0db75602a2e29cc15193da5c9bfe6b')
        parts=[]
        for p in modelpackage['parts']:pin(p['path'],p['sha256']);require(p['path'] in pubpaths,'model part public');parts.append((ROOT/p['path']).read_bytes())
        recovered=recover(modelpackage,parts);require(recovered==(ROOT/MODEL).read_bytes(),'literal whole recovered model equality')
        private=load(I+'hadamard_oriented_unknown/process_snapshot_availability.json','3b8c2c2549c5b70e84345f696d8029ac169304f26b922ffcf9c73be654f419d0')
        require('LOCAL_ONLY' in json.dumps(private) and 'OMIT' in json.dumps(private),'historical privacy omission preserved')
        # Inspect only targeted commands and their pinned hashes, never the old private raw stdout.
        for p in pubpaths:
            if p.endswith('.json'):
                obj=json.loads((ROOT/p).read_bytes())
                def walk(x):
                    if isinstance(x,dict):
                        cmd=x.get('command')
                        if isinstance(cmd,list) and any(str(t).rsplit('/',1)[-1]=='ps' for t in cmd):
                            require('-C' in cmd and cmd[cmd.index('-C')+1]=='cadical' and '-e' not in cmd and '-eo' not in cmd,'targeted process records only')
                        for v in x.values():walk(v)
                    elif isinstance(x,list):
                        for v in x:walk(v)
                walk(obj)
        pin(GEN);pin(REPORT);pin(GUIDE);text=(ROOT/REPORT).read_text(encoding='utf8');guide=(ROOT/GUIDE).read_text(encoding='utf8')
        for cid in IDS:require(text.count(cid+' r1')==1 and claims[cid]['scope']['description'] in text,'exact claim table')
        for token in ['Twelve independently checked claims','one partial prefix','7,335,060','121,869','984 labelled marginal profiles','complete9,139,513-byte trace','zero new whole-support, core or unrestricted exclusions','206 claims:203 VERIFIED/CLEAR,2 CANDIDATE/CLEAR and1 REFUTED/CLEAR','private-process omissions remain unchanged']:
            require(token in text,'report fact/scope '+token)
        for token in ['fresh output destinations','13,208,093 bytes','576,941-byte gzip','initial domains','smaller AC domains','9,139,513 bytes','within-group caps','Cross-group caps and residualD were omitted','No target automorphism is assumed','Do not restart','outside this milestone','Do not rerun one-shot registrars']:
            require(token in guide,'replay boundary '+token)
        require(cp['timestamp'] in text and cp['source_commit'] in text and cp['next_experiment'] in text,'report provenance')
        for p in ['README.md','ACTIVE_RESEARCH.md','docs/RESEARCH_MAP.md','docs/REPRODUCING.md']:
            pin(p);require('TWENTYFIRST_WAVE' in (ROOT/p).read_text(encoding='utf8'),'updated entry point')
        validation=load(B+'resume/twentyfirst_precommit_validation.json');require(validation['valid'] and validation['errors']==[],'ledger semantic/schema validation')
        ex=cp['execution'];require(ex['command']==['wsl.exe','-d','Ubuntu-24.04','--','ps','-C','cadical','-o','pid,etime,pcpu,rss,args'],'targeted checkpoint execution census')
        require(ex['state']=={0:'CADICAL_PROCESS_OBSERVED',1:'NO_CADICAL_PROCESS_OBSERVED'}.get(ex['exit_code'],'UNKNOWN_OBSERVATION_ERROR'),'saved process state')
        for channel in ['stdout','stderr']:pin(B+'resume/twentyfirst_process_snapshot.'+channel+'.log',ex[channel+'_sha256'])
        corrupt=[]
        def reject(label,fn):
            try:fn()
            except (ValueError,KeyError,TypeError,EOFError,gzip.BadGzipFile):corrupt.append(label)
            else:raise ValueError('corruption accepted '+label)
        for label,route,value in [('claim_count',['claim_population'],207),('status_count',['verified_clear'],206),('full_factor',['new_full_factors'],1),('whole_support',['new_whole_support_exclusions'],1),('all_joint_complete',['partial_enumeration','complete_profiles'],96),('marginals_are_factors',['six_group_screen','scope'],'Full factors.'),('extra_profile_exclusion',['case0_native','scope'],'All profiles.'),('missing_proof',['case0_native','complete_independent_proof_replay'],False),('wrong_target',['target_resolution'],'VERIFIED')]:
            bad=deepcopy(cp);where=bad
            for k in route[:-1]:where=where[k]
            where[route[-1]]=value;reject(label,lambda bad=bad:check_counts(bad,ledger))
        reject('private_staged',lambda:check_payload(entries,inventory['paths']+[PRIVATE]))
        reject('wave22_staged',lambda:check_payload(entries,inventory['paths']+[B+'hadamard_four_profile_cnfs/summary.json']))
        bad=deepcopy(proof);bad['replays'][-1]['accepted']=False;reject('proof_veto_ignored',lambda:check_proof(bad))
        bad=deepcopy(modelpackage);bad['raw_sha256']='0'*64;reject('wrong_recovery_hash',lambda:recover(bad,parts))
        reject('truncated_gzip',lambda:recover(modelpackage,[parts[0][:-1]]))
        current_at=datetime.now(timezone.utc).isoformat();proc=subprocess.run(ex['command'],cwd=ROOT,capture_output=True,timeout=15)
        for channel,raw in [('stdout',proc.stdout),('stderr',proc.stderr)]:
            with(out/('current_process.'+channel+'.log')).open('xb') as f:f.write(raw)
        fresh=dict(observed_at=current_at,command=ex['command'],exit_code=proc.returncode,state={0:'CADICAL_PROCESS_OBSERVED',1:'NO_CADICAL_PROCESS_OBSERVED'}.get(proc.returncode,'UNKNOWN_OBSERVATION_ERROR'),scope='Separate timestamped census; later-cohort processes do not change the frozen wave21 result.')
        for p in ['acceleration/audit_20260930_twentyfirst_checkpoint.py','acceleration/audit_20260930_sixteenth_checkpoint.py','docs/AUDIT_20260930_TWENTYFIRST_CHECKPOINT_PLAN.md','uv.lock','pyproject.toml']:pin(p)
        write(out/'summary.json',dict(status='INDEPENDENT_TWENTYFIRST_CHECKPOINT_REPORT_CONSISTENCY_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,outputs_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in out.iterdir() if p.is_file()},registrar_chain=chain,new_claim_ids=IDS,counts=dict(claims=206,verified_clear=203,candidate_clear=2,refuted_clear=1,new_verified=12,public_payloads=len(public),public_bytes=sum(r['bytes'] for r in public),local_raw_models=1,complete_proof_bytes=9139513,reference_bindings=len(refs['records']),referenced_files=len({r['path'] for r in refs['records']})),checkpoint_sha256=sha(ROOT/CP),report_sha256=sha(ROOT/REPORT),snapshot_sha256=LH,corruptions_rejected=corrupt,saved_execution=ex,current_execution=fresh,verifier='/root/structural_attack',scope='Independent metadata, immutable evidence identity, publication/recovery and report consistency only.',shared_components=['Frozen duplicate-key-safe YAML, hash and write helpers from a prior independent audit; no recorder, registrar or packaging imports.','This reviewer authored several prior mathematical gates. Their existing results are authenticated here, without a new mathematical approval.'],limitations=['No new mathematical verification, SAT solving or DRAT replay.','Raw model gzip recovery is an identity check only.','The historical private process snapshot is neither read, displayed nor published.','Wave22 work is excluded; saved live observations are timestamped separately from research status.'],target_resolution='UNKNOWN',solver_calls=0,proof_replays=0))
        print(json.dumps(dict(status='INDEPENDENT_TWENTYFIRST_CHECKPOINT_REPORT_CONSISTENCY_PASS',sha256=sha(out/'summary.json'))))
    except BaseException as exc:write(out/'failure.json',dict(error=repr(exc),source_sha256=sha(Path(__file__))));raise

if __name__=='__main__':main()
