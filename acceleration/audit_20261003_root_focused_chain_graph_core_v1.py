"""Independent strict-lex graph-only core; no producer imports or execution.

Disclosed checking primitives: K topology/bitmasks, S full scalar matrix, R
literal comparison/frozen rows, G strict JSON only. No old target decoder or
mutable module-global replacement is used.
"""
import copy
import hashlib
from pathlib import PurePosixPath
import audit_20261003_root_focused_census_core_v1 as K
import audit_20261003_root_focused_core_v2 as S
import audit_20261003_root_focused_census_records_v2 as R
import audit_20261003_root_focused_neighbor_graph_v1 as G

SCHEMA = 'FROZEN_ROOT_STRICT_LEX_GRAPH_INPUT_V1'
SOURCE_ROLES = {
    'INDEPENDENT_FROZEN_ROOT_SELECTED_NEIGHBOR_TWO_LINE_V1_COMPLETE_PASS': '/root/checkpoint_audit',
    'INDEPENDENT_FROZEN_ROOT_STRICT_LEX_TWO_LINE_V1_COMPLETE_PASS': '/root/structural',
}


class AuditError(ValueError):
    def __init__(self, stage, detail):
        self.stage = stage
        super().__init__(stage + ': ' + detail)


def need(condition, stage, detail):
    if not condition:
        raise AuditError(stage, detail)


def same(left, right):
    return R.literal_equal(left, right)


def loads(raw):
    try:
        return G.loads(raw)
    except G.AuditError as error:
        raise AuditError(error.stage, 'strict independent JSON path') from error


def energy(value):
    need(type(value) is dict and set(value) == {'E_lambda', 'E_mu', 'R_root'}
         and all(type(number) is int and number >= 0 for number in value.values()),
         'ENERGY', 'three literal nonnegative integer components')


def descriptor(value):
    need(type(value) is dict and set(value) == {'path', 'sha256'}, 'PROVENANCE', 'closed descriptor')
    path, identity = value['path'], value['sha256']
    need(type(path) is str and path and not path.startswith('/') and ':' not in path
         and '\\' not in path and all(part not in ('', '.', '..', '.git') for part in path.split('/'))
         and PurePosixPath(path).as_posix() == path, 'PROVENANCE', 'canonical repository-relative public path')
    need(type(identity) is str and len(identity) == 64
         and all(character in '0123456789abcdef' for character in identity), 'PROVENANCE', 'literal SHA256')


def synthetic_provenance():
    return dict(mode='synthetic_engineering_fixture', selected_proposal_id=None,
                source_manifest=None, source_matrix=None, source_triples=None, source_complete_audit=None,
                source_baseline_metrics=None, historical_native_state_written=False,
                null_reason='Known generic engineering graph; no selected99 input or historical computation.')


def provenance(value, actual=False):
    if same(value, synthetic_provenance()):
        need(not actual, 'TARGET_SCOPE', 'synthetic fixture cannot certify a99 input')
        return
    required = {'mode', 'selected_proposal_id', 'source_manifest', 'source_matrix', 'source_triples',
                'source_complete_audit', 'source_baseline_metrics', 'historical_native_state_written'}
    need(type(value) is dict and set(value) == required
         and value['mode'] == 'actual_independently_checked_strict_lex_selection'
         and value['historical_native_state_written'] is False, 'PROVENANCE', 'graph-only closed lineage')
    need(type(value['selected_proposal_id']) is int and 0 <= value['selected_proposal_id'] < 224784,
         'PROVENANCE', 'labelled single-neighborhood selection ID')
    for field in ['source_manifest', 'source_matrix', 'source_triples']:
        descriptor(value[field])
    audit = value['source_complete_audit']
    need(type(audit) is dict and set(audit) == {'path', 'sha256', 'status'}
         and audit['status'] in SOURCE_ROLES, 'PROVENANCE', 'explicit supported complete source interface')
    descriptor({key: audit[key] for key in ['path', 'sha256']})
    energy(value['source_baseline_metrics'])
    need(value['source_baseline_metrics']['E_lambda'] == 0, 'PROVENANCE', 'lambda-zero checked source')


def decode(raw, actual=False):
    obj = loads(raw)
    fields = {'schema', 'n', 'degree', 'root', 'ordered_triples', 'frozen_rows', 'mutable_labels', 'metrics', 'provenance'}
    need(type(obj) is dict and set(obj) == fields and obj['schema'] == SCHEMA, 'GRAPH_SCHEMA', 'new closed graph-only schema')
    need(all(type(obj[key]) is int for key in ['n', 'degree', 'root']), 'GRAPH_DOMAIN', 'literal dimensions')
    provenance(obj['provenance'], actual)
    if actual:
        need((obj['n'], obj['degree'], obj['root']) == (99, 7, 11), 'TARGET_SCOPE', 'fixed local root experiment')
    try:
        base = K.from_triples(obj['ordered_triples'], obj['n'], obj['degree'], obj['root'])
    except K.CensusError as error:
        raise AuditError('TOPOLOGY_DOMAIN', 'independent complete triple topology') from error
    need(same(obj['frozen_rows'], base['frozen']) and same(obj['mutable_labels'], base['mutable']),
         'FROZEN_LABELS', 'all literal ordered root rows and mutable labels')
    energy(obj['metrics'])
    exact = dict(E_lambda=base['lambda_energy'], E_mu=base['mu_energy'], R_root=base['root_residual'])
    need(same(obj['metrics'], exact), 'EXACT_SCORES', 'whole integer scores from independent topology')
    raw_matrix = K.matrix_bytes(base['bits'])
    scalar = S.scalar_matrix(raw_matrix, obj['n'], obj['degree'], obj['root'])
    need((scalar['lambda_energy'], scalar['mu_energy'], scalar['root_residual']) == tuple(exact.values()),
         'SEPARATE_SCALAR_SCORES', 'independent full adjacency score path')
    if actual:
        need(same(base['frozen'], R.FROZEN) and len(base['triples']) == 231 and len(base['mutable']) == 224
             and len(K.labelled_universe(base)) == 224784, 'TARGET_FROZEN', 'original seven rows and complete label universe')
        prior = obj['provenance']['source_baseline_metrics']
        need(exact['E_lambda'] == 0 and (exact['R_root'], exact['E_mu']) < (prior['R_root'], prior['E_mu']),
             'LEX_PROGRESS', 'strict rootR then mu; root descent may worsen mu')
        need(hashlib.sha256(raw_matrix).hexdigest() == obj['provenance']['source_matrix']['sha256'],
             'GRAPH_MATRIX', 'exact independently selected raw matrix identity')
    return obj, base, scalar


def payload(triples, n, degree, root):
    base = K.from_triples(triples, n, degree, root)
    return dict(schema=SCHEMA, n=n, degree=degree, root=root, ordered_triples=copy.deepcopy(triples),
                frozen_rows=base['frozen'], mutable_labels=base['mutable'],
                metrics=dict(E_lambda=base['lambda_energy'], E_mu=base['mu_energy'], R_root=base['root_residual']),
                provenance=synthetic_provenance())


def review_source(gate, manifest, refs):
    need(type(gate) is dict and gate.get('status') in SOURCE_ROLES
         and gate.get('producer') == '/root/native_driver' and gate.get('verifier') == SOURCE_ROLES[gate['status']]
         and gate.get('method') == 'independent_artifact_check' and gate.get('target_resolution') == 'NONE'
         and gate.get('graph_only_input') is True and gate.get('historical_native_state_written') is False,
         'SOURCE_REVIEW', 'precise complete-source status-specific independent role')
    need(type(gate.get('complete_labelled_proposals')) is int and gate['complete_labelled_proposals'] == 224784
         and type(gate.get('mutable_label_count')) is int and gate['mutable_label_count'] == 224
         and gate.get('literal_one_move_population_only') is True and same(gate.get('frozen_original_literal_rows'), R.FROZEN),
         'SOURCE_REVIEW', 'whole literal local population')
    need(type(manifest) is dict and manifest.get('status') == 'CANDIDATE_COMPLETE_PENDING_INDEPENDENT_CHECK'
         and all(type(manifest.get(key)) is int and manifest[key] == expected
                 for key, expected in [('completed_proposals', 224784), ('population', 224784), ('starting_proposal_id', 0)])
         and type(manifest.get('parts')) is list and type(manifest.get('checkpoints')) is list
         and len(manifest['parts']) == len(manifest['checkpoints']) == 45, 'SOURCE_REVIEW', 'declared complete45part source')
    selected = manifest.get('selected_proposal_id')
    need(type(selected) is int and 0 <= selected < 224784 and type(gate.get('selected_proposal_id')) is int
         and gate['selected_proposal_id'] == selected and type(gate.get('aggregate')) is dict
         and type(manifest.get('aggregate')) is dict and same(gate['aggregate'], manifest['aggregate']),
         'SOURCE_REVIEW', 'literal selected ID and all checked aggregate fields')
    identity = manifest.get('identity')
    need(type(identity) is dict and identity.get('graph_only_input') is True
         and identity.get('historical_native_state_written') is False and same(identity.get('frozen_rows'), R.FROZEN)
         and same([identity.get(key) for key in ['n', 'degree', 'root', 'total']], [99, 7, 11, 224784]),
         'SOURCE_REVIEW', 'raw source graph-only domain/history')
    need(type(gate.get('inputs_sha256')) is dict and type(refs) is dict
         and set(refs) == {'source_manifest', 'source_matrix', 'source_triples'}, 'SOURCE_REVIEW', 'direct raw input map')
    for record in refs.values():
        descriptor(record)
        need(gate['inputs_sha256'].get(record['path']) == record['sha256'], 'SOURCE_REVIEW', 'every direct artifact bound')
    return selected


def review_input(gate, obj, path, identity, projector, projector_spec, software):
    need(type(gate) is dict and same([gate.get(key) for key in ['status', 'producer', 'verifier', 'method', 'target_resolution']],
         ['INDEPENDENT_FROZEN_ROOT_STRICT_LEX_GRAPH_PROJECTION_V1_COMPLETE_PASS', '/root/native_driver', '/root/structural',
          'independent_artifact_check', 'NONE']) and gate.get('historical_native_state_written') is False
         and gate.get('graph_only_input') is True, 'INPUT_GATE', 'new honest independent graph-only roles')
    dims = dict(n=99, point_degree=7, root=11, ordered_triples=231, mutable_lines=224, frozen_lines=7)
    prov = obj['provenance']
    need(all(type(gate.get(key)) is int and gate[key] == value for key, value in dims.items())
         and type(gate.get('selected_proposal_id')) is int and gate['selected_proposal_id'] == prov['selected_proposal_id'],
         'INPUT_GATE', 'complete literal graph and selection dimensions')
    expected = {'graph_input_path': path, 'graph_input_sha256': identity}
    for field in ['source_manifest', 'source_matrix', 'source_triples', 'source_complete_audit']:
        expected[field + '_sha256'] = prov[field]['sha256']
    need(all(type(gate.get(key)) is str and gate[key] == value for key, value in expected.items()),
         'INPUT_GATE', 'all derivative/source raw identities')
    need(same(gate.get('metrics'), obj['metrics']) and same(gate.get('source_baseline_metrics'), prov['source_baseline_metrics'])
         and same(gate.get('frozen_original_literal_rows'), R.FROZEN), 'INPUT_GATE', 'full scores and original root rows')
    required = {path: identity, projector: software[projector], projector_spec: software[projector_spec]}
    required.update({prov[field]['path']: prov[field]['sha256'] for field in ['source_manifest', 'source_matrix', 'source_triples', 'source_complete_audit']})
    need(type(gate.get('inputs_sha256')) is dict and all(gate['inputs_sha256'].get(key) == value for key, value in required.items()),
         'INPUT_GATE', 'closed direct graph/source gate bindings')


def review_controls(gate, status, software):
    need(type(gate) is dict and same([gate.get(key) for key in ['status', 'producer', 'verifier', 'method', 'target_resolution']],
         [status, '/root/native_driver', '/root/structural', 'independent_artifact_check', 'NONE'])
         and type(gate.get('inputs_sha256')) is dict
         and all(gate['inputs_sha256'].get(key) == value for key, value in software.items()),
         'CONTROLS_GATE', 'changed interface exact native/structural software scope')
