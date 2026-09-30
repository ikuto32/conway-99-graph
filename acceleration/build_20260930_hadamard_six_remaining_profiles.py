"""Bounded54-case build-only launcher with immutable per-case checkpoints."""
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
import argparse,gzip,hashlib,json,platform,shutil,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results'
SOURCE=ROOT/'acceleration/theory_20260930_hadamard_six_profile_cnf.py';PROTOCOL=ROOT/'acceleration/theory_20260930_hadamard_six_profile_cnf_spec.md'
SELECTION=B/'20260930_hadamard_six_remaining_selection/selection.json'
PINS={SOURCE:'cac3d732f9045b32b77648acfb246f3a6c842724ec232bd10321806bb079ca0a',PROTOCOL:'0a55b28ed0e4869764aafedecb48471c60e8ad19b7eb79bceeca5838b915b520',SELECTION:'64035c4d033c9b7d605f556bf69447780bb185ba7bd0fd0c7733ab9e1b0e741f',ROOT/'acceleration/select_20260930_hadamard_six_remaining_profiles.py':'e78c11ee52105d054ce5dbcabca80cf0e1ae2b68ce74de2061156c439b39bb32',ROOT/'acceleration/select_20260930_hadamard_six_remaining_profiles_spec.md':'5dd604eda923e5427ee1a9ee547000d85d2117e92871f9be5a5d4449ede9a83b',ROOT/'acceleration/theory_20260930_hadamard_four_profile_cnf.py':'0b4b737486974a499026bee4146cc7b461b654aeeb5af46e0553e908fa012f2f',ROOT/'acceleration/theory_20260930_hadamard_balanced_gram_cnf.py':'ffb5c842b29d0268073656ce948561af0557c24d067bf0260a9cc8f65ab07016',ROOT/'uv.lock':'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',ROOT/'pyproject.toml':'273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339'}
LIMITS=dict(wall_seconds=180,minimum_remaining_seconds_to_launch=5,host_free_reserve_bytes=3*1024**3,native_solver_calls=0,automatic_retry=False)
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(Path(p).read_bytes())
def save(p,x):
    with Path(p).open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
def validate_completed(record,expected):
    summarypath=ROOT/record['summary_path'];need(sha(summarypath)==record['summary_sha256'],'case summary identity');s=read(summarypath);need(s['selected_profile_id']==expected['profile_id'] and s['selected_profile_sha256']==expected['profile_sha256'],'raw literal profile binding')
    for name,value in s['outputs_sha256'].items():need(sha(ROOT/name)==value,'completed producer output identity')
    for field in ('selectors','variables','clauses'):need(s[field]==expected['expected_'+field]==record[field],'exact derived formula dimensions')
    need(s['exceptional_initial_choices_per_group']==expected['initial_domain_sizes'] and not s['arc_pruning_used'] and not s['orbit_coverage_used'] and not s['cross_group_column_caps_encoded'] and not s['residual_D_encoded'],'unpruned exact initial profile scope')
    for field in ('cnf','model','scope','model_package'):
        path=ROOT/record[field+'_path'];need(sha(path)==record[field+'_sha256'],'direct raw output pin')
    scope=read(ROOT/record['scope_path']);need(scope['exceptional_groups']==expected['groups'] and scope['initial_domain_references']==expected['initial_domains'],'full initial domain input binding')
    package=read(ROOT/record['model_package_path']);compressed=ROOT/package['gzip_path'];need(sha(compressed)==package['gzip_sha256'],'model gzip identity');digest=hashlib.sha256();size=0
    with gzip.open(compressed,'rb') as f:
        for data in iter(lambda:f.read(1048576),b''):digest.update(data);size+=len(data)
    need(digest.hexdigest()==record['model_sha256']==package['raw_sha256'] and size==package['raw_bytes'],'complete recovered model identity')
    return dict(raw_bytes=size,gzip_bytes=compressed.stat().st_size,recovered_sha256=digest.hexdigest())
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--resume-checkpoint',type=Path);ap.add_argument('--resume-checkpoint-sha256');a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic();records=[];attempts=[]
    try:
        for p,h in PINS.items():need(sha(p)==h,'frozen build input '+key(p))
        inputs={key(p):h for p,h in PINS.items()}
        for p in (Path(__file__),Path(__file__).with_name('build_20260930_hadamard_six_remaining_profiles_spec.md')):inputs[key(p)]=sha(p)
        selection=read(SELECTION);expected=selection['remaining_records'];ids=selection['remaining_profile_ids'];need(len(ids)==54 and ids==sorted(set(ids)) and ids==[r['profile_id'] for r in expected] and 'rank4_00_profile_0000' not in ids,'exact54-case selection')
        if a.resume_checkpoint:
            need(a.resume_checkpoint_sha256 is not None and sha(a.resume_checkpoint)==a.resume_checkpoint_sha256,'explicit resume identity');prior=read(a.resume_checkpoint);need(prior['inputs_sha256']==inputs and prior['limits']==LIMITS and prior['selection']==ids,'immutable resume protocol');records=prior['completed_records'];need([r['profile_id'] for r in records]==ids[:len(records)],'completed selection prefix')
            for r,ex in zip(records,expected):validate_completed(r,ex)
        else:need(a.resume_checkpoint_sha256 is None,'resume hash requires checkpoint')
        need(shutil.disk_usage(ROOT).free>=LIMITS['host_free_reserve_bytes'],'initial disk reserve')
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=inputs,limits=LIMITS,selection=ids,resume_checkpoint=None if a.resume_checkpoint is None else key(a.resume_checkpoint),resume_checkpoint_sha256=a.resume_checkpoint_sha256,wave=23,native_solver_calls=0))
        base=dict(inputs_sha256=inputs,limits=LIMITS,selection=ids);save(out/'checkpoint_initial.json',dict(schema='REMAINING54_PROFILE_BUILD_CHECKPOINT_V1',**base,completed_records=records,attempt_records=attempts,stop_reason=None));stop='ALL_SELECTED_FORMULAS_BUILT'
        for index in range(len(records),len(expected)):
            remaining=180-(time.monotonic()-start)
            if remaining<5:stop='WALL_ALLOCATION_RESERVE';break
            if shutil.disk_usage(ROOT).free<LIMITS['host_free_reserve_bytes']:stop='HOST_DISK_RESERVE';break
            ex=expected[index];pid=ex['profile_id'];dest=out/pid;command=[sys.executable,'-B',str(SOURCE),'--profile-id',pid,'--out',str(dest)];began=time.monotonic();timedout=False
            try:result=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=remaining);stdout=result.stdout;stderr=result.stderr;code=result.returncode
            except subprocess.TimeoutExpired as error:stdout=error.stdout or b'';stderr=error.stderr or b'';code=None;timedout=True
            stdoutpath=out/f'{pid}.stdout.log';stderrpath=out/f'{pid}.stderr.log';stdoutpath.write_bytes(stdout);stderrpath.write_bytes(stderr);receipt=out/f'{pid}.receipt.json';attempt=dict(index=index,profile_id=pid,command=command,cwd=str(ROOT),exit_code=code,outer_timeout=timedout,outer_timeout_seconds=remaining,wall_seconds=time.monotonic()-began,source_sha256=PINS[SOURCE],stdout_path=key(stdoutpath),stdout_sha256=sha(stdoutpath),stderr_path=key(stderrpath),stderr_sha256=sha(stderrpath));save(receipt,attempt);attempts.append(dict(**attempt,receipt_path=key(receipt),receipt_sha256=sha(receipt)))
            if code!=0:stop='BUILD_TIMEOUT' if timedout else 'BUILD_ERROR';break
            s=read(dest/'summary.json');record=dict(index=index,profile_id=pid,summary_path=key(dest/'summary.json'),summary_sha256=sha(dest/'summary.json'),cnf_path=key(dest/'instance.cnf'),cnf_sha256=sha(dest/'instance.cnf'),model_path=key(dest/'model.json'),model_sha256=sha(dest/'model.json'),scope_path=key(dest/'scope.json'),scope_sha256=sha(dest/'scope.json'),model_package_path=key(dest/'model_package.json'),model_package_sha256=sha(dest/'model_package.json'),selectors=s['selectors'],variables=s['variables'],clauses=s['clauses'],receipt_path=key(receipt),receipt_sha256=sha(receipt));record['parent_streamed_model_recovery']=validate_completed(record,ex);records.append(record)
            save(out/f'checkpoint_{index:03d}.json',dict(schema='REMAINING54_PROFILE_BUILD_CHECKPOINT_V1',**base,completed_records=records,attempt_records=attempts,stop_reason=None))
            with (out/'progress.jsonl').open('a',encoding='utf-8',newline='\n') as f:f.write(json.dumps(record)+'\n')
            print(json.dumps(dict(profile_id=pid,completed=len(records),selected=54,variables=s['variables'],clauses=s['clauses'],elapsed_seconds=time.monotonic()-start)),flush=True)
        checkpoint=dict(schema='REMAINING54_PROFILE_BUILD_CHECKPOINT_V1',**base,completed_records=records,attempt_records=attempts,stop_reason=stop);save(out/'checkpoint.json',checkpoint);summary=dict(status='CANDIDATE_REMAINING54_SIX_PROFILE_FORMULAS_BUILT' if len(records)==54 else 'CANDIDATE_REMAINING54_BUILD_PARTIAL',inputs_sha256=inputs,selection=ids,records=records,attempts_this_invocation=len(attempts),completed_formulas=len(records),pending_profiles=ids[len(records):],failed_attempts_this_invocation=sum(r['exit_code']!=0 for r in attempts),stop_reason=stop,checkpoint_path=key(out/'checkpoint.json'),checkpoint_sha256=sha(out/'checkpoint.json'),dimension_histogram={str(k):v for k,v in Counter((r['selectors'],r['variables'],r['clauses']) for r in records).items()},total_raw_model_bytes=sum(r['parent_streamed_model_recovery']['raw_bytes'] for r in records),total_gzip_model_bytes=sum(r['parent_streamed_model_recovery']['gzip_bytes'] for r in records),elapsed_seconds=time.monotonic()-start,native_solver_calls=0,independent_approval=False,target_resolution=False,artifact_availability='LOCAL_ONLY',wave=23,scope='54 separate literal-profile Gram formulas, all initial domains. Cross-group caps and residualD omitted; no native outcomes or encoding approval.');save(out/'summary.json',summary);print(json.dumps({k:v for k,v in summary.items() if k not in ('inputs_sha256','selection','records')}))
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),source_sha256=sha(Path(__file__)),completed_records=records,attempt_records=attempts,native_solver_calls=0));raise
if __name__=='__main__':main()
