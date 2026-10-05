"""Independent literal affine-row feasibility checks; no producer import/LP solve."""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import argparse, hashlib, json, math, platform, sys, time
from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
MODEL='acceleration/results/20261002_rooted7_extension_model/model.json'
MODEL_SHA='21eb899c3606727ef4e452d518316957cf9eb76e5e85c5a79af82421f4004595'
CORNERS=[((0,0),'corner_0_0.json','71f30c7108cdcae7df865974270ea20ff0c9020fda7f1cfb05a8bdb2bfd7a62f'),
         ((20,0),'corner_20_0.json','233d9505e9fb7c8edeea4d7e92a9b4d34397613a91cc051f4776d917f4c33842'),
         ((0,9),'corner_0_9.json','7539fa5df54dcc2f86826147ae5d12a3054b94941fa405f3c4ee778c4f1efd61'),
         ((20,9),'corner_20_9.json','28f22f119f1eb5240a76cbed01f3c540f6e7f87bcecccac9bbcc3df49b92bcad')]
BASE='acceleration/results/20261002_rooted7_corner_certificates02/'


def need(value,message):
    if not value: raise ValueError(message)


def tick(deadline):
    status=deadline.status()
    need(not status['stop_required'] and status['remaining_seconds']>20,'not completed within allocated budget')


def safe(name):
    p=(ROOT/name).resolve()
    need(p.is_relative_to(ROOT) and p.relative_to(ROOT).as_posix()==name,'canonical repository path')
    return p


def sha(path,deadline):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(8*1024**2),b''): tick(deadline);h.update(block)
    return h.hexdigest()


def save(path,value):
    with path.open('x',encoding='utf8',newline='\n') as f:json.dump(value,f,indent=2);f.write('\n')


def integer(value):
    return type(value) is int


def parse_rows(equations,n):
    need(isinstance(equations,list),'equation list')
    parsed=[]
    for row in equations:
        need(isinstance(row,dict) and set(row)=={'terms','rhs_affine'},'literal row fields')
        rhs=row['rhs_affine'];need(isinstance(rhs,list) and len(rhs)==3 and all(integer(x)for x in rhs),'three integer affine RHS coefficients')
        terms=row['terms'];need(isinstance(terms,list),'literal sparse term list')
        pairs=[]
        for pair in terms:
            need(isinstance(pair,list) and len(pair)==2 and all(integer(x)for x in pair),'integer index/coefficient pair')
            col,coefficient=pair;need(0<=col<n,'variable index range');pairs.append((col,coefficient))
        parsed.append((tuple(pairs),tuple(rhs)))
    return tuple(parsed)


def exact_corner(values,n):
    need(isinstance(values,list) and len(values)==n,'complete exact rational coordinate population')
    result=[]
    for pair in values:
        need(isinstance(pair,list) and len(pair)==2 and all(integer(x)for x in pair),'exact integer numerator/denominator')
        numerator,denominator=pair;need(denominator==1,'recorded corner denominator exactly1')
        result.append(numerator)
    return result


def matvec_check(rows,coordinates,denominator,point,deadline=None):
    need(integer(denominator) and denominator>0 and all(integer(x)for x in coordinates),'integer-scaled vector domain')
    negative=[i for i,x in enumerate(coordinates)if x<0]
    mismatches=[]
    a,b=point
    for row_index,(terms,rhs) in enumerate(rows):
        if deadline is not None and row_index%512==0:tick(deadline)
        actual=sum(coordinates[col]*coefficient for col,coefficient in terms)
        expected=denominator*(rhs[0]+rhs[1]*a+rhs[2]*b)
        if actual!=expected:mismatches.append(dict(row=row_index,actual=actual,expected=expected))
    return dict(nonnegative=not negative,negative_coordinates=negative,row_mismatch_count=len(mismatches),
                mismatch_examples=mismatches[:5],rows_checked=len(rows))


def accepted(result):
    return result['nonnegative'] and result['row_mismatch_count']==0


def controls(rows,vector,deadline):
    records=[]
    def check(label,test_rows,x,d,p,expected):
        result=matvec_check(test_rows,x,d,p,deadline)
        actual=accepted(result);need(actual==expected,'control acceptance: '+label)
        records.append(dict(label=label,expected_acceptance=expected,actual_acceptance=actual,result=result))
    positive=parse_rows([dict(terms=[[0,1],[1,2]],rhs_affine=[8,0,0]),dict(terms=[[0,3],[1,-1]],rhs_affine=[3,0,0])],2)
    check('positive_nonsingular',[*positive],[2,3],1,(0,0),True)
    singular=parse_rows([dict(terms=[[0,1],[1,1]],rhs_affine=[6,0,0]),dict(terms=[[0,2],[1,2]],rhs_affine=[12,0,0]),dict(terms=[],rhs_affine=[0,0,0])],2)
    check('positive_singular_with_zero_row',singular,[2,4],1,(0,0),True)
    negative=parse_rows([dict(terms=[[0,1],[1,1]],rhs_affine=[3,0,0])],2)
    check('negative_vector_but_exact_rows',negative,[-1,4],1,(0,0),False)
    altered=vector[:];altered[0]+=1
    check('full_corner_coordinate_corruption',rows,altered,1,(0,0),False)
    terms,rhs=rows[0];modified=list(terms);need(modified and vector[modified[0][0]]>0,'nonzero observed coordinate coefficient control')
    col,coef=modified[0];modified[0]=(col,coef+1)
    row_copy=list(rows);row_copy[0]=(tuple(modified),rhs)
    check('full_corner_coefficient_corruption',row_copy,vector,1,(0,0),False)
    row_copy=list(rows);row_copy[0]=(terms,(rhs[0]+1,rhs[1],rhs[2]))
    check('full_corner_rhs_constant_corruption',row_copy,vector,1,(0,0),False)
    syntax=[]
    for label,callback in [
        ('zero_rational_denominator',lambda:exact_corner([[1,0]],1)),
        ('noninteger_corner_denominator',lambda:exact_corner([[1,2]],1)),
        ('truncated_coordinates',lambda:exact_corner([],1)),
        ('floating_row_coefficient',lambda:parse_rows([dict(terms=[[0,1.0]],rhs_affine=[1,0,0])],1)),
        ('floating_rhs',lambda:parse_rows([dict(terms=[[0,1]],rhs_affine=[1.0,0,0])],1)),
        ('out_of_range_column',lambda:parse_rows([dict(terms=[[1,1]],rhs_affine=[0,0,0])],1))]:
        try:callback()
        except ValueError as error:syntax.append(dict(label=label,rejected=True,error=str(error)))
        else:raise ValueError('malformed control unexpectedly accepted: '+label)
    return dict(arithmetic_controls=records,malformed_controls=syntax)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out',required=True);ap.add_argument('--seconds',type=float,required=True)
    ap.add_argument('--source-commit',required=True);ap.add_argument('--allocation-reason',required=True)
    args=ap.parse_args();deadline=CommandDeadline(args.seconds,allocation_reason=args.allocation_reason)
    out=safe(args.out);out.mkdir(parents=True,exist_ok=False)
    inputs={MODEL:MODEL_SHA,**{BASE+name:digest for point,name,digest in CORNERS}}
    for name,digest in inputs.items():need(sha(safe(name),deadline)==digest,'exact raw input pin: '+name)
    for p in [Path(__file__),Path(__file__).with_name(Path(__file__).stem+'_spec.md'),ROOT/'acceleration/command_deadline.py',ROOT/'acceleration/run_compute_command.py',ROOT/'pyproject.toml',ROOT/'uv.lock']:
        inputs[p.relative_to(ROOT).as_posix()]=sha(p,deadline)
    model=json.loads(safe(MODEL).read_bytes());n=len(model['variables']);rows=parse_rows(model['equations'],n)
    need(n==2766 and len(rows)==11749 and model['parameter_domain']==[[0,20],[0,9]],'exact frozen literal matrix dimensions/domain')
    vectors=[];corner_checks=[]
    for point,name,digest in CORNERS:
        raw=json.loads(safe(BASE+name).read_bytes());need(raw['parameters']==list(point),'literal corner coordinate binding')
        x=exact_corner(raw['exact_values'],n);result=matvec_check(rows,x,1,point,deadline)
        need(accepted(result),'full nonnegative corner primal')
        vectors.append(x);corner_checks.append(dict(point=list(point),artifact=BASE+name,sha256=digest,integer_coordinates=True,result=result))
    control_report=controls(rows,vectors[0],deadline);save(out/'controls.json',control_report)
    outcomes=[];integral=[];denominators=Counter()
    witness_path=out/'all210_scaled_witnesses.jsonl'
    with witness_path.open('x',encoding='utf8',newline='\n') as f:
        for a in range(21):
            for b in range(10):
                tick(deadline)
                weights=[(20-a)*(9-b),a*(9-b),(20-a)*b,a*b]
                need(min(weights)>=0 and sum(weights)==180,'exact nonnegative bilinear weights')
                need(sum(w*p[0][0] for w,p in zip(weights,CORNERS))==180*a and
                     sum(w*p[0][1] for w,p in zip(weights,CORNERS))==180*b,'exact affine parameter interpolation')
                scaled=[sum(weights[c]*vectors[c][i]for c in range(4))for i in range(n)]
                result=matvec_check(rows,scaled,180,(a,b),deadline)
                need(accepted(result),'full210 integer-scaled matvec')
                is_integer=all(x%180==0 for x in scaled)
                if is_integer:integral.append([a,b])
                reduced_lcm=math.lcm(*(180//math.gcd(x,180) for x in scaled));denominators[reduced_lcm]+=1
                record=dict(point=[a,b],corner_weight_numerators=weights,denominator=180,
                            scaled_coordinates=scaled,integer_vector=is_integer,reduced_common_denominator=reduced_lcm)
                f.write(json.dumps(record,separators=(',',':'))+'\n')
                outcomes.append(dict(point=[a,b],rows_checked=result['rows_checked'],row_mismatch_count=0,nonnegative=True,
                                     integer_vector=is_integer,reduced_common_denominator=reduced_lcm))
            print(json.dumps(dict(completed_points=len(outcomes),total_points=210,elapsed_seconds=deadline.status()['elapsed_seconds'])),flush=True)
    need(len(outcomes)==210,'complete rectangular210-point population')
    summary=dict(status='INDEPENDENT_ROOTED7_LITERAL_CORNERS_AND_BILINEAR_WITNESSES_V1_PASS',
        timestamp=datetime.now(timezone.utc).isoformat(),source_commit=args.source_commit,command=[sys.executable,*sys.argv],
        cwd=str(ROOT),python=platform.python_version(),verifier='/root/native_driver',
        method='Literal integer sparse row sums, four raw rational-pair primals, all210 full denominator180 vectors; no LP solver or producer import.',
        inputs_sha256=inputs,model_dimensions=dict(variables=n,equations=len(rows),term_occurrences=sum(len(t)for t,r in rows)),
        corner_checks=corner_checks,all210_point_checks=outcomes,integer_interpolated_points=integral,
        integer_interpolated_point_count=len(integral),rational_noninteger_interpolated_point_count=210-len(integral),
        reduced_denominator_distribution=dict(sorted(denominators.items())),
        evidence=dict(all210_witnesses=witness_path.relative_to(ROOT).as_posix(),all210_witnesses_sha256=sha(witness_path,deadline),
                      controls=(out/'controls.json').relative_to(ROOT).as_posix(),controls_sha256=sha(out/'controls.json',deadline)),
        exact_statement='For the fixed2766-coordinate11749-row integer affine system as recorded, all four supplied corners are nonnegative integer primals. Every integer point(a,b) in[0,20]x[0,9] has the explicitly recorded nonnegative rational bilinear witness satisfying every literal row exactly.',
        trusted_shared_components=['Python integer arithmetic, JSON parser, hashes and common deadline/supervisor only; producer model raw artifact is input, never trusted as a semantic derivation.'],
        limitations=['Row semantic necessity for SRG99 is UNVERIFIED and not promoted.','Rational noninteger interpolation does not imply integer feasibility.','Integral recorded witnesses establish only literal-model feasibility at the named points.','No graph construction, target exclusion, LP solver reproduction, independent matrix-row derivation or whole-model equivalence is asserted.'],
        mathematical_row_semantics_verified=False,target_resolution=False,artifact_availability='LOCAL_ONLY',
        elapsed_seconds=deadline.status()['elapsed_seconds'])
    save(out/'summary.json',summary);print(json.dumps(dict(status=summary['status'],integer_points=len(integral),summary_sha256=sha(out/'summary.json',deadline))),flush=True)


if __name__=='__main__':main()
