"""Candidate exact conditional triangle contraction, calibrated without F."""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'acceleration/results/20260930_independent_review/identity_p_triangle_partition/residual60_control.json'
PH='af1b48620c36a377a993cc18c55ac80a9fdc9ce35ce1b6000a8f232201c6f532'
GATE=ROOT/'acceleration/results/20260930_independent_review/identity_p_triangle_partition/summary.json'
GH='15a32c8e4fb4928f78a6e931e09054ddcfd90c027717e8c0d0828c6f5406a516'

def need(ok,why):
    if not ok:raise ValueError(why)
def digest(p):return sha256(p.read_bytes()).hexdigest()
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')

def contract(d,triangles):
    need(len(d)==60 and all(len(row)==60 and all(type(v)is int and v in(0,1) for v in row) for row in d),'binary60matrix')
    need(all(d[i][i]==0 and sum(d[i])==8 and all(d[i][j]==d[j][i] for j in range(60)) for i in range(60)),'simple symmetric degree8')
    need(len(triangles)==20 and all(len(t)==3 for t in triangles) and sorted(v for t in triangles for v in t)==list(range(60)),'triangle vertex partition')
    owner={v:q for q,t in enumerate(triangles) for v in t}
    need(all(d[i][j]==1 for t in triangles for i in t for j in t if i!=j),'actual triangles')
    r=[[int(owner[v]==q) for q in range(20)] for v in range(60)]
    dr=[[sum(d[v][u] for u in triangles[q]) for q in range(20)] for v in range(60)]
    w=[[dr[v][q]-2*r[v][q] for q in range(20)] for v in range(60)]
    need(all(x in(0,1) for row in w for x in row),'at most one neighbor in any other triangle')
    need(all(sum(row)==6 for row in w) and all(sum(w[v][q] for v in range(60))==18 for q in range(20)),'W margins')
    b=[[sum(w[v][q] for v in triangles[p]) for q in range(20)] for p in range(20)]
    need(all(b[p][p]==0 and sum(b[p])==18 and all(0<=b[p][q]<=3 and b[p][q]==b[q][p] for q in range(20)) for p in range(20)),'B weighteddegree and symmetry')
    wt=[[sum(w[v][p]*w[v][q] for v in range(60)) for q in range(20)] for p in range(20)]
    # LiteralD^2+D first, thensum blocks; separatefromDR factorization.
    ds=[[sum(d[i][k]*d[k][j] for k in range(60))+d[i][j] for j in range(60)] for i in range(60)]
    direct=[[sum(ds[i][j] for i in triangles[p] for j in triangles[q]) for q in range(20)] for p in range(20)]
    expanded=[[18*int(p==q)+5*b[p][q]+wt[p][q] for q in range(20)] for p in range(20)]
    need(direct==expanded,'all400 literal contraction entries')
    return dict(R=r,W=w,B=b,WtW=wt,literal_contracted_D2_plus_D=direct)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    need(digest(P)==PH and digest(GATE)==GH,'frozen independent positive and premise')
    raw=json.loads(P.read_bytes());result=contract(raw['D'],raw['triangles']);bad_records=[]
    mutations=[]
    loop=[r[:] for r in raw['D']];loop[0][0]=1;mutations.append(('loop',loop,raw['triangles']))
    badtri=json.loads(json.dumps(raw['triangles']));badtri[0][0]=badtri[1][0];mutations.append(('duplicate_partition_vertex',raw['D'],badtri))
    # Preserve degree/symmetry by an intertriangle switch which produces two
    # neighbors into one triangle for vertex0; find an exact such switch.
    d=raw['D'];owner={v:q for q,t in enumerate(raw['triangles']) for v in t};switched=None
    for a in range(60):
        if owner[a]==owner[0] or not d[0][a]:continue
        for b in range(60):
            if b==0 or d[0][b] or owner[b] in(owner[0],owner[a]):continue
            if not any(d[0][v] for v in raw['triangles'][owner[b]]):continue
            for c in range(60):
                if len({0,a,b,c})<4 or not d[b][c] or d[a][c] or owner[c] in(owner[a],owner[b]):continue
                switched=[row[:] for row in d]
                for i,j,value in [(0,a,0),(b,c,0),(0,b,1),(a,c,1)]:switched[i][j]=switched[j][i]=value
                break
            if switched is not None:break
        if switched is not None:break
    need(switched is not None,'construct degree-preserving double-triangle-neighbor corruption')
    mutations.append(('two_neighbors_in_one_triangle',switched,raw['triangles']))
    for name,matrix,triangles in mutations:
        try:contract(matrix,triangles)
        except ValueError as e:bad_records.append(dict(name=name,rejected=True,reason=str(e)))
        else:raise AssertionError('corrupt structural fixture accepted')
    wrong=[[18*int(p==q)+4*result['B'][p][q]+result['WtW'][p][q] for q in range(20)] for p in range(20)]
    need(wrong!=result['literal_contracted_D2_plus_D'],'wrong coefficient4 rejected')
    bad_records.append(dict(name='coefficient4_instead_of5',rejected=True))
    save(out/'raw_contraction.json',result);save(out/'controls.json',dict(corruptions=bad_records,raw_positive_scope=raw['label']))
    inputs={key(P):PH,key(GATE):GH}
    for p in [Path(__file__),Path(__file__).with_name('theory_20260930_triangle_contraction_spec.md'),ROOT/'docs/DERIVATION_20260930_TRIANGLE_CONTRACTION.md',ROOT/'uv.lock',ROOT/'pyproject.toml']:inputs[key(p)]=digest(p)
    need(time.monotonic()-start<30,'30second cap')
    summary=dict(status='CANDIDATE_CONDITIONAL_RESIDUAL_TRIANGLE_CONTRACTION',timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),
        versions=dict(python=platform.python_version(),uv=subprocess.check_output(['uv','--version'],text=True).strip()),
        inputs_sha256=inputs,outputs_sha256={key(p):digest(p) for p in out.iterdir() if p.is_file()},
        literal_contraction_entries_checked=400,corrupted_controls=len(bad_records),research_factor=None,
        research_factor_reason='The residual fixture is not an SRG99/factor; target implications are written conditional derivations.',
        solver_calls=0,independent_approval=False,target_resolution='UNKNOWN',wall_seconds=time.monotonic()-start,
        limitations=['ActualD triangle partition required.','Cycliccoarsecover not asserted to be actualDpartition.','No search or exclusion.','No novelty claim.'])
    save(out/'summary.json',summary);print(json.dumps(dict(status=summary['status'],summary_sha256=digest(out/'summary.json'))))

if __name__=='__main__':main()
