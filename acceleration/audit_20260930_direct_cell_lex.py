"""Independent lex suffix, relabelling and raw-object audit; no producer imports."""
from pathlib import Path
from itertools import product, combinations
from collections import defaultdict
from datetime import datetime, timezone
from copy import deepcopy
import argparse, hashlib, json, platform, subprocess, sys, time, traceback
import audit_20260930_direct_cell_count_cnf as base

ROOT = Path(__file__).resolve().parents[1]
B = ROOT / 'acceleration/results'
D = B / '20260930_direct_cell_lex'
PLAN = ROOT / 'docs/AUDIT_20260930_DIRECT_CELL_LEX.md'
STATUS = dict(audit='INDEPENDENT_DIRECT_CELL_LEX_ENCODING_PASS', calibrate='INDEPENDENT_DIRECT_CELL_LEX_OBJECT_CALIBRATION_PASS', sat='INDEPENDENT_DIRECT_CELL_LEX_SAT_OBJECT_PASS')
PINS = {
    Path(base.__file__): '97ed802d67b4583d29191fbc17153d3996dcf15fa07b1f63340441666379f2e8',
    D/'summary.json': '2077b3a005191d9c3a777c0e16b79e273f18b0aab60737dd880e199a833a1f22',
    ROOT/'acceleration/theory_20260930_direct_cell_lex.py': '56ee886ade80403743fd260d8b2ef9c227d9d1e2741c3edbb09b509fac9ade57',
    ROOT/'acceleration/theory_20260930_direct_cell_lex_spec.md': '1fe7cb6e2517e274c90ff9d4a64ed751be6340ae49da41ed9215762573c6cc1b',
    ROOT/'docs/DERIVATION_20260930_DIRECT_CELL_LEX.md': '71477332940078ed492017febee58442ba2ed8dde72958eec844482e7f742909',
    B/'20260930_independent_review/direct_cell_count_cnf/summary.json': 'a7fd5968681257c60a0e82a36b53f40798487d727f2f467dae47918becf84042',
    B/'20260930_independent_review/direct_cell_semantics/summary.json': '88d6e8134c34b61d44a29e0bc525aebfb260f3f71c78efa72b98a7049275fdc8'}
EXPECTED = {'standalone': (23272,321684,'c1bb9e7a14008b40ce4e93eee3b222bd78599d450fc25ab1852b80bb1b825bfa','e40cbc3d7497339b9c063e0566909e3b7702d41b4201584756b71c2b210d14b6','026c040815d590bbdc37adedfa3a4e2808aeab09ecd01972b0a888f7c57b1724'),
 'at_least_seven': (169311,970160,'b536d8461be954bb76a4f25087fa450527edc90904f4c26c3bfe8dbcc4f79649','973f86db6f026c8db9d81ef74f59d94679c4523cfadbee732fd8d0b38a3af51b','43a35fe406cf6951d9af7f937a94261cd08171d037681fef70195aa75aa65e43')}


def need(value, message):
    if not value: raise ValueError(message)


def sha(path):
    with Path(path).open('rb') as stream: return hashlib.file_digest(stream,'sha256').hexdigest()


def read(path): return json.loads(Path(path).read_bytes())
def key(path): return Path(path).resolve().relative_to(ROOT).as_posix()
def save(path,obj):
    with Path(path).open('x',encoding='utf8',newline='\n') as stream: json.dump(obj,stream,indent=2);stream.write('\n')
def truth(clauses,values): return all(any(values[abs(v)] == (v>0) for v in row) for row in clauses)


def own_comparator(left,right,eq,top):
    clauses=[];prefixes=[];guards=[None,eq[0]]
    for position in range(2,6):
        z=top+1;top=z;u=guards[-1];v=eq[position-1]
        # Independently fixed exact AND prime implications, truth checked below.
        rows=[[-u,-v,z],[u,-z],[v,-z]]
        prefixes.append(dict(position=position,id=z,left=u,right=v,clauses=rows));clauses+=rows;guards.append(z)
    inversions=[]
    for position in range(6):
        for f in range(3):
            for h in range(f):
                row=([-guards[position]] if position else [])+[-left[position][f],-right[position][h]]
                clauses.append(row);inversions.append(dict(position=position,left_fibre=f,right_fibre=h,guard=guards[position],clause=row))
    return clauses,dict(left_cells=left,right_cells=right,equality_flags=eq,prefixes=prefixes,inversions=inversions),top


def derive_extension(rec):
    geometry,recipe=rec['geometry'],rec['recipe'];top=rec['variables'];records=[];clauses=[]
    cells={(d,a,f):v for g,d,a,f,v in recipe['cell_variables']}
    caps={tuple(c['columns']):c for c in recipe['column_caps']}
    for g,(support,columns) in enumerate(zip(geometry['groups'],geometry['gc'],strict=True)):
        need(support==sorted(support) and len(support)==6 and columns==sorted(columns) and len(columns)==3,'raw sorted equal-support triplicate')
        for adjacent,(d,e) in enumerate(zip(columns,columns[1:])):
            cap=caps[d,e];need(cap['kind']=='within' and cap['common_coordinates']==support and len(cap['equality_flags'])==6,'independently reconstructed base exact equality channels')
            left=[[cells[d,a,f] for f in range(3)] for a in support];right=[[cells[e,a,f] for f in range(3)] for a in support]
            cs,meta,top=own_comparator(left,right,cap['equality_flags'],top)
            records.append(dict(group=g,adjacent=adjacent,columns=[d,e],support=support,first_clause=rec['clauses']+len(clauses)+1,clause_count=len(cs),**meta));clauses+=cs
    need(len(records)==40 and len(clauses)==1200 and top==rec['variables']+160,'complete lex inventory')
    return records,clauses,top


def expected_scope(rec):
    s=deepcopy(rec['scope']);variant=rec['variant'];folder=base.D/variant
    s.update(schema='FIXED_LITERAL_DIRECT_CELL_EQUAL_SUPPORT_LEX_SCOPE_V1',column_normalization='Weak lexicographic order on adjacent labelled columns in every equal-support triplicate; strictness follows existing caps.',column_normalization_null_reason=None,normalization_group='S3^20 acting within the fixed equal-support triples only',auxiliary_permutation_claimed=False,base_scope_path=key(folder/'scope.json'),base_scope_sha256=sha(folder/'scope.json'),candidate_only=True)
    return s


def validate_extension(rec,ext,scope):
    records,clauses,top=derive_extension(rec)
    need(ext['schema']=='DIRECT_CELL_EQUAL_SUPPORT_LEX_EXTENSION_V1' and ext['variant']==rec['variant'],'extension schema/variant')
    need(ext['new_variables']==160 and ext['new_clauses']==1200,'saved exact additions')
    need(ext['comparators']==records and ext['clauses']==clauses,'all literal maps, prefix IDs, boundaries and 1200 clauses')
    need(scope==expected_scope(rec),'scope equals old scope with only declared normalization changes')
    return records,clauses,top


def check_formula(variant,pin):
    rec=base.check_formula(variant,pin)
    folder=D/variant;n,m,cnfh,modelh,scopeh=EXPECTED[variant]
    for name,digest in [('instance.cnf',cnfh),('model.json',modelh),('scope.json',scopeh)]:pin(folder/name,digest)
    model,scope,ext=read(folder/'model.json'),read(folder/'scope.json'),read(folder/'extension.json')
    pin(folder/'extension.json');pin(folder/'summary.json')
    expected_base=next(r for r in read(base.D/'summary.json')['records'] if r['variant']==variant)
    need(model['schema']=='DIRECT_CELL_EQUAL_SUPPORT_LEX_REFERENCE_MODEL_V1' and model['variant']==variant,'new model schema')
    need(model['base']==ext['base']==expected_base,'entire frozen base reference metadata')
    records,cs,top=validate_extension(rec,ext,scope)
    need(top==n and rec['clauses']+len(cs)==m and (model['variables'],model['clauses'])==(n,m),'exact new dimensions')
    for name in ('scope','cnf','extension'):
        path=folder/('instance.cnf' if name=='cnf' else name+'.json')
        need(model[name+'_path']==key(path) and model[name+'_sha256']==sha(path),'new model raw '+name+' binding')
    body=hashlib.sha256();cnf=folder/'instance.cnf'
    suffix=b''.join(base.line(c) for c in cs)
    need(ext['suffix_path']==key(folder/'lex.units_and_clauses.cnfpart'),'declared suffix path');pin(ROOT/ext['suffix_path'],ext['suffix_sha256'])
    need((ROOT/ext['suffix_path']).read_bytes()==suffix,'exact standalone suffix bytes')
    with cnf.open('rb') as actual,(base.D/variant/'instance.cnf').open('rb') as original:
        need(actual.readline()==f'p cnf {n} {m}\n'.encode(),'new header')
        need(original.readline()==f"p cnf {rec['variables']} {rec['clauses']}\n".encode(),'base header')
        for block in iter(lambda:original.read(1024**2),b''):
            need(actual.read(len(block))==block,'every original body byte retained');body.update(block)
        need(actual.read()==suffix,'all1200 suffix clauses and no trailing data')
    need(ext['base_body_sha256']==body.hexdigest(),'saved base-body digest')
    return dict(variant=variant,variables=n,clauses=m,model=model,scope=scope,extension=ext,base=rec,comparators=records,suffix=cs,cnf_sha256=cnfh)


def strict_words(F,n,groups,columns):
    result=[]
    for support,ds in zip(groups,columns,strict=True):
        words=[]
        for d in ds:
            word=[]
            for a in support:
                selected=[f for f in range(3) if F[n*f+a][d]==1]
                need(len(selected)==1,'exactly one raw fibre at supported coordinate');word.append(selected[0])
            words.append(tuple(word))
        need(all(words[i]<words[i+1] for i in range(len(words)-1)),'raw strict adjacent lex order')
        result.append([list(w) for w in words])
    return result


def fixture_transport(out):
    fixture=read(base.FIXTURE);F=fixture['factor60x180'];C=fixture['cubic_core60'];D0=fixture['residual180x180'];n=20;m=180
    positive=base.old.raw_factor(F,C,n);need(not positive['column_cap_violations'] and not positive['mixed_cap_violations'],'genuine243 caps positive')
    supports=[tuple(a for a in range(n) if positive['coordinate_support'][a][d]) for d in range(m)]
    grouped=defaultdict(list)
    for d,s in enumerate(supports):grouped[s].append(d)
    need(len(grouped)==60 and all(len(s)==6 and len(ds)==3 for s,ds in grouped.items()),'genuine243 triplicates')
    groups=list(grouped);columns=[grouped[s] for s in groups]
    perm=list(range(m))
    for support,ds in zip(groups,columns):
        order=sorted(ds,key=lambda d:tuple(next(f for f in range(3) if F[n*f+a][d]) for a in support))
        for new,old in zip(ds,order):perm[new]=old
    need(sorted(perm)==list(range(m)),'sorting is a column bijection')
    Fn=[[row[perm[d]] for d in range(m)] for row in F];Dn=[[D0[perm[d]][perm[e]] for e in range(m)] for d in range(m)]
    after=base.old.raw_factor(Fn,C,n);need(after['coordinate_support']==positive['coordinate_support'] and not after['column_cap_violations'] and not after['mixed_cap_violations'],'sorted genuine support/caps')
    ordered=strict_words(Fn,n,groups,columns)
    for a,f,ds in product(range(n),range(3),columns):need(sum(F[n*f+a][d] for d in ds)==sum(Fn[n*f+a][d] for d in ds),'all count-master table values invariant')
    inverse=[perm.index(d) for d in range(m)]
    need([[row[inverse[d]] for d in range(m)] for row in Fn]==F and [[Dn[inverse[d]][inverse[e]] for e in range(m)] for d in range(m)]==D0,'literal factor/residual inverse')
    rows=[sum(v<<d for d,v in enumerate(row)) for row in Fn];dr=[sum(v<<d for d,v in enumerate(row)) for row in Dn];cols=[sum(Fn[i][d]<<i for i in range(3*n)) for d in range(m)]
    need(all(len(r)==m and all(type(x)is int and x in(0,1) for x in r) for r in Dn),'binary residual')
    need(all(Dn[d][d]==0 and sum(Dn[d])==16 and all(Dn[d][e]==Dn[e][d] for e in range(m)) for d in range(m)),'simple regular residual')
    for i,d in product(range(3*n),range(m)):need((rows[i]&dr[d]).bit_count()==2-Fn[i][d]-sum(C[i][j]*Fn[j][d] for j in range(3*n)),'genuine sorted FD equation')
    for d,e in product(range(m),repeat=2):need((dr[d]&dr[e]).bit_count()+(cols[d]&cols[e]).bit_count()==20*(d==e)-Dn[d][e]+2,'genuine sorted residual square')
    save(out/'genuine243_transport.json',dict(sigma_new_to_old=perm,inverse=inverse,groups=[list(g) for g in groups],group_columns=columns,sorted_words=ordered,scope='Genuine243 control only; not research factor.',factor=Fn,residual=Dn))
    return Fn,groups,columns


def controls(records,out):
    left=[[1+3*a+f for f in range(3)] for a in range(6)];right=[[19+3*a+f for f in range(3)] for a in range(6)];eq=list(range(37,43));cs,meta,top=own_comparator(left,right,eq,42)
    need(top==46 and len(cs)==30,'one comparator size')
    words=[w for w in product(range(3),repeat=6) if all(w.count(f)==2 for f in range(3))]
    accepted=0;cases=0
    for x,y in product(words,repeat=2):
        values={left[a][f]:x[a]==f for a in range(6) for f in range(3)};values.update({right[a][f]:y[a]==f for a in range(6) for f in range(3)});values.update({eq[a]:x[a]==y[a] for a in range(6)})
        satisfying=0
        for bits in product((False,True),repeat=4):
            values.update(dict(zip(range(43,47),bits)));satisfying+=truth(cs,values);cases+=1
        need(satisfying==int(x<=y),'all auxiliary assignments exactly implement word lex order');accepted+=satisfying
    for bits in product((False,True),repeat=3):need(truth([[-1,-2,3],[1,-3],[2,-3]],dict(enumerate(bits,1)))==(bits[2]==(bits[0] and bits[1])),'all exact AND cases')
    rejected=[]
    def reject(name,fn):
        try:fn()
        except(ValueError,KeyError,TypeError,IndexError):rejected.append(name)
        else:raise ValueError('corruption accepted '+name)
    for rec in records:
        for kind in ('prefix_id','equality_flag','column_map','suffix_literal','missing_clause','duplicate_comparator','scope_D','scope_count'):
            ext=deepcopy(rec['extension']);scope=deepcopy(rec['scope'])
            if kind=='prefix_id':ext['comparators'][0]['prefixes'][0]['id']+=1
            elif kind=='equality_flag':ext['comparators'][0]['equality_flags'][0]+=1
            elif kind=='column_map':ext['comparators'][0]['columns'].reverse()
            elif kind=='suffix_literal':ext['clauses'][-1][-1]*=-1
            elif kind=='missing_clause':ext['clauses'].pop()
            elif kind=='duplicate_comparator':ext['comparators'][1]=ext['comparators'][0]
            elif kind=='scope_D':scope['residual_D_encoded']=True
            elif kind=='scope_count':scope['minimum_exception_count']=8
            reject(rec['variant']+'_'+kind,lambda ext=ext,scope=scope,rec=rec:validate_extension(rec['base'],ext,scope))
        n,m=rec['variables'],rec['clauses'];vals=[i if i%2 else -i for i in range(1,n+1)];v=base.CODEC.assignment(vals,n)
        text='c SYNTHETIC CODEC ONLY\ns SATISFIABLE\n'+'\n'.join('v '+' '.join(map(str,vals[j:j+113])) for j in range(0,n,113))+' 0\n'
        need(base.CODEC.native(text,n)==v,'full larger native/JSON codec')
        reject(rec['variant']+'_missing_assignment',lambda:base.CODEC.assignment(vals[:-1],n))
        reject(rec['variant']+'_bool_literal',lambda:base.CODEC.assignment([True,*vals[1:]],n))
        reject(rec['variant']+'_duplicate_literal',lambda:base.CODEC.assignment([vals[1],*vals[1:]],n))
        reject(rec['variant']+'_native_unsat',lambda:base.CODEC.native(text.replace('s SATISFIABLE','s UNSATISFIABLE'),n))
        reject(rec['variant']+'_missing_native_literal',lambda:base.CODEC.native(text.replace('v 1 ','v ',1),n))
        fake=[[vals[i%n]] for i in range(m)];base.CODEC.all_clauses(fake,v);fake[-1][0]*=-1
        reject(rec['variant']+'_last_false_clause',lambda:base.CODEC.all_clauses(fake,v))
        save(out/(rec['variant']+'_synthetic_codec.json'),dict(variables=n,clauses=m,assignment_sha256=hashlib.sha256(json.dumps(vals).encode()).hexdigest(),scope='Full-size synthetic codec only, not actual-CNF satisfiability.'))
    F,groups,columns=fixture_transport(out)
    wrong=deepcopy(F);a,b=columns[0][:2]
    for row in wrong:row[a],row[b]=row[b],row[a]
    reject('descending_raw_factor',lambda:strict_words(wrong,20,groups,columns))
    wrong=deepcopy(F)
    for row in wrong:row[b]=row[a]
    reject('equal_raw_words',lambda:strict_words(wrong,20,groups,columns))
    C=read(base.FIXTURE)['cubic_core60']
    for kind in ('bit','bool','width','nonbinary'):
        bad=deepcopy(F)
        if kind=='bit':bad[0][0]^=1
        elif kind=='bool':bad[0][0]=bool(bad[0][0])
        elif kind=='width':bad[0].pop()
        else:bad[0][0]=2
        reject('genuine243_'+kind,lambda bad=bad:base.old.raw_factor(bad,C,20))
    return dict(balanced_words=90,ordered_pairs=8100,complete_auxiliary_assignments=cases,unique_allowed_extensions=accepted,AND_truth_cases=8,corruptions_rejected=rejected,genuine243_positive=True,full_size_synthetic_codecs=True,research_factor_available=False)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=STATUS);parser.add_argument('--out',type=Path,required=True)
    for name in ('encoding-gate','native-driver','native-spec','assignment','native-output','decoded'):parser.add_argument('--'+name,type=Path)
    for name in ('encoding-gate-sha256','native-driver-sha256','native-spec-sha256'):parser.add_argument('--'+name)
    parser.add_argument('--variant',choices=tuple(EXPECTED));args=parser.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};start=time.monotonic()
    def pin(path,expected=None):
        name=key(path)
        if name not in pins:pins[name]=sha(path)
        need(expected is None or pins[name]==expected,'exact bound artifact '+name)
    try:
        for path,digest in {**base.PINS,**PINS}.items():pin(path,digest)
        for path in base.closure(Path(__file__))|{PLAN,ROOT/'uv.lock',ROOT/'pyproject.toml'}:pin(path)
        need(not any(p.name.startswith(('theory_','native_')) for p in base.closure(Path(__file__))),'no producer imports in audit source closure')
        producer_summary=read(D/'summary.json')
        for field in ('inputs_sha256','outputs_sha256'):
            for path,digest in producer_summary[field].items():pin(ROOT/path,digest)
        for name,status in [('direct_cell_count_cnf','INDEPENDENT_DIRECT_CELL_ALL_CAPS_ENCODING_PASS'),('direct_cell_semantics','INDEPENDENT_DIRECT_CELL_SEMANTICS_PASS')]:
            gate=read(B/'20260930_independent_review'/name/'summary.json');need(gate['status']==status,'separate base gate')
            for path,digest in gate['inputs_sha256'].items():pin(ROOT/path,digest)
        records=[check_formula(v,pin) for v in EXPECTED]
        if args.mode!='audit':
            need(args.encoding_gate and args.encoding_gate_sha256,'explicit lex encoding gate');pin(args.encoding_gate,args.encoding_gate_sha256);gate=read(args.encoding_gate);need(gate['status']==STATUS['audit'],'approved exact lex encoding')
            for path,digest in gate['inputs_sha256'].items():pin(ROOT/path,digest)
        if args.mode=='calibrate':
            need(args.native_driver and args.native_spec and args.native_driver_sha256 and args.native_spec_sha256,'explicit frozen native source/spec pins')
            pin(args.native_driver,args.native_driver_sha256);pin(args.native_spec,args.native_spec_sha256)
            sources=base.closure(args.native_driver)
            sources|={ROOT/'acceleration/theory_20260930_direct_cell_count_cnf.py',ROOT/'acceleration/theory_20260930_direct_cell_count_preflight.py'}
            for path in sources:
                pin(path);spec=path.with_name(path.stem+'_spec.md')
                if spec.exists():pin(spec)
            for path,digest in [('build/research-cadical195/source/build/cadical','021e58781c761296b436cfbdf49507ff290db175f67e5609bf6f41e4cc62d0b7'),('build/rook-drat-checker/drat-trim.exe','23d1613cb0b1ed491f4e723ff82492a8be6c349c2426d440412842c5246b90ac')]:pin(ROOT/path,digest)
        if args.mode in ('audit','calibrate'):
            control=controls(records,out);save(out/'controls.json',control)
        else:
            need(args.variant and args.assignment and args.native_output,'complete native SAT input and selected variant')
            rec=next(r for r in records if r['variant']==args.variant);n=rec['variables'];pin(args.assignment);pin(args.native_output)
            values=base.CODEC.assignment(read(args.assignment)['assignment'],n);need(values==base.CODEC.native(args.native_output.read_text(),n),'complete native/JSON agreement')
            seen=0
            with (D/args.variant/'instance.cnf').open('rt',encoding='ascii') as stream:
                stream.readline()
                for row in stream:
                    ints=list(map(int,row.split()));need(ints and ints[-1]==0 and all(0<abs(v)<=n for v in ints[:-1]),'complete raw clause codec');need(any(values[abs(v)]==(v>0) for v in ints[:-1]),'every actual lex/base clause');seen+=1
            need(seen==rec['clauses'],'all actual clauses checked')
            F=[[0]*60 for _ in range(36)]
            for g,d,a,f,v in rec['base']['recipe']['cell_variables']:F[12*f+a][d]=int(values[v])
            result=base.raw_object(F,rec['base']['geometry']);need(args.variant=='standalone' or result['exception_count']>=7,'retained explicit exception lower bound')
            result['lex_words']=strict_words(F,12,rec['scope']['groups'],rec['scope']['group_columns'])
            for comparison in rec['comparators']:
                d,e=comparison['columns'];support=comparison['support'];bits=[]
                for a,flag in zip(support,comparison['equality_flags']):
                    equal=any(F[12*f+a][d] and F[12*f+a][e] for f in range(3));need(values[flag]==equal,'raw equality flag');bits.append(equal)
                for state in comparison['prefixes']:need(values[state['id']]==all(bits[:state['position']]),'raw exact prefix state')
            result.update(lexicographically_ordered=True,variant=args.variant,actual_clauses_checked=seen,independent_approval=True)
            if args.decoded:
                pin(args.decoded);candidate=read(args.decoded);need(candidate['factor']==F and candidate['lexicographically_ordered'] is True,'decoded factor and order metadata')
                for field,expected in [('lex_model_sha256',sha(D/args.variant/'model.json')),('lex_scope_sha256',sha(D/args.variant/'scope.json')),('lex_cnf_sha256',rec['cnf_sha256']),('actual_clauses_checked',seen)]:need(candidate[field]==expected,'decoded literal metadata '+field)
            save(out/'independent_factor.json',result);control=None
        need(time.monotonic()-start<180,'bounded audit execution')
        shared=['Root-authored independent base reconstruction/raw factor path and earlier independent full-assignment codecs are reused explicitly.', 'No production encoder/decoder/native source imported or executed.', 'Identical raw support and separate base encoding/semantic gates are premises; no research SAT witness exists at calibration.']
        report=dict(status=STATUS[args.mode],timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],python=platform.python_version(),inputs_sha256=pins,outputs_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},variants=[dict(variant=r['variant'],variables=r['variables'],clauses=r['clauses'],cnf_sha256=r['cnf_sha256'],added_variables=160,added_clauses=1200,comparators=40) for r in records],controls=control,shared_components=shared,scope='Exact two fixed-support formulations modulo S3^20 column relabelling. The second retains its >=7 exception premise. Full Gram and all caps; no residual D or unrestricted target support.',solver_calls=0,target_resolution=False,artifact_availability='LOCAL_ONLY',elapsed_seconds=time.monotonic()-start)
        save(out/'summary.json',report);print(json.dumps(dict(status=report['status'],summary_sha256=sha(out/'summary.json'))))
    except BaseException as error:
        save(out/'failure.json',dict(error=repr(error),traceback=traceback.format_exc(),inputs_sha256=pins,source_sha256=sha(Path(__file__))));raise


if __name__=='__main__':main()
