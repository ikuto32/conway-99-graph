"""Recover exact seventeenth inputs and prior checker sources; no executable build."""
from pathlib import Path
import argparse,gzip,hashlib,json
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_'
MANIFESTS={B+'hadamard_six_prism_cyclic_cnf/artifact_packages.json':'8cee7dceda5cf655df10bf9eb27ce936fb01ed3c60a135040d09eb697eb8ed82',
 B+'hadamard_prism_ordered_cnf/artifact_packages.json':'03f403dd97f96702a704d374de16685c6d8d798ac88fa5790d38b67ed64adcfa',
 B+'hadamard_cyclic_proof_packages/artifact_packages.json':'b6feaf43ddcd855294d4c8a86a9e7c88f975b15593f02aac6306ef9b40d958ca'}
CHECKER_SOURCE=B+'rook_sat_independent_proof/checker_build/'
CHECKER_TARGET='build/rook-drat-checker/'
CHECKER_FILES={'build_manifest.json':'219e14aeb9efb7df5629cb45405b08d45b2613133207e92bd4f7c09a5b2211b7',
 'build_receipt.json':'4862b4cc61fe2832943c988c5418cd85ae795924fd83a40482c0da4fb03b7e4b',
 'upstream-drat-trim.c':'d834b649f437e091597f5347f259b9f681087f89ca0844d0cee250a1a1a0c2ee',
 'windows-portability.patch':'2050f0b7ce9d4878944eecf6d94c414d8d60941a3e9f2df353ad30cd5316676c',
 'drat-trim.c':'82835512d4eda7dee1e0e3f610a0672fa1d216ea91246bcb576022020fe18f4c',
 'build.cmd':'c83b60af88ebbd92ef4fe554c851be35d8dfa4bea798b75941e6524c2597f456',
 'build_stdout.log':'9bca6aac2d4ec4663c7e7533a2a7804ae60aa9f6b6cbca8573746fd2195c7b17',
 'build_stderr.log':'9873a037014a27afc0ff96a6133e89a78294c6e2790e9c4a358ff12ebcb72e8a'}
def h(data):return hashlib.sha256(data).hexdigest()
def items(manifest):return manifest.get('packages',[manifest])
def decompress(package):
    parts=package.get('ordered_parts',package.get('parts'));chunks=[]
    if parts is not None:
        for part in parts:
            chunk=(ROOT/part['path']).read_bytes();assert len(chunk)==part['bytes'] and h(chunk)==part['sha256'];chunks.append(chunk)
        compressed=b''.join(chunks);assert h(compressed)==package.get('compressed_stream_sha256',package.get('compressed_sha256'))
    else:
        compressed=(ROOT/package['gzip_path']).read_bytes();assert len(compressed)==package['gzip_bytes'] and h(compressed)==package['gzip_sha256']
    raw=gzip.decompress(compressed);assert len(raw)==package['raw_bytes'] and h(raw)==package['raw_sha256'];return raw
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--destination-dir',type=Path);ap.add_argument('--receipt',type=Path);args=ap.parse_args();records=[]
    def write(relative,data,kind):
        path=Path(relative);assert not path.is_absolute() and '..' not in path.parts
        dest=((args.destination_dir or ROOT)/path).resolve();assert dest.is_relative_to(ROOT)
        if dest.exists():assert dest.read_bytes()==data,'Refuse differing destination'
        else:
            dest.parent.mkdir(parents=True,exist_ok=True)
            with dest.open('xb') as stream:stream.write(data)
        records.append(dict(path=str(dest),sha256=h(data),bytes=len(data),kind=kind))
    for path,pin in MANIFESTS.items():
        data=(ROOT/path).read_bytes();assert h(data)==pin
        for package in items(json.loads(data)):write(package['raw_path'],decompress(package),'lossless_gzip_recovery')
    for name,pin in CHECKER_FILES.items():
        raw=(ROOT/(CHECKER_SOURCE+name)).read_bytes();assert h(raw)==pin;write(CHECKER_TARGET+name,raw,'prior_public_exact_source_copy')
    result=dict(status='SEVENTEENTH_INPUT_RECOVERY_PASS',records=records,files=len(records),raw_bytes=sum(r['bytes'] for r in records),
        mathematical_verification=False,executable_provided=False,incomplete_ordered_trace_recovered=False)
    if args.receipt:
        with args.receipt.open('x',encoding='utf8',newline='\n') as stream:json.dump(result,stream,indent=2);stream.write('\n')
    print(json.dumps({k:v for k,v in result.items() if k!='records'}))
if __name__=='__main__':main()
