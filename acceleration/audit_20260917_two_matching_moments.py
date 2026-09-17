"""Reconstruct every two-coordinate integer LP coefficient from complete neighborhoods."""
from array import array
from datetime import datetime,timezone
from itertools import combinations
import json
import platform
import subprocess
import sys
import numpy as np
import scipy
from scipy.sparse import csc_matrix,load_npz
import audit_20260917_partial_matching as h

ROOT=h.ROOT;D=ROOT/'acceleration/results/20260917_two_matching_moments';TABLES=ROOT/'acceleration/results/20260917_partial_two_matchings'
def main():
    bindings={};head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    def read(p):
        bindings[h.key(p)]=h.digest(p);d=json.loads(p.read_bytes())
        for f,v in d.get('inputs_sha256',{}).items():h.require(h.digest(ROOT/f)==v,'changed input');bindings[h.key(ROOT/f)]=v
        return d
    manifest=read(D/'build_manifest.json');summary=read(D/'build_summary.json');meta=read(D/'model.json');ctrl=read(D/'controls.json');primary=read(TABLES/'manifest.json');read(TABLES/'summary.json')
    proofpath=ROOT/'acceleration/results/20260917_independent_review/two_matchings/summary.json';proof=read(proofpath)
    h.require(proof['status']=='INDEPENDENT_TWO_COORDINATE_DOMAINS_PASS'and proof['domain_choices']==89308,'complete domain gate')
    for f,v in summary['output_sha256'].items():h.require(h.digest(D/f)==v,'build output changed');bindings[h.key(D/f)]=v
    for name in ('TWO_COORDINATE_MOMENT_MODEL.md',):readpath=D/name;bindings[h.key(readpath)]=h.digest(readpath)
    labels=[(2*a+s,2*b+t)for a,b in combinations(range(7),2)for s in range(2)for t in range(2)]
    B=np.zeros((99,99),dtype=np.int64)
    def add(a,b):B[a,b]=B[b,a]=1
    for v in range(1,15):add(0,v)
    for v in range(1,15,2):add(v,v+1)
    for u,pair in enumerate(labels,15):
        for s in pair:add(u,s+1)
    fixed=set(map(tuple,primary['remaining_fixed_K_edges_outer']))
    for a,b in fixed:add(a+15,b+15)
    unknown=list(map(tuple,primary['unknown_edges_outer']));eid={e:i for i,e in enumerate(unknown)};pairs=list(combinations(range(84),2));pid={e:i for i,e in enumerate(pairs)}
    tables=[[int(s,16)for s in read(TABLES/f'domain_{u:02d}.json')['domain_masks_hex']]for u in range(84)];offsets=np.cumsum([0]+list(map(len,tables))).tolist();n=offsets[-1];hard=84+len(unknown)
    h.require(n==89308 and len(fixed)==156 and len(unknown)==1800 and meta['supports']==list(map(list,labels))and meta['fixed_edges']==sorted(map(list,fixed))and meta['unknown_edges']==list(map(list,unknown))and meta['pair_order']==list(map(list,pairs))and meta['probability_offsets']==offsets,'exact model indexing')
    rows=array('i');values=array('b');ptr=[0]
    for u,table in enumerate(tables):
        known={v for v in range(84)if B[u+15,v+15]}
        for mask in table:
            chosen=set(h.bits(mask));neighbors=known|chosen;h.require(len(neighbors)==12 and not known&chosen and u not in neighbors,'full outer neighborhood')
            terms=[(u,1)]+[(84+eid[tuple(sorted((u,v)))],1 if u<v else -1)for v in chosen]
            terms.extend((hard+pid[e],1)for e in combinations(sorted(neighbors),2));terms.extend((hard+pid[u,v],1)for v in chosen if u<v)
            terms.sort();h.require(len({r for r,c in terms})==len(terms),'duplicate row contribution')
            rows.extend(r for r,c in terms);values.extend(c for r,c in terms);ptr.append(len(values))
    for sign in(-1,1):
        for j in range(3486):rows.append(hard+j);values.append(sign);ptr.append(len(values))
    expected=csc_matrix((np.asarray(values,dtype=np.int64),np.asarray(rows),np.asarray(ptr)),shape=(5370,96280)).tocsr();expected.sort_indices()
    actual=load_npz(D/'integer_augmented_csr.npz');actual.sum_duplicates();actual.sort_indices()
    h.require(np.issubdtype(actual.dtype,np.integer)and actual.shape==expected.shape==tuple(meta['shape']),'matrix shape/type')
    for field in('indptr','indices','data'):h.require(np.array_equal(getattr(expected,field),getattr(actual,field)),'exact complete CSR '+field)
    rhs=[1]*84+[0]*1800+[2-int(B[a+15,b+15])-int(B[a+15,:15]@B[b+15,:15])for a,b in pairs]
    h.require(meta['rhs']==rhs and meta['costs']==[0]*n+[1]*6972 and meta['column_lower']==0 and meta['column_upper']is None and meta['all_rows_equalities']is True and meta['nonzeros']==actual.nnz==7315157,'full objective/bounds/rhs')
    A=ctrl['adjacency'];rook=[[int(i!=j and(i//3==j//3 or i%3==j%3))for j in range(9)]for i in range(9)];h.require(A==rook,'rook fixture identity');controls=[]
    for record in ctrl['records']:
        r=record['root'];inside={v for v in range(9)if A[r][v]};outer=[v for v in range(9)if v!=r and v not in inside];h.require(outer==record['outer'],'rook map');f=set(map(tuple,record['fixed_edges']));unknown9=set(map(tuple,record['unknown_edges']));matrix=[];b=[]
        for a,c in combinations(range(4),2):
            matrix.append([int(A[outer[t]][outer[a]]and A[outer[t]][outer[c]])+int(t==a and(a,c)in unknown9 and A[outer[a]][outer[c]])for t in range(4)])
            b.append(2-sum(A[outer[a]][w]*A[outer[c]][w]for w in inside)-int((a,c)in f))
        h.require(matrix==record['exact_moment_matrix']and b==record['rhs']and list(map(sum,matrix))==b,'rook exact witness')
        corrupted=[row[:]for row in matrix];corrupted[0][0]+=1;bad=b.copy();bad[0]+=1;h.require(list(map(sum,corrupted))!=b and list(map(sum,matrix))!=bad,'corrupt controls')
        controls.append(dict(root=r,fixed_edges=len(f),positive='PASS',corrupted_coefficient='REJECT',corrupted_rhs='REJECT'))
    h.require(len(controls)==18 and {(r['root'],r['fixed_edges'])for r in controls}=={(r,k)for r in range(9)for k in(0,1)},'all control cases')
    for p in(__file__,h.__file__,ROOT/'uv.lock'):bindings[h.key(p)]=h.digest(p)
    h.require(all(h.digest(ROOT/f)==v for f,v in bindings.items()),'artifact changed')
    report=dict(status='INDEPENDENT_TWO_COORDINATE_FULL_MOMENT_MODEL_PASS',claim_id='C-PARTIAL-K-TWO-COORDINATE-FULL-MOMENT-ENCODING',claim_revision=1,recommendation='VERIFIED',statement='Every SRG completion in the frozen two-coordinate partial-K scope induces a zero-objective feasible point in this exact full-neighborhood moment LP; no converse claimed.',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=head,command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,inputs_sha256=bindings,objective=meta['model'],shape=[5370,96280],nonzeros=7315157,probability_columns=n,hard_simplex_rows=84,hard_reciprocity_rows=1800,soft_moment_equalities=3486,complete_augmented_matrix_and_bounds_checked=True,controls=controls,producer_imported=False,dependency=dict(id='C-PARTIAL-K-TWO-COORDINATE-DOMAINS',revision=1,relation='uses_result'),scope=primary['scope'],derivation='A completion chooses exactly one admissible local star at each outer center. Reciprocity equates two representations of each unknown edge. Pair moments count all common outer neighbors through full center neighborhoods; adding the smaller-endpoint unknown edge marginal gives common_outer+A_unknown = 2-common_inner-B_fixed. Consequently all moment slacks can vanish. The converse is not needed.',shared_components=['Python standard library','NumPy/SciPy exact integer sparse storage','prior independent full99/domain artifact helpers'],limitations=['Necessary relaxation only; no new two-coordinate feasibility or exclusion certificate.','All89308 original new domains used; no matching or pair filter.','No unrestricted target resolution.'])
    out=ROOT/'acceleration/results/20260917_independent_review/two_matching_moments.json'
    with out.open('x')as f:json.dump(report,f,indent=2)
    print(report['status'],h.digest(out))
if __name__=='__main__':main()
