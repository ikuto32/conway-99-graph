"""Independent exact raw-object/root/RNG/replay core; no producer imports.

Splitmix/xoshiro formula is disclosed shared checking logic from prior independent
hypergraph controls, extended with a separately derived bounded rejection path.
"""
from collections import Counter
import copy
import hashlib
import itertools
import json
import math
import re

M=(1<<64)-1
OBJECTIVE='SRG_ROOT_LOCAL_PAIR_RESIDUAL_V1'
KERNEL='FROZEN_ROOT_LINEAR_TRIPLE_EXCLUSIVE_SWAP_V1'
DISTRIBUTION='MUTABLE_LABELLED_LINES_REJECTION_BOUNDED_XOSHIRO256SS_V1'
CONFIG=('objective','lambda_weight','move_kernel','distribution','n','degree','root','input_sha256','source_matrix_sha256','source_triples_sha256','selection_report_sha256','probe_identity','seed','mix_steps','schedule_steps','t_start','t_end','forced','checkpoint_every')
COUNTERS=('step','admissible','accepted','best_updates','local_updates')
SCORES=('root_energy','lambda_energy','mu_energy','root_residual')
HEX=re.compile(r'[0-9a-f]{64}\Z');INT=re.compile(r'-?(0|[1-9][0-9]*)\Z')
TOL=1e-12
class CheckError(ValueError):
 def __init__(self,stage,message):self.stage=stage;super().__init__(stage+': '+message)
def need(ok,message,stage='REPLAY'):
 if not ok:raise CheckError(stage,message)
def digest(raw):return hashlib.sha256(raw).hexdigest()
def integer(token,stage='SYNTAX',unsigned=False):
 need(type(token)is str and INT.fullmatch(token)is not None,'canonical decimal integer',stage);v=int(token)
 if unsigned:need(0<=v<=M,'uint64 range',stage)
 return v
def domain(n,degree,root):
 need(type(n)is int and type(degree)is int and type(root)is int and (n,degree)in[(99,7),(9,2),(12,2)]and 0<=root<n,'declared control/target dimensions and root','DOMAIN')
def fixture(name):
 if name=='rook9':return [[r*3+c for c in range(3)]for r in range(3)]+[[r*3+c for r in range(3)]for c in range(3)]
 if name=='prism9':return [[0,2,6],[0,1,7],[1,2,8],[3,5,6],[3,4,7],[4,5,8]]
 if name=='cube12_defect':return [[1,2,7],[0,3,4],[1,5,6],[3,5,7],[2,8,9],[4,8,10],[6,9,11],[0,10,11]]
 need(name=='target99','explicit known fixture','DOMAIN')
 return [[v,v+33,v+66]for v in range(33)]+[[v,(v+1)%99,(v+4)%99]for v in range(99)]+[[v,(v+7)%99,(v+18)%99]for v in range(99)]
def graph(triples,n,degree,root):
 domain(n,degree,root);need(type(triples)is list and len(triples)*3==n*degree,'complete ordered triple population','DOMAIN')
 adj=[set()for _ in range(n)];incidence=[0]*n
 for t in triples:
  need(type(t)is list and len(t)==3 and all(type(x)is int and 0<=x<n for x in t)and len(set(t))==3,'literal distinct triple vertices','DOMAIN')
  for x in t:incidence[x]+=1
  for x,y in itertools.combinations(t,2):need(y not in adj[x],'linear pair uniqueness','DOMAIN');adj[x].add(y);adj[y].add(x)
 need(incidence==[degree]*n and all(len(s)==2*degree for s in adj),'regular raw incidence and point graph','DOMAIN')
 el=em=rr=0;cn=[]
 for u in range(n):
  for v in range(u+1,n):
   c=len(adj[u]&adj[v]);cn.append(c)
   if v in adj[u]:el+=(c-1)**2
   else:em+=(c-2)**2;rr+=(c-2)**2 if root in (u,v) else 0
 return dict(adj=adj,cn=cn,root_energy=60*el+rr,lambda_energy=el,mu_energy=em,root_residual=rr)
def matrix_bytes(g):
 n=len(g['adj']);return (str(n)+'\n'+''.join(''.join('1'if v in a else'0'for v in range(n))+'\n'for a in g['adj'])).encode()
def scalar_matrix(raw,n,degree,root):
 domain(n,degree,root)
 try:lines=raw.decode('ascii').splitlines()
 except UnicodeError:raise CheckError('MATRIX','ASCII matrix')
 need(len(lines)==n+1 and lines[0]==str(n)and all(len(r)==n and set(r)<={'0','1'}for r in lines[1:]),'complete binary matrix','MATRIX')
 a=[[int(x)for x in row]for row in lines[1:]];cols=list(zip(*a));el=em=rr=0;bad=0;adj=Counter();non=Counter();root_adj=Counter();root_non=Counter()
 need(all(a[i][i]==0 and sum(a[i])==2*degree for i in range(n))and all(a[i][j]==a[j][i]for i in range(n)for j in range(n)),'zero diagonal/symmetry/exact degree','MATRIX')
 for i in range(n):
  for j in range(n):
   c=sum(x*y for x,y in zip(a[i],cols[j]));bad+=int(c!=(2*degree if i==j else 2-a[i][j]))
   if i<j:
    if a[i][j]:el+=(c-1)**2;adj[c]+=1
    else:em+=(c-2)**2;non[c]+=1;rr+=(c-2)**2 if root in (i,j) else 0
   if i==root and i!=j:(root_adj if a[i][j]else root_non)[c]+=1
 return dict(root_energy=60*el+rr,lambda_energy=el,mu_energy=em,root_residual=rr,ordered_entries_checked=n*n,identity_mismatches=bad,srg_valid=bad==0,
  adjacent_cn_histogram=dict(sorted(adj.items())),nonadjacent_cn_histogram=dict(sorted(non.items())),root_adjacent_cn_histogram=dict(sorted(root_adj.items())),root_nonadjacent_cn_histogram=dict(sorted(root_non.items())))
def target_zero(raw,claimed):
 need(type(claimed)is int and claimed==0,'literal zero claim','TARGET_ZERO');r=scalar_matrix(raw,99,7,11);need(r['srg_valid']and r['ordered_entries_checked']==9801,'complete99 integer target identity','TARGET_ZERO');return r
def frozen_map(triples,root):
 frozen=[[i,*t]for i,t in enumerate(triples)if root in t];mutable=[i for i,t in enumerate(triples)if root not in t];return frozen,mutable
def reference_check(s,reference,provenance=None):
 frozen,mutable=frozen_map(reference,s['root'])
 need(s['frozen']==frozen and s['mutable']==mutable,'original literal frozen rows and mutable labels','REFERENCE')
 if provenance is not None:need(all(s[k]==v for k,v in provenance.items()),'original input provenance','PROVENANCE')
 for rows in [s['current'],s['best_root']]+[s[k]['triples']for k in['first_localzero','best_localzero_mu']if s[k]is not None]:
  need(all(rows[r[0]]==r[1:]for r in frozen),'original root literal triples in every raw object','REFERENCE')
  need(graph(rows,s['n'],s['degree'],s['root'])['adj'][s['root']]=={v for r in frozen for v in r[1:]if v!=s['root']},'original root adjacency','REFERENCE')
def rot(v,k):return ((v<<k)|(v>>(64-k)))&M
def seed_words(seed):
 result=[]
 for _ in range(4):
  seed=(seed+0x9e3779b97f4a7c15)&M;z=seed;z=((z^(z>>30))*0xbf58476d1ce4e5b9)&M;z=((z^(z>>27))*0x94d049bb133111eb)&M;result.append(z^(z>>31))
 return result
def rng_next(s):
 result=(rot((s[1]*5)&M,7)*9)&M;t=(s[1]<<17)&M;s[2]^=s[0];s[3]^=s[1];s[1]^=s[2];s[0]^=s[3];s[2]^=t;s[3]=rot(s[3],45);return result
def bounded(draw,bound):
 need(type(bound)is int and 0<bound<=M,'positive uint64 bound','RNG');threshold=(1<<64)%bound
 for count in range(1,1025):
  word=draw();need(type(word)is int and 0<=word<=M,'uint64 random word','RNG')
  if word>=threshold:return word%bound,count
 raise CheckError('RNG','bounded rejection limit')
def snapshot(s,reason):return dict(**{k:s[k]for k in COUNTERS},rng=s['rng'][:],triples=copy.deepcopy(s['current']),reason=reason)
def capture(s):
 g=graph(s['current'],s['n'],s['degree'],s['root'])
 if g['lambda_energy']or g['root_residual']:return
 if s['first_localzero']is None:s['first_localzero']=snapshot(s,'initial'if s['step']==0 else'first_localzero');s['best_localzero_mu']=copy.deepcopy(s['first_localzero'])
 elif g['mu_energy']<graph(s['best_localzero_mu']['triples'],s['n'],s['degree'],s['root'])['mu_energy']:
  s['local_updates']+=1;s['best_localzero_mu']=snapshot(s,'accepted_mu_improvement')
def initial(name,root,seed=99033001,temp=0,end=None,mix=0,forced=False,checkpoint=64,schedule=1024,provenance=None,probe_identity='0'*64,triples=None):
 rows=fixture(name)if triples is None else copy.deepcopy(triples);n,d=(99,7)if name=='target99'else(12,2)if name=='cube12_defect'else(9,2);g=graph(rows,n,d,root)
 s=dict(objective=OBJECTIVE,lambda_weight=60,move_kernel=KERNEL,distribution=DISTRIBUTION,n=n,degree=d,root=root,input_sha256='0'*64,source_matrix_sha256='0'*64,source_triples_sha256='0'*64,selection_report_sha256='0'*64,probe_identity=probe_identity,
  seed=seed,mix_steps=mix,schedule_steps=schedule,t_start=float(temp),t_end=float(temp if end is None else end),forced=int(forced),checkpoint_every=checkpoint,
  step=0,admissible=0,accepted=0,best_updates=0,local_updates=0,rng=seed_words(seed),current=rows,best_root=copy.deepcopy(rows),first_localzero=None,best_localzero_mu=None)
 if provenance:s.update(provenance)
 s['frozen'],s['mutable']=frozen_map(rows,root)
 for k in SCORES:s[k]=g[k];s['best_'+k]=g[k]
 s['cn']=g['cn'];capture(s);return s
class Tokens:
 def __init__(self,raw):
  try:self.words=raw.decode('ascii').split()
  except UnicodeError:raise CheckError('SYNTAX','ASCII state')
  self.at=0
 def take(self):need(self.at<len(self.words),'complete ordered tokens','SYNTAX');v=self.words[self.at];self.at+=1;return v
 def expect(self,value):need(self.take()==value,'literal tag '+value,'SYNTAX')
 def field(self,name):self.expect(name);return self.take()
 def number(self,name,unsigned=False,stage='SYNTAX'):return integer(self.field(name),stage,unsigned)
 def rows(self,tag,count):
  need(self.number(tag)==count,'complete '+tag+' rows','DOMAIN');return [[integer(self.take())for _ in range(3)]for _ in range(count)]
 def rng(self,tag):
  self.expect(tag);s=[integer(self.take(),'RNG',True)for _ in range(4)];need(any(s),'nonzero four-word RNG','RNG');return s
 def end(self):self.expect('END');need(self.at==len(self.words),'exact EOF','SYNTAX')
def parse_snapshot(t,prefix,s):
 flag=t.number(prefix+'_found');need(flag in(0,1),'literal snapshot flag','SNAPSHOT')
 if not flag:return None
 r={k:t.number(prefix+'_'+k,True,'SNAPSHOT')for k in COUNTERS};r['reason']=t.field(prefix+'_reason');need(r['reason']in['initial','first_localzero','accepted_mu_improvement'],'snapshot reason','SNAPSHOT')
 r['rng']=t.rng(prefix+'_rng');r['triples']=t.rows(prefix+'_triples',s['n']*s['degree']//3);g=graph(r['triples'],s['n'],s['degree'],s['root'])
 need(g['lambda_energy']==g['root_residual']==0,'exact complete localzero object','SNAPSHOT')
 need(all(r[k]<=s[k]for k in COUNTERS)and r['best_updates']<=r['accepted']and r['local_updates']<=r['accepted']<=r['admissible']<=r['step'],'snapshot counter consistency','SNAPSHOT')
 return r
def parse_state(raw,reference=None):
 t=Tokens(raw);t.expect('ROOT_FOCUSED_ANNEAL_STATE_V1');s={}
 for name in CONFIG:
  v=t.field(name)
  if name in ['t_start','t_end']:
   try:s[name]=float(v)
   except ValueError:raise CheckError('SCHEDULE','finite temperature')
  elif name in ['n','degree','root','lambda_weight','forced']:s[name]=integer(v)
  elif name in ['seed','mix_steps','schedule_steps','checkpoint_every']:s[name]=integer(v,'COUNTERS',True)
  else:s[name]=v
 need(s['objective']==OBJECTIVE and s['lambda_weight']==60,'exact objective/weight','OBJECTIVE')
 need(s['move_kernel']==KERNEL and s['distribution']==DISTRIBUTION,'exact changed kernel/distribution','KERNEL');domain(s['n'],s['degree'],s['root'])
 need(all(HEX.fullmatch(s[k])is not None for k in ['input_sha256','source_matrix_sha256','source_triples_sha256','selection_report_sha256','probe_identity']),'literal provenance hashes','PROVENANCE')
 need(s['forced']in[0,1]and s['schedule_steps']>0 and s['checkpoint_every']>0 and all(math.isfinite(s[k])and 0<=s[k]<=1000 for k in ['t_start','t_end']),'finite bounded schedule','SCHEDULE')
 for name in COUNTERS:s[name]=t.number(name,True,'COUNTERS')
 need(s['best_updates']<=s['accepted']and s['local_updates']<=s['accepted']<=s['admissible']<=s['step'],'full counter order','COUNTERS')
 for name in SCORES+tuple('best_'+k for k in SCORES):s[name]=t.number(name)
 s['rng']=t.rng('rng');count=s['n']*s['degree']//3
 need(t.number('frozen')==s['degree'],'frozen row cardinality','REFERENCE');s['frozen']=[[integer(t.take())for _ in range(4)]for _ in range(s['degree'])]
 need(t.number('mutable')==count-s['degree'],'mutable cardinality','REFERENCE');s['mutable']=[integer(t.take())for _ in range(count-s['degree'])]
 s['current']=t.rows('current',count);s['best_root']=t.rows('best_root',count);g=graph(s['current'],s['n'],s['degree'],s['root']);b=graph(s['best_root'],s['n'],s['degree'],s['root'])
 need(all(s[k]==g[k]and s['best_'+k]==b[k]for k in SCORES)and b['root_energy']<=g['root_energy'],'exact current/best components','SCORE')
 need(t.number('cn')==len(g['cn']),'full CN population','CACHE');s['cn']=[integer(t.take())for _ in g['cn']];need(s['cn']==g['cn'],'all common-neighbor cache entries','CACHE')
 s['first_localzero']=parse_snapshot(t,'first_localzero',s);s['best_localzero_mu']=parse_snapshot(t,'best_localzero_mu',s);t.end()
 need((s['first_localzero']is None)==(s['best_localzero_mu']is None),'both retained snapshot flags','SNAPSHOT')
 if s['first_localzero']is not None:
  f=graph(s['first_localzero']['triples'],s['n'],s['degree'],s['root']);l=graph(s['best_localzero_mu']['triples'],s['n'],s['degree'],s['root'])
  need(l['mu_energy']<=f['mu_energy']and s['best_root_energy']==0 and (g['root_energy']!=0 or l['mu_energy']<=g['mu_energy']),'literal retained mu ordering','SNAPSHOT')
 need(g['root_energy']!=0 or s['first_localzero']is not None,'localzero selection complete','SNAPSHOT')
 reference_check(s,s['current']if reference is None else reference);return s
def serialize(s):
 lines=['ROOT_FOCUSED_ANNEAL_STATE_V1']+[k+' '+str(s[k])for k in CONFIG]+[k+' '+str(s[k])for k in COUNTERS]+[k+' '+str(s[k])for k in SCORES+tuple('best_'+k for k in SCORES)]+['rng '+' '.join(map(str,s['rng'])),'frozen '+str(len(s['frozen']))]
 lines+=[' '.join(map(str,r))for r in s['frozen']];lines+=['mutable '+str(len(s['mutable']))+' '+' '.join(map(str,s['mutable']))]
 for k in ['current','best_root']:lines+=[k+' '+str(len(s[k]))]+[' '.join(map(str,r))for r in s[k]]
 lines+=['cn '+str(len(s['cn']))]+list(map(str,s['cn']))
 for k in ['first_localzero','best_localzero_mu']:
  r=s[k];lines+=[k+'_found '+str(int(r is not None))]
  if r is not None:lines+=[k+'_'+f+' '+str(r[f])for f in COUNTERS]+[k+'_reason '+r['reason'],k+'_rng '+' '.join(map(str,r['rng'])),k+'_triples '+str(len(r['triples']))]+[' '.join(map(str,row))for row in r['triples']]
 return ('\n'.join(lines+['END'])+'\n').encode()
def parse_graph_input(raw):
 t=Tokens(raw);t.expect('ROOT_FOCUSED_GRAPH_INPUT_V1');n=t.number('n');d=t.number('degree');r=t.number('root');domain(n,d,r)
 p={k:t.field(k)for k in ['source_matrix_sha256','source_triples_sha256','selection_report_sha256']};need(all(HEX.fullmatch(v)for v in p.values()),'graph provenance syntax','PROVENANCE');p['input_sha256']=digest(raw)
 rows=t.rows('triples',n*d//3);t.end();graph(rows,n,d,r);return dict(n=n,degree=d,root=r,triples=rows,provenance=p)
def parse_selected(raw,parent):
 t=Tokens(raw);t.expect('ROOT_FOCUSED_SELECTED_OBJECT_V1');need(t.field('objective')==OBJECTIVE,'selected objective','OBJECTIVE')
 s={k:t.number(k)for k in ['n','degree','root']};need(all(s[k]==parent[k]for k in s),'selected dimensions/root','SNAPSHOT')
 for k in ['input_sha256','source_matrix_sha256','source_triples_sha256','selection_report_sha256']:need(t.field(k)==parent[k],'selected provenance','PROVENANCE')
 need(t.number('frozen')==s['degree'],'selected frozen cardinality','REFERENCE');rows=[[integer(t.take())for _ in range(4)]for _ in range(s['degree'])];need(rows==parent['frozen'],'selected original frozen rows','REFERENCE')
 count=t.number('mutable');need([integer(t.take())for _ in range(count)]==parent['mutable'],'selected mutable labels','REFERENCE')
 need(t.number('seed',True)==parent['seed'],'selected seed','SNAPSHOT');scores={k:t.number(k)for k in SCORES};r=parse_snapshot(t,'selected',parent);need(r is not None,'selected snapshot found','SNAPSHOT');t.end();g=graph(r['triples'],s['n'],s['degree'],s['root']);need(all(scores[k]==g[k]for k in SCORES),'selected exact scores','SCORE');return r
def proposal(s,indices):
 ti,tj,pi,pj=indices;m=len(s['current']);need(all(type(v)is int for v in indices)and 0<=ti<m and 0<=tj<m and ti!=tj and pi in range(3)and pj in range(3),'labelled proposal domain','TRACE')
 t,q=s['current'][ti][:],s['current'][tj][:];x,y=t[pi],q[pj];pt,pq=t[:],q[:];pt[pi]=y;pq[pj]=x
 frozen=ti not in s['mutable']or tj not in s['mutable'];exclusive=x not in q and y not in t
 adj=graph(s['current'],s['n'],s['degree'],s['root'])['adj'];old={tuple(sorted((x,z)))for k,z in enumerate(t)if k!=pi}|{tuple(sorted((y,z)))for k,z in enumerate(q)if k!=pj}
 new={tuple(sorted((y,z)))for k,z in enumerate(t)if k!=pi}|{tuple(sorted((x,z)))for k,z in enumerate(q)if k!=pj}
 absent=all(u!=v and (v not in adj[u]or (u,v)in old)for u,v in new)
 valid=not frozen and exclusive and absent;changed=copy.deepcopy(s['current']);changed[ti]=pt;changed[tj]=pq
 return dict(indices=indices,old_triples=[t,q],proposed_triples=[pt,pq],changed=changed,probe=None,
  frozen_line_selected=frozen,disjoint=not bool(set(t)&set(q)),selected_points_exclusive=exclusive,new_pairs_absent_after_old_removal=absent,
  invalid_reason='frozen_root_line'if frozen else'selected_point_not_exclusive'if not exclusive else'new_pair_conflict'if not absent else'NONE',admissible=valid)
def transition(s,indices=None):
 before=s['rng'][:];draws=0;probing=indices is not None
 if not probing:
  size=len(s['mutable']);first,k=bounded(lambda:rng_next(s['rng']),size);draws+=k;second,k=bounded(lambda:rng_next(s['rng']),size-1);draws+=k;second+=int(second>=first)
  pi,k=bounded(lambda:rng_next(s['rng']),3);draws+=k;pj,k=bounded(lambda:rng_next(s['rng']),3);draws+=k;indices=[s['mutable'][first],s['mutable'][second],pi,pj]
 p=proposal(s,indices);old=graph(s['current'],s['n'],s['degree'],s['root']);delta=[0,0,0,0];accepted=False;draw=0;margin=None;firstbefore=s['first_localzero']is not None
 elapsed=max(0,s['step']-s['mix_steps']);fraction=min(1.,float(elapsed)/float(s['schedule_steps']));temp=s['t_start']+(s['t_end']-s['t_start'])*fraction;mixing=s['step']<s['mix_steps']
 if p['admissible']:
  new=graph(p['changed'],s['n'],s['degree'],s['root']);delta=[new[k]-old[k]for k in SCORES];s['admissible']+=1
  if not probing:
   draw=rng_next(s['rng']);u=(draw>>11)*2**-53
   if s['forced']or mixing or delta[0]<=0:accepted=True
   elif temp>0:threshold=math.exp(-float(delta[0])/temp);margin=abs(u-threshold);need(margin>TOL,'unambiguous floating acceptance','FLOAT');accepted=u<threshold
  if accepted:
   s['current']=p['changed'];s['accepted']+=1
   for k in SCORES:s[k]=new[k]
   s['cn']=new['cn']
   if new['root_energy']<s['best_root_energy']:
    s['best_root']=copy.deepcopy(s['current']);s['best_updates']+=1
    for k in SCORES:s['best_'+k]=new[k]
 step=s['step'];s['step']+=1;capture(s)
 event=dict(trace_schema='ROOT_FOCUSED_MOVE_V1',objective=OBJECTIVE,distribution=DISTRIBUTION,step=step,root=s['root'],ti=indices[0],tj=indices[1],pi=indices[2],pj=indices[3],probe=probing,
  **{k:p[k]for k in ['frozen_line_selected','disjoint','selected_points_exclusive','new_pairs_absent_after_old_removal','invalid_reason','admissible','old_triples','proposed_triples']},
  accepted=accepted,mixing=mixing,temperature=temp,selection_draws=draws,draw=str(draw),delta_F=delta[0],delta_lambda=delta[1],delta_mu=delta[2],delta_root=delta[3],
  F_before=old['root_energy'],lambda_before=old['lambda_energy'],mu_before=old['mu_energy'],root_before=old['root_residual'],F_after=s['root_energy'],lambda_after=s['lambda_energy'],mu_after=s['mu_energy'],root_after=s['root_residual'],best_F=s['best_root_energy'],
  first_localzero_before=firstbefore,first_localzero_after=s['first_localzero']is not None,local_updates=s['local_updates'],rng_before=list(map(str,before)),rng_after=list(map(str,s['rng'])))
 return event,margin
def replay(s,record,probe=None):
 expected,margin=transition(s,probe);need(type(record)is dict and set(record)==set(expected),'complete literal trace schema','TRACE')
 for k,v in expected.items():
  if k=='temperature':need(type(record[k])in[int,float]and math.isfinite(record[k])and abs(record[k]-v)<=TOL,'temperature tolerance','FLOAT')
  else:need(type(record[k])is type(v)and record[k]==v,'exact transition field '+k,'TRACE')
 return expected,margin
def pair_costs():
 rows=[]
 for c in range(15):
  for a in range(2):
   for root_pair in range(2):
    old=[(c-1)**2 if a else 0,(c-2)**2 if not a else 0]
    for delta in[-1,1]:
     if not 0<=c+delta<=14:continue
     new=[(c+delta-1)**2 if a else 0,(c+delta-2)**2 if not a else 0];dl,dm=[new[k]-old[k]for k in range(2)];dr=root_pair*dm
     rows.append(dict(kind='CN',c=c,a=a,root_pair=root_pair,delta=delta,delta_lambda=dl,delta_mu=dm,delta_root=dr,delta_F=60*dl+dr))
    new=[(c-1)**2 if not a else 0,(c-2)**2 if a else 0];dl,dm=[new[k]-old[k]for k in range(2)];dr=root_pair*dm
    rows.append(dict(kind='EDGE',c=c,a=a,root_pair=root_pair,delta=1-2*a,delta_lambda=dl,delta_mu=dm,delta_root=dr,delta_F=60*dl+dr))
 return rows
def scalar_objects(s):
 reports={}
 for name,rows in [('current',s['current']),('best_root',s['best_root'])]+[(k,s[k]['triples'])for k in['first_localzero','best_localzero_mu']if s[k]is not None]:
  g=graph(rows,s['n'],s['degree'],s['root']);r=scalar_matrix(matrix_bytes(g),s['n'],s['degree'],s['root']);need(all(r[k]==g[k]for k in SCORES),'separate scalar full product matches set intersection','MATRIX');reports[name]=r
 return reports
