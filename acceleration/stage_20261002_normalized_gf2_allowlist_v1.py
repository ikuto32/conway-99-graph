"""Authenticate and stage exact engineering sources/controls for normalized GF2."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
ALLOW='acceleration/results/20261002_rooted8_normalized_allowlist01/manifest.json'
ALLOW_SHA='561ae98eb0b53621ed74d3ad86ae1b3b750846e8dbe3290bc561a091565759a2'
GATE='acceleration/results/20261002_independent_review/normalized_gf2_controls01/summary.json'
GATE_SHA='5f9fb0852f86491c628e0ba9ab6bc564f78bc06bfce0a7a0ea4b668241e589a1'
RAW='acceleration/results/20261002_rooted8_universal5_product_model02/model.json'
RAW_SHA='a2162b5edc4eb68952cc9887156c5d0cd731aaaf9a6b5f94f446174b9d10528b'

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--seconds',type=float,required=True)
 args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);deadline=CommandDeadline(args.seconds,allocation_reason='Exact105engineeringallowlist and independently checked normalizedgate/rowcontent sources; no scientificworker')
 def need(ok,message):
  if not ok:raise ValueError(message)
 def sha(name):
  need(not deadline.status()['stop_required'],'stagingdeadline');p=(ROOT/name).resolve();need(p.is_relative_to(ROOT) and p.is_file(),'bounded existingartifact')
  with p.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
 need(sha(ALLOW)==ALLOW_SHA and sha(GATE)==GATE_SHA,'exact producerallowlist/independentgate')
 allow=json.loads((ROOT/ALLOW).read_bytes());gate=json.loads((ROOT/GATE).read_bytes());pins={row['path']:row['sha256'] for row in allow['entries']};pins.update(gate['inputs_sha256']);pins.update({ALLOW:ALLOW_SHA,GATE:GATE_SHA})
 paths=set(pins)|set(allow['self_metadata_paths'])
 for folder in ['acceleration/results/20261002_independent_review/normalized_gf2_controls01','acceleration/results/20261002_independent_review/normalized_gf2_controls_supervision01','acceleration/results/20261002_rooted8_normalized_allowlist_supervision01','acceleration/results/20261002_rooted8_row_content_supervision01']:
  p=ROOT/folder
  if p.is_dir():paths.update(x.relative_to(ROOT).as_posix() for x in p.rglob('*') if x.is_file())
 paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/'acceleration').glob('freeze_20261002_rooted8_normalized_launch_v*') if p.is_file())
 paths.update(['acceleration/audit_20261002_rooted8_row_content_v1.py',Path(__file__).resolve().relative_to(ROOT).as_posix()])
 paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/'docs').glob('*NORMALIZED_GF2*'))
 records=[];omitted=[]
 for name in sorted(paths):
  identity=sha(name);need(name not in pins or pins[name]==identity,'exact gate/input identity');p=ROOT/name
  need(name.startswith(('acceleration/','docs/')) or name in {'uv.lock','pyproject.toml'},'explicit researchnamespace')
  if name==RAW:
   need(identity==RAW_SHA,'immutable compressedrawmodel identity');omitted.append(dict(path=name,sha256=identity,retrieval_manifest='acceleration/results/20261002_wave33_model_package01/manifest.json',retrieval_manifest_sha256='c3efa198c5f48eddb5ead69a4bb130a3dc55567bb298856143c6fb62eb0e0145'));continue
  need(p.stat().st_size<50*1024**2,'bounded directengineeringartifact');records.append(dict(path=name,sha256=identity,bytes=p.stat().st_size))
 names=[r['path'] for r in records]
 for start in range(0,len(names),75):subprocess.run(['git','add','-f','--',*names[start:start+75]],cwd=ROOT,check=True,capture_output=True)
 report=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),records=records,omitted=omitted,mathematical_promotion=False,ledger_changed=False)
 with(out/'manifest.json').open('x',encoding='utf8',newline='\n') as stream:json.dump(report,stream,indent=2);stream.write('\n')
 subprocess.run(['git','add','-f','--',(out/'manifest.json').relative_to(ROOT).as_posix()],cwd=ROOT,check=True,capture_output=True)
 print(json.dumps(dict(status='NORMALIZED_ENGINEERING_EXACT_ARTIFACTS_STAGED',direct_paths=len(records),omitted_compressed_inputs=len(omitted))))

if __name__=='__main__':main()
