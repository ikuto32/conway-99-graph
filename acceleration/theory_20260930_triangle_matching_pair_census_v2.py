"""Candidate complete ordered internal-matching pair census; no solver."""
from collections import Counter, deque
from datetime import datetime, timezone
from itertools import permutations, product
from pathlib import Path
import argparse
import hashlib
import json
import math
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
START = time.monotonic()


def check_limit():
    if time.monotonic() - START > 120:
        raise TimeoutError("preregistered 120-second wall limit")
    if sys.platform == 'win32':
        import ctypes
        from ctypes import wintypes
        class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
            _fields_ = [('cb', wintypes.DWORD), ('PageFaultCount', wintypes.DWORD)] + [(x, ctypes.c_size_t) for x in ('PeakWorkingSetSize', 'WorkingSetSize', 'QuotaPeakPagedPoolUsage', 'QuotaPagedPoolUsage', 'QuotaPeakNonPagedPoolUsage', 'QuotaNonPagedPoolUsage', 'PagefileUsage', 'PeakPagefileUsage')]
        item = PROCESS_MEMORY_COUNTERS()
        item.cb = ctypes.sizeof(item)
        ctypes.windll.psapi.GetProcessMemoryInfo(ctypes.windll.kernel32.GetCurrentProcess(), ctypes.byref(item), item.cb)
        if item.WorkingSetSize > 8 * 1024 ** 3:
            raise MemoryError("preregistered 8-GiB working-set limit")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')


def matchings(n):
    def rec(left, mate):
        if not left:
            yield tuple(mate)
            return
        a = left[0]
        for b in left[1:]:
            mate[a], mate[b] = b, a
            yield from rec([x for x in left if x not in (a, b)], mate)
    return sorted(rec(list(range(n)), [0] * n))


def centralizer(n):
    for pp in permutations(range(n // 2)):
        for flips in product(range(2), repeat=n // 2):
            yield tuple(2 * pp[u // 2] + ((u % 2) ^ flips[u // 2]) for u in range(n))


def compose(a, b):
    return tuple(a[x] for x in b)


def conjugate(m, p):
    out = [0] * len(m)
    for u, v in enumerate(m):
        out[p[u]] = p[v]
    return tuple(out)


def valid_permutation(p):
    return sorted(p) == list(range(len(p)))


def generators_for(full, n):
    target = set(full)
    identity = tuple(range(n))
    seen, gens = {identity}, []
    for g in full:
        if g in seen:
            continue
        gens.append(g)
        todo = deque(seen)
        while todo:
            p = todo.popleft()
            for gen in gens:
                q = compose(gen, p)
                if q not in seen:
                    assert q in target
                    seen.add(q)
                    todo.append(q)
            if len(seen) % 1024 == 0:
                check_limit()
    assert seen == target
    return gens


def orbit_partition(items, gens):
    lookup = {m: i for i, m in enumerate(items)}
    unseen = set(range(len(items)))
    orbits = []
    while unseen:
        a = min(unseen)
        unseen.remove(a)
        todo, members = deque([a]), [a]
        while todo:
            idx = todo.popleft()
            for gen in gens:
                j = lookup[conjugate(items[idx], gen)]
                if j in unseen:
                    unseen.remove(j)
                    todo.append(j)
                    members.append(j)
        orbits.append(sorted(members))
        check_limit()
    return orbits


def alternating_type(m0, m1):
    unseen, sizes = set(range(len(m0))), []
    while unseen:
        pending, component = [min(unseen)], set()
        while pending:
            u = pending.pop()
            if u not in component:
                component.add(u)
                pending.extend((m0[u], m1[u]))
        unseen.difference_update(component)
        sizes.append(len(component) // 2)
    return sorted(sizes)


def census(n, direct_control=False, out=None):
    items = matchings(n)
    m0 = tuple(u ^ 1 for u in range(n))
    full = list(centralizer(n))
    assert len(full) == len(set(full)) == 2 ** (n // 2) * math.factorial(n // 2)
    assert all(valid_permutation(p) and conjugate(m0, p) == m0 for p in full)
    gens = generators_for(full, n)
    first = orbit_partition(items, gens)
    if direct_control:
        for members in first:
            assert {conjugate(items[members[0]], p) for p in full} == {items[i] for i in members}
    stages = []
    for number, members in enumerate(first):
        m1 = items[members[0]]
        stabilizer = [p for p in full if conjugate(m1, p) == m1]
        assert len(stabilizer) * len(members) == len(full)
        sg = generators_for(stabilizer, n)
        second = orbit_partition(items, sg)
        records = []
        for orb in second:
            m2 = items[orb[0]]
            if direct_control:
                assert {conjugate(m2, p) for p in stabilizer} == {items[i] for i in orb}
            assert len(stabilizer) % len(orb) == 0
            records.append({'representative_index': orb[0], 'representative': m2,
                            'members': orb, 'orbit_size': len(orb),
                            'joint_stabilizer_order': len(stabilizer) // len(orb)})
        stage = {'first_representative_index': members[0], 'M1': m1,
                 'M0_M1_alternating_partition': alternating_type(m0, m1),
                 'first_members': members, 'first_orbit_size': len(members),
                 'stabilizer_order': len(stabilizer), 'stabilizer_generators': sg,
                 'second_orbits': records, 'second_orbit_count': len(second),
                 'second_covered_matchings': sum(len(x) for x in second)}
        assert stage['second_covered_matchings'] == len(items)
        stages.append(stage)
        if out is not None:
            save(out / ('stage_%02d.json' % number), stage)
        check_limit()
    weighted = sum(s['first_orbit_size'] * s['second_covered_matchings'] for s in stages)
    assert weighted == len(items) ** 2
    histogram = Counter(str(r['joint_stabilizer_order']) for s in stages for r in s['second_orbits'])
    return {'n': n, 'M0': m0, 'matchings': items, 'group_order': len(full), 'generators': gens,
            'first_orbit_count': len(first), 'ordered_pair_orbit_count': sum(s['second_orbit_count'] for s in stages),
            'labelled_ordered_pairs': weighted, 'unclassified_labelled_triples': weighted * math.factorial(n),
            'joint_stabilizer_order_histogram': dict(sorted(histogram.items(), key=lambda kv: int(kv[0]))),
            'stages': stages, 'direct_all_group_control': direct_control}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    sources = [Path(__file__), Path(__file__).with_name('theory_20260930_triangle_matching_pair_census_spec.md'), ROOT / 'uv.lock', ROOT / 'pyproject.toml']
    save(args.out / 'manifest.json', {'timestamp': datetime.now(timezone.utc).isoformat(),
        'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        'command': [sys.executable, *sys.argv], 'working_directory': str(ROOT),
        'python': platform.python_version(), 'platform': platform.platform(),
        'uv_version': subprocess.check_output(['uv', '--version'], text=True).strip(),
        'input_hashes': {p.relative_to(ROOT).as_posix(): digest(p) for p in sources},
        'limits': {'wall_seconds': 120, 'memory_bytes': 8 * 1024 ** 3},
        'random_seed': None, 'random_seed_reason': 'Exact deterministic enumeration',
        'numerical_thresholds': None, 'numerical_thresholds_reason': 'No floating-point decisions',
        'question': 'Complete H-orbits on ordered pairs of twelve-point perfect matchings, with P arbitrary.',
        'status': 'CANDIDATE', 'target_automorphism_assumed': False})
    try:
        assert not valid_permutation((0, 0, 2, 3))
        controls = [census(4, True), census(6, True)]
        save(args.out / 'controls.json', {'positive': controls, 'corrupt_duplicate_permutation_rejected': True,
             'independent_review': False, 'shared_code_disclosure': 'Controls use producer conjugation and enumeration helpers.'})
        result = census(12, out=args.out)
        save(args.out / 'matchings.json', result.pop('matchings'))
        result.pop('stages')
        result.update({'status': 'CANDIDATE_COMPLETE_MATCHING_PAIR_CENSUS',
                       'independent_verification': 'PENDING', 'target_resolution': False,
                       'elapsed_seconds': time.monotonic() - START,
                       'limitations': ['P is unclassified; no complete 39-vertex core census.', 'No outside incidence factor, residual graph, extension, or nonexistence claim.'],
                       'output_hashes': {p.resolve().relative_to(ROOT).as_posix(): digest(p) for p in sorted(args.out.iterdir()) if p.is_file()}})
        save(args.out / 'summary.json', result)
        print(json.dumps({k: v for k, v in result.items() if k in ('status', 'first_orbit_count', 'ordered_pair_orbit_count', 'joint_stabilizer_order_histogram', 'elapsed_seconds', 'labelled_ordered_pairs', 'unclassified_labelled_triples')}))
    except Exception as exc:
        save(args.out / 'failure.json', {'status': 'INCOMPLETE', 'error': repr(exc), 'elapsed_seconds': time.monotonic() - START})
        raise


if __name__ == '__main__':
    main()

