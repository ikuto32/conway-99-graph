"""Gated exact integer moment model for all eight-coordinate matching survivors."""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
from importlib.metadata import version
from itertools import combinations
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
import numpy as np
from scipy.sparse import save_npz
from tqdm import tqdm
import theory_20260917_six_filtered_moments as builder

ROOT=Path(__file__).resolve().parents[1]
DOMAIN=Path('acceleration/results/20260930_eight_domains/run01')
FILTER=Path('acceleration/results/20260930_eight_matching_filter/run01')
GATE=Path('acceleration/results/20260930_independent_review/eight_domains_claim_binding.json')
PROTOCOL=Path('docs/NEXT_20260930_EIGHT_MOMENT_BUILD.md')


def digest(p):return sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):
    with p.open('x',encoding='utf-8') as f:json.dump(x,f,indent=2);f.write('\n')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--filter-audit',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();bindings={}
    def read(p):
        bindings[p.as_posix()]=digest(p)
        return json.loads(p.read_bytes())
    gate=read(GATE);filtgate=read(args.filter_audit)
    assert gate['status']=='INDEPENDENT_EIGHT_COORDINATE_ALL84_BINDING_PASS'
    assert filtgate['status']=='INDEPENDENT_EIGHT_COORDINATE_NEIGHBORHOOD_MATCHING_FILTER_PASS'
    for audit in (gate,filtgate):
        for name,h in audit['inputs_sha256'].items():assert digest(ROOT/name)==h,name
    summary=read(DOMAIN/'summary.json');domain=read(DOMAIN/'manifest.json');filtering=read(FILTER/'summary.json')
    assert summary['complete_all_centers'] and summary['complete_domain_choices']==2290122
    assert filtgate['inputs_sha256'][(FILTER/'summary.json').as_posix()]==digest(FILTER/'summary.json')
    assert filtering['original_choices']==2290122 and filtering['empty_domains']==0
    tables=[];ids_by_center=[];original_counts=[]
    for u in tqdm(range(84),desc='Bind complete eight-coordinate survivors',unit='center'):
        p=DOMAIN/f'domain_{u:02d}.json';record=read(p)
        assert digest(p)==gate['records'][u]['raw_sha256']
        fpath=Path(filtering['vertices'][u]['path']);raw=read(fpath)
        assert digest(fpath)==filtering['vertices'][u]['sha256']==filtgate['records'][u]['raw_sha256']
        masks=[int(m,16) for m in record['domain_masks_hex']];ids=raw['surviving_ids'];rejected=raw['rejected_ids']
        assert ids==sorted(set(ids)) and rejected==filtgate['records'][u]['rejected_ids']
        assert sorted(ids+rejected)==list(range(len(masks)))
        tables.append([masks[i] for i in ids]);ids_by_center.append(ids);original_counts.append(len(masks))
    n=sum(map(len,tables));assert n==filtering['surviving_choices']
    for p in (Path(__file__),Path(builder.__file__),Path('acceleration/theory_20260917_partial_matching_moments.py'),Path('uv.lock'),PROTOCOL):bindings[p.as_posix()]=digest(p)
    args.out.mkdir(parents=True,exist_ok=False)
    save(args.out/'build_manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        command_argv=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),versions={x:version(x) for x in ('numpy','scipy','tqdm')},inputs_sha256=bindings,
        model='PARTIAL_K_EIGHT_COORDINATE_MATCHING_FILTERED_FULL_MOMENT_PHASE1_V1',scope=domain['scope'],
        selection='Every independently retained original domain ID; no further pruning.',build_seconds_cap=900,
        criterion='Exact integer model, independently rederived all columns/RHS, no numerical solve before separate model audit.',
        numerical_settings='int8 coefficients +/-1; int32 sparse indices; exact integer RHS. No floating-point values.',
        resource_projection='CSC+CSR typed arrays projected and recorded before allocation; additional Python overhead. Abort above2^31nonzeros in frozen builder.',
        shared_components='Frozen six-coordinate direct-column producer assembler and its rook9 calibration; independent checker is separate.',
        random_seed=None,random_seed_null_reason='Deterministic complete model construction.',solver_configuration=None,solver_configuration_null_reason='Build only; no solver launched.',target_resolution=False))
    start=time.monotonic();deadline=start+900
    save(args.out/'controls.json',builder.calibrate(deadline))
    supports=[{2*a+s,2*b+t} for a,b in combinations(range(7),2) for s in (0,1) for t in (0,1)]
    fixed=set(map(tuple,domain['remaining_fixed_K_edges_outer']));unknown=list(map(tuple,domain['unknown_edges_outer']))
    assert len(fixed)==120 and len(unknown)==2160
    A,rhs,offsets,pairs,projection=builder.assemble(supports,fixed,unknown,tables,deadline,args.out)
    assert time.monotonic()<deadline
    save_npz(args.out/'integer_augmented_csr.npz',A,compressed=True)
    model=dict(model='PARTIAL_K_EIGHT_COORDINATE_MATCHING_FILTERED_FULL_MOMENT_PHASE1_V1',shape=list(A.shape),nonzeros=A.nnz,matrix_sha256=digest(args.out/'integer_augmented_csr.npz'),
        coefficient_dtype=str(A.data.dtype),probability_offsets=offsets,retained_original_domain_ids=ids_by_center,
        original_probability_offsets=np.cumsum([0]+original_counts).tolist(),fixed_edges=sorted(fixed),unknown_edges=unknown,pair_order=pairs,supports=[sorted(s) for s in supports],
        rhs=rhs,costs=[0]*n+[1]*(2*len(pairs)),column_lower=0,column_upper=None,column_upper_null_reason='Positive infinity',all_rows_equalities=True,
        row_order='84 simplex,2160 reciprocity,3486 moments',column_order=f'{n} retained original stars then3486negative and3486positive slacks')
    save(args.out/'model.json',model)
    chunks=[]
    for p in (args.out/'integer_augmented_csr.npz',args.out/'model.json'):
        if p.stat().st_size<=10*1024**2:continue
        parts=[]
        with p.open('rb') as source:
            i=0
            while data:=source.read(8*1024**2):
                part=p.with_name(p.name+f'.part{i:03d}')
                with part.open('xb') as f:f.write(data)
                parts.append(dict(path=part.name,bytes=len(data),sha256=digest(part)));i+=1
        chunks.append(dict(source=p.name,source_bytes=p.stat().st_size,source_sha256=digest(p),source_availability='LOCAL_ONLY',parts=parts))
    save(args.out/'chunk_manifest.json',dict(schema_version=1,chunk_bytes=8*1024**2,artifacts=chunks,recovery='Verify eachpart, concatenate listedorder into freshfile, verify sourcebytes/hash'))
    assert all(digest(p)==h for p,h in bindings.items())
    result=dict(timestamp=datetime.now(timezone.utc).isoformat(),status='CANDIDATE_EIGHT_COORDINATE_FILTERED_MOMENT_BUILD',model=model['model'],
        shape=list(A.shape),nonzeros=A.nnz,original_choices=2290122,retained_choices=n,removed_choices=2290122-n,elapsed_seconds=time.monotonic()-start,
        output_sha256={p.name:digest(p) for p in args.out.iterdir() if p.is_file()},solver_launched=False,independent_model_review_pending=True,target_resolution=False)
    save(args.out/'build_summary.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='output_sha256'}))


if __name__=='__main__':main()
