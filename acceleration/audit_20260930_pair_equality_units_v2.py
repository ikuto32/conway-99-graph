"""Independent raw-polynomial and threshold-unit checking; no producer imports."""
from datetime import datetime,timezone
from hashlib import sha256
import copy,gzip,itertools,json,platform,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
B=ROOT/'acceleration/results'
D=B/'20260930_unrestricted_pair_equalities/run01'
BASE=B/'20260930_unrestricted_full99_cnf'
GATE=B/'20260930_independent_review/unrestricted_full99_cnf/summary.json'
OUT=B/'20260930_independent_review/unrestricted_pair_equalities_v2'
def h(p):return sha256(Path(p).read_bytes()).hexdigest()
def save(p,v):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(v,f,indent=2);f.write('\n')
def check_row(row,expected):
    for field,value in expected.items():assert row[field]==value,(row['pair'],field)
def main():
    OUT.mkdir(exist_ok=False)
    assert h(GATE)=='2d6702d0f60341378fcf6b5b0808e6c34ea6a1025775cfae60500626f199ef58'
    gate=json.loads(GATE.read_bytes());assert gate['status']=='INDEPENDENT_UNRESTRICTED_FULL99_CNF_ENCODING_PASS'
    for p,digest in gate['inputs_sha256'].items():assert h(ROOT/p)==digest,p
    model=BASE/'model.json';cnf=BASE/'instance.cnf';m=json.loads(model.read_bytes());a=m['known_adjacency_full99']
    edges={tuple(sorted((e['u'],e['v']))):e['id']for e in m['edge_variables']}
    assert set(edges)==set(itertools.combinations(range(15,99),2)) and len(set(edges.values()))==3486
    def ref(i,j):
        key=tuple(sorted((i,j)))
        return ('v',edges[key]) if key in edges else ('c',a[i][j])
    products={(p['pair'][0],p['pair'][1],p['center']):p for p in m['product_variables']}
    assert len(products)==len(m['product_variables'])==285852
    rows_path=D/'rows.jsonl';rows=[json.loads(line)for line in rows_path.read_text().splitlines()]
    assert gzip.decompress((D/'rows.jsonl.gz').read_bytes())==rows_path.read_bytes()
    pairs=list(itertools.combinations(range(99),2));assert len(rows)==len(pairs)==4851
    units=[];unit_pairs=[];taut=0;product_count=0;first=None
    for index,((u,v),row) in enumerate(zip(pairs,rows),99):
        known=[];linear=[];quadratic=[];inputs=[]
        for w in range(99):
            if w in (u,v):continue
            l,r=ref(u,w),ref(w,v)
            if ('c',0) in (l,r):continue
            if l[0]==r[0]=='c':
                assert l[1]==r[1]==1;known.append(['common',w])
            elif l[0]==r[0]=='v':
                p=products[(u,v,w)];assert (p['left'],p['right'])==(l[1],r[1])
                quadratic.append([p['id'],w,l[1],r[1]]);inputs.append(p['id']);product_count+=1
            else:
                variable=l[1] if l[0]=='v' else r[1]
                linear.append([variable,w,'left_fixed_one' if l[0]=='c' else 'right_fixed_one']);inputs.append(variable)
        edge=ref(u,v)
        if edge==('c',1):known.append(['adjacency',u,v])
        elif edge[0]=='v':linear.append([edge[1],None,'adjacency']);inputs.append(edge[1])
        counter=m['counter_rows'][index]
        assert counter['kind']=='pair_cap' and counter['pair']==[u,v] and not counter['equality']
        assert counter['original_bound']==2 and counter['constant']==len(known) and counter['inputs']==inputs
        residual=2-len(known);n=len(inputs)
        states={(i,j):value for i,j,value in counter['states']}
        assert len(states)==len(counter['states'])
        if residual<=0:final=True
        elif residual>n:final=False
        else:final=states[n,residual]
        assert final is not False,'Unexpected contradiction; retain as candidate and halt.'
        if final is True:decision='TAUTOLOGY';unit=None;taut+=1
        else:
            assert type(final)is int and 1<=final<=m['variables'];decision='UNIT';unit=final
            units.append(unit);unit_pairs.append({'literal':unit,'pairs':[[u,v]]})
        expected={'pair':[u,v],'counter_row_index':index,'constant':len(known),'constant_contribution_witnesses':known,
            'polynomial_input_variables':inputs,'linear_terms':linear,'quadratic_terms':quadratic,'original_exact_residual':residual,
            'encoded_upper_bound':counter['bound'],'input_count':n,'final_threshold_index':[n,residual],'final_threshold_reference':final,
            'decision':decision,'unit_literal':unit,'upper_row_first_clause':counter['first_clause'],'upper_row_clause_count':counter['clause_count']}
        check_row(row,expected)
        if first is None and unit is not None:first=(row,expected)
    assert taut==189 and product_count==285852 and len(units)==len(set(units))==4662
    saved=json.loads((D/'units.json').read_bytes())
    assert saved['units']==units and saved['unit_to_pairs']==unit_pairs and saved['contradictions']==[] and not saved['contradiction_clause_added']
    suffix=''.join(str(x)+' 0\n'for x in units).encode('ascii');assert suffix==(D/'pair_equalities.units.cnfpart').read_bytes()
    digest=sha256();digest.update(b'p cnf 1186500 4141116\n')
    with cnf.open('rb')as f:
        assert f.readline()==b'p cnf 1186500 4136454\n'
        for block in iter(lambda:f.read(1048576),b''):digest.update(block)
    digest.update(suffix)
    summary=json.loads((D/'summary.json').read_bytes());assert digest.hexdigest()==summary['future_augmented_cnf_sha256']=='b7aed200d2fdc13c45e3a218a7f80702bae16de0a82670070206254a88ee7986'
    controls=0
    for n in range(7):
        for bits in itertools.product((0,1),repeat=n):
            for k in range(n+2):
                t=lambda j:sum(bits)>=j
                assert ((not t(k+1)) and t(k))==(sum(bits)==k);controls+=1
    assert 99*14//2==693 and 99*(14*13//2)+693==2*4851==9702
    corruptions=[];row,expected=first
    for name,field,value in [('wrong_constant','constant',row['constant']+1),('wrong_residual','original_exact_residual',row['original_exact_residual']+1),
        ('wrong_threshold','final_threshold_reference',row['final_threshold_reference']+1),('negative_unit','unit_literal',-row['unit_literal']),
        ('wrong_pair','pair',[0,1]),('missing_polynomial_term','polynomial_input_variables',row['polynomial_input_variables'][:-1])]:
        bad=copy.deepcopy(row);bad[field]=value
        try:check_row(bad,expected)
        except AssertionError:corruptions.append(name)
        else:raise AssertionError(name)
    assert suffix!=suffix.replace(str(units[0]).encode(),str(-units[0]).encode(),1)
    paths=[Path(__file__),GATE,model,cnf,D/'manifest.json',D/'summary.json',D/'rows.jsonl',D/'rows.jsonl.gz',D/'units.json',D/'pair_equalities.units.cnfpart',ROOT/'uv.lock']
    report={'timestamp':datetime.now(timezone.utc).isoformat(),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        'command':[sys.executable,*sys.argv],'cwd':str(ROOT),'python':platform.python_version(),
        'status':'INDEPENDENT_UNRESTRICTED_PAIR_EQUALITY_UNITS_PASS','recommendation':'VERIFIED','claim_id':'C-UNRESTRICTED-PAIR-EQUALITY-UNITS','claim_revision':1,
        'kind':'encoding','basis':['DERIVED','COMPUTED'],'verifier':'/root independent raw-artifact and entailment checking path',
        'statement':'Every satisfying assignment of the exact unrestricted prefix CNF satisfies all4662 recorded positive threshold units. Appending their exact suffix gives an equivalent CNF with1186500variables and4141116clauses, whose satisfiability is equivalent to unrestricted target existence.',
        'scope':'Exact raw unrestricted CNF plus this suffix only. Entailed equality constraints, with no extra graph assumptions or solver result.',
        'dependencies':[{'id':'C-UNRESTRICTED-FULL99-PREFIX-CNF-ENCODING','revision':1,'relation':'encoding_equivalence'}],
        'inputs_sha256':{p.relative_to(ROOT).as_posix():h(p)for p in paths},'base_cnf_sha256':h(cnf),'model_sha256':h(model),'suffix_sha256':h(D/'pair_equalities.units.cnfpart'),
        'augmented_cnf_sha256':digest.hexdigest(),'variables':1186500,'clauses':4141116,'base_clauses':4136454,'unit_literals':units,
        'counts':{'pair_rows':4851,'tautologies':189,'units':4662,'duplicates':0,'contradictions':0,'product_terms':285852},
        'derivation':'For a symmetric binary degree14 matrix, the sum over unordered pairs of common-neighbor counts is99*C(14,2)=9009; the sum of adjacency is693. Thus all4851 pair polynomials A_ij+(A^2)_ij sum to9702. Each encoded upper cap is at most2, so every integer slack is zero. For each fully reconstructed raw polynomial with c constant terms, its true variable-input sum is exactly2-c. The already independently checked bidirectional product and threshold gates make its final threshold at2-c true.189 such thresholds are Boolean tautologies;4662 are positive variables. Their units are logical consequences, so adjoining them changes no satisfying graph or full auxiliary assignment.',
        'controls':{'exhaustive_small_counter_assignments':controls,'rejected_row_corruptions':corruptions,'negative_suffix_control_rejected':True,'raw_gzip_identity':True},
        'shared_components':['Python standard library exact integers','Frozen independent full-CNF gate reused as an explicit premise for threshold/product equivalence; its producer is not imported.'],
        'limitations':['Propagation or runtime improvement has not been measured.','No solver call or SAT/UNSAT result is established.','Full threshold truth-table clause checking is reused from the pinned complete encoding audit, not described as a second independent implementation.','No target resolution or external review.']}
    save(OUT/'summary.json',report)
    print(json.dumps({'status':report['status'],'sha256':h(OUT/'summary.json'),'units':len(units)}))
if __name__=='__main__':main()
