"""Freeze four necessary fixed-core reductions; no solver calls or approval."""
import argparse
import hashlib
import itertools
import json
import platform
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / 'acceleration/results'
BASE = RESULTS / '20260930_variable_core_factor_cnf'
CORES = RESULTS / '20260930_connected_identity_cores'
GATES = {
    RESULTS / '20260930_independent_review/connected_identity_cores/summary.json':
        'efdcacb9130bf29a28ece4c07022bdab11ab953a862f117fc55f44bd5244d2b4',
    RESULTS / '20260930_independent_review/variable_core_factor_cnf_v2/summary.json':
        'ecc6c2ee488e68826e790360f3d47d6b029ac33953806bdab530ba50394a6ea0',
}
BASE_HASHES = {
    'instance.cnf': '21b2cd8067971da66317afb3814e2b4f9232528fc8b1daceda4ff80594425684',
    'model.json': '42071b881973450db0f1813356133688b7532dd7d0495d37962acc5fa8c071f2',
    'scope.json': 'd5366bd061ab9f248d861522241fd28862f7164f591788f859bba90c91936d60',
}


def need(ok, why):
    if not ok:
        raise ValueError(why)


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def key(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def save(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2) + '\n', encoding='utf-8', newline='\n')


def matching_edges(q):
    need(len(q) == 12 and all(type(v) is int for v in q), '12-coordinate integer matching')
    need(sorted(q) == list(range(12)), 'matching bijection')
    need(all(q[a] != a and q[q[a]] == a for a in range(12)), 'fixed-point-free involution')
    return [(a, b) for a, b in enumerate(q) if a < b]


def unit_rows(core, model):
    mids = {(r['fibre'], *r['endpoints']): r['id'] for r in model['matching_variables']}
    pids = {(r['row'], r['column']): r['id'] for r in model['permutation_variables']}
    need(len(mids) == 132 and len(pids) == 144, 'base metadata sizes')
    rows = []
    for fibre in (1, 2):
        for a, b in matching_edges(core[f'M{fibre}']):
            rows.append(dict(kind='matching', fibre=fibre, endpoints=[a, b], literal=mids[fibre, a, b]))
    perm = core['P']
    need(sorted(perm) == list(range(12)), 'P bijection')
    for a, b in enumerate(perm):
        rows.append(dict(kind='permutation', row=a, column=b, literal=pids[a, b]))
    return rows


def validate_rows(rows, core, model):
    need(rows == unit_rows(core, model), 'all semantic units match exact ordered mapping')
    need(len(rows) == 24 and len({r['literal'] for r in rows}) == 24, '24 distinct units')
    need(all(type(r['literal']) is int and 1 <= r['literal'] <= 110904 for r in rows), 'positive base IDs')


def controls(core, model):
    matchings = [{(0, 1), (2, 3)}, {(0, 2), (1, 3)}, {(0, 3), (1, 2)}]
    matching_cases = 0
    for prescribed in matchings:
        for candidate in matchings:
            need((prescribed <= candidate) == (prescribed == candidate), 'small matching positive-unit uniqueness')
            matching_cases += 1
    permutation_cases = 0
    permutations = list(itertools.permutations(range(3)))
    for prescribed in permutations:
        for candidate in permutations:
            need(all(candidate[a] == b for a, b in enumerate(prescribed)) == (candidate == prescribed), 'small permutation positive-unit uniqueness')
            permutation_cases += 1
    good = unit_rows(core, model)
    validate_rows(good, core, model)
    rejected = []
    for name in ('omitted_unit', 'duplicated_unit', 'wrong_edge_literal', 'nonsymmetric_matching'):
        rows = json.loads(json.dumps(good))
        altered = json.loads(json.dumps(core))
        if name == 'omitted_unit': rows.pop()
        elif name == 'duplicated_unit': rows[-1] = rows[0]
        elif name == 'wrong_edge_literal': rows[0]['literal'] += 1
        else: altered['M1'][0] = altered['M1'][1]
        try:
            validate_rows(rows, altered, model)
        except ValueError as error:
            rejected.append(dict(name=name, rejected=True, reason=str(error)))
        else:
            raise AssertionError('corruption accepted: ' + name)
    return dict(matching_cases=matching_cases, permutation_cases=permutation_cases,
                positive_research_mapping_checked=True, rejected_controls=rejected,
                independent_review=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True, type=Path)
    args = ap.parse_args()
    started = time.monotonic()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    bindings = {}
    gate_objects = []
    for path, expected in GATES.items():
        need(digest(path) == expected, 'frozen independent gate ' + key(path))
        bindings[key(path)] = expected
        obj = json.loads(path.read_bytes())
        gate_objects.append(obj)
        for p, h in obj['inputs_sha256'].items():
            need(digest(ROOT / p) == h, 'gate-bound input ' + p)
            bindings[p] = h
    need(gate_objects[0]['status'] == 'INDEPENDENT_CONNECTED_IDENTITY_CORE_PORTFOLIO_PASS', 'domain approval status')
    for name, h in BASE_HASHES.items():
        p = BASE / name
        need(digest(p) == h, 'authenticated original base ' + name)
        bindings[key(p)] = h
    for p in (Path(__file__), Path(__file__).with_suffix('').with_name(Path(__file__).stem + '_spec.md'), ROOT / 'uv.lock', ROOT / 'pyproject.toml'):
        bindings[key(p)] = digest(p)
    model = json.loads((BASE / 'model.json').read_bytes())
    need(model['variables'] == 110904 and model['clauses'] == 518160, 'base dimensions')
    cores = [json.loads((CORES / f'core_{i:02d}.json').read_bytes()) for i in range(4)]
    for i in range(4):
        p = CORES / f'core_{i:02d}.json'
        need(bindings[key(p)] == digest(p), 'raw core bound by independent domain gate')
    save(out / 'manifest.json', dict(schema='CONNECTED_FIXED_CORE_CNF_PREPARATION_V1',
        timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        command=[sys.executable, *sys.argv], working_directory=str(ROOT), python=platform.python_version(),
        uv_version=subprocess.check_output(['uv', '--version'], text=True).strip(),
        inputs_sha256=bindings, limits=dict(seconds=120, output_bytes=512*1024**2, solver_calls=0),
        random_seed=None, random_seed_null_reason='Deterministic four frozen cores; no random sampling.',
        scope='Four specified connected identity-P cores only; necessary factor and all base caps, no residual D.',
        independent_approval=False))
    save(out / 'controls.json', controls(cores[0], model))
    records = []
    for index, core in enumerate(tqdm(cores, desc='fixed connected-core CNFs')):
        need(core['P'] == list(range(12)) and core['connected36'] is True, 'chosen identity-P connected domain')
        rows = unit_rows(core, model)
        validate_rows(rows, core, model)
        folder = out / f'core_{index:02d}'
        folder.mkdir()
        raw = folder / 'core.json'
        shutil.copyfile(CORES / f'core_{index:02d}.json', raw)
        save(folder / 'units.json', dict(core_index=index, core_path=key(raw), core_sha256=digest(raw), rows=rows))
        instance = folder / 'instance.cnf'
        with (BASE / 'instance.cnf').open('rb') as src, instance.open('wb') as dst:
            need(src.readline() == b'p cnf 110904 518160\n', 'base exact header')
            dst.write(b'p cnf 110904 518184\n')
            shutil.copyfileobj(src, dst)
            for row in rows:
                dst.write(f"{row['literal']} 0\n".encode('ascii'))
        records.append(dict(core_index=index, core_path=key(raw), core_sha256=digest(raw),
            units_path=key(folder / 'units.json'), units_sha256=digest(folder / 'units.json'),
            cnf_path=key(instance), cnf_sha256=digest(instance), cnf_bytes=instance.stat().st_size,
            variables=110904, clauses=518184, added_positive_units=24,
            base_model_path=key(BASE / 'model.json'), base_model_sha256=BASE_HASHES['model.json'],
            first_stage=core['first_stage'], second_orbit=core['second_orbit'],
            pair_representative_index=core['pair_representative_index']))
        need(time.monotonic() - started < 120, 'preparation time cap')
        need(sum(p.stat().st_size for p in out.rglob('*') if p.is_file()) <= 512*1024**2, 'preparation output cap')
    outputs = {key(p): digest(p) for p in sorted(out.rglob('*')) if p.is_file()}
    save(out / 'summary.json', dict(schema='CONNECTED_FIXED_CORE_CNF_BATCH_V1',
        status='CANDIDATE_CONNECTED_FIXED_CORE_CNF_BATCH_PENDING_INDEPENDENT_REVIEW',
        timestamp=datetime.now(timezone.utc).isoformat(), inputs_sha256=bindings, outputs_sha256=outputs,
        records=records, instances=4, solver_calls=0, target_resolution=False,
        scope='Exactly four selected core assignments; not a cover of arbitrary cores.',
        base_all_mixed_caps=True, base_all_column_caps=True, residual_D_encoded=False,
        target_automorphism_assumed=False, P_identity_is_without_loss=False,
        elapsed_seconds=time.monotonic()-started, independent_approval=False))
    print(json.dumps(dict(status='FOUR_FIXED_CONNECTED_CORE_CNFS_PREPARED', instances=4, solver_calls=0)))


if __name__ == '__main__':
    main()
