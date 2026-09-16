"""Bounded fixed-K SAT investigations selected from independently audited CP LPs.

Small exact LP upper bounds select candidates only. They are not feasibility
proofs. UNSAT here remains unverified; separate DRAT checking is required.
"""
import argparse
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    'fixed_overlap_cnf.py': 'e1edda9d43d2a2ea81209946960fae51aef1e7f547654b43569cc6d9a1bf8273',
    'audit_fixed_overlap_cnf.py': '2ba50a152f417e8647ccc738d609bcd689e73d8988053cf9d0c64ddfb4a0bc08',
    'run_fixed_overlap_sat.py': '68a6bf158e4a1be6e02df521e910ce5385029b932bd6d66245bbabfbb23fc5df',
}


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


def save(path, value):
    with resolve(path).open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(value, indent=2, allow_nan=False)+'\n')


def rational(value):
    return Fraction(int(value['numerator']), int(value['denominator']))


def preflight(args):
    require(sys.version_info[:2] == (3, 12), 'Use .venv/Scripts/python.exe')
    out, run = resolve(args.out), resolve(args.run)
    require(out.is_relative_to(ROOT) and not out.exists(), 'Use a fresh workspace output directory')
    require(1 <= args.max_candidates <= 64 and 0 < args.conflicts <= 2**31-1 and
            0 < args.seconds <= 3600, 'Invalid finite investigation limits')
    inputs = {}
    def bind(name, expected=None):
        label = key(name)
        value = inputs.setdefault(label, digest(name))
        require(expected is None or value == expected, 'Changed input: '+label)
        return value
    for name, expected in PINS.items():
        bind(ROOT/'acceleration'/name, expected)
    bind(Path(__file__))
    summary_path, audit_path = run/'summary.json', run/'audit.json'
    summary, audit = [json.loads(p.read_bytes()) for p in (summary_path, audit_path)]
    require(summary['status'] == 'BOUNDED_CP_MATCHING_SEARCH_FINISHED' and audit['status'] in
            ('INDEPENDENT_CP_MATCHING_SEARCH_AUDIT_PASS', 'INDEPENDENT_CP_CROSS_SEARCH_AUDIT_PASS'),
            'Expected independently audited CP search')
    declared = {key(p): h for p, h in audit['inputs_sha256'].items()}
    require(declared.get(key(summary_path)) == bind(summary_path), 'Audit/summary association differs')
    for name, expected in declared.items():
        bind(name, expected)
    bind(audit_path)
    rows = {r['proposal_index']: r for r in summary['records']}
    require(len(rows) == len(summary['records']) == summary['probes'] == audit['actual_LP_exact_intervals_checked'],
            'Wrong or duplicate LP records')
    eligible = []
    for report in audit['probe_reports']:
        row = rows[report['proposal_index']]
        lo = rational(report['phase1_audit']['exact_dual_lower_bound'])
        hi = rational(report['phase1_audit']['exact_primal_upper_bound'])
        if lo <= 0 and 0 <= hi <= Fraction(1, 100000000):
            for field in ('candidate', 'result'):
                require(declared.get(key(row[field+'_path'])) == row[field+'_sha256'], 'Unaudited selected artifact')
                bind(row[field+'_path'], row[field+'_sha256'])
            eligible.append(dict(proposal_index=row['proposal_index'], candidate_path=key(row['candidate_path']),
                                 candidate_sha256=row['candidate_sha256'], phase1_path=key(row['result_path']),
                                 phase1_sha256=row['result_sha256'], exact_interval=report['phase1_audit']))
    eligible.sort(key=lambda r: (rational(r['exact_interval']['exact_primal_upper_bound']), r['proposal_index']))
    require(eligible, 'No eligible nonpositive-lower-bound candidate')
    selected = eligible[:args.max_candidates]
    return dict(status='CP_COMPLETION_INVESTIGATION_MANIFEST', inputs_sha256=inputs,
                search_directory=key(run), eligible_candidates=len(eligible), selected_candidates=selected,
                conflict_budget=args.conflicts, solver_wall_seconds=args.seconds,
                selection_rule='Exact LP lower <=0 and upper <=1/100000000, then exact upper/index order',
                exact_LP_feasibility_claimed=False, graph_constructed=False, general_nonexistence_proved=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--max-candidates', type=int, default=9)
    parser.add_argument('--conflicts', type=int, default=200000)
    parser.add_argument('--seconds', type=float, default=60)
    parser.add_argument('--validate-only', action='store_true')
    args = parser.parse_args()
    manifest = preflight(args)
    if args.validate_only:
        print(json.dumps(dict(status='CP_COMPLETION_READ_ONLY_PREFLIGHT_PASS',
                              eligible=manifest['eligible_candidates'], selected=len(manifest['selected_candidates']),
                              output_created=False, processes_launched=0)), flush=True)
        return
    out = resolve(args.out)
    out.mkdir(parents=True, exist_ok=False)
    save(out/'manifest.json', manifest)
    completed, steps = [], []
    started = time.perf_counter()
    active = None
    def execute(script, arguments, result_path, logfile):
        require(all(digest(p) == h for p, h in manifest['inputs_sha256'].items()), 'Input changed during investigation')
        begin = time.perf_counter()
        with logfile.open('x', encoding='utf-8') as stream:
            process = subprocess.run([sys.executable, '-B', str(ROOT/'acceleration'/script)] + arguments,
                                     cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, check=False)
        require(process.returncode == 0, script+' failed; inspect '+key(logfile))
        result = json.loads(result_path.read_bytes())
        steps.append(dict(stage=script, result_path=key(result_path), result_sha256=digest(result_path),
                          log_path=key(logfile), log_sha256=digest(logfile), elapsed_seconds=time.perf_counter()-begin))
        return result
    try:
        for row in manifest['selected_candidates']:
            active = row['proposal_index']
            directory = out/f'index_{active}'
            directory.mkdir()
            cnf, sat = directory/'cnf', directory/'sat'
            print(json.dumps(dict(proposal_index=active, event='START')), flush=True)
            made = execute('fixed_overlap_cnf.py', ['--candidate', row['candidate_path'], '--out', key(cnf)],
                           cnf/'manifest.json', directory/'01_adapter.log')
            require(made['status'] == 'FIXED_OVERLAP_CNF_ADAPTER_COMPLETE', 'Adapter failed')
            audit = execute('audit_fixed_overlap_cnf.py', ['--manifest', key(cnf/'manifest.json'), '--out', key(cnf/'independent_audit.json')],
                            cnf/'independent_audit.json', directory/'02_mapping_audit.log')
            require(audit['status'] == 'INDEPENDENT_FIXED_OVERLAP_CNF_MAPPING_AUDIT_PASS', 'Mapping audit failed')
            result = execute('run_fixed_overlap_sat.py', ['--manifest', key(cnf/'manifest.json'), '--audit', key(cnf/'independent_audit.json'),
                             '--out', key(sat), '--conflicts', str(args.conflicts), '--seconds', str(args.seconds)],
                             sat/'result.json', directory/'03_sat.log')
            require(result['status'] in ('SAT_INDEPENDENTLY_VALIDATED_GRAPH', 'UNSAT_UNVERIFIED', 'UNKNOWN', 'INVALID_SAT_MODEL'),
                    'Unexpected SAT status')
            completed.append(dict(proposal_index=active, candidate_path=row['candidate_path'], candidate_sha256=row['candidate_sha256'],
                                  status=result['status'], result_path=key(sat/'result.json'), result_sha256=digest(sat/'result.json'),
                                  validated_witness=result['validated_witness']))
            print(json.dumps(completed[-1]), flush=True)
            if result['status'] in ('SAT_INDEPENDENTLY_VALIDATED_GRAPH', 'INVALID_SAT_MODEL'):
                break
        report = dict(status='BOUNDED_CP_COMPLETION_INVESTIGATIONS_FINISHED', manifest_path=key(out/'manifest.json'),
                      manifest_sha256=digest(out/'manifest.json'), inputs_sha256=manifest['inputs_sha256'], completed=completed,
                      completed_steps=steps, elapsed_seconds=time.perf_counter()-started,
                      fixed_K_exclusions_without_separate_proof=0, general_nonexistence_proved=False, goal_marked_complete=False)
        save(out/'summary.json', report)
    except BaseException as exc:
        save(out/'failure.json', dict(status='CP_COMPLETION_INVESTIGATIONS_STOPPED', active_index=active,
                                     error_type=type(exc).__name__, message=str(exc), completed=completed, completed_steps=steps))
        raise


if __name__ == '__main__':
    main()
