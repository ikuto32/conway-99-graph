"""Finite exact rerounding batch for the already audited two-coordinate bound."""
import argparse
from datetime import datetime,timezone
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

D=Path('acceleration/results/20260917_two_matching_moments')
AUDIT=Path('acceleration/results/20260917_independent_review/two_matching_solve_bound.json')
MODEL_AUDIT=Path('acceleration/results/20260917_independent_review/two_matching_moments.json')
DOMAIN_AUDIT=Path('acceleration/results/20260917_independent_review/two_matchings/summary.json')
PROTOCOL=Path('docs/NEXT_20260917_TWO_COORDINATE_SMALL_CERTIFICATE.md')
DENOMINATORS=[1,2,4,8,16,32,64,128,256]
PINS={AUDIT:'adf254892686dab05f0317b9ecec963b1b98eee8f9f8ccee129b05ebf6145065',
      MODEL_AUDIT:'5af1f353a70a16fc5f915195b911d782e360ffc0690463936b7a9dea983197ed',
      DOMAIN_AUDIT:'f3d2ba90be5e8c27bc64c2e4941174d36fc3ddfcbc29ce25da872df652383acb'}


def digest(p):return sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def save(p,x):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(x,f,indent=2);f.write('\n')


def round_scaled(numerator,new_denominator,old_denominator):
    sign=-1 if numerator<0 else 1
    magnitude=abs(numerator)*new_denominator
    return sign*((2*magnitude+old_denominator)//(2*old_denominator))


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    assert not any(args.out.iterdir())
    assert all(digest(p)==h for p,h in PINS.items())
    audit,model_audit=read(AUDIT),read(MODEL_AUDIT)
    assert audit['status']=='INDEPENDENT_TWO_COORDINATE_EXACT_SUPPORT_BOUND_PASS'
    assert model_audit['status']=='INDEPENDENT_TWO_COORDINATE_FULL_MOMENT_MODEL_PASS'
    paths=[*PINS,D/'model.json',D/'integer_augmented_csr.npz',D/'exact_support_bound.json',Path(__file__),PROTOCOL,Path('uv.lock')]
    for p in paths:
        if p.parent==D:
            expected=(model_audit if p.name in('model.json','integer_augmented_csr.npz') else audit)['inputs_sha256']
            assert digest(p)==expected[p.as_posix()]
    hashes={p.as_posix():digest(p) for p in paths}
    original=read(D/'exact_support_bound.json')['bound'];meta=read(D/'model.json')
    denominator=original['denominator'];q0=original['reciprocity_weight_numerators'];y0=original['moment_weight_numerators']
    assert denominator==1048576 and original['numerator']==469399553
    offsets=meta['probability_offsets'];n=offsets[-1];hard=84+len(meta['unknown_edges'])
    assert n==89308 and len(q0)==1800 and len(y0)==3486
    save(args.out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        command=[sys.executable,*sys.argv],cwd=str(Path.cwd()),python=platform.python_version(),inputs_sha256=hashes,
        question='Can smaller-denominator exact weights preserve a positive bound for the same two-coordinate family?',
        scope=audit['scope'],population='Nine prescribed reroundings of one fixed audited certificate; no newdomains or solver.',
        denominators=DENOMINATORS,rounding='Nearest integer, exact ties away fromzero; round original numerator*D/1048576, never chain rounded results.',
        clipping='Moment numerators clipped to[-D,D]; reciprocity numerators unclipped.',
        criterion='Exact integer support numerator>0 only; every outcome retained.',
        selection='Simplest positive is smallest testedD; strongest value separately maximizes exact numerator/D.',
        stopping='Exactly nine listed denominators; noadaptive followup or solver.',seed=None,seed_reason='Deterministic',target_resolution=False))
    import numpy as np
    import scipy
    from scipy.sparse import load_npz
    matrix=load_npz(D/'integer_augmented_csr.npz')[:,:n].tocsc();matrix.sum_duplicates();matrix.sort_indices()
    assert matrix.dtype.kind in 'iu'
    column_l1=max(int(x) for x in np.asarray(abs(matrix).sum(axis=0)).ravel())
    rhs=meta['rhs'][hard:]
    def evaluate(q,y,scale):
        assert len(q)==1800 and len(y)==3486 and max(map(abs,y),default=0)<=scale
        max_weight=max(map(abs,[*q,*y]),default=0)
        guard=column_l1*max_weight
        assert guard<2**62
        weights=np.array([0]*84+q+y,dtype=np.int64)
        scores=matrix.T@weights
        maxima=[];argmax=[]
        for u in range(84):
            section=scores[offsets[u]:offsets[u+1]]
            index=int(np.argmax(section));maxima.append(int(section[index]));argmax.append(index)
        rhs_dot=sum(int(a)*int(b) for a,b in zip(y,rhs))
        numerator=rhs_dot-sum(maxima)
        return dict(numerator=numerator,denominator=scale,strictly_positive=numerator>0,
                    exact_value=str(Fraction(numerator,scale)),moment_rhs_dot_numerator=rhs_dot,
                    center_maxima_numerators=maxima,first_argmax_original_ids=argmax,
                    maximum_column_L1=column_l1,maximum_weight_magnitude=max_weight,integer_product_absolute_bound=guard)
    for a,b,expected in[(1,2,1),(-1,2,-1),(3,2,2),(-3,2,-2),(1,3,0),(-1,3,0),(2,3,1)]:
        assert round_scaled(a,1,b)==expected
    original_replay=evaluate(q0,y0,denominator)
    assert original_replay['numerator']==469399553
    assert original_replay['center_maxima_numerators']==original['center_maxima_numerators']
    zero=evaluate([0]*1800,[0]*3486,1);assert zero['numerator']==0
    scaled=evaluate([2*x for x in q0],[2*x for x in y0],2*denominator)
    assert scaled['numerator']==2*469399553
    save(args.out/'controls.json',dict(status='PRODUCER_SMALL_CERTIFICATE_CONTROLS_PASS',exact_rounding_cases=7,
        original_audited_bound_reproduced=True,all84_original_maxima_reproduced=True,zero_weight_bound_zero=True,
        doubled_weight_homogeneity=True,independent_verification=False))
    records=[];start=time.monotonic()
    for scale in DENOMINATORS:
        q=[round_scaled(x,scale,denominator) for x in q0]
        y=[max(-scale,min(scale,round_scaled(x,scale,denominator))) for x in y0]
        result=evaluate(q,y,scale)
        result.update(status='CANDIDATE_EXACT_SIMPLIFIED_SUPPORT_BOUND',moment_weight_numerators=y,
                      reciprocity_weight_numerators=q,original_denominator=denominator,
                      model=meta['model'],scope=audit['scope'],complete_original_choices=n,
                      independent_check_pending=True,target_resolution=False)
        path=args.out/f'denominator_{scale:03d}.json';save(path,result)
        records.append(dict(denominator=scale,numerator=result['numerator'],exact_value=result['exact_value'],
                            strictly_positive=result['strictly_positive'],path=str(path),sha256=digest(path)))
    positive=[r for r in records if r['strictly_positive']]
    simplest=min(positive,key=lambda r:r['denominator']) if positive else None
    strongest=max(positive,key=lambda r:Fraction(r['numerator'],r['denominator'])) if positive else None
    summary=dict(timestamp=datetime.now(timezone.utc).isoformat(),status='CANDIDATE_COMPLETE_NINE_DENOMINATOR_BATCH',
        records=records,attempted=9,completed=9,positive_count=len(positive),nonpositive_count=9-len(positive),
        simplest_positive=simplest,strongest_positive=strongest,inputs_sha256=hashes,
        numpy=np.__version__,scipy=scipy.__version__,batch_seconds=time.monotonic()-start,
        mathematical_scope_changed=False,solver_called=False,independent_review='PENDING',target_resolution=False)
    save(args.out/'summary.json',summary)
    print(json.dumps({k:v for k,v in summary.items() if k!='inputs_sha256'}))


if __name__=='__main__':main()
