"""One restricted CN1/CN3 oriented role census on an exact checked graph.

SOURCE ONLY until fresh caller controls, independent gates and ROOT review.
No automatic path, repeated science, or manufactured native history.
"""
import argparse
import copy
import hashlib
import importlib.metadata
import importlib.util
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SELF = 'acceleration/census_20261003_root_focused_restricted_three_line_caller_v1.py'
SPEC = 'acceleration/census_20261003_root_focused_restricted_three_line_caller_v1_spec.md'
PROJECTOR = 'acceleration/project_20261003_root_focused_chain_graph_v2.py'
PROJECTOR_SHA = '5c22e4fec65ef3d95ae3f6e09023b3067b674d1a631c228e09b2282daa5d2aab'
PROJECTOR_SPEC = 'acceleration/project_20261003_root_focused_chain_graph_v2_spec.md'
PROJECTOR_SPEC_SHA = '80d5e9148bd8bf387448483e3dd470c3418dea1d7ecaeb392a9e4bf63a2ed2a3'
KERNEL = 'acceleration/census_20261003_root_focused_restricted_three_line_v3.py'
KERNEL_SHA = '493aeace43b91c755c2c038db0ab71fd61f4acbcf62d7a717b07894fb7f0f41e'
KERNEL_SPEC = 'acceleration/census_20261003_root_focused_restricted_three_line_v3_spec.md'
KERNEL_SPEC_SHA = 'e2dcded34b2deb6f5eb0c326353487bb741e5b22eae9447d5216902982bc0164'
GRAPH = 'acceleration/results/20261003_root_focused_selected145287_projection01/graph_input.json'
GRAPH_SHA = '203204c24e3a2f4901cabd85f9c3f740db5b053831393db65c201a3773ff1748'
INPUT_GATE = 'acceleration/results/20261003_independent_review/root_focused_selected145287_projection_full01/summary.json'
INPUT_GATE_SHA = 'b664c631ec37c8d4cbd08d395aebed538f8acdfebf8f4c751be731fd0b9152de'
KERNEL_PASS = 'INDEPENDENT_RESTRICTED_ROOT_THREE_LINE_V3_CONTROLS_PASS'
CALLER_PASS = 'INDEPENDENT_RESTRICTED_ROOT_THREE_LINE_CALLER_V1_CONTROLS_PASS'


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


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def lib():
    for path, identity in [(PROJECTOR, PROJECTOR_SHA), (PROJECTOR_SPEC, PROJECTOR_SPEC_SHA),
                           (KERNEL, KERNEL_SHA), (KERNEL_SPEC, KERNEL_SPEC_SHA)]:
        need(sha(ROOT / path) == identity, 'SOURCE', 'unchanged exact producer component:' + path)
    projector = load_module(PROJECTOR, 'unchanged_strict_lex_graph_projection')
    helper, engine = projector.lib()
    kernel = load_module(KERNEL, 'restricted_three_line_v3_kernel')
    return projector, helper, engine, kernel


def independent_header(gate, status, stage):
    need(type(gate) is dict and gate.get('status') == status
         and gate.get('producer') == '/root/native_driver' and gate.get('verifier') == '/root/structural'
         and gate.get('method') == 'independent_artifact_check' and gate.get('target_resolution') == 'NONE'
         and type(gate.get('inputs_sha256')) is dict, stage, 'exact changed-source independent scope and roles')


def review_input(gate, obj, projector, helper, engine):
    # Narrowly copied from the preserved fcf844 graph-only caller interface;
    # this new caller neither imports that caller nor transfers its gate.
    independent_header(gate, projector.INPUT_PASS, 'INPUT_GATE')
    need(gate.get('historical_native_state_written') is False and gate.get('graph_only_input') is True,
         'INPUT_GATE', 'graph-only input with no invented native state/history')
    dims = dict(n=99, point_degree=7, root=11, ordered_triples=231, mutable_lines=224, frozen_lines=7,
                selected_proposal_id=145287)
    need(all(type(gate.get(k)) is int and gate[k] == v for k, v in dims.items()), 'INPUT_GATE', 'exact selected graph dimensions')
    prov = obj['provenance']
    need(type(prov.get('selected_proposal_id')) is int and prov['selected_proposal_id'] == 145287,
         'INPUT_GATE', 'actual independently checked selected label')
    fields = dict(graph_input_path=GRAPH, graph_input_sha256=GRAPH_SHA,
        source_manifest_sha256=prov['source_manifest']['sha256'], source_matrix_sha256=prov['source_matrix']['sha256'],
        source_triples_sha256=prov['source_triples']['sha256'], source_complete_audit_sha256=prov['source_complete_audit']['sha256'])
    need(all(type(gate.get(k)) is str and gate[k] == v for k, v in fields.items()), 'INPUT_GATE', 'every selected source identity')
    need(helper.equal(gate.get('metrics'), obj['metrics'])
         and helper.equal(gate.get('source_baseline_metrics'), prov['source_baseline_metrics'])
         and helper.equal(gate.get('frozen_original_literal_rows'), engine.FROZEN_ROWS),
         'INPUT_GATE', 'exact components, baseline and seven original frozen literal rows')
    pins = {GRAPH: GRAPH_SHA, PROJECTOR: PROJECTOR_SHA, PROJECTOR_SPEC: PROJECTOR_SPEC_SHA}
    for key in ['source_manifest', 'source_matrix', 'source_triples', 'source_complete_audit']:
        pins[prov[key]['path']] = prov[key]['sha256']
    need(all(gate['inputs_sha256'].get(k) == v for k, v in pins.items()), 'INPUT_GATE', 'complete direct graph/source binding')


def review_kernel(gate, software):
    independent_header(gate, KERNEL_PASS, 'KERNEL_GATE')
    counts = dict(unique_fixture_role_records=4032, strict_author_negative_cases=95, whole_prefix_resume_equalities=3)
    need(all(type(gate.get(k)) is int and gate[k] == v for k, v in counts.items())
         and gate.get('actual_target_input_read') is False, 'KERNEL_GATE', 'finite generic role/control scope only')
    need(all(gate['inputs_sha256'].get(k) == v for k, v in software.items()), 'KERNEL_GATE', 'exact unchanged V3 kernel/runtime closure')


def review_caller(gate, software):
    independent_header(gate, CALLER_PASS, 'CALLER_GATE')
    need(all(gate['inputs_sha256'].get(k) == v for k, v in software.items()), 'CALLER_GATE', 'every changed caller and reused producer dependency')


def engineering(out, deadline, software, kernel_software, source_commit, projector, helper, engine, kernel):
    out.mkdir(parents=True, exist_ok=False)
    positives, fixture_counts = [], {}
    for name, fixture in kernel.fixtures().items():
        need(deadline.status()['remaining_seconds'] > 20, 'DEADLINE', 'finite integration preservation reserve')
        base = engine.domain(**fixture)
        obj = projector.payload(base, projector.synthetic_provenance())
        raw = kernel.canonical(obj)
        (out / (name + '.graph.json')).write_bytes(raw)
        decoded, found = projector.decode(raw, helper, engine, target=False)
        need(kernel.canonical(found) == kernel.canonical(obj), 'CONTROL', 'literal generic graph reader roundtrip')
        domain = kernel.restricted_domain(engine, fixture['n'], fixture['degree'], decoded['triples'], fixture['root'])
        limit = min(17, domain['total'])
        identity = dict(synthetic_fixture=name, software=software, universe=domain['universe'])
        whole = kernel.enumerate_to(engine, domain, out / (name + '_prefix_whole'), deadline, identity,
                                    limit=limit, chunk=10, progress=False)
        split = kernel.enumerate_to(engine, domain, out / (name + '_prefix7'), deadline, identity,
                                    limit=min(7, limit), chunk=10, progress=False)
        checkpoint = kernel.strict_json((ROOT / split['checkpoints'][-1]['path']).read_bytes())
        resumed = kernel.enumerate_to(engine, domain, out / (name + '_prefix_resumed'), deadline, identity,
                                      limit=limit, resume=checkpoint, chunk=10, progress=False)
        records = [r for part in whole['parts'] for r in kernel.read_part(part)]
        other = [r for part in resumed['parts'] for r in kernel.read_part(part)]
        need(kernel.canonical(records) == kernel.canonical(other)
             and kernel.canonical(whole['aggregate']) == kernel.canonical(resumed['aggregate']),
             'CONTROL', 'same literal finite prefix and full prefix aggregate after resume')
        for record in records:
            kernel.record_check(engine, domain, record)
        fixture_counts[name] = dict(role_universe=domain['total'], distinct_prefix_records=len(records),
            evaluation_calls=whole['proposals_evaluated_this_invocation'] + split['proposals_evaluated_this_invocation']
                             + resumed['proposals_evaluated_this_invocation'], prefix_resume_equal=True)
        positives.append(name)
    refs = {key: dict(path='synthetic/' + key + '.json', sha256='0' * 64)
            for key in ['source_manifest', 'source_matrix', 'source_triples', 'source_complete_audit']}
    obj = dict(metrics=dict(E_lambda=0, E_mu=5292, R_root=10), provenance=dict(selected_proposal_id=145287,
        **refs, source_baseline_metrics=dict(E_lambda=0, E_mu=5344, R_root=10)))
    input_gate = dict(status=projector.INPUT_PASS, producer='/root/native_driver', verifier='/root/structural',
        method='independent_artifact_check', target_resolution='NONE', graph_only_input=True, historical_native_state_written=False,
        n=99, point_degree=7, root=11, ordered_triples=231, mutable_lines=224, frozen_lines=7, selected_proposal_id=145287,
        graph_input_path=GRAPH, graph_input_sha256=GRAPH_SHA, frozen_original_literal_rows=copy.deepcopy(engine.FROZEN_ROWS),
        metrics=copy.deepcopy(obj['metrics']), source_baseline_metrics=copy.deepcopy(obj['provenance']['source_baseline_metrics']),
        **{key + '_sha256': refs[key]['sha256'] for key in refs},
        inputs_sha256={GRAPH: GRAPH_SHA, PROJECTOR: PROJECTOR_SHA, PROJECTOR_SPEC: PROJECTOR_SPEC_SHA,
                      **{v['path']: v['sha256'] for v in refs.values()}})
    kernel_gate = dict(status=KERNEL_PASS, producer='/root/native_driver', verifier='/root/structural',
        method='independent_artifact_check', target_resolution='NONE', inputs_sha256=copy.deepcopy(kernel_software),
        unique_fixture_role_records=4032, strict_author_negative_cases=95, whole_prefix_resume_equalities=3,
        actual_target_input_read=False)
    caller_gate = dict(status=CALLER_PASS, producer='/root/native_driver', verifier='/root/structural',
        method='independent_artifact_check', target_resolution='NONE', inputs_sha256=copy.deepcopy(software))
    reviewers = dict(INPUT_GATE=lambda g: review_input(g, obj, projector, helper, engine),
                     KERNEL_GATE=lambda g: review_kernel(g, kernel_software), CALLER_GATE=lambda g: review_caller(g, software))
    gates = dict(INPUT_GATE=input_gate, KERNEL_GATE=kernel_gate, CALLER_GATE=caller_gate)
    negatives = []
    for stage, gate in gates.items():
        reviewers[stage](gate)
        kernel.save(out / (stage + '_synthetic_positive.json'), dict(synthetic_metadata_only=True,
                    actual99graph_read=False, gate=gate, object_metadata=obj if stage == 'INPUT_GATE' else None))
        def reject(label, mutate):
            need(deadline.status()['remaining_seconds'] > 20, 'DEADLINE', 'finite gate-control preservation reserve')
            bad = copy.deepcopy(gate)
            mutate(bad)
            kernel.save(out / (stage + '_' + label + '.json'), dict(synthetic_metadata_only=True, gate=bad))
            try:
                reviewers[stage](bad)
            except CheckError as error:
                need(error.stage == stage, 'CONTROL', 'exact typed metadata veto:' + label)
                negatives.append(dict(case=stage + '_' + label, expected_stage=stage, actual_stage=error.stage, diagnostic=str(error)))
                return
            raise CheckError('CONTROL', 'accepted malformed gate:' + stage + '_' + label)
        for key in ['status', 'producer', 'verifier', 'method', 'target_resolution']:
            reject('wrong_' + key, lambda x, k=key: x.__setitem__(k, 'wrong'))
        for at, key in enumerate(gate['inputs_sha256']):
            reject('missing_pin_' + str(at), lambda x, k=key: x['inputs_sha256'].pop(k))
        if stage == 'INPUT_GATE':
            for key in ['graph_only_input', 'historical_native_state_written']:
                reject('wrong_' + key, lambda x, k=key: x.__setitem__(k, not x[k]))
            for key in ['n', 'point_degree', 'root', 'ordered_triples', 'mutable_lines', 'frozen_lines', 'selected_proposal_id']:
                for suffix, value in [('wrong', gate[key] + 1), ('bool', True), ('float', float(gate[key]))]:
                    reject(key + '_' + suffix, lambda x, k=key, v=value: x.__setitem__(k, v))
            for key in ['graph_input_path', 'graph_input_sha256', 'source_manifest_sha256', 'source_matrix_sha256',
                        'source_triples_sha256', 'source_complete_audit_sha256']:
                reject('wrong_' + key, lambda x, k=key: x.__setitem__(k, 'wrong'))
            for owner in ['metrics', 'source_baseline_metrics']:
                for key in ['E_lambda', 'E_mu', 'R_root']:
                    reject('wrong_' + owner + '_' + key, lambda x, o=owner, k=key: x[o].__setitem__(k, x[o][k] + 1))
                reject('bool_' + owner, lambda x, o=owner: x[o].__setitem__('R_root', False))
                reject('float_' + owner, lambda x, o=owner: x[o].__setitem__('R_root', float(x[o]['R_root'])))
            reject('frozen_row_reordered', lambda x: x['frozen_original_literal_rows'][0].reverse())
            reject('source_matrix_pin_corrupt', lambda x: x['inputs_sha256'].__setitem__(refs['source_matrix']['path'], '1' * 64))
        elif stage == 'KERNEL_GATE':
            reject('actual_target_read', lambda x: x.__setitem__('actual_target_input_read', True))
            for key in ['unique_fixture_role_records', 'strict_author_negative_cases', 'whole_prefix_resume_equalities']:
                for suffix, value in [('wrong', gate[key] + 1), ('bool', True), ('float', float(gate[key]))]:
                    reject(key + '_' + suffix, lambda x, k=key, v=value: x.__setitem__(k, v))
            reject('kernel_source_pin_corrupt', lambda x: x['inputs_sha256'].__setitem__(KERNEL, '1' * 64))
        else:
            reject('caller_source_pin_corrupt', lambda x: x['inputs_sha256'].__setitem__(SELF, '1' * 64))
    kernel.save(out / 'summary.json', dict(status='AUTHOR_RESTRICTED_THREE_LINE_CALLER_V1_CONTROLS_PENDING_INDEPENDENT_GATE',
        timestamp=datetime.now(timezone.utc).isoformat(), producer='/root/native_driver', command=[sys.executable, *sys.argv],
        cwd=str(ROOT), python=platform.python_version(), tqdm=importlib.metadata.version('tqdm'), source_reference_commit=source_commit,
        software=software, kernel_software=kernel_software, generic_fixture_positives=positives, finite_prefix_counts=fixture_counts,
        finite_prefix_resume_equalities=3, synthetic_gate_positives=3, strict_negatives=negatives,
        strict_negative_count=len(negatives), actual99graph_read=False, scientific_census_launched=False,
        independent_approval=False, target_resolution='NONE', deadline=deadline.status()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['controls', 'census'])
    parser.add_argument('--seconds', type=float, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--source-commit', required=True)
    for field in ['kernel_gate', 'caller_gate']:
        parser.add_argument('--' + field.replace('_', '-'), type=Path)
        parser.add_argument('--' + field.replace('_', '-') + '-sha256')
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='One narrow restricted three-line role census or finite caller controls; all input/gate hashes, preprocessing and saving included; no automatic retry/path loop')
    out = args.out.resolve()
    need(out.is_relative_to(ROOT) and not out.exists(), 'PATH', 'fresh bounded output directory')
    pins = {}
    def pin(relative, identity=None):
        need(deadline.status()['remaining_seconds'] > 20, 'DEADLINE', 'preservation reserve')
        path = (ROOT / relative).resolve()
        need(path.is_relative_to(ROOT) and path.is_file(), 'PATH', 'existing workspace input')
        name = path.relative_to(ROOT).as_posix()
        actual = sha(path)
        need(identity is None or actual == identity, 'IDENTITY', 'exact immutable artifact:' + name)
        need(name not in pins or pins[name] == actual, 'IDENTITY', 'stable repeated input')
        pins[name] = actual
        return path
    kernel = None
    try:
        projector, helper, engine, kernel = lib()
        for relative, identity in [(PROJECTOR, PROJECTOR_SHA), (PROJECTOR_SPEC, PROJECTOR_SPEC_SHA),
                (KERNEL, KERNEL_SHA), (KERNEL_SPEC, KERNEL_SPEC_SHA), (projector.HELPER, projector.HELPER_SHA),
                (projector.HELPER_SPEC, projector.HELPER_SPEC_SHA)]:
            pin(relative, identity)
        for relative, identity in kernel.SOFTWARE.items():
            pin(relative, identity)
        kernel_software = {**kernel.SOFTWARE, KERNEL: KERNEL_SHA, KERNEL_SPEC: KERNEL_SPEC_SHA}
        pin(SELF)
        pin(SPEC)
        software = dict(pins)
        if args.mode == 'controls':
            engineering(out, deadline, software, kernel_software, args.source_commit, projector, helper, engine, kernel)
            return
        need(all(getattr(args, field) is not None and getattr(args, field + '_sha256') is not None
                 for field in ['kernel_gate', 'caller_gate']), 'GATES', 'actual independent changed-kernel and caller controls gates')
        graph = pin(GRAPH, GRAPH_SHA)
        base, obj = projector.decode(graph.read_bytes(), helper, engine, target=True)
        input_gate = helper.loads(pin(INPUT_GATE, INPUT_GATE_SHA).read_bytes())
        review_input(input_gate, obj, projector, helper, engine)
        kernel_gate = helper.loads(pin(args.kernel_gate, args.kernel_gate_sha256).read_bytes())
        review_kernel(kernel_gate, kernel_software)
        caller_gate = helper.loads(pin(args.caller_gate, args.caller_gate_sha256).read_bytes())
        review_caller(caller_gate, software)
        for report in [input_gate, kernel_gate, caller_gate]:
            for relative, identity in report['inputs_sha256'].items():
                need(relative not in ['CLAIMS.yaml', '.git/index'], 'INPUT_ROLE', 'historical observations cannot be immutable gate inputs')
                pin(relative, identity)
        domain = kernel.restricted_domain(engine, 99, 7, base['triples'], 11)
        need(kernel.canonical(base['frozen_rows']) == kernel.canonical(engine.FROZEN_ROWS)
             and kernel.canonical(domain['base']['triples']) == kernel.canonical(base['triples']),
             'TARGET_FROZEN', 'same exact seven original root lines and literal graph')
        universe = domain['universe']
        need(len(universe['zero_neighbor_lines']) == 140 and len(universe['one_neighbor_lines']) == 84
             and domain['total'] == 7506 * len(universe['under_vertices']) * len(universe['over_vertices']),
             'TARGET_UNIVERSE', 'fresh exact target role population; no inherited U/V labels/counts')
        identity = dict(inputs_sha256=dict(pins), software=software, graph_input_path=GRAPH, graph_input_sha256=GRAPH_SHA,
            input_gate_sha256=INPUT_GATE_SHA, kernel_controls_gate_sha256=args.kernel_gate_sha256,
            caller_controls_gate_sha256=args.caller_gate_sha256, n=99, degree=7, root=11, total=domain['total'],
            source_reference_commit=args.source_commit, source_reference_scope='Published context only; exact new source/raw/gates separately pinned, availability not inferred.',
            graph_only_input=True, historical_native_state_written=False, input_provenance=obj['provenance'],
            frozen_rows=base['frozen_rows'], mutable_labels=base['mutable_labels'], universe=universe,
            question='Does this exact checked graph have a valid lambda-preserving root-R-descending proposal in this distinct-selected CN1/CN3 oriented role family? Mu may worsen.',
            role_population_scope='All declared raw roles including invalid selected repeats; not all three-line moves, a plateau or graph-space coverage.')
        manifest = kernel.enumerate_to(engine, domain, out, deadline, identity, resume=None)
        kernel.save(out / 'universe.json', universe)
        kernel.save(out / 'run_receipt.json', dict(timestamp=datetime.now(timezone.utc).isoformat(), producer='/root/native_driver',
            command=[sys.executable, *sys.argv], cwd=str(ROOT), python=platform.python_version(), tqdm=importlib.metadata.version('tqdm'),
            source_reference_commit=args.source_commit, manifest_sha256=sha(out / 'manifest.json'), universe_sha256=sha(out / 'universe.json'),
            actual_role_population=domain['total'], actual_U_size=len(universe['under_vertices']), actual_V_size=len(universe['over_vertices']),
            deadline=deadline.status(), historical_native_state_written=False, scientific_census_launched=True,
            independent_approval=False, target_resolution='NONE', overall_search_coverage='UNKNOWN; no validated denominator.'))
    except BaseException as error:
        out.mkdir(parents=True, exist_ok=True)
        record = dict(error=repr(error), inputs_sha256=pins, deadline=deadline.status(), scientific_outputs_preserved=True,
                      target_resolution='NONE', independent_approval=False)
        with (out / 'failure.json').open('x', encoding='utf8', newline='\n') as stream:
            json.dump(record, stream, indent=2)
            stream.write('\n')
        raise


if __name__ == '__main__':
    main()
