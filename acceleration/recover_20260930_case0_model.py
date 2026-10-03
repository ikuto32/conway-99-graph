"""Recover the exact case0 model from its public package; never replace bytes."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,gzip,hashlib,json,platform,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
MAN='acceleration/results/20260930_hadamard_case0_model_package/artifact_packages.json'
PIN='f5808a5c30b751e23144fd0c9a107ba6fd0db75602a2e29cc15193da5c9bfe6b'
def digest(b):return hashlib.sha256(b).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--destination-dir',type=Path,default=ROOT);ap.add_argument('--receipt',type=Path,required=True);a=ap.parse_args()
    rawmanifest=(ROOT/MAN).read_bytes();assert digest(rawmanifest)==PIN;m=json.loads(rawmanifest);parts=[];inputs={MAN:PIN}
    assert m['raw_path']=='acceleration/results/20260930_hadamard_case0_profile_cnf/model.json'
    for part in m['parts']:
        p=(ROOT/part['path']).resolve();assert p.is_relative_to(ROOT);b=p.read_bytes();assert len(b)==part['bytes']and digest(b)==part['sha256'];parts.append(b);inputs[part['path']]=part['sha256']
    packed=b''.join(parts);assert len(packed)==m['compressed_bytes']and digest(packed)==m['compressed_sha256'];raw=gzip.decompress(packed)
    assert len(raw)==m['raw_bytes']==13208093 and digest(raw)==m['raw_sha256']=='6705e33a26c332d093e3a2bff6dcd5dca276c6b50da2b24c61c7cbf891e0629c'
    base=a.destination_dir.resolve();dest=(base/m['raw_path']).resolve();assert base.is_relative_to(ROOT)and dest.is_relative_to(base)
    existed=dest.exists()
    if existed:assert dest.read_bytes()==raw,'refuse differing destination'
    else:
        dest.parent.mkdir(parents=True,exist_ok=True)
        with dest.open('xb')as f:f.write(raw)
    assert digest(dest.read_bytes())==m['raw_sha256']
    inputs[Path(__file__).relative_to(ROOT).as_posix()]=digest(Path(__file__).read_bytes())
    result=dict(status='CASE0_MODEL_LOSSLESS_RECOVERY_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=inputs,destination=str(dest),raw_sha256=m['raw_sha256'],raw_bytes=len(raw),existing_identical_file=existed,mathematical_verification=False)
    with a.receipt.open('x',encoding='utf8',newline='\n')as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(dict(status=result['status'],raw_bytes=len(raw),existing=existed)))
if __name__=='__main__':main()

