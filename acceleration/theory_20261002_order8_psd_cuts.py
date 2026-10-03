"""Discovery: exact integer rank-one flag cuts guided by floating eigenvectors.

The coefficient layer is inherited from archived Wave147; independent complete
coefficient/cut checking is required. No floating LP or spectrum is a proof.
"""
from collections import Counter
from datetime import datetime, timezone
import argparse
import gzip
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
import time

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix, vstack, csr_matrix

from theory_20261002_order8_marked_extension_v4 import ROOT, LEGACY, canonical, sha, save

COEFFICIENTS = LEGACY / 'attempts/wave147-alternative-lane/coefficients.json.gz'


def flag_data(keys):
    raw = json.loads(gzip.decompress(COEFFICIENTS.read_bytes()))
    index = {key:i for i,key in enumerate(keys)}
    data = {}
    for name, item in raw['families'].items():
        records = []
        for rec in item['class_coefficients']:
            order = rec['order']
            mask = canonical(order, rec['canonical_mask'])[0]
            records.append((index[order,mask], rec['upper_entries']))
        data[name] = dict(size=item['matrix_size'], records=records)
    return data


def moment(data, counts):
    matrix = np.zeros((data['size'],data['size']))
    for j, entries in data['records']:
        for u,v,a in entries:
            matrix[u,v] += counts[j]*a
            if u != v:
                matrix[v,u] += counts[j]*a
    return matrix


def cut(data, vector, count):
    """Integer v^T C_H v, exact Python integers throughout."""
    result = [0]*count
    for j, entries in data['records']:
        result[j] = sum((1 if u==v else 2)*a*vector[u]*vector[v] for u,v,a in entries)
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--model',type=Path,required=True)
    p.add_argument('--primal',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--iterations',type=int,default=24)
    p.add_argument('--lp-seconds',type=float,default=30)
    args=p.parse_args()
    args.out.mkdir(parents=True,exist_ok=False)
    start=time.monotonic()
    model=json.loads(gzip.decompress(args.model.read_bytes()))
    keys=[tuple(x) for x in model['variables']]
    scale=[math.comb(99,h) for h,_ in keys]
    input_primal=json.loads(args.primal.read_text())
    rounded=[int(round(x)) for x in input_primal['counts']]
    residual=[sum(rounded[j]*a for j,a in row['terms'])-row['rhs'] for row in model['equations']]
    rounding=dict(nonnegative=min(rounded)>=0, failed_rows=sum(r!=0 for r in residual),
                  largest_absolute_residual=max(abs(r) for r in residual),
                  max_count_rounding_error=max(abs(a-b) for a,b in zip(rounded,input_primal['counts'])),
                  status='CANDIDATE_EXACT_NULL_WITNESS' if not any(residual) and min(rounded)>=0 else 'ROUNDING_NOT_EXACT',
                  independent=False)
    save(args.out/'rounding_control.json',rounding)
    if rounding['status']=='CANDIDATE_EXACT_NULL_WITNESS':
        save(args.out/'integer_null_witness.json',dict(model_sha256=sha(args.model),counts=rounded,
                                                       statement='Exact nonnegative integer aggregate count vector satisfies all4543 frozen marked-extension equations at n3=4158; no graph follows.',
                                                       status='CANDIDATE_PENDING_INDEPENDENT_CHECK'))
    fd=flag_data(keys)
    rr,cc,vv,bb=[],[],[],[]
    for i,row in enumerate(model['equations']):
        denominator=max([abs(a*scale[j]) for j,a in row['terms']]+[abs(row['rhs']),1])
        for j,a in row['terms']:
            rr.append(i);cc.append(j);vv.append(a*scale[j]/denominator)
        bb.append(row['rhs']/denominator)
    equalities=coo_matrix((vv,(rr,cc)),shape=(len(bb),len(keys))).tocsr()
    n3=next(j for j,(n,m) in enumerate(keys) if n==6 and rows_n3(m))
    objective=np.zeros(len(keys));objective[n3]=-scale[n3]
    manifest=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                  command=[sys.executable,*sys.argv],cwd=str(ROOT),source_sha256=sha(Path(__file__)),
                  inputs=[dict(path=str(f),sha256=sha(f)) for f in [args.model,args.primal,COEFFICIENTS]],
                  inherited_helper=dict(path='acceleration/theory_20261002_order8_marked_extension_v4.py',sha256=sha(ROOT/'acceleration/theory_20261002_order8_marked_extension_v4.py')),
                  versions=dict(python=platform.python_version(),numpy=np.__version__),
                  scope='Unrestricted necessary aggregate counts with selected rational rank-one PSD cuts; no graph.',
                  acceptance='Rational directions and integer coefficient cuts are exact candidates; spectra and LP objectives only guide selection.',
                  stopping='At most stated iterations; LP timeout per iteration; hard outer supervisor deadline; save every cut.',
                  independent_verification='Separate implementation must check all coefficient identities and rank-one cuts before promotion.',
                  random_seed=None,random_seed_reason='Deterministic eigendirection and rounding, no randomized operation.')
    save(args.out/'manifest.json',manifest)
    inequalities=[];cutrecords=[];traces=[]
    densities=np.array(input_primal['densities'])
    for iteration in range(args.iterations):
        counts=densities*np.array(scale)
        diagnostics={};added=0
        for name,data in fd.items():
            matrix=moment(data,counts)
            norm=max(1.0,float(np.max(np.abs(matrix))))
            values,vectors=np.linalg.eigh(matrix/norm)
            diagnostics[name]=dict(minimum_scaled_eigenvalue=float(values[0]),moment_normalizer=norm)
            if values[0] < -1e-8:
                vec=[int(x) for x in np.rint(vectors[:,0]*10000)]
                coefficients=cut(data,vec,len(keys))
                value=sum(a*b for a,b in zip(coefficients,counts))
                if value>=0:
                    continue
                denominator=max(abs(a*scale[j]) for j,a in enumerate(coefficients))
                inequalities.append(csr_matrix([[-a*scale[j]/denominator for j,a in enumerate(coefficients)]]))
                record=dict(iteration=iteration,family=name,vector=vec,terms=[[j,a] for j,a in enumerate(coefficients) if a],
                            direction='sum coefficient[j]*count[j] >=0',
                            status='CANDIDATE_EXACT_RANK_ONE_CUT',independent_check=False)
                cutrecords.append(record)
                save(args.out/f'cut_{len(cutrecords):04d}.json',record)
                added+=1
        row=dict(iteration=iteration,n3_approximate=float(counts[n3]),moments=diagnostics,cuts_added=added,total_cuts=len(cutrecords),certificate_status='NUMERICAL_DIAGNOSTIC')
        traces.append(row);save(args.out/f'iteration_{iteration:03d}.json',row)
        print(json.dumps(row),flush=True)
        if not added:
            break
        result=linprog(objective,A_eq=equalities,b_eq=bb,A_ub=vstack(inequalities),b_ub=np.zeros(len(inequalities)),bounds=(0,None),method='highs',
                       options=dict(time_limit=args.lp_seconds,primal_feasibility_tolerance=1e-9,dual_feasibility_tolerance=1e-9))
        save(args.out/f'lp_{iteration:03d}.json',dict(status=int(result.status),message=result.message,
                                                   counts=None if result.x is None else [float(x*scale[j]) for j,x in enumerate(result.x)],
                                                   no_exact_bound=True))
        if not result.success:
            break
        densities=result.x
    save(args.out/'summary.json',dict(status='COMPLETED_INDEPENDENT_VERIFICATION_PENDING',target_resolution='UNKNOWN',
                                     exact_new_bound=None,cut_count=len(cutrecords),rounding=rounding,iterations=traces,
                                     elapsed_seconds=time.monotonic()-start,
                                     outputs=[dict(path=f.name,sha256=sha(f)) for f in sorted(args.out.iterdir()) if f.is_file()]))


def rows_n3(mask):
    # Degree multiset distinguishes the two-cross-edge graph in this locally
    # admissible six-class stream; explicitly compare its canonical edge mask.
    from theory_20261002_order8_marked_extension_v4 import positions
    desired=sum(1<<positions(6)[tuple(sorted(e))] for e in [(0,1),(1,2),(0,2),(3,4),(4,5),(3,5),(0,3),(1,4)])
    return mask==canonical(6,desired)[0]


if __name__=='__main__':
    main()
