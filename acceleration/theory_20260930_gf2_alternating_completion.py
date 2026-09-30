"""Exact, bounded discovery controls; no producer imports and no solver calls."""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import random
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'acceleration/results/20260930_'
SPEC = 'acceleration/theory_20260930_gf2_alternating_completion_spec.md'
DOC = 'docs/DERIVATION_20260930_GF2_ALTERNATING_COMPLETION.md'
PINS = {
 PREFIX+'srg243_residual_fixture/triangle_blocks.json':'3f8dfa3803d6a5db8146dd24a0857477e1aa061ab10dac0f9e6e564aabc86439',
 PREFIX+'srg243_residual_fixture/adjacency243.json':'5c7c8268b7d62997b5c87a56b11fd673f3f80fcb029b83816179ee8127b8e0d3',
 PREFIX+'independent_review/srg243_residual_fixture/summary.json':'28bbd97b8e69515c3eb0345e5aa2db12debfaa8a44e83b2e3487342104c5d50e',
 PREFIX+'connected_identity_cores/core_00.json':'3d4ad2d5b8ff92ca3d7761ac79e3651e306052897c3327b4eec87d7a85dabe81',
 PREFIX+'connected_identity_cores/core_01.json':'23fb79efbc42fcaf7d54edb32311703be47fa96014a1c46ed00859a0753576e4',
 PREFIX+'connected_identity_cores/core_02.json':'40c23054a9276039b0dc1320594f102ae65d06c8e2c819a31d6600c3ee279eeb',
 PREFIX+'connected_identity_cores/core_03.json':'cdd61bb140888090f092af7bbc3dbc40399f8e06bb3b41781dcfba22f0f701f1',
 PREFIX+'hadamard20_support/six_prism.json':'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',
 PREFIX+'factor_annealer_pilot/shift6_T1/best_00000.json':'7aa0712c8a487b13924cdb668f93ffd3a3a3b2472eadcbef90474fc0f0af1675',
 PREFIX+'factor_annealer_pilot/six_prism_T1/best_00000.json':'13767cddc97880f9568a3ba7f72bf22fb70f001f41851050a7dcda7fae11f393',
 'docs/AUDIT_20260930_TARGET_MODULAR_RANKS.md':'c819ec41287a1a5394d84e2031b6cd2ba564ed8c9771082363dc46ad11a894ed',
 'docs/AUDIT_20260930_TRIANGLE_GF2_MAXRANK.md':'fc831702c706566685f4078cf4906c5f032c3c673e6ebe489b24e8713b11b342',
 'docs/AUDIT_20260930_FIVE_CORE_MODULAR_GRAM.md':'a22f72f34236c7b046aaf9f024bd124d9d808ae0e56ee23ab525472e87de270b',
 'docs/AUDIT_20260930_TRIANGLE_RESIDUAL60.md':'ba511adcd3e873ca39e04afef50d690f4c41d33260ef9e9cf8851936b3d22661',
}
ARCHIVE = ['wave102-prism-incidence-code/derivation.md',
           'wave131-binary-lcd-enumerator/derivation.md',
           'wave142-interlace-isotropic/derivation.md',
           'wave140-arf-sign-lattice/derivation.md']
ARCHIVE_COMMIT = '85e705cc6c2a14d123120c93a847e30aaab1789e'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def save(path, obj):
    Path(path).write_text(json.dumps(obj, sort_keys=True, separators=(',', ':'))+'\n', encoding='utf-8')

def read(path):
    return json.loads((ROOT/path).read_text(encoding='utf-8'))

def bits(row):
    return sum((int(v)&1)<<j for j,v in enumerate(row))

def unbits(x, n):
    return [(x>>j)&1 for j in range(n)]

def transpose(a):
    return list(map(list, zip(*a))) if a else []

def rref(rows, width):
    v=list(rows); piv=[]; k=0
    for j in range(width):
        t=next((t for t in range(k,len(v)) if (v[t]>>j)&1), None)
        if t is None: continue
        v[k],v[t]=v[t],v[k]
        for i in range(len(v)):
            if i!=k and (v[i]>>j)&1: v[i]^=v[k]
        piv.append(j);k+=1
    kernel=[]
    for j in range(width):
        if j in piv: continue
        x=1<<j
        for i,p in enumerate(piv):
            if (v[i]>>j)&1: x|=1<<p
        kernel.append(x)
    assert all(all((x&y).bit_count()%2==0 for y in rows) for x in kernel)
    return {'rank':k,'pivot_columns':piv,'reduced_rows':v[:k], 'kernel_basis':kernel,'width':width}

def rank(a):
    return rref([bits(x) for x in a],len(a[0]) if a else 0)['rank']

def combine(rows, mask):
    out=0
    for i,row in enumerate(rows):
        if (mask>>i)&1: out^=row
    return out

def representation(rows, target):
    base={}
    for i,row in enumerate(rows):
        x=row;c=1<<i
        while x:
            p=x.bit_length()-1
            if p not in base:
                base[p]=(x,c);break
            x^=base[p][0];c^=base[p][1]
    c=0;x=target
    while x:
        p=x.bit_length()-1
        if p not in base: return None
        x^=base[p][0];c^=base[p][1]
    assert combine(rows,c)==target
    return c

def product(a,b):
    bt=[bits(x) for x in transpose(b)]
    return [[(bits(row)&col).bit_count()%2 for col in bt] for row in a]

def alternating(a):
    return all(a[i][i]==0 and all(a[i][j]==a[j][i] for j in range(len(a))) for i in range(len(a)))

def alt_matrix(n,mask):
    a=[[0]*n for _ in range(n)]
    for k,(i,j) in enumerate(itertools.combinations(range(n),2)):
        a[i][j]=a[j][i]=(mask>>k)&1
    return a

def completion_conditions(f,h):
    a=len(f);m=len(f[0]);fr=[bits(x) for x in f];hr=[bits(x) for x in h]
    ker=rref([bits(x) for x in transpose(f)],a)['kernel_basis']
    kernel_condition=all(combine(hr,x)==0 for x in ker)
    fh=product(f,transpose(h)); form_condition=alternating(fh)
    hj_zero=all(x.bit_count()%2==0 for x in hr)
    j_preimage=representation(fr,(1<<m)-1)
    j_image_zero=j_preimage is None or combine(hr,j_preimage)==0
    return {'kernel_condition':kernel_condition,'FHt_alternating':form_condition,
            'alternating_solution':kernel_condition and form_condition,
            'H_times_one_zero':hj_zero,'one_preimage':j_preimage,
            'one_prescribed_image_zero':j_image_zero,
            'even_degree_alternating_solution':kernel_condition and form_condition and hj_zero and j_image_zero}

def block(b,e,d):
    return [b[i]+e[i] for i in range(len(b))]+[transpose(e)[i]+d[i] for i in range(len(d))]

def controls(out):
    span_controls=[]
    for mask in range(64):
        rows=[mask&7,(mask>>3)&7]
        span={combine(rows,c) for c in range(4)}
        got=rref(rows,3)['rank'];assert len(span)==1<<got
        span_controls.append([mask,got,len(span)])
    matrices=[[[((mask>>(i*3+j))&1) for j in range(3)] for i in range(2)] for mask in range(64)]
    ds=[alt_matrix(3,k) for k in range(8)]
    comp=[]
    for fm,f in enumerate(matrices):
        actual={}
        for k,d in enumerate(ds):
            h=product(f,d);hm=sum(h[i][j]<<(3*i+j) for i in range(2) for j in range(3))
            actual.setdefault(hm,[]).append(k)
        for hm,h in enumerate(matrices):
            c=completion_conditions(f,h);hits=actual.get(hm,[])
            assert c['alternating_solution']==bool(hits)
            even=[k for k in hits if all(sum(row)%2==0 for row in ds[k])]
            assert c['even_degree_alternating_solution']==bool(even)
            comp.append({'F':fm,'H':hm,'conditions':c,'alternating_D_masks':hits,'even_D_masks':even})
    bounds=[]
    for bm in range(8):
        b=alt_matrix(3,bm);rb=rank(b)
        for em in range(64):
            e=[[((em>>(2*i+j))&1) for j in range(2)] for i in range(3)]
            s=rank([b[i]+e[i] for i in range(3)]);lower=2*s-rb
            rr=[rank(block(b,e,alt_matrix(2,k))) for k in range(2)]
            assert min(rr)==lower
            bounds.append([bm,em,rb,s,lower,rr])
    f=[[1,1,0,0],[0,0,1,1]];h=f
    c=completion_conditions(f,h)
    assert c['alternating_solution'] and not c['even_degree_alternating_solution']
    found=[k for k in range(64) if product(f,alt_matrix(4,k))==h]
    assert found and not any(all(sum(row)%2==0 for row in alt_matrix(4,k)) for k in found)
    generic={'F':f,'H':h,'conditions':c,'all_alternating_D_masks':found,'triangle_Gram_factor':False}
    # These explicit generic failures establish the need for each compatibility condition.
    bad=[([[0,0]],[[1,0]],'kernel_condition'),
         ([[1,0]],[[1,0]],'FHt_alternating'),
         ([[1,0],[0,1]],[[0,1],[0,0]],'FHt_alternating')]
    rejected=[]
    for ff,hh,key in bad:
        z=completion_conditions(ff,hh);assert not z[key];rejected.append({'F':ff,'H':hh,'failed':key})
    assert not alternating([[1,0],[0,0]]) and not alternating([[0,1],[0,0]])
    save(out/'completion_controls.json',comp)
    save(out/'rank_controls.json',{'span':span_controls,'block_bound':bounds})
    save(out/'generic_even_degree_counterexample.json',generic)
    save(out/'negative_controls.json',{'incompatible_F_H':rejected,'loop_and_asymmetry_rejected':True})
    return {'all_F_H_2_by_3':len(comp),'all_B3_E3_by2':len(bounds),'all_rank2_by3':len(span_controls),
            'generic_even_degree_adds_obstruction':True}

def triangle_b(c):
    n=len(c)//3;p=3+3*n
    b=[[0]*p for _ in range(p)]
    for i in range(3):
        for j in range(3):b[i][j]=int(i!=j)
        for u in range(n):b[i][3+i*n+u]=b[3+i*n+u][i]=1
    for i in range(3*n):
        for j in range(3*n):b[3+i][3+j]=c[i][j]
    return b

def gram_target(c):
    n=len(c)//3; cr=[bits(x) for x in c]
    return [[n*int(i==j)-c[i][j]-(cr[i]&cr[j]).bit_count()+2-int(i//n==j//n)
             for j in range(3*n)] for i in range(3*n)]

def local_cap(b):
    br=[bits(x) for x in b];viol=[]
    for i,j in itertools.combinations(range(len(b)),2):
        common=(br[i]&br[j]).bit_count();cap=2-b[i][j]
        if common>cap:viol.append([i,j,common,cap])
    return {'passes':not viol,'violations':viol}

def check_core(c):
    n=len(c)//3
    assert n%2==0 and alternating(c)
    assert all(sum(c[i][g*n:(g+1)*n])==1 for i in range(3*n) for g in range(3))
    g=gram_target(c);gp=[[x%2 for x in row] for row in g]
    ic=[[c[i][j]^int(i==j) for j in range(3*n)] for i in range(3*n)]
    commute=product(c,gp)==product(gp,c);form=product(gp,ic)
    assert commute and alternating(form)
    b=triangle_b(c); rb=rref([bits(x) for x in b],len(b));rc=rref([bits(x) for x in c],len(c))
    kr=[]
    for k in range(3):
        v=7+sum(1<<(3+k*n+j) for j in range(n))
        assert all((bits(row)&v).bit_count()%2==0 for row in b);kr.append(v)
    return {'C':c,'B':b,'n':n,'C_rank_certificate':rc,'B_rank_certificate':rb,
            'three_common_kernel_candidates':kr,'local_cap':local_cap(b),
            'G_commutes_C':commute,'G_times_I_plus_C_alternating':True,
            'full_factor_available':False,'bound_ceiling_if_F_even_cell_sums':6*n-rb['rank'],
            'conditional_rank54_test_vacuous':n==12 and rb['rank']>=18}

def make_core(matchings,p):
    n=len(p);c=[[0]*(3*n) for _ in range(3*n)]
    def edge(i,j):c[i][j]=c[j][i]=1
    for k in range(3):
        for u,v in enumerate(matchings[k]):edge(k*n+u,k*n+v)
    for u in range(n):
        edge(u,n+u);edge(u,2*n+u);edge(n+u,2*n+p[u])
    return c

def matching(rng,n):
    order=list(range(n));rng.shuffle(order);m=[None]*n
    for i in range(0,n,2):m[order[i]]=order[i+1];m[order[i+1]]=order[i]
    return m

def factor_diagnostic(c,f):
    n=len(c)//3;m=len(f[0]);b=triangle_b(c);e=[[0]*m for _ in range(3)]+f
    r=rank(b);s=rank([b[i]+e[i] for i in range(len(b))])
    fr=[bits(x) for x in f];g=gram_target(c)
    mismatches=[[i,j,(fr[i]&fr[j]).bit_count(),g[i][j]] for i in range(3*n) for j in range(3*n)
                if (fr[i]&fr[j]).bit_count()!=g[i][j]]
    h=[unbits(fr[i]^combine(fr,bits(c[i])),m) for i in range(3*n)]
    cells=all(sum(f[k*n+i][j] for i in range(n))==2 for k in range(3) for j in range(m))
    common=True
    for k in range(3):
        v=7+sum(1<<(3+k*n+j) for j in range(n))
        common &= all((bits(col)&v).bit_count()%2==0 for col in transpose(e))
    if cells:assert common and s<=3*n
    be=[b[i]+e[i] for i in range(len(b))]
    topid=product(be,transpose(be))==b
    return {'n':n,'outside':m,'rank_F':rank(f),'rank_B':r,'rank_B_E':s,
            'completion_rank_lower_bound':2*s-r,'rank_B_E_certificate':rref([bits(x) for x in be],len(be[0])),
            'integer_Gram_mismatch_count':len(mismatches),'first_Gram_mismatches':mismatches[:12],
            'exact_two_per_cell_column':cells,'three_common_kernel_vectors_valid':common,
            'top_binary_projector_identity':topid,'mixed_completion':completion_conditions(f,h)}

def graph_check(a,k):
    assert alternating(a) and all(sum(row)==k for row in a)
    ar=[bits(x) for x in a]
    for i in range(len(a)):
        for j in range(len(a)):
            assert (ar[i]&ar[j]).bit_count()==(k-2)*int(i==j)-a[i][j]+2
    return {'ordered_integer_entries':len(a)**2,'binary_rank':rank(a),'vertices':len(a),'degree':k}

def run(out,started):
    def limit():
        if time.monotonic()-started>120:raise TimeoutError('cooperative 120-second allocation')
    ctrl=controls(out);limit()
    d=read(PREFIX+'srg243_residual_fixture/triangle_blocks.json')
    raw=read(PREFIX+'srg243_residual_fixture/adjacency243.json')['adjacency']
    full=graph_check(raw,22)
    c=d['cubic_core60'];f=d['factor60x180'];res=d['residual180x180'];b=triangle_b(c)
    assert b==d['core_adjacency63']
    a=block(b,[[0]*180 for _ in range(3)]+f,res)
    order=d['canonical_order_original_vertex_ids'];assert sorted(order)==list(range(243))
    assert a==[[raw[i][j] for j in order] for i in order]
    fd=factor_diagnostic(c,f);assert fd['integer_Gram_mismatch_count']==0
    assert fd['mixed_completion']['even_degree_alternating_solution']
    fr=[bits(x) for x in f];h=[unbits(fr[i]^combine(fr,bits(c[i])),180) for i in range(60)]
    assert product(f,res)==h and alternating(res) and all(sum(row)%2==0 for row in res)
    assert fd['completion_rank_lower_bound']<=full['binary_rank']==110
    save(out/'srg243.json',{'graph':full,'factor':fd,'actual_D_mixed_even_alternating':True,
                           'full_integer_graph_and_literal_relabelling_checked':True})
    bad=[row[:] for row in raw];bad[0][1]^=1
    try:graph_check(bad,22)
    except AssertionError:pass
    else:raise AssertionError('corrupt graph accepted')
    ff=[row[:] for row in f];ff[0][0]^=1
    assert factor_diagnostic(c,ff)['integer_Gram_mismatch_count']>0
    save(out/'genuine_fixture_corruptions.json',{'one_entry_graph_rejected':True,'one_entry_F_Gram_rejected':True})
    limit()
    cases=[]
    for k in range(4):
        x=read(PREFIX+f'connected_identity_cores/core_{k:02}.json');z=check_core(x['core_adjacency'])
        assert z['B']==x['full39_adjacency'] and z['local_cap']['passes']
        z['label']=f'connected_{k:02}';cases.append(z)
    x=read(PREFIX+'hadamard20_support/six_prism.json');z=check_core(x['core_adjacency']);z['label']='six_prism';cases.append(z)
    standard=[i^1 for i in range(12)];z=check_core(make_core([standard]*3,standard));z['label']='six_K3_3_deliberately_invalid'
    assert not z['local_cap']['passes'];cases.append(z)
    rng=random.Random(20260930)
    for k in range(64):
        mm=[matching(rng,12) for _ in range(3)];p=list(range(12));rng.shuffle(p)
        z=check_core(make_core(mm,p));z.update(label=f'deterministic_scaffold_{k:02}',matchings=mm,P=p);cases.append(z)
    save(out/'core_diagnostics.json',cases);limit()
    local=[]
    for name in ['shift6','six_prism']:
        p=PREFIX+f'factor_annealer_pilot/{name}_T1/best_00000.json';x=read(p)
        z=factor_diagnostic(x['core_adjacency'],x['factor']);z.update(label=name,input_path=p,full_factor_claimed=False)
        assert z['integer_Gram_mismatch_count']>0;local.append(z)
    save(out/'local_nonfactor_diagnostics.json',local)
    result={'status':'CANDIDATE_GF2_ALTERNATING_COMPLETION_AND_BLOCK_RANK_DIAGNOSTIC',
            'controls':ctrl,'genuine243':{'rank_A':full['binary_rank'],'rank_B':fd['rank_B'],'rank_B_E':fd['rank_B_E'],
            'completion_lower_bound':fd['completion_rank_lower_bound'],'rank_F':fd['rank_F']},
            'core_ranks':[{'label':z['label'],'rank_B':z['B_rank_certificate']['rank'],'rank_C':z['C_rank_certificate']['rank'],
             'local_caps_pass':z['local_cap']['passes'],'rank54_bound_automatically_passes_if_factor':z['conditional_rank54_test_vacuous']} for z in cases],
            'local_fixtures_are_not_full_factors':True,'independent_approval':False,'target_resolution':False,
            'new_universal_rank_lower_bound_claimed':False,'projector_completion_claimed':False,
            'elapsed_seconds':time.monotonic()-started,'artifact_availability':'LOCAL_ONLY'}
    return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);args=ap.parse_args()
    out=Path(args.out).resolve();out.mkdir(parents=True,exist_ok=False);started=time.monotonic()
    try:
        actual={}
        for p,h in PINS.items():
            actual[p]=sha(ROOT/p);assert actual[p]==h,(p,actual[p],h)
        for p in [SPEC,DOC,Path(__file__).resolve().relative_to(ROOT).as_posix(),'uv.lock','pyproject.toml']:
            actual[p]=sha(ROOT/p)
        archive=[]
        for rel in ARCHIVE:
            p='external_conway99_research/attempts/'+rel
            blob=subprocess.run(['git','-C',str(ROOT/'external_conway99_research'),'show',ARCHIVE_COMMIT+':attempts/'+rel],capture_output=True,check=True).stdout
            assert (ROOT/p).read_bytes()==blob,(p,'immutable archive mismatch')
            actual[p]=sha(ROOT/p);archive.append({'path':p,'sha256':actual[p],'commit':ARCHIVE_COMMIT})
        save(out/'manifest.json',{'source_frozen_before_controls':True,'inputs_sha256':actual,'archive':archive,
                                  'command':sys.argv,'cwd':str(Path.cwd()),'budget_seconds':120,'imports':'Python standard library only'})
        result=run(out,started);result['inputs_sha256']=actual
        result['outputs_sha256']={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(out.iterdir()) if p.is_file()}
        save(out/'summary.json',result)
        print(json.dumps({'status':result['status'],'elapsed_seconds':result['elapsed_seconds'],'summary_sha256':sha(out/'summary.json'),'genuine243':result['genuine243']}))
    except Exception as exc:
        save(out/'failure.json',{'status':'PRESERVED_FAILURE_OR_PARTIAL','type':type(exc).__name__,'message':str(exc),
                                'source_sha256':sha(__file__),'elapsed_seconds':time.monotonic()-started})
        raise

if __name__=='__main__':main()
