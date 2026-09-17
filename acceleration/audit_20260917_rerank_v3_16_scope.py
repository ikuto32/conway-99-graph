"""Bind new v3 union16 exact certificates to the frozen112eligible population."""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import platform
import sys
import audit_20260917_fresh_review as raw


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run',type=Path,required=True);p.add_argument('--review',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();raw.check(not a.out.exists(),'preserve evidence');bindings={}
    def bind(p,h=None):
        k=raw.key(p)
        if k not in bindings:bindings[k]=raw.digest(p)
        raw.check(h is None or h==bindings[k],'input changed '+k)
        return bindings[k]
    def read(p):
        bind(p);d=json.loads(raw.path(p).read_bytes())
        for f,h in d.get('inputs_sha256',{}).items():bind(f,h)
        return d
    bind(__file__);bind(raw.__file__);bind('uv.lock')
    m=read(a.run/'manifest.json');s=read(a.run/'summary.json');review=read(a.review)
    rank=read(m['ranking_audit_path']);family=read(m['family_path'])
    raw.check(rank['status']=='INDEPENDENT_WHOLE_STAR_RERANK_V3_AUDIT_PASS','ranking gate')
    raw.check(bind(m['ranking_audit_path'],m['ranking_audit_sha256'])==
              'be17eb32de607753ca3b7f5972c80a38f58717a235119a78a03e12ccb10a56ed','frozen independent ranking')
    excluded=set(rank['excluded_LP_tested_indices'])
    raw.check(len(excluded)==16, 'excluded16 inventory')
    avail=[r for r in rank['records'] if r['available'] and r['proposal_index'] not in excluded]
    raw.check(len(avail)==112, 'eligible112 scope')
    upper=sorted(avail,key=lambda r:(r['best_upper_numeric'],r['proposal_index']))
    lower=sorted(avail,key=lambda r:(r['best_lower_numeric'],r['proposal_index']))
    selected=list(dict.fromkeys(r['proposal_index'] for r in upper[:8]+lower[:8]))
    for r in upper:
        if len(selected)==16:break
        if r['proposal_index']not in selected:selected.append(r['proposal_index'])
    raw.check(m['selection_mode']=='union' and m['max_candidates']==16 and
              selected==[r['proposal_index'] for r in m['selected_candidates']]==[r['proposal_index'] for r in s['records']]==
              [r['proposal_index'] for r in review['records']],'frozen union16 inventory')
    raw.check(len(set(selected))==16 and m['original_complete_domains_used']is True and m['pair_pruned_domains_used']is False,'original objective scope')
    graphs=[];domain_count=0
    for chosen,produced,checked in zip(m['selected_candidates'],s['records'],review['records']):
        i=chosen['proposal_index'];numeric=read(produced['result_path']);candidate=read(chosen['candidate_path'])
        raw.check(candidate['proposal_index']==candidate['original_native_index']==i and candidate['overlap_edges_outer_zero_based']==family['overlap_candidates'][i],'whole native graph mapping')
        raw.check(bind(chosen['candidate_path'],chosen['candidate_sha256'])==numeric['candidate_sha256'] and
                  raw.key(numeric['candidate_path'])==raw.key(chosen['candidate_path']),'numeric graph identity')
        graphs.append(tuple(map(tuple,candidate['overlap_edges_outer_zero_based'])))
        old=read(chosen['ranking_domains_path']);fresh=read(numeric['domains_path']);complete=read(numeric['domain_audit_path'])
        raw.check(complete['status']=='INDEPENDENT_EXACT_PAIR_DOMAIN_AUDIT_PASS' and complete['complete_used_domains_verified']is True and
                  [r['outer_vertex']for r in complete['independently_reenumerated_domains']]==list(range(84)),'fresh independent84 completeness')
        raw.check(numeric['original_complete_domains_used']is True and numeric['pair_pruned_domains_used']is False and fresh['complete_domain_enumeration']is True,'unpruned objective')
        raw.check([r['outer_vertex']for r in old['domains']]==[r['outer_vertex']for r in fresh['domains']]==list(range(84)),'original domain row mapping')
        for before,after in zip(old['domains'],fresh['domains']):
            raw.check(set(before['domain_masks_hex'])==set(after['domain_masks_hex']) and len(before['domain_masks_hex'])==len(after['domain_masks_hex']),'original mask identity')
            domain_count+=len(after['domain_masks_hex'])
        raw.check(checked['result']=='INDEPENDENT_RAW_CHECK_PASS' and checked['fixed_K_excluded']is True and raw.rational(checked['exact_lower'])>0,'exact positive independent lower')
        raw.check(raw.rational(produced['exact_lower'])==raw.rational(checked['exact_lower']) and raw.rational(produced['exact_upper'])==raw.rational(checked['exact_upper']),'recorded exact interval')
    raw.check(len(set(graphs))==16,'distinct labeled graphs')
    baseline=read('acceleration/results/20260917_independent_review/baseline_and_matrix.json')['baseline']
    raw.check(raw.rational(m['baseline_exact_lower'])==raw.rational(baseline['exact_lower']) and raw.rational(m['baseline_exact_upper'])==raw.rational(baseline['exact_upper']),'baseline interval identity')
    worse=[r['proposal_index']for r in review['records']if raw.rational(r['exact_lower'])>raw.rational(baseline['exact_upper'])]
    better=[r['proposal_index']for r in review['records']if raw.rational(r['exact_upper'])<raw.rational(baseline['exact_lower'])]
    ambiguous=[i for i in selected if i not in worse+better]
    best=min(review['records'],key=lambda r:(raw.rational(r['exact_upper']),r['proposal_index']))
    claims=[dict(id='C-RERANK-V3-STAR-16-EXCLUSIONS',revision=1,recommendation='VERIFIED',scope='Exactly these16 labeled fixedK assignments with prescribed absent edges; positive independent exact original-star lower bounds',indices=selected)]
    if worse==selected:
        claims.append(dict(id='C-RERANK-V3-STAR-16-NO-IMPROVEMENT',revision=1,recommendation='VERIFIED',scope='All16 exact original-star lower bounds exceed incumbent18481 upper bound',indices=selected,dependencies=[dict(id='C-STAR-BASELINE-18481',revision=1,relation='uses_result')]))
    raw.check(all(raw.digest(f)==h for f,h in bindings.items()),'bound inputs changed')
    report=dict(status='INDEPENDENT_WHOLE_STAR_RERANK_V3_SHORTLIST_AUDIT_PASS',timestamp=datetime.now(timezone.utc).isoformat(),
        checking_method='Independent union16 selection, exact raw original-star checking, complete-domain identity and interval comparison',
        evaluation_path=raw.key(a.run/'summary.json'),evaluation_sha256=bind(a.run/'summary.json'),
        raw_review_path=raw.key(a.review),raw_review_sha256=bind(a.review),records=review['records'],
        command=[sys.executable]+sys.argv,working_directory=str(Path.cwd()),python=platform.python_version(),inputs_sha256=bindings,
        source_commit=None,source_commit_null_reason='Checking source additions and all dependencies explicitly hashed; producer execution source commit is in its separate receipt',
        claim_bindings=claims,selected_indices=selected,excluded_prior16_indices=sorted(excluded),eligible_ranked_population=112,distinct_selected_graphs=16,independent_raw_passes=16,original_domains_per_graph=84,domain_choices_checked=domain_count,
        best=best,strictly_worse_indices=worse,strictly_better_indices=better,unseparated_intervals=ambiguous,
        original_ranked_masks_unchanged=True,producer_imported=False,shared_trusted_components=['Python standard library','independent raw arithmetic checker','hash-bound independent complete-domain auditors'],
        limitation='Conditional fixedK exclusions only; no exhaustive overlap coverage or symmetry assumption',target_resolution='UNKNOWN',overall_search_coverage='UNKNOWN; no validated denominator')
    a.out.open('x',encoding='utf-8').write(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],best=best['proposal_index'],strictly_better=better,strictly_worse=len(worse),unseparated=ambiguous)))


if __name__=='__main__':main()
