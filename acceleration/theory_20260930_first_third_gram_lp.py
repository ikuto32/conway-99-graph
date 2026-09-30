"""Fixed two-profile continuous Gram scout, exact certificate candidates only."""
from pathlib import Path
from importlib.metadata import version
from datetime import datetime,timezone
import argparse,hashlib,importlib.util,json,sys,time
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results'
BASE=B/'20260930_first_third_proof_obstructions';HELPER=ROOT/'acceleration/theory_20260930_hadamard_support_lp.py'
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(p.read_bytes())
def need(x,m):
    if not x:raise ValueError(m)
def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
def matrix(m):
    pairs=[(a,b,f,h) for a in range(12) for b in range(a+1,12) if a//2!=b//2 for f in range(3) for h in range(3)];index={v:20+i for i,v in enumerate(pairs)}
    rhs=[1]*20+[1 if f==h else 2 for a,b,f,h in pairs];columns=[];selectors=[]
    for g,d in enumerate(m['domains']):
        for choice in d['choices']:
            col=[g]
            for word in choice['colour_words']:
                for ia,a in enumerate(d['support']):
                    for ib in range(ia+1,6):
                        b=d['support'][ib];need(a//2!=b//2,'support nonmatching');col.append(index[a,b,word[ia],word[ib]])
            columns.append(sorted(col));selectors.append([g,choice['choice_index']])
    need(len(columns)==2184 and len(rhs)==560,'declared full matrix dimensions')
    for ci,(g,k) in enumerate(selectors):
        for cell in m['pair_cell_counts']:
            row=index[(*cell['coordinates'],*cell['fibres'])];record=next((r for r in cell['group_contributions'] if r['group']==g),None)
            need(columns[ci].count(row)==(record['coefficients'][k] if record else 0),'literal weighted coefficient matches audited raw model')
    return dict(variables=len(columns),equations=len(rhs),selectors=selectors,columns_nonzero_row_indices=columns,rhs=rhs,binary_coefficients=False,coefficient_representation='Repeated row indices are positive integer multiplicities.',gram_rows=[dict(row=20+i,coordinates=list(p[:2]),fibres=list(p[2:])) for i,p in enumerate(pairs)])
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.perf_counter();pins={};results=[]
    def pin(p,h=None):
        s=sha(p);need(h is None or s==h,'identity '+key(p));pins[key(p)]=s
    try:
        pin(HELPER,'0eed1385cf85055593cb7280ee8f4bb94f10ed0e29dc7394f4f8e4501fd20e8f');pin(BASE/'summary.json','018b134a4f6682e177ba4c95cb98a77036e4a05c42735608cd07dc53af2f1951');base=read(BASE/'summary.json')
        for p in [Path(__file__),Path(__file__).with_name(Path(__file__).stem+'_spec.md'),ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(p)
        versions={n:version(n) for n in ['highspy','numpy','scipy']};need(versions=={'highspy':'1.15.1','numpy':'2.5.3','scipy':'1.18.1'},'locked recorded versions')
        sp=importlib.util.spec_from_file_location('frozen_lp_helper',HELPER);h=importlib.util.module_from_spec(sp);sp.loader.exec_module(h);h.OUT=out
        control=[]
        for name,cols,rhs,kind in [('positive',[[0],[0]],[1],'EXACT_RATIONAL_PRIMAL_CANDIDATE'),('infeasible',[[0,1]],[0,1],'EXACT_RATIONAL_FARKAS_CANDIDATE')]:
            raw=h.solve(cols,rhs,3,name+'.log');cert=h.certify(cols,rhs,raw);need(cert['kind']==kind,'calibrated solver and exact arithmetic');control.append(dict(name=name,model=dict(columns=cols,rhs=rhs),raw=raw,certificate=cert))
        save(out/'controls.json',control)
        save(out/'manifest.json',dict(created_at=datetime.now(timezone.utc).isoformat(),inputs_sha256=pins,versions=versions,selection=['first','third'],research_calls=2,per_call_seconds=20,threads=1,seed=0,scales=[1,10,100,1000,10000,1000000],signs=[1,-1]))
        for name,directory in [('first','20260930_eight_count_profile_lift'),('third','20260930_eight_count_profile_lift_third')]:
            d=B/directory;modelpath=d/'model.json';pin(modelpath,base['inputs_sha256'][key(modelpath)]);m=matrix(read(modelpath));co=out/name;co.mkdir();save(co/'exact_model.json',m);h.OUT=co
            raw=h.solve(m['columns_nonzero_row_indices'],m['rhs'],20,'solver.log');save(co/'numerical_result.json',raw);cert=h.certify(m['columns_nonzero_row_indices'],m['rhs'],raw);save(co/'initial_exact_recovery.json',cert);trials=[];first=None
            ray=raw.get('dual_ray')
            if ray and ray['exists']:
                for scale in [1,10,100,1000,10000,1000000]:
                    for sign in [1,-1]:
                        y=[round(sign*v*scale) for v in ray['values']];repair=[]
                        for g in range(20):
                            low=min(sum(y[r] for r in col) for col,(gg,k) in zip(m['columns_nonzero_row_indices'],m['selectors']) if gg==g);delta=max(0,-low);y[g]+=delta;repair.append(delta)
                        dots=[sum(y[r] for r in col) for col in m['columns_nonzero_row_indices']];rhs=sum(a*b for a,b in zip(y,m['rhs']));passed=min(dots)>=0 and rhs<0
                        trial=dict(scale=scale,sign=sign,weights=y,onehot_increments=repair,minimum_column_dot=min(dots),rhs_dot=rhs,passed=passed);trials.append(trial)
                        if passed and first is None:first=trial|dict(column_dot_products=dots,kind='EXACT_INTEGER_FARKAS_CANDIDATE')
            save(co/'integer_repair_trials.json',trials);save(co/'certificate.json',first or cert)
            r=dict(name=name,numerical_status=raw['model_status'],solver_seconds=raw['wall_seconds'],certificate_kind=(first or cert)['kind'],exact_integer_candidates=sum(t['passed'] for t in trials));save(co/'summary.json',r);results.append(r);print(json.dumps(r),flush=True)
        r=dict(status='CANDIDATE_TWO_LITERAL_GRAM_LP_SCOUT',created_at=datetime.now(timezone.utc).isoformat(),inputs_sha256=pins,outputs_sha256={key(p):sha(p) for p in out.rglob('*') if p.is_file()},results=results,elapsed_seconds=time.perf_counter()-start,research_lp_calls=2,native_sat_calls=0,independent_approval=False)
        save(out/'summary.json',r);print(json.dumps(dict(summary_sha256=sha(out/'summary.json'),elapsed_seconds=r['elapsed_seconds'])))
    except BaseException as ex:save(out/'failure.json',dict(error=repr(ex)));raise
if __name__=='__main__':main()
