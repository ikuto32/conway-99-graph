"""Gate exactly improving CP-shortlist seeds and bind the first verified best.

Native failures/caps only prevent adoption; they are not independent proofs.
The first independently nonempty closure in exact-upper-bound order is adopted.
A candidate without a positive exact LP lower bound is left for completion work.
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


def require(ok, message):
    if not ok:
        raise ValueError(message)


def resolve(name):
    path = Path(str(name).replace('\\', '/'))
    return path if path.is_absolute() else ROOT/path


def key(path):
    return path.resolve().relative_to(ROOT).as_posix()


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def rational(value):
    return Fraction(int(value['numerator']), int(value['denominator']))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, required=True)
    args = parser.parse_args()
    directory = args.directory.resolve()
    summary_path, audit_path = directory/'summary.json', directory/'audit.json'
    report_path = directory/'adoption.json'
    require(not report_path.exists() and not (directory/'local').exists(), 'Preserve prior local/adoption evidence')
    started = time.perf_counter()
    summary, audit = [json.loads(p.read_bytes()) for p in (summary_path, audit_path)]
    require(summary['status'] == 'BOUNDED_CP_MATCHING_SEARCH_FINISHED' and
            audit['status'] == 'INDEPENDENT_CP_MATCHING_SEARCH_AUDIT_PASS', 'Search not independently audited')
    bindings = {key(resolve(name)): expected for name, expected in audit['inputs_sha256'].items()}
    require(bindings.get(key(summary_path)) == digest(summary_path), 'Audit is not bound to this summary')
    require(all(digest(resolve(name)) == expected for name, expected in bindings.items()), 'Changed search dependency')
    # Read the audited warm-phase association from the independent audit rather
    # than assuming the copied best wrapper has the original candidate hash.
    old_audit = audit['baseline_audit']
    old_candidates = [resolve(name) for name in old_audit['inputs_sha256']
                      if 'candidate' in Path(name).name]
    old_results = [resolve(name) for name in old_audit['inputs_sha256']
                   if 'phase1' in Path(name).name]
    require(len(old_candidates) == len(old_results) == 1, 'Ambiguous audited baseline inputs')
    previous_candidate, previous_phase = old_candidates[0], old_results[0]
    require(digest(previous_candidate) == old_audit['inputs_sha256'][next(n for n in old_audit['inputs_sha256'] if resolve(n) == previous_candidate)], 'Previous candidate changed')
    records = {r['proposal_index']: r for r in summary['records']}
    reports = {r['proposal_index']: r for r in audit['probe_reports']}
    indices = audit['exact_strict_improvement_indices']
    ordered = sorted(indices, key=lambda i:(rational(reports[i]['phase1_audit']['exact_primal_upper_bound']), i))
    require(len(set(ordered)) == len(ordered) and all(reports[i]['exact_strict_improvement'] for i in ordered), 'Bad strict improvement list')
    sources = [Path(__file__), ROOT/'acceleration/check_shortlist_native_pair.py',
               ROOT/'acceleration/audit_goal_theory_pairs.py', ROOT/'acceleration/bind_cp_matching_improvement.py']
    bindings.update({key(p):digest(p) for p in sources+[summary_path, audit_path]})
    attempted, adopted, pending = [], None, None

    def run(script, arguments):
        process = subprocess.run([sys.executable, '-B', str(ROOT/'acceleration'/script)] + arguments,
                                 cwd=ROOT, text=True, capture_output=True, timeout=180)
        require(process.returncode == 0, script+' failed: '+process.stderr)

    for index in ordered:
        row = records[index]
        candidate_path = resolve(row['candidate_path'])
        require(digest(candidate_path) == row['candidate_sha256'], 'Selected candidate changed')
        if rational(reports[index]['phase1_audit']['exact_dual_lower_bound']) <= 0:
            pending = dict(proposal_index=index, candidate_path=key(candidate_path),
                           reason='Nonpositive exact LP lower bound: requires completion work, not positive-merit seed adoption')
            break
        local = directory/'local'/f'index_{index}'
        run('check_shortlist_native_pair.py', ['--candidate', key(candidate_path), '--out', key(local)])
        gate = json.loads((local/'gate.json').read_bytes())
        attempt = dict(proposal_index=index, numeric_objective=row['numeric_objective'],
                       gate_path=key(local/'gate.json'), gate_sha256=digest(local/'gate.json'),
                       native_passed=gate['passed'], independently_nonempty=False)
        attempted.append(attempt)
        if gate['passed']:
            pair_audit = local/'independent_pair_audit.json'
            run('audit_goal_theory_pairs.py', ['--candidate', key(candidate_path), '--domains', key(local/'stars.json'),
                 '--pair-certificate', key(local/'pairs.json'), '--out', key(pair_audit), '--seconds', '60'])
            pair = json.loads(pair_audit.read_bytes())
            attempt.update(pair_audit_path=key(pair_audit), pair_audit_sha256=digest(pair_audit),
                           independently_nonempty=pair['status'] == 'INDEPENDENT_EXACT_PAIR_DOMAIN_AUDIT_PASS'
                           and pair.get('propagation_status') == 'ARC_CONSISTENT_NONEMPTY')
            if attempt['independently_nonempty']:
                adopted_dir = directory/f'adopted_index_{index}'
                run('bind_cp_matching_improvement.py', ['--summary', key(summary_path), '--search-audit', key(audit_path),
                     '--index', str(index), '--previous-candidate', key(previous_candidate), '--previous-phase1', key(previous_phase),
                     '--pair-audit', key(pair_audit), '--pair-certificate', key(local/'pairs.json'), '--out', key(adopted_dir)])
                combined = adopted_dir/'combined_evidence.json'
                adopted = dict(proposal_index=index, combined_evidence_path=key(combined), combined_evidence_sha256=digest(combined))
                break
        print(json.dumps(attempt), flush=True)
    require(all(digest(resolve(name)) == expected for name, expected in bindings.items()), 'Bound evidence changed during adoption')
    report = dict(status='CP_EXACT_IMPROVEMENT_LOCAL_ADOPTION_FINISHED', inputs_sha256=bindings,
                  sorted_exact_improvement_indices=ordered, attempts=attempted, adopted=adopted, pending_completion_work=pending,
                  elapsed_seconds=time.perf_counter()-started, graph_constructed=False, general_nonexistence_proved=False,
                  scope='First independently pair-consistent strictly improving seed in exact-upper order. Native failures or caps are not independent exclusions. A positive exact fixed-K lower bound still forbids completing the adopted K; change K further.')
    with report_path.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(report, indent=2, allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('inputs_sha256', 'attempts', 'sorted_exact_improvement_indices')}), flush=True)


if __name__ == '__main__':
    main()
