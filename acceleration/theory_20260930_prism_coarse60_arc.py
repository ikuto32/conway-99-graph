"""Exact candidate AC-3 scout; no SAT call or independent self-approval."""
import argparse
from collections import deque
from datetime import datetime, timezone
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'acceleration/results/20260930_prism_coarse60_bitlift'
EXT=ROOT/'acceleration/results/20260930_prism_coarse60_bitflip/extension.json'
EXT_HASH='4838c853fc99f3ffbb3736aa234e30a3f2a6f90da67b1a50217c132efe2f8c83'
GATE=ROOT/'acceleration/results/20260930_independent_review/prism_coarse60_bitlift_cnf/summary.json'
GATE_HASH='b82eb3d3c999ae8bdcdbfd246dd28ea9cd6a9dd8d1ce811abc82ee0f3e38d88d'

def need(ok, why):
    if not ok: raise ValueError(why)
def digest(p):return sha256(p.read_bytes()).hexdigest()
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(p.read_bytes())
def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
def mask_string(x):return format(x,'034x')

def arc_consistency(initial, relations, deadline):
    current=initial[:];queue=deque(sorted(relations));queued=set(queue);trace=[];visits=0
    while queue:
        need(time.monotonic()<deadline,'resource limit')
        i,j=queue.popleft();queued.remove((i,j));visits+=1;changed=False
        for value,support in enumerate(relations[i,j]):
            if (current[i]>>value)&1 and not support&current[j]:
                trace.append(dict(domain=i,value=value,neighbor=j,support_mask=mask_string(support),
                                  neighbor_current_mask=mask_string(current[j]),intersection_mask=mask_string(0)))
                current[i]&=~(1<<value);changed=True
        if changed:
            for k in sorted(a for a,b in relations if b==i and a!=j):
                if (k,i) not in queued:queue.append((k,i));queued.add((k,i))
    fixedpoint_checks=0
    for (i,j),rows in sorted(relations.items()):
        for value,support in enumerate(rows):
            if (current[i]>>value)&1:
                need(bool(support&current[j]),'actual final support required');fixedpoint_checks+=1
    return dict(initial_domains=[mask_string(x) for x in initial],removals=trace,
                final_domains=[mask_string(x) for x in current],arc_queue_visits=visits,
                final_live_value_arc_checks=fixedpoint_checks,empty_domains=[i for i,x in enumerate(current) if not x])

def replay(initial, relations, result):
    current=initial[:]
    need(result['initial_domains']==[mask_string(x) for x in current],'initial domain binding')
    for row in result['removals']:
        i,v,j=row['domain'],row['value'],row['neighbor']
        need((i,j) in relations and 0<=v<len(relations[i,j]),'existing directed value')
        need((current[i]>>v)&1,'value still present')
        support=relations[i,j][v]
        need(int(row['support_mask'],16)==support,'exact support row')
        need(int(row['neighbor_current_mask'],16)==current[j],'exact neighbor state')
        need(int(row['intersection_mask'],16)==0 and not support&current[j],'no remaining support')
        current[i]&=~(1<<v)
    need(result['final_domains']==[mask_string(x) for x in current],'exact terminal domains')
    for (i,j),rows in relations.items():
        need(all(not ((current[i]>>v)&1) or bool(s&current[j]) for v,s in enumerate(rows)),'fixed point')
    return current

def tiny_controls():
    fixtures=[dict(name='satisfiable_equal',initial=[1,3],relations={(0,1):[1,2],(1,0):[1,2]}),
              dict(name='empty_equal',initial=[1,2],relations={(0,1):[1,2],(1,0):[1,2]}),
              dict(name='arc_consistent_unsat_triangle',initial=[3,3,3],relations={(i,j):[2,1] for i in range(3) for j in range(3) if i!=j})]
    results=[]
    for f in fixtures:
        result=arc_consistency(f['initial'],f['relations'],time.monotonic()+5);replay(f['initial'],f['relations'],result)
        solutions=[list(v) for v in product(range(2),repeat=len(f['initial']))
                   if all((f['initial'][i]>>value)&1 for i,value in enumerate(v))
                   and all((rows[v[i]]>>v[j])&1 for (i,j),rows in f['relations'].items())]
        if f['name']=='satisfiable_equal':need(solutions==[[0,0]] and result['final_domains']==[mask_string(1)]*2,'positive fixture')
        elif f['name']=='empty_equal':need(not solutions and result['empty_domains'],'empty contradiction')
        else:need(not solutions and not result['empty_domains'] and not result['removals'],'arc-consistency is not feasibility')
        results.append(dict(name=f['name'],initial=f['initial'],relations=[dict(source=i,target=j,supports=r) for (i,j),r in f['relations'].items()],
                            complete_solutions=solutions,result=result))
    f=fixtures[0];good=results[0]['result'];negative=[]
    for name,change in [('wrong_support',lambda x:x['removals'][0].update(support_mask=mask_string(0))),
                        ('wrong_neighbor_state',lambda x:x['removals'][0].update(neighbor_current_mask=mask_string(3))),
                        ('wrong_value',lambda x:x['removals'][0].update(value=0)),
                        ('missing_removal',lambda x:x['removals'].clear()),
                        ('duplicate_removal',lambda x:x['removals'].append(dict(x['removals'][0]))),
                        ('false_terminal_domain',lambda x:x['final_domains'].__setitem__(0,mask_string(0)))]:
        bad=json.loads(json.dumps(good));change(bad)
        try:replay(f['initial'],f['relations'],bad)
        except ValueError:negative.append(dict(name=name,rejected=True))
        else:raise AssertionError('corrupted trace accepted: '+name)
    return dict(tiny_CSPs=results,corrupted_traces=negative,independent_research_verification=False)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic();deadline=start+120
    need(digest(GATE)==GATE_HASH and read(GATE)['status']=='INDEPENDENT_SIX_PRISM_COARSE60_BITLIFT_CNF_PASS','independent model gate')
    need(digest(EXT)==EXT_HASH,'candidate explicit-unit metadata unchanged')
    inputs=dict(read(GATE)['inputs_sha256']);inputs[key(GATE)]=GATE_HASH;inputs[key(EXT)]=EXT_HASH
    for p in [Path(__file__),Path(__file__).with_name('theory_20260930_prism_coarse60_arc_spec.md'),BASE/'model.json',BASE/'scope.json',ROOT/'uv.lock',ROOT/'pyproject.toml']:inputs[key(p)]=digest(p)
    for p,h in inputs.items():need(digest(ROOT/p)==h,'frozen input '+p)
    manifest=dict(created_at=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv],working_directory=str(ROOT),inputs_sha256=inputs,
        versions=dict(python=platform.python_version(),uv=subprocess.check_output(['uv','--version'],text=True).strip()),
        limits=dict(seconds=120,solver_calls=0),scope='Pair-relation arc consistency for the exact18-domain CSP with column0bits fixed0.',
        pending_premise='Relabelling coverage of this explicit fixed-bit restriction is a separately reviewed candidate; this run claims no such coverage.')
    save(out/'manifest.json',manifest);save(out/'controls.json',tiny_controls())
    model=read(BASE/'model.json');ext=read(EXT);domains=model['domains'];relations={};pairchecks=0
    for r in model['Gram_relations']:
        i,j=r['left_domain'],r['right_domain'];left=[int(v,16) for v in domains[i]['global_bit1_masks_hex']];right=[int(v,16) for v in domains[j]['global_bit1_masks_hex']]
        rows=[];reverse=[0]*len(right)
        for a,x in enumerate(left):
            row=0
            for b,y in enumerate(right):
                if (x&y).bit_count()==r['target_bit11']:row|=1<<b;reverse[b]|=1<<a
                pairchecks+=1
            rows.append(row)
        need(rows==[int(v,16) for v in r['allowed_right_masks_hex']],'raw mask relation reconstruction')
        relations[i,j]=rows;relations[j,i]=reverse
    need(len(relations)==270 and pairchecks==2496960,'complete directed relation inventory')
    bitlookup={v['variable']:v for v in model['raw_bits']};initial=[(1<<136)-1]*18;fixed=[]
    for unit in ext['appended_unit_literals']:
        need(unit<0 and -unit in bitlookup,'negative rawbit unit');bit=bitlookup[-unit]
        need(bit['column']==0,'column0unit');di=3*bit['component']+bit['fibre'];domain=domains[di]
        position=domain['column_positions'].index(0);removed=[]
        for value,mask in enumerate(domain['local_masks']):
            if (mask>>position)&1:initial[di]&=~(1<<value);removed.append(dict(value=value,selector=domain['selectors'][value]))
        need(len(removed)==68,'half-domain bit conditioning')
        fixed.append(dict(domain=di,unit=unit,local_position=position,removed_values=removed))
    need(len(fixed)==6 and len({r['domain'] for r in fixed})==6,'six distinct conditioned domains')
    result=arc_consistency(initial,relations,deadline)
    for row in result['removals']:row['selector']=domains[row['domain']]['selectors'][row['value']]
    final=replay(initial,relations,result)
    result.update(schema='COARSE60_EXACT_ARC_REMOVAL_TRACE_V1',fixed_bit_removals=fixed,
        initial_sizes=[x.bit_count() for x in initial],final_sizes=[x.bit_count() for x in final],
        relation_model=key(BASE/'model.json'),relation_model_sha256=digest(BASE/'model.json'),
        propagation_scope='All135binaryGramrelations; noYcappropagation.',global_feasibility=None,
        global_feasibility_reason='A nonempty arc-consistent fixed point is not a joint assignment.')
    save(out/'trace.json',result)
    need(all(digest(ROOT/p)==h for p,h in inputs.items()),'stable inputs')
    summary=dict(status='CANDIDATE_COARSE60_ARC_EMPTY' if result['empty_domains'] else 'CANDIDATE_COARSE60_ARC_NONEMPTY_FIXEDPOINT',
        created_at=manifest['created_at'],completed_at=datetime.now(timezone.utc).isoformat(),source_commit=manifest['source_commit'],
        inputs_sha256=inputs,outputs_sha256={key(p):digest(p) for p in out.iterdir() if p.is_file()},
        local_domains=18,choices_before_conditioning=2448,fixed_bit_removed_values=408,
        choices_after_conditioning=sum(x.bit_count() for x in initial),AC_removed_values=len(result['removals']),
        final_choices=sum(x.bit_count() for x in final),final_domain_sizes=result['final_sizes'],empty_domains=result['empty_domains'],
        complete_binary_relations=135,directed_arcs=270,raw_selector_pairs_reconstructed=pairchecks,
        arc_queue_visits=result['arc_queue_visits'],final_live_value_arc_checks=result['final_live_value_arc_checks'],
        solver_calls=0,independent_approval=False,scope=manifest['scope'],target_resolution='UNKNOWN',
        limitations=['The chosen coarse template is restricted.','No Y-cap propagation in this scout.',
                     'No global feasibility from a nonempty fixed point.','No new or changed CNF.'],wall_seconds=time.monotonic()-start)
    save(out/'summary.json',summary);print(json.dumps(dict(status=summary['status'],removed=summary['AC_removed_values'],sizes=summary['final_domain_sizes'],
        summary_sha256=digest(out/'summary.json'),trace_sha256=digest(out/'trace.json'),wall_seconds=time.monotonic()-start)))

if __name__=='__main__':main()
