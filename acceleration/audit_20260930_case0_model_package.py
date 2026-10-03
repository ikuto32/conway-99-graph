"""Independent raw identity check of the case0 model transport; no recovery writes."""
from pathlib import Path
from copy import deepcopy
from datetime import datetime,timezone
import argparse,gzip,hashlib,json,platform,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
RAW='acceleration/results/20260930_hadamard_case0_profile_cnf/model.json'
MAN='acceleration/results/20260930_hadamard_case0_model_package/artifact_packages.json'
EXPECTED='6705e33a26c332d093e3a2bff6dcd5dca276c6b50da2b24c61c7cbf891e0629c'
def digest(data):return hashlib.sha256(data).hexdigest()
def need(ok,text):
    if not ok:raise ValueError(text)
def check(man,parts,raw):
    need(man['raw_path']==RAW and man['raw_sha256']==EXPECTED,'exact scoped raw model')
    need(len(parts)==len(man['parts'])==1,'one frozen part')
    for data,part in zip(parts,man['parts']):need(len(data)==part['bytes'] and digest(data)==part['sha256'],'part identity')
    packed=b''.join(parts);need(len(packed)==man['compressed_bytes'] and digest(packed)==man['compressed_sha256'],'full gzip identity')
    result=gzip.decompress(packed)
    need(result==raw and len(result)==man['raw_bytes']==13208093 and digest(result)==EXPECTED,'literal decompressed bytes and hash')
    return len(result)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    man=json.loads((ROOT/MAN).read_bytes());parts=[(ROOT/p['path']).read_bytes()for p in man['parts']];raw=(ROOT/RAW).read_bytes();check(man,parts,raw);rejected=[]
    for name in ['part_hash','raw_hash','raw_path','truncated_part','changed_raw']:
        m=deepcopy(man);ps=parts[:];r=raw
        if name=='part_hash':m['parts'][0]['sha256']='0'*64
        elif name=='raw_hash':m['raw_sha256']='0'*64
        elif name=='raw_path':m['raw_path']='elsewhere.json'
        elif name=='truncated_part':ps[0]=ps[0][:-1]
        else:r=bytes([raw[0]^1])+raw[1:]
        try:check(m,ps,r)
        except ValueError:rejected.append(name)
        else:raise ValueError('accepted corruption '+name)
    paths=[RAW,MAN,*[p['path']for p in man['parts']],str(Path(__file__).resolve().relative_to(ROOT)).replace('\\','/')]
    report=dict(status='INDEPENDENT_CASE0_MODEL_TRANSPORT_IDENTITY_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256={p:digest((ROOT/p).read_bytes())for p in paths},raw_bytes=len(raw),compressed_bytes=sum(map(len,parts)),parts=1,rejected_corruptions=rejected,scope='Exact artifact identity only; no new mathematical or satisfiability claim.',recovery_writes=0,artifact_availability='LOCAL_ONLY')
    (out/'summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(dict(status=report['status'],summary_sha256=digest((out/'summary.json').read_bytes()))))
if __name__=='__main__':main()
