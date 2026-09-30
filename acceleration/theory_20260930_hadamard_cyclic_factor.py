"""Candidate20x30 restricted cyclic-factor CNF and raw decoder; no solver."""
from collections import Counter
from datetime import datetime,timezone
from itertools import combinations,product
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
RAW=ROOT/'acceleration/results/20260930_hadamard20_support/six_prism.json'
RAW_HASH='ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d'
GATE=ROOT/'acceleration/results/20260930_independent_review/hadamard20_support_v2/summary.json'
GH='a8477256446e3e402a2a21241dc383a515162dc9c8c07a9a8e26326c07b0f58f'
DEFAULT=ROOT/'acceleration/results/20260930_hadamard_six_prism_cyclic_cnf'

def need(ok,why):
    if not ok:raise ValueError(why)
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(Path(p).read_bytes())

def prepare(raw):
    m=[a^1 for a in range(12)];need(raw['matchings']==[m,m,m],'fixedsixprism only')
    groups={}
    for d,support in enumerate(raw['support_columns']):groups.setdefault(tuple(support),[]).append(d)
    ordered=sorted(groups.items(),key=lambda x:x[1][0]);need(len(ordered)==20 and all(len(cols)==3 for _,cols in ordered),'twenty triple multiplicities')
    words=[w for w in product(range(3),repeat=6) if all(w.count(g)==2 for g in range(3))]
    gauge=[w for w in words if w[0]==0];need(len(words)==90 and len(gauge)==30,'balancedgauge counts')
    phase_controls=[]
    for w in words:
        normalized=tuple((v-w[0])%3 for v in w);index=gauge.index(normalized)
        original=[sorted(12*((g+r)%3)+a for a,g in enumerate(w)) for r in range(3)]
        new=[sorted(12*((g+r)%3)+a for a,g in enumerate(normalized)) for r in range(3)]
        need(sorted(original)==sorted(new),'literal cycliccolumn gauge coverage')
        phase_controls.append(dict(original_coloring=list(w),normalized_choice=index,removed_phase=w[0]))
    domains=[]
    for p,(coords,cols) in enumerate(ordered):
        choices=[]
        for j,w in enumerate(gauge):
            lifted=[sorted(12*((g+r)%3)+a for a,g in zip(coords,w)) for r in range(3)]
            need(all(len({row//12 for row in rows})==3 and all(sum(row//12==g for row in rows)==2 for g in range(3)) for rows in lifted),'balanced liftedcolumns')
            need(all(not set(lifted[r])&set(lifted[s]) for r,s in combinations(range(3),2)),'withintriplet disjointness')
            choices.append(dict(selector=1+30*p+j,choice_index=j,coloring=list(w),lifted_rows=lifted,
                                lifted_masks_hex=[format(sum(1<<i for i in rows),'09x') for rows in lifted]))
        domains.append(dict(group=p,support_coordinates=list(coords),raw_columns=cols,choices=choices))
    return domains,phase_controls

def build(out):
    out.mkdir(parents=True,exist_ok=False);cap=ResourceCap();cap.check();need(digest(RAW)==RAW_HASH and digest(GATE)==GH,'rawsupport andindependentgate pins')
    need(read(GATE)['status']=='INDEPENDENT_HADAMARD20_SUPPORT_AND_PROJECTION_PASS','support status')
    sources=[Path(__file__),Path(__file__).with_name('theory_20260930_hadamard_cyclic_factor_spec.md'),ROOT/'docs/DERIVATION_20260930_HADAMARD_CYCLIC_FACTOR.md',
        ROOT/'acceleration/theory_20260930_eight_full99_cnf.py',ROOT/'acceleration/theory_20260930_full_srg_validator.py',RAW,GATE,ROOT/'uv.lock',ROOT/'pyproject.toml']
    pins={key(p):digest(p) for p in sources};created=datetime.now(timezone.utc).isoformat()
    save(out/'manifest.json',dict(created_at=created,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],
        working_directory=str(ROOT),inputs_sha256=pins,versions=dict(python=platform.python_version(),uv=subprocess.check_output(['uv','--version'],text=True).strip()),
        limits=dict(build_seconds=120,memory_bytes=8*1024**3,solver_calls=0),extra_restriction='Three identicalsupportcolumns are cyclicfibre shifts; notWLOG for arbitraryfactors.',
        residual_D_included=False,target_automorphism_assumed=False))
    try:
        raw=read(RAW);domains,phase_controls=prepare(raw);pairs=[list(p) for p in combinations(range(12),2) if p[1]!=(p[0]^1)]
        pair_inventory=[];local_truth_checks=0
        for a,b in pairs:
            containing=[d['group'] for d in domains if a in d['support_coordinates'] and b in d['support_coordinates']]
            need(len(containing)==5,'fivebase supportcooccurrences')
            pair_inventory.append(dict(coordinates=[a,b],containing_groups=containing))
            for p in containing:
                domain=domains[p];ia=domain['support_coordinates'].index(a);ib=domain['support_coordinates'].index(b)
                for choice in domain['choices']:
                    difference=(choice['coloring'][ib]-choice['coloring'][ia])%3
                    for g,h in product(range(3),repeat=2):
                        actual=sum((12*g+a in rows and 12*h+b in rows) for rows in choice['lifted_rows'])
                        need(actual==int((h-g)%3==difference),'literalGram difference control');local_truth_checks+=1
        save(out/'counter_controls.json',counter_controls());save(out/'local_controls.json',dict(phase_transports=phase_controls,
            complete_balanced90_to30_coverage=True,literal_local_Gram_checks=local_truth_checks,
            withintriplet_choice_pair_checks=20*30*3,complete_research_positive=None,
            complete_research_positive_reason='No full20-choice factor is provided by local controls.'))
        scope=dict(schema='FIXED_HADAMARD_SIX_PRISM_CYCLIC_FACTOR_SCOPE_V1',raw_support=key(RAW),raw_support_sha256=RAW_HASH,
            matchings=raw['matchings'],core_adjacency=raw['core_adjacency'],target_gram36=raw['prescribed_Gram36'],L=raw['L'],
            domains=domains,coordinate_pairs=pair_inventory,first_coordinate_color=0,
            within_group_phase_by_sorted_column=[0,1,2],extra_cyclic_factor_constraint=True,
            arbitrary_fixedL_factors_covered=False,all_D_unencoded=True,target_graph=False,no_target_automorphism_assumed=True)
        save(out/'scope.json',scope);counterrows=[];sections=[];caps=[];pairchecks=0;all9checks=0
        with (out/'clauses.body').open('xb') as body:
            clauses=Clauses(body,cap);enc=Encoder(600,clauses);first=clauses.count+1
            for domain in domains:counterrows.append(enc.counter([x['selector'] for x in domain['choices']],1,True,dict(kind='group_exactone',group=domain['group'])))
            sections.append(dict(kind='20group_exactone',first_clause=first,last_clause=clauses.count,count=clauses.count-first+1));first=clauses.count+1
            for pair in pair_inventory:
                a,b=pair['coordinates']
                for difference in range(3):
                    terms=[]
                    for p in pair['containing_groups']:
                        domain=domains[p];ia=domain['support_coordinates'].index(a);ib=domain['support_coordinates'].index(b)
                        terms.extend(x['selector'] for x in domain['choices'] if (x['coloring'][ib]-x['coloring'][ia])%3==difference)
                    target=[1,2,2][difference];counterrows.append(enc.counter(terms,target,True,dict(kind='coordinate_difference_count',coordinates=[a,b],difference=difference)))
            sections.append(dict(kind='180exact_difference_counts',first_clause=first,last_clause=clauses.count,count=clauses.count-first+1));first=clauses.count+1
            for p,q in tqdm(list(combinations(range(20),2)),desc='All cyclic lifted column caps'):
                cap.check();begin=clauses.count+1;forbidden=[];maxhist=Counter()
                for x in domains[p]['choices']:
                    xs=[int(v,16) for v in x['lifted_masks_hex']];mask=0
                    for j,y in enumerate(domains[q]['choices']):
                        ys=[int(v,16) for v in y['lifted_masks_hex']];nine=[(a&b).bit_count() for a in xs for b in ys]
                        counts=Counter(nine);need(all(n%3==0 for n in counts.values()),'nineoverlaps repeatin triples')
                        maximum=max(nine);maxhist[maximum]+=1;pairchecks+=1;all9checks+=9
                        if maximum>2:clauses.emit(-x['selector'],-y['selector']);mask|=1<<j
                    forbidden.append(format(mask,'08x'))
                caps.append(dict(groups=[p,q],actual_column_pairs=[[d,e] for d in domains[p]['raw_columns'] for e in domains[q]['raw_columns']],
                    forbidden_right_masks_hex=forbidden,maximum_overlap_histogram=dict(sorted(maxhist.items())),
                    first_clause=begin,clause_count=clauses.count-begin+1))
            sections.append(dict(kind='190all_lifted_cap_choice_relations',first_clause=first,last_clause=clauses.count,count=clauses.count-first+1))
        with (out/'instance.cnf').open('xb') as dest,(out/'clauses.body').open('rb') as src:
            dest.write(f'p cnf {enc.top} {clauses.count}\n'.encode());shutil.copyfileobj(src,dest,1048576)
        model=dict(schema='HADAMARD_SIX_PRISM_CYCLIC_FACTOR_PREFIX_CNF_V1',variables=enc.top,clauses=clauses.count,
            primary_selectors=600,scope_path=key(out/'scope.json'),scope_sha256=digest(out/'scope.json'),domains=domains,
            counter_rows=counterrows,lifted_cap_relations=caps,clause_sections=sections,full_target_encoded=False,
            counter_prefix_reference_format='JSONBooleanconstants; positiveinteger variableIDs.',
            counter_gate_order=dict(and_gate=['a -z','b -z','-a -b z'],or_gate=['-a z','-b z','a b -z'],recurrence=['-a z','-b -c z','a b -z','a c -z']))
        save(out/'model.json',model);cap.check();save(out/'artifact_packages.json',dict(packages=[package(p,cap) for p in [out/'instance.cnf',out/'model.json']],mathematical_verification=False))
        need(all(digest(ROOT/p)==h for p,h in pins.items()),'stableinputs')
        summary=dict(status='CANDIDATE_HADAMARD_CYCLIC_FACTOR_CNF',created_at=created,completed_at=datetime.now(timezone.utc).isoformat(),inputs_sha256=pins,
            outputs_sha256={key(p):digest(p) for p in out.iterdir() if p.is_file()},variables=enc.top,clauses=clauses.count,
            domains=20,choices_per_domain=30,onehot_rows=20,difference_equalities=180,group_pair_choice_checks=pairchecks,lifted_column_pair_checks=all9checks,
            actual_column_pairs_covered=1770,withintriplet_pairs_automatically_disjoint=60,forbidden_choice_pairs=sum(r['clause_count'] for r in caps),
            clause_sections=sections,wall_seconds=time.monotonic()-cap.start,peak_memory_bytes=cap.peak_bytes,solver_calls=0,independent_approval=False,target_resolution='UNKNOWN',
            scope='Extra cyclicfibre-triplet subfamily of onefixedsixprismHadamardL; arbitraryD unencoded.')
        save(out/'summary.json',summary);print(json.dumps({k:v for k,v in summary.items() if k not in ['inputs_sha256','outputs_sha256']}))
    except BaseException as e:save(out/'failure.json',dict(exception=repr(e),elapsed_seconds=time.monotonic()-cap.start));raise

def decode(assignment,model_path=DEFAULT/'model.json',scope_path=DEFAULT/'scope.json'):
    model=read(model_path);scope=read(scope_path);need(digest(scope_path)==model['scope_sha256'],'scopepin')
    values={}
    for v in assignment:need(type(v)is int and v and abs(v) not in values,'uniqueintegerliteral');values[abs(v)]=v>0
    need(set(values)==set(range(1,model['variables']+1)),'completeassignment')
    factor=[[0]*60 for _ in range(36)];selected=[]
    for domain in model['domains']:
        choices=[x for x in domain['choices'] if values[x['selector']]];need(len(choices)==1,'exactonechoice');choice=choices[0];selected.append(choice['selector'])
        for d,rows in zip(domain['raw_columns'],choice['lifted_rows'],strict=True):
            for i in rows:factor[i][d]=1
    need(all(sum(factor[i][d]*factor[j][d] for d in range(60))==scope['target_gram36'][i][j] for i in range(36) for j in range(36)),'literal1296Gram')
    need(all(sum(factor[12*g+a][d] for g in range(3))==scope['L'][a][d] for a in range(12) for d in range(60)),'exactLprojection')
    need(all(sum(factor[12*g+a][d] for a in range(12))==2 for g in range(3) for d in range(60)),'twoeachfibre')
    need(all(sum(factor[i][d]*factor[i][e] for i in range(36))<=2 for d,e in combinations(range(60),2)),'all1770caps')
    pairs=[tuple(i for i in range(12) if factor[i][d]) for d in range(60)];catalog=[p for p in combinations(range(12),2) if p[1]!=(p[0]^1)]
    need(sorted(pairs)==catalog,'exactC0catalog');order=[pairs.index(p) for p in catalog]
    return dict(factor=factor,L=scope['L'],selected_selector_ids=selected,core_adjacency=scope['core_adjacency'],matchings=scope['matchings'],
        M0=scope['matchings'][0],M1=scope['matchings'][1],M2=scope['matchings'][2],P=list(range(12)),target_gram36=scope['target_gram36'],
        canonical_factor=[[r[d] for d in order] for r in factor],canonical_column_order=order,canonical_C0_columns=[list(p) for p in catalog],
        scope_sha256=digest(scope_path),model_sha256=digest(model_path),extra_cyclic_factor_constraint=True,
        residual_D=None,residual_D_reason='Noresidualgraph encoded or automorphism imposed.',target_graph=False,independent_approval=False)

def main():
    ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='mode',required=True)
    b=sub.add_parser('build');b.add_argument('--out',type=Path,required=True)
    d=sub.add_parser('decode');d.add_argument('--assignment',type=Path,required=True);d.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    if args.mode=='build':build(args.out.resolve())
    else:
        a=read(args.assignment);save(args.out,decode(a if type(a)is list else a.get('assignment',a.get('model'))))

if __name__=='__main__':main()
