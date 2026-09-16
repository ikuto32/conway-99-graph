"""Read-only preflight/invalid-input controls; GPU and LP calls are forbidden."""
import argparse
from contextlib import redirect_stdout
from copy import deepcopy
from hashlib import sha256
import io
import json
from pathlib import Path
import sys
import time
from unittest.mock import patch

import search_cp_matching_v2 as driver

ROOT=Path(__file__).resolve().parents[1]
R=ROOT/'acceleration/results'


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def key(path):
    return path.resolve().relative_to(ROOT).as_posix()


def require(ok,message):
    if not ok:
        raise ValueError(message)


def write_new(path,data):
    with path.open('x',encoding='utf-8') as stream:
        json.dump(data,stream,separators=(',',':'),allow_nan=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=False)
    started=time.perf_counter()
    native=R/'20260916_cp_round2_family/all.json'
    family=R/'20260916_cp_round2_family/independent_audit.json'
    initial=R/'20260916_cp_matching_search/adopted_index_59390/best_candidate.json'
    warm=R/'20260916_cp_matching_search/adopted_index_59390/best_phase1.json'
    previous=R/'20260916_cp_matching_search/summary.json'
    sources=[Path(__file__),ROOT/'acceleration/search_cp_matching_v2.py',ROOT/'acceleration/search_cp_matching.py']
    bound={key(path):digest(path) for path in [native,family,initial,warm,previous,*sources]}
    common=['--native',str(native),'--family-audit',str(family),'--initial',str(initial),
            '--initial-phase1',str(warm),'--previous-summary',str(previous)]
    original_warm=json.loads(warm.read_bytes())
    records=[]
    forbidden=[]

    def forbid(*_args,**_kwargs):
        forbidden.append('CALLED')
        raise AssertionError('GPU/LP work is forbidden in input controls')

    def run(name,overrides=(),positive=False):
        out=args.out/(name+'_must_not_exist')
        argv=['search_cp_matching_v2',*common,'--out',str(out),*overrides]
        if positive:
            argv.append('--validate-only')
        printed=io.StringIO()
        try:
            with patch.object(sys,'argv',argv), patch.object(driver.subprocess,'run',side_effect=forbid), \
                 patch.object(driver,'solve_edges_with_basis',side_effect=forbid), redirect_stdout(printed):
                driver.main()
        except ValueError as exc:
            require(not positive,'Positive preflight rejected: '+str(exc))
            records.append(dict(name=name,expected='REJECT',observed='REJECT',reason=str(exc),
                                overrides=list(overrides),gpu_or_lp_calls=0,output_directory_created=out.exists()))
        else:
            require(positive,'Invalid input was accepted: '+name)
            parsed=json.loads(printed.getvalue())
            require(parsed['status']=='CP_MATCHING_V2_INPUT_VALIDATION_PASS','Unexpected validation status')
            records.append(dict(name=name,expected='PASS',observed='PASS',validation=parsed,
                                overrides=list(overrides),gpu_or_lp_calls=0,output_directory_created=out.exists()))
        require(not forbidden and not out.exists(),'A validation case launched work or created output')

    run('current_family_and_previous64',positive=True)
    run('repeated_previous_summary_deduplicated',['--previous-summary',str(previous)],positive=True)
    identity=args.out/'identical_graph_different_wrapper.json'
    content=json.loads(initial.read_bytes());content['preflight_control_note']='Same exact labeled K in a new wrapper'
    write_new(identity,content);bound[key(identity)]=digest(identity)
    run('same_labeled_base_new_wrapper',['--initial',str(identity)],positive=True)
    require(records[-1]['validation']['family_association']['base_method']=='EXACT_LABELED_GRAPH_IDENTITY','Identity method not recorded')
    for name,flags in [
        ('family_mismatch',['--family-audit',str(R/'20260916_cp_new_seed_family/independent_audit.json')]),
        ('native_mismatch',['--native',str(R/'20260916_cp_new_seed_family/all.json')]),
        ('base_mismatch',['--initial',str(R/'20260916_two_trade_pilot/best_candidate.json')]),
        ('lp_count_below32',['--lp-count','31']),('lp_count_above64',['--lp-count','65']),
        ('refine_count_below140',['--refine-count','139']),('refine_count_above99999',['--refine-count','100000']),
        ('zero_coarse_steps',['--coarse-steps','0']),('equal_stage_steps',['--coarse-steps','500','--refine-steps','500']),
        ('iteration_cap_exceeded',['--refine-steps','1000001']),
        ('different_gpu_binary',['--gpu',str(ROOT/'acceleration/build/overlap_cp_cpu.exe')]),
        ('different_gpu_source',['--gpu-source',str(ROOT/'acceleration/overlap_cp_cpu.rs')])]:
        run(name,flags)

    def bad_warm(name,mutate):
        data=deepcopy(original_warm);mutate(data)
        path=args.out/(name+'.json');write_new(path,data);bound[key(path)]=digest(path)
        run(name,['--initial-phase1',str(path)])

    bad_warm('nan_raw_dual',lambda d:d['phase1_multipliers'].__setitem__(0,float('nan')))
    bad_warm('inf_raw_dual',lambda d:d['phase1_multipliers'].__setitem__(0,float('inf')))
    bad_warm('short_raw_dual',lambda d:d['phase1_multipliers'].pop())
    bad_warm('long_raw_dual',lambda d:d['phase1_multipliers'].append(0))
    bad_warm('duplicate_semantic_key',lambda d:d['constraint_groups'].__setitem__(1,deepcopy(d['constraint_groups'][0])))
    bad_warm('nan_raw_x',lambda d:d['numeric_edge_values'].__setitem__(0,float('nan')))
    bad_previous=json.loads(previous.read_bytes());bad_previous['records'][0]['candidate_sha256']='0'*64
    path=args.out/'previous_candidate_hash_mismatch.json';write_new(path,bad_previous);bound[key(path)]=digest(path)
    run('previous_candidate_hash_mismatch',['--previous-summary',str(path)])
    for row in records[:3]:
        require(row['validation']['previous_candidate_artifacts']==257 and row['validation']['previous_unique_edge_signatures']==257,
                'Prior-summary exclusion count differs')
    require(all(digest(ROOT/path)==expected for path,expected in bound.items()),'Frozen input/source changed during QA')
    report=dict(status='CP_SEARCH_V2_PREFLIGHT_AND_CORRUPTION_CONTROLS_PASS',inputs_sha256=bound,
                producer_sha256=digest(ROOT/'acceleration/search_cp_matching_v2.py'),
                positive_controls=sum(row['observed']=='PASS' for row in records),
                negative_controls=sum(row['observed']=='REJECT' for row in records),records=records,
                gpu_launches=0,lp_solves=0,driver_output_directories_created=0,previous_source_preserved=True,
                elapsed_seconds=time.perf_counter()-started,
                scope='Real current-family preflight plus malformed input controls. No search/GPU/LP executed; statistical and mathematical search claims require separate run audits.')
    write_new(args.out/'report.json',report)
    print(json.dumps({name:report[name] for name in ('status','positive_controls','negative_controls','gpu_launches','lp_solves','elapsed_seconds')}))


if __name__=='__main__':
    main()
