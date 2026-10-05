"""Normalize and stream-verify the two exact wave26 oversized raw identities."""
from pathlib import Path
import argparse,gzip,hashlib,json
import package_20260930_twentyfourth_recovery as prior
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_'
INVENTORY=B+'twentysixth_candidate_inventory/inventory.json'
MANIFESTS=[B+'eight_count_profile_lift_third/model_package.json',B+'count_min_upper_cnf/artifact_packages.json']
PINS={INVENTORY:'bd1ba988658d0db25144f404fd96597fd2202a21b560e093c66c0ffd09fe8f10',MANIFESTS[0]:'8cc1cb61e2c3d476c1c892165ef72584128ba21a27b3a654f9065a246753372f',MANIFESTS[1]:'d3c7cfb8f7d0b7ce1a09ab629ce093893b8314314df9690a6bfb080cecdf9a1b'}
def sha(p):
    with(ROOT/p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def packages():
    assert all(sha(p)==v for p,v in PINS.items())
    single=read(MANIFESTS[0]);rows=[prior.normalize(single,MANIFESTS[0])]
    raw=read(MANIFESTS[1]);assert raw['schema']=='COUNT_MIN_UPPER_CNF_GZIP_PACKAGE_V1'
    for rec in raw['records']:
        rows.append(dict(manifest=MANIFESTS[1],path=rec['path'],sha256=rec['sha256'],bytes=rec['bytes'],parts=rec['parts']))
    assert len(rows)==len({r['path']for r in rows})==2
    expected={r['path']:(r['sha256'],r['bytes'])for r in read(INVENTORY)['oversized_raw_or_payload_files']}
    assert {r['path']:(r['sha256'],r['bytes'])for r in rows}==expected
    for r in rows:
        assert sha(r['path'])==r['sha256']and(ROOT/r['path']).stat().st_size==r['bytes'];offset=0
        for p in r['parts']:
            assert p['raw_offset']==offset and sha(p['path'])==p['gzip_sha256']and(ROOT/p['path']).stat().st_size==p['gzip_bytes']and p['gzip_bytes']<=10*1024**2
            offset+=p['raw_bytes']
        assert offset==r['bytes']
    return rows
def stream_identity(record):
    whole=hashlib.sha256();total=0
    with(ROOT/record['path']).open('rb')as original:
        for part in record['parts']:
            assert part['raw_offset']==total;chunk=hashlib.sha256();n=0
            with gzip.open(ROOT/part['path'],'rb')as f:
                for b in iter(lambda:f.read(1048576),b''):
                    assert original.read(len(b))==b;whole.update(b);chunk.update(b);n+=len(b)
            assert chunk.hexdigest()==part['raw_sha256']and n==part['raw_bytes'];total+=n
        assert not original.read(1)
    assert total==record['bytes']and whole.hexdigest()==record['sha256']
    return dict(path=record['path'],sha256=whole.hexdigest(),bytes=total,gzip_parts=len(record['parts']),literal_original_comparison=True)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);a=ap.parse_args();out=(ROOT/a.out).resolve();assert out==ROOT/(B+'twentysixth_raw_recovery');out.mkdir(exist_ok=False)
    rows=packages();controls=[stream_identity(r)for r in rows]
    inputs=MANIFESTS+[INVENTORY,Path(__file__).relative_to(ROOT).as_posix(),Path(prior.__file__).relative_to(ROOT).as_posix()]
    record=dict(schema='WAVE26_NORMALIZED_RAW_RECOVERY_V1',scope='Identity transport only; two oversized raw inputs, no mathematical or proof reapproval.',records=rows,inputs_sha256={p:sha(p)for p in inputs},raw_artifacts=len(rows),raw_bytes=sum(r['bytes']for r in rows),gzip_parts=sum(len(r['parts'])for r in rows),prior_recovery_catalog=dict(path=B+'twentyfifth_artifact_packaging_v2/catalog.json',sha256='2f4643672f2304bdec334d28f8e71de35925cc643e6d80821372cad156999c9c'),byte_recovery_performed_by_this_normalizer=True,stream_controls=controls)
    path=out/'manifest.json';path.write_text(json.dumps(record,indent=2)+'\n',encoding='utf8',newline='\n');print(json.dumps(dict(path=path.relative_to(ROOT).as_posix(),sha256=sha(path.relative_to(ROOT).as_posix()),raw_artifacts=2,raw_bytes=record['raw_bytes'],gzip_parts=record['gzip_parts'])))
if __name__=='__main__':main()
