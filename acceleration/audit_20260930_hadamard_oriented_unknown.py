"""Independent saved-run audit for the single oriented-triple UNKNOWN pilot."""
import argparse,copy,hashlib,json,platform,re,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results'
RUN=B/'20260930_hadamard_oriented_triples_native_pilot';DATA=B/'20260930_hadamard_oriented_triples'
PINS={RUN/'summary.json':'dfc9c56f54c4cce21e873836b262220b7a3864d95abe1d7d55d0d4092f17a971',RUN/'manifest.json':'64b1df3e412952f86876569efa702410bdf7bc48a9cd64443d06017a87187732',B/'20260930_independent_review/hadamard_oriented_triples/summary.json':'35d301643712de203946bb2dc2ce1908e5dc988a783dafff965015cde14a7f93',B/'20260930_independent_review/hadamard_oriented_triples_object_calibration/summary.json':'86d1f685fb5cae1ab83176c489555996dde27e82699e99374f8191a8cfbb0ecc'}
def need(x,m):
    if not x:raise ValueError(m)
def read(p):return json.loads(p.read_bytes())
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
def metric(text,pattern,convert):
    values=re.findall(pattern,text,re.MULTILINE);need(len(values)==1,'unique metric '+pattern);return convert(values[0])
def parse(text):
    need(re.findall(r'^c (UNKNOWN|SATISFIABLE|UNSATISFIABLE)\s*$',text,re.MULTILINE)==['UNKNOWN'],'literal UNKNOWN result')
    need(not re.search(r'^[sv] ',text,re.MULTILINE),'no model/status certificate')
    need(metric(text,r'^c exit (\d+)\s*$',int)==0,'native exit0 log')
    return dict(conflicts=metric(text,r'^c conflicts:\s+(\d+)\s',int),process_seconds=metric(text,r'^c total process time since initialization:\s+([0-9.]+)\s+seconds',float),native_wall_seconds=metric(text,r'^c total real time since initialization:\s+([0-9.]+)\s+seconds',float),maximum_RSS_MB=metric(text,r'^c maximum resident set size of process:\s+([0-9.]+)\s+MB',float),trace_bytes=metric(text,r'^c DRAT (\d+) bytes ',int))
def validate(summary,manifest,receipt,text,proofsha,proofsize):
    stats=parse(text)
    need(summary['receipt']==receipt,'actual receipt equality')
    need(receipt['actual_exit_code']==0 and not receipt['outer_windows_guard_expired'],'normal native UNKNOWN return')
    need(summary['interpreted_result']=='UNKNOWN_NATIVE_OR_RESOURCE_OUTCOME' and summary['research_calls']==1 and summary['target_resolution'] is False and summary['automatic_retry'] is False,'exact outcome scope')
    limits=manifest['limits'];need(limits==dict(native_wall_seconds=60,conflicts=1000000,address_space_bytes=4294967296,trace_file_bytes=10737418240,kill_after_seconds=5,outer_guard_seconds=70,maximum_research_calls=1,automatic_retry=False),'exact preregistered limits')
    need(receipt['outer_windows_guard_seconds']==70 and receipt['wall_seconds']<70,'outer guard receipt')
    command=receipt['command'];proof=summary['proof_copy']['linux_source']
    prefix=['wsl.exe','--distribution','Ubuntu-24.04','--exec','/usr/bin/timeout','--signal=TERM','--kill-after=5s','60s','/usr/bin/prlimit','--as=4294967296:4294967296','--fsize=10737418240:10737418240','--core=0:0']
    need(command[:len(prefix)]==prefix and command[len(prefix):]==['/mnt/c/Users/ikuto/projects/conway-99-graph/build/research-cadical195/source/build/cadical','--no-binary','-c','1000000','/mnt/c/Users/ikuto/projects/conway-99-graph/acceleration/results/20260930_hadamard_oriented_triples/instance.cnf',proof],'exact native command/resources')
    need(stats['conflicts']==1000000 and stats['native_wall_seconds']<60 and stats['trace_bytes']==proofsize,'actual conflict termination and trace count')
    need('c Version 1.9.5 146207318796f094dcded87349a64f0c6927309e' in text and "c found 'p cnf 800 109340' header" in text,'solver/version/exact parsed input')
    transfer=summary['proof_copy'];need(transfer['sha256']==proofsha and transfer['bytes']==proofsize and transfer['copy_receipt']['actual_exit_code']==0 and transfer['native_hash_receipt']['actual_exit_code']==0,'immediate complete byte transfer of partial trace')
    need(proofsize<limits['trace_file_bytes'],'trace within cap')
    return stats
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={}
    def pin(p,h=None):
        p=p.resolve();actual=sha(p);need(h is None or actual==h,'raw identity '+key(p));pins[key(p)]=actual;return actual
    try:
        for p,h in PINS.items():pin(p,h)
        summary,manifest=read(RUN/'summary.json'),read(RUN/'manifest.json')
        for p,h in {**manifest['inputs_sha256'],**summary['outputs_sha256']}.items():pin(ROOT/p,h)
        for p in RUN.iterdir():
            if p.is_file():pin(p)
        receipt=read(RUN/'main/solver.receipt.json');text=(RUN/'main/solver.stdout.log').read_text(encoding='utf-8');proof=RUN/'main/proof.drat';proofsha=pins[key(proof)];proofsize=proof.stat().st_size
        stats=validate(summary,manifest,receipt,text,proofsha,proofsize)
        need((RUN/'main/transfer_hash.stdout.log').read_text().split()[0]==proofsha,'independent copied/native trace hash agreement')
        need(not (RUN/'main/parsed_model.json').exists() and not (RUN/'main/decoded_oriented_cover.json').exists(),'no saved model or cover')
        need(read(RUN/'main/launch.json')['command']==receipt['command'],'frozen launch matches actual receipt')
        for r in [receipt,summary['proof_copy']['copy_receipt'],summary['proof_copy']['native_hash_receipt']]:
            for stream in ['stdout','stderr']:pin(ROOT/r[stream],r[stream+'_sha256'])
        rejected=[]
        for name in ['false_SAT','wrong_exit','conflict_limit','wrong_trace_hash','wrong_trace_size','outer_guard_expired','second_attempt','target_resolution']:
            s,m,r=copy.deepcopy(summary),copy.deepcopy(manifest),copy.deepcopy(receipt)
            if name=='false_SAT':s['interpreted_result']='ORIENTED_COVER_SAT_UNCHECKED'
            elif name=='wrong_exit':r['actual_exit_code']=20;s['receipt']=r
            elif name=='conflict_limit':m['limits']['conflicts']=999999
            elif name=='wrong_trace_hash':s['proof_copy']['sha256']='0'*64
            elif name=='wrong_trace_size':s['proof_copy']['bytes']+=1
            elif name=='outer_guard_expired':r['outer_windows_guard_expired']=True;s['receipt']=r
            elif name=='second_attempt':s['research_calls']=2
            else:s['target_resolution']=True
            try:validate(s,m,r,text,proofsha,proofsize)
            except ValueError:rejected.append(name)
            else:raise ValueError('corruption accepted '+name)
        for name,bad in [('SAT_log',text.replace('c UNKNOWN\n','c SATISFIABLE\n')),('wrong_count',text.replace('c conflicts:               1000000','c conflicts:               999999')),('missing_terminal_exit',text.replace('c exit 0','c exit 20'))]:
            try:validate(summary,manifest,receipt,bad,proofsha,proofsize)
            except ValueError:rejected.append(name)
            else:raise ValueError('log corruption accepted '+name)
        # A fresh read-only observation is separate from the historical receipt.
        command=['wsl.exe','--distribution','Ubuntu-24.04','--exec','/usr/bin/ps','-eo','pid,ppid,stat,args']
        started=datetime.now(timezone.utc).isoformat();proc=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=15)
        (out/'process.stdout.log').write_text(proc.stdout,encoding='utf-8');(out/'process.stderr.log').write_text(proc.stderr,encoding='utf-8')
        exact='/acceleration/results/20260930_hadamard_oriented_triples/instance.cnf'
        live=[line for line in proc.stdout.splitlines() if exact in line and ('cadical' in line or '/usr/bin/timeout' in line)]
        observation=dict(timestamp=started,command=command,exit_code=proc.returncode,exact_input_processes=live,state='NO_EXACT_INPUT_PROCESS_OBSERVED' if proc.returncode==0 and not live else 'UNKNOWN_OR_ACTIVE')
        save(out/'process_observation.json',observation)
        save(out/'controls.json',dict(corruptions_rejected=rejected,actual_positive='Complete saved native UNKNOWN logs/receipts; no positive SAT or UNSAT inference.'))
        pin(Path(__file__));ts=datetime.now(timezone.utc).isoformat()
        evidence={key(p):sha(p) for p in out.iterdir() if p.is_file()}
        binding=dict(id='C-FIXED-HADAMARD-ORIENTED-TRIPLE-NATIVE-UNKNOWN',revision=1,kind='empirical/engineering result',basis=['COMPUTED'],status='VERIFIED',review_state='CLEAR',
            statement='The single frozen oriented-triple native pilot returned UNKNOWN with exit0 after exactly1000000reported conflicts; its copied331620166-byte partial trace matches the original recorded native hash. No oriented cover or nonexistence certificate was produced.',scope='Only this exact source/input/configuration/run receipt; no mathematical exclusion or coverage conclusion.',assumptions=['The pinned native stdout/receipt records are the saved execution evidence.'],dependencies=[dict(id='C-FIXED-HADAMARD-ALL-MIXED-ORIENTED-TRIPLE-ENCODING',revision=1,relation='encoding_equivalence')],
            verifier='/root/structural_attack',producer='/root',method='Independent saved log/receipt/input/output identity audit, fresh complete trace hash, resource command review, and corruption controls.',shared_components=['The authenticated native binary and saved producer execution records.','No solver or producer-runner code imported or executed by the verifier.'],
            inputs_sha256=pins,evidence_sha256=evidence,metrics=stats,wrapper_wall_seconds=receipt['wall_seconds'],configured_limits=manifest['limits'],trace=dict(path=key(proof),sha256=proofsha,bytes=proofsize,availability='LOCAL_ONLY',reason='Large incomplete trace retained locally; not an UNSAT certificate.',proof_replay=None,proof_replay_reason='UNKNOWN did not emit a claimed complete contradiction proof; no replay attempted.'),
            external_review=None,external_review_reason='No external review asserted.',artifact_availability='LOCAL_ONLY',availability_reason='Evidence pending parent publication; partial trace remains local.',limitations=['UNKNOWN excludes nothing.','Resource cap is address space, not an independently measured RSS ceiling.','Timing is one observed run; no performance comparison.','Fresh process observation is timestamped, not a claim of continuing execution.'],created_at=ts,updated_at=ts)
        save(out/'claim_binding.json',binding)
        save(out/'summary.json',dict(status='INDEPENDENT_HADAMARD_ORIENTED_TRIPLE_UNKNOWN_RUN_AUDIT_PASS',timestamp=ts,inputs_sha256=pins,outputs_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},actual_exit_code=0,observed_result='UNKNOWN',metrics=stats,wrapper_wall_seconds=receipt['wall_seconds'],trace_bytes=proofsize,trace_sha256=proofsha,trace_availability='LOCAL_ONLY',trace_is_complete_unsat_certificate=False,controls_rejected=len(rejected),new_solver_calls=0,process_observation=observation))
        print(json.dumps(dict(status='INDEPENDENT_HADAMARD_ORIENTED_TRIPLE_UNKNOWN_RUN_AUDIT_PASS',sha256=sha(out/'summary.json'),claim_binding_sha256=sha(out/'claim_binding.json'))))
    except BaseException as ex:save(out/'failure.json',dict(error=repr(ex)));raise
if __name__=='__main__':main()
