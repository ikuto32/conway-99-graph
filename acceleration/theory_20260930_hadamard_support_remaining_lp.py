"""Frozen three-case continuous screen with preserved exact candidate certificates."""
from datetime import datetime, timezone
from itertools import combinations_with_replacement
from pathlib import Path
import hashlib
import json
import subprocess
import sys
from tqdm import tqdm
import theory_20260930_hadamard_support_lp as lp
import theory_20260930_hadamard_lp_dual_repair as repairer

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'
OUT=ROOT/(B+'hadamard_support_remaining_lp')
CASES=[('connected_02','bdd3faa4c01f58f67118414251a4bc57e2f42702c6346716ea96ec7bf24565f4'),
    ('connected_03','b2c1c638b8eac68151260dc50012fc48a7c78a594702862af4e08e57179d5ae2'),
    ('six_prism','ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d')]
GATE=B+'independent_review/hadamard20_support_v2/summary.json'


def h(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def save(folder,name,value):
    with(folder/name).open('x',encoding='utf-8',newline='\n')as f:json.dump(value,f,indent=2);f.write('\n')


def main():
    assert h(GATE)=='a8477256446e3e402a2a21241dc383a515162dc9c8c07a9a8e26326c07b0f58f'
    OUT.mkdir(parents=True,exist_ok=False);pins={GATE:h(GATE)}
    for name,value in CASES:
        p=B+'hadamard20_support/'+name+'.json';assert h(p)==value;pins[p]=value
    for p in [Path(__file__).resolve().relative_to(ROOT).as_posix(),'acceleration/theory_20260930_hadamard_support_remaining_lp_spec.md',
            Path(lp.__file__).resolve().relative_to(ROOT).as_posix(),Path(repairer.__file__).resolve().relative_to(ROOT).as_posix(),'uv.lock','pyproject.toml']:
        pins[p]=h(p)
    save(OUT,'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),
        inputs_sha256=pins,selection=[name for name,_ in CASES],limits=dict(seconds_per_case=30,maximum_attempts_per_case=1,automatic_retry=False),
        versions={v:lp.version(v)for v in ['highspy','numpy','scipy','tqdm']},python=lp.platform.python_version(),hardware=lp.platform.uname()._asdict(),
        scope='Three fixed Hadamard supports, nonnegative continuous Gram-selector equalities; Ycaps and residualD omitted.',
        shared_components=['Frozen first-case solver and exact candidate checking functions; separate independent checker required.']))
    controls=[];lp.OUT=OUT
    for name,columns,rhs,expected in [('feasible',[[0],[0]],[1],'EXACT_RATIONAL_PRIMAL_CANDIDATE'),('infeasible',[[0,1]],[0,1],'EXACT_RATIONAL_FARKAS_CANDIDATE')]:
        result=lp.solve(columns,rhs,3,'control_'+name+'.log');certificate=lp.certify(columns,rhs,result)
        assert certificate['kind']==expected;controls.append(dict(name=name,result=result,certificate=certificate))
    save(OUT,'controls.json',controls);records=[]
    pairs=list(combinations_with_replacement(range(36),2));index={pair:60+i for i,pair in enumerate(pairs)}
    for name,pin in tqdm(CASES,desc='Remaining fixed-support LPs'):
        folder=OUT/name;folder.mkdir();lp.OUT=folder
        raw=json.loads((ROOT/(B+'hadamard20_support/'+name+'.json')).read_bytes())
        columns=[];selectors=[];rhs=[1]*60+[raw['prescribed_Gram36'][a][b]for a,b in pairs]
        for d,options in enumerate(raw['column_colour_options']):
            assert options
            for j,option in enumerate(options):
                columns.append([d]+[index[pair]for pair in combinations_with_replacement(option['rows'],2)]);selectors.append([d,j])
        model=dict(nonnegative_variables=True,columns_nonzero_row_indices=columns,rhs=rhs,selectors=selectors,
            Gram_row_pairs=[list(p)for p in pairs],variables=len(columns),equations=len(rhs),binary_coefficients=True)
        save(folder,'exact_model.json',model)
        result=lp.solve(columns,rhs,30,'solver.log');save(folder,'numerical_result.json',result)
        cert=lp.certify(columns,rhs,result);save(folder,'original_certificate_attempt.json',cert)
        repaired=None
        if result.get('dual_ray')and result['dual_ray']['exists']:
            repaired=repairer.repair(columns,rhs,selectors,result['dual_ray']['values'],1000,60)
            repaired['status']='EXACT_INTEGER_FARKAS_CANDIDATE'if repaired['rhs_dot']<0 else'NO_NEGATIVE_CERTIFICATE'
            save(folder,'integer_repaired_certificate.json',repaired)
        row=dict(core=name,raw_sha256=pin,model_status=result['model_status'],original_certificate_kind=cert['kind'],
            repaired_certificate_status=None if repaired is None else repaired['status'],
            repaired_certificate_null_reason='No numerical dual ray was available.'if repaired is None else None,
            repaired_rhs_dot=None if repaired is None else repaired['rhs_dot'],variables=len(columns),equations=len(rhs),
            solver_wall_seconds=result['wall_seconds'],research_attempts=1,
            outputs_sha256={p.relative_to(ROOT).as_posix():h(p.relative_to(ROOT))for p in folder.iterdir()if p.is_file()})
        save(folder,'summary.json',row);records.append(row);print(json.dumps({k:row[k]for k in ['core','model_status','original_certificate_kind','repaired_certificate_status','repaired_rhs_dot']}),flush=True)
    assert all(h(p)==value for p,value in pins.items())
    save(OUT,'summary.json',dict(status='CANDIDATE_REMAINING_FIXED_HADAMARD_SUPPORT_LP_BATCH',timestamp=datetime.now(timezone.utc).isoformat(),
        attempted_cases=3,completed_cases=len(records),records=records,independent_approval=False,target_resolution='UNKNOWN',
        inputs_sha256=pins,outputs_sha256={p.relative_to(ROOT).as_posix():h(p.relative_to(ROOT))for p in OUT.rglob('*')if p.is_file()},
        limitations=['Exact certificates are candidates pending independent matrix/domain checking.','No core, Hadamard family or target coverage is asserted.']))


if __name__=='__main__':main()
