"""Source-only independent finite mixed-engine controls checker.

Calibrate solely on own fixtures before full producer-output inspection.
Full mode launches no native code and replays only the declared finite batch.
"""
import argparse
from collections import Counter
import copy
from datetime import datetime, timezone
import hashlib
from itertools import combinations
import json
import math
from pathlib import Path
import platform
import subprocess
import sys

from tqdm import tqdm
from command_deadline import CommandDeadline
import audit_20261003_ternary_mixed_core_v1 as core

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'acceleration/audit_20261003_ternary_mixed_engine_v2.py'
CORE = 'acceleration/audit_20261003_ternary_mixed_core_v1.py'
SPEC = SOURCE.replace('.py', '_spec.md')
CPP = 'acceleration/hypergraph_ternary_mixed_anneal_20261003_v1.cpp'
WRAPPER = 'acceleration/prepare_20261003_hypergraph_ternary_mixed_v1.py'
BINARY = 'acceleration/results/20261003_hypergraph_ternary_mixed_build01/hypergraph_ternary_mixed'
BUILD = 'acceleration/results/20261003_hypergraph_ternary_mixed_build01/build_manifest.json'
FINITE_FILE_CAP = 32*1024*1024
PINS = {
 CPP: 'eba379d3993e644084e62eba2153ca4870ff1e93cb64fd4212a383fe60c08b31',
 CPP.replace('.cpp', '_spec.md'): 'c03145e2aeee3726441a26581898b4a3a7f99998f0d6c4ed12ae6407471f869c',
 WRAPPER: '98119f80e795c2a826298eed159c50895de26597371cb653a864d704cc72bffa',
 WRAPPER.replace('.py', '_spec.md'): '80432c52635998c90d0c5781b645dd8ef0bcd056113ee8dbbc93c8bcffd6e13e',
 'acceleration/audit_20261003_ternary_two_line_raw_core_v1.py': '13783be56e50db81c4b474741129a2f6ae4e05dc25960d1551cbf70892d4292f',
 'acceleration/audit_20261003_restricted_three_line_raw_core_v1.py': '98efe2641fe2952857efaa62b7812b0abe7a0f87ce4550bf64544a4ba3ebaa95',
 'acceleration/command_deadline.py': '9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9',
 'acceleration/run_compute_command.py': '593a9feed6250739dc9672338df23ab171fc9a6a6db4196c1feb312efa33957a',
 'pyproject.toml': '273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339',
 'uv.lock': 'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',
 BINARY: '56e0ecf4295f72a51c58a6957da2d4e32787a2514e38866e41172eb79738cf09',
 BUILD: 'c1c3df1e9d933718c8b48ad94f2d03759bed17df4c5faaaf8b65651a08b928ea',
}
POSITIVE = ['rook_initial_probes','prism_initial_probes','cube_initial_probes',
 'target_initial','target_forced','target_greedy','target_anneal','target_cooling','target_mixed',
 'rook_forced','prism_forced','cube_forced',
 *[f+s for f in ('target','prism','cube','import') for s in ('_whole','_prefix73','_resumed')],
 'import_rook_reset','import_target_reset','rook_stop_zero']
NEGATIVE = ['magic','objective','kernel','distribution','source','weight','seed','mix','schedule',
 'temperature','forced','counter','rng_zero','rng_negative','rng_overflow','integer_bool',
 'integer_float','metric_overflow','metric_scalar','metric_score','histogram','cache','cache_bool',
 'cache_float','triple_range','triple_duplicate','degree','trailing','truncated','zero_count',
 'zero_missing_current','zero_missing_best','zero_duplicate','zero_rng','zero_counter',
 'zero_triples','zero_initial_rng','zero_initial_words','initial_rng','initial_words','initial_best',
 'import_magic','import_domain','import_hash','import_duplicate','import_trailing','import_integer_bool',
 'arg_duplicate','arg_unknown','arg_missing','arg_conflict','arg_zero_interval','arg_nonfinite',
 'arg_negative','arg_overflow','probe_scope']
DIAGNOSTICS = dict(zip(NEGATIVE, [
 'WIRE_FIELD:HYPERGRAPH_TERNARY_MIXED_STATE_V1','STATE_VERSION','STATE_VERSION','STATE_VERSION',
 'SOURCE_GRAPH_HASH','STATE_SCALAR_WEIGHT','RESUME_CONFIG_MISMATCH','RESUME_CONFIG_MISMATCH',
 'RESUME_CONFIG_MISMATCH','RESUME_CONFIG_MISMATCH','STATE_FORCED','STATE_COUNTERS','RNG_ZERO',
 'WIRE_INTEGER','WIRE_INTEGER_OVERFLOW','WIRE_INTEGER','WIRE_INTEGER','STATE_METRIC_TYPES',
 'STATE_METRIC_TYPES','STATE_SCORES','STATE_SCORES','STATE_CN_CACHE','WIRE_INTEGER','WIRE_INTEGER',
 'WIRE_RANGE','TRIPLE_LINEARITY','DOMAIN_DECLARED','WIRE_TRAILING','WIRE_TRUNCATED',
 'STATE_ZERO_POPULATION','STATE_ZERO_COMPLETENESS','STATE_BEST_ZERO_COMPLETENESS','STATE_ZERO_OBJECT',
 'RNG_ZERO','STATE_COUNTERS','TRIPLE_LINEARITY','STATE_ZERO_INITIAL_RESET','STATE_ZERO_INITIAL_RESET',
 'STATE_INITIAL_RESET','STATE_INITIAL_RESET','STATE_INITIAL_RESET','WIRE_FIELD:TERNARY_LINEAR_GRAPH_INPUT_V1',
 'DOMAIN_DECLARED','GRAPH_SOURCE_IDENTITY','TRIPLE_LINEARITY','WIRE_TRAILING','WIRE_INTEGER',
 'ARG_DUPLICATE','ARG_UNKNOWN','ARG_REQUIRED:--seed','ARG_INPUT_EXCLUSIVE','ARG_LIMITS',
 'WIRE_REAL','WIRE_INTEGER','WIRE_INTEGER_OVERFLOW','PROBE_SCOPE']))
need = core.need
same = core.io.same
raw_json = core.io.strict_json


def path(name):
    need(type(name) is str and '\\' not in name and not name.startswith('/')
         and '..' not in Path(name).parts and not name.startswith(('.git/', 'external_')), 'BOUND_PATH')
    p = (ROOT / name).resolve()
    need(p.is_relative_to(ROOT) and p.is_file(), 'BOUND_PATH')
    return p


def origin_path(name):
    """Only literal mapped workspace absolute paths from recorded Linux calls."""
    prefix = '/mnt/c/Users/ikuto/projects/conway-99-graph/'
    if name.startswith(prefix):
        name = name[len(prefix):]
    return path(name)


def wire_bytes(file):
    need(file.is_file() and file.stat().st_size<=FINITE_FILE_CAP,'FINITE_FILE_SIZE')
    return file.read_bytes()


def options(values):
    required = {'--seed','--steps','--mix-steps','--schedule-steps','--temperature-start','--temperature-end'}
    texts = {'--fixture','--graph-input','--source-graph-sha256','--resume'}
    ints = {'--seed','--steps','--mix-steps','--schedule-steps','--verify-every','--checkpoint-every',
            '--trace-prefix','--trace-stride'}
    reals = {'--temperature-start','--temperature-end','--checkpoint-seconds'}
    flags = {'--forced','--stop-at-zero','--emit-pair-costs','--probe-all'}
    result = {'--verify-every':1,'--checkpoint-every':1,'--checkpoint-seconds':1.,'--forced':False}
    seen = set(); at = 0
    while at < len(values):
        key = values[at]; at += 1
        need(key not in seen, 'ARG_DUPLICATE'); seen.add(key)
        if key in flags:
            result[key] = True; continue
        need(at < len(values), 'ARG_VALUE'); value = values[at]; at += 1
        need(key in texts | ints | reals, 'ARG_UNKNOWN')
        result[key] = core.number(value) if key in ints else core.real(value) if key in reals else value
    for key in sorted(required):
        need(key in seen, 'ARG_REQUIRED:' + key)
    need(sum(key in result for key in ('--fixture','--graph-input','--resume')) == 1, 'ARG_INPUT_EXCLUSIVE')
    imported = '--graph-input' in result or '--resume' in result
    need(imported == ('--source-graph-sha256' in result), 'ARG_GRAPH_SOURCE')
    if imported:
        need(core.re.fullmatch('[0-9a-f]{64}', result['--source-graph-sha256']) is not None, 'ARG_GRAPH_SOURCE')
    config = dict(seed=result['--seed'],mix_steps=result['--mix-steps'],schedule_steps=result['--schedule-steps'],
        t_start=result['--temperature-start'],t_end=result['--temperature-end'],forced=int(result['--forced']))
    core.config_check(config)
    need(result['--steps'] <= 0x0fffffffffffffff and result['--verify-every'] > 0
         and result['--checkpoint-every'] > 0 and result['--checkpoint-seconds'] > 0, 'ARG_LIMITS')
    return result, config


def starting(opts, config):
    if '--resume' in opts:
        return core.parse_state(wire_bytes(origin_path(opts['--resume'])), opts['--source-graph-sha256'], config)
    if '--graph-input' in opts:
        n, d, rows = core.parse_graph(wire_bytes(origin_path(opts['--graph-input'])), opts['--source-graph-sha256'])
        a, metrics, _ = core.geometry(n, d, rows)
        need(hashlib.sha256(core.io.matrix_bytes(a)).hexdigest() == opts['--source-graph-sha256'], 'INPUT_MATRIX_IDENTITY')
        s = core.initial('rook9', **{k:config[k] for k in ('seed',)})
        s.update(config); s.update(n=n,degree=d,current=rows,best=copy.deepcopy(rows),
             current_metrics=metrics,best_metrics=copy.deepcopy(metrics),zeros=[],
             source_graph_sha256=opts['--source-graph-sha256'])
        core.capture(s); return s
    s = core.initial(opts['--fixture'], seed=config['seed'],mix=config['mix_steps'],
                     start=config['t_start'],end=config['t_end'],forced=config['forced'])
    s['schedule_steps'] = config['schedule_steps']
    return s


def scalar_metrics(n, d, rows):
    adj = [set() for _ in range(n)]
    for row in rows:
        for u, v in combinations(row, 2):
            adj[u].add(v); adj[v].add(u)
    el = em = 0; hist = [0,0,0]
    for u, v in combinations(range(n), 2):
        a = int(v in adj[u]); r = len(adj[u] & adj[v]) + a - 2
        hist[r % 3] += 1
        if a:
            el += r*r
        else:
            em += r*r
    w = core.weight(n,d); f = hist[1]+hist[2]
    return dict(F3=f,E_lambda=el,E_mu=em,E=el+em,scalar_weight=w,scalar=w*f+el+em,residue_population=hist)


def manifest_scope(manifest):
    need(type(manifest) is dict and manifest.get('schema')=='TERNARY_MIXED_FINITE_CONTROLS_V1'
         and type(manifest.get('runs')) is list
         and all(type(r) is dict for r in manifest['runs'])
         and [r.get('label') for r in manifest['runs']]==POSITIVE+['reject_'+x for x in NEGATIVE],
         'FULL_83_POPULATION')
    expected=dict(positive_calls=27,strict_negative_calls=56,native_calls=83,
        actual_scientific_input_read=False,scientific_search_launched=False,
        target_resolution=False,independent_approval=False,whole_prefix_resume_equalities=4,
        complete_generic_probe_records=522,attempted_ordinary_proposals=8192)
    need(same({k:manifest.get(k) for k in expected},expected),'FULL_FINITE_SCOPE')


def native_receipt(row,receipt,launch):
    need(same(receipt.get('command'),row['command'])
         and same(receipt.get('actual_exit_code'),row['actual_exit_code'])
         and same(receipt.get('expected_exit_code'),row['expected_exit_code'])
         and receipt.get('reaped') is True and receipt.get('error') is None
         and type(receipt.get('observed_euid')) is int and receipt['observed_euid']==1000
         and type(receipt.get('process_group')) is int and receipt['process_group']>0
         and type(receipt.get('child_pid')) is int and receipt['child_pid']>0,
         'NATIVE_RECEIPT')
    need(same({k:launch.get(k) for k in ('command','label','expected_exit_code','expected_diagnostic')},
         {k:row[k] for k in ('command','label','expected_exit_code','expected_diagnostic')}),'NATIVE_LAUNCH')
    cmd=row['command']
    need(type(cmd) is list and len(cmd)>=14 and all(type(x) is str for x in cmd)
         and cmd[:4]==['/usr/bin/timeout','--foreground','--signal=TERM','--kill-after=5s']
         and cmd[5]=='/usr/bin/prlimit' and cmd[8]=='--core=0:0'
         and cmd[10]=='--out' and cmd[12]=='--seconds' and cmd[14:]==row['options'],
         'NATIVE_CONTAINED_COMMAND')
    need(cmd[4].endswith('s'),'NATIVE_LIMITS')
    guard=core.real(cmd[4][:-1]);cooperative=core.real(cmd[13])
    need(0<cooperative<guard<=10 and guard-cooperative>=4.99
         and cmd[6]=='--as=2147483648:2147483648'
         and cmd[7]=='--fsize=1073741824:1073741824','NATIVE_LIMITS')
    prefix='/mnt/c/Users/ikuto/projects/conway-99-graph/'
    need(cmd[11]==prefix+row['receipt'].removesuffix('.receipt.json')
         and receipt.get('cwd')==prefix[:-1]
         and receipt.get('stdout')==row['receipt'].replace('.receipt.json','.stdout.log')
         and receipt.get('stderr')==row['receipt'].replace('.receipt.json','.stderr.log'),
         'NATIVE_OUTPUT_IDENTITY')
    return guard


def costs(raws):
    reference=core.pair_costs()
    need(len(reference)==596 and len(raws)==596
         and all(same(raw_json(raw),wanted) for raw,wanted in zip(raws,reference)),
         'COMPLETE596_PAIR_COSTS')


def zero_selection(selection,s,start,resumed):
    expected=dict(schema='TERNARY_RETAINED_ZERO_SELECTION_V1',
        selection_rule='First RETAINED current F3zero object, including initial; every distinct retained zero matrix preserved. No unobserved earliest trajectory claim.',
        found=bool(s['zeros']),first_step=s['zeros'][0]['step'] if s['zeros'] else None,
        retained_distinct_objects=len(s['zeros']),
        carried_from_resume=bool(resumed and s['zeros'] and s['zeros'][0]['step']<=start),
        target_resolution=False,independent_approval=False)
    need(same(selection,expected),'ZERO_SELECTION')
    return expected


def zero_population(names,count):
    need(type(count) is int and count>=0,'ZERO_POPULATION_DOMAIN')
    need(set(names)=={f'object_{j}.{suffix}' for j in range(count) for suffix in ('adj','triples')},
         'COMPLETE_ZERO_EXPORT_POPULATION')


def required_states(names,start,end,every,captured):
    need(type(start) is int and type(end) is int and type(every) is int and every>0
         and 0<=start<=end,'STATE_POPULATION_DOMAIN')
    wanted={'initial.state','final.state'} | {f'checkpoint_{step}.state'
        for step in range(start+1,end+1) if step%every==0} | {f'zero_capture_{step}.state' for step in captured}
    need(wanted<=set(names),'SAVED_STATE_POPULATION')
    need(all(x in ('initial.state','final.state') or core.re.fullmatch(r'(?:checkpoint|zero_capture)_[0-9]+\.state',x)
         for x in names),'SAVED_STATE_FILENAME')


def artifact_population(listed,actual):
    need(set(listed)==set(actual),'EXACT_CASE_ARTIFACT_POPULATION')


def branch_population(checked,recorded):
    need(all(checked.values()) and same(checked,recorded),'ACTUAL_BRANCH_POPULATION')


def check_probes(records,s,tick=lambda:None):
    pid=0
    for i,j in combinations(range(len(s['current'])),2):
        for ix in range(3):
            for jy in range(3):
                tick();need(pid<len(records),'PROBE_POPULATION')
                need(same(raw_json(records[pid]),core.probe(s,pid,i,j,ix,jy)),'PROBE_RECORD')
                pid+=1
    need(pid==len(records),'PROBE_POPULATION')
    return pid


def outer_receipt(runtime,terminal,plan):
    need(type(terminal.get('command_exit_code')) is int and terminal['command_exit_code']==0
         and terminal.get('invocation_id')==runtime.get('invocation_id') and terminal.get('error') is None
         and terminal.get('cleanup',{}).get('reaped') is True
         and terminal['cleanup'].get('job_active_zero_observed') is True
         and terminal['cleanup'].get('cleanup_errors')==[]
         and terminal['cleanup'].get('process_group_live_pids')==[], 'ACTUAL_LINUX_CLEANUP')
    command=plan.get('command');need(type(command) is list and '--' in command,'ACTUAL_OUTER_COMMAND')
    need(same(runtime.get('command'),command[command.index('--')+1:])
         and type(runtime.get('seconds')) is float and runtime['seconds']==plan['allocation']['outer_seconds']
         and runtime.get('source_sha256')==PINS['acceleration/run_compute_command.py']
         and runtime.get('automatic_retry') is False
         and runtime.get('cumulative_across_commands') is False,'ACTUAL_OUTER_COMMAND')


def calibration(tick=lambda:None):
    """Own fixtures, exact stages; no producer files or outcomes."""
    positives = []; negatives = []
    def reject(label, stage, call):
        tick()
        try:
            call()
        except core.io.AuditError as error:
            need(error.stage == stage, 'WRONG_CONTROL_STAGE:' + label)
            negatives.append(dict(case=label,expected_stage=stage,actual_stage=error.stage))
        else:
            raise core.io.AuditError('ACCEPTED_CORRUPTION:' + label)
    states = {}
    for name in ('rook9','prism9','cube12','target99'):
        tick()
        s = core.initial(name)
        need(same(s,core.parse_state(core.serialize(s))), 'CAL_WIRE_ROUNDTRIP')
        need(same(s['current_metrics'], scalar_metrics(s['n'],s['degree'],s['current'])), 'CAL_SCALAR')
        states[name] = s; positives.append(dict(case=name,metrics=s['current_metrics'],scalar_complete_pairs=s['n']*(s['n']-1)//2))
    need(states['rook9']['current_metrics']['E'] == states['rook9']['current_metrics']['F3'] == 0, 'CAL_ROOK_ZERO')
    r = dict(rng=[0,1,2,3],rng_words=0)
    need(core.next_word(r) == 5760 and r == dict(rng=[2,3,131074,70368744177664],rng_words=1), 'CAL_RNG_LITERAL')
    need(core.seed_words(0) == [0xe220a8397b1dcdaf,0x6e789e6aa1b965f4,0x06c45d188009454f,0xf88bb8a8724c81ec], 'CAL_SEED_LITERAL')
    positives.append(dict(case='handwritten_rng_and_seed'))
    for bound, words, answer, consumed in [(1,[0],0,1),(3,[0,1],1,2),((1<<63)+1,[0,(1<<63)-1],(1<<63)-1,2)]:
        draws = iter(words); used=[]
        def draw():
            value=next(draws);used.append(value);return value
        need(core.bounded(draw,bound) == answer and len(used)==consumed, 'CAL_BOUNDED_REJECTIONS')
    rejected_rng=dict(rng=[0,0,0,1],rng_words=0)
    need(core.bounded(lambda:core.next_word(rejected_rng),3)==0
         and rejected_rng==dict(rng=[(1<<45)+(1<<26),(1<<45)+1,(1<<45)+(1<<17),(1<<45)+(1<<7)],rng_words=3),
         'CAL_REJECTED_WORD_RNG_STATES')
    positives.append(dict(case='bounded_word_rejections_three_bounds_and_handwritten_three_xoshiro_words'))
    for name in ('rook9','cube12'):
        s=core.initial(name,seed=181,forced=1)
        for _ in range(12):
            tick()
            event,_,_=core.transition(s);core.check_trace(copy.deepcopy(event),event)
            need(same(s,core.parse_state(core.serialize(s))), 'CAL_REPLAY_STATE')
        positives.append(dict(case=name+'_complete12_synthetic_replay'))
    wire=core.serialize(states['rook9'])
    replacements=[
      ('magic','HYPERGRAPH_TERNARY_MIXED_STATE_V1','WRONG','WIRE_FIELD:HYPERGRAPH_TERNARY_MIXED_STATE_V1'),
      ('objective',core.OBJECTIVE,'WRONG','STATE_VERSION'),
      ('weight','scalar_weight 577','scalar_weight 1','STATE_SCALAR_WEIGHT'),
      ('integer_bool','step 0','step False','WIRE_INTEGER'),
      ('integer_float','step 0','step 0.0','WIRE_INTEGER'),
      ('integer_negative','step 0','step -1','WIRE_INTEGER'),
      ('integer_overflow','step 0','step 18446744073709551616','WIRE_INTEGER_OVERFLOW'),
      ('forced','forced 0','forced 2','STATE_FORCED'),
      ('real_nonfinite','t_start 0','t_start nan','WIRE_REAL'),
      ('counter','accepted 0','accepted 1','STATE_COUNTERS'),
      ('cache','cn 36\n1','cn 36\n2','STATE_CN_CACHE'),
      ('zero_rng','zero_rng '+ ' '.join(map(str,states['rook9']['rng'])),'zero_rng 0 0 0 0','RNG_ZERO'),
      ('initial_words','rng_words 0','rng_words 1','STATE_INITIAL_RESET'),
      ('zero_population','zero_archive 1','zero_archive 999','STATE_ZERO_POPULATION'),
    ]
    for label,old,new,stage in replacements:
        need(old.encode() in wire, 'CAL_CORRUPTION_REACHABLE:'+label)
        reject(label,stage,lambda old=old,new=new:core.parse_state(wire.replace(old.encode(),new.encode(),1)))
    reject('trailing','WIRE_TRAILING',lambda:core.parse_state(wire+b'EXTRA\n'))
    reject('truncated','WIRE_TRUNCATED',lambda:core.parse_state(wire.rsplit(b'END',1)[0]))
    reject('source','SOURCE_GRAPH_HASH',lambda:core.parse_state(wire,'1'*64))
    reject('config','RESUME_CONFIG_MISMATCH',lambda:core.parse_state(wire,config=dict(seed=2,mix_steps=0,schedule_steps=2048,t_start=0.,t_end=0.,forced=0)))
    reject('bound_zero','RNG_BOUND',lambda:core.bounded(lambda:0,0))
    reject('bound_bool','RNG_BOUND',lambda:core.bounded(lambda:0,True))
    reject('draw_bool','RNG_WORD_TYPE',lambda:core.bounded(lambda:True,1))
    reject('draw_overflow','RNG_WORD_TYPE',lambda:core.bounded(lambda:1<<64,1))
    reject('real_python_underscore','WIRE_REAL',lambda:core.real('1_0'))
    for label,old,new,stage in [
        ('bad_metrics','current_metrics 0 0 0 36 0 0 0','current_metrics 0 0 0 0 0 0 0','STATE_SCORES'),
        ('bad_scalar','current_metrics 0 0 0 36 0 0 0','current_metrics 0 0 0 36 0 0 1','STATE_METRIC_TYPES'),
        ('bad_schedule','schedule_steps 2048','schedule_steps 0','CONFIG_SCHEDULE'),
        ('zero_snapshot_rng','zero_rng '+ ' '.join(map(str,states['rook9']['rng'])),'zero_rng 1 2 3 4','STATE_ZERO_INITIAL_RESET')]:
        need(old.encode() in wire,'CAL_CORRUPTION_REACHABLE:'+label)
        reject(label,stage,lambda old=old,new=new:core.parse_state(wire.replace(old.encode(),new.encode(),1)))
    no_zero=wire.split(b'zero_archive ',1)[0]+b'zero_archive 0\nEND\n'
    reject('zero_completeness','STATE_ZERO_COMPLETENESS',lambda:core.parse_state(no_zero))
    s=core.initial('cube12',seed=181,forced=1);event,_,_=core.transition(s)
    for key in event:
        corrupt=copy.deepcopy(event)
        if key=='temperature':
            corrupt[key]=float('nan');stage='TRACE_TEMPERATURE'
        else:
            corrupt[key]=None;stage='TRACE_CONTENT'
        reject('trace_'+key,stage,lambda corrupt=corrupt:core.check_trace(corrupt,event))
    corrupt=dict(event);corrupt['extra']=0
    reject('trace_extra','TRACE_FIELDS',lambda:core.check_trace(corrupt,event))
    for raw in (b'{"x":0,"x":1}',b'{"x":NaN}'):
        reject('json_'+str(len(negatives)),'JSON',lambda raw=raw:raw_json(raw))
    # Separate raw caller guards use invented metadata, not producer files.
    m=dict(schema='TERNARY_MIXED_FINITE_CONTROLS_V1',runs=[dict(label=x) for x in POSITIVE+['reject_'+x for x in NEGATIVE]],
           positive_calls=27,strict_negative_calls=56,native_calls=83,actual_scientific_input_read=False,
           scientific_search_launched=False,target_resolution=False,independent_approval=False,
           whole_prefix_resume_equalities=4,complete_generic_probe_records=522,attempted_ordinary_proposals=8192)
    manifest_scope(m)
    for key in ('positive_calls','strict_negative_calls','native_calls','whole_prefix_resume_equalities',
                'complete_generic_probe_records','attempted_ordinary_proposals'):
        bad=copy.deepcopy(m);bad[key]=float(bad[key])
        reject('manifest_float_'+key,'FULL_FINITE_SCOPE',lambda bad=bad:manifest_scope(bad))
    for key in ('actual_scientific_input_read','scientific_search_launched','target_resolution','independent_approval'):
        bad=copy.deepcopy(m);bad[key]=0
        reject('manifest_bool_'+key,'FULL_FINITE_SCOPE',lambda bad=bad:manifest_scope(bad))
    for label,bad in [('missing_call',dict(m,runs=m['runs'][:-1])),('duplicate_call',dict(m,runs=m['runs']+[m['runs'][0]])),
                      ('schema',dict(m,schema='WRONG'))]:
        reject('manifest_'+label,'FULL_83_POPULATION',lambda bad=bad:manifest_scope(bad))
    rows=[core.io.canonical(x) for x in core.pair_costs()];costs(rows)
    reject('cost_missing','COMPLETE596_PAIR_COSTS',lambda:costs(rows[:-1]))
    bad=rows[:];x=raw_json(bad[0]);x['delta_F3']+=1;bad[0]=core.io.canonical(x)
    reject('cost_coefficient','COMPLETE596_PAIR_COSTS',lambda:costs(bad))
    bad=rows[:];x=raw_json(bad[0]);x['a']=False;bad[0]=core.io.canonical(x)
    reject('cost_bool_alias','COMPLETE596_PAIR_COSTS',lambda:costs(bad))
    generic_count=0
    for name in ('rook9','prism9','cube12'):
        s=states[name];records=[]
        for i,j in combinations(range(len(s['current'])),2):
            for ix in range(3):
                for jy in range(3):
                    tick()
                    event=core.probe(s,len(records),i,j,ix,jy)
                    proposal=core.candidate(s,i,j,ix,jy)
                    if proposal['valid']:
                        need(same(event['candidate'],scalar_metrics(s['n'],s['degree'],proposal['rows'])),'CAL_PROBE_SCALAR')
                    records.append(core.io.canonical(event))
        generic_count+=check_probes(records,s)
    need(generic_count==522,'CAL522_PROBES')
    # Last own fixture's252records suffice for schema/population falsification.
    reject('probe_omission','PROBE_POPULATION',lambda:check_probes(records[:-1],s))
    reject('probe_extra','PROBE_POPULATION',lambda:check_probes(records+[records[0]],s))
    for key,value in [('proposal_id',False),('rollback',None),('delta_scalar',1)]:
        bad=records[:];x=raw_json(bad[0]);x[key]=value;bad[0]=core.io.canonical(x)
        reject('probe_'+key,'PROBE_RECORD',lambda bad=bad:check_probes(bad,s))
    positives.append(dict(case='complete522_own_probes_and_valid_scalar_comparisons',records=generic_count))
    selection=zero_selection(dict(schema='TERNARY_RETAINED_ZERO_SELECTION_V1',
        selection_rule='First RETAINED current F3zero object, including initial; every distinct retained zero matrix preserved. No unobserved earliest trajectory claim.',
        found=True,first_step=0,retained_distinct_objects=1,carried_from_resume=False,
        target_resolution=False,independent_approval=False),states['rook9'],0,False)
    for key,value in [('first_step',False),('retained_distinct_objects',1.),('found',1),('carried_from_resume',True),('selection_rule','earliest')]:
        bad=dict(selection);bad[key]=value
        reject('zero_selection_'+key,'ZERO_SELECTION',lambda bad=bad:zero_selection(bad,states['rook9'],0,False))
    zero_population(['object_0.adj','object_0.triples'],1)
    reject('zero_export_missing','COMPLETE_ZERO_EXPORT_POPULATION',lambda:zero_population(['object_0.adj'],1))
    reject('zero_export_extra','COMPLETE_ZERO_EXPORT_POPULATION',lambda:zero_population(['object_0.adj','object_0.triples','object_1.adj'],1))
    reject('zero_export_bool_count','ZERO_POPULATION_DOMAIN',lambda:zero_population([],False))
    state_names=['initial.state','final.state','checkpoint_64.state','checkpoint_128.state','zero_capture_73.state']
    required_states(state_names,0,128,64,[73])
    reject('checkpoint_omission','SAVED_STATE_POPULATION',lambda:required_states(state_names[:2]+state_names[3:],0,128,64,[73]))
    reject('capture_omission','SAVED_STATE_POPULATION',lambda:required_states(state_names[:-1],0,128,64,[73]))
    reject('state_extra_name','SAVED_STATE_FILENAME',lambda:required_states(state_names+['wrong.state'],0,128,64,[73]))
    artifact_population(['one','two'],['one','two'])
    reject('artifact_omission','EXACT_CASE_ARTIFACT_POPULATION',lambda:artifact_population(['one'],['one','two']))
    label='synthetic';base='acceleration/results/synthetic/'+label
    cmd=['/usr/bin/timeout','--foreground','--signal=TERM','--kill-after=5s','10.000000s',
         '/usr/bin/prlimit','--as=2147483648:2147483648','--fsize=1073741824:1073741824','--core=0:0',
         '/mnt/c/Users/ikuto/projects/conway-99-graph/build/synthetic','--out',
         '/mnt/c/Users/ikuto/projects/conway-99-graph/'+base,'--seconds','5.000000']
    row=dict(label=label,command=cmd,options=[],receipt=base+'.receipt.json',actual_exit_code=0,expected_exit_code=0,expected_diagnostic=None)
    receipt=dict(command=cmd,actual_exit_code=0,expected_exit_code=0,reaped=True,error=None,observed_euid=1000,
        process_group=10,child_pid=11,cwd='/mnt/c/Users/ikuto/projects/conway-99-graph',stdout=base+'.stdout.log',stderr=base+'.stderr.log')
    launch={k:row[k] for k in ('command','label','expected_exit_code','expected_diagnostic')};native_receipt(row,receipt,launch)
    for key,value in [('actual_exit_code',False),('observed_euid','1000'),('reaped',False),('error','x'),('child_pid',True)]:
        bad=dict(receipt);bad[key]=value
        reject('receipt_'+key,'NATIVE_RECEIPT',lambda bad=bad:native_receipt(row,bad,launch))
    bad=dict(launch);bad['expected_exit_code']=False
    reject('launch_bool','NATIVE_LAUNCH',lambda:native_receipt(row,receipt,bad))
    for index,value,stage in [(0,'timeout','NATIVE_CONTAINED_COMMAND'),(4,'11s','NATIVE_LIMITS'),
            (6,'--as=1:1','NATIVE_LIMITS'),(13,'10','NATIVE_LIMITS'),(11,'/tmp/out','NATIVE_OUTPUT_IDENTITY')]:
        changed=cmd[:];changed[index]=value;badrow=dict(row,command=changed);badreceipt=dict(receipt,command=changed);badlaunch=dict(launch,command=changed)
        reject('command_'+str(index),stage,lambda br=badrow,bc=badreceipt,bl=badlaunch:native_receipt(br,bc,bl))
    runtime=dict(invocation_id='synthetic',command=['python','worker'],seconds=300.,source_sha256=PINS['acceleration/run_compute_command.py'],automatic_retry=False,cumulative_across_commands=False)
    terminal=dict(invocation_id='synthetic',command_exit_code=0,error=None,cleanup=dict(reaped=True,job_active_zero_observed=True,cleanup_errors=[],process_group_live_pids=[]))
    plan=dict(command=['python','supervisor','--','python','worker'],allocation=dict(outer_seconds=300));outer_receipt(runtime,terminal,plan)
    for key,value in [('process_group_live_pids',[12]),('job_active_zero_observed',False),('reaped',False)]:
        bad=copy.deepcopy(terminal);bad['cleanup'][key]=value
        reject('outer_'+key,'ACTUAL_LINUX_CLEANUP',lambda bad=bad:outer_receipt(runtime,bad,plan))
    bad=dict(runtime);bad['source_sha256']='0'*64
    reject('outer_source','ACTUAL_OUTER_COMMAND',lambda:outer_receipt(bad,terminal,plan))
    branch=dict(accepted_overlap=1,rejected_overlap=1,accepted_F3_up=1,accepted_F3_down=1,
                accepted_E_up=1,rejected_valid=1,invalid_selection=1,blocked_pairs=1,late_zero=1)
    branch_population(branch,branch)
    bad=dict(branch);bad['late_zero']=True
    reject('branch_bool_int_alias','ACTUAL_BRANCH_POPULATION',lambda:branch_population(branch,bad))
    positives.append(dict(case='invented_raw_metadata_cost_archive_checkpoint_receipt_guards'))
    reject('harness_wrong_stage','WRONG_CONTROL_STAGE:harness',lambda:reject('harness','WIRE_INTEGER',lambda:need(False,'OTHER')))
    need(len(positives)==10 and len(negatives)==110,'DECLARED_OWN_CALIBRATION_POPULATION')
    return positives,negatives


def full_batch(manifest, pin, read, tick, save):
    manifest_scope(manifest)
    for name,identity in manifest['inputs_sha256'].items():
        pin(name,identity)
    for name,row in manifest['all_raw_artifacts'].items():
        pin(name,row['sha256'],row['bytes'])
    coverage=Counter({key:0 for key in ('accepted_overlap','rejected_overlap','accepted_F3_up',
        'accepted_F3_down','accepted_E_up','rejected_valid','invalid_selection','blocked_pairs','late_zero')})
    margin_values=[]; probes_count=attempted=states_checked=matrices_checked=zero_objects=0
    native_vetoes=[]; runs_checked=[]; prefixes={}
    pair_rows=core.pair_costs();need(len(pair_rows)==596,'PAIR_REFERENCE_POPULATION')
    def target_check(state,label,kind):
        if state['n']!=99:
            return
        a,_,_=core.geometry(state['n'],state['degree'],state[kind])
        verdict=core.dense.full_integer_target(a)
        if verdict['is_target']:
            save('unexpected_target_candidate.json',dict(label=label,kind=kind,matrix=verdict,
                target_resolution='PENDING_SEPARATE_ROOT_REVIEW'))
            raise core.io.AuditError('RAW99_TARGET_IDENTITY_ZERO_REQUIRES_ROOT')
    for row in tqdm(manifest['runs'],desc='Independent mixed finite calls',unit='call'):
        tick();label=row['label'];receipt=read(row['receipt'])
        pin(row['receipt'],row['receipt_sha256'])
        for kind in ('stdout','stderr'):
            pin(receipt[kind],receipt[kind+'_sha256'])
        launch_name=row['receipt'].replace('.receipt.json','.launch.json')
        launch=read(launch_name)
        guard=native_receipt(row,receipt,launch)
        cmd=row['command']
        native_path=origin_path(cmd[9]).relative_to(ROOT).as_posix()
        need(native_path==BINARY and manifest['inputs_sha256'].get(native_path)==PINS[BINARY],'NATIVE_BINARY_PIN')
        directory=origin_path(row['receipt']).parent/label
        # Receipt parent is a real file; output directory is bounded by its exact label.
        need(directory.is_relative_to(ROOT),'NATIVE_DIRECTORY')
        listed=set(row['artifacts'])
        actual={f.relative_to(ROOT).as_posix() for f in directory.rglob('*') if f.is_file()} if directory.exists() else set()
        artifact_population(listed,actual)
        for name,item in row['artifacts'].items():
            pin(name,item['sha256'],item['bytes'])
        if label.startswith('reject_'):
            case=label[len('reject_'):];diagnostic=DIAGNOSTICS[case]
            need(row['expected_exit_code']==row['actual_exit_code']==2 and row['expected_diagnostic']==diagnostic
                 and path(receipt['stdout']).read_bytes()==b''
                 and path(receipt['stderr']).read_bytes()==(diagnostic+'\n').encode('ascii'),'PRECISE_NATIVE_VETO')
            expected_own={'triple_duplicate':'DOMAIN_POINT_DEGREE','zero_triples':'DOMAIN_POINT_DEGREE',
                          'import_duplicate':'DOMAIN_POINT_DEGREE'}.get(case,diagnostic)
            try:
                opts,config=options(row['options']);s=starting(opts,config)
                need(not opts.get('--probe-all') or (s['n']<=12 and s['step']==0),'PROBE_SCOPE')
            except core.io.AuditError as error:
                need(error.stage==expected_own,'NATIVE_INPUT_WRONG_STAGE:'+case)
                native_vetoes.append(dict(case=case,native_diagnostic=diagnostic,
                    independent_input_rejection_stage=error.stage,exact_saved_exit_stderr=True))
            else:
                raise core.io.AuditError('NATIVE_INPUT_CORRUPTION_ACCEPTED:'+case)
            continue
        need(row['expected_exit_code']==row['actual_exit_code']==0 and row['expected_diagnostic'] is None,'POSITIVE_NATIVE_EXIT')
        opts,config=options(row['options']);s=starting(opts,config)
        target_check(s,label,'current');target_check(s,label,'best')
        need(not opts.get('--probe-all') or (s['n']<=12 and s['step']==0),'PROBE_SCOPE')
        need(same(s,core.parse_state((directory/'initial.state').read_bytes(),
                                   s['source_graph_sha256'],config)),'EXACT_INITIAL_IMPORT_RESET')
        start=s['step'];initial=copy.deepcopy(s['current_metrics'])
        saved_states={}
        state_names=[];captured_steps=[]
        for name in row['artifacts']:
            file=path(name)
            if file.suffix=='.state':
                state=core.parse_state(wire_bytes(file),s['source_graph_sha256'],config)
                target_check(state,label+'/'+file.name,'current');target_check(state,label+'/'+file.name,'best')
                state_names.append(file.name)
                if file.name not in ('initial.state','final.state'):
                    need(core.re.fullmatch(r'(?:checkpoint|zero_capture)_[0-9]+\.state',file.name)
                         and int(file.stem.rsplit('_',1)[1])==state['step'],'SAVED_STATE_FILENAME')
                saved_states.setdefault(state['step'],[]).append((name,state))
                states_checked+=1;matrices_checked+=2
        def compare_states():
            for name,state in saved_states.pop(s['step'],[]):
                need(same(s,state),'SAVED_COMPLETE_STATE:'+name)
        compare_states()
        cost=(directory/'pair_costs.jsonl').read_bytes().splitlines()
        costs(cost)
        if opts.get('--probe-all'):
            records=(directory/'probes.jsonl').read_bytes().splitlines()
            probes_count+=check_probes(records,s,tick)
        result=raw_json((directory/'result.json').read_bytes())
        count=result['proposals_this_invocation']
        need(type(count) is int and count== (0 if label=='rook_stop_zero' else opts['--steps']),
             'COMPLETE_REQUESTED_FINITE_STEPS')
        records=(directory/'moves.jsonl').read_bytes().splitlines()
        need(len(records)==count,'COMPLETE_FINITE_TRACE')
        for raw in records:
            tick();expected,margin,captured=core.transition(s)
            core.check_trace(raw_json(raw),expected)
            if margin is not None:
                margin_values.append(margin)
            valid=expected['admissible'];accepted=expected['accepted'];overlap=not expected['disjoint']
            coverage['accepted_overlap']+=int(valid and accepted and overlap)
            coverage['rejected_overlap']+=int(valid and not accepted and overlap)
            coverage['accepted_F3_up']+=int(accepted and expected['candidate']['F3']>expected['before']['F3'])
            coverage['accepted_F3_down']+=int(accepted and expected['candidate']['F3']<expected['before']['F3'])
            coverage['accepted_E_up']+=int(accepted and expected['candidate']['E']>expected['before']['E'])
            coverage['rejected_valid']+=int(valid and not accepted)
            coverage['invalid_selection']+=int(not expected['exclusive'])
            coverage['blocked_pairs']+=int(expected['exclusive'] and not expected['absent_after_removal'])
            if captured:
                captured_steps.append(s['step'])
                need((directory/('zero_capture_'+str(s['step'])+'.state')).is_file(),'IMMEDIATE_ZERO_CAPTURE_STATE')
            if s['step']%opts['--checkpoint-every']==0:
                need((directory/('checkpoint_'+str(s['step'])+'.state')).is_file(),'SCHEDULED_CHECKPOINT')
            compare_states()
        need(not saved_states,'ALL_SAVED_STATE_STEPS');attempted+=count
        required_states(state_names,start,s['step'],opts['--checkpoint-every'],captured_steps)
        need(same(s,core.parse_state((directory/'final.state').read_bytes(),
                                   s['source_graph_sha256'],config)),'FINAL_COMPLETE_STATE')
        for kind in ('current','best'):
            a,_,_=core.geometry(s['n'],s['degree'],s[kind])
            need((directory/(kind+'.adj')).read_bytes()==core.io.matrix_bytes(a),'RAW_ADJACENCY_EXPORT')
            if s['n']==99:
                verdict=core.dense.full_integer_target(a)
                if verdict['is_target']:
                    save('unexpected_target_candidate.json',dict(label=label,kind=kind,
                        raw_path=(directory/(kind+'.adj')).relative_to(ROOT).as_posix(),matrix=verdict,
                        target_resolution='PENDING_SEPARATE_ROOT_REVIEW'))
                    raise core.io.AuditError('RAW99_TARGET_IDENTITY_ZERO_REQUIRES_ROOT')
            matrices_checked+=1
        selection=raw_json((directory/'zero_selection.json').read_bytes())
        zero_selection(selection,s,start,'--resume' in opts)
        coverage['late_zero']+=int(bool(s['zeros']) and s['zeros'][0]['step']>0)
        objects={p.name:p for p in (directory/'zero_objects').glob('*')} if (directory/'zero_objects').exists() else {}
        zero_population(objects,len(s['zeros']))
        for j,z in enumerate(s['zeros']):
            a,m,_=core.geometry(s['n'],s['degree'],z['rows'])
            need(m['F3']==0 and objects[f'object_{j}.adj'].read_bytes()==core.io.matrix_bytes(a),'ZERO_RAW_MATRIX')
            r=core.Reader(objects[f'object_{j}.triples'].read_bytes());r.tag('TERNARY_RETAINED_ZERO_TRIPLES_V1')
            need(r.integer('step')==z['step'] and r.integer('n')==s['n'] and r.integer('degree')==s['degree']
                 and r.rows('triples',s['n'],s['degree'])==z['rows'],'ZERO_RAW_TRIPLES');r.end()
            zero_objects+=1;matrices_checked+=1
        expected_result=dict(objective=core.OBJECTIVE,move_kernel=core.KERNEL,distribution=core.DISTRIBUTION,
            n=s['n'],point_degree=s['degree'],initial=initial,current=s['current_metrics'],best=s['best_metrics'],
            starting_step=start,ending_step=s['step'],proposals_this_invocation=count,admissible_total=s['admissible'],
            accepted_total=s['accepted'],best_updates_total=s['best_updates'],rng_words_total=s['rng_words'],
            retained_zero_objects=len(s['zeros']),stop_reason='RAW_F3_ZERO_PENDING_INDEPENDENT_FULL_INTEGER_SRG_VALIDATOR'
            if label=='rook_stop_zero' else 'REQUESTED_STEPS_COMPLETE',
            historical_native_state_written=False,independent_approval=False,target_resolution=False)
        elapsed=result.pop('elapsed_seconds')
        need(type(elapsed) in (float,int) and 0<=elapsed<=guard+1 and same(result,expected_result),'RESULT_LITERAL')
        runs_checked.append(dict(label=label,proposals=count,ending_step=s['step'],
            current=s['current_metrics'],best=s['best_metrics'],zero_objects=len(s['zeros'])))
        prefixes[label]=directory
    for family in ('target','prism','cube','import'):
        whole,prefix,resume=(prefixes[family+x] for x in ('_whole','_prefix73','_resumed'))
        for name in ('final.state','current.adj','best.adj'):
            need((whole/name).read_bytes()==(resume/name).read_bytes(),'SPLIT_OBJECT')
        need((whole/'moves.jsonl').read_bytes()==(prefix/'moves.jsonl').read_bytes()+(resume/'moves.jsonl').read_bytes(),
             'SPLIT_TRACE')
        left={p.name:p.read_bytes() for p in (whole/'zero_objects').glob('*')}
        right={p.name:p.read_bytes() for p in (resume/'zero_objects').glob('*')}
        need(left==right,'SPLIT_ZERO_OBJECTS')
    need(attempted==8192 and probes_count==522 and len(native_vetoes)==56 and len(runs_checked)==27,
         'COMPLETE_FINITE_POPULATIONS')
    branch_population(dict(coverage),manifest['coverage'])
    need(margin_values and min(margin_values)>1e-12 and math.isclose(min(margin_values),
         manifest['minimum_floating_acceptance_margin'],rel_tol=1e-12,abs_tol=1e-14),'ACTUAL_ACCEPTANCE_MARGIN')
    save('native_vetoes.json',native_vetoes);save('finite_runs.json',runs_checked)
    return dict(native_positive_calls=27,native_strict_negative_calls=56,complete_native_calls=83,
        attempted_proposals_checked=attempted,complete_generic_probes=probes_count,pair_cost_rows_checked=27*596,
        complete_saved_states_checked=states_checked,complete_matrix_observations=matrices_checked,
        retained_zero_object_observations=zero_objects,whole_prefix_resume_equalities=4,
        actual_branch_population=dict(coverage),minimum_acceptance_margin=min(margin_values),
        target_candidates=0,complete_finite_trace_only=True)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('mode',choices=['calibration','full']);p.add_argument('--seconds',type=float,required=True)
    p.add_argument('--out',type=Path,required=True)
    for name in ('source','core','spec'):
        p.add_argument('--'+name+'-sha256',required=True)
    p.add_argument('--control-plan',required=True);p.add_argument('--control-plan-sha256',required=True)
    p.add_argument('--expected-head',required=True);p.add_argument('--protected-ledger-sha256',required=True)
    p.add_argument('--protected-index-sha256',required=True)
    for name in ('calibration','producer-manifest','producer-summary','runtime-manifest','runtime-summary'):
        p.add_argument('--'+name);p.add_argument('--'+name+'-sha256')
    args=p.parse_args();deadline=CommandDeadline(args.seconds,allocation_reason='Independent complete finite mixed controls;20save; no native calls or scientific search')
    out=args.out.resolve();need(out.is_relative_to(ROOT) and not out.exists(),'FRESH_OUTPUT');out.mkdir(parents=True)
    pins={};protected_before={}
    def tick():
        need(not deadline.status()['stop_required'] and deadline.status()['remaining_seconds']>20,'SAVE_RESERVE')
    def pin(name,identity,size=None):
        tick();f=path(name);h=hashlib.sha256();total=0
        need(name!='CLAIMS.yaml','HISTORICAL_STATE_NOT_IMMUTABLE_DEPENDENCY')
        need(type(identity) is str and core.re.fullmatch('[0-9a-f]{64}',identity) is not None
             and (size is None or type(size) is int and size>=0),'IDENTITY_TYPES')
        need(f.stat().st_size<=FINITE_FILE_CAP,'FINITE_FILE_SIZE')
        with f.open('rb') as stream:
            while chunk:=stream.read(1024*1024):
                tick();h.update(chunk);total+=len(chunk)
        need(h.hexdigest()==identity and (size is None or total==size),'INPUT_IDENTITY:'+name)
        need(name not in pins or pins[name]==identity,'INPUT_CONFLICT');pins[name]=identity
    def read(name):
        return raw_json(wire_bytes(path(name)))
    def save(name,value):
        (out/name).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf8')
    def protect():
        head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        ledger=hashlib.sha256((ROOT/'CLAIMS.yaml').read_bytes()).hexdigest()
        index=hashlib.sha256((ROOT/'.git/index').read_bytes()).hexdigest()
        need((head,ledger,index)==(args.expected_head,args.protected_ledger_sha256,args.protected_index_sha256),'PROTECTED_CONTEXT')
        return dict(head=head,ledger_sha256=ledger,index_sha256=index,role='historical protected observations, outside immutable inputs')
    try:
        protected_before=protect()
        for name,identity in {**PINS,SOURCE:args.source_sha256,CORE:args.core_sha256,SPEC:args.spec_sha256,
                              args.control_plan:args.control_plan_sha256}.items():
            pin(name,identity)
        control_plan=read(args.control_plan)
        for name,identity in control_plan['inputs_sha256'].items():
            pin(name,identity)
        build=read(BUILD)
        need(build['schema']=='TERNARY_MIXED_NATIVE_BUILD_V1'
             and build['source_cpp_sha256']==PINS[CPP] and build['binary_path']==BINARY
             and build['binary_sha256']==PINS[BINARY]
             and build['compiler_sha256']=='1353e9bdd29a7295c7226bf6c63abccce056d8cac31f112e5cdbecc3f28c2769',
             'LITERAL_BUILD_CLOSURE')
        for name,identity in build['inputs_sha256'].items():
            pin(name,identity)
        positives,negatives=calibration(tick);save('controls.json',dict(positive=positives,strict_negative=negatives))
        controls_name=(out/'controls.json').relative_to(ROOT).as_posix()
        pin(controls_name,hashlib.sha256((out/'controls.json').read_bytes()).hexdigest())
        report=dict(producer='/root/native_driver',verifier='/root/checkpoint_audit',method='independent_artifact_check',
            timestamp=datetime.now(timezone.utc).isoformat(),command=[sys.executable,*sys.argv],cwd=str(ROOT),
            python=platform.python_version(),numpy=core.dense.np.__version__,mode=args.mode,source_sha256=args.source_sha256,
            core_sha256=args.core_sha256,spec_sha256=args.spec_sha256,positive_controls=len(positives),
            strict_negative_controls=len(negatives),producer_outputs_inspected=False,native_calls=0,mathematical_trajectory_claim=False,
            target_resolution='NONE',independent_of_discovery_producer=True)
        report['scope']=dict(unrestricted_target=False,target_resolution='NONE',exclusion_scope='Finite engineering controls only; no mathematical exclusion')
        report['controls']=dict(path=controls_name,sha256=pins[controls_name],positive=10,strict_negative=110,
            complete_own_generic_probes=522,producer_controls_read_during_calibration=False)
        if args.mode=='calibration':
            report['status']='INDEPENDENT_TERNARY_MIXED_ENGINE_V1_CALIBRATION_PASS'
        else:
            values=[]
            for key in ('calibration','producer_manifest','producer_summary','runtime_manifest','runtime_summary'):
                name=getattr(args,key);identity=getattr(args,key+'_sha256')
                need(name is not None and identity is not None,'EXPLICIT_FULL_IDENTITIES')
                pin(name,identity);values.append(read(name))
            cal,manifest,producer,runtime,terminal=values
            need(cal['status']=='INDEPENDENT_TERNARY_MIXED_ENGINE_V1_CALIBRATION_PASS'
                 and cal['source_sha256']==args.source_sha256 and cal['core_sha256']==args.core_sha256
                 and cal['spec_sha256']==args.spec_sha256,'APPLICABLE_CALIBRATION')
            for name,identity in cal['inputs_sha256'].items():
                pin(name,identity)
            need(producer['status']=='TERNARY_MIXED_CONTROLS_PRODUCED_PENDING_INDEPENDENT_CHECK'
                 and producer['manifest']==args.producer_manifest
                 and producer['manifest_sha256']==args.producer_manifest_sha256,'PRODUCER_SUMMARY')
            outer_receipt(runtime,terminal,control_plan)
            report['finite_raw_scope']=full_batch(manifest,pin,read,tick,save)
            for file in ('native_vetoes.json','finite_runs.json'):
                name=(out/file).relative_to(ROOT).as_posix()
                pin(name,hashlib.sha256((out/file).read_bytes()).hexdigest())
            report['producer_outputs_inspected']=True
            report['status']='INDEPENDENT_TERNARY_MIXED_ENGINE_V1_CONTROLS_PASS'
        report.update(inputs_sha256=pins,historical_protected_execution_state=dict(before=protected_before,after=protect()),
            shared_components=['Independent dense13783 and geometry/strict IO98efe; new wire/RNG/replay core',
             'NumPy exact int64; Python/std JSON/hash/filesystem; pinned deadline/supervisor/runtime',
             'Native/producer source is authenticated data only, never imported or executed'],
            limitations=['Own calibration approves its tested synthetic behavior only; full mode separately checks the complete declared finite native batch. Future saved-object/science paths and target resolution require separate gates.',
             'Bounded rejection has unbiased residue counts conditional on uniform independent input words; no random-quality proof for deterministic xoshiro.',
             'No graph-space coverage, ergodicity, performance or external peer-review assertion.'],deadline=deadline.status())
        save('summary.json',report)
    except BaseException as error:
        save('failure.json',dict(error=repr(error),inputs_sha256=pins,historical_protected_before=protected_before,
             deadline=deadline.status(),outputs_preserved=True,automatic_retry=False,native_calls=0,target_resolution='NONE'))
        raise


if __name__=='__main__':
    main()
