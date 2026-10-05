"""Candidate exact sum-of-squares artifacts for the already frozen2688 cases."""
from datetime import datetime,timezone
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import json,platform,subprocess,sys,time
from tqdm import tqdm

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'acceleration/results/20260930_closed28_sos'
TABLES=ROOT/'acceleration/results/20260930_eight_domains/run01'
def digest(p):return sha256(Path(p).read_bytes()).hexdigest()
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def save(p,d):
    with p.open('x')as f:json.dump(d,f,indent=2)
def add(rows,a,b):rows[a]|=1<<b;rows[b]|=1<<a
def main():
    OUT.mkdir(parents=True,exist_ok=False);tick=time.monotonic();bindings={}
    def read(p):bindings[key(p)]=digest(p);return json.loads(p.read_bytes())
    for p in[Path(__file__),ROOT/'uv.lock',ROOT/'acceleration/theory_20260930_closed28_gram.md',ROOT/'acceleration/theory_20260930_closed28_gram_redundancy.md']:bindings[key(p)]=digest(p)
    screenpath=ROOT/'acceleration/results/20260930_closed28_gram/summary.json';assert digest(screenpath)=='d21f112240a6cf4a9667a80960903ce4247b5f303c59cdc374162cbdab5217f9';screen=read(screenpath)
    assert screen['completed_evaluations']==screen['frozen_population']==2688
    primary=read(TABLES/'manifest.json');assert bindings[key(TABLES/'manifest.json')]==screen['inputs_sha256'][key(TABLES/'manifest.json')]
    prereg=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),question='Does the proposed exact SOS identity hold coefficientwise for every already sampled closed28 graph?',selection='All2688 prior frozen cases in original order; no additional candidate selection.',acceptance='Exact center common counts, maximum deleted-center degree≤3, both exact Gram kernels, and all784 coefficients of the16G sum-of-squares identity.',resource_cap_seconds=100,numerical_threshold=None,numerical_threshold_reason='Integer-only checks; no numeric PSD inference.',inputs_sha256=dict(bindings),status='CANDIDATE producer evidence pending independent check')
    save(OUT/'preregistration.json',prereg)
    labels=[(2*a+s,2*b+t)for a,b in combinations(range(7),2)for s in range(2)for t in range(2)]
    base=[0]*99
    for a in range(1,15):add(base,0,a)
    for a in range(1,15,2):add(base,a,a+1)
    for u,label in enumerate(labels,15):
        for a in label:add(base,u,a+1)
    for a,b in primary['remaining_fixed_K_edges_outer']:add(base,a+15,b+15)
    records=[]
    for center_record in tqdm(screen['records'],desc='Exact closed28 SOS coefficients',unit='center'):
        assert time.monotonic()-tick<100,'cap reached; center artifacts preserve completed work'
        u=center_record['outer_vertex'];domain=read(TABLES/f'domain_{u:02d}.json');assert bindings[key(TABLES/f'domain_{u:02d}.json')]==screen['inputs_sha256'][key(TABLES/f'domain_{u:02d}.json')]
        cases=[]
        for case in center_record['cases']:
            i=case['original_id'];rows=base[:];mask=int(domain['domain_masks_hex'][i],16);center=u+15
            for a in range(84):
                if mask>>a&1:add(rows,center,a+15)
            neighbors=[a for a in range(99)if rows[center]>>a&1]
            for a,b in case['matching_witness_full99']:add(rows,a,b)
            vertices=sorted(set(range(15))|{center}|set(neighbors));assert len(vertices)==28
            H=[[int(rows[a]>>b&1)for b in vertices]for a in vertices];roots=[vertices.index(0),vertices.index(center)]
            R=[a for a in range(28)if a not in roots];N=[[b for b in range(28)if H[a][b]]for a in roots]
            assert all(len(n)==14 for n in N)and H[roots[0]][roots[1]]==0 and set(R)==set(N[0])|set(N[1])
            for a in roots:
                assert all(sum(H[a][k]*H[b][k]for k in range(28))==2-H[a][b]for b in range(28)if b!=a)
            G=[[27*int(a==b)-9*H[a][b]+1 for b in range(28)]for a in range(28)]
            for a,neighborhood in zip(roots,N):
                assert all(4*G[b][a]+sum(G[b][j]for j in neighborhood)==0 for b in range(28))
            degrees=[sum(H[a][b]for b in R)for a in R];assert max(degrees)<=3
            forms={a:{a:4,**{root:-1 for root,neighborhood in zip(roots,N)if a in neighborhood}}for a in R}
            target=[[0]*28 for _ in range(28)]
            def square(coefficients,weight):
                assert weight>=0
                for a,x in coefficients.items():
                    for b,y in coefficients.items():target[a][b]+=weight*x*y
            for a,b in combinations(R,2):
                if H[a][b]:
                    d={j:forms[a].get(j,0)-forms[b].get(j,0)for j in set(forms[a])|set(forms[b])};square(d,9)
            for a,degree in zip(R,degrees):square(forms[a],9*(3-degree))
            total={j:sum(forms[a].get(j,0)for a in R)for j in range(28)};square(total,1)
            assert target==[[16*v for v in row]for row in G],'exact complete SOS matrix identity'
            cases.append(dict(outer_vertex=u,original_id=i,star_mask=domain['domain_masks_hex'][i],matching_witness_full99=case['matching_witness_full99'],selected_full99_vertices=vertices,adjacency_rows_hex=[hex(sum(H[a][b]<<b for b in range(28)))for a in range(28)],centers_local=roots,deleted_center_vertices_local=R,deleted_center_degrees=degrees,exact_center_equalities=True,exact_kernel_vectors=True,all784_SOS_coefficients_equal=True,independent_check_pending=True))
        record=dict(outer_vertex=u,cases=cases,domain_sha256=bindings[key(TABLES/f'domain_{u:02d}.json')]);save(OUT/f'center_{u:02d}.json',record);records.append(dict(outer_vertex=u,path=key(OUT/f'center_{u:02d}.json'),sha256=digest(OUT/f'center_{u:02d}.json'),cases=len(cases)))
    assert all(digest(ROOT/k)==v for k,v in bindings.items()),'input changed'
    report=dict(status='CANDIDATE_CLOSED28_EXACT_SOS_COMPLETE',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=prereg['source_commit'],command=prereg['command'],cwd=str(ROOT),inputs_sha256=bindings,records=records,case_population=2688,completed_cases=sum(r['cases']for r in records),coefficient_identities_checked=2688*784,maximum_deleted_center_degree=3,arithmetic='Python integers only',elapsed_seconds=time.monotonic()-tick,independent_check_pending=True,general_theorem_status='CANDIDATE pending separate written review',target_resolution=False,limitations=['All sampled cases have exact PSD decompositions; no implication of SRG completion or existence.','The general redundancy statement requires the two exact center-row common-neighbor equalities, the union-of-neighborhoods coverage, and nonadjacent centers.','This producer does not approve its own result.'])
    save(OUT/'summary.json',report);print(json.dumps(dict(status=report['status'],completed_cases=report['completed_cases'],sha256=digest(OUT/'summary.json'),elapsed_seconds=report['elapsed_seconds'])))
if __name__=='__main__':main()
