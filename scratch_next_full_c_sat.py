"""Incremental SAT construction attempt for the entire graph at one fixed C.

The solver retains learnt clauses when necessary pair caps are added.
An output candidate is only valid after all99 degree/4851 pair checks pass.
"""
from itertools import combinations
from pathlib import Path
import hashlib
import json
import sys
import time

sys.path.insert(0, str(Path('.deps').resolve()))
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Solver


def main():
    inp = Path('scratch_resume_integral_compression.json')
    raw = inp.read_bytes()
    c = json.loads(raw)['C']
    supports = list(combinations(range(7), 2))
    labels = [(2*a+s, 2*b+t) for a, b in supports for s in range(2) for t in range(2)]
    pool = IDPool()
    variables = {(u, v): pool.id(('edge', u, v)) for u, v in combinations(range(84), 2) if u//4 != v//4}
    def edge(u, v):
        return variables.get(tuple(sorted((u, v))))
    clauses = []
    for f, h in combinations(range(21), 2):
        terms = [edge(u, v) for u in range(4*f, 4*f+4) for v in range(4*h, 4*h+4)]
        clauses += CardEnc.equals(terms, c[f][h], vpool=pool, encoding=EncType.seqcounter).clauses
    for u in range(84):
        for symbol in range(14):
            terms = [edge(u, v) for v in range(84) if edge(u, v) is not None and symbol in labels[v]]
            quota = 1 if symbol//2 in supports[u//4] else 2
            clauses += CardEnc.equals(terms, quota, vpool=pool, encoding=EncType.seqcounter).clauses
    h = next(i for i, s in enumerate(supports) if not set(s) & set(supports[0]))
    clauses.append([edge(0, 4*h)])
    constrained = set()
    rounds = []
    best = None
    terminal = 'TIME_LIMIT_UNKNOWN'
    start = time.monotonic()
    proof = None
    full_edges = None
    with Solver(name='cadical195', bootstrap_with=clauses, with_proof=True) as solver:
        while time.monotonic()-start < 120:
            solver.conf_budget(1000)
            tick = time.monotonic()
            answer = solver.solve_limited()
            rec = {'round': len(rounds), 'answer': answer, 'call_seconds': time.monotonic()-tick,
                   'constrained_pairs': len(constrained), 'variables': pool.top, 'clauses': len(clauses),
                   'stats': solver.accum_stats()}
            if answer is None:
                rounds.append(rec)
                if len(rounds) % 5 == 0 or len(rounds) <= 2:
                    print(json.dumps(rec), flush=True)
                continue
            if answer is False:
                terminal = 'FIXED_C_UNSAT_PROOF_NOT_YET_CHECKED'
                proof = solver.get_proof()
                rounds.append(rec)
                print(json.dumps(rec), flush=True)
                break
            positive = {v for v in solver.get_model() if v > 0}
            selected = {pair for pair, variable in variables.items() if variable in positive}
            adjacency = [set() for _ in range(84)]
            for u, v in selected:
                adjacency[u].add(v)
                adjacency[v].add(u)
            assert all(len(row) == 12 for row in adjacency)
            errors = []
            bad = 0
            for u, v in combinations(range(84), 2):
                residual = len(adjacency[u] & adjacency[v])+int((u, v) in selected) \
                           -(2-len(set(labels[u]) & set(labels[v])))
                bad += residual != 0
                if residual > 0:
                    assert (u, v) not in constrained
                    errors.append((residual, u, v))
            rec.update({'bad_outer_pairs': bad, 'upper_cap_violations': len(errors)})
            if best is None or bad < best['bad_outer_pairs']:
                best = {'bad_outer_pairs': bad, 'edges_outer_zero_based': sorted(map(list, selected))}
            if not errors:
                assert bad == 0
                full_edges = {(1, s+2) for s in range(14)} | {(2*g+2, 2*g+3) for g in range(7)}
                full_edges |= {(s+2, x+16) for x, label in enumerate(labels) for s in label}
                full_edges |= {(u+16, v+16) for u, v in selected}
                from validate_submission import verify_edges
                check = verify_edges(sorted(full_edges))
                assert check['valid'], check
                terminal = 'VERIFIED_99_VERTEX_SRG_CANDIDATE'
                rec['validation'] = check
                rounds.append(rec)
                print(json.dumps(rec), flush=True)
                break
            for _, u, v in sorted(errors, reverse=True)[:100]:
                terms = []
                added = []
                direct = edge(u, v)
                if direct is not None:
                    terms.append(direct)
                for w in range(84):
                    a, b = edge(u, w), edge(v, w)
                    if a is not None and b is not None:
                        p = pool.id(('and', u, v, w))
                        terms.append(p)
                        added.append([-a, -b, p])
                target = 2-len(set(labels[u]) & set(labels[v]))
                added += CardEnc.atmost(terms, target, vpool=pool, encoding=EncType.seqcounter).clauses
                clauses += added
                solver.append_formula(added)
                constrained.add((u, v))
            rounds.append(rec)
            print(json.dumps(rec), flush=True)
    result = {'status': terminal, 'elapsed_seconds': time.monotonic()-start,
              'compression_sha256': hashlib.sha256(raw).hexdigest(),
              'safe_sign_normalized_edge': [0, 4*h], 'rounds': rounds,
              'best_unverified_candidate': best,
              'scope': 'Full graph construction at one fixed integral C. No E0-wide exclusion. UNKNOWN is not UNSAT.'}
    if full_edges is not None:
        result['edges'] = sorted(map(list, full_edges))
    if proof is not None:
        cnf = Path('scratch_next_full_c_sat.cnf')
        drat = Path('scratch_next_full_c_sat.drat')
        cnf.write_bytes((f'p cnf {pool.top} {len(clauses)}\n'+''.join(' '.join(map(str, clause))+' 0\n' for clause in clauses)).encode('ascii'))
        drat.write_bytes(('\n'.join(proof)+'\n').encode('ascii'))
        result['cnf_sha256'] = hashlib.sha256(cnf.read_bytes()).hexdigest()
        result['proof_sha256'] = hashlib.sha256(drat.read_bytes()).hexdigest()
    Path('scratch_next_full_c_sat.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('rounds','best_unverified_candidate','edges')}), flush=True)


if __name__ == '__main__':
    main()
