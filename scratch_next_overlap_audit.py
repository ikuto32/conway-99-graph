"""Solver-free proof that the sealed RUP core does not use block totals."""
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path

from scratch_resume_overlap_review_rup import read_cnf, is_rup

HERE = Path(__file__).resolve().parent


def main():
    old = HERE/'scratch_resume_overlap_review.cnf'
    new = HERE/'scratch_next_overlap_drop_totals.cnf'
    core = HERE/'scratch_resume_overlap_review_core.cnf'
    proof = HERE/'scratch_resume_overlap_review_core_additions.drat'
    meta = json.loads((HERE/'scratch_next_overlap_semantic_map.json').read_bytes())
    variables, old_clauses = read_cnf(old)
    assert sha256(old.read_bytes()).hexdigest() == meta['sealed_original_cnf_sha256']
    new_variables, new_clauses = read_cnf(new)
    assert new_variables == variables
    expected = []
    positions = []
    for group in meta['groups']:
        if group['kind'] != 'block_total':
            start, stop = group['clause_start'], group['clause_stop']
            expected += old_clauses[start:stop]
            positions += list(range(start, stop))
    assert positions == meta['retained_original_clause_indices']
    assert new_clauses == expected
    assert read_cnf(core)[0] == variables
    core_clauses = read_cnf(core)[1]
    assert not (Counter(tuple(sorted(c)) for c in core_clauses) -
                Counter(tuple(sorted(c)) for c in new_clauses))
    core_groups = meta['original_core_groups']
    assert all(g['kind'] in ('label_quota', 'linear_pair_cap') for g in core_groups)
    assert sum(g['core_clauses'] for g in core_groups) == len(core_clauses)

    # Independently check every used semantic constraint against only the
    # overlap assignment. Disjoint compression entries are never read.
    known = set(map(tuple, json.loads((HERE/'scratch_resume_overlap_lift.json').read_bytes())['overlap_edges_outer_zero_based']))
    labels = sorted((a, b) for a in range(14) for b in range(a+1, 14) if a//2 != b//2)
    labels.sort(key=lambda z: (z[0]//2, z[1]//2, *z))
    support = [{a//2, b//2} for a, b in labels]
    edge_variables = {tuple(pair): index+1 for index, pair in enumerate(
        (pair for pair in combinations(range(84), 2) if not support[pair[0]] & support[pair[1]]))}
    assert meta['edge_variables'] == [[value, *pair] for pair, value in edge_variables.items()]
    neighbors = [{v if u == x else u for u, v in known if x in (u, v)} for x in range(84)]
    for group in core_groups:
        if group['kind'] == 'label_quota':
            u, symbol = group['coordinate']
            target = (1 if symbol//2 in support[u] else 2) - sum(symbol in labels[v] for v in neighbors[u])
            terms = [var for (a, b), var in edge_variables.items()
                     if a == u and symbol in labels[b] or b == u and symbol in labels[a]]
            assert group['equality']
        else:
            u, v = group['coordinate']
            target = 2-len(set(labels[u]) & set(labels[v]))-int((u, v) in known)-len(neighbors[u] & neighbors[v])
            terms = []
            for (a, b), var in edge_variables.items():
                coefficient = int((a, b) == (u, v))
                coefficient += int(a == v and b in neighbors[u] or b == v and a in neighbors[u])
                coefficient += int(a == u and b in neighbors[v] or b == u and a in neighbors[v])
                terms.extend([var]*coefficient)
            assert not group['equality']
        assert target == group['target'] and sorted(terms) == sorted(group['terms'])
    accepted = list(core_clauses)
    additions = []
    for line in proof.read_text(encoding='ascii').splitlines():
        values = list(map(int, line.split()))
        assert values[-1] == 0 and all(0 < abs(x) <= variables for x in values[:-1])
        clause = tuple(values[:-1])
        assert is_rup(accepted, clause)[0]
        accepted.append(clause)
        additions.append(clause)
    assert additions[-1] == ()
    result = {'status': 'INDEPENDENT_NO_DISJOINT_TOTALS_FIXED_OVERLAP_RUP_PASS',
              'removed_block_total_equations': 105,
              'weaker_cnf_clauses': len(new_clauses), 'reused_core_clauses': len(core_clauses),
              'RUP_additions_checked': len(additions),
              'used_semantic_groups': dict(Counter(g['kind'] for g in core_groups)),
              'semantic_group_coefficients_independently_reconstructed': True,
              'disjoint_compression_entries_read_by_this_auditor': False,
              'sha256': {p.name:sha256(p.read_bytes()).hexdigest() for p in (old,new,core,proof,Path(__file__))},
              'scope': 'This prescribed168-edge overlap assignment cannot extend with same-fiber and other overlap edges absent, regardless of disjoint compression totals. No all-overlap or global E0 exclusion.'}
    (HERE/'scratch_next_overlap_audit.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
