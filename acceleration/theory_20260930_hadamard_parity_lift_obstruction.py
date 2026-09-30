"""Preserve exact zero-row obstruction after the selected lift's failed build."""
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import argparse,json,platform,subprocess,sys,time

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'acceleration/results/20260930_hadamard_parity_lift_cnf'
PINS={'scope.json':'c7b232d8d6cf53bc7c7c0fb062191e25f88f2e0b531c98c21c0175335c79077c',
      'exact_model.json':'dc9534f38c2bf2cb6c7f24c027c7a0ef15e8a5282e3b1c83d87ed5679555fbbd',
      'failure.json':'8216623c56fd6c991747f9d97e9d639ac9cba82be1eff16f6ceb25f1a0e9845c'}
def h(path):return sha256(Path(path).read_bytes()).hexdigest()
def key(path):return Path(path).resolve().relative_to(ROOT).as_posix()
def save(path,value):
    with path.open('x',encoding='utf-8',newline='\n')as stream:json.dump(value,stream,indent=2);stream.write('\n')
def check_zero_row(columns,rhs,index):return rhs[index]>0 and all(index not in col for col in columns)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    assert all(h(BASE/p)==value for p,value in PINS.items())
    scope=json.loads((BASE/'scope.json').read_bytes());matrix=json.loads((BASE/'exact_model.json').read_bytes());domains=scope['domains'];gram=scope['target_gram36']
    pins={key(BASE/p):value for p,value in PINS.items()}
    for path in [Path(__file__),Path(__file__).with_name('theory_20260930_hadamard_parity_lift_obstruction_spec.md'),BASE/'manifest.json',ROOT/'acceleration/theory_20260930_hadamard_parity_lift_cnf.py',ROOT/'acceleration/theory_20260930_hadamard_parity_lift_cnf_spec.md',ROOT/'uv.lock',ROOT/'pyproject.toml']:
        pins[key(path)]=h(path)
    save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,selection='Preserve all exact zero rows found after counter bound assertion; no omitted failed cases.',
        limits=dict(wall_seconds=10,solver_calls=0),independent_approval=False))
    witnesses=[]
    for i in range(36):
        for j in range(i,36):
            coefficients=[sum(i in r and j in r for r in c['lifted_rows']) for d in domains for c in d['choices']]
            assert all(v in(0,1)for v in coefficients)
            if gram[i][j]>0 and not any(coefficients):
                row_index=next(k for k,row in enumerate(matrix['row_metadata'])if row.get('rows')==[i,j])
                assert check_zero_row(matrix['columns_nonzero_row_indices'],matrix['rhs'],row_index)
                contained=[]
                for d in domains:
                    coords=d['support_coordinates']
                    if i%12 in coords and j%12 in coords:
                        p=d['selected_parity_pattern']
                        contained.append(dict(group=d['group'],pattern=p,constant=not any(p),parity_disagreement=p[coords.index(i%12)]^p[coords.index(j%12)],
                            local_choice_count=len(d['choices']),all_local_coefficients=[sum(i in r and j in r for r in c['lifted_rows']) for c in d['choices']]))
                witnesses.append(dict(rows=[i,j],required_Gram_entry=gram[i][j],lp_row_index=row_index,all312coefficients=coefficients,containing_groups=contained))
    assert len(witnesses)==6
    zeros=[i for i,b in enumerate(matrix['rhs'])if b>0 and all(i not in col for col in matrix['columns_nonzero_row_indices'])]
    assert zeros==[w['lp_row_index']for w in witnesses]
    y=[0]*560;y[zeros[0]]=-1
    dots=[sum(y[r]for r in col)for col in matrix['columns_nonzero_row_indices']];right=sum(a*b for a,b in zip(y,matrix['rhs'],strict=True))
    assert len(dots)==312 and dots==[0]*312 and right==-1
    controls=[dict(name='positive_zero_row',accepted=check_zero_row([[0],[0]],[1,1],1)),
              dict(name='corrupt_nonzero_column',rejected=not check_zero_row([[0,1],[0]],[1,1],1)),
              dict(name='zero_rhs_not_obstruction',rejected=not check_zero_row([[0],[0]],[1,0],1))]
    assert all(r.get('accepted',r.get('rejected'))for r in controls)
    save(out/'certificate.json',dict(kind='CANDIDATE_EXACT_ZERO_ROW_FARKAS',scope_sha256=PINS['scope.json'],exact_model_sha256=PINS['exact_model.json'],
        witnesses=witnesses,weights=y,column_dots=dots,rhs_dot=right,zero_positive_rows=zeros,independent_approval=False))
    save(out/'controls.json',controls)
    save(out/'failure_diagnosis.json',dict(original_failure=key(BASE/'failure.json'),original_failure_sha256=PINS['failure.json'],
        failed_operation='Exact prefix counter asserted bound <= number of inputs when target1 had zero inputs.',
        original_source_unchanged=True,partial_CNF_complete=False,model_json_created=False,
        exact_matrix_and_scope_complete=True,research_solver_calls=0,
        proof_claim='Candidate branch exclusion relies on complete local-domain coverage and zero Gram row, not the incomplete CNF or assertion.'))
    assert time.monotonic()-start<10
    save(out/'summary.json',dict(status='CANDIDATE_SELECTED_PARITY_LIFT_ZERO_ROW_EXCLUSION',timestamp=datetime.now(timezone.utc).isoformat(),
        inputs_sha256=pins,outputs_sha256={key(p):h(p)for p in out.iterdir()if p.is_file()},zero_positive_Gram_rows=6,distinct_coordinate_pairs=2,
        lp_variables=312,lp_equations=560,nonzero_dual_weights=1,rhs_dot=-1,minimum_column_dot=0,
        scope='Only the first selected normalized parity branch of the balanced-triplet family on this fixed Hadamard six-prism support.',
        wall_seconds=time.monotonic()-start,solver_calls=0,independent_approval=False,target_resolution='UNKNOWN'))
    print(json.dumps(dict(zero_positive_Gram_rows=6,coordinate_pairs=[[4,9],[7,11]],rhs_dot=right,source_sha256=h(__file__))))
if __name__=='__main__':main()
