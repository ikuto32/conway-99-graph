"""Complete finite coordinate universe and exact partial-graph cap filter.

Producer evidence only: independent list/count and full-matrix checking required.
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

BASE = Path('acceleration/results/20260917_partial_matching/manifest.json')
AUDIT = Path('acceleration/results/20260917_independent_review/partial_matching/summary.json')
AUDIT_HASH = 'ed1d5b464466562cff722e45593095ec89c63bda761cfa7f784994abfc308b17'
PROTOCOL = Path('docs/NEXT_20260917_PARTIAL_COORDINATE_MATCHINGS.md')


def digest(p):
    return sha256(Path(p).read_bytes()).hexdigest()


def save(path, data):
    with Path(path).open('x', encoding='utf-8') as f:
        json.dump(data, f, separators=(',', ':'))
        f.write('\n')


def add(rows, a, b):
    rows[a] |= 1 << b
    rows[b] |= 1 << a


def first_bad(rows):
    for u in range(len(rows)):
        if (rows[u] >> u) & 1:
            return dict(kind='DIAGONAL', pair=[u,u])
        if rows[u].bit_count() > 14:
            return dict(kind='DEGREE_CAP', pair=[u,u], actual=rows[u].bit_count(), cap=14)
    for u, v in combinations(range(len(rows)), 2):
        edge = (rows[u] >> v) & 1
        if edge != ((rows[v] >> u) & 1):
            return dict(kind='ASYMMETRY', pair=[u,v])
        common = (rows[u] & rows[v]).bit_count()
        cap = 2-edge
        if common > cap:
            return dict(kind='COMMON_NEIGHBOR_CAP', pair=[u,v], actual=common, cap=cap)
    return None


def controls():
    rook = [sum(1 << v for v in range(9) if u != v and (u//3 == v//3 or u%3 == v%3)) for u in range(9)]
    assert first_bad(rook) is None
    diagonal = rook.copy(); diagonal[0] |= 1
    assert first_bad(diagonal)['kind'] == 'DIAGONAL'
    asymmetric = rook.copy(); asymmetric[0] ^= 1 << 1
    assert first_bad(asymmetric) is not None
    corrupt = rook.copy(); add(corrupt, 0, 4)
    assert first_bad(corrupt)['kind'] == 'COMMON_NEIGHBOR_CAP'
    return dict(status='PRODUCER_CONTROLS_PASS', positive_rook9=True,
                diagonal_rejected=True, asymmetric_rejected=True, added_edge_cap_rejected=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    assert digest(AUDIT) == AUDIT_HASH
    audit = json.loads(AUDIT.read_bytes())
    assert audit['status'] == 'INDEPENDENT_PARTIAL_K_DOMAINS_AND_LINEAR_CAPS_PASS'
    assert digest(BASE) in audit['inputs_sha256'].values()
    manifest = json.loads(BASE.read_bytes())
    paths = [BASE, AUDIT, PROTOCOL, Path(__file__), Path('uv.lock')]
    hashes = {str(p): digest(p) for p in paths}
    labels = [(2*a+s, 2*b+t) for a,b in combinations(range(7),2) for s in (0,1) for t in (0,1)]
    vertices = [u for u,pair in enumerate(labels) if 0 in pair]
    allowed = sorted(tuple(e) for e in manifest['freed_legal_matching_edges_outer'])
    independently_derived = [(u,v) for u,v in combinations(vertices,2)
                            if len({s//2 for s in labels[u]} & {s//2 for s in labels[v]}) == 1]
    assert allowed == independently_derived and len(vertices) == 12 and len(allowed) == 60
    fixed = [0]*99
    for v in range(1,15): add(fixed,0,v)
    for v in range(1,15,2): add(fixed,v,v+1)
    for u,pair in enumerate(labels,15):
        for s in pair: add(fixed,u,s+1)
    for u,v in manifest['remaining_fixed_K_edges_outer']: add(fixed,u+15,v+15)
    assert first_bad(fixed) is None
    save(args.out/'manifest.json', dict(timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        command=[sys.executable,*sys.argv],cwd=str(Path.cwd()),python=platform.python_version(),
        inputs_sha256=hashes,question='How many legal coordinate matchings exist and satisfy the frozen partial99-graph caps?',
        scope='Only root_group0 same_0 matching on twelve prescribed vertices with162other fixedKedges and prescribedotherabsences.',
        root_group=0,matching_class='same_0',coordinate_vertices_outer=vertices,allowed_matching_edges_outer=allowed,
        selection='All perfectmatchings; minimum unmatched outervertex, ascending allowedpartner; no symmetry reduction.',
        criterion='Each matching accepted iff full99partialgraph is symmetric loopless degree<=14 and everypair common<=2-edge.',
        expected_count=6040,expected_count_status='Prior expectation, not an assertion or stopping condition',
        seconds_cap=30,seed=None,seed_reason='Deterministic recursion',target_resolution=False,
        coverage='Finite conditional matching universe only; no denominator for unrestricted target'))
    save(args.out/'controls.json', controls())
    start = time.monotonic()
    allowed_set = set(allowed)
    records = []
    complete = True
    def visit(unmatched, chosen):
        nonlocal complete
        if time.monotonic()-start >= 30:
            complete = False
            return
        if not unmatched:
            records.append(dict(matching_id=len(records),edges_outer=chosen))
            return
        u = unmatched[0]
        for v in unmatched[1:]:
            if (u,v) in allowed_set:
                visit([x for x in unmatched if x not in (u,v)],chosen+[[u,v]])
                if not complete: return
    visit(vertices, [])
    save(args.out/'matchings.json',dict(complete=complete,vertices_outer=vertices,records=records))
    outcomes=[]
    for record in records:
        if time.monotonic()-start >= 30:
            break
        rows=fixed.copy()
        for u,v in record['edges_outer']: add(rows,u+15,v+15)
        witness=first_bad(rows)
        outcomes.append(dict(matching_id=record['matching_id'],accepted=witness is None,first_violation=witness,
                             first_violation_null_reason='All full99 partial caps passed' if witness is None else None))
    save(args.out/'outcomes.json',dict(records=outcomes))
    accepted=[r['matching_id'] for r in outcomes if r['accepted']]
    rejected=[r['matching_id'] for r in outcomes if not r['accepted']]
    summary=dict(timestamp=datetime.now(timezone.utc).isoformat(),
        status='CANDIDATE_COMPLETE_COORDINATE_MATCHING_CAP_FILTER' if complete and len(outcomes)==len(records) else 'CANDIDATE_TIME_CAPPED_COORDINATE_MATCHING_CAP_FILTER',
        universe_enumeration_complete=complete,generated_matchings=len(records),evaluated_matchings=len(outcomes),
        accepted_matching_ids=accepted,rejected_matching_ids=rejected,accepted_count=len(accepted),rejected_count=len(rejected),
        pending_evaluation_ids=[r['matching_id'] for r in records[len(outcomes):]],
        inputs_sha256=hashes,artifacts_sha256={str(args.out/p):digest(args.out/p) for p in ('manifest.json','controls.json','matchings.json','outcomes.json')},
        elapsed_seconds=time.monotonic()-start,independent_review='PENDING',target_resolution=False,
        limitations='Accepted partial graphs need not extend. Rejections cover this coordinate and frozenotherconfiguration only.')
    save(args.out/'summary.json',summary)
    print(json.dumps({k:v for k,v in summary.items() if k not in ('accepted_matching_ids','rejected_matching_ids','inputs_sha256','artifacts_sha256','pending_evaluation_ids')}))


if __name__=='__main__': main()
