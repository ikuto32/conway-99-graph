"""Independent complete oriented-triple CNF/raw-object checker. No solver."""
from collections import Counter
import argparse
import copy
from datetime import datetime, timezone
import hashlib
from itertools import combinations, permutations, product
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results';D=B/'20260930_hadamard_oriented_triples'
RAW=B/'20260930_hadamard20_support/six_prism.json'
PINS={
 RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',
 D/'instance.cnf':'7501790d51166b0b62719c2db274cb2581c57ef584c282e333377e4b72060999',
 D/'model.json':'81065b50b0caf2d8a5226570e321738faf47dabee7688f5cad96a17d1e72e5ee',
 D/'scope.json':'88ef7bf36dfd86a749ae84ea045e9707e6c27deff9c21e861d25d80c3de7d2e4',
 ROOT/'acceleration/theory_20260930_hadamard_oriented_triples.py':'1decce90cd18105430dd102a9739f08f46690e2424a6d3837f8ae8d6173c7eac',
 ROOT/'acceleration/theory_20260930_hadamard_oriented_triples_spec.md':'830f2da205da633b547b1ae62bca3103c5f3ac01bcf3301dd23954723450034b',
 B/'20260930_independent_review/hadamard20_support_v2/summary.json':'a8477256446e3e402a2a21241dc383a515162dc9c8c07a9a8e26326c07b0f58f',
 B/'20260930_independent_review/hadamard_general_f3_phase_necessity/summary.json':'30dd4e571140a139f7e36baf47f62a4428b752c79bbddd164ec6e54f3b232d67',
 B/'20260930_independent_review/balanced_phase_matrix_form_v2/summary.json':'c20758ad6c8cdb264a28aae97242efdc70ed8cfc582a914cad624bf83cc60c0b',
 ROOT/'uv.lock':'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',
 ROOT/'pyproject.toml':'273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339',
}

def need(x,message):
    if not x:raise ValueError(message)
def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def save(p,x):
    with Path(p).open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
def same(a,b):return json.dumps(a,sort_keys=True)==json.dumps(b,sort_keys=True)

def phase_domains(support):
    """120 normalized affine maps -> 40 classes, independently enumerated."""
    need(support==sorted(set(support)) and len(support)==6,'six distinct coordinates')
    table={};multiplicity=Counter()
    for p in product(range(2),repeat=6):
        if p[0] or sum(p)!=3:continue
        pos=[i for i in range(6) if not p[i]];neg=[i for i in range(6) if p[i]]
        for a in permutations(range(3)):
            if a[0]:continue
            for b in permutations(range(3)):
                t=[0]*6
                for i,x in zip(pos,a):t[i]=x
                for i,x in zip(neg,b):t[i]=x
                arcs=tuple(sorted((support[i],support[j]) for i in range(6) for j in range(6) if p[i]==p[j] and (t[j]-t[i])%3==1))
                need(len(arcs)==6,'local directed phases')
                multiplicity[arcs]+=1
                # Canonical representatives shift each triple's least phase to zero.
                canonical=t[:]
                for subset in [pos,neg]:
                    for i in subset:canonical[i]=(t[i]-t[subset[0]])%3
                triples=[[support[i] for i in subset] for subset in [pos,neg]]
                cycles=[]
                for subset in [pos,neg]:
                    cycles.append([support[next(i for i in subset if canonical[i]==v)] for v in range(3)])
                bits=[int(cycle[1]!=triple[1]) for cycle,triple in zip(cycles,triples)]
                item=dict(positive_triple=triples[0],negative_triple=triples[1],orientation_bits=bits,
                          positive_cycle=cycles[0],negative_cycle=cycles[1],
                          directed_arcs=[[cycle[i],cycle[(i+1)%3]] for cycle in cycles for i in range(3)],
                          normalized_parity_pattern=list(p),local_phase_representative=canonical)
                need(arcs not in table or same(table[arcs],item),'phase offset quotient')
                table[arcs]=item
    need(len(table)==40 and sum(multiplicity.values())==120 and set(multiplicity.values())=={3},'complete 120-to-40 quotient')
    return sorted(table.values(),key=lambda r:(r['positive_triple'],r['orientation_bits']))

def reconstruct(raw,scope,model):
    L=raw['L'];need(len(L)==12 and all(len(r)==60 and set(r)<={0,1} for r in L),'raw support shape')
    supports=[[a for a in range(12) if L[a][d]] for d in range(60)];groups=[]
    for s in supports:
        if s not in groups:groups.append(s)
    need(len(groups)==20 and all(supports.count(s)==3 and len(s)==6 and all(sum(a in s for a in [2*i,2*i+1])==1 for i in range(6)) for s in groups),'exact support groups')
    arcs=[[a,b] for a in range(12) for b in range(12) if a!=b and a^1!=b]
    need(len(arcs)==120 and all(sum(a in s and b in s for s in groups)==5 for a,b in arcs),'literal fivefold pair support')
    expected_scope=dict(schema='FIXED_HADAMARD_ALL_MIXED_ORIENTED_TRIPLE_SCOPE_V1',raw_support_path=key(RAW),raw_support_sha256=PINS[RAW],coordinate_matching=[a^1 for a in range(12)],L12x60=L,support_columns=supports,groups=groups,directed_arcs=arcs,
        balance_is_additional_assumption=True,all_groups_mixed=True,local_even_phase_screen_only=True,odd_phase_equations_encoded=False,outside_column_caps_encoded=False,full_factor=False,target_graph=False,residual_D=None,residual_D_null_reason='No residual completion is part of this projection.',scope='All oriented same-sign triples on one frozen support; exact equivalent local mixed/even-phase screen, pending independent review. No claim of arbitrary-factor coverage.')
    need(same(scope,expected_scope),'complete raw scope including limitations')
    domains=[]
    for g,s in enumerate(groups):
        choices=phase_domains(s)
        for i,item in enumerate(choices):item['choice_index']=i;item['selector']=40*g+i+1
        domains.append(dict(group=g,support=s,choices=choices))
    rows=[]
    for g,domain in enumerate(domains):rows.append(dict(index=len(rows),kind='group_exact_one',group=g,selectors=[x['selector'] for x in domain['choices']],rhs=1))
    for arc in arcs:rows.append(dict(index=len(rows),kind='directed_arc_exact_one',directed_arc=arc,selectors=[x['selector'] for domain in domains for x in domain['choices'] if arc in x['directed_arcs']],rhs=1))
    clauses=[]
    for row in rows:
        ids=row['selectors'];need(len(ids)==40 and ids==sorted(set(ids)),'literal forty-selector row')
        row['first_clause']=len(clauses)+1;row['clause_count']=781
        clauses.append(ids)
        clauses.extend([[-a,-b] for a,b in combinations(ids,2)])
    expected_model=dict(schema='FIXED_HADAMARD_ALL_MIXED_ORIENTED_TRIPLE_CNF_V1',variables=800,clauses=109340,primary_selectors=800,auxiliary_variables=0,domains=domains,exact_one_rows=rows,clause_order='20 groups then120 directed arcs; positive row then lexicographic negative selector pairs',scope_sha256=PINS[D/'scope.json'],scope_sha256_null_reason=None,independent_approval=False)
    need(same(model,expected_model),'complete independently reconstructed model')
    need(len(rows)==140 and len(clauses)==109340,'complete dimensions')
    return domains,arcs,clauses

def cnf_bytes(clauses,n):
    return ('p cnf '+str(n)+' '+str(len(clauses))+'\n'+''.join(' '.join(map(str,c))+' 0\n' for c in clauses)).encode('ascii')

def assignment(literals,n):
    need(type(literals)is list,'assignment list')
    values={}
    for lit in literals:
        need(type(lit)is int and 1<=abs(lit)<=n and abs(lit) not in values,'unique nonzero signed IDs')
        values[abs(lit)]=lit>0
    need(set(values)==set(range(1,n+1)),'complete assignment IDs')
    return values

def native(text,n):
    status=[];literals=[];terminated=False
    for line in text.splitlines():
        fields=line.split()
        if not fields:continue
        if fields[0]=='s':status.append(fields[1:])
        elif fields[0]=='v':
            need(not terminated,'native literal after terminal zero')
            for j,token in enumerate(fields[1:]):
                lit=int(token)
                if lit==0:
                    need(j==len(fields)-2,'native literal after zero');terminated=True
                else:need(not terminated,'post-zero native literal');literals.append(lit)
    need(status==[['SATISFIABLE']] and terminated,'single SAT status and terminal zero')
    return assignment(literals,n)

def all_clauses(clauses,values):
    for i,c in enumerate(clauses):need(any(values[abs(lit)]==(lit>0) for lit in c),'unsatisfied raw clause '+str(i+1))

def raw_cover(selected,arcs):
    counts=Counter(tuple(a) for item in selected for a in item['directed_arcs'])
    need(counts==Counter({tuple(a):1 for a in arcs}),'literal exact directed-arc cover')
    return [dict(arc=a,count=counts[tuple(a)]) for a in arcs]

def check_object(values,domains,arcs,clauses,decoded=None):
    all_clauses(clauses,values);selected=[]
    for domain in domains:
        active=[x for x in domain['choices'] if values[x['selector']]]
        need(len(active)==1,'one selected choice per group');selected.append(active[0])
    counts=raw_cover(selected,arcs)
    patterns=[x['normalized_parity_pattern'] for x in selected]
    even=[]
    for a,b in combinations(range(12),2):
        if a^1==b:continue
        phases=[];odd=0
        for domain,item in zip(domains,selected):
            if a not in domain['support'] or b not in domain['support']:continue
            i,j=domain['support'].index(a),domain['support'].index(b)
            p=item['normalized_parity_pattern'];t=item['local_phase_representative']
            if p[i]!=p[j]:odd+=1
            else:phases.append((t[j]-t[i])%3)
        need(odd==3 and sorted(phases)==[1,2],'literal parity and even phase necessity')
        even.append(dict(coordinates=[a,b],disagreements=odd,even_relative_phases=phases))
    obj=dict(selected_selector_ids=[x['selector'] for x in selected],selected_choices=selected,selected_group_parity_patterns=patterns,directed_arc_counts=counts,
             model_sha256=PINS[D/'model.json'],scope_sha256=PINS[D/'scope.json'],full_factor=False,target_graph=False,
             odd_phase_equations_checked=False,outside_column_caps_checked=False,residual_D=None,independent_approval=False,
             scope='Oriented local/even-phase cover only; twenty negative-triple offsets remain to be solved.')
    if decoded is not None:need(same(decoded,obj),'all independently decoded producer fields')
    return obj,even

def calibrate(model,scope,raw,domains,arcs,clauses):
    rejected=[]
    def reject(name,fn):
        try:fn()
        except(ValueError,TypeError,KeyError,IndexError):rejected.append(name)
        else:raise ValueError('accepted corruption '+name)
    truth=0
    for n in range(1,8):
        cs=[list(range(1,n+1))]+[[-a,-b] for a,b in combinations(range(1,n+1),2)]
        for bits in product([False,True],repeat=n):
            vals=dict(enumerate(bits,1))
            valid=all(any(vals[abs(x)]==(x>0) for x in c) for c in cs)
            need(valid==(sum(bits)==1),'exhaustive exact-one equivalence');truth+=1
    local=phase_domains(list(range(6)))
    for item in local:
        p=item['normalized_parity_pattern'];t=item['local_phase_representative'];s=[1-2*b for b in p]
        words=[[(s[i]*x+t[i])%3 for i in range(6)] for x in range(3)]
        need(all(Counter(w)==Counter({0:2,1:2,2:2}) for w in words),'literal local balanced columns')
        need(all(set(w[i] for w in words)=={0,1,2} for i in range(6)),'local coordinate permutations')
        for shift in range(3):
            tt=[(x+shift*p[i])%3 for i,x in enumerate(t)]
            need(all((tt[v]-tt[u])%3==1 for u,v in item['directed_arcs']),'negative offsets preserve arcs')
    paircases=0
    for a,b in product([1,2],repeat=2):
        need(((a+b)%3==0)==(sorted([a,b])==[1,2]),'nonzero even-phase equivalence');paircases+=1
    faces=[[0,1,2],[0,3,1],[0,2,3],[1,3,2]]
    generic=[dict(directed_arcs=[[f[i],f[(i+1)%3]] for i in range(3)]) for f in faces]
    generic_arcs=[[a,b] for a in range(4) for b in range(4) if a!=b]
    raw_cover(generic,generic_arcs)
    bad=copy.deepcopy(generic);bad[0]['directed_arcs'][0].reverse();reject('generic_reversed_arc',lambda:raw_cover(bad,generic_arcs))
    reject('generic_missing_face',lambda:raw_cover(generic[:-1],generic_arcs))
    for name in ['missing_choice','wrong_phase','wrong_parity','wrong_arc','wrong_selector','wrong_row_support','wrong_scope','scope_odd_flag']:
        m,s=copy.deepcopy(model),copy.deepcopy(scope)
        if name=='missing_choice':m['domains'][0]['choices'].pop()
        elif name=='wrong_phase':m['domains'][0]['choices'][0]['local_phase_representative'][0]=1
        elif name=='wrong_parity':m['domains'][0]['choices'][0]['normalized_parity_pattern'][0]=1
        elif name=='wrong_arc':m['domains'][0]['choices'][0]['directed_arcs'][0].reverse()
        elif name=='wrong_selector':m['domains'][0]['choices'][0]['selector']=2
        elif name=='wrong_row_support':m['exact_one_rows'][20]['selectors'][0]+=1
        elif name=='wrong_scope':s['all_groups_mixed']=False
        else:s['odd_phase_equations_encoded']=True
        reject(name,lambda m=m,s=s:reconstruct(raw,s,m))
    bad=copy.deepcopy(clauses);bad[0][0]*=-1
    reject('signed_formula_corruption',lambda:need(cnf_bytes(bad,800)==(D/'instance.cnf').read_bytes(),'all raw formula bytes'))
    reject('omitted_clause',lambda:need(cnf_bytes(clauses[:-1],800)==(D/'instance.cnf').read_bytes(),'complete formula'))
    literals=[i if i%2 else -i for i in range(1,801)];values=assignment(literals,800)
    text='c SYNTHETIC CODEC ONLY\ns SATISFIABLE\n'+'\n'.join('v '+' '.join(map(str,literals[i:i+31])) for i in range(0,800,31))+' 0\n'
    need(native(text,800)==values,'all800 native/JSON identities')
    synthetic=[[literals[i%800]] for i in range(109340)];all_clauses(synthetic,values)
    for name,txt in [('no_status',text.replace('s SATISFIABLE\n','')),('wrong_status',text.replace('s SATISFIABLE','s UNKNOWN')),('missing_zero',text.replace(' 0\n','\n')),('duplicate_ID',text.replace('v 1 -2','v 1 1')),('post_zero',text+'v 1\n'),('out_of_range',text.replace('v 1 -2','v 801 -2')),('native_zero_early',text.replace('v 1 -2','v 0 -2'))]:reject(name,lambda txt=txt:native(txt,800))
    reject('missing_JSON_ID',lambda:assignment(literals[:-1],800));reject('Boolean_JSON_literal',lambda:assignment([True,*literals[1:]],800))
    wrong=copy.deepcopy(synthetic);wrong[0][0]*=-1;reject('false_synthetic_clause',lambda:all_clauses(wrong,values))
    firstvals={i:((i-1)%40==0) for i in range(1,801)}
    reject('first_choices_are_not_research_cover',lambda:check_object(firstvals,domains,arcs,clauses))
    return dict(exact_one_truth_cases=truth,local_phase_orbits=40,local_normalized_assignments=120,negative_offset_controls=120,nonzero_even_phase_cases=paircases,generic_positive='Tetrahedron oriented faces only; not research support.',synthetic_positive='800 IDs and109340 synthetic unit clauses; not research SAT.',known_research_positive=None,known_research_positive_reason='No authenticated research oriented cover available at calibration time.',corruptions_rejected=rejected),text,synthetic

def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['audit','calibrate','sat']);ap.add_argument('--encoding-gate',type=Path);ap.add_argument('--encoding-gate-sha256');ap.add_argument('--assignment',type=Path);ap.add_argument('--native-output',type=Path);ap.add_argument('--decoded',type=Path);ap.add_argument('--driver',type=Path);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.perf_counter();pins={}
    def pin(p,h=None):
        p=p.resolve();value=sha(p);need(h is None or h==value,'input identity '+key(p));pins[key(p)]=value
    try:
        for p,h in PINS.items():pin(p,h)
        producer=read(D/'summary.json');pin(D/'summary.json')
        for p,h in {**producer['inputs_sha256'],**producer['outputs_sha256']}.items():pin(ROOT/p,h)
        pin(Path(__file__));pin(ROOT/'docs/AUDIT_20260930_HADAMARD_ORIENTED_TRIPLES.md')
        if args.driver:
            need(args.driver.resolve()==ROOT/'acceleration/native_20260930_hadamard_oriented_triples.py','intended native wrapper')
            pin(args.driver,'a68889732e48f87889b5adfd81f893964b638970f83f4fcc4cce1271d37d74b7')
            pin(args.driver.with_suffix('.md'),'eed1599dfdeccfd15ff39b85846ece5bb7447288a6a3721faf02d281cbb17e14')
        raw,scope,model=read(RAW),read(D/'scope.json'),read(D/'model.json')
        domains,arcs,clauses=reconstruct(raw,scope,model)
        need(cnf_bytes(clauses,800)==(D/'instance.cnf').read_bytes(),'every actual raw CNF byte')
        if args.mode!='audit':
            need(args.encoding_gate is not None and args.encoding_gate_sha256,'explicit encoding gate')
            pin(args.encoding_gate,args.encoding_gate_sha256);gate=read(args.encoding_gate)
            need(gate['status']=='INDEPENDENT_HADAMARD_ORIENTED_TRIPLE_ENCODING_PASS','approved exact encoding')
            for p in [RAW,D/'instance.cnf',D/'model.json',D/'scope.json',Path(__file__)]:need(gate['inputs_sha256'][key(p)]==pins[key(p)],'same gate input '+key(p))
        counts,text,synthetic=calibrate(model,scope,raw,domains,arcs,clauses)
        save(out/'controls.json',counts)
        (out/'synthetic_native.log').write_text(text,encoding='ascii')
        (out/'synthetic.cnf').write_bytes(cnf_bytes(synthetic,800))
        if args.mode=='sat':
            need(args.assignment is not None and args.native_output is not None,'raw assignment and native stdout required')
            pin(args.assignment);pin(args.native_output)
            data=read(args.assignment);vals=assignment(data['assignment'] if isinstance(data,dict) else data,800)
            need(vals==native(args.native_output.read_text(encoding='utf-8'),800),'whole native/JSON equality')
            dec=None
            if args.decoded:pin(args.decoded);dec=read(args.decoded)
            obj,even=check_object(vals,domains,arcs,clauses,dec)
            save(out/'independent_projection.json',obj);save(out/'independent_even_phase_checks.json',even)
        ts=datetime.now(timezone.utc).isoformat()
        save(out/'manifest.json',dict(timestamp=ts,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),uv=subprocess.check_output(['uv','--version'],text=True).strip(),inputs_sha256=pins,elapsed_seconds=time.perf_counter()-start,solver_calls=0))
        if args.mode=='audit':
            save(out/'claim_binding.json',dict(id='C-FIXED-HADAMARD-ALL-MIXED-ORIENTED-TRIPLE-ENCODING',revision=1,kind='encoding',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',
                statement='The frozen800-variable109340-clause CNF is equivalent to choosing one oriented pair of sign triples in each of20fixed support groups and covering all120directed nonmatching arcs exactly once. This is equivalent, modulo independent negative-triple phase offsets, to the all-mixed local and even-relative-phase screen. Every balanced full-Gram factor in this fixed-support all-mixed family projects to it.',
                scope='Only the fixed six-prism Hadamard support and all-mixed balanced subfamily; no odd-phase, outside-cap or residual-D equivalence.',assumptions=['Pinned fixed support/core.','Additional balanced triples and all20groups mixed.'],
                dependencies=[dict(id='C-FIVE-FIXED-HADAMARD20-SUPPORT-PROJECTIONS',revision=1,relation='premise'),dict(id='C-FIXED-HADAMARD-GENERAL-BALANCED-GF3-PHASE-NECESSITY',revision=1,relation='uses_result'),dict(id='C-FIXED-HADAMARD-BALANCED-PHASE-MATRIX-FORM',revision=1,relation='uses_result')],
                verifier='/root/structural_attack',producer='/root/state_literature_audit',method='Independent local phase enumeration, full raw scope/domain/row and byte reconstruction, exact derivation and corruption controls.',shared_components=['Pinned raw support and independently reviewed mathematical statements.','Python standard-library exact arithmetic/JSON; no producer/helper source imports.'],
                artifact_availability='LOCAL_ONLY',availability_reason='Workspace artifacts pending parent publication.',external_review=None,external_review_reason='No external review asserted.',limitations=['No actual SAT/UNSAT outcome in this gate.','No full factor or target graph.','Constant-containing balanced branches are not covered.'],created_at=ts,updated_at=ts,inputs_sha256=pins,evidence_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()}))
        status={'audit':'INDEPENDENT_HADAMARD_ORIENTED_TRIPLE_ENCODING_PASS','calibrate':'INDEPENDENT_HADAMARD_ORIENTED_TRIPLE_OBJECT_CALIBRATION_PASS','sat':'INDEPENDENT_HADAMARD_ORIENTED_TRIPLE_SAT_OBJECT_PASS'}[args.mode]
        report=dict(status=status,timestamp=ts,inputs_sha256=pins,outputs_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},variables=800,clauses=109340,group_domains=20,choices_per_group=40,exact_one_rows=140,local_phase_assignments_checked=2400,directed_arc_rows=120,controls=counts,solver_calls=0,target_resolution=False,scope='All-mixed balanced fixed-support local/even screen only; odd equations, caps and residualD omitted.')
        save(out/'summary.json',report);print(json.dumps(dict(status=status,summary_sha256=sha(out/'summary.json'),source_sha256=sha(Path(__file__)))))
    except BaseException as ex:save(out/'failure.json',dict(error=repr(ex)));raise

if __name__=='__main__':main()
