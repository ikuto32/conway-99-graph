"""Independent saved root-focused objects/scalar/sparse audit; no native launches."""
import argparse
import copy
from datetime import datetime,timezone
import json
import math
from pathlib import Path
import platform
import sys
from tqdm import tqdm
from command_deadline import CommandDeadline
import audit_20261003_root_focused_core_v2 as C
import audit_20261003_root_focused_engine_v4 as E

ROOT=E.ROOT
CODE=[*E.CODE,'acceleration/audit_20261003_root_focused_saved_objects_v4.py','acceleration/audit_20261003_root_focused_saved_objects_v4_spec.md']

def input_gate(gate,name,h):
 C.need(type(gate)is dict and gate.get('status')=='INDEPENDENT_ROOT_FOCUSED_GRAPH_INPUT_V1_PASS'and gate.get('method')=='independent_artifact_check'and gate.get('verifier')=='/root'and gate.get('inputs_sha256',{}).get(name)==h,'exact separate ROOT rawinput gate','INPUT_GATE')

def population(records,start,end,maximum,stride):
 C.need(all(type(v)is int and v>=0 for v in [start,end,maximum,stride])and start<=end,'literal sparse population parameters','POPULATION')
 chosen=set(range(start,min(end,start+maximum)))
 if stride:chosen.update(range(((start+stride-1)//stride)*stride,end,stride))
 C.need([r['step']for r in records]==sorted(chosen),'complete frozen sparse trace selection','POPULATION')

def local_trace(record,initial):
 template=C.transition(copy.deepcopy(initial))[0]
 C.need(type(record)is dict and set(record)==set(template),'complete local trace schema','LOCAL_TRACE')
 for name in ['trace_schema','objective','distribution','root']:C.need(type(record[name])is type(template[name])and record[name]==template[name],'literal local '+name,'LOCAL_TRACE')
 C.need(record['probe']is False,'scientific trace has no fixture probes','LOCAL_TRACE')
 for name in ['ti','tj','pi','pj','step','selection_draws','local_updates','delta_F','delta_lambda','delta_mu','delta_root','F_before','lambda_before','mu_before','root_before','F_after','lambda_after','mu_after','root_after','best_F']:C.need(type(record[name])is int,'literal local integer '+name,'LOCAL_TRACE')
 m=len(initial['current']);C.need(0<=record['ti']<m and 0<=record['tj']<m and record['ti']!=record['tj']and record['pi']in range(3)and record['pj']in range(3)and record['step']>=initial['step'],'local proposal indices/step','LOCAL_TRACE')
 for name in ['frozen_line_selected','disjoint','selected_points_exclusive','new_pairs_absent_after_old_removal','admissible','accepted','mixing','first_localzero_before','first_localzero_after']:C.need(type(record[name])is bool,'literal local Boolean '+name,'LOCAL_TRACE')
 for name in ['old_triples','proposed_triples']:C.need(type(record[name])is list and len(record[name])==2 and all(type(t)is list and len(t)==3 and all(type(v)is int and 0<=v<initial['n']for v in t)for t in record[name]),'literal local triple rows','LOCAL_TRACE')
 t,q=record['old_triples'];C.need(len(set(t))==len(set(q))==3 and len(set(t)&set(q))<=1,'local linear old lines','LOCAL_TRACE')
 pt,pq=t[:],q[:];x,y=t[record['pi']],q[record['pj']];pt[record['pi']],pq[record['pj']]=y,x
 frozen=record['ti']not in initial['mutable']or record['tj']not in initial['mutable'];exclusive=x not in q and y not in t;absent=record['new_pairs_absent_after_old_removal'];valid=not frozen and exclusive and absent
 reason='frozen_root_line'if frozen else'selected_point_not_exclusive'if not exclusive else'new_pair_conflict'if not absent else'NONE'
 C.need(record['proposed_triples']==[pt,pq]and record['frozen_line_selected']==frozen and record['disjoint']==(not bool(set(t)&set(q)))and record['selected_points_exclusive']==exclusive and record['admissible']==valid and record['invalid_reason']==reason,'local literal swap/veto predicate','LOCAL_TRACE')
 C.need(not frozen,'ordinary bounded sampling selects only mutable labels','LOCAL_TRACE')
 for suffix in ['before','after']:
  el,em,rr=record['lambda_'+suffix],record['mu_'+suffix],record['root_'+suffix];C.need(el>=0 and em>=0 and rr>=0 and record['F_'+suffix]==60*el+rr,'local exact objective components','COMPONENT')
 C.need(0<=record['best_F']<=record['F_after']and record['local_updates']>=0,'local minimum/counter domain','COMPONENT')
 for name in ['rng_before','rng_after']:C.need(type(record[name])is list and len(record[name])==4 and all(type(v)is str for v in record[name]),'four decimal RNG strings','LOCAL_RNG')
 before=[C.integer(v,'LOCAL_RNG',True)for v in record['rng_before']];after=[C.integer(v,'LOCAL_RNG',True)for v in record['rng_after']];C.need(any(before)and any(after),'local nonzero RNG','LOCAL_RNG');words=before[:];draws=0
 size=len(initial['mutable']);mi,k=C.bounded(lambda:C.rng_next(words),size);draws+=k;mj,k=C.bounded(lambda:C.rng_next(words),size-1);draws+=k;mj+=int(mj>=mi);pi,k=C.bounded(lambda:C.rng_next(words),3);draws+=k;pj,k=C.bounded(lambda:C.rng_next(words),3);draws+=k;draw=C.rng_next(words)if valid else 0
 C.need([initial['mutable'][mi],initial['mutable'][mj],pi,pj]==[record[k]for k in ['ti','tj','pi','pj']]and words==after and record['selection_draws']==draws and type(record['draw'])is str and record['draw']==str(draw),'exact local bounded RNG and valid acceptance word','LOCAL_RNG')
 fraction=min(1.,float(max(0,record['step']-initial['mix_steps']))/initial['schedule_steps']);temp=initial['t_start']+(initial['t_end']-initial['t_start'])*fraction
 C.need(type(record['temperature'])in[int,float]and math.isfinite(record['temperature'])and abs(record['temperature']-temp)<=C.TOL,'exact local temperature tolerance','LOCAL_TEMPERATURE');C.need(record['mixing']==(record['step']<initial['mix_steps']),'local schedule stage','LOCAL_TRACE')
 accepted=False
 if valid:
  if initial['forced']or record['mixing']or record['delta_F']<=0:accepted=True
  elif temp>0:
   p=math.exp(-float(record['delta_F'])/temp);u=(draw>>11)*2**-53;C.need(abs(u-p)>C.TOL,'unambiguous local floating acceptance','FLOAT');accepted=u<p
 C.need(record['accepted']==accepted,'recorded local acceptance','LOCAL_TRACE')
 for value,delta in [('F','F'),('lambda','lambda'),('mu','mu'),('root','root')]:
  C.need(record[value+'_after']-record[value+'_before']==(record['delta_'+delta]if accepted else 0),'exact local accepted/rejected components','COMPONENT')
 C.need(record['delta_F']==60*record['delta_lambda']+record['delta_root'],'literal local delta objective','COMPONENT')
 if not valid:C.need(all(record['delta_'+v]==0 for v in ['F','lambda','mu','root'])and record['draw']=='0','invalid zero delta/draw','LOCAL_TRACE')
 C.need(not record['first_localzero_before']or record['first_localzero_after'],'immutable observed first flag','LOCAL_FIRST')
 if not record['first_localzero_before']:C.need(record['first_localzero_after']==(record['F_after']==0),'new observed localzero flag','LOCAL_FIRST')

def anchored(records,initial,states,deadline):
 frontier=None;checked=[];gaps=[]
 for record in records:
  C.need(deadline.status()['remaining_seconds']>20,'sparse checking save reserve','DEADLINE');local_trace(record,initial)
  if frontier is not None and frontier['step']==record['step']:s=frontier
  elif record['step']in states:s=copy.deepcopy(states[record['step']])
  else:gaps.append(record['step']);frontier=None;continue
  C.replay(s,record);checked.append(record['step']);frontier=s
  if s['step']in states:C.need(s==states[s['step']],'literal next complete saved anchor','ANCHOR')
 return checked,gaps

def calibration(out,d):
 records=[]
 def positive(name,fn):fn();records.append(dict(case=name,outcome='PASS'))
 def negative(name,stage,fn):
  try:fn()
  except C.CheckError as e:C.need(e.stage==stage,'designated saved control '+name+': '+str(e),'CALIBRATION');records.append(dict(case=name,outcome='REJECTED',stage=stage));return
  raise C.CheckError('CALIBRATION','false acceptance '+name)
 initial=C.initial('rook9',0,seed=182,temp=16,forced=True);s=copy.deepcopy(initial);states={0:copy.deepcopy(s)};trace=[]
 for _ in range(12):trace.append(C.transition(s)[0]);states[s['step']]=copy.deepcopy(s)
 positive('known rook fullscalar four object categories',lambda:C.need(all(r['srg_valid']for r in C.scalar_objects(initial).values()),'rook exact identity','CALIBRATION'))
 positive('complete12 local RNG and complete anchored replay',lambda:C.need(anchored(trace,initial,states,d)==([*range(12)],[]),'full finite anchors','CALIBRATION'))
 sparse=[trace[0],trace[1],trace[4],trace[8]];population(sparse,0,12,2,4)
 positive('explicit sparse gaps are unverified globally',lambda:C.need(anchored(sparse,initial,{0:initial},d)==([0,1],[4,8]),'never bridge absent global state','CALIBRATION'))
 negative('omitted sparse record','POPULATION',lambda:population(sparse[:-1],0,12,2,4))
 b=copy.deepcopy(sparse);b[-1]['step']=9;negative('wrong sparse step','POPULATION',lambda:population(b,0,12,2,4))
 b=copy.deepcopy(initial);b['rng'][0]^=1;negative('wrong full anchor RNG','TRACE',lambda:anchored(trace,initial,{0:b},d))
 b=copy.deepcopy(states[1]);b['accepted']+=1;negative('wrong following full anchor','ANCHOR',lambda:anchored(trace,initial,{0:initial,1:b},d))
 actual=next(r for r in trace if r['admissible']);C.need(actual['accepted']is True,'forced valid component control','CALIBRATION')
 for key,value,stage in [('rng_before',['0']*4,'LOCAL_RNG'),('rng_after',['0']*4,'LOCAL_RNG'),('rng_after',[0]*4,'LOCAL_RNG'),('draw',str(int(actual['draw'])+1),'LOCAL_RNG'),('selection_draws',actual['selection_draws']+1,'LOCAL_RNG'),('temperature',actual['temperature']+1,'LOCAL_TEMPERATURE'),('accepted',not actual['accepted'],'LOCAL_TRACE'),('delta_mu',actual['delta_mu']+1,'COMPONENT'),('first_localzero_after',False,'LOCAL_FIRST'),('F_after',actual['F_after']+1,'COMPONENT')]:
  r=copy.deepcopy(actual);r[key]=value;negative('mutated sparse '+key+' '+str(value),stage,lambda:local_trace(r,initial))
 raw=C.matrix_bytes(C.graph(C.fixture('rook9'),9,2,0))
 for name,change in [('loop',lambda a:a[1].__setitem__(0,'1')),('asymmetric',lambda a:a[1].__setitem__(1,'0')),('binary',lambda a:a[1].__setitem__(1,'2')),('shape',lambda a:a.pop())]:
  lines=[list(s)for s in raw.decode().splitlines()];change(lines);bad=('\n'.join(''.join(s)for s in lines)+'\n').encode();negative('rawmatrix '+name,'MATRIX',lambda:C.scalar_matrix(bad,9,2,0))
 negative('local rook zero not99 SRG','MATRIX',lambda:C.target_zero(raw,0))
 negative('Boolean zero invalid','TARGET_ZERO',lambda:C.target_zero(raw,False))
 target=C.initial('target99',11);positive('full99 valid incidence nonSRG scalar control',lambda:C.need(C.scalar_objects(target)['current']['identity_mismatches']>0,'finite targetdomain nonzero','CALIBRATION'))
 negative('numerical claimed zero on complete99 nonSRG','TARGET_ZERO',lambda:C.target_zero(C.matrix_bytes(C.graph(target['current'],99,7,11)),0))
 g=dict(status='INDEPENDENT_ROOT_FOCUSED_GRAPH_INPUT_V1_PASS',method='independent_artifact_check',verifier='/root',inputs_sha256={'example/graph_input.txt':'1'*64})
 positive('explicit input gate independent of report filename',lambda:input_gate(g,'example/graph_input.txt','1'*64))
 for name,k,v in [('role','verifier','/root/checkpoint_audit'),('status','status','UNKNOWN'),('method','method','repeated_execution'),('rawhash','inputs_sha256',{'example/graph_input.txt':'0'*64})]:
  bad=copy.deepcopy(g);bad[k]=v;negative('inputgate '+name,'INPUT_GATE',lambda:input_gate(bad,'example/graph_input.txt','1'*64))
 E.write(out/'controls.json',records)
 return dict(status='INDEPENDENT_ROOT_FOCUSED_SAVED_OBJECTS_V1_CALIBRATION_PASS',positive_controls=sum(r['outcome']=='PASS'for r in records),strict_negative_controls=sum(r['outcome']=='REJECTED'for r in records),controls_sha256=E.sha(out/'controls.json'),scientific_outputs_checked=False,known_valid_target_graph=None,known_valid_target_graph_reason='No known complete99target fixture; generic rook9 and deliberately nonSRG complete99domain controls only.')

def full(a,out,pin,d,sourcepins):
 C.need(all([a.run_summary,a.run_summary_sha256,a.calibration,a.calibration_sha256,a.engine_gate,a.engine_gate_sha256,a.supervisor,a.supervisor_sha256,a.input_gate,a.input_gate_sha256]),'exact outcome/calibration/engineering/inputgate/supervisor identities','IDENTITY')
 pin(a.calibration,a.calibration_sha256);cal=json.loads(E.local(a.calibration).read_bytes());C.need(cal['status']=='INDEPENDENT_ROOT_FOCUSED_SAVED_OBJECTS_V1_CALIBRATION_PASS'and all(cal['inputs_sha256'].get(k)==v for k,v in sourcepins.items()),'unchanged pre-output saved source closure','IDENTITY')
 pin(a.engine_gate,a.engine_gate_sha256);gate=json.loads(E.local(a.engine_gate).read_bytes());C.need(gate['status']=='INDEPENDENT_ROOT_FOCUSED_ENGINE_V1_CONTROLS_PASS'and gate['verifier']=='/root/checkpoint_audit','exact independent finite engineering gate','IDENTITY')
 for k in sourcepins:
  if k in gate['inputs_sha256']:C.need(gate['inputs_sha256'][k]==sourcepins[k],'same engine/helper source','IDENTITY')
 pin(a.run_summary,a.run_summary_sha256);summary=json.loads(E.local(a.run_summary).read_bytes());base=E.local(a.run_summary).parent;pin((base/'protocol.json').relative_to(ROOT).as_posix());protocol=json.loads((base/'protocol.json').read_bytes());C.need(summary['status']=='ROOT_FOCUSED_RUN_COMPLETE_PENDING_INDEPENDENT_CHECK'and summary['independent_approval']is False and summary['target_resolution']is False and protocol['schema']=='ROOT_FOCUSED_RUN_PROTOCOL_V1'and protocol['inputs_sha256']==summary['inputs_sha256']and protocol['objective']==C.OBJECTIVE and protocol['distribution']==C.DISTRIBUTION,'literal prospective/run scope','RECEIPT')
 for name,h in summary['inputs_sha256'].items():pin(name,h)
 for name in [*E.CODE,*json.loads(E.local(E.PLAN).read_bytes())['source_inputs_sha256'],json.loads(E.local(E.BUILD).read_bytes())['binary_path'],E.BUILD]:C.need(gate['inputs_sha256'].get(name)==sourcepins.get(name),'exact source/build approved closure','IDENTITY')
 C.need(summary['inputs_sha256'].get(a.engine_gate)==a.engine_gate_sha256 and summary['inputs_sha256'].get(a.calibration)==a.calibration_sha256,'actual producer admitted exact two independent gates','IDENTITY')
 invocation_name=(base/'invocation.json').relative_to(ROOT).as_posix();pin(invocation_name);invocation=json.loads(E.local(invocation_name).read_bytes());outer,outer_manifest,outer_summary=E.supervision(invocation,pin);C.need(invocation['mode']=='run'and invocation['source_commit']==protocol['source_commit']and invocation['command'][1]=='acceleration/prepare_20261003_hypergraph_root_focused_v3.py','actual new scientific wrapper invocation/source identity','RECEIPT')
 pin(a.supervisor,a.supervisor_sha256);supervisor=json.loads(E.local(a.supervisor).read_bytes());cl=supervisor['cleanup'];C.need(supervisor['command_exit_code']==0 and cl['reaped']is True and cl['job_active_zero_observed']is True and cl['cleanup_errors']==[]and cl.get('process_group_live_pids',[])==[],'observed terminal contained process outcome','RECEIPT')
 C.need(E.local(a.supervisor)==E.local(outer['path']).parent/'summary.json'and supervisor==outer_summary,'caller hash binds actual native enclosing supervisor','RECEIPT')
 row=summary['raw'];pin(row['receipt'],row['receipt_sha256']);receipt=json.loads(E.local(row['receipt']).read_bytes());C.need(receipt['actual_exit_code']==receipt['expected_exit_code']==row['actual_exit_code']==0 and receipt['reaped']is True and receipt['error']is None and row['options']==protocol['options']and receipt['command'][-len(row['options']):]==row['options'],'actual native outcome/options','RECEIPT')
 command=receipt['command'];C.need(command[:4]==['/usr/bin/timeout','--foreground','--signal=TERM','--kill-after=5s']and command[4].endswith('s'),'actual scientific native foreground guard','RECEIPT');seconds=float(command[4][:-1]);C.need(math.isfinite(seconds)and 0<seconds<=outer['outer_seconds'],'scientific guard within outer allocation','RECEIPT')
 binary=json.loads(E.local(E.BUILD).read_bytes())['binary_path'];native_path=(base/'native').relative_to(ROOT).as_posix();expected=['/usr/bin/prlimit',f"--as={invocation['address_space_bytes']}:{invocation['address_space_bytes']}",f"--fsize={invocation['file_bytes']}:{invocation['file_bytes']}",'--core=0:0',E.linux(binary),'--out',E.linux(native_path),'--seconds',f'{max(.001,seconds-5):.6f}'];C.need(command[5:14]==expected and command[14:]==row['options']and receipt['cwd']==E.linux('acceleration')[:-len('/acceleration')]and receipt['process_group']==outer['group'],'scientific exact gated binary/resources/output/workingdirectory/group','RECEIPT')
 for channel in ['stdout','stderr']:pin(receipt[channel],receipt[channel+'_sha256'])
 native=base/'native';C.need({p.relative_to(ROOT).as_posix()for p in native.iterdir()if p.is_file()}==set(row['artifacts']),'complete actual saved file population','POPULATION')
 for name,r in row['artifacts'].items():pin(name,r['sha256'],r['bytes'])
 opts=E.options(row['options']);inputname=E.local(opts.get('--graph-input')or opts.get('--frozen-reference')).relative_to(ROOT).as_posix();pin(inputname,opts['--graph-identity']);decoded=C.parse_graph_input(E.local(inputname).read_bytes());C.need((decoded['n'],decoded['degree'],decoded['root'])==(99,7,11),'complete targetdomain raw input scope','DOMAIN');original=decoded['triples'];provenance=decoded['provenance']
 pin(a.input_gate,a.input_gate_sha256);C.need(summary['inputs_sha256'].get(a.input_gate)==a.input_gate_sha256,'actual native admission used exact input gate','INPUT_GATE');input_gate(json.loads(E.local(a.input_gate).read_bytes()),inputname,opts['--graph-identity'])
 configs={};states={};reports=[];allzero=[]
 for path in tqdm(sorted(native.glob('*.state')),desc='Independent saved full scalar matrices',unit='state',mininterval=1):
  C.need(d.status()['remaining_seconds']>20,'full object checking save reserve','DEADLINE');s=C.parse_state(path.read_bytes(),original);C.reference_check(s,original,provenance);C.need((s['n'],s['degree'],s['root'])==(99,7,11),'all complete saved raw99objects','DOMAIN');currentconfig={k:s[k]for k in C.CONFIG}
  if not configs:configs=currentconfig
  C.need(configs==currentconfig,'same exact saved configuration/provenance','CONFIG')
  if s['step']in states:C.need(states[s['step']]==s,'duplicate same-step full state equality','ANCHOR')
  states[s['step']]=s;result=C.scalar_objects(s);reports.append(dict(path=path.relative_to(ROOT).as_posix(),step=s['step'],full_scalar_objects=result))
  for selector,rows in [('current',s['current']),('best_root',s['best_root'])]+[(k,s[k]['triples'])for k in ['first_localzero','best_localzero_mu']if s[k]is not None]:
   if result[selector]['lambda_energy']==result[selector]['root_residual']==0:allzero.append(dict(path=path.relative_to(ROOT).as_posix(),selector=selector,mu_energy=result[selector]['mu_energy'],step=s['step']))
 initial=C.parse_state((native/'initial.state').read_bytes(),original);final=C.parse_state((native/'final.state').read_bytes(),original);C.need(min(states)==initial['step']and max(states)==final['step'],'saved initial/final range','ANCHOR');E.header_check((native/'initial.state').read_bytes(),opts,provenance)
 if '--resume'in opts:C.need(initial==C.parse_state(E.local(opts['--resume']).read_bytes(),original),'exact literal resume object','RESUME')
 else:
  expected=C.initial('target99',11,seed=int(opts['--seed']),temp=float(opts['--temperature-start']),end=float(opts['--temperature-end']),mix=int(opts['--mix-steps']),schedule=int(opts['--schedule-steps']),checkpoint=int(opts['--checkpoint-every']),provenance=provenance,triples=original);C.need(initial==expected,'newinput reset full counters/RNG/snapshots','INITIAL')
 for earlier,later in zip([states[j]for j in sorted(states)],[states[j]for j in sorted(states)][1:]):
  C.need(all(earlier[k]<=later[k]for k in C.COUNTERS)and earlier['best_root_energy']>=later['best_root_energy'],'observed saved monotone counters/minimum','ANCHOR')
  if earlier['first_localzero']is not None:C.need(earlier['first_localzero']==later['first_localzero']and C.graph(earlier['best_localzero_mu']['triples'],99,7,11)['mu_energy']>=C.graph(later['best_localzero_mu']['triples'],99,7,11)['mu_energy'],'immutable first and observed retained mu ordering','RETENTION')
 every=int(opts['--checkpoint-every']);C.need(set(range(((initial['step']//every)+1)*every,final['step']+1,every))<=set(states),'all scheduled step checkpoints saved','POPULATION')
 objects={};snapshotcounts={}
 for path in sorted(native.glob('*.object')):
  o=C.parse_selected(path.read_bytes(),final);g=C.graph(o['triples'],99,7,11);r=C.scalar_matrix(C.matrix_bytes(g),99,7,11);C.need(all(r[k]==g[k]for k in C.SCORES),'selected full scalar/set identity','MATRIX');objects[path.name]=o;allzero.append(dict(path=path.relative_to(ROOT).as_posix(),selector='selected',mu_energy=r['mu_energy'],step=o['step']));reports.append(dict(path=path.relative_to(ROOT).as_posix(),step=o['step'],full_scalar_objects={'selected':r}))
  if path.name.startswith('retained_'):
   prefix='retained_first_localzero_'if o['reason']in['initial','first_localzero']else'retained_localzero_mu_';C.need(path.name==prefix+str(o['step'])+'.object','literal immediate snapshot filename/reason','RETENTION');snapshotcounts[o['reason']]=snapshotcounts.get(o['reason'],0)+1
 for name,selector in [('current.adj','current'),('best_root.adj','best_root')]:C.need((native/name).read_bytes()==C.matrix_bytes(C.graph(final[selector],99,7,11)),'raw final current/best matrix bytes','MATRIX')
 C.need(('first_localzero.object'in objects)==('best_localzero_mu.object'in objects)==(final['first_localzero']is not None),'final retained file population','RETENTION')
 if final['first_localzero']is not None:
  for selector in ['first_localzero','best_localzero_mu']:
   C.need(objects[selector+'.object']==final[selector]and (native/(selector+'.adj')).read_bytes()==C.matrix_bytes(C.graph(final[selector]['triples'],99,7,11)),'literal final retained object/matrix','RETENTION')
  C.need(min(v['mu_energy']for v in allzero)==C.graph(final['best_localzero_mu']['triples'],99,7,11)['mu_energy'],'minimum over explicit actually saved localzero population','RETENTION')
 traces=[json.loads(line)for line in (native/'moves.jsonl').read_bytes().splitlines()];population(traces,initial['step'],final['step'],int(opts['--trace-max']),int(opts['--trace-stride']));checked,gaps=anchored(traces,initial,states,d)
 C.need(final['step']-initial['step']<=int(opts['--steps'])and summary['native_result']==json.loads((native/'result.json').read_bytes()),'actual saved native result/reported proposal bound','RESULT')
 E.write(out/'object_audits.json',reports);E.write(out/'sparse_trace_audit.json',dict(total_saved_records=len(traces),complete_anchored_proposals=checked,locally_checked_unreplayed_global_gaps=gaps,not_full_trajectory=True));E.write(out/'localzero_population.json',allzero)
 return dict(status='INDEPENDENT_ROOT_FOCUSED_SAVED_OBJECTS_V1_PASS',saved_states=len(states),saved_state_files=len(list(native.glob('*.state'))),saved_selected_object_files=len(objects),actual_retention_event_population=snapshotcounts,saved_localzero_object_observations=len(allzero),minimum_mu_over_saved_localzero=None if not allzero else min(v['mu_energy']for v in allzero),native_reported_proposals=final['step']-initial['step'],saved_trace_records=len(traces),complete_anchored_proposals=len(checked),locally_checked_global_gaps=len(gaps),complete_trajectory_checked=not gaps and len(traces)==final['step']-initial['step'],zero_target_candidates=sum(r['full_scalar_objects'][s]['srg_valid']for r in reports for s in r['full_scalar_objects']),target_resolution='NONE',object_audits_sha256=E.sha(out/'object_audits.json'),sparse_trace_audit_sha256=E.sha(out/'sparse_trace_audit.json'),localzero_population_sha256=E.sha(out/'localzero_population.json'))

def main():
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['calibration','full']);p.add_argument('--seconds',type=float,required=True);p.add_argument('--out',required=True)
 for arg in ['run-summary','calibration','engine-gate','input-gate','supervisor']:p.add_argument('--'+arg);p.add_argument('--'+arg+'-sha256')
 a=p.parse_args();d=CommandDeadline(a.seconds,allocation_reason='New root-focused saved object/scalar/sparse checker;180/150 synthetic calibration or separately allocated fullaudit;20save reserve');out=E.local(a.out);out.mkdir(parents=True,exist_ok=False);pins={}
 def pin(name,wanted=None,size=None):
  C.need(d.status()['remaining_seconds']>20,'saved checking reserve','DEADLINE');path=E.local(name);h=E.sha(path);C.need(wanted is None or h==wanted,'literal hash '+name,'IDENTITY');C.need(size is None or path.stat().st_size==size,'literal size '+name,'IDENTITY');pins[path.relative_to(ROOT).as_posix()]=h;return h
 try:
  ledger=pin('CLAIMS.yaml');index=pin('.git/index')
  for name in CODE:pin(name)
  pin(E.PLAN);plan=json.loads(E.local(E.PLAN).read_bytes())
  for name,h in plan['source_inputs_sha256'].items():pin(name,h)
  pin(E.BUILD,E.BUILD_SHA);build=json.loads(E.local(E.BUILD).read_bytes());pin(build['binary_path'],build['binary_sha256']);sourcepins={k:v for k,v in pins.items()if k not in ['CLAIMS.yaml','.git/index']}
  result=calibration(out,d)if a.mode=='calibration'else full(a,out,pin,d,sourcepins)
  C.need(pin('CLAIMS.yaml')==ledger and pin('.git/index')==index,'live ledger/index unchanged','IDENTITY')
  result.update(timestamp=datetime.now(timezone.utc).isoformat(),verifier='/root/checkpoint_audit',producer='/root/native_driver',method='independent_artifact_check',command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256={k:v for k,v in pins.items()if k not in ['CLAIMS.yaml','.git/index']},historical_protected_execution_state=dict(observations_sha256={k:pins[k]for k in ['CLAIMS.yaml','.git/index']},role='Protected before/after execution observations; not immutable native dependencies.',reason='Current ledger/index matched starting bytes during this command. Later authorized publication/registration changes do not alter tested native/helper artifacts.'),deadline=d.status(),shared_components=['New independently written root_focused_core_v2 and engine_v4 raw parsing/RNG/set-scoring/receipt helpers; no native producer imports.','Scalar exact integer row-by-column matrix multiplication is distinct from set CN scores.','Synthetic traces are generated by the independent checker itself; calibration is falsification of known objects and mutations, not approval of native histories.','Declared native formats, deterministic RNG/schedule, hashing, Python runtime/libm and supported supervision are trusted components.'],limitations=['Minimum is only over explicitly saved localzero objects. Unobserved gaps do not establish earliest attainment or a full historical minimum.','All sparse rows get local RNG/type/component/acceptance checks; global adjacency/predicates/deltas get complete checking only from saved complete anchors.','Generic rook9 zero is not a99vertex certificate; support pair uniqueness does not follow from root-localzero.','No performance, ergodicity, unrestricted exclusion or target resolution claim.'])
  E.write(out/'summary.json',result);print(json.dumps({k:result[k]for k in ['status','positive_controls','strict_negative_controls','saved_states']if k in result}))
 except BaseException as e:E.write(out/'failure.json',dict(error=repr(e),inputs_sha256=pins,deadline=d.status(),outputs_preserved=True,no_approval=True));raise
if __name__=='__main__':main()
