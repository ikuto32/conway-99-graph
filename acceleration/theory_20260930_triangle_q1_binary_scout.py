"""Bounded new exact Q1 factors and direct binary-row obstruction scout."""
from datetime import datetime, timezone
from itertools import combinations, permutations, product
from pathlib import Path
import argparse
import hashlib
import json
import math
import platform
import random
import subprocess
import sys
import time
from theory_20260930_eight_full99_cnf import Clauses, Encoder, ResourceCap
from theory_20260930_triangle_row_obstruction import controls as row_controls

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / 'external_conway99_research'
PIN = '85e705cc6c2a14d123120c93a847e30aaab1789e'
E = [e for e in combinations(range(12), 2) if e[1] != (e[0] ^ 1)]
EI = {e: i for i, e in enumerate(E)}
G01 = [[2-int(a == b)-2*int(b == (a ^ 1))-int(b == ((a+6) % 12)) for b in range(12)] for a in range(12)]
G12 = [[2-int(a == b)-int(b == ((a+6) % 12))-2*int(b == (((a ^ 1)+6) % 12)) for b in range(12)] for a in range(12)]


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p, obj): p.write_text(json.dumps(obj, indent=2)+'\n', encoding='utf-8')


def gram01(q):
    matrix = [[0]*12 for _ in range(12)]
    for d in range(60):
        for a in E[d]:
            for b in E[q[d]]:
                matrix[a][b] += 1
    return matrix


def validate_factor(q):
    if sorted(q) != list(range(60)) or gram01(q) != G01:
        return False
    rows = [sum((1 << d) for d in range(60) if a in E[d]) for a in range(12)]
    rows += [sum((1 << d) for d in range(60) if a in E[q[d]]) for a in range(12)]
    for a in range(24):
        for b in range(24):
            target = (10 if a%12 == b%12 else (0 if b%12 == ((a%12)^1) else 1)) if a//12 == b//12 else G01[a%12][b%12]
            if (rows[a]&rows[b]).bit_count() != target:
                return False
    return True


def maps():
    blocks = ((0,1,6,7),(2,3,8,9),(4,5,10,11))
    result = []
    for bp in permutations(range(3)):
        for flips in product(range(4), repeat=3):
            p = [0]*12
            for i in range(3):
                for j, v in enumerate(blocks[i]): p[v] = blocks[bp[i]][j ^ flips[i]]
            assert all(p[v ^ 1] == (p[v] ^ 1) and p[(v+6)%12] == (p[v]+6)%12 for v in range(12))
            result.append([EI[tuple(sorted((p[a],p[b])))] for a,b in E])
    assert len({tuple(x) for x in result}) == 384
    return result


def orbit(q, edge_maps):
    images = set()
    for p in edge_maps:
        image = [0]*60
        for d in range(60): image[p[d]] = p[q[d]]
        images.add(tuple(image))
    return images


def trade_candidates(q):
    inv = [0]*60
    for i,j in enumerate(q): inv[j] = i
    for x,y in combinations(range(12), 2):
        rr = [r for r in range(12) if tuple(sorted((x,r))) in EI and tuple(sorted((y,r))) in EI]
        dd = [(inv[EI[tuple(sorted((x,r)))]],inv[EI[tuple(sorted((y,r)))]]) for r in rr]
        vectors = []
        for a,b in dd:
            vectors.append([int(v in E[b])-int(v in E[a]) for v in range(12)])
        value, previous = [0]*12, 0
        for step in range(1,1<<len(rr)):
            mask = step ^ (step>>1)
            bit = (mask ^ previous).bit_length()-1
            sign = 1 if mask & (1<<bit) else -1
            value = [a+sign*b for a,b in zip(value,vectors[bit])]
            previous = mask
            if not any(value):
                new = q.copy()
                selected = []
                for i,(a,b) in enumerate(dd):
                    if mask & (1<<i): new[a],new[b] = new[b],new[a]; selected.append(rr[i])
                yield new, {'operation': 'balanced_two_row_trade', 'x':x,'y':y,'R':selected}


def row_solve(n, cs, cap):
    start = time.monotonic()
    nodes = []
    def dfs(a):
        cap.check()
        if len(nodes)>=20000 or time.monotonic()-start>2: raise TimeoutError('per-row limit')
        idx=len(nodes); node={'id':idx,'forces':[]}; nodes.append(node)
        while True:
            changed=False
            for ci,c in enumerate(cs):
                ones=sum(a[x]==1 for x in c['variables']); free=[x for x in c['variables'] if a[x]<0]
                if ones>c['upper'] or ones+len(free)<c['lower']:
                    node.update(status='CONFLICT',constraint=ci,ones=ones,free=len(free)); return None,idx
                val=0 if ones==c['upper'] else (1 if ones+len(free)==c['lower'] else None)
                if val is not None and free:
                    node['forces'].append({'constraint':ci,'ones_before':ones,'free_before':free,'value':val})
                    for x in free:a[x]=val
                    changed=True
            if not changed:break
        if -1 not in a:node.update(status='SAT',assignment=a);return a,idx
        score=[0]*n
        for c in cs:
            free=[x for x in c['variables'] if a[x]<0]
            for x in free:score[x]+=1000//max(1,len(free))
        x=max((i for i in range(n) if a[i]<0),key=lambda i:(score[i],-i))
        node.update(status='SPLIT',variable=x,children=[])
        for val in (0,1):
            b=a.copy();b[x]=val;answer,j=dfs(b);node['children'].append({'value':val,'node':j})
            if answer is not None:return answer,idx
        return None,idx
    try:
        solution,root=dfs([-1]*n)
        return {'status':'UNSAT' if solution is None else 'SAT','assignment':solution,'root':root,'nodes':nodes,'elapsed_seconds':time.monotonic()-start}
    except TimeoutError as e:
        return {'status':'UNKNOWN','reason':str(e),'root':0,'nodes':nodes,'elapsed_seconds':time.monotonic()-start}


def row_constraints(known,u):
    vv=[v for v in range(99) if known[u][v]==-1]; assert len(vv)==60
    cs=[{'kind':'degree','vertex':u,'variables':list(range(60)),'lower':10,'upper':10}]
    for v in range(3,27):
        common=[w for w in range(99) if known[u][w]==known[v][w]==1]
        bound=2-known[u][v]-len(common)
        cs.append({'kind':'exact_common','pair':[u,v],'known_common':common,'variables':[i for i,w in enumerate(vv) if known[v][w]==1],'lower':bound,'upper':bound})
    for i,j in combinations(range(60),2):
        a,b=vv[i],vv[j]; common=[w for w in range(99) if w!=u and known[a][w]==known[b][w]==1]
        bound=1 if known[a][b]==1 else 2
        if len(common)>=bound:
            assert len(common)==bound
            cs.append({'kind':'incompatible_pair','pair':[a,b],'known_edge':known[a][b],'known_common':common,'variables':[i,j],'lower':0,'upper':1})
    return vv,cs


def size_scout(cap):
    clauses=Clauses(None,cap); blocks=[[],[]]; variable=0
    for g in range(2):
        for a in range(12):
            row=[]
            for edge in E:
                if any(G01[b][a]==0 for b in edge):row.append(False)
                else:variable+=1;row.append(variable)
            blocks[g].append(row)
    primary=variable; enc=Encoder(primary,clauses); products=0; constraints=0
    for block in blocks:
        for row in block:enc.counter([x for x in row if type(x)is int],10,True,{});constraints+=1
        for d in range(60):enc.counter([block[a][d] for a in range(12) if type(block[a][d])is int],2,True,{});constraints+=1
        for a in range(12):
            for b in range(12):enc.counter([block[b][d] for d,e in enumerate(E) if a in e and type(block[b][d])is int],G01[a][b],True,{});constraints+=1
    rows=blocks[0]+blocks[1]
    for a,b in combinations(range(24),2):
        bound=(0 if b%12==((a%12)^1) else 1) if a//12==b//12 else G12[a%12][b%12]
        terms=[]
        for x,y in zip(rows[a],rows[b]):
            if type(x)is int and type(y)is int:
                terms.append(enc.conjunction(x,y));products+=1
        enc.counter(terms,bound,True,{});constraints+=1
    return {'status':'CANDIDATE_SIZE_ONLY','primary_binary_entries':primary,'AND_products':products,'variables':enc.top,'clauses':clauses.count,'constraints':constraints,'rows':24,'columns':120,'linear_cross_rows':288,'quadratic_gram_rows':276,'solver_calls':0,'no_equivalence_approval':True}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    cap=ResourceCap(); archive_files=[ARCHIVE/'attempts/wave151-triangle-root-factor/exact-results.json',ARCHIVE/'attempts/wave154-triangle-factor-portfolio/exact-results.json']
    raw_path=ROOT/'acceleration/results/20260930_triangle_partial99/wave154.json'
    sources=[Path(__file__),Path(__file__).with_name('theory_20260930_triangle_q1_binary_scout_spec.md'),raw_path,*archive_files,ROOT/'uv.lock',ROOT/'pyproject.toml',ROOT/'acceleration/theory_20260930_eight_full99_cnf.py',ROOT/'acceleration/theory_20260930_triangle_row_obstruction.py']
    save(out/'manifest.json',{'timestamp':datetime.now(timezone.utc).isoformat(),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'command':[sys.executable,*sys.argv],'cwd':str(ROOT),'python':platform.python_version(),'input_hashes':{p.relative_to(ROOT).as_posix():sha(p) for p in sources},'archive_pin':PIN,'random_seed':20260930,'limits':{'total_seconds':120,'trade_seconds':20,'heuristic_seconds':60,'heuristic_swaps':512000,'new_factors':8,'row_seconds':2,'row_nodes':20000},'status':'CANDIDATE','scope':'Only fixed Wave149 core; no unrestricted containment.'})
    old=[json.loads(archive_files[0].read_bytes())['exact_partial_factor']['Q1'],json.loads(archive_files[1].read_bytes())['second_exact_Q1_representative']['Q1']]
    assert all(validate_factor(q) for q in old)
    corrupt=old[0].copy();corrupt[0],corrupt[1]=corrupt[1],corrupt[0];assert not validate_factor(corrupt)
    save(out/'controls.json',{'archived_factors_replayed':2,'swapped_images_rejected':True,'row_controls':row_controls()})
    edge_maps=maps();seen=set().union(*(orbit(q,edge_maps) for q in old));new=[];trade_parents=0;trade_candidates_count=0
    def accept(q,origin):
        nonlocal seen
        assert validate_factor(q)
        if tuple(q) in seen:return False
        image=orbit(q,edge_maps);seen.update(image)
        record={'index':len(new),'Q1':q.copy(),'origin':origin,'coordinate_orbit_size':len(image),'exact_24x60_Gram_pass':True}
        new.append(record);save(out/('factor_%02d.json'%record['index']),record);return True
    trade_start=time.monotonic();parent_queue=[q.copy() for q in old]
    while parent_queue and len(new)<8 and time.monotonic()-trade_start<20:
        q=parent_queue.pop(0);parent=trade_parents;trade_parents+=1
        for candidate,trade in trade_candidates(q):
            cap.check();trade_candidates_count+=1
            if accept(candidate,{'parent_Q1':q,'parent_attempt':parent,**trade}):parent_queue.append(candidate)
            if len(new)>=8 or time.monotonic()-trade_start>=20:break
    rng=random.Random(20260930);swaps=0;zero_hits=0;score_records=[];hs=time.monotonic();q=old[0].copy();res=[[0]*12 for _ in range(12)];score=0
    while len(new)<8 and swaps<512000 and time.monotonic()-hs<60:
        if swaps%1024==0:cap.check()
        i,j=rng.sample(range(60),2);oldi,oldj=q[i],q[j]
        left=[(a,int(a in E[i])-int(a in E[j])) for a in set(E[i]+E[j])];right=[(b,int(b in E[oldj])-int(b in E[oldi])) for b in set(E[oldi]+E[oldj])]
        delta=sum((res[a][b]+x*y)**2-res[a][b]**2 for a,x in left for b,y in right)
        temp=0.25+2.75*(1-(swaps%16000)/16000)
        if delta<=0 or rng.random()<math.exp(-delta/temp):
            for a,x in left:
                for b,y in right:res[a][b]+=x*y
            q[i],q[j]=q[j],q[i];score+=delta
            if score==0:
                zero_hits+=1;accept(q,{'operation':'annealed_permutation','seed':20260930,'attempted_swap':swaps+1,'integer_objective':0})
        swaps+=1
        if swaps%16000==0:
            assert res==[[gram01(q)[a][b]-G01[a][b] for b in range(12)] for a in range(12)]
            score_records.append({'attempted_swaps':swaps,'exact_score':score,'new_factors':len(new)})
    save(out/'generation.json',{'new_factor_count':len(new),'trade_parents':trade_parents,'trade_candidates':trade_candidates_count,'heuristic_attempted_swaps':swaps,'heuristic_zero_hits':zero_hits,'heuristic_final_exact_score':score,'score_records':score_records})
    template=json.loads(raw_path.read_bytes())['initial_adjacency'];outcomes=[]
    for item in new:
        if time.monotonic()-cap.start>105:break
        cap.check();folder=out/('factor_%02d_rows'%item['index']);folder.mkdir();known=[r.copy() for r in template]
        for a in range(12):
            for d in range(60):known[15+a][39+d]=known[39+d][15+a]=int(a in E[item['Q1'][d]])
        save(folder/'raw99.json',{'known_adjacency':known,'Q1':item['Q1'],'scope':'Fixed core and two binary groups; C2 andD free.'});rows=[]
        for u in range(27,39):
            if time.monotonic()-cap.start>105:break
            vv,cs=row_constraints(known,u);tree=row_solve(60,cs,cap);row={'vertex':u,'variables':vv,'constraints':cs,'proof':tree}
            save(folder/('row_%02d.json'%u),row);rows.append({'vertex':u,'status':tree['status'],'nodes':len(tree['nodes'])})
            if tree['status']=='UNSAT':break
        outcome={'factor':item['index'],'rows':rows,'excluded_by_empty_row':any(r['status']=='UNSAT' for r in rows)};outcomes.append(outcome);save(folder/'summary.json',outcome)
    save(out/'joint_model_size.json',size_scout(cap))
    summary={'status':'CANDIDATE_BINARY_FACTOR_SCOUT_COMPLETE','independent_verification':'PENDING','new_coordinate_orbits':len(new),'factor_outcomes':outcomes,'unattempted_factor_evaluations':len(new)-len(outcomes),'excluded_factor_count':sum(x['excluded_by_empty_row'] for x in outcomes),'heuristic_swaps':swaps,'elapsed_seconds':time.monotonic()-cap.start,'peak_working_set_bytes':cap.peak_bytes,'target_resolution':False,'full_fixed_core_exclusion':False,'output_hashes':{p.relative_to(ROOT).as_posix():sha(p) for p in sorted(out.rglob('*')) if p.is_file()}}
    save(out/'summary.json',summary);print(json.dumps({k:v for k,v in summary.items() if k!='output_hashes'}))


if __name__=='__main__':main()
