"""Finite candidate controls for general balanced affine phase necessity."""
from collections import Counter
from datetime import datetime,timezone
from itertools import permutations,product
from pathlib import Path
import argparse,hashlib,json,platform,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1]
def need(v,msg):
    if not v:raise ValueError(msg)
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def matrix(maps):return [[sum((s*x+t)%3==y for s,t in maps)for y in range(3)]for x in range(3)]
def check_local(maps):
    need(matrix(maps)==[[2]*3 for _ in range(3)],'literal local balanced matrix')
    s0,t0=maps[0];normalized=[(s*s0%3,(t-s*s0*t0)%3)for s,t in maps]
    need(normalized[0]==(1,0),'first-coordinate identity gauge')
    signs=[s for s,t in normalized];phases=[t for s,t in normalized]
    if all(s==1 for s in signs):
        need(Counter(phases)==Counter({0:2,1:2,2:2})and sum(phases)%3==0,'constant-group phase multiplicities and sum')
        kind='constant'
    else:
        need(signs.count(1)==signs.count(2)==3,'mixed signs')
        for s in(1,2):
            ts=[t for r,t in normalized if r==s]
            need(sorted(ts)==[0,1,2]and sum(ts)%3==0,'mixed-group phases distinct and sum zero')
        kind='mixed'
    # Directly confirm normalized maps compose with the original first map.
    need(all((s*x+t)%3==(old_s*((s0*(x-t0))%3)+old_t)%3 for(s,t),(old_s,old_t)in zip(normalized,maps,strict=True)for x in range(3)),'all exact column-gauge equations')
    return kind,normalized
def check_pair(maps):
    need(matrix(maps)==[[2-int(x==y)for y in range(3)]for x in range(3)],'literal pair Gram matrix')
    odd=[t for s,t in maps if s==2];even=[t for s,t in maps if s==1]
    need(len(odd)in(0,3),'complete allowed odd counts')
    if not odd:need(Counter(even)==Counter({0:1,1:2,2:2}),'zero-odd exact profile')
    else:need(sorted(odd)==[0,1,2]and sorted(even)==[1,2],'three-odd exact profile')
    need(sum(odd)%3==sum(even)%3==0,'both relative-phase sums vanish')
    return len(odd)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    pins={key(p):h(p)for p in[Path(__file__),Path(__file__).with_name('theory_20260930_hadamard_general_f3_phase_spec.md'),ROOT/'docs/DERIVATION_20260930_GENERAL_BALANCED_F3_PHASES.md',ROOT/'uv.lock',ROOT/'pyproject.toml']}
    try:
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,resource_limit_seconds=60,planned_local_tuples=46656,planned_pair_tuples=7776,solver_calls=0,batch_candidates_generated=0,independent_approval=False))
        affine=list(product((1,2),range(3)));need(sorted(tuple((s*x+t)%3 for x in range(3))for s,t in affine)==list(permutations(range(3))),'all six S3 maps exactly affine')
        locals=[];quotient={};local_total=0
        for maps in product(affine,repeat=6):
            local_total+=1
            if matrix(maps)!=[[2]*3 for _ in range(3)]:continue
            kind,normalized=check_local(maps);quotient[tuple(normalized)]=kind;locals.append(dict(maps=[list(p)for p in maps],kind=kind,normalized_maps=[list(p)for p in normalized]))
        need(local_total==46656 and len(locals)==900 and len(quotient)==150,'complete local populations')
        need(Counter(quotient.values())==Counter(constant=30,mixed=120),'exact normalized local type counts')
        pair_total=0;pairs=[]
        for maps in product(affine,repeat=5):
            pair_total+=1
            if matrix(maps)!=[[2-int(x==y)for y in range(3)]for x in range(3)]:continue
            count=check_pair(maps);pairs.append(dict(maps=[list(p)for p in maps],odd_count=count))
        need(pair_total==7776 and len(pairs)==150 and Counter(p['odd_count']for p in pairs)==Counter({0:30,3:120}),'complete pair populations')
        constant=[(1,0),(1,0),(1,1),(1,1),(1,2),(1,2)];need(check_local(constant)[0]=='constant'and constant[0]==constant[1],'valid constant group falsifies blanket equal-sign distinctness')
        corrupt=[]
        bad=constant[:];bad[1]=(1,1)
        try:check_local(bad)
        except ValueError:corrupt.append('constant_wrong_phase_multiplicity')
        else:raise ValueError('bad local multiplicity accepted')
        badpair=[(1,0),(1,1),(1,1),(1,2),(1,2)];need(check_pair(badpair)==0,'positive zero-odd profile');badpair[0]=(1,1)
        try:check_pair(badpair)
        except ValueError:corrupt.append('zero_odd_missing_identity')
        else:raise ValueError('bad pair profile accepted')
        wrong=[(2,0),(2,0),(2,0),(1,1),(1,2)];need(sum(t for s,t in wrong if s==2)%3==sum(t for s,t in wrong if s==1)%3==0,'linear-only false positive control')
        try:check_pair(wrong)
        except ValueError:corrupt.append('linear_sums_not_sufficient')
        else:raise ValueError('linear false positive accepted')
        save(out/'local_controls.json',dict(all_ordered_valid_tuples=locals,all_normalized_gauge_orbits=[dict(maps=[list(p)for p in ps],kind=kind)for ps,kind in sorted(quotient.items())],constant_blanket_distinctness_countercontrol=[list(p)for p in constant],countercontrol_scope='Valid local group only; not a full factor.'))
        save(out/'pair_controls.json',dict(all_valid_ordered_profiles=pairs,linear_only_false_positive=[list(p)for p in wrong],corruptions_rejected=corrupt))
        need(time.monotonic()-start<60,'preparation resource limit')
        result=dict(status='CANDIDATE_GENERAL_BALANCED_GF3_PHASE_PREPARATION_COMPLETE',timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=pins,outputs_sha256={key(p):h(p)for p in out.iterdir()if p.is_file()},local_arrays_examined=local_total,local_valid_ordered=900,local_normalized_types=150,constant_types=30,mixed_types=120,pair_arrays_examined=pair_total,pair_valid_ordered=150,zero_odd_profiles=30,three_odd_profiles=120,corruptions_rejected=len(corrupt),solver_calls=0,branch_rank_calculations=0,batch_candidates_generated=0,nogoods_generated=0,independent_approval=False,scope='General necessary phase preparation for the additional balanced fixed-support class; finite local controls only.',elapsed_seconds=time.monotonic()-start,claim_status='CANDIDATE',target_resolution=False)
        save(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items()if k not in['inputs_sha256','outputs_sha256']}))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e),source_sha256=h(Path(__file__))));raise
if __name__=='__main__':main()
