"""Evaluate a fixed-dual shortlist outside an entire audited CP inventory.

The native fixed-dual value is only an ordering hint. No CP near-zero status,
edge-LP result, feasibility, or exclusion is inferred for newly selected K.
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

import evaluate_cp_star_shortlist_v2 as frozen
from audit_certificate import full_graph

ROOT = frozen.ROOT
PINS = dict(frozen.PINS)
PINS['evaluate_cp_star_shortlist_v2.py'] = '83cc10e42923ea5dfd6e39b81bee4ad19585539639045a03f9c812c97eac19ae'
ROOT_PINS = frozen.ROOT_PINS
require, resolve, key, digest, load, save = (frozen.require, frozen.resolve, frozen.key,
    frozen.digest, frozen.load, frozen.save)
number, rational, normalized = frozen.number, frozen.rational, frozen.normalized
complete_pair_evidence, checked_star_interval = frozen.complete_pair_evidence, frozen.checked_star_interval


def graph_key(edges):
    require(type(edges) is list and len(edges) == 168, 'Expected168 overlap edges')
    require(all(type(e) is list and len(e) == 2 and all(type(v) is int for v in e) and
                0 <= e[0] < e[1] < 84 for e in edges), 'Noncanonical overlap edge')
    require(edges == sorted(edges) and len(set(map(tuple, edges))) == 168, 'Unsorted/duplicate overlap edge')
    return bytes(v for pair in edges for v in pair)


def select_records(ranking, comparison, family, family_audit, scores, cp, cp_audit, cp_candidates):
    """Pure selection/association guard; mutated structures can test semantics."""
    require(ranking['status'] == 'HEURISTIC_FIXED_STAR_DUAL_FAMILY_RANKING_FINISHED', 'Unfinished ranking')
    require(comparison['status'] == 'FIXED_STAR_DUAL_CP_SELECTION_COMPARISON', 'Wrong comparison status')
    require(family['status'] == 'COMPLETE_CROSS_ATOMIC_CYCLE_SUBFAMILY_EXTRACTION' and
            family['selector'] == 'cross_3_4' and family['cycle_sizes'] == [3, 4], 'Unsupported family')
    require(family_audit['status'] == 'INDEPENDENT_COMPLETE_CROSS_ATOMIC_CYCLE_EXTRACTION_PASS' and
            family_audit['all_original_native_indices_and_final_graphs_checked'] is True and
            family_audit['all_cycles_min_vertex_removed_first_checked'] is True, 'Unaudited family')
    count = len(family['overlap_candidates'])
    require(count == family['legal_count'] == family_audit['legal_count'] == ranking['candidate_count'] ==
            comparison['candidate_count'] == scores['candidate_count'] == cp['coarse_candidate_count'] and
            len(family['moves']) == len(family['original_native_indices']) == count, 'Family inventory mismatch')
    require(family['by_class'] == family_audit['by_class'], 'Family coordinate counts differ')
    keys = [graph_key(edges) for edges in family['overlap_candidates']]
    require(len(set(keys)) == count, 'Duplicate final graph in family')
    # Reuse only the frozen inventory/association checks, not its near-zero
    # selection. Every audited CP record is excluded, regardless of its merit.
    frozen.select_records(cp, cp_audit)
    require(cp['probes'] == len(cp['records']) == len(cp_candidates) == 64 and
            comparison['cp_selected_count'] == 64, 'All64 CP candidates required')
    require(key(cp['paths']['native']) == key(ranking['family_path']) and
            cp['family_association']['native_sha256'] == ranking['family_sha256'], 'Different CP/ranking family')
    excluded_indices, excluded_keys = set(), set()
    for row, candidate in zip(cp['records'], cp_candidates):
        index = row['proposal_index']
        require(type(index) is int and 0 <= index < count and index not in excluded_indices, 'Bad CP family index')
        candidate_key = graph_key(candidate['overlap_edges_outer_zero_based'])
        require(candidate_key == keys[index], 'CP candidate/family graph association differs')
        excluded_indices.add(index); excluded_keys.add(candidate_key)
    require(len(excluded_keys) == 64, 'Duplicate exact CP graph')
    require(scores['status'] == 'HEURISTIC_FIXED_STAR_DUAL_BATCH_FINISHED' and
            len(scores['results']) == count and scores['scores_are_certificates'] is False,
            'Wrong native score inventory or scope')
    ranked = ranking['ranked']
    rank_indices = set()
    denominator = None
    for row in ranked:
        index = row['index']
        require(type(index) is int and 0 <= index < count and index not in rank_indices, 'Bad/duplicate rank index')
        rank_indices.add(index)
        value, move = scores['results'][index], family['moves'][index]
        require(value['status'] == 'COMPLETE_HEURISTIC_SCORE' and value['complete_domain_enumeration'] is True and
                value['local_empty_count'] == 0 and len(value['domain_counts']) == 84 and
                all(type(n) is int and n > 0 for n in value['domain_counts']), 'Unavailable native score ranked')
        require(type(row['score_numerator']) is int and type(row['denominator']) is int and row['denominator'] > 0 and
                row['score_numerator'] == value['score_numerator'] and row['denominator'] == value['denominator'],
                'Ranking score/native association differs')
        denominator = row['denominator'] if denominator is None else denominator
        require(row['denominator'] == denominator, 'Numerator order requires a common positive denominator')
        require(row['original_native_index'] == family['original_native_indices'][index] == move['original_native_index'] and
                row['root_group'] == move['root_group'] and row['cycle_size'] == move['cycle_size'] and
                move['matching_class'] == 'cross', 'Ranking move association differs')
    require(ranked == sorted(ranked, key=lambda r: (r['score_numerator'], r['index'])), 'Incorrect exact rank order')
    available = {i for i, r in enumerate(scores['results']) if r['status'] == 'COMPLETE_HEURISTIC_SCORE'}
    require(rank_indices == available and ranking['complete_scores'] == len(ranked) and
            ranking['unavailable_scores'] == count-len(ranked), 'Missing available native score')
    positions = {r['index']: i+1 for i, r in enumerate(ranked)}
    expected_cp = [dict(index=i, rank=positions.get(i)) for i in sorted(excluded_indices)]
    require(comparison['cp_candidates_with_fixed_dual_rank'] == expected_cp, 'Comparison CP inventory differs')
    eligible = [r for r in ranked if keys[r['index']] not in excluded_keys]
    require(comparison['first32_fixed_dual_candidates_outside_cp_selection'] == eligible[:32],
            'Comparison suggested inventory/order differs')
    require(len(eligible) >= 16, 'Fewer than16 eligible ranked candidates')
    return eligible, sorted(excluded_indices)


def candidate_bytes(document):
    return (json.dumps(document, indent=2, allow_nan=False)+'\n').encode('utf-8')


def preflight(args):
    require(sys.version_info[:2] == (3, 12), 'Use .venv/Scripts/python.exe')
    require(resolve(args.out).is_relative_to(ROOT) and not resolve(args.out).exists(), 'Use a fresh workspace output')
    require(type(args.max_candidates) is int and 1 <= args.max_candidates <= 16 and
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
    ranking, comparison = read(args.ranking), read(args.comparison)
    family, family_audit = read(args.family), read(args.family_audit)
    cp_path = resolve(args.cp_run)/'summary.json'
    cp_audit_path = resolve(args.cp_run)/'audit.json'
    cp, cp_audit = read(cp_path), read(cp_audit_path)
    family_hash = bind(args.family)
    require(key(ranking['family_path']) == key(args.family) and ranking['family_sha256'] == family_hash,
            'Ranking is bound to another family')
    require(normalized(family_audit['inputs_sha256']).get(key(args.family)) == family_hash and
            normalized(cp_audit['inputs_sha256']).get(key(cp_path)) == bind(cp_path), 'Independent report association differs')
    comparison_inputs = normalized(comparison['inputs_sha256'])
    require(comparison_inputs.get(key(args.ranking)) == bind(args.ranking) and
            comparison_inputs.get(key(cp_path)) == bind(cp_path), 'Comparison input association differs')
    rank_inputs = normalized(ranking['inputs_sha256'])
    scores_path = resolve(args.ranking).with_name('scores.json')
    scores = read(scores_path)
    require(rank_inputs.get(key(scores_path)) == bind(scores_path) and
            rank_inputs.get(key(args.family_audit)) == bind(args.family_audit), 'Ranking native/family proof association differs')
    cp_candidates = []
    for row in cp['records']:
        bind(row['candidate_path'], row['candidate_sha256'])
        cp_candidates.append(load(row['candidate_path']))
    eligible, excluded = select_records(ranking, comparison, family, family_audit, scores, cp, cp_audit, cp_candidates)
    baseline = read(args.baseline_star_audit)
    require(baseline['status'] == 'INDEPENDENT_EXACT_STAR_MARGINAL_PHASE1_AUDIT_PASS', 'Unaudited star baseline')
    lower, upper = number(baseline['exact_dual_lower']), number(baseline['exact_primal_upper'])
    require(0 < lower <= upper and baseline['positive_exact_dual_excludes_fixed_K'] is True, 'Positive exact star baseline required')
    cert = read(baseline['certificate_path'])
    bind(baseline['certificate_path'], baseline['certificate_sha256'])
    require(cert['fixed_K_excluded'] is True and number(cert['exact_phase1_lower_bound']) == lower, 'Baseline certificate differs')
    base_inputs = normalized(baseline['inputs_sha256'])
    require(base_inputs.get(key(family['candidate_path'])) == bind(family['candidate_path'], family['candidate_sha256']) and
            rank_inputs.get(key(args.baseline_star_audit)) == bind(args.baseline_star_audit), 'Baseline/family/rank association differs')
    for name in ('star_marginal_phase1.py', 'audit_star_marginal_phase1.py'):
        require(base_inputs.get(key(ROOT/'acceleration'/name)) == PINS[name], 'Baseline star objective differs')
    chosen = []
    for row in eligible[:args.max_candidates]:
        index = row['index']
        document = dict(status='FIXED_STAR_DUAL_SHORTLIST_CANDIDATE', proposal_index=index,
            overlap_edges_outer_zero_based=family['overlap_candidates'][index],
            family_path=key(args.family), family_sha256=family_hash,
            ranking_path=key(args.ranking), ranking_sha256=bind(args.ranking),
            ranking_score_numerator=row['score_numerator'], ranking_score_denominator=row['denominator'],
            score_used_only_for_ordering=True, edge_LP_status='NOT_EVALUATED_BY_THIS_PIPELINE',
            graph_constructed=False, fixed_K_excluded=False)
        full_graph(document)
        payload = candidate_bytes(document)
        chosen.append(dict(proposal_index=index, fixed_dual_rank=next(i+1 for i, r in enumerate(ranking['ranked']) if r['index'] == index),
            fixed_dual_score_numerator=row['score_numerator'], fixed_dual_score_denominator=row['denominator'],
            candidate_path=key(resolve(args.out)/f'index_{index}'/'candidate.json'), candidate_sha256=sha256(payload).hexdigest(),
            candidate_document=document, original_native_index=row['original_native_index'],
            root_group=row['root_group'], cycle_size=row['cycle_size']))
    require(all(digest(name) == expected for name, expected in inputs.items()), 'Input changed during preflight')
    return dict(status='FIXED_STAR_DUAL_SHORTLIST_EVALUATION_MANIFEST', inputs_sha256=inputs,
        ranking_path=key(args.ranking), ranking_sha256=bind(args.ranking), comparison_path=key(args.comparison),
        comparison_sha256=bind(args.comparison), family_path=key(args.family), family_sha256=family_hash,
        family_audit_path=key(args.family_audit), family_audit_sha256=bind(args.family_audit),
        excluded_CP_summary_path=key(cp_path), excluded_CP_summary_sha256=bind(cp_path),
        excluded_CP_audit_path=key(cp_audit_path), excluded_CP_audit_sha256=bind(cp_audit_path),
        excluded_CP_indices=excluded, excluded_exact_CP_graphs=64,
        baseline_star_audit_path=key(args.baseline_star_audit), baseline_star_audit_sha256=bind(args.baseline_star_audit),
        baseline_exact_lower=rational(lower), baseline_exact_upper=rational(upper), eligible_candidates=len(eligible),
        selected_candidates=chosen, max_candidates=args.max_candidates,
        unselected_eligible_indices=[r['index'] for r in eligible[args.max_candidates:]],
        unavailable_native_scores=ranking['unavailable_scores'],
        selection_rule='Ascending exact common-denominator score numerator then family index, excluding every exact graph in all64 audited CP records; take at most16.',
        native_scores_are_exclusion_certificates=False, CP_nearzero_eligibility_assumed=False,
        native_star_seconds=30, native_star_node_cap=2000000, native_star_domain_cap=20000,
        native_pair_seconds=30, native_pair_check_cap=500000000, independent_pair_seconds=args.audit_seconds,
        per_star_LP_seconds=args.seconds, subprocess_wall_seconds=180+max(args.seconds, args.audit_seconds),
        merit='STAR_SIMPLEX_RECIPROCITY_PLUS_LINEAR_CAP_VIOLATIONS', old_edge_merit_comparison=False,
        exact_edge_LP_feasibility_claimed=False, SAT_or_DRAT_invocations=0,
        graph_constructed=False, general_nonexistence_proved=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ranking', type=Path, required=True)
    parser.add_argument('--comparison', type=Path, required=True)
    parser.add_argument('--family', type=Path, required=True)
    parser.add_argument('--family-audit', type=Path, required=True)
    parser.add_argument('--cp-run', type=Path, required=True)
    parser.add_argument('--baseline-star-audit', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--max-candidates', type=int, default=16)
    parser.add_argument('--seconds', type=float, default=30)
    parser.add_argument('--audit-seconds', type=float, default=60)
    parser.add_argument('--validate-only', action='store_true')
    args = parser.parse_args()
    manifest = preflight(args)
    if args.validate_only:
        print(json.dumps(dict(status='FIXED_STAR_DUAL_SHORTLIST_READ_ONLY_PREFLIGHT_PASS', eligible=manifest['eligible_candidates'],
            selected=len(manifest['selected_candidates']), selected_indices=[r['proposal_index'] for r in manifest['selected_candidates']], excluded_CP_graphs=64, output_created=False, processes_launched=0)), flush=True)
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
            destination = resolve(chosen['candidate_path'])
            require(destination.parent.parent == out, 'Candidate destination escaped output')
            destination.parent.mkdir()
            with destination.open('xb') as stream:
                stream.write(candidate_bytes(chosen['candidate_document']))
            require(digest(destination) == chosen['candidate_sha256'], 'Candidate materialization differs')
            output_hashes[key(destination)] = digest(destination)
        for chosen in manifest['selected_candidates']:
            active = chosen['proposal_index']; directory = out/f'index_{active}'
            row = dict(**{k:v for k,v in chosen.items() if k != 'candidate_document'}, audited=False, fixed_K_excluded=False, exact_strict_improvement=False,
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
        save(out/'summary.json', dict(status='BOUNDED_FIXED_STAR_DUAL_SHORTLIST_EVALUATION_FINISHED', manifest_path=key(out/'manifest.json'),
            manifest_sha256=digest(out/'manifest.json'), inputs_sha256=manifest['inputs_sha256'], outputs_sha256=output_hashes,
            records=records, completed_steps=steps, best=audited[0] if audited else None,
            best_interval_strictly_below_other_audited_intervals=bool(audited) and all(number(audited[0]['exact_upper']) < number(r['exact_lower']) for r in audited[1:]),
            pending_candidates=[r for r in records if not r['fixed_K_excluded']], unselected_eligible_indices=manifest['unselected_eligible_indices'],
            exact_fixed_K_exclusions=sum(r['fixed_K_excluded'] for r in records),
            exact_strict_improvement_count=sum(r['exact_strict_improvement'] for r in records),
            elapsed_seconds=time.perf_counter()-started, SAT_or_DRAT_invocations=0, graph_constructed=False,
            general_nonexistence_proved=False, goal_marked_complete=False,
            native_scores_are_exclusion_certificates=False, CP_nearzero_eligibility_assumed=False, edge_LP_runs=0,
            scope='Only selected fixed K outside all64 prior CP graphs. Fixed-dual scores are ordering hints only. All accepted star bounds use84 independently complete domains and fresh integer replay. Caps and nonpositive bounds remain pending; positive excluded K may serve as search seeds under this distinct objective.'))
    except BaseException as exc:
        save(out/'failure.json', dict(status='FIXED_STAR_DUAL_SHORTLIST_EVALUATION_STOPPED', active_index=active,
            error_type=type(exc).__name__, message=str(exc), records=records, completed_steps=steps,
            outputs_sha256=output_hashes, no_exclusion_from_failure=True, graph_constructed=False))
        raise


if __name__ == '__main__':
    main()
