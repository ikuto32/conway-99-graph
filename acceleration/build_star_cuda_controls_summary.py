"""Bind the completed, bounded cold-star CUDA prototype controls; no reruns."""
from hashlib import sha256
import ast
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DIRECTORY=ROOT/'acceleration/results/20260916_star_cuda_controls'

def path(p):return (ROOT/str(p).replace('\\','/')).resolve()
def key(p):return path(p).relative_to(ROOT).as_posix()
def digest(p):
    h=sha256()
    with path(p).open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()
def require(ok,msg):
    if not ok:raise ValueError(msg)

def main():
    target=DIRECTORY/'summary.json';require(not target.exists(),'Preserve existing summary')
    bindings={}
    def bind(p,expected=None):
        name=key(p)
        if name not in bindings:bindings[name]=digest(p)
        require(expected is None or bindings[name]==expected,'Changed bound file '+name)
        return bindings[name]
    def load(p,status=None):
        bind(p);d=json.loads(path(p).read_bytes())
        require(status is None or d['status']==status,'Wrong control status '+key(p))
        for field in ('inputs_sha256','outputs_sha256'):
            for name,h in d.get(field,{}).items():bind(name,h)
        return d
    files=['export_star_pdhg_binary.py','review_star_pdhg_gpu.py','review_star_pdhg_gpu_controls.py','audit_star_gpu_quality14.py','build_star_cuda_controls_summary.py']
    for filename in files:
        p=ROOT/'acceleration'/filename;ast.parse(p.read_text(encoding='utf-8'));bind(p)
    source=ROOT/'acceleration/star_pdhg_gpu.cu';binary=ROOT/'acceleration/build/star_pdhg_gpu.exe'
    bind(source,'79593e296a4fba29882fb04b7e7dd88091dbc7f218135b6db2ba79c0b49002e8')
    bind(binary,'9dc3ea92ca53a6ebc8dd3715f5a0586ef00b18d5c8c8b7bd4e61cb6c2ae11075')
    bind(ROOT/'acceleration/build_star_pdhg_gpu.ps1','ca2b9f7117601b2e5d8e67fbfdab84d1604bf1a0b56fee36f021204a0895772b')
    bind(ROOT/'acceleration/STAR_PDHG_GPU_PROTOCOL.md','debbbb003c649bd895d4d9164512ad778b908452e4e53b50aa3f34b02d8ae96c')
    tiny=load(DIRECTORY/'tiny_parity.json','COLD_STAR_CUDA_CANONICAL_CPU_COMPONENTWISE_PARITY_PASS')
    real=load(DIRECTORY/'real2_parity.json','COLD_STAR_CUDA_CANONICAL_CPU_COMPONENTWISE_PARITY_PASS')
    negative=load(DIRECTORY/'negative_controls/report.json','INDEPENDENT_COLD_STAR_CUDA_PROJECTION_AND_CLI_CONTROLS_PASS')
    quality=load(DIRECTORY/'quality14_audit.json','COLD_STAR_CUDA_SAVED14_SCALAR_AND_RANK_PARITY_PASS')
    require(len(tiny['comparisons'])==12 and len(real['comparisons'])==10,'Missing parity checkpoints')
    require(tiny['max_vector_error']==0 and real['max_vector_error']==0,'Expected measured exact vector identity')
    require(negative['negative_control_count']==37 and negative['all_negative_controls_rejected'],'Missing CLI controls')
    require([r['size'] for r in negative['projection_checks']]==[3,1,2,1053,2049,8192],'Missing projection sizes')
    require(len(quality['records'])==14 and len(quality['metrics'])==6,'Missing saved14 comparison')
    for p in ('real2/manifest.json','quality14/manifest.json','tiny/manifest.json','real2_cpu/reference.json','tiny_cpu/reference.json'):
        load(DIRECTORY/p)
    load(DIRECTORY/'quality14_request.json')
    result=dict(status='COLD_STAR_CUDA_BOUNDED_PROTOTYPE_QA_PASS',inputs_sha256=bindings,
                native_source_path=key(source),native_source_sha256=digest(source),native_binary_path=key(binary),native_binary_sha256=digest(binary),
                protocol='C99SCP01 strict little-endian canonical CSR A/AT, cold uniform probabilities and zero duals',
                tiny_rational_models=4,tiny_checkpoints=[1,2,10],tiny_max_vector_error=tiny['max_vector_error'],tiny_max_scalar_error=tiny['max_scalar_error'],
                real_reference_candidates=[25496,26025],real_checkpoints=[1,2,10,500,2000],real_max_vector_error=real['max_vector_error'],real_max_scalar_error=real['max_scalar_error'],
                projection_checks=negative['projection_checks'],negative_CLI_controls=37,
                saved14_max_scalar_error=quality['max_scalar_error'],saved14_rank_metrics=quality['metrics'],saved14_gpu_timings=quality['gpu_timings'],
                timing_scope=quality['timing_scope'],all_source_syntax_checked=True,
                new_LP_runs=0,new_domain_enumerations=0,graph_constructed=False,new_exclusion_claims=0,
                limitations=['All numerical controls concern the listed models, not a proof of numerical convergence or global ranking quality.',
                             'CSR export canonicalizes row ordering; CPU parity references use those same exported bytes.',
                             'Maximum supported simplex size8192 is a parser/hardware limit, not a universal domain bound.',
                             'Native aggregate/input/vector-output limits remain authoritative; export only enforces its documented per-model limits.',
                             'The2GiB input and aggregate64million-nonzero caps were source-reviewed but not exercised with huge negative files.',
                             'All14 ranking observations were previously selected by CP and local gates; performance outside this sample is unmeasured.'])
    with target.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(dict(status=result['status'],bindings=len(bindings),summary_sha256=digest(target))))

if __name__=='__main__':main()
