"""Bounded exact binary arc consistency for the frozen partial-K star tables.

Separate generalized adapter: no old parser, producer, or domain flags reused.
Default is preparation only. Scientific results remain CANDIDATE pending review.
"""
import argparse
from collections import deque
from datetime import datetime, timezone
from hashlib import sha256
import itertools
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

BASE = Path('acceleration/results/20260917_partial_matching')
AUDIT = Path('acceleration/results/20260917_independent_review/partial_matching/summary.json')
AUDIT_HASH = 'ed1d5b464466562cff722e45593095ec89c63bda761cfa7f784994abfc308b17'
PROTOCOL = Path('docs/NEXT_20260917_PARTIAL_PAIR_AC.md')


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_bytes())


def save(path, value):
    with Path(path).open('x', encoding='utf-8') as f:
        json.dump(value, f, indent=2)
        f.write('\n')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def stamp():
    return datetime.now(timezone.utc).isoformat()


def graph(manifest):
    labels = [(2*a+s, 2*b+t) for a, b in itertools.combinations(range(7), 2)
              for s in (0, 1) for t in (0, 1)]
    rows = [0]*99
    def add(u, v):
        rows[u] |= 1 << v
        rows[v] |= 1 << u
    for v in range(1, 15):
        add(0, v)
    for v in range(1, 15, 2):
        add(v, v+1)
    for u, labels_u in enumerate(labels, 15):
        for s in labels_u:
            add(u, s+1)
    for u, v in manifest['remaining_fixed_K_edges_outer']:
        add(u+15, v+15)
    supports = [set(s//2 for s in pair) for pair in labels]
    unknown = {(u, v) for u, v in itertools.combinations(range(84), 2)
               if not supports[u] & supports[v]}
    unknown.update(tuple(e) for e in manifest['freed_legal_matching_edges_outer'])
    require(len(unknown) == 1740, 'unexpected variable pair count')
    require(len(manifest['remaining_fixed_K_edges_outer']) == 162, 'unexpected fixed K')
    allowed = [0]*84
    for u, v in unknown:
        allowed[u] |= 1 << v
        allowed[v] |= 1 << u
    return rows, allowed


def validate_masks(rows, allowed, masks):
    require(len(masks) == 84, 'wrong center count')
    for u, table in enumerate(masks):
        require(table == sorted(set(table)) and table, 'domain order/duplicate/empty')
        for mask in table:
            require(mask >= 0 and mask & ~allowed[u] == 0, 'nonvariable edge in star')
            require(mask.bit_count()+rows[u+15].bit_count() == 14, 'wrong completed degree')
            require(mask & (rows[u+15] >> 15) == 0, 'fixed edge repeated')


def compatible(nu, nv, u, v, mu):
    edge = (nu >> v) & 1
    return edge == ((nv >> u) & 1) and (nu & nv).bit_count() == mu-edge


def propagate(neighborhoods, centers, active, *, mu=2, seconds=180, pair_cap=10000000,
              pending=None):
    """Complete each directed arc atomically; discard incomplete arc deletions.

    Saved queue is sufficient for replay/resume; no partially built relation is
    ever trusted. Original IDs are indices in the immutable full domain tables.
    """
    started = time.monotonic()
    active = [set(row) for row in active]
    n = len(active)
    if pending is None:
        pairs = sorted((len(active[u])*len(active[v]), u, v)
                       for u, v in itertools.combinations(range(n), 2))
        pending = [(u, v) for _, a, b in pairs for u, v in ((a, b), (b, a))]
    queue = deque(map(tuple, pending))
    queued = set(queue)
    checks = 0
    visits = 0
    events = []
    cap = None
    empty = next((u for u in range(n) if not active[u]), None)
    while queue and empty is None:
        u, v = queue.popleft()
        queued.remove((u, v))
        opponents = sorted(active[v])
        removed = []
        for i in sorted(active[u]):
            supported = False
            for j in opponents:
                if checks >= pair_cap:
                    cap = 'PAIR_CHECK_CAP'
                    break
                if checks % 256 == 0 and time.monotonic()-started >= seconds:
                    cap = 'TIME_CAP'
                    break
                checks += 1
                if compatible(neighborhoods[u][i], neighborhoods[v][j], centers[u], centers[v], mu):
                    supported = True
                    break
            if cap:
                break
            if not supported:
                removed.append(i)
        if cap:
            queue.appendleft((u, v))
            queued.add((u, v))
            break  # Discard all incomplete-arc deletions.
        visits += 1
        if removed:
            before = len(active[u])
            active[u].difference_update(removed)
            events.append(dict(target=u, support=v, removed_original_ids=removed,
                               before=before, after=len(active[u]),
                               support_original_ids=opponents))
            if not active[u]:
                empty = u
                break
            for w in range(n):
                if w not in (u, v) and (w, u) not in queued:
                    queue.append((w, u))
                    queued.add((w, u))
    status = 'EMPTY_DOMAIN' if empty is not None else (cap or 'ARC_CONSISTENT')
    return dict(status=status, surviving_original_ids=[sorted(x) for x in active],
                events=events, pending_arcs=list(queue), empty_center=empty,
                compatibility_checks=checks, completed_directed_arcs=visits,
                elapsed_seconds=time.monotonic()-started)


def controls():
    # SRG(9,4,1,2), 3x3 rook graph: singleton full neighborhoods survive exactly.
    rook = [sum(1 << v for v in range(9) if u != v and (u//3 == v//3 or u%3 == v%3))
            for u in range(9)]
    good = propagate([[x] for x in rook], list(range(9)), [[0]]*9)
    require(good['status'] == 'ARC_CONSISTENT' and not good['events'], 'positive fixture')
    bad = rook.copy()
    bad[0] ^= 1 << 1
    rejected = propagate([[x] for x in bad], list(range(9)), [[0]]*9)
    require(rejected['status'] == 'EMPTY_DOMAIN', 'corrupt fixture')
    bounded = propagate([[x] for x in rook], list(range(9)), [[0]]*9, pair_cap=1)
    require(bounded['status'] == 'PAIR_CHECK_CAP', 'cap mislabeled')
    resumed = propagate([[x] for x in rook], list(range(9)), bounded['surviving_original_ids'],
                        pending=bounded['pending_arcs'])
    require(resumed['status'] == 'ARC_CONSISTENT', 'resume fixture')
    require(not compatible(0, 0, 0, 1, 2), 'missing common neighbors accepted')
    require(not compatible(2, 0, 0, 1, 2), 'asymmetric edge accepted')
    return dict(status='PRODUCER_CONTROLS_PASS', positive_rook9=True,
                corrupted_edge_rejected=True, cap_distinguished=True,
                resume_positive=True, bad_common_count_rejected=True, asymmetry_rejected=True)


def prepare(args):
    require(digest(AUDIT) == AUDIT_HASH, 'base independent audit changed')
    audit = read(AUDIT)
    require(audit['status'] == 'INDEPENDENT_PARTIAL_K_DOMAINS_AND_LINEAR_CAPS_PASS', 'base audit gate')
    paths = [AUDIT, BASE/'manifest.json', Path(__file__), PROTOCOL, Path('uv.lock')]
    paths += [BASE/f'domain_{u:02d}.json' for u in range(84)]
    for p in paths:
        if p.parent == BASE:
            require(digest(p) in audit['inputs_sha256'].values(), f'unbound domain input {p}')
    masks = [[int(x, 16) for x in read(BASE/f'domain_{u:02d}.json')['domain_masks_hex']]
             for u in range(84)]
    rows, allowed = graph(read(BASE/'manifest.json'))
    validate_masks(rows, allowed, masks)
    active = [list(range(len(row))) for row in masks]
    if args.filter_dir:
        require(args.filter_audit and args.filter_audit_sha256, 'filtered scope requires exact audit')
        require(digest(args.filter_audit) == args.filter_audit_sha256, 'filter audit changed')
        fa = read(args.filter_audit)
        require(fa['status'] == 'INDEPENDENT_PARTIAL_K_NEIGHBORHOOD_MATCHING_FILTER_PASS', 'filter gate status')
        paths.append(args.filter_audit)
        for u in range(84):
            p = args.filter_dir/f'vertex_{u:02d}.json'
            require(digest(p) in fa['inputs_sha256'].values(), f'unbound filtered IDs {u}')
            data = read(p)
            require(data['outer_vertex'] == u and data['original_count'] == len(masks[u]), 'filter mapping')
            rejected = data['rejected_ids']
            require(rejected == sorted(set(rejected)) and all(0 <= x < len(masks[u]) for x in rejected), 'invalid filtered IDs')
            active[u] = sorted(set(active[u])-set(rejected))
            paths.append(p)
    return masks, rows, active, {str(p): digest(p) for p in paths}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--filter-dir', type=Path)
    ap.add_argument('--filter-audit', type=Path)
    ap.add_argument('--filter-audit-sha256')
    ap.add_argument('--run', action='store_true')
    ap.add_argument('--input-review', type=Path)
    ap.add_argument('--input-review-sha256')
    ap.add_argument('--resume', type=Path)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    masks, rows, active, hashes = prepare(args)
    prepared = dict(timestamp=stamp(), source_commit=subprocess.check_output(['git','rev-parse','HEAD'], text=True).strip(),
                    command=[sys.executable, *sys.argv], cwd=str(Path.cwd()), python=platform.python_version(),
                    status='PREPARED_PARTIAL_K_BINARY_ARC_CONSISTENCY', inputs_sha256=hashes,
                    objective=None, objective_reason='Exact constraint propagation; no LP objective',
                    base_choices=sum(map(len, masks)), input_choices=sum(map(len, active)),
                    input_original_ids=active, filtered=bool(args.filter_dir),
                    seconds=180, pair_check_cap=10000000, centers=84, unordered_pairs=3486,
                    rule='reciprocity and exact completed-neighborhood intersection = 2 minus edge',
                    target_resolution=False, independent_review_required=True)
    save(args.out/'preflight.json', prepared)
    save(args.out/'controls.json', controls())
    if not args.run:
        print(json.dumps({k:v for k,v in prepared.items() if k not in ('inputs_sha256','input_original_ids')}))
        return
    require(args.input_review and args.input_review_sha256, 'run requires independent input gate')
    require(digest(args.input_review) == args.input_review_sha256, 'input review changed')
    gate = read(args.input_review)
    require(gate['status'] == 'INDEPENDENT_PARTIAL_K_PAIR_AC_INPUT_PASS', 'input gate status')
    require(all(h in gate['inputs_sha256'].values() for h in hashes.values()), 'unreviewed input or source')
    pending = None
    resume_sha = None
    if args.resume:
        prior = read(args.resume)
        require(prior['inputs_sha256'] == hashes, 'resume inputs changed')
        require(prior['status'] in ('TIME_CAP','PAIR_CHECK_CAP'), 'resume requires capped checkpoint')
        retained = prior['surviving_original_ids']
        require(len(retained) == 84 and all(row == sorted(set(row)) and set(row) <= set(active[u])
                for u, row in enumerate(retained)), 'invalid resume original IDs')
        active = retained
        pending = prior['pending_arcs']
        require(pending and len(set(map(tuple,pending))) == len(pending)
                and all(len(pair) == 2 and 0 <= pair[0] < 84 and 0 <= pair[1] < 84
                        and pair[0] != pair[1] for pair in pending), 'invalid resume queue')
        resume_sha = digest(args.resume)
    neighborhoods = [[rows[u+15] | (mask << 15) for mask in table] for u, table in enumerate(masks)]
    result = propagate(neighborhoods, list(range(15, 99)), active, pending=pending)
    result.update(inputs_sha256=hashes, input_review_sha256=digest(args.input_review),
                  resume_path=str(args.resume) if args.resume else None, resume_sha256=resume_sha,
                  timestamp=stamp(), result_review_state='CANDIDATE', target_resolution=False)
    save(args.out/'result.json', result)
    print(json.dumps({k:v for k,v in result.items() if k not in ('events','surviving_original_ids','pending_arcs','inputs_sha256')}))


if __name__ == '__main__':
    main()
