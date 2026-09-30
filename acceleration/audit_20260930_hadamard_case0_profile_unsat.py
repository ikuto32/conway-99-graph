"""Complete proof replay for the literal case0 profile, with no orbit inference."""
import argparse, hashlib, importlib.util, json, platform, re, subprocess, sys, time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results'
D=B/'20260930_hadamard_case0_profile_cnf';RUN=B/'20260930_hadamard_case0_profile_native_pilot'
ENC=B/'20260930_independent_review/hadamard_case0_profile_cnf/summary.json'
OBJ=B/'20260930_independent_review/hadamard_case0_profile_object_calibration/summary.json'
PRIOR=B/'20260930_independent_review/hadamard_balanced_gram_unsat_v2/summary.json'
HELPER=ROOT/'acceleration/audit_20260930_hadamard_balanced_gram_unsat_v2.py'
PINS={D/'instance.cnf':'2e949832491635b794e02b525ac983c0920d66cf91ee4e039564c5920008b22e',RUN/'summary.json':'89a4d2ea6bfdcd9d435f969ced185b8bd1868336a707101b7735fa14380558c4',RUN/'main/proof.drat':'01ee3198778714f32bf0e7e0c4a89ab3d29ecceb088ccf392ee0e2749418d07d',ENC:'ea0398fc4ac25ac4746effab578499d21eaa2ae67fc17509e5780e770835c186',OBJ:'1e8d6b79c903969ae35a389d374b5d2150da6b7d9c5f32be4ff89e268edbe05a',PRIOR:'edbbda720ea38ca5c565837bc39b5083eb145a64386c9e070fe89dfe5d6cebc5'}
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(p.read_bytes())
def save(p,v):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,indent=2);f.write('\n')
def parse(text,receipt):
    need([l for l in text.splitlines() if l.startswith('s ')]==['s UNSATISFIABLE'],'one literal UNSAT status')
    need(text.splitlines().count("c found 'p cnf 10564 187408' header")==1,'exact native formula dimensions')
    need(text.splitlines().count('c exit 20')==1 and receipt['actual_exit_code']==20 and not receipt['outer_windows_guard_expired'],'normal native20')
    need('c Version 1.9.5 146207318796f094dcded87349a64f0c6927309e' in text,'actual solver version')
    need("c setting conflict limit to 1000000 conflicts (due to '1000000')" in text,'configured conflict allocation')
    def one(pattern,typ):
        found=re.findall(pattern,text,re.M);need(len(found)==1,'unique native statistic');return typ(found[0])
    stats=dict(conflicts=one(r'^c conflicts:\s+(\d+)\s',int),native_cpu_seconds=one(r'^c total process time since initialization:\s+([0-9.]+)\s+seconds$',float),native_wall_seconds=one(r'^c total real time since initialization:\s+([0-9.]+)\s+seconds$',float),trace_bytes=one(r'^c DRAT (\d+) bytes ',int),wrapper_wall_seconds=receipt['wall_seconds'])
    need(stats['conflicts']==12232 and stats['trace_bytes']==9139513 and stats['native_wall_seconds']<60,'actual complete bounded result')
    return stats
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};started=time.perf_counter()
    def pin(p,h=None):
        p=p.resolve();v=sha(p);need(h is None or v==h,'identity '+key(p));pins[key(p)]=v
    try:
        for p,h in PINS.items():pin(p,h)
        prior=read(PRIOR);pin(HELPER,prior['inputs_sha256'][key(HELPER)])
        spec=importlib.util.spec_from_file_location('independent_authenticated_drat',HELPER);helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
        for p in [helper.BUILD/'drat-trim.exe',helper.BUILD/'build_manifest.json',helper.BUILD/'build_receipt.json']:pin(p,helper.PINS[p])
        provenance=helper.authenticate(pin)
        enc=read(ENC);need(enc['status']=='INDEPENDENT_HADAMARD_CASE0_PROFILE_ENCODING_PASS' and enc['variables']==10564 and enc['clauses']==187408,'complete exact encoding gate')
        for p,h in enc['inputs_sha256'].items():pin(ROOT/p,h)
        pin(ENC.parent/'claim_binding.json',enc['outputs_sha256'][key(ENC.parent/'claim_binding.json')]);eb=read(ENC.parent/'claim_binding.json')
        need(eb['id']=='C-FIXED-HADAMARD-FOUR-EXCEPTION-CASE0-GRAM-ENCODING' and eb['revision']==1,'exact scope claim dependency')
        summary=read(RUN/'summary.json');manifest=read(RUN/'manifest.json');receipt=read(RUN/'main/solver.receipt.json');launch=read(RUN/'main/launch.json')
        for p,h in {**manifest['inputs_sha256'],**summary['outputs_sha256']}.items():pin(ROOT/p,h)
        for p in RUN.iterdir():
            if p.is_file():pin(p)
        need(summary['receipt']==receipt and receipt['command']==launch['command'] and summary['research_calls']==1 and summary['automatic_retry'] is False,'one exact attempt')
        cmd=receipt['command'];need(all(v in cmd for v in ['60s','--signal=TERM','--kill-after=5s','--as=4294967296:4294967296','--fsize=10737418240:10737418240','--core=0:0','--no-binary']) and cmd[cmd.index('-c')+1]=='1000000','frozen resource command')
        need(receipt['outer_windows_guard_seconds']==70 and any(x.endswith('/'+key(D/'instance.cnf')) for x in cmd) and launch['cnf_sha256']==PINS[D/'instance.cnf'],'exact checked CNF launched')
        text=(ROOT/receipt['stdout']).read_text();stats=parse(text,receipt);proof=RUN/'main/proof.drat';transfer=summary['proof_copy']
        need(transfer['bytes']==proof.stat().st_size==9139513 and transfer['sha256']==PINS[proof],'complete trace bytes/hash')
        need((RUN/'main/transfer_hash.stdout.log').read_text().split()==[PINS[proof],transfer['linux_source']],'native and copied proof identity')
        for r in [receipt,transfer['copy_receipt'],transfer['native_hash_receipt']]:
            if r is not receipt:need(r['actual_exit_code']==0 and not r['outer_windows_guard_expired'],'trace copy success')
            for channel in ['stdout','stderr']:pin(ROOT/r[channel],r[channel+'_sha256'])
        corrupted=[]
        for name,t,r in [('wrong_header',text.replace('10564 187408','10564 187409'),receipt),('wrong_status',text.replace('s UNSATISFIABLE','s SATISFIABLE'),receipt),('duplicate_status',text+'s UNSATISFIABLE\n',receipt),('wrong_exit',text,{**receipt,'actual_exit_code':0}),('outer_timeout',text,{**receipt,'outer_windows_guard_expired':True}),('wrong_allocation',text.replace("1000000 conflicts (due to '1000000')","1000000 conflicts (due to '2')"),receipt)]:
            try:parse(t,r)
            except ValueError:corrupted.append(name)
            else:raise ValueError('accepted corrupted receipt '+name)
        fixtures={'tiny_unsat.cnf':b'p cnf 2 4\n1 2 0\n1 -2 0\n-1 2 0\n-1 -2 0\n','tiny_sat.cnf':b'p cnf 2 3\n1 2 0\n1 -2 0\n-1 2 0\n','tiny_valid.drat':b'-2 0\n1 0\n0\n','empty_only.drat':b'0\n','fresh_unit.drat':b'3 0\n0\n'}
        for name,contents in fixtures.items():(out/name).write_bytes(contents)
        clauses=[(1,2),(1,-2),(-1,2),(-1,-2)]
        oracle=lambda cs:[b for b in range(4) if all(any(bool(b&(1<<(abs(v)-1)))==(v>0) for v in c) for c in cs)]
        need(oracle(clauses)==[] and oracle(clauses[:-1])==[3],'complete tiny truth calibration')
        tests=[('positive_reasoning',out/'tiny_unsat.cnf',out/'tiny_valid.drat',True),('missing_reasoning',out/'tiny_unsat.cnf',out/'empty_only.drat',False),('fresh_unit',out/'tiny_unsat.cnf',out/'fresh_unit.drat',False),('changed_SAT_input',out/'tiny_sat.cnf',out/'tiny_valid.drat',False),('actual_input_empty_only',D/'instance.cnf',out/'empty_only.drat',False),('complete_case0_proof',D/'instance.cnf',proof,True)]
        replays=[helper.replay(name,cnf,p,out,expected) for name,cnf,p,expected in tests]
        command=['wsl.exe','--distribution','Ubuntu-24.04','--exec','/usr/bin/ps','-C','cadical','-o','pid,ppid,comm,pcpu,rss,args'];proc=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=10)
        need(proc.returncode in [0,1] and (proc.returncode!=1 or len(proc.stdout.splitlines())<=1),'targeted process observation')
        (out/'process.stdout.log').write_text(proc.stdout,encoding='utf-8');(out/'process.stderr.log').write_text(proc.stderr,encoding='utf-8')
        observation=dict(timestamp=datetime.now(timezone.utc).isoformat(),command=command,exit_code=proc.returncode,stdout_sha256=sha(out/'process.stdout.log'),stderr_sha256=sha(out/'process.stderr.log'),exact_input_processes=[l for l in proc.stdout.splitlines() if '/'+key(D/'instance.cnf') in l],scope='This timestamped targeted process observation only.')
        save(out/'process_observation.json',observation)
        for p in [Path(__file__),ROOT/'docs/AUDIT_20260930_HADAMARD_CASE0_PROFILE_UNSAT.md']:pin(p)
        ts=datetime.now(timezone.utc).isoformat();proof_record=dict(path=key(proof),sha256=PINS[proof],bytes=9139513,complete_independent_replay=True,availability='LOCAL_ONLY',availability_reason='Complete raw artifact is below10MiB and ready for parent publication; current local presence is not a public availability claim.')
        limitations=['Only the literal case0 count profile on this fixed support; no orbit transfer, other profile or whole-support conclusion.','Within-group column caps are premises of the encoded domains. Cross-group caps and residualD are omitted.','The exact proof checker, reviewed Windows portability shim, compiler and runtime remain trusted; no diverse or formal checker claim.','Solver correctness is not a premise of the proof result.']
        statement='No binary36x60factor on the frozen six-prism Hadamard support has the prescribed integer Gram, within-triple column caps, and literal case0 profile: exceptional groups0,7,9,19, signs1,-1,-1,1, common coordinates2,4, with deviations[-1,0,1] and[1,0,-1]. The exact10564-variable187408-clause equivalent formula is UNSAT by complete independently replayed DRAT proof.'
        binding=dict(id='C-FIXED-HADAMARD-FOUR-EXCEPTION-CASE0-EXCLUSION',revision=1,kind='exclusion',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',statement=statement,scope=limitations[0],assumptions=['Pinned fixed support and literal case0 count profile.','Within-triple column caps.','No target automorphism assumption.'],dependencies=[dict(id=eb['id'],revision=1,relation='encoding_equivalence')],verifier='/root/structural_attack',producer='/root',method='Complete raw DRAT replay against exact independently checked CNF, authenticated checker source/binary, positive/corrupt proof controls and native receipt validation.',shared_components=['Reuses only frozen independently authored checker-authentication and subprocess replay helpers from the balanced proof review.','Same source-authenticated DRAT-trim binary and compiler/runtime as earlier checks; no producer Python imports.'],inputs_sha256=pins,evidence_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},proof=proof_record,limitations=limitations,artifact_availability='LOCAL_ONLY',availability_reason='Awaiting parent publication.',external_review=None,external_review_reason='No external peer review asserted.',created_at=ts,updated_at=ts)
        save(out/'claim_binding.json',binding)
        report=dict(status='INDEPENDENT_FIXED_HADAMARD_CASE0_PROFILE_UNSAT_PASS',timestamp=ts,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,outputs_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},proof=proof_record,checker_provenance=provenance,replays=replays,native_outcome=stats,configured_limits=manifest['limits'],native_command=cmd,run_source_commit=manifest['source_commit'],native_receipt_corruptions_rejected=corrupted,process_observation=observation,claim_id=binding['id'],claim_revision=1,scope=limitations[0],new_solver_calls=0,target_resolution=False,elapsed_seconds=time.perf_counter()-started)
        save(out/'summary.json',report);print(json.dumps(dict(status=report['status'],summary_sha256=sha(out/'summary.json'),claim_binding_sha256=sha(out/'claim_binding.json'))))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e)));raise
if __name__=='__main__':main()
