"""Unpruned 96-choice column domains for the fixed six-prism Gram factor."""
from datetime import datetime, timezone
from itertools import combinations, product
from pathlib import Path
import argparse
import json
import platform
import shutil
import subprocess
import sys
import time
from tqdm import tqdm
from theory_20260930_eight_full99_cnf import Clauses, Encoder, ResourceCap, counter_controls, digest, package, save

ROOT = Path(__file__).resolve().parents[1]
ENCODER = ROOT/'acceleration/theory_20260930_eight_full99_cnf.py'
ENCODER_SHA = '21c357543c9397456a911175b277da6e6caa769be31d18c12e034cc76d99074c'


def key(p):
    return Path(p).resolve().relative_to(ROOT).as_posix()


def geometry():
    c = [[0]*36 for _ in range(36)]
    for g in range(3):
        for i in range(12):
            c[12*g+i][12*g+(i^1)] = 1
    for g, k in combinations(range(3), 2):
        for i in range(12):
            c[12*g+i][12*k+i] = c[12*k+i][12*g+i] = 1
    gram = [[12*int(a == b)-c[a][b]-sum(c[a][z]*c[z][b] for z in range(36))
             +2-int(a//12 == b//12) for b in range(36)] for a in range(36)]
    labels = [list(p) for p in combinations(range(12), 2) if p[0]//2 != p[1]//2]
    return c, gram, labels


def domains(labels):
    records = []
    for d, (i, j) in enumerate(labels):
        remaining = sorted(set(range(6))-{i//2, j//2})
        selected = []
        for cell1 in combinations(remaining, 2):
            for bits in product(range(2), repeat=4):
                rows = sorted([i, j]+[12*(1 if a in cell1 else 2)+2*a+b for a, b in zip(remaining, bits)])
                item = dict(id=len(records)+1, column=d, rows=rows)
                records.append(item)
                selected.append(tuple(rows))
        assert len(selected) == len(set(selected)) == 96
    return records


def decode(model, assignment):
    values = {abs(x): x > 0 for x in assignment}
    assert set(values) == set(range(1, model['variables']+1))
    f = [[0]*60 for _ in range(36)]
    selected = []
    for d in range(60):
        choices = [item for item in model['choices'] if item['column'] == d and values[item['id']]]
        assert len(choices) == 1
        selected.append(choices[0]['id'])
        for row in choices[0]['rows']:
            f[row][d] = 1
    return dict(factor=f, selected_choice_ids=selected, target_graph=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    cap = ResourceCap()
    assert digest(ENCODER) == ENCODER_SHA
    inputs = [Path(__file__), Path(__file__).with_name('theory_20260930_prism_all_columns_spec.md'),
              ENCODER, ROOT/'uv.lock', ROOT/'pyproject.toml']
    save(out/'manifest.json', dict(timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        command=[sys.executable, *sys.argv], cwd=str(ROOT), python=platform.python_version(),
        uv_version=subprocess.check_output(['uv', '--version'], text=True).strip(),
        inputs_sha256={key(p): digest(p) for p in inputs}, status='CANDIDATE_ENCODING',
        limits=dict(seconds=120, memory_bytes=8*1024**3, solver_calls=0),
        random_seed=None, random_seed_reason='Deterministic complete column-domain construction.',
        scope='All abstract incidence factors for the specified identity-cross six-prism core; no unrestricted core coverage.'))
    save(out/'counter_controls.json', counter_controls())
    c, gram, labels = geometry()
    choices = domains(labels)
    pairs = [(a, b) for a, b in combinations(range(36), 2) if (a % 12)//2 != (b % 12)//2 and b >= 12]
    assert len(pairs) == 480 and len(choices) == 5760
    pair_inputs = {p: [] for p in pairs}
    column_inputs = [[] for _ in range(60)]
    for item in choices:
        column_inputs[item['column']].append(item['id'])
        for p in combinations(item['rows'], 2):
            if p in pair_inputs:
                pair_inputs[p].append(item['id'])
    assert sum(map(len, pair_inputs.values())) == 80640
    assert sum(gram[a][b] == 1 for a, b in pairs) == 120
    assert sum(gram[a][b] == 2 for a, b in pairs) == 360
    rows = []
    with (out/'clauses.body').open('xb') as body:
        clauses = Clauses(body, cap)
        enc = Encoder(len(choices), clauses)
        for d, inputs in enumerate(column_inputs):
            rows.append(enc.counter(inputs, 1, True, dict(kind='one_choice_per_column', column=d)))
        for a, b in tqdm(pairs, desc='exact prism pair equations'):
            rows.append(enc.counter(pair_inputs[a, b], gram[a][b], True, dict(kind='row_gram', pair=[a, b])))
    cnf = out/'instance.cnf'
    with cnf.open('xb') as stream, (out/'clauses.body').open('rb') as body:
        stream.write(f'p cnf {enc.top} {clauses.count}\n'.encode('ascii'))
        shutil.copyfileobj(body, stream)
    model = dict(schema='SIX_PRISM_COMPLETE_COLUMN_DOMAINS_V1', core_adjacency=c, target_gram=gram,
        canonical_C0_columns=labels, choices=choices, counter_rows=rows, variables=enc.top, clauses=clauses.count,
        components=[[12*g+2*a+b for g in range(3) for b in range(2)] for a in range(6)],
        outside_column_caps_encoded=False, residual_D_encoded=False, target_graph_encoded=False,
        symmetry_or_orbit_pruning=False, complement_pairing=False, solver_calls=0)
    save(out/'model.json', model)
    cap.check()
    save(out/'artifact_packages.json', dict(packages=[package(p, cap) for p in [cnf, out/'model.json']],
        recovery='Concatenate each ordered gzip part list, decompress and check original byte length/SHA256.'))
    result = dict(status='CANDIDATE_COMPLETE_SIX_PRISM_COLUMN_ENCODING', independent_verification='PENDING',
        canonical_columns=60, choices_per_column=96, primary_variables=5760, equations=len(rows),
        row_pair_equations=480, row_pair_incidence_entries=80640, variables=enc.top, clauses=clauses.count,
        build_seconds=time.monotonic()-cap.start, peak_working_set_bytes=cap.peak_bytes, solver_calls=0,
        outputs={p.name: dict(bytes=p.stat().st_size, sha256=digest(p)) for p in sorted(out.iterdir()) if p.is_file() and p.name != 'clauses.body'},
        limitations=['Fixed six-prism core only.', 'Column overlap caps and residual D are absent.',
                     'A SAT factor is not a target graph.', 'Any exclusion requires independent full encoding and proof checks.'])
    save(out/'summary.json', result)
    print(json.dumps({k: v for k, v in result.items() if k != 'outputs'}))


if __name__ == '__main__':
    main()
