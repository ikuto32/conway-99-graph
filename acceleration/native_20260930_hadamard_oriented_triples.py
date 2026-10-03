"""One gated native pilot for the fixed-support oriented-triple projection."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,platform,shutil,subprocess,sys
import native_20260930_unrestricted_full99 as h
import native_20260930_proof_location as e
import theory_20260930_hadamard_oriented_triples as producer
ROOT=h.ROOT
B=ROOT/'acceleration/results'
DATA=B/'20260930_hadamard_oriented_triples'
CNF=DATA/'instance.cnf'
MODEL=DATA/'model.json'
SCOPE=DATA/'scope.json'
SPEC=Path(__file__).with_suffix('.md')
PINS={CNF:'7501790d51166b0b62719c2db274cb2581c57ef584c282e333377e4b72060999',
MODEL:'81065b50b0caf2d8a5226570e321738faf47dabee7688f5cad96a17d1e72e5ee',
SCOPE:'88ef7bf36dfd86a749ae84ea045e9707e6c27deff9c21e861d25d80c3de7d2e4',
DATA/'summary.json':'6c4206132abde0b3d2144937d37a7b65fe2219d5f1a043f58f0dc82877427cac',
producer.RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',
Path(producer.__file__):'1decce90cd18105430dd102a9739f08f46690e2424a6d3837f8ae8d6173c7eac',
Path(producer.__file__).with_name('theory_20260930_hadamard_oriented_triples_spec.md'):'830f2da205da633b547b1ae62bca3103c5f3ac01bcf3301dd23954723450034b',
Path(h.__file__):'da7ee9c03d454bd5ad0af0d82bead3520f3f270c70e71d4355161d036fd8ef22',
Path(e.__file__):'ff7fd55658b7cb63e9586bd862f8f182269f2978a3b873ba9afccfa41a345854',
ROOT/'uv.lock':'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',
ROOT/'pyproject.toml':'273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339',
h.NATIVE:h.NATIVE_SHA,h.CHECKER:h.CHECKER_SHA}

def preflight(args):
    bindings={}
    for path,sha in PINS.items():
        h.require(h.digest(path)==sha,'frozen source/input/tool '+h.key(path))
        bindings[h.key(path)]=sha
    reports=[]
    for path,sha,status in [(args.encoding_gate,args.encoding_gate_sha256,'INDEPENDENT_HADAMARD_ORIENTED_TRIPLE_ENCODING_PASS'),
        (args.object_gate,args.object_gate_sha256,'INDEPENDENT_HADAMARD_ORIENTED_TRIPLE_OBJECT_CALIBRATION_PASS')]:
        report=h.checked_gate(path,sha,status);reports.append(report)
        for key,value in report['inputs_sha256'].items():
            h.require(h.digest(ROOT/key)==value,'unchanged audit input '+key);bindings[key]=value
        for p in [CNF,MODEL,SCOPE,producer.RAW,Path(producer.__file__),Path(producer.__file__).with_name('theory_20260930_hadamard_oriented_triples_spec.md')]:
            h.require(report['inputs_sha256'][h.key(p)]==PINS[p],'exact independent model binding')
        bindings[h.key(path)]=sha
    h.require(reports[1]['inputs_sha256'][h.key(args.encoding_gate)]==args.encoding_gate_sha256,'same encoding gate')
    for p in [Path(__file__),SPEC]:
        h.require(reports[1]['inputs_sha256'][h.key(p)]==h.digest(p),'object gate binds native driver/spec')
        bindings[h.key(p)]=h.digest(p)
    for name,sha,status in [('20260930_native_cli_calibration','f5ff562aff2ec550a97685c7012b302e760314a6f3829d80d022e2a669e680eb','INDEPENDENT_NATIVE_CADICAL195_CLI_CALIBRATION_PASS'),
        ('20260930_native_proof_location','d1036cfcbe9b24e0f7ea6e0a3799968a5d9232e8167fb31b224211e5c845c619','NATIVE_EXT4_PROOF_PATH_CALIBRATION_PASS')]:
        path=B/name/'summary.json';h.checked_gate(path,sha,status);bindings[h.key(path)]=sha
    h.require(CNF.read_bytes().splitlines()[0]==b'p cnf 800 109340','exact native instance')
    return bindings

def run(args):
    bindings=preflight(args);out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    h.require(shutil.disk_usage(ROOT).free>=21*1024**3,'host21GiB reserve')
    mount,mounttext=e.local_capture(['/usr/bin/findmnt','--target','/tmp','--output','TARGET,SOURCE,FSTYPE,OPTIONS','--noheadings'],out/'filesystem')
    h.require('ext4' in mounttext.split(),'ext4 temporary proof path')
    disk,disktext=e.local_capture(['/usr/bin/df','--output=avail','-B1','/tmp'],out/'disk_free')
    h.require(int(disktext.splitlines()[-1])>=11*1024**3,'ext4 11GiB reserve')
    h.save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,
        mode='PREFLIGHT' if args.preflight else 'RESEARCH',selection_rule='First native result for exact unmodified oriented-triple CNF; native default seed.',
        limits=dict(native_wall_seconds=60,conflicts=1000000,address_space_bytes=e.AS_LIMIT,trace_file_bytes=e.FILE_LIMIT,kill_after_seconds=5,outer_guard_seconds=70,maximum_research_calls=1,automatic_retry=False),
        cpu_limit=None,cpu_limit_null_reason='Calibrated wall guard; no separate CPU rlimit.',random_seed=None,random_seed_null_reason='Native default.',
        scope='All-mixed balanced local/even-phase projection on one fixed support. Odd offsets, outside caps and residual D omitted. No target resolution.',filesystem=mount,disk=disk))
    if args.preflight:
        h.save(out/'summary.json',dict(status='ORIENTED_TRIPLE_NATIVE_PREFLIGHT_PASS',research_calls=0));return
    receipt,directory=e.local_capture(['/usr/bin/mktemp','-d','/tmp/conway99-oriented-triples-XXXXXX'],out/'mktemp')
    h.require(directory.startswith('/tmp/conway99-oriented-triples-') and '\n' not in directory,'fresh workspace')
    h.save(out/'workspace.json',dict(path=directory,preserved=True,receipt=receipt))
    folder=out/'main';folder.mkdir();proof=directory+'/proof.drat'
    command=e.command(60,[h.linux(h.NATIVE),'--no-binary','-c','1000000',h.linux(CNF),proof])
    h.save(folder/'launch.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),command=command,cnf_sha256=PINS[CNF],ext4_proof=proof))
    print(json.dumps(dict(state='ORIENTED_TRIPLE_NATIVE_LAUNCH',wall_seconds=60)),flush=True)
    native=h.run_record(command,folder/'solver',70)
    result=dict(status='ORIENTED_TRIPLE_NATIVE_PENDING_INDEPENDENT_REVIEW',timestamp=datetime.now(timezone.utc).isoformat(),receipt=native,research_calls=1,target_resolution=False,automatic_retry=False)
    if not native['outer_windows_guard_expired']:
        try:result['proof_copy']=e.proof_copy(proof,folder/'proof.drat',folder/'transfer')
        except BaseException as error:result['proof_copy_failure']=dict(error=repr(error),original_path=proof,availability='UNKNOWN_PENDING_OBSERVATION')
        stdout=(folder/'solver.stdout.log').read_text(encoding='utf-8')
        if native['actual_exit_code']==10:
            try:
                assignment=h.parse_sat_stdout(stdout,800)
                h.save(folder/'parsed_model.json',dict(assignment=assignment))
                values={abs(lit):lit>0 for lit in assignment}
                for line in CNF.read_text(encoding='ascii').splitlines()[1:]:
                    literals=list(map(int,line.split()));h.require(literals[-1]==0,'CNF terminator')
                    h.require(any(values[abs(lit)]==(lit>0) for lit in literals[:-1]),'literal native assignment satisfies every clause')
                h.save(folder/'decoded_oriented_cover.json',producer.decode(assignment,MODEL,SCOPE))
            except BaseException as error:result['parse_decode_failure']=dict(error=repr(error))
    code=native['actual_exit_code']
    result['interpreted_result']='ORIENTED_COVER_SAT_UNCHECKED' if code==10 else 'ORIENTED_COVER_UNSAT_TRACE_UNCHECKED' if code==20 else 'UNKNOWN_NATIVE_OR_RESOURCE_OUTCOME'
    result['linux_process_state']='UNKNOWN_AFTER_OUTER_GUARD' if native['outer_windows_guard_expired'] else 'WRAPPED_COMMAND_RETURNED'
    result['outputs_sha256']={h.key(p):h.digest(p) for p in folder.iterdir() if p.is_file()}
    result['limitations']=['Independent complete cover checking required for SAT. No full factor or target graph follows.','UNSAT needs exact complete proof replay and checked subfamily coverage; never unrestricted nonexistence.','No numerical tolerances; UNKNOWN excludes nothing. Trace copy time is separately recorded, outside the native wall allocation.']
    h.save(out/'summary.json',result);print(json.dumps(dict(result=result['interpreted_result'],code=code)),flush=True)

def main():
    p=argparse.ArgumentParser();m=p.add_mutually_exclusive_group(required=True);m.add_argument('--preflight',action='store_true');m.add_argument('--research',action='store_true')
    for name in ['out','encoding-gate','object-gate']:p.add_argument('--'+name,type=Path,required=True)
    for name in ['encoding-gate-sha256','object-gate-sha256']:p.add_argument('--'+name,required=True)
    run(p.parse_args())
if __name__=='__main__':main()
