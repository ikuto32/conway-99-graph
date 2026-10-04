"""Source-bound author controls for the closed V25 metadata callbacks only."""
import argparse
import copy
import hashlib
import importlib.util
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SELF = 'acceleration/calibrate_20261004_registrar_v25_helpers_v1.py'
SPEC = 'acceleration/calibrate_20261004_registrar_v25_helpers_v1_spec.md'
REGISTRAR = 'acceleration/register_20261004_bound_claims_v25.py'
PINS = {
    REGISTRAR: '540a1203a57e5dfd772233995c850382ce521ea9cba455c550d2b1d88cb6919b',
    'acceleration/register_20261004_bound_claims_v25_spec.md':
        '93a638cb4063a8f259500364bcd82b7392357affcf735c9321292344157d563c',
    'acceleration/proposal_20261004_wave45_focal_and_rank_four_bound_claims_v1.json':
        'b06bc418bf7f794f9635c25780b6085b13da2d7e50351a41bc5f1ca6d8ed7eaf',
    'acceleration/command_deadline.py':
        '9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9',
}


def need(ok, stage):
    if not ok:
        raise ValueError(stage)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    with Path(path).open('x', encoding='utf-8', newline='\n') as out:
        json.dump(value, out, indent=2, ensure_ascii=False)
        out.write('\n')


def context():
    return dict(head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT,
        text=True).strip(), ledger=digest(ROOT/'CLAIMS.yaml'), index=digest(ROOT/'.git/index'))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--seconds', type=float, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--source-sha256', required=True)
    ap.add_argument('--spec-sha256', required=True)
    ap.add_argument('--protected-ledger-sha256', required=True)
    ap.add_argument('--protected-index-sha256', required=True)
    ap.add_argument('--expected-head', required=True)
    args = ap.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='Closed four-ID author metadata controls only')
    out = args.out.resolve()
    need(out.is_relative_to(ROOT) and not out.exists(), 'FRESH_OUTPUT')
    out.mkdir(parents=True)
    controls, mappings = [], []
    pins = {SELF: args.source_sha256, SPEC: args.spec_sha256, **PINS}
    expected = dict(head=args.expected_head, ledger=args.protected_ledger_sha256,
        index=args.protected_index_sha256)

    def tick():
        need(deadline.status()['remaining_seconds'] > 20, 'SAVE_RESERVE')

    def case(name, expected_stage, call):
        tick()
        actual = 'PASS'
        try:
            call()
        except ValueError as exc:
            actual = str(exc)
        row = dict(index=len(controls), name=name, expected=expected_stage, actual=actual,
            match=actual == expected_stage)
        controls.append(row)
        need(row['match'], 'CONTROL_STAGE_MISMATCH:'+name)

    try:
        tick()
        need(context() == expected, 'PROTECTED_CONTEXT')
        for path, identity in pins.items():
            tick()
            need(digest(ROOT/path) == identity, 'SOURCE_PIN:'+path)
        spec = importlib.util.spec_from_file_location('v25_author_control_subject', ROOT/REGISTRAR)
        v = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(v)
        declaration = v.descriptor()
        pins.update(v.ANCESTRY)
        for path, identity in declaration['fresh_metadata_sha256'].items():
            need(path not in pins or pins[path] == identity, 'DIRECT_METADATA_CONFLICT')
            pins[path] = identity
        for path, identity in pins.items():
            tick()
            need(digest(ROOT/path) == identity, 'DIRECT_METADATA_PIN:'+path)
        # Import only the immutable metadata registrar/validator. Never call main.
        inherited = v.ancestor()
        prior = inherited.registry.read_ledger(ROOT/'CLAIMS.yaml')['claims']
        need(len(prior) == 418, 'PRIOR_418')
        records = declaration['records']
        preceding = copy.deepcopy(prior)
        for row in records:
            cid, identity = row['id'], row['binding']['sha256']
            b = json.loads((ROOT/row['binding']['path']).read_bytes())
            r = json.loads((ROOT/row['report']['path']).read_bytes())
            case(cid+':role', 'PASS', lambda: need(v.role(cid, identity, b), 'ROLE_FALSE'))
            case(cid+':scope', 'PASS', lambda: need(v.same(v.scope(cid, identity, b), row['scope']), 'SCOPE_FALSE'))
            case(cid+':report', 'PASS', lambda: mappings.append(v.report(cid, row['report']['sha256'], b, r)))
            case(cid+':dependencies', 'PASS', lambda: need(v.same(v.dependencies(cid, identity, b, preceding),
                b['dependencies']), 'DEPENDENCY_FALSE'))
            mutations = [
                ('schema_number', 'schema', 2, 'V25_ROLES_TIMESTAMP_REPORT'),
                ('wrong_id', 'id', cid+'-WRONG', 'V25_CORE_id'),
                ('revision_bool', 'revision', True, 'V25_REVISION'),
                ('revision_float', 'revision', 1.0, 'V25_REVISION'),
                ('assumptions_null', 'assumptions', None, 'V25_ASSUMPTIONS_LIMITATIONS'),
                ('assumptions_bool_member', 'assumptions', [True], 'V25_ASSUMPTIONS_LIMITATIONS'),
                ('statement', 'statement', b['statement']+' Changed.', 'V25_CORE_statement'),
                ('scope_bool_alias', 'scope', {**b['scope'], 'unrestricted_target': int(b['scope']['unrestricted_target'])}, 'V25_CORE_scope'),
                ('producer', 'producer', '/root/wrong', 'V25_CORE_producer'),
                ('verifier', 'verifier', '/root/wrong', 'V25_CORE_verifier'),
                ('method', 'method', 'unchecked', 'V25_CORE_method'),
                ('timestamp', 'verification_timestamp', b['verification_timestamp']+'Z', 'V25_ROLES_TIMESTAMP_REPORT'),
                ('status', 'status', 'REFUTED', 'V25_CORE_status'),
                ('dependency', 'dependencies', b['dependencies']+[dict(id='WRONG', revision=True, relation='uses_result')], 'V25_CORE_dependencies'),
            ]
            for name, field, replacement, stage in mutations:
                changed = copy.deepcopy(b)
                changed[field] = replacement
                case(cid+':'+name, stage, lambda changed=changed: v.role(cid, identity, changed))
            missing = copy.deepcopy(b)
            del missing['assumptions']
            case(cid+':missing_assumptions', 'V25_BINDING_FIELDS', lambda: v.role(cid, identity, missing))
            late = copy.deepcopy(b)
            late['late_unapproved_metadata'] = True
            case(cid+':late_binding_key', 'V25_COMPLETE_BINDING', lambda: v.role(cid, identity, late))
            case(cid+':wrong_binding_hash', 'V25_BINDING_IDENTITY', lambda: v.role(cid, '0'*64, b))
            wrong_report = copy.deepcopy(r)
            wrong_report['late_unapproved_metadata'] = True
            case(cid+':late_report_key', 'V25_COMPLETE_REPORT', lambda: v.report(cid, row['report']['sha256'], b, wrong_report))
            case(cid+':wrong_report_hash', 'V25_REPORT_BYTES', lambda: v.report(cid, '0'*64, b, r))
            if b['dependencies']:
                corrupted_prior = copy.deepcopy(preceding)
                target = next(c for c in corrupted_prior if c['id'] == b['dependencies'][0]['id'])
                target['status'] = 'REFUTED'
                case(cid+':refuted_dependency', 'V25_PRECEDING_VERIFIED_DEPENDENCY',
                    lambda: v.dependencies(cid, identity, b, corrupted_prior))
            preceding.append(dict(id=cid, revision=1, status='VERIFIED', review_state='CLEAR'))
        paths = [ROOT/r['binding']['path'] for r in records]
        identities = [r['binding']['sha256'] for r in records]
        case('exact_cli_order', 'PASS', lambda: v.cli_order(paths, identities))
        case('reversed_cli_order', 'V25_EXACT_CLI_ORDER', lambda: v.cli_order(list(reversed(paths)), identities))
        case('missing_cli_binding', 'V25_EXACT_CLI_ORDER', lambda: v.cli_order(paths[:-1], identities[:-1]))
        case('wrong_cli_hash', 'V25_EXACT_CLI_ORDER', lambda: v.cli_order(paths, ['0'*64]+identities[1:]))
        case('bool_numeric_alias', 'PASS', lambda: need(not v.same(True, 1), 'TYPED_EQUALITY'))
        case('unknown_id_no_role', 'PASS', lambda: need(v.role('UNAPPROVED', '0'*64, {}) is False, 'ROLE_WAIVER'))
        unchanged_main = inherited.main
        v.bridge(inherited)
        case('closed_bridge_slots', 'PASS', lambda: need(inherited.main is unchanged_main
            and inherited.v23_role is v.role and inherited.v23_scope is v.scope
            and inherited.v23_dependencies is v.dependencies and inherited.v23_evidence is v.evidence
            and inherited.v23_report is v.report and inherited.V23_EXACT == v.EXACT
            and all(inherited.v23_verification_outcome(r['id'], r['binding']['sha256'],
                json.loads((ROOT/r['binding']['path']).read_bytes())) == 'PASS' for r in records), 'BRIDGE_SLOTS'))
        actual_digest = v.digest
        actual_ancestor = v._ancestor
        try:
            v._ancestor = None
            v.digest = lambda path: '0'*64
            case('altered_inherited_source_identity', 'V25_ANCESTOR_HASH', v.ancestor)
        finally:
            v.digest = actual_digest
            v._ancestor = actual_ancestor
        need(sum(c['expected'] == 'PASS' for c in controls) == 20 and len(controls) == 103, 'CONTROL_POPULATION')
        tick()
        save(out/'controls.json', controls)
        tick()
        save(out/'mappings.json', mappings)
        tick()
        bridge_record = dict(inherited_main_file='acceleration/register_20261004_bound_claims_v23.py',
            inherited_main_bytes_sha256=v.ANCESTRY['acceleration/register_20261004_bound_claims_v23.py'],
            main_object_unchanged=True, exact_adapter_ids=list(v.EXACT), generic_role_waiver=False,
            source_AST_parsed=False, inherited_main_executed=False)
        save(out/'bridge.json', bridge_record)
        tick()
        need(context() == expected, 'CLOSING_PROTECTED_CONTEXT')
        outputs = {str(p.relative_to(ROOT)).replace('\\', '/'): digest(p)
            for p in (out/'controls.json', out/'mappings.json', out/'bridge.json')}
        tick()
        summary = dict(schema='REGISTRAR_V25_AUTHOR_HELPER_CONTROLS_V1',
            status='REGISTRAR_V25_AUTHOR_HELPER_CONTROLS_PASS', timestamp=datetime.now(timezone.utc).isoformat(),
            producer='/root/structural', verifier=None, verification_pending=True, positive_controls=20,
            strict_negative_controls=83, controls=103, all_stages_match=True, mapping_population=4,
            inputs_sha256=pins, outputs_sha256=outputs, protected_context=expected,
            registrar_main_called=False, scientific_member_hashes_checked=False, mathematical_replays=0,
            source_AST_parsed=False, ledger_mutated=False, index_mutated=False, availability_promotions=0,
            limits=['Author engineering controls only; no independent transition/math approval.',
                'In-memory mutations are source-reproducible; raw mutated binding/report copies are not separately persisted.',
                'Provisional PASS is accepted only with clean supported runtime and separate Root review.'])
        save(out/'summary.json', summary)
        tick()
    except Exception as exc:
        if not (out/'controls.json').exists():
            save(out/'controls.json', controls)
        save(out/'failure.json', dict(status='AUTHOR_CONTROLS_FAILED', exception=repr(exc), attempted=len(controls),
            mathematical_replays=0, registrar_main_called=False, actual_context=context()))
        raise


if __name__ == '__main__':
    main()
