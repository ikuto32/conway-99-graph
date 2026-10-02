"""Independent literal LP lifts, strict exact certificates and complete witnesses.

No discovery/solver imports. This checker uses Python integers/Fraction and the
shared invocation deadline only. Its controls run before raw result checking.
"""
import argparse, copy, hashlib, itertools, json, math, platform, subprocess, sys, time
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from tqdm import tqdm
from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
P='acceleration/results/'
BASE=P+'20261002_rooted7_unrestricted_extension01/model.json'
BASE_SHA='9f636889690071f69ad7a103b02abb2f43a5bbc2d2114c87a779da29c0f647a1'
AUDIT=P+'20261002_independent_review/rooted7_unrestricted_model01/summary.json'
AUDIT_SHA='e7631851f9cc5716c9d8a1bf5b30f9a4644d8e2170f116d1bb30378fbeb16d70'
RUN=P+'20261002_rooted7_unrestricted_corners01/'
SPEC='acceleration/audit_20261003_rooted7_unrestricted_lp_v2_spec.md'
PROOF='acceleration/audit_20261003_rooted7_unrestricted_lp_v2_proof.md'
PRODUCER='acceleration/theory_20261002_rooted7_unrestricted_corners_v3.py'
PINS={BASE:BASE_SHA,AUDIT:AUDIT_SHA,PRODUCER:'66a53b41d9ae30251325deb10ae291c8735ddd3b6a81785b5657c3a43eb9c326',
      'acceleration/theory_20261002_rooted7_unrestricted_corners_v1.py':'5a185a2b561f34a35b25593bbee23b4dd3af3b4476223cb6a22c857c98e4fcf4',
      'docs/PROTOCOL_20261002_UNRESTRICTED_ROOTED7_CORNERS_V3.md':'30148ecdb2f2d4e492fdc58e260eca9d1d1b911e24fa9bdde14a7985362f66e3',
      RUN+'global_domain_operator.json':'7e409f13e8e7ed29b67124b82163a8a7bcc8ed59dd1bb0458077687afb0d8a14',
      RUN+'c_ge_1_slice_operator.json':'6f9428f4a2bbe5b99bf1e0ec9cdcf52e212281f47f793a68a4bee3c1e7b12991',
      RUN+'global_domain.json':'52e6c582a2ab68e4946c57ec71c75d85d6820b7d460f2012e29cfec316a1fbf0',
      RUN+'c_ge_1_slice.json':'aee38a53c12835577f18d5b0e6d8f29afc257eb48151714d06877276e335e512',
      RUN+'all651_rational_witnesses.jsonl':'d699698d694215a8552bb5dca7080932c7907f8ef88eced7690d7fe23bf51cfd',
      RUN+'all651_outcomes.json':'360dab33ed611d96d407aee99093d0eaf62505f6fb791f95638b995a7b544d60'}
CORNERS=[(c,a,b) for c in (0,2) for a in (0,20) for b in (0,9+c//2)]
POPULATION=[(c,a,b) for c in range(3) for a in range(21) for b in range(10+c//2)]

class AuditError(ValueError):
    def __init__(self,stage):self.stage=stage;super().__init__(stage)
def need(ok,stage):
    if not ok:raise AuditError(stage)
def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def save(path,obj):
    with path.open('x',encoding='utf8',newline='\n') as stream:json.dump(obj,stream,indent=2,sort_keys=True);stream.write('\n')
def pairs(items):
    result={}
    for k,v in items:need(k not in result,'DUPLICATE_KEY');result[k]=v
    return result
def decode(text):return json.loads(text,object_pairs_hook=pairs)
def load(path):return decode(path.read_text(encoding='utf8'))
def integer(x):return type(x) is int
def vector(x,n,stage):need(type(x) is list and len(x)==n and all(integer(v) for v in x),stage);return x
def parameters(x):
    vector(x,3,'PARAMETER_SHAPE');c,a,b=x
    need(0<=c<=2 and 0<=a<=20 and 0<=2*b<=18+c,'PARAMETER_DOMAIN');return x
def receipt(raw):
    need(type(raw) is dict and type(raw.get('cleanup')) is dict,'RECEIPT_SHAPE')
    need(raw.get('command_exit_code')==0 and raw['cleanup'].get('reaped') is True and raw['cleanup'].get('job_active_zero_observed') is True,'PRODUCER_TERMINAL_CONTAINMENT')
def rows(raw,columns):
    need(type(raw) is list and integer(columns) and columns>0,'OPERATOR_SHAPE')
    for r in raw:
        need(type(r) is dict and type(r.get('terms')) is list,'ROW_SHAPE')
        vector(r.get('rhs_affine'),4,'RHS_SHAPE');previous=-1
        for term in r['terms']:
            vector(term,2,'TERM_SHAPE');j,coefficient=term
            need(previous<j<columns and coefficient!=0,'TERM_INDEX_UNIQUENESS');previous=j
    return raw
def lift(raw,n,slice_):
    """Move the three parameter-dependent RHS coefficients to the left side."""
    result=[]
    for r in rows(raw,n):
        coefficients={j:q for j,q in r['terms']}
        for coordinate in range(1,4):
            q=r['rhs_affine'][coordinate]
            if q:coefficients[n+coordinate-1]=-q
        result.append({'terms':[[j,coefficients[j]] for j in sorted(coefficients)],'rhs_affine':[r['rhs_affine'][0],0,0,0]})
    for coeff,const in [({n:1,n+3:1},2),({n+1:1,n+4:1},20),({n:-1,n+2:2,n+5:1},18)]:
        result.append({'terms':[[j,coeff[j]] for j in sorted(coeff)],'rhs_affine':[const,0,0,0]})
    if slice_:result.append({'terms':[[n,1],[n+6,-1]],'rhs_affine':[1,0,0,0]})
    return result
def lifted_object(raw,n,slice_):
    return {'format':'UNRESTRICTED_ROOTED7_PRIMARY_DOMAIN_LIFT_V1','base_model_sha256':BASE_SHA,
            'base_rows':len(raw),'base_columns':n,'equations':lift(raw,n,slice_),'columns':n+6+int(slice_),
            'primary_variables':{'c':n,'a':n+1,'b':n+2},
            'facet_slacks':{'2_minus_c':n+3,'20_minus_a':n+4,'18_plus_c_minus_2b':n+5},
            'c_ge_1_slack':n+6 if slice_ else None}
def verify_lift(actual,raw,n,slice_):
    expected=lifted_object(raw,n,slice_)
    need(type(actual) is dict,'LIFT_OBJECT_SHAPE')
    need({k:actual.get(k) for k in expected}==expected,'EXACT_LIFT_TRANSFORM')
    rows(actual['equations'],actual['columns']);return actual['equations']
def primal(operator,n,numerators,denominator,point):
    values=vector(numerators,n,'PRIMAL_VECTOR_SHAPE');need(integer(denominator) and denominator>0,'PRIMAL_DENOMINATOR')
    vector(point,3,'PARAMETER_SHAPE');need(all(v>=0 for v in values),'PRIMAL_NONNEGATIVE')
    affine=[1,*point]
    for index,r in enumerate(operator):
        right=sum(q*t for q,t in zip(r['rhs_affine'],affine))*denominator
        left=sum(values[j]*q for j,q in r['terms'])
        need(left==right,'PRIMAL_ROW')
    return {'rows_checked':len(operator),'coordinates_checked':n,'integer_vector':all(v%denominator==0 for v in values)}
def farkas(operator,n,multipliers,point):
    values=vector(multipliers,len(operator),'FARKAS_VECTOR_SHAPE');vector(point,3,'PARAMETER_SHAPE')
    columns=[0]*n;affine=[0]*4
    for y,r in zip(values,operator):
        for j,q in r['terms']:columns[j]+=q*y
        for j,q in enumerate(r['rhs_affine']):affine[j]+=q*y
    need(all(v>=0 for v in columns),'FARKAS_COLUMNS')
    rhs=sum(q*t for q,t in zip(affine,[1,*point]));need(rhs<0,'FARKAS_STRICT_RHS')
    return {'columns_checked':n,'rows_checked':len(operator),'rhs_affine':affine,'rhs':rhs,'column_products':columns}
def certify(record,operator,n,point,case):
    need(record.get('case',case)==case,'CERTIFICATE_CASE');need(record.get('parameters')==(None if case in ('global_domain','c_ge_1_slice') else list(point)),'CERTIFICATE_PARAMETERS')
    need(record.get('operator_rows',len(operator))==len(operator) and record.get('operator_columns',n)==n,'CERTIFICATE_OPERATOR_DIMENSIONS')
    if record.get('status')=='CANDIDATE_EXACT_RATIONAL_PRIMAL':
        result=primal(operator,n,record.get('certificate_numerators'),record.get('certificate_denominator'),list(point))
        need(record.get('integer_vector')==result['integer_vector'],'CERTIFICATE_INTEGRALITY');return dict(kind='exact_rational_primal',**result)
    if record.get('status')=='CANDIDATE_EXACT_FARKAS_EXCLUSION':
        result=farkas(operator,n,record.get('certificate_multipliers'),list(point))
        need(record.get('certificate_rhs_affine')==result['rhs_affine'],'FARKAS_RECORDED_RHS');return dict(kind='exact_farkas',**result)
    raise AuditError('NO_COMPLETE_EXACT_CERTIFICATE')
def weights(point):
    """Independent bilinear interpolation between the lower/upper c faces."""
    c,a,b=parameters(list(point));lower=Fraction(2-c,2);upper=Fraction(c,2)
    # The b-high face has height 9 on c=0 and 10 on c=2; linear height is (18+c)/2.
    high=Fraction(2*b,18+c);low=1-high;left=Fraction(20-a,20);right=1-left
    result=[C*A*B for C in (lower,upper) for A in (left,right) for B in (low,high)]
    need(all(w>=0 for w in result) and sum(result)==1,'INTERPOLATION_WEIGHTS')
    need([sum(w*p[j] for w,p in zip(result,CORNERS)) for j in range(3)]==list(point),'INTERPOLATION_PARAMETERS')
    return result
def control_suite():
    records=[]
    def positive(name,fn):fn();records.append({'name':name,'expected':'PASS','outcome':'PASS'})
    def negative(name,stage,fn):
        try:fn()
        except AuditError as e:need(e.stage==stage,'CONTROL_WRONG_FAILURE');records.append({'name':name,'expected':stage,'outcome':e.stage});return
        raise AuditError('CONTROL_FALSE_ACCEPT')
    tiny=[{'terms':[[0,2]],'rhs_affine':[1,1,0,0]}]
    glob=lifted_object(tiny,1,False);sli=lifted_object(tiny,1,True)
    gv=[1,0,0,0,4,40,36];sv=[2,2,0,0,2,40,38,0]
    positive('global_literal_transform',lambda:verify_lift(glob,tiny,1,False))
    positive('slice_literal_transform',lambda:verify_lift(sli,tiny,1,True))
    positive('global_fractional_primal',lambda:primal(glob['equations'],7,gv,2,[0,0,0]))
    positive('slice_fractional_primal',lambda:primal(sli['equations'],8,sv,2,[0,0,0]))
    negative('upper_facet_primal', 'PRIMAL_ROW',lambda:primal(glob['equations'],7,gv[:-1]+[35],2,[0,0,0]))
    negative('c0_slice_primal','PRIMAL_ROW',lambda:primal(sli['equations'],8,gv+[0],2,[0,0,0]))
    for name,change in [('parameter_sign',lambda x:x['equations'][0]['terms'][1].__setitem__(1,1)),('upper_rhs',lambda x:x['equations'][-1]['rhs_affine'].__setitem__(0,19)),('omitted_row',lambda x:x['equations'].pop()),('wrong_primary_index',lambda x:x['primary_variables'].__setitem__('c',2))]:
        bad=copy.deepcopy(glob);change(bad);negative('lift_'+name,'EXACT_LIFT_TRANSFORM',lambda bad=bad:verify_lift(bad,tiny,1,False))
    bad=copy.deepcopy(sli);bad['equations'][-1]['terms'][1][1]=1
    negative('slice_slack_sign','EXACT_LIFT_TRANSFORM',lambda:verify_lift(bad,tiny,1,True))
    for name,v,d,stage in [('short',gv[:-1],2,'PRIMAL_VECTOR_SHAPE'),('long',gv+[0],2,'PRIMAL_VECTOR_SHAPE'),('float',[1.0,*gv[1:]],2,'PRIMAL_VECTOR_SHAPE'),('bool',[True,*gv[1:]],2,'PRIMAL_VECTOR_SHAPE'),('zero_denominator',gv,0,'PRIMAL_DENOMINATOR'),('bool_denominator',gv,True,'PRIMAL_DENOMINATOR'),('negative',[1,-1,*gv[2:]],2,'PRIMAL_NONNEGATIVE')]:
        negative('primal_'+name,stage,lambda v=v,d=d:primal(glob['equations'],7,v,d,[0,0,0]))
    impossible=[{'terms':[[0,1]],'rhs_affine':[-1,0,0,0]}]
    positive('literal_farkas',lambda:farkas(impossible,1,[1],[0,0,0]))
    negative('farkas_sign','FARKAS_COLUMNS',lambda:farkas(impossible,1,[-1],[0,0,0]))
    negative('farkas_zero_rhs','FARKAS_STRICT_RHS',lambda:farkas(impossible,1,[0],[0,0,0]))
    for name,v in [('short',[]),('long',[1,0]),('float',[1.0]),('bool',[True])]:negative('farkas_'+name,'FARKAS_VECTOR_SHAPE',lambda v=v:farkas(impossible,1,v,[0,0,0]))
    impossible_global=lift(impossible,1,False)
    positive('global_farkas_with_slacks',lambda:farkas(impossible_global,7,[1,0,0,0],[0,0,0]))
    zero_c=[{'terms':[],'rhs_affine':[0,1,0,0]}];zero_slice=lift(zero_c,1,True)
    positive('slice_only_farkas',lambda:farkas(zero_slice,8,[-1,0,0,0,-1],[0,0,0]))
    negative('slice_farkas_wrong_sign','FARKAS_COLUMNS',lambda:farkas(zero_slice,8,[1,0,0,0,1],[0,0,0]))
    negative('out_of_domain','PARAMETER_DOMAIN',lambda:parameters([2,0,11]))
    negative('duplicate_json_key','DUPLICATE_KEY',lambda:decode('{"numerators": [1], "numerators": [2]}'))
    negative('duplicate_term','TERM_INDEX_UNIQUENESS',lambda:rows([{'terms':[[0,1],[0,2]],'rhs_affine':[0,0,0,0]}],1))
    negative('term_outside_universe','TERM_INDEX_UNIQUENESS',lambda:rows([{'terms':[[1,1]],'rhs_affine':[0,0,0,0]}],1))
    positive('all_651_exact_weight_coordinates',lambda:[weights(p) for p in POPULATION])
    good_receipt={'command_exit_code':0,'cleanup':{'reaped':True,'job_active_zero_observed':True}}
    positive('nested_supervisor_receipt',lambda:receipt(good_receipt))
    negative('old_flat_receipt','RECEIPT_SHAPE',lambda:receipt({'command_exit_code':0,'reaped':True,'job_active_zero_observed':True}))
    for label,field,value in [('unreaped','reaped',False),('nonempty_group','job_active_zero_observed',False)]:
        corrupted=copy.deepcopy(good_receipt);corrupted['cleanup'][field]=value
        negative('receipt_'+label,'PRODUCER_TERMINAL_CONTAINMENT',lambda corrupted=corrupted:receipt(corrupted))
    negative('receipt_exit_error','PRODUCER_TERMINAL_CONTAINMENT',lambda:receipt({'command_exit_code':1,'cleanup':good_receipt['cleanup']}))
    return records
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--controls-only',action='store_true');ap.add_argument('--calibration',type=Path);ap.add_argument('--calibration-sha256');args=ap.parse_args()
    deadline=CommandDeadline(args.seconds,allocation_reason='Independent complete lifts/10 certificates/651 witnesses;7.7M sparse integer rows,1.8M coordinates;300outer270worker30reserve, no solver')
    started=time.monotonic();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    tick=lambda:need(not deadline.status()['stop_required'],'NOT_COMPLETED_WITHIN_ALLOCATED_BUDGET')
    own=[Path(__file__).relative_to(ROOT).as_posix(),SPEC,PROOF,'uv.lock','pyproject.toml','acceleration/command_deadline.py','acceleration/run_compute_command.py']
    identity={p:sha(ROOT/p) for p in own}
    try:
        controls=control_suite();save(out/'controls.json',controls)
        manifest={'timestamp':datetime.now(timezone.utc).isoformat(),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'command':[sys.executable,*sys.argv],'cwd':str(ROOT),'python_version':platform.python_version(),'verifier':'/root/checkpoint_audit','inputs_sha256':identity,'discovery_imports':[],'numerical_tolerance':None,'numerical_tolerance_reason':'All acceptance checks use exact integers/rationals.'}
        if args.controls_only:
            save(out/'manifest.json',manifest);save(out/'summary.json',dict(status='INDEPENDENT_UNRESTRICTED_ROOTED7_LP_V2_CALIBRATION_PASS',timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=identity,controls_passed=len(controls),positive_controls=sum(r['expected']=='PASS' for r in controls),strict_negative_controls=sum(r['expected']!='PASS' for r in controls),elapsed_seconds=time.monotonic()-started,deadline=deadline.status(),scope='Finite exact checker/lift controls only; no research certificate approval.'));return
        need(args.calibration is not None and args.calibration_sha256 is not None,'CALIBRATION_REQUIRED');need(sha(args.calibration)==args.calibration_sha256,'CALIBRATION_HASH')
        calibration=load(args.calibration);need(calibration['status']=='INDEPENDENT_UNRESTRICTED_ROOTED7_LP_V2_CALIBRATION_PASS' and calibration['inputs_sha256']==identity,'CALIBRATION_CURRENT_SOURCE')
        identity[args.calibration.resolve().relative_to(ROOT).as_posix()]=args.calibration_sha256
        for p,digest in PINS.items():tick();need(sha(ROOT/p)==digest,'FROZEN_INPUT_HASH');identity[p]=digest
        producer_summary=load(ROOT/RUN/'summary.json');producer_manifest=load(ROOT/RUN/'manifest.json')
        for p,digest in {**producer_manifest['inputs_sha256'],**producer_summary['outputs_sha256']}.items():tick();need(sha(ROOT/p)==digest,'PRODUCER_CLOSURE_HASH');identity[p]=digest
        for p in [RUN+'summary.json',P+'20261002_rooted7_unrestricted_corners_supervisor01/summary.json',P+'20261002_rooted7_unrestricted_corner_calibration01/summary.json',P+'20261002_rooted7_unrestricted_corner_source_supervisor01/producer_source_v2.py.txt']:
            identity[p]=sha(ROOT/p)
        supervisor=load(ROOT/(P+'20261002_rooted7_unrestricted_corners_supervisor01/summary.json'))
        receipt(supervisor)
        model=load(ROOT/BASE);n=len(model['variables']);raw=rows(model['equations'],n);need(n==2810 and len(raw)==11769,'BASE_DIMENSIONS')
        need(producer_manifest['selected_corners']==list(map(list,CORNERS)) and producer_manifest['selected_integer_parameter_profiles']==list(map(list,POPULATION)),'FROZEN_POPULATION')
        actual_ops={};reports=[];records=[]
        for slice_ in (False,True):
            name='c_ge_1_slice' if slice_ else 'global_domain';actual=load(ROOT/RUN/(name+'_operator.json'));op=verify_lift(actual,raw,n,slice_);actual_ops[name]=op
            record=load(ROOT/RUN/(name+'.json'));report=certify(record,op,actual['columns'],(0,0,0),name);reports.append(dict(case=name,**report));records.append(record)
            if report['kind']=='exact_rational_primal':
                d=record['certificate_denominator'];v=record['certificate_numerators'];point=[Fraction(v[n+j],d) for j in range(3)]
                need(0<=point[0]<=2 and 0<=point[1]<=20 and 0<=2*point[2]<=18+point[0] and (not slice_ or point[0]>=1),'LIFTED_PRIMAL_DOMAIN')
                reports[-1]['actual_parameters']=[[q.numerator,q.denominator] for q in point]
        corner_records=[]
        for index,point in enumerate(CORNERS):
            tick();record=load(ROOT/RUN/f'corner_{index}.json');report=certify(record,raw,n,point,f'corner_{index}');reports.append(dict(case=f'corner_{index}',parameters=list(point),**report));corner_records.append(record)
        need(all(r['kind']=='exact_rational_primal' for r in reports),'EXPECTED_TEN_PRIMALS')
        # Important raw-artifact corruption controls, after the pre-output checker calibration.
        bad=copy.deepcopy(corner_records[0]);bad['certificate_numerators'][0]+=1
        try:certify(bad,raw,n,CORNERS[0],'corner_0')
        except AuditError as e:need(e.stage=='PRIMAL_ROW','RAW_CONTROL_WRONG_FAILURE');controls.append(dict(name='raw_corner_coordinate_plus_one',expected='PRIMAL_ROW',outcome=e.stage))
        else:raise AuditError('RAW_CONTROL_FALSE_ACCEPT')
        for name,where in [('literal_base_coefficient','coefficient'),('literal_base_rhs','rhs')]:
            corrupted=copy.deepcopy(raw)
            if where=='coefficient':
                at=next(i for i,r in enumerate(raw) if any(corner_records[0]['certificate_numerators'][j]!=0 for j,q in r['terms']))
                j=next(j for j,q in raw[at]['terms'] if corner_records[0]['certificate_numerators'][j]!=0)
                term=next(t for t in corrupted[at]['terms'] if t[0]==j);term[1]+=1
            else:corrupted[0]['rhs_affine'][0]+=1
            try:primal(corrupted,n,corner_records[0]['certificate_numerators'],corner_records[0]['certificate_denominator'],list(CORNERS[0]))
            except AuditError as e:need(e.stage=='PRIMAL_ROW','RAW_CONTROL_WRONG_FAILURE');controls.append(dict(name=name,expected='PRIMAL_ROW',outcome=e.stage))
            else:raise AuditError('RAW_CONTROL_FALSE_ACCEPT')
        outcomes=load(ROOT/RUN/'all651_outcomes.json');need(type(outcomes) is list and len(outcomes)==651,'OUTCOME_POPULATION')
        witness_reports=[];integer_points=[];rows_checked=0;coordinates_checked=0
        with (ROOT/RUN/'all651_rational_witnesses.jsonl').open('r',encoding='utf8') as stream:
            for index,line in enumerate(tqdm(stream,total=651,desc='Independent651 raw rational vector checks',mininterval=5)):
                tick();need(index<len(POPULATION),'WITNESS_EXTRA_RECORD');point=POPULATION[index];witness=decode(line);need(witness.get('parameters')==list(point),'WITNESS_POPULATION_ORDER')
                parameters(witness['parameters']);result=primal(raw,n,witness.get('numerators'),witness.get('denominator'),list(point));rows_checked+=result['rows_checked'];coordinates_checked+=n
                ws=weights(point);need(witness.get('corner_weights')==[[w.numerator,w.denominator] for w in ws],'WITNESS_WEIGHT_RECORD')
                common=math.lcm(*(w.denominator*r['certificate_denominator'] for w,r in zip(ws,corner_records)))
                factors=[w.numerator*(common//(w.denominator*r['certificate_denominator'])) for w,r in zip(ws,corner_records)]
                reconstructed=[sum(k*r['certificate_numerators'][j] for k,r in zip(factors,corner_records)) for j in range(n)]
                need(all(left*witness['denominator']==right*common for left,right in zip(reconstructed,witness['numerators'])),'WITNESS_COMPLETE_INTERPOLATION')
                expected={'parameters':list(point),'status':'CANDIDATE_EXACT_RATIONAL_PRIMAL','integer_vector':result['integer_vector']};need(outcomes[index]==expected,'OUTCOME_EXACT_CLASSIFICATION')
                if result['integer_vector']:integer_points.append(list(point))
                witness_reports.append(dict(parameters=list(point),integer_vector=result['integer_vector'],rows_checked=result['rows_checked'],coordinates_checked=n,denominator=witness['denominator']))
        need(len(witness_reports)==651 and len(integer_points)==21,'COMPLETE_WITNESS_COUNT')
        need(producer_summary['completed_actual_exact_convex_witnesses']==651 and producer_summary['integer_count_vectors']==21 and producer_summary['exact_ray_excluded_profiles']==0 and producer_summary['unknown_profiles']==0,'SUMMARY_EXACT_COUNTS')
        save(out/'raw_controls.json',controls);save(out/'checked_cases.json',reports);save(out/'checked_profiles.json',witness_reports);save(out/'integral_profiles.json',integer_points)
        reconstructed={k:lifted_object(raw,n,k=='c_ge_1_slice') for k in actual_ops};save(out/'reconstructed_lifts.json',reconstructed)
        manifest['inputs_sha256']=identity;manifest['producer_source_commit']=producer_manifest['source_commit'];manifest['producer_command']=producer_manifest['command'];manifest['producer_cwd']=producer_manifest['cwd'];manifest['producer_versions']={k:producer_manifest[k] for k in ('python_version','highs_version','numpy_version')};save(out/'manifest.json',manifest)
        statement='For the frozen independently reconstructed unrestricted rooted7 necessary operator with 2810 nonnegative variables and 11769 affine equations, both literal domain lifts (2816 variables/11772 equations and c>=1 slice2817 variables/11773 equations) exactly encode their declared parameter domains and have complete nonnegative rational primal witnesses. All eight fixed corners and all651 integer primary profiles have complete exact nonnegative rational witnesses in the original operator;21 of the saved651 count vectors are integral. These witnesses establish feasibility of these necessary linear count relaxations only, and establish neither graph realization nor an exclusion.'
        save(out/'summary.json',dict(status='INDEPENDENT_UNRESTRICTED_ROOTED7_LP_TEN_PRIMALS_651_WITNESSES_V2_PASS',timestamp=datetime.now(timezone.utc).isoformat(),statement=statement,verifier='/root/checkpoint_audit',producer='/root/structural',inputs_sha256=identity,exact_lift_rows_checked=11772+11773,complete_case_population=10,complete_exact_primal_cases=len(reports),complete_exact_farkas_cases=0,frozen_profile_population=651,complete_saved_profile_vectors=651,integer_count_vectors=21,profile_row_checks=rows_checked,profile_coordinates_checked=coordinates_checked,case_row_checks=sum(r['rows_checked'] for r in reports),case_coordinates_checked=sum(r['coordinates_checked'] for r in reports),strict_negative_controls=sum(c['expected']!='PASS' for c in controls),positive_controls=sum(c['expected']=='PASS' for c in controls),exclusions=0,target_resolution='NONE',overall_search_coverage='UNKNOWN; no validated denominator.',producer_terminal_state={'command_exit_code':0,'reaped':True,'job_active_zero_observed':True},shared_components=['command_deadline.py and supported supervisor; Python3.12.10/tqdm; pinned prior independent model necessity derivation reused without recomputation'],limitations=['No discovery/solver code imported or numerical result accepted.','No independent numeric solver rerun, rank or optimality claim.','21 integral count vectors are not decoded or realized graphs.','Global/slice vectors may use rational primary parameters; explicit exact values recorded.','The producer helper shape/length checks were weaker than this checker; full exact shape/type/length checks used here.','Historical transitive evidence hashes not recursively replayed; direct pinned inputs and completed outputs authenticated.','Original malformed V2 source-only AST failure preserved; V3 did not reuse its failed approval.','Independent checker V1 calibrated but not used for full replay: receipt shape correction preserved in new V2 and separately recalibrated.'],elapsed_seconds=time.monotonic()-started,deadline=deadline.status(),outputs_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in out.iterdir() if p.is_file()}))
    except BaseException as error:
        save(out/'failure.json',{'timestamp':datetime.now(timezone.utc).isoformat(),'error':repr(error),'stage':getattr(error,'stage',None),'elapsed_seconds':time.monotonic()-started,'all_completed_outputs_preserved':True});raise
if __name__=='__main__':main()
