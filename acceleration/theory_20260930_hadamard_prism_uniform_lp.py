"""Literal uniform rational witness for one fixed support's continuous relaxation."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'
RAW=B+'hadamard20_support/six_prism.json'
MODEL=B+'hadamard_support_remaining_lp/six_prism/exact_model.json'
OUT=ROOT/(B+'hadamard_prism_uniform_lp')


def h(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def save(n,v):
    with(OUT/n).open('x',encoding='utf-8',newline='\n')as f:json.dump(v,f,indent=2);f.write('\n')


def main():
    assert h(RAW)=='ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d'
    raw=json.loads((ROOT/RAW).read_bytes());model=json.loads((ROOT/MODEL).read_bytes())
    assert all(len(options)==90 for options in raw['column_colour_options'])
    assert model['variables']==5400 and model['equations']==726
    numerators=[0]*726
    for col in model['columns_nonzero_row_indices']:
        for row in col:numerators[row]+=1
    assert numerators==[90*x for x in model['rhs']]
    OUT.mkdir(parents=True,exist_ok=False);now=datetime.now(timezone.utc).isoformat()
    paths=[RAW,MODEL,Path(__file__).resolve().relative_to(ROOT).as_posix(),'uv.lock']
    save('manifest.json',dict(timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256={p:h(p)for p in paths},
        selection='The surviving saved six_prism support with all90 options per column.',
        plan='Use literal1/90 for every selector; require every exact integer row sum to equal90times its integer rhs.',
        solver_calls=0,numerical_tolerance=None,numerical_tolerance_reason='Exact integer sums and common rational denominator only.'))
    save('certificate.json',dict(status='EXACT_RATIONAL_PRIMAL_CANDIDATE',denominator=90,numerators=[1]*5400,
        row_numerators=numerators,model_path=MODEL,model_sha256=h(MODEL),
        scope='Continuous nonnegative Gram-selector equalities for this fixed support; not integer or pair-cap feasibility.'))
    save('summary.json',dict(timestamp=now,status='CANDIDATE_FIXED_HADAMARD_PRISM_UNIFORM_LP_WITNESS',
        variables=5400,equations=726,denominator=90,minimum_numerator=1,solver_calls=0,independent_approval=False,
        inputs_sha256={p:h(p)for p in paths},outputs_sha256={p.relative_to(ROOT).as_posix():h(p.relative_to(ROOT))for p in OUT.iterdir()if p.is_file()},
        target_resolution='UNKNOWN',limitations=['A fractional selector does not produce a binary factor.','All Y-column caps and residualD equations are absent.','No inference about other supports, cores or target feasibility.']))
    print(json.dumps(dict(status='EXACT_RATIONAL_PRIMAL_CANDIDATE',variables=5400,equations=726,denominator=90)))


if __name__=='__main__':main()
