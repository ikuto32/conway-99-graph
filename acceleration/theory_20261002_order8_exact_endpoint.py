"""Produce exact rational PSD certificates for the endpoint aggregate witness.

No solver floating arithmetic enters the integer matrix or decomposition.
Independent checking of model/cut conventions and certificates is still needed.
"""
from datetime import datetime, timezone
from fractions import Fraction
from functools import reduce
import argparse
import gzip
import json
import math
from pathlib import Path
import subprocess
import sys
import time

from theory_20261002_order8_marked_extension_v4 import ROOT, sha, save
from theory_20261002_order8_psd_cuts import COEFFICIENTS, flag_data


def exact_moment(data, counts):
    matrix=[[0]*data['size'] for _ in range(data['size'])]
    for j,entries in data['records']:
        for u,v,a in entries:
            matrix[u][v]+=counts[j]*a
            if u!=v:
                matrix[v][u]+=counts[j]*a
    return matrix


def decompose(matrix):
    size=len(matrix)
    residual=[[Fraction(v) for v in row] for row in matrix]
    active=list(range(size));terms=[]
    while active:
        if any(residual[i][i]<0 for i in active):
            return dict(status='NOT_PSD_NEGATIVE_PIVOT',rank=len(terms),terms=terms)
        pivot=next((i for i in active if residual[i][i]>0),None)
        if pivot is None:
            if any(residual[i][j] for i in active for j in active):
                return dict(status='NOT_PSD_NONZERO_ZERO_DIAGONAL_BLOCK',rank=len(terms),terms=terms)
            break
        diagonal=residual[pivot][pivot]
        column=[residual[i][pivot]/diagonal if i in active else Fraction(0) for i in range(size)]
        denominator=math.lcm(*(v.denominator for v in column))
        integer_vector=[int(v*denominator) for v in column]
        common=reduce(math.gcd,integer_vector)
        if common:
            integer_vector=[v//common for v in integer_vector]
        multiplier=diagonal*Fraction(common,denominator)**2
        terms.append(dict(multiplier=[multiplier.numerator,multiplier.denominator],integer_vector=integer_vector))
        for i in active:
            for j in active:
                residual[i][j]-=diagonal*column[i]*column[j]
        active.remove(pivot)
    # Producer reconstruction is a calibration, not independent verification.
    recovered=[[Fraction(0) for _ in range(size)] for _ in range(size)]
    for term in terms:
        weight=Fraction(*term['multiplier']);vec=term['integer_vector']
        assert weight>0
        for i in range(size):
            for j in range(size):
                recovered[i][j]+=weight*vec[i]*vec[j]
    assert recovered==matrix
    return dict(status='EXACT_PSD_CANDIDATE',rank=len(terms),terms=terms,
                mathematical_identity='M=sum positive_rational_weight * integer_vector * integer_vector^T',
                independent=False)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--model',type=Path,required=True)
    parser.add_argument('--witness',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=False)
    start=time.monotonic()
    save(args.out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),
                                     source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                                     source_sha256=sha(Path(__file__)),command=[sys.executable,*sys.argv],cwd=str(ROOT),
                                     inputs=[dict(path=str(p),sha256=sha(p)) for p in [args.model,args.witness,COEFFICIENTS]],
                                     dependencies=[dict(path=str(ROOT/'acceleration'/name),sha256=sha(ROOT/'acceleration'/name)) for name in
                                                   ['theory_20261002_order8_psd_cuts.py','theory_20261002_order8_marked_extension_v4.py']],
                                     scope='Frozen order8 aggregate count relaxation and66/87flag PSDs at n3=4158.',
                                     verification='Producer exact replay only; separate implementation must approve raw counts and decomposition.',
                                     numerical_settings=None,numerical_settings_reason='Only exact Python integers/Fraction arithmetic.',
                                     random_seed=None,random_seed_reason='Deterministic arithmetic.'))
    model=json.loads(gzip.decompress(args.model.read_bytes()))
    counts=json.loads(args.witness.read_text())['counts']
    assert min(counts)>=0
    assert len(counts)==len(model['variables'])
    assert all(sum(a*counts[j] for j,a in row['terms'])==row['rhs'] for row in model['equations'])
    positive=decompose([[2,1],[1,2]])
    negative=decompose([[1,2],[2,1]])
    zero=decompose([[0,0],[0,0]])
    assert positive['status']=='EXACT_PSD_CANDIDATE' and positive['rank']==2
    assert negative['status']=='NOT_PSD_NEGATIVE_PIVOT'
    assert zero['status']=='EXACT_PSD_CANDIDATE' and zero['rank']==0
    save(args.out/'producer_controls.json',dict(positive_2x2='PASS',indefinite_2x2='REJECTED',zero_matrix='PASS',independent=False))
    data=flag_data([tuple(x) for x in model['variables']])
    summary=[]
    for family,fd in data.items():
        matrix=exact_moment(fd,counts)
        certificate=decompose(matrix)
        save(args.out/f'{family}_matrix.json',dict(matrix=matrix,convention='Exact symmetric integer matrix M=sum_H count(H)*C_H'))
        save(args.out/f'{family}_certificate.json',certificate)
        result=dict(family=family,size=len(matrix),rank=certificate['rank'],status=certificate['status'])
        summary.append(result)
        print(json.dumps(result),flush=True)
    save(args.out/'summary.json',dict(status='COMPLETED_INDEPENDENT_VERIFICATION_PENDING',target_resolution='UNKNOWN',
                                     exact_new_bound=None,results=summary,exact_count_rows=len(model['equations']),
                                     claim='One explicit integer aggregate count vector satisfies the frozen4543 marked extension equations and two complete archived pair-root order8 PSD matrices at n3=4158.',
                                     limitations=['Conditional on exact model/coefficient conventions and complete class premise.',
                                                  'No consistent placement on99vertices or target graph follows.'],
                                     elapsed_seconds=time.monotonic()-start,
                                     outputs=[dict(path=p.name,sha256=sha(p)) for p in sorted(args.out.iterdir()) if p.is_file()]))


if __name__=='__main__':
    main()
