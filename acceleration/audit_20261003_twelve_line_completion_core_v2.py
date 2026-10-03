"""Root independent finite audit; no imports from the candidate producer."""
import argparse
import hashlib
import itertools
import json
import re
import sys
from pathlib import Path

from command_deadline import CommandDeadline
from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]
NOTE = 'docs/CANDIDATE_20261003_TERNARY_TWELVE_LINE_CAP_CORE_COMPLETION_OBSTRUCTION_V1.md'
NOTE_HASH = '9ba6929ec3ac6273e0ce56f06bab4e0da0f3e706f1a4be22054733209eeed702'


def need(value, message):
    if not value:
        raise ValueError(message)


def graph(n, triples):
    edges = set()
    for triple in triples:
        need(len(triple) == 3 and len(set(triple)) == 3, 'TRIPLE')
        for pair in itertools.combinations(sorted(triple), 2):
            need(pair not in edges, 'REPEATED_PAIR')
            edges.add(pair)
    return edges


def geometry(n, edges, *, require_completed_edges=True):
    neighbors = [set() for _ in range(n)]
    for u, v in edges:
        neighbors[u].add(v)
        neighbors[v].add(u)
    counts = {(u, v): len(neighbors[u] & neighbors[v])
              for u in range(n) for v in range(u + 1, n)}
    violations = [pair for pair, cn in counts.items()
                  if (pair in edges and (cn != 1 if require_completed_edges else cn > 1)) or (pair not in edges and cn > 2)]
    return neighbors, counts, violations


def rejects(call, reason):
    try:
        call()
    except ValueError as error:
        need(str(error) == reason, 'WRONG_CONTROL_VETO')
        return reason
    raise ValueError('CORRUPTION_ACCEPTED')


def word_check(triples, word):
    sums = [0] * 16
    for triple, coefficient in zip(triples, word, strict=True):
        for vertex in triple:
            sums[vertex] += coefficient
    need(all(s % 3 == 0 for s in sums), 'WORD_NOT_KERNEL')
    need(sum(word) % 3 != 0, 'WORD_BALANCED')
    return sums


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--seconds', type=float, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='Independent exact sixteen-point geometry and all CN-zero added-edge subsets; preserve20seconds')
    out = args.out.resolve()
    need(out.is_relative_to(ROOT) and not out.exists(), 'FRESH_OUTPUT')
    out.mkdir(parents=True)
    def tick():
        need(deadline.status()['remaining_seconds'] > 20, 'SAVE_RESERVE')
    result = {'schema': 'ROOT_TWELVE_LINE_FINITE_COMPLETION_AUDIT_V2',
              'producer': '/root/structural', 'verifier': '/root',
              'method': 'independent_artifact_check', 'target_resolution': 'NONE',
              'whole_target_coverage': 'UNKNOWN; no validated denominator.',
              'preserved_failed_v1': 'V1 wrongly rejected extra edges with no internal triangle completion; preserved source/spec/plan/result, no accepted claim.'}
    try:
        tick()
        raw = (ROOT / NOTE).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == NOTE_HASH, 'NOTE_IDENTITY')
        # Only the literal configuration table is parsed, independently of formulas.
        table = raw.decode().split('Let G be their point graph:')[0]
        triples = [tuple(map(int, row)) for row in re.findall(r'\((\d+),(\d+),(\d+)\)', table)]
        need(len(triples) == 12, 'LITERAL_TRIANGLE_COUNT')
        edges = graph(16, triples)
        ns, cn, bad = geometry(16, edges)
        need(not bad and len(edges) == 36, 'LOCAL_GEOMETRY')
        actual = {t for t in itertools.combinations(range(16), 3)
                  if all(p in edges for p in itertools.combinations(t, 2))}
        need(actual == {tuple(sorted(t)) for t in triples}, 'ACTUAL_TRIANGLES')
        need([len(n) for n in ns] == [6]*4 + [4]*12, 'DEGREES')
        word = [-1]*8 + [1]*4
        point_sums = word_check(triples, word)
        controls = []
        for n, ts in [(3, [(0,1,2)]), (5, [(0,1,2),(0,3,4)])]:
            need(not geometry(n, graph(n, ts))[2], 'KNOWN_VALID_CONTROL')
            controls.append({'kind': 'positive', 'vertices': n})
        controls.append({'kind': 'negative', 'diagnostic': rejects(lambda: graph(3, [(0,1,2)]*2), 'REPEATED_PAIR')})
        corrupted = word.copy(); corrupted[0] = 1
        controls.append({'kind': 'negative', 'diagnostic': rejects(lambda: word_check(triples, corrupted), 'WORD_NOT_KERNEL')})
        need(geometry(4, set(itertools.combinations(range(4),2)))[2], 'K4_CORRUPTION_ACCEPTED')
        controls.append({'kind': 'negative', 'diagnostic': 'K4_ADJACENT_CN_TWO'})
        need(geometry(16, edges | {(0,5)})[2], 'ADDED_EDGE_CORRUPTION_ACCEPTED')
        controls.append({'kind': 'negative', 'diagnostic': 'ADDED_EDGE_VIOLATION'})
        need(not geometry(2, {(0,1)}, require_completed_edges=False)[2] and geometry(2, {(0,1)})[2], 'UNCOMPLETED_EDGE_CONTROL')
        controls.append({'kind': 'positive', 'diagnostic': 'UNCOMPLETED_EDGE_CAP_ALLOWED'})
        zero_pairs = [p for p, c in cn.items() if p not in edges and c == 0]
        need(len(zero_pairs) == 14, 'ZERO_PAIR_UNIVERSE')
        cases = []; incompatible = 0
        # Every other nonedge is forbidden by its existing completed triangle.
        for mask in tqdm(range(1 << 14), desc='Exact extra-edge subsets', file=sys.stderr):
            if mask % 256 == 0:
                tick()
            added = {p for bit, p in enumerate(zero_pairs) if mask & (1 << bit)}
            h = edges | added
            hn, hc, hb = geometry(16, h, require_completed_edges=False)
            if hb:
                incompatible += 1
                continue
            f = len(added)
            allowed = {tuple(sorted((u,v))) for i in (0,1)
                       for u in (8+i,12+i) for v in (10+i,14+i)}
            need(added <= allowed and all(sum(v in e for e in added) <= 1 for v in range(8,16)), 'EXTRA_EDGE_EXHAUSTION')
            delta = {pair: (1 if pair in h else 2) - c for pair, c in hc.items()}
            need(all(value >= 0 for value in delta.values()), 'NEGATIVE_DEFICIT')
            anchors = set(range(4))
            need(all(delta[p] == 0 for p in itertools.combinations(range(4),2)), 'ANCHOR_SATURATION')
            for c in anchors:
                leaves = [s for s in range(4,16) if delta[tuple(sorted((c,s)))] > 0]
                need(all(delta[tuple(sorted(p))] == 0 for p in itertools.combinations(leaves,2)), 'ANCHOR_LEAF_SATURATION')
            v = sum(14-len(n) for n in hn)
            p = sum(delta.values())
            t = sum(14-len(hn[c]) for c in anchors)
            r = sum(delta[(c,s)] for c in anchors for s in range(4,16))
            n = 99-16-t; e = v-t-r; q = p-r
            need((v,p,t,r,n,e,q) == (152-2*f,72-9*f,32,8-2*f,51,112,64-7*f), 'EXACT_BUDGET')
            need(q < 2*e - 3*n, 'COMPLETION_NOT_VETOED')
            cases.append({'added_edges': sorted(added), 'f': f, 'cut': v, 'pairs': p,
                          'T': t, 'R': r, 'N': n, 'E': e, 'Q': q, 'required_min_Q': 2*e-3*n})
        need(len(cases) + incompatible == 16384, 'COVERAGE')
        result.update(status='INDEPENDENT_FINITE_GEOMETRY_AND_COMPLETION_BUDGET_PASS',
                      controls=controls, note_sha256=NOTE_HASH, parsed_triangles=triples,
                      incidence_integer_word_sums=point_sums, word_sum_mod3=sum(word)%3,
                      base_pair_counts=[{'pair': p, 'CN': c, 'adjacent': p in edges} for p,c in cn.items()],
                      extra_edge_universe=zero_pairs, attempted_subsets=16384,
                      locally_incompatible_subsets=incompatible, locally_cap_compatible_cases=cases,
                      complete_extra_edge_subset_check=True,
                      limitations=['Only the literal configuration is excluded, with arbitrary extra edges permitted.',
                                   'Tangent counting implication is independently checked in a separate written audit; integer counts here are not a formal proof.',
                                   'No forced occurrence, minimal circuit classification, target graph or general nonexistence proof.',
                                   'Optional Fourier spectrum claim is checked on paper, not by floating-point eigenvalues.'])
    except BaseException as error:
        result.update(status='FAILED', error=repr(error))
        raise
    finally:
        result['elapsed_seconds'] = deadline.status()['elapsed_seconds']
        result['source_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        (out/'summary.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf8')


if __name__ == '__main__':
    main()
