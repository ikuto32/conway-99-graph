"""Implementation V3, logical two-domain gate V2; preserves unexecuted V1/V2 and executed old seven-weight V2."""
import argparse
import copy
from datetime import datetime,timezone
from fractions import Fraction
from functools import lru_cache
import hashlib
import json
import platform
from pathlib import Path
import sys
import subprocess
from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
DOMAINS={'even13':list(range(36,61,2)),'divisible4_seven':list(range(36,61,4))}
WEIGHTS=DOMAINS['even13']
LOW={3:231,4:2079,5:12474,6:24486}
def need(ok,stage):
 if not ok:raise ValueError(stage)
def sha(path):
 with path.open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def save(path,obj):
 with path.open('x',encoding='utf8',newline='\n')as stream:json.dump(obj,stream,indent=2);stream.write('\n')
def pair(q):return[q.numerator,q.denominator]
def rational(v):
 need(type(v)is list and len(v)==2 and all(type(q)is int for q in v)and v[1]>0,'RATIONAL_SYNTAX')
 return Fraction(*v)
@lru_cache(maxsize=None)
def polynomial(n,w):
 need(type(n)is int and type(w)is int and 0<=w<=n,'POLYNOMIAL_DOMAIN')
 # Literal product (1-z)^w(1+z)^(n-w), not discovery's binomial sum.
 values=[1]
 for sign in [-1]*w+[1]*(n-w):
  new=[0]*(len(values)+1)
  for j,q in enumerate(values):new[j]+=q;new[j+1]+=sign*q
  values=new
 return tuple(values)
def model(n,weights,lower):
 zero=polynomial(n,0)
 need(all(type(j)is int and 1<=j<=n and type(q)is int and 0<=q<zero[j]for j,q in lower.items()),'LOW_COUNTS_DOMAIN')
 need(len(weights)==len(set(weights))and all(type(w)is int and 1<=w<=n for w in weights),'NONZERO_WEIGHT_DOMAIN')
 return[[Fraction(lower.get(j,0)-polynomial(n,w)[j],zero[j]-lower.get(j,0))for j in range(1,n+1)]for w in weights]
def dual(n,weights,lower,y):
 need(type(y)is list and len(y)==n,'DUAL_LENGTH');need(all(type(q)is Fraction and q>=0 for q in y),'DUAL_NONNEGATIVE')
 g=model(n,weights,lower);lhs=[sum(q*t for q,t in zip(row,y))for row in g]
 need(all(q>=1 for q in lhs),'DUAL_INEQUALITY')
 bound=1+sum(y);dimension=0
 while Fraction(1<<(dimension+1))<=bound:dimension+=1
 return bound,lhs,dimension
def reject(label,stage,fn,records):
 try:fn()
 except ValueError as exc:need(str(exc)==stage,'WRONG_CONTROL_DIAGNOSTIC');records.append(dict(case=label,diagnostic=stage));return
 raise ValueError('CORRUPTION_ACCEPTED '+label)
def calibration():
 literal_checks=0
 for n in range(7):
  for w in range(n+1):
   p=polynomial(n,w);x=(1<<w)-1
   for j in range(n+1):
    literal=sum((-1 if (x&u).bit_count()%2 else 1)for u in range(1<<n)if u.bit_count()==j)
    need(p[j]==literal,'LITERAL_CHARACTER_COEFFICIENT');literal_checks+=1
 # Known rook incidence kernel/image via complete literal triangle set.
 adj=[[int(i!=j and(i//3==j//3 or i%3==j%3))for j in range(9)]for i in range(9)]
 triples=[(i,j,k)for i in range(9)for j in range(i+1,9)for k in range(j+1,9)if adj[i][j]and adj[i][k]and adj[j][k]]
 kernel=[x for x in range(512)if all(sum(x>>v&1 for v in t)%2==0 for t in triples)]
 image={0}
 for t in triples:image|={x^sum(1<<v for v in t)for x in image}
 lower={3:6,4:9,5:9,6:6};need(len(kernel)==16 and len(image)==32,'KNOWN_COMPLETE_ROOK_CODES')
 histogram={w:sum(x.bit_count()==w for x in kernel)for w in range(10)}
 need(histogram=={0:1,1:0,2:0,3:0,4:9,5:0,6:6,7:0,8:0,9:0},'KNOWN_ROOK_WEIGHT_DOMAIN')
 zero=polynomial(9,0);g=model(9,[4,6],lower)
 for j in range(1,10):
  exact=sum(histogram[w]*polynomial(9,w)[j]for w in range(10))
  actual=sum(x.bit_count()==j for x in image)
  need(exact==len(kernel)*actual and actual>=lower.get(j,0),'COMPLETE_CHARACTER_AND_LOW_COUNTS')
  need(sum(histogram[w]*g[k][j-1]for k,w in enumerate([4,6]))<=1,'SHIFTED_CONSTANT_ROW')
 y=[Fraction(zero[j]-lower.get(j,0),31)for j in range(1,10)]
 bound,lhs,dimension=dual(9,[4,6],lower,y)
 need(bound==Fraction(512,31)and lhs==[1,1]and dimension==4,'KNOWN_SHIFTED_ROOK_DUAL')
 need(sum(x.bit_count()==5 for x in image)==9,'KNOWN_ROOK_WEIGHT5_IMAGE_COUNT')
 need([row[4] for row in g]==[Fraction(1,39),Fraction(5,39)],'KNOWN_WEIGHT5_SHIFTED_COEFFICIENTS')
 full=[Fraction(q)for q in polynomial(4,0)[1:]]
 need(dual(4,[1,2,3,4],{},full)[0]==16,'KNOWN_FULL_BINARY_CODE_DUAL')
 negatives=[]
 for label,stage,fn in[
  ('truncated','DUAL_LENGTH',lambda:dual(9,[4,6],lower,y[:-1])),
  ('negative','DUAL_NONNEGATIVE',lambda:dual(9,[4,6],lower,[-y[0],*y[1:]])),
  ('float','DUAL_NONNEGATIVE',lambda:dual(9,[4,6],lower,[float(y[0]),*y[1:]])),
  ('zero','DUAL_INEQUALITY',lambda:dual(9,[4,6],lower,[Fraction(0)]*9)),
  ('half','DUAL_INEQUALITY',lambda:dual(9,[4,6],lower,[q/2 for q in y])),
  ('count_equals_binomial','LOW_COUNTS_DOMAIN',lambda:model(9,[4,6],{3:84})),
  ('bool_count','LOW_COUNTS_DOMAIN',lambda:model(9,[4,6],{3:True})),
  ('bad_fraction','RATIONAL_SYNTAX',lambda:rational([1,0]))]:reject(label,stage,fn,negatives)
 reject('overstated_weight5_image','KNOWN_ROOK_WEIGHT5_IMAGE_COUNT',lambda:need(sum(x.bit_count()==5 for x in image)>=10,'KNOWN_ROOK_WEIGHT5_IMAGE_COUNT'),negatives)
 reject('omitted_weight5_zero_constant','SHARP_WEIGHT5_ZERO_CONSTANT',lambda:need(sum(histogram[w]*polynomial(9,w)[5]for w in range(1,10))>=len(kernel)*9,'SHARP_WEIGHT5_ZERO_CONSTANT'),negatives)
 return dict(status='INDEPENDENT_TRIANGLE_KERNEL_FOUR_COUNTS_LP_CHECKER_V2_CALIBRATION_PASS',
             complete_small_literal_coefficients=literal_checks,complete_rook_kernel=kernel,complete_rook_image=sorted(image),
             exact_rook_bound=pair(bound),exact_rook_lhs=[pair(q)for q in lhs],strict_corruptions=negatives,
             producer_output_inspected=False,full_producer_output_inspected=False,target_resolution='NONE')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['calibrate','check']);p.add_argument('--seconds',type=float,required=True);p.add_argument('--out',type=Path,required=True)
 p.add_argument('--producer',type=Path,required=True);p.add_argument('--producer-sha256',required=True)
 p.add_argument('--producer-protocol',type=Path,required=True);p.add_argument('--producer-protocol-sha256',required=True)
 p.add_argument('--summary',type=Path);p.add_argument('--summary-sha256');p.add_argument('--calibration',type=Path);p.add_argument('--calibration-sha256')
 p.add_argument('--low-weight-audit',type=Path,required=True);p.add_argument('--low-weight-audit-sha256',required=True)
 p.add_argument('--weight5-audit',type=Path,required=True);p.add_argument('--weight5-audit-sha256',required=True)
 p.add_argument('--weight-domain',choices=sorted(DOMAINS));a=p.parse_args()
 global WEIGHTS
 if a.mode=='check':need(a.weight_domain in DOMAINS,'EXPLICIT_WEIGHT_DOMAIN');WEIGHTS=DOMAINS[a.weight_domain]
 d=CommandDeadline(a.seconds,allocation_reason='Independent exact polynomial coefficients and rational dual, tiny shifted-code controls; no optimizer/scientific graph search')
 out=a.out.resolve();need(out.is_relative_to(ROOT),'WORKSPACE_OUTPUT');out.mkdir(parents=True,exist_ok=False)
 try:
  need(sha(a.producer)==a.producer_sha256 and sha(a.low_weight_audit)==a.low_weight_audit_sha256,'PINNED_PRODUCER_AND_PROOF_GATE')
  proof=json.loads(a.low_weight_audit.read_bytes());need(proof['status']=='INDEPENDENT_TRIANGLE_IMAGE_LOW_WEIGHT_COUNTS_CHARACTER_V1_PASS'
       and proof['target_lower_word_counts']=={str(k):v for k,v in LOW.items() if k!=5}
       and proof['universal_derivation_checked']is True and proof['target_resolution']=='NONE','UNIVERSAL_LOW_COUNT_AUDIT_STATUS')
  need(sha(a.weight5_audit)==a.weight5_audit_sha256,'PINNED_WEIGHT5_AUDIT')
  fifth=json.loads(a.weight5_audit.read_bytes())
  need(fifth['status']=='INDEPENDENT_TRIANGLE_IMAGE_WEIGHT5_PATH_LOWER_COUNT_V1_PASS'
       and fifth['universal_derivation_checked']is True and fifth['target_unordered_paths']==24948
       and fifth['target_weight5_lower_count']==12474 and fifth['target_resolution']=='NONE'
       and fifth['rank_bound_claimed']is False and fifth['new_exclusions']==0,'UNIVERSAL_WEIGHT5_AUDIT_STATUS')
  kernel_proof=ROOT/'acceleration/audit_20261003_triangle_kernel_divisible4_v1.md'
  need(sha(kernel_proof)=='0231d6873a87a7f51489e876ca4d633ae56f98c82c946b74ca856a1b4ec4924c','EXACT_DIVISIBLE4_WRITTEN_PROOF')
  need(sha(a.producer_protocol)==a.producer_protocol_sha256,'EXACT_FROZEN_PRODUCER_PROTOCOL')
  interval=ROOT/'acceleration/audit_20261003_incidence_griesmer_v1.md'
  need(sha(interval)=='65d8eea3f4d72eb56391284f95eb43ad021e92a88a41fdcc2fe7a2e10f9dd92d','EXACT_PREVIOUS_NONZERO_WEIGHT_INTERVAL')
  pins={q.resolve().relative_to(ROOT).as_posix():sha(q)for q in[Path(__file__),Path(__file__).with_name(Path(__file__).stem+'_spec.md'),Path(__file__).with_suffix('.md'),a.producer,a.producer_protocol,kernel_proof,interval,a.low_weight_audit,a.weight5_audit,ROOT/'pyproject.toml',ROOT/'uv.lock',ROOT/'acceleration/command_deadline.py',ROOT/'acceleration/run_compute_command.py']}
  for premise in [proof,fifth]:
   for name,expected_hash in premise['inputs_sha256'].items():need(sha(ROOT/name)==expected_hash,'EXACT_UNIVERSAL_AUDIT_COMPONENT');pins[name]=expected_hash
  protected={name:sha(ROOT/name)for name in['CLAIMS.yaml','.git/index']}
  if a.mode=='calibrate':
   result=calibration()
   domains=[]
   for label,weights in DOMAINS.items():
    WEIGHTS=weights
    zeros=polynomial(99,0);den=sum(LOW.values())+1
    synthetic_y=[Fraction(zeros[j]-LOW.get(j,0),den)for j in range(1,100)]
    bound,lhs,dim=dual(99,WEIGHTS,LOW,synthetic_y)
    need(bound==Fraction(1<<99,den)and lhs==[1]*len(WEIGHTS),'SYNTHETIC_FULL_SCHEMA_KNOWN_ALGEBRA')
    exact=dict(schema='TRIANGLE_KERNEL_LOW_WEIGHT_EXACT_MODEL_V1',weight_domain=label,length=99,nonzero_weights=WEIGHTS,degrees=list(range(1,100)),lower_word_counts={str(k):v for k,v in LOW.items()},normalized_denominators=[zeros[j]-LOW.get(j,0)for j in range(1,100)],coefficient_pairs=[[pair(q)for q in row]for row in model(99,WEIGHTS,LOW)],rhs=[1]*len(WEIGHTS))
    raw=dict(schema='TRIANGLE_KERNEL_LOW_WEIGHT_COMPLETE_RATIONAL_DUAL_V1',weight_domain=label,length=99,nonzero_weights=WEIGHTS,degrees=list(range(1,100)),lower_word_counts={str(k):v for k,v in LOW.items()},dual_pairs=[pair(q)for q in synthetic_y],lhs_pairs=[pair(q)for q in lhs],exact_size_upper=pair(bound),maximum_linear_dimension=dim,conditional_incidence_rank_lower=99-dim,optimum_asserted=False,target_resolution='NONE')
    sub=out/label;sub.mkdir();save(sub/'synthetic_exact_model.json',exact);save(sub/'synthetic_certificate.json',raw)
    check_raw(exact,raw,dict(candidate=raw),sub,pins)
    domains.append(dict(weight_domain=label,synthetic_complete_coefficients=99*len(WEIGHTS),synthetic_known_bound=pair(bound),synthetic_precise_corruptions=10))
   result.update(synthetic_schema_controls_only=True,approved_weight_domains=DOMAINS,domain_controls=domains,full_producer_output_inspected=False)
  else:
   need(a.summary and a.calibration and sha(a.summary)==a.summary_sha256 and sha(a.calibration)==a.calibration_sha256,'EXACT_RAW_AND_CALIBRATION')
   cal=json.loads(a.calibration.read_bytes());need(cal['status']=='INDEPENDENT_TRIANGLE_KERNEL_FOUR_COUNTS_LP_CHECKER_V2_CALIBRATION_PASS','EXACT_CALIBRATION_STATUS')
   for name,expected_hash in cal['inputs_sha256'].items():need(sha(ROOT/name)==expected_hash,'UNCHANGED_APPLICABLE_GATE_COMPONENT');pins[name]=expected_hash
   producer=json.loads(a.summary.read_bytes());need(producer['status']=='CANDIDATE_EXACT_CONDITIONAL_DUAL','RAW_EXACT_CERTIFICATE_REQUIRED')
   identity(producer['selected_code_domain'],dict(weight_domain=a.weight_domain,length=99,nonzero_weights=WEIGHTS,lower_word_counts={str(k):v for k,v in LOW.items()},unrestricted_target_conditional=True),'RAW_SELECTED_DOMAIN')
   for name,expected_hash in producer['inputs_outputs_sha256'].items():need(sha(ROOT/name)==expected_hash,'EXACT_PRODUCER_ARTIFACT');pins[name]=expected_hash
   raw=json.loads((a.summary.parent/'certificate.json').read_bytes());exact=json.loads((a.summary.parent/'exact_model.json').read_bytes())
   # Protocol field names are frozen with the new producer before first gate.
   check_raw(exact,raw,producer,out,pins)
   result=json.loads((out/'checked_values.json').read_bytes())
   pins[a.summary.resolve().relative_to(ROOT).as_posix()]=a.summary_sha256;pins[a.calibration.resolve().relative_to(ROOT).as_posix()]=a.calibration_sha256
  need(all(sha(ROOT/name)==h for name,h in protected.items()),'PROTECTED_STATE_UNCHANGED')
  need(not d.status()['stop_required'],'NOT_COMPLETED_WITHIN_ALLOCATED_BUDGET')
  result.update(checker_implementation_version=3,gate_interface_version=2,timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),python=platform.python_version(),producer='/root/structural',verifier='/root',method='independent_artifact_check',command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256=pins,historical_protected_execution_state=protected,
                shared_components=['Polynomial/rational algorithms adapted from independently checked ROOT seven-weight V2; changed fourth image count and explicit two-domain scope require fresh controls. Python integers/Fraction/deadline/runtime.', 'Polynomial product convolution plus full literal characters differs from discovery binomial sums; no producer/optimizer imports.'],
                limitations=['Conditional code-size bound only; no optimizer optimum, rank upper bound, target graph/nonexistence or external review.', 'Requires independent universal3/4/6 and5 image-count audits and separately proved nonzero kernel weights36..60 even; divisible4 premise applies only to the named seven-weight domain. Tiny fixtures alone do not prove necessity.'],deadline=d.status())
  save(out/'summary.json',result)
 except BaseException as error:save(out/'failure.json',dict(error=repr(error),timestamp=datetime.now(timezone.utc).isoformat(),saved_outputs_preserved=True));raise

def identity(actual,expected,stage):
 need(json.dumps(actual,sort_keys=True,separators=(',',':'))==json.dumps(expected,sort_keys=True,separators=(',',':')),stage)
def check_model(exact):
 need(exact['schema']=='TRIANGLE_KERNEL_LOW_WEIGHT_EXACT_MODEL_V1','MODEL_SCHEMA')
 identity([exact[k]for k in ('length','nonzero_weights','degrees','lower_word_counts','rhs')],
          [99,WEIGHTS,list(range(1,100)),{str(k):v for k,v in LOW.items()},[1]*len(WEIGHTS)],'MODEL_SCOPE')
 identity(exact['weight_domain'],next(k for k,v in DOMAINS.items() if v==WEIGHTS),'MODEL_DOMAIN')
 zeros=polynomial(99,0);identity(exact['normalized_denominators'],[zeros[j]-LOW.get(j,0)for j in range(1,100)],'MODEL_DENOMINATORS')
 need(type(exact['coefficient_pairs'])is list and len(exact['coefficient_pairs'])==len(WEIGHTS)
      and all(type(row)is list and len(row)==99 for row in exact['coefficient_pairs']),'MODEL_COMPLETE_SHAPE')
 actual=[[rational(v)for v in row]for row in exact['coefficient_pairs']]
 need(actual==model(99,WEIGHTS,LOW),'MODEL_EXACT_COEFFICIENTS')
def check_certificate(raw):
 need(raw['schema']=='TRIANGLE_KERNEL_LOW_WEIGHT_COMPLETE_RATIONAL_DUAL_V1','CERTIFICATE_SCHEMA')
 identity([raw[k]for k in ('length','nonzero_weights','degrees','lower_word_counts')],
          [99,WEIGHTS,list(range(1,100)),{str(k):v for k,v in LOW.items()}],'CERTIFICATE_SCOPE')
 identity(raw['weight_domain'],next(k for k,v in DOMAINS.items() if v==WEIGHTS),'CERTIFICATE_DOMAIN')
 need(type(raw['dual_pairs'])is list,'DUAL_LENGTH')
 y=[rational(v)for v in raw['dual_pairs']];bound,lhs,dim=dual(99,WEIGHTS,LOW,y)
 need([rational(v)for v in raw['lhs_pairs']]==lhs,'CERTIFICATE_ADVERTISED_LHS')
 need(rational(raw['exact_size_upper'])==bound,'CERTIFICATE_ADVERTISED_BOUND')
 identity([raw['maximum_linear_dimension'],raw['conditional_incidence_rank_lower']],[dim,99-dim],'CERTIFICATE_INTEGER_DIMENSION')
 need(raw['optimum_asserted']is False and raw['target_resolution']=='NONE','CERTIFICATE_SCOPE_LIMIT')
 return bound,lhs,dim
def check_raw(exact,raw,producer,out,pins):
 check_model(exact);bound,lhs,dim=check_certificate(raw)
 identity(producer['candidate'],raw,'EXACT_RAW_SUMMARY_BINDING')
 negatives=[]
 damaged=copy.deepcopy(raw);damaged['dual_pairs']=damaged['dual_pairs'][:-1]
 reject('actual_truncated','DUAL_LENGTH',lambda:check_certificate(damaged),negatives)
 damaged=copy.deepcopy(raw);damaged['dual_pairs'][0]=[-1,1]
 reject('actual_negative','DUAL_NONNEGATIVE',lambda:check_certificate(damaged),negatives)
 damaged=copy.deepcopy(raw);damaged['dual_pairs']=[[0,1]]*99
 reject('actual_zero','DUAL_INEQUALITY',lambda:check_certificate(damaged),negatives)
 damaged=copy.deepcopy(raw);damaged['exact_size_upper']=[bound.numerator+1,bound.denominator]
 reject('actual_changed_bound','CERTIFICATE_ADVERTISED_BOUND',lambda:check_certificate(damaged),negatives)
 damaged=copy.deepcopy(raw);damaged['conditional_incidence_rank_lower']+=1
 reject('actual_changed_rank','CERTIFICATE_INTEGER_DIMENSION',lambda:check_certificate(damaged),negatives)
 damaged=copy.deepcopy(exact);damaged['lower_word_counts']['3']+=1
 reject('actual_changed_low_count','MODEL_SCOPE',lambda:check_model(damaged),negatives)
 damaged=copy.deepcopy(exact);damaged['coefficient_pairs'][0][2]=pair(rational(damaged['coefficient_pairs'][0][2])+1)
 reject('actual_changed_coefficient','MODEL_EXACT_COEFFICIENTS',lambda:check_model(damaged),negatives)
 damaged=copy.deepcopy(exact);damaged['lower_word_counts']['5']+=1
 reject('actual_changed_weight5_count','MODEL_SCOPE',lambda:check_model(damaged),negatives)
 damaged=copy.deepcopy(exact);damaged['coefficient_pairs'][0][4]=pair(rational(damaged['coefficient_pairs'][0][4])+1)
 reject('actual_changed_weight5_coefficient','MODEL_EXACT_COEFFICIENTS',lambda:check_model(damaged),negatives)
 damaged=copy.deepcopy(raw);damaged['weight_domain']='divisible4_seven' if WEIGHTS==DOMAINS['even13'] else 'even13'
 reject('actual_changed_weight_domain','CERTIFICATE_DOMAIN',lambda:check_certificate(damaged),negatives)
 save(out/'corruptions.json',negatives);pins[(out/'corruptions.json').relative_to(ROOT).as_posix()]=sha(out/'corruptions.json')
 save(out/'checked_values.json',dict(status='INDEPENDENT_TRIANGLE_KERNEL_FOUR_COUNTS_COMPLETE_DUAL_V2_PASS',
      weight_domain=next(k for k,v in DOMAINS.items() if v==WEIGHTS),complete_exact_coefficients_checked=99*len(WEIGHTS),complete_nonnegative_dual_coordinates_checked=99,
      complete_exact_weight_inequalities_checked=len(WEIGHTS),exact_size_upper=pair(bound),maximum_linear_dimension=dim,
      conditional_incidence_rank_lower=99-dim,exact_lhs_pairs=[pair(v)for v in lhs],actual_strict_corruption_controls=10,
      lower_word_counts={str(k):v for k,v in LOW.items()},target_resolution='NONE',optimum_asserted=False))

if __name__=='__main__':main()


