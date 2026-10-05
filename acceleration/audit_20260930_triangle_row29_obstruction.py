"""Independent raw-graph constraint reconstruction and full binary-tree check.

No producer, SAT solver, or SAT core imports. Each forced bit is checked by
setting its opposite and deriving an impossible interval for the cited row.
"""
from __future__ import annotations
import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_triangle_wave154_row29_obstruction/'
RAW='acceleration/results/20260930_triangle_partial99/wave154.json'
GATE='acceleration/results/20260930_independent_review/triangle_q1_partial99/summary.json'
PINS={B+'summary.json':'a0814f7972a8592d454f7c4c9f5fabaf78bf3bc91ffc59e9509102c0b403205f',
      RAW:'e8581587313cf8207799dcf781d8469eb66a699687e023faf0a435000ab9f69b',
      GATE:'bad7ddc51101377b8eaa284c650db8adcee5c261a0717073b90fc9e2347d7594'}
def require(ok,msg):
    if not ok:raise ValueError(msg)
def h(p):return sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads((ROOT/p).read_bytes())
def save(p,data):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(data,f,indent=2);f.write('\n')
def canonical_sha(obj):return sha256(json.dumps(obj,separators=(',',':')).encode()).hexdigest()

def reconstruct(a,u,comparison,k=14,lam=1,mu=2):
    n=len(a)
    require(all(len(row)==n for row in a),'square partial graph')
    require(all(type(x)is int and x in (-1,0,1)for row in a for x in row),'partial ternary entries')
    require(all(a[i][i]==0 for i in range(n)),'zero diagonal')
    require(all(a[i][j]==a[j][i]for i in range(n)for j in range(n)),'partial symmetry')
    require(0<=u<n and mu>=lam,'valid chosen row and cap order')
    known=[{j for j,x in enumerate(row)if x==1}for row in a]
    unknown=[j for j,x in enumerate(a[u])if x==-1]
    lookup={x:i for i,x in enumerate(unknown)}
    degree=k-len(known[u])
    constraints=[dict(kind='degree',vertex=u,variables=list(range(len(unknown))),lower=degree,upper=degree)]
    for v in comparison:
        require(v!=u and all(x!=-1 for x in a[v])and a[u][v]in (0,1),'comparison row wholly fixed')
        constant=sorted(known[u]&known[v])
        quota=(lam if v in known[u]else mu)-len(constant)
        indices=[lookup[w]for w in unknown if w in known[v]]
        constraints.append(dict(kind='exact_common',pair=[u,v],known_common=constant,variables=indices,lower=quota,upper=quota))
    for b,c in combinations(unknown,2):
        common=sorted((known[b]&known[c])-{u})
        # An unknown b--c edge can only tighten mu to lambda, never loosen mu.
        cap=lam if c in known[b]else mu
        require(len(common)<=cap,'already inconsistent pair in partial graph')
        if len(common)==cap:
            constraints.append(dict(kind='incompatible_pair',pair=[b,c],known_edge=a[b][c],known_common=common,
                                    variables=[lookup[b],lookup[c]],lower=0,upper=1))
    return unknown,constraints

def validate_constraints(n,constraints):
    for c in constraints:
        require(type(c['lower'])is int and type(c['upper'])is int and c['lower']<=c['upper'],'integer interval')
        require(all(type(x)is int and 0<=x<n for x in c['variables']),'constraint variable domain')
        require(len(c['variables'])==len(set(c['variables'])),'distinct variables in constraint')

def feasible(bits,constraints):
    return all(c['lower']<=sum(bits[i]for i in c['variables'])<=c['upper']for c in constraints)

def check_tree(n,constraints,tree,record=False):
    validate_constraints(n,constraints)
    nodes=tree['nodes'];require(isinstance(nodes,list)and nodes,'nonempty node list')
    require([r['id']for r in nodes]==list(range(len(nodes))),'unique sequential node IDs')
    root=tree['root'];require(type(root)is int and 0<=root<len(nodes),'root index')
    seen=set();receipts=[];split_count=0;conflict_count=0;sat_count=0;forces=0;forced_bits=0;max_depth=0
    leaf_constraints=Counter();sat_assignments=[]
    def interval(c,assigned):
        one=sum(assigned.get(x)==1 for x in c['variables']);free=[x for x in c['variables']if x not in assigned]
        return one,free
    def visit(idx,assigned,depth):
        nonlocal split_count,conflict_count,sat_count,forces,forced_bits,max_depth
        require(type(idx)is int and 0<=idx<len(nodes)and idx not in seen,'acyclic unique-parent complete tree')
        seen.add(idx);node=nodes[idx];max_depth=max(max_depth,depth);before=dict(assigned)
        for step in node['forces']:
            ci=step['constraint'];require(type(ci)is int and 0<=ci<len(constraints),'force constraint index')
            c=constraints[ci];one,free=interval(c,assigned)
            require(step['ones_before']==one and step['free_before']==free and free,'force exact prestate')
            value=step['value'];require(type(value)is int and value in (0,1),'forced binary value')
            require(one<=c['upper']and one+len(free)>=c['lower'],'force starts in consistent interval')
            # Independent local entailment: contradict EACH opposite value while
            # all other free bits still range over {0,1}. No producer propagation
            # rule or search order is imported or trusted.
            for x in free:
                opposite=dict(assigned);opposite[x]=1-value
                alt_one,alt_free=interval(c,opposite)
                require(alt_one>c['upper']or alt_one+len(alt_free)<c['lower'],'opposite value not ruled out')
                forced_bits+=1
            for x in free:assigned[x]=value
            forces+=1
        status=node['status']
        if status=='CONFLICT':
            ci=node['constraint'];require(type(ci)is int and 0<=ci<len(constraints),'leaf constraint index')
            c=constraints[ci];one,free=interval(c,assigned)
            require(node['ones']==one and node['free']==len(free),'leaf exact counters')
            require(one>c['upper']or one+len(free)<c['lower'],'leaf contradiction')
            require('children'not in node,'conflict has no hidden children')
            conflict_count+=1;leaf_constraints[str(ci)]+=1
        elif status=='SPLIT':
            x=node['variable'];require(type(x)is int and 0<=x<n and x not in assigned,'split new variable')
            children=node['children'];require(len(children)==2 and sorted(c['value']for c in children)==[0,1],'both binary branches exactly once')
            require(all(type(c['value'])is int for c in children),'strict branch bits')
            split_count+=1
            for child in children:
                child_state=dict(assigned);child_state[x]=child['value'];visit(child['node'],child_state,depth+1)
        elif status=='SAT':
            require(len(assigned)==n,'SAT leaf complete assignment')
            assignment=[assigned[i]for i in range(n)]
            require(node['assignment']==assignment and feasible(assignment,constraints),'SAT leaf directly valid')
            require('children'not in node,'SAT no hidden children')
            sat_assignments.append(assignment);sat_count+=1
        else:raise ValueError('unrecognized node status')
        if record:receipts.append(dict(id=idx,status=status,depth=depth,inherited_assignment=sorted(before.items()),
                                        after_forces_assignment=sorted(assigned.items()),forced_batches=len(node['forces'])))
    visit(root,{},0)
    require(seen==set(range(len(nodes))),'no unused or omitted nodes')
    if sat_count:
        require(tree['status']=='SAT'and tree['assignment']in sat_assignments,'tree SAT status binding')
    else:require(tree['status']=='UNSAT'and tree['assignment']is None,'tree UNSAT status binding')
    return dict(nodes=len(nodes),splits=split_count,conflict_leaves=conflict_count,sat_leaves=sat_count,
                forced_batches=forces,individually_checked_forced_bits=forced_bits,max_split_depth=max_depth,
                leaf_constraint_histogram=dict(leaf_constraints),receipts=sorted(receipts,key=lambda r:r['id']))

def calibration():
    constraints=[dict(variables=[0,1],lower=1,upper=1),dict(variables=[1,2],lower=1,upper=1),dict(variables=[0,2],lower=1,upper=1)]
    tiny=dict(status='UNSAT',assignment=None,root=0,nodes=[
        dict(id=0,forces=[],status='SPLIT',variable=0,children=[dict(value=0,node=1),dict(value=1,node=2)]),
        dict(id=1,forces=[dict(constraint=0,ones_before=0,free_before=[1],value=1),dict(constraint=1,ones_before=1,free_before=[2],value=0)],status='CONFLICT',constraint=2,ones=0,free=0),
        dict(id=2,forces=[dict(constraint=0,ones_before=1,free_before=[1],value=0),dict(constraint=1,ones_before=0,free_before=[2],value=1)],status='CONFLICT',constraint=2,ones=2,free=0)])
    require(not any(feasible(bits,constraints)for bits in product((0,1),repeat=3)),'independent eight-assignment UNSAT oracle')
    positive=check_tree(3,constraints,tiny)
    sat=dict(status='SAT',assignment=[0,1],root=0,nodes=[
        dict(id=0,forces=[],status='SPLIT',variable=0,children=[dict(value=0,node=1),dict(value=1,node=2)]),
        dict(id=1,forces=[dict(constraint=0,ones_before=0,free_before=[1],value=1)],status='SAT',assignment=[0,1]),
        dict(id=2,forces=[dict(constraint=0,ones_before=1,free_before=[1],value=0)],status='SAT',assignment=[1,0])])
    satisfiable=check_tree(2,constraints[:1],sat)
    require(satisfiable['sat_leaves']==2,'positive SAT cases do not become UNSAT')
    a=[[int(x!=y and(x//3==y//3 or x%3==y%3))for y in range(9)]for x in range(9)]
    require(all(sum(row)==4 for row in a),'rook degree')
    require(all(sum(a[x][w]*a[y][w]for w in range(9))==2-a[x][y]for x,y in combinations(range(9),2)),'rook exact pair identities')
    masked=deepcopy(a)
    for x in [1,2,3,6]:masked[0][x]=masked[x][0]=-1
    unknown,necessary=reconstruct(masked,0,[4,5,7,8],k=4)
    require(unknown==[1,2,3,6]and feasible([a[0][x]for x in unknown],necessary),'known-valid graph satisfies extracted necessary constraints')
    bad=deepcopy(tiny);bad['status']='SAT';bad['assignment']=[0,0,0]
    try:check_tree(3,constraints,bad)
    except ValueError:pass
    else:raise ValueError('false SAT oracle accepted')
    return dict(known_unsat_eight_assignment_oracle=True,known_unsat_tree=positive,known_sat_tree=satisfiable,
                rook9_exact_SRG_positive=True,rook9_masked_row_necessary_constraints_preserve_valid_row=True,
                false_sat_status_rejected=True,trust='Independent literal truth-table and raw graph controls; no producer code imports.'),tiny

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);args=parser.parse_args()
    out=ROOT/args.out;out.mkdir(parents=True,exist_ok=False);start=time.monotonic();inputs={}
    def bind(path,expected=None):
        got=h(ROOT/path);require(expected is None or got==expected,'input hash '+path);inputs[path]=got
    for path,expected in PINS.items():bind(path,expected)
    producer=load(B+'summary.json')
    for path,expected in producer['output_hashes'].items():bind(path,expected)
    for path,expected in load(B+'manifest.json')['input_hashes'].items():bind(path,expected)
    gate=load(GATE);require(gate['status']=='INDEPENDENT_TRIANGLE_Q1_PARTIAL99_PROPAGATION_PASS','exact propagation gate')
    require(gate['inputs_sha256'][RAW]==PINS[RAW],'propagation input binding')
    raw=load(RAW);a=raw['final_adjacency'];record=load(B+'constraints.json');tree=load(B+'proof_tree.json')
    save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
         command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),inputs_sha256=dict(inputs),
         question='Do independently necessary row29 constraints have a complete exact unsatisfiability tree?',
         success='Reconstruct every constraint from raw partial99, check every counterfactual force, both branches and all contradiction leaves.',
         numerical_thresholds=None,numerical_thresholds_null_reason='Only exact integers and exhaustive certificate checking.',limits=dict(seconds=120)))
    controls,tiny=calibration();save(out/'controls.json',controls);save(out/'tiny_unsat_tree.json',tiny)
    unknown,constraints=reconstruct(a,29,list(range(3,27)))
    require(record['vertex']==29 and record['variables']==unknown and record['constraints']==constraints,'literal full reconstructed constraint equality')
    require(record['raw_matrix_path']==RAW and record['raw_matrix_sha256']==PINS[RAW],'raw matrix reference')
    require(len(unknown)==38 and all(v>=39 for v in unknown),'row38 unknown B edges')
    require(constraints[0]['lower']==constraints[0]['upper']==10,'row degree ten')
    kinds=Counter(c['kind']for c in constraints);require(kinds=={'degree':1,'exact_common':24,'incompatible_pair':53},'constraint populations')
    save(out/'reconstructed_constraints.json',dict(vertex=29,variables=unknown,constraints=constraints,raw_matrix_sha256=PINS[RAW],
                                                final_matrix_compact_json_sha256=canonical_sha(a)))
    checked=check_tree(38,constraints,tree,record=True)
    require((checked['nodes'],checked['splits'],checked['conflict_leaves'],checked['sat_leaves'])==(139,69,70,0),'exact tree population')
    save(out/'complete_node_check.json',checked)
    require(producer['result']=='UNSAT'and producer['tree_nodes']==139 and producer['splits']==69 and producer['conflict_leaves']==70,'producer tree claims')
    mutations={};firstforce=next(i for i,n in enumerate(tree['nodes'])if n['forces']);firstleaf=next(i for i,n in enumerate(tree['nodes'])if n['status']=='CONFLICT')
    bad=deepcopy(tree);bad['nodes'][0]['children'].pop();mutations['missing_branch']=bad
    bad=deepcopy(tree);bad['nodes'][0]['children'][1]['value']=0;mutations['duplicated_branch_value']=bad
    bad=deepcopy(tree);bad['nodes'][0]['children'][1]['node']=bad['nodes'][0]['children'][0]['node'];mutations['shared_child']=bad
    bad=deepcopy(tree);bad['nodes'][0]['children'][0]['node']=0;mutations['cycle']=bad
    bad=deepcopy(tree);extra=deepcopy(bad['nodes'][-1]);extra['id']=len(bad['nodes']);bad['nodes'].append(extra);mutations['unused_node']=bad
    bad=deepcopy(tree);bad['nodes'][firstforce]['forces'][0]['value']^=1;mutations['opposite_force']=bad
    bad=deepcopy(tree);bad['nodes'][firstforce]['forces'][0]['ones_before']+=1;mutations['false_force_count']=bad
    bad=deepcopy(tree);bad['nodes'][firstforce]['forces'][0]['free_before'].pop();mutations['omitted_forced_variable']=bad
    bad=deepcopy(tree);bad['nodes'][firstleaf]['ones']+=1;mutations['false_leaf_count']=bad
    bad=deepcopy(tree);bad['nodes'][firstleaf]['constraint']=0;mutations['wrong_leaf_witness']=bad
    bad=deepcopy(tree);bad['nodes'][firstleaf]['status']='SAT';bad['nodes'][firstleaf]['assignment']=[0]*38;mutations['false_sat_leaf']=bad
    bad=deepcopy(tree);bad['assignment']=[0]*38;mutations['UNSAT_with_assignment']=bad
    rejected=[]
    for name,bad in mutations.items():
        try:check_tree(38,constraints,bad)
        except (ValueError,KeyError):rejected.append(name)
        else:raise ValueError('accepted corrupted raw tree '+name)
    save(out/'actual_tree_corruptions.json',dict(rejected=rejected))
    # Constraint corruption controls compare against the independently derived graph equations.
    mutations={}
    bad=deepcopy(record);bad['variables'][0]=40;mutations['wrong_variable_vertex']=bad
    bad=deepcopy(record);bad['constraints'][0]['lower']=bad['constraints'][0]['upper']=9;mutations['wrong_degree']=bad
    bad=deepcopy(record);bad['constraints'][1]['upper']+=1;mutations['loosened_equality']=bad
    bad=deepcopy(record);bad['constraints'][-1]['known_common']=[];mutations['unsupported_pair_witness']=bad
    bad=deepcopy(record);bad['constraints'].pop();mutations['missing_pair']=bad
    require(all(bad['variables']!=unknown or bad['constraints']!=constraints for bad in mutations.values()),'constraint mutations reject')
    save(out/'actual_constraint_corruptions.json',dict(rejected=list(mutations)))
    for path,expected in list(inputs.items()):bind(path,expected)
    for path in [Path(__file__).relative_to(ROOT).as_posix(),'docs/AUDIT_20260930_TRIANGLE_ROW29_OBSTRUCTION.md']:bind(path)
    result=dict(status='INDEPENDENT_FIXED_WAVE154_ROW29_EMPTY_DOMAIN_PASS',timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),
        python=platform.python_version(),verifier='/root/state_literature_audit independent raw constraint and certificate checking agent',
        claim_id='C-FIXED-WAVE154-ROW29-EMPTY-DOMAIN',claim_revision=1,recommendation='VERIFIED',kind='exclusion',basis=['DERIVED','COMPUTED'],
        statement='For the exact propagated Wave154 partial99graph, no Boolean assignment to its38 unknown row29 edges satisfies the required degree10, the24 exact common-neighbor equations against vertices3 through26, and the53 pair incompatibilities forced by already known common neighbors. Consequently no row29 of a target completion of the exact initial Wave154 family is possible.',
        scope='Only row29 of the exact fixed labelled Wave154/Q1 partial graph; the claim is a necessary-row obstruction, not an equivalence of this row relaxation with full graph completion.',
        assumptions=['The frozen initial Wave154 partial graph is the fixed configuration under consideration.','No nontrivial target automorphism or universal containment of this configuration is assumed.'],
        dependencies=[dict(id='C-TRIANGLE-FIXED-Q1-PARTIAL99-PROPAGATION',revision=1,relation='uses_result')],
        inputs_sha256=inputs,raw_matrix_sha256=PINS[RAW],final_matrix_compact_json_sha256=canonical_sha(a),
        constraints=dict(unknown_row_bits=38,degree_equations=1,degree_quota=10,exact_common_equations=24,pair_incompatibilities=53),
        tree={k:v for k,v in checked.items()if k!='receipts'},controls=controls,
        complete_verification='Every reconstructed input constraint, every forced bit by counterfactual contradiction, both children of every split, every leaf witness and every reachable node; no sampling.',
        producer_imports=False,SAT_solver_calls=0,SAT_core_used_as_premise=False,
        artifact_availability='LOCAL_ONLY',artifact_availability_reason='All raw matrices, tree, audit receipts and sources are local; parent controls publication.',
        target_resolution=False,external_review=False,elapsed_seconds=time.monotonic()-start,
        limitations=['Fixed Wave154 family only; no unrestricted Conway-99 nonexistence or complete triangle-core coverage.',
                     'Necessary projected row constraints are weaker than full target feasibility; infeasibility suffices here, but a feasible row would not be a target graph.',
                     'The mathematical use of the initial configuration relies on the pinned independently checked propagation dependency.',
                     'The extracted SAT core and the separate DRAT exclusion are not premises of this derivation.'])
    result['audit_artifact_hashes']={p.relative_to(ROOT).as_posix():h(p)for p in sorted(out.iterdir())if p.is_file()}
    save(out/'summary.json',result);print(json.dumps({'status':result['status'],'summary_sha256':h(out/'summary.json'),'tree':result['tree']}))

if __name__=='__main__':main()
