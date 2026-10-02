"""Exact packed-trit GF3 consistency on all210 frozen integer profiles.

Two Python integer masks represent coefficients1 and2. Every surviving affine
consistency relation retains all original-row weights and is replayed directly
with ordinary integer modular arithmetic, separately from the packed operations.
Results remain conditional on the necessary-model derivation/coverage audit.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

from tqdm import tqdm
from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
MODEL=ROOT/'acceleration/results/20261002_rooted7_extension_model/model.json'
MODEL_SHA='21eb899c3606727ef4e452d518316957cf9eb76e5e85c5a79af82421f4004595'


def need(value,reason):
    if not value:raise ValueError(reason)


def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def save(path,value):
    with path.open('x',encoding='utf8',newline='\n') as stream:json.dump(value,stream,indent=2);stream.write('\n')


def add(first,second):
    a,b=first;c,d=second
    zero_a=~(a|b);zero_b=~(c|d)
    one=(zero_a&c)|(a&zero_b)|(b&d)
    two=(zero_a&d)|(b&zero_b)|(a&c)
    return one,two


def negate(value):return value[1],value[0]


def encode(row,columns):
    one,two=0,0
    actual=Counter()
    for j,coefficient in row['terms']:actual[j]+=coefficient
    for j,coefficient in enumerate(row['rhs_affine']):actual[columns+j]+=coefficient
    for j,coefficient in actual.items():
        if coefficient%3==1:one|=1<<j
        elif coefficient%3==2:two|=1<<j
    return one,two


def decoded_coefficients(value):
    one,two=value;indices=[]
    while one:
        first=one&-one;indices.append([first.bit_length()-1,1]);one-=first
    while two:
        first=two&-two;indices.append([first.bit_length()-1,2]);two-=first
    return sorted(indices)


def plain_certificate(rows,columns,weights,expected):
    sums=[0]*columns;parameters=[0]*3
    for i,weight in weights:
        for j,coefficient in rows[i]['terms']:sums[j]=(sums[j]+weight*coefficient)%3
        for j,coefficient in enumerate(rows[i]['rhs_affine']):parameters[j]=(parameters[j]+weight*coefficient)%3
    return not any(sums) and parameters==expected


def reduce(rows,columns,deadline):
    left_mask=(1<<columns)-1;pivots={};relations={}
    for i,row in enumerate(tqdm(rows,desc='complete GF3packed reduction',mininterval=5)):
        trits=encode(row,columns);witness=(1<<i,0)
        while (trits[0]|trits[1])&left_mask:
            first=((trits[0]|trits[1])&left_mask);first&=-first
            column=first.bit_length()-1
            if column not in pivots:
                if trits[1]&first:trits=negate(trits);witness=negate(witness)
                pivots[column]=(trits,witness);break
            old,old_witness=pivots[column]
            # pivot1: subtractold; pivot2: subtract2old = addold.
            if trits[0]&first:old=negate(old);old_witness=negate(old_witness)
            trits=add(trits,old);witness=add(witness,old_witness)
        else:
            coefficients=[int(bool(trits[0]>> (columns+j)&1))+2*int(bool(trits[1]>>(columns+j)&1)) for j in range(3)]
            if any(coefficients):
                first=next(value for value in coefficients if value)
                if first==2:coefficients=[2*value%3 for value in coefficients];witness=negate(witness)
                pattern=tuple(coefficients)
                if pattern not in relations:
                    weights=decoded_coefficients(witness)
                    need(plain_certificate(rows,columns,weights,coefficients),'separate ordinaryinteger certificate replay')
                    relations[pattern]=dict(rhs_affine_mod3=coefficients,original_row_weights_mod3=weights,
                        complete_left_zero_mod3=True,independent_plain_arithmetic_replay=True)
        if not i%128:need(not deadline.status()['stop_required'],'not completed within the allocated budget')
    return len(pivots),list(relations.values())


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,required=True);parser.add_argument('--seconds',type=float,required=True)
    args=parser.parse_args();deadline=CommandDeadline(args.seconds,allocation_reason='11749rows2766cols ternarybitsets, exactordinaryreplay ofallrelationwitnesses and210integerprofiles; reserve30.')
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    try:
        need(sha(MODEL)==MODEL_SHA,'frozen complete necessarymodel')
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256={MODEL.relative_to(ROOT).as_posix():MODEL_SHA,Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
            selection='All210integerprofiles a0..20,b0..9, no omissions.',
            success_criterion='Every modular exclusion retains complete original-row weights and independently replays allzero columns and nonzero RHS at exact selected profile.',
            falsification_criterion='Anytritaddition/multiplication failure, ordinaryinteger replay mismatch or missingcase vetoes certificates.',
            independent_verification_requirement='Separate agent/source checks rawweighted sums and catalogue+necessaryrowderivations before promotion.',
            scope='Conditional necessary integercount extension; finite-field inconsistency excludes integer profiles, never merely rational or graphfeasibility.'))
        for a in range(3):
            for b in range(3):
                first=(int(a==1),int(a==2));second=(int(b==1),int(b==2));total=(a+b)%3
                need(add(first,second)==(int(total==1),int(total==2)),'allnine scalartritcontrols')
        positive=[dict(terms=[[0,1],[1,1]],rhs_affine=[1,0,0]),dict(terms=[[0,2],[1,2]],rhs_affine=[2,0,0])]
        need(reduce(positive,2,deadline)[1]==[],'consistent positivecontrol')
        negative=[positive[0],dict(terms=[[0,2],[1,2]],rhs_affine=[0,0,0])]
        _,control=reduce(negative,2,deadline)
        need(len(control)==1 and control[0]['rhs_affine_mod3']==[1,0,0],'inconsistent negativecontrol')
        need(not plain_certificate(negative,2,[[0,1]],control[0]['rhs_affine_mod3']),'corruptedweightcontrol')
        model=json.loads(MODEL.read_bytes());rows=model['equations'];columns=len(model['variables'])
        rank,relations=reduce(rows,columns,deadline);save(out/'gf3_relations.json',relations)
        outcomes=[]
        for a in range(21):
            for b in range(10):
                violations=[j for j,relation in enumerate(relations) if sum(value*coefficient for value,coefficient in zip([1,a,b],relation['rhs_affine_mod3']))%3]
                # Eachrelation was already independently replayed with ordinary
                # arithmetic. Bind nonzero RHS to this actual integerprofile.
                outcomes.append(dict(parameters=[a,b],outcome='REJECTED_NECESSARY_INTEGER_EXTENSION' if violations else 'SURVIVES_GF3',
                    first_violated_certificate=None if not violations else violations[0],
                    first_nonzero_rhs_mod3=None if not violations else sum(value*coefficient for value,coefficient in zip([1,a,b],relations[violations[0]]['rhs_affine_mod3']))%3))
        save(out/'all210_outcomes.json',outcomes)
        summary=dict(status='CANDIDATE_EXACT_ROOTED7_GF3_SCREEN',timestamp=datetime.now(timezone.utc).isoformat(),
            matrix_columns=columns,matrix_rows=len(rows),exact_gf3_rank=rank,distinct_affine_relations=len(relations),
            selected=210,completed=210,rejected=sum(row['outcome']!='SURVIVES_GF3' for row in outcomes),survivors=sum(row['outcome']=='SURVIVES_GF3' for row in outcomes),
            relation_rhs_mod3=[row['rhs_affine_mod3'] for row in relations],target_resolution='UNKNOWN',
            independent_review=None,independent_review_reason='Exactrawwitnesses and modelnecessaryderivation pending separate review.',
            elapsed_seconds=time.monotonic()-start,outputs_sha256={path.relative_to(ROOT).as_posix():sha(path) for path in out.iterdir() if path.is_file()})
        save(out/'summary.json',summary);print(json.dumps(summary),flush=True)
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),elapsed_seconds=time.monotonic()-start,target_resolution='UNKNOWN'));raise


if __name__=='__main__':main()
