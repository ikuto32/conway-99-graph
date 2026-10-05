"""Create separate retry tooling; original frozen runner/resources remain intact."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    source=ROOT/'acceleration/run_20260930_eight_moment_pdhg.py'
    raw=source.read_bytes().decode('utf-8')
    raw=raw.replace("RESOURCE='acceleration/results/20260930_resume/eight_gpu_resource_preflight.json'", "RESOURCE='acceleration/results/20260930_resume/eight_gpu_retry_resource_preflight.json'\nLARGE_GATE='acceleration/results/20260930_independent_review/large_gpu_cpu_parity/summary.json'")
    old=" binary=confined(export['binary_path']);"
    new=" large=json.loads((ROOT/LARGE_GATE).read_bytes());assert large['status']=='INDEPENDENT_LARGE_READER_FULL_MOMENT_GPU_CPU_PARITY_PASS'\n for key,h in large['inputs_sha256'].items():assert digest(ROOT/key)==h\n bindings[LARGE_GATE]=digest(ROOT/LARGE_GATE)\n for key in ('acceleration/moment_pdhg_gpu_large.cu','acceleration/build/moment_pdhg_gpu_large.exe','acceleration/build_moment_pdhg_gpu_large.ps1'):\n  assert digest(ROOT/key)==large['inputs_sha256'][key];bindings[key]=digest(ROOT/key)\n bindings['docs/NEXT_20260930_EIGHT_GPU_RETRY.md']=digest(ROOT/'docs/NEXT_20260930_EIGHT_GPU_RETRY.md')\n binary=confined(export['binary_path']);"
    assert raw.count(old)==1;raw=raw.replace(old,new)
    raw=raw.replace("command=[str(ROOT/'acceleration/build/moment_pdhg_gpu.exe')", "command=[str(ROOT/'acceleration/build/moment_pdhg_gpu_large.exe')")
    raw=raw.replace("gates='Independent four-case CPU parity and eight fullmodel; no eight-model CPU trajectory parity asserted'", "gates='Independent large-reader guard delta, four-case CPU parity and eight fullmodel; no eight-model CPU trajectory parity asserted'")
    target=ROOT/'acceleration/run_20260930_eight_moment_pdhg_v2.py'
    with target.open('xb') as f:f.write(raw.encode('utf-8'))
    old=ROOT/'acceleration/record_20260930_eight_gpu_resources.py'
    new=ROOT/'acceleration/record_20260930_eight_gpu_retry_resources.py'
    raw=old.read_bytes().replace(b'eight_gpu_resource_preflight.json',b'eight_gpu_retry_resource_preflight.json')
    with new.open('xb') as f:f.write(raw)

if __name__=='__main__':main()
