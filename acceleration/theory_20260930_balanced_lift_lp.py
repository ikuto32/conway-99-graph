"""Cheap one-call LP screen; all resulting certificates remain candidates."""
from pathlib import Path
from datetime import datetime,timezone
from importlib.metadata import version
import argparse,hashlib,json,platform,subprocess,sys
import theory_20260930_hadamard_support_lp as previous
ROOT=Path(__file__).resolve().parents[1]
def h(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(path,value):
    with path.open('x',encoding='utf-8',newline='\n')as stream:json.dump(value,stream,indent=2);stream.write('\n')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--model',type=Path,required=True);ap.add_argument('--model-sha256',required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    out=args.out.resolve();assert out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False)
    try:
        assert h(args.model)==args.model_sha256
        source=Path(previous.__file__);expected='0eed1385cf85055593cb7280ee8f4bb94f10ed0e29dc7394f4f8e4501fd20e8f'
        # Freeze the actual imported helper identity in the manifest; it is not
        # a verifier and no result is promoted by this producer.
        prior_source=h(source);assert prior_source==expected
        assert {name:version(name)for name in ['highspy','numpy','scipy']}=={'highspy':'1.15.1','numpy':'2.5.3','scipy':'1.18.1'}
        previous.OUT=out
        model=json.loads(args.model.read_bytes());columns=model['columns_nonzero_row_indices'];rhs=model['rhs']
        assert model['variables']==len(columns)==312 and model['equations']==len(rhs)==560 and rhs[:20]==[1]*20
        assert model['binary_coefficients'] and all(type(b)is int for b in rhs)
        assert all(len(col)==len(set(col))and 0<=col[0]<20 and all(type(r)is int and 20<=r<560 for r in col[1:])for col in columns)
        groups=[[j for j,col in enumerate(columns)if col[0]==g]for g in range(20)];assert sorted(map(len,groups))==[12]*16+[30]*4
        manifest=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),hardware=platform.uname()._asdict(),
            versions={name:version(name)for name in ['highspy','numpy','scipy']},
            inputs_sha256={args.model.resolve().relative_to(ROOT).as_posix():args.model_sha256,source.relative_to(ROOT).as_posix():prior_source,
                Path(__file__).resolve().relative_to(ROOT).as_posix():h(__file__),
                'acceleration/theory_20260930_balanced_lift_lp_spec.md':h(ROOT/'acceleration/theory_20260930_balanced_lift_lp_spec.md'),
                'uv.lock':h(ROOT/'uv.lock'),'pyproject.toml':h(ROOT/'pyproject.toml')},
            selection='First independently checked parity assignment; exactly its balanced color-lift equality relaxation.',
            research_calls_configured=1,solver_seconds=20,threads=1,random_seed=0,scales=[1,10,100,1000,10000,1000000],signs=[1,-1],
            scope='One fixed parity branch of one fixed support; no integrality, inter-group Ycaps or residualD.',independent_approval=False)
        save(out/'manifest.json',manifest);controls=[]
        for name,cols,targets,kind in [('feasible',[[0],[0]],[1],'EXACT_RATIONAL_PRIMAL_CANDIDATE'),('infeasible',[[0,1]],[0,1],'EXACT_RATIONAL_FARKAS_CANDIDATE')]:
            result=previous.solve(cols,targets,3,'control_'+name+'.log');certificate=previous.certify(cols,targets,result);assert certificate['kind']==kind
            controls.append(dict(name=name,columns=cols,rhs=targets,result=result,certificate=certificate))
        save(out/'controls.json',controls)
        numerical=previous.solve(columns,rhs,20,'solver.log');save(out/'numerical_result.json',numerical)
        certificate=previous.certify(columns,rhs,numerical);save(out/'initial_rational_certificate.json',certificate);trials=[]
        ray=numerical.get('dual_ray')
        if certificate['kind']=='NO_EXACT_CERTIFICATE' and ray and ray['exists']:
            for scale in manifest['scales']:
                for sign in manifest['signs']:
                    y=[round(sign*value*scale)for value in ray['values']];assert len(y)==560
                    repairs=[]
                    for g,indices in enumerate(groups):
                        increment=max(0,-min(sum(y[r]for r in columns[j])for j in indices));y[g]+=increment;repairs.append(increment)
                    dots=[sum(y[r]for r in col)for col in columns];right=sum(a*b for a,b in zip(y,rhs,strict=True));passed=min(dots)>=0 and right<0
                    trial=dict(scale=scale,sign=sign,weights=y,onehot_increments=repairs,minimum_column_dot=min(dots),rhs_dot=right,exact_candidate=passed);trials.append(trial)
                    if passed and certificate['kind']=='NO_EXACT_CERTIFICATE':certificate=dict(kind='EXACT_INTEGER_FARKAS_CANDIDATE',**trial)
            save(out/'integer_repair_trials.json',trials)
        save(out/'certificate.json',certificate)
        save(out/'summary.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),status='CANDIDATE_FIXED_PARITY_LIFT_LP_OUTCOME',model_status=numerical['model_status'],
            certificate_kind=certificate['kind'],research_calls=1,variables=312,equations=560,solver_wall_seconds=numerical['wall_seconds'],integer_repair_trials=len(trials),
            exact_integer_candidates=sum(t['exact_candidate']for t in trials),independent_approval=False,target_resolution='UNKNOWN',
            outputs_sha256={p.relative_to(ROOT).as_posix():h(p)for p in out.iterdir()if p.is_file()}))
        print(json.dumps(dict(model_status=numerical['model_status'],certificate_kind=certificate['kind'],research_calls=1)))
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),source_sha256=h(__file__),mathematical_exclusion=False));raise
if __name__=='__main__':main()
