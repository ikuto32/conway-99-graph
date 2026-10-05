"""Independent interrupted-build provenance helper; draft, no producer imports.

This helper never substitutes a checkpoint for a complete formula audit.
The caller must run the independent full-domain/full-clause case reviewer.
"""
import copy
from pathlib import Path
import audit_20260930_exact_eight_explicit_batch_v3 as old
import audit_20261001_exact_eight_prefix64_selection as selection_audit

ROOT=old.ROOT
need=old.need
read=old.read
sha=old.sha
key=old.key
same=old.same
canonical=selection_audit.canonical
SERIAL=ROOT/'acceleration/build_20260930_exact_eight_explicit_batch_v2.py'
PRODUCER=ROOT/'acceleration/theory_20260930_exact_eight_campaign.py'
NAMED={'summary.json','instance.cnf','model.json','scope.json',
       'selected_profile.json','initial_domains.json','selection.json','model_package.json'}


def ref_read(ref,pin):
    need(type(ref)is dict and set(ref)=={'path','sha256'},'exact artifact reference')
    path=canonical(ref['path']);pin(path,ref['sha256'])
    return path,read(path)


def process_boundary(rec,index,interrupted):
    need(type(rec)is dict and type(rec['chunk'])is int and rec['chunk']==index and rec['resumed']is True,
         'exact launched chunk')
    need(rec['created_suspended']is True and type(rec['suspended_job_active'])is int
         and rec['suspended_job_active']==1,
         'observed suspension and Job membership')
    need(rec['reaped']is True and rec['job_active_zero_observed']is True
         and rec['cleanup_errors']==[],'observed complete cleanup')
    need(type(rec['deadline_monotonic'])in (int,float)
         and type(rec['started_monotonic'])in (int,float)
         and rec['deadline_monotonic']-rec['started_monotonic']==120,
         'separate exact120-second allocation')
    need(rec['stop_requested']is True,'terminal process boundary')
    if interrupted:
        need(type(rec['actual_exit_code'])is int and rec['actual_exit_code']==1223
             and rec['stop_reason']=='CHUNK_DEADLINE','literal interrupted root outcome')
    else:
        need(type(rec['actual_exit_code'])is int and rec['actual_exit_code']==0
             and rec['stop_reason']=='SERIAL_ROOT_EXIT','literal completed continuation root')


def checkpoint_equal(chk,ids,records,count,selection_hash):
    expected=dict(status='CANDIDATE_EXPLICIT_BUILD_PREFIX',selected_case_ids=ids,
                  completed_records=records[:count],pending_case_ids=ids[count:],
                  native_calls=0,producer_calls=count,selection_sha256=selection_hash,
                  automatic_resume=False,automatic_skip=False)
    need(same(chk,expected),'exact immutable checkpoint prefix')


def expected_case_command(plan,index,byid,folder):
    item=plan['commands'][index];cid=plan['ordered_case_ids'][index]
    original=byid[cid];attempt=plan['attempt_id']+f"_case_{original['case_index']:04d}"
    target=folder/f"case_{original['case_index']:04d}"
    cmd=[item['command'][0],'-B',str(PRODUCER),'build','--campaign-manifest',
         str(old.prior.POP),'--campaign-manifest-sha256',old.PINS[old.prior.POP],
         '--case-id',cid,'--attempt-id',attempt,'--out',str(target)]
    expected=dict(case_id=cid,case_index=original['case_index'],
                  subset_index=original['subset_index'],attempt_id=attempt,
                  output_path=key(target),command=cmd)
    need(same(item,expected),'exact planned child identity/command')
    return original,attempt,target,cmd


def child_receipt(rec,cid,attempt,cmd):
    need(rec['command']==cmd and rec['case_id']==cid and rec['attempt_id']==attempt,
         'literal producer receipt identity')
    need(type(rec['actual_exit_code'])is int and rec['actual_exit_code']==0
         and rec['outer_guard_expired']is False and rec['producer_calls']==1
         and rec['native_calls']==0,'actual successful child, not serial-root approval')


def interrupted_review(parent_path,parent,launch_ref,launcher_ref,checkpoints,pin,byid):
    """Authenticate all old bytes/receipts and return56 candidate records only."""
    launch_path,launch=ref_read(launch_ref,pin)
    launcher_path,launcher=ref_read(launcher_ref,pin)
    parent_ref=dict(path=key(parent_path),sha256=sha(parent_path))
    ids=parent['ordered_case_ids'];need(len(ids)==64 and len(set(ids))==64,'literal64 parent')
    need(launch['schema']=='EXACT_EIGHT_FOUR_SERIAL_BUILD_PLAN_V1'
         and launch['parent_selection_path']==parent_ref['path']
         and launch['parent_selection_sha256']==parent_ref['sha256']
         and launch['workers']==4 and launch['seconds_per_chunk']==120,'original four-way plan')
    need(type(launch['build_selections'])is list and len(launch['build_selections'])==4,
         'exact four original selections')
    need(launcher['status']=='CANDIDATE_FOUR_SERIAL_BUILD_INVOCATIONS_RECORDED'
         and launcher['selected_case_ids']==ids and launcher['build_invocations']==4
         and launcher['native_calls']==0 and launcher['automatic_resume']is False
         and launcher['independent_approval']is False
         and launcher['consolidation_required']is True,'honest interrupted launcher record')
    for name,h in {**launcher['inputs_sha256'],**launcher['outputs_sha256']}.items():
        pin(canonical(name),h)
    need(launcher['inputs_sha256'].get(key(launch_path))==launch_ref['sha256'],
         'original launcher directly bound exact plan')
    monitor=launcher['monitor'];chunks=launcher['chunks']
    need(monitor['failure']is None and monitor['stop_errors']==[]
         and len(chunks)==len(monitor['receipts'])==len(checkpoints)==4,'all four terminal roots')
    prepared=read(launcher_path.parent/'prepared_commands.json')
    need(prepared['selected_case_ids']==ids and prepared['per_chunk_seconds']==120
         and prepared['total_allocated_build_seconds']==480
         and prepared['maximum_concurrent_serial_builders']==4
         and prepared['automatic_resume']is False and prepared['native_calls']==0,
         'original prepared command resource boundary')
    need(len(prepared['commands'])==4,'exact four prepared commands')
    retained=[];pending=[];unaccepted=[];partitions=[]
    for j,(chunk,entry,checkpoint_ref)in enumerate(zip(chunks,launch['build_selections'],checkpoints)):
        need(chunk['chunk']==j and chunk['selection']==entry
             and chunk['process_receipt']==monitor['receipts'][j], 'same literal process receipt')
        process_boundary(chunk['process_receipt'],j,True)
        sp=canonical(entry['path']);pin(sp,entry['sha256']);part=read(sp)
        expected=selection_audit.child_for(parent,parent_ref,j)
        need(same(part,expected),'entire original partition from authenticated parent')
        folder=canonical(entry['out']);need(folder==canonical(chunk['output_directory']),
                                           'exact original output boundary')
        need(chunk['summary_path']is None and chunk['summary_sha256']is None
             and not(folder/'summary.json').exists(),'no invented terminal serial summary')
        saved=chunk['preserved_files'];actual={key(p)for p in folder.rglob('*')if p.is_file()}
        need(set(saved)==actual,'all original files preserved, no hidden extra or removed file')
        for name,info in saved.items():
            path=canonical(name);need(path.is_relative_to(folder),'old-file inventory boundary')
            need(set(info)=={'sha256','bytes'},'exact old-file record');pin(path,info['sha256'])
            need(path.stat().st_size==info['bytes'],'exact old preserved size')
        cp_path,checkpoint=ref_read(checkpoint_ref,pin)
        need(cp_path==folder/'checkpoint_014.json','declared retained checkpoint boundary')
        need({p.name for p in folder.glob('checkpoint_*.json')}
             =={f'checkpoint_{i:03d}.json'for i in range(1,15)},'complete14 checkpoint chain')
        records=checkpoint['completed_records'];local_ids=part['ordered_case_ids']
        need(len(records)==14 and [r['case_id']for r in records]==local_ids[:14],
             'only literal checkpointed14-record prefix retained')
        plan=read(folder/'plan.json')
        for name,h in plan['inputs_sha256'].items():pin(canonical(name),h)
        need(plan['schema']=='EXACT_EIGHT_EXPLICIT_BUILD_PLAN_V1'and plan['mode']=='build'
             and plan['selection_path']==key(sp)and plan['selection_sha256']==entry['sha256']
             and plan['ordered_case_ids']==local_ids and len(plan['commands'])==16
             and plan['attempt_id']==entry['attempt_id']and plan['allocation_seconds']==120
             and plan['automatic_resume']is False and plan['automatic_skip']is False
             and plan['native_calls']==plan['previous_outcomes_consumed']==0,
             'original serial plan remains authoritative')
        outer_cmd=prepared['commands'][j]
        need(outer_cmd==[outer_cmd[0],'-B',str(SERIAL),'build','--selection',str(sp),
                         '--selection-sha256',entry['sha256'],'--attempt-id',entry['attempt_id'],
                         '--seconds','120','--out',str(folder)],'exact serial invocation')
        need({p.name for p in folder.glob('case_*.receipt.json')}
             =={f'case_{i:03d}.receipt.json'for i in range(15)},'60 evidenced original producer calls')
        for i in range(16):
            original,attempt,target,cmd=expected_case_command(plan,i,byid,folder)
            if i<15:
                receipt=read(folder/f'case_{i:03d}.receipt.json')
                child_receipt(receipt,local_ids[i],attempt,cmd)
            if i>=14:continue
            record=records[i]
            need(all(record[k]==original[k]for k in ['case_id','case_index','subset_index','full_count_profile_sha256'])
                 and record['attempt_id']==attempt and set(record['files'])==NAMED,
                 'checkpoint candidate case/attempt/artifact identity')
            for name,info in record['files'].items():
                path=canonical(info['path']);need(path==target/name,'literal retained artifact path')
                pin(path,info['sha256']);need(path.stat().st_size==info['bytes'],'retained artifact size')
            summary=read(target/'summary.json')
            need(summary['status']=='CANDIDATE_EXACT_EIGHT_CAMPAIGN_LITERAL_FULL_GRAM_BUILT'
                 and summary['case_id']==local_ids[i]and summary['attempt_id']==attempt
                 and summary['native_calls']==0,'retained child reports candidate completion only')
            for name,h in {**summary['inputs_sha256'],**summary['outputs_sha256']}.items():
                pin(canonical(name),h)
            checkpoint_equal(read(folder/f'checkpoint_{i+1:03d}.json'),local_ids,records,i+1,entry['sha256'])
        retained.extend(records);pending.extend(local_ids[14:]);unaccepted.append(local_ids[14])
        partitions.append(dict(partition_index=j,partition_ref=dict(path=key(sp),sha256=entry['sha256']),
                               checkpoint_ref=checkpoint_ref,part=part,retained=records,
                               pending=local_ids[14:],original_attempt_id=plan['attempt_id'],
                               uncheckpointed_exit0_case_id=local_ids[14]))
    need(len(retained)==56 and len(pending)==8 and len(set(pending))==8
         and {r['case_id']for r in retained}.isdisjoint(pending),'56+8 exact disjoint coverage')
    need(set(ids)=={r['case_id']for r in retained}|set(pending),'no lost parent case')
    return dict(retained_records=retained,pending_case_ids=pending,partitions=partitions,
                evidenced_original_producer_calls=60,uncheckpointed_repeated_case_ids=unaccepted,
                formula_validity_approved=False)


def continuation_child(old_part,partition_ref,checkpoint_ref,launcher_ref,authority,reason):
    result=copy.deepcopy(old_part)
    result.update(selection_policy='AUTHORIZED_CHECKPOINT_SUFFIX_CONTINUATION_V1',
                  ordered_case_ids=old_part['ordered_case_ids'][14:],selected_instances=2,
                  selection_reason=reason,authorization_record_path=authority['path'],
                  authorization_record_sha256=authority['sha256'],original_partition=partition_ref,
                  retained_checkpoint=checkpoint_ref,interrupted_launcher=launcher_ref,
                  retained_prefix_count=14)
    return result


def continuation_plan_review(launch,parent_path,parent,old_state,old_launch_ref,old_launcher_ref,pin,fresh):
    need(launch['schema']=='EXACT_EIGHT_FOUR_CHECKPOINT_SUFFIX_BUILD_PLAN_V1'
         and launch['workers']==4 and launch['seconds_per_chunk']==120,
         'four explicitly authorized two-case continuation allocations')
    need(launch['original_selection']==dict(path=key(parent_path),sha256=sha(parent_path))
         and launch['original_launch_plan']==old_launch_ref
         and launch['interrupted_launcher']==old_launcher_ref,'unchanged original allocation')
    need(launch['retained_checkpoints']==[p['checkpoint_ref']for p in old_state['partitions']]
         and launch['original_producer_calls']==60 and launch['additional_allocated_producer_calls']==8
         and launch['repeated_uncheckpointed_case_ids']==old_state['uncheckpointed_repeated_case_ids'],
         'honest checkpoint/call/repeated-case accounting')
    authority=launch['authorization'];ap=canonical(authority['path']);pin(ap,authority['sha256'])
    entries=launch['build_selections'];need(type(entries)is list and len(entries)==4,'four new selections')
    folders=[];attempts=[];new_ids=[];children=[]
    for j,(entry,info)in enumerate(zip(entries,old_state['partitions'])):
        need(type(entry)is dict and set(entry)=={'path','sha256','attempt_id','out'},
             'literal continuation entry fields')
        sp=canonical(entry['path']);pin(sp,entry['sha256']);child=read(sp)
        need(type(child['selection_reason'])is str and child['selection_reason'].strip(),
             'explicit continuation reason')
        expected=continuation_child(info['part'],info['partition_ref'],info['checkpoint_ref'],
                                    old_launcher_ref,authority,child['selection_reason'])
        need(same(child,expected),'entire independently reconstructed pending-only selection')
        folder=canonical(entry['out']);attempt=entry['attempt_id']
        need(folder.is_relative_to(ROOT/'acceleration/results'),'new result output boundary')
        need(type(attempt)is str and attempt and attempt.isascii()
             and all(c.isalnum()or c in '_-'for c in attempt),'safe explicit new attempt')
        need(attempt not in {p['original_attempt_id']for p in old_state['partitions']}
             and folder!=canonical(info['checkpoint_ref']['path']).parent,
             'new attempt and output do not replace old provenance')
        if fresh:need(not folder.exists(),'fresh continuation output before launch')
        folders.append(folder);attempts.append(attempt);new_ids.extend(child['ordered_case_ids']);children.append((sp,child))
    need(len(set(folders))==len(set(attempts))==4
         and all(not a.is_relative_to(b)for a in folders for b in folders if a!=b),
         'disjoint fresh four-way output/attempt identities')
    old_folders=[canonical(p['checkpoint_ref']['path']).parent for p in old_state['partitions']]
    need(all(not a.is_relative_to(b)and not b.is_relative_to(a)for a in folders for b in old_folders),
         'no overlap with any preserved original output tree')
    need(new_ids==old_state['pending_case_ids']and len(set(new_ids))==8,'only exact eight pending cases')
    return children


def continuation_batch_review(path,expected_hash,selection,selection_path,pin,byid):
    """Verify interrupted-prefix plus complete fresh suffix provenance; no CNF approval."""
    pin(path,expected_hash);batch=read(path);ids=selection['ordered_case_ids']
    need(batch['schema']=='EXACT_EIGHT_CHECKPOINT_CONTINUATION_CONSOLIDATION_V1'
         and batch['status']=='CANDIDATE_EXACT_EIGHT_EXPLICIT_FORMULAS_COMPLETE'
         and batch['selected_case_ids']==ids and batch['completed_formulas']==64
         and batch['pending_case_ids']==[] and batch['native_calls']==0,'complete literal64 candidate only')
    need(batch['original_selection']==dict(path=key(selection_path),sha256=sha(selection_path))
         and all(batch[k]is False for k in ['automatic_retry','automatic_resume','automatic_skip','independent_approval']),
         'separately authorized continuation, no automatic retry/skip')
    for name,h in batch['inputs_sha256'].items():pin(canonical(name),h)
    cmd=batch['command'];need(type(cmd)is list and len(cmd)>=3,'literal consolidation source command')
    source=(ROOT/cmd[1]).resolve();need(source.parent==ROOT/'acceleration'and source.suffix=='.py',
                                       'repository consolidation source')
    pin(source,batch['source_sha256'])
    need(batch['source_commit']==batch['recorded_source_commit']and type(batch['source_commit'])is str
         and len(batch['source_commit'])==40 and all(c in '0123456789abcdef'for c in batch['source_commit']),
         'explicit recorded source-commit metadata')
    snapshot=interrupted_review(selection_path,selection,batch['original_launch_plan'],
                                batch['interrupted_launcher'],batch['retained_checkpoints'],pin,byid)
    lp,launch=ref_read(batch['continuation_launch_plan'],pin)
    children=continuation_plan_review(launch,selection_path,selection,snapshot,batch['original_launch_plan'],
                                      batch['interrupted_launcher'],pin,False)
    report_path,report=ref_read(batch['continuation_launcher'],pin)
    need(report['status']=='CANDIDATE_BATCH04_CONTINUATION_INVOCATIONS_RECORDED'
         and report['launch_plan']==batch['continuation_launch_plan']and report['build_invocations']==4
         and report['native_calls']==0 and report['automatic_retry']is False
         and report['consolidation_required']is True,'exact four continuation process receipts')
    for name,h in {**report['inputs_sha256'],**report['outputs_sha256']}.items():pin(canonical(name),h)
    need(report['inputs_sha256'].get(key(lp))==batch['continuation_launch_plan']['sha256'],
         'continuation launcher directly binds exact launch plan')
    preparation_gates=[]
    for name,h in report['inputs_sha256'].items():
        if name.endswith('/summary.json'):
            candidate=read(canonical(name))
            if candidate.get('status')=='INDEPENDENT_EXACT_EIGHT_BATCH04_CONTINUATION_PREFLIGHT_PASS':
                preparation_gates.append(candidate)
    need(len(preparation_gates)==1,'one actually consumed independent continuation preflight')
    pg=preparation_gates[0]
    need(pg['launch_plan_path']==key(lp)and pg['launch_plan_sha256']==batch['continuation_launch_plan']['sha256']
         and pg['selected_case_ids']==ids and pg['new_builds']==pg['new_solver_calls']==0
         and pg['formula_validity_approved']is False,'same pre-execution preparation boundary')
    for name,h in {**pg['inputs_sha256'],**pg['outputs_sha256']}.items():pin(canonical(name),h)
    need(pg['inputs_sha256'].get(key(source))==batch['source_sha256'],
         'actual continuation adapter is the independently reviewed source')
    monitor=report['monitor'];chunks=report['chunks']
    need(monitor['failure']is None and monitor['stop_errors']==[]
         and len(chunks)==len(monitor['receipts'])==4,'all continuation roots complete')
    prepared=read(report_path.parent/'prepared_commands.json')
    need(prepared['seconds_per_chunk']==120 and prepared['total_allocated_build_seconds']==480
         and prepared['maximum_workers']==4 and prepared['native_calls']==0
         and prepared['automatic_retry']is False and len(prepared['commands'])==4,
         'unchanged bounded containment allocation')
    need(batch['build_selections']==launch['build_selections']
         and type(batch['build_summaries'])is list and len(batch['build_summaries'])==4,
         'exact four actual continuation build references')
    aggregate=[];new=[]
    for j,(chunk,entry,(sp,child),summary_ref,info)in enumerate(zip(chunks,launch['build_selections'],children,
                                                               batch['build_summaries'],snapshot['partitions'])):
        need(chunk['chunk']==j and chunk['selection']==entry
             and chunk['process_receipt']==monitor['receipts'][j],'same new process receipt')
        process_boundary(chunk['process_receipt'],j,False)
        folder=canonical(entry['out']);saved=chunk['preserved_files']
        need(set(saved)=={key(p)for p in folder.rglob('*')if p.is_file()},'entire new output inventory')
        for name,info_file in saved.items():
            p=canonical(name);need(p.is_relative_to(folder),'new preserved-file boundary')
            pin(p,info_file['sha256']);need(p.stat().st_size==info_file['bytes'],'new preserved-file size')
        need(summary_ref==dict(path=key(folder/'summary.json'),sha256=chunk['summary_sha256'])
             and chunk['summary_path']==summary_ref['path'],'literal terminal new summary')
        outer_cmd=prepared['commands'][j]
        need(outer_cmd==[outer_cmd[0],'-B',str(SERIAL),'build','--selection',str(sp),
                         '--selection-sha256',entry['sha256'],'--attempt-id',entry['attempt_id'],
                         '--seconds','120','--out',str(folder)],'literal new serial command')
        actual=old.receipts.invocation_review(folder/'summary.json',summary_ref['sha256'],child,sp,pin,byid)
        need(actual['completed_formulas']==actual['producer_calls']==2 and actual['pending_case_ids']==[],
             'exact two complete new formulas')
        need({p.name for p in folder.glob('case_*.receipt.json')}=={'case_000.receipt.json','case_001.receipt.json'},
             'no hidden new producer calls')
        aggregate.extend(info['retained']);aggregate.extend(actual['records']);new.extend(actual['records'])
    need(aggregate==batch['records']and [r['case_id']for r in aggregate]==ids
         and len({r['case_id']for r in aggregate})==64,'literal ordered64 closure, no checkpoint promotion')
    need(batch['retained_checkpoint_records']==56 and batch['new_formula_records']==8
         and batch['original_producer_calls']==60 and batch['new_producer_calls']==8
         and batch['producer_calls']==68
         and batch['repeated_uncheckpointed_case_ids']==snapshot['uncheckpointed_repeated_case_ids'],
         '68 attempted producer calls,64 accepted records,four uncheckpointed repeats')
    return batch


def controls():
    ids=['case_'+str(i)for i in range(16)]
    records=[dict(case_id=cid)for cid in ids[:14]]
    good=dict(status='CANDIDATE_EXPLICIT_BUILD_PREFIX',selected_case_ids=ids,
              completed_records=records,pending_case_ids=ids[14:],native_calls=0,
              producer_calls=14,selection_sha256='a'*64,automatic_resume=False,automatic_skip=False)
    checkpoint_equal(good,ids,records,14,'a'*64)
    mutations=[('drop_record',lambda x:x['completed_records'].pop()),
               ('promote_uncheckpointed',lambda x:x['completed_records'].append(dict(case_id=ids[14]))),
               ('wrong_pending',lambda x:x['pending_case_ids'].reverse()),
               ('wrong_hash',lambda x:x.update(selection_sha256='b'*64)),
               ('hidden_native',lambda x:x.update(native_calls=1)),
               ('wrong_checkpoint_calls',lambda x:x.update(producer_calls=15)),
               ('auto_resume',lambda x:x.update(automatic_resume=True))]
    rejected=[]
    for name,mutate in mutations:
        bad=copy.deepcopy(good);mutate(bad)
        try:checkpoint_equal(bad,ids,records,14,'a'*64)
        except ValueError:rejected.append(name)
        else:raise ValueError('accepted checkpoint corruption '+name)
    process=dict(chunk=0,resumed=True,created_suspended=True,suspended_job_active=1,
                 reaped=True,job_active_zero_observed=True,cleanup_errors=[],
                 started_monotonic=100,deadline_monotonic=220,stop_requested=True,
                 actual_exit_code=1223,stop_reason='CHUNK_DEADLINE')
    process_boundary(process,0,True)
    completed=copy.deepcopy(process);completed.update(actual_exit_code=0,stop_reason='SERIAL_ROOT_EXIT')
    process_boundary(completed,0,False)
    for name,field,value in [('wrong_chunk','chunk',1),('not_resumed','resumed',False),
                             ('not_suspended','created_suspended',False),
                             ('not_in_job','suspended_job_active',0),('not_reaped','reaped',False),
                             ('nonempty_job','job_active_zero_observed',False),
                             ('cleanup_error','cleanup_errors',['failure']),
                             ('deadline_changed','deadline_monotonic',221),
                             ('no_stop','stop_requested',False),('wrong_exit','actual_exit_code',0),
                             ('wrong_reason','stop_reason','SERIAL_ROOT_EXIT')]:
        bad=copy.deepcopy(process);bad[field]=value
        try:process_boundary(bad,0,True)
        except ValueError:rejected.append(name)
        else:raise ValueError('accepted process-boundary corruption '+name)
    return dict(synthetic_exact_prefix_positive=True,terminal_process_positives=2,rejected=rejected,
                actual_artifact_controls_required_before_gate=True)
