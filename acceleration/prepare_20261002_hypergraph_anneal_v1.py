"""Contained build, engineering controls and independently gated hypergraph runs."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, os, platform, shutil, subprocess, sys, time
from command_deadline import CommandDeadline
from run_compute_command import review_evidence

ROOT = Path(__file__).resolve().parents[1]
CPP = ROOT/'acceleration/hypergraph_anneal_20261002_v1.cpp'
SPEC = Path(__file__).with_name(Path(__file__).stem+'_spec.md')
COMPILER = Path('/usr/bin/g++')
COMPILER_SHA = '1353e9bdd29a7295c7226bf6c63abccce056d8cac31f112e5cdbecc3f28c2769'
CODE = [Path(__file__), CPP, SPEC, ROOT/'acceleration/command_deadline.py',
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
    need(build['schema'] == 'HYPERGRAPH_ANNEAL_NATIVE_BUILD_V1' and build['binary_sha256'] == args.binary_sha256
         and build['source_cpp_sha256'] == pins[key(CPP)] and build['compiler_sha256'] == COMPILER_SHA,
         'exact new source/compiler/binary binding')


def build(args, out, pins, deadline, outer):
    need(sha(COMPILER, deadline) == COMPILER_SHA, 'pinned observed compiler')
    version = subprocess.run([str(COMPILER), '--version'], capture_output=True, text=True, timeout=10)
    need(version.returncode == 0 and version.stdout.startswith('g++ (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0'), 'pinned compiler version')
    binary = out/'hypergraph_anneal'
    command = [str(COMPILER), '-std=c++17', '-O3', '-Wall', '-Wextra', '-Werror', str(CPP), '-o', str(binary)]
    receipt = execute(command, out/'build', args, deadline, 0, outer)
    m = dict(schema='HYPERGRAPH_ANNEAL_NATIVE_BUILD_V1', timestamp=stamp(), source_commit=args.source_commit,
        command=command, binary_path=key(binary), binary_sha256=sha(binary, deadline),
        source_cpp_sha256=pins[key(CPP)], inputs_sha256=pins, compiler_path=str(COMPILER),
        compiler_sha256=COMPILER_SHA, compiler_version_stdout=version.stdout,
        receipt=key(out/'build.receipt.json'), receipt_sha256=sha(out/'build.receipt.json', deadline),
        independent_approval=False, mathematical_verification=False)
    save(out/'build_manifest.json', m)
    return dict(status='HYPERGRAPH_BUILD_COMPLETE_PENDING_INDEPENDENT_CHECK', binary=m['binary_path'],
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
    runs=[]
    def call(label, fixture='target99', steps=2048, seed=99032000, temp=8, mix=0, forced=False, resume=None, expected=0):
        opts=['--fixture',fixture,'--steps',str(steps),'--seed',str(seed),'--mix-steps',str(mix),
              '--temperature-start',str(temp),'--temperature-end',str(temp),'--schedule-steps','1024',
              '--verify-every','1','--checkpoint-every','64','--checkpoint-seconds','15','--trace-max',str(steps)]
        if forced: opts.append('--forced')
        if resume: opts += ['--resume',str(resume)]
        row=native(args,label,out/label,opts,out,deadline,outer,expected)
        runs.append(row)
        return row
    call('rook9_positive',fixture='rook9',steps=0,temp=0)
    call('rook9_forced',fixture='rook9',forced=True,temp=0)
    call('target99_forced',forced=True,temp=0)
    call('target99_greedy',temp=0)
    call('target99_anneal',temp=8)
    call('target99_mixed',temp=12,mix=256)
    call('resume_whole',steps=256,seed=99032002,temp=8,mix=64)
    call('resume_first',steps=73,seed=99032002,temp=8,mix=64)
    state=out/'resume_first/final.state'
    call('resume_second',steps=183,seed=99032002,temp=8,mix=64,resume=state)
    need((out/'resume_whole/final.state').read_bytes() == (out/'resume_second/final.state').read_bytes(), 'exact split resume state byte identity')
    original=state.read_text().splitlines()
    corruptions=[]
    for label in ['energy','best_energy','cn','duplicate_triple','zero_rng']:
        lines=original[:]
        if label in ['energy','best_energy']:
            i=next(i for i,x in enumerate(lines)if x.startswith(label+' ')); lines[i]=label+' '+str(int(lines[i].split()[1])+1)
        elif label == 'cn':
            i=next(i for i,x in enumerate(lines)if x.startswith('cn ')); lines[i+1]=str(int(lines[i+1])+1)
        elif label == 'duplicate_triple':
            i=next(i for i,x in enumerate(lines)if x.startswith('current ')); lines[i+2]=lines[i+1]
        else:
            i=next(i for i,x in enumerate(lines)if x.startswith('rng ')); lines[i]='rng 0 0 0 0'
        p=out/(label+'_corrupt.state'); p.write_text('\n'.join(lines)+'\n',encoding='utf8')
        corruptions.append(dict(path=key(p),sha256=sha(p,deadline),type=label,expected_exit_code=2))
        call('reject_'+label,steps=1,resume=p,expected=2)
    m=dict(schema='HYPERGRAPH_ANNEAL_CONTROLS_V1',timestamp=stamp(),source_commit=args.source_commit,
        inputs_sha256=pins,supervision=outer,objective='SRG_SQUARED_PAIR_RESIDUAL_V1',
        runs=runs,corruptions=corruptions,producer_resume_exact_byte_identity=True,
        full_recomputation_frequency='Every proposal for engineering controls',
        independent_approval=False,target_resolution=False,
        independent_requirement='Separate adjacency-set scorer replays every raw control proposal, exact RNG, CN cache, domain and energy; positive and corrupted controls; exact split resume. No producer import.',
        scope='Finite engineering controls, rook9 fixture and full99 linear3uniform pointdegree7 domain; not an exhaustive search or graph construction.')
    save(out/'controls_manifest.json',m)
    return dict(status='HYPERGRAPH_ENGINEERING_CONTROLS_PRODUCED_PENDING_INDEPENDENT_CHECK',
                manifest=key(out/'controls_manifest.json'),manifest_sha256=sha(out/'controls_manifest.json',deadline),
                native_calls=len(runs),scope=m['scope'])


def research(args,out,pins,deadline,outer):
    authenticate(args,pins,deadline)
    need(args.gate and args.gate_sha256,'new independent exact scorer/move controls gate required')
    pin(args.gate,args.gate_sha256,pins,deadline)
    gate=read(args.gate)
    need(gate['status'] == 'INDEPENDENT_HYPERGRAPH_ANNEAL_V1_CONTROLS_PASS', 'independent gate status')
    for p in [*CODE,args.binary,args.build_manifest]:
        need(gate['inputs_sha256'].get(key(p)) == pins[key(p)], 'independent gate binds exact source/binary/build')
    need(shutil.disk_usage(ROOT).free > 32*1024**3,'32GiB host free reserve')
    if args.resume:
        need(args.resume_sha256,'explicit resume state pin')
        pin(args.resume,args.resume_sha256,pins,deadline)
    opts=['--fixture','target99','--steps',str(args.steps),'--seed',str(args.seed),
          '--mix-steps',str(args.mix_steps),'--temperature-start',str(args.temperature_start),
          '--temperature-end',str(args.temperature_end),'--schedule-steps',str(args.schedule_steps),
          '--verify-every','100000','--checkpoint-every','1000000','--checkpoint-seconds','15',
          '--trace-max','2048','--trace-stride','100000','--stop-at-zero']
    if args.resume: opts += ['--resume',str(args.resume.resolve())]
    save(out/'protocol.json',dict(timestamp=stamp(),source_commit=args.source_commit,inputs_sha256=pins,
        supervision=outer,selection='Exactly one declared seed or exact saved state; no required automorphism, triangle core, or Hadamard support.',
        objective='SRG_SQUARED_PAIR_RESIDUAL_V1',domain='99points;231linear triples;eachpointdegree7;14regular point graph',
        options=opts,numerical_acceptance='Integer E only; temperature/acceptance are heuristic.',
        success='Raw E0 state becomes a candidate only after full independent99x99 SRG validation.',
        falsification='Cache/domain mismatch, corrupt checkpoint or independent validator veto prevents promotion.',
        limitations=['No connected move-space or exhaustive coverage assertion.','Scores not comparable with fixed-core factor/Gram objectives.','Sparse scientific move trace is sampled; complete engineering traces have separate verification.'],
        target_resolution=False,independent_approval=False))
    row=native(args,'research',out/'native',opts,out,deadline,outer)
    return dict(status='HYPERGRAPH_RESEARCH_OUTPUT_PENDING_INDEPENDENT_SAVED_STATE_CHECK',
                run=row,inputs_sha256=pins,target_resolution=False,independent_approval=False)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('mode',choices=['build','controls','research'])
    ap.add_argument('--seconds',type=float,required=True)
    ap.add_argument('--allocation-reason',required=True)
    ap.add_argument('--source-commit',required=True)
    ap.add_argument('--supervision-out',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    for name in ['binary','build-manifest','gate','resume']:
        ap.add_argument('--'+name,type=Path)
        ap.add_argument('--'+name+'-sha256')
    ap.add_argument('--native-seconds',type=float,required=True)
    ap.add_argument('--address-space-bytes',type=int,default=2*1024**3)
    ap.add_argument('--file-bytes',type=int,default=1024**3)
    ap.add_argument('--review-json',type=Path)
    ap.add_argument('--steps',type=int,default=100000000)
    ap.add_argument('--seed',type=int,default=99032000)
    ap.add_argument('--mix-steps',type=int,default=10000)
    ap.add_argument('--schedule-steps',type=int,default=1000000)
    ap.add_argument('--temperature-start',type=float,default=20)
    ap.add_argument('--temperature-end',type=float,default=.5)
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
