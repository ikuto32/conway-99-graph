"""Generic graph-only strict (root residual, mu) census-selection projection.

Source preparation only until new independent controls and ROOT authorization.
Calls unchanged producer helpers; never invokes an old main or fabricates state.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SELF = 'acceleration/project_20261003_root_focused_chain_graph_v2.py'
SPEC = 'acceleration/project_20261003_root_focused_chain_graph_v2_spec.md'
HELPER = 'acceleration/project_20261003_root_focused_neighbor_graph_v1.py'
HELPER_SHA = '593b04087da6d54f9d25c159466100dc2b215615d088caf1af7b0eb33009353c'
HELPER_SPEC = 'acceleration/project_20261003_root_focused_neighbor_graph_v1_spec.md'
HELPER_SPEC_SHA = '9842e294d920094140776246c6a36ed2b840f948cefac5607129be23bf0864ec'
SCHEMA = 'FROZEN_ROOT_STRICT_LEX_GRAPH_INPUT_V1'
CONTROLS = 'INDEPENDENT_FROZEN_ROOT_STRICT_LEX_GRAPH_PROJECTION_V1_CONTROLS_PASS'
INPUT_PASS = 'INDEPENDENT_FROZEN_ROOT_STRICT_LEX_GRAPH_PROJECTION_V1_COMPLETE_PASS'
SOURCE_STATUSES = ('INDEPENDENT_FROZEN_ROOT_SELECTED_NEIGHBOR_TWO_LINE_V1_COMPLETE_PASS',
                   'INDEPENDENT_FROZEN_ROOT_STRICT_LEX_TWO_LINE_V1_COMPLETE_PASS')
SOURCE_CHECKER_ROLES = {SOURCE_STATUSES[0]: '/root/checkpoint_audit', SOURCE_STATUSES[1]: '/root/structural'}

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

def save(path, value):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')

def lib():
    need(sha(ROOT / HELPER) == HELPER_SHA and sha(ROOT / HELPER_SPEC) == HELPER_SPEC_SHA,
         'SOURCE', 'unchanged disclosed JSON/equality/generic-engine helpers')
    spec = importlib.util.spec_from_file_location('unchanged_graph_json_helpers', ROOT / HELPER)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    return helper, helper.lib()

def descriptor(value):
    need(type(value) is dict and set(value) == {'path', 'sha256'}, 'PROVENANCE', 'closed artifact descriptor')
    path, identity = value['path'], value['sha256']
    need(type(path) is str and path and not Path(path).is_absolute() and '\\' not in path and ':' not in path
         and '..' not in Path(path).parts and '.git' not in Path(path).parts,
         'PROVENANCE', 'repository-relative public artifact path')
    need(type(identity) is str and len(identity) == 64 and all(c in '0123456789abcdef' for c in identity),
         'PROVENANCE', 'literal lowercase SHA256 identity')

def components(value):
    need(type(value) is dict and set(value) == {'E_lambda', 'E_mu', 'R_root'}
         and all(type(v) is int and v >= 0 for v in value.values()), 'ENERGY', 'closed exact nonnegative integer components')

def improves(selected, baseline):
    return (selected['R_root'], selected['E_mu']) < (baseline['R_root'], baseline['E_mu'])

def synthetic_provenance():
    return dict(mode='synthetic_engineering_fixture', selected_proposal_id=None,
                source_manifest=None, source_matrix=None, source_triples=None, source_complete_audit=None,
                source_baseline_metrics=None, historical_native_state_written=False,
                null_reason='Known generic engineering graph; no selected99 input or historical computation.')

def provenance(value, helper, target=False):
    if helper.equal(value, synthetic_provenance()):
        need(not target, 'TARGET_SCOPE', 'generic fixture is not a99 input certificate')
        return
    keys = {'mode', 'selected_proposal_id', 'source_manifest', 'source_matrix', 'source_triples',
            'source_complete_audit', 'source_baseline_metrics', 'historical_native_state_written'}
    need(type(value) is dict and set(value) == keys
         and value['mode'] == 'actual_independently_checked_strict_lex_selection'
         and value['historical_native_state_written'] is False,
         'PROVENANCE', 'closed graph-only actual selected provenance; no manufactured native history')
    need(type(value['selected_proposal_id']) is int and 0 <= value['selected_proposal_id'] < 224784,
         'PROVENANCE', 'literal labelled selection ID')
    for key in ['source_manifest', 'source_matrix', 'source_triples']:
        descriptor(value[key])
    report = value['source_complete_audit']
    need(type(report) is dict and set(report) == {'path', 'sha256', 'status'} and report['status'] in SOURCE_STATUSES,
         'PROVENANCE', 'only explicitly supported complete finite graph-only census interfaces')
    descriptor({k: report[k] for k in ['path', 'sha256']})
    components(value['source_baseline_metrics'])
    need(value['source_baseline_metrics']['E_lambda'] == 0, 'PROVENANCE', 'lambda-zero source baseline')

def payload(base, prov):
    return dict(schema=SCHEMA, n=base['n'], degree=base['degree'], root=base['root'],
                ordered_triples=copy.deepcopy(base['triples']), frozen_rows=copy.deepcopy(base['frozen_rows']),
                mutable_labels=base['mutable_labels'][:],
                metrics=dict(E_lambda=base['lambda_energy'], E_mu=base['mu_energy'], R_root=base['root_residual']),
                provenance=prov)

def decode(raw, helper, engine, target=False):
    obj = helper.loads(raw)
    need(type(obj) is dict and set(obj) == {'schema', 'n', 'degree', 'root', 'ordered_triples',
         'frozen_rows', 'mutable_labels', 'metrics', 'provenance'} and obj['schema'] == SCHEMA,
         'GRAPH_SCHEMA', 'new closed graph-only strict-lex schema')
    need(all(type(obj[k]) is int for k in ['n', 'degree', 'root']), 'GRAPH_DOMAIN', 'literal dimensions')
    provenance(obj['provenance'], helper, target)
    if target:
        need((obj['n'], obj['degree'], obj['root']) == (99, 7, 11), 'TARGET_SCOPE', 'exact99/root11 domain')
    base = engine.domain(obj['n'], obj['degree'], obj['ordered_triples'], obj['root'])
    need(helper.equal(obj['frozen_rows'], base['frozen_rows'])
         and helper.equal(obj['mutable_labels'], base['mutable_labels']), 'GRAPH_FROZEN', 'all literal root and mutable labels')
    components(obj['metrics'])
    exact = dict(E_lambda=base['lambda_energy'], E_mu=base['mu_energy'], R_root=base['root_residual'])
    need(helper.equal(obj['metrics'], exact), 'GRAPH_ENERGY', 'fully recomputed exact components')
    if target:
        need(helper.equal(base['frozen_rows'], engine.FROZEN_ROWS) and len(base['triples']) == 231
             and len(base['mutable_labels']) == 224 and base['total'] == 224784,
             'TARGET_FROZEN', 'same original seven literal root lines and whole labelled universe')
        need(exact['E_lambda'] == 0 and improves(exact, obj['provenance']['source_baseline_metrics']),
             'LEX_PROGRESS', 'strict(R,mu) decrease; root descent qualifies even if mu worsens')
        need(hashlib.sha256(engine.adjacency_bytes(base['masks'])).hexdigest() == obj['provenance']['source_matrix']['sha256'],
             'GRAPH_MATRIX', 'all raw selected matrix bytes')
    return base, obj

def review_source(gate, manifest, descriptors, helper, engine):
    need(type(gate) is dict and gate.get('status') in SOURCE_STATUSES
         and gate.get('producer') == '/root/native_driver' and gate.get('verifier') == SOURCE_CHECKER_ROLES.get(gate.get('status'))
         and gate.get('method') == 'independent_artifact_check' and gate.get('target_resolution') == 'NONE'
         and gate.get('graph_only_input') is True and gate.get('historical_native_state_written') is False,
         'SOURCE_REVIEW', 'exact independently checked finite graph-only source scope/roles')
    need(type(gate.get('complete_labelled_proposals')) is int and gate['complete_labelled_proposals'] == 224784
         and type(gate.get('mutable_label_count')) is int and gate['mutable_label_count'] == 224
         and gate.get('literal_one_move_population_only') is True
         and helper.equal(gate.get('frozen_original_literal_rows'), engine.FROZEN_ROWS),
         'SOURCE_REVIEW', 'complete fixed original frozen-root universe only')
    need(type(manifest) is dict and manifest.get('status') == 'CANDIDATE_COMPLETE_PENDING_INDEPENDENT_CHECK'
         and type(manifest.get('completed_proposals')) is int and manifest['completed_proposals'] == 224784
         and type(manifest.get('population')) is int and manifest['population'] == 224784
         and manifest.get('starting_proposal_id') == 0 and type(manifest.get('starting_proposal_id')) is int
         and type(manifest.get('parts')) is list and type(manifest.get('checkpoints')) is list
         and len(manifest['parts']) == len(manifest['checkpoints']) == 45,
         'SOURCE_REVIEW', 'complete raw starting-zero census45parts45checkpoints')
    selected = manifest.get('selected_proposal_id')
    need(type(selected) is int and 0 <= selected < 224784 and type(gate.get('selected_proposal_id')) is int
         and gate['selected_proposal_id'] == selected and type(gate.get('aggregate')) is dict
         and type(manifest.get('aggregate')) is dict and helper.equal(gate['aggregate'], manifest['aggregate']),
         'SOURCE_REVIEW', 'actual independently checked selection and all aggregate fields')
    identity = manifest.get('identity', {})
    need(type(identity) is dict and identity.get('graph_only_input') is True and identity.get('historical_native_state_written') is False
         and helper.equal(identity.get('frozen_rows'), engine.FROZEN_ROWS)
         and helper.equal([identity.get(k) for k in ['n', 'degree', 'root', 'total']], [99, 7, 11, 224784]),
         'SOURCE_REVIEW', 'literal raw source invocation domain/history')
    need(type(gate.get('inputs_sha256')) is dict, 'SOURCE_REVIEW', 'literal independent artifact map')
    for value in descriptors.values():
        descriptor(value)
        need(gate.get('inputs_sha256', {}).get(value['path']) == value['sha256'],
             'SOURCE_REVIEW', 'independent binding of every direct selected raw artifact')
    return selected

def synthetic_source(engine):
    refs = {key: dict(path='synthetic/' + key + '.json', sha256='0' * 64)
            for key in ['source_manifest', 'source_matrix', 'source_triples']}
    aggregate = dict(best_root_residual=10, root_neutral_minimum_mu=5344)
    manifest = dict(status='CANDIDATE_COMPLETE_PENDING_INDEPENDENT_CHECK', completed_proposals=224784,
                    population=224784, starting_proposal_id=0, parts=[None] * 45, checkpoints=[None] * 45,
                    selected_proposal_id=45369, aggregate=aggregate,
                    identity=dict(graph_only_input=True, historical_native_state_written=False,
                                  frozen_rows=copy.deepcopy(engine.FROZEN_ROWS), n=99, degree=7, root=11, total=224784))
    gate = dict(status=SOURCE_STATUSES[0], producer='/root/native_driver', verifier=SOURCE_CHECKER_ROLES[SOURCE_STATUSES[0]],
                method='independent_artifact_check', target_resolution='NONE', graph_only_input=True,
                historical_native_state_written=False, complete_labelled_proposals=224784, mutable_label_count=224,
                literal_one_move_population_only=True, frozen_original_literal_rows=copy.deepcopy(engine.FROZEN_ROWS),
                selected_proposal_id=45369, aggregate=copy.deepcopy(aggregate),
                inputs_sha256={value['path']: value['sha256'] for value in refs.values()})
    return gate, manifest, refs

def controls(out, deadline, helper, engine, pins):
    positives = []
    negatives = []
    for name, (path, identity) in helper.FIXTURES.items():
        need(sha(ROOT / path) == identity, 'FIXTURE', 'preserved positive graph fixture')
        pins[path] = identity
        base = engine.domain(**helper.loads((ROOT / path).read_bytes()))
        obj = payload(base, synthetic_provenance())
        raw = (json.dumps(obj, indent=2) + '\n').encode()
        (out / (name + '.graph.json')).write_bytes(raw)
        parsed, found = decode(raw, helper, engine)
        need(helper.equal(found, obj) and engine.adjacency_bytes(parsed['masks']) == engine.adjacency_bytes(base['masks']),
             'CONTROL', 'lossless complete literal graph roundtrip')
        positives.append(name)
        if name != 'rook9':
            continue
        need((base['lambda_energy'], base['mu_energy'], base['root_residual']) == (0, 0, 0), 'CONTROL', 'known generic exact SRG rook9')
        def reject(label, stage, change=None, blob=None, target=False):
            need(deadline.status()['remaining_seconds'] > 20, 'DEADLINE', 'finite controls preservation reserve')
            bad = copy.deepcopy(obj)
            if change:
                change(bad)
            rawbad = blob if blob is not None else (json.dumps(bad, indent=2) + '\n').encode()
            (out / (label + '.json')).write_bytes(rawbad)
            try:
                decode(rawbad, helper, engine, target=target)
            except (CheckError, helper.CheckError, engine.CheckError) as error:
                need(error.stage == stage, 'CONTROL', 'exact negative stage:' + label)
                negatives.append(dict(case=label, stage=stage, outcome='REJECTED'))
                return
            raise CheckError('CONTROL', 'accepted malformed graph:' + label)
        reject('duplicate_key', 'PROJECTION_JSON', blob=b'{"n":9,"n":9}')
        reject('malformed_utf8', 'PROJECTION_JSON', blob=b'\xff')
        reject('extra_field', 'GRAPH_SCHEMA', lambda x: x.update(native_state={}))
        reject('old_schema', 'GRAPH_SCHEMA', lambda x: x.update(schema=helper.SCHEMA))
        for key in ['n', 'degree', 'root']:
            reject('bool_' + key, 'GRAPH_DOMAIN', lambda x, k=key: x.__setitem__(k, True))
        reject('duplicate_vertex', 'DOMAIN', lambda x: x['ordered_triples'][0].__setitem__(1, x['ordered_triples'][0][0]))
        reject('duplicate_line', 'DOMAIN', lambda x: x['ordered_triples'].__setitem__(1, x['ordered_triples'][0][:]))
        reject('repeated_pair', 'LINEARITY', lambda x: x['ordered_triples'].__setitem__(1, [3, 4, 0]))
        reject('point_bool', 'DOMAIN', lambda x: x['ordered_triples'][0].__setitem__(0, False))
        reject('point_range', 'DOMAIN', lambda x: x['ordered_triples'][0].__setitem__(0, 9))
        reject('missing_line', 'DEGREE', lambda x: x['ordered_triples'].pop())
        reject('reordered_frozen', 'GRAPH_FROZEN', lambda x: x['frozen_rows'][0].reverse())
        reject('missing_mutable', 'GRAPH_FROZEN', lambda x: x['mutable_labels'].pop())
        reject('bool_mutable', 'GRAPH_FROZEN', lambda x: x['mutable_labels'].__setitem__(0, True))
        for key in ['E_lambda', 'E_mu', 'R_root']:
            reject('wrong_' + key, 'GRAPH_ENERGY', lambda x, k=key: x['metrics'].__setitem__(k, x['metrics'][k] + 1))
        reject('energy_bool', 'ENERGY', lambda x: x['metrics'].__setitem__('E_mu', False))
        reject('extra_energy', 'ENERGY', lambda x: x['metrics'].update(score=0))
        reject('native_history', 'PROVENANCE', lambda x: x['provenance'].update(historical_native_state_written=True))
        reject('rook_not_target99', 'TARGET_SCOPE', target=True)
    # Exact strict progress controls are metadata examples, not historical graphs.
    progress = [dict(name='root_down_mu_worse', selected=dict(E_lambda=0, E_mu=100, R_root=1), baseline=dict(E_lambda=0, E_mu=1, R_root=2), expected=True),
                dict(name='neutral_mu_down', selected=dict(E_lambda=0, E_mu=9, R_root=10), baseline=dict(E_lambda=0, E_mu=10, R_root=10), expected=True),
                dict(name='equal_pair', selected=dict(E_lambda=0, E_mu=10, R_root=10), baseline=dict(E_lambda=0, E_mu=10, R_root=10), expected=False),
                dict(name='root_up_mu_down', selected=dict(E_lambda=0, E_mu=0, R_root=11), baseline=dict(E_lambda=0, E_mu=10, R_root=10), expected=False)]
    for record in progress:
        components(record['selected'])
        components(record['baseline'])
        need(improves(record['selected'], record['baseline']) is record['expected'], 'CONTROL', 'exact strict pair ordering')
    save(out / 'progress_controls.json', progress)
    gate, manifest, refs = synthetic_source(engine)
    need(review_source(gate, manifest, refs, helper, engine) == 45369, 'CONTROL', 'synthetic review interface positive')
    save(out / 'synthetic_source_review.json', dict(synthetic_engineering_fixture=True, actual_selected_graph_read=False,
         gate=gate, manifest=manifest, descriptors=refs,
         limitations='Typed interface controls only; null synthetic45part entries are not proof artifacts or historical full-check records.'))
    future_gate = copy.deepcopy(gate)
    future_gate.update(status=SOURCE_STATUSES[1], verifier=SOURCE_CHECKER_ROLES[SOURCE_STATUSES[1]])
    need(review_source(future_gate, manifest, refs, helper, engine) == 45369, 'CONTROL', 'separate future status-specific role')
    save(out / 'synthetic_future_source_review.json', dict(synthetic_engineering_fixture=True,
         actual_selected_graph_read=False, gate=future_gate, manifest=manifest, descriptors=refs))
    reviews = []
    def review_negative(label, mutate):
        need(deadline.status()['remaining_seconds'] > 20, 'DEADLINE', 'controls preservation reserve')
        badgate, badmanifest, badrefs = copy.deepcopy((gate, manifest, refs))
        mutate(badgate, badmanifest, badrefs)
        save(out / (label + '.json'), dict(synthetic_engineering_fixture=True, gate=badgate, manifest=badmanifest, descriptors=badrefs))
        try:
            review_source(badgate, badmanifest, badrefs, helper, engine)
        except CheckError as error:
            need(error.stage == 'SOURCE_REVIEW', 'CONTROL', 'exact complete-source veto:' + label)
            reviews.append(dict(case=label, stage=error.stage, outcome='REJECTED'))
            return
        raise CheckError('CONTROL', 'accepted malformed complete-source metadata:' + label)
    for key in ['status', 'producer', 'verifier', 'method', 'target_resolution']:
        review_negative('source_wrong_' + key, lambda g, m, r, k=key: g.__setitem__(k, 'wrong'))
    for key in ['graph_only_input', 'literal_one_move_population_only']:
        review_negative('source_false_' + key, lambda g, m, r, k=key: g.__setitem__(k, False))
    review_negative('source_native_history', lambda g, m, r: g.__setitem__('historical_native_state_written', True))
    for key in ['complete_labelled_proposals', 'mutable_label_count', 'selected_proposal_id']:
        review_negative('source_wrong_' + key, lambda g, m, r, k=key: g.__setitem__(k, g[k] + 1))
        review_negative('source_bool_' + key, lambda g, m, r, k=key: g.__setitem__(k, True))
    review_negative('source_frozen_reordered', lambda g, m, r: g['frozen_original_literal_rows'][0].reverse())
    review_negative('source_aggregate_mismatch', lambda g, m, r: g['aggregate'].__setitem__('best_root_residual', 9))
    review_negative('source_aggregate_missing', lambda g, m, r: g.pop('aggregate'))
    review_negative('source_pinmap_type', lambda g, m, r: g.__setitem__('inputs_sha256', []))
    review_negative('source_matrix_pin_missing', lambda g, m, r: g['inputs_sha256'].pop(r['source_matrix']['path']))
    review_negative('source_triples_pin_corrupt', lambda g, m, r: g['inputs_sha256'].__setitem__(r['source_triples']['path'], '1' * 64))
    review_negative('raw_incomplete', lambda g, m, r: m.__setitem__('status', 'CANDIDATE_PREFIX_PENDING_INDEPENDENT_CHECK'))
    for key in ['completed_proposals', 'population', 'starting_proposal_id']:
        review_negative('raw_wrong_' + key, lambda g, m, r, k=key: m.__setitem__(k, m[k] + 1))
        review_negative('raw_bool_' + key, lambda g, m, r, k=key: m.__setitem__(k, False))
    for key in ['parts', 'checkpoints']:
        review_negative('raw_missing_' + key, lambda g, m, r, k=key: m[k].pop())
        review_negative('raw_type_' + key, lambda g, m, r, k=key: m.__setitem__(k, 45))
    review_negative('raw_selected_mismatch', lambda g, m, r: m.__setitem__('selected_proposal_id', 0))
    review_negative('raw_identity_missing', lambda g, m, r: m.pop('identity'))
    review_negative('raw_identity_history', lambda g, m, r: m['identity'].__setitem__('historical_native_state_written', True))
    review_negative('raw_identity_frozen', lambda g, m, r: m['identity']['frozen_rows'][0].reverse())
    review_negative('raw_identity_bool_n', lambda g, m, r: m['identity'].__setitem__('n', True))
    review_negative('old_complete_structural_role', lambda g, m, r: g.__setitem__('verifier', '/root/structural'))
    review_negative('future_complete_checkpoint_role', lambda g, m, r: g.update(status=SOURCE_STATUSES[1], verifier='/root/checkpoint_audit'))
    synthetic_actual = dict(mode='actual_independently_checked_strict_lex_selection', selected_proposal_id=45369,
        source_manifest=refs['source_manifest'], source_matrix=refs['source_matrix'], source_triples=refs['source_triples'],
        source_complete_audit=dict(path='synthetic/source_audit.json', sha256='0' * 64, status=SOURCE_STATUSES[0]),
        source_baseline_metrics=dict(E_lambda=0, E_mu=5408, R_root=10), historical_native_state_written=False)
    provenance(synthetic_actual, helper)
    save(out / 'synthetic_actual_provenance.json', dict(synthetic_engineering_fixture=True,
         provenance=synthetic_actual, actual_selected_graph_read=False))
    provenance_negatives = []
    def provenance_negative(label, stage, mutate):
        bad = copy.deepcopy(synthetic_actual)
        mutate(bad)
        save(out / (label + '.json'), dict(synthetic_engineering_fixture=True, provenance=bad))
        try:
            provenance(bad, helper)
        except CheckError as error:
            need(error.stage == stage, 'CONTROL', 'exact provenance rejection:' + label)
            provenance_negatives.append(dict(case=label, stage=stage, outcome='REJECTED'))
            return
        raise CheckError('CONTROL', 'accepted malformed provenance:' + label)
    provenance_negative('prov_extra_rng', 'PROVENANCE', lambda x: x.update(rng=[1, 2, 3, 4]))
    provenance_negative('prov_history', 'PROVENANCE', lambda x: x.update(historical_native_state_written=True))
    provenance_negative('prov_unknown_mode', 'PROVENANCE', lambda x: x.update(mode='old_native_resume'))
    provenance_negative('prov_pid_bool', 'PROVENANCE', lambda x: x.update(selected_proposal_id=True))
    provenance_negative('prov_pid_negative', 'PROVENANCE', lambda x: x.update(selected_proposal_id=-1))
    provenance_negative('prov_pid_outside', 'PROVENANCE', lambda x: x.update(selected_proposal_id=224784))
    for key in ['source_manifest', 'source_matrix', 'source_triples']:
        provenance_negative('prov_path_escape_' + key, 'PROVENANCE', lambda x, k=key: x[k].__setitem__('path', '../outside'))
        provenance_negative('prov_hash_' + key, 'PROVENANCE', lambda x, k=key: x[k].__setitem__('sha256', 'bad'))
    provenance_negative('prov_drive_path', 'PROVENANCE', lambda x: x['source_matrix'].__setitem__('path', 'C:/outside'))
    provenance_negative('prov_audit_status', 'PROVENANCE', lambda x: x['source_complete_audit'].__setitem__('status', 'AUTHOR_SUCCESS'))
    provenance_negative('prov_audit_extra', 'PROVENANCE', lambda x: x['source_complete_audit'].update(approval=True))
    provenance_negative('prov_audit_hash', 'PROVENANCE', lambda x: x['source_complete_audit'].__setitem__('sha256', 'X' * 64))
    provenance_negative('prov_lambda_nonzero', 'PROVENANCE', lambda x: x['source_baseline_metrics'].__setitem__('E_lambda', 1))
    provenance_negative('prov_score_bool', 'ENERGY', lambda x: x['source_baseline_metrics'].__setitem__('R_root', False))
    provenance_negative('prov_score_negative', 'ENERGY', lambda x: x['source_baseline_metrics'].__setitem__('E_mu', -1))
    provenance_negative('prov_score_missing', 'ENERGY', lambda x: x['source_baseline_metrics'].pop('E_mu'))
    save(out / 'summary.json', dict(status='AUTHOR_STRICT_LEX_GRAPH_PROJECTION_CONTROLS_PENDING_INDEPENDENT_GATE',
         timestamp=datetime.now(timezone.utc).isoformat(), producer='/root/native_driver', positive_fixtures=positives,
         graph_specific_negative_count=len(negatives), graph_specific_negatives=negatives, exact_progress_controls=progress,
         source_review_synthetic_positive=2, source_review_specific_negatives=reviews,
         source_review_specific_negative_count=len(reviews),
         provenance_synthetic_positive=1, provenance_specific_negative_count=len(provenance_negatives),
         provenance_specific_negatives=provenance_negatives,
         inputs_sha256=pins, command=[sys.executable, *sys.argv], cwd=str(ROOT), python=platform.python_version(),
         actual_selected_graph_read=False, historical_native_state_written=False, independent_approval=False,
         scientific_launched=False, deadline=deadline.status()))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['controls', 'project'])
    parser.add_argument('--seconds', type=float, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--source-commit', required=True)
    for field in ['controls_gate', 'source_audit', 'source_manifest', 'source_matrix', 'source_triples']:
        parser.add_argument('--' + field.replace('_', '-'), type=Path)
        parser.add_argument('--' + field.replace('_', '-') + '-sha256')
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='One graph-only finite selection projection or tinycontrols; complete hash/parse/rebuild/write included, no scientific neighborhood/state/history')
    out = args.out.resolve()
    need(out.is_relative_to(ROOT) and not out.exists(), 'PATH', 'fresh bounded output')
    out.mkdir(parents=True)
    pins = {}
    def pin(relative, identity=None):
        need(deadline.status()['remaining_seconds'] > 20, 'DEADLINE', 'invocation output reserve')
        path = (ROOT / relative).resolve()
        need(path.is_relative_to(ROOT) and path.is_file(), 'PATH', 'bounded existing immutable input')
        name = path.relative_to(ROOT).as_posix()
        actual = sha(path)
        need(identity is None or actual == identity, 'IDENTITY', 'exact input:' + name)
        need(name not in pins or pins[name] == actual, 'IDENTITY', 'stable repeated input')
        pins[name] = actual
        return path
    try:
        pin(HELPER, HELPER_SHA)
        pin(HELPER_SPEC, HELPER_SPEC_SHA)
        helper, engine = lib()
        for relative, identity in [(engine.__file__, helper.ENGINE_SHA), (helper.ENGINE_SPEC, helper.ENGINE_SPEC_SHA)]:
            pin(relative, identity)
        pin(SELF)
        pin(SPEC)
        for relative, identity in engine.SOFTWARE.items():
            pin(relative, identity)
        software = dict(pins)
        if args.mode == 'controls':
            controls(out, deadline, helper, engine, pins)
            return
        need(all(getattr(args, field) is not None and getattr(args, field + '_sha256') is not None
                 for field in ['controls_gate', 'source_audit', 'source_manifest', 'source_matrix', 'source_triples']),
             'GATES', 'all exact independent controls and raw-source descriptors')
        paths = {}
        descriptors = {}
        for field in ['controls_gate', 'source_audit', 'source_manifest', 'source_matrix', 'source_triples']:
            paths[field] = pin(getattr(args, field), getattr(args, field + '_sha256'))
            descriptors[field] = dict(path=paths[field].relative_to(ROOT).as_posix(), sha256=pins[paths[field].relative_to(ROOT).as_posix()])
        control = helper.loads(paths['controls_gate'].read_bytes())
        need(control.get('status') == CONTROLS and control.get('producer') == '/root/native_driver'
             and control.get('verifier') == '/root/structural' and control.get('method') == 'independent_artifact_check'
             and control.get('target_resolution') == 'NONE', 'CONTROLS_GATE', 'new generic projection engineering interface')
        for relative, identity in software.items():
            need(control.get('inputs_sha256', {}).get(relative) == identity, 'CONTROLS_GATE', 'all changed software exact pins')
        gate = helper.loads(paths['source_audit'].read_bytes())
        manifest = helper.loads(paths['source_manifest'].read_bytes())
        rawrefs = {k: descriptors[k] for k in ['source_manifest', 'source_matrix', 'source_triples']}
        selected_id = review_source(gate, manifest, rawrefs, helper, engine)
        for report in [control, gate]:
            for relative, identity in report['inputs_sha256'].items():
                need(relative not in ['CLAIMS.yaml', '.git/index'], 'INPUT_ROLE', 'historical state is not an immutable dependency')
                pin(relative, identity)
        selected = helper.loads(paths['source_triples'].read_bytes())
        need(type(selected) is dict and set(selected) == {'n', 'degree', 'root', 'frozen_rows', 'mutable_labels', 'triples', 'proposal_id'}
             and type(selected['proposal_id']) is int and selected['proposal_id'] == selected_id,
             'SOURCE_TRIPLES', 'literal independently checked selection ID and ordered graph')
        baseline = dict(E_lambda=manifest['baseline']['lambda_energy'], E_mu=manifest['baseline']['mu_energy'], R_root=manifest['baseline']['root_residual'])
        components(baseline)
        base = engine.domain(selected['n'], selected['degree'], selected['triples'], selected['root'])
        prov = dict(mode='actual_independently_checked_strict_lex_selection', selected_proposal_id=selected_id,
                    source_manifest=descriptors['source_manifest'], source_matrix=descriptors['source_matrix'],
                    source_triples=descriptors['source_triples'], source_complete_audit=dict(**descriptors['source_audit'], status=gate['status']),
                    source_baseline_metrics=baseline, historical_native_state_written=False)
        obj = payload(base, prov)
        raw = (json.dumps(obj, indent=2) + '\n').encode()
        decode(raw, helper, engine, target=True)
        need(helper.equal(selected['frozen_rows'], base['frozen_rows']) and helper.equal(selected['mutable_labels'], base['mutable_labels'])
             and engine.adjacency_bytes(base['masks']) == paths['source_matrix'].read_bytes(), 'SOURCE_MATRIX', 'entire selected raw matrix/order/frozen rows')
        (out / 'graph_input.json').write_bytes(raw)
        save(out / 'summary.json', dict(status='CANDIDATE_STRICT_LEX_GRAPH_INPUT_V1_PENDING_INDEPENDENT_FULL_CHECK',
             timestamp=datetime.now(timezone.utc).isoformat(), producer='/root/native_driver', source_reference_commit=args.source_commit,
             graph_input=dict(path=(out / 'graph_input.json').relative_to(ROOT).as_posix(), sha256=sha(out / 'graph_input.json'), bytes=len(raw)),
             metrics=obj['metrics'], source_baseline_metrics=baseline, selected_proposal_id=selected_id,
             ordered_triples=231, frozen_lines=7, mutable_lines=224, inputs_sha256=pins,
             historical_native_state_written=False, scientific_launched=False, independent_approval=False, target_resolution='NONE',
             command=[sys.executable, *sys.argv], cwd=str(ROOT), python=platform.python_version(), deadline=deadline.status(),
             limitations=['One lossless derivative from an independently checked finite census selection; no chain history/counters/RNG/native state invented.',
                          'A bounded path is maintained in separately reviewed actual run records; this adapter never automatically launches any neighborhood.',
                          'No whole plateau, unrestricted exclusion, support uniqueness or general minimum claim. New input needs independent full projection check before science.']))
    except BaseException as error:
        save(out / 'failure.json', dict(error=repr(error), inputs_sha256=pins, deadline=deadline.status(), scientific_launched=False, outputs_preserved=True))
        raise

if __name__ == '__main__':
    main()
