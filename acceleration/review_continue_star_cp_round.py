"""Read-only preflight/semantic QA for exactly one star-guided CP round."""
import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from types import SimpleNamespace

import continue_star_cp_round as driver


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();driver.require(not args.out.exists(),'Fresh QA report required')
    previous=driver.ROOT/'acceleration/results/20260916_star_guided_round1_checkpoint.json'
    expected='096464512005d2ad73f86dc26a820d7cb4eb5c99e28de560174bccaf56a0ea9d'
    document=json.loads(previous.read_bytes());current=document['current_star_marginal_best']
    base=SimpleNamespace(previous=str(previous),previous_sha256=expected,kind='same',
        out=str(driver.ROOT/'acceleration/results/never_created_continue_star_cp_same'),max_star_candidates=32)
    old_index,old_run=driver.Index,driver.subprocess.run
    process_calls=[];instances=[];trusted={};patch=None
    class ReviewIndex(old_index):
        def __init__(self):
            super().__init__();instances.append(self)
        def bind(self,name,expected=None):
            label=driver.key(name)
            if label in trusted:
                actual=trusted[label]
                driver.require(expected is None or expected==actual,'Changed cached dependency: '+label)
                self.verified[label]=actual
                return actual
            value=super().bind(name,expected);trusted[label]=value;return value
        def read(self,name,status=None):
            if patch is not None and driver.key(name)==driver.key(previous):
                data=deepcopy(document);patch(data)
                # Semantic controls deliberately rebind the parsed document;
                # actual frozen checkpoint bytes remain unchanged on disk.
                self.bindings(data)
                return data
            return super().read(name,status)
    def forbidden(*args,**kwargs):
        process_calls.append(True)
        raise AssertionError('Preflight attempted a process launch')
    driver.Index,driver.subprocess.run=ReviewIndex,forbidden
    negatives=[];positives=[];inputs={}
    def reject(name,operation):
        try:operation()
        except (ValueError,KeyError,TypeError,FileNotFoundError) as error:
            negatives.append(dict(name=name,rejected=True,exception=type(error).__name__,message=str(error)))
        else:raise ValueError('Accepted invalid control: '+name)
    try:
        for kind,count in (('same',4),('cross',6)):
            test=deepcopy(base);test.kind=kind;test.out=test.out.replace('_same','_'+kind)
            manifest,followups,seed,out=driver.preflight(test)
            inputs.update(manifest['inputs_sha256'])
            driver.require(not out.exists() and manifest['initial_candidate_path']==driver.key(current['best_candidate_path']) and
                manifest['initial_edge_phase1_path']==driver.key(current['edge_phase1_path']) and
                manifest['initial_candidate_path']!=driver.key(document['current_best']['best_candidate_path']),
                'Preflight selected old edge-positive seed or created output')
            driver.require(len(manifest['steps'])==count and [s['stage'] for s in followups]==['star_evaluation','checkpoint'] and
                sum(s['stage']=='native' for s in manifest['steps'])==1 and sum(s['stage']=='search' for s in manifest['steps'])==1 and
                sum(s['stage']=='search_audit' for s in manifest['steps'])==1 and manifest['goal_complete'] is False,
                'More than one round or incorrect stage plan')
            search=next(s for s in manifest['steps'] if s['stage']=='search')['command']
            driver.require(search[search.index('--initial')+1]==driver.key(current['best_candidate_path']) and
                search[search.index('--initial-phase1')+1]==driver.key(current['edge_phase1_path']), 'Search command uses wrong seed')
            cp=[s for s in manifest['previous_summaries'] if s.endswith('/summary.json')]
            driver.require(len(cp)==len(set(cp))==len(manifest['previous_summaries']) and cp,'Previous search exclusion inventory')
            positives.append(dict(kind=kind,status='READ_ONLY_PREFLIGHT_PASS',parent_reference_count=manifest['parent_reference_count'],
                seed_index=current['proposal_index'],seed_path=manifest['initial_candidate_path'],warm_path=manifest['initial_edge_phase1_path'],
                stages=[s['stage'] for s in manifest['steps']+followups],prior_CP_summaries=len(cp),output_created=False))
        for field,value in (('kind','invalid'),('max_star_candidates',0),('max_star_candidates',33),
                            ('previous_sha256','0'*64),('previous_sha256','Z'*64),('out',str(previous.parent)),
                            ('out',str(driver.ROOT.parent/'outside_star_cp_output'))):
            test=deepcopy(base);setattr(test,field,value)
            reject('argument_'+field+'_'+str(value),lambda t=test:driver.preflight(t))
        def semantic_preflight(name,mutation):
            nonlocal patch
            patch=mutation
            try:reject(name,lambda:driver.preflight(base))
            finally:patch=None
        nonseed=next(p for p in document['referenced_files_sha256'] if p.endswith('.rs'))
        for name,mutation in (
            ('malformed_nonseed_reference',lambda d:d['referenced_files_sha256'].update({nonseed:'not-a-sha256'})),
            ('incorrect_nonseed_reference',lambda d:d['referenced_files_sha256'].update({nonseed:'0'*64})),
            ('reference_count_mismatch',lambda d:d.update(verified_referenced_file_count=1)),
            ('unsupported_checkpoint',lambda d:d.update(status='NUMERICAL_ONLY')),
            ('pending_completion',lambda d:d.update(pending_completion_work={'index':1})),
            ('unselected_eligible',lambda d:d.update(unselected_eligible_indices=[1])),
            ('completed_goal',lambda d:d['goal'].update(complete=True)),
            ('inactive_goal',lambda d:d['goal'].update(active=False)),
            ('wrong_objective',lambda d:d['current_star_marginal_best'].update(objective='EDGE_PHASE1')),
            ('seed_outside_refs',lambda d:d['referenced_files_sha256'].pop(current['star_audit_path'])),
        ):semantic_preflight(name,mutation)
        fixture=[document]+[driver.load(current[field+'_path']) for field in
                           ('best_candidate','edge_phase1','star_audit','star_certificate_replay','independent_pair_audit')]
        driver.check_seed(*fixture)
        for name,mutation in (
            ('claimed_graph',lambda d:d[0].update(graph_constructed=True)),
            ('claimed_general_proof',lambda d:d[0].update(general_nonexistence_proved=True)),
            ('claimed_submission',lambda d:d[0].update(submission_txt_exists=True)),
            ('wrong_warm_candidate',lambda d:d[2].update(candidate_sha256='0'*64)),
            ('wrong_warm_path',lambda d:d[2].update(candidate_path='wrong.json')),
            ('nonpositive_star_lower',lambda d:d[0]['current_star_marginal_best']['exact_interval']['lower'].update(numerator='0')),
            ('wrong_star_interval',lambda d:d[3]['exact_primal_upper'].update(numerator='0')),
            ('unverified_replay',lambda d:d[4].update(status='NUMERICAL_ONLY')),
            ('wrong_replay_gap',lambda d:d[4].update(exact_integer_gap=str(int(d[4]['exact_integer_gap'])+1))),
            ('replay_scale_zero',lambda d:d[4].update(integer_scale='0')),
            ('local_incomplete',lambda d:d[5].update(complete_used_domains_verified=False)),
            ('local_empty',lambda d:d[5].update(propagation_status='EMPTY_DOMAIN')),
            ('local_missing_vertex',lambda d:d[5]['independently_reenumerated_domains'].pop()),
            ('repeated_graph_edge',lambda d:d[1]['overlap_edges_outer_zero_based'].__setitem__(1,d[1]['overlap_edges_outer_zero_based'][0])),
        ):
            data=deepcopy(fixture);mutation(data)
            reject(name,lambda d=data:driver.check_seed(*d))
        driver.require(not process_calls and not driver.resolve(base.out).exists(),'Read-only controls launched or wrote outputs')
    finally:
        driver.Index,driver.subprocess.run=old_index,old_run
    for path in (Path(__file__),Path(driver.__file__),previous):
        inputs[driver.key(path)]=sha256(path.read_bytes()).hexdigest()
    report=dict(status='ONE_STAR_CP_ROUND_PREFLIGHT_AND_SEMANTIC_CONTROLS_PASS',inputs_sha256=inputs,
        positive_controls=positives,negative_controls=negatives,negative_control_count=len(negatives),
        parsed_document_semantic_mutations_bypass_only_checkpoint_byte_binding=True,
        all_prior_references_hashed_before_cache_reuse=True,processes_launched=0,science_reruns=0,
        production_output_created=False,old_edge_positive_seed_never_selected=True,goal_marked_complete=False)
    with args.out.open('x',encoding='utf-8') as stream:stream.write(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],positive_controls=len(positives),negative_controls=len(negatives),processes_launched=0)))


if __name__=='__main__':main()
