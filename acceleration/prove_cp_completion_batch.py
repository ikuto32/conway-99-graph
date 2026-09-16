"""Prove only fully recorded UNSAT candidates from an exact-audited CP batch."""
import argparse
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
PINS = {'run_fixed_overlap_drat.py': '34467f38986d885eee17febc92df50f3e86c09c022d9aa435b599ca558fb6732',
        'audit_fixed_overlap_drat.py': 'b965e6146a5ff6f811e22a16a4ef7fbdedf696c5c692f31dc399a168a89045d5'}
QA = ROOT/'acceleration/results/20260916_fixed_overlap_drat_controls_v2/report.json'
QA_SHA = '63140f757ea6d410eea72e9ae4502c40e0628edbaaf9b57e5e6c4e5df89221f9'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def resolve(name):
    p = Path(str(name).replace('\\', '/'))
    return p.resolve() if p.is_absolute() else (ROOT/p).resolve()


def key(name):
    return resolve(name).relative_to(ROOT).as_posix()


def digest(name):
    h = sha256()
    with resolve(name).open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def fraction(row):
    return Fraction(int(row['numerator']), int(row['denominator']))


def save(name, value):
    with resolve(name).open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(value, indent=2, allow_nan=False)+'\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--completion', type=Path, required=True)
    parser.add_argument('--expected-count', type=int, required=True)
    args = parser.parse_args()
    directory = resolve(args.completion)
    require(sys.version_info[:2] == (3, 12), 'Use .venv Python3.12')
    require(not (directory/'drat_batch_manifest.json').exists() and not (directory/'drat_batch_summary.json').exists(), 'Preserve prior batch')
    inputs = {}
    def bind(path, expected=None):
        name = key(path)
        if name not in inputs:
            inputs[name] = digest(path)
        require(expected is None or inputs[name] == expected, 'Changed input: '+name)
        return inputs[name]
    def read(path, status=None):
        bind(path)
        obj = json.loads(resolve(path).read_bytes())
        require(status is None or obj['status'] == status, 'Wrong status: '+str(path))
        return obj
    summary = read(directory/'summary.json', 'BOUNDED_CP_COMPLETION_INVESTIGATIONS_FINISHED')
    manifest = read(directory/'manifest.json', 'CP_COMPLETION_INVESTIGATION_MANIFEST')
    require(resolve(summary['manifest_path']) == directory/'manifest.json' and summary['manifest_sha256'] == bind(directory/'manifest.json'), 'Wrong completion manifest')
    require(summary['inputs_sha256'] == manifest['inputs_sha256'], 'Completion input maps differ')
    for path, expected in manifest['inputs_sha256'].items():
        bind(path, expected)
    run = resolve(manifest['search_directory'])
    search = read(run/'summary.json', 'BOUNDED_CP_MATCHING_SEARCH_FINISHED')
    audit = read(run/'audit.json')
    require(audit['status'] in ('INDEPENDENT_CP_MATCHING_SEARCH_AUDIT_PASS', 'INDEPENDENT_CP_CROSS_SEARCH_AUDIT_PASS'), 'Search audit absent')
    declared = {key(p): h for p,h in audit['inputs_sha256'].items()}
    require(declared.get(key(run/'summary.json')) == bind(run/'summary.json'), 'Search/audit association differs')
    for p,h in declared.items():
        bind(p,h)
    rows = {r['proposal_index']: r for r in search['records']}
    reports = {r['proposal_index']: r for r in audit['probe_reports']}
    require(len(rows) == len(reports) == len(audit['probe_reports']) == search['probes'] == audit['actual_LP_exact_intervals_checked'] and set(rows) == set(reports), 'Incomplete/duplicate CP audit records')
    selected = []
    for index, report in reports.items():
        exact = report['phase1_audit']; row = rows[index]
        lo, hi = fraction(exact['exact_dual_lower_bound']), fraction(exact['exact_primal_upper_bound'])
        if lo <= 0 and 0 <= hi <= Fraction(1,100000000):
            for stem in ('candidate', 'result'):
                require(declared.get(key(row[stem+'_path'])) == bind(row[stem+'_path'], row[stem+'_sha256']), 'Selected LP artifact unbound')
            selected.append(dict(proposal_index=index, candidate_path=key(row['candidate_path']), candidate_sha256=row['candidate_sha256'],
                                 phase1_path=key(row['result_path']), phase1_sha256=row['result_sha256'], exact_interval=exact))
    selected.sort(key=lambda r: (fraction(r['exact_interval']['exact_primal_upper_bound']), r['proposal_index']))
    require(len(selected) == args.expected_count == manifest['eligible_candidates'] and selected == manifest['selected_candidates'], 'Exact expected candidate inventory differs')
    require(len(summary['completed']) == args.expected_count and [r['proposal_index'] for r in summary['completed']] == [r['proposal_index'] for r in selected], 'Completion batch is incomplete or reordered')
    records = []
    for row, result_row in zip(selected, summary['completed']):
        index = row['proposal_index']; base = directory/f'index_{index}'; cnf = base/'cnf'
        require(not (base/'drat').exists(), 'Proof directory already exists')
        require(result_row['candidate_path'] == row['candidate_path'] and result_row['candidate_sha256'] == row['candidate_sha256'], 'Completed SAT candidate differs')
        require(resolve(result_row['result_path']) == base/'sat/result.json', 'Wrong SAT result path')
        sat = read(result_row['result_path']); bind(result_row['result_path'], result_row['result_sha256'])
        require(sat['status'] == result_row['status'] and sat['validated_witness'] == result_row['validated_witness'], 'SAT outcome differs')
        made = read(cnf/'manifest.json', 'FIXED_OVERLAP_CNF_ADAPTER_COMPLETE')
        mapped = read(cnf/'independent_audit.json', 'INDEPENDENT_FIXED_OVERLAP_CNF_MAPPING_AUDIT_PASS')
        require(made['candidate_path'] == row['candidate_path'] and made['candidate_sha256'] == row['candidate_sha256'], 'CNF is for another candidate')
        require(resolve(sat['manifest_path']) == cnf/'manifest.json' and sat['manifest_sha256'] == bind(cnf/'manifest.json') and
                resolve(sat['audit_path']) == cnf/'independent_audit.json' and sat['audit_sha256'] == bind(cnf/'independent_audit.json'), 'SAT/CNF/audit linkage differs')
        for obj in (made, mapped, sat):
            for p,h in obj['inputs_sha256'].items():
                bind(p,h)
        bind(made['cnf_path'], made['cnf_sha256'])
        records.append(dict(**row, prior_sat_status=sat['status'], prior_sat_result_path=result_row['result_path'],
                            prior_sat_result_sha256=result_row['result_sha256'], cnf_manifest_path=key(cnf/'manifest.json'),
                            cnf_manifest_sha256=bind(cnf/'manifest.json'), cnf_audit_path=key(cnf/'independent_audit.json'),
                            cnf_audit_sha256=bind(cnf/'independent_audit.json'), cnf_path=made['cnf_path'], cnf_sha256=made['cnf_sha256']))
    qa = read(QA, 'FIXED_OVERLAP_DRAT_TINY_PROOF_AND_CAP_CONTROLS_PASS'); bind(QA, QA_SHA)
    for p,h in qa['inputs_sha256'].items():
        bind(p,h)
    for name,h in PINS.items():
        bind(ROOT/'acceleration'/name,h)
    bind(Path(__file__))
    batch_manifest = dict(status='EXACT_CP_COMPLETION_DRAT_BATCH_MANIFEST', inputs_sha256=inputs,
                          completion_summary_path=key(directory/'summary.json'), completion_summary_sha256=bind(directory/'summary.json'),
                          search_audit_path=key(run/'audit.json'), search_audit_sha256=bind(run/'audit.json'), records=records,
                          expected_candidates=args.expected_count, solver_conflicts=200000, solver_seconds=60, checker_seconds=60,
                          selection_reconstructed_from_exact_audit=True, ordinary_SAT_reruns=0,
                          scope='Only prior UNSAT_UNVERIFIED results receive proof-generating reruns; all other outcomes remain unresolved.')
    save(directory/'drat_batch_manifest.json', batch_manifest)
    started = time.perf_counter(); completed = []; outputs = {}
    def execute(script, argv, log):
        with log.open('x', encoding='utf-8') as stream:
            process = subprocess.run([sys.executable, '-B', str(ROOT/'acceleration'/script)]+argv, cwd=ROOT,
                                     stdout=stream, stderr=subprocess.STDOUT, check=False, timeout=85)
        outputs[key(log)] = digest(log)
        require(process.returncode == 0, script+' failed; inspect '+key(log))
    try:
        for row in records:
            index = row['proposal_index']; base = directory/f'index_{index}'; out = base/'drat'
            if row['prior_sat_status'] != 'UNSAT_UNVERIFIED':
                completed.append(dict(proposal_index=index, status='SKIPPED_NON_UNSAT', prior_sat_status=row['prior_sat_status']))
                continue
            execute('run_fixed_overlap_drat.py', ['--manifest', row['cnf_manifest_path'], '--audit', row['cnf_audit_path'],
                    '--out', key(out), '--conflicts', '200000', '--seconds', '60'], base/'04_proof_generation.log')
            produced = json.loads((out/'proof_generation.json').read_bytes())
            record = dict(proposal_index=index, candidate_path=row['candidate_path'], candidate_sha256=row['candidate_sha256'],
                          generation_path=key(out/'proof_generation.json'), generation_sha256=digest(out/'proof_generation.json'),
                          status=produced['status'], verified=False)
            require(produced['candidate_sha256'] == row['candidate_sha256'] and produced['cnf_sha256'] == row['cnf_sha256'], 'Proof producer switched candidate/CNF')
            if produced['status'] == 'UNSAT_PROOF_UNCHECKED':
                execute('audit_fixed_overlap_drat.py', ['--manifest', row['cnf_manifest_path'], '--audit', row['cnf_audit_path'],
                        '--proof', key(out/'proof.drat'), '--out', key(out/'independent_drat_audit.json'), '--seconds', '60'], base/'05_drat_audit.log')
                checked = json.loads((out/'independent_drat_audit.json').read_bytes())
                require(checked['candidate_sha256'] == row['candidate_sha256'] and checked['cnf_sha256'] == row['cnf_sha256'] and
                        checked['proof_sha256'] == produced['proof_sha256'], 'Checked proof candidate/CNF/log differs')
                record.update(status=checked['status'], verified=checked['verified'], proof_path=produced['proof_path'],
                              proof_sha256=produced['proof_sha256'], audit_path=key(out/'independent_drat_audit.json'),
                              audit_sha256=digest(out/'independent_drat_audit.json'))
            for path in out.iterdir():
                if path.is_file():
                    outputs[key(path)] = digest(path)
            completed.append(record)
            print(json.dumps(record), flush=True)
        require(all(digest(p) == h for p,h in inputs.items()), 'Batch input/source changed')
        summary = dict(status='BOUNDED_CP_COMPLETION_DRAT_BATCH_FINISHED', inputs_sha256=inputs, outputs_sha256=outputs,
                       manifest_path=key(directory/'drat_batch_manifest.json'), manifest_sha256=digest(directory/'drat_batch_manifest.json'),
                       expected_candidates=args.expected_count, records=completed,
                       fixed_K_DRAT_verified=sum(r.get('verified',False) for r in completed),
                       unresolved_candidates=sum(not r.get('verified',False) for r in completed),
                       elapsed_seconds=time.perf_counter()-started, graph_constructed=False, general_nonexistence_proved=False,
                       scope='Individual labeled fixed-K exclusions relative to frozen unrestricted CNF; no global coverage or exact LP feasibility claim.')
        save(directory/'drat_batch_summary.json', summary)
    except BaseException as exc:
        save(directory/'drat_batch_failure.json', dict(status='CP_COMPLETION_DRAT_BATCH_STOPPED', records=completed,
                                                     error_type=type(exc).__name__, message=str(exc)))
        raise


if __name__ == '__main__':
    main()
