"""Independent full DRAT replay for exactly the frozen Wave151 family.

No solver/encoding producer imports. This authenticates a previously built
drat-trim binary and its immutable source/build records; it does not claim
compiler diversity or a formal proof of the checker implementation.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
R = 'acceleration/results/'
CNF = R+'20260930_triangle_wave151_full99_cnf/instance.cnf'
PROOF = R+'20260930_wave151_triangle_native_pilot/main/proof.drat'
ENC = R+'20260930_independent_review/wave151_triangle_full99_cnf/summary.json'
PROP = R+'20260930_independent_review/triangle_q1_partial99/summary.json'
BUILD = 'build/rook-drat-checker/'
PINS = {
    'acceleration/audit_20260930_triangle_wave154_unsat.py':'b7b98d9da7986fac7c005fb9a6d4e5b9cd2811ea46a8ea75a6e7e34933e4b649',
    CNF:'24d6b14e08fcd10f390edf462f75a6bc160c91c863448adf72d076f2297fc27e',
    PROOF:'e53deda5d5b10b29b800481f9a7497034b7e8b08e023dea42a44f3863ad6384b',
    ENC:'e981efe0e234f130cd5bd378a669219c1e793c234b6991779993d9a57d940430',
    PROP:'bad7ddc51101377b8eaa284c650db8adcee5c261a0717073b90fc9e2347d7594',
    BUILD+'drat-trim.exe':'23d1613cb0b1ed491f4e723ff82492a8be6c349c2426d440412842c5246b90ac',
    BUILD+'build_manifest.json':'219e14aeb9efb7df5629cb45405b08d45b2613133207e92bd4f7c09a5b2211b7',
    BUILD+'build_receipt.json':'4862b4cc61fe2832943c988c5418cd85ae795924fd83a40482c0da4fb03b7e4b',
}

def digest(path):
    with Path(path).open('rb') as stream:
        return sha256(stream.read()).hexdigest()

def save(path, data):
    with Path(path).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(data, stream, indent=2)
        stream.write('\n')

def load(path):
    return json.loads((ROOT/path).read_text(encoding='utf-8'))

def bind(path, expected, records):
    got = digest(ROOT/path)
    if got != expected:
        raise ValueError(f'input hash mismatch {path}: {got}')
    records[path] = got

def authenticate(records):
    for path, expected in PINS.items():
        bind(path, expected, records)
    manifest, receipt = load(BUILD+'build_manifest.json'), load(BUILD+'build_receipt.json')
    assert receipt['exit_code'] == 0
    assert receipt['binary_sha256'] == PINS[BUILD+'drat-trim.exe']
    assert receipt['build_manifest_sha256'] == PINS[BUILD+'build_manifest.json']
    for filename, key in [('upstream-drat-trim.c','upstream_sha256'),
                          ('windows-portability.patch','patch_sha256'),
                          ('drat-trim.c','patched_source_sha256'),
                          ('build.cmd','build_script_sha256')]:
        bind(BUILD+filename, manifest[key], records)
    for filename,key in [('build_stdout.log','stdout_sha256'),('build_stderr.log','stderr_sha256')]:
        bind(BUILD+filename, receipt[key], records)
    bind('acceleration/audit_20260930_rook_drat_build_v1.py', receipt['source_auditor_sha256'], records)
    for pathkey, hashkey in [('compiler_path','compiler_sha256'),('environment_script_path','environment_script_sha256')]:
        assert digest(Path(manifest[pathkey])) == manifest[hashkey]
    upstream_cmd = ['git','-C','tools/drat-trim','show',manifest['upstream_commit']+':drat-trim.c']
    upstream = subprocess.check_output(upstream_cmd, cwd=ROOT)
    assert upstream == (ROOT/BUILD/'upstream-drat-trim.c').read_bytes()
    patch_cmd = ['git','show',manifest['patch_source_commit']+':'+manifest['patch_source_path']]
    patch = subprocess.check_output(patch_cmd,cwd=ROOT)
    assert patch == (ROOT/BUILD/'windows-portability.patch').read_bytes()
    # An explicit independent reconstruction of the only permitted source edit.
    # Every byte of checking logic outside this header/time portability block
    # must be identical to the immutable upstream Git blob.
    replacement = b'''#ifdef _WIN32
#include <windows.h>
#define getc_unlocked getc
#ifdef ERROR
#undef ERROR
#endif
#ifdef FAILED
#undef FAILED
#endif
static int gettimeofday(struct timeval *value, void *timezone_unused) {
  FILETIME file_time;
  ULARGE_INTEGER ticks;
  (void) timezone_unused;
  GetSystemTimeAsFileTime(&file_time);
  ticks.LowPart = file_time.dwLowDateTime;
  ticks.HighPart = file_time.dwHighDateTime;
  /* FILETIME counts 100 ns intervals since 1601-01-01. */
  ticks.QuadPart -= 116444736000000000ULL;
  value->tv_sec = (long) (ticks.QuadPart / 10000000ULL);
  value->tv_usec = (long) ((ticks.QuadPart % 10000000ULL) / 10ULL);
  return 0;
}
#else
#include <sys/time.h>
#endif
'''
    old = b'#include <sys/time.h>\n'
    assert upstream.count(old) == 1
    assert upstream.replace(old,replacement) == (ROOT/BUILD/'drat-trim.c').read_bytes()
    return dict(upstream_repository=manifest['upstream_repository'], upstream_commit=manifest['upstream_commit'],
                upstream_git_command=upstream_cmd,patch_git_command=patch_cmd,
                source_change='Only the explicit Windows header/getc/macro/time block; all checking logic byte-identical.',
                build_command=manifest['build_command'], compiler_path=manifest['compiler_path'],
                compiler_sha256=manifest['compiler_sha256'], source_sha256=manifest['patched_source_sha256'],
                binary_sha256=receipt['binary_sha256'], fresh_recompile_in_this_audit=False,
                reason='Authenticated and reused the preserved successful build; no diverse compilation claim.')

def replay(name, cnf, proof, out, expected):
    command=[str(ROOT/BUILD/'drat-trim.exe'),str(cnf),str(proof)]
    start=time.monotonic()
    run=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=120)
    for suffix,content in [('stdout.log',run.stdout),('stderr.log',run.stderr)]:
        (out/f'{name}.{suffix}').write_bytes(content)
    accepted=run.returncode == 0 and b's VERIFIED' in run.stdout
    rec=dict(name=name,command=command,working_directory=str(ROOT),timestamp=datetime.now(timezone.utc).isoformat(),
             exit_code=run.returncode,accepted=accepted,expected_acceptance=expected,
             elapsed_seconds=time.monotonic()-start,timeout_seconds=120,
             cnf_sha256=digest(cnf),proof_sha256=digest(proof),
             stdout=str((out/f'{name}.stdout.log').relative_to(ROOT)).replace('\\','/'),
             stdout_sha256=digest(out/f'{name}.stdout.log'),
             stderr=str((out/f'{name}.stderr.log').relative_to(ROOT)).replace('\\','/'),
             stderr_sha256=digest(out/f'{name}.stderr.log'))
    save(out/f'{name}.receipt.json',rec)
    print(json.dumps({'name':name,'accepted':accepted,'expected':expected,'exit':run.returncode}),flush=True)
    if accepted != expected:
        raise ValueError(f'control/replay mismatch: {name}')
    return rec

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',required=True)
    args=parser.parse_args()
    out=ROOT/args.out
    out.mkdir(parents=True,exist_ok=False)
    start=time.monotonic(); inputs={}
    provenance=authenticate(inputs)
    enc, prop=load(ENC),load(PROP)
    assert enc['status']=='INDEPENDENT_CONDITIONAL_WAVE151_TRIANGLE_FULL99_CNF_ENCODING_PASS'
    assert prop['status']=='INDEPENDENT_TRIANGLE_Q1_PARTIAL99_PROPAGATION_PASS'
    for path, expected in enc['inputs_sha256'].items():
        bind(path,expected,inputs)
    assert enc['inputs_sha256'][CNF] == PINS[CNF]
    assert (enc['variables'],enc['clauses'],enc['edge_variables']) == (429779,1487778,1928)
    for filename in ['manifest.json','summary.json','main/solver.receipt.json','main/solver.stdout.log','main/solver.stderr.log']:
        path=R+'20260930_wave151_triangle_native_pilot/'+filename
        inputs[path]=digest(ROOT/path)
    solver_manifest=load(R+'20260930_wave151_triangle_native_pilot/manifest.json')
    for path, expected in solver_manifest['inputs_sha256'].items():
        bind(path,expected,inputs)
    solver_summary=load(R+'20260930_wave151_triangle_native_pilot/summary.json')
    assert solver_summary['actual_exit_code']==20
    assert solver_summary['proof_copy']['sha256']==PINS[PROOF]
    assert solver_summary['proof_copy']['bytes']==(ROOT/PROOF).stat().st_size
    assert (ROOT/PROOF).read_bytes().isascii()
    assert (ROOT/CNF).read_bytes().splitlines()[0] == b'p cnf 429779 1487778'
    files={
        'tiny_unsat.cnf':b'p cnf 2 4\n1 2 0\n1 -2 0\n-1 2 0\n-1 -2 0\n',
        'tiny_sat.cnf':b'p cnf 2 3\n1 2 0\n1 -2 0\n-1 2 0\n',
        'tiny_valid.drat':b'-2 0\n1 0\n0\n',
        'invalid_empty_only.drat':b'0\n',
        'invalid_fresh_unit.drat':b'3 0\n0\n',
    }
    for name,data in files.items():
        (out/name).write_bytes(data)
    # Tiny formula truth-table oracle independent of both solver and checker.
    clauses=[(1,2),(1,-2),(-1,2),(-1,-2)]
    sats=lambda c:[bits for bits in range(4) if all(any(bool(bits&(1<<(abs(x)-1)))==(x>0) for x in row) for row in c)]
    assert sats(clauses)==[] and sats(clauses[:3])==[3]
    specs=[('positive_tiny',out/'tiny_unsat.cnf',out/'tiny_valid.drat',True),
           ('corrupt_missing_units',out/'tiny_unsat.cnf',out/'invalid_empty_only.drat',False),
           ('corrupt_fresh_unit',out/'tiny_unsat.cnf',out/'invalid_fresh_unit.drat',False),
           ('corrupt_formula_is_sat',out/'tiny_sat.cnf',out/'tiny_valid.drat',False),
           ('corrupt_main_empty_only',ROOT/CNF,out/'invalid_empty_only.drat',False),
           ('main_complete_proof',ROOT/CNF,ROOT/PROOF,True)]
    runs=[replay(name,cnf,proof,out,want) for name,cnf,proof,want in specs]
    # Rebind after all executions so mutation cannot be silently overlooked.
    for path, expected in list(inputs.items()):
        bind(path,expected,inputs)
    for path in [Path(__file__).relative_to(ROOT).as_posix(),'uv.lock','pyproject.toml']:
        inputs[path]=digest(ROOT/path)
    trace=(ROOT/PROOF).read_text(encoding='ascii').splitlines()
    additions=sum(bool(line.strip()) and not line.startswith('d ') for line in trace)
    result=dict(status='INDEPENDENT_FIXED_WAVE151_TRIANGLE_FULL99_UNSAT_PASS',
        claim_id='C-FIXED-WAVE151-TRIANGLE-FULL99-EXCLUSION',claim_revision=1,
        recommendation='VERIFIED',kind='exclusion',basis=['DERIVED','COMPUTED'],
        timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),
        verifier='/root/eight_domain_audit independent proof replay agent',
        verification_type='Complete independent artifact checking by authenticated DRAT checker, with separately audited encoding and propagation dependencies',
        statement='No symmetric binary zero-diagonal 99 by 99 matrix satisfying A^2 = 12I - A + 2J extends the exact frozen initial Wave151 triangle-root/Q1 partial graph. The exact 429779-variable, 1487778-clause completion CNF is UNSAT.',
        scope='Only the specified labelled Wave151 initial partial graph and its independently entailed 562 assignments. No universal triangle-factor containment or nontrivial target automorphism is assumed.',
        dependencies=[dict(id='C-FIXED-WAVE151-TRIANGLE-FULL99-CNF-ENCODING',revision=1,relation='encoding_equivalence'),
                      dict(id='C-TRIANGLE-FIXED-Q1-PARTIAL99-PROPAGATION',revision=1,relation='uses_result')],
        inputs_sha256=inputs,checker_provenance=provenance,controls_and_replay=runs,
        cnf_sha256=PINS[CNF],proof_sha256=PINS[PROOF],proof_bytes=(ROOT/PROOF).stat().st_size,
        ascii_trace_lines=len(trace),ascii_addition_lines=additions,ascii_deletion_lines=len(trace)-additions,
        variables=429779,clauses=1487778,edge_variables=1928,
        solver_engine='CaDiCaL 1.9.5 native Linux CLI',solver_command=solver_summary['receipt']['command'],
        solver_binary_sha256=solver_manifest['inputs_sha256']['build/research-cadical195/source/build/cadical'],
        solver_actual_exit_code=20,artifact_availability='LOCAL_ONLY',
        artifact_availability_reason='Complete trace, preserved checker source/build recipe and recovery packages exist locally; publication is controlled by the root agent.',
        target_resolution=False,external_review=False,elapsed_seconds=time.monotonic()-start,
        limitations=['This is a fixed-configuration exclusion, not a proof of unrestricted Conway-99 nonexistence.',
                     'DRAT-trim, its explicitly reviewed portability block, MSVC compilation, and Windows runtime remain trusted components.',
                     'The checker binary is authenticated from its prior preserved build, not independently recompiled in this replay.',
                     'Encoding and propagation mathematics rely on separately pinned independent audits; this replay does not rerun their full derivations.',
                     'Solver correctness is not trusted for UNSAT; the complete proof was checked independently.'])
    result['output_hashes']={p.relative_to(ROOT).as_posix():digest(p) for p in sorted(out.iterdir()) if p.is_file()}
    result['shared_checking_path']='Adapted the frozen independent Wave154 proof-audit source; same authenticated pristine-Git-source plus explicit portability-block checker build reused. All positive/corrupt controls and complete new proof replay run afresh. No solver or encoding producer imports, no new independent implementation or diverse compilation claim.'
    result['review_state']='CLEAR'
    save(out/'summary.json',result)
    print(json.dumps({'status':result['status'],'summary':str(out/'summary.json'),'sha256':digest(out/'summary.json')}))

if __name__=='__main__':
    main()

