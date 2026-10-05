"""Record a skipped numerical experiment after an exact cheaper exclusion."""
from datetime import datetime,timezone
from pathlib import Path
import hashlib,json,subprocess,sys
root=Path(__file__).resolve().parents[1]
paths=['acceleration/theory_20260930_balanced_lift_lp.py','acceleration/theory_20260930_balanced_lift_lp_spec.md',
       'acceleration/results/20260930_hadamard_parity_lift_cnf/exact_model.json',
       'acceleration/results/20260930_independent_review/balanced_lift_zero_rows/summary.json']
pins={p:hashlib.sha256((root/p).read_bytes()).hexdigest()for p in paths}
assert pins[paths[-1]]=='a6b7b5fd408e694b12cc630cf0e53e89542b1fe304f2f9d23d94735abe45af7f'
gate=json.loads((root/paths[-1]).read_bytes());assert gate['status']=='INDEPENDENT_SELECTED_PARITY_LIFT_ZERO_ROW_EXCLUSION_PASS'
out=root/'acceleration/results/20260930_balanced_lift_lp_not_run';out.mkdir(exist_ok=False)
record=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
    command=[sys.executable,*sys.argv],cwd=str(root),inputs_sha256=pins,status='SKIPPED_BEFORE_EXECUTION_EXACT_OBSTRUCTION',
    planned_research_calls=1,actual_research_calls=0,actual_control_solver_calls=0,actual_solver_command=None,
    actual_solver_command_null_reason='The prepared LP source was never invoked; no numeric solver was needed after independent exact zero-row exclusion.',
    reason='The complete selected branch has six required Gram rows with all-zero coefficients and RHS one. The independent exact certificate supersedes the planned numerical screen.',
    scope='Only this first selected parity branch; other parity assignments remain open.',
    source_retained=True,mathematical_verification_performed_by_this_recorder=False,target_resolution='UNKNOWN')
with(out/'summary.json').open('x',encoding='utf-8',newline='\n')as stream:json.dump(record,stream,indent=2);stream.write('\n')
print(json.dumps(dict(status=record['status'],actual_research_calls=0)))
