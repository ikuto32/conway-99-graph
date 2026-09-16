"""Read-only comparison of fixed-star-dual ranks with saved CP selections."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def path(p):
    return (ROOT/str(p).replace('\\','/')).resolve()

def key(p):
    return path(p).relative_to(ROOT).as_posix()

def digest(p):
    return sha256(path(p).read_bytes()).hexdigest()

def require(ok,msg):
    if not ok:
        raise ValueError(msg)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ranking',required=True)
    p.add_argument('--cp-summary',required=True)
    p.add_argument('--out',required=True)
    a=p.parse_args()
    require(not path(a.out).exists(),'Preserve output')
    bindings={}
    def bind(p,expected=None):
        h=digest(p)
        require(expected is None or expected==h,'Changed bound file '+key(p))
        bindings[key(p)]=h
        return h
    for f in (__file__,a.ranking,a.cp_summary):
        bind(f)
    ranking=json.loads(path(a.ranking).read_bytes())
    cp=json.loads(path(a.cp_summary).read_bytes())
    require(ranking['status']=='HEURISTIC_FIXED_STAR_DUAL_FAMILY_RANKING_FINISHED','Unfinished ranking')
    require(cp['status']=='BOUNDED_CP_MATCHING_SEARCH_FINISHED','Unfinished CP selection')
    for d in (ranking,cp):
        for name,h in d['inputs_sha256'].items():
            bind(name,h)
    family_path=ranking['family_path']
    family=json.loads(path(family_path).read_bytes())
    require(key(cp['paths']['native'])==key(family_path) and cp['family_association']['native_sha256']==bind(family_path,ranking['family_sha256']),'Different CP/ranking family')
    records=cp['records']; seen=set()
    for r in records:
        i=r['proposal_index']
        require(type(i)is int and 0<=i<len(family['overlap_candidates']) and i not in seen,'Invalid CP index')
        seen.add(i)
        bind(r['candidate_path'],r['candidate_sha256'])
        candidate=json.loads(path(r['candidate_path']).read_bytes())
        require(sorted(candidate['overlap_edges_outer_zero_based'])==family['overlap_candidates'][i],'CP candidate/index mismatch')
    rows=ranking['ranked']
    positions={r['index']:i+1 for i,r in enumerate(rows)}
    require(len(positions)==len(rows),'Duplicate rank index')
    overlap=[dict(prefix=k,cp_overlap_indices=[r['index'] for r in rows[:k] if r['index'] in seen]) for k in (16,32,64,128,256,2048)]
    result=dict(status='FIXED_STAR_DUAL_CP_SELECTION_COMPARISON',inputs_sha256=bindings,
                candidate_count=ranking['candidate_count'],cp_selected_count=len(seen),
                prefix_overlaps=overlap,cp_candidates_with_fixed_dual_rank=[dict(index=i,rank=positions.get(i)) for i in sorted(seen)],
                first32_fixed_dual_candidates_outside_cp_selection=[r for r in rows if r['index'] not in seen][:32],
                candidates_pruned=0,exclusions_claimed=0,lp_solves=0,
                scope='Comparison of two saved heuristic selections on the exact same candidate family. Suggested new ranks are not exclusions, feasibility results, or optimized star-marginal merits.')
    path(a.out).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(overlap=overlap,first8_new=[r['index'] for r in result['first32_fixed_dual_candidates_outside_cp_selection'][:8]],sha256=digest(a.out))))

if __name__=='__main__':
    main()
