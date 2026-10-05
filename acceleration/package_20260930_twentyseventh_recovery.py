"""Normalize14 oversized wave27 originals; preserve every existing raw/package."""
import argparse,gzip,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';INVENTORY=B+'twentyseventh_candidate_inventory/inventory.json';INVENTORY_SHA='381d1130d419894a9cfd916a5c41faee637d97bf850bb046e472f5d26f7cd4ba';OUT=B+'twentyseventh_raw_recovery';LIMIT=10*1024**2
def safe(p):
    q=(ROOT/p).resolve();assert q.is_relative_to(ROOT)and q.relative_to(ROOT).as_posix()==p;assert not p.startswith('tools/')and p!='PROMPT.md';return q
def sha(p):
    with safe(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(safe(p).read_bytes())
def key(p):return p.relative_to(ROOT).as_posix()
def save(p,x):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def packages():
    manifest=read(OUT+'/manifest.json');assert manifest['schema']=='WAVE27_NORMALIZED_RAW_RECOVERY_V1';return manifest['records']
def stream_identity(r):
    whole=hashlib.sha256();total=0
    with safe(r['path']).open('rb')as original:
        for p in r['parts']:
            assert p['raw_offset']==total and sha(p['path'])==p['gzip_sha256']and safe(p['path']).stat().st_size==p['gzip_bytes']<=LIMIT;h=hashlib.sha256();n=0
            with gzip.open(safe(p['path']),'rb')as f:
                for b in iter(lambda:f.read(1048576),b''):assert original.read(len(b))==b;whole.update(b);h.update(b);n+=len(b)
            assert n==p['raw_bytes']and h.hexdigest()==p['raw_sha256'];total+=n
        assert not original.read(1)
    assert total==r['bytes']and whole.hexdigest()==r['sha256'];return dict(path=r['path'],sha256=whole.hexdigest(),bytes=total,gzip_parts=len(r['parts']),literal_original_comparison=True)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);args=ap.parse_args();assert args.out==OUT;out=safe(OUT);out.mkdir(exist_ok=False);assert sha(INVENTORY)==INVENTORY_SHA;inventory=read(INVENTORY);large=inventory['oversized_raw_or_payload_files'];assert len(large)==14 and not inventory['pending']and not inventory['hash_mismatches'];rows=[];bindings={INVENTORY:INVENTORY_SHA}
    for item in large:
        raw=item['path'];h=item['sha256'];n=item['bytes'];assert sha(raw)==h and safe(raw).stat().st_size==n
        if item['package_records']:
            matches=[x for x in item['package_records']if x['raw_sha256']==h and x['raw_bytes']==n];assert matches;mp=sorted({x['manifest_path']for x in matches})[0];m=read(mp);bindings[mp]=sha(mp);assert m['raw_path']==raw and m['raw_sha256']==h and m['raw_bytes']==n;gp=m['gzip_path'];gh=m['gzip_sha256'];gn=m['gzip_bytes']
        else:
            assert raw==B+'exact_eight_population_inventory_v2/records.json';gp=OUT+'/inventory_records.json.gz'
            with safe(raw).open('rb')as f,safe(gp).open('xb')as compressed:
                with gzip.GzipFile(filename='',mode='wb',fileobj=compressed,mtime=0,compresslevel=9)as g:
                    for block in iter(lambda:f.read(1048576),b''):g.write(block)
            gh=sha(gp);gn=safe(gp).stat().st_size;mp=OUT+'/inventory_records_package.json';save(safe(mp),dict(raw_path=raw,raw_sha256=h,raw_bytes=n,gzip_path=gp,gzip_sha256=gh,gzip_bytes=gn));bindings[mp]=sha(mp)
        assert sha(gp)==gh and safe(gp).stat().st_size==gn<=LIMIT;rows.append(dict(path=raw,sha256=h,bytes=n,manifest=mp,parts=[dict(path=gp,gzip_sha256=gh,gzip_bytes=gn,raw_offset=0,raw_sha256=h,raw_bytes=n)]))
    assert len({r['path']for r in rows})==14;controls=[stream_identity(r)for r in rows]
    for p in[Path(__file__),Path(__file__).with_name(Path(__file__).stem+'_spec.md')]:bindings[key(p)]=sha(key(p))
    save(out/'manifest.json',dict(schema='WAVE27_NORMALIZED_RAW_RECOVERY_V1',records=rows,inputs_sha256=bindings,raw_artifacts=14,raw_bytes=sum(r['bytes']for r in rows),gzip_parts=sum(len(r['parts'])for r in rows),prior_recovery_catalog=dict(path=B+'twentysixth_artifact_packaging/catalog.json',sha256='d27a41ee61c1ed7453682ae69dd5a041e94e47e91d2aacaaf9b9c429619e27fb'),stream_controls=controls,byte_recovery_performed_by_this_normalizer=True,mathematical_verification=False));print(json.dumps(dict(path=OUT+'/manifest.json',sha256=sha(OUT+'/manifest.json'),raw_artifacts=14,raw_bytes=sum(r['bytes']for r in rows),gzip_parts=14)))
if __name__=='__main__':main()
