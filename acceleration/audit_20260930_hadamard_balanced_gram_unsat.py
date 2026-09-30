"""Independent complete DRAT replay for one balanced fixed-support family."""
import argparse,copy,hashlib,json,platform,re,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results';D=B/'20260930_hadamard_balanced_gram_cnf';RUN=B/'20260930_hadamard_balanced_gram_native_pilot';BUILD=ROOT/'build/rook-drat-checker'
ENC=B/'20260930_independent_review/hadamard_balanced_gram_cnf_v2/summary.json'
PINS={
 D/'instance.cnf':'c2d780f94dac4dda955743df03f8db2e8ec0f51217c671eb19fc5e42ed69ba37',
 RUN/'main/proof.drat':'94d2ab35c76b61f3deb01ebfd9ca0dc70452bddf847383d5838b2b2ca902396b',
 RUN/'summary.json':'08c3fd9709b4c810015499fe35b3078b4a3a3a2231517f94ad5782951c8f485e',
 RUN/'manifest.json':'a73070c8c5c5b16c803cbb6125f2a98502bf8510ceada23ff757c2276c4b9acd',
 ENC:'b63a4de43c1bcf4de56c52e4b4cc3ae8c697a3198654eb3f44d97bce7549ea7c',
 BUILD/'drat-trim.exe':'23d1613cb0b1ed491f4e723ff82492a8be6c349c2426d440412842c5246b90ac',
 BUILD/'build_manifest.json':'219e14aeb9efb7df5629cb45405b08d45b2613133207e92bd4f7c09a5b2211b7',
 BUILD/'build_receipt.json':'4862b4cc61fe2832943c988c5418cd85ae795924fd83a40482c0da4fb03b7e4b',
}
def need(x,m):
    if not x:raise ValueError(m)
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def save(p,x):
    with Path(p).open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')

def authenticate(pin):
    m,r=read(BUILD/'build_manifest.json'),read(BUILD/'build_receipt.json')
    need(r['exit_code']==0 and r['binary_sha256']==PINS[BUILD/'drat-trim.exe'] and r['build_manifest_sha256']==PINS[BUILD/'build_manifest.json'],'preserved successful checker build')
    for name,field in [('upstream-drat-trim.c','upstream_sha256'),('windows-portability.patch','patch_sha256'),('drat-trim.c','patched_source_sha256'),('build.cmd','build_script_sha256')]:pin(BUILD/name,m[field])
    for name,field in [('build_stdout.log','stdout_sha256'),('build_stderr.log','stderr_sha256')]:pin(BUILD/name,r[field])
    pin(ROOT/'acceleration/audit_20260930_rook_drat_build_v1.py',r['source_auditor_sha256'])
    for p,h in [('compiler_path','compiler_sha256'),('environment_script_path','environment_script_sha256')]:need(sha(m[p])==m[h],'preserved compiler environment')
    upstream_cmd=['git','-C','tools/drat-trim','show',m['upstream_commit']+':drat-trim.c']
    upstream=subprocess.check_output(upstream_cmd,cwd=ROOT)
    need(upstream==(BUILD/'upstream-drat-trim.c').read_bytes(),'immutable upstream Git blob')
    patch_cmd=['git','show',m['patch_source_commit']+':'+m['patch_source_path']]
    patch=subprocess.check_output(patch_cmd,cwd=ROOT)
    need(patch==(BUILD/'windows-portability.patch').read_bytes(),'immutable reviewed portability patch')
    # Reconstruct the sole replacement from the authenticated unified patch.
    removed=[];added=[];hunks=0
    for line in patch.splitlines(keepends=True):
        if line.startswith(b'@@'):hunks+=1
        elif line.startswith(b'-') and not line.startswith(b'---'):removed.append(line[1:])
        elif line.startswith(b'+') and not line.startswith(b'+++'):added.append(line[1:])
    old,new=b''.join(removed),b''.join(added)
    need(hunks==1 and old==b'#include <sys/time.h>\n' and upstream.count(old)==1,'only the one reviewed portability hunk')
    need(upstream.replace(old,new)==(BUILD/'drat-trim.c').read_bytes(),'all checking logic unchanged outside reviewed block')
    return dict(upstream_repository=m['upstream_repository'],upstream_commit=m['upstream_commit'],upstream_command=upstream_cmd,patch_command=patch_cmd,source_sha256=m['patched_source_sha256'],binary_sha256=r['binary_sha256'],compiler_sha256=m['compiler_sha256'],build_command=m['build_command'],fresh_recompile=False,limitations='Preserved authenticated MSVC build and reviewed Windows shim; no diverse compiler or formal checker claim.')

def parse(text,receipt):
    need([line for line in text.splitlines() if line.startswith('s ')]==['s UNSATISFIABLE'],'unique raw UNSAT status')
    need(text.splitlines().count("c found 'p cnf 10480 74200' header")==1,'literal full CNF header')
    need(text.splitlines().count('c exit 20')==1 and receipt['actual_exit_code']==20 and receipt['outer_windows_guard_expired'] is False,'normal native UNSAT exit')
    need("c setting conflict limit to 1000000 conflicts (due to '1000000')" in text,'raw configured conflict limit')
    need('c Version 1.9.5 146207318796f094dcded87349a64f0c6927309e' in text,'actual solver version')
    def one(p,t):
        found=re.findall(p,text,re.M);need(len(found)==1,'unique raw statistic '+p);return t(found[0])
    result=dict(conflicts=one(r'^c conflicts:\s+(\d+)\s',int),cpu_seconds=one(r'^c total process time since initialization:\s+([0-9.]+)\s+seconds$',float),native_wall_seconds=one(r'^c total real time since initialization:\s+([0-9.]+)\s+seconds$',float),trace_bytes=one(r'^c DRAT (\d+) bytes ',int),wrapper_wall_seconds=receipt['wall_seconds'])
    need(result['conflicts']<=1000000 and result['native_wall_seconds']<60 and result['trace_bytes']==227098316,'actual bounded outcome')
    return result

def replay(name,cnf,proof,out,expected):
    cmd=[str(BUILD/'drat-trim.exe'),str(cnf),str(proof)];start=time.perf_counter();stamp=datetime.now(timezone.utc).isoformat()
    print(json.dumps(dict(check=name,state='STARTED')),flush=True)
    try:run=subprocess.run(cmd,cwd=ROOT,capture_output=True,timeout=180)
    except subprocess.TimeoutExpired as ex:
        (out/(name+'.stdout.log')).write_bytes(ex.stdout or b'');(out/(name+'.stderr.log')).write_bytes(ex.stderr or b'')
        save(out/(name+'.receipt.json'),dict(command=cmd,timeout_seconds=180,outcome='TIMEOUT',accepted=False,timestamp=stamp));raise
    (out/(name+'.stdout.log')).write_bytes(run.stdout);(out/(name+'.stderr.log')).write_bytes(run.stderr)
    accepted=run.returncode==0 and b's VERIFIED' in run.stdout
    result=dict(name=name,command=cmd,cwd=str(ROOT),timestamp=stamp,actual_exit_code=run.returncode,accepted=accepted,expected_acceptance=expected,elapsed_seconds=time.perf_counter()-start,timeout_seconds=180,cnf_sha256=sha(cnf),proof_sha256=sha(proof),stdout_sha256=sha(out/(name+'.stdout.log')),stderr_sha256=sha(out/(name+'.stderr.log')))
    save(out/(name+'.receipt.json'),result);need(accepted==expected,'proof/control checking result '+name)
    print(json.dumps(dict(check=name,accepted=accepted,expected=expected)),flush=True);return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};start=time.perf_counter()
    def pin(p,h=None):
        p=p.resolve();actual=sha(p);need(h is None or actual==h,'input identity '+key(p));pins[key(p)]=actual
    try:
        for p,h in PINS.items():pin(p,h)
        provenance=authenticate(pin);encoding=read(ENC)
        need(encoding['status']=='INDEPENDENT_HADAMARD_BALANCED_GRAM_ENCODING_PASS' and encoding['variables']==10480 and encoding['clauses']==74200,'exact full balanced encoding gate')
        for p,h in encoding['inputs_sha256'].items():pin(ROOT/p,h)
        summary,manifest=read(RUN/'summary.json'),read(RUN/'manifest.json');receipt=read(RUN/'main/solver.receipt.json');launch=read(RUN/'main/launch.json')
        for p,h in {**manifest['inputs_sha256'],**summary['outputs_sha256']}.items():pin(ROOT/p,h)
        for p in RUN.iterdir():
            if p.is_file():pin(p)
        need(summary['receipt']==receipt and receipt['command']==launch['command'] and summary['research_calls']==1 and summary['automatic_retry'] is False,'one exact native attempt')
        cmd=receipt['command'];need(all(x in cmd for x in ['60s','--signal=TERM','--kill-after=5s','--as=4294967296:4294967296','--fsize=10737418240:10737418240','--core=0:0','--no-binary']) and cmd[cmd.index('-c')+1]=='1000000','literal resource command')
        need(receipt['outer_windows_guard_seconds']==70 and any(x.endswith('/'+key(D/'instance.cnf')) for x in cmd) and launch['cnf_sha256']==PINS[D/'instance.cnf'],'launched exact checked formula')
        text=(ROOT/receipt['stdout']).read_text();stats=parse(text,receipt)
        proof=RUN/'main/proof.drat';transfer=summary['proof_copy']
        need(transfer['bytes']==proof.stat().st_size==227098316 and transfer['sha256']==PINS[proof],'whole proof identity/size')
        need((RUN/'main/transfer_hash.stdout.log').read_text().split()==[PINS[proof],transfer['linux_source']],'native/copied proof hash match')
        for r in [receipt,transfer['copy_receipt'],transfer['native_hash_receipt']]:
            if r is not receipt:need(r['actual_exit_code']==0 and not r['outer_windows_guard_expired'],'trace transfer success')
            for channel in ['stdout','stderr']:pin(ROOT/r[channel],r[channel+'_sha256'])
        corrupt=[]
        for name,bad,r in [('wrong_header',text.replace('10480 74200','10480 74201'),receipt),('wrong_status',text.replace('s UNSATISFIABLE','s SATISFIABLE'),receipt),('duplicate_status',text+'s UNSATISFIABLE\n',receipt),('wrong_exit',text,{**receipt,'actual_exit_code':0}),('outer_timeout',text,{**receipt,'outer_windows_guard_expired':True}),('wrong_limit',text.replace("1000000 conflicts (due to '1000000')","1000000 conflicts (due to '2')"),receipt)]:
            try:parse(bad,r)
            except ValueError:corrupt.append(name)
            else:raise ValueError('accepted corrupted receipt '+name)
        fixtures={'tiny_unsat.cnf':b'p cnf 2 4\n1 2 0\n1 -2 0\n-1 2 0\n-1 -2 0\n','tiny_sat.cnf':b'p cnf 2 3\n1 2 0\n1 -2 0\n-1 2 0\n','tiny_valid.drat':b'-2 0\n1 0\n0\n','empty_only.drat':b'0\n','fresh_unit.drat':b'3 0\n0\n'}
        for name,data in fixtures.items():(out/name).write_bytes(data)
        tiny=[(1,2),(1,-2),(-1,2),(-1,-2)]
        oracle=lambda cs:[bits for bits in range(4) if all(any(bool(bits&(1<<(abs(x)-1)))==(x>0) for x in row) for row in cs)]
        need(oracle(tiny)==[] and oracle(tiny[:-1])==[3],'independent complete tiny truth control')
        tests=[('positive_reasoning',out/'tiny_unsat.cnf',out/'tiny_valid.drat',True),('missing_reasoning',out/'tiny_unsat.cnf',out/'empty_only.drat',False),('invalid_fresh_unit',out/'tiny_unsat.cnf',out/'fresh_unit.drat',False),('changed_SAT_formula',out/'tiny_sat.cnf',out/'tiny_valid.drat',False),('actual_input_empty_only',D/'instance.cnf',out/'empty_only.drat',False),('complete_research_proof',D/'instance.cnf',proof,True)]
        replays=[replay(name,cnf,p,out,expected) for name,cnf,p,expected in tests]
        # Targeted observation only; ps exit1 is explicitly no named process.
        command=['wsl.exe','--distribution','Ubuntu-24.04','--exec','/usr/bin/ps','-C','cadical','-o','pid,ppid,comm,pcpu,rss,args'];proc=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=10)
        (out/'process.stdout.log').write_text(proc.stdout,encoding='utf-8');(out/'process.stderr.log').write_text(proc.stderr,encoding='utf-8')
        observation=dict(timestamp=datetime.now(timezone.utc).isoformat(),command=command,exit_code=proc.returncode,stdout_sha256=sha(out/'process.stdout.log'),stderr_sha256=sha(out/'process.stderr.log'),exact_input_processes=[s for s in proc.stdout.splitlines() if '/'+key(D/'instance.cnf') in s],interpretation='Targeted process snapshot only; exit1 with no records means no named cadical process.')
        need(proc.returncode in(0,1) and (proc.returncode!=1 or len(proc.stdout.splitlines())<=1),'targeted observation outcome');save(out/'process_observation.json',observation)
        pin(Path(__file__));ts=datetime.now(timezone.utc).isoformat()
        proof_record=dict(path=key(proof),sha256=PINS[proof],bytes=227098316,complete_independent_replay=True,availability='LOCAL_ONLY',availability_reason='Full raw trace preserved locally pending a public compressed package; a hash alone is not public availability.')
        statement='No balanced binary36x60factor on the frozen six-prism Hadamard coordinate support has the prescribed integer Gram. The complete10480-variable74200-clause encoding covering all150normalized local choices per group is UNSAT by independently replayed DRAT proof.'
        limitations=['Excludes only the extra balanced-triplet class of this literal fixed support, not all factors on that support or all factors for the core.','No outside-column cap premise is needed for this exclusion; no unrestricted target or residualD conclusion.','Trusted DRAT-trim implementation, reviewed Windows portability shim, compiler and runtime; no formal or diverse-checker verification.','Solver correctness is not trusted for the UNSAT result.','Exact coverage depends on the separately checked encoding normalization and complete domain audit.']
        save(out/'claim_binding.json',dict(id='C-FIXED-HADAMARD-BALANCED-GRAM-EXCLUSION',revision=1,kind='exclusion',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',statement=statement,scope=limitations[0],assumptions=['Fixed raw six-prism core and Hadamard support.','Additional coordinatewise balance of every three-column repeated-support group.','No target automorphism is assumed.'],dependencies=[dict(id='C-FIXED-HADAMARD-COMPLETE-BALANCED-GRAM-ENCODING',revision=1,relation='encoding_equivalence')],verifier='/root/structural_attack',producer='/root',method='Independent complete exact DRAT replay plus source-authenticated checker, positive/corrupted proof controls and raw native evidence review.',shared_components=['Windows checker authentication/control method follows the previously independently reviewed proof-checker build; no producer Python code imported.','The calibrated proof-checker binary is shared with previous exclusions; compiler/runtime remain trusted.'],inputs_sha256=pins,evidence_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},proof=proof_record,limitations=limitations,external_review=None,external_review_reason='No external peer review asserted.',artifact_availability='LOCAL_ONLY',availability_reason='Workspace evidence pending parent publication.',created_at=ts,updated_at=ts))
        report=dict(status='INDEPENDENT_FIXED_HADAMARD_BALANCED_GRAM_UNSAT_PASS',timestamp=ts,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,outputs_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},checker_provenance=provenance,proof=proof_record,replays=replays,native_outcome=stats,native_receipt_corruptions_rejected=corrupt,configured_limits=manifest['limits'],native_command=cmd,run_source_commit=manifest['source_commit'],run_command=manifest['command'],process_observation=observation,claim_id='C-FIXED-HADAMARD-BALANCED-GRAM-EXCLUSION',claim_revision=1,statement=statement,limitations=limitations,new_solver_calls=0,target_resolution=False,elapsed_seconds=time.perf_counter()-start)
        save(out/'summary.json',report);print(json.dumps(dict(status=report['status'],summary_sha256=sha(out/'summary.json'),claim_binding_sha256=sha(out/'claim_binding.json'))))
    except BaseException as ex:save(out/'failure.json',dict(error=repr(ex)));raise
if __name__=='__main__':main()
