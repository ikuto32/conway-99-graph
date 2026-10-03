"""Independent S3 classification, complete parity CNF and raw object checker."""
from collections import Counter
from copy import deepcopy
from datetime import datetime,timezone
from itertools import combinations,permutations,product
from pathlib import Path
import argparse,hashlib,json,platform,subprocess,sys

ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';D=B+'hadamard_balanced_parity/';I=B+'independent_review/'
MODEL=D+'model.json';CNF=D+'instance.cnf';RAW=B+'hadamard20_support/six_prism.json'
PINS={MODEL:'a75b60c4ef0f8decd7537d70cced7bffa14cb7a4881de726bf98c96635888147',CNF:'92801921a62236effa19b0f6e7463c6f5c1ca2cb0b6957cf7d315a73e0e43fca',D+'summary.json':'b229ec37afa765713362df943f97eec72d85e27c77bf109a48a8267eddeb9eee',RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',I+'hadamard_triplicate_counts_v2/summary.json':'cb9f1c7f8cfe0db557f554ded5427a9cba46dda10dcd9b5df9968e1d3b776f88',I+'hadamard_cyclic_unsat/summary.json':'83029350b25523c015dfe916d8056324c0970021d2b024d68941dd41fb8c2b70',I+'hadamard_six_prism_cyclic_reduction/summary.json':'7b9d988b946284d7a9fbcccccf1c2f32592dbdeb2e30cb6201e1565ea75d4de1'}
def need(v,msg):
    if not v:raise ValueError(msg)
def h(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
def sign(p):
    visited=set();cycles=0
    for i in range(3):
        if i in visited:continue
        cycles+=1;j=i
        while j not in visited:visited.add(j);j=p[j]
    return (3-cycles)%2
def classification(raw,saved,local):
    ps=list(permutations(range(3)));bits=[sign(p) for p in ps]
    cells=[{(i,p[i]) for i in range(3)} for p in ps]
    intersections=[]
    for e in range(6):
        for o in range(6):
            if bits[e]==0 and bits[o]==1:
                common=cells[e]&cells[o];need(len(common)==1,'even/odd cell intersection');intersections.append([e,o,list(next(iter(common)))])
    need(len({tuple(r[2]) for r in intersections})==9,'all nine cell equations')
    six=Counter();five=Counter();tuples6=[];tuples5=[];quotient={};transports=[]
    worddomain=sorted({tuple(0 if i in a else 1 if i in b else 2 for i in range(6)) for a in combinations(range(6),2) for b in combinations([i for i in range(6) if i not in a],2)})
    need(len(worddomain)==90,'independent balanced domain')
    wordindex={w:i for i,w in enumerate(worddomain)}
    for indices in product(range(6),repeat=6):
        coord=[ps[j] for j in indices]
        if any(sum(p[r]==g for p in coord)!=2 for r in range(3) for g in range(3)):continue
        count=tuple(indices.count(j) for j in range(6));six[count]+=1;tuples6.append(list(indices))
        words=[tuple(coord[i][r] for i in range(6)) for r in range(3)]
        triple=tuple(sorted(wordindex[w] for w in words));need(len(set(triple))==3,'free three-column action')
        sortedcoord=[tuple(worddomain[t][i] for t in triple) for i in range(6)]
        s=[sign(p) for p in sortedcoord];gauge=tuple(x^s[0] for x in s);quotient[triple]=gauge
        if len(set(bits[j] for j in indices))==1:
            inverse=[coord[0].index(r) for r in range(3)]
            c=[p[inverse[0]] for p in coord]
            need(c[0]==0 and all(p[inverse[r]]==(c[i]+r)%3 for i,p in enumerate(coord) for r in range(3)),'complete cyclic normalization')
            transports.append(dict(coordinate_permutation_indices=list(indices),old_column_by_new=inverse,base_colours=c))
    for indices in product(range(6),repeat=5):
        if any(sum(ps[j][r]==g for j in indices)!=2-int(r==g) for r in range(3) for g in range(3)):continue
        count=tuple(indices.count(j) for j in range(6));five[count]+=1;tuples5.append(list(indices))
        need(sum(bits[j] for j in indices) in (0,3),'complete relative parity implication')
    expected_six={tuple(alpha if bits[j]==0 else 2-alpha for j in range(6)) for alpha in range(3)}
    ididx=ps.index((0,1,2));expected_five={tuple(t if j==ididx else 1-t if bits[j] else 1+t for j in range(6)) for t in range(2)}
    need(set(six)==expected_six and set(five)==expected_five,'exact symbolic multiplicity classification')
    need(len(tuples6)==900 and len(tuples5)==150 and len(quotient)==150 and len(transports)==180,'ordered finite populations')
    patterns=[(0,)*6]+[p for p in product(range(2),repeat=6) if p[0]==0 and sum(p)==3]
    histogram=Counter(patterns.index(p) for p in quotient.values());need(histogram==Counter({0:30,**{i:12 for i in range(1,11)}}),'complete parity profile counts')
    need(saved['permutations']==[list(p) for p in ps] and saved['parities']==bits,'permutation identities')
    need(saved['six_multisets_examined']==462 and saved['five_multisets_examined']==252,'producer multiset universe sizes')
    need({tuple(c) for c in saved['six_matrix_profiles']}==set(six) and {tuple(c) for c in saved['five_matrix_profiles']}==set(five),'all producer profile identities')
    need(sorted(map(list,quotient))==local['balanced'],'independently generated balanced triples')
    need(saved['parity_pattern_counts']=={str(k):v for k,v in histogram.items()},'producer histogram')
    for record in saved['balanced_local_triples']:
        triple=tuple(record['triple']);words=[worddomain[j] for j in triple];coord=[tuple(w[i] for w in words) for i in range(6)]
        need(record['coordinate_permutations']==[list(p) for p in coord] and record['permutation_multiplicities']==[coord.count(p) for p in ps],'each saved local permutation record')
        need(record['parity_pattern']==list(quotient[triple]) and record['kind']==('cyclic' if quotient[triple]==(0,)*6 else 'mixed'),'each saved parity record')
    need(len(saved['balanced_local_triples'])==150 and len({tuple(x['triple']) for x in saved['balanced_local_triples']})==150,'complete producer local population')
    # Bind the literal fixed core and target Gram used in the necessity proof.
    c=raw['core_adjacency'];need(len(c)==36 and all(len(r)==36 for r in c),'core dimensions')
    for i in range(36):
        for j in range(36):
            expect=int((i//12==j//12 and i%12==(j%12)^1) or (i//12!=j//12 and i%12==j%12))
            need(c[i][j]==expect,'literal six-prism core')
            target=12*int(i==j)+2-c[i][j]-sum(c[i][k]*c[k][j] for k in range(36))-int(i//12==j//12)
            need(raw['prescribed_Gram36'][i][j]==target,'raw exact Gram')
    return dict(permutations=[list(p) for p in ps],parities=bits,cell_intersections=intersections,ordered_six_tuples=tuples6,ordered_five_tuples=tuples5,cyclic_transports=transports,parity_histogram=dict(histogram)),patterns
def reconstruct(raw,model):
    supports=[[a for a in range(12) if raw['L'][a][d]] for d in range(60)];groups=[]
    for s in supports:
        if s not in groups:groups.append(s)
    need(len(groups)==20 and all(supports.count(s)==3 for s in groups),'exact triplicate groups')
    need(all(len(s)==6 and len({a//2 for a in s})==6 for s in groups),'six distinct matching pairs per support')
    patterns=[[0]*6]+[list(p) for p in product(range(2),repeat=6) if p[0]==0 and sum(p)==3]
    expected_groups=[];clauses=[]
    for g,s in enumerate(groups):
        ids=list(range(11*g+1,11*g+12));clauses.append(ids)
        for a,b in combinations(ids,2):clauses.append([-a,-b])
        expected_groups.append(dict(group=g,support=s,selectors=ids,parity_patterns=patterns))
    pairrows=[];var=220
    for a,b in combinations(range(12),2):
        if a//2==b//2:continue
        gs=[g for g,s in enumerate(groups) if a in s and b in s];need(len(gs)==5,'five raw cooccurrences')
        terms=[]
        for g in gs:
            ia=groups[g].index(a);ib=groups[g].index(b);ds=[11*g+1+i for i,p in enumerate(patterns) if p[ia]!=p[ib]]
            need(len(ds)==6,'six disagree selectors');var+=1
            for d in ds:clauses.append([-d,var])
            clauses.append([-var]+ds);terms.append(dict(group=g,difference_variable=var,disagree_selectors=ds))
        variables=[t['difference_variable'] for t in terms]
        for mask in range(32):
            bits=[(mask>>(4-i))&1 for i in range(5)]
            if sum(bits) not in (0,3):clauses.append([v if bit==0 else -v for v,bit in zip(variables,bits)])
        pairrows.append(dict(coordinates=[a,b],terms=terms,allowed_disagreement_counts=[0,3]))
    clauses.append([s for group in expected_groups for s in group['selectors'][1:]])
    need(model['schema']=='BALANCED_TRIPLET_PARITY_NECESSARY_CNF_V1' and model['groups']==expected_groups and model['pair_rows']==pairrows,'complete raw metadata reconstruction')
    need(model['variables']==var==520 and model['clauses']==len(clauses)==4481 and model['primary_selectors']==220,'CNF dimensions')
    need(model['requires_noncyclic_group'] is True and model['additional_balance_assumption'] is True and model['target_graph'] is False and model['residual_D'] is False,'explicit projection scope')
    return clauses,expected_groups,pairrows
def cnf_bytes(clauses,n=520):return ('p cnf '+str(n)+' '+str(len(clauses))+'\n'+''.join(' '.join(map(str,c))+' 0\n' for c in clauses)).encode('ascii')
def assignment(values,n):
    need(isinstance(values,list) and len(values)==n and all(type(v) is int and v!=0 and abs(v)<=n for v in values),'complete signed assignment domain')
    need({abs(v) for v in values}==set(range(1,n+1)),'unique all variable IDs')
    return {abs(v):v>0 for v in values}
def native(text,n):
    values=[];statuses=[];terminated=False
    for line in text.splitlines():
        if line.startswith('s '):statuses.append(line.strip())
        if not line.startswith('v '):continue
        for word in line[2:].split():
            v=int(word)
            if v==0:terminated=True;continue
            need(not terminated,'native literal after zero');values.append(v)
    need(statuses==['s SATISFIABLE'] and terminated,'native complete SAT record')
    return assignment(values,n)
def satisfied(clauses,values):return [i+1 for i,c in enumerate(clauses) if not any(values[abs(v)]==(v>0) for v in c)]
def projection(values,groups,pairs):
    indices=[];selectors=[];patterns=[];records=[]
    for g in groups:
        chosen=[i for i,v in enumerate(g['selectors']) if values[v]];need(len(chosen)==1,'exactly one selected pattern')
        i=chosen[0];p=g['parity_patterns'][i];indices.append(i);selectors.append(g['selectors'][i]);patterns.append(p)
        records.append(dict(group=g['group'],support=g['support'],selector=g['selectors'][i],pattern_index=i,parity_pattern=p,parity_mask_hex=hex(sum(v<<j for j,v in enumerate(p)))))
    need(any(indices),'at least one nonconstant group')
    counts=[]
    for pair in pairs:
        a,b=pair['coordinates'];total=0
        for t in pair['terms']:
            g=t['group'];s=groups[g]['support'];different=patterns[g][s.index(a)]!=patterns[g][s.index(b)]
            need(values[t['difference_variable']]==different,'raw OR output equality');total+=different
        need(total in (0,3),'literal parity projection relation');counts.append(dict(coordinates=[a,b],count=total))
    return dict(selected_group_selector_ids=selectors,selected_pattern_indices=indices,selected_group_parity_patterns=patterns,group_records=records,pair_disagreement_counts=counts,full_factor=False,target_graph=False,balance_is_additional_assumption=True,residual_D=None)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['audit','calibrate','sat']);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--encoding-gate');ap.add_argument('--encoding-gate-sha256');ap.add_argument('--assignment');ap.add_argument('--native-output');ap.add_argument('--decoded');a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};corrupt=[]
    def pin(p,expected=None):
        p=Path(p);p=p if p.is_absolute() else ROOT/p;v=h(p);need(expected is None or v==expected,'artifact identity '+str(p));pins[p.relative_to(ROOT).as_posix()]=v;return p
    def load(p,expected=None):return json.loads(pin(p,expected).read_bytes())
    def reject(label,fn):
        try:fn()
        except (ValueError,KeyError,IndexError,TypeError):corrupt.append(label)
        else:raise ValueError('corruption accepted '+label)
    try:
        for p,digest in PINS.items():pin(p,digest)
        producer=load(D+'summary.json')
        for p,digest in {**producer['inputs_sha256'],**producer['outputs_sha256']}.items():pin(p,digest)
        raw=load(RAW);model=load(MODEL);clauses,groups,pairs=reconstruct(raw,model)
        need((ROOT/CNF).read_bytes()==cnf_bytes(clauses),'all4481 exact clauses/bytes')
        # Exhaust all primitive relation truth tables independently.
        onehot=0
        for mask in range(2048):
            vals={i+1:bool(mask&(1<<i)) for i in range(11)};need((not satisfied(clauses[:56],vals))==(mask.bit_count()==1),'onehot full truth');onehot+=1
        for mask in range(128):
            values={i+1:bool(mask&(1<<i)) for i in range(7)};cs=[[-i,7] for i in range(1,7)]+[[-7,*range(1,7)]]
            need((not satisfied(cs,values))==(values[7]==any(values[i] for i in range(1,7))),'OR full truth')
        truthclauses=[]
        for bad in range(32):
            if bad.bit_count() not in (0,3):truthclauses.append([-i if bad&(1<<(i-1)) else i for i in range(1,6)])
        for mask in range(32):need((not satisfied(truthclauses,{i+1:bool(mask&(1<<i)) for i in range(5)}))==(mask.bit_count() in (0,3)),'weight full truth')
        for label,fn in [('short_assignment',lambda:assignment([1],520)),('duplicate_assignment',lambda:assignment([1]*520,520)),('zero_literal',lambda:assignment([0]+list(range(2,521)),520)),('bad_native_status',lambda:native('s UNSATISFIABLE\nv 1 0\n',1)),('native_missing_zero',lambda:native('s SATISFIABLE\nv 1\n',1)),('native_after_zero',lambda:native('s SATISFIABLE\nv 1 0 2\n',2))]:reject(label,fn)
        all_constant={i:False for i in range(1,521)}
        for g in groups:all_constant[g['selectors'][0]]=True
        need(satisfied(clauses,all_constant)==[4481],'real all-constant object fails only mixed clause')
        reject('all_constant_projection',lambda:projection(all_constant,groups,pairs))
        # A generic positive complete codec instance, explicitly not research SAT.
        synthetic=[i if i%2 else -i for i in range(1,521)];positive=assignment(synthetic,520)
        need(native('s SATISFIABLE\nv '+' '.join(map(str,synthetic))+' 0\n',520)==positive,'full520 native codec positive')
        need(not satisfied([[synthetic[j%520],-synthetic[j%520]] for j in range(4481)],positive),'synthetic4481 clause codec positive')
        bad=deepcopy(model);bad['groups'][0]['parity_patterns'][1][0]=1;reject('bad_pattern_metadata',lambda:reconstruct(raw,bad))
        bad=deepcopy(model);bad['pair_rows'][0]['terms'][0]['difference_variable']+=1;reject('bad_variable_metadata',lambda:reconstruct(raw,bad))
        bad=deepcopy(model);bad['additional_balance_assumption']=False;reject('missing_balance_premise',lambda:reconstruct(raw,bad))
        badclauses=deepcopy(clauses);badclauses[0][0]*=-1;reject('changed_clause',lambda:need(cnf_bytes(badclauses)==(ROOT/CNF).read_bytes(),'changed raw clause refused'))
        finite=None;result=None
        if a.mode=='audit':
            finite,_=classification(raw,load(D+'classification.json'),load(B+'hadamard_triplicate_counts/local_triples.json'))
            save(out/'ordered_classification_checks.json',finite)
        else:
            need(a.encoding_gate and a.encoding_gate_sha256,'required independent gate')
            gate=load(a.encoding_gate,a.encoding_gate_sha256);need(gate['status']=='INDEPENDENT_HADAMARD_BALANCED_PARITY_ENCODING_PASS','encoding gate status')
            for p in [CNF,MODEL]:need(gate['inputs_sha256'][p]==PINS[p],'gate exact formula')
            if a.mode=='sat':
                need(a.assignment and a.native_output,'raw actual SAT inputs')
                values=assignment(load(a.assignment)['assignment'],520);need(native(pin(a.native_output).read_text(),520)==values,'native/model assignment identity')
                need(not satisfied(clauses,values),'all actual research clauses')
                result=projection(values,groups,pairs);result['model_sha256']=PINS[MODEL]
                if a.decoded:
                    decoded=load(a.decoded)
                    for key,value in result.items():need(decoded.get(key)==value,'decoded raw projection field '+key)
                save(out/'independent_projection.json',result)
        for p in ['acceleration/audit_20260930_hadamard_balanced_parity.py','docs/AUDIT_20260930_HADAMARD_BALANCED_PARITY.md','uv.lock','pyproject.toml']:pin(p)
        status={'audit':'INDEPENDENT_HADAMARD_BALANCED_PARITY_ENCODING_PASS','calibrate':'INDEPENDENT_HADAMARD_BALANCED_PARITY_OBJECT_CHECKER_CALIBRATION_PASS','sat':'INDEPENDENT_HADAMARD_BALANCED_PARITY_SAT_OBJECT_PASS'}[a.mode]
        claim=dict(id='C-FIXED-HADAMARD-SIX-PRISM-BALANCED-PARITY-PROJECTION',revision=1,kind='encoding',basis=['DERIVED','COMPUTED'],recommendation='VERIFIED',review_state='CLEAR',statement='Every coordinatewise balanced prescribed-Gram factor on the exact saved six-prism support that also satisfies all outside-column overlap caps induces a satisfying assignment of the exact520-variable4481-clause parity formula: each group has one of11gauged parity patterns, all60five-group disagreement counts are0or3, and at least one group is mixed.',scope='Necessary projection only for the balanced fixed-support family WITH outside-column caps; SAT is not a factor and unbalanced factors remain outside its coverage.',dependencies=[dict(id='C-FIXED-HADAMARD-SIX-PRISM-LOCAL-TRIPLE-CENSUS',revision=1,relation='premise'),dict(id='C-FIXED-HADAMARD-SIX-PRISM-CYCLIC-FACTOR-EXCLUSION',revision=1,relation='uses_result'),dict(id='C-FIXED-HADAMARD-SIX-PRISM-CYCLIC-FIBRE-REDUCTION',revision=1,relation='normalization')])
        summary=dict(status=status,timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,outputs_sha256={p.relative_to(ROOT).as_posix():h(p) for p in out.glob('*.json')},counts=dict(variables=520,clauses=4481,onehot_truth_cases=onehot,OR_truth_cases=128,weight_truth_cases=32,ordered_six_universe=46656 if finite else None,ordered_five_universe=7776 if finite else None,valid_ordered_six=900 if finite else None,valid_ordered_five=150 if finite else None,unordered_balanced=150 if finite else None,cyclic_transports=180 if finite else None),corruptions=corrupt,claim=claim if a.mode=='audit' else None,verifier='/root/eight_domain_audit',scope='Exact semantic/encoding or raw parity-object verification according to mode; balance and fixed support are additional restrictions.',shared_components=['Python standard library only; no producer or other checker imports.','Existing independently checked cyclic exclusion supplies the nonconstant-group necessity premise.'],limitations=['No proof that the full Gram system forces coordinatewise balance.','No full36x60factor or residualD; SAT parity feasibility cannot construct a target graph.','UNSAT requires separate complete proof replay; no solver is called here.','The complete formula necessity invokes outside-column caps through the existing cyclic exclusion.'],artifact_availability='LOCAL_ONLY',target_resolution=False,solver_calls=0)
        save(out/'summary.json',summary);print(json.dumps(dict(status=status,sha256=h(out/'summary.json'))))
    except BaseException as exc:save(out/'failure.json',dict(error=repr(exc)));raise
if __name__=='__main__':main()
