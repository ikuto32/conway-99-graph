"""Independent exact block-identity checks; no producer imports or solver."""
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
import argparse
import copy
import hashlib
import json
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
B = 'acceleration/results/20260930_triangle_residual60/'


def h(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def read(path):
    return json.loads((ROOT/path).read_bytes())


def residual(a, k):
    n = len(a)
    assert all(len(r)==n and all(type(x) is int and x in (0,1) for x in r) for r in a)
    assert all(a[i][i]==0 and all(a[i][j]==a[j][i] for j in range(n)) for i in range(n))
    masks = [sum(v << i for i,v in enumerate(row)) for row in a]
    return [[(masks[i]&masks[j]).bit_count()+a[i][j]-2-(k-2)*int(i==j)
             for j in range(n)] for i in range(n)]


def block_fixture(raw):
    c,r,f,d = [raw[k] for k in ['C','R','F','D']]
    m,b = raw['m'],raw['b']
    s,n = 3*m,3+3*m+b
    a = [[0]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i<3 and j<3: a[i][j]=int(i!=j)
            elif i<3 and 3<=j<3+s: a[i][j]=r[j-3][i]
            elif j<3 and 3<=i<3+s: a[i][j]=r[i-3][j]
            elif 3<=i<3+s and 3<=j<3+s: a[i][j]=c[i-3][j-3]
            elif 3<=i<3+s and j>=3+s: a[i][j]=f[i-3][j-3-s]
            elif 3<=j<3+s and i>=3+s: a[i][j]=f[j-3][i-3-s]
            elif i>=3+s and j>=3+s: a[i][j]=d[i-3-s][j-3-s]
    assert a==raw['complete_adjacency']
    actual=residual(a,m+2)
    assert actual==raw['complete_residual']
    for i in range(n):
        for j in range(i,n):
            if i<3 and j<3: expected=0
            elif i<3 and j<3+s: expected=0
            elif i<3: expected=sum(r[x][i]*f[x][j-3-s] for x in range(s))-2
            elif j<3+s:
                x,z=i-3,j-3
                expected=sum(r[x][t]*r[z][t] for t in range(3))+sum(c[x][t]*c[z][t] for t in range(s))+sum(f[x][y]*f[z][y] for y in range(b))+c[x][z]-2-m*int(x==z)
            elif i<3+s:
                x,y=i-3,j-3-s
                expected=sum(c[x][z]*f[z][y] for z in range(s))+sum(f[x][z]*d[z][y] for z in range(b))+f[x][y]-2
            else:
                y,z=i-3-s,j-3-s
                expected=sum(f[x][y]*f[x][z] for x in range(s))+sum(d[y][w]*d[z][w] for w in range(b))+d[y][z]-2-m*int(y==z)
            assert actual[i][j]==expected, (i,j)
    return n*n


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);args=ap.parse_args()
    out=ROOT/args.out;assert not out.exists()
    producer=read(B+'summary.json')
    assert h(B+'summary.json')=='640f5d191e0e1ebdca9049595f9ab2d92b2e873466ecaa8d409032d5913440b3'
    inputs={B+'summary.json':h(B+'summary.json')}
    for path,value in producer['inputs_sha256'].items():
        assert h(path)==value;inputs[path]=value
    for path,value in producer['artifact_hashes'].items():
        assert h(path)==value;inputs[path]=value
    matrices=[];negatives=[]
    for m in [2,4,6,12]:
        raw=read(B+f'block_control_m{m:02d}.json')
        matrices.append(dict(cell_size=m,entries=block_fixture(raw)))
        bad=copy.deepcopy(raw);bad['complete_residual'][0][0]+=1
        try:block_fixture(bad)
        except AssertionError:negatives.append('altered residual '+str(m))
        else:raise AssertionError('corruption accepted')
    bad=copy.deepcopy(raw);bad['complete_adjacency'][0][1]=0
    try:block_fixture(bad)
    except AssertionError:negatives.append('altered adjacency assembly')
    else:raise AssertionError('assembly corruption accepted')
    rook=[[int(i!=j and (i//3==j//3 or i%3==j%3)) for j in range(9)] for i in range(9)]
    assert residual(rook,4)==[[0]*9 for _ in range(9)]
    bad=copy.deepcopy(rook);bad[0][1]=bad[1][0]=0
    assert any(x for row in residual(bad,4) for x in row)
    negatives.append('deleted known-valid rook edge')
    stars=read(B+'generic_star_controls.json');c,f=stars['core'],stars['F'];sd=stars['derived']
    s,b=len(c),len(f[0]);totals=[]
    overlaps=[[sum(f[x][y]*f[x][z] for x in range(s)) for z in range(b)] for y in range(b)]
    deficits=[[2-f[x][y]-sum(c[x][z]*f[z][y] for z in range(s)) for y in range(b)] for x in range(s)]
    allowed=[[z for z in range(b) if z!=y and overlaps[y][z]<=1 and all(f[x][z]<=deficits[x][y] and f[x][y]<=deficits[x][z] for x in range(s))] for y in range(b)]
    assert (overlaps,deficits,allowed)==(sd['column_overlaps'],sd['H'],sd['allowed_edges_by_vertex'])
    for item in stars['complete_star_subsets']:
        y,neighbors=item['center'],item['neighbors'];a=[[0]*(s+b) for _ in range(s+b)]
        for x in range(s):
            for z in range(s):a[x][z]=c[x][z]
            for z in range(b):a[x][s+z]=a[s+z][x]=f[x][z]
        for z in neighbors:a[s+y][s+z]=a[s+z][s+y]=1
        adj=[set(j for j,v in enumerate(row) if v) for row in a]
        valid=len(neighbors)==2 and y not in neighbors
        valid=valid and all(len(adj[i]&adj[j])+a[i][j]<=2 for i,j in combinations(range(s+b),2))
        valid=valid and all(len(adj[x]&adj[s+y])+a[x][s+y]==2 for x in range(s))
        assert valid==item['accepted'];totals.append(valid)
    assert len(totals)==12 and sum(totals)==3
    for path in [Path(__file__).relative_to(ROOT).as_posix(),'docs/AUDIT_20260930_TRIANGLE_RESIDUAL60.md']:
        inputs[path]=h(path)
    summary=dict(status='INDEPENDENT_TRIANGLE_RESIDUAL60_EQUIVALENCE_PASS',timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),
        verifier='/root independent written derivation and raw bitset control checker',
        claim_id=producer['claim_id'],claim_revision=1,statement=producer['statement'],kind=producer['kind'],basis=producer['basis'],
        scope=producer['scope'],recommendation='VERIFIED',review_state='CLEAR',dependencies=[],
        assumptions=['Exact triangle core with one C-neighbor in each of three12vertex cells.',
                     'F is binary36x60 and satisfies both stated factor equations.',
                     'D is symmetric binary zero-diagonal60x60.'],
        checks=dict(raw_block_matrices=matrices,known_valid_rook9=True,corruptions_rejected=negatives,
                    literal_small_star_cases=len(totals),small_star_positives=sum(totals)),
        inputs_sha256=inputs,shared_components=['Raw producer fixtures and Python exact integer arithmetic; no producer imports.'],
        limitations=producer['limitations']+['No complete SAT encoding or exhaustive star enumerator is certified by this theorem audit.',
                      'Producer screening API has only finite calibration here; any future claimed factor exclusion needs its own complete artifact audit.'],
        target_resolution=False,actual_target_factor_available=False)
    out.mkdir(parents=True,exist_ok=False)
    with (out/'summary.json').open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(summary,stream,indent=2);stream.write('\n')
    print(json.dumps(dict(status=summary['status'],summary_sha256=h((out/'summary.json').relative_to(ROOT).as_posix()))))


if __name__=='__main__':main()
