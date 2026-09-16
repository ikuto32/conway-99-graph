"""Compare saved fixed-dual ranks with independently audited star-LP intervals.

Descriptive, selected-sample diagnostics only. No optimization, native search,
new exclusion certificate, or claim about unobserved candidates is performed.
"""
import argparse
import csv
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
import json
import math
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

def rational(d):
    return Fraction(int(d['numerator']),int(d['denominator']))

def pearson(x,y):
    xbar,ybar=sum(x)/len(x),sum(y)/len(y)
    xx=[v-xbar for v in x]; yy=[v-ybar for v in y]
    denominator=math.sqrt(sum(v*v for v in xx)*sum(v*v for v in yy))
    return sum(a*b for a,b in zip(xx,yy))/denominator if denominator else None

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ranking',required=True)
    p.add_argument('--shortlist',required=True)
    p.add_argument('--out',required=True)
    a=p.parse_args()
    out=path(a.out)
    require(not out.exists(),'Preserve output directory')
    bindings={}
    def bind(p,expected=None):
        name=key(p)
        h=digest(p)
        require(expected is None or h==expected,'Changed bound file '+name)
        require(name not in bindings or bindings[name]==h,'Conflicting binding')
        bindings[name]=h
        return h
    def load(p):
        bind(p)
        d=json.loads(path(p).read_bytes())
        for section in ('inputs_sha256','outputs_sha256'):
            for name,h in d.get(section,{}).items():
                bind(name,h)
        return d
    bind(__file__)
    ranking=load(a.ranking); shortlist=load(a.shortlist)
    require(ranking['status']=='HEURISTIC_FIXED_STAR_DUAL_FAMILY_RANKING_FINISHED','Unfinished ranking')
    require(shortlist['status']=='BOUNDED_CP_STAR_SHORTLIST_EVALUATION_FINISHED','Unfinished shortlist')
    bind(shortlist['manifest_path'],shortlist['manifest_sha256'])
    manifest=load(shortlist['manifest_path'])
    bind(manifest['baseline_star_audit_path'],manifest['baseline_star_audit_sha256'])
    baseline=load(manifest['baseline_star_audit_path'])
    require(baseline['status']=='INDEPENDENT_EXACT_STAR_MARGINAL_PHASE1_AUDIT_PASS','Baseline audit unavailable')
    base_lower,base_upper=map(rational,(baseline['exact_dual_lower'],baseline['exact_primal_upper']))
    require(base_lower==rational(manifest['baseline_exact_lower']) and base_upper==rational(manifest['baseline_exact_upper']),'Baseline intervals differ')
    bind(ranking['family_path'],ranking['family_sha256'])
    family=load(ranking['family_path'])
    cp=load(manifest['search_summary_path'])
    bind(manifest['search_summary_path'],manifest['search_summary_sha256'])
    require(key(cp['paths']['native'])==key(ranking['family_path']) and cp['family_association']['native_sha256']==ranking['family_sha256'],'Different candidate families')
    cp_records={r['proposal_index']:r for r in cp['records']}
    ranks={r['index']:(position+1,r) for position,r in enumerate(ranking['ranked'])}
    require(len(ranks)==len(ranking['ranked']),'Duplicate rank index')
    rows,intervals=[],{}
    seen=set()
    for r in shortlist['records']:
        i=r['proposal_index']
        require(i not in seen and i in ranks and i in cp_records,'Duplicate/unassociated selection')
        seen.add(i)
        require(r['audited'] is True,'Unaudited observation')
        for field in ('candidate','result','audit','certificate','replay'):
            bind(r[field+'_path'],r[field+'_sha256'])
        require(r['candidate_sha256']==cp_records[i]['candidate_sha256'] and key(r['candidate_path'])==key(cp_records[i]['candidate_path']),'Wrong CP candidate association')
        candidate=json.loads(path(r['candidate_path']).read_bytes())
        require(sorted(candidate['overlap_edges_outer_zero_based'])==family['overlap_candidates'][i],'Candidate/family index mismatch')
        phase=load(r['result_path']); audit=load(r['audit_path'])
        require(audit['status']=='INDEPENDENT_EXACT_STAR_MARGINAL_PHASE1_AUDIT_PASS','Wrong star audit status')
        ab={key(p):h for p,h in audit['inputs_sha256'].items()}
        require(ab.get(key(r['candidate_path']))==r['candidate_sha256'] and ab.get(key(r['result_path']))==r['result_sha256'],'Audit candidate/result association')
        require(key(phase['candidate_path'])==key(r['candidate_path']) and phase['candidate_sha256']==r['candidate_sha256'],'Wrong optimized candidate')
        lower,upper=map(rational,(audit['exact_dual_lower'],audit['exact_primal_upper']))
        require(lower<=upper and lower==rational(r['exact_lower']) and upper==rational(r['exact_upper']),'Wrong star interval')
        improvement=upper<base_lower
        require(improvement==r['exact_strict_improvement'],'Wrong strict improvement flag')
        global_rank,score=ranks[i]
        intervals[i]=(lower,upper)
        rows.append(dict(index=i,fixed_dual_family_rank=global_rank,
                         fixed_dual_score_numerator=score['score_numerator'],fixed_dual_denominator=score['denominator'],
                         fixed_dual_score=float(Fraction(score['score_numerator'],score['denominator'])),
                         optimized_star_lower=float(lower),optimized_star_upper=float(upper),
                         optimized_star_midpoint=float((lower+upper)/2),
                         exact_strict_improvement=improvement,guaranteed_improvement=float(base_lower-upper) if improvement else 0.0,
                         candidate_path=key(r['candidate_path']),candidate_sha256=r['candidate_sha256'],
                         audit_path=key(r['audit_path']),audit_sha256=r['audit_sha256']))
    require(len(rows)==14,'This bounded diagnostic expects14 existing observations')
    rows.sort(key=lambda r:(r['fixed_dual_score_numerator'],r['index']))
    for j,r in enumerate(rows):
        r['fixed_dual_observed_rank']=j+1
    optimized=sorted(rows,key=lambda r:(intervals[r['index']][1],r['index']))
    separated=all(intervals[a['index']][1]<intervals[b['index']][0] for a,b in zip(optimized,optimized[1:]))
    require(separated,'Overlapping exact intervals need partial-order treatment')
    for j,r in enumerate(optimized):
        r['optimized_star_observed_rank']=j+1
    concordant=discordant=tied=0
    for r,s in combinations(rows,2):
        if r['fixed_dual_score_numerator']==s['fixed_dual_score_numerator']:
            tied+=1
        elif intervals[r['index']][1]<intervals[s['index']][0]:
            concordant+=1
        elif intervals[s['index']][1]<intervals[r['index']][0]:
            discordant+=1
        else:
            raise ValueError('Unresolved optimized order')
    require(tied==0,'Spearman implementation expects untied diagnostic values')
    metrics=dict(pearson_fixed_score_vs_interval_midpoint=pearson([r['fixed_dual_score'] for r in rows],[r['optimized_star_midpoint'] for r in rows]),
                 spearman_observed_ranks=pearson([r['fixed_dual_observed_rank'] for r in rows],[r['optimized_star_observed_rank'] for r in rows]),
                 concordant_exact_interval_pairs=concordant,discordant_exact_interval_pairs=discordant,
                 kendall_untied=(concordant-discordant)/(concordant+discordant))
    prefixes=[dict(observed_prefix=k,indices=[r['index'] for r in rows[:k]],strict_improvements=sum(r['exact_strict_improvement'] for r in rows[:k]),best_optimized_index=min(rows[:k],key=lambda r:r['optimized_star_observed_rank'])['index']) for k in (3,5,7,14)]
    report=dict(status='HEURISTIC_FIXED_STAR_DUAL_OBSERVED_STAR_LP_DIAGNOSTIC',inputs_sha256=bindings,
                observed_candidates=14,full_family_candidates=ranking['candidate_count'],
                baseline_star_interval=[float(base_lower),float(base_upper)],all_optimized_intervals_strictly_separated=separated,
                strict_improvements=sum(r['exact_strict_improvement'] for r in rows),metrics=metrics,
                fixed_dual_prefixes_within_observed_subset=prefixes,rows=rows,
                best_optimized=optimized[0],lp_solves=0,new_exclusions_claimed=0,
                scope='Retrospective selected sample: these14 were CP-selected, passed the local gate and had nearzero old edge-LP merit. Correlations do not estimate performance over8837 candidates or validate fixed-dual-only selection. Exact intervals are reused from independently audited results; score signs are not feasibility/exclusion claims.')
    out.mkdir(parents=True)
    (out/'diagnostic.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    columns=['index','fixed_dual_family_rank','fixed_dual_observed_rank','fixed_dual_score','optimized_star_observed_rank','optimized_star_lower','optimized_star_upper','exact_strict_improvement']
    with (out/'scatter_data.csv').open('x',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=columns,extrasaction='ignore');w.writeheader();w.writerows(rows)
    lines=['Fixed-dual ranking versus14 saved star-LP intervals','',
           'This is a retrospective, CP-selected sample; no new LPs were run. Lower is better for both quantities.',
           f"Pearson: {metrics['pearson_fixed_score_vs_interval_midpoint']:.4f}; Spearman: {metrics['spearman_observed_ranks']:.4f}; Kendall: {metrics['kendall_untied']:.4f}.",'',
           '| Index | Family rank | Fixed-dual score | Optimized star interval | Strict improvement |',
           '|---:|---:|---:|---:|:---:|']
    for r in rows:
        lines.append(f"| {r['index']} | {r['fixed_dual_family_rank']} | {r['fixed_dual_score']:.6f} | [{r['optimized_star_lower']:.9f}, {r['optimized_star_upper']:.9f}] | {'yes' if r['exact_strict_improvement'] else 'no'} |")
    lines.extend(['','The three lowest fixed-dual scores in this observed sample are all worse than the baseline after reoptimization. The best optimized candidate is3074 (family rank96), followed by1377 (rank176). Fixed-dual ranking is useful as a distinct shortlist heuristic, but this sample does not justify using only its few lowest scores.','',report['scope'],''])
    (out/'diagnostic.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps(dict(status=report['status'],metrics=metrics,best_index=optimized[0]['index'],report_sha256=digest(out/'diagnostic.json'))))

if __name__=='__main__':
    main()
