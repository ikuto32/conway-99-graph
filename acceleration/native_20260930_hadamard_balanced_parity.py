"""Prepared tiny necessary balanced-parity projection pilot, not a factor search."""
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

ROOT = helper.ROOT
D = ROOT / 'acceleration/results/20260930_hadamard_balanced_parity'
CNF, MODEL = D/'instance.cnf', D/'model.json'
PINS = {CNF:'92801921a62236effa19b0f6e7463c6f5c1ca2cb0b6957cf7d315a73e0e43fca',
        MODEL:'a75b60c4ef0f8decd7537d70cced7bffa14cb7a4881de726bf98c96635888147'}
CYCLIC_EXCLUSION=ROOT/'acceleration/results/20260930_independent_review/hadamard_cyclic_unsat/summary.json'
CYCLIC_EXCLUSION_SHA='83029350b25523c015dfe916d8056324c0970021d2b024d68941dd41fb8c2b70'
SPEC = Path(__file__).with_name('native_20260930_hadamard_balanced_parity_spec.md')
SECONDS, CONFLICTS, OUTER = 60, 100000, 80


def decode_projection(assignment):
    model=helper.read(MODEL);values={}
    for lit in assignment:
        helper.require(type(lit)is int and lit!=0 and abs(lit) not in values,'complete unique literal IDs')
        values[abs(lit)]=int(lit>0)
    helper.require(set(values)==set(range(1,521)),'all520 values')
    records=[];selected=[];ranks=[];patterns=[]
    for j,group in enumerate(model['groups']):
        active=[i for i,v in enumerate(group['selectors']) if values[v]]
        helper.require(len(active)==1,'one parity pattern per group')
        index=active[0];selector=group['selectors'][index];pattern=group['parity_patterns'][index]
        selected.append(selector);ranks.append(index);patterns.append(pattern)
        records.append(dict(group=j,support=group['support'],selector=selector,pattern_index=index,
            parity_pattern=pattern,parity_mask_hex=format(sum(v<<k for k,v in enumerate(pattern)),'02x')))
    helper.require(len(records)==20 and any(i!=0 for i in ranks),'one noncyclic parity group')
    counts=[]
    for row in model['pair_rows']:
        a,b=row['coordinates'];differences=[]
        for term in row['terms']:
            j=term['group'];support=model['groups'][j]['support'];different=int(patterns[j][support.index(a)]!=patterns[j][support.index(b)])
            helper.require(values[term['difference_variable']]==different,'decoded auxiliary exact relation')
            differences.append(different)
        count=sum(differences);helper.require(count in (0,3),'necessary pair disagreement count')
        counts.append(dict(coordinates=[a,b],count=count))
    helper.require(len(counts)==60,'all60 coordinate pairs')
    return dict(selected_group_selector_ids=selected,selected_pattern_indices=ranks,selected_group_parity_patterns=patterns,
        group_records=records,pair_disagreement_counts=counts,model_sha256=PINS[MODEL],full_factor=False,target_graph=False,
        balance_is_additional_assumption=True,residual_D=None,independent_approval=False,
        scope='Parity-projection witness only; no colour-phase lift, full Gram factor, outside caps or residualD supplied.')


def preflight(args):
    bindings = {}
    exact = {**PINS, Path(helper.__file__):'da7ee9c03d454bd5ad0af0d82bead3520f3f270c70e71d4355161d036fd8ef22',
        Path(ext4.__file__):'ff7fd55658b7cb63e9586bd862f8f182269f2978a3b873ba9afccfa41a345854',
        ROOT/'acceleration/theory_20260930_hadamard_balanced_parity.py':'123b552a6dab179e475f8f0872d0a30831c1c9cf570f99c1027bc09b7c44d2ca',
        ROOT/'acceleration/theory_20260930_hadamard_balanced_parity_spec.md':'ca9caaead671fd654203c04ccd7d92d5485209b1657d8e4df5ca5b7ae7473d28',
        ROOT/'acceleration/native_20260930_hadamard_prism_ordered.py':'154a6ebdee0382cef0aaf2cec15faed1eb51799add32d202077a2cb052568254',
        CYCLIC_EXCLUSION:CYCLIC_EXCLUSION_SHA,
        ROOT/'uv.lock':'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',
        ROOT/'pyproject.toml':'273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339',
        helper.NATIVE:helper.NATIVE_SHA, helper.CHECKER:helper.CHECKER_SHA}
    for p, sha in exact.items():
        helper.require(helper.digest(p) == sha, 'frozen input/tool/source '+helper.key(p))
        bindings[helper.key(p)] = sha
    for name, sha, status in [
        ('acceleration/results/20260930_native_cli_calibration/summary.json','f5ff562aff2ec550a97685c7012b302e760314a6f3829d80d022e2a669e680eb','INDEPENDENT_NATIVE_CADICAL195_CLI_CALIBRATION_PASS'),
        ('acceleration/results/20260930_native_proof_location/summary.json','d1036cfcbe9b24e0f7ea6e0a3799968a5d9232e8167fb31b224211e5c845c619','NATIVE_EXT4_PROOF_PATH_CALIBRATION_PASS')]:
        helper.checked_gate(ROOT/name, sha, status)
        bindings[name] = sha
    enc = helper.checked_gate(args.encoding_gate, args.encoding_gate_sha256, 'INDEPENDENT_HADAMARD_BALANCED_PARITY_ENCODING_PASS')
    obj = helper.checked_gate(args.object_gate, args.object_gate_sha256, 'INDEPENDENT_HADAMARD_BALANCED_PARITY_OBJECT_CHECKER_CALIBRATION_PASS')
    for gate in (enc, obj):
        for p, sha in PINS.items():
            helper.require(gate['inputs_sha256'][helper.key(p)] == sha, 'direct exact input binding')
        for p, sha in gate['inputs_sha256'].items():
            helper.require(helper.digest(ROOT/p) == sha, 'unchanged gate-bound input '+p)
            bindings[p] = sha
    helper.require(obj['inputs_sha256'][helper.key(args.encoding_gate)] == args.encoding_gate_sha256, 'object gate binds same encoding review')
    model=helper.read(MODEL)
    helper.require(model['variables']==520 and model['clauses']==4481,'exact dimensions')
    helper.require(model['primary_selectors']==220 and len(model['groups'])==20 and len(model['pair_rows'])==60,'exact parity projection')
    helper.require(model['additional_balance_assumption'] and model['requires_noncyclic_group'],'explicit restricted assumptions')
    helper.require(not model['target_graph'] and not model['residual_D'],'no encoded full factor or target')
    helper.require(enc['inputs_sha256'][helper.key(CYCLIC_EXCLUSION)]==CYCLIC_EXCLUSION_SHA,'noncyclic-necessity premise binding')
    with CNF.open('rb') as stream:
        helper.require(stream.readline() == b'p cnf 520 4481\n', 'exact CNF header')
    for p in (Path(__file__), SPEC, args.encoding_gate, args.object_gate, ROOT/'uv.lock', ROOT/'pyproject.toml'):
        bindings[helper.key(p)] = helper.digest(p)
    return bindings


def run(args):
    bindings = preflight(args)
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    free = shutil.disk_usage(ROOT).free
    helper.require(free >= 21*1024**3, 'host disk reserve21GiB')
    mount, text = ext4.local_capture(['/usr/bin/findmnt','--target','/tmp','--output','TARGET,SOURCE,FSTYPE,OPTIONS','--noheadings'],out/'filesystem')
    helper.require('ext4' in text.split(), 'calibrated ext4 mount')
    disk, text = ext4.local_capture(['/usr/bin/df','--output=avail','-B1','/tmp'],out/'disk_free')
    helper.require(int(text.splitlines()[-1]) >= 11*1024**3, 'ext4 disk reserve11GiB')
    helper.save(out/'manifest.json', dict(timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(), command=[sys.executable,*sys.argv],
        working_directory=str(ROOT), python=platform.python_version(), inputs_sha256=bindings,
        mode='PREFLIGHT_ONLY' if args.preflight else 'RESEARCH',
        scope='Necessary parity projection for balanced triplets on one fixed support, with at least one noncyclic group. The final clause is necessary for balanced full factors with allYcaps using the prior cyclic exclusion; balance is not WLOG.',
        limits=dict(native_wall_seconds=SECONDS, cpu_seconds_limit=None,cpu_seconds_limit_null_reason='Existing calibrated wall-time guard retained; no CPU rlimit set.', conflicts=CONFLICTS, address_space_bytes=ext4.AS_LIMIT, file_bytes=ext4.FILE_LIMIT,
            kill_after_seconds=5, outer_windows_guard_seconds=OUTER, maximum_research_attempts=1, automatic_retry=False),
        disk_free_host=free, filesystem_receipt=mount, ext4_disk_receipt=disk,
        random_seed=None, random_seed_null_reason='Native default retained.',
        shared_components=['Frozen authenticated native/parser/ext4 helpers and engineering controls.',
            'Candidate decoder creates parity patterns only; a separate independent assignment/clause/projection checker is required.']))
    if args.preflight:
        helper.save(out/'summary.json',dict(status='HADAMARD_BALANCED_PARITY_NATIVE_PREFLIGHT_PASS',research_calls=0,native_call_launched=False,source_sha256=helper.digest(__file__)))
        print(json.dumps(dict(status='HADAMARD_BALANCED_PARITY_NATIVE_PREFLIGHT_PASS',research_calls=0)))
        return
    made, directory = ext4.local_capture(['/usr/bin/mktemp','-d','/tmp/conway99-hadamard-parity-XXXXXX'],out/'mktemp')
    helper.require(directory.startswith('/tmp/conway99-hadamard-parity-') and '\n' not in directory,'fresh ext4 workspace')
    helper.save(out/'workspace.json',dict(path=directory,preserved=True,mktemp=made))
    folder = out/'main'
    folder.mkdir()
    proof = directory+'/proof.drat'
    command = ext4.command(SECONDS,[helper.linux(helper.NATIVE),'--no-binary','-c',str(CONFLICTS),helper.linux(CNF),proof])
    helper.save(folder/'launch.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),command=command,cnf_sha256=PINS[CNF],model_sha256=PINS[MODEL],ext4_proof=proof))
    print(json.dumps(dict(state='HADAMARD_BALANCED_PARITY_NATIVE_LAUNCHING',variables=520,clauses=4481,wall_seconds=SECONDS)),flush=True)
    receipt = helper.run_record(command,folder/'solver',OUTER)
    result = dict(status='HADAMARD_BALANCED_PARITY_NATIVE_ARTIFACTS_PENDING_INDEPENDENT_REVIEW',actual_exit_code=receipt['actual_exit_code'],
        receipt=receipt,research_calls=1,target_resolution=False,automatic_retry=False,
        scope='Balanced/noncyclic necessary parity projection only; no full factor, whole-core or target conclusion.')
    if not receipt['outer_windows_guard_expired']:
        try:
            result['proof_copy'] = ext4.proof_copy(proof,folder/'proof.drat',folder/'transfer')
            helper.require((folder/'proof.drat').stat().st_size <= ext4.FILE_LIMIT,'proof cap')
        except BaseException as error:
            result['proof_copy_failure'] = dict(type=type(error).__name__,message=str(error),linux_original_retained=proof)
        stdout = (folder/'solver.stdout.log').read_text()
        if any(line.strip() == 's SATISFIABLE' for line in stdout.splitlines()):
            try:
                assignment = helper.parse_sat_stdout(stdout,520)
                helper.save(folder/'parsed_model.json',dict(assignment=assignment))
                helper.save(folder/'decoded_projection.json',decode_projection(assignment))
            except BaseException as error:
                result['parse_decode_failure'] = dict(type=type(error).__name__,message=str(error))
    else:
        result['linux_process_state'] = 'UNKNOWN_AFTER_OUTER_GUARD'
    code = receipt['actual_exit_code']
    result['interpreted_result'] = 'PARITY_PROJECTION_SAT_RAW_UNCHECKED' if code == 10 else 'PARITY_PROJECTION_UNSAT_TRACE_UNCHECKED' if code == 20 else 'UNKNOWN_NATIVE_OR_RESOURCE_OUTCOME'
    result['outputs_sha256'] = {helper.key(p):helper.digest(p) for p in folder.iterdir() if p.is_file()}
    result['limitations'] = ['SAT supplies parity patterns only; independent all-assignment/clause/projection checking is mandatory, and no fullGram factor or residualD follows.',
        'UNSAT requires a full independent trace replay and exact projection reduction. A balanced-factor exclusion additionally uses allYcaps and the separately checked cyclic-factor exclusion.',
        'Balance is an extra assumption, not WLOG. No whole-support, core or target exclusion follows directly.',
        'No UNKNOWN result or incomplete trace is an exclusion.']
    helper.save(out/'summary.json',result)
    print(json.dumps(dict(actual_exit_code=code,interpreted_result=result['interpreted_result'],research_calls=1)),flush=True)


def main():
    ap = argparse.ArgumentParser()
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument('--preflight',action='store_true')
    mode.add_argument('--research',action='store_true')
    for name in ('out','encoding-gate','object-gate'): ap.add_argument('--'+name,type=Path,required=True)
    for name in ('encoding-gate-sha256','object-gate-sha256'): ap.add_argument('--'+name,required=True)
    run(ap.parse_args())


if __name__ == '__main__': main()
