"""Pure source-extracted preparation controls. No adapter import or process calls."""
from pathlib import Path
import ast, copy, hashlib, json

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'acceleration/continue_20261001_exact_eight_batch04.py'
SPEC=ROOT/'acceleration/continue_20261001_exact_eight_batch04_spec.md'
PLAN=ROOT/'acceleration/theory_20261001_exact_eight_prefix64_batch04_continuation_plan.md'
PINS={SOURCE:'4d41c360832e976a566e14bc3266c00d27b114754fc99f8cbfaef0c596016415',SPEC:'d34ab1422fa5371f53644ea07e217e55bd94f29e7033cbcb13bc4579be88883c',PLAN:'29f6ac7888a06eb4d34ff4eeb6f2ec8393fddcbcb993f595886ab73f2ff4bc52'}
OUT=ROOT/'acceleration/results/20261001_exact_eight_prefix64_batch04_continuation_preparation'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(x,m):
    if not x:raise ValueError(m)
def save(p,x):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')

def main():
    OUT.mkdir(exist_ok=False)
    try:
        for p,h in PINS.items():need(sha(p)==h,'frozen source/spec/plan')
        tree=ast.parse(SOURCE.read_bytes())
        extracted=ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in {'suffix','child_selection'}],type_ignores=[])
        need(len(extracted.body)==2,'only two pure functions')
        ns={'need':need,'copy':copy,'OLD_LAUNCHER':'old/launcher.json','PINS':{'old/launcher.json':'a'*64}}
        exec(compile(extracted,str(SOURCE)+'::pure-controls','exec'),ns)
        ids=[f'case_{i:02d}'for i in range(16)]
        cp=dict(completed_records=[dict(case_id=c)for c in ids[:14]],pending_case_ids=ids[14:],selected_case_ids=ids,native_calls=0,producer_calls=14)
        need(ns['suffix'](ids,cp)==ids[14:],'positive14+2 suffix')
        controls=[]
        mutations=[
            ('short_parent',lambda a,b:a.pop()),
            ('duplicate_parent',lambda a,b:a.__setitem__(15,a[14])),
            ('short_prefix',lambda a,b:b['completed_records'].pop()),
            ('reordered_prefix',lambda a,b:b['completed_records'].reverse()),
            ('foreign_prefix',lambda a,b:b['completed_records'][13].update(case_id='foreign')),
            ('reordered_suffix',lambda a,b:b['pending_case_ids'].reverse()),
            ('short_suffix',lambda a,b:b['pending_case_ids'].pop()),
            ('extra_suffix',lambda a,b:b['pending_case_ids'].append('foreign')),
            ('wrong_selected',lambda a,b:b.__setitem__('selected_case_ids',a[::-1])),
            ('native_called',lambda a,b:b.__setitem__('native_calls',1)),
            ('uncheckpointed_call_count',lambda a,b:b.__setitem__('producer_calls',15)),
            ('missing_suffix',lambda a,b:b.pop('pending_case_ids')),
        ]
        for label,mutate in mutations:
            a=copy.deepcopy(ids);b=copy.deepcopy(cp);mutate(a,b)
            try:ns['suffix'](a,b)
            except (ValueError,KeyError):controls.append(dict(name=label,rejected=True))
            else:raise AssertionError(label)
        old=dict(schema='EXACT_EIGHT_EXPLICIT_BUILD_SELECTION_V1',ordered_case_ids=ids,selected_instances=16,partition_index=2,partition_offset=32,parent_selection_path='parent.json',parent_selection_sha256='b'*64,unchanged={'nested':[1,2]})
        original=copy.deepcopy(old)
        info=dict(pending_case_ids=ids[14:],original_partition={'path':'partition.json','sha256':'c'*64},retained_checkpoint={'path':'checkpoint_014.json','sha256':'d'*64})
        auth={'path':'new_plan.md','sha256':'e'*64}
        child=ns['child_selection']({},old,info,auth)
        need(old==original,'deep-copy old selection, no mutation')
        need(child['ordered_case_ids']==ids[14:]and child['selected_instances']==2 and child['retained_prefix_count']==14,'two fresh IDs only')
        need(child['selection_policy']=='AUTHORIZED_CHECKPOINT_SUFFIX_CONTINUATION_V1'and child['authorization_record_path']==auth['path']and child['authorization_record_sha256']==auth['sha256'],'specific new authority')
        need(all(child[k]==old[k]for k in ['schema','partition_index','partition_offset','parent_selection_path','parent_selection_sha256','unchanged']),'unchanged parent metadata')
        child['unchanged']['nested'].append(3);need(old==original,'deep nested immutability')
        positive=dict(original_partition=old,checkpoint=cp,new_authorization=auth,derived_child_selection=ns['child_selection']({},old,info,auth))
        save(OUT/'pure_controls.json',dict(positive=positive,negative_controls=controls))
        result=dict(status='CANDIDATE_BATCH04_CONTINUATION_SOURCE_PREPARATION_CONTROLS_PASS',inputs_sha256={p.relative_to(ROOT).as_posix():h for p,h in PINS.items()},source_sha256=sha(Path(__file__)),positive_assertions=6,corruptions_rejected=len(controls),adapter_imported=False,adapter_modes_executed=0,actual_old_artifact_replays=0,process_creation_calls=0,producer_calls=0,native_calls=0,limitations=['These are source-extracted pure function controls, not independent approval.','No actual prepare/build/consolidate mode or Windows backend was executed.','The real old56/60 identities and continuation provenance require the separate independent prebuild gate.'])
        save(OUT/'summary.json',result);print(json.dumps(dict(summary_sha256=sha(OUT/'summary.json'),status=result['status'])))
    except BaseException as e:save(OUT/'failure.json',dict(error=repr(e),producer_calls=0,native_calls=0));raise

if __name__=='__main__':main()
