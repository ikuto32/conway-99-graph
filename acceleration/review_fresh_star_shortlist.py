"""Selection, original-domain equality, and restart safeguards; no science."""
import argparse
from copy import deepcopy
from fractions import Fraction
import json
from pathlib import Path
from types import SimpleNamespace

import evaluate_fresh_star_shortlist as e


def review():
    controls=[];inputs={}
    def read(p):
        inputs[e.key(p)]=e.digest(p)
        return e.load(p)
    def reject(name,call):
        try:call()
        except (ValueError,KeyError,TypeError) as error:controls.append(dict(name=name,rejected=True,error=str(error)))
        else:raise ValueError('Accepted invalid control: '+name)
    # In-memory scalar fixtures exercise choices; they are never scientific
    # reports and no synthetic candidate/file/hash pair is serialized.
    rows=[dict(proposal_index=i,available=True,best_upper_numeric=20.+i,best_lower_numeric=16.-i) for i in range(16)]
    audit=dict(status='INDEPENDENT_FRESH_STAR_PDHG_RANKING_AUDIT_PASS',producer_or_native_imported=False,
        all_serialized_models_reconstructed=True,independent_domain_enumeration_performed=False,records=rows,
        ranked_by_upper_indices=list(range(16)),ranked_by_lower_indices=list(reversed(range(16))),evaluation_selections={},
        numeric_cpu_controls=[dict(proposal_index=i) for i in (0,8,15)])
    family=dict(legal_count=16,overlap_candidates=[None]*16,moves=[None]*16)
    for mode in ('upper','union'):
        for n in (8,16):audit['evaluation_selections'][f'{mode}_{n}']=e.evaluation_selection(list(range(16)),list(reversed(range(16))),n,mode)
    choice,_,_,_=e.select_records(audit,family,8,'union')
    e.require([r['proposal_index'] for r in choice]==[0,1,2,3,15,14,13,12],'Union selection differs')
    duplicate=e.evaluation_selection(list(range(16)),list(range(16)),8,'union')
    e.require([r['proposal_index'] for r in duplicate]==list(range(8)) and duplicate[0]['selection_roles']==['upper','lower'] and
        duplicate[4]['selection_roles']==['upper_fill'],'Union role merging/fill differs')
    e.require(len(e.evaluation_selection([1,2],[2,1],16,'union'))==2,'Small available set not preserved')
    for name,change in (
        ('unfinished_ranking',lambda a,f:a.update(status='PENDING')),
        ('producer_imported',lambda a,f:a.update(producer_or_native_imported=True)),
        ('model_not_reconstructed',lambda a,f:a.update(all_serialized_models_reconstructed=False)),
        ('metadata_only_audit',lambda a,f:a.update(numeric_cpu_controls=[])),
        ('duplicate_CPU_control',lambda a,f:a['numeric_cpu_controls'][1].update(proposal_index=0)),
        ('wrong_native_completeness_scope',lambda a,f:a.update(independent_domain_enumeration_performed=True)),
        ('bad_family_count',lambda a,f:f.update(legal_count=17)),
        ('duplicate_attempt',lambda a,f:a['records'][1].update(proposal_index=0)),
        ('out_of_range_index',lambda a,f:a['records'][1].update(proposal_index=99)),
        ('nonbool_availability',lambda a,f:a['records'][1].update(available=1)),
        ('nonfinite_upper',lambda a,f:a['records'][1].update(best_upper_numeric=float('nan'))),
        ('nonfinite_lower',lambda a,f:a['records'][1].update(best_lower_numeric=float('inf'))),
        ('inconsistent_interval',lambda a,f:a['records'][1].update(best_lower_numeric=99)),
        ('unavailable_scored',lambda a,f:a['records'][1].update(available=False)),
        ('upper_order_changed',lambda a,f:a['ranked_by_upper_indices'].reverse()),
        ('lower_order_changed',lambda a,f:a['ranked_by_lower_indices'].reverse()),
        ('selection_missing',lambda a,f:a['evaluation_selections']['union_8'].pop()),
        ('selection_roles_changed',lambda a,f:a['evaluation_selections']['union_8'][0].update(selection_roles=['lower'])),
    ):
        objects=deepcopy([audit,family]);change(*objects)
        reject(name,lambda d=objects:e.select_records(*d,8,'union'))
    for cap,mode in ((True,'upper'),(0,'upper'),(32,'upper'),(8,'invalid')):
        reject('bad_selection_'+str((cap,mode)),lambda c=cap,m=mode:e.evaluation_selection([0],[0],c,m))
    checkpoint=read('acceleration/results/20260916_star_guided_round2_checkpoint.json')
    current=checkpoint['current_star_marginal_best'];pair=read(current['independent_pair_audit_path'])
    stars=read(e.resolve(current['independent_pair_audit_path']).with_name('stars.json'))
    e.compare_original_domains(stars,stars,pair)
    permuted=deepcopy(stars)
    for row in permuted['domains']:row['domain_masks_hex'].reverse()
    e.compare_original_domains(permuted,stars,pair)
    for name,change in (
        ('rank_domains_incomplete',lambda a,b,c:a.update(complete_domain_enumeration=False)),
        ('rank_missing_vertex',lambda a,b,c:a['domains'].pop()),
        ('fresh_missing_vertex',lambda a,b,c:b['domains'].pop()),
        ('rank_duplicate_mask',lambda a,b,c:a['domains'][0]['domain_masks_hex'].append(a['domains'][0]['domain_masks_hex'][0])),
        ('rank_different_mask',lambda a,b,c:a['domains'][0]['domain_masks_hex'].__setitem__(0,hex(int(a['domains'][0]['domain_masks_hex'][0],16)^1))),
        ('ranking_pair_pruned',lambda a,b,c:a['domains'][0]['domain_masks_hex'].pop()),
        ('independent_missing_vertex',lambda a,b,c:c['independently_reenumerated_domains'].pop()),
        ('independent_incomplete',lambda a,b,c:c.update(complete_used_domains_verified=False)),
        ('independent_empty',lambda a,b,c:c.update(propagation_status='EMPTY_DOMAIN')),
        ('independent_wrong_domain_count',lambda a,b,c:c['independently_reenumerated_domains'][0].update(domain_size=1)),
    ):
        objects=[deepcopy(stars),deepcopy(stars),deepcopy(pair)];change(*objects)
        reject(name,lambda d=objects:e.compare_original_domains(*d))
    good=dict(proposal_index=3,audited=True,fixed_K_excluded=True,exact_lower=e.rational(Fraction(2)),exact_upper=e.rational(Fraction(3)))
    e.require(e.restart_choice([good],Fraction(4)) is good,'Strict positive improver lost')
    e.require(e.restart_choice([good],Fraction(3)) is None,'Equality incorrectly improved')
    for changes in (dict(audited=False),dict(fixed_K_excluded=False),dict(exact_lower=e.rational(Fraction(0)))):
        row={**good,**changes};e.require(e.restart_choice([row],Fraction(4)) is None,'Pending/nonpositive record adopted')
    precise='acceleration/results/20260916_star_guided_round2/repair_19706/phase1.json'
    edge=read(precise);strict=read(e.resolve(precise).with_name('audit.json'))
    chosen=dict(candidate_path=edge['candidate_path'],candidate_sha256=edge['candidate_sha256'])
    e.check_edge_warm(chosen,edge,strict,precise)
    for name,change in (
        ('warm_not_optimal',lambda r,x,a:x.update(optimal=False)),
        ('warm_changed_tolerance',lambda r,x,a:x.update(independent_audit_tolerance_changed=True)),
        ('warm_wrong_producer',lambda r,x,a:x['source_sha256'].__setitem__('phase1_probe_precise.py','0'*64)),
        ('warm_relaxed_audit',lambda r,x,a:a.update(numerical_tolerance=1e-6)),
        ('warm_other_candidate',lambda r,x,a:r.update(candidate_sha256='0'*64)),
        ('warm_invalid_interval',lambda r,x,a:a.update(exact_dual_lower_bound=e.rational(Fraction(999)))),
    ):
        objects=deepcopy([chosen,edge,strict]);change(*objects)
        reject(name,lambda d=objects:e.check_edge_warm(*d,precise))
    return inputs,controls


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ranking',type=Path)
    parser.add_argument('--ranking-audit',type=Path)
    parser.add_argument('--baseline-star-audit',type=Path)
    parser.add_argument('--out',type=Path)
    args=parser.parse_args();e.require(args.out is None or not args.out.exists(),'Preserve old QA report')
    inputs,controls=review();actual=None
    if args.ranking is not None:
        e.require(args.ranking_audit is not None and args.baseline_star_audit is not None,'Actual preflight needs all paths')
        manifest=e.preflight(SimpleNamespace(ranking=args.ranking,ranking_audit=args.ranking_audit,baseline_star_audit=args.baseline_star_audit,
            out=Path('acceleration/results/__fresh_star_QA_no_output__'),max_candidates=8,selection='union',seconds=30.,audit_seconds=60.))
        inputs.update(manifest['inputs_sha256'])
        actual=dict(selected_indices=[r['proposal_index'] for r in manifest['selected_candidates']],eligible=manifest['eligible_candidates'])
    for path in (Path(__file__),Path(e.__file__)):
        inputs[e.key(path)]=e.digest(path)
    for p,h in e.PINS.items():
        path=e.ROOT/'acceleration'/p;e.require(e.digest(path)==h,'Changed frozen source');inputs[e.key(path)]=h
    report=dict(status='FRESH_STAR_SHORTLIST_SEMANTIC_CONTROLS_PASS',inputs_sha256=inputs,negative_controls=len(controls),controls=controls,
        positive_controls=['union_unique_selection','union_duplicate_role_fill','fewer_available','actual_original84_domains',
            'original_domain_set_order_independent','positive_strict_restart','nonpositive_pending','cap_pending','actual_precise_edge_audit'],
        actual_preflight=actual,synthetic_fixtures_are_scientific_evidence=False,semantic_controls_bypass_hash_guards=True,
        scientific_reruns=0,subprocess_invocations=0,output_created=args.out is not None)
    if args.out is not None:
        e.save(args.out,report)
    print(json.dumps(dict(status=report['status'],negative_controls=len(controls),actual_preflight=actual,output_created=args.out is not None)))


if __name__=='__main__':main()
