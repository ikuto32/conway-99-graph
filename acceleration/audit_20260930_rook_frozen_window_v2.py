"""Independent literal 59-vertex checking of one frozen rook-window exclusion."""
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import platform
import subprocess
import sys

RAW = Path('acceleration/results/20260930_rook_joint/joint_witness.json')
FILTER = Path('acceleration/results/20260930_rook_complete_window/single_edge_filter.json')
OUT = Path('acceleration/results/20260930_independent_review/rook_frozen_window_v2.json')


def digest(p):
    return sha256(Path(p).read_bytes()).hexdigest()


def add(g, u, v):
    g[u].add(v)
    g[v].add(u)


def violations(g):
    return [(u,v,len(g[u]&g[v]),2-int(v in g[u])) for u,v in combinations(range(len(g)),2)
            if len(g[u]&g[v]) > 2-int(v in g[u])]


def check_pair_record(g, record):
    u,v=record['full59_violating_pair']
    common=len(g[u]&g[v])
    cap=2-int(v in g[u])
    if (record['common'],record['cap']) != (common,cap) or common <= cap:
        raise ValueError('incorrect violating pair certificate')


def main():
    raw = json.loads(RAW.read_bytes())
    claimed = json.loads(FILTER.read_bytes())
    rows = [int(s,16) for s in raw['external_adjacency_rows_hex']]
    assert len(rows) == 50 and all(0 <= r < 1<<50 for r in rows)
    g = [set() for _ in range(59)]
    for u,v in combinations(range(9),2):
        if u//3 == v//3 or u%3 == v%3:
            add(g,u,v)
    assert not violations(g[:9])
    corrupted = [s.copy() for s in g[:9]]
    add(corrupted,0,4)
    assert violations(corrupted), 'corrupted rook control accepted'
    root_cells = [0,4,5,7,8]
    for u in range(50):
        assert not rows[u]>>u&1
        add(g,9+u,root_cells[u//10])
        for v in range(u+1,50):
            assert bool(rows[u]>>v&1) == bool(rows[v]>>u&1)
            if rows[u]>>v&1:
                add(g,9+u,9+v)
    assert not violations(g), 'weaker raw partial graph already violates cap'
    assert all(sum(9+v in g[9+u] for v in range((u//10)*10,(u//10+1)*10))==1 for u in range(50))
    rejected = {tuple(r['edge']):r for r in claimed['rejected_edges']}
    assert len(rejected) == len(claimed['rejected_edges'])
    possible, exact_rejections, records = {}, set(), []
    for ca, cb in ((1,4),(2,3)):
        assert root_cells[ca]//3 != root_cells[cb]//3 and root_cells[ca]%3 != root_cells[cb]%3
        for u in range(ca*10,ca*10+10):
            possible[u] = []
            for v in range(cb*10,cb*10+10):
                assert 9+v not in g[9+u]
                trial = [s.copy() for s in g]
                add(trial,9+u,9+v)
                bad = violations(trial)
                if not bad:
                    possible[u].append(v)
                    continue
                exact_rejections.add((u,v))
                r = rejected[(u,v)]
                a,b = r['violating_pair']
                common = len(trial[9+a]&trial[9+b])
                cap = 2-int(9+b in trial[9+a])
                assert common == r['common_after'] and cap == r['cap_after'] and common > cap
                records.append({'edge':[u,v], 'full59_violating_pair':[9+a,9+b], 'common':common, 'cap':cap})
    assert exact_rejections == set(rejected)
    assert {str(u):vs for u,vs in possible.items()} == claimed['possible_columns_by_row']
    obstruction = [{'vertex':u,'possible_neighbors':vs,'required_degree_in_block':2} for u,vs in possible.items() if len(vs)<2]
    assert obstruction == claimed['row_obstructions'] and obstruction
    # Positive and corrupt certificates use the same literal graph-checking path.
    r = records[0]
    trial=[neighbors.copy() for neighbors in g]
    add(trial,9+r['edge'][0],9+r['edge'][1])
    check_pair_record(trial,r)
    for corrupt in ({**r,'common':r['common']+1},{**r,'cap':r['cap']+1},{**r,'full59_violating_pair':[0,1]}):
        try:
            check_pair_record(trial,corrupt)
        except ValueError:
            pass
        else:
            raise ValueError('corrupted violating-pair record accepted')
    fake_edge=tuple(r['edge'])
    fake_trial=[neighbors.copy() for neighbors in g]
    add(fake_trial,9+fake_edge[0],9+fake_edge[1])
    assert violations(fake_trial), 'fabricated permitted edge accepted'
    paths = [RAW,FILTER,Path(__file__),Path('uv.lock'),Path('acceleration/results/20260917_independent_review/rook_regular_set_recheck.json')]
    report = dict(status='INDEPENDENT_FROZEN_ROOK_WINDOW_EXCLUSION_PASS', claim_id='C-ROOK-FROZEN-WINDOW-ROW-EXCLUSION',claim_revision=1,recommendation='VERIFIED',
        statement='No completion of the exact saved 50-vertex external adjacency window, with its five prescribed rook cells and the induced rook-nine scaffold fixed, can satisfy the rook-cell degree-two requirements and all target common-neighbor caps: all 200 possible edges in the two missing opposite-cell blocks were independently checked, 167 fail a monotone cap, and eight rows have fewer than two permissible neighbors.',
        scope='Only the hash-bound raw partial graph with cell labels [0,4,5,7,8]; not all joint matching assignments, not all rook-containing graphs, and not the unrestricted target.',
        dependencies=[{'id':'C-ROOK-NINE-REGULAR-SET-ENCODING','revision':1,'relation':'uses_result'}],
        timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),
        verifier='/root independent checker of structural_attack discovery',method='Full set-based adjacency reconstruction on59 vertices; enumerate all1711 pairs after each of200 prospective edges, independent of producer incremental checking.',
        inputs_sha256={p.as_posix():digest(p) for p in paths},supersedes_control_check='The v1 exact arithmetic result is preserved; this v2 independently reruns all calculations with nontrivial mutated-record controls.',candidate_edges=200,rejected_edges=len(exact_rejections),retained_edges=sum(map(len,possible.values())),
        raw_weaker_window_caps_pass=True,row_obstructions=obstruction,records=records,
        derivation='Every external vertex in cell i has exactly two neighbors in each rook-nonadjacent cell j by the independently established TH equation. Added edges can only increase common-neighbor counts and can only decrease a pair cap from2to1. Thus a row with fewer than2 individually permissible missing-block neighbors cannot be completed, regardless of edges to other cells.',
        controls=['Known-valid rook9 caps pass','Rook9 with extra diagonal-cell edge fails','All producer violating-pair arithmetic reconstructed from full graph','Three mutated violating-pair records rejected through check_pair_record; fabricated permitted edge rejected by complete cap check'],
        producer_imported=False,shared_components=['Python standard library and input JSON only; no discovery modules'],
        limitations=['No exact matching-domain counts or random attempt counts audited.','Weaker cap-compatible witness remains valid for its own weaker statement.','No general nonexistence, automorphism assumption or target-wide coverage fraction.'],target_resolution=False)
    assert (report['rejected_edges'], report['retained_edges'],len(obstruction)) == (167,33,8)
    with OUT.open('x',encoding='utf-8') as f:
        json.dump(report,f,indent=2)
        f.write('\n')
    print(report['status'],digest(OUT))


if __name__ == '__main__':
    main()
