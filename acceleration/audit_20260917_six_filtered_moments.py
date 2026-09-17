"""Independent full-column six-coordinate moment audit; recover large inputs from chunks."""
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
import hashlib
import json
import platform
import subprocess
import sys
import numpy as np
import scipy
from scipy.sparse import load_npz
from tqdm import tqdm
import audit_20260917_partial_matching as h

ROOT=h.ROOT
D=ROOT/'acceleration/results/20260917_six_filtered_moments'
TABLES=ROOT/'acceleration/results/20260917_partial_six_matchings'
OUT=ROOT/'acceleration/results/20260917_independent_review'

def main():
    bindings={}; recovered={}; recovery=[]
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    def digest(p):return h.digest(recovered.get(Path(p),Path(p)))
    def read(p):
        p=Path(p);bindings[h.key(p)]=digest(p)
        return json.loads(recovered.get(p,p).read_bytes())
    chunks=read(D/'chunk_manifest.json')
    for a in chunks['artifacts']:
        h.require(Path(a['source']).name==a['source'],'confined artifact')
        target=ROOT/'build/independent-six-model-recovery'/a['source'];target.parent.mkdir(parents=True,exist_ok=True)
        sha=hashlib.sha256();size=0
        with target.open('xb')as out:
            for part in a['parts']:
                h.require(Path(part['path']).name==part['path'],'confined part')
                p=D/part['path'];bindings[h.key(p)]=h.digest(p)
                h.require(bindings[h.key(p)]==part['sha256']and p.stat().st_size==part['bytes'],'part identity')
                with p.open('rb')as inp:
                    while block:=inp.read(100003):out.write(block);sha.update(block);size+=len(block)
        h.require(size==a['source_bytes']and sha.hexdigest()==a['source_sha256']==h.digest(target),'reconstructed artifact identity')
        recovered[D/a['source']]=target
        recovery.append(dict(source=a['source'],bytes=size,sha256=sha.hexdigest(),parts=len(a['parts']),original_raw_consulted=False,recovered_path=h.key(target)))
    manifest=read(D/'build_manifest.json');summary=read(D/'build_summary.json');meta=read(D/'model.json');read(D/'controls.json')
    for f,v in summary['output_sha256'].items():
        h.require(digest(D/f)==v,'build output binding');bindings[h.key(D/f)]=v
    primary=read(TABLES/'manifest.json');read(TABLES/'summary.json')
    proofpath=OUT/'six_matchings/summary.json';proof=read(proofpath)
    h.require(bindings[h.key(proofpath)]=='051a57b2fc1b5353a6100b949f86674483cff686c4f797f4f1ad8b037d7f3768'and proof['status']=='INDEPENDENT_SIX_COORDINATE_DOMAINS_PASS','complete domain gate')
    filterpath=OUT/'six_coordinate_matching_filter/summary.json';filtered=read(filterpath)
    h.require(bindings[h.key(filterpath)]=='05d4284f04fb5c84491394695c6f56a3e5517302ae95c1885b27592cfed78a7f'and filtered['status']=='INDEPENDENT_SIX_COORDINATE_NEIGHBORHOOD_MATCHING_FILTER_PASS','sound filter gate')
    # Hash-bound reuse of the independently checked inputs, including recovered gzip witnesses.
    for gate in(proof,filtered):
        for f,v in gate['inputs_sha256'].items():
            p=ROOT/f
            alt=next((ROOT/r['recovered_path']for r in filtered['lossless_gzip_recovery']if r['raw_path']==f),p)
            h.require(h.digest(alt)==v,'dependency input changed');bindings[f]=v
            if alt!=p:recovered[p]=alt
    labels=[(2*a+s,2*b+t)for a,b in combinations(range(7),2)for s in range(2)for t in range(2)]
    fixed=set(map(tuple,primary['remaining_fixed_K_edges_outer']));unknown=list(map(tuple,primary['unknown_edges_outer']))
    pairs=list(combinations(range(84),2));pid={p:i for i,p in enumerate(pairs)};eid={p:i for i,p in enumerate(unknown)}
    known=[set()for _ in range(84)]
    for a,b in fixed:known[a].add(b);known[b].add(a)
    rawtables=[[int(s,16)for s in read(TABLES/f'domain_{u:02d}.json')['domain_masks_hex']]for u in range(84)]
    original_offsets=np.cumsum([0]+list(map(len,rawtables))).tolist();retained=[]
    for u,table in enumerate(rawtables):
        row=filtered['records'][u];h.require(row['outer_vertex']==u and row['original_count']==len(table),'filter original population')
        rejected=set(row['rejected_ids']);h.require(len(rejected)==row['rejected_count']and all(0<=i<len(table)for i in rejected),'deletion identities')
        retained.append([i for i in range(len(table))if i not in rejected])
    tables=[[rawtables[u][i]for i in retained[u]]for u in range(84)]
    offsets=np.cumsum([0]+list(map(len,tables))).tolist();n=offsets[-1];hard=84+len(unknown)
    h.require(original_offsets[-1]==879449 and n==712721 and len(fixed)==132 and len(unknown)==2040,'new scope population')
    h.require(meta['retained_original_domain_ids']==retained and meta['original_probability_offsets']==original_offsets and meta['probability_offsets']==offsets,'exact original IDs and offsets')
    h.require(meta['supports']==list(map(list,labels))and meta['fixed_edges']==sorted(map(list,fixed))and meta['unknown_edges']==list(map(list,unknown))and meta['pair_order']==list(map(list,pairs)),'model edge identities')
    actual=load_npz(recovered[D/'integer_augmented_csr.npz'])
    h.require(actual.format=='csr'and actual.has_canonical_format and np.issubdtype(actual.dtype,np.integer)and actual.shape==(5610,719693)==tuple(meta['shape'])and actual.nnz==59380799==meta['nonzeros'],'exact matrix storage')
    h.require(set(map(int,np.unique(actual.data)))=={-1,1},'integer coefficient range')
    columns=actual.tocsc();columns.sort_indices();checked=0
    for u,table in enumerate(tqdm(tables,desc='Independent six moment columns',unit='center')):
        for j,mask in enumerate(table,offsets[u]):
            chosen=set(h.bits(mask));neighbors=known[u]|chosen
            h.require(len(neighbors)==12 and not known[u]&chosen and u not in neighbors,'full raw neighborhood')
            expected={u:1}
            for v in chosen:
                e=tuple(sorted((u,v)));expected[84+eid[e]]=1 if u<v else -1
                if u<v:expected[hard+pid[e]]=1
            for e in combinations(sorted(neighbors),2):
                r=hard+pid[e];h.require(r not in expected,'distinct moment terms');expected[r]=1
            start,end=int(columns.indptr[j]),int(columns.indptr[j+1])
            observed=dict(zip(map(int,columns.indices[start:end]),map(int,columns.data[start:end])))
            h.require(observed==expected and end-start==len(expected),'every integer column from full neighborhood');checked+=len(expected)
    for j in range(6972):
        start,end=int(columns.indptr[n+j]),int(columns.indptr[n+j+1])
        h.require(end-start==1 and int(columns.indices[start])==hard+j%3486 and int(columns.data[start])==(-1 if j<3486 else 1),'slack column');checked+=1
    rhs=[1]*84+[0]*2040+[2-len(set(labels[a])&set(labels[b]))-int((a,b)in fixed)for a,b in pairs]
    h.require(meta['rhs']==rhs and meta['costs']==[0]*n+[1]*6972 and meta['column_lower']==0 and meta['column_upper']is None and meta['all_rows_equalities']is True and checked==actual.nnz,'rhs objective bounds complete')
    # Independent rook9 reconstruction and deliberately damaged coefficients/right sides.
    fixture=read(ROOT/'acceleration/results/20260917_four_matching_moments/controls.json')
    A=[[int(a!=b and(a//3==b//3 or a%3==b%3))for b in range(9)]for a in range(9)]
    h.require(A==fixture['adjacency'],'known-valid rook fixture');controls=[]
    for rec in fixture['records']:
        r=rec['root'];inside={v for v in range(9)if A[r][v]};outer=[v for v in range(9)if v!=r and v not in inside]
        f=set(map(tuple,rec['fixed_edges']));unknown9=set(map(tuple,rec['unknown_edges']));rows=[];b=[]
        for a,c in combinations(range(4),2):
            rows.append([int(A[outer[t]][outer[a]]and A[outer[t]][outer[c]])+int(t==a and(a,c)in unknown9 and A[outer[a]][outer[c]])for t in range(4)])
            b.append(2-sum(A[outer[a]][w]*A[outer[c]][w]for w in inside)-int((a,c)in f))
        h.require(outer==rec['outer']and rows==rec['exact_moment_matrix']and b==rec['rhs']and list(map(sum,rows))==b,'rook exact positive witness')
        bad=[row[:]for row in rows];bad[0][0]+=1;wrong=b[:];wrong[0]+=1
        h.require(list(map(sum,bad))!=b and list(map(sum,rows))!=wrong,'corrupted controls')
        controls.append(dict(root=r,fixed_edges=len(f),positive='PASS',coefficient_corruption='REJECT',RHS_corruption='REJECT'))
    h.require(len(controls)==18 and {(x['root'],x['fixed_edges'])for x in controls}=={(r,k)for r in range(9)for k in(0,1)},'control population')
    for p in(__file__,h.__file__,ROOT/'uv.lock'):bindings[h.key(p)]=h.digest(p)
    h.require(all(digest(ROOT/f)==v for f,v in bindings.items()),'inputs stable')
    report=dict(status='INDEPENDENT_SIX_COORDINATE_FILTERED_FULL_MOMENT_MODEL_PASS',claim_id='C-PARTIAL-K-SIX-COORDINATE-MATCHING-FILTERED-MOMENT-ENCODING',claim_revision=1,recommendation='VERIFIED',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=head,command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,inputs_sha256=bindings,objective=meta['model'],shape=list(actual.shape),nonzeros=actual.nnz,original_probability_columns=879449,retained_original_probability_columns=n,removed_original_probability_columns=166728,hard_simplex_rows=84,hard_reciprocity_rows=2040,soft_moment_rows=3486,all_raw_neighborhood_columns_checked=True,all_bounds_costs_rows_slacks_checked=True,chunk_recovery=recovery,producer_imported=False,controls=controls,scope=primary['scope'],dependencies=[dict(id='C-PARTIAL-K-SIX-COORDINATE-DOMAINS',revision=1,relation='coverage'),dict(id='C-PARTIAL-K-SIX-COORDINATE-NEIGHBORHOOD-MATCHING-FILTER',revision=1,relation='uses_result')],statement='Every SRG completion in this frozen six-coordinate 132-fixed-K/prescribed-zero family induces a zero-objective feasible point in the exact recorded filtered full-neighborhood moment LP.',derivation='Each completion chooses one complete-domain star per center; the sound matching filter preserves each such star. Symmetry gives every hard reciprocity row. The full neighborhood moment counts all common outer neighbors, with unknown adjacency contributed once through the smaller endpoint. The target identity gives common_outer+A_unknown=2-common_inner-B_fixed. Thus every moment slack is zero. No converse is asserted.',shared_components=['Python standard library','NumPy/SciPy exact integer sparse representation and format conversion','tqdm','prior independent artifact helpers','hash-bound prior independent complete domains and matching partition'],limitations=['Necessary conditional relaxation, not an unrestricted normalization or target resolution.','No unfiltered source matrix exists; all retained coefficients were freshly reconstructed directly.','This check alone establishes no positive bound or family exclusion.'])
    out=OUT/'six_filtered_moments.json'
    with out.open('x')as f:json.dump(report,f,indent=2)
    print(report['status'],h.digest(out))

if __name__=='__main__':main()
