"""Candidate complete Gram encoding of one four-exception profile; no solve."""
from datetime import datetime, timezone
from itertools import combinations, product
from pathlib import Path
import argparse, hashlib, importlib.util, json, platform, subprocess, sys, time
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results'
BASE=ROOT/'acceleration/theory_20260930_hadamard_balanced_gram_cnf.py'
RAW=B/'20260930_hadamard20_support/six_prism.json'
LOCAL=B/'20260930_hadamard_triplicate_counts/local_triples.json'
CASE=B/'20260930_hadamard_four_group_local_screen/case_000.json'
SCREEN_GATE=B/'20260930_independent_review/hadamard_four_group_local_screen/summary.json'
CIRCUIT_GATE=B/'20260930_independent_review/hadamard_four_group_circuits/summary.json'
FIXTURE=B/'20260930_srg243_residual_fixture/triangle_blocks.json'
FIXTURE_GATE=B/'20260930_independent_review/srg243_residual_fixture/summary.json'
PINS={BASE:'ffb5c842b29d0268073656ce948561af0557c24d067bf0260a9cc8f65ab07016',RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',LOCAL:'9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776',CASE:'0b4f3c5ee3a51e83f40d3a2519f87e80d63842c6fcd4f4c125e808d11c44b7ab',SCREEN_GATE:'ff30d47b012d1661182f1cba066425dd9d5aaccad3754cad4d526b7477725c67',CIRCUIT_GATE:'efc6df8951399b99c6c3a68ebb084ead094f3cd147832f806d3604df4c65fb46',FIXTURE:'3f8dfa3803d6a5db8146dd24a0857477e1aa061ab10dac0f9e6e564aabc86439',FIXTURE_GATE:'28bbd97b8e69515c3eb0345e5aa2db12debfaa8a44e83b2e3487342104c5d50e'}
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(Path(p).read_bytes())
def save(p,x):
    with Path(p).open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
def helper():
    need(sha(BASE)==PINS[BASE],'shared producer helper source')
    spec=importlib.util.spec_from_file_location('shared_balanced_Gram_producer_helpers',BASE);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def controls(h):
    prior=h.controls();count_cases=0
    for bound in (1,2):
        clauses=h.exact_count(list(range(1,11)),bound)
        for mask in range(1024):
            values={i:bool(mask>>(i-1)&1) for i in range(1,11)};need(h.satisfied(clauses,values)==(mask.bit_count()==bound),'ten-bit exact count truth');count_cases+=1
    clauses=h.exact_one_prefix([1,2,3],[4,5])+h.OR(6,[2,3])+h.OR(7,[3]);weighted=0
    for mask in range(128):
        v={i:bool(mask>>(i-1)&1) for i in range(1,8)}
        expected=sum(v[i] for i in (1,2,3))==1 and v[4]==v[1] and v[5]==(v[1] or v[2]) and v[6]==(v[2] or v[3]) and v[7]==v[3]
        need(h.satisfied(clauses,v)==expected,'weighted0/1/2 channel truth')
        if expected:need(int(v[6])+int(v[7])==int(v[2])+2*int(v[3]),'exact weighted representation')
        weighted+=1
    bad={1:False,2:False,3:True,4:False,5:False,6:True,7:False};need(not h.satisfied(clauses,bad),'missing second threshold rejected')
    return dict(shared_frozen_generic_controls=prior,ten_bit_truth_cases=count_cases,weighted_channel_truth_cases=weighted,rejected_controls=['selected_multiplicity2_with_second_threshold_false'],research_factor_positive_available=False)
def prepare(h):
    raw=read(RAW);case=read(CASE);local=read(LOCAL);base_scope=h.scope_from_raw(raw);balanced=h.local_options();groups=base_scope['groups'];words=local['words'];triples=local['survivors']
    need(case['case']==0 and case['groups']==[0,7,9,19] and case['domain_sizes']==[48]*4,'literal frozen case0')
    scope=dict(schema='FIXED_HADAMARD_CASE0_PROFILE_SCOPE_V1',raw_support_path=key(RAW),raw_support_sha256=PINS[RAW],case_path=key(CASE),case_sha256=PINS[CASE],core_adjacency36=base_scope['core_adjacency36'],prescribed_Gram36=base_scope['prescribed_Gram36'],L12x60=base_scope['L12x60'],groups=groups,group_columns=base_scope['group_columns'],coordinate_pairs=base_scope['coordinate_pairs'],exceptional_groups=case['groups'],common_support=case['common_support'],circuit_relation=case['relation'],deviation_profile=case['profile'],balanced_groups=[g for g in range(20) if g not in case['groups']],within_group_column_caps_encoded=True,cross_group_column_caps_encoded=False,residual_D_encoded=False,assumed_target_automorphism=None,assumed_target_automorphism_null_reason='No target automorphism is assumed.',balance_WLOG=False,scope='All full prescribed-Gram factors in this literal four-exception profile with local column caps; cross-group caps and residualD omitted.',normalization='Balanced groups: first coordinate permutation identity. Exceptional groups: three words in increasing90-word-catalogue order. Both relabel only equal-support columns.',target_graph=False)
    domains=[];selector=1;expected_counts=[]
    for g,support in enumerate(groups):
        if g in case['groups']:
            side=case['groups'].index(g);sign=case['relation'][side];deltas={a:case['profile'][j] for j,a in enumerate(case['common_support'])}
            wanted=[[1+sign*deltas.get(a,[0,0,0])[f] for f in range(3)] for a in support]
            independently_selected=[]
            for index,tri in enumerate(triples):
                counts=[[sum(words[w][p]==f for w in tri) for f in range(3)] for p in range(6)]
                if counts==wanted:independently_selected.append(index)
            need(independently_selected==case['local_survivor_indices'][side] and len(independently_selected)==48,'complete initial exceptional domain, no AC pruning')
            choices=[dict(choice_index=j,local_survivor_index=index,word_indices=triples[index],colour_words=[words[w] for w in triples[index]]) for j,index in enumerate(independently_selected)];kind='exceptional_sorted_local_triple'
        else:
            wanted=[[1]*3 for _ in range(6)];choices=[dict(choice_index=x['choice_index'],colour_words=x['colour_words'],coordinate_permutations=x['coordinate_permutations']) for x in balanced];kind='balanced_normalized_triple'
        for option in choices:
            option['selector']=selector;selector+=1;option['lifted_rows']=[[12*w[pos]+a for pos,a in enumerate(support)] for w in option['colour_words']]
            need([[sum(w[pos]==f for w in option['colour_words']) for f in range(3)] for pos in range(6)]==wanted,'fixed local counts')
            need(all(len(set(rows))==6 for rows in option['lifted_rows']) and all(len(set(x)&set(y))<=2 for x,y in combinations(option['lifted_rows'],2)),'within-group column caps')
        expected_counts.append(wanted);domains.append(dict(group=g,support=support,columns=scope['group_columns'][g],kind=kind,fixed_counts=wanted,choices=choices))
    need(selector-1==2592,'primary population')
    margins=[]
    for a in range(12):
        for f in range(3):
            total=sum(expected_counts[g][groups[g].index(a)][f] for g in range(20) if a in groups[g]);need(total==10,'all36 exact diagonals by prescribed marginal counts');margins.append(dict(coordinate=a,fibre=f,total=total))
    scope['derived_row_margins']=margins;return scope,domains
def build(h,scope,domains):
    clauses=[];onehots=[];cells=[];nextvar=2593;channel_clause_total=0
    def fresh():
        nonlocal nextvar
        v=nextvar;nextvar+=1;return v
    def append(rows):
        start=len(clauses)+1;clauses.extend(rows);return dict(first_clause=start,clause_count=len(rows))
    for domain in domains:
        ids=[c['selector'] for c in domain['choices']];prefix=[fresh() for _ in range(len(ids)-1)]
        onehots.append(dict(group=domain['group'],selectors=ids,prefixes=prefix,**append(h.exact_one_prefix(ids,prefix))))
    for a,b in scope['coordinate_pairs']:
        incident=[g for g,s in enumerate(scope['groups']) if a in s and b in s]
        for f,z in product(range(3),repeat=2):
            flags=[]
            for g in incident:
                domain=domains[g];pa=domain['support'].index(a);pb=domain['support'].index(b)
                coefficients=[sum(w[pa]==f and w[pb]==z for w in c['colour_words']) for c in domain['choices']]
                need(all(c in (0,1,2) for c in coefficients),'unbalanced exact0/1/2 coefficients')
                channels=[]
                for threshold in (1,2):
                    ids=[c['selector'] for c,value in zip(domain['choices'],coefficients) if value>=threshold];v=fresh();section=append(h.OR(v,ids));channel_clause_total+=section['clause_count'];channels.append(dict(threshold=threshold,variable=v,selectors=ids,**section))
                flags.append(dict(group=g,coefficients=coefficients,channels=channels))
            bound=1 if f==z else 2;ids=[c['variable'] for entry in flags for c in entry['channels']]
            cells.append(dict(coordinates=[a,b],fibres=[f,z],bound=bound,group_contributions=flags,count_inputs=ids,**append(h.exact_count(ids,bound))))
    need(len(cells)==540 and nextvar-1==10564 and len(clauses)==187408,'complete predicted dimensions')
    need(sum(r['clause_count'] for r in onehots)==10288 and channel_clause_total==122040 and sum(r['clause_count'] for r in cells)==55080,'all clause sections')
    return dict(schema='FIXED_HADAMARD_CASE0_PROFILE_WEIGHTED_THRESHOLD_CNF_V1',variables=nextvar-1,clauses=len(clauses),primary_selectors=2592,domains=domains,exact_one_prefix_rows=onehots,pair_cell_counts=cells,variable_populations=dict(selectors=2592,onehot_prefixes=2572,weighted_threshold_channels=5400),clause_populations=dict(onehot=10288,channels=122040,counts=55080)),clauses
def decode(assignment,model_path,scope_path,cnf_path):
    h=helper();model=read(model_path);scope=read(scope_path);need(model['scope_sha256']==sha(scope_path),'scope pin');values={}
    for x in assignment:need(type(x) is int and x!=0 and abs(x) not in values,'unique signed assignment');values[abs(x)]=x>0
    need(set(values)==set(range(1,model['variables']+1)),'complete assignment')
    count=0
    with Path(cnf_path).open() as stream:
        need(stream.readline().strip()==f"p cnf {model['variables']} {model['clauses']}",'exact CNF header')
        for line in stream:
            literals=list(map(int,line.split()));need(literals and literals[-1]==0 and all(literals[:-1]) and all(abs(x)<=model['variables'] for x in literals[:-1]),'clause syntax');need(h.satisfied([literals[:-1]],values),'all actual clauses');count+=1
    need(count==model['clauses'],'exact complete clause count')
    f=[[0]*60 for _ in range(36)];selected=[];actual_profiles=[]
    for domain in model['domains']:
        active=[c for c in domain['choices'] if values[c['selector']]];need(len(active)==1,'one group option');choice=active[0];selected.append(choice['selector'])
        for d,rows in zip(domain['columns'],choice['lifted_rows']):
            for r in rows:f[r][d]=1
        actual=[[sum(f[12*z+a][d] for d in domain['columns']) for z in range(3)] for a in domain['support']];need(actual==domain['fixed_counts'],'literal selected count profile');actual_profiles.append(dict(group=domain['group'],counts=actual))
    checks=h.check_factor(f,scope['core_adjacency36'],scope['prescribed_Gram36'],12,scope['L12x60'])
    pairs=[list(p) for p in combinations(range(12),2) if p[0]^1!=p[1]];rawpairs=[[a for a in range(12) if f[a][d]] for d in range(60)];need(sorted(rawpairs)==pairs,'canonicalC0 bijection');order=[rawpairs.index(p) for p in pairs]
    return dict(factor=f,L=scope['L12x60'],selected_selector_ids=selected,actual_group_profiles=actual_profiles,canonical_column_order=order,canonical_factor=[[row[d] for d in order] for row in f],core_adjacency=scope['core_adjacency36'],target_gram=scope['prescribed_Gram36'],checks=checks,Gram_factor=True,factor_also_passes_column_caps=not checks['column_cap_violations'],factor_also_passes_mixed_caps=not checks['mixed_cap_violations'],target_graph=False,residual_D=None,profile_is_additional_assumption=True,model_sha256=sha(model_path),scope_sha256=sha(scope_path),independent_approval=False)
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);args=p.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    try:
        for path,digest in PINS.items():need(sha(path)==digest,'input pin '+key(path))
        inputs={key(p):d for p,d in PINS.items()}
        for path in [Path(__file__),Path(__file__).with_name('theory_20260930_hadamard_case0_profile_cnf_spec.md'),ROOT/'uv.lock',ROOT/'pyproject.toml']:inputs[key(path)]=sha(path)
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=inputs,limits=dict(seconds=120,native_solver_calls=0),selected_case=0,shared_components=['Frozen producer exact_one_prefix/OR/exact_count, local balanced generator, generic raw-factor validator; no independent approval.']))
        h=helper();save(out/'controls.json',controls(h));scope,domains=prepare(h);save(out/'scope.json',scope);model,clauses=build(h,scope,domains);model['scope_sha256']=sha(out/'scope.json');save(out/'model.json',model)
        with (out/'instance.cnf').open('x',encoding='ascii',newline='\n') as f:
            f.write(f"p cnf {model['variables']} {model['clauses']}\n")
            for clause in clauses:f.write(' '.join(map(str,clause))+' 0\n')
        need(time.monotonic()-start<120,'bounded build allocation')
        summary=dict(status='CANDIDATE_CASE0_FULL_GROUPED_GRAM_CNF_BUILT',timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=inputs,outputs_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},variables=model['variables'],clauses=model['clauses'],selectors=2592,balanced_groups=16,balanced_choices_per_group=150,exceptional_groups=4,exceptional_initial_choices_per_group=48,group_rows=20,nonmatched_Gram_cell_rows=540,weighted_threshold_channels=5400,cross_group_column_caps_encoded=False,within_group_column_caps_encoded=True,independent_approval=False,native_solver_calls=0,target_resolution=False,elapsed_seconds=time.monotonic()-start,scope=scope['scope'],artifact_availability='LOCAL_ONLY')
        save(out/'summary.json',summary);print(json.dumps({k:v for k,v in summary.items() if k not in ('inputs_sha256','outputs_sha256')}))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e),source_sha256=sha(Path(__file__))));raise
if __name__=='__main__':main()
