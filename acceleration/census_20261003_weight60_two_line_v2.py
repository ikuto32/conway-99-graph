"""Exact neutral-neighbor fixed-hypergraph census; unchanged V2 kernel/scorer."""
import argparse
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
TARGET_TRIPLES='acceleration/results/20261003_weight60_two_line_census01/best_neighbor_triples.json'
TARGET_TRIPLES_SHA='11074c406a0b6902e7dcccdd50f1a2e36104a6b964948b3f3fd5299ecdce2968'
TARGET_MATRIX='acceleration/results/20261003_weight60_two_line_census01/best_neighbor.adj'
TARGET_MATRIX_SHA='02d66dc7fb84f91b29be399abe760b452f85b6d79c6c37c681e566e6f4c809bd'
ORIGINAL_MANIFEST='acceleration/results/20261003_weight60_two_line_census01/manifest.json'
ORIGINAL_MANIFEST_SHA='70f4ec893d5ba443effdd29cd6e3d472d736e590af56691b751e822bbae49ffa'
ORIGINAL_CHECKER='acceleration/audit_20261003_two_line_records_v2.py'
ORIGINAL_CHECKER_SHA='d581ea5a2d9ef082aafae5b4de578813d09dc4fd61cb64ee3beaa8b91fa41165'
SOFTWARE={
 'acceleration/command_deadline.py':'9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9',
 'acceleration/run_compute_command.py':'593a9feed6250739dc9672338df23ab171fc9a6a6db4196c1feb312efa33957a',
 'acceleration/native_budget_env_v1/pyproject.toml':'96f96d7345153b4bde50d7f4a640a33d43dfd6458c35f4e6a4ab798b11673782',
 'acceleration/native_budget_env_v1/uv.lock':'54ecb16b929dac1035b5a8691df419d58eab33dc3f07c76c5259094e265a4434',
}
RECORD_SCHEMA='EXACT_V2_TWO_LINE_LABELLED_PROPOSAL_V1'
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
 pairs=[(i,j) for i in range(len(triples)) for j in range(i+1,len(triples))]
 return dict(n=n,degree=degree,triples=triples,root=root,masks=masks,cn=cn,lambda_energy=lam,mu_energy=mu,
             root_residual=row,pairs=pairs,total=len(pairs)*9)


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
             root_residual_delta=None,classification=None)
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
 classification='valid_lambda_changed' if delta_lam else 'valid_lambda_preserving_mu_'+('down' if delta_mu<0 else 'up' if delta_mu>0 else 'equal')
 record.update(valid=True,toggles=[list(edge) for edge in toggles],delta_lambda=delta_lam,delta_mu=delta_mu,
               new_lambda=base['lambda_energy']+delta_lam,new_mu=base['mu_energy']+delta_mu,
               new_root_residual=root_residual,root_residual_delta=root_residual-base['root_residual'],classification=classification)
 return record


def cache_check(base):
 fresh=domain(base['n'],base['degree'],base['triples'],base['root'])
 need(fresh['masks']==base['masks'],'ADJ_CACHE','adjacency cache')
 need(fresh['cn']==base['cn'],'CN_CACHE','common-neighbor cache')
 need(all(fresh[k]==base[k] for k in ['lambda_energy','mu_energy','root_residual']),'ENERGY_CACHE','integer score cache')


def accumulator():return dict(counts=Counter(),unique=set(),best_mu=None,best=[])


def accumulate(aggregate,record):
 aggregate['counts'][record['classification']]+=1
 if record['valid']:
  aggregate['unique'].add(tuple(tuple(e) for e in record['toggles']))
  if record['delta_lambda']==0:
   if aggregate['best_mu'] is None or record['new_mu']<aggregate['best_mu']:aggregate['best_mu']=record['new_mu'];aggregate['best']=[record]
   elif record['new_mu']==aggregate['best_mu']:aggregate['best'].append(record)


def snapshot(aggregate):return dict(counts=dict(sorted(aggregate['counts'].items())),unique_valid_neighbor_graphs=len(aggregate['unique']),best_mu=aggregate['best_mu'],best_proposal_ids=[r['proposal_id'] for r in aggregate['best']])


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
  need(resume['schema']=='EXACT_V2_TWO_LINE_CENSUS_CHECKPOINT_V1' and resume['identity']==identity,'CHECKPOINT_IDENTITY','same frozen input/software')
  for part in resume['parts']:
   need(part['start']==start and part['end']==part['start']+part['record_count'],'PART_SEQUENCE','checkpoint part coverage')
   for record in read_part(part):accumulate(aggregate,record)
   start=part['end'];parts.append(part)
  need(start==resume['next_proposal_id'] and snapshot(aggregate)==resume['aggregate'],'CHECKPOINT_AGGREGATE','prefix metadata reproduced')
 stop=min(base['total'],base['total'] if limit is None else limit);need(0<=start<=stop<=base['total'],'CHECKPOINT_IDENTITY','bounded prefix')
 counter=start;bar=tqdm(total=stop-start,desc='Exact fixed two-line proposals',unit='proposal',mininterval=1,disable=not progress)
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
  checkpoint=dict(schema='EXACT_V2_TWO_LINE_CENSUS_CHECKPOINT_V1',identity=identity,next_proposal_id=counter,parts=parts,aggregate=snapshot(aggregate))
  checkpoint_path=out/f'checkpoint_{counter:09d}.json';save(checkpoint_path,checkpoint);checkpoints.append(dict(path=checkpoint_path.relative_to(ROOT).as_posix(),sha256=sha(checkpoint_path)))
  if budget_stop:break
 bar.close()
 best=aggregate['best'];save(out/'best_ties.json',dict(records=best,scope='All lambda-preserving minimum-mu labelled proposals among saved prefix; complete only if all proposal IDs covered.'))
 selected=None
 if best:
  selected=best[0];masks=masks_from_record(base,selected);(out/'best_neighbor.adj').write_bytes(adjacency_bytes(masks))
  triples=copy_triples(base['triples']);triples[selected['i']]=selected['new_triples'][0];triples[selected['j']]=selected['new_triples'][1]
  save(out/'best_neighbor_triples.json',dict(n=base['n'],degree=base['degree'],triples=triples,proposal_id=selected['proposal_id']))
 manifest=dict(schema='EXACT_V2_TWO_LINE_CENSUS_MANIFEST_V1',identity=identity,population=base['total'],completed_proposals=counter,
               status='CANDIDATE_COMPLETE_PENDING_INDEPENDENT_CHECK' if counter==base['total'] else 'UNKNOWN_PREFIX_ONLY',
               budget_stop=budget_stop,starting_proposal_id=start,proposals_evaluated_this_invocation=counter-start,
               parts=parts,checkpoints=checkpoints,aggregate=snapshot(aggregate),
               baseline=dict(lambda_energy=base['lambda_energy'],mu_energy=base['mu_energy'],root=base['root'],root_residual=base['root_residual']),
               selected_proposal_id=None if selected is None else selected['proposal_id'],independent_approval=False,target_resolution=False,
               limitations=['Labelled one-move proposals of one frozen hypergraph only; no unrestricted graph coverage/global minimum/ergodicity.',
                            'Incomplete prefix cannot establish absence of a descending proposal.','Root diagnostic uses each new graph\'s actual nonneighbors.'])
 save(out/'manifest.json',manifest);return manifest


def copy_triples(triples):return [list(t) for t in triples]


def read_graph_object(data,root):
 need(type(data) is dict and all(key in data for key in ['n','degree','triples']),'GRAPH_READER','typed full triple object')
 return domain(data['n'],data['degree'],data['triples'],root)


def engineering(out,deadline,software,source_commit):
 fixtures={
  'rook9':dict(n=9,degree=2,root=0,triples=[[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8]]),
  'prism9':dict(n=9,degree=2,root=0,triples=[[0,2,6],[0,1,7],[1,2,8],[3,5,6],[3,4,7],[4,5,8]]),
 }
 out.mkdir(parents=True,exist_ok=False);checks=[];results={};negatives=[];evaluation_calls=0;reader_checks=[]
 def reject(label,stage,call,artifact=None):
  if artifact is not None:save(out/(label+'_input.json'),artifact)
  try:call()
  except CheckError as error:need(error.stage==stage,'CONTROL','exact diagnostic '+label);negatives.append(dict(label=label,stage=error.stage,diagnostic=str(error)))
  else:raise CheckError('CONTROL','accepted corruption '+label)
 for name,fixture in fixtures.items():
  save(out/(name+'.json'),fixture);base=domain(**fixture);need(base['total']==135,'CONTROL','complete tiny proposal universe')
  read=read_graph_object(dict(n=fixture['n'],degree=fixture['degree'],triples=copy_triples(fixture['triples'])),fixture['root'])
  need(read==base,'CONTROL','new JSON input-reader exact domain/cache');reader_checks.append(name)
  identity=dict(fixture_sha256=sha(out/(name+'.json')),software=software,n=9,degree=2,root=0,total=135)
  results[name]=enumerate_to(base,out/(name+'_whole'),deadline,identity,chunk=50,progress=False)
  evaluation_calls+=results[name]['proposals_evaluated_this_invocation']
  for part in results[name]['parts']:
   for record in read_part(part):
    if record['valid']:
     lam,mu,row,_=full_score(masks_from_record(base,record),base['root'])
     need((lam,mu,row)==(record['new_lambda'],record['new_mu'],record['new_root_residual']),'CONTROL','all tiny full rescoring')
    checks.append(dict(fixture=name,proposal_id=record['proposal_id'],valid=record['valid']))
  if name=='rook9':need((base['lambda_energy'],base['mu_energy'])==(0,0),'CONTROL','known exact rook SRG')
  else:
   known=proposal(base,18);need(known['valid'] and known['new_lambda']==known['new_mu']==0,'CONTROL','known overlapping prism-to-rook trade')
   save(out/'prism_known_overlap_18.json',known)
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
 base=domain(**fixtures['rook9']);reject('out_of_population_proposal','PROPOSAL_DOMAIN',lambda:proposal(base,135))
 reject('reader_missing_triples','GRAPH_READER',lambda:read_graph_object(dict(n=9,degree=2),0),artifact=dict(n=9,degree=2))
 reject('reader_boolean_n','DOMAIN',lambda:read_graph_object(dict(n=True,degree=2,triples=fixtures['rook9']['triples']),0),artifact=dict(n=True,degree=2,triples=fixtures['rook9']['triples']))
 reject('reader_boolean_degree','DOMAIN',lambda:read_graph_object(dict(n=9,degree=True,triples=fixtures['rook9']['triples']),0),artifact=dict(n=9,degree=True,triples=fixtures['rook9']['triples']))
 bad=copy_triples(fixtures['rook9']['triples']);bad[0][0]=False
 reject('reader_boolean_vertex','DOMAIN',lambda:read_graph_object(dict(n=9,degree=2,triples=bad),0),artifact=dict(n=9,degree=2,triples=bad))
 save(out/'summary.json',dict(status='AUTHOR_TWO_LINE_CENSUS_V2_CONTROLS_PENDING_INDEPENDENT_GATE',timestamp=datetime.now(timezone.utc).isoformat(),
      source_commit=source_commit,command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),tqdm=importlib.metadata.version('tqdm'),fixtures=fixtures,
      unique_complete_proposal_records_checked=len(checks),recorded_proposal_evaluation_calls=evaluation_calls,additional_known_overlap_evaluation_calls=1,
      whole_split_equal=True,strict_negative_count=len(negatives),strict_negatives=negatives,
      new_typed_reader_positive_fixtures=reader_checks,
      known_overlap_proposal=18,software=software,deadline=deadline.status(),independent_approval=False,scientific_census_launched=False))


def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('mode',choices=['controls','census']);ap.add_argument('--out',type=Path,required=True)
 ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--source-commit',required=True);ap.add_argument('--resume',type=Path);ap.add_argument('--resume-sha256')
 ap.add_argument('--input-audit',type=Path);ap.add_argument('--input-audit-sha256')
 args=ap.parse_args();deadline=CommandDeadline(args.seconds,allocation_reason='Exact finite fixedgraph two-line proposal census or finite engineering controls; independent checking required')
 out=args.out.resolve();need(out.is_relative_to(ROOT),'PATH','workspace output');software={}
 for name,identity in SOFTWARE.items():need(sha(ROOT/name)==identity,'SOURCE','exact software '+name);software[name]=identity
 for path in [Path(__file__),Path(__file__).with_name('census_20261003_weight60_two_line_v2_spec.md')]:software[path.relative_to(ROOT).as_posix()]=sha(path)
 if args.mode=='controls':engineering(out,deadline,software,args.source_commit);return
 inputs={}
 for name,identity in [(TARGET_TRIPLES,TARGET_TRIPLES_SHA),(TARGET_MATRIX,TARGET_MATRIX_SHA),(ORIGINAL_MANIFEST,ORIGINAL_MANIFEST_SHA),(ORIGINAL_CHECKER,ORIGINAL_CHECKER_SHA)]:
  need(sha(ROOT/name)==identity,'SOURCE','exact target input '+name);inputs[name]=identity
 need(args.input_audit is not None and args.input_audit_sha256 is not None,'INPUT_AUDIT','actual independent original complete census report required')
 input_audit=args.input_audit.resolve();need(input_audit.is_relative_to(ROOT) and sha(input_audit)==args.input_audit_sha256,'INPUT_AUDIT','exact original complete report')
 review=json.loads(input_audit.read_bytes());need(review.get('status')=='INDEPENDENT_TWO_LINE_COMPLETE_FIXED_GRAPH_CENSUS_V2_PASS'
   and review.get('verifier')=='/root' and review.get('producer')=='/root/native_driver' and review.get('method')=='independent_artifact_check'
   and review.get('complete_proposals_checked')==239085 and review.get('complete_universe') is True and review.get('target_resolution')=='NONE','INPUT_AUDIT','independent finite exact scope/roles')
 for name,identity in [(TARGET_TRIPLES,TARGET_TRIPLES_SHA),(TARGET_MATRIX,TARGET_MATRIX_SHA),(ORIGINAL_MANIFEST,ORIGINAL_MANIFEST_SHA),(ORIGINAL_CHECKER,ORIGINAL_CHECKER_SHA)]:
  need(review.get('inputs_sha256',{}).get(name)==identity,'INPUT_AUDIT','independent source/raw artifact binding '+name)
 inputs[input_audit.relative_to(ROOT).as_posix()]=args.input_audit_sha256
 data=json.loads((ROOT/TARGET_TRIPLES).read_bytes());need(data.get('proposal_id')==68908,'DOMAIN','exact declared neutral labelled input')
 base=read_graph_object(data,11);need(base['n']==99 and base['degree']==7 and len(base['triples'])==231,'DOMAIN','complete target-sized triple input')
 need(adjacency_bytes(base['masks'])==(ROOT/TARGET_MATRIX).read_bytes(),'DOMAIN','triples reproduce entire matrix')
 need((base['lambda_energy'],base['mu_energy'],base['root_residual'],base['total'])==(0,3480,52,239085),'DOMAIN','exact frozen objective/domain')
 identity=dict(inputs_sha256=inputs,software=software,n=99,degree=7,root=11,total=239085,source_commit=args.source_commit,
               proposal_order='unordered triplepairs i<j lex; selected positions ix,jy lex;9*pair_index+3*ix+jy')
 resume=None
 if args.resume is not None:
  need(args.resume_sha256 is not None and sha(args.resume)==args.resume_sha256,'CHECKPOINT_IDENTITY','explicit checkpoint hash')
  resume=json.loads(args.resume.read_bytes())
 manifest=enumerate_to(base,out,deadline,identity,resume=resume)
 save(out/'run_receipt.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=args.source_commit,command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),
      producer='/root/native_driver',manifest_sha256=sha(out/'manifest.json'),deadline=deadline.status(),independent_approval=False,target_resolution=False,
      overall_search_coverage='UNKNOWN; no validated denominator.'))


if __name__=='__main__':main()
