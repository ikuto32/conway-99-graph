"""Explicit caller-selected native-free build orchestration. No auto-resume/skip."""
import argparse,hashlib,json,subprocess,sys,time,traceback
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'acceleration';B=A/'results';SPEC=Path(__file__).with_name(Path(__file__).stem+'_spec.md')
PRODUCER=A/'theory_20260930_exact_eight_campaign.py';MANIFEST=B/'20260930_exact_eight_campaign_preparation/campaign_manifest.json';POPULATION_GATE=B/'20260930_independent_review/exact_eight_campaign/summary.json'
PINS={PRODUCER:'9ebd87fea886f45fc916ad8afb9dc212fa089f760d4b96e55082926baef02c57',PRODUCER.with_name(PRODUCER.stem+'_spec.md'):'76d89e652dc0d90084863e4478b9d887658daac21aedfa20ffc72bf7bf48bf69',MANIFEST:'e7b07ea2f7c6b9f6738641afc22779a503841d5ac3da58d3873ebb0fa4b784ba',POPULATION_GATE:'e334293416c1048cf3a6e7c4bd8242892dc84e7f7d773bd388b506fdde77ea27',A/'theory_20260930_hadamard_four_profile_cnf.py':'0b4b737486974a499026bee4146cc7b461b654aeeb5af46e0553e908fa012f2f',A/'theory_20260930_hadamard_balanced_gram_cnf.py':'ffb5c842b29d0268073656ce948561af0557c24d067bf0260a9cc8f65ab07016',ROOT/'uv.lock':'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',ROOT/'pyproject.toml':'273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339'}
def sha(p):
    h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(p.read_bytes())
def need(x,m):
    if not x:raise ValueError(m)
def save(p,x):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def repo_file(name):
    need(type(name)is str and name and '\\'not in name and not Path(name).is_absolute(),'normalized relative path');p=(ROOT/name).resolve();need(p.is_relative_to(ROOT)and key(p)==name,'literal repository path');need(p.is_file(),'existing frozen file');return p
def selection_ids(selection,universe):
    need(selection['schema']=='EXACT_EIGHT_EXPLICIT_BUILD_SELECTION_V1','selection schema');need(selection['campaign_manifest_path']==key(MANIFEST)and selection['campaign_manifest_sha256']==PINS[MANIFEST],'same exact manifest')
    ids=selection['ordered_case_ids'];need(type(ids)is list and ids and all(type(x)is str for x in ids),'explicit nonempty ID list');need(len(ids)==len(set(ids)),'duplicate case refused, never silently removed')
    need(type(selection['selection_reason'])is str and bool(selection['selection_reason'].strip()),'explicit selection reason');byid={r['case_id']:r for r in universe['records']};need(len(byid)==792 and all(cid in byid for cid in ids),'exact complete-universe membership');return list(ids)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['plan','build']);ap.add_argument('--selection',type=Path,required=True);ap.add_argument('--selection-sha256',required=True);ap.add_argument('--attempt-id',required=True);ap.add_argument('--seconds',type=int,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic();bindings={};records=[];ids=[];stop=None
    def pin(p,w=None):
        v=sha(p);need(w is None or v==w,'unchanged '+key(p));bindings[key(p)]=v
    try:
        need(1<=args.seconds<=120,'bounded1..120seconds');need(args.attempt_id and args.attempt_id.isascii()and all(x.isalnum()or x in '_-'for x in args.attempt_id),'safe explicit attempt id')
        for p,h in PINS.items():pin(p,h)
        for p in[Path(__file__),SPEC,A/'theory_20260930_hadamard_four_profile_cnf_spec.md',A/'theory_20260930_hadamard_balanced_gram_cnf_spec.md']:pin(p)
        selection_path=args.selection.resolve();need(selection_path.is_relative_to(ROOT),'repository-contained selection');pin(selection_path,args.selection_sha256);selection=read(selection_path);authority=repo_file(selection['authorization_record_path']);pin(authority,selection['authorization_record_sha256'])
        u=read(MANIFEST);need(u['universe_size']==len(u['records'])==792 and not u['historical_profiles_subtracted']and not u['prior_exclusions_used'],'complete un-subtracted manifest');ids=selection_ids(selection,u);byid={r['case_id']:r for r in u['records']};gate=read(POPULATION_GATE);need(gate['status']=='INDEPENDENT_EXACT_EIGHT_CAMPAIGN_ENCODING_PASS'and gate['population_size']==792 and gate['inputs_sha256'][key(MANIFEST)]==PINS[MANIFEST],'independent population authentication only')
        plan=[]
        for cid in ids:
            r=byid[cid];folder=out/f"case_{r['case_index']:04d}";attempt=args.attempt_id+f"_case_{r['case_index']:04d}";cmd=[sys.executable,'-B',str(PRODUCER),'build','--campaign-manifest',str(MANIFEST),'--campaign-manifest-sha256',PINS[MANIFEST],'--case-id',cid,'--attempt-id',attempt,'--out',str(folder)];plan.append(dict(case_id=cid,case_index=r['case_index'],subset_index=r['subset_index'],attempt_id=attempt,output_path=key(folder),command=cmd))
        save(out/'plan.json',dict(schema='EXACT_EIGHT_EXPLICIT_BUILD_PLAN_V1',timestamp=datetime.now(timezone.utc).isoformat(),mode=args.mode,inputs_sha256=bindings,selection_path=key(selection_path),selection_sha256=args.selection_sha256,ordered_case_ids=ids,attempt_id=args.attempt_id,allocation_seconds=args.seconds,commands=plan,automatic_resume=False,automatic_skip=False,native_calls=0,previous_outcomes_consumed=0))
        if args.mode=='plan':save(out/'summary.json',dict(status='CANDIDATE_EXACT_EIGHT_EXPLICIT_BUILD_PLAN_PREPARED',inputs_sha256=bindings,selected_case_ids=ids,completed_formulas=0,records=[],pending_case_ids=ids,native_calls=0,producer_calls=0,independent_approval=False,outputs_sha256={key(p):sha(p)for p in out.iterdir()}));return
        producer_calls=0
        for i,p in enumerate(plan):
            remaining=args.seconds-(time.monotonic()-start)
            if remaining<1:stop=dict(reason='CUMULATIVE_BUILD_BUDGET_EXHAUSTED',next_case_id=p['case_id']);break
            folder=ROOT/p['output_path'];need(not folder.exists(),'new per-case folder');before=time.monotonic();producer_calls+=1;expired=False
            try:cp=subprocess.run(p['command'],cwd=ROOT,capture_output=True,timeout=remaining);stdout=cp.stdout;stderr=cp.stderr;code=cp.returncode
            except subprocess.TimeoutExpired as ex:stdout=ex.stdout or b'';stderr=ex.stderr or b'';code=None;expired=True
            (out/f'case_{i:03d}.stdout.log').write_bytes(stdout);(out/f'case_{i:03d}.stderr.log').write_bytes(stderr);receipt=dict(command=p['command'],case_id=p['case_id'],attempt_id=p['attempt_id'],actual_exit_code=code,outer_guard_expired=expired,wall_seconds=time.monotonic()-before,producer_calls=1,native_calls=0);save(out/f'case_{i:03d}.receipt.json',receipt)
            if expired or code!=0:stop=dict(reason='PRODUCER_TIMEOUT'if expired else'PRODUCER_NONZERO_EXIT',case_id=p['case_id'],receipt=receipt);break
            summary=read(folder/'summary.json');need(summary['status']=='CANDIDATE_EXACT_EIGHT_CAMPAIGN_LITERAL_FULL_GRAM_BUILT'and summary['case_id']==p['case_id']and summary['attempt_id']==p['attempt_id']and summary['native_calls']==0,'completed literal child')
            for n,h in {**summary['inputs_sha256'],**summary['outputs_sha256']}.items():need(sha(repo_file(n))==h,'complete child input/output identity')
            r=byid[p['case_id']];need(summary['case_index']==r['case_index']and summary['selected_full_count_sha256']==r['full_count_profile_sha256'],'literal full-count identity');files={n:dict(path=key(folder/n),sha256=sha(folder/n),bytes=(folder/n).stat().st_size)for n in['summary.json','instance.cnf','model.json','scope.json','selected_profile.json','initial_domains.json','selection.json','model_package.json']}
            records.append(dict(case_id=p['case_id'],case_index=r['case_index'],subset_index=r['subset_index'],attempt_id=p['attempt_id'],full_count_profile_sha256=r['full_count_profile_sha256'],selectors=summary['selectors'],variables=summary['variables'],clauses=summary['clauses'],initial_domain_sizes=summary['initial_domain_sizes'],files=files))
            save(out/f'checkpoint_{len(records):03d}.json',dict(status='CANDIDATE_EXPLICIT_BUILD_PREFIX',selected_case_ids=ids,completed_records=records,pending_case_ids=ids[len(records):],native_calls=0,producer_calls=producer_calls,selection_sha256=args.selection_sha256,automatic_resume=False,automatic_skip=False))
        for p,h in PINS.items():need(sha(p)==h,'post-build unchanged input')
        save(out/'summary.json',dict(status='CANDIDATE_EXACT_EIGHT_EXPLICIT_FORMULAS_COMPLETE'if len(records)==len(ids)else'CANDIDATE_EXACT_EIGHT_EXPLICIT_FORMULAS_PARTIAL',inputs_sha256=bindings,selected_case_ids=ids,records=records,completed_formulas=len(records),pending_case_ids=ids[len(records):],stop=stop,elapsed_seconds=time.monotonic()-start,producer_calls=producer_calls,native_calls=0,independent_approval=False,automatic_resume=False,automatic_skip=False,previous_outcomes_consumed=0,outputs_sha256={key(p):sha(p)for p in out.iterdir()if p.is_file()}));print(json.dumps(dict(completed=len(records),pending=len(ids)-len(records),summary_sha256=sha(out/'summary.json'))))
    except BaseException as ex:save(out/'failure.json',dict(error=repr(ex),traceback=traceback.format_exc(),inputs_sha256=bindings,completed_records=records,pending_case_ids=ids[len(records):],native_calls=0,automatic_resume=False,automatic_skip=False));raise
if __name__=='__main__':main()
