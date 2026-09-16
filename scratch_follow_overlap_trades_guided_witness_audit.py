"""Check a constructed witness for the earlier UNKNOWN necessary model.

This witness cannot be completed to an SRG: a sign-conjugate cut rejects it.
No numerical solver or candidate producer is imported.
"""
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path


def main():
    path = Path('scratch_follow_overlap_trades_candidate.json')
    data = json.loads(path.read_bytes())
    labels = [(a, b) for a, b in combinations(range(14), 2) if a//2 != b//2]
    labels.sort(key=lambda pair: (pair[0]//2, pair[1]//2, pair))
    supports = [set(s//2 for s in pair) for pair in labels]
    vertex_of = {pair: u for u, pair in enumerate(labels)}
    overlap = [pair for pair in combinations(range(84), 2) if len(supports[pair[0]] & supports[pair[1]]) == 1]
    disjoint = [pair for pair in combinations(range(84), 2) if not supports[pair[0]] & supports[pair[1]]]
    listed = data['overlap_edges_outer_zero_based']
    known = frozenset(map(tuple, listed))
    assert len(known) == len(listed) == 168 and known <= set(overlap)
    def sign_image(edges, mask):
        permutation = [vertex_of[tuple(s ^ ((mask >> (s//2)) & 1) for s in pair)] for pair in labels]
        assert sorted(permutation) == list(range(84))
        return frozenset(tuple(sorted((permutation[u], permutation[v]))) for u, v in edges)
    source = Path(data['source_path'])
    assert sha256(source.read_bytes()).hexdigest() == data['source_sha256']
    original = frozenset(map(tuple, json.loads(source.read_bytes())['overlap_edges_outer_zero_based']))
    removed = frozenset(map(tuple, data['removed_edges_before_sign_flip']))
    added = frozenset(map(tuple, data['added_edges_before_sign_flip']))
    assert len(removed) == len(added) == 2 and removed <= original and not added & original
    assert known == sign_image(original-removed | added, data['sign_flip_mask'])
    saved = [Path('scratch_resume_overlap_lift.json')]+[Path(f'scratch_next_overlap_alternatives_r{i}.json') for i in range(4)]
    images = {sign_image(frozenset(map(tuple, json.loads(p.read_bytes())['overlap_edges_outer_zero_based'])), mask)
              for p in saved for mask in range(128)}
    assert len(images) == 640 and known not in images
    adj = [set() for _ in range(99)]
    def put(u, v):
        adj[u].add(v)
        adj[v].add(u)
    for u in range(1, 15):
        put(0, u)
    for u in range(1, 15, 2):
        put(u, u+1)
    for u, pair in enumerate(labels, 15):
        for symbol in pair:
            put(u, symbol+1)
    for u, v in known:
        put(u+15, v+15)
    assert Counter(map(len, adj)) == {14: 15, 6: 84}
    assert all(len(adj[u] & adj[v]) <= (1 if v in adj[u] else 2) for u, v in combinations(range(99), 2))
    cp = Path('scratch_resume_integral_compression.json')
    c = json.loads(cp.read_bytes())['C']
    totals = Counter(tuple(sorted((u//4, v//4))) for u, v in known)
    for f, h in combinations(range(21), 2):
        if supports[4*f] & supports[4*h]:
            assert totals[f, h] == c[f][h]
    for u in range(84):
        for symbol in range(14):
            count = sum(symbol in labels[v-15] for v in adj[u+15] if v >= 15)
            assert count == 1 if symbol//2 in supports[u] else count <= 2
    compiled_path = Path('scratch_next_overlap_cut_compiled.json')
    compiled = json.loads(compiled_path.read_bytes())
    guided_path = Path('scratch_next_overlap_cut_guided.json')
    guided = json.loads(guided_path.read_bytes())
    assert guided['status'] == 'UNKNOWN' and 'overlap_edges_outer_zero_based' not in guided
    assert sha256(compiled_path.read_bytes()).hexdigest() == guided['compiled_sha256']
    assert sha256(cp.read_bytes()).hexdigest() == guided['compression_sha256']
    for name, digest in compiled['input_sha256'].items():
        assert sha256(Path(name).read_bytes()).hexdigest() == digest
    assert compiled['overlap_variables'] == [[i+1, *pair] for i, pair in enumerate(overlap)]
    assert compiled['disjoint_variables'] == [[i+1, *pair] for i, pair in enumerate(disjoint)]
    overlap_values = {i+1: int(pair in known) for i, pair in enumerate(overlap)}
    possible_rows = [set(v if u == x else u for u, v in overlap if x in (u, v)) for x in range(84)]
    products = {(u, v, w): int(tuple(sorted((u, w))) in known and tuple(sorted((v, w))) in known)
                for u, v in combinations(range(84), 2) for w in possible_rows[u] & possible_rows[v]}
    assert len(products) == 65520 and sum(products.values()) == 504
    mapping = json.loads(Path('scratch_next_overlap_semantic_map.json').read_bytes())
    original_certificate = json.loads(Path('scratch_next_overlap_farkas.json').read_bytes())
    groups = [[{'kind': mapping['groups'][int(i)]['kind'], 'coordinate': mapping['groups'][int(i)]['coordinate'], 'multiplier': weight}
               for i, weight in original_certificate['group_multipliers'].items()]]
    groups += [json.loads(Path(f'scratch_next_overlap_alternatives_r{i}_farkas.json').read_bytes())['group_multipliers'] for i in range(4)]
    unknown = { (u+15, v+15) for u, v in disjoint }
    def direct(group_list, adjacency):
        rhs = 0
        coefficients = dict.fromkeys(unknown, 0)
        for group in group_list:
            kind, (a, b), weight = group['kind'], group['coordinate'], group['multiplier']
            u, v = a+15, b+1 if kind == 'label_quota' else b+15
            terms = Counter()
            if kind == 'label_quota':
                target = (1 if v in adjacency[u] else 2)-len(adjacency[u] & adjacency[v])
                for w in adjacency[v]:
                    pair = tuple(sorted((u, w)))
                    if pair in unknown:
                        terms[pair] += 1
            else:
                assert kind == 'linear_pair_cap' and weight >= 0
                target = 2-int(v in adjacency[u])-len(adjacency[u] & adjacency[v])
                if (u, v) in unknown:
                    terms[u, v] += 1
                for fixed, changing in ((u, v), (v, u)):
                    for w in adjacency[fixed]:
                        pair = tuple(sorted((changing, w)))
                        if pair in unknown:
                            terms[pair] += 1
            rhs += weight*target
            for pair, multiplicity in terms.items():
                coefficients[pair] += weight*multiplicity
        return rhs, coefficients
    scores, max_count = [], 0
    for cut, group_list in zip(compiled['cuts'], groups):
        rhs, coefficients = direct(group_list, adj)
        encoded_rhs = cut['R_constant']+sum(weight*overlap_values[i] for i, weight in cut['R_linear'])
        encoded_rhs += sum(weight*products[u, v, w] for u, v, w, weight in cut['R_products'])
        assert rhs == encoded_rhs
        negative_parts = 0
        for row, (u, v) in zip(cut['w_affine'], disjoint):
            w = row['constant']+sum(weight*overlap_values[i] for i, weight in row['terms'])
            assert w == coefficients[u+15, v+15]
            z = max(0, -w)
            assert 0 <= z <= row['z_upper']
            if row['mode'] == 'zero':
                assert z == 0
            else:
                assert row['mode'] == 'exact_max'
                max_count += 1
            negative_parts += z
        score = rhs+negative_parts
        assert score >= 0
        scores.append(score)
    assert max_count == 4881 and scores == data['cut_scores']
    # Restore the pre-swap sign indexing and apply the original valid cut.
    inverse = [set(row) for row in adj]
    for u in range(15, 99):
        inverse[u] = {v for v in inverse[u] if v < 15}
    unflipped = sign_image(known, data['sign_flip_mask'])
    for u, v in unflipped:
        inverse[u+15].add(v+15)
        inverse[v+15].add(u+15)
    rhs, co = direct(groups[0], inverse)
    rejecting_score = rhs-sum(min(0, value) for value in co.values())
    assert rejecting_score < 0
    report = {
        'status': 'INDEPENDENT_CONSTRUCTED_FIVE_CUT_MODEL_WITNESS_AND_CONJUGATE_EXCLUSION_PASS',
        'candidate_sha256': sha256(path.read_bytes()).hexdigest(),
        'compiled_sha256': sha256(compiled_path.read_bytes()).hexdigest(),
        'historical_guided_run_status': 'UNKNOWN',
        'new_witness_satisfies_that_necessary_model': True,
        'partial_graph_edges': 357, 'partial_pair_caps_checked': 4851,
        'prior_sign_images_excluded': 640,
        'one_way_products_assigned': 65520, 'true_products': 504,
        'exact_max_variables_assigned': max_count, 'affine_coefficients_checked': 8400,
        'five_fixed_cut_scores': scores,
        'rejecting_sign_mask': data['sign_flip_mask'], 'conjugate_cut_score': rejecting_score,
        'solver_or_producer_imported': False,
        'scope': 'A witness for the specific necessary-condition model only. Its graph completion is rigorously excluded by a sign-conjugate capacity cut. The historical UNKNOWN file remains unchanged; no full SRG.',
    }
    Path('scratch_follow_overlap_trades_guided_witness_audit.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
