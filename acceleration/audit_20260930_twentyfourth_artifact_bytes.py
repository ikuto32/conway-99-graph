"""Independent streaming byte/recovery and publication boundaries for wave24."""
from pathlib import Path, PurePosixPath
from copy import deepcopy
from collections import Counter
import gzip,hashlib,io,json,subprocess
from audit_20260930_sixteenth_checkpoint import require
from audit_20260930_twentythird_checkpoint_boundaries import PRIVATE,process_receipts
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';PACK=B+'twentyfourth_artifact_packaging/'
REC=B+'twentyfourth_raw_recovery/manifest.json'
REC_SHA='2311cebb8617c95c3ae3a4225def8ce2dce8992ae9621cdcfd8cf0684806c3c8'
WRAPPER_DIRS={B+'twentyfourth_preparation',B+'twentyfourth_artifact_packaging'}
WRAPPER_NAMES={'catalog.json','stage_inventory.json','reference_checks.json.gz'}
MAX=10*1024**2
FORBIDDEN=['count_master_eight_orbit_cut_native_pilot','count_master_eight_orbit_cut_native_preflight','count_master_eight_orbit_cut_object_calibration','count_master_eight_orbit_cut_sat_outcome','eight_count_profile_lift_second']
def safe(p):
    q=PurePosixPath(p)
    require(isinstance(p,str) and not q.is_absolute() and '..' not in q.parts and ':' not in p and '\\' not in p,'safe relative path')
    require(p!=PRIVATE and p!='PROMPT.md' and not p.startswith('tools/drat-trim') and q.name.lower() not in {'.env','.env.local','credentials','credentials.json','id_rsa','id_ed25519'} and not p.endswith(('.pem','.key')),'protected path excluded')
def payload_size(p,n):
    safe(p);q=PurePosixPath(p);maximum=32*1024**2 if q.parent.as_posix() in WRAPPER_DIRS and q.name in WRAPPER_NAMES else MAX
    require(type(n) is int and 0<=n<=maximum,'explicit public size boundary '+p)
def cohort(paths):
    for p in paths:
        safe(p);require(not any(x in p for x in FORBIDDEN),'future cohort excluded '+p)
        require(p not in ['acceleration/audit_20260930_count_master_eight_orbit_cut_object.py','acceleration/audit_20260930_count_master_eight_orbit_cut_object_spec.md','acceleration/native_20260930_count_master_eight_orbit_cuts.py','acceleration/native_20260930_count_master_eight_orbit_cuts_spec.md','docs/AUDIT_20260930_COUNT_MASTER_EIGHT_ORBIT_CUT_OBJECT.md'],'future native/checker excluded')
def normal(m,origin):
    path=m.get('raw_path',m.get('raw_original_path'));require(path,'raw package path')
    if 'gzip_path' in m:
        parts=[dict(path=m['gzip_path'],gzip_sha256=m['gzip_sha256'],gzip_bytes=m['gzip_bytes'],raw_offset=0,raw_sha256=m['raw_sha256'],raw_bytes=m['raw_bytes'])]
    else:
        parts=[]
        for i,p in enumerate(m['parts']):
            require('index' not in p or p['index']==i,'ordered part index')
            dest=p.get('path') or (PurePosixPath(origin).parent/p['relative_path']).as_posix()
            parts.append(dict(path=dest,gzip_sha256=p.get('gzip_sha256',p.get('sha256')),gzip_bytes=p.get('gzip_bytes',p.get('bytes')),raw_offset=p['raw_offset'],raw_sha256=p['raw_sha256'],raw_bytes=p['raw_bytes']))
    return dict(manifest=origin,path=path,sha256=m['raw_sha256'],bytes=m['raw_bytes'],parts=parts)
def recovery_population(load):
    manifest=load(REC,REC_SHA)
    for p,h in manifest['inputs_sha256'].items():load(p,h) if p.endswith('.json') else None
    batch=load(B+'hadamard_seven_remaining_cnfs/run02/summary.json')
    require(batch['completed_formulas']==215 and batch['pending_profiles']==[] and len(batch['selection'])==len(set(batch['selection']))==len(batch['records'])==215,'resumed complete215 build population')
    rows=[]
    for r in batch['records']:
        m=load(r['model_package_path'],r['model_package_sha256']);require(m['raw_path']==r['model_path'] and m['raw_sha256']==r['model_sha256'],'model identity in actual batch')
        rows.append(normal(m,r['model_package_path']))
    for p in [B+'hadamard_seven_profile_cnf/profile_0001/model_package.json',B+'eight_count_profile_lift/model_package.json']:rows.append(normal(load(p),p))
    for p,key in [(B+'hadamard_count_master_cnf/packages.json','records'),(B+'count_interval_cnf/packages.json','records'),(B+'count_master_eight_orbit_cuts/artifact_packages.json','packages'),(B+'count_interval_frechet_package/package_manifest.json','records'),(B+'hadamard_seven_profile_proof_package/package_manifest.json','records'),(B+'twentyfourth_literal_proof_package/package_manifest.json','records')]:
        rows.extend(normal(m,p) for m in load(p)[key])
    require(rows==manifest['records'] and len(rows)==len({r['path'] for r in rows})==443,'exact normalized recovery population')
    require(sum(r['bytes'] for r in rows)==manifest['raw_bytes']==3548174273 and sum(len(r['parts']) for r in rows)==manifest['gzip_parts']==484,'recovery byte/stream census')
    return rows
def stream_recover(record,raw_stream,open_part,pin=None):
    whole=hashlib.sha256();offset=0
    for p in record['parts']:
        require(p['raw_offset']==offset,'ordered raw offset')
        with open_part(p['path']) as compressed:
            ch=hashlib.sha256();n=0
            for block in iter(lambda:compressed.read(1048576),b''):ch.update(block);n+=len(block)
            require(n==p['gzip_bytes'] and ch.hexdigest()==p['gzip_sha256'],'compressed identity')
            compressed.seek(0);ph=hashlib.sha256();length=0
            with gzip.GzipFile(fileobj=compressed,mode='rb') as stream:
                for block in iter(lambda:stream.read(1048576),b''):
                    require(raw_stream.read(len(block))==block,'literal recovered/original bytes')
                    ph.update(block);whole.update(block);length+=len(block)
            require(length==p['raw_bytes'] and ph.hexdigest()==p['raw_sha256'],'per-part raw identity');offset+=length
        if pin:pin(p['path'],p['gzip_sha256'])
    require(raw_stream.read(1)==b'' and offset==record['bytes'] and whole.hexdigest()==record['sha256'],'whole restored original')
    return dict(path=record['path'],sha256=whole.hexdigest(),bytes=offset,gzip_streams=len(record['parts']))
def controls():
    positives=[];rejected=[]
    def reject(label,fn):
        try:fn()
        except (ValueError,KeyError,EOFError,gzip.BadGzipFile):rejected.append(label)
        else:raise ValueError('accepted corruption '+label)
    for d in WRAPPER_DIRS:
        for n in WRAPPER_NAMES:payload_size(d+'/'+n,32*1024**2);positives.append(d+'/'+n)
    for p,n in [('a.dat',MAX+1),(B+'twentyfourth_preparation/model.json',MAX+1),(B+'other/catalog.json',MAX+1),(PACK+'catalog.json',32*1024**2+1),('../escape',1),(PRIVATE,1)]:reject('size/privacy '+p,lambda p=p,n=n:payload_size(p,n))
    reject('future cohort',lambda:cohort([B+'eight_count_profile_lift_second/summary.json']))
    reject('broad process',lambda:process_receipts(dict(command=['ps','-eo','pid,args'])))
    raw=b'abc\x00\xff\n'*47;pieces=[raw[:131],raw[131:]];blobs={str(i):gzip.compress(x,mtime=0) for i,x in enumerate(pieces)}
    parts=[];offset=0
    for i,x in enumerate(pieces):
        z=blobs[str(i)];parts.append(dict(path=str(i),gzip_sha256=hashlib.sha256(z).hexdigest(),gzip_bytes=len(z),raw_offset=offset,raw_sha256=hashlib.sha256(x).hexdigest(),raw_bytes=len(x)));offset+=len(x)
    rec=dict(path='control',sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),parts=parts)
    def run(r=rec,b=blobs,x=raw):return stream_recover(r,io.BytesIO(x),lambda p:io.BytesIO(b[p]))
    run();positives.append('known two-part exact binary reconstruction')
    for label,field,value in [('wrong whole hash','sha256','0'*64),('wrong whole length','bytes',len(raw)+1)]:
        bad=deepcopy(rec);bad[field]=value;reject(label,lambda bad=bad:run(bad))
    for label,field,value in [('part hash','gzip_sha256','0'*64),('part length','gzip_bytes',0),('raw hash','raw_sha256','0'*64),('raw length','raw_bytes',0),('offset','raw_offset',1)]:
        bad=deepcopy(rec);bad['parts'][0][field]=value;reject(label,lambda bad=bad:run(bad))
    bad=deepcopy(rec);bad['parts'].reverse();reject('reordered parts',lambda:run(bad))
    reject('changed original',lambda:run(x=b'X'+raw[1:]));reject('truncated gzip',lambda:run(b={'0':blobs['0'][:-1],'1':blobs['1']}))
    return dict(positive=positives,rejected=rejected)
def canonical_gzip(path):
    with (ROOT/path).open('rb') as f:header=f.read(10)
    require(header[:3]==b'\x1f\x8b\x08' and header[3]&8==0 and header[4:8]==b'\0'*4,'deterministic gzip header')
    with gzip.open(ROOT/path,'rb') as f:raw=f.read()
    data=json.loads(raw);require(raw==(json.dumps(data,sort_keys=True,separators=(',',':'))+'\n').encode(),'canonical gzip JSON')
    return data
def audit_catalog(load,pin,summary_hash,catalog_hash,stage_hash,claim_ids,packages):
    summary=load(PACK+'summary.json',summary_hash);catalog=load(PACK+'catalog.json',catalog_hash);stage=load(PACK+'stage_inventory.json',stage_hash)
    require(summary['status']=='TWENTYFOURTH_EXPLICIT_PUBLICATION_INVENTORY_PASS' and summary['claim_ids']==claim_ids,'catalog cohort/status')
    for p,h in summary['output_hashes'].items():pin(p,h);payload_size(p,(ROOT/p).stat().st_size)
    entries=catalog['entries'];by={r['path']:r for r in entries};require(len(by)==len(entries),'unique catalog entries')
    local={r['path'] for r in entries if r['availability']=='LOCAL_ONLY'};public={r['path'] for r in entries if r['availability']=='READY_FOR_PUBLICATION'}
    require(local=={r['path'] for r in packages} and local|public==set(by),'exact available/local population')
    cohort(set(by)|set(stage['paths']));require(not local&set(stage['paths']),'local originals omitted from stage')
    require(len(entries)==summary['selected_files'] and len(public)==summary['public_research_files'] and sum(by[p]['bytes'] for p in public)==summary['public_research_bytes'],'public census')
    require(summary['new_local_only_research_artifacts']==443 and summary['new_gzip_streams']==484 and summary['recovered_raw_bytes']==3548174273,'complete recovery census')
    # Reconstruct the exact explicit allowlist from directories/files rather than trusting aggregate counts.
    expected=set(catalog['exact_files'])
    for d in catalog['exact_directories']:expected.update(p.relative_to(ROOT).as_posix() for p in (ROOT/d).rglob('*') if p.is_file())
    require(expected==set(by),'complete exact allowlist')
    for p,r in by.items():
        pin(p,r['sha256']);require((ROOT/p).stat().st_size==r['bytes'],'catalog length')
        if p in public:payload_size(p,r['bytes'])
        else:require('recovery available' in r['limitation'],'local recovery disclosure')
    require(public<=set(stage['paths']) and len(stage['paths'])==len(set(stage['paths'])),'stage coverage/uniqueness')
    require({r['path'] for r in stage['entries']}==set(stage['paths']),'exact stage row set')
    for r in stage['entries']:pin(r['path'],r['sha256']);require((ROOT/r['path']).stat().st_size==r['bytes'],'stage length');payload_size(r['path'],r['bytes'])
    require(load(PACK+'reference_diagnostics.json')==dict(errors=[],count=0),'no unresolved closure records')
    refs=canonical_gzip(PACK+'reference_checks.json.gz');require(refs['schema']=='WAVE24_REFERENCE_MANIFEST_V1' and refs['status']=='EXACT_HASH_CLOSURE_AND_GZIP_RECOVERY_PASS','chunk reference format')
    count=0;unique=set();origins=set();coverage=Counter()
    tracked=set(subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0'))
    prior=load(catalog['prior_catalog']['path'],catalog['prior_catalog']['sha256']);priorrecover=set(prior['prior_recoverable_dependencies'])|{r['path'] for r in prior['entries'] if r['availability']=='LOCAL_ONLY' and 'recovery available' in r['limitation']}
    require(set(catalog['prior_recoverable_dependencies'])==priorrecover,'authenticated prior recovery population')
    tools={r['path'] for r in catalog['local_tools']}
    for r in catalog['local_tools']:pin(r['path'],r['sha256'])
    for i,p in enumerate(refs['parts']):
        require(p['index']==i and p['record_offset']==count and 0<p['records']<=25000,'chunk exact index/count/offset')
        pin(p['path'],p['sha256']);payload_size(p['path'],p['bytes']);require((ROOT/p['path']).stat().st_size==p['bytes'],'chunk length')
        chunk=canonical_gzip(p['path']);require(chunk['schema']=='WAVE24_REFERENCE_CHUNK_V1' and chunk['index']==i and len(chunk['records'])==p['records'],'chunk schema/count')
        for r in chunk['records']:
            require(r['path']!=PRIVATE,'private reference omitted');pin(r['path'],r['sha256']);require((ROOT/r['path']).stat().st_size==r['bytes'],'actual referenced bytes')
            require(r['path'] in by or r['path'] in tracked or r['path'] in tools or r['path'] in priorrecover or r['path'].startswith('external_conway99_research/'),'public/recoverable reference closure')
            unique.add(r['path']);origins.add(r['origin']);coverage[(r['origin'],r['path'],r['sha256'])]+=1
        count+=len(chunk['records'])
    require(count==refs['record_count']==summary['reference_bindings'] and len(unique)==refs['unique_referenced_files']==summary['unique_referenced_files'] and len(refs['parts'])==summary['reference_parts'],'exact reference populations')
    # All advertised input maps in selected JSONs must appear in the saved closure.
    # Resolve only repository paths and artifact IDs here; historical absolute forms are already individually byte-bound above.
    maps={'inputs_sha256','input_hashes','output_hashes','artifact_hashes','audit_artifact_hashes','checked_input_bindings','outputs_sha256','input_sha256'}
    direct=0
    def walk(obj,origin):
        nonlocal direct
        if isinstance(obj,dict):
            for k,v in obj.items():
                if k in maps and isinstance(v,dict):
                    for p,h in v.items():
                        if isinstance(h,str) and len(h)==64 and isinstance(p,str) and p.startswith(('acceleration/','docs/','build/','external_conway99_research/')):
                            require(coverage[(origin,p,h)]>0,'missing direct input closure '+origin+' '+p);direct+=1
                walk(v,origin)
        elif isinstance(obj,list):
            for v in obj:walk(v,origin)
    for p in sorted(by):
        if p.endswith('.json'):
            obj=json.loads((ROOT/p).read_bytes());process_receipts(obj);walk(obj,p)
    git=load(PACK+'git_byte_checks.json');require(git['status']=='CURRENT_GIT_FILTER_BYTES_PASS' and {r['path'] for r in git['records']}==public,'exact Git check population')
    for r in git['records']:
        data=(ROOT/r['path']).read_bytes();require(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==r['git_blob_sha1'] and r['sha256']==by[r['path']]['sha256'],'literal Git bytes')
    actual=subprocess.check_output(['git','hash-object','--stdin-paths'],cwd=ROOT,input=('\n'.join(r['path'] for r in git['records'])+'\n').encode()).decode().splitlines()
    require(actual==[r['git_blob_sha1'] for r in git['records']],'current Git filter bytes')
    recovered=[]
    for n,r in enumerate(packages):
        for p in r['parts']:require(p['path'] in public,'every public recovery part');payload_size(p['path'],p['gzip_bytes'])
        with (ROOT/r['path']).open('rb') as raw:checked=stream_recover(r,raw,lambda p:(ROOT/p).open('rb'),pin)
        recovered.append(checked)
        if (n+1)%50==0:print('independent literal recovery '+str(n+1)+'/443',flush=True)
    require(refs['gzip_recoveries']==[{k:r[k] for k in ['path','sha256','bytes','manifest']}|dict(gzip_streams=len(r['parts'])) for r in packages],'reference recovery records')
    return dict(summary=summary,catalog=catalog,stage=stage,public_paths=public,recovered=recovered,reference_records=count,unique_references=len(unique),direct_input_bindings_checked=direct)
