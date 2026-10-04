"""Independent scientific mixed saved states and anchored sparse trace.

Source only. No producer imports, native calls, search, or historical state
manufacture. Changed science wrapper is explicitly pinned by this new gate.
"""
import argparse
from collections import Counter
import copy
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
from tqdm import tqdm

from command_deadline import CommandDeadline
import audit_20261003_ternary_mixed_core_v1 as core
import audit_20261003_ternary_mixed_engine_v2 as finite
import audit_20261003_ternary_mixed_graph_input_v1 as graph_input

ROOT=Path(__file__).resolve().parents[1]
SELF='acceleration/audit_20261003_ternary_mixed_saved_objects_v1.py'
SPEC=SELF.replace('.py','_spec.md')
SCI=graph_input.SCI
need,same=core.need,core.io.same
PINS={**graph_input.PINS,
 'acceleration/audit_20261003_ternary_mixed_engine_v2.py':'8271da2a35ae169a3a8f28fec58483a433bda8100dc9f6d3c1682d7d231586e7',
 'acceleration/audit_20261003_ternary_mixed_engine_v2_spec.md':'71ac9331d5f07aa75497ce8f7f34bb095274d8c4603bf9b6a71e35918eeb0226',
 'acceleration/audit_20261003_ternary_mixed_graph_input_v1.py':'79200405fe1b27ba01b4f75075c3c69099a2ce1d57041278e5af5c83efdcf360',
 'acceleration/audit_20261003_ternary_mixed_graph_input_v1_spec.md':'3a4ae18fb9aaff8019a329807f805f52e96577c35ef6cbbec5499be1dd39fac6',
 'acceleration/results/20261003_hypergraph_ternary_mixed_build01/build_manifest.json':'c1c3df1e9d933718c8b48ad94f2d03759bed17df4c5faaaf8b65651a08b928ea'}
TRACE_FIELDS=set('schema objective move_kernel distribution step ti tj pi pj old_triples proposed_triples disjoint exclusive absent_after_removal admissible accepted mixing temperature delta_scalar before candidate after best draw rng_words_before rng_words_after rng_before rng_after retained_zero_objects'.split())
RUN_UINT=set('seed steps mix-steps schedule-steps verify-every checkpoint-every trace-prefix trace-stride address-space-bytes file-bytes'.split())
RUN_REAL=set('seconds native-seconds temperature-start temperature-end checkpoint-seconds'.split())
RUN_PATHS=set('engine-gate saved-gate input-gate wire binary build-manifest'.split())
RUN_FIELDS={'--'+x for x in RUN_UINT|RUN_REAL|RUN_PATHS|{'out','supervision-out','source-commit'}}|{'--'+x+'-sha256' for x in RUN_PATHS}


def metric(value,n,d):
    need(type(value) is dict and set(value)==set(core.METRIC_KEYS),'LOCAL_METRIC_FIELDS')
    need(all(type(value[k]) is int and value[k]>=0 for k in core.METRIC_KEYS if k!='residue_population')
         and type(value['residue_population']) is list and len(value['residue_population'])==3
         and all(type(x) is int and x>=0 for x in value['residue_population']),'LOCAL_METRIC_TYPES')
    h=value['residue_population'];w=core.weight(n,d)
    need(sum(h)==n*(n-1)//2 and value['F3']==h[1]+h[2]
         and value['E']==value['E_lambda']+value['E_mu'] and value['scalar_weight']==w
         and value['scalar']==w*value['F3']+value['E'] and value['E']<=819819,'LOCAL_METRIC_RELATIONS')


def local_trace(raw,n,d,config):
    """Check trace-local algebra/RNG only; no invented missing adjacency anchor."""
    need(type(raw) is dict and set(raw)==TRACE_FIELDS,'TRACE_FIELDS')
    need(same([raw['schema'],raw['objective'],raw['move_kernel'],raw['distribution']],
        ['HYPERGRAPH_TERNARY_MIXED_MOVE_V1',core.OBJECTIVE,core.KERNEL,core.DISTRIBUTION]),'LOCAL_TRACE_VERSION')
    need(type(raw['step']) is int and 0<=raw['step']<=0x0fffffffffffffff
         and type(raw['retained_zero_objects']) is int and 0<=raw['retained_zero_objects']<=raw['step']+2,'LOCAL_TRACE_STEP')
    for key in ('disjoint','exclusive','absent_after_removal','admissible','accepted','mixing'):
        need(type(raw[key]) is bool,'LOCAL_TRACE_BOOL')
    m=n*d//3
    need(all(type(raw[k]) is int for k in ('ti','tj','pi','pj')) and 0<=raw['ti']<m
         and 0<=raw['tj']<m and raw['ti']!=raw['tj'] and 0<=raw['pi']<3 and 0<=raw['pj']<3,'LOCAL_TRACE_LABELS')
    old=raw['old_triples']
    need(type(old) is list and len(old)==2 and all(type(row) is list and len(row)==3
         and all(type(x) is int and 0<=x<n for x in row) and len(set(row))==3 for row in old),'LOCAL_TRACE_OLD_ROWS')
    t,q=old; x,y=t[raw['pi']],q[raw['pj']]
    proposed=copy.deepcopy(old);proposed[0][raw['pi']]=y;proposed[1][raw['pj']]=x
    exclusive=x not in q and y not in t
    need(same(raw['proposed_triples'],proposed) and raw['disjoint']==(not bool(set(t)&set(q)))
         and raw['exclusive']==exclusive and raw['admissible']==(exclusive and raw['absent_after_removal']), 'LOCAL_TRACE_GEOMETRY')
    for key in ('before','candidate','after','best'):metric(raw[key],n,d)
    need(type(raw['delta_scalar']) is int and raw['delta_scalar']==raw['candidate']['scalar']-raw['before']['scalar'], 'LOCAL_TRACE_DELTA')
    need(type(raw['rng_words_before']) is int and 4*raw['step']<=raw['rng_words_before']<=core.MASK
         and type(raw['rng_words_after']) is int and raw['rng_words_before']<=raw['rng_words_after']<=core.MASK,'LOCAL_TRACE_WORDS')
    need(type(raw['rng_before']) is list and len(raw['rng_before'])==4
         and type(raw['rng_after']) is list and len(raw['rng_after'])==4,'LOCAL_TRACE_RNG')
    rng=[core.number(x) for x in raw['rng_before']];need(any(rng),'RNG_ZERO')
    wanted_rng=[core.number(x) for x in raw['rng_after']]
    s=dict(rng=rng,rng_words=raw['rng_words_before'])
    ti=core.bounded(lambda:core.next_word(s),m);tj=core.bounded(lambda:core.next_word(s),m-1)
    if tj>=ti:tj+=1
    pi=core.bounded(lambda:core.next_word(s),3);pj=core.bounded(lambda:core.next_word(s),3)
    need(same([raw[k] for k in ('ti','tj','pi','pj')],[ti,tj,pi,pj]),'LOCAL_TRACE_RANDOM_LABELS')
    draw=core.next_word(s) if raw['admissible'] else 0
    need(core.number(raw['draw'])==draw and same(wanted_rng,s['rng'])
         and raw['rng_words_after']==s['rng_words'],'LOCAL_TRACE_RANDOM_CONSUMPTION')
    step=raw['step'];temp=config['t_start']+(config['t_end']-config['t_start'])*min(1.,max(step-config['mix_steps'],0)/config['schedule_steps'])
    need(type(raw['temperature']) in (int,float) and math.isfinite(raw['temperature'])
         and math.isclose(raw['temperature'],temp,rel_tol=1e-12,abs_tol=1e-10)
         and raw['mixing']==(step<config['mix_steps']),'LOCAL_TRACE_SCHEDULE')
    accepted=False;margin=None
    if raw['admissible']:
        easy=config['forced']==1 or raw['mixing'] or raw['delta_scalar']<=0
        threshold=math.exp(-raw['delta_scalar']/temp) if not easy and temp>0 else 0.
        u=(draw>>11)*2.**-53;accepted=easy or (temp>0 and u<threshold)
        if not easy and temp>0:margin=abs(u-threshold)
    else:
        need(same(raw['candidate'],raw['before']),'LOCAL_TRACE_INVALID_METRICS')
    need(raw['accepted']==accepted and same(raw['after'],raw['candidate'] if accepted else raw['before'])
         and (raw['best']['F3'],raw['best']['E'])<=(raw['after']['F3'],raw['after']['E']),'LOCAL_TRACE_ACCEPTANCE')
    return margin


def wanted_trace(end,prefix,stride):
    need(all(type(x) is int and x>=0 for x in (end,prefix,stride)),'TRACE_POPULATION_DOMAIN')
    return sorted(set(range(min(end,prefix)))| (set(range(0,end,stride)) if stride else set()))


def trace_audit(records,states,end,prefix,stride,tick=lambda:None,progress=False):
    wanted=wanted_trace(end,prefix,stride)
    need([r.get('step') for r in records]==wanted and all(type(r.get('step')) is int for r in records),'COMPLETE_STORED_TRACE_POPULATION')
    need(0 in states and end in states,'TRACE_ANCHOR_POPULATION')
    config={k:states[0][k] for k in ('seed','mix_steps','schedule_steps','t_start','t_end','forced')}
    cursor=copy.deepcopy(states[0]);anchored=0;unreplayed=[];margins=[]
    for record in tqdm(records,desc='Stored traces: anchors versus gaps',unit='record',disable=not progress):
        tick();margin=local_trace(record,states[0]['n'],states[0]['degree'],config)
        if margin is not None:margins.append(margin)
        step=record['step']
        if cursor is None or cursor['step']!=step:
            cursor=copy.deepcopy(states[step]) if step in states else None
        if cursor is None:
            unreplayed.append(step);continue
        expected,_,_=core.transition(cursor);core.check_trace(record,expected);anchored+=1
        if cursor['step'] in states:
            need(same(cursor,states[cursor['step']]),'COMPLETE_ANCHORED_STATE')
    need(not margins or min(margins)>1e-12,'FLOATING_ACCEPTANCE_MARGIN')
    return dict(stored_trace_records=len(records),trace_local_rng_and_algebra_checked=len(records),
        complete_anchored_proposals=anchored,unreplayed_gap_records=len(unreplayed),unreplayed_steps=unreplayed,
        minimum_acceptance_margin=min(margins) if margins else None,complete_scientific_trajectory_checked=(end==anchored))


def checkpoints(names,end,every,captures):
    need(type(end) is int and end>=0 and type(every) is int and every>0,'CHECKPOINT_DOMAIN')
    need({'initial.state','final.state'}|{f'checkpoint_{x}.state' for x in range(every,end+1,every)}
         |{f'zero_capture_{x}.state' for x in captures} <=set(names),'COMPLETE_SAVED_STATE_POPULATION')
    need(all(x in ('initial.state','final.state') or core.re.fullmatch(r'(?:checkpoint|zero_capture)_[0-9]+\.state',x) for x in names),'SAVED_STATE_NAME')


def artifact_population(raw,actual,prefix,summary_name):
    fixed={prefix+'/'+x for x in ('invocation.json','native.launch.json','native.receipt.json','native.stdout.log','native.stderr.log')}
    fixed|={prefix+'/native/'+x for x in ('initial.state','final.state','current.adj','best.adj','moves.jsonl','result.json','zero_selection.json')}
    need(type(raw) is dict and fixed<=set(raw),'COMPLETE_RAW_ARTIFACT_MAP')
    need(set(actual)==set(raw)|{summary_name} and summary_name not in raw,'COMPLETE_RAW_DIRECTORY_POPULATION')
    for name,entry in raw.items():
        need(graph_input.name_ok(name) and name.startswith(prefix+'/') and type(entry) is dict
             and set(entry)=={'sha256','bytes'} and graph_input.identity(entry['sha256'])
             and type(entry['bytes']) is int and 0<=entry['bytes']<=graph_input.CAP,'RAW_ARTIFACT_DESCRIPTOR')
        extra=name not in fixed
        need(not extra or core.re.fullmatch(core.re.escape(prefix)+r'/native/(?:checkpoint_[0-9]+\.state|zero_capture_[0-9]+\.state|zero_objects/object_[0-9]+\.(?:adj|triples))',name), 'RAW_ARTIFACT_NAME')


def run_options(command):
    need(type(command) is list and len(command)>=3 and all(type(x) is str for x in command)
         and recorded_name(command[1])==SCI and command[2]=='run','SCI_WRAPPER_COMMAND')
    values=command[3:];need(len(values)%2==0,'SCI_WRAPPER_ARGUMENTS');result={}
    for key,value in zip(values[::2],values[1::2]):
        need(key in RUN_FIELDS and key not in result,'SCI_WRAPPER_ARGUMENTS');result[key]=value
    need(set(result)==RUN_FIELDS,'SCI_WRAPPER_ARGUMENTS')
    for name in RUN_UINT:result['--'+name]=core.number(result['--'+name])
    for name in RUN_REAL:result['--'+name]=core.real(result['--'+name])
    need(all(result['--'+x]>0 for x in ('steps','schedule-steps','verify-every','checkpoint-every','address-space-bytes','file-bytes'))
         and result['--steps']<=0x0fffffffffffffff and result['--seconds']>30 and result['--native-seconds']>5
         and result['--checkpoint-seconds']>0,'SCI_WRAPPER_CONFIG')
    need(core.re.fullmatch('[0-9a-f]{40}',result['--source-commit']) is not None
         and all(graph_input.identity(result['--'+x+'-sha256']) for x in RUN_PATHS),'SCI_WRAPPER_IDENTITIES')
    return result


def recorded_name(value):
    need(type(value) is str,'RECORDED_PATH')
    text=value.replace('\\','/')
    for prefix in ('/mnt/c/Users/ikuto/projects/conway-99-graph/',ROOT.as_posix()+'/'):
        if text.startswith(prefix):text=text[len(prefix):];break
    need(graph_input.name_ok(text),'RECORDED_PATH')
    return text


def run_invocation(summary,invocation,runtime,runtime_sha):
    need(same(summary.get('command'),invocation.get('command')) and invocation.get('historical_native_state_written') is False
         and type(invocation.get('observed_euid')) is int and invocation['observed_euid']==1000
         and type(invocation.get('process_group')) is int and invocation['process_group']>0
         and invocation.get('independent_approval') is False and invocation.get('supervisor_manifest_sha256')==runtime_sha,'SCI_RUN_INVOCATION')
    options=run_options(summary['command'])
    need(summary['command'][1:]==runtime['command'][-(len(summary['command'])-1):]
         and invocation.get('source_context_commit')==options['--source-commit'],'SCI_RUN_INVOCATION_COMMAND')
    need(type(invocation.get('software_sha256')) is dict and all(invocation['software_sha256'].get(x)==PINS[x]
         for x in (SCI,SCI.replace('.py','_spec.md'),'acceleration/hypergraph_ternary_mixed_anneal_20261003_v1.cpp')),'SCI_RUN_INVOCATION_SOURCE')
    return options


def gate_header(value,status):
    wanted=dict(status=status,producer='/root/native_driver',verifier='/root/checkpoint_audit',method='independent_artifact_check',target_resolution='NONE')
    need(type(value) is dict and same({k:value.get(k) for k in wanted},wanted),'CANONICAL_SCIENCE_GATE')
    need(type(value.get('inputs_sha256')) is dict and value['inputs_sha256']
         and all(graph_input.name_ok(k) and graph_input.identity(v) for k,v in value['inputs_sha256'].items()),'SCIENCE_GATE_CLOSURE')


def native_receipt(launch,receipt,summary,runtime,plan,run):
    command=receipt.get('command')
    need(type(command) is list and len(command)>=18 and all(type(x) is str for x in command)
         and command[:4]==['/usr/bin/timeout','--foreground','--signal=TERM','--kill-after=5s']
         and command[5]=='/usr/bin/prlimit' and command[8]=='--core=0:0'
         and command[10]=='--out' and command[12]=='--seconds' and command[14]=='--graph-input'
         and command[16]=='--source-graph-sha256','SCI_NATIVE_COMMAND')
    need(command[4].endswith('s'),'SCI_NATIVE_LIMIT')
    guard=core.real(command[4][:-1]);cooperative=core.real(command[13])
    need(guard>5 and cooperative>0 and math.isclose(guard-cooperative,5.,rel_tol=0.,abs_tol=1e-6)
         and core.re.fullmatch(r'--as=([0-9]+):\1',command[6]) is not None
         and core.re.fullmatch(r'--fsize=([0-9]+):\1',command[7]) is not None,'SCI_NATIVE_LIMIT')
    need(recorded_name(command[9])==finite.BINARY and guard==run['--native-seconds']
         and int(command[6].split(':')[1])==run['--address-space-bytes']
         and int(command[7].split(':')[1])==run['--file-bytes']
         and recorded_name(command[11])==recorded_name(run['--out'])+'/native'
         and recorded_name(command[15])==recorded_name(run['--wire']),'SCI_NATIVE_CONFIG')
    options,config=finite.options(command[14:])
    native_fields={'--graph-input','--source-graph-sha256'}|{'--'+x for x in RUN_UINT-{'address-space-bytes','file-bytes'}}|{'--temperature-start','--temperature-end','--checkpoint-seconds'}
    need(len(command[14:])==2*len(native_fields) and set(command[14::2])==native_fields
         and all(same(options['--'+x],run['--'+x]) for x in (RUN_UINT-{'address-space-bytes','file-bytes'})|{'temperature-start','temperature-end','checkpoint-seconds'}),'SCI_NATIVE_CONFIG')
    need(same(launch.get('command'),command) and same(receipt.get('command'),command)
         and type(receipt.get('actual_exit_code')) is int and receipt['actual_exit_code']==0
         and type(receipt.get('observed_euid')) is int and receipt['observed_euid']==1000
         and receipt.get('reaped') is True and receipt.get('error') is None
         and type(receipt.get('automatic_retries')) is int and receipt['automatic_retries']==0
         and type(receipt.get('process_group')) is int and receipt['process_group']>0
         and type(receipt.get('child_pid')) is int and receipt['child_pid']>0
         and type(receipt.get('wall_seconds')) in (int,float) and math.isfinite(receipt['wall_seconds']) and receipt['wall_seconds']>=0
         and graph_input.identity(receipt.get('stdout_sha256')) and graph_input.identity(receipt.get('stderr_sha256')),'SCI_NATIVE_RECEIPT')
    need(summary.get('status')=='CANDIDATE_NATIVE_RUN_PENDING_INDEPENDENT_SAVED_OBJECT_CHECK'
         and summary.get('independent_approval') is False and summary.get('target_resolution')=='NONE'
         and type(summary.get('automatic_retries')) is int and summary['automatic_retries']==0
         and type(summary.get('actual_exit_code')) is int and summary['actual_exit_code']==0,'SCI_RUN_SUMMARY')
    graph_input.outer(runtime[0],runtime[1],plan)
    return command,guard,options,config


def receipt_link(receipt,invocation,raw,prefix):
    need(receipt['process_group']==invocation['process_group'] and receipt['stdout_sha256']==raw[prefix+'/native.stdout.log']['sha256']
         and receipt['stderr_sha256']==raw[prefix+'/native.stderr.log']['sha256'],'SCI_NATIVE_LOGS_AND_GROUP')


def calibration(tick):
    pos=[];neg=[]
    def reject(label,stage,callback):
        tick()
        try:callback()
        except core.io.AuditError as e:
            need(e.stage==stage,'WRONG_CONTROL_STAGE:'+label);neg.append(dict(case=label,expected_stage=stage,actual_stage=e.stage))
        else:raise core.io.AuditError('ACCEPTED_CORRUPTION:'+label)
    initial={}
    for fixture in ('rook9','prism9','cube12','target99'):
        s=core.initial(fixture,seed=181,forced=1)
        raw=core.serialize(s);parsed=core.parse_state(raw,s['source_graph_sha256'])
        need(same(s,parsed),'OWN_COMPLETE_STATE')
        for kind in ('current','best'):
            a,m,cn=core.geometry(s['n'],s['degree'],s[kind]);other,products=graph_input.scalar(s['n'],s['degree'],s[kind])
            need(same(m,other) and same(cn.tolist(),products),'OWN_SAVED_SCALAR')
        initial[fixture]=s;pos.append(dict(case=fixture+'_saved_state',whole_products=2*s['n']**2,zero_objects=len(s['zeros'])))
    s=copy.deepcopy(initial['cube12']);states={0:copy.deepcopy(s)};records=[]
    for _ in range(12):
        tick();record,_,_=core.transition(s);records.append(record)
        if s['step'] in (4,8,12):states[s['step']]=copy.deepcopy(s)
    sparse=[r for r in records if r['step']<3 or r['step']%3==0]
    outcome=trace_audit(sparse,states,12,3,3,tick)
    need(outcome['complete_anchored_proposals']==4 and outcome['unreplayed_gap_records']==2,'OWN_SPARSE_GAPS')
    pos.append(dict(case='explicit_sparse_gaps_and_anchors',**outcome))
    need(trace_audit(records,states,12,12,0,tick)['complete_anchored_proposals']==12,'OWN_COMPLETE_TRACE')
    pos.append(dict(case='complete_twelve_proposal_control',full_trace=True))
    example=records[0];config={k:initial['cube12'][k] for k in ('seed','mix_steps','schedule_steps','t_start','t_end','forced')}
    for key,value,stage in [('step',False,'LOCAL_TRACE_STEP'),('accepted',1,'LOCAL_TRACE_BOOL'),('ti',True,'LOCAL_TRACE_LABELS'),
        ('delta_scalar',0.0,'LOCAL_TRACE_DELTA'),('rng_words_before',False,'LOCAL_TRACE_WORDS'),
        ('temperature',True,'LOCAL_TRACE_SCHEDULE'),('draw','-1','WIRE_INTEGER')]:
        q=copy.deepcopy(example);q[key]=value
        reject('local_'+key,stage,lambda q=q:local_trace(q,12,2,config))
    q=copy.deepcopy(example);q['before']['scalar_weight']=1057.0
    reject('local_metric_float','LOCAL_METRIC_TYPES',lambda:local_trace(q,12,2,config))
    q=copy.deepcopy(example);q['before']['scalar_weight']=577
    reject('local_metric_weight','LOCAL_METRIC_RELATIONS',lambda:local_trace(q,12,2,config))
    q=copy.deepcopy(example);q['rng_before']=['0']*4
    reject('local_rng_zero','RNG_ZERO',lambda:local_trace(q,12,2,config))
    q=copy.deepcopy(example);q['old_triples'][0][0]=True
    reject('local_oldrow_bool','LOCAL_TRACE_OLD_ROWS',lambda:local_trace(q,12,2,config))
    q=copy.deepcopy(example);q['proposed_triples'][0][0]=99
    reject('local_proposed_row','LOCAL_TRACE_GEOMETRY',lambda:local_trace(q,12,2,config))
    q=copy.deepcopy(example);q['rng_after'][0]=str((int(q['rng_after'][0])+1)&core.MASK)
    reject('local_rng_post','LOCAL_TRACE_RANDOM_CONSUMPTION',lambda:local_trace(q,12,2,config))
    q=copy.deepcopy(example);q['exclusive']=not q['exclusive']
    reject('local_exclusive','LOCAL_TRACE_GEOMETRY',lambda:local_trace(q,12,2,config))
    q=copy.deepcopy(example);q['accepted']=not q['accepted']
    reject('local_acceptance','LOCAL_TRACE_ACCEPTANCE',lambda:local_trace(q,12,2,config))
    reject('omitted_trace','COMPLETE_STORED_TRACE_POPULATION',lambda:trace_audit(sparse[:-1],states,12,3,3))
    q=copy.deepcopy(states);q[4]['best_updates']+=1
    reject('wrong_complete_anchor','COMPLETE_ANCHORED_STATE',lambda:trace_audit(records,q,12,12,0))
    reject('missing_initial_anchor','TRACE_ANCHOR_POPULATION',lambda:trace_audit(records,{k:v for k,v in states.items() if k!=0},12,12,0))
    names=['initial.state','final.state','checkpoint_4.state','checkpoint_8.state','checkpoint_12.state']
    checkpoints(names,12,4,[])
    reject('missing_checkpoint','COMPLETE_SAVED_STATE_POPULATION',lambda:checkpoints(names[:-1],12,4,[]))
    reject('missing_immediate_zero','COMPLETE_SAVED_STATE_POPULATION',lambda:checkpoints(names,12,4,[5]))
    reject('state_name','SAVED_STATE_NAME',lambda:checkpoints(names+['unlisted.state'],12,4,[]))
    raw=core.serialize(initial['target99'])
    reject('saved_target_weight','STATE_SCALAR_WEIGHT',lambda:core.parse_state(raw.replace(b'scalar_weight 819820',b'scalar_weight 950797')))
    gate=dict(status='INDEPENDENT_TERNARY_MIXED_SAVED_OBJECTS_V1_CALIBRATION_PASS',producer='/root/native_driver',
        verifier='/root/checkpoint_audit',method='independent_artifact_check',target_resolution='NONE',inputs_sha256={SCI:PINS[SCI]})
    gate_header(gate,gate['status'])
    for key,value in [('producer','/root'),('verifier','/root/structural'),('method','independent_derivation'),('target_resolution','SOLVED')]:
        q=copy.deepcopy(gate);q[key]=value
        reject('gate_'+key,'CANONICAL_SCIENCE_GATE',lambda q=q:gate_header(q,gate['status']))
    q=copy.deepcopy(gate);q['inputs_sha256']={'CLAIMS.yaml':'1'*64}
    reject('mutable_gate_input','SCIENCE_GATE_CLOSURE',lambda:gate_header(q,gate['status']))
    prefix='build/synthetic_science';summary_name=prefix+'/summary.json'
    raw={prefix+'/'+x:dict(sha256='1'*64,bytes=0) for x in ('invocation.json','native.launch.json','native.receipt.json','native.stdout.log','native.stderr.log')}
    raw.update({prefix+'/native/'+x:dict(sha256='1'*64,bytes=0) for x in ('initial.state','final.state','current.adj','best.adj','moves.jsonl','result.json','zero_selection.json')})
    actual=list(raw)+[summary_name];artifact_population(raw,actual,prefix,summary_name)
    q=copy.deepcopy(raw);del q[prefix+'/native/final.state']
    reject('missing_raw_final','COMPLETE_RAW_ARTIFACT_MAP',lambda:artifact_population(q,actual,prefix,summary_name))
    reject('extra_directory_file','COMPLETE_RAW_DIRECTORY_POPULATION',lambda:artifact_population(raw,actual+[prefix+'/secret.tmp'],prefix,summary_name))
    q=copy.deepcopy(raw);q[prefix+'/native/current.adj']['bytes']=0.0
    reject('raw_bytes_float','RAW_ARTIFACT_DESCRIPTOR',lambda:artifact_population(q,actual,prefix,summary_name))
    q=copy.deepcopy(raw);q[prefix+'/native/undeclared.bin']=dict(sha256='1'*64,bytes=0)
    reject('undeclared_native_name','RAW_ARTIFACT_NAME',lambda:artifact_population(q,list(q)+[summary_name],prefix,summary_name))
    flags={'--'+x:'1' for x in RUN_UINT};flags.update({'--'+x:'0' for x in RUN_REAL})
    flags.update({'--seconds':'110','--native-seconds':'60','--seed':'181','--steps':'12','--schedule-steps':'2048',
        '--temperature-start':'10','--temperature-end':'0','--checkpoint-seconds':'10','--address-space-bytes':'2147483648',
        '--file-bytes':'1073741824','--out':prefix,'--supervision-out':'build/synthetic_supervision','--source-commit':'a'*40})
    for key in RUN_PATHS:flags['--'+key]='build/'+key;flags['--'+key+'-sha256']='1'*64
    flags.update({'--binary':finite.BINARY,'--binary-sha256':PINS[finite.BINARY],
        '--build-manifest':finite.BUILD,'--build-manifest-sha256':PINS[finite.BUILD]})
    command=['/usr/bin/python3',SCI,'run']+[word for key in sorted(flags) for word in (key,flags[key])]
    run=run_options(command)
    plan=dict(command=['python','supervisor','--out','build/synthetic_supervision','--','uv',*command],allocations=dict(outer_seconds=130))
    runtime=dict(command=['uv',*command],seconds=130.,source_sha256=PINS['acceleration/run_compute_command.py'],automatic_retry=False,cumulative_across_commands=False,invocation_id='synthetic')
    terminal=dict(command_exit_code=0,invocation_id='synthetic',error=None,cleanup=dict(reaped=True,job_active_zero_observed=True,cleanup_errors=[],process_group_live_pids=[]))
    summary=dict(command=command,status='CANDIDATE_NATIVE_RUN_PENDING_INDEPENDENT_SAVED_OBJECT_CHECK',independent_approval=False,target_resolution='NONE',automatic_retries=0,actual_exit_code=0)
    invocation=dict(command=command,historical_native_state_written=False,observed_euid=1000,process_group=42,
        independent_approval=False,supervisor_manifest_sha256='2'*64,source_context_commit='a'*40,
        software_sha256={x:PINS[x] for x in (SCI,SCI.replace('.py','_spec.md'),'acceleration/hypergraph_ternary_mixed_anneal_20261003_v1.cpp')})
    run_invocation(summary,invocation,runtime,'2'*64)
    native=['/usr/bin/timeout','--foreground','--signal=TERM','--kill-after=5s','60.000000s','/usr/bin/prlimit',
        '--as=2147483648:2147483648','--fsize=1073741824:1073741824','--core=0:0','/mnt/c/Users/ikuto/projects/conway-99-graph/'+finite.BINARY,
        '--out','/mnt/c/Users/ikuto/projects/conway-99-graph/'+prefix+'/native','--seconds','55.000000','--graph-input',
        '/mnt/c/Users/ikuto/projects/conway-99-graph/'+flags['--wire'],'--source-graph-sha256','3'*64]
    for key in sorted((RUN_UINT-{'address-space-bytes','file-bytes'})|{'temperature-start','temperature-end','checkpoint-seconds'}):native+=['--'+key,flags['--'+key]]
    launch=dict(command=native);receipt=dict(command=native,actual_exit_code=0,observed_euid=1000,reaped=True,error=None,
        automatic_retries=0,process_group=42,child_pid=43,wall_seconds=1.,stdout_sha256='1'*64,stderr_sha256='1'*64)
    native_receipt(launch,receipt,summary,[runtime,terminal],plan,run);receipt_link(receipt,invocation,raw,prefix)
    pos.append(dict(case='synthetic_science_wrapper_native_receipt_and_complete_artifacts',native_calls=0,source_or_output_read=False))
    for label,bad,stage in [('mode',[command[0],SCI,'project',*command[3:]],'SCI_WRAPPER_COMMAND'),
        ('duplicate',command+['--seed','181'],'SCI_WRAPPER_ARGUMENTS'),('omitted',command[:-2],'SCI_WRAPPER_ARGUMENTS'),
        ('unknown',command+['--forced','1'],'SCI_WRAPPER_ARGUMENTS')]:
        reject('wrapper_'+label,stage,lambda bad=bad:run_options(bad))
    for key,value,stage in [('seed','181.0','WIRE_INTEGER'),('steps','0','SCI_WRAPPER_CONFIG'),('native-seconds','NaN','WIRE_REAL'),
        ('source-commit','b'*39,'SCI_WRAPPER_IDENTITIES')]:
        bad=command[:];bad[bad.index('--'+key)+1]=value
        reject('wrapper_'+key,stage,lambda bad=bad:run_options(bad))
    for label,index,value,stage in [('prefix',2,'--signal=KILL','SCI_NATIVE_COMMAND'),('cooperative',13,'54','SCI_NATIVE_LIMIT'),
        ('resource',6,'--as=1:1','SCI_NATIVE_CONFIG'),('binary',9,'build/wrong_binary','SCI_NATIVE_CONFIG'),
        ('seed',native.index('--seed')+1,'182','SCI_NATIVE_CONFIG')]:
        bad=native[:];bad[index]=value
        reject('native_'+label,stage,lambda bad=bad:native_receipt(dict(command=bad),{**receipt,'command':bad},summary,[runtime,terminal],plan,run))
    bad=native+['--forced']
    reject('native_extra_flag','SCI_NATIVE_CONFIG',lambda:native_receipt(dict(command=bad),{**receipt,'command':bad},summary,[runtime,terminal],plan,run))
    for key,value in [('observed_euid',True),('child_pid',False),('actual_exit_code',False),('process_group',0),('wall_seconds',True),
        ('stdout_sha256','g'*64),('reaped',False),('error','error'),('automatic_retries',1)]:
        q=copy.deepcopy(receipt);q[key]=value
        reject('receipt_'+key,'SCI_NATIVE_RECEIPT',lambda q=q:native_receipt(launch,q,summary,[runtime,terminal],plan,run))
    q=copy.deepcopy(summary);q['independent_approval']=True
    reject('summary_ownapproval','SCI_RUN_SUMMARY',lambda:native_receipt(launch,receipt,q,[runtime,terminal],plan,run))
    q=copy.deepcopy(terminal);q['cleanup']['reaped']=False
    reject('outer_live','OUTER_CLEANUP',lambda:native_receipt(launch,receipt,summary,[runtime,q],plan,run))
    q=copy.deepcopy(runtime);q['command']=[]
    reject('outer_command','OUTER_COMMAND',lambda:native_receipt(launch,receipt,summary,[q,terminal],plan,run))
    for key,value in [('historical_native_state_written',True),('observed_euid',True),('supervisor_manifest_sha256','4'*64),('command',[])]:
        q=copy.deepcopy(invocation);q[key]=value
        reject('invocation_'+key,'SCI_RUN_INVOCATION',lambda q=q:run_invocation(summary,q,runtime,'2'*64))
    q=copy.deepcopy(invocation);q['source_context_commit']='b'*40
    reject('invocation_context','SCI_RUN_INVOCATION_COMMAND',lambda:run_invocation(summary,q,runtime,'2'*64))
    q=copy.deepcopy(invocation);q['software_sha256'][SCI]='4'*64
    reject('invocation_source','SCI_RUN_INVOCATION_SOURCE',lambda:run_invocation(summary,q,runtime,'2'*64))
    for key,value in [('stdout_sha256','4'*64),('stderr_sha256','4'*64),('process_group',44)]:
        q=copy.deepcopy(receipt);q[key]=value
        reject('link_'+key,'SCI_NATIVE_LOGS_AND_GROUP',lambda q=q:receipt_link(q,invocation,raw,prefix))
    reject('wrong_stage_harness','WRONG_CONTROL_STAGE:wrong_inner',lambda:reject('wrong_inner','WIRE_INTEGER',lambda:need(False,'TRACE_FIELDS')))
    need(len(pos)==7 and len(neg)==67,'DECLARED_CONTROL_POPULATION')
    return pos,neg


def full(summary,summary_name,plan,runtime,runtime_sha,input_gate,gate_identities,pin,read,tick,save):
    prefix=Path(summary_name).parent.as_posix();directory_root=ROOT/prefix
    raw=summary.get('raw_artifacts')
    actual=[]
    for x in directory_root.rglob('*'):
        tick()
        if x.is_file():actual.append(x.relative_to(ROOT).as_posix())
    artifact_population(raw,actual,prefix,summary_name)
    for name,entry in raw.items():
        need(type(entry) is dict and set(entry)=={'sha256','bytes'},'RAW_ARTIFACT_DESCRIPTOR');pin(name,entry['sha256'],entry['bytes'])
    invocation=read(prefix+'/invocation.json');run=run_invocation(summary,invocation,runtime[0],runtime_sha)
    for name,identity in invocation['software_sha256'].items():pin(name,identity)
    receipt=read(prefix+'/native.receipt.json')
    command,guard,opts,config=native_receipt(read(prefix+'/native.launch.json'),receipt,summary,runtime,plan,run)
    receipt_link(receipt,invocation,raw,prefix)
    need(recorded_name(run['--out'])==prefix and recorded_name(run['--binary'])==finite.BINARY
         and run['--binary-sha256']==PINS[finite.BINARY] and recorded_name(run['--build-manifest'])==finite.BUILD
         and run['--build-manifest-sha256']==PINS[finite.BUILD],'RUN_BUILD_IDENTITY')
    for key,(name,identity) in gate_identities.items():
        need(recorded_name(run['--'+key])==name and run['--'+key+'-sha256']==identity,'RUN_CANONICAL_GATE_IDENTITY:'+key)
    need(run['--seconds']+20<=runtime[0]['seconds']
         and recorded_name(run['--supervision-out'])==recorded_name(plan['command'][plan['command'].index('--out')+1]),'RUN_OUTER_ALLOCATION')
    need('--graph-input' in opts and '--resume' not in opts and opts.get('--forced') is False,'GRAPH_ONLY_NEW_RUN')
    source=input_gate['source_graph_sha256'];need(opts['--source-graph-sha256']==source,'RUN_INPUT_IDENTITY')
    source_file=finite.origin_path(opts['--graph-input']);wire_name=source_file.relative_to(ROOT).as_posix()
    need(wire_name==input_gate['graph_input_path'] and input_gate['inputs_sha256'].get(wire_name)==input_gate['graph_input_sha256']
         and run['--wire-sha256']==input_gate['graph_input_sha256'],'RUN_INPUT_WIRE')
    n,d,input_rows=core.parse_graph(source_file.read_bytes(),source)
    need((n,d)==(99,7),'SCIENTIFIC_TARGET_DOMAIN')
    directory=finite.origin_path(command[11]);names={x.name:x for x in directory.glob('*.state')}
    need('initial.state' in names and 'final.state' in names,'SAVED_INITIAL_FINAL')
    states={};objects=[];scalar_products=0;zero_observations=0
    for name,file in tqdm(sorted(names.items()),desc='Complete saved states',unit='state'):
        tick();s=core.parse_state(finite.wire_bytes(file),source,config)
        need(name in ('initial.state','final.state') or core.re.fullmatch(r'(?:checkpoint|zero_capture)_'+str(s['step'])+r'\.state',name),'STATE_FILENAME_STEP')
        need(s['step'] not in states or same(states[s['step']],s),'SAME_STEP_COMPLETE_STATE');states[s['step']]=s
        for kind in ('current','best'):
            a,m,cn=core.geometry(99,7,s[kind]);other,products=graph_input.scalar(99,7,s[kind]);scalar_products+=9801
            need(same(m,other) and same(cn.tolist(),products),'ALL_SAVED_INTEGER_PRODUCTS')
            objects.append(dict(file=file.relative_to(ROOT).as_posix(),kind=kind,metrics=m,matrix_sha256=hashlib.sha256(core.io.matrix_bytes(a)).hexdigest()))
            if m['F3']==0:
                save('target_candidate_pending_root.json',dict(state=file.relative_to(ROOT).as_posix(),kind=kind,metrics=m,
                    exact_integer_target=core.dense.full_integer_target(a),source_graph_sha256=source))
                raise core.io.AuditError('RAW99_F3ZERO_REQUIRES_ROOT_TARGET_REVIEW')
        zero_observations+=len(s['zeros'])
    initial=core.parse_state(finite.wire_bytes(directory/'initial.state'),source,config)
    final=core.parse_state(finite.wire_bytes(directory/'final.state'),source,config)
    need(initial['step']==0 and same(initial['current'],input_rows) and same(initial['current_metrics'],input_gate['metrics']),'EXACT_NEW_INPUT_RESET')
    end=final['step'];need(end<=opts['--steps'],'REPORTED_NATIVE_COUNTER')
    need(all(step<=end for step in states),'ALL_SAVED_STATE_RANGE')
    captures=[z['step'] for z in final['zeros'] if z['step']>0]
    checkpoints(names,end,opts['--checkpoint-every'],captures)
    for step,s in states.items():
        need(same(s['zeros'],[z for z in final['zeros'] if z['step']<=step]),'COMPLETE_SAVED_ARCHIVE_PREFIX')
    for kind in ('current','best'):
        a,_,_=core.geometry(n,d,final[kind]);need((directory/(kind+'.adj')).read_bytes()==core.io.matrix_bytes(a),'RAW_CURRENT_BEST_MATRIX')
    finite.zero_selection(read((directory/'zero_selection.json').relative_to(ROOT).as_posix()),final,0,False)
    zero_dir=directory/'zero_objects';exports={x.name:x for x in zero_dir.glob('*')} if zero_dir.exists() else {}
    finite.zero_population(exports,len(final['zeros']))
    for j,z in enumerate(final['zeros']):
        tick();a,m,cn=core.geometry(n,d,z['rows']);other,products=graph_input.scalar(n,d,z['rows']);scalar_products+=9801
        need(same(m,other) and same(cn.tolist(),products),'ZERO_OBJECT_INTEGER_PRODUCTS')
        need(exports[f'object_{j}.adj'].read_bytes()==core.io.matrix_bytes(a),'ZERO_EXPORT_MATRIX')
        r=core.Reader(exports[f'object_{j}.triples'].read_bytes());r.tag('TERNARY_RETAINED_ZERO_TRIPLES_V1')
        need([r.integer('step'),r.integer('n'),r.integer('degree')]==[z['step'],n,d]
             and same(r.rows('triples',n,d),z['rows']),'ZERO_EXPORT_TRIPLES');r.end()
    records=[core.io.strict_json(x) for x in finite.wire_bytes(directory/'moves.jsonl').splitlines()]
    trace=trace_audit(records,states,end,opts.get('--trace-prefix',0),opts.get('--trace-stride',0),tick,True)
    result=read((directory/'result.json').relative_to(ROOT).as_posix());elapsed=result.get('elapsed_seconds')
    need(type(elapsed) in (int,float) and not isinstance(elapsed,bool) and math.isfinite(elapsed) and 0<=elapsed<=guard+1,'RESULT_ELAPSED')
    reason=result.get('stop_reason');need(reason in ('REQUESTED_STEPS_COMPLETE','ALLOCATED_NATIVE_BUDGET_REACHED','SIGNAL_STOP_SAVED',
        'RAW_F3_ZERO_PENDING_INDEPENDENT_FULL_INTEGER_SRG_VALIDATOR'),'RESULT_STOP_REASON')
    need(reason!='REQUESTED_STEPS_COMPLETE' or end==opts['--steps'],'COMPLETE_REPORTED_REQUESTED_STEPS')
    expected=dict(objective=core.OBJECTIVE,move_kernel=core.KERNEL,distribution=core.DISTRIBUTION,n=99,point_degree=7,
        initial=initial['current_metrics'],current=final['current_metrics'],best=final['best_metrics'],starting_step=0,ending_step=end,
        proposals_this_invocation=end,admissible_total=final['admissible'],accepted_total=final['accepted'],best_updates_total=final['best_updates'],
        rng_words_total=final['rng_words'],retained_zero_objects=len(final['zeros']),stop_reason=reason,historical_native_state_written=False,
        independent_approval=False,target_resolution=False)
    need(same({k:v for k,v in result.items() if k!='elapsed_seconds'},expected) and same(summary.get('native_result'),result),'RESULT_COMPLETE_LITERAL')
    save('saved_objects.json',objects);save('trace_scope.json',trace)
    return dict(saved_state_files=len(names),distinct_saved_state_steps=len(states),complete_current_best_matrix_observations=len(objects),
        complete_scalar_matrix_products=scalar_products,retained_archive_object_observations=zero_observations,
        final_retained_zero_objects=len(final['zeros']),raw_native_artifacts=len([x for x in raw if '/native/' in x]),
        authenticated_native_reported_proposals=end,requested_proposals=opts['--steps'],stop_reason=reason,
        current=final['current_metrics'],best=final['best_metrics'],trace=trace,target_candidates=0,
        complete_producer_artifacts=len(raw),native_receipt_guard_seconds=guard,native_receipt_cooperative_seconds=core.real(command[13]))


def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['calibration','full']);p.add_argument('--seconds',type=float,required=True)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--self-sha256',required=True);p.add_argument('--spec-sha256',required=True)
    p.add_argument('--expected-head',required=True);p.add_argument('--protected-ledger-sha256',required=True);p.add_argument('--protected-index-sha256',required=True)
    for k in ('engine-gate','input-gate','calibration','producer-summary','producer-plan','runtime-manifest','runtime-summary'):
        p.add_argument('--'+k);p.add_argument('--'+k+'-sha256')
    args=p.parse_args();deadline=CommandDeadline(args.seconds,allocation_reason='Independent changedSCI V2 saved-object calibration/audit;20save, inclusive hashes and no native calls')
    out=args.out.resolve();need(out.is_relative_to(ROOT) and not out.exists(),'FRESH_OUTPUT');out.mkdir(parents=True);pins={};before={}
    def tick():need(not deadline.status()['stop_required'] and deadline.status()['remaining_seconds']>20,'SAVE_RESERVE')
    def pin(name,sha,size=None):
        tick();need(graph_input.name_ok(name) and graph_input.identity(sha),'BOUND_IDENTITY')
        file=(ROOT/name).resolve();need(file.is_relative_to(ROOT) and file.is_file() and file.stat().st_size<=graph_input.CAP,'BOUND_FILE')
        h=hashlib.sha256();total=0
        with file.open('rb') as f:
            while chunk:=f.read(1024*1024):tick();h.update(chunk);total+=len(chunk)
        need(h.hexdigest()==sha and (size is None or type(size) is int and total==size),'INPUT_IDENTITY:'+name)
        need(name not in pins or pins[name]==sha,'INPUT_CONFLICT');pins[name]=sha
    def read(name):return core.io.strict_json((ROOT/name).read_bytes())
    def save(name,obj):(out/name).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n',encoding='utf8')
    def protect():
        values=dict(head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),ledger_sha256=hashlib.sha256((ROOT/'CLAIMS.yaml').read_bytes()).hexdigest(),index_sha256=hashlib.sha256((ROOT/'.git/index').read_bytes()).hexdigest())
        need(same(list(values.values()),[args.expected_head,args.protected_ledger_sha256,args.protected_index_sha256]),'PROTECTED_CONTEXT');return values
    try:
        before=protect()
        for name,sha in {**PINS,SELF:args.self_sha256,SPEC:args.spec_sha256}.items():pin(name,sha)
        objects={}
        for key,status in [('engine_gate','INDEPENDENT_TERNARY_MIXED_ENGINE_V1_CONTROLS_PASS'),('input_gate','INDEPENDENT_TERNARY_MIXED_GRAPH_ONLY_INPUT_V1_COMPLETE_PASS')]:
            name=getattr(args,key);sha=getattr(args,key+'_sha256');need(name is not None and sha is not None,'EXPLICIT_SOURCE_GATES')
            pin(name,sha);value=read(name);gate_header(value,status)
            for file,identity in value['inputs_sha256'].items():pin(file,identity)
            objects[key]=value
        cpp='acceleration/hypergraph_ternary_mixed_anneal_20261003_v1.cpp'
        need(objects['engine_gate']['inputs_sha256'].get(cpp)==PINS[cpp]
             and objects['engine_gate']['inputs_sha256'].get(finite.BINARY)==PINS[finite.BINARY],'EXACT_ENGINE_GATE')
        input_value=objects['input_gate'];wire=input_value.get('graph_input_path')
        need(graph_input.name_ok(wire) and graph_input.identity(input_value.get('graph_input_sha256'))
             and graph_input.identity(input_value.get('source_graph_sha256')) and input_value['inputs_sha256'].get(wire)==input_value['graph_input_sha256']
             and all(input_value['inputs_sha256'].get(x)==PINS[x] for x in (SCI,SCI.replace('.py','_spec.md'))),'EXACT_INPUT_GATE')
        pos,neg=calibration(tick);save('controls.json',dict(positive=pos,strict_negative=neg))
        controls=(out/'controls.json').relative_to(ROOT).as_posix();pin(controls,hashlib.sha256((out/'controls.json').read_bytes()).hexdigest())
        report=dict(status='INDEPENDENT_TERNARY_MIXED_SAVED_OBJECTS_V1_CALIBRATION_PASS',producer='/root/native_driver',
            verifier='/root/checkpoint_audit',method='independent_artifact_check',target_resolution='NONE',mode=args.mode,timestamp=datetime.now(timezone.utc).isoformat(),
            command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),numpy=core.dense.np.__version__,source_sha256=args.self_sha256,
            spec_sha256=args.spec_sha256,positive_controls=len(pos),strict_negative_controls=len(neg),controls=dict(path=controls,sha256=pins[controls]),
            native_calls=0,scientific_output_inspected=False,checker_implementation_version=1,
            immutable_input_gate_dependencies_authenticated=True)
        if args.mode=='full':
            for key in ('calibration','producer_summary','producer_plan','runtime_manifest','runtime_summary'):
                name=getattr(args,key);sha=getattr(args,key+'_sha256');need(name is not None and sha is not None,'EXPLICIT_FULL_IDENTITIES');pin(name,sha);objects[key]=read(name)
            cal=objects['calibration'];gate_header(cal,'INDEPENDENT_TERNARY_MIXED_SAVED_OBJECTS_V1_CALIBRATION_PASS')
            need(cal.get('source_sha256')==args.self_sha256 and cal.get('spec_sha256')==args.spec_sha256,'APPLICABLE_CALIBRATION')
            for key in ('calibration','producer_summary','producer_plan'):
                for file,identity in objects[key]['inputs_sha256'].items():pin(file,identity)
            need(same(cal.get('positive_controls'),7) and same(cal.get('strict_negative_controls'),67),'CALIBRATION_POPULATION')
            identities={'engine-gate':(args.engine_gate,args.engine_gate_sha256),'input-gate':(args.input_gate,args.input_gate_sha256),
                'saved-gate':(args.calibration,args.calibration_sha256)}
            report['saved_raw_scope']=full(objects['producer_summary'],args.producer_summary,objects['producer_plan'],
                [objects['runtime_manifest'],objects['runtime_summary']],args.runtime_manifest_sha256,
                objects['input_gate'],identities,pin,read,tick,save)
            report.update(status='INDEPENDENT_TERNARY_MIXED_SAVED_OBJECTS_V1_COMPLETE_PASS',scientific_output_inspected=True)
            for x in ('saved_objects.json','trace_scope.json'):
                name=(out/x).relative_to(ROOT).as_posix();pin(name,hashlib.sha256((out/x).read_bytes()).hexdigest())
        report.update(inputs_sha256=pins,historical_protected_execution_state=dict(before=before,after=protect(),role='Historical observations outside immutable map'),deadline=deadline.status(),
            shared_components=['Exact independent f4e state/RNG/transition parser,13783 dense/98efe geometry; scalar full products from independent graph-input checker.',
                               'Finite engine checker8271 used only options/zero-export format predicates; no finite main or Native code executed.'],
            limitations=[('Complete all actual saved states/current/best/archive objects; sparse trace full replay only from literal complete anchors.'
                          if args.mode=='full' else 'Own synthetic saved-object/parser/receipt controls only; no actual scientific output, native call or native trajectory inspected.'),
                         'Trace-local RNG/algebra checks do not authenticate missing adjacency at gaps.',
                         'Native proposal counter is authenticated saved result/state metadata; it is not a full scientific trajectory proof.',
                         'Zero archives cover stored distinct RETAINED currents; no unseen earliest event or unrecorded-history completeness inferred.',
                         'Floating acceptance uses Python/libm tolerance and explicit1e-12 minimum margin; no random-quality/performance/coverage/target resolution.'])
        save('summary.json',report)
    except BaseException as error:
        save('failure.json',dict(error=repr(error),inputs_sha256=pins,protected_before=before,deadline=deadline.status(),outputs_preserved=True,automatic_retry=False,native_calls=0,target_resolution='NONE'));raise


if __name__=='__main__':main()
