"""New independent generic strict-lex graph projection and census audit.

SOURCE PREPARATION: no computation or gate approval from existence of this file.
No producer imports; independent prior K/S/R/G and new graph core are disclosed.
"""
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import sys
from types import SimpleNamespace
from tqdm import tqdm
from command_deadline import CommandDeadline
import audit_20261003_root_focused_chain_graph_core_v1 as C
import audit_20261003_root_focused_census_core_v1 as K
import audit_20261003_root_focused_core_v2 as S
import audit_20261003_root_focused_census_records_v2 as R
import audit_20261003_root_focused_neighbor_graph_v1 as G

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'acceleration/audit_20261003_root_focused_chain_v1.py'
SPEC = 'acceleration/audit_20261003_root_focused_chain_v1_spec.md'
CORE = 'acceleration/audit_20261003_root_focused_chain_graph_core_v1.py'
CAL = 'INDEPENDENT_FROZEN_ROOT_STRICT_LEX_CHECKER_V1_CALIBRATION_PASS'
GRAPH_CONTROLS = 'INDEPENDENT_FROZEN_ROOT_STRICT_LEX_GRAPH_PROJECTION_V1_CONTROLS_PASS'
GRAPH_PASS = 'INDEPENDENT_FROZEN_ROOT_STRICT_LEX_GRAPH_PROJECTION_V1_COMPLETE_PASS'
CENSUS_CONTROLS = 'INDEPENDENT_FROZEN_ROOT_STRICT_LEX_TWO_LINE_V1_CONTROLS_PASS'
CENSUS_PASS = 'INDEPENDENT_FROZEN_ROOT_STRICT_LEX_TWO_LINE_V1_COMPLETE_PASS'

NATIVE = {
 'acceleration/project_20261003_root_focused_chain_graph_v2.py': '5c22e4fec65ef3d95ae3f6e09023b3067b674d1a631c228e09b2282daa5d2aab',
 'acceleration/project_20261003_root_focused_chain_graph_v2_spec.md': '80d5e9148bd8bf387448483e3dd470c3418dea1d7ecaeb392a9e4bf63a2ed2a3',
 'acceleration/census_20261003_root_focused_chain_v2.py': 'fcf84498063d26cb36c003cc3868b865d7e6b7ef3a3da6594b335b1e5a3444ea',
 'acceleration/census_20261003_root_focused_chain_v2_spec.md': '6248f794c0413f4a0d445cc537b326d81576979a8f31c057ccf5a6b18b568b27',
}
PROJECTOR = 'acceleration/project_20261003_root_focused_chain_graph_v2.py'
PROJECTOR_SPEC = 'acceleration/project_20261003_root_focused_chain_graph_v2_spec.md'
CALLER = 'acceleration/census_20261003_root_focused_chain_v2.py'
CALLER_SPEC = 'acceleration/census_20261003_root_focused_chain_v2_spec.md'
SHARED = {
 'acceleration/audit_20261003_root_focused_census_core_v1.py': '78fdaa10e0056ca048b9e31049dc2e30951cfaa7dba418751a98008a2a69168c',
 'acceleration/audit_20261003_root_focused_core_v2.py': '5cd58d2936e5ffea2b86f0ed85ae85038b056a9fbe4205039eb867443b0d1579',
 'acceleration/audit_20261003_root_focused_census_records_v2.py': 'aa38a907d7962c475d7fc5fd25e9c0c95c15732d5285d9b0848d877fe79bea96',
 'acceleration/audit_20261003_root_focused_neighbor_graph_v1.py': '434ba53ed2e00663fa8464930bd3000457fd04158265fa0d7184048deb19be02',
 'acceleration/audit_20261003_root_focused_census_core_v1_spec.md': 'db48d13241e4fa1ae82b783593357e9cf051c68528073ae4dd600d859d4e30c6',
 'acceleration/audit_20261003_root_focused_census_records_v2_spec.md': '6a5fb3de50fc003a476550737498e46bc977ba1e435268e0a5453b8be375c5d9',
 'acceleration/audit_20261003_root_focused_neighbor_graph_v1_spec.md': 'f6dd849519a13ca4abd9bab812631313dc52580f3afac9a43cf03c043cfc0f8a',
 'acceleration/audit_20261003_root_focused_neighbor_census_v1.py': 'e01f2cda71f5cff8743fffbb5ee3227ae655e4b788476d03db025536871877d3',
 'acceleration/audit_20261003_root_focused_neighbor_census_v1_spec.md': '72911e9be2402d996d246c40a5cd0df5d88b3695523c1f6d045cb846f5ddb5e8',
}
OLD_SOFTWARE = {
 G.PRODUCER: G.PINS[G.PRODUCER], G.PRODUCER_SPEC: G.PINS[G.PRODUCER_SPEC],
 R.PRODUCER: R.PRODUCER_SHA, R.PRODUCER_SPEC: R.PRODUCER_SPEC_SHA,
 'acceleration/command_deadline.py': '9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9',
 'acceleration/run_compute_command.py': '593a9feed6250739dc9672338df23ab171fc9a6a6db4196c1feb312efa33957a',
 'acceleration/native_budget_env_v1/pyproject.toml': '96f96d7345153b4bde50d7f4a640a33d43dfd6458c35f4e6a4ab798b11673782',
 'acceleration/native_budget_env_v1/uv.lock': '54ecb16b929dac1035b5a8691df419d58eab33dc3f07c76c5259094e265a4434',
}


def need(ok, stage, detail):
    C.need(ok, stage, detail)


def sha(path):
    return G.sha(path)


def save(path, value):
    G.save(path, value)


def read_json(path):
    return C.loads(path.read_bytes())


def graph_software():
    return {**OLD_SOFTWARE, **{name: NATIVE[name] for name in [PROJECTOR, PROJECTOR_SPEC]}}


def census_software():
    return {**OLD_SOFTWARE, **NATIVE}


def terminal(ended, manifest):
    cleanup = ended.get('cleanup', {})
    need(type(ended.get('command_exit_code')) is int and ended['command_exit_code'] == 0
         and ended.get('error') is None and ended.get('deadline_reached') is False
         and ended.get('stop_reason') == 'COMMAND_EXITED' and cleanup.get('reaped') is True
         and cleanup.get('job_active_zero_observed') is True and cleanup.get('cleanup_errors') == []
         and type(cleanup.get('actual_exit_code')) is int and cleanup['actual_exit_code'] == 0,
         'TERMINAL', 'actual completed contained invocation')
    need(manifest.get('source_sha256') == OLD_SOFTWARE['acceleration/run_compute_command.py']
         and manifest.get('invocation_id') == ended.get('invocation_id')
         and type(manifest.get('command')) is list and all(type(word) is str for word in manifest['command']),
         'TERMINAL', 'same source-bound supervisor command')
    if 'process_group_live_pids' in cleanup:
        need(cleanup['process_group_live_pids'] == []
             and manifest.get('cwd') == '/mnt/c/Users/ikuto/projects/conway-99-graph'
             and manifest['command'][:5] == ['/usr/bin/env', 'UV_PROJECT_ENVIRONMENT=build/native-budget-linux-venv',
                                          '/root/.local/bin/uv', 'run', '--locked']
             and '--offline' in manifest['command'], 'TERMINAL', 'actual Linux process-group receipt; not a WindowsJob')
        return 'LINUX_PROCESS_GROUP_EMPTY_COMMON_LEGACY_FIELD_NOT_WINDOWS_JOB'
    need(manifest.get('cwd') in [str(ROOT), ROOT.as_posix()] and cleanup.get('created_suspended') is True,
         'TERMINAL', 'actual local Windows suspended Job receipt')
    return 'WINDOWS_SUSPENDED_JOB_EMPTY'


def reject(records, label, stage, call):
    try:
        call()
    except (C.AuditError, K.CensusError, G.AuditError) as error:
        need(error.stage == stage, 'CONTROL', 'exact rejection stage for ' + label)
        records.append(dict(case=label, stage=stage, outcome='REJECTED'))
        return
    raise C.AuditError('CONTROL', 'accepted deliberately corrupted ' + label)


def synthetic_source():
    refs = {name: dict(path='synthetic/' + name + '.json', sha256='0' * 64)
            for name in ['source_manifest', 'source_matrix', 'source_triples']}
    aggregate = dict(best_root_residual=10, root_neutral_minimum_mu=5344)
    manifest = dict(status='CANDIDATE_COMPLETE_PENDING_INDEPENDENT_CHECK', completed_proposals=224784,
                    population=224784, starting_proposal_id=0, parts=[None] * 45, checkpoints=[None] * 45,
                    selected_proposal_id=45369, aggregate=aggregate,
                    identity=dict(graph_only_input=True, historical_native_state_written=False,
                                  frozen_rows=copy.deepcopy(R.FROZEN), n=99, degree=7, root=11, total=224784))
    gate = dict(status=list(C.SOURCE_ROLES)[0], producer='/root/native_driver', verifier='/root/checkpoint_audit',
                method='independent_artifact_check', target_resolution='NONE', graph_only_input=True,
                historical_native_state_written=False, complete_labelled_proposals=224784, mutable_label_count=224,
                literal_one_move_population_only=True, frozen_original_literal_rows=copy.deepcopy(R.FROZEN),
                selected_proposal_id=45369, aggregate=copy.deepcopy(aggregate),
                inputs_sha256={value['path']: value['sha256'] for value in refs.values()})
    return gate, manifest, refs


def synthetic_actual(refs):
    return dict(mode='actual_independently_checked_strict_lex_selection', selected_proposal_id=45369,
                **copy.deepcopy(refs), source_complete_audit=dict(path='synthetic/source_audit.json', sha256='0' * 64,
                status=list(C.SOURCE_ROLES)[0]), source_baseline_metrics=dict(E_lambda=0, E_mu=5408, R_root=10),
                historical_native_state_written=False)


def own_graph_calibration(out):
    positives = []
    for name in ['rook9', 'prism9', 'cube12_defect']:
        obj = C.payload(S.fixture(name), 12 if name == 'cube12_defect' else 9, 2, 0)
        raw = (json.dumps(obj) + '\n').encode()
        _, _, scalar = C.decode(raw)
        if name == 'rook9':
            need(scalar['srg_valid'] is True, 'KNOWN_VALID', 'complete known-valid rook fixture')
        save(out / (name + '.json'), obj)
        positives.append(dict(name=name, scalar=scalar))
    good = C.payload(S.fixture('rook9'), 9, 2, 0)
    records = []
    for name, blob, stage in [('syntax', b'{broken', 'JSON_SYNTAX'), ('duplicate', b'{"n":9,"n":9}', 'JSON_DUPLICATE'),
                              ('NaN', b'{"n":NaN}', 'JSON_CONSTANT'), ('UTF8', b'\xff', 'JSON_SYNTAX')]:
        reject(records, name, stage, lambda blob=blob: C.decode(blob))
    mutations = [('extra', 'GRAPH_SCHEMA', lambda x: x.update(native_state={})),
                 ('old_schema', 'GRAPH_SCHEMA', lambda x: x.update(schema=G.SCHEMA))]
    for key in ['n', 'degree', 'root']:
        mutations += [('bool_' + key, 'GRAPH_DOMAIN', lambda x, key=key: x.update({key: True})),
                      ('float_' + key, 'GRAPH_DOMAIN', lambda x, key=key: x.update({key: float(x[key])}))]
    mutations += [('duplicate_point', 'TOPOLOGY_DOMAIN', lambda x: x['ordered_triples'][0].__setitem__(1, x['ordered_triples'][0][0])),
                  ('duplicate_line', 'TOPOLOGY_DOMAIN', lambda x: x['ordered_triples'].__setitem__(1, x['ordered_triples'][0][:])),
                  ('missing_line', 'TOPOLOGY_DOMAIN', lambda x: x['ordered_triples'].pop()),
                  ('reordered_root', 'FROZEN_LABELS', lambda x: x['frozen_rows'][0].reverse()),
                  ('missing_mutable', 'FROZEN_LABELS', lambda x: x['mutable_labels'].pop()),
                  ('bool_mutable', 'FROZEN_LABELS', lambda x: x['mutable_labels'].__setitem__(0, True)),
                  ('native_history', 'PROVENANCE', lambda x: x['provenance'].update(historical_native_state_written=True))]
    for key in ['E_lambda', 'E_mu', 'R_root']:
        mutations += [('wrong_' + key, 'EXACT_SCORES', lambda x, key=key: x['metrics'].__setitem__(key, x['metrics'][key] + 1)),
                      ('bool_' + key, 'ENERGY', lambda x, key=key: x['metrics'].__setitem__(key, False))]
    mutations += [('extra_score', 'ENERGY', lambda x: x['metrics'].update(other=0))]
    for name, stage, mutate in mutations:
        bad = copy.deepcopy(good)
        mutate(bad)
        reject(records, name, stage, lambda bad=bad: C.decode((json.dumps(bad) + '\n').encode()))
    reject(records, 'generic_not99', 'TARGET_SCOPE', lambda: C.decode((json.dumps(good) + '\n').encode(), actual=True))
    gate, manifest, refs = synthetic_source()
    need(C.review_source(gate, manifest, refs) == 45369, 'KNOWN_SCOPE', 'old source exact checkpoint role')
    new_gate = copy.deepcopy(gate)
    new_gate.update(status=list(C.SOURCE_ROLES)[1], verifier='/root/structural')
    need(C.review_source(new_gate, manifest, refs) == 45369, 'KNOWN_SCOPE', 'new source exact structural role')
    wrong = copy.deepcopy(new_gate)
    wrong['verifier'] = '/root/checkpoint_audit'
    reject(records, 'new_source_old_verifier', 'SOURCE_REVIEW', lambda: C.review_source(wrong, manifest, refs))
    wrong = copy.deepcopy(gate)
    wrong['verifier'] = '/root/structural'
    reject(records, 'old_source_new_verifier', 'SOURCE_REVIEW', lambda: C.review_source(wrong, manifest, refs))
    save(out / 'strict_graph_controls.json', records)
    save(out / 'synthetic_source_interfaces.json', dict(old=gate, new=new_gate, manifest=manifest, refs=refs,
         limitations='Synthetic typed metadata only; null45entries are not artifacts or coverage evidence.'))
    return dict(known_graph_positives=positives, precise_graph_and_role_negatives=len(records),
                old_source_role_positive=1, new_source_role_positive=1, actual99graph_read=False)


def read_author_graph(directory, pin):
    summary = read_json(directory / 'summary.json')
    pin((directory / 'summary.json').relative_to(ROOT).as_posix())
    need(summary['status'] == 'AUTHOR_STRICT_LEX_GRAPH_PROJECTION_CONTROLS_PENDING_INDEPENDENT_GATE'
         and summary['actual_selected_graph_read'] is False and summary['historical_native_state_written'] is False
         and summary['scientific_launched'] is False and summary['independent_approval'] is False,
         'AUTHOR_GRAPH', 'new finite source-only reader scope')
    need((summary['graph_specific_negative_count'], summary['source_review_specific_negative_count'], summary['provenance_specific_negative_count'])
         == (23, 38, 20) and summary['source_review_synthetic_positive'] == 2,
         'AUTHOR_GRAPH', 'exact frozen saved population')
    expected_graph = {'duplicate_key', 'malformed_utf8', 'extra_field', 'old_schema', 'bool_n', 'bool_degree', 'bool_root',
        'duplicate_vertex', 'duplicate_line', 'repeated_pair', 'point_bool', 'point_range', 'missing_line', 'reordered_frozen',
        'missing_mutable', 'bool_mutable', 'wrong_E_lambda', 'wrong_E_mu', 'wrong_R_root', 'energy_bool', 'extra_energy',
        'native_history', 'rook_not_target99'}
    expected_source = {'source_wrong_' + field for field in ['status', 'producer', 'verifier', 'method', 'target_resolution']}
    expected_source.update({'source_false_graph_only_input', 'source_false_literal_one_move_population_only', 'source_native_history',
        'source_frozen_reordered', 'source_aggregate_mismatch', 'source_aggregate_missing', 'source_pinmap_type', 'source_matrix_pin_missing',
        'source_triples_pin_corrupt', 'raw_incomplete', 'raw_missing_parts', 'raw_type_parts', 'raw_missing_checkpoints', 'raw_type_checkpoints',
        'raw_selected_mismatch', 'raw_identity_missing', 'raw_identity_history', 'raw_identity_frozen', 'raw_identity_bool_n',
        'old_complete_structural_role', 'future_complete_checkpoint_role'})
    for prefix, fields in [('source', ['complete_labelled_proposals', 'mutable_label_count', 'selected_proposal_id']),
                           ('raw', ['completed_proposals', 'population', 'starting_proposal_id'])]:
        expected_source.update(prefix + '_' + kind + '_' + field for kind in ['wrong', 'bool'] for field in fields)
    expected_prov = {'prov_extra_rng', 'prov_history', 'prov_unknown_mode', 'prov_pid_bool', 'prov_pid_negative', 'prov_pid_outside',
        'prov_drive_path', 'prov_audit_status', 'prov_audit_extra', 'prov_audit_hash', 'prov_lambda_nonzero', 'prov_score_bool',
        'prov_score_negative', 'prov_score_missing'}
    expected_prov.update('prov_' + kind + '_' + field for kind in ['path_escape', 'hash']
                         for field in ['source_manifest', 'source_matrix', 'source_triples'])
    for field, wanted in [('graph_specific_negatives', expected_graph), ('source_review_specific_negatives', expected_source),
                           ('provenance_specific_negatives', expected_prov)]:
        labels(summary[field], wanted)
    positives = []
    for name in ['rook9', 'prism9', 'cube12']:
        path = directory / (name + '.graph.json')
        pin(path.relative_to(ROOT).as_posix())
        obj, _, scalar = C.decode(path.read_bytes())
        need(C.same(obj['provenance'], C.synthetic_provenance()), 'AUTHOR_GRAPH', 'explicit generic fixture lineage')
        positives.append(dict(name=name, scalar=scalar))
    graph_records = []
    stages = {'PROJECTION_JSON': None, 'GRAPH_SCHEMA': 'GRAPH_SCHEMA', 'GRAPH_DOMAIN': 'GRAPH_DOMAIN',
              'DOMAIN': 'TOPOLOGY_DOMAIN', 'LINEARITY': 'TOPOLOGY_DOMAIN', 'DEGREE': 'TOPOLOGY_DOMAIN',
              'GRAPH_FROZEN': 'FROZEN_LABELS', 'GRAPH_ENERGY': 'EXACT_SCORES', 'ENERGY': 'ENERGY',
              'PROVENANCE': 'PROVENANCE', 'TARGET_SCOPE': 'TARGET_SCOPE'}
    for record in summary['graph_specific_negatives']:
        path = directory / (record['case'] + '.json')
        pin(path.relative_to(ROOT).as_posix())
        stage = stages[record['stage']]
        if stage is None:
            stage = 'JSON_DUPLICATE' if record['case'] == 'duplicate_key' else 'JSON_SYNTAX'
        need(record['outcome'] == 'REJECTED', 'AUTHOR_GRAPH', 'literal producer rejection')
        reject(graph_records, record['case'], stage, lambda path=path, stage=stage: C.decode(path.read_bytes(), actual=stage == 'TARGET_SCOPE'))
    source = read_json(directory / 'synthetic_source_review.json')
    pin((directory / 'synthetic_source_review.json').relative_to(ROOT).as_posix())
    need(source['synthetic_engineering_fixture'] is True and source['actual_selected_graph_read'] is False,
         'AUTHOR_GRAPH', 'synthetic complete-source interface scope')
    C.review_source(source['gate'], source['manifest'], source['descriptors'])
    future_path = directory / 'synthetic_future_source_review.json'
    pin(future_path.relative_to(ROOT).as_posix())
    future = read_json(future_path)
    need(future['synthetic_engineering_fixture'] is True and future['actual_selected_graph_read'] is False,
         'AUTHOR_GRAPH', 'future role interface remains synthetic')
    C.review_source(future['gate'], future['manifest'], future['descriptors'])
    source_records = []
    for record in summary['source_review_specific_negatives']:
        path = directory / (record['case'] + '.json')
        pin(path.relative_to(ROOT).as_posix())
        bad = read_json(path)
        need(bad['synthetic_engineering_fixture'] is True and record['stage'] == 'SOURCE_REVIEW'
             and record['outcome'] == 'REJECTED', 'AUTHOR_GRAPH', 'actual typed source-review control')
        reject(source_records, record['case'], 'SOURCE_REVIEW', lambda bad=bad: C.review_source(bad['gate'], bad['manifest'], bad['descriptors']))
    prov = read_json(directory / 'synthetic_actual_provenance.json')
    pin((directory / 'synthetic_actual_provenance.json').relative_to(ROOT).as_posix())
    need(prov['synthetic_engineering_fixture'] is True and prov['actual_selected_graph_read'] is False,
         'AUTHOR_GRAPH', 'typed provenance only')
    C.provenance(prov['provenance'])
    prov_records = []
    for record in summary['provenance_specific_negatives']:
        path = directory / (record['case'] + '.json')
        pin(path.relative_to(ROOT).as_posix())
        bad = read_json(path)
        need(bad['synthetic_engineering_fixture'] is True and record['outcome'] == 'REJECTED', 'AUTHOR_GRAPH', 'saved actual provenance veto')
        reject(prov_records, record['case'], record['stage'], lambda bad=bad: C.provenance(bad['provenance']))
    progress_path = directory / 'progress_controls.json'
    pin(progress_path.relative_to(ROOT).as_posix())
    progress = read_json(progress_path)
    wanted = [('root_down_mu_worse', True), ('neutral_mu_down', True), ('equal_pair', False), ('root_up_mu_down', False)]
    need([(item['name'], item['expected']) for item in progress] == wanted, 'AUTHOR_GRAPH', 'all four frozen comparisons')
    for item in progress:
        C.energy(item['selected'])
        C.energy(item['baseline'])
        actual = (item['selected']['R_root'], item['selected']['E_mu']) < (item['baseline']['R_root'], item['baseline']['E_mu'])
        need(actual is item['expected'], 'AUTHOR_GRAPH', 'literal strict lex result')
    need((len(graph_records), len(source_records), len(prov_records)) == (23, 38, 20), 'AUTHOR_GRAPH', 'complete saved negative populations')
    for path in sorted(directory.rglob('*')):
        if path.is_file():
            pin(path.relative_to(ROOT).as_posix())
    return dict(positive_graphs=positives, graph_negatives=graph_records, source_review_negatives=source_records,
                provenance_negatives=prov_records, progress_controls=progress, actual99graph_read=False)


def synthetic_input():
    _, _, refs = synthetic_source()
    prov = synthetic_actual(refs)
    obj = dict(metrics=dict(E_lambda=0, E_mu=5344, R_root=10), provenance=prov)
    path, identity = 'synthetic/graph_input.json', '0' * 64
    gate = dict(status=GRAPH_PASS, producer='/root/native_driver', verifier='/root/structural',
                method='independent_artifact_check', target_resolution='NONE', graph_only_input=True,
                historical_native_state_written=False, n=99, point_degree=7, root=11, ordered_triples=231,
                mutable_lines=224, frozen_lines=7, selected_proposal_id=45369,
                graph_input_path=path, graph_input_sha256=identity, metrics=copy.deepcopy(obj['metrics']),
                source_baseline_metrics=copy.deepcopy(prov['source_baseline_metrics']),
                frozen_original_literal_rows=copy.deepcopy(R.FROZEN),
                inputs_sha256={path: identity, PROJECTOR: NATIVE[PROJECTOR], PROJECTOR_SPEC: NATIVE[PROJECTOR_SPEC],
                               **{prov[field]['path']: prov[field]['sha256'] for field in ['source_manifest', 'source_matrix', 'source_triples', 'source_complete_audit']}})
    for field in ['source_manifest', 'source_matrix', 'source_triples', 'source_complete_audit']:
        gate[field + '_sha256'] = prov[field]['sha256']
    return path, identity, obj, gate


def own_gate_calibration(out):
    path, identity, obj, gate = synthetic_input()
    C.review_input(gate, obj, path, identity, PROJECTOR, PROJECTOR_SPEC, census_software())
    records = []
    mutations = []
    for field in ['status', 'producer', 'verifier', 'method', 'target_resolution']:
        mutations.append(('wrong_' + field, lambda x, field=field: x.update({field: 'wrong'})))
    mutations += [('old_verifier', lambda x: x.update(verifier='/root/checkpoint_audit')),
                  ('native_history', lambda x: x.update(historical_native_state_written=True)),
                  ('not_graph_only', lambda x: x.update(graph_only_input=False))]
    for field in ['n', 'point_degree', 'root', 'ordered_triples', 'mutable_lines', 'frozen_lines', 'selected_proposal_id']:
        for value, label in [(gate[field] + 1, 'wrong'), (True, 'bool'), (float(gate[field]), 'float')]:
            mutations.append((label + '_' + field, lambda x, field=field, value=value: x.update({field: value})))
    for field in ['graph_input_path', 'graph_input_sha256', 'source_manifest_sha256', 'source_matrix_sha256', 'source_triples_sha256', 'source_complete_audit_sha256']:
        mutations.append(('wrong_' + field, lambda x, field=field: x.update({field: 'wrong'})))
    mutations.append(('reordered_frozen', lambda x: x['frozen_original_literal_rows'][0].reverse()))
    for owner in ['metrics', 'source_baseline_metrics']:
        for field in ['E_lambda', 'E_mu', 'R_root']:
            mutations.append(('wrong_' + owner + '_' + field, lambda x, owner=owner, field=field: x[owner].__setitem__(field, x[owner][field] + 1)))
        mutations += [('bool_' + owner, lambda x, owner=owner: x[owner].__setitem__('R_root', False)),
                      ('float_' + owner, lambda x, owner=owner: x[owner].__setitem__('R_root', float(x[owner]['R_root'])))]
    for field in [path, PROJECTOR, PROJECTOR_SPEC, obj['provenance']['source_complete_audit']['path']]:
        mutations.append(('missing_pin_' + field, lambda x, field=field: x['inputs_sha256'].pop(field)))
    for label, mutation in mutations:
        bad = copy.deepcopy(gate)
        mutation(bad)
        reject(records, label, 'INPUT_GATE', lambda bad=bad: C.review_input(bad, obj, path, identity, PROJECTOR, PROJECTOR_SPEC, census_software()))
    software_records = []
    for status, software in [(GRAPH_CONTROLS, graph_software()), (CENSUS_CONTROLS, census_software())]:
        good = dict(status=status, producer='/root/native_driver', verifier='/root/structural',
                    method='independent_artifact_check', target_resolution='NONE', inputs_sha256=software.copy())
        C.review_controls(good, status, software)
        for field in ['status', 'producer', 'verifier', 'method', 'target_resolution']:
            bad = copy.deepcopy(good)
            bad[field] = 'wrong'
            reject(software_records, status + '_wrong_' + field, 'CONTROLS_GATE', lambda bad=bad, status=status, software=software: C.review_controls(bad, status, software))
        for field in software:
            for action in ['missing', 'changed']:
                bad = copy.deepcopy(good)
                if action == 'missing':
                    bad['inputs_sha256'].pop(field)
                else:
                    bad['inputs_sha256'][field] = '0' * 64
                reject(software_records, status + '_' + action + '_' + field, 'CONTROLS_GATE',
                       lambda bad=bad, status=status, software=software: C.review_controls(bad, status, software))
    ended = dict(command_exit_code=0, error=None, deadline_reached=False, stop_reason='COMMAND_EXITED', invocation_id='synthetic_only',
                 cleanup=dict(reaped=True, job_active_zero_observed=True, actual_exit_code=0, cleanup_errors=[], process_group_live_pids=[]))
    manifest = dict(invocation_id='synthetic_only', source_sha256=OLD_SOFTWARE['acceleration/run_compute_command.py'],
                    cwd='/mnt/c/Users/ikuto/projects/conway-99-graph', command=['/usr/bin/env', 'UV_PROJECT_ENVIRONMENT=build/native-budget-linux-venv',
                    '/root/.local/bin/uv', 'run', '--locked', '--offline', 'python', 'synthetic'])
    terminal(ended, manifest)
    terminal_records = []
    for field, value in [('command_exit_code', 1), ('command_exit_code', True), ('error', 'wrong'), ('deadline_reached', True), ('stop_reason', 'TIMEOUT')]:
        bad = copy.deepcopy(ended)
        bad[field] = value
        reject(terminal_records, field + '_' + str(value), 'TERMINAL', lambda bad=bad: terminal(bad, manifest))
    for field, value in [('reaped', False), ('job_active_zero_observed', False), ('cleanup_errors', ['wrong']),
                         ('process_group_live_pids', [1]), ('actual_exit_code', 1), ('actual_exit_code', True)]:
        bad = copy.deepcopy(ended)
        bad['cleanup'][field] = value
        reject(terminal_records, field, 'TERMINAL', lambda bad=bad: terminal(bad, manifest))
    for field, value in [('cwd', 'C:/outside'), ('source_sha256', '0' * 64), ('invocation_id', 'different')]:
        bad = copy.deepcopy(manifest)
        bad[field] = value
        reject(terminal_records, field, 'TERMINAL', lambda bad=bad: terminal(ended, bad))
    linux_observer = dict(schema='ROOT_FOCUSED_PILOT_FRESH_LINUX_ADMISSION_OBSERVATION_V1',
                          scientific_UID1000_observed=dict(euid=1000, egid=1000, process_group=123))
    admitted = dict(schema='ROOT_FOCUSED_STRICT_LEX_V2_AUTHOR_CONTROLS_ADMISSION_V1', actual_default_UID=1000,
                    default_user_probe=dict(command=['wsl.exe', '-d', 'Ubuntu-24.04', '--', '/usr/bin/id', '-u'],
                    stdout='1000', exit_code=0, timestamp='synthetic metadata, not an actual wallclock observation',
                    raw_stdout=dict(path='synthetic/default_uid.stdout', sha256='0' * 64)),
                    all_pins_match=True, source_pins=census_software(),
                    linux_observation=dict(path='synthetic/linux_observation.json', sha256='0' * 64, age_seconds=1))
    def synthetic_read(name, wanted, observer=linux_observer):
        return 1000 if name == 'synthetic/default_uid.stdout' else observer
    verify_admission(admitted, census_software(), synthetic_read)
    admission_records = []
    changes = [('bool_uid', lambda x: x.update(actual_default_UID=True)), ('root_uid', lambda x: x.update(actual_default_UID=0)),
               ('wrong_admission_schema', lambda x: x.update(schema='old')), ('probe_error', lambda x: x['default_user_probe'].update(exit_code=1)),
               ('probe_bool_exit', lambda x: x['default_user_probe'].update(exit_code=False)), ('probe_stdout', lambda x: x['default_user_probe'].update(stdout='0')),
               ('probe_wrong_command', lambda x: x['default_user_probe']['command'].__setitem__(-1, 'different')),
               ('probe_command_tail', lambda x: x['default_user_probe']['command'].append('unexpected')),
               ('pins_false', lambda x: x.update(all_pins_match=False)), ('missing_caller_pin', lambda x: x['source_pins'].pop(CALLER)),
               ('observation_old', lambda x: x['linux_observation'].update(age_seconds=1801)),
               ('observation_bool_age', lambda x: x['linux_observation'].update(age_seconds=True))]
    for name, mutation in changes:
        bad = copy.deepcopy(admitted)
        mutation(bad)
        reject(admission_records, name, 'ADMISSION', lambda bad=bad: verify_admission(bad, census_software(), synthetic_read))
    wrong_observer = copy.deepcopy(linux_observer)
    wrong_observer['scientific_UID1000_observed']['euid'] = 0
    reject(admission_records, 'roothelper_is_not_scientific_uid', 'ADMISSION',
           lambda: verify_admission(admitted, census_software(), lambda name, wanted: synthetic_read(name, wanted, wrong_observer)))
    labels([dict(case='a'), dict(case='b')], {'a', 'b'})
    label_records = []
    for name, malformed in [('duplicate', [dict(case='a'), dict(case='a')]), ('omitted', [dict(case='a')]),
                             ('unexpected', [dict(case='a'), dict(case='c')]), ('typed', [dict(case=True), dict(case='b')])]:
        reject(label_records, name, 'CONTROL_POPULATION', lambda malformed=malformed: labels(malformed, {'a', 'b'}))
    save(out / 'own_gate_controls.json', dict(synthetic_input_positive=gate, precise_input_negatives=records,
         precise_software_gate_negatives=software_records, synthetic_linux_terminal_positive=ended,
         synthetic_linux_manifest_positive=manifest, precise_terminal_negatives=terminal_records,
         synthetic_admission_positive=admitted, synthetic_linux_observer_positive=linux_observer,
         precise_admission_negatives=admission_records, exact_control_population_negatives=label_records,
         limitations='Synthetic algebraic/metadata fixtures; no actual99 input or producer raw outputs checked.'))
    return dict(input_gate_positives=1, precise_input_gate_negatives=len(records), software_gate_positives=2,
                precise_software_gate_negatives=len(software_records), linux_terminal_metadata_positives=1,
                precise_terminal_negatives=len(terminal_records), admission_metadata_positives=1,
                precise_admission_negatives=len(admission_records), precise_control_population_negatives=len(label_records))


def labels(records, expected):
    need(type(records) is list and all(type(record) is dict and type(record.get('case')) is str for record in records)
         and len(records) == len(expected) and {record['case'] for record in records} == expected,
         'CONTROL_POPULATION', 'exact distinct declared corruption labels; retries and duplicates cannot replace cases')


# The following complete literal-manifest and synthetic-stream functions are
# preserved from the independently authored e01f selected-neighbor checker.
# They use explicit new base/graph_sha parameters; no old globals are replaced.
def check_manifest(path,base,pin,deadline,audit_out,graph_sha):
 # Literal path adapted from independent R: only new checking-progress identity
 # is graph-only. Never overwrite R's old original-state/MATRIX globals.
 pin(path.relative_to(ROOT).as_posix());manifest=read_json(path);universe=K.labelled_universe(base);total=len(universe);completed=manifest['completed_proposals']
 need(manifest['schema']=='FROZEN_ROOT_TWO_LINE_CENSUS_MANIFEST_V1'and type(completed)is int and 0<=completed<=total
  and type(manifest['population'])is int and manifest['population']==total,'MANIFEST','exact labelled population')
 need(R.literal_equal(manifest['baseline'],dict(lambda_energy=base['lambda_energy'],mu_energy=base['mu_energy'],root=base['root'],root_residual=base['root_residual'],
  frozen_rows=base['frozen'],mutable_labels=base['mutable'])),'MANIFEST','complete exact new graph baseline')
 need(all(type(manifest[k])is int for k in['starting_proposal_id','proposals_evaluated_this_invocation'])and 0<=manifest['starting_proposal_id']<=completed
  and manifest['proposals_evaluated_this_invocation']==completed-manifest['starting_proposal_id'],'MANIFEST','literal invocation prefix counts')
 identity=manifest['identity'];need(R.literal_equal({k:identity[k]for k in['n','degree','root','total','frozen_rows','mutable_labels']},
  dict(n=base['n'],degree=base['degree'],root=base['root'],total=total,frozen_rows=base['frozen'],mutable_labels=base['mutable'])),'MANIFEST','exact raw domain')
 for name,wanted in identity['software'].items():pin(name,wanted)
 need(manifest['independent_approval']is False and manifest['target_resolution']is False,'MANIFEST','producer pending scope')
 expected=[];end=0;bar=tqdm(total=completed,desc='Independent selected-neighbor literal rows',unit='record',mininterval=1)
 for part in manifest['parts']:
  need(deadline.status()['remaining_seconds']>20,'DEADLINE','checking serialization reserve');need(part['start']==end,'PART_SEQUENCE','gap-free manifest coverage')
  raw=R.read_part(part,pin)
  for record in raw:
   wanted=R.expected_record(base,record['proposal_id'],universe);R.check_record(record,wanted);expected.append(wanted);bar.update(1)
  end=part['end'];save(audit_out/('checked_prefix_'+str(end)+'.json'),dict(status='UNKNOWN_PREFIX_CHECKED_NO_COMPLETE_CENSUS_CLAIM',
   checked_proposal_records=end,raw_part_sha256=part['raw_sha256'],gzip_part_sha256=part['gzip_sha256'],input_graph_json_sha256=graph_sha,
   input_matrix_sha256=hashlib.sha256(K.matrix_bytes(base['bits'])).hexdigest(),graph_only_input=True,historical_native_state_written=False,deadline=deadline.status()))
 bar.close();need(end==completed and len(expected)==completed,'PART_SEQUENCE','complete raw prefix population');want=R.aggregate(expected)
 need(R.literal_equal(manifest['aggregate'],want),'AGGREGATE','all labels counts minima ties and literal graph identities')
 need(manifest['status']==('CANDIDATE_COMPLETE_PENDING_INDEPENDENT_CHECK'if completed==total else'UNKNOWN_PREFIX_ONLY'),'MANIFEST','complete versus prefix status')
 for descriptor in manifest['checkpoints']:
  pin(descriptor['path'],descriptor['sha256']);cp=read_json(ROOT/descriptor['path']);upto=cp['next_proposal_id']
  need(type(upto)is int and 0<=upto<=completed and cp['schema']=='FROZEN_ROOT_TWO_LINE_CENSUS_CHECKPOINT_V1'
   and R.literal_equal(cp['identity'],identity),'CHECKPOINT','exact source/input/prefix identity')
  matching=[part for part in manifest['parts']if part['end']<=upto]
  need(R.literal_equal(cp['parts'],matching)and(matching[-1]['end']if matching else 0)==upto
   and R.literal_equal(cp['aggregate'],R.aggregate(expected[:upto])),'CHECKPOINT','all complete prefix parts and aggregate coverage')
 directory=path.parent
 for filename,ids in[('best_root_ties.json',want['best_root_proposal_ids']),('minimum_mu_ties.json',want['minimum_mu_proposal_ids']),
  ('root_neutral_minimum_mu_ties.json',want['root_neutral_minimum_mu_proposal_ids'])]:
  member=(directory/filename).relative_to(ROOT).as_posix();pin(member);saved=read_json(ROOT/member)
  need(R.literal_equal(saved['records'],[expected[pid]for pid in ids]),'TIES','complete literal tie population')
 selected=min((expected[pid]for pid in want['best_root_proposal_ids']),key=lambda record:(record['new_mu'],record['proposal_id']),default=None)
 need(R.literal_equal(manifest['selected_proposal_id'],None if selected is None else selected['proposal_id']),'SELECTED','lex R mu ID selection')
 selected_scalar=None
 if selected is not None:
  candidate=K.evaluate(base,universe[selected['proposal_id']]);rows=K.reconstruct_triples(base,candidate);matrix=directory/'best_root_neighbor.adj';pin(matrix.relative_to(ROOT).as_posix())
  need(matrix.read_bytes()==K.matrix_bytes(candidate['candidate_bits']),'SELECTED','entire new selected raw adjacency')
  triple=directory/'best_root_neighbor_triples.json';pin(triple.relative_to(ROOT).as_posix());saved=read_json(triple)
  need(R.literal_equal(saved,dict(n=base['n'],degree=base['degree'],root=base['root'],frozen_rows=base['frozen'],mutable_labels=base['mutable'],triples=rows,
   proposal_id=selected['proposal_id'])),'SELECTED','entire ordered selected triples and original frozen rows')
  selected_scalar=S.scalar_matrix(matrix.read_bytes(),base['n'],base['degree'],base['root'])
  need((selected_scalar['lambda_energy'],selected_scalar['mu_energy'],selected_scalar['root_residual'])
   ==(selected['new_lambda'],selected['new_mu'],selected['new_root_residual']),'SELECTED','separate full scalar selected components')
 return dict(completed=completed,population=total,aggregate=want,selected_proposal_id=manifest['selected_proposal_id'],selected_scalar=selected_scalar),expected

def caller_path_calibration(out,record_out,pin,deadline):
 rows=[[3*r+c for c in range(3)]for r in range(3)]+[[3*r+c for r in range(3)]for c in range(3)];base=K.from_triples(rows,9,2,0)
 positive_out=out/'caller_positive';positive_out.mkdir();audit,records=check_manifest(record_out/'synthetic_manifest'/'manifest.json',base,pin,deadline,positive_out,'0'*64)
 need(audit['completed']==54 and audit['selected_scalar']['srg_valid']is True,'CALLER_CALIBRATION','independent complete rook synthetic stream and selected matrix')
 rejected=[]
 for name,stage in[('float_population','MANIFEST'),('bool_baseline_root','MANIFEST'),('dropped_part','PART_SEQUENCE'),('wrong_aggregate','AGGREGATE'),
  ('float_selected_id','SELECTED'),('checkpoint_aggregate','CHECKPOINT'),('missing_tie','TIES'),('selected_matrix','SELECTED')]:
  checked_out=out/('caller_'+name);checked_out.mkdir()
  reject(rejected,name,stage,lambda name=name,checked_out=checked_out:check_manifest(record_out/name/'manifest.json',base,pin,deadline,checked_out,'0'*64))
 save(out/'caller_path_controls.json',dict(positive_audit=audit,precise_negatives=rejected,input_history_scope='Synthetic graph-only path, no native history or actual selected99input'))
 return dict(positive_complete_caller_streams=1,positive_caller_records=54,precise_caller_path_negatives=8)


def verify_admission(record, required_software, read):
    need(type(record) is dict and record.get('schema') == 'ROOT_FOCUSED_STRICT_LEX_V2_AUTHOR_CONTROLS_ADMISSION_V1'
         and type(record.get('actual_default_UID')) is int and record['actual_default_UID'] == 1000,
         'ADMISSION', 'actual defaultUID1000 declaration')
    probe = record.get('default_user_probe')
    need(type(probe) is dict and type(probe.get('exit_code')) is int and probe['exit_code'] == 0
         and probe.get('stdout') == '1000' and type(probe.get('timestamp')) is str
         and type(probe.get('command')) is list and len(probe['command']) == 6
         and type(probe['command'][0]) is str and probe['command'][0].replace('\\', '/').split('/')[-1] == 'wsl.exe'
         and probe['command'][1:] == ['-d', 'Ubuntu-24.04', '--', '/usr/bin/id', '-u'],
         'ADMISSION', 'literal saved default-user probe')
    # Exact planned probe has six words: wsl.exe,-d,Ubuntu-24.04,--,/usr/bin/id,-u.
    need(type(probe.get('raw_stdout')) is dict, 'ADMISSION', 'mandatory preserved probe bytes')
    C.descriptor(probe['raw_stdout'])
    probe_value = read(probe['raw_stdout']['path'], probe['raw_stdout']['sha256'])
    need(type(probe_value) is int and probe_value == 1000, 'ADMISSION', 'hashed rawUID output agrees with declaration')
    need(record.get('all_pins_match') is True and type(record.get('source_pins')) is dict
         and all(record['source_pins'].get(name) == value for name, value in required_software.items()),
         'ADMISSION', 'fresh exact changed software census/projection pins')
    linux = record.get('linux_observation')
    need(type(linux) is dict and type(linux.get('age_seconds')) in [int, float] and 0 <= linux['age_seconds'] <= 1800,
         'ADMISSION', 'bounded fresh finite Linux observation')
    observer = read(linux['path'], linux['sha256'])
    need(observer.get('schema') == 'ROOT_FOCUSED_PILOT_FRESH_LINUX_ADMISSION_OBSERVATION_V1'
         and type(observer.get('scientific_UID1000_observed')) is dict
         and observer['scientific_UID1000_observed'].get('euid') == 1000
         and type(observer['scientific_UID1000_observed'].get('euid')) is int,
         'ADMISSION', 'source-bound separate UID1000 observation, not root helper euid')
    return dict(actual_default_uid=1000, default_probe_timestamp=probe['timestamp'], linux_observation_path=linux['path'],
                linux_observation_sha256=linux['sha256'], physical_process_scope='Finite saved OS observations only, not global absence or a hard-real-time guarantee')


def author_census_controls(out, pin, deadline, args):
    summary = read_json(ROOT / args.producer_summary)
    need(summary['status'] == 'AUTHOR_STRICT_LEX_TWO_LINE_CONTROLS_PENDING_INDEPENDENT_GATE'
         and summary['producer'] == '/root/native_driver' and summary['independent_approval'] is False
         and summary['actual99graph_read'] is False and summary['scientific_launched'] is False
         and summary['historical_native_state_written'] is False and C.same(summary['software'], census_software()),
         'AUTHOR_CENSUS', 'changed caller finite-only exact software scope')
    fields = ['unique_complete_proposal_records_checked', 'recorded_proposal_evaluation_calls', 'additional_known_overlap_evaluation_calls',
              'kernel_negative_controls', 'whole_split_equal', 'reader_graph_negatives', 'source_review_negatives', 'provenance_negatives',
              'input_gate_specific_negative_count', 'controls_gate_specific_negative_count']
    need(C.same([summary[field] for field in fields], [243, 486, 1, 41, True, 23, 38, 20, 39, 18]),
         'AUTHOR_CENSUS', 'exact stage-specific finite population')
    expected_input = {'gate_wrong_' + field for field in ['status', 'producer', 'verifier', 'method', 'target_resolution',
        'graph_input_path', 'graph_input_sha256', 'source_manifest_sha256', 'source_matrix_sha256', 'source_triples_sha256', 'source_complete_audit_sha256']}
    expected_input.update({'gate_native_history', 'gate_not_graph_only', 'gate_frozen_reordered', 'gate_bool_metrics',
        'gate_bool_source_baseline_metrics', 'gate_graph_pin_missing', 'gate_projector_pin_missing', 'gate_matrix_pin_corrupt'})
    expected_input.update('gate_' + kind + '_' + field for kind in ['wrong', 'bool']
                          for field in ['n', 'point_degree', 'root', 'ordered_triples', 'mutable_lines', 'frozen_lines', 'selected_proposal_id'])
    expected_input.update('gate_wrong_' + owner + '_' + field for owner in ['metrics', 'source_baseline_metrics']
                          for field in ['E_lambda', 'E_mu', 'R_root'])
    expected_control = {'control_wrong_' + field for field in ['status', 'producer', 'verifier', 'method', 'target_resolution']}
    expected_control.update('control_missing_software_' + str(index) for index in range(12))
    expected_control.add('control_self_source_corrupt')
    labels(summary['input_gate_specific_negatives'], expected_input)
    labels(summary['controls_gate_specific_negatives'], expected_control)
    directory = (ROOT / args.producer_summary).parent
    kernel = directory / 'unchanged_kernel/summary.json'
    pin(kernel.relative_to(ROOT).as_posix(), summary['kernel_summary_sha256'])
    kernel_out = out / 'actual_kernel'
    kernel_out.mkdir()
    kernel_audit = R.controls(kernel_out, pin, deadline, SimpleNamespace(producer_summary=kernel.relative_to(ROOT).as_posix(),
                producer_summary_sha256=summary['kernel_summary_sha256'], supervisor=args.supervisor, supervisor_sha256=args.supervisor_sha256))
    reader = directory / 'graph_reader'
    pin((reader / 'summary.json').relative_to(ROOT).as_posix(), summary['graph_reader_summary_sha256'])
    reader_audit = read_author_graph(reader, pin)
    fixture = directory / 'synthetic_input_gate_fixture.json'
    pin(fixture.relative_to(ROOT).as_posix())
    raw = read_json(fixture)
    need(raw['synthetic_engineering_fixture'] is True and raw['actual99graph_decoded'] is False,
         'AUTHOR_CENSUS', 'metadata-only input fixture')
    path, identity = 'synthetic/graph_input.json', '0' * 64
    obj = raw['object_metadata']
    C.review_input(raw['gate'], obj, path, identity, PROJECTOR, PROJECTOR_SPEC, census_software())
    input_records = []
    for record in summary['input_gate_specific_negatives']:
        member = directory / (record['case'] + '.json')
        pin(member.relative_to(ROOT).as_posix())
        bad = read_json(member)
        need(record['stage'] == 'INPUT_GATE' and record['outcome'] == 'REJECTED' and bad['synthetic_engineering_fixture'] is True,
             'AUTHOR_CENSUS', 'actual saved input-stage negative')
        reject(input_records, record['case'], 'INPUT_GATE', lambda bad=bad: C.review_input(bad['gate'], obj, path, identity, PROJECTOR, PROJECTOR_SPEC, census_software()))
    fixture = directory / 'synthetic_controls_gate_fixture.json'
    pin(fixture.relative_to(ROOT).as_posix())
    raw = read_json(fixture)
    need(raw['synthetic_engineering_fixture'] is True, 'AUTHOR_CENSUS', 'metadata-only caller control fixture')
    C.review_controls(raw['gate'], CENSUS_CONTROLS, census_software())
    control_records = []
    for record in summary['controls_gate_specific_negatives']:
        member = directory / (record['case'] + '.json')
        pin(member.relative_to(ROOT).as_posix())
        bad = read_json(member)
        need(record['stage'] == 'CONTROLS_GATE' and record['outcome'] == 'REJECTED' and bad['synthetic_engineering_fixture'] is True,
             'AUTHOR_CENSUS', 'actual saved caller-stage negative')
        reject(control_records, record['case'], 'CONTROLS_GATE', lambda bad=bad: C.review_controls(bad['gate'], CENSUS_CONTROLS, census_software()))
    need(len(input_records) == 39 and len(control_records) == 18 and kernel_audit['raw_record_observations'] == 597,
         'AUTHOR_CENSUS', 'complete saved typed/record populations')
    for member in sorted(directory.rglob('*')):
        if member.is_file():
            pin(member.relative_to(ROOT).as_posix())
    save(out / 'author_caller_interface_audit.json', dict(input=input_records, caller=control_records))
    save(out / 'author_graph_reader_audit.json', reader_audit)
    return dict(kernel_audit=kernel_audit, graph_reader_audit_sha256=sha(out / 'author_graph_reader_audit.json'),
                saved_input_gate_negatives=39, saved_caller_gate_negatives=18, actual99graph_read=False, scientific_census_checked=False)


def projection_full(out, pin, closure, read, args):
    summary = read(args.producer_summary, args.producer_summary_sha256)
    need(summary['status'] == 'CANDIDATE_STRICT_LEX_GRAPH_INPUT_V1_PENDING_INDEPENDENT_FULL_CHECK'
         and summary['producer'] == '/root/native_driver' and summary['independent_approval'] is False
         and summary['scientific_launched'] is False and summary['historical_native_state_written'] is False
         and summary['target_resolution'] == 'NONE', 'PROJECTED', 'actual lossless graph-only candidate scope')
    closure(summary)
    member = summary['graph_input']
    C.descriptor({field: member[field] for field in ['path', 'sha256']})
    pin(member['path'], member['sha256'])
    graph = (ROOT / member['path']).read_bytes()
    need(type(member.get('bytes')) is int and member['bytes'] == len(graph), 'PROJECTED', 'entire raw graph bytes')
    obj, base, scalar = C.decode(graph, actual=True)
    prov = obj['provenance']
    for field in ['source_manifest', 'source_matrix', 'source_triples', 'source_complete_audit']:
        pin(prov[field]['path'], prov[field]['sha256'])
    gate = read_json(ROOT / prov['source_complete_audit']['path'])
    manifest_path = ROOT / prov['source_manifest']['path']
    manifest = read_json(manifest_path)
    refs = {field: prov[field] for field in ['source_manifest', 'source_matrix', 'source_triples']}
    selected = C.review_source(gate, manifest, refs)
    need(gate['status'] == prov['source_complete_audit']['status'], 'PROJECTED', 'actual named source scope')
    closure(gate)
    R.full_checkpoint_population(manifest, manifest_path)
    baseline = dict(E_lambda=manifest['baseline']['lambda_energy'], E_mu=manifest['baseline']['mu_energy'], R_root=manifest['baseline']['root_residual'])
    C.energy(baseline)
    need(C.same(baseline, prov['source_baseline_metrics']), 'PROJECTED', 'source-derived full baseline components')
    selected_rows = read_json(ROOT / prov['source_triples']['path'])
    need(C.same(selected_rows, dict(n=99, degree=7, root=11, frozen_rows=base['frozen'], mutable_labels=base['mutable'],
                                  triples=base['triples'], proposal_id=selected)), 'PROJECTED', 'every ordered selected triangle/label')
    need((ROOT / prov['source_matrix']['path']).read_bytes() == K.matrix_bytes(base['bits']), 'PROJECTED', 'literal selected matrix equality')
    need(C.same(summary['metrics'], obj['metrics']) and C.same(summary['source_baseline_metrics'], baseline)
         and type(summary['selected_proposal_id']) is int and summary['selected_proposal_id'] == selected,
         'PROJECTED', 'raw summary agrees completely with graph and source')
    control = read(args.controls_gate, args.controls_gate_sha256)
    C.review_controls(control, GRAPH_CONTROLS, graph_software())
    closure(control)
    save(out / 'projection_audit.json', dict(source_gate=prov['source_complete_audit'], raw_graph=member,
         exact_selected_metrics=obj['metrics'], source_baseline_metrics=baseline, independent_full_scalar=scalar,
         ordered_rows_checked=231, literal_original_frozen_rows=R.FROZEN,
         scope='Source census complete record checking reused only as explicitly hash-bound prior dependency; this stage independently rechecks exact graph derivative and source identities.'))
    result = dict(graph_input_path=member['path'], graph_input_sha256=member['sha256'], n=99, point_degree=7, root=11,
                  ordered_triples=231, mutable_lines=224, frozen_lines=7, selected_proposal_id=selected,
                  metrics=obj['metrics'], source_baseline_metrics=baseline, frozen_original_literal_rows=R.FROZEN,
                  graph_only_input=True, historical_native_state_written=False, actual99graph_read=True,
                  projection_audit_sha256=sha(out / 'projection_audit.json'), target_graph_valid=scalar['srg_valid'])
    for field in ['source_manifest', 'source_matrix', 'source_triples', 'source_complete_audit']:
        result[field + '_sha256'] = prov[field]['sha256']
    if scalar['srg_valid']:
        (out / 'target_candidate.adj').write_bytes(K.matrix_bytes(base['bits']))
        result['target_candidate_path'] = (out / 'target_candidate.adj').relative_to(ROOT).as_posix()
        result['target_candidate_sha256'] = sha(out / 'target_candidate.adj')
    return result


def census_full(out, pin, closure, read, deadline, args):
    graph_path = args.graph_input
    pin(graph_path, args.graph_input_sha256)
    obj, base, input_scalar = C.decode((ROOT / graph_path).read_bytes(), actual=True)
    input_gate = read(args.input_gate, args.input_gate_sha256)
    C.review_input(input_gate, obj, graph_path, args.graph_input_sha256, PROJECTOR, PROJECTOR_SPEC, census_software())
    closure(input_gate)
    control = read(args.controls_gate, args.controls_gate_sha256)
    C.review_controls(control, CENSUS_CONTROLS, census_software())
    closure(control)
    manifest_path = ROOT / args.manifest
    manifest = read(args.manifest, args.manifest_sha256)
    R.full_checkpoint_population(manifest, manifest_path)
    identity = manifest['identity']
    need(identity.get('graph_only_input') is True and identity.get('historical_native_state_written') is False
         and identity.get('graph_input_schema') == C.SCHEMA and C.same(identity.get('input_provenance'), obj['provenance'])
         and C.same(identity.get('frozen_rows'), R.FROZEN) and C.same(identity.get('mutable_labels'), base['mutable'])
         and C.same([identity.get(key) for key in ['n', 'degree', 'root', 'total']], [99, 7, 11, 224784]),
         'INPUT', 'explicit generic graph-only full invocation identity')
    need(C.same(identity.get('software'), census_software()), 'INPUT', 'all12exact changed software identities')
    step = identity.get('bounded_experiment_declared_step')
    need(type(step) is int and 1 <= step <= 5 and type(identity.get('bounded_experiment_cap')) is int
         and identity['bounded_experiment_cap'] == 5, 'INPUT', 'declared position only; not invented earlier path coverage')
    for field in ['graph_input', 'input_gate', 'controls_gate']:
        need(identity['inputs_sha256'].get(getattr(args, field)) == getattr(args, field + '_sha256'),
             'INPUT', 'every actual input and separate checking gate identity')
    closure(identity)
    audit, records = check_manifest(manifest_path, base, pin, deadline, out, args.graph_input_sha256)
    need(audit['completed'] == audit['population'] == 224784, 'COVERAGE', 'entire one-graph labelled universe')
    universe = K.labelled_universe(base)
    matrices, zeros = [], []
    for pid in tqdm(audit['aggregate']['best_root_proposal_ids'], desc='Independent minimum-R literal matrices', unit='matrix', mininterval=1):
        need(deadline.status()['remaining_seconds'] > 20, 'DEADLINE', 'preserve complete checking evidence')
        candidate = K.evaluate(base, universe[pid])
        raw = K.matrix_bytes(candidate['candidate_bits'])
        scalar = S.scalar_matrix(raw, 99, 7, 11)
        record = records[pid]
        need((scalar['lambda_energy'], scalar['mu_energy'], scalar['root_residual'])
             == (record['new_lambda'], record['new_mu'], record['new_root_residual']), 'TIES', 'all minimum-R full scalar checks')
        matrices.append(dict(proposal_id=pid, matrix_sha256=hashlib.sha256(raw).hexdigest(), scalar=scalar))
        if scalar['srg_valid']:
            member = out / ('target_candidate_' + str(pid) + '.adj')
            member.write_bytes(raw)
            save(out / ('target_candidate_' + str(pid) + '_triples.json'), K.reconstruct_triples(base, candidate))
            zeros.append(dict(proposal_id=pid, path=member.relative_to(ROOT).as_posix(), sha256=sha(member)))
            print('FULL99_TARGET_MATRIX_CANDIDATE_PENDING_ROOT_REVIEW ' + str(pid), flush=True)
    receipt_path = manifest_path.parent / 'run_receipt.json'
    pin(receipt_path.relative_to(ROOT).as_posix())
    receipt = read_json(receipt_path)
    need(receipt['manifest_sha256'] == args.manifest_sha256 and receipt['producer'] == '/root/native_driver'
         and receipt['independent_approval'] is False and receipt['target_resolution'] == 'NONE'
         and receipt['historical_native_state_written'] is False
         and receipt['independently_approved_input_gate'] == args.input_gate_sha256
         and receipt['new_wrapper_controls_gate'] == args.controls_gate_sha256
         and type(receipt['declared_experiment_step']) is int and receipt['declared_experiment_step'] == step,
         'RECEIPT', 'exact actual invocation and declared position without native history')
    save(out / 'census_audit.json', audit)
    save(out / 'minimum_root_tie_scalar_audits.json', matrices)
    return dict(complete_labelled_proposals=224784, scope_graph_input_path=graph_path,
                scope_graph_input_sha256=args.graph_input_sha256,
                scope_input_matrix_sha256=hashlib.sha256(K.matrix_bytes(base['bits'])).hexdigest(),
                graph_only_input=True, historical_native_state_written=False, input_scalar=input_scalar,
                frozen_original_literal_rows=R.FROZEN, mutable_label_count=224, aggregate=audit['aggregate'],
                selected_proposal_id=audit['selected_proposal_id'], minimum_root_tie_scalar_matrices=len(matrices),
                target_candidate_objects=zeros, literal_one_move_population_only=True,
                declared_experiment_step=step, declared_step_not_execution_history=True,
                census_audit_sha256=sha(out / 'census_audit.json'),
                minimum_root_tie_scalar_audits_sha256=sha(out / 'minimum_root_tie_scalar_audits.json'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['calibration', 'graph-controls', 'census-controls', 'projection', 'census'])
    parser.add_argument('--seconds', type=float, required=True)
    parser.add_argument('--out', required=True)
    for field in ['calibration', 'producer_summary', 'supervisor', 'execution_admission', 'controls_gate', 'manifest', 'graph_input', 'input_gate']:
        parser.add_argument('--' + field.replace('_', '-'))
        parser.add_argument('--' + field.replace('_', '-') + '-sha256')
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='Independent strict-lex graph-only schema/controls/artifacts and exact labelled census; no producer imports or native calls;20s output reserve')
    out = (ROOT / args.out).resolve()
    need(out.is_relative_to(ROOT) and not out.exists(), 'PATH', 'fresh bounded independent output')
    out.mkdir(parents=True)
    pins = {}
    protected = {name: sha(ROOT / name) for name in ['CLAIMS.yaml', '.git/index']}

    def pin(name, wanted=None):
        need(deadline.status()['remaining_seconds'] > 20, 'DEADLINE', 'checking serialization reserve')
        path = (ROOT / name).resolve()
        need(path.is_relative_to(ROOT) and path.is_file() and name not in ['CLAIMS.yaml', '.git/index'], 'PATH', 'workspace public immutable input')
        relative = path.relative_to(ROOT).as_posix()
        need(relative not in ['CLAIMS.yaml', '.git/index'], 'PATH', 'protected observation is never an input artifact')
        found = sha(path)
        need(wanted is None or found == wanted, 'IDENTITY', 'exact input ' + relative)
        need(relative not in pins or pins[relative] == found, 'IDENTITY', 'stable repeated input')
        pins[relative] = found

    def read(name, wanted=None):
        pin(name, wanted)
        return read_json(ROOT / name)

    def closure(record):
        need(type(record.get('inputs_sha256')) is dict, 'CLOSURE', 'explicit immutable input map')
        for name, identity in record['inputs_sha256'].items():
            C.descriptor(dict(path=name, sha256=identity))
            pin(name, identity)

    try:
        for name, identity in {**SHARED, **census_software()}.items():
            pin(name, identity)
        for name in [SOURCE, SPEC, CORE, 'pyproject.toml', 'uv.lock']:
            pin(name)
        kernel_gate = read(R.KERNEL_CAL, R.KERNEL_CAL_SHA)
        need(kernel_gate['status'] == 'INDEPENDENT_FROZEN_ROOT_TWO_LINE_KERNEL_V1_CALIBRATION_PASS', 'KERNEL', 'unchanged independent primitive calibration')
        closure(kernel_gate)
        records_out = out / 'own_records'
        records_out.mkdir()
        records_cal = R.calibration(records_out, pin, deadline)
        stream_cal = caller_path_calibration(out, records_out, pin, deadline)
        graphs_out = out / 'own_graphs'
        graphs_out.mkdir()
        graph_cal = own_graph_calibration(graphs_out)
        gate_cal = own_gate_calibration(out)
        result = dict(status=CAL, record_calibration=records_cal, stream_calibration=stream_cal,
                      graph_calibration=graph_cal, gate_calibration=gate_cal, producer_outputs_checked=False,
                      actual99graph_read=False, scientific_census_checked=False)
        if args.mode != 'calibration':
            for field in ['calibration', 'supervisor']:
                need(getattr(args, field) and getattr(args, field + '_sha256'), 'ACTUAL', 'explicit ' + field + ' identity')
            calibration = read(args.calibration, args.calibration_sha256)
            need(calibration['status'] == CAL and calibration['producer_outputs_checked'] is False
                 and calibration['inputs_sha256'].get(SOURCE) == pins[SOURCE]
                 and calibration['inputs_sha256'].get(SPEC) == pins[SPEC]
                 and calibration['inputs_sha256'].get(CORE) == pins[CORE], 'CALIBRATION', 'same complete changed checker path')
            closure(calibration)
            ended = read(args.supervisor, args.supervisor_sha256)
            supervisor_manifest = (ROOT / args.supervisor).parent / 'manifest.json'
            pin(supervisor_manifest.relative_to(ROOT).as_posix())
            observed_profile = terminal(ended, read_json(supervisor_manifest))
            if args.mode in ['graph-controls', 'census-controls']:
                for field in ['producer_summary', 'execution_admission']:
                    need(getattr(args, field) and getattr(args, field + '_sha256'), 'ACTUAL', 'explicit ' + field + ' identity')
                author = read(args.producer_summary, args.producer_summary_sha256)
                closure(author)
                required = graph_software() if args.mode == 'graph-controls' else census_software()
                admission = read(args.execution_admission, args.execution_admission_sha256)
                admission_audit = verify_admission(admission, required, read)
                if args.mode == 'graph-controls':
                    actual = read_author_graph((ROOT / args.producer_summary).parent, pin)
                    save(out / 'author_graph_audit.json', actual)
                    result = dict(status=GRAPH_CONTROLS, actual_author_graph_audit_sha256=sha(out / 'author_graph_audit.json'),
                                  positive_graphs=3, graph_negatives=23, source_review_positives=2, source_review_negatives=38,
                                  provenance_positives=1, provenance_negatives=20, exact_progress_controls=4,
                                  actual99graph_read=False, scientific_census_checked=False)
                else:
                    result = dict(status=CENSUS_CONTROLS, **author_census_controls(out, pin, deadline, args))
                result.update(admission_audit=admission_audit)
            elif args.mode == 'projection':
                for field in ['producer_summary', 'controls_gate']:
                    need(getattr(args, field) and getattr(args, field + '_sha256'), 'ACTUAL', 'explicit ' + field + ' identity')
                result = dict(status=GRAPH_PASS, **projection_full(out, pin, closure, read, args))
            else:
                for field in ['manifest', 'controls_gate', 'graph_input', 'input_gate']:
                    need(getattr(args, field) and getattr(args, field + '_sha256'), 'ACTUAL', 'explicit ' + field + ' identity')
                result = dict(status=CENSUS_PASS, **census_full(out, pin, closure, read, deadline, args))
            result.update(producer_outputs_checked=True, observed_terminal_profile=observed_profile,
                          terminal_record=dict(path=args.supervisor, sha256=args.supervisor_sha256,
                          elapsed_seconds=ended['elapsed_seconds'], reaped=True, observed_process_scope_empty=True))
        need(all(sha(ROOT / name) == identity for name, identity in protected.items()), 'PROTECTED', 'live ledger/index unchanged')
        save(out / 'summary.json', dict(**result, checker_implementation_version=1, timestamp=datetime.now(timezone.utc).isoformat(),
             producer='/root/native_driver', verifier='/root/structural', method='independent_artifact_check', inputs_sha256=pins,
             command=[sys.executable, *sys.argv], cwd=str(ROOT), python=platform.python_version(), deadline=deadline.status(),
             target_resolution='NONE', new_unrestricted_exclusions=0, native_calls=0, census_calls=0, ledger_mutations=0, index_mutations=0,
             historical_protected_execution_state=dict(observations_sha256=protected, role='Before/after observations, not immutable input artifacts'),
             shared_components=['Prior independent K topology/proposal math, S full scalar adjacency, R canonical21field/parts/prefix/ties/calibration and G strictJSON are reused with exact pins.',
                                'New independent graph core and caller define changed schema/role/software/provenance/progress and receipts; no producer imports, old main, or mutable global override.',
                                'Literal manifest/synthetic stream checking is preserved from independently authored e01f path; Python/JSON/gzip/SHA256/tqdm/locked deadline/runtime are trusted.'],
             limitations=['Calibration and finite producer-controls audit do not establish actual99 census completion or approve changed science.',
                          'Actual projection reuses only an explicitly hash-bound prior complete source-census audit; it independently rechecks all derivative graph bytes and lineage.',
                          'A complete census covers one frozen-root graph and one labelled move universe only; graph counts are net adjacency toggles, not isomorphism classes.',
                          'No whole plateau, global minimum, target-wide coverage, automorphism, support uniqueness, invented native history or accepted path is inferred from a declared step.',
                          'Any actual99 exact SRG zero is exported for separate ROOT review; conservative NONE is not a veto or concealed target candidate.']))
        print(result['status'], flush=True)
    except BaseException as error:
        save(out / 'failure.json', dict(error=repr(error), inputs_sha256=pins, deadline=deadline.status(), outputs_preserved=True,
             native_calls=0, census_calls=0, ledger_mutations=0, index_mutations=0,
             protected_unchanged=all(sha(ROOT / name) == identity for name, identity in protected.items()),
             restart='No automatic retry; preserve failure and exact frozen source, inspect stage, then a separately reviewed new invocation/version if needed.'))
        raise


if __name__ == '__main__':
    main()

