"""Independent raw-pattern, integer-minor and parity audit; no producer imports."""
from datetime import datetime, timezone
from itertools import combinations, permutations, product
from pathlib import Path
import argparse
import copy
import hashlib
import json
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT/'acceleration/results/20260930_prism_unpaired_design_pilot/model.json'
PRODUCER = ROOT/'acceleration/results/20260930_prism_unpaired_kernel'
SUMMARY_SHA = '46ab1f208faa608a502df7ffcd8963afca08904db22894c96b56a131b1a618f0'
RAW_SHA = '24beb62eecb4eee61501b597734d91be6325958d002af6ad1e3ab16f1e287974'
AUDIT = ROOT/'docs/AUDIT_20260930_PRISM_UNPAIRED_KERNEL.md'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def key(p):
    return Path(p).resolve().relative_to(ROOT).as_posix()


def save(p, data):
    p.write_text(json.dumps(data, indent=2)+'\n', encoding='utf-8')


def determinant(a):
    """Integer Bareiss determinant with pivoting; no Fraction or producer algebra."""
    n = len(a)
    need(all(len(r) == n for r in a), 'square determinant input')
    if not n:
        return 1
    b = [r.copy() for r in a]
    sign, divisor = 1, 1
    for k in range(n-1):
        pivot = next((i for i in range(k, n) if b[i][k]), None)
        if pivot is None:
            return 0
        if pivot != k:
            b[pivot], b[k] = b[k], b[pivot]
            sign = -sign
        value = b[k][k]
        for i in range(k+1, n):
            for j in range(k+1, n):
                numerator = b[i][j]*value-b[i][k]*b[k][j]
                quotient, remainder = divmod(numerator, divisor)
                need(remainder == 0, 'Bareiss exact division')
                b[i][j] = quotient
            b[i][k] = 0
        divisor = value
    return sign*b[-1][-1]


def independent_rows_mod(a, modulus=101):
    """Find row indices for a minor; final rank evidence is its integer determinant."""
    basis, chosen = [], []
    for i, row in enumerate(a):
        reduced = [x % modulus for x in row]
        for pivot, previous in basis:
            scale = reduced[pivot]
            reduced = [(x-scale*y) % modulus for x, y in zip(reduced, previous)]
        pivot = next((j for j, x in enumerate(reduced) if x), None)
        if pivot is not None:
            inverse = pow(reduced[pivot], -1, modulus)
            basis.append((pivot, [x*inverse % modulus for x in reduced]))
            chosen.append(i)
    return chosen


def certify(matrix, vector):
    need(len(matrix) == 15 and all(len(r) == 10 for r in matrix), '15x10 shape')
    need(len(vector) == 10 and all(type(x) is int and x in (-1, 1) for x in vector), 'full-support unit vector')
    image = [sum(x*y for x, y in zip(r, vector)) for r in matrix]
    need(image == [0]*15, 'literal matrix-kernel product')
    columns = list(range(9))
    rows = independent_rows_mod([r[:9] for r in matrix])
    need(len(rows) == 9, 'nine independent selected rows')
    minor = [[matrix[i][j] for j in columns] for i in rows]
    det = determinant(minor)
    need(det != 0, 'nonzero exact9minor')
    return {'minor_rows': rows, 'minor_columns': columns, 'minor_matrix': minor,
            'minor_determinant': det, 'kernel_vector': vector, 'matrix_times_kernel': image,
            'rank_lower_bound': 9, 'rank_upper_bound': 9, 'rank': 9,
            'rank_reason': 'Nonzero9minor gives rank>=9; nonzero10-coordinate kernel vector gives rank<=9.'}


def reject(call):
    try:
        call()
    except (ValueError, AssertionError, IndexError, TypeError):
        return True
    raise ValueError('corrupted control unexpectedly accepted')


def controls():
    determinants = 0
    for entries in product((-1, 0, 1), repeat=4):
        a = [list(entries[:2]), list(entries[2:])]
        need(determinant(a) == entries[0]*entries[3]-entries[1]*entries[2], '2x2 determinant control')
        determinants += 1
    for seed in range(100):
        a = [[((seed*(i+1)+3*j+7*i*j) % 7)-3 for j in range(3)] for i in range(3)]
        literal = sum((-1)**sum(p[i] > p[j] for i in range(3) for j in range(i+1, 3))
                      * a[0][p[0]]*a[1][p[1]]*a[2][p[2]] for p in permutations(range(3)))
        need(determinant(a) == literal, '3x3 Leibniz determinant control')
        determinants += 1
    a = [[int(i == j) for j in range(9)]+[1] for i in range(9)]+[[0]*10 for _ in range(6)]
    positive = certify(a, [-1]*9+[1])
    need(positive['minor_determinant'] == 1, 'known rank9 fixture')
    corruptions = []
    corruptions.append(reject(lambda: certify(a, [1]*10)))
    corruptions.append(reject(lambda: certify([[0]*10 for _ in range(15)], [-1]*9+[1])))
    for bits in product((0, 1), repeat=3):
        need(sum(bits[i] != bits[j] for i, j in combinations(range(3), 2)) in (0, 2), 'triple parity')
    even_cases = 0
    for a0, b0, a1, b1 in product((0, 1), repeat=4):
        counts = [2*int((a0, b0) == pair)+2*int((a1, b1) == pair) for pair in product((0, 1), repeat=2)]
        need(all(x % 2 == 0 for x in counts) and counts != [1]*4, 'same-cell even count')
        even_cases += 1
    return {'determinant_cases': determinants, 'known_rank9_positive': positive,
            'basic_corruptions_rejected': len(corruptions), 'triple_parity_cases': 8, 'same_cell_even_cases': even_cases}


def reconstruct_patterns(raw):
    matchings = [[[5, r], [(r+1) % 5, (r-1) % 5], [(r+2) % 5, (r-2) % 5]] for r in range(5)]
    need(raw['matchings'] == matchings, 'independent round-robin reconstruction')
    need(sorted(tuple(sorted(e)) for m in matchings for e in m) == list(combinations(range(6), 2)), 'K6 edge partition')
    patterns = []
    for mi, matching in enumerate(matchings):
        for labels in permutations(range(3)):
            cells = [None]*6
            for pair, cell in zip(matching, labels):
                for a in pair:
                    cells[a] = cell
            patterns.append({'matching': mi, 'cells': cells})
    need(raw['patterns'] == patterns, 'all30 ordered cell patterns')
    need(len(raw['columns']) == 60, '60 repeated pattern columns')
    for i, c in enumerate(raw['columns']):
        need(c == {'pattern': i//2, 'repeat': i % 2, 'cells': patterns[i//2]['cells'],
                   'bit_variables': list(range(6*i+1, 6*i+7))}, 'raw independent-bit column mapping')
    need(raw['global_complement_pairing_required'] is False and raw['fixed_bit_normalization'] is False, 'unpaired scope')
    return [x['cells'] for x in patterns]


def core_gram():
    # Rows have index12*cell+2*component+bit. Each core component is a triangular prism.
    coords = [(g, a, b) for g in range(3) for a in range(6) for b in range(2)]
    b = [[int(a == c and ((g == h and bit != other) or (g != h and bit == other)))
          for h, c, other in coords] for g, a, bit in coords]
    need(all(sum(r) == 3 for r in b), 'raw cubic prism core')
    gram = [[12*int(i == j)-b[i][j]-sum(b[i][k]*b[k][j] for k in range(36))+2-int(coords[i][0] == coords[j][0])
             for j in range(36)] for i in range(36)]
    for i, (g, a, bit) in enumerate(coords):
        for j, (h, c, other) in enumerate(coords):
            if a != c:
                need(gram[i][j] == (1 if g == h else 2), 'bit-independent cross-component prescribed Gram')
    return b, gram


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    need(sha(RAW) == RAW_SHA and sha(PRODUCER/'summary.json') == SUMMARY_SHA, 'frozen research inputs')
    raw = json.loads(RAW.read_bytes())
    producer = json.loads((PRODUCER/'summary.json').read_bytes())
    calibration = controls()
    patterns = reconstruct_patterns(raw)
    b, gram = core_gram()
    records, corruptions, inputs = [], [], [RAW, PRODUCER/'summary.json', Path(__file__), AUDIT, ROOT/'uv.lock', ROOT/'pyproject.toml']
    same_cell = []
    for a, bcomp in combinations(range(6), 2):
        for g in range(3):
            selected = [i for i, p in enumerate(patterns) if p[a] == p[bcomp] == g]
            need(len(selected) == 2, 'all45same-cell intersections')
            same_cell.append({'components': [a, bcomp], 'cell': g, 'patterns': selected})
    for a in range(6):
        for g in range(3):
            path = PRODUCER/('component_%d_cell_%d.json' % (a, g))
            need(sha(path) == producer['outputs_sha256'][key(path)], 'certificate hash binding')
            inputs.append(path)
            data = json.loads(path.read_bytes())
            selected = [i for i, p in enumerate(patterns) if p[a] == g]
            labels = [[bcomp, h] for bcomp in range(6) if bcomp != a for h in range(3)]
            matrix = [[int(patterns[t][bcomp] == h) for t in selected] for bcomp, h in labels]
            need(len(selected) == 10, 'ten patterns per component-cell')
            need(data['component'] == a and data['cell'] == g and data['selected_pattern_indices'] == selected
                 and data['row_labels'] == labels and data['matrix'] == matrix, 'literal matrix and coordinate reconstruction')
            for row, (bcomp, h) in zip(matrix, labels):
                need(sum(row) == (2 if g == h else 4), 'marginal RHS equals pattern count')
            basis = data['certificate']['nullbasis']
            need(len(basis) == 1, 'one proposed generator')
            need(all(v[1] == 1 for v in basis[0]), 'integral proposed generator')
            v = [entry[0] for entry in basis[0]]
            result = certify(matrix, v)
            need(data['certificate']['rank'] == 9, 'exact claimed rank')
            result.update(component=a, cell=g, selected_pattern_indices=selected, matrix=matrix,
                          producer_certificate_sha256=sha(path), producer_rref_operations_reused=False)
            save(out/('minor_%d_%d.json' % (a, g)), result)
            records.append({k: result[k] for k in ('component', 'cell', 'rank', 'minor_rows', 'minor_columns', 'minor_determinant')})
            bad = v.copy()
            bad[0] *= -1
            corruptions.append(reject(lambda matrix=matrix, bad=bad: certify(matrix, bad)))
            altered = copy.deepcopy(matrix)
            altered[0][0] ^= 1
            corruptions.append(reject(lambda altered=altered, matrix=matrix: need(altered == matrix, 'changed raw matrix')))
            corruptions.append(reject(lambda result=result: need(result['minor_determinant']+1 == determinant(result['minor_matrix']), 'changed determinant')))
    # Independent finite implication controls supplement the written arbitrary-u argument.
    for v in (-1, 1):
        need([s for s in range(-4, 5) if s*v in (-1, 0, 1)] == [-1, 0, 1], 'unit-coordinate scalar restriction')
    pair_count_sums = [sum(gram[12*g+2*a+x][12*h+2*bcomp+y] for g in range(3) for h in range(3))
                       for a, bcomp in combinations(range(6), 2) for x, y in product((0, 1), repeat=2)]
    need(pair_count_sums == [15]*60, 'all60 global pair-bit counts')
    save(out/'controls.json', {**calibration, 'research_certificate_corruptions_rejected': len(corruptions)})
    save(out/'raw_reconstruction.json', {'patterns': patterns, 'core_adjacency': b, 'prescribed_gram': gram,
        'same_cell_intersections': same_cell, 'global_pair_bit_counts': pair_count_sums})
    summary = {'status': 'INDEPENDENT_PRISM_UNPAIRED_FIVE_MATCHING_EXCLUSION_PASS',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        'command': [sys.executable, *sys.argv], 'working_directory': str(ROOT), 'python': platform.python_version(),
        'verifier': '/root/structural_attack', 'checking_path': 'Independent raw round-robin/core reconstruction, literal signed kernel products, integer Bareiss9minors and written parity argument; no producer-code imports.',
        'claim_id': 'C-SIX-PRISM-FIVE-MATCHING-UNPAIRED-DESIGN-EXCLUSION', 'claim_revision': 1,
        'exact_statement': producer['statement'], 'reviewed_producer_summary_sha256': SUMMARY_SHA,
        'matrices_completely_checked': 18, 'records': records, 'rank_method': 'Nonzero exact9minor plus nonzero full-support kernel; no reliance on producer elimination trace.',
        'written_audit': key(AUDIT), 'inputs_sha256': {key(p): sha(p) for p in inputs},
        'outputs_sha256': {key(p): sha(p) for p in sorted(out.iterdir()) if p.is_file()},
        'elapsed_seconds': time.monotonic()-start,
        'scope': 'Exactly30specified round-robin cell patterns, each repeated twice, with all360bits free; fixed six-prism core.',
        'limitations': ['Not arbitrary cell patterns or every factor for the six-prism core.', 'No unrestricted target exclusion or automorphism/containment premise.',
                        'Native UNKNOWN run and its SAT encoding are not proof premises; no solver launched.', 'No novelty or external peer-review assertion.'],
        'trusted_components': ['CPython integer arithmetic and standard library', 'Raw artifact identity by SHA256', 'Written matrix/block and parity reasoning']}
    save(out/'summary.json', summary)
    print(json.dumps({'status': summary['status'], 'matrices': 18, 'corruptions_rejected': len(corruptions)+2,
                      'summary_sha256': sha(out/'summary.json')}))


if __name__ == '__main__':
    main()
