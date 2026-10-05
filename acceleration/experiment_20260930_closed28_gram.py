"""Candidate closed-two-neighborhood Gram screen; exact negative witnesses only."""
import os
for name in('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[name]='1'
from datetime import datetime,timezone
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import argparse,json,platform,subprocess,sys,time
import numpy as np
from tqdm import tqdm

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'acceleration/results/20260930_closed28_gram'
REVIEW=ROOT/'acceleration/results/20260930_independent_review/eight_coordinate_matching_filter'
TABLES=ROOT/'acceleration/results/20260930_eight_domains/run01'
def digest(p):
    h=sha256()
    with Path(p).open('rb')as f:
        while b:=f.read(1<<20):h.update(b)
    return h.hexdigest()
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def save(p,d):
    with p.open('x')as f:json.dump(d,f,indent=2)
def add(rows,a,b):rows[a]|=1<<b;rows[b]|=1<<a
def gram(A):return[[27*int(a==b)-9*A[a][b]+1 for b in range(len(A))]for a in range(len(A))]
def quadratic(G,z):return sum(int(z[a])*int(G[a][b])*int(z[b])for a in range(len(z))for b in range(len(z)))
def exact_psd(matrix):
    M=[[Fraction(v)for v in r]for r in matrix]
    for i in range(len(M)):
        if M[i][i]<0:return False
        if M[i][i]==0:
            if any(M[i][j]for j in range(i+1,len(M))):return False
        else:
            for j in range(i+1,len(M)):
                for k in range(j,len(M)):
                    M[j][k]-=M[i][j]*M[i][k]/M[i][i];M[k][j]=M[j][k]
    return True
def controls():
    rook=[[int(a!=b and(a//3==b//3 or a%3==b%3))for b in range(9)]for a in range(9)]
    assert exact_psd(gram(rook))
    clique=[[int(a!=b)for b in range(5)]for a in range(5)];G=gram(clique);z=[1]*5
    assert quadratic(G,z)==-20 and not exact_psd(G)
    assert quadratic(G,[0]*5)==0 and not quadratic(G,[0]*5)<0 and quadratic(G,z)!=-19
    return dict(rook9_exact_fraction_PSD='PASS',clique5_exact_negative=dict(adjacency=clique,vector=z,quadratic=-20),zero_vector_corruption='REJECTED',wrong_quadratic_corruption='REJECTED')
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--seconds',type=float,default=100);parser.add_argument('--resume',action='store_true');args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=args.resume);assert not(OUT/'summary.json').exists();tick=time.monotonic();bindings={}
    def read(p):bindings[key(p)]=digest(p);return json.loads(p.read_bytes())
    for p in[Path(__file__),ROOT/'uv.lock',ROOT/'acceleration/theory_20260930_closed28_gram.md']:bindings[key(p)]=digest(p)
    gatepath=REVIEW/'summary.json';assert digest(gatepath)=='4fcd5fd7f02cd5362bda1f8f0a1c8e4669ce036bde56a04dcd1b6a3391b262f4';gate=read(gatepath)
    assert gate['status']=='INDEPENDENT_EIGHT_COORDINATE_NEIGHBORHOOD_MATCHING_FILTER_PASS'
    primary=read(TABLES/'manifest.json');assert bindings[key(TABLES/'manifest.json')]==gate['inputs_sha256'][key(TABLES/'manifest.json')]
    prereg=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),numpy=np.__version__,question='Do closed unions of root and center neighborhoods with one saved permitted matching fail the necessary target Gram PSD condition?',selection='First32 retained original IDs per center0..83, one saved matching witness per star, all2688 selections retained.',frozen_population=2688,eigenvalue_guidance_threshold=-1e-8,negative_vector_scales=[1024,1048576,1073741824],exact_acceptance='Python integer z^T(27I-9H+J)z<0; no floating value proves rejection or PSD.',scope='Each selected matching-specific complete induced28 adjacency only; no whole-star exclusion without all-matchings coverage.',resource_cap_seconds=args.seconds,cap_boundary='Between full centers; saved completed centers resume unchanged.',first_certificate='Preserve first in deterministic center/original-ID order; continue all preregistered cases.',inputs_sha256=dict(bindings),status='CANDIDATE experiment pending independent review')
    attempt=1+len(list(OUT.glob('invocation_*.json')));save(OUT/f'invocation_{attempt:02d}.json',prereg)
    if not(OUT/'controls.json').exists():save(OUT/'controls.json',controls())
    ctrl=read(OUT/'controls.json')
    labels=[(2*a+s,2*b+t)for a,b in combinations(range(7),2)for s in range(2)for t in range(2)]
    base=[0]*99
    for a in range(1,15):add(base,0,a)
    for a in range(1,15,2):add(base,a,a+1)
    for u,label in enumerate(labels,15):
        for a in label:add(base,u,a+1)
    fixed=set(map(tuple,primary['remaining_fixed_K_edges_outer']));unknown=set(map(tuple,primary['unknown_edges_outer']))
    for a,b in fixed:add(base,a+15,b+15)
    records=[]
    for u in tqdm(range(84),desc='Closed28 Gram guidance and certificates',unit='center'):
        target=OUT/f'center_{u:02d}.json'
        if target.exists():
            r=read(target);assert r['source_sha256']==bindings[key(Path(__file__))];records.append(r);continue
        if time.monotonic()-tick>=args.seconds:break
        rawpath=REVIEW/'recovered'/f'vertex_{u:02d}.json'
        if not rawpath.exists():rawpath=ROOT/'acceleration/results/20260930_eight_matching_filter/run01'/f'vertex_{u:02d}.json'
        raw=read(rawpath);assert bindings[key(rawpath)]==gate['records'][u]['raw_sha256']
        reject=set(gate['records'][u]['rejected_ids']);selected=[i for i in range(raw['original_count'])if i not in reject][:32]
        domain=read(TABLES/f'domain_{u:02d}.json');assert bindings[key(TABLES/f'domain_{u:02d}.json')]==gate['inputs_sha256'][key(TABLES/f'domain_{u:02d}.json')]
        cases=[]
        for i in selected:
            r=raw['records'][i];assert r['original_id']==i and r['mask']==domain['domain_masks_hex'][i]and r['matching_count']>0
            rows=base[:];center=u+15;mask=int(r['mask'],16)
            for v in range(84):
                if mask>>v&1:add(rows,center,v+15)
            neighbors=[v for v in range(99)if rows[center]>>v&1];assert len(neighbors)==14 and 0 not in neighbors
            forced=[(a,b)for a,b in combinations(neighbors,2)if rows[a]>>b&1];witness=list(map(tuple,r['matching_witness_full99']))
            assert len(forced+witness)==7 and sorted(v for e in forced+witness for v in e)==sorted(neighbors)
            assert all(list(e)in r['allowed_edges_full99']and tuple(sorted((e[0]-15,e[1]-15)))in unknown for e in witness)
            for e in witness:add(rows,*e)
            neighborhood_edges=set(forced+witness)
            assert all(bool(rows[a]>>b&1)==((a,b)in neighborhood_edges)for a,b in combinations(neighbors,2))
            vertices=sorted(set(range(15))|{center}|set(neighbors));assert len(vertices)==28
            H=[[int(rows[a]>>b&1)for b in vertices]for a in vertices]
            assert all(H[a][a]==0 and all(H[a][b]==H[b][a]for b in range(28))for a in range(28))
            # Root/inner incidence and the matching force every entry on these
            # vertices; the written closure argument is an explicit premise.
            G=gram(H);eigenvectors=np.linalg.eigh(np.asarray(G,dtype=np.float64));minimum=float(eigenvectors[0][0]);vector=None;value=None;scale_used=None
            if minimum<-1e-8:
                for scale in(1024,1048576,1073741824):
                    z=[int(v)for v in np.rint(eigenvectors[1][:,0]*scale)];q=quadratic(G,z)
                    if q<0:vector=z;value=q;scale_used=scale;break
            case=dict(outer_vertex=u,original_id=i,matching_witness_full99=[list(e)for e in witness],float64_minimum_eigenvalue_heuristic=minimum,negative_eigenvalue_signal=minimum<-1e-8,exact_negative=value is not None,integer_vector=vector,exact_quadratic=value,rounding_scale=scale_used)
            cases.append(case)
            if value is not None and not(OUT/'first_negative_certificate.json').exists():
                save(OUT/'first_negative_certificate.json',dict(status='CANDIDATE_EXACT_MATCHING_SPECIFIC_GRAM_REJECTION',case=case,selected_full99_vertices=vertices,adjacency_matrix=H,gram_matrix=G,star_mask=r['mask'],forced_matching_full99=[list(e)for e in forced],root_labels_outer=labels,domain_path=key(TABLES/f'domain_{u:02d}.json'),domain_sha256=bindings[key(TABLES/f'domain_{u:02d}.json')],raw_matching_path=key(rawpath),raw_matching_sha256=bindings[key(rawpath)],claim='This particular closed28 induced graph cannot occur in a target SRG because its necessary Gram principal matrix has a negative exact quadratic form.',whole_star_excluded=False,general_family_excluded=False,target_resolution=False,independent_check_pending=True))
        record=dict(outer_vertex=u,selected_ids=selected,cases=cases,source_sha256=bindings[key(Path(__file__))],raw_sha256=bindings[key(rawpath)],domain_sha256=bindings[key(TABLES/f'domain_{u:02d}.json')])
        save(target,record);records.append(record)
    cases=[c for r in records for c in r['cases']];complete=len(records)==84
    assert all(digest(ROOT/k)==v for k,v in bindings.items()),'source/input changed'
    report=dict(status='CANDIDATE_CLOSED28_GRAM_SCREEN_COMPLETE'if complete else'INCOMPLETE_CLOSED28_GRAM_SCREEN_TIME_CAP',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=prereg['source_commit'],command=prereg['command'],cwd=str(ROOT),python=platform.python_version(),numpy=np.__version__,inputs_sha256=bindings,records=records,frozen_population=2688,attempted_evaluations=len(cases),completed_evaluations=len(cases),centers_completed=len(records),unattempted_evaluations=2688-len(cases),negative_numerical_signals=sum(c['negative_eigenvalue_signal']for c in cases),exact_negative_certificates=sum(c['exact_negative']for c in cases),numerical_signal_without_exact_certificate=sum(c['negative_eigenvalue_signal']and not c['exact_negative']for c in cases),minimum_eigenvalue_heuristic=min((c['float64_minimum_eigenvalue_heuristic']for c in cases),default=None),controls=ctrl,elapsed_seconds=time.monotonic()-tick,whole_stars_excluded=0,independently_verified_rejections=0,first_negative_artifact='first_negative_certificate.json'if(OUT/'first_negative_certificate.json').exists()else None,limitations=['All numerical eigenvalues are heuristic; absence of a negative signal does not certify PSD.','An exact negative vector rejects only its matching-specific closed28 graph, subject to independently checked closure and Gram necessity.','Only one saved matching per sampled star was examined; a rejected witness does not exclude the star or all its matchings.','No producer filter or numerical scoring modules imported; NumPy is used only for eigenvector guidance.'],target_resolution=False)
    save(OUT/('summary.json'if complete else f'checkpoint_{attempt:02d}.json'),report)
    print(json.dumps({k:report[k]for k in('status','completed_evaluations','negative_numerical_signals','exact_negative_certificates','unattempted_evaluations','elapsed_seconds')}))
if __name__=='__main__':main()
