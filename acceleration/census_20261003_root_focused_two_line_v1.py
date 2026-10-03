"""Exact fixed-root mutable-two-line census of one saved labelled hypergraph."""
import argparse
import re
import gzip
import hashlib
import importlib.metadata
import json
import platform
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from tqdm import tqdm
from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
TARGET_STATE='acceleration/results/20261003_hypergraph_root_focused_pilot01/native/final.state'
TARGET_STATE_SHA='f38346ba0d3367acfc585854587e30bf5748ffe5ede658cd0055f41edd0f0bb3'
TARGET_MATRIX='acceleration/results/20261003_hypergraph_root_focused_pilot01/native/current.adj'
TARGET_MATRIX_SHA='3f910d235e38191b5ac47523c22166f1abfc4d1f3ad285b60d4c684392a6670d'
SAVED_AUDIT='acceleration/results/20261003_independent_review/root_focused_saved_pilot01/summary.json'
SAVED_AUDIT_SHA='7b54dfeb4d54c6a0cb99ab18a67bf2a5d0b263290e4a120cebc6d38a0d5af558'
FROZEN_ROWS=[[15,59,3,11],[18,78,11,62],[22,37,18,11],[57,11,77,15],[61,88,11,12],[82,11,23,96],[154,11,93,46]]
SOURCE_STATE_MAGIC='ROOT_FOCUSED_ANNEAL_STATE_V1'
STATE_SCOPES={'objective':'SRG_ROOT_LOCAL_PAIR_RESIDUAL_V1','lambda_weight':'60','move_kernel':'FROZEN_ROOT_LINEAR_TRIPLE_EXCLUSIVE_SWAP_V1','distribution':'MUTABLE_LABELLED_LINES_REJECTION_BOUNDED_XOSHIRO256SS_V1'}
SOFTWARE={
 'acceleration/command_deadline.py':'9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9',
 'acceleration/run_compute_command.py':'593a9feed6250739dc9672338df23ab171fc9a6a6db4196c1feb312efa33957a',
 'acceleration/native_budget_env_v1/pyproject.toml':'96f96d7345153b4bde50d7f4a640a33d43dfd6458c35f4e6a4ab798b11673782',
 'acceleration/native_budget_env_v1/uv.lock':'54ecb16b929dac1035b5a8691df419d58eab33dc3f07c76c5259094e265a4434',
}
RECORD_SCHEMA='FROZEN_ROOT_TWO_LINE_LABELLED_PROPOSAL_V1'
CHECKPOINT_SCHEMA='FROZEN_ROOT_TWO_LINE_CENSUS_CHECKPOINT_V1'
MANIFEST_SCHEMA='FROZEN_ROOT_TWO_LINE_CENSUS_MANIFEST_V1'
CHUNK=5000
MAX_LINE=4096


class CheckError(ValueError):
 def __init__(self,stage,message):self.stage=stage;super().__init__(stage+': '+message)


def need(ok,stage,message):
 if not ok:raise CheckError(stage,message)


def sha(path):
 with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def save(path,value):
 with path.open('x',encoding='utf8',newline='\n') as stream:json.dump(value,stream,indent=2);stream.write('\n')


def canonical(value):return (json.dumps(value,sort_keys=True,separators=(',',':'))+'\n').encode()


def full_score(masks,root):
 n=len(masks);lam=mu=0;cn=[[0]*n for _ in range(n)]
 for i in range(n):
  for j in range(i+1,n):
   common=(masks[i]&masks[j]).bit_count();cn[i][j]=cn[j][i]=common
   if (masks[i]>>j)&1:lam+=(common-1)**2
   else:mu+=(common-2)**2
 row=sum((cn[root][j]-2)**2 for j in range(n) if j!=root and not ((masks[root]>>j)&1))
 return lam,mu,row,cn


def domain(n,degree,triples,root):
 need(type(n) is int and n>0 and type(root) is int and 0<=root<n,'DOMAIN','n/root')
 need(type(degree) is int and degree>0 and type(triples) is list,'DOMAIN','degree/triples')
 masks=[0]*n;point_degrees=[0]*n;seen=set()
 for triple in triples:
  need(type(triple) is list and len(triple)==3 and all(type(x) is int and 0<=x<n for x in triple) and len(set(triple))==3,'DOMAIN','three distinct literal points')
  key=tuple(sorted(triple));need(key not in seen,'DOMAIN','duplicate triple');seen.add(key)
  for x in triple:point_degrees[x]+=1
  for i in range(3):
   for j in range(i+1,3):
    a,b=triple[i],triple[j];need(not ((masks[a]>>b)&1),'LINEARITY','repeated pair')
    masks[a]|=1<<b;masks[b]|=1<<a
 need(all(d==degree for d in point_degrees) and all(m.bit_count()==2*degree for m in masks),'DEGREE','complete regular incidence')
 lam,mu,row,cn=full_score(masks,root)
 frozen=[[i,*t] for i,t in enumerate(triples) if root in t];mutable=[i for i,t in enumerate(triples) if root not in t]
 need(len(frozen)==degree,'FROZEN_DOMAIN','root incident literal rows')
 pairs=[(i,j) for at,i in enumerate(mutable) for j in mutable[at+1:]]
 return dict(n=n,degree=degree,triples=triples,root=root,masks=masks,cn=cn,lambda_energy=lam,mu_energy=mu,
             root_residual=row,frozen_rows=frozen,mutable_labels=mutable,pairs=pairs,total=len(pairs)*9)


def adjacency_bytes(masks):
 return (str(len(masks))+'\n'+''.join(''.join(str((mask>>j)&1) for j in range(len(masks)))+'\n' for mask in masks)).encode()


def masks_from_record(base,record):
 masks=list(base['masks'])
 for a,b in record['toggles']:masks[a]^=1<<b;masks[b]^=1<<a
 return masks


def proposal(base,pid):
 need(type(pid) is int and 0<=pid<base['total'],'PROPOSAL_DOMAIN','proposal ID')
 i,j=base['pairs'][pid//9];ix,jy=(pid%9)//3,pid%3
 first,second=base['triples'][i],base['triples'][j];x,y=first[ix],second[jy]
 record=dict(schema=RECORD_SCHEMA,proposal_id=pid,i=i,j=j,ix=ix,jy=jy,old_triples=[first,second],
             new_triples=None,valid=False,invalid_reason=None,conflict_pair=None,toggles=None,
             delta_lambda=None,delta_mu=None,new_lambda=None,new_mu=None,new_root_residual=None,
             root_residual_delta=None,frozen_root_unchanged=None,mu_direction=None,classification=None)
 if x in second or y in first:
  record.update(invalid_reason='selected_point_not_exclusive',classification='invalid_selection');return record
 a,b=[point for k,point in enumerate(first) if k!=ix];c,d=[point for k,point in enumerate(second) if k!=jy]
 new_first=list(first);new_second=list(second);new_first[ix]=y;new_second[jy]=x;record['new_triples']=[new_first,new_second]
 old=[tuple(sorted(edge)) for edge in [(x,a),(x,b),(y,c),(y,d)]]
 new=[tuple(sorted(edge)) for edge in [(y,a),(y,b),(x,c),(x,d)]]
 masks=list(base['masks'])
 for u,v in old:masks[u]&=~(1<<v);masks[v]&=~(1<<u)
 for u,v in new:
  if (masks[u]>>v)&1:
   record.update(invalid_reason='new_pair_already_present',conflict_pair=[u,v],classification='invalid_linearity');return record
  masks[u]|=1<<v;masks[v]|=1<<u
 toggles=sorted(set(old)^set(new));touched=sorted({v for edge in toggles for v in edge});touched_set=set(touched)
 delta_lam=delta_mu=0
 for u in touched:
  for v in range(base['n']):
   if u==v or (v in touched_set and v<u):continue
   old_common=base['cn'][u][v];new_common=(masks[u]&masks[v]).bit_count()
   if (base['masks'][u]>>v)&1:delta_lam-=(old_common-1)**2
   else:delta_mu-=(old_common-2)**2
   if (masks[u]>>v)&1:delta_lam+=(new_common-1)**2
   else:delta_mu+=(new_common-2)**2
 root=base['root']
 root_residual=sum(((masks[root]&masks[v]).bit_count()-2)**2 for v in range(base['n']) if v!=root and not ((masks[root]>>v)&1))
 need(masks[root]==base['masks'][root] and all(base['triples'][r[0]]==r[1:] for r in base['frozen_rows']),'FROZEN_INVARIANT','literal root lines and root adjacency retained')
 root_delta=root_residual-base['root_residual']
 classification='valid_lambda_changed' if delta_lam else 'valid_lambda_preserving_root_'+('down' if root_delta<0 else 'up' if root_delta>0 else 'equal')
 record.update(valid=True,toggles=[list(edge) for edge in toggles],delta_lambda=delta_lam,delta_mu=delta_mu,
               new_lambda=base['lambda_energy']+delta_lam,new_mu=base['mu_energy']+delta_mu,
               new_root_residual=root_residual,root_residual_delta=root_delta,frozen_root_unchanged=True,mu_direction='down' if delta_mu<0 else 'up' if delta_mu>0 else 'equal',classification=classification)
 return record


def cache_check(base):
 fresh=domain(base['n'],base['degree'],base['triples'],base['root'])
 need(fresh['masks']==base['masks'],'ADJ_CACHE','adjacency cache')
 need(fresh['cn']==base['cn'],'CN_CACHE','common-neighbor cache')
 need(all(fresh[k]==base[k] for k in ['lambda_energy','mu_energy','root_residual']),'ENERGY_CACHE','integer score cache')


def accumulator():return dict(counts=Counter(),mu_counts=Counter(),unique=set(),lambda_unique=set(),neutral_unique=set(),
 best_root=None,best=[],best_mu=None,mu_best=[],neutral_mu=None,neutral_best=[],zero_proposal_ids=[])


def accumulate(aggregate,record):
 aggregate['counts'][record['classification']]+=1
 if record['valid']:
  key=tuple(tuple(e) for e in record['toggles']);aggregate['unique'].add(key)
  if record['delta_lambda']==0:
   aggregate['lambda_unique'].add(key);aggregate['mu_counts'][record['mu_direction']]+=1
   if aggregate['best_root'] is None or record['new_root_residual']<aggregate['best_root']:aggregate['best_root']=record['new_root_residual'];aggregate['best']=[record]
   elif record['new_root_residual']==aggregate['best_root']:aggregate['best'].append(record)
   if aggregate['best_mu'] is None or record['new_mu']<aggregate['best_mu']:aggregate['best_mu']=record['new_mu'];aggregate['mu_best']=[record]
   elif record['new_mu']==aggregate['best_mu']:aggregate['mu_best'].append(record)
   if record['root_residual_delta']==0:
    aggregate['neutral_unique'].add(key)
    if aggregate['neutral_mu'] is None or record['new_mu']<aggregate['neutral_mu']:aggregate['neutral_mu']=record['new_mu'];aggregate['neutral_best']=[record]
    elif record['new_mu']==aggregate['neutral_mu']:aggregate['neutral_best'].append(record)
  if record['new_lambda']==record['new_mu']==0:aggregate['zero_proposal_ids'].append(record['proposal_id'])


def snapshot(aggregate):
 return dict(counts=dict(sorted(aggregate['counts'].items())),lambda_preserving_mu_directions=dict(sorted(aggregate['mu_counts'].items())),
  unique_valid_neighbor_graphs=len(aggregate['unique']),unique_lambda_preserving_graphs=len(aggregate['lambda_unique']),
  unique_root_neutral_lambda_preserving_graphs=len(aggregate['neutral_unique']),best_root_residual=aggregate['best_root'],
  best_root_proposal_ids=[r['proposal_id'] for r in aggregate['best']],minimum_mu=aggregate['best_mu'],
  minimum_mu_proposal_ids=[r['proposal_id'] for r in aggregate['mu_best']],root_neutral_minimum_mu=aggregate['neutral_mu'],
  root_neutral_minimum_mu_proposal_ids=[r['proposal_id'] for r in aggregate['neutral_best']],zero_score_proposal_ids=aggregate['zero_proposal_ids'])


def read_part(part):
 path=(ROOT/part['path']).resolve();need(path.is_relative_to(ROOT) and path.is_file(),'PART_PATH','bounded existing part')
 need(path.stat().st_size==part['gzip_bytes'] and sha(path)==part['gzip_sha256'],'PART_HASH','compressed part identity')
 digest=hashlib.sha256();raw_bytes=0;records=[]
 with gzip.open(path,'rb') as stream:
  while True:
   line=stream.readline(MAX_LINE+1)
   if not line:break
   need(len(line)<=MAX_LINE and line.endswith(b'\n'),'PART_LENGTH','bounded complete JSONL record')
   raw_bytes+=len(line);need(raw_bytes<=part['record_count']*MAX_LINE,'PART_LENGTH','bounded decompression')
   digest.update(line);records.append(json.loads(line))
 need(raw_bytes==part['raw_bytes'] and digest.hexdigest()==part['raw_sha256'] and len(records)==part['record_count'],'PART_HASH','literal part identity')
 need([r['proposal_id'] for r in records]==list(range(part['start'],part['end'])),'PART_SEQUENCE','complete contiguous proposal IDs')
 return records


def enumerate_to(base,out,deadline,identity,limit=None,resume=None,chunk=CHUNK,progress=True):
 out.mkdir(parents=True,exist_ok=False);parts=[];aggregate=accumulator();start=0
 if resume is not None:
  need(resume['schema']==CHECKPOINT_SCHEMA and resume['identity']==identity,'CHECKPOINT_IDENTITY','same frozen input/software')
  for part in resume['parts']:
   need(part['start']==start and part['end']==part['start']+part['record_count'],'PART_SEQUENCE','checkpoint part coverage')
   for record in read_part(part):accumulate(aggregate,record)
   start=part['end'];parts.append(part)
  need(start==resume['next_proposal_id'] and snapshot(aggregate)==resume['aggregate'],'CHECKPOINT_AGGREGATE','prefix metadata reproduced')
 stop=min(base['total'],base['total'] if limit is None else limit);need(0<=start<=stop<=base['total'],'CHECKPOINT_IDENTITY','bounded prefix')
 counter=start;bar=tqdm(total=stop-start,desc='Exact frozen-root two-line proposals',unit='proposal',mininterval=1,disable=not progress)
 checkpoints=[];budget_stop=False
 while counter<stop:
  if deadline is not None and (deadline.status()['stop_required'] or deadline.status()['remaining_seconds']<=20):budget_stop=True;break
  part_start=counter;target=out/f'part_{part_start:09d}.jsonl.gz';digest=hashlib.sha256();raw_bytes=0
  with target.open('xb') as raw_writer:
   with gzip.GzipFile(filename='',fileobj=raw_writer,mode='wb',compresslevel=1,mtime=0) as writer:
    while counter<min(stop,part_start+chunk):
     if (counter-part_start)%1000==0 and deadline is not None and (deadline.status()['stop_required'] or deadline.status()['remaining_seconds']<=20):budget_stop=True;break
     record=proposal(base,counter);line=canonical(record);need(len(line)<=MAX_LINE,'RECORD_LENGTH','record bound')
     writer.write(line);digest.update(line);raw_bytes+=len(line);accumulate(aggregate,record);counter+=1;bar.update(1)
  part=dict(path=target.relative_to(ROOT).as_posix(),start=part_start,end=counter,record_count=counter-part_start,
            raw_bytes=raw_bytes,raw_sha256=digest.hexdigest(),gzip_bytes=target.stat().st_size,gzip_sha256=sha(target));parts.append(part)
  checkpoint=dict(schema=CHECKPOINT_SCHEMA,identity=identity,next_proposal_id=counter,parts=parts,aggregate=snapshot(aggregate))
  checkpoint_path=out/f'checkpoint_{counter:09d}.json';save(checkpoint_path,checkpoint);checkpoints.append(dict(path=checkpoint_path.relative_to(ROOT).as_posix(),sha256=sha(checkpoint_path)))
  if budget_stop:break
 bar.close()
 best=aggregate['best']
 save(out/'best_root_ties.json',dict(records=best,scope='All lambda-preserving minimum-R labelled proposals among saved prefix; complete only if all IDs covered.'))
 save(out/'minimum_mu_ties.json',dict(records=aggregate['mu_best'],scope='All lambda-preserving minimum-mu labelled proposals among saved prefix.'))
 save(out/'root_neutral_minimum_mu_ties.json',dict(records=aggregate['neutral_best'],scope='All lambda-preserving R-neutral minimum-mu labelled proposals among saved prefix; graph counts use literal adjacency toggles, no isomorphism collapse.'))
 selected=None
 if best:
  selected=min(best,key=lambda r:(r['new_mu'],r['proposal_id']));masks=masks_from_record(base,selected);(out/'best_root_neighbor.adj').write_bytes(adjacency_bytes(masks))
  triples=copy_triples(base['triples']);triples[selected['i']]=selected['new_triples'][0];triples[selected['j']]=selected['new_triples'][1]
  save(out/'best_root_neighbor_triples.json',dict(n=base['n'],degree=base['degree'],root=base['root'],frozen_rows=base['frozen_rows'],mutable_labels=base['mutable_labels'],triples=triples,proposal_id=selected['proposal_id']))
 manifest=dict(schema=MANIFEST_SCHEMA,identity=identity,population=base['total'],completed_proposals=counter,
               status='CANDIDATE_COMPLETE_PENDING_INDEPENDENT_CHECK' if counter==base['total'] else 'UNKNOWN_PREFIX_ONLY',
               budget_stop=budget_stop,starting_proposal_id=start,proposals_evaluated_this_invocation=counter-start,
               parts=parts,checkpoints=checkpoints,aggregate=snapshot(aggregate),
               baseline=dict(lambda_energy=base['lambda_energy'],mu_energy=base['mu_energy'],root=base['root'],root_residual=base['root_residual'],frozen_rows=base['frozen_rows'],mutable_labels=base['mutable_labels']),
               selection_rule='among lambda-preserving proposals minimize rootR then mu then proposalID',
               selected_proposal_id=None if selected is None else selected['proposal_id'],independent_approval=False,target_resolution=False,
               limitations=['Labelled one-move proposals between two of the literal non-root triples of ONE saved graph only; no graph-space/global minimum/ergodicity or target exclusion.',
                            'Incomplete prefix cannot establish absence of a descending proposal.','Root diagnostic uses each new graph\'s actual nonneighbors.'])
 save(out/'manifest.json',manifest);return manifest


def copy_triples(triples):return [list(t) for t in triples]


def read_state_graph(raw):
 # Topology projection only. The separately pinned SavedV4 report authenticates full state semantics.
 try:lines=raw.decode('ascii').splitlines()
 except UnicodeError:raise CheckError('STATE_READER','ASCII literal topology projection')
 need(len(lines)>4 and lines[0]==SOURCE_STATE_MAGIC and lines[-1]=='END','STATE_READER','exact state wrapper')
 def at(label):
  found=[i for i,line in enumerate(lines) if line.split(' ',1)[0]==label]
  need(len(found)==1,'STATE_READER','exactly one '+label);return found[0]
 def number(label):
  fields=lines[at(label)].split();need(len(fields)==2 and re.fullmatch(r'0|[1-9][0-9]*',fields[1]) is not None,'STATE_READER','typed '+label);return int(fields[1])
 for key,value in STATE_SCOPES.items():need(lines[at(key)]==key+' '+value,'STATE_READER','unchanged native state scope '+key)
 n,d,r=number('n'),number('degree'),number('root');f=number('frozen');c=number('current')
 fi,mi,ci=at('frozen'),at('mutable'),at('current')
 need(mi==fi+f+1 and ci==mi+1 and ci+c+1<len(lines) and lines[ci+c+1].startswith('best_root '),'STATE_READER','contiguous labelled frozen/mutable/current sections')
 def rows(offset,count,width):
  result=[]
  for line in lines[offset:offset+count]:
   fields=line.split();need(len(fields)==width and all(re.fullmatch(r'0|[1-9][0-9]*',v) is not None for v in fields),'STATE_READER','literal row')
   result.append([int(v) for v in fields])
  need(len(result)==count,'STATE_READER','full row count');return result
 current=rows(ci+1,c,3);frozen=rows(fi+1,f,4);fields=lines[mi].split()
 need(len(fields)>=2 and all(re.fullmatch(r'0|[1-9][0-9]*',v) is not None for v in fields[1:]),'STATE_READER','mutable labels')
 mutable=[int(v) for v in fields[2:]];need(int(fields[1])==len(mutable),'STATE_READER','mutable count')
 base=domain(n,d,current,r)
 need(c*3==n*d and frozen==base['frozen_rows'] and mutable==base['mutable_labels'],'FROZEN_READER','all exact incident/nonincident literal labels')
 return base


def topology_control_bytes(fixture):
 # Synthetic topology-projection fixture, not a complete serialized native RNG/cache state.
 base=domain(**fixture);lines=[SOURCE_STATE_MAGIC]+[k+' '+v for k,v in STATE_SCOPES.items()]
 lines+=['n '+str(base['n']),'degree '+str(base['degree']),'root '+str(base['root']),'frozen '+str(len(base['frozen_rows']))]
 lines+=[' '.join(map(str,row)) for row in base['frozen_rows']]
 lines+=['mutable '+str(len(base['mutable_labels']))+' '+' '.join(map(str,base['mutable_labels'])),'current '+str(len(base['triples']))]
 lines+=[' '.join(map(str,row)) for row in base['triples']]+['best_root 0','END']
 return ('\n'.join(lines)+'\n').encode()


def labelled_id(base,i,j,ix,jy):
 need(all(type(v)is int for v in (i,j,ix,jy)) and 0<=ix<3 and 0<=jy<3,'PROPOSAL_DOMAIN','literal labelled selection')
 need(i in base['mutable_labels'] and j in base['mutable_labels'] and i<j,'FROZEN_UNIVERSE','only two distinct non-root lines in original order')
 return 9*base['pairs'].index((i,j))+3*ix+jy


def engineering(out,deadline,software,source_commit):
 fixtures={
  'rook9':dict(n=9,degree=2,root=0,triples=[[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8]]),
  'prism9':dict(n=9,degree=2,root=8,triples=[[0,2,6],[0,1,7],[1,2,8],[3,5,6],[3,4,7],[4,5,8]]),
  'cube12':dict(n=12,degree=2,root=0,triples=[[0,1,2],[0,3,4],[1,5,6],[3,5,7],[2,8,9],[4,8,10],[6,9,11],[7,10,11]]),
 }
 out.mkdir(parents=True,exist_ok=False);checks=[];results={};negatives=[];evaluation_calls=0;reader_checks=[]
 def reject(label,stage,call,artifact=None):
  if artifact is not None:save(out/(label+'_input.json'),artifact)
  try:call()
  except CheckError as error:need(error.stage==stage,'CONTROL','exact diagnostic '+label);negatives.append(dict(label=label,stage=error.stage,diagnostic=str(error)))
  else:raise CheckError('CONTROL','accepted corruption '+label)
 for name,fixture in fixtures.items():
  save(out/(name+'.json'),fixture);base=domain(**fixture);need(base['total']==(135 if name=='cube12' else 54),'CONTROL','complete tiny mutable proposal universe')
  raw=topology_control_bytes(fixture);(out/(name+'_topology_projection.txt')).write_bytes(raw)
  read=read_state_graph(raw)
  need(read==base,'CONTROL','native-state topology projection exact rebuilt domain/cache');reader_checks.append(name)
  identity=dict(fixture_sha256=sha(out/(name+'.json')),software=software,n=fixture['n'],degree=2,root=fixture['root'],total=base['total'],frozen_rows=base['frozen_rows'],mutable_labels=base['mutable_labels'])
  results[name]=enumerate_to(base,out/(name+'_whole'),deadline,identity,chunk=50,progress=False)
  evaluation_calls+=results[name]['proposals_evaluated_this_invocation']
  for part in results[name]['parts']:
   for record in read_part(part):
    if record['valid']:
     lam,mu,row,_=full_score(masks_from_record(base,record),base['root'])
     need((lam,mu,row)==(record['new_lambda'],record['new_mu'],record['new_root_residual']),'CONTROL','all tiny full rescoring')
    checks.append(dict(fixture=name,proposal_id=record['proposal_id'],valid=record['valid']))
  if name=='rook9':need((base['lambda_energy'],base['mu_energy'])==(0,0),'CONTROL','known exact rook SRG')
  elif name=='prism9':
   known=proposal(base,9);need(known['valid'] and known['new_lambda']==known['new_mu']==0,'CONTROL','known overlapping prism-to-rook trade')
   save(out/'prism_known_overlap_9.json',known)
  prefix=enumerate_to(base,out/(name+'_prefix37'),deadline,identity,limit=37,chunk=50,progress=False)
  evaluation_calls+=prefix['proposals_evaluated_this_invocation']
  checkpoint=json.loads((ROOT/prefix['checkpoints'][-1]['path']).read_bytes())
  resumed=enumerate_to(base,out/(name+'_resumed'),deadline,identity,resume=checkpoint,chunk=50,progress=False)
  evaluation_calls+=resumed['proposals_evaluated_this_invocation']
  whole_records=[r for p in results[name]['parts'] for r in read_part(p)];resume_records=[r for p in resumed['parts'] for r in read_part(p)]
  need(whole_records==resume_records and results[name]['aggregate']==resumed['aggregate'],'CONTROL','complete deterministic split equality')
  bad_checkpoint=json.loads(json.dumps(checkpoint));bad_checkpoint['aggregate']['unique_valid_neighbor_graphs']+=1
  save(out/(name+'_corrupt_checkpoint.json'),bad_checkpoint)
  reject(name+'_checkpoint_aggregate','CHECKPOINT_AGGREGATE',lambda:enumerate_to(base,out/(name+'_negative_resume'),deadline,identity,resume=bad_checkpoint,progress=False))
  bad=dict(base);bad['cn']=[list(row) for row in base['cn']];bad['cn'][0][1]+=1
  reject(name+'_common_cache','CN_CACHE',lambda:cache_check(bad),artifact=bad)
  bad=dict(base);bad['lambda_energy']+=1;reject(name+'_score_cache','ENERGY_CACHE',lambda:cache_check(bad),artifact=bad)
  bad=dict(base);bad['masks']=list(base['masks']);bad['masks'][0]^=1;reject(name+'_adjacency_cache','ADJ_CACHE',lambda:cache_check(bad),artifact=bad)
  cache_check(base)
 bad=copy_triples(fixtures['rook9']['triples']);bad[0][1]=bad[0][0];reject('duplicate_vertex','DOMAIN',lambda:domain(9,2,bad,0),artifact=dict(n=9,degree=2,root=0,triples=bad))
 bad=copy_triples(fixtures['rook9']['triples']);bad[0][0]=9;reject('out_of_range','DOMAIN',lambda:domain(9,2,bad,0),artifact=dict(n=9,degree=2,root=0,triples=bad))
 bad=copy_triples(fixtures['rook9']['triples']);bad[1]=list(bad[0]);reject('duplicate_triple','DOMAIN',lambda:domain(9,2,bad,0),artifact=dict(n=9,degree=2,root=0,triples=bad))
 reject('wrong_point_degree','DEGREE',lambda:domain(9,3,fixtures['rook9']['triples'],0),artifact=dict(n=9,degree=3,root=0,triples=fixtures['rook9']['triples']))
 base=domain(**fixtures['rook9']);reject('out_of_population_proposal','PROPOSAL_DOMAIN',lambda:proposal(base,54))
 for name,fixture in fixtures.items():
  base=domain(**fixture);raw=topology_control_bytes(fixture)
  def damaged(label,stage,old,new):
   need(old in raw,'CONTROL','mutation anchor');bad=raw.replace(old,new,1);(out/(label+'_state.txt')).write_bytes(bad)
   reject(label,stage,lambda:read_state_graph(bad))
  damaged(name+'_reader_magic','STATE_READER',SOURCE_STATE_MAGIC.encode(),b'WRONG_STATE')
  damaged(name+'_reader_duplicate_n','STATE_READER',('n '+str(fixture['n'])+'\n').encode(),('n '+str(fixture['n'])+'\nn '+str(fixture['n'])+'\n').encode())
  damaged(name+'_reader_boolean_n','STATE_READER',('n '+str(fixture['n'])+'\n').encode(),b'n true\n')
  damaged(name+'_reader_wrong_mutable_count','STATE_READER',('mutable '+str(len(base['mutable_labels']))+' ').encode(),('mutable '+str(len(base['mutable_labels'])+1)+' ').encode())
  damaged(name+'_reader_wrong_root','FROZEN_READER',('root '+str(fixture['root'])+'\n').encode(),('root '+str((fixture['root']+1)%fixture['n'])+'\n').encode())
  row=base['frozen_rows'][0];old=(' '.join(map(str,row))+'\n').encode();newrow=row[:];newrow[1],newrow[2]=newrow[2],newrow[1]
  damaged(name+'_reader_reordered_frozen','FROZEN_READER',old,(' '.join(map(str,newrow))+'\n').encode())
  reject(name+'_excluded_frozen_label','FROZEN_UNIVERSE',lambda:labelled_id(base,base['frozen_rows'][0][0],base['mutable_labels'][-1],0,0))
  damaged(name+'_reader_truncated','STATE_READER',b'END\n',b'BROKEN\n')
 save(out/'summary.json',dict(status='AUTHOR_FROZEN_ROOT_TWO_LINE_V1_CONTROLS_PENDING_INDEPENDENT_GATE',timestamp=datetime.now(timezone.utc).isoformat(),
      source_commit=source_commit,command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),tqdm=importlib.metadata.version('tqdm'),fixtures=fixtures,
      unique_complete_proposal_records_checked=len(checks),recorded_proposal_evaluation_calls=evaluation_calls,additional_known_overlap_evaluation_calls=1,
      whole_split_equal=True,strict_negative_count=len(negatives),strict_negatives=negatives,
      new_topology_reader_positive_fixtures=reader_checks,
      known_overlap_proposal=9,software=software,deadline=deadline.status(),independent_approval=False,scientific_census_launched=False))


def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('mode',choices=['controls','census']);ap.add_argument('--out',type=Path,required=True)
 ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--source-commit',required=True);ap.add_argument('--resume',type=Path);ap.add_argument('--resume-sha256')
 ap.add_argument('--input-audit',type=Path);ap.add_argument('--input-audit-sha256');ap.add_argument('--controls-gate',type=Path);ap.add_argument('--controls-gate-sha256')
 args=ap.parse_args();deadline=CommandDeadline(args.seconds,allocation_reason='Exact finite frozen-root two-line proposal census or finite engineering controls; independent checking required')
 out=args.out.resolve();need(out.is_relative_to(ROOT),'PATH','workspace output');software={}
 for name,identity in SOFTWARE.items():need(sha(ROOT/name)==identity,'SOURCE','exact software '+name);software[name]=identity
 for path in [Path(__file__),Path(__file__).with_name('census_20261003_root_focused_two_line_v1_spec.md')]:software[path.relative_to(ROOT).as_posix()]=sha(path)
 if args.mode=='controls':engineering(out,deadline,software,args.source_commit);return
 inputs={}
 for name,identity in [(TARGET_STATE,TARGET_STATE_SHA),(TARGET_MATRIX,TARGET_MATRIX_SHA),(SAVED_AUDIT,SAVED_AUDIT_SHA)]:
  need(sha(ROOT/name)==identity,'SOURCE','exact target input '+name);inputs[name]=identity
 need(args.input_audit is not None and args.input_audit_sha256==SAVED_AUDIT_SHA and args.input_audit.resolve()==ROOT/SAVED_AUDIT,'INPUT_AUDIT','actual exact SavedV4 full report required')
 review=json.loads((ROOT/SAVED_AUDIT).read_bytes())
 need(review.get('status')=='INDEPENDENT_ROOT_FOCUSED_SAVED_OBJECTS_V1_PASS' and review.get('verifier')=='/root/checkpoint_audit'
  and review.get('producer')=='/root/native_driver' and review.get('method')=='independent_artifact_check' and review.get('target_resolution')=='NONE'
  and review.get('saved_state_files')==102 and review.get('complete_trajectory_checked')is False,'INPUT_AUDIT','independent saved-object exact scope/roles')
 for name,identity in [(TARGET_STATE,TARGET_STATE_SHA),(TARGET_MATRIX,TARGET_MATRIX_SHA)]:need(review.get('inputs_sha256',{}).get(name)==identity,'INPUT_AUDIT','independent raw saved-object binding '+name)
 need(args.controls_gate is not None and args.controls_gate_sha256 is not None,'CONTROLS_GATE','new independent finite source gate required')
 gatepath=args.controls_gate.resolve();need(gatepath.is_relative_to(ROOT) and sha(gatepath)==args.controls_gate_sha256,'CONTROLS_GATE','exact new finite report')
 gate=json.loads(gatepath.read_bytes());need(gate.get('status')=='INDEPENDENT_FROZEN_ROOT_TWO_LINE_V1_CONTROLS_PASS' and gate.get('verifier')=='/root/checkpoint_audit'
  and gate.get('producer')=='/root/native_driver' and gate.get('method')=='independent_artifact_check','CONTROLS_GATE','changed source independent scope/roles')
 for name,identity in software.items():need(gate.get('inputs_sha256',{}).get(name)==identity,'CONTROLS_GATE','new finite gate software '+name)
 inputs[gatepath.relative_to(ROOT).as_posix()]=args.controls_gate_sha256
 base=read_state_graph((ROOT/TARGET_STATE).read_bytes())
 need(base['n']==99 and base['degree']==7 and base['root']==11 and len(base['triples'])==231 and base['frozen_rows']==FROZEN_ROWS,'DOMAIN','exact labelled root11 input')
 need(adjacency_bytes(base['masks'])==(ROOT/TARGET_MATRIX).read_bytes(),'DOMAIN','current triples reproduce entire matrix')
 need((base['lambda_energy'],base['mu_energy'],base['root_residual'],base['total'])==(0,5476,10,224784),'DOMAIN','exact frozen objective/domain')
 identity=dict(inputs_sha256=inputs,software=software,n=99,degree=7,root=11,total=224784,source_commit=args.source_commit,
  frozen_rows=base['frozen_rows'],mutable_labels=base['mutable_labels'],proposal_order='lex original mutable labels i<j; selected ix,jy lex;9*pair_index+3*ix+jy',
  question='exists admissible lambda-preserving strictly rootR-descending proposal; mu may worsen; no whole graph-space inference',
  input_selection='ROOT selects current graph among tied rootF10 saved current/best because mu5476<5520; no isomorphism collapse')
 resume=None
 if args.resume is not None:
  need(args.resume_sha256 is not None and sha(args.resume)==args.resume_sha256,'CHECKPOINT_IDENTITY','explicit checkpoint hash');resume=json.loads(args.resume.read_bytes())
 manifest=enumerate_to(base,out,deadline,identity,resume=resume)
 save(out/'run_receipt.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=args.source_commit,command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),
  producer='/root/native_driver',manifest_sha256=sha(out/'manifest.json'),deadline=deadline.status(),independent_approval=False,target_resolution=False,
  overall_search_coverage='UNKNOWN; no validated denominator.'))


if __name__=='__main__':main()

