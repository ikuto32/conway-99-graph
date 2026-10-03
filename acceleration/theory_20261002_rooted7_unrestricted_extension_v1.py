"""Candidate unrestricted rooted7 primary-nonedge necessary count model.

All2770 already independently enumerated classes; three primary nonedge axes,
varying secondary edge/nonedge aggregate axes and exact prism/mean coupling.
Existing discovery geometry is shared and pinned, not independent approval.
"""
import argparse
from collections import Counter
from datetime import datetime,timezone
from fractions import Fraction
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
import time

from tqdm import tqdm
from command_deadline import CommandDeadline
import theory_20261002_rooted7_extension_model as G

ROOT=G.ROOT;R=ROOT/'acceleration/results'
GEOMETRY_SHA='ac0e8882f5fa72ba3872c8d47fa8e8b1dbcb1c47b9a8016e17f3dacc954e133e'
INPUTS={
 '20261002_rooted7_extension_model/catalogue.json':'a01649d78eccfcb93c85ff2a86c84463458c120fd22cebaf34b8e573363084d5',
 '20261002_rooted7_extension_model/model.json':'21eb899c3606727ef4e452d518316957cf9eb76e5e85c5a79af82421f4004595',
 '20261002_independent_review/rooted7_catalogue01/summary.json':'3355afb38656eadc83eff6e0db3818eded9621f890c9d46f489fdb0324370758',
 '20261002_rooted6_prismfree_rigidity/ordered_nonedge_model.json':'ecf558faa95576b8e76fbc5a62743729a875307eeb99df803c7cb5cdac7b7645',
 '20261002_rooted6_prismfree_rigidity/ordered_edge_model.json':'06051294a142dfcda956f4ee3748986982f7f8ba5f9785fe4d7680d967538584',
 '20261002_rooted6_unrestricted_domain01/domain.json':'dcf63f8a34784fe0a125d52a12423239f72559bfeeb370bc8ccda0b5404c3381',
 '20261002_rooted6_unrestricted_edge_domain01/domain.json':'e2cade276f89c87ece74df8544c99704ce116bb55d84a5bd5e364c6264d75c95',
 '20261002_independent_review/rooted6_unrestricted_domain01/summary.json':'63addcfc02c13b516d3fe379646d5bc82950c2b9444914d668f66b6713529e00',
 '20261002_independent_review/rooted6_unrestricted_domain01/claim_binding.json':'472202b5c6698b797f385a1434246521fae07b10e79c24ed43db402f835323fe',
 '20261002_independent_review/rooted6_unrestricted_edge_domain01/summary.json':'3199d91f6d2c7f7de601584802412bfa86e2c6a5dfeca6fdddef03c7fe8371fe',
 '20261002_independent_review/rooted6_unrestricted_edge_domain01/claim_binding.json':'5100f82b408a74866a7276e2929a4e8f723cb4badbd2bb086800e082a808b2e0',
 '20261002_independent_review/rooted6_means02/summary.json':'ffd497c6afacb9173bcb215eceab7603e7530d18d9c4a51dad6ea0e7d8e1d025',
 '20261002_independent_review/rooted6_means02/universal_claim_binding.json':'f39634de8e150908b4846c0c1959ca7d7c7e73df4b3877399de3875c2a0fecf7'}
PROTOCOL=ROOT/'docs/PROTOCOL_20261002_UNRESTRICTED_ROOTED7_EXTENSION_V1.md'


def tick(deadline):G.need(not deadline.status()['stop_required'],'not completed within allocated budget')


def profiles(data,domain):
    def exact(v):
        x=Fraction(*v)if isinstance(v,list)else Fraction(v);G.need(x.denominator==1,'INTEGER_AFFINE_BASIS');return int(x)
    origin={mask:exact(domain['origin'][j])for j,(h,mask)in enumerate(data['variables'])if h==6}
    basis=[{mask:exact(vector[j])for j,(h,mask)in enumerate(data['variables'])if h==6}for vector in domain['basis']]
    return origin,basis


def reroot(six,seven,cardinalities,edge_origin,edge_basis,nonedge_origin,nonedge_basis,aggregates,deadline):
    rows=[];positions={}
    for anchor in [0,1]:
        for partition in range(4):
            relation='edge'if partition&(1<<anchor)else'nonedge'
            origin,basis=(edge_origin,edge_basis)if relation=='edge'else(nonedge_origin,nonedge_basis)
            for flag,constant in sorted(origin.items()):
                terms=[]
                if aggregates:
                    for coordinate,vector in enumerate(basis):
                        if vector[flag]:terms.append([aggregates[anchor,partition,coordinate],-vector[flag]])
                positions[anchor,partition,flag]=len(rows)
                rows.append(dict(kind='reroot6',anchor=anchor,partition=partition,relation=relation,new_root6mask=flag,terms=terms,known_terms=[],rhs=cardinalities[partition]*constant))
    coefficients=[Counter(dict(row['terms']))for row in rows];known=[Counter()for _ in rows]
    for h,masks in [(6,six),(7,seven)]:
        for index,mask in enumerate(tqdm(masks,desc='unrestricted exact reroot coefficients',mininterval=5)):
            if not index%128:tick(deadline)
            adj=G.graph(h,mask)
            for anchor in [0,1]:
                for marked in range(2,h):
                    partition=int(adj[0]>>marked&1)+2*int(adj[1]>>marked&1)
                    remaining=[u for u in range(h)if u not in[anchor,marked]and(h==6 or u!=1-anchor)]
                    order=[anchor,marked,*remaining];G.need(len(order)==6,'REROOT_UNION_COLLISION_SIZE')
                    flag=G.canonical(6,G.encode(adj,order))[0];row=positions[anchor,partition,flag]
                    if h==6:known[row][mask]+=1
                    else:coefficients[row][index]+=1
    for row,terms,collision in zip(rows,coefficients,known):row['terms']=[[j,c]for j,c in sorted(terms.items())if c];row['known_terms']=[[mask,c]for mask,c in sorted(collision.items())]
    return rows


def aggregate_layout(seven):
    variables=[[7,mask]for mask in seven];aggregates={}
    for anchor in [0,1]:
        for partition in range(4):
            relation='edge'if partition&(1<<anchor)else'nonedge';names=['s','t']if relation=='edge'else['c','a','b']
            for coordinate,name in enumerate(names):aggregates[anchor,partition,coordinate]=len(variables);variables.append(['aggregate',relation,anchor,partition,name])
    return variables,aggregates


def bound_rows(variables,aggregates,cardinalities):
    rows=[]
    for anchor in [0,1]:
        for partition in range(4):
            d=cardinalities[partition];relation='edge'if partition&(1<<anchor)else'nonedge';ids=[aggregates[anchor,partition,q]for q in range(2 if relation=='edge'else 3)]
            facets=[('s_upper',[[ids[0],1]],12*d),('t_upper',[[ids[1],1]],6*d)]if relation=='edge'else[('c_upper',[[ids[0],1]],2*d),('a_upper',[[ids[1],1]],20*d),('b_upper',[[ids[2],2],[ids[0],-1]],18*d)]
            for name,terms,rhs in facets:
                slack=len(variables);variables.append(['aggregate_slack',relation,anchor,partition,name]);rows.append(dict(kind='aggregate_domain_facet',anchor=anchor,partition=partition,relation=relation,facet=name,terms=sorted([*terms,[slack,1]]),known_terms=[],rhs=rhs))
    return rows


def coupling_rows(aggregates,k,n):
    rows=[];G.need(k*(k-2)==2*(n-k-1),'SRG_PARAMETER_MEAN_IDENTITY')
    for anchor in [0,1]:
        nonedges=[p for p in range(4)if not p&(1<<anchor)];edges=[p for p in range(4)if p&(1<<anchor)]
        first=[[aggregates[anchor,p,q],1]for p in nonedges for q in[0,1]]
        second=[[aggregates[anchor,p,0],1]for p in nonedges]+[[aggregates[anchor,p,2],2]for p in nonedges]
        triangle=[[aggregates[anchor,p,0],1]for p in edges]+[[aggregates[anchor,p,0],-1]for p in nonedges]
        matching=[[aggregates[anchor,p,1],2]for p in edges]+[[aggregates[anchor,p,0],-1]for p in nonedges]
        for name,terms,known,rhs in[
            ('almost_triangle_mean',first,[[7100,1],[8024,1]],k*(k-2)),
            ('almost_matching_mean',second,[[7100,1],[15540,2]],2*(n-k-1)),
            ('triangle_prism_incidence',triangle,[[7100,-1]],0),
            ('matching_prism_incidence',matching,[[7100,-1]],0)]:
            rows.append(dict(kind='unrestricted_pervertex_coupling',anchor=anchor,identity=name,terms=sorted(terms),known_terms=known,rhs=rhs,scope='Exact incidences through actual anchor; no uniformity or target automorphism.'))
    return rows


def actual_aggregates(adj,root,six,edge_six,agg,cached):
    vector={};u,v=root
    for anchor in[0,1]:
        for partition in range(4):
            relation='edge'if partition&(1<<anchor)else'nonedge';masks=[8025,15541]if relation=='edge'else[7100,8024,15540]
            selected=[w for w in range(len(adj))if w not in root and((int(adj[u]>>w&1)+2*int(adj[v]>>w&1))==partition)]
            for q,mask in enumerate(masks):
                total=0
                for w in selected:
                    pair=(root[anchor],w)
                    if pair not in cached:cached[pair]=G.actual_counts(adj,list(pair),6,edge_six if relation=='edge'else six)
                    total+=cached[pair][mask]
                vector[agg[anchor,partition,q]]=total
    return vector


def controls(six,seven,edge_six,deadline):
    # Full known-valid lambda1/mu2 rook9, with positive prism counts.
    adj=[0]*9
    for u,v in combinations9():
        if u//3==v//3 or u%3==v%3:adj[u]|=1<<v;adj[v]|=1<<u
    G.need(all(v.bit_count()==4 for v in adj)and all((adj[u]&adj[v]).bit_count()==(1 if adj[u]>>v&1 else 2)for u,v in combinations9()),'ROOK9_EXACT_SRG_CONTROL')
    partitions=dict(Counter(int(adj[0]>>w&1)+2*int(adj[4]>>w&1)for w in range(9)if w not in[0,4]));G.need(partitions=={0:1,1:2,2:2,3:2},'ROOK9_DIRECT_PARTITION_CARDINALITIES')
    variables,agg=aggregate_layout(seven);bounds=bound_rows(variables,agg,partitions);coupling=coupling_rows(agg,4,9)
    extension=G.extension_rows(six,seven,9,4,1,2);cached={};reports=[];all_edges=[];all_nonedges=[]
    for u in range(9):
        for v in range(9):
            if u==v:continue
            tick(deadline);pair=(u,v);relation='edge'if adj[u]>>v&1 else'nonedge';catalogue=edge_six if relation=='edge'else six
            cached[pair]=G.actual_counts(adj,list(pair),6,catalogue)
            (all_edges if relation=='edge'else all_nonedges).append(cached[pair])
    # Uniformity is observed only in this fixture; never assumed in target.
    G.need(all(v==all_edges[0]for v in all_edges)and all(v==all_nonedges[0]for v in all_nonedges),'ROOK9_OBSERVED_LOWER_CONTROL')
    reroot_rows=reroot(six,seven,partitions,all_edges[0],[],all_nonedges[0],[],{},deadline)
    for pair,known in cached.items():
        if adj[pair[0]]>>pair[1]&1:continue
        G.need(dict(Counter(int(adj[pair[0]]>>w&1)+2*int(adj[pair[1]]>>w&1)for w in range(9)if w not in pair))==partitions,'EVERY_ROOK9_DIRECT_PARTITION_CARDINALITY')
        count=G.actual_counts(adj,list(pair),7,seven);vector=[count[mask]for mask in seven]+[0]*(len(variables)-len(seven));values=actual_aggregates(adj,pair,six,edge_six,agg,cached)
        for j,v in values.items():vector[j]=v
        for row in bounds:
            slack=row['terms'][-1][0];G.need(variables[slack][0]=='aggregate_slack','FIXTURE_SLACK_ORDER')
            vector[slack]=row['rhs']-sum(c*vector[j]for j,c in row['terms']if j!=slack)
        G.need(min(vector)>=0 and all(G.residual(row,vector,known)==0 for row in [*extension,*reroot_rows,*bounds,*coupling]),'ALL_ROOK9_EXACT_GEOMETRY_AND_MEAN_ROWS')
        reports.append(dict(root=list(pair),c=known[7100],a=known[8024],b=known[15540],full_extension_rows=len(extension),full_reroot_rows=len(reroot_rows),aggregate_bound_rows=len(bounds),global_coupling_rows=len(coupling)))
    G.need(len(reports)==36 and len(all_edges)==36,'ROOK9_COMPLETE_ORDERED_PAIR_CONTROL_POPULATION')
    pair=(0,4);known=cached[pair];count=G.actual_counts(adj,list(pair),7,seven);vector=[count[mask]for mask in seven]
    bad=vector[:];bad[0]+=1;G.need(any(G.residual(row,bad,known)for row in extension),'CORRUPT_ROOT7_COUNT_CONTROL')
    changed=dict(known);changed[7100]+=1;G.need(any(G.residual(row,vector,changed)for row in extension),'CORRUPT_PRISM_LOWER_COUNT_CONTROL')
    row=next(row for row in extension if any(vector[j]for j,c in row['terms']));j,c=next((j,c)for j,c in row['terms']if vector[j]);changed=json.loads(json.dumps(row));changed['terms'][changed['terms'].index([j,c])][1]+=1
    G.need(G.residual(changed,vector,known)!=0,'GENUINE_CORRUPT_COEFFICIENT_CONTROL')
    changed=json.loads(json.dumps(row));changed['rhs']+=1;G.need(G.residual(changed,vector,known)!=0,'CORRUPT_RHS_CONTROL')
    return dict(rook9_adjacency_bitmasks=adj,ordered_primary_nonedge_roots=reports,all72lower_pair_roots_directly_counted=True,fixture_edge_prism_counts=dict(s=all_edges[0][8025],t=all_edges[0][15541]),producer_calibration_only=True,fixture_target_affine_origin_used=False,corrupted_controls_rejected=['root7count','lowerprismcount','genuine_nonzero_coefficient','rhs'])


def combinations9():
    return[(u,v)for u in range(9)for v in range(u+1,9)]


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();deadline=CommandDeadline(args.seconds,allocation_reason='Previousconditionalroot7model2.453s; modest20class/12aggregategrowth and72rook controls;180outer150worker30reserve, no solver');started=time.monotonic();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={}
    try:
        G.need(G.sha(G.__file__)==GEOMETRY_SHA,'FROZEN_SHARED_DISCOVERY_GEOMETRY')
        for path,wanted in INPUTS.items():G.need(G.sha(R/path)==wanted,'FROZEN_INPUT '+path);pins[(R/path).relative_to(ROOT).as_posix()]=wanted
        for path in [Path(__file__),Path(G.__file__),PROTOCOL,ROOT/'docs/DESIGN_20261002_UNRESTRICTED_ROOTED7_EXTENSION_V2.md',ROOT/'acceleration/command_deadline.py',ROOT/'acceleration/run_compute_command.py',ROOT/'uv.lock',ROOT/'pyproject.toml']:pins[path.relative_to(ROOT).as_posix()]=G.sha(path)
        G.save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256=pins,python_version=platform.python_version(),question='Can the complete unrestricted localroot6 profiles extend to exact rooted7 marked/reroot/mean constraints?',selection='All2770 independentlyenumeratedroot7classes; primary651(c,a,b)profiles/eightcorners; all secondaryedge/nonedgeprofiles allowed to vary, no common secondaryprofile.',success='Complete exact sparse necessary operator with4affineRHScomponents,2810variables11769rows, independent reviewpending; source controls and allrawprimal/kernel sanitychecks.',falsification='Any coefficient/control/domain/reroot collision discrepancy vetoes use; preserve failure, no automaticretry.',independent_requirement='Different author reconstructs allmarked/reroot/aggregate/coupling coefficients and necessities, plus domain dependencies, before exclusion promotion.',scope='Unrestricted necessary count model only; no graph, automorphism, fixedcommonsecondaryprofile or rank claim.',shared_discovery_geometry='Existing frozen helper ac0e8882..., producer calibration is not independent verification.'))
        catalog=G.read(R/'20261002_rooted7_extension_model/catalogue.json');seven=catalog['complete_locally_admissible_masks'];G.need(len(seven)==2770 and len(catalog['prismfree_masks'])==2750,'FULL_ROOT7_CATALOGUE_POPULATION')
        nd=G.read(R/'20261002_rooted6_prismfree_rigidity/ordered_nonedge_model.json');ed=G.read(R/'20261002_rooted6_prismfree_rigidity/ordered_edge_model.json');nonedge_domain=G.read(R/'20261002_rooted6_unrestricted_domain01/domain.json');edge_domain=G.read(R/'20261002_rooted6_unrestricted_edge_domain01/domain.json')
        six=[mask for h,mask in nd['variables']if h==6];edge_six=[mask for h,mask in ed['variables']if h==6];nonedge_origin,nonedge_basis=profiles(nd,nonedge_domain);edge_origin,edge_basis=profiles(ed,edge_domain)
        G.need(len(six)==456 and len(edge_six)==307 and len(nonedge_basis)==3 and len(edge_basis)==2,'COMPLETE_LOWER_AFFINE_SHAPES')
        for data,dom in [(nd,nonedge_domain),(ed,edge_domain)]:
            origin=[Fraction(*v)if isinstance(v,list)else Fraction(v)for v in dom['origin']];basis=[[Fraction(*v)if isinstance(v,list)else Fraction(v)for v in vec]for vec in dom['basis']]
            G.need(all(sum(c*origin[j]for j,c in row['terms'])==row['rhs']for row in data['equations'])and all(all(sum(c*vec[j]for j,c in row['terms'])==0 for row in data['equations'])for vec in basis),'EVERY_LOWER_AFFINE_RAW_ROW')
        G.save(out/'producer_controls.json',controls(six,seven,edge_six,deadline));tick(deadline)
        variables,agg=aggregate_layout(seven);cardinalities={0:71,1:12,2:12,3:2};rows=G.extension_rows(six,seven,99,14,1,2);tick(deadline)
        rows+=reroot(six,seven,cardinalities,edge_origin,edge_basis,nonedge_origin,nonedge_basis,agg,deadline);rows+=bound_rows(variables,agg,cardinalities);rows+=coupling_rows(agg,14,99)
        equations=[]
        for row in rows:
            rhs=[row['rhs']-sum(c*nonedge_origin[mask]for mask,c in row['known_terms'])]
            rhs += [-sum(c*vec[mask]for mask,c in row['known_terms'])for vec in nonedge_basis]
            equations.append(dict(terms=row['terms'],rhs_affine=rhs))
        G.need(len(variables)==2810 and len(rows)==11769,'DECLARED_OPERATOR_DIMENSIONS')
        corners=[[int(Fraction(*v))for v in p]for p in nonedge_domain['vertices']];G.need(len(corners)==8,'EIGHT_EXACT_PRIMARY_CORNERS')
        model=dict(format='ROOTED7_UNRESTRICTED_EXTENSION_AFFINE_MODEL_V1',variables=variables,equations=equations,row_derivation_descriptors=rows,affine_RHS_coordinate_order=['constant','c','a','b'],parameter_domain=dict(c=[0,2],a=[0,20],b='0<=2b<=18+c',complete_integer_profiles=nonedge_domain['integer_points'],rational_vertices=corners),parameters='Actual primary nonedge rooted6 counts masks7100,8024,15540; secondary coordinates vary per pair and are aggregated.',root6_nonedge_profile_basis=dict(origin=nonedge_origin,basis=nonedge_basis),root6_edge_profile_basis=dict(origin=edge_origin,basis=edge_basis),secondary_aggregate_partition_cardinalities=cardinalities,feasible_domain='Every variable nonnegative INTEGER for actual graph counts; numerical/rational relaxation must be labelled separately.',assumptions='Finite simple srg(99,14,1,2); no prism-free premise or target automorphism; known exact local domain/mean dependencies need independent audit.',dependencies=[dict(id='C-UNRESTRICTED-ORDERED-PAIR-ROOTED5-RIGIDITY',revision=1,relation='uses_result'),dict(id='C-UNRESTRICTED-ROOTED6-NONEDGE-NECESSARY-SYSTEM-NULLSPACE',revision=1,relation='uses_result'),dict(id='C-UNRESTRICTED-ROOTED6-NONEDGE-INTEGER-DOMAIN',revision=1,relation='uses_result'),dict(id='C-UNRESTRICTED-ROOTED6-PER-VERTEX-GLOBAL-PRISM-MEAN-IDENTITIES',revision=1,relation='uses_result')],pending_dependencies=['Unrestricted edge exact kernel/domain independent check','New prism coordinate/edge incidence double-count verification','New full model coefficient/necessity verification'],scope='Complete unrestricted rooted7 necessary count operator candidate; no graph realization, integer feasibility, rank or unrestricted resolution.')
        model['dependencies'].append(dict(id='C-UNRESTRICTED-ROOTED6-EDGE-KERNEL-INTEGER-DOMAIN',revision=1,relation='uses_result'))
        model['pending_dependencies']=['New prism coordinate/edge incidence double-count verification','New full model coefficient/necessity verification']
        G.save(out/'model.json',model);G.save(out/'eight_primary_corners.json',dict(coordinate_order=['c','a','b'],corners=corners,scope='Rational vertices of localnecessary domain, not graph candidates; no solver attempts.'))
        summary=dict(status='CANDIDATE_UNRESTRICTED_ROOTED7_NECESSARY_OPERATOR',timestamp=datetime.now(timezone.utc).isoformat(),variables=len(variables),rows=len(rows),terms=sum(len(r['terms'])for r in equations),root7classes=len(seven),primary_integer_profiles=len(nonedge_domain['integer_points']),rational_primary_corners=8,secondary_aggregate_variables=20,aggregate_slacks=20,row_type_counts=dict(Counter(r['kind']for r in rows)),solver_attempts=0,independent_review=None,independent_review_reason='New exact encoding/coverage/dependency audit pending.',elapsed_seconds=time.monotonic()-started,deadline=deadline.status(),target_resolution=False,overall_search_coverage='UNKNOWN; no validated denominator.',outputs_sha256={p.relative_to(ROOT).as_posix():G.sha(p)for p in out.iterdir()if p.is_file()})
        G.save(out/'summary.json',summary);print(json.dumps(summary))
    except BaseException as error:G.save(out/'failure.json',dict(error=repr(error),elapsed_seconds=time.monotonic()-started,outputs_preserved=True));raise


if __name__=='__main__':main()
