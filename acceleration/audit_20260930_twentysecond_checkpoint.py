"""Independent wave22 metadata/byte review; no mathematical replay or producer imports."""
from collections import Counter
from copy import deepcopy
from datetime import datetime,timezone
from pathlib import Path
import argparse,gzip,hashlib,json,platform,subprocess,sys
from audit_20260930_sixteenth_checkpoint import read_ledger,require,sha,write
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';I=B+'independent_review/'
CP=B+'resume/twentysecond_milestone_checkpoint.json';SNAP=B+'resume/claims_at_twentysecond_milestone.yaml';PACK=B+'twentysecond_artifact_packaging/'
REPORT='docs/RESEARCH_20260930_TWENTYSECOND_WAVE.md';GUIDE='docs/REPRODUCING_20260930_TWENTYSECOND_WAVE.md'
PRIVATE=I+'hadamard_oriented_unknown/process.stdout.log';LH='e58a3cea34b0fafcb636c299af9db67ceaba2ea29666ecf5d0e6ec6a23c81e80'
CASES=[6,12,18,24,30,36,42,48,51,72,78,84,90,96,102]
REG=['local_domains','encoding_and_seven','six_pairs_and_orbits','fifteen_proofs','four_union']
IDS=['C-FIXED-HADAMARD-'+s for s in ['SIX-EXCEPTION-LOCAL-DOMAIN-FILTER','FIFTEEN-FOUR-EXCEPTION-GRAM-ENCODINGS','MATCHING-COORDINATE-RELABELING-CENSUS','SEVEN-EXCEPTION-KERNEL-CENSUS','SEVEN-EXCEPTION-INTEGER-MARGINAL-CENSUS','SIX-EXCEPTION-PAIRWISE-PROFILE-SCREEN','SIX-EXCEPTION-FIBRE-NORMALIZATION','FIFTEEN-FOUR-EXCEPTION-EXCLUSIONS','EXACTLY-FOUR-UNBALANCED-GROUPS-EXCLUSION','AT-MOST-FIVE-UNBALANCED-GROUPS-EXCLUSION']]
LOCAL={B+f'hadamard_four_profile_cnfs/case_{c:03d}/model.json' for c in CASES}|{B+f'hadamard_four_profile_native_campaign/case_{c:03d}/main/proof.drat' for c in CASES}
EXCLUDE=['hadamard_six_profile_cnf','hadamard_six_profile_native','hadamard_six_profile_object_calibration','hadamard_six_profile_unsat','hadamard_six_profile0000_unsat','hadamard_six_remaining','hadamard_fiftyfour','all_triple_descent']
def counts(cp,ledger):
    require(cp['claim_population']==len(ledger['claims'])==216,'216 records')
    require(cp['claim_status_counts']==dict(Counter(c['status'] for c in ledger['claims']))==dict(VERIFIED=213,CANDIDATE=2,REFUTED=1),'status populations')
    require(cp['claim_review_counts']==dict(Counter(c['review_state'] for c in ledger['claims']))==dict(CLEAR=216),'clear population')
    require((cp['verified_clear'],cp['candidate_clear'],cp['refuted_clear'])==(213,2,1),'clear counts')
    require(cp['new_verified_ids']==IDS and cp['evidence_only_revision_changes']==[],'ten additions only')
    require(cp['target_resolution']=='UNKNOWN' and cp['external_review'] is None and cp['external_review_null_reason'],'target/external status')
    require(cp['coverage']=='Overall search coverage: UNKNOWN; no validated denominator.','coverage')
    require(cp['necessary_unbalanced_counts']==dict(at_least=6,scope='Literal fixed support, prescribed full integer Gram and all outside-column overlap caps.'),'conditional lower bound')
    require(cp['four_profile_union']==dict(profile_population=108,local_exclusions=12,proof_representatives=16,proof_orbit_members=96,duplicate_coverage=0,missing_profiles=0),'disjoint union')
    require(cp['native_batch']==dict(selected=15,attempted=15,completed=15,SAT=0,UNSAT=15,UNKNOWN=0,complete_independent_proof_replays=15,proof_bytes=149571922,wrapped_solver_wall_seconds=25.903999999864027,end_to_end_wall_seconds=41.21900000004098,scope='Fifteen literal fixed-support profile formulas; cross-group caps and residualD omitted.'),'actual native population')
    require(cp['six_profile_screen']==dict(labelled_profiles=984,relations=12648,distinct_option_pairs=12846624,checked_deletions=208608,checked_surviving_supports=815040,Gram_pair_empty_profiles=582,combined_empty_profiles=654,nonempty_profiles=330,all_profile_orbits=164,recorded_nonempty_orbits=55,scope='Both variants start with within-group cap-filtered domains. Nonempty AC outcomes are not joint/full-factor feasibility.'),'six-profile scopes/counts')
    require(cp['seven_profile_screen']==dict(subsets=77520,rank_counts={'7':56264,'6':20930,'5':326},retained_kernel_subsets=200,marginal_empty_subsets=162,marginal_nonempty_subsets=38,labelled_marginal_profiles=1608,full_sequences=154214,saved_layers=2400,saved_state_witnesses=101146,scope='Necessary integer/count relaxation only; positive counts do not establish local triples or factors.'),'seven marginal population')
    for k in ['new_full_factors','complete99_graphs','new_whole_support_exclusions','new_core_exclusions','new_unrestricted_exclusions']:require(cp[k]==0,'no broader outcome '+k)
def payload(entries,stage):
    by={r['path']:r for r in entries};require(len(by)==len(entries),'unique catalog paths')
    require({p for p,r in by.items() if r['availability']=='LOCAL_ONLY'}==LOCAL,'exact30 local originals')
    require(not LOCAL&set(stage) and PRIVATE not in by and PRIVATE not in stage,'omitted raw/private paths')
    for p in set(by)|set(stage):require(not any(t in p for t in EXCLUDE),'later cohort omitted '+p)
    for p in LOCAL:require('recovery available' in by[p]['limitation'],'lossless recovery limitation')
    require(all(r['availability'] in ['LOCAL_ONLY','READY_FOR_PUBLICATION'] for r in entries),'readiness not unsupported PUBLIC claim')
def proof_metadata(proof):
    require(proof['status']=='INDEPENDENT_FIXED_HADAMARD_FIFTEEN_PROFILE_UNSAT_PASS' and proof['claim_id']==IDS[7] and proof['checked_cases']==CASES,'exact proof collection')
    require(proof['completed_proof_replays']==15 and proof['SAT']==proof['UNKNOWN']==0 and proof['proof_bytes']==149571922 and proof['retained_two_copy_bytes']==299143844,'distinct byte populations')
    require([r['case'] for r in proof['case_records']]==CASES,'all literal proof rows')
    for r in proof['case_records']:
        p=r['proof'];q=r['replay'];require(p['complete_independent_replay'] and q['accepted'] and q['actual_exit_code']==0 and q['cnf_sha256']==r['cnf_sha256'] and q['proof_sha256']==p['sha256'],'complete proof identity/replay')
        require(proof['inputs_sha256'][r['cnf_path']]==r['cnf_sha256'] and proof['inputs_sha256'][p['path']]==p['sha256'],'exact input bindings')
    require(sum(r['proof']['bytes'] for r in proof['case_records'])==149571922,'actual proof sum')
    require(len(proof['controls'])==19 and sum(r['accepted'] for r in proof['controls'])==1 and all(r['accepted']==r['expected_acceptance'] for r in proof['controls']),'positive and18 negatives')
    require(len(proof['native_receipt_corruptions_rejected'])==90 and proof['new_solver_calls']==0,'receipt controls and no rerun')
def recover(package,part_data):
    require(len(package['parts'])==len(part_data)>0,'ordered gzip parts')
    chunks=[];offset=0
    for p,data in zip(package['parts'],part_data,strict=True):
        require(p['raw_offset']==offset and len(data)==p['gzip_bytes'] and hashlib.sha256(data).hexdigest()==p['gzip_sha256'],'part order/identity')
        raw=gzip.decompress(data);require(len(raw)==p['raw_bytes'] and hashlib.sha256(raw).hexdigest()==p['raw_sha256'],'decompressed chunk identity');chunks.append(raw);offset+=len(raw)
    raw=b''.join(chunks);require(len(raw)==package['bytes'] and hashlib.sha256(raw).hexdigest()==package['sha256'],'full raw recovery');return raw
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--checkpoint-sha256',required=True);ap.add_argument('--catalog-summary-sha256',required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};cache={}
    def pin(p,h=None):
        require(p!=PRIVATE,'private historical stdout never read or hashed')
        if p not in cache:cache[p]=sha(ROOT/p)
        require(h is None or cache[p]==h,'identity '+p);pins[p]=cache[p];return cache[p]
    def load(p,h=None):pin(p,h);return json.loads((ROOT/p).read_bytes())
    try:
        index_before=subprocess.check_output(['git','ls-files','--stage','-z'],cwd=ROOT);additions=[];chain=[];last=None
        for name in REG:
            d=B+'twentysecond_'+name+'_registration/';rec=load(d+'summary.json');before=d+'CLAIMS.before.yaml';after=d+'CLAIMS.after.yaml';pin(before,rec['previous_ledger_sha256']);pin(after,rec['ledger_sha256']);old,new=read_ledger(ROOT/before),read_ledger(ROOT/after)
            if last is not None:require((ROOT/before).read_bytes()==last,'contiguous snapshots')
            else:
                pub=load(B+'resume/twentyfirst_publication_pointer_receipt.json');prior=read_ledger(ROOT/(B+'resume/claims_at_twentyfirst_milestone.yaml'));pin(B+'resume/claims_at_twentyfirst_milestone.yaml',pub['previous_ledger_sha256']);require(len(old['claims'])==206 and sha(ROOT/before)==pub['ledger_sha256'],'public wave21 ledger')
                require(prior['claims']==old['claims'] and all(prior[k]==old[k] for k in prior if k not in ['updated_at','artifacts']),'historical claims preserved')
                pa,pb={v['id']:v for v in prior['artifacts']},{v['id']:v for v in old['artifacts']};require(set(pa)==set(pb),'artifact population unchanged');changed={k for k in pa if pa[k]!=pb[k]};promoted=set(pub['new_public_artifact_ids']);recovered=set(pub['public_recovery_metadata_updated']);require(changed==promoted|recovered and not promoted&recovered,'exact disclosed availability transitions')
                for k in changed:
                    require(all(pa[k].get(f)==pb[k].get(f) for f in set(pa[k])|set(pb[k]) if f not in ['availability','retrieval','unavailable_reason']),'unchanged identities')
                    if k in promoted:require(pa[k]['availability']=='LOCAL_ONLY' and pb[k]['availability']=='PUBLIC' and pub['published_commit'] in pb[k]['retrieval'],'publication transition')
                    else:require(pa[k]['availability']==pb[k]['availability']=='LOCAL_ONLY' and pub['published_commit'] in pb[k]['retrieval'] and 'publicly recoverable' in pb[k]['unavailable_reason'],'retained raw/public recovery')
                require(pub['mathematical_claim_changes']==[] and pub['published_commit']==pub['confirmed_remote_ref'],'public pointer confirmation')
            aa,bb={c['id']:c for c in old['claims']},{c['id']:c for c in new['claims']};require(all(bb[k]==v for k,v in aa.items()),'existing claims unchanged')
            oa,na={v['id']:v for v in old['artifacts']},{v['id']:v for v in new['artifacts']};require(all(na[k]==v for k,v in oa.items()),'existing artifacts unchanged')
            added=[c['id'] for c in new['claims'] if c['id'] not in aa];require(added==rec['new_claim_ids'] and rec['registrar_performs_mathematical_verification'] is False and rec['validation']['valid'] and not rec['validation']['errors'],'registrar exact additions/schema only')
            additions+=added;last=(ROOT/after).read_bytes();chain.append(dict(name=name,before=sha(ROOT/before),after=sha(ROOT/after),added=added))
        require(additions==IDS and hashlib.sha256(last).hexdigest()==LH,'ten-claim cutoff');ledger=new;claims={c['id']:c for c in ledger['claims']};artifacts={r['id']:r for r in ledger['artifacts']}
        for cid in IDS:
            c=claims[cid];require(c['revision']==1 and c['status']=='VERIFIED' and c['review_state']=='CLEAR' and c['scope']['target_resolution']=='NONE' and c['scope']['unrestricted_target'] is False,'exact scoped current claim')
            for dep in c['dependencies']:require(claims[dep['id']]['revision']==dep['revision'],'pinned dependency')
            for eid in c['evidence']:pin(artifacts[eid]['path'],artifacts[eid]['sha256'])
            for v in c['verification']:
                require(v['claim_revision']==1 and v['outcome']=='PASS','saved claim-revision check')
                for aid,h in v['artifact_hashes'].items():require(artifacts[aid]['sha256']==h,'verification hashes')
        cp=load(CP,a.checkpoint_sha256);counts(cp,ledger);pin(SNAP,LH);require(cp['ledger_snapshot_sha256']==LH and (ROOT/SNAP).read_bytes()==last==(ROOT/'CLAIMS.yaml').read_bytes(),'frozen ledger exact')
        require(subprocess.check_output(['git','show',cp['source_commit']+':CLAIMS.yaml'],cwd=ROOT)==(ROOT/(B+'twentysecond_local_domains_registration/CLAIMS.before.yaml')).read_bytes(),'immutable public starting Git bytes')
        prev=load(B+'resume/twentyfirst_milestone_checkpoint.json',cp['previous_checkpoint_sha256']);require(prev['claim_population']==206,'prior checkpoint')
        for p,h in cp['evidence_sha256'].items():pin(p,h)
        proof=load(I+'hadamard_fifteen_profile_unsat_v2/summary.json');proof_metadata(proof)
        union=load(I+'hadamard_four_profile_union/summary.json');require(union['status']=='INDEPENDENT_FIXED_HADAMARD_FOUR_PROFILE_UNION_PASS' and all(union[k]==v for k,v in cp['four_profile_union'].items()),'independent exact union binding')
        arc=load(I+'hadamard_six_profile_arc_v3/summary.json');orb=load(I+'hadamard_six_fibre_orbits/summary.json');seven=load(I+'hadamard_seven_rank5_profiles/summary.json')
        require(arc['status']=='INDEPENDENT_SIX_EXCEPTION_PROFILE_ARC_SCREEN_PASS' and all(arc[k]==cp['six_profile_screen'][k] for k in ['relations','distinct_option_pairs','checked_deletions','checked_surviving_supports','Gram_pair_empty_profiles','combined_empty_profiles','nonempty_profiles']),'raw AC counts')
        require(orb['orbits']==164 and orb['recorded_nonempty_orbits']==55 and orb['AC_exclusion_validity_approved'] is False,'orbit coverage distinct from AC review')
        require(seven['labelled_feasible_marginal_profiles']==1608 and seven['complete_profile_sequences']==154214 and seven['saved_layers_checked']==2400 and seven['saved_state_witnesses_checked']==101146,'full independent marginal records')
        native=load(B+'hadamard_four_profile_native_campaign/summary.json');require(native['selected_cases']==CASES and native['completed_attempts']==15 and not native['unattempted_cases'] and native['wrapped_solver_wall_seconds']==cp['native_batch']['wrapped_solver_wall_seconds'] and native['end_to_end_wall_seconds']==cp['native_batch']['end_to_end_wall_seconds'],'campaign actual counts')
        catalogsummary=load(PACK+'summary.json',a.catalog_summary_sha256);require(catalogsummary['status']=='TWENTYSECOND_EXPLICIT_PUBLICATION_INVENTORY_PASS' and catalogsummary['claim_ids']==IDS,'final exact-cohort catalog')
        for p,h in catalogsummary['output_hashes'].items():pin(p,h)
        catalog=load(PACK+'catalog.json');inventory=load(PACK+'stage_inventory.json');entries=catalog['entries'];payload(entries,inventory['paths']);public=[r for r in entries if r['availability']=='READY_FOR_PUBLICATION'];pubpaths={r['path'] for r in public}
        require(len(entries)==catalogsummary['selected_files'] and len(public)==catalogsummary['public_research_files'] and sum(r['bytes'] for r in public)==catalogsummary['public_research_bytes'],'exact payload populations')
        require(catalogsummary['new_local_only_research_artifacts']==30 and catalogsummary['new_gzip_streams']==40,'15 model streams plus25 proof streams')
        for r in entries:
            pin(r['path'],r['sha256']);require((ROOT/r['path']).stat().st_size==r['bytes'],'literal payload size')
            if r['availability']=='READY_FOR_PUBLICATION':require(r['bytes']<=10*1024**2,'research payload ceiling')
        require(pubpaths<=set(inventory['paths']),'public staging coverage')
        for r in inventory['entries']:pin(r['path'],r['sha256'])
        compressed=(ROOT/(PACK+'reference_checks.json.gz')).read_bytes();require(compressed[3]&8==0 and compressed[4:8]==b'\0'*4,'deterministic gzip header')
        rawrefs=gzip.decompress(compressed);refs=json.loads(rawrefs);require(rawrefs==(json.dumps(refs,sort_keys=True,separators=(',',':'))+'\n').encode(),'lossless canonical JSON wrapper')
        require(refs['status']=='EXACT_HASH_CLOSURE_AND_GZIP_RECOVERY_PASS' and len(refs['records'])==catalogsummary['reference_bindings'] and len({r['path'] for r in refs['records']})==catalogsummary['unique_referenced_files'],'complete closure population')
        require(load(PACK+'reference_diagnostics.json')==dict(errors=[],count=0),'no omitted hash failures')
        for r in refs['records']:pin(r['path'],r['sha256']);require((ROOT/r['path']).stat().st_size==r['bytes'],'reference size')
        gitrows=load(PACK+'git_byte_checks.json');require(gitrows['status']=='CURRENT_GIT_FILTER_BYTES_PASS','saved Git filter pass')
        for r in gitrows['records']:
            require(r['path'] in pubpaths,'public Git payload');raw=(ROOT/r['path']).read_bytes();require(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==r['git_blob_sha1'],'literal Git blob identity')
        actual_git=subprocess.check_output(['git','hash-object','--stdin-paths'],cwd=ROOT,input=('\n'.join(r['path'] for r in gitrows['records'])+'\n').encode()).decode().splitlines();require(actual_git==[r['git_blob_sha1'] for r in gitrows['records']],'current actual Git filtering')
        packages=[];batch=load(B+'hadamard_four_profile_cnfs/summary.json');pm_path=B+'hadamard_four_profile_proof_package/package_manifest.json';pm=load(pm_path,'e55ce731d5ca1d18c4f5f5c9fc3195bc934f20f45b0172fc867ca1781e976250')
        require(batch['selection']==CASES==[r['case'] for r in pm['records']],'recovery input population')
        for r in batch['records']:
            m=load(r['model_package_path'],r['model_package_sha256']);packages.append(dict(path=m['raw_path'],sha256=m['raw_sha256'],bytes=m['raw_bytes'],parts=[dict(path=m['gzip_path'],gzip_sha256=m['gzip_sha256'],gzip_bytes=m['gzip_bytes'],raw_sha256=m['raw_sha256'],raw_bytes=m['raw_bytes'],raw_offset=0)]))
        for r in pm['records']:packages.append(dict(path=r['raw_original_path'],sha256=r['raw_sha256'],bytes=r['raw_bytes'],parts=[{**p,'path':str(Path(pm_path).parent/p['relative_path']).replace('\\','/')} for p in r['parts']]))
        require({p['path'] for p in packages}==LOCAL and len(packages)==30,'exact recoverable originals');recovery=[]
        for package in packages:
            for p in package['parts']:pin(p['path'],p['gzip_sha256']);require(p['path'] in pubpaths,'all transport parts public')
            data=[(ROOT/p['path']).read_bytes() for p in package['parts']];raw=recover(package,data);require(raw==(ROOT/package['path']).read_bytes(),'literal recovered/raw equality');recovery.append({k:package[k] for k in ['path','sha256','bytes']})
        require(sum(r['bytes'] for r in recovery)==catalogsummary['recovered_raw_bytes'],'recovered byte population')
        for p in [I+'hadamard_six_profile_arc/failure.json',I+'hadamard_six_profile_arc_v2/failure.json',I+'hadamard_fifteen_profile_unsat/failure.json',B+'resume/twentysecond_raw_recovery_v1_failure.json']:require(p in pubpaths,'failed attempts preserved')
        private=load(I+'hadamard_oriented_unknown/process_snapshot_availability.json','3b8c2c2549c5b70e84345f696d8029ac169304f26b922ffcf9c73be654f419d0');require('LOCAL_ONLY' in json.dumps(private) and 'OMIT' in json.dumps(private),'prior privacy unchanged')
        def safe_processes(x):
            if isinstance(x,dict):
                cmd=x.get('command')
                if isinstance(cmd,list) and any(str(v).rsplit('/',1)[-1]=='ps' for v in cmd):require('-C' in cmd and cmd[cmd.index('-C')+1]=='cadical' and '-e' not in cmd and '-eo' not in cmd,'targeted public process receipts')
                for v in x.values():safe_processes(v)
            elif isinstance(x,list):
                for v in x:safe_processes(v)
        for p in pubpaths:
            if p.endswith('.json'):safe_processes(json.loads((ROOT/p).read_bytes()))
        pin(REPORT,'f067b88f35fe7eb6f633f6ada7791879f4ef1e72b4ffd77e286710b91e37d848');pin(GUIDE);text=(ROOT/REPORT).read_text(encoding='utf8');guide=(ROOT/GUIDE).read_text(encoding='utf8')
        for cid in IDS:require(text.count(cid+' r1')==1 and claims[cid]['scope']['description'] in text,'exact claim row')
        for t in ['Ten independently checked claims','149,571,922','12,846,624','208,608','815,040','77,520','1,608 labelled profiles','154,214','2,400','101,146','Both stages start with within-group cap-filtered domains','zero new whole-support, core or unrestricted exclusions','216 claims: 213 VERIFIED/CLEAR, two CANDIDATE/CLEAR and one REFUTED/CLEAR','Four older missing traces and earlier privacy omissions remain unchanged']:require(t in text,'report scope/count '+t)
        for t in ['raw model/proof paths remain LOCAL_ONLY','25 gzip parts','149,571,922','Identity recovery is not DRAT verification','cannot be promised to run unchanged on a fresh machine','within-group cap-filtered domains','not a Gram-only-family exclusion','outside this publication cutoff']:
            # The guide describes the first-stage scope in a plural sentence.
            require(t in guide or (t=='not a Gram-only-family exclusion' and 'Neither count is a Gram-only-family exclusion' in guide),'guide boundary '+t)
        require(cp['timestamp'] in text and cp['source_commit'] in text and cp['next_experiment'] in text,'provenance/continuation')
        pin('acceleration/record_20260930_twentysecond_checkpoint.py',cp['writer_sha256'])
        for p in ['README.md','ACTIVE_RESEARCH.md','docs/RESEARCH_MAP.md','docs/REPRODUCING.md']:pin(p);require('TWENTYSECOND_WAVE' in (ROOT/p).read_text(encoding='utf8'),'updated entry point')
        validation=load(B+'resume/twentysecond_precommit_validation.json');require(validation['valid'] and not validation['errors'],'registry schema/semantics receipt')
        ex=cp['execution'];safe_processes(ex);require(ex['state']=={0:'CADICAL_PROCESS_OBSERVED',1:'NO_CADICAL_PROCESS_OBSERVED'}.get(ex['exit_code'],'UNKNOWN_OBSERVATION_ERROR'),'saved process state')
        for c in ['stdout','stderr']:pin(B+'resume/twentysecond_process_snapshot.'+c+'.log',ex[c+'_sha256'])
        rejected=[]
        def reject(label,fn):
            try:fn()
            except (ValueError,KeyError,TypeError,EOFError,gzip.BadGzipFile):rejected.append(label)
            else:raise ValueError('accepted corruption '+label)
        for label,path,value in [('count',['claim_population'],217),('target',['target_resolution'],'VERIFIED'),('whole_support',['new_whole_support_exclusions'],1),('Gram_only_scope',['necessary_unbalanced_counts','scope'],'Gram only.'),('all_984_feasible',['six_profile_screen','nonempty_profiles'],984),('missing_proof',['native_batch','complete_independent_proof_replays'],14),('marginals_as_factors',['seven_profile_screen','scope'],'Full factors.'),('overlapping_union',['four_profile_union','duplicate_coverage'],1)]:
            bad=deepcopy(cp);where=bad
            for k in path[:-1]:where=where[k]
            where[path[-1]]=value;reject(label,lambda bad=bad:counts(bad,ledger))
        reject('private_staged',lambda:payload(entries,inventory['paths']+[PRIVATE]));reject('future_staged',lambda:payload(entries,inventory['paths']+[B+'hadamard_all_triple_descent/summary.json']))
        bad=deepcopy(proof);bad['case_records'][0]['replay']['accepted']=False;reject('ignored_proof_veto',lambda:proof_metadata(bad))
        bad=deepcopy(proof);bad['case_records'][0]['cnf_sha256']='0'*64;reject('wrong_proof_input',lambda:proof_metadata(bad))
        package=next(p for p in packages if len(p['parts'])>1);parts=[(ROOT/p['path']).read_bytes() for p in package['parts']]
        reject('reversed_recovery_parts',lambda:recover(package,list(reversed(parts))));reject('truncated_recovery_part',lambda:recover(package,[parts[0][:-1]]+parts[1:]));bad=deepcopy(package);bad['sha256']='0'*64;reject('wrong_raw_hash',lambda:recover(bad,parts))
        stamp=datetime.now(timezone.utc).isoformat();proc=subprocess.run(ex['command'],cwd=ROOT,capture_output=True,timeout=15)
        for c,raw in [('stdout',proc.stdout),('stderr',proc.stderr)]:
            with (out/('current_process.'+c+'.log')).open('xb') as stream:stream.write(raw)
        observation=dict(timestamp=stamp,command=ex['command'],exit_code=proc.returncode,state={0:'CADICAL_PROCESS_OBSERVED',1:'NO_CADICAL_PROCESS_OBSERVED'}.get(proc.returncode,'UNKNOWN_OBSERVATION_ERROR'),scope='A separate fresh targeted observation; later-cohort activity does not alter the frozen checkpoint.')
        require(subprocess.check_output(['git','ls-files','--stage','-z'],cwd=ROOT)==index_before,'index unchanged')
        for p in [str(Path(__file__).relative_to(ROOT)).replace('\\','/'),'acceleration/audit_20260930_sixteenth_checkpoint.py','docs/AUDIT_20260930_TWENTYSECOND_CHECKPOINT_PLAN.md','uv.lock','pyproject.toml']:pin(p)
        write(out/'summary.json',dict(status='INDEPENDENT_TWENTYSECOND_CHECKPOINT_REPORT_CONSISTENCY_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,outputs_sha256={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in out.iterdir() if p.is_file()},registrar_chain=chain,new_claim_ids=IDS,counts=dict(claims=216,verified_clear=213,candidate_clear=2,refuted_clear=1,new_verified=10,public_payloads=len(public),public_bytes=sum(r['bytes'] for r in public),local_originals=30,complete_proof_bytes=149571922,gzip_streams=40,reference_bindings=len(refs['records']),referenced_files=len({r['path'] for r in refs['records']})),recovery=recovery,checkpoint_sha256=sha(ROOT/CP),report_sha256=sha(ROOT/REPORT),snapshot_sha256=LH,corruptions_rejected=rejected,saved_execution=ex,current_execution=observation,verifier='/root/structural_attack',scope='Metadata, byte identity, publication/recovery and reporting only; no mathematical reapproval.',shared_components=['Frozen duplicate-key-safe YAML/hash/write helpers from a prior independent audit; no recorder/registrar/packager imports.','Reviewer authored some earlier mathematical gates; their frozen results are bound here without new mathematical approval.'],limitations=['No native solver or DRAT replay.','Recovery checks identity, not proof validity.','Private historical stdout never read, hashed or published.','All wave23 work excluded.'],target_resolution='UNKNOWN',solver_calls=0,proof_replays=0))
        print(json.dumps(dict(status='INDEPENDENT_TWENTYSECOND_CHECKPOINT_REPORT_CONSISTENCY_PASS',summary_sha256=sha(out/'summary.json'))))
    except BaseException as e:write(out/'failure.json',dict(error=repr(e),source_sha256=sha(Path(__file__))));raise
if __name__=='__main__':main()
