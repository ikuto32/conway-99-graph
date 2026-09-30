"""Normalize eight explicit wave25 raw identities; no solver/ledger/index edits."""
from pathlib import Path
import argparse,hashlib,json
import package_20260930_twentyfourth_recovery as prior
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_'
MANIFESTS=[B+x for x in ['count_master_scalar_cuts/artifact_packages.json','direct_cell_count_cnf/artifact_packages.json','direct_cell_lex/artifact_packages.json','direct_cell_unknown_trace_package/package_manifest.json','direct_cell_lex_unknown_trace_package/package_manifest.json']]
SINGLE=B+'eight_count_profile_lift_second/model_package.json'
INVENTORY=B+'twentyfifth_candidate_inventory_v2/inventory.json'
def sha(p):
    with(ROOT/p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def packages():
    rows=[prior.normalize(read(SINGLE),SINGLE)]
    for p in MANIFESTS:rows.extend(prior.normalize(record,p)for record in read(p)['records'])
    assert len(rows)==len({r['path']for r in rows})==8
    for r in rows:
        assert sha(r['path'])==r['sha256'] and(ROOT/r['path']).stat().st_size==r['bytes'];offset=0
        for part in r['parts']:
            assert part['raw_offset']==offset and sha(part['path'])==part['gzip_sha256'] and(ROOT/part['path']).stat().st_size==part['gzip_bytes'] and part['gzip_bytes']<=10*1024**2;offset+=part['raw_bytes']
        assert offset==r['bytes']
    assert sha(INVENTORY)=='2246ed2989638dba95438450a72f1ee27b5878480e6eae226eef374502cc3c9a'
    inventory=read(INVENTORY);assert{r['path']for r in rows}=={r['path']for r in inventory['oversized_raw_or_payload_files']}
    return rows
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);a=ap.parse_args();out=(ROOT/a.out).resolve();assert out==ROOT/(B+'twentyfifth_raw_recovery');out.mkdir(exist_ok=False)
    rows=packages();inputs=MANIFESTS+[SINGLE,INVENTORY,Path(__file__).relative_to(ROOT).as_posix(),Path(prior.__file__).relative_to(ROOT).as_posix()]
    record=dict(schema='WAVE25_NORMALIZED_RAW_RECOVERY_V1',scope='Identity transport only; mathematical and UNSAT-proof validity have separate independent records. Four raw streams are UNKNOWN partial traces, not complete proofs.',records=rows,inputs_sha256={p:sha(p)for p in inputs},raw_artifacts=len(rows),raw_bytes=sum(r['bytes']for r in rows),gzip_parts=sum(len(r['parts'])for r in rows),prior_recovery_catalog=dict(path=B+'twentyfourth_artifact_packaging/catalog.json',sha256='ff5fae36a849fd2baddc3ccc5fd06d3b58df4fee047e68ff2dc58e560e921de6'),byte_recovery_performed_by_this_normalizer=False)
    dest=out/'manifest.json'
    with dest.open('x',encoding='utf8',newline='\n')as f:json.dump(record,f,indent=2);f.write('\n')
    print(json.dumps(dict(path=dest.relative_to(ROOT).as_posix(),sha256=sha(dest.relative_to(ROOT)),raw_artifacts=record['raw_artifacts'],raw_bytes=record['raw_bytes'],gzip_parts=record['gzip_parts'])))
if __name__=='__main__':main()
