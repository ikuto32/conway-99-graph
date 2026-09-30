"""Candidate greedy premise reduction; discovery only, never self-approval."""
from pathlib import Path
from datetime import datetime,timezone
from itertools import product
import argparse,hashlib,json,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_'
PINS={B+'hadamard_f3_phases/phase_system.json':'aecf80f4f1c7cd29f821cb52ec502b810aa87fc8ff908ea38e2f36a69e416061',
 B+'independent_review/hadamard_f3_phase_obstruction/summary.json':'0ccca8ba45e0ffa5ff0e1d8d7c051ffcbee3d9d30092fac5df33274d80dea346',
 B+'hadamard20_support/six_prism.json':'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d'}
def need(ok,message):
    if not ok:raise ValueError(message)
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def save(p,obj):
    with p.open('x',encoding='utf8',newline='\n')as stream:json.dump(obj,stream,indent=2);stream.write('\n')
def literal_identity(matrix,weights,target):
    need(len(matrix)==len(weights),'one weight for each original row')
    need(all(type(x)is int and 0<=x<3 for x in weights),'canonical exact GF3 weights')
    need(all(sum(weights[r]*matrix[r][c]for r in range(len(matrix)))%3==target[c]for c in range(len(target))),'literal row-combination identity')
def span(matrix,indices,target):
    basis={};m=len(matrix);n=len(target)
    for index in indices:
        v=matrix[index][:];w=[0]*m;w[index]=1
        for pivot,(row,weight)in sorted(basis.items()):
            coefficient=v[pivot]
            if coefficient:
                v=[(a-coefficient*b)%3 for a,b in zip(v,row,strict=True)]
                w=[(a-coefficient*b)%3 for a,b in zip(w,weight,strict=True)]
        pivot=next((c for c in range(n)if v[c]),None)
        if pivot is None:continue
        inverse=v[pivot]
        basis[pivot]=([(inverse*a)%3 for a in v],[(inverse*a)%3 for a in w])
    remainder=target[:];weights=[0]*m
    for pivot,(row,weight)in sorted(basis.items()):
        coefficient=remainder[pivot]
        if coefficient:
            remainder=[(a-coefficient*b)%3 for a,b in zip(remainder,row,strict=True)]
            weights=[(a+coefficient*b)%3 for a,b in zip(weights,weight,strict=True)]
    if not any(remainder):literal_identity(matrix,weights,target)
    return dict(rank=len(basis),contains=not any(remainder),weights=weights if not any(remainder)else None,remainder=remainder)
def controls():
    cases=0
    for flat in product(range(3),repeat=4):
        matrix=[list(flat[:2]),list(flat[2:])]
        achievable={tuple(sum(coef[r]*matrix[r][c]for r in range(2))%3 for c in range(2))for coef in product(range(3),repeat=2)}
        for target in product(range(3),repeat=2):
            result=span(matrix,[0,1],list(target));need(result['contains']==(target in achievable),'exhaustive tiny span membership');cases+=1
    matrix=[[1,0],[0,1]];target=[1,0]
    corrupt=[]
    for label,weights,goal in [('bad_weight',[0,1],target),('bad_rhs',[1,0],[1,1]),('noncanonical_weight',[4,0],target)]:
        try:literal_identity(matrix,weights,goal)
        except ValueError:corrupt.append(label)
        else:raise ValueError('corruption accepted '+label)
    return dict(tiny_complete_membership_cases=cases,corruptions_rejected=corrupt,scope='Tiny exact algebra only, not a full factor.')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    pins=dict(PINS)
    for p,expected in pins.items():need(sha(p)==expected,'frozen input '+p)
    for p in ['acceleration/theory_20260930_hadamard_phase_premise_subset.py','acceleration/theory_20260930_hadamard_phase_premise_subset_spec.md','uv.lock','pyproject.toml']:pins[p]=sha(p)
    save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256=pins,limits=dict(span_calls=20,cooperative_seconds=60,solver_calls=0),status='PREREGISTERED_CANDIDATE_DISCOVERY'))
    try:
        save(out/'controls.json',controls())
        system=read(B+'hadamard_f3_phases/phase_system.json');raw=read(B+'hadamard20_support/six_prism.json')
        groups=system['groups'];need(len(groups)==20,'twenty fixed support groups')
        observed=[]
        for d in range(60):
            support=[a for a in range(12)if raw['L'][a][d]]
            if support not in observed:observed.append(support)
        need(observed==groups,'literal ordered raw support')
        rows=system['rows'];matrix=[r['coefficients']for r in rows];need(len(matrix)==180 and all(len(r)==120 for r in matrix),'exact matrix dimensions')
        target=system['necessary_nonzero_functionals'][0];need(target['kind']=='local_same_sign_distinct'and target['group']==0,'fixed first local functional')
        dependencies=[]
        for row in rows:
            if row['kind']=='column_gauge':needed=[]
            elif row['kind']=='local_same_sign_sum':needed=[row['group']]
            else:
                need(row['kind']in('pair_odd_phase_sum','pair_even_phase_sum'),'known equation kind')
                a,b=row['coordinates'];needed=[g for g,support in enumerate(groups)if a in support and b in support]
                need(len(needed)==5,'all five pair-row premises retained')
            dependencies.append(needed)
        fixed=set(range(20));attempts=[]
        def test(proposal,removed):
            allowed=[i for i,d in enumerate(dependencies)if set(d)<=proposal]
            result=span(matrix,allowed,target['coefficients'])
            attempts.append(dict(attempt=len(attempts),tried_removal=removed,fixed_groups=sorted(proposal),retained_equations=allowed,**result))
            need(time.monotonic()-start<60,'cooperative total allocation')
            return result
        initial=test(fixed,None);need(initial['contains'],'known full branch contradiction control')
        final=initial
        for group in range(19,0,-1):
            proposal=fixed-{group};result=test(proposal,group)
            if result['contains']:fixed=proposal;final=result
        need(len(attempts)==20 and 0 in fixed,'frozen finite schedule')
        literal_identity(matrix,final['weights'],target['coefficients'])
        for i,w in enumerate(final['weights']):need(not w or set(dependencies[i])<=fixed,'every used row has its full premise set')
        certificate=dict(field=3,fixed_group_indices=sorted(fixed),fixed_patterns=[dict(group=g,pattern=system['patterns'][g])for g in sorted(fixed)],
            required_nonzero=target,row_combination=final['weights'],row_dependencies=dependencies,
            all_gauges_unconditional=True,remaining_groups_unrestricted=True,minimum_cardinality_claim=False,
            independent_approval=False,scope='Candidate conditional exclusion of these fixed group patterns on the balanced fixed-support family only.')
        save(out/'attempts.json',attempts);save(out/'certificate.json',certificate)
        summary=dict(status='CANDIDATE_GREEDY_PHASE_PREMISE_REDUCTION_COMPLETE',timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=pins,
            outputs_sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in out.iterdir()if p.is_file()},
            initial_fixed_groups=20,final_fixed_groups=len(fixed),removed_groups=sorted(set(range(20))-fixed),span_calls=len(attempts),solver_calls=0,
            success=len(fixed)<20,independent_approval=False,target_resolution=False,elapsed_seconds=time.monotonic()-start,
            limitations=['No minimum-cardinality or whole-parity-space exhaustion claim.','No shortened SAT clause has been applied.','Independent semantic and literal-certificate review is required.'])
        save(out/'summary.json',summary);print(json.dumps({k:v for k,v in summary.items()if k not in('inputs_sha256','outputs_sha256')}))
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),source_sha256=sha('acceleration/theory_20260930_hadamard_phase_premise_subset.py')));raise
if __name__=='__main__':main()
