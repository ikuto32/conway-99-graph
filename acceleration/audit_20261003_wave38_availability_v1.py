"""Independent Wave38 availability-only checking; no producer imports or ledger writes."""
import argparse,copy,gzip,hashlib,json,platform,re,subprocess,sys,tarfile,time
from datetime import datetime,timezone
from pathlib import Path,PurePosixPath
import yaml
from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
COMMIT='2d578fa8171597d7a009f02f0d92ee987de24555'
BEFORE='cc8184dbe3c0c1bc6d539e8925fc392b80a3a4344c29e051118af0157d948a2c'
BASE='acceleration/results/20261003_wave38_registration01/CLAIMS.before.yaml'
FROZEN='acceleration/results/20261003_wave38_milestone02/CLAIMS.yaml'
STAGE='acceleration/results/20261003_wave38_milestone02/manifest.json'
STAGE_SHA='27dc978a9206aff0c245ab8f673525487f5dadec54683c6afd035dad648e5894'
NUL='acceleration/results/20261003_wave38_milestone02/stage_paths.nul'
PACKAGES=[
 ('acceleration/results/20261002_wave33_model_package01/manifest.json','c3efa198c5f48eddb5ead69a4bb130a3dc55567bb298856143c6fb62eb0e0145',
  'acceleration/results/20261002_independent_review/wave33_model_recovery01/summary.json','b9352a5e5810f20ff9187c06f5e00636f2f3abad2810ed3d7c23df655b76f583'),
 ('acceleration/results/20261002_wave33_reconstruction_package01/manifest.json','f639431b7ea9ce0f1500ea48b002629d2523271eead700217dd512e8ade66989',
  'acceleration/results/20261002_independent_review/wave33_reconstruction_recovery01/summary.json','09623c7c36a6b6b4d7905992361721f38b9ea7778fe7493f01455a4de90d1ba5'),
 ('acceleration/results/20261003_wave36_coupling_package01/manifest.json','38f641ec21ec3d1d617515e8b3e578e098886863f7016ad640ac1906e8b0988f',
  'acceleration/results/20261003_independent_review/wave36_census_recovery01/summary.json','659827807687970e2ca5ab714ba779a703fc9223f84bbe29fd4edc1c7259079b'),
 ('acceleration/results/20261003_wave37_rooted8_package01/manifest.json','ea48c30dfa68fe70bad17edbfd3697d8a2dcf28f9ab24b63d0d66895e7eb9b14',
  'acceleration/results/20261003_independent_review/wave37_recovery01/summary.json','6dd37b0d65e16522a71ac8a07419907b281ea96f5638bbab170678122564392c')]

class AuditError(ValueError):
    def __init__(self,stage,detail=''):
        self.stage=stage;super().__init__(stage+(': '+detail if detail else ''))

def need(ok,stage,detail=''):
    if not ok:raise AuditError(stage,detail)

class UniqueLoader(yaml.SafeLoader):pass
def unique(loader,node,deep=False):
    result={}
    for key,value in node.value:
        key=loader.construct_object(key,deep=deep)
        need(key not in result,'DUPLICATE_YAML_KEY',str(key))
        result[key]=loader.construct_object(value,deep=deep)
    return result
UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,unique)

def digest(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

def indexed(rows):
    result={}
    for row in rows:
        need(row['id'] not in result,'DUPLICATE_ID');result[row['id']]=row
    return result

def guard(deadline):need(deadline.status()['remaining_seconds']>20,'DEADLINE','shutdown reserve')

def archive_hashes(names,deadline):
    result={};commands=[]
    for start in range(0,len(names),40):
        guard(deadline);batch=names[start:start+40]
        command=['git','archive','--format=tar',COMMIT,'--',*batch];commands.append(command)
        child=subprocess.Popen(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        try:
            with tarfile.open(fileobj=child.stdout,mode='r|') as archive:
                for member in archive:
                    guard(deadline)
                    if not member.isfile():continue
                    need(member.name in batch and member.name not in result,'ARCHIVE_MEMBER_POPULATION',member.name)
                    h=hashlib.sha256();count=0;stream=archive.extractfile(member)
                    for block in iter(lambda:stream.read(1024*1024),b''):h.update(block);count+=len(block)
                    need(count==member.size,'ARCHIVE_COMPLETE_MEMBER')
                    result[member.name]={'sha256':h.hexdigest(),'bytes':count}
            # Retain the independently calibrated stdout-drain fix. No Git
            # archive stderr/wait before consuming its residual tar padding.
            for block in iter(lambda:child.stdout.read(65536),b''):need(not any(block),'ARCHIVE_TRAILING_PADDING')
            stderr=child.stderr.read().decode('utf8',errors='replace')
            need(child.wait(timeout=10)==0,'ARCHIVE_EXIT',stderr)
            need(set(batch)<=set(result),'ARCHIVE_NO_OMITTED_MEMBER')
        finally:
            if child.poll() is None:child.kill();child.wait(timeout=5)
    return result,commands

def decoded_records(package,name,identity,blobs,deadline):
    result={};parts=compressed=0
    for row in package['records']:
        guard(deadline);path=row['raw_path'];need(path not in result,'DUPLICATE_RAW_PATH')
        whole=hashlib.sha256();offset=0
        for part in row['parts']:
            guard(deadline);need(part['raw_offset']==offset,'RAW_CONTIGUOUS_OFFSET')
            need(blobs[part['path']]=={'sha256':part['gzip_sha256'],'bytes':part['gzip_bytes']},'IMMUTABLE_GZIP_HASH')
            need(digest(ROOT/part['path'])==part['gzip_sha256'],'LOCAL_GZIP_IMMUTABLE_IDENTITY')
            chunk=hashlib.sha256();count=0
            with gzip.open(ROOT/part['path'],'rb') as stream:
                for block in iter(lambda:stream.read(1024*1024),b''):
                    need(count+len(block)<=part['raw_bytes'],'RAW_PART_DECLARED_LENGTH')
                    whole.update(block);chunk.update(block);count+=len(block)
            need(count==part['raw_bytes'] and chunk.hexdigest()==part['raw_sha256'],'RAW_PART_IDENTITY')
            offset+=count;parts+=1;compressed+=part['gzip_bytes']
        need(offset==row['raw_bytes'] and whole.hexdigest()==row['raw_sha256'],'RAW_WHOLE_IDENTITY')
        need(path not in blobs,'RAW_INTENTIONALLY_ABSENT_FROM_GIT')
        result[path]={'sha256':whole.hexdigest(),'bytes':offset,'manifest':name,'manifest_sha256':identity}
    return result,parts,compressed

def transition(before,after,baseline,direct,raw):
    need(before['claims']==after['claims'],'CLAIMS_AND_VERIFICATION_UNCHANGED')
    need(before['claims'][:len(baseline['claims'])]==baseline['claims'],'BASELINE343_CLAIMS_UNCHANGED')
    need(len(after['claims'])==350,'EXACT_CLAIM_POPULATION')
    for key in set(before)|set(after):
        if key not in ('artifacts','updated_at'):need(before[key]==after[key],'TOPLEVEL_UNCHANGED',key)
    need(after['target']['status']=='UNKNOWN' and after['target']['overall_search_coverage'] is None,'TARGET_UNKNOWN')
    old,new,prior=map(indexed,(before['artifacts'],after['artifacts'],baseline['artifacts']))
    need(set(old)==set(new),'ARTIFACT_ID_POPULATION_UNCHANGED')
    need([new[row['id']] for row in before['artifacts']]==after['artifacts'],'ARTIFACT_ORDER_UNCHANGED')
    need(all(old[aid]==value==new[aid] for aid,value in prior.items()),'ALL_PRIOR_ARTIFACTS_UNCHANGED')
    changed=[];retained=[];prefix='https://github.com/ikuto32/conway-99-graph/blob/'+COMMIT+'/'
    for aid,a in old.items():
        if aid in prior:continue
        b=new[aid]
        excluded=('availability','retrieval','unavailable_reason')
        need({k:v for k,v in a.items() if k not in excluded}=={k:v for k,v in b.items() if k not in excluded},'ARTIFACT_IDENTITY_UNCHANGED',aid)
        path=a['path'];entry=raw.get(path) or direct.get(path)
        if entry is None:
            need(a==b,'UNAUTHENTICATED_ARTIFACT_NOT_PROMOTED',aid);retained.append(aid);continue
        need(entry['sha256']==a['sha256'],'AUTHENTICATED_ARTIFACT_HASH',aid)
        need(b['availability']=='PUBLIC' and b['unavailable_reason'] is None,'EXACT_PUBLIC_AVAILABILITY',aid)
        need(isinstance(b['retrieval'],str),'RETRIEVAL_TEXT')
        links=re.findall(r'https://[^\s;]+',b['retrieval'])
        if path in raw:
            need(links==[prefix+entry['manifest']] and path in b['retrieval'] and a['sha256'] in b['retrieval'] and 'fresh destination' in b['retrieval'] and 'not mathematical replay' in b['retrieval'],'LOSSLESS_IMMUTABLE_RETRIEVAL',aid)
        else:need(links==[prefix+path] and 'Historical transitive' in b['retrieval'],'DIRECT_IMMUTABLE_RETRIEVAL',aid)
        changed.append(aid)
    return changed,retained

def rejection(rows,label,expected,call):
    try:call()
    except AuditError as error:
        need(error.stage==expected,'CONTROL_EXACT_STAGE',str(error));rows.append({'label':label,'stage':error.stage,'diagnostic':str(error)})
    else:raise AuditError('CONTROL_ACCEPTED',label)

def calibration(before,baseline,out,deadline):
    """Metadata-only synthetic transitions and tiny real gzip/raw controls."""
    prior=indexed(baseline['artifacts']);new=[a for a in before['artifacts'] if a['id'] not in prior]
    direct={a['path']:{'sha256':a['sha256']} for a in new if a['path'] is not None}
    # This table calibrates logic only. It does not establish real publication.
    after=copy.deepcopy(before);prefix='https://github.com/ikuto32/conway-99-graph/blob/'+COMMIT+'/'
    for a in after['artifacts']:
        if a['id'] not in prior and a['path'] in direct:a.update(availability='PUBLIC',retrieval=prefix+a['path']+'; Historical transitive closure remains separate.',unavailable_reason=None)
    changed,retained=transition(before,after,baseline,direct,{})
    controls=[]
    for label,stage,mutate in [
        ('statement','CLAIMS_AND_VERIFICATION_UNCHANGED',lambda a:a['claims'][0].update(statement='corrupted')),
        ('verification','CLAIMS_AND_VERIFICATION_UNCHANGED',lambda a:a['claims'][0]['verification'][0].update(outcome='FAIL')),
        ('target','TOPLEVEL_UNCHANGED',lambda a:a['target'].update(status='NONEXISTENCE')),
        ('prior_hash','ALL_PRIOR_ARTIFACTS_UNCHANGED',lambda a:a['artifacts'][0].update(sha256='0'*64)),
        ('omitted_claim','CLAIMS_AND_VERIFICATION_UNCHANGED',lambda a:a['claims'].pop()),
        ('omitted_artifact','ARTIFACT_ID_POPULATION_UNCHANGED',lambda a:a['artifacts'].pop())]:
        damaged=copy.deepcopy(after);mutate(damaged)
        rejection(controls,label,stage,lambda:transition(before,damaged,baseline,direct,{}))
    synthetic={'id':'synthetic-missing-control','path':'build/synthetic-missing-publication.bin','sha256':'0'*64,'availability':'LOCAL_ONLY','retrieval':None,'unavailable_reason':'Synthetic control only.'}
    b=copy.deepcopy(before);a=copy.deepcopy(after);b['artifacts'].append(synthetic);a['artifacts'].append(copy.deepcopy(synthetic))
    need(transition(b,a,baseline,direct,{})[1]==['synthetic-missing-control'],'MISSING_POSITIVE_RETAINED')
    a['artifacts'][-1]['availability']='PUBLIC'
    rejection(controls,'missing_false_public','UNAUTHENTICATED_ARTIFACT_NOT_PROMOTED',lambda:transition(b,a,baseline,direct,{}))
    name=out.relative_to(ROOT).as_posix()+'/tiny.raw';payload=b'wave38 calibration raw bytes\n'*3;rawhash=hashlib.sha256(payload).hexdigest()
    parts=[];blobs={}
    for index,(offset,piece) in enumerate(((0,payload[:20]),(20,payload[20:]))):
        path=out.relative_to(ROOT).as_posix()+'/tiny_'+str(index)+'.gz';data=gzip.compress(piece,mtime=0);(ROOT/path).write_bytes(data)
        parts.append({'path':path,'gzip_sha256':hashlib.sha256(data).hexdigest(),'gzip_bytes':len(data),'raw_offset':offset,'raw_sha256':hashlib.sha256(piece).hexdigest(),'raw_bytes':len(piece)})
        blobs[path]={'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
    package={'records':[{'raw_path':name,'raw_sha256':rawhash,'raw_bytes':len(payload),'parts':parts}]}
    raw,pc,gc=decoded_records(package,'synthetic-package.json','1'*64,blobs,deadline)
    need(raw[name]['sha256']==rawhash and pc==2,'TINY_COMPLETE_DECODE')
    entry={'id':'synthetic-raw-control','path':name,'sha256':rawhash,'availability':'LOCAL_ONLY','retrieval':None,'unavailable_reason':'Synthetic control only.'}
    b=copy.deepcopy(before);a=copy.deepcopy(after);b['artifacts'].append(entry);a['artifacts'].append(copy.deepcopy(entry))
    a['artifacts'][-1].update(availability='PUBLIC',unavailable_reason=None,retrieval='Lossless public package: '+prefix+'synthetic-package.json; restore into a fresh destination; '+name+'; '+rawhash+'; not mathematical replay.')
    transition(b,a,baseline,direct,raw);a['artifacts'][-1]['retrieval']='https://github.com/ikuto32/conway-99-graph/blob/main/unknown'
    rejection(controls,'mutable_raw_retrieval','LOSSLESS_IMMUTABLE_RETRIEVAL',lambda:transition(b,a,baseline,direct,raw))
    for label,stage,mutate in [
        ('dropped_part','RAW_WHOLE_IDENTITY',lambda p:p['records'][0]['parts'].pop()),
        ('raw_hash','RAW_WHOLE_IDENTITY',lambda p:p['records'][0].update(raw_sha256='0'*64)),
        ('offset','RAW_CONTIGUOUS_OFFSET',lambda p:p['records'][0]['parts'][1].update(raw_offset=1)),
        ('compressed_hash','IMMUTABLE_GZIP_HASH',lambda p:p['records'][0]['parts'][0].update(gzip_sha256='0'*64))]:
        damaged=copy.deepcopy(package);mutate(damaged)
        rejection(controls,label,stage,lambda:decoded_records(damaged,'synthetic-package.json','1'*64,blobs,deadline))
    damaged=copy.deepcopy(after);indexed(damaged['artifacts'])[changed[0]]['retrieval']=prefix+'wrong'
    rejection(controls,'wrong_direct_retrieval','DIRECT_IMMUTABLE_RETRIEVAL',lambda:transition(before,damaged,baseline,direct,{}))
    return {'controls':controls,'new_artifact_population':len(new),'new_artifacts':new,'synthetic_direct_logic_only':True,'positive_tiny_gzip':{'raw_bytes':len(payload),'gzip_parts':pc,'gzip_bytes':gc}}

def stage_scope(stage,nul):
    need(stage['schema']=='WAVE38_FIXED350_EXPLICIT_PUBLICATION_ALLOWLIST_V1' and stage['current_claims']==350 and stage['previous_claims']==343 and stage['ledger_sha256']==BEFORE
         and stage['before_ledger_sha256']=='b2df016825e41180c2d22d04835ce3922d13384b4c3803e9adb39d56b204384d','FROZEN_STAGE_SCOPE')
    need(stage['direct_record_count']==len(stage['records'])==612 and sum(r['bytes'] for r in stage['records'])==stage['direct_bytes']==174036218,'EXACT_STAGE_COUNT')
    members=[r['path'] for r in stage['records']];metadata=stage['self_metadata_paths']
    need(len(set(members))==len(members) and len(metadata)==13 and not(set(members)&set(metadata)),'UNIQUE_STAGE_MEMBERS')
    need(len(set(metadata))==13 and STAGE in metadata and FROZEN in metadata and NUL in metadata,'EXACT_STAGE_SELF_METADATA')
    need(nul.endswith(b'\0') and hashlib.sha256(nul).hexdigest()==stage['stage_paths_sha256']=='25d93927303fcce492d6d00f87fc6d6ac1737372672bce729f476c81e72dbfcf','EXACT_STAGE_NUL_HASH')
    labels=nul[:-1].decode('utf8').split('\0');need(len(labels)==stage['stage_paths_count']==625 and labels==sorted(set(members)|set(metadata)),'EXACT_STAGE_NUL_POPULATION')
    need(len(stage['omitted'])==8 and len({r['path'] for r in stage['omitted']})==8 and not({r['path'] for r in stage['omitted']}&set(labels)),'EXACT_EIGHT_RAW_OMISSIONS')
    return labels

def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=('calibration','full'))
    ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--publication-dir',type=Path);ap.add_argument('--receipt-sha256');ap.add_argument('--after-sha256')
    ap.add_argument('--producer-source');ap.add_argument('--producer-source-sha256');ap.add_argument('--producer-supervisor',type=Path)
    ap.add_argument('--calibration',type=Path);ap.add_argument('--calibration-sha256')
    args=ap.parse_args();start=time.monotonic();deadline=CommandDeadline(args.seconds,allocation_reason='Independent350-claim publication bookkeeping and bounded immutable archive/367MB streaming recovery')
    out=args.out.resolve();need(out.is_relative_to(ROOT),'BOUNDED_OUTPUT');out.mkdir(parents=True,exist_ok=False);pins={}
    def pin(name,identity=None):
        name=Path(name).as_posix();actual=digest(ROOT/name);need(identity is None or identity==actual,'INPUT_PIN',name);pins[name]=actual;return actual
    def read(name,identity=None):pin(name,identity);return json.loads((ROOT/name).read_bytes())
    def ledger(name,identity=None):pin(name,identity);return yaml.load((ROOT/name).read_text(encoding='utf8'),Loader=UniqueLoader)
    live_ledger=pin('CLAIMS.yaml');live_index=pin('.git/index')
    before=ledger(FROZEN,BEFORE);baseline=ledger(BASE,'b2df016825e41180c2d22d04835ce3922d13384b4c3803e9adb39d56b204384d')
    need(len(before['claims'])==350 and len(baseline['claims'])==343,'FROZEN350_AND343_POPULATIONS')
    stage=read(STAGE,STAGE_SHA)
    pin(NUL);nul=(ROOT/NUL).read_bytes();stage_members=stage_scope(stage,nul)
    records={r['path']:r for r in stage['records']}
    need(len(records)==len(stage['records']),'UNIQUE_STAGE_MEMBERS')
    for name in (Path(__file__).relative_to(ROOT).as_posix(),'acceleration/audit_20261003_wave38_availability_v1_spec.md','acceleration/audit_20261003_wave37_availability_v1.py','acceleration/audit_20261003_wave37_availability_v1_spec.md','acceleration/command_deadline.py','acceleration/run_compute_command.py','uv.lock','pyproject.toml'):
        pin(name)
    controls=calibration(before,baseline,out,deadline)
    for label,code,mutate in [('wrong_ledger_population','FROZEN_STAGE_SCOPE',lambda s:s.update(current_claims=349)),('wrong_prior_scope','FROZEN_STAGE_SCOPE',lambda s:s.update(previous_claims=337)),('omitted_direct_member','EXACT_STAGE_COUNT',lambda s:s['records'].pop()),('duplicated_self_member','EXACT_STAGE_SELF_METADATA',lambda s:s['self_metadata_paths'].__setitem__(0,s['self_metadata_paths'][1])),('omitted_raw_claim','EXACT_EIGHT_RAW_OMISSIONS',lambda s:s['omitted'].pop())]:
        damaged=copy.deepcopy(stage);mutate(damaged);rejection(controls['controls'],label,code,lambda:stage_scope(damaged,nul))
    rejection(controls['controls'],'damaged_stage_nul','EXACT_STAGE_NUL_HASH',lambda:stage_scope(stage,nul[:-1]))
    blobs,reader_commands=archive_hashes([STAGE,FROZEN],deadline)
    need(blobs[STAGE]['sha256']==STAGE_SHA and blobs[FROZEN]['sha256']==BEFORE,'NEW_READER_LITERAL_ANCHORS')
    report={'timestamp':datetime.now(timezone.utc).isoformat(),'verifier':'/root/checkpoint_audit','producer':'/root','source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'command':[sys.executable,*sys.argv],'cwd':str(ROOT),'python':platform.python_version(),'publication_commit':COMMIT,'inputs_sha256':pins,'before_ledger_sha256':BEFORE,'unchanged_claims':350,'new_claims':0,'mathematical_replays':0,'new_exclusions':0,'target_resolution':'UNKNOWN','overall_search_coverage':'UNKNOWN; no validated denominator.','calibration':controls,'reader_calibration':{'commands':reader_commands,'literal_records':blobs,'outcome':'PASS'},'shared_components':['Preserved independent Wave37 archive/streaming and exact-transition implementations adapted to new350-record scope; no publication producer imported.','Git archive/tree implementations, Python gzip/SHA256, duplicate-key rejecting YAML loader, command_deadline and supported Job supervisor.'],'limitations':['Byte-publication checking only; no mathematical replay or target resolution.','Calibration synthetic metadata tests transition logic, not real availability.','Historical complete transitive evidence/platform-binary availability remains separately recorded.']}
    report['calibration_timing']='Fresh independent controls before full checking; publication producer had already completed. No pre-output calibration is claimed.'
    if args.mode=='calibration':report['status']='INDEPENDENT_WAVE38_AVAILABILITY_V1_PREFULL_CALIBRATION_PASS'
    else:
        need(all((args.publication_dir,args.receipt_sha256,args.after_sha256,args.producer_source,args.producer_source_sha256,args.producer_supervisor,args.calibration,args.calibration_sha256)),'FULL_EXACT_ARGUMENTS')
        prior_cal=read(args.calibration,args.calibration_sha256)
        need(prior_cal['status']=='INDEPENDENT_WAVE38_AVAILABILITY_V1_PREFULL_CALIBRATION_PASS' and prior_cal['inputs_sha256'][Path(__file__).relative_to(ROOT).as_posix()]==pins[Path(__file__).relative_to(ROOT).as_posix()],'APPLICABLE_PREFULL_CALIBRATION')
        pub=args.publication_dir.as_posix();after=ledger(pub+'/CLAIMS.after.yaml',args.after_sha256)
        need(ledger(pub+'/CLAIMS.before.yaml',BEFORE)==before,'EXACT_FROZEN_BEFORE')
        receipt=read(pub+'/receipt.json',args.receipt_sha256);pin(args.producer_source,args.producer_source_sha256)
        supervisor=read(args.producer_supervisor/'summary.json')
        need(supervisor['command_exit_code']==0 and supervisor['cleanup']['reaped'] is True and supervisor['cleanup']['job_active_zero_observed'] is True,'PRODUCER_TERMINAL_CONTAINMENT')
        need(receipt['publication_commit']==COMMIT and receipt['before_ledger_sha256']==BEFORE and receipt['after_ledger_sha256']==args.after_sha256,'EXACT_PUBLICATION_RECEIPT')
        need(receipt['status']=='IMMUTABLE_WAVE38_DIRECT_AND_LOSSLESS_EVIDENCE_PUBLICATION_CONFIRMED' and receipt['immutable_records']==stage['records'] and receipt['source_sha256']==args.producer_source_sha256,'EXACT_PRODUCER_SCOPE_AND_SOURCE')
        need(receipt['changed_material_claims']==0 and receipt['new_exclusions']==0 and receipt['mathematical_replay'] is False,'NO_MATHEMATICAL_PROMOTION')
        remote=subprocess.check_output(['git','ls-remote','origin','refs/heads/codex/eight-coordinate-continuation-20260930'],cwd=ROOT,text=True,timeout=30).strip()
        need(subprocess.run(['git','merge-base','--is-ancestor',COMMIT,remote.split()[0]],cwd=ROOT,timeout=20).returncode==0,'IMMUTABLE_PUBLICATION_REACHABLE')
        public=json.loads(subprocess.check_output(['gh','api','repos/ikuto32/conway-99-graph','--jq','{private:.private,html_url:.html_url}'],cwd=ROOT,text=True,timeout=30))
        remote_commit=json.loads(subprocess.check_output(['gh','api',f'repos/ikuto32/conway-99-graph/git/commits/{COMMIT}','--jq','{sha:.sha,tree:.tree.sha}'],cwd=ROOT,text=True,timeout=30))
        need(public['private'] is False and public['html_url']=='https://github.com/ikuto32/conway-99-graph' and remote_commit['sha']==COMMIT,'PUBLIC_REMOTE_OBSERVATION')
        wanted=set(stage_members)
        wanted.update(a['path'] for a in controls['new_artifacts'] if a['path'] is not None)
        packages=[];raw_paths=set()
        for name,identity,review,review_hash in PACKAGES:
            package=read(name,identity);recovery=read(review,review_hash);packages.append((name,identity,package,recovery))
            wanted.update([name,review]);wanted.update(part['path'] for row in package['records'] for part in row['parts']);raw_paths.update(row['raw_path'] for row in package['records'])
        wanted.update(raw_paths)
        clean=read('acceleration/results/20261003_wave37_recovery_clean01/summary.json','5091fc02647848d5330943a440387007f66cf905748a2c908af84c415eab5499')
        wanted.add('acceleration/results/20261003_wave37_recovery_clean01/summary.json')
        available=set();tree_commands=[];ordered=sorted(wanted)
        for path in ordered:
            p=PurePosixPath(path);need(not p.is_absolute() and '..' not in p.parts and '\n' not in path,'LITERAL_PATH')
        for i in range(0,len(ordered),40):
            guard(deadline);command=['git','ls-tree','-r','--name-only',COMMIT,'--',*ordered[i:i+40]];tree_commands.append(command)
            available.update(subprocess.check_output(command,cwd=ROOT,text=True,timeout=20).splitlines())
        need(available<=wanted and not (available&raw_paths),'GIT_EXACT_POPULATION_AND_EIGHT_RAW_ABSENCE')
        blobs,archive_commands=archive_hashes(sorted(available),deadline)
        for path,r in records.items():need(blobs.get(path)=={'sha256':r['sha256'],'bytes':r['bytes']},'STAGED_AND_LATE_IMMUTABLE_BYTES',path)
        for path in stage['self_metadata_paths']:
            need(blobs[path]=={'sha256':pin(path),'bytes':(ROOT/path).stat().st_size},'STAGED_SELF_METADATA_BYTES',path)
        need(blobs[STAGE]['sha256']==STAGE_SHA and blobs[FROZEN]['sha256']==BEFORE,'IMMUTABLE_STAGE_AND_FINAL_ANCHORS')
        raw={};parts=compressed=0
        for name,identity,package,recovery in packages:
            need(blobs[name]['sha256']==identity,'IMMUTABLE_PACKAGE_ANCHOR')
            review_path,review_sha=next((p[2],p[3]) for p in PACKAGES if p[0]==name)
            need(blobs[review_path]['sha256']==review_sha,'IMMUTABLE_INDEPENDENT_RECOVERY_REPORT')
            decoded,pc,gc=decoded_records(package,name,identity,blobs,deadline)
            need(not(set(decoded)&set(raw)),'DISJOINT_RAW_POPULATION');raw.update(decoded);parts+=pc;compressed+=gc
            if name==PACKAGES[-1][0]:
                need(recovery['status']=='PASS' and recovery['verifier']=='/root/native_driver' and recovery['producer']=='/root','NEW_RECOVERY_REVIEW_ROLES')
                checked={r['raw_path']:r for r in recovery['records']};need(set(checked)==set(decoded),'EXACT_RECOVERY_REVIEW_POPULATION')
                for path,row in decoded.items():need(checked[path]['raw_sha256']==row['sha256'] and checked[path]['raw_bytes']==row['bytes'] and checked[path]['literal_bytes_compared']==row['bytes'],'BOUND_NEW_INDEPENDENT_RECOVERY')
            else:
                checked={r['path']:r for r in recovery['records']};need(set(checked)==set(decoded),'EXACT_RECOVERY_REVIEW_POPULATION')
                for path,row in decoded.items():need(checked[path]['sha256']==row['sha256'] and checked[path]['bytes']==row['bytes'] and checked[path]['restored_every_byte_matches'] is True,'BOUND_PRIOR_INDEPENDENT_RECOVERY')
        need((len(raw),parts,sum(r['bytes'] for r in raw.values()),compressed)==(8,48,367261301,11723542),'EXACT_EIGHT_RAW_POPULATION')
        omitted={r['path']:r for r in stage['omitted']};need(set(omitted)==set(raw),'EXACT_STAGE_PACKAGE_OMISSION_POPULATION')
        for path,item in raw.items():need(omitted[path]['sha256']==item['sha256'] and omitted[path]['bytes']==item['bytes'] and omitted[path]['fresh_hash_checked'] is True,'EXACT_STAGE_RAW_RECOVERY_IDENTITY',path)
        need(clean['status']=='WAVE37_EIGHT_PUBLIC_INPUTS_RECOVERED' and clean['child_action_counts']==[{'RESTORED_MISSING':4},{'RESTORED_MISSING':1},{'RESTORED_MISSING':1},{'RESTORED_MISSING':2}],'FRESH_EIGHT_RESTORE_IDENTITY')
        need(blobs['acceleration/results/20261003_wave37_recovery_clean01/summary.json']['sha256']=='5091fc02647848d5330943a440387007f66cf905748a2c908af84c415eab5499','IMMUTABLE_CLEAN_RECOVERY_REPORT')
        changed,retained=transition(before,after,baseline,blobs,raw)
        need(changed==receipt['changed_artifact_ids'] and retained==[a['id'] for a in receipt['retained_artifacts']],'PRODUCER_RECEIPT_COUNTS_MATCH_CALCULATION')
        need(len(changed)+len(retained)==controls['new_artifact_population'],'COMPLETE_NEW_AVAILABILITY_POPULATION')
        need(len(changed)==463 and not retained and receipt['raw_population']=={'raw_members':8,'gzip_parts':48,'raw_bytes':367261301,'gzip_bytes':11723542},'EXACT463_PUBLIC_ZERO_RETAINED')
        report.update(status='INDEPENDENT_WAVE38_AVAILABILITY_ONLY_PUBLIC_TRANSITION_PASS',after_ledger_sha256=args.after_sha256,changed_public_artifact_records=len(changed),changed_artifact_ids=changed,retained_artifact_ids=retained,immutable_git_blob_records=blobs,immutable_git_blob_count=len(blobs),stage_record_count=len(stage['records']),stage_union_count=len(stage_members),raw_records=raw,raw_population={'raw_members':len(raw),'gzip_parts':parts,'raw_bytes':sum(r['bytes'] for r in raw.values()),'gzip_bytes':compressed},git_tree_commands=tree_commands,git_archive_commands=archive_commands,remote_branch_observation=remote,public_repository_observation=public,remote_commit_observation=remote_commit)
        report['limitations'].extend(['Immutable Git archive bytes authenticated to independently observed public commit; no separate full clean-clone network retransmission.','Original eight raw paths absent in Git and publicly recovered from48 literal parts; complete bytes checked, mathematics not replayed.','Core612direct/13self metadata records and all463new artifact references checked. Later committed engineering metadata outside this frozen claim closure is not assigned availability by this report.','Historical archive reader failures, wave36 EOL/index correction and wave37 failed allowlist setup are preserved; this changed scope has fresh controls.'])
    need(pin('CLAIMS.yaml')==live_ledger and pin('.git/index')==live_index,'LIVE_LEDGER_AND_INDEX_UNCHANGED')
    report.update(elapsed_seconds=time.monotonic()-start,deadline=deadline.status())
    with (out/'summary.json').open('x',encoding='utf8',newline='\n') as stream:json.dump(report,stream,indent=2);stream.write('\n')
    print(json.dumps({'path':str(out/'summary.json'),'sha256':digest(out/'summary.json'),'status':report['status'],'new_artifact_population':controls['new_artifact_population'],'strict_controls':len(controls['controls'])}))

if __name__=='__main__':main()
