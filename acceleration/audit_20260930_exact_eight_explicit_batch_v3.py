"""Independent explicit1..64 formula and raw-object review; no producer imports."""
import argparse,copy,hashlib,json,platform,subprocess,sys,time,traceback
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
import audit_20260930_exact_eight_campaign as prior
import audit_20260930_exact_eight_next32 as receipts
ROOT=prior.ROOT;B=prior.B;I=prior.I;core=prior.core;codec=prior.codec
need=prior.need;same=prior.same;read=prior.read;sha=prior.sha;key=prior.key;save=prior.save
SPEC=ROOT/'acceleration/audit_20260930_exact_eight_explicit_batch_v3_spec.md'
STATUSES=dict(audit='INDEPENDENT_EXACT_EIGHT_EXPLICIT_BATCH_ENCODING_PASS',calibrate='INDEPENDENT_EXACT_EIGHT_EXPLICIT_BATCH_OBJECT_CALIBRATION_PASS',sat='INDEPENDENT_EXACT_EIGHT_EXPLICIT_BATCH_SAT_OBJECT_PASS')
PINS=dict(prior.PINS)
PINS.update({Path(prior.__file__):'bc1a14ac619986664bd689eca16eeaaa7ca840fbe2e154a777935dc8a0ecd58c',Path(receipts.__file__):'7f55b64aab1f0a96aec07d537dfd8927c50496e241c92ab8810ac6a887e38b6c',ROOT/'acceleration/build_20260930_exact_eight_explicit_batch_v2.py':'c5acba24df4c224dce98510a6a77b4ca490ed0cd632f56d674fccffc0d0d7c2b',ROOT/'acceleration/build_20260930_exact_eight_explicit_batch_v2_spec.md':'17ed516985ab44ad1301b5c20020eb89fc9834b8147fe679d7294484531397be'})
PROOF_STATUSES={'INDEPENDENT_EXACT_EIGHT_FIRST12_LITERAL_PROOFS_PASS':'SAT_pending','INDEPENDENT_EXACT_EIGHT_NEXT32_LITERAL_PROOFS_PASS':'SAT_verified','INDEPENDENT_EXACT_EIGHT_EXPLICIT_BATCH_LITERAL_PROOFS_PASS':'SAT_verified'}
ENCODING_STATUSES={'INDEPENDENT_EXACT_EIGHT_CAMPAIGN_ENCODING_PASS','INDEPENDENT_EXACT_EIGHT_NEXT32_ENCODING_PASS',STATUSES['audit']}

def proof_skips(selection,byid,pin):
    skipped=[];bindings=[];review=[]
    for ref in selection['completed_proof_gates']:
        path=ROOT/ref['path'];pin(path,ref['sha256']);proof=read(path)
        need(proof['status']in PROOF_STATUSES,'recognized independent complete-proof report')
        count=proof['completed_proof_replays'];need(set(ref)<=set(['path','sha256','completed_cases'])and ('completed_cases'not in ref or ref['completed_cases']==count),'exact supplied proof count');need(type(count)is int and count>0 and proof['completed_proof_replays']==count and proof[PROOF_STATUSES[proof['status']]]==proof['UNKNOWN']==0 and proof['pending_case_ids']==[],'complete exact proof premise')
        for name,h in proof['inputs_sha256'].items():pin(ROOT/name,h)
        for name,h in proof['outputs_sha256'].items():pin(ROOT/name,h)
        bp=path.parent/'claim_binding.json';need(proof['outputs_sha256'].get(key(bp))==sha(bp),'bound original proof claim');binding=read(bp);need(binding['revision']==1 and binding['status']=='VERIFIED','approved literal exclusion binding');bindings.append(binding)
        encodings=[]
        for name,h in proof['inputs_sha256'].items():
            if name.endswith('/summary.json'):
                candidate=read(ROOT/name)
                if candidate.get('status')in ENCODING_STATUSES:encodings.append(candidate)
        proved=proof['case_records'];need(len(proved)==count and [r['case_id']for r in proved]==proof['selected_case_ids'],'all exact proof rows/order')
        for row in proved:
            cid=row['case_id'];need(cid in byid and cid not in skipped and row['outcome']=='UNSAT_VERIFIED'and row['trace']['complete_proof']is True,'distinct fully checked literal skip')
            candidates=[r for enc in encodings for r in enc['checked_cases']if r['case_id']==cid and r['cnf_path']==row['cnf_path']and r['cnf_sha256']==row['cnf_sha256']and r['scope_path']==row['scope_path']and r['scope_sha256']==row['scope_sha256']]
            need(len(candidates)==1,'one exact independently approved formula for proof');encoded=candidates[0];raw=read(ROOT/encoded['profile_path'])
            need(row['full_count_profile_sha256']==encoded['full_count_profile_sha256']==byid[cid]['full_count_profile_sha256'],'same canonical raw count identity')
            need(core.counts_vector(raw['coordinate_group_fibre_counts'])==core.counts_vector(byid[cid]['raw_representative']['counts']),'literal profile/count byte equality')
            for field in ['cnf','scope']:pin(ROOT/row[field+'_path'],row[field+'_sha256'])
            trace=row['trace'];pin(ROOT/trace['path'],trace['sha256']);need((ROOT/trace['path']).stat().st_size==trace['bytes'],'saved complete proof size')
            replay=row['replay'];need(replay['accepted']is True and replay['expected_acceptance']is True and replay['actual_exit_code']==0 and replay['cnf_sha256']==row['cnf_sha256']and replay['proof_sha256']==trace['sha256'],'exact accepted complete replay identity')
            skipped.append(cid);review.append(dict(case_id=cid,full_count_profile_sha256=row['full_count_profile_sha256'],proof_gate=ref,cnf_sha256=row['cnf_sha256'],proof_sha256=trace['sha256'],proof_bytes=trace['bytes']))
    need(len(skipped)==len(set(skipped)),'no repeated skips')
    return skipped,bindings,review

def inventory_review(selection,pop,pin):
    ref=selection['inventory_gate'];path=ROOT/ref['path'];pin(path,ref['sha256']);gate=read(path)
    need(gate['status']=='INDEPENDENT_EXACT_EIGHT_CAMPAIGN_INVENTORY_PASS'and gate['cases']==792 and gate['initial_domains']==15840,'complete independently checked domain inventory')
    for name,h in gate['inputs_sha256'].items():pin(ROOT/name,h)
    for name,h in gate['outputs_sha256'].items():pin(ROOT/name,h)
    rr=selection['inventory_records'];rp=ROOT/rr['path'];pin(rp,rr['sha256']);need(gate['outputs_sha256'].get(key(rp))==rr['sha256'],'bound independent inventory records')
    data=read(rp);need(data['complete_class_ranklists_checked']==6061 and data['domain_records_checked']==15840,'all complete initial classes')
    rows=data['records'];need([r['case_id']for r in rows]==[r['case_id']for r in pop['records']],'entire same792 inventory order')
    classes=Counter();domain_sizes=Counter()
    for r,p in zip(rows,pop['records']):
        need(all(r[k]==p[k]for k in ['case_id','case_index','subset_index','full_count_profile_sha256']),'complete inventory identity')
        sizes=r['initial_domain_sizes'];need(len(sizes)==20 and all(type(x)is int and x>0 for x in sizes),'positive literal domains')
        s=sum(sizes);need(r['computed_formula_dimensions']==dict(selectors=s,variables=2*s+5380,clauses=49*s+60400),'inventory exact schema dimensions');classes[s]+=1;domain_sizes.update(sizes)
    distribution=[dict(selectors=s,estimated_variables=2*s+5380,estimated_clauses=49*s+60400,cases=n)for s,n in sorted(classes.items())]
    need(distribution==gate['formula_dimension_distribution']and {str(k):v for k,v in domain_sizes.items()}==gate['group_domain_size_distribution'],'complete independent distribution')
    bp=path.parent/'claim_binding.json';pin(bp);binding=read(bp);need(binding['verification']['report']==key(path) and binding['verification']['report_sha256']==ref['sha256'] and binding['verification']['status']==gate['status'] and binding['revision']==1 and binding['status_recommendation']=='VERIFIED','append-only inventory claim explicitly binds frozen report')
    return {r['case_id']:r for r in rows},classes,read(bp)

def validate_selection(actual,expected):
    need(same(actual,expected),'entire independently reconstructed allocation')

def prefix_selection(universe,skipped,n):
    need(type(n)is int and 1<=n<=64,'bounded explicit prefix size')
    need(type(universe)is list and type(skipped)is list and all(type(x)is str for x in universe+skipped),'literal string-ID lists')
    need(len(universe)==len(set(universe)),'unique ordered universe')
    need(len(skipped)==len(set(skipped))and set(skipped)<=set(universe),'distinct authenticated skips in universe')
    remaining=[cid for cid in universe if cid not in set(skipped)]
    need(len(remaining)>=n,'enough unproved literal cases')
    return remaining[:n]

def prefix_controls():
    universe=['case_'+str(i)for i in range(100)];skipped=['case_'+str(i)for i in [0,3,17,42,99]];expected=[x for x in universe if x not in skipped];positives=[];negatives=[]
    for n in range(1,65):
        need(prefix_selection(universe,skipped,n)==expected[:n]and prefix_selection(universe,list(reversed(skipped)),n)==expected[:n],'all bounded ordered prefixes independent of skip order');positives.append(n)
    for label,u,s,n in [('zero',universe,skipped,0),('too_many',universe,skipped,65),('bool',universe,skipped,True),('duplicate_universe',universe+[universe[0]],skipped,1),('duplicate_skip',universe,skipped+[skipped[0]],1),('unknown_skip',universe,skipped+['absent'],1),('short_remaining',universe[:6],universe[:5],2),('string_universe','abc',[],1),('string_skips',universe,'abc',1),('nonstr_ID',universe+[1],skipped,1)]:
        try:prefix_selection(u,s,n)
        except ValueError:negatives.append(label)
        else:raise ValueError('accepted prefix corruption '+label)
    return dict(all_sizes_1_to_64=positives,skip_order_controls=64,rejected=negatives)

def selection_review(selection_path,pop,pin):
    selection=read(selection_path);byid={r['case_id']:r for r in pop['records']};ids=selection['ordered_case_ids']
    need(selection['schema']=='EXACT_EIGHT_EXPLICIT_BUILD_SELECTION_V1'and selection['selection_policy']in ['FIRST_UNPROVED_PER_SELECTOR_SIZE_CLASS_V1','FIRST_UNPROVED_MANIFEST_PREFIX_V1'],'supported explicit allocation policy')
    need(1<=len(ids)<=64 and len(set(ids))==len(ids)and all(i in byid for i in ids),'bounded distinct explicit manifest cases')
    pin(ROOT/selection['authorization_record_path'],selection['authorization_record_sha256'])
    skipped,bindings,review=proof_skips(selection,byid,pin)
    if selection['selection_policy']=='FIRST_UNPROVED_MANIFEST_PREFIX_V1':
        chosen=prefix_selection([r['case_id']for r in pop['records']],skipped,selection['selected_instances'])
        need(type(selection['selection_reason'])is str and selection['selection_reason'],'pinned editorial allocation description')
        expected=dict(schema='EXACT_EIGHT_EXPLICIT_BUILD_SELECTION_V1',selection_policy='FIRST_UNPROVED_MANIFEST_PREFIX_V1',campaign_manifest_path=key(prior.POP),campaign_manifest_sha256=PINS[prior.POP],ordered_case_ids=chosen,selection_reason=selection['selection_reason'],authorization_record_path=selection['authorization_record_path'],authorization_record_sha256=selection['authorization_record_sha256'],completed_proof_gates=selection['completed_proof_gates'],skipped_verified_case_ids=skipped,population=792,unresolved_before_batch=792-len(skipped),selected_instances=len(chosen))
        validate_selection(selection,expected)
        return selection,byid,None,bindings,None,review
    inventory,classes,ib=inventory_review(selection,pop,pin)
    candidates={}
    for r in pop['records']:
        cid=r['case_id'];s=inventory[cid]['computed_formula_dimensions']['selectors']
        if cid not in set(skipped)and s not in candidates:candidates[s]=cid
    sizes=sorted(candidates);chosen=[candidates[s]for s in sizes]
    expected=dict(schema='EXACT_EIGHT_EXPLICIT_BUILD_SELECTION_V1',selection_policy='FIRST_UNPROVED_PER_SELECTOR_SIZE_CLASS_V1',campaign_manifest_path=key(prior.POP),campaign_manifest_sha256=PINS[prior.POP],ordered_case_ids=chosen,selection_reason='First unproved manifest member in each independently inventoried selector-size class; classes ordered by increasing selector count. No class-wide exclusion is inferred.',authorization_record_path=selection['authorization_record_path'],authorization_record_sha256=selection['authorization_record_sha256'],completed_proof_gates=selection['completed_proof_gates'],inventory_gate=selection['inventory_gate'],inventory_records=selection['inventory_records'],skipped_verified_case_ids=skipped,population=792,unresolved_before_batch=792-len(skipped),selected_instances=len(chosen),selected_selector_sizes=sizes,class_populations=[dict(selectors=s,cases=n)for s,n in sorted(classes.items())])
    validate_selection(selection,expected)
    return selection,byid,inventory,bindings,ib,review

def validate_partition(ids,parts):
    need(type(ids)is list and all(type(x)is str for x in ids)and type(parts)is list and parts and all(type(part)is list and part and all(type(x)is str for x in part)for part in parts),'nonempty literal string-list build partition')
    need([cid for part in parts for cid in part]==ids,'complete ordered disjoint build partition')
    need(len(ids)==len(set(ids)),'no duplicate partition case')

def partition_controls():
    ids=['x'+str(i)for i in range(64)];parts=[ids[k:k+16]for k in range(0,64,16)];validate_partition(ids,parts);rejected=[]
    for label,wrong in [('dropped_last',parts[:-1]),('duplicate_part',parts[:3]+[parts[0]]),('reverse_parts',list(reversed(parts))),('empty_part',[[],*parts]),('reverse_internal',[list(reversed(parts[0])),*parts[1:]]),('string_part',[''.join(ids)]),('nonstr_ID',[[1],*parts])]:
        try:validate_partition(ids,wrong)
        except ValueError:rejected.append(label)
        else:raise ValueError('accepted build-partition corruption '+label)
    return dict(complete_four_by_sixteen_positive=True,rejected=rejected)

def partitioned_batch_review(batch,selection,selection_path,pin,byid):
    ids=selection['ordered_case_ids'];refs=batch['build_summaries'];subrefs=batch['build_selections']
    need(type(refs)is list and type(subrefs)is list and len(ids)==64 and len(refs)==len(subrefs)==4,'preregistered four independently allocated16-case invocations')
    need(all(type(ref)is dict and set(ref)=={'path','sha256'} for ref in refs+subrefs),'literal exact build/partition references')
    need(len({ref['path']for ref in refs})==len({ref['path']for ref in subrefs})==4,'four distinct actual build/selection receipts')
    need(not batch.get('continuation_selections',[]),'disjoint partition is not a continuation chain')
    aggregate=[];parts=[];calls=0
    for j,(ref,subref)in enumerate(zip(refs,subrefs)):
        sp=ROOT/subref['path'];pin(sp,subref['sha256']);local=read(sp);part=ids[16*j:16*(j+1)]
        expected=copy.deepcopy(selection);expected.update(selection_policy='AUTHORIZED_DISJOINT_BUILD_PARTITION_V1',ordered_case_ids=part,selection_reason=local['selection_reason'],selected_instances=16,parent_selection_path=key(selection_path),parent_selection_sha256=sha(selection_path),partition_index=j,partition_offset=16*j)
        need(same(local,expected),'entire independently reconstructed authorized partition selection')
        actual=receipts.invocation_review(ROOT/ref['path'],ref['sha256'],local,sp,pin,byid)
        need(actual['completed_formulas']==16 and actual['pending_case_ids']==[]and actual['producer_calls']==16,'every serial invocation completes all16 actual formulas')
        parts.append(local['ordered_case_ids']);aggregate.extend(actual['records']);calls+=actual['producer_calls']
    validate_partition(ids,parts)
    need(aggregate==batch['records']and calls==batch['producer_calls']==64,'exact ordered four-way completed union, no retry/unfinished child promoted')
    return batch

def batch_review(path,expected_hash,selection,selection_path,pin,byid):
    pin(path,expected_hash);batch=read(path);ids=selection['ordered_case_ids'];n=len(ids)
    if batch.get('schema')!='EXACT_EIGHT_EXPLICIT_BUILD_CONSOLIDATION_V1':
        result=receipts.invocation_review(path,expected_hash,selection,selection_path,pin,byid)
        need(result['completed_formulas']==n and result['pending_case_ids']==[],'complete explicit invocation required for formula gate');return result
    need(batch['status']=='CANDIDATE_EXACT_EIGHT_EXPLICIT_FORMULAS_COMPLETE'and batch['completed_formulas']==n and batch['selected_case_ids']==ids and [r['case_id']for r in batch['records']]==ids and batch['pending_case_ids']==[]and batch['native_calls']==0,'complete ordered consolidation')
    need(all(batch[k]is False for k in ['automatic_resume','automatic_skip','independent_approval'])and batch['original_selection']==dict(path=key(selection_path),sha256=sha(selection_path)),'exact original allocation/no implicit continuation')
    for name,h in batch['inputs_sha256'].items():pin(ROOT/name,h)
    if 'source_sha256'in batch:
        need(type(batch.get('command'))is list and len(batch['command'])>=3,'recorded consolidation source command')
        source=(ROOT/batch['command'][1]).resolve();need(source.parent==ROOT/'acceleration'and source.suffix=='.py','repository consolidation source');pin(source,batch['source_sha256'])
    if 'build_selections'in batch:return partitioned_batch_review(batch,selection,selection_path,pin,byid)
    refs=batch['build_summaries'];continuations=batch['continuation_selections'];need(len(refs)==len(continuations)+1 and refs,'explicit invocation chain')
    aggregate=[];calls=0;previous=None
    for j,ref in enumerate(refs):
        if j==0:local=selection;sp=selection_path
        else:
            cr=continuations[j-1];sp=ROOT/cr['path'];pin(sp,cr['sha256']);local=read(sp);pin(ROOT/local['authorization_record_path'],local['authorization_record_sha256'])
            expected=copy.deepcopy(selection);expected.update(ordered_case_ids=ids[len(aggregate):],selection_reason=local['selection_reason'],authorization_record_path=local['authorization_record_path'],authorization_record_sha256=local['authorization_record_sha256'],parent_selection_path=key(selection_path),parent_selection_sha256=sha(selection_path),partial_build_path=refs[j-1]['path'],partial_build_sha256=refs[j-1]['sha256'],counts=dict(parent_selected=n,previously_completed_builds=len(aggregate),selected_pending_builds=n-len(aggregate)))
            need(same(local,expected)and previous['pending_case_ids']==local['ordered_case_ids'],'literal separately authorized pending suffix')
        actual=receipts.invocation_review(ROOT/ref['path'],ref['sha256'],local,sp,pin,byid);aggregate.extend(actual['records']);calls+=actual['producer_calls'];previous=actual
    need(aggregate==batch['records']and calls==batch['producer_calls']and len({r['case_id']for r in aggregate})==n,'entire completed union; no partial child promoted')
    return batch

def selection_controls(selection):
    attacks=[]
    mutations=[('skip_selected',lambda x:x['skipped_verified_case_ids'].append(x['ordered_case_ids'][0])),('drop_case',lambda x:x['ordered_case_ids'].pop()),('wrong_prior_proof',lambda x:x['completed_proof_gates'][0].__setitem__('sha256','0'*64)),('not_first_unproved',lambda x:x['ordered_case_ids'].__setitem__(0,x['skipped_verified_case_ids'][0])),('wrong_unresolved_count',lambda x:x.__setitem__('unresolved_before_batch',0)),('wrong_selected_count',lambda x:x.__setitem__('selected_instances',0))]
    if selection['selection_policy']=='FIRST_UNPROVED_PER_SELECTOR_SIZE_CLASS_V1':mutations.extend([('wrong_inventory',lambda x:x['inventory_records'].__setitem__('sha256','0'*64)),('wrong_class_population',lambda x:x['class_populations'][0].__setitem__('cases',0)),('wrong_selector_size',lambda x:x['selected_selector_sizes'].__setitem__(0,0))])
    if len(selection['ordered_case_ids'])>1:mutations.append(('reorder_cases',lambda x:x['ordered_case_ids'].reverse()))
    for name,mutate in mutations:
        bad=copy.deepcopy(selection);mutate(bad)
        try:validate_selection(bad,selection)
        except(ValueError,AssertionError):attacks.append(name)
        else:raise ValueError('accepted selection corruption '+name)
    return attacks

def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=list(STATUSES))
    for name in ['selection','batch-summary','encoding-gate','assignment','native-output','decoded','native-driver','native-spec']:ap.add_argument('--'+name,type=Path)
    for name in ['selection-sha256','batch-summary-sha256','encoding-gate-sha256','native-driver-sha256','native-spec-sha256','case-id','claim-id']:ap.add_argument('--'+name)
    ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};start=time.perf_counter()
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
        if args.mode=='audit':
            need(args.selection and args.selection_sha256 and args.batch_summary and args.batch_summary_sha256,'explicit selection/build identities');sp=args.selection.resolve();sh=args.selection_sha256;bp=args.batch_summary.resolve();bh=args.batch_summary_sha256;eg=None
        else:
            need(args.encoding_gate and args.encoding_gate_sha256,'explicit reviewed encoding report');pin(args.encoding_gate,args.encoding_gate_sha256);eg=read(args.encoding_gate);need(eg['status']==STATUSES['audit']and 1<=eg['complete_formulas']<=64,'approved bounded formula gate')
            for name,h in eg['inputs_sha256'].items():pin(ROOT/name,h)
            sp=ROOT/eg['selection_path'];sh=eg['selection_sha256'];bp=ROOT/eg['batch_summary_path'];bh=eg['batch_summary_sha256']
            for actual,want in [(args.selection,sp),(args.batch_summary,bp)]:need(actual is None or actual.resolve()==want.resolve(),'same approved explicit paths')
            for actual,want in [(args.selection_sha256,sh),(args.batch_summary_sha256,bh)]:need(actual is None or actual==want,'same approved explicit hashes')
        pin(sp,sh);pin(bp,bh);pop=prior.population(pin);selection,byid,inventory,bindings,inventory_binding,proof_review=selection_review(sp,pop,pin)
        batch=batch_review(bp,bh,selection,sp,pin,byid);ids=selection['ordered_case_ids']
        need(args.case_id is None if args.mode!='sat'else args.case_id in ids,'requested SAT case is approved selected formula')
        if eg is not None:need(eg['selected_case_ids']==ids and eg['complete_formulas']==len(ids),'same complete reviewed allocation')
        chosen=batch['records']if args.mode!='sat'else[r for r in batch['records']if r['case_id']==args.case_id];catalogue=core.prior.catalogue();checked=[];cases=[]
        for rec in chosen:
            f=rec['files']['summary.json'];row,data=prior.case_review(byid[rec['case_id']],ROOT/f['path'],f['sha256'],pin,catalogue,rec['attempt_id'])
            need(all(row[k]==rec[k]for k in ['variables','clauses','selectors','initial_domain_sizes']),'actual build dimensions derived independently')
            if inventory is not None:
                ir=inventory[row['case_id']];need(ir['computed_formula_dimensions']=={k:row[k]for k in ['selectors','variables','clauses']}and ir['initial_domain_sizes']==row['initial_domain_sizes'],'actual complete formula matches independently inventoried domain sizes')
            if eg is not None:need(row in eg['checked_cases'],'same previously approved actual formula')
            checked.append(row);cases.append((row['case_id'],data));print(json.dumps(dict(checked_case=row['case_id'],selectors=row['selectors'],complete_clauses=row['clauses'],count=len(checked))),flush=True)
        native_closure=[]
        if args.mode=='calibrate':
            need(args.native_driver and args.native_driver_sha256 and args.native_spec and args.native_spec_sha256,'fresh native source/spec');pin(args.native_driver,args.native_driver_sha256);pin(args.native_spec,args.native_spec_sha256)
            ns=prior.static_closure(args.native_driver)|{args.native_spec.resolve(),ROOT/'acceleration/theory_20260930_exact_eight_campaign_spec.md',ROOT/'acceleration/theory_20260930_hadamard_balanced_gram_cnf.py'}
            for p in ns:pin(p)
            native_closure=sorted(map(key,ns))
        if args.mode in ('audit','calibrate'):
            control=prior.controls(cases,out);control['prefix_policy_controls']=prefix_controls();control['partition_controls']=partition_controls();control['selection_corruptions']=selection_controls(selection);control['actual_clause_corruptions']=[]
            for row,(_,data)in zip(checked,cases):
                model,scope,profile,clauses=data;raw=(ROOT/row['cnf_path']).read_bytes();need(codec.cnf_bytes(clauses[:-1],model['variables'])!=raw,'dropped actual clause rejected');v=clauses[0][0];clauses[0][0]=-v;need(codec.cnf_bytes(clauses,model['variables'])!=raw,'flipped actual literal rejected');clauses[0][0]=v;control['actual_clause_corruptions'].append(dict(case_id=row['case_id'],mutations=2))
            save(out/'controls.json',control);save(out/'prior_proof_identity_review.json',proof_review)
        else:
            control=None;need(args.assignment and args.native_output,'complete raw SAT inputs');pin(args.assignment);pin(args.native_output);model,scope,profile,clauses=cases[0][1];values=codec.assignment(read(args.assignment)['assignment'],model['variables']);need(values==codec.native(args.native_output.read_text(encoding='utf8'),model['variables']),'all signed native/JSON values equal')
            result=core.decode_and_verify(values,model,scope,profile,clauses);obj=prior.native_decode_shape(result,model,scope,profile);obj['model_sha256']=checked[0]['model_sha256'];obj['scope_sha256']=checked[0]['scope_sha256']
            if args.decoded:pin(args.decoded);need(same(obj,read(args.decoded)),'entire independently reconstructed decoded factor')
            save(out/'independent_Gram_factor.json',obj);save(out/'independent_case_identity.json',checked[0])
        stamp=datetime.now(timezone.utc).isoformat();need(time.perf_counter()-start<600,'600-second complete checking allocation')
        if args.mode=='audit':
            dependencies=[dict(id='C-FIVE-FIXED-HADAMARD20-SUPPORT-PROJECTIONS',revision=1,relation='premise'),dict(id='C-FIXED-HADAMARD-SIX-PRISM-LOCAL-TRIPLE-CENSUS',revision=1,relation='verification_dependency'),dict(id='C-FIXED-HADAMARD-EXACT-EIGHT-SEPARATE-GRAM-BLOCK-SCREEN',revision=1,relation='uses_result')]+([dict(id=inventory_binding['claim_id'],revision=1,relation='uses_result')]if inventory_binding is not None else[])+[dict(id=b['id'],revision=b['revision'],relation='uses_result')for b in bindings]
            claim_id=args.claim_id or 'C-FIXED-HADAMARD-EXACT-EIGHT-EXPLICIT-BATCH-'+bh[:16].upper()+'-GRAM-ENCODINGS'
            need(claim_id.startswith('C-')and all(c.isupper()or c.isdigit()or c=='-'for c in claim_id),'safe explicit claim label')
            save(out/'claim_binding.json',dict(id=claim_id,revision=1,kind='encoding',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',statement=f'For each of the exact {len(ids)} selected literal count profiles, its complete CNF is satisfiable iff the fixed six-prism Hadamard support admits a binary36x60 factor with that count table, full prescribed integer Gram and within-triplicate caps, modulo independent equal-support column relabellings. Every initial local domain is complete and auxiliary assignments unique.',scope='Only the actual formulas explicitly listed in checked_cases. Selection authenticates prior literal proof skips and the declared supported manifest-prefix or size-class allocation policy; no class-wide or universe-wide exclusion follows. No native outcome, cross-group cap or residualD claim.',assumptions=['Frozen fixed support/local catalogue and authenticated complete792 block-survivor manifest.'],dependencies=dependencies,verifier='/root/structural_attack',producer='/root/eight_domain_audit (generic formulas), /root (explicit selection/build)',method='Complete independent allocation/proof-identity/inventory review, initial-domain and raw coefficient reconstruction, literal full-clause comparison, all actual dimensions and genuine243/synthetic/corruption controls.',shared_components=['Frozen independent campaign/core functions; frozen next32 invocation-receipt function only. No producer/native imports.'],inputs_sha256=pins,checked_cases=checked,artifact_availability='LOCAL_ONLY',availability_reason='Pending publication.',external_review=None,external_review_reason='Independent internal review only.',created_at=stamp,updated_at=stamp))
        save(out/'summary.json',dict(status=STATUSES[args.mode],timestamp=stamp,source_commit=batch['source_commit'],source_commit_provenance='Authenticated build receipt; no current Git query.',command=[sys.executable,*sys.argv],python=platform.python_version(),inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in out.rglob('*')if p.is_file()},selection_path=key(sp),selection_sha256=sh,batch_summary_path=key(bp),batch_summary_sha256=bh,population_size=792,unresolved_before_batch=selection['unresolved_before_batch'],skipped_verified_case_ids=selection['skipped_verified_case_ids'],selected_case_ids=ids,complete_formulas=len(checked),checked_cases=checked,complete_clauses_checked=sum(r['clauses']for r in checked),controls=control,native_source_closure=native_closure,checker_source_closure=sorted(map(key,closure)),elapsed_seconds=time.perf_counter()-start,solver_calls=0,git_commands=0,target_resolution=False,cross_group_column_caps_encoded=False,residual_D_encoded=False));print(json.dumps(dict(status=STATUSES[args.mode],summary_sha256=sha(out/'summary.json'),source_sha256=sha(Path(__file__)))))
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),traceback=traceback.format_exc(),source_sha256=sha(Path(__file__)),inputs_sha256=pins));raise
if __name__=='__main__':main()
