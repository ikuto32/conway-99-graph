"""Frozen fifteen-case formula build/byte-packaging launcher, never a solver."""
from datetime import datetime,timezone
from pathlib import Path
import argparse,gzip,hashlib,json,platform,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'acceleration/theory_20260930_hadamard_four_profile_cnf.py'
SPEC=ROOT/'acceleration/theory_20260930_hadamard_four_profile_cnf_spec.md'
SELECTION=ROOT/'acceleration/results/20260930_independent_review/hadamard_remaining_profile_universe/summary.json'
SELECTION_SHA='dffd4d638ee0cfca637a6ae4ba1a5cff5d7cb40d50f0dad2a9dd8f3ac79853ec'
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(p.read_bytes())
def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True,type=Path);args=p.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    try:
        need(sha(SELECTION)==SELECTION_SHA,'independent selection pin');selection=read(SELECTION);cases=selection['remaining_representatives'];need(len(cases)==15 and cases==sorted(set(cases)) and 0 not in cases,'frozen fifteen-case selection')
        inputs={key(p):sha(p) for p in [Path(__file__),SOURCE,SPEC,SELECTION,ROOT/'uv.lock',ROOT/'pyproject.toml']}
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=inputs,selected_cases=cases,limit_seconds=120,native_solver_calls=0))
        records=[]
        for case in cases:
            need(time.monotonic()-start<120,'cooperative total build allocation');dest=out/f'case_{case:03d}';command=[sys.executable,'-B',str(SOURCE),'--case',str(case),'--selection',str(SELECTION),'--selection-sha256',SELECTION_SHA,'--out',str(dest)];called=time.monotonic()
            result=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=max(1,120-(time.monotonic()-start)))
            stdout=out/f'case_{case:03d}.stdout.log';stderr=out/f'case_{case:03d}.stderr.log';stdout.write_bytes(result.stdout);stderr.write_bytes(result.stderr)
            receipt=out/f'case_{case:03d}.receipt.json';save(receipt,dict(command=command,cwd=str(ROOT),exit_code=result.returncode,wall_seconds=time.monotonic()-called,source_sha256=inputs[key(SOURCE)],stdout_sha256=sha(stdout),stderr_sha256=sha(stderr)))
            need(result.returncode==0,'single build failed; no retry');summary=read(dest/'summary.json');need(summary['selected_case']==case,'actual case summary')
            model=dest/'model.json';compressed=dest/'model.json.gz'
            with model.open('rb') as source,compressed.open('xb') as sink:
                with gzip.GzipFile(filename='',mode='wb',fileobj=sink,mtime=0) as encoded:
                    for block in iter(lambda:source.read(1048576),b''):encoded.write(block)
            recovered_hash=hashlib.sha256();recovered_bytes=0
            with gzip.open(compressed,'rb') as recovered:
                for block in iter(lambda:recovered.read(1048576),b''):recovered_hash.update(block);recovered_bytes+=len(block)
            need(recovered_hash.hexdigest()==sha(model) and recovered_bytes==model.stat().st_size,'full lossless model recovery')
            package=dest/'model_package.json';save(package,dict(raw_path=key(model),raw_sha256=sha(model),raw_bytes=model.stat().st_size,gzip_path=key(compressed),gzip_sha256=sha(compressed),gzip_bytes=compressed.stat().st_size,recovered_sha256=recovered_hash.hexdigest(),recovered_bytes=recovered_bytes,method='Complete streamed gzip decompression and SHA256/byte count equality.',retrieval='Decompress the referenced model.json.gz to model.json before replay; original raw model retained locally.',artifact_availability='LOCAL_ONLY'))
            records.append(dict(case=case,summary_path=key(dest/'summary.json'),summary_sha256=sha(dest/'summary.json'),cnf_path=key(dest/'instance.cnf'),cnf_sha256=sha(dest/'instance.cnf'),model_path=key(model),model_sha256=sha(model),scope_path=key(dest/'scope.json'),scope_sha256=sha(dest/'scope.json'),variables=summary['variables'],clauses=summary['clauses'],model_package_path=key(package),model_package_sha256=sha(package),receipt_path=key(receipt),receipt_sha256=sha(receipt)))
            with (out/'progress.jsonl').open('a',encoding='utf-8',newline='\n') as f:f.write(json.dumps(records[-1])+'\n')
            print(json.dumps(dict(case=case,variables=summary['variables'],clauses=summary['clauses'],elapsed_seconds=time.monotonic()-start)),flush=True)
        summary=dict(status='CANDIDATE_FIFTEEN_FOUR_PROFILE_CNF_BATCH_BUILT',timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=inputs,selection=cases,records=records,completed=len(records),native_solver_calls=0,independent_approval=False,target_resolution=False,elapsed_seconds=time.monotonic()-start,scope='Fifteen literal profile formulas; native outcomes and any union/normalization proof are separate.')
        save(out/'summary.json',summary);print(json.dumps(dict(status=summary['status'],completed=len(records),elapsed_seconds=summary['elapsed_seconds'])))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e),source_sha256=sha(Path(__file__))));raise
if __name__=='__main__':main()
