"""Freeze a command and its environment before a bounded research invocation.

The invoked workflow must provide its own limits/checkpoints. This recorder
never converts an exit code into a mathematical conclusion.
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess
import sys


def stamp():
    return datetime.now(timezone.utc).isoformat()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--protocol',type=Path,required=True)
    parser.add_argument('--input',type=Path,action='append',default=[])
    parser.add_argument('command',nargs=argparse.REMAINDER)
    args=parser.parse_args()
    command=args.command[1:] if args.command[:1]==['--'] else args.command
    if not command or args.out.exists():
        raise ValueError('Command and fresh output directory required')
    inputs=list(dict.fromkeys([args.protocol,Path(__file__),Path('uv.lock'),Path('pyproject.toml'),*args.input]))
    hashes={p.as_posix():sha256(p.read_bytes()).hexdigest() for p in inputs}
    args.out.mkdir(parents=True)
    def save(name,data):
        with (args.out/name).open('x',encoding='utf-8') as stream:
            json.dump(data,stream,indent=2)
            stream.write('\n')
    manifest=dict(schema_version=1,created_at=stamp(),
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        cwd=str(Path.cwd()),command=command,protocol=args.protocol.as_posix(),inputs_sha256=hashes,
        python=sys.version,platform=platform.platform(),
        dependencies={p:importlib.metadata.version(p) for p in ('numpy','scipy','highspy','PyYAML','tqdm')},
        hardware={'CPU':'13th Gen Intel(R) Core(TM) i9-13900K','physical_cores':24,'logical_processors':32,
            'GPU':'NVIDIA GeForce RTX 4090','driver':'616.56','GPU_memory_MiB':24564,
            'observation':'Get-CimInstance Win32_Processor and nvidia-smi on 2026-09-17 before this invocation'},
        numerical_configuration='Frozen in the hashed protocol, sources and child manifests; no changed thresholds.',
        seed='Parent checkpoint and exact candidate identities are among input artifacts; downstream manifest records random choices.',
        result='NOT_YET_EXECUTED',scope='Only the declared bounded experiment; no target resolution inferred.')
    save('manifest.json',manifest)
    started=stamp()
    with (args.out/'console.txt').open('x',encoding='utf-8') as log:
        result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=False)
    save('receipt.json',dict(started_at=started,finished_at=stamp(),command=command,cwd=str(Path.cwd()),
        returncode=result.returncode,console_sha256=sha256((args.out/'console.txt').read_bytes()).hexdigest(),
        inputs_unchanged=all(sha256(Path(p).read_bytes()).hexdigest()==h for p,h in hashes.items()),
        mathematical_conclusion_from_exit_code=False))
    print(json.dumps(dict(returncode=result.returncode,record=str(args.out))))
    raise SystemExit(result.returncode)


if __name__=='__main__':
    main()
