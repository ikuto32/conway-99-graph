"""Independent literal-set fixed-point certificate for the frozen coarse60 scout.

No producer/checker imports. The research path proves every conditioned value
has a direct support on every incident binary relation; it does not run AC-3.
Tiny controls use simultaneous sweeps and exhaustive greatest-fixed-point sets.
"""
import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
B = 'acceleration/results/20260930_'
I = B+'independent_review/'
RUN = B+'prism_coarse60_arc/'
MODEL = B+'prism_coarse60_bitlift/model.json'
TEMPLATE = B+'prism_coarse_complement/coarse_template.json'
EXT = B+'prism_coarse60_bitflip/extension.json'
GATE = I+'prism_coarse60_bitlift_cnf/summary.json'
PINS = {
    RUN+'summary.json': '687fadb768581892e3e30d621dd333dbdddb60870b4ff045243e3c6faa61e45e',
    RUN+'trace.json': '28c406d8dc63c65f7d97051fec5feef929e325f9e56da83052a54f44b1b9b215',
    MODEL: 'a437d3f1381e9554bff2376726a991f1d1e0ea23c240f8ebacf005c57e82fcb5',
    TEMPLATE: 'e391dec13d58ed2484d1fc0cb9d856ac53771e0e51305a265f244e9a8f082ae2',
    EXT: '4838c853fc99f3ffbb3736aa234e30a3f2a6f90da67b1a50217c132efe2f8c83',
    GATE: 'b82eb3d3c999ae8bdcdbfd246dd28ea9cd6a9dd8d1ce811abc82ee0f3e38d88d',
}

def need(ok, why):
    if not ok: raise ValueError(why)

def digest(p):
    with p.open('rb') as f:
        h=sha256()
        for chunk in iter(lambda:f.read(1048576),b''): h.update(chunk)
    return h.hexdigest()

def key(p): return p.resolve().relative_to(ROOT).as_posix()
def read(p): return json.loads((ROOT/p).read_bytes())
def save(p,obj):
    with p.open('x',encoding='utf-8',newline='\n') as f: json.dump(obj,f,indent=2);f.write('\n')
def hexset(values): return format(sum(1<<v for v in values),'034x')

def sweeps(initial, relations):
    """Simultaneous monotone revision, distinct from producer AC queue."""
    current=[set(x) for x in initial]
    while True:
        following=[{v for v in values if all(any((v,w) in allowed for w in current[j])
                    for (i,j),allowed in relations.items() if i==di)}
                   for di,values in enumerate(current)]
        if following==current: return current
        current=following

def fixed(values,relations):
    return all(all(any((v,w) in allowed for w in values[j]) for v in values[i])
               for (i,j),allowed in relations.items())

def support_check(initial, supports, relations):
    need(set(supports)==set(relations),'complete directed arc inventory')
    checks=0
    for (i,j),allowed in relations.items():
        need(set(supports[i,j])==initial[i],'every live value occurs once')
        for value,witness in supports[i,j].items():
            need(witness in initial[j] and (value,witness) in allowed,'literal support exists')
            checks+=1
    return checks

def reject(name,operation,records):
    try: operation()
    except (ValueError,KeyError,IndexError,TypeError): records.append(dict(name=name,rejected=True))
    else: raise AssertionError('corrupt control accepted: '+name)

def controls():
    cases=0
    subsets=[set(),{0},{1},{0,1}]
    for mask in range(16):
        allowed={(x,y) for x,y in product(range(2),repeat=2) if mask>>(2*x+y)&1}
        relations={(0,1):allowed,(1,0):{(y,x) for x,y in allowed}}
        for first,second in product(subsets[1:],repeat=2):
            initial=[first,second];actual=sweeps(initial,relations)
            candidates=[[a,b] for a,b in product(subsets,repeat=2)
                        if a<=first and b<=second and fixed([a,b],relations)]
            greatest=[set().union(*(c[i] for c in candidates)) for i in range(2)]
            need(actual==greatest,'complete greatest-fixed-point control')
            solutions=[(a,b) for a,b in product(sorted(first),sorted(second)) if (a,b) in allowed]
            need(all(a in actual[0] and b in actual[1] for a,b in solutions),'no valid assignment removed')
            cases+=1
    equality={(0,0),(1,1)}
    chain={(0,1):equality,(1,0):equality,(1,2):equality,(2,1):equality}
    need(sweeps([{0},{0,1},{0,1}],chain)==[{0}]*3,'known positive propagating chain')
    need(sweeps([{0},{1}],{(0,1):equality,(1,0):equality})==[set(),set()],'known contradiction')
    triangle={(i,j):{(0,1),(1,0)} for i in range(3) for j in range(3) if i!=j}
    initial=[{0,1}]*3
    need(sweeps(initial,triangle)==initial,'arc-consistent odd cycle')
    need(not [x for x in product(range(2),repeat=3) if all((x[i],x[j]) in r for (i,j),r in triangle.items())],
         'complete enumeration shows arc consistency is not feasibility')
    tiny={(0,1):{0:0,1:1},(1,0):{0:0,1:1}}
    rel={(0,1):equality,(1,0):equality}
    need(support_check([{0,1}]*2,tiny,rel)==4,'positive support certificate')
    negative=[]
    for name,mutate in [
        ('missing_reverse_arc',lambda x:x.pop((1,0))),
        ('missing_value',lambda x:x[0,1].pop(1)),
        ('invalid_witness',lambda x:x[0,1].update({0:1})),
        ('out_of_domain_witness',lambda x:x[0,1].update({0:2})),
        ('unexpected_value',lambda x:x[0,1].update({2:0})),
        ('extra_arc',lambda x:x.update({(0,0):{0:0}})),
    ]:
        bad=deepcopy(tiny);mutate(bad)
        reject(name,lambda:support_check([{0,1}]*2,bad,rel),negative)
    return dict(exhaustive_two_variable_cases=cases,positive_propagating_chain=True,
        contradiction=True,arc_consistent_but_unsatisfiable_triangle=True,
        known_positive_support_checks=4,corruptions=negative)

def reconstruct(model, columns, raw_domains):
    need(len(columns)==60 and len({tuple(c) for c in columns})==60,'fixed distinct template')
    need(len(model['domains'])==18 and len(raw_domains)==18,'18 domains')
    sets=[]
    for di in range(18):
        a,g=divmod(di,3);d=model['domains'][di];raw=raw_domains[di]
        positions=[c for c,word in enumerate(columns) if word[a]==g]
        need((d['component'],d['fibre'])==(a,g)==(raw['component'],raw['fibre']),'domain labels')
        need(d['column_positions']==raw['column_positions']==positions and len(positions)==20,'literal column positions')
        need(d['local_masks']==raw['survivors'] and len(set(raw['survivors']))==136,'authenticated local domain order')
        need(d['selectors']==list(range(136*di+1,136*(di+1)+1)),'selector IDs')
        family=[]
        for mask,global_hex in zip(d['local_masks'],d['global_bit1_masks_hex'],strict=True):
            need(type(mask) is int and 0<=mask<2**20,'local mask domain')
            actual=frozenset(c for i,c in enumerate(positions) if mask//(2**i)%2)
            need(len(actual)==10,'weight10 domain')
            need(sum(2**c for c in actual)==int(global_hex,16),'global literal set equals recorded mask')
            family.append(actual)
        sets.append(family)
    need(model['raw_bits']==[dict(variable=2449+6*c+a,column=c,component=a,fibre=columns[c][a])
            for c in range(60) for a in range(6)],'complete literal raw-bit mapping')
    return sets

def conditioned(model,extension,sets,columns):
    expected=[-(2449+a) for a in range(6)]
    need(extension['appended_unit_literals']==expected,'exact six negative column-zero units')
    need(extension['first_column_records']==model['raw_bits'][:6],'unit raw-bit mapping')
    current=[];fixed_records=[]
    for di,family in enumerate(sets):
        a,g=divmod(di,3)
        live={v for v,s in enumerate(family) if g!=columns[0][a] or 0 not in s}
        current.append(live)
        if g==columns[0][a]:
            need(len(live)==68,'six half-domains')
            fixed_records.append(dict(domain=di,unit=expected[a],local_position=model['domains'][di]['column_positions'].index(0),
                removed_values=[dict(value=v,selector=136*di+v+1) for v in range(136) if v not in live]))
        else: need(len(live)==136,'other domains unconditioned')
    need(len(fixed_records)==6 and sum(map(len,current))==2040,'conditioned population')
    return current,fixed_records

def relation_inventory(model,sets):
    expected=[(i,j) for i in range(18) for j in range(i+1,18) if i//3!=j//3]
    need([(r['left_domain'],r['right_domain']) for r in model['Gram_relations']]==expected,'all135binaryrelations')
    relations={};pairchecks=0
    for r in model['Gram_relations']:
        i,j=r['left_domain'],r['right_domain'];target=1 if i%3==j%3 else 2
        need(r['target_bit11']==target,'target derived from literal fibre labels')
        allowed=set()
        for a,x in enumerate(sets[i]):
            row=[]
            for b,y in enumerate(sets[j]):
                if len(x.intersection(y))==target: allowed.add((a,b));row.append(b)
                pairchecks+=1
            need(sum(2**b for b in row)==int(r['allowed_right_masks_hex'][a],16),'every raw relation coefficient')
        relations[i,j]=allowed;relations[j,i]={(b,a) for a,b in allowed}
    need(len(relations)==270 and pairchecks==2496960,'complete coefficient population')
    return relations,pairchecks

def check_trace(trace,current,fixed_records,checks):
    expected=[hexset(s) for s in current]
    need(trace['initial_domains']==expected and trace['final_domains']==expected,'exact initial/final conditioned sets')
    need(trace['fixed_bit_removals']==fixed_records,'every unit-conditioned deletion')
    need(trace['removals']==[] and trace['empty_domains']==[],'zero AC deletions and no empty domain')
    need(trace['initial_sizes']==trace['final_sizes']==list(map(len,current)),'per-domain sizes')
    need(trace['arc_queue_visits']==270 and trace['final_live_value_arc_checks']==checks,'zero-revision queue accounting')
    need(trace['relation_model']==MODEL and trace['relation_model_sha256']==PINS[MODEL],'exact model trace binding')
    need(trace['global_feasibility'] is None,'no joint feasibility claim')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    out=args.out.resolve();need(out.is_relative_to(ROOT),'workspace output');out.mkdir(parents=True,exist_ok=False)
    started=time.monotonic();now=datetime.now(timezone.utc).isoformat();bindings={}
    try:
        calibration=controls();save(out/'controls.json',calibration)
        for p,h in PINS.items():need(digest(ROOT/p)==h,'frozen input '+p);bindings[p]=h
        summary=read(RUN+'summary.json');gate=read(GATE)
        need(gate['status']=='INDEPENDENT_SIX_PRISM_COARSE60_BITLIFT_CNF_PASS','independent encoding premise')
        for name,h in summary['inputs_sha256'].items():need(digest(ROOT/name)==h,'producer raw input '+name);bindings[name]=h
        for name,h in summary['outputs_sha256'].items():need(digest(ROOT/name)==h,'producer raw output '+name);bindings[name]=h
        model=read(MODEL);columns=read(TEMPLATE)['columns60'];extension=read(EXT)
        raw=[read(d['source_path']) for d in model['domains']]
        for d in model['domains']:need(digest(ROOT/d['source_path'])==d['source_sha256'],'local domain raw identity')
        sets=reconstruct(model,columns,raw);current,fixed_records=conditioned(model,extension,sets,columns)
        relations,pairchecks=relation_inventory(model,sets)
        certificates=[];supports={};hist=Counter()
        for (i,j),allowed in sorted(relations.items()):
            values=sorted(current[i]);witnesses=[];counts=[]
            for v in values:
                candidates=sorted(w for w in current[j] if (v,w) in allowed)
                need(candidates,'every conditioned value retains support');witnesses.append(candidates[0]);counts.append(len(candidates));hist[len(candidates)]+=1
            supports[i,j]=dict(zip(values,witnesses,strict=True))
            certificates.append(dict(source_domain=i,target_domain=j,source_values=values,witness_values=witnesses,support_counts=counts))
        checks=support_check(current,supports,relations);need(checks==30600,'complete live directed supports')
        save(out/'direct_supports.json',dict(schema='COARSE60_DIRECT_LITERAL_SUPPORTS_V1',initial_values=[sorted(s) for s in current],arcs=certificates,
            input_hashes={p:PINS[p] for p in (MODEL,TEMPLATE,EXT)},checks=checks))
        # Separate saved-certificate replay uses literal raw column-set intersection,
        # not relation matrices, producer bitset code, or the generated supports dict.
        written=json.loads((out/'direct_supports.json').read_bytes());replayed=0
        for cert in written['arcs']:
            i,j=cert['source_domain'],cert['target_domain'];target=1 if i%3==j%3 else 2
            need(cert['source_values']==sorted(current[i]),'raw certificate live-value coverage')
            for v,w in zip(cert['source_values'],cert['witness_values'],strict=True):
                need(w in current[j] and sum(c in sets[j][w] for c in sets[i][v])==target,'direct raw witness replay')
                replayed+=1
        need(replayed==checks,'complete saved-certificate replay')
        trace=read(RUN+'trace.json');check_trace(trace,current,fixed_records,checks)
        for k,v in dict(local_domains=18,choices_before_conditioning=2448,fixed_bit_removed_values=408,
                choices_after_conditioning=2040,AC_removed_values=0,final_choices=2040,final_domain_sizes=list(map(len,current)),
                empty_domains=[],complete_binary_relations=135,directed_arcs=270,raw_selector_pairs_reconstructed=pairchecks,
                arc_queue_visits=270,final_live_value_arc_checks=checks,solver_calls=0).items():need(summary[k]==v,'recorded result '+k)
        corrupt=[]
        for name,change in [
            ('trace_deletes_live_value',lambda x:x['final_domains'].__setitem__(0,hexset(current[0]-{min(current[0])}))),
            ('trace_invents_removal',lambda x:x['removals'].append(dict(domain=0,value=68,neighbor=3))),
            ('trace_forgets_unit_deletion',lambda x:x['fixed_bit_removals'][0]['removed_values'].pop()),
            ('trace_false_support_count',lambda x:x.update(final_live_value_arc_checks=30599)),
            ('trace_claims_feasibility',lambda x:x.update(global_feasibility=True)),
        ]:
            bad=deepcopy(trace);change(bad);reject(name,lambda:check_trace(bad,current,fixed_records,checks),corrupt)
        bad=deepcopy(extension);bad['appended_unit_literals'][0]*=-1
        reject('wrong_sign_unit',lambda:conditioned(model,bad,sets,columns),corrupt)
        bad=deepcopy(model);bad['domains'][0]['global_bit1_masks_hex'][0]='0'
        reject('wrong_raw_global_mask',lambda:reconstruct(bad,columns,raw),corrupt)
        bad=deepcopy(model);bad['Gram_relations'][0]['target_bit11']=2
        reject('wrong_relation_target',lambda:relation_inventory(bad,sets),corrupt)
        bad=deepcopy(model);bad['Gram_relations'].pop()
        reject('missing_binary_relation',lambda:relation_inventory(bad,sets),corrupt)
        bad=deepcopy(supports);bad[0,3][min(current[0])]=0
        need(0 not in current[3],'control uses forbidden witness')
        reject('research_witness_violates_unit',lambda:support_check(current,bad,relations),corrupt)
        save(out/'research_corruptions.json',dict(controls=corrupt))
        doc=ROOT/'docs/AUDIT_20260930_PRISM_COARSE60_ARC.md'
        for p in [Path(__file__),doc,ROOT/'uv.lock',ROOT/'pyproject.toml']:bindings[key(p)]=digest(p)
        need(all(digest(ROOT/p)==h for p,h in bindings.items()),'input stability')
        statement='In the frozen 18-domain coarse60 binary-Gram CSP, fixing all six actual bits in column zero to zero removes exactly408 of2448 local domain values; all2040 remaining values have a support in each of their15 neighboring domains, so the conditioned domains are already an arc-consistent fixed point and AC-3 removes no additional value.'
        report=dict(status='INDEPENDENT_SIX_PRISM_COARSE60_ARC_FIXEDPOINT_PASS',created_at=now,updated_at=datetime.now(timezone.utc).isoformat(),
            source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),
            python=platform.python_version(),inputs_sha256=bindings,outputs_sha256={key(p):digest(p) for p in out.iterdir() if p.is_file()},
            claim_id='C-SIX-PRISM-COARSE60-UNIT-CONDITIONED-ARC-FIXEDPOINT',claim_revision=1,statement=statement,
            kind='empirical/engineering result',basis=['COMPUTED'],recommendation='VERIFIED',review_state='CLEAR',
            scope='The exact frozen60coarse-word template,18authenticated136-value domains,135binaryGramrelations and six explicit column-zero bit conditions only.',
            dependencies=[dict(id='C-SIX-PRISM-COARSE60-EXACT-BITLIFT-CNF',revision=1,relation='uses_result'),
                dict(id='C-SIX-PRISM-COMPLEMENT60-SINGLE-ROW-DOMAINS',revision=1,relation='premise')],
            assumptions=['No hypothetical target automorphism is assumed.','The explicit six fixed bits are conditions; normalization coverage is not used in this claim.'],
            verifier='/root/eight_domain_audit',method='independent_artifact_check',
            shared_components=['Frozen raw domain/encoding artifacts and their earlier independent gates are reused as premises.','This checker imports only Python standard library; no producer, prior checker, AC queue or bitset relation code is imported.'],
            counts=dict(conditioned_values=2040,unit_removed_values=408,AC_removed_values=0,directed_arcs=270,
                full_relation_coefficients=pairchecks,independently_saved_and_replayed_supports=checks,conditioned_domain_sizes=list(map(len,current)),
                support_count_histogram=dict(sorted(hist.items())),tiny_exhaustive_cases=calibration['exhaustive_two_variable_cases'],corruptions=len(corrupt)+len(calibration['corruptions'])),
            limitations=['No jointly compatible selection is exhibited.','Outside-column overlap caps are omitted from this propagation study.',
                'No target graph, residual adjacency, family exclusion, unrestricted coverage or novelty claim.',
                'The producer elapsed time is retained as historical evidence; this audit does not certify a performance claim.'],
            artifact_availability='LOCAL_ONLY',retrieval='Exact raw input paths and generated direct_supports.json are included in this report; immutable publication has not yet been confirmed.',
            target_resolution=False,external_review=False,overall_search_coverage='UNKNOWN; no validated denominator.',wall_seconds=time.monotonic()-started)
        save(out/'summary.json',report);print(json.dumps(dict(status=report['status'],summary_sha256=digest(out/'summary.json'),checks=checks,wall_seconds=report['wall_seconds'])))
    except BaseException as exc:
        save(out/'failure.json',dict(error=repr(exc),timestamp=datetime.now(timezone.utc).isoformat(),source_sha256=digest(Path(__file__))));raise

if __name__=='__main__':main()
