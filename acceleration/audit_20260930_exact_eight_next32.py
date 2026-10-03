"""Independent next32 selection, full encoding and raw-object audit; no producers imported."""
import argparse,copy,hashlib,json,platform,subprocess,sys,time,traceback
from datetime import datetime,timezone
from pathlib import Path
import audit_20260930_exact_eight_campaign as prior
ROOT=prior.ROOT;B=prior.B;I=prior.I;core=prior.core;codec=prior.codec
need=prior.need;same=prior.same;read=prior.read;sha=prior.sha;key=prior.key;save=prior.save
SELECTION=B/'20260930_exact_eight_next32_selection/selection.json';PLAN=ROOT/'acceleration/theory_20260930_exact_eight_next32_plan.md'
FIRST=I/'exact_eight_first12_proofs/summary.json';FIRST_ENCODING=I/'exact_eight_campaign/summary.json'
BATCH=B/'20260930_exact_eight_next32_consolidated/summary.json';ENC=I/'exact_eight_next32_cnfs/summary.json';SPEC=ROOT/'acceleration/audit_20260930_exact_eight_next32_spec.md'
STATUSES=dict(audit='INDEPENDENT_EXACT_EIGHT_NEXT32_ENCODING_PASS',calibrate='INDEPENDENT_EXACT_EIGHT_NEXT32_OBJECT_CALIBRATION_PASS',sat='INDEPENDENT_EXACT_EIGHT_NEXT32_SAT_OBJECT_PASS')
PINS=dict(prior.PINS);PINS.update({Path(prior.__file__):'bc1a14ac619986664bd689eca16eeaaa7ca840fbe2e154a777935dc8a0ecd58c',SELECTION:'b906256dcf706c7d03360cc2cb7e31e5dd09b52cec3ba994ae9600954aeb88cd',PLAN:'b91ff543c53b223b8db55d03d04a9266ffaca71b43bdbca10d85ddfa607bbd42',FIRST:'a47da7d0e2e70d61c51679477de5257c676a201e59cc8977b250ed75e8c05ef9',FIRST_ENCODING:'e334293416c1048cf3a6e7c4bd8242892dc84e7f7d773bd388b506fdde77ea27'})
PINS.update({ROOT/'acceleration/build_20260930_exact_eight_explicit_batch_v2.py':'c5acba24df4c224dce98510a6a77b4ca490ed0cd632f56d674fccffc0d0d7c2b',ROOT/'acceleration/build_20260930_exact_eight_explicit_batch_v2_spec.md':'17ed516985ab44ad1301b5c20020eb89fc9834b8147fe679d7294484531397be'})
# Final build pins are supplied explicitly by CLI after root completes this batch.
def selection_review(pop,pin):
    proof=read(FIRST);enc=read(FIRST_ENCODING);byid={r['case_id']:r for r in pop['records']};approved={r['case_id']:r for r in enc['checked_cases']}
    need(proof['status']=='INDEPENDENT_EXACT_EIGHT_FIRST12_LITERAL_PROOFS_PASS'and proof['completed_proof_replays']==12 and proof['SAT_pending']==proof['UNKNOWN']==0 and proof['pending_case_ids']==[],'complete exact first12 proof premise')
    need(proof['inputs_sha256'][key(FIRST_ENCODING)]==PINS[FIRST_ENCODING]and enc['status']=='INDEPENDENT_EXACT_EIGHT_CAMPAIGN_ENCODING_PASS','exact independent first12 formula premise')
    for gate in [proof,enc]:
        for path,h in gate['inputs_sha256'].items():pin(ROOT/path,h)
    pb=FIRST.parent/'claim_binding.json';pin(pb,proof['outputs_sha256'][key(pb)]);binding=read(pb);need(binding['id']=='C-FIXED-HADAMARD-EXACT-EIGHT-FIRST12-LITERAL-PROFILE-EXCLUSIONS'and binding['revision']==1,'exact approved skip claim')
    skip=[]
    for rec in proof['case_records']:
        cid=rec['case_id'];need(cid in byid and cid in approved and rec['outcome']=='UNSAT_VERIFIED'and rec['trace']['complete_proof']is True,'literal fully replayed case')
        need(rec['full_count_profile_sha256']==byid[cid]['full_count_profile_sha256']==approved[cid]['full_count_profile_sha256'],'same manifest raw count identity')
        for field in ['cnf','scope']:
            need(rec[field+'_path']==approved[cid][field+'_path']and rec[field+'_sha256']==approved[cid][field+'_sha256'],'same proof/encoding input');pin(ROOT/rec[field+'_path'],rec[field+'_sha256'])
        pin(ROOT/rec['trace']['path'],rec['trace']['sha256']);need((ROOT/rec['trace']['path']).stat().st_size==rec['trace']['bytes'],'complete saved proof size');skip.append(cid)
    need(skip==proof['selected_case_ids']==pop['first_batch_case_ids']and len(skip)==len(set(skip))==12,'only twelve authenticated skips')
    remaining=[r['case_id']for r in pop['records']if r['case_id']not in set(skip)];need(len(remaining)==780,'literal unresolved count')
    expected=dict(schema='EXACT_EIGHT_EXPLICIT_BUILD_SELECTION_V1',campaign_manifest_path=key(prior.POP),campaign_manifest_sha256=PINS[prior.POP],ordered_case_ids=remaining[:32],selection_reason='First32 manifest-ordered instances after removing only the12 independently proved campaign literal cases.',authorization_record_path=key(PLAN),authorization_record_sha256=PINS[PLAN],completed_proof_gate_path=key(FIRST),completed_proof_gate_sha256=PINS[FIRST],skipped_verified_case_ids=skip,population=792,unresolved_before_batch=780,selected_instances=32)
    need(same(expected,read(SELECTION)),'entire independently reconstructed next32 selection')
    return expected,byid,binding

def invocation_review(path,expected_hash,selected,selection_path,pin,byid):
    pin(path,expected_hash);batch=read(path);ids=selected['ordered_case_ids'];count=len(batch['records']);complete=count==len(ids)
    need(batch['status']==('CANDIDATE_EXACT_EIGHT_EXPLICIT_FORMULAS_COMPLETE'if complete else'CANDIDATE_EXACT_EIGHT_EXPLICIT_FORMULAS_PARTIAL')and batch['completed_formulas']==count,'honest complete/partial build boundary')
    need(batch['selected_case_ids']==ids and [r['case_id']for r in batch['records']]==ids[:count]and batch['pending_case_ids']==ids[count:],'exact complete prefix/pending suffix')
    need(batch['native_calls']==batch['previous_outcomes_consumed']==0 and all(batch[k]is False for k in ['independent_approval','automatic_resume','automatic_skip']),'explicit native-free invocation')
    need(batch['stop']is None if complete else batch['stop']is not None,'terminal build stop disclosure')
    for name,h in {**batch['inputs_sha256'],**batch['outputs_sha256']}.items():pin(ROOT/name,h)
    plan=read(path.parent/'plan.json');need(plan['schema']=='EXACT_EIGHT_EXPLICIT_BUILD_PLAN_V1'and plan['mode']=='build'and plan['inputs_sha256']==batch['inputs_sha256']and plan['ordered_case_ids']==ids,'entire build origin')
    need(plan['selection_path']==key(selection_path)and plan['selection_sha256']==sha(selection_path)and plan['allocation_seconds']==120 and plan['native_calls']==plan['previous_outcomes_consumed']==0 and plan['automatic_resume']is False and plan['automatic_skip']is False,'declared bounded explicit invocation')
    need(len(plan['commands'])==len(ids)and len({r['attempt_id']for r in batch['records']})==count,'all explicit distinct build attempts')
    names={'summary.json','instance.cnf','model.json','scope.json','selected_profile.json','initial_domains.json','selection.json','model_package.json'}
    for i,r in enumerate(batch['records']):
        original=byid[r['case_id']];folder=path.parent/f"case_{original['case_index']:04d}";attempt=plan['attempt_id']+f"_case_{original['case_index']:04d}"
        need(r['case_index']==original['case_index']and r['subset_index']==original['subset_index']and r['full_count_profile_sha256']==original['full_count_profile_sha256']and r['attempt_id']==attempt,'actual manifest case/attempt identity')
        command=[plan['commands'][i]['command'][0],'-B',str(ROOT/'acceleration/theory_20260930_exact_eight_campaign.py'),'build','--campaign-manifest',str(prior.POP),'--campaign-manifest-sha256',PINS[prior.POP],'--case-id',r['case_id'],'--attempt-id',attempt,'--out',str(folder)]
        want=dict(case_id=r['case_id'],case_index=r['case_index'],subset_index=r['subset_index'],attempt_id=attempt,output_path=key(folder),command=command);need(plan['commands'][i]==want,'entire raw build command')
        need(set(r['files'])==names,'complete named formula artifacts')
        for name,f in r['files'].items():
            p=ROOT/f['path'];need(p==folder/name,'literal named artifact');pin(p,f['sha256']);need(p.stat().st_size==f['bytes'],'artifact size')
        rec=read(path.parent/f'case_{i:03d}.receipt.json');need(rec['command']==command and rec['case_id']==r['case_id']and rec['attempt_id']==attempt and rec['actual_exit_code']==0 and rec['outer_guard_expired']is False and rec['producer_calls']==1 and rec['native_calls']==0,'exact successful build receipt')
        checkpoint=read(path.parent/f'checkpoint_{i+1:03d}.json');need(checkpoint==dict(status='CANDIDATE_EXPLICIT_BUILD_PREFIX',selected_case_ids=ids,completed_records=batch['records'][:i+1],pending_case_ids=ids[i+1:],native_calls=0,producer_calls=i+1,selection_sha256=sha(selection_path),automatic_resume=False,automatic_skip=False),'every complete immutable prefix checkpoint')
    if complete:need(batch['producer_calls']==count,'all successful invocation calls')
    elif batch['stop']['reason']=='CUMULATIVE_BUILD_BUDGET_EXHAUSTED':need(batch['producer_calls']==count and batch['stop']['next_case_id']==ids[count],'cooperative build stop')
    else:
        failed=read(path.parent/f'case_{count:03d}.receipt.json');need(batch['producer_calls']==count+1 and failed==batch['stop']['receipt']and failed['case_id']==ids[count]and failed['command']==plan['commands'][count]['command']and failed['native_calls']==0,'preserved incomplete producer call')
        need(failed['outer_guard_expired']or failed['actual_exit_code']!=0,'failed call cannot become completed formula')
        # Preserve/authenticate every unfinished child artifact without treating it as a formula.
        unfinished=ROOT/plan['commands'][count]['output_path']
        if unfinished.is_dir():
            for q in unfinished.rglob('*'):
                if q.is_file():pin(q)
    return batch

def batch_review(selection,byid,pin,expected_hash):
    pin(BATCH,expected_hash);batch=read(BATCH);ids=selection['ordered_case_ids']
    need(batch['schema']=='EXACT_EIGHT_EXPLICIT_BUILD_CONSOLIDATION_V1'and batch['status']=='CANDIDATE_EXACT_EIGHT_EXPLICIT_FORMULAS_COMPLETE'and batch['completed_formulas']==32,'complete32 consolidation only')
    need(batch['selected_case_ids']==ids and [r['case_id']for r in batch['records']]==ids and batch['pending_case_ids']==[]and batch['native_calls']==0 and all(batch[k]is False for k in ['automatic_resume','automatic_skip','independent_approval']),'exact32 ordered candidate records')
    need(batch['original_selection']==dict(path=key(SELECTION),sha256=PINS[SELECTION]),'original authenticated selection')
    for name,h in batch['inputs_sha256'].items():pin(ROOT/name,h)
    pin(ROOT/'acceleration/continue_20260930_exact_eight_next32.py',batch['source_sha256'])
    refs=batch['build_summaries'];continuations=batch['continuation_selections'];need(len(refs)==len(continuations)+1 and len(refs)>=1,'explicit invocation chain')
    aggregate=[];calls=0;previous=None
    for j,ref in enumerate(refs):
        path=ROOT/ref['path']
        if j==0:selected=selection;sp=SELECTION
        else:
            x=continuations[j-1];sp=ROOT/x['path'];pin(sp,x['sha256']);selected=read(sp);pin(ROOT/selected['authorization_record_path'],selected['authorization_record_sha256'])
            expected=copy.deepcopy(selection);expected.update(ordered_case_ids=ids[len(aggregate):],selection_reason='Explicit root continuation of the ten pending build IDs after the preserved120-second partial invocation; no mathematical result inferred.',authorization_record_path=selected['authorization_record_path'],authorization_record_sha256=selected['authorization_record_sha256'],parent_selection_path=key(SELECTION),parent_selection_sha256=PINS[SELECTION],partial_build_path=refs[j-1]['path'],partial_build_sha256=refs[j-1]['sha256'],counts=dict(parent_selected=32,previously_completed_builds=len(aggregate),selected_pending_builds=32-len(aggregate)))
            need(same(selected,expected)and previous['pending_case_ids']==selected['ordered_case_ids'],'exact independently reconstructed explicit pending selection')
        actual=invocation_review(path,ref['sha256'],selected,sp,pin,byid);aggregate.extend(actual['records']);calls+=actual['producer_calls'];previous=actual
    need(aggregate==batch['records']and calls==batch['producer_calls']and len({r['case_id']for r in aggregate})==32,'exact complete32 union; no unfinished attempt promoted')
    return batch

def main():
    global BATCH
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=list(STATUSES));ap.add_argument('--batch-summary',type=Path);ap.add_argument('--batch-summary-sha256');ap.add_argument('--case-id');ap.add_argument('--encoding-gate',type=Path);ap.add_argument('--encoding-gate-sha256');ap.add_argument('--assignment',type=Path);ap.add_argument('--native-output',type=Path);ap.add_argument('--decoded',type=Path);ap.add_argument('--native-driver',type=Path);ap.add_argument('--native-driver-sha256');ap.add_argument('--native-spec',type=Path);ap.add_argument('--native-spec-sha256');ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};start=time.perf_counter()
    if args.batch_summary:BATCH=args.batch_summary.resolve()
    need(BATCH.is_relative_to(ROOT),'repository-contained consolidation')
    def pin(p,h=None):
        p=p.resolve();name=key(p)
        if name not in pins:pins[name]=sha(p)
        need(h is None or pins[name]==h,'hash '+name)
    try:
        for p,h in PINS.items():pin(p,h)
        for p in [Path(__file__),SPEC]:pin(p)
        closure=prior.static_closure(Path(__file__))
        for p in closure:pin(p)
        need(all(not p.name.startswith(('theory_','native_'))for p in closure),'no producer/native imports')
        pop=prior.population(pin);selection,byid,skip_binding=selection_review(pop,pin)
        if args.mode!='audit':
            need(args.encoding_gate and args.encoding_gate.resolve()==ENC and args.encoding_gate_sha256,'explicit exact next32 gate');pin(args.encoding_gate,args.encoding_gate_sha256);eg=read(args.encoding_gate);need(eg['status']==STATUSES['audit']and eg['selected_case_ids']==selection['ordered_case_ids']and eg['complete_formulas']==32,'approved exact32 population')
            for name,h in eg['inputs_sha256'].items():pin(ROOT/name,h)
            if not args.batch_summary:BATCH=ROOT/eg['batch_summary_path']
            need(key(BATCH)==eg['batch_summary_path'],'same calibrated consolidation path');batch_hash=eg['inputs_sha256'][key(BATCH)]
            if args.batch_summary_sha256:need(args.batch_summary_sha256==batch_hash,'same frozen build summary')
        else:need(args.batch_summary_sha256,'explicit terminal build SHA required');batch_hash=args.batch_summary_sha256;eg=None
        batch=batch_review(selection,byid,pin,batch_hash);ids=selection['ordered_case_ids'];need(args.case_id is None if args.mode!='sat'else args.case_id in ids,'SAT case among32 approved formulas')
        chosen=batch['records']if args.mode!='sat'else[r for r in batch['records']if r['case_id']==args.case_id];catalogue=core.prior.catalogue();checked=[];cases=[]
        for rec in chosen:
            f=rec['files']['summary.json'];row,data=prior.case_review(byid[rec['case_id']],ROOT/f['path'],f['sha256'],pin,catalogue,rec['attempt_id']);need([row[k]for k in ['variables','clauses','selectors','initial_domain_sizes']]==[rec[k]for k in ['variables','clauses','selectors','initial_domain_sizes']],'all independently derived case dimensions');checked.append(row);cases.append((row['case_id'],data))
            if eg is not None:need(row in eg['checked_cases'],'same independently approved formula')
            print(json.dumps(dict(checked_case=row['case_id'],complete_clauses=row['clauses'],count=len(checked))),flush=True)
        native_closure=[]
        if args.mode=='calibrate':
            need(args.native_driver and args.native_driver_sha256 and args.native_spec and args.native_spec_sha256,'exact fresh native source/spec');pin(args.native_driver,args.native_driver_sha256);pin(args.native_spec,args.native_spec_sha256)
            ns=prior.static_closure(args.native_driver)|{args.native_spec.resolve(),ROOT/'acceleration/theory_20260930_exact_eight_campaign_spec.md',ROOT/'acceleration/theory_20260930_hadamard_balanced_gram_cnf.py'}
            for p in ns:pin(p)
            native_closure=sorted(map(key,ns))
        if args.mode in ('audit','calibrate'):
            control=prior.controls(cases,out);attacks=[]
            for name,mutate in [('skip_unproved',lambda x:x['skipped_verified_case_ids'].append(x['ordered_case_ids'][0])),('drop_selected',lambda x:x['ordered_case_ids'].pop()),('reorder',lambda x:x['ordered_case_ids'].reverse()),('false_prior_gate',lambda x:x.__setitem__('completed_proof_gate_sha256','0'*64))]:
                bad=copy.deepcopy(selection);mutate(bad);need(not same(bad,selection),'rejected selection attack '+name);attacks.append(name)
            control['selection_corruptions']=attacks;control['actual_clause_corruptions']=[]
            for row,(_,data)in zip(checked,cases):
                model,scope,profile,clauses=data;raw=(ROOT/row['cnf_path']).read_bytes();need(codec.cnf_bytes(clauses[:-1],model['variables'])!=raw,'dropped actual clause rejected');v=clauses[0][0];clauses[0][0]=-v;need(codec.cnf_bytes(clauses,model['variables'])!=raw,'flipped actual literal rejected');clauses[0][0]=v;control['actual_clause_corruptions'].append(dict(case_id=row['case_id'],mutations=2))
            save(out/'controls.json',control)
        else:
            control=None;need(args.assignment and args.native_output,'full raw SAT inputs');pin(args.assignment);pin(args.native_output);model,scope,profile,clauses=cases[0][1];values=codec.assignment(read(args.assignment)['assignment'],model['variables']);need(values==codec.native(args.native_output.read_text(encoding='utf8'),model['variables']),'complete native/JSON equality')
            result=core.decode_and_verify(values,model,scope,profile,clauses);obj=prior.native_decode_shape(result,model,scope,profile);obj['model_sha256']=checked[0]['model_sha256'];obj['scope_sha256']=checked[0]['scope_sha256']
            if args.decoded:pin(args.decoded);need(same(obj,read(args.decoded)),'complete independently decoded factor')
            save(out/'independent_Gram_factor.json',obj);save(out/'independent_case_identity.json',checked[0])
        stamp=datetime.now(timezone.utc).isoformat();need(time.perf_counter()-start<240,'240-second complete32 checking allocation')
        if args.mode=='audit':
            save(out/'claim_binding.json',dict(id='C-FIXED-HADAMARD-EXACT-EIGHT-NEXT32-GRAM-ENCODINGS',revision=1,kind='encoding',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',statement='For each of the exact next32 selected literal count profiles, its complete CNF is satisfiable iff the fixed six-prism Hadamard support admits a binary36x60 factor with that count table, full prescribed integer Gram and within-triplicate caps, modulo independent equal-support column relabellings. All initial domains are complete and auxiliary assignments unique.',scope='Only32 actual formulas. Selection skips exactly the twelve authenticated complete first-batch exclusions from the unchanged792 manifest. No native result, cross-group cap, residualD or wider profile exclusion.',assumptions=['Frozen fixed support/local catalogue and independently authenticated complete block-survivor manifest.'],dependencies=[dict(id='C-FIVE-FIXED-HADAMARD20-SUPPORT-PROJECTIONS',revision=1,relation='premise'),dict(id='C-FIXED-HADAMARD-SIX-PRISM-LOCAL-TRIPLE-CENSUS',revision=1,relation='verification_dependency'),dict(id='C-FIXED-HADAMARD-EXACT-EIGHT-SEPARATE-GRAM-BLOCK-SCREEN',revision=1,relation='uses_result'),dict(id=skip_binding['id'],revision=1,relation='uses_result')],verifier='/root/structural_attack',producer='/root/eight_domain_audit (generic formula), /root (selection/build)',method='Independent manifest-order/proof-bound skip audit and literal reconstruction of every initial domain, Gram coefficient, auxiliary relation and actual clause in all32 formulas; generic and corruption controls.',shared_components=['Frozen independent campaign checking functions and generic raw-count core; no producer/native imports.'],inputs_sha256=pins,checked_cases=checked,artifact_availability='LOCAL_ONLY',availability_reason='Pending publication.',external_review=None,external_review_reason='Independent internal review only.',created_at=stamp,updated_at=stamp))
        save(out/'summary.json',dict(status=STATUSES[args.mode],timestamp=stamp,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],python=platform.python_version(),inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in out.rglob('*')if p.is_file()},batch_summary_path=key(BATCH),batch_summary_sha256=batch_hash,population_size=792,unresolved_before_batch=780,skipped_verified_case_ids=selection['skipped_verified_case_ids'],selected_case_ids=ids,complete_formulas=len(checked),checked_cases=checked,complete_clauses_checked=sum(r['clauses']for r in checked),controls=control,native_source_closure=native_closure,checker_source_closure=sorted(map(key,closure)),elapsed_seconds=time.perf_counter()-start,solver_calls=0,target_resolution=False,cross_group_column_caps_encoded=False,residual_D_encoded=False));print(json.dumps(dict(status=STATUSES[args.mode],summary_sha256=sha(out/'summary.json'),source_sha256=sha(Path(__file__)))))
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),traceback=traceback.format_exc(),source_sha256=sha(Path(__file__)),inputs_sha256=pins));raise
if __name__=='__main__':main()
