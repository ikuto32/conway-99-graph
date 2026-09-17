"""Producer-side no-compute controls for the new whole-family mapping wrapper."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
from rank_fresh_whole_v2 import (argument_parser,digest,execution_gate,geometry,key,load_sources,
                                path,read_json,stamp,validate_request,write_json)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--indices',required=True)
    p.add_argument('--out',required=True)
    p.add_argument('--ranking-out',required=True)
    args=p.parse_args()
    command=['--indices',args.indices,'--out',args.ranking_out,'--validate-only']
    rank_args=argument_parser().parse_args(command)
    c=load_sources(rank_args);request=read_json(args.indices)
    validate_request(rank_args,c,request)
    rows=[dict(name='ACTUAL128_REQUEST',outcome='ACCEPT',scope='Positive mapping control; no numeric or graph-existence claim')]

    def reject(name,change):
        corrupted=deepcopy(request);change(corrupted)
        try:validate_request(rank_args,c,corrupted)
        except (ValueError,KeyError,TypeError) as error:
            rows.append(dict(name=name,outcome='REJECT',reason=str(error)));return
        raise ValueError('Corrupted request accepted: '+name)

    reject('DUPLICATE_SELECTION_INDEX',lambda r:r['indices'].__setitem__(1,r['indices'][0]))
    reject('ALREADY_LP_EVALUATED_SELECTION',lambda r:r['indices'].__setitem__(0,r['excluded_current64_indices'][0]))
    reject('FAKE_CROSS_FAMILY_STATUS',lambda r:r.__setitem__('family_status','COMPLETE_CROSS_ATOMIC_CYCLE_SUBFAMILY_EXTRACTION'))
    reject('CHANGED_ORIGINAL_NATIVE_ROW_ID',lambda r:r['records'][0].__setitem__('original_native_index',r['records'][0]['original_native_index']+1))
    reject('CHANGED_CYCLE_SHAPE',lambda r:r['records'][0].__setitem__('alternating_cycle_sizes',[3,4]))
    reject('CHANGED_MATCHING_CLASS',lambda r:r['records'][0].__setitem__('matching_class','cross'))
    reject('CHANGED_RAW_GRAPH_SHA',lambda r:r['records'][0].__setitem__('overlap_edges_sha256','0'*64))
    reject('CHANGED_RAW_CANDIDATE_FILE_SHA',lambda r:r['records'][0].__setitem__('prepared_candidate_sha256','0'*64))
    reject('CHANGED_REFINED_SCORE',lambda r:r['records'][0].__setitem__('refined_upper',r['records'][0]['refined_upper']+1))
    reject('FILTERED_OBJECTIVE_SUBSTITUTION',lambda r:r.__setitem__('objective_id','TRIANGLE_PAIR_FILTERED_STAR_SIMPLEX_V1'))
    reject('CHANGED_ITERATION_CAP',lambda r:r.__setitem__('iterations',501))
    reject('CHANGED_SOURCE_BINDING',lambda r:r['inputs_sha256'].__setitem__('acceleration/rank_fresh_whole_v2.py','0'*64))
    move=deepcopy(c['family']['moves'][request['indices'][0]])
    move['alternating_cycles'][0][0]=move['alternating_cycles'][0][1]
    try:geometry(move)
    except ValueError as error:rows.append(dict(name='CORRUPTED_ALTERNATING_CYCLE',outcome='REJECT',reason=str(error)))
    else:raise ValueError('Corrupted cycle accepted')
    try:execution_gate(rank_args,dict(indices=request['indices']))
    except ValueError as error:rows.append(dict(name='UNREVIEWED_EXECUTION_GATE',outcome='REJECT',reason=str(error)))
    else:raise ValueError('Execution gate accepted missing independent mapping review')
    c['bindings'].recheck()
    write_json(args.out,dict(status='WHOLE_FRESH_V2_PRODUCER_MAPPING_CONTROLS_PASS',created_at=stamp(),
        inputs_sha256={**c['bindings'].values,key(args.indices):digest(args.indices),key(__file__):digest(__file__)},
        controls=rows,control_count=len(rows),native_processes=0,GPU_processes=0,LP_runs=0,
        independent_verification=False,scope='Fail-closed producer mapping and gate controls only; no fresh-star computation executed.'))
    print(json.dumps(dict(status='WHOLE_FRESH_V2_PRODUCER_MAPPING_CONTROLS_PASS',controls=len(rows),
        native_processes=0,GPU_processes=0,LP_runs=0,sha256=digest(args.out))))


if __name__=='__main__':main()
