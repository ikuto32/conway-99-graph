"""Independent coordinate-list GF2 review; no producer/checker imports."""
from pathlib import Path
from itertools import combinations,product
from datetime import datetime,timezone
from collections import Counter
import argparse,copy,hashlib,json,platform,random,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';D=B+'gf2_alternating_completion/';SUMMARY_SHA='8abffdf66cb15dbfca6e6d0f29adf2425a9975832aeac5f5187c2c4da901fe98'
def need(x,s):
 if not x:raise ValueError(s)
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def save(p,x):
 with p.open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def trans(A):return [list(x)for x in zip(*A)]
def binary(A):need(type(A)is list and A and type(A[0])is list and all(type(r)is list and len(r)==len(A[0])and all(type(x)is int and x in(0,1)for x in r)for r in A),'strict nonempty binary matrix')
def modproduct(A,B):
 Bt=trans(B);return [[sum(x*y for x,y in zip(a,b))%2 for b in Bt]for a in A]
def reduce_rows(A,n=None):
 R=[list(r)for r in A];n=len(R[0])if n is None and R else(0 if n is None else n);piv=[];k=0
 for col in reversed(range(n)):
  pivot=next((i for i in range(k,len(R))if R[i][col]),None)
  if pivot is None:continue
  R[k],R[pivot]=R[pivot],R[k]
  for i in range(len(R)):
   if i!=k and R[i][col]:R[i]=[x^y for x,y in zip(R[i],R[k])]
  piv.append(col);k+=1
 return R,piv
def rank(A):return len(reduce_rows(A)[1])
def nullspace(A):
 R,piv=reduce_rows(A);n=len(A[0]);out=[]
 for f in range(n):
  if f in piv:continue
  x=[int(i==f)for i in range(n)]
  for r,p in zip(R,piv):x[p]=r[f]
  out.append(x)
 return out
def solve(A,b):
 n=len(A[0]);R,piv=reduce_rows([row+[v]for row,v in zip(A,b)],n)
 if any(not any(row[:n])and row[n]for row in R):return None
 x=[0]*n
 for row,p in zip(R,piv):x[p]=row[n]
 need([sum(v*w for v,w in zip(row,x))%2 for row in A]==b,'direct equation solution');return x
def alt(A):return len(A)==len(A[0])and all(A[i][i]==0 for i in range(len(A)))and A==trans(A)
def maskvec(x,n):return [(x//(2**j))%2 for j in range(n)]
def sym(n,mask,diagonal=False):
 A=[[0]*n for _ in range(n)];positions=[(i,j)for i in range(n)for j in range(i if diagonal else i+1,n)]
 for k,(i,j)in enumerate(positions):A[i][j]=A[j][i]=(mask//(2**k))%2
 return A
def conditions(F,H):
 binary(F);binary(H);need(len(F)==len(H)and len(F[0])==len(H[0]),'matched F/H dimensions');a=len(F);m=len(F[0]);ker=nullspace(trans(F));kc=all(not any(sum(x[i]*H[i][j]for i in range(a))%2 for j in range(m))for x in ker);fc=alt(modproduct(F,trans(H)));hj=all(sum(row)%2==0 for row in H);x=solve(trans(F),[1]*m);image=x is None or not any(sum(x[i]*H[i][j]for i in range(a))%2 for j in range(m))
 return dict(kernel_condition=kc,FHt_alternating=fc,alternating_solution=kc and fc,H_times_one_zero=hj,one_prescribed_image_zero=image,even_degree_alternating_solution=kc and fc and hj and image),x
def check_conditions(saved,F,H):
 expected,x=conditions(F,H)
 for k,v in expected.items():need(saved[k]==v,'exact condition '+k)
 old=saved['one_preimage'];need((old is None)==(x is None),'ones membership')
 if old is not None:
  need(type(old)is int and 0<=old<2**len(F),'preimage vector bounds');v=maskvec(old,len(F));need([sum(v[i]*F[i][j]for i in range(len(F)))%2 for j in range(len(F[0]))]==[1]*len(F[0]),'saved preimage identity')
 return expected
def direct_completion(F,H,even=False):
 a=len(F);m=len(F[0]);edges=list(combinations(range(m),2));A=[];rhs=[]
 for i in range(a):
  for j in range(m):A.append([F[i][v]if u==j else(F[i][u]if v==j else 0)for u,v in edges]);rhs.append(H[i][j])
 if even:
  for j in range(m):A.append([int(j in e)for e in edges]);rhs.append(0)
 x=solve(A,rhs)
 if x is not None:
  M=[[0]*m for _ in range(m)]
  for val,(u,v)in zip(x,edges):M[u][v]=M[v][u]=val
  need(modproduct(F,M)==H and alt(M)and(not even or all(sum(r)%2==0 for r in M)),'direct alternating solution actual identity')
 return x is not None
def block(B,E,D0):return [b+e for b,e in zip(B,E)]+[e+d for e,d in zip(trans(E),D0)]
def check_cert(A,c):
 width=len(A[0]);r=rank(A);need(c['width']==width and c['rank']==r,'certificate dimensions/rank');rows=[maskvec(v,width)for v in c['reduced_rows']];need(all(type(v)is int and 0<=v<2**width for v in c['reduced_rows']+c['kernel_basis']),'certificate integer range');need(len(rows)==r and rank(rows)==r and rank(A+rows)==r,'complete same rowspace');ps=c['pivot_columns'];need(len(ps)==r and ps==sorted(set(ps)),'saved pivot list')
 for i,p in enumerate(ps):need(rows[i][p]==1 and all(rows[j][p]==int(i==j)for j in range(r))and all(not rows[i][j]for j in range(p)),'saved reduced pivot semantics')
 ker=[maskvec(v,width)for v in c['kernel_basis']];need(len(ker)==width-r and rank(ker)==width-r and all(sum(x*y for x,y in zip(row,k))%2==0 for row in A for k in ker),'complete independent kernel')
 return r
def triangle(C):
 n=len(C)//3;A=[[0]*(3+3*n)for _ in range(3+3*n)]
 for i in range(3):
  for j in range(3):A[i][j]=int(i!=j)
  for u in range(n):A[i][3+i*n+u]=A[3+i*n+u][i]=1
 for i in range(3*n):
  for j in range(3*n):A[3+i][3+j]=C[i][j]
 return A
def target(C):
 n=len(C)//3;S=[{j for j,v in enumerate(row)if v}for row in C];return [[n*(i==j)-C[i][j]-len(S[i]&S[j])+2-int(i//n==j//n)for j in range(3*n)]for i in range(3*n)]
def cap(A):
 N=[{j for j,v in enumerate(row)if v}for row in A];v=[[i,j,len(N[i]&N[j]),2-A[i][j]]for i,j in combinations(range(len(A)),2)if len(N[i]&N[j])>2-A[i][j]];return dict(passes=not v,violations=v)
def core(C):
 binary(C);n=len(C)//3;need(3*n==len(C)and len(C[0])==len(C)and n%2==0 and alt(C),'simple even-cell core');need(all(sum(C[i][g*n:(g+1)*n])==1 for i in range(3*n)for g in range(3)),'one neighbour in each cell');G=[[v%2 for v in row]for row in target(C)];IC=[[C[i][j]^int(i==j)for j in range(3*n)]for i in range(3*n)];need(modproduct(C,G)==modproduct(G,C)and alt(modproduct(G,IC)),'universal core polynomial identities');BB=triangle(C);vectors=[[1]*3+[int(g*n<=j<(g+1)*n)for j in range(3*n)]for g in range(3)];need(rank(vectors)==3 and all(sum(a*b for a,b in zip(row,v))%2==0 for row in BB for v in vectors),'three independent literal B kernels');return BB,vectors
def graph(A,k):
 binary(A);need(alt(A)and all(sum(r)==k for r in A),'simple regular graph');N=[{j for j,v in enumerate(row)if v}for row in A]
 for i in range(len(A)):
  for j in range(len(A)):need(len(N[i]&N[j])==(k-2)*(i==j)-A[i][j]+2,'literal integer target graph identity')
 return rank(A)
def factor(C,F,saved):
 binary(F);n=len(C)//3;m=len(F[0]);BB=triangle(C);E=[[0]*m for _ in range(3)]+F;BE=[b+e for b,e in zip(BB,E)];G=target(C);N=[{d for d,v in enumerate(row)if v}for row in F];bad=[[i,j,len(N[i]&N[j]),G[i][j]]for i in range(3*n)for j in range(3*n)if len(N[i]&N[j])!=G[i][j]];H=[[(F[i][d]+sum(C[i][j]*F[j][d]for j in range(3*n)))%2 for d in range(m)]for i in range(3*n)];rb=rank(BB);s=check_cert(BE,saved['rank_B_E_certificate']);even=all(sum(F[n*g+a][d]for a in range(n))==2 for g in range(3)for d in range(m));vectors=[[1]*3+[int(g*n<=j<(g+1)*n)for j in range(3*n)]for g in range(3)];common=all(sum(row[i]*v[i]for i in range(len(v)))%2==0 for row in trans(E)for v in vectors);top=modproduct(BE,trans(BE))==BB
 actual=dict(n=n,outside=m,rank_F=rank(F),rank_B=rb,rank_B_E=s,completion_rank_lower_bound=2*s-rb,integer_Gram_mismatch_count=len(bad),first_Gram_mismatches=bad[:12],exact_two_per_cell_column=even,three_common_kernel_vectors_valid=common,top_binary_projector_identity=top)
 for k,v in actual.items():need(saved[k]==v,'raw factor diagnostic '+k)
 check_conditions(saved['mixed_completion'],F,H)
 if even:need(common and s<=3*n,'even cell margin rank ceiling')
 return actual,H
def make_core(mm,p):
 n=len(p);C=[[0]*(3*n)for _ in range(3*n)]
 for g in range(3):
  for a in range(n):C[g*n+a][g*n+mm[g][a]]=1
 for a in range(n):
  for x,y in [(a,n+a),(a,2*n+a),(n+a,2*n+p[a])]:C[x][y]=C[y][x]=1
 return C
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic();pins={}
 try:
  need(sha(ROOT/(D+'summary.json'))==SUMMARY_SHA,'candidate summary');pins[D+'summary.json']=SUMMARY_SHA;summ=read(D+'summary.json')
  for field in ['inputs_sha256','outputs_sha256']:
   for p,h in summ[field].items():need(sha(ROOT/p)==h,'frozen input '+p);pins[p]=h
  manifest=read(D+'manifest.json')
  for x in manifest['archive']:
   rel=x['path'].split('external_conway99_research/',1)[1];blob=subprocess.check_output(['git','-C',str(ROOT/'external_conway99_research'),'show',x['commit']+':'+rel]);need(blob==(ROOT/x['path']).read_bytes(),'literal archive source')
  completion=read(D+'completion_controls.json');need(len(completion)==4096,'complete F/H population');hits=evenhits=0
  for idx,rec in enumerate(completion):
   fm,hm=divmod(idx,64);need((rec['F'],rec['H'])==(fm,hm),'complete F/H ordering');F=[maskvec(fm//(8**i),3)for i in range(2)];H=[maskvec(hm//(8**i),3)for i in range(2)];expected=check_conditions(rec['conditions'],F,H);ds=[k for k in range(8)if modproduct(F,sym(3,k))==H];ed=[k for k in ds if all(sum(r)%2==0 for r in sym(3,k))];need(rec['alternating_D_masks']==ds and rec['even_D_masks']==ed,'literal exhaustive D solutions');need(direct_completion(F,H)==bool(ds)==expected['alternating_solution']and direct_completion(F,H,True)==bool(ed)==expected['even_degree_alternating_solution'],'independent unknown-D equation criterion');hits+=bool(ds);evenhits+=bool(ed)
  controls=read(D+'rank_controls.json');need(len(controls['span'])==64 and len(controls['block_bound'])==512,'rank control populations')
  for mask,got,size in controls['span']:
   rows=[maskvec(mask,3),maskvec(mask//8,3)];span={tuple(sum(b[i]*rows[i][j]for i in range(2))%2 for j in range(3))for b in product(range(2),repeat=2)};need(got==rank(rows)and size==len(span)==2**got,'direct64 span ranks')
  for idx,rec in enumerate(controls['block_bound']):
   bm,em=divmod(idx,64);BB=sym(3,bm);E=[maskvec(em//(4**i),2)for i in range(3)];r=rank(BB);s=rank([b+e for b,e in zip(BB,E)]);rs=[rank(block(BB,E,sym(2,k)))for k in range(2)];need(rec==[bm,em,r,s,2*s-r,rs]and min(rs)==2*s-r,'complete512 alternating block cases')
  general_cases=0
  for bm,em,dm in product(range(64),range(64),range(8)):
   BB=sym(3,bm,True);E=[maskvec(em//(4**i),2)for i in range(3)];need(rank(block(BB,E,sym(2,dm,True)))>=2*rank([b+e for b,e in zip(BB,E)])-rank(BB),'full symmetric block bound control');general_cases+=1
  generic=read(D+'generic_even_degree_counterexample.json');F,H=generic['F'],generic['H'];expected=check_conditions(generic['conditions'],F,H);ds=[k for k in range(64)if modproduct(F,sym(4,k))==H];need(ds==generic['all_alternating_D_masks']and expected['alternating_solution']and not expected['even_degree_alternating_solution']and direct_completion(F,H)and not direct_completion(F,H,True),'genuine generic separation')
  negatives=read(D+'negative_controls.json')
  for rec in negatives['incompatible_F_H']:need(not conditions(rec['F'],rec['H'])[0][rec['failed']],'saved generic incompatibility')
  fixture=read(B+'srg243_residual_fixture/triangle_blocks.json');A=read(B+'srg243_residual_fixture/adjacency243.json')['adjacency'];ra=graph(A,22);C,F,res=fixture['cubic_core60'],fixture['factor60x180'],fixture['residual180x180'];BB=triangle(C);need(BB==fixture['core_adjacency63'],'literal fixture core');order=fixture['canonical_order_original_vertex_ids'];need(sorted(order)==list(range(243))and block(BB,[[0]*180 for _ in range(3)]+F,res)==[[A[i][j]for j in order]for i in order],'literal243 graph relabelling');sd=read(D+'srg243.json');diagnostic,H=factor(C,F,sd['factor']);need(ra==110 and sd['graph']==dict(ordered_integer_entries=59049,binary_rank=110,vertices=243,degree=22),'exact positive graph result');need(alt(res)and all(sum(r)%2==0 for r in res)and modproduct(F,res)==H and diagnostic['integer_Gram_mismatch_count']==0,'actual nonempty even alternating residual')
  need(summ['genuine243']==dict(rank_A=110,rank_B=diagnostic['rank_B'],rank_B_E=diagnostic['rank_B_E'],completion_lower_bound=diagnostic['completion_rank_lower_bound'],rank_F=diagnostic['rank_F']),'genuine summary ranks')
  cores=read(D+'core_diagnostics.json');need(len(cores)==70 and len(summ['core_ranks'])==70,'exact saved70 core population');rng=random.Random(20260930);core_results=[]
  for idx,rec in enumerate(cores):
   CC=rec['C'];bb,vectors=core(CC);need(bb==rec['B']and rec['n']==12,'literal saved core/B');rc=check_cert(CC,rec['C_rank_certificate']);rb=check_cert(bb,rec['B_rank_certificate']);need(rec['local_cap']==cap(bb)and rec['three_common_kernel_candidates']==[sum(x*2**j for j,x in enumerate(v))for v in vectors],'raw local caps/kernels');need(rec['G_commutes_C']and rec['G_times_I_plus_C_alternating']and rec['bound_ceiling_if_F_even_cell_sums']==72-rb and rec['conditional_rank54_test_vacuous']==(rb>=18),'conditional core claims')
   if idx<4:need(CC==read(B+f'connected_identity_cores/core_{idx:02d}.json')['core_adjacency'],'saved connected core')
   elif idx==4:need(CC==read(B+'hadamard20_support/six_prism.json')['core_adjacency'],'saved sixprism core')
   elif idx==5:need(CC==make_core([[j^1 for j in range(12)]]*3,[j^1 for j in range(12)])and not rec['local_cap']['passes'],'invalid sixK33 not admissible')
   else:
    mm=[]
    for _ in range(3):
     items=list(range(12));rng.shuffle(items);m=[0]*12
     for j in range(0,12,2):m[items[j]]=items[j+1];m[items[j+1]]=items[j]
     mm.append(m)
    p=list(range(12));rng.shuffle(p);need(rec['matchings']==mm and rec['P']==p and CC==make_core(mm,p),'saved deterministic sample identities')
   result=dict(label=rec['label'],rank_B=rb,rank_C=rc,local_caps_pass=rec['local_cap']['passes'],rank54_bound_automatically_passes_if_factor=rb>=18);need(result==summ['core_ranks'][idx],'all70 measured ranks');core_results.append(result)
  local=read(D+'local_nonfactor_diagnostics.json');need(len(local)==2,'two nonfactor records');nonfactor=[]
  for rec in local:
   inp=read(rec['input_path']);actual,_=factor(inp['core_adjacency'],inp['factor'],rec);need(actual['integer_Gram_mismatch_count']>0 and rec['full_factor_claimed']is False,'saved annealer not full factor');nonfactor.append(actual)
  rejected=[]
  def reject(name,fn):
   try:fn()
   except(ValueError,KeyError,TypeError,IndexError):rejected.append(name)
   else:raise ValueError('accepted corruption '+name)
  reject('nonbinary_F',lambda:conditions([[2,0]],[[0,0]]));reject('dimension_mismatch',lambda:conditions([[1,0]],[[0]]));reject('false_kernel_condition',lambda:need(conditions([[0,0]],[[1,0]])[0]['alternating_solution'],'bad kernel'));reject('diagonal_prescription',lambda:need(conditions([[1,0]],[[1,0]])[0]['alternating_solution'],'bad diagonal'));reject('asymmetric_prescription',lambda:need(conditions([[1,0],[0,1]],[[0,1],[0,0]])[0]['alternating_solution'],'bad symmetry'));reject('even_degree_counterexample',lambda:need(expected['even_degree_alternating_solution'],'bad even degree'))
  for field in ['rank','kernel_basis','reduced_rows']:
   bad=copy.deepcopy(cores[0]['B_rank_certificate'])
   if field=='rank':bad[field]+=1
   else:bad[field][0]^=1
   reject('certificate_'+field,lambda bad=bad:check_cert(cores[0]['B'],bad))
  bad=copy.deepcopy(A);bad[0][1]^=1;reject('changed_genuine_graph',lambda:graph(bad,22));badF=copy.deepcopy(F);badF[0][0]^=1;reject('changed_genuine_factor',lambda:factor(C,badF,sd['factor']))
  save(out/'controls.json',dict(F_H_cases=4096,alternating_satisfiable=hits,even_degree_satisfiable=evenhits,independent_unknown_D_systems=8192,saved_rank_span_cases=64,saved_alternating_B_E_cases=512,saved_D_completions=1024,additional_general_symmetric_block_cases=general_cases,genuine243_integer_entries=59049,corruptions_rejected=rejected,scope='Finite controls only; universal statements are separately proved in written audit.'))
  save(out/'independent_diagnostics.json',dict(genuine243=diagnostic,cores=core_results,nonfactor_objects=nonfactor,random_sample_count=64,random_generator_shared_for_label_replay_only=True,universal_rank_B_lower_bound_claimed=False))
  for p in [Path(__file__).relative_to(ROOT).as_posix(),'docs/AUDIT_20260930_GF2_ALTERNATING_COMPLETION.md']:pins[p]=sha(ROOT/p)
  stamp=datetime.now(timezone.utc).isoformat();shared=['Raw frozen matrices, prior reports and standard-library arithmetic only; no producer/checker code imports.','List-coordinate reverse-pivot elimination/direct unknown-D systems versus producer integer-bitset elimination.','Python random.Random and its saved seed are shared solely to authenticate the64 diagnostic labels.'];limits=['No quadratic residual or idempotent completion inferred.','No universal rank(B)>=18 or new target exclusion.','The genuine243 graph is a positive fixture in different parameters.','Two saved annealer objects fail integer Gram; finite core measurements do not prove coverage.','Archive overlap retained; no novelty assertion.']
  claims=[dict(id='C-GF2-ALTERNATING-MIXED-COMPLETION-CRITERION',revision=1,kind='mathematical result',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',statement='For arbitrary GF2 matrices F,H of equal shape, an alternating D satisfying FD=H exists exactly when ker(F^T) is contained in ker(H^T) and FH^T is alternating. Requiring D1=0 adds exactly H1=0 and H^T x=0 whenever F^T x=1 is solvable. For genuine even-cell cubic triangle factors with the stated integer Gram identity, FH^T is automatically alternating, so only the kernel condition remains for alternating completion.',scope='Exact linear binary mixed equation and explicitly conditional triangle specialization; no quadratic residual or graph completion.',dependencies=[dict(id='C-TRIANGLE-FACTOR-RESIDUAL60-COMPLETION-EQUIVALENCE',revision=1,relation='premise')]),dict(id='C-SYMMETRIC-BLOCK-RANK-COMPLETION-BOUND',revision=1,kind='mathematical result',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',statement='Over any field, symmetric block completions A=[[B,E],[E^T,D]] obey rank(A)>=2rank([B,E])-rank(B). For even n triangle factors with even cell-column sums, rank([B,E])<=3n. Consequently, for n12 and the prior target binary rank54, this lower-bound test is automatically satisfied conditional on rank(B)>=18; that rank premise is not asserted universally.',scope='General algebraic rank inequality and conditional target consequence; finite diagnostics only for the saved matrices.',dependencies=[dict(id='C-TARGET-MODULAR-RANKS',revision=1,relation='premise')])]
  for c in claims:c.update(verifier='/root/eight_domain_audit',producer='/root/state_literature_audit',checking_method='Independent written proof plus complete finite controls and literal raw-matrix replay.',shared_components=shared,limitations=limits,created_at=stamp,updated_at=stamp,inputs_sha256=pins,outputs_sha256={p.relative_to(ROOT).as_posix():sha(p)for p in out.iterdir()if p.is_file()})
  save(out/'claim_bindings.json',dict(claims=claims));need(time.monotonic()-start<120,'bounded120second audit');summary=dict(status='INDEPENDENT_GF2_ALTERNATING_COMPLETION_AND_BLOCK_RANK_PASS',timestamp=stamp,command=[sys.executable,*sys.argv],python=platform.python_version(),inputs_sha256=pins,outputs_sha256={p.relative_to(ROOT).as_posix():sha(p)for p in out.iterdir()if p.is_file()},claims=[dict(id=c['id'],revision=1)for c in claims],genuine243_rank_A=110,exact_completion_pairs=4096,direct_D_systems=8192,saved_core_diagnostics=70,nonfactor_objects=2,shared_components=shared,limitations=limits,native_calls=0,target_resolution='UNKNOWN',elapsed_seconds=time.monotonic()-start);save(out/'summary.json',summary);print(json.dumps(dict(status=summary['status'],summary_sha256=sha(out/'summary.json'),bindings_sha256=sha(out/'claim_bindings.json'),elapsed_seconds=summary['elapsed_seconds'])))
 except BaseException as e:save(out/'failure.json',dict(error=repr(e),source_sha256=sha(Path(__file__)),inputs_sha256=pins,elapsed_seconds=time.monotonic()-start));raise
if __name__=='__main__':main()
