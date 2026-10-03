"""UNEXECUTED four-image-count target-kernel guide; each domain has explicit scope."""
import argparse
from collections import Counter
from datetime import datetime,timezone
from fractions import Fraction
import hashlib
from itertools import combinations
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
import time
from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
SPEC='acceleration/theory_20261003_incidence_four_low_counts_lp_v2_spec.md'
BASE='acceleration/theory_20261003_incidence_code_lp_v2.py'
BASE_SHA='453de424f08c5e87a2f8e9e08202b592c19fd7d1ddefc6119cd21e002b8d5edf'
WEIGHT_AUDIT='acceleration/results/20261003_independent_review/incidence_griesmer01/summary.json'
WEIGHT_AUDIT_SHA='f6d37038fa7f5969331e8d7ee9490bdcc6ebda09b3a0770b7a99dea298a9c59b'
PRESERVED13='acceleration/theory_20261003_incidence_low_weight_lp_v1.py'
PRESERVED13_SHA='90002c96a9b192562e299bc832ac2e7a6162899b3e97418549023b40d3f32045'
PRESERVED7='acceleration/theory_20261003_incidence_low_weight_lp_v2.py'
PRESERVED7_SHA='01ed2b4dd7798f0ff8059548822eea1ca686b63be5bf4e8989eeb83b6d40c199'
N5_PRODUCER='acceleration/results/20261003_triangle_image_weight5_controls01/summary.json'
N5_PRODUCER_SHA='53cdcff6185d199b8f83a4989d0ea37a4b6ebbfa4fce69362e59594dcd3a6283'
N5_PROOF='acceleration/audit_20261003_triangle_image_weight5_v1_proof.md'
N5_PROOF_SHA='8844b6f2d6456ea8e8f642fcac172a93143fad7d61600f1ac24567b7b1ea76ee'
DIVISIBLE4='acceleration/audit_20261003_triangle_kernel_divisible4_v1.md'
DIVISIBLE4_SHA='0231d6873a87a7f51489e876ca4d633ae56f98c82c946b74ca856a1b4ec4924c'
DOMAINS={'even13':list(range(36,61,2)),'divisible4_seven':list(range(36,61,4))}
LOWER={3:231,4:2079,5:12474,6:24486}
LOW_STATUS='INDEPENDENT_TRIANGLE_IMAGE_LOW_WEIGHT_COUNTS_CHARACTER_V1_PASS'
CHECKER_STATUS='INDEPENDENT_TRIANGLE_KERNEL_FOUR_COUNTS_LP_CHECKER_V2_CALIBRATION_PASS'
N5_STATUS='INDEPENDENT_TRIANGLE_IMAGE_WEIGHT5_PATH_LOWER_COUNT_V1_PASS'
LIMITS=[1000,1000000,1000000000]

def need(ok,stage):
    if not ok:raise ValueError(stage)
def sha(path):
    with path.open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def save(path,obj):
    with path.open('x',encoding='utf8',newline='\n')as stream:json.dump(obj,stream,indent=2);stream.write('\n')
def frac(value):return[value.numerator,value.denominator]
def kraw(n,j,w):return sum((-1)**s*math.comb(w,s)*math.comb(n-w,j-s)for s in range(max(0,j-(n-w)),min(j,w)+1))
def matrix(n,weights,lower):
    need(type(n)is int and n>=1 and all(type(w)is int and 1<=w<=n for w in weights),'CODE_DOMAIN')
    need(all(type(j)is int and 1<=j<=n and type(value)is int and 0<=value<math.comb(n,j)for j,value in lower.items()),'LOWER_COUNT_DENOMINATOR')
    return [[Fraction(lower.get(j,0)-kraw(n,j,w),math.comb(n,j)-lower.get(j,0))for j in range(1,n+1)]for w in weights]
def exact_check(n,weights,lower,y):
    need(len(y)==n and all(type(v)is Fraction for v in y),'COMPLETE_RATIONAL_DUAL')
    need(all(v>=0 for v in y),'NONNEGATIVE_DUAL')
    coefficients=matrix(n,weights,lower);lhs=[sum(y[j]*row[j]for j in range(n))for row in coefficients]
    need(all(v>=1 for v in lhs),'ALL_EXACT_DUAL_INEQUALITIES')
    return Fraction(1)+sum(y),lhs
def power(bound):
    need(bound>=1,'CODE_SIZE_BOUND_DOMAIN');d=0
    while Fraction(1<<(d+1))<=bound:d+=1
    need(Fraction(1<<d)<=bound<Fraction(1<<(d+1)),'EXACT_POWER_OF_TWO')
    return d
def rejected(call,stage):
    try:call()
    except ValueError as error:need(type(error)is ValueError and str(error)==stage,'PRECISE_NEGATIVE_STAGE');return stage
    raise ValueError('NEGATIVE_CONTROL_ACCEPTED')
def controls(weights):
    n=9;g=[[int(v!=w and(v//3==w//3 or v%3==w%3))for w in range(n)]for v in range(n)]
    triangles=[list(t)for t in combinations(range(n),3)if all(g[v][w]for v,w in combinations(t,2))]
    need(len(triangles)==6 and all(sum(g[v][u]*g[w][u]for u in range(n))==(4 if v==w else 1 if g[v][w]else 2)for v in range(n)for w in range(n)),'LITERAL_ROOK9_SRG')
    generators=[sum(1<<v for v in t)for t in triangles];image={0}
    for t in generators:image|={x^t for x in image}
    kernel=[x for x in range(1<<n)if all((x&t).bit_count()%2==0 for t in generators)];hist=Counter(x.bit_count()for x in kernel);lower={3:6,4:9,5:9,6:6}
    need(len(kernel)==16 and len(image)==32 and hist=={0:1,4:9,6:6}and all(sum(x.bit_count()==j for x in image)==value for j,value in lower.items()),'ROOK9_ACTUAL_CODE_COUNTS')
    rows=matrix(n,[4,6],lower);y=[Fraction(math.comb(n,j)-lower.get(j,0),31)for j in range(1,n+1)];bound,lhs=exact_check(n,[4,6],lower,y);need(bound==Fraction(512,31)and lhs==[1,1]and power(bound)==4,'SHARP_SHIFTED_ROOK_DUAL')
    character=[]
    for j in range(1,n+1):
        count=sum(x.bit_count()==j for x in image);full=sum(c*kraw(n,j,w)for w,c in hist.items());nj=lower.get(j,0);shifted=sum(c*Fraction(nj-kraw(n,j,w),math.comb(n,j)-nj)for w,c in hist.items()if w)
        need(full==len(kernel)*count and shifted<=1,'ROOK_SHIFTED_CHARACTER_ROWS');character.append(dict(degree=j,lower=nj,actual=count,full_character_sum=full,shifted_nonzero_lhs=frac(shifted)))
    small=0
    for nn in range(1,7):
        for w in range(nn+1):
            x=(1<<w)-1
            for j in range(nn+1):need(kraw(nn,j,w)==sum((-1)**((x&u).bit_count())for u in range(1<<nn)if u.bit_count()==j),'LITERAL_CHARACTER_BINOMIAL');small+=1
    negative=[]
    for label,changed,stage in [('negative',[-y[0],*y[1:]],'NONNEGATIVE_DUAL'),('truncated',y[:-1],'COMPLETE_RATIONAL_DUAL'),('zero',[Fraction(0)]*n,'ALL_EXACT_DUAL_INEQUALITIES'),('insufficient',[v/2 for v in y],'ALL_EXACT_DUAL_INEQUALITIES')]:negative.append(dict(case=label,diagnostic=rejected(lambda changed=changed:exact_check(n,[4,6],lower,changed),stage)))
    negative.append(dict(case='zero_normalization_denominator',diagnostic=rejected(lambda:matrix(3,[2],{3:1}),'LOWER_COUNT_DENOMINATOR')))
    # Actual count7 instead of6 invalidates the j3 character inequality.
    negative.append(dict(case='overstated_dual_count',diagnostic=rejected(lambda:need(sum(c*kraw(n,3,w)for w,c in hist.items())>=7*len(kernel),'SHARP_CHARACTER_LOWER_COUNT'),'SHARP_CHARACTER_LOWER_COUNT')))
    negative.append(dict(case='omitted_A0_constant',diagnostic=rejected(lambda:need(sum(c*kraw(n,3,w)for w,c in hist.items()if w)>=6*len(kernel),'SHARP_CHARACTER_ZERO_CONSTANT'),'SHARP_CHARACTER_ZERO_CONSTANT')))
    mutated=[row[:]for row in rows];mutated[0][2]+=1;negative.append(dict(case='changed_coefficient',diagnostic=rejected(lambda:need(mutated==matrix(n,[4,6],lower),'COMPLETE_EXACT_COEFFICIENTS'),'COMPLETE_EXACT_COEFFICIENTS')))
    need(matrix(9,[4],lower)[0][2]==Fraction(5,39),'KNOWN_SHIFTED_COEFFICIENT')
    need([row[4] for row in rows]==[Fraction(1,39),Fraction(5,39)],'KNOWN_NEW_WEIGHT5_COEFFICIENTS')
    negative.append(dict(case='overstated_weight5_count',diagnostic=rejected(lambda:need(sum(c*kraw(n,5,w)for w,c in hist.items())>=10*len(kernel),'SHARP_CHARACTER_WEIGHT5_LOWER_COUNT'),'SHARP_CHARACTER_WEIGHT5_LOWER_COUNT')))
    changed_fifth=matrix(n,[4,6],lower);changed_fifth[0][4]*=-1
    negative.append(dict(case='changed_weight5_sign',diagnostic=rejected(lambda:need(changed_fifth==matrix(n,[4,6],lower),'EXACT_WEIGHT5_ROW_SIGN'),'EXACT_WEIGHT5_ROW_SIGN')))
    # A complete exact synthetic certificate calibrates all7-by99 raw cells.
    synthetic=[Fraction(math.comb(99,j)-LOWER.get(j,0),39271)for j in range(1,100)]
    synthetic_bound,synthetic_lhs=exact_check(99,weights,LOWER,synthetic)
    need(synthetic_bound==Fraction(2**99,39271)and synthetic_lhs==[1]*len(weights),'COMPLETE_SELECTED_DOMAIN_SYNTHETIC_DUAL')
    need(6 in hist,'ROOK9_HAS_WEIGHT6_CONTEXT_NOT_TARGET_FIXTURE')
    bad_seven=matrix(99,weights,LOWER);bad_seven[-1][-1]+=1
    negative.append(dict(case='selected_domain_changed_coefficient',diagnostic=rejected(lambda:need(bad_seven==matrix(99,weights,LOWER),'COMPLETE_SELECTED_DOMAIN_COEFFICIENTS'),'COMPLETE_SELECTED_DOMAIN_COEFFICIENTS')))
    negative.append(dict(case='selected_domain_missing_inequality',diagnostic=rejected(lambda:need(len(matrix(99,weights,LOWER)[:-1])==len(weights),'COMPLETE_SELECTED_DOMAIN_POPULATION'),'COMPLETE_SELECTED_DOMAIN_POPULATION')))
    return dict(status='AUTHOR_TRIANGLE_KERNEL_FOUR_COUNTS_LP_V2_CALIBRATION_PASS_PENDING_INDEPENDENT_REVIEW',rook_adjacency=g,rook_triangles=triangles,kernel_words=kernel,image_words=sorted(image),lower_counts={str(k):v for k,v in lower.items()},coefficient_pairs=[[frac(v)for v in row]for row in rows],positive_dual_pairs=[frac(v)for v in y],positive_lhs_pairs=[frac(v)for v in lhs],positive_exact_bound=frac(bound),maximum_linear_dimension=4,complete_literal_character_checks=small,actual_shifted_character_rows=character,synthetic_selected_domain_coefficients=[[frac(v)for v in row]for row in matrix(99,weights,LOWER)],synthetic_selected_domain_dual=[frac(v)for v in synthetic],synthetic_selected_domain_lhs=[frac(v)for v in synthetic_lhs],synthetic_selected_domain_bound=frac(synthetic_bound),target_nonzero_weights=weights,complete_target_coefficient_entries=99*len(weights),strict_negative_controls=negative,numerical_solver_invocations=0,full_target_guide_inspected=False,independent_approval=False,limitation='Author controls only; rook9 has weight6 and cannot certify target divisibility; independent written target proof and changed checker required.')
def gates(args,pins):
    for key in['low_weight_audit','low_weight_audit_sha256','weight5_audit','weight5_audit_sha256','checker_calibration','checker_calibration_sha256']:need(getattr(args,key)is not None,'GUIDE_REQUIRES_SEPARATE_GATES')
    records=[]
    for path,expected in[(args.low_weight_audit,args.low_weight_audit_sha256),(args.weight5_audit,args.weight5_audit_sha256),(args.checker_calibration,args.checker_calibration_sha256)]:
        path=path.resolve();need(path.is_relative_to(ROOT)and sha(path)==expected,'INDEPENDENT_GATE_HASH');pins[path.relative_to(ROOT).as_posix()]=expected;records.append(json.loads(path.read_bytes()))
    low,weight5,checker=records
    need(low['status']==LOW_STATUS and low['target_lower_word_counts']=={'3':231,'4':2079,'6':24486}and low['target_resolution']=='NONE'and low['universal_derivation_checked']is True,'INDEPENDENT_OLD_LOW_WEIGHT_THEOREM_GATE')
    need(weight5['status']==N5_STATUS and weight5['target_unordered_paths']==24948 and weight5['target_weight5_lower_count']==12474 and weight5['universal_derivation_checked']is True and weight5['target_resolution']=='NONE'and weight5['new_exclusions']==0 and weight5['rank_bound_claimed']is False,'INDEPENDENT_WEIGHT5_PATH_THEOREM_GATE')
    need(checker['status']==CHECKER_STATUS and checker['verifier']=='/root'and checker['full_producer_output_inspected']is False,'INDEPENDENT_CHANGED_CHECKER_PREOUTPUT_GATE')
    need(checker['approved_weight_domains']==DOMAINS and checker['inputs_sha256'].get(Path(__file__).relative_to(ROOT).as_posix())==args.source_sha256 and checker['inputs_sha256'].get(SPEC)==args.protocol_sha256,'INDEPENDENT_EXACT_PRODUCER_DOMAIN_GATE')
    return dict(low_weight_audit=args.low_weight_audit.resolve().relative_to(ROOT).as_posix(),low_weight_audit_sha256=args.low_weight_audit_sha256,weight5_audit=args.weight5_audit.resolve().relative_to(ROOT).as_posix(),weight5_audit_sha256=args.weight5_audit_sha256,checker_calibration=args.checker_calibration.resolve().relative_to(ROOT).as_posix(),checker_calibration_sha256=args.checker_calibration_sha256)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['calibrate','guide'],required=True);ap.add_argument('--weight-domain',choices=sorted(DOMAINS),required=True);ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--source-sha256',required=True);ap.add_argument('--protocol-sha256',required=True);ap.add_argument('--low-weight-audit',type=Path);ap.add_argument('--low-weight-audit-sha256');ap.add_argument('--weight5-audit',type=Path);ap.add_argument('--weight5-audit-sha256');ap.add_argument('--checker-calibration',type=Path);ap.add_argument('--checker-calibration-sha256');args=ap.parse_args();weights=DOMAINS[args.weight_domain]
    deadline=CommandDeadline(args.seconds,allocation_reason='Author tiny exactcontrols OR one explicitly selected7or13row99column conditional four-count dual guide; native<=30s and internalreserve30s; fullguide separately ROOT-authorized.');out=args.out.resolve();need(out.is_relative_to(ROOT),'WORKSPACE_OUTPUT');out.mkdir(parents=True,exist_ok=False);pins={};attempts=[];completed_native=0;started=time.monotonic()
    try:
        fixed={Path(__file__).relative_to(ROOT).as_posix():args.source_sha256,SPEC:args.protocol_sha256,BASE:BASE_SHA,WEIGHT_AUDIT:WEIGHT_AUDIT_SHA,PRESERVED13:PRESERVED13_SHA,PRESERVED7:PRESERVED7_SHA,N5_PRODUCER:N5_PRODUCER_SHA,N5_PROOF:N5_PROOF_SHA}
        if args.weight_domain=='divisible4_seven':fixed[DIVISIBLE4]=DIVISIBLE4_SHA
        for name,expected in fixed.items():pins[name]=sha(ROOT/name);need(pins[name]==expected,'EXACT_SOURCE_PROTOCOL_CONTEXT_HASH')
        for name in['pyproject.toml','uv.lock','acceleration/command_deadline.py','acceleration/run_compute_command.py','docs/COMPUTE_POLICY.md','acceleration/compute_policy.json']:pins[name]=sha(ROOT/name)
        weight_record=json.loads((ROOT/WEIGHT_AUDIT).read_bytes());need(weight_record['nonzero_kernel_weights']==list(range(36,61,2)) and weight_record['target_nonexistence']is False,'EXACT_EARLIER_WEIGHT_PREMISE')
        cal=controls(weights);cal['weight_domain']=args.weight_domain;save(out/'controls.json',cal);pins[(out/'controls.json').relative_to(ROOT).as_posix()]=sha(out/'controls.json')
        common=dict(timestamp=datetime.now(timezone.utc).isoformat(),producer='/root/structural',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_commit_limitation='New source/protocol are separately pinned working artifacts; old base source/outputs are byte-preserved.',command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),weight_domain=args.weight_domain,copied_components=['Original genericV2 and seven-weightV2 binomial/numerical wrapping/rational normalization implementation; exact sourceSHAs pinned, no approval transfer.'],target_resolution='NONE',ledger_mutations=0,graph_searches=0)
        if args.mode=='calibrate':save(out/'summary.json',dict(**common,status=cal['status'],inputs_outputs_sha256=pins,positive_controls=2,positive_control_unit='Complete exact dual fixtures: rook9 and synthetic explicitly selected n99 weight domain',strict_negative_controls=len(cal['strict_negative_controls']),numerical_solver_invocations=0,independent_approval=False,full_target_guide_launched=False,deadline=deadline.status()));print(cal['status']);return
        checked=gates(args,pins);n=99;coefficients=matrix(n,weights,LOWER);save(out/'exact_model.json',dict(schema='TRIANGLE_KERNEL_LOW_WEIGHT_EXACT_MODEL_V1',weight_domain=args.weight_domain,length=n,nonzero_weights=weights,degrees=list(range(1,n+1)),lower_word_counts={str(k):v for k,v in LOWER.items()},normalized_denominators=[math.comb(n,j)-LOWER.get(j,0)for j in range(1,n+1)],coefficient_pairs=[[frac(v)for v in row]for row in coefficients],rhs=[1]*len(weights),direction='minimize sum y_j; y>=0; G*y>=1',scope='Only conditional target triangle kernels with independently established four image counts; explicit weight domain is part of exact scope, not generic binary codes.'))
        import highspy
        import numpy as np
        from scipy.sparse import csr_matrix
        numeric_matrix=csr_matrix(np.asarray([[float(v)for v in row]for row in coefficients]));original=numeric_matrix.data.copy();numeric_matrix.data[np.abs(numeric_matrix.data)<1e-11]=0.;numeric_matrix.eliminate_zeros();save(out/'numeric_input_metadata.json',dict(absolute_truncation_threshold=1e-11,removed_small_coefficients=int(np.count_nonzero(np.abs(original)<1e-11)),scope='Only floating guide truncation; every exact coefficient is retained and checked.'))
        lp=highspy.HighsLp();lp.num_col_,lp.num_row_=n,len(weights);lp.col_cost_,lp.col_lower_,lp.col_upper_=np.ones(n),np.zeros(n),np.full(n,highspy.kHighsInf);lp.row_lower_,lp.row_upper_=np.ones(len(weights)),np.full(len(weights),highspy.kHighsInf);lp.a_matrix_.format_=highspy.MatrixFormat.kRowwise;lp.a_matrix_.start_,lp.a_matrix_.index_,lp.a_matrix_.value_=numeric_matrix.indptr,numeric_matrix.indices,numeric_matrix.data
        solver=highspy.Highs();guide_seconds=deadline.child_seconds(30,reserve_seconds=30);options=[('threads',1),('random_seed',0),('solver','simplex'),('output_flag',False),('small_matrix_value',1e-12),('time_limit',guide_seconds),('primal_feasibility_tolerance',1e-10),('dual_feasibility_tolerance',1e-10)]
        for name,value in options:need(solver.setOptionValue(name,value)==highspy.HighsStatus.kOk,'EXPLICIT_GUIDE_OPTION_'+name)
        pass_status=solver.passModel(lp);save(out/'numeric_pass_status.json',dict(status=str(pass_status),options=options));need(pass_status==highspy.HighsStatus.kOk,'NUMERICAL_GUIDE_INPUT_ACCEPTED');guide_started=time.monotonic();run_status=solver.run();completed_native=1;numeric=list(solver.getSolution().col_value);save(out/'numerical_guide.json',dict(run_status=str(run_status),model_status=str(solver.getModelStatus()),elapsed=time.monotonic()-guide_started,allocation=guide_seconds,objective=solver.getObjectiveValue(),values=numeric));candidate=None
        if len(numeric)==n and all(math.isfinite(v)for v in numeric):
            for limit in LIMITS:
                need(not deadline.status()['stop_required']and deadline.status()['remaining_seconds']>10,'NOT_COMPLETED_WITHIN_ALLOCATED_BUDGET');y=[Fraction(max(0.,v)).limit_denominator(limit)for v in numeric];lhs=[sum(y[j]*row[j]for j in range(n))for row in coefficients];minimum=min(lhs);attempts.append(dict(max_denominator=limit,exact_minimum=frac(minimum)))
                if minimum<=0:continue
                normalized=[v/minimum for v in y];bound,lhs=exact_check(n,weights,LOWER,normalized);dimension=power(bound);current=dict(schema='TRIANGLE_KERNEL_LOW_WEIGHT_COMPLETE_RATIONAL_DUAL_V1',weight_domain=args.weight_domain,length=n,nonzero_weights=weights,degrees=list(range(1,n+1)),lower_word_counts={str(k):v for k,v in LOWER.items()},dual_pairs=[frac(v)for v in normalized],lhs_pairs=[frac(v)for v in lhs],exact_size_upper=frac(bound),maximum_linear_dimension=dimension,conditional_incidence_rank_lower=n-dimension,source_rounded_denominator_limit=limit,normalization_minimum=frac(minimum),status='CANDIDATE_PENDING_INDEPENDENT_CERTIFICATE_AND_CONDITIONAL_DERIVATION_CHECK',optimum_asserted=False,target_resolution='NONE',scope='Target triangle-incidence kernels with four low-image counts and this explicit weight domain only; no generic-code bound or graph contradiction.');save(out/('certificate_limit_'+str(limit)+'.json'),current);attempts[-1].update(exact_bound=frac(bound),certificate_path='certificate_limit_'+str(limit)+'.json')
                if candidate is None or bound<Fraction(*candidate['exact_size_upper']):candidate=current
        if candidate is not None:save(out/'certificate.json',candidate)
        for path in sorted(out.iterdir()):
            if path.is_file():pins[path.relative_to(ROOT).as_posix()]=sha(path)
        save(out/'summary.json',dict(**common,status='CANDIDATE_EXACT_CONDITIONAL_DUAL'if candidate else'UNKNOWN_NO_EXACT_DUAL',inputs_outputs_sha256=pins,selected_code_domain=dict(weight_domain=args.weight_domain,length=99,nonzero_weights=weights,lower_word_counts={str(k):v for k,v in LOWER.items()},unrestricted_target_conditional=True),independent_gates=checked,attempted_guides=1,completed_guides=completed_native,exact_candidate_certificates=sum('certificate_path'in row for row in attempts),candidate=candidate,lift_attempts=attempts,selection_rule='Lowest exact upper bound among the complete frozen denominator-limit sequence1000/1000000/1000000000; no extra optimizer call and no optimum claim.',elapsed_seconds=time.monotonic()-started,highspy=solver.version(),numpy=np.__version__,deadline=deadline.status(),limitations=['Complete exact dual requires a separate checker after output.','Graph-specific image counts/weight domain are premises; this is not a generic-code bound.','No optimum, rank upper bound, minimum kernel dimension, construction or target exclusion.','No novelty, external review or target-wide search coverage.']));print(json.dumps(dict(status='CANDIDATE_EXACT_CONDITIONAL_DUAL'if candidate else'UNKNOWN_NO_EXACT_DUAL',dimension=None if candidate is None else candidate['maximum_linear_dimension'],rank_lower=None if candidate is None else candidate['conditional_incidence_rank_lower'],target_resolution='NONE')))
    except Exception as error:
        save(out/'failure.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),exception=type(error).__name__,diagnostic=str(error),inputs_outputs_sha256=pins,completed_guides=completed_native,lift_attempts=attempts,deadline=deadline.status(),target_resolution='NONE',restart='Preserve source/output/receipt; explicit new supported invocation required, changed source needs new version and gates.'));raise
if __name__=='__main__':main()
