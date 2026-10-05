"""Independent polynomial-convolution rational dual check; never imports producer."""
import argparse
import copy
from datetime import datetime,timezone
from fractions import Fraction
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import sys
from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
WEIGHTS=list(range(36,61,2))
LOW={3:231,4:2079,6:24486}
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
 lower={3:6,4:9,6:6};need(len(kernel)==16 and len(image)==32,'KNOWN_COMPLETE_ROOK_CODES')
 histogram={w:sum(x.bit_count()==w for x in kernel)for w in range(10)}
 need(histogram=={0:1,1:0,2:0,3:0,4:9,5:0,6:6,7:0,8:0,9:0},'KNOWN_ROOK_WEIGHT_DOMAIN')
 zero=polynomial(9,0);g=model(9,[4,6],lower)
 for j in range(1,10):
  exact=sum(histogram[w]*polynomial(9,w)[j]for w in range(10))
  actual=sum(x.bit_count()==j for x in image)
  need(exact==len(kernel)*actual and actual>=lower.get(j,0),'COMPLETE_CHARACTER_AND_LOW_COUNTS')
  need(sum(histogram[w]*g[k][j-1]for k,w in enumerate([4,6]))<=1,'SHIFTED_CONSTANT_ROW')
 y=[Fraction(zero[j]-lower.get(j,0),22)for j in range(1,10)]
 bound,lhs,dimension=dual(9,[4,6],lower,y)
 need(bound==Fraction(256,11)and lhs==[1,1]and dimension==4,'KNOWN_SHIFTED_ROOK_DUAL')
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
 return dict(status='INDEPENDENT_TRIANGLE_KERNEL_LOW_WEIGHT_LP_CHECKER_V1_CALIBRATION_PASS',
             complete_small_literal_coefficients=literal_checks,complete_rook_kernel=kernel,complete_rook_image=sorted(image),
             exact_rook_bound=pair(bound),exact_rook_lhs=[pair(q)for q in lhs],strict_corruptions=negatives,
             producer_output_inspected=False,full_producer_output_inspected=False,target_resolution='NONE')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['calibrate','check']);p.add_argument('--seconds',type=float,required=True);p.add_argument('--out',type=Path,required=True)
 p.add_argument('--producer',type=Path,required=True);p.add_argument('--producer-sha256',required=True)
 p.add_argument('--summary',type=Path);p.add_argument('--summary-sha256');p.add_argument('--calibration',type=Path);p.add_argument('--calibration-sha256')
 p.add_argument('--low-weight-audit',type=Path,required=True);p.add_argument('--low-weight-audit-sha256',required=True);a=p.parse_args()
 d=CommandDeadline(a.seconds,allocation_reason='Independent exact polynomial coefficients and rational dual, tiny shifted-code controls; no optimizer/scientific graph search')
 out=a.out.resolve();need(out.is_relative_to(ROOT),'WORKSPACE_OUTPUT');out.mkdir(parents=True,exist_ok=False)
 try:
  need(sha(a.producer)==a.producer_sha256 and sha(a.low_weight_audit)==a.low_weight_audit_sha256,'PINNED_PRODUCER_AND_PROOF_GATE')
  proof=json.loads(a.low_weight_audit.read_bytes());need(proof['status']=='INDEPENDENT_TRIANGLE_IMAGE_LOW_WEIGHT_COUNTS_CHARACTER_V1_PASS'
       and proof['target_lower_word_counts']=={str(k):v for k,v in LOW.items()}
       and proof['universal_derivation_checked']is True and proof['target_resolution']=='NONE','UNIVERSAL_LOW_COUNT_AUDIT_STATUS')
  pins={q.resolve().relative_to(ROOT).as_posix():sha(q)for q in[Path(__file__),Path(__file__).with_name(Path(__file__).stem+'_spec.md'),Path(__file__).with_suffix('.md'),a.producer,a.low_weight_audit,ROOT/'pyproject.toml',ROOT/'uv.lock',ROOT/'acceleration/command_deadline.py']}
  for name,identity in proof['inputs_sha256'].items():need(sha(ROOT/name)==identity,'EXACT_UNIVERSAL_AUDIT_COMPONENT');pins[name]=identity
  if a.mode=='calibrate':
   result=calibration()
   zeros=polynomial(99,0);den=sum(LOW.values())+1
   synthetic_y=[Fraction(zeros[j]-LOW.get(j,0),den)for j in range(1,100)]
   bound,lhs,dim=dual(99,WEIGHTS,LOW,synthetic_y)
   need(bound==Fraction(1<<99,den)and lhs==[1]*13,'SYNTHETIC_FULL_SCHEMA_KNOWN_ALGEBRA')
   exact=dict(schema='TRIANGLE_KERNEL_LOW_WEIGHT_EXACT_MODEL_V1',length=99,nonzero_weights=WEIGHTS,degrees=list(range(1,100)),lower_word_counts={str(k):v for k,v in LOW.items()},normalized_denominators=[zeros[j]-LOW.get(j,0)for j in range(1,100)],coefficient_pairs=[[pair(q)for q in row]for row in model(99,WEIGHTS,LOW)],rhs=[1]*13)
   raw=dict(schema='TRIANGLE_KERNEL_LOW_WEIGHT_COMPLETE_RATIONAL_DUAL_V1',length=99,nonzero_weights=WEIGHTS,degrees=list(range(1,100)),lower_word_counts={str(k):v for k,v in LOW.items()},dual_pairs=[pair(q)for q in synthetic_y],lhs_pairs=[pair(q)for q in lhs],exact_size_upper=pair(bound),maximum_linear_dimension=dim,conditional_incidence_rank_lower=99-dim,optimum_asserted=False,target_resolution='NONE')
   save(out/'synthetic_exact_model.json',exact);save(out/'synthetic_certificate.json',raw)
   check_raw(exact,raw,dict(candidate=raw),out,pins)
   result.update(synthetic_schema_controls_only=True,synthetic_complete_coefficients=1287,synthetic_known_bound=pair(bound),synthetic_precise_corruptions=7)
  else:
   need(a.summary and a.calibration and sha(a.summary)==a.summary_sha256 and sha(a.calibration)==a.calibration_sha256,'EXACT_RAW_AND_CALIBRATION')
   cal=json.loads(a.calibration.read_bytes());need(cal['status']=='INDEPENDENT_TRIANGLE_KERNEL_LOW_WEIGHT_LP_CHECKER_V1_CALIBRATION_PASS','EXACT_CALIBRATION_STATUS')
   for name,identity in cal['inputs_sha256'].items():need(sha(ROOT/name)==identity,'UNCHANGED_APPLICABLE_GATE_COMPONENT');pins[name]=identity
   producer=json.loads(a.summary.read_bytes());need(producer['status']=='CANDIDATE_EXACT_CONDITIONAL_DUAL','RAW_EXACT_CERTIFICATE_REQUIRED')
   for name,identity in producer['inputs_outputs_sha256'].items():need(sha(ROOT/name)==identity,'EXACT_PRODUCER_ARTIFACT');pins[name]=identity
   raw=json.loads((a.summary.parent/'certificate.json').read_bytes());exact=json.loads((a.summary.parent/'exact_model.json').read_bytes())
   # Protocol field names are frozen with the new producer before first gate.
   check_raw(exact,raw,producer,out,pins)
   result=json.loads((out/'checked_values.json').read_bytes())
   pins[a.summary.resolve().relative_to(ROOT).as_posix()]=a.summary_sha256;pins[a.calibration.resolve().relative_to(ROOT).as_posix()]=a.calibration_sha256
  result.update(timestamp=datetime.now(timezone.utc).isoformat(),producer='/root/structural',verifier='/root',method='independent_artifact_check',command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256=pins,
                shared_components=['Same exact stated necessary binary-kernel domain; Python integers/Fraction/deadline/runtime.', 'Polynomial product convolution plus full literal characters differs from discovery binomial sums; no producer/optimizer imports.'],
                limitations=['Conditional code-size bound only; no optimizer optimum, rank upper bound, target graph/nonexistence or external review.', 'Requires independent universal low-weight audit and separately derived kernel weights36..60; finite fixture controls alone do not prove necessity.'],deadline=d.status())
  save(out/'summary.json',result)
 except BaseException as error:save(out/'failure.json',dict(error=repr(error),timestamp=datetime.now(timezone.utc).isoformat(),saved_outputs_preserved=True));raise

def identity(actual,expected,stage):
 need(json.dumps(actual,sort_keys=True,separators=(',',':'))==json.dumps(expected,sort_keys=True,separators=(',',':')),stage)
def check_model(exact):
 need(exact['schema']=='TRIANGLE_KERNEL_LOW_WEIGHT_EXACT_MODEL_V1','MODEL_SCHEMA')
 identity([exact[k]for k in ('length','nonzero_weights','degrees','lower_word_counts','rhs')],
          [99,WEIGHTS,list(range(1,100)),{str(k):v for k,v in LOW.items()},[1]*13],'MODEL_SCOPE')
 zeros=polynomial(99,0);identity(exact['normalized_denominators'],[zeros[j]-LOW.get(j,0)for j in range(1,100)],'MODEL_DENOMINATORS')
 need(type(exact['coefficient_pairs'])is list and len(exact['coefficient_pairs'])==13
      and all(type(row)is list and len(row)==99 for row in exact['coefficient_pairs']),'MODEL_COMPLETE_SHAPE')
 actual=[[rational(v)for v in row]for row in exact['coefficient_pairs']]
 need(actual==model(99,WEIGHTS,LOW),'MODEL_EXACT_COEFFICIENTS')
def check_certificate(raw):
 need(raw['schema']=='TRIANGLE_KERNEL_LOW_WEIGHT_COMPLETE_RATIONAL_DUAL_V1','CERTIFICATE_SCHEMA')
 identity([raw[k]for k in ('length','nonzero_weights','degrees','lower_word_counts')],
          [99,WEIGHTS,list(range(1,100)),{str(k):v for k,v in LOW.items()}],'CERTIFICATE_SCOPE')
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
 save(out/'corruptions.json',negatives);pins[(out/'corruptions.json').relative_to(ROOT).as_posix()]=sha(out/'corruptions.json')
 save(out/'checked_values.json',dict(status='INDEPENDENT_TRIANGLE_KERNEL_LOW_WEIGHT_COMPLETE_DUAL_V1_PASS',
      complete_exact_coefficients_checked=1287,complete_nonnegative_dual_coordinates_checked=99,
      complete_exact_weight_inequalities_checked=13,exact_size_upper=pair(bound),maximum_linear_dimension=dim,
      conditional_incidence_rank_lower=99-dim,exact_lhs_pairs=[pair(v)for v in lhs],actual_strict_corruption_controls=7,
      lower_word_counts={str(k):v for k,v in LOW.items()},target_resolution='NONE',optimum_asserted=False))

if __name__=='__main__':main()
