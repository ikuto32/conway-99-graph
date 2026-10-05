"""Independent lossless recovery of the already checked balanced proof."""
import argparse,copy,gzip,hashlib,io,json,platform,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results'
PACKAGE=B/'20260930_hadamard_balanced_gram_proof_packages/artifact_packages.json'
GATE=B/'20260930_independent_review/hadamard_balanced_gram_unsat_v2/summary.json'
PACKAGE_SHA='788368dea343adff368a2d0fdd464e7e743a957625bbd6ec3c2f7f5523b138f9'
GATE_SHA='edbbda720ea38ca5c565837bc39b5083eb145a64386c9e070fe89dfe5d6cebc5'
RAW_SHA='94d2ab35c76b61f3deb01ebfd9ca0dc70452bddf847383d5838b2b2ca902396b'
def need(x,m):
    if not x:raise ValueError(m)
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def save(p,x):
    with Path(p).open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
def validate_manifest(m):
    need(m['raw_sha256']==RAW_SHA and m['raw_bytes']==227098316,'already checked raw proof identity')
    need(m['raw_path']=='acceleration/results/20260930_hadamard_balanced_gram_native_pilot/main/proof.drat','exact raw proof path')
    need(m['independent_proof_gate']==dict(path=key(GATE),sha256=GATE_SHA),'same complete proof gate')
    need(len(m['parts'])==6 and m['compressed_bytes']==52339920,'complete transport counts')
    seen=set()
    for i,r in enumerate(m['parts']):
        expected='acceleration/results/20260930_hadamard_balanced_gram_proof_packages/proof.drat.gz.part'+format(i,'03d')
        need(r['path']==expected and r['path'] not in seen,'exact unique ordered part path');seen.add(r['path'])
        need(type(r['bytes'])is int and 0<r['bytes']<=9*1024**2 and len(r['sha256'])==64,'public-size part metadata')
    need(sum(r['bytes'] for r in m['parts'])==m['compressed_bytes'],'complete compressed byte count')
def decode_bytes(blob):
    # Generic control uses the same gzip file interface as actual recovery.
    with gzip.GzipFile(fileobj=io.BytesIO(blob),mode='rb') as stream:return stream.read()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--recovery-dir',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();recovery=a.recovery_dir.resolve()
    need(recovery.is_relative_to(ROOT/'build'),'fresh recovery stays in ignored build directory')
    out.mkdir(parents=True,exist_ok=False);recovery.mkdir(parents=True,exist_ok=False);start=time.perf_counter();pins={}
    def pin(p,h=None):
        p=p.resolve();actual=sha(p);need(h is None or actual==h,'input hash '+key(p));pins[key(p)]=actual
    try:
        pin(PACKAGE,PACKAGE_SHA);pin(GATE,GATE_SHA);m=read(PACKAGE);gate=read(GATE);validate_manifest(m)
        need(gate['status']=='INDEPENDENT_FIXED_HADAMARD_BALANCED_GRAM_UNSAT_PASS' and gate['proof']['complete_independent_replay'] is True and gate['proof']['sha256']==RAW_SHA and gate['proof']['bytes']==m['raw_bytes'],'bind already replayed exact proof')
        producer_manifest=PACKAGE.parent/'manifest.json';pin(producer_manifest)
        for path,h in read(producer_manifest)['inputs_sha256'].items():
            if path==m['raw_path']:continue
            pin(ROOT/path,h)
        combined=recovery/'proof.drat.gz';compressed_hash=hashlib.sha256();compressed_bytes=0
        with combined.open('xb') as target:
            for record in m['parts']:
                p=ROOT/record['path'];pin(p,record['sha256']);need(p.stat().st_size==record['bytes'],'part raw length')
                with p.open('rb') as source:
                    for chunk in iter(lambda:source.read(1048576),b''):
                        target.write(chunk);compressed_hash.update(chunk);compressed_bytes+=len(chunk)
        need(compressed_bytes==m['compressed_bytes'] and compressed_hash.hexdigest()==m['compressed_sha256'],'ordered combined compressed bytes/hash')
        original=ROOT/m['raw_path'];original_exists=original.exists();original_stream=original.open('rb') if original_exists else None
        recovered=recovery/'proof.drat';raw_hash=hashlib.sha256();raw_bytes=0
        try:
            with gzip.open(combined,'rb') as source,recovered.open('xb') as target:
                for chunk in iter(lambda:source.read(1048576),b''):
                    target.write(chunk);raw_hash.update(chunk);raw_bytes+=len(chunk)
                    need(raw_bytes<=m['raw_bytes'],'no inflated recovery size')
                    if original_stream:need(original_stream.read(len(chunk))==chunk,'literal byte equality with original checked trace')
            if original_stream:need(original_stream.read(1)==b'','same original EOF')
        finally:
            if original_stream:original_stream.close()
        need(raw_bytes==m['raw_bytes'] and raw_hash.hexdigest()==RAW_SHA and sha(recovered)==RAW_SHA,'complete independently recovered raw identity')
        if original_exists:pin(original,RAW_SHA)
        rejected=[]
        def reject(name,fn):
            try:fn()
            except(ValueError,EOFError,OSError,KeyError,IndexError):rejected.append(name)
            else:raise ValueError('accepted corrupt transport '+name)
        for name in ['missing_part','swap_parts','duplicate_part','wrong_raw_hash','oversize_part','wrong_gate','wrong_total']:
            bad=copy.deepcopy(m)
            if name=='missing_part':bad['parts'].pop()
            elif name=='swap_parts':bad['parts'][0],bad['parts'][1]=bad['parts'][1],bad['parts'][0]
            elif name=='duplicate_part':bad['parts'][1]=copy.deepcopy(bad['parts'][0])
            elif name=='wrong_raw_hash':bad['raw_sha256']='0'*64
            elif name=='oversize_part':bad['parts'][0]['bytes']=10*1024**2
            elif name=='wrong_gate':bad['independent_proof_gate']['sha256']='0'*64
            else:bad['compressed_bytes']-=1
            reject(name,lambda bad=bad:validate_manifest(bad))
        positive=bytes(range(256))*19+b'0\n';encoded=gzip.compress(positive,mtime=0)
        chunks=[encoded[i:i+37] for i in range(0,len(encoded),37)]
        need(decode_bytes(b''.join(chunks))==positive,'generic segmented gzip positive')
        reject('truncated_gzip',lambda:decode_bytes(encoded[:-3]))
        altered=bytearray(encoded);altered[-8]^=1;reject('changed_gzip_CRC',lambda:decode_bytes(bytes(altered)))
        # Raw part identity catches changes even if an altered gzip header remains decodable.
        altered=bytearray(encoded);altered[4]^=1
        reject('changed_part_bytes',lambda:need(hashlib.sha256(altered).digest()==hashlib.sha256(encoded).digest(),'exact part identity'))
        save(out/'controls.json',dict(generic_segmented_positive_bytes=len(positive),generic_segments=len(chunks),corruptions_rejected=rejected))
        ts=datetime.now(timezone.utc).isoformat();pin(Path(__file__));pin(ROOT/'uv.lock');pin(ROOT/'pyproject.toml')
        result=dict(status='INDEPENDENT_BALANCED_GRAM_PROOF_TRANSPORT_PASS',timestamp=ts,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,outputs_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},proof_gate=dict(path=key(GATE),sha256=GATE_SHA),recovery=dict(raw_path=key(recovered),raw_bytes=raw_bytes,raw_sha256=RAW_SHA,compressed_path=key(combined),compressed_bytes=compressed_bytes,compressed_sha256=compressed_hash.hexdigest(),literal_original_comparison=original_exists,raw_original_retained=original_exists),parts=6,maximum_part_bytes=max(r['bytes'] for r in m['parts']),corruptions_rejected=len(rejected),proof_replays=0,reason_no_repeat_replay='Recovered bytes are identical to the exact complete proof already independently replayed.',artifact_availability='LOCAL_ONLY',availability_reason='Package parts are ready for public-size publication; repository publication is controlled by parent and has not been inferred.',shared_components=['Python gzip implementation shares zlib with the producer compression library; verification additionally requires exact compressed/raw hashes and complete literal raw comparison.','No producer packaging code imported.'],target_resolution=False,elapsed_seconds=time.perf_counter()-start)
        save(out/'summary.json',result);print(json.dumps(dict(status=result['status'],summary_sha256=sha(out/'summary.json'))))
    except BaseException as ex:save(out/'failure.json',dict(error=repr(ex)));raise
if __name__=='__main__':main()
