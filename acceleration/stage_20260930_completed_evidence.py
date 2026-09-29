"""Stage the frozen second/third milestone evidence, excluding ongoing next waves."""
from datetime import datetime,timezone
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
def main():
    excluded=('box','matching_cap','closed28','degree_bound','weighted','block_bound','wave02','v2_worker','sat_seek')
    sources=[p for p in (ROOT/'acceleration').iterdir() if p.is_file() and '20260930' in p.name and not any(s in p.name for s in excluded)]
    sources += [ROOT/'acceleration/moment_pdhg_gpu_large.cu',ROOT/'acceleration/build_moment_pdhg_gpu_large.ps1']
    names=['20260930_eight_filtered_moments','20260930_eight_moment_pdhg','20260930_large_gpu_build','20260930_large_gpu_reader',
       '20260930_rook_free_internal_gram','20260930_rook_free_internal_independent_certificate','20260930_rook_free_internal_pilot','20260930_rook_free_internal_sat',
       '20260930_rook_gram_calibration','20260930_rook_gram_minimized','20260930_rook_sat_independent_proof','20260930_rook_sat_pilot','20260930_rook_sat_solver_calibration',
       '20260930_rook_window_sat','20260930_rook_lazy_wave01','20260930_rook_lazy_checker_controls','20260930_resume','20260930_second_packaging','20260930_third_packaging']
    paths=sources+[ROOT/'acceleration/results'/n for n in names]+[ROOT/'acceleration/environments/rook-sat']
    review=ROOT/'acceleration/results/20260930_independent_review'
    for p in review.iterdir():
        if p.name.startswith(('eight_','large_gpu','rook_original_gram','target_gram_support','minimized_gram','rook_lazy_wave01','rook_lazy_binding')):paths.append(p)
    paths += [ROOT/p for p in ['.gitignore','CLAIMS.yaml','ACTIVE_RESEARCH.md','README.md','docs/RESEARCH_MAP.md','docs/REPRODUCING.md','docs/local-artifacts.json','docs/AUDIT_20260930_EIGHT_MOMENT_NECESSITY.md','docs/DERIVATION_20260930_TARGET_GRAM_NOGOODS.md','docs/NEXT_20260930_EIGHT_GPU_RETRY.md','docs/RESEARCH_20260930_SECOND_WAVE.md','docs/RESEARCH_20260930_THIRD_WAVE.md','docs/REPRODUCING_20260930_SECOND_WAVE.md']]
    keys=sorted({p.relative_to(ROOT).as_posix() for p in paths if p.exists()})
    subprocess.run(['git','add','--',*keys],cwd=ROOT,check=True,capture_output=True)
    logs=[]
    for n in names:
        logs.extend(p.relative_to(ROOT).as_posix() for p in (ROOT/'acceleration/results'/n).rglob('*.log'))
    if logs:subprocess.run(['git','add','-f','--',*logs],cwd=ROOT,check=True,capture_output=True)
    staged=subprocess.check_output(['git','diff','--cached','--name-only'],cwd=ROOT,text=True).splitlines()
    oversized=[p for p in staged if (ROOT/p).is_file() and (ROOT/p).stat().st_size>10<<20]
    assert not oversized,oversized
    assert 'PROMPT.md' not in staged and 'tools/drat-trim' not in staged
    print(json.dumps(dict(timestamp=datetime.now(timezone.utc).isoformat(),staged_files=len(staged),staged_file_bytes=sum((ROOT/p).stat().st_size for p in staged if (ROOT/p).is_file()),oversized_files=oversized,explicit_log_files=len(logs),excluded_next_wave_patterns=excluded)))

if __name__=='__main__':main()
