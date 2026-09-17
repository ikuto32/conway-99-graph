"""Independent full-neighborhood column reconstruction of the moment LP."""
from array import array
from datetime import datetime,timezone
from itertools import combinations
import json
from pathlib import Path
import platform
import sys
import time
import numpy as np
from scipy.sparse import csc_matrix,load_npz
from tqdm import tqdm
import audit_20260917_partial_matching as scope

ROOT=scope.ROOT
D=ROOT/'acceleration/results/20260917_partial_matching_moments'

def main():
    tick=time.perf_counter();bindings={}
    def read(p):
        p=Path(p);bindings[scope.key(p)]=scope.digest(p);d=json.loads(p.read_bytes())
        for f,h in d.get('inputs_sha256',{}).items():scope.require(scope.digest(ROOT/f)==h,'input changed');bindings[f]=h
        return d
    out=ROOT/'acceleration/results/20260917_independent_review/partial_moments.json';scope.require(not out.exists(),'preserve audit')
    for p in (__file__,scope.__file__,ROOT/'uv.lock'):bindings[scope.key(p)]=scope.digest(p)
    manifest=read(D/'manifest.json');meta=read(D/'model.json');summary=read(D/'summary.json');numeric=read(D/'numeric_lp.json');bound=read(D/'exact_support_bound.json');controls=read(D/'controls.json')
    for f,h in summary['output_sha256'].items():scope.require(scope.digest(D/f)==h,'output changed');bindings[scope.key(D/f)]=h
    primary=read(scope.D/'manifest.json');caps=read(scope.D/'linear_caps.json')
    proof=read(ROOT/'acceleration/results/20260917_independent_review/partial_matching/summary.json')
    scope.require(proof['status']=='INDEPENDENT_PARTIAL_K_DOMAINS_AND_LINEAR_CAPS_PASS'and scope.digest(ROOT/'acceleration/results/20260917_independent_review/partial_matching/summary.json')=='ed1d5b464466562cff722e45593095ec89c63bda761cfa7f784994abfc308b17','complete domain dependency')
    tables=[[int(s,16)for s in read(scope.D/f'domain_{u:02d}.json')['domain_masks_hex']]for u in range(84)]
    B=np.zeros((99,99),dtype=np.int64)
    def add(u,v):B[u,v]=B[v,u]=1
    for v in range(1,15):add(0,v)
    for v in range(1,15,2):add(v,v+1)
    labels=[(2*a+s,2*b+t)for a,b in combinations(range(7),2)for s in range(2)for t in range(2)]
    for u,p in enumerate(labels,15):
        for s in p:add(u,s+1)
    fixed=set(map(tuple,primary['remaining_fixed_K_edges_outer']))
    for u,v in fixed:add(u+15,v+15)
    unknown=list(map(tuple,caps['variable_edges']));eid={e:i for i,e in enumerate(unknown)}
    pairs=list(combinations(range(84),2));pid={p:i for i,p in enumerate(pairs)}
    offsets=np.cumsum([0]+list(map(len,tables))).tolist();n=offsets[-1]
    scope.require(n==54478 and len(unknown)==1740 and meta['probability_offsets']==offsets and meta['unknown_edges']==list(map(list,unknown))and meta['pair_order']==list(map(list,pairs)),'model indexing')
    row_ids=array('i');values=array('b');colptr=[0]
    for u,table in tqdm(list(enumerate(tables)),desc='Independent moment columns',unit='center'):
        known={v for v in range(84)if B[u+15,v+15]}
        for mask in table:
            selected=set(scope.bits(mask));neighbors=known|selected
            scope.require(u not in neighbors and len(neighbors)==12 and not known&selected,'full outer neighborhood')
            terms=[(u,1)]
            for v in selected:
                e=(min(u,v),max(u,v));terms.append((84+eid[e],1 if u<v else -1))
            # Contribution of this complete center neighborhood to EVERY
            # outer-pair common-neighbor count, including variable-variable terms.
            terms.extend((1824+pid[e],1)for e in combinations(sorted(neighbors),2))
            terms.extend((1824+pid[u,v],1)for v in selected if u<v)
            terms.sort();scope.require(len({r for r,c in terms})==len(terms),'unexpected duplicate column row')
            row_ids.extend(r for r,c in terms);values.extend(c for r,c in terms);colptr.append(len(values))
    for sign in (-1,1):
        for j in range(3486):row_ids.append(1824+j);values.append(sign);colptr.append(len(values))
    expected=csc_matrix((np.asarray(values,dtype=np.int64),np.asarray(row_ids),np.asarray(colptr)),shape=(5310,61450)).tocsr()
    actual=load_npz(D/'integer_augmented_csr.npz');actual.sum_duplicates();actual.sort_indices();expected.sort_indices()
    scope.require(np.issubdtype(actual.dtype,np.integer)and actual.shape==expected.shape==tuple(meta['shape']),'integer matrix shape')
    for field in ('indptr','indices','data'):scope.require(np.array_equal(getattr(actual,field),getattr(expected,field)),'full augmented CSR '+field)
    rhs=[1]*84+[0]*1740+[2-int(B[a+15,b+15])-int(B[a+15,:15]@B[b+15,:15])for a,b in pairs]
    scope.require(meta['rhs']==rhs and meta['costs']==[0]*n+[1]*6972 and meta['column_lower']==0 and meta['column_upper']is None and meta['all_rows_equalities']is True,'objective/bounds/RHS')
    scope.require(meta['nonzeros']==actual.nnz==4425506,'nonzero count')
    A=controls['adjacency'];rook=[[int(i!=j and(i//3==j//3 or i%3==j%3))for j in range(9)]for i in range(9)]
    scope.require(A==rook,'rook fixture identity');control_results=[]
    for record in controls['records']:
        r=record['root'];inner={v for v in range(9)if A[r][v]};outer=[v for v in range(9)if v!=r and v not in inner]
        scope.require(outer==record['outer'],'rook outside map');f=set(map(tuple,record['fixed_edges']));unknown9=set(map(tuple,record['unknown_edges']))
        matrix=[];rhs9=[]
        for a,b in combinations(range(4),2):
            matrix.append([int(A[outer[t]][outer[a]]and A[outer[t]][outer[b]])+int(t==a and(a,b)in unknown9 and A[outer[a]][outer[b]])for t in range(4)])
            rhs9.append(2-sum(A[outer[a]][w]*A[outer[b]][w]for w in inner)-int((a,b)in f))
        scope.require(matrix==record['exact_moment_matrix']and rhs9==record['rhs']and list(map(sum,matrix))==rhs9,'rook exact moment witness')
        bad=[row[:]for row in matrix];bad[0][0]+=1;bad_rhs=rhs9.copy();bad_rhs[0]+=1
        scope.require(list(map(sum,bad))!=rhs9 and list(map(sum,matrix))!=bad_rhs,'rook corruption controls')
        control_results.append(dict(root=r,fixed_edges=len(f),positive='PASS',corrupted_coefficient='REJECT',corrupted_rhs='REJECT'))
    scope.require(len(control_results)==18 and {(r['root'],r['fixed_edges'])for r in control_results}=={(r,k)for r in range(9)for k in (0,1)},'all18 control cases')
    # This run has no valid primal or dual. Preserve those exact execution facts,
    # and refuse to turn the raw solver's default objective into a bound.
    scope.require(numeric['value_valid']is False and numeric['dual_valid']is False and numeric['objective_usable']is False and
                  summary['objective']is None and summary['near_zero_diagnostic']is False and bound['bound']is None,'invalid solver output scope')
    scope.require('TimeLimit'in numeric['model_status']and 'TimeLimit'in summary['model_status'],'observed time-limit classification')
    scope.require(all(scope.digest(ROOT/f)==h for f,h in bindings.items()),'inputs changed')
    result=dict(status='INDEPENDENT_PARTIAL_K_FULL_MOMENT_MODEL_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=manifest['source_commit'],
        command=[sys.executable]+sys.argv,working_directory=str(Path.cwd()),python=platform.python_version(),numpy=np.__version__,inputs_sha256=bindings,
        claim_id='C-PARTIAL-K-FULL-MOMENT-ENCODING',claim_revision=1,recommendation='VERIFIED',
        statement='Every target completion in the frozen one-freed-coordinate partialK scope induces a feasible zero-objective point of this exact full-neighborhood-moment LP. No converse asserted.',
        objective='PARTIAL_K_FULL_CENTER_STAR_MOMENT_PHASE1_V1',shape=[5310,61450],nonzeros=4425506,probability_columns=54478,
        hard_simplex_rows=84,hard_reciprocity_rows=1740,soft_moment_equalities=3486,complete_augmented_matrix_and_bounds_checked=True,
        controls=control_results,producer_imported=False,model_built_from_complete_neighborhoods=True,
        dependency=dict(id='C-PARTIAL-K-ONE-COORDINATE-DOMAINS',revision=1,relation='uses_result'),
        solver_outcome=dict(model_status=numeric['model_status'],valid_primal=False,valid_dual=False,exact_bound_attempted=False,raw_objective_not_usable=True),
        scope=primary['scope'],shared_trusted_components=['NumPy/SciPy integer storage','Python standard library','tqdm display','independent domain audit helpers and complete-table proof'],
        limitations=['Necessary relaxation only','No valid primal/dual or exact support bound in this run','No feasibility, family exclusion or target resolution','No comparison with old cap objective'],target_resolution='UNKNOWN',elapsed_seconds=time.perf_counter()-tick)
    out.open('x',encoding='utf8').write(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(status=result['status'],sha256=scope.digest(out))))

if __name__=='__main__':main()
