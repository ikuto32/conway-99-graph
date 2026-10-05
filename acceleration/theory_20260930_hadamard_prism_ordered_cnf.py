"""Candidate fixed six-prism L coloring CNF with audited column ordering; no solver."""
from collections import Counter
from datetime import datetime,timezone
from itertools import combinations,product,permutations
from pathlib import Path
import argparse
import json
import platform
import shutil
import subprocess
import sys
import time
from tqdm import tqdm
from theory_20260930_eight_full99_cnf import Clauses,Encoder,ResourceCap,counter_controls,digest,package,save

ROOT=Path(__file__).resolve().parents[1]
SCOUT=ROOT/'acceleration/results/20260930_hadamard20_support'
RAW=SCOUT/'six_prism.json'
RAW_HASH='ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d'
SUMMARY_HASH='94e146c8e4c04acda9468f691cf91e2a2e82dbc6d60019d0bfb2d7e02b568f05'
ORDER_DIR=ROOT/'acceleration/results/20260930_independent_review/hadamard_six_prism_column_order'
ORDER_GATE=ORDER_DIR/'summary.json'
ORDER_HASH='0ce1be9ca11a3e860aa97791cfb4f42c1660d937a69ac7a9b7d96ca37640c9d2'
SUPPORT_GATE=ROOT/'acceleration/results/20260930_independent_review/hadamard20_support_v2/summary.json'
SUPPORT_HASH='a8477256446e3e402a2a21241dc383a515162dc9c8c07a9a8e26326c07b0f58f'
DEFAULT_OUT=ROOT/'acceleration/results/20260930_hadamard_prism_ordered_cnf'

def need(ok,why):
    if not ok:raise ValueError(why)
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(Path(p).read_bytes())

def exact_domains(raw):
    gram=raw['prescribed_Gram36'];support=raw['support_columns'];words=[w for w in product(range(3),repeat=6) if all(w.count(g)==2 for g in range(3))]
    rebuilt=[]
    for d,coords in enumerate(support):
        need(coords==[a for a in range(12) if raw['L'][a][d]],'exact raw support')
        options=[]
        for colours in words:
            rows=sorted(12*g+a for g,a in zip(colours,coords))
            if any(gram[i][j]==0 for i,j in combinations(rows,2)):continue
            options.append(dict(fibres_by_sorted_coordinate=list(colours),rows=rows,row_mask_hex=format(sum(1<<i for i in rows),'09x')))
        need(options==raw['column_colour_options'][d] and options,'complete nonempty option domain');rebuilt.append(options)
    return rebuilt

def new_controls():
    # On an exactly-one choice, a rowpair's Gram contribution is a linear
    # selector sum; deliberate double selection shows why onehot is required.
    options=[{0,1},{0,2},{1,2}];cases=0
    for selected in range(3):
        for i,j in product(range(3),repeat=2):
            linear=sum(int(k==selected) for k,rows in enumerate(options) if i in rows and j in rows)
            need(linear==int(i in options[selected] and j in options[selected]),'onehot linearGram truth');cases+=1
    capcases=0
    for a,b in product([{0,1,2},{0,1,3},{2,3,4}],repeat=2):
        forbidden=len(a&b)>2
        for x,y in product((False,True),repeat=2):
            clause_value=(not x or not y) if forbidden else True
            need(clause_value==(not(x and y and len(a&b)>2)),'binarycap control');capcases+=1
    ordercases=0
    for n in range(2,9):
        for left,right in product(range(n),repeat=2):
            clauses_hold=all(not(left==a and right==b) for a in range(n) for b in range(a+1))
            need(clauses_hold==(left<right),'strict-order negative-pair clauses');ordercases+=1
        for triple in permutations(range(n),3):
            sorted_triple=sorted(triple);need(sorted_triple[0]<sorted_triple[1]<sorted_triple[2],'column sorting control')
    need(not (3<3) and not (4<2),'duplicate and descending rank controls')
    return dict(onehot_linear_Gram_cases=cases,paircap_truth_cases=capcases,strict_order_truth_cases=ordercases,research_positive_F=None,
                research_positive_F_reason='No complete factor known for this fixed support; encoding controls only.')

def build(out):
    out.mkdir(parents=True,exist_ok=False);cap=ResourceCap();cap.check();need(digest(RAW)==RAW_HASH and digest(SCOUT/'summary.json')==SUMMARY_HASH,'frozen scout pins')
    need(digest(ORDER_GATE)==ORDER_HASH and digest(SUPPORT_GATE)==SUPPORT_HASH,'independent scope gates')
    ordergate=read(ORDER_GATE);need(ordergate['status']=='INDEPENDENT_HADAMARD_SIX_PRISM_IDENTICAL_SUPPORT_ORDER_PASS','ordering gate status')
    group_path=ORDER_DIR/'groups.json';need(digest(group_path)==ordergate['outputs_sha256'][key(group_path)],'audited group file')
    ordering=read(group_path)
    sources=[Path(__file__),Path(__file__).with_name('theory_20260930_hadamard_prism_ordered_cnf_spec.md'),
        ROOT/'acceleration/theory_20260930_fixed_support_coloring_cnf.py',ORDER_GATE,SUPPORT_GATE,group_path,
        ROOT/'acceleration/theory_20260930_eight_full99_cnf.py',ROOT/'acceleration/theory_20260930_full_srg_validator.py',
        RAW,SCOUT/'summary.json',SCOUT/'Hadamard20.json',ROOT/'uv.lock',ROOT/'pyproject.toml']
    pins={key(p):digest(p) for p in sources}
    manifest=dict(created_at=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv],working_directory=str(ROOT),versions=dict(python=platform.python_version(),uv=subprocess.check_output(['uv','--version'],text=True).strip()),
        inputs_sha256=pins,limits=dict(build_seconds=120,process_memory_bytes=8*1024**3,solver_calls=0),
        scope='All fullGram/Ycap factors for the frozen six-prism L modulo independently justified identical-support column ordering; no cyclic restriction, residualD or unrestrictedcoverage.',
        independent_scope_gates={key(ORDER_GATE):ORDER_HASH,key(SUPPORT_GATE):SUPPORT_HASH},
        independent_encoding_review='PENDING; this producer does not approve its own CNF',random_seed=None,random_seed_reason='Deterministic exact encoding.')
    save(out/'manifest.json',manifest)
    try:
        raw=read(RAW);opts=exact_domains(raw);gram=raw['prescribed_Gram36'];domains=[];next_id=0
        for d,options in enumerate(opts):
            choices=[]
            for index,op in enumerate(options):next_id+=1;choices.append(dict(selector=next_id,option_index=index,**op))
            domains.append(dict(column=d,support_coordinates=raw['support_columns'][d],choices=choices))
        selectors=next_id;need(selectors==5400 and all(len(d['choices'])==90 for d in domains),'all5400 unrestricted local color choices')
        need(len(ordering['groups'])==20 and len(ordering['adjacent_order_pairs'])==40,'audited groups and adjacent pairs')
        for group in ordering['groups']:
            columns=group['columns'];need(len(columns)==3 and columns==sorted(columns),'three ascending raw columns')
            need(all(raw['support_columns'][d]==group['support'] and opts[d]==opts[columns[0]] for d in columns),'identical ordered options')
        need(sorted(d for group in ordering['groups'] for d in group['columns'])==list(range(60)),'complete disjoint column grouping')
        save(out/'counter_controls.json',counter_controls());save(out/'local_encoding_controls.json',new_controls())
        scope=dict(schema='FIXED_HADAMARD_SIX_PRISM_ORDERED_COLORING_SCOPE_V1',core_name='six_prism',matchings=raw['matchings'],
            core_adjacency=raw['core_adjacency'],target_gram36=gram,L=raw['L'],support_columns=raw['support_columns'],
            source_raw_support=key(RAW),source_raw_support_sha256=RAW_HASH,cross_matchings='identity',
            column_sum_per_fibre=2,row_sum=10,all_distinct_column_overlap_caps=2,complete_Gram=True,
            canonical_C0_prescribed=False,target_graph=False,residual_D=False,other_supports_covered=False,
            domains=domains,domain_filter='All90 balanced fibre assignments minus every choice containing any full-Gram-zero rowpair, including crossfibre zeros.',
            identical_support_groups=ordering['groups'],adjacent_order_pairs=ordering['adjacent_order_pairs'],
            strictly_increasing_option_rank=True,cyclic_colour_constraint=False,
            ordering_gate_path=key(ORDER_GATE),ordering_gate_sha256=ORDER_HASH,
            no_target_automorphism_assumed=True)
        save(out/'scope.json',scope);rows=[];sections=[];pair_caps=[];order_rows=[];all_pairs_checked=0
        with (out/'clauses.body').open('xb') as body:
            clauses=Clauses(body,cap);enc=Encoder(selectors,clauses);first=clauses.count+1
            for domain in domains:rows.append(enc.counter([o['selector'] for o in domain['choices']],1,True,dict(kind='column_exactly_one',column=domain['column'])))
            sections.append(dict(kind='60column_exactone',first_clause=first,last_clause=clauses.count,count=clauses.count-first+1));first=clauses.count+1
            for i,j in tqdm([(i,j) for i in range(36) for j in range(i,36)],desc='Exact Gram selector counts'):
                inputs=[o['selector'] for domain in domains for o in domain['choices'] if i in o['rows'] and j in o['rows']]
                need(len(inputs)>=gram[i][j],'raw Gram capacity')
                rows.append(enc.counter(inputs,gram[i][j],True,dict(kind='full_Gram',rows=[i,j])))
            sections.append(dict(kind='666exactGram_uppertriangle',first_clause=first,last_clause=clauses.count,count=clauses.count-first+1));first=clauses.count+1
            for d,e in tqdm(list(combinations(range(60),2)),desc='All column-pair forbidden choices'):
                cap.check();begin=clauses.count+1;right=domains[e]['choices'];rm=[int(o['row_mask_hex'],16) for o in right];forbidden=[];allowed_count=0
                for lo in domains[d]['choices']:
                    mask=int(lo['row_mask_hex'],16);bits=0
                    for j,(ro,r) in enumerate(zip(right,rm,strict=True)):
                        overlap=(mask&r).bit_count();all_pairs_checked+=1
                        if overlap>2:clauses.emit(-lo['selector'],-ro['selector']);bits|=1<<j
                        else:allowed_count+=1
                    forbidden.append(format(bits,'x'))
                pair_caps.append(dict(columns=[d,e],forbidden_right_masks_hex=forbidden,
                    tested_choice_pairs=len(domains[d]['choices'])*len(right),allowed_choice_pairs=allowed_count,
                    forbidden_choice_pairs=clauses.count-begin+1,first_clause=begin,clause_count=clauses.count-begin+1))
            sections.append(dict(kind='1770columncap_forbidden_option_pairs',first_clause=first,last_clause=clauses.count,count=clauses.count-first+1))
            base_clause_count=clauses.count;first=clauses.count+1
            for d,e in ordering['adjacent_order_pairs']:
                cap.check();begin=clauses.count+1
                for left in range(90):
                    for right in range(left+1):clauses.emit(-domains[d]['choices'][left]['selector'],-domains[e]['choices'][right]['selector'])
                need(clauses.count-begin+1==4095,'full >= rank-pair universe')
                order_rows.append(dict(columns=[d,e],left_option_ranks=list(range(90)),right_forbidden_ranks='0..left inclusive',first_clause=begin,clause_count=4095))
            sections.append(dict(kind='40strict_adjacent_order_pairs',first_clause=first,last_clause=clauses.count,count=clauses.count-first+1))
            need(clauses.count-base_clause_count==163800,'exact audited order suffix count')
        with (out/'instance.cnf').open('xb') as dest,(out/'clauses.body').open('rb') as src:
            dest.write(f'p cnf {enc.top} {clauses.count}\n'.encode());shutil.copyfileobj(src,dest,1048576)
        model=dict(schema='FIXED_HADAMARD_PRISM_ORDERED_COLOR_SELECTOR_PREFIX_CNF_V1',variables=enc.top,clauses=clauses.count,primary_selectors=selectors,
            scope_path=key(out/'scope.json'),scope_sha256=digest(out/'scope.json'),domains=domains,counter_rows=rows,
            column_cap_pairs=pair_caps,clause_sections=sections,strict_order_pairs=order_rows,base_clause_count=base_clause_count,
            ordered_suffix_clause_count=163800,counter_prefix_reference_format='JSON Boolean constants; positive integer variableIDs.',
            counter_gate_order=dict(and_gate=['a -z','b -z','-a -b z'],or_gate=['-a z','-b z','a b -z'],
                                    recurrence=['-a z','-b -c z','a b -z','a c -z']),
            counter_thresholds='throughbound+1; exactlowerpositiveunit anduppernegativeunit',no_product_variables=True,
            independent_scope_gates={key(ORDER_GATE):ORDER_HASH,key(SUPPORT_GATE):SUPPORT_HASH},independent_CNF_gate=None,
            independent_CNF_gate_reason='Fresh complete encoding and raw-object gates required before any solver.',solver_calls=0)
        save(out/'model.json',model);cap.check();save(out/'artifact_packages.json',dict(packages=[package(p,cap) for p in [out/'instance.cnf',out/'clauses.body',out/'model.json']],
            retrieval='Concatenate orderedgzip parts, decompress and verify rawSHA256; originals retained.'))
        need(all(digest(ROOT/p)==h for p,h in pins.items()),'frozen inputs')
        summary=dict(status='CANDIDATE_FIXED_HADAMARD_SIX_PRISM_ORDERED_COLORING_CNF',created_at=manifest['created_at'],completed_at=datetime.now(timezone.utc).isoformat(),
            source_commit=manifest['source_commit'],inputs_sha256=pins,outputs_sha256={key(p):digest(p) for p in out.iterdir() if p.is_file()},
            variables=enc.top,clauses=clauses.count,primary_selectors=selectors,columns=60,column_options_histogram=dict(Counter(len(d['choices']) for d in domains)),
            exact_one_rows=60,Gram_equality_rows=666,distinct_column_pairs=1770,tested_choice_pairs=all_pairs_checked,
            forbidden_choice_pairs=sum(r['forbidden_choice_pairs'] for r in pair_caps),clause_sections=sections,
            identical_support_groups=20,adjacent_order_pairs=40,ordered_suffix_clauses=163800,cyclic_colour_constraint=False,
            wall_seconds=time.monotonic()-cap.start,peak_working_set_bytes=cap.peak_bytes,solver_calls=0,independent_approval=False,target_resolution='UNKNOWN',
            limitations=['No completefactorpositive known.','ChosenL only; nootherHadamardchoices orsupports covered.','NoD or99graph.'])
        save(out/'summary.json',summary);print(json.dumps({k:v for k,v in summary.items() if k not in ['inputs_sha256','outputs_sha256']}))
    except BaseException as e:
        save(out/'failure.json',dict(status='FAILED_BUILD',exception=repr(e),elapsed_seconds=time.monotonic()-cap.start));raise

def decode(assignment,model_path=DEFAULT_OUT/'model.json',scope_path=DEFAULT_OUT/'scope.json'):
    model=read(model_path);scope=read(scope_path);need(digest(scope_path)==model['scope_sha256'],'scopehash')
    values={}
    for literal in assignment:
        need(type(literal)is int and literal and abs(literal) not in values,'unique literalIDs');values[abs(literal)]=literal>0
    need(set(values)==set(range(1,model['variables']+1)),'complete assignment')
    factor=[[0]*60 for _ in range(36)];selected=[];selected_ranks=[]
    for d,domain in enumerate(model['domains']):
        choices=[o for o in domain['choices'] if values[o['selector']]];need(len(choices)==1,'exactlyone selectedoption')
        choice=choices[0];selected.append(choice['selector']);selected_ranks.append(choice['option_index'])
        for row in choice['rows']:factor[row][d]=1
    need(all(sum(factor[12*g+a][d] for g in range(3))==scope['L'][a][d] for a in range(12) for d in range(60)),'rawLprojection')
    need(all(sum(factor[i][d]*factor[j][d] for d in range(60))==scope['target_gram36'][i][j] for i in range(36) for j in range(36)),'full1296Gram')
    need(all(sum(factor[12*g+a][d] for a in range(12))==2 for g in range(3) for d in range(60)),'twoeachfibre')
    need(all(sum(factor[i][d]*factor[i][e] for i in range(36))<=2 for d,e in combinations(range(60),2)),'allYcaps')
    need(all(selected_ranks[d]<selected_ranks[e] for d,e in scope['adjacent_order_pairs']),'strict identical-support column ranks')
    c=scope['core_adjacency'];need(all(factor[i][d]+sum(c[i][j]*factor[j][d] for j in range(36))<=2 for i in range(36) for d in range(60)),'literal mixedcaps')
    pairs=[tuple(i for i in range(12) if factor[i][d]) for d in range(60)];catalog=[p for p in combinations(range(12),2) if scope['matchings'][0][p[0]]!=p[1]]
    need(sorted(pairs)==catalog,'C0columnbijection');order=[pairs.index(p) for p in catalog];canonical=[[r[d] for d in order] for r in factor]
    return dict(factor=factor,L=scope['L'],selected_selector_ids=selected,selected_option_ranks=selected_ranks,
        adjacent_order_pairs=scope['adjacent_order_pairs'],cyclic_colour_constraint=False,core_adjacency=c,matchings=scope['matchings'],
        M0=scope['matchings'][0],M1=scope['matchings'][1],M2=scope['matchings'][2],P=list(range(12)),target_gram36=scope['target_gram36'],
        canonical_factor=canonical,canonical_column_order=order,canonical_C0_columns=[list(p) for p in catalog],
        scope_sha256=digest(scope_path),model_sha256=digest(model_path),independent_approval=False,target_graph=False,residual_D=None,
        residual_D_reason='Only fixed-support factor constraints encoded.')

def main():
    ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='mode',required=True)
    b=sub.add_parser('build');b.add_argument('--out',type=Path,required=True)
    d=sub.add_parser('decode');d.add_argument('--assignment',type=Path,required=True);d.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    if args.mode=='build':build(args.out.resolve())
    else:
        raw=read(args.assignment);assignment=raw if type(raw)is list else raw.get('assignment',raw.get('model'))
        save(args.out,decode(assignment))

if __name__=='__main__':main()
