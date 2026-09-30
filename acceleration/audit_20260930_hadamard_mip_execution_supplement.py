"""Append-only exact saved-record audit for the single completed MIP timeout.

No producer imports, no solver calls, and no mathematical infeasibility claim.
The frozen broader model/object audit remains separate and unchanged.
"""
import copy
import hashlib
import json
import math
import platform
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'acceleration/results/20260930_hadamard_prism_binary_mip_pilot'
OUT = ROOT / 'acceleration/results/20260930_independent_review/hadamard_prism_binary_mip_execution'
AUDIT = ROOT / 'acceleration/results/20260930_independent_review/hadamard_prism_binary_mip_pilot/summary.json'

def need(ok, message):
    if not ok:
        raise ValueError(message)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def save(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n', encoding='utf-8')

def check(summary, native, launch, log):
    need(summary['limits'] == dict(total_wall_seconds=120, maximum_research_calls=3, threads=1, random_seed=0, automatic_reset=False), 'frozen shared limits')
    need(summary['research_calls'] == 1 and len(summary['attempts']) == 1, 'single research call')
    attempt = summary['attempts'][0]
    need(attempt['index'] == 0 and attempt['integer_incumbent'] is False, 'no reported exact incumbent')
    need(summary['stop_reason'] == 'NO_VALID_NATIVE_INCUMBENT' and summary['saved_exact_Gram_incumbents'] == 0 and summary['distinct_lazy_cuts'] == 0 and summary['numerical_status_is_exclusion'] is False, 'no object/cut/exclusion')
    need(native['model_status'] == attempt['model_status'] == 'HighsModelStatus.kTimeLimit' and native['run_status'] == 'HighsStatus.kWarning' and native['solution_value_valid'] is False, 'native timeout and no valid solution')
    need(native['native_version'] == summary['versions']['highspy'] == '1.15.1', 'native version record')
    options = native['options']
    need(options['threads'] == 1 and options['random_seed'] == 0 and options['mip_feasibility_tolerance'] == 1e-7 and options['primal_feasibility_tolerance'] == 1e-7, 'frozen numerical settings')
    need(options['time_limit'] == launch['remaining_wall_seconds'] and 0 < options['time_limit'] <= 120 and launch['ordered_prior_cuts'] == [] and launch['reused_same_solver_instance'] is False, 'first call budget / no prior cuts')
    values, hexes = native['col_value'], native['col_value_float_hex']
    need(len(values) == len(hexes) == 5400, 'complete vector')
    need(all(type(v) in (int, float) and math.isfinite(v) and float(v).hex() == h for v, h in zip(values, hexes)), 'every native float/hex identity')
    need(native['info']['primal_solution_status'] == 0 and native['info']['mip_node_count'] == 0, 'no primal solution in info')
    need('MIP has 766 rows; 5400 cols; 125920 nonzeros; 5400 integer variables (5400 binary)' in log, 'literal original model dimensions')
    need(len(re.findall(r'^\s*Status\s+Time limit reached\s*$', log, re.M)) == 1 and re.search(r'^\s*Solution status\s+-\s*$', log, re.M), 'literal final log status')
    need(re.search(r'^\s*Primal bound\s+inf\s*$', log, re.M) and re.search(r'^\s*Nodes\s+0\s*$', log, re.M), 'literal no incumbent log')
    times = re.findall(r'^\s*Timing\s+(\d+\.\d+)\s*$', log, re.M)
    need(len(times) == 1 and float(times[0]) == native['wall_seconds'] == attempt['wall_seconds'] == 120.0, 'saved rounded call wall and log timing')
    need(native['highs_runtime_before'] == 0 and 120 <= native['highs_runtime_after'] < 121, 'native cumulative runtime record')
    need(summary['observed_total_wall_seconds'] == 120.25 and summary['cooperative_budget_overrun_seconds'] == summary['observed_total_wall_seconds'] - 120 == 0.25, 'explicit cooperative overrun')
    return dict(native_values_checked=5400, exact_float_hex_pairs_checked=5400, vector_all_zero=all(v == 0 for v in values), first_onehot_value=sum(values[:90]), first_onehot_required=1, original_rows=766, original_variables=5400, original_nonzeros=125920, research_calls=1, native_internal_sub_mips_not_counted_as_separate_research_calls=True, valid_native_incumbent=False, saved_Gram_objects=0, saved_lazy_cuts=0, native_log_time_seconds=120.0, native_cumulative_runtime_seconds=native['highs_runtime_after'], wrapper_wall_seconds=120.25, cooperative_overrun_seconds=0.25)

def main():
    OUT.mkdir(parents=True, exist_ok=False)
    pins = {}
    def pin(path, expected=None):
        value = sha(path)
        need(expected is None or value == expected, 'input hash ' + str(path))
        pins[path.relative_to(ROOT).as_posix()] = value
    try:
        pin(AUDIT, '9c13093a8c71959a59e9266ebf2c19c4e1bbe1ce1d5ef8b3c5698d87ac6914c1')
        pin(RUN/'summary.json', '081cce1e5126534eadd2a30d6813a85685b1f6caac052dabce71fe52c970635a')
        summary = read(RUN/'summary.json')
        for p,h in summary['outputs_sha256'].items():
            pin(ROOT/p, h)
        pin(RUN/'manifest.json')
        native, launch = read(RUN/'attempt_00/native_incumbent.json'), read(RUN/'attempt_00/launch.json')
        log = (RUN/'attempt_00/solver.log').read_text(encoding='utf-8')
        result = check(summary, native, launch, log)
        rejected = []
        for case in range(12):
            s,n,l,t = copy.deepcopy(summary),copy.deepcopy(native),copy.deepcopy(launch),log
            if case == 0: s['limits']['total_wall_seconds'] = 121
            elif case == 1: s['research_calls'] = 2
            elif case == 2: s['numerical_status_is_exclusion'] = True
            elif case == 3: n['solution_value_valid'] = True
            elif case == 4: n['col_value_float_hex'][0] = '0x1.0000000000000p+0'
            elif case == 5: n['col_value'][0] = True
            elif case == 6: n['col_value'].pop()
            elif case == 7: n['options']['threads'] = 2
            elif case == 8: l['reused_same_solver_instance'] = True
            elif case == 9: t = t.replace('Time limit reached', 'Infeasible')
            elif case == 10: t = t.replace('125920 nonzeros; 5400', '125921 nonzeros; 5400')
            else: s['cooperative_budget_overrun_seconds'] = 0
            try: check(s,n,l,t)
            except ValueError as e: rejected.append(dict(case=case, rejection=str(e)))
            else: raise ValueError('corrupt control accepted ' + str(case))
        save(OUT/'controls.json',dict(positive='Authentic completed timeout record; engineering control only.',rejected=rejected))
        command = "$p=Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^python(w)?\\.exe$' -and $_.CommandLine -like '*theory_20260930_hadamard_prism_binary_mip.py*' -and $_.CommandLine -like '*20260930_hadamard_prism_binary_mip_pilot*' }; @($p | Select-Object ProcessId,CommandLine) | ConvertTo-Json -Compress"
        ps = subprocess.run(['powershell','-NoProfile','-Command',command],capture_output=True,text=True,check=True)
        save(OUT/'process_observation.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),command=command,stdout=ps.stdout,stderr=ps.stderr,exit_code=ps.returncode,scope='Read-only Python processes matching exact producer basename and this output prefix only; not global research state.'))
        pin(Path(__file__)); pin(ROOT/'uv.lock'); pin(ROOT/'pyproject.toml')
        report = dict(status='INDEPENDENT_FIXED_SUPPORT_PRISM_BINARY_MIP_EXECUTION_SUPPLEMENT_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),verifier='/root/state_literature_audit',inputs_sha256=pins,result=result,corrupted_controls_rejected=len(rejected),artifact_availability='LOCAL_ONLY',producer_imports=False,solver_calls_by_this_audit=0,mathematical_claim_changes=False,target_resolution=False,limitations=['Saved-record authentication only, not an independent run of HiGHS.','Native model status and timing are engineering telemetry; no infeasibility, exhaustion, or target claim.','The cooperative 120-second allocation overran by the saved 0.25 seconds; no strict wall-deadline guarantee is asserted.','The 5,400 saved values are invalid as an incumbent; their first one-hot sum is independently reported only to prevent accidental promotion.','One fixed six-prism Hadamard coordinate support; no cyclic restriction or residual D.'],outputs_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in OUT.iterdir() if p.is_file()})
        save(OUT/'summary.json',report)
        print(json.dumps(dict(status=report['status'],sha256=sha(OUT/'summary.json'))))
    except BaseException as e:
        save(OUT/'failure.json',dict(error=repr(e)));raise

if __name__ == '__main__':
    main()
