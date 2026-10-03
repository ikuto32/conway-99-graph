"""Append-only auditor clarification; no mathematical rerun or ledger change."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,copy,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'acceleration/results/20260930_independent_review/gf2_alternating_completion_v2'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):
 with p.open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False)
 inputs={BASE/'summary.json':'a18dbc2aff1e98a881226e04432e3db08a0b827741dc615eaf00c1c06ca0d093',BASE/'claim_bindings.json':'dbf2ef99403476d7bf438843e075446e463833df6a2ef30f02e8ee23c71b3255'}
 for f,h in inputs.items():
  if sha(f)!=h:raise ValueError('old immutable input changed: '+str(f))
 original=json.loads((BASE/'claim_bindings.json').read_bytes());result=copy.deepcopy(original);stamp=datetime.now(timezone.utc).isoformat()
 result['claims'][0]['statement']='For arbitrary GF(2) matrices F,H of equal shape, an alternating D satisfying FD=H exists exactly when ker(F^T) is contained in ker(H^T) and FH^T is alternating. Requiring D1=0 adds exactly H1=0 and H^T x=0 whenever F^T x=1 is solvable. In the triangle specialization, let n be even, C be a simple undirected three-cell cubic scaffold with one neighbour in each cell, let the integer factor satisfy FF^T=nI-C-C^2+2J-U, and set H=(I+C)F over GF(2). Then FH^T is automatically alternating, so only the kernel condition remains for an alternating solution of the binary mixed equation.'
 result['claims'][0]['assumptions']=['General criterion: F,H are arbitrary equal-shaped matrices over GF(2); alternating means symmetric and zero diagonal.','Triangle specialization only: n is even, C is binary symmetric zero-diagonal on three n-cells and has one neighbour in each cell per row; U is the block diagonal of three all-one n-by-n matrices.','Triangle specialization only: F has the stated integer Gram identity, and H=(I+C)F is formed over GF(2).','The Dj=0 extension uses both extra conditions stated; no quadratic residual identity or integer residual degree follows.']
 result['claims'][1]['statement']='Over any field, symmetric block completions A=[[B,E],[E^T,D]] obey rank(A)>=2rank([B,E])-rank(B). Separately, over GF(2), for the triangle scaffold with even cell size n and an incidence matrix F having even sums in every cell of every column, B is the triangle-plus-core block and E=[0;F], and rank([B,E])<=3n. Hence over GF(2), when n=12 and the target rank is54, this lower-bound test is automatically satisfied conditional on rank(B)>=18. No universal rank(B)>=18 premise is asserted.'
 result['claims'][1]['assumptions']=['General block inequality: B,D are symmetric over one arbitrary field, E is rectangular and ranks are over that same field.','Triangle specialization only: all ranks and kernel equations are over GF(2); n is even and the simple cubic three-cell core has one neighbour per cell.','Triangle specialization only: each F column has even sum in each of the three cells; B=[[J3-I3,R^T],[R,C]] and E=[0;F], with R the cell-indicator matrix.','Target consequence only: n=12, the previously proved target binary rank is54, and rank(B)>=18 is an explicit condition, not a proved universal property.']
 for old,new in zip(original['claims'],result['claims']):
  new['updated_at']=stamp;new['scope_clarification']=dict(original_binding_path=(BASE/'claim_bindings.json').relative_to(ROOT).as_posix(),original_binding_sha256=inputs[BASE/'claim_bindings.json'],mathematical_statement_unchanged=True,reason='Make the field and the triangle H/n hypotheses explicit in the compact registry statement.',approved_by='/root/eight_domain_audit')
  if old['id']!=new['id']or old['revision']!=new['revision']:raise ValueError('claim identity changed')
 save(out/'claim_bindings.json',result);pins={f.relative_to(ROOT).as_posix():h for f,h in inputs.items()};pins[Path(__file__).relative_to(ROOT).as_posix()]=sha(Path(__file__))
 save(out/'summary.json',dict(status='INDEPENDENT_GF2_COMPLETION_SCOPE_CLARIFICATION_PASS',timestamp=stamp,verifier='/root/eight_domain_audit',inputs_sha256=pins,outputs_sha256={(out/'claim_bindings.json').relative_to(ROOT).as_posix():sha(out/'claim_bindings.json')},unchanged_originals=True,mathematical_rerun=False,semantic_claims_unchanged=True,ledger_writes=0,command=[sys.executable,*sys.argv]));print(json.dumps(dict(summary_sha256=sha(out/'summary.json'),bindings_sha256=sha(out/'claim_bindings.json'))))
if __name__=='__main__':main()
