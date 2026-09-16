"""Replay a finished nine-candidate integer-certificate batch; never rerun LPs."""
import argparse
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def resolve(name):
    p = Path(str(name).replace('\\', '/'))
    return p.resolve() if p.is_absolute() else (ROOT/p).resolve()


def key(path):
    return resolve(path).relative_to(ROOT).as_posix()


def digest(path):
    return sha256(resolve(path).read_bytes()).hexdigest()


def number(q):
    require(type(q) is dict and type(q['numerator']) is str and type(q['denominator']) is str
            and int(q['denominator']) > 0, 'Malformed exact interval endpoint')
    return Fraction(int(q['numerator']), int(q['denominator']))


def rational(q):
    return dict(numerator=str(q.numerator), denominator=str(q.denominator), approximate=float(q))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), 'Preserve previous replay summary')
    started, inputs, outputs = time.perf_counter(), {}, {}
    def bind(path, expected=None):
        label = key(path)
        if label not in inputs:
            inputs[label] = digest(path)
        require(expected is None or inputs[label] == expected, 'Changed input: '+label)
        return inputs[label]
    def read(path, status=None):
        bind(path)
        obj = json.loads(resolve(path).read_bytes())
        require(status is None or obj['status'] == status, 'Unexpected status: '+key(path))
        for p, expected in obj.get('inputs_sha256', {}).items():
            bind(p, expected)
        return obj
    summary_path = args.directory/'summary.json'
    summary = read(summary_path, 'BOUNDED_STAR_MARGINAL_SHORTLIST_FINISHED')
    bind(summary['manifest_path'], summary['manifest_sha256'])
    manifest = read(summary['manifest_path'], 'STAR_MARGINAL_SHORTLIST_MANIFEST')
    require(summary['inputs_sha256'] == manifest['inputs_sha256'], 'Manifest/summary input map differs')
    rows = summary['records']
    require(len(rows) == 9 and len({r['proposal_index'] for r in rows}) == 9 and all(r['audited'] for r in rows),
            'Expected nine independently audited candidates')
    selected = {r['proposal_index']: r for r in manifest['candidates']}
    require(set(selected) == {r['proposal_index'] for r in rows}, 'Batch selection inventory differs')
    verifier = ROOT/'acceleration/verify_star_marginal_certificate.py'
    for source in (Path(__file__), verifier, ROOT/'acceleration/audit_certificate.py', ROOT/'acceleration/run_star_marginal_shortlist.py'):
        bind(source)
    baseline = read(manifest['baseline_audit_path'], 'INDEPENDENT_EXACT_STAR_MARGINAL_PHASE1_AUDIT_PASS')
    bind(manifest['baseline_audit_path'], manifest['baseline_audit_sha256'])
    baseline_lower = number(baseline['exact_dual_lower'])
    require(baseline_lower == number(manifest['baseline_exact_lower']) > 0, 'Baseline exact interval differs')
    # Validate all completed outputs before launching even the first replay.
    for step in summary['completed_steps']:
        bind(step['result_path'], step['result_sha256']); bind(step['log_path'], step['log_sha256'])
    jobs = []
    for row in rows:
        i = row['proposal_index']; chosen = selected[i]
        require(row['candidate_path'] == chosen['candidate_path'] and row['candidate_sha256'] == chosen['candidate_sha256'], 'Selected candidate differs')
        bind(row['candidate_path'], row['candidate_sha256']); bind(row['result_path'], row['result_sha256'])
        bind(row['audit_path'], row['audit_sha256'])
        phase = read(row['result_path'])
        audit = read(row['audit_path'], 'INDEPENDENT_EXACT_STAR_MARGINAL_PHASE1_AUDIT_PASS')
        audit_map = {key(p): h for p, h in audit['inputs_sha256'].items()}
        require(audit_map.get(key(row['result_path'])) == row['result_sha256'] and
                audit_map.get(key(row['candidate_path'])) == row['candidate_sha256'], 'LP audit not bound to selected input')
        require(phase['candidate_sha256'] == row['candidate_sha256'] and resolve(phase['candidate_path']) == resolve(row['candidate_path']), 'LP input identity differs')
        lower, upper = number(audit['exact_dual_lower']), number(audit['exact_primal_upper'])
        require(lower == number(row['exact_lower']) and upper == number(row['exact_upper']) and 0 < lower <= upper, 'Positive exact interval differs')
        require(row['fixed_K_excluded'] is True and row['exact_strict_improvement'] == (upper < baseline_lower), 'Wrong batch interval claim')
        cert = resolve(audit['certificate_path'])
        bind(cert, audit['certificate_sha256'])
        require(cert == (args.directory/f'index_{i}'/'integer_certificate.json').resolve(), 'Unexpected certificate location')
        replay = args.directory/f'index_{i}'/'replay.json'
        require(not replay.exists(), 'Preserve existing per-candidate replay')
        jobs.append((row, phase, cert, replay, lower, upper))
    reports = []
    for row, phase, cert, replay, lower, upper in jobs:
        command = [sys.executable, '-B', str(verifier), '--candidate', row['candidate_path'], '--domains', phase['domains_path'],
                   '--domain-audit', phase['domain_audit_path'], '--certificate', key(cert), '--out', key(replay)]
        subprocess.run(command, cwd=ROOT, check=True)
        result = json.loads(replay.read_bytes())
        require(result['status'] == 'INDEPENDENT_INTEGER_STAR_MARGINAL_CERTIFICATE_REPLAY_PASS' and result['fixed_K_excluded'], 'Integer certificate replay failed')
        require(Fraction(int(result['exact_integer_gap']), int(result['integer_scale'])) == lower, 'Replayed exact lower differs')
        outputs[key(replay)] = digest(replay)
        reports.append(dict(proposal_index=row['proposal_index'], candidate_path=row['candidate_path'], candidate_sha256=row['candidate_sha256'],
                            certificate_path=key(cert), certificate_sha256=digest(cert), replay_path=key(replay), replay_sha256=digest(replay),
                            audit_path=row['audit_path'], audit_sha256=row['audit_sha256'], exact_lower=rational(lower), exact_upper=rational(upper),
                            exact_strict_improvement=upper < baseline_lower, guaranteed_improvement=rational(baseline_lower-upper),
                            domain_choices_checked=result['domain_choices_checked'], fixed_K_excluded=True))
    best = min(reports, key=lambda r: (number(r['exact_upper']), r['proposal_index']))
    require(summary['best']['proposal_index'] == best['proposal_index'] and
            summary['exact_strict_improvement_count'] == sum(r['exact_strict_improvement'] for r in reports), 'Batch best/improvement count differs')
    best_upper = number(best['exact_upper'])
    separated = all(best_upper < number(r['exact_lower']) for r in reports if r is not best)
    require(all(digest(p) == expected for p, expected in inputs.items()), 'Bound source/input changed during replay')
    report = dict(status='NINE_STAR_MARGINAL_INTEGER_CERTIFICATES_AND_EXACT_INTERVAL_COMPARISON_PASS', inputs_sha256=inputs,
                  outputs_sha256=outputs, records=reports, best=best, baseline_exact_lower=rational(baseline_lower),
                  all_nine_fixed_K_certificates_positive=True, best_interval_strictly_below_all_other_intervals=separated,
                  exact_strict_improvement_count=sum(r['exact_strict_improvement'] for r in reports),
                  solver_calls=0, prior_phase1_audits_rerun=0, certificate_replays=9, graph_constructed=False, general_nonexistence_proved=False,
                  elapsed_seconds=time.perf_counter()-started,
                  scope='Fresh integer-only proof replay for nine fixed K; exact upper endpoints are reused from hash-bound independent rational-normalization audits. Rankings compare only this star-marginal objective.')
    with args.out.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(report, indent=2, allow_nan=False)+'\n')
    print(json.dumps(dict(status=report['status'], best_index=best['proposal_index'], best_upper=float(best_upper),
                          guaranteed_baseline_improvement=float(baseline_lower-best_upper), separated=separated,
                          elapsed_seconds=report['elapsed_seconds'])))


if __name__ == '__main__':
    main()
