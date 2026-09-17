"""Independent derivation binding and exact rook9 artifact controls."""
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
from itertools import combinations,permutations
import json
from pathlib import Path
import platform
import sys

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'acceleration/results/20260917_root_scaffold'
def require(ok,msg):
    if not ok:raise ValueError(msg)
def digest(p):return sha256(Path(p).read_bytes()).hexdigest()
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def validate(a):
    require(len(a)==9 and all(len(r)==9 for r in a),'matrix size')
    require(all(type(v)is int and v in (0,1)for row in a for v in row),'binary integer')
    require(all(a[i][i]==0 for i in range(9)),'diagonal')
    require(all(a[i][j]==a[j][i]for i in range(9)for j in range(9)),'symmetry')
    n=[{j for j in range(9)if a[i][j]}for i in range(9)]
    require(all(len(s)==4 for s in n),'degree4')
    require(all(len(n[i]&n[j])==2-a[i][j]for i,j in combinations(range(9),2)),'exact common-neighbor equation')
    return n
def normalize(n,r,inner):
    require(set(inner)==n[r] and len(set(inner))==4,'inner inventory')
    require(inner[1]in n[inner[0]] and inner[3]in n[inner[2]],'ordered matching')
    outer=[]
    for i,j in ((0,2),(0,3),(1,2),(1,3)):
        outside=(n[inner[i]]&n[inner[j]])-{r}
        require(len(outside)==1,'unique outside neighbor');outer.append(next(iter(outside)))
    result=[r]+list(inner)+outer;require(len(set(result))==9,'full bijection')
    return result
def checkmap(n,m):
    require(len(m)==len(set(m))==9 and set(m)==set(range(9)),'label permutation')
    require(m==normalize(n,m[0],m[1:5]),'outside label mismatch')

def main():
    out=ROOT/'acceleration/results/20260917_independent_review/root_scaffold.json';require(not out.exists(),'preserve evidence');bindings={}
    def read(p):
        bindings[key(p)]=digest(p);d=json.loads(Path(p).read_bytes())
        for f,h in d.get('inputs_sha256',{}).items():require(digest(ROOT/f)==h,'input changed');bindings[f]=h
        return d
    for p in (__file__,ROOT/'acceleration/results/20260917_independent_review/ROOT_SCAFFOLD_DERIVATION.md',ROOT/'uv.lock'):bindings[key(p)]=digest(p)
    manifest=read(D/'manifest.json');summary=read(D/'summary.json');fixture=read(D/'rook9_adjacency.json')
    require(summary['manifest_sha256']==digest(D/'manifest.json') and summary['fixture_sha256']==digest(D/'rook9_adjacency.json'),'raw evidence identity')
    a=fixture['adjacency'];n=validate(a)
    coords=[(i,j)for i in range(3)for j in range(3)]
    require(a==[[int(u!=v and (u[0]==v[0]or u[1]==v[1]))for v in coords]for u in coords],'independently constructed rook9')
    expected=set()
    for r in range(9):
        for inner in permutations(sorted(n[r])):
            if inner[1]in n[inner[0]] and inner[3]in n[inner[2]]:expected.add(tuple(normalize(n,r,inner)))
    actual=set()
    for row in summary['records']:
        m=row['new_to_old_vertices'];checkmap(n,m);require(m[0]==row['root'] and row['result']=='PASS','map root/status')
        require(row['outside_root_symbol_labels']==[[0,2],[0,3],[1,2],[1,3]],'pair order')
        scaff={(0,i)for i in range(1,5)}|{(1,2),(3,4)}|{(s+1,v)for v,p in enumerate(((0,2),(0,3),(1,2),(1,3)),5)for s in p}
        require(sorted(map(list,scaff))==row['scaffold_edges'] and len(scaff)==row['scaffold_edge_count']==14 and all(m[v]in n[m[u]]for u,v in scaff),'scaffold edge identity')
        actual.add(tuple(m))
    require(len(summary['records'])==len(actual)==len(expected)==72 and actual==expected,'all72 labelings, no missing/duplicate')
    controls=[]
    for i,j in combinations(range(9),2):
        b=deepcopy(a);b[i][j]=b[j][i]=1-b[i][j]
        try:validate(b)
        except ValueError as e:controls.append(dict(kind='toggle',pair=[i,j],outcome='REJECT',reason=str(e)))
        else:raise ValueError('edge toggle accepted')
    b=deepcopy(a);b[0][1]=0;c=deepcopy(a);c[0][0]=1;d=deepcopy(a);d[0][1]=d[1][0]=2;e=deepcopy(a)
    for i,j in ((0,1),(3,4),(0,4),(1,3)):e[i][j]=e[j][i]=1-e[i][j]
    require(all(sum(row)==4 for row in e),'switched fixture preserves degree')
    for name,bad in [('asymmetric',b),('loop',c),('nonbinary',d),('degree_preserving_switch',e)]:
        try:validate(bad)
        except ValueError as err:controls.append(dict(kind=name,outcome='REJECT',reason=str(err)))
        else:raise ValueError('corrupt matrix accepted')
    for name in ('duplicate_image','wrong_pair'):
        m=list(min(expected))
        if name=='duplicate_image':m[-1]=m[-2]
        else:m[5],m[6]=m[6],m[5]
        try:checkmap(n,m)
        except ValueError as err:controls.append(dict(kind=name,outcome='REJECT',reason=str(err)))
        else:raise ValueError('corrupt map accepted')
    require(all(digest(ROOT/f)==h for f,h in bindings.items()),'bound inputs changed')
    report=dict(status='INDEPENDENT_ROOT_SCAFFOLD_DERIVATION_AND_CALIBRATION_PASS',claim_id='C-ROOT-SCAFFOLD-NORMALIZATION',claim_revision=1,
        timestamp=datetime.now(timezone.utc).isoformat(),source_commit=manifest['source_commit'],command=[sys.executable]+sys.argv,working_directory=str(Path.cwd()),python=platform.python_version(),
        inputs_sha256=bindings,statement='Every target matrix, every root, and every ordered/oriented neighborhood matching has the unique84outside-pair labeling and189positive scaffold; no outer-edge/nonedge restriction or automorphism assumption.',
        mathematical_check='Independent written derivation ROOT_SCAFFOLD_DERIVATION.md establishes universal implication directly from exact degree/common-neighbor equations',
        calibration=dict(fixture='rook9',roots=9,full_maps=72,positive_controls=1,corrupted_controls=42,controls=controls),
        calibration_is_general_proof=False,producer_imported=False,shared_trusted_components=['Python standard library'],recommendation='VERIFIED',
        limitations=['Conditional representation theorem, not existence/nonexistence','No novelty or literature-priority assertion','No outer adjacency restriction follows from normalization alone'],target_resolution='UNKNOWN')
    out.open('x',encoding='utf8').write(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status=report['status'],sha256=digest(out))))

if __name__=='__main__':main()
