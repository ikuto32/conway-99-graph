"""Exact F2 affine-span pilot on hash-bound complete two-coordinate stars."""
import argparse
from bisect import bisect_right
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

D=Path('acceleration/results/20260917_two_matching_moments')
DOMAIN_AUDIT=Path('acceleration/results/20260917_independent_review/two_matchings/summary.json')
MODEL_AUDIT=Path('acceleration/results/20260917_independent_review/two_matching_moments.json')
PROTOCOL=Path('docs/NEXT_20260917_TWO_COORDINATE_BINARY_SPAN.md')
PINS={DOMAIN_AUDIT:'f3d2ba90be5e8c27bc64c2e4941174d36fc3ddfcbc29ce25da872df652383acb',
      MODEL_AUDIT:'5af1f353a70a16fc5f915195b911d782e360ffc0690463936b7a9dea983197ed'}


def digest(path): return sha256(Path(path).read_bytes()).hexdigest()
def read(path): return json.loads(Path(path).read_bytes())
def stamp(): return datetime.now(timezone.utc).isoformat()
def save(path,value):
    with Path(path).open('x',encoding='utf-8') as f:
        json.dump(value,f,separators=(',',':'));f.write('\n')


def reduce_vector(vector,combination,basis):
    while vector:
        pivot=vector.bit_length()-1
        if pivot not in basis: break
        row,provenance=basis[pivot]
        vector^=row;combination^=provenance
    return vector,combination


def separator(remainder,basis):
    assert remainder and remainder.bit_length()-1 not in basis
    w=1 << (remainder.bit_length()-1)
    for p,(row,_) in sorted(basis.items()):
        if (row&w).bit_count()%2: w^=1 << p
    assert all((row&w).bit_count()%2==0 for row,_ in basis.values())
    assert (remainder&w).bit_count()%2==1
    return w


def toy(columns,target):
    basis={}
    for j,column in enumerate(columns):
        v,c=reduce_vector(column,1<<j,basis)
        if v: basis[v.bit_length()-1]=(v,c)
    r,c=reduce_vector(target,0,basis)
    return basis,r,c


def controls():
    # Integer scalar columns0,2 both become zero; target1 is not in their F2 affine span.
    b,r,c=toy([0%2,2%2],1)
    assert r and separator(r,b)==1
    # Rational convex mixture(1/2,1/2) reaches1 over Q despite parity rejection.
    from fractions import Fraction
    assert Fraction(1,2)*0+Fraction(1,2)*2==1
    cases=0
    for columns in ([1,2],[3,5,6],[0,2,4],[7,7,1]):
        attainable={0}
        for x in columns: attainable|={v^x for v in list(attainable)}
        for target in range(8):
            b,r,c=toy(columns,target)
            assert (r==0)==(target in attainable)
            if r:
                w=separator(r,b)
                assert all((w&x).bit_count()%2==0 for x in columns)
                assert (w&target).bit_count()%2==1
                assert (0&target).bit_count()%2!=1  # corrupted zero separator
            else:
                value=0
                for j,x in enumerate(columns):
                    if c>>j&1:value^=x
                assert value==target
                assert (value^1)!=target  # corrupted target witness
            cases+=1
    return dict(status='PRODUCER_BINARY_SPAN_CONTROLS_PASS',scalar_LP_feasible_parity_infeasible=True,
                exhaustive_targets_checked=cases,positive_membership_witnesses_checked=True,
                negative_separators_checked=True,corrupt_zero_separator_and_target_rejected=True,
                independent_verification=False)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--resume',type=Path)
    args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    assert all(digest(p)==h for p,h in PINS.items())
    da,ma=read(DOMAIN_AUDIT),read(MODEL_AUDIT)
    assert da['status']=='INDEPENDENT_TWO_COORDINATE_DOMAINS_PASS'
    assert ma['status']=='INDEPENDENT_TWO_COORDINATE_FULL_MOMENT_MODEL_PASS'
    paths=[*PINS,D/'model.json',D/'integer_augmented_csr.npz',Path(__file__),PROTOCOL,Path('uv.lock')]
    for name,h in ma['inputs_sha256'].items():
        if '/20260917_partial_two_matchings/' in name:
            assert digest(name)==h;paths.append(Path(name))
    for p in (D/'model.json',D/'integer_augmented_csr.npz'):
        assert digest(p)==ma['inputs_sha256'][p.as_posix()]
    hashes={p.as_posix():digest(p) for p in dict.fromkeys(paths)}
    meta=read(D/'model.json');offsets=meta['probability_offsets'];n=offsets[-1]
    assert n==89308 and len(offsets)==85 and meta['shape']==[5370,96280]
    save(args.out/'manifest.json',dict(timestamp=stamp(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        command=[sys.executable,*sys.argv],cwd=str(Path.cwd()),python=platform.python_version(),inputs_sha256=hashes,
        question='Does the target residual belong to the F2 span of complete center-star column differences?',
        population='All89308 original probabilities grouped in84 independently complete two-coordinate domains; all5370 equalityrows; no residualslacks.',
        selection='Ascending original globalprobabilitycolumn, reference firstoriginalID percenter, cold basis unless explicitly resumed.',
        criterion='Early membership only with exact coefficient witness; outside-span only afterallcolumns processed and exactannihilator verified.',
        seconds=30,timed_region='Reference and column parity construction plus elimination; excludes inputhashing, matrixI/O, controls and checkpointserialization.',
        initialization='Empty GF2 basis' if not args.resume else 'Hash-bound explicit resume',seed=None,seed_reason='Deterministic',
        scope=ma['scope'],resume_path=str(args.resume) if args.resume else None,resume_sha256=digest(args.resume) if args.resume else None,
        target_resolution=False))
    save(args.out/'controls.json',controls())
    import numpy as np
    import scipy
    from scipy.sparse import load_npz
    matrix=load_npz(D/'integer_augmented_csr.npz')[:,:n].tocsc()
    matrix.sum_duplicates();matrix.sort_indices()
    assert matrix.dtype.kind in 'iu'
    started=time.monotonic()
    def column(j):
        value=0
        for k in range(matrix.indptr[j],matrix.indptr[j+1]):
            if int(matrix.data[k])%2:value^=1<<int(matrix.indices[k])
        return value
    refs=[column(offsets[u]) for u in range(84)]
    target=sum(1<<i for i,v in enumerate(meta['rhs']) if int(v)%2)
    for reference in refs:target^=reference
    basis={};remainder=target;combination=0;next_column=0
    if args.resume:
        old=read(args.resume)
        assert old['inputs_sha256']==hashes and old['status']=='INCOMPLETE_TIME_CAP'
        assert int(old['target_hex'],16)==target
        basis={r['pivot']:(int(r['vector_hex'],16),int(r['coefficient_hex'],16)) for r in old['basis']}
        remainder=int(old['remainder_hex'],16);combination=int(old['combination_hex'],16)
        next_column=old['next_column']
    initial_rank=len(basis);initial_column=next_column
    while next_column<n and remainder:
        if time.monotonic()-started>=30:break
        j=next_column;u=bisect_right(offsets,j)-1
        vector=column(j)^refs[u]
        v,c=reduce_vector(vector,1<<j,basis)
        if v:
            basis[v.bit_length()-1]=(v,c)
            remainder,combination=reduce_vector(remainder,combination,basis)
        next_column+=1
    if not remainder: status='CANDIDATE_EXACT_SPAN_MEMBERSHIP'
    elif next_column==n:status='CANDIDATE_MODULAR_EXCLUSION'
    else:status='INCOMPLETE_TIME_CAP'
    elapsed=time.monotonic()-started
    cert=None
    if not remainder:
        selected=[j for j in range(n) if combination>>j&1]
        actual=0
        for j in selected:actual^=column(j)^refs[bisect_right(offsets,j)-1]
        assert actual==target
        cert=dict(kind='AFFINE_DIFFERENCE_MEMBERSHIP',selected_global_columns=selected,
                  selected_original_ids=[dict(center=bisect_right(offsets,j)-1,original_id=j-offsets[bisect_right(offsets,j)-1]) for j in selected],
                  target_hex=hex(target),reference_global_columns=offsets[:-1],
                  meaning='Necessary linearparity screen survives; not a graph, exactLP point, or productdomain solution.')
    elif next_column==n:
        w=separator(remainder,basis)
        assert (w&target).bit_count()%2==1
        assert all((w&(column(j)^refs[bisect_right(offsets,j)-1])).bit_count()%2==0 for j in range(n))
        cert=dict(kind='AFFINE_DIFFERENCE_SEPARATOR',row_multiplier_hex=hex(w),
                  row_indices=[i for i in range(5370) if w>>i&1],target_dot=1,
                  annihilated_differences=n,reference_global_columns=offsets[:-1],
                  meaning='Conditional family exclusion candidate, subject to independent raw-neighborhood replay.')
    if cert:save(args.out/'certificate.json',cert)
    checkpoint=dict(status=status,inputs_sha256=hashes,next_column=next_column,
        target_hex=hex(target),remainder_hex=hex(remainder),combination_hex=hex(combination),
        basis=[dict(pivot=p,vector_hex=hex(v),coefficient_hex=hex(c)) for p,(v,c) in sorted(basis.items())])
    save(args.out/'checkpoint.json',checkpoint)
    summary=dict(timestamp=stamp(),status=status,scope=ma['scope'],total_original_choices=n,
        initial_processed_columns=initial_column,processed_columns=next_column,new_columns_processed=next_column-initial_column,
        full_population_processed=next_column==n,basis_rank=len(basis),initial_basis_rank=initial_rank,
        screening_seconds=elapsed,certificate_path=str(args.out/'certificate.json') if cert else None,
        certificate_null_reason=None if cert else 'Time cap before complete span or membershipwitness',
        numpy=np.__version__,scipy=scipy.__version__,inputs_sha256=hashes,
        artifacts_sha256={str(p):digest(p) for p in args.out.glob('*.json')},
        claim_status='CANDIDATE',independent_review='PENDING',target_resolution=False)
    save(args.out/'summary.json',summary)
    print(json.dumps({k:v for k,v in summary.items() if k not in ('inputs_sha256','artifacts_sha256')}))


if __name__=='__main__':main()
