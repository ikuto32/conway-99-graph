"""Independent arithmetic path for a literature candidate, not an approval gate."""
import argparse, collections, datetime, hashlib, itertools, json, math, tarfile, time, traceback
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'
A='acceleration/results/20261001_reimbayev_seven_access/'
W='external_conway99_research/attempts/wave23-weighted-extensions/'
PINS={
'acceleration/theory_20261001_reimbayev_z82_overlap.py':'e7a3bfca44dd14d57e345505d3196565e9f4035f7c161ece6b6940164968cf48',
'acceleration/theory_20261001_reimbayev_z82_overlap_spec.md':'979c179a0dff45d543b4f91e95ee76b333e8ad07837c932ad33e9cc42012ea60',
'acceleration/results/20261001_reimbayev_z82_overlap/failure.json':'9fd6af88825b9f0c6ba84a148bf2f270d0e5c19004f0c215e78f85823862c8a6',
A+'source.tar.gz':'21f5e912ede113c3dc1a892156274b2a4e184152bfe26b888ab4906b5e506e50',
A+'fulltext.html':'09377f0b08646cfd92c847f76ee342805161f2480f8d3bbf49a95b4d52ff33af',
A+'summary.json':'e3af72b27c456bcebe2ccd6387669c548d8aa06c53ddbd61828b8eac94d7b134',
W+'model.py':'8bc0f100772d95d06b60ec672ccc73817af4c30fd7fbf3276700554a87186abf',
W+'affine-witness.json':'16ade54a77589b91478b3426dc3dbe57ebb2a5e0f7d209602ca282e42ac3ec77',
W+'exact-results.json':'83a41b78eac02d845650ccdcb5b9782aba80caff9bdb7be983ec3f9e91c65b4c',
W+'failed-routes.md':'400966fae98ccd206b8cadf14ae37b3e95dfebc3754da741409089b8a251daf5',
'external_conway99_research/verification/wave23-weighted-extensions/2026-07-23T202156Z-audit.md':'3991ccbc64753e867829a650c00bd64191e2a28ea8e947bb68f83e889ebe249d',
'docs/LITERATURE_20260917.md':'e73d030b5c54b29b53f8883c3802fc8a72f5cb98a5821ce877b02bcbb3ded12d',
B+'srg243_residual_fixture/adjacency243.json':'5c7c8268b7d62997b5c87a56b11fd673f3f80fcb029b83816179ee8127b8e0d3',
B+'independent_review/srg243_residual_fixture/summary.json':'28bbd97b8e69515c3eb0345e5aa2db12debfaa8a44e83b2e3487342104c5d50e'}
E6=list(itertools.combinations(range(6),2));E7=list(itertools.combinations(range(7),2))
H={(0,1),(0,2),(1,2),(3,4),(3,5),(4,5),(0,3),(1,4)}
FORMULA=r'z_{82}=&(n-6k+18)n_3,'

def need(q,m):
    if not q: raise ValueError(m)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads((ROOT/p).read_text(encoding='utf-8'))
def save(p,d): p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def orbit(edges,n):
    positions={e:i for i,e in enumerate(itertools.combinations(range(n),2))}
    return {sum(1<<positions[tuple(sorted((p[a],p[b])))] for a,b in edges) for p in itertools.permutations(range(n))}
def rows(mask,n):
    result=[0]*n
    for i,(a,b) in enumerate(itertools.combinations(range(n),2)):
        if mask>>i&1: result[a]|=1<<b;result[b]|=1<<a
    return result
def admissible(rr):
    return all((rr[a]&rr[b]).bit_count() <= (1 if rr[a]>>b&1 else 2) for a,b in itertools.combinations(range(len(rr)),2))
def fixture_check(adj):
    n=len(adj);need(n==243 and all(len(r)==n for r in adj),'243 shape')
    need(all(type(v) is int and v in (0,1) for r in adj for v in r),'binary fixture')
    rr=[sum(v<<j for j,v in enumerate(r)) for r in adj]
    need(all(rr[i].bit_count()==22 and not(rr[i]>>i&1) for i in range(n)),'fixture degree/diagonal')
    for a,b in itertools.combinations(range(n),2):
        need(adj[a][b]==adj[b][a],'fixture symmetry')
        need((rr[a]&rr[b]).bit_count()==(1 if adj[a][b] else 2),'fixture common neighbors')
    return rr
def reject(fn,label):
    try: fn()
    except (ValueError,AssertionError): return label
    raise ValueError('corruption unexpectedly passed: '+label)

def run(out):
    start=time.monotonic()
    def budget(): need(time.monotonic()-start<120,'cooperative 120s ceiling')
    for p,h in PINS.items(): need(sha(ROOT/p)==h,'input pin '+p)
    with tarfile.open(ROOT/(A+'source.tar.gz'),'r:gz') as tar:
        raw=tar.extractfile('The_Subgraphs_of_Order_Seven.tex').read()
        tex=raw.decode('utf-8')
        fig=tar.extractfile('figure_2.png').read()
    need(FORMULA in tex,'literal selected paper formula')
    line=next(i for i,x in enumerate(tex.splitlines(),1) if FORMULA in x)
    horbit=orbit(H,6);zorbit=orbit(H,7)
    hmask=min(horbit);zmask=min(zorbit)
    need(hmask==5941,'existing N3 source alignment')
    hrows=rows(sum(1<<E6.index(e) for e in H),6)
    pair_residuals=[]
    for a,b in E6:
        internal=(hrows[a]&hrows[b]).bit_count()
        target=1 if hrows[a]>>b&1 else 2
        pair_residuals.append(dict(pair=[a,b],target=target,inside=internal,outside=target-internal))
    need(sum(x['outside'] for x in pair_residuals)==8,'outside pair sum')
    attachments=[]
    for mask in range(64):
        rr=hrows+[mask]
        for a in range(6):
            if mask>>a&1: rr[a]|=1<<6
        ok=admissible(rr);d=mask.bit_count()
        if ok: need(d<=2 and 1-d+math.comb(d,2)==int(d==0),'attachment degree polynomial')
        attachments.append(dict(mask=mask,admissible=ok,degree=d,combination=1-d+math.comb(d,2)))
    need(sum(x['admissible'] for x in attachments)==14,'attachment population')
    archive=read(W+'affine-witness.json');records=archive['order_seven_affine_family']['records']
    need(len(records)==208 and len({r['canonical_mask'] for r in records})==208,'archived208 population')
    coeff=[]
    for record in records:
        mask=record['canonical_mask'];rr=rows(mask,7);need(admissible(rr),'raw upper graph locally admissible')
        terms=[]
        for root in range(7):
            vertices=[v for v in range(7) if v!=root]
            card=sum(1<<i for i,(a,b) in enumerate(E6) if rr[vertices[a]]>>vertices[b]&1)
            if card in horbit:
                degree=rr[root].bit_count();need(degree<=2,'upper root degree')
                terms.append(dict(root=root,deletion=1,vertex_sum=degree,pair_sum=math.comb(degree,2)))
        value=sum(t['deletion']-t['vertex_sum']+t['pair_sum'] for t in terms)
        need(value==int(mask in zorbit),'complete208 row-combination coefficient')
        coeff.append(dict(mask=mask,coefficient=value,terms=terms))
    zrecord=next(r for r in records if r['canonical_mask']==zmask)
    need(zrecord['count_at_z_min']==33*705 and zrecord['delta_per_z']==0,'archived selected coordinate')
    budget()
    adj=read(B+'srg243_residual_fixture/adjacency243.json')['adjacency'];rr=fixture_check(adj)
    triangles=[]
    for a in range(243):
        for b in range(a+1,243):
            if rr[a]>>b&1:
                common=rr[a]&rr[b]
                for c in range(b+1,243):
                    if common>>c&1: triangles.append((a,b,c))
    need(len(triangles)==891,'genuine243 triangle census')
    examples=[];cross_hist=collections.Counter()
    for t,u in itertools.combinations(triangles,2):
        if set(t)&set(u): continue
        cross=sum((rr[a]>>b)&1 for a in t for b in u);cross_hist[cross]+=1
        if cross!=2 or len(examples)>=32: continue
        vertices=list(t+u)
        mask=sum(1<<i for i,(a,b) in enumerate(E6) if rr[vertices[a]]>>vertices[b]&1)
        need(mask in horbit,'two-cross triangle matching identification')
        selected=sum(1<<v for v in vertices);hist=[0]*7
        outsiders=[]
        for v in range(243):
            if selected>>v&1: continue
            d=(rr[v]&selected).bit_count();hist[d]+=1
            if d==0: outsiders.append(v)
        need(hist==[129,100,8,0,0,0,0],'genuine243 literal histogram')
        examples.append(dict(triangles=[list(t),list(u)],outside_histogram=hist,isolated_extenders=outsiders))
    need(cross_hist[2]==0 or len(examples)==min(32,cross_hist[2]),'actual positive population')
    # Synthetic local completion of the six degrees and 15 pair equations only.
    chosen=[[] for _ in range(33)]
    for row in pair_residuals: chosen.extend([row['pair']]*row['outside'])
    pair_degree=[sum(a in row for row in chosen) for a in range(6)]
    for a in range(6): chosen.extend([[a]]*(14-hrows[a].bit_count()-pair_degree[a]))
    need(len(chosen)==93,'synthetic outside count')
    synthetic=hrows+[0]*93
    for i,nb in enumerate(chosen,6):
        for a in nb: synthetic[i]|=1<<a;synthetic[a]|=1<<i
    need(all(synthetic[a].bit_count()==14 for a in range(6)),'synthetic six degrees')
    need(all((synthetic[a]&synthetic[b]).bit_count()==(1 if synthetic[a]>>b&1 else 2) for a,b in E6),'synthetic15 pair equations')
    need(admissible(synthetic),'synthetic entire local caps')
    synthetic_hist=[sum(len(nb)==d for nb in chosen) for d in range(3)]
    need(synthetic_hist==[33,52,8],'synthetic nonvacuous histogram')
    need(any(r.bit_count()!=14 for r in synthetic),'synthetic is not an SRG')
    bad=[r[:] for r in adj];bad[0][1]=1-bad[0][1]
    corruptions=[reject(lambda:fixture_check(bad),'asymmetric_fixture'),
                 reject(lambda:need(FORMULA in tex.replace(FORMULA,FORMULA.replace('+18','+17')),'formula'),'changed_paper_formula'),
                 reject(lambda:need(99-6*14+17==33,'constant'),'wrong_local_constant'),
                 reject(lambda:need(1-2==0,'missing pair term'),'omitted_pair_rows'),
                 reject(lambda:need(zrecord['count_at_z_min']+1==33*705,'witness'),'changed_archive_coordinate'),
                 reject(lambda:need(admissible([7,7,7]),'invalid local triangle'),'malformed_local_graph')]
    # Explicit invalid attachment is rejected without relying on the malformed fixture control.
    need(not next(r for r in attachments if r['mask']==3)['admissible'],'two neighbors in one triangle forbidden')
    budget()
    save(out/'selected_graph.json',dict(edges=sorted(H),N3_canonical_mask=hmask,Z82_canonical_mask=zmask,
        figure_member='figure_2.png',figure_sha256=hashlib.sha256(fig).hexdigest(),formula_tex=FORMULA,
        tex_member_sha256=hashlib.sha256(raw).hexdigest(),tex_line=line,pdf_formula_page=10,pdf_graph_page=5))
    save(out/'attachments_and_pair_residuals.json',dict(attachments=attachments,pair_residuals=pair_residuals))
    save(out/'archive_overlap.json',dict(coefficients=coeff,selected_affine_record=zrecord,
        combination='one deletion row minus sum of vertex-orbit rows plus sum of pair-orbit rows',
        independent_archived_system_reapproval=False))
    save(out/'controls.json',dict(genuine243_examples=examples,triangles=891,
        disjoint_triangle_pair_cross_edge_histogram=dict(sorted(cross_hist.items())),
        genuine243_N3_control_vacuous=cross_hist[2]==0,corruptions_rejected=corruptions,
        synthetic_local_fixture=dict(parameters_for_six_completed_rows=[99,14,1,2],
            outside_neighborhoods_in_core=chosen,outside_histogram=synthetic_hist,
            full_SRG=False,outside_degrees_incomplete=True)))
    save(out/'correction.json',dict(original_source='acceleration/theory_20261001_reimbayev_z82_overlap.py',
        original_failure='acceleration/results/20261001_reimbayev_z82_overlap/failure.json',
        change='Replace unjustified expected-positive 243 count with exact population/vacuity disclosure; add synthetic LOCAL non-SRG positive.',
        mathematical_predicate_changed=False,old_source_mutated=False))
    source=Path(__file__);spec=source.with_name(source.stem+'_spec.md')
    pins={**PINS,source.relative_to(ROOT).as_posix():sha(source),spec.relative_to(ROOT).as_posix():sha(spec)}
    summary=dict(status='CANDIDATE_REIMBAYEV_Z82_REDUNDANCY_RECORD',created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        selected_identity='z82=(n-6k+18)*n3; target z82=33*n3',target_local_histogram=[33,52,8],
        source_version='arXiv:2608.19410v1, Section 2, unnumbered z82 formula, PDF page 10',
        finding='This selected identity is already a linear combination of the archived extension-row families. No new restriction is supplied.',
        independent_approval=False,all_paper_formulas_approved=False,novelty_claim=False,target_resolution=False,
        native_calls=0,solver_calls=0,ledger_edits=0,archive_modules_imported=False,elapsed_seconds=time.monotonic()-start,
        inputs_sha256=pins,outputs_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in out.iterdir() if p.is_file()})
    save(out/'summary.json',summary);print(json.dumps(summary))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);args=ap.parse_args()
    out=ROOT/args.out;out.mkdir(parents=True,exist_ok=False)
    try: run(out)
    except BaseException as exc:
        save(out/'failure.json',dict(status='FAILED',error=repr(exc),traceback=traceback.format_exc(),source_sha256=sha(__file__)))
        raise
if __name__=='__main__': main()
