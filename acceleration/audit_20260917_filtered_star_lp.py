"""Exact independent CSR, integer-dual and rational-primal filtered-star audit.

Imports only the separately written third checking path's graph construction,
never the filtered LP producer or its graph/matrix helper.
"""
import argparse
from datetime import datetime, timezone
from fractions import Fraction
import gzip
import json
from math import isfinite, lcm
from pathlib import Path
import platform
import sys
import time

import audit_20260917_fresh_review as independent

OBJECTIVE = 'TRIANGLE_PAIR_FILTERED_STAR_SIMPLEX_V1'
SCOPE = 'TRIANGLE_AND_PAIR_FILTERED_ORIGINAL_ID_DOMAINS'
CONVENTION = 'X_UV_FROM_SMALLER_CURRENT_OUTER_INDEX;RECIPROCITY_SMALLER_MINUS_LARGER'
check, key, path, digest = independent.check, independent.key, independent.path, independent.digest


def qdict(q):
    return dict(numerator=str(q.numerator), denominator=str(q.denominator), approximate=float(q))


def frozen_tables(frozen, original, reduction):
    check(frozen['objective_id'] == OBJECTIVE and frozen['domain_scope'] == SCOPE and
          frozen['original_complete_domains_used'] is False, 'filtered domain scope')
    check([r['outer_vertex'] for r in frozen['domains']] == list(range(84)), 'filtered vertex inventory')
    ids = reduction['surviving_original_domain_ids']
    tables, offsets = [], [0]
    for u, row in enumerate(frozen['domains']):
        check(row['original_domain_ids'] == ids[u] and ids[u] == sorted(set(ids[u])) and ids[u], 'reduction original IDs')
        expected = [int(original['domains'][u]['domain_masks_hex'][i], 16) for i in ids[u]]
        check([int(s, 16) for s in row['domain_masks_hex']] == expected, 'filtered mask/original-ID association')
        check(len(set(expected)) == len(expected), 'duplicate filtered mask')
        table = []
        for mask in expected:
            check(mask >= 0 and mask < 1 << 84 and mask.bit_count() == 8, 'filtered mask shape')
            table.append([v for v in range(84) if mask & (1 << v)])
        tables.append(table); offsets.append(offsets[-1]+len(table))
    check(offsets[-1] == 15335, 'frozen population')
    return tables, offsets


def matrix_rows(tables, offsets, edges, lookup, caps):
    n = offsets[-1]
    rows = [dict() for _ in range(5250)]
    incidence = [[] for _ in edges]
    for cap, (_, terms) in enumerate(caps):
        for edge, coefficient in terms:
            incidence[edge].append((1764+cap, coefficient))
    for u, table in enumerate(tables):
        for i, selected in enumerate(table):
            col = offsets[u]+i
            rows[u][col] = 1
            for v in selected:
                edge = lookup[tuple(sorted((u, v)))]
                rows[84+edge][col] = 1 if u < v else -1
                if u < v:
                    for r, c in incidence[edge]:
                        rows[r][col] = rows[r].get(col, 0)+c
    for r in range(84, 5250):
        rows[r][n+r-84] = -1
    for r in range(84, 1764):
        rows[r][n+5166+r-84] = 1
    rhs = [1]*84+[0]*1680+[b for b, _ in caps]
    return rows, rhs


def validate_model(model, rows, rhs, offsets, edges, caps):
    n = offsets[-1]
    check(model['objective_id'] == OBJECTIVE and model['domain_scope'] == SCOPE and
          model['original_complete_domains_used'] is False and model['projection_convention'] == CONVENTION, 'model scope')
    check(model['shape'] == [5250, n+6846] and model['probability_columns'] == n and model['domain_offsets'] == offsets, 'model dimensions')
    check(model['row_order'] == {'normalization': [0, 84], 'reciprocity': [84, 1764], 'linear_caps': [1764, 5250]}, 'row order')
    check(model['edge_order'] == [list(e) for e in edges], 'unknown edge column order')
    check(model['integer_column_cost'] == [0]*n+[1]*6846 and model['column_lower_bound'] == 0 and
          model['column_upper_bound'] is None, 'column costs/bounds')
    check(model['integer_row_upper_bounds'] == rhs and model['row_lower_bounds'] == rhs[:1764]+[None]*3486, 'row bounds')
    pointers, columns, values = model['csr_indptr'], model['csr_indices'], model['csr_integer_values']
    check(len(pointers) == 5251 and pointers[0] == 0 and pointers[-1] == len(columns) == len(values) and
          all(type(i) is int for i in pointers+columns+values), 'integer CSR dimensions')
    for r, expected in enumerate(rows):
        a, b = pointers[r:r+2]
        check(0 <= a <= b <= len(values), 'CSR pointer range')
        cs, vs = columns[a:b], values[a:b]
        check(cs == sorted(set(cs)) and dict(zip(cs, vs)) == expected, 'independent CSR row differs at '+str(r))
    check(len(model['cap_rows']) == 3486, 'cap metadata count')
    pairs = [(u, v) for u in range(84) for v in range(u+1, 84)]
    for cap, (u, v), (rhs_, terms) in zip(model['cap_rows'], pairs, caps):
        check(cap['kind'] == 'linear_pair_cap' and cap['coordinate'] == [u, v] and cap['target'] == rhs_ and cap['equality'] is False and
              sorted(cap['terms']) == sorted(i for i, c in terms for _ in range(c)), 'cap metadata differs')


def numeric_vector(values, count, low=None, high=None):
    check(type(values) is list and len(values) == count and all(type(v) in (float, int) and isfinite(v) for v in values), 'finite vector dimensions')
    qs = [Fraction(v) for v in values]
    check((low is None or all(q >= low for q in qs)) and (high is None or all(q <= high for q in qs)), 'exact vector bounds')
    return qs


def dual_bound(tables, edges, lookup, caps, scale, beta, gamma):
    check(type(scale) is int and scale > 0 and len(beta) == 1680 and len(gamma) == 3486 and
          all(type(v) is int for v in beta+gamma), 'integer dual dimensions')
    check(all(-scale <= v <= scale for v in beta) and all(0 <= v <= scale for v in gamma), 'integer dual boxes')
    costs = [0]*1680
    for g, (_, terms) in zip(gamma, caps):
        for edge, coefficient in terms: costs[edge] += g*coefficient
    minima, minimizers = [], []
    for u, table in enumerate(tables):
        values = [sum(beta[lookup[u, v]]+costs[lookup[u, v]] if u < v else -beta[lookup[v, u]]
                      for v in selected) for selected in table]
        minima.append(min(values)); minimizers.append(values.index(min(values)))
    rhs = sum(g*b for g, (b, _) in zip(gamma, caps))
    gap = sum(minima)-rhs
    return Fraction(gap, scale), dict(integer_scale=str(scale), integer_reciprocity_weights=list(map(str, beta)),
        integer_cap_weights=list(map(str, gamma)), integer_vertex_minima=list(map(str, minima)),
        minimizing_filtered_domain_ids=minimizers, integer_cap_rhs=str(rhs), integer_gap=str(gap))


def primal_bound(tables, offsets, edges, caps, values):
    probabilities = numeric_vector(values, offsets[-1], low=0)
    marginals = [[Fraction(0) for _ in range(84)] for _ in range(84)]
    for u, table in enumerate(tables):
        ps = probabilities[offsets[u]:offsets[u+1]]
        total = sum(ps)
        check(total > 0, 'zero probability simplex')
        for selected, p in zip(table, ps):
            for v in selected: marginals[u][v] += p/total
    x = [marginals[u][v] for u, v in edges]
    reciprocity = sum(abs(marginals[u][v]-marginals[v][u]) for u, v in edges)
    violation = sum(max(Fraction(0), sum(x[i]*c for i, c in terms)-b) for b, terms in caps)
    return reciprocity+violation, reciprocity, violation


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    bindings = {key(__file__): digest(__file__), key(independent.__file__): digest(independent.__file__), 'uv.lock': digest('uv.lock')}
    def read(p):
        bindings[key(p)] = digest(p)
        return json.loads(path(p).read_bytes())
    def bind_all(d):
        for f, h in d.get('inputs_sha256', {}).items():
            check(digest(f) == h, 'bound prerequisite changed: '+str(f)); bindings[key(f)] = h
    summary = read(args.input/'summary.json'); manifest = read(args.input/'manifest.json'); result = read(args.input/'phase1.json')
    for d in (manifest, result): bind_all(d)
    for f, h in summary['outputs_sha256'].items():
        check(digest(args.input/f) == h, 'producer output changed'); bindings[key(args.input/f)] = h
    check(result['objective_id'] == manifest['objective_id'] == OBJECTIVE and result['domain_scope'] == manifest['domain_scope'] == SCOPE and
          result['original_complete_domains_used'] is False and result['pair_pruned_domains_used'] is True and
          result['projection_convention'] == CONVENTION, 'filtered result objective/scope')
    reduction_review = read(result['reduction_audit_path'])
    check(digest(result['reduction_audit_path']) == result['reduction_audit_sha256'] == '820545f4c4331f7873119b7579b61db9365abc07e57462b5930e4b91d90e16a6', 'independent reduction pin')
    bind_all(reduction_review)
    check(reduction_review['status'] == 'INDEPENDENT_MATCHING_FILTERED_PAIR_PROPAGATION_AND_COMPARISON_PASS' and
          reduction_review['pair_verification']['final_all_directed_pair_closure_checked'] is True, 'sound filtered domain prerequisite')
    candidate = read(result['candidate_path']); frozen = read(result['frozen_domains_path']); reduction = read(result['reduction_path'])
    original = read(frozen['original_domains_path'])
    check(digest(result['candidate_path']) == result['candidate_sha256'] and digest(result['frozen_domains_path']) == result['frozen_domains_sha256'] and
          digest(frozen['original_domains_path']) == frozen['original_domains_sha256'] and
          digest(result['reduction_path']) == result['reduction_sha256'] == frozen['reduction_sha256'], 'frozen input associations')
    tables, offsets = frozen_tables(frozen, original, reduction)
    B, edges, lookup, caps = independent.model(candidate)
    for u, table in enumerate(tables):
        for selected in table:
            check(all(tuple(sorted((u, v))) in lookup for v in selected), 'filtered star edge universe')
            check(all(sum(B[u+15][w]*B[s][w] for w in range(99))+sum(B[s][v+15] for v in selected) ==
                      2-B[u+15][s] for s in range(1, 15)), 'filtered star root quota')
    model = json.loads(gzip.decompress(path(result['exact_model_path']).read_bytes()))
    check(digest(result['exact_model_path']) == result['exact_model_sha256'] and model['domains_sha256'] == digest(result['frozen_domains_path']), 'exact model binding')
    rows, rhs = matrix_rows(tables, offsets, edges, lookup, caps)
    validate_model(model, rows, rhs, offsets, edges, caps)
    control_records = [dict(name='complete_independent_5250_row_integer_CSR_reconstruction', outcome='PASS')]
    # Deliberate in-memory mutations bypass file hash protection; restored after rejection.
    first_slack_position = next(i for i, col in enumerate(model['csr_indices']) if col >= offsets[-1])
    old = model['csr_integer_values'][first_slack_position]
    model['csr_integer_values'][first_slack_position] = -old
    try:
        validate_model(model, rows, rhs, offsets, edges, caps)
    except ValueError as e:
        control_records.append(dict(name='wrong_slack_sign', outcome='REJECT', reason=str(e)))
    else: raise ValueError('slack sign corruption accepted')
    finally: model['csr_integer_values'][first_slack_position] = old
    old = model['integer_row_upper_bounds'][1764]; model['integer_row_upper_bounds'][1764] += 1
    try:
        validate_model(model, rows, rhs, offsets, edges, caps)
    except ValueError as e:
        control_records.append(dict(name='wrong_cap_rhs', outcome='REJECT', reason=str(e)))
    else: raise ValueError('cap RHS corruption accepted')
    finally: model['integer_row_upper_bounds'][1764] = old
    old = frozen['domains'][0]['original_domain_ids'][0]; frozen['domains'][0]['original_domain_ids'][0] = -1
    try:
        frozen_tables(frozen, original, reduction)
    except ValueError as e:
        control_records.append(dict(name='wrong_filtered_original_ID', outcome='REJECT', reason=str(e)))
    else: raise ValueError('filtered-ID corruption accepted')
    finally: frozen['domains'][0]['original_domain_ids'][0] = old
    beta_q = numeric_vector(result['numeric_reciprocity_duals'], 1680, -1, 1)
    gamma_q = numeric_vector(result['numeric_cap_duals'], 3486, 0, 1)
    scale = lcm(*(q.denominator for q in beta_q+gamma_q))
    beta = [int(q*scale) for q in beta_q]; gamma = [int(q*scale) for q in gamma_q]
    lower, certificate = dual_bound(tables, edges, lookup, caps, scale, beta, gamma)
    upper, reciprocal_merit, cap_merit = primal_bound(tables, offsets, edges, caps, result['numeric_probabilities'])
    check(0 < lower <= upper, 'positive exact filtered interval')
    zero, _ = dual_bound(tables, edges, lookup, caps, 1, [0]*1680, [0]*3486)
    check(zero == 0, 'zero dual must not exclude')
    control_records.append(dict(name='zero_dual_is_bound_not_exclusion', outcome='PASS'))
    scaled, _ = dual_bound(tables, edges, lookup, caps, scale*10**30, [v*10**30 for v in beta], [v*10**30 for v in gamma])
    check(scaled == lower, 'integer scaling invariance')
    control_records.append(dict(name='integer_scale_10_to_30_preserves_bound', outcome='PASS'))
    bad_gamma = gamma[:]; bad_gamma[0] = -1
    try: dual_bound(tables, edges, lookup, caps, scale, beta, bad_gamma)
    except ValueError as e: control_records.append(dict(name='negative_cap_weight', outcome='REJECT', reason=str(e)))
    else: raise ValueError('negative cap weight accepted')
    bad = result['numeric_probabilities'][:]; bad[:offsets[1]] = [0]*offsets[1]
    try: primal_bound(tables, offsets, edges, caps, bad)
    except ValueError as e: control_records.append(dict(name='zero_probability_simplex', outcome='REJECT', reason=str(e)))
    else: raise ValueError('zero probability simplex accepted')
    check(all(digest(f) == h for f, h in bindings.items()), 'input/source changed')
    certificate.update(status='EXACT_FILTERED_STAR_SIMPLEX_DUAL_CERTIFICATE', objective_id=OBJECTIVE,
        domain_scope=SCOPE, original_complete_domains_used=False, candidate_path=result['candidate_path'], candidate_sha256=result['candidate_sha256'],
        frozen_domains_path=result['frozen_domains_path'], frozen_domains_sha256=result['frozen_domains_sha256'],
        reduction_audit_path=result['reduction_audit_path'], reduction_audit_sha256=result['reduction_audit_sha256'],
        exact_lower=qdict(lower), fixed_K_excluded=True, no_general_nonexistence_claim=True,
        proof='Weighted simplex support minima minus nonnegative cap RHS bound the sum of absolute reciprocity and positive cap residuals. Every target completion survives the independently sound reductions, hence would give zero residual.')
    cp = args.out/'integer_certificate.json'
    with cp.open('x', encoding='utf-8') as f: json.dump(certificate, f, indent=2); f.write('\n')
    report = dict(status='INDEPENDENT_EXACT_FILTERED_STAR_MODEL_PRIMAL_DUAL_PASS',
        timestamp=datetime.now(timezone.utc).isoformat(), source_commit=manifest['source_commit'], source_additions_explicitly_hashed=True,
        command=[sys.executable]+sys.argv, working_directory=str(Path.cwd()), python=platform.python_version(), inputs_sha256=bindings,
        claim_binding=dict(id='C-FILTERED-STAR-LP-18481', revision=1, recommendation='VERIFIED',
            statement='For the fixed baseline18481 assignment, the TRIANGLE_PAIR_FILTERED_STAR_SIMPLEX_V1 optimum over all15335 independently sound filtered original-ID masks lies in the exact interval recorded here; the positive lower endpoint is a fixed-K obstruction.',
            dependencies=[dict(id='C-STAR-MATCHING-PAIR-18481', revision=1, relation='uses_result')]),
        objective_id=OBJECTIVE, domain_scope=SCOPE, original_complete_domains_used=False, filtered_probability_columns=offsets[-1],
        model_rows_checked=5250, augmented_columns_checked=len(model['integer_column_cost']), integer_nonzeros_checked=len(model['csr_integer_values']),
        cap_metadata_rows_checked=3486, normalizations_checked=84, exact_lower=qdict(lower), exact_upper=qdict(upper),
        exact_gap=qdict(upper-lower), exact_primal_reciprocity=qdict(reciprocal_merit), exact_primal_cap_merit=qdict(cap_merit),
        numeric_hint_discrepancies_diagnostic_only=dict(lower=float(lower)-result['numeric_simplex_dual_lower'], upper=float(upper)-result['numeric_objective']),
        certificate_path=key(cp), certificate_sha256=digest(cp), controls=control_records,
        checking_path='Independent full99 known adjacency and matrix-entry cap coefficients; complete integer CSR reconstruction; integer simplex support certificate and rationally normalized primal evaluation',
        shared_trusted_components=['Python standard library','previous third-checker independent graph construction only','hash-bound independent matching/pair reduction proof'],
        producer_or_solver_imported=False, solver_executed=False, original_objective_comparison_performed=False,
        limitations=['New objective domain is strictly filtered; interval is not directly comparable as performance to the original-domain objective.',
                    'Baseline assignment already excluded; this supplies another obstruction for it, not a new unrestricted exclusion.',
                    'HiGHS optimality, raw solver residuals and native performance are not asserted by this exact certificate check.'],
        elapsed_seconds=time.perf_counter()-started, target_resolution='UNKNOWN', overall_search_coverage='UNKNOWN; no validated denominator')
    with (args.out/'audit.json').open('x', encoding='utf-8') as f: json.dump(report, f, indent=2); f.write('\n')
    print(json.dumps(dict(status=report['status'], lower=float(lower), upper=float(upper), gap=float(upper-lower), rows=5250)))


if __name__ == '__main__':
    main()
