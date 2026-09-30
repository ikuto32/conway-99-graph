"""Independent all-quartet Gram-determinant and exact-four-margin audit."""
from collections import Counter,defaultdict
from datetime import datetime,timezone
from itertools import combinations,permutations,product
from pathlib import Path
import argparse,copy,hashlib,json,platform,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results';D=B/'20260930_hadamard_four_group_circuits';RAW=B/'20260930_hadamard20_support/six_prism.json';MARGINAL=B/'20260930_independent_review/hadamard_few_exception_marginals/summary.json'
PINS={D/'summary.json':'fdc3269c8ca6147a0abaa2e2c06796c249bcdff3b8a9010639d30e494efb6265',RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',MARGINAL:'6b9512567a77ef3bad2fbb1b581fadb30c486c9ac4151543001705776e0c5df9',MARGINAL.parent/'claim_bindings.json':'98b3f7206ec559fd16a0e531608954981150e85ff71274f82466b9cfecbffe4d'}
def need(x,m):
    if not x:raise ValueError(m)
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def save(p,x):
    with Path(p).open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
def same(a,b):return json.dumps(a,sort_keys=True)==json.dumps(b,sort_keys=True)
def bareiss(matrix):
    n=len(matrix);need(n and all(len(r)==n for r in matrix),'square determinant')
    a=[r[:] for r in matrix];previous=1;sign=1
    for k in range(n-1):
        pivot=next((i for i in range(k,n) if a[i][k]),None)
        if pivot is None:return 0
        if pivot!=k:a[pivot],a[k]=a[k],a[pivot];sign=-sign
        value=a[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                numerator=a[i][j]*value-a[i][k]*a[k][j]
                need(numerator%previous==0,'exact Bareiss division');a[i][j]=numerator//previous
        for i in range(k+1,n):a[i][k]=0
        previous=value
    return sign*a[-1][-1]
def leibniz(a):
    n=len(a);total=0
    for p in permutations(range(n)):
        value=(-1)**sum(p[i]>p[j] for i in range(n) for j in range(i+1,n))
        for i in range(n):value*=a[i][p[i]]
        total+=value
    return total
def gram(a):return [[sum(r[i]*r[j] for r in a) for j in range(len(a[0]))] for i in range(len(a[0]))]
def split_relation(columns,ids):
    answers=[]
    for other in ids[1:]:
        pos=[ids[0],other];neg=[i for i in ids if i not in pos]
        if all(columns[pos[0]][a]+columns[pos[1]][a]==columns[neg[0]][a]+columns[neg[1]][a] for a in range(len(columns[0]))):answers.append((pos,neg))
    need(len(answers)<=1,'unique equal-pair split for distinct points')
    if not answers:return None
    p,q=answers[0];return dict(positive_pair=p,negative_pair=q,relation=[1 if i in p else -1 for i in ids],pair_sum=[x+y for x,y in zip(columns[p[0]],columns[p[1]])])
def classify(a,relation):
    G=gram(a);d=bareiss(G);need(d>=0,'Gram determinant nonnegative')
    if d:
        need(relation is None,'no kernel on independent columns');return dict(rank=4,Gram_determinant=d)
    need(relation is not None and all(sum(x*y for x,y in zip(row,relation))==0 for row in a),'literal four-column null relation')
    g3=[[G[i][j] for j in range(3)] for i in range(3)];d3=bareiss(g3);need(d3>0,'rank at least3')
    return dict(rank=3,Gram_determinant=0,first_three_Gram_determinant=d3,relation=relation)
def certificate(cert,a,expected_rank):
    need(cert['rank']==expected_rank,'claimed exact rank')
    if expected_rank==3:
        relation=cert['relation'];need(len(relation)==4 and set(relation)=={-1,1} and relation.count(1)==2,'primitive rectangle coefficient pattern')
        need(all(sum(x*y for x,y in zip(row,relation))==0 for row in a),'literal certificate relation')
    else:
        rows=cert['rows'];need(len(rows)==4 and len(set(rows))==4 and all(type(i)is int and 0<=i<len(a) for i in rows),'four legal minor rows')
        minor=[a[i] for i in rows];need(cert['minor']==minor,'minor raw entries')
        d=leibniz(minor);need(d!=0 and cert['determinant']==d,'independent Leibniz minor certificate')
def controls():
    totals=[]
    for n in [3,4]:
        points=list(product(range(2),repeat=n));count=0;dependent=0
        for ids in combinations(range(len(points)),4):
            a=[[1]*4]+[[points[i][j] for i in ids] for j in range(n)]
            rel=split_relation(points,ids);check=classify(a,rel['relation'] if rel else None)
            need(bareiss(gram(a))==leibniz(gram(a)),'two determinant paths in cube controls')
            dependent+=check['rank']==3;count+=1
        totals.append(dict(cube_dimension=n,quartets=count,circuits=dependent))
    need(len(set([(0,0),(0,0),(1,0),(0,1)]))<4,'duplicates outside theorem')
    # Four nonbinary collinear points need not form an equal-pair-sum rectangle.
    nonbinary=[(0,),(1,),(2,),(4,)];need(split_relation(nonbinary,(0,1,2,3)) is None and bareiss(gram([[1]*4,[0,1,2,4]]))==0,'binary premise counterexample')
    return totals
def margin_witness(ids,rel,common,groups):
    need(len(common)>=2,'two common coordinates required')
    a,b=common[:2];z=[[0]*3 for _ in range(12)];z[a]=[1,-1,0];z[b]=[-1,1,0]
    delta=[[[0]*3 for _ in range(12)] for _ in range(20)]
    for g,c in zip(ids,rel):
        for x in range(12):delta[g][x]=[c*v for v in z[x]]
    need([g for g in range(20) if any(v for row in delta[g] for v in row)]==list(ids),'exactly four nonzero formal groups')
    for g in range(20):
        need(all(sum(delta[g][x][f] for x in range(12))==0 for f in range(3)),'group fibre quota deviation zero')
        for x in range(12):
            need(sum(delta[g][x])==0,'coordinate sum zero')
            need(x in groups[g] or delta[g][x]==[0,0,0],'supported deviations')
            need(all(0<=1+v<=3 for v in delta[g][x]),'integer coordinate count bounds')
    for x in range(12):
        for f in range(3):
            need(sum(delta[g][x][f] for g in range(20))==0,'row margin')
            for y in range(12):
                if y in [x,x^1]:continue
                need(sum(delta[g][x][f] for g in range(20) if y in groups[g])==0,'all full-Gram marginal identities')
    return dict(groups=list(ids),relation=rel,common_support=common,z=z,scope='Formal integer deviation/count-margin witness only; no binary factor or local triple realization claimed.')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.perf_counter();pins={}
    def pin(p,h=None):
        p=p.resolve();v=sha(p);need(h is None or h==v,'input identity '+key(p));pins[key(p)]=v
    try:
        for p,h in PINS.items():pin(p,h)
        summary=read(D/'summary.json')
        for p,h in {**summary['inputs_sha256'],**summary['outputs_sha256']}.items():pin(ROOT/p,h)
        marginal=read(MARGINAL);need(marginal['status']=='INDEPENDENT_HADAMARD_FEW_EXCEPTION_MARGINALS_PASS','separate sparse-marginal theorem gate')
        need(marginal['inputs_sha256'][key(RAW)]==PINS[RAW],'same exact marginal support')
        bindings=read(MARGINAL.parent/'claim_bindings.json');need(any(x['id']=='C-FIXED-HADAMARD-AT-MOST-THREE-EXCEPTIONS-IMPLIES-BALANCED' and x['revision']==1 for x in bindings),'exact sparse theorem claim ID')
        L=read(RAW)['L'];groups=[]
        for d in range(60):
            s=[i for i in range(12) if L[i][d]]
            if s not in groups:groups.append(s)
        need(len(groups)==20 and len(set(map(tuple,groups)))==20,'twenty distinct supports')
        columns=[[int(a in s) for a in range(12)] for s in groups]
        raw_pairs=read(D/'pair_sums.json');sums=defaultdict(list)
        for i,j in combinations(range(20),2):sums[tuple(a+b for a,b in zip(columns[i],columns[j]))].append([i,j])
        expected_pairs=dict(groups=groups,records=[dict(sum=list(s),pairs=ps) for s,ps in sorted(sums.items())],unordered_pairs=190)
        need(same(raw_pairs,expected_pairs),'all190 literal pair sums')
        raw_quartets=read(D/'all_quartets.json');need(raw_quartets['complete_population']==4845 and len(raw_quartets['records'])==4845,'complete quartet population')
        checks=[];circuits=[];lookup={}
        for ids,record in zip(combinations(range(20),4),raw_quartets['records'],strict=True):
            need(record['groups']==list(ids),'complete unique lex quartet coverage')
            matrix=[[1]*4]+[[columns[g][r] for g in ids] for r in range(12)]
            relation=split_relation(columns,ids);c=classify(matrix,relation['relation'] if relation else None);certificate(record['certificate'],matrix,c['rank'])
            checks.append(dict(groups=list(ids),**c));lookup[ids]=c
            if relation:
                common=sorted(set.intersection(*(set(groups[g]) for g in ids)));union=sorted(set.union(*(set(groups[g]) for g in ids)))
                circuits.append(dict(groups=list(ids),**relation,common_support=common,union_support=union,local_margin_can_sustain_nonzero_deviation=len(common)>=2))
        need(read(D/'circuits.json')['records']==circuits,'all exact circuit/intersection records')
        raw_coord=read(D/'coordinate_marginal_quartets.json');need(raw_coord['complete_population']==2520 and len(raw_coord['records'])==2520,'coordinate quartet population')
        index=0;coord_counts=Counter()
        for x in range(12):
            containing=[g for g,s in enumerate(groups) if x in s];other=[y for y in range(12) if y not in [x,x^1]]
            need(len(containing)==10,'ten incident support groups')
            for ids in combinations(containing,4):
                record=raw_coord['records'][index];index+=1
                need(record['coordinate']==x and record['groups']==list(ids) and record['other_coordinates']==other,'coordinate quartet scope')
                matrix=[[1]*4]+[[columns[g][y] for g in ids] for y in other]
                c=classify(matrix,lookup[ids].get('relation'));certificate(record['certificate'],matrix,c['rank'])
                need(c['rank']==lookup[ids]['rank'],'coordinate/global column-relation equivalence');coord_counts[c['rank']]+=1
        hist=Counter(len(c['common_support']) for c in circuits)
        need(hist==Counter({1:7,2:13,3:1}) and len(circuits)==21 and len(sums)==170,'derived finite results')
        for field,value in [('quartets',4845),('coordinate_quartets',2520),('affine_circuits',21),('distinct_pair_sums',170),('circuits_not_eliminated_by_local_margins',14)]:need(summary[field]==value,'producer reported count '+field)
        witnesses=[margin_witness(c['groups'],c['relation'],c['common_support'],groups) for c in circuits if len(c['common_support'])>=2]
        rejected=[]
        def reject(name,fn):
            try:fn()
            except(ValueError,IndexError,KeyError,TypeError):rejected.append(name)
            else:raise ValueError('accepted corruption '+name)
        independent=next(r for r in raw_quartets['records'] if r['certificate']['rank']==4);ids=independent['groups'];matrix=[[1]*4]+[[columns[g][r] for g in ids] for r in range(12)]
        bad=copy.deepcopy(independent['certificate']);bad['determinant']+=1;reject('wrong_minor_determinant',lambda:certificate(bad,matrix,4))
        bad=copy.deepcopy(independent['certificate']);bad['minor'][0][0]^=1;reject('changed_minor_entry',lambda:certificate(bad,matrix,4))
        dep=next(r for r in raw_quartets['records'] if r['certificate']['rank']==3);ids=dep['groups'];matrix2=[[1]*4]+[[columns[g][r] for g in ids] for r in range(12)]
        bad=copy.deepcopy(dep['certificate']);bad['relation'][0]*=-1;reject('wrong_relation',lambda:certificate(bad,matrix2,3))
        bad=copy.deepcopy(circuits);bad[0]['common_support'].append(11);reject('changed_intersection',lambda:need(bad==circuits,'literal common intersection'))
        reject('missing_quartet',lambda:need(len(raw_quartets['records'][:-1])==4845,'complete coverage'))
        reject('missing_coordinate_case',lambda:need(len(raw_coord['records'][:-1])==2520,'complete coordinate coverage'))
        reject('false_zero_or_three_intersections',lambda:need(len(set(groups[0])&set(groups[1])) in[0,3],'raw refuted premise'))
        finite_controls=controls();save(out/'controls.json',dict(cube_controls=finite_controls,corruptions_rejected=rejected,refuted_intersection_control=dict(groups=[0,1],intersection=sorted(set(groups[0])&set(groups[1])))))
        save(out/'independent_Gram_determinants.json',dict(records=checks,coordinate_rank_counts=dict(coord_counts)))
        save(out/'independent_circuits.json',dict(records=circuits,retained_quartets=[c['groups'] for c in circuits if len(c['common_support'])>=2],excluded_singleton_quartets=[c['groups'] for c in circuits if len(c['common_support'])==1]))
        save(out/'formal_margin_witnesses.json',dict(records=witnesses,scope='Necessary linear/count margins only; no F construction.'))
        pin(Path(__file__));pin(ROOT/'docs/AUDIT_20260930_HADAMARD_FOUR_GROUP_CIRCUITS.md');ts=datetime.now(timezone.utc).isoformat()
        save(out/'manifest.json',dict(timestamp=ts,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,elapsed_seconds=time.perf_counter()-start,solver_calls=0))
        binding=dict(id='C-FIXED-HADAMARD-FOUR-GROUP-CIRCUIT-NECESSITY',revision=1,kind='mathematical result',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',statement='The20frozen support columns have exactly21affinely dependent four-element subsets, each a rank3equal-pair-sum circuit with primitive coefficients(1,1,-1,-1); their common-support sizes are1:7,2:13,3:1. Any prescribed-Gram factor on this fixed support with exactly four unbalanced groups must use one of the14saved circuit quartets with common support of size at least2, and its deviations are the circuit signs times a common coordinate/fibre array supported in that intersection.',scope='Complete finite support census and a necessary condition for exactly four exceptional groups only; none of the14retained quartets is claimed realizable.',assumptions=['Literal fixed six-prism Hadamard coordinate support.','BinaryF with prescribed full integer Gram for the exact-four-group implication.','Unbalanced means nonzero coordinate/fibre deviation within a triplicate-support group.'],dependencies=[dict(id='C-FIVE-FIXED-HADAMARD20-SUPPORT-PROJECTIONS',revision=1,relation='premise'),dict(id='C-FIXED-HADAMARD-AT-MOST-THREE-EXCEPTIONS-IMPLIES-BALANCED',revision=1,relation='uses_result')],verifier='/root/structural_attack',producer='/root/state_literature_audit',discovery_contributor='/root',method='Independent fraction-free Gram determinants for every quartet, separate Leibniz verification of every raw minor, exact relation/intersection reconstruction, and written cube-circuit/marginal derivation.',shared_components=['Raw support and saved producer certificates; no producer source imports.','Previously separately reviewed sparse marginal theorem and Python exact integer primitives.'],inputs_sha256=pins,evidence_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},artifact_availability='LOCAL_ONLY',availability_reason='Workspace artifacts pending parent publication.',external_review=None,external_review_reason='No external peer review asserted.',limitations=['No simultaneous local-triple, full-Gram or residual realization of any retained quartet.','No full-support/core/unrestricted-target exclusion.','The refuted0-or3 intersection premise is unused.','No balanced UNSAT replay is repeated or required for this exact-four-group conditional statement.'],created_at=ts,updated_at=ts)
        save(out/'claim_binding.json',binding)
        result=dict(status='INDEPENDENT_HADAMARD_FOUR_GROUP_CIRCUIT_NECESSITY_PASS',timestamp=ts,inputs_sha256=pins,outputs_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},global_quartets=4845,coordinate_quartets=2520,pair_sums=190,distinct_pair_sums=170,circuits=21,common_support_histogram=dict(hist),retained_necessary_quartets=14,formal_margin_witnesses=14,controls=finite_controls,corruptions_rejected=len(rejected),solver_calls=0,target_resolution=False)
        save(out/'summary.json',result);print(json.dumps(dict(status=result['status'],summary_sha256=sha(out/'summary.json'),claim_binding_sha256=sha(out/'claim_binding.json'))))
    except BaseException as ex:save(out/'failure.json',dict(error=repr(ex)));raise
if __name__=='__main__':main()
