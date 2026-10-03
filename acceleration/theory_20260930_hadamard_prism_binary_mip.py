"""Prepared direct binary HiGHS construction with exact saved-incumbent checks.

No entry point is invoked by importing this module. Numerical status is never
an exclusion; the producer never grants independent approval.
"""
from copy import deepcopy
from datetime import datetime,timezone
from importlib.metadata import version
from itertools import combinations,combinations_with_replacement,product
from pathlib import Path
import argparse,hashlib,json,math,platform,subprocess,sys,time
import highspy
import numpy as np
from scipy.sparse import coo_matrix

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'
RAW=B+'hadamard20_support/six_prism.json'
LP=B+'hadamard_support_remaining_lp/six_prism/exact_model.json'
ORDER=B+'independent_review/hadamard_six_prism_column_order/'
SUPPORT=B+'independent_review/hadamard20_support_v2/summary.json'
PINS={RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',
      LP:'f5ac7adc289d6ca3cc7ce77394565919813138f6322e5ae2dc1856684eef6ae2',
      ORDER+'summary.json':'0ce1be9ca11a3e860aa97791cfb4f42c1660d937a69ac7a9b7d96ca37640c9d2',
      ORDER+'groups.json':'a3d8366a607bfd10787d4e879f8971c84ba5835b2b22c71ebfd081f55352f404',
      SUPPORT:'a8477256446e3e402a2a21241dc383a515162dc9c8c07a9a8e26326c07b0f58f',
      'uv.lock':'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',
      'pyproject.toml':'273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339'}
TOLERANCE=1e-7
TOTAL_SECONDS=120
MAX_CALLS=3


def need(ok,why):
    if not ok:raise ValueError(why)
def key(path):return Path(path).resolve().relative_to(ROOT).as_posix()
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_bytes())
def save(path,obj):
    with Path(path).open('x',encoding='utf-8',newline='\n') as stream:json.dump(obj,stream,indent=2,allow_nan=False);stream.write('\n')
def finite_json(value):
    if isinstance(value,float) and not math.isfinite(value):return dict(nonfinite=repr(value))
    return value


def bind():
    for p,h in PINS.items():need(digest(ROOT/p)==h,'frozen input '+p)
    need(read(ROOT/(ORDER+'summary.json'))['status']=='INDEPENDENT_HADAMARD_SIX_PRISM_IDENTICAL_SUPPORT_ORDER_PASS','ordering review')
    result=dict(PINS)
    for p in [Path(__file__),Path(__file__).with_name('theory_20260930_hadamard_prism_binary_mip_spec.md')]:result[key(p)]=digest(p)
    expected={'highspy':'1.15.1','numpy':'2.5.3','scipy':'1.18.1','tqdm':'4.67.1'}
    need({p:version(p) for p in expected}==expected,'locked package versions')
    return result


def reconstruct():
    raw=read(ROOT/RAW);old=read(ROOT/LP);groups=read(ROOT/(ORDER+'groups.json'))
    gram=raw['prescribed_Gram36'];pairs=list(combinations_with_replacement(range(36),2));ri={p:60+i for i,p in enumerate(pairs)}
    columns=[];selectors=[];choices=[];words=[w for w in product(range(3),repeat=6) if all(w.count(g)==2 for g in range(3))]
    for d in range(60):
        coordinates=[a for a in range(12) if raw['L'][a][d]];need(coordinates==raw['support_columns'][d],'literal support')
        expected=[]
        for word in words:
            rows=sorted(12*g+a for a,g in zip(coordinates,word,strict=True))
            if any(gram[a][b]==0 for a,b in combinations(rows,2)):continue
            expected.append(dict(fibres_by_sorted_coordinate=list(word),rows=rows,row_mask_hex=format(sum(1<<r for r in rows),'09x')))
        need(expected==raw['column_colour_options'][d] and len(expected)==90,'full90 domain reconstruction')
        for rank,option in enumerate(expected):
            index=len(columns);selectors.append([d,rank]);choices.append(dict(index=index,selector_id=index+1,column=d,rank=rank,**option))
            columns.append([d]+[ri[p] for p in combinations_with_replacement(option['rows'],2)])
    rhs=[1]*60+[gram[a][b] for a,b in pairs]
    rebuilt=dict(nonnegative_variables=True,columns_nonzero_row_indices=columns,rhs=rhs,selectors=selectors,
                 Gram_row_pairs=[list(p) for p in pairs],variables=5400,equations=726,binary_coefficients=True)
    need(old==rebuilt,'entire exact archived LP matrix/metadata')
    rows=[[] for _ in rhs]
    for j,column in enumerate(columns):
        for r in column:rows[r].append([j,1])
    exactrows=[dict(kind='onehot' if i<60 else 'Gram',index=i,terms=terms,lower=rhs[i],upper=rhs[i],
                    semantic_column=i if i<60 else None,semantic_pair=None if i<60 else list(pairs[i-60])) for i,terms in enumerate(rows)]
    for d,e in groups['adjacent_order_pairs']:
        need(raw['column_colour_options'][d]==raw['column_colour_options'][e],'identical rank ordering')
        terms=[[90*d+r,r] for r in range(1,90)]+[[90*e+r,-r] for r in range(1,90)]
        exactrows.append(dict(kind='strict_rank_order',index=len(exactrows),terms=terms,lower=None,upper=-1,columns=[d,e]))
    return dict(schema='EXACT_FIXED_HADAMARD_PRISM_BINARY_MIP_V1',variables=5400,rows=exactrows,row_count=766,
        bounds=[[0,1] for _ in range(5400)],integrality=[1]*5400,objective=[0]*5400,choices=choices,
        L=raw['L'],core_adjacency=raw['core_adjacency'],matchings=raw['matchings'],target_gram36=gram,
        adjacent_order_pairs=groups['adjacent_order_pairs'],cyclic_colour_constraint=False,residual_D=False,
        input_pins=PINS,lazy_cuts=[],lower_null_meaning='negative infinity',index_convention='Zero-based MIP column; selector_id=index+1.')


def exact_vector(model,values):
    n=model['variables'];need(len(values)==n,'all native values')
    need(all(type(v) in (int,float) and math.isfinite(v) for v in values),'finite native numeric vector')
    distances=[min(abs(v),abs(v-1)) for v in values];need(max(distances,default=0)<=TOLERANCE,'binary rounding distance exceeds1e-7')
    bits=[int(v>=0.5) for v in values]
    need(len(model['bounds'])==len(model['integrality'])==n and all(b==[0,1] and all(type(v)is int for v in b) for b in model['bounds'])
        and all(type(v)is int and v==1 for v in model['integrality']),'exact binary metadata')
    evaluated=[]
    for row in model['rows']:
        need(all(row[b] is None or type(row[b])is int for b in ['lower','upper']),'exact integer row bounds')
        need(all(type(i)is int and type(c)is int and 0<=i<n and c!=0 for i,c in row['terms']),'literal integer sparse row')
        need(len({i for i,c in row['terms']})==len(row['terms']),'no duplicated coefficient IDs')
        got=sum(bits[i]*c for i,c in row['terms'])
        need(row['lower'] is None or got>=row['lower'],'exact row lower bound '+str(row['index']))
        need(row['upper'] is None or got<=row['upper'],'exact row upper bound '+str(row['index']))
        evaluated.append(got)
    return bits,dict(maximum_binary_rounding_distance=max(distances,default=0),tolerance=TOLERANCE,checked_rows=len(evaluated),row_values=evaluated)


def decode_gram(model,bits):
    need(model['variables']==5400 and len(bits)==5400,'research variable dimension')
    factor=[[0]*60 for _ in range(36)];selected=[];ranks=[]
    for d in range(60):
        active=[i for i in range(90*d,90*(d+1)) if bits[i]];need(len(active)==1,'exactone choice')
        i=active[0];choice=model['choices'][i];selected.append(i);ranks.append(choice['rank'])
        for row in choice['rows']:factor[row][d]=1
    need(all(sum(factor[i][d]*factor[j][d] for d in range(60))==model['target_gram36'][i][j] for i in range(36) for j in range(36)),'all1296 exact Gram entries')
    need([[sum(factor[12*g+a][d] for g in range(3)) for d in range(60)] for a in range(12)]==model['L'],'exactL')
    need(all(sum(factor[12*g+a][d] for a in range(12))==2 for g in range(3) for d in range(60)),'all180 fibre margins')
    need(all(ranks[d]<ranks[e] for d,e in model['adjacent_order_pairs']),'all40 ranks')
    overlaps=[];violations=[]
    for d,e in combinations(range(60),2):
        overlap=sum(factor[r][d]*factor[r][e] for r in range(36));item=dict(columns=[d,e],overlap=overlap,selected_indices=[selected[d],selected[e]])
        overlaps.append(item)
        if overlap>2:violations.append(item)
    c=model['core_adjacency'];mixed=[dict(row=r,column=d,value=factor[r][d]+sum(c[r][s]*factor[s][d] for s in range(36)))
        for r in range(36) for d in range(60) if factor[r][d]+sum(c[r][s]*factor[s][d] for s in range(36))>2]
    return dict(factor=factor,L=model['L'],core_adjacency=c,matchings=model['matchings'],selected_indices=selected,
        selected_selector_ids=[i+1 for i in selected],selected_option_ranks=ranks,target_gram36=model['target_gram36'],
        all_column_overlaps=overlaps,column_cap_violations=violations,mixed_cap_violations=mixed,
        exact_Gram_valid=True,all_caps_pass=not violations and not mixed,target_graph=False,residual_D=None,independent_approval=False)


def sparse_rows(rows,n):
    rr=[];cc=[];vv=[]
    for r,row in enumerate(rows):
        for j,value in row['terms']:rr.append(r);cc.append(j);vv.append(value)
    return coo_matrix((np.asarray(vv,dtype=np.float64),(np.asarray(rr,dtype=np.int32),np.asarray(cc,dtype=np.int32))),shape=(len(rows),n)).tocsr()


def new_solver(model,log):
    a=sparse_rows(model['rows'],model['variables']);lp=highspy.HighsLp();lp.num_row_,lp.num_col_=a.shape
    lp.col_cost_=np.zeros(model['variables']);lp.col_lower_=np.zeros(model['variables']);lp.col_upper_=np.ones(model['variables'])
    lp.integrality_=[highspy.HighsVarType.kInteger]*model['variables']
    lp.row_lower_=np.array([-highspy.kHighsInf if r['lower'] is None else r['lower'] for r in model['rows']],dtype=float)
    lp.row_upper_=np.array([highspy.kHighsInf if r['upper'] is None else r['upper'] for r in model['rows']],dtype=float)
    lp.a_matrix_.format_=highspy.MatrixFormat.kRowwise;lp.a_matrix_.start_,lp.a_matrix_.index_,lp.a_matrix_.value_=a.indptr,a.indices,a.data
    solver=highspy.Highs();options=dict(solver='choose',presolve='on',threads=1,random_seed=0,
        mip_feasibility_tolerance=TOLERANCE,primal_feasibility_tolerance=TOLERANCE,mip_rel_gap=0.0,mip_abs_gap=0.0,
        log_to_console=False,output_flag=True,log_file=str(log))
    for k,v in options.items():need(solver.setOptionValue(k,v)==highspy.HighsStatus.kOk,'accepted option '+k)
    need(solver.passModel(lp)==highspy.HighsStatus.kOk,'exact sparse model accepted')
    return solver,options


def native_call(solver,seconds,folder,options):
    need(seconds>0,'positive remaining budget');need(solver.setOptionValue('time_limit',seconds)==highspy.HighsStatus.kOk,'remaining time limit')
    log=folder/'solver.log';need(solver.setOptionValue('log_file',str(log))==highspy.HighsStatus.kOk,'per-call log')
    start=time.monotonic();before=solver.getRunTime();status=solver.run();elapsed=time.monotonic()-start
    solution=solver.getSolution();values=list(solution.col_value);info=solver.getInfo()
    fields=['mip_node_count','mip_gap','mip_dual_bound','objective_function_value','max_integrality_violation','primal_solution_status']
    raw=dict(run_status=str(status),model_status=str(solver.getModelStatus()),solution_value_valid=bool(solution.value_valid),
        col_value=[finite_json(v) for v in values],col_value_float_hex=[float(v).hex() for v in values],
        info={k:finite_json(getattr(info,k)) for k in fields},options={**options,'time_limit':seconds,'log_file':str(log)},
        wall_seconds=elapsed,highs_runtime_before=before,highs_runtime_after=solver.getRunTime(),native_version=solver.version())
    save(folder/'native_incumbent.json',raw);return raw,values


def provenance(bindings,args):
    return dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),platform=platform.uname()._asdict(),
        versions={p:version(p) for p in ['highspy','numpy','scipy','tqdm']},inputs_sha256=bindings,
        limits=dict(total_wall_seconds=TOTAL_SECONDS,maximum_research_calls=MAX_CALLS,threads=1,random_seed=0,automatic_reset=False),
        scope='One fixed six-prism Hadamard L, all colourings modulo identical-support order; no cyclic constraint or residualD.',
        target_resolution='UNKNOWN',independent_approval=False)


def prepare(args,bindings):
    model=reconstruct();save(args.out/'exact_model.json',model)
    save(args.out/'summary.json',{**provenance(bindings,args),'status':'CANDIDATE_EXACT_FIXED_SUPPORT_BINARY_MIP_MODEL',
        'variables':5400,'equality_rows':726,'order_rows':40,'solver_calls':0,'matrix_sha256':digest(args.out/'exact_model.json'),
        'matrix_path':key(args.out/'exact_model.json')})


def controls(args,bindings):
    model=dict(variables=4,bounds=[[0,1]]*4,integrality=[1]*4,rows=[
        dict(index=0,terms=[[0,1],[1,1]],lower=1,upper=1),dict(index=1,terms=[[2,1],[3,1]],lower=1,upper=1),
        dict(index=2,terms=[[1,1],[3,-1]],lower=None,upper=-1)])
    valid=[1,0,0,1];exact_vector(model,valid);rejected=[]
    def reject(label,fn):
        try:fn()
        except (ValueError,IndexError,KeyError):rejected.append(label)
        else:raise ValueError('corrupted control accepted '+label)
    for label,vector in [('fractional',[.5,.5,.5,.5]),('beyond_tolerance',[1+2e-7,0,0,1]),('wrong_order',[0,1,1,0]),('missing',[1,0,0]),('nonfinite',[float('nan'),0,0,1])]:reject(label,lambda vector=vector:exact_vector(model,vector))
    for label in ['bounds','integrality','coefficient','false_cut','duplicate_index']:
        bad=deepcopy(model)
        if label=='bounds':bad['bounds'][0]=[0,2]
        elif label=='integrality':bad['integrality'][0]=0
        elif label=='coefficient':bad['rows'][0]['terms'][0][1]=2
        elif label=='false_cut':bad['rows'].append(dict(index=3,terms=[[0,1],[3,1]],lower=None,upper=1))
        else:bad['rows'][0]['terms'].append([0,1])
        reject(label,lambda bad=bad:exact_vector(bad,valid))
    solver,options=new_solver(model,args.out/'solver.log');native,values=native_call(solver,5,args.out,options)
    bits,check=exact_vector(model,values);need(bits==valid,'known unique positive MIP solution')
    rebuilt=reconstruct();need(len(rebuilt['rows'])==766,'complete research matrix reconstruction control')
    save(args.out/'summary.json',{**provenance(bindings,args),'status':'PRODUCER_MIP_CONTROLS_PENDING_INDEPENDENT_REVIEW',
        'known_positive_bits':bits,'exact_checks':check,'corruptions_rejected':rejected,'tiny_solver_calls':1,'research_calls':0,
        'research_positive_factor':None,'research_positive_factor_null_reason':'No complete research factor known.'})


def research(args,bindings):
    need(args.matrix and args.review_gate and args.review_gate_sha256,'independent MIP calibration required')
    need(digest(args.review_gate)==args.review_gate_sha256,'exact review report')
    gate=read(args.review_gate);need(gate['status']=='INDEPENDENT_FIXED_SUPPORT_PRISM_BINARY_MIP_MODEL_OBJECT_CALIBRATION_PASS','independent MIP model/object gate')
    for p,h in gate['inputs_sha256'].items():need(digest(ROOT/p)==h,'unchanged independent input '+p)
    need(gate['inputs_sha256'][key(args.matrix)]==digest(args.matrix),'gate binds exact matrix')
    need(gate['inputs_sha256'][key(Path(__file__))]==digest(__file__),'gate binds actual source')
    model=read(args.matrix);need(model==reconstruct(),'literal complete prepared matrix')
    bindings.update({key(args.matrix):digest(args.matrix),key(args.review_gate):args.review_gate_sha256})
    save(args.out/'manifest.json',provenance(bindings,args));start=time.monotonic();solver,options=new_solver(model,args.out/'initial.log')
    attempts=[];cutset=set();reason='CALL_LIMIT';exact_gram_objects=0
    for index in range(MAX_CALLS):
        remaining=TOTAL_SECONDS-(time.monotonic()-start)
        if remaining<=0:reason='TOTAL_WALL_BUDGET';break
        folder=args.out/f'attempt_{index:02d}';folder.mkdir();save(folder/'exact_model.json',model)
        save(folder/'launch.json',dict(remaining_wall_seconds=remaining,exact_matrix_sha256=digest(folder/'exact_model.json'),
            ordered_prior_cuts=sorted([list(x) for x in cutset]),reused_same_solver_instance=index>0))
        raw,values=native_call(solver,remaining,folder,options)
        attempt=dict(index=index,model_status=raw['model_status'],wall_seconds=raw['wall_seconds'],integer_incumbent=False)
        attempts.append(attempt)
        if not raw['solution_value_valid']:reason='NO_VALID_NATIVE_INCUMBENT';break
        try:
            bits,check=exact_vector(model,values);save(folder/'exact_integer_assignment.json',dict(bits=bits,checks=check))
            factor=decode_gram(model,bits);save(folder/'decoded_Gram_factor.json',factor)
        except (ValueError,IndexError,KeyError) as error:
            save(folder/'incumbent_rejection.json',dict(reason=str(error)));reason='EXACT_INCUMBENT_CHECK_FAILED';break
        exact_gram_objects+=1;attempt.update(integer_incumbent=True,column_cap_violations=len(factor['column_cap_violations']),all_caps_pass=factor['all_caps_pass'])
        if factor['all_caps_pass']:reason='CANDIDATE_FULL_FACTOR_PENDING_INDEPENDENT_REVIEW';break
        need(not factor['mixed_cap_violations'],'identity-P mixed-cap theorem or decoder inconsistency')
        new=sorted({tuple(sorted(v['selected_indices'])) for v in factor['column_cap_violations']}-cutset)
        if not new:reason='NO_NEW_SOUND_CUT';break
        rows=[]
        for a,b in new:
            ca,cb=model['choices'][a],model['choices'][b];overlap=len(set(ca['rows'])&set(cb['rows']))
            need(ca['column']!=cb['column'] and overlap>2,'exact raw paircut witness')
            rows.append(dict(kind='column_cap_lazy_cut',index=len(model['rows'])+len(rows),terms=[[a,1],[b,1]],lower=None,upper=1,
                selected_indices=[a,b],source_attempt=index,columns=[ca['column'],cb['column']],option_ranks=[ca['rank'],cb['rank']],
                raw_selected_rows=[ca['rows'],cb['rows']],exact_overlap=overlap))
        save(folder/'new_exact_cuts.json',rows);cutset.update(new);model['rows'].extend(rows);model['row_count']=len(model['rows']);model['lazy_cuts'].extend(rows)
        if index+1==MAX_CALLS:reason='CALL_LIMIT';break
        if time.monotonic()-start>=TOTAL_SECONDS:reason='TOTAL_WALL_BUDGET';break
        a=sparse_rows(rows,5400)
        need(solver.addRows(len(rows),np.full(len(rows),-highspy.kHighsInf),np.ones(len(rows)),a.nnz,a.indptr,a.indices,a.data)==highspy.HighsStatus.kOk,'add exact sound pair cuts')
    elapsed=time.monotonic()-start
    save(args.out/'summary.json',{**provenance(bindings,args),'status':'BINARY_MIP_ARTIFACTS_PENDING_INDEPENDENT_REVIEW','stop_reason':reason,
        'research_calls':len(attempts),'attempts':attempts,'saved_exact_Gram_incumbents':exact_gram_objects,'distinct_lazy_cuts':len(cutset),
        'observed_total_wall_seconds':elapsed,'cooperative_budget_overrun_seconds':max(0,elapsed-TOTAL_SECONDS),
        'numerical_status_is_exclusion':False,'outputs_sha256':{key(p):digest(p) for p in args.out.rglob('*') if p.is_file()}})


def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['prepare','controls','research']);ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--matrix',type=Path);ap.add_argument('--review-gate',type=Path);ap.add_argument('--review-gate-sha256')
    args=ap.parse_args();args.out=args.out.resolve();need(args.out.is_relative_to(ROOT),'workspace output');args.out.mkdir(parents=True,exist_ok=False)
    try:
        bindings=bind();{'prepare':prepare,'controls':controls,'research':research}[args.mode](args,bindings)
    except BaseException as error:
        save(args.out/'failure.json',dict(error=repr(error),timestamp=datetime.now(timezone.utc).isoformat(),source_sha256=digest(__file__),
            mathematical_exclusion=False,partial_artifacts_preserved=True));raise


if __name__=='__main__':main()
