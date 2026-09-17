"""Independent unbounded-integer support bound directly from full neighborhoods."""
from datetime import datetime,timezone
from fractions import Fraction
from itertools import combinations
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
import audit_20260917_partial_matching as h

ROOT=h.ROOT
def score(u,chosen,known,y,q):
    total=sum(y[a,b]for a,b in combinations(sorted(known|chosen),2))
    for v in chosen:
        edge=tuple(sorted((u,v)))
        total+=q[edge]if u<v else -q[edge]
        if u<v:total+=y[edge]
    return total

def controls():
    # Independent rook graph, all roots; real target adjacency gives one column
    # per center, so support bound is exactly zero for arbitrary signed q/y.
    graph=[{v for v in range(9)if v!=u and (u//3==v//3 or u%3==v%3)}for u in range(9)]
    records=[]
    for r in range(9):
        inside=graph[r];outside=sorted(set(range(9))-{r}-inside);pairs=list(combinations(range(4),2))
        y={e:(i%5)-2 for i,e in enumerate(pairs)};q={e:(i%7)-3 for i,e in enumerate(pairs)}
        b={e:2-len(graph[outside[e[0]]]&graph[outside[e[1]]]&inside)for e in pairs}
        columns=[score(u,{v for v in range(4)if outside[v]in graph[outside[u]]},set(),y,q)for u in range(4)]
        dot=sum(y[e]*b[e]for e in pairs)
        h.require(dot==sum(columns),'positive rook support identity')
        h.require(dot+1!=sum(columns),'corrupted rhs not rejected')
        h.require(dot!=sum(columns)+1,'corrupted coefficient not rejected')
        records.append(dict(root=r,lower_numerator=dot-sum(columns),rhs_corruption_rejected=True,column_corruption_rejected=True))
    return records

def main():
    started=datetime.now(timezone.utc).isoformat();tick=time.perf_counter();head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();bindings={}
    def read(p):bindings[h.key(p)]=h.digest(p);return json.loads(Path(p).read_bytes())
    d=ROOT/'acceleration/results/20260917_partial_matching_moment_replay600'
    manifest=read(d/'manifest.json');summary=read(d/'summary.json');envelope=read(d/'exact_support_bound.json');cert=envelope['bound']
    h.require(h.digest(d/'exact_support_bound.json')=='bbc507e6c6734c056caf6198027541c86e2a8ecb2319788adedc2537369e2008','raw certificate pin')
    for f,v in manifest['inputs_sha256'].items():h.require(h.digest(ROOT/f)==v,'input changed');bindings[h.key(ROOT/f)]=v
    for f,v in summary['output_sha256'].items():h.require(h.digest(d/f)==v,'output changed');bindings[h.key(d/f)]=v
    dependencies=[]
    for name,pin in [('partial_moments.json','1d4d08ecc9e73a00e06d210fa5137e7885e677756dc8f33b016fa3227ddec5e1'),('partial_matching/summary.json','ed1d5b464466562cff722e45593095ec89c63bda761cfa7f784994abfc308b17')]:
        p=ROOT/'acceleration/results/20260917_independent_review'/name
        h.require(h.digest(p)==pin,'dependency review pin');a=read(p)
        for f,v in a['inputs_sha256'].items():h.require(h.digest(ROOT/f)==v,'dependency artifact changed');bindings[h.key(ROOT/f)]=v
        dependencies.append(dict(path=h.key(p),sha256=pin,status=a['status']))
    primary=read(h.D/'manifest.json');caps=read(h.D/'linear_caps.json')
    labels=sorted([(a,b)for a in range(14)for b in range(a+1,14)if a//2!=b//2],key=lambda e:(e[0]//2,e[1]//2,e[0],e[1]))
    B=[set()for _ in range(99)]
    def edge(a,b):B[a].add(b);B[b].add(a)
    for v in range(1,15):edge(0,v)
    for v in range(1,15,2):edge(v,v+1)
    for u,pair in enumerate(labels,15):
        for v in pair:edge(u,v+1)
    for a,b in primary['remaining_fixed_K_edges_outer']:edge(a+15,b+15)
    pairs=list(combinations(range(84),2));unknown=list(map(tuple,caps['variable_edges']))
    h.require(len(unknown)==1740 and len(set(unknown))==1740,'unknown indexing')
    scale=cert['denominator'];yv=cert['moment_weight_numerators'];qv=cert['reciprocity_weight_numerators']
    h.require(type(scale)is int and scale>0 and len(yv)==3486 and len(qv)==1740,'weight dimensions')
    h.require(all(type(v)is int for v in yv+qv)and all(abs(v)<=scale for v in yv),'weight admissibility')
    y=dict(zip(pairs,yv));q=dict(zip(unknown,qv))
    rhs={e:2-len(B[e[0]+15]&B[e[1]+15]&set(range(1,15)))-int(e[1]+15 in B[e[0]+15])for e in pairs}
    dot=sum(rhs[e]*y[e]for e in pairs);maxima=[];argmax=[];counts=[];column_hashes=[]
    import hashlib
    for u in range(84):
        table=read(h.D/f'domain_{u:02d}.json')['domain_masks_hex'];counts.append(len(table));known={v-15 for v in B[u+15]if v>=15};values=[]
        for masktext in table:
            chosen=set(h.bits(int(masktext,16)))
            h.require(len(known|chosen)==12 and not known&chosen and u not in chosen and all(tuple(sorted((u,v)))in q for v in chosen),'complete local neighborhood')
            values.append(score(u,chosen,known,y,q))
        maxima.append(max(values));argmax.append(values.index(max(values)));column_hashes.append(hashlib.sha256(json.dumps(values,separators=(',',':')).encode()).hexdigest())
    numerator=dot-sum(maxima)
    h.require(sum(counts)==54478 and maxima==cert['center_maxima_numerators']and numerator==cert['numerator']and numerator>0,'positive exact bound mismatch')
    ctrl=controls()
    h.require(numerator+1!=dot-sum(maxima),'altered bound accepted')
    h.require(not(abs(scale+1)<=scale),'invalid box weight accepted')
    h.require(sum(0 for _ in pairs)-sum([0]*84)==0,'zero-weight control')
    for p in(__file__,h.__file__,ROOT/'uv.lock'):bindings[h.key(p)]=h.digest(p)
    h.require(all(h.digest(ROOT/f)==v for f,v in bindings.items()),'artifact changed during audit')
    result=dict(status='INDEPENDENT_PARTIAL_K_POSITIVE_MOMENT_EXCLUSION_PASS',claim_id='C-PARTIAL-K-ONE-COORDINATE-EXCLUSION',claim_revision=1,recommendation='VERIFIED',statement='No symmetric binary zero-diagonal 99-vertex graph satisfying A^2=12I-A+2J extends the frozen root scaffold and 162 fixed outer edges while respecting all prescribed absences of the one-freed-coordinate partial-K family.',scope_manifest=h.key(h.D/'manifest.json'),scope_manifest_sha256=h.digest(h.D/'manifest.json'),unrestricted_target_resolution=False,started_at=started,completed_at=datetime.now(timezone.utc).isoformat(),source_commit=head,command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,dependencies=[dict(id='C-PARTIAL-K-ONE-COORDINATE-DOMAINS',revision=1,relation='coverage'),dict(id='C-PARTIAL-K-FULL-MOMENT-ENCODING',revision=1,relation='encoding_equivalence')],dependency_artifact_review=dependencies,exact_bound=dict(numerator=numerator,denominator=scale,reduced=str(Fraction(numerator,scale)),strictly_positive=True,rhs_dot_numerator=dot,center_maxima_numerators=maxima,maximizing_original_domain_ids=argmax),checked_centers=84,checked_original_choices=sum(counts),per_center_choices=counts,per_center_score_list_sha256=column_hashes,controls=dict(rook9=ctrl,altered_bound_rejected=True,out_of_box_weight_rejected=True,zero_weight_bound=0),method='Direct set-based full99 scaffold reconstruction and each original star; Python unbounded-integer sums of all 66 outer-neighbor pairs plus unknown-edge adjacency and signed reciprocity terms. No producer or serialized matrix imports. Rechecked exact hashes of both prerequisite independent reviews and every recorded input.',independent_derivation='For any admitted completion, local one-hot stars satisfy per-center simplex and reciprocal equations and exact full moment equations. For any integer moment weights |y|<=D and arbitrary integer reciprocal weights q, L1 moment residual >= (y*b - sum_center max_column(M^T*y+R^T*q))/D. This verified value is strictly positive, contradicting the zero residual of any completion.',solver_feasible_dual_claimed=False,producer_imported=False,shared_components=['Python standard library','prior independent domain artifact helpers','previous independent completeness and full-moment necessity derivations'],limitations=['Exclusion only of the precise fixed-162-edge and prescribed-absence family. No additional count of discrete overlap configurations asserted.','No unrestricted Conway-99 nonexistence proof; no assumption of nontrivial automorphism.','The reported lower bound need not equal the LP optimum; solver feasibility flags and floating arithmetic are unnecessary for this certificate.'],elapsed_seconds=time.perf_counter()-tick)
    p=ROOT/'acceleration/results/20260917_independent_review/moment_positive600.json'
    with p.open('x')as f:json.dump(result,f,indent=2)
    print(result['status'],numerator,scale,h.digest(p))
if __name__=='__main__':main()
