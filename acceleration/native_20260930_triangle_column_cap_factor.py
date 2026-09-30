"""Gated native pilot for target-column-cap fixed-core binary36x60 factors."""
from datetime import datetime, timezone
from itertools import combinations
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
DATA=ROOT/'acceleration/results/20260930_triangle_factor_column_caps'
CNF,MODEL=DATA/'instance.cnf',DATA/'model.json'
SCOPE=DATA/'scope.json'
KERNEL=ROOT/'acceleration/results/20260930_triangle_factor_components/kernel_certificate.json'
KERNEL_SHA='34852bbae744a346c87843bdd76d1697767cbbc9d9ad0b2276e9c8ccba47e0e1'
CNF_SHA='5a4f1972c74b6987ed05b2e2d19f1919fbe8426f02f4657faaf4b1e3ce1b92c6'
MODEL_SHA='2ac81d4e5f42cd6957b2361b440bcd79ce713f0078dba7140d2a3602f846570b'
SCOPE_SHA='e46b360d3e87c1bc0bbc1568262102b2c07d4d976b4fd7f41d6835b257052d45'
SPEC=Path(__file__).with_name('native_20260930_triangle_column_cap_factor_spec.md')
ENGINEERING_GATES=[
    ('acceleration/results/20260930_native_cli_calibration/summary.json','f5ff562aff2ec550a97685c7012b302e760314a6f3829d80d022e2a669e680eb','INDEPENDENT_NATIVE_CADICAL195_CLI_CALIBRATION_PASS'),
    ('acceleration/results/20260930_native_proof_location/summary.json','d1036cfcbe9b24e0f7ea6e0a3799968a5d9232e8167fb31b224211e5c845c619','NATIVE_EXT4_PROOF_PATH_CALIBRATION_PASS')]


def preflight(args):
    bindings={}
    for path,expected in [(CNF,CNF_SHA),(MODEL,MODEL_SHA),(SCOPE,SCOPE_SHA),(KERNEL,KERNEL_SHA),(helper.NATIVE,helper.NATIVE_SHA),(helper.CHECKER,helper.CHECKER_SHA)]:
        helper.require(helper.digest(path)==expected,'exact input/native identity: '+helper.key(path));bindings[helper.key(path)]=expected
    for name,expected,status in ENGINEERING_GATES:
        helper.checked_gate(ROOT/name,expected,status);bindings[name]=expected
    enc=helper.checked_gate(args.encoding_gate,args.encoding_gate_sha256,'INDEPENDENT_TRIANGLE_COLUMN_CAP_FACTOR_CNF_ENCODING_PASS')
    for p,h in [(CNF,CNF_SHA),(MODEL,MODEL_SHA),(SCOPE,SCOPE_SHA),(KERNEL,KERNEL_SHA)]:helper.require(enc['inputs_sha256'][helper.key(p)]==h,'joint factor encoding gate scope binding')
    obj=helper.checked_gate(args.object_gate,args.object_gate_sha256,'INDEPENDENT_TRIANGLE_COLUMN_CAP_FACTOR_OBJECT_CHECKER_CALIBRATION_PASS')
    for p,h in [(CNF,CNF_SHA),(MODEL,MODEL_SHA)]:helper.require(obj['inputs_sha256'][helper.key(p)]==h,'joint factor object gate scope binding')
    for p in [Path(__file__),SPEC,Path(helper.__file__),Path(ext4.__file__),ext4.SPEC,args.encoding_gate,args.object_gate,ROOT/'uv.lock',ROOT/'pyproject.toml']:bindings[helper.key(p)]=helper.digest(p)
    model=helper.read(MODEL);scope=helper.read(SCOPE)
    helper.require(model['schema']=='FIXED_TRIANGLE_FULL_FACTOR_COLUMN_CAP_PREFIX_CNF_V1' and model['variables']==61296 and model['clauses']==256320,'dedicated factor schema/counts')
    helper.require(model['scope_sha256']==SCOPE_SHA and model['full_target_graph_encoded'] is False,'local factor scope')
    helper.require(model['component_kernel_certificate_sha256']==KERNEL_SHA and model['appended_component_counters']==180,'exact component extension binding')
    helper.require(scope['abstract_gram_implies_column_caps_claimed'] is False and model['column_pair_overlap_upper_bound']==2,'new necessary target conditions, not Gram entailment')
    helper.require(len(model['column_cap_clauses'])==43740 and model['retained_component_base_clauses']==212580,'complete new suffix population')
    helper.require(scope['Q1_fixed'] is False and scope['Q2_fixed'] is False and scope['residual_D_included'] is False and scope['target_automorphism_assumed'] is False,'joint scope no extra fixed factor')
    with CNF.open('rb') as f:helper.require(f.readline()==b'p cnf 61296 256320\n','exact joint factor header')
    return bindings


def decode(assignment):
    model=helper.read(MODEL);helper.require(len(assignment)==61296,'complete native assignment')
    values={abs(x):int(x>0) for x in assignment};c=[r.copy() for r in model['known_incidence_rows']]
    for item in model['entry_variables']:c[item['row']][item['column']]=values[item['id']]
    helper.require(len(c)==36 and all(len(r)==60 and all(type(x)is int and x in (0,1) for x in r) for r in c),'decoded binary36x60shape')
    errors=[]
    for r in range(36):
        if sum(c[r])!=10:errors.append(['row_margin',r])
    for g in range(3):
        for d in range(60):
            if sum(c[r][d] for r in range(12*g,12*g+12))!=2:errors.append(['column_margin',g,d])
    for a in range(36):
        for b in range(a,36):
            if sum(c[a][d]*c[b][d] for d in range(60))!=model['target_gram_rows'][a][b]:errors.append(['gram',a,b])
    components=helper.read(KERNEL)['components']
    for i,component in enumerate(components):
        for d in range(60):
            if sum(c[a][d] for a in component)!=2:errors.append(['component_margin',i,d])
    for d,e in combinations(range(60),2):
        if sum(c[a][d]*c[a][e] for a in range(36))>2:errors.append(['target_column_overlap',d,e])
    return {'status':'CANDIDATE_TARGET_COLUMN_CAP_FACTOR_PENDING_INDEPENDENT_CHECK','incidence_matrix':c,'encoding_model_sha256':MODEL_SHA,'scope_sha256':SCOPE_SHA,'component_kernel_certificate_sha256':KERNEL_SHA,'producer_exact_check':{'valid':not errors,'error_count':len(errors),'first_errors':errors[:12]},'independent_approval':False,'is_full99_graph':False}


def run(args):
    bindings=preflight(args);out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    host_free=shutil.disk_usage(ROOT).free;helper.require(host_free>=21*1024**3,'host free below21GiB')
    mount,mount_text=ext4.local_capture(['/usr/bin/findmnt','--target','/tmp','--output','TARGET,SOURCE,FSTYPE,OPTIONS','--noheadings'],out/'filesystem');helper.require('ext4' in mount_text.split(),'calibrated ext4 filesystem required')
    disk,disk_text=ext4.local_capture(['/usr/bin/df','--output=avail','-B1','/tmp'],out/'disk_free');helper.require(int(disk_text.splitlines()[-1])>=11*1024**3,'ext4 free below11GiB')
    helper.save(out/'manifest.json',{'timestamp':datetime.now(timezone.utc).isoformat(),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'command':[sys.executable,*sys.argv],'cwd':str(ROOT),'python':platform.python_version(),'inputs_sha256':bindings,'mode':'PREFLIGHT_ONLY' if args.preflight else 'RESEARCH','scope':'Joint binary36x60factor with target column caps for one fixed39core; no residualD, no target graph.','limits':{'native_seconds':300,'conflicts':1000000,'address_space_bytes':ext4.AS_LIMIT,'file_bytes':ext4.FILE_LIMIT,'kill_after_seconds':5,'outer_windows_guard_seconds':320},'disk_free_host':host_free,'filesystem_receipt':mount,'ext4_disk_receipt':disk,'random_seed':None,'random_seed_null_reason':'Native default retained.','shared_components':['Frozen native parser/subprocess/ext4copy helpers','Pristine native executable and authenticated checker with prior calibrations'],'fixed_Q1_or_historical_UNSAT_premise':False})
    if args.preflight:
        helper.save(out/'summary.json',{'status':'TRIANGLE_COLUMN_CAP_FACTOR_NATIVE_PREFLIGHT_PASS','research_calls':0,'new_encoding_object_gates_checked':True,'source_sha256':helper.digest(Path(__file__)),'scope':'Fixedcore jointfactor only','native_call_launched':False});print(json.dumps({'status':'TRIANGLE_COLUMN_CAP_FACTOR_NATIVE_PREFLIGHT_PASS','research_calls':0}));return
    made,linux_dir=ext4.local_capture(['/usr/bin/mktemp','-d','/tmp/conway99-column-cap-factor-XXXXXX'],out/'mktemp');helper.require(linux_dir.startswith('/tmp/conway99-column-cap-factor-') and '\n' not in linux_dir,'exclusive proof directory')
    helper.save(out/'workspace.json',{'path':linux_dir,'preserved':True,'mktemp':made});folder=out/'main';folder.mkdir();linux_proof=linux_dir+'/proof.drat'
    command=ext4.command(300,[helper.linux(helper.NATIVE),'--no-binary','-c','1000000',helper.linux(CNF),linux_proof])
    helper.save(folder/'launch.json',{'timestamp':datetime.now(timezone.utc).isoformat(),'command':command,'cnf_sha256':CNF_SHA,'model_sha256':MODEL_SHA,'ext4_proof':linux_proof});print(json.dumps({'state':'COLUMN_CAP_FACTOR_NATIVE_LAUNCHING','variables':61296,'clauses':256320,'native_seconds':300}),flush=True)
    receipt=helper.run_record(command,folder/'solver',320);result={'actual_exit_code':receipt['actual_exit_code'],'receipt':receipt,'research_calls':1,'status':'LOCAL_FACTOR_ARTIFACTS_PENDING_INDEPENDENT_REVIEW','target_resolution':False,'scope':'Binary factors with necessary target column caps for one fixed39core only','automatic_retry':False}
    if not receipt['outer_windows_guard_expired']:
        try:
            result['proof_copy']=ext4.proof_copy(linux_proof,folder/'proof.drat',folder/'transfer');helper.require((folder/'proof.drat').stat().st_size<=ext4.FILE_LIMIT,'proof cap')
        except BaseException as e:result['proof_copy_failure']={'type':type(e).__name__,'message':str(e),'linux_original_retained':linux_proof}
        stdout=(folder/'solver.stdout.log').read_text()
        if any(x.strip()=='s SATISFIABLE' for x in stdout.splitlines()):
            try:
                assignment=helper.parse_sat_stdout(stdout,61296);helper.save(folder/'parsed_model.json',{'assignment':assignment});decoded=decode(assignment);helper.save(folder/'decoded_factor.json',decoded);result['producer_local_factor_check']=decoded['producer_exact_check']
            except BaseException as e:result['parse_decode_failure']={'type':type(e).__name__,'message':str(e)}
    else:result['linux_process_state']='UNKNOWN_AFTER_OUTER_GUARD'
    code=receipt['actual_exit_code'];result['interpreted_result']='LOCAL_FACTOR_SAT_RAW_UNCHECKED' if code==10 else 'FIXED_CORE_UNSAT_TRACE_UNCHECKED' if code==20 else 'UNKNOWN_NATIVE_OR_RESOURCE_OUTCOME'
    result['outputs_sha256']={helper.key(p):helper.digest(p) for p in folder.iterdir() if p.is_file()};result['limitations']=['SAT requires independent complete assignment/clause/integer36x60factor checking and does not construct99vertices.','UNSAT requires independent complete proof replay; any exclusion is this fixed core only.']
    helper.save(out/'summary.json',result);print(json.dumps({'actual_exit_code':code,'interpreted_result':result['interpreted_result'],'research_calls':1}),flush=True)


def main():
    ap=argparse.ArgumentParser();modes=ap.add_mutually_exclusive_group(required=True);modes.add_argument('--preflight',action='store_true');modes.add_argument('--research',action='store_true')
    for name in ('out','encoding-gate','object-gate'):ap.add_argument('--'+name,type=Path,required=True)
    for name in ('encoding-gate-sha256','object-gate-sha256'):ap.add_argument('--'+name,required=True)
    run(ap.parse_args())


if __name__=='__main__':main()

