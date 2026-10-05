"""Versioned contained root-focused build, finite controls and gated run wrapper.

Every output is producer evidence pending separate independent checking.
"""
import argparse
import hashlib
import json
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
CPP=ROOT/'acceleration/hypergraph_root_focused_anneal_20261003_v2.cpp'
SPEC=Path(__file__).with_name(Path(__file__).stem+'_spec.md')
OBJECTIVE='SRG_ROOT_LOCAL_PAIR_RESIDUAL_V1'
DISTRIBUTION='MUTABLE_LABELLED_LINES_REJECTION_BOUNDED_XOSHIRO256SS_V1'
COMPILER=Path('/usr/bin/g++')
COMPILER_SHA='1353e9bdd29a7295c7226bf6c63abccce056d8cac31f112e5cdbecc3f28c2769'
CODE=[Path(__file__),CPP,SPEC,ROOT/'acceleration/hypergraph_root_focused_anneal_20261003_v2_spec.md',
      ROOT/'docs/DESIGN_20261003_ROOT_FOCUSED_HYPERGRAPH_V1.md',ROOT/'acceleration/audit_20261003_root_focused_design_v1.md',
      ROOT/'acceleration/command_deadline.py',ROOT/'acceleration/run_compute_command.py',
      ROOT/'acceleration/native_budget_env_v1/pyproject.toml',ROOT/'acceleration/native_budget_env_v1/uv.lock']
POSITIVE_LABELS=['rook_positive','rook_forced','target_forced','target_greedy','target_anneal','target_cooling','target_mixed',
    'prism_initial','cube_initial','cube_forced','rook_probes','prism_probes',
    *[family+suffix for family in ['target','prism','import','rook'] for suffix in ['_whole','_prefix73','_resumed']],
    'import_rook_reset','import_target_reset']
NEGATIVE_LABELS=['objective','weight','kernel','distribution','root','seed','temperature','checkpoint','counter','local_counter',
    'score','lambda','mu','root_score','best_score','graph_identity','fixture_provenance',
    'version','cache','zero_rng','negative_rng','duplicate_current','frozen_literal','mutable_map',
    'first_flag','first_rng','first_counter','first_triple','best_local_rng','best_local_triple',
    'import_version','import_root','import_domain','import_hash','import_duplicate','import_trailing']


def need(ok,message):
    if not ok:raise ValueError(message)


def stamp():return datetime.now(timezone.utc).isoformat()
def key(path):return Path(path).resolve().relative_to(ROOT).as_posix()
def read(path):return json.loads(Path(path).read_bytes())


def save(path,value):
    with Path(path).open('x',encoding='utf8',newline='\n') as stream:
        json.dump(value,stream,indent=2)
        stream.write('\n')


def digest(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def tick(deadline,reserve=30):
    status=deadline.status()
    need(not status['stop_required'] and status['remaining_seconds']>reserve,'not completed within the allocated budget; preserve all checkpoints/attempted and unattempted controls')
    return status


def pin(path,identity,pins,deadline):
    tick(deadline)
    path=Path(path).resolve()
    need(path.is_relative_to(ROOT) and path.is_file(),'exact repository input')
    actual=digest(path)
    need(identity is None or actual==identity,'exact input hash '+key(path))
    need(key(path) not in pins or pins[key(path)]==actual,'consistent repeated pin')
    pins[key(path)]=actual
    return actual


def execute(argv,prefix,args,deadline,expected):
    tick(deadline)
    start=time.monotonic()
    error=None
    with Path(str(prefix)+'.stdout.log').open('xb') as stdout,Path(str(prefix)+'.stderr.log').open('xb') as stderr:
        process=subprocess.Popen(argv,cwd=ROOT,stdout=stdout,stderr=stderr)
        try:
            need(os.getpgid(process.pid)==os.getpgid(0),'child stays in enclosing Linux group')
            while process.poll() is None:
                tick(deadline)
                time.sleep(.05)
        except BaseException as caught:error=caught
        finally:
            if process.poll() is None:
                process.terminate()
                try:process.wait(timeout=5)
                except subprocess.TimeoutExpired:process.kill()
            code=process.wait(timeout=5)
    receipt=dict(timestamp=stamp(),command=argv,cwd=str(ROOT),actual_exit_code=code,expected_exit_code=expected,
        wall_seconds=time.monotonic()-start,child_pid=process.pid,process_group=os.getpgid(0),reaped=True,
        stdout=key(Path(str(prefix)+'.stdout.log')),stderr=key(Path(str(prefix)+'.stderr.log')),
        error=None if error is None else repr(error),independent_approval=False)
    for label in ['stdout','stderr']:receipt[label+'_sha256']=digest(ROOT/receipt[label])
    save(Path(str(prefix)+'.receipt.json'),receipt)
    if error is not None:raise error
    need(code==expected,'actual child outcome differs from declared control')
    return receipt


def supervision(args,pins,deadline):
    need(sys.platform.startswith('linux'),'supported supervision must execute inside Linux')
    manifest=args.supervision_out.resolve()/'manifest.json'
    m=read(manifest)
    pin(ROOT/'acceleration/run_compute_command.py',m['source_sha256'],pins,deadline)
    need(m['seconds']>=args.seconds+10 and not m['automatic_retry'] and not m['cumulative_across_commands'],'independent fixed outer allocation')
    group=os.getpgid(0)
    guard=[word.decode() for word in (Path('/proc')/str(group)/'cmdline').read_bytes().split(b'\0') if word]
    need(guard and Path(guard[0]).name=='timeout' and '--signal=KILL' in guard,'live supported Linux enclosing group')
    need(key(Path(__file__)) in m['command'] or str(Path(__file__).resolve()) in m['command'],'actual supervised wrapper command')
    return dict(path=key(manifest),sha256=digest(manifest),invocation_id=m['invocation_id'],outer_seconds=m['seconds'],group=group,guard_argv=guard)


def authenticate(args,pins,deadline):
    need(args.binary and args.binary_sha256 and args.build_manifest and args.build_manifest_sha256,'explicit new binary/build hashes')
    pin(args.binary,args.binary_sha256,pins,deadline)
    pin(args.build_manifest,args.build_manifest_sha256,pins,deadline)
    m=read(args.build_manifest)
    need(m['schema']=='ROOT_FOCUSED_NATIVE_BUILD_V1' and m['binary_sha256']==args.binary_sha256
         and m['source_cpp_sha256']==pins[key(CPP)] and m['compiler_sha256']==COMPILER_SHA,'new exact source/compiler/binary binding')
    for name,identity in m['inputs_sha256'].items():pin(ROOT/name,identity,pins,deadline)


def build(args,out,pins,deadline):
    need(digest(COMPILER)==COMPILER_SHA,'exact pinned compiler')
    version=subprocess.run([str(COMPILER),'--version'],capture_output=True,text=True,timeout=min(10,deadline.child_seconds(10,reserve_seconds=30)))
    need(version.returncode==0 and version.stdout.startswith('g++ (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0'),'compiler version')
    allowed=deadline.child_seconds(args.compiler_seconds,reserve_seconds=30)
    binary=out/'hypergraph_root_focused_anneal'
    command=['/usr/bin/timeout','--foreground','--signal=TERM','--kill-after=5s',f'{allowed:.6f}s',
             str(COMPILER),'-std=c++17','-O3','-Wall','-Wextra','-Werror',str(CPP),'-o',str(binary)]
    receipt=execute(command,out/'build',args,deadline,0)
    manifest=dict(schema='ROOT_FOCUSED_NATIVE_BUILD_V1',timestamp=stamp(),source_commit=args.source_commit,command=command,
        binary_path=key(binary),binary_sha256=digest(binary),source_cpp_sha256=pins[key(CPP)],compiler_path=str(COMPILER),
        compiler_sha256=COMPILER_SHA,compiler_version_stdout=version.stdout,inputs_sha256=pins,
        receipt=key(out/'build.receipt.json'),receipt_sha256=digest(out/'build.receipt.json'),independent_approval=False)
    save(out/'build_manifest.json',manifest)
    return dict(status='ROOT_FOCUSED_BUILD_COMPLETE_PENDING_INDEPENDENT_CHECK',binary=manifest['binary_path'],binary_sha256=manifest['binary_sha256'],
        build_manifest=key(out/'build_manifest.json'),build_manifest_sha256=digest(out/'build_manifest.json'),receipt=receipt)


def native(args,label,directory,options,out,deadline,expected=0):
    allowed=deadline.child_seconds(args.native_seconds,reserve_seconds=30)
    command=['/usr/bin/timeout','--foreground','--signal=TERM','--kill-after=5s',f'{allowed:.6f}s',
        '/usr/bin/prlimit',f'--as={args.address_space_bytes}:{args.address_space_bytes}',f'--fsize={args.file_bytes}:{args.file_bytes}',
        '--core=0:0',str(args.binary.resolve()),'--out',str(directory),'--seconds',f'{max(.001,allowed-5):.6f}',*options]
    receipt=execute(command,out/label,args,deadline,expected)
    artifacts={key(path):dict(sha256=digest(path),bytes=path.stat().st_size) for path in sorted(directory.iterdir()) if path.is_file()} if directory.exists() else {}
    return dict(label=label,options=options,receipt=key(out/(label+'.receipt.json')),receipt_sha256=digest(out/(label+'.receipt.json')),
        artifacts=artifacts,actual_exit_code=receipt['actual_exit_code'])


def fixture(name):
    if name=='rook9':return [[3*x,3*x+1,3*x+2] for x in range(3)]+[[x,x+3,x+6] for x in range(3)]
    if name=='prism9':return [[0,2,6],[0,1,7],[1,2,8],[3,5,6],[3,4,7],[4,5,8]]
    return [[x,x+33,x+66] for x in range(33)]+[[x,(x+1)%99,(x+4)%99] for x in range(99)]+[[x,(x+7)%99,(x+18)%99] for x in range(99)]


def graph_input(out,name,root,pins,deadline):
    n,d=(99,7) if name=='target99' else (9,2)
    rows=fixture(name)
    typed=out/(name+'_input_triples.json')
    save(typed,dict(n=n,degree=d,root=root,triples=rows,scope='Generic engineering fixture, not target graph certificate.'))
    adjacency=[[0]*n for _ in range(n)]
    for row in rows:
        for i in range(3):
            for j in range(i+1,3):adjacency[row[i]][row[j]]=adjacency[row[j]][row[i]]=1
    matrix=out/(name+'_input.adj')
    matrix.write_text(str(n)+'\n'+''.join(''.join(map(str,row))+'\n' for row in adjacency),encoding='ascii',newline='\n')
    selection=out/(name+'_input_selection.json')
    save(selection,dict(scope='Known explicit generic engineering input only',matrix_sha256=digest(matrix),triples_sha256=digest(typed),independent_approval=False))
    path=out/(name+'_graph_input.txt')
    text=f'ROOT_FOCUSED_GRAPH_INPUT_V1\nn {n}\ndegree {d}\nroot {root}\nsource_matrix_sha256 {digest(matrix)}\nsource_triples_sha256 {digest(typed)}\nselection_report_sha256 {digest(selection)}\ntriples {len(rows)}\n'+''.join(' '.join(map(str,row))+'\n' for row in rows)+'END\n'
    path.write_text(text,encoding='ascii',newline='\n')
    for item in [typed,matrix,selection,path]:pin(item,None,pins,deadline)
    return path


def controls(args,out,pins,deadline):
    authenticate(args,pins,deadline)
    runs=[]
    planned=[]
    save(out/'control_population.json',dict(schema='ROOT_FOCUSED_FROZEN_FINITE_POPULATION_V1',
        positive_labels=POSITIVE_LABELS,negative_labels=['reject_'+label for label in NEGATIVE_LABELS],
        native_calls=62,positive_calls=26,strict_negative_calls=36,success='Every declared call completes with its exact expected outcome and designated negative diagnostic; failed/unattempted cases preserved, never removed.'))
    rook_input=graph_input(out,'rook9',0,pins,deadline)
    target_input=graph_input(out,'target99',11,pins,deadline)
    probe_files={}
    for name in ['rook9','prism9']:
        m=len(fixture(name));rows=[(i,j,pi,pj) for i in range(m) for j in range(i+1,m) for pi in range(3) for pj in range(3)]
        path=out/(name+'_all_probes.txt')
        path.write_text('ROOT_FOCUSED_CONTROL_PROBES_V1\ncount '+str(len(rows))+'\n'+''.join(' '.join(map(str,row))+'\n' for row in rows)+'END\n',encoding='ascii',newline='\n')
        pin(path,None,pins,deadline)
        probe_files[name]=path
    def call(label,name='target99',root=11,steps=1024,seed=99033001,temp=16,end=None,mix=0,forced=False,resume=None,imported=None,probe=None,expected=0,diagnostic=None,extra=None):
        planned.append(dict(label=label,expected_exit_code=expected))
        opts=['--fixture',name,'--root',str(root),'--steps',str(steps),'--seed',str(seed),'--mix-steps',str(mix),'--schedule-steps','1024',
            '--temperature-start',str(temp),'--temperature-end',str(temp if end is None else end),
            '--verify-every','1','--checkpoint-every','64','--trace-max',str(steps),'--emit-pair-costs']
        if forced:opts.append('--forced')
        if resume:opts.extend(['--resume',str(resume)])
        if imported:
            opts.extend(['--frozen-reference' if resume else '--graph-input',str(imported),'--graph-identity',digest(imported)])
        if probe:opts.extend(['--probe-file',str(probe),'--probe-identity',digest(probe)])
        if extra:opts.extend(extra)
        row=native(args,label,out/label,opts,out,deadline,expected)
        if diagnostic is not None:
            need((out/(label+'.stderr.log')).read_bytes()==(diagnostic+'\n').encode('ascii') and (out/(label+'.stdout.log')).read_bytes()==b'','strict designated native veto '+label)
            row['expected_diagnostic']=diagnostic
        runs.append(row)
        save(out/'progress_'+str(len(runs))+'.json',dict(completed_calls=len(runs),last_label=label,mathematical_approval=False,deadline=deadline.status()))
        return row
    for label,kw in tqdm([
        ('rook_positive',dict(name='rook9',root=0,steps=0,temp=0)),('rook_forced',dict(name='rook9',root=0,forced=True,temp=0)),
        ('target_forced',dict(forced=True,temp=0)),('target_greedy',dict(temp=0)),('target_anneal',dict(temp=16)),
        ('target_cooling',dict(temp=48,end=.2)),('target_mixed',dict(temp=24,mix=256)),
        ('prism_initial',dict(name='prism9',root=8,steps=0,temp=0)),('cube_initial',dict(name='cube12_defect',root=11,steps=0,temp=0)),
        ('cube_forced',dict(name='cube12_defect',root=11,steps=512,forced=True,temp=0)),
        ('rook_probes',dict(name='rook9',root=0,steps=135,probe=probe_files['rook9'],temp=0)),
        ('prism_probes',dict(name='prism9',root=8,steps=135,probe=probe_files['prism9'],temp=0))],desc='Root-focused finite positive paths'):
        call(label,**kw)
    splits=[]
    for family,kw,steps in [('target',dict(seed=99033002,temp=16,mix=64),512),
        ('prism',dict(name='prism9',root=8,seed=181,temp=0),2048),
        ('import',dict(imported=target_input,seed=99033003,temp=24,end=.2,mix=64),512),
        ('rook',dict(name='rook9',root=0,seed=99033004,temp=16),256)]:
        call(family+'_whole',steps=steps,**kw)
        call(family+'_prefix73',steps=73,**kw)
        call(family+'_resumed',steps=steps-73,resume=out/(family+'_prefix73/final.state'),**kw)
        for member in ['final.state','current.adj','best_root.adj','moves.jsonl']:
            first=(out/(family+'_whole')/member).read_bytes()
            second=(out/(family+'_resumed')/member).read_bytes()
            if member=='moves.jsonl':second=(out/(family+'_prefix73')/member).read_bytes()+second
            need(first==second,'exact whole/split bytes '+family+'/'+member)
        for member in ['first_localzero.object','first_localzero.adj','best_localzero_mu.object','best_localzero_mu.adj']:
            a=out/(family+'_whole')/member;b=out/(family+'_resumed')/member
            need(a.exists()==b.exists() and (not a.exists() or a.read_bytes()==b.read_bytes()),'exact split retained population '+family+'/'+member)
        splits.append(dict(family=family,split_step=73,total_steps=steps,raw_objects_and_complete_trace_equal=True))
    need(read(out/'prism_initial/result.json')['current_lambda']>0 and read(out/'prism_whole/result.json')['first_retained_localzero_found'] is True,'frozen prism late localzero control must actually succeed within2048 proposals; failure preserves all earlier cases')
    call('import_rook_reset',name='rook9',root=0,steps=0,temp=0,imported=rook_input)
    call('import_target_reset',steps=0,temp=0,imported=target_input)
    base=(out/'target_prefix73/final.state').read_text().splitlines()
    scalar={
        'objective':('objective','wrong','state exact objective'),'weight':('lambda_weight','61','state exact objective'),
        'kernel':('move_kernel','wrong','state exact kernel/distribution'),'distribution':('distribution','wrong','state exact kernel/distribution'),
        'root':('root','12','state root'),'seed':('seed','1','state exact continuation config'),
        'temperature':('t_start','17','state exact continuation config'),'checkpoint':('checkpoint_every','65','state exact continuation config'),
        'counter':('accepted','999999','state counter consistency'),'local_counter':('local_updates','999999','state counter consistency'),
        'score':('root_energy','-1','state exact components/scores'),'lambda':('lambda_energy','-1','state exact components/scores'),
        'mu':('mu_energy','-1','state exact components/scores'),'root_score':('root_residual','-1','state exact components/scores'),
        'best_score':('best_root_energy','-1','state exact components/scores'),
        'graph_identity':('input_sha256','1'*64,'state graph identity'),
        'fixture_provenance':('source_matrix_sha256','1'*64,'fixture exact provenance')}
    negatives=[]
    for label,(tag,value,diagnostic) in tqdm(scalar.items(),desc='Root-focused scalar corruptions'):
        lines=base[:];i=next(i for i,row in enumerate(lines) if row.startswith(tag+' '));lines[i]=tag+' '+value
        path=out/('corrupt_'+label+'.state');path.write_text('\n'.join(lines)+'\n',encoding='ascii',newline='\n');pin(path,None,pins,deadline)
        call('reject_'+label,steps=1,seed=99033002,temp=16,mix=64,resume=path,expected=2,diagnostic=diagnostic)
        negatives.append(label)
    for label,diagnostic in [('version','state version'),('cache','state exact CN cache'),('zero_rng','state RNG nonzero'),
        ('negative_rng','strict unsigned argument'),('duplicate_current','linear pair multiplicity'),
        ('frozen_literal','state literal frozen/mutable identity'),('mutable_map','state literal frozen/mutable identity')]:
        lines=base[:]
        if label=='version':lines[0]='WRONG_STATE'
        elif label=='cache':i=next(i for i,row in enumerate(lines) if row.startswith('cn '));lines[i+1]=str(int(lines[i+1])+1)
        elif label in ['zero_rng','negative_rng']:i=next(i for i,row in enumerate(lines) if row.startswith('rng '));lines[i]='rng '+('0 0 0 0' if label=='zero_rng' else '-1 0 0 0')
        elif label=='duplicate_current':i=next(i for i,row in enumerate(lines) if row.startswith('current '));lines[i+2]=lines[i+1]
        elif label=='frozen_literal':i=next(i for i,row in enumerate(lines) if row.startswith('frozen '));parts=lines[i+1].split();parts[-1]=str((int(parts[-1])+1)%99);lines[i+1]=' '.join(parts)
        elif label=='mutable_map':i=next(i for i,row in enumerate(lines) if row.startswith('mutable '));parts=lines[i].split();parts[2]=parts[3];lines[i]=' '.join(parts)
        path=out/('corrupt_'+label+'.state');path.write_text('\n'.join(lines)+'\n',encoding='ascii',newline='\n');pin(path,None,pins,deadline)
        call('reject_'+label,steps=1,seed=99033002,temp=16,mix=64,resume=path,expected=2,diagnostic=diagnostic);negatives.append(label)
    zero=(out/'rook_positive/final.state').read_text().splitlines()
    for label,diagnostic in [('first_flag','snapshot flag first_localzero'),('first_rng','first_localzero RNG nonzero'),
        ('first_counter','snapshot counter consistency'),('first_triple','linear pair multiplicity'),
        ('best_local_rng','best_localzero_mu RNG nonzero'),('best_local_triple','linear pair multiplicity')]:
        lines=zero[:]
        if label=='first_flag':i=lines.index('first_localzero_found 1');lines[i]='first_localzero_found 2'
        elif label in ['first_rng','best_local_rng']:tag='first_localzero_rng' if label=='first_rng' else 'best_localzero_mu_rng';i=next(i for i,row in enumerate(lines) if row.startswith(tag+' '));lines[i]=tag+' 0 0 0 0'
        elif label=='first_counter':i=lines.index('first_localzero_step 0');lines[i]='first_localzero_step 1'
        else:tag='first_localzero_triples' if label=='first_triple' else 'best_localzero_mu_triples';i=next(i for i,row in enumerate(lines) if row.startswith(tag+' '));lines[i+2]=lines[i+1]
        path=out/('corrupt_'+label+'.state');path.write_text('\n'.join(lines)+'\n',encoding='ascii',newline='\n');pin(path,None,pins,deadline)
        call('reject_'+label,name='rook9',root=0,steps=1,temp=0,resume=path,expected=2,diagnostic=diagnostic);negatives.append(label)
    for label,diagnostic in [('import_version','graph input version'),('import_root','graph input root'),
        ('import_domain','declared target or generic domain'),('import_hash','graph input provenance'),
        ('import_duplicate','linear pair multiplicity'),('import_trailing','graph input exact end')]:
        text=target_input.read_text()
        if label=='import_version':text=text.replace('ROOT_FOCUSED_GRAPH_INPUT_V1','WRONG_GRAPH',1)
        elif label=='import_root':text=text.replace('root 11\n','root 12\n',1)
        elif label=='import_domain':text=text.replace('n 99\n','n 100\n',1)
        elif label=='import_hash':text=text.replace('source_matrix_sha256 ','source_matrix_sha256 X',1)
        elif label=='import_duplicate':lines=text.splitlines();i=lines.index('triples 231');lines[i+2]=lines[i+1];text='\n'.join(lines)+'\n'
        else:text+='EXTRA\n'
        path=out/('corrupt_'+label+'.txt');path.write_text(text,encoding='ascii',newline='\n');pin(path,None,pins,deadline)
        call('reject_'+label,steps=0,temp=0,imported=path,expected=2,diagnostic=diagnostic);negatives.append(label)
    all_artifacts={key(path):dict(sha256=digest(path),bytes=path.stat().st_size) for path in sorted(out.rglob('*')) if path.is_file()}
    need([row['label'] for row in runs]==POSITIVE_LABELS+['reject_'+label for label in NEGATIVE_LABELS], 'exact frozen62-call population/order')
    coverage=dict(ordinary_accepted_overlap=0,ordinary_rejected_valid_overlap=0,probe_frozen_vetoes=0,probe_valid_rollbacks=0)
    for row in runs:
        if row['actual_exit_code']!=0:continue
        trace=out/row['label']/'moves.jsonl'
        for line in trace.read_bytes().splitlines():
            event=json.loads(line)
            if event['probe']:
                coverage['probe_frozen_vetoes']+=int(event['frozen_line_selected'])
                coverage['probe_valid_rollbacks']+=int(event['admissible'])
            elif event['admissible'] and not event['disjoint']:
                coverage['ordinary_accepted_overlap' if event['accepted'] else 'ordinary_rejected_valid_overlap']+=1
    need(all(coverage.values()),'all preregistered accepted/rejected overlap and frozen/probe rollback controls actually exercised')
    manifest=dict(schema='ROOT_FOCUSED_ENGINE_CONTROLS_V1',timestamp=stamp(),source_commit=args.source_commit,inputs_sha256=pins,
        native_calls=len(runs),positive_calls=sum(row['actual_exit_code']==0 for row in runs),strict_negative_calls=len(negatives),
        runs=runs,all_raw_artifacts=all_artifacts,split_records=splits,coverage=coverage,probe_population=dict(rook9=135,prism9=135,root_line_exclusion_complete=True),
        fixture_scope='Generic rook9/prism9/cube12 plus99 linear pointdegree7 fixture; finite engineering only, no optimized target result.',
        objective=OBJECTIVE,distribution=DISTRIBUTION,independent_approval=False,target_resolution=False,
        independent_requirement='A separately authored adjacency/dense scorer replays every actual finite proposal/RNG/rollback/root/frozen literal/input/reset/retention/cache and strict diagnostics; no producer imports. Saved-object checker needs a separate pre-output calibration.')
    save(out/'controls_manifest.json',manifest)
    return dict(status='ROOT_FOCUSED_CONTROLS_PRODUCED_PENDING_INDEPENDENT_CHECK',manifest=key(out/'controls_manifest.json'),manifest_sha256=digest(out/'controls_manifest.json'),native_calls=len(runs),positive_calls=manifest['positive_calls'],strict_negative_calls=len(negatives))


def run(args,out,pins,deadline):
    authenticate(args,pins,deadline)
    for label,path,wanted,status in [
        ('controls',args.controls_gate,args.controls_gate_sha256,'INDEPENDENT_ROOT_FOCUSED_ENGINE_V1_CONTROLS_PASS'),
        ('saved_objects',args.saved_gate,args.saved_gate_sha256,'INDEPENDENT_ROOT_FOCUSED_SAVED_OBJECTS_V1_CALIBRATION_PASS'),
        ('input',args.graph_gate,args.graph_gate_sha256,'INDEPENDENT_ROOT_FOCUSED_GRAPH_INPUT_V1_PASS')]:
        need(path is not None and wanted is not None,'required independent '+label+' gate')
        pin(path,wanted,pins,deadline)
        gate=read(path)
        need(gate['status']==status and gate['verifier'] in ['/root','/root/checkpoint_audit','/root/structural']
             and gate['method']=='independent_artifact_check','exact independent '+label+' gate scope/role')
        for name,identity in gate['inputs_sha256'].items():pin(ROOT/name,identity,pins,deadline)
        if label!='input':need(gate['inputs_sha256'][key(CPP)]==pins[key(CPP)] and gate['inputs_sha256'][key(Path(__file__))]==pins[key(Path(__file__))]
            and gate['inputs_sha256'][key(args.binary)]==args.binary_sha256,'gate exact changed source/build')
        else:need(args.graph_input is not None and gate['inputs_sha256'][key(args.graph_input)]==args.graph_input_sha256,'gate exact graph derivative')
        if label=='input':need(gate['verifier']=='/root','only separate ROOT may approve checkpoint-authored graph input')
    pin(args.graph_input,args.graph_input_sha256,pins,deadline)
    if args.resume:pin(args.resume,args.resume_sha256,pins,deadline)
    need(args.root==11 and args.steps>0,'frozen declared target root/steps')
    options=['--root','11','--seed',str(args.seed),'--steps',str(args.steps),'--mix-steps',str(args.mix_steps),
        '--schedule-steps',str(args.schedule_steps),'--temperature-start',str(args.temperature_start),'--temperature-end',str(args.temperature_end),
        '--verify-every',str(args.verify_every),'--checkpoint-every',str(args.checkpoint_every),'--trace-max',str(args.trace_max),'--trace-stride',str(args.trace_stride),
        '--graph-identity',args.graph_input_sha256,'--frozen-reference' if args.resume else '--graph-input',str(args.graph_input.resolve())]
    if args.resume:options.extend(['--resume',str(args.resume.resolve())])
    protocol=dict(schema='ROOT_FOCUSED_RUN_PROTOCOL_V1',timestamp=stamp(),source_commit=args.source_commit,inputs_sha256=pins,options=options,
        objective=OBJECTIVE,distribution=DISTRIBUTION,selection_population='Current/bestF checkpoint objects, first retained localzero and immediate strictly mu-improving retained localzero snapshots; verify minimum only over actual retained objects, no complete trajectory/earliest claim.',
        target_resolution=False,independent_approval=False,restricted_move_space=True)
    save(out/'protocol.json',protocol)
    row=native(args,'research',out/'native',options,out,deadline)
    return dict(status='ROOT_FOCUSED_RUN_COMPLETE_PENDING_INDEPENDENT_CHECK',native_result=read(out/'native/result.json'),raw=row,inputs_sha256=pins,independent_approval=False,target_resolution=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=['build','controls','run'])
    parser.add_argument('--seconds',type=float,required=True)
    parser.add_argument('--allocation-reason',required=True)
    parser.add_argument('--source-commit',required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--supervision-out',type=Path,required=True)
    parser.add_argument('--engineering-plan',type=Path,required=True)
    parser.add_argument('--engineering-plan-sha256',required=True)
    parser.add_argument('--compiler-seconds',type=float,default=100)
    parser.add_argument('--native-seconds',type=float,required=True)
    for label in ['binary','build-manifest','controls-gate','saved-gate','graph-input','graph-gate','resume']:
        parser.add_argument('--'+label,type=Path)
        parser.add_argument('--'+label+'-sha256')
    parser.add_argument('--address-space-bytes',type=int,default=2*1024**3)
    parser.add_argument('--file-bytes',type=int,default=1024**3)
    parser.add_argument('--root',type=int,default=11)
    parser.add_argument('--seed',type=int,default=99033001)
    parser.add_argument('--steps',type=int,default=100000000)
    parser.add_argument('--mix-steps',type=int,default=0)
    parser.add_argument('--schedule-steps',type=int,default=80000000)
    parser.add_argument('--temperature-start',type=float,default=20)
    parser.add_argument('--temperature-end',type=float,default=.1)
    parser.add_argument('--verify-every',type=int,default=100000)
    parser.add_argument('--checkpoint-every',type=int,default=1000000)
    parser.add_argument('--trace-max',type=int,default=2048)
    parser.add_argument('--trace-stride',type=int,default=100000)
    args=parser.parse_args()
    deadline=CommandDeadline(args.seconds,allocation_reason=args.allocation_reason)
    out=args.out.resolve()
    need(out.is_relative_to(ROOT) and not out.exists(),'fresh output in existing repository')
    out.mkdir(parents=True)
    pins={key(path):digest(path) for path in CODE}
    try:
        pin(args.engineering_plan,args.engineering_plan_sha256,pins,deadline)
        plan=read(args.engineering_plan)
        need(plan['schema']=='ROOT_FOCUSED_ENGINEERING_PLAN_V1' and plan['objective']==OBJECTIVE,'frozen exact engineering plan')
        for name,identity in plan['source_inputs_sha256'].items():pin(ROOT/name,identity,pins,deadline)
        outer=supervision(args,pins,deadline)
        save(out/'invocation.json',dict(timestamp=stamp(),mode=args.mode,command=[sys.executable,*sys.argv],cwd=str(ROOT),source_commit=args.source_commit,
            inputs_sha256=pins,supervision=outer,python=platform.python_version(),tqdm_version=__import__('tqdm').__version__,address_space_bytes=args.address_space_bytes,file_bytes=args.file_bytes,
            independent_approval=False,target_resolution=False))
        result=dict(build=build,controls=controls,run=run)[args.mode](args,out,pins,deadline)
        result.update(timestamp=stamp(),elapsed_seconds=deadline.status()['elapsed_seconds'])
        save(out/'summary.json',result)
        print(json.dumps(result),flush=True)
    except BaseException as error:
        save(out/'failure.json',dict(timestamp=stamp(),error=repr(error),deadline=deadline.status(),outputs_preserved=True,independent_approval=False,target_resolution=False))
        raise


if __name__=='__main__':main()
