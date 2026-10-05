"""Independent raw singleton checker. No producer imports or work on import."""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import itertools
import json
import math
from pathlib import Path
import stat
import sys

from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SELF = 'acceleration/audit_20261004_fixed17_dual_gram_singletons_v1.py'
SPEC = 'acceleration/audit_20261004_fixed17_dual_gram_singletons_v1_spec.md'
PRODUCER = 'acceleration/diagnose_20261004_fixed17_dual_gram_singletons_v1.py'
PRODUCER_SPEC = 'acceleration/diagnose_20261004_fixed17_dual_gram_singletons_v1_spec.md'
MODEL = 'acceleration/results/20261003_external_moment_outside_cn_filter01/filtered_system.json'
TYPES = 'acceleration/results/20261003_external_moment_outside_cn_filter01/types.json'
FILTER = 'acceleration/results/20261003_independent_review/external_moment_outside_cn_filter_full01/summary.json'
RAW = 'acceleration/results/20261004_fixed17_dual_gram_singletons01'
AUTHOR = 'acceleration/results/20261004_fixed17_dual_gram_singleton_controls01'
PLAN = 'acceleration/plan_20261004_fixed17_dual_gram_singletons_v1.json'
SUP = 'acceleration/results/20261004_fixed17_dual_gram_singletons_supervision01'
MODEL_PINS = {
    MODEL: 'c628c76325d5b49106740bce7c6d3b72bc7728fdc78d85437ad484f3afbd7306',
    TYPES: '87d0272e244f60f1eefa06d3a0b2d0179a275791f7bb586992b16f648595bad2',
    FILTER: '50b096b69decdea439097199cdb93a00f4c67de8653c224cbd90312dfcf2620a',
}
SOFTWARE = {
    'acceleration/command_deadline.py': '9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9',
    'acceleration/run_compute_command.py': '593a9feed6250739dc9672338df23ab171fc9a6a6db4196c1feb312efa33957a',
    'acceleration/run_compute_command_v2.py': '46410201dcad20eb056b8206a1b6687f9ac74f0f34e3cc66197eff5c59d55e17',
    'pyproject.toml': '273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339',
    'uv.lock': 'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',
}
PRODUCER_PINS = {
    PRODUCER: '3f705972d1b7d7623d609ac333545d68dda450b4eeb8c5779bfe5cb417b41dec',
    PRODUCER_SPEC: 'f8ea9005f895cc49c05edb0ebb62d58fc79a986d35960a0901ed5905753958b7',
    PLAN: 'bfdd7e5149b50aef61aba8f66bea4a364deb7310d1873cb531595687e7dfa1e8',
    RAW + '/summary.json': 'e6d60171fb6d2d8b22e7d1eac02d68972de805ecb56329e77d75a199cb4f4be9',
    SUP + '/manifest.json': '84c29fe7e84b65eea89834735276c2972b35e355f3e5096e6c2f1b94f5fd77f7',
    SUP + '/summary.json': 'a07e5948f5f47a397976fa85fc14effea97463ef7f02b164abcd6990acd9c83e',
    AUTHOR + '/summary.json': 'ab9cb60b33aa2eca0b02d4b964ddd01e009280fba07f7561b6b816bb8628bed4',
    AUTHOR + '/controls.json': 'df1c88c87da0e3e7e29d2ed2b0e04061878329c38037520db48ac54092d37531',
    'acceleration/plan_20261004_fixed17_dual_gram_singleton_author_controls_v1.json': '971ca139d6b42f471fd296e1832d6d6864c8eef75c4f408645cad02aa9be6235',
    'acceleration/results/20261004_fixed17_dual_gram_singleton_controls_supervision01/manifest.json': '66adc8d3be19c6fab054a43c43a07a5be17b3753de312e7b6f70f8de77761a96',
    'acceleration/results/20261004_fixed17_dual_gram_singleton_controls_supervision01/summary.json': '2c641bad4f665ad5c546393548c734599013cb63fd347214e8a6e558140c7c42',
    'acceleration/results/20261004_fixed17_dual_gram_singleton_v1_root_actual_author_controls_acceptance01.json': 'ad89ea1fc30976a985cf796536ae9df3e77eeeaf64dbe54530e81293fd9ab93e',
}
CAL_STATUS = 'INDEPENDENT_FIXED17_DUAL_GRAM_SINGLETON_V1_CALIBRATION_PASS'
FULL_STATUS = 'INDEPENDENT_FIXED17_DUAL_GRAM_SINGLETON_V1_COMPLETE_PASS'
AUTHOR_COUNTS = dict(positive=15, strict_negative=37, total=52,
                     all_expected_actual_match=True, fixture_n=2,
                     complete_fixture_types=4)
OWN_COUNTS = dict(positive=15, strict_negative=63, total=78,
                  all_expected_actual_match=True)
ROWS = [[0, 1, 2], [0, 3, 4], [0, 5, 6], [1, 7, 9], [1, 8, 10],
        [15, 11, 14], [16, 12, 13], [2, 15, 16], [3, 7, 11],
        [4, 8, 12], [5, 9, 13], [6, 10, 14]]


class Veto(ValueError):
    def __init__(self, stage):
        super().__init__(stage)
        self.stage = stage


def need(ok, stage):
    if not ok:
        raise Veto(stage)


def same(x, y):
    if type(x) is not type(y):
        return False
    if type(x) is dict:
        return x.keys() == y.keys() and all(same(x[k], y[k]) for k in y)
    if type(x) is list:
        return len(x) == len(y) and all(same(a, b) for a, b in zip(x, y))
    return x == y


def integer(x, stage):
    need(type(x) is int, stage)
    return x


def fraction(x):
    need(type(x) is str, 'RATIONAL_TYPE')
    try:
        q = Fraction(x)
    except (ValueError, ZeroDivisionError):
        raise Veto('RATIONAL_CANONICAL') from None
    need(str(q) == x, 'RATIONAL_CANONICAL')
    return q


def parse(raw):
    def object_pairs(pairs):
        d = {}
        for k, v in pairs:
            need(k not in d, 'JSON_DUPLICATE')
            d[k] = v
        return d

    def constant(_):
        raise Veto('JSON_CONSTANT')
    try:
        return json.loads(raw, object_pairs_hook=object_pairs, parse_constant=constant)
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise Veto('JSON_SYNTAX') from None


def budget_snapshot(snapshot):
    need(type(snapshot) is dict and snapshot.get('stop_required') is False and
         type(snapshot.get('remaining_seconds')) in (int, float) and
         math.isfinite(snapshot['remaining_seconds']) and
         snapshot['remaining_seconds'] > 20, 'SAVE_RESERVE')


class Budget:
    def __init__(self, seconds):
        self.deadline = CommandDeadline(seconds, allocation_reason=
            'Independent submitted inverse/LDL/472 singleton verification including all I/O')

    def tick(self):
        budget_snapshot(self.deadline.status())


def safe_path(name, existing=True):
    p = Path(name)
    p = p if p.is_absolute() else ROOT / p
    need(p.resolve().is_relative_to(ROOT), 'PATH_SCOPE')
    for part in [p, *p.parents]:
        if part == ROOT.parent:
            break
        if part.exists():
            s = part.lstat()
            need(not part.is_symlink() and not
                 (getattr(s, 'st_file_attributes', 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT),
                 'PATH_REPARSE')
    if existing:
        need(p.is_file(), 'INPUT_FILE')
    return p


class Reader:
    def __init__(self, budget):
        self.budget = budget
        self.pins = {}

    def read(self, name, expected, decode=True):
        self.budget.tick()
        p = safe_path(name)
        need(p.stat().st_size <= 64 * 1024 * 1024, 'INPUT_SIZE')
        chunks, h = [], hashlib.sha256()
        with p.open('rb') as stream:
            while True:
                self.budget.tick()
                data = stream.read(1024 * 1024)
                if not data:
                    break
                h.update(data)
                chunks.append(data)
        digest = h.hexdigest()
        need(type(expected) is str and digest == expected, 'INPUT_HASH')
        key = p.relative_to(ROOT).as_posix()
        need(key not in self.pins or self.pins[key] == digest, 'PIN_CONFLICT')
        self.pins[key] = digest
        self.budget.tick()
        return parse(b''.join(chunks)) if decode else None

    def closing(self):
        for name, digest in list(self.pins.items()):
            self.read(name, digest, False)
        self.budget.tick()


def save(out, name, value, budget):
    budget.tick()
    p = out / name
    with p.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')
    budget.tick()


def adjacency(h, n):
    need(type(h) is list and len(h) == n and all(type(r) is list and len(r) == n for r in h), 'H_SHAPE')
    need(all(type(x) is int for row in h for x in row), 'H_INTEGER')
    need(all(x in (0, 1) for row in h for x in row), 'H_BINARY')
    need(all(h[i][i] == 0 for i in range(n)), 'H_DIAGONAL')
    need(all(h[i][j] == h[j][i] for i in range(n) for j in range(n)), 'H_SYMMETRY')
    return [{j for j in range(n) if h[i][j]} for i in range(n)]


def type_masks(rows, n, count):
    need(type(rows) is list and len(rows) == count, 'TYPE_POPULATION')
    result = []
    for row in rows:
        need(type(row) is dict and set(row) == {'mask', 'coefficient'}, 'TYPE_KEYS')
        m = integer(row['mask'], 'MASK_INTEGER')
        need(0 <= m < 2 ** n, 'MASK_RANGE')
        need(not result or result[-1] < m, 'MASK_ORDER')
        selected = {i for i in range(n) if m & (2 ** i)}
        expected = [1] + [int(i in selected) for i in range(n)] + [
            int(i in selected and j in selected) for i in range(n) for j in range(i + 1, n)]
        c = row['coefficient']
        need(type(c) is list and len(c) == len(expected), 'COEFFICIENT_SHAPE')
        need(all(type(v) is int for v in c), 'COEFFICIENT_INTEGER')
        need(c == expected, 'COEFFICIENT_IDENTITY')
        result.append(m)
    return result


def matrix(raw, n):
    need(type(raw) is list and len(raw) == n and all(type(row) is list and len(row) == n for row in raw), 'MATRIX_SHAPE')
    return [[fraction(x) for x in row] for row in raw]


def scaled_gram(h, name):
    adjacency(h, len(h))
    need(name in ('upper', 'lower'), 'GRAM_NAME')
    scale = 9 if name == 'upper' else 1
    a = [[(27 * int(i == j) - 9 * h[i][j] + 1) if name == 'upper'
          else 4 * int(i == j) + h[i][j] for j in range(len(h))] for i in range(len(h))]
    return a, scale


def inverse_identity(a, scale, inv, budget):
    n = len(a)
    need(len(inv) == n and all(len(r) == n for r in inv), 'MATRIX_SHAPE')
    for i in range(n):
        budget.tick()
        for j in range(n):
            left = sum((a[i][k] * inv[k][j] for k in range(n)), Fraction(0))
            right = sum((inv[i][k] * a[k][j] for k in range(n)), Fraction(0))
            need(left == right == scale * int(i == j), 'INVERSE_IDENTITY')


def ldl_witness(a, scale, low, diagonal, budget):
    n = len(a)
    need(len(diagonal) == n, 'LDL_SHAPE')
    need(all(low[i][j] == int(i == j) for i in range(n) for j in range(i, n)), 'LDL_TRIANGULAR')
    need(all(x > 0 for x in diagonal), 'LDL_POSITIVE')
    for i in range(n):
        budget.tick()
        for j in range(n):
            value = sum((low[i][k] * diagonal[k] * low[j][k] for k in range(n)), Fraction(0))
            need(value * scale == a[i][j], 'LDL_IDENTITY')


def certificate(c, h, name, budget):
    keys = {'schema', 'gram', 'dimension', 'matrix', 'inverse', 'left_product',
            'right_product', 'unit_lower_factor', 'positive_diagonal_pivots',
            'ldl_reconstruction', 'all_left_right_289_entries_exact', 'positive_definite_exact'}
    need(type(c) is dict and set(c) == keys, 'CERTIFICATE_KEYS')
    n = len(h)
    need(c['schema'] == 'EXACT_DUAL_GRAM_INVERSE_LDL_CERTIFICATE_V1' and
         c['gram'] == name and type(c['dimension']) is int and c['dimension'] == n,
         'CERTIFICATE_HEADER')
    need(c['all_left_right_289_entries_exact'] is True and c['positive_definite_exact'] is True, 'CERTIFICATE_FLAGS')
    a, scale = scaled_gram(h, name)
    observed = matrix(c['matrix'], n)
    need(all(observed[i][j] * scale == a[i][j] for i in range(n) for j in range(n)), 'GRAM_MATRIX')
    inv = matrix(c['inverse'], n)
    inverse_identity(a, scale, inv, budget)
    for key in ('left_product', 'right_product'):
        p = matrix(c[key], n)
        need(all(p[i][j] == int(i == j) for i in range(n) for j in range(n)), 'SAVED_PRODUCT')
    low = matrix(c['unit_lower_factor'], n)
    ds = c['positive_diagonal_pivots']
    need(type(ds) is list and len(ds) == n, 'LDL_SHAPE')
    diagonal = [fraction(x) for x in ds]
    ldl_witness(a, scale, low, diagonal, budget)
    rebuilt = matrix(c['ldl_reconstruction'], n)
    need(all(rebuilt[i][j] * scale == a[i][j] for i in range(n) for j in range(n)), 'SAVED_LDL')
    return inv


def equal_type_rules(q, ell, size):
    upper, lower, cn = [], [], []
    for edge in range(2):
        u = Fraction(28, 9) - q
        l = 4 - ell
        if u >= 0 and u * u - (Fraction(1, 9) - edge - q) ** 2 >= 0:
            upper.append(edge)
        if l >= 0 and l * l - (edge - ell) ** 2 >= 0:
            lower.append(edge)
        if size <= 2 - edge:
            cn.append(edge)
    return upper, lower, cn, [a for a in range(2) if a in upper and a in lower and a in cn]


def expected_record(index, mask, ui, li, budget):
    budget.tick()
    n = len(ui)
    selected = {i for i in range(n) if mask & (2 ** i)}
    bits = [int(i in selected) for i in range(n)]
    b = [Fraction(1, 9) - int(i in selected) for i in range(n)]
    ux = [sum((ui[i][j] * b[j] for j in range(n)), Fraction(0)) for i in range(n)]
    lx = [sum((li[i][j] for j in selected), Fraction(0)) for i in range(n)]
    # Full quadratic sums deliberately differ from the producer's vector-dot path.
    q = sum((b[i] * ui[i][j] * b[j] for i in range(n) for j in range(n)), Fraction(0))
    ell = sum((li[i][j] for i in selected for j in selected), Fraction(0))
    rules = equal_type_rules(q, ell, len(selected))
    return dict(index=index, mask=mask, bits=bits, upper_vector=list(map(str, b)),
        upper_inverse_product=list(map(str, ux)), upper_q=str(q),
        upper_margin=str(Fraction(28, 9) - q), upper_pass=q <= Fraction(28, 9),
        lower_inverse_product=list(map(str, lx)), lower_q=str(ell), lower_margin=str(4 - ell),
        lower_pass=ell <= 4, singleton_pass=q <= Fraction(28, 9) and ell <= 4,
        equal_type_distinct_vertices_upper_bits=rules[0], equal_type_distinct_vertices_lower_bits=rules[1],
        equal_type_distinct_vertices_cn_bits=rules[2], equal_type_distinct_vertices_combined_bits=rules[3])


def record(r, index, mask, ui, li, budget):
    expected = expected_record(index, mask, ui, li, budget)
    need(type(r) is dict and set(r) == set(expected), 'RECORD_KEYS')
    for k in ('index', 'mask'):
        integer(r[k], 'RECORD_INTEGER')
    for k in ('upper_pass', 'lower_pass', 'singleton_pass'):
        need(type(r[k]) is bool, 'RECORD_BOOLEAN')
    for k in ('upper_q', 'lower_q', 'upper_margin', 'lower_margin'):
        fraction(r[k])
    for k in ('upper_vector', 'upper_inverse_product', 'lower_inverse_product'):
        need(type(r[k]) is list and len(r[k]) == len(ui), 'RECORD_VECTOR')
        for x in r[k]:
            fraction(x)
    for k in ('bits', 'equal_type_distinct_vertices_upper_bits',
              'equal_type_distinct_vertices_lower_bits', 'equal_type_distinct_vertices_cn_bits',
              'equal_type_distinct_vertices_combined_bits'):
        need(type(r[k]) is list and all(type(x) is int for x in r[k]), 'RECORD_BITS_INTEGER')
    need(same(r, expected), 'RECORD_IDENTITY')
    return expected


def filter_header(g, pins):
    need(type(g) is dict and g.get('status') == 'INDEPENDENT_EXTERNAL_MOMENT_OUTSIDE_CN_FILTER_V1_COMPLETE_PASS'
         and g.get('producer') == '/root/checkpoint_audit' and g.get('verifier') == '/root/native_driver'
         and g.get('method') == 'independent_artifact_check' and type(g.get('implementation_version')) is int
         and g['implementation_version'] == 1 and g.get('target_resolution') == 'NONE', 'FILTER_HEADER')
    need(type(g.get('inputs_sha256')) is dict and all(g['inputs_sha256'].get(p) == h for p, h in pins.items()), 'FILTER_DIRECT_PINS')


def author_header(s):
    need(type(s) is dict and s.get('status') == 'FIXED17_DUAL_GRAM_SINGLETON_V1_AUTHOR_CONTROLS_PASS'
         and type(s.get('implementation_version')) is int and s['implementation_version'] == 1
         and s.get('actual_target_input_read') is False and s.get('producer') == '/root/structural'
         and s.get('independent_approval') is False and s.get('target_resolution') == 'NONE'
         and same(s.get('controls'), AUTHOR_COUNTS), 'AUTHOR_HEADER')
    need(same(s.get('source_software'), {PRODUCER: PRODUCER_PINS[PRODUCER], PRODUCER_SPEC: PRODUCER_PINS[PRODUCER_SPEC]}), 'AUTHOR_SOURCE')


def runtime(plan, manifest, terminal, summary):
    need(type(plan) is dict and type(manifest) is dict and type(terminal) is dict, 'RUNTIME_SCHEMA')
    worker, child, command = plan.get('worker_argv'), plan.get('child_argv'), plan.get('command')
    need(type(worker) is list and len(worker) >= 3 and type(child) is list and
         len(child) >= len(worker) and type(command) is list and len(command) >= len(child) and
         all(type(x) is str for x in worker + child + command), 'RUNTIME_VECTOR')
    need(same(command, plan.get('supervisor_argv')) and same(command[-len(child):], child)
         and same(child[-len(worker):], worker)
         and worker[1] == '-B' and same(summary.get('command'), worker[2:])
         and same(manifest.get('command'), child), 'RUNTIME_COMMAND')
    need(manifest.get('source_sha256') == SOFTWARE['acceleration/run_compute_command_v2.py']
         and manifest.get('runtime_scope') == 'LOCAL_WINDOWS_SUSPENDED_JOB_V1'
         and type(manifest.get('seconds')) in (int, float) and manifest['seconds'] == 180
         and type(manifest.get('shutdown_reserve_seconds')) in (int, float)
         and manifest['shutdown_reserve_seconds'] == 20,
         'RUNTIME_ALLOCATION')
    need(manifest.get('invocation_id') == terminal.get('invocation_id')
         and type(terminal.get('command_exit_code')) is int and terminal['command_exit_code'] == 0
         and terminal.get('error') is None, 'RUNTIME_EXIT')
    cleanup = terminal.get('cleanup')
    need(type(cleanup) is dict and type(cleanup.get('actual_exit_code')) is int
         and cleanup['actual_exit_code'] == 0 and cleanup.get('reaped') is True
         and cleanup.get('job_active_zero_observed') is True and same(cleanup.get('cleanup_errors'), []), 'RUNTIME_CLEANUP')


def checkpoint(c, records, end, pins):
    need(type(c) is dict and set(c) == {'schema', 'next_index', 'records', 'inputs_sha256'}
         and c['schema'] == 'DUAL_GRAM_SINGLETON_PREFIX_V1'
         and type(c['next_index']) is int and c['next_index'] == end, 'CHECKPOINT_HEADER')
    width = 24 if end == 472 else 32
    need(same(c['records'], records[end - width:end]), 'CHECKPOINT_RECORDS')
    need(same(c['inputs_sha256'], pins), 'CHECKPOINT_PINS')


def population(reader, root, summary, names):
    p = safe_path(root, False)
    need(p.is_dir(), 'OUTPUT_DIRECTORY')
    children = list(p.iterdir())
    need({x.name for x in children} == set(names) | {'summary.json'} and
         all(x.is_file() and not x.is_symlink() for x in children), 'RAW_POPULATION')
    pins = summary.get('outputs_sha256')
    need(type(pins) is dict and set(pins) == set(names), 'RAW_OUTPUT_MAP')
    result = {}
    for name in sorted(names):
        need('/' not in name and '\\' not in name, 'RAW_NAME')
        result[name] = reader.read(p / name, pins[name])
    return result


def own_header(c, source_pins):
    need(type(c) is dict and c.get('status') == CAL_STATUS and
         type(c.get('implementation_version')) is int and c['implementation_version'] == 1
         and c.get('producer') == '/root/structural' and c.get('verifier') == '/root/checkpoint_audit'
         and c.get('method') == 'independent_artifact_check' and c.get('target_resolution') == 'NONE'
         and c.get('actual_target_input_read') is False and same(c.get('controls'), OWN_COUNTS)
         and same(c.get('source_software'), source_pins), 'OWN_CALIBRATION')


def full(reader, args, out, source_pins):
    own = reader.read(args.calibration, args.calibration_sha256)
    own_header(own, source_pins)
    own_files = population(reader, Path(args.calibration).parent, own, own['outputs_sha256'].keys())
    own_rows = own_files.get('controls.json')
    need(type(own_rows) is list and len(own_rows) == OWN_COUNTS['total'] and
         all(r.get('expected_stage') == r.get('actual_stage') for r in own_rows), 'OWN_CONTROL_ROWS')
    for p, digest in {**PRODUCER_PINS, **MODEL_PINS}.items():
        reader.read(p, digest, p.endswith('.json'))
    summary = reader.read(RAW + '/summary.json', PRODUCER_PINS[RAW + '/summary.json'])
    author = reader.read(AUTHOR + '/summary.json', PRODUCER_PINS[AUTHOR + '/summary.json'])
    author_header(author)
    author_names = set(author.get('outputs_sha256', {}))
    need(len(author_names) == 53, 'AUTHOR_POPULATION')
    author_files = population(reader, AUTHOR, author, author_names)
    table = author_files['controls.json']
    need(type(table) is list and len(table) == 52 and
         all(type(r) is dict and r.get('expected_stage') == r.get('actual_stage') for r in table)
         and len({r['case'] for r in table}) == 52 and
         sum(r['expected_stage'] == 'PASS' for r in table) == 15, 'AUTHOR_STAGE_TABLE')
    need(set(author_names) == {'controls.json'} | {r['case'] + '.json' for r in table}, 'AUTHOR_PAYLOAD_NAMES')
    runtime(reader.read(PLAN, PRODUCER_PINS[PLAN]),
            reader.read(SUP + '/manifest.json', PRODUCER_PINS[SUP + '/manifest.json']),
            reader.read(SUP + '/summary.json', PRODUCER_PINS[SUP + '/summary.json']), summary)
    need(summary.get('status') == 'CANDIDATE_FIXED17_DUAL_GRAM_SINGLETON_V1_COMPLETE'
         and type(summary.get('implementation_version')) is int and summary['implementation_version'] == 1
         and summary.get('producer') == '/root/structural' and summary.get('independent_approval') is False
         and summary.get('target_resolution') == 'NONE' and summary.get('actual_target_input_read') is True
         and summary.get('fixed_induced17_only') is True and summary.get('controls') is None
         and same(summary.get('source_software'), author['source_software'])
         and same(summary.get('inputs_sha256'), MODEL_PINS), 'PRODUCER_HEADER')
    filter_header(reader.read(FILTER, MODEL_PINS[FILTER]), {MODEL: MODEL_PINS[MODEL], TYPES: MODEL_PINS[TYPES]})
    model = reader.read(MODEL, MODEL_PINS[MODEL])
    need(model.get('schema') == 'OUTSIDE_VERTEX_CN_FILTERED_MOMENT_SYSTEM_V1' and
         all(type(model.get(k)) is int and model[k] == v for k, v in
             [('target_order', 99), ('target_degree', 14), ('adjacent_cn', 1),
              ('nonadjacent_cn', 2), ('eligible_type_count', 472)]), 'MODEL_HEADER')
    need(same(model.get('ordered_support_vertices'), list(range(17))), 'SUPPORT_ORDER')
    labels = [{'kind': 'total'}] + [{'kind': 'vertex', 'vertex': i} for i in range(17)] + [
        {'kind': 'pair', 'vertices': [i, j]} for i in range(17) for j in range(i + 1, 17)]
    need(same(model.get('row_labels'), labels), 'ROW_LABELS')
    h = model.get('induced_adjacency')
    neighbors = adjacency(h, 17)
    literal_neighbors = [set() for _ in range(17)]
    for row in ROWS:
        for v in row:
            literal_neighbors[v].update(set(row) - {v})
    need(neighbors == literal_neighbors, 'LITERAL_ALL289')
    masks = type_masks(reader.read(TYPES, MODEL_PINS[TYPES]), 17, 472)
    names = {'parsed_input.json', 'singletons.json', 'upper_inverse_certificate.json', 'lower_inverse_certificate.json'} | {
        'checkpoint_%03d.json' % end for end in [*range(32, 449, 32), 472]}
    payload = population(reader, RAW, summary, names)
    base = dict(literal_twelve_rows=ROWS, positive_row_order=ROWS[8:], centers=[0, 1],
        common_center_neighbor=2, bridge_endpoints=[15, 16], free_sides=[[11, 14], [12, 13]],
        PA=[[0, 1], [2, 3]], PB=[[0, 2], [1, 3]], PR=[[0, 3], [1, 2]],
        partition_pattern='all three distinct: class IV', all289_literal_edge_union_entries_compared=True,
        enumeration_PID_not_used=True)
    need(same(payload['parsed_input.json'], dict(schema='FIXED17_DUAL_GRAM_PARSED_INPUT_V1',
         support_vertices=list(range(17)), induced_adjacency=h, ordered_masks=masks,
         exact_class_IV_identity=base, authenticated_eligible_universe_only=True,
         complete_all17bit_masks_reenumerated=False)), 'PARSED_INPUT')
    ui = certificate(payload['upper_inverse_certificate.json'], h, 'upper', reader.budget)
    li = certificate(payload['lower_inverse_certificate.json'], h, 'lower', reader.budget)
    records = payload['singletons.json']
    need(type(records) is list and len(records) == 472, 'RECORD_POPULATION')
    observations = []
    for i, mask in enumerate(masks):
        r = record(records[i], i, mask, ui, li, reader.budget)
        observations.append(dict(index=i, mask=mask, upper_q=r['upper_q'], lower_q=r['lower_q'],
            upper_pass=r['upper_pass'], lower_pass=r['lower_pass'], singleton_pass=r['singleton_pass'],
            equal_type_distinct_vertices_combined_bits=r['equal_type_distinct_vertices_combined_bits']))
    for end in [*range(32, 449, 32), 472]:
        checkpoint(payload['checkpoint_%03d.json' % end], records, end, MODEL_PINS)
    outcome = dict(complete_type_records=472, upper_pass=sum(r['upper_pass'] for r in records),
        lower_pass=sum(r['lower_pass'] for r in records), combined_pass=sum(r['singleton_pass'] for r in records),
        eliminated_by_upper=[r['index'] for r in records if not r['upper_pass']],
        eliminated_by_lower=[r['index'] for r in records if not r['lower_pass']],
        pairs_enumerated=0, future_unordered_pairs_including_equal_types=111628)
    need(same(summary.get('outcome'), outcome), 'PRODUCER_OUTCOME')
    save(out, 'singleton_observations.json', observations, reader.budget)
    return dict(outcome=outcome, inverse_matrices=2, dimension=17,
        left_inverse_entries_per_matrix=289, right_inverse_entries_per_matrix=289,
        LDL_reconstruction_entries_per_matrix=289, strictly_positive_pivots_per_matrix=17,
        checkpoint_records_compared=472, checkpoint_files=15, producer_raw_files=20,
        author_control_payloads_byte_authenticated=52, author_stage_table_metadata_matched=52,
        author_control_arithmetic_replayed=False, inverse_generated=False, LDL_generated=False,
        fixed_induced17_only=True, complete_all17bit_masks_reenumerated=False)


def hand_certificate(n, name):
    # Analytic empty-graph fixtures, not an inverse/factor algorithm on an input matrix.
    h = [[0] * n for _ in range(n)]
    a, scale = scaled_gram(h, name)
    inv = [[Fraction(int(i == j), 3) - Fraction(1, 3 * (27 + n)) if name == 'upper'
            else Fraction(int(i == j), 4) for j in range(n)] for i in range(n)]
    low = [[Fraction(int(i == j)) if i <= j or name == 'lower' else Fraction(1, 28 + j)
            for j in range(n)] for i in range(n)]
    ds = [Fraction(3 * (28 + j), 27 + j) if name == 'upper' else Fraction(4) for j in range(n)]
    serial = lambda rows: [[str(x) for x in r] for r in rows]
    gram = [[Fraction(x, scale) for x in r] for r in a]
    identity = [[str(int(i == j)) for j in range(n)] for i in range(n)]
    return dict(schema='EXACT_DUAL_GRAM_INVERSE_LDL_CERTIFICATE_V1', gram=name, dimension=n,
        matrix=serial(gram), inverse=serial(inv), left_product=copy.deepcopy(identity),
        right_product=copy.deepcopy(identity), unit_lower_factor=serial(low),
        positive_diagonal_pivots=list(map(str, ds)), ldl_reconstruction=serial(gram),
        all_left_right_289_entries_exact=True, positive_definite_exact=True)


def calibration(out, budget):
    rows = []

    def case(label, expected, payload, action):
        save(out, label + '.json', payload, budget)
        try:
            action(payload)
            actual = 'PASS'
        except Veto as exc:
            actual = exc.stage
        rows.append(dict(case=label, expected_stage=expected, actual_stage=actual))
        need(actual == expected, 'OWN_STAGE_MISMATCH')

    h = [[0, 0], [0, 0]]
    uc, lc = hand_certificate(2, 'upper'), hand_certificate(2, 'lower')
    ui, li = matrix(uc['inverse'], 2), matrix(lc['inverse'], 2)
    hand = dict(index=1, mask=1, bits=[1, 0], upper_vector=['-8/9', '1/9'],
        upper_inverse_product=['-25/87', '4/87'], upper_q='68/261', upper_margin='248/87',
        upper_pass=True, lower_inverse_product=['1/4', '0'], lower_q='1/4', lower_margin='15/4',
        lower_pass=True, singleton_pass=True, equal_type_distinct_vertices_upper_bits=[0, 1],
        equal_type_distinct_vertices_lower_bits=[0, 1], equal_type_distinct_vertices_cn_bits=[0, 1],
        equal_type_distinct_vertices_combined_bits=[0, 1])
    types = [{'mask': m, 'coefficient': [1, m & 1, (m >> 1) & 1, int(m == 3)]} for m in range(4)]
    fake = dict(status='INDEPENDENT_EXTERNAL_MOMENT_OUTSIDE_CN_FILTER_V1_COMPLETE_PASS',
        producer='/root/checkpoint_audit', verifier='/root/native_driver', method='independent_artifact_check',
        implementation_version=1, target_resolution='NONE', inputs_sha256={'m': 'a', 't': 'b'})
    worker = ['python', '-B', 'source', 'singletons']
    child = ['uv', 'run', '--locked', '--offline'] + worker
    plan = dict(command=['supervisor', '--'] + child, supervisor_argv=['supervisor', '--'] + child,
                child_argv=child, worker_argv=worker)
    manifest = dict(command=child, source_sha256=SOFTWARE['acceleration/run_compute_command_v2.py'],
        runtime_scope='LOCAL_WINDOWS_SUSPENDED_JOB_V1', seconds=180.0, shutdown_reserve_seconds=20.0, invocation_id='x')
    terminal = dict(invocation_id='x', command_exit_code=0, error=None, cleanup=dict(actual_exit_code=0,
        reaped=True, job_active_zero_observed=True, cleanup_errors=[]))
    fixture_runtime = dict(plan=plan, manifest=manifest, terminal=terminal, summary={'command': worker[2:]})
    runtime_action = lambda p: runtime(p['plan'], p['manifest'], p['terminal'], p['summary'])
    cp = dict(schema='DUAL_GRAM_SINGLETON_PREFIX_V1', next_index=32,
              records=[copy.deepcopy(hand) for _ in range(32)], inputs_sha256={'m': 'a'})
    cp_action = lambda p: checkpoint(p, [hand] * 32, 32, {'m': 'a'})
    case('upper_certificate2', 'PASS', uc, lambda p: certificate(p, h, 'upper', budget))
    case('lower_certificate2', 'PASS', lc, lambda p: certificate(p, h, 'lower', budget))
    uc17 = hand_certificate(17, 'upper'); li17 = matrix(hand_certificate(17, 'lower')['inverse'], 17)
    case('upper_certificate17_last_entries', 'PASS', uc17, lambda p: certificate(p, [[0] * 17 for _ in range(17)], 'upper', budget))
    case('all_four_types2', 'PASS', types, lambda p: type_masks(p, 2, 4))
    case('hand_record2', 'PASS', hand, lambda p: record(p, 1, 1, ui, li, budget))
    hand17 = dict(index=0, mask=65536, bits=[0] * 16 + [1], upper_vector=['1/9'] * 16 + ['-8/9'],
        upper_inverse_product=['1/33'] * 16 + ['-10/33'], upper_q='32/99', upper_margin='92/33',
        upper_pass=True, lower_inverse_product=['0'] * 16 + ['1/4'], lower_q='1/4', lower_margin='15/4',
        lower_pass=True, singleton_pass=True, equal_type_distinct_vertices_upper_bits=[0, 1],
        equal_type_distinct_vertices_lower_bits=[0, 1], equal_type_distinct_vertices_cn_bits=[0, 1],
        equal_type_distinct_vertices_combined_bits=[0, 1])
    case('hand_last_coordinate17', 'PASS', hand17, lambda p: record(p, 0, 65536, matrix(uc17['inverse'], 17), li17, budget))
    case('filter_header', 'PASS', fake, lambda p: filter_header(p, {'m': 'a', 't': 'b'}))
    case('contained_runtime', 'PASS', fixture_runtime, runtime_action)
    case('complete_checkpoint', 'PASS', cp, cp_action)
    case('binary_adjacency', 'PASS', h, lambda p: adjacency(p, 2))
    fake_own = dict(status=CAL_STATUS, implementation_version=1, producer='/root/structural',
        verifier='/root/checkpoint_audit', method='independent_artifact_check', target_resolution='NONE',
        actual_target_input_read=False, controls=copy.deepcopy(OWN_COUNTS), source_software={'fixture': 'hash'})
    case('own_header', 'PASS', fake_own, lambda p: own_header(p, {'fixture': 'hash'}))
    for label, q, ell, bit, channel in [('upper_nonadj_equal', '29/18', '0', 0, 0),
        ('upper_adj_equal', '10/9', '0', 1, 0), ('lower_nonadj_equal', '0', '2', 0, 1),
        ('lower_adj_equal', '0', '5/2', 1, 1)]:
        case(label, 'PASS', dict(q=q, ell=ell, bit=bit, channel=channel),
             lambda p: need(p['bit'] in equal_type_rules(fraction(p['q']), fraction(p['ell']), 0)[p['channel']], 'THRESHOLD'))
    # Each precise rejection changes one authenticated field of a passing fixture.
    for label, value, stage in [('h_bool', [[False, 0], [0, 0]], 'H_INTEGER'),
        ('h_float', [[0.0, 0], [0, 0]], 'H_INTEGER'), ('h_shape', [[0]], 'H_SHAPE'),
        ('h_diagonal', [[1, 0], [0, 0]], 'H_DIAGONAL'), ('h_asym', [[0, 1], [0, 0]], 'H_SYMMETRY'),
        ('h_binary', [[0, 2], [2, 0]], 'H_BINARY')]:
        case(label, stage, value, lambda p: adjacency(p, 2))
    for label, key, value, stage in [('mask_bool', 'mask', False, 'MASK_INTEGER'),
        ('mask_float', 'mask', 0.0, 'MASK_INTEGER'), ('mask_negative', 'mask', -1, 'MASK_RANGE'),
        ('mask_high', 'mask', 4, 'MASK_RANGE'), ('coefficient_bool', 'coefficient', [True, 0, 0, 0], 'COEFFICIENT_INTEGER'),
        ('coefficient_float', 'coefficient', [1.0, 0, 0, 0], 'COEFFICIENT_INTEGER'),
        ('coefficient_short', 'coefficient', [1], 'COEFFICIENT_SHAPE'),
        ('coefficient_wrong', 'coefficient', [0, 0, 0, 0], 'COEFFICIENT_IDENTITY')]:
        damaged = copy.deepcopy(types); damaged[0][key] = value
        case(label, stage, damaged, lambda p: type_masks(p, 2, 4))
    for label, value, stage in [('mask_order', list(reversed(types)), 'MASK_ORDER'),
        ('type_count', types[:3], 'TYPE_POPULATION'), ('type_keys', [dict(types[0], extra=1)] + types[1:], 'TYPE_KEYS')]:
        case(label, stage, value, lambda p: type_masks(p, 2, 4))
    for label, value, stage in [('rational_bool', False, 'RATIONAL_TYPE'),
        ('rational_float', 0.0, 'RATIONAL_TYPE'), ('rational_alias', '2/2', 'RATIONAL_CANONICAL')]:
        case(label, stage, value, fraction)
    for label, key, value, stage in [('certificate_bool_dimension', 'dimension', True, 'CERTIFICATE_HEADER'),
        ('certificate_flag_alias', 'positive_definite_exact', 1, 'CERTIFICATE_FLAGS'),
        ('matrix_last_wrong', 'matrix', [['28/9', '1/9'], ['1/9', '0']], 'GRAM_MATRIX'),
        ('inverse_last_wrong', 'inverse', [['28/87', '-1/87'], ['-1/87', '0']], 'INVERSE_IDENTITY'),
        ('saved_left_wrong', 'left_product', [['1', '0'], ['0', '0']], 'SAVED_PRODUCT'),
        ('saved_right_bool', 'right_product', [['1', '0'], ['0', True]], 'RATIONAL_TYPE'),
        ('ldl_upper_nonzero', 'unit_lower_factor', [['1', '1'], ['1/28', '1']], 'LDL_TRIANGULAR'),
        ('ldl_zero_pivot', 'positive_diagonal_pivots', ['28/9', '0'], 'LDL_POSITIVE'),
        ('ldl_negative_pivot', 'positive_diagonal_pivots', ['28/9', '-1'], 'LDL_POSITIVE'),
        ('ldl_factor_wrong', 'unit_lower_factor', [['1', '0'], ['0', '1']], 'LDL_IDENTITY'),
        ('saved_ldl_wrong', 'ldl_reconstruction', [['28/9', '1/9'], ['1/9', '0']], 'SAVED_LDL')]:
        damaged = copy.deepcopy(uc); damaged[key] = value
        case(label, stage, damaged, lambda p: certificate(p, h, 'upper', budget))
    for label, key, value, stage in [('record_bool_index', 'index', True, 'RECORD_INTEGER'),
        ('record_float_mask', 'mask', 1.0, 'RECORD_INTEGER'), ('record_flag_alias', 'upper_pass', 1, 'RECORD_BOOLEAN'),
        ('record_bits_bool', 'bits', [True, 0], 'RECORD_BITS_INTEGER'),
        ('record_vector_alias', 'upper_vector', ['-16/18', '1/9'], 'RATIONAL_CANONICAL'),
        ('record_vector_last', 'upper_inverse_product', ['-25/87', '0'], 'RECORD_IDENTITY'),
        ('record_q_wrong', 'upper_q', '0', 'RECORD_IDENTITY'),
        ('record_margin_wrong', 'lower_margin', '0', 'RECORD_IDENTITY'),
        ('record_rule_wrong', 'equal_type_distinct_vertices_combined_bits', [0], 'RECORD_IDENTITY')]:
        damaged = copy.deepcopy(hand); damaged[key] = value
        case(label, stage, damaged, lambda p: record(p, 1, 1, ui, li, budget))
    for label, key, value, stage in [('gate_status', 'status', 'CANDIDATE', 'FILTER_HEADER'),
        ('gate_method_key', 'method', None, 'FILTER_HEADER'), ('gate_bool_version', 'implementation_version', True, 'FILTER_HEADER'),
        ('gate_verifier', 'verifier', '/root/structural', 'FILTER_HEADER'),
        ('gate_direct_pin', 'inputs_sha256', {'m': 'x', 't': 'b'}, 'FILTER_DIRECT_PINS')]:
        damaged = copy.deepcopy(fake); damaged[key] = value
        case(label, stage, damaged, lambda p: filter_header(p, {'m': 'a', 't': 'b'}))
    for label, section, key, value, stage in [('runtime_command', 'manifest', 'command', [], 'RUNTIME_COMMAND'),
        ('runtime_outer_bool', 'manifest', 'seconds', True, 'RUNTIME_ALLOCATION'),
        ('runtime_exit_bool', 'terminal', 'command_exit_code', False, 'RUNTIME_EXIT'),
        ('runtime_cleanup_bool', 'cleanup', 'actual_exit_code', False, 'RUNTIME_CLEANUP'),
        ('runtime_reaped_alias', 'cleanup', 'reaped', 1, 'RUNTIME_CLEANUP'),
        ('runtime_live_job', 'cleanup', 'job_active_zero_observed', False, 'RUNTIME_CLEANUP')]:
        damaged = copy.deepcopy(fixture_runtime)
        (damaged['terminal']['cleanup'] if section == 'cleanup' else damaged[section])[key] = value
        case(label, stage, damaged, runtime_action)
    for label, key, value, stage in [('checkpoint_bool', 'next_index', True, 'CHECKPOINT_HEADER'),
        ('checkpoint_count', 'records', cp['records'][:-1], 'CHECKPOINT_RECORDS'),
        ('checkpoint_suffix_wrong', 'records', cp['records'][:-1] + [dict(hand, mask=0)], 'CHECKPOINT_RECORDS'),
        ('checkpoint_pin', 'inputs_sha256', {'m': 'b'}, 'CHECKPOINT_PINS')]:
        damaged = copy.deepcopy(cp); damaged[key] = value
        case(label, stage, damaged, cp_action)
    for label, remaining, stop in [('reserve_equal', 20, False), ('reserve_below', 19, False),
                                   ('reserve_stop', 100, True), ('reserve_bool', True, False)]:
        case(label, 'SAVE_RESERVE', dict(remaining_seconds=remaining, stop_required=stop), budget_snapshot)
    case('json_duplicate', 'JSON_DUPLICATE', '{"x":1,"x":2}', parse)
    case('json_nonfinite', 'JSON_CONSTANT', '{"x":NaN}', parse)
    for label, key, value in [('own_float_count', 'positive', 15.0), ('own_integer_match_flag', 'all_expected_actual_match', 1)]:
        damaged = copy.deepcopy(fake_own); damaged['controls'][key] = value
        case(label, 'OWN_CALIBRATION', damaged, lambda p: own_header(p, {'fixture': 'hash'}))
    need(len(rows) == OWN_COUNTS['total'] and sum(r['expected_stage'] == 'PASS' for r in rows) == OWN_COUNTS['positive'], 'OWN_CONTROL_POPULATION')
    save(out, 'controls.json', rows, budget)
    return copy.deepcopy(OWN_COUNTS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('mode', choices=['calibrate', 'full'])
    ap.add_argument('--seconds', required=True, type=float)
    ap.add_argument('--out', required=True)
    ap.add_argument('--self-sha256', required=True)
    ap.add_argument('--spec-sha256', required=True)
    ap.add_argument('--calibration')
    ap.add_argument('--calibration-sha256')
    args = ap.parse_args()
    budget = Budget(args.seconds)
    reader = Reader(budget)
    out = safe_path(args.out, False)
    need(out.is_relative_to(ROOT / 'acceleration/results/20261004_independent_review'), 'OUTPUT_SCOPE')
    need(not out.exists(), 'OUTPUT_EXISTS')
    out.mkdir(parents=True)
    source_pins = {**SOFTWARE, SELF: args.self_sha256, SPEC: args.spec_sha256}
    try:
        for p, h in source_pins.items():
            reader.read(p, h, False)
        if args.mode == 'calibrate':
            result = calibration(out, budget)
            status = CAL_STATUS
        else:
            need(args.calibration is not None and args.calibration_sha256 is not None, 'OWN_CALIBRATION_REQUIRED')
            result = full(reader, args, out, source_pins)
            status = FULL_STATUS
        reader.closing()
        outputs = {}
        for p in sorted(out.iterdir()):
            budget.tick()
            need(p.is_file() and not p.is_symlink(), 'CHECKER_OUTPUT_TREE')
            outputs[p.name] = hashlib.sha256(p.read_bytes()).hexdigest()
            budget.tick()
        report = dict(status=status, implementation_version=1,
            timestamp=datetime.now(timezone.utc).isoformat(), producer='/root/structural',
            verifier='/root/checkpoint_audit', method='independent_artifact_check', target_resolution='NONE',
            checker_author='/root/checkpoint_audit', source_software=source_pins,
            actual_target_input_read=args.mode == 'full', controls=result if args.mode == 'calibrate' else OWN_COUNTS,
            checked_scope=result if args.mode == 'full' else {'synthetic_only': True},
            outcome=result['outcome'] if args.mode == 'full' else None,
            inputs_sha256=reader.pins, outputs_sha256=outputs, command=sys.argv,
            LP_calls=0, RREF_calls=0, inverse_generation_calls=0, LDL_factor_generation_calls=0,
            complete_ancestor_evidence_closure_rehashed=False,
            shared_components=['Python Fraction/json/hashlib, canonical producer field names, command_deadline and Windows Job supervisor',
                'Known analytic empty-graph fixtures also used by producer; submitted-target algorithms are separate'],
            limitations='Fixed literal induced17/ordered472 only. Equal-type rules refer to distinct exterior vertices. No unequal-type pairs, integer/graph completion, induced-family enumeration or target conclusion.',
            deadline=budget.deadline.status(), automatic_retry=False, ledger_index_mutations=0)
        save(out, 'summary.json', report, budget)
        budget.tick()
        return 0
    except BaseException as exc:
        try:
            with (out / 'failure.json').open('x', encoding='utf8') as stream:
                json.dump(dict(status='FAILED_OR_NOT_COMPLETED_WITH_ALLOCATED_BUDGET',
                    stage=getattr(exc, 'stage', type(exc).__name__), reason=str(exc),
                    deadline=budget.deadline.status(), target_resolution='NONE',
                    pending_suffix_saved=False, provisional_summary_is_not_a_gate=True,
                    automatic_retry=False), stream, indent=2)
        except OSError:
            pass
        raise


if __name__ == '__main__':
    raise SystemExit(main())
