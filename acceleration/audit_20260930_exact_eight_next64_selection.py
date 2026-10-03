"""Independent selection preparation only; no formulas, searches or gate promotion."""
import argparse,copy,hashlib,json,time,traceback
from datetime import datetime,timezone
from pathlib import Path
import audit_20260930_exact_eight_explicit_batch_v2 as checked
ROOT=checked.ROOT;B=checked.B;I=checked.I;prior=checked.prior
read=checked.read;sha=checked.sha;key=checked.key;save=checked.save;need=checked.need;same=checked.same
DATA=B/'20260930_exact_eight_next64_selection';SPEC=ROOT/'acceleration/audit_20260930_exact_eight_next64_selection_spec.md'
PINS={Path(checked.__file__):'55787855b41863e007d7de8e7ea92ccc038caabb5dc1c6d0790f282804baed02',DATA/'selection.json':'0716de33dff78fb10850240e387e3000580e482f9d0768c5098c5e1f07470b18',ROOT/'acceleration/select_20260930_exact_eight_next64.py':'9761886725771368fe0b94edb28c3895cbe21f91b5ecad301e1aed32307ab98f',ROOT/'acceleration/theory_20260930_exact_eight_next64_plan.md':'8bf172ad0b19affd9f26a9558cb2c83498060596925b561b974a1f3df8c420c0'}
def derive(universe,skip,n):
    need(type(n)is int and 1<=n<=64,'bounded integer N')
    need(type(universe)is list and type(skip)is list and all(type(x)is str for x in universe+skip),'literal ID lists')
    need(len(universe)==len(set(universe))and len(skip)==len(set(skip))and set(skip)<=set(universe),'unique complete universe and known skips')
    out=[x for x in universe if x not in set(skip)];need(len(out)>=n,'enough remaining cases');return out[:n]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};start=time.perf_counter()
    def pin(p,h=None):
        p=p.resolve();name=key(p)
        if name not in pins:pins[name]=sha(p)
        need(h is None or pins[name]==h,'hash '+name)
    try:
        for p,h in {**checked.PINS,**PINS}.items():pin(p,h)
        for p in [Path(__file__),SPEC]:pin(p)
        for p in prior.static_closure(Path(__file__)):pin(p);need(not p.name.startswith(('theory_','native_')),'no producer/native imports')
        pop=prior.population(pin);parent=read(DATA/'selection.json');byid={r['case_id']:r for r in pop['records']};skip,bindings,proof_records=checked.proof_skips(parent,byid,pin)
        need(len(skip)==60,'exact reviewed60 skips');ids=derive([r['case_id']for r in pop['records']],skip,64)
        expected=dict(schema='EXACT_EIGHT_EXPLICIT_BUILD_SELECTION_V1',selection_policy='FIRST_UNPROVED_MANIFEST_PREFIX_V1',campaign_manifest_path=key(prior.POP),campaign_manifest_sha256=prior.PINS[prior.POP],ordered_case_ids=ids,selection_reason='First64 manifest-ordered instances after removing only the60 independently proved first12, next32 and sizeclass16 literal cases.',authorization_record_path='acceleration/theory_20260930_exact_eight_next64_plan.md',authorization_record_sha256=PINS[ROOT/'acceleration/theory_20260930_exact_eight_next64_plan.md'],completed_proof_gates=parent['completed_proof_gates'],skipped_verified_case_ids=skip,population=792,unresolved_before_batch=732,selected_instances=64)
        need(same(parent,expected),'complete exact parent prefix selection')
        meta=read(DATA/'summary.json');pin(DATA/'summary.json')
        need(meta['native_calls']==meta['producer_calls']==0 and meta['independent_approval']is False,'selection preparation only')
        for name,h in {**meta['inputs_sha256'],**meta['outputs_sha256']}.items():pin(ROOT/name,h)
        need(meta['source_sha256']==PINS[ROOT/'acceleration/select_20260930_exact_eight_next64.py']and meta['selection']==dict(path=key(DATA/'selection.json'),sha256=PINS[DATA/'selection.json']),'exact producer source and parent reference')
        parts=[]
        for i,ref in enumerate(meta['build_selections']):
            path=DATA/f'partition_{i:02d}.json';need(ref['path']==key(path),'literal partition path');pin(path,ref['sha256']);child=read(path)
            wanted=copy.deepcopy(expected);wanted.update(selection_policy='AUTHORIZED_DISJOINT_BUILD_PARTITION_V1',ordered_case_ids=ids[16*i:16*(i+1)],selection_reason=f'Authorized ordered16-case build partition{i} of the parent64 selection; no new proof or skip inference.',parent_selection_path=key(DATA/'selection.json'),parent_selection_sha256=PINS[DATA/'selection.json'],partition_index=i,partition_offset=16*i,selected_instances=16)
            need(same(child,wanted),'complete literal partition identity');parts.append(child)
        need(len(parts)==4 and all(len(r['ordered_case_ids'])==16 for r in parts)and [x for r in parts for x in r['ordered_case_ids']]==ids,'four disjoint ordered16 lists')
        indices=[byid[x]['case_index']for x in ids];need(indices==meta['selected_case_indices'],'same actual manifest indices')
        controls=[];toy=['a'+str(i)for i in range(100)];gone=['a1','a3','a50'];remaining=[x for x in toy if x not in gone]
        for n in range(1,65):need(derive(toy,gone,n)==derive(toy,list(reversed(gone)),n)==remaining[:n],'all N1..64 positive prefixes')
        for label,u,s,n in [('bool',toy,gone,True),('zero',toy,gone,0),('65',toy,gone,65),('duplicate_universe',toy+[toy[0]],gone,1),('duplicate_skip',toy,gone+[gone[0]],1),('absent_skip',toy,gone+['absent'],1),('short',toy[:2],toy[:1],2),('string','abc',[],1)]:
            try:derive(u,s,n)
            except ValueError:controls.append(label)
            else:raise ValueError('accepted malformed prefix '+label)
        for label,mutate in [('wrong_skip',lambda p:p['skipped_verified_case_ids'].append(ids[0])),('wrong_order',lambda p:p['ordered_case_ids'].reverse()),('wrong_size',lambda p:p.__setitem__('selected_instances',63)),('missing_case',lambda p:p['ordered_case_ids'].pop())]:
            bad=copy.deepcopy(parent);mutate(bad);need(not same(bad,expected),'real parent corruption rejected');controls.append(label)
        for i,part in enumerate(parts):
            for field,value in [('partition_offset',1),('partition_index',4),('parent_selection_sha256','0'*64)]:
                bad=copy.deepcopy(part);bad[field]=value;need(not same(bad,part),'real partition corruption rejected');controls.append(f'partition{i}_{field}')
        save(out/'proof_identity_records.json',proof_records);save(out/'controls.json',dict(positive_prefix_sizes=list(range(1,65)),reverse_skip_order_controls=64,rejected=controls))
        save(out/'summary.json',dict(status='INDEPENDENT_EXACT_EIGHT_NEXT64_SELECTION_PREPARATION_PASS',timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in out.rglob('*')if p.is_file()},selected_case_indices=indices,selected_case_ids=ids,prior_verified_skips=60,remaining_before_selection=732,build_partition_sizes=[16]*4,scope='Preparation identity check only; no new formula, exclusion, build-backend or native approval.',new_formula_checks=0,new_solver_calls=0,new_proof_replays=0,elapsed_seconds=time.perf_counter()-start));print(json.dumps(dict(status='PASS',summary_sha256=sha(out/'summary.json'))))
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),traceback=traceback.format_exc(),inputs_sha256=pins,source_sha256=sha(Path(__file__))));raise
if __name__=='__main__':main()
