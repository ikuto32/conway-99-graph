"""Independent complete outside-CN filter artifacts; no filter producer imports."""
import argparse
from collections import Counter
import copy
from datetime import datetime, timezone
import hashlib
import itertools
import json
from pathlib import Path
import re
import sys

from command_deadline import CommandDeadline
import audit_20261003_external_neighborhood_moments_v3 as Q

ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()
SPEC = SELF.with_name(SELF.stem + '_spec.md')
PRODUCER = 'acceleration/filter_20261003_external_moment_outside_cn_v1.py'
PINS = {
    PRODUCER: '3332f8177b3df8148ce0be491b3ead5230b71f5124667fc7a4b263cfbc567204',
    PRODUCER.replace('.py', '_spec.md'): '4224f4badce7ae14988afd9eed4f943612c87f4c505b690488585989e5376206',
    'acceleration/audit_20261003_external_neighborhood_moments_v3.py': '4a7f555c18475482dd9575e923f48939ceba165229b10e599358cde8b7f6f90c',
    'acceleration/audit_20261003_external_neighborhood_moments_v3_spec.md': 'a1fc166c2fe77216ca1bfe3ef61edcd59b3e55fa7781f52b8ebc452218114e71',
    'acceleration/command_deadline.py': '9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9',
    'acceleration/run_compute_command.py': '593a9feed6250739dc9672338df23ab171fc9a6a6db4196c1feb312efa33957a',
    'pyproject.toml': '273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339',
    'uv.lock': 'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',
    'acceleration/audit_20261003_external_type_cross_cn_cap_native_v1.md': '9336f741cb8088d09924de2074f70c3232d059ea387fc3f7f914fb67a75c3793',
    'docs/CANDIDATE_20261003_SEVENTEEN_POINT_EXTERNAL_NEIGHBOR_MOMENTS_V1.md': '70ef6392e86c6b9a3c9c6eac9b5d72abb9ea25741d3649282f66ac200bb93349',
}
BASE = 'acceleration/results/20261003_external_neighborhood_moment_seventeen_base01'
MODEL, TYPES = BASE + '/seventeen_base/model.json', BASE + '/seventeen_base/types.json'
ORIGINAL = {
    BASE + '/summary.json': '23fc6d633fe626a0a8141d3f974c415b6a559c6b67c60f231de8c412b63672d0',
    MODEL: 'd5f1afaf937b75c22f6e5d5c376a36f55f9326dc131399011a5502598742a3f9',
    TYPES: '4799c4603dc949ace22184c5742816eb0dbfe1bd6ea9b2d0ff407678e13de46a',
}
GATE = 'acceleration/results/20261003_independent_review/external_neighborhood_moments_seventeen_base_full01/summary.json'
GATE_SHA = 'af6b7877acb4519ca004707a46b21150d46a63f6ac8b57020656570a56ec099d'
CAL_STATUS = 'INDEPENDENT_EXTERNAL_MOMENT_OUTSIDE_CN_FILTER_V1_CALIBRATION_PASS'
CONTROLS_STATUS = 'INDEPENDENT_EXTERNAL_MOMENT_OUTSIDE_CN_FILTER_V1_CONTROLS_PASS'
FULL_STATUS = 'INDEPENDENT_EXTERNAL_MOMENT_OUTSIDE_CN_FILTER_V1_COMPLETE_PASS'
TRIPLES = ((0, 1, 2), (0, 3, 4), (0, 5, 6), (1, 7, 9), (1, 8, 10),
           (15, 11, 14), (16, 12, 13), (2, 15, 16), (3, 7, 11),
           (4, 8, 12), (5, 9, 13), (6, 10, 14))
need, same, tick, strict_json = Q.need, Q.same, Q.tick, Q.strict_json


def identity_map(mapping, stage):
    need(type(mapping) is dict and mapping, stage)
    for name, sha in mapping.items():
        need(type(name) is str and name and '\\' not in name and ':' not in name
             and not name.startswith('/') and all(p not in ('', '.', '..') for p in name.split('/'))
             and name != 'CLAIMS.yaml' and not name.startswith('.git/'), stage)
        need(type(sha) is str and re.fullmatch('[0-9a-f]{64}', sha) is not None, stage)
    return mapping


def fixed_h():
    edges = {tuple(sorted(pair)) for triple in TRIPLES for pair in itertools.combinations(triple, 2)}
    need(len(edges) == 36, 'LITERAL_BASE_PAIRS')
    return [[int(u != v and tuple(sorted((u, v))) in edges) for v in range(17)] for u in range(17)]


def dense_geometry(h, n, k, deadline):
    need(type(h) is list and 0 < len(h) <= 17 and type(n) is int and type(k) is int
         and n >= len(h) and k > 0 and k % 2 == 0, 'MODEL_PARAMETERS')
    m = len(h)
    need(all(type(row) is list and len(row) == m for row in h), 'GRAPH_SHAPE')
    need(all(type(v) is int and v in (0, 1) for row in h for v in row), 'GRAPH_BINARY_INTEGER')
    need(all(h[u][u] == 0 for u in range(m)), 'GRAPH_DIAGONAL')
    need(all(h[u][v] == h[v][u] for u in range(m) for v in range(m)), 'GRAPH_SYMMETRY')
    # Full dense integer products, separate from producer adjacency-set intersections.
    cn = []
    for u in range(m):
        tick(deadline)
        cn.append([sum(h[u][w] * h[w][v] for w in range(m)) for v in range(m)])
    b = [k - sum(row) for row in h]
    delta = [[None if u == v else 2 - h[u][v] - cn[u][v] for v in range(m)] for u in range(m)]
    need(min(b) >= 0 and all(delta[u][v] >= 0 for u, v in itertools.combinations(range(m), 2)), 'MODEL_DEFICIT')
    labels = [{'kind': 'total'}] + [{'kind': 'vertex', 'vertex': u} for u in range(m)]
    labels += [{'kind': 'pair', 'vertices': [u, v]} for u, v in itertools.combinations(range(m), 2)]
    rhs = [n - m] + b + [delta[u][v] for u, v in itertools.combinations(range(m), 2)]
    gram = [[n - m, *b]] + [[b[u], *[b[u] if u == v else delta[u][v] for v in range(m)]] for u in range(m)]
    return dict(schema='EXTERIOR_NEIGHBOR_MOMENT_MODEL_V1', target_order=n, target_degree=k,
                adjacent_cn=1, nonadjacent_cn=2, ordered_support_vertices=list(range(m)),
                induced_adjacency=h, H_squared=cn, vertex_rhs=b, pair_deficits=delta,
                row_labels=labels, right_hand_side=rhs, gram_matrix=gram, universe_mask_range=[0, (1 << m) - 1])


def column(mask, m):
    need(type(mask) is int and 0 <= mask < 1 << m, 'TYPE_MASK_INTEGER')
    selected = [(mask >> u) & 1 for u in range(m)]
    return {'mask': mask, 'coefficient': [1, *selected,
            *[selected[u] * selected[v] for u, v in itertools.combinations(range(m), 2)]]}


def typed_columns(columns, m, deadline):
    need(type(columns) is list and columns, 'TYPE_POPULATION')
    previous = -1
    for raw in columns:
        tick(deadline)
        need(type(raw) is dict and set(raw) == {'mask', 'coefficient'}, 'TYPE_FIELDS')
        mask = raw['mask']; expected = column(mask, m)
        need(mask > previous, 'TYPE_MASK_ORDER')
        need(same(raw['coefficient'], expected['coefficient']), 'TYPE_COEFFICIENT')
        previous = mask


def cap_record(h, mask, deadline):
    m = len(h); column(mask, m)
    selected = [u for u in range(m) if (mask >> u) & 1]
    bits = [(mask >> u) & 1 for u in range(m)]
    points = []
    for u in range(m):
        tick(deadline)
        count = sum(h[u][v] * bits[v] for v in range(m))
        witnesses = [v for v in range(m) if h[u][v] == 1 and bits[v] == 1]
        need(count == len(witnesses), 'DENSE_WITNESS_COUNT')
        inside = bits[u] == 1; cap = 1 if inside else 2
        points.append(dict(u=u, u_in_type=inside, cn_in_induced_H=count, necessary_cap=cap,
                           common_neighbor_witnesses=witnesses, passes=count <= cap))
    first = next((r for r in points if not r['passes']), None)
    return dict(mask=mask, selected_vertices=selected, eligible=first is None,
                first_veto=first, point_checks=points)


def result_counts(decisions, m, row_count):
    counts = Counter(str(r['first_veto']['u']) for r in decisions if not r['eligible'])
    retained = sum(r['eligible'] for r in decisions)
    return dict(original_types=len(decisions), support_vertices=m, complete_point_checks=m * len(decisions),
                retained_types=retained, removed_types=len(decisions) - retained,
                first_veto_point_counts=dict(sorted(counts.items(), key=lambda r: int(r[0]))),
                rows_unchanged=row_count, retained_coefficients_are_literal_originals=True,
                all_point_witnesses_saved_even_after_first_veto=True)


def expected_packet(model, columns, deadline, model_path=MODEL, model_sha=ORIGINAL[MODEL],
                    types_path=TYPES, types_sha=ORIGINAL[TYPES]):
    h = model['induced_adjacency']; m = len(h)
    typed_columns(columns, m, deadline)
    decisions = []
    for index, raw in enumerate(columns):
        record = cap_record(h, raw['mask'], deadline); record['original_type_index'] = index
        decisions.append(record)
    indices = [i for i, record in enumerate(decisions) if record['eligible']]
    retained = [columns[i] for i in indices]
    filtered = {key: model[key] for key in ['target_order', 'target_degree', 'adjacent_cn', 'nonadjacent_cn',
                     'ordered_support_vertices', 'induced_adjacency', 'row_labels', 'right_hand_side']}
    filtered.update(schema='OUTSIDE_VERTEX_CN_FILTERED_MOMENT_SYSTEM_V1',
        original_model_path=model_path, original_model_sha256=model_sha,
        original_types_path=types_path, original_types_sha256=types_sha,
        original_eligible_type_count=len(columns), eligible_type_count=len(retained),
        retained_original_type_indices=indices, retained_coefficients_are_literal_originals=True,
        original_row_labels_rhs_unchanged=True,
        additional_necessary_filter='For everyu: |N_H(u) intersectT| <=1 insideT, <=2 outsideT',
        feasibility_certificate=None,
        feasibility_certificate_unavailable_reason='No LP or primal reconstruction is run by this filter.')
    return dict(decisions=decisions, retained=retained, filtered=filtered,
                result=result_counts(decisions, m, len(model['row_labels'])))


def check_packet(packet, expected, deadline):
    decisions = packet.get('decisions')
    need(type(decisions) is list and len(decisions) == len(expected['decisions']), 'DECISION_POPULATION')
    for raw, wanted in zip(decisions, expected['decisions']):
        tick(deadline)
        need(type(raw) is dict and set(raw) == set(wanted), 'DECISION_FIELDS')
        need(same([raw['mask'], raw['original_type_index']], [wanted['mask'], wanted['original_type_index']]), 'DECISION_IDENTITY')
        need(same(raw['selected_vertices'], wanted['selected_vertices']), 'DECISION_SELECTED')
        points = raw['point_checks']
        need(type(points) is list and len(points) == len(wanted['point_checks']), 'POINT_POPULATION')
        for observed, point in zip(points, wanted['point_checks']):
            tick(deadline)
            need(type(observed) is dict and set(observed) == set(point), 'POINT_FIELDS')
            need(same(observed, point), 'POINT_COUNTS')
        need(same(raw['first_veto'], wanted['first_veto']), 'FIRST_VETO')
        need(same(raw['eligible'], wanted['eligible']), 'DECISION_ELIGIBILITY')
    need(same(packet.get('retained'), expected['retained']), 'RETAINED_COLUMNS')
    system, wanted = packet.get('filtered'), expected['filtered']
    need(type(system) is dict and set(system) == set(wanted), 'SYSTEM_FIELDS')
    groups = [(['schema'], 'SYSTEM_SCHEMA'),
              (['target_order', 'target_degree', 'adjacent_cn', 'nonadjacent_cn'], 'SYSTEM_PARAMETERS'),
              (['ordered_support_vertices', 'induced_adjacency'], 'SYSTEM_GEOMETRY'),
              (['original_model_path', 'original_model_sha256', 'original_types_path', 'original_types_sha256'], 'SYSTEM_ORIGIN'),
              (['row_labels'], 'SYSTEM_LABELS'), (['right_hand_side'], 'SYSTEM_RHS'),
              (['original_eligible_type_count', 'eligible_type_count', 'retained_original_type_indices'], 'SYSTEM_TYPES'),
              (['retained_coefficients_are_literal_originals', 'original_row_labels_rhs_unchanged', 'additional_necessary_filter'], 'SYSTEM_SEMANTICS'),
              (['feasibility_certificate', 'feasibility_certificate_unavailable_reason'], 'SYSTEM_NO_CERTIFICATE')]
    for keys, stage in groups:
        need(same({key: system[key] for key in keys}, {key: wanted[key] for key in keys}), stage)
    need(same(packet.get('result'), expected['result']), 'FILTER_RESULT')


def original_header(gate):
    need(type(gate) is dict and gate.get('status') == 'INDEPENDENT_EXTERNAL_NEIGHBOR_MOMENTS_V1_COMPLETE_PASS'
         and gate.get('producer') == '/root' and gate.get('verifier') == '/root/native_driver'
         and gate.get('method') == 'independent_artifact_check' and gate.get('target_resolution') == 'NONE'
         and type(gate.get('checker_implementation_version')) is int and gate['checker_implementation_version'] == 3, 'ORIGINAL_GATE_HEADER')
    mapping = identity_map(gate.get('inputs_sha256'), 'ORIGINAL_GATE_MAP')
    need(all(mapping.get(name) == sha for name, sha in ORIGINAL.items()), 'ORIGINAL_GATE_BINDING')
    science = gate.get('checked_scope', {}).get('science', {})
    need(same({key: science.get(key) for key in ['full_mask_universe', 'eligible_types', 'rows', 'complete_induced_products']},
              dict(full_mask_universe=131072, eligible_types=534, rows=154, complete_induced_products=289)), 'ORIGINAL_GATE_SCOPE')
    return mapping


def producer_header(report, mode):
    status = ('AUTHOR_EXTERNAL_MOMENT_OUTSIDE_CN_FILTER_V1_CONTROLS_PASS' if mode == 'calibrate'
              else 'CANDIDATE_EXTERNAL_MOMENT_OUTSIDE_CN_FILTER_V1_PENDING_INDEPENDENT_CHECK')
    need(type(report) is dict and report.get('status') == status and report.get('mode') == mode
         and report.get('source_author') == '/root/checkpoint_audit' and report.get('producer') == '/root/checkpoint_audit'
         and report.get('independent_verifier_required') == '/root/native_driver'
         and report.get('independent_approval') is False and report.get('target_resolution') == 'NONE'
         and report.get('ledger_index_git_mutations') is False, 'PRODUCER_HEADER')
    need(all(type(report.get(key)) is int and report[key] == 0
             for key in ['LP_calls', 'primal_solves', 'original_universe_reenumerations']), 'PRODUCER_FORBIDDEN_CALLS')
    need(same(report.get('controls'), dict(positive=2, strict_negative=4, total=6)), 'PRODUCER_CONTROL_COUNTS')
    need(mode != 'calibrate' or report.get('filter_result') is None, 'CALIBRATION_NOT_FILTER')
    identity_map(report.get('inputs_sha256'), 'PRODUCER_INPUT_MAP')
    identity_map(report.get('outputs_sha256'), 'PRODUCER_OUTPUT_MAP')


def receipt(plan, manifest, terminal, report, mode, packet_name, supervision_name):
    profile = plan.get('calibration') if mode == 'calibrate' and 'command' not in plan else plan
    need(type(profile) is dict, 'PLAN_PROFILE')
    command = profile.get('command')
    need(type(command) is list and all(type(word) is str for word in command) and command.count('--') == 1
         and command[:3] == ['C:/Users/ikuto/projects/conway-99-graph/build/research-venv/Scripts/python.exe',
                             '-B', 'acceleration/run_compute_command.py'], 'PLAN_COMMAND')
    child = command[command.index('--') + 1:]
    need(child[:6] == ['C:/Users/ikuto/.local/bin/uv.exe', 'run', '--locked', '--offline', 'python', '-B']
         and same(profile.get('child_argv'), child) and same(manifest.get('command'), child), 'CHILD_COMMAND')
    worker = [PRODUCER, mode, '--seconds', '150', '--out', packet_name,
              '--source-sha256', PINS[PRODUCER], '--spec-sha256', PINS[PRODUCER.replace('.py', '_spec.md')]]
    if mode == 'filter':
        worker += ['--full-gate', GATE, '--full-gate-sha256', GATE_SHA]
    need(same(child[6:], worker) and type(report.get('command')) is list
         and len(report['command']) == len(worker) + 1 and same(report['command'][1:], worker), 'WORKER_COMMAND')
    need(type(report['command'][0]) is str and Path(report['command'][0]).resolve()
         == (ROOT / 'build/research-venv/Scripts/python.exe').resolve(), 'WORKER_INTERPRETER')
    need(manifest.get('source_sha256') == PINS['acceleration/run_compute_command.py']
         and manifest.get('cwd') == str(ROOT) and report.get('cwd') == str(ROOT), 'SUPERVISOR_SOURCE_CWD')
    need(manifest.get('automatic_retry') is False and manifest.get('cumulative_across_commands') is False, 'SUPERVISOR_RETRY')
    for option, key, wanted in [('--seconds', 'seconds', 180), ('--shutdown-reserve-seconds', 'shutdown_reserve_seconds', 20)]:
        need(command.count(option) == (2 if option == '--seconds' else 1)
             and command[command.index(option) + 1] == str(wanted)
             and type(manifest.get(key)) in (int, float) and manifest[key] == wanted, 'PLAN_ALLOCATION')
    need(command[command.index('--out') + 1] == supervision_name, 'SUPERVISOR_OUTPUT')
    need(type(manifest.get('invocation_id')) is str and bool(manifest['invocation_id'])
         and terminal.get('invocation_id') == manifest['invocation_id']
         and type(terminal.get('command_exit_code')) is int and terminal['command_exit_code'] == 0
         and terminal.get('error') is None, 'TERMINAL')
    cleanup = terminal.get('cleanup')
    need(type(cleanup) is dict and cleanup.get('reaped') is True and cleanup.get('job_active_zero_observed') is True
         and type(cleanup.get('actual_exit_code')) is int and cleanup['actual_exit_code'] == 0
         and type(cleanup.get('cleanup_errors')) is list and cleanup['cleanup_errors'] == [], 'CLEANUP')


def rook_controls(deadline):
    rook = [[int(u != v and (u // 3 == v // 3 or u % 3 == v % 3)) for v in range(9)] for u in range(9)]
    rectangle = [0, 1, 3, 4]; exterior = [2, 5, 6, 7, 8]
    h4 = [[rook[u][v] for v in rectangle] for u in rectangle]; h8 = [row[:8] for row in rook[:8]]
    masks = [sum(rook[x][v] << i for i, v in enumerate(rectangle)) for x in exterior]
    h4_counts = [cap_record(h4, mask, deadline) for mask in masks]
    h8_mask = sum(rook[8][v] << v for v in range(8)); h8_counts = [cap_record(h8, h8_mask, deadline)]
    need(same(masks, [3, 12, 5, 10, 0]) and h8_mask == 228, 'LITERAL_ROOK_MASKS')
    need(all(row['eligible'] for row in h4_counts + h8_counts), 'KNOWN_ROOK_CAPS')
    bad = cap_record(fixed_h(), 44, deadline)
    need(same(bad['first_veto'], dict(u=0, u_in_type=False, cn_in_induced_H=3, necessary_cap=2,
              common_neighbor_witnesses=[2, 3, 5], passes=False)) and len(bad['point_checks']) == 17, 'LITERAL_BAD44')
    return dict(h4=h4, h8=h8, masks=masks, h4_counts=h4_counts, h8_counts=h8_counts, bad=bad)


def replay_controls(packet, deadline, read, save):
    fixture = rook_controls(deadline); rows = []
    cases = [('rook_rectangle_five_exterior', 'PASS'), ('rook_eight_vertex_exterior', 'PASS'),
             ('bad_mask44', 'OUTSIDE_CN_CAP'), ('bool_mask', 'TYPE_MASK_INTEGER'),
             ('float_mask', 'TYPE_MASK_INTEGER'), ('unordered_types', 'TYPE_MASK_ORDER')]
    for label, expected_stage in cases:
        raw = read(packet / ('control_' + label + '.json')); tick(deadline)
        if label == 'rook_rectangle_five_exterior':
            expected = dict(h=fixture['h4'], masks=fixture['masks'], expected_h=[[1] * 4] * 4 + [[0] * 4])
            observed_geometry = [cap_record(raw['h'], mask, deadline) for mask in raw['masks']]
        elif label == 'rook_eight_vertex_exterior':
            expected = dict(h=fixture['h8'], masks=[228], expected_h=[[2, 2, 1, 2, 2, 1, 1, 1]])
            observed_geometry = [cap_record(raw['h'], mask, deadline) for mask in raw['masks']]
        elif label == 'bad_mask44':
            expected = dict(h=fixed_h(), mask=44, expected_first_veto=fixture['bad']['first_veto'])
            observed_geometry = cap_record(raw['h'], raw['mask'], deadline)
        elif label in ['bool_mask', 'float_mask']:
            expected = dict(h=fixture['h4'], mask=True if label == 'bool_mask' else 3.0)
            observed_geometry = None
        else:
            expected = dict(types=[column(1, 17), column(0, 17)]); observed_geometry = None
        need(same(raw, expected), 'LITERAL_CONTROL:' + label)
        observed = 'PASS'
        try:
            if label == 'unordered_types':
                typed_columns(raw['types'], 17, deadline)
            elif label in ['bool_mask', 'float_mask']:
                cap_record(raw['h'], raw['mask'], deadline)
            elif label == 'bad_mask44':
                observed = 'OUTSIDE_CN_CAP' if not observed_geometry['eligible'] else 'PASS'
        except ValueError as error:
            observed = str(error)
        need(observed == expected_stage, 'PRODUCER_CONTROL_STAGE:' + label)
        rows.append(dict(case=label, expected_stage=expected_stage, actual_stage=observed,
                         actual_geometry=observed_geometry))
    wanted = dict(positive=2, strict_negative=4, total=6, records=rows, known_graph_exterior_types=6,
                  known_graph_point_checks=28, deliberately_bad_mask_point_checks=17,
                  known_realizations_are_rook9_only=True, target_graph_realizations=0)
    need(same(read(packet / 'controls.json'), wanted), 'COMPLETE_PRODUCER_CONTROL_TABLE')
    save('producer_controls_replay.json', wanted)
    return dict(producer_positive_cases=2, producer_precise_negative_cases=4, producer_raw_control_files=7,
                known_rook_exterior_types=6, known_rook_point_checks=28, bad44_point_checks=17,
                actual534_filter_read=False)


def synthetic_frames(mode):
    packet, supervision = 'acceleration/results/synthetic_cap_packet', 'acceleration/results/synthetic_cap_supervision'
    worker = [PRODUCER, mode, '--seconds', '150', '--out', packet,
              '--source-sha256', PINS[PRODUCER], '--spec-sha256', PINS[PRODUCER.replace('.py', '_spec.md')]]
    if mode == 'filter':
        worker += ['--full-gate', GATE, '--full-gate-sha256', GATE_SHA]
    child = ['C:/Users/ikuto/.local/bin/uv.exe', 'run', '--locked', '--offline', 'python', '-B', *worker]
    command = ['C:/Users/ikuto/projects/conway-99-graph/build/research-venv/Scripts/python.exe', '-B',
               'acceleration/run_compute_command.py', '--seconds', '180', '--shutdown-reserve-seconds', '20',
               '--allocation-reason', 'synthetic', '--success-criterion', 'synthetic',
               '--verification-criterion', 'synthetic', '--out', supervision, '--', *child]
    report = dict(status='AUTHOR_EXTERNAL_MOMENT_OUTSIDE_CN_FILTER_V1_CONTROLS_PASS' if mode == 'calibrate'
                       else 'CANDIDATE_EXTERNAL_MOMENT_OUTSIDE_CN_FILTER_V1_PENDING_INDEPENDENT_CHECK',
                  producer='/root/checkpoint_audit', source_author='/root/checkpoint_audit',
                  independent_verifier_required='/root/native_driver', independent_approval=False, mode=mode,
                  target_resolution='NONE', ledger_index_git_mutations=False, LP_calls=0, primal_solves=0,
                  original_universe_reenumerations=0, controls=dict(positive=2, strict_negative=4, total=6),
                  filter_result=None, inputs_sha256={'synthetic/in': 'a' * 64}, outputs_sha256={'synthetic/out': 'b' * 64},
                  command=[str(ROOT / 'build/research-venv/Scripts/python.exe'), *worker], cwd=str(ROOT))
    manifest = dict(command=child, source_sha256=PINS['acceleration/run_compute_command.py'], cwd=str(ROOT),
                    automatic_retry=False, cumulative_across_commands=False, seconds=180.0,
                    shutdown_reserve_seconds=20.0, invocation_id='synthetic')
    terminal = dict(invocation_id='synthetic', command_exit_code=0, error=None,
                    cleanup=dict(reaped=True, job_active_zero_observed=True, actual_exit_code=0, cleanup_errors=[]))
    return dict(plan=dict(command=command, child_argv=child), manifest=manifest, terminal=terminal, report=report)


def own_calibration(deadline, save):
    fixtures = rook_controls(deadline); positives, negatives = [], []
    for label, value in [('rook_rectangle', fixtures['h4_counts']), ('rook_eight', fixtures['h8_counts']), ('bad44', fixtures['bad'])]:
        save('positive_' + label + '.json', value); positives.append(label)
    model = dense_geometry(fixtures['h4'], 9, 4, deadline)
    columns = [column(mask, 4) for mask in range(16)]
    expected = expected_packet(model, columns, deadline)
    check_packet(expected, expected, deadline); save('positive_all16_synthetic_columns.json', dict(model=model, columns=columns, packet=expected))
    positives.append('all16_synthetic_columns')
    for mode in ['calibrate', 'filter']:
        raw = synthetic_frames(mode); producer_header(raw['report'], mode)
        receipt(raw['plan'], raw['manifest'], raw['terminal'], raw['report'], mode,
                'acceleration/results/synthetic_cap_packet', 'acceleration/results/synthetic_cap_supervision')
        save('positive_' + mode + '_receipt.json', raw); positives.append(mode + '_receipt')
    gate = dict(status='INDEPENDENT_EXTERNAL_NEIGHBOR_MOMENTS_V1_COMPLETE_PASS', producer='/root',
                verifier='/root/native_driver', method='independent_artifact_check', target_resolution='NONE',
                checker_implementation_version=3, inputs_sha256=ORIGINAL,
                checked_scope=dict(science=dict(full_mask_universe=131072, eligible_types=534, rows=154, complete_induced_products=289)))
    original_header(gate); save('positive_original_gate.json', gate); positives.append('original_gate')
    def reject(label, value, stage, function):
        tick(deadline); save('negative_' + label + '.json', value); observed = None
        try:
            function(value)
        except ValueError as error:
            observed = str(error)
        need(observed == stage, 'CONTROL_STAGE:' + label)
        negatives.append(dict(case=label, expected_stage=stage, actual_stage=observed))
    def put(value, path, replacement):
        parent = value
        for key in path[:-1]:
            parent = parent[key]
        parent[path[-1]] = replacement
    packet_changes = [
        ('decision_population', ['decisions'], [], 'DECISION_POPULATION'),
        ('decision_extra', ['decisions', 0, 'extra'], 0, 'DECISION_FIELDS'),
        ('mask_bool', ['decisions', 0, 'mask'], False, 'DECISION_IDENTITY'),
        ('index_float', ['decisions', 0, 'original_type_index'], 0.0, 'DECISION_IDENTITY'),
        ('selected_order', ['decisions', 3, 'selected_vertices'], [1, 0], 'DECISION_SELECTED'),
        ('point_truncated_after_veto', ['decisions', 7, 'point_checks'], expected['decisions'][7]['point_checks'][:1], 'POINT_POPULATION'),
        ('point_extra', ['decisions', 0, 'point_checks', 0, 'extra'], 0, 'POINT_FIELDS'),
        ('point_u_bool', ['decisions', 0, 'point_checks', 0, 'u'], False, 'POINT_COUNTS'),
        ('point_inside_integer', ['decisions', 0, 'point_checks', 0, 'u_in_type'], 0, 'POINT_COUNTS'),
        ('point_count_bool', ['decisions', 0, 'point_checks', 0, 'cn_in_induced_H'], False, 'POINT_COUNTS'),
        ('point_count_float', ['decisions', 0, 'point_checks', 0, 'cn_in_induced_H'], 0.0, 'POINT_COUNTS'),
        ('point_one_bool', ['decisions', 3, 'point_checks', 0, 'cn_in_induced_H'], True, 'POINT_COUNTS'),
        ('point_cap_uniform_one', ['decisions', 0, 'point_checks', 0, 'necessary_cap'], 1, 'POINT_COUNTS'),
        ('point_pass_integer', ['decisions', 0, 'point_checks', 0, 'passes'], 1, 'POINT_COUNTS'),
        ('point_witness_extra', ['decisions', 0, 'point_checks', 0, 'common_neighbor_witnesses'], [1], 'POINT_COUNTS'),
        ('point_witness_order', ['decisions', 7, 'point_checks', 0, 'common_neighbor_witnesses'], [2, 1], 'POINT_COUNTS'),
        ('point_after_veto_damage', ['decisions', 7, 'point_checks', 1, 'cn_in_induced_H'], 9, 'POINT_COUNTS'),
        ('first_veto_missing', ['decisions', 7, 'first_veto'], None, 'FIRST_VETO'),
        ('first_veto_wrong_point', ['decisions', 7, 'first_veto'], expected['decisions'][7]['point_checks'][1], 'FIRST_VETO'),
        ('false_veto', ['decisions', 0, 'first_veto'], expected['decisions'][0]['point_checks'][0], 'FIRST_VETO'),
        ('eligible_numeric', ['decisions', 0, 'eligible'], 1, 'DECISION_ELIGIBILITY'),
        ('retained_truncated', ['retained'], expected['retained'][:-1], 'RETAINED_COLUMNS'),
        ('retained_coefficient_bool', ['retained', 0, 'coefficient', 0], True, 'RETAINED_COLUMNS'),
        ('system_extra', ['filtered', 'extra'], 0, 'SYSTEM_FIELDS'),
        ('system_schema', ['filtered', 'schema'], 'EXTERIOR_NEIGHBOR_MOMENT_MODEL_V1', 'SYSTEM_SCHEMA'),
        ('system_degree_float', ['filtered', 'target_degree'], 4.0, 'SYSTEM_PARAMETERS'),
        ('system_order', ['filtered', 'ordered_support_vertices'], [1, 0, 2, 3], 'SYSTEM_GEOMETRY'),
        ('system_h_bool', ['filtered', 'induced_adjacency', 0, 0], False, 'SYSTEM_GEOMETRY'),
        ('system_origin_hash', ['filtered', 'original_types_sha256'], '0' * 64, 'SYSTEM_ORIGIN'),
        ('system_labels', ['filtered', 'row_labels'], [], 'SYSTEM_LABELS'),
        ('system_rhs_float', ['filtered', 'right_hand_side', 0], 5.0, 'SYSTEM_RHS'),
        ('system_retained_ids', ['filtered', 'retained_original_type_indices'], [], 'SYSTEM_TYPES'),
        ('system_count_float', ['filtered', 'original_eligible_type_count'], 16.0, 'SYSTEM_TYPES'),
        ('system_literal_false', ['filtered', 'retained_coefficients_are_literal_originals'], False, 'SYSTEM_SEMANTICS'),
        ('system_certificate', ['filtered', 'feasibility_certificate'], {}, 'SYSTEM_NO_CERTIFICATE'),
        ('result_bool', ['result', 'complete_point_checks'], True, 'FILTER_RESULT'),
        ('result_veto_counts', ['result', 'first_veto_point_counts'], {}, 'FILTER_RESULT'),
    ]
    for label, path, value, stage in packet_changes:
        damaged = copy.deepcopy(expected); put(damaged, path, value)
        reject(label, damaged, stage, lambda v: check_packet(v, expected, deadline))
    for label, value, stage in [('bool', True, 'TYPE_MASK_INTEGER'), ('float', 0.0, 'TYPE_MASK_INTEGER'),
                              ('negative', -1, 'TYPE_MASK_INTEGER'), ('range', 16, 'TYPE_MASK_INTEGER')]:
        reject('column_mask_' + label, value, stage, lambda v: column(v, 4))
    for label, value, stage in [('order', [column(1, 4), column(0, 4)], 'TYPE_MASK_ORDER'),
          ('duplicate', [column(0, 4), column(0, 4)], 'TYPE_MASK_ORDER'),
          ('extra', [dict(column(0, 4), extra=0)], 'TYPE_FIELDS'),
          ('coefficient_bool', [dict(mask=0, coefficient=[True, *column(0, 4)['coefficient'][1:]])], 'TYPE_COEFFICIENT')]:
        reject('columns_' + label, value, stage, lambda v: typed_columns(v, 4, deadline))
    graph_changes = [('shape', [], 'MODEL_PARAMETERS'), ('row', [[]] * 4, 'GRAPH_SHAPE'),
                     ('bool', [0, 0], 'GRAPH_BINARY_INTEGER'), ('float', [0, 0], 'GRAPH_BINARY_INTEGER'),
                     ('diagonal', [0, 0], 'GRAPH_DIAGONAL'), ('symmetry', [0, 1], 'GRAPH_SYMMETRY')]
    for label, path, stage in graph_changes:
        damaged = copy.deepcopy(fixtures['h4'])
        if label in ['shape', 'row']:
            damaged = path
        else:
            damaged[path[0]][path[1]] = {'bool': False, 'float': 0.0, 'diagonal': 1, 'symmetry': 0}[label]
        reject('graph_' + label, damaged, stage, lambda v: dense_geometry(v, 9, 4, deadline))
    base = synthetic_frames('filter')
    frame_changes = [
        ('report_status', ['report', 'status'], 'PASS', 'PRODUCER_HEADER'),
        ('report_role', ['report', 'producer'], '/root/native_driver', 'PRODUCER_HEADER'),
        ('report_approved', ['report', 'independent_approval'], True, 'PRODUCER_HEADER'),
        ('report_LP_bool', ['report', 'LP_calls'], False, 'PRODUCER_FORBIDDEN_CALLS'),
        ('report_solve', ['report', 'primal_solves'], 1, 'PRODUCER_FORBIDDEN_CALLS'),
        ('report_controls_float', ['report', 'controls', 'total'], 6.0, 'PRODUCER_CONTROL_COUNTS'),
        ('report_mutable', ['report', 'inputs_sha256'], {'CLAIMS.yaml': 'a' * 64}, 'PRODUCER_INPUT_MAP'),
        ('report_hash', ['report', 'outputs_sha256', 'synthetic/out'], 'a' * 63, 'PRODUCER_OUTPUT_MAP'),
        ('plan_empty', ['plan', 'command'], [], 'PLAN_COMMAND'),
        ('plan_child_empty', ['plan', 'child_argv'], [], 'CHILD_COMMAND'),
        ('manifest_child', ['manifest', 'command'], [], 'CHILD_COMMAND'),
        ('worker_empty', ['report', 'command'], [], 'WORKER_COMMAND'),
        ('interpreter', ['report', 'command', 0], 'elsewhere/python.exe', 'WORKER_INTERPRETER'),
        ('source', ['manifest', 'source_sha256'], 'a' * 64, 'SUPERVISOR_SOURCE_CWD'),
        ('cwd', ['manifest', 'cwd'], 'elsewhere', 'SUPERVISOR_SOURCE_CWD'),
        ('retry', ['manifest', 'automatic_retry'], True, 'SUPERVISOR_RETRY'),
        ('outer_bool', ['manifest', 'seconds'], True, 'PLAN_ALLOCATION'),
        ('outer_changed', ['manifest', 'seconds'], 180.5, 'PLAN_ALLOCATION'),
        ('reserve_changed', ['manifest', 'shutdown_reserve_seconds'], 19, 'PLAN_ALLOCATION'),
        ('terminal_exit_bool', ['terminal', 'command_exit_code'], False, 'TERMINAL'),
        ('terminal_id', ['terminal', 'invocation_id'], 'other', 'TERMINAL'),
        ('terminal_error', ['terminal', 'error'], 'error', 'TERMINAL'),
        ('reaped', ['terminal', 'cleanup', 'reaped'], False, 'CLEANUP'),
        ('job', ['terminal', 'cleanup', 'job_active_zero_observed'], False, 'CLEANUP'),
        ('cleanup_bool', ['terminal', 'cleanup', 'actual_exit_code'], False, 'CLEANUP'),
        ('cleanup_float', ['terminal', 'cleanup', 'actual_exit_code'], 0.0, 'CLEANUP'),
        ('cleanup_errors', ['terminal', 'cleanup', 'cleanup_errors'], ['error'], 'CLEANUP'),
    ]
    def frame_check(value):
        producer_header(value['report'], 'filter')
        receipt(value['plan'], value['manifest'], value['terminal'], value['report'], 'filter',
                'acceleration/results/synthetic_cap_packet', 'acceleration/results/synthetic_cap_supervision')
    for label, path, value, stage in frame_changes:
        damaged = copy.deepcopy(base); put(damaged, path, value)
        reject(label, damaged, stage, frame_check)
    for label, path, value, stage in [
        ('status', ['status'], 'PASS', 'ORIGINAL_GATE_HEADER'),
        ('role', ['verifier'], '/root/checkpoint_audit', 'ORIGINAL_GATE_HEADER'),
        ('version_bool', ['checker_implementation_version'], True, 'ORIGINAL_GATE_HEADER'),
        ('type_binding', ['inputs_sha256', TYPES], 'a' * 64, 'ORIGINAL_GATE_BINDING'),
        ('scope_float', ['checked_scope', 'science', 'rows'], 154.0, 'ORIGINAL_GATE_SCOPE')]:
        damaged = copy.deepcopy(gate); put(damaged, path, value)
        reject('gate_' + label, damaged, stage, original_header)
    for label, raw, stage in [('duplicate', b'{"x":0,"x":1}', 'JSON_DUPLICATE'), ('nonfinite', b'{"x":NaN}', 'JSON_NONFINITE')]:
        reject('json_' + label, dict(raw_utf8=raw.decode('utf8')), stage, lambda v: strict_json(v['raw_utf8'].encode('utf8')))
    need(len(positives) == 7 and len(negatives) == 85, 'OWN_CONTROL_POPULATION')
    save('controls.json', dict(positive=positives, precise_negative=negatives,
         actual_producer_packet_read=False, actual534_filter_read=False, synthetic_all_mask_columns=16,
         synthetic_complete_point_checks=64, known_rook_exterior_types=6, known_rook_point_checks=28, bad44_point_checks=17))
    return dict(positive_cases=7, precise_negative_cases=85, actual_producer_packet_read=False,
                actual534_filter_read=False, synthetic_all_mask_columns=16, synthetic_complete_point_checks=64)


def authenticated_gate(path, sha, status, deadline, read, pin):
    report = read(path, sha)
    need(type(report) is dict and report.get('status') == status and report.get('producer') == '/root/checkpoint_audit'
         and report.get('verifier') == '/root/native_driver' and report.get('method') == 'independent_artifact_check'
         and report.get('target_resolution') == 'NONE' and type(report.get('implementation_version')) is int
         and report['implementation_version'] == 1 and report.get('source_sha256') == pin(SELF)[1]
         and report.get('spec_sha256') == pin(SPEC)[1], 'CHECKER_GATE_HEADER')
    for key in ['inputs_sha256', 'outputs_sha256']:
        for name, digest in identity_map(report.get(key), 'CHECKER_GATE_MAP').items():
            tick(deadline); pin(ROOT / name, digest)
    return report


def actual_check(args, deadline, read, pin, save):
    required = ['calibration', 'calibration_sha256', 'producer_root', 'producer_summary_sha256', 'producer_plan',
                'producer_plan_sha256', 'supervision_out', 'supervisor_manifest_sha256', 'supervisor_summary_sha256']
    need(all(getattr(args, key) is not None for key in required), 'ACTUAL_ARGUMENTS')
    own = authenticated_gate(args.calibration, args.calibration_sha256, CAL_STATUS, deadline, read, pin)
    need(same(own.get('checked_scope'), dict(positive_cases=7, precise_negative_cases=85,
              actual_producer_packet_read=False, actual534_filter_read=False,
              synthetic_all_mask_columns=16, synthetic_complete_point_checks=64)), 'OWN_CALIBRATION_SCOPE')
    mode = 'calibrate' if args.mode == 'producer-controls' else 'filter'
    packet = args.producer_root.resolve()
    need(packet.is_relative_to(ROOT / 'acceleration/results') and packet.is_dir()
         and not packet.is_relative_to(ROOT / BASE), 'PRODUCER_NAMESPACE')
    report = read(packet / 'summary.json', args.producer_summary_sha256); producer_header(report, mode)
    plan = read(args.producer_plan, args.producer_plan_sha256)
    manifest = read(args.supervision_out / 'manifest.json', args.supervisor_manifest_sha256)
    terminal = read(args.supervision_out / 'summary.json', args.supervisor_summary_sha256)
    receipt(plan, manifest, terminal, report, mode, packet.relative_to(ROOT).as_posix(),
            args.supervision_out.resolve().relative_to(ROOT).as_posix())
    for name, sha in report['inputs_sha256'].items():
        pin(ROOT / name, sha)
    required_software = {key: value for key, value in PINS.items() if key in
        [PRODUCER, PRODUCER.replace('.py', '_spec.md'), 'acceleration/command_deadline.py',
         'acceleration/run_compute_command.py', 'pyproject.toml', 'uv.lock',
         'acceleration/audit_20261003_external_type_cross_cn_cap_native_v1.md']}
    need(all(report['inputs_sha256'].get(name) == sha for name, sha in required_software.items()), 'PRODUCER_SOFTWARE_BINDING')
    controls_names = {'control_' + label + '.json' for label in ['rook_rectangle_five_exterior',
                'rook_eight_vertex_exterior', 'bad_mask44', 'bool_mask', 'float_mask', 'unordered_types']} | {'controls.json'}
    expected_names = controls_names | ({'decisions.json', 'types.json', 'filtered_system.json'} if mode == 'filter' else set())
    actual_names = {p.relative_to(packet).as_posix() for p in packet.rglob('*') if p.is_file() and p != packet / 'summary.json'}
    need(actual_names == expected_names and set(report['outputs_sha256'])
         == {(packet / name).relative_to(ROOT).as_posix() for name in expected_names}, 'OUTPUT_POPULATION')
    for name, sha in report['outputs_sha256'].items():
        path = (ROOT / name).resolve(); need(path.is_relative_to(packet), 'OUTPUT_NAMESPACE'); pin(path, sha)
    replay = replay_controls(packet, deadline, read, save)
    if mode == 'calibrate':
        need(args.producer_controls is None and args.producer_controls_sha256 is None
             and GATE not in report['inputs_sha256'] and all(name not in report['inputs_sha256'] for name in ORIGINAL), 'CONTROLS_NO_ORIGINAL_FILTER')
        return replay
    need(args.producer_controls is not None and args.producer_controls_sha256 is not None, 'GENUINE_CONTROLS_GATE_REQUIRED')
    controls_gate = authenticated_gate(args.producer_controls, args.producer_controls_sha256, CONTROLS_STATUS, deadline, read, pin)
    need(same(controls_gate.get('checked_scope'), replay), 'CONTROLS_GATE_SCOPE')
    gate = read(ROOT / GATE, GATE_SHA); closure = original_header(gate)
    for name, sha in closure.items():
        pin(ROOT / name, sha)
    need(report['inputs_sha256'].get(GATE) == GATE_SHA
         and all(report['inputs_sha256'].get(name) == sha for name, sha in closure.items()), 'PRODUCER_ORIGINAL_CLOSURE')
    model = read(ROOT / MODEL, ORIGINAL[MODEL]); columns = read(ROOT / TYPES, ORIGINAL[TYPES])
    core = dense_geometry(fixed_h(), 99, 14, deadline)
    need(type(model) is dict and same({key: model.get(key) for key in core}, core)
         and type(model.get('eligible_type_count')) is int and model['eligible_type_count'] == 534, 'ORIGINAL_MODEL_REBUILD')
    need(type(columns) is list and len(columns) == 534, 'ORIGINAL_TYPE_POPULATION')
    expected = expected_packet(model, columns, deadline)
    actual = dict(decisions=read(packet / 'decisions.json'), retained=read(packet / 'types.json'),
                  filtered=read(packet / 'filtered_system.json'), result=report.get('filter_result'))
    check_packet(actual, expected, deadline)
    save('independent_filter_counts.json', expected['result'])
    return dict(original_types=534, complete_support_point_checks=9078, support_vertices=17,
                complete_dense_induced_products=289, original_unchanged_moment_rows=154,
                retained_types=expected['result']['retained_types'], removed_types=expected['result']['removed_types'],
                first_veto_point_counts=expected['result']['first_veto_point_counts'],
                complete_witnesses_after_first_veto=True, literal_original_retained_columns=True,
                producer_controls=replay, original_universe_reenumerated=False,
                feasibility_certificate_checked=False, graph_completion_proved=False)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode', choices=['calibrate', 'producer-controls', 'full'])
    p.add_argument('--seconds', type=float, required=True); p.add_argument('--out', type=Path, required=True)
    for name in ['calibration', 'producer-root', 'producer-plan', 'supervision-out', 'producer-controls']:
        p.add_argument('--' + name, type=Path)
        if name not in ['producer-root', 'supervision-out']:
            p.add_argument('--' + name + '-sha256')
    for name in ['producer-summary-sha256', 'supervisor-manifest-sha256', 'supervisor-summary-sha256']:
        p.add_argument('--' + name)
    args = p.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='Complete independent534x17 dense integer cap/witness checking and immutable receipt closure; twenty-second save reserve')
    out = args.out.resolve(); need(out.is_relative_to(ROOT / 'acceleration/results') and not out.exists(), 'FRESH_OUTPUT')
    out.mkdir(parents=True); pins = {}
    def digest(path):
        tick(deadline); sha = hashlib.sha256()
        with path.open('rb') as stream:
            while block := stream.read(1024 * 1024):
                sha.update(block); tick(deadline)
        tick(deadline); return sha.hexdigest()
    def pin(path, expected=None):
        path = Path(path).resolve(); need(path.is_relative_to(ROOT) and path.is_file(), 'INPUT_PATH')
        name = path.relative_to(ROOT).as_posix()
        need(name != 'CLAIMS.yaml' and not name.startswith('.git/'), 'MUTABLE_INPUT')
        observed = digest(path); need(expected is None or type(expected) is str and observed == expected, 'INPUT_IDENTITY:' + name)
        need(name not in pins or pins[name] == observed, 'INPUT_CHANGED'); pins[name] = observed
        return path, observed
    def read(path, expected=None):
        value = strict_json(pin(path, expected)[0].read_bytes()); tick(deadline); return value
    def save(name, value):
        tick(deadline); raw = (json.dumps(value, allow_nan=False, indent=2) + '\n').encode('utf8'); tick(deadline)
        with (out / name).open('xb') as stream:
            for start in range(0, len(raw), 1024 * 1024):
                stream.write(raw[start:start + 1024 * 1024]); tick(deadline)
        tick(deadline)
    try:
        for name, sha in PINS.items():
            pin(ROOT / name, sha)
        pin(SELF); pin(SPEC)
        if args.mode == 'calibrate':
            need(all(getattr(args, key) is None for key in ['calibration', 'calibration_sha256',
                'producer_root', 'producer_summary_sha256', 'producer_plan', 'producer_plan_sha256',
                'supervision_out', 'supervisor_manifest_sha256', 'supervisor_summary_sha256',
                'producer_controls', 'producer_controls_sha256']), 'CAL_NO_ACTUAL_INPUTS')
            scope = own_calibration(deadline, save); status = CAL_STATUS
        else:
            scope = actual_check(args, deadline, read, pin, save)
            status = CONTROLS_STATUS if args.mode == 'producer-controls' else FULL_STATUS
        for name, sha in list(pins.items()):
            pin(ROOT / name, sha)
        outputs = {path.relative_to(ROOT).as_posix(): digest(path) for path in sorted(out.iterdir()) if path.is_file()}
        save('summary.json', dict(status=status, timestamp=datetime.now(timezone.utc).isoformat(),
             producer='/root/checkpoint_audit', verifier='/root/native_driver', method='independent_artifact_check',
             target_resolution='NONE', implementation_version=1, command=[sys.executable, *sys.argv],
             source_sha256=pins[SELF.relative_to(ROOT).as_posix()], spec_sha256=pins[SPEC.relative_to(ROOT).as_posix()],
             inputs_sha256=pins, outputs_sha256=outputs, checked_scope=scope,
             shared_origins=['ROOT proposed cap; Native9336 separately derived necessary lemma',
                'Unchanged qualified independent Native momentV3 strictJSON/type-exact equality/deadline scaffold only; new dense cap/model arithmetic does not import producer3332'],
             producer_code_imports=0, target_or_feasibility_claimed=False, deadline=deadline.status()))
        tick(deadline); return 0
    except BaseException as error:
        if (out / 'summary.json').exists():
            (out / 'summary.json').rename(out / 'summary.not_approved.json')
        (out / 'failure.json').write_text(json.dumps(dict(error=repr(error), inputs_sha256=pins,
             deadline=deadline.status(), automatic_retry=False, partial_outputs_preserved=True,
             feasibility_or_nonexistence_inferred=False), allow_nan=False, indent=2) + '\n', encoding='utf8')
        raise


if __name__ == '__main__':
    raise SystemExit(main())
