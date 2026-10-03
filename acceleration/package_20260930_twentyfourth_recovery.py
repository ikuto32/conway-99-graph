"""Normalize only explicitly enumerated wave24 recovery manifests."""
from pathlib import Path
import argparse, hashlib, json
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_'
SINGLE_MANIFESTS=[
 B+'hadamard_seven_profile_cnf/profile_0001/model_package.json',
 B+'eight_count_profile_lift/model_package.json',
]
LIST_MANIFESTS=[
 (B+'hadamard_count_master_cnf/packages.json','records'),
 (B+'count_interval_cnf/packages.json','records'),
 (B+'count_master_eight_orbit_cuts/artifact_packages.json','packages'),
 (B+'count_interval_frechet_package/package_manifest.json','records'),
 (B+'hadamard_seven_profile_proof_package/package_manifest.json','records'),
 (B+'twentyfourth_literal_proof_package/package_manifest.json','records'),
]
BATCH=B+'hadamard_seven_remaining_cnfs/run02/summary.json'
def load(p):return json.loads((ROOT/p).read_bytes())
def normalize(m,origin):
 path=m.get('raw_path',m.get('raw_original_path'));assert path
 if 'gzip_path' in m:
  parts=[dict(path=m['gzip_path'],gzip_sha256=m['gzip_sha256'],gzip_bytes=m['gzip_bytes'],raw_offset=0,raw_sha256=m['raw_sha256'],raw_bytes=m['raw_bytes'])]
 else:
  parts=[]
  for i,p in enumerate(m['parts']):
   if 'index' in p:assert p['index']==i
   dest=p.get('path') or (Path(origin).parent/p['relative_path']).as_posix()
   parts.append(dict(path=dest,gzip_sha256=p.get('gzip_sha256',p.get('sha256')),gzip_bytes=p.get('gzip_bytes',p.get('bytes')),raw_offset=p['raw_offset'],raw_sha256=p['raw_sha256'],raw_bytes=p['raw_bytes']))
 return dict(manifest=origin,path=path,sha256=m['raw_sha256'],bytes=m['raw_bytes'],parts=parts)
def packages():
 records=[]
 batch=load(BATCH);assert batch['completed_formulas']==215 and not batch['pending_profiles']
 assert len(batch['selection'])==len(set(batch['selection']))==len(batch['records'])==215
 for r in batch['records']:
  m=load(r['model_package_path']);assert m['raw_path']==r['model_path'] and m['raw_sha256']==r['model_sha256']
  records.append(normalize(m,r['model_package_path']))
 for p in SINGLE_MANIFESTS:records.append(normalize(load(p),p))
 for p,key in LIST_MANIFESTS:
  records.extend(normalize(m,p) for m in load(p)[key])
 assert len({r['path'] for r in records})==len(records)
 return records

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);args=ap.parse_args()
 out=(ROOT/args.out).resolve();assert out==ROOT/(B+'twentyfourth_raw_recovery');out.mkdir(exist_ok=False)
 rows=packages();inputs=sorted({r['manifest'] for r in rows}|{BATCH,Path(__file__).relative_to(ROOT).as_posix()})
 record=dict(schema='WAVE24_NORMALIZED_RAW_RECOVERY_V1',scope='Transport only. Existing proof validity and all mathematical claims have separate gates.',records=rows,inputs_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in inputs},raw_artifacts=len(rows),raw_bytes=sum(r['bytes'] for r in rows),gzip_parts=sum(len(r['parts']) for r in rows),prior_recovery_catalog=dict(path=B+'twentythird_artifact_packaging/catalog.json',sha256='5683804e5a4e0e42e50024799f05102d202665ec1b67c7f0dcb1917342dc1265'))
 dest=out/'manifest.json';dest.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(dict(path=dest.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),raw_artifacts=len(rows),raw_bytes=record['raw_bytes'],gzip_parts=record['gzip_parts'])))
if __name__=='__main__':main()
