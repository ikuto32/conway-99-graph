"""Bounded preregistered numerical pilot; preserves every process outcome."""
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import platform
import struct
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
EXPORT=ROOT/'acceleration/results/20260917_moment_pdhg_gpu/export'
OUT=ROOT/'acceleration/results/20260917_moment_pdhg_gpu/pilot'
EXE=ROOT/'acceleration/build/moment_pdhg_gpu.exe'
def digest(p):return sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):
 with p.open('x',encoding='utf-8') as f:json.dump(d,f,indent=2);f.write('\n')
def run(command,stem):
 started=time.monotonic();code=None;timeout=False
 with (OUT/(stem+'.console.txt')).open('x',encoding='utf-8') as f:
  try:code=subprocess.run(command,stdout=f,stderr=subprocess.STDOUT,timeout=120,check=False).returncode
  except subprocess.TimeoutExpired:timeout=True
 r=dict(command=command,returncode=code,timeout=timeout,elapsed_seconds=time.monotonic()-started)
 save(OUT/(stem+'.receipt.json'),r);return r
def main():
 assert not OUT.exists();OUT.mkdir(parents=True)
 manifest=json.loads((EXPORT/'manifest.json').read_bytes())
 for p,h in manifest['inputs_sha256'].items():assert digest(ROOT/p)==h,(p,'input changed')
 paths=[Path(__file__),EXE,EXPORT/'manifest.json',ROOT/'acceleration/moment_pdhg_gpu.cu',ROOT/'acceleration/build_moment_pdhg_gpu.ps1',ROOT/'uv.lock']
 bindings={p.relative_to(ROOT).as_posix():digest(p) for p in paths}
 for r in manifest['records'].values():assert digest(ROOT/r['path'])==r['sha256'];bindings[r['path']]=r['sha256']
 versions={}
 for name,cmd in [('nvcc',['nvcc','--version']),('gpu',['nvidia-smi','--query-gpu=name,driver_version,memory.total','--format=csv,noheader'])]:
  result=subprocess.run(cmd,capture_output=True,text=True,check=False);versions[name]=dict(command=cmd,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr)
 save(OUT/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
  command=[sys.executable,*sys.argv],cwd=str(Path.cwd()),python=platform.python_version(),inputs_sha256=bindings,versions=versions,
  build_command=['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File','acceleration/build_moment_pdhg_gpu.ps1'],
  build_observation='Previously completed with exit0; nvcc warned about host INFINITY macro narrowing; source initializes a double minimum to positive infinity. Build stdout was visible in tool transcript, not saved as an independent artifact.',
  protocol=manifest['inputs_sha256']['docs/NEXT_20260917_MOMENT_PDHG_GPU.md'],per_process_timeout_seconds=120))
 # Negative controls are exact mutations of the small positive input.
 original=(EXPORT/'positive_uniform.bin').read_bytes();rec=manifest['records']['positive_uniform'];mutations={}
 a=bytearray(original);a[0]=0;mutations['bad_magic']=a
 a=bytearray(original);struct.pack_into('<d',a,rec['arrays']['AT_values']['offset'],3.);mutations['bad_transpose']=a
 mutations['trailing_bytes']=original+b'x'
 a=bytearray(original);struct.pack_into('<I',a,rec['arrays']['offsets']['offset']+4,100001);mutations['domain_out_of_range']=a
 controls=[]
 for name,data in mutations.items():
  p=OUT/(name+'.bin');p.write_bytes(data);r=run([str(EXE),str(p),str(OUT/name)],name)
  r.update(name=name,input_sha256=digest(p),expected='nonzero exit and no output checkpoint',passed=r['returncode']==2 and not r['timeout'] and not (OUT/(name+'_1.json')).exists());controls.append(r)
 save(OUT/'controls.json',controls)
 if not all(r['passed'] for r in controls):raise RuntimeError('Parser control failed; no numeric launch')
 results={}
 for name in ('positive_uniform','unbounded_hard_dual','large_uniform','two_coordinate'):
  results[name]=run([str(EXE),str(EXPORT/(name+'.bin')),str(OUT/name)],name)
  print(json.dumps(dict(case=name,**results[name])),flush=True)
  if results[name]['returncode']!=0 or results[name]['timeout']:break
 save(OUT/'summary.json',dict(status='FULL_MOMENT_GPU_PILOT_EXECUTION_FINISHED',results=results,controls_passed=all(r['passed'] for r in controls),
  input_hashes_unchanged=all(digest(ROOT/p)==h for p,h in bindings.items()),output_sha256={p.name:digest(p) for p in OUT.iterdir() if p.is_file()},
  independent_CPU_parity='PENDING',mathematical_claim=False,six_coordinate_launched=False))
if __name__=='__main__':main()
