"""Gated native pilot for all abstract factors of the fixed six-prism Gram."""
from datetime import datetime,timezone
from itertools import combinations
from pathlib import Path
import argparse
import importlib.util
import json
import platform
import shutil
import subprocess
import sys
import native_20260930_unrestricted_full99 as helper
import native_20260930_proof_location as ext4

ROOT=helper.ROOT
DATA=ROOT/'acceleration/results/20260930_prism_all_columns'
CNF,MODEL=DATA/'instance.cnf',DATA/'model.json'
CNF_SHA='d45b7e9837ed02b669f3681aaa8a63af78ff46487e968c59cf47cd7a49e53d6f'
MODEL_SHA='a801e721a4c03d18e2fa9711a60f053895a4bfb8898b264f5174bcc36265f038'
ENCODING_SHA='07c589160e930205bc7e42f9524846280b4a8f0573ca9e5dfa06b627a6d115c3'
PRODUCER=ROOT/'acceleration/theory_20260930_prism_all_columns.py'
PRODUCER_SHA='4cd41ad4a75a50c196567860fb6a367f5981b584fd0f525c4c8eed281c2f754f'
SPEC=Path(__file__).with_name('native_20260930_prism_all_columns_spec.md')
ENGINEERING_GATES=[
 ('acceleration/results/20260930_native_cli_calibration/summary.json','f5ff562aff2ec550a97685c7012b302e760314a6f3829d80d022e2a669e680eb','INDEPENDENT_NATIVE_CADICAL195_CLI_CALIBRATION_PASS'),
 ('acceleration/results/20260930_native_proof_location/summary.json','d1036cfcbe9b24e0f7ea6e0a3799968a5d9232e8167fb31b224211e5c845c619','NATIVE_EXT4_PROOF_PATH_CALIBRATION_PASS'),
]

def preflight(args):
    bindings={}
    def bind(p,expected=None):
        observed=helper.digest(p);helper.require(expected is None or observed==expected,'exact identity '+helper.key(p));bindings[helper.key(p)]=observed
    for p,sha in [(CNF,CNF_SHA),(MODEL,MODEL_SHA),(PRODUCER,PRODUCER_SHA),(helper.NATIVE,helper.NATIVE_SHA),(helper.CHECKER,helper.CHECKER_SHA)]:bind(p,sha)
    for name,sha,status in ENGINEERING_GATES:helper.checked_gate(ROOT/name,sha,status);bind(ROOT/name,sha)
    helper.require(args.encoding_gate_sha256==ENCODING_SHA,'exact independently checked encoding revision')
    enc=helper.checked_gate(args.encoding_gate,args.encoding_gate_sha256,'INDEPENDENT_SIX_PRISM_ALL_COLUMNS_CNF_ENCODING_PASS')
    obj=helper.checked_gate(args.object_gate,args.object_gate_sha256,'INDEPENDENT_SIX_PRISM_ALL_COLUMNS_OBJECT_CHECKER_CALIBRATION_PASS')
    for gate in [enc,obj]:
        for p,sha in [(CNF,CNF_SHA),(MODEL,MODEL_SHA)]:helper.require(gate['inputs_sha256'][helper.key(p)]==sha,'exact gate scope binding')
        for name,sha in gate['inputs_sha256'].items():bind(ROOT/name,sha)
    for p in [Path(__file__),SPEC,Path(helper.__file__),Path(ext4.__file__),ext4.SPEC,args.encoding_gate,args.object_gate,ROOT/'uv.lock',ROOT/'pyproject.toml']:bind(p)
    model=helper.read(MODEL)
    helper.require(model['schema']=='SIX_PRISM_COMPLETE_COLUMN_DOMAINS_V1'and model['variables']==245880 and model['clauses']==874800,'exact dedicated schema and dimensions')
    helper.require(len(model['choices'])==5760 and len(model['counter_rows'])==540,'complete encoded choice/equation populations')
    for field in ['outside_column_caps_encoded','residual_D_encoded','target_graph_encoded','symmetry_or_orbit_pruning','complement_pairing']:
        helper.require(model[field]is False,'scope '+field)
    with CNF.open('rb')as stream:helper.require(stream.readline()==b'p cnf 245880 874800\n','exact header')
    return bindings

def decode(assignment):
    helper.require(helper.digest(PRODUCER)==PRODUCER_SHA,'frozen producer decoder')
    model=helper.read(MODEL)
    # Producer decoder is used only for CANDIDATE output, never for independent approval.
    spec=importlib.util.spec_from_file_location('prism_all_columns_candidate_decoder',PRODUCER)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    decoded=module.decode(model,assignment)
    f=decoded['factor'];errors=[]
    helper.require(len(f)==36 and all(len(row)==60 and all(type(x)is int and x in(0,1)for x in row)for row in f),'literal decoded factor')
    for a in range(36):
        if sum(f[a])!=10:errors.append(['row_margin',a])
        for b in range(36):
            if sum(f[a][d]*f[b][d]for d in range(60))!=model['target_gram'][a][b]:errors.append(['Gram',a,b])
    for d in range(60):
        for g in range(3):
            if sum(f[a][d]for a in range(12*g,12*g+12))!=2:errors.append(['cell_margin',g,d])
        for c,rows in enumerate(model['components']):
            if sum(f[a][d]for a in rows)!=1:errors.append(['component_margin',c,d])
    overlaps=[];violations=[]
    for d,e in combinations(range(60),2):
        q=sum(f[a][d]*f[a][e]for a in range(36));overlaps.append(q)
        if q>2:violations.append([d,e,q])
    return {**decoded,'status':'CANDIDATE_ABSTRACT_SIX_PRISM_FACTOR_PENDING_INDEPENDENT_CHECK','encoding_model_sha256':MODEL_SHA,
      'producer_exact_check':{'valid':not errors,'error_count':len(errors),'first_errors':errors[:12]},
      'outside_column_cap_diagnostic':{'encoded':False,'column_pairs':1770,'maximum_overlap':max(overlaps),'violations':violations,'passes_necessary_target_cap':not violations},
      'independent_approval':False,'residual_D':None,'residual_D_null_reason':'Residual adjacency is not encoded or constructed.','is_full99_graph':False}

def run(args):
    bindings=preflight(args);out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    host_free=shutil.disk_usage(ROOT).free;helper.require(host_free>=21*1024**3,'host free below21GiB')
    mount,mount_text=ext4.local_capture(['/usr/bin/findmnt','--target','/tmp','--output','TARGET,SOURCE,FSTYPE,OPTIONS','--noheadings'],out/'filesystem')
    helper.require('ext4'in mount_text.split(),'calibrated ext4 filesystem required')
    disk,disk_text=ext4.local_capture(['/usr/bin/df','--output=avail','-B1','/tmp'],out/'disk_free')
    helper.require(int(disk_text.splitlines()[-1])>=11*1024**3,'ext4 free below11GiB')
    helper.save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,
      mode='PREFLIGHT_ONLY'if args.preflight else'RESEARCH',scope='All abstract binary36x60 factors of the fixed six-prism Gram; outside-column caps and residual D unencoded; no unrestricted target coverage.',
      limits=dict(native_seconds=300,conflicts=1000000,address_space_bytes=ext4.AS_LIMIT,file_bytes=ext4.FILE_LIMIT,kill_after_seconds=5,outer_windows_guard_seconds=320),
      disk_free_host=host_free,filesystem_receipt=mount,ext4_disk_receipt=disk,random_seed=None,random_seed_null_reason='Native default retained.',
      shared_components=['Authenticated native parser/subprocess/ext4 copy helpers and prior engineering calibrations.','Producer decode(model, assignment) used only for explicitly candidate artifacts.','Separate independent raw-object checker gate required.'],automatic_retry=False))
    if args.preflight:
        helper.save(out/'summary.json',dict(status='SIX_PRISM_ALL_COLUMNS_NATIVE_PREFLIGHT_PASS',research_calls=0,encoding_and_object_gates_checked=True,source_sha256=helper.digest(Path(__file__)),native_call_launched=False,scope='One fixed six-prism abstract factor problem'))
        print(json.dumps(dict(status='SIX_PRISM_ALL_COLUMNS_NATIVE_PREFLIGHT_PASS',research_calls=0)));return
    made,linux_dir=ext4.local_capture(['/usr/bin/mktemp','-d','/tmp/conway99-prism-all-columns-XXXXXX'],out/'mktemp')
    helper.require(linux_dir.startswith('/tmp/conway99-prism-all-columns-')and'\n'not in linux_dir,'exclusive ext4 proof directory')
    helper.save(out/'workspace.json',dict(path=linux_dir,preserved=True,mktemp=made));folder=out/'main';folder.mkdir();linux_proof=linux_dir+'/proof.drat'
    command=ext4.command(300,[helper.linux(helper.NATIVE),'--no-binary','-c','1000000',helper.linux(CNF),linux_proof])
    helper.save(folder/'launch.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),command=command,cnf_sha256=CNF_SHA,model_sha256=MODEL_SHA,ext4_proof=linux_proof))
    print(json.dumps(dict(state='SIX_PRISM_ALL_COLUMNS_NATIVE_LAUNCHING',variables=245880,clauses=874800,native_seconds=300)),flush=True)
    receipt=helper.run_record(command,folder/'solver',320)
    result=dict(actual_exit_code=receipt['actual_exit_code'],receipt=receipt,research_calls=1,status='FIXED_SIX_PRISM_ARTIFACTS_PENDING_INDEPENDENT_REVIEW',target_resolution=False,scope='Abstract factors of one fixed six-prism core only; caps/D unencoded',automatic_retry=False)
    if not receipt['outer_windows_guard_expired']:
        try:
            result['proof_copy']=ext4.proof_copy(linux_proof,folder/'proof.drat',folder/'transfer');helper.require((folder/'proof.drat').stat().st_size<=ext4.FILE_LIMIT,'proof cap')
        except BaseException as error:result['proof_copy_failure']=dict(type=type(error).__name__,message=str(error),linux_original_retained=linux_proof)
        stdout=(folder/'solver.stdout.log').read_text()
        if any(line.strip()=='s SATISFIABLE'for line in stdout.splitlines()):
            try:
                assignment=helper.parse_sat_stdout(stdout,245880);helper.save(folder/'parsed_model.json',dict(assignment=assignment))
                decoded=decode(assignment);helper.save(folder/'decoded_factor.json',decoded);result['producer_local_factor_check']=decoded['producer_exact_check'];result['producer_column_cap_diagnostic']=decoded['outside_column_cap_diagnostic']
            except BaseException as error:result['parse_decode_failure']=dict(type=type(error).__name__,message=str(error))
    else:result['linux_process_state']='UNKNOWN_AFTER_OUTER_GUARD'
    code=receipt['actual_exit_code']
    result['interpreted_result']='ABSTRACT_FACTOR_SAT_RAW_UNCHECKED'if code==10 else'FIXED_SIX_PRISM_UNSAT_TRACE_UNCHECKED'if code==20 else'UNKNOWN_NATIVE_OR_RESOURCE_OUTCOME'
    result['outputs_sha256']={helper.key(p):helper.digest(p)for p in folder.iterdir()if p.is_file()}
    result['limitations']=['SAT requires independent complete assignment/all-clause/raw-factor validation; omitted column caps must be screened separately.','A factor is not a99vertex graph.','UNSAT requires a complete independently replayed proof and excludes only this fixed-core factor family.','UNKNOWN and incomplete traces prove no exclusion.']
    helper.save(out/'summary.json',result);print(json.dumps(dict(actual_exit_code=code,interpreted_result=result['interpreted_result'],research_calls=1)),flush=True)

def main():
    ap=argparse.ArgumentParser();mode=ap.add_mutually_exclusive_group(required=True)
    mode.add_argument('--preflight',action='store_true');mode.add_argument('--research',action='store_true')
    for name in('out','encoding-gate','object-gate'):ap.add_argument('--'+name,type=Path,required=True)
    for name in('encoding-gate-sha256','object-gate-sha256'):ap.add_argument('--'+name,required=True)
    run(ap.parse_args())

if __name__=='__main__':main()
