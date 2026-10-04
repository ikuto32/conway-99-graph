"""Closed four-binding registrar adapter; execution requires separate Root ONE.

The immutable V23 main performs the existing schema/impact and artifact writes.
Only its disjoint V23 adapter slots are replaced in memory for this invocation.
No prior source, claim, artifact, mathematical statement or gate is rewritten.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SELF = 'acceleration/register_20261004_bound_claims_v25.py'
SPEC = 'acceleration/register_20261004_bound_claims_v25_spec.md'
DESCRIPTOR = {
    'path': 'acceleration/proposal_20261004_wave45_focal_and_rank_four_bound_claims_v1.json',
    'sha256': 'b06bc418bf7f794f9635c25780b6085b13da2d7e50351a41bc5f1ca6d8ed7eaf',
}
ANCESTRY = {
    'acceleration/register_20261004_bound_claims_v23.py':
        'fb7c9ce93c15713086d4149f15afac6e8c6c4fec978dba180012b6664a0c434d',
    'acceleration/validate_claims.py':
        'a48f55b54918b0c494e6f06f80bdcdc52f304dfc370dd25842aeae3a0f861265',
    'docs/claims.schema.json':
        '0d752f62c7c9a43c7ddc5fbfe8d2c5644eec3d70d1baea236cb290d475aa5dac',
}
EXACT = {
    'C-TARGET-INDEPENDENT-SUPPORT-FOCAL-NEIGHBOR-MATCHING-CUTS': (
        '6288d24cd39736c1577b5093d38aa514f59cfed932c78f479d99bd1f164b92c9',
        '848d35933fe2b2876ac20631a3370a73d6696cd053a7e07004b113703220a7d3'),
    'C-FIXED17-PLAIN-FOCAL-NEIGHBOR-SYSTEMS-INTEGER-FEASIBLE': (
        '320028e62a66aaf7adea1b78107c347ad21b26d8e62f0cc460ddec5cd7b5e502',
        'ae11274983db5b43834f7f8dec4f0e1945d2c53e2a391133bf8d36346378453c'),
    'C-FIXED17-FOCAL-SELECTOR-MATCHING-SYSTEMS-INTEGER-FEASIBLE': (
        '760b9bd690649617baa40659ab804fcc91c550589e4d466186af50df66153c14',
        'efde74be34983d7ededd200da5ae3d195966234ef33a4941aecab72e7112bcca'),
    'C-UNRESTRICTED-TARGET-TERNARY-DIVIDED-GRAM-FORM-RANK77': (
        '658438c82fa24b2a11cac073bfe4f47b75a6e9a4e0bef5c8c0d1799a01a282ea',
        '7ceb72cae1825ab3883ac3b6911ca6fa7fc9b334e6a0838112cbdd1f89c54b50'),
}
ROLES = {
    list(EXACT)[0]: ('/root', '/root/structural', 'independent_derivation'),
    list(EXACT)[1]: ('/root/checkpoint_audit', '/root/native_driver', 'independent_artifact_check'),
    list(EXACT)[2]: ('/root/structural', '/root/native_driver', 'independent_artifact_check'),
    list(EXACT)[3]: ('/root/structural', '/root/native_driver', 'independent_derivation'),
}
_descriptor = None
_ancestor = None
_execution_pins = {}


def need(ok, stage):
    if not ok:
        raise ValueError(stage)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def same(a, b):
    if type(a) is not type(b):
        return False
    if type(a) is dict:
        return set(a) == set(b) and all(same(a[k], b[k]) for k in a)
    if type(a) is list:
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    return a == b


def descriptor():
    global _descriptor
    if _descriptor is None:
        need(digest(ROOT/DESCRIPTOR['path']) == DESCRIPTOR['sha256'], 'V25_DESCRIPTOR_HASH')
        value = json.loads((ROOT/DESCRIPTOR['path']).read_bytes())
        need(value['schema'] == 'WAVE45_FOCAL_AND_RANK_FOUR_BOUND_CLAIMS_SOURCE_ONLY_V1'
             and type(value['record_population']) is int and value['record_population'] == 4
             and same(value['dependency_order'], list(EXACT))
             and same([r['id'] for r in value['records']], list(EXACT)), 'V25_DESCRIPTOR_POPULATION')
        for row in value['records']:
            cid = row['id']
            need(row['binding']['sha256'] == EXACT[cid][0]
                 and row['report']['sha256'] == EXACT[cid][1]
                 and (row['producer'], row['verifier'], row['method']) == ROLES[cid], 'V25_DESCRIPTOR_IDENTITIES')
        expected_roles = [dict(id=cid, binding_sha256=EXACT[cid][0], producer=ROLES[cid][0],
            verifier=ROLES[cid][1], method=ROLES[cid][2], no_generic_role_waiver=True) for cid in EXACT]
        need(same(value['exact_role_matrix'], expected_roles), 'V25_DESCRIPTOR_ROLES')
        _descriptor = value
    return _descriptor


def record(cid):
    need(cid in EXACT, 'V25_ID')
    return next(r for r in descriptor()['records'] if r['id'] == cid)


def role(cid, expected, binding):
    if cid not in EXACT:
        return False
    row = record(cid)
    need(expected == EXACT[cid][0], 'V25_BINDING_IDENTITY')
    required = {'schema', 'id', 'revision', 'claim_revision', 'status', 'review_state', 'kind',
        'basis', 'statement', 'producer', 'verifier', 'method', 'verification_timestamp',
        'report', 'report_sha256', 'scope', 'dependencies', 'target_resolution', 'assumptions', 'limitations'}
    need(type(binding) is dict and required <= set(binding), 'V25_BINDING_FIELDS')
    need(type(binding['revision']) is int and type(binding['claim_revision']) is int
         and binding['revision'] == binding['claim_revision'] == 1, 'V25_REVISION')
    need(type(binding['assumptions']) is list and all(type(x) is str for x in binding['assumptions'])
         and type(binding['limitations']) is list and all(type(x) is str for x in binding['limitations']),
         'V25_ASSUMPTIONS_LIMITATIONS')
    for key in ('id', 'revision', 'status', 'review_state', 'kind', 'basis', 'statement',
                'producer', 'verifier', 'method', 'assumptions', 'scope', 'dependencies'):
        need(same(binding[key], row[key]), 'V25_CORE_'+key)
    need(type(binding['schema']) is str and binding['schema'] == 'CLAIM_BINDING_SCHEMA2'
         and binding['status'] == 'VERIFIED' and binding['review_state'] == 'CLEAR'
         and (binding['producer'], binding['verifier'], binding['method']) == ROLES[cid]
         and binding['producer'] != binding['verifier'] and binding['target_resolution'] == 'NONE'
         and type(binding['verification_timestamp']) is str
         and binding['verification_timestamp'] == row['verification_timestamp_literal']
         and binding['report'] == row['report']['path'] and binding['report_sha256'] == EXACT[cid][1]
         and 'verification_records' not in binding, 'V25_ROLES_TIMESTAMP_REPORT')
    need(digest(ROOT/row['binding']['path']) == expected, 'V25_BINDING_BYTES')
    need(same(binding, json.loads((ROOT/row['binding']['path']).read_bytes())), 'V25_COMPLETE_BINDING')
    return True


def scope(cid, expected, binding):
    need(role(cid, expected, binding), 'V25_SCOPE_ROLE')
    value = binding['scope']
    need(type(value) is dict and set(value) == {'description', 'unrestricted_target', 'target_resolution'}
         and type(value['description']) is str and type(value['unrestricted_target']) is bool
         and value['target_resolution'] == 'NONE', 'V25_CANONICAL_SCOPE')
    return copy.deepcopy(value)


def dependencies(cid, expected, binding, claims):
    need(role(cid, expected, binding), 'V25_DEPENDENCY_ROLE')
    need(type(binding['dependencies']) is list, 'V25_DEPENDENCY_LIST')
    result = []
    for dep in binding['dependencies']:
        need(type(dep) is dict and {'id', 'revision', 'relation'} <= set(dep)
             and set(dep) <= {'id', 'revision', 'relation', 'reason'}
             and type(dep['id']) is str and type(dep['revision']) is int
             and dep['revision'] == 1 and dep['relation'] == 'uses_result', 'V25_DEPENDENCY_FIELDS')
        if 'reason' in dep:
            need(type(dep['reason']) is str, 'V25_DEPENDENCY_REASON')
        prior = [c for c in claims if c['id'] == dep['id']]
        need(len(prior) == 1 and type(prior[0]['revision']) is int
             and prior[0]['revision'] == dep['revision'] and prior[0]['status'] == 'VERIFIED'
             and prior[0]['review_state'] == 'CLEAR', 'V25_PRECEDING_VERIFIED_DEPENDENCY')
        result.append(copy.deepcopy(dep))
    return result


def evidence(cid):
    record(cid)
    pins = {DESCRIPTOR['path']: DESCRIPTOR['sha256'], **ANCESTRY, **_execution_pins}
    for path, identity in descriptor()['fresh_metadata_sha256'].items():
        need(type(path) is str and type(identity) is str and len(identity) == 64
             and all(c in '0123456789abcdef' for c in identity), 'V25_EVIDENCE_FIELDS')
        resolved = (ROOT/path).resolve()
        need(resolved.is_relative_to(ROOT) and (path not in pins or pins[path] == identity), 'V25_EVIDENCE_CONFLICT')
        pins[path] = identity
    for path, identity in pins.items():
        need(digest(ROOT/path) == identity, 'V25_METADATA_EVIDENCE_HASH')
    return pins


def report(cid, report_sha, binding, value):
    if cid not in EXACT:
        return None
    need(role(cid, EXACT[cid][0], binding), 'V25_REPORT_ROLE')
    row = record(cid)
    need(report_sha == EXACT[cid][1] and digest(ROOT/binding['report']) == report_sha, 'V25_REPORT_BYTES')
    need(same(value, json.loads((ROOT/binding['report']).read_bytes())), 'V25_COMPLETE_REPORT')
    need(value['status'] == row['report']['status'] and value['statement'] == binding['statement']
         and value['producer'] == binding['producer'] and value['verifier'] == binding['verifier']
         and value['method'] == binding['method'] and same(value['scope'], binding['scope']), 'V25_REPORT_CORE')
    evidence(cid)
    return dict(adapter_version=25, descriptor=DESCRIPTOR, recorded_binding=row['binding']['path'],
        recorded_binding_sha256=EXACT[cid][0], recorded_report=binding['report'], recorded_report_sha256=report_sha,
        recorded_binding_statement=binding['statement'], raw_statement_changed=False,
        original_binding_scope=copy.deepcopy(binding['scope']), original_report_scope=copy.deepcopy(value['scope']),
        original_dependencies=copy.deepcopy(binding['dependencies']), schema_scope=scope(cid, EXACT[cid][0], binding),
        original_verification_timestamp=binding['verification_timestamp'], theorem_verification_outcome='PASS',
        no_new_mathematical_approval=True, generic_role_waiver=False, target_resolution='NONE',
        controls_semantics=copy.deepcopy(descriptor()['controls_semantics']))


def ancestor():
    global _ancestor
    if _ancestor is None:
        for path, identity in ANCESTRY.items():
            need(digest(ROOT/path) == identity, 'V25_ANCESTOR_HASH')
        path = ROOT/'acceleration/register_20261004_bound_claims_v23.py'
        spec = importlib.util.spec_from_file_location('v25_pinned_v23_shared_main', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _ancestor = module
    return _ancestor


def bridge(module):
    # These are exactly the inherited disjoint adapter interfaces, not patches
    # to old file bytes or permission for arbitrary ROOT/Native verifier routes.
    module.V23_EXACT = dict(EXACT)
    module.v23_role = role
    module.v23_scope = scope
    module.v23_dependencies = dependencies
    module.v23_evidence = evidence
    module.v23_report = report
    module.v23_verification_outcome = lambda cid, expected, binding: (
        'PASS' if role(cid, expected, binding) else None)
    return module


def cli_order(paths, identities):
    rows = descriptor()['records']
    need(same([Path(p).resolve() for p in paths], [(ROOT/r['binding']['path']).resolve() for r in rows])
         and same(identities, [EXACT[r['id']][0] for r in rows]), 'V25_EXACT_CLI_ORDER')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', required=True, type=Path)
    ap.add_argument('--previous-sha256', required=True)
    ap.add_argument('--binding', action='append', required=True, type=Path)
    ap.add_argument('--binding-sha256', action='append', required=True)
    ap.add_argument('--source-sha256', required=True)
    ap.add_argument('--spec-sha256', required=True)
    args = ap.parse_args()
    need(digest(ROOT/SELF) == args.source_sha256 and digest(ROOT/SPEC) == args.spec_sha256,
         'V25_SOURCE_SPEC_HASH')
    _execution_pins.update({SELF: args.source_sha256, SPEC: args.spec_sha256})
    cli_order(args.binding, args.binding_sha256)
    need(args.out.resolve().is_relative_to(ROOT) and not args.out.exists(), 'V25_FRESH_OUTPUT')
    need(args.previous_sha256 == descriptor()['current_accepted_context']['ledger_sha256']
         and digest(ROOT/'CLAIMS.yaml') == args.previous_sha256, 'V25_PRIOR_LEDGER')
    module = bridge(ancestor())
    old = module.registry.read_ledger(ROOT/'CLAIMS.yaml')
    need(len(old['claims']) == 418 and dict(module.Counter(c['status'] for c in old['claims']))
         == {'VERIFIED': 409, 'CANDIDATE': 3, 'REFUTED': 6}, 'V25_PRIOR_COUNTS')
    argv = [str(ROOT/SELF), '--out', str(args.out), '--previous-sha256', args.previous_sha256]
    for path, identity in zip(args.binding, args.binding_sha256):
        argv += ['--binding', str(path), '--binding-sha256', identity]
    original = sys.argv
    try:
        sys.argv = argv
        module.main()
    finally:
        sys.argv = original


if __name__ == '__main__':
    main()
