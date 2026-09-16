"""Evaluate an audited completion shortlist with a distinct star-simplex merit.

This orchestration does not compare star merit numerically to edge phase-I
merit, infer feasibility from zero, or claim general nonexistence.
"""
import argparse
from fractions import Fraction
from hashlib import sha256
import json
from math import isfinite
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def path(name):
    p = Path(str(name).replace('\\', '/'))
    return p.resolve() if p.is_absolute() else (ROOT/p).resolve()


def key(name):
    return path(name).relative_to(ROOT).as_posix()


def digest(name):
    return sha256(path(name).read_bytes()).hexdigest()


def save(name, data):
    with path(name).open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(data, indent=2, allow_nan=False)+'\n')


def number(q):
    return Fraction(int(q['numerator']), int(q['denominator']))


def preflight(args):
    require(sys.version_info[:2] == (3, 12), 'Use .venv/Scripts/python.exe')
    require(not args.out.exists() and args.out.resolve().is_relative_to(ROOT), 'Use a fresh workspace output')
    require(isfinite(args.seconds) and 0 < args.seconds <= 3600, 'Finite positive LP budget required')
    inputs = {}
    def bind(name, expected=None):
        label = key(name)
        if label not in inputs:
            inputs[label] = digest(name)
        require(expected is None or inputs[label] == expected, 'Changed dependency: '+label)
        return inputs[label]
    def read(name, status):
        bind(name)
        data = json.loads(path(name).read_bytes())
        require(data['status'] == status, 'Unexpected report status: '+key(name))
        for p, h in data.get('inputs_sha256', {}).items():
            bind(p, h)
        return data
    manifest = read(args.manifest, 'CP_COMPLETION_INVESTIGATION_MANIFEST')
    baseline = read(args.baseline_audit, 'INDEPENDENT_EXACT_STAR_MARGINAL_PHASE1_AUDIT_PASS')
    bind(baseline['certificate_path'], baseline['certificate_sha256'])
    require(number(baseline['exact_dual_lower']) > 0, 'A positive exact baseline bound is required')
    sources = [Path(__file__), ROOT/'acceleration/star_marginal_phase1.py', ROOT/'acceleration/audit_star_marginal_phase1.py']
    for source in sources:
        bind(source)
    require(inputs[key(sources[-1])] == baseline['inputs_sha256'].get(key(sources[-1])) and
            inputs[key(sources[-2])] == baseline['inputs_sha256'].get(key(sources[-2])), 'Use baseline-audited frozen implementations')
    rows = manifest['selected_candidates']
    require(rows and len(rows) <= 64 and len({r['proposal_index'] for r in rows}) == len(rows), 'Invalid selected candidate inventory')
    for row in rows:
        bind(row['candidate_path'], row['candidate_sha256'])
        local = path(args.manifest).parent/f"index_{row['proposal_index']}"/'local'
        audit = read(local/'independent_pair_audit.json', 'INDEPENDENT_EXACT_PAIR_DOMAIN_AUDIT_PASS')
        require(audit['complete_used_domains_verified'] and audit['propagation_status'] == 'ARC_CONSISTENT_NONEMPTY'
                and len(audit['independently_reenumerated_domains']) == 84, 'Incomplete local domain proof')
        declared = {key(p): h for p, h in audit['inputs_sha256'].items()}
        require(declared.get(key(row['candidate_path'])) == row['candidate_sha256'] and
                declared.get(key(local/'stars.json')) == bind(local/'stars.json'), 'Domain proof/candidate mismatch')
    return dict(status='STAR_MARGINAL_SHORTLIST_MANIFEST', inputs_sha256=inputs, selection_manifest_path=key(args.manifest),
                selection_manifest_sha256=bind(args.manifest), baseline_audit_path=key(args.baseline_audit),
                baseline_audit_sha256=bind(args.baseline_audit), baseline_exact_lower=baseline['exact_dual_lower'],
                candidates=rows, per_LP_time_limit_seconds=args.seconds,
                merit='STAR_SIMPLEX_RECIPROCITY_PLUS_LINEAR_CAP_VIOLATIONS', old_edge_merit_comparison=False,
                graph_constructed=False, general_nonexistence_proved=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--baseline-audit', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--seconds', type=float, default=30)
    parser.add_argument('--validate-only', action='store_true')
    args = parser.parse_args()
    manifest = preflight(args)
    if args.validate_only:
        print(json.dumps(dict(status='STAR_MARGINAL_SHORTLIST_READ_ONLY_PREFLIGHT_PASS', candidates=len(manifest['candidates']),
                             processes_launched=0, output_created=False)), flush=True)
        return
    args.out.mkdir(parents=True, exist_ok=False)
    save(args.out/'manifest.json', manifest)
    started, records, steps = time.perf_counter(), [], []
    def run(script, arguments, output, log):
        require(all(digest(p) == h for p, h in manifest['inputs_sha256'].items()), 'Bound input changed')
        with log.open('x', encoding='utf-8') as stream:
            result = subprocess.run([sys.executable, '-B', str(ROOT/'acceleration'/script)] + arguments,
                                    cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, check=False)
        require(result.returncode == 0, script+' failed; see '+key(log))
        steps.append(dict(result_path=key(output), result_sha256=digest(output), log_path=key(log), log_sha256=digest(log)))
        return json.loads(output.read_bytes())
    active = None
    try:
        for chosen in manifest['candidates']:
            active = chosen['proposal_index']
            local = path(args.manifest).parent/f'index_{active}'/'local'
            out = args.out/f'index_{active}'
            out.mkdir()
            print(json.dumps(dict(index=active, event='START')), flush=True)
            result = run('star_marginal_phase1.py', ['--candidate', chosen['candidate_path'], '--domains', key(local/'stars.json'),
                         '--domain-audit', key(local/'independent_pair_audit.json'), '--out', key(out/'phase1.json'),
                         '--seconds', str(args.seconds)], out/'phase1.json', out/'01_lp.log')
            row = dict(proposal_index=active, candidate_path=chosen['candidate_path'], candidate_sha256=chosen['candidate_sha256'],
                       result_path=key(out/'phase1.json'), result_sha256=digest(out/'phase1.json'), numerical_status=result['status'],
                       audited=False, exact_strict_improvement=False)
            if 'numeric_probabilities' in result and 'numeric_cap_duals' in result:
                audit = run('audit_star_marginal_phase1.py', ['--result', key(out/'phase1.json'), '--out', key(out/'audit.json'),
                            '--certificate-out', key(out/'integer_certificate.json')], out/'audit.json', out/'02_audit.log')
                require(audit['status'] == 'INDEPENDENT_EXACT_STAR_MARGINAL_PHASE1_AUDIT_PASS', 'Independent bound audit failed')
                row.update(audited=True, audit_path=key(out/'audit.json'), audit_sha256=digest(out/'audit.json'),
                           exact_lower=audit['exact_dual_lower'], exact_upper=audit['exact_primal_upper'],
                           fixed_K_excluded=audit['positive_exact_dual_excludes_fixed_K'],
                           exact_strict_improvement=number(audit['exact_primal_upper']) < number(manifest['baseline_exact_lower']))
            records.append(row)
            print(json.dumps(dict(index=active, audited=row['audited'], exact_strict_improvement=row['exact_strict_improvement'],
                                  numeric_objective=result.get('numeric_objective'))), flush=True)
        audited = sorted((r for r in records if r['audited']), key=lambda r: (number(r['exact_upper']), r['proposal_index']))
        save(args.out/'summary.json', dict(status='BOUNDED_STAR_MARGINAL_SHORTLIST_FINISHED',
             manifest_path=key(args.out/'manifest.json'), manifest_sha256=digest(args.out/'manifest.json'),
             inputs_sha256=manifest['inputs_sha256'], records=records, completed_steps=steps, best=audited[0] if audited else None,
             exact_strict_improvement_count=sum(r['exact_strict_improvement'] for r in records),
             graph_constructed=False, general_nonexistence_proved=False, goal_marked_complete=False,
             elapsed_seconds=time.perf_counter()-started))
    except BaseException as exc:
        save(args.out/'failure.json', dict(status='STAR_MARGINAL_SHORTLIST_STOPPED', active_index=active,
                                         error_type=type(exc).__name__, message=str(exc), records=records, completed_steps=steps))
        raise


if __name__ == '__main__':
    main()
