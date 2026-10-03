"""Gated native pilot for component-capacity-aware binary24x60 Q1 factors."""
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import platform
import shutil
import subprocess
import sys
import native_20260930_unrestricted_full99 as helper
import native_20260930_proof_location as ext4

ROOT=helper.ROOT
DATA=ROOT/'acceleration/results/20260930_triangle_q1_capacity_cnf'
CNF,MODEL=DATA/'instance.cnf',DATA/'model.json'
SCOPE=DATA/'scope.json'
KERNEL=ROOT/'acceleration/results/20260930_triangle_factor_components/kernel_certificate.json'
KERNEL_SHA='34852bbae744a346c87843bdd76d1697767cbbc9d9ad0b2276e9c8ccba47e0e1'
CNF_SHA='4887d76a20e0303d17eb3b4071ac147b2c7e12ce1fca9ba861a3ba68e15f9543'
MODEL_SHA='e2593a30f6a0f4b9cd8cbe602477846f679e9d30aabb2d0b73d476a60cf2f870'
SCOPE_SHA='280097aa4894ea928ec9636d385a111d1bac5d15fdddcaa30a6c66cce00633ce'
SPEC=Path(__file__).with_name('native_20260930_triangle_q1_capacity_spec.md')
ENGINEERING_GATES=[
    ('acceleration/results/20260930_native_cli_calibration/summary.json','f5ff562aff2ec550a97685c7012b302e760314a6f3829d80d022e2a669e680eb','INDEPENDENT_NATIVE_CADICAL195_CLI_CALIBRATION_PASS'),
    ('acceleration/results/20260930_native_proof_location/summary.json','d1036cfcbe9b24e0f7ea6e0a3799968a5d9232e8167fb31b224211e5c845c619','NATIVE_EXT4_PROOF_PATH_CALIBRATION_PASS')]


def preflight(args):
    bindings={}
    for path,expected in [(CNF,CNF_SHA),(MODEL,MODEL_SHA),(SCOPE,SCOPE_SHA),(KERNEL,KERNEL_SHA),(helper.NATIVE,helper.NATIVE_SHA),(helper.CHECKER,helper.CHECKER_SHA)]:
        helper.require(helper.digest(path)==expected,'exact input/native identity: '+helper.key(path));bindings[helper.key(path)]=expected
    for name,expected,status in ENGINEERING_GATES:
        helper.checked_gate(ROOT/name,expected,status);bindings[name]=expected
    enc=helper.checked_gate(args.encoding_gate,args.encoding_gate_sha256,'INDEPENDENT_TRIANGLE_Q1_CAPACITY_CNF_ENCODING_PASS')
    for p,h in [(CNF,CNF_SHA),(MODEL,MODEL_SHA),(SCOPE,SCOPE_SHA),(KERNEL,KERNEL_SHA)]:helper.require(enc['inputs_sha256'][helper.key(p)]==h,'joint factor encoding gate scope binding')
    obj=helper.checked_gate(args.object_gate,args.object_gate_sha256,'INDEPENDENT_TRIANGLE_Q1_CAPACITY_OBJECT_CHECKER_CALIBRATION_PASS')
    for p,h in [(CNF,CNF_SHA),(MODEL,MODEL_SHA)]:helper.require(obj['inputs_sha256'][helper.key(p)]==h,'joint factor object gate scope binding')
    for p in [Path(__file__),SPEC,Path(helper.__file__),Path(ext4.__file__),ext4.SPEC,args.encoding_gate,args.object_gate,ROOT/'uv.lock',ROOT/'pyproject.toml']:bindings[helper.key(p)]=helper.digest(p)
    model=helper.read(MODEL);scope=helper.read(SCOPE)
    helper.require(model['schema']=='TRIANGLE_Q1_COMPONENT_CAPACITY_PREFIX_CNF_V1' and model['variables']==19686 and model['clauses']==68328,'dedicated factor schema/counts')
    helper.require(model['scope_sha256']==SCOPE_SHA and model['full_target_graph_encoded'] is False,'local factor scope')
    helper.require(scope['kernel_certificate_sha256']==KERNEL_SHA and model['complete36row_factor_encoded'] is False,'exact necessary component projection binding')
    helper.require(scope['C1_free'] is True and scope['C2_included'] is False and scope['D_included'] is False and scope['target_automorphism_assumed'] is False,'freeQ1 projection scope')
    with CNF.open('rb') as f:helper.require(f.readline()==b'p cnf 19686 68328\n','exact joint factor header')
    return bindings


def decode(assignment):
    model=helper.read(MODEL);helper.require(len(assignment)==19686,'complete native assignment')
    values={abs(x):int(x>0) for x in assignment};c=[r.copy() for r in model['known_incidence_rows']]
    for item in model['entry_variables']:c[item['row']][item['column']]=values[item['id']]
    helper.require(len(c)==24 and all(len(r)==60 and all(type(x)is int and x in (0,1) for x in r) for r in c),'decoded binary24x60shape')
    errors=[]
    for r in range(24):
        if sum(c[r])!=10:errors.append(['row_margin',r])
    for g in range(2):
        for d in range(60):
            if sum(c[r][d] for r in range(12*g,12*g+12))!=2:errors.append(['column_margin',g,d])
    for a in range(24):
        for b in range(a,24):
            if sum(c[a][d]*c[b][d] for d in range(60))!=model['target_gram_rows'][a][b]:errors.append(['gram',a,b])
    components=helper.read(KERNEL)['components']
    for i,component in enumerate(components):
        for d in range(60):
            if sum(c[a][d] for a in component if a<24)>2:errors.append(['component_capacity',i,d])
    edge_index={tuple(e):i for i,e in enumerate(helper.read(SCOPE)['edge_columns_C0'])}
    q=[]
    for d in range(60):
        pair=tuple(a-12 for a in range(12,24) if c[a][d])
        if pair not in edge_index:errors.append(['Q1_column_not_nonmatching_edge',d]);q.append(None)
        else:q.append(edge_index[pair])
    if any(x is None for x in q) or sorted(q)!=list(range(60)):errors.append(['Q1_not_permutation'])
    return {'status':'CANDIDATE_CAPACITY_Q1_PENDING_INDEPENDENT_CHECK','incidence_matrix':c,'Q1':q,'encoding_model_sha256':MODEL_SHA,'scope_sha256':SCOPE_SHA,'component_kernel_certificate_sha256':KERNEL_SHA,'producer_exact_check':{'valid':not errors,'error_count':len(errors),'first_errors':errors[:12]},'independent_approval':False,'is_full99_graph':False,'is_complete36row_factor':False}


def run(args):
    bindings=preflight(args);out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    host_free=shutil.disk_usage(ROOT).free;helper.require(host_free>=21*1024**3,'host free below21GiB')
    mount,mount_text=ext4.local_capture(['/usr/bin/findmnt','--target','/tmp','--output','TARGET,SOURCE,FSTYPE,OPTIONS','--noheadings'],out/'filesystem');helper.require('ext4' in mount_text.split(),'calibrated ext4 filesystem required')
    disk,disk_text=ext4.local_capture(['/usr/bin/df','--output=avail','-B1','/tmp'],out/'disk_free');helper.require(int(disk_text.splitlines()[-1])>=11*1024**3,'ext4 free below11GiB')
    helper.save(out/'manifest.json',{'timestamp':datetime.now(timezone.utc).isoformat(),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'command':[sys.executable,*sys.argv],'cwd':str(ROOT),'python':platform.python_version(),'inputs_sha256':bindings,'mode':'PREFLIGHT_ONLY' if args.preflight else 'RESEARCH','scope':'Binary24x60 Q1 factor with component capacity; C2 andD absent, no target graph.','limits':{'native_seconds':300,'conflicts':1000000,'address_space_bytes':ext4.AS_LIMIT,'file_bytes':ext4.FILE_LIMIT,'kill_after_seconds':5,'outer_windows_guard_seconds':320},'disk_free_host':host_free,'filesystem_receipt':mount,'ext4_disk_receipt':disk,'random_seed':None,'random_seed_null_reason':'Native default retained.','shared_components':['Frozen native parser/subprocess/ext4copy helpers','Pristine native executable and authenticated checker with prior calibrations'],'fixed_Q1_or_historical_UNSAT_premise':False})
    if args.preflight:
        helper.save(out/'summary.json',{'status':'TRIANGLE_Q1_CAPACITY_NATIVE_PREFLIGHT_PASS','research_calls':0,'new_encoding_object_gates_checked':True,'source_sha256':helper.digest(Path(__file__)),'scope':'Fixedcore jointfactor only','native_call_launched':False});print(json.dumps({'status':'TRIANGLE_Q1_CAPACITY_NATIVE_PREFLIGHT_PASS','research_calls':0}));return
    made,linux_dir=ext4.local_capture(['/usr/bin/mktemp','-d','/tmp/conway99-q1-capacity-XXXXXX'],out/'mktemp');helper.require(linux_dir.startswith('/tmp/conway99-q1-capacity-') and '\n' not in linux_dir,'exclusive proof directory')
    helper.save(out/'workspace.json',{'path':linux_dir,'preserved':True,'mktemp':made});folder=out/'main';folder.mkdir();linux_proof=linux_dir+'/proof.drat'
    command=ext4.command(300,[helper.linux(helper.NATIVE),'--no-binary','-c','1000000',helper.linux(CNF),linux_proof])
    helper.save(folder/'launch.json',{'timestamp':datetime.now(timezone.utc).isoformat(),'command':command,'cnf_sha256':CNF_SHA,'model_sha256':MODEL_SHA,'ext4_proof':linux_proof});print(json.dumps({'state':'Q1_CAPACITY_NATIVE_LAUNCHING','variables':19686,'clauses':68328,'native_seconds':300}),flush=True)
    receipt=helper.run_record(command,folder/'solver',320);result={'actual_exit_code':receipt['actual_exit_code'],'receipt':receipt,'research_calls':1,'status':'LOCAL_FACTOR_ARTIFACTS_PENDING_INDEPENDENT_REVIEW','target_resolution':False,'scope':'Necessary24row projection of one fixed39core only','automatic_retry':False}
    if not receipt['outer_windows_guard_expired']:
        try:
            result['proof_copy']=ext4.proof_copy(linux_proof,folder/'proof.drat',folder/'transfer');helper.require((folder/'proof.drat').stat().st_size<=ext4.FILE_LIMIT,'proof cap')
        except BaseException as e:result['proof_copy_failure']={'type':type(e).__name__,'message':str(e),'linux_original_retained':linux_proof}
        stdout=(folder/'solver.stdout.log').read_text()
        if any(x.strip()=='s SATISFIABLE' for x in stdout.splitlines()):
            try:
                assignment=helper.parse_sat_stdout(stdout,19686);helper.save(folder/'parsed_model.json',{'assignment':assignment});decoded=decode(assignment);helper.save(folder/'decoded_factor.json',decoded);result['producer_local_factor_check']=decoded['producer_exact_check']
            except BaseException as e:result['parse_decode_failure']={'type':type(e).__name__,'message':str(e)}
    else:result['linux_process_state']='UNKNOWN_AFTER_OUTER_GUARD'
    code=receipt['actual_exit_code'];result['interpreted_result']='LOCAL_FACTOR_SAT_RAW_UNCHECKED' if code==10 else 'FIXED_CORE_UNSAT_TRACE_UNCHECKED' if code==20 else 'UNKNOWN_NATIVE_OR_RESOURCE_OUTCOME'
    result['outputs_sha256']={helper.key(p):helper.digest(p) for p in folder.iterdir() if p.is_file()};result['limitations']=['SAT requires independent complete assignment/clause/integer24x60factor checking and does not construct99vertices.','UNSAT requires independent complete proof replay; any exclusion is this fixed core only.']
    helper.save(out/'summary.json',result);print(json.dumps({'actual_exit_code':code,'interpreted_result':result['interpreted_result'],'research_calls':1}),flush=True)


def main():
    ap=argparse.ArgumentParser();modes=ap.add_mutually_exclusive_group(required=True);modes.add_argument('--preflight',action='store_true');modes.add_argument('--research',action='store_true')
    for name in ('out','encoding-gate','object-gate'):ap.add_argument('--'+name,type=Path,required=True)
    for name in ('encoding-gate-sha256','object-gate-sha256'):ap.add_argument('--'+name,required=True)
    run(ap.parse_args())


if __name__=='__main__':main()


