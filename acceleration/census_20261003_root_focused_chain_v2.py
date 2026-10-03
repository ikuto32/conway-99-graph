"""One exact fixed-root census from a separately checked strict-lex graph input.

No automatic path loop. New source-only execution needs fresh independent gates.
"""
import argparse
import copy
import importlib.metadata
import importlib.util
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SELF = 'acceleration/census_20261003_root_focused_chain_v2.py'
SPEC = 'acceleration/census_20261003_root_focused_chain_v2_spec.md'
PROJECTOR = 'acceleration/project_20261003_root_focused_chain_graph_v2.py'
PROJECTOR_SHA = '5c22e4fec65ef3d95ae3f6e09023b3067b674d1a631c228e09b2282daa5d2aab'
PROJECTOR_SPEC = 'acceleration/project_20261003_root_focused_chain_graph_v2_spec.md'
PROJECTOR_SPEC_SHA = '80d5e9148bd8bf387448483e3dd470c3418dea1d7ecaeb392a9e4bf63a2ed2a3'
CONTROLS = 'INDEPENDENT_FROZEN_ROOT_STRICT_LEX_TWO_LINE_V1_CONTROLS_PASS'

class CheckError(ValueError):
    def __init__(self, stage, message):
        self.stage = stage
        super().__init__(stage + ': ' + message)

def need(ok, stage, message):
    if not ok:
        raise CheckError(stage, message)

def lib():
    import hashlib
    def digest(path):
        with path.open('rb') as stream:
            return hashlib.file_digest(stream, 'sha256').hexdigest()
    need(digest(ROOT / PROJECTOR) == PROJECTOR_SHA and digest(ROOT / PROJECTOR_SPEC) == PROJECTOR_SPEC_SHA,
         'SOURCE', 'exact new graph-only projection interface')
    spec = importlib.util.spec_from_file_location('strict_lex_graph_projection', ROOT / PROJECTOR)
    projector = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(projector)
    helper, engine = projector.lib()
    return projector, helper, engine

def review_input(gate, obj, graph_path, graph_sha, projector, helper, engine):
    need(type(gate) is dict and gate.get('status') == projector.INPUT_PASS
         and gate.get('producer') == '/root/native_driver' and gate.get('verifier') == '/root/structural'
         and gate.get('method') == 'independent_artifact_check' and gate.get('target_resolution') == 'NONE'
         and gate.get('historical_native_state_written') is False and gate.get('graph_only_input') is True,
         'INPUT_GATE', 'new strict-lex graph input independent scope and roles')
    dimensions = dict(n=99, point_degree=7, root=11, ordered_triples=231, mutable_lines=224, frozen_lines=7)
    need(all(type(gate.get(k)) is int and gate[k] == v for k, v in dimensions.items()), 'INPUT_GATE', 'literal domain dimensions')
    prov = obj['provenance']
    need(type(gate.get('selected_proposal_id')) is int and gate['selected_proposal_id'] == prov['selected_proposal_id'],
         'INPUT_GATE', 'new raw labelled selection identity')
    fields = {'graph_input_path': graph_path, 'graph_input_sha256': graph_sha,
              'source_manifest_sha256': prov['source_manifest']['sha256'],
              'source_matrix_sha256': prov['source_matrix']['sha256'],
              'source_triples_sha256': prov['source_triples']['sha256'],
              'source_complete_audit_sha256': prov['source_complete_audit']['sha256']}
    need(all(type(gate.get(k)) is str and gate[k] == v for k, v in fields.items()), 'INPUT_GATE', 'all actual selected source/derivative identities')
    need(helper.equal(gate.get('metrics'), obj['metrics'])
         and helper.equal(gate.get('source_baseline_metrics'), prov['source_baseline_metrics'])
         and helper.equal(gate.get('frozen_original_literal_rows'), engine.FROZEN_ROWS),
         'INPUT_GATE', 'all exact components/baseline/literal original frozen rows')
    needed = {graph_path: graph_sha, PROJECTOR: PROJECTOR_SHA, PROJECTOR_SPEC: PROJECTOR_SPEC_SHA}
    for key in ['source_manifest', 'source_matrix', 'source_triples', 'source_complete_audit']:
        needed[prov[key]['path']] = prov[key]['sha256']
    need(type(gate.get('inputs_sha256')) is dict
         and all(gate['inputs_sha256'].get(k) == v for k, v in needed.items()), 'INPUT_GATE', 'independent full raw/source binding')

def review_controls(gate, software):
    need(type(gate) is dict and gate.get('status') == CONTROLS and gate.get('producer') == '/root/native_driver'
         and gate.get('verifier') == '/root/structural' and gate.get('method') == 'independent_artifact_check'
         and gate.get('target_resolution') == 'NONE' and type(gate.get('inputs_sha256')) is dict,
         'CONTROLS_GATE', 'new generic caller engineering interface')
    need(all(gate['inputs_sha256'].get(k) == v for k, v in software.items()), 'CONTROLS_GATE', 'complete changed caller/projector/helper/kernel/runtime source pins')

def engineering(out, deadline, software, source_commit, projector, helper, engine):
    out.mkdir(parents=True, exist_ok=False)
    engine.engineering(out / 'unchanged_kernel', deadline, software, source_commit)
    graph_out = out / 'graph_reader'
    graph_out.mkdir()
    projector.controls(graph_out, deadline, helper, engine, dict(software))
    _, _, refs = projector.synthetic_source(engine)
    prov = dict(mode='actual_independently_checked_strict_lex_selection', selected_proposal_id=45369,
                source_manifest=refs['source_manifest'], source_matrix=refs['source_matrix'], source_triples=refs['source_triples'],
                source_complete_audit=dict(path='synthetic/source_audit.json', sha256='0' * 64, status=projector.SOURCE_STATUSES[0]),
                source_baseline_metrics=dict(E_lambda=0, E_mu=5408, R_root=10), historical_native_state_written=False)
    # Metadata-only fixture. It is never decoded as an actual graph or historic gate.
    obj = dict(metrics=dict(E_lambda=0, E_mu=5344, R_root=10), provenance=prov)
    graph_path, graph_sha = 'synthetic/graph_input.json', '0' * 64
    gate = dict(status=projector.INPUT_PASS, producer='/root/native_driver', verifier='/root/structural',
                method='independent_artifact_check', target_resolution='NONE', graph_only_input=True,
                historical_native_state_written=False, n=99, point_degree=7, root=11, ordered_triples=231,
                mutable_lines=224, frozen_lines=7, selected_proposal_id=45369,
                graph_input_path=graph_path, graph_input_sha256=graph_sha,
                source_manifest_sha256=prov['source_manifest']['sha256'], source_matrix_sha256=prov['source_matrix']['sha256'],
                source_triples_sha256=prov['source_triples']['sha256'], source_complete_audit_sha256=prov['source_complete_audit']['sha256'],
                metrics=obj['metrics'], source_baseline_metrics=prov['source_baseline_metrics'],
                frozen_original_literal_rows=copy.deepcopy(engine.FROZEN_ROWS),
                inputs_sha256={graph_path: graph_sha, PROJECTOR: PROJECTOR_SHA, PROJECTOR_SPEC: PROJECTOR_SPEC_SHA,
                              **{prov[k]['path']: prov[k]['sha256'] for k in ['source_manifest', 'source_matrix', 'source_triples', 'source_complete_audit']}})
    review_input(gate, obj, graph_path, graph_sha, projector, helper, engine)
    projector.save(out / 'synthetic_input_gate_fixture.json', dict(synthetic_engineering_fixture=True,
        actual99graph_decoded=False, object_metadata=obj, gate=gate))
    negatives = []
    def reject(label, mutate):
        need(deadline.status()['remaining_seconds'] > 20, 'DEADLINE', 'controls save reserve')
        bad = copy.deepcopy(gate)
        mutate(bad)
        projector.save(out / (label + '.json'), dict(synthetic_engineering_fixture=True, gate=bad))
        try:
            review_input(bad, obj, graph_path, graph_sha, projector, helper, engine)
        except CheckError as error:
            need(error.stage == 'INPUT_GATE', 'CONTROL', 'exact new input-gate veto')
            negatives.append(dict(case=label, stage=error.stage, outcome='REJECTED'))
            return
        raise CheckError('CONTROL', 'accepted malformed new graph gate')
    for key in ['status', 'producer', 'verifier', 'method', 'target_resolution']:
        reject('gate_wrong_' + key, lambda x, k=key: x.__setitem__(k, 'wrong'))
    reject('gate_native_history', lambda x: x.__setitem__('historical_native_state_written', True))
    reject('gate_not_graph_only', lambda x: x.__setitem__('graph_only_input', False))
    for key in ['n', 'point_degree', 'root', 'ordered_triples', 'mutable_lines', 'frozen_lines', 'selected_proposal_id']:
        reject('gate_wrong_' + key, lambda x, k=key: x.__setitem__(k, x[k] + 1))
        reject('gate_bool_' + key, lambda x, k=key: x.__setitem__(k, True))
    for key in ['graph_input_path', 'graph_input_sha256', 'source_manifest_sha256', 'source_matrix_sha256', 'source_triples_sha256', 'source_complete_audit_sha256']:
        reject('gate_wrong_' + key, lambda x, k=key: x.__setitem__(k, 'wrong'))
    reject('gate_frozen_reordered', lambda x: x['frozen_original_literal_rows'][0].reverse())
    for owner in ['metrics', 'source_baseline_metrics']:
        for key in ['E_lambda', 'E_mu', 'R_root']:
            reject('gate_wrong_' + owner + '_' + key, lambda x, o=owner, k=key: x[o].__setitem__(k, x[o][k] + 1))
        reject('gate_bool_' + owner, lambda x, o=owner: x[o].__setitem__('R_root', False))
    reject('gate_graph_pin_missing', lambda x: x['inputs_sha256'].pop(graph_path))
    reject('gate_projector_pin_missing', lambda x: x['inputs_sha256'].pop(PROJECTOR))
    reject('gate_matrix_pin_corrupt', lambda x: x['inputs_sha256'].__setitem__(prov['source_matrix']['path'], '1' * 64))
    control = dict(status=CONTROLS, producer='/root/native_driver', verifier='/root/structural',
                   method='independent_artifact_check', target_resolution='NONE', inputs_sha256=dict(software))
    review_controls(control, software)
    projector.save(out / 'synthetic_controls_gate_fixture.json', dict(synthetic_engineering_fixture=True, gate=control))
    control_negatives = []
    def control_reject(label, mutate):
        bad = copy.deepcopy(control)
        mutate(bad)
        projector.save(out / (label + '.json'), dict(synthetic_engineering_fixture=True, gate=bad))
        try:
            review_controls(bad, software)
        except CheckError as error:
            need(error.stage == 'CONTROLS_GATE', 'CONTROL', 'exact caller gate veto')
            control_negatives.append(dict(case=label, stage=error.stage, outcome='REJECTED'))
            return
        raise CheckError('CONTROL', 'accepted malformed caller gate')
    for key in ['status', 'producer', 'verifier', 'method', 'target_resolution']:
        control_reject('control_wrong_' + key, lambda x, k=key: x.__setitem__(k, 'wrong'))
    for index, key in enumerate(software):
        control_reject('control_missing_software_' + str(index), lambda x, k=key: x['inputs_sha256'].pop(k))
    control_reject('control_self_source_corrupt', lambda x: x['inputs_sha256'].__setitem__(SELF, '0' * 64))
    kernel = helper.loads((out / 'unchanged_kernel/summary.json').read_bytes())
    reader = helper.loads((out / 'graph_reader/summary.json').read_bytes())
    projector.save(out / 'summary.json', dict(status='AUTHOR_STRICT_LEX_TWO_LINE_CONTROLS_PENDING_INDEPENDENT_GATE',
        timestamp=datetime.now(timezone.utc).isoformat(), producer='/root/native_driver', source_reference_commit=source_commit,
        command=[sys.executable, *sys.argv], cwd=str(ROOT), python=platform.python_version(), tqdm=importlib.metadata.version('tqdm'),
        software=software, inputs_sha256=reader['inputs_sha256'], kernel_summary_sha256=projector.sha(out / 'unchanged_kernel/summary.json'),
        graph_reader_summary_sha256=projector.sha(out / 'graph_reader/summary.json'),
        unique_complete_proposal_records_checked=kernel['unique_complete_proposal_records_checked'],
        recorded_proposal_evaluation_calls=kernel['recorded_proposal_evaluation_calls'],
        additional_known_overlap_evaluation_calls=kernel['additional_known_overlap_evaluation_calls'],
        kernel_negative_controls=kernel['strict_negative_count'], whole_split_equal=kernel['whole_split_equal'],
        reader_positive_graphs=reader['positive_fixtures'], reader_graph_negatives=reader['graph_specific_negative_count'],
        source_review_negatives=reader['source_review_specific_negative_count'], provenance_negatives=reader['provenance_specific_negative_count'],
        progress_controls=reader['exact_progress_controls'], input_gate_synthetic_positive=1,
        input_gate_specific_negative_count=len(negatives), input_gate_specific_negatives=negatives,
        controls_gate_synthetic_positive=1, controls_gate_specific_negative_count=len(control_negatives), controls_gate_specific_negatives=control_negatives,
        actual99graph_read=False, scientific_launched=False, historical_native_state_written=False,
        independent_approval=False, target_resolution='NONE', deadline=deadline.status()))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['controls', 'census'])
    parser.add_argument('--seconds', type=float, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--source-commit', required=True)
    parser.add_argument('--experiment-step', type=int)
    for field in ['graph_input', 'input_gate', 'controls_gate']:
        parser.add_argument('--' + field.replace('_', '-'), type=Path)
        parser.add_argument('--' + field.replace('_', '-') + '-sha256')
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='One explicit strict-lex graph-input census or finite integration controls; all hashes/setup/read/records/write included; no automatic chain loop')
    out = args.out.resolve()
    need(out.is_relative_to(ROOT) and not out.exists(), 'PATH', 'fresh bounded output')
    pins = {}
    def pin(relative, identity=None):
        need(deadline.status()['remaining_seconds'] > 20, 'DEADLINE', 'preservation reserve')
        path = (ROOT / relative).resolve()
        need(path.is_relative_to(ROOT) and path.is_file(), 'PATH', 'bounded existing immutable input')
        name = path.relative_to(ROOT).as_posix()
        actual = projector.sha(path)
        need(identity is None or identity == actual, 'IDENTITY', 'exact immutable:' + name)
        need(name not in pins or pins[name] == actual, 'IDENTITY', 'stable repeated input')
        pins[name] = actual
        return path
    try:
        projector, helper, engine = lib()
        for relative, identity in [(PROJECTOR, PROJECTOR_SHA), (PROJECTOR_SPEC, PROJECTOR_SPEC_SHA),
                                  (projector.HELPER, projector.HELPER_SHA), (projector.HELPER_SPEC, projector.HELPER_SPEC_SHA),
                                  (helper.ENGINE, helper.ENGINE_SHA), (helper.ENGINE_SPEC, helper.ENGINE_SPEC_SHA)]:
            pin(relative, identity)
        pin(SELF)
        pin(SPEC)
        for relative, identity in engine.SOFTWARE.items():
            pin(relative, identity)
        software = dict(pins)
        if args.mode == 'controls':
            engineering(out, deadline, software, args.source_commit, projector, helper, engine)
            return
        need(type(args.experiment_step) is int and 1 <= args.experiment_step <= 5, 'EXPERIMENT_SCOPE', 'declared bounded path invocation1through5; not proof of previous execution')
        need(all(getattr(args, field) is not None and getattr(args, field + '_sha256') is not None
                 for field in ['graph_input', 'input_gate', 'controls_gate']), 'GATES', 'actual new graph and independent caller gates')
        graph = pin(args.graph_input, args.graph_input_sha256)
        base, obj = projector.decode(graph.read_bytes(), helper, engine, target=True)
        gate = helper.loads(pin(args.input_gate, args.input_gate_sha256).read_bytes())
        review_input(gate, obj, graph.relative_to(ROOT).as_posix(), args.graph_input_sha256, projector, helper, engine)
        control = helper.loads(pin(args.controls_gate, args.controls_gate_sha256).read_bytes())
        review_controls(control, software)
        for report in [gate, control]:
            for relative, identity in report['inputs_sha256'].items():
                need(relative not in ['CLAIMS.yaml', '.git/index'], 'INPUT_ROLE', 'historical protected observations cannot be immutable gate inputs')
                pin(relative, identity)
        identity = dict(inputs_sha256=dict(pins), software=software, n=99, degree=7, root=11, total=224784,
            source_reference_commit=args.source_commit, source_reference_scope='Published context only; new graph/code/checker/gate closure separately LOCAL_ONLY until exact publication.',
            graph_input_schema=projector.SCHEMA, graph_only_input=True, historical_native_state_written=False,
            frozen_rows=base['frozen_rows'], mutable_labels=base['mutable_labels'], input_provenance=obj['provenance'],
            bounded_experiment_declared_step=args.experiment_step, bounded_experiment_cap=5,
            bounded_experiment_position_scope='Caller declared invocation number only; no automatic loop or invented completed chain history.',
            proposal_order='lex original mutable labels i<j;selected ix,jy lex;9*pair_index+3*ix+jy',
            question='exists lambda-preserving strict rootR-descending proposal from ONE exact graph;mu may worsen. If none, selected strict(R,mu)neutral descent may seed next separately checked invocation.')
        manifest = engine.enumerate_to(base, out, deadline, identity, resume=None)
        projector.save(out / 'run_receipt.json', dict(timestamp=datetime.now(timezone.utc).isoformat(), producer='/root/native_driver',
            command=[sys.executable, *sys.argv], cwd=str(ROOT), python=platform.python_version(), tqdm=importlib.metadata.version('tqdm'),
            source_reference_commit=args.source_commit, manifest_sha256=projector.sha(out / 'manifest.json'),
            deadline=deadline.status(), historical_native_state_written=False, independently_approved_input_gate=args.input_gate_sha256,
            new_wrapper_controls_gate=args.controls_gate_sha256, declared_experiment_step=args.experiment_step,
            target_resolution='NONE', independent_approval=False, overall_search_coverage='UNKNOWN;no validated denominator.'))
    except BaseException as error:
        out.mkdir(parents=True, exist_ok=True)
        # lib authentication can fail before a projector object exists.
        record = dict(error=repr(error), inputs_sha256=pins, deadline=deadline.status(), scientific_outputs_preserved=True)
        with (out / 'failure.json').open('x', encoding='utf8', newline='\n') as stream:
            json.dump(record, stream, indent=2)
            stream.write('\n')
        raise

if __name__ == '__main__':
    main()
