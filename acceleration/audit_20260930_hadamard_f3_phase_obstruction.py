"""Independent literal GF(3) branch-obstruction checker; no producer imports."""
from collections import Counter
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
from itertools import combinations,permutations,product
from pathlib import Path
import argparse,json,platform,subprocess,sys,time

ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_'
RAW=B+'hadamard20_support/six_prism.json';PROJ=B+'independent_review/hadamard_parity_support_cuts_sat/independent_projection.json';GATE=B+'independent_review/hadamard_parity_support_cuts_sat/summary.json';D=B+'hadamard_f3_phases/'
PINS={RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',PROJ:'f43ad5f79d6fc8c8f6825f52d0140a07852a873207642b4edb7c035cb5ed4a8c',
 GATE:'02ae20d479a0d2589c02f435e2a8fdd781ec0459b60095d130b68b5f2721a04a',
 D+'summary.json':'13525086e739f0c62ed4a9a46f2527316832bcaf08aa403aef10e4420dc51868',
 D+'phase_system.json':'aecf80f4f1c7cd29f821cb52ec502b810aa87fc8ff908ea38e2f36a69e416061',
 D+'linear_certificate.json':'e7d8640b5ee9a2024b17e6539133f9a36f6328f335dc3150206d8eb9732d6fc3',
 D+'inequality_screen.json':'5cacba21b7824d666a6380063dcfa686b8833817755c1d7655eaddaf59c45624',
 'acceleration/theory_20260930_hadamard_f3_phases.py':'154d145af9f23a3b150ec8c798598d63779fab28a1474468b622a718fc82beaa',
 'acceleration/theory_20260930_hadamard_f3_phases_spec.md':'988a20303d2bcb0ff36be4295e8da3389b55dadb70b4633ac80304b651550ddb',
 'docs/DERIVATION_20260930_HADAMARD_F3_PHASES.md':'5fe452fba8fe496a00e81e7beb937fe999c61d1e43d200c227fae08861f8c6e2',
 'uv.lock':'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db','pyproject.toml':'273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339'}
def need(ok,why):
    if not ok:raise ValueError(why)
def h(p):return sha256(Path(p).read_bytes()).hexdigest()
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(Path(p).read_bytes())
def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def dot(x,y):return sum(a*b for a,b in zip(x,y,strict=True))%3
def linear_combination(weights,rows):
    result=[0]*len(rows[0])
    for weight,row in zip(weights,rows,strict=True):
        need(type(weight)is int and weight in(0,1,2),'field coefficient')
        if weight:
            for j,value in enumerate(row):result[j]=(result[j]+weight*value)%3
    return result
def column_rank(matrix):
    """Reduce columns right-to-left, using descending row pivots; no RREF."""
    m,n=len(matrix),len(matrix[0]);basis={}
    for col in reversed(range(n)):
        vector=[matrix[r][col]%3 for r in range(m)];comb=[0]*n;comb[col]=1
        for pivot in sorted(basis,reverse=True):
            coefficient=vector[pivot]
            if coefficient:
                b,w=basis[pivot]
                vector=[(x-coefficient*y)%3 for x,y in zip(vector,b,strict=True)]
                comb=[(x-coefficient*y)%3 for x,y in zip(comb,w,strict=True)]
        occupied=[r for r,x in enumerate(vector)if x]
        if occupied:
            p=max(occupied);inverse=vector[p]
            basis[p]=([(inverse*x)%3 for x in vector],[(inverse*x)%3 for x in comb])
    return [dict(pivot_row=p,column_combination=w,echelon_column=v)for p,(v,w)in sorted(basis.items(),reverse=True)]
def derive(raw,projection):
    expected_core=[[0]*36 for _ in range(36)]
    for g in range(3):
        for a in range(12):
            expected_core[12*g+a][12*g+(a^1)]=1
            for q in range(3):
                if q!=g:expected_core[12*g+a][12*q+a]=1
    need(raw['core_adjacency']==expected_core,'raw literal six-prism adjacency')
    gram=[[12*int(i==j)+2-expected_core[i][j]-sum(expected_core[i][k]*expected_core[k][j]for k in range(36))-int(i//12==j//12)for j in range(36)]for i in range(36)]
    need(gram==raw['prescribed_Gram36'],'Gram derived from core and root attachments')
    L=raw['L'];catalog={}
    for col in range(60):
        support=tuple(i for i in range(12)if L[i][col])
        need(len(support)==6 and all(L[i][col]in(0,1)for i in range(12)),'binary6-support')
        catalog.setdefault(support,[]).append(col)
    groups=[list(s)for s in catalog];need(len(groups)==20 and all(len(c)==3 for c in catalog.values()),'support multiplicities')
    patterns=projection['selected_group_parity_patterns'];need(len(patterns)==20 and all(p[0]==0 and sum(p)==3 for p in patterns),'all20 mixed patterns')
    signs=[[(-1)**p%3 for p in pattern]for pattern in patterns]
    # Build by global coordinate keys, rather than copying producer expressions.
    ids={(g,a):6*g+pos for g,support in enumerate(groups)for pos,a in enumerate(support)}
    sign={(g,a):signs[g][pos]for g,support in enumerate(groups)for pos,a in enumerate(support)}
    rows=[];inequalities=[];pair_records=[]
    def dense(coeff):return [coeff.get(j,0)%3 for j in range(120)]
    def addrow(kind,coeff,**metadata):rows.append(dict(index=len(rows),kind=kind,coefficients=dense(coeff),rhs=0,**metadata))
    def nonzero(kind,coeff,**metadata):inequalities.append(dict(index=len(inequalities),kind=kind,coefficients=dense(coeff),required='nonzero in GF(3)',**metadata))
    for g,support in enumerate(groups):addrow('column_gauge',{ids[g,support[0]]:1},group=g)
    for g,support in enumerate(groups):
        for s in(1,2):
            coordinates=[a for a in support if sign[g,a]==s];positions=[support.index(a)for a in coordinates]
            need(len(coordinates)==3,'3coordinates of each sign')
            addrow('local_same_sign_sum',{ids[g,a]:1 for a in coordinates},group=g,sign=s,positions=positions)
            for a,b in combinations(coordinates,2):nonzero('local_same_sign_distinct',{ids[g,a]:2,ids[g,b]:1},group=g,positions=[support.index(a),support.index(b)])
    for a,b in combinations(range(12),2):
        if (a^1)==b:continue
        need([[gram[12*x+a][12*y+b]for y in range(3)]for x in range(3)]==[[2-int(x==y)for y in range(3)]for x in range(3)],'literal pair2J-I block')
        common=[g for g,support in enumerate(groups)if a in support and b in support];need(len(common)==5,'five containing groups')
        relative=[]
        for g in common:
            ratio=sign[g,b]*sign[g,a]%3;coeff={ids[g,b]:1,ids[g,a]:(-ratio)%3}
            relative.append(dict(group=g,positions=[groups[g].index(a),groups[g].index(b)],relative_sign=ratio,relative_phase_coefficients=dense(coeff)))
        odd=[r for r in relative if r['relative_sign']==2];even=[r for r in relative if r['relative_sign']==1]
        need(len(odd)==3 and len(even)==2,'eachpair3reflections2translations')
        for label,part in [('odd',odd),('even',even)]:
            coeff={i:sum(r['relative_phase_coefficients'][i]for r in part)%3 for i in range(120)}
            addrow('pair_'+label+'_phase_sum',coeff,coordinates=[a,b],groups=[r['group']for r in part])
        for left,right in combinations(odd,2):nonzero('odd_relative_phases_distinct',{i:(left['relative_phase_coefficients'][i]-right['relative_phase_coefficients'][i])%3 for i in range(120)},coordinates=[a,b],groups=[left['group'],right['group']])
        for record in even:nonzero('even_relative_phase_nonzero',{i:v for i,v in enumerate(record['relative_phase_coefficients'])},coordinates=[a,b],group=record['group'])
        pair_records.append(dict(coordinates=[a,b],relative_maps=relative))
    variables=[dict(index=ids[g,a],group=g,position=pos,coordinate=a,sign=sign[g,a])for g,support in enumerate(groups)for pos,a in enumerate(support)]
    need((len(variables),len(rows),len(inequalities),len(pair_records))==(120,180,420,60),'complete reconstructed dimensions')
    return dict(field=3,variables=variables,groups=groups,patterns=patterns,signs=signs,rows=rows,pair_records=pair_records,necessary_nonzero_functionals=inequalities,
        all_balanced_parity_branches_covered=False,one_fixed_parity_branch=True,Ycaps_encoded=False,residual_D_encoded=False)
def compare_system(actual,expected):need(actual==expected,'full independent raw equation and inequality reconstruction')
def check_obstruction(record,matrix,condition):
    need(record['condition']==condition,'exact required nonzero functional')
    need(len(record['row_combination'])==180,'all180 row coefficients')
    need(linear_combination(record['row_combination'],matrix)==condition['coefficients'],'literal row-combination identity')
    need(condition['required']=='nonzero in GF(3)'and any(condition['coefficients']),'genuine nonzero requirement')
def finite_controls():
    affine={tuple((s*x+t)%3 for x in range(3)):(s,t)for s in(1,2)for t in range(3)}
    need(set(affine)==set(permutations(range(3))),'allS3 are affine uniquely')
    orientation=0
    for pa,(sa,ta)in affine.items():
        for pb,(sb,tb)in affine.items():
            relative=tuple(pb[pa.index(x)]for x in range(3));r=affine[relative]
            need(r==(sb*sa%3,(tb-sb*sa*ta)%3),'relative map from literal inverse/composition');orientation+=3
    words=[w for w in product(range(3),repeat=6)if all(w.count(c)==2 for c in range(3))];count=0;hist=Counter();local=[]
    for triple in combinations(words,3):
        if not all(sorted(w[k]for w in triple)==[0,1,2]for k in range(6)):continue
        count+=1;first=[w[0]for w in triple];normalized=[triple[first.index(x)]for x in range(3)]
        maps=[tuple(normalized[x][k]for x in range(3))for k in range(6)];pairs=[affine[p]for p in maps];pattern=tuple(int(s==2)for s,t in pairs);hist[pattern]+=1
        need(pairs[0]==(1,0),'literal column permutation gives first-map identity')
        if any(pattern):
            need(sum(pattern)==3 and len(set(pairs))==6,'mixed balance forces allsix permutations')
            for s in(1,2):need(sorted(t for u,t in pairs if u==s)==[0,1,2],'each sign class is phase bijection')
        local.append(dict(words=[list(w)for w in triple],normalized_affine_maps=[list(p)for p in pairs]))
    need(count==150 and sorted(hist.values())==[12]*10+[30],'complete direct117480 triple controls')
    pair_positive=[]
    for intercepts in product(range(3),repeat=5):
        maps=[tuple((-x+t)%3 for x in range(3))for t in intercepts[:3]]+[tuple((x+t)%3 for x in range(3))for t in intercepts[3:]]
        entries=[[sum(p[x]==y for p in maps)for y in range(3)]for x in range(3)]
        exact=entries==[[2-int(x==y)for y in range(3)]for x in range(3)]
        expected=sorted(intercepts[:3])==[0,1,2]and sorted(intercepts[3:])==[1,2]
        need(exact==expected,'literal243 pair configurations')
        if exact:need(sum(intercepts[:3])%3==sum(intercepts[3:])%3==0,'pair sum consequences');pair_positive.append(list(intercepts))
    need(len(pair_positive)==12,'nonempty exact pair controls')
    ranks=0
    for v in product(range(3),repeat=6):
        m=[list(v[:3]),list(v[3:])];rank=len(column_rank(m));expected=2 if any((m[0][a]*m[1][b]-m[0][b]*m[1][a])%3 for a,b in combinations(range(3),2))else int(any(v))
        need(rank==expected,'729rank controls by direct minors');ranks+=1
    need({((y-x)%3,(y+x)%3)for x,y in product(range(3),repeat=2)}==set(product(range(3),repeat=2)),'entry transform is bijective')
    return dict(affine_literal_cases=orientation,all_unordered_word_triples=117480,balanced_local_positives=150,mixed_local_positives=120,
        local_objects=local,all_pair_phase_cases=243,pair_positive_objects=pair_positive,rank_minor_controls=ranks,full_research_factor_control=None,
        full_research_factor_control_reason='No research factor is assumed; positives calibrate the complete local mathematical implications.')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    try:
        need(all(h(ROOT/p)==value for p,value in PINS.items()),'exact immutable raw pins');gate=read(ROOT/GATE)
        need(gate['status']=='INDEPENDENT_HADAMARD_PARITY_SUPPORT_CUT_SAT_OBJECT_PASS'and gate['outputs_sha256'][PROJ]==PINS[PROJ],'authenticated parity object')
        pins={**PINS,key(__file__):h(__file__),'docs/AUDIT_20260930_HADAMARD_F3_PHASE_OBSTRUCTION.md':h(ROOT/'docs/AUDIT_20260930_HADAMARD_F3_PHASE_OBSTRUCTION.md')}
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),
            inputs_sha256=pins,verifier='/root/structural_attack',producer='/root/state_literature_audit',producer_code_imported=False,
            limits=dict(wall_seconds=60,solver_calls=0),scope='Independent exact exclusion review of the one second selected balanced parity branch.'))
        save(out/'finite_controls.json',finite_controls());expected=derive(read(ROOT/RAW),read(ROOT/PROJ));actual=read(ROOT/(D+'phase_system.json'));compare_system(actual,expected)
        matrix=[r['coefficients']for r in expected['rows']];cert=read(ROOT/(D+'linear_certificate.json'));screen=read(ROOT/(D+'inequality_screen.json'))
        independent_columns=column_rank(matrix);need(len(independent_columns)==119,'alternate119 column rank')
        need(len({r['pivot_row']for r in independent_columns})==119,'distinct column basis pivots')
        for c in independent_columns:
            need([dot(row,c['column_combination'])for row in matrix]==c['echelon_column'],'independent column basis identity')
            p=c['pivot_row'];need(c['echelon_column'][p]==1 and not any(c['echelon_column'][p+1:]),'triangular independent columns')
        need(cert['rank']==119 and cert['nullity']==1 and len(cert['rref'])==180 and len(cert['row_transform'])==180,'producer rank dimensions')
        for combination,target in zip(cert['row_transform'],cert['rref'],strict=True):need(linear_combination(combination,matrix)==target,'all21600 producer transform outputs')
        need(len(cert['nullspace_basis'])==1 and len(cert['nullspace_basis'][0])==120 and all(type(v)is int and v in(0,1,2)for v in cert['nullspace_basis'][0])and any(cert['nullspace_basis'][0]),'nonzero kernel witness')
        need(all(dot(row,cert['nullspace_basis'][0])==0 for row in matrix),'all180 kernel products')
        need(len(screen['obstructions'])==len(screen['screens'])==420,'all420 obstruction records')
        for i,condition in enumerate(expected['necessary_nonzero_functionals']):
            check_obstruction(screen['obstructions'][i],matrix,condition)
            need(screen['screens'][i]==dict(inequality_index=i,restricted_coefficients=[0],identically_zero=True),'exact corresponding screen record')
            need(dot(condition['coefficients'],cert['nullspace_basis'][0])==0,'all420 kernel restrictions')
        rejected=[]
        def rejects(name,fn):
            try:fn()
            except(ValueError,AssertionError,IndexError,KeyError):rejected.append(name)
            else:raise ValueError('corruption accepted: '+name)
        for name,mutate in [
            ('changed_equation_coefficient',lambda x:x['rows'][0]['coefficients'].__setitem__(0,2)),
            ('changed_rhs',lambda x:x['rows'][0].__setitem__('rhs',1)),
            ('changed_sign',lambda x:x['signs'][0].__setitem__(0,2)),
            ('changed_coordinate',lambda x:x['variables'][0].__setitem__('coordinate',11)),
            ('missing_equation',lambda x:x['rows'].pop()),
            ('changed_pattern',lambda x:x['patterns'][0].__setitem__(1,0)),
            ('reversed_inequality',lambda x:x['necessary_nonzero_functionals'][0].__setitem__('required','zero'))]:
            bad=deepcopy(actual);mutate(bad);rejects(name,lambda bad=bad:compare_system(bad,expected))
        first=screen['obstructions'][0];condition=expected['necessary_nonzero_functionals'][0]
        bad=deepcopy(first);bad['row_combination'][0]=(bad['row_combination'][0]+1)%3;rejects('changed_row_combination',lambda:check_obstruction(bad,matrix,condition))
        bad=deepcopy(first);bad['condition']['coefficients'][1]=(bad['condition']['coefficients'][1]+1)%3;rejects('changed_required_functional',lambda:check_obstruction(bad,matrix,condition))
        wrong=cert['nullspace_basis'][0][:];wrong[0]=(wrong[0]+1)%3;rejects('changed_kernel_vector',lambda:need(all(dot(row,wrong)==0 for row in matrix),'bad kernel rejected'))
        need(all(row['rhs']==0 for row in expected['rows']),'homogeneous equation premise')
        first_ids=[i for i,c in enumerate(condition['coefficients'])if c];need(len(first_ids)==2,'first local phase difference')
        save(out/'independent_rank_certificate.json',dict(method='Right-to-left column elimination with descending row pivots; direct column combination verification.',columns=independent_columns,nonzero_kernel=cert['nullspace_basis'][0],rank=119,nullity=1))
        save(out/'minimal_obstruction.json',dict(field=3,condition=condition,row_combination=first['row_combination'],
            used_equations=[dict(multiplier=w,**expected['rows'][i])for i,w in enumerate(first['row_combination'])if w],
            first_variables=[expected['variables'][i]for i in first_ids],literal_identity_checked=True,all_homogeneous_rhs=0,
            contradiction='A required nonzero difference is a linear combination of homogeneous equations, so it equals zero.'))
        save(out/'corruptions.json',dict(rejected=rejected,count=len(rejected)))
        elapsed=time.monotonic()-start;need(elapsed<60,'bounded audit');need(all(h(ROOT/p)==value for p,value in pins.items()),'unchanged inputs')
        output_hashes={key(p):h(p)for p in out.iterdir()if p.is_file()}
        claim=dict(id='C-FIXED-HADAMARD-SECOND-PARITY-GF3-PHASE-SCREEN',revision=1,
            statement='No binary36x60factor on the fixed six-prism Hadamard support with balanced identical-support triplets and the exact20normalized parity patterns in independent projection f43ad5f79d6fc8c8f6825f52d0140a07852a873207642b4edb7c035cb5ed4a8c can have the prescribed Gram.',
            kind='exclusion',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',
            scope='Only this second selected balanced parity branch; outside-column caps are not needed for this exclusion, residualD absent.',
            assumptions=['Fixed raw support/core and specified projection hashes.','The three columns in each identical-support group are coordinatewise balanced.'],
            dependencies=[dict(relation='premise',reference=GATE,sha256=PINS[GATE]),dict(relation='premise',reference=RAW,sha256=PINS[RAW])],
            verifier='/root/structural_attack',method='Independent literal permutation derivation, direct equation reconstruction, full raw row-combination checking, alternate column rank and corruption controls.',
            artifact_availability='LOCAL_ONLY',availability_reason='This review checks workspace bytes; publication is controlled separately by the root agent.',
            external_review=None,external_review_reason='No external reviewer or peer review asserted.',
            limitations=['No all-parity, all-balanced-support, core or unrestricted target exclusion.','The previously produced240-option CNF was not solved or used as a premise.'],
            created_at=datetime.now(timezone.utc).isoformat(),updated_at=datetime.now(timezone.utc).isoformat(),inputs_sha256=pins,evidence_sha256=output_hashes)
        save(out/'claim_binding.json',claim)
        save(out/'summary.json',dict(status='INDEPENDENT_SELECTED_PARITY_GF3_PHASE_EXCLUSION_PASS',timestamp=datetime.now(timezone.utc).isoformat(),
            claim_id=claim['id'],claim_revision=1,inputs_sha256=pins,outputs_sha256={key(p):h(p)for p in out.iterdir()if p.is_file()},
            variables=120,equations=180,rank=119,nullity=1,all_required_nonzero_functionals_checked=420,raw_row_combination_identities=420,
            corrupted_cases_rejected=len(rejected),elapsed_seconds=elapsed,solver_calls=0,producer_code_imported=False,
            target_resolution='UNKNOWN',external_review=False,scope=claim['scope']))
        print(json.dumps(dict(status='INDEPENDENT_SELECTED_PARITY_GF3_PHASE_EXCLUSION_PASS',rank=119,nullity=1,checked_obstructions=420,corruptions=len(rejected),seconds=elapsed)))
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),source_sha256=h(__file__),elapsed_seconds=time.monotonic()-start,claim_approved=False));raise
if __name__=='__main__':main()
