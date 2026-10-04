"""One exact all-line F3/E census from a separately verified Saved-BEST wire.

SOURCE_ONLY until new caller controls and graph-input gates are independently
checked. The unchanged kernel defines all labelled proposals and raw records.
No native state parser, RNG, trajectory, frozen root or lambda filter is used.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
import os
import platform
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SELF = 'acceleration/census_20261003_ternary_saved_best_caller_v2.py'
SPEC = 'acceleration/census_20261003_ternary_saved_best_caller_v2_spec.md'
KERNEL = 'acceleration/census_20261003_ternary_two_line_v1.py'
KERNEL_SHA = '54d6160e61b1de83f3aa4ce9ec1b92517c542d5da73a9b54a3fbc466557a2b73'
KERNEL_SPEC = 'acceleration/census_20261003_ternary_two_line_v1_spec.md'
KERNEL_SPEC_SHA = 'c437f688324bfa9ea19587e2d51e2eae6423462284295ff01cfac04638046e2d'
SUP = 'acceleration/run_compute_command_v2.py'
SUP_SHA = '46410201dcad20eb056b8206a1b6687f9ac74f0f34e3cc66197eff5c59d55e17'
SUP_SPEC = 'acceleration/run_compute_command_v2_spec.md'
SUP_SPEC_SHA = '33e242b6dc28fa783b29825b76311fdc36d16f5cdf1897ca3b41671cafc1acc1'
KERNEL_PASS = 'INDEPENDENT_TERNARY_TWO_LINE_KERNEL_V1_COMPLETE_CONTROLS_PASS'
CALLER_PASS = 'INDEPENDENT_TERNARY_SAVED_BEST_TWO_LINE_CALLER_V1_COMPLETE_CONTROLS_PASS'
INPUT_PASS = 'INDEPENDENT_TERNARY_MIXED_GRAPH_ONLY_INPUT_V1_COMPLETE_PASS'
START_PINS = {
    'acceleration/results/20261003_ternary_mixed_pilot03/native/final.state':
        '140c3603069f01c59043c7642f7c0cff625f6a31a9386d04930bf99825188640',
    'acceleration/results/20261003_ternary_mixed_pilot03/native/best.adj':
        'bf313e3060513d501f8c7c6abe22f08f1b5b459e2ed252c6bf40f376a2fbef35',
    'acceleration/results/20261003_independent_review/ternary_mixed_saved_pilot03/summary.json':
        '7e43e40dc25d6130a7b11e648a2444b7d49c85b2e8743d641a28322fa4c4c7dd',
}
START_MATRIX_SHA = START_PINS['acceleration/results/20261003_ternary_mixed_pilot03/native/best.adj']


class CheckError(ValueError):
    def __init__(self, stage, detail=''):
        self.stage = stage
        super().__init__(stage + ': ' + detail)


def need(ok, stage, detail=''):
    if not ok:
        raise CheckError(stage, detail)


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def lib():
    for name, identity in ((KERNEL, KERNEL_SHA), (KERNEL_SPEC, KERNEL_SPEC_SHA)):
        need(sha(ROOT/name) == identity, 'SOURCE', name)
    loader = importlib.util.spec_from_file_location('unchanged_ternary_neighborhood', ROOT/KERNEL)
    kernel = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(kernel)
    structure, io, reference, shared = kernel.lib()
    return kernel, structure, io, shared


def read_wire(raw, kernel, structure):
    need(type(raw) is bytes and len(raw) <= 131072, 'WIRE_BYTES')
    try:
        text = raw.decode('ascii')
    except UnicodeError as error:
        raise CheckError('WIRE_BYTES', 'ASCII') from error
    need(text.endswith('\n') and '\r' not in text and '\0' not in text, 'WIRE_BYTES')
    lines = text[:-1].split('\n')
    need(len(lines) >= 7 and lines[0] == 'TERNARY_LINEAR_GRAPH_INPUT_V1'
         and lines[-1] == 'END', 'WIRE_SCHEMA')
    values = []
    for at, key in ((1, 'n'), (2, 'degree'), (4, 'triples')):
        need(re.fullmatch(key+r' (0|[1-9][0-9]*)', lines[at]) is not None, 'WIRE_FIELDS', key)
        values.append(int(lines[at].split(' ')[1]))
    need(re.fullmatch(r'source_graph_sha256 [0-9a-f]{64}', lines[3]) is not None, 'WIRE_FIELDS', 'source hash')
    n, degree, count = values
    need(3 <= n <= 99 and 0 < 2*degree < n and 3*count == n*degree, 'WIRE_DIMENSIONS')
    need(len(lines) == count+6, 'WIRE_POPULATION')
    rows = []
    for line in lines[5:-1]:
        need(re.fullmatch(r'(0|[1-9][0-9]*) (0|[1-9][0-9]*) (0|[1-9][0-9]*)', line) is not None,
             'WIRE_ROWS', 'three literal canonical unsigned labels')
        rows.append([int(x) for x in line.split(' ')])
    base = kernel.domain(structure, n, degree, rows)
    source = lines[3].split(' ')[1]
    need(hashlib.sha256(structure.adjacency_bytes(base['masks'])).hexdigest() == source,
         'WIRE_MATRIX', 'complete rebuilt adjacency identity')
    return base, source


def fixture_wire(base, structure):
    source = hashlib.sha256(structure.adjacency_bytes(base['masks'])).hexdigest()
    return (f'TERNARY_LINEAR_GRAPH_INPUT_V1\nn {base["n"]}\ndegree {base["degree"]}\n'
            + f'source_graph_sha256 {source}\ntriples {len(base["triples"])}\n'
            + ''.join(' '.join(map(str, row))+'\n' for row in base['triples'])+'END\n').encode('ascii')


def header(gate, status, verifier, stage):
    need(type(gate) is dict and gate.get('status') == status
         and gate.get('producer') == '/root/native_driver' and gate.get('verifier') == verifier
         and gate.get('method') == 'independent_artifact_check' and gate.get('target_resolution') == 'NONE'
         and type(gate.get('inputs_sha256')) is dict, stage, 'exact independently assigned role/status')


def finite_gate(gate, software, caller=False):
    stage = 'CALLER_GATE' if caller else 'KERNEL_GATE'
    header(gate, CALLER_PASS if caller else KERNEL_PASS, '/root/structural', stage)
    counts = dict(unique_fixture_labels=51, strict_author_negative_cases=144, whole_prefix_resume_equalities=3) if caller else dict(
        unique_fixture_labels=522, strict_author_negative_cases=160, whole_prefix_resume_equalities=3)
    need(gate.get('actual_target_input_read') is False
         and all(type(gate.get(k)) is int and gate[k] == v for k, v in counts.items()), stage, 'exact finite scope')
    need(all(gate['inputs_sha256'].get(k) == v for k, v in software.items()), stage, 'every software pin')


def input_gate(gate, base, wire_name, wire_sha, source_sha, prerequisite_pins, io):
    stage = 'INPUT_GATE'
    header(gate, INPUT_PASS, '/root/checkpoint_audit', stage)
    need(type(gate.get('input_implementation_version')) is int and gate['input_implementation_version'] == 2
         and gate.get('source_kind') == 'final.best', stage, 'new Saved-BEST implementation, no old census gate transfer')
    need(gate.get('native_state_written') is False and gate.get('history_rng_counters_imported') is False
         and gate.get('retained_construction_triples_are_all_graph_triangles_claimed') is False,
         stage, 'geometry only; construction triples need not be every actual triangle')
    expected = dict(n=base['n'], point_degree=base['degree'], ordered_triples=len(base['triples']),
                    complete_integer_matrix_products=base['n']**2)
    need(all(type(gate.get(k)) is int and gate[k] == v for k, v in expected.items()), stage, 'literal complete matrix scope')
    need(gate.get('graph_input_path') == wire_name and gate.get('graph_input_sha256') == wire_sha
         and gate.get('source_graph_sha256') == source_sha, stage, 'exact wire and reconstructed source matrix')
    need(io.canonical(gate.get('metrics')) == io.canonical(base['metrics']), stage, 'typed complete scalar metrics')
    required = {**prerequisite_pins, wire_name: wire_sha}
    need(all(gate['inputs_sha256'].get(k) == v for k, v in required.items()), stage, 'new wire and exact Saved-BEST prerequisite identities')


def engineering(out, deadline, kernel, structure, io, software, kernel_software, source_commit):
    out.mkdir(parents=True, exist_ok=False)
    negatives, fixtures = [], {}
    def reject(label, stage, call, raw=None, obj=None):
        need(deadline.status()['remaining_seconds'] > 20, 'DEADLINE', 'control preservation reserve')
        if raw is not None:
            (out/(label+'.wire')).write_bytes(raw)
        if obj is not None:
            io.save(out/(label+'.json'), obj)
        try:
            call()
        except (CheckError, kernel.CheckError, structure.CheckError, io.CheckError) as error:
            need(error.stage == stage, 'CONTROL_STAGE', label+': '+str(error))
            negatives.append(dict(case=label, expected_stage=stage, actual_stage=error.stage, diagnostic=str(error)))
        else:
            raise CheckError('CONTROL_ACCEPTED', label)
    for name, fixture in kernel.fixtures().items():
        base = kernel.domain(structure, fixture['n'], fixture['point_degree'], fixture['triples'])
        raw = fixture_wire(base, structure)
        (out/(name+'.wire')).write_bytes(raw)
        decoded, source = read_wire(raw, kernel, structure)
        need(io.canonical(decoded) == io.canonical(base), 'CONTROL', 'complete exact generic wire roundtrip')
        identity = dict(synthetic_fixture=name, software=software, objective_version=kernel.OBJECTIVE)
        whole = kernel.enumerate_to(structure, io, base, out/(name+'_whole17'), deadline, identity, limit=17, chunk=10, progress=False)
        prefix = kernel.enumerate_to(structure, io, base, out/(name+'_prefix7'), deadline, identity, limit=7, chunk=10, progress=False)
        cp = io.strict_json((ROOT/prefix['checkpoints'][-1]['path']).read_bytes())
        resumed = kernel.enumerate_to(structure, io, base, out/(name+'_resumed17'), deadline, identity, limit=17, resume=cp, chunk=10, progress=False)
        records = [r for p in whole['parts'] for r in io.read_part(p)]
        replay = [r for p in resumed['parts'] for r in io.read_part(p)]
        need(io.canonical(records) == io.canonical(replay) and io.canonical(whole['aggregate']) == io.canonical(resumed['aggregate']),
             'CONTROL', 'literal whole versus prefix/resume records and aggregate')
        fixtures[name] = dict(distinct_prefix_labels=17, evaluated_calls=34, prefix_resume_equal=True,
                              metrics=base['metrics'], source_graph_sha256=source)
        if name == 'prism9':
            need(base['metrics']['E_lambda'] > 0, 'CONTROL', 'positive-lambda input accepted')
        lines = raw.decode('ascii').splitlines()
        bad_count = raw.replace(f'triples {len(base["triples"])}\n'.encode(), f'triples {len(base["triples"])+1}\n'.encode())
        duplicate = lines[:2]+[lines[1]]+lines[2:]
        short = lines[:5]+lines[6:]
        float_row = lines[:];float_row[5] = float_row[5].replace(' ', '.0 ', 1)
        repeated = lines[:];points = repeated[5].split(' ');points[1] = points[0];repeated[5] = ' '.join(points)
        variants = [
            ('no_lf', raw[:-1], 'WIRE_BYTES'), ('crlf', raw.replace(b'\n', b'\r\n'), 'WIRE_BYTES'),
            ('nonascii', raw+b'\xff', 'WIRE_BYTES'), ('magic', raw.replace(b'TERNARY_LINEAR_GRAPH_INPUT_V1', b'OTHER_INPUT'), 'WIRE_SCHEMA'),
            ('float_n', raw.replace(f'n {base["n"]}\n'.encode(), f'n {base["n"]}.0\n'.encode()), 'WIRE_FIELDS'),
            ('duplicate_header', ('\n'.join(duplicate)+'\n').encode(), 'WIRE_FIELDS'),
            ('bad_hash', raw.replace(source.encode(), b'X'*64), 'WIRE_FIELDS'), ('wrong_count', bad_count, 'WIRE_DIMENSIONS'),
            ('short_rows', ('\n'.join(short)+'\n').encode(), 'WIRE_POPULATION'),
            ('float_row', ('\n'.join(float_row)+'\n').encode(), 'WIRE_ROWS'),
            ('repeated_point', ('\n'.join(repeated)+'\n').encode(), 'DOMAIN'),
            ('different_hash', raw.replace(source.encode(), b'0'*64), 'WIRE_MATRIX')]
        for label, bad, stage in variants:
            reject(name+'_'+label, stage, lambda b=bad: read_wire(b, kernel, structure), raw=bad)
    for caller, expected in ((False, kernel_software), (True, software)):
        stage = 'CALLER_GATE' if caller else 'KERNEL_GATE'
        counts = dict(unique_fixture_labels=51, strict_author_negative_cases=144, whole_prefix_resume_equalities=3) if caller else dict(
            unique_fixture_labels=522, strict_author_negative_cases=160, whole_prefix_resume_equalities=3)
        gate = dict(status=CALLER_PASS if caller else KERNEL_PASS, producer='/root/native_driver', verifier='/root/structural',
                    method='independent_artifact_check', target_resolution='NONE', inputs_sha256=expected.copy(),
                    actual_target_input_read=False, **counts)
        finite_gate(gate, expected, caller)
        io.save(out/(stage+'_synthetic_positive.json'), gate)
        for key in ('status', 'producer', 'verifier', 'method', 'target_resolution'):
            bad = copy.deepcopy(gate);bad[key] = 'wrong'
            reject(stage+'_'+key, stage, lambda b=bad: finite_gate(b, expected, caller), obj=bad)
        for at, key in enumerate(expected):
            bad = copy.deepcopy(gate);bad['inputs_sha256'].pop(key)
            reject(stage+'_missing_pin_'+str(at), stage, lambda b=bad: finite_gate(b, expected, caller), obj=bad)
        bad = copy.deepcopy(gate);bad['actual_target_input_read'] = True
        reject(stage+'_target_read', stage, lambda: finite_gate(bad, expected, caller), obj=bad)
        for key, value in counts.items():
            for label, replacement in (('wrong', value+1), ('bool', True), ('float', float(value))):
                bad = copy.deepcopy(gate);bad[key] = replacement
                reject(stage+'_'+key+'_'+label, stage, lambda b=bad: finite_gate(b, expected, caller), obj=bad)
    # This is a synthetic metadata relation over the already decoded generic
    # rook fixture. It is not an actual Saved4 report or target graph approval.
    fixture = kernel.fixtures()['rook9']
    base = kernel.domain(structure, fixture['n'], fixture['point_degree'], fixture['triples'])
    source = hashlib.sha256(structure.adjacency_bytes(base['masks'])).hexdigest()
    wire_name, wire_sha = 'build/synthetic-geometry.wire', '1'*64
    prerequisite = {'build/synthetic-state.fragment':'2'*64, 'build/synthetic-matrix.adj':source, 'build/synthetic-report.json':'3'*64}
    gate = dict(status=INPUT_PASS, producer='/root/native_driver', verifier='/root/checkpoint_audit', method='independent_artifact_check',
        target_resolution='NONE', input_implementation_version=2, source_kind='final.best', native_state_written=False,
        history_rng_counters_imported=False, retained_construction_triples_are_all_graph_triangles_claimed=False,
        n=9, point_degree=2, ordered_triples=6, complete_integer_matrix_products=81,
        graph_input_path=wire_name, graph_input_sha256=wire_sha, source_graph_sha256=source,
        metrics=copy.deepcopy(base['metrics']), inputs_sha256={**prerequisite, wire_name:wire_sha})
    review = lambda obj: input_gate(obj, base, wire_name, wire_sha, source, prerequisite, io)
    review(gate);io.save(out/'INPUT_GATE_synthetic_positive.json', gate)
    for key in ('status', 'producer', 'verifier', 'method', 'target_resolution'):
        bad = copy.deepcopy(gate);bad[key] = 'wrong'
        reject('INPUT_GATE_'+key, 'INPUT_GATE', lambda b=bad: review(b), obj=bad)
    for label, value in (('wrong', 3), ('bool', True), ('float', 2.0)):
        bad = copy.deepcopy(gate);bad['input_implementation_version'] = value
        reject('INPUT_GATE_version_'+label, 'INPUT_GATE', lambda b=bad: review(b), obj=bad)
    bad = copy.deepcopy(gate);bad['source_kind'] = 'census_selected'
    reject('INPUT_GATE_source_kind', 'INPUT_GATE', lambda: review(bad), obj=bad)
    for key in ('native_state_written', 'history_rng_counters_imported', 'retained_construction_triples_are_all_graph_triangles_claimed'):
        bad = copy.deepcopy(gate);bad[key] = True
        reject('INPUT_GATE_'+key, 'INPUT_GATE', lambda b=bad: review(b), obj=bad)
    for key in ('n', 'point_degree', 'ordered_triples', 'complete_integer_matrix_products'):
        for label, value in (('wrong', gate[key]+1), ('bool', True), ('float', float(gate[key]))):
            bad = copy.deepcopy(gate);bad[key] = value
            reject('INPUT_GATE_'+key+'_'+label, 'INPUT_GATE', lambda b=bad: review(b), obj=bad)
    for key in ('graph_input_path', 'graph_input_sha256', 'source_graph_sha256'):
        bad = copy.deepcopy(gate);bad[key] = 'wrong'
        reject('INPUT_GATE_'+key, 'INPUT_GATE', lambda b=bad: review(b), obj=bad)
    for key in base['metrics']:
        bad = copy.deepcopy(gate)
        bad['metrics'][key] = [True,0,0] if key == 'residue_population' else float(base['metrics'][key])
        reject('INPUT_GATE_metric_'+key, 'INPUT_GATE', lambda b=bad: review(b), obj=bad)
    for at, key in enumerate(gate['inputs_sha256']):
        bad = copy.deepcopy(gate);bad['inputs_sha256'].pop(key)
        reject('INPUT_GATE_missing_pin_'+str(at), 'INPUT_GATE', lambda b=bad: review(b), obj=bad)
    groups = {key:sum(row['expected_stage'] == key for row in negatives) for key in ('KERNEL_GATE', 'CALLER_GATE', 'INPUT_GATE')}
    groups['WIRE'] = len(negatives)-sum(groups.values())
    need(groups == dict(KERNEL_GATE=33, CALLER_GATE=37, INPUT_GATE=38, WIRE=36) and len(negatives) == 144,
         'CONTROL_POPULATION', 'source-derived 36+33+37+38 precise stages')
    need(deadline.status()['remaining_seconds'] > 20, 'DEADLINE', 'final control preservation reserve')
    io.save(out/'summary.json', dict(status='AUTHOR_TERNARY_SAVED_BEST_TWO_LINE_CALLER_V2_CONTROLS_PENDING_INDEPENDENT_GATE',
        timestamp=datetime.now(timezone.utc).isoformat(), producer='/root/native_driver', command=[sys.executable,*sys.argv], cwd=str(ROOT),
        source_reference_commit=source_commit, software=software, kernel_software=kernel_software,
        unique_fixture_labels=51, evaluated_fixture_calls=102, whole_prefix_resume_equalities=3, fixture_counts=fixtures,
        strict_author_negative_cases=144, negative_group_counts=groups, strict_negatives=negatives, synthetic_gate_positives=3,
        actual_target_input_read=False, scientific_census_launched=False, native_calls=0, historical_native_state_written=False,
        rng_or_trajectory_imported=False, independent_approval=False, target_resolution='NONE', deadline=deadline.status()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('controls','census'))
    parser.add_argument('--seconds', type=float, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--supervision-out', type=Path, required=True)
    parser.add_argument('--source-commit', required=True)
    for name in ('kernel-gate','caller-gate','input-gate','wire'):
        parser.add_argument('--'+name, type=Path)
        parser.add_argument('--'+name+'-sha256')
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='One Saved-BEST all-line F3/E neighborhood or finite caller controls; complete source/gate/input hashing inside invocation;20save;no retry/history/native')
    out = args.out.resolve();pins = {}; started = False
    def tick():
        need(not deadline.status()['stop_required'] and deadline.status()['remaining_seconds'] > 20, 'DEADLINE', 'preservation reserve')
    def pin(name, identity=None):
        tick();path = (ROOT/name).resolve()
        need(path.is_relative_to(ROOT) and path.is_file(), 'PATH', 'exact workspace file')
        relative = path.relative_to(ROOT).as_posix()
        need(relative not in ('CLAIMS.yaml','.git/index'), 'INPUT_ROLE', 'mutable observations cannot be immutable inputs')
        value = sha(path)
        need(identity is None or type(identity) is str and re.fullmatch('[0-9a-f]{64}',identity) and value == identity, 'IDENTITY', relative)
        need(relative not in pins or pins[relative] == value, 'IDENTITY', 'repeated pin stability')
        pins[relative] = value;return path
    try:
        need(out.is_relative_to(ROOT) and not out.exists(), 'FRESH_OUTPUT')
        started = True
        kernel, structure, io, shared = lib()
        for name, identity in {**shared,**io.SOFTWARE,KERNEL:KERNEL_SHA,KERNEL_SPEC:KERNEL_SPEC_SHA}.items():
            pin(name, identity)
        kernel_software = pins.copy()
        for name, identity in ((SUP,SUP_SHA),(SUP_SPEC,SUP_SPEC_SHA),(SELF,None),(SPEC,None)):
            pin(name, identity)
        software = pins.copy()
        need(len(kernel_software) == 18 and len(software) == 22, 'SOFTWARE_POPULATION')
        runtime = io.strict_json(pin(args.supervision_out/'manifest.json').read_bytes())
        need(os.name == 'posix' and os.geteuid() == 1000 and runtime.get('source_sha256') == SUP_SHA
             and runtime.get('runtime_scope') == 'LOCAL_LINUX_GROUP_BOUNDED_CLEANUP_V2'
             and runtime.get('cwd') == str(ROOT) and runtime.get('automatic_retry') is False
             and runtime.get('cumulative_across_commands') is False and runtime.get('seconds') >= args.seconds+20
             and runtime.get('command',[])[-len(sys.argv):] == [sys.executable,*sys.argv][1:], 'SUPERVISOR', 'actual inside-Linux SUP2/UID/worker suffix')
        group = os.getpgid(0)
        guard = [value.decode() for value in (Path('/proc')/str(group)/'cmdline').read_bytes().split(b'\0') if value]
        need(guard and Path(guard[0]).name == 'timeout' and '--signal=KILL' in guard, 'SUPERVISOR', 'actual supported live Linux group')
        if args.mode == 'controls':
            engineering(out, deadline, kernel, structure, io, software, kernel_software, args.source_commit)
            tick()
            return
        need(all(getattr(args,name) is not None and getattr(args,name+'_sha256') is not None
                 for name in ('kernel_gate','caller_gate','input_gate','wire')), 'GATE_ARGUMENTS', 'genuine explicit gates and wire')
        kernel_gate = io.strict_json(pin(args.kernel_gate,args.kernel_gate_sha256).read_bytes())
        caller_gate = io.strict_json(pin(args.caller_gate,args.caller_gate_sha256).read_bytes())
        finite_gate(kernel_gate,kernel_software)
        finite_gate(caller_gate,software,True)
        wire_file = pin(args.wire,args.wire_sha256)
        base, source = read_wire(wire_file.read_bytes(),kernel,structure)
        need((base['n'],base['degree'],len(base['triples']),base['total']) == (99,7,231,239085)
             and source == START_MATRIX_SHA, 'TARGET_START', 'exact independently saved pilot03 BEST, no root or lambda restriction')
        checked = io.strict_json(pin(args.input_gate,args.input_gate_sha256).read_bytes())
        wire_name = wire_file.relative_to(ROOT).as_posix()
        input_gate(checked,base,wire_name,args.wire_sha256,source,START_PINS,io)
        for gate in (kernel_gate,caller_gate,checked):
            for name, identity in gate['inputs_sha256'].items():
                pin(name,identity)
        identity = dict(schema='TERNARY_SAVED_BEST_NEIGHBORHOOD_IDENTITY_V1', inputs_sha256=pins.copy(), software=software,
            objective_version=kernel.OBJECTIVE, n=99, point_degree=7, total=239085,
            graph_input_path=wire_name,graph_input_sha256=args.wire_sha256,source_graph_sha256=source,
            saved_best_prerequisite_pins=START_PINS, source_reference_commit=args.source_commit,
            all_lines_mutable=True, lambda_zero_filter=False, root_filter=False,
            historical_native_state_written=False,rng_or_trajectory_imported=False,
            question='Does this exact Saved-BEST graph admit a valid labelled two-line swap with smaller exact(F3,E), or exact zero?',
            selection_rule='All valid labels eligible;minimum(F3,E),then proposalID;no graph-space/global-optimum claim.')
        tick()
        manifest = kernel.enumerate_to(structure,io,base,out,deadline,identity)
        tick()
        for name, value in ((args.wire,args.wire_sha256),(args.kernel_gate,args.kernel_gate_sha256),
                            (args.caller_gate,args.caller_gate_sha256),(args.input_gate,args.input_gate_sha256)):
            need(sha(ROOT/name) == value, 'CLOSING_IDENTITY')
            tick()
        io.save(out/'graph_input.json',dict(schema='TERNARY_SAVED_BEST_ALL_LINE_CENSUS_INPUT_V1',n=99,point_degree=7,
            ordered_triples=base['triples'],metrics=base['metrics'],source_graph_sha256=source,
            graph_input_path=wire_name,graph_input_sha256=args.wire_sha256,saved_best_prerequisite_pins=START_PINS,
            all_lines_mutable=True,historical_native_state_written=False,rng_or_trajectory_imported=False))
        tick()
        io.save(out/'run_receipt.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),producer='/root/native_driver',
            command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),source_reference_commit=args.source_commit,
            inputs_sha256=pins,software=software,source_graph_sha256=source,baseline_metrics=base['metrics'],
            graph_input_sha256=sha(out/'graph_input.json'),manifest_sha256=sha(out/'manifest.json'),
            scientific_census_launched=True,native_calls=0,all_lines_mutable=True,historical_native_state_written=False,
            rng_or_trajectory_imported=False,independent_approval=False,target_resolution='NONE',deadline=deadline.status()))
        tick()
    except BaseException as error:
        if started:
            out.mkdir(parents=True,exist_ok=True)
            with (out/'failure.json').open('x',encoding='utf8',newline='\n') as stream:
                json.dump(dict(error=repr(error),inputs_sha256=pins,outputs_preserved=True,
                    automatic_retry=False,independent_approval=False,target_resolution='NONE',deadline=deadline.status()),stream,indent=2,allow_nan=False)
                stream.write('\n')
        raise


if __name__ == '__main__':
    main()
