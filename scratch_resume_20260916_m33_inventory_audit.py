"""Independent certificate replay and inverse whole-document m33 ledger audit.

No inventory producer, solver, or runner is imported. The historical catalog
auditor reconstructs representative identities independently of search output.
"""
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import scratch_root_e72_source150_small5_aggregate_audit as foundation

BEFORE = Path('scratch_root_e72_complete_coverage_inventory.json')
AFTER = Path('scratch_resume_20260916_e72_complete_coverage_inventory.json')
CERTIFICATE = Path('scratch_resume_20260916_small5_m33_complete_audit.json')
OUTPUT = Path('scratch_resume_20260916_m33_inventory_delta_audit.json')
BEFORE_SHA = 'A9F2F186B6818E5A4B953607EB419B1CBE7744BED1E715E965BAE2C451A91D98'
CERTIFICATE_SHA = '90B2D1FD30D58B63092900BE225247322FFE652D5B34367001EA664AA5A6B929'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load(path):
    return json.loads(path.read_bytes())


def verify_certificate():
    require(sha(BEFORE) == BEFORE_SHA, 'Historical ledger changed')
    before = load(BEFORE)
    for name, digest in before['inputs'].items():
        require(sha(Path(name)) == digest, f'Historical evidence changed: {name}')
    require(sha(CERTIFICATE) == CERTIFICATE_SHA, 'Immutable m33 certificate changed')
    certificate = load(CERTIFICATE)
    require(certificate['status'] == 'SOURCE150_SINGLE_MACRO_JOINT_PRIMARY_INDEPENDENT_AUDIT_PASS', 'Certificate status')
    require((certificate['source_row_index'], certificate['macro'], certificate['Q']) == (150, [3, 3], 4), 'Certificate macro')
    require((certificate['catalog_orbits'], certificate['catalog_coverage']) == (116, 8192), 'Certificate coverage')
    require(certificate['status_histogram'] == {'UNSAT': 116, 'SAT': 0, 'UNKNOWN': 0}, 'Certificate histogram')
    require(certificate['status_mass'] == {'UNSAT': 8192, 'SAT': 0, 'UNKNOWN': 0}, 'Certificate masses')
    require(certificate['evidence_class'] == 'exact_solver_free_finite_local_CSP', 'Evidence class')
    require(certificate['DRAT_certificate_present'] is False and certificate['solver_or_runner_imported'] is False, 'Evidence boundary')
    require(certificate['mode'] == dict(ordinary_local_pair=True, ordinary_local_pair_every_depth=True,
        ordinary_joint_map=True, node_cap=0, joint_map_node_cap=0, ordinary_joint_map_unknowns_relaxed_as_pass=0, projection=[]), 'Search mode')
    source_paths = {
        'solver_sha256': Path('scratch_theory_e72_source150_synchronized_config_csp.py'),
        'runner_sha256': Path('scratch_root_e72_source150_small5_joint_primary_runner.py'),
        'audit_source_sha256': Path('scratch_resume_20260916_small5_partial_audit.py'),
        'foundation_sha256': Path(foundation.__file__),
    }
    for key, path in source_paths.items():
        require(sha(path) == certificate[key], f'Frozen code changed: {path}')
    expected_inputs = {str(p): sha(p) for p in (foundation.LOCAL, foundation.CATALOG, foundation.GRAM,
                                               foundation.FIBRE_FILTER, foundation.CONFIG_FRONTIER)}
    require(certificate['inputs'] == expected_inputs, 'Certificate input domain or hashes')
    catalog = load(foundation.CATALOG)
    canonical = [r for r in catalog['macro_entries'] if r['signature_stabilizer_canonical']]
    require(len(canonical) == 163 and sum(r['signature_orbit_labelled_coverage'] for r in canonical) == 141545472, 'Catalog partition')
    selected = [r for r in canonical if (r['source_row_index'], r['state_orbit_number'], r['signature_stabilizer_orbit_number']) == (150, 3, 3)]
    require(len(selected) == 1 and selected[0]['signature_orbit_labelled_coverage'] == 8192, 'Macro catalog mass')
    representatives = foundation.independently_reconstruct_records()[(3, 3)]
    require(len(representatives) == 116 and sum(int(r['orbit_size']) for r in representatives) == 8192, 'Representative catalog')
    require([r['record_number'] for r in certificate['records']] == list(range(116)), 'Record coverage')
    require(len({r['mask_hex'] for r in certificate['records']}) == 116, 'Distinct representatives')
    artifacts = {}
    for start in range(0, 116, 8):
        stop = min(start + 8, 116)
        matches = [r for r in certificate['shards'] if r['task'] == f'3:3:{start}:{stop}']
        require(len(matches) == 1, 'Shard partition')
        shard = matches[0]
        path = Path(f'scratch_theory_e72_source150_sync_jointprimary_small5_m33_r{start}_{stop}.json')
        require(shard['path'] == str(path) and sha(path) == shard['sha256'], 'Shard path/hash')
        document = load(path)
        artifacts[str(path)] = (shard, document)
        require(document['status'] == 'EXACT_SYNCHRONIZED_CONFIG_CSP_SLICE_COMPLETE', 'Incomplete shard')
        require(document['inputs'] == expected_inputs, 'Shard inputs')
        summary = document['summary']
        require(summary['wanted_macros'] == [[3, 3]] and summary['available_orbits_in_wanted_macros'] == 116, 'Shard macro')
        require((summary['slice_start'], summary['slice_stop']) == (start, stop), 'Shard bounds')
        require(summary['explicit_record_selection'] == summary['fixed_block_projection'] == [], 'Restricted projection')
        require(all(summary[k] is True for k in ('ordinary_local_pair_filter_enabled', 'ordinary_local_pair_every_depth_enabled', 'ordinary_joint_map_filter_enabled')), 'Shard filter mode')
        require(summary['ordinary_joint_map_unknowns_relaxed_as_pass'] == 0, 'Relaxed UNKNOWN')
        require([r[0] for r in document['results']] == list(range(start, stop)), 'Shard result coverage')
        mass = sum(int(representatives[i]['orbit_size']) for i in range(start, stop))
        require(summary['input_orbits'] == shard['records'] == stop-start, 'Shard count')
        require(summary['input_mass'] == summary['UNSAT_mass'] == mass and summary['SAT_mass'] == summary['UNKNOWN_mass'] == 0, 'Shard masses')
        require(summary['status_histogram'] == shard['status_histogram'] == {'UNSAT': stop-start}, 'Shard histogram')
        require(shard['status_mass'] == {'UNSAT': mass}, 'Certificate shard mass')
    require(len(certificate['shards']) == len(artifacts) == 15, 'Unexpected shard')
    for record, representative in zip(certificate['records'], representatives):
        number = record['record_number']
        require(record['mask_hex'] == representative['mask_hex'] and record['orbit_size'] == int(representative['orbit_size']) and record['Q'] == int(representative['Q']) == 4, 'Representative identity')
        require(record['status'] == 'UNSAT' and record['artifact'] in artifacts, 'Record artifact/status')
        shard, document = artifacts[record['artifact']]
        require(record['sha256'] == shard['sha256'], 'Record artifact hash')
        rows = [r for r in document['results'] if r[0] == number]
        require(len(rows) == 1 and rows[0][:6] == [number, record['mask_hex'], record['orbit_size'], 4, [3, 3], 'UNSAT'], 'Recorded UNSAT result')
    return before, certificate


def partition(inventory):
    require(inventory['status'] == 'COMPLETE_E72_COVERAGE_INVENTORY_PASS', 'Inventory status')
    buckets, counts = inventory['buckets'], inventory['global']
    require(len({r['name'] for r in buckets}) == len(buckets), 'Duplicate bucket')
    drat = sum(r['coverage'] for r in buckets if 'DRAT' in r['status'] or r['status'] == 'FORMAL_AUDIT_PASS')
    exact = sum(r['coverage'] for r in buckets if r['status'].startswith('EXACT_'))
    terminal = sum(r['coverage'] for r in buckets if r['status'].startswith('TERMINAL_'))
    unresolved = sum(r['coverage'] for r in buckets if r['status'] == 'OPEN')
    require(drat == counts['DRAT_backed_coverage'] == 135098368, 'DRAT accounting')
    require(terminal == counts['computational_terminal_UNSAT_without_checked_proof'] == 1163264, 'Unproved terminal accounting')
    require(exact == counts['exact_executable_non_DRAT_coverage'] and unresolved == counts['unresolved_or_pending_coverage'], 'Coverage accounting')
    require(drat + exact + terminal == counts['classified_nonopen_coverage'], 'Classified coverage')
    require(sum(r['coverage'] for r in buckets) == drat + exact + terminal + unresolved == counts['catalog_coverage'] == 141545472, 'Global partition')
    rows = inventory['source150']['macro_rows']
    require(sum(r['coverage'] for r in rows) == inventory['source150']['input_coverage'] == 2244608, 'Source partition')
    require(all(r['excluded_coverage'] + r['open_coverage'] == r['coverage'] for r in rows), 'Macro partition')
    require(sum(r['open_coverage'] for r in rows) == inventory['source150']['open_coverage'], 'Source open coverage')


def main():
    before, certificate = verify_certificate()
    after = load(AFTER)
    partition(before)
    partition(after)
    restored = deepcopy(after)
    require(restored['inputs'].pop(str(CERTIFICATE)) == CERTIFICATE_SHA, 'Successor evidence hash')
    source = restored['source150']
    require(source.pop('m33_joint_primary_additional_rejected_coverage') == 8192, 'New macro credit')
    require(source.pop('m33_joint_primary_audit') == str(CERTIFICATE), 'Certificate provenance')
    require(source.pop('m33_joint_primary_audit_sha256') == CERTIFICATE_SHA, 'Certificate provenance hash')
    rows = [r for r in source['macro_rows'] if r['macro'] == [3, 3]]
    require(rows == [dict(macro=[3, 3], coverage=8192, status='EXACT_SYNCHRONIZED_LOCAL_CSP_ENUM_REJECTED', excluded_coverage=8192, open_coverage=0)], 'Only m33 is eligible')
    rows[0].update(status='OPEN', excluded_coverage=0, open_coverage=8192)
    source['open_coverage'] += 8192
    positions = [i for i, r in enumerate(restored['buckets']) if r['name'] == 'source150_m33_joint_primary_rejected']
    require(len(positions) == 1, 'New bucket multiplicity')
    index = positions[0]
    require(restored['buckets'].pop(index) == dict(name='source150_m33_joint_primary_rejected', coverage=8192, status='EXACT_SOLVER_FREE_LOCAL_CSP_JOINT_MAP_PRIMARY'), 'New evidence bucket')
    require(restored['buckets'][index]['name'] == 'source150_open', 'Bucket placement')
    restored['buckets'][index]['coverage'] += 8192
    restored['global']['classified_nonopen_coverage'] -= 8192
    restored['global']['unresolved_or_pending_coverage'] += 8192
    restored['global']['exact_executable_non_DRAT_coverage'] -= 8192
    require(restored == before, 'Unexpected whole-document change outside m33 transition')
    require((after['global']['unresolved_or_pending_coverage'], after['source150']['open_coverage'], after['global']['exact_executable_non_DRAT_coverage']) == (442368, 20480, 4841472), 'Unexpected final coverage')
    require(sha(BEFORE) == BEFORE_SHA, 'Historical inventory bytes changed during audit')
    result = dict(status='INDEPENDENT_E72_M33_ONLY_SUCCESSOR_INVENTORY_DELTA_AUDIT_PASS',
        inputs_sha256={str(p): sha(p) for p in (BEFORE, AFTER, CERTIFICATE, Path(__file__))},
        only_changed_macro=[150, 3, 3], new_exact_non_DRAT_coverage=8192,
        independently_reconstructed_catalog_orbits=116, independently_checked_shards=15,
        historical_inventory_inputs_hash_checked=25, whole_document_inverse_equals_historical_inventory=True,
        historical_inventory_bytes_preserved=True, partial_mass_counted_separately=False,
        previously_credited_m10_and_m03_unchanged=True, DRAT_coverage_unchanged=135098368,
        terminal_without_checked_proof_coverage_unchanged=1163264, total_partition_coverage=141545472,
        exact_executable_non_DRAT_coverage_before_after=[4833280, 4841472],
        source150_open_coverage_before_after=[28672, 20480], global_unresolved_coverage_before_after=[450560, 442368],
        inventory_producer_solver_or_runner_imported=False, central_inventory_written=False,
        scope='Only complete source150 macro (3,3) is transferred once into exact executable non-DRAT coverage. Restricted E72 accounting; no complete E72 or Conway nonexistence proof.')
    if OUTPUT.exists():
        require(load(OUTPUT) == result, 'Existing audit differs')
    else:
        with OUTPUT.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
