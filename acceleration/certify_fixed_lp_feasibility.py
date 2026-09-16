"""Try bounded rational reconstructions, certifying only exact LP feasibility.

All 4,326 nontrivial/outer-pair rows and 336 omitted zero quotas come from the
independent full99 graph checker. Failed reconstruction is inconclusive and
does not exclude K. The necessary linear system still omits X*X products.
"""
import argparse
from fractions import Fraction
from hashlib import sha256
import json
from math import isfinite
from pathlib import Path
import time

from audit_phase1 import graph_rows, compare_rows

ROOT = Path(__file__).resolve().parents[1]
DENOMINATORS = (1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 32, 64, 128, 256, 512, 1024, 10000, 1000000)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def resolve(name):
    path = Path(str(name).replace('\\', '/'))
    return path.resolve() if path.is_absolute() else (ROOT/path).resolve()


def key(path):
    return resolve(path).relative_to(ROOT).as_posix()


def digest(path):
    return sha256(resolve(path).read_bytes()).hexdigest()


def fraction(value):
    return dict(numerator=str(value.numerator), denominator=str(value.denominator), approximate=float(value))


def check_rational_point(rows, values):
    require(len(values) == 1680 and all(type(v) is Fraction for v in values), 'Expected exact rational X')
    residuals = [sum((values[j] for j in row['terms']), Fraction(0))-row['target'] for row in rows]
    quota = [abs(v) for row, v in zip(rows, residuals) if row['equality']]
    cap = [max(Fraction(0), v) for row, v in zip(rows, residuals) if not row['equality']]
    bad_box = sum(not 0 <= v <= 1 for v in values)
    total = sum(quota, Fraction(0))+sum(cap, Fraction(0))
    return dict(feasible=bad_box == 0 and total == 0, box_violations=bad_box,
                quota_failed_rows=sum(v != 0 for v in quota), cap_failed_rows=sum(v != 0 for v in cap),
                maximum_absolute_quota_residual=fraction(max(quota)), maximum_positive_cap_residual=fraction(max(cap)),
                total_violation=fraction(total))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--phase1', type=Path, required=True)
    parser.add_argument('--search-audit', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), 'Preserve all prior reconstruction artifacts')
    started, bindings = time.perf_counter(), {}
    def bind(path, expected=None):
        name = key(path)
        if name not in bindings:
            bindings[name] = digest(path)
        require(expected is None or bindings[name] == expected, 'Changed artifact: '+name)
        return bindings[name]
    for path in (args.candidate, args.phase1, args.search_audit, Path(__file__),
                 ROOT/'acceleration/audit_phase1.py', ROOT/'acceleration/audit_certificate.py'):
        bind(path)
    audit = json.loads(args.search_audit.read_bytes())
    require(audit['status'] in ('INDEPENDENT_CP_MATCHING_SEARCH_AUDIT_PASS', 'INDEPENDENT_CP_CROSS_SEARCH_AUDIT_PASS'),
            'Independent search audit missing')
    audit_bindings = {key(name): expected for name, expected in audit['inputs_sha256'].items()}
    for path in (args.candidate, args.phase1):
        require(audit_bindings.get(key(path)) == bind(path), 'Search audit does not bind original candidate/phase')
    for path, expected in audit_bindings.items():
        bind(path, expected)
    candidate, phase = [json.loads(path.read_bytes()) for path in (args.candidate, args.phase1)]
    require(phase['candidate_sha256'] == bind(args.candidate), 'Phase/candidate hash mismatch')
    require(resolve(phase['candidate_path']) == args.candidate.resolve(), 'Use the original phase candidate path')
    for name, expected in phase['source_sha256'].items():
        require(Path(name).name == name, 'Producer source must be a basename')
        bind(ROOT/'acceleration'/name, expected)
    edges, rows, omitted = graph_rows(candidate)
    require(len(rows) == 4326 and len(omitted) == 336 and all(r['target'] == 0 for r in omitted), 'Full99 row inventory differs')
    compare_rows(phase['constraint_groups'], rows)
    require(phase['edge_variables'] == [list(e) for e in edges], 'Stored X column order differs')
    numeric = phase['numeric_edge_values']
    require(type(numeric) is list and len(numeric) == 1680 and all(type(v) in (int, float) and isfinite(v) and 0 <= v <= 1 for v in numeric),
            'Stored X must be finite and box feasible')
    original = list(map(Fraction, numeric))
    trials, witness = [], None
    candidates = [('STORED_BINARY_FLOATS_AS_EXACT_RATIONALS', None, original)]
    candidates.extend(('COMMON_DENOMINATOR_NEAREST_TIES_TO_EVEN', d, [Fraction(round(v*d), d) for v in original]) for d in DENOMINATORS)
    candidates.extend(('INDIVIDUAL_DENOMINATOR_LIMIT', d, [v.limit_denominator(d) for v in original]) for d in DENOMINATORS)
    for method, limit, values in candidates:
        checked = check_rational_point(rows, values)
        trial = dict(method=method, denominator_limit=limit, **checked)
        trials.append(trial)
        if checked['feasible']:
            witness = dict(method=method, denominator_limit=limit, edge_variables=[list(e) for e in edges],
                           rational_edge_values=[fraction(v) for v in values], all_x_binary=all(v in (0, 1) for v in values),
                           exact_checks=checked, quota_equalities_checked=840, pair_inequalities_checked=3486,
                           omitted_zero_quota_identities_checked=336, box_bounds_checked=1680)
            break
    require(all(digest(path) == expected for path, expected in bindings.items()), 'Input/source changed during reconstruction')
    report = dict(status='EXACT_FIXED_K_NECESSARY_LINEAR_RELAXATION_FEASIBLE' if witness else 'BOUNDED_RATIONAL_RECONSTRUCTION_INCONCLUSIVE',
                  inputs_sha256=bindings, candidate_path=key(args.candidate), candidate_sha256=bind(args.candidate),
                  phase1_path=key(args.phase1), phase1_sha256=bind(args.phase1), search_audit_path=key(args.search_audit),
                  search_audit_sha256=bind(args.search_audit), stored_numeric_objective=phase['numeric_objective'],
                  denominators_tested=list(DENOMINATORS), trials=trials, exact_feasibility_witness=witness,
                  exact_LP_feasibility_proved=witness is not None, fixed_K_infeasibility_claimed=False,
                  graph_constructed=False, general_nonexistence_proved=False,
                  symbolic_linear_solve_performed=False, numerical_solver_called=False, elapsed_seconds=time.perf_counter()-started,
                  scope='Only exact feasibility of the independently derived necessary continuous LP can be certified. Reconstruction failure is inconclusive; binary X still requires all omitted quadratic common-neighbor terms and pure full99 graph verification.')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(report, indent=2, allow_nan=False)+'\n')
    print(json.dumps({k: report[k] for k in ('status', 'stored_numeric_objective', 'exact_LP_feasibility_proved', 'elapsed_seconds')}))


if __name__ == '__main__':
    main()
