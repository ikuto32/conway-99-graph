"""SOURCE ONLY: contained build and finite controls for new ternary C++ V1.

There is deliberately no scientific-run mode or graph-search allocation here.
"""
import argparse
import hashlib
import json
import math
import os
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from tqdm import tqdm
from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
CPP=ROOT/'acceleration/hypergraph_ternary_mixed_anneal_20261003_v1.cpp'
SPEC=Path(__file__).with_name(Path(__file__).stem+'_spec.md')
OBJECTIVE='SRG_COMPLETE_TERNARY_PAIR_RESIDUE_V1'
KERNEL='ALL_LINE_EXCLUSIVE_SWAP_TERNARY_V1'
DISTRIBUTION='ALL_LABELLED_LINES_REJECTION_BOUNDED_XOSHIRO256SS_V1'
COMPILER=Path('/usr/bin/g++')
COMPILER_SHA='1353e9bdd29a7295c7226bf6c63abccce056d8cac31f112e5cdbecc3f28c2769'
CODE=[Path(__file__),CPP,SPEC,CPP.with_name(CPP.stem+'_spec.md'),
      ROOT/'acceleration/design_20261003_ternary_mixed_search_v1.md',
      ROOT/'acceleration/hypergraph_weight60_anneal_20261002_v2.cpp',
      ROOT/'docs/CANDIDATE_20261003_TERNARY_DEGREE14_EXACTNESS_V1.md',
      ROOT/'acceleration/audit_20261003_ternary_degree14_exactness_v1.md',
      ROOT/'docs/CANDIDATE_20261003_TERNARY_RESIDUE_ENERGY_BOUNDS_V1.md',
      ROOT/'acceleration/audit_20261003_ternary_residue_energy_bounds_v1.md',
      ROOT/'acceleration/command_deadline.py',ROOT/'acceleration/run_compute_command.py',
      ROOT/'acceleration/native_budget_env_v1/pyproject.toml',ROOT/'acceleration/native_budget_env_v1/uv.lock']
POSITIVE=['rook_initial_probes','prism_initial_probes','cube_initial_probes',
          'target_initial','target_forced','target_greedy','target_anneal','target_cooling','target_mixed',
          'rook_forced','prism_forced','cube_forced',
          *[family+suffix for family in ['target','prism','cube','import'] for suffix in ['_whole','_prefix73','_resumed']],
          'import_rook_reset','import_target_reset','rook_stop_zero']
NEGATIVE=['magic','objective','kernel','distribution','source','weight','seed','mix','schedule','temperature','forced',
          'counter','rng_zero','rng_negative','rng_overflow','integer_bool','integer_float','metric_overflow','metric_scalar',
          'metric_score','histogram','cache','cache_bool','cache_float','triple_range','triple_duplicate','degree',
          'trailing','truncated','zero_count','zero_missing_current','zero_missing_best','zero_duplicate','zero_rng',
          'zero_counter','zero_triples','zero_initial_rng','zero_initial_words','initial_rng','initial_words','initial_best',
          'import_magic','import_domain','import_hash','import_duplicate','import_trailing','import_integer_bool',
          'arg_duplicate','arg_unknown','arg_missing','arg_conflict','arg_zero_interval','arg_nonfinite','arg_negative',
          'arg_overflow','probe_scope']

def need(ok,stage):
    if not ok:raise ValueError(stage)

def stamp():return datetime.now(timezone.utc).isoformat()
def key(path):return Path(path).resolve().relative_to(ROOT).as_posix()
def read(path):return json.loads(Path(path).read_bytes())
def digest(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(path,value):
    with Path(path).open('x',encoding='utf8',newline='\n') as f:json.dump(value,f,indent=2);f.write('\n')
def text(path,value):
    with Path(path).open('x',encoding='ascii',newline='\n') as f:f.write(value)
def tick(deadline,reserve=30):
    state=deadline.status()
    need(not state['stop_required'] and state['remaining_seconds']>reserve,'not completed within the allocated budget; preserve failed/completed/unattempted population')
    return state
def pin(path,wanted,pins,deadline):
    tick(deadline);path=Path(path).resolve();need(path.is_relative_to(ROOT) and path.is_file(),'PIN_PATH')
    actual=digest(path);need(wanted is None or wanted==actual,'PIN_HASH:'+key(path))
    need(key(path) not in pins or pins[key(path)]==actual,'PIN_REPEAT');pins[key(path)]=actual;return actual
def artifacts(directory):
    return {key(p):dict(sha256=digest(p),bytes=p.stat().st_size) for p in sorted(directory.rglob('*')) if p.is_file()}

def contained(args,pins,deadline):
    need(sys.platform.startswith('linux') and os.geteuid()==1000,'LINUX_DEFAULT_UID1000')
    path=args.supervision_out.resolve()/'manifest.json';m=read(path)
    pin(ROOT/'acceleration/run_compute_command.py',m['source_sha256'],pins,deadline)
    need(m['seconds']>=args.seconds+20 and m['automatic_retry'] is False and m['cumulative_across_commands'] is False,'OUTER_ALLOCATION')
    need(str(Path(__file__).resolve()) in m['command'] or key(__file__) in m['command'],'EXACT_WRAPPER_SUPERVISION')
    group=os.getpgid(0);guard=[x.decode() for x in (Path('/proc')/str(group)/'cmdline').read_bytes().split(b'\0') if x]
    need(guard and Path(guard[0]).name=='timeout' and '--signal=KILL' in guard,'LIVE_SUPPORTED_LINUX_GROUP')
    return dict(manifest=key(path),manifest_sha256=digest(path),invocation_id=m['invocation_id'],outer_seconds=m['seconds'],process_group=group,guard_argv=guard,observed_euid=os.geteuid())

def execute(argv,prefix,deadline,expected):
    tick(deadline);start=time.monotonic();caught=None
    with Path(str(prefix)+'.stdout.log').open('xb') as out,Path(str(prefix)+'.stderr.log').open('xb') as err:
        child=subprocess.Popen(argv,cwd=ROOT,stdout=out,stderr=err)
        try:
            need(os.getpgid(child.pid)==os.getpgid(0),'CHILD_CONTAINED')
            while child.poll() is None:tick(deadline);time.sleep(.05)
        except BaseException as error:caught=error
        finally:
            if child.poll() is None:
                child.terminate()
                try:child.wait(timeout=5)
                except subprocess.TimeoutExpired:child.kill()
            code=child.wait(timeout=5)
    receipt=dict(timestamp=stamp(),command=argv,cwd=str(ROOT),actual_exit_code=code,expected_exit_code=expected,
        wall_seconds=time.monotonic()-start,child_pid=child.pid,process_group=os.getpgid(0),observed_euid=os.geteuid(),reaped=True,
        stdout=key(str(prefix)+'.stdout.log'),stderr=key(str(prefix)+'.stderr.log'),error=None if caught is None else repr(caught),independent_approval=False)
    for name in ['stdout','stderr']:receipt[name+'_sha256']=digest(ROOT/receipt[name])
    save(str(prefix)+'.receipt.json',receipt)
    if caught is not None:raise caught
    need(code==expected,'CHILD_EXIT');return receipt

def build(args,out,pins,deadline):
    need(digest(COMPILER)==COMPILER_SHA,'COMPILER_HASH')
    version=subprocess.run([str(COMPILER),'--version'],capture_output=True,text=True,timeout=deadline.child_seconds(10,reserve_seconds=30))
    need(version.returncode==0 and version.stdout.startswith('g++ (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0'),'COMPILER_VERSION')
    allowed=deadline.child_seconds(args.compiler_seconds,reserve_seconds=30)
    command=['/usr/bin/timeout','--foreground','--signal=TERM','--kill-after=5s',f'{allowed:.6f}s',str(COMPILER),'-std=c++17','-O3','-Wall','-Wextra','-Werror',str(CPP),'-o',str(out/'hypergraph_ternary_mixed')]
    receipt=execute(command,out/'build',deadline,0)
    manifest=dict(schema='TERNARY_MIXED_NATIVE_BUILD_V1',timestamp=stamp(),source_commit=args.source_commit,command=command,
        source_cpp_sha256=pins[key(CPP)],binary_path=key(out/'hypergraph_ternary_mixed'),binary_sha256=digest(out/'hypergraph_ternary_mixed'),
        compiler_path=str(COMPILER),compiler_sha256=COMPILER_SHA,compiler_version_stdout=version.stdout,inputs_sha256=dict(pins),
        receipt=key(out/'build.receipt.json'),receipt_sha256=digest(out/'build.receipt.json'),independent_approval=False)
    save(out/'build_manifest.json',manifest);return dict(status='TERNARY_MIXED_BUILD_COMPLETE_PENDING_INDEPENDENT_CHECK',manifest=key(out/'build_manifest.json'),manifest_sha256=digest(out/'build_manifest.json'),binary_sha256=manifest['binary_sha256'],receipt=receipt)

def authenticate(args,pins,deadline):
    need(args.binary and args.binary_sha256 and args.build_manifest and args.build_manifest_sha256,'EXPLICIT_BUILD')
    pin(args.binary,args.binary_sha256,pins,deadline);pin(args.build_manifest,args.build_manifest_sha256,pins,deadline);m=read(args.build_manifest)
    need(m['schema']=='TERNARY_MIXED_NATIVE_BUILD_V1' and m['source_cpp_sha256']==pins[key(CPP)] and m['binary_sha256']==args.binary_sha256 and m['compiler_sha256']==COMPILER_SHA,'BUILD_BINDING')
    for path,identity in m['inputs_sha256'].items():pin(ROOT/path,identity,pins,deadline)

def fixture(name):
    if name=='rook9':return [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8]]
    return [[x,x+33,x+66] for x in range(33)]+[[x,(x+1)%99,(x+4)%99] for x in range(99)]+[[x,(x+7)%99,(x+18)%99] for x in range(99)]
def input_fixture(out,name,pins,deadline):
    rows=fixture(name);n,pd=(9,2) if name=='rook9' else (99,7);a=[[0]*n for _ in range(n)]
    for row in rows:
        for i in range(3):
            for j in range(i+1,3):a[row[i]][row[j]]=a[row[j]][row[i]]=1
    matrix=out/(name+'_input.adj');text(matrix,str(n)+'\n'+''.join(''.join(map(str,row))+'\n' for row in a));identity=pin(matrix,None,pins,deadline)
    path=out/(name+'_input.txt');text(path,f'TERNARY_LINEAR_GRAPH_INPUT_V1\nn {n}\ndegree {pd}\nsource_graph_sha256 {identity}\ntriples {len(rows)}\n'+''.join(' '.join(map(str,row))+'\n' for row in rows)+'END\n');pin(path,None,pins,deadline)
    return path,identity

def native(args,out,label,options,pins,deadline,expected=0,diagnostic=None):
    allowed=deadline.child_seconds(args.native_seconds,reserve_seconds=30)
    directory=out/label
    command=['/usr/bin/timeout','--foreground','--signal=TERM','--kill-after=5s',f'{allowed:.6f}s','/usr/bin/prlimit',
        f'--as={args.address_space_bytes}:{args.address_space_bytes}',f'--fsize={args.file_bytes}:{args.file_bytes}','--core=0:0',str(args.binary.resolve()),
        '--out',str(directory),'--seconds',f'{max(.001,allowed-5):.6f}',*options]
    save(out/(label+'.launch.json'),dict(timestamp=stamp(),label=label,command=command,expected_exit_code=expected,expected_diagnostic=diagnostic,deadline=deadline.status(),independent_approval=False))
    receipt=execute(command,out/label,deadline,expected)
    if diagnostic is not None:need((out/(label+'.stderr.log')).read_bytes()==(diagnostic+'\n').encode('ascii') and (out/(label+'.stdout.log')).read_bytes()==b'','PRECISE_DIAGNOSTIC:'+label)
    row=dict(label=label,command=command,options=options,expected_exit_code=expected,actual_exit_code=receipt['actual_exit_code'],expected_diagnostic=diagnostic,
        receipt=key(out/(label+'.receipt.json')),receipt_sha256=digest(out/(label+'.receipt.json')),artifacts=artifacts(directory) if directory.exists() else {})
    for path,item in row['artifacts'].items():pin(ROOT/path,item['sha256'],pins,deadline)
    return row

def controls(args,out,pins,deadline):
    authenticate(args,pins,deadline);runs=[];splits=[]
    save(out/'control_population.json',dict(schema='TERNARY_MIXED_FROZEN_FINITE_POPULATION_V1',positive_labels=POSITIVE,negative_labels=['reject_'+x for x in NEGATIVE],
        positive_calls=len(POSITIVE),negative_calls=len(NEGATIVE),native_calls=len(POSITIVE)+len(NEGATIVE),requested_ordinary_proposals=8704,expected_attempted_ordinary_proposals=8192,
        ordinary_count_reason='Rook stop-zero requests512 but must attempt0 on known generic initial F3zero. All other positive trajectories request8192 total.',
        scope='Finite generic fixtures and explicit unoptimized99 incidence fixture only; no saved scientific warm graph/input or stochastic search.',
        success='All preregistered outcomes/stages, complete522 generic probes,596 pair-cost records per emit, exact splits, designated actual branch populations and native zero scope controls. All failures/unattempted preserved.'))
    rook_input,rook_sha=input_fixture(out,'rook9',pins,deadline);target_input,target_sha=input_fixture(out,'target99',pins,deadline)
    def call(label,name='target99',steps=512,seed=99034001,temp=1000000,end=None,mix=0,forced=False,imported=None,resumed=None,expected=0,diagnostic=None,extra=None):
        opts=['--seed',str(seed),'--steps',str(steps),'--mix-steps',str(mix),'--schedule-steps','2048','--temperature-start',str(temp),'--temperature-end',str(temp if end is None else end),
            '--verify-every','1','--checkpoint-every','64','--checkpoint-seconds','20','--trace-prefix','4096','--emit-pair-costs']
        if resumed:opts+=['--resume',str(resumed),'--source-graph-sha256',target_sha if imported==target_input else rook_sha if imported==rook_input else '0'*64]
        elif imported:opts+=['--graph-input',str(imported),'--source-graph-sha256',target_sha if imported==target_input else rook_sha]
        else:opts+=['--fixture',name]
        if forced:opts.append('--forced')
        if extra:opts+=extra
        row=native(args,out,label,opts,pins,deadline,expected,diagnostic);runs.append(row)
        save(out/('progress_'+str(len(runs))+'.json'),dict(completed_calls=len(runs),planned_calls=len(POSITIVE)+len(NEGATIVE),last_label=label,deadline=deadline.status(),independent_approval=False));return row
    for label,name in [('rook','rook9'),('prism','prism9'),('cube','cube12')]:call(label+'_initial_probes',name=name,steps=0,temp=0,extra=['--probe-all'])
    for label,settings in tqdm([('target_initial',dict(steps=0,temp=0)),('target_forced',dict(forced=True,temp=0)),('target_greedy',dict(temp=0)),
        ('target_anneal',dict()),('target_cooling',dict(temp=2000000,end=10)),('target_mixed',dict(temp=1000000,mix=128)),
        ('rook_forced',dict(name='rook9',forced=True,temp=0)),('prism_forced',dict(name='prism9',forced=True,temp=0)),('cube_forced',dict(name='cube12',forced=True,temp=0))],desc='Ternary finite paths'):call(label,**settings)
    families=[('target',dict(seed=99034002,temp=1000000,mix=64)),('prism',dict(name='prism9',seed=181,temp=0)),
              ('cube',dict(name='cube12',seed=99034003,temp=1000)),('import',dict(imported=target_input,seed=99034004,temp=2000000,end=10,mix=64))]
    for family,settings in families:
        call(family+'_whole',steps=512,**settings);call(family+'_prefix73',steps=73,**settings);call(family+'_resumed',steps=439,resumed=out/(family+'_prefix73/final.state'),**settings)
        for member in ['final.state','current.adj','best.adj']:
            need((out/(family+'_whole')/member).read_bytes()==(out/(family+'_resumed')/member).read_bytes(),'SPLIT_OBJECT:'+family+'/'+member)
        need((out/(family+'_whole/moves.jsonl')).read_bytes()==(out/(family+'_prefix73/moves.jsonl')).read_bytes()+(out/(family+'_resumed/moves.jsonl')).read_bytes(),'SPLIT_TRACE:'+family)
        a=artifacts(out/(family+'_whole/zero_objects'));b=artifacts(out/(family+'_resumed/zero_objects'))
        need({Path(p).name:v for p,v in a.items()}=={Path(p).name:v for p,v in b.items()},'SPLIT_ZERO_ARCHIVE:'+family)
        splits.append(dict(family=family,total_steps=512,split_step=73,final_state_matrix_trace_zero_bytes_equal=True))
    call('import_rook_reset',name='rook9',steps=0,temp=0,imported=rook_input);call('import_target_reset',steps=0,temp=0,imported=target_input)
    call('rook_stop_zero',name='rook9',steps=512,temp=0,extra=['--stop-at-zero'])
    base=(out/'target_prefix73/final.state').read_text().splitlines();zero=(out/'rook_initial_probes/final.state').read_text().splitlines()
    def field(lines,name,value):
        at=next(i for i,x in enumerate(lines) if x.startswith(name+' '));lines[at]=name+' '+value
    mutations={
        'magic':('MAGIC','x','WIRE_FIELD:HYPERGRAPH_TERNARY_MIXED_STATE_V1'),
        'objective':('objective','wrong','STATE_VERSION'),'kernel':('move_kernel','wrong','STATE_VERSION'),'distribution':('distribution','wrong','STATE_VERSION'),
        'source':('source_graph_sha256','1'*64,'SOURCE_GRAPH_HASH'),'weight':('scalar_weight','1','STATE_SCALAR_WEIGHT'),
        'seed':('seed','1','RESUME_CONFIG_MISMATCH'),'mix':('mix_steps','1','RESUME_CONFIG_MISMATCH'),'schedule':('schedule_steps','1','RESUME_CONFIG_MISMATCH'),
        'temperature':('t_start','1','RESUME_CONFIG_MISMATCH'),'forced':('forced','2','STATE_FORCED'),
        'counter':('accepted','999999','STATE_COUNTERS'),'rng_zero':('rng','0 0 0 0','RNG_ZERO'),'rng_negative':('rng','-1 0 0 0','WIRE_INTEGER'),
        'rng_overflow':('rng','18446744073709551616 0 0 0','WIRE_INTEGER_OVERFLOW'),'integer_bool':('step','False','WIRE_INTEGER'),'integer_float':('step','0.0','WIRE_INTEGER'),
        'metric_overflow':('current_metrics','18446744073709551615 0 0 0 0 0 0','STATE_METRIC_TYPES'),
        'metric_scalar':('current_metrics','0 0 0 0 0 0 1','STATE_METRIC_TYPES'),
        'metric_score':('current_metrics','0 0 0 4851 0 0 0','STATE_SCORES'),
        'histogram':('current_metrics','0 0 0 0 4851 0 0','STATE_SCORES'),
        'degree':('degree','2','DOMAIN_DECLARED'),'zero_count':('zero_archive','999999','STATE_ZERO_POPULATION')}
    for label in tqdm(NEGATIVE,desc='Ternary strict native corruptions'):
        tick(deadline);lines=base[:];diagnostic=None;kw=dict(steps=1,seed=99034002,temp=1000000,mix=64,expected=2)
        if label in mutations:
            tag,value,diagnostic=mutations[label]
            if tag=='MAGIC':lines[0]=value
            else:field(lines,tag,value)
        elif label in ['cache','cache_bool','cache_float']:
            at=next(i for i,x in enumerate(lines) if x.startswith('cn '));lines[at+1]=str(int(lines[at+1])+1) if label=='cache' else 'False' if label=='cache_bool' else '0.0';diagnostic='STATE_CN_CACHE' if label=='cache' else 'WIRE_INTEGER'
        elif label in ['triple_range','triple_duplicate']:
            at=next(i for i,x in enumerate(lines) if x.startswith('current '));lines[at+1]='99 1 2' if label=='triple_range' else lines[at+2];diagnostic='WIRE_RANGE' if label=='triple_range' else 'TRIPLE_LINEARITY'
        elif label in ['trailing','truncated']:lines=lines+['EXTRA'] if label=='trailing' else lines[:-1];diagnostic='WIRE_TRAILING' if label=='trailing' else 'WIRE_TRUNCATED'
        elif label.startswith('zero_') or label.startswith('initial_'):
            lines=zero[:];kw=dict(name='rook9',steps=1,temp=0,expected=2)
            if label=='zero_missing_current':
                at=next(i for i,x in enumerate(lines) if x.startswith('zero_archive '));lines=lines[:at]+['zero_archive 0','END'];diagnostic='STATE_ZERO_COMPLETENESS'
            elif label=='zero_missing_best':
                other=(out/'prism_initial_probes/final.state').read_text().splitlines()
                at=next(i for i,x in enumerate(lines) if x.startswith('current '));jt=next(i for i,x in enumerate(other) if x.startswith('current '));lines[at:at+7]=other[jt:jt+7]
                at=next(i for i,x in enumerate(lines) if x.startswith('cn '));jt=next(i for i,x in enumerate(other) if x.startswith('cn '));lines[at:at+37]=other[jt:jt+37]
                field(lines,'current_metrics',next(x.split(' ',1)[1] for x in other if x.startswith('current_metrics ')))
                field(lines,'step','1');field(lines,'rng_words','4')
                at=next(i for i,x in enumerate(lines) if x.startswith('zero_archive '));lines=lines[:at]+['zero_archive 0','END'];diagnostic='STATE_BEST_ZERO_COMPLETENESS'
            elif label=='zero_duplicate':
                at=next(i for i,x in enumerate(lines) if x.startswith('zero_step '));field(lines,'step','1');field(lines,'rng_words','4');field(lines,'zero_archive','2');lines=lines[:-1]+lines[at:-1]+['END'];diagnostic='STATE_ZERO_OBJECT'
            elif label=='zero_rng':field(lines,'zero_rng','0 0 0 0');diagnostic='RNG_ZERO'
            elif label=='zero_counter':field(lines,'zero_accepted','1');diagnostic='STATE_COUNTERS'
            elif label=='zero_triples':at=next(i for i,x in enumerate(lines) if x.startswith('zero_triples '));lines[at+1]=lines[at+2];diagnostic='TRIPLE_LINEARITY'
            elif label=='zero_initial_rng':field(lines,'zero_rng','1 2 3 4');diagnostic='STATE_ZERO_INITIAL_RESET'
            elif label=='zero_initial_words':field(lines,'zero_rng_words','1');diagnostic='STATE_ZERO_INITIAL_RESET'
            elif label=='initial_rng':field(lines,'rng','1 2 3 4');diagnostic='STATE_INITIAL_RESET'
            elif label=='initial_words':field(lines,'rng_words','1');diagnostic='STATE_INITIAL_RESET'
            elif label=='initial_best':at=next(i for i,x in enumerate(lines) if x.startswith('best '));parts=lines[at+1].split();lines[at+1]=' '.join(parts[::-1]);diagnostic='STATE_INITIAL_RESET'
        elif label.startswith('import_'):
            raw=target_input.read_text();diagnostic='GRAPH_SOURCE_IDENTITY';kw=dict(steps=0,temp=0,expected=2)
            if label=='import_magic':raw=raw.replace('TERNARY_LINEAR_GRAPH_INPUT_V1','WRONG',1);diagnostic='WIRE_FIELD:TERNARY_LINEAR_GRAPH_INPUT_V1'
            elif label=='import_domain':raw=raw.replace('degree 7','degree 2',1);diagnostic='DOMAIN_DECLARED'
            elif label=='import_hash':raw=raw.replace(target_sha,'1'*64,1)
            elif label=='import_duplicate':items=raw.splitlines();at=items.index('triples 231');items[at+1]=items[at+2];raw='\n'.join(items)+'\n';diagnostic='TRIPLE_LINEARITY'
            elif label=='import_trailing':raw+='EXTRA\n';diagnostic='WIRE_TRAILING'
            elif label=='import_integer_bool':raw=raw.replace('n 99','n True',1);diagnostic='WIRE_INTEGER'
            path=out/('corrupt_'+label+'.txt');text(path,raw);pin(path,None,pins,deadline)
            opts=['--graph-input',str(path),'--source-graph-sha256',target_sha,'--seed','99034001','--steps','0','--mix-steps','0','--schedule-steps','2048','--temperature-start','0','--temperature-end','0']
            row=native(args,out,'reject_'+label,opts,pins,deadline,2,diagnostic);runs.append(row);continue
        elif label.startswith('arg_') or label=='probe_scope':
            opts=['--fixture','target99','--seed','1','--steps','0','--mix-steps','0','--schedule-steps','1','--temperature-start','0','--temperature-end','0']
            if label=='arg_duplicate':opts+=['--seed','2'];diagnostic='ARG_DUPLICATE'
            elif label=='arg_unknown':opts+=['--wrong','1'];diagnostic='ARG_UNKNOWN'
            elif label=='arg_missing':at=opts.index('--seed');del opts[at:at+2];diagnostic='ARG_REQUIRED:--seed'
            elif label=='arg_conflict':opts+=['--resume','unused','--source-graph-sha256','0'*64];diagnostic='ARG_INPUT_EXCLUSIVE'
            elif label=='arg_zero_interval':opts+=['--verify-every','0'];diagnostic='ARG_LIMITS'
            elif label=='arg_nonfinite':opts[opts.index('--temperature-start')+1]='nan';diagnostic='WIRE_REAL'
            elif label=='arg_negative':opts[opts.index('--steps')+1]='-1';diagnostic='WIRE_INTEGER'
            elif label=='arg_overflow':opts[opts.index('--steps')+1]='18446744073709551616';diagnostic='WIRE_INTEGER_OVERFLOW'
            elif label=='probe_scope':opts+=['--probe-all'];diagnostic='PROBE_SCOPE'
            row=native(args,out,'reject_'+label,opts,pins,deadline,2,diagnostic);runs.append(row);continue
        need(diagnostic is not None,'DECLARED_NEGATIVE:'+label);path=out/('corrupt_'+label+'.state');text(path,'\n'.join(lines)+'\n');pin(path,None,pins,deadline)
        call('reject_'+label,resumed=path,diagnostic=diagnostic,**kw)
    need([x['label'] for x in runs]==POSITIVE+['reject_'+x for x in NEGATIVE],'COMPLETE_FROZEN_POPULATION')
    coverage=dict(accepted_overlap=0,rejected_overlap=0,accepted_F3_up=0,accepted_F3_down=0,accepted_E_up=0,rejected_valid=0,invalid_selection=0,blocked_pairs=0,late_zero=0)
    margins=[];probe_count=0;attempted=0
    for row in runs[:len(POSITIVE)]:
        directory=out/row['label'];result=read(directory/'result.json')
        attempted+=result['proposals_this_invocation']
        need(result['stop_reason'] in ['REQUESTED_STEPS_COMPLETE','RAW_F3_ZERO_PENDING_INDEPENDENT_FULL_INTEGER_SRG_VALIDATOR'],'FINITE_REQUEST_COMPLETE')
        need(len((directory/'pair_costs.jsonl').read_bytes().splitlines())==596,'PAIR_COST_RECORD_POPULATION')
        if (directory/'probes.jsonl').exists():probe_count+=len((directory/'probes.jsonl').read_bytes().splitlines())
        for raw in (directory/'moves.jsonl').read_bytes().splitlines():
            event=json.loads(raw);valid=event['admissible'];accepted=event['accepted'];overlap=not event['disjoint']
            coverage['accepted_overlap']+=int(valid and accepted and overlap);coverage['rejected_overlap']+=int(valid and not accepted and overlap)
            coverage['accepted_F3_up']+=int(accepted and event['candidate']['F3']>event['before']['F3']);coverage['accepted_F3_down']+=int(accepted and event['candidate']['F3']<event['before']['F3'])
            coverage['accepted_E_up']+=int(accepted and event['candidate']['E']>event['before']['E']);coverage['rejected_valid']+=int(valid and not accepted)
            coverage['invalid_selection']+=int(not event['exclusive']);coverage['blocked_pairs']+=int(event['exclusive'] and not event['absent_after_removal'])
            if valid and not event['mixing'] and not row['label'].endswith('_forced') and event['delta_scalar']>0 and event['temperature']>0:
                u=(int(event['draw'])>>11)*2.0**-53;p=math.exp(-event['delta_scalar']/event['temperature']);margins.append(abs(u-p))
        selection=read(directory/'zero_selection.json');coverage['late_zero']+=int(selection['found'] and selection['first_step']>0)
    need(probe_count==522,'ALL_GENERIC_PROBES');need(attempted==8192,'COMPLETE_ORDINARY_FINITE_PROPOSALS');need(all(coverage.values()),'PREREGISTERED_ACTUAL_BRANCH_COVERAGE')
    need(margins and min(margins)>1e-12,'FINITE_ACCEPTANCE_MARGIN')
    manifest=dict(schema='TERNARY_MIXED_FINITE_CONTROLS_V1',timestamp=stamp(),source_commit=args.source_commit,inputs_sha256=dict(pins),runs=runs,
        positive_calls=len(POSITIVE),strict_negative_calls=len(NEGATIVE),native_calls=len(runs),whole_prefix_resume_equalities=len(splits),splits=splits,
        complete_generic_probe_records=probe_count,attempted_ordinary_proposals=attempted,coverage=coverage,minimum_floating_acceptance_margin=min(margins),
        actual_scientific_input_read=False,scientific_search_launched=False,target_resolution=False,independent_approval=False,
        scope='Finite generic rook9/prism9/cube12 and explicit unoptimized99 initializer only; no target certificate or trajectory/performance guarantee.',
        independent_requirement='Separate exact adjacency/CN/F3/E/scalar/residue/RNG/typed-state/proposal/acceptance/rollback/archive checker must consume every raw control and strict veto; no producer imports; new saved-object pre-output calibration required before scientific search.',
        all_raw_artifacts=artifacts(out))
    save(out/'controls_manifest.json',manifest);return dict(status='TERNARY_MIXED_CONTROLS_PRODUCED_PENDING_INDEPENDENT_CHECK',manifest=key(out/'controls_manifest.json'),manifest_sha256=digest(out/'controls_manifest.json'),native_calls=len(runs),coverage=coverage,independent_approval=False,target_resolution=False)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['build','controls'])
    p.add_argument('--seconds',type=float,required=True);p.add_argument('--allocation-reason',required=True);p.add_argument('--source-commit',required=True)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--supervision-out',type=Path,required=True)
    p.add_argument('--engineering-plan',type=Path,required=True);p.add_argument('--engineering-plan-sha256',required=True)
    p.add_argument('--compiler-seconds',type=float,required=True);p.add_argument('--native-seconds',type=float,required=True)
    for name in ['binary','build-manifest']:p.add_argument('--'+name,type=Path);p.add_argument('--'+name+'-sha256')
    p.add_argument('--address-space-bytes',type=int,required=True);p.add_argument('--file-bytes',type=int,required=True);args=p.parse_args()
    deadline=CommandDeadline(args.seconds,allocation_reason=args.allocation_reason);out=args.out.resolve()
    need(out.is_relative_to(ROOT) and not out.exists(),'FRESH_OUTPUT');out.mkdir(parents=True);pins={}
    try:
        for path in CODE:pin(path,None,pins,deadline)
        pin(args.engineering_plan,args.engineering_plan_sha256,pins,deadline);plan=read(args.engineering_plan)
        need(plan['schema']=='TERNARY_MIXED_ENGINEERING_PLAN_V1' and plan['objective']==OBJECTIVE and plan['move_kernel']==KERNEL and plan['distribution']==DISTRIBUTION,'ENGINEERING_PLAN')
        for path,identity in plan['source_inputs_sha256'].items():pin(ROOT/path,identity,pins,deadline)
        outer=contained(args,pins,deadline)
        save(out/'invocation.json',dict(timestamp=stamp(),command=[sys.executable,*sys.argv],cwd=str(ROOT),mode=args.mode,source_commit=args.source_commit,
            inputs_sha256=dict(pins),supervision=outer,python=platform.python_version(),tqdm_version=__import__('tqdm').__version__,address_space_bytes=args.address_space_bytes,file_bytes=args.file_bytes,
            scientific_search_launched=False,independent_approval=False,target_resolution=False))
        result=dict(build=build,controls=controls)[args.mode](args,out,pins,deadline);result.update(timestamp=stamp(),elapsed_seconds=deadline.status()['elapsed_seconds']);save(out/'summary.json',result);print(json.dumps(result),flush=True)
    except BaseException as error:
        save(out/'failure.json',dict(timestamp=stamp(),error=repr(error),deadline=deadline.status(),outputs_preserved=True,completed_run_receipts=sorted(key(x) for x in out.glob('*.receipt.json')),independent_approval=False,target_resolution=False));raise

if __name__=='__main__':main()
