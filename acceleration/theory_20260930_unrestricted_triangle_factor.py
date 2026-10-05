"""Candidate universal triangle normalization and variable-core factor theorem."""
from datetime import datetime,timezone
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import argparse
import json
import platform
import random
import subprocess
import sys
import time
import yaml

ROOT=Path(__file__).resolve().parents[1]
PIN='85e705cc6c2a14d123120c93a847e30aaab1789e'
DOC=ROOT/'docs/DERIVATION_20260930_UNRESTRICTED_TRIANGLE_FACTOR.md'
SPEC=Path(__file__).with_name('theory_20260930_unrestricted_triangle_factor_spec.md')
def need(ok,msg):
    if not ok:raise ValueError(msg)
def h(p):return sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def transpose(a):return [list(row)for row in zip(*a)]
def mul(a,b):return [[sum(x*y for x,y in zip(row,col))for col in zip(*b)]for row in a]
def identity(n):return [[int(i==j)for j in range(n)]for i in range(n)]
def matrix(q):return [[int(q[i]==j)for j in range(len(q))]for i in range(len(q))]
def check_matching(q):
    n=len(q);need(sorted(q)==list(range(n))and all(q[i]!=i and q[q[i]]==i for i in range(n)),'perfect matching involution')
def core(qs,p):
    m=len(p);need(m%2==0 and len(qs)==3 and all(len(q)==m for q in qs),'matching sizes')
    for q in qs:check_matching(q)
    need(sorted(p)==list(range(m)),'cross permutation')
    c=[[0]*(3*m)for _ in range(3*m)]
    for g in range(3):
        for i in range(m):c[g*m+i][g*m+qs[g][i]]=1
    for i in range(m):
        for j in [m+i,2*m+i]:c[i][j]=c[j][i]=1
        c[m+i][2*m+p[i]]=c[2*m+p[i]][m+i]=1
    return c
def direct_gram(c,m):
    square=mul(c,c)
    return [[m*int(i==j)-c[i][j]-square[i][j]+2-int(i//m==j//m)for j in range(3*m)]for i in range(3*m)]
def blocks(qs,p):
    m=len(p);ms=list(map(matrix,qs));pm=matrix(p);pt=transpose(pm);mp=mul(ms[1],pm);pm2=mul(pm,ms[2]);gg=[[None]*3 for _ in range(3)]
    for g in range(3):gg[g][g]=[[(m-3)*int(i==j)+1-ms[g][i][j]for j in range(m)]for i in range(m)]
    gg[0][1]=[[2-int(i==j)-ms[0][i][j]-ms[1][i][j]-pt[i][j]for j in range(m)]for i in range(m)]
    gg[0][2]=[[2-int(i==j)-ms[0][i][j]-ms[2][i][j]-pm[i][j]for j in range(m)]for i in range(m)]
    gg[1][2]=[[2-int(i==j)-pm[i][j]-mp[i][j]-pm2[i][j]for j in range(m)]for i in range(m)]
    for i,j in combinations(range(3),2):gg[j][i]=transpose(gg[i][j])
    return [[gg[i//m][j//m][i%m][j%m]for j in range(3*m)]for i in range(3*m)]

def canonical_columns(c0,matching):
    m=len(matching);check_matching(matching);need(len(c0)==m,'incidence row count')
    count=m*(m-2)//2;need(all(len(row)==count and all(type(v)is int and v in(0,1)for v in row)for row in c0),'incidence binaryshape')
    labels=[]
    for d in range(count):
        pair=tuple(i for i in range(m)if c0[i][d]);need(len(pair)==2 and matching[pair[0]]!=pair[1],'nonmatching column pair');labels.append(pair)
    expected=[(i,j)for i,j in combinations(range(m),2)if matching[i]!=j]
    need(sorted(labels)==expected,'exact edge bijection')
    order=sorted(range(count),key=lambda d:labels[d])
    return order,[[row[d]for d in order]for row in c0]

def validate_srg(a,k):
    n=len(a);need(all(len(r)==n and all(type(x)is int and x in(0,1)for x in r)for r in a),'binary square')
    need(all(a[i][i]==0 for i in range(n))and all(a[i][j]==a[j][i]for i,j in combinations(range(n),2)),'simple symmetry')
    need(all(sum(r)==k for r in a),'regular degree')
    need(mul(a,a)==[[(k-2)*int(i==j)-a[i][j]+2 for j in range(n)]for i in range(n)],'exact generic lambda1mu2 identity')

def normalize(a,root,k):
    validate_srg(a,k);m=k-2;need(len(set(root))==3 and all(a[i][j]for i,j in combinations(root,2)),'triangle root')
    cells=[[v for v in range(len(a))if v not in root and a[t][v]]for t in root]
    need(all(len(cell)==m for cell in cells)and len(set(sum(cells,[])))==3*m,'disjoint fibres')
    pending=set(cells[0]);a0=[]
    while pending:
        v=min(pending);mates=[w for w in cells[0]if a[v][w]];need(len(mates)==1,'internal matching');w=mates[0]
        need(w in pending and w!=v,'disjoint matching pair');a0.extend([v,w]);pending-={v,w}
    ordered=[a0]
    for cell in cells[1:]:
        labels=[]
        for v in a0:
            choices=[w for w in cell if a[v][w]];need(len(choices)==1,'cross matching');labels.append(choices[0])
        need(len(set(labels))==m,'cross bijection');ordered.append(labels)
    inside=set(root+sum(ordered,[]));outside=sorted(set(range(len(a)))-inside)
    c0=[[a[v][w]for w in outside]for v in a0];order,_=canonical_columns(c0,[i^1 for i in range(m)])
    outside=[outside[d]for d in order];labels=root+sum(ordered,[])+outside
    normalized=[[a[i][j]for j in labels]for i in labels]
    qs=[]
    for cell in ordered:qs.append([next(j for j,w in enumerate(cell)if a[v][w])for v in cell])
    p=[next(j for j,w in enumerate(ordered[2])if a[v][w])for v in ordered[1]]
    c=core(qs,p);need([row[3:3+3*m]for row in normalized[3:3+3*m]]==c,'normalized literal core')
    f=[row[3+3*m:]for row in normalized[3:3+3*m]]
    gram=[[sum(x*y for x,y in zip(r,s))for s in f]for r in f]
    need(gram==direct_gram(c,m)==blocks(qs,p),'known-valid normalized full Gram')
    return dict(new_to_old_labels=labels,root=root,matchings=qs,P_row_to_column=p,normalized_adjacency=normalized,incidence=f,Y_size=len(outside),C0_degenerate=not outside)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    inputs={p.relative_to(ROOT).as_posix():h(p)for p in [Path(__file__),SPEC,DOC,ROOT/'uv.lock',ROOT/'pyproject.toml']}
    save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),inputs_sha256=inputs,limits=dict(seconds=120),random_seed=20260930,seed_scope='Only arbitrary algebra/codec fixtures.',numerical_thresholds=None,numerical_thresholds_null_reason='Exact integers.',status='CANDIDATE',independent_approval=False))
    rook=[[int(i!=j and(i//3==j//3 or i%3==j%3))for j in range(9)]for i in range(9)];roots=[list(t)for t in combinations(range(9),3)if all(rook[i][j]for i,j in combinations(t,2))]
    need(len(roots)==6,'rook six triangles');rng=random.Random(20260930);rook_cases=[normalize(rook,t,4)for t in roots]
    for _ in range(6):
        perm=list(range(9));rng.shuffle(perm);a=[[rook[i][j]for j in perm]for i in perm];t=[perm.index(v)for v in roots[0]];rook_cases.append(normalize(a,t,4))
    save(out/'rook9_normalization_controls.json',dict(SRG_parameters=[9,4,1,2],cases=rook_cases,limitations='AllYsets are empty; this does not calibrate nonempty target incidence existence.'))
    fixtures=[];negative=[]
    def matching(n):
        labels=list(range(n));rng.shuffle(labels);q=[None]*n
        for i in range(0,n,2):q[labels[i]]=labels[i+1];q[labels[i+1]]=labels[i]
        return q
    for i in range(12):
        need(time.monotonic()-start<120,'120second cap')
        qs=[[j^1 for j in range(12)],matching(12),matching(12)];p=list(range(12));rng.shuffle(p)
        if i==0:qs=[[j^1 for j in range(12)]for _ in range(3)];p=list(range(12))
        if i==1:qs=[[j^1 for j in range(12)]for _ in range(3)];p=[(j+6)%12 for j in range(12)]
        c=core(qs,p);g=direct_gram(c,12);need(g==blocks(qs,p),'all1296 arbitrary core coefficients')
        fixtures.append(dict(index=i,matchings=qs,P_row_to_column=p,core36=c,prescribed_Gram=g,P_is_involution=all(p[p[j]]==j for j in range(12)),local_feasibility_asserted=False))
    save(out/'arbitrary12_core_coefficients.json',fixtures)
    fixture=next(f for f in fixtures if not f['P_is_involution']);qs=fixture['matchings'];p=fixture['P_row_to_column'];wrong=blocks(qs,p);pm=matrix(p);pt=transpose(pm)
    for i in range(12):
        for j in range(12):wrong[i][12+j]+=pt[i][j]-pm[i][j]
    need(wrong!=fixture['prescribed_Gram'],'wrong transpose convention detected');negative.append('G01_P_instead_of_Ptranspose')
    canonical=[[int(i in e)for e in combinations(range(12),2)if e[1]!=(e[0]^1)]for i in range(12)];codec=[]
    for _ in range(6):
        order=list(range(60));rng.shuffle(order);raw=[[row[d]for d in order]for row in canonical]
        recovered,result=canonical_columns(raw,[i^1 for i in range(12)]);need(result==canonical and [order[d]for d in recovered]==list(range(60)),'nonempty C0 exact recovery');codec.append(dict(input_column_order=order,recovered_column_order=recovered))
    save(out/'nonempty_C0_codec_controls.json',dict(raw_canonical_C0=canonical,cases=codec,scope='Exact incidence fixtures only, not a fulltarget factor.'))
    from copy import deepcopy
    corruptions=[]
    bad=deepcopy(rook);bad[0][1]=bad[1][0]=0;corruptions.append(('corrupted_rook_edge',lambda:validate_srg(bad,4)))
    # Execute distinct controls without deferred capture of mutable fixtures.
    for name,fn in corruptions:
        try:fn()
        except ValueError:negative.append(name)
        else:raise ValueError('corrupted graph accepted')
    for name,q in [('matching_fixed_point',[0]+[j^1 for j in range(1,12)]),('matching_duplicate',[j^1 for j in range(12)])]:
        if name=='matching_duplicate':q[0]=q[2]
        try:check_matching(q)
        except ValueError:negative.append(name)
        else:raise ValueError('bad matching accepted')
    bad=deepcopy(canonical)
    for row in bad:row[1]=row[0]
    try:canonical_columns(bad,[i^1 for i in range(12)])
    except ValueError:negative.append('duplicated_nonmatching_column')
    else:raise ValueError('duplicate column accepted')
    bad=deepcopy(canonical)
    for i,row in enumerate(bad):row[0]=int(i in(0,1))
    try:canonical_columns(bad,[i^1 for i in range(12)])
    except ValueError:negative.append('forbidden_matching_column')
    else:raise ValueError('matching column accepted')
    try:core([[j^1 for j in range(12)]for _ in range(3)],[0]*12)
    except ValueError:negative.append('nonbijective_cross_permutation')
    else:raise ValueError('bad permutation accepted')
    save(out/'corrupted_controls.json',dict(rejected=negative))
    archive=[];texts={}
    for path,section in [('attempts/wave149-terwilliger-triple/derivation.md','Sections1-3 general partition and Gram; sections4-5 fixedprism-free example'),('verification/wave149-terwilliger-triple/derivation.md','Historical independent derivation, scopechecked only'),('attempts/wave151-triangle-root-factor/derivation.md','Edge-permutation reduction; historical fixedfactor context'),('verification/wave151-triangle-root-factor/derivation.md','Historical independent edge reduction, scopechecked only'),('CLAIMS.yaml','Historical authoritative ledger; search for identifiers naming149/151')]:
        command=['git','-C','external_conway99_research','show',PIN+':'+path];raw=subprocess.check_output(command,cwd=ROOT);need(raw==(ROOT/'external_conway99_research'/path).read_bytes(),'immutable archive bytes');texts[path]=raw.decode('utf-8')
        archive.append(dict(repository='https://github.com/YesterdaysLemon/conway-99-research',commit=PIN,path=path,sha256=sha256(raw).hexdigest(),section=section,command=command))
    legacy=yaml.safe_load(texts['CLAIMS.yaml']);matches=[c['id']for c in legacy['claims']if any(s in json.dumps(c).lower()for s in ['wave149','wave151'])]
    save(out/'archive_overlap.json',dict(references=archive,original_claim_ids=matches or None,original_claim_ids_null_reason='No entry naming Wave149 or Wave151 was found in the pinned ledger.'if not matches else None,
        assessment='General partition/Gram and edge-incidence mechanisms already appear in the archive. Present universal coverage proof rederives them without inheriting the fixedprism-free experiment scope.',historical_VERIFIED_labels_imported=False,historical_experiments_rerun=False,novelty='UNKNOWN'))
    save(out/'summary.json',dict(status='CANDIDATE_UNRESTRICTED_TRIANGLE_FACTOR_NORMALIZATION',proposed_claim_id='C-UNRESTRICTED-TRIANGLE-CORE-FACTOR-NORMALIZATION',proposed_claim_revision=1,
        statement='Every symmetric binaryzero-diagonal99x99matrix satisfying A^2=12I-A+2J admits, after vertex relabelling, the triangle-core form with standardM0, identitycross01/cross02, arbitrarymatchingM1/M2 and arbitrarypermutationP, canonicalC0 incidence onall60nonmatching pairs, and binary36x60F with the exact stated Gram blocks, margins and necessarycolumn caps.',
        scope='Universal necessary normalization of the unrestricted target, with no prism-free or automorphism premise. A satisfying factor is only a partial specification, not a completegraph.',
        kind='mathematical result',basis=['DERIVED','COMPUTED'],independent_approval=False,assumptions=['Only the exact target identity and simplebinarysymmetry for the universalcoverage statement.'],
        controls=dict(known_valid_rook9_normalizations=12,rookYdegenerate=True,arbitrary12_core_fixtures=12,exact_Gram_entries_per_fixture=1296,nonempty_C0_codec_cases=6,corruptions_rejected=negative),
        written_coverage_proof=DOC.relative_to(ROOT).as_posix(),inputs_sha256=inputs,outputs_sha256={p.relative_to(ROOT).as_posix():h(p)for p in sorted(out.iterdir())if p.is_file()},
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),timestamp=datetime.now(timezone.utc).isoformat(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),
        target_resolution=False,external_review=False,limitations=['Producer-only candidate pending independent proof and artifact review.','No target or fullfactor construction, exclusion, novelty, or targetcoveragepercentage.','Arbitrarycore coefficientfixtures can be infeasible; they test algebra only.'],elapsed_seconds=time.monotonic()-start))
    print(json.dumps(dict(status='CANDIDATE_UNRESTRICTED_TRIANGLE_FACTOR_NORMALIZATION',summary_sha256=h(out/'summary.json'))))

if __name__=='__main__':main()
