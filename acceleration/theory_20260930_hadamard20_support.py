"""Candidate collapsed-support construction and cheap necessary lift screens."""
import argparse
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations,product
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
from tqdm import tqdm

ROOT=Path(__file__).resolve().parents[1]
CORE=ROOT/'acceleration/results/20260930_connected_identity_cores'
CORE_PINS=['3d4ad2d5b8ff92ca3d7761ac79e3651e306052897c3327b4eec87d7a85dabe81','23fb79efbc42fcaf7d54edb32311703be47fa96014a1c46ed00859a0753576e4',
           '40c23054a9276039b0dc1320594f102ae65d06c8e2c819a31d6600c3ee279eeb','cdd61bb140888090f092af7bbc3dbc40399f8e06bb3b41781dcfba22f0f701f1']
GATE=ROOT/'acceleration/results/20260930_independent_review/connected_identity_cores/summary.json'
GH='efdcacb9130bf29a28ece4c07022bdab11ab953a862f117fc55f44bd5244d2b4'

def need(ok,why):
    if not ok:raise ValueError(why)
def digest(p):return sha256(p.read_bytes()).hexdigest()
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def save(p,x,compact=False):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=None if compact else 2,separators=(',',':') if compact else None);f.write('\n')
def validate_h(h):
    need(len(h)==20 and all(len(row)==20 and all(type(v)is int and v in(-1,1) for v in row) for row in h),'20sign matrix')
    need(all(sum(h[k][i]*h[k][j] for k in range(20))==20*int(i==j) for i in range(20) for j in range(20)),'HtransposeH exact')
    need(all(v==1 for v in [row[0] for row in h]) and all(sum(row[j] for row in h)==0 for j in range(1,20)),'constant first and balanced remaining columns')
def matching_ok(m):return len(m)==12 and all(type(v)is int and 0<=v<12 for v in m) and all(m[a]!=a and m[m[a]]==a for a in range(12))
def core_gram(ms):
    need(len(ms)==3 and all(matching_ok(m) for m in ms),'three perfectmatchings')
    c=[[0]*36 for _ in range(36)]
    for g,a in product(range(3),range(12)):
        c[12*g+a][12*g+ms[g][a]]=1
        for h in range(3):
            if g!=h:c[12*g+a][12*h+a]=1
    gram=[[12*int(i==j)+2-c[i][j]-sum(c[i][k]*c[k][j] for k in range(36))-int(i//12==j//12) for j in range(36)] for i in range(36)]
    return c,gram
def support(h,ms):
    blocks=[]
    for m in ms:
        need(matching_ok(m),'matching input');pairs=[(a,m[a]) for a in range(12) if a<m[a]];x=[[0]*20 for _ in range(12)]
        for j,(a,b) in enumerate(pairs):x[a]=[h[t][j+1] for t in range(20)];x[b]=[-h[t][j+1] for t in range(20)]
        blocks.append(x)
    x=[sum((block[a] for block in blocks),[]) for a in range(12)];l=[[(v+1)//2 for v in row] for row in x]
    validate_support(x,l,ms)
    return x,l,blocks
def validate_support(x,l,ms):
    need(len(x)==12 and all(len(row)==60 and all(type(v)is int and v in(-1,1) for v in row) and sum(row)==0 for row in x),'balancedX')
    need(l==[[(v+1)//2 for v in row] for row in x] and all(sum(row)==30 for row in l),'binary support rowmargins')
    need(all(sum(l[a][d] for a in range(12))==6 for d in range(60)),'support columnmargins')
    for a,b in product(range(12),repeat=2):
        s=sum(m[a]==b for m in ms)
        need(sum(x[a][d]*x[b][d] for d in range(60))==20*(3*int(a==b)-s),'XGram')
        need(sum(l[a][d]*l[b][d] for d in range(60))==15*int(a==b)+15-5*s,'LGram')

def bipartite(neighbors,nright):
    match=[-1]*nright
    def aug(v,seen):
        for r in neighbors[v]:
            if r in seen:continue
            seen.add(r)
            if match[r]<0 or aug(match[r],seen):match[r]=v;return True
        return False
    for left in range(len(neighbors)):
        if aug(left,set()):continue
        leftset={left};rightset=set();todo=[left]
        while todo:
            v=todo.pop()
            for r in neighbors[v]:
                rightset.add(r)
                if match[r]>=0 and match[r] not in leftset:leftset.add(match[r]);todo.append(match[r])
        need(rightset==set(r for v in leftset for r in neighbors[v]) and len(rightset)<len(leftset),'literalHall deficit')
        return dict(status='HALL_DEFICIT',left_subset=sorted(leftset),neighbor_subset=sorted(rightset))
    assignment=[None]*len(neighbors)
    for r,v in enumerate(match):
        if v>=0:assignment[v]=r
    validate_matching(neighbors,assignment)
    return dict(status='PERFECT_MATCHING',right_by_left=assignment)
def validate_matching(neighbors,assignment):
    need(len(assignment)==len(neighbors) and len(set(assignment))==len(assignment) and all(r in neighbors[v] for v,r in enumerate(assignment)),'literalcomplete bipartite witness')

def controls(h):
    records=[];bad=[row[:] for row in h];bad[0][1]*=-1
    try:validate_h(bad)
    except ValueError:records.append('Hadamard_sign_flip')
    else:raise AssertionError('badH accepted')
    m=[a^1 for a in range(12)];x,l,_=support(h,[m,m,m]);badl=[r[:] for r in l];badl[0][0]^=1
    try:validate_support(x,badl,[m,m,m])
    except ValueError:records.append('support_bit_flip')
    else:raise AssertionError('badL accepted')
    try:core_gram([list(range(12)),m,m])
    except ValueError:records.append('invalid_matching')
    else:raise AssertionError('badmatching accepted')
    positive=bipartite([[0,1],[1,2],[0,2]],3);negative=bipartite([[0],[0],[1,2]],3)
    need(positive['status']=='PERFECT_MATCHING' and negative['status']=='HALL_DEFICIT','tiny bipartite controls')
    for assignment in [[0,0,2],[2,1,0],[0,1]]:
        try:validate_matching([[0,1],[1,2],[0,2]],assignment)
        except ValueError:records.append('bad_matching_witness')
        else:raise AssertionError('badmatching witness accepted')
    return dict(corruptions_rejected=records,bipartite_positive=positive,bipartite_negative=negative,full_research_factor_positive=None,
                full_research_factor_positive_reason='Only supportandprojection positives; fullF is unavailable.')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic();deadline=start+120
    need(digest(GATE)==GH,'connected core gate');pins={key(GATE):GH};cases=[]
    for i,h in enumerate(CORE_PINS):
        p=CORE/f'core_{i:02}.json';need(digest(p)==h,'selected core pin');pins[key(p)]=h;raw=json.loads(p.read_bytes())
        cases.append(dict(name=f'connected_{i:02}',matchings=[raw[f'M{g}'] for g in range(3)],raw_gram=raw['target_gram']))
    m=[a^1 for a in range(12)];cases.append(dict(name='six_prism',matchings=[m,m,m],raw_gram=None))
    for p in [Path(__file__),Path(__file__).with_name('theory_20260930_hadamard20_support_spec.md'),ROOT/'docs/DERIVATION_20260930_HADAMARD20_SUPPORT.md',ROOT/'uv.lock',ROOT/'pyproject.toml']:pins[key(p)]=digest(p)
    created=datetime.now(timezone.utc).isoformat();save(out/'manifest.json',dict(created_at=created,
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),
        inputs_sha256=pins,versions=dict(python=platform.python_version(),uv=subprocess.check_output(['uv','--version'],text=True).strip()),
        selection=[c['name'] for c in cases],limits=dict(seconds=120,solver_calls=0),scope='One deterministicHadamard support per fivefixedidentityPcores; necessarylift projections only.'))
    search=['rg','-n','-i','hadamard.{0,8}20|paley.{0,8}20|paley.{0,20}19|15I.{0,12}15J',
            'external_conway99_research/attempts','docs','--glob','*.md','--glob','*.py','--glob','!**/results/**','--glob','!**/build/**']
    sr=subprocess.run(search,cwd=ROOT,capture_output=True,text=True);(out/'archive_search.stdout.txt').write_text(sr.stdout,encoding='utf-8');(out/'archive_search.stderr.txt').write_text(sr.stderr,encoding='utf-8')
    save(out/'archive_search.json',dict(command=search,exit_code=sr.returncode,scope='Narrow keyword search; no novelty or comprehensiveabsence claim.'))
    residues={x*x%19 for x in range(1,19)}
    def chi(x):return 0 if x%19==0 else 1 if x%19 in residues else -1
    h=[[1]*20]+[[1]+[chi(i-j)-int(i==j) for j in range(19)] for i in range(19)]
    validate_h(h);save(out/'Hadamard20.json',dict(matrix=h,nonconstant_columns_used=list(range(1,7)),quadratic_residues=sorted(residues),literal_orthogonality_entries=400))
    save(out/'controls.json',controls(h));colourwords=[w for w in product(range(3),repeat=6) if all(w.count(g)==2 for g in range(3))];need(len(colourwords)==90,'all90balancedcolours')
    results=[]
    for case in tqdm(cases,desc='Hadamard support screens'):
        need(time.monotonic()<deadline,'120second cap');ms=case['matchings'];c,gram=core_gram(ms)
        if case['raw_gram'] is not None:need(gram==case['raw_gram'],'literal authenticatedcore Gram')
        x,l,blocks=support(h,ms);supports=[[a for a in range(12) if l[a][d]] for d in range(60)]
        need(all(sum(gram[12*g+a][12*h+b] for g,h in product(range(3),repeat=2))==sum(l[a][d]*l[b][d] for d in range(60)) for a,b in product(range(12),repeat=2)),'collapsed rawGram matchesL')
        options=[];capacity=[[0]*36 for _ in range(36)]
        for d,coords in enumerate(supports):
            opts=[];possible=set()
            for colours in colourwords:
                rows=sorted(12*g+a for g,a in zip(colours,coords))
                if any(gram[i][j]==0 for i,j in combinations(rows,2)):continue
                opts.append(dict(fibres_by_sorted_coordinate=list(colours),rows=rows,row_mask_hex=format(sum(1<<i for i in rows),'09x')))
                possible.update((i,j) for i in rows for j in rows)
            for i,j in possible:capacity[i][j]+=1
            options.append(opts)
        deficits=[dict(rows=[i,j],required=gram[i][j],available_column_capacity=capacity[i][j]) for i in range(36) for j in range(i,36) if capacity[i][j]<gram[i][j]]
        capwitness=[];empty_pairs=[]
        for d,e in combinations(range(60),2):
            good=None
            for i,op in enumerate(options[d]):
                a=int(op['row_mask_hex'],16)
                for j,oq in enumerate(options[e]):
                    overlap=(a&int(oq['row_mask_hex'],16)).bit_count()
                    if overlap<=2:good=dict(columns=[d,e],option_indices=[i,j],overlap=overlap);break
                if good is not None:break
            if good is None:empty_pairs.append([d,e])
            else:capwitness.append(good)
        fibres=[]
        for g in range(3):
            catalog=[list(pair) for pair in combinations(range(12),2) if ms[g][pair[0]]!=pair[1]];index={tuple(pair):i for i,pair in enumerate(catalog)}
            neighbors=[sorted({index[tuple(i%12 for i in op['rows'] if i//12==g)] for op in opts}) for opts in options]
            result=bipartite(neighbors,60);fibres.append(dict(fibre=g,nonmatching_catalog=catalog,available_pair_indices_by_column=neighbors,result=result))
        raw=dict(core=case['name'],matchings=ms,core_adjacency=c,prescribed_Gram36=gram,X=x,L=l,matching_blocks=blocks,
            support_columns=supports,support_multiplicities=[dict(support=list(s),multiplicity=n) for s,n in sorted(Counter(map(tuple,supports)).items())],
            column_colour_options=options,Gram_entry_capacities=capacity,Gram_capacity_deficits=deficits,pair_cap_witnesses=capwitness,
            incompatible_column_pairs=empty_pairs,fibre_pair_matching_projections=fibres,
            full_factor=None,full_factor_reason='Independentcolumn/pair/fibre projections have not been made jointly compatible.',target_graph=False)
        p=out/(case['name']+'.json');save(p,raw,compact=True)
        results.append(dict(core=case['name'],artifact=key(p),sha256=digest(p),unique_supports=len(set(map(tuple,supports))),
            duplicate_support_multiplicity_histogram=dict(Counter(Counter(map(tuple,supports)).values())),
            column_option_count_histogram=dict(Counter(map(len,options))),empty_columns=[d for d,o in enumerate(options) if not o],
            Gram_capacity_deficit_count=len(deficits),pair_cap_compatible_pairs=len(capwitness),pair_cap_incompatible_pairs=len(empty_pairs),
            fibre_matching_statuses=[f['result']['status'] for f in fibres]))
    need(time.monotonic()<deadline and all(digest(ROOT/p)==h for p,h in pins.items()),'limits and stableinputs')
    summary=dict(status='CANDIDATE_HADAMARD20_SUPPORT_SCREEN_RESULTS',created_at=created,completed_at=datetime.now(timezone.utc).isoformat(),
        inputs_sha256=pins,outputs_sha256={key(p):digest(p) for p in out.iterdir() if p.is_file()},cases=results,
        exact_support_matrices=5,solver_calls=0,independent_approval=False,target_resolution='UNKNOWN',wall_seconds=time.monotonic()-start,
        limitations=['OnechosenH sixcolumns andendpointorientation percore, notcompletecoverage.','Passingprojections isnotjointcolour feasibility.',
                     'No fullF, D or target graph.','Narrowarchivesearch isnot novelty proof.'])
    save(out/'summary.json',summary);print(json.dumps(dict(summary_sha256=digest(out/'summary.json'),cases=results,wall_seconds=time.monotonic()-start)))

if __name__=='__main__':main()
