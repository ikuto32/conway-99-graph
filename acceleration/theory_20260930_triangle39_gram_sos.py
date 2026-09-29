"""Candidate exact universal39-core Gram SOS; producer, not its verifier.

The symbolic proof is in docs/DERIVATION_20260930_TRIANGLE39_GRAM_SOS.md.
Finite integer matrix checks here calibrate it; samples do not prove a
universal statement, and no self-promotion is performed.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime,timezone
from hashlib import sha256
from itertools import combinations
from math import gcd
from pathlib import Path
import json
import platform
import random
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
PIN='85e705cc6c2a14d123120c93a847e30aaab1789e'
ARCHIVE='https://github.com/YesterdaysLemon/conway-99-research'
def need(ok,msg):
    if not ok:raise ValueError(msg)
def h(p):return sha256(Path(p).read_bytes()).hexdigest()
def save(p,data):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(data,f,indent=2);f.write('\n')
def matching(m):return len(m)==12 and sorted(m)==list(range(12))and all(m[i]!=i and m[m[i]]==i for i in range(12))
def core(ms,p):
    need(len(ms)==3 and all(matching(m)for m in ms),'three perfect matchings')
    need(len(p)==12 and sorted(p)==list(range(12)),'permutation P')
    a=[[0]*39 for _ in range(39)]
    def edge(x,y):need(x!=y,'no loop');a[x][y]=a[y][x]=1
    for x,y in combinations(range(3),2):edge(x,y)
    for i in range(3):
        for j in range(12):edge(i,3+12*i+j);edge(3+12*i+j,3+12*i+ms[i][j])
    for j in range(12):edge(3+j,15+j);edge(3+j,27+j);edge(15+j,27+p[j])
    need([sum(r)for r in a]==[14]*3+[4]*36,'core degrees')
    b=[r[3:]for r in a[3:]]
    need(all(sum(r)==3 for r in b),'inner cubic')
    for i in range(3):
        for j in range(3):need(all(sum(b[x][12*j:12*j+12])==1 for x in range(12*i,12*i+12)),'all blocks permutation')
    return a,b
def components(b):
    unseen=set(range(len(b)));out=[]
    while unseen:
        found={min(unseen)};stack=list(found)
        while stack:
            u=stack.pop()
            for v,e in enumerate(b[u]):
                if e and v not in found:found.add(v);stack.append(v)
        unseen-=found;out.append(sorted(found))
    return out
def rank(a):
    # Integer row operations with exact gcd rescaling: rank over Q, not mod p.
    a=[r[:]for r in a];r=0
    for c in range(len(a[0])):
        pivot=next((i for i in range(r,len(a))if a[i][c]),None)
        if pivot is None:continue
        a[r],a[pivot]=a[pivot],a[r];q=a[r][c]
        for i in range(r+1,len(a)):
            v=a[i][c]
            if not v:continue
            a[i]=[q*x-v*y for x,y in zip(a[i],a[r])]
            d=0
            for x in a[i]:d=gcd(d,abs(x))
            if d:a[i]=[x//d for x in a[i]]
        r+=1
        if r==len(a):break
    return r
def vec(n,index=None,weight=1):return [weight if i==index else 0 for i in range(n)]
def linear(*terms):return [sum(c*v[i]for c,v in terms)for i in range(len(terms[0][1]))]
def outer_sum(n,forms):
    result=[[0]*n for _ in range(n)]
    for weight,v in forms:
        nz=[i for i,x in enumerate(v)if x]
        for i in nz:
            for j in nz:result[i][j]+=weight*v[i]*v[j]
    return result
def annihilates(a,v):return all(sum(x*y for x,y in zip(row,v))==0 for row in a)
def gram(a,kind):
    return [[(27*int(i==j)-9*a[i][j]+1)if kind=='G'else a[i][j]+4*int(i==j)for j in range(39)]for i in range(39)]
def sos39(a,b):
    # b_i=S_i/12, z_x=Z_x/12. Multiply identities by144 to avoid fractions.
    S=[[int(3+12*i<=j<3+12*(i+1))for j in range(39)]for i in range(3)]
    total=linear(*[(1,s)for s in S]);R=[int(i<3)for i in range(39)]
    Z=[linear((12,vec(39,3+j)),(-1,S[j//12]))for j in range(36)]
    edges=[(i,j)for i,j in combinations(range(36),2)if b[i][j]]
    qforms=[(1,z)for z in Z]+[(1,linear((1,Z[i]),(1,Z[j])))for i,j in edges]
    qforms +=[(3,linear((12,vec(39,i)),(4,S[i])))for i in range(3)]
    qforms +=[(1,linear((12,R))),(12,total)]
    gforms=[(9,linear((1,Z[i]),(-1,Z[j])))for i,j in edges]
    gforms +=[(36,linear((12,vec(39,i)),(-4,R),(-3,S[i]),(1,total)))for i in range(3)]
    gforms +=[(4,linear((12,R),(-6,total)))]
    G,Q=gram(a,'G'),gram(a,'Q')
    need(outer_sum(39,gforms)==[[144*x for x in row]for row in G],'G exact coefficient identity')
    need(outer_sum(39,qforms)==[[144*x for x in row]for row in Q],'Q exact coefficient identity')
    return G,Q,gforms,qforms
def kernel_bases(comps):
    q=[];g=[]
    for j in [0,1]:
        b=[int(i==j)-int(i==2)for i in range(3)]
        q.append([-4*x for x in b]+[b[i//12]for i in range(36)])
    for i in range(3):g.append([4 if j==i else 1 for j in range(3)]+[int(j//12==i)for j in range(36)])
    reference=set(comps[-1]);ref_units=len(reference)//3
    for c in comps[:-1]:
        this=set(c);units=len(this)//3
        g.append([0]*3+[ref_units*int(j in this)-units*int(j in reference)for j in range(36)])
    return g,q
def archive_overlap():
    specs=[('verification/wave36-block-compatibility/audit.md','sections1 and3; Gram identity and component balance','C-WAVE36-BLOCK-COMPATIBILITY-064'),
           ('verification/wave38-higher-order/audit.md','section4; factor(3I-A_X)(4I+A_X) on zero fiber-sum space for a connected control','C-WAVE38-HIGHER-ORDER-074'),
           ('attempts/wave40-exact-coupling-model/README.md','section5; cubic-core and39-space decomposition over F7',None),
           ('verification/wave41-allquotient-lifts/audit.md','section4; F7 decomposition, not a real PSD identity','C-WAVE40-CORE-LAPLACIAN-084'),
           ('attempts/wave58-cross-incidence-rank/derivation.md','section2; factor-Gram kernel dimensionkappa+1 and rank35-kappa; explicitly prior Wave36 content','C-WAVE58-CROSS-INCIDENCE-001')]
    records=[]
    for path,section,claim in specs:
        cmd=['git','-C','external_conway99_research','show',PIN+':'+path]
        raw=subprocess.check_output(cmd,cwd=ROOT)
        need(raw==(ROOT/'external_conway99_research'/path).read_bytes(),'archive immutable exact bytes')
        records.append(dict(repository=ARCHIVE,commit=PIN,path=path,sha256=sha256(raw).hexdigest(),section=section,
                            original_claim_id=claim,original_claim_id_null_reason=None if claim else 'This cited prose is not bound here to a unique archived claim statement.',
                            command=cmd,access_timestamp=datetime.now(timezone.utc).isoformat()))
    return dict(status='IMMUTABLE_SOURCE_OVERLAP_RECORDED',sources=records,
                coverage='Targeted inspection of the five named sections; not a complete archive or literature novelty search.',
                finding='The36factor-Gram factorization and exact rank/kernel argument already occur in the pinned archive. The39-dimensional fiber/Laplacian decomposition also appears in prior F7 work. No novelty claim.',
                historical_verified_labels_reused_as_fresh_review=False,
                mathematical_note='The present exact39 SOS is a candidate reusable real-field restatement; the theorem is not promoted by this producer.')
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);args=parser.parse_args()
    out=ROOT/args.out;out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    inputs={p:h(ROOT/p)for p in [Path(__file__).relative_to(ROOT).as_posix(),'docs/DERIVATION_20260930_TRIANGLE39_GRAM_SOS.md','uv.lock','pyproject.toml']}
    save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
         command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),inputs_sha256=inputs,
         question='Are both universal target Gram PSD tests automatic for every arbitrary39 triangle matching core?',
         success='Exact general sum-of-squares derivation, exact coefficient identity controls, and rank/kernel controls; universal theorem remains candidate pending separate review.',
         fixtures='Six component-count controls, the archived shift6 core, and8 deterministic arbitrary matching/permutation controls.',
         random_seed=20260930,numerical_thresholds=None,numerical_thresholds_null_reason='No floating point.',limits=dict(seconds=120)))
    overlap=archive_overlap();save(out/'archive_overlap.json',overlap)
    standard=[i^1 for i in range(12)];cases=[]
    for c in range(1,7):
        size=7-c;p=list(range(12))
        for i in range(size):p[2*i]=2*((i+1)%size)
        cases.append((f'components_{c}',[standard]*3,p,c))
    cases.append(('archived_shift6',[standard]*3,[(i+6)%12 for i in range(12)],3))
    rng=random.Random(20260930)
    for i in range(8):
        ms=[standard]
        for _ in range(2):
            labels=list(range(12));rng.shuffle(labels);m=[0]*12
            for x,y in zip(labels[::2],labels[1::2]):m[x]=y;m[y]=x
            ms.append(m)
        p=list(range(12));rng.shuffle(p);cases.append((f'arbitrary_{i:02d}',ms,p,None))
    records=[]
    for name,ms,p,want in cases:
        need(time.monotonic()-start<120,'time cap')
        a,b=core(ms,p);cs=components(b);c=len(cs)
        if want is not None:need(c==want,'component-control exact count')
        need(all(len(set(part)&set(range(12*i,12*i+12)))==len(part)//3 for part in cs for i in range(3)),'component fiber balance')
        G,Q,gforms,qforms=sos39(a,b);gkernel,qkernel=kernel_bases(cs)
        need(all(annihilates(G,v)for v in gkernel)and all(annihilates(Q,v)for v in qkernel),'explicit kernel vectors')
        need(rank(gkernel)==c+2 and rank(qkernel)==2,'independent proposed kernel bases')
        gr,qr=rank(G),rank(Q);need(gr==37-c and qr==37,'exact rational rank controls')
        record=dict(name=name,matchings=ms,permutation=p,adjacency39=a,inner_components=cs,G=G,Q=Q,
                    G_rank_over_Q=gr,Q_rank_over_Q=qr,G_kernel_basis=gkernel,Q_kernel_basis=qkernel,
                    G_scaled144_SOS=[dict(weight=w,coefficients=v)for w,v in gforms],Q_scaled144_SOS=[dict(weight=w,coefficients=v)for w,v in qforms])
        save(out/(name+'.json'),record);records.append(dict(name=name,components=c,G_rank=gr,Q_rank=qr,sha256=h(out/(name+'.json'))))
    # Invalid assumptions and corrupted conclusions must be rejected.
    corruptions=[]
    invalid=[0]*12
    try:core([standard]*3,invalid)
    except ValueError:corruptions.append('nonpermutation_P')
    else:raise ValueError('accepted nonpermutation')
    try:core([list(range(12)),standard,standard],list(range(12)))
    except ValueError:corruptions.append('nonmatching_M0')
    else:raise ValueError('accepted nonmatching')
    a,b=core([standard]*3,list(range(12)));G,Q,gf,qf=sos39(a,b)
    bad=[row[:]for row in G];bad[0][0]+=1
    need(outer_sum(39,gf)!=[[144*x for x in row]for row in bad],'G diagonal corruption');corruptions.append('wrong_G_diagonal')
    bad=[row[:]for row in Q];bad[0][1]*=-1;bad[1][0]*=-1
    need(outer_sum(39,qf)!=[[144*x for x in row]for row in bad],'Q offdiag corruption');corruptions.append('wrong_Q_offdiagonal')
    bad=gf[:];bad[0]=(bad[0][0]+1,bad[0][1]);need(outer_sum(39,bad)!=outer_sum(39,gf),'wrong SOS coefficient');corruptions.append('wrong_SOS_weight')
    gk,qk=kernel_bases(components(b));gk[0][0]+=1;need(not annihilates(G,gk[0]),'corrupt kernel');corruptions.append('wrong_kernel_coordinate')
    controls=dict(status='PRODUCER_EXACT_CONTROLS_PASS',matrix_fixtures=len(records),corruptions_rejected=corruptions,
                  rank_controls_method='Exact integer row elimination with gcd scaling over Q; no modular or floating-point rank.',
                  independent_verification=False)
    save(out/'controls.json',controls)
    summary=dict(status='CANDIDATE_UNIVERSAL_TRIANGLE39_GRAM_SOS',timestamp=datetime.now(timezone.utc).isoformat(),
                 claim_id='C-TRIANGLE39-UNIVERSAL-GRAM-PSD-REDUNDANCY',claim_revision=1,kind='mathematical result',basis=['DERIVED','COMPUTED'],
                 statement='For every three perfect matchings M0,M1,M2 on12 labels and every permutation P, the specified complete39 triangle core has both27I-9A39+J andA39+4I positive semidefinite. If its cubic36 inner graph hasc connected components, the two real ranks are37-c and37, with kernel dimensionsc+2 and2 respectively.',
                 scope='All explicitly defined normalized39-vertex cores, including those that violate other target conditions. No prism-free, commutation, automorphism or feasibility premise.',
                 independent_verification=None,independent_verification_null_reason='Producer derivation and calibration only; root separately reviews exact theorem and artifacts.',
                 inputs_sha256=inputs,records=records,controls=controls,archive_overlap='archive_overlap.json',
                 target_resolution=False,elapsed_seconds=time.monotonic()-start,
                 limitations=['PSD/rank tests on these exact39 matrices cannot prune this core family; other constraints can still exclude cores.',
                              'The raw fixtures are calibration examples, not exhaustive P or matching coverage.',
                              'Prior archive material overlaps the decomposition; novelty is not claimed.',
                              'No target graph, incidence factor or nonexistence result is produced.'])
    summary['artifact_hashes']={p.relative_to(ROOT).as_posix():h(p)for p in sorted(out.iterdir())if p.is_file()}
    save(out/'summary.json',summary);print(json.dumps({'status':summary['status'],'summary_sha256':h(out/'summary.json'),'fixture_count':len(records)}))

if __name__=='__main__':main()
