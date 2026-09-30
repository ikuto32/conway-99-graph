"""Independent complete CNF audit for one balanced parity-lift branch."""
from collections import Counter
from copy import deepcopy
from datetime import datetime,timezone
from itertools import combinations
from pathlib import Path
import argparse,io,json,platform,subprocess,sys,time
from tqdm import tqdm
import audit_20260930_hadamard_parity_lift_domains as local
import audit_20260930_eight_full99_cnf_v1 as gates
ROOT=local.ROOT;B=ROOT/'acceleration/results';D=B/'20260930_hadamard_parity_lift_cnf'
need,digest,key,save=gates.need,gates.digest,gates.key,gates.save
GATES_SHA='c956504752a937ffa6aa1ad84d4aa30d95db8723287970e76cbfd262b74ecf4c'
PRODUCER_PROJECTION=B/'20260930_hadamard_balanced_parity_native_pilot/main/decoded_projection.json'
PRODUCER_PROJECTION_SHA='0e80251a964330092d8da9030df2e2ee7f56476cee9e588be921dbe2f470e646'
def read(p):return json.loads(Path(p).read_bytes())
def same(a,b):return json.dumps(a,sort_keys=True)==json.dumps(b,sort_keys=True)

def domains(data):
    result=[]
    for d in data['domains']:
        choices=[]
        for j,x in enumerate(d['choices']):
            choices.append(dict(selector=x['selector'],choice_index=j,balanced_triple_index=x['local_triple_index'],word_indices=x['word_indices'],color_words=x['words'],lifted_rows=x['column_rows'],lifted_masks_hex=x['column_masks_hex']))
        result.append(dict(group=d['group'],support_coordinates=d['coordinates'],raw_columns=d['columns'],selected_parity_pattern=d['parity'],choices=choices))
    return result

def scope_check(model,scope,data):
    ds=domains(data);projection=read(local.PROJECTION)
    need(scope['schema']=='FIXED_HADAMARD_SINGLE_PARITY_BALANCED_LIFT_SCOPE_V1','scope schema')
    expected=dict(raw_support=key(local.RAW),raw_support_sha256=local.RAW_SHA,parity_projection=key(PRODUCER_PROJECTION),parity_projection_sha256=PRODUCER_PROJECTION_SHA,matchings=[[i^1 for i in range(12)]for _ in range(3)],core_adjacency=data['core'],target_gram36=data['gram'],L=data['L'],domains=ds,selected_pattern_indices=projection['selected_pattern_indices'],balanced_group_columns=True,one_fixed_parity_branch=True,all_balanced_branches_covered=False,arbitrary_fixedL_factors_covered=False,column_word_order='Strictly increasing word indices along the ascending three raw columns of each identical-support group.',residual_D_encoded=False,target_graph=False,no_target_automorphism_assumed=True)
    need(set(scope)==set(expected)|{'schema'},'complete scope field inventory')
    for k,v in expected.items():need(same(scope[k],v),'scope '+k)
    need(model['schema']=='HADAMARD_SINGLE_PARITY_BALANCED_LIFT_PREFIX_CNF_V1' and model['primary_selectors']==312,'model schema/primary count')
    need(same(model['domains'],ds),'all312 reconstructed selector domains')
    need(model['scope_path']==key(D/'scope.json') and model['scope_sha256']==digest(D/'scope.json') and model['full_target_encoded']is False,'exact model scope identity')
    return ds

def gram_inputs(ds,i,j):
    result=[]
    for d in ds:
        for x in d['choices']:
            count=sum(i in rows and j in rows for rows in x['lifted_rows'])
            need(count in(0,1),'balanced local triple gives binary Gram coefficient')
            if count:result.append(x['selector'])
    return result

def cap_record(left,right,first):
    hist=Counter();masks=[];clauses=[]
    for x in left['choices']:
        xs=[frozenset(row)for row in x['lifted_rows']];mask=0
        for j,y in enumerate(right['choices']):
            maximum=max(len(a.intersection(b))for a in xs for b in y['lifted_rows']);hist[maximum]+=1
            if maximum>2:mask|=1<<j;clauses.append(tuple(sorted([-x['selector'],-y['selector']])))
        masks.append(format(mask,'x'))
    record=dict(groups=[left['group'],right['group']],actual_column_pairs=[[a,b]for a in left['raw_columns']for b in right['raw_columns']],forbidden_right_masks_hex=masks,maximum_overlap_histogram={str(k):v for k,v in sorted(hist.items())},first_clause=first,clause_count=len(clauses))
    return record,clauses

def check_cnf(model,scope,data,path):
    ds=scope_check(model,scope,data);rows=model['counter_rows'];ri=0;sections=[];pairs=0;forbidden=0
    with path.open('rb')as stream:
        need(stream.readline()==f"p cnf {model['variables']} {model['clauses']}\n".encode(),'literal full DIMACS header')
        cursor=gates.ClauseCursor(stream,model['variables']);audit=gates.GateAudit(cursor,312);first=1
        for d in ds:
            audit.counter(rows[ri],[x['selector']for x in d['choices']],1,True,dict(kind='group_exactone',group=d['group']));ri+=1
        sections.append(dict(kind='20group_exactone',first_clause=first,last_clause=cursor.count,count=cursor.count-first+1));first=cursor.count+1
        for i in tqdm(range(36),desc='Independent one-branch Gram counters'):
            for j in range(i,36):
                audit.counter(rows[ri],gram_inputs(ds,i,j),data['gram'][i][j],True,dict(kind='gram_count',rows=[i,j]));ri+=1
        sections.append(dict(kind='666exact_Gram_counts',first_clause=first,last_clause=cursor.count,count=cursor.count-first+1));first=cursor.count+1
        for k,(p,q)in enumerate(combinations(range(20),2)):
            expected,clauses=cap_record(ds[p],ds[q],cursor.count+1);need(same(model['lifted_cap_relations'][k],expected),'all raw9 cap overlaps '+str((p,q)));cursor.consume(clauses)
            pairs+=len(ds[p]['choices'])*len(ds[q]['choices']);forbidden+=len(clauses)
        sections.append(dict(kind='190lifted_cap_choice_relations',first_clause=first,last_clause=cursor.count,count=cursor.count-first+1))
        need(stream.read()==b'','no omitted or additional clauses')
    need(ri==len(rows)==686 and len(model['lifted_cap_relations'])==190,'complete row and cap populations')
    need(audit.top==model['variables'] and cursor.count==model['clauses'] and same(model['clause_sections'],sections),'all fresh auxiliary IDs and clause ranges')
    return dict(variables=audit.top,clauses=cursor.count,primary_selectors=312,domains=20,domain_sizes=[len(d['choices'])for d in ds],onehot_rows=20,gram_equalities=666,group_pair_choice_checks=pairs,lifted_column_pair_checks=9*pairs,actual_column_pairs_covered=1770,withintriplet_disjoint_pairs=60,forbidden_choice_pairs=forbidden,clause_sections=sections)

def controls(model,scope,data):
    result=local.controls(data);result['threshold_controls']=gates.controls();rejected=[]
    def reject(label,fn):
        try:fn()
        except(ValueError,KeyError,IndexError,TypeError):rejected.append(label)
        else:raise ValueError('corrupt branch accepted '+label)
    for name in ['core','L','parity','deleted_choice','wrong_selector','Boolean_selector','all_branches','unrestricted_support','balance','target_automorphism']:
        bad=deepcopy(scope)
        if name=='core':bad['core_adjacency'][0][1]^=1
        elif name=='L':bad['L'][0][0]^=1
        elif name=='parity':bad['domains'][0]['selected_parity_pattern'][1]^=1
        elif name=='deleted_choice':bad['domains'][0]['choices'].pop()
        elif name=='wrong_selector':bad['domains'][0]['choices'][0]['selector']+=1
        elif name=='Boolean_selector':bad['domains'][0]['choices'][0]['selector']=True
        elif name=='all_branches':bad['all_balanced_branches_covered']=True
        elif name=='unrestricted_support':bad['arbitrary_fixedL_factors_covered']=True
        elif name=='balance':bad['balanced_group_columns']=False
        else:bad['no_target_automorphism_assumed']=False
        reject(name,lambda bad=bad:scope_check(model,bad,data))
    ds=domains(data)
    for p,q in combinations(range(20),2):
        record,cs=cap_record(ds[p],ds[q],1)
        if cs:break
    blob=b''.join((' '.join(map(str,c))+' 0\n').encode()for c in cs)
    gates.ClauseCursor(io.BytesIO(blob),model['variables']).consume(cs)
    reject('missing_cap_clause',lambda:gates.ClauseCursor(io.BytesIO(blob.split(b'\n',1)[1]),model['variables']).consume(cs))
    badcs=[(-cs[0][0],cs[0][1]),*cs[1:]]
    badblob=b''.join((' '.join(map(str,c))+' 0\n').encode()for c in badcs)
    reject('wrong_cap_sign',lambda:gates.ClauseCursor(io.BytesIO(badblob),model['variables']).consume(cs))
    result['artifact_corruptions_rejected']=rejected
    return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--summary-sha256',required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();args.out=args.out.resolve();args.out.mkdir(parents=True,exist_ok=False);pins={};start=time.monotonic()
    def pin(p,h=None):
        value=digest(p);need(h is None or value==h,'input identity '+key(p));pins[key(p)]=value
    try:
        pin(D/'summary.json',args.summary_sha256);producer=read(D/'summary.json')
        for p,h in {**producer['inputs_sha256'],**producer['outputs_sha256']}.items():pin(ROOT/p,h)
        pin(local.GATE,local.GATE_SHA);pin(local.PROJECTION,local.PROJECTION_SHA);pin(local.RAW,local.RAW_SHA);pin(Path(gates.__file__),GATES_SHA)
        gate=read(local.GATE)
        for p,h in {**gate['inputs_sha256'],**gate['outputs_sha256']}.items():pin(ROOT/p,h)
        need(gate['inputs_sha256'][key(PRODUCER_PROJECTION)]==PRODUCER_PROJECTION_SHA,'independent parity gate binds producer projection')
        data=local.authenticated_reconstruct();model=read(D/'model.json');scope=read(D/'scope.json')
        save(args.out/'controls.json',controls(model,scope,data));save(args.out/'independent_domains.json',dict(domains=domains(data),local_triples=data['triples'],all_words=data['words'],one_fixed_parity_branch=True))
        counts=check_cnf(model,scope,data,D/'instance.cnf')
        for k,v in counts.items():need(same(producer[k],v),'producer population '+k)
        for p in [Path(__file__),Path(local.__file__),Path(local.support.__file__),ROOT/'docs/AUDIT_20260930_HADAMARD_PARITY_LIFT_CNF.md',ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(p)
        report=dict(status='INDEPENDENT_FIXED_PARITY_BALANCED_LIFT_CNF_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,outputs_sha256={key(p):digest(p)for p in args.out.iterdir()if p.is_file()},counts=counts,verifier='/root/state_literature_audit',method='Independent S3-array domain enumeration, literal set-intersection coefficients and complete truth-relation DIMACS reconstruction',artifact_availability='LOCAL_ONLY',producer_imports=False,shared_components=['Own frozen independent six-prism core/domain reconstruction.','Frozen independent prime-implicate prefix checker; standard library and tqdm.','No producer local-triple, encoder, decoder, LP or solver imports.'],limitations=['One selected authenticated parity branch of an additional balanced-triplet restriction on one exact support.','Other parity branches, other supports and arbitrary fixed-support factors are not covered.','No residual D or complete target graph.','This report audits the CNF, not the separately saved LP relaxation.','No genuine research factor is known; local and Boolean controls have narrower declared scope.'],elapsed_seconds=time.monotonic()-start,target_resolution=False,solver_calls=0,recommendation='VERIFIED')
        save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))
    except BaseException as e:save(args.out/'failure.json',dict(error=repr(e)));raise

if __name__=='__main__':main()
