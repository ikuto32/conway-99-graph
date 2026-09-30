"""Bounded source-frozen first12 formula preparation; never invokes a SAT solver."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,subprocess,sys,time,traceback
from tqdm import tqdm
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results'
PRODUCER=ROOT/'acceleration/theory_20260930_exact_eight_campaign.py'
SPEC=PRODUCER.with_name(PRODUCER.stem+'_spec.md')
MANIFEST=B/'20260930_exact_eight_campaign_preparation/campaign_manifest.json'
PINS={PRODUCER:'9ebd87fea886f45fc916ad8afb9dc212fa089f760d4b96e55082926baef02c57',SPEC:'76d89e652dc0d90084863e4478b9d887658daac21aedfa20ffc72bf7bf48bf69',MANIFEST:'e7b07ea2f7c6b9f6738641afc22779a503841d5ac3da58d3873ebb0fa4b784ba',ROOT/'acceleration/theory_20260930_exact_eight_campaign_plan.md':'d497a23778ac45f644e95a0f928988e8d682875466aae81a65cc71319315fee9',B/'20260930_exact_eight_campaign_preparation/summary.json':'465726d62746ff323d424cd13d28e8a5ed5f038214f91d625f9df03960d4d14e'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def key(p):return p.relative_to(ROOT).as_posix()
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf8',newline='\n')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic();records=[];selected=[];failure=None
    try:
        for p,h in PINS.items():assert sha(p)==h,key(p)
        u=json.loads(MANIFEST.read_bytes());assert u['universe_size']==len(u['records'])==792 and not u['historical_profiles_subtracted'];selected=u['first_batch_case_ids'];assert len(selected)==len(set(selected))==12;byid={r['case_id']:r for r in u['records']}
        recomputed=[];seen=set()
        for r in u['records']:
            if r['subset_index']not in seen:seen.add(r['subset_index']);recomputed.append(r['case_id'])
        assert selected==recomputed[:12]
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),command=[sys.executable,*sys.argv],inputs_sha256={key(p):h for p,h in PINS.items()}|{key(Path(__file__)):sha(Path(__file__))},selected_case_ids=selected,allocation_seconds=120,native_calls=0,subprocess_contract='Only locked-environment Python producer build commands; no native SAT command.'))
        for number,cid in enumerate(tqdm(selected,desc='Build first12 exact-eight formulas',mininterval=1)):
            remaining=120-(time.monotonic()-start)
            if remaining<5:failure=dict(reason='cooperative120-second batch limit',next_case=cid);break
            r=byid[cid];folder=out/f"case_{r['case_index']:04d}";cmd=[sys.executable,'-B',str(PRODUCER),'build','--campaign-manifest',str(MANIFEST),'--campaign-manifest-sha256',PINS[MANIFEST],'--case-id',cid,'--attempt-id','first12_build01','--out',str(folder)];before=time.monotonic()
            try:
                cp=subprocess.run(cmd,cwd=ROOT,capture_output=True,timeout=remaining);(out/f'case_{number:02d}.stdout.log').write_bytes(cp.stdout);(out/f'case_{number:02d}.stderr.log').write_bytes(cp.stderr)
                receipt=dict(command=cmd,actual_exit_code=cp.returncode,wall_seconds=time.monotonic()-before,native_calls=0,outer_guard_expired=False);save(out/f'case_{number:02d}.receipt.json',receipt)
                if cp.returncode:failure=dict(reason='producer nonzero exit',case_id=cid,receipt=receipt);break
            except subprocess.TimeoutExpired as ex:
                (out/f'case_{number:02d}.stdout.log').write_bytes(ex.stdout or b'');(out/f'case_{number:02d}.stderr.log').write_bytes(ex.stderr or b'');failure=dict(reason='producer timeout under cumulative120-second budget',case_id=cid,native_calls=0);break
            summary=json.loads((folder/'summary.json').read_bytes());assert summary['status']=='CANDIDATE_EXACT_EIGHT_CAMPAIGN_LITERAL_FULL_GRAM_BUILT'and summary['case_id']==cid and summary['native_calls']==0
            rec=dict(case_id=cid,case_index=r['case_index'],subset_index=r['subset_index'],attempt_id='first12_build01',full_count_profile_sha256=r['full_count_profile_sha256'],variables=summary['variables'],clauses=summary['clauses'],selectors=summary['selectors'],initial_domain_sizes=summary['initial_domain_sizes'],files={n:dict(path=key(folder/n),sha256=sha(folder/n),bytes=(folder/n).stat().st_size)for n in ['summary.json','instance.cnf','model.json','scope.json','selected_profile.json','initial_domains.json','selection.json','model_package.json']})
            records.append(rec);save(out/f'checkpoint_{len(records):02d}.json',dict(completed_records=records,pending_case_ids=selected[len(records):],native_calls=0))
        for p,h in PINS.items():assert sha(p)==h,key(p)
        save(out/'summary.json',dict(status='CANDIDATE_FIRST12_EXACT_EIGHT_FORMULAS_COMPLETE'if len(records)==12 else'CANDIDATE_FIRST12_EXACT_EIGHT_FORMULAS_PARTIAL',inputs_sha256={key(p):h for p,h in PINS.items()}|{key(Path(__file__)):sha(Path(__file__))},selected_case_ids=selected,records=records,completed_formulas=len(records),pending_case_ids=selected[len(records):],stop=failure,elapsed_seconds=time.monotonic()-start,native_calls=0,independent_approval=False,outputs_sha256={key(p):sha(p)for p in out.iterdir()if p.is_file()}));print(json.dumps(dict(completed=len(records),pending=len(selected)-len(records),summary_sha256=sha(out/'summary.json'))))
    except BaseException as ex:save(out/'failure.json',dict(error=repr(ex),traceback=traceback.format_exc(),completed_records=records,pending_case_ids=selected[len(records):]));raise
if __name__=='__main__':main()
