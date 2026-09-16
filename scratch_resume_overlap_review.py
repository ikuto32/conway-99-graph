"""Independent fixed-lift review and a bounded linear-relaxation proof attempt."""
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / '.deps'))
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Solver


def main():
    started = time.monotonic()
    cp = HERE / 'scratch_resume_integral_compression.json'
    lp = HERE / 'scratch_resume_overlap_lift.json'
    c = json.loads(cp.read_bytes())['C']
    lift = json.loads(lp.read_bytes())
    assert lift['input_sha256'] == sha256(cp.read_bytes()).hexdigest()
    supports = sorted(combinations(range(7), 2))
    labels = sorted((a, b) for a in range(14) for b in range(a + 1, 14) if a//2 != b//2)
    labels.sort(key=lambda z: (z[0]//2, z[1]//2, *z))
    known = {tuple(e) for e in lift['overlap_edges_outer_zero_based']}
    assert len(known) == len(lift['overlap_edges_outer_zero_based']) == 168
    outer = [set() for _ in range(84)]
    full = {(0, v) for v in range(1, 15)} | {(v, v+1) for v in range(1, 15, 2)}
    full |= {(a+1, u+15) for u, lab in enumerate(labels) for a in lab}
    totals = Counter()
    for u, v in known:
        assert type(u) is int and type(v) is int and 0 <= u < v < 84
        assert len(set(supports[u//4]) & set(supports[v//4])) == 1
        outer[u].add(v)
        outer[v].add(u)
        full.add((u+15, v+15))
        totals[u//4, v//4] += 1
    assert all(len(row) == 4 for row in outer)
    for f, h in combinations(range(21), 2):
        if set(supports[f]) & set(supports[h]):
            assert totals[f, h] == c[f][h]
    rows = [set() for _ in range(99)]
    for u, v in full:
        rows[u].add(v)
        rows[v].add(u)
    assert len(full) == 357
    assert all(len(rows[u] & rows[v]) <= (1 if v in rows[u] else 2)
               for u, v in combinations(range(99), 2))
    for u in range(84):
        for symbol in range(14):
            count = sum(symbol in labels[v] for v in outer[u])
            assert count == 1 if symbol//2 in supports[u//4] else count <= 2

    pool = IDPool()
    variables = {(u, v): pool.id(('edge', u, v)) for u, v in combinations(range(84), 2)
                 if not set(supports[u//4]) & set(supports[v//4])}
    clauses = []
    constraint_count = Counter()

    def equation(terms, target, kind, equality=True):
        # Constants are separated before this function. Every listed term
        # is an edge Boolean. Repeated terms would be separate multiplicity.
        assert len(set(terms)) == len(terms)
        constraint_count[kind] += 1
        if target < 0 or equality and target > len(terms):
            clauses.append([])
        elif not terms:
            assert not equality or target == 0
        else:
            encoder = CardEnc.equals if equality else CardEnc.atmost
            clauses.extend(encoder(lits=terms, bound=target, vpool=pool,
                                   encoding=EncType.seqcounter).clauses)

    for u in range(84):
        for symbol in range(14):
            target = 1 if symbol//2 in supports[u//4] else 2
            target -= sum(symbol in labels[v] for v in outer[u])
            terms = [variables[tuple(sorted((u, v)))] for v in range(84)
                     if symbol in labels[v] and tuple(sorted((u, v))) in variables]
            equation(terms, target, 'label_quota')
    for f, h in combinations(range(21), 2):
        if not set(supports[f]) & set(supports[h]):
            equation([variables[u, v] for u in range(4*f, 4*f+4)
                      for v in range(4*h, 4*h+4)], c[f][h], 'block_total')
    for u, v in combinations(range(84), 2):
        target = 2 - len(set(labels[u]) & set(labels[v])) - int((u, v) in known)
        target -= len(outer[u] & outer[v])
        terms = [variables[u, v]] if (u, v) in variables else []
        for w in outer[u]:
            edge = tuple(sorted((v, w)))
            if edge in variables:
                terms.append(variables[edge])
        for w in outer[v]:
            edge = tuple(sorted((u, w)))
            if edge in variables:
                terms.append(variables[edge])
        equation(terms, target, 'linear_pair_cap', equality=False)
    cnf_path = HERE / 'scratch_resume_overlap_review.cnf'
    cnf_path.write_text(f'p cnf {pool.top} {len(clauses)}\n' +
                        ''.join(' '.join(map(str, clause)) + ' 0\n' for clause in clauses), encoding='ascii', newline='\n')
    result = {
        'status': 'INDEPENDENT_FIXED_OVERLAP_PARTIAL_AUDIT_PASS',
        'lift_sha256': sha256(lp.read_bytes()).hexdigest(),
        'compression_sha256': sha256(cp.read_bytes()).hexdigest(),
        'exposed_edges': len(full), 'pair_caps_checked': 4851,
        'degree_histogram': dict(Counter(map(len, rows))),
        'relaxation': 'exact label quotas and disjoint C block totals; pair upper caps drop all unknown-times-unknown terms',
        'edge_variables': len(variables), 'cnf_variables': pool.top,
        'clauses': len(clauses), 'constraint_counts': dict(constraint_count),
        'cnf_sha256': sha256(cnf_path.read_bytes()).hexdigest(),
        'scope': 'Only this fixed overlap lift and this C; no exclusion of all E0=0 or all sharp compressions.'}
    with Solver(name='cadical195', bootstrap_with=clauses, with_proof=True) as solver:
        solver.conf_budget(100000)
        answer = solver.solve_limited()
        result['linear_relaxation_status'] = 'UNKNOWN' if answer is None else 'SAT' if answer else 'UNSAT'
        result['solver_stats'] = solver.accum_stats()
        if answer is False:
            proof = HERE / 'scratch_resume_overlap_review.drat'
            proof.write_text('\n'.join(solver.get_proof()) + '\n', encoding='ascii', newline='\n')
            result['proof_sha256'] = sha256(proof.read_bytes()).hexdigest()
            checker = HERE / 'tools/drat-trim/drat-trim.exe'
            checked = subprocess.run([str(checker), str(cnf_path), str(proof), '-t', '20'],
                                     text=True, capture_output=True, timeout=25, check=False)
            transcript = checked.stdout + checked.stderr
            (HERE / 'scratch_resume_overlap_review_drat.log').write_text(transcript, encoding='utf-8')
            result['proof_checked'] = checked.returncode == 0 and 's VERIFIED' in transcript
            result['proof_checker_sha256'] = sha256(checker.read_bytes()).hexdigest()
            result['proof_checker_exit_code'] = checked.returncode
    result['elapsed_seconds'] = time.monotonic()-started
    (HERE / 'scratch_resume_overlap_review.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
