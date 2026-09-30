"""Independent raw-cell reconstruction; no production encoder imports."""
from pathlib import Path
from itertools import combinations, product
from datetime import datetime, timezone
from copy import deepcopy
import argparse, ast, gzip, hashlib, json, platform, subprocess, sys, time, traceback
import audit_20260930_hadamard_balanced_gram_v2 as old

ROOT=Path(__file__).resolve().parents[1]; B=ROOT/'acceleration/results'
D=B/'20260930_direct_cell_count_cnf'; RAW=B/'20260930_hadamard20_support/six_prism.json'
MASTER=B/'20260930_hadamard_count_master_cnf'
FIXTURE=B/'20260930_srg243_residual_fixture/triangle_blocks.json'
PLAN=ROOT/'docs/AUDIT_20260930_DIRECT_CELL_COUNT_CNF.md'
CODEC=old.codec
PINS={RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',
 MASTER/'model.json':'a9a354e2fc28bff8a8f986d69f3cfd30fc06de0d76e394e125ffff884debdc44',
 MASTER/'at_least_seven.cnf':'f303edec9a91dc9bcecb95804ee151d0e38e8100b17c9c45a7b4d58b8edbf55e',
 B/'20260930_independent_review/hadamard_count_master_cnf_v2/summary.json':'80137a50c7097a0ebec1d958e5e48fd05364ea9b84cfd5793a705a07a10e1888',
 FIXTURE:'3f8dfa3803d6a5db8146dd24a0857477e1aa061ab10dac0f9e6e564aabc86439',
 Path(old.__file__):'cfddc6521887d6d44904ee7f2b92b0f189cfe5675b4f8d12d6df96ffe830e35c',
 Path(CODEC.__file__):'f572c91dc43f7208d34976b165c621c1b314e6963e437eaa475520ae1eb0add3'}
PINS.update({ROOT/'acceleration/theory_20260930_direct_cell_count_cnf.py':'ea7a07b7adcea4d5faebd174d3b3755ae8ed7e05d2fa844f135db39c7e075fc3',ROOT/'acceleration/theory_20260930_direct_cell_count_cnf_spec.md':'294a25a5734d7283761fba9b10d65c9533c49417b1c12e77486f6d2559787c2a',D/'summary.json':'4153f081634db52c88cf03421cae38b9919d0b6435e7836a8df8b8c5b77d1aa2',D/'standalone/instance.cnf':'45bac5dddcc805010dd4da150cc1c4613855b5d0e1e436f7b584067875c85250',D/'standalone/model.json':'c74a90c4e81218d98623fa7fa683a5680c67e3b82f2e33fefc453c705c411b87',D/'standalone/scope.json':'aa7f0e9ce4cd1679a1acc0aff0a8a76bbf60d2834013e419289be82ce8331e1e',D/'at_least_seven/instance.cnf':'07323c9fbbd75e328dfa0d1a99c760823799ecf7bba74722e2720d7dbb97c959',D/'at_least_seven/model.json':'ea45aa8045ac7193e9492daae383d599cccdfcf0741d3a9357984dcadd5e0cbb',D/'at_least_seven/scope.json':'8455669b3eec2edecd3e37bf7accebca75d8a65798b08a35f07fabb24edd96bf'})
STATUSES={'audit':'INDEPENDENT_DIRECT_CELL_ALL_CAPS_ENCODING_PASS','calibrate':'INDEPENDENT_DIRECT_CELL_ALL_CAPS_OBJECT_CALIBRATION_PASS','sat':'INDEPENDENT_DIRECT_CELL_ALL_CAPS_SAT_OBJECT_PASS'}
def need(ok,s):
    if not ok:raise ValueError(s)
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(Path(p).read_bytes())
def save(p,v):
    with Path(p).open('x',encoding='utf8',newline='\n')as f:json.dump(v,f,indent=2);f.write('\n')
def closure(path):
    seen=set()
    def walk(p):
        p=p.resolve()
        if p in seen:return
        seen.add(p)
        for node in ast.walk(ast.parse(p.read_text(encoding='utf8'))):
            names=[n.name for n in node.names]if isinstance(node,ast.Import)else [node.module]if isinstance(node,ast.ImportFrom)and node.module else []
            for name in names:
                q=ROOT/'acceleration'/(name.split('.')[0]+'.py')
                if q.is_file():walk(q)
    walk(path);return seen
def exact(xs,k):
    return [[-v for v in row]for row in combinations(xs,k+1)]+[list(row)for row in combinations(xs,len(xs)-k+1)]
def relation(z,q,x,r):
    ids=sorted({v for v in(z,q,x,r)if type(v)is int});clauses=[]
    for values in product((False,True),repeat=len(ids)):
        a=dict(zip(ids,values));get=lambda v:v if type(v)is bool else a[v]
        if a[z]!=(get(q)or(get(x)and get(r))):clauses.append([-v if a[v]else v for v in ids])
    return clauses
def truth(cs,v):return all(any(v[abs(x)]==(x>0)for x in c)for c in cs)

def derive(raw,variant):
    L=raw['L'];C=[[int((i%12==j%12 and i//12!=j//12)or(i//12==j//12 and i%12^1==j%12))for j in range(36)]for i in range(36)]
    K=[[12*(i==j)-C[i][j]-sum(C[i][k]*C[k][j]for k in range(36))+2-int(i//12==j//12)for j in range(36)]for i in range(36)]
    need(raw['core_adjacency']==C and raw['prescribed_Gram36']==K,'raw core and integer Gram derivation')
    need(len(L)==12 and all(len(r)==60 and all(type(v)is int and v in(0,1)for v in r)for r in L),'binary literal support')
    cols=[[a for a in range(12)if L[a][d]]for d in range(60)];need(cols==raw['support_columns'],'raw support transpose')
    groups=list(map(list,dict.fromkeys(map(tuple,cols))));gc=[[d for d in range(60)if cols[d]==s]for s in groups]
    need(len(groups)==20 and all(len(s)==6 and len(ds)==3 and all(sum(a in s for a in(m,m+1))==1 for m in range(0,12,2))for s,ds in zip(groups,gc)),'literal support geometry')
    master=read(MASTER/'model.json');base=None if variant=='standalone'else master['variants']['at_least_seven']
    top=0 if base is None else base['variables'];clauses=[];sections={};cells=[];x={};links=[];rowcounters=[];products=[];gram=[];caps=[]
    def alloc():
        nonlocal top
        top+=1;return top
    def begin(name):sections[name]=dict(variables_before=top,first=len(clauses))
    def end(name):
        s=sections[name];cs=clauses[s.pop('first'):];s.update(variables_after=top,clauses=len(cs),literals=sum(map(len,cs)),negative_literals=sum(v<0 for c in cs for v in c),ascii_body_bytes=sum(len(line(c))for c in cs),max_clause_literals=max(map(len,cs),default=0))
    begin('primary_cells')
    for g,s in enumerate(groups):
        for d,a,f in product(gc[g],s,range(3)):
            v=alloc();x[d,a,f]=v;cells.append([g,d,a,f,v])
    end('primary_cells');begin('one_fibre_per_coordinate')
    for d,s in enumerate(cols):
        for a in s:clauses.extend(exact([x[d,a,f]for f in range(3)],1))
    end('one_fibre_per_coordinate');begin('two_per_fibre_per_column')
    for d,s in enumerate(cols):
        for f in range(3):clauses.extend(exact([x[d,a,f]for a in s],2))
    end('two_per_fibre_per_column');section='explicit_row_counts'if base is None else 'row_counts_via_master';begin(section)
    if base is None:
        for a,f in product(range(12),range(3)):
            xs=[x[d,a,f]for d in range(60)if a in cols[d]];states=[];ids={};need(len(xs)==30,'row domain')
            for i,v in enumerate(xs,1):
                for j in range(1,min(i,11)+1):
                    z=alloc();q=ids.get((i-1,j),False);r=True if j==1 else ids.get((i-1,j-1),False)
                    clauses.extend(relation(z,q,v,r));ids[i,j]=z;states.append(dict(i=i,j=j,id=z,q=q,x=v,r=r))
            clauses.extend([[ids[30,10]],[-ids[30,11]]]);rowcounters.append(dict(coordinate=a,fibre=f,inputs=xs,states=states))
    else:
        need(master['groups']==groups,'verified master groups')
        for domain in master['coordinate_domains']:
            for table in domain['count_tables']:need(all(sum(row[f]for row in table)==10 for f in range(3)),'all master coordinate rows10')
        for c in master['count_channels']:
            g,a=c['group'],c['coordinate']
            for values,selector in zip(c['values'],c['variables']):
                for f,k in enumerate(values):
                    xs=[x[d,a,f]for d in gc[g]]
                    for bits in product((False,True),repeat=3):
                        if sum(bits)!=k:clauses.append([-selector,*[-v if b else v for v,b in zip(xs,bits)]])
                    links.append(dict(group=g,coordinate=a,fibre=f,selector=selector,value=k,inputs=xs))
    end(section);begin('full_Gram_products_and_counts')
    for a,b in combinations(range(12),2):
        if a^1==b:continue
        ds=[d for g,s in enumerate(groups)if a in s and b in s for d in gc[g]];need(len(ds)==15,'Gram term population')
        for f,h in product(range(3),repeat=2):
            qs=[]
            for d in ds:
                u,v=x[d,a,f],x[d,b,h];z=alloc();clauses.extend([[-u,-v,z],[u,-z],[v,-z]]);products.append([u,v,z]);qs.append(z)
            target=K[12*f+a][12*h+b];need(target==(1 if f==h else 2),'Gram target');clauses.extend(exact(qs,target));gram.append(dict(coordinates=[a,b],fibres=[f,h],target=target,products=qs))
    end('full_Gram_products_and_counts')
    within=[(d,e)for ds in gc for d,e in combinations(ds,2)]
    for section,pairs in [('within_group_column_caps',within),('optional_cross_group_column_caps',[p for p in combinations(range(60),2)if p not in set(within)])]:
        begin(section)
        for d,e in pairs:
            common=sorted(set(cols[d])&set(cols[e]));es=[]
            if len(common)>2:
                for a in common:
                    z=alloc();es.append(z)
                    clauses.extend([[-x[d,a,f],-x[e,a,f],z]for f in range(3)]+[[-x[d,a,f],x[e,a,f],-z]for f in range(3)])
                clauses.extend([[-v for v in q]for q in combinations(es,3)])
            caps.append(dict(columns=[d,e],kind='within'if section.startswith('within')else 'cross',common_coordinates=common,equality_flags=es,automatic=len(common)<=2))
        end(section)
    need(len(cells)==1080 and len(products)==8100 and len(gram)==540 and len(caps)==1770,'complete finite populations')
    recipe=dict(variant=variant,base=base,groups=groups,group_columns=gc,cell_variables=cells,count_links=links,standalone_row_counters=rowcounters,Gram_products=products,Gram_rows=gram,column_caps=caps,sections=sections)
    return recipe,clauses,top,dict(C=C,K=K,L=L,cols=cols,groups=groups,gc=gc)

def line(c):return ((' '.join(map(str,c))+' 0\n')if c else '0\n').encode('ascii')
def raw_object(F,geometry):
    need(len(F)==36 and all(len(r)==60 and all(type(v)is int and v in(0,1)for v in r)for r in F),'complete strict binary36x60')
    rows=[sum(v<<d for d,v in enumerate(r))for r in F]
    need([[int((u&v).bit_count())for v in rows]for u in rows]==geometry['K'],'1296 exact Gram entries')
    need([[sum(F[12*f+a][d]for f in range(3))for d in range(60)]for a in range(12)]==geometry['L'],'literal support')
    need(all(sum(F[12*f+a][d]for a in range(12))==2 for f in range(3)for d in range(60)),'all180 fibre margins')
    colbits=[sum(F[r][d]<<r for r in range(36))for d in range(60)]
    need(all((colbits[d]&colbits[e]).bit_count()<=2 for d,e in combinations(range(60),2)),'all1770 overlap caps')
    need(all(F[i][d]+sum(geometry['C'][i][j]*F[j][d]for j in range(36))<=2 for i in range(36)for d in range(60)),'all2160 mixed caps')
    tables=[[[sum(F[12*f+a][d]for d in ds)for f in range(3)]for a in s]for s,ds in zip(geometry['groups'],geometry['gc'])]
    return dict(factor=F,exception_count=sum(any(row!=[1,1,1]for row in t)for t in tables),count_tables=tables,Gram_entries_checked=1296,column_caps_checked=1770,mixed_caps_checked=2160,full_target=False,residual_D=None)

def check_formula(variant,pin):
    folder=D/variant;model=read(folder/'model.json');scope=read(folder/'scope.json');summary=read(folder/'summary.json')
    for p in [folder/'model.json',folder/'scope.json',folder/'instance.cnf',folder/'summary.json']:pin(p)
    for doc in [model,summary]:
        for field in ['inputs_sha256','outputs_sha256']:
            for p,h in doc.get(field,{}).items():pin(ROOT/p,h)
    recipe,cs,n,geometry=derive(read(RAW),variant)
    for k,v in recipe.items():need(model['recipe'][k]==v,'independent recipe '+variant+' '+k)
    need(scope['core_adjacency36']==geometry['C']and scope['prescribed_Gram36']==geometry['K']and scope['L12x60']==geometry['L'],'literal scope matrices')
    need(scope['groups']==geometry['groups']and scope['group_columns']==geometry['gc']and scope['support_columns']==geometry['cols'],'literal scope sets')
    for field in ['full_Gram_encoded','within_group_caps_encoded','cross_group_caps_encoded']:need(scope[field]is True,'complete raw constraints '+field)
    for field in ['residual_D_encoded','target_automorphism_assumed','target_graph']:need(scope[field]is False,'scope omission '+field)
    need(scope['column_normalization']is None and scope['column_normalization_null_reason']=='All original labelled outside columns retained.','no column normalization')
    need(scope['count_master_included']==(variant!='standalone')and scope['minimum_exception_count']==(None if variant=='standalone'else 7),'exact variant restriction')
    need(scope['row_sum']==10 and scope['column_fibre_sum']==2 and scope['raw_support_path']==key(RAW)and scope['raw_support_sha256']==PINS[RAW],'scope margins and immutable support')
    expected=(23112,320484)if variant=='standalone'else(169151,968960);m=len(cs)+(0 if recipe['base']is None else recipe['base']['clauses'])
    need((n,m)==expected and model['variables']==n and model['clauses']==m,'exact complete header')
    cnf=folder/'instance.cnf'
    with cnf.open('rb')as actual:
        need(actual.readline()==f'p cnf {n} {m}\n'.encode(),'header bytes')
        if recipe['base']is not None:
            with (MASTER/'at_least_seven.cnf').open('rb')as prefix:
                need(prefix.readline()==b'p cnf 155939 705833\n','base header')
                for row in prefix:need(actual.readline()==row,'all verified prefix bytes')
        for c in cs:need(actual.readline()==line(c),'every appended clause byte')
        need(actual.read()==b'','no extra formula bytes')
    need(model['cnf_sha256']==sha(cnf)and model['scope_sha256']==sha(folder/'scope.json'),'model artifact bindings')
    ranges={};cursor=0
    if recipe['base']:cursor=recipe['base']['clauses'];ranges['count_master_prefix']=dict(first_clause=1,clause_count=cursor,last_clause=cursor)
    for name,section in recipe['sections'].items():ranges[name]=dict(first_clause=cursor+1,clause_count=section['clauses'],last_clause=cursor+section['clauses'],variables_before=section['variables_before'],variables_after=section['variables_after']);cursor+=section['clauses']
    need(cursor==m and model['clause_sections']==ranges,'all saved clause boundaries')
    return dict(variant=variant,variables=n,clauses=m,cnf_sha256=sha(cnf),scope=scope,model=model,recipe=recipe,geometry=geometry,clauses_list=cs)

def controls(records,out):
    rejected=[];cases=0
    def reject(name,fn):
        try:fn()
        except(ValueError,KeyError,TypeError):rejected.append(name)
        else:raise ValueError('accepted corruption '+name)
    for n,k in [(3,1),(6,2),(15,1),(15,2)]:
        cs=exact(list(range(1,n+1)),k)
        for bits in product((False,True),repeat=n):need(truth(cs,dict(enumerate(bits,1)))==(sum(bits)==k),'all cardinality truth assignments');cases+=1
    recurrence=0
    for q in(False,1):
        for r in(False,True,2):
            for bits in product((False,True),repeat=4):
                v=dict(enumerate(bits,1));get=lambda x:x if type(x)is bool else v[x]
                need(truth(relation(4,q,3,r),v)==(v[4]==(get(q)or(get(3)and get(r)))),'threshold recurrence all auxiliary truth');recurrence+=1
    flag_cases=0
    for f,g,z in product(range(3),range(3),(False,True)):
        v={**{i+1:i==f for i in range(3)},**{i+4:i==g for i in range(3)},7:z};cs=[[-i-1,-i-4,7]for i in range(3)]+[[-i-1,i+4,-7]for i in range(3)]
        need(truth(cs,v)==(z==(f==g)),'onehot equality truth');flag_cases+=1
    and_cases=count_cases=0
    for bits in product((False,True),repeat=3):need(truth([[-1,-2,3],[1,-3],[2,-3]],dict(enumerate(bits,1)))==(bits[2]==(bits[0]and bits[1])),'AND equivalence truth');and_cases+=1
    for k in range(4):
        cs=[[-4,*[-i if b else i for i,b in enumerate(bits,1)]]for bits in product((False,True),repeat=3)if sum(bits)!=k]
        for bits in product((False,True),repeat=4):need(truth(cs,dict(enumerate(bits,1)))==(not bits[3]or sum(bits[:3])==k),'conditional count truth including false antecedent');count_cases+=1
    fixture=read(FIXTURE);old.raw_factor(fixture['factor60x180'],fixture['cubic_core60'],20)
    for name in ['bit','bool','width','nonbinary']:
        f=deepcopy(fixture['factor60x180'])
        if name=='bit':f[0][0]^=1
        elif name=='bool':f[0][0]=bool(f[0][0])
        elif name=='width':f[0].pop()
        else:f[0][0]=2
        reject('fixture_'+name,lambda f=f:old.raw_factor(f,fixture['cubic_core60'],20))
    for rec in records:
        name=rec['variant'];r=rec['recipe'];n=rec['variables'];m=rec['clauses'];selected={v for g,d,a,f,v in r['cell_variables']if f==a//2%3}
        # Complete local one-hot/fibre positives are not claimed as global factors.
        F=[[0]*60 for _ in range(36)]
        for g,d,a,f,v in r['cell_variables']:F[12*f+a][d]=int(v in selected)
        need(all(sum(F[12*f+a][d]for f in range(3))==rec['geometry']['L'][a][d]for a in range(12)for d in range(60)),'known local support positive')
        need(all(sum(F[12*f+a][d]for a in range(12))==2 for f in range(3)for d in range(60)),'known local fibre positive')
        reject(name+'_local_not_global',lambda:raw_object(F,rec['geometry']))
        vals=[i if i%2 else -i for i in range(1,n+1)];assignment=CODEC.assignment(vals,n)
        text='c SYNTHETIC CODEC ONLY\ns SATISFIABLE\n'+'\n'.join('v '+' '.join(map(str,vals[j:j+113]))for j in range(0,n,113))+' 0\n'
        need(CODEC.native(text,n)==assignment,'complete signed native codec')
        reject(name+'_missing_variable',lambda:CODEC.assignment(vals[:-1],n));reject(name+'_bool_variable',lambda:CODEC.assignment([True,*vals[1:]],n))
        reject(name+'_wrong_native_status',lambda:CODEC.native(text.replace('s SATISFIABLE','s UNSATISFIABLE'),n))
        reject(name+'_out_of_range',lambda:CODEC.assignment([n+1,*vals[1:]],n))
        synthetic=[[vals[i%n]]for i in range(m)];CODEC.all_clauses(synthetic,assignment);synthetic[-1][0]*=-1;reject(name+'_false_final_clause',lambda:CODEC.all_clauses(synthetic,assignment))
        save(out/(name+'_synthetic_codec.json'),dict(variables=n,clauses=m,scope='synthetic codec positive only; not a factor',assignment_sha256=hashlib.sha256(json.dumps(vals).encode()).hexdigest()))
    return dict(cardinality_truth_assignments=cases,threshold_truth_assignments=recurrence,AND_truth_assignments=and_cases,conditional_count_truth_assignments=count_cases,onehot_equality_truth_assignments=flag_cases,known_positive='Independent generic raw-factor validator on genuine243 residual fixture; complete local support/fibre and synthetic assignment positives.',corruptions_rejected=rejected,fixed_support_full_Gram_positive=None,fixed_support_full_Gram_positive_null_reason='No such factor is known; no claim of calibrated genuine fixed-support SAT.')

def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=STATUSES);p.add_argument('--out',type=Path,required=True)
    for name in ['encoding-gate','native-driver','native-spec','assignment','native-output','decoded']:p.add_argument('--'+name,type=Path)
    for name in ['encoding-gate-sha256','native-driver-sha256','native-spec-sha256']:p.add_argument('--'+name)
    p.add_argument('--variant',choices=['standalone','at_least_seven']);args=p.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};start=time.monotonic()
    def pin(path,h=None):
        value=sha(path);need(h is None or value==h,'pinned input '+key(path));pins[key(path)]=value
    try:
        for path,h in PINS.items():pin(path,h)
        for path in closure(Path(__file__))|{PLAN,ROOT/'uv.lock',ROOT/'pyproject.toml'}:pin(path)
        need(all(not q.name.startswith(('theory_','native_'))for q in closure(Path(__file__))),'no producer imports')
        records=[check_formula(v,pin)for v in ['standalone','at_least_seven']]
        if args.mode!='audit':
            need(args.encoding_gate and args.encoding_gate_sha256,'explicit encoding gate');pin(args.encoding_gate,args.encoding_gate_sha256);eg=read(args.encoding_gate);need(eg['status']==STATUSES['audit'],'approved same encoding')
            for path,h in eg['inputs_sha256'].items():pin(ROOT/path,h)
        if args.mode=='calibrate':
            need(args.native_driver and args.native_spec and args.native_driver_sha256 and args.native_spec_sha256,'frozen driver/spec');pin(args.native_driver,args.native_driver_sha256);pin(args.native_spec,args.native_spec_sha256)
            for path in closure(args.native_driver):pin(path)
        if args.mode in('audit','calibrate'):control=controls(records,out);save(out/'controls.json',control)
        else:
            need(args.variant and args.assignment and args.native_output,'complete raw SAT inputs');rec=next(r for r in records if r['variant']==args.variant);n=rec['variables']
            pin(args.assignment);pin(args.native_output);vals=CODEC.assignment(read(args.assignment)['assignment'],n);need(vals==CODEC.native(args.native_output.read_text(),n),'all native/JSON values')
            cs=[]
            with (D/args.variant/'instance.cnf').open('rt',encoding='ascii')as f:
                f.readline()
                for row in f:items=list(map(int,row.split()));need(items[-1]==0 and all(0<abs(v)<=n for v in items[:-1]),'literal clause codec');cs.append(items[:-1])
            CODEC.all_clauses(cs,vals);F=[[0]*60 for _ in range(36)]
            for g,d,a,h,v in rec['recipe']['cell_variables']:F[12*h+a][d]=int(vals[v])
            result=raw_object(F,rec['geometry']);need(args.variant=='standalone'or result['exception_count']>=7,'explicit >=7 scope')
            if args.decoded:pin(args.decoded);need(read(args.decoded)['factor']==F,'candidate decoded object equality')
            save(out/'independent_factor.json',result);control=None
        need(time.monotonic()-start<180,'180-second audit budget')
        compact=[{k:r[k]for k in ['variant','variables','clauses','cnf_sha256']}for r in records]
        save(out/'summary.json',dict(status=STATUSES[args.mode],timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,outputs_sha256={key(q):sha(q)for q in out.iterdir()if q.is_file()},formulas=compact,controls=control,elapsed_seconds=time.monotonic()-start,scope='One literal support. Complete raw full Gram plus all1770 column caps; >=7 count-coupled variant has its explicit count-master and lower-bound premises. No D or unrestricted target coverage.',shared_components=['Earlier independent native/JSON codecs and genuine243 raw-factor validator; no producer encoder imports.','Previously verified count-master byte prefix and necessary-projection coverage.'],solver_calls=0,target_resolution=False))
        print(json.dumps(dict(status=STATUSES[args.mode],summary_sha256=sha(out/'summary.json'))))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e),traceback=traceback.format_exc(),inputs_sha256=pins,source_sha256=sha(Path(__file__))));raise
if __name__=='__main__':main()
