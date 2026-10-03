"""Source-only exact two-row endpoint candidate; no floating optimizer."""
import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
from itertools import combinations
import json
from math import comb
from pathlib import Path
import platform
import subprocess
import sys
from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
SOURCE='acceleration/theory_20261003_triangle_kernel_c4_endpoint_v3.py'
SPEC='acceleration/theory_20261003_triangle_kernel_c4_endpoint_v3_spec.md'
PRODUCER='acceleration/theory_20261003_triangle_image_weight5_c4_v2.py'
PRODUCER_SHA='f10cc3f06d0178ff73ea9db547fb01662e3f65ae8f3664e1abf637667dc4fd87'
PRODUCER_SPEC='acceleration/theory_20261003_triangle_image_weight5_c4_v2_spec.md'
PRODUCER_SPEC_SHA='d84d894f7f69f26d236ae0020ea9ee8cb069a8373c47135bed4076853fddd843'
LOW='acceleration/results/20261003_independent_review/incidence_low_weights01/summary.json'
LOW_SHA='626e405502f6054483d7bc722610e83788c663d50d016f34a48b248edea4c2cd'
INTERVAL='acceleration/audit_20261003_incidence_griesmer_v1.md'
INTERVAL_SHA='65d8eea3f4d72eb56391284f95eb43ad021e92a88a41fdcc2fe7a2e10f9dd92d'
COLLISION_PROOF='acceleration/audit_20261003_triangle_image_weight5_c4_v1.md'
COLLISION_PROOF_SHA='bdc99b2f6a2bf92f9e322616227c4be26db7d57b08ccbcfd9353fbf76260ce12'
HISTORICAL_SOURCE='acceleration/theory_20261003_triangle_kernel_c4_endpoint_v2.py'
HISTORICAL_SOURCE_SHA='91df2f1b782f0e7b8d30478a1e338deab6fb8341ea686b50983acf5d2892a531'
HISTORICAL_SPEC='acceleration/theory_20261003_triangle_kernel_c4_endpoint_v2_spec.md'
HISTORICAL_SPEC_SHA='01c7cd3813bf43a18882ad08092e79c7461bbc747812b31f8f71c1eebc9b50c8'
LOWER={3:231,4:2079,5:22869,6:24486}
WEIGHTS=list(range(36,61,2))
COUNT_STATUS='INDEPENDENT_WEIGHT5_C4_COLLISION_COMPLETE_RAW_V1_PASS'
CHECKER_STATUS='INDEPENDENT_TRIANGLE_KERNEL_C4_ENDPOINT_CHECKER_V1_CALIBRATION_PASS'

def need(ok,stage):
 if not ok: raise ValueError(stage)
def sha(path):
 with path.open('rb')as stream: return hashlib.file_digest(stream,'sha256').hexdigest()
def save(path,value):
 with path.open('x',encoding='utf8',newline='\n')as stream:
  json.dump(value,stream,indent=2,allow_nan=False);stream.write('\n')
def frac(value): return [value.numerator,value.denominator]
def kraw(n,j,w):
 return sum((-1)**s*comb(w,s)*comb(n-w,j-s)for s in range(max(0,j-(n-w)),min(j,w)+1))
def matrix(n,weights,lower):
 need(type(n)is int and n>=1 and all(type(w)is int and 1<=w<=n for w in weights),'CODE_DOMAIN')
 need(all(type(j)is int and 1<=j<=n and type(v)is int and 0<=v<comb(n,j)for j,v in lower.items()),'NORMALIZATION_DOMAIN')
 return [[Fraction(lower.get(j,0)-kraw(n,j,w),comb(n,j)-lower.get(j,0))for j in range(1,n+1)]for w in weights]
def endpoint(n,weights,lower,degrees,ends):
 need(len(degrees)==len(ends)==2 and len(set(degrees))==len(set(ends))==2 and all(j in range(1,n+1)for j in degrees)and all(w in weights for w in ends),'ENDPOINT_DOMAIN')
 raw=[[Fraction(lower.get(j,0)-kraw(n,j,w))for j in degrees]for w in ends]
 a,b=raw[0];c,d=raw[1];det=a*d-b*c;need(det!=0,'NONSINGULAR_ENDPOINT')
 z=[(d-b)/det,(a-c)/det];dual=[Fraction(0)]*n
 for j,value in zip(degrees,z):dual[j-1]=value*(comb(n,j)-lower.get(j,0))
 return dual,dict(degrees=degrees,endpoint_weights=ends,unnormalized_matrix_pairs=[[frac(v)for v in row]for row in raw],determinant=frac(det),unnormalized_dual_pairs=[frac(v)for v in z])
def exact_check(n,weights,lower,dual):
 need(type(dual)is list and len(dual)==n and all(type(v)is Fraction for v in dual),'COMPLETE_RATIONAL_DUAL')
 need(all(v>=0 for v in dual),'NONNEGATIVE_DUAL')
 lhs=[sum(v*y for v,y in zip(row,dual))for row in matrix(n,weights,lower)]
 need(all(v>=1 for v in lhs),'ALL_EXACT_INEQUALITIES')
 bound=1+sum(dual);dimension=0
 while Fraction(1<<(dimension+1))<=bound:dimension+=1
 need(Fraction(1<<dimension)<=bound<Fraction(1<<(dimension+1)),'EXACT_POWER2_THRESHOLD')
 return bound,lhs,dimension
def rejects(callback,stage):
 try:callback()
 except ValueError as error:
  need(type(error)is ValueError and str(error)==stage,'PRECISE_CORRUPTION_STAGE');return stage
 raise ValueError('CORRUPTION_ACCEPTED')
def controls():
 n=9;adj=[{v for v in range(n)if v!=u and(u//3==v//3 or u%3==v%3)}for u in range(n)]
 triangles=[sum(1<<v for v in t)for t in combinations(range(n),3)if all(v in adj[u]for u,v in combinations(t,2))]
 image={0}
 for t in triangles:image|={x^t for x in image}
 kernel=[x for x in range(1<<n)if all((x&t).bit_count()%2==0 for t in triangles)]
 lower={3:6,4:9,5:9,6:6};need(len(triangles)==6 and len(image)==32 and len(kernel)==16 and Counter(x.bit_count()for x in kernel)=={0:1,4:9,6:6},'ROOK_LITERAL_KERNEL')
 need(all(sum(x.bit_count()==j for x in image)==v for j,v in lower.items()),'ROOK_LITERAL_IMAGE')
 y,system=endpoint(n,[4,6],lower,[4,6],[4,6]);bound,lhs,dimension=exact_check(n,[4,6],lower,y)
 need(y==[Fraction(0),Fraction(0),Fraction(0),Fraction(9),Fraction(0),Fraction(6),Fraction(0),Fraction(0),Fraction(0)]and system['unnormalized_dual_pairs']==[[1,13],[1,13]] and bound==16 and lhs==[1,1]and dimension==4,'EXACT_ROOK_ENDPOINT_U16')
 chars=0
 for nn in range(7):
  for w in range(nn+1):
   for j in range(nn+1):
    need(kraw(nn,j,w)==sum((-1)**((u&((1<<w)-1)).bit_count())for u in range(1<<nn)if u.bit_count()==j),'LITERAL_CHARACTERS');chars+=1
 synthetic=[Fraction(comb(99,j)-LOWER.get(j,0),1+sum(LOWER.values()))for j in range(1,100)]
 sbound,slhs,sdim=exact_check(99,WEIGHTS,LOWER,synthetic)
 need(sbound==Fraction(2**99,49666)and slhs==[1]*13,'COMPLETE_SYNTHETIC_1287_CELLS')
 negatives=[]
 for name,callback,stage in [
  ('truncated_dual',lambda:exact_check(9,[4,6],lower,y[:-1]),'COMPLETE_RATIONAL_DUAL'),
  ('floating_dual',lambda:exact_check(9,[4,6],lower,[float(v)for v in y]),'COMPLETE_RATIONAL_DUAL'),
  ('negative_dual',lambda:exact_check(9,[4,6],lower,[Fraction(-1),*y[1:]]),'NONNEGATIVE_DUAL'),
  ('zero_dual',lambda:exact_check(9,[4,6],lower,[Fraction(0)]*9),'ALL_EXACT_INEQUALITIES'),
  ('insufficient_scale',lambda:exact_check(9,[4,6],lower,[v/2 for v in y]),'ALL_EXACT_INEQUALITIES'),
  ('preserved_wrong_rook_degree45_dual',lambda:exact_check(9,[4,6],lower,[Fraction(0),Fraction(0),Fraction(0),Fraction(6),Fraction(9),Fraction(0),Fraction(0),Fraction(0),Fraction(0)]),'ALL_EXACT_INEQUALITIES'),
  ('preserved_singular_rook_degree45_system',lambda:endpoint(9,[4,6],lower,[4,5],[4,6]),'NONSINGULAR_ENDPOINT'),
  ('singular_endpoints',lambda:endpoint(3,[1,2,3],{},[1,3],[1,2]),'NONSINGULAR_ENDPOINT'),
  ('repeated_endpoint',lambda:endpoint(9,[4,6],lower,[4,6],[4,4]),'ENDPOINT_DOMAIN'),
  ('missing_endpoint',lambda:endpoint(9,[4,6],lower,[4,6],[4,5]),'ENDPOINT_DOMAIN'),
  ('zero_denominator',lambda:matrix(3,[1],{3:1}),'NORMALIZATION_DOMAIN'),
  ('changed_rook_weight5_count',lambda:need(sum(kraw(9,5,x.bit_count())for x in kernel)>=10*len(kernel),'EXACT_CHARACTER_IMAGE_COUNT'),'EXACT_CHARACTER_IMAGE_COUNT'),
  ('omitted_zero_word',lambda:need(sum(kraw(9,5,x.bit_count())for x in kernel if x)>=9*len(kernel),'EXACT_CHARACTER_A0_CONSTANT'),'EXACT_CHARACTER_A0_CONSTANT')]:
  negatives.append(dict(case=name,observed_stage=rejects(callback,stage)))
 return dict(status='AUTHOR_C4_ENDPOINT_ARITHMETIC_CONTROLS_PASS_PENDING_INDEPENDENT_CALIBRATION',complete_rook_kernel=kernel,complete_rook_image=sorted(image),rook_exact_dual=[frac(v)for v in y],rook_system=system,rook_size_upper=frac(bound),literal_character_coefficients=chars,synthetic_complete_model_cells=1287,synthetic_complete_dual_coordinates=99,synthetic_complete_weight_inequalities=13,synthetic_upper=frac(sbound),strict_negative_controls=negatives,full_target_endpoint_constructed=False,numerical_solver_invocations=0)
def main():
 p=argparse.ArgumentParser();p.add_argument('--mode',choices=['calibration','endpoint'],required=True);p.add_argument('--seconds',type=float,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--source-sha256',required=True);p.add_argument('--protocol-sha256',required=True);p.add_argument('--count-audit',type=Path);p.add_argument('--count-audit-sha256');p.add_argument('--checker-calibration',type=Path);p.add_argument('--checker-calibration-sha256');a=p.parse_args()
 deadline=CommandDeadline(a.seconds,allocation_reason='Exact two by two endpoint arithmetic and1287 rational coefficients only;no numerical solver;10second preservation reserve')
 out=a.out.resolve();need(out.is_relative_to(ROOT)and not out.exists(),'FRESH_WORKSPACE_OUTPUT');out.mkdir(parents=True);pins={};protected={path:sha(ROOT/path)for path in ['CLAIMS.yaml','.git/index']}
 def pin(name,identity):
  need(deadline.status()['remaining_seconds']>10,'SERIALIZATION_RESERVE');path=(ROOT/name).resolve();need(path.is_relative_to(ROOT),'INPUT_BOUNDARY');actual=sha(path);need(actual==identity,'EXACT_INPUT_IDENTITY');need(name not in pins or pins[name]==actual,'STABLE_INPUT');pins[name]=actual
 try:
  for name,identity in {SOURCE:a.source_sha256,SPEC:a.protocol_sha256,PRODUCER:PRODUCER_SHA,PRODUCER_SPEC:PRODUCER_SPEC_SHA,LOW:LOW_SHA,INTERVAL:INTERVAL_SHA,COLLISION_PROOF:COLLISION_PROOF_SHA,HISTORICAL_SOURCE:HISTORICAL_SOURCE_SHA,HISTORICAL_SPEC:HISTORICAL_SPEC_SHA}.items():pin(name,identity)
  for name in ['pyproject.toml','uv.lock','acceleration/command_deadline.py','acceleration/run_compute_command.py','docs/COMPUTE_POLICY.md','acceleration/compute_policy.json']:pin(name,sha(ROOT/name))
  control=controls();save(out/'controls.json',control)
  common=dict(timestamp=datetime.now(timezone.utc).isoformat(),producer='/root/structural',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_commit_limitation='New working source/spec and changed count are separately pinned; not asserted part of context commit.',command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),mode=a.mode,numerical_solver_invocations=0,target_resolution='NONE',independent_approval=False,protected_state=protected,shared_components=['Prior producer binomial/Fraction/raw-model convention reused as disclosed algorithm evidence; no prior code imports or old gate transfer.','Python exact integer/Fraction arithmetic, hashing/JSON and common per-command deadline helper.'])
  if a.mode=='calibration':
   need(protected=={path:sha(ROOT/path)for path in protected},'PROTECTED_STATE_CHANGED');pins[(out/'controls.json').relative_to(ROOT).as_posix()]=sha(out/'controls.json');save(out/'summary.json',dict(**common,status=control['status'],inputs_outputs_sha256=pins,positive_fixtures=2,strict_negative_controls=len(control['strict_negative_controls']),complete_literal_characters=140,target_endpoint_launched=False,deadline=deadline.status()));print(control['status']);return
  need(a.count_audit and a.count_audit_sha256 and a.checker_calibration and a.checker_calibration_sha256,'ACTUAL_INDEPENDENT_GATES_REQUIRED')
  for path,identity in [(a.count_audit,a.count_audit_sha256),(a.checker_calibration,a.checker_calibration_sha256)]:pin(path.resolve().relative_to(ROOT).as_posix(),identity)
  count=json.loads(a.count_audit.read_bytes());gate=json.loads(a.checker_calibration.read_bytes())
  need(count['status']==COUNT_STATUS and count['verifier']=='/root' and count['producer']=='/root/structural' and count['method']=='independent_derivation_and_complete_artifact_checking' and count['universal_derivation_checked']is True and count['producer_outputs_checked']is True and count['target_weight5_lower_count']==22869 and count['target_character_rhs']==71500275 and count['complete_character_coefficients']==100 and count['complete_normalized_weights']==99 and count['target_resolution']=='NONE','EXACT_CHANGED_COUNT_SCOPE')
  need(count['inputs_sha256'].get(PRODUCER)==PRODUCER_SHA and count['inputs_sha256'].get(COLLISION_PROOF)==COLLISION_PROOF_SHA,'CHANGED_PRODUCER_PROOF_GATE')
  need(gate['status']==CHECKER_STATUS and gate['producer_outputs_checked']is False and gate['inputs_sha256'].get(SOURCE)==a.source_sha256 and gate['inputs_sha256'].get(SPEC)==a.protocol_sha256,'APPLICABLE_PREOUTPUT_CHECKER_GATE')
  for report in [count,gate]:
   for name,identity in report['inputs_sha256'].items():pin(name,identity)
  low=json.loads((ROOT/LOW).read_bytes());need(low['status']=='INDEPENDENT_TRIANGLE_IMAGE_LOW_WEIGHT_COUNTS_CHARACTER_V1_PASS'and low['target_lower_word_counts']=={'3':231,'4':2079,'6':24486}and low['universal_derivation_checked']is True,'EXACT_PRIOR_LOW_COUNTS')
  coefficients=matrix(99,WEIGHTS,LOWER);save(out/'exact_model.json',dict(schema='TRIANGLE_KERNEL_LOW_WEIGHT_EXACT_MODEL_V1',weight_domain='even13',length=99,nonzero_weights=WEIGHTS,degrees=list(range(1,100)),lower_word_counts={str(j):v for j,v in LOWER.items()},normalized_denominators=[comb(99,j)-LOWER.get(j,0)for j in range(1,100)],coefficient_pairs=[[frac(v)for v in row]for row in coefficients],rhs=[1]*13,direction='Feasible complete rational dual only: y>=0,G*y>=1; no optimum assertion',scope='Conditional target triangle kernel even nonzero weights36..60 and independently established3/4/5/6 image counts; no generic binary-code bound.'))
  dual,system=endpoint(99,WEIGHTS,LOWER,[4,5],[36,60]);save(out/'endpoint_system.json',system)
  bound,lhs,dimension=exact_check(99,WEIGHTS,LOWER,dual)
  need(bound==Fraction(12187808,2723),'FROZEN_ENDPOINT_CANDIDATE_BOUND')
  certificate=dict(schema='TRIANGLE_KERNEL_LOW_WEIGHT_COMPLETE_RATIONAL_DUAL_V1',weight_domain='even13',length=99,nonzero_weights=WEIGHTS,degrees=list(range(1,100)),lower_word_counts={str(j):v for j,v in LOWER.items()},dual_pairs=[frac(v)for v in dual],lhs_pairs=[frac(v)for v in lhs],exact_size_upper=frac(bound),maximum_linear_dimension=dimension,conditional_incidence_rank_lower=99-dimension,construction='One exact2x2degree4/5 intersection at weights36/60; all13exact inequalities checked afterwards',status='CANDIDATE_PENDING_INDEPENDENT_COMPLETE_ARTIFACT_AND_DERIVATION_CHECK',optimum_asserted=False,target_resolution='NONE',scope='Only conditional target kernels with new independently established N5>=22869; no generic-code, nonzero-kernel existence or graph contradiction.')
  save(out/'certificate.json',certificate);need(protected=={path:sha(ROOT/path)for path in protected},'PROTECTED_STATE_CHANGED')
  for path in out.iterdir():
   if path.is_file():pins[path.relative_to(ROOT).as_posix()]=sha(path)
  save(out/'summary.json',dict(**common,status='CANDIDATE_EXACT_ENDPOINT_DUAL',inputs_outputs_sha256=pins,exact_size_upper=frac(bound),maximum_linear_dimension=dimension,conditional_incidence_rank_lower=99-dimension,complete_exact_coefficients=1287,complete_dual_coordinates=99,complete_weight_inequalities=13,calibration_positive_fixtures=2,calibration_strict_negative_controls=len(control['strict_negative_controls']),exact_endpoint_system=system,optimization_calls=0,graph_exclusions=0,limitations=['Complete independent raw coefficient/dual checking and conditional interpretation required after output.','Zero kernel is allowed; no minimum kernel dimension or rank upper bound.','No optimum, novelty, external review or target-wide coverage assertion.'],deadline=deadline.status()));print(json.dumps(dict(status='CANDIDATE_EXACT_ENDPOINT_DUAL',size_upper=frac(bound),target_resolution='NONE')))
 except BaseException as error:
  save(out/'failure.json',dict(error=repr(error),inputs_outputs_sha256=pins,outputs_preserved=True,target_resolution='NONE',restart='No automatic retry; preserve exact source/raw/receipt and obtain separate new invocation authorization.',deadline=deadline.status()));raise
if __name__=='__main__':main()
