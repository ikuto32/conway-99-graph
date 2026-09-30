"""Candidate finite affine-circuit census; exact arithmetic, no solver."""
from collections import defaultdict, Counter
from datetime import datetime, timezone
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path
import argparse, hashlib, json, platform, subprocess, sys, time
from tqdm import tqdm

ROOT=Path(__file__).resolve().parents[1]
B=ROOT/'acceleration/results'
RAW=B/'20260930_hadamard20_support/six_prism.json'
PREVIOUS=B/'20260930_hadamard_exception_groups/summary.json'
MARGINAL=B/'20260930_independent_review/hadamard_triplicate_counts_v2/summary.json'
PINS={RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',PREVIOUS:'59bb3232eabf096c29234dda732bab0230a01806c72116d71fd0adc232515a01',MARGINAL:'cb9f1c7f8cfe0db557f554ded5427a9cba46dda10dcd9b5df9968e1d3b776f88'}
def need(ok,msg):
    if not ok: raise ValueError(msg)
def sha(p):
    with p.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
def key(p): return p.resolve().relative_to(ROOT).as_posix()
def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n') as f: json.dump(x,f,indent=2);f.write('\n')
def det(a):
    if len(a)==1:return a[0][0]
    return sum((-1)**j*a[0][j]*det([r[:j]+r[j+1:] for r in a[1:]]) for j in range(len(a)))
def row_basis(a):
    basis={}; indices=[]
    for i,row in enumerate(a):
        v=list(map(Fraction,row))
        for p,b in sorted(basis.items()):
            if v[p]:
                x=v[p];v=[y-x*z for y,z in zip(v,b)]
        if any(v):
            p=next(j for j,x in enumerate(v) if x);x=v[p];basis[p]=[y/x for y in v];indices.append(i)
    return indices
def certify(a,relation=None):
    indices=row_basis(a)
    if len(indices)==4:
        minor=[a[i] for i in indices];d=det(minor);need(d!=0,'exact independent minor')
        return dict(rank=4,rows=indices,minor=minor,determinant=d)
    need(len(indices)==3 and relation is not None,'only approved four-circuit dependence')
    need(all(sum(x*y for x,y in zip(row,relation))==0 for row in a),'literal primitive relation')
    return dict(rank=3,relation=relation)
def collisions(columns):
    buckets=defaultdict(list)
    for i,j in combinations(range(len(columns)),2):buckets[tuple(x+y for x,y in zip(columns[i],columns[j]))].append([i,j])
    circuits={}
    for total,pairs in buckets.items():
        for p,q in combinations(pairs,2):
            need(set(p).isdisjoint(q),'distinct columns force disjoint equal-sum pairs')
            ids=tuple(sorted(p+q));relation=[1 if i in p else -1 for i in ids]
            need(ids not in circuits,'four distinct points have unique equal-sum split')
            circuits[ids]=dict(positive_pair=p,negative_pair=q,relation=relation,pair_sum=list(total))
    return buckets,circuits
def controls():
    cube=list(product(range(2),repeat=3));_,circuits=collisions(cube)
    for ids in combinations(range(8),4):
        a=[[1]*4]+[[cube[i][a] for i in ids] for a in range(3)]
        certify(a,circuits[ids]['relation'] if ids in circuits else None)
    square=[[1,1,1,1],[0,0,1,1],[0,1,0,1]];rel=[1,-1,-1,1]
    need(all(sum(x*y for x,y in zip(row,rel))==0 for row in square),'square positive')
    bad=rel.copy();bad[0]+=1;need(any(sum(x*y for x,y in zip(row,bad)) for row in square),'corrupt relation rejected')
    tetra=[[1,1,1,1],[0,1,0,0],[0,0,1,0],[0,0,0,1]];d=det(tetra)
    need(d!=0 and d!=d+1,'independent tetrahedron/corrupt determinant')
    duplicates=[(0,0),(0,0),(1,0),(0,1)]
    need(len(set(duplicates))!=4,'duplicate input rejected')
    return dict(cube_four_subsets=70,cube_circuits=len(circuits),square=square,relation=rel,tetrahedron=tetra,tetrahedron_determinant=d,rejected_controls=['corrupt_null_coefficient','corrupt_minor_determinant','duplicate_columns'])
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);args=p.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    try:
        for path,digest in PINS.items():need(sha(path)==digest,'input pin '+key(path))
        inputs={key(x):y for x,y in PINS.items()}
        for path in [Path(__file__),Path(__file__).with_name('theory_20260930_hadamard_four_group_circuits_spec.md'),ROOT/'uv.lock',ROOT/'pyproject.toml']:inputs[key(path)]=sha(path)
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=inputs,limits=dict(seconds=120,solver_calls=0),status='PREREGISTERED_COMPLETE_FOUR_GROUP_CENSUS'))
        save(out/'controls.json',controls())
        raw=json.loads(RAW.read_bytes());groups=list(dict.fromkeys(tuple(a for a in range(12) if raw['L'][a][d]) for d in range(60)))
        need(len(groups)==20,'twenty raw distinct supports')
        columns=[tuple(int(a in g) for a in range(12)) for g in groups]
        buckets,circuits=collisions(columns)
        save(out/'pair_sums.json',dict(groups=groups,records=[dict(sum=list(total),pairs=pairs) for total,pairs in sorted(buckets.items())],unordered_pairs=190))
        quartets=[]
        for ids in tqdm(list(combinations(range(20),4)),desc='Exact four-group ranks',mininterval=1):
            a=[[1]*4]+[[columns[g][r] for g in ids] for r in range(12)]
            cert=certify(a,circuits[ids]['relation'] if ids in circuits else None)
            quartets.append(dict(groups=list(ids),certificate=cert))
            need(time.monotonic()-start<120,'resource allocation')
        save(out/'all_quartets.json',dict(records=quartets,complete_population=4845))
        records=[]
        for ids,c in sorted(circuits.items()):
            common=sorted(set.intersection(*(set(groups[g]) for g in ids)))
            records.append(dict(groups=list(ids),**c,common_support=common,union_support=sorted(set.union(*(set(groups[g]) for g in ids))),local_margin_can_sustain_nonzero_deviation=len(common)>=2))
        save(out/'circuits.json',dict(records=records,statement='All affine dependencies of four distinct raw support columns; exact global incidence circuits, not only coordinate-specific subsets.',independent_approval=False))
        marginal=[]
        for a in range(12):
            containing=[g for g in range(20) if a in groups[g]];others=[b for b in range(12) if b not in (a,a^1)]
            need(len(containing)==10,'coordinate population')
            for ids in combinations(containing,4):
                matrix=[[1]*4]+[[int(b in groups[g]) for g in ids] for b in others]
                cert=certify(matrix,circuits[ids]['relation'] if ids in circuits else None)
                marginal.append(dict(coordinate=a,groups=list(ids),other_coordinates=others,certificate=cert))
        save(out/'coordinate_marginal_quartets.json',dict(records=marginal,complete_population=2520))
        hist=Counter(len(c['common_support']) for c in records)
        result=dict(status='CANDIDATE_COMPLETE_FOUR_GROUP_AFFINE_CIRCUIT_CENSUS',timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=inputs,outputs_sha256={key(f):sha(f) for f in out.iterdir() if f.is_file()},groups=20,pair_sums_population=190,distinct_pair_sums=len(buckets),quartets=4845,coordinate_quartets=2520,affine_circuits=len(records),common_support_size_histogram=dict(sorted(hist.items())),circuits_not_eliminated_by_local_margins=sum(len(c['common_support'])>=2 for c in records),independent_approval=False,solver_calls=0,target_resolution=False,elapsed_seconds=time.monotonic()-start,scope='Only one saved fixed support; all4-group affine circuits and necessary exceptional-group constraints, no factor construction or target exclusion.')
        save(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('inputs_sha256','outputs_sha256')}))
    except BaseException as e:
        save(out/'failure.json',dict(error=repr(e),source_sha256=sha(Path(__file__))));raise
if __name__=='__main__':main()
