"""Independent triangle-image collision/character proof and complete tiny artifacts."""
import argparse,copy,hashlib,itertools,json,math,platform,subprocess,sys,time
from collections import Counter,defaultdict
from datetime import datetime,timezone
from fractions import Fraction
from pathlib import Path
from command_deadline import CommandDeadline
ROOT=Path(__file__).resolve().parents[1]
RAW='acceleration/results/20261003_incidence_low_weight_controls01/'
NOTE='docs/CANDIDATE_20261003_TRIANGLE_INCIDENCE_LOW_WEIGHTS_V1.md'
PROOF='acceleration/audit_20261003_incidence_low_weights_v1_proof.md'
PINS={NOTE:'ee6baa598f50bbad32c6dd9e51c77729202ffca6597f0bb35eca2d1ed5f122cd',
 'acceleration/theory_20261003_incidence_low_weight_controls_v1.py':'bdea6f2c7ab312f9ab803e7cc2622d27cbec5e0b463610ff57a378ed6711ebfd'}
class AuditError(ValueError):
 def __init__(self,stage):self.stage=stage;super().__init__(stage)
def need(ok,stage):
 if not ok:raise AuditError(stage)
def sha(p):
 with p.open('rb') as s:return hashlib.file_digest(s,'sha256').hexdigest()
def save(p,data):
 with p.open('x',encoding='utf8',newline='\n') as s:json.dump(data,s,indent=2,sort_keys=True);s.write('\n')
def unique(items):
 d={}
 for k,v in items:need(k not in d,'DUPLICATE_KEY');d[k]=v
 return d
def load(p):return json.loads(p.read_text(encoding='utf8'),object_pairs_hook=unique)
def adjacency(n,edges):return [[int(tuple(sorted((u,v))) in edges) for v in range(n)] for u in range(n)]
def from_lines(n,lines):return adjacency(n,{tuple(sorted(pair)) for t in lines for pair in itertools.combinations(t,2)})
def validate(g):
 n=len(g);need(type(g) is list and all(type(r) is list and len(r)==n and all(type(x) is int and x in (0,1) for x in r) for r in g),'GRAPH_DOMAIN')
 need(all(g[u][u]==0 and all(g[u][v]==g[v][u] for v in range(n)) for u in range(n)),'SIMPLE_GRAPH')
 sets=[{v for v in range(n) if g[u][v]} for u in range(n)]
 need(all(len(sets[u]&sets[v])==1 for u,v in itertools.combinations(range(n),2) if g[u][v]),'EDGE_UNIQUE_TRIANGLE');return sets
def polynomial(n,w):
 c=[1]
 for i in range(n):
  sign=-1 if i<w else 1;d=[0]*(len(c)+1)
  for j,x in enumerate(c):d[j]+=x;d[j+1]+=sign*x
  c=d
 return c
def encode(s):return sum(2**v for v in s)
def check_fixture(g):
 sets=validate(g);n=len(g);triangles=[list(t) for t in itertools.combinations(range(n),3) if all(v in sets[u] for u,v in itertools.combinations(t,2))];T=[frozenset(t) for t in triangles]
 groups={4:defaultdict(list),6:defaultdict(list)};pairs=[]
 for i,j in itertools.combinations(range(len(T)),2):
  meet=T[i]&T[j];support=T[i]^T[j];weight=len(support);need(weight in (4,6),'PAIR_WEIGHT');S=sorted(support)
  if meet:
   edges=[list(p) for p in itertools.combinations(S,2) if p[1] in sets[p[0]]];need(len(edges)==2 and set(edges[0]).isdisjoint(edges[1]),'SUPPORT_2K2')
   centers=[sets[u]&sets[v] for u,v in edges];need(centers==[meet,meet],'RECOVERY_CENTER');recovered=sorted(sorted(set(e)|meet) for e in edges)
  else:
   recovered=[t for t in triangles if set(t)<=support];need(len(recovered)==2,'DISJOINT_RECOVERY')
  need(recovered==[triangles[i],triangles[j]],'PAIR_INVERSE');word=encode(support);groups[weight][word].append([i,j]);pairs.append(dict(pair=[i,j],intersection=sorted(meet),support=S,word=word,weight=weight,recovered_triangles=recovered))
 need(all(len(v)==1 for group in groups.values() for v in group.values()),'PAIR_COLLISION')
 triangle_degrees=[sum(v in t for t in T) for v in range(n)];counts={3:len(T),4:sum(t*(t-1)//2 for t in triangle_degrees),6:len(T)*(len(T)-1)//2-sum(t*(t-1)//2 for t in triangle_degrees)}
 need(len(groups[4])==counts[4] and len(groups[6])==counts[6],'PAIR_COUNT')
 ambient=[frozenset(s) for j in range(n+1) for s in itertools.combinations(range(n),j)]
 span={frozenset()}
 for t in T:span=span|{s^t for s in span}
 C=[s for s in ambient if all(len(s&t)%2==0 for t in T)];D={u for u in ambient if all(len(u&s)%2==0 for s in C)}
 need(D==span and len(C)*len(D)==2**n,'ORTHOGONAL_IDENTITY')
 K={w:polynomial(n,w) for w in range(n+1)}
 for w in range(n+1):
  witness=frozenset(range(w))
  for j in range(n+1):need(K[w][j]==sum((-1)**len(u&witness) for u in ambient if len(u)==j),'POLYNOMIAL_LITERAL_CHARACTERS')
 inequalities=[];M=len(C)
 for j in range(n+1):
  full=sum(K[len(x)][j] for x in C);actual=sum(len(u)==j for u in D);N=counts.get(j,0);k0=K[0][j]
  need(full==M*actual,'CHARACTER_IDENTITY');need(actual>=N,'LOWER_WEIGHT_COUNT')
  nonzero=full-k0;sharp=N*M-k0;shift=sum(N-K[len(x)][j] for x in C if x)
  need(nonzero>=sharp and shift<=k0-N,'SHARP_CONSTANT')
  inequalities.append(dict(degree=j,dual_count=actual,lower_count=N,k_zero=k0,full_sum=full,nonzero_sum=nonzero,sharp_rhs=sharp,shifted_lhs=shift,shifted_rhs=k0-N))
 return dict(triangles=triangles,triangle_degrees=triangle_degrees,lower_counts={str(k):v for k,v in counts.items()},pair_records=pairs,image_words=sorted(encode(s) for s in D),kernel_words=sorted(encode(s) for s in C),image_weight_histogram={str(k):v for k,v in sorted(Counter(map(len,D)).items())},kernel_weight_histogram={str(k):v for k,v in sorted(Counter(map(len,C)).items())},character_inequalities=inequalities,complete_literal_character_checks=(n+1)**2)
def reject(records,label,stage,fn):
 try:fn()
 except AuditError as e:need(e.stage==stage,'CONTROL_WRONG_STAGE');records.append(dict(label=label,expected=stage,outcome=stage));return
 raise AuditError('CONTROL_ACCEPTED')
def equal_fixture(raw,actual):need(all(raw.get(k)==v for k,v in actual.items()),'COMPLETE_RAW_FIXTURE_EQUALITY')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--producer-summary-sha256',required=True);args=ap.parse_args();start=time.monotonic();deadline=CommandDeadline(args.seconds,allocation_reason='Independent complete five tiny raw graph/code/character fixtures, collision countercontrols and written universal proof; no optimizer')
 out=args.out.resolve();need(out.is_relative_to(ROOT),'BOUNDED_OUTPUT');out.mkdir(parents=True,exist_ok=False);pins={};controls=[]
 def pin(p,h=None):
  need(deadline.status()['remaining_seconds']>20,'NOT_COMPLETED_WITHIN_ALLOCATED_BUDGET');actual=sha(ROOT/p);need(h is None or actual==h,'INPUT_HASH');pins[p]=actual
 try:
  for p in [Path(__file__).relative_to(ROOT).as_posix(),PROOF,'acceleration/audit_20261003_incidence_low_weights_v1_spec.md','acceleration/command_deadline.py','acceleration/run_compute_command.py','uv.lock','pyproject.toml']:pin(p)
  for p,h in PINS.items():pin(p,h)
  rook=adjacency(9,{(u,v) for u,v in itertools.combinations(range(9),2) if u//3==v//3 or u%3==v%3});good=check_fixture(rook)
  need(all(sum(row)==4 for row in rook) and all(sum(rook[u][k]*rook[v][k] for k in range(9))==(4 if u==v else 1 if rook[u][v] else 2) for u in range(9) for v in range(9)),'ROOK_SRG_IDENTITY')
  for label,stage,mutate in [('diagonal','SIMPLE_GRAPH',lambda g:g[0].__setitem__(0,1)),('asymmetry','SIMPLE_GRAPH',lambda g:g[0].__setitem__(1,0)),('bool','GRAPH_DOMAIN',lambda g:g[0].__setitem__(1,True)),('nonbinary','GRAPH_DOMAIN',lambda g:g[0].__setitem__(1,2))]:
   damaged=copy.deepcopy(rook);mutate(damaged);reject(controls,label,stage,lambda damaged=damaged:validate(damaged))
  one=check_fixture(from_lines(3,[[0,1,2]]));j3=one['character_inequalities'][3]
  reject(controls,'omitted_A0_constant','OMITTED_A0_CONSTANT',lambda:need(j3['nonzero_sum']>=len(one['kernel_words']),'OMITTED_A0_CONSTANT'))
  reject(controls,'overstated_dual_count','OVERSTATED_DUAL_COUNT',lambda:need(j3['full_sum']>=len(one['kernel_words'])*(j3['dual_count']+1),'OVERSTATED_DUAL_COUNT'))
  corrupt=copy.deepcopy(good);corrupt['pair_records'][0]['support'][0]=8;reject(controls,'wrong_raw_pair_support','COMPLETE_RAW_FIXTURE_EQUALITY',lambda:equal_fixture(corrupt,good))
  corrupt=copy.deepcopy(good);corrupt['character_inequalities'][3]['shifted_rhs']+=1;reject(controls,'wrong_raw_shifted_constant','COMPLETE_RAW_FIXTURE_EQUALITY',lambda:equal_fixture(corrupt,good))
  fixtures=[('triangle3',from_lines(3,[[0,1,2]])),('two_disjoint_triangles6',from_lines(6,[[0,1,2],[3,4,5]])),('friendship7',from_lines(7,[[0,1,2],[0,3,4],[0,5,6]])),('loose_cycle8',from_lines(8,[[0,1,2],[2,3,4],[4,5,6],[0,6,7]])),('rook9',rook)]
  pin(RAW+'summary.json',args.producer_summary_sha256);production=load(ROOT/(RAW+'summary.json'))
  for p,h in {**production['inputs_sha256'],**production['outputs_sha256']}.items():pin(p,h)
  sup='acceleration/results/20261003_incidence_low_weight_controls_supervision01/summary.json';pin(sup);terminal=load(ROOT/sup);need(terminal['command_exit_code']==0 and terminal['cleanup']['reaped'] is True and terminal['cleanup']['job_active_zero_observed'] is True,'PRODUCER_TERMINAL')
  checked=[]
  for label,g in fixtures:
   raw=load(ROOT/(RAW+label+'.json'));need(raw['label']==label and raw['adjacency']==g,'KNOWN_FIXTURE_BYTES');actual=check_fixture(g)
   equal_fixture(raw,actual);checked.append(dict(label=label,vertices=len(g),triangles=len(actual['triangles']),pair_checks=len(actual['pair_records']),image_words=len(actual['image_words']),kernel_words=len(actual['kernel_words']),literal_character_checks=actual['complete_literal_character_checks']))
  pasch=load(ROOT/(RAW+'pasch_hypothesis_countercontrol.json'));T=[frozenset(t) for t in pasch['triples']];groups=defaultdict(list)
  need(pasch['n']==6 and len(T)==4 and all(len(t)==3 and t<=set(range(6)) for t in T) and pasch['adjacency']==from_lines(6,pasch['triples']),'PASCH_SOURCE_POINT_GRAPH')
  for i,j in itertools.combinations(range(4),2):need(len(T[i]&T[j])==1,'PASCH_LINEARITY');groups[T[i]^T[j]].append([i,j])
  need(len(groups)==3 and all(len(s)==4 and len(v)==2 for s,v in groups.items()),'PASCH_COLLISIONS')
  need(pasch['collisions']==[dict(word=encode(s),support=sorted(s),weight=len(s),pairs=groups[s]) for s in sorted(groups,key=encode)],'PASCH_RAW_COLLISION_RECORDS');reject(controls,'linear_Pasch_hypothesis','EDGE_UNIQUE_TRIANGLE',lambda:validate(pasch['adjacency']))
  k6=load(ROOT/(RAW+'complete6_hypothesis_countercontrol.json'));complete=adjacency(6,set(itertools.combinations(range(6),2)));need(k6['adjacency']==complete,'K6_LITERAL_BYTES');ts=[frozenset(t) for t in itertools.combinations(range(6),3)];disjoint=[(i,j) for i,j in itertools.combinations(range(20),2) if not(ts[i]&ts[j])]
  need(len(disjoint)==10 and all(ts[i]^ts[j]==frozenset(range(6)) for i,j in disjoint),'K6_DISJOINT_COLLISIONS')
  need(k6['triangles']==[sorted(t) for t in ts] and k6['disjoint_collisions']==[dict(word=63,support=list(range(6)),weight=6,pairs=[list(p) for p in disjoint])],'K6_RAW_COLLISION_RECORDS');reject(controls,'K6_hypothesis','EDGE_UNIQUE_TRIANGLE',lambda:validate(complete))
  m=99*14//6;Q=99*(7*6//2);counts={'3':m,'4':Q,'6':m*(m-1)//2-Q};need(counts=={'3':231,'4':2079,'6':24486},'EXACT_TARGET_LOWER_COUNTS')
  K={w:polynomial(99,w) for w in range(100)};normalized={}
  for j in (3,4,6):
   N=counts[str(j)];denom=K[0][j]-N;need(denom>0,'NORMALIZED_POSITIVE_DENOMINATOR');coefs={}
   for w in range(1,100):q=Fraction(N-K[w][j],denom);coefs[str(w)]=[q.numerator,q.denominator]
   normalized[str(j)]={'denominator':denom,'lower_word_count':N,'coefficient_by_weight':coefs}
  save(out/'controls.json',controls);save(out/'checked_fixtures.json',checked);save(out/'normalized_rows.json',normalized)
  statement='For every finite simple graph in which every edge has exactly one common neighbor, its complete triangle-incidence image over GF(2) contains at least m weight3 words, sum_v binom(t_v,2) weight4 words, and binom(m,2)-sum_v binom(t_v,2) weight6 words. Consequently any graph satisfying the exact target identity has lower counts231,2079,24486 respectively, and its kernel weight enumerator satisfies the stated sharp shifted character inequalities; these are conditional necessary bounds, not existence or nonexistence.'
  report=dict(status='INDEPENDENT_TRIANGLE_IMAGE_LOW_WEIGHT_COUNTS_CHARACTER_V1_PASS',timestamp=datetime.now(timezone.utc).isoformat(),statement=statement,producer='/root/structural',verifier='/root/checkpoint_audit',method='independent_derivation',universal_derivation_checked=True,written_audit=PROOF,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,target_lower_word_counts=counts,normalized_rows=normalized,positive_fixtures=checked,strict_negative_controls=len(controls),character_constant_convention='sum_w>0 A_w*K_j(w) >= N_j*M-K_j(0); equivalently sum_w>0 A_w*(N_j-K_j(w)) <= K_j(0)-N_j',prior_weight_interval_rederived=False,prior_weight_interval_context='65d8eea3f4d72eb56391284f95eb43ad021e92a88a41fdcc2fe7a2e10f9dd92d supplies separate36..60 premise; not required for this all-weight inequality.',target_resolution='NONE',new_exclusions=0,rank_bound_claimed=False,mathematical_scope='Universal written implication under edge-unique-triangle hypothesis; all finite raw controls independently checked but not substituted for proof.',shared_components=['Python exact integers/Fraction/JSON/SHA256 and supported deadline/supervisor.','Original raw small graph/control artifacts; checking uses independently constructed adjacency sets, support symmetric differences, exhaustive ambient orthogonal words and repeated polynomial multiplication.','Rank-nullity/character convention as exact written mathematics; no producer code imported.'],limitations=['Pair-generated words are lower bounds, not full target low-weight enumerators.','Arbitrary linear hypergraphs insufficient; Pasch/K6 hypothesis failures explicitly retained.','No novelty, external review, target graph, rank consequence, optimization or target-wide coverage.'],elapsed_seconds=time.monotonic()-start,deadline=deadline.status());save(out/'summary.json',report);print(json.dumps({'status':report['status'],'sha256':sha(out/'summary.json'),'strict_controls':len(controls)}))
 except BaseException as error:save(out/'failure.json',{'timestamp':datetime.now(timezone.utc).isoformat(),'error':repr(error),'stage':getattr(error,'stage',None),'inputs_sha256':pins,'outputs_preserved':True});raise
if __name__=='__main__':main()
