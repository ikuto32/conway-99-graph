"""Twelve declared greedy orders; candidate certificates only."""
from datetime import datetime,timezone
from pathlib import Path
import argparse,hashlib,json,random,subprocess,sys,time
import theory_20260930_hadamard_phase_premise_subset as helper
ROOT=helper.ROOT;B=helper.B
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    helper.need(helper.sha('acceleration/theory_20260930_hadamard_phase_premise_subset.py')=='ee64eb1ef3f8b88a47b8dfc4e9a6f7ae81a923fe3456dce2f54ab76a8bb44c04','frozen exact helper')
    pins=dict(helper.PINS)
    for p,d in pins.items():helper.need(helper.sha(p)==d,'input '+p)
    for p in ['acceleration/theory_20260930_hadamard_phase_premise_subset.py','acceleration/theory_20260930_hadamard_phase_premise_orders.py','acceleration/theory_20260930_hadamard_phase_premise_orders_spec.md',B+'hadamard_phase_premise_subset/certificate.json',B+'hadamard_phase_premise_subset/summary.json','uv.lock','pyproject.toml']:pins[p]=helper.sha(p)
    rng=random.Random(0);orders=[list(range(19,0,-1)),list(range(1,20))]
    for _ in range(10):order=list(range(1,20));rng.shuffle(order);orders.append(order)
    helper.save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256=pins,seed=0,orders=orders,limits=dict(orderings=12,span_calls=240,cooperative_seconds=60,solver_calls=0),success_threshold='strictly fewer than14 fixed patterns',selection_rule='minimum fixed group count, tie by trial index',independent_approval=False))
    try:
        helper.save(out/'controls.json',helper.controls())
        system=helper.read(B+'hadamard_f3_phases/phase_system.json');old=helper.read(B+'hadamard_phase_premise_subset/certificate.json')
        matrix=[r['coefficients']for r in system['rows']];target=old['required_nonzero'];dependencies=[]
        for r in system['rows']:
            if r['kind']=='column_gauge':needed=[]
            elif r['kind']=='local_same_sign_sum':needed=[r['group']]
            else:
                a,b=r['coordinates'];needed=[g for g,support in enumerate(system['groups'])if a in support and b in support]
                helper.need(len(needed)==5,'complete five-group pair dependence')
            dependencies.append(needed)
        helper.need(dependencies==old['row_dependencies'],'same independently reviewable dependency rule')
        records=[];calls=0
        for trial,order in enumerate(orders):
            fixed=set(range(20));attempts=[];answer=None
            for removed in [None,*order]:
                proposal=fixed if removed is None else fixed-{removed}
                allowed=[i for i,d in enumerate(dependencies)if set(d)<=proposal]
                result=helper.span(matrix,allowed,target['coefficients']);calls+=1
                attempts.append(dict(removed=removed,proposed_groups=sorted(proposal),retained_rows=allowed,rank=result['rank'],contains=result['contains'],remainder=result['remainder']))
                if result['contains']:fixed=proposal;answer=result
                helper.need(time.monotonic()-start<60,'cooperative allocation')
            helper.need(answer is not None and 0 in fixed,'nonempty exact certificate')
            helper.literal_identity(matrix,answer['weights'],target['coefficients'])
            certificate=dict(field=3,fixed_group_indices=sorted(fixed),fixed_patterns=[dict(group=g,pattern=system['patterns'][g])for g in sorted(fixed)],required_nonzero=target,row_combination=answer['weights'],row_dependencies=dependencies,remaining_groups_unrestricted=True,all_gauges_unconditional=True,minimum_cardinality_claim=False,independent_approval=False)
            helper.save(out/f'trial_{trial:02d}.json',dict(trial=trial,order=order,attempts=attempts,certificate=certificate))
            records.append(dict(trial=trial,fixed_groups=sorted(fixed),count=len(fixed),path=(out/f'trial_{trial:02d}.json').relative_to(ROOT).as_posix(),sha256=hashlib.sha256((out/f'trial_{trial:02d}.json').read_bytes()).hexdigest()))
            helper.save(out/f'checkpoint_{trial:02d}.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),completed_trials=trial+1,span_calls=calls,results=records.copy(),execution='FINITE_TRIAL_CHECKPOINT',solver_calls=0))
            print(json.dumps(dict(completed_orderings=trial+1,total_orderings=12,fixed_groups=len(fixed))),flush=True)
        best=min(records,key=lambda r:(r['count'],r['trial']));helper.need(calls==240,'exact finite schedule')
        helper.save(out/'summary.json',dict(status='CANDIDATE_TWELVE_PHASE_PREMISE_ORDERS_COMPLETE',timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=pins,results=records,best=best,improved_over_fourteen=best['count']<14,completed_orderings=12,span_calls=calls,solver_calls=0,elapsed_seconds=time.monotonic()-start,independent_approval=False,target_resolution=False,outputs_sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in out.iterdir()if p.is_file()}))
    except BaseException as error:helper.save(out/'failure.json',dict(error=repr(error)));raise
if __name__=='__main__':main()
