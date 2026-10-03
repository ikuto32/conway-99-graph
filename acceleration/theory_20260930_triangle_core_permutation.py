"""Exact candidate P-domain census for frozen normalized matching pairs."""
from datetime import datetime, timezone
from itertools import combinations, permutations
from pathlib import Path
import argparse
import hashlib
import json
import math
import platform
import subprocess
import sys
import time
from tqdm import tqdm
from theory_20260930_eight_full99_cnf import ResourceCap

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'acceleration/results/20260930_triangle_matching_pair_census_v2'
GATE = ROOT / 'acceleration/results/20260930_independent_review/triangle_matching_pair_census/summary.json'
GATE_SHA = '085748fd2ebb03bdb7ea6048d782be0c17ce8cadef4ea32028cb58ca6b0efb79'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(p, obj):
    p.write_text(json.dumps(obj, indent=2) + '\n', encoding='utf-8')


def all_matchings(n):
    def rec(left, m):
        if not left:
            yield tuple(m)
            return
        a = min(left)
        for b in sorted(left - {a}):
            m[a], m[b] = b, a
            yield from rec(left - {a, b}, m)
    return sorted(rec(set(range(n)), [0] * n))


def core(m0, m1, m2, perm):
    n = len(m0)
    assert sorted(perm) == list(range(n))
    rows = [0] * (3 + 3 * n)
    def edge(a, b):
        rows[a] |= 1 << b
        rows[b] |= 1 << a
    for a, b in combinations(range(3), 2):
        edge(a, b)
    for g, m in enumerate((m0, m1, m2)):
        for i in range(n):
            edge(g, 3 + g * n + i)
            edge(3 + g * n + i, 3 + g * n + m[i])
    for i in range(n):
        edge(3 + i, 3 + n + i)
        edge(3 + i, 3 + 2 * n + i)
        edge(3 + n + i, 3 + 2 * n + perm[i])
    return rows


def raw_caps(rows):
    return all((rows[a] & rows[b]).bit_count() + ((rows[a] >> b) & 1) <= 2 for a, b in combinations(range(len(rows)), 2))


def reduced_caps(m0, m1, m2, p):
    n = len(m0)
    return all(not ((m0[i] == m1[i] or m0[i] == m2[i]) and p[i] == m0[i]) and not (p[m1[i]] == i and p[i] == m2[i]) for i in range(n))


def transition_table(n):
    pairs = list(combinations(range(n), 2))
    tables = []
    for k in range(n // 2):
        table = {}
        for mask in range(1 << n):
            if mask.bit_count() == 2 * k:
                table[mask] = [(mask | (1 << a) | (1 << b), ei) for ei, (a, b) in enumerate(pairs) if not (mask & ((1 << a) | (1 << b)))]
        tables.append(table)
    return pairs, tables


def dp_count(m0, m1, m2, tables):
    n = len(m0)
    pairs, transitions = tables
    row_pairs = [(r, s) for r, s in enumerate(m1) if r < s]
    layers = [{0: 1}]
    weights, orientations = [], []
    for k, (r, s) in enumerate(row_pairs):
        options = []
        for a, b in pairs:
            legal = []
            for x, y in ((a, b), (b, a)):
                if ((m0[r] == m1[r] or m0[r] == m2[r]) and x == m0[r]) or ((m0[s] == m1[s] or m0[s] == m2[s]) and y == m0[s]):
                    continue
                if (x == s and y == m2[s]) or (y == r and x == m2[r]):
                    continue
                legal.append((x, y))
            options.append(legal)
        weight = [len(x) for x in options]
        orientations.append(options)
        weights.append(weight)
        next_layer = {}
        for mask, count in layers[-1].items():
            for new_mask, ei in transitions[k][mask]:
                if weight[ei]:
                    next_layer[new_mask] = next_layer.get(new_mask, 0) + count * weight[ei]
        layers.append(next_layer)
    full = (1 << n) - 1
    total = layers[-1].get(full, 0)
    witness = None
    if total:
        witness = [-1] * n
        mask = full
        for k in reversed(range(n // 2)):
            r, s = row_pairs[k]
            for ei, (a, b) in enumerate(pairs):
                bits = (1 << a) | (1 << b)
                if mask & bits == bits and weights[k][ei] and layers[k].get(mask ^ bits, 0):
                    witness[r], witness[s] = orientations[k][ei][0]
                    mask ^= bits
                    break
            else:
                raise AssertionError('positive count lacks predecessor')
        assert mask == 0 and sorted(witness) == list(range(n))
    return total, witness, layers


def controls(cap):
    records = []
    for n in (4, 6):
        m0 = tuple(i ^ 1 for i in range(n))
        mm = all_matchings(n)
        if n == 6:
            mm = [mm[0], mm[7], mm[-1]]
        table = transition_table(n)
        comparisons = 0
        for m1 in mm:
            for m2 in mm:
                count = 0
                for p in permutations(range(n)):
                    direct = raw_caps(core(m0, m1, m2, p))
                    assert direct == reduced_caps(m0, m1, m2, p)
                    count += direct
                    comparisons += 1
                got, witness, _ = dp_count(m0, m1, m2, table)
                assert got == count
                if witness is not None:
                    assert raw_caps(core(m0, m1, m2, witness))
                cap.check()
        records.append({'n': n, 'ordered_matching_pairs': len(mm) ** 2, 'all_permutation_literal_comparisons': comparisons, 'dp_count_comparisons': len(mm) ** 2})
    m = tuple(i ^ 1 for i in range(12))
    p = tuple((i + 6) % 12 for i in range(12))
    rows = core(m, m, m, p)
    assert raw_caps(rows)
    rows[3] |= 1 << 17
    rows[17] |= 1 << 3
    assert not raw_caps(rows)
    try:
        core(m, m, m, [0] * 12)
    except AssertionError:
        repeated_rejected = True
    else:
        raise AssertionError('repeated permutation image accepted')
    return {'positive_records': records, 'extra_cross_edge_rejected': True, 'repeated_image_rejected': repeated_rejected, 'independent_review': False, 'trusted_shared_code': 'Raw-core construction and reduced inequalities separately coded here; both remain discovery-owned.'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    cap = ResourceCap()
    assert sha(GATE) == GATE_SHA
    assert json.loads(GATE.read_bytes())['status'] == 'INDEPENDENT_TRIANGLE_ORDERED_MATCHING_PAIR_CENSUS_PASS'
    sources = [Path(__file__), Path(__file__).with_name('theory_20260930_triangle_core_permutation_spec.md'), GATE, DATA / 'summary.json', ROOT / 'uv.lock', ROOT / 'pyproject.toml', ROOT / 'acceleration/theory_20260930_eight_full99_cnf.py', *sorted(DATA.glob('stage_*.json'))]
    manifest = {'timestamp': datetime.now(timezone.utc).isoformat(), 'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(), 'command': [sys.executable, *sys.argv], 'working_directory': str(ROOT), 'python': platform.python_version(), 'uv_version': subprocess.check_output(['uv', '--version'], text=True).strip(), 'input_hashes': {p.relative_to(ROOT).as_posix(): sha(p) for p in sources}, 'status': 'CANDIDATE', 'frozen_matching_pair_representatives': 3580, 'limits': {'seconds': 120, 'memory_bytes': 8 * 1024 ** 3}, 'shared_components': ['ResourceCap engineering helper only; no imported discovery mathematics.'], 'random_seed': None, 'random_seed_reason': 'Deterministic exact enumeration.', 'numerical_thresholds': None, 'numerical_thresholds_reason': 'All Boolean and integer.', 'scope': 'Labelled P pair-cap domains for complete fixed matching-pair representatives; no extension or P-orbit census.'}
    save(out / 'manifest.json', manifest)
    completed, total, weighted = 0, 0, 0
    records = []
    try:
        save(out / 'controls.json', controls(cap))
        cases = []
        for path in sorted(DATA.glob('stage_*.json')):
            stage = json.loads(path.read_bytes())
            for i, item in enumerate(stage['second_orbits']):
                cases.append((path.name, i, stage['M1'], item))
        assert len(cases) == 3580
        tables = transition_table(12)
        m0 = tuple(i ^ 1 for i in range(12))
        with (out / 'cases.jsonl').open('x', encoding='utf-8') as stream:
            for source, idx, m1, item in tqdm(cases, desc='Exact core P domains', mininterval=1):
                cap.check()
                m2 = item['representative']
                count, p, layers = dp_count(m0, m1, m2, tables)
                if p is not None:
                    assert raw_caps(core(m0, m1, m2, p))
                else:
                    save(out / ('zero_case_%04d.json' % completed), {'layers': layers, 'M0': m0, 'M1': m1, 'M2': m2})
                weight = 46080 // item['joint_stabilizer_order']
                assert weight * item['joint_stabilizer_order'] == 46080
                record = {'case': completed, 'source_stage': source, 'second_orbit_index': idx, 'M1': m1, 'M2': m2, 'joint_stabilizer_order': item['joint_stabilizer_order'], 'matching_pair_orbit_size': weight, 'labelled_permutation_count': count, 'witness_P': p, 'witness_literal_full39_caps_pass': p is not None}
                stream.write(json.dumps(record, separators=(',', ':')) + '\n')
                records.append(record)
                total += count
                weighted += count * weight
                completed += 1
                if completed % 100 == 0:
                    stream.flush()
                    save(out / 'checkpoint.json', {'completed': completed, 'frozen_cases': 3580, 'completed_prefix_labelled_P_sum': total, 'completed_prefix_weighted_triples': weighted})
        assert sum(r['matching_pair_orbit_size'] for r in records) == 10395 ** 2
        summary = {'status': 'CANDIDATE_COMPLETE_CORE_PAIRCAP_PERMUTATION_CENSUS', 'independent_verification': 'PENDING', 'completed_matching_pair_cases': completed, 'frozen_matching_pair_cases': 3580, 'zero_permutation_domains': sum(r['labelled_permutation_count'] == 0 for r in records), 'distinct_positive_witnesses_by_case': sum(r['witness_P'] is not None for r in records), 'minimum_labelled_P_domain': min(r['labelled_permutation_count'] for r in records), 'maximum_labelled_P_domain': max(r['labelled_permutation_count'] for r in records), 'unweighted_P_counts_sum': total, 'weighted_labelled_cap_compatible_triples': weighted, 'labelled_triple_population': 10395 ** 2 * math.factorial(12), 'counting_scope': 'All normalized labelled(M1,M2,P) triple choices before paircaps; weights restore exact matching-pair orbit sizes. Counts are not canonical P-orbits or target extensions.', 'target_resolution': False, 'overall_search_coverage': 'UNKNOWN; no validated denominator.', 'elapsed_seconds': time.monotonic() - cap.start, 'peak_working_set_bytes': cap.peak_bytes, 'output_hashes': {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(out.iterdir()) if p.is_file()}}
        save(out / 'summary.json', summary)
        print(json.dumps({k: v for k, v in summary.items() if k != 'output_hashes'}))
    except Exception as exc:
        save(out / 'failure.json', {'status': 'INCOMPLETE_UNKNOWN', 'error': repr(exc), 'completed_cases': completed, 'elapsed_seconds': time.monotonic() - cap.start})
        raise


if __name__ == '__main__':
    main()
