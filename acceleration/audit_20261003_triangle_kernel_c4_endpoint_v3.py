"""Fresh independent exact C4-count endpoint checker; no discovery imports."""
import argparse
import copy
from datetime import datetime, timezone
from fractions import Fraction
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import platform
import sys
from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
SOURCE='acceleration/audit_20261003_triangle_kernel_c4_endpoint_v3.py'
SPEC='acceleration/audit_20261003_triangle_kernel_c4_endpoint_v3_spec.md'
PROOF='acceleration/audit_20261003_triangle_kernel_c4_endpoint_v1.md'
PRODUCER='acceleration/theory_20261003_triangle_kernel_c4_endpoint_v3.py'
PRODUCER_SPEC='acceleration/theory_20261003_triangle_kernel_c4_endpoint_v3_spec.md'
COUNT='acceleration/results/20261003_independent_review/weight5_c4_raw_full02/summary.json'
LOW_AUDIT='acceleration/results/20261003_independent_review/incidence_low_weights01/summary.json'
INTERVAL='acceleration/audit_20261003_incidence_griesmer_v1.md'
PINS={
'acceleration/audit_20261003_triangle_kernel_c4_endpoint_v2.py':'4714c255caddc6840a210af1e0fd38e9b1eafb3f54418f2c24b36abe66dcf182',
'acceleration/audit_20261003_triangle_kernel_c4_endpoint_v2_spec.md':'d678dcae0c8890cd797c656ec0404a61a2f82f849f6293aab0cacd43b6a9598c',
'acceleration/audit_20261003_triangle_kernel_c4_endpoint_v2_review.md':'c96332afedda33c6839ff8439ef31d982a3ec287d7c616a77e049803d63567ad',
'acceleration/audit_20261003_triangle_kernel_c4_endpoint_v2_review_correction_v1.md':'573ef3f82ceedc422e940dcc11415355cf0adb3e11809234c0cd104ad4a1470f',
'acceleration/audit_20261003_triangle_kernel_c4_endpoint_v1.py':'a19873a20b658c28945388893b2c70af71766e63206e8781525478158c1b4cdb',
'acceleration/audit_20261003_triangle_kernel_c4_endpoint_v1_spec.md':'eacec481d2026da26c4b3aec8d085f78fa7471ea860fb451f7e41a213cc8d3a7',
PRODUCER:'7cb503ef66a494192856c10f8dbd33c3b6d094d1ecbb6d33b13c82fefb69c219',
PRODUCER_SPEC:'946cedbb301af25ff722e1592a9e4d947c9f86485eeaa57f71757b5e7bf9ed18',
COUNT:'75bf5f7adc8b082311b4ad786d46f53857960ea07c8cb58576c3a38d2bbce5a5',
LOW_AUDIT:'626e405502f6054483d7bc722610e83788c663d50d016f34a48b248edea4c2cd',
INTERVAL:'65d8eea3f4d72eb56391284f95eb43ad021e92a88a41fdcc2fe7a2e10f9dd92d',
'acceleration/results/20261003_independent_review/weight5_c4_raw_full_supervision02/summary.json':'954c218a27bd053d353c5d8a27320c05b3e1e1d82b059aa20fcf26d4182f1fa3',
'acceleration/audit_20261003_triangle_kernel_four_counts_lp_v3.py':'f72133c5bd1e8cfb8fa9459e29c75c2f4e98f6b5dff79ea8974fdb1f0daf4df6'}
W=list(range(36,61,2))
L={3:231,4:2079,5:22869,6:24486}
CAL_STATUS='INDEPENDENT_TRIANGLE_KERNEL_C4_ENDPOINT_CHECKER_V1_CALIBRATION_PASS'
FULL_STATUS='INDEPENDENT_TRIANGLE_KERNEL_C4_ENDPOINT_COMPLETE_DUAL_V1_PASS'

def need(ok,stage):
 if not ok:raise ValueError(stage)
def sha(path):
 with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def pairs(q):return [q.numerator,q.denominator]
def same(a,b):return json.dumps(a,sort_keys=True,allow_nan=False,separators=(',',':'))==json.dumps(b,sort_keys=True,allow_nan=False,separators=(',',':'))
def rational(v):
 need(type(v)is list and len(v)==2 and all(type(t)is int for t in v) and v[1]>0,'RATIONAL_SYNTAX')
 q=Fraction(*v);need(pairs(q)==v,'REDUCED_RATIONAL');return q
def save(path,value):
 with path.open('x',encoding='utf8',newline='\n')as stream:json.dump(value,stream,indent=2,allow_nan=False);stream.write('\n')
def read(path):
 def unique(items):
  result={}
  for k,v in items:
   need(k not in result,'DUPLICATE_JSON_KEY');result[k]=v
  return result
 return json.loads(path.read_bytes(),object_pairs_hook=unique)
@lru_cache(maxsize=None)
def poly(n,w):
 need(type(n)is int and type(w)is int and 0<=w<=n,'POLYNOMIAL_DOMAIN')
 coefficients=[1]
 for sign in [-1]*w+[1]*(n-w):
  nxt=[0]*(len(coefficients)+1)
  for j,value in enumerate(coefficients):nxt[j]+=value;nxt[j+1]+=sign*value
  coefficients=nxt
 return tuple(coefficients)
def model(n,weights,lower):
 z=poly(n,0)
 need(type(weights)is list and len(set(weights))==len(weights) and all(type(w)is int and 1<=w<=n for w in weights),'WEIGHT_DOMAIN')
 need(all(type(j)is int and 1<=j<=n and type(q)is int and 0<=q<z[j] for j,q in lower.items()),'LOWER_COUNTS')
 return [[Fraction(lower.get(j,0)-poly(n,w)[j],z[j]-lower.get(j,0)) for j in range(1,n+1)] for w in weights]
def dual(n,weights,lower,y):
 need(type(y)is list and len(y)==n,'DUAL_LENGTH')
 need(all(type(q)is Fraction and q>=0 for q in y),'NONNEGATIVE_DUAL')
 lhs=[sum(q*r for q,r in zip(row,y)) for row in model(n,weights,lower)]
 need(all(q>=1 for q in lhs),'ALL_WEIGHT_INEQUALITIES')
 bound=1+sum(y);dim=0
 while Fraction(1<<(dim+1))<=bound:dim+=1
 return bound,lhs,dim
def system(n,lower,degrees,ends):
 raw=[[Fraction(lower.get(j,0)-poly(n,w)[j]) for j in degrees] for w in ends]
 a,b=raw[0];c,d=raw[1];det=a*d-b*c;need(det!=0,'NONSINGULAR_SYSTEM')
 # Independent rational Gaussian elimination instead of producer closed inversion.
 rows=[[*raw[0],Fraction(1)],[*raw[1],Fraction(1)]]
 if rows[0][0]==0:rows.reverse()
 first=rows[0][0];need(first!=0,'NONSINGULAR_SYSTEM')
 rows[0]=[q/first for q in rows[0]];factor=rows[1][0]
 rows[1]=[q-factor*r for q,r in zip(rows[1],rows[0])]
 pivot=rows[1][1];need(pivot!=0,'NONSINGULAR_SYSTEM')
 rows[1]=[q/pivot for q in rows[1]];factor=rows[0][1]
 rows[0]=[q-factor*r for q,r in zip(rows[0],rows[1])]
 z=[rows[0][2],rows[1][2]]
 return dict(degrees=degrees,endpoint_weights=ends,unnormalized_matrix_pairs=[[pairs(q) for q in row]for row in raw],
 determinant=pairs(det),unnormalized_dual_pairs=[pairs(q)for q in z]),z
def expected_model():
 zero=poly(99,0)
 return dict(schema='TRIANGLE_KERNEL_LOW_WEIGHT_EXACT_MODEL_V1',weight_domain='even13',length=99,
 nonzero_weights=W,degrees=list(range(1,100)),lower_word_counts={str(j):q for j,q in L.items()},
 normalized_denominators=[zero[j]-L.get(j,0) for j in range(1,100)],
 coefficient_pairs=[[pairs(q)for q in row]for row in model(99,W,L)],rhs=[1]*13)
def check_model(raw):
 expected=expected_model()
 for key in ['schema','weight_domain','length','nonzero_weights','degrees','lower_word_counts','rhs']:need(same(raw.get(key),expected[key]),'MODEL_SCOPE')
 need(same(raw.get('normalized_denominators'),expected['normalized_denominators']),'MODEL_DENOMINATORS')
 need(type(raw.get('coefficient_pairs'))is list and len(raw['coefficient_pairs'])==13 and all(type(row)is list and len(row)==99 for row in raw['coefficient_pairs']),'MODEL_COMPLETE_SHAPE')
 actual=[[rational(q)for q in row]for row in raw['coefficient_pairs']]
 need(actual==model(99,W,L),'COMPLETE_POLYNOMIAL_COEFFICIENTS')
def check_certificate(raw):
 for key in ['schema','weight_domain','length','nonzero_weights','degrees','lower_word_counts']:
  expected=expected_model()[key] if key!='schema' else 'TRIANGLE_KERNEL_LOW_WEIGHT_COMPLETE_RATIONAL_DUAL_V1'
  need(same(raw.get(key),expected),'CERTIFICATE_SCOPE')
 need(type(raw.get('dual_pairs'))is list,'DUAL_LENGTH')
 y=[rational(q)for q in raw['dual_pairs']];bound,lhs,dim=dual(99,W,L,y)
 need(same(raw.get('lhs_pairs'),[pairs(q)for q in lhs]),'ADVERTISED_LHS')
 need(same(raw.get('exact_size_upper'),pairs(bound)),'ADVERTISED_BOUND')
 need(same([raw.get('maximum_linear_dimension'),raw.get('conditional_incidence_rank_lower')],[dim,99-dim]),'INTEGER_DIMENSION')
 need(raw.get('optimum_asserted')is False and raw.get('target_resolution')=='NONE','SCOPE_LIMIT')
 return bound,lhs,dim,y
def check_system(raw):
 expected,z=system(99,L,[4,5],[36,60])
 need(same(raw,expected),'EXACT_ENDPOINT_SYSTEM')
 return z
def metadata(raw):
 need(raw.get('status')=='CANDIDATE_EXACT_ENDPOINT_DUAL' and raw.get('producer')=='/root/structural' and raw.get('independent_approval')is False and raw.get('target_resolution')=='NONE','PRODUCER_ROLE_SCOPE')
 need(same([raw.get('numerical_solver_invocations'),raw.get('optimization_calls'),raw.get('graph_exclusions'),raw.get('complete_exact_coefficients'),raw.get('complete_dual_coordinates'),raw.get('complete_weight_inequalities')],[0,0,0,1287,99,13]),'TYPED_PRODUCER_COUNTS')
 need(raw.get('inputs_outputs_sha256',{}).get(PRODUCER)==PINS[PRODUCER] and raw.get('inputs_outputs_sha256',{}).get(PRODUCER_SPEC)==PINS[PRODUCER_SPEC],'CHANGED_PRODUCER_IDENTITY')
def rejection(name,stage,call,records):
 try:call()
 except ValueError as err:
  need(type(err)is ValueError and str(err)==stage,'PRECISE_CONTROL_STAGE');records.append(dict(case=name,outcome='REJECTED',stage=stage));return
 raise ValueError('CORRUPTION_ACCEPTED:'+name)
def fixture():
 y=[Fraction(poly(99,0)[j]-L.get(j,0),1+sum(L.values()))for j in range(1,100)]
 bound,lhs,dim=dual(99,W,L,y)
 need(bound==Fraction(2**99,49666) and lhs==[1]*13,'SYNTHETIC_CHARACTER_SUM')
 cert={k:copy.deepcopy(v)for k,v in expected_model().items()if k not in ['normalized_denominators','coefficient_pairs','rhs']}
 cert.update(schema='TRIANGLE_KERNEL_LOW_WEIGHT_COMPLETE_RATIONAL_DUAL_V1',dual_pairs=[pairs(q)for q in y],lhs_pairs=[pairs(q)for q in lhs],exact_size_upper=pairs(bound),maximum_linear_dimension=dim,conditional_incidence_rank_lower=99-dim,optimum_asserted=False,target_resolution='NONE')
 check_model(expected_model());check_certificate(cert);return cert
def calibration():
 literal=0
 for n in range(7):
  for w in range(n+1):
   for j,value in enumerate(poly(n,w)):
    need(value==sum((-1 if (x&((1<<w)-1)).bit_count()%2 else 1)for x in range(1<<n)if x.bit_count()==j),'LITERAL_CHARACTERS');literal+=1
 triangles=[sum(1<<v for v in t) for t in __import__('itertools').combinations(range(9),3) if all(u//3==v//3 or u%3==v%3 for u,v in __import__('itertools').combinations(t,2))]
 image={0}
 for t in triangles:image|={x^t for x in image}
 kernel=[x for x in range(512)if all((x&t).bit_count()%2==0 for t in triangles)]
 lower={3:6,4:9,5:9,6:6}
 need(len(triangles)==6 and len(kernel)==16 and len(image)==32 and all(sum(x.bit_count()==j for x in image)==q for j,q in lower.items()),'LITERAL_ROOK_CODES')
 ys=[Fraction(0)]*9;ys[3]=Fraction(9);ys[5]=Fraction(6)
 bound,lhs,dim=dual(9,[4,6],lower,ys);tiny,z=system(9,lower,[4,6],[4,6])
 need(bound==16 and lhs==[1,1] and dim==4 and z==[Fraction(1,13),Fraction(1,13)],'SHARP_ROOK_ENDPOINT')
 cert=fixture();exact=expected_model();records=[]
 cases=[
 ('truncated_dual','DUAL_LENGTH','cert',lambda x:x.update(dual_pairs=x['dual_pairs'][:-1])),
 ('negative_dual','NONNEGATIVE_DUAL','cert',lambda x:x['dual_pairs'].__setitem__(0,[-1,1])),
 ('float_pair','RATIONAL_SYNTAX','cert',lambda x:x['dual_pairs'].__setitem__(0,[1.0,1])),
 ('bool_pair','RATIONAL_SYNTAX','cert',lambda x:x['dual_pairs'].__setitem__(0,[True,1])),
 ('zero_denominator','RATIONAL_SYNTAX','cert',lambda x:x['dual_pairs'].__setitem__(0,[1,0])),
 ('unreduced_fraction','REDUCED_RATIONAL','cert',lambda x:x['dual_pairs'].__setitem__(0,[2,2])),
 ('zero_dual','ALL_WEIGHT_INEQUALITIES','cert',lambda x:x.update(dual_pairs=[[0,1]]*99)),
 ('changed_lhs','ADVERTISED_LHS','cert',lambda x:x['lhs_pairs'].__setitem__(0,[2,1])),
 ('changed_bound','ADVERTISED_BOUND','cert',lambda x:x.update(exact_size_upper=[1,1])),
 ('wrong_rank','INTEGER_DIMENSION','cert',lambda x:x.update(conditional_incidence_rank_lower=99)),
 ('bool_dimension','INTEGER_DIMENSION','cert',lambda x:x.update(maximum_linear_dimension=True)),
 ('claimed_optimum','SCOPE_LIMIT','cert',lambda x:x.update(optimum_asserted=True)),
 ('claimed_resolution','SCOPE_LIMIT','cert',lambda x:x.update(target_resolution='UNSAT')),
 ('old_N5_certificate','CERTIFICATE_SCOPE','cert',lambda x:x['lower_word_counts'].__setitem__('5',12474)),
 ('different_domain_certificate','CERTIFICATE_SCOPE','cert',lambda x:x.update(weight_domain='divisible4_seven')),
 ('changed_model_schema','MODEL_SCOPE','model',lambda x:x.update(schema='WRONG')),
 ('old_N5_model','MODEL_SCOPE','model',lambda x:x['lower_word_counts'].__setitem__('5',12474)),
 ('bool_length','MODEL_SCOPE','model',lambda x:x.update(length=True)),
 ('omitted_weight','MODEL_SCOPE','model',lambda x:x.update(nonzero_weights=W[:-1])),
 ('changed_denominator','MODEL_DENOMINATORS','model',lambda x:x['normalized_denominators'].__setitem__(4,1)),
 ('omitted_row','MODEL_COMPLETE_SHAPE','model',lambda x:x.update(coefficient_pairs=x['coefficient_pairs'][:-1])),
 ('character_sign','COMPLETE_POLYNOMIAL_COEFFICIENTS','model',lambda x:x['coefficient_pairs'][0].__setitem__(4,pairs(rational(x['coefficient_pairs'][0][4])+1))),
 ('bool_coefficient','RATIONAL_SYNTAX','model',lambda x:x['coefficient_pairs'][0].__setitem__(4,[False,1]))]
 for name,stage,kind,change in cases:
  damaged=copy.deepcopy(cert if kind=='cert' else exact);change(damaged)
  rejection(name,stage,lambda damaged=damaged,kind=kind:check_certificate(damaged)if kind=='cert' else check_model(damaged),records)
 # Calibrate Gaussian elimination and endpoint metadata on a tiny known sharp fixture.
 for name,change in [('wrong_determinant',lambda x:x.update(determinant=[1,1])),('bool_determinant',lambda x:x.update(determinant=[True,1])),('wrong_endpoint',lambda x:x.update(endpoint_weights=[4,5])),('wrong_unnormalized_dual',lambda x:x['unnormalized_dual_pairs'].__setitem__(0,[0,1]))]:
  damaged=copy.deepcopy(tiny);change(damaged)
  rejection(name,'TINY_ENDPOINT_IDENTITY',lambda damaged=damaged:need(same(damaged,tiny),'TINY_ENDPOINT_IDENTITY'),records)
 rejection('singular_system','NONSINGULAR_SYSTEM',lambda:system(3,{},[1,3],[1,2]),records)
 rejection('zero_word_omitted','SHARP_CHARACTER_ZERO',lambda:need(sum(poly(9,x.bit_count())[5] for x in kernel if x)>=9*len(kernel),'SHARP_CHARACTER_ZERO'),records)
 meta=dict(status='CANDIDATE_EXACT_ENDPOINT_DUAL',producer='/root/structural',independent_approval=False,target_resolution='NONE',numerical_solver_invocations=0,optimization_calls=0,graph_exclusions=0,complete_exact_coefficients=1287,complete_dual_coordinates=99,complete_weight_inequalities=13,inputs_outputs_sha256={PRODUCER:PINS[PRODUCER],PRODUCER_SPEC:PINS[PRODUCER_SPEC]})
 for name,stage,change in [('bool_solver_count','TYPED_PRODUCER_COUNTS',lambda x:x.update(numerical_solver_invocations=False)),('producer_selfapproval','PRODUCER_ROLE_SCOPE',lambda x:x.update(independent_approval=True)),('wrong_source_pin','CHANGED_PRODUCER_IDENTITY',lambda x:x['inputs_outputs_sha256'].__setitem__(PRODUCER,'0'*64))]:
  damaged=copy.deepcopy(meta);change(damaged);rejection(name,stage,lambda damaged=damaged:metadata(damaged),records)
 old_wrong_y=[Fraction(0)]*9;old_wrong_y[3]=Fraction(6);old_wrong_y[4]=Fraction(9)
 rejection('preserved_wrong_rook45_dual','ALL_WEIGHT_INEQUALITIES',lambda:dual(9,[4,6],lower,old_wrong_y),records)
 rejection('preserved_singular_rook45_system','NONSINGULAR_SYSTEM',lambda:system(9,lower,[4,5],[4,6]),records)
 need(literal==140 and len(records)==34,'CALIBRATION_POPULATIONS')
 return dict(complete_literal_characters=literal,complete_rook_kernel=kernel,complete_rook_image=sorted(image),rook_size_upper=[16,1],rook_lhs=[[1,1],[1,1]],synthetic_size_upper=pairs(Fraction(2**99,49666)),synthetic_complete_coefficients=1287,strict_controls=records)
def main():
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['calibration','full']);p.add_argument('--seconds',type=float,required=True);p.add_argument('--out',type=Path,required=True)
 for arg in ['calibration','calibration-sha256','producer-summary','producer-summary-sha256','supervisor','supervisor-sha256']:p.add_argument('--'+arg)
 a=p.parse_args();deadline=CommandDeadline(a.seconds,allocation_reason='Independent full exact polynomial/rational endpoint check and fresh strict controls, no optimizer;10second serialization reserve')
 out=a.out.resolve();need(out.is_relative_to(ROOT) and not out.exists(),'FRESH_OUTPUT');out.mkdir(parents=True);pins={};protected={name:sha(ROOT/name)for name in ['CLAIMS.yaml','.git/index']}
 def pin(name,identity):
  need(deadline.status()['remaining_seconds']>10,'SERIALIZATION_RESERVE');path=(ROOT/name).resolve();need(path.is_relative_to(ROOT),'INPUT_BOUNDARY');need(sha(path)==identity,'EXACT_SOURCE_ARTIFACT_HASH');need(name not in pins or pins[name]==identity,'CONSISTENT_IDENTITY');pins[name]=identity
 def closure(report):
  for name,identity in report['inputs_sha256'].items():pin(name,identity)
 try:
  for name,identity in PINS.items():pin(name,identity)
  for name in [SOURCE,SPEC,PROOF,'pyproject.toml','uv.lock','acceleration/command_deadline.py','acceleration/run_compute_command.py']:pin(name,sha(ROOT/name))
  count=read(ROOT/COUNT);need(same([count['status'],count['producer'],count['verifier'],count['method'],count['universal_derivation_checked'],count['producer_outputs_checked'],count['target_weight5_lower_count'],count['target_character_rhs'],count['target_resolution']],['INDEPENDENT_WEIGHT5_C4_COLLISION_COMPLETE_RAW_V1_PASS','/root/structural','/root','independent_derivation_and_complete_artifact_checking',True,True,22869,71500275,'NONE']),'EXACT_C4_PREMISE')
  low=read(ROOT/LOW_AUDIT);need(same(low['target_lower_word_counts'],{'3':231,'4':2079,'6':24486}) and low['universal_derivation_checked']is True,'EXACT_LOW_COUNTS_PREMISE');closure(count);closure(low)
  cal=calibration();save(out/'controls.json',cal);pin((out/'controls.json').relative_to(ROOT).as_posix(),sha(out/'controls.json'))
  result=dict(status=CAL_STATUS,producer_outputs_checked=False,complete_exact_coefficients_checked=0,complete_nonnegative_dual_coordinates_checked=0,complete_exact_weight_inequalities_checked=0)
  if a.mode=='full':
   need(all([a.calibration,a.calibration_sha256,a.producer_summary,a.producer_summary_sha256,a.supervisor,a.supervisor_sha256]),'EXPLICIT_ACTUAL_IDENTITIES')
   for name,identity in [(a.calibration,a.calibration_sha256),(a.producer_summary,a.producer_summary_sha256),(a.supervisor,a.supervisor_sha256)]:pin(name,identity)
   previous=read(ROOT/a.calibration);need(previous['status']==CAL_STATUS and previous['producer_outputs_checked']is False and previous['inputs_sha256'][SOURCE]==pins[SOURCE] and previous['inputs_sha256'][SPEC]==pins[SPEC],'FRESH_APPLICABLE_CALIBRATION');closure(previous)
   terminal=read(ROOT/a.supervisor);need(terminal['command_exit_code']==0 and terminal['error']is None and terminal['deadline_reached']is False and terminal['cleanup']['reaped']is True and terminal['cleanup']['job_active_zero_observed']is True and terminal['cleanup']['cleanup_errors']==[],'COMPLETE_CONTAINED_PRODUCER')
   report=read(ROOT/a.producer_summary);metadata(report)
   for name,identity in report['inputs_outputs_sha256'].items():pin(name,identity)
   folder=(ROOT/a.producer_summary).parent
   def raw(name):
    member=(folder/name).relative_to(ROOT).as_posix();need(member in report['inputs_outputs_sha256'],'RAW_MEMBER_RECORDED');return read(ROOT/member)
   exact=raw('exact_model.json');certificate=raw('certificate.json');check_model(exact);bound,lhs,dim,y=check_certificate(certificate);z=check_system(raw('endpoint_system.json'))
   need(all(y[j-1]==z[[4,5].index(j)]*(poly(99,0)[j]-L[j]) if j in [4,5] else y[j-1]==0 for j in range(1,100)),'ENDPOINT_COMPLETE_DUAL_BINDING')
   need(same(report['exact_endpoint_system'],raw('endpoint_system.json')) and same([report['exact_size_upper'],report['maximum_linear_dimension'],report['conditional_incidence_rank_lower']],[pairs(bound),dim,99-dim]),'SUMMARY_RAW_BINDING')
   need(bound==Fraction(12187808,2723) and dim==12 and 99-dim==87,'EXACT_ENDPOINT_RESULT')
   author=raw('controls.json');need(same(author['complete_rook_kernel'],cal['complete_rook_kernel']) and same(author['complete_rook_image'],cal['complete_rook_image']) and same(author['rook_size_upper'],[16,1]) and type(author['literal_character_coefficients'])is int and author['literal_character_coefficients']==140 and author['full_target_endpoint_constructed']is False,'AUTHOR_LITERAL_CONTROLS')
   result=dict(status=FULL_STATUS,producer_outputs_checked=True,complete_exact_coefficients_checked=1287,complete_nonnegative_dual_coordinates_checked=99,complete_exact_weight_inequalities_checked=13,exact_size_upper=pairs(bound),maximum_linear_dimension=dim,conditional_incidence_rank_lower=99-dim,exact_lhs_pairs=[pairs(q)for q in lhs],exact_endpoint_system=raw('endpoint_system.json'),
   statement='For every srg(99,14,1,2), its complete 99-by231 triangle-incidence matrix B has binary rank at least87: its binary kernel has size at most12187808/2723<8192, hence dimension at most12. This conditional implication allows the zero kernel and uses the even36..60 nonzero-weight interval and image counts N3>=231,N4>=2079,N5>=22869,N6>=24486.')
  need(all(sha(ROOT/name)==identity for name,identity in protected.items()),'PROTECTED_STATE_CHANGED')
  result.update(checker_implementation_version=3,timestamp=datetime.now(timezone.utc).isoformat(),producer='/root/structural',verifier='/root',method='independent_derivation_and_complete_artifact_checking',claim_revision=1,inputs_sha256=pins,command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),strict_corruptions=34,complete_literal_characters=140,lower_word_counts={str(j):q for j,q in L.items()},weight_domain='even13',universal_conditional_derivation_checked=True,target_resolution='NONE',graph_exclusions=0,optimum_asserted=False,rank_upper_asserted=False,nonzero_kernel_asserted=False,numerical_solver_invocations=0,historical_protected_execution_state=protected,deadline=deadline.status(),
  shared_components=['Polynomial product/Fraction algorithm adapted from ROOT f721 independent checker; no discovery imports and no old gate transfer.','Fresh Gaussian elimination differs from discovery closed inversion. Exact prior graph premise proofs, Python integer/Fraction arithmetic, hashing/JSON and locked deadline runtime trusted.'],
  limitations=['Conditional target theorem only; no graph, nonexistence, optimizer optimum, rank upper bound, forced nonzero kernel, novelty or external review.','Calibration uses complete synthetic target-sized model and literal rook, without constructing the target endpoint; full reconstructs complete actual producer raw model, certificate and system.','Independent finite controls do not establish universal graph premises; separate written proofs and input audits remain explicit.'])
  save(out/'summary.json',result);print(result['status'])
 except BaseException as error:save(out/'failure.json',dict(error=repr(error),inputs_sha256=pins,deadline=deadline.status(),preserved_outputs=True));raise
if __name__=='__main__':main()

