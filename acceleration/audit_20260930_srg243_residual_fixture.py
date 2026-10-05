"""Independent literal integer-dot-product audit of the non-target243 fixture."""
import argparse
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'acceleration/results/20260930_srg243_residual_fixture'
SUMMARY_SHA='cb338497d16b3e79c523d4ac5e749aa7b7f00d68a8873a5edcd8b488bfa64395'
def need(ok,message):
    if not ok:raise ValueError(message)
def digest(p):return sha256(Path(p).read_bytes()).hexdigest()
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def save(p,x):
    with Path(p).open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
def read(p):return json.loads(Path(p).read_bytes())

def exact_graph(a,n,k):
    need(len(a)==n and all(len(row)==n and all(type(x) is int and x in (0,1) for x in row) for row in a),'literal binary graph dimensions')
    need(all(a[i][i]==0 and sum(a[i])==k for i in range(n)) and all(a[i][j]==a[j][i] for i,j in combinations(range(n),2)),'simple symmetric regular graph')
    for i in range(n):
        for j in range(n):need(sum(x*y for x,y in zip(a[i],a[j]))==(k-2)*int(i==j)-a[i][j]+2,'exact integer identity '+str((i,j)))
    return dict(vertices=n,degree=k,integer_square_entries=n*n,arithmetic='Literal Python integer dot products, no producer bitset code')

def check_blocks(a,b):
    t=b['original_triangle'];fibres=b['original_fibres'];outside=b['original_outside_vertices'];order=t+sum(fibres,[])+outside
    need(len(t)==3 and [len(f) for f in fibres]==[20]*3 and len(outside)==180 and sorted(order)==list(range(243)) and b['canonical_order_original_vertex_ids']==order,'complete raw vertex relabelling')
    need(all(a[i][j] for i,j in combinations(t,2)),'root triangle')
    need(all(set(fibres[g])=={v for v in range(243) if v not in t and a[t[g]][v]} for g in range(3)),'all three raw neighbour fibres')
    h=[[a[i][j] for j in order[:63]] for i in order[:63]];c=[row[3:] for row in h[3:]]
    f=[[a[i][j] for j in outside] for i in order[3:63]];d=[[a[i][j] for j in outside] for i in outside]
    need(b['core_adjacency63']==h and b['cubic_core60']==c and b['factor60x180']==f and b['residual180x180']==d,'every raw block entry and orientation')
    labels=[list(pair) for pair in combinations(range(20),2) if pair[1]!=(pair[0]^1)]
    need(b['canonical_C0_pairs']==labels and f[:20]==[[int(r in pair) for pair in labels] for r in range(20)],'canonical180outside pair labels')
    qs=[]
    for g in range(3):
        q=[]
        for r in range(20):
            hits=[s for s in range(20) if c[20*g+r][20*g+s]];need(len(hits)==1,'internal matching');q.append(hits[0])
        qs.append(q)
    need(b['internal_matchings']==qs and qs[0]==[r^1 for r in range(20)],'all internal matching maps')
    for g in [1,2]:need(all(c[r][20*g+s]==int(r==s) for r in range(20) for s in range(20)),'normalized identity crossmatching')
    perm=[]
    for r in range(20):
        hits=[s for s in range(20) if c[20+r][40+s]];need(len(hits)==1,'cross12matching');perm.append(hits[0])
    need(b['cross01']==b['cross02']==list(range(20)) and b['cross12']==perm,'all cross maps')
    need(all(sum(row)==18 for row in f) and all(sum(f[20*g+r][j] for r in range(20))==2 for g in range(3) for j in range(180)),'factor row and fibre margins')
    need(all(sum(row)==16 for row in d),'nonempty residual degree16')
    for r in range(60):
        for s in range(60):need(sum(x*y for x,y in zip(f[r],f[s]))==20*int(r==s)-c[r][s]+2-sum(x*y for x,y in zip(h[3+r],h[3+s])),'all3600factor Gram entries')
        for j in range(180):need(sum(f[r][z]*d[z][j] for z in range(180))==2-f[r][j]-sum(c[r][s]*f[s][j] for s in range(60)),'all10800mixed residual entries')
    for i in range(180):
        for j in range(180):need(sum(x*y for x,y in zip(d[i],d[j]))+sum(f[r][i]*f[r][j] for r in range(60))==20*int(i==j)-d[i][j]+2,'all32400residual quadratic entries')
    need(b['target99_graph'] is False,'non-target positive-control scope')
    return dict(factor_shape=[60,180],residual_shape=[180,180],factor_Gram_entries=3600,mixed_entries=10800,residual_square_entries=32400,factor_row_margin=18,residual_degree=16)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();bindings={}
    def bind(p,expected=None):
        p=Path(p);h=digest(p);need(expected is None or h==expected,'hash '+str(p));bindings[key(p)]=h;return p
    try:
        summary=read(bind(D/'summary.json',SUMMARY_SHA));manifest=read(bind(D/'manifest.json'))
        for p,h in {**manifest['inputs_sha256'],**summary['artifact_hashes']}.items():bind(ROOT/p,h)
        raw=read(D/'adjacency243.json');blocks=read(D/'triangle_blocks.json');a=raw['adjacency']
        need(raw['parameters']==dict(v=243,k=22,lambda_value=1,mu=2),'actual fixture parameters')
        exact=exact_graph(a,243,22);block_result=check_blocks(a,blocks);rejected=[]
        def reject(name,fn,required=None):
            try:fn()
            except ValueError as error:
                need(required is None or required in str(error),'corruption reaches intended checking path');rejected.append(dict(control=name,error=str(error)))
            else:raise ValueError('corruption accepted '+name)
        rook=[[int(i!=j and (i//3==j//3 or i%3==j%3)) for j in range(9)] for i in range(9)];positive=exact_graph(rook,9,4)
        bad=deepcopy(a);bad[0][1]=bad[1][0]=0;reject('deleted_fixture_edge',lambda:exact_graph(bad,243,22))
        bad=deepcopy(a);bad[0][0]=False;reject('Boolean_diagonal',lambda:exact_graph(bad,243,22))
        switch=None
        for x,y in combinations(range(243),2):
            if not a[x][y]:continue
            for z,w in combinations(range(243),2):
                if len({x,y,z,w})==4 and a[z][w] and not a[x][z] and not a[y][w]:switch=(x,y,z,w);break
            if switch:break
        need(switch is not None,'degree-preserving corruption exists');x,y,z,w=switch;bad=deepcopy(a)
        for i,j,v in [(x,y,0),(z,w,0),(x,z,1),(y,w,1)]:bad[i][j]=bad[j][i]=v
        need(all(sum(row)==22 for row in bad),'corruption preserves degrees');reject('degree_preserving_switch',lambda:exact_graph(bad,243,22),'exact integer identity')
        for name in ['factor_bit','residual_bit','vertex_map','cross_map']:
            bad=deepcopy(blocks)
            if name=='factor_bit':bad['factor60x180'][0][0]^=1
            elif name=='residual_bit':bad['residual180x180'][0][1]^=1
            elif name=='vertex_map':bad['canonical_order_original_vertex_ids'][0]=bad['canonical_order_original_vertex_ids'][1]
            else:bad['cross12'][0]=(bad['cross12'][0]+1)%20
            reject(name,lambda:check_blocks(a,bad))
        bind(__file__);need(all(digest(ROOT/p)==h for p,h in bindings.items()),'stable raw inputs')
        report=dict(status='INDEPENDENT_SRG243_NONEMPTY_RESIDUAL_FIXTURE_PASS',claim_id='C-SRG243-NONEMPTY-RESIDUAL-POSITIVE-CONTROL',claim_revision=1,timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,
          verifier='/root/eight_domain_audit independent literal graph/block integer checker',recommendation='VERIFIED',review_state='CLEAR',kind='construction',basis=['COMPUTED'],
          statement='The exact saved243vertex matrix is a symmetric binaryzero-diagonal SRG(243,22,1,2), and its saved triangle extraction gives the exact60x180 incidence factor and180x180 residual graph of degree16 satisfying the coefficient20 block identities.',
          scope='A nonempty positive verification fixture of a different known parameter family; not Conway99 evidence.',dependencies=[],checks=dict(full_graph=exact,blocks=block_result,known_rook9=positive,corruptions_rejected=rejected,degree_preserving_switch=switch),producer_imports=False,
          limitations=['No99vertex factor or graph is provided.','Polynomial selection, syndrome census, code construction theory and novelty are not approved by this raw-artifact check.','The factor has60rows180columns and residual degree16, not36rows60columns anddegree8.'],target_resolution=False,external_review=False,artifact_availability='LOCAL_ONLY',elapsed_seconds=time.monotonic()-start)
        save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))
    except BaseException as error:save(args.out/'failure.json',dict(status='AUDIT_FAILED',error=repr(error)));raise

if __name__=='__main__':main()
