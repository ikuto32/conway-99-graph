"""Corruption and resolution controls for the independently indexed cohort."""
import argparse
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path

import build_star_dual_shortlist_checkpoint as b


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cohort',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();b.require(not args.out.exists(),'Fresh QA output required')
    inputs={};controls=[]
    def read(path):
        path=b.resolve(path);inputs[b.key(path)]=sha256(path.read_bytes()).hexdigest()
        return json.loads(path.read_bytes())
    summary=read(args.cohort/'summary.json');manifest=read(summary['manifest_path'])
    family=read(manifest['family_path']);ranking=read(manifest['ranking_path'])
    scores=read(b.resolve(manifest['ranking_path']).with_name('scores.json'))
    cp=read(manifest['excluded_CP_summary_path']);candidates=[read(r['candidate_path']) for r in cp['records']]
    selected,unselected,excluded,rank,unavailable=b.rank_selection(family,scores,ranking,cp,candidates,16)
    b.require(selected==[2963,3125,8469,8293,8466,8467,8138,7757,8527,8468,2962,8555,8528,8796,8166,3055],
              'Independent historical ranking differs')
    def reject(name,operation):
        try:operation()
        except (ValueError,KeyError,TypeError,IndexError) as error:
            controls.append(dict(name=name,rejected=True,message=str(error)))
        else:raise ValueError('Accepted invalid control: '+name)
    def rank_control(name,change):
        # Shallow outer copies avoid repeatedly duplicating the large frozen
        # graph family. Only mutated paths receive fresh containers.
        data=[dict(family),dict(scores),dict(ranking),dict(cp),list(candidates)]
        change(data)
        reject(name,lambda:b.rank_selection(*data,16))
    rank_control('wrong_family_count',lambda d:d[0].update(legal_count=1))
    rank_control('rank_order_reversed',lambda d:d[2].update(ranked=list(reversed(ranking['ranked']))))
    rank_control('native_scores_claim_proof',lambda d:d[1].update(scores_are_certificates=True))
    rank_control('missing_ranked_score',lambda d:d[2].update(ranked=ranking['ranked'][:-1]))
    rank_control('wrong_native_denominator',lambda d:d[1].update(results=[dict(scores['results'][0],denominator=1)]+scores['results'][1:]))
    rank_control('wrong_CP_graph',lambda d:d[4].__setitem__(0,candidates[1]))
    rank_control('duplicate_CP_index',lambda d:d[3].update(records=[cp['records'][0],dict(cp['records'][1],proposal_index=cp['records'][0]['proposal_index'])]+cp['records'][2:]))
    rank_control('wrong_rank_move',lambda d:d[2].update(ranked=[dict(ranking['ranked'][0],root_group=99)]+ranking['ranked'][1:]))
    first=manifest['selected_candidates'][0];candidate=read(first['candidate_path'])
    def check_candidate(chosen,doc):
        b.check_chosen(chosen,doc,family,manifest['ranking_path'],manifest['ranking_sha256'],manifest['family_path'],manifest['family_sha256'],rank,scores)
    check_candidate(first,candidate)
    for name,change in (
        ('chosen_wrong_score',lambda c,d:c.update(fixed_dual_score_numerator=c['fixed_dual_score_numerator']+1)),
        ('chosen_wrong_rank',lambda c,d:c.update(fixed_dual_rank=999)),
        ('candidate_claims_edge_LP',lambda c,d:d.update(edge_LP_status='FEASIBLE')),
        ('candidate_claims_exclusion',lambda c,d:d.update(fixed_K_excluded=True)),
        ('candidate_wrong_family',lambda c,d:d.update(family_sha256='0'*64)),
    ):
        chosen,doc=deepcopy(first),deepcopy(candidate);change(chosen,doc)
        # Rebind selected candidate_document too, so metadata checks are tested.
        chosen['candidate_document']=deepcopy(doc)
        reject(name,lambda c=chosen,d=doc:check_candidate(c,d))
    records=summary['records'];resolution_paths=[args.cohort/f'index_{i}/local/independent_empty_pair_audit.json' for i in (3125,2962)]
    book=b.Index();resolved=[b.resolve_empty_pair(book,p,records) for p in resolution_paths]
    b.require([r['proposal_index'] for r in resolved]==[3125,2962] and all(r['fixed_K_excluded'] for r in resolved),'Real empty-pair resolutions failed')
    inputs.update(book.verified)
    audit_path=resolution_paths[0];audit=read(audit_path)
    class MutatedBook(b.Index):
        def __init__(self,change):super().__init__();self.change=change
        def read(self,path,status=None):
            obj=deepcopy(super().read(path))
            if b.key(path)==b.key(audit_path):self.change(obj)
            b.require(status is None or obj['status']==status,'Mutated status mismatch')
            return obj
    candidate_key=next(p for p in audit['inputs_sha256'] if Path(p).name=='candidate.json')
    proof_key=next(p for p in audit['inputs_sha256'] if Path(p).name=='pairs.json')
    for name,change in (
        ('resolution_wrong_candidate_hash',lambda d:d['inputs_sha256'].update({candidate_key:'0'*64})),
        ('resolution_wrong_proof_hash',lambda d:d['inputs_sha256'].update({proof_key:'0'*64})),
        ('resolution_incomplete',lambda d:d.update(complete_used_domains_verified=False)),
        ('resolution_capped_status',lambda d:d.update(status='INCOMPLETE_PAIR_AUDIT_NO_EXCLUSION')),
        ('resolution_cap_reason',lambda d:d.update(cap_reason='TIME_CAP')),
        ('resolution_not_empty',lambda d:d.update(propagation_status='ARC_CONSISTENT_NONEMPTY')),
        ('resolution_wrong_empty_vertex',lambda d:d.update(empty_vertex=0)),
        ('resolution_wrong_events',lambda d:d.update(events_verified=d['events_verified']-1)),
        ('resolution_missing_used_domain',lambda d:d['independently_reenumerated_domains'].pop()),
        ('resolution_imported_solver',lambda d:d.update(producer_or_solver_imported=True)),
    ):
        reject(name,lambda c=change:b.resolve_empty_pair(MutatedBook(c),audit_path,records))
    previous=read(b.ROOT/'acceleration/results/20260916_star_guided_round1_checkpoint.json')
    incumbent=b.fraction(previous['current_star_marginal_best']['exact_interval']['lower'])
    actual=b.incumbent_improvers(records,incumbent)
    eligible=next(r for r in records if r['audited']);test=deepcopy(eligible)
    test.update(exact_lower=b.rational(Fraction(4)),exact_upper=b.rational(Fraction(5)),fixed_K_excluded=True)
    b.require(b.incumbent_improvers([test],incumbent)==[test],'Synthetic positive strict candidate not selected')
    test.update(exact_lower=b.rational(Fraction(0)),fixed_K_excluded=False)
    b.require(not b.incumbent_improvers([test],incumbent),'Nonpositive bound adopted')
    test.update(audited=False,status='PENDING_INCOMPLETE_INDEPENDENT_PAIR_AUDIT')
    b.require(not b.incumbent_improvers([test],incumbent),'Incomplete candidate adopted')
    for p in (Path(__file__),Path(b.__file__),b.ROOT/'acceleration/build_star_guided_checkpoint.py',b.ROOT/'acceleration/build_cp_completion_checkpoint.py'):
        inputs[b.key(p)]=sha256(p.read_bytes()).hexdigest()
    report=dict(status='FIXED_STAR_DUAL_COHORT_CHECKPOINT_CONTROLS_PASS',inputs_sha256=inputs,controls=controls,
        negative_controls=len(controls),selected_indices=selected,real_empty_resolutions=[r['proposal_index'] for r in resolved],
        actual_incumbent_improvers=[r['proposal_index'] for r in actual],semantic_mutations_bypass_byte_binding=True,
        processes_launched=0,science_reruns=0,checkpoint_created=False)
    with args.out.open('x',encoding='utf-8') as stream:stream.write(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],negative_controls=len(controls),real_empty_resolutions=2)))


if __name__=='__main__':
    main()
