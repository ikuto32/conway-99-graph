"""Fresh exact selected lift after the sixty-cut SAT projection; no optimizer."""
from collections import Counter
from datetime import datetime,timezone
from itertools import combinations,permutations,product
from pathlib import Path
import argparse,json,math,platform,subprocess,sys,time
from tqdm import tqdm
from theory_20260930_eight_full99_cnf import ResourceCap,digest,save

ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_'
RAW=B+'hadamard20_support/six_prism.json'
GROUPS=B+'independent_review/hadamard_six_prism_column_order/groups.json'
PROJECTION=B+'independent_review/hadamard_parity_support_cuts_sat/independent_projection.json'
GATE=B+'independent_review/hadamard_parity_support_cuts_sat/summary.json'
PINS={RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',
 GROUPS:'a3d8366a607bfd10787d4e879f8971c84ba5835b2b22c71ebfd081f55352f404',
 B+'independent_review/hadamard_six_prism_column_order/summary.json':'0ce1be9ca11a3e860aa97791cfb4f42c1660d937a69ac7a9b7d96ca37640c9d2',
 PROJECTION:'f43ad5f79d6fc8c8f6825f52d0140a07852a873207642b4edb7c035cb5ed4a8c',
 GATE:'02ae20d479a0d2589c02f435e2a8fdd781ec0459b60095d130b68b5f2721a04a',
 'acceleration/theory_20260930_eight_full99_cnf.py':'21c357543c9397456a911175b277da6e6caa769be31d18c12e034cc76d99074c',
 'acceleration/theory_20260930_full_srg_validator.py':'c0e070aa1ac39e8860b52a7f5e086b3e8da5e01f83d0f4fe76ab1e91c077279b',
 'uv.lock':'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',
 'pyproject.toml':'273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339'}
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(Path(p).read_bytes())
def need(ok,why):
    if not ok:raise ValueError(why)
def parity(words):
    signs=[]
    for k in range(6):
        p=[w[k]for w in words];need(sorted(p)==[0,1,2],'coordinate permutation')
        signs.append(sum(p[a]>p[b]for a,b in combinations(range(3),2))%2)
    return tuple(s^signs[0]for s in signs)
def residuals(columns,rhs,numerators,denominator):
    left=[0]*len(rhs)
    for col,numerator in zip(columns,numerators,strict=True):
        for r in col:left[r]+=numerator
    return [value-denominator*b for value,b in zip(left,rhs,strict=True)]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);cap=ResourceCap()
    try:
        need(all(digest(ROOT/p)==h for p,h in PINS.items()),'input pins');gate=read(ROOT/GATE)
        need(gate['status']=='INDEPENDENT_HADAMARD_PARITY_SUPPORT_CUT_SAT_OBJECT_PASS','actual new SAT object gate')
        need(gate['outputs_sha256'][PROJECTION]==PINS[PROJECTION],'independent raw projection hash binding')
        pins={**PINS,key(__file__):digest(__file__),key(Path(__file__).with_name('theory_20260930_hadamard_support_cut_lift_matrix_spec.md')):digest(Path(__file__).with_name('theory_20260930_hadamard_support_cut_lift_matrix_spec.md'))}
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),uv=subprocess.check_output(['uv','--version'],text=True).strip(),
            inputs_sha256=pins,selection='First completed independently checked SAT object of the60-cut parity formula; all20 saved patterns retained.',
            limits=dict(wall_seconds=30,memory_bytes=8*1024**3,solver_calls=0),independent_approval=False))
        raw=read(ROOT/RAW);projection=read(ROOT/PROJECTION);groups=read(ROOT/GROUPS)['groups']
        need(raw['matchings']==[[a^1 for a in range(12)]]*3,'fixed six-prism core')
        all_triples=set();labeled=0;s3=list(permutations(range(3)))
        for coordinates in product(s3,repeat=6):
            words=tuple(tuple(coordinates[k][r]for k in range(6))for r in range(3))
            if all(all(w.count(g)==2 for g in range(3))for w in words):
                labeled+=1;all_triples.add(tuple(sorted(words)))
        triples=sorted(all_triples);need(labeled==900 and len(triples)==150,'complete balanced universe')
        patterns=[parity(t)for t in triples];hist=Counter(patterns)
        need(sorted(hist.values())==[12]*10+[30],'pattern fibers')
        need(all(parity(tuple(t[p]for p in perm))==q for t,q in zip(triples,patterns,strict=True)for perm in permutations(range(3))),'sorting preserves normalized parity')
        save(out/'local_triples.json',dict(enumerated_coordinate_permutation_tuples=6**6,labeled_balanced=900,sorted_balanced=150,
            triples=[[list(w)for w in t]for t in triples],normalized_patterns=[list(p)for p in patterns]))
        all_words=sorted({w for t in triples for w in t});need(len(all_words)==90,'90 word universe')
        domains=[];next_id=1
        for group,wanted in tqdm(list(zip(groups,projection['selected_group_parity_patterns'],strict=True)),desc='New parity branch local domains'):
            coords=group['support'];cols=group['columns'];options=[]
            need(all(raw['support_columns'][d]==coords for d in cols),'identical support group')
            for index,(words,p)in enumerate(zip(triples,patterns,strict=True)):
                if list(p)!=wanted:continue
                rows=[sorted(12*g+a for a,g in zip(coords,w,strict=True))for w in words]
                need(all(not set(a)&set(b)for a,b in combinations(rows,2)),'balanced disjoint columns')
                options.append(dict(selector=next_id,choice_index=len(options),balanced_triple_index=index,word_indices=[all_words.index(w)for w in words],
                    color_words=[list(w)for w in words],lifted_rows=rows,lifted_masks_hex=[format(sum(1<<i for i in r),'09x')for r in rows]));next_id+=1
            need(len(options)==(30 if not any(wanted) else 12),'complete selected local domain')
            domains.append(dict(group=group['group'],support_coordinates=coords,raw_columns=cols,selected_parity_pattern=wanted,choices=options))
            cap.check()
        need([d['group']for d in domains]==list(range(20)),'20 ordered groups');variables=next_id-1
        scope=dict(schema='SIXTY_CUT_SELECTED_PARITY_LIFT_SCOPE_V1',raw_support=RAW,raw_support_sha256=PINS[RAW],projection=PROJECTION,projection_sha256=PINS[PROJECTION],
            actual_projection_gate=GATE,actual_projection_gate_sha256=PINS[GATE],selected_pattern_indices=projection['selected_pattern_indices'],
            matchings=raw['matchings'],core_adjacency=raw['core_adjacency'],target_gram36=raw['prescribed_Gram36'],L=raw['L'],domains=domains,
            one_fixed_parity_branch=True,balance_is_extra_assumption=True,all_balanced_branches_covered=False,residual_D_encoded=False,target_graph=False,independent_approval=False)
        save(out/'scope.json',scope);gram_rows=[]
        for i in range(36):
            for j in range(i,36):
                terms=[]
                for d in domains:
                    for choice in d['choices']:
                        coefficient=sum(i in r and j in r for r in choice['lifted_rows'])
                        need(coefficient in(0,1),'binary Gram coefficients')
                        if coefficient:terms.append(choice['selector'])
                gram_rows.append(dict(rows=[i,j],target=raw['prescribed_Gram36'][i][j],inputs=terms))
        nontrivial=[r for r in gram_rows if r['rows'][0]!=r['rows'][1]and r['target']>0];need(len(nontrivial)==540,'540 positive offdiagonal rows')
        for r in gram_rows:
            if r['target']==0:need(not r['inputs'],'zero target automatic from all local choices')
            if r['rows'][0]==r['rows'][1]:
                i=r['rows'][0];containing=[d for d in domains if i%12 in d['support_coordinates']]
                need(r['target']==len(containing)==10,'diagonal follows from10 group normalizations')
                need(r['inputs']==[c['selector']for d in containing for c in d['choices']],'diagonal row exact sum of onehots')
        rows=[dict(kind='group_exactone',group=d['group'],target=1,inputs=[c['selector']for c in d['choices']])for d in domains]
        rows.extend(dict(kind='gram_count',**r)for r in nontrivial);columns=[[]for _ in range(variables)]
        for index,row in enumerate(rows):
            for v in row['inputs']:columns[v-1].append(index)
        matrix=dict(nonnegative_variables=True,columns_nonzero_row_indices=columns,rhs=[r['target']for r in rows],
            selectors=[[d['group'],c['choice_index']]for d in domains for c in d['choices']],variables=variables,equations=len(rows),binary_coefficients=True,
            row_metadata=rows,scope_sha256=digest(out/'scope.json'),omitted_constraints=['integrality','inter-group outside-column caps'],relaxation_only=True,independent_approval=False)
        save(out/'exact_model.json',matrix);save(out/'all_gram_rows.json',gram_rows)
        zero_rows=[dict(index=i,**r)for i,r in enumerate(rows)if r['target']>0 and not r['inputs']]
        save(out/'row_coverage.json',dict(required_rows=len(rows),zero_required_rows=zero_rows,available_selector_counts=[len(r['inputs'])for r in rows],
            row_coverage_is_not_joint_feasibility=True))
        denominator=math.lcm(*(len(d['choices'])for d in domains));numerators=[denominator//len(d['choices'])for d in domains for _ in d['choices']]
        residual=residuals(columns,matrix['rhs'],numerators,denominator);passed=not any(residual)
        controls=[dict(name='exact_half_weights',passed=not any(residuals([[0],[0]],[1],[1,1],2))),
            dict(name='corrupt_weight',rejected=any(residuals([[0],[0]],[1],[2,1],2))),
            dict(name='corrupt_rhs',rejected=any(residuals([[0],[0]],[2],[1,1],2)))]
        need(all(x.get('passed',x.get('rejected'))for x in controls),'rational checking controls')
        save(out/'controls.json',controls)
        save(out/'uniform_primal.json',dict(kind='CANDIDATE_EXACT_RATIONAL_PRIMAL'if passed else'UNSUCCESSFUL_EXACT_UNIFORM_TEST',
            exact_model_sha256=digest(out/'exact_model.json'),numerators=numerators,denominator=denominator,row_residuals=residual,exact_feasible=passed,
            integer_selector_solution=False,full_factor=False,independent_approval=False))
        if zero_rows:
            weights=[0]*len(rows);weights[zero_rows[0]['index']]=-1
            products=[sum(weights[r]for r in c)for c in columns];right=sum(a*b for a,b in zip(weights,matrix['rhs'],strict=True))
            need(min(products)>=0 and right<0,'exact empty-row certificate')
            save(out/'zero_row_certificate.json',dict(weights=weights,column_products=products,rhs_dot=right,independent_approval=False))
        cap.check();need(time.monotonic()-cap.start<30,'30second cap');need(all(digest(ROOT/p)==h for p,h in pins.items()),'unchanged inputs')
        save(out/'summary.json',dict(status='CANDIDATE_NEW_SELECTED_PARITY_LIFT_EXACT_SCREEN',timestamp=datetime.now(timezone.utc).isoformat(),
            inputs_sha256=pins,outputs_sha256={key(p):digest(p)for p in out.iterdir()if p.is_file()},variables=variables,equations=len(rows),domains=20,
            domain_sizes=[len(d['choices'])for d in domains],zero_required_rows=len(zero_rows),uniform_exact_primal_pass=passed,
            uniform_denominator=denominator,nonzero_uniform_residuals=sum(v!=0 for v in residual),wall_seconds=time.monotonic()-cap.start,
            peak_memory_bytes=cap.peak_bytes,solver_calls=0,full_factor=False,independent_approval=False,target_resolution='UNKNOWN'))
        print(json.dumps(dict(variables=variables,equations=len(rows),zero_required_rows=len(zero_rows),uniform_exact_primal_pass=passed,denominator=denominator)))
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),wall_seconds=time.monotonic()-cap.start,mathematical_exclusion=False));raise
if __name__=='__main__':main()
