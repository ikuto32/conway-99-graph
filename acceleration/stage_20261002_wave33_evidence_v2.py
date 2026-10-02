"""Stage bounded completed wave33 evidence; preserve large raw originals locally.

Exact raw model replacements are lossless manifests, not mathematical approval.
No arbitrary untracked files, submodules, secrets or ongoing experiment folders.
"""
import argparse,hashlib,json,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
import yaml
from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
LEDGER='dbb72994ed9f43c88b3227ec8940d355aca244ac4b05b58dca6ba8b436cb9b96'
PACKAGES={
 'acceleration/results/20261002_wave33_model_package01/manifest.json':'c3efa198c5f48eddb5ead69a4bb130a3dc55567bb298856143c6fb62eb0e0145',
 'acceleration/results/20261002_wave33_reconstruction_package01/manifest.json':'f639431b7ea9ce0f1500ea48b002629d2523271eead700217dd512e8ade66989',
}
DIRECT_LARGE={
 'acceleration/results/20261002_independent_review/rooted7_model01/reconstructed_model.json':'ff8c03ae1d3bc0cd249b6545dab37112d7521163e8273b98839b3966be748740',
}
SOURCE_PREFIXES=('audit_20261002_hypergraph_saved_objects','audit_20261002_rooted7_corner','audit_20261002_rooted7_model','audit_20261002_rooted7_transition','audit_20261002_rooted8_catalogue','audit_20261002_rooted8_model','audit_20261002_wave32_publication','audit_20261002_wave33','calibrate_20261002_rooted8_products','record_20261002_hypergraph_controls','record_20261002_hypergraph_pilot','record_20261002_rooted7_model','record_20261002_rooted7_rational','record_20261002_rooted8_catalogue','record_20261002_rooted8_model','register_20261002_bound_claims','record_20261002_wave33','review_20261002_hypergraph_pilot','theory_20261002_rooted7','theory_20261002_rooted8_corner','theory_20261002_rooted8_gf2_screen','theory_20261002_rooted8_universal5','theory_20261002_rooted8_product_subset','package_20261002_wave33','stage_20261002_wave33','hypergraph_weighted_anneal_20261002_v1','prepare_20261002_hypergraph_weighted','plan_20261002_hypergraph_weighted_engineering','design_20261002_hypergraph_weighted')
RESULT_PREFIXES=('20261002_rooted7','20261002_rooted8_corner','20261002_rooted8_gf2_screen','20261002_rooted8_gf2_controls','20261002_rooted8_highs_api','20261002_rooted8_universal5','20261002_rooted8_v2_syntax','20261002_rooted8_product_calibration','20261002_rooted8_product_subset_v2_controls','20261002_rooted8_product_subset_v3_controls','20261002_rooted8_product_subset_v3_run','20261002_rooted8_product_subset_v3_supervisor','20261002_hypergraph_pilot','20261002_hypergraph_weighted_build','20261002_hypergraph_weighted_controls','20261002_wave33')
AUDIT_PREFIXES=('rooted7_corner_witnesses','rooted7_model','rooted8_catalogue','rooted8_model','hypergraph_saved','hypergraph_pilot','wave33_model_recovery','wave33_reconstruction_recovery','wave33_transition')

def need(ok,message):
 if not ok:raise ValueError(message)

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--seconds',type=float,required=True)
 args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
 deadline=CommandDeadline(args.seconds,allocation_reason='Finite explicit completed evidence and five exact lossless replacements; preserve originals and index on any error')
 def digest(path):
  h=hashlib.sha256()
  with path.open('rb') as stream:
   for block in iter(lambda:stream.read(8*1024**2),b''):
    need(not deadline.status()['stop_required'] and deadline.status()['remaining_seconds']>20,'not completed within allocated budget');h.update(block)
  return h.hexdigest()
 need(digest(ROOT/'CLAIMS.yaml')==LEDGER,'exact324-record milestone ledger')
 data=yaml.safe_load((ROOT/'CLAIMS.yaml').read_bytes());before=yaml.safe_load((ROOT/'acceleration/results/20261002_wave33_registration02/CLAIMS.before.yaml').read_bytes())
 old={a['id'] for a in before['artifacts']};pins={a['path']:a['sha256'] for a in data['artifacts'] if a['id'] not in old and a['path']}
 replacements={};package_paths=set()
 for name,identity in PACKAGES.items():
  need(digest(ROOT/name)==identity,'frozen payload manifest');manifest=json.loads((ROOT/name).read_bytes());package_paths.add(ROOT/name)
  for record in manifest['records']:
   replacements[record['raw_path']]=dict(manifest=name,manifest_sha256=identity,raw_sha256=record['raw_sha256'],raw_bytes=record['raw_bytes'])
   for part in record['parts']:
    p=ROOT/part['path'];need(digest(p)==part['gzip_sha256'] and p.stat().st_size==part['gzip_bytes'],'exact compressed payload');package_paths.add(p)
 candidates={ROOT/name for name in ['CLAIMS.yaml','README.md','ACTIVE_RESEARCH.md','docs/RESEARCH_MAP.md','docs/REPRODUCING.md','docs/RESEARCH_20261002_THIRTYTHIRD_WAVE.md','docs/DERIVATION_20261002_ROOTED6_PARAMETER_ROOTED7_SCREEN.md','docs/DERIVATION_20261002_ROOTED8_UNIVERSAL5_PRODUCTS.md','docs/DEVIATION_20261002_ROOTED8_BUILD_CONTROLS.md','docs/PROTOCOL_20261002_ROOTED8_UNIVERSAL5_PRODUCTS.md']}
 candidates.update(ROOT/name for name in pins);candidates.update(package_paths)
 candidates.update(p for p in (ROOT/'acceleration').iterdir() if p.is_file() and p.name.startswith(SOURCE_PREFIXES))
 folders=[p for p in (ROOT/'acceleration/results').iterdir() if p.is_dir() and p.name.startswith(RESULT_PREFIXES) and not p.name.startswith('20261002_wave33_stage')]
 folders.append(ROOT/'acceleration/results/20261002_wave33_stage_supervision01')
 folders.extend(p for p in (ROOT/'acceleration/results/20261002_independent_review').iterdir() if p.is_dir() and p.name.startswith(AUDIT_PREFIXES))
 for folder in folders:candidates.update(p for p in folder.rglob('*') if p.is_file())
 records=[];omitted=[]
 for p in sorted(candidates):
  p=p.resolve();need(p.is_relative_to(ROOT) and p.is_file(),'bounded existing evidence path');name=p.relative_to(ROOT).as_posix()
  need(not name.startswith(('tools/','external_conway99_research/','build/')) and p.name not in {'AGENTS.md','PROMPT.md','.env'},'protected namespaces')
  identity=digest(p);need(name not in pins or pins[name]==identity,'exact newly bound evidence identity')
  if name in DIRECT_LARGE:need(identity==DIRECT_LARGE[name] and p.stat().st_size<50*1024**2,'exact independently reconstructed raw file below50MiB')
  if p.stat().st_size>8*1024**2 and name not in DIRECT_LARGE:
   replacement=replacements.get(name);need(replacement is not None and replacement['raw_sha256']==identity and replacement['raw_bytes']==p.stat().st_size,'every large omission has exact lossless payload')
   omitted.append(dict(path=name,sha256=identity,bytes=p.stat().st_size,replacement=replacement,reason='Raw original preserved locally; deterministic byte-recoverable payload staged.'));continue
  records.append(dict(path=name,sha256=identity,bytes=p.stat().st_size))
 paths=[r['path'] for r in records]
 for start in range(0,len(paths),100):
  need(not deadline.status()['stop_required'],'staging deadline');result=subprocess.run(['git','add','-f','--',*paths[start:start+100]],cwd=ROOT,capture_output=True)
  need(result.returncode==0,'exact allowlisted staging '+result.stderr.decode(errors='replace'))
 need(digest(ROOT/'CLAIMS.yaml')==LEDGER,'no concurrent ledger mutation')
 report=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),source_sha256=digest(Path(__file__)),ledger_sha256=LEDGER,records=records,omitted_raw_replacements=omitted,distinct_staged_paths=len(paths),staged_bytes=sum(r['bytes'] for r in records),public_availability_changed=False,mathematical_replay=False)
 with (out/'manifest.json').open('x',encoding='utf8',newline='\n') as stream:json.dump(report,stream,indent=2);stream.write('\n')
 subprocess.run(['git','add','-f','--',(out/'manifest.json').relative_to(ROOT).as_posix()],cwd=ROOT,check=True,capture_output=True)
 print(json.dumps(dict(status='WAVE33_EXACT_COMPLETED_EVIDENCE_STAGED',paths=len(paths),raw_replacements=len(omitted),bytes=report['staged_bytes'])))

if __name__=='__main__':main()
