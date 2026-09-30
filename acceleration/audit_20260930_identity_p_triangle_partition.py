"""Independent identity-P mixed-cap derivation and conditional triangle controls."""
from collections import Counter
from copy import deepcopy
from datetime import datetime,timezone
from itertools import combinations
from pathlib import Path
import argparse
import hashlib
import json
import platform
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
PRODUCER=ROOT/'acceleration/results/20260930_identity_p_mixed_redundancy'
PRODUCER_SHA='badb65f6e8ea5c2c7268c3f452d2222b8d2d79d8a158616409819e98a87aa644'
ARCHIVE='85e705cc6c2a14d123120c93a847e30aaab1789e'
def need(x,s):
    if not x:raise ValueError(s)
def digest(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(Path(p).read_bytes())
def save(p,x):
    with Path(p).open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')

def mixed_controls(raw):
    c=raw['core_adjacency'];need(len(c)==36 and all(len(row)==36 for row in c),'raw core dimensions')
    for i,row in enumerate(c):
        need(all(type(x)is int and x in (0,1) for x in row) and row[i]==0 and sum(row)==3,'raw cubic graph')
        g,a=divmod(i,12)
        for h in range(3):
            want={12*g+raw[f'M{g}'][a]} if h==g else {12*h+a}
            need({j for j in range(h*12,(h+1)*12) if row[j]}==want,'literal identity crosses/internal matching')
        need(all(c[j][i]==row[j] for j in range(36)),'symmetric core')
    nb=[{j for j,x in enumerate(row) if x} for row in c]
    gram=[[12*int(i==j)+2-c[i][j]-len(nb[i]&nb[j])-int(i//12==j//12) for j in range(36)] for i in range(36)]
    need(gram==raw['target_gram'],'literal prescribed Gram')
    for a in range(12):
        for g,h in combinations(range(3),2):need(gram[12*g+a][12*h+a]==0,'same-coordinate zero Gram')
    closed=[sum(1<<j for j in neighbors|{i}) for i,neighbors in enumerate(nb)]
    hist=Counter();compatible=0;total=0
    for p0 in combinations(range(12),2):
        for p1 in combinations([a for a in range(12) if a not in p0],2):
            for p2 in combinations([a for a in range(12) if a not in p0+p1],2):
                support=p0+tuple(12+a for a in p1)+tuple(24+a for a in p2);mask=sum(1<<i for i in support)
                maximum=max((mask&s).bit_count() for s in closed);need(maximum<=2,'literal mixed cap');hist[maximum]+=1;total+=1
                if all(gram[i][j]>0 for i,j in combinations(support,2)):
                    need(all(not c[i][j] for i,j in combinations(support,2)),'zero-compatible six points independent');compatible+=1
    need(total==83160,'frozen finite support population')
    return dict(support_population=total,mixed_cap_maximum_histogram={str(k):v for k,v in hist.items()},zero_Gram_pair_compatible_supports=compatible)

def all_matchings(left,partner):
    if not left:yield bytes(partner);return
    i=left[0]
    for j in left[1:]:
        partner[i]=j;partner[j]=i
        yield from all_matchings(tuple(x for x in left[1:] if x!=j),partner)

def matching_check(partner,require_independent=True):
    need(len(partner)==14 and all(type(x)is int and 0<=x<14 for x in partner),'partner map shape')
    need(all(partner[i]!=i and partner[partner[i]]==i for i in range(14)),'perfect matching involution')
    internal=sum(i<partner[i]<6 for i in range(6));outside=sum(6<=i<partner[i] for i in range(6,14))
    need(outside==1+internal,'exact endpoint count identity')
    if require_independent:need(internal==0 and outside==1,'independent-six conclusion')
    return internal,outside

def residual(q):
    return [[int((u==v and b!=d) or (q[u][v] and b==d)) for v in range(20) for d in range(3)]
            for u in range(20) for b in range(3)]

def residual_check(d):
    need(len(d)==60 and all(len(row)==60 and all(type(x)is int and x in (0,1) for x in row) for row in d),'raw60binary')
    need(all(d[i][i]==0 and sum(d[i])==8 and all(d[i][j]==d[j][i] for j in range(60)) for i in range(60)),'simple symmetric degree8')
    nb=[{j for j,x in enumerate(row) if x} for row in d]
    triangles=set()
    for y in range(60):
        edges=[(a,b) for a,b in combinations(sorted(nb[y]),2) if d[a][b]]
        need(len(edges)==1,'exactly one neighbor edge and one triangle per vertex')
        triangles.add(tuple(sorted((y,*edges[0]))))
    need(len(triangles)==20 and sorted(v for t in triangles for v in t)==list(range(60)),'twenty disjoint covering triangles')
    return sorted(triangles)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    args.out=args.out.resolve();args.out.mkdir(parents=True,exist_ok=False);bindings={};start=time.monotonic()
    def pin(p,h=None):
        value=digest(p);need(h is None or value==h,'artifact hash '+key(p));bindings[key(p)]=value
    def load(p,h=None):pin(p,h);return read(p)
    try:
        candidate=load(PRODUCER/'summary.json',PRODUCER_SHA)
        for p,h in {**candidate['inputs_sha256'],**candidate['outputs_sha256']}.items():pin(ROOT/p,h)
        producer=read(PRODUCER/'controls.json');finite=[]
        for rec in producer['cores']:
            raw=load(ROOT/rec['core']);checked=mixed_controls(raw)
            need(all(rec[k]==v for k,v in checked.items()),'independent complete finite control population agrees')
            finite.append(dict(core=rec['core'],**checked))
        total=0;admissible=0;hist=Counter();seen=set();counterexample=None
        with (args.out/'all14_matchings.bin').open('xb') as f:
            for encoded in all_matchings(tuple(range(14)),[0]*14):
                need(encoded not in seen,'unique enumerated matching');seen.add(encoded);f.write(encoded)
                inside,outside=matching_check(list(encoded),require_independent=False);hist[f'{inside},{outside}']+=1;total+=1
                if inside==0:matching_check(list(encoded));admissible+=1;positive=list(encoded)
                elif counterexample is None:counterexample=list(encoded)
        need(total==135135 and admissible==20160,'complete14matching population and independent-six subpopulation')
        q=[[0]*20 for _ in range(20)]
        for i in range(10):
            for s in range(6):q[i][10+(i+s)%10]=q[10+(i+s)%10][i]=1
        need(all(sum(row)==6 for row in q) and all(not(q[a][b] and q[b][c] and q[c][a]) for a,b,c in combinations(range(20),3)), 'six-regular triangle-free20 graph')
        d=residual(q);triangles=residual_check(d)
        save(args.out/'residual60_control.json',dict(label='Only degree8 and20triangle partition positive; NOT a factor or SRG99',Q=q,D=d,triangles=triangles))
        badq=deepcopy(q)
        for a,b in [(0,10),(1,11)]:badq[a][b]=badq[b][a]=0
        for a,b in [(0,1),(10,11)]:badq[a][b]=badq[b][a]=1
        badD=residual(badq);need(all(sum(row)==8 for row in badD),'corrupted residual keeps degree8')
        rejected=[]
        def reject(name,fn):
            try:fn()
            except ValueError:rejected.append(name)
            else:raise ValueError('accepted corrupt control '+name)
        reject('degree_preserving_extra_triangles',lambda:residual_check(badD))
        reject('missing_independent_six_premise',lambda:matching_check(counterexample))
        for label in ['self_loop','noninvolution','missing_endpoint']:
            bad=positive[:]
            if label=='self_loop':bad[0]=0
            elif label=='noninvolution':bad[0]=(bad[0]+1)%14
            else:bad.pop()
            reject(label,lambda bad=bad:matching_check(bad))
        save(args.out/'controls.json',dict(finite_core_supports=finite,total_matchings=total,independent_six_matchings=admissible,
            matching_record_bytes=14,matching_histogram_core_edges_outside_edges=dict(hist),matching_countercontrol=counterexample,
            degree_preserving_residual_countercontrol=badD,corruptions_rejected=rejected))
        need(subprocess.check_output(['git','-C','external_conway99_research','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==ARCHIVE,'immutable archive pin')
        archive_paths=['external_conway99_research/attempts/wave149-terwilliger-triple/derivation.md',
                       'external_conway99_research/attempts/wave133-triangle-holonomy-topology/README.md',
                       'external_conway99_research/attempts/wave39-simultaneous-bh/README.md']
        for p in archive_paths:pin(ROOT/p)
        search_command=['rg','-n','-i','-g','*.md',r'33 triangles|20 triangles|triangle spread|33K3|20K3|partition.{0,45}triangles',
                        'external_conway99_research/attempts','external_conway99_research/verification']
        search=subprocess.run(search_command,cwd=ROOT,capture_output=True,text=True);need(search.returncode in (0,1),'archive text search')
        (args.out/'archive_search.stdout.txt').write_text(search.stdout,encoding='utf-8',newline='\n')
        (args.out/'archive_search.stderr.txt').write_text(search.stderr,encoding='utf-8',newline='\n')
        save(args.out/'overlap_review.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),archive_repository='https://github.com/YesterdaysLemon/conway-99-research',
            archive_commit=ARCHIVE,archive_sections=[dict(path=archive_paths[0],section='1 Root partition;2 Prisms as fixed points;3 Forced Gram'),dict(path=archive_paths[1],section='Rooted triangle holonomy and scope boundary'),dict(path=archive_paths[2],section='Simultaneous B/H consequences, lines120-134',overlap='Historical local formula: y belongs to1+e_y outside triangles; its32 count is under a distinct prism-free endpoint premise. The present proof independently derives e_y=0 and20 triangles for identity crosses.')],
            archive_command=search_command,archive_return_code=search.returncode,novelty='UNKNOWN',
            primary_web_candidate=dict(url='https://math.uchicago.edu/~may/REU2023/REUPapers/Selub.pdf',version='REU2023',fetch_result='web open failed: restricted URL; no theorem attributed'),
            web_search_date='2026-09-30',web_queries=['"99" "14" "1" "2" "triangle spread"','"Conway" "99" "33" "triangles"','"99-graph" "triangles" "partition"','"Conway’s 99-graph" "triangle"','"srg(99,14,1,2)" "spread"','"Conway" "99-graph" "holonomy"'],
            exploratory_failures=['Initial rg used unsupported Windows path acceleration/*.md; repeated using -g glob.','Attempted wave133 derivation.md was absent; actual README.md was read.'],
            interpretation='Overlapping normalization/Gram/holonomy prerequisites and the historical1+e_y local formula located. The archive32-triangle count belongs to a distinct prism-free endpoint. The exact identity-cross33-partition is derived independently, with no inherited endpoint premise. This is neither a novelty nor a comprehensive-literature claim.'))
        for p in [Path(__file__),ROOT/'docs/AUDIT_20260930_IDENTITY_P_TRIANGLE_PARTITION.md',ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(p)
        now=datetime.now(timezone.utc).isoformat()
        report=dict(status='INDEPENDENT_IDENTITY_P_MIXED_AND_TRIANGLE_PARTITION_PASS',timestamp=now,
            source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),
            inputs_sha256=bindings,outputs_sha256={key(p):digest(p) for p in args.out.iterdir() if p.is_file()},
            mathematical_audit='docs/AUDIT_20260930_IDENTITY_P_TRIANGLE_PARTITION.md',
            finite_support_controls=332640,matching_population=135135,independent_six_subpopulation=20160,
            residual_positive=dict(vertices=60,degree=8,triangle_partition_size=20,full_factor=False,target_graph=False),corruptions_rejected=rejected,
            verifier='/root/state_literature_audit',method='independent_derivation_and_exact_artifact_check',
            shared_components=['Python standard library only; no producer imports.','Raw four-core matrices authenticated by the earlier independent domain gate.'],
            recommendation='VERIFIED',review_state='CLEAR',artifact_availability='LOCAL_ONLY',target_resolution=False,external_review=False,
            limitations=['Identity cross matchings are a conditional restriction, not unrestricted normalization.',
                         'No actual full36factor, residual completion or target graph is provided.',
                         'No uniqueness of the full99 triangle partition and no novelty claim.',
                         'The finite controls are separate from the universal written proof.'],elapsed_seconds=time.monotonic()-start)
        save(args.out/'summary.json',report)
        claims=[dict(id='C-IDENTITY-P-FACTOR-DISTINCT-COORDINATES-MIXED-CAP-REDUNDANCY',revision=1,
            statement='For any three perfect matchings on12coordinates and identity cross matchings, each column of every binary36x60 exact prescribed-Gram factor uses at most one vertex per coordinate triangle, hence every entry of (I+C)F is at most2; with two entries per fibre its six chosen vertices are independent.',
            scope='All internal matching triples with identity cross matchings; conditional factor lemma only.',dependencies=[]),
            dict(id='C-IDENTITY-P-COMPLETION-THIRTYTHREE-TRIANGLE-PARTITION',revision=1,
            statement='Every SRG(99,14,1,2) completion of a triangle-root core whose three cross matchings are identity has an outside8-regular60vertex graph in which each vertex belongs to exactly one triangle, so its20disjoint triangles together with the root and12coordinate triangles partition all99vertices into33triangles.',
            scope='Conditional identity-cross family only; existence and uniqueness of the global partition are not asserted.',
            dependencies=[dict(id='C-IDENTITY-P-FACTOR-DISTINCT-COORDINATES-MIXED-CAP-REDUNDANCY',revision=1,relation='premise'),
                          dict(id='C-UNRESTRICTED-TRIANGLE-CORE-FACTOR-NORMALIZATION',revision=1,relation='uses_result')])]
        for c in claims:c.update(kind='mathematical result',basis=['DERIVED'],recommendation='VERIFIED',review_state='CLEAR',
            assumptions=['No nontrivial target automorphism is assumed.','The recorded identity-cross premise is explicit.'],
            verifier=report['verifier'],method=report['method'],evidence=[dict(path=key(args.out/'summary.json'),sha256=digest(args.out/'summary.json'),availability='LOCAL_ONLY')],
            limitations=report['limitations'],created_at=now,updated_at=now)
        save(args.out/'claim_bindings.json',dict(claims=claims,ledger_changed=False))
        print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'),binding_sha256=digest(args.out/'claim_bindings.json'))))
    except BaseException as e:save(args.out/'failure.json',dict(error=repr(e)));raise
if __name__=='__main__':main()
