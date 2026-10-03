"""Separate finite engineering controls/artifact audit, never runs native code."""
import argparse
import copy
from datetime import datetime,timezone
import hashlib
import json
import math
from pathlib import Path
import platform
import sys
from tqdm import tqdm
from command_deadline import CommandDeadline
import audit_20261003_root_focused_core_v2 as C

ROOT=Path(__file__).resolve().parents[1]
PLAN='acceleration/plan_20261003_hypergraph_root_focused_engineering_v3.json'
POSITIVE=['rook_positive','rook_forced','target_forced','target_greedy','target_anneal','target_cooling','target_mixed','prism_initial','cube_initial','cube_forced','rook_probes','prism_probes',*[f+s for f in ['target','prism','import','rook']for s in['_whole','_prefix73','_resumed']],'import_rook_reset','import_target_reset']
NEGATIVE={'objective':'state exact objective','weight':'state exact objective','kernel':'state exact kernel/distribution','distribution':'state exact kernel/distribution','root':'state root','seed':'state exact continuation config','temperature':'state exact continuation config','checkpoint':'state exact continuation config','counter':'state counter consistency','local_counter':'state counter consistency','score':'state exact components/scores','lambda':'state exact components/scores','mu':'state exact components/scores','root_score':'state exact components/scores','best_score':'state exact components/scores','graph_identity':'state graph identity','fixture_provenance':'fixture exact provenance','version':'state version','cache':'state exact CN cache','zero_rng':'state RNG nonzero','negative_rng':'strict unsigned argument','duplicate_current':'linear pair multiplicity','frozen_literal':'state literal frozen/mutable identity','mutable_map':'state literal frozen/mutable identity','first_flag':'snapshot flag first_localzero','first_rng':'first_localzero RNG nonzero','first_counter':'snapshot counter consistency','first_triple':'linear pair multiplicity','best_local_rng':'best_localzero_mu RNG nonzero','best_local_triple':'linear pair multiplicity','import_version':'graph input version','import_root':'graph input root','import_domain':'declared target or generic domain','import_hash':'graph input provenance','import_duplicate':'linear pair multiplicity','import_trailing':'graph input exact end'}
CODE=['acceleration/audit_20261003_root_focused_core_v2.py','acceleration/audit_20261003_root_focused_engine_v4.py','acceleration/audit_20261003_root_focused_engine_v4_spec.md','acceleration/command_deadline.py','acceleration/run_compute_command.py','pyproject.toml','uv.lock']
BUILD='acceleration/results/20261003_hypergraph_root_focused_build02/build_manifest.json'
BUILD_SHA='80ae03734c3ede83514b1453900a5fa9337ccf45c663f2fd3286867fbff81b2d'
OWN_NEGATIVE={'objective':'OBJECTIVE','weight':'OBJECTIVE','kernel':'KERNEL','distribution':'KERNEL','root':'CONFIG','seed':'CONFIG','temperature':'CONFIG','checkpoint':'CONFIG','counter':'COUNTERS','local_counter':'COUNTERS','score':'SCORE','lambda':'SCORE','mu':'SCORE','root_score':'SCORE','best_score':'SCORE','graph_identity':'PROVENANCE','fixture_provenance':'PROVENANCE','version':'SYNTAX','cache':'CACHE','zero_rng':'RNG','negative_rng':'RNG','duplicate_current':'DOMAIN','frozen_literal':'REFERENCE','mutable_map':'REFERENCE','first_flag':'SNAPSHOT','first_rng':'RNG','first_counter':'SNAPSHOT','first_triple':'DOMAIN','best_local_rng':'RNG','best_local_triple':'DOMAIN','import_version':'SYNTAX','import_root':'IMPORT','import_domain':'DOMAIN','import_hash':'PROVENANCE','import_duplicate':'DOMAIN','import_trailing':'SYNTAX'}
def sha(path):
 with Path(path).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(path,value):
 with Path(path).open('x',encoding='utf8',newline='\n')as f:json.dump(value,f,indent=2);f.write('\n')
def local(path):
 prefix='/mnt/c/'+str(ROOT)[3:].replace('\\','/')+'/'
 if path.startswith(prefix):path=path[len(prefix):]
 p=(ROOT/path).resolve();C.need(p.is_relative_to(ROOT),'workspace literal path','IDENTITY');return p
def options(values):
 result={};at=0
 while at<len(values):
  k=values[at];at+=1;C.need(k.startswith('--')and k not in result,'unique option','RECEIPT')
  if k in['--forced','--emit-pair-costs','--stop-at-localzero']:result[k]=True
  else:C.need(at<len(values),'complete option value','RECEIPT');result[k]=values[at];at+=1
 return result

def header_check(raw,opts,provenance):
 t=C.Tokens(raw);t.expect('ROOT_FOCUSED_ANNEAL_STATE_V1');h={k:t.field(k)for k in C.CONFIG}
 C.need(h['objective']==C.OBJECTIVE and h['lambda_weight']=='60','recorded exact objective','OBJECTIVE')
 C.need(h['move_kernel']==C.KERNEL and h['distribution']==C.DISTRIBUTION,'recorded exact distribution/kernel','KERNEL')
 C.need(C.integer(h['root'])==int(opts['--root']),'recorded root equals command root','CONFIG')
 C.need(all(h[k]==v for k,v in provenance.items()),'command input identity/provenance','PROVENANCE')
 for k,opt in [('seed','--seed'),('mix_steps','--mix-steps'),('schedule_steps','--schedule-steps'),('checkpoint_every','--checkpoint-every')]:C.need(C.integer(h[k],'CONFIG',True)==int(opts[opt]),'exact continuation '+k,'CONFIG')
 C.need(h['forced']==str(int(bool(opts.get('--forced')))) and float(h['t_start'])==float(opts['--temperature-start'])and float(h['t_end'])==float(opts['--temperature-end'])and h['probe_identity']==opts.get('--probe-identity','0'*64),'exact continuation settings','CONFIG')

def independent_negative(opts,kind):
 original=C.fixture(opts['--fixture'])
 provenance={k:'0'*64 for k in ['input_sha256','source_matrix_sha256','source_triples_sha256','selection_report_sha256']}
 if '--graph-input'in opts:
  decoded=C.parse_graph_input(local(opts['--graph-input']).read_bytes())
  C.need(decoded['root']==int(opts['--root']),'literal import root equals command root','IMPORT')
  C.need(decoded['triples']==original,'literal import rows equal fixture','IMPORT')
 else:
  raw=local(opts['--resume']).read_bytes();header_check(raw,opts,provenance);C.parse_state(raw,original)
 raise C.CheckError('NATIVE_VETO','independent false acceptance '+kind)
def calibration(out,deadline):
 records=[]
 def positive(name,fn):fn();records.append(dict(case=name,outcome='PASS'))
 def negative(name,stage,fn):
  try:fn()
  except C.CheckError as e:C.need(e.stage==stage,'strict diagnostic '+name+': '+str(e),'CALIBRATION');records.append(dict(case=name,outcome='REJECTED',stage=stage));return
  raise C.CheckError('CALIBRATION','false acceptance '+name)
 rook=C.initial('rook9',0);raw=C.serialize(rook)
 positive('known rook exact set/scalar zero',lambda:C.need(all(C.scalar_objects(rook)[k]['srg_valid']for k in ['current','best_root','first_localzero','best_localzero_mu']),'rook9 SRG','CALIBRATION'))
 positive('full synthetic state roundtrip with two snapshots',lambda:C.need(C.parse_state(raw,C.fixture('rook9'))==rook,'roundtrip','CALIBRATION'))
 early=ROOT/'acceleration/results/20261003_hypergraph_root_focused_controls01/rook_positive'
 positive('one preserved actual native rook parser and scalar fixture',lambda:C.need(C.parse_state((early/'initial.state').read_bytes(),C.fixture('rook9'))==rook and C.parse_state((early/'final.state').read_bytes(),C.fixture('rook9'))==rook and C.scalar_matrix((early/'current.adj').read_bytes(),9,2,0)['srg_valid'],'single completed control before wrapper failure only','CALIBRATION'))
 prism=C.initial('prism9',8);positive('prism positive nonzero partial state',lambda:C.need(prism['lambda_energy']>0 and prism['first_localzero']is None,'nonzero prism','CALIBRATION'))
 cube=C.initial('cube12_defect',11);positive('cube12 exact scalar agreement',lambda:C.scalar_objects(cube))
 probes=0;veto=valid=0
 for name,root in [('rook9',0),('prism9',8)]:
  s=C.initial(name,root);rng=s['rng'][:];old=copy.deepcopy(s['current'])
  for i,j in __import__('itertools').combinations(range(len(s['current'])),2):
   for pi in range(3):
    for pj in range(3):
     event,_=C.transition(s,[i,j,pi,pj]);C.need(event['accepted']is False and event['selection_draws']==0 and event['draw']=='0'and s['rng']==rng and s['current']==old,'probe no RNG/mutation','CALIBRATION');probes+=1;veto+=int(event['frozen_line_selected']);valid+=int(event['admissible'])
 positive('complete270probe root-veto/delta rollbacks',lambda:C.need(probes==270 and veto>0 and valid>0,'actual probe populations','CALIBRATION'))
 s=C.initial('rook9',0,seed=42,temp=16,forced=True);whole=copy.deepcopy(s);events=[]
 for _ in range(96):events.append(C.transition(whole)[0])
 split=copy.deepcopy(s)
 for event in events[:73]:C.replay(split,event)
 resumed=C.parse_state(C.serialize(split),C.fixture('rook9'))
 for event in events[73:]:C.replay(resumed,event)
 positive('exact96 whole/split73 serialized replay',lambda:C.need(resumed==whole,'whole/split objects','CALIBRATION'))
 tape=iter([0,0,2]);positive('bounded rejection threshold preserves draw count',lambda:C.need(C.bounded(lambda:next(tape),3)==(2,3),'threshold one','CALIBRATION'))
 tape=iter([0,0,3]);positive('power2 bound acceptszero immediately',lambda:C.need(C.bounded(lambda:next(tape),4)==(0,1),'no unnecessary rejection','CALIBRATION'))
 positive('bound one always returns zero',lambda:C.need(C.bounded(lambda:C.M,1)==(0,1),'unit bound','CALIBRATION'))
 tape=iter([0,C.M]);positive('near uint64 limit rejects zero',lambda:C.need(C.bounded(lambda:next(tape),C.M)==(0,2),'large bound exact threshold','CALIBRATION'))
 inv=dict(command=['python','acceleration/prepare_20261003_hypergraph_root_focused_v3.py','controls'],supervision=dict(invocation_id='synthetic',outer_seconds=600,guard_argv=['/usr/bin/timeout','--signal=KILL','580s','/usr/bin/env','UV_PROJECT_ENVIRONMENT=build/native-budget-linux-venv','/root/.local/bin/uv','run','--locked','--offline']),address_space_bytes=2147483648,file_bytes=1073741824)
 m=dict(invocation_id='synthetic',source_sha256=sha(local('acceleration/run_compute_command.py')),seconds=600,automatic_retry=False,cumulative_across_commands=False,command=['/usr/bin/env','UV_PROJECT_ENVIRONMENT=build/native-budget-linux-venv','/root/.local/bin/uv','run','--locked','--offline','--project','acceleration/native_budget_env_v1','--cache-dir','build/native-budget-linux-cache','--python','/usr/bin/python3','python',*inv['command'][1:]])
 inv['supervision']['guard_argv']=['/usr/bin/timeout','--signal=KILL','580s',*m['command']]
 terminal=dict(invocation_id='synthetic',command_exit_code=0,cleanup=dict(reaped=True,job_active_zero_observed=True,cleanup_errors=[],process_group_live_pids=[]))
 positive('synthetic complete contained invocation receipt',lambda:supervision_values(inv,m,terminal))
 for name,change in [('activegroup',lambda a,b,c:c['cleanup'].update(process_group_live_pids=[1])),('exit',lambda a,b,c:c.update(command_exit_code=1)),('invocationid',lambda a,b,c:b.update(invocation_id='other')),('sourcehash',lambda a,b,c:b.update(source_sha256='0'*64)),('command',lambda a,b,c:b['command'].append('other')),('budget',lambda a,b,c:b.update(seconds=21601)),('guard',lambda a,b,c:a['supervision']['guard_argv'].__setitem__(1,'--signal=TERM'))]:
  i,j,k=copy.deepcopy(inv),copy.deepcopy(m),copy.deepcopy(terminal);change(i,j,k);negative('contained receipt '+name,'SUPERVISION',lambda:supervision_values(i,j,k))
 negative('1024 bounded rejection limit','RNG',lambda:C.bounded(lambda:0,3))
 negative('bounded Boolean domain','RNG',lambda:C.bounded(lambda:0,True))
 for name,stage,change in [('objective','OBJECTIVE',lambda x:x.update(objective='other')),('kernel','KERNEL',lambda x:x.update(move_kernel='old')),('distribution','KERNEL',lambda x:x.update(distribution='oldmodulo')),
  ('currentscore','SCORE',lambda x:x.update(root_energy=1)),('bestscore','SCORE',lambda x:x.update(best_root_energy=1)),('cache','CACHE',lambda x:x['cn'].__setitem__(0,x['cn'][0]+1)),('zeroRNG','RNG',lambda x:x.update(rng=[0,0,0,0])),('counter','COUNTERS',lambda x:x.update(accepted=1)),
  ('frozenmap','REFERENCE',lambda x:x['frozen'][0].__setitem__(3,8)),('mutablemap','REFERENCE',lambda x:x['mutable'].__setitem__(0,x['mutable'][1])),('snapshotcounter','SNAPSHOT',lambda x:x['first_localzero'].update(step=1)),('snapshotRNG','RNG',lambda x:x['first_localzero'].update(rng=[0]*4)),('snapshotflag','SNAPSHOT',lambda x:x.update(first_localzero=None))]:
  b=copy.deepcopy(rook);change(b);negative(name,stage,lambda:C.parse_state(C.serialize(b),C.fixture('rook9')))
 deceptive=copy.deepcopy(rook)
 for k in ['current','best_root']:deceptive[k][0]=list(reversed(deceptive[k][0]))
 for k in ['first_localzero','best_localzero_mu']:deceptive[k]['triples'][0]=list(reversed(deceptive[k]['triples'][0]))
 deceptive['frozen'][0][1:]=deceptive['current'][0]
 negative('selfconsistent replaced frozen literal versus original','REFERENCE',lambda:C.parse_state(C.serialize(deceptive),C.fixture('rook9')))
 negative('truncated state','SYNTAX',lambda:C.parse_state(raw[:-4]))
 negative('trailing state','SYNTAX',lambda:C.parse_state(raw+b'EXTRA\n'))
 negative('generic rook not99 certificate','MATRIX',lambda:C.target_zero(C.matrix_bytes(C.graph(C.fixture('rook9'),9,2,0)),0))
 negative('Boolean zero claim','TARGET_ZERO',lambda:C.target_zero(b'',False))
 event=events[0]
 for name,k,value,stage in [('delta','delta_root',event['delta_root']+1,'TRACE'),('acceptance','accepted',not event['accepted'],'TRACE'),('RNGword','draw',str(int(event['draw'])+1),'TRACE'),('selectionwords','selection_draws',event['selection_draws']+1,'TRACE'),('proposedline','proposed_triples',[[0,0,0],[0,0,0]],'TRACE'),('temperature','temperature',event['temperature']+1,'FLOAT'),('fieldomission',None,None,'TRACE')]:
  b=copy.deepcopy(event)
  if k is None:b.pop('root')
  else:b[k]=value
  negative(name,stage,lambda:C.replay(copy.deepcopy(s),b))
 write(out/'controls.json',records)
 return dict(status='INDEPENDENT_ROOT_FOCUSED_ENGINE_V1_SYNTHETIC_CALIBRATION_PASS',positive_controls=sum(v['outcome']=='PASS'for v in records),strict_negative_controls=sum(v['outcome']=='REJECTED'for v in records),complete_probe_proposals=probes,probe_frozen_vetoes=veto,probe_valid_rollbacks=valid,controls_sha256=sha(out/'controls.json'),controls=records,actual_native_fixture_calls_checked=1,complete_native_batch_approved=False)

def linux(path):return '/mnt/c/'+str(local(path))[3:].replace('\\','/')

def supervision_values(invocation,m,s):
 outer=invocation['supervision'];cl=s['cleanup']
 C.need(m['invocation_id']==s['invocation_id']==outer['invocation_id']and s['command_exit_code']==0 and cl['reaped']is True and cl['job_active_zero_observed']is True and cl['cleanup_errors']==[]and cl['process_group_live_pids']==[],'actual completed contained group','SUPERVISION')
 C.need(m['source_sha256']==sha(local('acceleration/run_compute_command.py'))and 0<m['seconds']<=21600 and m['seconds']==outer['outer_seconds']and m['automatic_retry']is False and m['cumulative_across_commands']is False,'exact supported per-command allocation','SUPERVISION')
 C.need(outer['guard_argv'][:2]==['/usr/bin/timeout','--signal=KILL']and outer['guard_argv'][3:5]==['/usr/bin/env','UV_PROJECT_ENVIRONMENT=build/native-budget-linux-venv']and outer['guard_argv'][5:9]==['/root/.local/bin/uv','run','--locked','--offline'],'actual Linux containment guard/runtime','SUPERVISION')
 C.need(outer['guard_argv'][3:]==m['command'],'guard owns the exact contained command','SUPERVISION')
 launcher=['/usr/bin/env','UV_PROJECT_ENVIRONMENT=build/native-budget-linux-venv','/root/.local/bin/uv','run','--locked','--offline','--project','acceleration/native_budget_env_v1','--cache-dir','build/native-budget-linux-cache','--python','/usr/bin/python3','python']
 C.need(m['command'][:13]==launcher and invocation['command'][1:]==m['command'][13:],'same actual supervised producer command','SUPERVISION')
 return outer,m,s

def supervision(invocation,pin):
 outer=invocation['supervision'];pin(outer['path'],outer['sha256']);m=json.loads(local(outer['path']).read_bytes());summary=(local(outer['path']).parent/'summary.json').relative_to(ROOT).as_posix();pin(summary);s=json.loads(local(summary).read_bytes());supervision_values(invocation,m,s)
 return outer,m,s

def native_receipt(receipt,options,invocation,outer,binary,directory):
 command=receipt['command'];C.need(command[:4]==['/usr/bin/timeout','--foreground','--signal=TERM','--kill-after=5s']and command[4].endswith('s'),'native foreground guard','RECEIPT');seconds=float(command[4][:-1]);C.need(math.isfinite(seconds)and 0<seconds<=10,'allocated finite native guard','RECEIPT')
 expected=['/usr/bin/prlimit',f"--as={invocation['address_space_bytes']}:{invocation['address_space_bytes']}",f"--fsize={invocation['file_bytes']}:{invocation['file_bytes']}",'--core=0:0',linux(binary),'--out',linux(directory),'--seconds',f'{max(.001,seconds-5):.6f}']
 C.need(command[5:14]==expected and command[14:]==options and receipt['cwd']==linux('acceleration')[:-len('/acceleration')]and receipt['process_group']==outer['group'],'actual native binary/resources/output/options/group/cwd','RECEIPT')

def full(manifest,out,pin,deadline,manifest_path):
 C.need(manifest['schema']=='ROOT_FOCUSED_ENGINE_CONTROLS_V1'and manifest['native_calls']==62 and manifest['positive_calls']==26 and manifest['strict_negative_calls']==36 and manifest['objective']==C.OBJECTIVE and manifest['distribution']==C.DISTRIBUTION and manifest['independent_approval']is False and manifest['target_resolution']is False,'exact finite engine scope','MANIFEST')
 C.need([r['label']for r in manifest['runs']]==POSITIVE+['reject_'+k for k in NEGATIVE],'exact62 frozen calls/order','MANIFEST')
 for name,h in manifest['inputs_sha256'].items():pin(name,h)
 for name,r in manifest['all_raw_artifacts'].items():C.need(pin(name,r['sha256'])and local(name).stat().st_size==r['bytes'],'all literal artifact bytes','IDENTITY')
 base=local(manifest_path).parent;invocation_path=(base/'invocation.json').relative_to(ROOT).as_posix();pin(invocation_path,manifest['all_raw_artifacts'][invocation_path]['sha256']);invocation=json.loads(local(invocation_path).read_bytes());outer,outer_manifest,outer_summary=supervision(invocation,pin);C.need(invocation['mode']=='controls'and invocation['source_commit']==manifest['source_commit'],'exact finite controls invocation/source','SUPERVISION')
 plan=json.loads(local(PLAN).read_bytes());allocation=plan['controls_allocation'];C.need(invocation['address_space_bytes']==allocation['address_space_bytes']and invocation['file_bytes']==allocation['file_bytes'],'exact frozen resources','SUPERVISION')
 argv=options(invocation['command'][3:]);C.need(invocation['command'][1]=='acceleration/prepare_20261003_hypergraph_root_focused_v3.py'and invocation['command'][2]=='controls'and argv['--engineering-plan']==PLAN and argv['--engineering-plan-sha256']==sha(local(PLAN))and float(argv['--native-seconds'])==allocation['native_guard_seconds'],'exact new wrapper/plan/native allocation','SUPERVISION')
 build=json.loads(local(BUILD).read_bytes())
 reports=[];total=0;costs=0;retention_counts={'initial':0,'first_localzero':0,'accepted_mu_improvement':0};coverage=dict(ordinary_accepted_overlap=0,ordinary_rejected_valid_overlap=0,probe_frozen_vetoes=0,probe_valid_rollbacks=0);families={}
 for run in tqdm(manifest['runs'],desc='Independent complete root-focused native controls',unit='call',mininterval=1):
  C.need(deadline.status()['remaining_seconds']>20,'not completed within allocated checking budget','DEADLINE');label=run['label'];opts=options(run['options']);receipt=json.loads(local(run['receipt']).read_bytes());pin(run['receipt'],run['receipt_sha256'])
  C.need(receipt['actual_exit_code']==run['actual_exit_code']and receipt['reaped']is True and receipt['error']is None,'actual terminal native receipt','RECEIPT')
  for k in ['stdout','stderr']:pin(receipt[k],receipt[k+'_sha256'])
  C.need(receipt['command'][-len(run['options']):]==run['options'],'receipt native options match frozen case','RECEIPT')
  directory=opts['--out']if '--out'in opts else (base/label).relative_to(ROOT).as_posix();native_receipt(receipt,run['options'],invocation,outer,build['binary_path'],directory)
  for path,r in run['artifacts'].items():C.need(path in manifest['all_raw_artifacts']and r==manifest['all_raw_artifacts'][path],'every run artifact belongs to frozen raw closure','IDENTITY')
  if label.startswith('reject_'):
   kind=label[len('reject_'):];expected=NEGATIVE[kind];C.need(run['actual_exit_code']==receipt['expected_exit_code']==2 and run['expected_diagnostic']==expected and local(receipt['stderr']).read_bytes()==(expected+'\n').encode()and local(receipt['stdout']).read_bytes()==b'','exact designated actual native veto','NATIVE_VETO')
   try:independent_negative(opts,kind)
   except C.CheckError as e:C.need(e.stage==OWN_NEGATIVE[kind],'designated separate raw corruption rejection '+str(e),'NATIVE_VETO');stage=e.stage
   reports.append(dict(label=label,expected_exit=2,diagnostic=expected,actual_veto_checked=True,independent_raw_rejection_stage=stage));continue
  C.need(run['actual_exit_code']==receipt['expected_exit_code']==0,'positive outcome','RECEIPT');files={Path(n).name:n for n in run['artifacts']};C.need(all(n in files for n in ['initial.state','final.state','moves.jsonl','result.json','current.adj','best_root.adj','pair_costs.jsonl']),'complete native output domain','FILES')
  original=C.fixture(opts['--fixture']);provenance=dict(input_sha256='0'*64,source_matrix_sha256='0'*64,source_triples_sha256='0'*64,selection_report_sha256='0'*64)
  imported=opts.get('--graph-input')or opts.get('--frozen-reference')
  if imported:
   inp=local(imported);pin(inp.relative_to(ROOT).as_posix(),opts['--graph-identity']);decoded=C.parse_graph_input(inp.read_bytes());C.need(decoded['triples']==original and decoded['root']==int(opts['--root']),'known literal fixture import, no scientific start','IMPORT');original=decoded['triples'];provenance=decoded['provenance']
   C.need(C.digest(C.matrix_bytes(C.graph(original,decoded['n'],decoded['degree'],decoded['root'])))==provenance['source_matrix_sha256'],'imported literal matrix provenance','IMPORT')
   identity_map={h:n for n,h in manifest['inputs_sha256'].items()};C.need(all(h in identity_map for k,h in provenance.items()if k!='input_sha256'),'all import metadata present/hashbound','IMPORT')
   typed=json.loads(local(identity_map[provenance['source_triples_sha256']]).read_bytes());C.need(typed['triples']==original and typed['root']==decoded['root']and typed['n']==decoded['n']and typed['degree']==decoded['degree'],'actual labelled JSON rows','IMPORT')
  parsed={}
  for name,path in files.items():
   if name.endswith('.state'):
    s=C.parse_state(local(path).read_bytes(),original);C.reference_check(s,original,provenance);parsed[name]=s
  s=copy.deepcopy(parsed['initial.state']);C.need(all(s[k]==v for k,v in provenance.items()),'initial provenance','IMPORT')
  C.need(s['root']==int(opts['--root'])and s['seed']==int(opts['--seed'])and s['mix_steps']==int(opts['--mix-steps'])and s['schedule_steps']==int(opts['--schedule-steps'])and s['checkpoint_every']==int(opts['--checkpoint-every'])and s['forced']==int(bool(opts.get('--forced')))and s['t_start']==float(opts['--temperature-start'])and s['t_end']==float(opts['--temperature-end']),'exact native configuration','CONFIG')
  if '--resume'in opts:C.need(s==C.parse_state(local(opts['--resume']).read_bytes(),original),'literal prefix continuation','RESUME')
  else:
   expected=C.initial(opts['--fixture'],int(opts['--root']),seed=int(opts['--seed']),temp=float(opts['--temperature-start']),end=float(opts['--temperature-end']),mix=int(opts['--mix-steps']),forced=bool(opts.get('--forced')),checkpoint=int(opts['--checkpoint-every']),schedule=int(opts['--schedule-steps']),provenance=provenance,probe_identity=opts.get('--probe-identity','0'*64),triples=original)
   C.need(s==expected,'fresh reset exact RNG/counters/object populations','IMPORT')
  probes=None
  if '--probe-file'in opts:
   raw=local(opts['--probe-file']).read_bytes();C.need(C.digest(raw)==opts['--probe-identity'],'exact probe identity','PROBE');t=C.Tokens(raw);t.expect('ROOT_FOCUSED_CONTROL_PROBES_V1');count=t.number('count');probes=[[C.integer(t.take())for _ in range(4)]for _ in range(count)];t.end();C.need(count==135 and probes==[[i,j,a,b]for i in range(6)for j in range(i+1,6)for a in range(3)for b in range(3)],'complete labelled135probe universe','PROBE')
  objects={name:C.parse_selected(local(path).read_bytes(),parsed['final.state'])for name,path in files.items()if name.endswith('.object')};wanted={p['step']for p in parsed.values()}|{o['step']for o in objects.values()};anchors={s['step']:copy.deepcopy(s)};count=0;minmargin=None
  inherited=[s[k]for k in ['first_localzero','best_localzero_mu']if s[k]is not None]
  retained={}
  if '--resume'not in opts and s['first_localzero']is not None:retained['retained_first_localzero_'+str(s['step'])+'.object']=copy.deepcopy(s['first_localzero'])
  for line in local(files['moves.jsonl']).read_bytes().splitlines():
   if count%256==0:C.need(deadline.status()['remaining_seconds']>20,'finite replay deadline','DEADLINE')
   firstbefore=s['first_localzero']is not None;updates=s['local_updates'];event=json.loads(line);probe=probes[s['step']]if probes is not None else None;expected,margin=C.replay(s,event,probe);count+=1
   if not firstbefore and s['first_localzero']is not None:retained['retained_first_localzero_'+str(s['step'])+'.object']=copy.deepcopy(s['first_localzero'])
   elif s['local_updates']>updates:retained['retained_localzero_mu_'+str(s['step'])+'.object']=copy.deepcopy(s['best_localzero_mu'])
   if margin is not None:minmargin=margin if minmargin is None else min(minmargin,margin)
   if expected['probe']:coverage['probe_frozen_vetoes']+=int(expected['frozen_line_selected']);coverage['probe_valid_rollbacks']+=int(expected['admissible'])
   elif expected['admissible']and not expected['disjoint']:coverage['ordinary_accepted_overlap'if expected['accepted']else'ordinary_rejected_valid_overlap']+=1
   if s['step']in wanted:anchors[s['step']]=copy.deepcopy(s)
  C.need(count==int(opts['--steps'])and s==parsed['final.state'],'complete exact finite trace/end state','REPLAY');total+=count
  C.need({n:o for n,o in objects.items()if n.startswith('retained_')}==retained,'complete immediate retained object population/content','RETENTION')
  for o in retained.values():retention_counts[o['reason']]+=1
  expected_checkpoints={'checkpoint_'+str(step)+'.state'for step in range(parsed['initial.state']['step']+1,s['step']+1)if step%s['checkpoint_every']==0}
  C.need({n for n in parsed if n.startswith('checkpoint_')}==expected_checkpoints,'complete deterministic checkpoint population','FILES')
  scalar={}
  for name,p in parsed.items():C.need(p==anchors[p['step']],'every checkpoint complete replay anchor','REPLAY');scalar[name]=C.scalar_objects(p)
  for name,o in objects.items():
   anchor=anchors.get(o['step']);C.need(o in inherited or (anchor is not None and (o==anchor['first_localzero']or o==anchor['best_localzero_mu'])),'every literal retained snapshot attained/inherited from checked anchor','RETENTION')
   g=C.graph(o['triples'],s['n'],s['degree'],s['root']);r=C.scalar_matrix(C.matrix_bytes(g),s['n'],s['degree'],s['root']);C.need(all(r[k]==g[k]for k in C.SCORES),'selected separate scalar matrix','MATRIX');scalar[name]=r
  f=parsed['final.state'];selections=[('current.adj',f['current']),('best_root.adj',f['best_root'])]
  if f['first_localzero']is not None:selections +=[('first_localzero.adj',f['first_localzero']['triples']),('best_localzero_mu.adj',f['best_localzero_mu']['triples'])]
  C.need(('first_localzero.object'in files)==('best_localzero_mu.object'in files)==(f['first_localzero']is not None),'exact selected file population','RETENTION')
  for name,rows in selections:C.need(local(files[name]).read_bytes()==C.matrix_bytes(C.graph(rows,s['n'],s['degree'],s['root'])),'raw selected adjacency literal bytes','MATRIX')
  costrows=[json.loads(line)for line in local(files['pair_costs.jsonl']).read_bytes().splitlines()];C.need(costrows==C.pair_costs()and len(costrows)==172,'all exact independent pair costs','PAIR_COST');costs+=172
  result=json.loads(local(files['result.json']).read_bytes());expected=dict(objective=C.OBJECTIVE,move_kernel=C.KERNEL,distribution=C.DISTRIBUTION,n=f['n'],point_degree=f['degree'],root=f['root'],frozen_lines=len(f['frozen']),mutable_lines=len(f['mutable']),current_F=f['root_energy'],current_lambda=f['lambda_energy'],current_mu=f['mu_energy'],current_root_residual=f['root_residual'],best_F=f['best_root_energy'],best_lambda=f['best_lambda_energy'],best_mu=f['best_mu_energy'],best_root_residual=f['best_root_residual'],first_retained_localzero_found=f['first_localzero']is not None,first_retained_localzero_step=None if f['first_localzero']is None else f['first_localzero']['step'],best_retained_localzero_mu=None if f['best_localzero_mu']is None else C.graph(f['best_localzero_mu']['triples'],f['n'],f['degree'],f['root'])['mu_energy'],starting_step=parsed['initial.state']['step'],ending_step=f['step'],proposals_this_invocation=count,admissible_total=f['admissible'],accepted_total=f['accepted'],best_updates_total=f['best_updates'],local_updates_total=f['local_updates'],stop_reason='REQUESTED_STEPS_COMPLETE',target_resolution=False,independent_approval=False)
  C.need(set(result)==set(expected)|{'elapsed_seconds'}and type(result['elapsed_seconds'])in[int,float]and math.isfinite(result['elapsed_seconds'])and result['elapsed_seconds']>=0 and all(type(result[k])is type(v)and result[k]==v for k,v in expected.items()),'exact result fields/counters/selectors','RESULT')
  families[label]=(files,parsed);reports.append(dict(label=label,full_proposals_checked=count,saved_states=len(parsed),retained_object_files=len(objects),minimum_floating_acceptance_margin=minmargin,all_raw_scalars=scalar,final_scores={k:f[k]for k in C.SCORES}))
 C.need(all(coverage.values())and coverage==manifest['coverage'],'actual complete overlap/veto/rollback populations','COVERAGE')
 for family,steps in [('target',512),('prism',2048),('import',512),('rook',256)]:
  a,b,c=[families[family+k]for k in['_whole','_prefix73','_resumed']]
  C.need(a[1]['final.state']==c[1]['final.state']and b[1]['final.state']==c[1]['initial.state'],'four exact full/split state families','SPLIT')
  C.need(local(a[0]['moves.jsonl']).read_bytes()==local(b[0]['moves.jsonl']).read_bytes()+local(c[0]['moves.jsonl']).read_bytes(),'complete concatenated trace bytes','SPLIT')
  for name in ['current.adj','best_root.adj','first_localzero.object','first_localzero.adj','best_localzero_mu.object','best_localzero_mu.adj']:
   C.need((name in a[0])==(name in c[0])and(name not in a[0]or local(a[0][name]).read_bytes()==local(c[0][name]).read_bytes()),'whole/split raw selected byte equality','SPLIT')
 C.need(families['prism_initial'][1]['final.state']['lambda_energy']>0 and families['prism_whole'][1]['final.state']['first_localzero']is not None,'actual preregistered late prism zero succeeds','COVERAGE')
 write(out/'case_audits.json',reports)
 return dict(status='INDEPENDENT_ROOT_FOCUSED_ENGINE_V1_CONTROLS_PASS',positive_native_calls=26,strict_native_vetoes=36,complete_finite_proposals=total,complete_probe_proposals=270,pair_cost_records_checked=costs,whole_split_families=4,actual_coverage=coverage,actual_immediate_retention_events=retention_counts,unexercised_retention_branches=[k for k,v in retention_counts.items()if v==0],case_audits_sha256=sha(out/'case_audits.json'),target_resolution='NONE',scientific_results_approved=0)

def main():
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['calibration','full']);p.add_argument('--seconds',type=float,required=True);p.add_argument('--out',required=True);p.add_argument('--manifest');p.add_argument('--manifest-sha256');p.add_argument('--calibration');p.add_argument('--calibration-sha256');a=p.parse_args()
 d=CommandDeadline(a.seconds,allocation_reason='New independent root-focused finite calibration/full controls only; no native launches;20save reserve');out=(ROOT/a.out).resolve();C.need(out.is_relative_to(ROOT),'workspace output','IDENTITY');out.mkdir(parents=True,exist_ok=False);pins={}
 def pin(name,h=None):
  C.need(d.status()['remaining_seconds']>20,'checking save reserve','DEADLINE');path=local(name);value=sha(path);C.need(h is None or value==h,'exact artifact '+name,'IDENTITY');pins[path.relative_to(ROOT).as_posix()]=value;return value
 try:
  live=pin('CLAIMS.yaml');index=pin('.git/index')
  for name in CODE:pin(name)
  plan=json.loads(local(PLAN).read_bytes());pin(PLAN);C.need(plan['schema']=='ROOT_FOCUSED_ENGINEERING_PLAN_V1'and plan['controls_allocation']['native_calls']==62,'exact frozen engineering plan','MANIFEST')
  for name,h in plan['source_inputs_sha256'].items():pin(name,h)
  early=ROOT/'acceleration/results/20261003_hypergraph_root_focused_controls01/rook_positive'
  for name in ['initial.state','final.state','current.adj']:pin((early/name).relative_to(ROOT).as_posix())
  pin(BUILD,BUILD_SHA);build=json.loads(local(BUILD).read_bytes());C.need(build['schema']=='ROOT_FOCUSED_NATIVE_BUILD_V1'and build['source_cpp_sha256']==plan['source_inputs_sha256']['acceleration/hypergraph_root_focused_anneal_20261003_v2.cpp'],'exact V2 build source','BUILD');pin(build['binary_path'],build['binary_sha256']);pin(build['receipt'],build['receipt_sha256']);br=json.loads(local(build['receipt']).read_bytes());C.need(br['actual_exit_code']==br['expected_exit_code']==0 and br['reaped']is True and br['error']is None and br['command']==build['command'],'actual compiler/build receipt','BUILD')
  for k in ['stdout','stderr']:pin(br[k],br[k+'_sha256']);C.need(local(br[k]).read_bytes()==b'','warning-free native build logs','BUILD')
  cal=calibration(out,d)
  if a.mode=='calibration':result=cal
  else:
   C.need(all([a.manifest,a.manifest_sha256,a.calibration,a.calibration_sha256]),'exact full checker arguments','IDENTITY');pin(a.calibration,a.calibration_sha256);old=json.loads(local(a.calibration).read_bytes());C.need(old['status']=='INDEPENDENT_ROOT_FOCUSED_ENGINE_V1_SYNTHETIC_CALIBRATION_PASS'and all(old['inputs_sha256'][n]==pins[n]for n in CODE),'fresh unchanged full calibration','CALIBRATION');pin(a.manifest,a.manifest_sha256);result=full(json.loads(local(a.manifest).read_bytes()),out,pin,d,a.manifest);result['pre_full_controls']=cal
  C.need(pin('CLAIMS.yaml')==live and pin('.git/index')==index,'live ledger/index unchanged','IDENTITY');result.update(timestamp=datetime.now(timezone.utc).isoformat(),verifier='/root/checkpoint_audit',producer='/root/native_driver',method='independent_artifact_check',command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,deadline=d.status(),mathematical_target_resolution='NONE',
   shared_components=['Prior independently written splitmix/xoshiro formulas and exact set/scalar graph methods; new source imports no native producer or census/engine implementation.','Declared RNG distribution/fixture/state format; Python exact integers/JSON/gzip/SHA256 and libm acceptance with strict margin1e-12.','Supported deadline/supervisor and locked uv environment; runtime/compiler and wrapper raw authentication are trusted components.'],limitations=['Finite engineering controls only; no ergodicity/performance/target exclusion or target graph result.','Native importer does not authenticate cryptographic hashes; raw wrapper/checker hashes and ROOT independent selected-input gate are separate requirements.','Full finite traces establish only tested histories; sparse future histories may not bridge unobserved gaps.'])
  write(out/'summary.json',result);print(json.dumps({k:result[k]for k in ['status','positive_controls','strict_negative_controls','complete_finite_proposals']if k in result}))
 except BaseException as e:write(out/'failure.json',dict(error=repr(e),inputs_sha256=pins,deadline=d.status(),outputs_preserved=True,no_approval=True));raise
if __name__=='__main__':main()
