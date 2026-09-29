"""Bind the completed independent large-reader engineering audit to one revision."""
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import json,platform,subprocess,sys

ROOT=Path(__file__).resolve().parents[1]
def digest(p):return sha256(Path(p).read_bytes()).hexdigest()
def main():
    path=ROOT/'acceleration/results/20260930_independent_review/large_gpu_cpu_parity/summary.json'
    assert digest(path)=='e71cee4a33b855a8986419ad6643e145e5ce4c8ebef083778e21a54700e25e48'
    audit=json.loads(path.read_bytes());assert audit['status']=='INDEPENDENT_LARGE_READER_FULL_MOMENT_GPU_CPU_PARITY_PASS'
    assert len(audit['records'])==4 and sum(len(r['checkpoints'])for r in audit['records'])==16 and len(audit['native_guard_controls'])==14
    assert all([c['iteration']for c in r['checkpoints']]==[1,2,10,100]for r in audit['records'])
    assert all(c['returncode']==2 and not c['timeout']for c in audit['native_guard_controls'])
    assert len(audit['guard_delta']['changes'])==4 and audit['guard_delta']['kernels_and_numerics_byte_preserved']
    bindings={path.relative_to(ROOT).as_posix():digest(path)}
    for p in[Path(__file__).resolve(),ROOT/'uv.lock',ROOT/'acceleration/results/20260930_large_gpu_reader/pilot/summary.json',ROOT/'acceleration/results/20260930_large_gpu_reader/pilot/source_delta.json',ROOT/'acceleration/results/20260930_independent_review/large_gpu_sparse_fixture_storage.json']:
        bindings[p.relative_to(ROOT).as_posix()]=digest(p)
    maximum_vector=max(v for r in audit['records']for c in r['checkpoints']for v in c['vector_absolute_Linf_errors'].values())
    maximum_scalar=max(v for r in audit['records']for c in r['checkpoints']for group in c['scalar_absolute_errors'].values()for v in group.values())
    assert maximum_vector<=1e-8 and maximum_scalar<=1e-7
    statement='The exact recorded large-reader CUDA source differs from the previously audited source only in four input/geometry guard literal replacements, and its recorded executable passes all 14 saved malformed/boundary controls. On each of the four frozen calibration inputs, its five saved state vectors at iterations 1, 2, 10 and 100 agree with the separate CPU reference within absolute Linf 1e-8, and the checked scalar diagnostics agree within 1e-7.'
    report=dict(status='INDEPENDENT_LARGE_GPU_CALIBRATION_CLAIM_BINDING_PASS',claim_id='C-GPU-LARGE-MOMENT-PDHG-CALIBRATION',claim_revision=1,recommendation='VERIFIED',review_state='CLEAR',verifier='/root/state_literature_audit independent checking agent',timestamp=datetime.now(timezone.utc).isoformat(),statement=statement,kind='empirical/engineering result',basis=['COMPUTED'],scope='Only the two pinned source/executable versions, 14 reader controls, and four inputs run for 100 iterations with 16 inspected case-checkpoints. No eight-coordinate numerical trajectory guarantee, performance claim, exact feasibility or mathematical exclusion.',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,source_sha256=audit['guard_delta']['source_sha256'],executable_sha256=audit['guard_delta']['binary_sha256'],dependencies=[dict(id='C-MOMENT-PDHG-GPU-CPU-PARITY',revision=1,relation='verification_dependency'),dict(id='C-PARTIAL-K-TWO-COORDINATE-FULL-MOMENT-ENCODING',revision=1,relation='verification_dependency')],counts=dict(guard_literal_replacements=4,native_controls=14,old_malformed_inputs=4,tiny_header_dimension_boundaries=8,sparse_file_length_boundaries=2,numerical_inputs=4,case_checkpoints=16,iterations_per_case=100),numerical_comparison=dict(vector_absolute_Linf_tolerance=1e-8,scalar_absolute_tolerance=1e-7,maximum_vector_error=maximum_vector,maximum_scalar_error=maximum_scalar,engineering_only=True),checking_method='Exact byte replacement delta; separate executable executions at rejection boundaries and four frozen inputs; independent binary parser and CPU update using sorted-threshold simplex projection; complete every-vector-entry and scalar comparisons at 16 case-checkpoints.',shared_components=audit['shared_components'],controls='Known uniform, unbounded hard dual, 45882-variable simplex, audited 89308-column two-coordinate model; malformed binaries, guard boundaries, and injected vector corruption.',limitations=audit['limitations']+['Aggregate geometry guards are reviewed in source; exactly-one-model parsing means a separate multi-model aggregate scenario is unreachable.','Sparse fixtures are LOCAL_ONLY under ignored build paths and have exact all-zero generation recipes; no whole-file hash is claimed. Storage allocation correction preserves their logical bytes.','The original pilot record integer_review used a strict word below where the exact cap is at most 2010131; the main audit explicitly records this editorial correction, retaining original evidence.'],unrestricted_target_resolution=False,external_review=False)
    out=ROOT/'acceleration/results/20260930_independent_review/large_gpu_calibration_claim_binding.json'
    with out.open('x')as f:json.dump(report,f,indent=2)
    print(report['status'],digest(out))
if __name__=='__main__':main()
