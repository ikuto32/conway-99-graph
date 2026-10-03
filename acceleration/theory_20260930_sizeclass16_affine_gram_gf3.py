"""Candidate exact GF(3) affine Gram spans for sixteen frozen literal profiles."""
import argparse,hashlib,json,platform,sys,time,traceback
from collections import defaultdict
from itertools import combinations,product
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'acceleration';B=A/'results';SPEC=Path(__file__).with_name(Path(__file__).stem+'_spec.md')
RAW=B/'20260930_hadamard20_support/six_prism.json';LOCAL=B/'20260930_hadamard_triplicate_counts/local_triples.json';GATE=B/'20260930_independent_review/exact_eight_sizeclass16_cnfs_v2/summary.json';SELECT=B/'20260930_exact_eight_sizeclass16_selection/selection.json';FIXTURE=B/'20260930_srg243_residual_fixture/triangle_blocks.json';OLD=B/'20260930_independent_review/hadamard_gram_affine_gf2/summary.json'
PINS={RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',LOCAL:'9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776',GATE:'b5e5a90ecc9a52996200e3e8cc4988fd04a85122be22b7355de73678ddcb2b0a',SELECT:'9e8bb4c4347cd90d1f6a61f7a6cbdde4bc3a6d86fbb3307cc9015b0b53f20b06',FIXTURE:'3f8dfa3803d6a5db8146dd24a0857477e1aa061ab10dac0f9e6e564aabc86439',OLD:'d581cc37dc751f6aa96be2b016ac33084d466d7497982002506bf7091178dcfa'}
def need(v,m):
    if not v:raise ValueError(m)
def sha(p):
    with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(p.read_bytes())
def save(p,x):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,separators=(',',':'));f.write('\n')
def pack(values):
    one=two=0
    for i,x in enumerate(values):
        if x%3==1:one|=1<<i
        elif x%3==2:two|=1<<i
    return one,two
def unpack(v,n):return [((v[0]>>i)&1)+2*((v[1]>>i)&1)for i in range(n)]
def add(a,b,mask):
    a0=mask^(a[0]|a[1]);b0=mask^(b[0]|b[1])
    return (a0&b[0])|(a[0]&b0)|(a[1]&b[1]),(a0&b[1])|(a[1]&b0)|(a[0]&b[0])
def neg(a):return a[1],a[0]
def scale(a,c):return a if c==1 else neg(a)if c==2 else(0,0)
def dot(a,b):return ((a[0]&b[0]).bit_count()+(a[1]&b[1]).bit_count()+2*((a[0]&b[1]).bit_count()+(a[1]&b[0]).bit_count()))%3
def encoded(a):return [hex(a[0]),hex(a[1])]
def combine(vectors,coeff,n):
    result=(0,0);mask=(1<<n)-1
    for coefficient,bits in [(1,coeff[0]),(2,coeff[1])]:
        while bits:
            bit=bits&-bits;i=bit.bit_length()-1;result=add(result,scale(vectors[i],coefficient),mask);bits-=bit
    return result
def solve(gens,target,n):
    mask=(1<<n)-1;rmask=(1<<len(gens))-1;basis={}
    def reduce(v):
        removed=(0,0)
        while v[0]|v[1]:
            p=(v[0]|v[1]).bit_length()-1
            if p not in basis:break
            row,rep=basis[p];c=1 if(v[0]>>p)&1 else 2
            v=add(v,neg(scale(row,c)),mask);removed=add(removed,scale(rep,c),rmask)
        return v,removed
    for i,g in enumerate(gens):
        v,removed=reduce(g)
        if v!=(0,0):
            p=(v[0]|v[1]).bit_length()-1;rep=add((1<<i,0),neg(removed),rmask)
            if(v[1]>>p)&1:v=neg(v);rep=neg(rep)
            basis[p]=(v,rep)
    residual,coeff=reduce(target)
    need(all(reduce(g)[0]==(0,0)for g in gens),'complete span of all generators')
    for p,(row,rep)in basis.items():need(combine(gens,rep,n)==row and ((row[0]>>p)&1)==1,'literal normalized basis combination')
    result=dict(feasible=residual==(0,0),rank=len(basis),residual=encoded(residual),basis=[dict(pivot=p,row=encoded(row),generator_coefficients=encoded(rep))for p,(row,rep)in sorted(basis.items(),reverse=True)])
    if residual==(0,0):
        need(combine(gens,coeff,n)==target,'literal target span combination');result.update(target_generator_coefficients=encoded(coeff),separating_functional=None)
    else:
        p=(residual[0]|residual[1]).bit_length()-1;functional=(1<<p,0)if(residual[0]>>p)&1 else(0,1<<p)
        for pivot,(row,rep)in sorted(basis.items()):
            c=(-dot(row,functional))%3
            functional=add(functional,scale((1<<pivot,0),c),mask)
        need(all(dot(g,functional)==0 for g in gens)and dot(target,functional)==1,'literal separating functional')
        result.update(target_generator_coefficients=None,separating_functional=encoded(functional))
    return result

def full_gram(rows):
    return [sum(a*b for a,b in zip(rows[i],rows[j]))%3 for i in range(len(rows))for j in range(i,len(rows))]

def controls():
    arithmetic=systems=0
    vectors=list(product(range(3),repeat=2))
    for a,b in product(vectors,repeat=2):
        need(unpack(add(pack(a),pack(b),3),2)==[(x+y)%3 for x,y in zip(a,b)],'complete GF3 bit-plane addition');arithmetic+=1
    for a,b in product(vectors,repeat=2):
        reachable={tuple((u*x+v*y)%3 for x,y in zip(a,b))for u,v in product(range(3),repeat=2)}
        for target in vectors:
            result=solve([pack(a),pack(b)],pack(target),2);need(result['feasible']==(target in reachable),'complete tiny independent Cartesian span');systems+=1
    f=read(FIXTURE)['factor60x180'];need(len(f)==60 and all(len(r)==180 and all(type(x)is int and x in[0,1]for x in r)for r in f),'genuine243 raw factor shape')
    originals=[];alternatives=[]
    for start in range(0,180,3):
        block=[r[start:start+3]for r in f];alt=[r[:]for r in block];alt[0],alt[1]=alt[1],alt[0]
        originals.append(pack(full_gram(block)));alternatives.append(pack(full_gram(alt)))
    n=1830;mask=(1<<n)-1;target=pack(full_gram(f));refs=(0,0)
    for v in alternatives:refs=add(refs,v,mask)
    gens=[add(a,neg(b),mask)for a,b in zip(originals,alternatives)];rhs=add(target,neg(refs),mask);cert=solve(gens,rhs,n)
    need(cert['feasible']and combine(gens,pack([1]*60),n)==rhs,'genuine243 one actual option per block')
    changed=add(rhs,(1,0),mask);coef=tuple(int(x,16)for x in cert['target_generator_coefficients']);need(combine(gens,coef,n)!=changed,'changed target certificate refused')
    need(not solve([pack([1,0])],pack([0,1]),2)['feasible'],'explicit inconsistent small system')
    need(unpack(pack([2,1]),2)==[2,1]and pack([2,1])!=pack([1,2]),'field coefficient sign changes matter')
    return dict(exhaustive_arithmetic_pairs=arithmetic,exhaustive_tiny_systems=systems,genuine243_control=cert,corruptions=['changed target residue','known outside-span vector','coefficient sign swap'],native_calls=0)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);began=time.monotonic();pins={};records=[]
    try:
        def checktime():need(time.monotonic()-began<120,'120-second exact-screen budget')
        def pin(p,w=None):
            value=sha(p);need(w is None or value==w,'frozen input '+key(p));pins[key(p)]=value
        for p,w in PINS.items():pin(p,w)
        for p in [Path(__file__),SPEC,ROOT/'uv.lock',ROOT/'pyproject.toml',A/'theory_20260930_hadamard_gram_affine_gf2.py',A/'theory_20260930_hadamard_gram_affine_gf2_spec.md']:pin(p)
        gate=read(GATE);selection=read(SELECT);cases=gate['checked_cases'];need(gate['status']=='INDEPENDENT_EXACT_EIGHT_EXPLICIT_BATCH_ENCODING_PASS'and len(cases)==16 and gate['selected_case_ids']==selection['ordered_case_ids']==[r['case_id']for r in cases],'exact16 authenticated literal domains')
        save(out/'manifest.json',dict(inputs_sha256=pins,command=[sys.executable,*sys.argv],python=platform.python_version(),seconds=120,finite_field=3,scope='Exactly sixteen sizeclass16 literal initial-domain affine Gram relaxations; not integral factors.',prior_work='217 GF2 domains differ in characteristic and selected profiles; balanced GF3 phase/residual models are different equations.',source_frozen_before_execution=True,native_calls=0,independent_approval=False))
        save(out/'controls.json',controls());checktime()
        raw=read(RAW);C=raw['core_adjacency'];G=raw['prescribed_Gram36'];local=read(LOCAL);words=local['words'];triples=local['survivors'];groups=list(dict.fromkeys(tuple(a for a in range(12)if raw['L'][a][d])for d in range(60)))
        need(len(groups)==20 and all(len(s)==6 and len({a//2 for a in s})==6 for s in groups),'twenty six-coordinate supports')
        need(all(G[i][j]==12*int(i==j)-C[i][j]+2-sum(C[i][k]*C[k][j]for k in range(36))-int(i//12==j//12)for i in range(36)for j in range(36)),'raw core-derived entire integer Gram')
        global_cells=[(i,j)for i in range(36)for j in range(i,36)];gi={pair:i for i,pair in enumerate(global_cells)};target=pack([G[i][j]for i,j in global_cells]);mask=(1<<666)-1
        local_cells=[(a,f,a,f)for a in range(6)for f in range(3)]+[(a,f,b,h)for a,b in combinations(range(6),2)for f,h in product(range(3),repeat=2)]
        maps=[[gi[tuple(sorted((12*f+s[a],12*h+s[b])))]for a,f,b,h in local_cells]for s in groups]
        classes=defaultdict(list)
        for ti,t in enumerate(triples):classes[tuple(sum(words[w][a]==f for w in t)for a in range(6)for f in range(3))].append(ti)
        need(len(triples)==31110 and len(classes)==6061,'complete authenticated local catalogue inventory')
        lv={};lifted={}
        def local_vector(ti):
            if ti not in lv:lv[ti]=pack([sum(words[w][a]==f and words[w][b]==h for w in triples[ti])for a,f,b,h in local_cells])
            return lv[ti]
        def lift(ti,g):
            if(ti,g)not in lifted:
                v=local_vector(ti);lifted[ti,g]=tuple(sum(1<<maps[g][i]for i in range(153)if(plane>>i)&1)for plane in v)
            return lifted[ti,g]
        save(out/'coordinate_order.json',dict(field=3,global_upper_triangle=global_cells,local_cells=local_cells,group_supports=groups,local_to_global=maps,integer_Gram=G))
        for case_number,r in enumerate(cases):
            checktime();pp=ROOT/r['profile_path'];sp=ROOT/r['scope_path'];pin(pp,r['profile_sha256']);pin(sp,r['scope_sha256']);p=read(pp);scope=read(sp);need(p['campaign_case_id']==r['case_id']and p['full_count_profile_sha256']==r['full_count_profile_sha256'],'literal profile identity')
            domains=[]
            for g,support in enumerate(groups):
                signature=tuple(x for a in support for x in p['coordinate_group_fibre_counts'][a][g]);ids=classes[signature];need(ids==p['local_survivor_indices_by_group'][g]and ids,'all original local class members');domains.append(ids)
            need(sum(map(len,domains))==r['selectors']and scope['coordinate_group_fibre_counts']==p['coordinate_group_fibre_counts'],'gate-bound count/domain totals')
            rhs=target;refs=[];gens=[];genrecords=[]
            for g,ids in enumerate(domains):
                ref=ids[0];refs.append(ref);rv=lift(ref,g);rhs=add(rhs,neg(rv),mask)
                for ti in ids[1:]:gens.append(add(lift(ti,g),neg(rv),mask));genrecords.append([g,ti,ref])
            cert=solve(gens,rhs,666);checktime()
            # Construct literal per-group affine weights, each summing to one.
            weights=None
            if cert['feasible']:
                cs=unpack(tuple(int(x,16)for x in cert['target_generator_coefficients']),len(gens));weights=[{ids[0]:1}for ids in domains]
                for coefficient,(g,ti,ref)in zip(cs,genrecords):weights[g][ti]=coefficient;weights[g][ref]=(weights[g][ref]-coefficient)%3
                total=(0,0)
                for g,ws in enumerate(weights):
                    need(sum(ws.values())%3==1,'affine weights sum1 per group')
                    for ti,coefficient in ws.items():total=add(total,scale(lift(ti,g),coefficient),mask)
                need(total==target,'literal twenty affine contributions equal all666 target residues')
            result=dict(case_id=r['case_id'],case_index=r['case_index'],subset_index=r['subset_index'],profile_path=key(pp),profile_sha256=sha(pp),full_count_profile_sha256=r['full_count_profile_sha256'],field=3,domain_indices=domains,domain_counts=list(map(len,domains)),references=refs,generator_records=genrecords,target=encoded(target),target_minus_references=encoded(rhs),certificate=cert,affine_weights=weights,full_factor=False)
            file=out/f'case_{case_number:02d}.json';save(file,result);records.append(dict(case_id=r['case_id'],case_path=key(file),case_sha256=sha(file),rank=cert['rank'],generators=len(gens),feasible=cert['feasible']));save(out/f'checkpoint_{case_number+1:02d}.json',dict(completed=records,pending_case_ids=[x['case_id']for x in cases[case_number+1:]],native_calls=0));print(json.dumps(records[-1]),flush=True)
        save(out/'raw_local_vectors.json',dict(local_vectors=[dict(local_survivor_index=i,word_indices=triples[i],residues=encoded(v))for i,v in sorted(lv.items())]))
        checktime();save(out/'summary.json',dict(status='CANDIDATE_SIZECLASS16_AFFINE_GRAM_GF3_SCREEN_COMPLETE',inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in out.iterdir()if p.is_file()},records=records,field=3,coordinates=666,models=16,consistent=sum(r['feasible']for r in records),inconsistent=sum(not r['feasible']for r in records),elapsed_seconds=time.monotonic()-began,native_calls=0,independent_approval=False,scope='Exact affine relaxation only on sixteen named initial local count classes. GF3 coefficients arbitrary with sum1 per group; no one-hot/integral/full-factor claim, no residualD or target conclusion.'))
    except BaseException as ex:save(out/'failure.json',dict(error=repr(ex),traceback=traceback.format_exc(),inputs_sha256=pins,completed=records,elapsed_seconds=time.monotonic()-began,native_calls=0));raise
if __name__=='__main__':main()
