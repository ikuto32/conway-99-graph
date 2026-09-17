"""Save-only artifact catalog/ignore additions after explicit user stop."""
from datetime import datetime,timezone
from hashlib import sha256
import gzip
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[1]
def digest(p):
 h=sha256()
 with p.open('rb') as f:
  while block:=f.read(8<<20):h.update(block)
 return h.hexdigest()
def save(p,d):
 with p.open('x',encoding='utf-8') as f:json.dump(d,f,indent=2);f.write('\n')
def key(p):return p.relative_to(ROOT).as_posix()
def main():
 out=ROOT/'acceleration/results/20260917_stop_packaging';assert not out.exists();out.mkdir(parents=True)
 catalog=ROOT/'docs/local-artifacts.json';ignore=ROOT/'.gitignore'
 shutil.copyfile(catalog,out/'local-artifacts.before.json');shutil.copyfile(ignore,out/'gitignore.before.txt')
 data=json.loads(catalog.read_bytes());known={r['path']:r for r in data['files']};added=[];ignore_paths=[]
 def append(path,recovery):
  p=ROOT/path;record=dict(path=path,size_bytes=p.stat().st_size,sha256=digest(p),artifact_availability='LOCAL_ONLY',
   recorded_at=datetime.now(timezone.utc).isoformat(),recovery=recovery)
  if path in known:
   assert known[path]['size_bytes']==record['size_bytes'] and known[path]['sha256']==record['sha256'],'Existing record conflicts; do not overwrite'
  else:data['files'].append(record);known[path]=record;added.append(record)
  ignore_paths.append('/'+path)
 gpu=ROOT/'acceleration/results/20260917_six_moment_pdhg/run01'
 gm=json.loads((gpu/'compressed_artifacts.json').read_bytes())
 for r in gm['files']:
  assert digest(ROOT/r['path'])==r['sha256'] and digest(ROOT/r['compressed_path'])==r['compressed_sha256']
  append(r['path'],dict(kind='EXACT_GZIP',manifest=key(gpu/'compressed_artifacts.json'),companion=r['compressed_path'],
   checker='acceleration/audit_compressed_artifact_manifest.py',existing_recovery_report='acceleration/results/20260917_artifact_replay/six_gpu_checkpoints_gzip.json'))
 cpu=ROOT/'acceleration/results/20260917_six_filtered_solve5400/run01'
 chunks=json.loads((cpu/'chunk_manifest.json').read_bytes());r=next(r for r in chunks['artifacts'] if r['source']=='numeric_lp.json')
 assert digest(cpu/r['source'])==r['source_sha256']
 for part in r['parts']:assert digest(cpu/part['path'])==part['sha256'] and (cpu/part['path']).stat().st_size==part['bytes']
 append(key(cpu/'numeric_lp.json'),dict(kind='EXACT_RAW_BYTE_PARTS',manifest=key(cpu/'chunk_manifest.json'),restorer='acceleration/restore_chunked_artifacts.py'))
 pilot=ROOT/'acceleration/results/20260917_moment_pdhg_gpu'
 export=json.loads((pilot/'export/manifest.json').read_bytes());r=export['records']['two_coordinate']
 assert digest(ROOT/r['path'])==r['sha256']
 append(r['path'],dict(kind='DETERMINISTIC_REGENERATION',source='acceleration/export_20260917_moment_pdhg.py',
  source_sha256=digest(ROOT/'acceleration/export_20260917_moment_pdhg.py'),manifest=key(pilot/'export/manifest.json'),
  command='UV_PROJECT_ENVIRONMENT=build/research-venv; uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/export_20260917_moment_pdhg.py --out FRESH_WORKSPACE_DIRECTORY',
  caveat='No public binary upload. Requires exact audited two-coordinate matrix and pinned dependencies; compare regenerated binary SHA256. No GPU run needed.'))
 six_export=ROOT/'acceleration/results/20260917_six_moment_pdhg/export/manifest.json';r=json.loads(six_export.read_bytes())
 assert digest(ROOT/r['binary_path'])==r['binary_sha256']
 append(r['binary_path'],dict(kind='DETERMINISTIC_REGENERATION',source='acceleration/export_20260917_six_moment_pdhg.py',
  source_sha256=digest(ROOT/'acceleration/export_20260917_six_moment_pdhg.py'),manifest=key(six_export),
  command='UV_PROJECT_ENVIRONMENT=build/research-venv; uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/export_20260917_six_moment_pdhg.py --out FRESH_MANIFEST_DIRECTORY --binary FRESH_BINARY_PATH',
  caveat='No public binary upload. First restore six audited NPZ from its chunk manifest. Compare regenerated binary SHA256; no GPU launch.'))
 filter_manifest=ROOT/'acceleration/results/20260917_six_coordinate_matching_filter/run01/compressed_artifacts.json'
 entries={Path(r['path']).name:r for r in json.loads(filter_manifest.read_bytes())['files']}
 recovered=ROOT/'acceleration/results/20260917_independent_review/six_coordinate_matching_filter/recovered'
 recovered_count=0
 for p in sorted(recovered.glob('*.json')):
  if p.stat().st_size<=10<<20:continue
  r=entries[p.name];assert digest(p)==r['sha256'];recovered_count+=1
  append(key(p),dict(kind='EXACT_GZIP_DUPLICATE_RECOVERY',manifest=key(filter_manifest),companion=r['compressed_path'],
   same_bytes_as=r['path'],retrieval='Decode the referenced gzip and verify this SHA256; preserve reviewer directory naming. No matching search or audit rerun required.'))
 assert recovered_count==11
 tiny=[]
 for p in sorted(pilot.rglob('*.bin')):
  if p.stat().st_size>=10<<20:continue
  z=p.with_suffix('.bin.gz');assert not z.exists()
  with p.open('rb') as src,z.open('xb') as dst:
   with gzip.GzipFile(fileobj=dst,mode='wb',filename='',mtime=0,compresslevel=9) as enc:shutil.copyfileobj(src,enc)
  assert gzip.decompress(z.read_bytes())==p.read_bytes()
  tiny.append(dict(path=key(p),size_bytes=p.stat().st_size,sha256=digest(p),compressed_path=key(z),compressed_size_bytes=z.stat().st_size,compressed_sha256=digest(z)))
 assert len(tiny)==7
 tiny_manifest=pilot/'pilot_binary_compressed_artifacts.json';save(tiny_manifest,dict(schema_version=1,encoding='gzip; exact byte recovery',files=tiny,
  saved_after_user_stop=True,verification='Seven small fixtures gzip-decompressed and compared byte-for-byte; no numerical/search experiment'))
 for r in tiny:append(r['path'],dict(kind='EXACT_GZIP',manifest=key(tiny_manifest),companion=r['compressed_path'],checker='acceleration/audit_compressed_artifact_manifest.py'))
 old_ignore=ignore.read_text();existing=set(old_ignore.splitlines());new=[p for p in ignore_paths if p not in existing]
 with ignore.open('a',encoding='utf-8') as f:f.write('\n# Saved on explicit stop: large local artifacts and raw pilot binaries.\n'+'\n'.join(new)+'\n')
 catalog.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
 save(out/'summary.json',dict(status='SAVE_ONLY_ARTIFACT_PACKAGING_COMPLETE',timestamp=datetime.now(timezone.utc).isoformat(),
  appended_catalog_records=added,added_ignore_patterns=new,tiny_binary_gzip_manifest=key(tiny_manifest),
  catalog_sha256=digest(catalog),gitignore_sha256=digest(ignore),research_runs=0,recovered_oversized_duplicates=11))
 print(json.dumps(dict(added_catalog_records=len(added),added_ignore_patterns=len(new),tiny_gzip_fixtures=len(tiny),summary=key(out/'summary.json'))))
if __name__=='__main__':main()
