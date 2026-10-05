"""Independent derivation and raw coefficient/kernel checks; no producer imports."""
import argparse
import copy
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'acceleration/results/20260930_triangle39_gram_sos'
SUMMARY_SHA='23950ec095c3c9b4b127da12755a902f0ed4c9a26a0e36a02e0ab3333ef4e38b'
def need(ok,message):
    if not ok:raise ValueError(message)
def digest(path):
    with path.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(path):return json.loads(path.read_bytes())

def rank(matrix):
    a=[[Fraction(x)for x in row]for row in matrix];r=0
    for col in range(len(a[0])):
        chosen=next((i for i in range(r,len(a))if a[i][col]),None)
        if chosen is None:continue
        a[r],a[chosen]=a[chosen],a[r]
        pivot=a[r][col];a[r]=[value/pivot for value in a[r]]
        for i in range(r+1,len(a)):
            multiplier=a[i][col]
            if multiplier:a[i]=[x-multiplier*y for x,y in zip(a[i],a[r])]
        r+=1
        if r==len(a):break
    return r

def check_record(record):
    ms,p=record['matchings'],record['permutation']
    need(len(ms)==3 and all(len(m)==12 and all(type(v)is int for v in m)and sorted(m)==list(range(12))
         and all(m[i]!=i and m[m[i]]==i for i in range(12))for m in ms),'valid matchings')
    need(len(p)==12 and all(type(v)is int for v in p)and sorted(p)==list(range(12)),'valid permutation')
    edges={frozenset(pair)for pair in itertools.combinations(range(3),2)}
    for i in range(3):
        for j in range(12):
            edges.add(frozenset((i,3+12*i+j)))
            edges.add(frozenset((3+12*i+j,3+12*i+ms[i][j])))
    for j in range(12):
        for pair in [(3+j,15+j),(3+j,27+j),(15+j,27+p[j])]:edges.add(frozenset(pair))
    adjacency=[[int(i!=j and frozenset((i,j))in edges)for j in range(39)]for i in range(39)]
    need(record['adjacency39']==adjacency,'literal core adjacency')
    remaining=set(range(3,39));comps=[]
    while remaining:
        comp={min(remaining)}
        while True:
            larger=comp|{j for i in comp for j in remaining if adjacency[i][j]}
            if larger==comp:break
            comp=larger
        remaining-=comp;comps.append(sorted(i-3 for i in comp))
    need(record['inner_components']==comps,'connected components')
    need(all(len(set(c)&set(range(12*i,12*i+12)))==len(c)//3 and len(c)//3%2==0
         for c in comps for i in range(3)),'balanced even component sizes')
    c=len(comps);need(1<=c<=6,'component count')
    counts={}
    for kind in ['G','Q']:
        matrix=[[(27*int(i==j)-9*adjacency[i][j]+1)if kind=='G'else (adjacency[i][j]+4*int(i==j))
                 for j in range(39)]for i in range(39)]
        need(record[kind]==matrix,'literal '+kind+' matrix')
        forms=record[kind+'_scaled144_SOS']
        need(all(type(f['weight'])is int and f['weight']>0 and len(f['coefficients'])==39
                 and all(type(x)is int for x in f['coefficients'])for f in forms),'positive exact SOS factors')
        for i in range(39):
            for j in range(i,39):
                total=sum(f['weight']*f['coefficients'][i]*f['coefficients'][j]for f in forms)
                need(total==144*matrix[i][j],'complete rational coefficient identity '+kind)
        basis=record[kind+'_kernel_basis'];dimension=c+2 if kind=='G'else 2
        need(len(basis)==dimension and all(len(v)==39 for v in basis),'kernel dimensions')
        need(all(sum(row[j]*v[j]for j in range(39))==0 for row in matrix for v in basis),'kernel annihilation')
        need(rank(basis)==dimension,'independent rational basis rank')
        actual=rank(matrix)
        need(actual==39-dimension==record[kind+'_rank_over_Q'],'independent rational matrix rank')
        counts[kind]=actual
    return dict(name=record['name'],components=c,ranks=counts,independent_upper_triangle_coefficients_checked=1560)

def quotient_control():
    # Completely independent scalar formulas; polarization recovers all 21 coefficients.
    def literal(v,kind):
        r=v[:3];b=v[3:];R=sum(r);B=sum(b)
        norm=sum(x*x for x in r)+12*sum(x*x for x in b)
        adjacency=R*R-sum(x*x for x in r)+24*sum(x*y for x,y in zip(r,b))+12*B*B
        return 27*norm-9*adjacency+(R+12*B)**2 if kind=='G'else 4*norm+adjacency
    def squares(v,kind):
        r=v[:3];b=v[3:];R=sum(r);B=sum(b)
        if kind=='Q':return 3*sum((r[i]+4*b[i])**2 for i in range(3))+R*R+12*B*B
        return 36*sum((r[i]-R/3-3*(b[i]-B/3))**2 for i in range(3))+4*(R-6*B)**2
    count=0
    for kind in ['G','Q']:
        for i in range(6):
            for j in range(i,6):
                v=[Fraction(0)]*6;v[i]+=1;v[j]+=1
                need(literal(v,kind)==squares(v,kind),'universal six-variable quotient coefficient')
                count+=1
    return count

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);args=parser.parse_args()
    out=ROOT/args.out;out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    need(digest(RUN/'summary.json')==SUMMARY_SHA,'frozen candidate report')
    summary=read(RUN/'summary.json');inputs={}
    for name,expected in {**summary['inputs_sha256'],**summary['artifact_hashes']}.items():
        need(digest(ROOT/name)==expected,'unchanged raw input '+name);inputs[name]=expected
    inputs[(RUN/'summary.json').relative_to(ROOT).as_posix()]=SUMMARY_SHA
    records=[]
    for row in summary['records']:
        path=RUN/(row['name']+'.json');need(digest(path)==row['sha256'],'fixture identity')
        records.append(check_record(read(path)))
    need(len(records)==15 and {r['components']for r in records}==set(range(1,7)),'all declared finite controls')
    quotient=quotient_control()
    need(rank([[0,0],[0,0]])==0 and rank([[0,2],[3,0]])==2 and rank([[1,2],[2,4]])==1,'independent rank controls')
    bads=[];base=read(RUN/'components_1.json')
    mutations=[
        ('nonmatching',lambda r:r['matchings'][0].__setitem__(0,0)),
        ('nonpermutation',lambda r:r['permutation'].__setitem__(0,r['permutation'][1])),
        ('wrong_graph_edge',lambda r:r['adjacency39'][0].__setitem__(1,0)),
        ('wrong_G_diagonal',lambda r:r['G'][0].__setitem__(0,r['G'][0][0]-1)),
        ('wrong_Q_offdiagonal',lambda r:r['Q'][0].__setitem__(1,0)),
        ('negative_SOS_weight',lambda r:r['G_scaled144_SOS'][0].update(weight=-9)),
        ('wrong_SOS_coefficient',lambda r:r['Q_scaled144_SOS'][0]['coefficients'].__setitem__(3,0)),
        ('wrong_kernel_vector',lambda r:r['G_kernel_basis'][0].__setitem__(0,99)),
        ('wrong_component_partition',lambda r:r['inner_components'][0].pop()),
        ('wrong_reported_rank',lambda r:r.update(Q_rank_over_Q=38)),
    ]
    for name,change in mutations:
        r=copy.deepcopy(base);change(r)
        try:check_record(r)
        except ValueError:bads.append(name)
        else:raise AssertionError('accepted corruption '+name)
    # Independently authenticate the cited archive version/paths, without importing any historical status.
    overlap=read(RUN/'archive_overlap.json');archived=[]
    for source in overlap['sources']:
        command=['git','-C','external_conway99_research','show',source['commit']+':'+source['path']]
        content=subprocess.check_output(command,cwd=ROOT)
        need(hashlib.sha256(content).hexdigest()==source['sha256'],'immutable archive source identity')
        archived.append({k:source[k]for k in ['repository','commit','path','sha256','section']})
    inputs[Path(__file__).relative_to(ROOT).as_posix()]=digest(Path(__file__))
    report=dict(status='INDEPENDENT_UNIVERSAL_TRIANGLE39_GRAM_SOS_PASS',claim_id=summary['claim_id'],claim_revision=1,
        recommendation='VERIFIED',kind='mathematical result',basis=['DERIVED','COMPUTED'],statement=summary['statement'],
        scope=summary['scope'],dependencies=[],dependencies_reason='Self-contained exact identities and real rank theorem for the explicitly defined finite graph family; no target existence/normalization premise.',
        timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),
        verifier='/root independent derivation, raw polynomial coefficient and Fraction-elimination checker',
        verification_type='Independent derivation plus complete finite artifact checking; no producer code imported.',inputs_sha256=inputs,
        exact_derivation=[
            'Every block of the inner C has row/column sum1. The three cell-constant vectors span an invariant F; its orthogonal W has zero sum per cell. Triangle-to-cell edges and J annihilate W. Thus both forms split as a W block plus six-dimensional quotient without cross terms.',
            'On W, Q=C+4I=I+(3I+C) and G=9(3I-C). Cubicity gives z^T(3I+C)z=sum_edges(z_u+z_v)^2 and z^T(3I-C)z=sum_edges(z_u-z_v)^2; these identities require only symmetric simple cubic C.',
            'On quotient coordinates (r,b), literal adjacency is R^2-sum(r_i^2)+24sum(r_i b_i)+12B^2 and norm is sum(r_i^2)+12sum(b_i^2). Exact coefficient expansion yields Q=3sum(r_i+4b_i)^2+R^2+12B^2 and G=36sum(r_i-R/3-3(b_i-B/3))^2+4(R-6B)^2.',
            'Q vanishes exactly for z=0,r=-4b,B=0, hence nullity2. For G, edge differences force z constant on each component. Every component has equal even cardinality in the three cells: cross-block bijections balance them and each internal matching pairs them. Therefore c in1..6, and imposing the three zero-cell-sum equations on component constants imposes one independent weighted equation: nullity c-1 on W.',
            'G quotient squares vanish exactly when r_i=3b_i+B, with three independent b coordinates. Total nullity(c-1)+3=c+2, rank39-(c+2)=37-c. Q rank39-2=37. These arguments are universal, independent of the fifteen calibration fixtures.',
        ],
        checked_fixtures=records,checks=dict(full_scaled_matrix_coefficients=15*1560,quotient_polarization_cases=quotient,
            rational_matrix_ranks=30,rational_kernel_basis_ranks=30,corruptions_rejected=bads,rank_calibration_cases=3),
        archive_overlap=archived,archive_review_scope='Targeted five-section overlap authentication; the prior36-factor mechanism/rank is disclosed. No novelty or general literature search claim.',
        shared_components=['Python standard-library exact integer/Fraction arithmetic and Git object retrieval; raw fixtures shared with producer, checker implementation separate.'],
        limitations=['No target graph, incidence factor or nonexistence proof. These PSD/rank tests do not remove a core from the stated family.',
                     'The finite fixtures calibrate computations; the written invariant-subspace and SOS proof supplies universal coverage.',
                     'No novelty, external review, or independent verification of every archived claim is asserted.'],
        elapsed_seconds=time.monotonic()-start)
    path=out/'summary.json';path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'status':report['status'],'sha256':digest(path),'elapsed_seconds':report['elapsed_seconds']}))

if __name__=='__main__':main()
