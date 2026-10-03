"""Produce a raw start from TWO checked finite censuses; never self-approve."""
import argparse
from collections import Counter
import copy
from datetime import datetime, timezone
import gzip
import hashlib
import importlib.metadata
import itertools
import json
from pathlib import Path
import platform
import sys
from tqdm import tqdm
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SELF = 'acceleration/export_20261003_root_focused_start_v2.py'
SPEC = 'acceleration/export_20261003_root_focused_start_v2_spec.md'
COMMIT = 'e1691ed8cdab8e21b9038497c6ba109de7f781c8'
SOFTWARE = {
 'acceleration/command_deadline.py':'9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9',
 'acceleration/run_compute_command.py':'593a9feed6250739dc9672338df23ab171fc9a6a6db4196c1feb312efa33957a',
 'pyproject.toml':'273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339',
 'uv.lock':'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',
 'acceleration/export_20261003_root_focused_start_v1.py':'b4d0a5712ce7f07696bbbd2511583873550dd416c4516861b6fdc6febb14a3b6',
 'acceleration/export_20261003_root_focused_start_v1_spec.md':'152b2f243de3376a9906aa9448bc05612965e840ffffa0eb100cf12881d3cc8c',
 'acceleration/results/20261003_root_focused_start_controls01/summary.json':'1865eface3478a12fb7abb32798042abb4fdf83219e8011715ba9442cd93880b',
}
CENSUSES = [dict(label='original',eligible=187,
 manifest='acceleration/results/20261003_weight60_two_line_census01/manifest.json',
 manifest_sha='70f4ec893d5ba443effdd29cd6e3d472d736e590af56691b751e822bbae49ffa',
 review='acceleration/results/20261003_independent_review/two_line_full01/summary.json',
 review_sha='1d3cecc2fd8d3e689966a334af59a9af7d0a2e8c66b356b98484aef3ed79e589',
 review_status='INDEPENDENT_TWO_LINE_COMPLETE_FIXED_GRAPH_CENSUS_V2_PASS',
 minimum='acceleration/results/20261003_independent_review/two_line_full01/all_lambda_preserving_minimum_root_ties.json',
 minimum_sha='e70dea272951477c892c575f6185ee52b0fc2f6c8df392a4dc3514ee5e887341',
 triples='acceleration/results/20261003_hypergraph_weight60_warm01/native/final.state',
 triples_sha='c15b421468af173b6c2ee11e9bcb31d5abca586fcb47a7c7ee312f527b31979b',
 matrix='acceleration/results/20261003_hypergraph_weight60_warm01/native/best.adj',
 matrix_sha='9d5b88ba2a2eb13d39d2a5edea1c25af9a9105c143c4297fe37e84f666a37a2d'),
 dict(label='neighbor',eligible=186,
 manifest='acceleration/results/20261003_weight60_two_line_neighbor_census01/manifest.json',
 manifest_sha='15874e9fa9b2f83f9e811ca4efa3e7892fa81e0ebf026778d545466724720480',
 review='acceleration/results/20261003_independent_review/two_line_neighbor_full01/summary.json',
 review_sha='24c20b8454ba2ac16501e3d7ae49dadf922b1870d6ed72706e9ce8349d4a26e0',
 review_status='INDEPENDENT_TWO_LINE_COMPLETE_NEUTRAL_GRAPH_CENSUS_V3_PASS',
 minimum='acceleration/results/20261003_independent_review/two_line_neighbor_full01/all_lambda_preserving_minimum_root_ties.json',
 minimum_sha='a7561a9d57a3b4f066c28d3a76fe88b08c8d4ac6d4a6cd98999d11d2f211e662',
 triples='acceleration/results/20261003_weight60_two_line_census01/best_neighbor_triples.json',
 triples_sha='11074c406a0b6902e7dcccdd50f1a2e36104a6b964948b3f3fd5299ecdce2968',
 matrix='acceleration/results/20261003_weight60_two_line_census01/best_neighbor.adj',
 matrix_sha='02d66dc7fb84f91b29be399abe760b452f85b6d79c6c37c681e566e6f4c809bd')]
OLD = dict(matrix='acceleration/results/20261003_hypergraph_weight60_warm01/native/first_lambda0.adj',
 matrix_sha='818314b75fccfa0f3fe702602afb02b6415f3138a770ef15ed0621d189d88836',
 review='acceleration/results/20261003_independent_review/weight60_warm_roots_dense01/summary.json',
 review_sha='becf048cbb32ec577a78c7084fc949103af91f66c92c5936137a9740c5cdd35a')
CATEGORIES = {'invalid_selection','invalid_linearity','valid_lambda_changed',
 'valid_lambda_preserving_mu_down','valid_lambda_preserving_mu_equal','valid_lambda_preserving_mu_up'}

class ExportError(ValueError):
 def __init__(self,stage,message): self.stage=stage; super().__init__(stage+': '+message)
def need(ok,stage,message):
 if not ok: raise ExportError(stage,message)
def sha(path):
 with path.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
def digest(raw): return hashlib.sha256(raw).hexdigest()
def canonical(v): return (json.dumps(v,sort_keys=True,separators=(',',':'))+'\n').encode()
def unique_keys(pairs):
 d={}
 for k,v in pairs:
  need(k not in d,'JSON_KEYS','duplicate key'); d[k]=v
 return d
def loads(raw): return json.loads(raw,object_pairs_hook=unique_keys)
def write(path,v):
 with path.open('x',encoding='utf8',newline='\n') as f: json.dump(v,f,indent=2);f.write('\n')
def authenticate(name,expected,pins):
 path=(ROOT/name).resolve();need(path.is_relative_to(ROOT) and path.is_file(),'INPUT_PATH','workspace input')
 actual=sha(path);need(expected is None or actual==expected,'INPUT_HASH','frozen '+name);pins[name]=actual
 return path
def clock_check(deadline):
 need(not deadline.status()['stop_required'] and deadline.status()['remaining_seconds']>20,'BUDGET','not completed within allocated budget')

def from_triples(n,degree,triples,root):
 need(type(n) is int and n>0 and type(degree) is int and degree>0 and type(root) is int and 0<=root<n,'DOMAIN','integer parameters')
 need(type(triples) is list and len(triples)*3==n*degree,'DOMAIN','exact triple cardinality')
 neighbors=[set() for _ in range(n)];incidence=[0]*n;seen=set()
 for t in triples:
  need(type(t) is list and len(t)==3 and all(type(v) is int and 0<=v<n for v in t) and len(set(t))==3,'DOMAIN','literal triple')
  key=tuple(sorted(t));need(key not in seen,'LINEARITY','duplicate triple');seen.add(key)
  for v in t:incidence[v]+=1
  for u,v in itertools.combinations(t,2):
   need(v not in neighbors[u],'LINEARITY','repeated pair');neighbors[u].add(v);neighbors[v].add(u)
 need(all(v==degree for v in incidence) and all(len(s)==2*degree for s in neighbors),'DEGREE','regular incidence')
 return from_neighbors(neighbors,root,degree)

def from_neighbors(neighbors,root,degree):
 n=len(neighbors);need(type(root) is int and 0<=root<n,'DOMAIN','root range')
 need(all(type(s) is set and all(type(v) is int and 0<=v<n for v in s) and i not in s and len(s)==2*degree for i,s in enumerate(neighbors)),'MATRIX','zero diagonal/degree/domain')
 need(all(i in neighbors[j] for i,s in enumerate(neighbors) for j in s),'MATRIX','symmetry')
 lam=mu=row=0;adj_hist=Counter();non_hist=Counter();outsiders=[]
 for i in range(n):
  for j in range(i+1,n):
   cn=len(neighbors[i].intersection(neighbors[j]))
   if j in neighbors[i]:lam+=(cn-1)**2
   else:mu+=(cn-2)**2
 for v in range(n):
  if v==root:continue
  support=sorted(neighbors[root].intersection(neighbors[v]));cn=len(support)
  if v in neighbors[root]:adj_hist[cn]+=1
  else:non_hist[cn]+=1;row+=(cn-2)**2;outsiders.append(dict(vertex=v,root_neighbors=support,common_neighbors=cn))
 matrix=(str(n)+'\n'+''.join(''.join('1' if j in s else '0' for j in range(n))+'\n' for s in neighbors)).encode()
 pair_occ=Counter(tuple(o['root_neighbors']) for o in outsiders if o['common_neighbors']==2)
 return dict(n=n,degree=degree,root=root,lambda_energy=lam,mu_energy=mu,root_residual=row,root_objective=60*lam+row,
  base_energy=lam+mu,matrix=matrix,matrix_sha256=digest(matrix),root_neighbors=sorted(neighbors[root]),
  adjacent_cn_histogram=dict(sorted(adj_hist.items())),nonadjacent_cn_histogram=dict(sorted(non_hist.items())),
  outsider_supports=outsiders,pair_support_multiplicities=[dict(pair=list(p),multiplicity=c) for p,c in sorted(pair_occ.items())],
  support_pair_uniqueness_assumed=False)

def read_matrix(raw,n,degree,root):
 lines=raw.decode('ascii').splitlines();need(len(lines)==n+1 and lines[0]==str(n),'MATRIX','header/dimensions')
 need(all(len(s)==n and set(s)<={'0','1'} for s in lines[1:]),'MATRIX','binary entries')
 return from_neighbors([{j for j,b in enumerate(s) if b=='1'} for s in lines[1:]],root,degree)
def state_current(raw):
 lines=raw.decode('ascii').splitlines();need(lines[0]=='HYPERGRAPH_WEIGHT60_ANNEAL_STATE_V2','STATE','pinned state schema')
 need(lines.count('n 99')==1 and lines.count('degree 7')==1 and lines.count('current 231')==1,'STATE','literal state fields')
 p=lines.index('current 231')+1;triples=[]
 for s in lines[p:p+231]:
  try:t=[int(v) for v in s.split()]
  except ValueError:raise ExportError('STATE','integer current triple')
  need(len(t)==3,'STATE','complete current triples');triples.append(t)
 return triples

def reconstruct(base,record):
 need(type(record.get('proposal_id')) is int and 0<=record['proposal_id']<len(base)*(len(base)-1)//2*9,'RECORD','proposal ID')
 pid=record['proposal_id'];pairs=list(itertools.combinations(range(len(base)),2));i,j=pairs[pid//9];ix,jy=divmod(pid%9,3)
 need(all(type(record.get(k)) is int and record[k]==v for k,v in [('i',i),('j',j),('ix',ix),('jy',jy)]),'RECORD','literal proposal decoding')
 need(record['old_triples']==[base[i],base[j]],'RECORD','source triples')
 x,y=base[i][ix],base[j][jy];need(x not in base[j] and y not in base[i],'RECORD','exclusive selection')
 a=list(base[i]);b=list(base[j]);a[ix]=y;b[jy]=x
 need(record['new_triples']==[a,b],'RECORD','literal swapped rows')
 result=[list(t) for t in base];result[i]=a;result[j]=b
 return result
def eligible(record):
 need(type(record.get('proposal_id')) is int and type(record.get('valid')) is bool and record.get('classification') in CATEGORIES,'RECORD','typed census record')
 need(record['valid']==record['classification'].startswith('valid_'),'RECORD','classification/validity')
 if record['valid']:
  need(all(type(record.get(k)) is int for k in ['delta_lambda','delta_mu','new_lambda','new_mu','new_root_residual','root_residual_delta']),'RECORD','integer energies')
  need((record['classification']=='valid_lambda_changed')==(record['delta_lambda']!=0),'RECORD','lambda classification')
  if record['delta_lambda']==0:
   sign='down' if record['delta_mu']<0 else 'up' if record['delta_mu']>0 else 'equal'
   need(record['classification']=='valid_lambda_preserving_mu_'+sign,'RECORD','mu classification')
   need(record['new_lambda']==0,'RECORD','zero lambda from checked zero baseline');return True
 return False
def key(v):
 need(all(type(v.get(k)) is int and v[k]>=0 for k in ['root_residual','mu_energy','proposal_id']),'SELECTION','integer key')
 h=v.get('input_adjacency_sha256');need(type(h) is str and len(h)==64 and all(c in '0123456789abcdef' for c in h),'SELECTION','input hash key')
 return v['root_residual'],v['mu_energy'],h,v['proposal_id']
def select(pool):
 need(type(pool) is list and pool,'SELECTION','nonempty eligible population')
 return min(pool,key=key)

def stream_part(part,path,start,deadline=None):
 need(all(type(part.get(k)) is int and part[k]>=0 for k in ['start','end','record_count','raw_bytes','gzip_bytes']),'PART_SEQUENCE','integer part descriptor')
 need(part['start']==start and part['end']==start+part['record_count'] and part['record_count']>0,'PART_SEQUENCE','contiguous part')
 need(path.stat().st_size==part['gzip_bytes'] and sha(path)==part['gzip_sha256'],'PART_HASH','compressed identity')
 raw_hash=hashlib.sha256();raw_size=0;count=0
 with gzip.open(path,'rb') as f:
  while True:
   line=f.readline(4097)
   if not line:break
   need(len(line)<=4096 and line.endswith(b'\n'),'PART_FORMAT','complete bounded record')
   record=loads(line);need(canonical(record)==line,'PART_FORMAT','literal canonical record')
   need(type(record.get('proposal_id')) is int and record['proposal_id']==start+count,'PART_SEQUENCE','all ordered labels')
   raw_size+=len(line);raw_hash.update(line);count+=1
   need(count<=part['record_count'] and raw_size<=part['raw_bytes'],'PART_HASH','decompression bounds')
   if deadline is not None and count%1000==0:clock_check(deadline)
   yield record,line
 need(count==part['record_count'] and raw_size==part['raw_bytes'] and raw_hash.hexdigest()==part['raw_sha256'],'PART_HASH','complete raw identity')

def native_bytes(n,degree,root,triples,matrix_sha,triples_sha,selection_sha):
 text='ROOT_FOCUSED_GRAPH_INPUT_V1\n'+f'n {n}\ndegree {degree}\nroot {root}\nsource_matrix_sha256 {matrix_sha}\nsource_triples_sha256 {triples_sha}\nselection_report_sha256 {selection_sha}\ntriples {len(triples)}\n'
 text+=''.join(' '.join(map(str,t))+'\n' for t in triples)+'END\n';return text.encode()
def public_score(score):return {k:v for k,v in score.items() if k!='matrix'}

def receipt_scope(c,m,r):
 need(r['status']==c['review_status'] and type(r['complete_proposals_checked']) is int and r['complete_proposals_checked']==239085 and type(r['frozen_labelled_proposals']) is int and r['frozen_labelled_proposals']==239085 and r['complete_universe'] is True and r['verifier']=='/root' and r['target_resolution']=='NONE','AUDIT','exact complete independent finite review')
 need(type(m['population']) is int and m['population']==239085 and type(m['completed_proposals']) is int and m['completed_proposals']==239085 and m['budget_stop'] is False and m['independent_approval'] is False and m['target_resolution'] is False,'AUDIT','completed candidate manifest')
 need(all(type(m['identity'][k]) is int and m['identity'][k]==v for k,v in [('n',99),('degree',7),('root',11),('total',239085)]) and m['identity']['source_commit']==COMMIT,'AUDIT','target finite scope')

def controls(out,deadline):
 results=[]
 def good(name,fn):clock_check(deadline);fn();results.append(dict(name=name,outcome='PASS',expectation='positive'))
 def bad(name,stage,fn):
  clock_check(deadline)
  try:fn()
  except ExportError as e:need(e.stage==stage,'CONTROL','exact rejection '+name);results.append(dict(name=name,outcome='PASS',expectation=stage));return
  raise ExportError('CONTROL','accepted corruption '+name)
 rook=[[3*r+c for c in range(3)] for r in range(3)]+[[3*r+c for r in range(3)] for c in range(3)]
 score=from_triples(9,2,rook,0)
 good('known rook9 exact zero',lambda:need((score['lambda_energy'],score['mu_energy'],score['root_residual'])==(0,0,0),'CONTROL','rook SRG'))
 good('raw matrix roundtrip',lambda:need(read_matrix(score['matrix'],9,2,0)['matrix']==score['matrix'],'CONTROL','matrix roundtrip'))
 lines=[[0,1,2],[3,4,5]];s=from_triples(6,1,lines,0)
 good('two disjoint triples exact arithmetic',lambda:need((s['lambda_energy'],s['mu_energy'],s['root_residual'])==(0,36,12),'CONTROL','K3 union scores'))
 rec=dict(proposal_id=0,i=0,j=1,ix=0,jy=0,old_triples=copy.deepcopy(lines),new_triples=[[3,1,2],[0,4,5]],valid=True,
  delta_lambda=0,delta_mu=0,new_lambda=0,new_mu=36,new_root_residual=12,root_residual_delta=0,classification='valid_lambda_preserving_mu_equal')
 good('literal swapped ordered rows',lambda:need(from_triples(6,1,reconstruct(lines,rec),0)['mu_energy']==36,'CONTROL','swapped triangles'))
 good('eligible neutral',lambda:need(eligible(rec),'CONTROL','neutral included'))
 worse=copy.deepcopy(rec);worse.update(delta_mu=4,new_mu=40,classification='valid_lambda_preserving_mu_up')
 good('mu worsening retained in selection population',lambda:need(eligible(worse),'CONTROL','worsening included'))
 h0='0'*64;h1='1'*64
 pool=[dict(root_residual=10,mu_energy=100,input_adjacency_sha256=h0,proposal_id=0),dict(root_residual=9,mu_energy=110,input_adjacency_sha256=h1,proposal_id=1)]
 good('root residual precedes global mu',lambda:need(select(pool)==pool[1],'CONTROL','root-first key'))
 p=[dict(root_residual=9,mu_energy=110,input_adjacency_sha256=h1,proposal_id=0),dict(root_residual=9,mu_energy=110,input_adjacency_sha256=h0,proposal_id=2),dict(root_residual=9,mu_energy=110,input_adjacency_sha256=h0,proposal_id=1)]
 good('hash then proposal tie order',lambda:need(select(p)==p[2],'CONTROL','tie key'))
 bad('boolean vertex','DOMAIN',lambda:from_triples(6,1,[[False,1,2],[3,4,5]],0))
 bad('repeated vertex','DOMAIN',lambda:from_triples(6,1,[[0,0,2],[3,4,5]],0))
 bad('duplicate triple','LINEARITY',lambda:from_triples(6,1,[[0,1,2],[0,1,2]],0))
 bad('nonregular incidence','DEGREE',lambda:from_triples(6,1,[[0,1,2],[0,3,4]],0))
 bad('wrong cardinality','DOMAIN',lambda:from_triples(6,1,[[0,1,2]],0))
 bad('asymmetric matrix','MATRIX',lambda:read_matrix(score['matrix'].replace(b'011',b'001',1),9,2,0))
 bad('nonbinary matrix','MATRIX',lambda:read_matrix(score['matrix'].replace(b'1',b'2',1),9,2,0))
 broken=copy.deepcopy(rec);broken['i']=True
 bad('boolean proposal index','RECORD',lambda:reconstruct(lines,broken))
 broken=copy.deepcopy(rec);broken['new_triples'][0][0]=4
 bad('wrong literal trade','RECORD',lambda:reconstruct(lines,broken))
 broken=copy.deepcopy(rec);broken['valid']=1
 bad('boolean validity required','RECORD',lambda:eligible(broken))
 broken=copy.deepcopy(rec);broken['new_lambda']=1
 bad('nonzero alleged preserving graph','RECORD',lambda:eligible(broken))
 broken=copy.deepcopy(rec);broken['classification']='valid_lambda_preserving_mu_up'
 bad('wrong mu sign category','RECORD',lambda:eligible(broken))
 bad('empty population','SELECTION',lambda:select([]))
 broken=copy.deepcopy(p);broken[0]['proposal_id']=True
 bad('boolean selection key','SELECTION',lambda:select(broken))
 bad('duplicate JSON keys','JSON_KEYS',lambda:loads(b'{"a":1,"a":2}'))
 c=CENSUSES[0];m=dict(population=239085,completed_proposals=239085,budget_stop=False,independent_approval=False,target_resolution=False,identity=dict(n=99,degree=7,root=11,total=239085,source_commit=COMMIT))
 r=dict(status=c['review_status'],complete_proposals_checked=239085,frozen_labelled_proposals=239085,complete_universe=True,verifier='/root',target_resolution='NONE')
 good('actual typed manifest and ROOT audit scope',lambda:receipt_scope(c,m,r))
 b=copy.deepcopy(m);b['target_resolution']=None
 bad('null is not Boolean false target result','AUDIT',lambda:receipt_scope(c,b,r))
 b=copy.deepcopy(m);b['target_resolution']=0
 bad('integer zero is not Boolean false target result','AUDIT',lambda:receipt_scope(c,b,r))
 b=copy.deepcopy(r);b['verifier']='ROOT'
 bad('invented reviewer alias','AUDIT',lambda:receipt_scope(c,m,b))
 b=copy.deepcopy(r);b['complete_universe']=1
 bad('typed complete scope','AUDIT',lambda:receipt_scope(c,m,b))
 b=copy.deepcopy(m);b['identity']['root']=81
 bad('other root not selection universe','AUDIT',lambda:receipt_scope(c,b,r))
 b=copy.deepcopy(m);b['completed_proposals']=239084
 bad('unfinished census','AUDIT',lambda:receipt_scope(c,b,r))
 raw=canonical(rec);path=out/'tiny.jsonl.gz'
 with path.open('xb') as f:
  with gzip.GzipFile(filename='',fileobj=f,mode='wb',mtime=0) as g:g.write(raw)
 part=dict(start=0,end=1,record_count=1,raw_bytes=len(raw),raw_sha256=digest(raw),gzip_bytes=path.stat().st_size,gzip_sha256=sha(path))
 good('complete gzip identity/ordered labels',lambda:need(len(list(stream_part(part,path,0)))==1,'CONTROL','part'))
 b=dict(part);b['gzip_sha256']='0'*64
 bad('compressed hash corruption','PART_HASH',lambda:list(stream_part(b,path,0)))
 b=dict(part);b['raw_sha256']='0'*64
 bad('raw hash corruption','PART_HASH',lambda:list(stream_part(b,path,0)))
 b=dict(part);b['start']=1;b['end']=2
 bad('noncontiguous part','PART_SEQUENCE',lambda:list(stream_part(b,path,0)))
 b=dict(part);b['record_count']=2;b['end']=2
 bad('missing raw record','PART_HASH',lambda:list(stream_part(b,path,0)))
 b=dict(part);b['raw_bytes']=len(raw)-1
 bad('decompression byte bound','PART_HASH',lambda:list(stream_part(b,path,0)))
 write(out/'controls.json',results)
 return dict(status='ROOT_FOCUSED_START_EXPORT_V2_AUTHOR_CONTROLS_PASS_PENDING_ROOT_REVIEW',controls_count=len(results),positive=sum(r['expectation']=='positive' for r in results),strict_negative=sum(r['expectation']!='positive' for r in results),controls_sha256=sha(out/'controls.json'))

def export(out,deadline,pins):
 pool=[];census_records=[];base_triples={};part_total=0
 for c in CENSUSES:
  clock_check(deadline)
  m=loads(authenticate(c['manifest'],c['manifest_sha'],pins).read_bytes());r=loads(authenticate(c['review'],c['review_sha'],pins).read_bytes())
  minimum=loads(authenticate(c['minimum'],c['minimum_sha'],pins).read_bytes())
  receipt_scope(c,m,r)
  need(r['inputs_sha256'].get(c['manifest'])==c['manifest_sha'] and r['inputs_sha256'].get(c['minimum'])==c['minimum_sha'],'AUDIT','review binds literal census/minimum artifacts')
  for name,h in {**m['identity']['inputs_sha256'],**m['identity']['software']}.items():authenticate(name,h,pins)
  raw=authenticate(c['triples'],c['triples_sha'],pins).read_bytes()
  triples=state_current(raw) if c['label']=='original' else loads(raw)['triples'];base_triples[c['label']]=triples
  base=from_triples(99,7,triples,11)
  need(base['matrix']==authenticate(c['matrix'],c['matrix_sha'],pins).read_bytes() and base['matrix_sha256']==c['matrix_sha'],'SOURCE','source incidence/matrix equality')
  need(base['lambda_energy']==0 and base['mu_energy']==3480 and base['root_residual']==52,'SOURCE','exact zero-lambda source scores')
  start=0;found=[];counts=Counter()
  for part in tqdm(m['parts'],desc=c['label']+' authenticated census parts',unit='part',mininterval=1):
   clock_check(deadline);path=authenticate(part['path'],part['gzip_sha256'],pins)
   for record,line in stream_part(part,path,start,deadline):
    counts[record['classification']]+=1
    if not eligible(record):continue
    changed=reconstruct(triples,record);score=from_triples(99,7,changed,11)
    need(score['lambda_energy']==record['new_lambda']==0 and score['mu_energy']==record['new_mu'] and score['root_residual']==record['new_root_residual'],'SCORE','complete reconstructed exact candidate scores')
    need(record['delta_lambda']==0 and record['delta_mu']==score['mu_energy']-base['mu_energy'] and record['root_residual_delta']==score['root_residual']-base['root_residual'],'SCORE','exact source-relative deltas')
    v=dict(census=c['label'],input_adjacency_sha256=c['matrix_sha'],proposal_id=record['proposal_id'],
     root_residual=score['root_residual'],mu_energy=score['mu_energy'],lambda_energy=score['lambda_energy'],
     adjacency_sha256=score['matrix_sha256'],raw_record_sha256=digest(line),raw_part=part['path'],raw_part_sha256=part['raw_sha256'],
     full_record=record,literal_record=line.decode('ascii'),census_manifest=c['manifest'],census_manifest_sha256=c['manifest_sha'])
    pool.append(v);found.append(v)
   start=part['end'];part_total+=1
   write(out/f"checkpoint_{c['label']}_{start:09d}.json",dict(census=c['label'],complete_raw_labels=start,eligible_labels=len(found),inputs_sha256={part['path']:part['gzip_sha256']},next_part_start=start,complete=False))
  need(start==239085 and len(m['parts'])==48 and len(found)==c['eligible'] and dict(counts)==m['aggregate']['counts']==r['aggregate']['counts'],'POPULATION','complete finite population and category counts')
  minr=min(v['root_residual'] for v in found)
  expected=[dict(proposal_id=v['proposal_id'],new_root_residual=v['root_residual'],new_mu=v['mu_energy']) for v in found if v['root_residual']==minr]
  need(minimum['population_count']==len(found) and minimum['minimum_root_residual']==minr and minimum['minimum_records']==expected,'POPULATION','all minimum-root ties match checked literal artifact')
  census_records.append(dict(label=c['label'],labels_scanned=start,eligible_labels=len(found),category_counts=dict(counts),minimum_root_residual=minr,minimum_root_ties=len(expected)))
 need(len(pool)==373 and len({c['matrix_sha'] for c in CENSUSES})==2,'POPULATION','373 labelled proposals from two distinct graph inputs')
 chosen=select(pool);c=next(c for c in CENSUSES if c['label']==chosen['census']);triples=reconstruct(base_triples[c['label']],chosen['full_record']);score=from_triples(99,7,triples,11)
 root_triples=[dict(index=i,points=t) for i,t in enumerate(triples) if 11 in t]
 need(len(root_triples)==7 and len({v for r in root_triples for v in r['points'] if v!=11})==14,'EXPORT','seven literal root triples')
 old=read_matrix(authenticate(OLD['matrix'],OLD['matrix_sha'],pins).read_bytes(),99,7,81)
 authenticate(OLD['review'],OLD['review_sha'],pins)
 need((old['lambda_energy'],old['mu_energy'],old['root_residual'])==(0,3608,50),'COMPARISON','separate old root81 baseline')
 write(out/'ordered_triples.json',dict(schema='ROOT_FOCUSED_ORDERED_TRIPLES_V1',n=99,degree=7,root=11,triples=triples,root_triples=root_triples))
 (out/'selected.adj').write_bytes(score['matrix']);(out/'selected_record.jsonl').write_bytes(chosen['literal_record'].encode('ascii'))
 sorted_pool=sorted(pool,key=key);write(out/'eligible_population.json',dict(unit='labelled eligible proposal',count=len(pool),records=sorted_pool))
 graph_groups={}
 for v in sorted_pool:graph_groups.setdefault(v['adjacency_sha256'],[]).append(dict(census=v['census'],proposal_id=v['proposal_id']))
 duplicates=[dict(adjacency_sha256=h,labelled_proposals=v) for h,v in sorted(graph_groups.items()) if len(v)>1]
 write(out/'duplicate_graph_ties.json',dict(unique_graphs=len(graph_groups),duplicate_groups=duplicates))
 selection=dict(schema='ROOT_FOCUSED_START_SELECTION_V1',status='CANDIDATE_PENDING_ROOT_INDEPENDENT_CHECK',producer='/root/checkpoint_audit',root=11,
  selection_rule=['root_residual','mu_energy','input_adjacency_sha256','proposal_id'],population_unit='lambda-preserving labelled proposal from either complete census, including mu-worsening',
  eligible_count=373,distinct_input_graphs=2,census_records=census_records,selected=chosen,exact_scores=public_score(score),seven_frozen_literal_root_triples=root_triples,
  minimum_root_mu_ties=[dict(census=v['census'],proposal_id=v['proposal_id'],input_adjacency_sha256=v['input_adjacency_sha256'],adjacency_sha256=v['adjacency_sha256']) for v in sorted_pool if (v['root_residual'],v['mu_energy'])==(chosen['root_residual'],chosen['mu_energy'])],
  unique_eligible_graphs=len(graph_groups),separate_old_stepzero_root81=dict(matrix=OLD['matrix'],matrix_sha256=OLD['matrix_sha'],lambda_energy=old['lambda_energy'],mu_energy=old['mu_energy'],root_residual=old['root_residual'],eligible_for_selection=False),
  output_hashes={n:sha(out/n) for n in ['ordered_triples.json','selected.adj','selected_record.jsonl','eligible_population.json','duplicate_graph_ties.json']},
  source_inputs_sha256=dict(pins),target_resolution='NONE',support_pair_uniqueness_assumed=False,
  limitations=['Selection is finite over 373 labelled proposals; no plateau closure, ergodicity or target exclusion.',
   'Full census correctness is reused from the two exact ROOT reviews; this producer authenticates all raw bytes and independently reconstructs/scores only eligible graphs.',
   'RNG/caches/best-state fields from historical state are not imported; only literal current ordered triples are extracted.',
   'No optimization, root-scaffold feasibility or support-pair uniqueness is asserted.'])
 write(out/'selection.json',selection)
 (out/'graph_input.txt').write_bytes(native_bytes(99,7,11,triples,sha(out/'selected.adj'),sha(out/'ordered_triples.json'),sha(out/'selection.json')))
 return dict(status='ROOT_FOCUSED_START_EXPORT_V2_CANDIDATE_PENDING_ROOT_INDEPENDENT_CHECK',parts_authenticated=part_total,
  raw_labels_authenticated=478170,eligible_labels_reconstructed=373,unique_eligible_graphs=len(graph_groups),selection=chosen,
  scores=public_score(score),seven_root_triples=root_triples,target_resolution='NONE',independent_approval=False,
  output_hashes={n:sha(out/n) for n in ['ordered_triples.json','selected.adj','selected_record.jsonl','eligible_population.json','duplicate_graph_ties.json','selection.json','graph_input.txt']})

def main():
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['controls','export']);p.add_argument('--seconds',type=float,required=True);p.add_argument('--out',required=True);p.add_argument('--controls');p.add_argument('--controls-sha256');a=p.parse_args()
 deadline=CommandDeadline(a.seconds,allocation_reason='Finite raw start selection/export controls or literal extraction only; two fully reviewed censuses, no optimizer')
 out=(ROOT/a.out).resolve();need(out.is_relative_to(ROOT) and not out.exists(),'OUTPUT','fresh workspace directory');out.mkdir(parents=True)
 pins={};start=datetime.now(timezone.utc).isoformat()
 try:
  for name,h in SOFTWARE.items():authenticate(name,h,pins)
  authenticate(SELF,None,pins);authenticate(SPEC,None,pins)
  write(out/'manifest.json',dict(mode=a.mode,source_commit=COMMIT,source_commit_role='input-census source and existing repository HEAD; new working producer is separately hash-pinned',command=sys.argv,cwd=str(ROOT),started_at=start,
    seconds=a.seconds,save_reserve_seconds=20,inputs_sha256=pins,producer='/root/checkpoint_audit',python=platform.python_version(),tqdm=importlib.metadata.version('tqdm'),
    success_criterion='controls reject exact corrupt stages; export authenticates all478170labels and scores all373eligible, deterministic literal export pending ROOT review',
    independent_verification_requirement='ROOT must independently check population/selection/raw triples/root lines/full integer matrix product before import; producer cannot approve itself'))
  if a.mode=='controls':result=controls(out,deadline)
  else:
   need(a.controls and a.controls_sha256,'CALIBRATION','exact applicable author controls required')
   cal=loads(authenticate(a.controls,a.controls_sha256,pins).read_bytes())
   need(cal['status']=='ROOT_FOCUSED_START_EXPORT_V2_AUTHOR_CONTROLS_PASS_PENDING_ROOT_REVIEW' and cal['inputs_sha256'][SELF]==pins[SELF] and cal['inputs_sha256'][SPEC]==pins[SPEC] and all(cal['inputs_sha256'][name]==h for name,h in SOFTWARE.items()),'CALIBRATION','unchanged source/spec/environment controls')
   result=export(out,deadline,pins)
  result.update(timestamp=datetime.now(timezone.utc).isoformat(),started_at=start,producer='/root/checkpoint_audit',source_commit=COMMIT,inputs_sha256=pins,command=sys.argv,cwd=str(ROOT),python=platform.python_version(),tqdm=importlib.metadata.version('tqdm'),deadline=deadline.status())
  write(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k in ['status','controls_count','positive','strict_negative','parts_authenticated','raw_labels_authenticated','eligible_labels_reconstructed','unique_eligible_graphs','deadline']}))
 except Exception as e:
  write(out/'summary.json',dict(status='FAILED_NO_APPROVAL',error_type=type(e).__name__,error=str(e),timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=pins,deadline=deadline.status(),target_resolution='NONE'))
  raise
if __name__=='__main__':main()
