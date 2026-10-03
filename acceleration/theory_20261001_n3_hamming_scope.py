"""Bounded candidate scope probe; no universal covering inference from fixtures."""
import argparse, collections, datetime, hashlib, itertools, json, time, traceback, urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_srg243_residual_fixture/'
PINS={B+'adjacency243.json':'5c7c8268b7d62997b5c87a56b11fd673f3f80fcb029b83816179ee8127b8e0d3',
      B+'syndrome_certificate.json':'519aa2861e7a01078bae4abc2ab6f22d76c8ac562097640b3e0ac83ba6cbb9a4',
      'acceleration/results/20261001_reimbayev_z82_overlap_v2/controls.json':'96f1a3a03f284533af661a0c86e2ddcc1530d7d7344f447f6548614a73257e1c'}
def need(q,m):
    if not q: raise ValueError(m)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads((ROOT/p).read_text(encoding='utf-8'))
def save(p,d): p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def reject(fn,name):
    try: fn()
    except (ValueError,AssertionError): return name
    raise ValueError('corruption accepted: '+name)
def check_srg(A,k):
    n=len(A);need(all(len(r)==n for r in A),'shape')
    need(all(type(x) is int and x in (0,1) for r in A for x in r),'binary')
    rows=[sum(x<<j for j,x in enumerate(r)) for r in A]
    need(all(A[i][i]==0 and sum(A[i])==k for i in range(n)),'diagonal/degree')
    for i,j in itertools.combinations(range(n),2):
        need(A[i][j]==A[j][i],'symmetry')
        need((rows[i]&rows[j]).bit_count()==(1 if A[i][j] else 2),'SRG common counts')
    return rows
def bits(v):
    while v:
        x=v&-v;yield x.bit_length()-1;v-=x
def grid_check(A,layout):
    need(len(layout)==9 and len(set(layout))==9,'grid vertices')
    for i,j in itertools.combinations(range(9),2):
        need(A[layout[i]][layout[j]]==int(i//3==j//3 or i%3==j%3),'grid induced edges')
def grid_census(A,k,budget):
    rows=check_srg(A,k);n=len(A)
    def partner(a,b):
        need(A[a][b]==1,'triangle edge')
        c=list(bits(rows[a]&rows[b]));need(len(c)==1,'triangle uniqueness');return c[0]
    squares={}
    for a,c in itertools.combinations(range(n),2):
        if A[a][c]:continue
        b,d=list(bits(rows[a]&rows[c]))
        key=tuple(sorted((a,b,c,d)))
        if key in squares:continue
        e,f,h,g=partner(a,b),partner(d,c),partner(a,d),partner(b,c)
        need(A[e][f] and A[h][g],'N3-free opposite triangle completion')
        i=partner(e,f);layout=[a,b,e,d,c,f,h,g,i]
        grid_check(A,layout);squares[key]=tuple(sorted(layout))
        budget()
    multiplicities=collections.Counter(squares.values())
    return dict(vertices=n,valency=k,a1=1,a2=k-2,c2=2,c3=None,
                square_count=len(squares),grid_count=len(multiplicities),
                grids=[dict(vertices=list(g),squares=s) for g,s in sorted(multiplicities.items())])
def cover243(A,vertices,H):
    need(len(H)==11 and all(len(c)==5 for c in H),'syndrome shape')
    need(H[:5]==[[int(i==j) for j in range(5)] for i in range(5)],'surjective identity minor')
    index={tuple(v):i for i,v in enumerate(vertices)};need(len(index)==243,'all 3^5 images')
    for i,v in enumerate(vertices):
        images=[index[tuple((v[a]+s*c[a])%3 for a in range(5))] for c in H for s in (1,2)]
        need(len(set(images))==22 and set(images)=={j for j,x in enumerate(A[i]) if x},'cover neighbourhood bijection')
    return dict(domain='H(11,3)',codomain_vertices=243,domain_vertices=3**11,
                fibre_size=3**6,neighbourhood_bijections_checked=243,
                proof='linear syndrome map has rank 5 and 22 distinct neighbour increments')
def access(out):
    records=[]
    urls=[('makhnev_1988.pdf','https://www.mathnet.ru/php/getFT.phtml?jrnid=mzm&paperid=4220&what=fullt&option_lang=eng'),
          ('matsumoto_1991.pdf','https://www.kurims.kyoto-u.ac.jp/~kyodo/kokyuroku/contents/pdf/0768-07.pdf')]
    for name,url in urls:
        r=dict(url=url,accessed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),availability='LOCAL_ONLY')
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'Conway99-literature-scope/1.0'})
            with urllib.request.urlopen(req,timeout=20) as response:
                data=response.read(10*1024*1024+1);need(len(data)<=10*1024*1024,'access byte ceiling')
                need(data.startswith(b'%PDF-'),'PDF signature')
                r.update(http_status=response.status,final_url=response.url,headers=dict(response.headers))
            p=out/name;p.write_bytes(data);r.update(outcome='SAVED',path=p.as_posix(),sha256=sha(p),bytes=len(data))
        except Exception as e:r.update(outcome='ACCESS_FAILED',error=repr(e))
        records.append(r)
    return records
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);a=ap.parse_args()
    out=Path(a.out);out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    def budget():need(time.monotonic()-start<60,'finite computation 60s bound')
    try:
        for p,h in PINS.items():need(sha(ROOT/p)==h,'pin '+p)
        raw=read(B+'adjacency243.json');A=raw['adjacency'];H=read(B+'syndrome_certificate.json')['coordinate_syndromes']
        prior=read('acceleration/results/20261001_reimbayev_z82_overlap_v2/controls.json')
        need(prior['disjoint_triangle_pair_cross_edge_histogram'].get('2',0)==0,'prior N3-free control')
        A9=[[int(i!=j and (i//3==j//3 or i%3==j%3)) for j in range(9)] for i in range(9)]
        grids=[grid_census(A9,4,budget),grid_census(A,22,budget)]
        cover=cover243(A,raw['vertex_vectors'],H)
        bad=[r[:] for r in A9];bad[0][1]^=1
        corrupt=[reject(lambda:check_srg(bad,4),'changed adjacency'),
                 reject(lambda:cover243(A,raw['vertex_vectors'],H[:-1]+[H[0]]),'repeated syndrome direction'),
                 reject(lambda:grid_check(A9,[0,1,2,3,4,5,6,8,7]),'wrong grid incidence')]
        arithmetic=[dict(v=v,k=k,d=k//2,domain_size=3**(k//2),divisible=(3**(k//2))%v==0) for v,k in [(9,4),(99,14),(243,22)]]
        need([r['divisible'] for r in arithmetic]==[True,False,True],'cover divisibility controls')
        budget();finite_seconds=time.monotonic()-start
        save(out/'grid_census.json',dict(records=grids,controls=corrupt))
        save(out/'cover_checks.json',dict(explicit_243_cover=cover,conditional_divisibility=arithmetic,universal_cover_from_N3_free='UNKNOWN'))
        literature=access(out);save(out/'source_access.json',literature)
        source=Path(__file__);spec=source.with_name(source.stem+'_spec.md')
        inputs=dict(PINS);inputs[source.relative_to(ROOT).as_posix()]=sha(source);inputs[spec.relative_to(ROOT).as_posix()]=sha(spec)
        save(out/'summary.json',dict(schema='N3_HAMMING_SCOPE_PROBE_V1',status='CANDIDATE_SCOPE_LIMITATION',
             created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),inputs_sha256=inputs,
             finite_seconds=finite_seconds,grid_counts=[r['grid_count'] for r in grids],
             square_counts=[r['square_count'] for r in grids],universal_cover='UNKNOWN',new_target_exclusion=False,
             outputs_sha256={p.as_posix():sha(p) for p in out.iterdir() if p.is_file()},
             scope='finite 9/243 controls and conditional cover arithmetic only; no general covering theorem'))
        print(json.dumps(dict(status='CANDIDATE_SCOPE_LIMITATION',finite_seconds=finite_seconds,grid_counts=[r['grid_count'] for r in grids],source_access=[r['outcome'] for r in literature])))
    except BaseException as e:
        save(out/'failure.json',dict(error=repr(e),traceback=traceback.format_exc()));raise
if __name__=='__main__':main()
