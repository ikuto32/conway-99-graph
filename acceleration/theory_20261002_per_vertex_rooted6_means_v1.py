"""Candidate per-vertex identity calibration and saved-root7 witness screen.

No solver launch; a violating saved witness is not an excluded graph/profile.
Shares frozen discovery graph and canonical-mask helpers only.
"""
import argparse
from datetime import datetime,timezone
from fractions import Fraction
from itertools import combinations
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

from command_deadline import CommandDeadline
import theory_20261002_almost_prism_global_mean_v1 as prior

ROOT=prior.ROOT
PROTOCOL=ROOT/'docs/DERIVATION_20261002_PER_VERTEX_ROOTED6_MEANS.md'
FIRST=ROOT/'acceleration/results/20261002_almost_prism_global_mean01'
SECOND=ROOT/'acceleration/results/20261002_prism_global_parameter_means01'
MODEL=ROOT/'acceleration/results/20261002_rooted7_extension_model/model.json'
CORNERS=ROOT/'acceleration/results/20261002_rooted7_corner_certificates02'
POINTS=[(0,0),(20,0),(0,9),(20,9)]


def need(ok,message):
    if not ok:raise ValueError(message)


def dump(path,value):
    with path.open('x',encoding='utf8',newline='\n')as stream:json.dump(value,stream,indent=2);stream.write('\n')


def vertex_totals(A,k,a,b,prisms):
    n=len(A);population={(u,v)for u,v in combinations(range(n),2)if not A[u][v]}
    need({tuple(row[:2])for row in a}==population and len(a)==len(population)and {tuple(row[:2])for row in b}==population and len(b)==len(population),'complete raw unordered pair population')
    need(all(type(c)is int and c>=0 for u,v,c in [*a,*b]),'integer nonnegative raw counts')
    sa=[0]*n;sb=[0]*n;tu=[0]*n
    for u,v,c in a:sa[u]+=c;sa[v]+=c
    for u,v,c in b:sb[u]+=c;sb[v]+=c
    for vertices in prisms:
        need(len(vertices)==len(set(vertices))==6 and prior.is_prism(A,vertices),'raw induced prism sixset')
        for u in vertices:tu[u]+=1
    rows=[]
    for u in range(n):
        need(sa[u]+2*tu[u]==k*(k-2)and sb[u]+tu[u]==n-k-1,'PER_VERTEX_MEAN_IDENTITY')
        rows.append({'vertex':u,'sum_a_over_nonneighbors':sa[u],'sum_b_over_nonneighbors':sb[u],'prisms_containing_vertex':tu[u]})
    return rows


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--seconds',type=float,required=True);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();deadline=CommandDeadline(args.seconds,allocation_reason='Saved26730pair arrays/twofixtures and4exact2766vectors;outer60worker40reserve20,no solver')
    started=time.monotonic();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    try:
        paths=[Path(__file__),Path(prior.__file__),PROTOCOL,prior.RAW,FIRST/'controls.json',FIRST/'rook9_adjacency.json',FIRST/'243_unordered_nonedge_a_counts.json',SECOND/'243_unordered_nonedge_b_counts.json',SECOND/'243_prism_six_sets.json',MODEL,ROOT/'uv.lock',ROOT/'pyproject.toml',*[CORNERS/f'corner_{a}_{b}.json'for a,b in POINTS]]
        dump(out/'manifest.json',{'timestamp':datetime.now(timezone.utc).isoformat(),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':[sys.executable,*sys.argv],'cwd':str(ROOT),'python_version':platform.python_version(),'inputs_sha256':{str(p.relative_to(ROOT)):prior.sha(p)for p in paths},
            'selection':'All4already saved exact root7corners and every vertex of rook9/243fixtures; no favorable omissions.',
            'success':'Every pervertex raw count identity and corrupted control; exact old11749rows preserved and new4candidate row residuals saved.',
            'scope':'CANDIDATE pervertexmean theorem and saved necessary-relaxation witness screen; no localprofile exclusion or graph feasibility.',
            'independent_requirement':'Alternate derivation and source-free raw fixture audit before theorem/necessary rows promotion.'})
        controls=json.loads((FIRST/'controls.json').read_bytes());rook=json.loads((FIRST/'rook9_adjacency.json').read_bytes())['adjacency'];prior.validate(rook,4)
        ra=controls['rook9_nonedge_a_counts'];rb=[]
        for u,v,c in ra:
            count=sum(prior.canonical6(rook,[u,v,*subset])==15540 for subset in combinations([x for x in range(9)if x not in [u,v]],4));rb.append([u,v,count])
        rookrows=vertex_totals(rook,4,ra,rb,controls['rook9_prisms']);dump(out/'rook9_vertex_totals.json',rookrows)
        rejected=[]
        for label,modified_a,modified_prisms in [('changed_pair_count',[[u,v,c+int(i==0)]for i,(u,v,c)in enumerate(ra)],controls['rook9_prisms']),('removed_prism',ra,controls['rook9_prisms'][1:])]:
            try:vertex_totals(rook,4,modified_a,rb,modified_prisms)
            except ValueError as error:need(str(error)=='PER_VERTEX_MEAN_IDENTITY','specific corrupt stage');rejected.append({'label':label,'diagnostic':str(error)})
            else:raise ValueError('corrupt incidence accepted')
        A=json.loads(prior.RAW.read_bytes())['adjacency'];prior.validate(A,22)
        a=json.loads((FIRST/'243_unordered_nonedge_a_counts.json').read_bytes());b=json.loads((SECOND/'243_unordered_nonedge_b_counts.json').read_bytes());prisms=json.loads((SECOND/'243_prism_six_sets.json').read_bytes())
        dump(out/'243_vertex_totals.json',vertex_totals(A,22,a,b,prisms))
        model=json.loads(MODEL.read_bytes());variables=model['variables'];lookup={tuple(v):i for i,v in enumerate(variables)};oldrows=model['equations'];need(len(variables)==2766 and len(oldrows)==11749,'frozen root7universe')
        records=[]
        for point in POINTS:
            raw=json.loads((CORNERS/f'corner_{point[0]}_{point[1]}.json').read_bytes());values=[Fraction(*cell)for cell in raw['exact_values']]
            need(len(values)==len(variables)and all(c>=0 for c in values),'exact saved primal shape')
            need(all(sum(c*values[j]for j,c in row['terms'])==row['rhs_affine'][0]+row['rhs_affine'][1]*point[0]+row['rhs_affine'][2]*point[1]for row in oldrows),'every original exact row')
            residuals=[]
            for anchor in [0,1]:
                parts=[p for p in range(4)if not(p&1<<anchor)]
                for coordinate,constant in [(0,168),(1,84)]:
                    indices=[lookup[('aggregate',anchor,p,coordinate)]for p in parts]
                    rhs=constant-point[coordinate];left=sum(values[j]for j in indices);residual=left-rhs
                    residuals.append({'anchor':anchor,'coordinate':coordinate,'partitions':parts,'literal_terms':[[j,1]for j in indices],
                        'rhs_affine':[constant,-int(coordinate==0),-int(coordinate==1)],'left':[left.numerator,left.denominator],
                        'rhs':rhs,'residual':[residual.numerator,residual.denominator],'candidate_row_satisfied':residual==0})
            records.append({'parameters':list(point),'original11749rows_rechecked':True,'proposed_four_rows':residuals,
                'saved_witness_satisfies_new_candidate_rows':all(row['candidate_row_satisfied']for row in residuals),'profile_excluded':False})
            need(deadline.status()['remaining_seconds']>10,'not completed within allocated budget')
        dump(out/'saved_corner_rows.json',records)
        dump(out/'summary.json',{'status':'CANDIDATE_PER_VERTEX_ROOTED6_MEANS_SAVED_WITNESS_SCREEN','timestamp':datetime.now(timezone.utc).isoformat(),
            'fixture_vertices_checked':{'rook9':9,'srg243':243},'corrupt_controls':rejected,'saved_exact_corner_witnesses_checked':len(records),
            'saved_witnesses_satisfying_proposed_rows':sum(r['saved_witness_satisfies_new_candidate_rows']for r in records),
            'profiles_excluded':0,'numerical_or_modular_solver_attempts':0,'conditional_target_per_vertex_sums':{'a':168,'b':84,'prism_absence':'UNKNOWN'},
            'theorem_status':'CANDIDATE_PENDING_INDEPENDENT_DERIVATION','target_resolution':False,'elapsed_seconds':time.monotonic()-started,
            'outputs_sha256':{str(p.relative_to(ROOT)):prior.sha(p)for p in out.iterdir()if p.is_file()}})
    except BaseException as error:
        dump(out/'failure.json',{'error':repr(error),'elapsed_seconds':time.monotonic()-started,'partial_only':True,'automatic_resume':False});raise


if __name__=='__main__':main()
