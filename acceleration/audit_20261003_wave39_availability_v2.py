"""Independent Wave39 availability-only checking; no producer imports or ledger writes."""
import argparse,copy,gzip,hashlib,json,platform,re,subprocess,sys,tarfile,time
from datetime import datetime,timezone
from pathlib import Path,PurePosixPath
import yaml
from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
COMMIT='16be41cee26421941eaecb615b64bd21095c5765'
BEFORE='b2796504a736ef16872ee36812d3b8ddb6446d0ea28d4883525f9ab9a3dd5679'
BASE='acceleration/results/20261003_wave39_registration01/CLAIMS.before.yaml'
FROZEN='acceleration/results/20261003_wave39_milestone01/CLAIMS.yaml'
STAGE='acceleration/results/20261003_wave39_milestone01/manifest.json'
STAGE_SHA='f9ad0134d583c6cb26d8b211731db66c137e9703f4499d420ca5d926823872fa'
NUL='acceleration/results/20261003_wave39_milestone01/stage_paths.nul'
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


EXTERNAL=dict(path='external_conway99_research/attempts/wave102-prism-incidence-code/derivation.md',sha256='df8841bee7f23b444186ab65947f77865ffb243363967dd56340207628f00c6f',
 repository='https://github.com/YesterdaysLemon/conway-99-research',commit='85e705cc6c2a14d123120c93a847e30aaab1789e',external_path='attempts/wave102-prism-incidence-code/derivation.md',
 retrieval='https://github.com/YesterdaysLemon/conway-99-research/blob/85e705cc6c2a14d123120c93a847e30aaab1789e/attempts/wave102-prism-incidence-code/derivation.md',
 reason='Exact historical source reference; no submodule-content staging or new historical verification.',git_blob_sha256='df8841bee7f23b444186ab65947f77865ffb243363967dd56340207628f00c6f',git_blob_bytes=6085,git_blob_rehashed=True)
def external_scope(row):
    need(type(row)is dict and json.dumps(row,sort_keys=True)==json.dumps(EXTERNAL,sort_keys=True),'EXTERNAL_SCOPE')
def external_controls():
    external_scope(copy.deepcopy(EXTERNAL));rows=[]
    for key,value in dict(path='../escape',sha256='0'*64,repository='https://github.com/wrong/repo',commit='0'*40,external_path='../escape',retrieval=EXTERNAL['retrieval'].replace(EXTERNAL['commit'],'main'),git_blob_bytes=6085.0,git_blob_rehashed=False,git_blob_sha256='1'*64).items():
        bad=copy.deepcopy(EXTERNAL);bad[key]=value
        rejection(rows,'external_'+key,'EXTERNAL_SCOPE',lambda:external_scope(bad))
    return dict(positive_controls=1,strict_controls=rows,scope='Literal external metadata only; no historical mathematics rechecked.')
def external_archive(deadline):
    guard(deadline)
    link_command=['git','ls-tree',COMMIT,'--','external_conway99_research']
    link=subprocess.check_output(link_command,cwd=ROOT,text=True,timeout=20).strip()
    need(link=='160000 commit '+EXTERNAL['commit']+'\texternal_conway99_research','EXTERNAL_GITLINK')
    command=['git','archive','--format=tar',EXTERNAL['commit'],'--',EXTERNAL['external_path']]
    child=subprocess.Popen(command,cwd=ROOT/'external_conway99_research',stdout=subprocess.PIPE,stderr=subprocess.PIPE);found={}
    try:
        with tarfile.open(fileobj=child.stdout,mode='r|')as tar:
            for member in tar:
                guard(deadline)
                if member.isdir():continue
                need(member.isfile()and member.name==EXTERNAL['external_path']and member.name not in found,'EXTERNAL_ARCHIVE_MEMBER')
                h=hashlib.sha256();size=0;stream=tar.extractfile(member)
                for block in iter(lambda:stream.read(65536),b''):size+=len(block);h.update(block)
                need(size==member.size==6085 and h.hexdigest()==EXTERNAL['sha256'],'EXTERNAL_ARCHIVE_BYTES');found[member.name]=dict(sha256=h.hexdigest(),bytes=size)
        for block in iter(lambda:child.stdout.read(65536),b''):need(not any(block),'EXTERNAL_TAR_PADDING')
        errors=child.stderr.read().decode('utf8',errors='replace');need(child.wait(timeout=10)==0,'EXTERNAL_ARCHIVE_EXIT',errors)
    finally:
        if child.poll()is None:child.kill();child.wait(timeout=5)
    need(set(found)=={EXTERNAL['external_path']}and digest(ROOT/EXTERNAL['path'])==EXTERNAL['sha256'],'EXTERNAL_LITERAL_POPULATION')
    guard(deadline)
    repo=json.loads(subprocess.check_output(['gh','api','repos/YesterdaysLemon/conway-99-research','--jq','{private:.private,html_url:.html_url}'],cwd=ROOT,text=True,timeout=30))
    commit=json.loads(subprocess.check_output(['gh','api','repos/YesterdaysLemon/conway-99-research/git/commits/'+EXTERNAL['commit'],'--jq','{sha:.sha,tree:.tree.sha}'],cwd=ROOT,text=True,timeout=30))
    need(repo['private']is False and repo['html_url']==EXTERNAL['repository']and commit['sha']==EXTERNAL['commit'],'EXTERNAL_PUBLIC_OBSERVATION')
    return dict(reference=EXTERNAL,main_gitlink_command=link_command,main_gitlink=link,archive_command=command,literal_records=found,public_repository_observation=repo,public_commit_observation=commit,mathematical_replay=False,historical_verification_promoted=False)

def transition(before,after,baseline,direct,raw,external=None):
    external={} if external is None else external
    need(before['claims']==after['claims'],'CLAIMS_AND_VERIFICATION_UNCHANGED')
    need(before['claims'][:len(baseline['claims'])]==baseline['claims'],'BASELINE350_CLAIMS_UNCHANGED')
    need(len(after['claims'])==353,'EXACT_CLAIM_POPULATION')
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
        path=a['path'];entry=raw.get(path) or direct.get(path) or external.get(path)
        if entry is None:
            need(a==b,'UNAUTHENTICATED_ARTIFACT_NOT_PROMOTED',aid);retained.append(aid);continue
        need(entry['sha256']==a['sha256'],'AUTHENTICATED_ARTIFACT_HASH',aid)
        need(b['availability']=='PUBLIC' and b['unavailable_reason'] is None,'EXACT_PUBLIC_AVAILABILITY',aid)
        need(isinstance(b['retrieval'],str),'RETRIEVAL_TEXT')
        links=re.findall(r'https://[^\s;]+',b['retrieval'])
        if path in raw:
            need(links==[prefix+entry['manifest']] and path in b['retrieval'] and a['sha256'] in b['retrieval'] and 'fresh destination' in b['retrieval'] and 'not mathematical replay' in b['retrieval'],'LOSSLESS_IMMUTABLE_RETRIEVAL',aid)
        elif path in external:need(links==[EXTERNAL['retrieval']] and 'No fresh mathematical endorsement' in b['retrieval'],'EXTERNAL_RETRIEVAL',aid)
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
    direct={a['path']:{'sha256':a['sha256']} for a in new if a['path'] is not None and a['path']!=EXTERNAL['path']}
    # This table calibrates logic only. It does not establish real publication.
    after=copy.deepcopy(before);prefix='https://github.com/ikuto32/conway-99-graph/blob/'+COMMIT+'/'
    for a in after['artifacts']:
        if a['id'] not in prior and a['path']==EXTERNAL['path']:a.update(availability='PUBLIC',retrieval=EXTERNAL['retrieval']+'; No fresh mathematical endorsement or complete historical transitive replay is implied.',unavailable_reason=None)
        elif a['id'] not in prior and a['path'] in direct:a.update(availability='PUBLIC',retrieval=prefix+a['path']+'; Historical transitive closure remains separate.',unavailable_reason=None)
    changed,retained=transition(before,after,baseline,direct,{},{EXTERNAL['path']:EXTERNAL})
    controls=[]
    for label,stage,mutate in [
        ('statement','CLAIMS_AND_VERIFICATION_UNCHANGED',lambda a:a['claims'][0].update(statement='corrupted')),
        ('verification','CLAIMS_AND_VERIFICATION_UNCHANGED',lambda a:a['claims'][0]['verification'][0].update(outcome='FAIL')),
        ('target','TOPLEVEL_UNCHANGED',lambda a:a['target'].update(status='NONEXISTENCE')),
        ('prior_hash','ALL_PRIOR_ARTIFACTS_UNCHANGED',lambda a:a['artifacts'][0].update(sha256='0'*64)),
        ('omitted_claim','CLAIMS_AND_VERIFICATION_UNCHANGED',lambda a:a['claims'].pop()),
        ('omitted_artifact','ARTIFACT_ID_POPULATION_UNCHANGED',lambda a:a['artifacts'].pop())]:
        damaged=copy.deepcopy(after);mutate(damaged)
        rejection(controls,label,stage,lambda:transition(before,damaged,baseline,direct,{},{EXTERNAL['path']:EXTERNAL}))
    synthetic={'id':'synthetic-missing-control','path':'build/synthetic-missing-publication.bin','sha256':'0'*64,'availability':'LOCAL_ONLY','retrieval':None,'unavailable_reason':'Synthetic control only.'}
    b=copy.deepcopy(before);a=copy.deepcopy(after);b['artifacts'].append(synthetic);a['artifacts'].append(copy.deepcopy(synthetic))
    need(transition(b,a,baseline,direct,{},{EXTERNAL['path']:EXTERNAL})[1]==['synthetic-missing-control'],'MISSING_POSITIVE_RETAINED')
    a['artifacts'][-1]['availability']='PUBLIC'
    rejection(controls,'missing_false_public','UNAUTHENTICATED_ARTIFACT_NOT_PROMOTED',lambda:transition(b,a,baseline,direct,{},{EXTERNAL['path']:EXTERNAL}))
    name=out.relative_to(ROOT).as_posix()+'/tiny.raw';payload=b'wave39 calibration raw bytes\n'*3;rawhash=hashlib.sha256(payload).hexdigest()
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
    transition(b,a,baseline,direct,raw,{EXTERNAL['path']:EXTERNAL});a['artifacts'][-1]['retrieval']='https://github.com/ikuto32/conway-99-graph/blob/main/unknown'
    rejection(controls,'mutable_raw_retrieval','LOSSLESS_IMMUTABLE_RETRIEVAL',lambda:transition(b,a,baseline,direct,raw,{EXTERNAL['path']:EXTERNAL}))
    for label,stage,mutate in [
        ('dropped_part','RAW_WHOLE_IDENTITY',lambda p:p['records'][0]['parts'].pop()),
        ('raw_hash','RAW_WHOLE_IDENTITY',lambda p:p['records'][0].update(raw_sha256='0'*64)),
        ('offset','RAW_CONTIGUOUS_OFFSET',lambda p:p['records'][0]['parts'][1].update(raw_offset=1)),
        ('compressed_hash','IMMUTABLE_GZIP_HASH',lambda p:p['records'][0]['parts'][0].update(gzip_sha256='0'*64))]:
        damaged=copy.deepcopy(package);mutate(damaged)
        rejection(controls,label,stage,lambda:decoded_records(damaged,'synthetic-package.json','1'*64,blobs,deadline))
    damaged=copy.deepcopy(after);indexed(damaged['artifacts'])[next(aid for aid in changed if indexed(after['artifacts'])[aid]['path'] in direct)]['retrieval']=prefix+'wrong'
    rejection(controls,'wrong_direct_retrieval','DIRECT_IMMUTABLE_RETRIEVAL',lambda:transition(before,damaged,baseline,direct,{},{EXTERNAL['path']:EXTERNAL}))
    return {'controls':controls,'new_artifact_population':len(new),'new_artifacts':new,'synthetic_direct_logic_only':True,'positive_tiny_gzip':{'raw_bytes':len(payload),'gzip_parts':pc,'gzip_bytes':gc}}


HISTORICAL_INDEX=dict(path='.git/index',sha256='68b695ba680915be542d08a9522a2a3acd329f8fd05e471b35ae27a9e0523152',
 reason='Historical read-only index observation stays in the immutable impact report; no Git metadata payload.')
def omissions(stage,labels,expected_raw=None):
    rows=stage.get('omitted');need(type(rows)is list and len(rows)==9,'STAGE_OMISSION_POPULATION')
    need(all(type(r)is dict and type(r.get('path'))is str for r in rows),'OMISSION_ROW_TYPE')
    table={r['path']:r for r in rows};need(len(table)==9,'OMISSION_UNIQUE_PATHS')
    need(table.get('.git/index')==HISTORICAL_INDEX,'HISTORICAL_INDEX_SCOPE')
    raw={k:v for k,v in table.items()if k!='.git/index'};need(len(raw)==8,'RAW_OMISSION_POPULATION')
    for path,row in raw.items():
        need(set(row)=={'path','sha256','bytes','reason'},'RAW_OMISSION_FIELDS')
        p=PurePosixPath(path);need(not p.is_absolute()and '..'not in p.parts and path not in labels,'RAW_OMISSION_PATH')
        need(type(row['bytes'])is int and row['bytes']>0,'RAW_OMISSION_SIZE_TYPE')
        h=row['sha256'];need(type(h)is str and len(h)==64 and all(c in '0123456789abcdef'for c in h),'RAW_OMISSION_HASH_TYPE')
        need(row['reason']=='Existing public lossless package; no duplicate raw blob.','RAW_OMISSION_REASON')
    need(not(set(table)&set(labels)),'OMISSIONS_NOT_STAGED')
    if expected_raw is not None:
        need(set(raw)==set(expected_raw),'EXACT_RAW_OMISSION_POPULATION')
        for path,row in raw.items():
            need(row['sha256']==expected_raw[path]['sha256']and row['bytes']==expected_raw[path]['bytes'],'EXACT_STAGE_RAW_RECOVERY_IDENTITY',path)
    return raw
def omission_controls(stage,labels):
    expected={p:dict(sha256=r['sha256'],bytes=r['bytes'])for p,r in omissions(stage,labels).items()}
    omissions(stage,labels,expected);cases=[]
    raw_index=next(i for i,r in enumerate(stage['omitted'])if r['path']!='.git/index')
    historical_index=next(i for i,r in enumerate(stage['omitted'])if r['path']=='.git/index')
    for label,code,mutate in [
        ('historical_index_hash','HISTORICAL_INDEX_SCOPE',lambda s:s['omitted'][historical_index].update(sha256='0'*64)),
        ('historical_index_current_hash','HISTORICAL_INDEX_SCOPE',lambda s:s['omitted'][historical_index].update(sha256='709d1d0b6cfbdc69214c996c440e86e373d719bdb2a918b49303c7edbcf3e3d1')),
        ('historical_index_bytes_claim','HISTORICAL_INDEX_SCOPE',lambda s:s['omitted'][historical_index].update(bytes=1)),
        ('historical_index_reason','HISTORICAL_INDEX_SCOPE',lambda s:s['omitted'][historical_index].update(reason='Public byte payload')),
        ('dropped_raw','STAGE_OMISSION_POPULATION',lambda s:s['omitted'].pop(raw_index)),
        ('duplicated_raw_path','OMISSION_UNIQUE_PATHS',lambda s:s['omitted'][-1].update(path=s['omitted'][raw_index]['path'])),
        ('raw_wrong_hash','EXACT_STAGE_RAW_RECOVERY_IDENTITY',lambda s:s['omitted'][raw_index].update(sha256='0'*64)),
        ('raw_wrong_bytes','EXACT_STAGE_RAW_RECOVERY_IDENTITY',lambda s:s['omitted'][raw_index].update(bytes=s['omitted'][raw_index]['bytes']+1)),
        ('raw_float_bytes','RAW_OMISSION_SIZE_TYPE',lambda s:s['omitted'][raw_index].update(bytes=float(s['omitted'][raw_index]['bytes']))),
        ('raw_bool_bytes','RAW_OMISSION_SIZE_TYPE',lambda s:s['omitted'][raw_index].update(bytes=True)),
        ('raw_fresh_true_claim','RAW_OMISSION_FIELDS',lambda s:s['omitted'][raw_index].update(fresh_hash_checked=True)),
        ('raw_fresh_false_claim','RAW_OMISSION_FIELDS',lambda s:s['omitted'][raw_index].update(fresh_hash_checked=False)),
        ('raw_wrong_reason','RAW_OMISSION_REASON',lambda s:s['omitted'][raw_index].update(reason='Already freshly rechecked'))]:
        bad=copy.deepcopy(stage);mutate(bad)
        rejection(cases,label,code,lambda:omissions(bad,labels,expected))
    return dict(positive_controls=1,strict_controls=cases,scope='Exact actual nine-entry metadata shape: one historical index plus eight raw identities. Fresh full decompression independently establishes raw byte hashes; no invented stage fresh_hash_checked field.')

def stage_scope(stage,nul):
    need(stage['schema']=='WAVE39_FIXED353_EXPLICIT_PUBLICATION_ALLOWLIST_V1' and stage['current_claims']==353 and stage['previous_claims']==350 and stage['ledger_sha256']==BEFORE
         and stage['before_ledger_sha256']=='ff94b87187d712bc2fce166b8afffaa3e2155db9fbdf8a4b3179b1f3fe2e304a','FROZEN_STAGE_SCOPE')
    need(stage['direct_record_count']==len(stage['records'])==472 and sum(r['bytes'] for r in stage['records'])==stage['direct_bytes']==93428906,'EXACT_STAGE_COUNT')
    members=[r['path'] for r in stage['records']];metadata=stage['self_metadata_paths']
    need(len(set(members))==len(members) and len(metadata)==16 and not(set(members)&set(metadata)),'UNIQUE_STAGE_MEMBERS')
    need(len(set(metadata))==16 and STAGE in metadata and FROZEN in metadata and NUL in metadata,'EXACT_STAGE_SELF_METADATA')
    need(nul.endswith(b'\0') and hashlib.sha256(nul).hexdigest()==stage['stage_paths_sha256']=='fe3442f89286ea8fc005cfc348b577e144eb5c38ee6f16b7f0a2b7c5c7dd1215','EXACT_STAGE_NUL_HASH')
    labels=nul[:-1].decode('utf8').split('\0');need(len(labels)==stage['stage_paths_count']==488 and labels==sorted(set(members)|set(metadata)),'EXACT_STAGE_NUL_POPULATION')
    omissions(stage,labels)
    need(type(stage.get('historical_external_sources'))is list and len(stage['historical_external_sources'])==1,'EXTERNAL_POPULATION');external_scope(stage['historical_external_sources'][0])
    return labels

def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=('calibration','full'))
    ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--publication-dir',type=Path);ap.add_argument('--receipt-sha256');ap.add_argument('--after-sha256')
    ap.add_argument('--producer-source');ap.add_argument('--producer-source-sha256');ap.add_argument('--producer-supervisor',type=Path)
    ap.add_argument('--calibration',type=Path);ap.add_argument('--calibration-sha256')
    args=ap.parse_args();start=time.monotonic();deadline=CommandDeadline(args.seconds,allocation_reason='Independent353-claim publication bookkeeping and bounded immutable archive/367MB streaming recovery')
    out=args.out.resolve();need(out.is_relative_to(ROOT),'BOUNDED_OUTPUT');out.mkdir(parents=True,exist_ok=False);pins={}
    def pin(name,identity=None):
        name=Path(name).as_posix();actual=digest(ROOT/name);need(identity is None or identity==actual,'INPUT_PIN',name);pins[name]=actual;return actual
    def read(name,identity=None):pin(name,identity);return json.loads((ROOT/name).read_bytes())
    def ledger(name,identity=None):pin(name,identity);return yaml.load((ROOT/name).read_text(encoding='utf8'),Loader=UniqueLoader)
    live_ledger=pin('CLAIMS.yaml');live_index=pin('.git/index')
    before=ledger(FROZEN,BEFORE);baseline=ledger(BASE,'ff94b87187d712bc2fce166b8afffaa3e2155db9fbdf8a4b3179b1f3fe2e304a')
    need(len(before['claims'])==353 and len(baseline['claims'])==350,'FROZEN353_AND350_POPULATIONS')
    stage=read(STAGE,STAGE_SHA)
    pin(NUL);nul=(ROOT/NUL).read_bytes();stage_members=stage_scope(stage,nul)
    records={r['path']:r for r in stage['records']}
    need(len(records)==len(stage['records']),'UNIQUE_STAGE_MEMBERS')
    for name in (Path(__file__).relative_to(ROOT).as_posix(),'acceleration/audit_20261003_wave39_availability_v2_spec.md','acceleration/audit_20261003_wave39_availability_v1.py','acceleration/audit_20261003_wave39_availability_v1_spec.md','acceleration/audit_20261003_wave38_availability_v1.py','acceleration/audit_20261003_wave38_availability_v1_spec.md','acceleration/audit_20261003_wave37_availability_v1.py','acceleration/audit_20261003_wave37_availability_v1_spec.md','acceleration/command_deadline.py','acceleration/run_compute_command.py','uv.lock','pyproject.toml'):
        pin(name)
    controls=calibration(before,baseline,out,deadline)
    controls['external_metadata']=external_controls()
    controls['actual_omission_metadata']=omission_controls(stage,stage_members)
    for label,code,mutate in [('wrong_ledger_population','FROZEN_STAGE_SCOPE',lambda s:s.update(current_claims=352)),('wrong_prior_scope','FROZEN_STAGE_SCOPE',lambda s:s.update(previous_claims=337)),('omitted_direct_member','EXACT_STAGE_COUNT',lambda s:s['records'].pop()),('duplicated_self_member','EXACT_STAGE_SELF_METADATA',lambda s:s['self_metadata_paths'].__setitem__(0,s['self_metadata_paths'][1])),('omitted_raw_claim','STAGE_OMISSION_POPULATION',lambda s:s['omitted'].pop())]:
        damaged=copy.deepcopy(stage);mutate(damaged);rejection(controls['controls'],label,code,lambda:stage_scope(damaged,nul))
    rejection(controls['controls'],'damaged_stage_nul','EXACT_STAGE_NUL_HASH',lambda:stage_scope(stage,nul[:-1]))
    blobs,reader_commands=archive_hashes([STAGE,FROZEN],deadline)
    need(blobs[STAGE]['sha256']==STAGE_SHA and blobs[FROZEN]['sha256']==BEFORE,'NEW_READER_LITERAL_ANCHORS')
    report={'timestamp':datetime.now(timezone.utc).isoformat(),'verifier':'/root/native_driver','producer':'/root','source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'command':[sys.executable,*sys.argv],'cwd':str(ROOT),'python':platform.python_version(),'publication_commit':COMMIT,'inputs_sha256':pins,'before_ledger_sha256':BEFORE,'unchanged_claims':353,'new_claims':0,'mathematical_replays':0,'new_exclusions':0,'target_resolution':'UNKNOWN','overall_search_coverage':'UNKNOWN; no validated denominator.','calibration':controls,'reader_calibration':{'commands':reader_commands,'literal_records':blobs,'outcome':'PASS'},'shared_components':['Preserved independently authored Wave38 archive/streaming/transition implementation adapted to new353-record scope; native_driver adapter is independent of ROOT publication producer; no publication producer imported.','Git archive/tree implementations, Python gzip/SHA256, duplicate-key rejecting YAML loader, command_deadline and supported Job supervisor.'],'limitations':['Byte-publication checking only; no mathematical replay or target resolution.','Calibration synthetic metadata tests transition logic, not real availability.','Historical complete transitive evidence/platform-binary availability remains separately recorded.']}
    report['calibration_timing']='Fresh checker controls before full checking; actual producer ordering is documented by separately preserved receipt. No pre-producer-output gate claim is implied.'
    if args.mode=='calibration':report['status']='INDEPENDENT_WAVE39_AVAILABILITY_V2_PREFULL_CALIBRATION_PASS'
    else:
        need(all((args.publication_dir,args.receipt_sha256,args.after_sha256,args.producer_source,args.producer_source_sha256,args.producer_supervisor,args.calibration,args.calibration_sha256)),'FULL_EXACT_ARGUMENTS')
        prior_cal=read(args.calibration,args.calibration_sha256)
        need(prior_cal['status']=='INDEPENDENT_WAVE39_AVAILABILITY_V2_PREFULL_CALIBRATION_PASS' and prior_cal['inputs_sha256'][Path(__file__).relative_to(ROOT).as_posix()]==pins[Path(__file__).relative_to(ROOT).as_posix()],'APPLICABLE_PREFULL_CALIBRATION')
        pub=args.publication_dir.as_posix();after=ledger(pub+'/CLAIMS.after.yaml',args.after_sha256)
        need(ledger(pub+'/CLAIMS.before.yaml',BEFORE)==before,'EXACT_FROZEN_BEFORE')
        receipt=read(pub+'/receipt.json',args.receipt_sha256);pin(args.producer_source,args.producer_source_sha256)
        supervisor=read(args.producer_supervisor/'summary.json')
        need(supervisor['command_exit_code']==0 and supervisor['cleanup']['reaped'] is True and supervisor['cleanup']['job_active_zero_observed'] is True,'PRODUCER_TERMINAL_CONTAINMENT')
        need(receipt['publication_commit']==COMMIT and receipt['before_ledger_sha256']==BEFORE and receipt['after_ledger_sha256']==args.after_sha256,'EXACT_PUBLICATION_RECEIPT')
        need(receipt['status']=='IMMUTABLE_WAVE39_DIRECT_AND_LOSSLESS_EVIDENCE_PUBLICATION_CONFIRMED' and receipt['immutable_records']==stage['records'] and receipt['source_sha256']==args.producer_source_sha256,'EXACT_PRODUCER_SCOPE_AND_SOURCE')
        external=external_archive(deadline)
        need(receipt['external_historical_source']['reference']==EXTERNAL and receipt['external_historical_source']['pinned_blob_bytes']==6085 and receipt['external_historical_source']['pinned_blob_sha256']==EXTERNAL['sha256'],'PRODUCER_EXTERNAL_SCOPE')
        need(receipt['changed_material_claims']==0 and receipt['new_exclusions']==0 and receipt['mathematical_replay'] is False,'NO_MATHEMATICAL_PROMOTION')
        remote=subprocess.check_output(['git','ls-remote','origin','refs/heads/codex/eight-coordinate-continuation-20260930'],cwd=ROOT,text=True,timeout=30).strip()
        need(subprocess.run(['git','merge-base','--is-ancestor',COMMIT,remote.split()[0]],cwd=ROOT,timeout=20).returncode==0,'IMMUTABLE_PUBLICATION_REACHABLE')
        public=json.loads(subprocess.check_output(['gh','api','repos/ikuto32/conway-99-graph','--jq','{private:.private,html_url:.html_url}'],cwd=ROOT,text=True,timeout=30))
        remote_commit=json.loads(subprocess.check_output(['gh','api',f'repos/ikuto32/conway-99-graph/git/commits/{COMMIT}','--jq','{sha:.sha,tree:.tree.sha}'],cwd=ROOT,text=True,timeout=30))
        need(public['private'] is False and public['html_url']=='https://github.com/ikuto32/conway-99-graph' and remote_commit['sha']==COMMIT,'PUBLIC_REMOTE_OBSERVATION')
        wanted=set(stage_members)
        wanted.update(a['path'] for a in controls['new_artifacts'] if a['path'] is not None and a['path']!=EXTERNAL['path'])
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
        omitted=omissions(stage,stage_members,raw)
        need(len(omitted)==8,'EXACT_STAGE_PACKAGE_OMISSION_POPULATION')
        need(clean['status']=='WAVE37_EIGHT_PUBLIC_INPUTS_RECOVERED' and clean['child_action_counts']==[{'RESTORED_MISSING':4},{'RESTORED_MISSING':1},{'RESTORED_MISSING':1},{'RESTORED_MISSING':2}],'FRESH_EIGHT_RESTORE_IDENTITY')
        need(blobs['acceleration/results/20261003_wave37_recovery_clean01/summary.json']['sha256']=='5091fc02647848d5330943a440387007f66cf905748a2c908af84c415eab5499','IMMUTABLE_CLEAN_RECOVERY_REPORT')
        changed,retained=transition(before,after,baseline,blobs,raw,{EXTERNAL['path']:EXTERNAL})
        need(changed==receipt['changed_artifact_ids'] and retained==[a['id'] for a in receipt['retained_artifacts']],'PRODUCER_RECEIPT_COUNTS_MATCH_CALCULATION')
        need(len(changed)+len(retained)==controls['new_artifact_population'],'COMPLETE_NEW_AVAILABILITY_POPULATION')
        need(len(changed)==controls['new_artifact_population'] and not retained and receipt['raw_population']=={'raw_members':8,'gzip_parts':48,'raw_bytes':367261301,'gzip_bytes':11723542},'EXACT_NEW_PUBLIC_ZERO_RETAINED')
        report.update(status='INDEPENDENT_WAVE39_AVAILABILITY_V2_ONLY_PUBLIC_TRANSITION_PASS',external_historical_source=external,after_ledger_sha256=args.after_sha256,changed_public_artifact_records=len(changed),changed_artifact_ids=changed,retained_artifact_ids=retained,immutable_git_blob_records=blobs,immutable_git_blob_count=len(blobs),stage_record_count=len(stage['records']),stage_union_count=len(stage_members),raw_records=raw,raw_population={'raw_members':len(raw),'gzip_parts':parts,'raw_bytes':sum(r['bytes'] for r in raw.values()),'gzip_bytes':compressed},git_tree_commands=tree_commands,git_archive_commands=archive_commands,remote_branch_observation=remote,public_repository_observation=public,remote_commit_observation=remote_commit)
        report['limitations'].extend(['Immutable Git archive bytes authenticated to independently observed public commit; no separate full clean-clone network retransmission.','Original eight raw paths absent in Git and publicly recovered from48 literal parts; complete bytes checked, mathematics not replayed.','Core472direct/16self metadata records and every new artifact reference checked, including one separate external historical source. Later committed engineering metadata outside this frozen claim closure is not assigned availability by this report.','Historical archive reader failures, wave36 EOL/index correction and wave37 failed allowlist setup are preserved; this changed scope has fresh controls.'])
    need(pin('CLAIMS.yaml')==live_ledger and pin('.git/index')==live_index,'LIVE_LEDGER_AND_INDEX_UNCHANGED')
    report.update(elapsed_seconds=time.monotonic()-start,deadline=deadline.status())
    with (out/'summary.json').open('x',encoding='utf8',newline='\n') as stream:json.dump(report,stream,indent=2);stream.write('\n')
    print(json.dumps({'path':str(out/'summary.json'),'sha256':digest(out/'summary.json'),'status':report['status'],'new_artifact_population':controls['new_artifact_population'],'strict_controls':len(controls['controls'])+len(controls['external_metadata']['strict_controls'])+len(controls['actual_omission_metadata']['strict_controls'])}))

if __name__=='__main__':main()
