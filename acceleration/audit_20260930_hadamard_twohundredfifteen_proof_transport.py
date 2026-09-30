"""Independent literal gzip transport check; no producer/recovery imports."""
from copy import deepcopy
from datetime import datetime,timezone
from pathlib import Path,PurePosixPath
import argparse,gzip,hashlib,json,platform,subprocess,sys,time,zlib
from tqdm import tqdm

ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results'
PACKAGE=B/'20260930_hadamard_seven_profile_proof_package'
PROOF=B/'20260930_independent_review/hadamard_twohundredfifteen_profile_proofs/summary.json'
PLAN=ROOT/'docs/AUDIT_20260930_HADAMARD_TWOHUNDREDFIFTEEN_PROOF_TRANSPORT.md'
PINS={PACKAGE/'package_manifest.json':'05a524f429c2750e6cb8097a0f9235dddf9ad8a5c22176f411871bd977a78d4e',PACKAGE/'summary.json':'58978760203004a28e7cf865145f7d9a069a2c65d045acce97b84e032a7941e4',PACKAGE/'standalone_recovery_cli/receipt.json':'6c7719457c0d051f822fb3a7e78d0da597702b583a9e61d359581d4d93875d3a',PROOF:'14d5064f7d09f491899f25113844df53b0b49658abc549ed784ed0b92ad55210'}
MAX_RAW=8388608;MAX_GZIP=10485760
def need(ok,msg):
    if not ok:raise ValueError(msg)
def digest(data):return hashlib.sha256(data).hexdigest()
def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def key(path):return path.resolve().relative_to(ROOT).as_posix()
def read(path):return json.loads(path.read_bytes())
def save(path,obj):
    with path.open('x',encoding='utf8',newline='\n') as stream:json.dump(obj,stream,indent=2);stream.write('\n')

def checked_stream(record,base,original):
    total=hashlib.sha256();offset=0;compressed_bytes=0;parts=[];seen=set()
    need(record['parts'],'nonempty part list')
    with original.open('rb') as raw:
        for index,part in enumerate(record['parts']):
            name=PurePosixPath(part['relative_path']);need(not name.is_absolute() and '..' not in name.parts,'safe relative part path')
            path=(base/str(name)).resolve();need(path.is_relative_to(base.resolve()),'part inside frozen package')
            need(str(name) not in seen,'unique part path');seen.add(str(name))
            need(type(part['index']) is int and part['index']==index and part['raw_offset']==offset,'ordered contiguous part metadata')
            need(0<part['raw_bytes']<=MAX_RAW and (index==len(record['parts'])-1 or part['raw_bytes']==MAX_RAW),'bounded regular raw chunks')
            zipped=path.read_bytes();need(0<len(zipped)<MAX_GZIP and len(zipped)==part['gzip_bytes'] and digest(zipped)==part['gzip_sha256'],'compressed bytes and identity')
            need(zipped[:4]==b'\x1f\x8b\x08\x00' and zipped[4:8]==b'\x00'*4,'unnamed mtime-zero gzip header')
            decoder=zlib.decompressobj(31);recovered=decoder.decompress(zipped,MAX_RAW+1)
            need(decoder.eof and not decoder.unconsumed_tail and not decoder.unused_data,'single complete gzip stream')
            recovered+=decoder.flush();need(len(recovered)==part['raw_bytes'] and digest(recovered)==part['raw_sha256'],'literal raw chunk identity')
            need(raw.read(len(recovered))==recovered,'every byte equals independently checked original range')
            total.update(recovered);offset+=len(recovered);compressed_bytes+=len(zipped)
            parts.append(dict(index=index,relative_path=str(name),raw_offset=part['raw_offset'],raw_bytes=len(recovered),raw_sha256=digest(recovered),gzip_bytes=len(zipped),gzip_sha256=digest(zipped)))
        need(raw.read(1)==b'','no missing original suffix')
    need(offset==record['raw_bytes'] and total.hexdigest()==record['raw_sha256'],'whole proof exact identity')
    return dict(profile_id=record['profile_id'],raw_bytes=offset,raw_sha256=total.hexdigest(),gzip_bytes=compressed_bytes,parts=parts,literal_original_comparison=True)

def controls(out):
    out.mkdir();unit=b'alpha\x00\xff\n0\n';raw=unit*(MAX_RAW//len(unit)+2)+b'final suffix';original=out/'original.bin';original.write_bytes(raw)
    parts=[]
    for index,start in enumerate(range(0,len(raw),MAX_RAW)):
        block=raw[start:start+MAX_RAW];p=out/f'part{index}.gz';p.write_bytes(gzip.compress(block,compresslevel=9,mtime=0))
        parts.append(dict(index=index,relative_path=p.name,raw_offset=start,raw_bytes=len(block),raw_sha256=digest(block),gzip_bytes=p.stat().st_size,gzip_sha256=sha(p)))
    good=dict(profile_id='synthetic_binary_transport',raw_bytes=len(raw),raw_sha256=digest(raw),parts=parts);save(out/'positive.json',good);checked_stream(good,out,original)
    bads=[]
    def add(label,edit):
        bad=deepcopy(good);edit(bad);bads.append((label,bad))
    add('missing_part',lambda b:b['parts'].pop())
    add('duplicate_part',lambda b:b['parts'].append(deepcopy(b['parts'][0])))
    add('reordered_parts',lambda b:b['parts'].reverse())
    add('wrong_index',lambda b:b['parts'][0].update(index=1))
    add('wrong_offset',lambda b:b['parts'][0].update(raw_offset=1))
    add('wrong_gzip_hash',lambda b:b['parts'][0].update(gzip_sha256='0'*64))
    add('wrong_gzip_size',lambda b:b['parts'][0].update(gzip_bytes=1))
    add('wrong_raw_hash',lambda b:b['parts'][0].update(raw_sha256='0'*64))
    add('wrong_raw_size',lambda b:b['parts'][0].update(raw_bytes=1))
    add('wrong_whole_hash',lambda b:b.update(raw_sha256='0'*64))
    add('wrong_whole_size',lambda b:b.update(raw_bytes=b['raw_bytes']+1))
    add('outside_path',lambda b:b['parts'][0].update(relative_path='../outside.gz'))
    compressed=(out/parts[0]['relative_path']).read_bytes()
    mutated=bytearray(compressed);mutated[-8]^=1
    for label,data in [('truncated',compressed[:-1]),('bad_CRC',bytes(mutated)),('appended_member',compressed+gzip.compress(b'extra',mtime=0))]:
        path=out/(label+'.gz');path.write_bytes(data);add(label,lambda b,path=path:b['parts'][0].update(relative_path=path.name,gzip_bytes=path.stat().st_size,gzip_sha256=sha(path)))
    wrong=bytearray(raw[:MAX_RAW]);wrong[17]^=1;path=out/'changed_payload.gz';path.write_bytes(gzip.compress(wrong,compresslevel=9,mtime=0))
    add('self_consistent_changed_payload',lambda b:b['parts'][0].update(relative_path=path.name,gzip_bytes=path.stat().st_size,gzip_sha256=sha(path),raw_sha256=digest(wrong)))
    rejected=[]
    for label,bad in bads:
        save(out/(label+'.json'),bad)
        try:checked_stream(bad,out,original)
        except (ValueError,zlib.error,EOFError,OSError) as exc:rejected.append(dict(control=label,rejection=repr(exc)))
        else:raise ValueError('accepted corruption '+label)
    return dict(positive_binary_bytes=len(raw),positive_parts=len(parts),rejected=rejected)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True);args=parser.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic();pins={}
    def pin(path,expected=None):
        k=key(path)
        if k not in pins:pins[k]=sha(path)
        need(expected is None or pins[k]==expected,'identity '+k);return pins[k]
    try:
        for path,h in PINS.items():pin(path,h)
        manifest=read(PACKAGE/'package_manifest.json');summary=read(PACKAGE/'summary.json');proof=read(PROOF)
        need(manifest['schema']=='TWOHUNDREDFIFTEEN_PROFILE_RAW_DRAT_GZIP_PARTS_V1' and proof['status']=='INDEPENDENT_FIXED_HADAMARD_TWOHUNDREDFIFTEEN_PROFILE_UNSAT_PASS','exact transport and proof gates')
        need(manifest['raw_chunk_bytes']==MAX_RAW and manifest['strict_maximum_part_bytes']==MAX_GZIP and manifest['gzip_parameters']==dict(compresslevel=9,mtime=0,filename=''),'frozen packaging recipe')
        need(summary['package_manifest_path']==key(PACKAGE/'package_manifest.json') and summary['package_manifest_sha256']==PINS[PACKAGE/'package_manifest.json'],'summary manifest binding')
        for name,h in manifest['inputs_sha256'].items():pin(ROOT/name,h)
        need([r['profile_id'] for r in manifest['records']]==proof['selected_profiles'] and len(manifest['records'])==215,'exact ordered checked population')
        positive=controls(out/'controls');save(out/'controls.json',positive)
        checked=[];all_part_paths=set()
        for record,proved in tqdm(list(zip(manifest['records'],proof['profile_records'],strict=True)),desc='Independent literal proof recovery',mininterval=1):
            need(record['profile_id']==proved['profile_id'] and proved['outcome']=='UNSAT_VERIFIED','same literal proven profile')
            need(record['raw_original_path']==proved['trace']['path'] and record['raw_sha256']==proved['trace']['sha256'] and record['raw_bytes']==proved['trace']['bytes'],'proof identity from independent replay')
            need(record['cnf_sha256']==proved['cnf_sha256'] and record['profile_summary_path']==proved['run_summary_path'] and record['profile_summary_sha256']==proved['run_summary_sha256'],'same CNF and native receipt')
            native=read(ROOT/record['profile_summary_path']);need(record['preserved_ext4_original']==native['proof_copy']['linux_source'],'recorded original ext4 path')
            original=ROOT/record['raw_original_path'];pin(original,proved['trace']['sha256'])
            result=checked_stream(record,PACKAGE,original)
            for part in record['parts']:
                path=(PACKAGE/part['relative_path']).resolve();need(key(path) not in all_part_paths,'no shared package part');all_part_paths.add(key(path));pin(path,part['gzip_sha256'])
            need(sha(original)==record['raw_sha256'],'original preserved after literal comparison');checked.append(result)
        rawsum=sum(r['raw_bytes'] for r in checked);gzsum=sum(r['gzip_bytes'] for r in checked);partcount=sum(len(r['parts']) for r in checked);maximum=max(p['gzip_bytes'] for r in checked for p in r['parts'])
        need(rawsum==577482170==manifest['total_raw_bytes']==summary['total_raw_bytes']==proof['proof_bytes'],'complete raw byte total')
        need(gzsum==90689391==manifest['total_gzip_bytes']==summary['total_gzip_bytes'] and partcount==223==manifest['parts']==summary['gzip_parts'] and maximum==1732088==summary['largest_gzip_part_bytes'],'complete compressed inventory')
        need(all_part_paths=={key(p) for folder in PACKAGE.glob('rank5_*') for p in folder.glob('*.gz')},'no missing or extra research parts')
        cli=read(PACKAGE/'standalone_recovery_cli/receipt.json');need(cli['actual_exit_code']==0 and cli['manifest_sha256']==PINS[PACKAGE/'package_manifest.json'] and cli['proof_validity_checked'] is False,'standalone receipt scope')
        need(cli['command']==['uv','run','--locked','--offline','--cache-dir','.uv-cache-20260917','python','-B','acceleration/recover_20260930_seven_profile_proofs.py','--manifest',key(PACKAGE/'package_manifest.json'),'--manifest-sha256',PINS[PACKAGE/'package_manifest.json'],'--verify-only'],'exact standalone command')
        pin(ROOT/'acceleration/recover_20260930_seven_profile_proofs.py',cli['source_sha256'])
        for field in ['stdout','stderr']:pin(PACKAGE/'standalone_recovery_cli'/(field+'.log'),cli[field+'_sha256'])
        saved_cli=json.loads((PACKAGE/'standalone_recovery_cli/stdout.log').read_text());need(saved_cli['status']=='RAW_PROOF_RECOVERY_IDENTITY_PASS' and saved_cli['proofs']==215 and saved_cli['raw_bytes']==rawsum,'saved standalone complete result')
        need([(r['profile_id'],r['raw_bytes'],r['raw_sha256'],r['parts']) for r in saved_cli['results']]==[(r['profile_id'],r['raw_bytes'],r['raw_sha256'],len(r['parts'])) for r in checked],'independent agreement with saved CLI records')
        save(out/'recovered_identity_records.json',dict(records=checked))
        for path in [Path(__file__),PLAN,ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(path)
        now=datetime.now(timezone.utc).isoformat();cid='C-FIXED-HADAMARD-TWOHUNDREDFIFTEEN-PROOF-TRANSPORT'
        statement='The 223 hash-bound gzip parts in the frozen215-proof package reconstruct exactly, byte for byte, all215 independently checked raw proof streams totalling577482170 bytes, in their recorded chunk order. Every part is below10MiB; the aggregate compressed size is90689391 bytes.'
        limits=['Byte transport only; prior complete DRAT replay remains a separate dependency.','All payloads are currently local artifacts; no public publication or retrieval availability asserted.','No fixed-family union or Conway99 target conclusion is supplied by packaging.']
        claim=dict(id=cid,revision=1,statement=statement,kind='empirical/engineering result',basis=['COMPUTED'],status='VERIFIED',review_state='CLEAR',scope='Exactly215 streams and223 parts named in the frozen manifest.',assumptions=['Authentic prior proof identities and local retained original streams.'],dependencies=[dict(id='C-FIXED-HADAMARD-TWOHUNDREDFIFTEEN-SEVEN-EXCEPTION-PROFILE-EXCLUSIONS',revision=1,relation='verification_dependency')],verifier='/root',producer='/root/state_literature_audit',checking_method='Independent zlib member decoding and literal full-byte comparison against authenticated originals; all offsets, lengths, part/whole hashes and prior CNF identities checked.',shared_components=['Python hashlib/SHA256 and underlying zlib implementation; decoder path differs from producer gzip.open recovery.','No producer or recovery helper imported; prior exact proof verdict is hash-bound and not replayed here.'],inputs_sha256=pins,artifact_availability='LOCAL_ONLY',limitations=limits,created_at=now,updated_at=now)
        save(out/'claim_binding.json',claim)
        report=dict(status='INDEPENDENT_HADAMARD_TWOHUNDREDFIFTEEN_PROOF_TRANSPORT_PASS',timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),zlib_runtime=zlib.ZLIB_RUNTIME_VERSION,inputs_sha256=pins,outputs_sha256={key(p):sha(p) for p in out.rglob('*') if p.is_file()},proofs=215,raw_bytes=rawsum,gzip_parts=partcount,gzip_bytes=gzsum,largest_gzip_part_bytes=maximum,literal_original_comparison=True,controls=positive,claim_id=cid,claim_revision=1,limitations=limits,new_DRAT_replays=0,solver_calls=0,target_resolution=False,elapsed_seconds=time.monotonic()-start)
        save(out/'summary.json',report);print(json.dumps(dict(status=report['status'],summary_sha256=sha(out/'summary.json'),binding_sha256=sha(out/'claim_binding.json'))))
    except BaseException as exc:save(out/'failure.json',dict(error=repr(exc),source_sha256=sha(Path(__file__))));raise

if __name__=='__main__':main()
