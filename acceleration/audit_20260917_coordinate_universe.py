"""Independent inclusion-exclusion coverage and dense integer partial-cap audit."""
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations
import json
from math import comb, prod
from pathlib import Path
import platform
import subprocess
import sys
import time
import numpy as np
from tqdm import tqdm

BASE=Path('acceleration/results/20260917_partial_coordinate_matchings')
PARTIAL=Path('acceleration/results/20260917_partial_matching/manifest.json')


def digest(p):return sha256(Path(p).read_bytes()).hexdigest()


def universe_check(records,vertices,allowed,expected):
    assert len(records)==expected
    seen=set()
    for i,r in enumerate(records):
        assert r['matching_id']==i
        edges=tuple(tuple(e) for e in r['edges_outer'])
        assert len(edges)==6 and tuple(sorted(edges))==edges
        assert all(a<b and (a,b) in allowed for a,b in edges)
        assert Counter(x for e in edges for x in e)==Counter(vertices)
        assert edges not in seen
        seen.add(edges)
    return True


def partial_check(a,degree=14):
    if a.ndim!=2 or a.shape[0]!=a.shape[1]:return False
    if not np.array_equal(a,a.T) or np.any(np.diag(a)) or not np.all((a==0)|(a==1)):return False
    if np.max(np.sum(a,axis=1))>degree:return False
    common=a@a;off=~np.eye(len(a),dtype=bool)
    return bool(np.all(common[off]<=(2-a)[off]))


def main():
    out=Path('acceleration/results/20260917_independent_review/coordinate_universe.json')
    assert not out.exists()
    paths=[BASE/x for x in ('manifest.json','matchings.json','outcomes.json','summary.json')]+[PARTIAL,Path(__file__),Path('uv.lock')]
    hashes={p.as_posix():digest(p) for p in paths}
    manifest,raw,outcomes,summary=[json.loads((BASE/x).read_bytes()) for x in ('manifest.json','matchings.json','outcomes.json','summary.json')]
    p=json.loads(PARTIAL.read_bytes())
    for name,h in manifest['inputs_sha256'].items():assert digest(name)==h
    vertices=manifest['coordinate_vertices_outer'];allowed={tuple(e) for e in manifest['allowed_matching_edges_outer']}
    assert vertices==sorted(u for u in range(84) if u in p['affected_outer_vertices'])
    assert allowed=={tuple(e) for e in p['freed_legal_matching_edges_outer']}
    forbidden=set(combinations(vertices,2))-allowed
    assert len(vertices)==12 and len(allowed)==60 and len(forbidden)==6
    assert Counter(x for e in forbidden for x in e)==Counter(vertices)
    terms=[(-1)**k*comb(6,k)*prod(range(1,12-2*k,2)) for k in range(7)]
    expected=sum(terms)
    assert terms==[10395,-5670,1575,-300,45,-6,1] and expected==6040
    assert raw['complete'] and raw['vertices_outer']==vertices
    assert universe_check(raw['records'],vertices,allowed,expected)
    controls=[]
    for name,records in [('missing_matching',raw['records'][:-1]),('duplicated_matching',raw['records'][:-1]+[raw['records'][0]])]:
        try:universe_check(records,vertices,allowed,expected)
        except AssertionError:controls.append(dict(name=name,outcome='REJECT'))
        else:raise AssertionError('Failed corruption control')
    rook=np.array([[int(i!=j and (i//3==j//3 or i%3==j%3)) for j in range(9)] for i in range(9)],dtype=np.int64)
    assert partial_check(rook,4)
    bad=rook.copy();bad[0,1]=0;assert not partial_check(bad,4)
    bad=rook.copy();bad[0,0]=1;assert not partial_check(bad,4)
    bad=rook.copy();bad[0,4]=bad[4,0]=1;assert not partial_check(bad,4)
    controls.extend([dict(name='rook9_own_parameters',outcome='PASS'),dict(name='asymmetric_corruption',outcome='REJECT'),dict(name='loop_corruption',outcome='REJECT'),dict(name='extra_edge_corruption',outcome='REJECT')])
    labels=[(2*g+s,2*h+t) for g in range(7) for h in range(g+1,7) for s in (0,1) for t in (0,1)]
    a=np.zeros((99,99),dtype=np.int64)
    def add(u,v):a[u,v]=a[v,u]=1
    for u in range(1,15):add(0,u)
    for u in range(1,15,2):add(u,u+1)
    for u,pair in enumerate(labels,15):
        for s in pair:add(u,s+1)
    assert int(a.sum())==378
    for u,v in p['remaining_fixed_K_edges_outer']:add(u+15,v+15)
    assert int(a.sum())==702 and partial_check(a)
    started=time.monotonic();accepted=[];rejected=[]
    for r,observed in tqdm(list(zip(raw['records'],outcomes['records'],strict=True)),desc='Independent dense integer caps',unit='matching'):
        matrix=a.copy()
        for u,v in r['edges_outer']:matrix[u+15,v+15]=matrix[v+15,u+15]=1
        verdict=partial_check(matrix)
        assert observed['matching_id']==r['matching_id'] and observed['accepted']==verdict
        (accepted if verdict else rejected).append(r['matching_id'])
    assert accepted==summary['accepted_matching_ids'] and rejected==summary['rejected_matching_ids']
    report=dict(status='INDEPENDENT_PARTIAL_COORDINATE_MATCHING_UNIVERSE_PASS',timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(Path.cwd()),
        python=platform.python_version(),numpy=np.__version__,inputs_sha256=hashes,
        claim_id='C-PARTIAL-K-COORDINATE-MATCHING-UNIVERSE',claim_revision=1,recommendation='VERIFIED',
        statement='The frozen one-coordinate allowed matching graph has exactly6040 labeled perfect matchings. The supplied list is complete and duplicate-free; all6040 added to the fixed162-edge partial scaffold satisfy degree<=14 and all pair upper caps common(u,v)<=2-A_uv.',
        inclusion_exclusion_terms=terms,matching_count=expected,accepted_partial_cap_assignments=len(accepted),rejected_partial_cap_assignments=len(rejected),
        controls=controls,method='Independent inclusion-exclusion over six disjoint forbidden edges; every listed matching checked legal and unique. Equal exact cardinality proves list coverage. Separate dense NumPy int64 A@A checks each99vertex partial adjacency matrix.',
        mathematical_scope='The12vertices/60allowededges and162fixedK edges in the frozen manifest only; no symmetry quotient.',
        count_does_not_describe_graphs_or_target_coverage=True,producer_imported=False,shared_components=['Python standard library','NumPy integer matrix multiplication','tqdm'],
        limitations=['Passing upper caps does not imply a completion or a target graph.','6040 is a count of labeled coordinate assignments, not graphs; no target-wide fraction is claimed.','No overlap union with earlier excluded fixed configurations is asserted.'],elapsed_seconds=time.monotonic()-started)
    with out.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps({k:report[k] for k in ('status','matching_count','accepted_partial_cap_assignments','elapsed_seconds')}))


if __name__=='__main__':main()
