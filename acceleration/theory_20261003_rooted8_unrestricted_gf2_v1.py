"""Exact content-divided unrestricted rooted8 GF2 necessary consistency screen.

Producer scalar checks are calibration, not independent mathematical approval.
All certificates retain complete raw row maps for another checking path.
"""
import argparse
import ctypes
from collections import Counter
from datetime import datetime,timezone
from functools import reduce
import gzip
import hashlib
import json
import math
from pathlib import Path
from itertools import product
import platform
import subprocess
import sys
import time
from tqdm import tqdm
from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
MODEL=ROOT/'acceleration/results/20261003_rooted8_unrestricted_extension01/model.json'
MODEL_SHA='b143c129fce1f450b54a397d6d508ecb81a67870c2bafd2e9f50dee0bda83f1a'
SPEC=ROOT/'docs/PROTOCOL_20261003_UNRESTRICTED_ROOTED8_GF2_V1.md'
ROOT_CAL=ROOT/'acceleration/results/20261003_independent_review/root8_mod2_calibration01/summary.json'
ROOT_CAL_SHA='d0238a17825e7fe23aa438c6f2f45a1cf26d470f64aa0f79c2524fc4d6900af2'
AUDIT=ROOT/'acceleration/results/20261003_independent_review/rooted8_unrestricted_model01/summary.json'
AUDIT_SHA='ec5073a22027c512e29dac1d49048a507f272cb8ce1a0a79d2ca1f663f1be974'
CAT_AUDIT=ROOT/'acceleration/results/20261003_independent_review/rooted8_unrestricted_catalogue01/summary.json'
CAT_AUDIT_SHA='1cf70d9caed5235bcce437fbc57280a0778c1f9a6cd9d628766de586516f9a6a'
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


def checkpoint_save(path,pins,next_row,columns,total_rows,pivots,relations):
    temporary=path.with_suffix(path.suffix+'.partial')
    with gzip.open(temporary,'xt',encoding='ascii',compresslevel=1)as stream:
        stream.write(json.dumps(dict(format='UNRESTRICTED_ROOTED8_GF2_ELIMINATION_CHECKPOINT_V1',inputs_sha256=pins,next_row=next_row,columns=columns,total_rows=total_rows,complete_checkpoint=True),separators=(',',':'))+'\n')
        for pivot,(mask,target,origin)in sorted(pivots.items()):stream.write(json.dumps(['p',pivot,target,hex(mask),hex(origin)],separators=(',',':'))+'\n')
        for target,origin in sorted(relations.items()):stream.write(json.dumps(['r',target,hex(origin)],separators=(',',':'))+'\n')
        stream.write('"END"\n')
    temporary.replace(path)


def checkpoint_load(path,pins,columns,total_rows):
    pivots={};relations={}
    with gzip.open(path,'rt',encoding='ascii')as stream:
        header=json.loads(next(stream));need(header['format']=='UNRESTRICTED_ROOTED8_GF2_ELIMINATION_CHECKPOINT_V1'and header['inputs_sha256']==pins and header['columns']==columns and header['total_rows']==total_rows and header['complete_checkpoint']is True,'checkpoint exact source/input/dimensions')
        completed=header['next_row'];need(type(completed)is int and 0<=completed<=total_rows,'checkpoint complete prefix')
        terminated=False
        for line in stream:
            record=json.loads(line)
            if record=='END':terminated=True;need(not stream.read(),'checkpoint extra trailing data');break
            if record[0]=='p':
                _,pivot,target,mask,origin=record;mask=int(mask,16);origin=int(origin,16)
                need(type(pivot)is int and 0<=pivot<columns and pivot not in pivots and type(target)is int and 0<=target<16 and mask>0 and mask.bit_length()<=columns and(mask&-mask)==1<<pivot and origin>0 and origin.bit_length()<=completed,'checkpoint exact pivot/bit bounds')
                pivots[pivot]=(mask,target,origin)
            else:
                need(record[0]=='r'and len(record)==3,'checkpoint record type');_,target,origin=record;origin=int(origin,16)
                need(type(target)is int and 0<target<16 and target not in relations and origin>0 and origin.bit_length()<=completed,'checkpoint exact relation/bit bounds');relations[target]=origin
        need(terminated,'checkpoint complete END record')
    return completed,pivots,relations


def elimination(rows,columns,deadline=None,out=None,pins=None,resume=None,stop_after=None):
    completed,pivots,relations=checkpoint_load(resume,pins,columns,len(rows))if resume else(0,{},{})
    def stop(index):
        if out is not None:checkpoint_save(out/'elimination_stop.jsonl.gz',pins,index,columns,len(rows),pivots,relations)
        return pivots,relations,index,False
    for index in tqdm(range(completed,len(rows)),desc='Original normalized rooted8 rows overGF2',mininterval=5,disable=len(rows)<100):
        if (stop_after is not None and index>=stop_after)or(deadline is not None and(deadline.status()['stop_required']or deadline.status()['remaining_seconds']<=40)):return stop(index)
        row=rows[index]
        mask=0
        for j,value in row['terms']:
            if value%2:mask^=1<<j
        target=sum((v%2)<<j for j,v in enumerate(row['rhs_affine']));origin=1<<index
        reduced=0
        while mask:
            pivot=(mask&-mask).bit_length()-1
            if pivot not in pivots:pivots[pivot]=(mask,target,origin);break
            m,t,w=pivots[pivot];mask^=m;target^=t;origin^=w
            reduced+=1
            if reduced%1024==0 and deadline is not None and deadline.status()['remaining_seconds']<=40:return stop(index)
        if not mask and target and target not in relations:relations[target]=origin
        if out is not None and(index+1)%10000==0:save(out/f'progress_{index+1:06d}.json',dict(completed_original_rows=index+1,total_rows=len(rows),nonzero_affine_relations=len(relations),rank_asserted=False,timestamp=datetime.now(timezone.utc).isoformat(),deadline=None if deadline is None else deadline.status()))
    return pivots,relations,len(rows),True


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
    path.write_text('UNRESTRICTED_ROOTED8_GF2_PRIMAL_V1\n'+str(len(bits))+' '+label+'\n'+''.join(map(str,bits))+'\n',encoding='ascii',newline='\n')


def controls(out):
    out=out/'control_checkpoint';out.mkdir(exist_ok=False)
    raw=[dict(terms=[[0,1],[0,1]],rhs_affine=[2,0,0,0])];rows=normalize(raw,1);need(rows[0]['positive_integer_content']==2 and rows[0]['terms']==[[0,1]]and rows[0]['rhs_affine']==[1,0,0,0],'exact duplicate-term aggregation and gcd-content division')
    pivots,rels,done,complete=elimination(rows,1);need(not rels and complete and done==1,'tiny feasible operator')
    values=solve(pivots,1,1);need(values==[1]and scalar_primal(rows,1,values,component=0)and not scalar_primal(rows,1,[0],component=0),'complete positive and coordinate-corrupt binary primal')
    broken=normalize([dict(terms=[[0,1]],rhs_affine=[0,0,0,0]),dict(terms=[[0,1]],rhs_affine=[1,0,0,0])],1)
    _,relations,done,complete=elimination(broken,1);need(set(relations)=={1}and complete,'complete inconsistent tiny affine relation')
    witness=indices(relations[1]);ok,rhs=scalar_relation(broken,1,witness);need(witness==[0,1]and ok and rhs==[1,0,0,0],'exact original-row XOR witness')
    need(not scalar_relation(broken,1,[0])[0],'changed row relation rejects nonzero column')
    wrong=[dict(row,positive_integer_content=1)for row in rows];need(wrong!=normalize(raw,1),'changed divisor rejected by independent recomputation')
    changed=json.loads(json.dumps(broken));changed[1]['rhs_affine'][0]=0;need(scalar_relation(changed,1,witness)[1]==[0,0,0,0],'changedRHS nullifies intended contradiction')
    coefficient=json.loads(json.dumps(broken));coefficient[1]['terms'][0][1]=2;need(not scalar_relation(coefficient,1,witness)[0],'changed genuine coefficient rejects relation')
    identity=normalize([dict(terms=[[j,4 if j%2 else-2]],rhs_affine=[(4 if j%2 else-2)*int(k==j)for k in range(4)])for j in range(4)],4)
    pp,rr,_,complete=elimination(identity,4);need(complete and not rr,'allfourRHS signed/content4control')
    need(all(scalar_primal(identity,4,solve(pp,4,1<<j),component=j)for j in range(4)),'allfourfullcomponent primals')
    odd=normalize([dict(terms=[[0,2]],rhs_affine=[0,0,0,0]),dict(terms=[[0,4]],rhs_affine=[0,4,0,0]),dict(terms=[],rhs_affine=[0,0,0,0])],1)
    pp,rr,_,complete=elimination(odd,1);need(complete and set(rr)=={2},'c-only relation and zero row')
    for parity in product(range(2),repeat=3):
        affine=1|sum(value<<(j+1)for j,value in enumerate(parity));predicted=not any((mask&affine).bit_count()%2 for mask in rr)
        brute=any(scalar_primal(odd,1,[value],point=parity)for value in range(2));need(predicted==brute==(parity[0]==0),'all8parity brute-force truth table')
    need(sum(c%2==1 for c,a,b in POPULATION)==210,'odd-c control651classification')
    pin={'synthetic_exact_control':'four_rhs_identity'};prefix,rels,done,complete=elimination(identity,4,out=out,pins=pin,stop_after=2);need(not complete and done==2,'declared split checkpoint')
    restored,rels,done,complete=elimination(identity,4,pins=pin,resume=out/'elimination_stop.jsonl.gz');need(complete and done==4,'complete split resume')
    whole,whole_rel,_,_=elimination(identity,4);need(restored==whole and rels==whole_rel,'whole/split exact bitsets')
    try:checkpoint_load(out/'elimination_stop.jsonl.gz',{'synthetic_exact_control':'corrupt'},4,4)
    except ValueError:pass
    else:raise ValueError('changed checkpoint input accepted')
    with gzip.open(out/'elimination_stop.jsonl.gz','rt',encoding='ascii')as stream:records=[json.loads(line)for line in stream]
    negatives=[]
    for label in ['missing_END','pivot_outside','origin_after_prefix','wrong_rhs','extra_after_END']:
        changed=json.loads(json.dumps(records))
        if label=='missing_END':changed=changed[:-1]
        elif label=='pivot_outside':changed[1][1]=4
        elif label=='origin_after_prefix':changed[1][4]='0x10'
        elif label=='wrong_rhs':changed[1][2]=16
        else:changed.append(['r',1,'0x1'])
        bad=out/f'corrupt_{label}.jsonl.gz'
        with gzip.open(bad,'xt',encoding='ascii')as stream:
            for record in changed:stream.write(json.dumps(record,separators=(',',':'))+'\n')
        try:checkpoint_load(bad,pin,4,4)
        except ValueError:negatives.append(label)
        else:raise ValueError('Corrupt checkpoint accepted: '+label)
    sign=json.loads(json.dumps(identity));sign[0]['terms'][0][1]*=-1;need(sign!=identity,'Sign changes exact normalized coefficients even if modulo2 is unchanged')
    return dict(positive_binary_primal=True,inconsistent_original_row_xor=True,duplicate_terms_combined_before_content=True,four_rhs_signed_contents_2_4=True,all_eight_parity_truth_tables=True,odd_c_control_exclusions=210,exact_whole_split_checkpoint=True,checkpoint_sha256=sha(out/'elimination_stop.jsonl.gz'),checkpoint_precise_negative_controls=negatives,corrupted_controls=['binarycoordinate','rowrelation','divisor','rhs','coefficient','checkpoint_input','integer_sign_identity'],sign_scope='Mod2 alone cannot distinguish coefficient sign; raw exact normalization identity can.',producer_calibration_only=True)


class Memory(ctypes.Structure):
    _fields_=[('length',ctypes.c_uint32),('load_percent',ctypes.c_uint32),('physical_total',ctypes.c_uint64),('physical_available',ctypes.c_uint64),('page_total',ctypes.c_uint64),('page_available',ctypes.c_uint64),('virtual_total',ctypes.c_uint64),('virtual_available',ctypes.c_uint64),('extended_available',ctypes.c_uint64)]


def memory_observation():
    if sys.platform!='win32':return dict(available_bytes=None,reason='Windows actual memory observation unavailable on this host; separately supervised launch resource check required')
    observed=Memory();observed.length=ctypes.sizeof(observed);need(ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(observed)),'Actual local Windows memory observation')
    need(observed.physical_available>=4*1024**3,'At least4GiB actual free physical memory required')
    return dict(available_bytes=observed.physical_available,total_bytes=observed.physical_total,load_percent=observed.load_percent)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--controls-only',action='store_true');ap.add_argument('--calibration',type=Path);ap.add_argument('--calibration-sha256');ap.add_argument('--resume',type=Path);args=ap.parse_args()
    deadline=CommandDeadline(args.seconds,allocation_reason='New unrestricted86434x23334 exact GF2/fourRHS content-divided bitset test,300outer260worker40reserve; calibration separately small supported invocation')
    started=time.monotonic();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    try:
        need(sha(MODEL)==MODEL_SHA and sha(AUDIT)==AUDIT_SHA and sha(CAT_AUDIT)==CAT_AUDIT_SHA and sha(ROOT_CAL)==ROOT_CAL_SHA,'Frozen unrestricted literaloperator, complete necessary-encoding/catalogue audits and pre-output independent checker calibration')
        pins={p.relative_to(ROOT).as_posix():sha(p)for p in[MODEL,AUDIT,CAT_AUDIT,ROOT_CAL,SPEC,Path(__file__),ROOT/'uv.lock',ROOT/'pyproject.toml',ROOT/'acceleration/command_deadline.py',ROOT/'acceleration/run_compute_command.py']}
        root_cal=json.loads(ROOT_CAL.read_bytes())
        for name,expected in root_cal['inputs_sha256'].items():need(sha(ROOT/name)==expected,'Exact unchanged pre-output independent checker closure '+name);pins[name]=expected
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_commit_scope='Actual base commit; new working source/protocol/calibrations separately hashed, do not infer their Git presence',command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256=pins,python_version=platform.python_version(),profile_population=POPULATION,rhs_component_order=LABELS,selection='All651integer localprimary c,a,b profiles; no omitted favorable cases. Exact4RHS simultaneously reduced.',scope='Literal content-divided GF2 necessary consistency for integer countsolutions of one unrestricted rooted8 model. No nonnegative/integer sufficiency or graph realization.',success='Complete4primalvectors or normalized-original-row-index XOR relations independentlycheckable; everyclaimedexclusion exactallcolumns and RHS, all651classified.',falsification='Nonzero scalarresidual, invalidcontentroundtrip, badrelation/RHS or missingprofile vetoes certificate.',independent_requirement='Different author recomputes rawcontentdivision and complete scalar allrow primals/allcolumn relations and651outcomes; producer checks/calibration cannot approve discovery.',arithmetic='Exact Python integers/gcd/XOR; no floating arithmetic',allocation=dict(outer_seconds=300,worker_seconds=args.seconds,worker_reserve_seconds=40),memory_observation=memory_observation(),max_fullwidth_pivot_bitset_payload_estimate_bytes=23334*((23334+7)//8+(86434+7)//8),automatic_retry=False,resume=None if args.resume is None else dict(path=args.resume.as_posix(),sha256=sha(args.resume))))
        if args.controls_only:
            need(not args.resume and not args.calibration,'Calibration cannot resume or launch scientific output');save(out/'controls.json',controls(out));save(out/'summary.json',dict(status='UNRESTRICTED_ROOTED8_GF2_PRODUCER_CONTROLS_PASS',producer_calibration_only=True,inputs_sha256=pins,elapsed_seconds=time.monotonic()-started,outputs_sha256={p.relative_to(out).as_posix():sha(p)for p in out.rglob('*')if p.is_file()}));return
        need(args.calibration and args.calibration_sha256 and sha(args.calibration)==args.calibration_sha256,'Exact frozen producer calibration required')
        calibration=json.loads(args.calibration.read_bytes());need(calibration['status']=='UNRESTRICTED_ROOTED8_GF2_PRODUCER_CONTROLS_PASS'and calibration['inputs_sha256']==pins,'Changed source cannot transfer old engineering gate')
        for name,expected in calibration['outputs_sha256'].items():need(sha(args.calibration.parent/name)==expected,'Producer calibration raw identity '+name)
        save(out/'calibration_binding.json',dict(producer_calibration_path=args.calibration.as_posix(),producer_calibration_sha256=args.calibration_sha256,independent_preoutput_checker_calibration_sha256=ROOT_CAL_SHA,discovery_cannot_approve=True))
        raw=json.loads(MODEL.read_bytes());rows=raw['equations'];columns=len(raw['variables']);need(columns==23334 and len(rows)==86434,'Frozen complete unrestricted root8dimensions')
        normalized=normalize(rows,columns);path=out/'normalized_literal_rows.jsonl'
        with path.open('x',encoding='utf8',newline='\n')as stream:
            for record in normalized:stream.write(json.dumps(record,separators=(',',':'))+'\n')
        pivots,relations,completed,complete=elimination(normalized,columns,deadline,out,pins,args.resume);need(complete,'not completed within the allocated budget; exact elimination_stop.jsonl.gz checkpoint preserved')
        if deadline.status()['remaining_seconds']<=40:
            checkpoint_save(out/'elimination_stop.jsonl.gz',pins,completed,columns,len(rows),pivots,relations);raise ValueError('not completed within the allocated budget; reduction complete, certificates pending and exact checkpoint preserved')
        relation_records=[]
        for mask,origin in sorted(relations.items()):
            selected=indices(origin);ok,affine=scalar_relation(normalized,columns,selected);need(ok and affine==[(mask>>j)&1 for j in range(4)],'All23334column scalar XOR relation plus exact4RHS')
            name=f'relation_{mask}.json';save(out/name,dict(format='UNRESTRICTED_ROOTED8_CONTENT_DIVIDED_ORIGINAL_ROW_XOR_V1',columns=columns,rows=len(rows),original_row_indices=selected,rhs_affine_residue=affine,normalized_literal_sha256=sha(path),scope='Normalized originalrows have rawintegercontent divisions. Integer necessity only; do not call this original-undivided mod2 relation.'));relation_records.append(dict(path=name,sha256=sha(out/name),rhs_affine_residue=affine))
        full_vectors=[];profile_vectors={}
        if not relations:
            for component,label in enumerate(LABELS):
                values=solve(pivots,columns,1<<component);need(scalar_primal(normalized,columns,values,component=component),'Complete86434scalar normalized rows of componentprimal')
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
        save(out/'summary.json',dict(status='CANDIDATE_UNRESTRICTED_ROOTED8_CONTENT_DIVIDED_GF2_RESULTS',timestamp=datetime.now(timezone.utc).isoformat(),rows=len(rows),columns=columns,completed_original_rows=completed,raw_literal_terms=sum(len(row['terms'])for row in rows),content_census=dict(Counter(record['positive_integer_content']for record in normalized)),normalization='Combine duplicatedcolumn terms, divide positivegcd of allinteger coefficients and4RHScomponents; exactinteger equivalence, GF2necessaryonly.',normalized_literal_rows=path.relative_to(ROOT).as_posix(),normalized_literal_sha256=sha(path),complete_component_primals=full_vectors,nonzero_affine_relation_certificates=relation_records,selected_integer_parameter_profiles=651,excluded_profiles=sum(r['status']=='CANDIDATE_EXACT_INTEGER_NECESSARY_PROFILE_EXCLUSION'for r in outcomes),compatible_profiles=sum(r['status']=='CANDIDATE_LITERAL_MOD2_COMPATIBLE'for r in outcomes),rank_asserted=False,independent_review=None,target_resolution=False,overall_search_coverage='UNKNOWN; no validated denominator.',elapsed_seconds=time.monotonic()-started,deadline=deadline.status(),outputs_sha256={p.name:sha(p)for p in out.iterdir()if p.is_file()}))
    except Exception as error:save(out/'failure.json',dict(error=repr(error),elapsed_seconds=time.monotonic()-started,all_outputs_preserved=True,target_resolution=False));raise


if __name__=='__main__':main()
