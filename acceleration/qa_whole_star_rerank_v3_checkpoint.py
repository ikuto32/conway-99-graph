"""Independent-cohort indexing semantic controls; no science or native calls."""
import argparse
from copy import deepcopy
from fractions import Fraction
import json
from pathlib import Path

import build_whole_star_rerank_v3_checkpoint as b


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path)
    args=parser.parse_args();b.require(args.out is None or not args.out.exists(),'Fresh QA output required')
    book=b.Index();controls=[]
    def reject(name,call):
        try:call()
        except (ValueError,KeyError,TypeError) as error:controls.append(dict(name=name,rejected=True,error=str(error)))
        else:raise ValueError('Accepted invalid control: '+name)
    records=[dict(proposal_index=i,available=True,best_upper_numeric=float(i+20),best_lower_numeric=float(128-i)) for i in range(128)]
    upper=list(range(16,128));lower=list(reversed(upper))
    audit=dict(excluded_LP_tested_indices=list(range(16)),records=records,eligible_ranked_by_upper_indices=upper,eligible_ranked_by_lower_indices=lower,
        numeric_cpu_controls=[dict(proposal_index=i) for i in (0,64,127)],
        evaluation_selections={'union_16':[dict(proposal_index=i,selection_roles=['upper' if i<24 else 'lower']) for i in list(range(16,24))+list(range(127,119,-1))]})
    selected,_,_=b.rebuild_selection(audit,16,'union');b.require(len(selected)==16,'Union size')
    for name,change in (
        ('duplicate_attempt',lambda a:a['records'][1].update(proposal_index=0)),
        ('bool_index',lambda a:a['records'][0].update(proposal_index=False)),
        ('nonbool_availability',lambda a:a['records'][0].update(available=1)),
        ('nonfinite_upper',lambda a:a['records'][0].update(best_upper_numeric=float('nan'))),
        ('nonfinite_lower',lambda a:a['records'][0].update(best_lower_numeric=float('inf'))),
        ('metadata_only',lambda a:a.update(numeric_cpu_controls=[])),
        ('duplicate_CPU_control',lambda a:a['numeric_cpu_controls'][1].update(proposal_index=0)),
        ('wrong_upper_order',lambda a:a['eligible_ranked_by_upper_indices'].reverse()),
        ('wrong_lower_order',lambda a:a['eligible_ranked_by_lower_indices'].reverse()),
        ('missing_selection',lambda a:a['evaluation_selections']['union_16'].pop()),
        ('missing_exclusion',lambda a:a['excluded_LP_tested_indices'].pop()),
        ('duplicate_exclusion',lambda a:a['excluded_LP_tested_indices'].__setitem__(0,1)),
        ('previous_tested_selected',lambda a:a['evaluation_selections']['union_16'][0].update(proposal_index=0)),
        ('wrong_selection_role',lambda a:a['evaluation_selections']['union_16'][0].update(selection_roles=['lower'])),
    ):
        changed=deepcopy(audit);change(changed);reject(name,lambda x=changed:b.rebuild_selection(x,16,'union'))
    prior=book.read('acceleration/results/20260916_star_guided_dual_checkpoint.json')
    newest=book.read('acceleration/results/20260916_star_guided_round2_checkpoint.json')
    row=next(r for r in newest['star_records'] if r['proposal_index']==18481)
    row_snapshot=deepcopy(row);current=deepcopy(prior['current_star_marginal_best'])
    # A different current baseline must produce a different exact gain while
    # preserving the original cohort record and its own baseline-relative claim.
    current['exact_interval']['lower']=b.rational(Fraction(6))
    frontier,index=b.promote_to_parent(current,row)
    b.require(index==18481 and b.fraction(frontier['guaranteed_improvement'])==Fraction(6)-b.fraction(row['exact_upper']) and row==row_snapshot,
        'Parent-relative promotion changed evidence or used old comparison baseline')
    stronger=deepcopy(current);stronger['exact_interval']['lower']=b.rational(Fraction(5))
    retained,index=b.promote_to_parent(stronger,row)
    b.require(index is None and retained is stronger,'Nonimproving parent comparison replaced incumbent')
    for changes in (dict(audited=False),dict(fixed_K_excluded=False),dict(exact_lower=b.rational(Fraction(0)))):
        modified={**row,**changes};b.require(b.parent_improvement([modified],Fraction(6)) is None,'Capped/nonpositive row adopted')
    pair=book.read(row['independent_pair_audit_path']);stars=book.read(b.resolve(row['gate_path']).parent/'stars.json')
    b.compare_domain_sets(stars,stars,pair)
    for name,change in (
        ('native_incomplete',lambda a,c,p:a.update(complete_domain_enumeration=False)),
        ('rank_pruned_table',lambda a,c,p:a['domains'][0]['domain_masks_hex'].pop()),
        ('rank_different_mask',lambda a,c,p:a['domains'][0]['domain_masks_hex'].__setitem__(0,hex(int(a['domains'][0]['domain_masks_hex'][0],16)^1))),
        ('missing_original_vertex',lambda a,c,p:a['domains'].pop()),
        ('independent_incomplete',lambda a,c,p:p.update(complete_used_domains_verified=False)),
        ('independent_empty',lambda a,c,p:p.update(propagation_status='EMPTY_DOMAIN')),
    ):
        data=[deepcopy(stars),deepcopy(stars),deepcopy(pair)];change(*data)
        reject(name,lambda d=data:b.compare_domain_sets(*d))
    phase_path='acceleration/results/20260916_star_guided_round2/repair_19706/phase1.json'
    phase=book.read(phase_path);audit_path=b.resolve(phase_path).with_name('audit.json');book.read(audit_path)
    warm=dict(candidate_path=phase['candidate_path'],candidate_sha256=phase['candidate_sha256'],
        edge_LP_status='STRICTLY_AUDITED_RESTART_WARM',edge_phase1_path=phase_path,edge_phase1_audit_path=b.key(audit_path))
    b.check_warm(book,warm)
    class SemanticBook(b.Index):
        def __init__(self,path,change):
            super().__init__();self.documents=book.documents;self.verified=dict(book.verified)
            self.path=b.key(path);self.change=change
        def read(self,path,status=None):
            data=deepcopy(super().read(path,status))
            if b.key(path)==self.path:self.change(data)
            return data
    for name,path,change in (
        ('warm_other_candidate',phase_path,lambda d:d.update(candidate_sha256='0'*64)),
        ('warm_not_optimal',phase_path,lambda d:d.update(optimal=False)),
        ('warm_imprecise_solver',phase_path,lambda d:d['requested_solver_tolerances'].update(ipm_optimality_tolerance=1e-8)),
        ('warm_wrong_source',phase_path,lambda d:d['source_sha256'].__setitem__('phase1_probe_precise.py','0'*64)),
        ('warm_relaxed_audit',audit_path,lambda d:d.update(numerical_tolerance=1e-6)),
        ('warm_wrong_auditor',audit_path,lambda d:d.update(auditor_sha256='0'*64)),
        ('warm_wrong_graph_auditor',audit_path,lambda d:d.update(graph_auditor_sha256='0'*64)),
        ('warm_invalid_interval',audit_path,lambda d:d.update(exact_dual_lower_bound=b.rational(Fraction(99)))),
    ):
        reject(name,lambda p=path,c=change:b.check_warm(SemanticBook(p,c),warm))
    from qa_evaluate_whole_star_rerank_v3 import fixtures
    ranking,rank_audit,family=fixtures()
    manifest=dict(objective_id='ORIGINAL_STAR_SIMPLEX_PDHG_V1',original_complete_domains_used=True,pair_pruned_domains_used=False,
        selected_candidates=deepcopy(ranking['records'][:16]))
    b.check_whole_identity(ranking,rank_audit,family,manifest)
    for name,change in (
        ('cross_family',lambda r,a,f,m:f.update(status='COMPLETE_CROSS_ATOMIC_CYCLE_SUBFAMILY_EXTRACTION')),
        ('rank_filtered',lambda r,a,f,m:r.update(pair_pruned_domains_used=True)),
        ('manifest_filtered',lambda r,a,f,m:m.update(pair_pruned_domains_used=True)),
        ('filtered_objective',lambda r,a,f,m:m.update(objective_id='TRIANGLE_PAIR_FILTERED_STAR_SIMPLEX_V1')),
        ('native_index_mismatch',lambda r,a,f,m:r['records'][0].update(original_native_index=1)),
        ('native_bool',lambda r,a,f,m:r['records'][1].update(original_native_index=True)),
        ('wrong_multiple_cycles',lambda r,a,f,m:m['selected_candidates'][0].update(alternating_cycle_sizes=[4])),
        ('wrong_selected_native',lambda r,a,f,m:m['selected_candidates'][0].update(original_native_index=1)),
        ('wrong_numeric_hash',lambda r,a,f,m:r['records'][0].update(candidate_sha256='corrupt')),
        ('wrong_whole_coordinate',lambda r,a,f,m:f['moves'][0].update(matching_class='cross')),
    ):
        data=deepcopy([ranking,rank_audit,family,manifest]);change(*data)
        reject(name,lambda d=data:b.check_whole_identity(*d))
    reject('nonunion_selection',lambda:b.rebuild_selection(rank_audit,16,'upper'))
    reject('non16_selection',lambda:b.rebuild_selection(rank_audit,8,'union'))
    book.bind(b.ROOT/'acceleration/qa_evaluate_whole_star_rerank_v3.py')
    for name,h in b.PINS.items():book.bind(b.ROOT/'acceleration'/name,h)
    book.bind(Path(__file__));book.bind(Path(b.__file__))
    report=dict(status='WHOLE_STAR_RERANK_V3_CHECKPOINT_CONTROLS_PASS',inputs_sha256=book.verified,
        negative_controls=len(controls),controls=controls,positive_controls=['deterministic_union_selection','actual_original84_domains',
            'actual_precise_edge_warm','different_parent_gain_recomputed_on_copy','stronger_parent_retains_incumbent','nonpositive_and_caps_not_adopted'],
        synthetic_fixtures_are_scientific_evidence=False,semantic_controls_bypass_hash_guards=True,
        scientific_reruns=0,subprocess_invocations=0,checkpoint_created=False)
    if args.out is not None:
        with args.out.open('x',encoding='utf-8') as stream:stream.write(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps(dict(status=report['status'],negative_controls=len(controls),output_created=args.out is not None)))


if __name__=='__main__':main()
