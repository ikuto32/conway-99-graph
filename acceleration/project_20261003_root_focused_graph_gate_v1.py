"""Narrow editorial interface projection of one preserved ROOT input audit.

This is metadata/identity work, never a fresh mathematical verification.
"""
import argparse
import copy
import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SELF = 'acceleration/project_20261003_root_focused_graph_gate_v1.py'
SPEC = 'acceleration/project_20261003_root_focused_graph_gate_v1_spec.md'
ORIGINAL = 'acceleration/results/20261003_independent_review/root_focused_start_full01/summary.json'
ORIGINAL_SHA = '97c251ab0e5383303f4ec19852b3f6a05b4e1f768a742efa10adabf0d0e29d34'
CALIBRATION = 'acceleration/results/20261003_independent_review/root_focused_start_calibration01/summary.json'
CALIBRATION_SHA = 'a27dedb5d81e6b56ca2e021ec666838a10bfb7f8c0a5e026b713c47fad3a23ad'
EXPORT = 'acceleration/results/20261003_root_focused_start_export01/'
RAW_PINS = {
    EXPORT+'graph_input.txt': '203e9a28106304476efeb92bae143be448e0423e87e227cf2a0ec85852ded30e',
    EXPORT+'selected.adj': 'a55f63d6423b23f0945699ad5bc8265081a88f0b1cb92b751247d32203be8a63',
    EXPORT+'ordered_triples.json': '39707948648e5a07c88cd495abb8f401e5acfb154821036a557434f732826a73',
    EXPORT+'selection.json': '9a58ae85bdd2fed2bafc4dd6bc4c33c62457f2879948bad9effdbeda44581472',
}
SCORES = dict(n=99, degree=7, root=11, lambda_energy=0, mu_energy=3484,
              root_residual=50, root_objective=50, base_energy=3484)
COUNTS = dict(mutable_line_count=224, complete_raw_parts=96,
              authenticated_raw_labels=478170, eligible_labelled_graphs_checked=373,
              unique_eligible_graphs=220, minimum_root_mu_tie_count=6,
              ordered_target_identity_mismatches=4760, complete_dense_products=376)
FROZEN = [dict(index=i, points=row) for i, row in [
    (15, [59, 3, 11]), (18, [78, 11, 62]), (22, [37, 18, 11]),
    (57, [11, 77, 15]), (61, [88, 11, 12]), (82, [11, 23, 96]),
    (154, [11, 93, 46])]]
ENVIRONMENT = ['acceleration/command_deadline.py', 'acceleration/run_compute_command.py',
               'pyproject.toml', 'uv.lock']


class ProjectionError(ValueError):
    def __init__(self, stage):
        super().__init__(stage)
        self.stage = stage


def need(value, stage):
    if not value:
        raise ProjectionError(stage)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def unique(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, 'JSON_DUPLICATE')
        result[key] = value
    return result


def decode(raw):
    result = json.loads(raw, object_pairs_hook=unique)
    need(type(result) is dict, 'JSON_OBJECT')
    return result


def pin_shape(name, identity):
    need(type(name) is str and bool(name) and '\\' not in name, 'PIN_PATH')
    path = PurePosixPath(name)
    need(not path.is_absolute() and '..' not in path.parts and ':' not in name, 'PIN_PATH')
    need(type(identity) is str and len(identity) == 64
         and all(c in '0123456789abcdef' for c in identity), 'PIN_HASH')


def validate_report(report):
    need(type(report) is dict, 'JSON_OBJECT')
    need(report.get('status') == 'INDEPENDENT_ROOT_FOCUSED_START_V1_COMPLETE_FINITE_SELECTION_PASS', 'STATUS')
    need(report.get('verifier') == '/root' and report.get('producer') == '/root/checkpoint_audit', 'ROLE')
    need('method' not in report, 'HISTORICAL_METHOD_FIELD')
    need(report.get('target_resolution') == 'NONE'
         and report.get('overall_search_coverage') == 'UNKNOWN; no validated denominator.', 'SCOPE')
    need(report.get('graph_input') == EXPORT+'graph_input.txt'
         and report.get('graph_input_sha256') == RAW_PINS[EXPORT+'graph_input.txt']
         and report.get('selected_matrix_sha256') == RAW_PINS[EXPORT+'selected.adj']
         and report.get('selected_triples_sha256') == RAW_PINS[EXPORT+'ordered_triples.json']
         and report.get('selection_sha256') == RAW_PINS[EXPORT+'selection.json'], 'IDENTITY')
    scores = report.get('exact_scores')
    need(type(scores) is dict, 'SCORES')
    for key, value in SCORES.items():
        need(type(scores.get(key)) is int, 'SCORE_TYPE')
        need(scores[key] == value, 'SCORES')
    need(scores.get('matrix_sha256') == RAW_PINS[EXPORT+'selected.adj']
         and scores.get('support_pair_uniqueness_assumed') is False, 'SCORES')
    for key, value in COUNTS.items():
        need(type(report.get(key)) is int, 'COUNT_TYPE')
        need(report[key] == value, 'COUNTS')
    frozen = report.get('frozen_root_rows')
    need(type(frozen) is list and len(frozen) == 7, 'FROZEN')
    for row in frozen:
        need(type(row) is dict and type(row.get('index')) is int
             and type(row.get('points')) is list and len(row['points']) == 3
             and all(type(v) is int for v in row['points']), 'FROZEN_TYPE')
    need(frozen == FROZEN, 'FROZEN')
    selected = report.get('selected_proposal')
    need(type(selected) is dict and type(selected.get('proposal_id')) is int
         and selected['proposal_id'] == 25587 and selected.get('census') == 'neighbor'
         and selected.get('adjacency_sha256') == RAW_PINS[EXPORT+'selected.adj'], 'SELECTED')
    controls = report.get('controls')
    need(type(controls) is dict and type(controls.get('positive_controls')) is int
         and controls['positive_controls'] == 5 and type(controls.get('strict_negative_count')) is int
         and controls['strict_negative_count'] == 15
         and type(controls.get('strict_negative_controls')) is list
         and len(controls['strict_negative_controls']) == 15
         and controls.get('all_products_exact') is True, 'CONTROL_SCOPE')
    pins = report.get('inputs_sha256')
    need(type(pins) is dict and bool(pins), 'PIN_MAP')
    for name, identity in pins.items():
        pin_shape(name, identity)
    need('CLAIMS.yaml' not in pins and '.git/index' not in pins, 'UNEXPECTED_MUTABLE_OBSERVATION')
    for name, identity in {**RAW_PINS, CALIBRATION: CALIBRATION_SHA}.items():
        need(pins.get(name) == identity, 'PIN_BINDING')
    return True


def synthetic_report():
    # This hand-defined metadata fixture is explicitly not a graph/certificate.
    return dict(synthetic_metadata_fixture=True,
        status='INDEPENDENT_ROOT_FOCUSED_START_V1_COMPLETE_FINITE_SELECTION_PASS',
        producer='/root/checkpoint_audit', verifier='/root', target_resolution='NONE',
        overall_search_coverage='UNKNOWN; no validated denominator.', graph_input=EXPORT+'graph_input.txt',
        graph_input_sha256=RAW_PINS[EXPORT+'graph_input.txt'], selected_matrix_sha256=RAW_PINS[EXPORT+'selected.adj'],
        selected_triples_sha256=RAW_PINS[EXPORT+'ordered_triples.json'], selection_sha256=RAW_PINS[EXPORT+'selection.json'],
        exact_scores={**SCORES, 'matrix_sha256': RAW_PINS[EXPORT+'selected.adj'], 'support_pair_uniqueness_assumed': False},
        **COUNTS, frozen_root_rows=copy.deepcopy(FROZEN),
        selected_proposal=dict(census='neighbor', proposal_id=25587, adjacency_sha256=RAW_PINS[EXPORT+'selected.adj']),
        controls=dict(positive_controls=5, strict_negative_count=15, all_products_exact=True,
                      strict_negative_controls=[dict(label='synthetic_'+str(i), error='synthetic_not_an_execution') for i in range(15)]),
        inputs_sha256={**RAW_PINS, CALIBRATION: CALIBRATION_SHA})


def write(path, value):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def calibration(out, deadline):
    good = synthetic_report()
    validate_report(good)
    write(out/'positive_synthetic_metadata.json', good)
    additional = copy.deepcopy(good)
    additional['editorial_note'] = 'Noncritical historical fields are preserved, not interpreted as mathematical claims.'
    validate_report(additional)
    write(out/'positive_editorial_extra.json', additional)
    cases = []
    def check(label, stage, change):
        need(not deadline.status()['stop_required'], 'DEADLINE')
        item = copy.deepcopy(good)
        change(item)
        write(out/('negative_'+label+'.json'), item)
        try:
            validate_report(item)
        except ProjectionError as error:
            need(error.stage == stage, 'WRONG_NEGATIVE_STAGE')
            cases.append(dict(label=label, exact_stage=stage))
        else:
            raise ProjectionError('CORRUPTION_ACCEPTED')
    for label, value, stage in [
        ('status', 'UNSAT', 'STATUS'), ('verifier', '/root/native_driver', 'ROLE'),
        ('producer', '/root/native_driver', 'ROLE'), ('target_resolution', 'VERIFIED', 'SCOPE'),
        ('overall_search_coverage', '100%', 'SCOPE'), ('graph_input_sha256', '0'*64, 'IDENTITY')]:
        check(label, stage, lambda x, k=label, v=value: x.__setitem__(k, v))
    check('invented_historical_method', 'HISTORICAL_METHOD_FIELD', lambda x: x.__setitem__('method', 'independent_artifact_check'))
    for key in ['n', 'degree', 'root', 'lambda_energy', 'mu_energy', 'root_residual', 'root_objective']:
        check('score_'+key, 'SCORES', lambda x, k=key: x['exact_scores'].__setitem__(k, SCORES[k]+1))
    check('boolean_lambda', 'SCORE_TYPE', lambda x: x['exact_scores'].__setitem__('lambda_energy', False))
    check('support_uniqueness_claim', 'SCORES', lambda x: x['exact_scores'].__setitem__('support_pair_uniqueness_assumed', True))
    check('changed_population', 'COUNTS', lambda x: x.__setitem__('authenticated_raw_labels', 478171))
    check('boolean_count', 'COUNT_TYPE', lambda x: x.__setitem__('minimum_root_mu_tie_count', True))
    check('frozen_literal', 'FROZEN', lambda x: x['frozen_root_rows'][0]['points'].__setitem__(0, 58))
    check('frozen_bool_label', 'FROZEN_TYPE', lambda x: x['frozen_root_rows'][0]['points'].__setitem__(0, True))
    check('selected_id', 'SELECTED', lambda x: x['selected_proposal'].__setitem__('proposal_id', 25588))
    check('control_count', 'CONTROL_SCOPE', lambda x: x['controls'].__setitem__('strict_negative_count', 14))
    check('control_product_flag', 'CONTROL_SCOPE', lambda x: x['controls'].__setitem__('all_products_exact', False))
    check('missing_raw_pin', 'PIN_BINDING', lambda x: x['inputs_sha256'].pop(EXPORT+'graph_input.txt'))
    check('wrong_raw_pin', 'PIN_BINDING', lambda x: x['inputs_sha256'].__setitem__(EXPORT+'graph_input.txt', '1'*64))
    check('absolute_pin', 'PIN_PATH', lambda x: x['inputs_sha256'].__setitem__('/private', '0'*64))
    check('parent_pin', 'PIN_PATH', lambda x: x['inputs_sha256'].__setitem__('../private', '0'*64))
    check('uppercase_hash', 'PIN_HASH', lambda x: x['inputs_sha256'].__setitem__('extra', 'A'*64))
    check('unexpected_ledger', 'UNEXPECTED_MUTABLE_OBSERVATION', lambda x: x['inputs_sha256'].__setitem__('CLAIMS.yaml', '0'*64))
    for label, raw, stage in [('duplicate_key', b'{"a":1,"a":2}', 'JSON_DUPLICATE'), ('array_top', b'[]', 'JSON_OBJECT')]:
        (out/('negative_'+label+'.json')).write_bytes(raw)
        try:
            decode(raw)
        except ProjectionError as error:
            need(error.stage == stage, 'WRONG_NEGATIVE_STAGE')
            cases.append(dict(label=label, exact_stage=stage))
        else:
            raise ProjectionError('CORRUPTION_ACCEPTED')
    return dict(status='ROOT_FOCUSED_GRAPH_GATE_V1_AUTHOR_SYNTHETIC_CALIBRATION_PASS',
        positive_controls=2, strict_negative_controls=len(cases), cases=cases,
        synthetic_only=True, actual_ROOT_report_read=False, actual_graph_checked=False,
        independent_approval=False, new_mathematical_verification=False)


def filehash(path, deadline):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        while block := stream.read(1024*1024):
            need(not deadline.status()['stop_required'] and deadline.status()['remaining_seconds'] > 5, 'DEADLINE')
            h.update(block)
    return h.hexdigest()


def adapt(args, out, deadline):
    need(args.calibration is not None and args.calibration_sha256 is not None, 'CALIBRATION_ARGUMENTS')
    pins = {}
    def pin(name, wanted=None):
        path = (ROOT/name).resolve()
        need(path.is_relative_to(ROOT), 'PIN_PATH')
        actual = filehash(path, deadline)
        need(wanted is None or actual == wanted, 'RAW_HASH')
        pins[name] = actual
        return actual
    for name in [SELF, SPEC, *ENVIRONMENT]:
        pin(name)
    calpath = args.calibration.resolve()
    need(calpath.is_relative_to(ROOT), 'PIN_PATH')
    calname = calpath.relative_to(ROOT).as_posix()
    pin(calname, args.calibration_sha256)
    author = decode(calpath.read_bytes())
    need(author.get('status') == 'ROOT_FOCUSED_GRAPH_GATE_V1_AUTHOR_SYNTHETIC_CALIBRATION_PASS'
         and author.get('positive_controls') == 2 and author.get('strict_negative_controls') == 31
         and author.get('synthetic_only') is True and author.get('independent_approval') is False,
         'CALIBRATION_SCOPE')
    for name in [SELF, SPEC, *ENVIRONMENT]:
        need(author['inputs_sha256'].get(name) == pins[name], 'CALIBRATION_SOURCE')
    pin(ORIGINAL, ORIGINAL_SHA)
    original = decode((ROOT/ORIGINAL).read_bytes())
    validate_report(original)
    for name, identity in original['inputs_sha256'].items():
        pin(name, identity)
    need(pins[EXPORT+'graph_input.txt'] == RAW_PINS[EXPORT+'graph_input.txt'], 'PIN_BINDING')
    record = dict(status='INDEPENDENT_ROOT_FOCUSED_GRAPH_INPUT_V1_PASS', method='independent_artifact_check',
        verifier='/root', interface_projection_producer='/root/native_driver', timestamp=datetime.now(timezone.utc).isoformat(),
        inputs_sha256=pins, original_independent_report=dict(path=ORIGINAL, sha256=ORIGINAL_SHA,
            status=original['status'], verifier=original['verifier'], producer=original['producer'],
            command=original['command'], timestamp=original['timestamp'], source_commit=original['source_commit']),
        editorial_field_projection=dict(schema='EXACT_ROOT_GRAPH_INPUT_GATE_INTERFACE_V1',
            status='New canonical interface label for the exact original graph-input scope; original report bytes/status are unchanged.',
            method='New umbrella interface field describes the original separately implemented ROOT artifact check; absent from original report. The adapter does metadata/identity checking only.'),
        graph_input=original['graph_input'], graph_input_sha256=original['graph_input_sha256'],
        exact_scores={k: original['exact_scores'][k] for k in SCORES}, frozen_root_rows=original['frozen_root_rows'],
        mutable_line_count=224, original_verified_population=COUNTS, controls=original['controls'],
        author_calibration=dict(path=calname, sha256=args.calibration_sha256),
        new_mathematical_verification_performed=False, source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True, timeout=5).strip(),
        scope='Only the exact independently checked ROOT graph-input203e, selected matrix a55f/root11/frozen seven literal rows/224mutable lines and original finite selection. No new graph, optimization, support-uniqueness implication or target resolution.',
        target_resolution='NONE', shared_components=original['shared_components']+['Metadata projection reuses original immutable report and raw hash identities; does not import or reexecute ROOT mathematical checker or exporter.'],
        limitations=original['limitations']+['This is an editorial execution-interface projection after ROOT explicit review; no new independent mathematical calculation is claimed.'],
        deadline=deadline.status())
    write(out/'gate.json', record)
    return dict(status='ROOT_FOCUSED_GRAPH_GATE_INTERFACE_PROJECTION_PRODUCED', gate=out.relative_to(ROOT).as_posix()+'/gate.json',
                gate_sha256=filehash(out/'gate.json', deadline), new_mathematical_verification=False)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode', choices=['calibration', 'adapt'])
    p.add_argument('--seconds', required=True, type=float)
    p.add_argument('--out', required=True, type=Path)
    p.add_argument('--calibration', type=Path)
    p.add_argument('--calibration-sha256')
    args = p.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='Narrow graph-gate metadata projection/synthetic controls only;100worker20reserve under separately supervised120outer; no new mathematical replay/native/scientific launch')
    out = args.out.resolve()
    need(out.is_relative_to(ROOT) and not out.exists(), 'FRESH_OUTPUT')
    out.mkdir(parents=True)
    try:
        result = calibration(out, deadline) if args.mode == 'calibration' else adapt(args, out, deadline)
        result.update(timestamp=datetime.now(timezone.utc).isoformat(), command=[sys.executable, *sys.argv], cwd=str(ROOT),
            python=platform.python_version(), inputs_sha256={name: filehash(ROOT/name, deadline) for name in [SELF, SPEC, *ENVIRONMENT]},
            target_resolution='NONE', deadline=deadline.status())
        write(out/'summary.json', result)
        print(json.dumps(dict(status=result['status'], summary_sha256=filehash(out/'summary.json', deadline))))
    except BaseException as error:
        write(out/'failure.json', dict(error=repr(error), deadline=deadline.status(), outputs_preserved=True, new_mathematical_verification=False))
        raise


if __name__ == '__main__':
    main()
