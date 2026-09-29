"""Independent guard-delta and executable boundary/pilot checks before CPU parity."""
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import ctypes,json,msvcrt,platform,struct,subprocess,sys,time
import audit_20260917_partial_matching as h

ROOT=h.ROOT
OUT=ROOT/'acceleration/results/20260930_large_gpu_reader/pilot'
OLD=ROOT/'acceleration/results/20260917_moment_pdhg_gpu'
EXE=ROOT/'acceleration/build/moment_pdhg_gpu_large.exe'

def stamp():return datetime.now(timezone.utc).isoformat()
def digest(path):
    v=sha256()
    with Path(path).open('rb')as f:
        while b:=f.read(8<<20):v.update(b)
    return v.hexdigest()
def save(path,value):
    with path.open('x')as f:json.dump(value,f,indent=2)

def main():
    OUT.mkdir(parents=True,exist_ok=False);started=time.monotonic();bindings={}
    def read(path):bindings[h.key(path)]=digest(path);return json.loads(path.read_bytes())
    for p in(__file__,h.__file__,ROOT/'uv.lock',EXE,ROOT/'acceleration/moment_pdhg_gpu_large.cu',ROOT/'acceleration/build_moment_pdhg_gpu_large.ps1'):
        bindings[h.key(p)]=digest(p)
    prereg=dict(timestamp=stamp(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),question='Does the new executable differ only in four guard literals and preserve all four 100-iteration calibration cases?',selection='Four original full pilot inputs; four corrupt old inputs; below/at/above new geometry guards; exact sparse file-size boundaries.',scope='Engineering source/reader/pilot audit only; no general trajectory guarantee or mathematical certificate.',per_process_wall_cap_seconds=120,whole_pilot_wall_cap_seconds=300,numerical_tolerances='Separate subsequent CPU parity: vector absolute Linf 1e-8, scalar absolute 1e-7; frozen original values.',inputs_sha256=dict(bindings))
    save(OUT/'preregistration.json',prereg)
    previous=read(ROOT/'acceleration/results/20260917_independent_review/moment_pdhg_gpu_cpu_parity_v2/summary.json')
    h.require(bindings[h.key(ROOT/'acceleration/results/20260917_independent_review/moment_pdhg_gpu_cpu_parity_v2/summary.json')]=='c0ae24550c1f33c1d808107f7aaa9bf49d83d968805f2691a26388b777e2aaf2','old parity identity')
    source=ROOT/'acceleration/moment_pdhg_gpu.cu';bindings[h.key(source)]=digest(source)
    h.require(bindings[h.key(source)]==previous['inputs_sha256'][h.key(source)],'original source unchanged')
    original=source.read_bytes();expected=original
    changes=[(b'uint64_t(2)*1024*1024*1024,"Input exceeds2GiB limit"',b'uint64_t(8)*1024*1024*1024,"Input exceeds8GiB limit"'),(b'g.n<=1000000 ',b'g.n<=2000000 '),(b'g.nnz<=100000000,',b'g.nnz<=200000000,'),(b'total_nnz<=100000000,',b'total_nnz<=200000000,')]
    for a,b in changes:h.require(expected.count(a)==1,'unique literal delta');expected=expected.replace(a,b)
    h.require(expected==(ROOT/'acceleration/moment_pdhg_gpu_large.cu').read_bytes(),'only guard literals changed, including all kernels and arithmetic')
    oldbuild=ROOT/'acceleration/build_moment_pdhg_gpu.ps1';bindings[h.key(oldbuild)]=digest(oldbuild)
    h.require(oldbuild.read_bytes().replace(b'moment_pdhg_gpu.cu',b'moment_pdhg_gpu_large.cu').replace(b'moment_pdhg_gpu.exe',b'moment_pdhg_gpu_large.exe')==(ROOT/'acceleration/build_moment_pdhg_gpu_large.ps1').read_bytes(),'only build input/output names changed')
    receipt=read(ROOT/'acceleration/results/20260930_large_gpu_build/receipt.json')
    h.require(receipt['returncode']==0 and receipt['source_sha256']==bindings['acceleration/moment_pdhg_gpu_large.cu'] and receipt['binary_sha256']==bindings[h.key(EXE)],'recorded build/source/binary binding')
    delta=dict(status='INDEPENDENT_EXACT_GUARD_ONLY_SOURCE_DELTA_PASS',changes=[dict(before=a.decode(),after=b.decode())for a,b in changes],kernels_and_numerics_byte_preserved=True,source_sha256=bindings['acceleration/moment_pdhg_gpu_large.cu'],binary_sha256=bindings[h.key(EXE)],integer_review='Reader lengths and aggregate sums are uint64_t; required geometry explicitly widens products. At new caps all unsigned indices and row-pointer values remain below 2^32; n+m+blocks+3 is below 2010131. Windows x64 size_t/streamsize hold 8 GiB, as also exercised by sparse boundary inputs.',aggregate_guard_scope='Exactly one model is accepted. Per-model new n and nnz caps imply unchanged aggregate n and changed aggregate nnz caps; multi-model aggregate behavior is unreachable and not dynamically claimed.')
    save(OUT/'source_delta.json',delta)
    manifest=read(OLD/'export/manifest.json')
    for rec in manifest['records'].values():h.require(digest(ROOT/rec['path'])==rec['sha256'],'frozen calibration artifact');bindings[rec['path']]=rec['sha256']
    versions={}
    for name,cmd in [('nvcc',['nvcc','--version']),('gpu',['nvidia-smi','--query-gpu=name,driver_version,memory.total','--format=csv,noheader'])]:
        r=subprocess.run(cmd,capture_output=True,text=True,check=False);versions[name]=dict(command=cmd,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr)
    save(OUT/'manifest.json',dict(timestamp=stamp(),source_commit=prereg['source_commit'],command=prereg['command'],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=dict(bindings),versions=versions,independent_CPU_parity='PENDING',source_delta=h.key(OUT/'source_delta.json')))
    def run(path,name,error=None):
        h.require(time.monotonic()-started<300,'whole pilot cap')
        t=time.monotonic();command=[str(EXE),str(path),str(OUT/name)];timeout=False;code=None
        with(OUT/(name+'.console.txt')).open('x')as f:
            try:code=subprocess.run(command,stdout=f,stderr=subprocess.STDOUT,timeout=120,check=False).returncode
            except subprocess.TimeoutExpired:timeout=True
        console=(OUT/(name+'.console.txt')).read_text()
        record=dict(command=command,returncode=code,timeout=timeout,elapsed_seconds=time.monotonic()-t,expected_error=error,observed_console=console)
        save(OUT/(name+'.receipt.json'),record)
        h.require(not timeout and code==(2 if error else 0),'native outcome')
        if error:h.require(error in console and not list(OUT.glob(name+'_*.json')),'exact rejection and no checkpoints')
        print(json.dumps(dict(case=name,returncode=code,expected_error=error)),flush=True)
        return record
    controls=[]
    errors={'bad_magic':'Bad moment binary magic','bad_transpose':'AT is not the exact transpose of A','trailing_bytes':'Trailing bytes','domain_out_of_range':'Invalid domain offsets'}
    for name,error in errors.items():
        old=OLD/'pilot'/f'{name}.bin';bindings[h.key(old)]=digest(old);path=OUT/f'{name}.bin';path.write_bytes(old.read_bytes());controls.append(dict(name=name,**run(path,name,error)))
    # Only 40 bytes; dimension acceptance is distinguished from the subsequent
    # required-byte guard before any large allocation or numerical execution.
    for axis,values in [('n',[1000001,1999999,2000000,2000001]),('nnz',[100000001,199999999,200000000,200000001])]:
        for value in values:
            n=value if axis=='n'else 1;nnz=value if axis=='nnz'else 0
            path=OUT/f'{axis}_{value}.bin';path.write_bytes(b'C99MHP01'+struct.pack('<8I',1,1,1,n,1,1,1,nnz))
            limit=2000000 if axis=='n'else 200000000;error='Unsupported candidate dimensions'if value>limit else'Truncated candidate geometry'
            controls.append(dict(name=path.stem,header_only=True,**run(path,path.stem,error)))
    # Sparse zero fixtures exercise actual 64-bit file sizes without allocating
    # 16 GiB of disk. The all-zero recipe is exact; only file length and the first
    # eight bytes are consumed, so no full-file hash is claimed.
    local=ROOT/'build/research-local/large_gpu_reader_boundary';local.mkdir(parents=True,exist_ok=False)
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    ioctl=kernel.DeviceIoControl;ioctl.argtypes=[ctypes.c_void_p,ctypes.c_uint32,ctypes.c_void_p,ctypes.c_uint32,ctypes.c_void_p,ctypes.c_uint32,ctypes.POINTER(ctypes.c_uint32),ctypes.c_void_p];ioctl.restype=ctypes.c_int
    for size in(8*1024**3,8*1024**3+1):
        path=local/f'zeros_{size}.bin'
        with path.open('xb')as f:
            returned=ctypes.c_uint32();h.require(ioctl(msvcrt.get_osfhandle(f.fileno()),0x900c4,None,0,None,0,ctypes.byref(returned),None)!=0,'mark exact fixture sparse');f.truncate(size)
        h.require(path.stat().st_size==size and path.open('rb').read(8)==bytes(8),'sparse fixture size/prefix')
        error='Bad moment binary magic'if size==8*1024**3 else'Input exceeds8GiB limit'
        controls.append(dict(name=path.stem,path=h.key(path),logical_bytes=size,artifact_availability='LOCAL_ONLY',retrieval='Rerun this checker to create a Windows sparse file of the stated logical length containing only zero bytes.',sha256=None,sha256_reason='Only length and eight-byte zero prefix are read by the exercised rejection branch; full 8 GiB hash intentionally not computed.',**run(path,path.stem,error)))
    save(OUT/'controls.json',controls)
    results={}
    for name in('positive_uniform','unbounded_hard_dual','large_uniform','two_coordinate'):
        results[name]=run(ROOT/manifest['records'][name]['path'],name)
    h.require(all(digest(ROOT/k)==v for k,v in bindings.items()),'stable frozen pilot inputs')
    save(OUT/'summary.json',dict(status='LARGE_READER_GPU_PILOT_EXECUTION_FINISHED',timestamp=stamp(),results=results,controls_passed=True,guard_controls=controls,source_delta=delta,inputs_sha256=bindings,input_hashes_unchanged=True,output_sha256={p.name:digest(p)for p in OUT.iterdir()if p.is_file()},independent_CPU_parity='PENDING',mathematical_claim=False,elapsed_seconds=time.monotonic()-started))
    print('LARGE_READER_GPU_PILOT_EXECUTION_FINISHED',digest(OUT/'summary.json'))

if __name__=='__main__':main()
