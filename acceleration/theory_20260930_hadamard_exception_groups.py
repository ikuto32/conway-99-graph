"""Candidate few-exception theorem and separately scoped row-margin census."""
from collections import Counter
from datetime import datetime, timezone
from itertools import combinations, product
from pathlib import Path
import argparse, hashlib, json, platform, subprocess, sys, time
from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]
B = ROOT/'acceleration/results'
RAW = B/'20260930_hadamard20_support/six_prism.json'
LOCAL = B/'20260930_hadamard_triplicate_counts/local_triples.json'
AUDIT = B/'20260930_independent_review/hadamard_triplicate_counts_v2/summary.json'
PINS = {RAW: 'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',
        LOCAL: '9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776',
        AUDIT: 'cb9f1c7f8cfe0db557f554ded5427a9cba46dda10dcd9b5df9968e1d3b776f88'}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_bytes())


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def key(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def save(path, obj):
    with Path(path).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(obj, stream, indent=2)
        stream.write('\n')


def determinant(a):
    if len(a) == 1:
        return a[0][0]
    if len(a) == 2:
        return a[0][0]*a[1][1]-a[0][1]*a[1][0]
    return sum((1 if j % 2 == 0 else -1)*a[0][j]*determinant([[row[k] for k in range(3) if k != j] for row in a[1:]]) for j in range(3))


def nonzero_minor(matrix, columns):
    for rows in combinations(range(len(matrix)), len(columns)):
        minor = [[matrix[r][c] for c in columns] for r in rows]
        d = determinant(minor)
        if d:
            return dict(columns=list(columns), rows=list(rows), minor=minor, determinant=d)
    return None


def literal_local(words):
    need(len(words) == 3 and len(set(map(tuple, words))) == 3, 'distinct local words')
    need(all(sorted(w) == [0, 0, 1, 1, 2, 2] for w in words), 'two coordinates per fibre per column')
    need(all(sum(a == b for a, b in zip(left, right, strict=True)) <= 2 for left, right in combinations(words, 2)), 'local column caps')
    for i, j in combinations(range(6), 2):
        need(all(count <= (1 if a == b else 2) for (a, b), count in Counter((w[i], w[j]) for w in words).items()), 'local Gram upper bounds')
    return [[sum(w[i] == f for w in words) for f in range(3)] for i in range(6)]


def controls(local):
    words = local['words']
    balanced = literal_local([words[i] for i in local['balanced'][0]])
    unbalanced = literal_local([words[i] for i in local['first_unbalanced']['option_indices']])
    need(all(c == [1, 1, 1] for c in balanced) and any(c != [1, 1, 1] for c in unbalanced), 'genuine local positive scopes')
    vertices = list(product(range(2), repeat=3))
    matrix = [[1]*8]+[[v[i] for v in vertices] for i in range(3)]
    for columns in combinations(range(8), 3):
        need(nonzero_minor(matrix, columns) is not None, 'all binary cube triple columns independent')
    duplicate = [[1, 1], [0, 0], [1, 1]]
    need(nonzero_minor(duplicate, [0, 1]) is None, 'duplicate-column independence corruption rejected')
    square = [[1, 1, 1, 1], [0, 0, 1, 1], [0, 1, 0, 1]]
    coefficients = [1, -1, -1, 1]
    need(all(sum(x*y for x, y in zip(row, coefficients, strict=True)) == 0 for row in square), 'four-column limitation control')
    delta = [1, -1, 0]
    need([a+b for a, b in zip(delta, [-1, 1, 0], strict=True)] == [0, 0, 0], 'two-deviation cancellation control')
    need(any(a+b for a, b in zip(delta, [0, 1, -1], strict=True)), 'uncancelled deviation rejected')
    return dict(binary_cube_triples=56, duplicate_column_minor=None, duplicate_null_reason='Dependent control intentionally lacks a nonzero minor.',
        balanced_local=balanced, unbalanced_local=unbalanced, four_column_square=square, four_column_relation=coefficients,
        rejected_controls=['duplicate_column_independence', 'uncancelled_deviation'], scope='Local/cube controls only, no complete factor.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    try:
        for path, digest in PINS.items():
            need(sha(path) == digest, 'frozen input '+key(path))
        audit = read(AUDIT)
        need(audit['status'] == 'INDEPENDENT_HADAMARD_TRIPLICATE_PROJECTIONS_PASS' and audit['inputs_sha256'][key(LOCAL)] == PINS[LOCAL], 'literal prior marginal/census premise binding')
        inputs = {key(p): d for p, d in PINS.items()}
        for path in [Path(__file__), Path(__file__).with_name('theory_20260930_hadamard_exception_groups_spec.md'), ROOT/'uv.lock', ROOT/'pyproject.toml']:
            inputs[key(path)] = sha(path)
        save(out/'manifest.json', dict(timestamp=datetime.now(timezone.utc).isoformat(), source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            command=[sys.executable, *sys.argv], cwd=str(ROOT), python=platform.python_version(), inputs_sha256=inputs,
            limits=dict(seconds=120, solver_calls=0), status='PREREGISTERED_CANDIDATE_EXCEPTION_GROUP_ANALYSIS'))
        raw, local = read(RAW), read(LOCAL)
        save(out/'controls.json', controls(local))
        supports = [[a for a in range(12) if raw['L'][a][d]] for d in range(60)]
        groups = list(dict.fromkeys(map(tuple, supports)))
        need(len(groups) == 20 and all(supports.count(list(g)) == 3 for g in groups), 'raw20 distinct triple supports')
        histogram = Counter(len(set(groups[g]) & set(groups[h])) for g, h in combinations(range(20), 2))
        g, h = next((g, h) for g, h in combinations(range(20), 2) if len(set(groups[g]) & set(groups[h])) not in (0, 3))
        refutation = dict(statement_refuted='Every pair of distinct supports intersects in0 or3 coordinates.', groups=[g, h],
            left_support=list(groups[g]), right_support=list(groups[h]), actual_intersection=sorted(set(groups[g]) & set(groups[h])),
            complete_histogram={str(k): v for k, v in sorted(histogram.items())}, independent_approval=False)
        save(out/'intersection_counterexample.json', refutation)
        matrices = []
        total_minors = 0
        for a in range(12):
            containing = [g for g, support in enumerate(groups) if a in support]
            others = [b for b in range(12) if b != a and b != (a ^ 1)]
            matrix = [[1]*len(containing)]+[[int(b in groups[g]) for g in containing] for b in others]
            need(len(containing) == 10 and all(sum(row) == 5 for row in matrix[1:]), 'raw marginal shape and baseline')
            certificates = []
            for n in (1, 2, 3):
                for columns in combinations(range(10), n):
                    certificate = nonzero_minor(matrix, columns)
                    need(certificate is not None, 'all up-to-three marginal columns independent')
                    certificates.append(certificate)
            total_minors += len(certificates)
            matrices.append(dict(coordinate=a, groups=containing, other_coordinates=others, matrix=matrix, certificates=certificates))
        save(out/'few_exception_marginal_certificates.json', dict(matrices=matrices, nonzero_minors=total_minors,
            candidate_statement='Every prescribed-Gram factor on the fixed support with at most3 unbalanced support groups is completely balanced.',
            no_balanced_UNSAT_premise_used=True, independent_approval=False))
        words, survivors = local['words'], local['survivors']
        need(len(words) == 90 and len(survivors) == 31110, 'pinned finite local domain')
        counts = [literal_local([words[i] for i in triple]) for triple in survivors]
        balanced_masks = [sum(1 << i for i, c in enumerate(cc) if c == [1, 1, 1]) for cc in counts]
        catalogs = []
        for required in range(64):
            indices = [i for i, mask in enumerate(balanced_masks) if mask & required == required]
            catalogs.append(dict(required_balanced_positions_mask=required, required_positions=[i for i in range(6) if required & (1 << i)],
                survivor_indices=indices, count=len(indices), balanced_count=sum(balanced_masks[i] == 63 for i in indices),
                genuinely_unbalanced_count=sum(balanced_masks[i] != 63 for i in indices)))
        save(out/'required_balance_domains.json', dict(local_catalog_path=key(LOCAL), local_catalog_sha256=PINS[LOCAL], catalogs=catalogs))
        pair_records, first_witness = [], None
        for g, h in tqdm(list(combinations(range(20), 2)), desc='Row-only exception pairs', mininterval=1):
            common = sorted(set(groups[g]) & set(groups[h]))
            sides = []
            for p in (g, h):
                positions = [groups[p].index(a) for a in common]
                required = sum(1 << i for i, a in enumerate(groups[p]) if a not in common)
                selected = catalogs[required]['survivor_indices']
                profiles, representative = Counter(), {}
                for i in selected:
                    signature = tuple(counts[i][pos][f]-1 for pos in positions for f in range(3))
                    profiles[signature] += 1
                    representative.setdefault(signature, i)
                sides.append((required, selected, profiles, representative))
            terms = []
            compatible = exact_two = 0
            for sig, left_count in sorted(sides[0][2].items()):
                opposite = tuple(-x for x in sig)
                right_count = sides[1][2][opposite]
                compatible += left_count*right_count
                if any(sig):
                    exact_two += left_count*right_count
                terms.append(dict(shared_deviation=list(sig), left_count=left_count, opposite_right_count=right_count))
                if first_witness is None and any(sig) and right_count:
                    li, ri = sides[0][3][sig], sides[1][3][opposite]
                    coordinate = common[next(i for i in range(len(common)) if any(sig[3*i:3*i+3]))]
                    b = next(a for a in groups[g] if a not in groups[h])
                    need(b != coordinate and b != (coordinate ^ 1), 'summed-Gram witness is nonmatched')
                    delta = counts[li][groups[g].index(coordinate)]
                    first_witness = dict(groups=[g, h], shared_coordinates=common, survivor_indices=[li, ri],
                        raw_words=[[words[i] for i in survivors[j]] for j in (li, ri)], colour_counts=[counts[li], counts[ri]],
                        deviations_cancel=True, only_row_margins_claimed=True,
                        violated_full_Gram_marginal=dict(coordinates=[coordinate, b], isolating_group=g, deviation=[x-1 for x in delta]))
            need(compatible >= 22500 and compatible-exact_two == 22500, 'exact balanced150x150 subpopulation')
            pair_records.append(dict(groups=[g, h], shared_coordinates=common,
                required_masks=[side[0] for side in sides], individual_domain_sizes=[len(side[1]) for side in sides],
                individual_unbalanced_sizes=[sum(balanced_masks[i] != 63 for i in side[1]) for side in sides],
                deviation_profile_products=terms, row_margin_compatible_option_pairs=compatible,
                both_genuinely_unbalanced_option_pairs=exact_two, intergroup_Gram_or_caps_checked=False))
            need(time.monotonic()-started < 120, 'bounded exception census allocation')
        save(out/'two_group_row_margin_census.json', dict(records=pair_records, first_local_cancellation_witness=first_witness,
            first_witness_null_reason=None if first_witness else 'No genuinely unbalanced row-margin pair found.',
            scope='Only row margins, local Gram upper bounds and within-group caps; no full-Gram or intergroup compatibility claim.'))
        summary = dict(status='CANDIDATE_FEW_EXCEPTION_THEOREM_AND_ROW_ONLY_CENSUS', timestamp=datetime.now(timezone.utc).isoformat(), inputs_sha256=inputs,
            outputs_sha256={key(p): sha(p) for p in out.iterdir() if p.is_file()}, full_marginal_matrices=12, nonzero_minors=total_minors,
            candidate_at_most_three_implies_balanced=True, local_domain=31110, required_balance_masks=64, actual_support_pairs=190,
            row_margin_pairs_allowing_two_unbalanced=sum(r['both_genuinely_unbalanced_option_pairs'] > 0 for r in pair_records),
            required_mask_domain_count_histogram=dict(Counter(c['count'] for c in catalogs)),
            intersection_histogram={str(k): v for k, v in sorted(histogram.items())},
            solver_calls=0, independent_approval=False, target_resolution=False, elapsed_seconds=time.monotonic()-started,
            scope='Separate full-Gram few-exception implication and weaker row-margin-only local-domain census on one saved support; neither is an unrestricted target result.')
        save(out/'summary.json', summary)
        print(json.dumps({k: v for k, v in summary.items() if k not in ('inputs_sha256', 'outputs_sha256')}))
    except BaseException as error:
        save(out/'failure.json', dict(error=repr(error), source_sha256=sha(Path(__file__))))
        raise


if __name__ == '__main__':
    main()
