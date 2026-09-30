"""One gated bit-normalized coarse60 construction attempt; no self-approval of outcomes."""
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
import theory_20260930_prism_coarse60_decode as decoder

ROOT = helper.ROOT
D = ROOT / 'acceleration/results/20260930_prism_coarse60_bitlift'
MODEL, SCOPE = D/'model.json', D/'scope.json'
NORMAL = ROOT / 'acceleration/results/20260930_prism_coarse60_bitflip'
CNF, EXTENSION = NORMAL/'instance.cnf', NORMAL/'extension.json'
PINS = {CNF:'afa6581bfc3309e6c1ddb434996fb53aee712771fabaf2aef9432cfc30dc3c72',
        MODEL:'a437d3f1381e9554bff2376726a991f1d1e0ea23c240f8ebacf005c57e82fcb5',
        SCOPE:'3237da2a02c60fc3f0c61e562788582b7ce25946afb523a84dc6634912ed98e9',
        EXTENSION:'4838c853fc99f3ffbb3736aa234e30a3f2a6f90da67b1a50217c132efe2f8c83'}
SPEC = Path(__file__).with_name('native_20260930_prism_coarse60_bitflip_spec.md')
SECONDS, CONFLICTS, OUTER = 300, 2000000, 320


def preflight(args):
    bindings = {}
    exact = {**PINS, Path(helper.__file__):'da7ee9c03d454bd5ad0af0d82bead3520f3f270c70e71d4355161d036fd8ef22',
        Path(ext4.__file__):'ff7fd55658b7cb63e9586bd862f8f182269f2978a3b873ba9afccfa41a345854',
        Path(decoder.__file__):'3450e4009d2e4b98df71606c90334dbc4d3bb56915c0bbc7e4bb1dd7c1f70ace',
        helper.NATIVE:helper.NATIVE_SHA, helper.CHECKER:helper.CHECKER_SHA}
    for p, sha in exact.items():
        helper.require(helper.digest(p) == sha, 'frozen input/tool/source '+helper.key(p))
        bindings[helper.key(p)] = sha
    for name, sha, status in [
        ('acceleration/results/20260930_native_cli_calibration/summary.json','f5ff562aff2ec550a97685c7012b302e760314a6f3829d80d022e2a669e680eb','INDEPENDENT_NATIVE_CADICAL195_CLI_CALIBRATION_PASS'),
        ('acceleration/results/20260930_native_proof_location/summary.json','d1036cfcbe9b24e0f7ea6e0a3799968a5d9232e8167fb31b224211e5c845c619','NATIVE_EXT4_PROOF_PATH_CALIBRATION_PASS')]:
        helper.checked_gate(ROOT/name, sha, status)
        bindings[name] = sha
    enc = helper.checked_gate(args.encoding_gate, args.encoding_gate_sha256, 'INDEPENDENT_SIX_PRISM_COARSE60_BITFLIP_NORMALIZATION_PASS')
    obj = helper.checked_gate(args.object_gate, args.object_gate_sha256, 'INDEPENDENT_SIX_PRISM_COARSE60_BITFLIP_OBJECT_CHECKER_CALIBRATION_PASS')
    for gate in (enc, obj):
        for p, sha in PINS.items():
            helper.require(gate['inputs_sha256'][helper.key(p)] == sha, 'direct exact input binding')
        for p, sha in gate['inputs_sha256'].items():
            helper.require(helper.digest(ROOT/p) == sha, 'unchanged gate-bound input '+p)
            bindings[p] = sha
    helper.require(obj['inputs_sha256'][helper.key(args.encoding_gate)] == args.encoding_gate_sha256, 'object gate binds same encoding review')
    model, scope = helper.read(MODEL), helper.read(SCOPE)
    helper.require(model['variables'] == 5238 and model['clauses'] == 85698, 'exact dimensions')
    helper.require(scope['columns_each_once'] and scope['full_Gram_required'] and scope['all_distinct_column_caps_required'], 'all restricted requirements')
    helper.require(scope['no_complement_pairing'] and scope['no_target_automorphism_assumed'], 'no extra hidden pairing or automorphism')
    helper.require(not scope['residual_D_encoded'] and not scope['target_graph_encoded'] and not scope['unrestricted_prism_coverage'], 'restricted construction scope')
    extension = helper.read(EXTENSION)
    helper.require(extension['variables'] == 5238 and extension['clauses'] == 85704 and extension['appended_unit_literals'] == [-2449,-2450,-2451,-2452,-2453,-2454], 'exact six-unit normalization')
    helper.require(extension['base_model_sha256'] == PINS[MODEL] and extension['base_scope_sha256'] == PINS[SCOPE] and extension['group_size'] == 64 and extension['auxiliaries_regenerated'], 'normalization boundary')
    with CNF.open('rb') as stream:
        helper.require(stream.readline() == b'p cnf 5238 85704\n', 'exact CNF header')
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
        scope='Bit-normalized fixed six-prism60-distinct-pattern bit-lift with full Gram and all column caps; no residual D or unrestricted core coverage.',
        limits=dict(native_seconds=SECONDS, conflicts=CONFLICTS, address_space_bytes=ext4.AS_LIMIT, file_bytes=ext4.FILE_LIMIT,
            kill_after_seconds=5, outer_windows_guard_seconds=OUTER, maximum_research_attempts=1, automatic_retry=False),
        disk_free_host=free, filesystem_receipt=mount, ext4_disk_receipt=disk,
        random_seed=None, random_seed_null_reason='Native default retained.',
        shared_components=['Frozen authenticated native/parser/ext4 helpers and engineering controls.',
            'Producer decoder creates candidate output only; separate independent complete raw checker is required.']))
    if args.preflight:
        helper.save(out/'summary.json',dict(status='PRISM_COARSE60_BITFLIP_NATIVE_PREFLIGHT_PASS',research_calls=0,native_call_launched=False,source_sha256=helper.digest(__file__)))
        print(json.dumps(dict(status='PRISM_COARSE60_BITFLIP_NATIVE_PREFLIGHT_PASS',research_calls=0)))
        return
    made, directory = ext4.local_capture(['/usr/bin/mktemp','-d','/tmp/conway99-prism-coarse60-bitflip-XXXXXX'],out/'mktemp')
    helper.require(directory.startswith('/tmp/conway99-prism-coarse60-bitflip-') and '\n' not in directory,'fresh ext4 workspace')
    helper.save(out/'workspace.json',dict(path=directory,preserved=True,mktemp=made))
    folder = out/'main'
    folder.mkdir()
    proof = directory+'/proof.drat'
    command = ext4.command(SECONDS,[helper.linux(helper.NATIVE),'--no-binary','-c',str(CONFLICTS),helper.linux(CNF),proof])
    helper.save(folder/'launch.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),command=command,cnf_sha256=PINS[CNF],model_sha256=PINS[MODEL],ext4_proof=proof))
    print(json.dumps(dict(state='PRISM_COARSE60_BITFLIP_NATIVE_LAUNCHING',variables=5238,clauses=85704,seconds=SECONDS)),flush=True)
    receipt = helper.run_record(command,folder/'solver',OUTER)
    result = dict(status='PRISM_COARSE60_BITFLIP_NATIVE_ARTIFACTS_PENDING_INDEPENDENT_REVIEW',actual_exit_code=receipt['actual_exit_code'],
        receipt=receipt,research_calls=1,target_resolution=False,automatic_retry=False,
        scope='One fixed60-pattern bit-lift; no whole-core or target conclusion.')
    if not receipt['outer_windows_guard_expired']:
        try:
            result['proof_copy'] = ext4.proof_copy(proof,folder/'proof.drat',folder/'transfer')
            helper.require((folder/'proof.drat').stat().st_size <= ext4.FILE_LIMIT,'proof cap')
        except BaseException as error:
            result['proof_copy_failure'] = dict(type=type(error).__name__,message=str(error),linux_original_retained=proof)
        stdout = (folder/'solver.stdout.log').read_text()
        if any(line.strip() == 's SATISFIABLE' for line in stdout.splitlines()):
            try:
                assignment = helper.parse_sat_stdout(stdout,5238)
                helper.require(set([-2449,-2450,-2451,-2452,-2453,-2454]) <= set(assignment), 'six normalized raw bits are false')
                helper.save(folder/'parsed_model.json',dict(assignment=assignment))
                helper.save(folder/'decoded_factor.json',decoder.decode(assignment))
            except BaseException as error:
                result['parse_decode_failure'] = dict(type=type(error).__name__,message=str(error))
    else:
        result['linux_process_state'] = 'UNKNOWN_AFTER_OUTER_GUARD'
    code = receipt['actual_exit_code']
    result['interpreted_result'] = 'RESTRICTED_FACTOR_SAT_RAW_UNCHECKED' if code == 10 else 'RESTRICTED_TEMPLATE_UNSAT_TRACE_UNCHECKED' if code == 20 else 'UNKNOWN_NATIVE_OR_RESOURCE_OUTCOME'
    result['outputs_sha256'] = {helper.key(p):helper.digest(p) for p in folder.iterdir() if p.is_file()}
    result['limitations'] = ['Independent whole-assignment/clause/raw-factor/column-cap check is mandatory on SAT; residual D is absent.',
        'Complete independently checked UNSAT proof excludes only this60-pattern template, not all six-prism factors.',
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
