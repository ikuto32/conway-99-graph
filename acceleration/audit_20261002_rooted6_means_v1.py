"""Independent ordered-wedge / marked-four-cycle audit; no producer imports.

Universal theorem review is the separately pinned written proof. These finite
integer checks calibrate definitions, test failure cases and check raw evidence.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import itertools as it
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
from tqdm import tqdm
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parent.parent
PAIRS = tuple(it.combinations(range(6), 2))
FREE = tuple(it.permutations(range(2, 6)))
PINS = {
 'docs/DERIVATION_20261002_ALMOST_PRISM_GLOBAL_MEAN.md': '15e4613fe217f8cde54d18eaeb59c57f89ccf0ce38912c95606730981e1b7d98',
 'docs/DERIVATION_20261002_PRISM_GLOBAL_PARAMETER_MEANS.md': 'fac0d9acd943c8c6f4daa98416b7dd8d2ff6a17ad078a1e10f36305e8865b73b',
 'docs/DERIVATION_20261002_PER_VERTEX_ROOTED6_MEANS.md': '53438904f2beee4176a825ca2b283b185a6a8d80457154d6751cd37c79444123',
 'acceleration/results/20260930_srg243_residual_fixture/adjacency243.json': '5c7c8268b7d62997b5c87a56b11fd673f3f80fcb029b83816179ee8127b8e0d3',
 'acceleration/results/20261002_almost_prism_global_mean01/rook9_adjacency.json': '65f6e5ebbd7353674605237a00a75d6ddabc88bd3b02e78d1992da939499679c',
 'acceleration/results/20261002_almost_prism_global_mean01/243_unordered_nonedge_a_counts.json': '730619a939fadc546d72503a1c4ac1c2f7c074b85895f9682026f39f38b13b0d',
 'acceleration/results/20261002_prism_global_parameter_means01/243_unordered_nonedge_b_counts.json': '730619a939fadc546d72503a1c4ac1c2f7c074b85895f9682026f39f38b13b0d',
 'acceleration/results/20261002_prism_global_parameter_means01/243_prism_six_sets.json': 'd15a402b5a8bdcfcb3d017522817767bf00ed823b2de0b770e2adb5859170bbf',
 'acceleration/results/20261002_per_vertex_rooted6_means01/rook9_vertex_totals.json': '9f5ad08d47839ab1b1227b6420754e4e8855f0b7adc172f3f59f62444cd63bba',
 'acceleration/results/20261002_per_vertex_rooted6_means01/243_vertex_totals.json': 'cf74897b4ccd5f11af23ecf0364e163e93d2645d6a6b410d8c4162643ae95609',
 'acceleration/results/20261002_per_vertex_rooted6_means01/saved_corner_rows.json': '50da3f7d00c9cafcf5c03aa7281e6f5de4ebf607c2f21a6679b6b6419037ea3a',
 'acceleration/results/20261002_rooted7_extension_model/model.json': '21eb899c3606727ef4e452d518316957cf9eb76e5e85c5a79af82421f4004595',
 'acceleration/results/20261002_rooted6_prismfree_rigidity/ordered_nonedge_model.json': 'ecf558faa95576b8e76fbc5a62743729a875307eeb99df803c7cb5cdac7b7645',
 'acceleration/results/20261002_rooted7_corner_certificates02/corner_0_0.json': '71f30c7108cdcae7df865974270ea20ff0c9020fda7f1cfb05a8bdb2bfd7a62f',
 'acceleration/results/20261002_rooted7_corner_certificates02/corner_20_0.json': '233d9505e9fb7c8edeea4d7e92a9b4d34397613a91cc051f4776d917f4c33842',
 'acceleration/results/20261002_rooted7_corner_certificates02/corner_0_9.json': '7539fa5df54dcc2f86826147ae5d12a3054b94941fa405f3c4ee778c4f1efd61',
 'acceleration/results/20261002_rooted7_corner_certificates02/corner_20_9.json': '28f22f119f1eb5240a76cbed01f3c540f6e7f87bcecccac9bbcc3df49b92bcad',
}

class AuditError(ValueError):
    def __init__(self, stage, detail):
        self.stage = stage
        super().__init__(f'{stage}: {detail}')

def require(test, stage, detail):
    if not test:
        raise AuditError(stage, detail)

def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()

def load(path):
    with open(ROOT/path, encoding='utf-8') as f:
        return json.load(f)

def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, indent=2, sort_keys=True)
        f.write('\n')

def check_time(deadline):
    require(deadline.status()['remaining_seconds'] > 20,
            'DEADLINE', 'not completed within allocated budget; save/shutdown reserve')

def mask_graph(mask):
    g = [set() for _ in range(6)]
    for bit, (u,v) in enumerate(PAIRS):
        if mask >> bit & 1:
            g[u].add(v); g[v].add(u)
    return g

def encode(g, labels):
    return sum(1 << bit for bit,(i,j) in enumerate(PAIRS)
               if labels[j] in g[labels[i]])

def orbit(mask):
    g = mask_graph(mask)
    return {encode(g, (0,1)+p) for p in FREE}

A_ORBIT = orbit(8024)
B_ORBIT = orbit(15540)
PRISM_ORBIT = {encode(mask_graph(8025), p) for p in it.permutations(range(6))}

def graph_domain(matrix):
    require(isinstance(matrix,list) and len(matrix)>0, 'GRAPH_DOMAIN', 'nonempty square matrix')
    n=len(matrix)
    require(all(isinstance(row,list) and len(row)==n for row in matrix), 'GRAPH_DOMAIN', 'square')
    require(all(type(x) is int and x in (0,1) for row in matrix for x in row), 'GRAPH_DOMAIN', 'binary integers')
    require(all(matrix[u][u]==0 for u in range(n)), 'GRAPH_DOMAIN', 'zero diagonal')
    require(all(matrix[u][v]==matrix[v][u] for u in range(n) for v in range(n)), 'GRAPH_DOMAIN', 'symmetric')
    return [{v for v,x in enumerate(row) if x} for row in matrix]

def srg(matrix, k, deadline):
    g=graph_domain(matrix); n=len(g)
    require(all(len(x)==k for x in g), 'SRG_SCOPE', 'degree')
    require(n-k-1>0, 'SRG_SCOPE', 'nonedges')
    for u in range(n):
        if u%20==0: check_time(deadline)
        for v in range(n):
            # A separate literal scalar row/column integer product; no producer validator.
            value=sum(matrix[u][w]*matrix[w][v] for w in range(n))
            expected=k if u==v else 1 if matrix[u][v] else 2
            require(value==expected,'SRG_IDENTITY',f'entry{u},{v}: {value}!={expected}')
    require(2*(n-k-1)==k*(k-2), 'SRG_SCOPE', 'parameter double count')
    return g, {'vertices':n,'degree':k,'scalar_entries_checked':n*n,
               'adjacent_pair_common_neighbors':1,'nonadjacent_pair_common_neighbors':2}

def triangles(g):
    return [tuple((u,v,w)) for u in range(len(g)) for v in sorted(g[u]) if v>u
            for w in sorted(g[u]&g[v]) if w>v]

def caps(g):
    return all(len(g[u]&g[v]) <= (1 if v in g[u] else 2)
               for u in range(len(g)) for v in range(u+1,len(g)))

def triangle_pairs(g, deadline):
    ts=triangles(g); prism=set(); b=Counter(); counts=Counter(); pair_attempts=0
    for i,t in enumerate(ts):
        if i%30==0: check_time(deadline)
        for s in ts[i+1:]:
            pair_attempts+=1
            if set(t)&set(s): continue
            cross=[(x,y) for x in t for y in s if y in g[x]]
            require(len({x for x,y in cross})==len(cross) and
                    len({y for x,y in cross})==len(cross),'TRIANGLE_CROSS','cross matching')
            counts[len(cross)]+=1
            six=tuple(sorted(t+s))
            if len(cross)==3:
                require(six not in prism,'PRISM_UNIQUENESS','unique two triangles')
                prism.add(six)
            if len(cross)==2:
                u=next(x for x in t if all(x!=a for a,z in cross))
                v=next(y for y in s if all(y!=z for a,z in cross))
                labels=(u,v)+tuple(x for x in six if x not in (u,v))
                require(encode(g,labels) in B_ORBIT,'B_SHAPE','missing matching edge')
                b[(min(u,v),max(u,v),six)]+=1
    require(all(v==1 for v in b.values()),'B_UNIQUENESS','one triangle pair per rooted occurrence')
    return ts,prism,b,{'all_unordered_triangle_pairs_attempted':pair_attempts,
                        'disjoint_triangle_pair_cross_histogram':dict(counts)}

def classify(g,u,v,six,kind):
    require(len(six)==6,'BIJECTION_SHAPE','six distinct vertices')
    labels=(u,v)+tuple(x for x in six if x not in (u,v))
    value=encode(g,labels)
    if v in g[u]:
        require(value in PRISM_ORBIT,'BIJECTION_SHAPE','prism')
        return 'prism'
    require(value in (A_ORBIT if kind=='a' else B_ORBIT), 'BIJECTION_SHAPE', kind)
    return kind

def ordered_wedges(g, deadline, complete):
    """Fixed u: ordered (x,w) nonadjacent neighbors; p,y,v uniquely forced."""
    a=Counter(); prism=Counter(); tried=0; skipped=0
    for u in range(len(g)):
        check_time(deadline)
        for x in sorted(g[u]):
            for w in sorted(g[u]-g[x]-{x}):
                tried+=1
                common=g[x]&g[w]
                if len(common)!=2 or u not in common:
                    require(not complete,'WEDGE_COMPLETE','two common neighbors'); skipped+=1; continue
                p=next(z for z in common if z!=u)
                third=g[p]&g[x]
                if len(third)!=1:
                    require(not complete,'WEDGE_COMPLETE','unique px triangle'); skipped+=1; continue
                y=next(iter(third))
                common=g[w]&g[y]
                if len(common)!=2 or p not in common:
                    require(not complete,'WEDGE_COMPLETE','two wy common neighbors'); skipped+=1; continue
                v=next(z for z in common if z!=p)
                six=tuple(sorted((u,v,x,w,p,y)))
                result=classify(g,u,v,six,'a')
                if result=='a': a[(u,v,six)]+=1
                else: prism[(u,six)]+=1
    return a,prism,{'ordered_neighbor_wedges_attempted':tried,'unsupported_partial_graph_wedges':skipped}

def triangle_seed_a(g, deadline, complete):
    """Independent unordered triangle seed, not the producer matching routine."""
    a=Counter(); prism=Counter(); attempted=0; skipped=0
    for t in triangles(g):
        check_time(deadline)
        for p in t:
            x,y=sorted(set(t)-{p})
            for w in sorted(g[p]-set(t)):
                attempted+=1
                c1=(g[x]&g[w])-{p}; c2=(g[y]&g[w])-{p}
                if len(c1)!=1 or len(c2)!=1:
                    require(not complete,'TRIANGLE_SEED_COMPLETE','forced two endpoints'); skipped+=1; continue
                u=next(iter(c1)); v=next(iter(c2)); six=tuple(sorted((u,v,w,p,x,y)))
                result=classify(g,u,v,six,'a')
                if result=='a': a[(min(u,v),max(u,v),six)]+=1
                else: prism[six]+=1
    return a,prism,{'triangle_seed_a_attempts':attempted,'unsupported_partial_graph_seeds':skipped}

def marked_fourcycles(g, deadline, complete):
    """Fixed u: triangle {u,p,q} and induced C4 p,q,y,x; extend edge xy."""
    b=Counter(); prism=Counter(); tried=0; skipped=0
    for u in range(len(g)):
        check_time(deadline)
        for p in sorted(g[u]):
            for q in sorted(g[u]&g[p]):
                if p>=q: continue
                for x in sorted(g[p]-{u,p,q}):
                    tried+=1
                    other=(g[x]&g[q])-{p}
                    if len(other)!=1:
                        require(not complete,'C4_COMPLETE','other common neighbor'); skipped+=1; continue
                    y=next(iter(other)); third=g[x]&g[y]
                    if len(third)!=1:
                        require(not complete,'C4_COMPLETE','xy unique third vertex'); skipped+=1; continue
                    v=next(iter(third)); six=tuple(sorted((u,v,p,q,x,y)))
                    result=classify(g,u,v,six,'b')
                    if result=='b': b[(u,v,six)]+=1
                    else: prism[(u,six)]+=1
    return b,prism,{'marked_triangle_fourcycle_attempts':tried,'unsupported_partial_graph_cycles':skipped}

def direct_six(g, deadline):
    """All six-subsets/all ordered root nonedges; only used on <=9 vertices."""
    a=Counter(); b=Counter(); prism=set(); attempted=0
    for six in it.combinations(range(len(g)),6):
        check_time(deadline)
        if encode(g,six) in PRISM_ORBIT: prism.add(six)
        for u,v in it.permutations(six,2):
            if v in g[u]: continue
            attempted+=1
            value=encode(g,(u,v)+tuple(x for x in six if x not in (u,v)))
            if value in A_ORBIT: a[(u,v,six)]+=1
            if value in B_ORBIT: b[(u,v,six)]+=1
    return a,b,prism,attempted

def incidence_check(a,wa,wp,sa,sp,b,wb,bp,prism):
    require(all(v==1 for v in wa.values()),'A_MULTIPLICITY','wedge exactly once per ordered rooted flag')
    expected_a=Counter()
    for (u,v,six), count in sa.items():
        require(count==1,'A_MULTIPLICITY','triangle seed exactly once per unordered rooted flag')
        expected_a[(u,v,six)]=1; expected_a[(v,u,six)]=1
    require(wa==expected_a,'A_PATH_AGREEMENT','ordered wedges versus independent triangle seed')
    expected_b=Counter()
    for (u,v,six),count in b.items():
        require(count==1,'B_MULTIPLICITY','unordered triangle pair once')
        expected_b[(u,v,six)]=1; expected_b[(v,u,six)]=1
    require(wb==expected_b,'B_PATH_AGREEMENT','marked cycles versus disjoint triangle pair')
    expected_wp=Counter({(u,six):2 for six in prism for u in six})
    expected_bp=Counter({(u,six):1 for six in prism for u in six})
    require(wp==expected_wp,'A_PRISM_MULTIPLICITY','two wedges per prism/vertex')
    require(bp==expected_bp,'B_PRISM_MULTIPLICITY','one marked cycle per prism/vertex')
    require(sp==Counter({six:6 for six in prism}),'A_PRISM_MULTIPLICITY','six triangle seeds per prism')
    if a is not None: require(a==wa,'DIRECT_A','all six-subsets')
    return expected_b

def pair_counts(g, entries, ordered):
    result=Counter()
    for (u,v,six),c in entries.items():
        if not ordered:
            if u>v: continue
        result[(min(u,v),max(u,v))]+=c
    return [[u,v,result[(u,v)]] for u in range(len(g)) for v in range(u+1,len(g)) if v not in g[u]]

def vertex_rows(g,a,b,prism):
    sa=Counter(); sb=Counter(); tu=Counter()
    for (u,v,six),c in a.items(): sa[u]+=c
    for (u,v,six),c in b.items(): sb[u]+=c
    for six in prism:
        for u in six: tu[u]+=1
    return [{'vertex':u,'sum_a_over_nonneighbors':sa[u],'sum_b_over_nonneighbors':sb[u],
             'prisms_containing_vertex':tu[u]} for u in range(len(g))]

def mean_check(rows,n,k):
    require(len(rows)==n and [r['vertex'] for r in rows]==list(range(n)), 'MEAN_SCOPE','all vertices')
    for r in rows:
        require(r['sum_a_over_nonneighbors']+2*r['prisms_containing_vertex']==k*(k-2) and
                r['sum_b_over_nonneighbors']+r['prisms_containing_vertex']==n-k-1,
                'MEAN_IDENTITY',f'vertex {r["vertex"]}')

def fixture(matrix,k,label,out,deadline):
    g,identity=srg(matrix,k,deadline)
    ts,prism,b,tc=triangle_pairs(g,deadline)
    wa,wp,wc=ordered_wedges(g,deadline,True)
    sa,sp,sc=triangle_seed_a(g,deadline,True)
    wb,bp,bc=marked_fourcycles(g,deadline,True)
    db=incidence_check(None,wa,wp,sa,sp,b,wb,bp,prism)
    if len(g)<=9:
        da,direct_b,direct_prism,dcount=direct_six(g,deadline)
        require(wa==da and wb==direct_b and prism==direct_prism,'DIRECT_SIX','all rooted shapes/prisms')
    else: dcount=None
    rows=vertex_rows(g,wa,wb,prism); mean_check(rows,len(g),k)
    result={'label':label,'identity':identity,'triangles':len(ts),'prism_sixsets':len(prism),
            'distinct_ordered_root_a_occurrences':len(wa),'distinct_ordered_root_b_occurrences':len(wb),
            'direct_rooted_sixsubset_attempts':dcount,**tc,**wc,**sc,**bc,
            'all_prism_vertex_multiplicities_checked':len(prism)*6,
            'sum_a':sum(r['sum_a_over_nonneighbors'] for r in rows),
            'sum_b':sum(r['sum_b_over_nonneighbors'] for r in rows)}
    save(out/f'{label}_vertex_totals.json',rows)
    save(out/f'{label}_unordered_a_counts.json',pair_counts(g,wa,False))
    save(out/f'{label}_unordered_b_counts.json',pair_counts(g,wb,False))
    save(out/f'{label}_prism_sixsets.json',sorted(prism))
    # Save each exact incidence rather than reducing agreement to a scalar total.
    save(out/f'{label}_a_prism_incidence_multiplicities.json',[[u,list(s),c] for (u,s),c in sorted(wp.items())])
    save(out/f'{label}_b_prism_incidence_multiplicities.json',[[u,list(s),c] for (u,s),c in sorted(bp.items())])
    return result,rows,g,wa,wb,prism

def expect_failure(controls,label,stage,call):
    try: call()
    except AuditError as e:
        require(e.stage==stage,'CONTROL_STAGE',f'{label}: wanted {stage}, actual {e.stage}')
        controls.append({'label':label,'outcome':'REJECTED_EXPECTED','stage':e.stage,'diagnostic':str(e)})
    else: raise AuditError('CONTROL_FAILURE',f'{label}: corruption accepted')

def controls(deadline):
    records=[]; positives=[]
    for mask,kind in ((8024,'a'),(15540,'b'),(8025,'prism')):
        g=mask_graph(mask)
        require(caps(g),'CONTROL_POSITIVE','local common-neighbor caps')
        a,db,pr,attempts=direct_six(g,deadline)
        ts,prism,b,tc=triangle_pairs(g,deadline)
        wa,wp,wc=ordered_wedges(g,deadline,False)
        sa,sp,sc=triangle_seed_a(g,deadline,False)
        wb,bp,bc=marked_fourcycles(g,deadline,False)
        eb=incidence_check(a,wa,wp,sa,sp,b,wb,bp,prism)
        require(db==eb and pr==prism,'DIRECT_PATTERN','six-vertex positive')
        require((len(a),len(db),len(pr))==({'a':(2,0,0),'b':(0,2,0),'prism':(0,0,1)}[kind]),
                'CONTROL_POSITIVE','nonzero exact counts')
        positives.append({'mask':mask,'ordered_a':len(a),'ordered_b':len(db),'prisms':len(pr),
                          'wedge_prism_incidences':sum(wp.values()),'cycle_prism_incidences':sum(bp.values()),
                          'scope':'raw induced pattern; not an SRG fixture'})
        if kind=='a':
            expect_failure(records,'nonzero_a_wrong_mask','BIJECTION_SHAPE',lambda:classify(mask_graph(15540),0,1,tuple(range(6)),'a'))
        if kind=='b':
            expect_failure(records,'nonzero_b_wrong_root_endpoints','BIJECTION_SHAPE',lambda:classify(g,0,2,tuple(range(6)),'b'))
    require(encode(mask_graph(8024),(1,0,2,3,4,5)) in A_ORBIT and
            encode(mask_graph(15540),(1,0,2,3,4,5)) in B_ORBIT,'ROOT_SWAP','same orbit with ordered roots swapped')
    require(A_ORBIT.isdisjoint(B_ORBIT),'PATTERN_DISTINCTION','remove different prism edge types')
    # All completions of the eight required edges, independently testing every
    # otherwise unspecified internal edge. lambda<=1 alone must leave precisely
    # the missing-root-edge alternatives; no floating point or SAT producer.
    extra_edge_controls=[]
    for mask in (8024,15540):
        unset=[bit for bit in range(15) if not mask>>bit&1]
        surviving=[]
        for extra in range(1<<len(unset)):
            value=mask|sum(1<<bit for j,bit in enumerate(unset) if extra>>j&1)
            if all(len(mask_graph(value)[u]&mask_graph(value)[v])<=1
                   for u,v in PAIRS if value>>PAIRS.index((u,v))&1): surviving.append(value)
        require(surviving==[mask,mask|1],'FORCED_EDGE_EXHAUSTION','only a/b and prism alternatives')
        extra_edge_controls.append({'required_mask':mask,'all_completions':1<<len(unset),
                                    'lambda_cap_survivors':surviving})
    return records,positives,extra_edge_controls

def corner_screen(deadline):
    model=load('acceleration/results/20261002_rooted7_extension_model/model.json')
    variables=model['variables']; rawrows=model['equations']
    require(len(variables)==2766 and len(rawrows)==11749,'CORNER_SCOPE','frozen operator dimensions')
    equations=[]
    for anchor,parts in ((0,(0,2)),(1,(0,1))):
        for coordinate,constant in ((0,168),(1,84)):
            indices=[variables.index(['aggregate',anchor,p,coordinate]) for p in parts]
            rhs=[constant,-1 if coordinate==0 else 0,-1 if coordinate==1 else 0]
            equations.append({'anchor':anchor,'coordinate':coordinate,'partitions':list(parts),
                              'literal_terms':[[i,1] for i in indices],'rhs_affine':rhs})
    results=[]
    for a,b in ((0,0),(20,0),(0,9),(20,9)):
        check_time(deadline)
        raw=load(f'acceleration/results/20261002_rooted7_corner_certificates02/corner_{a}_{b}.json')
        require(raw['parameters']==[a,b] and len(raw['exact_values'])==2766,'CORNER_SCOPE','literal vector')
        vector=[Fraction(x,y) for x,y in raw['exact_values']]
        require(all(x>=0 for x in vector),'CORNER_SCOPE','nonnegative vector')
        for row in rawrows:
            lhs=sum(c*vector[i] for i,c in row['terms'])
            c,ca,cb=row['rhs_affine']
            require(lhs==c+ca*a+cb*b,'CORNER_ORIGINAL_ROW','literal frozen operator')
        local=[]
        for row in equations:
            lhs=sum(c*vector[i] for i,c in row['literal_terms'])
            c,ca,cb=row['rhs_affine']; rhs=c+ca*a+cb*b; residual=lhs-rhs
            require(residual==0,'CORNER_MEAN_ROW','saved exact witness')
            local.append({**row,'left':[lhs.numerator,lhs.denominator],'rhs':rhs,
                          'residual':[residual.numerator,residual.denominator]})
        results.append({'parameters':[a,b],'original_rows_checked':11749,'derived_rows':local,
                        'meaning':'necessary-relaxation witness only; no realized graph'})
    prior=load('acceleration/results/20261002_per_vertex_rooted6_means01/saved_corner_rows.json')
    require(len(prior)==4,'RAW_CORNER_RECORD','all prior corners')
    for old,new in zip(prior,results):
        require(old['parameters']==new['parameters'],'RAW_CORNER_RECORD','same frozen corner order')
        for o,n in zip(old['proposed_four_rows'],new['derived_rows']):
            for field in ('anchor','coordinate','partitions','literal_terms','rhs_affine','left','rhs','residual'):
                require(o[field]==n[field],'RAW_CORNER_RECORD',f'field {field}')
    return equations,results

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--seconds',type=float,required=True)
    ap.add_argument('--allocation-reason',required=True); ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args(); start=time.monotonic()
    deadline=CommandDeadline(args.seconds,allocation_reason=args.allocation_reason)
    out=args.out; out.mkdir(parents=True,exist_ok=False)
    inputs={}
    proof='acceleration/audit_20261002_rooted6_means_v1_proof.md'
    spec='acceleration/audit_20261002_rooted6_means_v1_spec.md'
    for p,want in PINS.items():
        check_time(deadline); actual=sha(ROOT/p)
        require(actual==want,'INPUT_IDENTITY',p); inputs[p]=actual
    for p in (Path(__file__).relative_to(ROOT).as_posix(),proof,spec,
              'acceleration/command_deadline.py','acceleration/run_compute_command.py','uv.lock','pyproject.toml'):
        inputs[p]=sha(ROOT/p)
    source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    manifest={'source_commit':source,'command':[sys.executable,*sys.argv], 'cwd':str(ROOT),
              'python_version':platform.python_version(),'timestamp':datetime.now(timezone.utc).isoformat(),
              'inputs_sha256':inputs,'selection':'All declared finite controls and every raw fixture vertex/incidence; all four saved corners.',
              'success':'Full exact raw agreement; specific corruption rejection; written complete independent derivation.',
              'scope':'Universal necessary pervertex/global identities under srg(n,k,1,2); no target resolution or prism absence.',
              'allocation_seconds':args.seconds,'shutdown_reserve_seconds':20,
              'shared_components':['command_deadline.py (scheduling only)','tqdm (progress only)','Python stdlib integer/Fraction arithmetic'],
              'producer_code_imports':[],'proof':proof}
    save(out/'manifest.json',manifest)
    coordinate_model=load('acceleration/results/20261002_rooted6_prismfree_rigidity/ordered_nonedge_model.json')
    require(coordinate_model['variables'][552]==[6,8024] and
            coordinate_model['variables'][566]==[6,15540], 'COORDINATE_BINDING','literal a/b axes')
    neg,pos,extras=controls(deadline)
    rookraw=load('acceleration/results/20261002_almost_prism_global_mean01/rook9_adjacency.json')
    rook=rookraw['adjacency']
    large=load('acceleration/results/20260930_srg243_residual_fixture/adjacency243.json')['adjacency']
    fixture_records=[]
    for label,matrix,k in tqdm([('rook9',rook,4),('srg243',large,22)],desc='Independent exact fixtures'):
        result,rows,g,a,b,prism=fixture(matrix,k,label,out,deadline); fixture_records.append(result)
        prior=load(f'acceleration/results/20261002_per_vertex_rooted6_means01/{"243" if label=="srg243" else "rook9"}_vertex_totals.json')
        require(rows==prior,'RAW_VERTEX_RECORD','every saved vertex row')
        changed=json.loads(json.dumps(rows)); changed[0]['sum_a_over_nonneighbors']+=1
        expect_failure(neg,f'{label}_changed_pair_a','MEAN_IDENTITY',lambda:mean_check(changed,len(g),k))
        changed=json.loads(json.dumps(rows)); changed[0]['sum_b_over_nonneighbors']+=1
        expect_failure(neg,f'{label}_changed_pair_b','MEAN_IDENTITY',lambda:mean_check(changed,len(g),k))
        changed=json.loads(json.dumps(rows)); changed[0]['prisms_containing_vertex']-=1
        expect_failure(neg,f'{label}_removed_prism_incidence','MEAN_IDENTITY',lambda:mean_check(changed,len(g),k))
        damaged=[row[:] for row in matrix]; damaged[0][0]=1
        expect_failure(neg,f'{label}_corrupt_diagonal','GRAPH_DOMAIN',lambda:srg(damaged,k,deadline))
        damaged=[row[:] for row in matrix]; damaged[0][1]=1-damaged[0][1]
        expect_failure(neg,f'{label}_corrupt_asymmetry','GRAPH_DOMAIN',lambda:srg(damaged,k,deadline))
        damaged=[row[:] for row in matrix]; damaged[0][1]=2
        expect_failure(neg,f'{label}_corrupt_nonbinary','GRAPH_DOMAIN',lambda:srg(damaged,k,deadline))
        expect_failure(neg,f'{label}_wrong_regular_degree','SRG_SCOPE',lambda:srg(matrix,k+1,deadline))
        damaged_wp=Counter({(u,s):2 for s in prism for u in s}); key=next(iter(damaged_wp)); damaged_wp[key]-=1
        expect_failure(neg,f'{label}_wrong_a_prism_factor','A_PRISM_MULTIPLICITY',
                       lambda:incidence_check(None,a,damaged_wp,*triangle_seed_a(g,deadline,True)[:2],
                          triangle_pairs(g,deadline)[2],b,Counter({(u,s):1 for s in prism for u in s}),prism))
        if label=='srg243':
            require(pair_counts(g,a,False)==load('acceleration/results/20261002_almost_prism_global_mean01/243_unordered_nonedge_a_counts.json'),
                    'RAW_A_COUNTS','all unordered nonedges')
            require(pair_counts(g,b,False)==load('acceleration/results/20261002_prism_global_parameter_means01/243_unordered_nonedge_b_counts.json'),
                    'RAW_B_COUNTS','all unordered nonedges')
            require(sorted(prism)==[tuple(s) for s in load('acceleration/results/20261002_prism_global_parameter_means01/243_prism_six_sets.json')],
                    'RAW_PRISM_COUNTS','all sixsets, no omissions/duplicates')
    equations,corners=corner_screen(deadline)
    save(out/'derived_root7_rows.json',equations); save(out/'saved_corner_exact_screen.json',corners)
    save(out/'controls.json',{'positive_nonzero_pattern_controls':pos,'extra_edge_completion_controls':extras,
                              'negative_controls':neg,'root_swap_orbits_checked':True})
    outputs={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(out.iterdir()) if p.is_file()}
    statement=('For every finite simple srg(n,k,1,2) with n-k-1>0, every vertex u satisfies '
      'sum_{v nonadjacent u} a(u,v)+2T_u=k(k-2) and sum_{v nonadjacent u} b(u,v)+T_u=n-k-1, '
      'where a,b count ordered-root/unordered-four-subset induced flags in the free-label orbits of masks8024,15540 '
      'and T_u counts induced triangular-prism sixsets containing u once. Consequently sum_ordered a=nk(k-2)-12T '
      'and sum_ordered b=n(n-k-1)-6T. No graph automorphism or prism absence is assumed.')
    report={'status':'INDEPENDENT_ROOTED6_PER_VERTEX_GLOBAL_MEANS_V1_PASS',
            'timestamp':datetime.now(timezone.utc).isoformat(),'verifier':'/root/checkpoint_audit',
            'producer':'/root/structural','statement':statement,'claim_status':'VERIFIED_WITHIN_EXACT_SCOPE',
            'method':'independent_derivation_and_complete_artifact_checking','written_proof':proof,
            'source_commit':source,'inputs_sha256':inputs,'outputs_sha256':outputs,
            'fixture_records':fixture_records,'all_saved_corners_checked':4,'saved_corners_passing_derived_rows':4,
            'derived_conditional_root7_rows':4,'negative_controls_rejected':len(neg),
            'nonzero_positive_pattern_controls':len(pos),'exhaustive_extra_edge_completions':256,
            'root_swap_same_free_orbit':True,'numerical_or_modular_solver_calls':0,
            'target_resolution':False,'profiles_excluded':0,'prism_absence_status':'UNKNOWN',
            'elapsed_seconds':time.monotonic()-start,'deadline':deadline.status(),
            'limitations':['Fixture identities alone do not prove the universal theorem; the pinned written bijections do.',
              'Raw sixvertex patterns are positive shape/incidence controls and are not SRG fixtures.',
              'Rook9/243 a,b counts are zero; exhaustive nonzero rawshape paths and forbidden-edge controls address that limitation.',
              'Four saved relaxation witnesses remain feasible for the new mean rows; no graph realization/profile exclusion follows.',
              'No novelty claim; archive Wave35 overlap is disclosed by producer docs, not freshly verified here.',
              'No target graph, general nonexistence proof, targetwide coverage or independent external review.']}
    save(out/'summary.json',report)
    print(json.dumps({'status':report['status'],'report':str(out/'summary.json'),'sha256':sha(out/'summary.json'),
                      'elapsed_seconds':report['elapsed_seconds']}))

if __name__=='__main__': main()
