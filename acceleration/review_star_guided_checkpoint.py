"""Semantic association and conservative-adoption QA; no scientific reruns."""
import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

import build_star_guided_checkpoint as b


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();b.require(not args.out.exists(),'Fresh control report required')
    root=b.ROOT;inputs={};controls=[]
    def read(path):
        path=b.resolve(path);inputs[b.key(path)]=sha256(path.read_bytes()).hexdigest()
        return json.loads(path.read_bytes())
    previous=read(root/'acceleration/results/20260916_cp_completion_checkpoint.json')
    round_manifest=read(root/'acceleration/results/20260916_star_guided_round1/manifest.json')
    evaluation=read(root/'acceleration/results/20260916_star_guided_round1/star_shortlist/manifest.json')
    baseline=read(evaluation['baseline_star_audit_path'])
    b.check_baseline(previous,round_manifest,evaluation,baseline)
    def rejected(name,operation):
        try:operation()
        except (ValueError,KeyError,TypeError) as error:
            controls.append(dict(name=name,rejected=True,error=str(error)))
        else:raise ValueError('Accepted invalid control: '+name)
    for name,change in (
        ('wrong_initial_candidate',lambda p,r,e,a:r.update(initial_candidate_path='wrong.json')),
        ('wrong_initial_edge_LP',lambda p,r,e,a:r.update(initial_edge_phase1_sha256='0'*64)),
        ('wrong_baseline_audit',lambda p,r,e,a:e.update(baseline_star_audit_path='wrong.json')),
        ('wrong_objective',lambda p,r,e,a:e.update(merit='EDGE_MERIT')),
        ('baseline_lower_changed',lambda p,r,e,a:a.update(exact_dual_lower=b.rational(1))),
        ('baseline_nonpositive',lambda p,r,e,a:a.update(positive_exact_dual_excludes_fixed_K=False)),
    ):
        data=deepcopy([previous,round_manifest,evaluation,baseline]);change(*data)
        rejected(name,lambda d=data:b.check_baseline(*d))
    historical=root/'acceleration/results/20260916_cp_star_shortlist_orchestration_v2_qa'
    manifest=read(historical/'manifest.json');summary=read(historical/'summary.json')
    search=read(manifest['search_summary_path']);cp=read(manifest['search_audit_path'])
    chosen=manifest['selected_candidates'][0];row=summary['records'][0]
    selected=b.select_from_cp(search,cp)
    b.require(len(selected)==9 and selected[0]==chosen,'Historical exact shortlist differs')
    for name,change in (
        ('duplicate_CP_row',lambda s,a:s['records'][1].update(proposal_index=s['records'][0]['proposal_index'])),
        ('missing_CP_audit',lambda s,a:a['probe_reports'].pop()),
        ('wrong_CP_candidate',lambda s,a:a['probe_reports'][0].update(candidate_path='wrong.json')),
        ('wrong_CP_phase_hash',lambda s,a:s['records'][0].update(result_sha256='0'*64)),
        ('negative_CP_upper',lambda s,a:a['probe_reports'][0]['phase1_audit'].update(exact_primal_upper_bound=b.rational(-1))),
    ):
        data=deepcopy([search,cp]);change(*data)
        rejected(name,lambda d=data:b.select_from_cp(*d))
    book=b.Index();baseline_lower=b.fraction(manifest['baseline_exact_lower'])
    b.inspect_record(book,row,chosen,baseline_lower)
    inputs.update(book.verified)
    audit,replay,cert=map(read,(row['audit_path'],row['replay_path'],row['certificate_path']))
    b.check_audited_row(row,audit,replay,cert,baseline_lower)
    for name,change in (
        ('wrong_star_lower',lambda r,a,v,c:r.update(exact_lower=b.rational(1))),
        ('wrong_integer_gap',lambda r,a,v,c:v.update(exact_integer_gap=str(int(v['exact_integer_gap'])+1))),
        ('wrong_certificate_scale',lambda r,a,v,c:c.update(integer_scale='1')),
        ('false_exclusion',lambda r,a,v,c:v.update(fixed_K_excluded=False)),
        ('wrong_certificate_status',lambda r,a,v,c:c.update(status='EXACT_STAR_MARGINAL_SIMPLEX_DUAL_BOUND')),
        ('false_improvement',lambda r,a,v,c:r.update(exact_strict_improvement=not r['exact_strict_improvement'])),
        ('wrong_guaranteed_gain',lambda r,a,v,c:r.update(guaranteed_improvement=b.rational(999))),
    ):
        data=deepcopy([row,audit,replay,cert]);change(*data)
        rejected(name,lambda d=data:b.check_audited_row(*d,baseline_lower))
    # Rebound in-memory documents bypass hash checks deliberately: exercise
    # semantic local/LP associations rather than merely detecting changed bytes.
    class SemanticBook(b.Index):
        def __init__(self,patch_path,patch):
            super().__init__();self.patch_path=b.key(patch_path);self.patch=patch
        def read(self,path,status=None):
            result=deepcopy(super().read(path,status))
            if b.key(path)==self.patch_path:self.patch(result)
            return result
    for name,path,change in (
        ('native_other_candidate',row['gate_path'],lambda d:d.update(candidate_sha256='0'*64)),
        ('local_missing_vertex',row['independent_pair_audit_path'],lambda d:d['independently_reenumerated_domains'].pop()),
        ('local_false_complete',row['independent_pair_audit_path'],lambda d:d.update(complete_used_domains_verified=False)),
        ('local_empty',row['independent_pair_audit_path'],lambda d:d.update(propagation_status='EMPTY_DOMAIN')),
        ('LP_wrong_candidate',row['result_path'],lambda d:d.update(candidate_sha256='0'*64)),
        ('LP_wrong_domain_proof',row['result_path'],lambda d:d.update(domain_audit_path='wrong.json')),
        ('audit_wrong_certificate',row['audit_path'],lambda d:d.update(certificate_path='wrong.json')),
    ):
        rejected(name,lambda p=path,c=change:b.inspect_record(SemanticBook(p,c),row,chosen,baseline_lower))
    prior=previous['current_star_marginal_best']
    retained,index=b.choose_best(prior,[row],b.fraction(prior['exact_interval']['lower']))
    b.require(index is None and retained is prior,'Nonimproving candidate replaced prior')
    adopted,index=b.choose_best(prior,[row],baseline_lower)
    b.require(index==row['proposal_index'] and adopted['edge_phase1_path']==row['edge_phase1_path'],'Positive strict improvement not associated')
    zero=deepcopy(row);zero.update(fixed_K_excluded=False,exact_lower=b.rational(0),exact_upper=b.rational(0),status='PENDING_NONPOSITIVE_EXACT_STAR_BOUND')
    retained,index=b.choose_best(prior,[zero],baseline_lower)
    b.require(index is None and retained is prior,'Nonpositive lower incorrectly adopted')
    pending=deepcopy(row);pending.update(audited=False,fixed_K_excluded=False,status='PENDING_INCOMPLETE_INDEPENDENT_PAIR_AUDIT')
    retained,index=b.choose_best(prior,[pending],baseline_lower)
    b.require(index is None and retained is prior,'Capped candidate incorrectly adopted')
    for path in (Path(__file__),Path(b.__file__),root/'acceleration/build_cp_completion_checkpoint.py'):
        inputs[b.key(path)]=sha256(path.read_bytes()).hexdigest()
    report=dict(status='STAR_GUIDED_CHECKPOINT_ASSOCIATION_CONTROLS_PASS',inputs_sha256=inputs,negative_controls=len(controls),
        controls=controls,positive_controls=['real_prior_baseline','historical_complete_record','exact_shortlist',
        'retain_nonimprovement','adopt_only_positive_strict','nonpositive_pending','cap_pending'],scientific_reruns=0,
        semantic_controls_bypass_hash_guards=True,checkpoint_created=False)
    with args.out.open('x',encoding='utf-8') as stream:stream.write(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],negative_controls=len(controls),positive_controls=7)))


if __name__=='__main__':main()
