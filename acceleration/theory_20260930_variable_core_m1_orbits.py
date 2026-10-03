"""Append eleven first-matching orbit selectors without assuming automorphisms."""
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import platform
import subprocess
import sys
from tqdm import tqdm
from theory_20260930_eight_full99_cnf import ResourceCap, digest, package, save

ROOT = Path(__file__).resolve().parents[1]
B = ROOT/'acceleration/results'
CENSUS = B/'20260930_triangle_matching_pair_census_v2'
BASE = B/'20260930_variable_core_factor_cnf'
GATES = {
    B/'20260930_independent_review/triangle_matching_pair_census/summary.json': '085748fd2ebb03bdb7ea6048d782be0c17ce8cadef4ea32028cb58ca6b0efb79',
    B/'20260930_independent_review/variable_core_factor_cnf_v2/summary.json': 'ecc6c2ee488e68826e790360f3d47d6b029ac33953806bdab530ba50394a6ea0',
    B/'20260930_independent_review/unrestricted_triangle_factor/summary.json': 'a7d470ccf10df7dff77884c8bd1fe4784234ac80bc4e1b684e0050c3e33a4acd',
}


def key(p):
    return p.relative_to(ROOT).as_posix()


def conjugate(m, h):
    a = [0]*12
    for i in range(12):
        a[h[i]] = h[m[i]]
    return tuple(a)


def inverse(h):
    a = [0]*12
    for i, j in enumerate(h):
        a[j] = i
    return a


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    cap = ResourceCap()
    bindings = {}
    for p, expected in GATES.items():
        assert digest(p) == expected
        bindings[key(p)] = expected
        report = json.loads(p.read_bytes())
        for name, value in report['inputs_sha256'].items():
            assert digest(ROOT/name) == value, name
            bindings[name] = value
    for p in [Path(__file__), Path(__file__).with_name('theory_20260930_variable_core_m1_orbits_spec.md'),
              ROOT/'acceleration/theory_20260930_eight_full99_cnf.py', ROOT/'acceleration/theory_20260930_full_srg_validator.py',
              ROOT/'uv.lock', ROOT/'pyproject.toml']:
        bindings[key(p)] = digest(p)
    save(out/'manifest.json', dict(timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
        command=[sys.executable, *sys.argv], cwd=str(ROOT), python=platform.python_version(), inputs_sha256=bindings,
        question='Eleven M1 orbit normalization of the arbitrary-core necessary model by simultaneous relabelling.',
        limits=dict(seconds=120, memory_bytes=8*1024**3, solver_calls=0), random_seed=None,
        random_seed_reason='Deterministic traversal of the already audited census.'))
    census = json.loads((CENSUS/'summary.json').read_bytes())
    raw = json.loads((CENSUS/'matchings.json').read_bytes())
    matchings = [tuple(m) for m in (raw['matchings'] if isinstance(raw, dict) else raw)]
    assert len(matchings) == 10395
    lookup = {m: i for i, m in enumerate(matchings)}
    m0 = tuple(i^1 for i in range(12))
    generators = census['generators']
    records = {}
    representatives = []
    for stage_id in tqdm(range(11), desc='transport existing M1 orbits'):
        stage = json.loads((CENSUS/f'stage_{stage_id:02d}.json').read_bytes())
        rep = tuple(stage['M1'])
        representatives.append(list(rep))
        identity = tuple(range(12))
        todo = deque([(rep, identity)])
        seen = {rep}
        while todo:
            matching, forward = todo.popleft()
            back = inverse(forward)
            assert conjugate(m0, back) == m0 and conjugate(matching, back) == rep
            idx = lookup[matching]
            assert idx not in records
            records[idx] = dict(matching_index=idx, representative=stage_id, coordinate_permutation=back)
            for g in generators:
                new = conjugate(matching, g)
                if new not in seen:
                    seen.add(new)
                    todo.append((new, tuple(g[forward[i]] for i in range(12))))
        assert sorted(lookup[m] for m in seen) == stage['first_members']
        cap.check()
    assert set(records) == set(range(10395))
    save(out/'transports.json', dict(M0=list(m0), representatives=representatives,
        records=[records[i] for i in range(10395)], matching_universe_path=key(CENSUS/'matchings.json'),
        matching_universe_sha256=digest(CENSUS/'matchings.json')))
    base_model = json.loads((BASE/'model.json').read_bytes())
    ids = {tuple(v['endpoints']): v['id'] for v in base_model['matching_variables'] if v['fibre'] == 1}
    assert len(ids) == 66 and base_model['variables'] == 110904 and base_model['clauses'] == 518160
    selectors = list(range(110905, 110916))
    appended = [selectors]
    for selector, rep in zip(selectors, representatives):
        appended.extend([[-selector, ids[i, rep[i]]] for i in range(12) if i < rep[i]])
    assert len(appended) == 67
    with (out/'instance.cnf').open('xb') as f, (BASE/'instance.cnf').open('rb') as source:
        assert source.readline() == b'p cnf 110904 518160\n'
        f.write(b'p cnf 110915 518227\n')
        for chunk in iter(lambda: source.read(1048576), b''):
            f.write(chunk)
        for row in appended:
            f.write((' '.join(map(str, row))+' 0\n').encode())
    save(out/'extension.json', dict(schema='ARBITRARY_CORE_M1_ELEVEN_ORBIT_EXTENSION_V1',
        base_cnf_path=key(BASE/'instance.cnf'), base_cnf_sha256=digest(BASE/'instance.cnf'),
        base_model_path=key(BASE/'model.json'), base_model_sha256=digest(BASE/'model.json'),
        selectors=selectors, representatives=representatives, appended_clauses=appended,
        variables=110915, clauses=518227, primary_assignments_restricted=True,
        equivalence='Equisatisfiable after simultaneous coordinate and canonical C0-column relabelling; not identical primary assignments.',
        M2_P_restricted=False, automorphism_of_target_assumed=False, residual_D_included=False))
    save(out/'artifact_packages.json', dict(packages=[package(out/'instance.cnf', cap)],
        recovery='Concatenate ordered gzip parts and verify decompressed length/hash.'))
    save(out/'summary.json', dict(status='CANDIDATE_M1_ORBIT_NORMALIZED_VARIABLE_CORE_CNF',
        matching_universe=10395, representative_count=11, transports=10395,
        variables=110915, clauses=518227, additional_variables=11, additional_clauses=67,
        independent_verification='PENDING', solver_calls=0, target_resolution=False,
        outputs={p.name: dict(bytes=p.stat().st_size, sha256=digest(p)) for p in sorted(out.iterdir()) if p.is_file()}))
    print(json.dumps(dict(transports=10395, variables=110915, clauses=518227, solver_calls=0)))


if __name__ == '__main__':
    main()
