"""Preserve native v1; generate/build a guards-only large-input variant."""
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'acceleration/results/20260930_large_gpu_build'
def digest(p):return sha256(p.read_bytes()).hexdigest()
def main():
    OUT.mkdir(exist_ok=False)
    original=ROOT/'acceleration/moment_pdhg_gpu.cu';target=ROOT/'acceleration/moment_pdhg_gpu_large.cu'
    raw=original.read_bytes()
    changes=[(b'uint64_t(2)*1024*1024*1024,"Input exceeds2GiB limit"',b'uint64_t(8)*1024*1024*1024,"Input exceeds8GiB limit"'),
             (b'g.n<=1000000 ',b'g.n<=2000000 '),
             (b'g.nnz<=100000000,',b'g.nnz<=200000000,'),
             (b'total_nnz<=100000000,',b'total_nnz<=200000000,')]
    for before,after in changes:
        assert raw.count(before)==1
        raw=raw.replace(before,after)
    with target.open('xb') as f:f.write(raw)
    builder=ROOT/'acceleration/build_moment_pdhg_gpu.ps1';newbuilder=ROOT/'acceleration/build_moment_pdhg_gpu_large.ps1'
    raw=builder.read_bytes().replace(b'moment_pdhg_gpu.cu',b'moment_pdhg_gpu_large.cu').replace(b'build/moment_pdhg_gpu.exe',b'build/moment_pdhg_gpu_large.exe')
    with newbuilder.open('xb') as f:f.write(raw)
    manifest=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        command=[sys.executable,*sys.argv],cwd=str(Path.cwd()),question='Can explicitly bounded 8 GiB / 2 million variable / 200 million nonzero guards admit the audited eight-coordinate model without any numerical code changes?',
        selection='Guard literals only; all kernels, parser array types, exact-transpose checks and numerical acceptance tolerances byte-preserved.',
        resource_cap_seconds=120,independent_parity_required_before_research_run=True,
        changes=[dict(before=a.decode(),after=b.decode()) for a,b in changes],
        input_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in [original,builder,Path(__file__)]},
        generated_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in [target,newbuilder]})
    (OUT/'preregistration.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    command=['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',str(newbuilder)]
    start=time.monotonic();run=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=120)
    (OUT/'build_stdout.txt').write_text(run.stdout,encoding='utf-8');(OUT/'build_stderr.txt').write_text(run.stderr,encoding='utf-8')
    exe=ROOT/'acceleration/build/moment_pdhg_gpu_large.exe'
    receipt=dict(timestamp=datetime.now(timezone.utc).isoformat(),command=command,returncode=run.returncode,elapsed_seconds=time.monotonic()-start,
        nvcc_version=subprocess.check_output(['nvcc','--version'],text=True),
        source_sha256=digest(target),binary_sha256=digest(exe) if exe.exists() else None,
        original_unchanged=all(digest(ROOT/p)==v for p,v in manifest['input_sha256'].items()))
    (OUT/'receipt.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    assert run.returncode==0 and receipt['original_unchanged']
    print(json.dumps(receipt))

if __name__=='__main__':main()
