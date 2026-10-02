"""Editorial V2: explicit control/verification records for the same r1 exclusion."""
import argparse
import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
OLD_BINDING = 'acceleration/results/20261003_fixed_two_line_census_binding01/claim_binding_schema2_draft.json'
OLD_SHA = 'c0fe9d893c139df760e0038a24abae1a8a9bf1ecdb5763b22a52564ae19edbd8'
OLD_CLOSURE = 'acceleration/results/20261003_fixed_two_line_census_binding01/closure.json'
OLD_CLOSURE_SHA = '9621e396390d2204eac50e8485175c69de1871de661ad094cdfb5659e39e36b0'
REPORT = 'acceleration/results/20261003_independent_review/two_line_full01/summary.json'
REPORT_SHA = '1d3cecc2fd8d3e689966a334af59a9af7d0a2e8c66b356b98484aef3ed79e589'
CAL = 'acceleration/results/20261003_independent_review/two_line_records_calibration01/summary.json'
CAL_SHA = 'ab51f23bbbd09e6d0b94ce861b391bb349cd583bc62f69439e2da1afb66af3b6'


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seconds', required=True, type=float)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='Metadata only: preserve approved r1 statement, expose existing nested controls and two exact revision/artifact-bound verification records with unavailablefield reasons')
    out = args.out.resolve()
    need(out.is_relative_to(ROOT) and not out.exists(), 'Fresh metadata derivative output')
    out.mkdir(parents=True)
    pins = {}

    def pin(name, wanted=None):
        need(not deadline.status()['stop_required'] and deadline.status()['remaining_seconds'] > 20, 'Not completed within allocated metadata budget')
        path = (ROOT/name).resolve()
        need(not Path(name).is_absolute() and path.is_relative_to(ROOT) and path.is_file(), 'Exact local input '+name)
        identity = sha(path)
        need(wanted is None or identity == wanted, 'Exact input identity '+name)
        need(name not in pins or pins[name] == identity, 'Consistent repeated pin '+name)
        pins[name] = identity
        return json.loads(path.read_bytes()) if path.suffix == '.json' else None

    old = pin(OLD_BINDING, OLD_SHA)
    pin(OLD_CLOSURE, OLD_CLOSURE_SHA)
    report = pin(REPORT, REPORT_SHA)
    cal = pin(CAL, CAL_SHA)
    need(old['id'] == 'C-HYPERGRAPH-WEIGHT60-WARM01-FIXED-V2-TWO-LINE-CENSUS'
         and old['claim_revision'] == old['revision'] == 1 and old['dependencies'] == [], 'Same exact initial claim r1')
    need(old['report_sha256'] == REPORT_SHA and old['pre_output_calibration']['sha256'] == CAL_SHA
         and old['scope']['unrestricted_target'] is False and old['producer'] == '/root/native_driver'
         and old['verifier'] == '/root' and old['method'] == 'independent_artifact_check', 'Approved exact statement/roles/scope source')
    need(cal['complete_unique_tiny_records'] == 270 and cal['complete_records_including_split_replay'] == 540
         and cal['complete_new_fullmatrix_and_scalar_comparisons'] == 96
         and len(cal['strict_record_corruptions']) == 15 and cal['pre_full_scientific_output'] is True,
         'Exact existing nested calibration counts, not invented new checks')
    need(report['complete_proposals_checked'] == 239085 and report['complete_universe'] is True
         and report['absence_of_descent_asserted'] is True, 'Exact existing full verification scope')
    for name, identity in old['inputs_sha256'].items():
        pin(name, identity)
    own = Path(__file__).relative_to(ROOT).as_posix()
    pin(own)
    pin(own.replace('.py','_spec.md'))
    binding = copy.deepcopy(old)
    binding['updated_at'] = datetime.now(timezone.utc).isoformat()
    binding['editorial_binding_version'] = 2
    binding['previous_editorial_binding'] = dict(path=OLD_BINDING,sha256=OLD_SHA,
        statement_scope_roles_dependencies_unchanged=True,
        original_ROOT_editorial_review='Direct parent message accepted original c0fe exact statement/scope/exclusion; this derivative changes control record presentation only and requires review of its new bytes.')
    binding['inputs_sha256'] = pins
    binding['controls'] = dict(
        pre_output_independent=dict(report=CAL,report_sha256=CAL_SHA,
            complete_unique_tiny_records=cal['complete_unique_tiny_records'],
            complete_records_including_split_replay=cal['complete_records_including_split_replay'],
            complete_fullmatrix_and_scalar_valid_comparisons=cal['complete_new_fullmatrix_and_scalar_comparisons'],
            known_overlap_checked=cal['known_overlap_checked'],strict_saved_corruptions=cal['strict_record_corruptions'],
            strict_corruption_count=len(cal['strict_record_corruptions']),pre_full_scientific_output=True),
        full_independent=dict(report=REPORT,report_sha256=REPORT_SHA,
            complete_proposals_checked=report['complete_proposals_checked'],complete_universe=True,
            raw_parts=48,checkpoint_prefixes=48,all_ties_and_selected_raw_objects=True,
            complete_trajectory_checked=False,trajectory_reason='This is a static full neighbor census, not an annealer trajectory audit.'))
    records = []
    for label, record, path, identity, scope in [
        ('pre_output_checker_calibration',cal,CAL,CAL_SHA,
         'Finite270 unique rook/prism proposals/540 whole-split stream records,96 scalar/matrix valid comparisons and15 actual saved-stream/metadata corruptions. No target-input census was inspected.'),
        ('complete_static_artifact_check',report,REPORT,REPORT_SHA,
         'Every239085 original fixed-input proposal, all48rawparts/checkpoints/ties/selected rawmatrix/triples and exact no-descent outcome. No other starting graph or move space.')]:
        records.append(dict(claim_id=old['id'],claim_revision=1,record_kind=label,
            verifier=record['verifier'],method=record['method'],outcome='PASS',
            timestamp=record['timestamp'],report=path,report_sha256=identity,scope=scope,
            artifact_hashes=record['inputs_sha256'],command=record['command'],cwd=record['cwd'],
            versions=dict(python=record['python'],numpy=record['numpy']),
            shared_components=record['shared_components'],independent_of_discovery_producer=True,
            external_review=False,verification_level='Independent artifact checking by a separate authored dense/scalar path; not peer review or schema validation.'))
    binding['verification_records'] = records
    binding['unavailable_information'] = [
        dict(field='verifier_source_commit',value=None,
            reason='Neither actual ROOT calibration nor full report records a verifier Git commit; exact source/spec SHA256 and commands are preserved.'),
        dict(field='hardware_cpu_model',value=None,
            reason='Producer receipt and checking reports do not record a CPU model. Exact finite integer correctness has no hardware-dependent acceptance threshold, and no performance guarantee is claimed.'),
        dict(field='individual_human_reviewer_identity',value=None,
            reason='Evidence records agent role /root only; no human identity or external reviewer is invented.'),
        dict(field='external_peer_review_record',value=None,
            reason='No external peer review was performed or evidenced by these internal reports.'),
        dict(field='random_seed',value=None,
            reason='The producer performs deterministic complete enumeration; no RNG exists for this command.')]
    need(all(binding[key] == old[key] for key in ['id','revision','claim_revision','statement','scope','dependencies',
        'assumptions','status','review_state','kind','basis','producer','verifier','method','report','report_sha256']),
        'Editorial derivative leaves mathematical claim/approval scope unchanged')
    save(out/'claim_binding_schema2_draft.json',binding)
    save(out/'closure.json',dict(schema='FIXED_TWO_LINE_CENSUS_BINDING_EDITORIAL_V2_CLOSURE',
        claim_id=old['id'],claim_revision=1,source_commit=old['source_commit'],
        records=[dict(path=name,sha256=identity,bytes=(ROOT/name).stat().st_size,availability='LOCAL_ONLY') for name,identity in sorted(pins.items())],
        claim_binding=dict(path=(out/'claim_binding_schema2_draft.json').relative_to(ROOT).as_posix(),sha256=sha(out/'claim_binding_schema2_draft.json')),
        new_mathematical_checks=False,statement_unchanged=True,ledger_edited=False))
    print(json.dumps(dict(binding_sha256=sha(out/'claim_binding_schema2_draft.json'),closure_sha256=sha(out/'closure.json'),records=len(pins),new_mathematical_checks=False,ledger_edited=False)))


if __name__ == '__main__':
    main()
