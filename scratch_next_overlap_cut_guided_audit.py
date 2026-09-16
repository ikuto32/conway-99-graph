"""Independent partial-graph and five-bank-cut audit of the guided result."""
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path

from scratch_next_overlap_cut_bank import load_cuts, evaluate

HERE=Path(__file__).resolve().parent


def main():
    path=HERE/'scratch_next_overlap_cut_guided.json'
    data=json.loads(path.read_bytes())
    compiled_path=HERE/'scratch_next_overlap_cut_compiled.json'
    assert sha256(compiled_path.read_bytes()).hexdigest()==data['compiled_sha256']
    compiled=json.loads(compiled_path.read_bytes())
    assert compiled['input_sha256']==data['compiled_input_sha256']
    for name,digest in data['compiled_input_sha256'].items():
        assert sha256((HERE/name).read_bytes()).hexdigest()==digest
    assert data['solver_workers']==1 and data['time_limit_seconds']==45
    assert data['max_modes']['exact_max']==4881
    assert data['distinct_sign_images_excluded']==640
    output={'input_sha256':sha256(path.read_bytes()).hexdigest(),'solve_status':data['status'],
            'compiled_sha256':data['compiled_sha256'],'compiled_leaf_hashes_checked':len(data['compiled_input_sha256']),
            'exact_max_constraints':4881,'solver_workers':1,'solver_time_limit_seconds':45,
            'scope':'Complete168-edge overlap assignment only, all unlisted overlap and same-fiber edges absent. No LP, dual, full graph, or global exclusion.'}
    if data['status'] not in ('OPTIMAL','FEASIBLE'):
        assert 'overlap_edges_outer_zero_based' not in data
        output['status']='CUT_GUIDED_NO_CANDIDATE_RETURNED'
    else:
        labels=sorted((a,b) for a in range(14) for b in range(a+1,14) if a//2!=b//2)
        labels.sort(key=lambda pair:(pair[0]//2,pair[1]//2,*pair))
        vertex_of={pair:u for u,pair in enumerate(labels)}
        supports=[{a//2,b//2} for a,b in labels]
        known=set(map(tuple,data['overlap_edges_outer_zero_based']))
        assert len(known)==len(data['overlap_edges_outer_zero_based'])==168
        cp=HERE/'scratch_resume_integral_compression.json'
        assert sha256(cp.read_bytes()).hexdigest()==data['compression_sha256']
        c=json.loads(cp.read_bytes())['C']
        rows=[set() for _ in range(99)]
        def add(u,v): rows[u].add(v);rows[v].add(u)
        for u in range(1,15): add(0,u)
        for u in range(1,15,2): add(u,u+1)
        for u,pair in enumerate(labels):
            for symbol in pair: add(symbol+1,u+15)
        outer=[set() for _ in range(84)]
        totals=Counter()
        for u,v in known:
            assert type(u) is int and type(v) is int and 0<=u<v<84 and len(supports[u]&supports[v])==1
            add(u+15,v+15)
            outer[u].add(v);outer[v].add(u)
            totals[u//4,v//4]+=1
        assert all(len(row)==4 for row in outer)
        for f,h in combinations(range(21),2):
            if supports[4*f]&supports[4*h]: assert totals[f,h]==c[f][h]
        for u in range(84):
            for symbol in range(14):
                count=sum(symbol in labels[v] for v in outer[u])
                assert count==1 if symbol//2 in supports[u] else count<=2
        assert all(len(rows[u]&rows[v])<=(1 if v in rows[u] else 2) for u,v in combinations(range(99),2))
        excluded=set()
        for name,digest in data['excluded_source_hashes'].items():
            source=HERE/name
            assert sha256(source.read_bytes()).hexdigest()==digest
            source_edges=set(map(tuple,json.loads(source.read_bytes())['overlap_edges_outer_zero_based']))
            for mask in range(128):
                mapping={u:vertex_of[tuple(symbol^((mask>>(symbol//2))&1) for symbol in pair)] for u,pair in enumerate(labels)}
                excluded.add(tuple(sorted(tuple(sorted((mapping[u],mapping[v]))) for u,v in source_edges)))
        assert len(excluded)==640 and tuple(sorted(known)) not in excluded
        active={i for i,u,v in compiled['overlap_variables'] if (u,v) in known}
        bank=load_cuts()
        assert [cut['name'] for cut in bank]==[cut['name'] for cut in compiled['cuts']]
        cut_values=[]
        for cut,bank_cut,modeled in zip(compiled['cuts'],bank,data['modeled_cut_values']):
            rhs=cut['R_constant']+sum(weight for i,weight in cut['R_linear'] if i in active)
            rhs+=sum(weight for u,v,w,weight in cut['R_products'] if w in outer[u] and w in outer[v])
            zs=sum(max(0,-row['constant']-sum(weight for i,weight in row['terms'] if i in active))
                   for row in cut['w_affine'])
            independent=evaluate(known,bank_cut,include_upper=False)
            assert independent['combined_rhs']==rhs and independent['score']==rhs+zs
            assert modeled['name']==cut['name'] and modeled['z_total']==zs
            assert modeled['R']<=rhs and modeled['score']==modeled['R']+zs
            assert 0<=modeled['score']<=independent['score']
            cut_values.append({'name':cut['name'],**independent,'modeled_score':modeled['score']})
        output.update(status='INDEPENDENT_CUT_GUIDED_OVERLAP_AUDIT_PASS',overlap_edges=168,
                      exposed_edges=sum(map(len,rows))//2,degree_histogram=dict(Counter(map(len,rows))),
                      pair_caps_checked=4851,prior_sign_images_excluded=640,
                      independent_bank_cut_values=cut_values,product_overestimation_direction_checked=True)
    (HERE/'scratch_next_overlap_cut_guided_audit.json').write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(output))


if __name__=='__main__': main()
