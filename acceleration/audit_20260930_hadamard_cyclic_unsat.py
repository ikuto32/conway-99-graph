"""Full authenticated DRAT replay and raw native outcome; cyclic subclass only."""
from datetime import datetime,timezone
from hashlib import sha256,file_digest
from pathlib import Path
import argparse,json,platform,re,subprocess,sys,time

ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/'
RUN=B+'20260930_hadamard_cyclic_native_pilot/'
CNF=B+'20260930_hadamard_six_prism_cyclic_cnf/instance.cnf'
PROOF=RUN+'main/proof.drat'
ENC=B+'20260930_independent_review/hadamard_cyclic_factor_cnf/summary.json'
RED=B+'20260930_independent_review/hadamard_six_prism_cyclic_reduction/summary.json'
BUILD='build/rook-drat-checker/'
PINS={CNF:'e0895d94060a8d8b25adb78cf298b4b6f6f94f8c89ac242c180c1e4b320580d8',PROOF:'51d67cf0f60365e01a744d2066e0999e944c27a56e3024a73dd5135b000e6ed9',ENC:'494add3aecbd2d7d4629c738be73dda3a884c89ecb624fbdb5e867dca2a6ad64',RED:'7b9d988b946284d7a9fbcccccf1c2f32592dbdeb2e30cb6201e1565ea75d4de1',RUN+'summary.json':'6a31c5d8dee7e8d781fca5ec51f27731e935a1cc1e25dbf0eb026ae6f119d3d5',BUILD+'drat-trim.exe':'23d1613cb0b1ed491f4e723ff82492a8be6c349c2426d440412842c5246b90ac',BUILD+'build_manifest.json':'219e14aeb9efb7df5629cb45405b08d45b2613133207e92bd4f7c09a5b2211b7',BUILD+'build_receipt.json':'4862b4cc61fe2832943c988c5418cd85ae795924fd83a40482c0da4fb03b7e4b'}
def need(ok,why):
    if not ok:raise ValueError(why)
def digest(p):
    with Path(p).open('rb')as f:return file_digest(f,'sha256').hexdigest()
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def load(p):return json.loads((ROOT/p).read_bytes())
def save(p,x):
    with Path(p).open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def bind(path,h,records):
    need(digest(ROOT/path)==h,'bound input '+path);records[path]=h

def authenticate(records):
    # Adapted from the frozen independent Wave154 checker authentication path.
    # Read immutable Git blobs only; the dirty tools working copy is untouched.
    for p,h in PINS.items():bind(p,h,records)
    manifest=load(BUILD+'build_manifest.json');receipt=load(BUILD+'build_receipt.json')
    need(receipt['exit_code']==0 and receipt['binary_sha256']==PINS[BUILD+'drat-trim.exe'] and receipt['build_manifest_sha256']==PINS[BUILD+'build_manifest.json'],'successful authenticated checker build')
    for name,field in [('upstream-drat-trim.c','upstream_sha256'),('windows-portability.patch','patch_sha256'),('drat-trim.c','patched_source_sha256'),('build.cmd','build_script_sha256')]:bind(BUILD+name,manifest[field],records)
    for name,field in [('build_stdout.log','stdout_sha256'),('build_stderr.log','stderr_sha256')]:bind(BUILD+name,receipt[field],records)
    bind('acceleration/audit_20260930_rook_drat_build_v1.py',receipt['source_auditor_sha256'],records)
    for pathfield,hashfield in [('compiler_path','compiler_sha256'),('environment_script_path','environment_script_sha256')]:need(digest(manifest[pathfield])==manifest[hashfield],'checker build tool identity')
    upstream_command=['git','-C','tools/drat-trim','show',manifest['upstream_commit']+':drat-trim.c'];upstream=subprocess.check_output(upstream_command,cwd=ROOT)
    need(upstream==(ROOT/BUILD/'upstream-drat-trim.c').read_bytes(),'immutable upstream source')
    patch_command=['git','show',manifest['patch_source_commit']+':'+manifest['patch_source_path']];patch=subprocess.check_output(patch_command,cwd=ROOT)
    need(patch==(ROOT/BUILD/'windows-portability.patch').read_bytes(),'immutable portability patch')
    replacement=b'''#ifdef _WIN32
#include <windows.h>
#define getc_unlocked getc
#ifdef ERROR
#undef ERROR
#endif
#ifdef FAILED
#undef FAILED
#endif
static int gettimeofday(struct timeval *value, void *timezone_unused) {
  FILETIME file_time;
  ULARGE_INTEGER ticks;
  (void) timezone_unused;
  GetSystemTimeAsFileTime(&file_time);
  ticks.LowPart = file_time.dwLowDateTime;
  ticks.HighPart = file_time.dwHighDateTime;
  /* FILETIME counts 100 ns intervals since 1601-01-01. */
  ticks.QuadPart -= 116444736000000000ULL;
  value->tv_sec = (long) (ticks.QuadPart / 10000000ULL);
  value->tv_usec = (long) ((ticks.QuadPart % 10000000ULL) / 10ULL);
  return 0;
}
#else
#include <sys/time.h>
#endif
'''
    old=b'#include <sys/time.h>\n';need(upstream.count(old)==1 and upstream.replace(old,replacement)==(ROOT/BUILD/'drat-trim.c').read_bytes(),'all checker logic unchanged outside exact portability block')
    return dict(upstream_repository=manifest['upstream_repository'],upstream_commit=manifest['upstream_commit'],upstream_git_command=upstream_command,patch_git_command=patch_command,build_command=manifest['build_command'],compiler_path=manifest['compiler_path'],compiler_sha256=manifest['compiler_sha256'],source_sha256=manifest['patched_source_sha256'],binary_sha256=receipt['binary_sha256'],fresh_recompile=False,reason='Authenticated preserved successful build; no compiler-diversity claim.')

def parse_native(text,receipt):
    need(text.splitlines().count("c found 'p cnf 26360 122394' header")==1,'actual complete formula header')
    need([s for s in text.splitlines() if s.startswith('s ')]==['s UNSATISFIABLE'],'exact unique native UNSAT status')
    need(text.splitlines().count('c exit 20')==1 and receipt['actual_exit_code']==20 and not receipt['outer_windows_guard_expired'],'actual normal UNSAT return')
    need("c setting conflict limit to 2000000 conflicts (due to '2000000')" in text,'actual requested conflict limit')
    need('c Version 1.9.5 146207318796f094dcded87349a64f0c6927309e' in text,'native solver source version')
    def one(pattern,convert):
        found=re.findall(pattern,text,re.M);need(len(found)==1,'unique statistic '+pattern);return convert(found[0])
    conflicts=one(r'^c conflicts:\s+(\d+)\s',int);cpu=one(r'^c total process time since initialization:\s+([0-9.]+)\s+seconds$',float);wall=one(r'^c total real time since initialization:\s+([0-9.]+)\s+seconds$',float)
    need(0<=conflicts<=2000000 and 0<=cpu and 0<=wall<300,'actual observed finite limits')
    return dict(result='UNSAT',native_exit=20,conflicts=conflicts,cpu_seconds_display=cpu,wall_seconds_display=wall,wrapper_wall_seconds=receipt['wall_seconds'])

def replay(name,cnf,proof,out,expected):
    command=[str(ROOT/BUILD/'drat-trim.exe'),str(cnf),str(proof)];start=time.monotonic();run=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=120)
    for suffix,data in [('stdout.log',run.stdout),('stderr.log',run.stderr)]:(out/f'{name}.{suffix}').write_bytes(data)
    accepted=run.returncode==0 and b's VERIFIED' in run.stdout
    record=dict(name=name,command=command,cwd=str(ROOT),timestamp=datetime.now(timezone.utc).isoformat(),exit_code=run.returncode,accepted=accepted,expected_acceptance=expected,elapsed_seconds=time.monotonic()-start,timeout_seconds=120,cnf_sha256=digest(cnf),proof_sha256=digest(proof),stdout=key(out/f'{name}.stdout.log'),stdout_sha256=digest(out/f'{name}.stdout.log'),stderr=key(out/f'{name}.stderr.log'),stderr_sha256=digest(out/f'{name}.stderr.log'))
    save(out/f'{name}.receipt.json',record);print(json.dumps(dict(name=name,accepted=accepted,expected=expected,exit=run.returncode)),flush=True);need(accepted==expected,'independent proof/control result '+name);return record

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);inputs={};started=time.monotonic()
    try:
        checker=authenticate(inputs);enc=load(ENC);red=load(RED)
        need(enc['status']=='INDEPENDENT_FIXED_SUPPORT_CYCLIC_COLORING_CNF_PASS' and red['status']=='INDEPENDENT_HADAMARD_CYCLIC_FACTOR_REDUCTION_PASS','separate scope/encoding gates')
        for report in [enc,red]:
            for p,h in report['inputs_sha256'].items():bind(p,h,inputs)
        need((enc['counts']['variables'],enc['counts']['clauses'])==(26360,122394) and enc['inputs_sha256'][CNF]==PINS[CNF],'exact complete encoding scope')
        summary=load(RUN+'summary.json');manifest=load(RUN+'manifest.json');receipt=load(RUN+'main/solver.receipt.json');launch=load(RUN+'main/launch.json')
        for p,h in {**manifest['inputs_sha256'],**summary['outputs_sha256']}.items():bind(p,h,inputs)
        for p in [RUN+'manifest.json',RUN+'main/solver.receipt.json',RUN+'main/launch.json']:bind(p,digest(ROOT/p),inputs)
        limits=dict(native_seconds=300,conflicts=2000000,address_space_bytes=4294967296,file_bytes=10737418240,kill_after_seconds=5,outer_windows_guard_seconds=320,maximum_research_attempts=1,automatic_retry=False)
        need(manifest['mode']=='RESEARCH' and manifest['limits']==limits and summary['research_calls']==1 and summary['automatic_retry']is False,'one frozen bounded attempt')
        need(summary['receipt']==receipt and summary['actual_exit_code']==20 and receipt['command']==launch['command'],'raw invocation identity')
        cmd=receipt['command'];need(all(x in cmd for x in ['300s','--signal=TERM','--kill-after=5s','--as=4294967296:4294967296','--fsize=10737418240:10737418240','--core=0:0','--no-binary'])and cmd[cmd.index('-c')+1]=='2000000','exact resource invocation')
        need(launch['cnf_sha256']==PINS[CNF] and any(x.endswith('/'+CNF)for x in cmd),'launched exact CNF')
        text=(ROOT/receipt['stdout']).read_text();need(digest(ROOT/receipt['stdout'])==receipt['stdout_sha256']and digest(ROOT/receipt['stderr'])==receipt['stderr_sha256']and(ROOT/receipt['stderr']).read_bytes()==b'','authentic native logs')
        outcome=parse_native(text,receipt);corrupt=[]
        for label,bad,r in [('wrong_header',text.replace('26360 122394','26360 122393'),receipt),('wrong_status',text.replace('s UNSATISFIABLE','s SATISFIABLE'),receipt),('duplicate_status',text+'s UNSATISFIABLE\n',receipt),('wrong_exit',text,{**receipt,'actual_exit_code':0}),('outer_guard',text,{**receipt,'outer_windows_guard_expired':True}),('wrong_limit',text.replace("2000000 conflicts (due to '2000000')","2000000 conflicts (due to '1')"),receipt)]:
            try:parse_native(bad,r)
            except ValueError:corrupt.append(label)
            else:raise ValueError('accepted corrupt native record '+label)
        copy=summary['proof_copy'];need(copy['sha256']==PINS[PROOF]and copy['bytes']==(ROOT/PROOF).stat().st_size==29697087,'whole trace bytes and identity')
        for name,field in [('transfer_hash','native_hash_receipt'),('transfer_copy','copy_receipt')]:
            rec=load(RUN+'main/'+name+'.receipt.json');need(copy[field]==rec and rec['actual_exit_code']==0 and rec['outer_windows_guard_expired']is False,'trace transfer command success')
            for channel in ['stdout','stderr']:bind(rec[channel],rec[channel+'_sha256'],inputs)
        need((ROOT/copy['native_hash_receipt']['stdout']).read_text().split()==[PINS[PROOF],copy['linux_source']],'native and local trace identity')
        for rec in [manifest['filesystem_receipt'],manifest['ext4_disk_receipt']]:
            need(rec['actual_exit_code']==0 and not rec['outer_windows_guard_expired'],'prelaunch filesystem observations succeeded')
            for channel in ['stdout','stderr']:bind(rec[channel],rec[channel+'_sha256'],inputs)
        fixtures={'tiny_unsat.cnf':b'p cnf 2 4\n1 2 0\n1 -2 0\n-1 2 0\n-1 -2 0\n','tiny_sat.cnf':b'p cnf 2 3\n1 2 0\n1 -2 0\n-1 2 0\n','tiny_valid.drat':b'-2 0\n1 0\n0\n','invalid_empty_only.drat':b'0\n','invalid_fresh_unit.drat':b'3 0\n0\n'}
        for name,data in fixtures.items():(out/name).write_bytes(data)
        clauses=[(1,2),(1,-2),(-1,2),(-1,-2)];sat=lambda cs:[bits for bits in range(4)if all(any(bool(bits&(1<<(abs(x)-1)))==(x>0)for x in row)for row in cs)]
        need(sat(clauses)==[]and sat(clauses[:3])==[3],'independent tiny truth oracle')
        specs=[('positive_tiny',out/'tiny_unsat.cnf',out/'tiny_valid.drat',True),('corrupt_missing_units',out/'tiny_unsat.cnf',out/'invalid_empty_only.drat',False),('corrupt_fresh_unit',out/'tiny_unsat.cnf',out/'invalid_fresh_unit.drat',False),('corrupt_formula_is_sat',out/'tiny_sat.cnf',out/'tiny_valid.drat',False),('corrupt_main_empty_only',ROOT/CNF,out/'invalid_empty_only.drat',False),('main_complete_proof',ROOT/CNF,ROOT/PROOF,True)]
        runs=[replay(*spec[:3],out,spec[3])for spec in specs]
        command=['wsl.exe','--distribution','Ubuntu-24.04','--exec','/usr/bin/ps','-eo','pid,args'];ps=subprocess.run(command,capture_output=True,text=True,timeout=20);need(ps.returncode==0,'fresh read-only process observation')
        observation=dict(timestamp=datetime.now(timezone.utc).isoformat(),command=command,matching_exact_input_processes=[s.strip()for s in ps.stdout.splitlines()if '/'+CNF in s]);save(out/'process_observation.json',observation)
        for p,h in list(inputs.items()):bind(p,h,inputs)
        for p in [key(__file__),'uv.lock','pyproject.toml','docs/AUDIT_20260930_HADAMARD_CYCLIC_UNSAT.md']:bind(p,digest(ROOT/p),inputs)
        now=datetime.now(timezone.utc).isoformat();statement='No binary36x60 prescribed-Gram factor of the frozen six-prism coordinate support L satisfies both all1770 column-pair overlap caps and the prescribed cyclic fibre-triplet construction restriction; its exact26360-variable122394-clause CNF is UNSAT.'
        limitations=['This excludes only the extra cyclic construction subfamily of one literal support, not all factors for that support or core.','No residual D, full99 graph, target automorphism premise or general nonexistence claim.','DRAT-trim, its reviewed Windows portability block, MSVC and runtime remain trusted; no fresh diverse compilation.','Complete trace was replayed; solver correctness is not trusted for UNSAT.','Encoding/reduction mathematics rely on separately pinned independent audits.']
        report=dict(status='INDEPENDENT_FIXED_HADAMARD_CYCLIC_FACTOR_UNSAT_PASS',timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=inputs,outputs_sha256={key(p):digest(p)for p in out.iterdir()if p.is_file()},checker_provenance=checker,controls_and_replay=runs,native_outcome=outcome,native_corruptions_rejected=corrupt,configured_limits=limits,native_command=cmd,run_source_commit=manifest['source_commit'],run_command=manifest['command'],proof=dict(path=PROOF,sha256=PINS[PROOF],bytes=29697087,complete_independent_replay=True,availability='LOCAL_ONLY'),cnf_sha256=PINS[CNF],variables=26360,clauses=122394,current_process_observation=observation,claim_id='C-FIXED-HADAMARD-SIX-PRISM-CYCLIC-FACTOR-EXCLUSION',claim_revision=1,statement=statement,verifier='/root/state_literature_audit',method='independent_complete_D​RAT_artifact_check_and_native_receipt_review'.replace('\u200b',''),recommendation='VERIFIED',review_state='CLEAR',artifact_availability='LOCAL_ONLY',external_review=False,target_resolution=False,limitations=limitations,shared_components=['Authentication and tiny DRAT controls adapted from prior independently authored Wave154 checker, no producer imports.','Proof checker source/build authenticated against immutable Git blobs.'],elapsed_seconds=time.monotonic()-started)
        save(out/'summary.json',report)
        save(out/'claim_binding.json',dict(id=report['claim_id'],revision=1,statement=statement,kind='exclusion',basis=['DERIVED','COMPUTED'],recommendation='VERIFIED',review_state='CLEAR',scope=limitations[0],assumptions=['No nontrivial target automorphism is assumed.','The cyclic restriction is an additional condition on the partial factor, not a normalization of all fixed-support factors.'],dependencies=[dict(id='C-FIXED-HADAMARD-SIX-PRISM-CYCLIC-COLORING-CNF',revision=1,relation='encoding_equivalence')],reduction_dependency=dict(path=RED,sha256=PINS[RED],relation='normalization',ledger_id=None,ledger_id_null_reason='Await exact proposed reduction claim ID; mathematical artifact binding is complete.'),evidence=[dict(path=key(out/'summary.json'),sha256=digest(out/'summary.json'),availability='LOCAL_ONLY'),dict(path=PROOF,sha256=PINS[PROOF],availability='LOCAL_ONLY')],verifier=report['verifier'],method=report['method'],limitations=limitations,created_at=now,updated_at=now))
        print(json.dumps(dict(status=report['status'],sha256=digest(out/'summary.json'),binding_sha256=digest(out/'claim_binding.json'))))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e)));raise
if __name__=='__main__':main()
