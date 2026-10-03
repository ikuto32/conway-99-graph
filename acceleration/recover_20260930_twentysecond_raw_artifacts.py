"""Restore exact fifteen model/proof originals from public lossless packages."""
from datetime import datetime,timezone
from pathlib import Path
import argparse,gzip,hashlib,json,os,platform,subprocess,sys,uuid
ROOT=Path(__file__).resolve().parents[1]
BATCH='acceleration/results/20260930_hadamard_four_profile_cnfs/summary.json'
PROOFS='acceleration/results/20260930_hadamard_four_profile_proof_package/package_manifest.json'
PINS={BATCH:'692f74a5bf3be681832978d2a0ec51ec373237d45f3df24ccf1c01cfb009584b',PROOFS:'e55ce731d5ca1d18c4f5f5c9fc3195bc934f20f45b0172fc867ca1781e976250'}
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(p.read_bytes())
def identity(p,d,n=None):need(p.is_file() and sha(p)==d and (n is None or p.stat().st_size==n),'exact artifact '+str(p))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--destination-dir',type=Path,default=ROOT);ap.add_argument('--verify-only',action='store_true');ap.add_argument('--receipt',type=Path,required=True);args=ap.parse_args()
    need(not args.receipt.exists(),'fresh receipt');destination=args.destination_dir.resolve();inputs={}
    for rel,d in PINS.items():identity(ROOT/rel,d);inputs[rel]=d
    batch=read(ROOT/BATCH);proofs=read(ROOT/PROOFS);need(batch['selection']==[p['case'] for p in proofs['records']],'same fifteen cases')
    records=[]
    for case in batch['records']:
        p=ROOT/case['model_package_path'];identity(p,case['model_package_sha256']);inputs[case['model_package_path']]=case['model_package_sha256'];m=read(p)
        need(m['raw_path']==case['model_path'] and m['raw_sha256']==case['model_sha256'],'model package raw binding')
        records.append(dict(kind='model',case=case['case'],raw_path=m['raw_path'],raw_sha256=m['raw_sha256'],raw_bytes=m['raw_bytes'],parts=[dict(path=m['gzip_path'],gzip_sha256=m['gzip_sha256'],gzip_bytes=m['gzip_bytes'],raw_sha256=m['raw_sha256'],raw_bytes=m['raw_bytes'],raw_offset=0)]))
    for proof in proofs['records']:
        parts=[]
        for part in proof['parts']:
            path=(ROOT/PROOFS).parent/part['relative_path'];need(path.resolve().is_relative_to((ROOT/PROOFS).parent.resolve()),'part contained in package')
            parts.append({**part,'path':path.relative_to(ROOT).as_posix()})
        records.append(dict(kind='proof',case=proof['case'],raw_path=proof['raw_path'],raw_sha256=proof['raw_sha256'],raw_bytes=proof['raw_bytes'],parts=parts))
    results=[]
    for record in records:
        rel=Path(record['raw_path']);need(not rel.is_absolute(),'relative target');target=(destination/rel).resolve();need(target.is_relative_to(destination),'target contained in destination')
        if target.exists():identity(target,record['raw_sha256'],record['raw_bytes'])
        temporary=None;writer=None;action='VERIFIED_EXISTING' if target.exists() else 'VERIFIED_STREAM_ONLY'
        if not target.exists() and not args.verify_only:
            target.parent.mkdir(parents=True,exist_ok=True);temporary=target.with_name(target.name+'.recovering-'+uuid.uuid4().hex);writer=temporary.open('xb');action='RESTORED_MISSING'
        whole=hashlib.sha256();total=0
        try:
            for part in record['parts']:
                p=ROOT/part['path'];identity(p,part['gzip_sha256'],part['gzip_bytes']);inputs[part['path']]=part['gzip_sha256'];need(part['raw_offset']==total,'contiguous raw chunks');chunk=hashlib.sha256();size=0
                with gzip.open(p,'rb') as f:
                    for block in iter(lambda:f.read(1048576),b''):
                        whole.update(block);chunk.update(block);size+=len(block)
                        if writer:writer.write(block)
                need(size==part['raw_bytes'] and chunk.hexdigest()==part['raw_sha256'],'exact decompressed chunk');total+=size
            need(total==record['raw_bytes'] and whole.hexdigest()==record['raw_sha256'],'exact whole original')
        finally:
            if writer:writer.close()
        if temporary is not None:
            identity(temporary,record['raw_sha256'],record['raw_bytes']);need(not target.exists(),'never overwrite an existing target');os.rename(temporary,target);identity(target,record['raw_sha256'],record['raw_bytes'])
        results.append({k:record[k] for k in ('kind','case','raw_path','raw_sha256','raw_bytes')}|dict(action=action))
    result=dict(status='TWENTYSECOND_RAW_ARTIFACT_RECOVERY_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),source_sha256=sha(Path(__file__)),inputs_sha256=inputs,destination=str(destination),verify_only=args.verify_only,records=results,models=15,proofs=15,mathematical_verification=False)
    args.receipt.parent.mkdir(parents=True,exist_ok=True)
    with args.receipt.open('x',encoding='utf-8',newline='\n') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(dict(status=result['status'],models=15,proofs=15,restored=sum(r['action']=='RESTORED_MISSING' for r in results))))
if __name__=='__main__':main()
