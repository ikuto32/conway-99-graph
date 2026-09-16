"""Semantic corruption controls for completion-index associations, no solving."""
import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

import build_cp_completion_checkpoint as b


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);args=p.parse_args()
    b.require(not args.out.exists(),'Preserve prior controls')
    root=b.ROOT;zero=root/'acceleration/results/20260916_cp_zero_completion'
    candidate=root/'acceleration/results/20260916_cp_round9_auto/search/probes/selection_07_index_226_candidate.json'
    paths=[candidate.parent.parent/'summary.json',candidate.parent.parent/'audit.json',zero/'cnf_226/manifest.json',
           zero/'cnf_226/independent_audit.json',zero/'sat_226/result.json',zero/'drat_226/proof_generation.json',
           zero/'drat_226/independent_drat_audit.json',zero/'local_226/independent_pair_audit.json']
    search,audit,made,mapped,sat,produced,drat,local=map(b.read_json,paths)
    row=next(r for r in search['records'] if r['proposal_index']==226)
    report=next(r for r in audit['probe_reports'] if r['proposal_index']==226)
    fixture=[row,report,made,mapped,sat,produced,drat,local]
    candidate_sha=sha256(candidate.read_bytes()).hexdigest()
    def check(data):
        b.check_case_semantics(226,candidate,candidate_sha,*data)
    check(fixture)
    cases=[]
    mutations=[
        ('wrong_CP_index',lambda x:x[0].__setitem__('proposal_index',2700)),
        ('wrong_CP_candidate',lambda x:x[0].__setitem__('candidate_path','elsewhere.json')),
        ('wrong_CP_result',lambda x:x[1].__setitem__('result_path','elsewhere.json')),
        ('positive_edge_lower',lambda x:x[1]['phase1_audit']['exact_dual_lower_bound'].__setitem__('numerator','1')),
        ('nonzero_edge_upper',lambda x:x[1]['phase1_audit']['exact_primal_upper_bound'].__setitem__('numerator',x[1]['phase1_audit']['exact_primal_upper_bound']['denominator'])),
        ('wrong_CNF_candidate',lambda x:x[2].__setitem__('candidate_sha256','0'*64)),
        ('wrong_CNF_bytes',lambda x:x[3].__setitem__('cnf_sha256','0'*64)),
        ('wrong_SAT_status',lambda x:x[4].__setitem__('status','UNKNOWN')),
        ('SAT_claims_witness',lambda x:x[4].__setitem__('validated_witness',{})),
        ('proof_incomplete',lambda x:x[5].__setitem__('status','UNKNOWN')),
        ('synthesized_empty',lambda x:x[5]['solver_record'].__setitem__('terminal_empty_clause_synthesized',True)),
        ('DRAT_failure_return',lambda x:x[6].__setitem__('return_code',1)),
        ('DRAT_false_flag',lambda x:x[6].__setitem__('verified',False)),
        ('DRAT_missing_verified_line',lambda x:x[6].__setitem__('transcript','s NOT VERIFIED\n')),
        ('DRAT_wrong_proof',lambda x:x[6].__setitem__('proof_sha256','0'*64)),
        ('local_incomplete',lambda x:x[7].__setitem__('complete_used_domains_verified',False)),
        ('local_missing_vertex',lambda x:x[7]['independently_reenumerated_domains'].pop()),
        ('local_empty',lambda x:x[7].__setitem__('propagation_status','EMPTY_DOMAIN'))]
    for name,mutate in mutations:
        changed=deepcopy(fixture);mutate(changed)
        try:check(changed)
        except ValueError as exc:cases.append(dict(name=name,rejected=True,reason=str(exc)))
        else:raise ValueError('Corruption accepted: '+name)
    book=b.Index()
    try:book.bind(candidate,'0'*64)
    except ValueError:cases.append(dict(name='wrong_actual_file_hash',rejected=True))
    else:raise ValueError('Wrong file hash accepted')
    inputs={b.key(path):sha256(path.read_bytes()).hexdigest() for path in paths+[candidate,Path(__file__),root/'acceleration/build_cp_completion_checkpoint.py']}
    result=dict(status='CP_COMPLETION_CHECKPOINT_ASSOCIATION_CONTROLS_PASS',inputs_sha256=inputs,
                real_case_semantics_positive=True,negative_controls=cases,all_negative_controls_rejected=True,
                semantic_fixtures_in_memory_bypass_hashes_to_reach_guards=True,files_mutated=False,
                solver_or_domain_reruns=0,final_index_created=False,
                scope='Pure association guards plus an actual wrong-SHA rejection; full hash/11-case/star-best validation is separately run in validate-only mode.')
    with args.out.open('x',encoding='utf-8') as stream:stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'negative_controls':len(cases)}))


if __name__=='__main__':main()
