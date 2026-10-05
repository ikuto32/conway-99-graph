"""Independent finite falsification controls for the separate written rank audit.

No hypothetical target is supplied or constructed. General mathematical proof
comes from the written audit, not enumeration of these small controls.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import itertools
import json
from pathlib import Path
import platform
import subprocess
import sys
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
NOTE = 'docs/CANDIDATE_20261003_TRIANGLE_INCIDENCE_GRIESMER_V1.md'
NOTE_SHA = '06c72ef3ed8d1f3167336420016e2d0ec86f481ebe97d5910ff154c6a44d9c16'


def need(ok, why):
    if not ok:
        raise ValueError(why)


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write(path, obj):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(obj, stream, indent=2)
        stream.write('\n')


def span(rows):
    words = {0}
    for row in rows:
        words |= {word ^ row for word in words}
    return words


def all_codes(n):
    # Every binary subspace has one unique RREF generator matrix in this order.
    for t in range(n + 1):
        for pivots in itertools.combinations(range(n), t):
            free = [j for j in range(n) if j not in pivots]
            positions = [(i, j) for i, p in enumerate(pivots) for j in free if j > p]
            for mask in range(1 << len(positions)):
                rows = [1 << p for p in pivots]
                for bit, (i, j) in enumerate(positions):
                    if mask >> bit & 1:
                        rows[i] |= 1 << j
                yield rows


def residual(words, n, chosen):
    need(chosen in words and chosen != 0, 'chosen nonzero codeword')
    d = min(word.bit_count() for word in words if word)
    need(chosen.bit_count() == d, 'puncture a minimum-weight word')
    outside_mask = ((1 << n) - 1) ^ chosen
    kernel = {word for word in words if word & outside_mask == 0}
    image = {word & outside_mask for word in words}
    need(kernel == {0, chosen}, 'exact one-dimensional puncturing kernel')
    need(len(image) * 2 == len(words), 'dimension decreases by exactly one')
    if len(image) > 1:
        need(min(word.bit_count() for word in image if word) >= (d + 1) // 2,
             'exact residual minimum-distance bound')
    return len(image)


def graph_check(a, triples, k):
    n = len(a)
    need(all(len(row) == n and all(type(v) is int and v in (0, 1) for v in row) for row in a),
         'literal binary square')
    need(all(a[i][i] == 0 and sum(a[i]) == k for i in range(n)), 'diagonal and all degrees')
    need(all(a[i][j] == a[j][i] for i in range(n) for j in range(n)), 'symmetry')
    square = [[sum(a[i][v] * a[v][j] for v in range(n)) for j in range(n)] for i in range(n)]
    need(all(square[i][j] == ((k - 2 if i == j else 0) - a[i][j] + 2)
             for i in range(n) for j in range(n)), 'integer lambda1 mu2 identity')
    actual = [list(t) for t in itertools.combinations(range(n), 3)
              if all(a[i][j] for i, j in itertools.combinations(t, 2))]
    need(triples == actual, 'complete literal triangle incidence')
    return square


def controls(deadline, out):
    n = 9
    a = [[int(i != j and (i // 3 == j // 3 or i % 3 == j % 3)) for j in range(n)]
         for i in range(n)]
    triples = [list(range(3 * r, 3 * r + 3)) for r in range(3)]
    triples += [[c, c + 3, c + 6] for c in range(3)]
    triples.sort()
    square = graph_check(a, triples, 4)
    code = [word for word in range(1 << n)
            if all(sum(word >> v & 1 for v in t) % 2 == 0 for t in triples)]
    need(len(code) == 16, 'rook kernel dimension four')
    histogram = dict(sorted(Counter(word.bit_count() for word in code).items()))
    need(histogram == {0: 1, 4: 9, 6: 6}, 'complete rook kernel weight distribution')
    words_checked = 0
    for word in code:
        if not word:
            continue
        inside = [v for v in range(n) if word >> v & 1]
        outside = [v for v in range(n) if v not in inside]
        s = len(inside)
        rv = [sum(a[v][u] for u in inside) for v in outside]
        need(s % 2 == 0 and all(sum(a[v][u] for u in inside) == 2 for v in inside),
             'induced half-degree and even support')
        need(all(value % 2 == 0 for value in rv) and sum(rv) == 2 * s,
             'outside parity and exact cut')
        need(sum(value * value for value in rv) == 2 * s * (s - 2), 'generalized exact moment')
        need((2 * s) ** 2 <= len(outside) * sum(value * value for value in rv), 'Cauchy moment')
        need(sum(square[i][j] for i in inside for j in inside) == 2 * s * s,
             'independent scalar quadratic form')
        words_checked += 1
    failures = []
    for label, graph, inc in [('missing_triangle', a, triples[:-1]),
                             ('duplicate_triangle', a, triples + [triples[0]]),
                             ('altered_incidence', a, [[0, 1, 4], *triples[1:]])]:
        try:
            graph_check(graph, inc, 4)
        except ValueError as exc:
            failures.append(dict(case=label, diagnostic=str(exc)))
        else:
            raise ValueError('invalid incidence control accepted')
    bad_a = [row[:] for row in a]
    bad_a[0][1] = bad_a[1][0] = 0
    try:
        graph_check(bad_a, triples, 4)
    except ValueError as exc:
        failures.append(dict(case='altered_graph', diagnostic=str(exc)))
    else:
        raise ValueError('invalid graph control accepted')
    generic = span([1, 6])
    need(min(w.bit_count() for w in generic if w) == 1,
         'general binary code does not satisfy incidence-derived distance36')
    try:
        residual(generic, 3, 7)
    except ValueError as exc:
        need(str(exc) == 'puncture a minimum-weight word', 'exact invalid-puncturing diagnostic')
        failures.append(dict(case='nonminimum_puncturing', diagnostic=str(exc)))
    else:
        raise ValueError('nonminimum puncturing accepted')
    # All subspaces for n<=6; finite calibration does not prove the general lemma.
    populations, total, checks = [], 0, 0
    for length in range(7):
        seen = set()
        for rows in all_codes(length):
            words = span(rows)
            signature = tuple(sorted(words))
            need(signature not in seen, 'unique RREF generated subspace')
            seen.add(signature)
            t = len(rows)
            need(len(words) == 1 << t, 'RREF independent basis')
            if t:
                d = min(word.bit_count() for word in words if word)
                need(length >= sum((d + (1 << i) - 1) // (1 << i) for i in range(t)),
                     'finite exact Griesmer inequality')
                for chosen in words:
                    if chosen.bit_count() == d:
                        residual(words, length, chosen)
                        checks += 1
            total += 1
            if total % 100 == 0:
                need(not deadline.status()['stop_required'], 'not completed within allocated budget')
        populations.append(dict(length=length, subspaces=len(seen)))
    need([r['subspaces'] for r in populations] == [1, 2, 5, 16, 67, 374, 2825],
         'complete independent known small Gaussian populations')
    even_weights = [s for s in range(1, 99) if s % 2 == 0
                   and 49 * s <= (99 - s) * 2 * (s - 22)]
    need(even_weights == list(range(36, 61, 2)), 'literal integer target moment bounds')
    terms = [(36 + (1 << i) - 1) // (1 << i) for i in range(33)]
    need(sum(terms) == 100 and sum(terms[:-1]) == 99, 'dimension33 contradiction threshold')
    rec = dict(positive_graph='SRG(9,4,1,2) rook graph', scalar_matrix_entries=81,
               complete_kernel_population=16, nonzero_kernel_words_checked=words_checked,
               weight_histogram=histogram, strict_corrupt_controls=failures,
               general_code_without_incidence_not_given_distance36=True,
               small_binary_code_populations=populations, total_subspaces=total,
               minimum_word_residual_checks=checks, target_even_weight_set=even_weights,
               target_dimension33_griesmer_terms=terms, target_dimension33_sum=100,
               control_scope='Finite known-valid and deliberately invalid controls, not general proof.')
    write(out / 'controls.json', rec)
    return rec


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--seconds', type=float, required=True)
    args = ap.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='Finite3290binarysubspaces n<=6, rook9 fullkernel and five strict corrupt controls; exact integer operations, no solver/search;100worker inside120outer leaves20shutdown.')
    out = args.out.resolve()
    need(out.is_relative_to(ROOT), 'workspace output')
    out.mkdir(parents=True, exist_ok=False)
    calibrated = controls(deadline, out)
    note = ROOT / NOTE
    need(sha(note) == NOTE_SHA, 'exact discovery statement')
    audit = ROOT / 'acceleration/audit_20261003_incidence_griesmer_v1.md'
    need(audit.is_file(), 'separate complete written independent audit')
    pins = {p.relative_to(ROOT).as_posix(): sha(p) for p in
            [note, audit, Path(__file__), ROOT / 'acceleration/audit_20261003_incidence_griesmer_v1_spec.md',
             ROOT / 'acceleration/command_deadline.py', ROOT / 'pyproject.toml', ROOT / 'uv.lock', out / 'controls.json']}
    report = dict(status='INDEPENDENT_CONDITIONAL_TRIANGLE_INCIDENCE_GRIESMER_DERIVATION_V1_PASS',
                  timestamp=datetime.now(timezone.utc).isoformat(), producer='/root/structural', verifier='/root',
                  method='independent_derivation', command=[sys.executable, *sys.argv], cwd=str(ROOT),
                  source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                  python=platform.python_version(), inputs_sha256=pins,
                  exact_claim='Every binary symmetric zero-diagonal99matrix A satisfying A^2=12I-A+2J has triangle-incidence rank_GF2(B)>=67, equivalently dim ker(B^T)<=32.',
                  conditional_premise='Existence of a complete graph with the exact target integer identity remains UNKNOWN.',
                  minimum_rank=67, maximum_kernel_dimension=32,
                  nonzero_kernel_weights=list(range(36, 61, 2)),
                  written_audit=audit.relative_to(ROOT).as_posix(), controls=calibrated,
                  formalization=None, formalization_reason='Complete ordinary written proof, no proof-assistant formalization.',
                  target_resolution='NONE', graph_constructed=False, target_nonexistence=False,
                  rank_upper72_status='UNKNOWN; refuted generic lemma supplies no such premise.',
                  shared_components=['Same stated SRG hypotheses and classical residual-code inequality; independent scalar finite implementation, no producer imports.', 'Python exact integer runtime and pinned deadline helper.'],
                  limitations=['Conditional rank lower bound only; no rank upper bound or contradiction.', 'Finite controls do not constitute exhaustive verification of the general theorem.', 'Novelty and peer review not established; archival weight-bound overlap disclosed in pinned source.'], deadline=deadline.status())
    write(out / 'summary.json', report)
    print(json.dumps(dict(status=report['status'], controls_subspaces=calibrated['total_subspaces'],
                          residual_checks=calibrated['minimum_word_residual_checks'], target_resolution='NONE')))


if __name__ == '__main__':
    main()
