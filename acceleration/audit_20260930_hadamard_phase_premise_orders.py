"""Independent finite12-order certificate collection audit; no search."""
from copy import deepcopy
from datetime import datetime,timezone
from itertools import product
from pathlib import Path
import argparse,json,platform,random,subprocess,sys,time
import audit_20260930_hadamard_phase_premise_subset as check
ROOT=check.ROOT;B=check.B;D=B+'hadamard_phase_premise_orders/'
PINS={D+'summary.json':'9c4e0c3b7aab61ccc836145746e56798ca4adef93757b53ec5fd7760fc532d77',
 'acceleration/theory_20260930_hadamard_phase_premise_orders.py':'3384bfd5773e09ed794ff76bd76900f0ffc6ffd379c62d582b42c00fb22a74df',
 'acceleration/theory_20260930_hadamard_phase_premise_orders_spec.md':'dc97aefc342501726de73715b944502a999f79c2e540cb8d9ea55e7051073cf4',
 'acceleration/audit_20260930_hadamard_phase_premise_subset.py':'fc3fbe445b4f5ae3d811f2d0317008de3a008d93950c9135f1807cb9ffa9fc2e',
 'acceleration/audit_20260930_hadamard_f3_phase_obstruction.py':'7c6c3708b994f55c5e5ec3809639d2a88ec958c4ef66659325a1cef6e4d22e19',
 B+'independent_review/hadamard_phase_premise_subset/summary.json':'0a475da571e5766594f3b675b4348af76814c17b4f0fd2f0484de98428429c20',
 B+'independent_review/hadamard_general_f3_phase_necessity/summary.json':'30dd4e571140a139f7e36baf47f62a4428b752c79bbddd164ec6e54f3b232d67'}
need=check.need;h=check.h;read=check.read;save=check.save;key=check.key
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    try:
        need(all(h(ROOT/p)==value for p,value in PINS.items()),'frozen direct pins');summary=read(ROOT/(D+'summary.json'))
        pins=dict(PINS)
        for table in(summary['inputs_sha256'],summary['outputs_sha256'],check.PINS):
            for p,value in table.items():need(h(ROOT/p)==value,'transitive bound artifact '+p);pins[p]=value
        pins[key(__file__)]=h(__file__);pins['docs/AUDIT_20260930_HADAMARD_PHASE_PREMISE_ORDERS.md']=h(ROOT/'docs/AUDIT_20260930_HADAMARD_PHASE_PREMISE_ORDERS.md')
        manifest=read(ROOT/(D+'manifest.json'));rng=random.Random(0);orders=[list(range(19,0,-1)),list(range(1,20))]
        for _ in range(10):order=list(range(1,20));rng.shuffle(order);orders.append(order)
        need(manifest['seed']==0 and manifest['orders']==orders and manifest['limits']['span_calls']==240,'exact declared seed/order protocol')
        need(read(ROOT/(B+'independent_review/hadamard_phase_premise_subset/summary.json'))['status']=='INDEPENDENT_FOURTEEN_PATTERN_PHASE_EXCLUSION_PASS','calibrated independent helper gate')
        need(read(ROOT/(B+'independent_review/hadamard_general_f3_phase_necessity/summary.json'))['status']=='INDEPENDENT_GENERAL_BALANCED_GF3_PHASE_NECESSITY_PASS','general necessity gate')
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,
            producer='/root',verifier='/root/structural_attack',producer_code_imported=False,limits=dict(seconds=60,solver_calls=0),
            shared_components=['Frozen independently authored phase/dependency/rank checkers; no producer routines.','Pythonrandom.Random reproduces declaredseed0 order protocol only; mathematical certificates use separate exact checking.']))
        raw=read(ROOT/(B+'hadamard20_support/six_prism.json'));projection=read(ROOT/(B+'independent_review/hadamard_parity_support_cuts_sat/independent_projection.json'))
        system=check.independent.derive(raw,projection);matrix=[r['coefficients']for r in system['rows']];target=system['necessary_nonzero_functionals'][0]['coefficients']
        dependencies=[check.row_dependencies(r,system['groups'])for r in system['rows']];model=read(ROOT/(B+'hadamard_parity_support_cuts/model.json'))
        patterns=[[0]*6]+[list(p)for p in product(range(2),repeat=6)if p[0]==0 and sum(p)==3];selector={}
        for g,row in enumerate(model['groups']):
            need(row['parity_patterns']==patterns and row['selectors']==list(range(11*g+1,11*g+12))and row['support']==system['groups'][g],'full literal220selector map')
            selector[g]=row['selectors'][patterns.index(system['patterns'][g])]
        cache={};records=[];calls=0;last_trial=None
        for trial,record in enumerate(summary['results']):
            need(record['trial']==trial and h(ROOT/record['path'])==record['sha256'],'saved trial hash');data=read(ROOT/record['path']);last_trial=data
            need(data['trial']==trial and data['order']==orders[trial]and len(data['attempts'])==20,'exact20trial schedule')
            fixed=set(range(20));attempt_checks=[]
            for position,attempt in enumerate(data['attempts']):
                removed=None if position==0 else orders[trial][position-1];proposal=fixed if removed is None else fixed-{removed}
                retained=[i for i,d in enumerate(dependencies)if set(d)<=proposal]
                need(attempt['removed']==removed and attempt['proposed_groups']==sorted(proposal)and attempt['retained_rows']==retained,'recorded row selection uses full dependencies')
                k=tuple(retained)
                if k not in cache:cache[k]=check.span_check(matrix,retained,target)
                rank,contains=cache[k];need(attempt['rank']==rank and attempt['contains']==contains,'independent rank membership record');calls+=1
                if contains:fixed=set(proposal)
                attempt_checks.append(dict(position=position,removed=removed,rank=rank,contains=contains))
            deps,used,union=check.validate_certificate(data['certificate'],system)
            need(sorted(fixed)==data['certificate']['fixed_group_indices']==record['fixed_groups']and len(fixed)==record['count'],'actual final subset/count')
            need(set(union)<=fixed,'literal certificate premise union')
            clause=tuple(-selector[g]for g in sorted(fixed));need(all(-lit in projection['selected_group_selector_ids']for lit in clause),'common originalbranch lies in every excludedfamily')
            checkpoint=read(ROOT/(D+f'checkpoint_{trial:02d}.json'));need(checkpoint['completed_trials']==trial+1 and checkpoint['span_calls']==20*(trial+1)and checkpoint['results']==summary['results'][:trial+1]and checkpoint['solver_calls']==0,'all saved finite checkpoints')
            records.append(dict(trial=trial,order=orders[trial],fixed_groups=sorted(fixed),count=len(fixed),clause=list(clause),used_rows=used,premise_union=union,attempt_checks=attempt_checks,
                raw_certificate_file=record['path'],raw_certificate_file_sha256=record['sha256']))
        need(calls==240 and len(records)==12 and summary['completed_orderings']==12 and summary['span_calls']==240,'complete finite population')
        best=min(records,key=lambda r:(r['count'],r['trial']));need(summary['best']['trial']==best['trial']and summary['best']['count']==best['count']==14 and summary['improved_over_fourteen']is False,'finite best/tie rule')
        unique={}
        for record in records:unique.setdefault(tuple(record['clause']),[]).append(record['trial'])
        unique_records=[dict(index=i,clause=list(c),source_trials=trials,fixed_group_count=len(c))for i,(c,trials)in enumerate(unique.items())]
        subsumptions=[]
        for a in unique_records:
            for b in unique_records:
                if a['index']!=b['index']and set(a['clause'])<set(b['clause']):subsumptions.append(dict(stronger=a['index'],weaker=b['index']))
        rejected=[]
        def reject(name,fn):
            try:fn()
            except(ValueError,AssertionError,IndexError,KeyError):rejected.append(name)
            else:raise ValueError('corruption accepted: '+name)
        bad=deepcopy(last_trial['certificate']);bad['row_combination'][0]=(bad['row_combination'][0]+1)%3;reject('changed_trial_certificate',lambda:check.validate_certificate(bad,system))
        bad=deepcopy(last_trial['certificate']);pair=next(i for i,w in enumerate(bad['row_combination'])if w and system['rows'][i]['kind'].startswith('pair_'));bad['row_dependencies'][pair].pop();reject('dropped_pair_dependency',lambda:check.validate_certificate(bad,system))
        reject('wrong_stage_count',lambda:need(summary['span_calls']-1==calls,'stagecountcorruption'))
        reject('wrong_selected_best',lambda:need(summary['best']['count']-1==min(r['count']for r in records),'bestcountcorruption'))
        reject('duplicate_order_element',lambda:need(sorted(orders[0][:-1]+[orders[0][0]])==list(range(1,20)),'orderpermutationcorruption'))
        save(out/'checked_trials.json',records);save(out/'unique_clauses.json',dict(clauses=unique_records,proper_subsumptions=subsumptions,
            original_projection_is_common_antecedent=True,common_projection_sha256=pins[B+'independent_review/hadamard_parity_support_cuts_sat/independent_projection.json'],
            exclusions_are_disjoint=False,coverage_union_computed=False,SAT_formula_modified=False,solver_clauses_applied=0))
        save(out/'corruptions.json',dict(rejected=rejected,count=len(rejected),prior_full_independent_helper_controls_reused=True))
        need(time.monotonic()-start<60,'audit resource cap');need(all(h(ROOT/p)==value for p,value in pins.items()),'all inputs unchanged')
        claim=dict(id='C-FIXED-HADAMARD-TWELVE-ORDER-PHASE-PREMISE-COLLECTION',revision=1,kind='exclusion',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',
            statement=f'Each of the {len(unique)} distinct saved partial parity assignments produced by the exact12-order experiment is incompatible with any balanced full-Gram factor on the fixed six-prism Hadamard support; all12final row-combination certificates and240greedy decisions check exactly. The smallest retained-group count among these12trials is14, with no improvement over the original14-pattern certificate.',
            scope='Only the finite hash-bound collection of partial assignments in unique_clauses.json. Their excluded parity families overlap; no summed graph/search coverage or global minimum is claimed.',
            assumptions=['Fixed support/core and prescribed factor Gram.','Additional coordinatewise balanced triple condition.','Only the exact recorded group pattern values are fixed; all others free.'],
            dependencies=[dict(id='C-FIXED-HADAMARD-GENERAL-BALANCED-GF3-PHASE-NECESSITY',revision=1,relation='uses_result'),dict(id='C-FIVE-FIXED-HADAMARD20-SUPPORT-PROJECTIONS',revision=1,relation='premise'),
                dict(id='C-FIXED-HADAMARD-SIX-PRISM-SUPPORT-CUT-PARITY-SAT-WITNESS',revision=1,relation='derived_from'),dict(id='C-FIXED-HADAMARD-FOURTEEN-PATTERN-PHASE-EXCLUSION',revision=1,relation='verification_dependency')],
            verifier='/root/structural_attack',producer='/root',method='Independent exact all-certificate dependency/identity checking and all240rank-membership records; literal clause mapping and complete pairwise subsumption checks.',
            shared_components=['Pinned previously independently authored raw phase/dependency/column-rank checkers.','Raw support/parity data and Pythonstandardlibrary arithmetic; declared RNG protocol repeated for order identity only.','No discovery source is imported.'],
            artifact_availability='LOCAL_ONLY',availability_reason='Workspace evidence until parent publication.',external_review=None,external_review_reason='No external reviewer asserted.',
            limitations=['No globally minimum group count.','No disjoint coverage or probability interpretation.','No SAT clause applied and no factor/graph constructed.'],
            created_at=datetime.now(timezone.utc).isoformat(),updated_at=datetime.now(timezone.utc).isoformat(),inputs_sha256=pins,evidence_sha256={key(p):h(p)for p in out.iterdir()if p.is_file()})
        save(out/'claim_binding.json',claim)
        save(out/'summary.json',dict(status='INDEPENDENT_TWELVE_ORDER_PHASE_PREMISE_COLLECTION_PASS',timestamp=datetime.now(timezone.utc).isoformat(),claim_id=claim['id'],claim_revision=1,
            inputs_sha256=pins,outputs_sha256={key(p):h(p)for p in out.iterdir()if p.is_file()},completed_recorded_orders=12,complete_final_certificates_checked=12,
            recorded_span_calls=240,independently_checked_membership_records=calls,distinct_retained_row_sets_evaluated=len(cache),
            retained_group_counts=[r['count']for r in records],unique_clauses=len(unique),proper_subsumptions=len(subsumptions),minimum_in_this_batch=14,
            global_minimality_claim=False,overlap_union_coverage=None,overlap_union_coverage_reason='The partial parity families overlap; no union size was calculated.',
            corruptions_rejected=len(rejected),solver_calls=0,clauses_applied=0,elapsed_seconds=time.monotonic()-start,target_resolution='UNKNOWN'))
        print(json.dumps(dict(status='INDEPENDENT_TWELVE_ORDER_PHASE_PREMISE_COLLECTION_PASS',orders=12,records=calls,unique_clauses=len(unique),proper_subsumptions=len(subsumptions),seconds=time.monotonic()-start)))
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),source_sha256=h(__file__),elapsed_seconds=time.monotonic()-start,claim_approved=False));raise
if __name__=='__main__':main()
