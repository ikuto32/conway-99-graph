"""Exact affine GF(2) necessary screen, with raw local-option certificates."""
from datetime import datetime, timezone
from itertools import combinations, product
from pathlib import Path
import argparse, hashlib, json, platform, subprocess, sys, time, traceback
from tqdm import tqdm
ROOT = Path(__file__).resolve().parents[1]
B = 'acceleration/results/20260930_'
RAW = B + 'hadamard20_support/six_prism.json'
LOCAL = B + 'hadamard_triplicate_counts/local_triples.json'
COUNT = B + 'independent_review/count_master_sat_outcome/independent_count_profile.json'
BATCH = B + 'hadamard_seven_remaining_cnfs/run02/summary.json'
PINS = {RAW: 'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d', LOCAL: '9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776', COUNT: '0714d44765e29a4f0bf5c0769a25a5ed805a9602ae9a5f25b8c327ce4afe3152', BATCH: 'eabd989bd427c6fcfc57564d62b907d80630f1b5c7b7d56df17fa09f2df16119'}
def need(ok, message):
    if not ok:
        raise ValueError(message)
def sha(path):
    with (ROOT / path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()
def read(path):
    return json.loads((ROOT / path).read_bytes())
def save(path, value):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')
def reduce_vector(vector, basis):
    used = 0
    while vector:
        pivot = vector.bit_length() - 1
        if pivot not in basis:
            break
        row, representation = basis[pivot]
        vector ^= row
        used ^= representation
    return vector, used
def solve_affine(generators, target):
    basis = {}
    for index, vector in enumerate(generators):
        residual, used = reduce_vector(vector, basis)
        if residual:
            basis[residual.bit_length() - 1] = (residual, used ^ (1 << index))
    residual, used = reduce_vector(target, basis)
    if not residual:
        return dict(feasible=True, rank=len(basis), selected_generators=[i for i in range(len(generators)) if used >> i & 1], residual_hex='0x0', separating_functional_hex=None)
    # Solve the transposed homogeneous system with one nonzero residual pivot.
    functional = 1 << (residual.bit_length() - 1)
    for pivot in sorted(basis):
        row = basis[pivot][0]
        if (row & functional).bit_count() & 1:
            functional ^= 1 << pivot
    need(all((v & functional).bit_count() % 2 == 0 for v in generators), 'exact annihilator')
    need((target & functional).bit_count() % 2 == 1, 'exact separated target')
    return dict(feasible=False, rank=len(basis), selected_generators=None, residual_hex=hex(residual), separating_functional_hex=hex(functional))
def controls():
    checked = 0
    for rows in product(range(4), repeat=3):
        reachable = {0}
        for value in rows:
            reachable |= {x ^ value for x in list(reachable)}
        for target in range(4):
            result = solve_affine(rows, target)
            need(result['feasible'] == (target in reachable), 'tiny exhaustive linear span')
            if result['feasible']:
                actual = 0
                for i in result['selected_generators']:
                    actual ^= rows[i]
                need(actual == target, 'actual combination certificate')
            checked += 1
    need(not solve_affine([1], 2)['feasible'], 'known inconsistent system')
    need(solve_affine([1, 2], 3)['feasible'], 'known consistent system')
    return dict(exhaustive_tiny_systems=checked, exact_positive_and_negative=True)
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    began = time.monotonic()
    pins = {}
    try:
        for path, digest in PINS.items():
            need(sha(path) == digest, 'input pin ' + path)
            pins[path] = digest
        for path in [Path(__file__).relative_to(ROOT), Path(__file__).with_name(Path(__file__).stem + '_spec.md').relative_to(ROOT), Path('uv.lock'), Path('pyproject.toml')]:
            pins[path.as_posix()] = sha(path)
        save(out / 'manifest.json', dict(timestamp=datetime.now(timezone.utc).isoformat(), source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), command=[sys.executable, *sys.argv], cwd=str(ROOT), python=platform.python_version(), inputs_sha256=pins, limits=dict(wall_seconds=180, solver_calls=0), selection='One unrestricted local-catalogue domain on the fixed support, the one saved eight-count profile, and the frozen215 literal seven profiles. No target-wide coverage.'))
        save(out / 'controls.json', controls())
        raw = read(RAW)
        local = read(LOCAL)
        words, triples = local['words'], local['survivors']
        groups = list(dict.fromkeys(tuple(a for a in range(12) if raw['L'][a][d]) for d in range(60)))
        #153 local entries:18 diagonal entries and135 between different coordinates.
        cells = [(a, f, a, f) for a in range(6) for f in range(3)] + [(a, f, b, h) for a, b in combinations(range(6), 2) for f, h in product(range(3), repeat=2)]
        local_vectors = []
        for triple in triples:
            vector = 0
            for index, (a, f, b, h) in enumerate(cells):
                if sum(words[w][a] == f and words[w][b] == h for w in triple) % 2:
                    vector |= 1 << index
            local_vectors.append(vector)
        global_cells = [(a, f, a, f) for a in range(12) for f in range(3)] + [(a, f, b, h) for a, b in combinations(range(12), 2) if a // 2 != b // 2 for f, h in product(range(3), repeat=2)]
        need(len(cells) == 153 and len(global_cells) == 576, 'cell populations')
        index = {cell: i for i, cell in enumerate(global_cells)}
        mappings = [[index[group[a], f, group[b], h] for a, f, b, h in cells] for group in groups]
        def lift(vector, group):
            result = 0
            while vector:
                bit = vector & -vector
                result ^= 1 << mappings[group][bit.bit_length() - 1]
                vector ^= bit
            return result
        target = sum((raw['prescribed_Gram36'][12*f+a][12*h+b] % 2) << i for i, (a, f, b, h) in enumerate(global_cells))
        cache = {}
        def compressed_domain(ids):
            key = tuple(ids)
            if key not in cache:
                basis, selected = {}, []
                reference = local_vectors[ids[0]]
                for ti in ids[1:]:
                    residual, used = reduce_vector(local_vectors[ti] ^ reference, basis)
                    if residual:
                        basis[residual.bit_length() - 1] = (residual, 0)
                        selected.append(ti)
                cache[key] = (ids[0], selected)
            return cache[key]
        balanced = [i for i, triple in enumerate(triples) if all(sum(words[w][a] == f for w in triple) == 1 for a in range(6) for f in range(3))]
        cases = [('full_local_catalogue', [list(range(len(triples)))] * 20), ('literal_eight_count_profile', read(COUNT)['local_survivor_indices_by_group'])]
        for record in read(BATCH)['records']:
            path = str(Path(record['scope_path']).parent / 'selected_profile.json').replace('\\', '/')
            profile = read(path)
            pins[path] = sha(path)
            by_group = {}
            for ref, group in zip(profile['local_domains'], profile['group_ids']):
                need(sha(ref['path']) == ref['sha256'], 'complete seven initial domain')
                pins[ref['path']] = ref['sha256']
                domain = read(ref['path'])
                by_group[group] = domain['local_survivor_indices']
            cases.append((profile['id'], [by_group.get(g, balanced) for g in range(20)]))
        records = []
        for identity, domains in tqdm(cases, desc='Exact affine Gram mod2', mininterval=1):
            rhs, generators, generator_records, references = target, [], [], []
            for group, ids in enumerate(domains):
                reference, selected = compressed_domain(ids)
                references.append(reference)
                rhs ^= lift(local_vectors[reference], group)
                for ti in selected:
                    generators.append(lift(local_vectors[ti] ^ local_vectors[reference], group))
                    generator_records.append(dict(group=group, local_survivor_index=ti, reference_local_survivor_index=reference))
            certificate = solve_affine(generators, rhs)
            if certificate['feasible']:
                actual = 0
                for i in certificate['selected_generators']:
                    actual ^= generators[i]
                need(actual == rhs, 'complete actual global combination')
            record = dict(identity=identity, domain_counts=list(map(len, domains)), references=references, generators=generator_records, target_minus_references_hex=hex(rhs), certificate=certificate)
            save(out / (identity + '.json'), record)
            records.append(dict(identity=identity, feasible=certificate['feasible'], rank=certificate['rank'], generators=len(generators)))
            need(time.monotonic() - began < 180, '180second allocation')
        save(out / 'summary.json', dict(status='CANDIDATE_FIXED_SUPPORT_AFFINE_GRAM_GF2_SCREEN_COMPLETE', inputs_sha256=pins, outputs_sha256={p.relative_to(ROOT).as_posix(): sha(p.relative_to(ROOT)) for p in out.iterdir()}, records=records, model_population=len(records), inconsistent_models=sum(not r['feasible'] for r in records), local_catalogue_size=len(triples), compressed_distinct_domains=len(cache), native_calls=0, elapsed_seconds=time.monotonic()-began, scope='Necessary affine relaxation modulo2 only; arbitrary XOR combinations do not select one valid triple per group.', target_resolution=False, independent_approval=False))
        print(json.dumps(dict(models=len(records), inconsistent=sum(not r['feasible'] for r in records), elapsed_seconds=time.monotonic()-began)))
    except BaseException as error:
        save(out / 'failure.json', dict(error=repr(error), traceback=traceback.format_exc(), inputs_sha256=pins, source_sha256=sha(Path(__file__).relative_to(ROOT))))
        raise
if __name__ == '__main__':
    main()
