"""Independent adjacency-set audit of one conditional literature identity."""
from pathlib import Path
from itertools import combinations
from collections import Counter
from datetime import datetime, timezone
import argparse, hashlib, json, platform, subprocess, sys, tarfile, time, traceback

ROOT=Path(__file__).resolve().parents[1]
P='acceleration/results/20261001_reimbayev_z82_overlap_v2/'
SUMMARY=P+'summary.json'
EXPECTED='6e79aa0c91a0f28fb575f089f9eb75915ce2b0debb0e777e73f27d0bc6fe1d57'
H=[{1,2,3},{0,2,4},{0,1},{0,4,5},{1,3,5},{3,4}]

def need(q,m):
    if not q: raise ValueError(m)
def sha(p):
    with p.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
def read(p): return json.loads((ROOT/p).read_bytes())
def save(p,x):
    with p.open('x',encoding='utf8',newline='\n') as f: json.dump(x,f,indent=2);f.write('\n')
def matrix(mask,n):
    a=[set() for _ in range(n)]
    for i,(u,v) in enumerate(combinations(range(n),2)):
        if mask & (1<<i): a[u].add(v);a[v].add(u)
    return a
def triangles(a,vertices):
    return [frozenset(t) for t in combinations(vertices,3) if all(v in a[u] for u,v in combinations(t,2))]
def is_h(a,vertices):
    vertices=set(vertices)
    if len(vertices)!=6: return False
    ts=triangles(a,sorted(vertices))
    if len(ts)!=2 or ts[0]&ts[1] or ts[0]|ts[1]!=vertices: return False
    cross=[(u,v) for u in ts[0] for v in ts[1] if v in a[u]]
    return len(cross)==2 and len({u for u,v in cross})==len({v for u,v in cross})==2
def caps(a):
    return all(len(a[u]&a[v]) <= (1 if v in a[u] else 2) for u,v in combinations(range(len(a)),2))
def srg(raw,n,k):
    need(len(raw)==n and all(len(r)==n for r in raw),'shape')
    need(all(type(v) is int and v in (0,1) for r in raw for v in r),'binary')
    a=[{j for j,x in enumerate(row) if x} for row in raw]
    need(all(len(a[i])==k and i not in a[i] for i in range(n)),'degree and diagonal')
    for u,v in combinations(range(n),2):
        need((v in a[u])==(u in a[v]),'symmetry')
        need(len(a[u]&a[v])==(1 if v in a[u] else 2),'exact common neighbors')
    return a
def rejected(fn,label):
    try: fn()
    except (ValueError,AssertionError): return label
    raise ValueError('bad control accepted: '+label)

def run(out):
    started=datetime.now(timezone.utc).isoformat(); clock=time.monotonic()
    need(sha(ROOT/SUMMARY)==EXPECTED,'candidate summary identity'); candidate=read(SUMMARY)
    pins={SUMMARY:EXPECTED,**candidate['inputs_sha256'],**candidate['outputs_sha256']}
    for p,d in pins.items(): need(sha(ROOT/p)==d,'input identity '+p)
    need(is_h(H,range(6)) and caps(H),'recognizer positive H')
    badcross=[s.copy() for s in H];badcross[0].remove(3);badcross[3].remove(0)
    need(not is_h(badcross,range(6)),'recognizer one-cross corruption')
    prism=[s.copy() for s in H];prism[2].add(5);prism[5].add(2)
    need(not is_h(prism,range(6)),'recognizer prism corruption')
    # A separate full positive validator fixture: the 3 by 3 rook graph.
    rook=[[int(i!=j and (i//3==j//3 or i%3==j%3)) for j in range(9)] for i in range(9)]
    srg(rook,9,4)
    bad=[r[:] for r in rook];bad[0][0]=1
    controls=[rejected(lambda:srg(bad,9,4),'positive_fixture_diagonal_corruption')]
    bad2=[r[:] for r in rook];bad2[0][1]=bad2[1][0]=0
    controls.append(rejected(lambda:srg(bad2,9,4),'positive_fixture_edge_removed'))
    selected=read(P+'selected_graph.json'); overlap=read(P+'archive_overlap.json')
    need(is_h(matrix(selected['N3_canonical_mask'],6),range(6)),'raw N3 alignment')
    z=matrix(selected['Z82_canonical_mask'],7); isolates=[v for v in range(7) if not z[v]]
    need(len(isolates)==1 and is_h(z,set(range(7))-set(isolates)),'raw Z82 alignment')
    rows=read('external_conway99_research/attempts/wave23-weighted-extensions/affine-witness.json')['order_seven_affine_family']['records']
    need(len(rows)==208 and len({r['canonical_mask'] for r in rows})==208,'exact archive population')
    observed=[]
    for r in rows:
        m=r['canonical_mask'];a=matrix(m,7);need(caps(a),'archive local bounds')
        roots=[v for v in range(7) if is_h(a,set(range(7))-{v})]
        degrees=[len(a[v]) for v in roots];need(all(d<=2 for d in degrees),'triangle attachment bound')
        # Count actual neighbor subsets rather than use the producer permutation path.
        terms=[dict(root=v,deletion=1,vertex_sum=len(a[v]),pair_sum=len(list(combinations(a[v],2)))) for v in roots]
        coefficient=sum(t['deletion']-t['vertex_sum']+t['pair_sum'] for t in terms)
        iso=[v for v in range(7) if not a[v]]
        wanted=int(len(iso)==1 and is_h(a,set(range(7))-set(iso)))
        need(coefficient==wanted,'row identity on raw class')
        observed.append(dict(mask=m,coefficient=coefficient,terms=terms))
    need(observed==overlap['coefficients'],'all208 independently reconstructed coefficients and roots')
    need(sum(r['coefficient'] for r in observed)==1,'one Z82 class in archive')
    zrecord=next(r for r in rows if r['canonical_mask']==selected['Z82_canonical_mask'])
    need(zrecord==overlap['selected_affine_record'] and zrecord['count_at_z_min']==23265 and zrecord['delta_per_z']==0,'one archive coordinate')
    residual=[(1 if v in H[u] else 2)-len(H[u]&H[v]) for u,v in combinations(range(6),2)]
    need(sum(residual)==8 and sum(map(len,H))==16,'exact local count derivation')
    ap=read(P+'attachments_and_pair_residuals.json'); independent=[]
    for mask in range(64):
        a=[s.copy() for s in H]+[{i for i in range(6) if mask&(1<<i)}]
        for i in a[6]: a[i].add(6)
        degree=len(a[6]);valid=caps(a)
        if valid: need(degree<=2,'all locally valid attachments have degree <=2')
        independent.append(dict(mask=mask,admissible=valid,degree=degree,combination=1-degree+len(list(combinations(a[6],2)))))
    need(independent==ap['attachments'],'complete64 attachment comparison')
    need(sum(x['admissible'] for x in independent)==14,'14 admissible attachments')
    c=read(P+'controls.json'); synthetic=c['synthetic_local_fixture']; nb=synthetic['outside_neighborhoods_in_core']
    local=[s.copy() for s in H]+[set(r) for r in nb]
    for i in range(6,99):
        for v in local[i]: local[v].add(i)
    need(len(local)==99 and all(len(local[i])==14 for i in range(6)),'six local degrees')
    need(all(len(local[u]&local[v])==(1 if v in local[u] else 2) for u,v in combinations(range(6),2)),'15 local pair equations')
    need(caps(local) and any(len(s)!=14 for s in local),'local caps and not full SRG')
    hist=[sum(len(s&set(range(6)))==i for s in local[6:]) for i in range(3)]
    need(hist==[33,52,8],'nonvacuous synthetic local histogram')
    raw=read('acceleration/results/20260930_srg243_residual_fixture/adjacency243.json')['adjacency']
    a=srg(raw,243,22);ts=triangles(a,range(243));need(len(ts)==891,'genuine243 triangles')
    census=Counter()
    for t,u in combinations(ts,2):
        if not t&u: census[sum(len(a[v]&u) for v in t)]+=1
    need(dict(census)=={0:133650,1:240570,3:8910},'complete243 disjoint triangle pair census')
    need({str(k):v for k,v in sorted(census.items())}==c['disjoint_triangle_pair_cross_edge_histogram'],'producer census comparison')
    need(c['genuine243_N3_control_vacuous'] and c['genuine243_examples']==[],'vacuity disclosure')
    controls.append(rejected(lambda:need(observed[0]['coefficient']+1==overlap['coefficients'][0]['coefficient'],'coefficient'),'changed_coefficient'))
    controls.append(rejected(lambda:need(hist==[32,53,8],'histogram'),'wrong_local_histogram'))
    controls.append(rejected(lambda:need(census[2]>0,'nonvacuous'),'false_genuine243_positive'))
    controls.append(rejected(lambda:need(zrecord['count_at_z_min']+1==33*705,'coordinate'),'changed_archive_coordinate'))
    access='acceleration/results/20261001_reimbayev_seven_access/source.tar.gz'
    with tarfile.open(ROOT/access,'r:gz') as tar:
        tex=tar.extractfile('The_Subgraphs_of_Order_Seven.tex').read()
        figure=tar.extractfile('figure_2.png').read()
    need(hashlib.sha256(tex).hexdigest()==selected['tex_member_sha256'],'source TeX identity')
    need(selected['formula_tex'].encode() in tex,'exact selected primary formula')
    need(hashlib.sha256(figure).hexdigest()==selected['figure_sha256'],'source figure identity')
    (out/'source_figure_2.png').write_bytes(figure)
    need(time.monotonic()-clock<120,'predeclared120-second cooperative ceiling')
    save(out/'coefficients.json',observed);save(out/'controls.json',dict(rejected=controls,recognizer_positive=True,recognizer_negative=['one_cross_edge','three_cross_edges'],rook_positive=[9,4,1,2],genuine243_valid=True,genuine243_census=dict(census),genuine243_N3_positive=False,synthetic_local_histogram=hist,synthetic_full_SRG=False))
    pins[Path(__file__).relative_to(ROOT).as_posix()]=sha(Path(__file__))
    spec=Path(__file__).with_name(Path(__file__).stem+'_spec.md');pins[spec.relative_to(ROOT).as_posix()]=sha(spec)
    summary=dict(status='INDEPENDENT_REIMBAYEV_Z82_ARITHMETIC_PASS',timestamp=started,verifier='/root',claim_originator='/root/state_literature_audit',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),elapsed_seconds=time.monotonic()-clock,inputs_sha256=pins,outputs_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in out.iterdir()},complete_archive_coefficients=208,complete_local_attachments=64,scope='Conditional exact z82=(n-6k+18)n3 identity and overlap with the archived deletion/vertex/pair row definitions; no new restriction or full-paper approval.',source_alignment_visual_review='PENDING; extracted unchanged primary figure for separate root inspection.',shared_components=['Python standard library and raw primary/archive input bytes; no producer or archive module imports.','Archive row normalization additionally requires written source review; not a fresh full-system reapproval.'],limitations=['243 positive is vacuous for N3; nonvacuous local fixture is not an SRG.','No verification of all208 published formulas, whole712-row archive model, novelty, graph construction, or exclusion.'],solver_calls=0,ledger_mutations=0)
    save(out/'summary.json',summary);print(json.dumps(dict(status=summary['status'],summary_sha256=sha(out/'summary.json'),elapsed_seconds=summary['elapsed_seconds'])))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);args=ap.parse_args();out=ROOT/args.out;out.mkdir(parents=True,exist_ok=False)
    try: run(out)
    except BaseException as ex: save(out/'failure.json',dict(error=repr(ex),traceback=traceback.format_exc(),source_sha256=sha(Path(__file__))));raise
