"""Independent saved-BEST graph-only input checker V3, input implementation2.

Only independent checking helpers are imported. Native projector/SCI parsers
are authenticated source data and never imported or executed. Synthetic BEST
fragments are distinguished from whole valid native states.
"""
import argparse,copy,hashlib,json,platform,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
from command_deadline import CommandDeadline
import audit_20261003_ternary_mixed_graph_input_v1 as G
core=G.core
ROOT=Path(__file__).resolve().parents[1]
SELF='acceleration/audit_20261003_ternary_mixed_saved_best_input_v3.py'
SPEC=SELF.replace('.py','_spec.md')
PROJECT='acceleration/project_20261003_ternary_mixed_saved_best_v2.py'
PROJECT_SHA='0395227419dfb9140480cf58f7c6410940f345c69f2bdf8c54fc96f8a5112307'
PROJECT_SPEC_SHA='cecda6b65b24e1cbba7bb73078cbd4d3266aa82b47925d813a991c43c3e3ca9f'
SAVED='acceleration/audit_20261003_ternary_mixed_saved_objects_v4.py'
SAVED_SHA='0a5399036b97a1d1386bdf5a26e63af537f689421567e36596929a9e2d3a6f2c'
SAVED_SPEC_SHA='80ad0f20610024f363a034c29f23e93e86fd86a46ef0ba2eddf8efb03d62a7b5'
SCI='acceleration/prepare_20261003_ternary_mixed_science_v3.py'
SUP='acceleration/run_compute_command_v2.py'
AUTHOR='acceleration/calibrate_20261003_ternary_mixed_saved_best_v2.py'
PINS={**G.PINS,
 'acceleration/audit_20261003_ternary_mixed_graph_input_v1.py':'79200405fe1b27ba01b4f75075c3c69099a2ce1d57041278e5af5c83efdcf360',
 'acceleration/audit_20261003_ternary_mixed_graph_input_v1_spec.md':'3a4ae18fb9aaff8019a329807f805f52e96577c35ef6cbbec5499be1dd39fac6',
 PROJECT:PROJECT_SHA,PROJECT.replace('.py','_spec.md'):PROJECT_SPEC_SHA,
 SAVED:SAVED_SHA,SAVED.replace('.py','_spec.md'):SAVED_SPEC_SHA,
 SCI:'d1e25078b03719a957e51efb5cbc78f15bf1f8ed1f8039f398285f4a7508927a',
 SCI.replace('.py','_spec.md'):'c2045026b6ead1e545ed93b1d48fe6e8ea6cbe80ca090f6fedda1965ed7cde64',
 SUP:'46410201dcad20eb056b8206a1b6687f9ac74f0f34e3cc66197eff5c59d55e17',
 SUP.replace('.py','_spec.md'):'33e242b6dc28fa783b29825b76311fdc36d16f5cdf1897ca3b41671cafc1acc1',
 AUTHOR:'1c409e176435f75f510c733b47a48d044d3d3c7cf881321bdc34d8693d09dfc1',
 AUTHOR.replace('.py','_spec.md'):'e31c6d562b8db03c4e76b8055eaf3bafcd78facb53c2bea5fa82a0f7889c5bc1',
 # Historical source evidence only; no old approval transfers to projector V2.
 'acceleration/project_20261003_ternary_mixed_saved_best_v1.py':'cc7477213ed0416003168c43f62b4352d6d7e87bf410c185752887b18d00bf99',
 'acceleration/project_20261003_ternary_mixed_saved_best_v1_spec.md':'3ad7d8f620ccdb57d23452c200ebc9617e87110886a8482adfba714a2c41ddde',
 'acceleration/calibrate_20261003_ternary_mixed_saved_best_v1.py':'a9dc7cf5f4849080a5c6713dc11ac7e8c917a3027568983d90d8d7db1079f077',
 'acceleration/calibrate_20261003_ternary_mixed_saved_best_v1_spec.md':'f5e9799e2f789055f62c79c281d9352c3e824d0195dbc7a3da3393b9bd80e595'}
need,same=core.need,core.io.same
CAP=32*1024*1024
ANCESTRY='Complete prerequisite closure retains historical SCI2/spec formatter ancestry; no old input checker approval of this new implementation.'
HEADER=['HYPERGRAPH_TERNARY_MIXED_STATE_V1','objective '+core.OBJECTIVE,
        'move_kernel '+core.KERNEL,'distribution '+core.DISTRIBUTION]
STATUS_CAL='INDEPENDENT_TERNARY_MIXED_GRAPH_ONLY_INPUT_V1_CALIBRATION_PASS'
STATUS_CONTROLS='INDEPENDENT_TERNARY_MIXED_SAVED_BEST_INPUT_V1_CONTROLS_PASS'
STATUS_FULL='INDEPENDENT_TERNARY_MIXED_GRAPH_ONLY_INPUT_V1_COMPLETE_PASS'

def digest(raw):return hashlib.sha256(raw).hexdigest()

def selected_fragment(raw):
    """Independent selected-field reader for labelled synthetic fragments only."""
    need(type(raw)is bytes and len(raw)<=1024*1024,'STATE_BYTES')
    try: text=raw.decode('ascii')
    except UnicodeDecodeError:raise core.io.AuditError('STATE_ASCII')from None
    need(text.endswith('\n')and '\r'not in text,'STATE_NEWLINE')
    lines=text.splitlines();need(lines[:4]==HEADER and lines[-1:]==['END'],'STATE_HEADER')
    fields={k:[]for k in ('n','degree','best','best_metrics')}
    for at,line in enumerate(lines):
        words=line.split(' ')
        if words[0]in fields:fields[words[0]].append((at,words[1:]))
    def values(name,count,stage):
        need(len(fields[name])==1,'BEST_FIELD_UNIQUE:'+name)
        at,words=fields[name][0]
        need(words and all(words),'BEST_FIELD_LAYOUT:'+name)
        need(len(words)==count and all(core.NATURAL.fullmatch(x)is not None and int(x)<2**64 for x in words),stage)
        return at,list(map(int,words))
    n=values('n',1,'BEST_DOMAIN_INTEGER')[1][0];d=values('degree',1,'BEST_DOMAIN_INTEGER')[1][0]
    need((n,d)in((9,2),(12,2),(99,7)),'BEST_DOMAIN')
    at,v=values('best',1,'BEST_COUNT_INTEGER');count=v[0]
    need(count==n*d//3 and at+count<len(lines),'BEST_COUNT')
    rows=[]
    for line in lines[at+1:at+1+count]:
        words=line.split(' ')
        need(len(words)==3 and all(core.NATURAL.fullmatch(x)is not None and int(x)<2**64 for x in words),'BEST_ROW_INTEGER')
        rows.append(list(map(int,words)))
    _,v=values('best_metrics',7,'BEST_METRIC_INTEGER')
    f,el,em,q0,q1,q2,scalar=v
    recorded=dict(F3=f,E_lambda=el,E_mu=em,E=el+em,scalar_weight=core.weight(n,d),scalar=scalar,residue_population=[q0,q1,q2])
    matrix,metrics=G.graph(n,d,rows);need(same(metrics,recorded),'BEST_METRICS')
    return n,d,rows,matrix,metrics

def saved_relation(report,state_name,state_sha,matrix_name,matrix_sha,metrics):
    expected=dict(status='INDEPENDENT_TERNARY_MIXED_SAVED_OBJECTS_V1_COMPLETE_PASS',
        producer='/root/native_driver',verifier='/root/checkpoint_audit',method='independent_artifact_check',target_resolution='NONE')
    need(type(report)is dict and same({k:report.get(k)for k in expected},expected),'SAVED_HEADER')
    need(type(report.get('checker_implementation_version'))is int and report['checker_implementation_version']==4
         and report.get('source_sha256')==SAVED_SHA and report.get('spec_sha256')==SAVED_SPEC_SHA,'SAVED_IMPLEMENTATION')
    inputs=report.get('inputs_sha256')
    need(type(inputs)is dict and inputs and all(G.name_ok(k)and G.identity(v)for k,v in inputs.items()),'SAVED_INPUTS')
    need(inputs.get(state_name)==state_sha and inputs.get(matrix_name)==matrix_sha,'SAVED_BEST_IDENTITIES')
    need(state_name.endswith('/native/final.state')and matrix_name==state_name[:-len('final.state')]+'best.adj','FINAL_BEST_SOURCE_PAIR')
    keys=(SAVED,SAVED.replace('.py','_spec.md'),G.SCI,G.SCI.replace('.py','_spec.md'))
    need(all(inputs.get(k)==PINS[k]for k in keys),'SAVED_ANCESTRY')
    scope=report.get('saved_raw_scope')
    need(type(scope)is dict and same(scope.get('best'),metrics),'SAVED_BEST_METRICS')
    for k in ('saved_state_files','complete_current_best_matrix_observations','complete_scalar_matrix_products'):
        need(type(scope.get(k))is int and scope[k]>0,'SAVED_COMPLETE_SCOPE:'+k)
    need(type(scope.get('authenticated_native_reported_proposals'))is int and scope['authenticated_native_reported_proposals']>0,'SAVED_COMPLETE_SCOPE:proposals')
    return inputs

def projection_relation(p,wire,matrix,s,state_name,state_sha,matrix_name,gate_name,gate_sha):
    expected=dict(schema='TERNARY_MIXED_SAVED_BEST_GRAPH_ONLY_PROJECTION_V1',input_implementation_version=2,
      source_state=state_name,source_state_sha256=state_sha,source_kind='final.best',
      source_matrix=matrix_name,source_matrix_sha256=digest(matrix),prerequisite_saved_full_report=gate_name,
      prerequisite_saved_full_sha256=gate_sha,n=s['n'],point_degree=s['degree'],ordered_triples=s['best'],
      metrics=s['best_metrics'],graph_input_sha256=digest(wire),history_rng_counters_imported=False,native_state_written=False,
      native_calls=0,independent_approval=False,retained_construction_triples_are_all_graph_triangles_claimed=False,historical_ancestry_role=ANCESTRY)
    need(same(p,expected),'RESET_PROJECTION_LITERAL')
    need(same(G.check_wire(wire,matrix,s['n'],s['degree'],s['best']),s['best_metrics']),'RESET_WIRE_METRICS')

def outer(runtime,terminal,plan):
    command=plan.get('command');a=plan.get('allocations')
    need(type(command)is list and '--'in command and all(type(x)is str for x in command),'RESET_OUTER_PLAN')
    need(type(a)is dict and type(a.get('outer_seconds'))is int and a['outer_seconds']>0,'RESET_OUTER_ALLOCATION')
    need(same(runtime.get('command'),command[command.index('--')+1:])and type(runtime.get('seconds'))is float
      and runtime['seconds']==a['outer_seconds']and runtime.get('source_sha256')==PINS[SUP]
      and runtime.get('automatic_retry')is False and runtime.get('cumulative_across_commands')is False,'RESET_OUTER_COMMAND')
    cleanup=terminal.get('cleanup',{})
    need(type(terminal.get('command_exit_code'))is int and terminal['command_exit_code']==0
      and terminal.get('invocation_id')==runtime.get('invocation_id')and terminal.get('error')is None
      and cleanup.get('reaped')is True and type(cleanup.get('actual_exit_code'))is int and cleanup['actual_exit_code']==0
      and cleanup.get('process_group_live_pids')==[]and cleanup.get('cleanup_errors')==[]
      and cleanup.get('process_state_unknown')is not True,'RESET_OUTER_CLEANUP')

def producer_header(summary,metrics,runtime):
    expected=dict(status='CANDIDATE_SAVED_BEST_GRAPH_ONLY_WIRE_PENDING_INDEPENDENT_CHECK',producer='/root/native_driver',
      metrics=metrics,native_calls=0,native_state_written=False,history_rng_counters_imported=False,independent_approval=False,target_resolution='NONE')
    need(same({k:summary.get(k)for k in expected},expected),'RESET_PRODUCER_HEADER')
    inputs=summary.get('inputs_sha256')
    need(type(inputs)is dict and all(inputs.get(k)==v for k,v in ((PROJECT,PROJECT_SHA),(PROJECT.replace('.py','_spec.md'),PROJECT_SPEC_SHA),(SCI,PINS[SCI]),(SCI.replace('.py','_spec.md'),PINS[SCI.replace('.py','_spec.md')]),(SUP,PINS[SUP]))),'RESET_PRODUCER_SOURCE')
    command=summary.get('command')
    need(type(command)is list and len(command)>1 and command[1]==PROJECT
      and runtime.get('command',[])[-(len(command)-1):]==command[1:]and summary.get('cwd')==runtime.get('cwd')
      and type(summary.get('observed_euid'))is int and summary['observed_euid']==1000
      and type(summary.get('process_group'))is int and summary['process_group']>0,'RESET_PRODUCER_COMMAND')

def artifacts(raw,actual,prefix):
    expected={prefix+'/'+name for name in ('graph_input.txt','projection.json')}
    need(type(raw)is dict and set(raw)==expected,'RESET_ARTIFACT_POPULATION')
    need(set(actual)==expected|{prefix+'/summary.json'},'RESET_DIRECTORY_POPULATION')
    for row in raw.values():
        need(type(row)is dict and set(row)=={'sha256','bytes'}and G.identity(row['sha256'])
          and type(row['bytes'])is int and 0<=row['bytes']<=CAP,'RESET_ARTIFACT_DESCRIPTOR')

def author_positives(recorded,fixtures):
    expected=[dict(case=x['case'],binary_matrix_entries=x['complete_integer_matrix_products'],unordered_pair_dot_products=x['pair_scores'],
      metrics=x['metrics'],exact_best_order=True,exact_wire=True,opaque_seed_step_rng_excluded=True,
      full_native_state_fixture=False)for x in fixtures]
    need(same(recorded,expected),'AUTHOR_POSITIVES')

BUDGET_POSITIVE=(('budget_above_reserve',20.000001),('budget_full_worker',100.0))
BUDGET_NEGATIVE=(('budget_at_reserve',20.0,False),('budget_below_reserve',19.0,False),
                 ('budget_expired',0.0,False),('budget_stop_required',100.0,True))

class SyntheticDeadline:
    def __init__(self,remaining,stopped):
        self.snapshot=dict(remaining_seconds=remaining,stop_required=stopped);self.calls=0
    def status(self):
        self.calls+=1;return dict(self.snapshot)

def check_budget(deadline):
    """Independent one-snapshot reconstruction of the frozen cooperative predicate."""
    snapshot=deadline.status()
    need(snapshot['remaining_seconds']>20 and not snapshot['stop_required'],'SAVE_RESERVE')

def author_budget_positives(recorded):
    expected=[dict(case=label,snapshot=dict(remaining_seconds=remaining,stop_required=False),
      status_reads=1,accepted=True)for label,remaining in BUDGET_POSITIVE]
    need(same(recorded,expected),'AUTHOR_BUDGET_POSITIVES')

def author_population(actual,prefix,patterns):
    expected={prefix+'/'+label+'.'+ext for label in ('rook9','cube12','cyclic99_initializer')
      for ext in ('synthetic_fragment','adj','wire','rows.json')}
    expected.update(prefix+'/'+name for name in ('summary.json','controls.json','synthetic_report.json'))
    expected.update(prefix+'/'+label+'.json'for label,_,_ in patterns[22:])
    expected.update(prefix+'/'+label+'.json'for label,_,_ in BUDGET_NEGATIVE)
    need(type(actual)is set and actual==expected and len(expected)==39,'AUTHOR_DIRECTORY_POPULATION')

def fragment(n,d,rows,m):
    v=[m['F3'],m['E_lambda'],m['E_mu'],*m['residue_population'],m['scalar']]
    return ('\n'.join(HEADER+[f'n {n}',f'degree {d}','seed 3','step 7','rng opaque-not-parsed',
      'best_metrics '+' '.join(map(str,v)),'best '+str(len(rows)),*[' '.join(map(str,row))for row in rows],
      'zero_archive opaque-not-parsed','END'])+'\n').encode('ascii')

def synthetic_report(state_name,state_sha,matrix_name,matrix_sha,m):
    return dict(status='INDEPENDENT_TERNARY_MIXED_SAVED_OBJECTS_V1_COMPLETE_PASS',producer='/root/native_driver',
      verifier='/root/checkpoint_audit',method='independent_artifact_check',target_resolution='NONE',
      checker_implementation_version=4,source_sha256=SAVED_SHA,spec_sha256=SAVED_SPEC_SHA,
      inputs_sha256={state_name:state_sha,matrix_name:matrix_sha,**{k:PINS[k]for k in (SAVED,SAVED.replace('.py','_spec.md'),G.SCI,G.SCI.replace('.py','_spec.md'))}},
      saved_raw_scope=dict(best=m,saved_state_files=1,complete_current_best_matrix_observations=2,
      complete_scalar_matrix_products=162,authenticated_native_reported_proposals=7))

def rejection(rows,label,stage,call):
    try:call()
    except core.io.AuditError as error:
        need(error.stage==stage,'WRONG_CONTROL_STAGE:'+label)
        rows.append(dict(case=label,expected_stage=stage,actual_stage=error.stage))
    else:raise core.io.AuditError('CONTROL_ACCEPTED:'+label)

def independent_author_stage(label,producer_stage):
    """Keep producer diagnostics literal; independently name our geometry route."""
    if label=='repeated_point':
        need(producer_stage=='TRIPLE_DISTINCT','AUTHOR_STAGE_PAIR_LITERAL')
        return 'DOMAIN_ROW_DISTINCT'
    return producer_stage

def author_patterns(raw,report,state_name,state_sha,matrix_name,matrix_sha,m):
    """Literal42 saved author cases, reconstructed without executing that source."""
    rows=[]
    add=lambda label,stage,call:rows.append((label,stage,call))
    for label,bad,stage in [('nonbytes','x','STATE_BYTES'),('oversize',b'x'*(1024*1024+1),'STATE_BYTES'),
      ('nonascii',raw+b'\xff','STATE_ASCII'),('crlf',raw.replace(b'\n',b'\r\n'),'STATE_NEWLINE'),
      ('no_newline',raw[:-1],'STATE_NEWLINE'),('wrong_header',raw.replace(b'HYPERGRAPH_',b'WRONG_',1),'STATE_HEADER'),
      ('wrong_end',raw.replace(b'END\n',b'OTHER\n'),'STATE_HEADER')]:
        add(label,stage,lambda bad=bad:selected_fragment(bad))
    for key in ('n','degree','best','best_metrics'):
        line=next(x for x in raw.splitlines()if x.startswith(key.encode()+b' '))
        bad=raw.replace(line+b'\n',line+b'\n'+line+b'\n',1)
        add('duplicate_'+key,'BEST_FIELD_UNIQUE:'+key,lambda bad=bad:selected_fragment(bad))
    for label,old,new,stage in [('bool_n',b'n 9\n',b'n True\n','BEST_DOMAIN_INTEGER'),
      ('float_degree',b'degree 2\n',b'degree 2.0\n','BEST_DOMAIN_INTEGER'),('bad_domain',b'n 9\n',b'n 10\n','BEST_DOMAIN'),
      ('float_count',b'best 6\n',b'best 6.0\n','BEST_COUNT_INTEGER'),('wrong_count',b'best 6\n',b'best 5\n','BEST_COUNT'),
      ('bool_row',b'0 1 2\n',b'False 1 2\n','BEST_ROW_INTEGER'),('float_row',b'0 1 2\n',b'0.0 1 2\n','BEST_ROW_INTEGER'),
      ('repeated_point',b'0 1 2\n',b'0 0 2\n','TRIPLE_DISTINCT'),('negative_row',b'0 1 2\n',b'-1 1 2\n','BEST_ROW_INTEGER'),
      ('bad_metric',b'best_metrics 0 0 0 36 0 0 0\n',b'best_metrics 1 0 0 36 0 0 0\n','BEST_METRICS'),
      ('float_metric',b'best_metrics 0 0 0 36 0 0 0\n',b'best_metrics 0.0 0 0 36 0 0 0\n','BEST_METRIC_INTEGER')]:
        bad=raw.replace(old,new,1);need(bad!=raw,'CONTROL_MUTATION');add(label,stage,lambda bad=bad:selected_fragment(bad))
    for key,value,stage in [('status','OTHER','SAVED_HEADER'),('producer','/root','SAVED_HEADER'),('verifier','/root/structural','SAVED_HEADER'),
      ('method','independent_derivation','SAVED_HEADER'),('target_resolution',True,'SAVED_HEADER'),
      ('checker_implementation_version',4.0,'SAVED_IMPLEMENTATION'),('source_sha256','0'*64,'SAVED_IMPLEMENTATION'),
      ('spec_sha256','0'*64,'SAVED_IMPLEMENTATION'),('inputs_sha256',{},'SAVED_INPUTS')]:
        q=copy.deepcopy(report);q[key]=value
        add('report_'+key,stage,lambda q=q:saved_relation(q,state_name,state_sha,matrix_name,matrix_sha,m))
    for key in (state_name,matrix_name,SAVED,SAVED.replace('.py','_spec.md'),G.SCI,G.SCI.replace('.py','_spec.md')):
        label='closure_'+str(len(rows));q=copy.deepcopy(report);q['inputs_sha256'][key]='0'*64
        stage='SAVED_BEST_IDENTITIES'if key in(state_name,matrix_name)else'SAVED_ANCESTRY'
        add(label,stage,lambda q=q:saved_relation(q,state_name,state_sha,matrix_name,matrix_sha,m))
    for key,value,stage in [('best',dict(m,F3=False),'SAVED_BEST_METRICS'),('saved_state_files',True,'SAVED_COMPLETE_SCOPE:saved_state_files'),
      ('complete_current_best_matrix_observations',0,'SAVED_COMPLETE_SCOPE:complete_current_best_matrix_observations'),
      ('complete_scalar_matrix_products',162.0,'SAVED_COMPLETE_SCOPE:complete_scalar_matrix_products'),
      ('authenticated_native_reported_proposals',False,'SAVED_COMPLETE_SCOPE:proposals')]:
        q=copy.deepcopy(report);q['saved_raw_scope'][key]=value
        add('scope_'+key,stage,lambda q=q:saved_relation(q,state_name,state_sha,matrix_name,matrix_sha,m))
    need(len(rows)==42,'AUTHOR_PATTERN_POPULATION');return rows

def calibration(tick):
    positives=[];negatives=[]
    for label in ('rook9','cube12','target99'):
        tick();s=core.initial(label);whole=core.serialize(s);parsed=core.parse_state(whole)
        matrix,m=G.graph(s['n'],s['degree'],s['best'])
        need(same(parsed['best'],s['best'])and same(parsed['best_metrics'],m),'KNOWN_WHOLE_STATE')
        wire=G.canonical_wire(s['n'],s['degree'],s['best'],digest(matrix))
        G.check_wire(wire,matrix,s['n'],s['degree'],s['best'])
        positives.append(dict(case=label,whole_native_state=True,adjacency_entries=s['n']**2,integer_matrix_products=s['n']**2,pair_scores=s['n']*(s['n']-1)//2,metrics=m))
        other=core.initial(label,seed=88);core.parse_state(core.serialize(other))
        need(same(other['best'],s['best'])and G.canonical_wire(s['n'],s['degree'],other['best'],digest(matrix))==wire,'HISTORY_EXCLUSION')
        positives.append(dict(case=label+'_fresh_seed_same_graph',whole_native_state=True,new_seed=88,wire_equal=True))
    s=core.initial('rook9');whole=core.serialize(s);matrix,m=G.graph(9,2,s['best'])
    raw=fragment(9,2,s['best'],m);n,d,rows,rebuilt,recorded=selected_fragment(raw)
    need(same([n,d,rows,recorded],[9,2,s['best'],m])and rebuilt==matrix,'KNOWN_FRAGMENT')
    positives.append(dict(case='synthetic_selected_best_fragment',whole_native_state=False))
    state_name='synthetic/native/final.state';matrix_name='synthetic/native/best.adj';gate_name='synthetic/saved_full.json'
    report=synthetic_report(state_name,digest(raw),matrix_name,digest(matrix),m)
    saved_relation(report,state_name,digest(raw),matrix_name,digest(matrix),m)
    positives.append(dict(case='synthetic_saved_report_relation',executed_saved_gate=False))
    for label,stage,call in author_patterns(raw,report,state_name,digest(raw),matrix_name,digest(matrix),m):
        tick();rejection(negatives,label,independent_author_stage(label,stage),call)
        negatives[-1].update(original_producer_expected_stage=stage,original_producer_actual_stage=None,
          original_producer_actual_stage_unavailable_reason='Own calibration reads no actual producer control records; the original producer stage is a frozen source expectation only.')
    wire=G.canonical_wire(9,2,s['best'],digest(matrix));gate_sha='1'*64
    p=dict(schema='TERNARY_MIXED_SAVED_BEST_GRAPH_ONLY_PROJECTION_V1',input_implementation_version=2,source_state=state_name,
      source_state_sha256=digest(raw),source_kind='final.best',source_matrix=matrix_name,source_matrix_sha256=digest(matrix),
      prerequisite_saved_full_report=gate_name,prerequisite_saved_full_sha256=gate_sha,n=9,point_degree=2,ordered_triples=s['best'],
      metrics=m,graph_input_sha256=digest(wire),history_rng_counters_imported=False,native_state_written=False,native_calls=0,
      independent_approval=False,retained_construction_triples_are_all_graph_triangles_claimed=False,historical_ancestry_role=ANCESTRY)
    call=lambda q=p,w=wire:projection_relation(q,w,matrix,s,state_name,digest(raw),matrix_name,gate_name,gate_sha)
    call();positives.append(dict(case='synthetic_projection_and_wire',actual_projection=False))
    for key,value in [('schema','OTHER'),('input_implementation_version',2.0),('source_state','other/native/final.state'),('source_state_sha256','0'*64),
      ('source_kind','current'),('source_matrix_sha256','0'*64),('prerequisite_saved_full_report','other'),('prerequisite_saved_full_sha256','0'*64),
      ('n',True),('point_degree',2.0),('ordered_triples',s['best'][::-1]),('metrics',dict(m,F3=False)),
      ('graph_input_sha256','0'*64),('history_rng_counters_imported',True),('native_state_written',True),('native_calls',False),
      ('independent_approval',True),('retained_construction_triples_are_all_graph_triangles_claimed',True),('historical_ancestry_role','old approval')]:
        q=copy.deepcopy(p);q[key]=value;rejection(negatives,'projection_'+key,'RESET_PROJECTION_LITERAL',lambda q=q:call(q=q))
    for label,bad,stage in [('source',wire.replace(digest(matrix).encode(),b'0'*64),'GRAPH_SOURCE_IDENTITY'),
      ('newline',wire.replace(b'\n',b'\r\n'),'CANONICAL_WIRE_BYTES'),('trailing',wire+b'junk','WIRE_TRAILING'),
      ('bool_n',wire.replace(b'n 9\n',b'n True\n'),'WIRE_INTEGER')]:
        rejection(negatives,'wire_'+label,stage,lambda bad=bad:G.check_wire(bad,matrix,9,2,s['best']))
    runtime=dict(command=['uv','python',PROJECT],seconds=120.,source_sha256=PINS[SUP],automatic_retry=False,cumulative_across_commands=False,invocation_id='synthetic',cwd=str(ROOT))
    terminal=dict(command_exit_code=0,invocation_id='synthetic',error=None,cleanup=dict(reaped=True,actual_exit_code=0,process_group_live_pids=[],cleanup_errors=[],process_state_unknown=False))
    plan=dict(command=['python',SUP,'--','uv','python',PROJECT],allocations=dict(outer_seconds=120))
    outer(runtime,terminal,plan);positives.append(dict(case='synthetic_linux_runtime',executed_native=False))
    for key,value in [('seconds',120),('source_sha256','0'*64),('automatic_retry',True),('command',['wrong'])]:
        q=copy.deepcopy(runtime);q[key]=value;rejection(negatives,'runtime_'+key,'RESET_OUTER_COMMAND',lambda q=q:outer(q,terminal,plan))
    for key,value in [('reaped',False),('actual_exit_code',False),('process_group_live_pids',[7]),('process_state_unknown',True)]:
        q=copy.deepcopy(terminal);q['cleanup'][key]=value;rejection(negatives,'cleanup_'+key,'RESET_OUTER_CLEANUP',lambda q=q:outer(runtime,q,plan))
    for label,bad,stage in [('cache',whole.replace(b'cn 36\n1',b'cn 36\n2',1),'STATE_CN_CACHE'),
      ('source',whole.replace(b'source_graph_sha256 ',b'other ',1),'WIRE_FIELD:source_graph_sha256'),
      ('trailing',whole+b'junk','WIRE_TRAILING')]:
        need(bad!=whole,'CONTROL_MUTATION');rejection(negatives,'whole_'+label,stage,lambda bad=bad:core.parse_state(bad))
    for label,data in [('duplicate',b'{"x":1,"x":2}'),('nan',b'{"x":NaN}')]:
        rejection(negatives,'json_'+label,'JSON',lambda data=data:core.io.strict_json(data))
    rejection(negatives,'wrong_stage_harness','WRONG_CONTROL_STAGE:inner',lambda:rejection([], 'inner','JSON',lambda:need(False,'STATE_BYTES')))
    budget_positive=[]
    for label,remaining in BUDGET_POSITIVE:
        tick();synthetic=SyntheticDeadline(remaining,False);check_budget(synthetic)
        need(synthetic.calls==1,'ONE_BUDGET_SNAPSHOT')
        row=dict(case=label,snapshot=synthetic.snapshot,status_reads=synthetic.calls,accepted=True)
        budget_positive.append(row);positives.append(row)
    for label,remaining,stopped in BUDGET_NEGATIVE:
        tick();synthetic=SyntheticDeadline(remaining,stopped)
        rejection(negatives,label,'SAVE_RESERVE',lambda synthetic=synthetic:check_budget(synthetic))
        need(synthetic.calls==1,'ONE_BUDGET_SNAPSHOT')
        negatives[-1].update(original_producer_expected_stage='SAVE_RESERVE',original_producer_actual_stage=None,
          original_producer_actual_stage_unavailable_reason='Own calibration reads no actual producer budget records; the producer stage is a frozen source expectation only.')
    author_budget_positives(budget_positive)
    for label,change in [('status_reads_bool',lambda x:x[0].update(status_reads=True)),
      ('reserve_snapshot',lambda x:x[0]['snapshot'].update(remaining_seconds=20.0))]:
        q=copy.deepcopy(budget_positive);change(q)
        rejection(negatives,'author_budget_'+label,'AUTHOR_BUDGET_POSITIVES',lambda q=q:author_budget_positives(q))
    fixture=[dict(case='synthetic',complete_integer_matrix_products=81,pair_scores=36,metrics=m)]
    records=[dict(case='synthetic',binary_matrix_entries=81,unordered_pair_dot_products=36,metrics=m,exact_best_order=True,
      exact_wire=True,opaque_seed_step_rng_excluded=True,full_native_state_fixture=False)]
    author_positives(records,fixture)
    for label,change in [('bool_count',lambda x:x[0].update(binary_matrix_entries=True)),
      ('false_whole_state',lambda x:x[0].update(full_native_state_fixture=True)),
      ('unordered_bool_count',lambda x:x[0].update(unordered_pair_dot_products=True))]:
        q=copy.deepcopy(records);change(q)
        rejection(negatives,'author_'+label,'AUTHOR_POSITIVES',lambda q=q:author_positives(q,fixture))
    patterns=author_patterns(raw,report,state_name,digest(raw),matrix_name,digest(matrix),m)
    names={'synthetic/'+label+'.'+ext for label in ('rook9','cube12','cyclic99_initializer')
      for ext in ('synthetic_fragment','adj','wire','rows.json')}
    names.update('synthetic/'+name for name in ('summary.json','controls.json','synthetic_report.json'))
    names.update('synthetic/'+label+'.json'for label,_,_ in patterns[22:])
    names.update('synthetic/'+label+'.json'for label,_,_ in BUDGET_NEGATIVE);author_population(names,'synthetic',patterns)
    for label,values in [('missing_saved_corruption',names-{'synthetic/report_status.json'}),('extra_file',names|{'synthetic/extra.bin'})]:
        rejection(negatives,'author_'+label,'AUTHOR_DIRECTORY_POPULATION',lambda values=values:author_population(values,'synthetic',patterns))
    need((len(positives),len(negatives))==(12,90),'DECLARED_OWN_CONTROLS')
    return positives,negatives

def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=('calibration','controls','full'))
    p.add_argument('--seconds',type=float,required=True);p.add_argument('--out',type=Path,required=True)
    for k in ('self','spec'):p.add_argument('--'+k+'-sha256',required=True)
    for k in ('expected-head','protected-ledger-sha256','protected-index-sha256'):p.add_argument('--'+k,required=True)
    for k in ('calibration','controls-gate','author-summary','author-controls','author-runtime-manifest','author-runtime-summary','author-plan',
              'author-count-correction','saved-gate','state','matrix','producer-summary','producer-plan','runtime-manifest','runtime-summary'):
        p.add_argument('--'+k);p.add_argument('--'+k+'-sha256')
    args=p.parse_args();deadline=CommandDeadline(args.seconds,allocation_reason='New saved-BEST independent input implementation2: inclusive hashes/own controls/selected fragment replay or whole-state/raw matrix/wire checking;20save; no native/search')
    out=args.out.resolve();need(out.is_relative_to(ROOT)and not out.exists(),'FRESH_OUTPUT');out.mkdir(parents=True)
    pins={};before={}
    def tick():snap=deadline.status();need(not snap['stop_required']and snap['remaining_seconds']>20,'SAVE_RESERVE')
    def pin(name,sha,size=None):
        tick();need(G.name_ok(name)and G.identity(sha),'BOUND_IDENTITY')
        file=(ROOT/name).resolve();need(file.is_relative_to(ROOT)and file.is_file()and file.stat().st_size<=CAP,'BOUND_FILE')
        h=hashlib.sha256();count=0
        with file.open('rb')as f:
            while block:=f.read(1024*1024):tick();h.update(block);count+=len(block)
        need(h.hexdigest()==sha and(size is None or type(size)is int and size==count),'INPUT_IDENTITY:'+name)
        need(name not in pins or pins[name]==sha,'INPUT_CONFLICT');pins[name]=sha;return file
    def read(name):return core.io.strict_json((ROOT/name).read_bytes())
    def save(name,value):(out/name).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    def protect():
        tick();head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True,timeout=deadline.child_seconds(10,reserve_seconds=20)).strip()
        row=dict(head=head,ledger_sha256=digest((ROOT/'CLAIMS.yaml').read_bytes()),index_sha256=digest((ROOT/'.git/index').read_bytes()))
        need(same(list(row.values()),[args.expected_head,args.protected_ledger_sha256,args.protected_index_sha256]),'PROTECTED_CONTEXT');return row
    def object_arg(k):
        name=getattr(args,k);sha=getattr(args,k+'_sha256');need(name is not None and sha is not None,'EXPLICIT_IDENTITIES')
        pin(name,sha);return read(name)if k not in('state','matrix')else(ROOT/name).read_bytes()
    def closure(row):
        values=row.get('inputs_sha256');need(type(values)is dict and values,'IMMUTABLE_CLOSURE')
        for name,sha in values.items():pin(name,sha)
    try:
        before=protect()
        for name,sha in {**PINS,SELF:args.self_sha256,SPEC:args.spec_sha256}.items():pin(name,sha)
        pos,neg=calibration(tick);save('controls.json',dict(positive=pos,strict_negative=neg))
        controls=(out/'controls.json').relative_to(ROOT).as_posix();pin(controls,digest((out/'controls.json').read_bytes()))
        result=dict(status=STATUS_CAL,checker_implementation_version=3,input_implementation_version=2,producer='/root/native_driver',verifier='/root/checkpoint_audit',
          method='independent_artifact_check',target_resolution='NONE',source_sha256=args.self_sha256,spec_sha256=args.spec_sha256,
          timestamp=datetime.now(timezone.utc).isoformat(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),
          numpy=core.dense.np.__version__,mode=args.mode,positive_controls=len(pos),strict_negative_controls=len(neg),
          controls=dict(path=controls,sha256=pins[controls]),native_calls=0,actual_saved_target_read=False,
          history_rng_counters_imported=False,native_state_written=False,retained_construction_triples_are_all_graph_triangles_claimed=False)
        if args.mode!='calibration':
            cal=object_arg('calibration');need(cal.get('status')==STATUS_CAL and cal.get('input_implementation_version')==2
              and cal.get('checker_implementation_version')==3
              and cal.get('source_sha256')==args.self_sha256 and cal.get('spec_sha256')==args.spec_sha256,'APPLICABLE_CALIBRATION');closure(cal)
        if args.mode=='controls':
            summary=object_arg('author_summary');records=object_arg('author_controls')
            runtime=object_arg('author_runtime_manifest');terminal=object_arg('author_runtime_summary');plan=object_arg('author_plan')
            correction=object_arg('author_count_correction')
            need(summary.get('status')=='AUTHOR_TERNARY_MIXED_SAVED_BEST_V2_SYNTHETIC_CONTROLS_PASS'
              and summary.get('producer')=='/root/native_driver'and same([summary.get(k)for k in('geometry_fixture_positives','synthetic_report_positives','strict_negative_cases','opaque_history_exclusion_equalities',
              'preserved_extractor_report_strict_negative_cases','budget_predicate_positives','budget_predicate_strict_negative_cases',
              'binary_matrix_entries','unordered_pair_dot_products','actual_saved_target_input_read','actual_saved_report_read','native_calls','same_author_controls_only','independent_approval')],
              [3,1,46,3,42,2,4,10026,4953,False,False,0,True,False]),'AUTHOR_SCOPE')
            closure(summary);outer(runtime,terminal,plan)
            need(records.get('synthetic_report_relation_positive')is True,'AUTHOR_POSITIVES')
            prefix=Path(args.author_summary).parent.as_posix();parsed=[]
            for label in ('rook9','cube12','cyclic99_initializer'):
                for ext in ('synthetic_fragment','adj','wire','rows.json'):
                    name=prefix+'/'+label+'.'+ext;pin(name,digest((ROOT/name).read_bytes()))
                raw=(ROOT/(prefix+'/'+label+'.synthetic_fragment')).read_bytes()
                n,d,rows,matrix,m=selected_fragment(raw);G.check_wire((ROOT/(prefix+'/'+label+'.wire')).read_bytes(),matrix,n,d,rows)
                expected_fixture=core.fixture('target99'if label=='cyclic99_initializer'else label)
                need(same([n,d,rows],list(expected_fixture)),'AUTHOR_FROZEN_FIXTURE')
                need(matrix==(ROOT/(prefix+'/'+label+'.adj')).read_bytes()
                  and same(read(prefix+'/'+label+'.rows.json'),dict(n=n,point_degree=d,ordered_triples=rows,metrics=m)),'AUTHOR_LITERAL_FIXTURE')
                changed=raw.replace(b'seed 3\nstep 7\nrng opaque-not-parsed',b'seed 88\nstep 12345\nrng different-opaque')
                need(same(selected_fragment(raw)[:3],selected_fragment(changed)[:3])and selected_fragment(changed)[3]==matrix,'AUTHOR_OPAQUE_EXCLUSION')
                parsed.append(dict(case=label,complete_integer_matrix_products=n*n,pair_scores=n*(n-1)//2,metrics=m,whole_native_state_fixture=False))
            author_positives(records.get('positive'),parsed)
            name=prefix+'/synthetic_report.json';pin(name,digest((ROOT/name).read_bytes()));report=read(name)
            raw=(ROOT/(prefix+'/rook9.synthetic_fragment')).read_bytes();n,d,rows,matrix,m=selected_fragment(raw)
            saved_relation(report,'synthetic/native/final.state',digest(raw),'synthetic/native/best.adj',digest(matrix),m)
            patterns=author_patterns(raw,report,'synthetic/native/final.state',digest(raw),'synthetic/native/best.adj',digest(matrix),m)
            population={x.relative_to(ROOT).as_posix()for x in(ROOT/prefix).rglob('*')if x.is_file()}
            author_population(population,prefix,patterns)
            expected=[];observed=[]
            for at,(label,stage,call)in enumerate(patterns):
                tick();expected.append(dict(case=label,expected_stage=stage,actual_stage=stage))
                independent_stage=independent_author_stage(label,stage)
                file=ROOT/prefix/(label+'.json')
                if at>=22:
                    pin(file.relative_to(ROOT).as_posix(),digest(file.read_bytes()));q=read(file.relative_to(ROOT).as_posix())
                    rejection(observed,label,independent_stage,lambda q=q:saved_relation(q,'synthetic/native/final.state',digest(raw),'synthetic/native/best.adj',digest(matrix),m))
                else:rejection(observed,label,independent_stage,call)
            budget_positive=[]
            for label,remaining in BUDGET_POSITIVE:
                tick();synthetic=SyntheticDeadline(remaining,False);check_budget(synthetic)
                need(synthetic.calls==1,'ONE_BUDGET_SNAPSHOT')
                budget_positive.append(dict(case=label,snapshot=synthetic.snapshot,status_reads=synthetic.calls,accepted=True))
            author_budget_positives(records.get('budget_predicate_positive'))
            need(same(records['budget_predicate_positive'],budget_positive),'AUTHOR_BUDGET_POSITIVES')
            for label,remaining,stopped in BUDGET_NEGATIVE:
                tick();name=prefix+'/'+label+'.json';pin(name,digest((ROOT/name).read_bytes()));snapshot=read(name)
                need(same(snapshot,dict(remaining_seconds=remaining,stop_required=stopped)),'AUTHOR_BUDGET_SNAPSHOT')
                synthetic=SyntheticDeadline(snapshot['remaining_seconds'],snapshot['stop_required'])
                rejection(observed,label,'SAVE_RESERVE',lambda synthetic=synthetic:check_budget(synthetic))
                need(synthetic.calls==1,'ONE_BUDGET_SNAPSHOT')
                expected.append(dict(case=label,expected_stage='SAVE_RESERVE',actual_stage='SAVE_RESERVE'))
            need(same(records.get('strict_negative'),expected),'AUTHOR_ALL46_SAVED_NEGATIVES')
            for row,original in zip(observed,records['strict_negative']):
                row.update(original_producer_expected_stage=original['expected_stage'],original_producer_actual_stage=original['actual_stage'])
            need(sum(x['complete_integer_matrix_products']for x in parsed)==10026 and sum(x['pair_scores']for x in parsed)==4953,'AUTHOR_INDEPENDENT_PRODUCTS')
            save('author_replay.json',dict(fixtures=parsed,strict_negative=observed,budget_predicate_positive=budget_positive,
              historical_count_correction_sha256=args.author_count_correction_sha256,
              author_oracle_scope='AuthorV2 reports10026 binary adjacency entries and4953 unordered-pair products; this checker independently recomputes10026 complete matrix products including diagonals.',
              budget_predicate_scope='Two accepted/four rejected one-snapshot synthetic predicates only; no blocking-I/O, actual final-write timing or generic containment guarantee.',whole_native_state_fixture=False))
            result.update(status=STATUS_CONTROLS,author_fixture_count=3,author_synthetic_report_count=1,author_opaque_equalities=3,
              author_strict_negative_controls=46,preserved_author_extractor_report_negatives=42,
              author_budget_predicate_positives=2,author_budget_predicate_strict_negatives=4,
              complete_integer_matrix_products=10026,unordered_pair_scores=4953,
              historical_author_count_correction_bound=True,actual_saved_target_read=False,retained_author_corrupt_report_files=20,
              retained_author_budget_snapshot_files=4,author_raw_corruption_patterns_reconstructed_from_frozen_source=22,complete_author_directory_files=39)
        if args.mode=='full':
            cg=object_arg('controls_gate');need(cg.get('status')==STATUS_CONTROLS and cg.get('source_sha256')==args.self_sha256
              and cg.get('spec_sha256')==args.spec_sha256 and cg.get('input_implementation_version')==2
              and cg.get('checker_implementation_version')==3,'APPLICABLE_AUTHOR_CONTROLS');closure(cg)
            checked=object_arg('saved_gate');raw=object_arg('state');matrix=object_arg('matrix')
            summary=object_arg('producer_summary');plan=object_arg('producer_plan');runtime=object_arg('runtime_manifest');terminal=object_arg('runtime_summary')
            need(len(raw)<=1024*1024,'WHOLE_STATE_SIZE');s=core.parse_state(raw)
            need((s['n'],s['degree'])==(99,7),'ACTUAL_TARGET_DOMAIN')
            rebuilt,m=G.graph(99,7,s['best']);need(rebuilt==matrix and same(m,s['best_metrics']),'WHOLE_BEST_MATRIX')
            closure_map=saved_relation(checked,args.state,args.state_sha256,args.matrix,args.matrix_sha256,m)
            for name,sha in closure_map.items():pin(name,sha)
            closure(summary);closure(plan);outer(runtime,terminal,plan);producer_header(summary,m,runtime)
            prefix=Path(args.producer_summary).parent.as_posix();population={x.relative_to(ROOT).as_posix()for x in(ROOT/prefix).rglob('*')if x.is_file()}
            artifacts(summary.get('raw_artifacts'),population,prefix)
            for name,row in summary['raw_artifacts'].items():pin(name,row['sha256'],row['bytes'])
            wire_name=prefix+'/graph_input.txt';projection=read(prefix+'/projection.json')
            projection_relation(projection,(ROOT/wire_name).read_bytes(),matrix,s,args.state,args.state_sha256,args.matrix,args.saved_gate,args.saved_gate_sha256)
            result.update(status=STATUS_FULL,actual_saved_target_read=True,n=99,point_degree=7,ordered_triples=231,
              graph_input_path=wire_name,graph_input_sha256=pins[wire_name],source_graph_sha256=args.matrix_sha256,
              source_kind='final.best',source_state_path=args.state,source_state_sha256=args.state_sha256,
              source_matrix_path=args.matrix,source_matrix_sha256=args.matrix_sha256,
              prerequisite_saved_full_report_path=args.saved_gate,prerequisite_saved_full_report_sha256=args.saved_gate_sha256,
              metrics=m,complete_integer_matrix_products=9801,unordered_pair_scores=4851,whole_source_state_checked=True,
              source_state_history_authenticated_but_not_imported=True)
            if m['F3']==0 and m['E']==0:
                save('target_candidate_pending_root.json',dict(matrix=args.matrix,sha256=args.matrix_sha256,metrics=m))
                raise core.io.AuditError('FULL99_IDENTITY_ZERO_PENDING_ROOT')
        result.update(inputs_sha256=pins,historical_protected_execution_state=dict(before=before,after=protect(),role='Protected historical observations outside immutable source dependency map'),
          shared_components=['Independent f4e whole-state/geometry plus13783 dense/98efe IO; existing792004 independent adjacency-set products and canonical wire only, no old main/census relation/global overrides.',
            'Projector/SCI/helper/native sources are hash-bound authenticated data only, never imported or executed. Format constants and prior independently checked Saved4 scope are disclosed prerequisites.'],
          limitations=['One graph-only saved final BEST conversion, no old census selection approval or new native state/RNG/counters/trajectory.',
            'Full checks the whole source state and all9801 integer CN entries; prerequisite saved-artifact/trajectory scope is not broadened or re-executed.',
            'Synthetic selected-field fragments and opaque history controls are explicitly not whole native state fixtures; own complete state positives are separate.',
            'Retained construction triples are not asserted to exhaust graph triangles. No target resolution/general performance/global optimum or denominator.',
            'Budget predicate controls are synthetic one-snapshot tests; source inspection and actual contained receipt remain separate. No blocking-I/O or hard-real-time containment guarantee.'],deadline=deadline.status())
        tick();save('summary.json',result);tick()
    except BaseException as error:
        save('failure.json',dict(error=repr(error),inputs_sha256=pins,protected_before=before,deadline=deadline.status(),
          outputs_preserved=True,automatic_retry=False,native_calls=0,target_resolution='NONE'));raise

if __name__=='__main__':main()

