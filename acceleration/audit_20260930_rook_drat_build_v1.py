"""Build a fresh DRAT checker from pinned Git bytes, preserving dirty submodule."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'build/rook-drat-checker'
PIN = '2e3b2dc0ecf938addbd779d42877b6ed69d9a985'
COMPILER = Path('C:/Program Files/Microsoft Visual Studio/18/Community/VC/Tools/MSVC/14.44.35207/bin/Hostx64/x64/cl.exe')
VCVARS = Path('C:/Program Files/Microsoft Visual Studio/18/Community/VC/Auxiliary/Build/vcvars64.bat')


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def save(path,value):
    with path.open('x',encoding='utf-8') as stream:
        json.dump(value,stream,indent=2)
        stream.write('\n')


def main():
    OUT.mkdir(parents=True,exist_ok=False)
    head = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    original = subprocess.check_output(['git','-C',str(ROOT/'tools/drat-trim'),'show',PIN+':drat-trim.c'])
    patch = subprocess.check_output(['git','show',head+':tools/patches/drat-trim-windows.patch'],cwd=ROOT)
    # This immutable repository patch contains one ordinary unified hunk.
    # Apply only its exact before/after byte blocks, rejecting ambiguity.
    lines = patch.splitlines(keepends=True)
    starts = [i for i,line in enumerate(lines) if line.startswith(b'@@')]
    if len(starts) != 1:
        raise ValueError('unexpected portability patch format')
    body = lines[starts[0]+1:]
    if not all(line[:1] in (b' ',b'+',b'-') for line in body):
        raise ValueError('unexpected patch body')
    before = b''.join(line[1:] for line in body if line[:1] != b'+')
    after = b''.join(line[1:] for line in body if line[:1] != b'-')
    if original.count(before) != 1:
        raise ValueError('portability patch does not match pinned source exactly')
    patched = original.replace(before,after,1)
    for name,data in [('upstream-drat-trim.c',original),('windows-portability.patch',patch),('drat-trim.c',patched)]:
        with (OUT/name).open('xb') as stream:
            stream.write(data)
    executable = OUT/'drat-trim.exe'
    object_file = OUT/'drat-trim.obj'
    script = OUT/'build.cmd'
    body = '\r\n'.join(['@echo off',f'call "{VCVARS}" -vcvars_ver=14.44',
                       'if errorlevel 1 exit /b %errorlevel%',
                       f'"{COMPILER}" /O2 /std:c11 /TC /Fe:"{executable}" /Fo:"{object_file}" "{OUT / "drat-trim.c"}"',
                       'exit /b %errorlevel%',''])
    script.write_bytes(body.encode('utf-8'))
    command = ['cmd.exe','/d','/c',str(script)]
    manifest = dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=head,
                    command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),
                    question='Build a source-authenticated independent DRAT checker without using dirty working-tree source',
                    upstream_repository='https://github.com/marijnheule/drat-trim',upstream_commit=PIN,
                    upstream_blob_command=['git','-C','tools/drat-trim','show',PIN+':drat-trim.c'],
                    upstream_sha256=sha256(original).hexdigest(),patch_source_commit=head,
                    patch_source_path='tools/patches/drat-trim-windows.patch',patch_sha256=sha256(patch).hexdigest(),
                    patched_source_sha256=sha256(patched).hexdigest(),compiler_path=str(COMPILER),compiler_sha256=digest(COMPILER),
                    environment_script_path=str(VCVARS),environment_script_sha256=digest(VCVARS),
                    build_script=str(script),build_script_sha256=digest(script),build_command=command,build_seconds_limit=120,
                    portability_change='Only Windows headers, getc_unlocked-to-getc alias, macro conflict undefinitions, and gettimeofday shim. Original checking logic outside exact patch hunk unchanged.',
                    dirty_submodule_source_consulted=False,dirty_submodule_mutated=False,
                    limitations=['Windows portability patch remains a trusted reviewed source change.',
                                 'MSVC compilation and runtime are trusted components; this is not diverse compiler verification.'])
    save(OUT/'build_manifest.json',manifest)
    run = subprocess.run(command,cwd=OUT,capture_output=True,timeout=120)
    (OUT/'build_stdout.log').write_bytes(run.stdout)
    (OUT/'build_stderr.log').write_bytes(run.stderr)
    receipt = dict(timestamp=datetime.now(timezone.utc).isoformat(),exit_code=run.returncode,
                   binary_exists=executable.is_file(),binary_sha256=digest(executable) if executable.is_file() else None,
                   stdout_sha256=digest(OUT/'build_stdout.log'),stderr_sha256=digest(OUT/'build_stderr.log'),
                   build_manifest_sha256=digest(OUT/'build_manifest.json'),source_auditor_sha256=digest(__file__))
    save(OUT/'build_receipt.json',receipt)
    print(json.dumps(receipt))
    if run.returncode:
        print(run.stdout.decode(errors='replace'))
        print(run.stderr.decode(errors='replace'))
        raise SystemExit(run.returncode)


if __name__ == '__main__':
    main()
