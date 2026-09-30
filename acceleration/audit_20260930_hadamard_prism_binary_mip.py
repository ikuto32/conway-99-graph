"""Independent exact direct-MIP model, sound-cut and raw-incumbent checks."""
from copy import deepcopy
from datetime import datetime,timezone
from itertools import combinations
from pathlib import Path
import argparse,json,math,platform,subprocess,sys
import audit_20260930_hadamard_prism_ordered_cnf as domain
import audit_20260930_hadamard_mip_raw as rawcheck
import audit_20260930_fixed_support_raw_preparation as full
ROOT=domain.ROOT;B=domain.B;RAW=domain.RAW
LP=B/'20260930_hadamard_support_remaining_lp/six_prism/exact_model.json'
SOURCE=ROOT/'acceleration/theory_20260930_hadamard_prism_binary_mip.py'
SOURCE_SHA='493525947e728094357f800e0dd555e22468e58b5c98dc2a255ae7e3b1beefa2'
need,read,save,digest,key=domain.need,domain.read,domain.save,domain.digest,domain.key

def expected_model(raw,lp):
    core,gram,l,supports,domains,groups=domain.reconstruct(raw);pairs=[(i,j)for i in range(36)for j in range(i,36)];position={pair:60+i for i,pair in enumerate(pairs)}
    columns=[];selectors=[];choices=[]
    for d,record in enumerate(domains):
        for j,choice in enumerate(record['choices']):
            rows=choice['rows'];index=90*d+j;columns.append([d]+[position[a,b]for a in rows for b in rows if a<=b]);selectors.append([d,j]);choices.append(dict(index=index,selector_id=index+1,column=d,rank=j,fibres_by_sorted_coordinate=choice['fibres_by_sorted_coordinate'],rows=rows,row_mask_hex=choice['row_mask_hex']))
    rhs=[1]*60+[gram[i][j]for i,j in pairs];wantlp=dict(nonnegative_variables=True,columns_nonzero_row_indices=columns,rhs=rhs,selectors=selectors,Gram_row_pairs=[list(p)for p in pairs],variables=5400,equations=726,binary_coefficients=True);need(lp==wantlp,'complete legacy LP matrix identity')
    terms=[[]for _ in rhs]
    for index,col in enumerate(columns):
        for r in col:terms[r].append([index,1])
    rows=[dict(kind='onehot'if i<60 else'Gram',index=i,terms=term,lower=rhs[i],upper=rhs[i],semantic_column=i if i<60 else None,semantic_pair=None if i<60 else list(pairs[i-60]))for i,term in enumerate(terms)]
    adjacent=[p for cols in groups for p in [[cols[0],cols[1]],[cols[1],cols[2]]]]
    for d,e in adjacent:rows.append(dict(kind='strict_rank_order',index=len(rows),terms=[[90*d+j,j]for j in range(1,90)]+[[90*e+j,-j]for j in range(1,90)],lower=None,upper=-1,columns=[d,e]))
    expected=dict(schema='EXACT_FIXED_HADAMARD_PRISM_BINARY_MIP_V1',variables=5400,rows=rows,row_count=766,bounds=[[0,1]for _ in range(5400)],integrality=[1]*5400,objective=[0]*5400,choices=choices,L=l,core_adjacency=core,matchings=raw['matchings'],target_gram36=gram,adjacent_order_pairs=adjacent,cyclic_colour_constraint=False,residual_D=False,lazy_cuts=[],lower_null_meaning='negative infinity',index_convention='Zero-based MIP column; selector_id=index+1.')
    return expected,columns,rhs

def cut_check(cut,index,choices):
    ids=cut['selected_indices'];need(type(ids)is list and len(ids)==2 and all(type(v)is int and 0<=v<5400 for v in ids)and ids==sorted(set(ids)),'valid distinct ordered cut indices');a,b=ids;x,y=choices[a],choices[b]
    overlap=len(set(x['rows']).intersection(y['rows']));need(x['column']!=y['column']and overlap>2,'sound literal forbidden outside-column pair')
    expected=dict(kind='column_cap_lazy_cut',index=index,terms=[[a,1],[b,1]],lower=None,upper=1,selected_indices=ids,source_attempt=cut['source_attempt'],columns=[x['column'],y['column']],option_ranks=[x['rank'],y['rank']],raw_selected_rows=[x['rows'],y['rows']],exact_overlap=overlap)
    need(type(cut['source_attempt'])is int and 0<=cut['source_attempt']<3 and json.dumps(cut,sort_keys=True)==json.dumps(expected,sort_keys=True),'complete exact cut coefficients and raw witness');return ids

def model_check(model,expected):
    need(set(model)==set(expected)|{'input_pins'},'exact matrix schema keys');base={k:v for k,v in model.items()if k not in['input_pins','rows','row_count','lazy_cuts']}
    need(json.dumps(base,sort_keys=True)==json.dumps({k:v for k,v in expected.items()if k not in['rows','row_count','lazy_cuts']},sort_keys=True),'exact domains, binary bounds, objective, support and scope')
    need(json.dumps(model['rows'][:766],sort_keys=True)==json.dumps(expected['rows'],sort_keys=True),'all726 equalities and40 strict-order rows')
    need(model['row_count']==len(model['rows'])==766+len(model['lazy_cuts'])and model['rows'][766:]==model['lazy_cuts'],'complete appended-cut suffix')
    cuts=[cut_check(c,766+i,model['choices'])for i,c in enumerate(model['lazy_cuts'])];need(len(cuts)==len({tuple(p)for p in cuts}),'no duplicated cut identities')
    for p,h in model['input_pins'].items():need(digest(ROOT/p)==h,'raw matrix input pin '+p)
    need(model['input_pins'][key(RAW)]==domain.RAW_SHA and model['input_pins'][key(LP)]=='f5ac7adc289d6ca3cc7ce77394565919813138f6322e5ae2dc1856684eef6ae2'and model['input_pins'][key(domain.ORDER)]==domain.ORDER_SHA,'required literal premise pins')
    return cuts

def decode(bits,expected):
    selected=[];ranks=[];factor=[[0]*60 for _ in range(36)]
    for d in range(60):
        chosen=[i for i in range(90*d,90*(d+1))if bits[i]];need(len(chosen)==1,'exactly one chosen actual colouring');i=chosen[0];selected.append(i);rank=i-90*d;ranks.append(rank);choice=expected['choices'][i]
        coordinates=[a for a in range(12)if expected['L'][a][d]]
        for a,g in zip(coordinates,choice['fibres_by_sorted_coordinate'],strict=True):factor[12*g+a][d]=1
    need(all(ranks[d]<ranks[e]for d,e in expected['adjacent_order_pairs']),'literal forty rank inequalities');return selected,ranks,factor

def check_incumbent(model,expected,columns,rhs,native,decoded=None,integer_assignment=None):
    cuts=model_check(model,expected);need(native['solution_value_valid']is True,'native validity flag for a claimed incumbent')
    values=native['col_value'];need(len(native['col_value_float_hex'])==5400 and all(type(v)in(int,float)and math.isfinite(v)and float(v).hex()==h for v,h in zip(values,native['col_value_float_hex'],strict=True)),'all exact saved native float encodings')
    bits,rounding=rawcheck.rounded_binary(values,5400);rowvalues,ordervalues=rawcheck.exact_linear(bits,columns,rhs,expected['rows'][726:],cuts);selected,ranks,factor=decode(bits,expected)
    result=rawcheck.gram_factor(expected['core_adjacency'],factor,expected['L']);need(result['prescribed_gram']==expected['target_gram36'],'exact model/independent Gram equality')
    if integer_assignment is not None:need(integer_assignment['bits']==bits,'all producer rounded bits')
    if decoded is not None:
        compare=dict(factor=factor,L=expected['L'],core_adjacency=expected['core_adjacency'],matchings=expected['matchings'],selected_indices=selected,selected_selector_ids=[i+1 for i in selected],selected_option_ranks=ranks,target_gram36=expected['target_gram36'],exact_Gram_valid=True,all_caps_pass=result['all_caps_valid'],target_graph=False,residual_D=None)
        for field,want in compare.items():need(type(decoded[field])is type(want)and decoded[field]==want,'producer raw comparison '+field)
        overlaps=[dict(columns=[d,e],overlap=value,selected_indices=[selected[d],selected[e]])for d,e,value in result['all_column_overlaps']];need(decoded['all_column_overlaps']==overlaps and decoded['column_cap_violations']==[v for v in overlaps if v['overlap']>2]and decoded['mixed_cap_violations']==result['mixed_cap_violations'],'all cap records compared independently')
    if result['all_caps_valid']:
        second,_,_=full.verify_fixed_support(expected['core_adjacency'],factor,expected['L']);need(second['canonical_factor']['incidence_matrix']==result['canonical_factor'],'separate complete full-factor path')
    return {**result,'selected_indices':selected,'selected_option_ranks':ranks,'rounding_check':rounding,'all_equality_values':rowvalues,'all_order_values':ordervalues,'rounded_bits':bits}

def native_matrix_roundtrip(expected):
    # Build independent column-major data directly from raw exact rows. No
    # scipy conversion or producer matrix function is called and no run occurs.
    import highspy
    import numpy as np
    columns=[[]for _ in range(5400)]
    for r,row in enumerate(expected['rows']):
        for j,value in row['terms']:columns[j].append((r,value))
    starts=[0];indices=[];values=[]
    for col in columns:
        for row,value in col:indices.append(row);values.append(value)
        starts.append(len(indices))
    lp=highspy.HighsLp();lp.num_col_=5400;lp.num_row_=766;lp.col_cost_=[0.0]*5400;lp.col_lower_=[0.0]*5400;lp.col_upper_=[1.0]*5400;lp.integrality_=[highspy.HighsVarType.kInteger]*5400
    lp.row_lower_=[-highspy.kHighsInf if row['lower']is None else row['lower']for row in expected['rows']];lp.row_upper_=[row['upper']for row in expected['rows']]
    lp.a_matrix_.format_=highspy.MatrixFormat.kColwise;lp.a_matrix_.start_=starts;lp.a_matrix_.index_=indices;lp.a_matrix_.value_=values
    solver=highspy.Highs();need(solver.setOptionValue('output_flag',False)==highspy.HighsStatus.kOk and solver.passModel(lp)==highspy.HighsStatus.kOk,'independent full exact model accepted without solve');got=solver.getLp()
    need(got.num_col_==5400 and got.num_row_==766 and list(got.col_lower_)==[0.0]*5400 and list(got.col_upper_)==[1.0]*5400 and list(got.col_cost_)==[0.0]*5400 and list(got.integrality_)==[highspy.HighsVarType.kInteger]*5400,'native exact dimensions,bounds,integrality,objective')
    need(list(got.row_lower_)==list(lp.row_lower_)and list(got.row_upper_)==list(lp.row_upper_),'native all row bounds')
    need(got.a_matrix_.format_==highspy.MatrixFormat.kColwise and list(got.a_matrix_.start_)==starts and list(got.a_matrix_.index_)==indices and list(got.a_matrix_.value_)==values,'all exact native sparse coefficients roundtrip')
    return dict(highs_version=solver.version(),rows=766,columns=5400,nonzero_coefficients=len(values),native_run_calls=0,all_integer_coefficients_exact_in_float64=True,independent_conversion='Column-major lists, no scipy/producer builder import.')

def model_controls(model,expected,columns,rhs):
    rejected=[]
    def reject(label,fn):
        try:fn()
        except(ValueError,KeyError,IndexError,TypeError):rejected.append(label)
        else:raise ValueError('accepted bad model/control '+label)
    for label in ['coefficient','RHS','binary_bound','integrality','objective','Boolean_coefficient','order_upper','order_direction','deleted_choice','cyclic_restriction','support']:
        bad=deepcopy(model)
        if label=='coefficient':bad['rows'][0]['terms'][0][1]=2
        elif label=='RHS':bad['rows'][0]['lower']=2
        elif label=='binary_bound':bad['bounds'][0]=[0,2]
        elif label=='integrality':bad['integrality'][0]=0
        elif label=='objective':bad['objective'][0]=1
        elif label=='Boolean_coefficient':bad['rows'][0]['terms'][0][1]=True
        elif label=='order_upper':bad['rows'][726]['upper']=0
        elif label=='order_direction':bad['rows'][726]['terms'][0][1]*=-1
        elif label=='deleted_choice':bad['choices'].pop()
        elif label=='cyclic_restriction':bad['cyclic_colour_constraint']=True
        else:bad['L'][0][0]^=1
        reject(label,lambda bad=bad:model_check(bad,expected))
    a=0;x=expected['choices'][a];b=next(i for i,y in enumerate(expected['choices'])if y['column']!=x['column']and len(set(x['rows'])&set(y['rows']))>2);y=expected['choices'][b]
    cut=dict(kind='column_cap_lazy_cut',index=766,terms=[[a,1],[b,1]],lower=None,upper=1,selected_indices=[a,b],source_attempt=0,columns=[x['column'],y['column']],option_ranks=[x['rank'],y['rank']],raw_selected_rows=[x['rows'],y['rows']],exact_overlap=len(set(x['rows'])&set(y['rows'])))
    extended=deepcopy(model);extended['rows'].append(cut);extended['lazy_cuts'].append(cut);extended['row_count']+=1;need(model_check(extended,expected)==[[a,b]],'actual-domain sound cut positive')
    for label in ['overlap','coefficient','bound','false_pair','source_attempt']:
        bad=deepcopy(cut)
        if label=='overlap':bad['exact_overlap']=0
        elif label=='coefficient':bad['terms'][0][1]=-1
        elif label=='bound':bad['upper']=2
        elif label=='false_pair':bad['selected_indices']=[0,1]
        else:bad['source_attempt']=3
        reject('cut_'+label,lambda bad=bad:cut_check(bad,766,expected['choices']))
    bits=[0]*5400
    groups={}
    for d in range(60):groups.setdefault(tuple(a for a in range(12)if expected['L'][a][d]),[]).append(d)
    for cols in groups.values():
        for rank,d in enumerate(cols):bits[90*d+rank]=1
    selected,ranks,factor=decode(bits,expected);need(len(selected)==60 and all(sum(factor[12*g+a][d]for a in range(12))==2 for d in range(60)for g in range(3)),'local actual-model codec positive')
    reject('local_codec_not_Gram',lambda:rawcheck.exact_linear(bits,columns,rhs,expected['rows'][726:],[]))
    return dict(corruptions_rejected=rejected,actual_domain_sound_cut_positive=cut,local_codec_selected_indices=selected,local_codec_option_ranks=ranks,local_codec_factor=factor,local_codec_is_research_factor=False)

def provenance(bindings):
    return dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,verifier='/root/state_literature_audit',artifact_availability='LOCAL_ONLY',target_resolution=False,producer_imports=False,shared_components=['Frozen independently authored ordered-domain reconstruction, raw integer factor helpers and exact rounding/linear helpers.','Highs/native conversion control uses highspy/numpy only; no solver.run call in this audit.','No producer matrix/decoder/cut function imported.'],limitations=['One fixed six-prism coordinate support only, with no cyclic restriction and no target automorphism premise.','Numerical infeasibility or absence of an incumbent is never an exclusion.','A Gram-valid object with cap violations is weaker evidence; all caps are required before residual completion.'])

def main():
    ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='mode',required=True)
    c=sub.add_parser('calibrate');c.add_argument('--model-summary',type=Path,required=True);c.add_argument('--model-summary-sha256',required=True);c.add_argument('--producer-controls',type=Path,required=True);c.add_argument('--producer-controls-sha256',required=True);c.add_argument('--out',type=Path,required=True)
    a=sub.add_parser('audit');a.add_argument('--run',type=Path,required=True);a.add_argument('--summary-sha256',required=True);a.add_argument('--gate',type=Path,required=True);a.add_argument('--gate-sha256',required=True);a.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);bindings={}
    def pin(p,h=None):
        value=digest(p);need(h is None or value==h,'input identity '+key(p));bindings[key(p)]=value
    try:
        pin(SOURCE,SOURCE_SHA);pin(RAW,domain.RAW_SHA);pin(LP,'f5ac7adc289d6ca3cc7ce77394565919813138f6322e5ae2dc1856684eef6ae2');pin(domain.ORDER,domain.ORDER_SHA)
        rawgate=B/'20260930_independent_review/hadamard_mip_raw_controls/summary.json';pin(rawgate,'fe472fcf0b9b7d43698f7e523144475f847103e8cc42d6e82b8efb54836698eb')
        for p,h in read(rawgate)['inputs_sha256'].items():pin(ROOT/p,h)
        expected,columns,rhs=expected_model(read(RAW),read(LP))
        if args.mode=='calibrate':
            pin(args.model_summary,args.model_summary_sha256);prepared=read(args.model_summary);need(prepared['status']=='CANDIDATE_EXACT_FIXED_SUPPORT_BINARY_MIP_MODEL'and prepared['solver_calls']==0,'prepared-only exact model')
            for p,h in prepared['inputs_sha256'].items():pin(ROOT/p,h)
            matrixpath=ROOT/prepared['matrix_path'];pin(matrixpath,prepared['matrix_sha256']);model=read(matrixpath);need(model_check(model,expected)==[],'base model has no hidden cuts')
            control=model_controls(model,expected,columns,rhs);save(out/'model_controls.json',control);roundtrip=native_matrix_roundtrip(expected);save(out/'native_model_roundtrip.json',roundtrip)
            pin(args.producer_controls,args.producer_controls_sha256);pcontrols=read(args.producer_controls)
            for p,h in pcontrols['inputs_sha256'].items():pin(ROOT/p,h)
            nativepath=args.producer_controls.parent/'native_incumbent.json';pin(nativepath);tiny=read(nativepath);tinybits,tinyround=rawcheck.rounded_binary(tiny['col_value'],4)
            need(tinybits==[1,0,0,1]and tiny['solution_value_valid']is True and pcontrols['known_positive_bits']==tinybits,'separate tiny known integral solution')
            need([float(v).hex()for v in tiny['col_value']]==tiny['col_value_float_hex'],'tiny native exactfloat identities');save(out/'tiny_native_control.json',dict(bits=tinybits,rounding=tinyround,scope='Four-variable unique tiny positive; no research solve.'))
            for p in [Path(__file__),Path(domain.__file__),Path(rawcheck.__file__),ROOT/'docs/AUDIT_20260930_HADAMARD_PRISM_BINARY_MIP.md',ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(p)
            report={**provenance(bindings),'status':'INDEPENDENT_FIXED_SUPPORT_PRISM_BINARY_MIP_MODEL_OBJECT_CALIBRATION_PASS','matrix_path':key(matrixpath),'matrix_sha256':digest(matrixpath),'variables':5400,'equalities':726,'strict_order_inequalities':40,'full_Gram_entries_on_incumbent':1296,'column_caps_on_incumbent':1770,'mixed_caps_on_incumbent':2160,'native_matrix_roundtrip':roundtrip,'raw_helper_calibration_sha256':digest(rawgate),'corruptions_rejected':control['corruptions_rejected'],'rounding_threshold_exact':[1,10000000],'research_positive_factor':None,'research_positive_factor_null_reason':'Known243 is a nonempty generic positive; actual-model local codecs are not research factors.','research_calls':0,'native_run_calls_in_this_audit':0}
        else:
            pin(args.gate,args.gate_sha256);gate=read(args.gate);need(gate['status']=='INDEPENDENT_FIXED_SUPPORT_PRISM_BINARY_MIP_MODEL_OBJECT_CALIBRATION_PASS','exact model/object gate')
            for p,h in gate['inputs_sha256'].items():pin(ROOT/p,h)
            summarypath=args.run/'summary.json';pin(summarypath,args.summary_sha256);summary=read(summarypath);manifest=read(args.run/'manifest.json');pin(args.run/'manifest.json')
            for p,h in {**summary['inputs_sha256'],**summary['outputs_sha256']}.items():pin(ROOT/p,h)
            need(summary['research_calls']==len(summary['attempts'])<=3 and summary['numerical_status_is_exclusion']is False,'bounded attempt population, no exclusion');previouscuts=[];cases=[]
            for index,attempt in enumerate(summary['attempts']):
                folder=args.run/f'attempt_{index:02d}';model=read(folder/'exact_model.json');cuts=model_check(model,expected);need(cuts==previouscuts,'exact prior cut suffix');launch=read(folder/'launch.json');need(launch['exact_matrix_sha256']==digest(folder/'exact_model.json')and launch['ordered_prior_cuts']==sorted(previouscuts)and launch['reused_same_solver_instance']==(index>0),'actual model launch binding')
                native=read(folder/'native_incumbent.json');need(len(native['col_value'])==len(native['col_value_float_hex'])==5400,'complete saved raw vector')
                need(native['options']['threads']==1 and native['options']['random_seed']==0 and native['options']['mip_feasibility_tolerance']==1e-7 and native['options']['time_limit']==launch['remaining_wall_seconds']and 0<launch['remaining_wall_seconds']<=120,'actual frozen per-call options')
                record=dict(attempt=index,model_status=native['model_status'],native_solution_value_valid=native['solution_value_valid'],exact_Gram_object_checked=False)
                if attempt['integer_incumbent']:
                    result=check_incumbent(model,expected,columns,rhs,native,read(folder/'decoded_Gram_factor.json'),read(folder/'exact_integer_assignment.json'));save(out/f'attempt_{index:02d}_independent_factor.json',result);record.update(exact_Gram_object_checked=True,classification=result['classification'],all_caps_valid=result['all_caps_valid'],column_cap_violations=len(result['column_cap_violations']))
                    if(folder/'new_exact_cuts.json').exists():
                        new=read(folder/'new_exact_cuts.json');ids=[cut_check(c,766+len(previouscuts)+i,expected['choices'])for i,c in enumerate(new)];want=sorted({tuple(sorted([result['selected_indices'][x['columns'][0]],result['selected_indices'][x['columns'][1]]]))for x in result['column_cap_violations']}-{tuple(x)for x in previouscuts});need(ids==[list(x)for x in want]and all(c['source_attempt']==index for c in new),'all and only newly discovered selected cap violations');previouscuts.extend(ids)
                else:
                    need(not(folder/'decoded_Gram_factor.json').exists(),'no unreviewed exact object hidden from attempt count')
                    if native['solution_value_valid']:
                        try:check_incumbent(model,expected,columns,rhs,native)
                        except(ValueError,KeyError,IndexError,TypeError)as error:record['independent_incumbent_rejection']=str(error)
                        else:raise ValueError('An exact Gram incumbent was omitted by the producer; preserve and review it before accepting this execution summary.')
                cases.append(record)
            need(summary['distinct_lazy_cuts']==len(previouscuts),'distinct saved cuts count')
            report={**provenance(bindings),'status':'INDEPENDENT_FIXED_SUPPORT_PRISM_BINARY_MIP_RUN_AUDIT_PASS','actual_research_calls':len(cases),'attempts':cases,'distinct_sound_lazy_cuts':len(previouscuts),'producer_stop_reason':summary['stop_reason'],'observed_total_wall_seconds':summary['observed_total_wall_seconds'],'cooperative_budget_overrun_seconds':summary['cooperative_budget_overrun_seconds'],'numerical_status_is_exclusion':False,'checked_full_factor_count':sum(x.get('all_caps_valid',False)for x in cases),'checked_Gram_object_count':sum(x['exact_Gram_object_checked']for x in cases)}
        report['outputs_sha256']={key(p):digest(p)for p in out.rglob('*')if p.is_file()};save(out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(out/'summary.json'))))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e)));raise
if __name__=='__main__':main()
