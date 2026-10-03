"""Independent complete selected-lift matrix and exact rational primal audit.

No project/producer/checker imports. Enumerate balanced word triples directly,
rather than the producer's ordered S3 arrays, then count literal Gram products.
"""
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction
from itertools import combinations, combinations_with_replacement, product
from pathlib import Path
import argparse
import hashlib
import json
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
B = 'acceleration/results/20260930_'
I = B + 'independent_review/'
D = B + 'hadamard_support_cut_lift_matrix/'
RAW = B + 'hadamard20_support/six_prism.json'
GATE = I + 'hadamard_parity_support_cuts_sat/summary.json'
PROJECTION = I + 'hadamard_parity_support_cuts_sat/independent_projection.json'
PINS = {
    RAW: 'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',
    GATE: '02ae20d479a0d2589c02f435e2a8fdd781ec0459b60095d130b68b5f2721a04a',
    PROJECTION: 'f43ad5f79d6fc8c8f6825f52d0140a07852a873207642b4edb7c035cb5ed4a8c',
    D + 'exact_model.json': 'cdedc77904ba8cfc8b3a12d1da876cd55c87e85fd85427caf6c2d766715b493b',
    D + 'scope.json': '9c4723d00e7788b1aea471c604b9d7e4b38545da83ce0467e4e6c0b71642715a',
    D + 'uniform_primal.json': '7b4cba322b7dc84c63f0779bcc5f4858a30e3f47aaba90c3ff03f6f1de23c585',
}


def need(ok, text):
    if not ok:
        raise ValueError(text)


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, obj):
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(obj, stream, indent=2)
        stream.write('\n')


def local_catalog():
    # Exhaust all 3^6 words; then every increasing triple of the 90 balanced words.
    words = [w for w in product(range(3), repeat=6) if Counter(w) == {0: 2, 1: 2, 2: 2}]
    triples = []
    population = 0
    for indices in combinations(range(len(words)), 3):
        population += 1
        ws = [words[i] for i in indices]
        if not all({w[a] for w in ws} == {0, 1, 2} for a in range(6)):
            continue
        signs = [sum(ws[j][a] > ws[k][a] for j, k in combinations(range(3), 2)) % 2 for a in range(6)]
        triples.append(dict(word_indices=list(indices), words=[list(w) for w in ws],
                            pattern=[s ^ signs[0] for s in signs]))
    need(len(words) == 90 and population == 117480 and len(triples) == 150, 'complete finite local universe')
    counts = Counter(tuple(t['pattern']) for t in triples)
    need(counts[(0,) * 6] == 30 and sorted(counts.values()) == [12] * 10 + [30], 'S3 parity classification')
    return words, triples, population


def geometry(raw):
    c = raw['core_adjacency']
    need(len(c) == 36 and all(len(r) == 36 for r in c), 'core dimensions')
    expected = [[int((a // 12 == b // 12 and (a % 12) ^ 1 == b % 12)
                     or (a // 12 != b // 12 and a % 12 == b % 12)) for b in range(36)] for a in range(36)]
    need(c == expected, 'literal fixed six-prism geometry')
    # Each core row has its own triangle vertex as one further known neighbor.
    g = [[12 * int(a == b) - c[a][b] + 2 - int(a // 12 == b // 12)
          - sum(c[a][z] * c[b][z] for z in range(36)) for b in range(36)] for a in range(36)]
    need(g == raw['prescribed_Gram36'], 'every raw-core prescribed Gram coefficient')
    l = raw['L']
    need(len(l) == 12 and all(len(r) == 60 and all(type(v) is int and v in [0, 1] for v in r) for r in l), 'binary support dimensions')
    groups = []
    for col in range(60):
        support = [a for a in range(12) if l[a][col]]
        need(len(support) == 6 and len({a // 2 for a in support}) == 6, 'one endpoint of every matching pair')
        previous = next((x for x in groups if x['support'] == support), None)
        if previous is None:
            groups.append(dict(support=support, columns=[col]))
        else:
            previous['columns'].append(col)
    need(len(groups) == 20 and all(len(x['columns']) == 3 for x in groups), 'complete support partition')
    return g, groups


def reconstruct(groups, triples, patterns, gram):
    rowpairs = [p for p in combinations(range(36), 2) if gram[p[0]][p[1]] > 0]
    need(len(rowpairs) == 540, 'positive off-diagonal Gram population')
    columns, selectors, domains, literal = [], [], [], []
    for group, data in enumerate(groups):
        pattern = patterns[group] if patterns is not None else None
        choices = [t for t in triples if pattern is None or t['pattern'] == pattern]
        need(choices, 'nonempty exact filtered domain')
        domains.append(choices)
        for choice, t in enumerate(choices):
            rs = [sorted(data['support'][a] + 12 * w[a] for a in range(6)) for w in t['words']]
            count = Counter(p for rows in rs for p in combinations_with_replacement(rows, 2))
            need(all(v == 1 for v in count.values()), 'binary literal triple Gram coefficients')
            need(all(gram[a][b] > 0 for a, b in count), 'all omitted zero Gram rows satisfied')
            col = [group] + [20 + i for i, pair in enumerate(rowpairs) if pair in count]
            need(len(col) == 46, 'exact sparse coefficient count')
            columns.append(col)
            selectors.append([group, choice])
            literal.append(dict(group=group, choice=choice, rows=rs, counts=count))
    rhs = [1] * 20 + [gram[a][b] for a, b in rowpairs]
    return columns, rhs, selectors, domains, literal, rowpairs


def exact_primal(columns, rhs, numerators, denominator):
    need(type(denominator) is int and denominator > 0, 'positive integer denominator')
    need(len(numerators) == len(columns) and all(type(n) is int and n >= 0 for n in numerators), 'nonnegative rational vector')
    sums = [0] * len(rhs)
    for n, col in zip(numerators, columns):
        need(len(set(col)) == len(col) and all(type(r) is int and 0 <= r < len(rhs) for r in col), 'binary sparse column')
        for row in col:
            sums[row] += n
    need(sums == [denominator * b for b in rhs], 'all exact integer-scaled primal equations')
    return sums


def check_domains(saved, domains, groups, triples, patterns):
    need(len(saved) == 20, 'all twenty domains')
    offset = 0
    for group, (record, choices) in enumerate(zip(saved, domains, strict=True)):
        need(record['group'] == group and record['support_coordinates'] == groups[group]['support']
             and record['raw_columns'] == groups[group]['columns'] and record['selected_parity_pattern'] == patterns[group], 'domain alignment')
        need(len(record['choices']) == len(choices), 'exhaustive local choices')
        for j, (item, choice) in enumerate(zip(record['choices'], choices, strict=True)):
            rows = [sorted(groups[group]['support'][a] + 12 * w[a] for a in range(6)) for w in choice['words']]
            need(item['selector'] == offset + j + 1 and item['choice_index'] == j
                 and item['balanced_triple_index'] == triples.index(choice), 'selector/catalog identity')
            need(item['word_indices'] == choice['word_indices'] and item['color_words'] == choice['words']
                 and item['lifted_rows'] == rows, 'literal local factor option')
            need([int(x, 16) for x in item['lifted_masks_hex']] == [sum(1 << a for a in row) for row in rows], 'raw masks')
        offset += len(choices)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    pins, corruptions = {}, []

    def load(p, sha=None):
        value = digest(ROOT / p)
        need(sha is None or sha == value, 'artifact identity: ' + p)
        pins[p] = value
        return json.loads((ROOT / p).read_bytes())

    def pin(p, sha=None):
        value = digest(ROOT / p)
        need(sha is None or sha == value, 'artifact identity: ' + p)
        pins[p] = value

    def reject(name, action):
        try:
            action()
        except (ValueError, TypeError, KeyError, IndexError):
            corruptions.append(name)
        else:
            raise ValueError('corruption accepted: ' + name)

    try:
        for p, sha in PINS.items():
            pin(p, sha)
        gate = load(GATE)
        need(gate['status'] == 'INDEPENDENT_HADAMARD_PARITY_SUPPORT_CUT_SAT_OBJECT_PASS', 'selected projection gate')
        need(gate['outputs_sha256'][PROJECTION] == PINS[PROJECTION], 'gate binds raw selected projection')
        summary = load(D + 'summary.json')
        for field in ['inputs_sha256', 'outputs_sha256']:
            for p, sha in summary[field].items():
                pin(p, sha)
        raw, projection = load(RAW), load(PROJECTION)
        gram, groups = geometry(raw)
        words, triples, population = local_catalog()
        patterns = projection['selected_group_parity_patterns']
        need(len(patterns) == 20 and all(p[0] == 0 and sum(p) == 3 for p in patterns), 'twenty mixed patterns')
        for g, group in enumerate(groups):
            need(projection['group_records'][g]['support'] == group['support'], 'projection raw support alignment')
        # Positive exact full-geometry relaxation before inspecting the candidate certificate.
        allcols, allrhs, _, _, _, _ = reconstruct(groups, triples, None, gram)
        exact_primal(allcols, allrhs, [1] * 3000, 150)
        exact_primal([[0], [0]], [1], [1, 1], 2)
        reject('uniform_control_wrong_denominator', lambda: exact_primal(allcols, allrhs, [1] * 3000, 149))
        reject('negative_weight', lambda: exact_primal([[0], [0]], [1], [-1, 3], 2))
        reject('zero_denominator', lambda: exact_primal([[0], [0]], [1], [1, 1], 0))
        reject('float_numerator', lambda: exact_primal([[0], [0]], [1], [1.0, 1], 2))
        cols, rhs, selectors, domains, literal, rowpairs = reconstruct(groups, triples, patterns, gram)
        need(len(cols) == 240 and len(rhs) == 560 and list(map(len, domains)) == [12] * 20, 'selected full matrix dimensions')
        model, scope, cert = load(D + 'exact_model.json'), load(D + 'scope.json'), load(D + 'uniform_primal.json')
        need(model['columns_nonzero_row_indices'] == cols and model['rhs'] == rhs and model['selectors'] == selectors, 'all exact matrix entries and indexing')
        need(model['variables'] == 240 and model['equations'] == 560 and model['binary_coefficients'] is True
             and model['nonnegative_variables'] is True and model['relaxation_only'] is True, 'continuous model scope')
        need(model['scope_sha256'] == PINS[D + 'scope.json'], 'model binds scope')
        need(scope['raw_support'] == RAW and scope['raw_support_sha256'] == PINS[RAW]
             and scope['projection'] == PROJECTION and scope['projection_sha256'] == PINS[PROJECTION]
             and scope['actual_projection_gate'] == GATE and scope['actual_projection_gate_sha256'] == PINS[GATE], 'exact selected source scope')
        need(scope['L'] == raw['L'] and scope['core_adjacency'] == raw['core_adjacency']
             and scope['target_gram36'] == gram and scope['matchings'] == raw['matchings']
             and scope['selected_pattern_indices'] == projection['selected_pattern_indices'], 'raw scope geometry/patterns')
        need(scope['one_fixed_parity_branch'] and scope['balance_is_extra_assumption']
             and not scope['all_balanced_branches_covered'] and not scope['residual_D_encoded'] and not scope['target_graph'], 'explicit restricted scope')
        check_domains(scope['domains'], domains, groups, triples, patterns)
        saved_catalog = load(D + 'local_triples.json')
        need(saved_catalog['triples'] == [t['words'] for t in triples]
             and saved_catalog['sorted_balanced'] == 150 and saved_catalog['labeled_balanced'] == 6 * 150
             and saved_catalog['enumerated_coordinate_permutation_tuples'] == 6 ** 6, 'complete saved S3 catalog')
        rowmeta = []
        for row in range(560):
            inputs = [j + 1 for j, col in enumerate(cols) if row in col]
            rowmeta.append(dict(kind='group_exactone', group=row, target=rhs[row], inputs=inputs) if row < 20
                           else dict(kind='gram_count', rows=list(rowpairs[row - 20]), target=rhs[row], inputs=inputs))
        need(model['row_metadata'] == rowmeta, 'all row constraints and literal domains')
        allgram = []
        for pair in combinations_with_replacement(range(36), 2):
            a, b = pair
            inputs = [j + 1 for j, item in enumerate(literal) if item['counts'][pair]]
            allgram.append(dict(rows=[a, b], target=gram[a][b], inputs=inputs))
            if a == b:
                expected_inputs = [j + 1 for j, item in enumerate(literal) if a % 12 in groups[item['group']]['support']]
                need(inputs == expected_inputs and len(set(literal[j - 1]['group'] for j in inputs)) == gram[a][a] == 10,
                     'omitted diagonal is sum of ten group normalizations')
            elif gram[a][b] == 0:
                need(not inputs, 'omitted zero row identically zero')
        need(load(D + 'all_gram_rows.json') == allgram, 'all 666 literal Gram rows')
        coverage = load(D + 'row_coverage.json')
        need(coverage['required_rows'] == 560 and coverage['zero_required_rows'] == []
             and coverage['available_selector_counts'] == [len(r['inputs']) for r in rowmeta], 'complete nonzero row census')
        need(cert['kind'] == 'CANDIDATE_EXACT_RATIONAL_PRIMAL' and cert['exact_model_sha256'] == PINS[D + 'exact_model.json'], 'primal identity')
        sums = exact_primal(cols, rhs, cert['numerators'], cert['denominator'])
        need(cert['numerators'] == [1] * 240 and cert['denominator'] == 12
             and cert['row_residuals'] == [0] * 560 and cert['exact_feasible'] is True
             and cert['integer_selector_solution'] is False and cert['full_factor'] is False, 'exact saved rational-only interpretation')
        # Second exact path evaluates all literal 666 products as Fraction sums.
        fraction_products = [sum((Fraction(cert['numerators'][j - 1], cert['denominator']) for j in row['inputs']), Fraction()) for row in allgram]
        need(fraction_products == [row['target'] for row in allgram], 'complete independent literal rational Gram products')
        badn = cert['numerators'].copy(); badn[0] += 1
        reject('actual_changed_numerator', lambda: exact_primal(cols, rhs, badn, 12))
        reject('actual_changed_denominator', lambda: exact_primal(cols, rhs, [1] * 240, 13))
        badrhs = rhs.copy(); badrhs[20] += 1
        reject('actual_changed_rhs', lambda: exact_primal(cols, badrhs, [1] * 240, 12))
        badcols = deepcopy(cols); badcols[0].append(badcols[0][-1])
        reject('duplicate_sparse_coefficient', lambda: exact_primal(badcols, rhs, [1] * 240, 12))
        badcols = deepcopy(cols); badcols[0].pop()
        reject('missing_sparse_coefficient', lambda: exact_primal(badcols, rhs, [1] * 240, 12))
        badscope = deepcopy(scope['domains']); badscope[0]['choices'][0]['color_words'][0][0] = 2
        reject('changed_literal_word', lambda: check_domains(badscope, domains, groups, triples, patterns))
        badscope = deepcopy(scope['domains']); badscope[0]['choices'].pop()
        reject('missing_local_option', lambda: check_domains(badscope, domains, groups, triples, patterns))
        badraw = deepcopy(raw); badraw['core_adjacency'][0][1] = 0
        reject('changed_raw_core', lambda: geometry(badraw))
        save(out / 'independent_matrix.json', dict(columns_nonzero_row_indices=cols, rhs=rhs, selectors=selectors,
             domain_sizes=list(map(len, domains)), row_metadata=rowmeta, all_gram_rows=allgram))
        save(out / 'exact_primal_check.json', dict(numerators=[1] * 240, denominator=12, integer_row_products=sums,
             integer_row_residuals=[0] * 560, literal_gram_products=[[v.numerator, v.denominator] for v in fraction_products]))
        save(out / 'controls.json', dict(positive_full_geometry_variables=3000, positive_full_geometry_equations=560,
             positive_uniform_denominator=150, local_word_triples_examined=population, corruptions_rejected=corruptions))
        for p in ['acceleration/audit_20260930_hadamard_support_cut_lift_primal.py',
                  'docs/AUDIT_20260930_HADAMARD_SUPPORT_CUT_LIFT_PRIMAL.md', 'uv.lock', 'pyproject.toml']:
            pin(p)
        now = datetime.now(timezone.utc).isoformat()
        limitations = ['Only the exact saved support and twenty selected parity patterns are covered.',
            'The feasible continuous selector relaxation omits integrality, inter-group outside-column caps and residual D.',
            'No binary full Gram factor, graph, target existence or nonexistence follows.',
            'No solver call, exhaustive target coverage, external acceptance or novelty claim.']
        claim = dict(id='C-FIXED-HADAMARD-SIX-PRISM-SUPPORT-CUT-PARITY-LIFT-RATIONAL-PRIMAL', revision=1,
            statement='For the exact second independently checked parity assignment on the frozen six-prism Hadamard support, all twenty balanced local triple domains have twelve options. The authenticated 240-variable, 560-equation nonnegative Gram-selector system is feasible: assigning exactly 1/12 to every selector satisfies every equation, including the implied 666 upper-triangular Gram entries.',
            kind='construction', basis=['DERIVED', 'COMPUTED'], recommendation='VERIFIED', review_state='CLEAR',
            scope='One exact rational point in one specified continuous selected-parity Gram relaxation; not an integral factor.',
            assumptions=['Coordinatewise balanced triples and the authenticated twenty selected parity patterns.',
                         'Columns in each fixed identical-support group are ordered using the previously checked relabelling; no target automorphism is assumed.'],
            dependencies=[dict(id='C-FIXED-HADAMARD-SIX-PRISM-SUPPORT-CUT-PARITY-SAT-WITNESS', revision=1, relation='premise'),
                          dict(id='C-FIXED-HADAMARD-SIX-PRISM-IDENTICAL-SUPPORT-ORDER-NORMALIZATION', revision=1, relation='normalization')],
            limitations=limitations, created_at=now, updated_at=now)
        save(out / 'claim_binding.json', claim)
        report = dict(status='INDEPENDENT_SUPPORT_CUT_PARITY_LIFT_RATIONAL_PRIMAL_PASS', timestamp=now,
            source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            command=[sys.executable, *sys.argv], cwd=str(ROOT), python=platform.python_version(), inputs_sha256=pins,
            outputs_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in out.glob('*.json')},
            counts=dict(variables=240, equations=560, nonzeros=sum(map(len, cols)), domains=20,
                        domain_sizes=[12] * 20, zero_required_rows=0, full_gram_rows=666,
                        local_triples_examined=population, balanced_local_triples=150, corruptions=len(corruptions)),
            verifier='/root/eight_domain_audit', method='Independent direct word-triple enumeration, raw-core Gram derivation, literal matrix reconstruction and two exact rational checking paths',
            shared_components=['Python standard library only; no producer, prior checker, solver or matrix-builder code imported.',
                               'The saved independently checked parity projection and fixed raw support are authenticated input premises.'],
            claim_id=claim['id'], claim_revision=1, recommendation='VERIFIED', review_state='CLEAR',
            artifact_availability='LOCAL_ONLY', limitations=limitations, solver_calls=0, target_resolution=False)
        save(out / 'summary.json', report)
        print(json.dumps(dict(status=report['status'], sha256=digest(out / 'summary.json'))))
    except BaseException as exc:
        save(out / 'failure.json', dict(error=repr(exc), source_sha256=digest(__file__)))
        raise


if __name__ == '__main__':
    main()
