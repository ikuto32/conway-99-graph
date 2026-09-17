"""Gated one-process six-coordinate GPU pilot; retains every checkpoint/attempt."""
import argparse
from datetime import datetime,timezone
import gzip
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
from export_20260917_six_moment_pdhg import ROOT,MODEL,digest,save,confined,PROTOCOL

GATE='acceleration/results/20260917_independent_review/moment_pdhg_gpu_cpu_parity_v2/summary.json'
GATE_SHA='c0ae24550c1f33c1d808107f7aaa9bf49d83d968805f2691a26388b777e2aaf2'
EXPORT_GATE='acceleration/results/20260917_independent_review/six_gpu_export_verifier.json'
EXPORT_GATE_SHA='e9bef8db00a638de44546f3d03ae873312b693f76814127c8563a4dc345ae7d4'
EXPORT='acceleration/results/20260917_six_moment_pdhg/export/manifest.json'
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--validate-only',action='store_true');a=p.parse_args();out=confined(a.out)
 assert not out.exists();out.mkdir(parents=True)
 assert digest(ROOT/GATE)==GATE_SHA;gate=json.loads((ROOT/GATE).read_bytes());assert gate['status']=='INDEPENDENT_FULL_MOMENT_GPU_CPU_PARITY_PASS'
 export=json.loads((ROOT/EXPORT).read_bytes());bindings={GATE:GATE_SHA,EXPORT:digest(ROOT/EXPORT),EXPORT_GATE:EXPORT_GATE_SHA}
 assert digest(ROOT/EXPORT_GATE)==EXPORT_GATE_SHA;export_gate=json.loads((ROOT/EXPORT_GATE).read_bytes());assert export_gate['status']=='INDEPENDENT_SIX_COORDINATE_GPU_EXPORT_MAPPING_PASS'
 for key,h in export_gate['inputs_sha256'].items():assert digest(ROOT/key)==h
 assert export_gate['inputs_sha256'][EXPORT]==digest(ROOT/EXPORT)
 for key,h in export['inputs_sha256'].items():assert digest(ROOT/key)==h;bindings[key]=h
 for key in ('acceleration/moment_pdhg_gpu.cu','acceleration/build/moment_pdhg_gpu.exe'):
  assert digest(ROOT/key)==gate['inputs_sha256'][key]==bindings[key]
 binary=confined(export['binary_path']);assert digest(binary)==export['binary_sha256'];bindings[export['binary_path']]=export['binary_sha256']
 assert export['checkpoints']==[1000,5000,10000] and export['shape']==[5526,712721]
 for path in (Path(__file__),ROOT/'acceleration/certify_20260917_six_moment_pdhg.py',ROOT/PROTOCOL,ROOT/'docs/NEXT_20260917_SIX_MOMENT_PDHG_EXECUTION_GATE.md'):bindings[path.relative_to(ROOT).as_posix()]=digest(path)
 command=[str(ROOT/'acceleration/build/moment_pdhg_gpu.exe'),str(binary),str(out/'six')]
 manifest=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
  command=[sys.executable,*sys.argv],cwd=str(Path.cwd()),inputs_sha256=bindings,GPU_command=command,whole_process_wall_cap_seconds=300,
  gates='Independent four-case CPU parity and six fullmodel; no six-model CPU trajectory parity asserted',
  requested_checkpoints=[1000,5000,10000],support_attempts=6,validate_only=a.validate_only,GPU_launched=False)
 save(out/'manifest.json',manifest)
 if a.validate_only:
  save(out/'preflight.json',dict(status='SIX_MOMENT_GPU_PREFLIGHT_PASS',input_hashes_unchanged=True,GPU_launched=False));return
 start=time.monotonic();code=None;timeout=False
 with (out/'console.txt').open('x',encoding='utf-8') as f:
  try:code=subprocess.run(command,stdout=f,stderr=subprocess.STDOUT,timeout=300,check=False).returncode
  except subprocess.TimeoutExpired:timeout=True
 wall=time.monotonic()-start;summary=out/'six_summary.json';native=json.loads(summary.read_bytes()) if summary.exists() else None
 save(out/'receipt.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),command=command,returncode=code,timeout=timeout,process_wall_seconds=wall,
  gpu_event_compute_seconds=native['gpu_iteration_seconds'] if native else None,native_post_import_elapsed_seconds=native['elapsed_seconds'] if native else None,
  startup_import_shutdown_residual_seconds=wall-native['elapsed_seconds'] if native else None,
  timing_limitation='Residual includes startup/import/shutdown and is not a pure import measurement; no speedup or general performance claim',
  input_hashes_unchanged=all(digest(ROOT/key)==h for key,h in bindings.items()),completed_checkpoint_files=[p.name for p in sorted(out.glob('six_[0-9]*.json'))]))
 cert_command=[sys.executable,'-B',str(ROOT/'acceleration/certify_20260917_six_moment_pdhg.py'),'--out',str(out/'certificates'),'--checkpoints-dir',str(out)]
 cert=subprocess.run(cert_command,check=False);save(out/'certificate_receipt.json',dict(command=cert_command,returncode=cert.returncode))
 compressed=[];chunked=[]
 for path in sorted(out.glob('six_[0-9]*.json')):
  if path.stat().st_size<=8<<20:continue
  target=path.with_suffix('.json.gz')
  with path.open('rb') as src,target.open('xb') as dst:
   with gzip.GzipFile(fileobj=dst,mode='wb',filename='',mtime=0,compresslevel=9) as z:shutil.copyfileobj(src,z,1<<20)
  compressed.append(dict(path=path.relative_to(ROOT).as_posix(),size_bytes=path.stat().st_size,sha256=digest(path),compressed_path=target.relative_to(ROOT).as_posix(),compressed_size_bytes=target.stat().st_size,compressed_sha256=digest(target)))
  if target.stat().st_size>8<<20:
   parts=[]
   with target.open('rb') as f:
    while block:=f.read(8<<20):
     part=target.with_name(target.name+f'.part{len(parts):03d}')
     with part.open('xb') as w:w.write(block)
     parts.append(dict(path=part.name,bytes=len(block),sha256=digest(part)))
   chunked.append(dict(source=target.name,source_bytes=target.stat().st_size,source_sha256=digest(target),source_availability='LOCAL_ONLY',parts=parts))
 save(out/'compressed_artifacts.json',dict(schema_version=1,encoding='gzip; exact byte recovery',files=compressed))
 save(out/'chunk_manifest.json',dict(schema_version=1,chunk_bytes=8<<20,artifacts=chunked))
 save(out/'summary.json',dict(status='SIX_MOMENT_GPU_PILOT_EXECUTION_RECORDED',GPU_returncode=code,GPU_timeout=timeout,certificate_process_returncode=cert.returncode,
  output_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()},independent_support_check_pending=True,target_resolution=False))
if __name__=='__main__':main()
