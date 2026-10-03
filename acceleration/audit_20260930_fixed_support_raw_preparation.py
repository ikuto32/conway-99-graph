"""Generic fixed-coordinate support controls; NOT a research encoding gate."""
from copy import deepcopy
from itertools import combinations
from pathlib import Path
import argparse,gzip,json
import audit_20260930_prism_coarse60_bitlift_object as shared

ROOT=shared.ROOT;need=shared.need;digest=shared.digest;key=shared.key;read=shared.read;save=shared.save

def exact_domains(core,support):
    h=len(core);need(h%3==0,'three fibres');n=h//3
    need(len(support)==n and support and len({len(row) for row in support})==1,'coordinate support shape')
    m=len(support[0]);need(all(type(v)is int and v in (0,1) for row in support for v in row),'literal binary support')
    need(all(sum(row)==3*(n-2) for row in support) and all(sum(row[y] for row in support)==6 for y in range(m)),'fixed support margins')
    need(m==n*(n-2)//2,'triangle-family outside population')
    domains=[]
    for y in range(m):
        coords=[a for a in range(n) if support[a][y]];choices=[]
        for first in combinations(coords,2):
            remaining=[a for a in coords if a not in first]
            for second in combinations(remaining,2):
                third=tuple(a for a in remaining if a not in second)
                groups=[first,second,third]
                if any(core[g*n+pair[0]][g*n+pair[1]] for g,pair in enumerate(groups)):continue
                choices.append(tuple(sorted(g*n+a for g,pair in enumerate(groups) for a in pair)))
        need(len(choices)==len(set(choices)) and len(choices)<=90,'balanced coloring enumeration without duplicates')
        domains.append(sorted(choices))
    return domains

def verify_fixed_support(core,factor,support,research=True):
    # The independent complete raw path establishes dimensions, core, Gram,
    # margins and caps first; no producer factor routines are imported.
    result=shared.rawcheck.canonicalize_and_check(core,factor,research=research)
    n=len(core)//3;m=len(factor[0]);need(len(support)==n and all(len(row)==m for row in support),'matching raw support shape')
    need(all(type(v)is int and v in (0,1) for row in support for v in row),'binary fixed support entries')
    rebuilt=[[sum(factor[g*n+a][y] for g in range(3)) for y in range(m)] for a in range(n)]
    need(rebuilt==support,'every coordinate/fibre support incidence')
    domains=exact_domains(core,support);chosen=[]
    for y in range(m):
        rows=tuple(i for i,row in enumerate(factor) if row[y]);need(rows in domains[y],'raw support is an admissible balanced coloring');chosen.append(domains[y].index(rows))
    return result,domains,chosen

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    try:
        _,_,bindings=shared.bind();fixture=ROOT/'acceleration/results/20260930_srg243_residual_fixture/triangle_blocks.json'
        need(digest(fixture)=='3f8dfa3803d6a5db8146dd24a0857477e1aa061ab10dac0f9e6e564aabc86439','authenticated nonempty fixture')
        f=read(fixture);core=f['cubic_core60'];factor=f['factor60x180'];n=20
        support=[[sum(factor[g*n+a][y] for g in range(3)) for y in range(180)] for a in range(n)]
        raw,domains,chosen=verify_fixed_support(core,factor,support,research=False)
        reverse,_,_=verify_fixed_support(core,[r[::-1] for r in factor],[r[::-1] for r in support],research=False)
        need(reverse['canonical_factor']['incidence_matrix']==raw['canonical_factor']['incidence_matrix'],'complete independent canonical column recovery')
        save(out/'known243_raw_support.json',dict(label='Known243 positive only; no research99factor',coordinate_support=support,domain_lengths=list(map(len,domains)),selected_domain_choice_indices=chosen,complete_raw_checks=raw['canonical_factor']['exact_checks']))
        with gzip.open(out/'known243_domains.json.gz','wt',encoding='utf8') as stream:json.dump(domains,stream)
        rejected=[]
        def reject(label,fn):
            try:fn()
            except (ValueError,KeyError,IndexError):rejected.append(label)
            else:raise ValueError('accepted corrupted fixed-support control '+label)
        for label in ['wrong_support','Boolean_support','wrong_F','wrong_core','wrong_column_order']:
            c=deepcopy(core);a=deepcopy(factor);l=deepcopy(support)
            if label=='wrong_support':l[0][0]^=1
            elif label=='Boolean_support':l[0][0]=bool(l[0][0])
            elif label=='wrong_F':a[20][0]^=1
            elif label=='wrong_core':c[0][1]^=1
            else:a=[row[::-1] for row in a]
            reject(label,lambda c=c,a=a,l=l:verify_fixed_support(c,a,l,research=False))
        reject('243_not_research99',lambda:verify_fixed_support(core,factor,support))
        for p in [Path(__file__),fixture,ROOT/'docs/REVIEW_PLAN_20260930_FIXED_SUPPORT_COLORING.md']:bindings[key(p)]=digest(p)
        report={**shared.provenance(bindings),'status':'FIXED_SUPPORT_RAW_CONTROL_PREPARATION_COMPLETE_NOT_MODEL_GATE','research_encoding_gate':False,
            'known_positive_parameters':[243,22,1,2],'columns_checked':180,'raw_coordinate_entries_checked':3600,'full_domain_colorings_per_column_before_filter':90,
            'corruptions_rejected':rejected,'research_model':None,'research_model_null_reason':'Actual fixed-L CNF, domains, gate and dimensions are not available yet.',
            'outputs_sha256':{key(p):digest(p) for p in out.iterdir() if p.is_file()},
            'limitations':['Only reusable raw-helper preparation and known243 controls.','No complete research assignment/CNF check was performed.','No research gate, fixed-support equivalence or search outcome is approved.']}
        save(out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(out/'summary.json'))))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e)));raise
if __name__=='__main__':main()
