"""Deterministic raw local-core preparation only; not an approved generic GPU domain."""
from collections import Counter
from datetime import datetime,timezone
from hashlib import file_digest
from itertools import combinations
from pathlib import Path
import argparse
import json
import platform
import subprocess
import sys
import time
from tqdm import tqdm

ROOT=Path(__file__).resolve().parents[1]
CENSUS=ROOT/'acceleration/results/20260930_triangle_matching_pair_census_v2'
GATES={
 ROOT/'acceleration/results/20260930_independent_review/triangle_core_identity/summary.json':('a38394b4438c79e89e19095ff92fdb4c2d21e20284c0c417fb19c8a146913db3','INDEPENDENT_TRIANGLE_CORE_IDENTITY_CONSTRUCTION_PASS'),
 ROOT/'acceleration/results/20260930_independent_review/triangle_matching_pair_census/summary.json':('085748fd2ebb03bdb7ea6048d782be0c17ce8cadef4ea32028cb58ca6b0efb79','INDEPENDENT_TRIANGLE_ORDERED_MATCHING_PAIR_CENSUS_PASS'),
 ROOT/'acceleration/results/20260930_independent_review/unrestricted_triangle_factor/summary.json':('a7d470ccf10df7dff77884c8bd1fe4784234ac80bc4e1b684e0050c3e33a4acd','INDEPENDENT_UNRESTRICTED_TRIANGLE_FACTOR_NORMALIZATION_PASS')}

def need(b,s):
    if not b:raise ValueError(s)
def digest(p):
    with p.open('rb') as f:return file_digest(f,'sha256').hexdigest()
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(p.read_bytes())
def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')

def graph(matchings):
    n=len(matchings[0]);need(len(matchings)==3 and n%2==0,'three even matching fibres')
    for q in matchings:need(len(q)==n and all(type(x)is int and 0<=x<n for x in q) and all(q[i]!=i and q[q[i]]==i for i in range(n)),'fixed-point-free perfect matching')
    a=[[0]*(3+3*n) for _ in range(3+3*n)]
    def edge(i,j):a[i][j]=a[j][i]=1
    for i,j in combinations(range(3),2):edge(i,j)
    for g,q in enumerate(matchings):
        for i,j in enumerate(q):edge(g,3+g*n+i);edge(3+g*n+i,3+g*n+j)
    for g,h in combinations(range(3),2):
        for i in range(n):edge(3+g*n+i,3+h*n+i)
    return a

def check_caps(a):
    n=len(a);need(all(len(r)==n and all(type(x)is int and x in (0,1) for x in r) for r in a),'binary square graph')
    need(all(a[i][i]==0 and a[i][j]==a[j][i] for i in range(n) for j in range(n)),'simple symmetric graph')
    masks=[sum(x<<j for j,x in enumerate(r)) for r in a];hist=Counter()
    for i,j in combinations(range(n),2):
        value=(masks[i]&masks[j]).bit_count()+a[i][j];need(value<=2,'literal positive-graph paircap');hist[value]+=1
    return dict(pairs=n*(n-1)//2,histogram=dict(sorted(hist.items())))

def components(c):
    unseen=set(range(len(c)));parts=[]
    while unseen:
        todo=[min(unseen)];part=[];unseen.remove(todo[0])
        while todo:
            i=todo.pop();part.append(i)
            for j,x in enumerate(c[i]):
                if x and j in unseen:unseen.remove(j);todo.append(j)
        parts.append(sorted(part))
    return parts

def selected_artifact(stage,local,gid,matchings,a,capcheck):
    c=[r[3:] for r in a[3:]];n=12;catalogs=[[list(pair) for pair in combinations(range(n),2) if q[pair[0]]!=pair[1]] for q in matchings]
    need(all(len(x)==60 for x in catalogs),'three full nonmatching-edge catalogs')
    nn=[set(j for j,x in enumerate(r) if x) for r in c];an=[set(j for j,x in enumerate(r) if x) for r in a]
    g=[[12*int(i==j)+2-c[i][j]-len(nn[i]&nn[j])-int(i//12==j//12) for j in range(36)] for i in range(36)]
    literal=[[12*int(i==j)+2-a[i+3][j+3]-len(an[i+3]&an[j+3]) for j in range(36)] for i in range(36)]
    need(g==literal and all(v>=0 for r in g for v in r),'literal39 vs core-polynomial Gram')
    for fibre in range(3):
        incidence=[[int(i in pair) for pair in catalogs[fibre]] for i in range(12)]
        need(all(sum(row)==10 for row in incidence),'catalog row margins')
        need(all(sum(incidence[i][d]*incidence[j][d] for d in range(60))==g[12*fibre+i][12*fibre+j] for i in range(12) for j in range(12)),'full within-catalog Gram')
    return dict(schema='CANDIDATE_CONNECTED_IDENTITY_P_CORE_DOMAIN_V1',first_stage=stage,second_orbit=local,pair_representative_index=gid,M0=matchings[0],M1=matchings[1],M2=matchings[2],P=list(range(12)),cross01=list(range(12)),cross02=list(range(12)),coordinate_labels=list(range(12)),core_row_labels=[dict(fibre=i//12,coordinate=i%12,full39_vertex=3+i) for i in range(36)],core_adjacency=c,full39_adjacency=a,components=components(c),canonical_C0_columns=catalogs[0],nonmatching_edge_catalogs=catalogs,target_gram=g,local_pair_cap_check=capcheck,within_Gram_entries_checked=432,full_Gram_entries_checked=1296,connected36=True,P_chosen_not_without_loss=True,full_factor=None,full_factor_reason='Construction domain preparation only; no factor search run.',target_graph=False,independent_verification='PENDING')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic();inputs={}
    for p,(h,status) in GATES.items():
        need(digest(p)==h and read(p)['status']==status,'independent premise gate');inputs[key(p)]=h
        for path,value in read(p)['inputs_sha256'].items():need(digest(ROOT/path)==value,'premise inputs unchanged');inputs[path]=value
    for p in [Path(__file__),Path(__file__).with_name('theory_20260930_connected_identity_cores_spec.md'),ROOT/'uv.lock',ROOT/'pyproject.toml']:inputs[key(p)]=digest(p)
    manifest=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=inputs,selection_rule='For each M1stage ascending, firstM2 representative in frozen second_orbits order whose36core withP=I is connected; select first4 qualifying distinctstages. Scan all3580 representatives and report actualcount if fewerthan4.',frozen_population=dict(first_stages=11,ordered_pair_representatives=3580),resource_limit_seconds=60,seed=None,seed_reason='Deterministic frozen catalog order.',solver_calls=0,GPU_calls=0,independent_approval=False)
    save(out/'selection_manifest.json',manifest)
    # Calibrate before the eligibility scan.
    rook=graph([[1,0]]*3);check_caps(rook)
    need(all(sum(rook[i][k]*rook[k][j] for k in range(9))==2*int(i==j)-rook[i][j]+2 for i in range(9) for j in range(9)),'known valid SRG9 identity')
    small=graph([[1,0,3,2],[2,3,0,1],[3,2,1,0]]);check_caps(small);need(len(components([r[3:] for r in small[3:]]))==1,'connected small core control')
    rejected=[]
    def reject(label,fun):
        try:fun()
        except (ValueError,KeyError,IndexError,TypeError):rejected.append(label)
        else:raise AssertionError('bad control accepted '+label)
    bad=[r[:] for r in small];bad[0][7]=bad[7][0]=1;reject('extra_root_foreign_fibre_edge',lambda:check_caps(bad))
    reject('fixedpoint_matching',lambda:graph([[0,1],[1,0],[1,0]]))
    eligibility=[];stages=[];selected=[];gid=0
    for stage in tqdm(range(11),desc='Selecting connected identity cores'):
        path=CENSUS/f'stage_{stage:02d}.json';saved=read(path);m0=[i^1 for i in range(12)];m1=saved['M1'];first=None;connected_count=0;component_hist=Counter()
        for local,orb in enumerate(saved['second_orbits']):
            m2=orb['representative'];a=graph([m0,m1,m2]);capcheck=check_caps(a);c=[r[3:] for r in a[3:]];parts=components(c);sizes=tuple(sorted(map(len,parts)));connected=len(parts)==1;component_hist[sizes]+=1;connected_count+=int(connected)
            eligibility.append(dict(pair_representative_index=gid,first_stage=stage,second_orbit=local,matching_universe_representative_index=orb['representative_index'],component_sizes=list(sizes),connected36=connected,all_local39_pair_caps=True,local39_pair_caps_checked=741))
            if connected and first is None:
                first=dict(first_stage=stage,second_orbit=local,pair_representative_index=gid)
                if len(selected)<4:
                    artifact=selected_artifact(stage,local,gid,[m0,m1,m2],a,capcheck);name=out/f'core_{len(selected):02d}.json';save(name,artifact);selected.append({**first,**dict(path=key(name),sha256=digest(name),component_sizes=[36])})
            gid+=1
        stages.append(dict(first_stage=stage,candidates=len(saved['second_orbits']),connected_candidates=connected_count,first_connected=first,component_size_histogram=[dict(sizes=list(k),count=v) for k,v in sorted(component_hist.items())]))
        need(time.monotonic()-start<60,'bounded preparation time')
    need(gid==len(eligibility)==3580,'all frozen pair representatives visited')
    expected=[s['first_connected'] for s in stages if s['first_connected'] is not None][:4]
    need([{k:r[k] for k in ['first_stage','second_orbit','pair_representative_index']} for r in selected]==expected,'deterministic first4 stage rule')
    if selected:
        chosen=read(ROOT/selected[0]['path']);bad=[r[:] for r in chosen['target_gram']];bad[0][0]+=1;reject('altered_Gram_coefficient',lambda:need(bad==chosen['target_gram'],'exact Gram data'))
    save(out/'eligibility.json',dict(population='3580 frozen ordered matching-pair representatives with P fixedtoidentity',records=eligibility))
    save(out/'stages.json',stages);save(out/'controls.json',dict(known_valid_rook9=True,small_connected_n4=True,rejected=rejected))
    summary=dict(status='CANDIDATE_FOUR_CONNECTED_IDENTITY_CORE_DOMAINS_PREPARED',timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=inputs,selection_manifest=key(out/'selection_manifest.json'),selection_manifest_sha256=digest(out/'selection_manifest.json'),candidates_evaluated=3580,connected_candidates=sum(s['connected_candidates'] for s in stages),qualifying_first_stages=sum(s['first_connected']is not None for s in stages),selected_count=len(selected),selected=selected,all_candidate_pair_caps_checked=3580*741,selected_Gram_entries_checked=len(selected)*1296,selected_within_Gram_entries_checked=len(selected)*432,solver_calls=0,GPU_calls=0,search_calls=0,independent_verification='PENDING',scope='Only the four raw specified connected36cores and their local39positive graphs; P=I is a chosen restriction, not target normalization.',target_resolution=False,limitations=['No full incidence factor, residualD or target graph.','Distinct M1stages ensure the declared stage diversity, not a classification of all core isomorphism types.','Generic GPU admission still requires a separate independently authenticated raw-domain gate.'],elapsed_seconds=time.monotonic()-start,outputs_sha256={key(p):digest(p) for p in out.iterdir() if p.is_file()})
    save(out/'summary.json',summary);print(json.dumps(dict(status=summary['status'],summary_sha256=digest(out/'summary.json'),selected_count=len(selected),selected=[(r['first_stage'],r['second_orbit']) for r in selected],elapsed_seconds=summary['elapsed_seconds'])))

if __name__=='__main__':main()
