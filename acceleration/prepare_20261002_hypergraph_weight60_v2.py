"""New fixed-weight60 hypergraph engine build/full controls and exact-source gate.

Producer output only. Independent weighted scorer/RNG/import controls must own
approval; unchanged unweighted gates do not approve these new source bytes.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, os, platform, shutil, subprocess, sys, time
from command_deadline import CommandDeadline
from run_compute_command import review_evidence

ROOT = Path(__file__).resolve().parents[1]
CPP = ROOT/'acceleration/hypergraph_weight60_anneal_20261002_v2.cpp'
DESIGN=ROOT/'acceleration/design_20261002_hypergraph_weight60_v2.md'
OBJECTIVE='SRG_LAMBDA_WEIGHTED_PAIR_RESIDUAL_V2'
IMPORT='acceleration/results/20261002_hypergraph_weighted_controls01/target99_warming/final.state'
IMPORT_SHA='fa54362fc5822d36e7107cbab35398a2e223cdc378593598153205bb77595cf2'
WEIGHT6_GATE='acceleration/results/20261002_independent_review/hypergraph_weighted_controls01/summary.json'
WEIGHT6_GATE_SHA='464a90e4093194ac59c4bdba3c19da661f7eabde52806307b37dbd33a7249f57'
PILOT='acceleration/results/20261002_hypergraph_weighted_pilot02/native/final.state'
PILOT_SHA='f4df0eadf3e7c4199c0715ed6c647ea995e41ffe8f972f91889b3a62a10879ad'
PILOT_GATE='acceleration/results/20261002_independent_review/hypergraph_weighted_pilot02/summary.json'
PILOT_GATE_SHA='6e84a14ccd230801ce9efacdddf99bf90876933ff53997898b367e73c91156f0'
ROOK_IMPORT='acceleration/results/20261002_hypergraph_weighted_controls01/rook9_positive/final.state'
ROOK_IMPORT_SHA='6e0c7116a1f81ba83ff543a1ce27b8f067aee7d6d67f41d762b8bd99a9bb0e77'
SPEC = Path(__file__).with_name(Path(__file__).stem+'_spec.md')
PLAN = ROOT/'acceleration/plan_20261002_hypergraph_weight60_engineering_v2.json'
CORRECTION = ROOT/'acceleration/plan_20261002_hypergraph_weight60_correction_v2.json'
DIAGNOSIS = ROOT/'acceleration/results/20261002_weight60_fixture_diagnosis03/summary.json'
DIAGNOSIS_SHA='d292c6ab61f3a7d61276b0d335035a681e4e4e371d260b725d1c6c959ffefeaf'
COMPILER = Path('/usr/bin/g++')
COMPILER_SHA = '1353e9bdd29a7295c7226bf6c63abccce056d8cac31f112e5cdbecc3f28c2769'
CODE = [Path(__file__), CPP, SPEC, DESIGN, PLAN, CORRECTION, ROOT/'acceleration/command_deadline.py',
        ROOT/'acceleration/run_compute_command.py', ROOT/'acceleration/native_budget_env_v1/pyproject.toml',
        ROOT/'acceleration/native_budget_env_v1/uv.lock']


def need(value, message):
    if not value:
        raise ValueError(message)


def stamp():
    return datetime.now(timezone.utc).isoformat()


def key(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def read(path):
    return json.loads(Path(path).read_bytes())


def save(path, value):
    with Path(path).open('x', encoding='utf8', newline='\n') as f:
        json.dump(value, f, indent=2)
        f.write('\n')


def tick(deadline, reserve=20):
    status = deadline.status()
    need(not status['stop_required'] and status['remaining_seconds'] > reserve,
         'not completed within the allocated budget; preserve exact checkpoints')
    return status


def sha(path, deadline):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(8*1024**2), b''):
            tick(deadline)
            h.update(b)
    return h.hexdigest()


def pin(path, digest, pins, deadline):
    path = Path(path).resolve()
    need(path.is_relative_to(ROOT) and path.is_file(), 'repository input')
    actual = sha(path, deadline)
    need(actual == digest and (key(path) not in pins or pins[key(path)] == digest), 'exact input identity')
    pins[key(path)] = digest


def supervision(args, pins, deadline):
    need(sys.platform.startswith('linux'), 'supervisor and compiler/native worker must execute inside Linux')
    manifest = args.supervision_out.resolve()/'manifest.json'
    m = read(manifest)
    pin(ROOT/'acceleration/run_compute_command.py', m['source_sha256'], pins, deadline)
    need(m['seconds'] >= args.seconds+10 and not m['automatic_retry'] and not m['cumulative_across_commands'], 'outer fixed command budget')
    group = os.getpgid(0)
    guard = [x.decode() for x in (Path('/proc')/str(group)/'cmdline').read_bytes().split(b'\0') if x]
    need(guard and Path(guard[0]).name == 'timeout' and '--signal=KILL' in guard, 'live Linux enclosing process-group guard')
    need(str(Path(__file__).resolve()) in m['command'] or key(Path(__file__)) in m['command'], 'actual supervised wrapper')
    return dict(path=key(manifest), sha256=sha(manifest, deadline), invocation_id=m['invocation_id'],
                outer_seconds=m['seconds'], producer_seconds=args.seconds, group=group, guard_argv=guard)


def execute(argv, prefix, args, deadline, expected, outer):
    start = time.monotonic()
    last_review = None
    with Path(str(prefix)+'.stdout.log').open('xb') as stdout, Path(str(prefix)+'.stderr.log').open('xb') as stderr:
        process = subprocess.Popen(argv, cwd=ROOT, stdout=stdout, stderr=stderr)
        try:
            need(os.getpgid(process.pid) == os.getpgid(0), 'child remains in enclosing group')
            while process.poll() is None:
                if args.review_json and args.review_json.exists():
                    raw = args.review_json.read_bytes()
                    need(len(raw) <= 65536, 'bounded external review')
                    h = hashlib.sha256(raw).hexdigest()
                    if h != last_review:
                        item = json.loads(raw)
                        item['observed_at_elapsed_seconds'] = item['observed_at_producer_elapsed_seconds']
                        reviewed = review_evidence(item, outer['invocation_id'], deadline.status()['elapsed_seconds'])
                        need(reviewed['decision'] == 'continue', 'external review requested stop/change')
                        deadline.review(evidence=json.dumps(reviewed, sort_keys=True))
                        last_review = h
                tick(deadline)
                time.sleep(.05)
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
            code = process.wait(timeout=5)
    receipt = dict(timestamp=stamp(), command=argv, cwd=str(ROOT), actual_exit_code=code,
        expected_exit_code=expected, reaped=True, wall_seconds=time.monotonic()-start,
        child_pid=process.pid, process_group=os.getpgid(0),
        stdout=key(Path(str(prefix)+'.stdout.log')), stderr=key(Path(str(prefix)+'.stderr.log')),
        independent_approval=False)
    for field in ['stdout', 'stderr']:
        receipt[field+'_sha256'] = sha(ROOT/receipt[field], deadline)
    save(Path(str(prefix)+'.receipt.json'), receipt)
    need(code == expected, 'actual child outcome differs from declared control')
    return receipt


def authenticate(args, pins, deadline):
    need(args.binary and args.binary_sha256 and args.build_manifest and args.build_manifest_sha256, 'explicit binary/build pins')
    pin(args.binary, args.binary_sha256, pins, deadline)
    pin(args.build_manifest, args.build_manifest_sha256, pins, deadline)
    build = read(args.build_manifest)
    need(build['schema'] == 'HYPERGRAPH_WEIGHT60_ANNEAL_NATIVE_BUILD_V2' and build['binary_sha256'] == args.binary_sha256
         and build['source_cpp_sha256'] == pins[key(CPP)] and build['compiler_sha256'] == COMPILER_SHA,
         'exact new source/compiler/binary binding')


def build(args, out, pins, deadline, outer):
    need(sha(COMPILER, deadline) == COMPILER_SHA, 'pinned observed compiler')
    version = subprocess.run([str(COMPILER), '--version'], capture_output=True, text=True, timeout=10)
    need(version.returncode == 0 and version.stdout.startswith('g++ (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0'), 'pinned compiler version')
    binary = out/'hypergraph_weight60_anneal'
    command = [str(COMPILER), '-std=c++17', '-O3', '-Wall', '-Wextra', '-Werror', str(CPP), '-o', str(binary)]
    receipt = execute(command, out/'build', args, deadline, 0, outer)
    m = dict(schema='HYPERGRAPH_WEIGHT60_ANNEAL_NATIVE_BUILD_V2', timestamp=stamp(), source_commit=args.source_commit,
        command=command, binary_path=key(binary), binary_sha256=sha(binary, deadline),
        source_cpp_sha256=pins[key(CPP)], inputs_sha256=pins, compiler_path=str(COMPILER),
        compiler_sha256=COMPILER_SHA, compiler_version_stdout=version.stdout,
        receipt=key(out/'build.receipt.json'), receipt_sha256=sha(out/'build.receipt.json', deadline),
        independent_approval=False, mathematical_verification=False)
    save(out/'build_manifest.json', m)
    return dict(status='HYPERGRAPH_WEIGHT60_BUILD_COMPLETE_PENDING_INDEPENDENT_CHECK', binary=m['binary_path'],
                binary_sha256=m['binary_sha256'], build_manifest=key(out/'build_manifest.json'),
                build_manifest_sha256=sha(out/'build_manifest.json', deadline), receipt=receipt)


def native(args, label, directory, options, out, deadline, outer, expected=0):
    allowed = deadline.child_seconds(args.native_seconds, reserve_seconds=30)
    cmd = ['/usr/bin/timeout', '--foreground', '--signal=TERM', '--kill-after=5s', f'{allowed:.6f}s',
           '/usr/bin/prlimit', f'--as={args.address_space_bytes}:{args.address_space_bytes}',
           f'--fsize={args.file_bytes}:{args.file_bytes}', '--core=0:0', str(args.binary.resolve()),
           '--out', str(directory), '--seconds', f'{max(.001,allowed-5):.6f}', *options]
    receipt = execute(cmd, out/label, args, deadline, expected, outer)
    artifacts = {key(p):dict(sha256=sha(p,deadline), bytes=p.stat().st_size)
                 for p in sorted(directory.iterdir()) if p.is_file()}
    return dict(label=label, options=options, receipt=key(out/(label+'.receipt.json')),
                receipt_sha256=sha(out/(label+'.receipt.json'),deadline), artifacts=artifacts,
                actual_exit_code=receipt['actual_exit_code'])


def controls(args, out, pins, deadline, outer):
    authenticate(args,pins,deadline)
    pin(ROOT/WEIGHT6_GATE,WEIGHT6_GATE_SHA,pins,deadline)
    oldgate=read(ROOT/WEIGHT6_GATE);need(oldgate['status']=='INDEPENDENT_HYPERGRAPH_WEIGHTED_ANNEAL_V1_CONTROLS_PASS','raw import source is independently checked')
    need(oldgate['inputs_sha256'][IMPORT]==IMPORT_SHA,'old gate binds raw import record only; does not approve weighted execution')
    pin(ROOT/IMPORT,IMPORT_SHA,pins,deadline)
    pin(ROOT/ROOK_IMPORT,ROOK_IMPORT_SHA,pins,deadline)
    need(oldgate['inputs_sha256'][ROOK_IMPORT]==ROOK_IMPORT_SHA,'weight6 gate binds rook import')
    pin(ROOT/PILOT_GATE,PILOT_GATE_SHA,pins,deadline);pin(ROOT/PILOT,PILOT_SHA,pins,deadline)
    pilotgate=read(ROOT/PILOT_GATE)
    need(pilotgate['status']=='INDEPENDENT_HYPERGRAPH_WEIGHTED_SAVED_OBJECTS_V2_PASS' and pilotgate['inputs_sha256'][PILOT]==PILOT_SHA,'independent pilot raw state binding only')
    pin(DIAGNOSIS,DIAGNOSIS_SHA,pins,deadline)
    runs=[]
    diagnostics={
        'lambda_weight':'checkpoint exact objective/weight','objective':'checkpoint exact objective/weight','version':'checkpoint version',
        'weighted_energy':'checkpoint exact weighted current/best scores','best_weighted_energy':'checkpoint exact weighted current/best scores',
        'lambda_energy':'checkpoint exact component/base scores','mu_energy':'checkpoint exact component/base scores','base_energy':'checkpoint exact component/base scores',
        'cn':'checkpoint exact CN cache','duplicate_triple':'linear hypergraph pair multiplicity','zero_rng':'nonzero RNG state','counter':'checkpoint counter consistency',
        'import_energy':'import weight6 exact weighted current/best scores','import_cn':'import weight6 exact CN cache','import_triple':'linear hypergraph pair multiplicity',
        'import_counter':'import weight6 counters','import_zero_rng':'import weight6 nonzero RNG','import_objective':'import weight6 exact objective/weight',
        'import_weight':'import weight6 exact objective/weight','import_lambda':'import weight6 exact component/base scores','import_base':'import weight6 exact component/base scores',
        'import_selector':'import weight6 graph selector','first_flag':'checkpoint first lambda0 flag','first_rng':'checkpoint first lambda0 nonzero RNG',
        'first_counter':'checkpoint first lambda0 counters','first_triple':'linear hypergraph pair multiplicity','missing_first':'checkpoint lambda0 selection completeness','kernel':'checkpoint exact move kernel'}
    def call(label, fixture='target99', steps=2048, seed=99032020, temp=16, end=None,mix=0, forced=False, resume=None, imported=None,select='current',expected=0):
        if end is None:end=temp
        opts=['--fixture',fixture,'--steps',str(steps),'--seed',str(seed),'--mix-steps',str(mix),
              '--temperature-start',str(temp),'--temperature-end',str(end),'--schedule-steps','1024',
              '--verify-every','1','--checkpoint-every','64','--checkpoint-seconds','15','--trace-max',str(steps),'--emit-pair-costs']
        if forced: opts.append('--forced')
        if resume: opts += ['--resume',str(resume)]
        if imported:opts+=['--import-weight6',str(imported),'--import-select',select]
        row=native(args,label,out/label,opts,out,deadline,outer,expected)
        if expected==2:
            stage=diagnostics[label.removeprefix('reject_')]
            need((out/(label+'.stderr.log')).read_bytes()==(stage+'\n').encode('ascii') and (out/(label+'.stdout.log')).read_bytes()==b'' and row['artifacts']=={},'exact designated malformed native rejection')
            row['expected_diagnostic']=stage
        runs.append(row)
        return row
    call('rook9_positive',fixture='rook9',steps=0,temp=0)
    call('rook9_forced',fixture='rook9',forced=True,temp=0)
    call('target99_forced',forced=True,temp=0)
    call('target99_greedy',temp=0)
    call('target99_anneal',temp=16)
    call('target99_cooling',temp=48,end=.2)
    call('target99_warming',temp=.2,end=48)
    call('target99_mixed',temp=24,mix=256)
    call('resume_whole',steps=256,seed=99032021,temp=16,mix=64)
    call('resume_first',steps=73,seed=99032021,temp=16,mix=64)
    state=out/'resume_first/final.state'
    call('resume_second',steps=183,seed=99032021,temp=16,mix=64,resume=state)
    need((out/'resume_whole/final.state').read_bytes() == (out/'resume_second/final.state').read_bytes(), 'exact split resume state byte identity')
    for which in ['current','best']:call('import_weight6_'+which,steps=2048,seed=99032060,temp=60,end=.1,mix=0,imported=ROOT/IMPORT,select=which)
    imported=out/'import_weight6_best/initial.state'
    call('import_resume_whole',steps=256,seed=99032022,temp=24,end=.2,mix=64,resume=imported)
    call('import_resume_first',steps=73,seed=99032022,temp=24,end=.2,mix=64,resume=imported)
    call('import_resume_second',steps=183,seed=99032022,temp=24,end=.2,mix=64,resume=out/'import_resume_first/final.state')
    need((out/'import_resume_whole/final.state').read_bytes()==(out/'import_resume_second/final.state').read_bytes(),'imported split resume raw byte identity')
    for family in ['resume','import_resume']:
        need((out/(family+'_whole/moves.jsonl')).read_bytes()==(out/(family+'_first/moves.jsonl')).read_bytes()+(out/(family+'_second/moves.jsonl')).read_bytes(),'complete split trace byte identity')
    call('rook_resume_whole',fixture='rook9',steps=256,seed=99032060,temp=60,mix=0)
    call('rook_resume_first',fixture='rook9',steps=73,seed=99032060,temp=60,mix=0)
    call('rook_resume_second',fixture='rook9',steps=183,resume=out/'rook_resume_first/final.state')
    for name in ['final.state','first_lambda0.state','first_lambda0.adj']:
        need((out/'rook_resume_whole'/name).read_bytes()==(out/'rook_resume_second'/name).read_bytes(),'lambda0 complete split object bytes')
    need((out/'rook_resume_whole/moves.jsonl').read_bytes()==(out/'rook_resume_first/moves.jsonl').read_bytes()+(out/'rook_resume_second/moves.jsonl').read_bytes(),'lambda0 complete split trace')
    call('import_weight6_rook',fixture='rook9',steps=0,seed=99032060,temp=60,end=.1,imported=ROOT/ROOK_IMPORT,select='best')
    call('import_weight6_pilot_best',steps=0,seed=99032060,temp=60,end=.1,imported=ROOT/PILOT,select='best')
    call('prism9_initial',fixture='prism9',steps=0,temp=0)
    call('prism9_whole',fixture='prism9',steps=256,seed=181,temp=0)
    call('prism9_first',fixture='prism9',steps=73,seed=181,temp=0)
    call('prism9_second',fixture='prism9',steps=183,resume=out/'prism9_first/final.state')
    need(read(out/'prism9_initial/result.json')['current_lambda_energy']>0 and not read(out/'prism9_initial/lambda0_selection.json')['found'],'prism control begins outside lambda0')
    selected=read(out/'prism9_whole/lambda0_selection.json')
    need(selected['found'] and selected['first_step']==1,'new exclusive overlap kernel known prism first-proposal capture')
    for name in ['final.state','first_lambda0.state','first_lambda0.adj']:
        need((out/'prism9_whole'/name).read_bytes()==(out/'prism9_second'/name).read_bytes(),'new overlap prism lambda0 complete split bytes')
    need((out/'prism9_whole/moves.jsonl').read_bytes()==(out/'prism9_first/moves.jsonl').read_bytes()+(out/'prism9_second/moves.jsonl').read_bytes(),'new overlap prism complete split trace')
    call('cube12_initial',fixture='cube12_defect',steps=0,seed=149,temp=0)
    call('cube12_whole',fixture='cube12_defect',steps=256,seed=149,temp=0)
    call('cube12_first',fixture='cube12_defect',steps=73,seed=149,temp=0)
    call('cube12_second',fixture='cube12_defect',steps=183,resume=out/'cube12_first/final.state')
    need(read(out/'cube12_initial/result.json')['current_lambda_energy']==6 and read(out/'cube12_initial/result.json')['current_mu_energy']==62 and not read(out/'cube12_initial/lambda0_selection.json')['found'],'cube12 exact initial nonzero components')
    selected=read(out/'cube12_whole/lambda0_selection.json')
    need(selected['found'] and selected['first_step']==1,'cube12 frozen known inverse first-proposal capture')
    first=(out/'cube12_whole/first_lambda0.state').read_text().splitlines()
    need('lambda_energy 0' in first and 'mu_energy 48' in first,'cube12 first lambda0 is partial non-SRG')
    for name in ['final.state','first_lambda0.state','first_lambda0.adj']:
        need((out/'cube12_whole'/name).read_bytes()==(out/'cube12_second'/name).read_bytes(),'post-proposal cube lambda0 complete split bytes')
    need((out/'cube12_whole/moves.jsonl').read_bytes()==(out/'cube12_first/moves.jsonl').read_bytes()+(out/'cube12_second/moves.jsonl').read_bytes(),'cube lambda0 complete split trace')
    original=state.read_text().splitlines()
    corruptions=[]
    for label in ['lambda_weight','weighted_energy','best_weighted_energy','lambda_energy','mu_energy','base_energy','cn','duplicate_triple','zero_rng','counter','objective','version','kernel']:
        lines=original[:]
        if label in ['lambda_weight','weighted_energy','best_weighted_energy','lambda_energy','mu_energy','base_energy']:
            i=next(i for i,x in enumerate(lines)if x.startswith(label+' ')); lines[i]=label+' '+str(int(lines[i].split()[1])+1)
        elif label == 'cn':
            i=next(i for i,x in enumerate(lines)if x.startswith('cn ')); lines[i+1]=str(int(lines[i+1])+1)
        elif label == 'duplicate_triple':
            i=next(i for i,x in enumerate(lines)if x.startswith('current ')); lines[i+2]=lines[i+1]
        elif label=='zero_rng':
            i=next(i for i,x in enumerate(lines)if x.startswith('rng ')); lines[i]='rng 0 0 0 0'
        elif label=='objective':lines[1]='objective SRG_LAMBDA_WEIGHTED_PAIR_RESIDUAL_V1'
        elif label=='version':lines[0]='HYPERGRAPH_WEIGHT60_ANNEAL_STATE_V1'
        elif label=='kernel':i=next(i for i,x in enumerate(lines)if x.startswith('move_kernel '));lines[i]='move_kernel DISJOINT_TRIPLE_SWAP_V1'
        else:
            i=next(i for i,x in enumerate(lines)if x.startswith('accepted '));lines[i]='accepted 74'
        p=out/(label+'_corrupt.state'); p.write_text('\n'.join(lines)+'\n',encoding='utf8')
        corruptions.append(dict(path=key(p),sha256=sha(p,deadline),type=label,expected_exit_code=2))
        call('reject_'+label,steps=1,resume=p,expected=2)
    import_lines=(ROOT/IMPORT).read_text().splitlines()
    for label in ['import_energy','import_cn','import_triple','import_counter','import_zero_rng','import_objective','import_weight','import_lambda','import_base']:
        lines=import_lines[:]
        if label=='import_energy':i=next(i for i,x in enumerate(lines)if x.startswith('weighted_energy '));lines[i]='weighted_energy 8878'
        elif label=='import_cn':i=next(i for i,x in enumerate(lines)if x.startswith('cn '));lines[i+1]=str(int(lines[i+1])+1)
        elif label=='import_triple':i=next(i for i,x in enumerate(lines)if x.startswith('current '));lines[i+2]=lines[i+1]
        elif label=='import_counter':i=next(i for i,x in enumerate(lines)if x.startswith('accepted '));lines[i]='accepted 2049'
        elif label=='import_zero_rng':i=next(i for i,x in enumerate(lines)if x.startswith('rng '));lines[i]='rng 0 0 0 0'
        elif label=='import_objective':lines[1]='objective SRG_LAMBDA_WEIGHTED_PAIR_RESIDUAL_V2'
        elif label=='import_weight':lines[2]='lambda_weight 60'
        elif label=='import_lambda':i=next(i for i,x in enumerate(lines)if x.startswith('lambda_energy '));lines[i]='lambda_energy 680'
        else:i=next(i for i,x in enumerate(lines)if x.startswith('base_energy '));lines[i]='base_energy 5483'
        p=out/(label+'_corrupt.state');p.write_text('\n'.join(lines)+'\n',encoding='utf8')
        corruptions.append(dict(path=key(p),sha256=sha(p,deadline),type=label,expected_exit_code=2))
        call('reject_'+label,steps=1,imported=p,select='best',expected=2)
    call('reject_import_selector',steps=1,imported=ROOT/IMPORT,select='wrong',expected=2)
    firstlines=(out/'rook_resume_first/final.state').read_text().splitlines()
    for label in ['first_flag','first_rng','first_counter','first_triple','missing_first']:
        lines=firstlines[:]
        if label=='first_flag':i=next(i for i,x in enumerate(lines)if x.startswith('first_lambda0 '));lines[i]='first_lambda0 2'
        elif label=='first_rng':i=next(i for i,x in enumerate(lines)if x.startswith('first_rng '));lines[i]='first_rng 0 0 0 0'
        elif label=='first_counter':i=next(i for i,x in enumerate(lines)if x.startswith('first_step '));lines[i]='first_step 74'
        elif label=='first_triple':i=next(i for i,x in enumerate(lines)if x.startswith('first_current '));lines[i+2]=lines[i+1]
        else:
            lines=(out/'rook9_positive/final.state').read_text().splitlines()
            i=next(i for i,x in enumerate(lines)if x.startswith('first_lambda0 '));lines=lines[:i]+['first_lambda0 0','END']
        p=out/(label+'_corrupt.state');p.write_text('\n'.join(lines)+'\n',encoding='utf8')
        corruptions.append(dict(path=key(p),sha256=sha(p,deadline),type=label,expected_exit_code=2))
        call('reject_'+label,steps=1,resume=p,expected=2)
    m=dict(schema='HYPERGRAPH_WEIGHT60_ANNEAL_CONTROLS_V2',timestamp=stamp(),source_commit=args.source_commit,
        inputs_sha256=pins,supervision=outer,objective=OBJECTIVE,lambda_weight=60,
        runs=runs,corruptions=corruptions,producer_resume_exact_byte_identity=True,
        producer_imported_resume_exact_byte_identity=True,producer_first_lambda0_resume_exact_byte_identity=True,
        producer_post_proposal_lambda0_resume_exact_byte_identity=True,prior_failed_version=dict(failure='acceleration/results/20261002_hypergraph_weight60_controls01/failure.json',sha256='a702e7a17e21a5c244cb888c6e6ca56083f8d673459f4209d14ac00fdb507135',scope='Original exact late-lambda0 prism expectation failed; preserved25positive calls and27unattempted negatives'),
        import_weight6_source=dict(path=IMPORT,sha256=IMPORT_SHA,raw_gate=WEIGHT6_GATE,raw_gate_sha256=WEIGHT6_GATE_SHA,
             selection=['current','best'],new_seed=99032060,counters_reset=True,new_config=dict(temperature_start=60,temperature_end=.1,mix_steps=0,schedule_steps=1024),old_base_scores=dict(current=5482,best=5590),old_weighted_scores=dict(current=8877,best=8815)),
        pilot_zero_step_import=dict(path=PILOT,sha256=PILOT_SHA,raw_gate=PILOT_GATE,raw_gate_sha256=PILOT_GATE_SHA,selected='best',expected_lambda=63,expected_mu=3423,expected_F60=7203),
        full_recomputation_frequency='Every proposal for engineering controls',
        independent_approval=False,target_resolution=False,
        independent_requirement='Separate adjacency-set scorer replays every raw control proposal, exact RNG, all component/weighted scores, CN cache, domain and weighted category-switch arithmetic; exact positive/corrupted/import controls and fresh/imported split resume; no producer import.',
        scope='Finite engineering controls, rook9 fixture and full99 linear3uniform pointdegree7 domain; not an exhaustive search or graph construction.')
    save(out/'controls_manifest.json',m)
    return dict(status='HYPERGRAPH_WEIGHT60_ENGINEERING_CONTROLS_PRODUCED_PENDING_INDEPENDENT_CHECK',
                manifest=key(out/'controls_manifest.json'),manifest_sha256=sha(out/'controls_manifest.json',deadline),
                native_calls=len(runs),scope=m['scope'])


def research(args,out,pins,deadline,outer):
    authenticate(args,pins,deadline)
    need(args.gate and args.gate_sha256,'new independent exact scorer/move controls gate required')
    pin(args.gate,args.gate_sha256,pins,deadline)
    gate=read(args.gate)
    need(gate['status'] == 'INDEPENDENT_HYPERGRAPH_WEIGHT60_ANNEAL_V2_CONTROLS_PASS', 'independent gate status')
    for p in [*CODE,args.binary,args.build_manifest]:
        need(gate['inputs_sha256'].get(key(p)) == pins[key(p)], 'independent gate binds exact source/binary/build')
    need(args.saved_gate and args.saved_gate_sha256,'independent changed-format saved-object checker calibration required')
    pin(args.saved_gate,args.saved_gate_sha256,pins,deadline)
    savedgate=read(args.saved_gate)
    need(savedgate['status']=='INDEPENDENT_HYPERGRAPH_WEIGHT60_SAVED_OBJECTS_V2_CALIBRATION_PASS','new independent saved-object calibration status')
    need(shutil.disk_usage(ROOT).free > 32*1024**3,'32GiB host free reserve')
    if args.resume:
        need(args.resume_sha256,'explicit resume state pin')
        pin(args.resume,args.resume_sha256,pins,deadline)
    if args.import_weight6:
        need(args.import_weight6_sha256 and args.import_select in ['current','best'] and not args.resume,'explicit exclusive import source/selector pins')
        pin(args.import_weight6,args.import_weight6_sha256,pins,deadline)
        need(key(args.import_weight6)==PILOT and args.import_weight6_sha256==PILOT_SHA,'frozen science import population is exact approved pilot02 state')
        pin(ROOT/PILOT_GATE,PILOT_GATE_SHA,pins,deadline)
    opts=['--fixture','target99','--steps',str(args.steps),'--seed',str(args.seed),
          '--mix-steps',str(args.mix_steps),'--temperature-start',str(args.temperature_start),
          '--temperature-end',str(args.temperature_end),'--schedule-steps',str(args.schedule_steps),
          '--verify-every','100000','--checkpoint-every','1000000','--checkpoint-seconds','15',
          '--trace-max','2048','--trace-stride','100000','--stop-at-zero']
    if args.resume: opts += ['--resume',str(args.resume.resolve())]
    if args.import_weight6:opts+=['--import-weight6',str(args.import_weight6.resolve()),'--import-select',args.import_select]
    save(out/'protocol.json',dict(timestamp=stamp(),source_commit=args.source_commit,inputs_sha256=pins,
        supervision=outer,selection='Exactly one declared seed or exact saved state; no required automorphism, triangle core, or Hadamard support.',
        objective=OBJECTIVE,lambda_weight=60,domain='99points;231linear triples;eachpointdegree7;14regular point graph',
        options=opts,numerical_acceptance='Integer F60=60E_lambda+E_mu and components only; temperature/acceptance heuristic.',
        success='Raw F60=0 state becomes a candidate only after full independent99x99 SRG validation. First E_lambda0 gets a separate immutable exact current-graph/RNG/counter snapshot even if not best F60; lambda0 alone is not SRG.',
        falsification='Cache/domain mismatch, corrupt checkpoint or independent validator veto prevents promotion.',
        limitations=['No connected move-space or exhaustive coverage assertion.','Scores not comparable with fixed-core factor/Gram objectives.','Sparse scientific move trace is sampled; complete engineering traces have separate verification.'],
        target_resolution=False,independent_approval=False))
    row=native(args,'research',out/'native',opts,out,deadline,outer)
    return dict(status='HYPERGRAPH_WEIGHT60_RESEARCH_OUTPUT_PENDING_INDEPENDENT_SAVED_STATE_CHECK',
                run=row,inputs_sha256=pins,target_resolution=False,independent_approval=False)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('mode',choices=['build','controls','research'])
    ap.add_argument('--seconds',type=float,required=True)
    ap.add_argument('--allocation-reason',required=True)
    ap.add_argument('--source-commit',required=True)
    ap.add_argument('--supervision-out',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    for name in ['binary','build-manifest','gate','saved-gate','resume','import-weight6']:
        ap.add_argument('--'+name,type=Path)
        ap.add_argument('--'+name+'-sha256')
    ap.add_argument('--import-select',choices=['current','best'],default='current')
    ap.add_argument('--native-seconds',type=float,required=True)
    ap.add_argument('--address-space-bytes',type=int,default=2*1024**3)
    ap.add_argument('--file-bytes',type=int,default=1024**3)
    ap.add_argument('--review-json',type=Path)
    ap.add_argument('--steps',type=int,default=100000000)
    ap.add_argument('--seed',type=int,default=99032060)
    ap.add_argument('--mix-steps',type=int,default=0)
    ap.add_argument('--schedule-steps',type=int,default=80000000)
    ap.add_argument('--temperature-start',type=float,default=60)
    ap.add_argument('--temperature-end',type=float,default=.1)
    args=ap.parse_args()
    deadline=CommandDeadline(args.seconds,allocation_reason=args.allocation_reason)
    out=args.out.resolve();need(out.is_relative_to(ROOT),'existing repository output')
    out.mkdir(parents=True,exist_ok=False)
    pins={key(p):sha(p,deadline) for p in CODE}
    outer=supervision(args,pins,deadline)
    save(out/'invocation.json',dict(timestamp=stamp(),mode=args.mode,command=[sys.executable,*sys.argv],
         cwd=str(ROOT),source_commit=args.source_commit,inputs_sha256=pins,supervision=outer,
         python=platform.python_version(),tqdm_version=__import__('tqdm').__version__,
         address_space_bytes=args.address_space_bytes,file_bytes=args.file_bytes,
         independent_approval=False,target_resolution=False))
    try:
        result=dict(build=build,controls=controls,research=research)[args.mode](args,out,pins,deadline,outer)
        result.update(timestamp=stamp(),elapsed_seconds=deadline.status()['elapsed_seconds'])
        save(out/'summary.json',result);print(json.dumps(result),flush=True)
    except BaseException as error:
        save(out/'failure.json',dict(timestamp=stamp(),error=repr(error),deadline=deadline.status(),
             independent_approval=False,target_resolution=False,outputs_preserved=True))
        raise


if __name__ == '__main__':
    main()
