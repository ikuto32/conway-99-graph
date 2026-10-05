"""Stream recovery/identity check for packaged raw DRAT bytes; no proof approval."""
from pathlib import Path
import argparse,gzip,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def recover_record(record,base,destination=None):
    total=hashlib.sha256();offset=0;writer=None
    if destination is not None:
        destination=Path(destination);destination.parent.mkdir(parents=True,exist_ok=True);writer=destination.open('xb')
    try:
        for index,part in enumerate(record['parts']):
            path=(base/part['relative_path']).resolve();need(path.is_relative_to(base.resolve()),'package part stays inside package');need(part['index']==index and part['raw_offset']==offset,'ordered contiguous chunks');need(path.stat().st_size==part['gzip_bytes'] and sha(path)==part['gzip_sha256'],'compressed part identity')
            one=hashlib.sha256();size=0
            with gzip.open(path,'rb') as f:
                for block in iter(lambda:f.read(1048576),b''):
                    total.update(block);one.update(block);size+=len(block)
                    if writer:writer.write(block)
            need(size==part['raw_bytes'] and one.hexdigest()==part['raw_sha256'],'decompressed part identity');offset+=size
        need(offset==record['raw_bytes'] and total.hexdigest()==record['raw_sha256'],'whole raw proof identity')
        return dict(case=record['case'],raw_bytes=offset,raw_sha256=total.hexdigest(),parts=len(record['parts']),identity_pass=True,proof_validity_checked=False)
    finally:
        if writer:writer.close()
def main():
    p=argparse.ArgumentParser();p.add_argument('--manifest',type=Path,required=True);p.add_argument('--manifest-sha256',required=True);mode=p.add_mutually_exclusive_group(required=True);mode.add_argument('--verify-only',action='store_true');mode.add_argument('--out',type=Path);p.add_argument('--case',type=int);a=p.parse_args();need(sha(a.manifest)==a.manifest_sha256,'manifest identity');m=json.loads(a.manifest.read_bytes());need(m['schema']=='FOUR_PROFILE_RAW_DRAT_GZIP_PARTS_V1','package schema');records=m['records']
    if a.case is not None:records=[r for r in records if r['case']==a.case];need(len(records)==1,'case occurs exactly once')
    if a.out:a.out.mkdir(parents=True,exist_ok=False)
    results=[recover_record(r,a.manifest.parent,None if a.verify_only else a.out/f'case_{r["case"]:03d}'/'proof.drat') for r in records];print(json.dumps(dict(status='RAW_PROOF_RECOVERY_IDENTITY_PASS',proofs=len(results),raw_bytes=sum(r['raw_bytes'] for r in results),results=results,proof_validity_checked=False)))
if __name__=='__main__':main()
