"""Frozen single-model gzip recovery for wave23 transport, not an encoding audit.

Authenticate the existing package and original, stream to a fresh ignored build
directory, and preserve both originals. No new compression, native call or ledger
mutation. Expected raw12,246,378 bytes; gzip470,548 bytes (<10MiB).
"""
from datetime import datetime, timezone
from pathlib import Path
import argparse, gzip, hashlib, json, platform, subprocess, sys, time

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'acceleration/results/20260930_hadamard_six_profile_cnf/profile_0000'
PINS={BASE/'model_package.json':'f523bbb7f6f897429e0d11a051f31efa89ebd88630ea7917a84fa95b47a80e34',BASE/'model.json':'d4135051531ee32265b7217ee89a37f0046b59f19862a35eb7cf3dfc8a6738bc',BASE/'model.json.gz':'5599fb13869d074e1bce90e05e18f05505ad1983912d62e8e743f9822000eff2'}

def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def need(ok,msg):
    if not ok:raise ValueError(msg)
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--receipt-dir',type=Path,required=True);a=p.parse_args()
    out=a.out.resolve();receipt=a.receipt_dir.resolve()
    need(out.is_relative_to((ROOT/'build').resolve()),'restoration confined to build workspace')
    need(receipt.is_relative_to(ROOT),'receipt confined to workspace')
    out.mkdir(parents=True,exist_ok=False);receipt.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    try:
        for path,digest in PINS.items():need(sha(path)==digest,'existing package/original identity')
        package=json.loads((BASE/'model_package.json').read_bytes())
        need(package['raw_bytes']==12246378 and package['gzip_bytes']==470548,'frozen size')
        need(package['raw_sha256']==PINS[BASE/'model.json'] and package['gzip_sha256']==PINS[BASE/'model.json.gz'],'manifest hashes')
        need(package['raw_path']==key(BASE/'model.json') and package['gzip_path']==key(BASE/'model.json.gz'),'literal paths')
        total=hashlib.sha256();size=0;dest=out/'model.json'
        with gzip.open(BASE/'model.json.gz','rb') as source,dest.open('xb') as target:
            for block in iter(lambda:source.read(1048576),b''):
                target.write(block);size+=len(block);total.update(block)
        need(size==package['raw_bytes'] and total.hexdigest()==package['raw_sha256']==sha(dest),'whole restored identity')
        for path,digest in PINS.items():need(sha(path)==digest,'existing files unchanged')
        result=dict(status='SIX_LITERAL_MODEL_GZIP_RECOVERY_IDENTITY_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256={**{key(p):h for p,h in PINS.items()},key(Path(__file__)):sha(Path(__file__)),key(ROOT/'uv.lock'):sha(ROOT/'uv.lock'),key(ROOT/'pyproject.toml'):sha(ROOT/'pyproject.toml')},restored_path=key(dest),restored_sha256=sha(dest),raw_bytes=size,gzip_bytes=package['gzip_bytes'],elapsed_seconds=time.monotonic()-start,originals_preserved=True,mathematical_verification=False,native_calls=0,artifact_availability='LOCAL_ONLY')
        with (receipt/'summary.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(result,f,indent=2);f.write('\n')
        print(json.dumps(result))
    except BaseException as error:
        with (receipt/'failure.json').open('x',encoding='utf-8') as f:json.dump(dict(error=repr(error),source_sha256=sha(Path(__file__)),originals_not_deleted=True),f,indent=2)
        raise
if __name__=='__main__':main()
