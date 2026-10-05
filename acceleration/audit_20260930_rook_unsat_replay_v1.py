"""Fresh-source DRAT replay for the exact frozen-star local-window instance."""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT/'build/rook-drat-checker'
ENCODING = ROOT/'acceleration/results/20260930_rook_window_sat'
GATE = ENCODING/'independent_cnf_encoding.json'
GATE_HASH = 'bb4a98eef383ddfe2134992be41704945a65e694aac55296a4b62775bbfd6041'
PIN = '2e3b2dc0ecf938addbd779d42877b6ed69d9a985'


def need(condition,message):
    if not condition:
        raise ValueError(message)


def digest(path):
    value = sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):
            value.update(block)
    return value.hexdigest()


def key(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def save(path,value):
    with Path(path).open('x',encoding='utf-8') as stream:
        json.dump(value,stream,indent=2)
        stream.write('\n')


def parse_small(path):
    clauses = []
    with Path(path).open() as stream:
        header = stream.readline().split()
        need(header[:2] == ['p','cnf'],'small header')
        variables,count = map(int,header[2:])
        for line in stream:
            row = list(map(int,line.split()))
            need(row[-1] == 0,'small clause termination')
            clauses.append(row[:-1])
    need(len(clauses) == count and variables == 2,'calibration dimensions')
    satisfying = []
    for values in product((False,True),repeat=variables):
        if all(any(values[abs(lit)-1] == (lit>0) for lit in clause) for clause in clauses):
            satisfying.append(list(values))
    return satisfying


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--solver-run',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=False)
    tick = time.monotonic()
    bindings = {}
    def read(path):
        bindings[key(path)] = digest(path)
        return json.loads(Path(path).read_bytes())
    build = read(BUILD/'build_manifest.json')
    build_receipt = read(BUILD/'build_receipt.json')
    need(build['upstream_commit'] == PIN and build['dirty_submodule_source_consulted'] is False
         and build['dirty_submodule_mutated'] is False and build_receipt['exit_code'] == 0,'fresh checker source provenance')
    binary = BUILD/'drat-trim.exe'
    need(digest(binary) == build_receipt['binary_sha256'],'fresh checker binary binding')
    need(digest(BUILD/'upstream-drat-trim.c') == build['upstream_sha256']
         and digest(BUILD/'windows-portability.patch') == build['patch_sha256']
         and digest(BUILD/'drat-trim.c') == build['patched_source_sha256'],'checker source identities')
    upstream = subprocess.check_output(['git','-C',str(ROOT/'tools/drat-trim'),'show',PIN+':drat-trim.c'])
    need(sha256(upstream).hexdigest() == build['upstream_sha256'],'pinned Git blob independent reread')
    solver = read(args.solver_run/'manifest.json')
    receipt = read(args.solver_run/'main/receipt.json')
    need(receipt['solver_answer'] == 'UNSAT_PROOF_UNCHECKED' and receipt['proof_stream_finalized']
         and receipt['synthesized_empty_clause'] is False,'preserved native proof receipt')
    need(digest(GATE) == GATE_HASH,'independent encoding gate hash')
    gate = read(GATE)
    need(gate['status'] == 'INDEPENDENT_FROZEN_ROOK_STAR_WINDOW_CNF_ENCODING_PASS','encoding gate status')
    cnf = ENCODING/'instance.cnf'
    proof = args.solver_run/'main/proof.drat'
    need(digest(cnf) == receipt['cnf_sha256'] and digest(proof) == receipt['proof_sha256'],'exact CNF/proof receipt identity')
    bindings[key(cnf)] = digest(cnf)
    bindings[key(proof)] = digest(proof)
    for path,expected in solver['input_hashes'].items():
        actual_path = Path(path) if Path(path).is_absolute() else ROOT/path
        need(digest(actual_path) == expected,'solver input identity')
        bindings[key(actual_path)] = expected
    native = Path(solver['native_module_path'])
    need(digest(native) == solver['native_module_sha256'],'solver native extension identity')
    bindings[key(native)] = digest(native)
    build_copy = args.out/'checker_build'
    build_copy.mkdir()
    copied = []
    for name in ('upstream-drat-trim.c','windows-portability.patch','drat-trim.c','drat-trim.exe',
                 'build.cmd','build_manifest.json','build_receipt.json','build_stdout.log','build_stderr.log'):
        original = BUILD/name
        target = build_copy/name
        with target.open('xb') as stream:
            stream.write(original.read_bytes())
        need(digest(target) == digest(original),'checker package byte copy')
        bindings[key(original)] = digest(original)
        copied.append(dict(path=key(target),sha256=digest(target)))
    license_bytes = subprocess.check_output(['git','-C',str(ROOT/'tools/drat-trim'),'show',PIN+':LICENSE'])
    (build_copy/'LICENSE').write_bytes(license_bytes)
    copied.append(dict(path=key(build_copy/'LICENSE'),sha256=digest(build_copy/'LICENSE')))
    audit_manifest = dict(timestamp=datetime.now(timezone.utc).isoformat(),
                         source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                         command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),
                         inputs_sha256=dict(bindings),question='Does the complete preserved DRAT prove UNSAT for the independently encoded exact frozen-star CNF?',
                         scope=gate['scope'],checker_binary=key(binary),checker_binary_sha256=digest(binary),
                         checker_upstream_commit=PIN,checker_patched_source_sha256=build['patched_source_sha256'],
                         checker_command_limit_seconds=60,success='Fresh checker returns exit0 and an exact s VERIFIED line for complete proof; invalid empty-only proofs must be rejected',
                         calibration='Enumerate both2variable calibration CNFs directly; replay known valid proof; reject empty-only proof on calibration and exact main CNFs',
                         solver_engine=receipt['engine'],pysat_version=solver['pysat_version'],solver_native_sha256=solver['native_module_sha256'],
                         compiler='Microsoft C/C++19.44.35227 x64',compiler_binary_sha256=build['compiler_sha256'],
                         compiler_warnings='Two printf %li versus64bit argument warnings on diagnostic output lines834/836; unmodified checking logic. Complete compiler logs retained.',
                         dirty_submodule_modified=False,proof_producer_imported=False,target_resolution=False)
    save(args.out/'manifest.json',audit_manifest)

    def replay(name,instance,trace,should_accept):
        command = [str(binary),str(instance.resolve()),str(trace.resolve())]
        start = time.monotonic()
        process = subprocess.run(command,cwd=ROOT,capture_output=True,timeout=60)
        log = args.out/(name+'.log')
        log.write_bytes(process.stdout+process.stderr)
        accepted = process.returncode == 0 and b's VERIFIED' in (process.stdout+process.stderr).splitlines()
        row = dict(name=name,command=command,working_directory=str(ROOT),exit_code=process.returncode,
                   accepted=accepted,expected_acceptance=should_accept,elapsed_seconds=time.monotonic()-start,
                   cnf_sha256=digest(instance),proof_sha256=digest(trace),log_path=key(log),log_sha256=digest(log))
        save(args.out/(name+'.json'),row)
        need(accepted == should_accept,'checker calibration or main replay mismatch: '+name)
        return row

    sat = args.solver_run/'control_sat/instance.cnf'
    unsat = args.solver_run/'control_unsat/instance.cnf'
    tiny_proof = args.solver_run/'control_unsat/proof.drat'
    need(len(parse_small(sat)) > 0 and parse_small(unsat) == [],'independent small truth table')
    for path in (sat,unsat,tiny_proof):
        bindings[key(path)] = digest(path)
    invalid = args.out/'invalid_empty_only.drat'
    invalid.write_bytes(b'0\n')
    runs = [replay('positive_small_unsat',unsat,tiny_proof,True),
            replay('negative_small_empty',unsat,invalid,False),
            replay('negative_sat_empty',sat,invalid,False),
            replay('negative_main_empty',cnf,invalid,False),
            replay('main_complete_proof',cnf,proof,True)]
    need(all(digest(ROOT/path) == value for path,value in bindings.items()),'input stability')
    bindings[key(__file__)] = digest(__file__)
    with proof.open('rb') as stream:
        line_count = sum(1 for _ in stream)
    need(line_count == receipt['proof_lines'],'complete proof line count')
    result = dict(status='INDEPENDENT_FIXED_ROOK_STAR_WINDOW_UNSAT_PASS',
                  claim_id='C-ROOK-FIXED-STAR-WINDOW-EXCLUSION',claim_revision=1,recommendation='VERIFIED',
                  statement='No assignment of the600arbitrary labelled right-cell edges, forming four perfect-matchings and two bipartite2regular blocks, extends this exact frozen central star and five internal matchings while satisfying all known common-neighbor upper caps. Thus no Conway99target containing this exact fixed labelled star can exist.',
                  timestamp=datetime.now(timezone.utc).isoformat(),source_commit=audit_manifest['source_commit'],
                  command=audit_manifest['command'],working_directory=str(Path.cwd()),python=platform.python_version(),
                  verifier='/root/eight_domain_audit independent checking agent',verification_type='Independent raw DRAT replay using freshly built source-authenticated checker plus independent encoding equivalence',
                  inputs_sha256=bindings,cnf_sha256=digest(cnf),proof_sha256=digest(proof),proof_lines=line_count,
                  variables=18000,edge_variables=600,clauses=819840,proof_artifact=key(proof),cnf_artifact=key(cnf),
                  checker_upstream_repository=build['upstream_repository'],checker_upstream_commit=PIN,
                  checker_binary_sha256=digest(binary),checker_patched_source_sha256=build['patched_source_sha256'],
                  checker_build_manifest=key(BUILD/'build_manifest.json'),checker_package=copied,
                  solver_engine=receipt['engine'],pysat_version=solver['pysat_version'],solver_native_sha256=solver['native_module_sha256'],
                  controls_and_replay=runs,dependencies=[dict(id='C-ROOK-FIXED-STAR-WINDOW-CNF-ENCODING',revision=1,relation='encoding_equivalence'),
                                                     dict(id='C-ROOK-NINE-REGULAR-SET-ENCODING',revision=1,relation='normalization')],
                  scope=gate['scope'],proof_producer_imported=False,dirty_submodule_modified=False,
                  elapsed_seconds=time.monotonic()-tick,target_resolution=False,external_review=False,
                  artifact_availability='LOCAL_ONLY',artifact_availability_reason='Complete local source/binary/proof package preserved before publication',
                  limitations=['Excludes only the exact frozen central star with the five specified internal matchings; not all central factor stars or all rook-containing graphs.',
                               'No universal rook containment assumption and no unrestricted nonexistence result.',
                               'DRAT checker, explicit portability shim, MSVC compiler, and Windows runtime are trusted; no formal proof of these tools is claimed.',
                               'The producer used a separate earlier checker only for its calibration; this decisive replay used the freshly built checker recorded here.'])
    save(args.out/'summary.json',result)
    print(json.dumps(dict(status=result['status'],sha256=digest(args.out/'summary.json'),main_replay_accepted=runs[-1]['accepted'])))


if __name__ == '__main__':
    main()
