"""Candidate29vertex partial-family extension screen; not an independent audit."""
import os
for option in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[option]='1'
import argparse
from datetime import datetime,timezone
from hashlib import sha256
from itertools import combinations,product
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

import numpy as np
from tqdm import tqdm

ROOT=Path(__file__).resolve().parents[1]


def need(condition,message):
    if not condition:raise ValueError(message)
def digest(path):
    value=sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1<<20),b''):value.update(block)
    return value.hexdigest()
def key(path):return Path(path).resolve().relative_to(ROOT).as_posix()
def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8') as stream:json.dump(value,stream,indent=2);stream.write('\n')
def matrix(rows):return [[int(row>>j&1) for j in range(len(rows))] for row in rows]
def row_bits(A):return [sum(int(x)<<j for j,x in enumerate(row)) for row in A]


def cap_failure(rows):
    for i,j in combinations(range(len(rows)),2):
        common=(rows[i]&rows[j]).bit_count();cap=2-int(rows[i]>>j&1)
        if common>cap:return dict(pair=[i,j],common=common,cap=cap)
    return None


def extension_cap_failure(rows,neighbors):
    chosen=[i for i in range(len(rows)) if neighbors>>i&1]
    for i,j in combinations(chosen,2):
        common=(rows[i]&rows[j]).bit_count()+1;cap=2-int(rows[i]>>j&1)
        if common>cap:return dict(pair=[i,j],common=common,cap=cap)
    for i,row in enumerate(rows):
        common=(row&neighbors).bit_count();cap=2-int(neighbors>>i&1)
        if common>cap:return dict(pair=[i,len(rows)],common=common,cap=cap)
    return None


def grams(A):
    n=len(A)
    return [('27I-9A+J',[[27*int(i==j)-9*A[i][j]+1 for j in range(n)] for i in range(n)]),
            ('A+4I',[[A[i][j]+4*int(i==j) for j in range(n)] for i in range(n)])]


def screen(G):
    values,vectors=np.linalg.eigh(np.asarray(G,dtype=np.float64));minimum=float(values[0])
    result=dict(float64_minimum_eigenvalue=minimum,negative_signal=minimum < -1e-8,exact_negative=None)
    if result['negative_signal']:
        for scale in (1024,1048576,1073741824):
            z=[int(x) for x in np.rint(vectors[:,0]*scale)]
            q=sum(z[i]*G[i][j]*z[j] for i in range(len(z)) for j in range(len(z)))
            if q<0:result['exact_negative']=dict(vector=z,quadratic=q,rounding_scale=scale);break
    return result


def choices(required,optional,target):
    needed=target-len(required)
    if needed<0 or needed>len(optional):return []
    return [sorted(required+list(extra)) for extra in combinations(optional,needed)]


def controls():
    rook=[[int(i!=j and(i//3==j//3 or i%3==j%3)) for j in range(9)] for i in range(9)]
    need(cap_failure(row_bits(rook)) is None,'known rook caps')
    need(all(not screen(G)['negative_signal'] for name,G in grams(rook)),'known rook twoGram control')
    clique=[[int(i!=j) for j in range(5)] for i in range(5)]
    need(cap_failure(row_bits(clique)) is not None,'deliberate cap corruption')
    upper=screen(grams(clique)[0][1]);need(upper['exact_negative'] is not None,'known upperGram negative fixture')
    biclique=[[int((i<5)!=(j<5)) for j in range(10)] for i in range(10)]
    lower=screen(grams(biclique)[1][1]);need(lower['exact_negative'] is not None,'known lowerGram negative fixture')
    cases=0
    for required_mask in range(1<<6):
        required=[i for i in range(6) if required_mask>>i&1]
        optional=[i for i in range(6) if i not in required]
        for target in range(7):
            observed=choices(required,optional,target)
            expected=[list(i for i,bit in enumerate(bits) if bit) for bits in product((0,1),repeat=6) if sum(bits)==target and all(bits[i] for i in required)]
            need(sorted(observed)==sorted(expected),'complete forced-subset enumeration');cases+=1
    for neighbors in range(1<<9):
        old=row_bits(rook);extended=[row|((neighbors>>i&1)<<9) for i,row in enumerate(old)]+[neighbors]
        need(bool(extension_cap_failure(old,neighbors))==bool(cap_failure(extended)),'incremental/literal cap equivalence')
    return dict(status='PRODUCER_CALIBRATION_ONLY',known_rook_caps_and_twoGram_guidance_passed=True,cap_corruption_rejected=True,
                upper_exact_negative=upper,lower_exact_negative=lower,subset_fixture_cases=cases,incremental_cap_fixture_cases=512)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True);parser.add_argument('--resume',action='store_true');parser.add_argument('--seconds',type=float,default=120)
    args=parser.parse_args();args.out.mkdir(parents=True,exist_ok=args.resume)
    need(not(args.out/'summary.json').exists(),'completed run must not be overwritten')
    bindings={}
    def read(path,expected=None):
        observed=digest(path);need(expected is None or observed==expected,'input hash mismatch: '+str(path));bindings[key(path)]=observed
        return json.loads(Path(path).read_bytes())
    gate=read(ROOT/'acceleration/results/20260930_independent_review/local_redundancy_v2/closed_gram_lemma.json','463c7af9414d051290347b77b0aeca60da1bda958ec113405cc26a2ed5036f4b')
    filter_gate=read(ROOT/'acceleration/results/20260930_independent_review/eight_coordinate_matching_filter/summary.json','4fcd5fd7f02cd5362bda1f8f0a1c8e4669ce036bde56a04dcd1b6a3391b262f4')
    primary_path=ROOT/'acceleration/results/20260930_eight_domains/run01/manifest.json'
    primary=read(primary_path,filter_gate['inputs_sha256'][key(primary_path)])
    baseline=read(ROOT/'acceleration/results/20260916_star_guided_round2/search/probes/selection_03_index_18481_candidate.json')
    labels=[(2*a+s,2*b+t) for a,b in combinations(range(7),2) for s in range(2) for t in range(2)]
    support=[{a//2,b//2} for a,b in labels]
    freed={edge for edge in combinations(range(84),2) if len(support[edge[0]]&support[edge[1]])==1 and any(s<8 and s in labels[edge[1]] for s in labels[edge[0]])}
    fixed=set(map(tuple,baseline['overlap_edges_outer_zero_based']))-freed
    unknown=freed|{edge for edge in combinations(range(84),2) if support[edge[0]].isdisjoint(support[edge[1]])}
    need(len(fixed)==120 and len(unknown)==2160 and primary['remaining_fixed_K_edges_outer']==list(map(list,sorted(fixed)))
         and primary['unknown_edges_outer']==list(map(list,sorted(unknown))),'authenticated actual family fixed/free partition')
    def outer_state(a,b):
        pair=tuple(sorted((a-15,b-15)))
        return 1 if pair in fixed else -1 if pair in unknown else 0
    cases=[]
    for center in range(8):
        path=ROOT/f'acceleration/results/20260930_closed28_sos/center_{center:02d}.json'
        raw=read(path,gate['inputs_sha256'][key(path)])
        domain_path=ROOT/f'acceleration/results/20260930_eight_domains/run01/domain_{center:02d}.json'
        domain=read(domain_path,filter_gate['inputs_sha256'][key(domain_path)])
        for case in raw['cases'][:4]:
            need(case['star_mask']==domain['domain_masks_hex'][case['original_id']] and case['original_id'] not in filter_gate['records'][center]['rejected_ids'],'retained authenticated star ID')
            vertices=case['selected_full99_vertices'];rows=[int(row,16) for row in case['adjacency_rows_hex']]
            need(len(vertices)==len(rows)==28 and len(set(vertices))==28 and vertices[:15]==list(range(15)),'raw closed28 labels')
            need(cap_failure(rows) is None,'closed28 literal caps')
            u=center+15;need(u in vertices and case['centers_local']==[vertices.index(0),vertices.index(u)],'center labels')
            need(rows[vertices.index(u)].bit_count()==14 and all(rows[i]>>i&1==0 for i in range(28)),'closed neighborhood degrees/diagonal')
            for i,j in combinations(range(28),2):
                a,b=vertices[i],vertices[j];value=int(rows[i]>>j&1)
                need(value==int(rows[j]>>i&1),'symmetric raw graph')
                if a>=15:
                    state=outer_state(a,b);need(state==-1 or value==state,'raw closed28 honors family fixed entries')
                elif b<15:need(value==int(a==0 or(a>0 and(a-1)//2==(b-1)//2)),'root/seven matching scaffold')
                else:need(value==int(a>0 and a-1 in labels[b-15]),'fixed inner/outer incidence')
            cases.append(dict(index=len(cases),center=center,case=case,vertices=vertices,rows=rows,source=key(path),source_sha256=digest(path)))
    need(len(cases)==32,'frozen32case sample')
    source_hash=digest(Path(__file__))
    for path in (Path(__file__),ROOT/'uv.lock',ROOT/'acceleration/theory_20260930_closed29_extension_screen.md'):bindings[key(path)]=digest(path)
    invocation=1+len(list(args.out.glob('invocation_*.json')))
    save(args.out/f'invocation_{invocation:02d}.json',dict(status='CANDIDATE_PREREGISTERED',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
         command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),numpy=np.__version__,inputs_sha256=bindings,selected_closed28_cases=32,extra_vertex_choices_per_case=71,selected_case_vertex_pairs=2272,
         numerical_settings=dict(dtype='float64',negative_signal_threshold=-1e-8,integer_rounding_scales=[1024,1048576,1073741824],blas_threads=1),resource_limit_seconds=args.seconds,
         stopping_rule='First pair with all allowed assignments rejected by exact cap or numerical negative signal, or wall cap between pairs; record exact/inexact distinction',scope='Matching-specific closed28extensions in frozen120fixed/2160unknown family only'))
    if not(args.out/'controls.json').exists():save(args.out/'controls.json',controls())
    started=time.monotonic();completed=[];obstruction=None;stop='COMPLETE'
    for record in tqdm(cases,desc='Closed29 matching-specific cases'):
        vertices,rows=record['vertices'],record['rows'];u=record['center']+15
        T=[v for v in vertices if v>=15 and v!=u]
        need(len(T)==12 and set(T)=={vertices[i] for i in range(28) if rows[vertices.index(u)]>>i&1 and vertices[i]>=15},'complete12outer neighbors')
        for w in (v for v in range(15,99) if v not in vertices):
            path=args.out/'pairs'/f'case_{record["index"]:02d}_w_{w:02d}.json'
            if path.exists():
                result=json.loads(path.read_bytes());need(result['source_sha256']==source_hash and result['raw_closed28_source_sha256']==record['source_sha256'],'resume exact source/case binding')
                completed.append(result)
                if result['all_assignments_rejected']:obstruction=key(path);stop='FIRST_PROMISING_OBSTRUCTION';break
                continue
            if time.monotonic()-started>=args.seconds:stop='WALL_CAP';break
            need(outer_state(u,w)!=1,'outside vertex conflicts with fixed completed star')
            required=[v for v in T if outer_state(w,v)==1];optional=[v for v in T if outer_state(w,v)==-1]
            inner_neighbors=[a+1 for a in labels[w-15]]
            common_inner=len(set(labels[w-15])&set(labels[u-15]));target=2-common_inner
            assignments=choices(required,optional,target);outputs=[]
            inner_mask=sum(1<<vertices.index(v) for v in inner_neighbors)
            for picked in assignments:
                neighbors=inner_mask|sum(1<<vertices.index(v) for v in picked)
                extended=[row|((neighbors>>i&1)<<28) for i,row in enumerate(rows)]+[neighbors]
                failure=extension_cap_failure(rows,neighbors)
                item=dict(chosen_outer_edges_to_w=picked,w_neighbors_local_mask=hex(neighbors),adjacency_rows_hex=[hex(row) for row in extended],pair_cap_failure=failure,gram_screens=None)
                if failure is None:
                    screens=[dict(matrix=name,**screen(G)) for name,G in grams(matrix(extended))]
                    item['gram_screens']=screens
                    item['rejected']=any(r['negative_signal'] for r in screens)
                    item['exact_rejection']=any(r['exact_negative'] is not None for r in screens)
                else:item['rejected']=item['exact_rejection']=True
                outputs.append(item)
            all_rejected=all(row['rejected'] for row in outputs)
            result=dict(status='CANDIDATE',case_index=record['index'],center=record['center'],original_id=record['case']['original_id'],outer_extra_vertex=w,
                        full99_vertex_map=vertices+[w],raw_closed28_source=record['source'],raw_closed28_source_sha256=record['source_sha256'],source_sha256=source_hash,
                        fixed_required_outer_neighbors=required,unknown_optional_outer_neighbors=optional,forbidden_outer_neighbors=[v for v in T if outer_state(w,v)==0],
                        fixed_inner_neighbors=inner_neighbors,required_outer_neighbor_count=target,common_inner_count=common_inner,
                        complete_assignment_population=len(assignments),assignments=outputs,all_assignments_rejected=all_rejected,
                        all_rejections_exact=all(row['exact_rejection'] for row in outputs),cap_rejections=sum(row['pair_cap_failure'] is not None for row in outputs),
                        numerical_gram_rejections=sum(row['pair_cap_failure'] is None and row['rejected'] for row in outputs),
                        exact_gram_rejections=sum(row['pair_cap_failure'] is None and row['exact_rejection'] for row in outputs),
                        surviving_guidance_assignments=sum(not row['rejected'] for row in outputs),
                        target_resolution=False,whole_star_excluded=False,independent_review_pending=True)
            save(path,result);completed.append(result)
            if all_rejected:obstruction=key(path);stop='FIRST_PROMISING_OBSTRUCTION';break
        if stop!='COMPLETE':break
    need(all(digest(ROOT/name)==value for name,value in bindings.items()),'input/source stability')
    report=dict(status='CANDIDATE_SCREEN_RECORDS_PENDING_REVIEW',timestamp=datetime.now(timezone.utc).isoformat(),stop_reason=stop,
                completed_case_vertex_pairs=len(completed),frozen_case_vertex_pairs=2272,completed_assignments=sum(r['complete_assignment_population'] for r in completed),
                pair_cap_rejections=sum(r['cap_rejections'] for r in completed),numerical_gram_rejections=sum(r['numerical_gram_rejections'] for r in completed),
                exact_gram_rejections=sum(r['exact_gram_rejections'] for r in completed),surviving_guidance_assignments=sum(r['surviving_guidance_assignments'] for r in completed),
                first_promising_obstruction=obstruction,first_promising_obstruction_null_reason=None if obstruction else 'No fully rejected assignment population found among completed pairs',
                elapsed_this_invocation_seconds=time.monotonic()-started,inputs_sha256=bindings,independently_verified_exclusions=0,target_resolution=False,
                limitations=['Each case fixes one saved matching; no star exclusion without coverage of all matching possibilities.','Numerical survival is not a PSD certificate; numerical rejection without exact vector is not a proof.',
                             'Actual domain family fixed/free masks were used; edges outside the29vertex principal set remain unspecified.'],
                restart='Same exact script, --out this directory --resume --seconds120; completed immutable pair files are hash/source-bound and reused. No background process remains from this script.')
    save(args.out/('summary.json' if stop!='WALL_CAP' else f'checkpoint_{invocation:02d}.json'),report)
    print(json.dumps({k:report[k] for k in ('stop_reason','completed_case_vertex_pairs','completed_assignments','pair_cap_rejections','numerical_gram_rejections','exact_gram_rejections','first_promising_obstruction','elapsed_this_invocation_seconds')}))


if __name__=='__main__':main()
