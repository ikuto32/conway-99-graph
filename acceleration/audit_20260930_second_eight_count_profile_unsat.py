"""Complete proof replay for the literal eight-exception count profile, with no orbit inference."""
import argparse, hashlib, importlib.util, json, platform, re, subprocess, sys, time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results'
D=B/'20260930_eight_count_profile_lift_second';RUN=B/'20260930_eight_count_profile_lift_second_native_pilot'
ENC=B/'20260930_independent_review/eight_count_profile_lift_second/summary.json'
OBJ=B/'20260930_independent_review/eight_count_profile_lift_second_object/summary.json'
PRIOR=B/'20260930_independent_review/hadamard_balanced_gram_unsat_v2/summary.json'
HELPER=ROOT/'acceleration/audit_20260930_hadamard_balanced_gram_unsat_v2.py'
PINS={D/'instance.cnf':'dbd7b51dca52b69877888f88addc111f93f02ef52ddd58efebdc5c67e746bc87',RUN/'summary.json':'06865dd375bb4d99c98ec5b51223b796f62f62ec3e7829056f65817510fb1034',RUN/'main/proof.drat':'4d22afafcd8f9ef6629319617c9f671c97a585a4deba8ecec2072e4c1f7ac2c8',ENC:'271d0a82f576bad3273045c5e31a637c317f2426897cdfca4784f443cbbab4bd',OBJ:'6a06c4c6eadc8cf521831fff22cf6a4055230b252bc074f15b043192b374e5df',PRIOR:'edbbda720ea38ca5c565837bc39b5083eb145a64386c9e070fe89dfe5d6cebc5'}
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(p.read_bytes())
def save(p,v):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,indent=2);f.write('\n')
def read_cnf(path):
    clauses=[];pending=[];header=None
    for line in path.read_text().splitlines():
        if line.startswith('c') or not line.strip():continue
        if line.startswith('p '):
            need(header is None,'one CNF header');_,kind,n,m=line.split();need(kind=='cnf','CNF format');header=(int(n),int(m));continue
        for value in map(int,line.split()):
            if value:pending.append(value)
            else:clauses.append(tuple(pending));pending=[]
    need(not pending and header==(9532,len(clauses)) and len(clauses)==162124,'whole exact raw CNF')
    return clauses

def unit_propagation(raw_clauses):
    # Independent sparse occurrence lists and explicit forcing-clause trail.
    clauses=[];satisfied=[];remaining=[];occ={};queue=[];assignment={};trail=[]
    for original,row in enumerate(raw_clauses):
        c=tuple(sorted(set(row),key=lambda v:(abs(v),v)))
        taut=any(-v in c for v in c);index=len(clauses)
        clauses.append(c);satisfied.append(taut);remaining.append(len(c))
        if taut:continue
        if not c:return dict(contradiction=True,conflict_clause=original,trail=trail)
        for v in c:occ.setdefault(v,[]).append(index)
        if len(c)==1:queue.append((c[0],index))
    at=0
    while at<len(queue):
        literal,cause=queue[at];at+=1;v=abs(literal)
        if v in assignment:
            if assignment[v]!=literal:return dict(contradiction=True,conflict_clause=cause,trail=trail)
            continue
        need(all(x==literal or assignment.get(abs(x))==-x for x in clauses[cause]),'literal unit forcing clause')
        assignment[v]=literal;trail.append(dict(literal=literal,forcing_clause=cause))
        for index in occ.get(literal,[]):satisfied[index]=True
        for index in occ.get(-literal,[]):
            if satisfied[index]:continue
            remaining[index]-=1
            if remaining[index]==0:
                need(all(assignment.get(abs(x))==-x for x in clauses[index]),'literal empty clause witness')
                return dict(contradiction=True,conflict_clause=index,trail=trail)
            if remaining[index]==1:
                unassigned=[x for x in clauses[index] if abs(x) not in assignment]
                need(len(unassigned)==1,'unique residual unit');queue.append((unassigned[0],index))
    return dict(contradiction=False,conflict_clause=None,trail=trail,meaning='No unit-propagation contradiction found; no SAT conclusion.')

def parse(text,receipt):
    need([l for l in text.splitlines() if l.startswith('s ')]==['s UNSATISFIABLE'],'one literal UNSAT status')
    need(text.splitlines().count("c found 'p cnf 9532 162124' header")==1,'exact native formula dimensions')
    need(text.splitlines().count('c exit 20')==1 and receipt['actual_exit_code']==20 and not receipt['outer_windows_guard_expired'],'normal native20')
    need('c Version 1.9.5 146207318796f094dcded87349a64f0c6927309e' in text,'actual solver version')
    need("c setting conflict limit to 1000000 conflicts (due to '1000000')" in text,'configured conflict allocation')
    def one(pattern,typ):
        found=re.findall(pattern,text,re.M);need(len(found)==1,'unique native statistic');return typ(found[0])
    conflicts=re.findall(r'^c conflicts:\s+(\d+)\s',text,re.M);need(len(conflicts)<=1,'at most one named conflict statistic')
    stats=dict(conflicts=int(conflicts[0]) if conflicts else None,conflicts_reporting='named native statistic' if conflicts else 'not printed; no count inferred',native_cpu_seconds=one(r'^c total process time since initialization:\s+([0-9.]+)\s+seconds$',float),native_wall_seconds=one(r'^c total real time since initialization:\s+([0-9.]+)\s+seconds$',float),trace_bytes=one(r'^c DRAT (\d+) bytes ',int),wrapper_wall_seconds=receipt['wall_seconds'])
    need((stats['conflicts'] is None or 0<=stats['conflicts']<=1000000) and stats['trace_bytes']==1269209 and stats['native_wall_seconds']<60,'actual complete bounded result')
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
        enc=read(ENC);obj=read(OBJ);need(obj['status']=='INDEPENDENT_SECOND_LITERAL_EIGHT_COUNT_PROFILE_OBJECT_CALIBRATION_PASS','prelaunch object gate');need(enc['status']=='INDEPENDENT_SECOND_LITERAL_EIGHT_COUNT_PROFILE_ENCODING_PASS' and enc['variables']==9532 and enc['clauses']==162124,'complete exact encoding gate')
        for gate in [enc,obj]:
            for p,h in gate['inputs_sha256'].items():pin(ROOT/p,h)
        pin(ENC.parent/'claim_binding.json',enc['outputs_sha256'][key(ENC.parent/'claim_binding.json')]);eb=read(ENC.parent/'claim_binding.json')
        need(eb['id']=='C-FIXED-HADAMARD-SECOND-EIGHT-COUNT-PROFILE-GRAM-ENCODING' and eb['revision']==1,'exact scope claim dependency')
        scope=read(D/'scope.json');need(scope['selected_profile_id']=='count_master_second_native_sat_after_six_cuts' and scope['selected_profile_sha256']=='086fc4155012236d30b13756b01e48ed2050db7cf028274b4aea533333ef0f17' and scope['exceptional_groups']==[1,3,5,11,13,15,18,19] and scope['within_group_column_caps_encoded'] is True and not scope['cross_group_column_caps_encoded'] and not scope['residual_D_encoded'] and not scope['orbit_coverage_used'] and not scope['arc_pruning_used'],'literal initial-domain scope');
        summary=read(RUN/'summary.json');manifest=read(RUN/'manifest.json');receipt=read(RUN/'main/solver.receipt.json');launch=read(RUN/'main/launch.json')
        for p,h in {**manifest['inputs_sha256'],**summary['outputs_sha256']}.items():pin(ROOT/p,h)
        for p in RUN.iterdir():
            if p.is_file():pin(p)
        need(summary['receipt']==receipt and receipt['command']==launch['command'] and summary['research_calls']==1 and summary['automatic_retry'] is False,'one exact attempt')
        cmd=receipt['command'];need(all(v in cmd for v in ['60s','--signal=TERM','--kill-after=5s','--as=4294967296:4294967296','--fsize=10737418240:10737418240','--core=0:0','--no-binary']) and cmd[cmd.index('-c')+1]=='1000000','frozen resource command')
        need(receipt['outer_windows_guard_seconds']==70 and any(x.endswith('/'+key(D/'instance.cnf')) for x in cmd) and launch['cnf_sha256']==PINS[D/'instance.cnf'],'exact checked CNF launched')
        need(cmd[-1]==launch['ext4_proof']==summary['proof_copy']['linux_source'],'same immediate ext4 trace');
        text=(ROOT/receipt['stdout']).read_text();stats=parse(text,receipt);proof=RUN/'main/proof.drat';transfer=summary['proof_copy']
        need(transfer['bytes']==proof.stat().st_size==1269209 and transfer['sha256']==PINS[proof],'complete trace bytes/hash')
        need((RUN/'main/transfer_hash.stdout.log').read_text().split()==[PINS[proof],transfer['linux_source']],'native and copied proof identity')
        for r in [receipt,transfer['copy_receipt'],transfer['native_hash_receipt']]:
            if r is not receipt:need(r['actual_exit_code']==0 and not r['outer_windows_guard_expired'],'trace copy success')
            for channel in ['stdout','stderr']:pin(ROOT/r[channel],r[channel+'_sha256'])
        need(summary['interpreted_result']=='EIGHT_COUNT_PROFILE_UNSAT_TRACE_UNCHECKED','original unapproved result preserved')
        for phase in ['processes_before','fresh_process_observation']:
            obs=summary[phase];need(obs['command'][4:]==['/usr/bin/ps','-C','cadical','-o','pid,ppid,comm,pcpu,rss,args'] and obs['actual_exit_code'] in (0,1) and not obs['outer_windows_guard_expired'],'targeted saved observation')
            for c in ['stdout','stderr']:pin(ROOT/obs[c],obs[c+'_sha256'])
            need('/'+key(D/'instance.cnf') not in (ROOT/obs['stdout']).read_text(),'no live exact formula in saved observation')
        for field in ['mount_receipt','disk_receipt']:
            rr=manifest[field];need(rr['actual_exit_code']==0 and not rr['outer_windows_guard_expired'],'proof location check')
            for c in ['stdout','stderr']:pin(ROOT/rr[c],rr[c+'_sha256'])
        need('ext4' in (ROOT/manifest['mount_receipt']['stdout']).read_text().split(),'actual ext4 location')
        need(int((ROOT/manifest['disk_receipt']['stdout']).read_text().split()[-1])==manifest['ext4_free_bytes'],'saved disk reading')
        need(transfer['native_hash_receipt']['command'][-2:]==['/usr/bin/sha256sum',transfer['linux_source']] and transfer['copy_receipt']['command'][-4:-1]==['/usr/bin/cp','--',transfer['linux_source']] and transfer['copy_receipt']['command'][-1].endswith('/'+key(proof)),'exact original/copy proof paths')
        corrupted=[]
        for name,t,r in [('wrong_header',text.replace('9532 162124','9532 171092'),receipt),('wrong_status',text.replace('s UNSATISFIABLE','s SATISFIABLE'),receipt),('duplicate_status',text+'s UNSATISFIABLE\n',receipt),('wrong_exit',text,{**receipt,'actual_exit_code':0}),('outer_timeout',text,{**receipt,'outer_windows_guard_expired':True}),('wrong_allocation',text.replace("1000000 conflicts (due to '1000000')","1000000 conflicts (due to '2')"),receipt)]:
            try:parse(t,r)
            except ValueError:corrupted.append(name)
            else:raise ValueError('accepted corrupted receipt '+name)
        up=unit_propagation(read_cnf(D/'instance.cnf'));save(out/'unit_propagation.json',up)
        need(unit_propagation([[1],[-1]])['contradiction'] and not unit_propagation([[1,2],[-1,2]])['contradiction'] and not unit_propagation([[1,2],[1,-2],[-1,2],[-1,-2]])['contradiction'],'independent unit propagation controls')
        fixtures={'tiny_unsat.cnf':b'p cnf 2 4\n1 2 0\n1 -2 0\n-1 2 0\n-1 -2 0\n','tiny_sat.cnf':b'p cnf 2 3\n1 2 0\n1 -2 0\n-1 2 0\n','tiny_valid.drat':b'-2 0\n1 0\n0\n','empty_only.drat':b'0\n','fresh_unit.drat':b'3 0\n0\n'}
        for name,contents in fixtures.items():(out/name).write_bytes(contents)
        clauses=[(1,2),(1,-2),(-1,2),(-1,-2)]
        oracle=lambda cs:[b for b in range(4) if all(any(bool(b&(1<<(abs(v)-1)))==(v>0) for v in c) for c in cs)]
        need(oracle(clauses)==[] and oracle(clauses[:-1])==[3],'complete tiny truth calibration')
        tests=[('positive_reasoning',out/'tiny_unsat.cnf',out/'tiny_valid.drat',True),('missing_reasoning',out/'tiny_unsat.cnf',out/'empty_only.drat',False),('fresh_unit',out/'tiny_unsat.cnf',out/'fresh_unit.drat',False),('changed_SAT_input',out/'tiny_sat.cnf',out/'tiny_valid.drat',False),('actual_input_empty_only',D/'instance.cnf',out/'empty_only.drat',up['contradiction']),('complete_eight_count_profile_proof',D/'instance.cnf',proof,True)]
        replays=[helper.replay(name,cnf,p,out,expected) for name,cnf,p,expected in tests]
        command=['wsl.exe','--distribution','Ubuntu-24.04','--exec','/usr/bin/ps','-C','cadical','-o','pid,ppid,comm,pcpu,rss,args'];proc=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=10)
        need(proc.returncode in [0,1] and (proc.returncode!=1 or len(proc.stdout.splitlines())<=1),'targeted process observation')
        (out/'process.stdout.log').write_text(proc.stdout,encoding='utf-8');(out/'process.stderr.log').write_text(proc.stderr,encoding='utf-8')
        observation=dict(timestamp=datetime.now(timezone.utc).isoformat(),command=command,exit_code=proc.returncode,stdout_sha256=sha(out/'process.stdout.log'),stderr_sha256=sha(out/'process.stderr.log'),exact_input_processes=[l for l in proc.stdout.splitlines() if '/'+key(D/'instance.cnf') in l],scope='This timestamped targeted process observation only.')
        save(out/'process_observation.json',observation)
        pin(ROOT/'acceleration/audit_20260930_hadamard_seven_profile_unsat.py','0fe8a566d32b30aff4cd7030901d80f490757e2fd9c76c26b5eb4b5762b83f95')
        pin(ROOT/'acceleration/audit_20260930_eight_count_profile_unsat.py','136ac31432df596de62352df874215e7200d9198a3f5253824a8cf9f207614bf')
        for p in [Path(__file__),ROOT/'docs/AUDIT_20260930_SECOND_EIGHT_COUNT_PROFILE_UNSAT.md']:pin(p)
        ts=datetime.now(timezone.utc).isoformat();proof_record=dict(path=key(proof),sha256=PINS[proof],bytes=1269209,complete_independent_replay=True,availability='LOCAL_ONLY',availability_reason='Complete raw artifact is below10MiB and ready for parent publication; current local presence is not a public availability claim.')
        limitations=['Only the literal count_master_second_native_sat_after_six_cuts count profile on this fixed support; no orbit transfer, other profile or whole-support conclusion.','Within-group column caps are premises of the encoded domains. Cross-group caps and residualD are omitted.','The exact proof checker, reviewed Windows portability shim, compiler and runtime remain trusted; no diverse or formal checker claim.','Solver correctness is not a premise of the proof result.','Previously verified count-master and interval witnesses remain valid for their weaker necessary models.']
        statement='No binary 36x60 factor on the frozen six-prism Hadamard support has the prescribed integer Gram, within-triple column caps, and literal eight-exception profile count_master_second_native_sat_after_six_cuts (digest 086fc4155012236d30b13756b01e48ed2050db7cf028274b4aea533333ef0f17), with exceptional groups 1, 3, 5, 11, 13, 15, 18, 19. The exact equivalent formula with 9,532 variables and 162,124 clauses is UNSAT by complete independently replayed DRAT proof.'
        binding=dict(id='C-FIXED-HADAMARD-SECOND-EIGHT-COUNT-PROFILE-EXCLUSION',revision=1,kind='exclusion',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',statement=statement,scope=limitations[0],assumptions=['Pinned fixed support and literal count_master_second_native_sat_after_six_cuts count profile.','Within-triple column caps.','No target automorphism assumption.'],dependencies=[dict(id=eb['id'],revision=1,relation='encoding_equivalence')],verifier='/root/structural_attack',producer='/root/eight_domain_audit (encoding), /root (native execution)',method='Complete raw DRAT replay against exact independently checked CNF, authenticated checker source/binary, positive/corrupt proof controls and native receipt validation.',shared_components=['Specialized from the frozen first-eight-profile audit, with optional absent conflict counter and independent raw unit-propagation calibration; that source specialized the frozen independent seven-profile receipt/control audit, itself adapted from the six-profile and case0 audits; reuses only independently authored checker-authentication and subprocess replay helpers from the balanced proof review.','Same source-authenticated DRAT-trim binary and compiler/runtime as earlier checks; no producer Python imports.'],inputs_sha256=pins,evidence_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},proof=proof_record,literal_profile={k:scope[k] for k in ['selected_profile_id','selected_profile_sha256','exceptional_groups','coordinate_fibre_deviations']},limitations=limitations,artifact_availability='LOCAL_ONLY',availability_reason='Awaiting parent publication.',external_review=None,external_review_reason='No external peer review asserted.',created_at=ts,updated_at=ts)
        save(out/'claim_binding.json',binding)
        report=dict(status='INDEPENDENT_SECOND_LITERAL_EIGHT_COUNT_PROFILE_UNSAT_PASS',timestamp=ts,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,outputs_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},proof=proof_record,checker_provenance=provenance,replays=replays,native_outcome=stats,unit_propagation=up,configured_limits=manifest['limits'],native_command=cmd,run_source_commit=manifest['source_commit'],native_receipt_corruptions_rejected=corrupted,process_observation=observation,claim_id=binding['id'],claim_revision=1,scope=limitations[0],new_solver_calls=0,target_resolution=False,elapsed_seconds=time.perf_counter()-started)
        save(out/'summary.json',report);print(json.dumps(dict(status=report['status'],summary_sha256=sha(out/'summary.json'),claim_binding_sha256=sha(out/'claim_binding.json'))))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e)));raise
if __name__=='__main__':main()
