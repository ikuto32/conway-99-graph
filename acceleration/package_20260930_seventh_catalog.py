"""Read-only seventh inventory and exact gzip/body recovery proposal; no staging."""
from datetime import datetime, timezone
from hashlib import sha256
import gzip
import io
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'acceleration/results/20260930_seventh_artifact_packaging'
CHECKPOINT=ROOT/'acceleration/results/20260930_resume/sixth_milestone_checkpoint.json'
PREVIOUS=ROOT/'acceleration/results/20260930_sixth_artifact_packaging/catalog.json'
HELPER=ROOT/'acceleration/reconstruct_20260930_triangle_artifacts.py'
CAL=ROOT/'acceleration/results/20260930_independent_review/seventh_triangle_recovery_calibration/summary.json'
LIMIT=10*1024**2
EXCLUDED_TOKENS=['matching_pair_census','proof_core','row_obstruction','p_core']
EXCLUDED_PREFIX='acceleration/results/20260930_seventh_artifact_packaging/'
PACKAGES=['20260930_triangle_full99_cnf','20260930_triangle_wave151_full99_cnf']
PROOFS=[('20260930_triangle_native_pilot','triangle_wave154_unsat','INDEPENDENT_FIXED_WAVE154_TRIANGLE_FULL99_UNSAT_PASS'),('20260930_wave151_triangle_native_pilot','triangle_wave151_unsat','INDEPENDENT_FIXED_WAVE151_TRIANGLE_FULL99_UNSAT_PASS')]
def h(p):
    result=sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(1<<20),b''):result.update(b)
    return result.hexdigest()
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(p.read_bytes())
def save(name,obj):
    with(OUT/name).open('x',encoding='utf-8',newline='\n')as f:json.dump(obj,f,indent=2);f.write('\n')
def excluded(name):return name.startswith(EXCLUDED_PREFIX)or any(t in name.lower()for t in EXCLUDED_TOKENS)
def rec(p):return dict(path=key(p),sha256=h(p),bytes=p.stat().st_size,availability='LOCAL_ONLY',publication_ready_under_10MiB=p.stat().st_size<=LIMIT)
def recover_packages():
    entries=[]
    for name in PACKAGES:
        d=ROOT/'acceleration/results'/name;package_file=d/'artifact_packages.json';metadata=read(package_file)
        for row in metadata['packages']:
            parts=[];buffers=[]
            for part in row['ordered_parts']:
                p=ROOT/part['path'];actual=rec(p)
                assert actual['bytes']==part['bytes']<=LIMIT and actual['sha256']==part['sha256']
                parts.append(actual);buffers.append(p.read_bytes())
            compressed=b''.join(buffers);assert sha256(compressed).hexdigest()==row['compressed_stream_sha256']
            raw_hash,body_hash,count,body_count=sha256(),sha256(),0,0;header=None
            with gzip.GzipFile(fileobj=io.BytesIO(compressed))as stream:
                if row['raw_path'].endswith('/instance.cnf'):
                    header=stream.readline();assert header.startswith(b'p cnf ')and header.endswith(b'\n')and b'\r'not in header
                    raw_hash.update(header);count+=len(header)
                for b in iter(lambda:stream.read(1<<20),b''):
                    raw_hash.update(b);count+=len(b)
                    if header is not None:body_hash.update(b);body_count+=len(b)
            raw=ROOT/row['raw_path'];assert raw_hash.hexdigest()==row['raw_sha256']==h(raw)and count==row['raw_bytes']==raw.stat().st_size
            entries.append({**rec(raw),'recovery_type':'ORDERED_GZIP_PARTS','package_manifest':rec(package_file),'parts':parts,'compressed_stream_sha256':row['compressed_stream_sha256'],'reconstruction_checked':True,'recovery':'Concatenate listed parts in order, gzip-decompress, check exact raw hash and bytes.','raw_file_retained':True,'new_compression_performed':False})
            if header is not None:
                body=raw.with_name('clauses.body');assert body_hash.hexdigest()==h(body)and body_count==body.stat().st_size
                entries.append({**rec(body),'recovery_type':'DROP_EXACT_FIRST_LF_HEADER','from_raw_cnf':rec(raw),'exact_header_ascii':header.decode('ascii'),'reconstruction_checked':True,'recovery':'Recover authenticated CNF, remove exactly its first LF-terminated header line, and check recorded body hash/bytes.','raw_file_retained':True})
    return entries
def main():
    shared_before={p:h(ROOT/p)for p in['.gitignore','CLAIMS.yaml']}
    names=subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z'],cwd=ROOT).decode().split('\0')
    names=sorted(n for n in names if n and(n.startswith('acceleration/')or n.startswith('docs/'))and not excluded(n))
    OUT.mkdir(parents=True,exist_ok=False)
    save('manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),source_sha256=h(Path(__file__)),previous_checkpoint=rec(CHECKPOINT),previous_catalog=rec(PREVIOUS),population='All untracked nonignored acceleration/ and docs/ files at this snapshot, excluding stated ongoing or deferred eighth-wave work and this catalog. Artifact counts are not research progress.',excluded_path_substrings=EXCLUDED_TOKENS,excluded_prefix=EXCLUDED_PREFIX,exclusion_basis='Parent explicitly defers all matching-pair census, proof-core, row-obstruction and new P-core source/docs/output work to wave8, even if recently completed.',live_process_state='UNKNOWN; not inspected by this packaging script',authorized_changes='Only new catalog/proposal files; no source artifacts, ledger, .gitignore, staging or commits.'))
    inventory=[];unstable=[]
    for name in names:
        p=ROOT/name;before=p.stat();r=rec(p);after=p.stat()
        if(before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns):unstable.append(name)
        r['git_state_at_scan']='UNTRACKED_NONIGNORED';inventory.append(r)
    save('untracked_inventory.json',dict(entries=inventory,unstable_files=unstable,excluded_path_substrings=EXCLUDED_TOKENS))
    assert not unstable,'snapshot files changed; preserve and repeat a fresh catalog'
    entries=recover_packages();oversized={r['path']for r in inventory if r['bytes']>LIMIT}
    assert oversized=={r['path']for r in entries},'every oversized untracked item must be explicitly covered'
    # Raw logs are commonly ignored globally. Enumerate only direct parents of
    # included completed artifacts, never deferred matching/core directories.
    tracked=set(subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0'))
    logs={p for name in names for p in(ROOT/name).parent.glob('*.log')if not excluded(key(p))}
    log_records=[{**rec(p),'already_tracked':key(p)in tracked,'publication_action':'Keep raw log; force-add if ignored by existing global patterns.'}for p in sorted(logs)]
    assert all(r['bytes']<=LIMIT for r in log_records),'oversized log requires explicit new disposition'
    save('raw_logs_publication.json',dict(population='Raw .log files adjacent to included completed seventh-wave artifacts; deferred eighth-wave paths excluded.',entries=log_records))
    proof_records=[]
    for run,audit,status in PROOFS:
        base=ROOT/'acceleration/results'/run;ap=ROOT/'acceleration/results/20260930_independent_review'/audit/'summary.json';a=read(ap);proof=base/'main/proof.drat'
        assert a['status']==status and a['proof_sha256']==h(proof)and a['proof_bytes']==proof.stat().st_size<=LIMIT
        assert a['target_resolution']is False
        proof_records.append({**rec(proof),'proof_completeness':'COMPLETE_INDEPENDENTLY_REPLAYED','publication_action':'PUBLISH_RAW; do not ignore as an incomplete timeout trace.','independent_audit':rec(ap),'exact_cnf_sha256':a['cnf_sha256'],'claim_id':a['claim_id'],'scope':a['scope']})
    save('complete_proofs_publication.json',dict(entries=proof_records,raw_proof_count=2,compression_required=False))
    ignore=['# Seventh milestone: recoverable triangle CNF/model/body originals only.']
    existing_ignore=set((ROOT/'.gitignore').read_text().splitlines())
    ignore+=['/'+name for name in sorted(oversized)if'/'+name not in existing_ignore]
    (OUT/'proposed_gitignore.txt').write_text('\n'.join(ignore)+'\n',encoding='utf-8',newline='\n')
    stage=sorted({r['path']for r in inventory if r['bytes']<=LIMIT}|{r['path']for r in log_records if not r['already_tracked']})
    (OUT/'proposed_stage_paths.txt').write_text('\n'.join(stage)+'\n',encoding='utf-8',newline='\n')
    save('stage_inventory.json',dict(paths=stage,unit='Exact source/document/artifact paths in the frozen seventh snapshot; proposal only.',ignored_raw_log_paths=[r['path']for r in log_records if not r['already_tracked']],complete_raw_proof_paths=[r['path']for r in proof_records],oversized_raw_paths_not_to_stage=sorted(oversized),catalog_files_note='Also stage this new catalog directory after reviewing it; it is intentionally excluded from its own frozen inventory.'))
    calibration=read(CAL);assert calibration['status']=='EXACT_TRIANGLE_RECONSTRUCTION_CONTROLS_PASS'and calibration['source_sha256']==h(HELPER)
    catalog=dict(status='SEVENTH_COMPLETED_ARTIFACT_RECOVERY_AND_PUBLICATION_PROPOSAL_READY',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),entries=entries,inventory=rec(OUT/'untracked_inventory.json'),stage_inventory=rec(OUT/'stage_inventory.json'),proposed_stage_paths=rec(OUT/'proposed_stage_paths.txt'),raw_logs=rec(OUT/'raw_logs_publication.json'),complete_proofs=rec(OUT/'complete_proofs_publication.json'),proposed_ignore=rec(OUT/'proposed_gitignore.txt'),reconstruction_tool=rec(HELPER),reconstruction_calibration=rec(CAL),locked_recovery_command='Set UV_PROJECT_ENVIRONMENT=build/research-venv; uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/reconstruct_20260930_triangle_artifacts.py recover --include-bodies --report build/triangle-recovery-report.json',fresh_root_option='Add --out-root build/fresh-triangle-replay to restore all exact prescribed repo-relative paths beneath that fresh root; default restores missing raw paths in this repository.',counts=dict(inventoried_untracked_paths=len(inventory),oversized_recoverable_raw_inputs=len(entries),gzip_recovered_raw_inputs=4,header_drop_recovered_bodies=2,complete_raw_proofs=2,raw_logs=len(log_records),proposed_stage_paths=len(stage),proposed_ignore_lines=len(ignore)-1),all_oversized_mathematical_inputs_recoverable_from_under_10MiB_parts=True,mathematical_verification=False,independent_review=False,source_artifacts_modified=False,shared_gitignore_modified_by_this_script=False,ledger_modified_by_this_script=False,staged_or_committed=False,excluded_path_substrings=EXCLUDED_TOKENS,shared_files_before_sha256=shared_before,shared_files_after_sha256={p:h(ROOT/p)for p in shared_before},limitations=['Artifact counts do not measure target search coverage or mathematical progress.','Files remain LOCAL_ONLY until root actually publishes them.','The existing exact gzip packages are reused; no completed environment record was rewritten.','Checker and solver build provenance remains bound in the independent proof audits; this catalog does not claim portable binary identity or newly package installed compiler binaries.','Deferred eighth-wave matching/core/row artifacts were not inventoried.'])
    save('catalog.json',catalog);print(json.dumps(dict(status=catalog['status'],counts=catalog['counts'],sha256=h(OUT/'catalog.json'))))
if __name__=='__main__':main()
