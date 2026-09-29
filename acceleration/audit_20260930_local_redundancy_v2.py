"""Independent exact review of two local redundancy lemmas; no producer imports."""
from datetime import datetime,timezone
from hashlib import sha256
import itertools
import json
from pathlib import Path
import platform
import subprocess
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'acceleration/results/20260930_independent_review/local_redundancy_v2'
def h(p):return sha256((ROOT/p).read_bytes()).hexdigest()
def save(p,v):
    with p.open('x',encoding='utf-8')as f:json.dump(v,f,indent=2);f.write('\n')
def caps(n,edges):
    a=[[int(i!=j and tuple(sorted((i,j))) in edges) for j in range(n)] for i in range(n)]
    return all(sum(a[i][k]*a[k][j] for k in range(n))<=2-a[i][j] for i in range(n) for j in range(i+1,n))
def matching_controls():
    universe=list(itertools.combinations(range(4),2));checked=0;premises=0
    for bits in range(1<<len(universe)):
        g={e for k,e in enumerate(universe) if bits>>k&1}
        for m_bits in range(1<<len(universe)):
            m={e for k,e in enumerate(universe) if m_bits>>k&1};ends=[v for e in m for v in e]
            if len(set(ends))!=len(ends):continue
            if any(x in ends and y in ends for x,y in g):continue
            checked+=1
            if caps(4,g) and all(caps(4,g|{e}) for e in m):
                premises+=1;assert caps(4,g|m)
    g={(0,3),(0,4),(1,2),(2,4)};m={(0,1),(2,3)}
    assert caps(5,g) and all(caps(5,g|{e}) for e in m) and not caps(5,g|m)
    g={(0,1),(0,2),(0,3)};m={(1,2),(1,3)}
    assert caps(4,g) and all(caps(4,g|{e}) for e in m) and not caps(4,g|m)
    g={(0,i) for i in range(1,7)};m={(1,2),(3,4),(5,6)}
    assert caps(7,g|m)
    return dict(exhaustive_four_vertex_base_graphs=64,independent_endpoint_partial_matching_cases=checked,satisfying_premises=premises,removed_independence_counterexample=True,overlapping_added_edges_counterexample=True,windmill_positive=True)

def check_case(case):
    rows=[int(s,16) for s in case['adjacency_rows_hex']];n=len(rows);assert n==28
    assert all(0<=r<(1<<n) for r in rows)
    a=np.array([[(r>>j)&1 for j in range(n)] for r in rows],dtype=np.int64)
    assert np.array_equal(a,a.T) and not np.diag(a).any()
    v,u=case['centers_local'];assert v!=u and a[v,u]==0
    sets=[{j for j in range(n) if a[i,j]} for i in range(n)]
    assert len(sets[v])==len(sets[u])==14
    assert sets[v]|sets[u]|{v,u}==set(range(n)) and len(sets[v]&sets[u])==2
    for c in (v,u):
        assert all(len(sets[c]&sets[x])==2-int(a[c,x]) for x in range(n) if x!=c)
    retained=[i for i in range(n) if i not in (v,u)];deg=[len(sets[i]&set(retained)) for i in retained]
    assert max(deg)<=3
    gram=27*np.eye(n,dtype=np.int64)-9*a+np.ones((n,n),dtype=np.int64)
    for c in (v,u):
        kernel=a[c].copy();kernel[c]=4;assert not (gram@kernel).any()
    z={i:np.zeros(n,dtype=np.int64) for i in retained}
    for i in retained:z[i][i]=4;z[i][v]=-a[v,i];z[i][u]=-a[u,i]
    factors=[]
    for i in retained:
        for j in retained:
            if i<j and a[i,j]:factors.append(3*(z[i]-z[j]))
    for i,d in zip(retained,deg):
        factors.extend([3*z[i]]*(3-d))
    factors.append(sum(z.values(),np.zeros(n,dtype=np.int64)))
    f=np.stack(factors)
    # Integer dot arithmetic is exact: every term bounded, with < 80 terms.
    assert len(f)<=79 and np.max(np.abs(f))<=14 and 79*14*14<(1<<63)
    assert np.array_equal(f.T@f,16*gram)
    labels=case['selected_full99_vertices'];assert len(labels)==len(set(labels))==28
    assert labels[v]==0 and labels[u]==15+case['outer_vertex'] and set(range(15)).issubset(labels)
    outer_mask=sum(1<<(labels[j]-15) for j in sets[u] if labels[j]>=15)
    assert int(case['star_mask'],16) & ~outer_mask == 0  # Saved variable-edge mask is a subset, not the full row.
    # This verifies each recorded matrix and map, not the entire enumeration.
    return dict(vertices=n,remaining_max_degree=max(deg),factor_rows=len(f),coefficients_checked=n*n),f,gram

def main():
    OUT.mkdir(exist_ok=False);now=datetime.now(timezone.utc).isoformat()
    proof1='acceleration/theory_20260930_matching_cap_composition.md';proof2='acceleration/theory_20260930_closed28_gram_redundancy.md'
    common=dict(timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(Path.cwd()),python=platform.python_version(),numpy=np.__version__,verifier='/root independent written and exact raw-matrix review',recommendation='VERIFIED',claim_revision=1,external_review=False,target_resolution=False)
    controls=matching_controls()
    cap=dict(**common,status='INDEPENDENT_MATCHING_CAP_COMPOSITION_LEMMA_PASS',claim_id='C-INDEPENDENT-SET-MATCHING-CAP-COMPOSITION',
        statement='For every finite simple graph G, independent set R and matching M with endpoints in R, if G and every single-edge extension G+e for e in M have common-neighbor counts at most 2-adjacency for all distinct pairs, then G+M has the same caps.',
        kind='mathematical result',basis=['DERIVED'],scope='Universal finite-graph implication under independent-endpoint and matching hypotheses; only common-neighbor upper caps, not graph completion.',dependencies=[],
        inputs_sha256={p:h(p) for p in [proof1,Path(__file__).relative_to(ROOT).as_posix(),'uv.lock']},controls=controls,
        derivation='With adjacency matrices A and matching M, the off-diagonal change in (A+M)^2 is AM+MA because M^2 is diagonal. For two matched endpoints both cross terms vanish by independence of R. For exactly one matched endpoint the rows/count are the same as its single-edge extension; for no matched endpoint nothing changes. The changed adjacency cap occurs only on a matching edge and is covered by its single-edge hypothesis. These cases exhaust every distinct pair.',
        application_review='For a cap-admissible complete center star, known edges induced on its neighborhood have maximum degree one (otherwise a center-neighbor adjacent pair has at least two common neighbors). Removing all known-edge endpoints leaves an independent set. Thus the theorem applies to the residual matching in the existing filter whenever its separately checked individual-edge premises hold.',
        shared_components=['Python exact integers and standard library'],limitations=['The producer 21,504-star sample is not independently replayed by this report and is not a premise for this general proof.','No claim that different centers can choose their matchings consistently.','No degree completion, SRG construction, or exclusion is established.'])
    save(OUT/'matching_cap_lemma.json',cap)
    records=[];bindings={p:h(p) for p in [proof2,Path(__file__).relative_to(ROOT).as_posix(),'uv.lock']};first=None
    for path in sorted((ROOT/'acceleration/results/20260930_closed28_sos').glob('center_*.json')):
        key=path.relative_to(ROOT).as_posix();bindings[key]=h(key);blob=json.loads(path.read_bytes());assert len(blob['cases'])==32
        per=[]
        for case in blob['cases']:
            row,f,g=check_case(case);per.append(row)
            if first is None:first=(case,f,g)
        records.append(dict(path=key,cases=len(per),coefficients_checked=sum(r['coefficients_checked'] for r in per),max_remaining_degree=max(r['remaining_max_degree'] for r in per)))
    assert len(records)==84 and sum(r['cases'] for r in records)==2688
    case,f,g=first;bad=f.copy();bad[0,0]+=1;assert not np.array_equal(bad.T@bad,16*g)
    badg=g.copy();badg[0,0]+=1;assert not np.array_equal(f.T@f,16*badg)
    wrong=dict(case,centers_local=[0,1])
    try:check_case(wrong)
    except AssertionError:pass
    else:raise AssertionError('Adjacent centers corruption accepted')
    closed=dict(**common,status='INDEPENDENT_CLOSED_TWO_NEIGHBORHOOD_GRAM_REDUNDANCY_PASS',claim_id='C-CLOSED-TWO-NEIGHBORHOOD-GRAM-REDUNDANCY',
        statement='For every finite simple graph H on N[v] union N[u], where v and u are nonadjacent vertices of degree 14 and each center c satisfies |N(c) intersection N(x)|=2-adjacency(c,x) for every x distinct from c, the integer matrix 27I-9A(H)+J is positive semidefinite.',
        kind='mathematical result',basis=['DERIVED'],scope='A universal necessary-test redundancy theorem for two complete nonadjacent center neighborhoods satisfying the stated local equalities; no target existence conclusion.',dependencies=[],inputs_sha256=bindings,
        derivation='Deleting the two centers leaves R of size 26. Every vertex lies in at least one center neighborhood, so its degree in R is at most the sum of its two center-common-neighbor counts, hence at most 3. Both vectors 4e_c+1_N(c) are in the kernel of G by direct substitution. Their center-coordinate matrix is 4I, so subtracting kernel multiples eliminates any test vector at both centers. On R, 3I-A is the graph Laplacian plus diagonal 3-degree; therefore G_R is PSD. The written factor identity with z_i=4x_i-x_v*1_N(v)(i)-x_u*1_N(u)(i) explicitly gives 16*x^T*G*x as a sum of integer-weighted squares.',
        controls=dict(all_raw_matrices_rechecked=2688,all_matrix_coefficients_checked=2688*784,wrong_factor_rejected=True,wrong_gram_diagonal_rejected=True,adjacent_centers_rejected=True,integer_overflow_excluded_by_explicit_bound=True),records=records,
        shared_components=['NumPy int64 exact small matrix multiplication with explicit overflow bound','Python standard library and integer set intersections'],
        limitations=['Raw matrix hypotheses and every SOS coefficient were independently checked, not the producer floating eigenvalues.','Original domain-to-raw graph generation is not independently rerun here; this theorem is conditional on the displayed local graph hypotheses.','Fixture completeness is exactly the 84 saved files and 32 cases each, not all domain stars or matchings.','No assertion that adding more vertices or other constraints remains redundant.','No target graph, general exclusion, or external peer review.'])
    save(OUT/'closed_gram_lemma.json',closed)
    print(json.dumps(dict(cap_lemma_sha256=h((OUT/'matching_cap_lemma.json').relative_to(ROOT)),closed_lemma_sha256=h((OUT/'closed_gram_lemma.json').relative_to(ROOT)),raw_cases=2688,raw_coefficients=2688*784)))

if __name__=='__main__':main()
