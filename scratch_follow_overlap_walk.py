"""One bounded exact-cut-guided walk through legal overlap edge trades.

At most12 two-edge switches; stop at the first complete640-cut survivor.
This never supplies the unknown disjoint edges or a submission file.
"""
from hashlib import sha256
import json
from pathlib import Path
import time

from scratch_follow_overlap_trades import legal_trades
from scratch_next_overlap_cut_bank import load_cuts, evaluate
from scratch_next_overlap_cut_orbit import transform


def scan(known, cuts):
    minima = []
    tested = 0
    for index, cut in enumerate(cuts):
        values = []
        for mask in range(128):
            value = evaluate(transform(known, mask), cut)['score']
            values.append(value)
            tested += 1
            if value < 0:
                return {'all_640_pass': False, 'tested': tested,
                        'rejecting_cut': index, 'rejecting_mask': mask, 'score': value}
        minima.append(min(values))
    return {'all_640_pass': True, 'tested': tested, 'cut_orbit_minima': minima}


def main():
    out = Path('scratch_follow_overlap_walk.json')
    assert not out.exists(), 'preserve this bounded walk; no implicit extension'
    started = time.monotonic()
    source = Path('scratch_resume_overlap_lift.json')
    known = frozenset(map(tuple, json.loads(source.read_bytes())['overlap_edges_outer_zero_based']))
    cuts = load_cuts()
    visited = {known}
    records = []
    status = scan(known, cuts)
    for step in range(1, 13):
        assert not status['all_640_pass']
        index, mask = status['rejecting_cut'], status['rejecting_mask']
        counters, trades = legal_trades(known)
        choices = []
        for removed, added in trades:
            changed = known-removed | added
            if changed in visited:
                continue
            score = evaluate(transform(changed, mask), cuts[index])['score']
            choices.append((score, tuple(sorted(removed)), tuple(sorted(added)), changed))
        if not choices:
            records.append({'step': step, 'status': 'NO_UNVISITED_LEGAL_TRADE'})
            break
        chosen = max(choices, key=lambda row: row[:3])
        score, removed, added, known = chosen
        visited.add(known)
        before = status
        status = scan(known, cuts)
        record = {'step': step, 'legal_trades': len(trades),
                  'removed': [list(pair) for pair in removed], 'added': [list(pair) for pair in added],
                  'active_cut': index, 'active_sign_mask': mask,
                  'active_score_before': before['score'], 'active_score_after': score,
                  'new_scan': status}
        records.append(record)
        print(json.dumps(record), flush=True)
        if status['all_640_pass']:
            break
    result = {'status': 'SIX_HUNDRED_FORTY_CUT_SURVIVOR' if status['all_640_pass'] else 'BOUNDED_LOCAL_WALK_NO_SURVIVOR',
              'source': source.name, 'source_sha256': sha256(source.read_bytes()).hexdigest(),
              'step_limit': 12, 'steps': records, 'final_cut_scan': status,
              'overlap_edges_outer_zero_based': [list(pair) for pair in sorted(known)],
              'elapsed_seconds': time.monotonic()-started,
              'scope': 'One walk at fixed overlapping C totals and E0=0. Full640 cut passage is only a necessary condition, not a linear completion or SRG witness. No exhaustive class claim.'}
    out.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in result.items() if key not in ('steps', 'overlap_edges_outer_zero_based')}))


if __name__ == '__main__':
    main()
