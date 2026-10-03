"""Exact content-divided unrestricted rooted7 GF2 necessary consistency screen.

Producer scalar checks are calibration, not independent mathematical approval.
All certificates retain complete raw row maps for another checking path.
"""
import argparse
from collections import Counter
from datetime import datetime,timezone
from functools import reduce
import hashlib
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
import time
from tqdm import tqdm
from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
MODEL=ROOT/'acceleration/results/20261002_rooted7_unrestricted_extension01/model.json'
MODEL_SHA='9f636889690071f69ad7a103b02abb2f43a5bbc2d2114c87a779da29c0f647a1'
AUDIT=ROOT/'acceleration/results/20261002_independent_review/rooted7_unrestricted_model01/summary.json'
AUDIT_SHA='e7631851f9cc5716c9d8a1bf5b30f9a4644d8e2170f116d1bb30378fbeb16d70'
SPEC=ROOT/'docs/PROTOCOL_20261003_UNRESTRICTED_ROOTED7_GF2_V1.md'
POPULATION=[(c,a,b) for c in range(3) for a in range(21) for b in range(10+c//2)]
LABELS=['const','c','a','b']


def need(value,reason):
    if not value:raise ValueError(reason)


def sha(path):
    with Path(path).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def save(path,data):
    with Path(path).open('x',encoding='utf8',newline='\n')as stream:json.dump(data,stream,indent=2);stream.write('\n')


def normalize(rows,columns):
    records=[]
    for index,row in enumerate(rows):
        coefficients={}
        for j,value in row['terms']:
            need(type(j)is int and 0<=j<columns and type(value)is int,'literal integer terms/range')
            coefficients[j]=coefficients.get(j,0)+value
        terms=sorted((j,value)for j,value in coefficients.items()if value)
        target=row['rhs_affine'];need(len(target)==4 and all(type(v)is int for v in target),'four exact RHS components')
        divisor=reduce(math.gcd,[abs(v)for j,v in terms]+[abs(v)for v in target],0)or 1
        records.append(dict(original_row=index,positive_integer_content=divisor,terms=[[j,v//divisor]for j,v in terms],rhs_affine=[v//divisor for v in target]))
    return records


def scalar_primal(rows,columns,bits,component=None,point=None):
    need(len(bits)==columns and all(type(v)is int and v in[0,1]for v in bits),'complete binary primal')
    if component is not None:target=[row['rhs_affine'][component]for row in rows]
    else:target=[sum(v*w for v,w in zip(row['rhs_affine'],[1,*point]))for row in rows]
    return all((sum(v*bits[j]for j,v in row['terms'])-t)%2==0 for row,t in zip(rows,target))


def scalar_relation(rows,columns,indices):
    need(indices==sorted(set(indices))and all(type(i)is int and 0<=i<len(rows)for i in indices),'strict original-row index relation')
    lhs=[0]*columns;target=[0]*4
    for i in indices:
        for j,v in rows[i]['terms']:lhs[j]+=v
        for j,v in enumerate(rows[i]['rhs_affine']):target[j]+=v
    return all(v%2==0 for v in lhs),[v%2 for v in target]


def elimination(rows,columns,deadline=None):
    pivots={};relations={}
    for index,row in enumerate(tqdm(rows,desc='original normalized rows overGF2',mininterval=5,disable=len(rows)<100)):
        if deadline is not None:need(not deadline.status()['stop_required']and deadline.status()['remaining_seconds']>20,'not completed within the allocated budget')
        mask=0
        for j,value in row['terms']:
            if value%2:mask^=1<<j
        target=sum((v%2)<<j for j,v in enumerate(row['rhs_affine']));origin=1<<index
        while mask:
            pivot=(mask&-mask).bit_length()-1
            if pivot not in pivots:pivots[pivot]=(mask,target,origin);break
            m,t,w=pivots[pivot];mask^=m;target^=t;origin^=w
        if not mask and target and target not in relations:relations[target]=origin
    return pivots,relations


def solve(pivots,columns,affine_mask):
    solution=0
    for pivot,(mask,target,origin)in sorted(pivots.items(),reverse=True):
        value=((target&affine_mask).bit_count()+(mask&solution).bit_count())%2
        if value:solution|=1<<pivot
    return[(solution>>j)&1 for j in range(columns)]


def indices(mask):
    result=[]
    while mask:
        low=mask&-mask;result.append(low.bit_length()-1);mask^=low
    return result


def raw_bits(path,bits,label):
    path.write_text('UNRESTRICTED_ROOTED7_GF2_PRIMAL_V1\n'+str(len(bits))+' '+label+'\n'+''.join(map(str,bits))+'\n',encoding='ascii',newline='\n')


def controls():
    raw=[dict(terms=[[0,1],[0,1]],rhs_affine=[2,0,0,0])];rows=normalize(raw,1);need(rows[0]['positive_integer_content']==2 and rows[0]['terms']==[[0,1]]and rows[0]['rhs_affine']==[1,0,0,0],'exact duplicate-term aggregation and gcd-content division')
    pivots,rels=elimination(rows,1);need(not rels,'tiny feasible operator')
    values=solve(pivots,1,1);need(values==[1]and scalar_primal(rows,1,values,component=0)and not scalar_primal(rows,1,[0],component=0),'complete positive and coordinate-corrupt binary primal')
    broken=normalize([dict(terms=[[0,1]],rhs_affine=[0,0,0,0]),dict(terms=[[0,1]],rhs_affine=[1,0,0,0])],1)
    _,relations=elimination(broken,1);need(set(relations)=={1},'complete inconsistent tiny affine relation')
    witness=indices(relations[1]);ok,rhs=scalar_relation(broken,1,witness);need(witness==[0,1]and ok and rhs==[1,0,0,0],'exact original-row XOR witness')
    need(not scalar_relation(broken,1,[0])[0],'changed row relation rejects nonzero column')
    wrong=[dict(row,positive_integer_content=1)for row in rows];need(wrong!=normalize(raw,1),'changed divisor rejected by independent recomputation')
    changed=json.loads(json.dumps(broken));changed[1]['rhs_affine'][0]=0;need(scalar_relation(changed,1,witness)[1]==[0,0,0,0],'changedRHS nullifies intended contradiction')
    coefficient=json.loads(json.dumps(broken));coefficient[1]['terms'][0][1]=2;need(not scalar_relation(coefficient,1,witness)[0],'changed genuine coefficient rejects relation')
    return dict(positive_binary_primal=True,inconsistent_original_row_xor=True,duplicate_terms_combined_before_content=True,corrupted_controls=['binarycoordinate','rowrelation','divisor','rhs','coefficient'],producer_calibration_only=True)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--controls-only',action='store_true');args=ap.parse_args()
    deadline=CommandDeadline(args.seconds,allocation_reason='New unrestricted11769x2810 exact GF2/fourRHS content-divided bitset test,120outer100worker20reserve; small sparse root7bitsets/no numerical or native solver')
    started=time.monotonic();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    try:
        need(sha(MODEL)==MODEL_SHA and sha(AUDIT)==AUDIT_SHA,'frozen unrestricted literaloperator and independent necessary-encoding audit')
        pins={p.relative_to(ROOT).as_posix():sha(p)for p in[MODEL,AUDIT,SPEC,Path(__file__),ROOT/'uv.lock',ROOT/'pyproject.toml',ROOT/'acceleration/command_deadline.py',ROOT/'acceleration/run_compute_command.py']}
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256=pins,python_version=platform.python_version(),profile_population=POPULATION,rhs_component_order=LABELS,selection='All651integer localprimary c,a,b profiles; no omitted favorable cases. Exact4RHS simultaneously reduced.',scope='Literal content-divided GF2 necessary consistency for integer countsolutions of one unrestricted rooted7 model. No nonnegative/integer sufficiency or graph realization.',success='Complete4primalvectors or normalized-original-row-index XOR relations independentlycheckable; everyclaimedexclusion exactallcolumns and RHS, all651classified.',falsification='Nonzero scalarresidual, invalidcontentroundtrip, badrelation/RHS or missingprofile vetoes certificate.',independent_requirement='Different author recomputes rawcontentdivision and complete scalar allrow primals/allcolumn relations and651outcomes; producer checks/calibration cannot approve discovery.',arithmetic='Exact Python integers/gcd/XOR; no floating arithmetic',automatic_retry=False))
        save(out/'controls.json',controls())
        if args.controls_only:save(out/'summary.json',dict(status='UNRESTRICTED_ROOTED7_GF2_PRODUCER_CONTROLS_PASS',producer_calibration_only=True,elapsed_seconds=time.monotonic()-started));return
        raw=json.loads(MODEL.read_bytes());rows=raw['equations'];columns=len(raw['variables']);need(columns==2810 and len(rows)==11769,'frozen dimensions')
        normalized=normalize(rows,columns);path=out/'normalized_literal_rows.jsonl'
        with path.open('x',encoding='utf8',newline='\n')as stream:
            for record in normalized:stream.write(json.dumps(record,separators=(',',':'))+'\n')
        pivots,relations=elimination(normalized,columns,deadline);relation_records=[]
        for mask,origin in sorted(relations.items()):
            selected=indices(origin);ok,affine=scalar_relation(normalized,columns,selected);need(ok and affine==[(mask>>j)&1 for j in range(4)],'all2810column scalar XOR relation plus exact4RHS')
            name=f'relation_{mask}.json';save(out/name,dict(format='UNRESTRICTED_ROOTED7_CONTENT_DIVIDED_ORIGINAL_ROW_XOR_V1',columns=columns,rows=len(rows),original_row_indices=selected,rhs_affine_residue=affine,normalized_literal_sha256=sha(path),scope='Normalized originalrows have rawintegercontent divisions. Integer necessity only; do not call this original-undivided mod2 relation.'));relation_records.append(dict(path=name,sha256=sha(out/name),rhs_affine_residue=affine))
        full_vectors=[];profile_vectors={}
        if not relations:
            for component,label in enumerate(LABELS):
                values=solve(pivots,columns,1<<component);need(scalar_primal(normalized,columns,values,component=component),'complete11769scalar normalized rows of componentprimal')
                name='x_'+label+'.bits';raw_bits(out/name,values,label);full_vectors.append(dict(component=label,path=name,sha256=sha(out/name),binary_coordinates=columns))
        else:
            for c in range(2):
                for a in range(2):
                    for b in range(2):
                        target=1|(c<<1)|(a<<2)|(b<<3)
                        if any((mask&target).bit_count()%2 for mask in relations):continue
                        values=solve(pivots,columns,target);need(scalar_primal(normalized,columns,values,point=[c,a,b]),'everyconsistent parityprofile scalarprimal')
                        name=f'parity_{c}_{a}_{b}.bits';raw_bits(out/name,values,f'profile_{c}_{a}_{b}');profile_vectors[(c,a,b)]=name
        outcomes=[]
        for point in POPULATION:
            target=1|((point[0]&1)<<1)|((point[1]&1)<<2)|((point[2]&1)<<3);excluded=[j for j,r in enumerate(relation_records)if sum(v*w for v,w in zip(r['rhs_affine_residue'],[1,*point]))%2]
            if excluded:outcomes.append(dict(parameters=point,status='CANDIDATE_EXACT_INTEGER_NECESSARY_PROFILE_EXCLUSION',first_relation=excluded[0]))
            else:outcomes.append(dict(parameters=point,status='CANDIDATE_LITERAL_MOD2_COMPATIBLE',certificate='fourRHSlinearcombination'if not relations else profile_vectors[tuple(v%2 for v in point)]))
        save(out/'all651_outcomes.json',outcomes)
        save(out/'summary.json',dict(status='CANDIDATE_UNRESTRICTED_ROOTED7_CONTENT_DIVIDED_GF2_RESULTS',timestamp=datetime.now(timezone.utc).isoformat(),rows=len(rows),columns=columns,raw_literal_terms=sum(len(row['terms'])for row in rows),content_census=dict(Counter(record['positive_integer_content']for record in normalized)),normalization='Combine duplicatedcolumn terms, divide positivegcd of allinteger coefficients and4RHScomponents; exactinteger equivalence, GF2necessaryonly.',normalized_literal_rows=path.relative_to(ROOT).as_posix(),normalized_literal_sha256=sha(path),complete_component_primals=full_vectors,nonzero_affine_relation_certificates=relation_records,selected_integer_parameter_profiles=651,excluded_profiles=sum(r['status']=='CANDIDATE_EXACT_INTEGER_NECESSARY_PROFILE_EXCLUSION'for r in outcomes),compatible_profiles=sum(r['status']=='CANDIDATE_LITERAL_MOD2_COMPATIBLE'for r in outcomes),rank_asserted=False,independent_review=None,target_resolution=False,overall_search_coverage='UNKNOWN; no validated denominator.',elapsed_seconds=time.monotonic()-started,deadline=deadline.status(),outputs_sha256={p.name:sha(p)for p in out.iterdir()if p.is_file()}))
    except Exception as error:save(out/'failure.json',dict(error=repr(error),elapsed_seconds=time.monotonic()-started,all_outputs_preserved=True,target_resolution=False));raise


if __name__=='__main__':main()
