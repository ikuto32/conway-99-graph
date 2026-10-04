"""Independent graph-only input calibration and exact projection audit.

Imports independent checking code only. No producer helper/parser is imported,
no native process is launched, and no state/RNG/history is created.
"""
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys

from command_deadline import CommandDeadline
import audit_20261003_ternary_mixed_core_v1 as core

ROOT = Path(__file__).resolve().parents[1]
SELF = 'acceleration/audit_20261003_ternary_mixed_graph_input_v1.py'
SPEC = SELF.replace('.py', '_spec.md')
SCI = 'acceleration/prepare_20261003_ternary_mixed_science_v2.py'
CORE = 'acceleration/audit_20261003_ternary_mixed_core_v1.py'
CENSUS_CODE = 'acceleration/audit_20261003_ternary_two_line_target_v1.py'
CENSUS_SHA = 'a902d41d33b5672d6d1f1a0e3876c6a6e53c0c318ab70978e78c679b472ac2e0'
CENSUS_SPEC_SHA = '992ac802a15ab93e7c6b031bac338bda95e32ad24a562f8f5bb9c48d342f5ff4'
CAP = 32 * 1024 * 1024
need, same = core.need, core.io.same
PINS = {
 SCI: '6e29380cc08766264f4697e175f387443e658010af0fbeb2b49911b1349a7b19',
 SCI.replace('.py', '_spec.md'): '491cee55730ca34f1c1c304f7f6128f37d2164bd9a49a3f9deb48f8168b7c3fb',
 CORE: 'f4e55cc885fbad31d8e80a8053a7ab56b2114e6f91b9a137fee101e79ae98a85',
 'acceleration/audit_20261003_ternary_two_line_raw_core_v1.py': '13783be56e50db81c4b474741129a2f6ae4e05dc25960d1551cbf70892d4292f',
 'acceleration/audit_20261003_restricted_three_line_raw_core_v1.py': '98efe2641fe2952857efaa62b7812b0abe7a0f87ce4550bf64544a4ba3ebaa95',
 'acceleration/hypergraph_ternary_mixed_anneal_20261003_v1.cpp': 'eba379d3993e644084e62eba2153ca4870ff1e93cb64fd4212a383fe60c08b31',
 'acceleration/hypergraph_ternary_mixed_anneal_20261003_v1_spec.md': 'c03145e2aeee3726441a26581898b4a3a7f99998f0d6c4ed12ae6407471f869c',
 'acceleration/results/20261003_hypergraph_ternary_mixed_build01/hypergraph_ternary_mixed': '56e0ecf4295f72a51c58a6957da2d4e32787a2514e38866e41172eb79738cf09',
 'acceleration/command_deadline.py': '9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9',
 'acceleration/run_compute_command.py': '593a9feed6250739dc9672338df23ab171fc9a6a6db4196c1feb312efa33957a',
 'pyproject.toml': '273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339',
 'uv.lock': 'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',
}


def identity(x):
    return type(x) is str and core.re.fullmatch('[0-9a-f]{64}', x) is not None


def name_ok(x):
    return (type(x) is str and '\\' not in x and not x.startswith(('/', '.git/', 'external_'))
            and x != 'CLAIMS.yaml' and '..' not in Path(x).parts)


def scalar(n, d, rows):
    """Separate Python adjacency sets; all n^2 products, including diagonal."""
    adj = [set() for _ in range(n)]
    for row in rows:
        for u, v in core.combinations(row, 2):
            adj[u].add(v); adj[v].add(u)
    cn = [[len(adj[u] & adj[v]) for v in range(n)] for u in range(n)]
    hist = [0, 0, 0]; el = em = 0
    for u, v in core.combinations(range(n), 2):
        r = cn[u][v] + int(v in adj[u]) - 2
        hist[r % 3] += 1
        if v in adj[u]:
            el += r*r
        else:
            em += r*r
    f = hist[1] + hist[2]; w = core.weight(n, d)
    return dict(F3=f, E_lambda=el, E_mu=em, E=el+em, scalar_weight=w,
                scalar=w*f+el+em, residue_population=hist), cn


def graph(n, d, rows):
    need(type(rows) is list and all(type(row) is list for row in rows), 'GRAPH_ROWS_TYPE')
    a, metrics, cn = core.geometry(n, d, rows)
    other, products = scalar(n, d, rows)
    need(same(metrics, other) and same(cn.tolist(), products), 'WHOLE_SCALAR_PRODUCT')
    return core.io.matrix_bytes(a), metrics


def canonical_wire(n, d, rows, source):
    need(identity(source), 'GRAPH_SOURCE_IDENTITY')
    return ('TERNARY_LINEAR_GRAPH_INPUT_V1\nn '+str(n)+'\ndegree '+str(d)
            +'\nsource_graph_sha256 '+source+'\ntriples '+str(len(rows))+'\n'
            +''.join(' '.join(map(str, row))+'\n' for row in rows)+'END\n').encode('ascii')


def check_wire(raw, matrix, n, d, rows):
    source = hashlib.sha256(matrix).hexdigest()
    got_n, got_d, got_rows = core.parse_graph(raw, source)
    need(same([got_n, got_d, got_rows], [n, d, rows]), 'WIRE_ORDERED_ROWS')
    need(raw == canonical_wire(n, d, rows, source), 'CANONICAL_WIRE_BYTES')
    rebuilt, metrics = graph(n, d, rows)
    need(matrix == rebuilt, 'MATRIX_LITERAL')
    return metrics


def source_relation(checked, payload, matrix, matrix_name, triples_name, triples_sha):
    expected = dict(status='INDEPENDENT_TERNARY_ALL_LINE_CENSUS_V1_COMPLETE_PASS',
        producer='/root/native_driver', verifier='/root/structural',
        method='independent_artifact_check', target_resolution='NONE')
    need(type(checked) is dict and same({k:checked.get(k) for k in expected}, expected), 'CENSUS_HEADER')
    for key, value in dict(complete_labelled_proposals=239085, complete_raw_record_fields=24,
                           complete_parts=48, complete_checkpoints=48).items():
        need(type(checked.get(key)) is int and checked[key] == value, 'CENSUS_SCOPE:'+key)
    closure = checked.get('inputs_sha256')
    need(type(closure) is dict and closure and all(name_ok(k) and identity(v) for k,v in closure.items()), 'CENSUS_CLOSURE')
    need(closure.get(CENSUS_CODE)==CENSUS_SHA and closure.get(CENSUS_CODE.replace('.py','_spec.md'))==CENSUS_SPEC_SHA,'CENSUS_SOURCE')
    need(closure.get(matrix_name) == hashlib.sha256(matrix).hexdigest()
         and closure.get(triples_name)==triples_sha, 'CENSUS_SELECTED_PINS')
    need(type(payload) is dict and same([payload.get('n'), payload.get('point_degree')], [99,7]), 'TARGET_INPUT_DOMAIN')
    need(type(payload.get('proposal_id')) is int and 0 <= payload['proposal_id'] < 239085, 'SELECTED_ID')
    selected = checked.get('selected_neighbor')
    need(type(selected) is dict and type(selected.get('proposal_id')) is int
         and selected['proposal_id'] == payload['proposal_id'], 'CENSUS_SELECTED_ID')
    aggregate = checked.get('aggregate')
    need(type(aggregate) is dict, 'CENSUS_AGGREGATE')
    ids = aggregate.get('minimum_pair_proposal_ids')
    need(type(ids) is list and ids and all(type(x) is int and 0<=x<239085 for x in ids)
         and ids == sorted(set(ids)), 'MINIMUM_IDS')
    need(selected['proposal_id'] == min(ids), 'MINIMUM_SELECTED')
    raw, metrics = graph(99,7,payload.get('ordered_triples'))
    need(raw == matrix, 'MATRIX_LITERAL')
    need(same(selected.get('metrics'), metrics), 'CENSUS_METRICS')
    need(same(aggregate.get('minimum_pair'), [metrics['F3'],metrics['E']]), 'CENSUS_MINIMUM_PAIR')
    return metrics, payload['ordered_triples'], selected['proposal_id']


def projection_relation(projection, wire, matrix, payload, metrics, pid, matrix_name, triples_name, triples_sha):
    rows = payload['ordered_triples']; source = hashlib.sha256(matrix).hexdigest()
    expected = dict(schema='TERNARY_MIXED_GRAPH_ONLY_PROJECTION_V1', ordered_triples=rows,
        n=99, point_degree=7, source_matrix=matrix_name, source_matrix_sha256=source,
        source_triples=triples_name, source_triples_sha256=triples_sha,
        selected_proposal_id=pid, metrics=metrics, graph_input_sha256=hashlib.sha256(wire).hexdigest(),
        historical_native_state_written=False, rng_or_trajectory_imported=False, independent_approval=False)
    need(same(projection, expected), 'PROJECTION_LITERAL')
    need(same(check_wire(wire,matrix,99,7,rows),metrics), 'PROJECTION_METRICS')


def outer(runtime, terminal, plan):
    command = plan.get('command')
    need(type(command) is list and '--' in command and all(type(x) is str for x in command), 'OUTER_PLAN')
    allocation = plan.get('allocations')
    need(type(allocation) is dict and type(allocation.get('outer_seconds')) is int
         and allocation['outer_seconds'] > 0, 'OUTER_ALLOCATION')
    need(same(runtime.get('command'), command[command.index('--')+1:])
         and type(runtime.get('seconds')) is float and runtime['seconds']==allocation['outer_seconds']
         and runtime.get('source_sha256')==PINS['acceleration/run_compute_command.py']
         and runtime.get('automatic_retry') is False and runtime.get('cumulative_across_commands') is False,
         'OUTER_COMMAND')
    need(type(terminal.get('command_exit_code')) is int and terminal['command_exit_code']==0
         and terminal.get('invocation_id')==runtime.get('invocation_id') and terminal.get('error') is None
         and terminal.get('cleanup',{}).get('reaped') is True
         and terminal['cleanup'].get('job_active_zero_observed') is True
         and terminal['cleanup'].get('cleanup_errors')==[]
         and terminal['cleanup'].get('process_group_live_pids')==[], 'OUTER_CLEANUP')


def producer_header(summary,metrics):
    need(summary.get('status')=='CANDIDATE_GRAPH_ONLY_WIRE_PENDING_INDEPENDENT_CHECK'
         and same(summary.get('metrics'),metrics) and summary.get('independent_approval') is False
         and summary.get('target_resolution')=='NONE' and type(summary.get('automatic_retries')) is int
         and summary['automatic_retries']==0,'PRODUCER_SUMMARY')
    need(type(summary.get('inputs_sha256')) is dict
         and summary['inputs_sha256'].get(SCI)==PINS[SCI]
         and summary['inputs_sha256'].get(SCI.replace('.py','_spec.md'))==PINS[SCI.replace('.py','_spec.md')],'PRODUCER_SOURCE')


def artifact_population(raw,actual,prefix,summary_name):
    wanted={prefix+'/'+x for x in ('invocation.json','graph_input.txt','projection.json')}
    need(type(raw) is dict and set(raw)==wanted,'PROJECTION_ARTIFACT_POPULATION')
    need(set(actual)==wanted|{summary_name},'PROJECTION_DIRECTORY_POPULATION')
    for entry in raw.values():
        need(type(entry) is dict and set(entry)=={'sha256','bytes'} and identity(entry['sha256'])
             and type(entry['bytes']) is int and 0<=entry['bytes']<=CAP,'ARTIFACT_DESCRIPTOR')


def invocation_frame(summary,invocation,runtime,runtime_sha):
    need(same(summary.get('command'),invocation.get('command')) and invocation.get('historical_native_state_written') is False
         and type(invocation.get('observed_euid')) is int and invocation['observed_euid']==1000
         and invocation.get('independent_approval') is False
         and invocation.get('supervisor_manifest_sha256')==runtime_sha,'PROJECT_INVOCATION')
    command=summary.get('command')
    need(type(command) is list and len(command)>2 and all(type(x) is str for x in command)
         and command[1:]==runtime['command'][-(len(command)-1):]
         and command[1].replace('\\','/').endswith(SCI) and command[2]=='project','PROJECT_COMMAND')


def calibration(tick):
    positives=[]; negatives=[]
    def reject(label, stage, callback):
        tick()
        try:
            callback()
        except core.io.AuditError as error:
            need(error.stage==stage,'WRONG_CONTROL_STAGE:'+label)
            negatives.append(dict(case=label,expected_stage=stage,actual_stage=error.stage))
        else:
            raise core.io.AuditError('ACCEPTED_CORRUPTION:'+label)
    rook=[[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8]]
    cube=[[0,1,2],[0,3,4],[1,5,6],[3,5,7],[2,8,9],[4,8,10],[6,9,11],[7,10,11]]
    target=[[x,x+33,x+66] for x in range(33)]
    target += [[x,(x+1)%99,(x+4)%99] for x in range(99)]
    target += [[x,(x+7)%99,(x+18)%99] for x in range(99)]
    for label,n,d,rows,w in [('rook9',9,2,rook,577),('cube12',12,2,cube,1057),('cyclic99_fixture',99,7,target,819820)]:
        tick(); raw,m=graph(n,d,rows); wire=canonical_wire(n,d,rows,hashlib.sha256(raw).hexdigest())
        need(same(check_wire(wire,raw,n,d,rows),m) and m['scalar_weight']==w,'OWN_FIXTURE')
        positives.append(dict(case=label,matrix_products=n*n,pair_scores=n*(n-1)//2,metrics=m,wire_literal=True))
    raw,m=graph(99,7,target); matrix_name='build/synthetic.adj'; triples_name='build/synthetic.triples.json'
    payload=dict(n=99,point_degree=7,ordered_triples=target,proposal_id=42)
    triples_sha='1'*64
    checked=dict(status='INDEPENDENT_TERNARY_ALL_LINE_CENSUS_V1_COMPLETE_PASS',producer='/root/native_driver',
        verifier='/root/structural',method='independent_artifact_check',target_resolution='NONE',
        complete_labelled_proposals=239085,complete_raw_record_fields=24,complete_parts=48,complete_checkpoints=48,
        inputs_sha256={matrix_name:hashlib.sha256(raw).hexdigest(),triples_name:triples_sha,
                      CENSUS_CODE:CENSUS_SHA,CENSUS_CODE.replace('.py','_spec.md'):CENSUS_SPEC_SHA},
        selected_neighbor=dict(proposal_id=42,metrics=m),aggregate=dict(minimum_pair_proposal_ids=[42,50],minimum_pair=[m['F3'],m['E']]))
    relation=lambda c=checked,p=payload,a=raw: source_relation(c,p,a,matrix_name,triples_name,triples_sha)
    need(same(relation(),(m,target,42)), 'OWN_SOURCE_RELATION')
    wire=canonical_wire(99,7,target,hashlib.sha256(raw).hexdigest())
    projection=dict(schema='TERNARY_MIXED_GRAPH_ONLY_PROJECTION_V1',ordered_triples=target,n=99,point_degree=7,
        source_matrix=matrix_name,source_matrix_sha256=hashlib.sha256(raw).hexdigest(),source_triples=triples_name,
        source_triples_sha256=triples_sha,selected_proposal_id=42,metrics=m,graph_input_sha256=hashlib.sha256(wire).hexdigest(),
        historical_native_state_written=False,rng_or_trajectory_imported=False,independent_approval=False)
    projection_relation(projection,wire,raw,payload,m,42,matrix_name,triples_name,triples_sha)
    positives.append(dict(case='synthetic_complete_source_and_projection',real_census_read=False,actual_saved_target_read=False))
    for key,value in [('n',True),('n',99.0),('point_degree',True),('point_degree',7.0)]:
        q=copy.deepcopy(payload);q[key]=value
        reject('typed_'+key+'_'+str(value),'TARGET_INPUT_DOMAIN',lambda q=q:relation(p=q))
    for label,value in [('negative',-1),('range',99),('bool',True),('float',0.0)]:
        rows=copy.deepcopy(rook);rows[0][0]=value
        reject('point_'+label,'DOMAIN_ROW_TYPES' if label in ('bool','float') else 'DOMAIN_POINT_RANGE',lambda rows=rows:graph(9,2,rows))
    for label,rows,stage in [('tuple_rows',tuple(rook),'GRAPH_ROWS_TYPE'),('short_rows',rook[:-1],'DOMAIN_POPULATION'),
        ('repeated_point',[[0,0,2]]+rook[1:],'DOMAIN_ROW_DISTINCT'),('duplicate_row',[rook[0]]*2+rook[2:],'DOMAIN_POINT_DEGREE')]:
        reject(label,stage,lambda rows=rows:graph(9,2,rows))
    for key,value in [('status','OTHER'),('producer','/root'),('verifier','/root/checkpoint_audit'),
                      ('method','independent_derivation'),('target_resolution','SOLVED')]:
        q=copy.deepcopy(checked);q[key]=value
        reject('header_'+key,'CENSUS_HEADER',lambda q=q:relation(c=q))
    for key in ('complete_labelled_proposals','complete_raw_record_fields','complete_parts','complete_checkpoints'):
        for label,value in [('wrong',0),('float',float(checked[key])),('bool',True)]:
            q=copy.deepcopy(checked);q[key]=value
            reject(key+'_'+label,'CENSUS_SCOPE:'+key,lambda q=q:relation(c=q))
    for label,closure in [('empty',{}),('mutable',{'CLAIMS.yaml':'2'*64}),('upper',{matrix_name:'A'*64}),('parent',{'../x':'2'*64})]:
        q=copy.deepcopy(checked);q['inputs_sha256']=closure
        reject('closure_'+label,'CENSUS_CLOSURE',lambda q=q:relation(c=q))
    for label,key in [('code',CENSUS_CODE),('spec',CENSUS_CODE.replace('.py','_spec.md'))]:
        q=copy.deepcopy(checked);q['inputs_sha256'][key]='2'*64
        reject('census_'+label,'CENSUS_SOURCE',lambda q=q:relation(c=q))
    q=copy.deepcopy(checked);q['inputs_sha256'][matrix_name]='2'*64
    reject('matrix_pin','CENSUS_SELECTED_PINS',lambda:relation(c=q))
    q=copy.deepcopy(checked);q['inputs_sha256'][triples_name]='2'*64
    reject('triples_pin','CENSUS_SELECTED_PINS',lambda:relation(c=q))
    for label,value in [('bool',True),('float',42.0),('range',239085)]:
        q=copy.deepcopy(payload);q['proposal_id']=value
        reject('pid_'+label,'SELECTED_ID',lambda q=q:relation(p=q))
    q=copy.deepcopy(checked);q['selected_neighbor']['proposal_id']=True
    reject('selected_bool','CENSUS_SELECTED_ID',lambda:relation(c=q))
    for label,ids in [('empty',[]),('bool',[True]),('float',[42.0]),('duplicate',[42,42]),('unsorted',[50,42]),('range',[239085])]:
        q=copy.deepcopy(checked);q['aggregate']['minimum_pair_proposal_ids']=ids
        reject('min_ids_'+label,'MINIMUM_IDS',lambda q=q:relation(c=q))
    q=copy.deepcopy(checked);q['aggregate']['minimum_pair_proposal_ids']=[1,42]
    reject('nonminimum','MINIMUM_SELECTED',lambda:relation(c=q))
    for key,value in [('F3',float(m['F3'])),('E_lambda',True),('scalar_weight',950797),('residue_population',[0,0,0])]:
        q=copy.deepcopy(checked);q['selected_neighbor']['metrics'][key]=value
        reject('metric_'+key,'CENSUS_METRICS',lambda q=q:relation(c=q))
    q=copy.deepcopy(checked);q['aggregate']['minimum_pair']=[float(m['F3']),m['E']]
    reject('min_pair_float','CENSUS_MINIMUM_PAIR',lambda:relation(c=q))
    changed=raw.replace(b'0',b'1',1)
    q=copy.deepcopy(checked);q['inputs_sha256'][matrix_name]=hashlib.sha256(changed).hexdigest()
    reject('consistent_corrupt_matrix','MATRIX_LITERAL',lambda:relation(c=q,a=changed))
    for label,bad,stage in [('source',wire.replace(hashlib.sha256(raw).hexdigest().encode(),b'0'*64),'GRAPH_SOURCE_IDENTITY'),
        ('float',wire.replace(b'n 99',b'n 99.0'),'WIRE_INTEGER'),('trailing',wire+b'junk\n','WIRE_TRAILING'),
        ('newline',wire.replace(b'\n',b'\r\n'),'CANONICAL_WIRE_BYTES'),
        ('ordered',wire.replace(b'triples 231\n0 33 66',b'triples 231\n33 0 66'),'WIRE_ORDERED_ROWS')]:
        reject('wire_'+label,stage,lambda bad=bad:check_wire(bad,raw,99,7,target))
    for key,value in [('n',99.0),('historical_native_state_written',True),('rng_or_trajectory_imported',True),
                      ('source_matrix_sha256','3'*64),('graph_input_sha256','3'*64)]:
        q=copy.deepcopy(projection);q[key]=value
        reject('projection_'+key,'PROJECTION_LITERAL',lambda q=q:projection_relation(q,wire,raw,payload,m,42,matrix_name,triples_name,triples_sha))
    plan=dict(command=['python','supervisor','--','uv','python',SCI,'project'],allocations=dict(outer_seconds=120))
    runtime=dict(command=plan['command'][3:],seconds=120.,source_sha256=PINS['acceleration/run_compute_command.py'],
        automatic_retry=False,cumulative_across_commands=False,invocation_id='synthetic')
    terminal=dict(command_exit_code=0,invocation_id='synthetic',error=None,
        cleanup=dict(reaped=True,job_active_zero_observed=True,cleanup_errors=[],process_group_live_pids=[]))
    outer(runtime,terminal,plan);positives.append(dict(case='synthetic_supported_receipt',native_calls=0))
    for key,value in [('seconds',120),('command',['wrong']),('automatic_retry',True),('source_sha256','0'*64)]:
        q=copy.deepcopy(runtime);q[key]=value
        reject('runtime_'+key,'OUTER_COMMAND',lambda q=q:outer(q,terminal,plan))
    for key,value in [('reaped',False),('job_active_zero_observed',False),('process_group_live_pids',[123]),('cleanup_errors',['x'])]:
        q=copy.deepcopy(terminal);q['cleanup'][key]=value
        reject('cleanup_'+key,'OUTER_CLEANUP',lambda q=q:outer(runtime,q,plan))
    summary=dict(status='CANDIDATE_GRAPH_ONLY_WIRE_PENDING_INDEPENDENT_CHECK',metrics=m,independent_approval=False,
                 target_resolution='NONE',automatic_retries=0,inputs_sha256={SCI:PINS[SCI],SCI.replace('.py','_spec.md'):PINS[SCI.replace('.py','_spec.md')]},
                 command=['python',SCI,'project'])
    invocation=dict(command=summary['command'],historical_native_state_written=False,observed_euid=1000,
                    independent_approval=False,supervisor_manifest_sha256='4'*64)
    descriptors={'build/p/'+x:dict(sha256='4'*64,bytes=12) for x in ('invocation.json','graph_input.txt','projection.json')}
    producer_header(summary,m);artifact_population(descriptors,list(descriptors)+['build/p/summary.json'],'build/p','build/p/summary.json')
    invocation_frame(summary,invocation,runtime,'4'*64)
    positives.append(dict(case='synthetic_producer_files_command_and_invocation',actual_producer_output_read=False))
    for key,value in [('status','OTHER'),('metrics',dict(m,F3=float(m['F3']))),('automatic_retries',False),('independent_approval',True)]:
        q=copy.deepcopy(summary);q[key]=value
        reject('producer_'+key,'PRODUCER_SUMMARY',lambda q=q:producer_header(q,m))
    q=copy.deepcopy(summary);q['inputs_sha256'][SCI]='4'*64
    reject('producer_source','PRODUCER_SOURCE',lambda:producer_header(q,m))
    q=copy.deepcopy(descriptors);del q['build/p/invocation.json']
    reject('omitted_invocation','PROJECTION_ARTIFACT_POPULATION',lambda:artifact_population(q,list(descriptors)+['build/p/summary.json'],'build/p','build/p/summary.json'))
    reject('extra_raw','PROJECTION_DIRECTORY_POPULATION',lambda:artifact_population(descriptors,list(descriptors)+['build/p/summary.json','build/p/extra'],'build/p','build/p/summary.json'))
    q=copy.deepcopy(descriptors);q['build/p/graph_input.txt']['bytes']=True
    reject('bytes_boolean','ARTIFACT_DESCRIPTOR',lambda:artifact_population(q,list(descriptors)+['build/p/summary.json'],'build/p','build/p/summary.json'))
    for key,value in [('historical_native_state_written',True),('observed_euid',1000.0),('supervisor_manifest_sha256','5'*64)]:
        q=copy.deepcopy(invocation);q[key]=value
        reject('invocation_'+key,'PROJECT_INVOCATION',lambda q=q:invocation_frame(summary,q,runtime,'4'*64))
    q=copy.deepcopy(summary);q['command']=['python',SCI,'run']
    inv=copy.deepcopy(invocation);inv['command']=q['command']
    rt=copy.deepcopy(runtime);rt['command']=['uv','python',SCI,'run']
    reject('wrong_mode','PROJECT_COMMAND',lambda:invocation_frame(q,inv,rt,'4'*64))
    for label,raw_json in [('duplicate',b'{"x":1,"x":2}'),('nonfinite',b'{"x":NaN}')]:
        reject('json_'+label,'JSON',lambda raw_json=raw_json:core.io.strict_json(raw_json))
    reject('wrong_stage_harness','WRONG_CONTROL_STAGE:wrong_stage_inner',
           lambda:reject('wrong_stage_inner','WIRE_INTEGER',lambda:need(False,'JSON')))
    need((len(positives),len(negatives))==(6,87),'DECLARED_CONTROL_POPULATION')
    return positives,negatives


def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['calibration','full'])
    p.add_argument('--seconds',type=float,required=True);p.add_argument('--out',type=Path,required=True)
    for k in ('self','spec'):p.add_argument('--'+k+'-sha256',required=True)
    p.add_argument('--expected-head',required=True);p.add_argument('--protected-ledger-sha256',required=True)
    p.add_argument('--protected-index-sha256',required=True)
    for k in ('calibration','census-gate','matrix','triples','producer-summary','producer-plan','runtime-manifest','runtime-summary'):
        p.add_argument('--'+k);p.add_argument('--'+k+'-sha256')
    args=p.parse_args(); deadline=CommandDeadline(args.seconds,allocation_reason='Exact mixed graph-only input; inclusive hashes/own controls/full scalar,20save; no native or search')
    out=args.out.resolve();need(out.is_relative_to(ROOT) and not out.exists(),'FRESH_OUTPUT');out.mkdir(parents=True)
    pins={};before={}
    def tick():need(not deadline.status()['stop_required'] and deadline.status()['remaining_seconds']>20,'SAVE_RESERVE')
    def pin(name,sha,size=None):
        tick();need(name_ok(name) and identity(sha),'BOUND_IDENTITY')
        file=(ROOT/name).resolve();need(file.is_relative_to(ROOT) and file.is_file() and file.stat().st_size<=CAP,'BOUND_FILE')
        h=hashlib.sha256();total=0
        with file.open('rb') as f:
            while chunk:=f.read(1024*1024):tick();h.update(chunk);total+=len(chunk)
        need(h.hexdigest()==sha and (size is None or type(size) is int and total==size),'INPUT_IDENTITY:'+name)
        need(name not in pins or pins[name]==sha,'INPUT_CONFLICT');pins[name]=sha
        return file
    def read(name):return core.io.strict_json((ROOT/name).read_bytes())
    def save(name,value):(out/name).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf8')
    def protect():
        x=dict(head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            ledger_sha256=hashlib.sha256((ROOT/'CLAIMS.yaml').read_bytes()).hexdigest(),index_sha256=hashlib.sha256((ROOT/'.git/index').read_bytes()).hexdigest())
        need(same(list(x.values()),[args.expected_head,args.protected_ledger_sha256,args.protected_index_sha256]),'PROTECTED_CONTEXT');return x
    try:
        before=protect()
        for name,sha in {**PINS,SELF:args.self_sha256,SPEC:args.spec_sha256}.items():pin(name,sha)
        pos,neg=calibration(tick);save('controls.json',dict(positive=pos,strict_negative=neg))
        controls=(out/'controls.json').relative_to(ROOT).as_posix();pin(controls,hashlib.sha256((out/'controls.json').read_bytes()).hexdigest())
        report=dict(status='INDEPENDENT_TERNARY_MIXED_GRAPH_ONLY_INPUT_V1_CALIBRATION_PASS',producer='/root/native_driver',
            verifier='/root/checkpoint_audit',method='independent_artifact_check',target_resolution='NONE',mode=args.mode,
            timestamp=datetime.now(timezone.utc).isoformat(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),
            numpy=core.dense.np.__version__,source_sha256=args.self_sha256,spec_sha256=args.spec_sha256,
            positive_controls=len(pos),strict_negative_controls=len(neg),controls=dict(path=controls,sha256=pins[controls]),
            native_calls=0,actual_saved_target_read=False,mathematical_replay_of_census=False)
        if args.mode=='full':
            objects={}
            for k in ('calibration','census_gate','matrix','triples','producer_summary','producer_plan','runtime_manifest','runtime_summary'):
                name=getattr(args,k);sha=getattr(args,k+'_sha256');need(name is not None and sha is not None,'EXPLICIT_FULL_IDENTITIES')
                pin(name,sha);objects[k]=read(name) if k!='matrix' else (ROOT/name).read_bytes()
            cal=objects['calibration'];need(cal.get('status')=='INDEPENDENT_TERNARY_MIXED_GRAPH_ONLY_INPUT_V1_CALIBRATION_PASS'
                and cal.get('source_sha256')==args.self_sha256 and cal.get('spec_sha256')==args.spec_sha256,'APPLICABLE_CALIBRATION')
            for owner in ('calibration','census_gate','producer_summary','producer_plan'):
                for name,sha in objects[owner]['inputs_sha256'].items():pin(name,sha)
            checked,payload,matrix=objects['census_gate'],objects['triples'],objects['matrix']
            need(checked['inputs_sha256'].get(args.triples)==args.triples_sha256,'CENSUS_SELECTED_PINS')
            metrics,rows,pid=source_relation(checked,payload,matrix,args.matrix,args.triples,args.triples_sha256)
            summary=objects['producer_summary'];producer_header(summary,metrics)
            prefix=Path(args.producer_summary).parent.as_posix();raw=summary.get('raw_artifacts')
            wanted={prefix+'/'+x for x in ('invocation.json','graph_input.txt','projection.json')}
            actual={x.relative_to(ROOT).as_posix() for x in (ROOT/prefix).rglob('*') if x.is_file()}
            artifact_population(raw,actual,prefix,args.producer_summary)
            for name,entry in raw.items():
                pin(name,entry['sha256'],entry['bytes'])
            wire_name=prefix+'/graph_input.txt';projection=read(prefix+'/projection.json')
            projection_relation(projection,(ROOT/wire_name).read_bytes(),matrix,payload,metrics,pid,args.matrix,args.triples,args.triples_sha256)
            outer(objects['runtime_manifest'],objects['runtime_summary'],objects['producer_plan'])
            invocation=read(prefix+'/invocation.json')
            invocation_frame(summary,invocation,objects['runtime_manifest'],args.runtime_manifest_sha256)
            report.update(status='INDEPENDENT_TERNARY_MIXED_GRAPH_ONLY_INPUT_V1_COMPLETE_PASS',actual_saved_target_read=True,
                n=99,point_degree=7,ordered_triples=231,source_graph_sha256=args.matrix_sha256,
                source_triples_sha256=args.triples_sha256,source_complete_census_sha256=args.census_gate_sha256,
                graph_input_path=wire_name,graph_input_sha256=pins[wire_name],selected_proposal_id=pid,metrics=metrics,
                complete_integer_matrix_products=9801,historical_native_state_written=False,rng_or_trajectory_imported=False)
            if metrics['F3']==0 and metrics['E']==0:
                save('target_candidate_pending_root.json',dict(matrix=args.matrix,sha256=args.matrix_sha256,metrics=metrics))
                raise core.io.AuditError('FULL99_IDENTITY_ZERO_PENDING_ROOT')
        report.update(inputs_sha256=pins,historical_protected_execution_state=dict(before=before,after=protect(),
            role='Historical execution observations outside immutable dependency map'),deadline=deadline.status(),
            shared_components=['Independent mixed f4e wire/domain plus dense13783 and strict IO98efe; whole Python adjacency-set products repeated independently.',
                               'Native SCI V2/C++ are authenticated source data only, never imported or executed.'],
            limitations=['A graph-only conversion of one separately checked finite census selection; no imported native state/RNG/counters/history.',
                         'Prior census completeness is an explicit independently authenticated dependency, not replayed here.',
                         'Calibration synthetic complete-census frame is not an executed census or graph-space coverage. No target resolution.'])
        save('summary.json',report)
    except BaseException as error:
        save('failure.json',dict(error=repr(error),inputs_sha256=pins,protected_before=before,deadline=deadline.status(),
                                outputs_preserved=True,automatic_retry=False,native_calls=0,target_resolution='NONE'));raise


if __name__=='__main__':main()
