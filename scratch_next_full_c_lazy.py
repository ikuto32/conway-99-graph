"""Bounded exact graph search at one prescribed integral compression C.

Every accepted solution must satisfy all SRG conditions. Lazy constraints
are only necessary upper bounds; no unconstrained candidate is a solution.
No failure here excludes other compressions or E0 values.
"""
from itertools import combinations
from pathlib import Path
import argparse
import hashlib
import json
import sys
import time

sys.path.insert(0, str(Path('.ortools').resolve()))
from ortools.sat.python import cp_model


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seconds', type=float, default=120)
    ap.add_argument('--step-seconds', type=float, default=10)
    ap.add_argument('--batch', type=int, default=100)
    args = ap.parse_args()
    inp = Path('scratch_resume_integral_compression.json')
    raw = inp.read_bytes()
    c = json.loads(raw)['C']
    supports = list(combinations(range(7), 2))
    labels = [(2*a+s, 2*b+t) for a, b in supports for s in range(2) for t in range(2)]
    model = cp_model.CpModel()
    variables = {(u, v): model.new_bool_var(f'e_{u}_{v}') for u, v in combinations(range(84), 2)
                 if u//4 != v//4}
    def edge(u, v):
        return variables.get(tuple(sorted((u, v))))
    for f, h in combinations(range(21), 2):
        model.add(sum(edge(u, v) for u in range(4*f, 4*f+4)
                      for v in range(4*h, 4*h+4)) == c[f][h])
    for u in range(84):
        for symbol in range(14):
            model.add(sum(edge(u, v) for v in range(84)
                          if edge(u, v) is not None and symbol in labels[v])
                      == (1 if symbol//2 in supports[u//4] else 2))
    # The independent swaps of exact symbols in each support group preserve
    # C and are transitive on the16 possible edges between disjoint fibres.
    # Such a block has C>0, so fixing one representative edge is exhaustive
    # within this one prescribed-C search.
    h = next(i for i, s in enumerate(supports) if not set(s) & set(supports[0]))
    model.add(edge(0, 4*h) == 1)
    constrained = set()
    products = 0
    def add_pair(u, v):
        nonlocal products
        if (u, v) in constrained:
            return
        terms = []
        direct = edge(u, v)
        if direct is not None:
            terms.append(direct)
        for w in range(84):
            a, b = edge(u, w), edge(v, w)
            if a is not None and b is not None:
                p = model.new_bool_var(f'p_{u}_{v}_{w}')
                model.add_bool_or([a.Not(), b.Not(), p])
                terms.append(p)
                products += 1
        model.add(sum(terms) <= 2-len(set(labels[u]) & set(labels[v])))
        constrained.add((u, v))
    for u, v in combinations(range(84), 2):
        if u//4 == v//4:
            add_pair(u, v)
    start = time.monotonic()
    rounds = []
    best = None
    terminal = 'TIME_LIMIT'
    unknown_streak = 0
    candidate_full = None
    while time.monotonic()-start < args.seconds:
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = min(args.step_seconds*(1+unknown_streak),
                                                    args.seconds-(time.monotonic()-start))
        solver.parameters.num_search_workers = 1
        solver.parameters.random_seed = 141299+len(rounds)
        tick = time.monotonic()
        status = solver.solve(model)
        record = {'round': len(rounds), 'status': solver.status_name(status),
                  'elapsed_seconds': time.monotonic()-tick,
                  'constrained_pairs': len(constrained), 'product_variables': products}
        if status == cp_model.INFEASIBLE:
            terminal = 'FIXED_C_SOLVER_INFEASIBLE_NO_CHECKED_PROOF'
            rounds.append(record)
            print(json.dumps(record), flush=True)
            break
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            unknown_streak += 1
            rounds.append(record)
            print(json.dumps(record), flush=True)
            continue
        unknown_streak = 0
        selected = {pair for pair, var in variables.items() if solver.value(var)}
        neighbours = [set() for _ in range(84)]
        for u, v in selected:
            neighbours[u].add(v)
            neighbours[v].add(u)
        assert all(len(row) == 12 for row in neighbours)
        errors = []
        bad_pairs = 0
        for u, v in combinations(range(84), 2):
            residual = len(neighbours[u] & neighbours[v]) + int((u, v) in selected) \
                       - (2-len(set(labels[u]) & set(labels[v])))
            if residual:
                bad_pairs += 1
            if residual > 0:
                assert (u, v) not in constrained
                errors.append((residual, u, v))
        record.update({'selected_outer_edges': len(selected), 'bad_outer_pairs': bad_pairs,
                       'violated_upper_caps': len(errors)})
        if best is None or bad_pairs < best['bad_outer_pairs']:
            best = {'bad_outer_pairs': bad_pairs, 'edges_outer_zero_based': sorted(map(list, selected))}
        if not errors:
            assert bad_pairs == 0
            candidate_full = {(1, s+2) for s in range(14)} | {(2*g+2, 2*g+3) for g in range(7)}
            candidate_full |= {(s+2, x+16) for x, label in enumerate(labels) for s in label}
            candidate_full |= {(u+16, v+16) for u, v in selected}
            from validate_submission import verify_edges
            checked = verify_edges(sorted(candidate_full))
            assert checked['valid'], checked
            terminal = 'VERIFIED_99_VERTEX_SRG_CANDIDATE'
            record['validation'] = checked
        else:
            for _, u, v in sorted(errors, reverse=True)[:args.batch]:
                add_pair(u, v)
        rounds.append(record)
        print(json.dumps(record), flush=True)
        if candidate_full is not None:
            break
    result = {'status': terminal, 'elapsed_seconds': time.monotonic()-start,
              'compression_sha256': hashlib.sha256(raw).hexdigest(),
              'safe_fixed_edge_outer_indices': [0, 4*h],
              'scope': 'All reciprocal adjacency completions of one fixed C, with safe sign-swap normalization. Not an E0-wide search or global nonexistence proof.',
              'rounds': rounds, 'best_unverified_candidate': best}
    if candidate_full is not None:
        result['edges'] = sorted(map(list, candidate_full))
    Path('scratch_next_full_c_lazy.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('rounds','best_unverified_candidate','edges')}), flush=True)


if __name__ == '__main__':
    main()
