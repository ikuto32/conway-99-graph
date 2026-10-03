"""Prepared gated all-colouring fixed-Hadamard pilot; no target automorphism."""
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
import theory_20260930_hadamard_prism_ordered_cnf as decoder

ROOT = helper.ROOT
D = ROOT / 'acceleration/results/20260930_hadamard_prism_ordered_cnf'
CNF, MODEL, SCOPE = D/'instance.cnf', D/'model.json', D/'scope.json'
PINS = {CNF:'51cedaa0e54ab569e6ec4b8ad19fb17136ad5e8a9bdbd751b994903e4024f5df',
        MODEL:'85f2008d34c5f089e04e87306462a10be4919c582da6b6a2303523f5f6ea737a',
        SCOPE:'5d8cac247339006994035ac21c379edafdb8b55ec11213eba2ac22859430b466'}
SPEC = Path(__file__).with_name('native_20260930_hadamard_prism_ordered_spec.md')
SECONDS, CONFLICTS, OUTER = 300, 2000000, 320


def preflight(args):
    bindings = {}
    exact = {**PINS, Path(helper.__file__):'da7ee9c03d454bd5ad0af0d82bead3520f3f270c70e71d4355161d036fd8ef22',
        Path(ext4.__file__):'ff7fd55658b7cb63e9586bd862f8f182269f2978a3b873ba9afccfa41a345854',
        Path(decoder.__file__):'7520b147cc67ac0f01cd8a754ab3060ad6add27583e28f2cf8d7e065340fea8a',
        ROOT/'acceleration/native_20260930_hadamard_cyclic.py':'3fb70f4f00e9c4c608291463cdb2127dc4f784866bfbce49319b26d10c95bc67',
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
    enc = helper.checked_gate(args.encoding_gate, args.encoding_gate_sha256, 'INDEPENDENT_FIXED_SUPPORT_PRISM_ORDERED_COLORING_CNF_PASS')
    obj = helper.checked_gate(args.object_gate, args.object_gate_sha256, 'INDEPENDENT_FIXED_SUPPORT_PRISM_ORDERED_COLORING_OBJECT_CHECKER_CALIBRATION_PASS')
    for gate in (enc, obj):
        for p, sha in PINS.items():
            helper.require(gate['inputs_sha256'][helper.key(p)] == sha, 'direct exact input binding')
        for p, sha in gate['inputs_sha256'].items():
            helper.require(helper.digest(ROOT/p) == sha, 'unchanged gate-bound input '+p)
            bindings[p] = sha
    helper.require(obj['inputs_sha256'][helper.key(args.encoding_gate)] == args.encoding_gate_sha256, 'object gate binds same encoding review')
    model, scope = helper.read(MODEL), helper.read(SCOPE)
    helper.require(model['variables'] == 595464 and model['clauses'] == 3336642, 'exact dimensions')
    helper.require(model['primary_selectors'] == 5400 and len(model['counter_rows']) == 726, 'full all-colouring selector model')
    helper.require(not scope['cyclic_colour_constraint'] and scope['no_target_automorphism_assumed'], 'no cyclic restriction or target automorphism')
    helper.require(scope['strictly_increasing_option_rank'] and len(scope['adjacent_order_pairs']) == 40, 'audited column-rank normalization')
    helper.require(not scope['residual_D'] and not scope['target_graph'] and not scope['other_supports_covered'], 'no residual/core coverage assertion')
    helper.require(scope['source_raw_support_sha256'] == 'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d', 'exact fixed support')
    helper.require(helper.digest(ROOT/scope['source_raw_support']) == scope['source_raw_support_sha256'], 'unchanged fixed support')
    helper.require(scope['ordering_gate_sha256'] == '0ce1be9ca11a3e860aa97791cfb4f42c1660d937a69ac7a9b7d96ca37640c9d2', 'exact independent ordering premise')
    helper.require(helper.digest(ROOT/scope['ordering_gate_path']) == scope['ordering_gate_sha256'], 'ordering premise unchanged')
    bindings[scope['source_raw_support']] = scope['source_raw_support_sha256']
    bindings[scope['ordering_gate_path']] = scope['ordering_gate_sha256']
    with CNF.open('rb') as stream:
        helper.require(stream.readline() == b'p cnf 595464 3336642\n', 'exact CNF header')
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
        scope='All colourings of one fixed six-prism Hadamard support modulo audited identical-support column ordering; full Gram and column caps, no cyclic restriction, residual D or other-support coverage.',
        limits=dict(native_wall_seconds=SECONDS, cpu_seconds_limit=None,cpu_seconds_limit_null_reason='Existing calibrated wall-time guard retained; no CPU rlimit set.', conflicts=CONFLICTS, address_space_bytes=ext4.AS_LIMIT, file_bytes=ext4.FILE_LIMIT,
            kill_after_seconds=5, outer_windows_guard_seconds=OUTER, maximum_research_attempts=1, automatic_retry=False),
        disk_free_host=free, filesystem_receipt=mount, ext4_disk_receipt=disk,
        random_seed=None, random_seed_null_reason='Native default retained.',
        shared_components=['Frozen authenticated native/parser/ext4 helpers and engineering controls.',
            'Producer decoder creates candidate output only; separate independent complete raw checker is required.']))
    if args.preflight:
        helper.save(out/'summary.json',dict(status='HADAMARD_PRISM_ORDERED_NATIVE_PREFLIGHT_PASS',research_calls=0,native_call_launched=False,source_sha256=helper.digest(__file__)))
        print(json.dumps(dict(status='HADAMARD_PRISM_ORDERED_NATIVE_PREFLIGHT_PASS',research_calls=0)))
        return
    made, directory = ext4.local_capture(['/usr/bin/mktemp','-d','/tmp/conway99-hadamard-ordered-XXXXXX'],out/'mktemp')
    helper.require(directory.startswith('/tmp/conway99-hadamard-ordered-') and '\n' not in directory,'fresh ext4 workspace')
    helper.save(out/'workspace.json',dict(path=directory,preserved=True,mktemp=made))
    folder = out/'main'
    folder.mkdir()
    proof = directory+'/proof.drat'
    command = ext4.command(SECONDS,[helper.linux(helper.NATIVE),'--no-binary','-c',str(CONFLICTS),helper.linux(CNF),proof])
    helper.save(folder/'launch.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),command=command,cnf_sha256=PINS[CNF],model_sha256=PINS[MODEL],ext4_proof=proof))
    print(json.dumps(dict(state='HADAMARD_PRISM_ORDERED_NATIVE_LAUNCHING',variables=595464,clauses=3336642,wall_seconds=SECONDS)),flush=True)
    receipt = helper.run_record(command,folder/'solver',OUTER)
    result = dict(status='HADAMARD_PRISM_ORDERED_NATIVE_ARTIFACTS_PENDING_INDEPENDENT_REVIEW',actual_exit_code=receipt['actual_exit_code'],
        receipt=receipt,research_calls=1,target_resolution=False,automatic_retry=False,
        scope='All-colouring fixed-support factor model with audited column ordering; no residual D, whole-core or target conclusion.')
    if not receipt['outer_windows_guard_expired']:
        try:
            result['proof_copy'] = ext4.proof_copy(proof,folder/'proof.drat',folder/'transfer')
            helper.require((folder/'proof.drat').stat().st_size <= ext4.FILE_LIMIT,'proof cap')
        except BaseException as error:
            result['proof_copy_failure'] = dict(type=type(error).__name__,message=str(error),linux_original_retained=proof)
        stdout = (folder/'solver.stdout.log').read_text()
        if any(line.strip() == 's SATISFIABLE' for line in stdout.splitlines()):
            try:
                assignment = helper.parse_sat_stdout(stdout,595464)
                helper.save(folder/'parsed_model.json',dict(assignment=assignment))
                helper.save(folder/'decoded_factor.json',decoder.decode(assignment,MODEL,SCOPE))
            except BaseException as error:
                result['parse_decode_failure'] = dict(type=type(error).__name__,message=str(error))
    else:
        result['linux_process_state'] = 'UNKNOWN_AFTER_OUTER_GUARD'
    code = receipt['actual_exit_code']
    result['interpreted_result'] = 'RESTRICTED_FACTOR_SAT_RAW_UNCHECKED' if code == 10 else 'RESTRICTED_TEMPLATE_UNSAT_TRACE_UNCHECKED' if code == 20 else 'UNKNOWN_NATIVE_OR_RESOURCE_OUTCOME'
    result['outputs_sha256'] = {helper.key(p):helper.digest(p) for p in folder.iterdir() if p.is_file()}
    result['limitations'] = ['Independent whole-assignment/clause/raw-factor/column-cap check is mandatory on SAT; residual D is absent.',
        'Complete independently checked UNSAT proof plus exact encoding/order coverage gates excludes this fixed support, not other supports or the core.',
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
