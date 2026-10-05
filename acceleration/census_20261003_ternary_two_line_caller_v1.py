"""SOURCE ONLY: graph-only warm-input adapter and one exact F3/E neighborhood.

Every line is mutable. No native state, RNG, trajectory or root normalization is
created. Fresh decoder/caller/objective gates precede any target computation.
"""
import argparse
import copy
import hashlib
import importlib.metadata
import importlib.util
import platform
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SELF = 'acceleration/census_20261003_ternary_two_line_caller_v1.py'
SPEC = 'acceleration/census_20261003_ternary_two_line_caller_v1_spec.md'
KERNEL = 'acceleration/census_20261003_ternary_two_line_v1.py'
KERNEL_SHA = '54d6160e61b1de83f3aa4ce9ec1b92517c542d5da73a9b54a3fbc466557a2b73'
KERNEL_SPEC = 'acceleration/census_20261003_ternary_two_line_v1_spec.md'
KERNEL_SPEC_SHA = 'c437f688324bfa9ea19587e2d51e2eae6423462284295ff01cfac04638046e2d'
STATE = 'acceleration/results/20261003_hypergraph_weight60_warm01/native/final.state'
STATE_SHA = 'c15b421468af173b6c2ee11e9bcb31d5abca586fcb47a7c7ee312f527b31979b'
MATRIX = 'acceleration/results/20261003_hypergraph_weight60_warm01/native/best.adj'
MATRIX_SHA = '9d5b88ba2a2eb13d39d2a5edea1c25af9a9105c143c4297fe37e84f666a37a2d'
AUDIT = 'acceleration/results/20261003_independent_review/weight60_warm01/summary.json'
AUDIT_SHA = '256c8277ab5c69e74f4c9725c4b42e96e31b4e546c490b8e231df4ed6831bf6c'
WARM_SOURCE = 'acceleration/results/20261003_hypergraph_weight60_warm01/summary.json'
WARM_SOURCE_SHA = 'da370b4898dcd7288e42787684d12b7945933516234c2965155ed312722d4baf'
INPUT_SCHEMA = 'TERNARY_ALL_LINE_GRAPH_ONLY_INPUT_V1'
KERNEL_PASS = 'INDEPENDENT_TERNARY_TWO_LINE_KERNEL_V1_COMPLETE_CONTROLS_PASS'
CALLER_PASS = 'INDEPENDENT_TERNARY_TWO_LINE_CALLER_V1_COMPLETE_CONTROLS_PASS'
INPUT_PASS = 'INDEPENDENT_TERNARY_ALL_LINE_GRAPH_ONLY_INPUT_V1_COMPLETE_PASS'
VERIFIER = '/root/structural'


class CheckError(ValueError):
    def __init__(self, stage, message):
        self.stage = stage
        super().__init__(stage + ': ' + message)


def need(ok, stage, message):
    if not ok:
        raise CheckError(stage, message)


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def lib():
    for path, identity in [(KERNEL, KERNEL_SHA), (KERNEL_SPEC, KERNEL_SPEC_SHA)]:
        need(sha(ROOT / path) == identity, 'SOURCE', 'unchanged objective component:' + path)
    spec = importlib.util.spec_from_file_location('unchanged_ternary_two_line_kernel', ROOT / KERNEL)
    kernel = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kernel)
    structure, io, reference, pins = kernel.lib()
    return kernel, structure, io, reference, pins


def wire_lines(raw, stage):
    need(type(raw) is bytes and len(raw) <= 131072, stage, 'bounded literal wire bytes')
    try:
        text = raw.decode('ascii')
    except UnicodeError as error:
        raise CheckError(stage, 'ASCII wire bytes') from error
    need(text.endswith('\n') and '\r' not in text and '\x00' not in text, stage, 'literal LF-terminated ASCII')
    return text[:-1].split('\n')


def state_graph(raw, kernel, structure):
    # Extract ONLY the ordered best object. All other saved state/history fields
    # are opaque archived provenance; their old independent audit is preserved.
    rows = wire_lines(raw, 'STATE_WIRE')
    need(rows and rows[0] == 'HYPERGRAPH_WEIGHT60_ANNEAL_STATE_V2'
         and rows[-1] == 'END', 'STATE_SCHEMA', 'exact archived state family/end')
    selected = {}
    for name in ['n', 'degree', 'best']:
        hits = [row for row in rows if row.startswith(name + ' ')]
        need(len(hits) == 1 and re.fullmatch(name + r' (0|[1-9][0-9]*)', hits[0]) is not None,
             'STATE_HEADERS', 'one canonical integer header:' + name)
        selected[name] = int(hits[0].split(' ')[1])
    n, degree, count = selected['n'], selected['degree'], selected['best']
    need(3 <= n <= 99 and 0 < 2 * degree < n and 3 * count == n * degree,
         'STATE_DIMENSIONS', 'finite complete regular triple object')
    at = rows.index('best ' + str(count)) + 1
    need(at + count < len(rows), 'STATE_TRIPLES', 'complete labelled best section')
    triples = []
    for row in rows[at:at + count]:
        need(re.fullmatch(r'(0|[1-9][0-9]*) (0|[1-9][0-9]*) (0|[1-9][0-9]*)', row) is not None,
             'STATE_TRIPLES', 'canonical three literal integer labels')
        triples.append([int(value) for value in row.split(' ')])
    need(not re.fullmatch(r'[0-9]+ [0-9]+ [0-9]+', rows[at + count]),
         'STATE_TRIPLES', 'best section ends after declared population')
    return kernel.domain(structure, n, degree, triples)


def matrix_graph(raw, base, structure):
    rows = wire_lines(raw, 'MATRIX_WIRE')
    n = base['n']
    need(len(rows) == n + 1 and rows[0] == str(n)
         and all(len(row) == n and set(row) <= {'0', '1'} for row in rows[1:]),
         'MATRIX_SHAPE', 'complete canonical binary adjacency wire')
    need(raw == structure.adjacency_bytes(base['masks']), 'MATRIX_IDENTITY',
         'every raw row equals the complete graph rebuilt from ordered best triples')


def review_warm_audit(audit, base, io):
    need(type(audit) is dict and audit.get('status') == 'INDEPENDENT_HYPERGRAPH_WEIGHT60_SAVED_OBJECTS_V2_PASS'
         and audit.get('producer') == '/root/native_driver' and audit.get('verifier') == '/root/structural'
         and audit.get('target_resolution') is False and type(audit.get('inputs_sha256')) is dict,
         'WARM_AUDIT', 'literal original independent report interface, no status/method rewrite')
    for key, value in [('saved_state_files', 103), ('complete_integer_saved_current_best_objects', 206)]:
        need(type(audit.get(key)) is int and audit[key] == value, 'WARM_AUDIT', 'exact archived saved-object population')
    pins = {STATE: STATE_SHA, MATRIX: MATRIX_SHA, WARM_SOURCE: WARM_SOURCE_SHA}
    need(all(audit['inputs_sha256'].get(path) == identity for path, identity in pins.items()),
         'WARM_AUDIT', 'original exact raw state/matrix/source identities')
    diag = audit.get('final_best_diagnostics')
    need(type(diag) is dict and diag.get('domain_valid') is True and diag.get('srg_valid') is False
         and all(type(diag.get(k)) is int and diag[k] == v for k, v in
                 dict(ordered_entries_checked=9801, lambda_energy=0, mu_energy=3480,
                      base_energy=3480, identity_mismatches=4764).items()),
         'WARM_AUDIT', 'exact complete best-graph scalar scope and unresolved target')
    need(base['n'] == 99 and base['degree'] == 7 and len(base['triples']) == 231
         and base['metrics']['E_lambda'] == 0 and base['metrics']['E_mu'] == 3480,
         'WARM_AUDIT', 'new full baseline reconstruction matches old scoped component checks')


def header(gate, status, stage):
    need(type(gate) is dict and gate.get('status') == status
         and gate.get('producer') == '/root/native_driver' and gate.get('verifier') == VERIFIER
         and gate.get('method') == 'independent_artifact_check' and gate.get('target_resolution') == 'NONE'
         and type(gate.get('inputs_sha256')) is dict, stage, 'fresh changed-source exact roles/scope')


def review_kernel(gate, software):
    header(gate, KERNEL_PASS, 'KERNEL_GATE')
    counts = dict(unique_fixture_labels=522, strict_author_negative_cases=160, whole_prefix_resume_equalities=3)
    need(all(type(gate.get(k)) is int and gate[k] == value for k, value in counts.items())
         and gate.get('actual_target_input_read') is False, 'KERNEL_GATE', 'finite generic objective controls only')
    need(all(gate['inputs_sha256'].get(k) == v for k, v in software.items()),
         'KERNEL_GATE', 'complete unchanged kernel/runtime/objective source pins')


def review_caller(gate, software):
    header(gate, CALLER_PASS, 'CALLER_GATE')
    need(gate.get('actual_target_input_read') is False
         and all(gate['inputs_sha256'].get(k) == v for k, v in software.items()),
         'CALLER_GATE', 'new decoder/caller finite scope and complete source pins')


def payload(base):
    return dict(schema=INPUT_SCHEMA, n=base['n'], point_degree=base['degree'], ordered_triples=base['triples'],
        metrics=base['metrics'], source_state_path=STATE, source_state_sha256=STATE_SHA,
        source_matrix_path=MATRIX, source_matrix_sha256=MATRIX_SHA,
        source_independent_audit_path=AUDIT, source_independent_audit_sha256=AUDIT_SHA,
        source_section='ordered best triples only', historical_native_state_written=False,
        rng_or_trajectory_imported=False, all_lines_mutable=True)


def review_input(gate, obj, software, io):
    header(gate, INPUT_PASS, 'INPUT_GATE')
    need(gate.get('graph_only_input') is True and gate.get('historical_native_state_written') is False
         and gate.get('rng_or_trajectory_imported') is False and gate.get('all_lines_mutable') is True,
         'INPUT_GATE', 'graph-only provenance and unrestricted line proposal domain')
    need(all(type(gate.get(k)) is int and gate[k] == v for k, v in
             dict(n=99, point_degree=7, ordered_triples=231, proposal_population=239085).items()),
         'INPUT_GATE', 'complete graph and all labelled line-pair dimensions')
    required = {**software, STATE: STATE_SHA, MATRIX: MATRIX_SHA, AUDIT: AUDIT_SHA, WARM_SOURCE: WARM_SOURCE_SHA}
    need(io.canonical(gate.get('graph_input')) == io.canonical(obj)
         and all(gate['inputs_sha256'].get(k) == v for k, v in required.items()),
         'INPUT_GATE', 'exact full independently checked literal input and changed decoder sources')


def synthetic_state(fixture):
    n, degree, triples = fixture['n'], fixture['point_degree'], fixture['triples']
    return ('HYPERGRAPH_WEIGHT60_ANNEAL_STATE_V2\n' + f'n {n}\ndegree {degree}\n'
            + 'current 0\nbest ' + str(len(triples)) + '\n'
            + ''.join(' '.join(map(str, row)) + '\n' for row in triples) + 'cn 0\nEND\n').encode()


def engineering(out, deadline, software, kernel_software, source_commit, kernel, structure, io):
    out.mkdir(parents=True, exist_ok=False)
    positives, negatives, fixture_counts = [], [], {}
    def reject(name, stage, call, raw=None, obj=None):
        need(deadline.status()['remaining_seconds'] > 20, 'DEADLINE', 'finite-control preservation reserve')
        if raw is not None:
            (out / (name + '.wire')).write_bytes(raw)
        if obj is not None:
            io.save(out / (name + '.json'), obj)
        try:
            call()
        except (CheckError, kernel.CheckError, structure.CheckError, io.CheckError) as error:
            need(error.stage == stage, 'CONTROL', 'precise malformed fixture diagnostic:' + name)
            negatives.append(dict(case=name, expected_stage=stage, actual_stage=error.stage, diagnostic=str(error)))
            return
        raise CheckError('CONTROL', 'accepted malformed fixture:' + name)
    for name, fixture in kernel.fixtures().items():
        raw = synthetic_state(fixture)
        (out / (name + '.state')).write_bytes(raw)
        base = state_graph(raw, kernel, structure)
        matrix = structure.adjacency_bytes(base['masks'])
        (out / (name + '.adj')).write_bytes(matrix)
        matrix_graph(matrix, base, structure)
        need(io.canonical(base['triples']) == io.canonical(fixture['triples']), 'CONTROL', 'literal ordered triple extraction')
        identity = dict(synthetic_fixture=name, objective=kernel.OBJECTIVE, software=software)
        whole = kernel.enumerate_to(structure, io, base, out / (name + '_whole17'), deadline, identity, limit=17, chunk=10, progress=False)
        prefix = kernel.enumerate_to(structure, io, base, out / (name + '_prefix7'), deadline, identity, limit=7, chunk=10, progress=False)
        cp = io.strict_json((ROOT / prefix['checkpoints'][-1]['path']).read_bytes())
        resumed = kernel.enumerate_to(structure, io, base, out / (name + '_resumed17'), deadline, identity, limit=17, resume=cp, chunk=10, progress=False)
        records = [r for part in whole['parts'] for r in io.read_part(part)]
        replay = [r for part in resumed['parts'] for r in io.read_part(part)]
        need(io.canonical(records) == io.canonical(replay)
             and io.canonical(whole['aggregate']) == io.canonical(resumed['aggregate']), 'CONTROL', 'exact prefix-resume equality')
        fixture_counts[name] = dict(distinct_prefix_labels=17, streamed_evaluation_calls=34, prefix_resume_equal=True)
        positives.append(name)
        for suffix, bad, stage in [('no_lf', raw[:-1], 'STATE_WIRE'), ('crlf', raw.replace(b'\n', b'\r\n'), 'STATE_WIRE'),
                                  ('nonascii', raw + b'\xff', 'STATE_WIRE'), ('badmagic', raw.replace(b'ANNEAL_STATE_V2', b'ANNEAL_STATE_V1'), 'STATE_SCHEMA'),
                                  ('duplicate_best', raw.replace(b'current 0\n', b'best 0\n'), 'STATE_HEADERS'),
                                  ('float_n', raw.replace(f'n {base["n"]}\n'.encode(), f'n {base["n"]}.0\n'.encode()), 'STATE_HEADERS'),
                                  ('short_best', raw.replace(b'best ', b'best 999'), 'STATE_DIMENSIONS')]:
            reject(name + '_' + suffix, stage, lambda x=bad: state_graph(x, kernel, structure), raw=bad)
        for suffix, bad, stage in [('no_lf', matrix[:-1], 'MATRIX_WIRE'), ('nonbinary', matrix.replace(b'0', b'2', 1), 'MATRIX_SHAPE'),
                                  ('diagonal', matrix[:len(str(base['n'])) + 1] + b'1' + matrix[len(str(base['n'])) + 2:], 'MATRIX_IDENTITY')]:
            reject(name + '_matrix_' + suffix, stage, lambda x=bad: matrix_graph(x, base, structure), raw=bad)
    synthetic_graph = dict(schema=INPUT_SCHEMA, n=99, point_degree=7, ordered_triples=[],
        metrics=dict(F3=2376, E_lambda=0, E_mu=3480, E=3480), synthetic_metadata_only=True,
        source_state_path=STATE, source_state_sha256=STATE_SHA,
        source_matrix_path=MATRIX, source_matrix_sha256=MATRIX_SHA,
        source_independent_audit_path=AUDIT, source_independent_audit_sha256=AUDIT_SHA,
        historical_native_state_written=False, rng_or_trajectory_imported=False, all_lines_mutable=True)
    gates = dict(KERNEL_GATE=dict(status=KERNEL_PASS, producer='/root/native_driver', verifier=VERIFIER,
        method='independent_artifact_check', target_resolution='NONE', inputs_sha256=copy.deepcopy(kernel_software),
        unique_fixture_labels=522, strict_author_negative_cases=160, whole_prefix_resume_equalities=3, actual_target_input_read=False),
        CALLER_GATE=dict(status=CALLER_PASS, producer='/root/native_driver', verifier=VERIFIER,
        method='independent_artifact_check', target_resolution='NONE', inputs_sha256=copy.deepcopy(software), actual_target_input_read=False),
        INPUT_GATE=dict(status=INPUT_PASS, producer='/root/native_driver', verifier=VERIFIER,
        method='independent_artifact_check', target_resolution='NONE', graph_only_input=True,
        historical_native_state_written=False, rng_or_trajectory_imported=False, all_lines_mutable=True,
        n=99, point_degree=7, ordered_triples=231, proposal_population=239085, graph_input=synthetic_graph,
        inputs_sha256={**software, STATE: STATE_SHA, MATRIX: MATRIX_SHA, AUDIT: AUDIT_SHA, WARM_SOURCE: WARM_SOURCE_SHA}))
    for stage, gate in gates.items():
        expected = kernel_software if stage == 'KERNEL_GATE' else software
        if stage == 'INPUT_GATE':
            reviewer = lambda value, ignored: review_input(value, synthetic_graph, software, io)
            expected = gate['inputs_sha256']
        else:
            reviewer = review_kernel if stage == 'KERNEL_GATE' else review_caller
        reviewer(gate, expected)
        io.save(out / (stage + '_positive.json'), gate)
        for key in ['status', 'producer', 'verifier', 'method', 'target_resolution']:
            bad = copy.deepcopy(gate)
            bad[key] = 'wrong'
            reject(stage + '_' + key, stage, lambda x=bad: reviewer(x, expected), obj=bad)
        for key in expected:
            bad = copy.deepcopy(gate)
            bad['inputs_sha256'].pop(key)
            reject(stage + '_missing_' + str(len(negatives)), stage, lambda x=bad: reviewer(x, expected), obj=bad)
        if stage != 'INPUT_GATE':
            bad = copy.deepcopy(gate)
            bad['actual_target_input_read'] = True
            reject(stage + '_target_read', stage, lambda x=bad: reviewer(x, expected), obj=bad)
        if stage == 'KERNEL_GATE':
            for key in ['unique_fixture_labels', 'strict_author_negative_cases', 'whole_prefix_resume_equalities']:
                for suffix, value in [('wrong', gate[key] + 1), ('bool', True), ('float', float(gate[key]))]:
                    bad = copy.deepcopy(gate)
                    bad[key] = value
                    reject(stage + '_' + key + '_' + suffix, stage, lambda x=bad: reviewer(x, expected), obj=bad)
        elif stage == 'INPUT_GATE':
            for key in ['graph_only_input', 'historical_native_state_written', 'rng_or_trajectory_imported', 'all_lines_mutable']:
                bad = copy.deepcopy(gate)
                bad[key] = not bad[key]
                reject(stage + '_' + key, stage, lambda x=bad: reviewer(x, expected), obj=bad)
            for key in ['n', 'point_degree', 'ordered_triples', 'proposal_population']:
                for suffix, value in [('wrong', gate[key] + 1), ('bool', True), ('float', float(gate[key]))]:
                    bad = copy.deepcopy(gate)
                    bad[key] = value
                    reject(stage + '_' + key + '_' + suffix, stage, lambda x=bad: reviewer(x, expected), obj=bad)
            for key in synthetic_graph:
                bad = copy.deepcopy(gate)
                bad['graph_input'].pop(key)
                reject(stage + '_graph_missing_' + key, stage, lambda x=bad: reviewer(x, expected), obj=bad)
    synthetic_base = dict(n=99, degree=7, triples=[[0, 1, 2]] * 231, metrics=dict(E_lambda=0, E_mu=3480))
    warm = dict(status='INDEPENDENT_HYPERGRAPH_WEIGHT60_SAVED_OBJECTS_V2_PASS', producer='/root/native_driver',
        verifier='/root/structural', target_resolution=False, saved_state_files=103,
        complete_integer_saved_current_best_objects=206, inputs_sha256={STATE: STATE_SHA, MATRIX: MATRIX_SHA, WARM_SOURCE: WARM_SOURCE_SHA},
        final_best_diagnostics=dict(domain_valid=True, srg_valid=False, ordered_entries_checked=9801,
            lambda_energy=0, mu_energy=3480, base_energy=3480, identity_mismatches=4764))
    review_warm_audit(warm, synthetic_base, io)
    io.save(out / 'WARM_AUDIT_positive.json', dict(synthetic_metadata_only=True, audit=warm))
    for key in ['status', 'producer', 'verifier', 'target_resolution']:
        bad = copy.deepcopy(warm)
        bad[key] = 'wrong'
        reject('WARM_AUDIT_' + key, 'WARM_AUDIT', lambda x=bad: review_warm_audit(x, synthetic_base, io), obj=bad)
    for key in warm['inputs_sha256']:
        bad = copy.deepcopy(warm)
        bad['inputs_sha256'].pop(key)
        reject('WARM_AUDIT_missing_' + str(len(negatives)), 'WARM_AUDIT', lambda x=bad: review_warm_audit(x, synthetic_base, io), obj=bad)
    for key in ['saved_state_files', 'complete_integer_saved_current_best_objects']:
        for suffix, value in [('wrong', warm[key] + 1), ('bool', True), ('float', float(warm[key]))]:
            bad = copy.deepcopy(warm)
            bad[key] = value
            reject('WARM_AUDIT_' + key + '_' + suffix, 'WARM_AUDIT', lambda x=bad: review_warm_audit(x, synthetic_base, io), obj=bad)
    for key in ['domain_valid', 'srg_valid']:
        bad = copy.deepcopy(warm)
        bad['final_best_diagnostics'][key] = not bad['final_best_diagnostics'][key]
        reject('WARM_AUDIT_diag_' + key, 'WARM_AUDIT', lambda x=bad: review_warm_audit(x, synthetic_base, io), obj=bad)
    for key in ['ordered_entries_checked', 'lambda_energy', 'mu_energy', 'base_energy', 'identity_mismatches']:
        for suffix, value in [('wrong', warm['final_best_diagnostics'][key] + 1), ('bool', True), ('float', float(warm['final_best_diagnostics'][key]))]:
            bad = copy.deepcopy(warm)
            bad['final_best_diagnostics'][key] = value
            reject('WARM_AUDIT_diag_' + key + '_' + suffix, 'WARM_AUDIT', lambda x=bad: review_warm_audit(x, synthetic_base, io), obj=bad)
    io.save(out / 'summary.json', dict(status='AUTHOR_TERNARY_TWO_LINE_CALLER_V1_CONTROLS_PENDING_INDEPENDENT_GATE',
        timestamp=datetime.now(timezone.utc).isoformat(), producer='/root/native_driver', command=[sys.executable, *sys.argv],
        cwd=str(ROOT), python=platform.python_version(), tqdm=importlib.metadata.version('tqdm'), source_reference_commit=source_commit,
        software=software, kernel_software=kernel_software, fixture_positives=positives, finite_prefix_counts=fixture_counts,
        synthetic_gate_positives=4, strict_negatives=negatives, strict_negative_count=len(negatives),
        actual_target_input_read=False, scientific_census_launched=False, historical_native_state_written=False,
        independent_approval=False, target_resolution='NONE', deadline=deadline.status()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['controls', 'input', 'census'])
    parser.add_argument('--seconds', type=float, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--source-commit', required=True)
    for name in ['kernel_gate', 'caller_gate', 'input_gate']:
        parser.add_argument('--' + name.replace('_', '-'), type=Path)
        parser.add_argument('--' + name.replace('_', '-') + '-sha256')
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='One all-line F3/E graph-only adapter/census or finite controls; source/input hashing and preservation included; no automatic retry or trajectory import')
    out = args.out.resolve()
    need(out.is_relative_to(ROOT) and not out.exists(), 'PATH', 'fresh bounded output')
    pins = {}
    kernel, structure, io, reference, shared = lib()
    def pin(relative, identity=None):
        need(deadline.status()['remaining_seconds'] > 20, 'DEADLINE', 'preservation reserve')
        path = (ROOT / relative).resolve()
        need(path.is_relative_to(ROOT) and path.is_file(), 'PATH', 'existing exact workspace artifact')
        name = path.relative_to(ROOT).as_posix()
        actual = sha(path)
        need(identity is None or actual == identity, 'IDENTITY', 'exact input:' + name)
        need(name not in pins or pins[name] == actual, 'IDENTITY', 'stable repeated identity')
        pins[name] = actual
        return path
    try:
        for path, identity in {**shared, **io.SOFTWARE, KERNEL: KERNEL_SHA, KERNEL_SPEC: KERNEL_SPEC_SHA}.items():
            pin(path, identity)
        kernel_software = dict(pins)
        pin(SELF)
        pin(SPEC)
        software = dict(pins)
        if args.mode == 'controls':
            engineering(out, deadline, software, kernel_software, args.source_commit, kernel, structure, io)
            return
        gates = []
        for name, reviewer, expected in [('kernel_gate', review_kernel, kernel_software), ('caller_gate', review_caller, software)]:
            need(getattr(args, name) is not None and getattr(args, name + '_sha256') is not None, 'GATES', 'genuine new finite gate')
            gate = io.strict_json(pin(getattr(args, name), getattr(args, name + '_sha256')).read_bytes())
            reviewer(gate, expected)
            gates.append(gate)
        base = state_graph(pin(STATE, STATE_SHA).read_bytes(), kernel, structure)
        matrix_graph(pin(MATRIX, MATRIX_SHA).read_bytes(), base, structure)
        audit = io.strict_json(pin(AUDIT, AUDIT_SHA).read_bytes())
        review_warm_audit(audit, base, io)
        gates.append(audit)
        graph = payload(base)
        if args.mode == 'census':
            need(args.input_gate is not None and args.input_gate_sha256 is not None, 'GATES', 'fresh independent complete graph-only input gate')
            gate = io.strict_json(pin(args.input_gate, args.input_gate_sha256).read_bytes())
            review_input(gate, graph, software, io)
            gates.append(gate)
        for gate in gates:
            for path, identity in gate['inputs_sha256'].items():
                need(path not in ['CLAIMS.yaml', '.git/index'], 'INPUT_ROLE', 'mutable historical observations are not immutable inputs')
                pin(path, identity)
        identity = dict(inputs_sha256=dict(pins), software=software, objective_version=kernel.OBJECTIVE,
            graph_only_input=graph, n=99, point_degree=7, total=239085, source_reference_commit=args.source_commit,
            source_reference_scope='Published context only; changed source/raw gates separately pinned, availability not inferred.',
            all_lines_mutable=True, lambda_zero_filter=False, root_filter=False, historical_native_state_written=False,
            question='Does this exact complete graph have an admissible line swap with smaller exact(F3,E), or exact F3zero?',
            selection_rule='Every valid proposal eligible; minimum(F3,E), then proposalID; no global search claim.')
        need(base['total'] == 239085, 'TARGET_UNIVERSE', 'all231choose2 times9 labelled proposals')
        if args.mode == 'input':
            out.mkdir(parents=True, exist_ok=False)
        else:
            kernel.enumerate_to(structure, io, base, out, deadline, identity)
        io.save(out / 'graph_input.json', graph)
        io.save(out / 'run_receipt.json', dict(timestamp=datetime.now(timezone.utc).isoformat(), producer='/root/native_driver',
            command=[sys.executable, *sys.argv], cwd=str(ROOT), python=platform.python_version(), tqdm=importlib.metadata.version('tqdm'),
            source_reference_commit=args.source_commit, inputs_sha256=pins, graph_input_sha256=sha(out / 'graph_input.json'),
            scientific_census_launched=args.mode == 'census', graph_only_input=True, historical_native_state_written=False,
            rng_or_trajectory_imported=False, all_lines_mutable=True, baseline_metrics=base['metrics'], deadline=deadline.status(),
            independent_approval=False, target_resolution='NONE', overall_search_coverage='UNKNOWN; no validated denominator.'))
    except BaseException as error:
        out.mkdir(parents=True, exist_ok=True)
        io.save(out / 'failure.json', dict(error=repr(error), inputs_sha256=pins, deadline=deadline.status(),
            preserved_partial_artifacts=True, target_resolution='NONE', independent_approval=False))
        raise


if __name__ == '__main__':
    main()
