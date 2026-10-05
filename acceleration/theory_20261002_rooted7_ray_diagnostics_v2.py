"""Exact diagnostics for preserved numerical root7 rays; no promotion."""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import time
import sys
import numpy as np
from scipy.sparse import coo_matrix
from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
B=ROOT/'acceleration/results'


def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def save(path,value):
    with path.open('x',encoding='utf8',newline='\n') as stream:json.dump(value,stream,indent=2);stream.write('\n')


def main():
    # Frozen bounded diagnostics can have large exact Fraction denominator
    # inventories; v1 computation finished but JSON conversion hit4300digits.
    # Preservev1 output/failure and permit this explicitly bounded new output.
    sys.set_int_max_str_digits(0)
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True);parser.add_argument('--seconds',type=float,required=True)
    args=parser.parse_args();deadline=CommandDeadline(args.seconds,allocation_reason='Threepreservednumericalrays exactresidualdiagnostics, noLP orproofclaim.')
    args.out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    modelpath=B/'20261002_rooted7_extension_model/model.json';model=json.loads(modelpath.read_bytes());rows=model['equations'];columns=len(model['variables'])
    rr,cc,vv=[],[],[]
    for i,row in enumerate(rows):
        for j,coef in row['terms']:rr.append(i);cc.append(j);vv.append(coef)
    matrix=coo_matrix((vv,(rr,cc)),shape=(len(rows),columns)).tocsr();results=[]
    for point in [(0,0),(20,0),(20,9)]:
        path=B/f'20261002_rooted7_corner_certificates/corner_{point[0]}_{point[1]}.json';data=json.loads(path.read_bytes());ray=data['numerical_ray']
        magnitude=max(abs(value) for value in ray);numeric=np.asarray(ray)/magnitude
        raw_products=matrix.transpose()@numeric
        report=dict(parameters=list(point),raw_sha256=sha(path),nonzero_support=sum(value!=0 for value in ray),
            floating_min_column=float(np.min(raw_products)),floating_max_column=float(np.max(raw_products)),
            floating_near_zero_columns=int(np.sum(abs(raw_products)<1e-7)),lifts=[])
        for denominator in [1,10,1000,1000000]:
            weights=[Fraction(float(value)).limit_denominator(denominator) for value in numeric]
            products=[Fraction(0)]*columns;rhs=[Fraction(0)]*3
            for i,weight in enumerate(weights):
                if weight:
                    for j,coef in rows[i]['terms']:products[j]+=weight*coef
                    for j,coef in enumerate(rows[i]['rhs_affine']):rhs[j]+=weight*coef
            negative=[j for j,value in enumerate(products) if value<0];positive=[j for j,value in enumerate(products) if value>0]
            report['lifts'].append(dict(max_denominator=denominator,negative_columns=len(negative),positive_columns=len(positive),
                exact_min=[min(products).numerator,min(products).denominator],exact_max=[max(products).numerator,max(products).denominator],
                negative_samples=[[j,products[j].numerator,products[j].denominator] for j in negative[:10]],
                rhs_affine=[[value.numerator,value.denominator] for value in rhs]))
            if deadline.status()['stop_required']:raise ValueError('not completed within the allocated budget')
        results.append(report)
    save(args.out/'summary.json',dict(status='NUMERICAL_RAY_EXACT_DIAGNOSTICS_ONLY',model_sha256=sha(modelpath),results=results,
        target_resolution='UNKNOWN',new_exclusions=0,elapsed_seconds=time.monotonic()-start))
    print(json.dumps([dict(parameters=row['parameters'],nonzero_support=row['nonzero_support'],
        floating_min_column=row['floating_min_column'],floating_max_column=row['floating_max_column'],
        lift_negative_columns=[lift['negative_columns'] for lift in row['lifts']],
        lift_positive_columns=[lift['positive_columns'] for lift in row['lifts']]) for row in results]),flush=True)


if __name__=='__main__':main()
