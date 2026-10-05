"""Explicit request-driven first-unproved64 preparation and strict consolidation.

No producer, native, Git or ledger calls. This module does not run on import.
Historical proof gates are premises, not proof replays performed by this source.
"""
import argparse,copy,hashlib,json,platform,re,sys,traceback
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SPEC=Path(__file__).with_name(Path(__file__).stem+'_spec.md')
MANIFEST='acceleration/results/20260930_exact_eight_campaign_preparation/campaign_manifest.json'
MANIFEST_SHA='e7b07ea2f7c6b9f6738641afc22779a503841d5ac3da58d3873ebb0fa4b784ba'
PRODUCER='acceleration/theory_20260930_exact_eight_campaign.py'
SERIAL='acceleration/build_20260930_exact_eight_explicit_batch_v2.py'
SOURCE_PINS={SERIAL:'c5acba24df4c224dce98510a6a77b4ca490ed0cd632f56d674fccffc0d0d7c2b',PRODUCER:'9ebd87fea886f45fc916ad8afb9dc212fa089f760d4b96e55082926baef02c57'}
PROOF_STATUSES={'INDEPENDENT_EXACT_EIGHT_FIRST12_LITERAL_PROOFS_PASS':'SAT_pending','INDEPENDENT_EXACT_EIGHT_NEXT32_LITERAL_PROOFS_PASS':'SAT_verified','INDEPENDENT_EXACT_EIGHT_EXPLICIT_BATCH_LITERAL_PROOFS_PASS':'SAT_verified'}
ENCODING_STATUSES={'INDEPENDENT_EXACT_EIGHT_CAMPAIGN_ENCODING_PASS','INDEPENDENT_EXACT_EIGHT_NEXT32_ENCODING_PASS','INDEPENDENT_EXACT_EIGHT_EXPLICIT_BATCH_ENCODING_PASS'}
HEX=re.compile(r'[0-9a-f]{64}')

def need(ok,why):
    if not ok:raise ValueError(why)

def key(p):return p.resolve().relative_to(ROOT).as_posix()

def path(name,exists=True):
    need(type(name)is str and name and '\\'not in name and not Path(name).is_absolute(),'canonical relative path')
    p=(ROOT/name).resolve();need(p.is_relative_to(ROOT)and key(p)==name,'repository path without aliases')
    need(name not in ['PROMPT.md','acceleration/results/20260930_independent_review/hadamard_oriented_unknown/process.stdout.log']and not name.startswith(('tools/','external_conway99_research/')),'protected path')
    need(p.name.lower()not in {'.env','.env.local','credentials','credentials.json','id_rsa','id_ed25519'}and p.suffix.lower()not in {'.pem','.key'},'private file')
    if exists:need(p.is_file(),'existing input '+name)
    return p

def sha(p):
    with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()

def read(p):return json.loads(p.read_bytes())

def save(p,value):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(value,f,indent=2);f.write('\n')

def ref(p):return dict(path=key(p),sha256=sha(p))

class Store:
    def __init__(self):self.pins={}
    def pin(self,name,expected=None):
        p=path(name)
        if expected is not None:need(type(expected)is str and HEX.fullmatch(expected),'literal SHA256')
        if name not in self.pins:self.pins[name]=sha(p)
        need(expected is None or self.pins[name]==expected,'exact input SHA '+name)
        return p
    def load(self,name,expected=None):return read(self.pin(name,expected))
    def maps(self,obj):
        for field in ['inputs_sha256','outputs_sha256']:
            need(type(obj[field])is dict,'complete hash maps')
            for name,value in obj[field].items():self.pin(name,value)
    def unchanged(self):
        for name,value in self.pins.items():need(sha(path(name))==value,'input changed during operation '+name)

def count_bytes(counts):
    need(type(counts)is list and len(counts)==12 and all(type(row)is list and len(row)==20 and all(type(v)is list and len(v)==3 and all(type(x)is int and 0<=x<=3 for x in v)for v in row)for row in counts),'literal12x20x3 count table')
    return bytes(x for row in counts for v in row for x in v)

def population(store,name,pin):
    need(name==MANIFEST and pin==MANIFEST_SHA,'same frozen792 manifest')
    u=store.load(name,pin);rows=u['records']
    need(u['schema']=='EXACT_EIGHT_ALL792_CAMPAIGN_MANIFEST_V1'and u['universe_size']==len(rows)==792 and u['historical_profiles_subtracted']is False and u['prior_exclusions_used']is False,'complete un-subtracted population')
    need(len({r['case_id']for r in rows})==792 and [r['case_index']for r in rows]==list(range(792)),'unique exact manifest index order')
    need([(r['subset_index'],r['full_count_profile_sha256'])for r in rows]==sorted((r['subset_index'],r['full_count_profile_sha256'])for r in rows),'frozen subset/digest order')
    for r in rows:
        digest=hashlib.sha256(count_bytes(r['raw_representative']['counts'])).hexdigest()
        need(r['full_count_profile_sha256']==digest and r['case_id']=='exact_eight_'+digest,'literal raw count digest/case ID')
    return rows,{r['case_id']:r for r in rows}

def literal_proof_row(row,encoded,original,raw):
    need(row['outcome']=='UNSAT_VERIFIED'and row['trace']['complete_proof']is True,'only complete independently verified UNSAT')
    need(row['case_id']==encoded['case_id']==original['case_id']and row['case_index']==encoded['case_index']==original['case_index'],'literal manifest case index')
    need(row['full_count_profile_sha256']==encoded['full_count_profile_sha256']==original['full_count_profile_sha256'],'full count digest identity')
    need(count_bytes(raw['coordinate_group_fibre_counts'])==count_bytes(original['raw_representative']['counts']),'literal complete raw count equality')
    for field in ['cnf','scope']:need(row[field+'_path']==encoded[field+'_path']and row[field+'_sha256']==encoded[field+'_sha256'],'same independently checked formula '+field)
    replay=row['replay'];trace=row['trace']
    need(replay['accepted']is True and replay['expected_acceptance']is True and type(replay['actual_exit_code'])is int and replay['actual_exit_code']==0,'actual accepted complete replay exit')
    need(replay['cnf_sha256']==row['cnf_sha256']and replay['proof_sha256']==trace['sha256'],'literal replay CNF/trace identity')

def proof_skips(store,refs,byid):
    need(type(refs)is list and refs and len({r['path']for r in refs})==len(refs),'explicit nonempty distinct proof-gate list')
    done=[];review=[];normalized=[]
    for r in refs:
        need(type(r)is dict and {'path','sha256'}<=set(r)<= {'path','sha256','completed_cases'},'exact proof reference fields')
        gate=store.load(r['path'],r['sha256']);need(gate['status']in PROOF_STATUSES,'recognized independent complete proof status')
        n=gate['completed_proof_replays'];satkey=PROOF_STATUSES[gate['status']]
        need(type(n)is int and n>0 and gate[satkey]==0 and gate['UNKNOWN']==0 and gate['pending_case_ids']==[],'complete gate without pending/SAT/UNKNOWN')
        need('completed_cases'not in r or type(r['completed_cases'])is int and r['completed_cases']==n,'literal referenced count')
        store.maps(gate)
        binding_path=key(path(r['path']).parent/'claim_binding.json');need(binding_path in gate['outputs_sha256'],'bound original literal claim')
        binding=store.load(binding_path,gate['outputs_sha256'][binding_path]);need(binding['revision']==1 and binding['status']=='VERIFIED','approved exact literal proof claim')
        encodings=[]
        for name,pin in gate['inputs_sha256'].items():
            if name.endswith('/summary.json'):
                value=store.load(name,pin)
                if value.get('status')in ENCODING_STATUSES:encodings.append(value)
        rows=gate['case_records'];need(len(rows)==n and [x['case_id']for x in rows]==gate['selected_case_ids'],'every proof row in selected order')
        for row in rows:
            cid=row['case_id'];need(cid in byid and cid not in done,'unknown or duplicated literal exclusion refused')
            candidates=[x for g in encodings for x in g['checked_cases']if x['case_id']==cid and all(x[k]==row[k]for k in ['cnf_path','cnf_sha256','scope_path','scope_sha256'])]
            need(len(candidates)==1,'one independently checked formula identity')
            encoded=candidates[0];raw=store.load(encoded['profile_path'],encoded['profile_sha256'])
            literal_proof_row(row,encoded,byid[cid],raw)
            for field in ['cnf','scope']:store.pin(row[field+'_path'],row[field+'_sha256'])
            t=row['trace'];p=store.pin(t['path'],t['sha256']);need(type(t['bytes'])is int and p.stat().st_size==t['bytes'],'complete retained trace byte length')
            done.append(cid);review.append(dict(case_id=cid,case_index=row['case_index'],full_count_profile_sha256=row['full_count_profile_sha256'],proof_gate=dict(path=r['path'],sha256=r['sha256']),cnf_sha256=row['cnf_sha256'],proof_sha256=t['sha256'],proof_bytes=t['bytes']))
        normalized.append(dict(path=r['path'],sha256=r['sha256'],completed_cases=n))
    need(len(done)==len(set(done)),'duplicate exclusions never deduplicated')
    return done,normalized,review

def first64(universe,done):
    need(type(universe)is list and type(done)is list and all(type(x)is str for x in universe+done),'literal ID lists')
    need(len(universe)==len(set(universe))and len(done)==len(set(done))and set(done)<=set(universe),'distinct exact universe/skips')
    remaining=[cid for cid in universe if cid not in set(done)];need(len(remaining)>=64,'refuse fewer than64 remaining')
    return remaining[:64]

def selection_for(rows,done,gates,reason,authority):
    chosen=first64([r['case_id']for r in rows],done)
    need(type(reason)is str and bool(reason.strip()),'explicit root allocation reason')
    return dict(schema='EXACT_EIGHT_EXPLICIT_BUILD_SELECTION_V1',selection_policy='FIRST_UNPROVED_MANIFEST_PREFIX_V1',campaign_manifest_path=MANIFEST,campaign_manifest_sha256=MANIFEST_SHA,ordered_case_ids=chosen,selection_reason=reason,authorization_record_path=authority['path'],authorization_record_sha256=authority['sha256'],completed_proof_gates=gates,skipped_verified_case_ids=done,population=792,unresolved_before_batch=792-len(done),selected_instances=64)

def partition_for(parent,parent_ref,i):
    need(type(i)is int and 0<=i<4,'literal partition index')
    child=copy.deepcopy(parent);child.update(selection_policy='AUTHORIZED_DISJOINT_BUILD_PARTITION_V1',ordered_case_ids=parent['ordered_case_ids'][16*i:16*(i+1)],selection_reason=f'Explicit contiguous16-case partition{i} of the authenticated first-unproved64 selection; no new proof or skip inference.',parent_selection_path=parent_ref['path'],parent_selection_sha256=parent_ref['sha256'],partition_index=i,partition_offset=16*i,selected_instances=16)
    return child

def allocations(rows,out):
    need(type(rows)is list and len(rows)==4,'four explicit build outputs/attempt IDs');folders=[];attempts=[]
    for r in rows:
        need(type(r)is dict and set(r)=={'attempt_id','out'},'literal build allocation fields')
        p=path(r['out'],False);a=r['attempt_id'];need(type(a)is str and a and a.isascii()and all(c.isalnum()or c in '_-'for c in a),'safe explicit attempt')
        need(not p.exists()and not p.is_relative_to(out)and not out.is_relative_to(p),'new build output separate from selection output');folders.append(p);attempts.append(a)
    need(len(set(folders))==len(set(attempts))==4 and all(not a.is_relative_to(b)for a in folders for b in folders if a!=b),'disjoint outputs and attempts')

def stamp(commit):
    need(type(commit)is str and re.fullmatch('[0-9a-f]{40}',commit),'explicit recorded source commit')
    return dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=commit,source_commit_provenance='Caller-frozen request metadata; no current Git query.',command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),source_sha256=sha(Path(__file__)),native_calls=0,independent_approval=False)

def select(args,store,out):
    request=store.load(args.request,args.request_sha256)
    need(set(request)=={'schema','campaign_manifest_path','campaign_manifest_sha256','authorization_record_path','authorization_record_sha256','completed_proof_gates','selection_reason','build_allocations','recorded_source_commit'},'exact frozen request schema')
    need(request['schema']=='EXACT_EIGHT_PREFIX64_REQUEST_V1','request version')
    rows,byid=population(store,request['campaign_manifest_path'],request['campaign_manifest_sha256'])
    provenance=stamp(request['recorded_source_commit'])
    authority=dict(path=request['authorization_record_path'],sha256=request['authorization_record_sha256']);store.pin(authority['path'],authority['sha256'])
    done,gates,review=proof_skips(store,request['completed_proof_gates'],byid);allocations(request['build_allocations'],out)
    parent=selection_for(rows,done,gates,request['selection_reason'],authority);save(out/'selection.json',parent);pr=ref(out/'selection.json');parts=[]
    for i in range(4):
        p=out/f'partition_{i:02d}.json';save(p,partition_for(parent,pr,i));parts.append(ref(p))
    launch=dict(schema='EXACT_EIGHT_FOUR_SERIAL_BUILD_PLAN_V1',parent_selection_path=pr['path'],parent_selection_sha256=pr['sha256'],workers=4,seconds_per_chunk=120,build_selections=[dict(**r,**a)for r,a in zip(parts,request['build_allocations'],strict=True)])
    save(out/'launch_plan.json',launch);save(out/'prior_proof_identity_review.json',review);store.unchanged()
    save(out/'summary.json',dict(provenance,status='CANDIDATE_EXACT_EIGHT_PREFIX64_SELECTION_PREPARED',inputs_sha256=store.pins,outputs_sha256={key(p):sha(p)for p in out.iterdir()if p.is_file()},selection=pr,build_selections=parts,launch_plan=ref(out/'launch_plan.json'),selected_case_ids=parent['ordered_case_ids'],skipped_verified_case_ids=done,selected_case_indices=[byid[cid]['case_index']for cid in parent['ordered_case_ids']],producer_calls=0,scope='Selection/provenance only; no build, search, proof replay or universe exclusion.'))

def checked_invocation(store,summary_ref,part,part_ref,allocation,byid):
    sp=store.pin(summary_ref['path'],summary_ref['sha256']);b=read(sp);ids=part['ordered_case_ids']
    need(key(sp.parent)==allocation['out'],'build output matches frozen launch plan')
    need(b['status']=='CANDIDATE_EXACT_EIGHT_EXPLICIT_FORMULAS_COMPLETE'and b['completed_formulas']==b['producer_calls']==16 and b['pending_case_ids']==[]and b['stop']is None,'all16 complete without timeout/retry')
    need(b['selected_case_ids']==ids==[r['case_id']for r in b['records']]and b['native_calls']==b['previous_outcomes_consumed']==0,'literal ordered native-free invocation')
    need(all(b[k]is False for k in ['independent_approval','automatic_resume','automatic_skip']),'no automatic outcome promotion')
    store.maps(b);plan=store.load(key(sp.parent/'plan.json'));need(plan['schema']=='EXACT_EIGHT_EXPLICIT_BUILD_PLAN_V1'and plan['mode']=='build'and plan['inputs_sha256']==b['inputs_sha256'],'literal build origin')
    need(plan['selection_path']==part_ref['path']and plan['selection_sha256']==part_ref['sha256']and plan['ordered_case_ids']==ids and plan['allocation_seconds']==120 and plan['attempt_id']==allocation['attempt_id'],'original partition/attempt/allocation')
    need(plan['automatic_resume']is False and plan['automatic_skip']is False and plan['native_calls']==plan['previous_outcomes_consumed']==0,'source-only build protocol')
    need(len(plan['commands'])==16,'all16 explicit producer commands')
    names={'summary.json','instance.cnf','model.json','scope.json','selected_profile.json','initial_domains.json','selection.json','model_package.json'}
    for i,r in enumerate(b['records']):
        orig=byid[r['case_id']];folder=sp.parent/f"case_{orig['case_index']:04d}";attempt=plan['attempt_id']+f"_case_{orig['case_index']:04d}"
        need(all(r[k]==orig[k]for k in ['case_index','subset_index','full_count_profile_sha256'])and r['attempt_id']==attempt,'case/count/attempt identity')
        command=[plan['commands'][i]['command'][0],'-B',str(path(PRODUCER)),'build','--campaign-manifest',str(path(MANIFEST)),'--campaign-manifest-sha256',MANIFEST_SHA,'--case-id',r['case_id'],'--attempt-id',attempt,'--out',str(folder)]
        need(plan['commands'][i]==dict(case_id=r['case_id'],case_index=r['case_index'],subset_index=r['subset_index'],attempt_id=attempt,output_path=key(folder),command=command),'exact leaf producer command')
        need(set(r['files'])==names,'all eight original artifacts')
        for name,f in r['files'].items():
            need(f['path']==key(folder/name),'literal file path');p=store.pin(f['path'],f['sha256']);need(p.stat().st_size==f['bytes'],'literal file size')
        rec=store.load(key(sp.parent/f'case_{i:03d}.receipt.json'))
        need(rec['command']==command and rec['case_id']==r['case_id']and rec['attempt_id']==attempt and type(rec['actual_exit_code'])is int and rec['actual_exit_code']==0 and rec['outer_guard_expired']is False and rec['producer_calls']==1 and rec['native_calls']==0,'successful actual build receipt')
        chk=store.load(key(sp.parent/f'checkpoint_{i+1:03d}.json'))
        need(chk==dict(status='CANDIDATE_EXPLICIT_BUILD_PREFIX',selected_case_ids=ids,completed_records=b['records'][:i+1],pending_case_ids=ids[i+1:],native_calls=0,producer_calls=i+1,selection_sha256=part_ref['sha256'],automatic_resume=False,automatic_skip=False),'all complete immutable prefix checkpoints')
        raw=store.load(r['files']['selected_profile.json']['path'],r['files']['selected_profile.json']['sha256'])
        need(count_bytes(raw['coordinate_group_fibre_counts'])==count_bytes(orig['raw_representative']['counts']),'raw built count table')
    return b

def consolidate(args,store,out):
    parent=store.load(args.selection,args.selection_sha256);rows,byid=population(store,parent['campaign_manifest_path'],parent['campaign_manifest_sha256'])
    authority=dict(path=parent['authorization_record_path'],sha256=parent['authorization_record_sha256']);store.pin(authority['path'],authority['sha256'])
    done,gates,review=proof_skips(store,parent['completed_proof_gates'],byid)
    need(parent==selection_for(rows,done,gates,parent['selection_reason'],authority),'entire same first-unproved64 selection')
    launch=store.load(args.launch_plan,args.launch_plan_sha256);pr=dict(path=args.selection,sha256=args.selection_sha256)
    need(launch['schema']=='EXACT_EIGHT_FOUR_SERIAL_BUILD_PLAN_V1'and launch['parent_selection_path']==pr['path']and launch['parent_selection_sha256']==pr['sha256']and launch['workers']==4 and launch['seconds_per_chunk']==120,'same frozen four16 launch plan')
    need(args.build_summary and len(args.build_summary)==4 and len(launch['build_selections'])==4,'four explicit complete build references')
    need(len({r[0]for r in args.build_summary})==4,'no repeated build receipt')
    records=[];parts=[];summaries=[];attempts=[];folders=[]
    for i,((name,pin),entry)in enumerate(zip(args.build_summary,launch['build_selections'],strict=True)):
        part=store.load(entry['path'],entry['sha256']);need(part==partition_for(parent,pr,i),'literal exact partition')
        part_ref=dict(path=entry['path'],sha256=entry['sha256']);b=checked_invocation(store,dict(path=name,sha256=pin),part,part_ref,entry,byid)
        records.extend(b['records']);parts.append(part_ref);summaries.append(dict(path=name,sha256=pin));attempts.append(entry['attempt_id']);folders.append(path(entry['out'],False))
    need(len(set(attempts))==len(set(folders))==4 and all(not a.is_relative_to(b)for a in folders for b in folders if a!=b),'four disjoint attempts/outputs')
    need([r['case_id']for r in records]==parent['ordered_case_ids']and len({r['case_id']for r in records})==64,'exact complete64 union')
    store.unchanged()
    save(out/'summary.json',dict(stamp(args.recorded_source_commit),status='CANDIDATE_EXACT_EIGHT_EXPLICIT_FORMULAS_COMPLETE',schema='EXACT_EIGHT_EXPLICIT_BUILD_CONSOLIDATION_V1',inputs_sha256=store.pins,records=records,selected_case_ids=parent['ordered_case_ids'],completed_formulas=64,pending_case_ids=[],producer_calls=64,build_summaries=summaries,build_selections=parts,original_selection=pr,launch_plan=dict(path=args.launch_plan,sha256=args.launch_plan_sha256),automatic_resume=False,automatic_skip=False,limitations=['Artifact identity aggregation only; independent clause/encoding review remains required.','Four separately budgeted120-second serial allocations, not one global120-second deadline.','No completed native outcome inferred from a formula build; no retry or unverified proof skip.']))

def main():
    ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='mode',required=True)
    a=sub.add_parser('select');a.add_argument('--request',required=True);a.add_argument('--request-sha256',required=True);a.add_argument('--out',required=True)
    a=sub.add_parser('consolidate')
    for field in ['selection','selection-sha256','launch-plan','launch-plan-sha256','recorded-source-commit','out']:a.add_argument('--'+field,required=True)
    a.add_argument('--build-summary',nargs=2,action='append',required=True,metavar=('PATH','SHA256'))
    args=ap.parse_args();out=path(args.out,False);need(not out.exists(),'fresh output only');out.mkdir(parents=True,exist_ok=False);store=Store()
    try:
        for name,pin in SOURCE_PINS.items():store.pin(name,pin)
        for p in [Path(__file__),SPEC]:store.pin(key(p))
        (select if args.mode=='select'else consolidate)(args,store,out)
    except BaseException as ex:
        save(out/'failure.json',dict(error=repr(ex),traceback=traceback.format_exc(),inputs_sha256=store.pins,source_sha256=sha(Path(__file__)),command=[sys.executable,*sys.argv],native_calls=0,producer_calls=0,independent_approval=False));raise

if __name__=='__main__':main()
