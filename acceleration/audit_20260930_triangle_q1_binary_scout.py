"""Independent raw binary factors, restricted coordinate orbits, and row trees.

No producer imports. Reuses only the hash-pinned independent row-certificate
checker, including its counterfactual forcing checks, with explicit disclosure.
"""
from __future__ import annotations
import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations, permutations
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_triangle_q1_binary_scout/'
PIN='85e705cc6c2a14d123120c93a847e30aaab1789e'
HELPER='acceleration/audit_20260930_triangle_row29_obstruction.py'
HELPER_SHA='109671d882976ab68b350883340f3f0d7437571caa56b01d56a875f7897c4730'
def h(p):return sha256(Path(p).read_bytes()).hexdigest()
if h(ROOT/HELPER)!=HELPER_SHA:raise ValueError('frozen independent tree-checker changed')
from audit_20260930_triangle_row29_obstruction import check_tree, reconstruct, calibration

def need(ok,msg):
    if not ok:raise ValueError(msg)
def load(p):return json.loads((ROOT/p).read_bytes())
def save(p,data):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(data,f,indent=2);f.write('\n')
def ch(obj):return sha256(json.dumps(obj,separators=(',',':')).encode()).hexdigest()
E=[(a,b)for a,b in combinations(range(12),2)if b!=a^1]
EI={edge:i for i,edge in enumerate(E)}

def raw_scope(q):
    need(len(q)==60 and all(type(x)is int for x in q)and sorted(q)==list(range(60)),'Q1 permutation')
    a=[[0]*99 for _ in range(99)]
    def edge(x,y,state=1):need(x!=y,'no loop');a[x][y]=a[y][x]=state
    for x,y in combinations(range(3),2):edge(x,y)
    for i in range(3):
        for j in range(12):edge(i,3+12*i+j);edge(3+12*i+j,3+12*i+(j^1))
    for j in range(12):edge(3+j,15+j);edge(3+j,27+j);edge(15+j,27+(j+6)%12)
    for d,e in enumerate(E):
        for u in e:edge(3+u,39+d)
        for u in E[q[d]]:edge(15+u,39+d)
        for u in range(27,39):edge(u,39+d,-1)
    for x,y in combinations(range(39,99),2):edge(x,y,-1)
    return a

def verify_factor(q):
    a=raw_scope(q)
    inner=[r[3:39]for r in a[3:39]]
    # The entire prescribed Gram is independently derived from the raw39 core
    # block of A^2=12I-A+2J, rather than the producer's explicit G01 formula.
    target=[[12*int(i==j)-inner[i][j]-sum(inner[i][k]*inner[k][j]for k in range(36))
             +2-int(i//12==j//12) for j in range(24)]for i in range(24)]
    incidence=[a[i][39:]for i in range(3,27)]
    need(all(sum(row)==10 for row in incidence),'row degrees ten')
    need(all(sum(incidence[12*g+i][d]for i in range(12))==2 for g in [0,1]for d in range(60)),'two per cell per column')
    actual=[[sum(x*y for x,y in zip(r,s))for s in incidence]for r in incidence]
    need(actual==target,'full576 exact prescribed Gram entries')
    need(all(sum(x==1 for x in row)<=14<=sum(x!=0 for x in row)for row in a),'raw99 degree feasibility intervals')
    for i,j in combinations(range(99),2):
        common=sum(a[i][k]==a[j][k]==1 for k in range(99))
        need(common<=(1 if a[i][j]==1 else 2),'raw99 known common cap')
    need(sum(a[i][j]==-1 for i,j in combinations(range(99),2))==2490,'C2 plus D unknown population')
    return a,incidence,target

def coordinate_group(target):
    full=[];group=[]
    for p6 in permutations(range(6)):
        for mask in range(64):
            p=[]
            for i,j in enumerate(p6):
                x=2*j+((mask>>i)&1);p.extend([x,x^1])
            full.append(tuple(p))
            if all(p[(x+6)%12]==(p[x]+6)%12 for x in range(12)):group.append(p)
    need(len(full)==len(set(full))==46080,'complete centralizer of M')
    need(len(group)==len({tuple(p)for p in group})==384,'complete joint centralizer order')
    rows=[];c0=[[int(i in e)for e in E]for i in range(12)]
    for p in group:
        need(sorted(p)==list(range(12))and all(p[x^1]==p[x]^1 for x in range(12)),'M-preserving permutation')
        ep=[EI[tuple(sorted((p[x],p[y])))]for x,y in E]
        need(sorted(ep)==list(range(60)),'induced edge permutation')
        need(all(c0[p[i]][ep[d]]==c0[i][d]for i in range(12)for d in range(60)),'literal canonical C0 incidence covariance')
        p24=p+[12+x for x in p]
        need(all(target[p24[i]][p24[j]]==target[i][j]for i in range(24)for j in range(24)),'prescribed Gram invariance')
        rows.append(dict(vertices=p,columns=ep))
    return rows

def orbit(q,maps):
    images=set()
    for m in maps:
        p=m['columns'];transformed=[None]*60
        for i in range(60):transformed[p[i]]=p[q[i]]
        # Equivalent literal incidence covariance: C1'[p(a),pE(d)]=C1[a,d].
        for a in range(12):
            for d in range(60):
                need((m['vertices'][a]in E[transformed[p[d]]])==(a in E[q[d]]),'literal C1 image convention')
        images.add(tuple(transformed))
    return images

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);args=parser.parse_args()
    out=ROOT/args.out;out.mkdir(parents=True,exist_ok=False);start=time.monotonic();inputs={}
    def bind(path,expected=None):
        got=h(ROOT/path);need(expected is None or got==expected,'input hash '+path);inputs[path]=got
    bind(B+'summary.json','a10fbfec83f8b5707e5664103ee271d5cd4151312727add008adaa4ebfcd2da8')
    summary=load(B+'summary.json')
    for path,expected in summary['output_hashes'].items():bind(path,expected)
    for path,expected in load(B+'manifest.json')['input_hashes'].items():bind(path,expected)
    bind(HELPER,HELPER_SHA)
    gate='acceleration/results/20260930_independent_review/triangle_wave154_row29_obstruction/summary.json'
    bind(gate,'43b81ed2aef9cde8b600cb6981455cdec69a84bb1961aa08ecb68a1248ba5fb9')
    bind(B+'supplemental_row_controls.json')
    save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
         command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),inputs_sha256=dict(inputs),
         question='Are the three supplied Q1 factors exact prescribed-Gram factors, inequivalent under the exact384 coordinate maps, and each unable to supply row27?',
         success='All full raw factor/matrix equations, all coordinate maps/images, every tree implication and both branches checked exactly.',
         limits=dict(seconds=120),numerical_thresholds=None,numerical_thresholds_null_reason='Exact integer, set and tree checking.'))
    controls,_=calibration();save(out/'tree_controls.json',controls)
    archived=[];refs=[]
    for path,key in [('attempts/wave151-triangle-root-factor/exact-results.json','exact_partial_factor'),
                     ('attempts/wave154-triangle-factor-portfolio/exact-results.json','second_exact_Q1_representative')]:
        command=['git','-C','external_conway99_research','show',PIN+':'+path]
        raw=subprocess.check_output(command,cwd=ROOT)
        need(raw==(ROOT/'external_conway99_research'/path).read_bytes(),'immutable archive factor bytes')
        archived.append(json.loads(raw)[key]['Q1'])
        refs.append(dict(repository='https://github.com/YesterdaysLemon/conway-99-research',commit=PIN,path=path,
                         json_key=key+'.Q1',sha256=sha256(raw).hexdigest(),command=command))
    raw_factors=[load(B+f'factor_{i:02d}.json')for i in range(3)]
    allq=archived+[r['Q1']for r in raw_factors];checked=[verify_factor(q)for q in allq]
    # Freshly checked old raw factors are positive controls, not historical label imports.
    corrupt=archived[0].copy();corrupt[0],corrupt[1]=corrupt[1],corrupt[0]
    try:verify_factor(corrupt)
    except ValueError:pass
    else:raise ValueError('swapped-image factor accepted')
    corrupt=archived[0].copy();corrupt[1]=corrupt[0]
    try:verify_factor(corrupt)
    except ValueError:pass
    else:raise ValueError('duplicate-image factor accepted')
    maps=coordinate_group(checked[0][2]);save(out/'all384_coordinate_maps.json',maps)
    previous=set();orbits=[]
    for i,q in enumerate(allq):
        images=orbit(q,maps);need(not previous&images,'five coordinate orbits are disjoint');previous|=images
        sorted_images=[list(row)for row in sorted(images)]
        save(out/f'orbit_{i:02d}.json',dict(input_Q1=q,members=sorted_images,coordinate_group_order=384))
        if i>=2:need(raw_factors[i-2]['coordinate_orbit_size']==len(images),'producer coordinate orbit size')
        orbits.append(dict(factor=i,scope='archived'if i<2 else'new',orbit_size=len(images),canonical=sorted_images[0],
                           all_images_sha256=h(out/f'orbit_{i:02d}.json')))
    # A noncommuting signed-coordinate map and a corrupt induced edge permutation
    # are rejected by the literal preservation conditions, independent of names.
    invalid=list(range(12));invalid[0],invalid[1]=invalid[1],invalid[0]
    need(any(invalid[(i+6)%12]!=(invalid[i]+6)%12 for i in range(12)),'wrong coordinate group negative')
    invalid=deepcopy(maps[0]);invalid['columns'][0]=invalid['columns'][1]
    need(sorted(invalid['columns'])!=list(range(60)),'wrong edge map negative')
    records=[];rejected=[]
    for i,item in enumerate(raw_factors):
        need(time.monotonic()-start<120,'audit time cap')
        need(item['index']==i,'factor identity');a,incidence,target=checked[i+2]
        rawpath=B+f'factor_{i:02d}_rows/raw99.json';raw=load(rawpath)
        need(raw['Q1']==item['Q1']and raw['known_adjacency']==a,'literal raw99 assembly')
        rowpath=B+f'factor_{i:02d}_rows/row_27.json';row=load(rowpath)
        variables,constraints=reconstruct(a,27,list(range(3,27)))
        need(row['vertex']==27 and row['variables']==variables and row['constraints']==constraints,'all raw row constraints reconstructed')
        kinds=Counter(c['kind']for c in constraints)
        need(len(variables)==60 and variables==list(range(39,99))and kinds=={'degree':1,'exact_common':24,'incompatible_pair':108},'row scope counts')
        verified=check_tree(60,constraints,row['proof'],record=True)
        need(verified['sat_leaves']==0 and verified['nodes']==[167,321,167][i],'complete UNSAT tree population')
        save(out/f'factor_{i:02d}_tree_check.json',verified)
        save(out/f'factor_{i:02d}_raw_check.json',dict(Q1=item['Q1'],incidence24x60=incidence,prescribed_Gram24x24=target,
                                                    known_adjacency99=a,variables=variables,constraints=constraints))
        # Changed actual raw graph must be detected by independent assembly.
        bad=deepcopy(raw);bad['known_adjacency'][15][39]^=1;bad['known_adjacency'][39][15]=bad['known_adjacency'][15][39]
        need(bad['known_adjacency']!=a,'raw scope corruption rejection');rejected.append(f'factor{i}_changed_raw_edge')
        tree=row['proof'];f=next(j for j,n in enumerate(tree['nodes'])if n['forces']);leaf=next(j for j,n in enumerate(tree['nodes'])if n['status']=='CONFLICT')
        corruptions={}
        bad=deepcopy(tree);bad['nodes'][tree['root']]['children'].pop();corruptions['missing_branch']=bad
        bad=deepcopy(tree);bad['nodes'][f]['forces'][0]['value']^=1;corruptions['wrong_force']=bad
        bad=deepcopy(tree);bad['nodes'][leaf]['ones']+=1;corruptions['false_conflict_counter']=bad
        for label,bad in corruptions.items():
            try:check_tree(60,constraints,bad)
            except ValueError:rejected.append(f'factor{i}_{label}')
            else:raise ValueError('accepted bad tree '+label)
        record=dict(factor=i,factor_sha256=inputs[B+f'factor_{i:02d}.json'],raw99_sha256=inputs[rawpath],
                    row_certificate_sha256=inputs[rowpath],Gram_entries_checked=576,known_pair_caps_checked=4851,
                    constraints=dict(degree=1,degree_quota=10,exact_common=24,incompatible_pair=108),
                    tree={k:v for k,v in verified.items()if k!='receipts'},outcome='NO_VALID_ROW27')
        records.append(record)
    save(out/'corruption_controls.json',dict(factor_swapped_image_rejected=True,factor_duplicate_image_rejected=True,
         noncommuting_coordinate_map_rejected=True,corrupted_induced_map_rejected=True,actual_raw_and_tree_rejections=rejected))
    generation=load(B+'generation.json')
    need(generation['heuristic_attempted_swaps']==512000 and generation['heuristic_zero_hits']==0,'historical failed heuristic record')
    for path,expected in list(inputs.items()):bind(path,expected)
    for path in [Path(__file__).relative_to(ROOT).as_posix(),'docs/AUDIT_20260930_TRIANGLE_Q1_BINARY_SCOUT.md']:bind(path)
    result=dict(status='INDEPENDENT_THREE_Q1_FACTORS_AND_ROW27_EXCLUSIONS_PASS',timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),
        python=platform.python_version(),verifier='/root/state_literature_audit independent raw factor and proof checking agent',
        inputs_sha256=inputs,archive_references=refs,records=records,coordinate_orbits=orbits,
        claims=[dict(id='C-FIXED-TRIANGLE-THREE-Q1-GRAM-FACTORS',revision=1,recommendation='VERIFIED',kind='construction',basis=['COMPUTED'],
                     statement='Each of the three exact saved Q1 permutations gives a binary24by60 two-cell incidence factor with row sums10, two ones per cell per column, and all576 entries of its Gram equal to the prescribed fixed-core24by24 Gram.',
                     scope='Three finite binary factors for the specified M0=M1=M2 and P=shift6 core; no third incidence cell or target extension.',dependencies=[]),
                dict(id='C-FIXED-TRIANGLE-Q1-FIVE-COORDINATE-ORBITS',revision=1,recommendation='VERIFIED',kind='mathematical result',basis=['DERIVED','COMPUTED'],
                     statement='The two pinned archived Q1 permutations and the three saved new Q1 permutations belong to five pairwise disjoint orbits under all384 simultaneous label permutations commuting with the standard matching and shift6, with the canonical C0 column relabeling induced on its60 distinct edges.',
                     scope='Only this explicitly defined complete384-element coordinate group and five raw factors; no classification of all factors or arbitrary target isomorphisms.',
                     dependencies=[dict(id='C-FIXED-TRIANGLE-THREE-Q1-GRAM-FACTORS',revision=1,relation='uses_result')]),
                dict(id='C-FIXED-TRIANGLE-THREE-Q1-ROW27-EXCLUSIONS',revision=1,recommendation='VERIFIED',kind='exclusion',basis=['DERIVED','COMPUTED'],
                     statement='For each of the three specified Q1 factors with the fixed triangle core and canonical C0, no Boolean assignment to the60 unknown row27 edges satisfies its necessary degree10,24 exact common-neighbor equations and108 known-pair incompatibilities. None of these three exact fixed factors extends to an srg(99,14,1,2).',
                     scope='Three raw fixed configurations, each independently assembled without propagation; no exclusion of all Q1 factors or of the fixed core.',
                     dependencies=[dict(id='C-FIXED-TRIANGLE-THREE-Q1-GRAM-FACTORS',revision=1,relation='uses_result')])],
        sharing=dict(producer_imports=False,independent_helper_path=HELPER,independent_helper_sha256=HELPER_SHA,
                     description='Frozen independent counterfactual-force/tree checker and raw row-constraint reconstruction reused; no producer search, factor validator, row scorer or orbit code imported.'),
        historical_failed_search=dict(path=B+'generation.json',sha256=inputs[B+'generation.json'],recorded_attempted_swaps=512000,
                                      recorded_zero_hits=0,recorded_final_score=generation['heuristic_final_exact_score'],independently_reexecuted=False,
                                      scope='Saved heuristic failure retained as provenance only; no search coverage or performance claim.'),
        counts=dict(new_factors_checked=3,archived_positive_factors_freshly_checked=2,Gram_entries_new_factors=1728,
                    complete_coordinate_maps=384,full_match_preserving_permutations_tested=46080,distinct_checked_coordinate_orbits=5,
                    complete_empty_row_certificates=3,tree_nodes=sum(r['tree']['nodes']for r in records),
                    splits=sum(r['tree']['splits']for r in records),conflict_leaves=sum(r['tree']['conflict_leaves']for r in records)),
        target_resolution=False,external_review=False,artifact_availability='LOCAL_ONLY',artifact_availability_reason='All raw factors, maps, orbit images, exact trees and independent receipts retained locally; parent controls publication.',
        elapsed_seconds=time.monotonic()-start,
        limitations=['No nontrivial target automorphism is assumed.',
                     'All384 maps are label changes preserving this fixed core, not assumed symmetries of an unknown completed graph.',
                     'Pairwise inequivalence under this restricted group is not a general graph nonisomorphism claim.',
                     'Three fixed exclusions do not cover the unknown full factor population.',
                     'Producer trade-search and annealing counts are preserved but not replayed as independently verified claims.',
                     'The joint_model_size artifact is hashed for provenance only; its encoding/count correctness is outside this audit.'])
    result['audit_artifact_hashes']={p.relative_to(ROOT).as_posix():h(p)for p in sorted(out.iterdir())if p.is_file()}
    save(out/'summary.json',result);print(json.dumps({'status':result['status'],'summary_sha256':h(out/'summary.json'),'counts':result['counts']}))

if __name__=='__main__':main()
