"""Cross-driver preflight controls; all GPU and LP entry points are forbidden."""
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

import search_cp_cross as driver

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / 'acceleration/results'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def key(path):
    return path.resolve().relative_to(ROOT).as_posix()


def encoded(value):
    return (json.dumps(value, separators=(',', ':'), allow_nan=True) + '\n').encode()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    native = R/'20260916_cp_cross_current_family/cross.json'
    family = R/'20260916_cp_cross_current_family/cross_audit.json'
    initial = R/'20260916_cp_matching_round3/adopted_index_16044/best_candidate.json'
    warm = initial.with_name('best_phase1.json')
    previous = [R/name/'summary.json' for name in
                ('20260916_cp_matching_search', '20260916_cp_matching_round2', '20260916_cp_matching_round3')]
    gpu_audit = R/'20260916_cp_gpu_layout_v2_controls/audit.json'
    gpu = ROOT/'acceleration/build/overlap_cp_gpu_layout_v2.exe'
    gpu_source = ROOT/'acceleration/overlap_cp_gpu_layout_v2.cu'
    inputs = {key(p): digest(p) for p in [native, family, initial, warm, gpu_audit, gpu, gpu_source, *previous,
              Path(__file__), ROOT/'acceleration/search_cp_cross.py', ROOT/'acceleration/search_cp_matching_v2.py']}
    family_json, native_json = json.loads(family.read_bytes()), json.loads(native.read_bytes())
    for report in (family_json, json.loads(gpu_audit.read_bytes())):
        for name, expected in report['inputs_sha256'].items():
            require(digest(ROOT/name) == expected, 'Changed preflight dependency')
            inputs[name] = expected
    common = ['--native', str(native), '--family-audit', str(family), '--initial', str(initial),
              '--initial-phase1', str(warm), '--gpu', str(gpu), '--gpu-source', str(gpu_source),
              '--gpu-audit', str(gpu_audit)]
    for prior in previous:
        common.extend(['--previous-summary', str(prior)])
    records, forbidden = [], []
    original_read = Path.read_bytes

    def forbid(*_args, **_kwargs):
        forbidden.append('CALLED')
        raise AssertionError('GPU/LP work is forbidden in these controls')

    def run(name, overrides=(), positive=False, virtual=None):
        virtual = virtual or {}
        virtual = {p.resolve(): value for p, value in virtual.items()}
        out = args.out/(name+'_must_not_exist')
        argv = ['search_cp_cross', *common, '--out', str(out), *overrides]
        if positive:
            argv.append('--validate-only')
        printed = io.StringIO()
        def read(path):
            return virtual[path.resolve()] if path.resolve() in virtual else original_read(path)
        try:
            with patch.object(sys, 'argv', argv), patch.object(Path, 'read_bytes', read), \
                 patch.object(driver.subprocess, 'run', side_effect=forbid), \
                 patch.object(driver, 'solve_edges_with_basis', side_effect=forbid), redirect_stdout(printed):
                driver.main()
        except ValueError as exc:
            require(not positive, 'Positive control rejected: '+str(exc))
            result = dict(expected='REJECT', observed='REJECT', reason=str(exc))
        else:
            require(positive, 'Invalid input accepted: '+name)
            validation = json.loads(printed.getvalue())
            require(validation['status'] == 'CP_CROSS_INPUT_VALIDATION_PASS' and
                    validation['producer_version'] == 'cross1', 'Unexpected positive status')
            require(validation['candidate_count'] == 8899 and validation['previous_candidate_artifacts'] == 385
                    and validation['previous_unique_edge_signatures'] == 385, 'Candidate/prior binding counts differ')
            result = dict(expected='PASS', observed='PASS', validation=validation)
        require(not forbidden and not out.exists(), 'A control performed work or created output')
        records.append(dict(name=name, **result, overrides=list(overrides),
                            virtual_input_sha256={key(p): sha256(v).hexdigest() for p, v in virtual.items()},
                            gpu_or_lp_calls=0, output_directory_created=False))

    run('current_cross_with_three_priors', positive=True)
    run('repeated_prior_summary_deduplicated', ['--previous-summary', str(previous[1])], positive=True)
    run('original_gpu_still_supported', ['--gpu', str(ROOT/'acceleration/build/overlap_cp_gpu.exe'),
         '--gpu-source', str(ROOT/'acceleration/overlap_cp_gpu.cu'),
         '--gpu-audit', str(R/'20260916_cp_gpu_controls/audit.json')], positive=True)
    wrapper = args.out/'virtual_identical_base.json'
    same = json.loads(initial.read_bytes()); same['test_note'] = 'Same exact labeled base K'
    run('same_labeled_base_wrapper', ['--initial', str(wrapper)], positive=True, virtual={wrapper: encoded(same)})
    require(records[-1]['validation']['family_association']['base_method'] == 'EXACT_LABELED_GRAPH_IDENTITY', 'Wrong wrapper method')
    copy = args.out/'virtual_identical_native.json'
    run('identical_native_bytes', ['--native', str(copy)], positive=True, virtual={copy: native.read_bytes()})
    require(records[-1]['validation']['family_association']['native_method'] == 'IDENTICAL_BOUND_BYTES', 'Wrong payload identity method')
    for name, overrides in [
        ('wrong_same_sign_family', ['--family-audit', str(R/'20260916_cp_round2_family/independent_audit.json')]),
        ('wrong_cross_family_base', ['--family-audit', str(R/'20260916_cp_cross_family_qa/cross_independent_audit.json')]),
        ('wrong_native_cross_base', ['--native', str(R/'20260916_cp_cross_family_qa/cross.json')]),
        ('wrong_initial_graph', ['--initial', str(R/'20260916_two_trade_pilot/best_candidate.json')]),
        ('wrong_warm_graph', ['--initial-phase1', str(R/'20260916_two_trade_pilot/best_phase1.json')]),
        ('bad_lp_count', ['--lp-count', '65']), ('bad_refine_count', ['--refine-count', '139']),
        ('bad_stage_order', ['--coarse-steps', '500', '--refine-steps', '500']),
        ('wrong_gpu', ['--gpu', str(ROOT/'acceleration/build/overlap_cp_cpu.exe')]),
        ('wrong_gpu_source', ['--gpu-source', str(ROOT/'acceleration/overlap_cp_cpu.rs')])]:
        run(name, overrides)

    def bad_warm(name, mutate):
        obj = json.loads(warm.read_bytes()); mutate(obj)
        path = args.out/('virtual_'+name+'.json')
        run(name, ['--initial-phase1', str(path)], virtual={path: encoded(obj)})
    bad_warm('nan_raw_dual', lambda d: d['phase1_multipliers'].__setitem__(0, float('nan')))
    bad_warm('inf_raw_dual', lambda d: d['phase1_multipliers'].__setitem__(0, float('inf')))
    bad_warm('short_raw_dual', lambda d: d['phase1_multipliers'].pop())
    bad_warm('duplicate_semantic_key', lambda d: d['constraint_groups'].__setitem__(1, deepcopy(d['constraint_groups'][0])))
    bad_warm('nan_raw_x', lambda d: d['numeric_edge_values'].__setitem__(0, float('nan')))
    bad_prior = json.loads(previous[0].read_bytes()); bad_prior['records'][0]['candidate_sha256'] = '0'*64
    path = args.out/'virtual_bad_previous_hash.json'
    run('wrong_previous_candidate_hash', ['--previous-summary', str(path)], virtual={path: encoded(bad_prior)})

    def bad_native(name, mutate):
        obj = deepcopy(native_json); mutate(obj)
        npath, fpath = args.out/('virtual_'+name+'_native.json'), args.out/('virtual_'+name+'_family.json')
        raw = encoded(obj)
        proof = deepcopy(family_json)
        del proof['inputs_sha256'][key(native)]
        proof['inputs_sha256'][key(npath)] = sha256(raw).hexdigest()
        run(name, ['--native', str(npath), '--family-audit', str(fpath)],
            virtual={npath: raw, fpath: encoded(proof)})
        records[-1]['native_hash_rebound_to_reach_semantic_guard'] = True
    bad_native('wrong_selector', lambda d: d.__setitem__('selector', 'all'))
    bad_native('missing_cycle_shape', lambda d: d.__setitem__('cycle_sizes', [3]))
    bad_native('wrong_original_index', lambda d: d['moves'][0].__setitem__('original_native_index', -1))
    bad_native('wrong_matching_class', lambda d: d['moves'][0].__setitem__('matching_class', 'same_0'))
    bad_native('wrong_root_group', lambda d: d['moves'][0].__setitem__('root_group', (d['moves'][0]['root_group']+1)%7))
    bad_native('wrong_cycle_colors', lambda d: d['moves'][0]['alternating_cycle'].reverse())
    bad_native('wrong_candidate_order', lambda d: d['overlap_candidates'].__setitem__(0, deepcopy(d['overlap_candidates'][1])))
    bad_native('wrong_source_candidate_binding', lambda d: d.__setitem__('candidate_sha256', '0'*64))
    bad_native('wrong_legal_count', lambda d: d.__setitem__('legal_count', d['legal_count']-1))

    scores = {i: float((i*997) % 10007) for i in range(len(native_json['moves']))}
    choices = driver.choose(list(scores), scores, native_json['moves'], 64, 32)
    chosen = [row['proposal_index'] for row in choices]
    require(len(set(chosen)) == 64 and all(native_json['moves'][i]['matching_class'] == 'cross' for i in chosen), 'Cross selection failed')
    for group in range(7):
        for size in (3, 4):
            expected = min((i for i, move in enumerate(native_json['moves']) if (move['root_group'], move['cycle_size']) == (group, size)),
                           key=lambda i: (scores[i], i))
            require(expected in chosen, 'Cross selection lost a coordinate/size minimum')
    require(all(digest(ROOT/name) == expected for name, expected in inputs.items()), 'Frozen dependency changed')
    report = dict(status='CP_CROSS_PREFLIGHT_AND_CORRUPTED_FAMILY_ASSOCIATION_CONTROLS_PASS', inputs_sha256=inputs,
                  positive_controls=sum(r['observed']=='PASS' for r in records), negative_controls=sum(r['observed']=='REJECT' for r in records),
                  records=records, cross_selection_control=dict(candidates=8899, selected=64, coordinate_size_minima_present=14),
                  gpu_launches=0, lp_solves=0, driver_output_directories_created=0, previous_sources_preserved=True,
                  elapsed_seconds=time.perf_counter()-started,
                  scope='Preflight and association guards only. Hash-rebound virtual corruptions exercise semantics without editing artifacts. No GPU or LP search; family completeness and later search results require their independent audits.')
    with (args.out/'report.json').open('x', encoding='utf-8') as stream:
        json.dump(report, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps({k: report[k] for k in ('status', 'positive_controls', 'negative_controls', 'gpu_launches', 'lp_solves', 'elapsed_seconds')}))


if __name__ == '__main__':
    main()
