"""Candidate exact identity-P lemma controls; no solver or independent approval."""
import argparse
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]
CORE_DIR = ROOT / 'acceleration/results/20260930_connected_identity_cores'
PINS = ['3d4ad2d5b8ff92ca3d7761ac79e3651e306052897c3327b4eec87d7a85dabe81',
        '23fb79efbc42fcaf7d54edb32311703be47fa96014a1c46ed00859a0753576e4',
        '40c23054a9276039b0dc1320594f102ae65d06c8e2c819a31d6600c3ee279eeb',
        'cdd61bb140888090f092af7bbc3dbc40399f8e06bb3b41781dcfba22f0f701f1']
GATE = ROOT / 'acceleration/results/20260930_independent_review/connected_identity_cores/summary.json'
GATE_HASH = 'efdcacb9130bf29a28ece4c07022bdab11ab953a862f117fc55f44bd5244d2b4'

def need(ok, message):
    if not ok: raise ValueError(message)

def digest(p): return sha256(p.read_bytes()).hexdigest()
def key(p): return p.resolve().relative_to(ROOT).as_posix()
def dump(p, obj):
    with p.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(obj, f, indent=2); f.write('\n')

def reconstruct(matchings):
    need(len(matchings) == 3, 'three matchings')
    for m in matchings:
        need(len(m) == 12 and all(type(v) is int and 0 <= v < 12 for v in m), 'matching range')
        need(all(m[a] != a and m[m[a]] == a for a in range(12)), 'perfect matching')
    c = [[0] * 36 for _ in range(36)]
    for g in range(3):
        for a in range(12):
            c[12*g+a][12*g+matchings[g][a]] = 1
            for h in range(3):
                if g != h: c[12*g+a][12*h+a] = 1
    gram = [[12*int(i == j)+2-c[i][j]-sum(c[i][k]*c[k][j] for k in range(36))-int(i//12 == j//12)
             for j in range(36)] for i in range(36)]
    return c, gram

def premise_column(bits):
    need(len(bits) == 36 and all(type(v) is int and v in (0,1) for v in bits), 'binary column')
    need(all(sum(bits[12*g+a] for g in range(3)) <= 1 for a in range(12)), 'distinct coordinates')

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args(); out = args.out.resolve(); out.mkdir(parents=True, exist_ok=False)
    start = time.monotonic(); timestamp = datetime.now(timezone.utc).isoformat()
    inputs = {key(GATE): digest(GATE)}; need(inputs[key(GATE)] == GATE_HASH, 'core gate unchanged')
    for p in [Path(__file__), Path(__file__).with_name('theory_20260930_identity_p_mixed_redundancy_spec.md'),
              ROOT/'docs/DERIVATION_20260930_IDENTITY_P_MIXED_REDUNDANCY.md', ROOT/'uv.lock', ROOT/'pyproject.toml']:
        inputs[key(p)] = digest(p)
    words = [w for w in product(range(3), repeat=6) if all(w.count(g) == 2 for g in range(3))]
    need(len(words) == 90, 'balanced fibre words')
    records = []; corruptions = []
    for index in tqdm(range(4), desc='Exact identity-P column controls'):
        p = CORE_DIR / f'core_{index:02}.json'; need(digest(p) == PINS[index], 'core pin'); inputs[key(p)] = digest(p)
        raw = json.loads(p.read_bytes()); c, gram = reconstruct([raw[f'M{g}'] for g in range(3)])
        need(raw['P'] == list(range(12)) and c == raw['core_adjacency'] and gram == raw['target_gram'], 'raw scope reconstruction')
        need(all(gram[12*g+a][12*h+a] == 0 for a in range(12) for g,h in combinations(range(3),2)), '36 cross-coordinate zeros')
        closed = [sum((int(i == j) + c[i][j]) << j for j in range(36)) for i in range(36)]
        forbidden = [(i,j) for i,j in combinations(range(36),2) if gram[i][j] == 0]
        mask_hist = Counter(); allowed = 0; count = 0; examples = []
        for coords in combinations(range(12),6):
            need(time.monotonic()-start < 120, 'protocol time cap')
            for fibres in words:
                support = [12*g+a for g,a in zip(fibres,coords)]
                mask = sum(1 << i for i in support)
                maximum = max((mask & row).bit_count() for row in closed)
                need(maximum <= 2, 'mixed-cap counterexample'); mask_hist[maximum] += 1; count += 1
                if all(not ((mask >> i)&1 and (mask >> j)&1) for i,j in forbidden):
                    allowed += 1
                    if len(examples) < 3: examples.append(support)
        need(count == 83160, 'complete support population')
        records.append(dict(core=key(p), support_population=count, mixed_cap_maximum_histogram=dict(mask_hist),
                            zero_Gram_pair_compatible_supports=allowed, example_compatible_supports=examples,
                            exact_Gram_entries_reconstructed=1296, full_factor_found=False))
        # These failures are validation controls, not mathematical counterexamples.
        for label,bits in [('coordinate_triangle', [int(i in (0,12,24)) for i in range(36)]),
                           ('repeated_coordinate', [int(i in (0,12)) for i in range(36)]),
                           ('nonbinary', [2]+[0]*35)]:
            try: premise_column(bits)
            except ValueError: corruptions.append(dict(core=index, corruption=label, rejected=True))
            else: raise AssertionError('corrupt premise accepted')
        triangle = sum(1 << i for i in (0,12,24))
        need(max((triangle & row).bit_count() for row in closed) == 3, 'mixed-cap failing control')
        bad = [row[:] for row in c]; bad[0][12] = 0
        need(bad != c, 'wrong core detectable')
        wrong_gram = [row[:] for row in gram]; wrong_gram[0][12] = 1
        need(wrong_gram != gram, 'wrong Gram detectable')
        corruptions.extend([dict(core=index,corruption=x,rejected=True) for x in ['wrong_core_entry','wrong_Gram_zero']])
    bad = [list(range(12)) for _ in range(3)]
    try: reconstruct(bad)
    except ValueError: corruptions.append(dict(corruption='fixed_point_matching',rejected=True))
    else: raise AssertionError('invalid matching accepted')
    dump(out/'controls.json', dict(cores=records, corruptions=corruptions))
    dump(out/'summary.json', dict(status='CANDIDATE_IDENTITY_P_MIXED_CAP_REDUNDANCY',
        claim_id='C-IDENTITY-P-FACTOR-DISTINCT-COORDINATES-MIXED-CAP-REDUNDANCY',revision=1,
        created_at=timestamp, completed_at=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        exact_command=[sys.executable,*sys.argv],working_directory=str(ROOT),
        versions=dict(python=platform.python_version(),uv=subprocess.check_output(['uv','--version'],text=True).strip()),
        inputs_sha256=inputs,outputs_sha256={key(out/'controls.json'):digest(out/'controls.json')},
        finite_core_examples=4, support_population_per_core=83160, total_core_support_evaluations=332640,
        corruption_controls=len(corruptions), wall_seconds=time.monotonic()-start,
        proof=key(ROOT/'docs/DERIVATION_20260930_IDENTITY_P_MIXED_REDUNDANCY.md'),
        independent_verification=None, independent_verification_reason='Producer cannot approve its own candidate.',
        scope='Binary36x60 exact-Gram factors; three arbitrary perfect matchings; all cross matchings identity.',
        limitations=['No existence or exclusion result.','No arbitrary-P claim.','No complete factor, graph, or residual D.',
                     'Finite controls do not establish the universal theorem.','Column-pair caps remain separate.'],
        existing_claim_scope_comparison=['C-TRIANGLE-CORE-IDENTITY-P-CONSTRUCTION r1: local-core construction only.',
                                        'C-TRIANGLE-CORE-PERMUTATION-PAIR-CAP-REDUCTION r1: local-core pair caps only.'],
        target_resolution='UNKNOWN'))
    print(json.dumps(dict(output=key(out),summary_sha256=digest(out/'summary.json'),wall_seconds=time.monotonic()-start)))

if __name__ == '__main__': main()
