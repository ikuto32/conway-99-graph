"""Independent complete balanced fixed-support Gram CNF/object audit."""
from collections import Counter
import argparse,copy,hashlib,json,platform,subprocess,sys,time
from datetime import datetime,timezone
from itertools import combinations,permutations,product
from pathlib import Path
import audit_20260930_hadamard_oriented_triples as codec

ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results';D=B/'20260930_hadamard_balanced_gram_cnf'
RAW=B/'20260930_hadamard20_support/six_prism.json';FIXTURE=B/'20260930_srg243_residual_fixture/triangle_blocks.json'
PINS={
 ROOT/'acceleration/audit_20260930_hadamard_balanced_gram.py':'aa20f56e25a628f6d612e41507a9b2bb2ecb28a4fa42cd26e4f8dc4c3f92e641',
 B/'20260930_independent_review/hadamard_balanced_gram_cnf/failure.json':'59035bac1af4075be6cf93225807dfe26db54d61bcf02b1fb5fe54fa835ef403',
 D/'summary.json':'686b73bb4678f1c2f92afcc0f93cd7e18f6d7d3fbe87e6bbafb5c4045aaf2497',
 D/'instance.cnf':'c2d780f94dac4dda955743df03f8db2e8ec0f51217c671eb19fc5e42ed69ba37',
 D/'model.json':'82717d648ad00255fe06c97f2c55ae25e6a3ba73e2e064287a15059c8be6cf98',
 D/'scope.json':'9cc4630a4d7f7b5a36da321465f58f86f1ed918a99e507b50f76f6e485eb334a',
 D/'all150_local_options.json':'dca0c26307c17e11aada1376beab30e7662d2e2d59d208f4e3f83f4f07463e62',
 RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',
 FIXTURE:'3f8dfa3803d6a5db8146dd24a0857477e1aa061ab10dac0f9e6e564aabc86439',
 Path(codec.__file__):'f572c91dc43f7208d34976b165c621c1b314e6963e437eaa475520ae1eb0add3',
 B/'20260930_independent_review/srg243_residual_fixture/summary.json':'28bbd97b8e69515c3eb0345e5aa2db12debfaa8a44e83b2e3487342104c5d50e',
 B/'20260930_independent_review/hadamard20_support_v2/summary.json':'a8477256446e3e402a2a21241dc383a515162dc9c8c07a9a8e26326c07b0f58f',
 ROOT/'acceleration/theory_20260930_hadamard_balanced_gram_cnf.py':'ffb5c842b29d0268073656ce948561af0557c24d067bf0260a9cc8f65ab07016',
 ROOT/'acceleration/theory_20260930_hadamard_balanced_gram_cnf_spec.md':'937e9ae29f4818822b0516cc61f35060cc8352b5cfca9abda2ba2648c53d6a6d',
 ROOT/'uv.lock':'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',
 ROOT/'pyproject.toml':'273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339',
}
need=codec.need;read=codec.read;sha=codec.sha;key=codec.key;save=codec.save;same=codec.same
PERMS=list(permutations(range(3)))

def domain():
    words=[w for w in product(range(3),repeat=6) if all(w.count(f)==2 for f in range(3))]
    need(len(words)==90,'literal balanced words')
    options=[];visited=0
    for triple in combinations(words,3):
        visited+=1
        if any(set(w[a] for w in triple)!={0,1,2} for a in range(6)):continue
        need([w[0] for w in triple]==[0,1,2],'sorted triple first-coordinate normalization')
        pi=[tuple(w[a] for w in triple) for a in range(6)]
        need(pi[0]==(0,1,2),'identity first coordinate')
        phases=[p[0] for p in pi];signs=[(p[1]-p[0])%3 for p in pi]
        need(all((signs[a]*x+phases[a])%3==pi[a][x] for a in range(6) for x in range(3)),'affine S3 description')
        options.append(dict(coordinate_permutations=list(map(list,pi)),colour_words=list(map(list,triple)),signs=signs,phases=phases,normalized_parity_pattern=[int(s==2) for s in signs]))
    options.sort(key=lambda r:r['coordinate_permutations'])
    for i,r in enumerate(options):r['choice_index']=i
    need(visited==117480 and len(options)==150 and sum(not any(x['normalized_parity_pattern']) for x in options)==30 and sum(sum(x['normalized_parity_pattern'])==3 for x in options)==120,'complete local population')
    return options

def gram_from_core(C,n):
    need(len(C)==3*n and all(len(r)==3*n and all(type(x)is int and x in[0,1] for x in r) for r in C),'raw core binary shape')
    need(all(C[i][i]==0 and all(C[i][j]==C[j][i] for j in range(3*n)) for i in range(3*n)),'raw core simple symmetric')
    neighbors=[{j for j,x in enumerate(row) if x} for row in C]
    return [[n*int(i==j)+2-int(i//n==j//n)-C[i][j]-len(neighbors[i]&neighbors[j]) for j in range(3*n)] for i in range(3*n)]

def relative_words(choice,ia,ib):
    words=choice['colour_words']
    return tuple(next(w[ib] for w in words if w[ia]==x) for x in range(3))

def or_clauses(y,xs):return [[-x,y] for x in xs]+[[-y,*xs]]

def onehot_clauses(xs,ps):
    need(len(ps)==len(xs)-1 and len(xs)>=2,'onehot shape')
    rows=[[-xs[0],ps[0]],[-ps[0],xs[0]]]
    for i in range(1,len(ps)):
        rows += [[-ps[i-1],ps[i]],[-xs[i],ps[i]],[-ps[i],ps[i-1],xs[i]],[-ps[i-1],-xs[i]]]
    rows += [[ps[-1],xs[-1]],[-ps[-1],-xs[-1]]]
    return rows

def count_clauses(xs,k):
    return [[-x for x in subset] for subset in combinations(xs,k+1)]+[list(subset) for subset in combinations(xs,len(xs)-k+1)]

def reconstruct(raw,scope,model,options):
    L=raw['L'];need(len(L)==12 and all(len(row)==60 and set(row)<={0,1} for row in L),'raw support')
    supports=[[a for a in range(12) if L[a][d]] for d in range(60)];groups=[]
    for s in supports:
        if s not in groups:groups.append(s)
    columns=[[d for d,s in enumerate(supports) if s==group] for group in groups]
    need(len(groups)==20 and all(len(g)==6 and len(ds)==3 and all(sum(x in g for x in (a,a+1))==1 for a in range(0,12,2)) for g,ds in zip(groups,columns)),'literal support triplicates')
    pairs=[list(pair) for pair in combinations(range(12),2) if pair[0]^1!=pair[1]]
    need(all(sum(a in g for g in groups)==10 for a in range(12)) and all(sum(a in g and b in g for g in groups)==5 for a,b in pairs),'literal support multiplicities')
    C=raw['core_adjacency'];K=gram_from_core(C,12)
    need(C==[[int((i%12==j%12 and i//12!=j//12) or (i//12==j//12 and i%12^1==j%12)) for j in range(36)] for i in range(36)],'literal six-prism core')
    need(K==raw['prescribed_Gram36'],'raw Gram independently derived')
    expected_scope=dict(schema='FIXED_HADAMARD_COMPLETE_BALANCED_GRAM_SCOPE_V1',raw_support_path=key(RAW),raw_support_sha256=PINS[RAW],core_adjacency36=C,prescribed_Gram36=K,L12x60=L,support_columns=supports,groups=groups,group_columns=columns,coordinate_pairs=pairs,balance_is_additional_assumption=True,normalization='First coordinate permutation identity by independent relabelling of each group of three equal-support columns.',all_normalized_local_options=True,prescribed_Gram_encoded=True,outside_column_caps_encoded=False,residual_D_encoded=False,target_graph=False,assumed_target_automorphism=None,assumed_target_automorphism_null_reason='No target automorphism is assumed.',scope='All normalized balanced36x60 factors on this one fixedL with the full prescribed integer Gram; outside caps and residualD omitted.')
    need(same(scope,expected_scope),'complete scope')
    domains=[]
    for g,s in enumerate(groups):
        choices=[]
        for option in options:
            item=copy.deepcopy(option);item['selector']=150*g+option['choice_index']+1
            item['lifted_rows']=[[12*w[i]+s[i] for i in range(6)] for w in option['colour_words']]
            choices.append(item)
        domains.append(dict(group=g,support=s,columns=columns[g],choices=choices))
    clauses=[];onehots=[];channels=[];cells=[];nextvar=3001
    def append(cs):
        meta=dict(first_clause=len(clauses)+1,clause_count=len(cs));clauses.extend(cs);return meta
    for g,dom in enumerate(domains):
        xs=[x['selector'] for x in dom['choices']];ps=list(range(nextvar,nextvar+149));nextvar+=149
        onehots.append(dict(group=g,selectors=xs,prefixes=ps,**append(onehot_clauses(xs,ps))))
    lookup={}
    for a,b in pairs:
        for g,s in enumerate(groups):
            if a not in s or b not in s:continue
            ia,ib=s.index(a),s.index(b)
            for pi in PERMS:
                xs=[x['selector'] for x in domains[g]['choices'] if relative_words(x,ia,ib)==pi]
                need(len(xs)>0,'nonempty literal relative-permutation population')
                y=nextvar;nextvar+=1;lookup[a,b,g,pi]=y
                channels.append(dict(coordinates=[a,b],group=g,permutation=list(pi),variable=y,selectors=xs,**append(or_clauses(y,xs))))
    for a,b in pairs:
        incident=[g for g,s in enumerate(groups) if a in s and b in s]
        for x,y in product(range(3),repeat=2):
            flags=[]
            for g in incident:
                inputs=[lookup[a,b,g,pi] for pi in PERMS if pi[x]==y];flag=nextvar;nextvar+=1
                flags.append(dict(group=g,variable=flag,relative_indicator_inputs=inputs,**append(or_clauses(flag,inputs))))
            bound=1 if x==y else 2
            cells.append(dict(coordinates=[a,b],fibres=[x,y],bound=bound,flags=flags,**append(count_clauses([f['variable'] for f in flags],bound))))
    expected_model=dict(schema='FIXED_HADAMARD_COMPLETE_BALANCED_GRAM_CNF_V1',variables=10480,clauses=74200,primary_selectors=3000,domains=domains,exact_one_prefix_rows=onehots,relative_channels=channels,pair_cell_counts=cells,permutations=list(map(list,PERMS)),variable_populations=dict(selectors=3000,exact_one_prefixes=2980,relative_indicators=1800,cell_flags=2700),scope_sha256=PINS[D/'scope.json'])
    need(Counter(len(c['selectors']) for c in channels)==Counter({6:300,24:900,36:600}),'complete nonuniform channel-population histogram')
    need(nextvar==10481 and len(clauses)==74200 and same(model,expected_model),'all variables/metadata/clauses independently derived')
    return expected_model,clauses

def raw_factor(F,C,n,expected_L=None,groups=None,group_columns=None):
    need(type(F)is list and len(F)==3*n and all(type(row)is list for row in F),'factor rows')
    m=len(F[0]);need(m>0 and all(len(row)==m and all(type(x)is int and x in(0,1) for x in row) for row in F),'complete binary factor')
    neighbors=[{d for d,x in enumerate(row) if x} for row in F]
    K=gram_from_core(C,n)
    actual=[[sum(F[a][d]*F[b][d] for d in range(m)) for b in range(3*n)] for a in range(3*n)]
    need(actual==K,'all integer dot-product Gram entries')
    need(all(sum(row)==n-2 for row in F),'all row margins')
    need(all(sum(F[g*n+a][d] for a in range(n))==2 for g in range(3) for d in range(m)),'all fibre column margins')
    L=[[sum(F[g*n+a][d] for g in range(3)) for d in range(m)] for a in range(n)]
    need(all(x in(0,1) for row in L for x in row),'binary coordinate aggregation')
    need(expected_L is None or L==expected_L,'exact fixed support')
    if groups is not None:
        for support,ds in zip(groups,group_columns,strict=True):
            need(len(ds)==3 and all(sum(F[g*n+a][d] for d in ds)==1 for a in support for g in range(3)),'exact local balance')
            need(all(F[g*n+support[0]][ds[g]]==1 for g in range(3)),'normalized first coordinate')
    columnsets=[{a for a in range(3*n) if F[a][d]} for d in range(m)]
    caps=[dict(columns=[d,e],overlap=len(columnsets[d]&columnsets[e])) for d,e in combinations(range(m),2)]
    mixed=[[F[a][d]+sum(C[a][b]*F[b][d] for b in range(3*n)) for d in range(m)] for a in range(3*n)]
    return dict(actual_Gram=actual,coordinate_support=L,column_pair_records=caps,column_cap_violations=[r for r in caps if r['overlap']>2],mixed_cap_violations=[dict(row=a,column=d,value=mixed[a][d]) for a in range(3*n) for d in range(m) if mixed[a][d]>2])

def canonical(F,n):
    pairs=[list(pair) for pair in combinations(range(n),2) if pair[0]^1!=pair[1]]
    raw=[[a for a in range(n) if F[a][d]] for d in range(len(F[0]))]
    need(sorted(raw)==pairs,'literal first-fibre pair catalogue')
    order=[raw.index(pair) for pair in pairs];need(sorted(order)==list(range(len(raw))),'column permutation bijection')
    transformed=[[row[d] for d in order] for row in F]
    inverse=[order.index(d) for d in range(len(order))]
    need([[row[d] for d in inverse] for row in transformed]==F,'inverse canonical column permutation')
    return order,transformed

def object_check(values,model,scope,clauses,decoded=None):
    codec.all_clauses(clauses,values)
    F=[[0]*60 for _ in range(36)];selected=[]
    for dom in model['domains']:
        active=[x for x in dom['choices'] if values[x['selector']]];need(len(active)==1,'one local selected option')
        choice=active[0];selected.append(choice['selector'])
        for d,word in zip(dom['columns'],choice['colour_words'],strict=True):
            for a,fibre in zip(dom['support'],word,strict=True):F[12*fibre+a][d]=1
    checks=raw_factor(F,scope['core_adjacency36'],12,scope['L12x60'],scope['groups'],scope['group_columns'])
    order,canonical_F=canonical(F,12)
    obj=dict(factor=F,L=scope['L12x60'],selected_selector_ids=selected,canonical_column_order=order,canonical_factor=canonical_F,core_adjacency=scope['core_adjacency36'],target_gram=scope['prescribed_Gram36'],checks=checks,Gram_factor=True,factor_also_passes_column_caps=not checks['column_cap_violations'],factor_also_passes_mixed_caps=not checks['mixed_cap_violations'],target_graph=False,residual_D=None,balance_is_additional_assumption=True,model_sha256=PINS[D/'model.json'],scope_sha256=PINS[D/'scope.json'],independent_approval=False)
    if decoded is not None:need(same(obj,decoded),'entire independently decoded factor/diagnostics')
    return obj

def controls(raw,scope,model,options,clauses):
    rejected=[]
    def reject(name,fn):
        try:fn()
        except(ValueError,KeyError,TypeError,IndexError):rejected.append(name)
        else:raise ValueError('corruption accepted '+name)
    prefix_cases=0
    for n in range(2,7):
        xs=list(range(1,n+1));ps=list(range(n+1,2*n));cs=onehot_clauses(xs,ps)
        counts=Counter()
        for bits in product([False,True],repeat=2*n-1):
            vals=dict(enumerate(bits,1));actual=all(any(vals[abs(x)]==(x>0) for x in c) for c in cs)
            expected=sum(vals[i] for i in xs)==1 and all(vals[p]==any(vals[x] for x in xs[:j+1]) for j,p in enumerate(ps))
            need(actual==expected,'prefix full truth relation')
            if actual:counts[tuple(bits[:n])]+=1
            prefix_cases+=1
        need(len(counts)==n and set(counts.values())=={1},'unique prefix extension')
    or_cases=0
    for n in range(1,6):
        cs=or_clauses(n+1,list(range(1,n+1)))
        for bits in product([False,True],repeat=n+1):
            vals=dict(enumerate(bits,1));actual=all(any(vals[abs(x)]==(x>0) for x in c) for c in cs)
            need(actual==(bits[-1]==any(bits[:-1])),'OR truth');or_cases+=1
    for k in(1,2):
        cs=count_clauses(list(range(1,6)),k)
        for bits in product([False,True],repeat=5):
            vals=dict(enumerate(bits,1));need(all(any(vals[abs(x)]==(x>0) for x in c) for c in cs)==(sum(bits)==k),'five flag exact count')
    rel_controls=0
    for pa,pb in product(PERMS,repeat=2):
        words=[[pa[d],pb[d]] for d in range(3)]
        rel=relative_words(dict(colour_words=words),0,1)
        for x,y in product(range(3),repeat=2):need(sum(w==[x,y] for w in words)==int(rel[x]==y),'literal relative cell orientation');rel_controls+=1
    fixture=read(FIXTURE);F=fixture['factor60x180'];C=fixture['cubic_core60']
    genuine=raw_factor(F,C,20);need(not genuine['column_cap_violations'] and not genuine['mixed_cap_violations'],'genuine243 factor all cap controls')
    order,canon=canonical(F,20);need(len(order)==180,'generic full canonicalization')
    reversed_F=[row[::-1] for row in F];need(raw_factor(reversed_F,C,20)['actual_Gram']==genuine['actual_Gram'],'literal reordered positive')
    for name in ['bit','row_length','Boolean_bit','nonbinary','missing_row']:
        bad=copy.deepcopy(F)
        if name=='bit':bad[0][0]^=1
        elif name=='row_length':bad[0].pop()
        elif name=='Boolean_bit':bad[0][0]=bool(bad[0][0])
        elif name=='nonbinary':bad[0][0]=2
        else:bad.pop()
        reject('raw_'+name,lambda bad=bad:raw_factor(bad,C,20))
    for name in ['drop_constant','wrong_relative','wrong_prefix','wrong_cell_bound','wrong_flag','wrong_lifted_row','invent_caps']:
        bad=copy.deepcopy(model);s=copy.deepcopy(scope)
        if name=='drop_constant':bad['domains'][0]['choices'].pop(next(i for i,x in enumerate(bad['domains'][0]['choices']) if not any(x['normalized_parity_pattern'])))
        elif name=='wrong_relative':bad['relative_channels'][0]['permutation']=[0,2,1]
        elif name=='wrong_prefix':bad['exact_one_prefix_rows'][0]['prefixes'][0]+=1
        elif name=='wrong_cell_bound':bad['pair_cell_counts'][0]['bound']=2
        elif name=='wrong_flag':bad['pair_cell_counts'][0]['flags'][0]['relative_indicator_inputs'][0]+=1
        elif name=='wrong_lifted_row':bad['domains'][0]['choices'][0]['lifted_rows'][0][0]+=1
        else:s['outside_column_caps_encoded']=True
        reject(name,lambda bad=bad,s=s:reconstruct(raw,s,bad,options))
    reject('dropped_clause',lambda:need(codec.cnf_bytes(clauses[:-1],10480)==(D/'instance.cnf').read_bytes(),'complete raw CNF'))
    bad=copy.deepcopy(clauses);bad[11920][0]*=-1;reject('signed_channel_clause',lambda:need(codec.cnf_bytes(bad,10480)==(D/'instance.cnf').read_bytes(),'correct OR direction'))
    literals=[i if i%2 else -i for i in range(1,10481)];values=codec.assignment(literals,10480)
    text='c SYNTHETIC10480 CODEC ONLY\ns SATISFIABLE\n'+'\n'.join('v '+' '.join(map(str,literals[i:i+113])) for i in range(0,10480,113))+' 0\n'
    need(codec.native(text,10480)==values,'all10480 native/JSON equality')
    synthetic=[[literals[i%10480]] for i in range(74200)];codec.all_clauses(synthetic,values)
    for name,bad in [('missing_status',text.replace('s SATISFIABLE\n','')),('wrong_status',text.replace('SATISFIABLE','UNSATISFIABLE')),('missing_zero',text.replace(' 0\n','\n')),('duplicate',text.replace('v 1 -2','v 1 1')),('post_zero',text+'v 1\n'),('out_of_range',text.replace('v 1 -2','v 10481 -2'))]:reject(name,lambda bad=bad:codec.native(bad,10480))
    reject('missing_JSON_literal',lambda:codec.assignment(literals[:-1],10480));reject('Boolean_JSON',lambda:codec.assignment([True,*literals[1:]],10480))
    wrong=copy.deepcopy(synthetic);wrong[-1][0]*=-1;reject('false_synthetic_clause',lambda:codec.all_clauses(wrong,values))
    return dict(prefix_truth_cases=prefix_cases,OR_truth_cases=or_cases,five_bit_count_cases=64,relative_cell_cases=rel_controls,local_word_triples=117480,retained_options=150,generic_positive='Authenticated243 factor60x180 and reversed column order; not research balanced support.',synthetic_positive='Full10480-ID and74200-clause codec only.',known_research_positive=None,known_research_positive_reason='No authenticated research Gram factor available at gate time.',corruptions_rejected=rejected),text,synthetic

def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['audit','calibrate','sat']);ap.add_argument('--encoding-gate',type=Path);ap.add_argument('--encoding-gate-sha256');ap.add_argument('--assignment',type=Path);ap.add_argument('--native-output',type=Path);ap.add_argument('--decoded',type=Path);ap.add_argument('--driver',type=Path);ap.add_argument('--driver-sha256');ap.add_argument('--driver-spec-sha256');ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};start=time.perf_counter()
    def pin(p,h=None):
        p=p.resolve();value=sha(p);need(h is None or value==h,'input identity '+key(p));pins[key(p)]=value
    try:
        for p,h in PINS.items():pin(p,h)
        summary=read(D/'summary.json')
        for p,h in {**summary['inputs_sha256'],**summary['outputs_sha256']}.items():pin(ROOT/p,h)
        pin(Path(__file__));pin(ROOT/'docs/AUDIT_20260930_HADAMARD_BALANCED_GRAM.md')
        if args.driver:
            need(args.driver_sha256 and args.driver_spec_sha256,'explicit driver/spec frozen hashes')
            pin(args.driver,args.driver_sha256);pin(args.driver.with_name(args.driver.stem+'_spec.md'),args.driver_spec_sha256)
            # These are the native driver's documented frozen direct helper imports.
            pin(ROOT/'acceleration/native_20260930_unrestricted_full99.py','da7ee9c03d454bd5ad0af0d82bead3520f3f270c70e71d4355161d036fd8ef22')
            pin(ROOT/'acceleration/native_20260930_proof_location.py','ff7fd55658b7cb63e9586bd862f8f182269f2978a3b873ba9afccfa41a345854')
        raw,scope,model=read(RAW),read(D/'scope.json'),read(D/'model.json');options=domain()
        need(same(options,read(D/'all150_local_options.json')),'complete independent local domain table')
        expected,clauses=reconstruct(raw,scope,model,options)
        need(codec.cnf_bytes(clauses,10480)==(D/'instance.cnf').read_bytes(),'all74200 raw clauses/header')
        if args.mode!='audit':
            need(args.encoding_gate is not None and args.encoding_gate_sha256,'explicit encoding gate')
            pin(args.encoding_gate,args.encoding_gate_sha256);gate=read(args.encoding_gate)
            need(gate['status']=='INDEPENDENT_HADAMARD_BALANCED_GRAM_ENCODING_PASS','exact balanced Gram gate')
            for p in[RAW,D/'scope.json',D/'model.json',D/'instance.cnf',Path(__file__)]:need(gate['inputs_sha256'][key(p)]==pins[key(p)],'same encoding source/input '+key(p))
        control,text,synthetic=controls(raw,scope,model,options,clauses);save(out/'controls.json',control)
        (out/'synthetic_native.log').write_text(text,encoding='ascii');(out/'synthetic.cnf').write_bytes(codec.cnf_bytes(synthetic,10480))
        if args.mode=='sat':
            need(args.assignment is not None and args.native_output is not None,'complete raw assignment/stdout')
            pin(args.assignment);pin(args.native_output);data=read(args.assignment);vals=codec.assignment(data['assignment'] if isinstance(data,dict) else data,10480)
            need(vals==codec.native(args.native_output.read_text(encoding='utf-8'),10480),'every native/JSON value')
            decoded=None
            if args.decoded:pin(args.decoded);decoded=read(args.decoded)
            obj=object_check(vals,expected,scope,clauses,decoded);save(out/'independent_Gram_factor.json',obj)
        ts=datetime.now(timezone.utc).isoformat();save(out/'manifest.json',dict(timestamp=ts,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),uv=subprocess.check_output(['uv','--version'],text=True).strip(),inputs_sha256=pins,elapsed_seconds=time.perf_counter()-start,solver_calls=0))
        if args.mode=='audit':
            save(out/'claim_binding.json',dict(id='C-FIXED-HADAMARD-COMPLETE-BALANCED-GRAM-ENCODING',revision=1,kind='encoding',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',
                statement='The frozen10480-variable74200-clause CNF is equivalent to a binary36x60factor with the full prescribed integer Gram, the fixed six-prism Hadamard support, and balanced identical-support triples, modulo independent relabelling of the three columns in each group to normalize its first coordinate. All150local choices per group are included; the auxiliary variables have unique extensions.',scope='One fixed core/support and the extra balanced-triple condition; outside-column caps and residualD are omitted.',
                assumptions=['Pinned raw support/core.','Coordinatewise balance of each three-column identical-support group.'],dependencies=[dict(id='C-FIVE-FIXED-HADAMARD20-SUPPORT-PROJECTIONS',revision=1,relation='premise')],verification_dependencies=[dict(id='C-FIXED-HADAMARD-ALL-MIXED-ORIENTED-TRIPLE-ENCODING',revision=1,relation='verification_dependency',reason='Only frozen generic assignment/native/format helper code is reused; its mathematics is not a premise of this broader encoding.')],
                verifier='/root/structural_attack',producer='/root/state_literature_audit',method='Independent unordered color-word triple enumeration, literal raw-core/Gram and relative-cell reconstruction, all-clause byte checking and exact controls.',shared_components=['Pinned raw support and genuine243 fixture.','Frozen independently authored generic native/JSON/clause-codec helpers, newly calibrated at full10480/74200 size.','No producer code imported.'],artifact_availability='LOCAL_ONLY',availability_reason='Workspace evidence pending parent publication.',external_review=None,external_review_reason='No external review asserted.',limitations=['Balance and this fixed support are additional restrictions.','No Ycaps or residualD encoded.','No research SAT/UNSAT result in this gate.'],created_at=ts,updated_at=ts,inputs_sha256=pins,evidence_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()}))
        status={'audit':'INDEPENDENT_HADAMARD_BALANCED_GRAM_ENCODING_PASS','calibrate':'INDEPENDENT_HADAMARD_BALANCED_GRAM_OBJECT_CALIBRATION_PASS','sat':'INDEPENDENT_HADAMARD_BALANCED_GRAM_SAT_OBJECT_PASS'}[args.mode]
        save(out/'summary.json',dict(status=status,timestamp=ts,inputs_sha256=pins,outputs_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},variables=10480,clauses=74200,local_options_per_group=150,group_count=20,relative_channels=1800,exact_cell_rows=540,controls=control,solver_calls=0,outside_caps_encoded=False,target_resolution=False,scope='Complete prescribed Gram under fixedL and additional balance only; cap diagnostics do not add constraints.'))
        print(json.dumps(dict(status=status,summary_sha256=sha(out/'summary.json'),source_sha256=sha(Path(__file__)))))
    except BaseException as ex:save(out/'failure.json',dict(error=repr(ex)));raise
if __name__=='__main__':main()
