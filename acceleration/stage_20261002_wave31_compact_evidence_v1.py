"""Stage an explicit compact milestone package; never stage large raw closures.

Availability labels remain LOCAL_ONLY until immutable publication is confirmed.
No compression, deletion, solver invocation or mathematical verification occurs.
"""
from pathlib import Path
import hashlib
import json
import subprocess
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
SOURCES=['audit_20261002_batch05_checkpoint_v1.py','audit_20261002_batch05_checkpoint_v1_spec.md',
 'audit_20261002_exact_eight_policy_v1.py','audit_20261002_exact_eight_policy_v2.py','audit_20261002_exact_eight_policy_v2_spec.md',
 'audit_20261002_policy_drat_core_v1.py','audit_20261002_policy_drat_core_v2.py','audit_20261002_linux_descendants_v1.py',
 'control_20261002_linux_descendants_v1.py','audit_20261002_order8_null_v1.py','audit_20261002_wave147_all_coefficients.py',
 'native_20261002_exact_eight_budget_v1.py','native_20261002_exact_eight_budget_v1_spec.md',
 'native_20261002_budget_single_v2.py','native_20261002_budget_single_v2_spec.md','audit_20261002_policy_single_v1.py','audit_20261002_policy_single_v1_spec.md',
 'prepare_20261002_unrestricted_native_plan_v1.py','register_20261002_wave31_claims_v1.py','register_20261002_wave31_claims_v2.py',
 'record_20261002_wave31_milestone_v1.py','stage_20261002_wave31_compact_evidence_v1.py',
 'theory_20261002_order8_marked_extension.py','theory_20261002_order8_marked_extension_v2.py',
 'theory_20261002_order8_marked_extension_v3.py','theory_20261002_order8_marked_extension_v4.py',
 'theory_20261002_order8_psd_cuts.py','theory_20261002_order8_exact_endpoint.py']
DIRS=['20261002_native_budget_controls_supervision01','20261002_native_budget_controls_supervision02',
 '20261002_native_budget_controls02','20261002_batch05_preflight01','20261002_batch05_preflight_supervision01',
 '20261002_batch05_native01','20261002_batch05_native_supervision01',
 '20261002_order8_marked_extension','20261002_order8_marked_extension_v2','20261002_order8_marked_extension_v3','20261002_order8_marked_extension_v4',
 '20261002_order8_marked_extension_supervisor','20261002_order8_marked_extension_supervisor_v2',
 '20261002_order8_marked_extension_supervisor_v3','20261002_order8_marked_extension_supervisor_v4','20261002_order8_marked_extension_supervisor_v5',
 '20261002_order8_psd_cuts','20261002_order8_psd_cuts_supervisor','20261002_order8_exact_endpoint','20261002_order8_exact_endpoint_supervisor',
 '20261002_order8_null_supervision01','20261002_wave147_all_coefficients','20261002_wave147_all_coefficients_supervisor',
 '20261002_wave31_registration01','20261002_wave31_registration02','20261002_wave31_registration_supervision01','20261002_wave31_registration_supervision02',
 '20261002_wave31_milestone01','20261002_wave31_milestone_supervision01','20261002_wave31_milestone_supervision02',
 '20261002_wave31_public_registry01','20261002_wave31_public_registry_supervision01',
 '20261002_unrestricted_native_plan01','20261002_unrestricted_plan_supervision01']
AUDITS=['batch05_checkpoint_identity01','batch05_proofs01','order8_null01','policy_driver_calibration01','policy_driver_calibration02',
 'linux_descendants_audit01','single_v2_calibration01']


def main():
    out=ROOT/'acceleration/results/20261002_wave31_compact_stage01'
    out.mkdir(parents=True,exist_ok=False)
    candidates=[ROOT/name for name in ['CLAIMS.yaml','README.md','ACTIVE_RESEARCH.md','docs/RESEARCH_MAP.md','docs/REPRODUCING.md',
     'docs/RESEARCH_20261002_THIRTYFIRST_WAVE.md','docs/DERIVATION_20261002_ORDER8_MARKED_ENDPOINT.md','docs/LITERATURE_20261002_STRUCTURAL_REFRESH.md',
     'acceleration/native_budget_env_v1/pyproject.toml','acceleration/native_budget_env_v1/uv.lock']]
    candidates += [ROOT/'acceleration'/name for name in SOURCES]
    dirs=[ROOT/'acceleration/results'/name for name in DIRS]
    dirs += [ROOT/'acceleration/results/20261002_independent_review'/name for name in AUDITS]
    for folder in dirs:
        if folder.is_dir():
            candidates.extend(p for p in folder.rglob('*') if p.is_file() and p.suffix in {'.json','.jsonl','.yaml','.gz','.md'})
    staged,omitted=[],[]
    for path in sorted(set(candidates)):
        if not path.is_file():
            omitted.append(dict(path=str(path),reason='Not present; not invented'))
            continue
        name=path.relative_to(ROOT).as_posix()
        if path.stat().st_size>8*1024**2:
            omitted.append(dict(path=name,reason='Large raw checking closure retained locally'))
            continue
        staged.append(dict(path=name,bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    for start in range(0,len(staged),100):
        subprocess.run(['git','add','--',*[r['path'] for r in staged[start:start+100]]],cwd=ROOT,check=True,capture_output=True)
    report=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        scope='Compact exact reports/sources/witness only; no full raw formula/proof closure publication claim.',
        stage_records=staged,omitted=omitted,staged_files=len(staged),staged_bytes=sum(r['bytes'] for r in staged),
        mathematics_replayed=False,artifact_availability_changed=False)
    (out/'manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8',newline='\n')
    subprocess.run(['git','add','--',(out/'manifest.json').relative_to(ROOT).as_posix()],cwd=ROOT,check=True,capture_output=True)
    print(json.dumps({k:report[k] for k in ['staged_files','staged_bytes','scope']}))


if __name__=='__main__':
    main()
