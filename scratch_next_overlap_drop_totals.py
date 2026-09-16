"""Drop every disjoint block-total equation from the sealed fixed-lift CNF.

Rebuild the old encoding byte-for-byte and record semantic clause origins,
then retain only root-label quotas and linear pair caps. Single CaDiCaL
run, 100000-conflict bound. No old certificate is written.
"""
from collections import Counter, defaultdict
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
from scratch_resume_overlap_review_rup import read_cnf


def main():
    started = time.monotonic()
    lift_path = HERE / 'scratch_resume_overlap_lift.json'
    c_path = HERE / 'scratch_resume_integral_compression.json'
    known = set(map(tuple, json.loads(lift_path.read_bytes())['overlap_edges_outer_zero_based']))
    c = json.loads(c_path.read_bytes())['C']
    supports = list(combinations(range(7), 2))
    labels = [(2*a+s, 2*b+t) for a, b in supports for s in range(2) for t in range(2)]
    outer = [set() for _ in range(84)]
    for u, v in known:
        outer[u].add(v)
        outer[v].add(u)
    pool = IDPool()
    variables = {(u, v): pool.id(('edge', u, v)) for u, v in combinations(range(84), 2)
                 if not set(supports[u//4]) & set(supports[v//4])}
    clauses, origins, groups = [], [], []

    def emit(terms, target, kind, coordinate, equality=True):
        assert len(set(terms)) == len(terms)
        start = len(clauses)
        if target < 0 or equality and target > len(terms):
            encoded = [[]]
        elif not terms:
            assert not equality or target == 0
            encoded = []
        else:
            encoder = CardEnc.equals if equality else CardEnc.atmost
            encoded = encoder(lits=terms, bound=target, vpool=pool,
                              encoding=EncType.seqcounter).clauses
        group = {'kind': kind, 'coordinate': coordinate, 'target': target,
                 'equality': equality, 'terms': terms,
                 'clause_start': start, 'clause_stop': start + len(encoded)}
        origins.extend([len(groups)] * len(encoded))
        clauses.extend(encoded)
        groups.append(group)

    for u in range(84):
        for symbol in range(14):
            target = (1 if symbol//2 in supports[u//4] else 2) - sum(symbol in labels[v] for v in outer[u])
            terms = [variables[tuple(sorted((u, v)))] for v in range(84)
                     if symbol in labels[v] and tuple(sorted((u, v))) in variables]
            emit(terms, target, 'label_quota', [u, symbol])
    for f, h in combinations(range(21), 2):
        if not set(supports[f]) & set(supports[h]):
            emit([variables[u, v] for u in range(4*f, 4*f+4) for v in range(4*h, 4*h+4)],
                 c[f][h], 'block_total', [f, h])
    for u, v in combinations(range(84), 2):
        target = 2 - len(set(labels[u]) & set(labels[v])) - int((u, v) in known) - len(outer[u] & outer[v])
        terms = [variables[u, v]] if (u, v) in variables else []
        for w in outer[u]:
            edge = tuple(sorted((v, w)))
            if edge in variables:
                terms.append(variables[edge])
        for w in outer[v]:
            edge = tuple(sorted((u, w)))
            if edge in variables:
                terms.append(variables[edge])
        emit(terms, target, 'linear_pair_cap', [u, v], False)

    def dimacs(items):
        return (f'p cnf {pool.top} {len(items)}\n' +
                ''.join(' '.join(map(str, clause)) + ' 0\n' for clause in items)).encode('ascii')

    sealed = HERE / 'scratch_resume_overlap_review.cnf'
    assert dimacs(clauses) == sealed.read_bytes()
    old_core = read_cnf(HERE / 'scratch_resume_overlap_review_core.cnf')[1]
    clause_locations = defaultdict(list)
    for i, clause in enumerate(clauses):
        clause_locations[tuple(sorted(clause))].append(i)

    def map_core(core_clauses, permitted_kinds=None):
        counts = Counter()
        uses = []
        for clause in core_clauses:
            positions = clause_locations[tuple(sorted(clause))]
            if permitted_kinds:
                positions = [i for i in positions if groups[origins[i]]['kind'] in permitted_kinds]
            assert positions
            # Where the exact same clause has several valid explanations,
            # use a deterministic first occurrence; record this convention.
            index = positions[0]
            counts[origins[index]] += 1
            uses.append(index)
        return [{'group_id': gid, 'core_clauses': count, **groups[gid]} for gid, count in sorted(counts.items())]

    old_groups = map_core(old_core)
    retained_indices = [i for i, gid in enumerate(origins) if groups[gid]['kind'] != 'block_total']
    retained = [clauses[i] for i in retained_indices]
    cnf = HERE / 'scratch_next_overlap_drop_totals.cnf'
    cnf.write_bytes(dimacs(retained))
    metadata = {'groups': groups, 'edge_variables': [[var, *pair] for pair, var in variables.items()],
                'original_core_groups': old_groups,
                'original_core_mapping_convention': 'first exact canonical clause occurrence; duplicate clauses may have alternative valid origins',
                'retained_original_clause_indices': retained_indices,
                'sealed_original_cnf_sha256': sha256(sealed.read_bytes()).hexdigest()}
    meta_path = HERE / 'scratch_next_overlap_semantic_map.json'
    meta_path.write_text(json.dumps(metadata, indent=2)+'\n', encoding='utf-8')
    result = {'status': 'BOUNDED_DROP_DISJOINT_TOTALS_RUN',
              'lift_sha256': sha256(lift_path.read_bytes()).hexdigest(),
              'old_cnf_reproduced_byte_identically': True,
              'removed_block_total_constraints': 105, 'removed_clauses': len(clauses)-len(retained),
              'retained_clauses': len(retained), 'variables': pool.top,
              'old_core_constraint_histogram': dict(Counter(g['kind'] for g in old_groups)),
              'old_core_clause_histogram': dict(sum((Counter({g['kind']: g['core_clauses']}) for g in old_groups), Counter())),
              'cnf_sha256': sha256(cnf.read_bytes()).hexdigest(),
              'scope': 'This fixed168-edge overlap assignment, all same-fiber/other overlap edges absent; no disjoint C block totals. No global E0 exclusion.'}
    with Solver(name='cadical195', bootstrap_with=retained, with_proof=True) as solver:
        solver.conf_budget(100000)
        sat = solver.solve_limited()
        result['answer'] = 'UNKNOWN' if sat is None else 'SAT' if sat else 'UNSAT'
        result['solver_stats'] = solver.accum_stats()
        if sat is False:
            proof = HERE / 'scratch_next_overlap_drop_totals.drat'
            proof.write_bytes(('\n'.join(solver.get_proof())+'\n').encode('ascii'))
            core = HERE / 'scratch_next_overlap_drop_totals_core.cnf'
            coreproof = HERE / 'scratch_next_overlap_drop_totals_core.drat'
            checked = subprocess.run([str(HERE/'tools/drat-trim/drat-trim.exe'), str(cnf), str(proof),
                                      '-c', str(core), '-l', str(coreproof), '-t', '20', '-w'],
                                     capture_output=True, text=True, timeout=25, check=False)
            transcript = checked.stdout + checked.stderr
            (HERE/'scratch_next_overlap_drop_totals_drat.log').write_text(transcript, encoding='utf-8')
            result['drat_checked'] = checked.returncode == 0 and 's VERIFIED' in transcript
            if result['drat_checked']:
                new_core = read_cnf(core)[1]
                new_groups = map_core(new_core, {'label_quota', 'linear_pair_cap'})
                result['new_core_clauses'] = len(new_core)
                result['new_core_constraint_histogram'] = dict(Counter(g['kind'] for g in new_groups))
                metadata['new_core_groups'] = new_groups
                meta_path.write_text(json.dumps(metadata, indent=2)+'\n', encoding='utf-8')
        elif sat:
            positive = {v for v in solver.get_model() if v > 0}
            assert all(any(lit in positive if lit > 0 else -lit not in positive for lit in clause)
                       for clause in retained)
            result['satisfying_edge_variables'] = [list(pair) for pair, var in variables.items() if var in positive]
    result['elapsed_seconds'] = time.monotonic()-started
    (HERE/'scratch_next_overlap_drop_totals.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k != 'satisfying_edge_variables'}))


if __name__ == '__main__':
    main()
