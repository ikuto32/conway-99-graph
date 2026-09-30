"""Exact candidate Farkas ray from frozen numerical guidance, with per-column repair."""
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'
INPUT=B+'hadamard_support_lp/'
OUT=ROOT/(B+'hadamard_support_lp_dual_repair')


def h(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def save(n,o):
    with (OUT/n).open('x',encoding='utf-8',newline='\n') as f:json.dump(o,f,indent=2);f.write('\n')


def repair(columns,rhs,selectors,ray,scale,groups):
    y=[round(-Fraction(value)*scale)for value in ray]
    initial=y[:];adjustments=[]
    for d in range(groups):
        selected=[j for j,pair in enumerate(selectors)if pair[0]==d]
        assert selected and all(columns[j][0]==d and all(i>=groups for i in columns[j][1:])for j in selected)
        minimum=min(sum(y[i]for i in columns[j])for j in selected)
        change=max(0,-minimum);y[d]+=change;adjustments.append(change)
    products=[sum(y[i]for i in col)for col in columns];right=sum(v*b for v,b in zip(y,rhs,strict=True))
    assert min(products)>=0
    return dict(values=y,rounded_before_repair=initial,nonnegative_onehot_adjustments=adjustments,
        column_dots=products,rhs_dot=right,minimum_column_dot=min(products),scale=scale,
        sign_convention='y*A>=0 and y*b<0; x>=0 and A*x=b would contradict this.')


def main():
    OUT.mkdir(parents=True,exist_ok=False);now=datetime.now(timezone.utc).isoformat()
    paths=[INPUT+'exact_model.json',INPUT+'numerical_result.json',INPUT+'summary.json',
        Path(__file__).resolve().relative_to(ROOT).as_posix(),'uv.lock']
    save('manifest.json',dict(timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256={p:h(p)for p in paths},
        selection='Only the frozen first connected01 LP ray; one fixed scale1000, no new solver or retry.',
        algorithm='Negate the numerical ray, multiply by1000 and round to integers; add the smallest nonnegative integer to each of60onehot row weights that makes every column dot nonnegative.',
        acceptance='Only an exactly negative integer y*b with all exact integer y*A>=0 is a candidate certificate. Independent raw-domain/matrix/dual checking remains mandatory.',
        numerical_threshold=None,numerical_threshold_reason='No floating acceptance; guidance is rounded then all claims checked as integers.',solver_calls=0))
    good=repair([[0,1]],[0,1],[[0,0]],[1,-1],1000,1)
    # This orientation has positive rhs and must not become a false exclusion.
    assert good['rhs_dot']>=0
    negative=repair([[0,1]],[0,1],[[0,0]],[-1,1],1000,1)
    assert negative['rhs_dot']<0
    save('controls.json',dict(noncertificate=good,certificate=negative))
    model=read(INPUT+'exact_model.json');numerical=read(INPUT+'numerical_result.json')
    assert numerical['dual_ray']['exists'] and model['nonnegative_variables']
    cert=repair(model['columns_nonzero_row_indices'],model['rhs'],model['selectors'],numerical['dual_ray']['values'],1000,60)
    cert['status']='EXACT_INTEGER_FARKAS_CANDIDATE' if cert['rhs_dot']<0 else 'NO_NEGATIVE_CERTIFICATE'
    save('certificate.json',cert)
    summary=dict(timestamp=datetime.now(timezone.utc).isoformat(),status=cert['status'],minimum_column_dot=cert['minimum_column_dot'],rhs_dot=cert['rhs_dot'],
        variables=model['variables'],equations=model['equations'],integer_certificate=True,independent_approval=False,
        scope='One saved connected01 Hadamard aggregate support and its exact continuous Gram-selector relaxation only.',
        solver_calls=0,target_resolution='UNKNOWN',
        outputs_sha256={p.relative_to(ROOT).as_posix():h(p.relative_to(ROOT))for p in OUT.iterdir()if p.is_file()})
    save('summary.json',summary);print(json.dumps({k:summary[k]for k in ['status','minimum_column_dot','rhs_dot','variables','equations']}))


if __name__=='__main__':main()
