"""Independent sampled parity objects, exact full-pattern blocks and GF(3) screens.

Only the frozen independent parity parser/reconstructor is reused. The general
phase equations and literal row-combination checking are separately authored.
"""
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
import argparse
import ast
import hashlib
import json
import platform
import subprocess
import sys
import audit_20260930_hadamard_balanced_parity_v2 as parity

ROOT = Path(__file__).resolve().parents[1]
B = 'acceleration/results/20260930_'
I = B + 'independent_review/'
RAW = B + 'hadamard20_support/six_prism.json'
OLD_MODEL = B + 'hadamard_balanced_parity/model.json'
BASE_MODEL = B + 'hadamard_parity_support_cuts/model.json'
BASE_CNF = B + 'hadamard_parity_support_cuts/instance.cnf'
ENCODING_GATE = I + 'hadamard_parity_support_cuts_encoding/summary.json'
NECESSITY_GATE = I + 'hadamard_general_f3_phase_necessity/summary.json'
FIRST_PROJECTION = I + 'hadamard_parity_support_cuts_sat/independent_projection.json'
PINS = {
    RAW: 'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',
    OLD_MODEL: 'a75b60c4ef0f8decd7537d70cced7bffa14cb7a4881de726bf98c96635888147',
    BASE_MODEL: 'c477693bbf634609c234bf5b791c499f8f9ded091795b01bec297746288b4f4f',
    BASE_CNF: 'db9816ddf037250efc04b1e093e407eac0ec2c4fadf2f24b5774fb3249eba07f',
    ENCODING_GATE: '7a9b76b9e139f065c850194b6968ebf4a98c0211668e1f824d2ac75640b7dd12',
    NECESSITY_GATE: '30dd4e571140a139f7e36baf47f62a4428b752c79bbddd164ec6e54f3b232d67',
    FIRST_PROJECTION: 'f43ad5f79d6fc8c8f6825f52d0140a07852a873207642b4edb7c035cb5ed4a8c',
    'acceleration/audit_20260930_hadamard_balanced_parity_v2.py': '74557011dc83dd38a302766392273278e10b6ecc58fcc0639bbf4b0a78a8f7ae',
}
PRODUCER_SOURCE = 'acceleration/theory_20260930_hadamard_parity_phase_batch.py'
PRODUCER_SPEC = 'acceleration/theory_20260930_hadamard_parity_phase_batch_spec.md'
# Filled only after the producer explicitly freezes these inputs, before calibration.
PRODUCER_PINS = {
    PRODUCER_SOURCE: '9a3e0a717e5295881ef8b65bb6bc638c242d5abb2ea045b85f62b3e349bf96b5',
    PRODUCER_SPEC: 'ab01cc76cac92189cfc1879fbfb7b869bc303a58cd4165f8d200853cdf23c314',
    'acceleration/theory_20260930_hadamard_general_f3_system.py': '77877e34ca6a6f73f98546d0221faef375e091e54ba4c9b4f8b8a2e23b0d0162',
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_bytes())


def save(path, value):
    with Path(path).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def canonical_base(raw, model):
    clauses, groups, pairs = parity.reconstruct(raw, model)
    need(len(clauses) == 4481, 'original complete clause population')
    for pair in pairs:
        terms = pair['terms']
        need(len(terms) == 5, 'all five incident groups')
        clauses.append([term['difference_variable'] for term in terms]
                       + [groups[term['group']]['selectors'][0] for term in terms])
    need(len(clauses) == 4541, 'full strengthened base population')
    return clauses, groups, pairs


def raw_projection(values, clauses, groups, pairs, decoded=None):
    need(not parity.satisfied(clauses, values), 'complete actual assignment satisfies every clause')
    result = parity.projection(values, groups, pairs)
    result['model_sha256'] = PINS[BASE_MODEL]
    cuts = []
    for pair in pairs:
        a, b = pair['coordinates']
        count, constants = 0, []
        for term in pair['terms']:
            g = term['group']
            support = groups[g]['support']
            pattern = result['selected_group_parity_patterns'][g]
            count += pattern[support.index(a)] != pattern[support.index(b)]
            if not any(pattern):
                constants.append(g)
        ok = count > 0 or bool(constants)
        need(ok, 'raw constant-group support necessity')
        cuts.append(dict(coordinates=[a, b], disagreement_count=count,
                         selected_constant_groups=constants, satisfied=ok))
    result['support_cut_checks'] = cuts
    if decoded is not None:
        parity.compare_decoded(result, decoded)
    return result


def blocked_formula(base_clauses, records, groups, read_projection):
    need(type(records) is list and len(records) > 0, 'ordered initial and previous sampling blocks')
    need(records[0]['projection_path'] == FIRST_PROJECTION
         and records[0]['projection_sha256'] == PINS[FIRST_PROJECTION], 'first known second-parity witness block')
    clauses = list(base_clauses)
    seen = set()
    for record in records:
        projection = read_projection(record['projection_path'], record['projection_sha256'])
        selected = record['selected_group_selector_ids']
        need(selected == projection['selected_group_selector_ids'] and len(selected) == 20, 'exact full twenty selector block')
        for g, literal in enumerate(selected):
            need(type(literal) is int and literal in groups[g]['selectors'], 'one positive selector per group in order')
        key = tuple(selected)
        need(key not in seen, 'no repeated blocked projection')
        seen.add(key)
        clauses.append([-literal for literal in selected])
    return clauses, seen


def field_rank_and_kernel(rows, width=120):
    need(all(len(row) == width and all(type(v) is int and v in [0, 1, 2] for v in row) for row in rows), 'canonical GF3 matrix')
    # Use descending pivot columns, unlike ordinary left-to-right producer RREF.
    work = [row.copy() for row in rows]
    rank, pivot_columns = 0, []
    for column in reversed(range(width)):
        found = next((r for r in reversed(range(rank, len(work))) if work[r][column]), None)
        if found is None:
            continue
        work[rank], work[found] = work[found], work[rank]
        inv = 1 if work[rank][column] == 1 else 2
        work[rank] = [v * inv % 3 for v in work[rank]]
        for r in range(len(work)):
            if r != rank and work[r][column]:
                multiplier = work[r][column]
                work[r] = [(a - multiplier * b) % 3 for a, b in zip(work[r], work[rank])]
        pivot_columns.append(column)
        rank += 1
    free = [c for c in range(width) if c not in pivot_columns]
    kernel = []
    for column in free:
        v = [0] * width
        v[column] = 1
        for r, pivot in enumerate(pivot_columns):
            v[pivot] = -work[r][column] % 3
        need(all(sum(x * y for x, y in zip(row, v)) % 3 == 0 for row in rows), 'independent raw nullvector')
        kernel.append(v)
    return rank, kernel


def phase_equations(raw, projection, groups):
    need(raw['core_adjacency'] == [[int((a // 12 == b // 12 and (a % 12 ^ 1) == b % 12)
               or (a // 12 != b // 12 and a % 12 == b % 12)) for b in range(36)] for a in range(36)], 'fixed raw six-prism core')
    patterns = projection['selected_group_parity_patterns']
    need(len(patterns) == 20, 'twenty full parity patterns')
    supports = [g['support'] for g in groups]
    signs = []
    for g, p in enumerate(patterns):
        need(p in groups[g]['parity_patterns'] and p[0] == 0, 'normalized constant or mixed parity')
        signs.append([1 if value == 0 else 2 for value in p])
    equations, functionals, pair_records = [], [], []

    def row(kind, terms, dependencies, **metadata):
        coefficients = [0] * 120
        for column, value in terms:
            coefficients[column] = (coefficients[column] + value) % 3
        equations.append(dict(index=len(equations), kind=kind, coefficients=coefficients, rhs=0,
                              parity_dependency_groups=dependencies, **metadata))

    for g in range(20):
        row('column_gauge', [(6 * g, 1)], [], group=g)
    for g in range(20):
        classes = [[i for i, s in enumerate(signs[g]) if s == slope] for slope in [1, 2]]
        if not classes[1]:
            row('local_constant_sum', [(6 * g + i, 1) for i in range(6)], [g], group=g, positions=list(range(6)))
        else:
            need(list(map(len, classes)) == [3, 3], 'mixed sign populations')
            for slope, positions in zip([1, 2], classes):
                row('local_same_sign_sum', [(6 * g + i, 1) for i in positions], [g],
                    group=g, sign=slope, positions=positions)
                for left, right in combinations(positions, 2):
                    coefficients = [0] * 120
                    coefficients[6 * g + left], coefficients[6 * g + right] = 2, 1
                    functionals.append(dict(index=len(functionals), kind='local_same_sign_distinct', group=g,
                        positions=[left, right], coefficients=coefficients,
                        parity_dependency_groups=[g], required='nonzero in GF(3)'))
    for a, b in combinations(range(12), 2):
        if a ^ 1 == b:
            continue
        common = [g for g, support in enumerate(supports) if a in support and b in support]
        need(len(common) == 5, 'five containing groups from raw support')
        relative = []
        split = {1: [], 2: []}
        members = {1: [], 2: []}
        for g in common:
            left, right = supports[g].index(a), supports[g].index(b)
            slope = signs[g][left] * signs[g][right] % 3
            split[slope] += [(6 * g + right, 1), (6 * g + left, -slope)]
            members[slope].append(g)
            coefficients = [0] * 120
            coefficients[6 * g + left], coefficients[6 * g + right] = -slope % 3, 1
            relative.append(dict(group=g, positions=[left, right], relative_sign=slope,
                                 relative_phase_coefficients=coefficients))
        need(len(members[2]) in [0, 3], 'pair projection parity relation')
        for slope, label in [(2, 'odd'), (1, 'even')]:
            row('pair_' + label + '_phase_sum', split[slope], common,
                coordinates=[a, b], groups=members[slope])
        pair_records.append(dict(coordinates=[a, b], incident_groups=common, relative_maps=relative))
    mixed = sum(any(p) for p in patterns)
    need(len(equations) == 160 + mixed and len(functionals) == 6 * mixed, 'retained zero rows and declared rejection population')
    variables = [dict(index=6*g+pos, group=g, position=pos, coordinate=a, sign=signs[g][pos])
                 for g, support in enumerate(supports) for pos, a in enumerate(support)]
    return dict(schema='GENERAL_BALANCED_GF3_PHASE_SYSTEM_V1', field=3, variables=variables,
        groups=supports, patterns=patterns, signs=signs, rows=equations, pair_records=pair_records,
        necessary_nonzero_functionals=functionals, mixed_groups=mixed, constant_groups=20-mixed,
        one_fixed_parity_branch=True, Ycaps_encoded=False, residual_D_encoded=False,
        rejection_rule='First mixed-group same-sign difference contained in the equation row space; no pair inequalities used.')


def check_row_combination(matrix, functional, weights):
    need(len(weights) == len(matrix) and all(type(v) is int and v in [0, 1, 2] for v in weights), 'complete canonical row combination')
    need(len(functional) == 120 and any(functional), 'nonzero required functional')
    combined = [sum(weights[r] * matrix[r][c] for r in range(len(matrix))) % 3 for c in range(120)]
    need(combined == functional, 'all120 literal row-combination coordinates')
    return combined


def check_screen(system, saved):
    matrix = [row['coefficients'] for row in system['rows']]
    rank, kernel = field_rank_and_kernel(matrix)
    certificate = saved['linear_certificate']
    need(certificate['rank'] == saved['rank'] == rank and certificate['nullity'] == saved['nullity'] == 120-rank,
         'independent rank/nullity agreement')
    rr, transform = certificate['rref'], certificate['row_transform']
    need(len(rr) == len(transform) == len(matrix), 'full row certificate population')
    for actual, weights in zip(rr, transform):
        need(len(actual) == 120 and all(type(v) is int and v in [0, 1, 2] for v in actual), 'canonical RREF row')
        need(len(weights) == len(matrix) and all(type(v) is int and v in [0, 1, 2] for v in weights), 'full canonical row transform')
        nonzero = [(r, w) for r, w in enumerate(weights) if w]
        need(actual == [sum(w * matrix[r][c] for r, w in nonzero) % 3 for c in range(120)], 'literal full row-transform identity')
    pivots = []
    for i, row in enumerate(rr):
        present = [c for c, value in enumerate(row) if value]
        if present:
            need(i == len(pivots), 'zero RREF rows at end')
            pivot = present[0]
            need(row[pivot] == 1 and all(r[pivot] == int(j == i) for j, r in enumerate(rr)), 'normalized isolated RREF pivot')
            pivots.append(pivot)
    free = [c for c in range(120) if c not in pivots]
    need(pivots == sorted(pivots) == certificate['pivots'] and len(pivots) == rank and free == certificate['free_columns'], 'every RREF pivot and free coordinate')
    nullspace = certificate['nullspace_basis']
    need(len(nullspace) == 120-rank, 'complete producer nullspace dimension')
    for i, vector in enumerate(nullspace):
        need(len(vector) == 120 and all(type(v) is int and v in [0, 1, 2] for v in vector), 'canonical nullvector')
        need([vector[c] for c in free] == [int(j == i) for j in range(len(free))], 'independent free-coordinate kernel basis')
        need(all(sum(x*y for x, y in zip(row, vector)) % 3 == 0 for row in matrix), 'all raw nullspace products')
    functionals = system['necessary_nonzero_functionals']
    vanishing = [i for i, f in enumerate(functionals)
                 if all(sum(a*b for a, b in zip(f['coefficients'], v)) % 3 == 0 for v in kernel)]
    first = vanishing[0] if vanishing else None
    need(saved['schema'] == 'GENERAL_BALANCED_GF3_PHASE_SCREEN_V1'
         and saved['complete_nonlinear_feasibility'] is False and saved['independent_approval'] is False
         and saved['mathematical_nogood_generated'] is False and saved['shortened_nogood_generated'] is False, 'candidate-only producer screen interpretation')
    need(saved['functionals_attempted'] == (first+1 if first is not None else len(functionals)), 'first-declared-functional screen order')
    if first is None:
        need(saved['obstruction'] is None and saved['status'] == 'UNKNOWN_LINEAR_SCREEN', 'no false linear exclusion')
    else:
        need(saved['status'] == 'CANDIDATE_PHASE_OBSTRUCTION', 'producer exact-screen state')
        obstruction = saved['obstruction']
        need(obstruction['condition'] == functionals[first], 'exact first necessary nonzero condition')
        check_row_combination(matrix, functionals[first]['coefficients'], obstruction['row_combination'])
    return dict(rank=rank, nullity=120-rank, independently_derived_kernel=kernel,
                functionals=len(functionals), vanishing_functionals=vanishing, first_vanishing_index=first,
                exact_exclusion=first is not None,
                operations_log_replayed=False,
                operations_log_scope='Complete row-transform identities are checked directly instead of replaying the redundant operation log.')


def repository_import_closure(start):
    pending, found = [ROOT / start], set()
    while pending:
        path = pending.pop()
        if path in found:
            continue
        found.add(path)
        tree = ast.parse(path.read_text(encoding='utf-8-sig'), filename=str(path))
        for node in ast.walk(tree):
            names = [alias.name for alias in node.names] if isinstance(node, ast.Import) else [node.module] if isinstance(node, ast.ImportFrom) and node.module else []
            for name in names:
                local = ROOT / 'acceleration' / (name.split('.')[0] + '.py')
                if local.exists():
                    pending.append(local)
    return sorted(path.relative_to(ROOT).as_posix() for path in found)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('mode', choices=['calibrate', 'case'])
    ap.add_argument('--case-dir', type=Path)
    ap.add_argument('--case-index', type=int)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    pins, rejected = {}, []

    def pin(path, expected=None):
        path = Path(path)
        path = path if path.is_absolute() else ROOT / path
        path = path.resolve()
        need(path.is_relative_to(ROOT), 'artifact stays in repository')
        key = path.relative_to(ROOT).as_posix()
        value = sha(path)
        need(expected is None or value == expected, 'exact input identity ' + key)
        pins[key] = value
        return path

    def load(path, expected=None):
        return read(pin(path, expected))

    def reject(label, action):
        try:
            action()
        except (ValueError, TypeError, KeyError, IndexError):
            rejected.append(label)
        else:
            raise ValueError('corruption accepted ' + label)

    try:
        need(set(PRODUCER_PINS) == {PRODUCER_SOURCE, PRODUCER_SPEC, 'acceleration/theory_20260930_hadamard_general_f3_system.py'}, 'producer inputs frozen before calibration')
        for path, value in {**PINS, **PRODUCER_PINS}.items():
            pin(path, value)
        closure = repository_import_closure(PRODUCER_SOURCE)
        for path in closure:
            pin(path)
        raw, old_model = load(RAW), load(OLD_MODEL)
        encoding, necessity = load(ENCODING_GATE), load(NECESSITY_GATE)
        need(encoding['status'] == 'INDEPENDENT_HADAMARD_PARITY_SUPPORT_CUT_ENCODING_PASS'
             and necessity['status'] == 'INDEPENDENT_GENERAL_BALANCED_GF3_PHASE_NECESSITY_PASS', 'independent exact semantic gates')
        for path in [BASE_CNF, BASE_MODEL]:
            need(encoding['inputs_sha256'][path] == PINS[path], 'encoding gate bound to same raw base')
        clauses, groups, pairs = canonical_base(raw, old_model)
        need((ROOT / BASE_CNF).read_bytes() == parity.cnf_bytes(clauses), 'complete independently rebuilt base CNF bytes')
        initial = load(FIRST_PROJECTION)
        old_dir = B + 'hadamard_balanced_parity_native_pilot/main/'
        new_dir = B + 'hadamard_parity_support_cuts_native_pilot/main/'
        oldvalues = parity.assignment(load(old_dir + 'parsed_model.json')['assignment'], 520)
        newvalues = parity.assignment(load(new_dir + 'parsed_model.json')['assignment'], 520)
        for directory, values in [(old_dir, oldvalues), (new_dir, newvalues)]:
            text = pin(directory + 'solver.stdout.log').read_text(encoding='utf-8')
            need(parity.native(text, 520) == values, 'genuine complete native/JSON control')
        need(not parity.satisfied(clauses[:4481], oldvalues), 'actual old witness for its old formula')
        oldprojection = parity.projection(oldvalues, groups, pairs)
        need(len(parity.satisfied(clauses, oldvalues)) == 2, 'old witness correctly fails strengthened formula')
        newprojection = raw_projection(newvalues, clauses, groups, pairs, load(new_dir + 'decoded_projection.json'))
        need(newprojection == initial, 'actual strengthened witness and authenticated initial projection')
        first_record = dict(projection_path=FIRST_PROJECTION, projection_sha256=PINS[FIRST_PROJECTION],
                            selected_group_selector_ids=initial['selected_group_selector_ids'])
        augmented, _ = blocked_formula(clauses, [first_record], groups, load)
        need(parity.satisfied(augmented, newvalues) == [4542], 'full twenty-selector block rejects exactly the already known projection')
        # Synthetic codec/clause positive only: does not claim an augmented research witness.
        synthetic_values = [-i for i in range(1, 521)]
        synthetic_native = 'c SYNTHETIC CODEC ONLY\ns SATISFIABLE\nv ' + ' '.join(map(str, synthetic_values)) + ' 0\n'
        synthetic = parity.native(synthetic_native, 520)
        need(synthetic == parity.assignment(synthetic_values, 520), 'complete synthetic native/JSON positive')
        synthetic_clauses = [[-(i % 520 + 1)] for i in range(4541)] + [augmented[-1]]
        need(not parity.satisfied(synthetic_clauses, synthetic), 'synthetic complete formula plus exact full-pattern suffix')
        for label, text in [('missing_SAT_status', synthetic_native.replace('s SATISFIABLE\n', '')),
                            ('false_UNSAT_status', synthetic_native.replace('SATISFIABLE', 'UNSATISFIABLE')),
                            ('missing_final_zero', synthetic_native.replace(' 0\n', '\n')),
                            ('duplicate_variable', synthetic_native.replace('v -1 -2', 'v -1 -1')),
                            ('literal_after_zero', synthetic_native + 'v 1\n')]:
            reject(label, lambda text=text: parity.native(text, 520))
        reject('short_JSON_assignment', lambda: parity.assignment(synthetic_values[:-1], 520))
        reject('Boolean_JSON_literal', lambda: parity.assignment([True, *synthetic_values[1:]], 520))
        bad = deepcopy(first_record); bad['selected_group_selector_ids'].pop()
        reject('shortened_sampling_block', lambda: blocked_formula(clauses, [bad], groups, load))
        reject('duplicate_sampling_block', lambda: blocked_formula(clauses, [first_record, first_record], groups, load))
        bad = deepcopy(first_record); bad['projection_sha256'] = '0' * 64
        reject('wrong_projection_hash', lambda: blocked_formula(clauses, [bad], groups, load))
        expected_bytes = parity.cnf_bytes(augmented)
        for label, mutated in [('wrong_header', expected_bytes.replace(b'p cnf 520 4542', b'p cnf 520 4541', 1)),
                               ('omitted_full_block', parity.cnf_bytes(clauses)),
                               ('changed_block_literal', parity.cnf_bytes(clauses + [[-augmented[-1][0], *augmented[-1][1:]]])),
                               ('reordered_body', parity.cnf_bytes([*clauses[1:], clauses[0], augmented[-1]]))]:
            reject(label, lambda mutated=mutated: need(mutated == expected_bytes, 'exact composed header and body'))
        need(field_rank_and_kernel([[1, 1], [2, 2]], 2)[0] == 1, 'small rank positive')
        from itertools import product
        for entries in product(range(3), repeat=6):
            matrix = [list(entries[:3]), list(entries[3:])]
            minor_rank = 2 if any((matrix[0][a]*matrix[1][b]-matrix[0][b]*matrix[1][a]) % 3 for a, b in combinations(range(3), 2)) else int(any(entries))
            need(field_rank_and_kernel(matrix, 3)[0] == minor_rank, 'all729 two-by-three rank controls')
        constants = deepcopy(newprojection); constants['selected_group_parity_patterns'] = [[0]*6 for _ in range(20)]
        constant_system = phase_equations(raw, constants, groups)
        need(len(constant_system['rows']) == 160 and not constant_system['necessary_nonzero_functionals']
             and sum(not any(r['coefficients']) for r in constant_system['rows']) == 60, 'constant-group no-distinctness and zero-row positive control')
        old_system = phase_equations(raw, oldprojection, groups)
        need(len(old_system['rows']) == 176 and len(old_system['necessary_nonzero_functionals']) == 96,
             'actual old sixteen-mixed/four-constant general-system control')
        system = phase_equations(raw, newprojection, groups)
        old_phase = load(B + 'hadamard_f3_phases/phase_system.json', 'aecf80f4f1c7cd29f821cb52ec502b810aa87fc8ff908ea38e2f36a69e416061')
        need([r['coefficients'] for r in old_phase['rows']] == [r['coefficients'] for r in system['rows']], 'independent general rows agree with authenticated all-mixed special case')
        certificate = load(B + 'hadamard_f3_phases/linear_certificate.json', 'e7d8640b5ee9a2024b17e6539133f9a36f6328f335dc3150206d8eb9732d6fc3')
        minimal = load(I + 'hadamard_f3_phase_obstruction/minimal_obstruction.json', 'c86e0826bbd56c86e42ce3983924030d7a4c0df63859a704dca296130c852489')
        saved_screen = dict(schema='GENERAL_BALANCED_GF3_PHASE_SCREEN_V1', status='CANDIDATE_PHASE_OBSTRUCTION',
            rank=certificate['rank'], nullity=certificate['nullity'], linear_certificate=certificate,
            obstruction=dict(condition=system['necessary_nonzero_functionals'][0], row_combination=minimal['row_combination']),
            functionals_attempted=1, complete_nonlinear_feasibility=False, independent_approval=False,
            mathematical_nogood_generated=False, shortened_nogood_generated=False)
        checked = check_screen(system, saved_screen)
        need(checked['exact_exclusion'] and checked['rank'] == 119 and checked['first_vanishing_index'] == 0, 'actual prior exact phase certificate positive')
        bad = deepcopy(saved_screen); bad['obstruction']['row_combination'] = [0]*180
        reject('zero_false_certificate', lambda: check_screen(system, bad))
        bad = deepcopy(saved_screen); bad['obstruction']['condition']['coefficients'][0] = 0
        reject('altered_required_difference', lambda: check_screen(system, bad))
        bad = deepcopy(saved_screen); bad['linear_certificate']['nullspace_basis'][0][0] = 1
        reject('invalid_nullspace_vector', lambda: check_screen(system, bad))
        bad = deepcopy(saved_screen); bad['rank'] -= 1
        reject('wrong_rank_claim', lambda: check_screen(system, bad))
        bad = deepcopy(saved_screen); bad['functionals_attempted'] += 1
        reject('wrong_first_functional', lambda: check_screen(system, bad))
        bad = deepcopy(system); bad['rows'][0]['coefficients'][0] = 0
        reject('missing_gauge_coefficient', lambda: need(bad == phase_equations(raw, newprojection, groups), 'every necessary equation'))
        bad = deepcopy(system); bad['rows'][-1]['parity_dependency_groups'].pop()
        reject('dropped_pair_dependency', lambda: need(bad == phase_equations(raw, newprojection, groups), 'all five parity dependencies'))
        save(out / 'controls.json', dict(corruptions_rejected=rejected, small_rank_cases=729,
            genuine_native_objects=2, prior_exact_phase_certificate='Authenticated previously excluded second branch',
            constant_group_control_scope='General linear equations and absence of blanket distinctness only; not a satisfying full parity formula or factor.',
            synthetic_control_scope='520-literal codec and4542 synthetic clauses only, not research SAT.'))
        result = None
        if args.mode == 'case':
            need(args.case_dir is not None and args.case_index is not None and 0 <= args.case_index < 16, 'bounded case identity')
            folder = args.case_dir.resolve()
            need(folder.name == f'case_{args.case_index:02d}', 'case directory index')
            records = load(folder / 'blocked_projections.json')
            need(len(records) == args.case_index + 1, 'initial plus every earlier sampled case')
            for prior_index, record in enumerate(records[1:]):
                expected_path = (folder.parent / f'case_{prior_index:02d}' / 'decoded_projection.json').relative_to(ROOT).as_posix()
                need(record['projection_path'] == expected_path and record['purpose'] == 'DISTINCT_CANDIDATE_SAMPLING'
                     and record['mathematical_exclusion_approved'] is False, 'ordered prior sampling-only record')
            complete, previous = blocked_formula(clauses, records, groups, load)
            need(pin(folder / 'instance.cnf').read_bytes() == parity.cnf_bytes(complete), 'all exact current header/base/ordered-block bytes')
            values = parity.assignment(load(folder / 'parsed_model.json')['assignment'], 520)
            need(parity.native(pin(folder / 'solver.stdout.log').read_text(encoding='utf-8'), 520) == values, 'all actual native/JSON literals')
            projection = raw_projection(values, complete, groups, pairs, load(folder / 'decoded_projection.json'))
            need(tuple(projection['selected_group_selector_ids']) not in previous, 'new unique full pattern')
            actual_system = load(folder / 'phase_system.json')
            expected_system = phase_equations(raw, projection, groups)
            need(actual_system == expected_system, 'complete independent general phase-system reconstruction')
            phase_result = check_screen(expected_system, load(folder / 'phase_screen.json'))
            save(out / 'independent_projection.json', projection)
            save(out / 'independent_phase_check.json', phase_result)
            result = dict(case_index=args.case_index, native_literals=520, clauses=len(complete),
                blocking_clauses=len(records), projection_unique=True, mixed_groups=expected_system['mixed_groups'],
                constant_groups=expected_system['constant_groups'], phase_variables=120,
                phase_rows=len(expected_system['rows']), **phase_result)
        pin('acceleration/audit_20260930_hadamard_parity_phase_batch.py')
        pin('docs/AUDIT_20260930_HADAMARD_PARITY_PHASE_BATCH.md')
        for path in ['uv.lock', 'pyproject.toml']:
            pin(path)
        status = 'INDEPENDENT_HADAMARD_PARITY_PHASE_BATCH_OBJECT_CALIBRATION_PASS' if args.mode == 'calibrate' else 'INDEPENDENT_HADAMARD_PARITY_PHASE_BATCH_CASE_PASS'
        report = dict(status=status, timestamp=datetime.now(timezone.utc).isoformat(),
            source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            command=[sys.executable, *sys.argv], cwd=str(ROOT), python=platform.python_version(),
            inputs_sha256=pins, outputs_sha256={p.relative_to(ROOT).as_posix(): sha(p) for p in out.glob('*.json')},
            mode=args.mode, result=result, corruption_controls=len(rejected),
            producer_static_source_closure=closure, verifier='/root/eight_domain_audit',
            shared_components=['Frozen independently authored original parity native/JSON/assignment/projection reconstruction reused with exact source binding.',
                'Own general GF3 reconstruction, reverse-column rank and literal row-combination checker; no producer source imported.',
                'Static producer import closure is hashed without executing those modules.'],
            scope='Calibration or one complete sampled projection and conditional phase screen only. Full20 blocks are sampling bookkeeping unless their exclusions are separately verified.',
            limitations=['No native solver call, new full factor or target claim.',
                'A surviving linear screen is not simultaneous nonlinear feasibility.',
                'No sample-wide completeness or target-level consequence from augmented UNSAT.',
                'Row-transform identities are checked directly; redundant producer operation logs are preserved but not replayed.'],
            artifact_availability='LOCAL_ONLY', target_resolution=False, solver_calls=0)
        save(out / 'summary.json', report)
        print(json.dumps(dict(status=status, sha256=sha(out / 'summary.json'))))
    except BaseException as exc:
        save(out / 'failure.json', dict(error=repr(exc), source_sha256=sha(__file__)))
        raise


if __name__ == '__main__':
    main()
