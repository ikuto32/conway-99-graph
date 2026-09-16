"""Exact one-step two-edge trades of five saved complete overlap assignments.

This is a small neighbourhood of five fixed points, not E0 coverage.
All changes preserve degrees, overlapping block totals, quotas and caps.
"""
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import time

from scratch_next_overlap_cut_bank import LABELS, SUPPORTS, load_cuts, evaluate
from scratch_next_overlap_cut_orbit import transform


def canonical(u, v):
    return (u, v) if u < v else (v, u)


def block_counts(edges):
    return Counter(canonical(u//4, v//4) for u, v in edges)


def legal_trades(known):
    rows = [set() for _ in range(84)]
    for u, v in known:
        rows[u].add(v)
        rows[v].add(u)
    counters = Counter()
    valid = []
    for first, second in combinations(sorted(known), 2):
        a, b = first
        c, d = second
        if len({a, b, c, d}) != 4:
            continue
        counters['disjoint_edge_pairs'] += 1
        removed = frozenset((first, second))
        old_blocks = block_counts(removed)
        for added in (frozenset((canonical(a, c), canonical(b, d))),
                      frozenset((canonical(a, d), canonical(b, c)))):
            if added & known or any(len(SUPPORTS[u] & SUPPORTS[v]) != 1 for u, v in added):
                continue
            counters['overlap_and_absence_pass'] += 1
            if block_counts(added) != old_blocks:
                continue
            counters['block_total_pass'] += 1
            changed = {a, b, c, d}
            trial_rows = list(rows)
            for u in changed:
                trial_rows[u] = set(rows[u])
            for u, v in removed:
                trial_rows[u].remove(v)
                trial_rows[v].remove(u)
            for u, v in added:
                trial_rows[u].add(v)
                trial_rows[v].add(u)
            assert all(len(trial_rows[u]) == 4 for u in changed)
            if any((sum(s in LABELS[v] for v in trial_rows[u]) != 1
                    if s//2 in SUPPORTS[u] else sum(s in LABELS[v] for v in trial_rows[u]) > 2)
                   for u in changed for s in range(14)):
                continue
            counters['label_quota_pass'] += 1
            if any(len(trial_rows[u] & trial_rows[v])+len(set(LABELS[u]) & set(LABELS[v]))
                   > (1 if v in trial_rows[u] else 2)
                   for u in changed for v in range(84) if u != v):
                continue
            counters['all_partial_caps_pass'] += 1
            valid.append((removed, added))
    assert len(valid) == len({(removed, added) for removed, added in valid})
    return dict(counters), valid


def main():
    started = time.monotonic()
    paths = [Path('scratch_resume_overlap_lift.json')]
    paths += [Path(f'scratch_next_overlap_alternatives_r{i}.json') for i in range(4)]
    saved = [frozenset(map(tuple, json.loads(path.read_bytes())['overlap_edges_outer_zero_based'])) for path in paths]
    forbidden = {transform(known, mask) for known in saved for mask in range(128)}
    assert len(forbidden) == 640
    cuts = load_cuts()
    records, selected = [], None
    for index, (path, known) in enumerate(zip(paths, saved)):
        counters, trades = legal_trades(known)
        outcomes = []
        for removed, added in trades:
            candidate = known-removed | added
            assert len(candidate) == 168
            scores = [evaluate(candidate, cut)['score'] for cut in cuts]
            image = transform(candidate, 1)
            image_scores = [evaluate(image, cut)['score'] for cut in cuts]
            if selected is None and image not in forbidden and min(image_scores) >= 0:
                selected = {
                    'status': 'NEW_OVERLAP_TRADE_PASSES_FIVE_FIXED_CUTS',
                    'source_path': path.name, 'source_sha256': sha256(path.read_bytes()).hexdigest(),
                    'removed_edges_before_sign_flip': [list(pair) for pair in sorted(removed)],
                    'added_edges_before_sign_flip': [list(pair) for pair in sorted(added)],
                    'sign_flip_mask': 1, 'cut_scores': image_scores,
                    'overlap_edges_outer_zero_based': [list(pair) for pair in sorted(image)],
                    'scope': 'Complete overlap assignment only. Five fixed-index cuts pass; their full sign families and disjoint completion have not been certified feasible.',
                }
            outcomes.append({'removed': [list(pair) for pair in sorted(removed)],
                             'added': [list(pair) for pair in sorted(added)],
                             'fixed_cut_scores': scores, 'one_sign_flip_scores': image_scores,
                             'belongs_to_saved_sign_orbits': candidate in forbidden})
        records.append({'source': path.name, 'counters': counters, 'legal_trades': len(trades),
                        'all_rejected_by_own_fixed_cut': bool(trades) and all(row['fixed_cut_scores'][index] < 0 for row in outcomes),
                        'own_cut_score_range': [min(row['fixed_cut_scores'][index] for row in outcomes), max(row['fixed_cut_scores'][index] for row in outcomes)] if outcomes else None,
                        'outcomes': outcomes})
        print(json.dumps({key: value for key, value in records[-1].items() if key != 'outcomes'}), flush=True)
    if selected is not None:
        Path('scratch_follow_overlap_trades_candidate.json').write_text(json.dumps(selected, indent=2)+'\n', encoding='utf-8')
    result = {
        'status': 'FIVE_FIXED_OVERLAP_TWO_EDGE_TRADE_ENUMERATION_COMPLETE',
        'input_sha256': {path.name: sha256(path.read_bytes()).hexdigest() for path in paths},
        'records': records, 'selected_fixed_cut_candidate': selected is not None,
        'elapsed_seconds': time.monotonic()-started,
        'scope': 'Exactly one two-edge switch from each of five stored K assignments, preserving overlap totals and partial caps. Neither all assignments at C nor E0 is enumerated. Negative cuts prove only prescribed completions impossible.',
    }
    Path('scratch_follow_overlap_trades.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in result.items() if key not in ('records', 'input_sha256')}))


if __name__ == '__main__':
    main()
