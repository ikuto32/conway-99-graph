"""Candidate exact independent-degree-block Gram bounds; not a verifier."""
import argparse
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations,product
import json
from pathlib import Path
import platform
import random
import subprocess
import sys
import time

from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]


def need(condition,message):
    if not condition: raise ValueError(message)


def digest(path):
    value = sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''): value.update(block)
    return value.hexdigest()


def key(path): return Path(path).resolve().relative_to(ROOT).as_posix()


def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8') as stream:
        json.dump(value,stream,indent=2)
        stream.write('\n')


def check_time(deadline):
    if deadline is not None and time.monotonic() >= deadline: raise TimeoutError('declared overall60second resource cap')


def internal_optimum(vertices,edges,weights,fixed):
    """Perfect matching optimum, including forced0/1edge values."""
    position = {v:i for i,v in enumerate(vertices)}
    pair_to_var = {tuple(sorted((position[u],position[v]))):var for var,u,v in edges}
    forced = [var for var,u,v in edges if fixed.get(var) == 1]
    mask = (1 << len(vertices))-1
    used = set()
    for var,u,v in edges:
        if var in forced:
            if u in used or v in used: return None
            used.update((u,v));mask &= ~(1 << position[u]);mask &= ~(1 << position[v])
    values,choices = {0:0},{}
    def recurse(current):
        if current in values:return values[current]
        u = (current & -current).bit_length()-1
        remaining = current & ~(1 << u)
        best,best_var,best_child = None,None,None
        for v in range(u+1,len(vertices)):
            if not(remaining >> v & 1):continue
            variable = pair_to_var[u,v]
            if fixed.get(variable) == 0:continue
            child = remaining & ~(1 << v)
            value = recurse(child)
            if value is not None and (best is None or weights[variable]+value > best):
                best,best_var,best_child = weights[variable]+value,variable,child
        values[current] = best
        choices[current] = (best_var,best_child)
        return best
    optimum = recurse(mask)
    if optimum is None:return None
    selected,current = list(forced),mask
    while current:
        variable,current = choices[current]
        selected.append(variable)
    result = dict(kind='internal_matching',vertices=vertices,forced_one_edges=forced,remaining_mask=mask,
                  selected_edges=sorted(selected),objective=sum(weights[v] for v in selected),
                  residual_objective=optimum,dp_values={str(k):v for k,v in sorted(values.items())})
    need(result['objective'] == optimum+sum(weights[v] for v in forced),'internal objective equality')
    return result


def verify_internal(result,vertices,edges,weights,fixed):
    need(result is not None,'missing internal witness')
    selected = result['selected_edges']
    edge_map = {var:(u,v) for var,u,v in edges}
    need(len(selected) == len(set(selected)) and all(v in edge_map for v in selected),'internal primal edge IDs')
    degrees = Counter(x for var in selected for x in edge_map[var])
    need(all(degrees[v] == 1 for v in vertices),'internal primal degrees')
    need(all(int(var in selected) == value for var,value in fixed.items() if var in edge_map),'internal fixed values')
    need(result['objective'] == sum(weights[v] for v in selected),'internal primal objective')
    position = {v:i for i,v in enumerate(vertices)}
    pair_map = {tuple(sorted((position[u],position[v]))):var for var,u,v in edges}
    table = {int(mask):value for mask,value in result['dp_values'].items()}
    need(table.get(0) == 0,'DP empty state')
    for mask,value in table.items():
        if mask == 0:continue
        u = (mask & -mask).bit_length()-1
        candidates = []
        for v in range(u+1,len(vertices)):
            if mask >> v & 1:
                variable = pair_map[u,v]
                if fixed.get(variable) == 0:continue
                child = mask & ~(1 << u) & ~(1 << v)
                need(child in table,'complete recurrence child')
                if table[child] is not None:candidates.append(weights[variable]+table[child])
        need(value == (max(candidates) if candidates else None),'internal exact recurrence')
    forced = [var for var,u,v in edges if fixed.get(var) == 1]
    covered = {x for var in forced for x in edge_map[var]}
    mask = sum(1 << position[v] for v in vertices if v not in covered)
    need(result['remaining_mask'] == mask and result['forced_one_edges'] == forced,'internal forced mask')
    need(table[mask]+sum(weights[v] for v in forced) == result['objective'],'internal optimum certificate')


def bipartite_optimum(left,right,edges,degree,weights,fixed):
    li,ri = {v:i for i,v in enumerate(left)},{v:i for i,v in enumerate(right)}
    left_need,right_need = [degree]*len(left),[degree]*len(right)
    forced = []
    for variable,u,v in edges:
        if fixed.get(variable) == 1:
            forced.append(variable);left_need[li[u]] -= 1;right_need[ri[v]] -= 1
    if min(left_need+right_need) < 0:return None
    nleft,nright = len(left),len(right)
    source,sink = nleft+nright,nleft+nright+1
    n = sink+1
    arcs = []
    def add(u,v,capacity,cost):
        index = len(arcs)
        arcs.append([u,v,capacity,cost,index+1])
        arcs.append([v,u,0,-cost,index])
        return index
    for i,capacity in enumerate(left_need):add(source,i,capacity,0)
    for j,capacity in enumerate(right_need):add(nleft+j,sink,capacity,0)
    edge_arcs = {}
    allowed = []
    for variable,u,v in edges:
        if variable in fixed:continue
        edge_arcs[variable] = add(li[u],nleft+ri[v],1,-weights[variable])
        allowed.append((variable,u,v))
    required = sum(left_need)
    need(required == sum(right_need),'balanced residual quotas')
    sent,augmentations = 0,0
    while sent < required:
        distance,parent = [None]*n,[None]*n
        distance[source] = 0
        for iteration in range(n-1):
            changed = False
            for index,(u,v,capacity,cost,reverse) in enumerate(arcs):
                if capacity and distance[u] is not None and (distance[v] is None or distance[v] > distance[u]+cost):
                    distance[v],parent[v] = distance[u]+cost,index;changed = True
            if not changed:break
        if distance[sink] is None:return None
        path,current = [],sink
        while current != source:
            index = parent[current]
            need(index is not None and index not in path,'shortest path predecessor cycle')
            path.append(index);current = arcs[index][0]
        amount = min(arcs[index][2] for index in path)
        for index in path:
            arcs[index][2] -= amount;arcs[arcs[index][4]][2] += amount
        sent += amount;augmentations += 1
    selected = forced+[variable for variable,index in edge_arcs.items() if arcs[index][2] == 0]
    # Residual row/column arc shortest potentials from an artificial source
    # connected to every node with cost0 give a directly checkable dual.
    residual = []
    for variable,u,v in allowed:
        if variable in selected:residual.append((nleft+ri[v],li[u],weights[variable]))
        else:residual.append((li[u],nleft+ri[v],-weights[variable]))
    potential = [0]*(nleft+nright)
    for iteration in range(nleft+nright):
        changed = False
        for u,v,cost in residual:
            if potential[v] > potential[u]+cost:
                potential[v] = potential[u]+cost;changed = True
        if not changed:break
    need(not changed,'negative residual cycle contradicts optimum')
    alpha_left,alpha_right = potential[:nleft],[-value for value in potential[nleft:]]
    beta = {variable:max(0,weights[variable]-alpha_left[li[u]]-alpha_right[ri[v]]) for variable,u,v in allowed}
    dual = sum(a*b for a,b in zip(alpha_left,left_need))+sum(a*b for a,b in zip(alpha_right,right_need))+sum(beta.values())
    forced_weight = sum(weights[v] for v in forced)
    result = dict(kind='bipartite_factor',left=left,right=right,degree=degree,left_residual_degrees=left_need,right_residual_degrees=right_need,
                  forced_one_edges=forced,selected_edges=sorted(selected),objective=sum(weights[v] for v in selected),
                  residual_objective=dual,alpha_left=alpha_left,alpha_right=alpha_right,
                  capacity_dual={str(v):b for v,b in sorted(beta.items())},augmentations=augmentations)
    need(result['objective'] == forced_weight+dual,'exact bipartite primal/dual equality')
    return result


def verify_bipartite(result,left,right,edges,degree,weights,fixed):
    need(result is not None,'missing bipartite certificate')
    edge_map = {variable:(u,v) for variable,u,v in edges}
    selected = result['selected_edges']
    need(len(selected) == len(set(selected)) and all(v in edge_map for v in selected),'bipartite primal edge IDs')
    need(all(int(var in selected) == value for var,value in fixed.items() if var in edge_map),'bipartite fixed values')
    counts = Counter(x for var in selected for x in edge_map[var])
    need(all(counts[v] == degree for v in left+right),'bipartite primal degrees')
    li,ri = {v:i for i,v in enumerate(left)},{v:i for i,v in enumerate(right)}
    forced = [variable for variable,u,v in edges if fixed.get(variable) == 1]
    left_need = [degree-sum(u == v for variable in forced for u in edge_map[variable]) for v in left]
    right_need = [degree-sum(u == v for variable in forced for u in edge_map[variable]) for v in right]
    need(result['left_residual_degrees'] == left_need and result['right_residual_degrees'] == right_need,'residual dual quotas')
    al,ar = result['alpha_left'],result['alpha_right']
    need(len(al) == len(left) and len(ar) == len(right) and all(type(x) is int for x in al+ar),'integer dual potentials')
    beta = {int(k):v for k,v in result['capacity_dual'].items()}
    allowed = [(variable,u,v) for variable,u,v in edges if variable not in fixed]
    need(set(beta) == {variable for variable,u,v in allowed},'capacity dual coverage')
    need(all(type(beta[var]) is int and beta[var] >= 0 and al[li[u]]+ar[ri[v]]+beta[var] >= weights[var] for var,u,v in allowed),'dual feasibility')
    dual = sum(a*b for a,b in zip(al,left_need))+sum(a*b for a,b in zip(ar,right_need))+sum(beta.values())+sum(weights[v] for v in forced)
    primal = sum(weights[v] for v in selected)
    need(result['objective'] == primal == dual,'primal/dual strong equality')


def controls():
    rng = random.Random(20260930)
    cases,corruptions = [],[]
    for n in (4,6):
        vertices = list(range(n))
        edges = [(i+1,u,v) for i,(u,v) in enumerate(combinations(vertices,2))]
        weights = {var:rng.randrange(-9,10) for var,u,v in edges}
        def enumerate_matchings(remaining):
            if not remaining:yield [];return
            u,*tail = remaining
            for v in tail:
                variable = next(var for var,a,b in edges if (a,b) == (u,v))
                for rest in enumerate_matchings([x for x in tail if x != v]):yield [variable]+rest
        matchings = list(enumerate_matchings(vertices))
        for fixed in ({},{matchings[0][0]:1},{matchings[0][0]:0}):
            exact = max(sum(weights[v] for v in m) for m in matchings if all(int(v in m) == a for v,a in fixed.items()))
            result = internal_optimum(vertices,edges,weights,fixed)
            verify_internal(result,vertices,edges,weights,fixed)
            need(result['objective'] == exact,'exhaustive internal calibration')
            cases.append(dict(kind='internal',n=n,fixed=fixed,exact=exact))
        bad = json.loads(json.dumps(result));bad['dp_values'][str(result['remaining_mask'])] += 1
        try:verify_internal(bad,vertices,edges,weights,fixed)
        except ValueError:corruptions.append('internal_wrong_dp_'+str(n))
        else:raise ValueError('corrupt DP accepted')
    for n,degree in ((2,1),(2,2),(3,1),(3,2)):
        left,right = list(range(n)),list(range(n,2*n))
        edges = [(i+1,u,v) for i,(u,v) in enumerate(product(left,right))]
        weights = {var:rng.randrange(-9,10) for var,u,v in edges}
        feasible = []
        for bits in product((0,1),repeat=len(edges)):
            selected = [var for bit,(var,u,v) in zip(bits,edges) if bit]
            counts = Counter(x for bit,(var,u,v) in zip(bits,edges) if bit for x in (u,v))
            if all(counts[v] == degree for v in left+right):feasible.append(selected)
        for fixed in ({},{feasible[0][0]:1}):
            exact = max(sum(weights[v] for v in m) for m in feasible if all(int(v in m) == a for v,a in fixed.items()))
            result = bipartite_optimum(left,right,edges,degree,weights,fixed)
            verify_bipartite(result,left,right,edges,degree,weights,fixed)
            need(result['objective'] == exact,'exhaustive bipartite calibration')
            cases.append(dict(kind='bipartite',n=n,degree=degree,fixed=fixed,exact=exact))
        for mutation in ('primal','dual'):
            bad = json.loads(json.dumps(result))
            if mutation == 'primal':bad['selected_edges'].pop()
            else:bad['alpha_left'][0] -= 1
            try:verify_bipartite(bad,left,right,edges,degree,weights,fixed)
            except ValueError:corruptions.append('bipartite_wrong_'+mutation+'_'+str(n)+'_'+str(degree))
            else:raise ValueError('corrupt flow certificate accepted')
    vertices = [0,1,2,3];edges = [(i+1,u,v) for i,(u,v) in enumerate(combinations(vertices,2))]
    need(internal_optimum(vertices,edges,{var:1 for var,u,v in edges},{1:1,2:1}) is None,'infeasible internal forced degrees')
    left,right = [0,1],[2,3];edges = [(i+1,u,v) for i,(u,v) in enumerate(product(left,right))]
    need(bipartite_optimum(left,right,edges,1,{var:1 for var,u,v in edges},{1:1,2:1}) is None,'infeasible bipartite forced degrees')
    return dict(status='PRODUCER_CONTROLS_PASSED_NOT_INDEPENDENT_VERIFICATION',seed=20260930,exhaustive_small_cases=cases,
                corruptions_rejected=corruptions,infeasible_forced_degree_controls_rejected=2)


def make_blocks(model):
    edges = [(row['id'],row['u'],row['v']) for row in model['edge_variables']]
    need(len(edges) == 780 and {(u,v) for var,u,v in edges} == set(combinations(range(10,50),2)),'exact780pair universe')
    need({var for var,u,v in edges} == set(range(1,781)),'exact variable labels')
    blocks,degree_rows = [],[]
    for cell in range(1,5):
        vertices = list(range(10*cell,10*cell+10))
        selected = [e for e in edges if e[1] in vertices and e[2] in vertices]
        blocks.append(dict(name=f'internal_{cell}',kind='internal',vertices=vertices,edges=selected))
        for v in vertices:degree_rows.append((tuple(sorted(var for var,u,w in selected if v in (u,w))),1))
    coordinates = model['cell_rook_coordinates']
    for left_cell,right_cell in combinations(range(1,5),2):
        left,right = list(range(left_cell*10,left_cell*10+10)),list(range(right_cell*10,right_cell*10+10))
        degree = 1 if any(coordinates[left_cell][i] == coordinates[right_cell][i] for i in (0,1)) else 2
        selected = [e for e in edges if e[1] in left and e[2] in right]
        blocks.append(dict(name=f'cross_{left_cell}_{right_cell}',kind='bipartite',left=left,right=right,degree=degree,edges=selected))
        for v in left+right:degree_rows.append((tuple(sorted(var for var,u,w in selected if v in (u,w))),degree))
    actual = Counter((tuple(sorted(row['variables'])),row['value']) for row in model['degree_constraints'])
    need(Counter(degree_rows) == actual and len(degree_rows) == 160,'all exact saved degree constraints')
    need(Counter(var for b in blocks for var,u,v in b['edges']) == Counter(range(1,781)),'disjoint complete degree blocks')
    return edges,blocks


def bound(polynomial,blocks,fixed,deadline):
    weights = {int(var):value for var,value in polynomial['coefficients'].items()}
    results = []
    for block in blocks:
        check_time(deadline)
        if block['kind'] == 'internal':
            result = internal_optimum(block['vertices'],block['edges'],weights,fixed)
            need(result is not None,'unexpected infeasible known-valid fixed internal pattern')
            verify_internal(result,block['vertices'],block['edges'],weights,fixed)
        else:
            result = bipartite_optimum(block['left'],block['right'],block['edges'],block['degree'],weights,fixed)
            need(result is not None,'unexpected infeasible known-valid fixed bipartite pattern')
            verify_bipartite(result,block['left'],block['right'],block['edges'],block['degree'],weights,fixed)
        results.append(dict(block=block['name'],**result))
    total = polynomial['constant']+sum(row['objective'] for row in results)
    return dict(status='CANDIDATE',fixed_values={str(var):value for var,value in sorted(fixed.items())},
                exact_degree_relaxation_maximum=total,strictly_negative=total < 0,blocks=results,
                scope='Exact maximum over the independent degree-block relaxation; an upper bound for the more constrained local window',independent_verification_pending=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=False)
    model_path = ROOT/'acceleration/results/20260930_rook_free_internal_sat/model.json'
    checkpoint_path = ROOT/'acceleration/results/20260930_rook_box_batch01/accepted_checkpoint.json'
    gate_path = ROOT/'acceleration/results/20260930_rook_free_internal_sat/independent_cnf_encoding.json'
    bindings = {}
    def read(path,expected=None):
        observed = digest(path)
        need(expected is None or observed == expected,'input hash mismatch: '+str(path))
        bindings[key(path)] = observed
        return json.loads(Path(path).read_bytes())
    model = read(model_path,'26908e992235e307cfc6145275deb3d2765a930c7c59a774c9a7bc42f2f0f95e')
    read(gate_path,'a74e821f70680187e0ee14fb956d51928e6aa9517acc1bc0186448b32c985ba0')
    checkpoint = read(checkpoint_path)
    ordered = checkpoint['ordered_cuts']
    need(len(ordered) == 9,'frozen nine-vector population')
    edges,blocks = make_blocks(model)
    block_path = args.out/'blocks.json'
    save(block_path,dict(blocks=blocks,edge_variables=edges,model_sha256=digest(model_path)))
    polynomials,raw_graphs = [],[]
    for index,record in enumerate(ordered):
        cert_path,audit_path = ROOT/record['certificate'],ROOT/record['audit']
        cert,audit = read(cert_path,record['certificate_sha256']),read(audit_path,record['audit_sha256'])
        need(audit['status'] == 'INDEPENDENT_TARGET_GRAM_BOX_NOGOOD_PASS','input vector checked box provenance')
        graph_paths = [ROOT/name for name,value in audit['inputs_sha256'].items() if value == cert['graph_sha256']]
        need(len(graph_paths) == 1,'raw graph binding')
        graph = read(graph_paths[0],cert['graph_sha256'])['adjacency_full59']
        vector = cert['integer_negative_vector']
        need(len(vector) == 59 and all(type(x) is int for x in vector),'integer vector')
        constant_graph = [row.copy() for row in graph]
        for var,u,v in edges:constant_graph[u+9][v+9] = constant_graph[v+9][u+9] = 0
        constant = sum(vector[u]*(27*int(u==v)-9*constant_graph[u][v]+1)*vector[v] for u in range(59) for v in range(59))
        coefficients = {str(var):-18*vector[u+9]*vector[v+9] for var,u,v in edges}
        current = constant+sum(coefficients[str(var)]*graph[u+9][v+9] for var,u,v in edges)
        need(constant == cert['linear_quadratic_constant'] and current == cert['quadratic_value_at_parent_graph'] < 0,'independently recomputed raw polynomial')
        polynomial = dict(index=index,vector=vector,constant=constant,coefficients=coefficients,parent_current_value=current,
                          graph_path=key(graph_paths[0]),graph_sha256=digest(graph_paths[0]),box_certificate=key(cert_path),box_certificate_sha256=digest(cert_path),
                          model_sha256=digest(model_path),blocks_sha256=digest(block_path))
        path = args.out/f'polynomial_{index:02d}.json'
        save(path,polynomial);bindings[key(path)] = digest(path)
        polynomials.append(polynomial);raw_graphs.append(graph)
    for path in (Path(__file__),Path(__file__).with_suffix('.md'),ROOT/'uv.lock'):
        bindings[key(path)] = digest(path)
    save(args.out/'manifest.json',dict(status='CANDIDATE_PREREGISTERED',timestamp=datetime.now(timezone.utc).isoformat(),
         source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),
         python=platform.python_version(),inputs_sha256=bindings,question='Degree-only maximum for all nine saved negative Gram vectors, then greedy strengthening of initial21literal pattern',
         scope='One exact780edge family; no common-neighbor constraints in this relaxation',limits=dict(overall_seconds=60,greedy_attempts=100),
         thresholds=dict(required_exact_upper_bound='strictly less than zero'),selection_rule='All9vectors in saved order, then initial21variables in ascending ID order',
         seed=20260930,seed_scope='Deterministic small calibration weights only; optimization itself has no random choices',
         no_independent_verification_claimed=True))
    started = time.monotonic();deadline = started+60
    control = controls();save(args.out/'controls.json',control)
    unrestricted,attempts = [],[]
    stop_reason = 'COMPLETE'
    baseline = None
    fixed = {}
    try:
        for index,polynomial in enumerate(tqdm(polynomials,desc='Exact degree bounds')):
            result = bound(polynomial,blocks,{},deadline)
            result['polynomial_sha256'] = digest(args.out/f'polynomial_{index:02d}.json')
            path = args.out/'no_fixed'/f'vector_{index:02d}.json';save(path,result)
            unrestricted.append(dict(index=index,exact_degree_relaxation_maximum=result['exact_degree_relaxation_maximum'],strictly_negative=result['strictly_negative'],path=key(path),sha256=digest(path)))
            save(args.out/f'checkpoint_no_fixed_{index:02d}.json',dict(completed=unrestricted,pending_indices=list(range(index+1,9)),elapsed_seconds=time.monotonic()-started))
        clause = ordered[0]['clause']
        fixed = {abs(literal):int(literal < 0) for literal in clause}
        baseline = bound(polynomials[0],blocks,fixed,deadline)
        need(baseline['strictly_negative'],'degree relaxation should not exceed independently negative box bound')
        save(args.out/'initial21_degree_bound.json',baseline)
        for variable in tqdm(sorted(fixed),desc='Greedy literal deletions'):
            if len(attempts) >= 100:stop_reason='GREEDY_ATTEMPT_CAP';break
            check_time(deadline)
            candidate = {v:value for v,value in fixed.items() if v != variable}
            result = bound(polynomials[0],blocks,candidate,deadline)
            accepted = result['strictly_negative']
            path = args.out/'greedy'/f'attempt_{len(attempts)+1:03d}.json'
            save(path,dict(tried_removing=variable,accepted=accepted,**result))
            if accepted:fixed=candidate
            attempts.append(dict(attempt=len(attempts)+1,removed_variable=variable,accepted=accepted,
                                 exact_degree_relaxation_maximum=result['exact_degree_relaxation_maximum'],path=key(path),sha256=digest(path)))
            save(args.out/f'checkpoint_greedy_{len(attempts):03d}.json',dict(current_fixed_values=fixed,attempts=attempts,remaining_variables_to_try=[v for v in sorted(fixed) if v > variable],elapsed_seconds=time.monotonic()-started))
    except TimeoutError as exc:
        stop_reason = 'OVERALL60SECOND_CAP';save(args.out/'resource_stop.json',dict(reason=str(exc),elapsed_seconds=time.monotonic()-started))
    clause = [-variable if value else variable for variable,value in sorted(fixed.items())] if baseline is not None else None
    final = dict(status='CANDIDATE_PENDING_INDEPENDENT_REVIEW',timestamp=datetime.now(timezone.utc).isoformat(),stop_reason=stop_reason,
                 completed_no_fixed_vectors=len(unrestricted),unrestricted_bounds=unrestricted,candidate_whole_family_negative_vectors=[r['index'] for r in unrestricted if r['strictly_negative']],
                 greedy_attempts=len(attempts),accepted_deletions=sum(r['accepted'] for r in attempts),attempts=attempts,
                 final_fixed_values=fixed,final_clause=clause,final_clause_length=len(clause) if clause is not None else None,
                 final_clause_null_reason=None if clause is not None else 'Initial degree-bound evaluation not completed before resource cap',
                 elapsed_seconds=time.monotonic()-started,scope='Degree-only necessary relaxation of one frozen780edge family',
                 verification='Producer controls and certificate self-checks only; a distinct agent/checker must validate before use',
                 target_resolution=False,solver_launched=False,external_review=False,
                 restart='Preserve this directory. Reinvoke this exact command with a fresh --out directory for the full cheap deterministic pilot; intermediate checkpoints preserve every completed bound and greedy state but no live optimizer is resumable.')
    save(args.out/'summary.json',final)
    print(json.dumps(dict(status=final['status'],completed_vectors=len(unrestricted),whole_family_negative_vectors=final['candidate_whole_family_negative_vectors'],
                          final_clause_length=final['final_clause_length'],attempts=len(attempts),elapsed=final['elapsed_seconds'],sha256=digest(args.out/'summary.json'))))


if __name__ == '__main__':main()
