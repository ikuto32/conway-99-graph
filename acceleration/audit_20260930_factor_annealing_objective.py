"""Independent integer reference for full-factor permutation objective v1.

No heuristic producer imports. Positive nonempty calibration uses the separately
checked SRG243 fixture; a zero score is only a Gram factor, not a target graph.
"""
from copy import deepcopy
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
import argparse
import hashlib
import json
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT/'acceleration/results/20260930_srg243_residual_fixture/triangle_blocks.json'
GATE = ROOT/'acceleration/results/20260930_independent_review/srg243_residual_fixture/summary.json'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(p):
    with p.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def evaluate(core, factor):
    n = len(core)//3
    m = n*(n-2)//2
    require(n >= 2 and n % 2 == 0 and len(core) == 3*n, 'three even fibres')
    require(all(len(row) == 3*n and all(type(x) is int and x in (0,1) for x in row) for row in core), 'binary square core')
    require(all(core[i][i] == 0 and sum(core[i]) == 3 for i in range(3*n)), 'cubic simple core')
    require(all(core[i][j] == core[j][i] for i,j in combinations(range(3*n),2)), 'core symmetry')
    for g in range(3):
        for i in range(n):
            require(all(sum(core[g*n+i][k*n:(k+1)*n]) == 1 for k in range(3)), 'core block matchings')
    require(all(core[i][j] == int(j == (i^1)) for i in range(n) for j in range(n)), 'canonical M0')
    require(all(core[i][g*n+j] == int(i == j) for g in (1,2) for i in range(n) for j in range(n)), 'two canonical cross matchings')
    require(len(factor) == 3*n and all(len(row) == m and all(type(x) is int and x in (0,1) for x in row) for row in factor), 'binary factor dimensions')
    canonical = [pair for pair in combinations(range(n),2) if pair[1] != (pair[0]^1)]
    require(factor[:n] == [[int(i in pair) for pair in canonical] for i in range(n)], 'canonical C0 columns')
    for g in range(3):
        labels = []
        for d in range(m):
            support = tuple(i for i in range(n) if factor[g*n+i][d])
            require(len(support) == 2, 'two rows per fibre per column')
            labels.append(support)
        required = [pair for pair in combinations(range(n),2) if core[g*n+pair[0]][g*n+pair[1]] == 0]
        require(sorted(labels) == required, 'exact nonmatching-edge permutation')
        require(all(sum(row) == n-2 for row in factor[g*n:(g+1)*n]), 'row margins')
    neighbours = [set(j for j,x in enumerate(row) if x) for row in core]
    masks = [sum(x << d for d,x in enumerate(row)) for row in factor]
    gram = [[n*int(i == j)-core[i][j]-len(neighbours[i]&neighbours[j])+2-int(i//n == j//n)
             for j in range(3*n)] for i in range(3*n)]
    require(all((masks[i]&masks[j]).bit_count() == gram[i][j] for g in range(3)
                for i in range(g*n,(g+1)*n) for j in range(g*n,(g+1)*n)), 'within-fibre Gram')
    block_scores = []
    for g,k in combinations(range(3),2):
        block_scores.append(sum(((masks[i]&masks[j]).bit_count()-gram[i][j])**2
                               for i in range(g*n,(g+1)*n) for j in range(k*n,(k+1)*n)))
    columns = [set(i for i in range(3*n) if factor[i][d]) for d in range(m)]
    overlap_violations = [[d,e,len(columns[d]&columns[e])] for d,e in combinations(range(m),2) if len(columns[d]&columns[e]) > 2]
    mixed_violations = [[i,d,factor[i][d]+len(neighbours[i]&columns[d])] for i in range(3*n) for d in range(m)
                        if factor[i][d]+len(neighbours[i]&columns[d]) > 2]
    return dict(objective_version='TRIANGLE_FACTOR_CROSS_GRAM_SQUARED_V1', score=sum(block_scores),
        block_scores_01_02_12=block_scores, direction='MINIMIZE', integer_arithmetic=True,
        rows=3*n, columns=m, cross_entries_checked=3*n*n, within_entries_checked=3*n*n,
        mixed_cap_violations=mixed_violations, column_overlap_violations=overlap_violations,
        exact_Gram_factor=sum(block_scores) == 0, target_graph=False,
        meaning='Score zero means this fixed-core abstract Gram factor only; neither the caps nor residual D follow from the score.')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('mode', choices=['calibrate','evaluate'])
    ap.add_argument('--raw', type=Path)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    inputs = [Path(__file__), ROOT/'uv.lock', ROOT/'pyproject.toml']
    if args.mode == 'calibrate':
        require(digest(FIXTURE) == '3f8dfa3803d6a5db8146dd24a0857477e1aa061ab10dac0f9e6e564aabc86439', 'raw243 fixture pin')
        require(digest(GATE) == '28bbd97b8e69515c3eb0345e5aa2db12debfaa8a44e83b2e3487342104c5d50e', 'independent243 gate pin')
        raw = json.loads(FIXTURE.read_bytes())
        c, f = raw['cubic_core60'], raw['factor60x180']
        positive = evaluate(c,f)
        require(positive['score'] == 0 and not positive['mixed_cap_violations'] and not positive['column_overlap_violations'], 'known nonempty positive')
        swapped = deepcopy(f)
        for row in swapped[20:40]:
            row[0], row[1] = row[1], row[0]
        altered = evaluate(c,swapped)
        require(altered['score'] > 0, 'valid-domain corruption must affect exact cross-Gram score')
        failures = []
        for label, cc, ff in [('asymmetric_core',deepcopy(c),deepcopy(f)), ('nonbinary_factor',deepcopy(c),deepcopy(f)),
                              ('wrong_C0',deepcopy(c),deepcopy(f)), ('broken_permutation',deepcopy(c),deepcopy(f))]:
            if label == 'asymmetric_core': cc[0][1] ^= 1
            elif label == 'nonbinary_factor': ff[20][0] = True
            elif label == 'wrong_C0': ff[0][0] ^= 1
            else: ff[20][0] ^= 1
            try:
                evaluate(cc,ff)
            except ValueError as e:
                failures.append(dict(control=label,error=str(e)))
            else:
                raise AssertionError(label)
        result = dict(status='INDEPENDENT_FACTOR_OBJECTIVE_RAW_CHECKER_CALIBRATION_PASS',
            positive=positive, valid_domain_swapped_score=altered['score'], malformed_controls_rejected=failures,
            producer_imports=False, research_factor_supplied=False, target_resolution=False,
            limitation='This is independent raw-object/scoring calibration, not a GPU delta, acceptance-rule or search-outcome audit.')
        inputs += [FIXTURE,GATE]
    else:
        require(args.raw is not None,'raw artifact required')
        raw = json.loads(args.raw.read_bytes())
        result = evaluate(raw['core_adjacency'],raw['factor'])
        if 'claimed_score' in raw:
            require(type(raw['claimed_score']) is int and raw['claimed_score'] == result['score'], 'saved score identity')
        inputs += [args.raw.resolve()]
    result.update(timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),
        inputs_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in inputs})
    with (args.out/'summary.json').open('x',encoding='utf-8',newline='\n') as out:
        json.dump(result,out,indent=2)
        out.write('\n')
    print(json.dumps({k:v for k,v in result.items() if k in ('status','score','valid_domain_swapped_score')}))


if __name__ == '__main__':
    main()
