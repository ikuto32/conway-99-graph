"""Independent recurrence/character checking; no producer or optimizer imports."""
import argparse
import copy
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys
from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
WEIGHTS=list(range(36,61,2))
SPEC='acceleration/audit_20261003_incidence_code_dual_v1_spec.md'
NOTE='acceleration/audit_20261003_incidence_code_dual_v1.md'

def need(ok,stage):
    if not ok:raise ValueError(stage)
def sha(path):
    with path.open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def save(path,obj):
    with path.open('x',encoding='utf8',newline='\n')as stream:json.dump(obj,stream,indent=2);stream.write('\n')
def pair(v):return[v.numerator,v.denominator]
def rational(raw):
    need(type(raw)is list and len(raw)==2 and all(type(x)is int for x in raw)and raw[1]>0,'RATIONAL_SYNTAX')
    return Fraction(*raw)
def polynomials(n,w):
    need(type(n)is int and n>=0 and type(w)is int and 0<=w<=n,'POLYNOMIAL_DOMAIN')
    values=[1]
    if n:values.append(n-2*w)
    for j in range(1,n):
        numerator=(n-2*w)*values[j]-(n-j+1)*values[j-1]
        need(numerator%(j+1)==0,'RECURRENCE_DIVISIBILITY')
        values.append(numerator//(j+1))
    return values
def exact_dual(n,weights,y):
    need(len(y)==n,'DUAL_LENGTH')
    need(all(v>=0 for v in y),'DUAL_NONNEGATIVE')
    zero=polynomials(n,0);need(all(v>0 for v in zero),'ZERO_WEIGHT_POSITIVE')
    lhs=[-sum(y[j-1]*Fraction(polynomials(n,w)[j],zero[j])for j in range(1,n+1))for w in weights]
    need(all(v>=1 for v in lhs),'DUAL_INEQUALITY')
    bound=1+sum(y);dimension=0
    while Fraction(1<<(dimension+1))<=bound:dimension+=1
    need(Fraction(1<<dimension)<=bound<Fraction(1<<(dimension+1)),'EXACT_POWER_OF_TWO')
    return bound,lhs,dimension
def distribution(n,words):
    need(len(words)==len(set(words))and 0 in words and all(type(w)is int and 0<=w<1<<n for w in words),'CODE_WORD_DOMAIN')
    need(all(x^y in words for x in words for y in words),'CODE_LINEARITY')
    histogram=[sum(w.bit_count()==j for w in words)for j in range(n+1)]
    sums=[]
    for j in range(n+1):
        total=sum(histogram[w]*polynomials(n,w)[j]for w in range(n+1))
        dual_count=sum(all((u&x).bit_count()%2==0 for x in words)for u in range(1<<n)if u.bit_count()==j)
        need(total==len(words)*dual_count and total>=0,'CHARACTER_POSITIVITY')
        sums.append(total)
    return dict(size=len(words),weight_histogram=histogram,character_sums=sums)
def rejected(action,stage):
    try:action()
    except ValueError as error:need(str(error)==stage,'WRONG_CONTROL_STAGE');return stage
    raise ValueError('MISSING_CONTROL_REJECTION')
def check_model(model,n,weights):
    need(model['length']==n and model['nonzero_weights']==weights and model['degrees']==list(range(1,n+1))and model['rhs']==[1]*len(weights),'MODEL_SCOPE')
    zero=polynomials(n,0)
    expected=[[-Fraction(polynomials(n,w)[j],zero[j])for j in range(1,n+1)]for w in weights]
    need(len(model['coefficient_pairs'])==len(weights)and all(len(row)==n for row in model['coefficient_pairs']),'MODEL_DIMENSIONS')
    actual=[[rational(c)for c in row]for row in model['coefficient_pairs']]
    need(actual==expected,'MODEL_COEFFICIENT')
    return expected
def check_certificate(cert,n,weights):
    need(cert['schema']=='BINARY_CODE_COMPLETE_RATIONAL_DUAL_V1'and cert['length']==n and cert['nonzero_weights']==weights and cert['degrees']==list(range(1,n+1)),'CERTIFICATE_SCOPE')
    y=[rational(v)for v in cert['dual_pairs']]
    bound,lhs,dimension=exact_dual(n,weights,y)
    need([rational(v)for v in cert['lhs_pairs']]==lhs,'ADVERTISED_LHS')
    need(rational(cert['exact_size_upper'])==bound,'ADVERTISED_SIZE_BOUND')
    need(cert['maximum_linear_dimension']==dimension and cert['conditional_incidence_rank_lower']==n-dimension,'ADVERTISED_POWER_OF_TWO')
    need(cert['optimum_asserted']is False and cert['target_resolution']=='NONE','CERTIFICATE_LIMITATIONS')
    return bound,lhs,dimension
def calibrate():
    character_checks=0
    for n in range(7):
        for w in range(n+1):
            values=polynomials(n,w);x=(1<<w)-1
            for j in range(n+1):
                literal=sum(1 if (x&u).bit_count()%2==0 else -1 for u in range(1<<n)if u.bit_count()==j)
                need(values[j]==literal,'RECURRENCE_LITERAL_CHARACTER');character_checks+=1
    full=distribution(4,list(range(16)))
    even=distribution(3,[0,3,5,6])
    adjacency=[[int(i!=j and(i//3==j//3 or i%3==j%3))for j in range(9)]for i in range(9)]
    triples=[(i,j,k)for i in range(9)for j in range(i+1,9)for k in range(j+1,9)if adjacency[i][j]and adjacency[i][k]and adjacency[j][k]]
    rook_words=[x for x in range(512)if all(sum(x>>v&1 for v in triple)%2==0 for triple in triples)]
    rook=distribution(9,rook_words);need(rook['size']==16 and rook['weight_histogram'][4]==9 and rook['weight_histogram'][6]==6,'ROOK_KERNEL')
    dual=[Fraction(v)for v in polynomials(4,0)[1:]]
    bound,lhs,dim=exact_dual(4,list(range(1,5)),dual);need(bound==16 and lhs==[1]*4 and dim==4,'FULL_CODE_DUAL')
    even_dual=[Fraction(0),Fraction(3),Fraction(0)]
    need(exact_dual(3,[2],even_dual)[0]==4,'EVEN_CODE_DUAL')
    negatives=[]
    for label,fn,stage in[
        ('truncated',lambda:exact_dual(4,[1,2,3,4],dual[:-1]),'DUAL_LENGTH'),
        ('negative',lambda:exact_dual(4,[1,2,3,4],[-dual[0],*dual[1:]]),'DUAL_NONNEGATIVE'),
        ('zero',lambda:exact_dual(4,[1,2,3,4],[Fraction(0)]*4),'DUAL_INEQUALITY'),
        ('half',lambda:exact_dual(4,[1,2,3,4],[v/2 for v in dual]),'DUAL_INEQUALITY'),
        ('invalid_rational',lambda:rational([1,0]),'RATIONAL_SYNTAX'),
        ('nonlinear_words',lambda:distribution(3,[0,1,2]),'CODE_LINEARITY')]:
        negatives.append(dict(case=label,diagnostic=rejected(fn,stage)))
    model=dict(length=3,nonzero_weights=[2],degrees=[1,2,3],rhs=[1],coefficient_pairs=[[pair(-Fraction(polynomials(3,2)[j],polynomials(3,0)[j]))for j in range(1,4)]])
    check_model(model,3,[2]);bad=copy.deepcopy(model);bad['coefficient_pairs'][0][1]=[0,1]
    negatives.append(dict(case='changed_coefficient',diagnostic=rejected(lambda:check_model(bad,3,[2]),'MODEL_COEFFICIENT')))
    return dict(status='INDEPENDENT_INCIDENCE_CODE_DUAL_RECURRENCE_CALIBRATION_V1_PASS',positive_fixtures=5,strict_negative_controls=negatives,complete_small_character_checks=character_checks,full_binary_code=full,even_length3_code=even,complete_rook_kernel=rook,producer_output_inspected=False,scope='Finite checker calibration only, not target/code bound approval.')
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['calibrate','check']);p.add_argument('--seconds',type=float,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--summary',type=Path);p.add_argument('--summary-sha256');p.add_argument('--calibration',type=Path);p.add_argument('--calibration-sha256');args=p.parse_args()
    deadline=CommandDeadline(args.seconds,allocation_reason='Independent tiny exact recurrence, character controls and13x99 rational dual replay; no optimizer/elimination/imports.')
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    try:
        pins={path:sha(ROOT/path)for path in[SPEC,NOTE,Path(__file__).resolve().relative_to(ROOT).as_posix(),'acceleration/command_deadline.py','pyproject.toml','uv.lock']}
        if args.mode=='calibrate':
            report=calibrate();report.update(timestamp=datetime.now(timezone.utc).isoformat(),command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256=pins,producer='/root',verifier='/root/structural',shared_components=['Same stated binary code domain; independently implemented recurrence and direct character sums.','Python standard library/deadline helper only; no producer, optimizer or numerical arithmetic imports.']);save(out/'summary.json',report);return
        need(args.summary and args.calibration and sha(args.summary)==args.summary_sha256 and sha(args.calibration)==args.calibration_sha256,'EXACT_INPUT_PINS')
        cal=json.loads(args.calibration.read_bytes());need(cal['status']=='INDEPENDENT_INCIDENCE_CODE_DUAL_RECURRENCE_CALIBRATION_V1_PASS'and cal['inputs_sha256'][Path(__file__).resolve().relative_to(ROOT).as_posix()]==pins[Path(__file__).resolve().relative_to(ROOT).as_posix()],'UNCHANGED_PREOUTPUT_CALIBRATION')
        producer=json.loads(args.summary.read_bytes());need(producer['status']=='CANDIDATE_EXACT_DUAL','PRODUCER_CANDIDATE_EXISTS')
        for name,expected in producer['inputs_outputs_sha256'].items():need(sha(ROOT/name)==expected,'PRODUCER_ARTIFACT_IDENTITY '+name);pins[name]=expected
        folder=args.summary.resolve().parent;cert=json.loads((folder/'certificate.json').read_bytes());model=json.loads((folder/'exact_model.json').read_bytes())
        coefficients=check_model(model,99,WEIGHTS);bound,lhs,dimension=check_certificate(cert,99,WEIGHTS)
        need(producer['candidate']==cert,'SUMMARY_RAW_CERTIFICATE_IDENTITY')
        controls=[]
        bad=copy.deepcopy(cert);bad['dual_pairs']=[[-1,1],*bad['dual_pairs'][1:]];controls.append(dict(case='actual_negative_coordinate',diagnostic=rejected(lambda:check_certificate(bad,99,WEIGHTS),'DUAL_NONNEGATIVE')))
        bad=copy.deepcopy(cert);bad['dual_pairs']=[[0,1]]*99;controls.append(dict(case='actual_zero_dual',diagnostic=rejected(lambda:check_certificate(bad,99,WEIGHTS),'DUAL_INEQUALITY')))
        bad=copy.deepcopy(cert);bad['exact_size_upper']=[bound.numerator+1,bound.denominator];controls.append(dict(case='actual_changed_size_bound',diagnostic=rejected(lambda:check_certificate(bad,99,WEIGHTS),'ADVERTISED_SIZE_BOUND')))
        bad=copy.deepcopy(model);value=rational(bad['coefficient_pairs'][0][0]);bad['coefficient_pairs'][0][0]=pair(value+1);controls.append(dict(case='actual_changed_coefficient',diagnostic=rejected(lambda:check_model(bad,99,WEIGHTS),'MODEL_COEFFICIENT')))
        save(out/'corruption_controls.json',controls)
        pins[args.summary.resolve().relative_to(ROOT).as_posix()]=args.summary_sha256;pins[args.calibration.resolve().relative_to(ROOT).as_posix()]=args.calibration_sha256;pins[(out/'corruption_controls.json').relative_to(ROOT).as_posix()]=sha(out/'corruption_controls.json')
        report=dict(status='INDEPENDENT_INCIDENCE_CODE_COMPLETE_DUAL_V1_PASS',timestamp=datetime.now(timezone.utc).isoformat(),producer='/root',verifier='/root/structural',method='independent_artifact_check_and_derivation',command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256=pins,complete_coefficients_checked=1287,complete_nonnegative_dual_coordinates_checked=99,complete_weight_inequalities_checked=13,exact_lhs_pairs=[pair(v)for v in lhs],exact_size_upper=pair(bound),maximum_linear_dimension=dimension,conditional_incidence_rank_lower=99-dimension,optimum_asserted=False,target_resolution='NONE',pre_output_calibration=args.calibration.resolve().relative_to(ROOT).as_posix(),written_derivation=NOTE,shared_components=cal['shared_components'],actual_strict_corruption_controls=4,rank_upper_assumed=False,limitations=['Complete rational dual certifies a code-size upper bound, not optimizer optimality.','Target rank consequence uses the separately independently derived incidence-kernel weight36..60 premise.','No code construction, target existence/nonexistence or rank upper bound is established.','No novelty/external-review or target-wide coverage claim.'],deadline=deadline.status())
        save(out/'summary.json',report)
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),timestamp=datetime.now(timezone.utc).isoformat(),completed_outputs_preserved=True));raise

if __name__=='__main__':main()
