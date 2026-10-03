"""Independent wave23 artifact/recovery helpers; no producer imports."""
from pathlib import Path
import gzip,hashlib,json,subprocess
from audit_20260930_twentythird_checkpoint_boundaries import require,payload_size,privacy,process_receipts

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_';PACK=B+'twentythird_artifact_packaging/'

def recovery_population(load):
    batch=load(B+'hadamard_six_remaining_cnfs/run01/summary.json')
    proof_path=B+'hadamard_six_profile_proof_package/package_manifest.json'
    proofs=load(proof_path,'46edb96dd42e7c41105bd0cd2997ddec98e1e631a8aad268aeab0c0923058f5c')
    require(batch['selection']==[r['profile_id'] for r in proofs['records']] and len(batch['records'])==54,'same54 formula/proof population')
    model_refs=[(r['model_package_path'],r['model_package_sha256']) for r in batch['records']]
    model_refs.append((B+'hadamard_six_profile_cnf/profile_0000/model_package.json','f523bbb7f6f897429e0d11a051f31efa89ebd88630ea7917a84fa95b47a80e34'))
    result=[]
    for path,h in model_refs:
        m=load(path,h)
        result.append(dict(kind='model',path=m['raw_path'],sha256=m['raw_sha256'],bytes=m['raw_bytes'],parts=[dict(path=m['gzip_path'],gzip_sha256=m['gzip_sha256'],gzip_bytes=m['gzip_bytes'],raw_sha256=m['raw_sha256'],raw_bytes=m['raw_bytes'],raw_offset=0)]))
    for record in proofs['records']:
        result.append(dict(kind='proof',path=record['raw_original_path'],sha256=record['raw_sha256'],bytes=record['raw_bytes'],parts=[{**p,'path':(Path(proof_path).parent/p['relative_path']).as_posix()} for p in record['parts']]))
    require(len(result)==len({r['path'] for r in result})==109,'exact109 recoverable originals')
    return result

def recover(package,part_data):
    require(len(package['parts'])==len(part_data)>0,'all ordered gzip parts')
    chunks=[];offset=0
    for p,data in zip(package['parts'],part_data,strict=True):
        require(p['raw_offset']==offset and len(data)==p['gzip_bytes'] and hashlib.sha256(data).hexdigest()==p['gzip_sha256'],'exact ordered compressed part')
        raw=gzip.decompress(data)
        require(len(raw)==p['raw_bytes'] and hashlib.sha256(raw).hexdigest()==p['raw_sha256'],'exact raw part')
        chunks.append(raw);offset+=len(raw)
    raw=b''.join(chunks)
    require(offset==len(raw)==package['bytes'] and hashlib.sha256(raw).hexdigest()==package['sha256'],'exact whole recovery')
    return raw

def audit_catalog(load,pin,summary_sha256,claim_ids,packages):
    summary=load(PACK+'summary.json',summary_sha256)
    require(summary['status']=='TWENTYTHIRD_EXPLICIT_PUBLICATION_INVENTORY_PASS' and summary['claim_ids']==claim_ids,'exact wave23 catalog cohort')
    for path,h in summary['output_hashes'].items():pin(path,h);payload_size(path,(ROOT/path).stat().st_size)
    catalog=load(PACK+'catalog.json');stage=load(PACK+'stage_inventory.json')
    entries=catalog['entries'];by={r['path']:r for r in entries};require(len(by)==len(entries),'unique catalog paths')
    privacy(set(by)|set(stage['paths']))
    local={r['path'] for r in entries if r['availability']=='LOCAL_ONLY'}
    require(local=={r['path'] for r in packages} and not local&set(stage['paths']),'exact109 local originals excluded from staging')
    require(all(r['availability'] in ['READY_FOR_PUBLICATION','LOCAL_ONLY'] for r in entries),'readiness not unsupported public assertion')
    public=[r for r in entries if r['availability']=='READY_FOR_PUBLICATION'];public_paths={r['path'] for r in public}
    require(len(entries)==summary['selected_files'] and len(public)==summary['public_research_files'] and sum(r['bytes'] for r in public)==summary['public_research_bytes'],'literal payload populations')
    require(summary['new_local_only_research_artifacts']==109 and summary['new_gzip_streams']==154,'55 model streams plus99 proof streams')
    for row in entries:
        pin(row['path'],row['sha256']);require((ROOT/row['path']).stat().st_size==row['bytes'],'exact payload length')
        if row['availability']=='READY_FOR_PUBLICATION':payload_size(row['path'],row['bytes'])
    require(public_paths<=set(stage['paths']),'public payload staging coverage')
    require(len(stage['paths'])==len(set(stage['paths'])),'unique stage paths')
    for row in stage['entries']:
        pin(row['path'],row['sha256']);payload_size(row['path'],(ROOT/row['path']).stat().st_size)
    require({r['path'] for r in stage['entries']}==set(stage['paths']),'stage entries exactly match paths')
    compressed=(ROOT/(PACK+'reference_checks.json.gz')).read_bytes()
    require(compressed[3]&8==0 and compressed[4:8]==b'\0'*4,'deterministic gzip reference wrapper')
    raw=gzip.decompress(compressed);refs=json.loads(raw)
    require(raw==(json.dumps(refs,sort_keys=True,separators=(',',':'))+'\n').encode(),'canonical JSON inside gzip')
    require(refs['status']=='EXACT_HASH_CLOSURE_AND_GZIP_RECOVERY_PASS' and len(refs['records'])==summary['reference_bindings'] and len({r['path'] for r in refs['records']})==summary['unique_referenced_files'],'complete reference populations')
    require(load(PACK+'reference_diagnostics.json')==dict(errors=[],count=0),'no unresolved reference diagnostics')
    for row in refs['records']:pin(row['path'],row['sha256']);require((ROOT/row['path']).stat().st_size==row['bytes'],'actual reference length')
    git=load(PACK+'git_byte_checks.json');require(git['status']=='CURRENT_GIT_FILTER_BYTES_PASS','saved Git filter check')
    for row in git['records']:
        require(row['path'] in public_paths,'Git payload is staged public research');data=(ROOT/row['path']).read_bytes()
        require(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['git_blob_sha1'],'literal Git blob identity')
    actual=subprocess.check_output(['git','hash-object','--stdin-paths'],cwd=ROOT,input=('\n'.join(r['path'] for r in git['records'])+'\n').encode()).decode().splitlines()
    require(actual==[r['git_blob_sha1'] for r in git['records']],'current actual Git filter result')
    recovered=[]
    for package in packages:
        for part in package['parts']:pin(part['path'],part['gzip_sha256']);require(part['path'] in public_paths,'every recovery part included')
        reconstructed=recover(package,[(ROOT/p['path']).read_bytes() for p in package['parts']])
        require(reconstructed==(ROOT/package['path']).read_bytes(),'literal recovered-original bytes')
        recovered.append({k:package[k] for k in ['kind','path','sha256','bytes']})
    require(sum(r['bytes'] for r in recovered)==summary['recovered_raw_bytes'],'exact raw recovery total')
    for path in public_paths:
        if path.endswith('.json'):process_receipts(json.loads((ROOT/path).read_bytes()))
    return dict(summary=summary,catalog=catalog,stage=stage,public=public,public_paths=public_paths,reference_records=len(refs['records']),unique_references=len({r['path'] for r in refs['records']}),recovered=recovered)
