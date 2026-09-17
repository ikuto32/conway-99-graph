"""Synthetic engineering controls for honest whole-ranking shortlist adaptation.

Fixtures stay in memory and are never serialized as scientific ranking/audit
artifacts. No graph search, domain enumeration, GPU, LP, or old experiment runs.
"""
import argparse
from copy import deepcopy
from datetime import datetime,timezone
import json
from pathlib import Path

import evaluate_fresh_whole_v2 as e


def fixtures():
    moves=[dict(root_group=i%7,matching_class='same_'+str(i%2),changed_edges=4,
        alternating_cycles=[[0,1,2,3],[4,5,6,7]]) for i in range(20)]
    family=dict(status='COMPLETE_WHOLE_SAME_SIGN_MATCHING_SUBFAMILY_ENUMERATION',selector='all',
                legal_count=20,overlap_candidates=[None]*20,moves=moves)
    rows=[dict(proposal_index=i,original_native_index=i,available=True,best_upper_numeric=30.+i,
        best_lower_numeric=20.-i,candidate_path='IN_MEMORY_ONLY',candidate_sha256='NOT_AN_ARTIFACT',
        domains_path='IN_MEMORY_ONLY',domains_sha256='NOT_AN_ARTIFACT') for i in range(20)]
    upper=list(range(20));lower=list(reversed(upper))
    audit=dict(status=e.RANKING_AUDIT_STATUS,producer_or_native_imported=False,all_serialized_models_reconstructed=True,
        independent_domain_enumeration_performed=False,records=rows,input_selected_indices=upper,
        numeric_cpu_controls=[dict(proposal_index=i) for i in (0,10,19)],
        ranked_by_upper_indices=upper,ranked_by_lower_indices=lower,
        evaluation_selections={'union_16':e.evaluation_selection(upper,lower,16,'union')})
    ranking=dict(status='NUMERICAL_WHOLE_FRESH_STAR_PDHG_RANKING_FINISHED',producer_version='whole_fresh_v2_balanced',
        objective_id=e.OBJECTIVE,original_complete_domains_used=True,pair_pruned_domains_used=False,
        independently_audited_original_domains=False,input_selected_indices=upper,
        records=[dict(**r,status='NUMERICALLY_SCORED',root_group=moves[i]['root_group'],matching_class=moves[i]['matching_class'],
                      changed_edges=4,alternating_cycle_sizes=[2,2]) for i,r in enumerate(rows)])
    return ranking,audit,family


def review():
    ranking,audit,family=fixtures()
    e.verify_whole_records(ranking,audit,family)
    selected,_,_,_=e.select_records(audit,family,16,'union')
    e.require([r['proposal_index'] for r in selected]==list(range(8))+list(range(19,11,-1)),'Union8+8 selection')
    overlap=e.evaluation_selection(list(range(20)),list(range(20)),16,'union')
    e.require([r['proposal_index'] for r in overlap]==list(range(16)) and overlap[0]['selection_roles']==['upper','lower']
        and overlap[8]['selection_roles']==['upper_fill'],'Union fill/roles')
    e.require(len(e.evaluation_selection([0,1],[1,0],16,'union'))==2,'Fewer-than16 available case')
    controls=[dict(name='WHOLE_MULTI_CYCLE_RECORD_AND_UNION16',outcome='ACCEPT'),
              dict(name='OVERLAP_ROLES_AND_FILL',outcome='ACCEPT'),dict(name='ONLY_TWO_AVAILABLE',outcome='ACCEPT')]

    def reject(name,call):
        try:call()
        except (ValueError,KeyError,TypeError) as error:controls.append(dict(name=name,outcome='REJECT',reason=str(error)))
        else:raise ValueError('Corruption accepted: '+name)

    for name,change in (
        ('LEGACY_CROSS_AUDIT_STATUS',lambda r,a,f:a.update(status='INDEPENDENT_FRESH_STAR_PDHG_RANKING_AUDIT_PASS')),
        ('AUDITOR_IMPORTED_PRODUCER',lambda r,a,f:a.update(producer_or_native_imported=True)),
        ('MODEL_NOT_REBUILT',lambda r,a,f:a.update(all_serialized_models_reconstructed=False)),
        ('MISSING_NUMERIC_REPLAY',lambda r,a,f:a.update(numeric_cpu_controls=[])),
        ('FAKE_DOMAIN_COMPLETENESS',lambda r,a,f:a.update(independent_domain_enumeration_performed=True)),
        ('DUPLICATE_INDEX',lambda r,a,f:a['records'][1].update(proposal_index=0)),
        ('WRONG_NATIVE_INDEX',lambda r,a,f:a['records'][1].update(original_native_index=2)),
        ('BOOLEAN_NATIVE_INDEX',lambda r,a,f:a['records'][1].update(original_native_index=True)),
        ('NONFINITE_SCORE',lambda r,a,f:a['records'][1].update(best_upper_numeric=float('inf'))),
        ('UNAVAILABLE_BUT_SCORED',lambda r,a,f:a['records'][1].update(available=False)),
        ('CHANGED_UNION_ROLES',lambda r,a,f:a['evaluation_selections']['union_16'][0].update(selection_roles=['lower'])),
        ('CROSS_FAMILY_STATUS',lambda r,a,f:f.update(status='COMPLETE_CROSS_ATOMIC_CYCLE_SUBFAMILY_EXTRACTION')),
    ):
        r,a,f=deepcopy([ranking,audit,family]);change(r,a,f)
        reject(name,lambda a=a,f=f:e.select_records(a,f,16,'union'))
    for name,change in (
        ('FILTERED_OBJECTIVE',lambda r,a,f:r.update(objective_id='TRIANGLE_PAIR_FILTERED_STAR_SIMPLEX_V1')),
        ('FILTERED_TABLE_FLAG',lambda r,a,f:r.update(pair_pruned_domains_used=True)),
        ('MISSING_ORIGINAL_FLAG',lambda r,a,f:r.update(original_complete_domains_used=False)),
        ('WRONG_PRODUCER_VERSION',lambda r,a,f:r.update(producer_version='fresh1')),
        ('WRONG_WHOLE_GEOMETRY',lambda r,a,f:r['records'][0].update(alternating_cycle_sizes=[4])),
        ('FAKE_SINGLE_CYCLE',lambda r,a,f:r['records'][0].update(alternating_cycle_sizes=[3])),
        ('CROSS_MATCHING_CLASS',lambda r,a,f:r['records'][0].update(matching_class='cross')),
        ('AUDIT_GRAPH_HASH_MISMATCH',lambda r,a,f:a['records'][0].update(candidate_sha256='OTHER')),
        ('AUDIT_DOMAIN_HASH_MISMATCH',lambda r,a,f:a['records'][0].update(domains_sha256='OTHER')),
        ('AUDIT_NATIVE_ID_MISMATCH',lambda r,a,f:a['records'][0].update(original_native_index=1)),
        ('BOOLEAN_RANK_NATIVE_ID',lambda r,a,f:r['records'][1].update(original_native_index=True)),
    ):
        r,a,f=deepcopy([ranking,audit,family]);change(r,a,f)
        reject(name,lambda r=r,a=a,f=f:e.verify_whole_records(r,a,f))
    reject('WRONG_SELECTION_MODE',lambda:e.select_records(audit,family,16,'upper'))
    reject('WRONG_SELECTION_SIZE',lambda:e.select_records(audit,family,8,'union'))
    reject('BOOLEAN_SELECTION_SIZE',lambda:e.select_records(audit,family,True,'union'))
    # Verify that an absent auditor source prevents actual preflight before any
    # output or solver operation. Do not fake a successful audit report.
    return controls


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    e.require(not e.resolve(args.out).exists(),'Preserve previous controls')
    controls=review()
    inputs={e.key(Path(__file__)):e.digest(__file__),e.key(Path(e.__file__)):e.digest(e.__file__)}
    for name,h in e.PINS.items():
        p=e.ROOT/'acceleration'/name;e.require(e.digest(p)==h,'Changed frozen helper');inputs[e.key(p)]=h
    for name,h in e.ROOT_PINS.items():
        p=e.ROOT/name;e.require(e.digest(p)==h,'Changed frozen root helper');inputs[e.key(p)]=h
    result=dict(status='WHOLE_FRESH_SHORTLIST_V2_SYNTHETIC_CONTROLS_PASS',created_at=datetime.now(timezone.utc).isoformat(),
        inputs_sha256=inputs,controls=controls,control_count=len(controls),processes_launched=0,
        scientific_fixture_artifacts_written=False,actual_ranking_preflight=None,
        actual_ranking_preflight_reason='Future numerical ranking and independent ranking audit not yet available at adapter preparation',
        independent_verification=False,scope='Producer engineering controls only; frozen selection contract and whole-family metadata handoff.')
    e.resolve(args.out).parent.mkdir(parents=True,exist_ok=True);e.save(args.out,result)
    print(json.dumps(dict(status=result['status'],control_count=len(controls),processes_launched=0,sha256=e.digest(args.out))))


if __name__=='__main__':main()
