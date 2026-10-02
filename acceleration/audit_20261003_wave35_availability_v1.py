"""Independent availability-only audit using Git archive and streaming gzip.

Read-only frozen ledger snapshots; no registrar/producer imports, no math replay.
"""
import argparse,copy,gzip,hashlib,itertools,json,platform,re,subprocess,sys,tarfile,time
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path,PurePosixPath
import yaml
from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
COMMIT='51a0c019178add446941d920ae0d3da63c58ac29'
PUB='acceleration/results/20261003_wave35_public_confirmation01'
BASE='acceleration/results/20261002_wave35_registration01/CLAIMS.before.yaml'
STAGE='acceleration/results/20261002_wave35_stage02/manifest.json'
BEFORE='5476fe90324fb7a3a8aa275fc1ae1061f7aaeb8e42d9c5123d33a8d1c3f65f5a'
AFTER='4b7470f6e2bd183d355a2247e28a354159681f0b12c10fcb90181bff94e91ea5'
PACKAGES=[
 ('acceleration/results/20261002_wave33_model_package01/manifest.json','c3efa198c5f48eddb5ead69a4bb130a3dc55567bb298856143c6fb62eb0e0145',
  'acceleration/results/20261002_independent_review/wave33_model_recovery01/summary.json','b9352a5e5810f20ff9187c06f5e00636f2f3abad2810ed3d7c23df655b76f583'),
 ('acceleration/results/20261002_wave33_reconstruction_package01/manifest.json','f639431b7ea9ce0f1500ea48b002629d2523271eead700217dd512e8ade66989',
  'acceleration/results/20261002_independent_review/wave33_reconstruction_recovery01/summary.json','09623c7c36a6b6b4d7905992361721f38b9ea7778fe7493f01455a4de90d1ba5')]

class AuditError(ValueError):
    def __init__(self,stage,detail=''):
        self.stage=stage;super().__init__(stage+(': '+detail if detail else ''))

def need(test,stage,detail=''):
    if not test:raise AuditError(stage,detail)

class UniqueLoader(yaml.SafeLoader):pass
def unique(loader,node,deep=False):
    result={}
    for k,v in node.value:
        key=loader.construct_object(k,deep=deep)
        need(key not in result,'DUPLICATE_YAML_KEY',str(key));result[key]=loader.construct_object(v,deep=deep)
    return result
UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,unique)

def digest(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

def indexed(records):
    result={}
    for row in records:
        need(row['id'] not in result,'DUPLICATE_ID');result[row['id']]=row
    return result

def clock_check(deadline):need(deadline.status()['remaining_seconds']>20,'DEADLINE','shutdown reserve')

def archive_hashes(names,deadline):
    """Git archive reads the commit tree via a different path than cat-file producer."""
    result={};commands=[]
    for start in range(0,len(names),40):
        clock_check(deadline)
        batch=names[start:start+40]
        command=['git','archive','--format=tar',COMMIT,'--',*batch];commands.append(command)
        child=subprocess.Popen(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        try:
            with tarfile.open(fileobj=child.stdout,mode='r|') as archive:
                for member in archive:
                    clock_check(deadline)
                    if not member.isfile():continue
                    need(member.name in batch and member.name not in result,'ARCHIVE_MEMBER_POPULATION',member.name)
                    h=hashlib.sha256();total=0
                    stream=archive.extractfile(member)
                    for block in iter(lambda:stream.read(1024*1024),b''):
                        h.update(block);total+=len(block)
                    need(total==member.size,'ARCHIVE_COMPLETE_MEMBER')
                    result[member.name]={'sha256':h.hexdigest(),'bytes':total}
            # tarfile stops at its end marker and may leave zero padding in the
            # OS pipe. Drain before stderr/wait so native Git cannot block while
            # writing remaining stdout through the Windows command shim.
            for padding in iter(lambda:child.stdout.read(65536),b''):
                need(not any(padding),'ARCHIVE_TRAILING_PADDING')
            stderr=child.stderr.read().decode('utf8',errors='replace')
            need(child.wait(timeout=10)==0,'ARCHIVE_EXIT',stderr)
            need(set(batch)<=set(result),'ARCHIVE_NO_OMITTED_MEMBER')
        finally:
            if child.poll() is None:child.kill();child.wait(timeout=5)
    return result,commands

def decoded_records(package,manifest_name,manifest_hash,blobs,deadline):
    result={};part_count=gzip_bytes=0
    for row in package['records']:
        clock_check(deadline);name=row['raw_path'];need(name not in result,'DUPLICATE_RAW_PATH')
        aggregate=hashlib.sha256();offset=0
        for part in row['parts']:
            clock_check(deadline)
            need(part['raw_offset']==offset,'RAW_CONTIGUOUS_OFFSET')
            need(blobs[part['path']]=={'sha256':part['gzip_sha256'],'bytes':part['gzip_bytes']},'IMMUTABLE_GZIP_HASH')
            local=ROOT/part['path'];need(digest(local)==part['gzip_sha256'],'LOCAL_GZIP_IMMUTABLE_IDENTITY')
            chunk=hashlib.sha256();total=0
            # Bounded streaming, unlike the producer's full gzip.decompress.
            with gzip.open(local,'rb') as stream:
                for block in iter(lambda:stream.read(1024*1024),b''):
                    need(total+len(block)<=part['raw_bytes'],'RAW_PART_DECLARED_LENGTH')
                    aggregate.update(block);chunk.update(block);total+=len(block)
            need(total==part['raw_bytes'] and chunk.hexdigest()==part['raw_sha256'],'RAW_PART_IDENTITY')
            offset+=total;part_count+=1;gzip_bytes+=part['gzip_bytes']
        need(offset==row['raw_bytes'] and aggregate.hexdigest()==row['raw_sha256'],'RAW_WHOLE_IDENTITY')
        need(name not in blobs,'RAW_INTENTIONALLY_ABSENT_FROM_GIT')
        result[name]={'sha256':aggregate.hexdigest(),'bytes':offset,'manifest':manifest_name,'manifest_sha256':manifest_hash}
    return result,part_count,gzip_bytes

def transition(before,after,baseline,direct,raw):
    need(before['claims']==after['claims'],'CLAIMS_AND_VERIFICATION_UNCHANGED')
    need(len(after['claims'])==334,'EXACT_CLAIM_POPULATION')
    for key in set(before)|set(after):
        if key not in ('artifacts','updated_at'):need(before[key]==after[key],'TOPLEVEL_UNCHANGED',key)
    need(after['target']['status']=='UNKNOWN' and after['target']['overall_search_coverage'] is None,'TARGET_UNKNOWN')
    old,new=indexed(before['artifacts']),indexed(after['artifacts']);prior=indexed(baseline['artifacts'])
    need(set(old)==set(new),'ARTIFACT_ID_POPULATION_UNCHANGED')
    need([new[x['id']] for x in before['artifacts']]==after['artifacts'],'ARTIFACT_ORDER_UNCHANGED')
    need(all(old[aid]==value==new[aid] for aid,value in prior.items()),'ALL_PRIOR_ARTIFACTS_UNCHANGED')
    changed=[];retained=[]
    prefix='https://github.com/ikuto32/conway-99-graph/blob/'+COMMIT+'/'
    for aid,a in old.items():
        b=new[aid]
        if aid in prior:continue
        need({k:v for k,v in a.items() if k not in ('availability','retrieval','unavailable_reason')}==
             {k:v for k,v in b.items() if k not in ('availability','retrieval','unavailable_reason')},'ARTIFACT_IDENTITY_UNCHANGED',aid)
        name=a['path'];entry=raw.get(name) or direct.get(name)
        if entry is None:
            need(a==b,'UNAUTHENTICATED_ARTIFACT_NOT_PROMOTED',aid);retained.append(aid);continue
        need(entry['sha256']==a['sha256'],'AUTHENTICATED_ARTIFACT_HASH',aid)
        need(b['availability']=='PUBLIC' and b['unavailable_reason'] is None,'EXACT_PUBLIC_AVAILABILITY',aid)
        retrieval=b['retrieval'];need(isinstance(retrieval,str),'RETRIEVAL_TEXT')
        links=re.findall(r'https://[^\s;]+',retrieval)
        if name in raw:
            need(links==[prefix+entry['manifest']] and name in retrieval and a['sha256'] in retrieval
                 and 'fresh destination' in retrieval and 'not mathematical replay' in retrieval,'LOSSLESS_IMMUTABLE_RETRIEVAL',aid)
        else:
            need(links==[prefix+name] and 'Historical transitive' in retrieval,'DIRECT_IMMUTABLE_RETRIEVAL',aid)
        changed.append(aid)
    return changed,retained

def rejection(records,label,expected,call):
    try:call()
    except AuditError as error:
        need(error.stage==expected,'CONTROL_EXACT_STAGE',str(error));records.append({'label':label,'stage':error.stage,'diagnostic':str(error)})
    else:raise AuditError('CONTROL_ACCEPTED',label)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();start=time.monotonic();deadline=CommandDeadline(args.seconds,allocation_reason='Independent availability bookkeeping,immutable Git archive hashes and184MiB streaming recovery')
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={}
    def pin(name,expected=None):
        actual=digest(ROOT/name);need(expected is None or actual==expected,'INPUT_PIN',name);pins[name]=actual;return actual
    def read(name,expected=None):pin(name,expected);return json.loads((ROOT/name).read_bytes())
    def ledger(name,expected=None):pin(name,expected);return yaml.load((ROOT/name).read_text(encoding='utf8'),Loader=UniqueLoader)
    before=ledger(PUB+'/CLAIMS.before.yaml',BEFORE);after=ledger(PUB+'/CLAIMS.after.yaml',AFTER);baseline=ledger(BASE)
    receipt=read(PUB+'/receipt.json','0137ee22ef26c4a8b21c54910187168dfe7fed5177b947737c80b96425a86246');stage=read(STAGE,'e32348ae19ed9e5c5ad3ba8121dcca080bd85666ec2e560685e94e811e9957a4')
    pin('acceleration/confirm_20261003_wave35_publication_v1.py','d5f88684ef4c498e6bbe773f05dd400c121b91ad38aa5bafc88e3f1c4979e88c')
    pin('acceleration/audit_20261002_wave34_availability_v1.py','a2d68be65b2ec32a88d2df6a2b3e5551215a5be30352e26fd54475514715042e')
    pin('acceleration/audit_20261002_wave33_availability_v3.py','9550324f6a81260c068dbed73b71fb16d20c98ec329868eb0ce1b2719336fb2f')
    need(receipt['publication_commit']==COMMIT and receipt['before_ledger_sha256']==BEFORE and receipt['after_ledger_sha256']==AFTER,'EXACT_PUBLICATION_RECEIPT')
    need(receipt['immutable_records']==stage['records'],'EXACT_STAGE_POPULATION')
    need(receipt['changed_material_claims']==0 and receipt['new_exclusions']==0 and receipt['mathematical_replay'] is False,'NO_MATHEMATICAL_PROMOTION')
    need(len(stage['records'])==324 and sum(r['bytes'] for r in stage['records'])==112814168,'FROZEN_STAGE_COUNT')
    impact=read('acceleration/results/20261002_independent_review/wave35_transition01/summary.json','72e4f59613bc9ca62ffabf591985326b31256b0beb4b4e726ed983c2f8a87b5c')
    need(impact['status']=='INDEPENDENT_WAVE35_EXACT329_TO334_TRANSITION_PASS','PINNED_PRIOR_IMPACT_REVIEW')
    frozen=ledger('acceleration/results/20261002_wave35_milestone01/CLAIMS.yaml',BEFORE)
    need(before==frozen,'EXACT_VERIFIED_MILESTONE_BEFORE')
    supervisor=read('acceleration/results/20261003_wave35_public_confirmation_supervision01/summary.json')
    need(supervisor['command_exit_code']==0 and supervisor['cleanup']['reaped'] is True and supervisor['cleanup']['job_active_zero_observed'] is True,'PRODUCER_TERMINAL_CONTAINMENT')
    calibration_blobs,calibration_commands=archive_hashes([STAGE],deadline)
    need(calibration_blobs[STAGE]=={'sha256':pins[STAGE],'bytes':(ROOT/STAGE).stat().st_size},'ARCHIVE_READER_CALIBRATION')
    remote=subprocess.check_output(['git','ls-remote','origin','refs/heads/codex/eight-coordinate-continuation-20260930'],cwd=ROOT,text=True,timeout=30).strip()
    remote_head=remote.split()[0]
    need(subprocess.run(['git','merge-base','--is-ancestor',COMMIT,remote_head],cwd=ROOT,timeout=20).returncode==0,'IMMUTABLE_PUBLICATION_REACHABLE')
    public=json.loads(subprocess.check_output(['gh','api','repos/ikuto32/conway-99-graph','--jq','{private:.private,html_url:.html_url}'],cwd=ROOT,text=True,timeout=30))
    remote_commit=json.loads(subprocess.check_output(['gh','api',f'repos/ikuto32/conway-99-graph/git/commits/{COMMIT}','--jq','{sha:.sha,tree:.tree.sha}'],cwd=ROOT,text=True,timeout=30))
    need(public['private'] is False and public['html_url']=='https://github.com/ikuto32/conway-99-graph' and remote_commit['sha']==COMMIT,'PUBLIC_REMOTE_OBSERVATION')
    wanted={STAGE};packages=[];recoveries=[]
    wanted.update(row['path'] for row in stage['records'])
    old_artifacts=indexed(before['artifacts']);prior=indexed(baseline['artifacts'])
    wanted.update(a['path'] for aid,a in old_artifacts.items() if aid not in prior and a['path'] is not None)
    for name,identity,review,review_hash in PACKAGES:
        package=read(name,identity);recovery=read(review,review_hash);packages.append((name,identity,package));recoveries.append(recovery)
        wanted.update([name,review]);wanted.update(part['path'] for row in package['records'] for part in row['parts'])
    raw_paths={row['raw_path'] for name,identity,p in packages for row in p['records']}
    wanted.update(raw_paths)
    for path in wanted:
        p=PurePosixPath(path);need(not p.is_absolute() and '..' not in p.parts and '\n' not in path,'LITERAL_PATH')
    available=set();tree_commands=[]
    ordered=sorted(wanted)
    for i in range(0,len(ordered),40):
        clock_check(deadline);command=['git','ls-tree','-r','--name-only',COMMIT,'--',*ordered[i:i+40]];tree_commands.append(command)
        names=subprocess.check_output(command,cwd=ROOT,text=True,timeout=20).splitlines();available.update(names)
    need(available<=wanted and not(available&raw_paths),'GIT_EXACT_POPULATION_AND_RAW_ABSENCE')
    blobs,archive_commands=archive_hashes(sorted(available),deadline)
    for row in stage['records']:need(blobs[row['path']]=={'sha256':row['sha256'],'bytes':row['bytes']},'STAGED_IMMUTABLE_BYTES',row['path'])
    need(blobs[STAGE]['sha256']==pins[STAGE],'IMMUTABLE_STAGE_ANCHOR')
    raw={};parts=compressed=0
    for (name,identity,package),recovery in zip(packages,recoveries):
        need(blobs[name]['sha256']==identity,'IMMUTABLE_PACKAGE_ANCHOR')
        decoded,pc,gc=decoded_records(package,name,identity,blobs,deadline)
        need(not(set(decoded)&set(raw)),'DISJOINT_RAW_POPULATION');raw.update(decoded);parts+=pc;compressed+=gc
        checked={row['path']:row for row in recovery['records']}
        need(set(checked)==set(decoded),'EXACT_RECOVERY_REVIEW_POPULATION')
        for path,data in decoded.items():
            need(checked[path]['sha256']==data['sha256'] and checked[path]['bytes']==data['bytes'] and checked[path]['restored_every_byte_matches'] is True,'BOUND_PRIOR_INDEPENDENT_RECOVERY')
    need((len(raw),parts,sum(x['bytes'] for x in raw.values()),compressed)==(5,25,184494332,6873080),'EXACT_RAW_POPULATION')
    changed,retained=transition(before,after,baseline,blobs,raw)
    need(changed==receipt['changed_artifact_ids'] and retained==[r['id'] for r in receipt['retained_artifacts']],'PRODUCER_RECEIPT_COUNTS_MATCH_CALCULATION')
    need(len(changed)==198 and len(retained)==1,'FROZEN_WAVE35_AVAILABILITY_POPULATION')
    retained_record=old_artifacts[retained[0]]
    need(retained_record['path']=='acceleration/results/20261002_rooted8_gf3_solve01/solve/checkpoint.bin'
         and retained_record['sha256']=='c2c13e6e83079264344f9610ba31ebe254544b501d9b95e9cafea9ff2d66b0b8'
         and retained_record['availability']=='LOCAL_ONLY'
         and indexed(after['artifacts'])[retained[0]]==retained_record,'EXACT_RETAINED_CHECKPOINT_SCOPE')
    controls=[]
    damaged=copy.deepcopy(after);damaged['claims'][0]['statement']='changed'
    rejection(controls,'claim_statement_mutation','CLAIMS_AND_VERIFICATION_UNCHANGED',lambda:transition(before,damaged,baseline,blobs,raw))
    damaged=copy.deepcopy(after);damaged['claims'][0]['verification'][0]['outcome']='FAIL'
    rejection(controls,'verification_outcome_mutation','CLAIMS_AND_VERIFICATION_UNCHANGED',lambda:transition(before,damaged,baseline,blobs,raw))
    damaged=copy.deepcopy(after);damaged['target']['status']='NONEXISTENCE'
    rejection(controls,'target_promotion','TOPLEVEL_UNCHANGED',lambda:transition(before,damaged,baseline,blobs,raw))
    damaged=copy.deepcopy(after);damaged['artifacts'][0]['sha256']='0'*64
    rejection(controls,'prior_artifact_hash_mutation','ALL_PRIOR_ARTIFACTS_UNCHANGED',lambda:transition(before,damaged,baseline,blobs,raw))
    damaged=copy.deepcopy(after);indexed(damaged['artifacts'])[retained[0]]['availability']='PUBLIC'
    rejection(controls,'actual_local_checkpoint_false_public','UNAUTHENTICATED_ARTIFACT_NOT_PROMOTED',lambda:transition(before,damaged,baseline,blobs,raw))
    damaged=copy.deepcopy(after);damaged['claims'].pop()
    rejection(controls,'omitted_claim','CLAIMS_AND_VERIFICATION_UNCHANGED',lambda:transition(before,damaged,baseline,blobs,raw))
    damaged=copy.deepcopy(after);damaged['artifacts'].pop()
    rejection(controls,'omitted_artifact','ARTIFACT_ID_POPULATION_UNCHANGED',lambda:transition(before,damaged,baseline,blobs,raw))
    # The published direct members and five raw models are public. Test a truly unavailable member
    # using an explicit synthetic control, without inventing a real ledger item.
    synthetic={'id':'synthetic-unavailable-control','path':'build/synthetic-nonexistent-publication-control.bin',
               'sha256':'0'*64,'availability':'LOCAL_ONLY','retrieval':None,
               'unavailable_reason':'Synthetic negative control only; no actual artifact or claim.'}
    control_before=copy.deepcopy(before);control_after=copy.deepcopy(after)
    control_before['artifacts'].append(synthetic);control_after['artifacts'].append(copy.deepcopy(synthetic))
    positive,_=transition(control_before,control_after,baseline,blobs,raw)
    need(positive==changed,'SYNTHETIC_MISSING_POSITIVE_RETAINED')
    control_after['artifacts'][-1]['availability']='PUBLIC'
    rejection(controls,'synthetic_missing_artifact_false_public','UNAUTHENTICATED_ARTIFACT_NOT_PROMOTED',
              lambda:transition(control_before,control_after,baseline,blobs,raw))
    lossless=next((aid for aid in changed if old_artifacts[aid]['path'] in raw),None)
    if lossless is not None:
        damaged=copy.deepcopy(after);indexed(damaged['artifacts'])[lossless]['retrieval']='https://github.com/ikuto32/conway-99-graph/blob/main/unknown'
        rejection(controls,'actual_mutable_wrong_package_retrieval','LOSSLESS_IMMUTABLE_RETRIEVAL',lambda:transition(before,damaged,baseline,blobs,raw))
    else:
        # Existing package-backed artifacts may all belong to the preserved baseline.
        # Exercise the same exact transition path using a labelled synthetic record
        # with a real authenticated raw hash, not a fabricated production item.
        name=next(iter(raw));item=raw[name];prefix='https://github.com/ikuto32/conway-99-graph/blob/'+COMMIT+'/'
        added={'id':'synthetic-real-package-control','path':name,'sha256':item['sha256'],'availability':'LOCAL_ONLY','retrieval':None,'unavailable_reason':'Synthetic checking control only.'}
        control_before=copy.deepcopy(before);control_after=copy.deepcopy(after);control_before['artifacts'].append(added)
        promoted=copy.deepcopy(added);promoted.update(availability='PUBLIC',unavailable_reason=None,retrieval='Lossless public package: '+prefix+item['manifest']+'; restore into a fresh destination. '+name+'; '+item['sha256']+'; not mathematical replay.')
        control_after['artifacts'].append(promoted);transition(control_before,control_after,baseline,blobs,raw)
        control_after['artifacts'][-1]['retrieval']='https://github.com/ikuto32/conway-99-graph/blob/main/unknown'
        rejection(controls,'synthetic_mutable_wrong_package_retrieval','LOSSLESS_IMMUTABLE_RETRIEVAL',lambda:transition(control_before,control_after,baseline,blobs,raw))
    sample_name,sample_hash,sample_package=packages[0]
    for label,expected,mutate in [
        ('dropped_gzip_part','RAW_WHOLE_IDENTITY',lambda p:p['records'][0]['parts'].pop()),
        ('wrong_raw_hash','RAW_WHOLE_IDENTITY',lambda p:p['records'][0].update(raw_sha256='0'*64)),
        ('noncontiguous_offset','RAW_CONTIGUOUS_OFFSET',lambda p:p['records'][0]['parts'][1].update(raw_offset=1))]:
        corrupt=copy.deepcopy(sample_package);mutate(corrupt)
        rejection(controls,label,expected,lambda:decoded_records(corrupt,sample_name,sample_hash,blobs,deadline))
    for name in (Path(__file__).relative_to(ROOT).as_posix(),'acceleration/audit_20261003_wave35_availability_v1_spec.md',
                 'acceleration/audit_20261002_wave34_availability_v1_spec.md',
                 'acceleration/audit_20261002_wave33_availability_v2.py','acceleration/audit_20261002_wave33_availability_v2_spec.md',
                 'acceleration/audit_20261002_wave33_availability_v1.py','acceleration/audit_20261002_wave33_availability_v1_spec.md',
                 'acceleration/confirm_20261003_wave35_publication_v1.py','acceleration/command_deadline.py','acceleration/run_compute_command.py','uv.lock','pyproject.toml',
                 'docs/DEVIATION_20261002_WAVE35_STAGE_METADATA.md','.gitattributes',
                 'acceleration/results/20261002_wave35_stage01/manifest.json',
                 'acceleration/results/20261002_wave35_stage_supervision01/summary.json',
                 'acceleration/results/20261002_wave35_index_identity_supervision01/summary.json',
                 'acceleration/results/20261002_wave35_index_identity_supervision02/summary.json',
                 'acceleration/results/20261003_wave35_public_confirmation_supervision01/summary.json'):
        pin(name)
    report={'status':'INDEPENDENT_WAVE35_AVAILABILITY_ONLY_PUBLIC_TRANSITION_PASS','timestamp':datetime.now(timezone.utc).isoformat(),
       'verifier':'/root/checkpoint_audit','producer':'/root','source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
       'command':[sys.executable,*sys.argv],'cwd':str(ROOT),'python':platform.python_version(),'inputs_sha256':pins,
       'publication_commit':COMMIT,'remote_branch_observation':remote,'public_repository_observation':public,'remote_commit_observation':remote_commit,
       'before_ledger_sha256':BEFORE,'after_ledger_sha256':AFTER,'unchanged_claims':334,'new_claims':0,'mathematical_replays':0,
       'changed_public_artifact_records':len(changed),'changed_artifact_ids':changed,'retained_artifact_ids':retained,
       'immutable_git_blob_records':blobs,'immutable_git_blob_count':len(blobs),'stage_record_count':len(stage['records']),
       'raw_records':raw,'raw_population':{'raw_members':5,'gzip_parts':parts,'raw_bytes':184494332,'gzip_bytes':compressed},
       'git_tree_commands':tree_commands,'git_archive_commands':archive_commands,'controls':controls,
       'changed_reader_calibration':{'commands':calibration_commands,'literal_stage_anchor':calibration_blobs[STAGE],
                                    'outcome':'PASS','residual_stdout_drained_before_stderr_wait':True},
       'preserved_failed_version':{'source':'acceleration/audit_20261002_wave33_availability_v1.py',
                                  'supervision':'acceleration/results/20261002_independent_review/wave33_availability_supervision01',
                                  'outcome':'Contained Git archive stdout/stderr pipe deadlock; authenticated early child stop,240.734seconds,exit1,reaped,empty Job. No availability approval.'},
       'preserved_failed_version2':{'source':'acceleration/audit_20261002_wave33_availability_v2.py',
                                   'supervision':'acceleration/results/20261002_independent_review/wave33_availability_supervision02',
                                   'outcome':'All byte/transition checks passed before StopIteration in unavailable-artifact control setup because all new wave33 records were public;12.172seconds,exit1,reaped,empty Job. No PASS summary.'},
       'target_resolution':'UNKNOWN','overall_search_coverage':'UNKNOWN; no validated denominator.','new_exclusions':0,
       'elapsed_seconds':time.monotonic()-start,'deadline':deadline.status(),
       'shared_components':['Prior independent wave34 audit implementation copied into a newly versioned334-claim/198-public/one-local scope, with new controls and exact new pins; historical gates do not approve this changed invocation.','Git commit/tree/archive implementations','Python yaml.SafeLoader with independent duplicate-key rejection','gzip/sha256 byte decoding','command_deadline scheduling'],
       'limitations':['No mathematical replay, claim promotion or live-ledger equivalence assertion; frozen334-record snapshots only.',
         'Public repo and commit independently observed viaGitHub API; local Git archive bytes authenticated to immutable commit. No separate clean-clone/network retransmission of all payload bytes.',
         'Five literal raw artifacts publicly recover through25 gzip parts; original raw paths are absent from Git.',
         'Complete historical transitive proof/checker closure and platform binaries have separately retained availability.',
         'The fresh wave35 producer invocation succeeded. Stage01 success prose had a checkpoint size typo, separately corrected without changing its successful executed guard or receipts. Index01 detected two documentation line-ending mismatches, remedied by new byte-preserving attributes and renormalization. Original artifacts and receipts retained.',
         'The new unrestricted root7 model/LP claims are outside this frozen wave35 cutoff.']}
    with (out/'summary.json').open('x',encoding='utf8',newline='\n') as stream:json.dump(report,stream,indent=2);stream.write('\n')
    print(json.dumps({'path':str(out/'summary.json'),'sha256':digest(out/'summary.json'),'changed_artifact_records':len(changed),'status':report['status']}))

if __name__=='__main__':main()
