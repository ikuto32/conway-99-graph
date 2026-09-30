"""Independent exact selected-parity domain, LP matrix and certificates."""
from collections import Counter
from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction
from itertools import combinations,product
from pathlib import Path
import argparse,hashlib,json,platform,subprocess,sys

ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';I=B+'independent_review/'
RAW=B+'hadamard20_support/six_prism.json';GATE=I+'hadamard_balanced_parity_sat_v2/summary.json'
PINS={RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',GATE:'d2536119ac3fa0d45c190a6562de2ccc67c3f9c9765fbfc03257e37b15097f9c'}
def need(v,s):
    if not v:raise ValueError(s)
def h(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
def word_domain():
    return sorted(tuple(0 if i in a else 1 if i in b else 2 for i in range(6)) for a in combinations(range(6),2) for b in combinations([i for i in range(6) if i not in a],2))
def parity3(p):
    need(sorted(p)==[0,1,2],'coordinate permutation')
    return 0 if tuple(p) in [(0,1,2),(1,2,0),(2,0,1)] else 1
def triples():
    words=word_domain();index={w:i for i,w in enumerate(words)};result=set()
    for first in words:
        for decisions in product(range(2),repeat=6):
            second=tuple([g for g in range(3) if g!=first[i]][decisions[i]] for i in range(6))
            third=tuple(3-first[i]-second[i] for i in range(6))
            if sorted(second)!=[0,0,1,1,2,2] or sorted(third)!=[0,0,1,1,2,2]:continue
            result.add(tuple(sorted([index[first],index[second],index[third]])))
    need(len(words)==90 and len(result)==150,'complete balanced triple domain')
    records=[]
    for triple in sorted(result):
        ws=[words[j] for j in triple];sgn=[parity3([w[i] for w in ws]) for i in range(6)]
        records.append(dict(word_indices=list(triple),words=[list(w) for w in ws],pattern=[s^sgn[0] for s in sgn]))
    need(Counter(tuple(r['pattern']) for r in records)==Counter({(0,)*6:30,**{p:12 for p in product(range(2),repeat=6) if p[0]==0 and sum(p)==3}}),'complete parity domain sizes')
    return records
def matrix(raw,projection,all_patterns=False):
    l=raw['L'];supports=[[a for a in range(12) if l[a][d]] for d in range(60)];groups=[]
    for support in supports:
        if support not in groups:groups.append(support)
    need(len(groups)==20 and all(supports.count(s)==3 and len(s)==6 for s in groups),'twenty raw support triples')
    rowpairs=[(a,b) for a,b in combinations(range(36),2) if (a%12)//2!=(b%12)//2]
    rowmap={pair:20+n for n,pair in enumerate(rowpairs)}
    rhs=[1]*20+[1 if a//12==b//12 else 2 for a,b in rowpairs]
    columns=[];selectors=[];domains=[];catalog=triples()
    need(len(projection['selected_group_parity_patterns'])==20,'fixed selected parity branch')
    for group,support in enumerate(groups):
        pattern=projection['selected_group_parity_patterns'][group]
        need(projection['group_records'][group]['support']==support,'raw parity support alignment')
        choices=[r for r in catalog if all_patterns or r['pattern']==pattern];domains.append(choices)
        for choice,record in enumerate(choices):
            counts=Counter()
            for word in record['words']:
                occupied=sorted(support[i]+12*word[i] for i in range(6))
                for pair in combinations(occupied,2):counts[rowmap[pair]]+=1
            need(len(counts)==45 and set(counts.values())=={1},'literal binary Gram coefficients')
            columns.append([group]+sorted(counts));selectors.append(dict(group=group,choice=choice,word_indices=record['word_indices'],pattern=record['pattern']))
    need(len(columns)==(3000 if all_patterns else 312) and len(rhs)==560,'matrix dimensions')
    if not all_patterns:need(sorted(map(len,domains))==[12]*16+[30]*4,'selected branch option populations')
    return columns,rhs,selectors,domains
def rational(values):
    need(isinstance(values,list) and all(isinstance(v,list) and len(v)==2 and all(type(x) is int for x in v) and v[1]>0 for v in values),'exact fraction encoding')
    return [Fraction(*v) for v in values]
def primal(columns,rhs,values):
    need(len(values)==len(columns) and all(v>=0 for v in values),'nonnegative primal domain');got=[Fraction(0) for _ in rhs]
    for x,col in zip(values,columns):
        need(len(col)==len(set(col)) and all(type(r) is int and 0<=r<len(rhs) for r in col),'binary sparse column')
        for r in col:got[r]+=x
    need(got==rhs,'all exact primal equations');return got
def dual(columns,rhs,values,accept=True):
    need(len(values)==len(rhs),'exact dual length');products=[sum(values[r] for r in col) for col in columns];right=sum(x*y for x,y in zip(values,rhs))
    if accept:need(min(products)>=0 and right<0,'exact Farkas separation')
    return products,right
def certificate(columns,rhs,cert):
    kind=cert['kind']
    if kind=='EXACT_RATIONAL_PRIMAL_CANDIDATE':
        x=rational(cert['values']);primal(columns,rhs,x);return dict(type='PRIMAL',values=[[v.numerator,v.denominator] for v in x])
    if kind=='EXACT_RATIONAL_FARKAS_CANDIDATE':
        y=rational(cert['values']);products,right=dual(columns,rhs,y)
        need(cert['minimum_column_dot']==[min(products).numerator,min(products).denominator] and cert['rhs_dot']==[right.numerator,right.denominator],'saved rational products')
        return dict(type='FARKAS',values=[[v.numerator,v.denominator] for v in y],column_products=[[v.numerator,v.denominator] for v in products],rhs_product=[right.numerator,right.denominator])
    if kind=='EXACT_INTEGER_FARKAS_CANDIDATE':
        y=cert['weights'];need(all(type(v) is int for v in y),'integer dual weights');products,right=dual(columns,rhs,y)
        need(cert['minimum_column_dot']==min(products) and cert['rhs_dot']==right,'saved integer products')
        return dict(type='FARKAS',integer_weights=y,column_products=products,rhs_product=right)
    need(kind=='NO_EXACT_CERTIFICATE','recognized candidate type');return dict(type='NONE')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--model',type=Path,required=True);ap.add_argument('--lp-results',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};corrupt=[]
    def pin(p,digest=None):
        p=Path(p);p=p if p.is_absolute() else ROOT/p;value=h(p);need(digest is None or value==digest,'artifact identity '+str(p));pins[p.relative_to(ROOT).as_posix()]=value;return p
    def load(p,digest=None):return json.loads(pin(p,digest).read_bytes())
    def reject(name,fn):
        try:fn()
        except (ValueError,KeyError,IndexError,TypeError):corrupt.append(name)
        else:raise ValueError('corruption accepted '+name)
    try:
        for p,digest in PINS.items():pin(p,digest)
        gate=load(GATE);need(gate['status']=='INDEPENDENT_HADAMARD_BALANCED_PARITY_SAT_OBJECT_PASS','independent selected branch')
        for p,digest in gate['outputs_sha256'].items():pin(p,digest)
        projection=load(I+'hadamard_balanced_parity_sat_v2/independent_projection.json');raw=load(RAW)
        allcols,allrhs,_,_=matrix(raw,projection,True)
        # Exact feasible relaxation on the genuine fixed geometry, before candidate checking.
        primal(allcols,allrhs,[Fraction(1,150)]*3000)
        primal([[0],[0]],[1],[Fraction(1,3),Fraction(2,3)])
        dual([[0,1]],[0,1],[1,-1])
        reject('wrong_primal_denominator',lambda:primal(allcols,allrhs,[Fraction(1,149)]*3000))
        reject('negative_primal',lambda:primal([[0],[0]],[1],[Fraction(-1),Fraction(2)]))
        reject('zero_rhs_separation',lambda:dual([[0,1]],[0,1],[0,0]))
        reject('bad_dual_sign',lambda:dual([[0,1]],[0,1],[-1,1]))
        reject('bad_fraction_denominator',lambda:rational([[1,0]]))
        columns,rhs,selectors,domains=matrix(raw,projection)
        model=load(a.model);need(model['variables']==312 and model['equations']==560 and model['binary_coefficients'] is True and model['nonnegative_variables'] is True,'literal relaxation domain')
        need(model['columns_nonzero_row_indices']==columns and model['rhs']==rhs,'complete independent matrix identity')
        manifest=load(a.lp_results/'manifest.json');summary=load(a.lp_results/'summary.json')
        for p,digest in manifest['inputs_sha256'].items():pin(p,digest)
        for p,digest in summary['outputs_sha256'].items():pin(p,digest)
        need(manifest['research_calls_configured']==summary['research_calls']==1 and manifest['solver_seconds']==20 and manifest['random_seed']==0 and manifest['threads']==1,'frozen finite LP protocol')
        need(manifest['scales']==[1,10,100,1000,10000,1000000] and manifest['signs']==[1,-1],'prespecified repair attempts')
        modelkey=a.model.resolve().relative_to(ROOT).as_posix();need(manifest['inputs_sha256'][modelkey]==pins[modelkey],'producer exact input')
        for control in load(a.lp_results/'controls.json'):need(certificate(control['columns'],control['rhs'],control['certificate'])['type'] in ['PRIMAL','FARKAS'],'saved producer tiny control exact check')
        initial=load(a.lp_results/'initial_rational_certificate.json');initial_result=certificate(columns,rhs,initial)
        final=load(a.lp_results/'certificate.json');checked=certificate(columns,rhs,final);numerical=load(a.lp_results/'numerical_result.json');trial_checks=[]
        trials_path=a.lp_results/'integer_repair_trials.json'
        if trials_path.exists():
            trials=load(trials_path);need(initial_result['type']=='NONE' and len(trials)==12,'all twelve preserved repair trials')
            for trial,(scale,sign) in zip(trials,product(manifest['scales'],manifest['signs'])):
                need(trial['scale']==scale and trial['sign']==sign,'prespecified trial order')
                ray=numerical['dual_ray']['values'];base=[round(sign*v*scale) for v in ray]
                # Floats identify the recorded rounding operation only. Exact acceptance is separate.
                increments=[]
                for group in range(20):
                    minimum=min(sum(base[r] for r in col) for col in columns if col[0]==group);increments.append(max(0,-minimum))
                y=base.copy()
                for group,value in enumerate(increments):y[group]+=value
                need(y==trial['weights'] and increments==trial['onehot_increments'],'literal minimal onehot repair')
                products,right=dual(columns,rhs,y,False);valid=min(products)>=0 and right<0
                need(trial['minimum_column_dot']==min(products) and trial['rhs_dot']==right and trial['exact_candidate']==valid,'every successful and failed exact trial')
                trial_checks.append(dict(scale=scale,sign=sign,column_products=products,rhs_product=right,accepted=valid))
            need(summary['integer_repair_trials']==12 and summary['exact_integer_candidates']==sum(t['accepted'] for t in trial_checks),'repair result population')
        else:need(summary['integer_repair_trials']==0 and initial_result['type']!='NONE','no undeclared missing repair artifacts')
        if checked['type']=='FARKAS':
            values=checked.get('integer_weights') or [Fraction(*v) for v in checked['values']]
            reject('actual_reverse_dual',lambda:dual(columns,rhs,[-v for v in values]))
            reject('actual_zero_dual',lambda:dual(columns,rhs,[0]*560))
        elif checked['type']=='PRIMAL':
            values=[Fraction(*v) for v in checked['values']];bad=values.copy();bad[0]+=1;reject('actual_bad_primal',lambda:primal(columns,rhs,bad))
        bad=deepcopy(columns);bad[0][1]=bad[0][2];reject('duplicate_matrix_entry',lambda:primal(bad,rhs,[Fraction(1,12)]*312))
        badrhs=rhs.copy();badrhs[0]+=1;reject('corrupt_real_geometry_rhs',lambda:primal(allcols,badrhs,[Fraction(1,150)]*3000))
        save(out/'independent_matrix.json',dict(columns_nonzero_row_indices=columns,rhs=rhs,selectors=selectors,domain_sizes=list(map(len,domains))))
        save(out/'exact_certificate_check.json',checked);save(out/'all_repair_trial_checks.json',trial_checks)
        for p in ['acceleration/audit_20260930_balanced_lift_lp.py','docs/AUDIT_20260930_BALANCED_LIFT_LP.md','uv.lock','pyproject.toml']:pin(p)
        status='INDEPENDENT_SELECTED_PARITY_BALANCED_LIFT_'+('FARKAS_PASS' if checked['type']=='FARKAS' else 'RATIONAL_PRIMAL_PASS' if checked['type']=='PRIMAL' else 'NO_CERTIFICATE_RECORDED')
        report=dict(status=status,timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,outputs_sha256={p.relative_to(ROOT).as_posix():h(p) for p in out.glob('*.json')},counts=dict(variables=312,equations=560,nonzeros=sum(map(len,columns)),groups=20,mixed_groups=16,constant_groups=4,positive_control_variables=3000,positive_control_equations=560,repair_trials=len(trial_checks)),certificate_type=checked['type'],verifier='/root/eight_domain_audit',method='independent_raw_domain_literal_matrix_and_exact_certificate_check',corruptions=corrupt,shared_components=['Python standard library only; no producer, matrix-builder, solver or prior checker imports.','The independently checked parity object is an authenticated input premise.'],scope='One selected parity branch of one fixed support; continuous Gram-selector system only. Other parity branches, unbalanced factors, core and target unresolved.',limitations=['No integrality, between-group Ycaps or residualD in the LP.','Floating rays/statuses do not certify any result; only exact products do.','No new solver call and no full factor constructed.'],target_resolution=False,solver_calls=0,artifact_availability='LOCAL_ONLY')
        save(out/'summary.json',report);print(json.dumps(dict(status=status,sha256=h(out/'summary.json'))))
    except BaseException as exc:save(out/'failure.json',dict(error=repr(exc)));raise
if __name__=='__main__':main()
