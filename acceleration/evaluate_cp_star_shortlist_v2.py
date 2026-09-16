"""Evaluate an audited CP near-zero shortlist with complete stars and exact bounds.

No SAT run, graph witness, or global nonexistence claim is made. Native failures,
caps and nonpositive exact bounds remain pending. The star objective is distinct
from the edge phase-I objective used only for the initial selection.
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
ROOT_PINS = {
    'scratch_next_overlap_cut_bank.py': '6634ac5ac9caa9d2658bbf146774729d4a810d3d4c15a2a20c2b9485877b9a24',
    'scratch_next_overlap_cut.py': 'f3069af836a03fc46cf08b647c7bcce2d5b1349e976b4bfd82d9a0a7f968a449',
    'scratch_next_overlap_cut_orbit.py': 'b56acd616862b807d7c1ad1f442c35c98ab3db9ab1aa964cef3b29b397c7ec96',
}
PINS = {
    'check_shortlist_native_pair.py': '5422d2d1cf5abb07ce7c6483f3fc5f5af41c0b2ddcdccf31c70c4c553cf0b398',
    'audit_goal_theory_pairs.py': '9da60c600c45c16274efd05db0cf3c21cab8a61969dd2fe0d372ac9a2e7be75f',
    'audit_goal_theory_domains.py': '150ea838ad370793b6508728a9ce4d88e5121f51e2774d24f9bb37d244b52388',
    'audit_goal_theory_stars.py': 'e572175d69bef9a31ea4896dd74a181cd0d27d212a14f37e4c9871a0f213fb78',
    'star_marginal_phase1.py': 'bd2c656b5b8c17b374895a6fc3ea11a6e4402aceda4ee9370694c0af847319ef',
    'audit_star_marginal_phase1.py': 'c4485a047219cb8bbeed5baf1b9ee3a36203e8febb6490a45edd8ec7d2245b78',
    'verify_star_marginal_certificate.py': '43952955884b8b2dc04281b92d6b826dc5c8279d2ec6e7b540e930adddfe291b',
    'audit_phase1.py': '655898a7f9f565dea18236aaa706081c2adb169b84ad836c49dccbe459f7ff2d',
    'audit_certificate.py': '22d3e334930f734890216f18cfc8335c0a5c046f142a72e5a30beca6be9f1c9d',
    'guided_overlap.py': '03a839c004fc049e20ecbbeeb11eaff97baee49b6e8212fc15c2eb596d43fcbf',
    'prepare.py': 'f9eaf973bb5530b88f12ad455bffa4a82d17904be0786ee37070bb98ead16417',
    'star_domains.rs': 'b3637615352c0a5372fe7ed2237f34bc2d5c8773a892ee647c05acb772584d80',
    'pair_domains.rs': '39fe24d3a87ee4780ad8daff1aeb95cb830fe0877d9ed2b56b0ccdb82e3621ff',
    'build/star_domains.exe': 'e34d5081e1ce73ef68c47cd9dff2baa41046b7defbea8abe12c2126c5eb95f36',
    'build/pair_domains.exe': '7031a0a9d32075fb8f32777149ff5f54466c930726a2777709aa5278779eb976',
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


def load(name):
    return json.loads(resolve(name).read_bytes())


def save(name, data):
    with resolve(name).open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(data, indent=2, allow_nan=False)+'\n')


def number(q):
    require(type(q) is dict and type(q['numerator']) is str and type(q['denominator']) is str
            and int(q['denominator']) > 0, 'Malformed exact endpoint')
    return Fraction(int(q['numerator']), int(q['denominator']))


def rational(q):
    return dict(numerator=str(q.numerator), denominator=str(q.denominator), approximate=float(q))


def normalized(mapping):
    result = {key(p): h for p, h in mapping.items()}
    require(len(result) == len(mapping), 'Ambiguous normalized dependency names')
    return result


def select_records(summary, audit):
    """Pure inventory/association check, separately exercised by corruption QA."""
    require(summary['status'] == 'BOUNDED_CP_MATCHING_SEARCH_FINISHED' and audit['status'] in
            ('INDEPENDENT_CP_MATCHING_SEARCH_AUDIT_PASS', 'INDEPENDENT_CP_CROSS_SEARCH_AUDIT_PASS'),
            'Expected independently audited completed CP search')
    rows = {r['proposal_index']: r for r in summary['records']}
    reports = {r['proposal_index']: r for r in audit['probe_reports']}
    require(len(rows) == len(summary['records']) == summary['probes'] ==
            audit['actual_LP_exact_intervals_checked'] == len(reports) == len(audit['probe_reports']) and
            set(rows) == set(reports), 'Duplicate, missing or inconsistent LP inventory')
    declared = normalized(audit['inputs_sha256'])
    eligible = []
    for index, row in rows.items():
        require(type(index) is int and index >= 0, 'Invalid proposal index')
        report = reports[index]
        phase = report['phase1_audit']
        require(phase['status'] == 'INDEPENDENT_PHASE1_GRAPH_MODEL_PRIMAL_DUAL_AUDIT_PASS', 'Unaudited LP record')
        phase_bindings = normalized(phase['inputs_sha256'])
        for field in ('candidate', 'result'):
            name, expected = key(row[field+'_path']), row[field+'_sha256']
            require(name == key(report[field+'_path']) and declared.get(name) == expected and
                    phase_bindings.get(name) == expected, 'CP candidate/result association differs')
        lo, hi = number(phase['exact_dual_lower_bound']), number(phase['exact_primal_upper_bound'])
        require(lo <= hi and hi >= 0, 'Invalid exact edge merit interval')
        if lo <= 0 and hi <= Fraction(1, 100000000):
            eligible.append(dict(proposal_index=index, candidate_path=key(row['candidate_path']),
                candidate_sha256=row['candidate_sha256'], edge_phase1_path=key(row['result_path']),
                edge_phase1_sha256=row['result_sha256'], exact_edge_lower=rational(lo), exact_edge_upper=rational(hi)))
    eligible.sort(key=lambda r: (number(r['exact_edge_upper']), r['proposal_index']))
    return eligible


def preflight(args):
    require(sys.version_info[:2] == (3, 12), 'Use .venv/Scripts/python.exe')
    require(resolve(args.out).is_relative_to(ROOT) and not resolve(args.out).exists(), 'Use a fresh workspace output')
    require(type(args.max_candidates) is int and 1 <= args.max_candidates <= 32 and
            isfinite(args.seconds) and 0 < args.seconds <= 3600 and
            isfinite(args.audit_seconds) and 0 < args.audit_seconds <= 3600, 'Invalid finite evaluation limits')
    inputs = {}
    def bind(name, expected=None):
        label = key(name)
        if label not in inputs:
            inputs[label] = digest(name)
        require(expected is None or inputs[label] == expected, 'Changed dependency: '+label)
        return inputs[label]
    def read(name):
        bind(name)
        data = load(name)
        for p, h in data.get('inputs_sha256', {}).items():
            bind(p, h)
        return data
    for name, expected in PINS.items():
        bind(ROOT/'acceleration'/name, expected)
    for name, expected in ROOT_PINS.items():
        bind(ROOT/name, expected)
    bind(Path(__file__))
    run = resolve(args.run)
    summary, audit = read(run/'summary.json'), read(run/'audit.json')
    require(normalized(audit['inputs_sha256']).get(key(run/'summary.json')) == bind(run/'summary.json'),
            'Audit is not bound to the selected search summary')
    eligible = select_records(summary, audit)
    baseline = read(args.baseline_star_audit)
    require(baseline['status'] == 'INDEPENDENT_EXACT_STAR_MARGINAL_PHASE1_AUDIT_PASS', 'Unaudited star baseline')
    lower, upper = number(baseline['exact_dual_lower']), number(baseline['exact_primal_upper'])
    require(0 < lower <= upper and baseline['positive_exact_dual_excludes_fixed_K'] is True, 'Positive exact star baseline required')
    cert = read(baseline['certificate_path'])
    bind(baseline['certificate_path'], baseline['certificate_sha256'])
    require(cert['fixed_K_excluded'] is True and number(cert['exact_phase1_lower_bound']) == lower,
            'Baseline certificate differs')
    base_map = normalized(baseline['inputs_sha256'])
    for name in ('star_marginal_phase1.py', 'audit_star_marginal_phase1.py'):
        require(base_map.get(key(ROOT/'acceleration'/name)) == PINS[name], 'Baseline uses a different star objective implementation')
    return dict(status='CP_STAR_SHORTLIST_EVALUATION_MANIFEST', inputs_sha256=inputs,
        search_directory=key(run), search_summary_path=key(run/'summary.json'), search_summary_sha256=bind(run/'summary.json'),
        search_audit_path=key(run/'audit.json'), search_audit_sha256=bind(run/'audit.json'),
        baseline_star_audit_path=key(args.baseline_star_audit), baseline_star_audit_sha256=bind(args.baseline_star_audit),
        baseline_exact_lower=rational(lower), baseline_exact_upper=rational(upper), eligible_candidates=len(eligible),
        selected_candidates=eligible[:args.max_candidates], max_candidates=args.max_candidates,
        unselected_eligible_indices=[r['proposal_index'] for r in eligible[args.max_candidates:]],
        selection_rule='Exact edge LP lower <=0, upper in [0,1/100000000], ordered by exact upper then index',
        native_star_seconds=30, native_star_node_cap=2000000, native_star_domain_cap=20000,
        native_pair_seconds=30, native_pair_check_cap=500000000, independent_pair_seconds=args.audit_seconds,
        per_star_LP_seconds=args.seconds, subprocess_wall_seconds=180+max(args.seconds, args.audit_seconds),
        merit='STAR_SIMPLEX_RECIPROCITY_PLUS_LINEAR_CAP_VIOLATIONS', old_edge_merit_comparison=False,
        exact_edge_LP_feasibility_claimed=False, SAT_or_DRAT_invocations=0,
        graph_constructed=False, general_nonexistence_proved=False)


def complete_pair_evidence(pair, chosen, stars_path):
    require(pair['status'] == 'INDEPENDENT_EXACT_PAIR_DOMAIN_AUDIT_PASS' and
            pair['complete_used_domains_verified'] is True and pair['propagation_status'] == 'ARC_CONSISTENT_NONEMPTY',
            'Incomplete or empty local proof cannot feed star LP')
    rows = pair['independently_reenumerated_domains']
    require([r['outer_vertex'] for r in rows] == list(range(84)) and all(r['domain_size'] > 0 for r in rows),
            'All84 complete nonempty domains required')
    bindings = normalized(pair['inputs_sha256'])
    require(bindings.get(key(chosen['candidate_path'])) == chosen['candidate_sha256'] and
            bindings.get(key(stars_path)) == digest(stars_path), 'Independent local proof input mismatch')


def checked_star_interval(audit, replay):
    require(audit['status'] == 'INDEPENDENT_EXACT_STAR_MARGINAL_PHASE1_AUDIT_PASS' and
            replay['status'] == 'INDEPENDENT_INTEGER_STAR_MARGINAL_CERTIFICATE_REPLAY_PASS', 'Missing exact star evidence')
    lo, hi = number(audit['exact_dual_lower']), number(audit['exact_primal_upper'])
    require(lo <= hi and hi >= 0 and int(replay['integer_scale']) > 0 and
            Fraction(int(replay['exact_integer_gap']), int(replay['integer_scale'])) == lo and
            replay['fixed_K_excluded'] == audit['positive_exact_dual_excludes_fixed_K'] == (lo > 0),
            'Independent integer replay or interval claim differs')
    return lo, hi


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--baseline-star-audit', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--max-candidates', type=int, default=9)
    parser.add_argument('--seconds', type=float, default=30)
    parser.add_argument('--audit-seconds', type=float, default=60)
    parser.add_argument('--validate-only', action='store_true')
    args = parser.parse_args()
    manifest = preflight(args)
    if args.validate_only:
        print(json.dumps(dict(status='CP_STAR_SHORTLIST_READ_ONLY_PREFLIGHT_PASS', eligible=manifest['eligible_candidates'],
            selected=len(manifest['selected_candidates']), output_created=False, processes_launched=0)), flush=True)
        return
    out = resolve(args.out); out.mkdir(parents=True, exist_ok=False)
    save(out/'manifest.json', manifest)
    records, steps, output_hashes = [], [], {}
    started, active = time.perf_counter(), None
    source_bindings = {key(ROOT/'acceleration'/p): h for p, h in PINS.items()}
    source_bindings.update({key(ROOT/p): h for p, h in ROOT_PINS.items()})
    source_bindings[key(Path(__file__))] = manifest['inputs_sha256'][key(Path(__file__))]
    def collect(name, status=None):
        data = load(name)
        require(status is None or data['status'] == status, 'Unexpected output status: '+key(name))
        output_hashes[key(name)] = digest(name)
        for field in ('inputs_sha256', 'files_sha256'):
            for p, expected in data.get(field, {}).items():
                require(digest(p) == expected, 'Output dependency changed: '+key(p))
                output_hashes[key(p)] = expected
        return data
    def execute(script, arguments, result_path, logfile):
        require(all(digest(p) == h for p, h in source_bindings.items()), 'Pinned source changed')
        with logfile.open('x', encoding='utf-8') as stream:
            result = subprocess.run([sys.executable, '-B', str(ROOT/'acceleration'/script)]+arguments,
                cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, timeout=manifest['subprocess_wall_seconds'], check=False)
        require(result.returncode == 0, script+' failed; inspect '+key(logfile))
        output_hashes[key(logfile)] = digest(logfile)
        data = collect(result_path)
        steps.append(dict(stage=script, result_path=key(result_path), result_sha256=digest(result_path),
            log_path=key(logfile), log_sha256=digest(logfile)))
        return data
    try:
        for chosen in manifest['selected_candidates']:
            active = chosen['proposal_index']; directory = out/f'index_{active}'; directory.mkdir()
            row = dict(**chosen, audited=False, fixed_K_excluded=False, exact_strict_improvement=False,
                       status='PENDING_LOCAL_EVIDENCE')
            records.append(row)
            print(json.dumps(dict(index=active, event='START')), flush=True)
            require(digest(chosen['candidate_path']) == chosen['candidate_sha256'], 'Selected input changed')
            local = directory/'local'
            gate = execute('check_shortlist_native_pair.py', ['--candidate', chosen['candidate_path'], '--out', key(local)],
                           local/'gate.json', directory/'01_native.log')
            require(gate['status'] == 'NATIVE_SHORTLIST_PAIR_GATE_FINISHED' and
                    key(gate['candidate_path']) == chosen['candidate_path'] and gate['candidate_sha256'] == chosen['candidate_sha256'],
                    'Native gate input differs')
            row.update(gate_path=key(local/'gate.json'), gate_sha256=digest(local/'gate.json'), native_passed=gate['passed'])
            if not gate['passed']:
                row.update(status='PENDING_NATIVE_GATE_FAILED_OR_CAPPED', reason='Native outcomes alone give no independent exclusion')
                continue
            pair_path = local/'independent_pair_audit.json'
            pair = execute('audit_goal_theory_pairs.py', ['--candidate', chosen['candidate_path'], '--domains', key(local/'stars.json'),
                '--pair-certificate', key(local/'pairs.json'), '--out', key(pair_path), '--seconds', str(args.audit_seconds)],
                pair_path, directory/'02_pair_audit.log')
            row.update(independent_pair_audit_path=key(pair_path), independent_pair_audit_sha256=digest(pair_path))
            if pair['status'] != 'INDEPENDENT_EXACT_PAIR_DOMAIN_AUDIT_PASS':
                require(pair['status'] in ('INCOMPLETE_PAIR_SEARCH_NO_EXCLUSION', 'INCOMPLETE_PAIR_AUDIT_NO_EXCLUSION'),
                        'Unexpected independent pair result')
                row.update(status='PENDING_INCOMPLETE_INDEPENDENT_PAIR_AUDIT'); continue
            complete_pair_evidence(pair, chosen, local/'stars.json')
            result_path = directory/'phase1.json'
            result = execute('star_marginal_phase1.py', ['--candidate', chosen['candidate_path'], '--domains', key(local/'stars.json'),
                '--domain-audit', key(pair_path), '--out', key(result_path), '--seconds', str(args.seconds)],
                result_path, directory/'03_star_lp.log')
            require(key(result['candidate_path']) == chosen['candidate_path'] and result['candidate_sha256'] == chosen['candidate_sha256']
                    and key(result['domains_path']) == key(local/'stars.json') and key(result['domain_audit_path']) == key(pair_path),
                    'Star LP input differs')
            row.update(result_path=key(result_path), result_sha256=digest(result_path), numerical_status=result['status'])
            if not all(k in result for k in ('numeric_probabilities', 'numeric_cap_duals', 'numeric_reciprocity_duals')):
                row.update(status='PENDING_NO_STAR_PRIMAL_DUAL'); continue
            audit_path, cert_path, replay_path = directory/'audit.json', directory/'integer_certificate.json', directory/'replay.json'
            audit = execute('audit_star_marginal_phase1.py', ['--result', key(result_path), '--out', key(audit_path),
                '--certificate-out', key(cert_path)], audit_path, directory/'04_star_audit.log')
            require(key(audit['certificate_path']) == key(cert_path) and audit['certificate_sha256'] == digest(cert_path),
                    'Certificate association differs')
            collect(cert_path)
            audit_map = normalized(audit['inputs_sha256'])
            require(audit_map.get(key(result_path)) == digest(result_path) and
                    audit_map.get(chosen['candidate_path']) == chosen['candidate_sha256'], 'Star audit association differs')
            replay = execute('verify_star_marginal_certificate.py', ['--candidate', chosen['candidate_path'], '--domains', key(local/'stars.json'),
                '--domain-audit', key(pair_path), '--certificate', key(cert_path), '--out', key(replay_path)],
                replay_path, directory/'05_integer_replay.log')
            lo, hi = checked_star_interval(audit, replay)
            row.update(status='FIXED_K_EXCLUDED_EXACT_STAR_CERTIFICATE' if lo > 0 else 'PENDING_NONPOSITIVE_EXACT_STAR_BOUND',
                audited=True, fixed_K_excluded=lo > 0, exact_lower=rational(lo), exact_upper=rational(hi),
                audit_path=key(audit_path), audit_sha256=digest(audit_path), certificate_path=key(cert_path), certificate_sha256=digest(cert_path),
                replay_path=key(replay_path), replay_sha256=digest(replay_path),
                exact_strict_improvement=hi < number(manifest['baseline_exact_lower']),
                guaranteed_improvement=rational(number(manifest['baseline_exact_lower'])-hi))
            print(json.dumps(dict(index=active, status=row['status'], star_lower=float(lo), star_upper=float(hi))), flush=True)
        require(all(digest(p) == h for p, h in {**manifest['inputs_sha256'], **output_hashes}.items()), 'Bound evidence changed during evaluation')
        audited = sorted((r for r in records if r['audited']), key=lambda r: (number(r['exact_upper']), r['proposal_index']))
        save(out/'summary.json', dict(status='BOUNDED_CP_STAR_SHORTLIST_EVALUATION_FINISHED', manifest_path=key(out/'manifest.json'),
            manifest_sha256=digest(out/'manifest.json'), inputs_sha256=manifest['inputs_sha256'], outputs_sha256=output_hashes,
            records=records, completed_steps=steps, best=audited[0] if audited else None,
            best_interval_strictly_below_other_audited_intervals=bool(audited) and all(number(audited[0]['exact_upper']) < number(r['exact_lower']) for r in audited[1:]),
            pending_candidates=[r for r in records if not r['fixed_K_excluded']], unselected_eligible_indices=manifest['unselected_eligible_indices'],
            exact_fixed_K_exclusions=sum(r['fixed_K_excluded'] for r in records),
            exact_strict_improvement_count=sum(r['exact_strict_improvement'] for r in records),
            elapsed_seconds=time.perf_counter()-started, SAT_or_DRAT_invocations=0, graph_constructed=False,
            general_nonexistence_proved=False, goal_marked_complete=False,
            scope='Only the selected fixed K. All accepted star bounds use84 independently complete domains and fresh integer replay. Caps and nonpositive bounds remain pending; positive excluded K may serve as search seeds under this distinct objective.'))
    except BaseException as exc:
        save(out/'failure.json', dict(status='CP_STAR_SHORTLIST_EVALUATION_STOPPED', active_index=active,
            error_type=type(exc).__name__, message=str(exc), records=records, completed_steps=steps,
            outputs_sha256=output_hashes, no_exclusion_from_failure=True, graph_constructed=False))
        raise


if __name__ == '__main__':
    main()
