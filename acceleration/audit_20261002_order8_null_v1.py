"""Independent exact checking of the selected order-eight aggregate null witness.

No producer imports. Reconstruct marked-extension equations by graph isomorphism
and explicit automorphism permutations, then contract immutable flag coefficients
and use exact Schur complements. This does not construct a graph or prove the
input catalogue exhaustive.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
from fractions import Fraction
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
COEFF = ROOT / 'external_conway99_research/attempts/wave147-alternative-lane/coefficients.json.gz'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def graph(n, mask):
    need(type(n) is int and type(mask) is int and 1 <= n <= 8 and 0 <= mask < 1 << (n*(n-1)//2), 'graph mask range')
    a = [[0]*n for _ in range(n)]
    for bit, (u, v) in enumerate(itertools.combinations(range(n), 2)):
        a[u][v] = a[v][u] = (mask >> bit) & 1
    return a


def signature(a):
    d = [sum(row) for row in a]
    return tuple(sorted((d[u], tuple(sorted(d[v] for v in range(len(a)) if a[u][v]))) for u in range(len(a))))


def iso(a, b):
    """Backtracking adjacency-preserving bijection, distinct from min-mask canonicalization."""
    if len(a) != len(b) or signature(a) != signature(b):
        return None
    n = len(a)
    da, db = [sum(row) for row in a], [sum(row) for row in b]
    candidates = [[v for v in range(n) if da[u] == db[v] and
                   sorted(da[w] for w in range(n) if a[u][w]) == sorted(db[w] for w in range(n) if b[v][w])]
                  for u in range(n)]
    order = sorted(range(n), key=lambda u: (len(candidates[u]), -da[u], u))
    mapping = [-1]*n
    used = set()
    def visit(depth):
        if depth == n:
            return tuple(mapping)
        u = order[depth]
        for v in candidates[u]:
            if v not in used and all(a[u][w] == b[v][mapping[w]] for w in order[:depth]):
                mapping[u] = v
                used.add(v)
                result = visit(depth+1)
                if result is not None:
                    return result
                used.remove(v)
                mapping[u] = -1
        return None
    return visit(0)


def mark_orbits(a):
    n = len(a)
    degrees = [sum(row) for row in a]
    autos = [p for p in itertools.permutations(range(n))
             if all(degrees[u] == degrees[p[u]] for u in range(n)) and
             all(a[u][v] == a[p[u]][p[v]] for u in range(n) for v in range(u))]
    need(autos, 'identity automorphism')
    marks = {(u,) for u in range(n)} | set(itertools.combinations(range(n), 2))
    groups = set()
    while marks:
        seed = min(marks, key=lambda m: (len(m), m))
        orbit = frozenset(tuple(sorted(p[u] for u in seed)) for p in autos)
        need(orbit <= marks, 'disjoint complete mark orbits')
        marks -= orbit
        groups.add(orbit)
    return groups


def exact_psd(matrix):
    """Exact PSD criterion: positive Schur pivots or identically zero pivot rows."""
    n = len(matrix)
    need(all(len(row) == n for row in matrix) and all(matrix[i][j] == matrix[j][i] for i in range(n) for j in range(i)), 'symmetric square moment')
    a = [[Fraction(x) for x in row] for row in matrix]
    positive = 0
    for k in range(n):
        pivot = a[k][k]
        need(pivot >= 0, 'negative exact Schur pivot')
        if pivot == 0:
            need(all(a[k][j] == 0 for j in range(k, n)), 'nonzero row at zero PSD pivot')
            continue
        positive += 1
        for i in range(k+1, n):
            for j in range(i, n):
                a[i][j] -= a[i][k]*a[k][j]/pivot
                a[j][i] = a[i][j]
    return positive


def reconstruct(model, deadline):
    import math
    keys = [tuple(x) for x in model['variables']]
    need(len(keys) == len(set(keys)) == 1223, '1223 distinct variables')
    graphs = [graph(*key) for key in keys]
    lookup = defaultdict(list)
    for j, (key, a) in enumerate(zip(keys, graphs)):
        lookup[key[0], signature(a)].append(j)
        for u, v in itertools.combinations(range(len(a)), 2):
            need(sum(a[u][w]*a[v][w] for w in range(len(a))) <= (1 if a[u][v] else 2), 'local common-neighbor caps')
    def locate(a):
        matches = [(j, mapping) for j in lookup[len(a), signature(a)] if (mapping := iso(a, graphs[j])) is not None]
        need(len(matches) == 1, 'unique listed isomorphism class')
        return matches[0]
    descriptors, accum, recorded = {}, {}, {}
    for row in model['equations']:
        terms = Counter()
        for j, coefficient in row['terms']:
            need(type(j) is int and 0 <= j < len(keys) and type(coefficient) is int and coefficient, 'integer sparse coefficient')
            need(j not in terms, 'duplicate sparse index')
            terms[j] = coefficient
        need(type(row['rhs']) is int, 'integer RHS')
        mark = None if row['mark'] is None else frozenset(tuple(m) for m in row['mark'])
        ident = row['kind'], row['order'], row['mask'], mark
        need(ident not in recorded, 'distinct row identity')
        recorded[ident] = (terms, row['rhs'])
    expected = {}
    for n in range(1, 9):
        expected['total', n, None, None] = (Counter({j:1 for j,key in enumerate(keys) if key[0] == n}), math.comb(99, n))
    for j, ((n, mask), a) in enumerate(zip(keys, graphs)):
        if n == 8:
            continue
        deadline.child_seconds(1)
        entries = [('deletion', None, 99-n)]
        for orbit in mark_orbits(a):
            if len(next(iter(orbit))) == 1:
                entries.append(('degree', orbit, sum(14-sum(a[u]) for (u,) in orbit)))
            else:
                entries.append(('common_neighbor', orbit, sum((1 if a[u][v] else 2)-sum(a[u][w]*a[v][w] for w in range(n)) for u,v in orbit)))
        descriptors[j] = entries
        for kind, orbit, left in entries:
            ident = kind, n, mask, orbit
            accum[ident] = Counter({j:-left}) if left else Counter()
    for h, ((n, _), a) in enumerate(zip(keys, graphs)):
        if n == 1:
            continue
        deadline.child_seconds(1)
        for removed in range(n):
            kept = [u for u in range(n) if u != removed]
            sub = [[a[u][v] for v in kept] for u in kept]
            j, mapping = locate(sub)
            neighbors = {mapping[i] for i,u in enumerate(kept) if a[removed][u]}
            for kind, orbit, _ in descriptors[j]:
                coefficient = 1 if orbit is None else sum(all(u in neighbors for u in mark) for mark in orbit)
                if coefficient:
                    accum[kind, n-1, keys[j][1], orbit][h] += coefficient
    expected.update({ident:(Counter({j:a for j,a in terms.items() if a}), 0) for ident,terms in accum.items()})
    need(expected == recorded and len(expected) == 4543, 'complete independently reconstructed marked-extension equations')
    return keys, graphs, locate


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--model', type=Path, required=True)
    ap.add_argument('--model-sha256', required=True)
    ap.add_argument('--witness', type=Path, required=True)
    ap.add_argument('--witness-sha256', required=True)
    ap.add_argument('--seconds', type=float, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='Independent complete integer equation reconstruction and two exact Schur PSD checks')
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    try:
        need(sha(args.model) == args.model_sha256 and sha(args.witness) == args.witness_sha256, 'exact frozen candidate input identities')
        model = json.loads(gzip.decompress(args.model.read_bytes()))
        witness = json.loads(args.witness.read_bytes())
        need(witness['model_sha256'] == args.model_sha256, 'witness/model binding')
        counts = witness['counts']
        need(len(counts) == 1223 and all(type(x) is int and x >= 0 for x in counts), '1223 nonnegative exact integers')
        need(not any(sum(counts[j]*a for j,a in row['terms'])-row['rhs'] for row in model['equations']), 'all4543 exact residuals zero')
        need(model['target'] == {'n':99, 'k':14, 'lambda_':1, 'mu':2}, 'exact target parameters of count model')
        keys, graphs, locate = reconstruct(model, deadline)
        n3 = [[0]*6 for _ in range(6)]
        for u,v in [(0,1),(1,2),(0,2),(3,4),(4,5),(3,5),(0,3),(1,4)]:
            n3[u][v] = n3[v][u] = 1
        n3index, _ = locate(n3)
        need(counts[n3index] == 4158, 'explicit six-vertex endpoint count4158')
        raw = json.loads(gzip.decompress(COEFF.read_bytes()))
        moments = {}
        for family, data in raw['families'].items():
            n = data['matrix_size']
            a = [[0]*n for _ in range(n)]
            for record in data['class_coefficients']:
                j, _ = locate(graph(record['order'], record['canonical_mask']))
                for u,v,c in record['upper_entries']:
                    need(all(type(x) is int for x in [u,v,c]) and 0 <= u <= v < n, 'integer upper moment coefficients')
                    a[u][v] += counts[j]*c
                    if u != v:
                        a[v][u] += counts[j]*c
            deadline.child_seconds(1)
            rank = exact_psd(a)
            save(out/(family+'_moment_integer.json'), a)
            moments[family] = {'dimension':n, 'exact_rank':rank, 'PSD':True, 'method':'Exact Fraction Schur complements; zero pivots require entire remaining row zero', 'matrix_sha256':sha(out/(family+'_moment_integer.json'))}
        need(sorted(x['dimension'] for x in moments.values()) == [66,87], 'both selected complete flag matrices')
        need(exact_psd([[1,1],[1,1]]) == 1, 'positive rank-deficient PSD control')
        rejected = []
        for name, damaged in [('negative_eigenvalue',[[1,2],[2,1]]), ('zero_diagonal_nonzero_row',[[0,1],[1,2]])]:
            try:
                exact_psd(damaged)
            except ValueError:
                rejected.append(name)
            else:
                raise ValueError('corrupted PSD fixture accepted')
        bad = counts[:]
        bad[n3index] += 1
        need(any(sum(bad[j]*a for j,a in row['terms'])-row['rhs'] for row in model['equations']), 'corrupted endpoint count rejected')
        report = {'status':'INDEPENDENT_ORDER8_SELECTED_RELAXATION_INTEGER_NULL_PASS', 'timestamp':datetime.now(timezone.utc).isoformat(),
                  'verifier':'/root', 'claim_revision':1, 'command':[sys.executable,*sys.argv], 'cwd':str(ROOT), 'python':platform.python_version(),
                  'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                  'input_hashes':{str(p.resolve().relative_to(ROOT)):sha(p) for p in [args.model,args.witness,COEFF,Path(__file__),ROOT/'acceleration/command_deadline.py',ROOT/'uv.lock']},
                  'variables':1223, 'complete_reconstructed_equations':4543, 'nonnegative_integer_counts':True, 'exact_zero_residuals':4543,
                  'explicit_N3_graph_edges':[[u,v] for u in range(6) for v in range(u+1,6) if n3[u][v]], 'N3_index':n3index, 'exact_N3_count':4158,
                  'moments':moments, 'controls':{'rejected_PSD':rejected,'corrupted_endpoint_rejected':True}, 'producer_imports':[],
                  'shared_components':['Python standard library, Fraction, existing deadline helper, immutable raw archived graph/flag coefficient data'],
                  'limitations':['No graph is constructed; no target resolution.', 'Catalogue completeness and universal flag coefficient derivation are not independently established here.', 'Conditional counting-row derivation assumes the listed catalogue covers induced graphs of a target.', 'Only the two explicit66/87 coefficient contractions are PSD; no all-order moment hierarchy claim.'],
                  'elapsed_seconds':time.monotonic()-start}
        save(out/'summary.json',report)
        print(json.dumps({'status':report['status'],'rows':4543,'moments':moments,'seconds':report['elapsed_seconds']}))
    except BaseException as error:
        save(out/'failure.json', {'timestamp':datetime.now(timezone.utc).isoformat(),'error':repr(error),'elapsed_seconds':time.monotonic()-start,'no_promotion':True})
        raise


if __name__ == '__main__':
    main()
