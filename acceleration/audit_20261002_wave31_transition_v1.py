"""Independent read-only four-claim ledger transition and literal union audit."""
import argparse
import copy
import hashlib
import json
import platform
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / 'acceleration/results/20261002_wave31_registration02'
EXPECTED = {'C-FIXED-HADAMARD-EXACT-EIGHT-PREFIX64-BATCH05-LITERAL-PROFILE-EXCLUSIONS', 'C-WAVE147-ALL-STORED-PAIR-ROOT-COEFFICIENT-RECONSTRUCTION', 'C-ORDER8-MARKED-EXTENSION-SELECTED-RELAXATION-INTEGER-ENDPOINT-WITNESS', 'C-POLICY-AWARE-EXACT-EIGHT-NATIVE-DRIVER-CONTROLS'}


def need(ok, why):
    if not ok:
        raise ValueError(why)


class UniqueLoader(yaml.SafeLoader):
    pass


def unique_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        need(key not in result, 'duplicate YAML key ' + str(key))
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def indexed(records):
    out = {}
    for record in records:
        need(record['id'] not in out, 'duplicate record ID')
        out[record['id']] = record
    return out


def transition(before, after):
    old, new = indexed(before['claims']), indexed(after['claims'])
    need(set(new) - set(old) == EXPECTED and set(old) <= set(new), 'exact four new IDs and no deletion')
    need(all(old[key] == new[key] for key in old), 'all existing claim bytes-as-data remain unchanged')
    old_artifacts, artifacts = indexed(before['artifacts']), indexed(after['artifacts'])
    need(set(old_artifacts) <= set(artifacts) and all(old_artifacts[key] == artifacts[key] for key in old_artifacts), 'all existing artifact records preserved')
    for field in ['schema_version', 'archives', 'target', 'editorial_migrations']:
        need(before[field] == after[field], 'unchanged historical/target/migration field ' + field)
    need(after['target']['status'] == 'UNKNOWN' and after['target']['overall_search_coverage'] is None, 'unresolved target and unknown denominator retained')
    for cid in EXPECTED:
        claim = new[cid]
        need(claim['revision'] == 1 and claim['status'] == 'VERIFIED' and claim['review_state'] == 'CLEAR', 'new revision1 independently approved recorded claim')
        need(claim['scope']['unrestricted_target'] is False and claim['scope']['target_resolution'] == 'NONE', 'no target resolution or scope expansion')
        need(any(record['claim_revision'] == 1 and record['outcome'] == 'PASS' and record['method'] in {'independent_artifact_check', 'independent_derivation'} for record in claim['verification']), 'new current-revision independent PASS')
        for dependency in claim['dependencies']:
            need(dependency['id'] in new and dependency['revision'] == new[dependency['id']]['revision'] and new[dependency['id']]['status'] == 'VERIFIED' and new[dependency['id']]['review_state'] == 'CLEAR', 'exact live verified dependency pin')
    return old, new, artifacts


def union_batches(batches, universe):
    seen, bytes_total = {}, 0
    for name, summary in batches:
        records = summary['case_records']
        need(len(records) == summary['completed_proof_replays'] and summary.get('target_resolution') is False, 'complete saved literal proof record scope')
        for row in records:
            cid = row['case_id']
            need(cid in universe and cid not in seen, 'literal universe member and distinct disjoint union')
            outcome = row.get('verification_outcome', row.get('outcome'))
            need(outcome == 'UNSAT_VERIFIED', 'only actually independently checked UNSAT outcomes counted')
            replay = row.get('complete_independent_replay', row.get('replay'))
            need(replay['accepted'] is True and replay['actual_exit_code'] == 0, 'complete successful saved replay receipt')
            proof_bytes = row.get('proof_bytes', row.get('trace', {}).get('bytes'))
            need(type(proof_bytes) is int and proof_bytes > 0, 'complete raw proof size recorded')
            bytes_total += proof_bytes
            seen[cid] = {'batch': name, 'proof_bytes': proof_bytes, 'case_index': row['case_index']}
    return seen, bytes_total


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    pins = {}
    def pin(p, expected=None):
        p = p.resolve()
        with p.open('rb') as stream:
            actual = hashlib.file_digest(stream, 'sha256').hexdigest()
        need(expected is None or actual == expected, 'actual artifact identity ' + p.name)
        pins[p.relative_to(ROOT).as_posix()] = actual
        return actual
    def load(p, expected=None):
        pin(p, expected)
        return json.loads(p.read_bytes())
    try:
        before_path, after_path = REG / 'CLAIMS.before.yaml', ROOT / 'CLAIMS.yaml'
        old_sha = pin(before_path, '9e76cdb8efa4ee9fca25243b461002720b9d387acf00381f0893c01bb5655719')
        new_sha = pin(after_path, 'e55403664288e5595316b07a2772735a35dd4de1503239992e7ca7d496c9c423')
        before = yaml.load(before_path.read_text(encoding='utf8'), Loader=UniqueLoader)
        after = yaml.load(after_path.read_text(encoding='utf8'), Loader=UniqueLoader)
        old, new, artifacts = transition(before, after)
        report = load(REG / 'summary.json')
        need(report['previous_ledger_sha256'] == old_sha and report['ledger_sha256'] == new_sha and set(report['new_claim_ids']) == EXPECTED, 'actual registration snapshot identities')
        evidence_paths = {}
        for cid in EXPECTED:
            claim = new[cid]
            for aid in claim['evidence']:
                artifact = artifacts[aid]
                pin(ROOT / artifact['path'], artifact['sha256'])
                need(artifact['availability'] == 'LOCAL_ONLY', 'new evidence availability explicitly local only')
                evidence_paths[aid] = ROOT / artifact['path']
            for review in claim['verification']:
                need(review['claim_revision'] == claim['revision'], 'review bound exact current revision')
                for aid, expected in review['artifact_hashes'].items():
                    need(artifacts[aid]['sha256'] == expected, 'review hash resolves exact registered artifact')
                need(review['scope'] == claim['scope']['description'], 'review binds exact declared scope')
        proof = load(evidence_paths['wave31-proof-audit'])
        binding = load(evidence_paths['wave31-proof-binding'])
        cid = 'C-FIXED-HADAMARD-EXACT-EIGHT-PREFIX64-BATCH05-LITERAL-PROFILE-EXCLUSIONS'
        need(new[cid]['statement'] == binding['statement'] and new[cid]['scope'] == binding['scope'] and new[cid]['dependencies'] == binding['dependencies'], 'exact proof statement/scope/dependency transported without broadening')
        need(proof['status'] == 'INDEPENDENT_EXACT_EIGHT_POLICY_LITERAL_PROOFS_PASS' and proof['claim_id'] == cid and proof['claim_revision'] == 1 and proof['completed_proof_replays'] == 64 and proof['proof_bytes'] == 164530579, 'exact complete new batch proof facts')
        coefficients = load(evidence_paths['wave31-coefficient-audit'])
        need(coefficients['status'] == 'PASS_COMPLETE_STORED_COEFFICIENTS' and coefficients['all_records'] == 2414 and coefficients['all_nonzero_upper_entries'] == 272054 and all(row['result'] == 'ALL_EXACT_MATCH' for row in coefficients['family_results']), 'complete stated stored coefficient population')
        coef_manifest = load(evidence_paths['wave31-coefficient-manifest'])
        pin(ROOT / coef_manifest['checker']['path'], coef_manifest['checker']['sha256'])
        for descriptor in coef_manifest['inputs']:
            pin(ROOT / descriptor['path'], descriptor['sha256'])
        null = load(evidence_paths['wave31-null-audit'])
        need(null['status'] == 'INDEPENDENT_ORDER8_SELECTED_RELAXATION_INTEGER_NULL_PASS' and null['variables'] == 1223 and null['complete_reconstructed_equations'] == null['exact_zero_residuals'] == 4543 and null['nonnegative_integer_counts'] is True and null['exact_N3_count'] == 4158, 'exact literal relaxation endpoint facts')
        need(all(null['moments'][name]['PSD'] is True and null['moments'][name]['exact_rank'] == 1 and null['moments'][name]['dimension'] == count for name, count in [('ordered_edge', 66), ('ordered_nonedge', 87)]), 'both exact explicit moment dimensions/ranks')
        for name, expected in null['input_hashes'].items():
            pin(ROOT / name, expected)
        driver = load(evidence_paths['wave31-driver-audit'])
        containment = load(evidence_paths['wave31-containment-audit'])
        need(driver['status'] == 'INDEPENDENT_EXACT_EIGHT_POLICY_NATIVE_DRIVER_PASS' and driver['target_resolution'] is False and driver['new_solver_calls'] == 0 and containment['status'] == 'INDEPENDENT_LINUX_COMMAND_CONTAINMENT_PASS', 'new driver control approval exact recorded scope')
        stop = load(ROOT / 'acceleration/results/20261001_user_stop/checkpoint.json')
        universe = load(ROOT / 'acceleration/results/20260930_exact_eight_campaign_preparation/campaign_manifest.json')
        universe_ids = {row['case_id'] for row in universe['records']}
        need(len(universe_ids) == universe['universe_size'] == 792, 'frozen finite literal denominator')
        batches = []
        for descriptor in stop['completed_literal_batches']:
            batches.append((descriptor['path'], load(ROOT / descriptor['path'], descriptor['sha256'])))
        prior_union, prior_bytes = union_batches(batches, universe_ids)
        union, proof_bytes = union_batches([*batches, ('batch05_new', proof)], universe_ids)
        need(len(prior_union) == 316 and prior_bytes == 908646622 and len(union) == 380 and proof_bytes == 1073177201 and len(universe_ids - set(union)) == 412, 'independently recalculated disjoint saved-record union')
        need(report['distinct_literal_exclusions'] == len(union) and report['unresolved_literal_cases'] == 412 and report['complete_proof_bytes'] == proof_bytes, 'milestone counts derive exact independently checked record union')
        # These controls falsify bookkeeping errors; no mathematical replay.
        rejected = []
        for label, mutation in [('old_claim_changed', lambda data: data['claims'][0].update(revision=999)), ('broad_new_target_scope', lambda data: next(row for row in data['claims'] if row['id'] in EXPECTED)['scope'].update(target_resolution='NEGATIVE')), ('duplicate_claim_id', lambda data: data['claims'].append(copy.deepcopy(data['claims'][-1])))]:
            damaged = copy.deepcopy(after)
            mutation(damaged)
            try:
                transition(before, damaged)
            except ValueError:
                rejected.append(label)
            else:
                raise ValueError('accepted transition corruption ' + label)
        try:
            union_batches([*batches, batches[0]], universe_ids)
        except ValueError:
            rejected.append('duplicate_literal_batch')
        else:
            raise ValueError('accepted overlapping union')
        try:
            yaml.load('key: 1\nkey: 2\n', Loader=UniqueLoader)
        except ValueError:
            rejected.append('duplicate_yaml_key')
        else:
            raise ValueError('accepted duplicate YAML key')
        for p in [Path(__file__), ROOT / 'uv.lock', ROOT / 'pyproject.toml', ROOT / 'docs/CLAIMS_SCHEMA.md']:
            pin(p)
        summary = {'status': 'INDEPENDENT_WAVE31_EXACT_LEDGER_TRANSITION_PASS', 'timestamp': datetime.now(timezone.utc).isoformat(), 'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), 'command': [sys.executable, *sys.argv], 'cwd': str(ROOT), 'python': platform.python_version(), 'yaml_version': yaml.__version__, 'verifier': '/root/checkpoint_audit', 'method': 'independent_artifact_check', 'inputs_sha256': pins, 'before_ledger_sha256': old_sha, 'after_ledger_sha256': new_sha, 'unchanged_existing_claims': len(old), 'new_claim_ids': sorted(EXPECTED), 'claims': len(new), 'status_counts': dict(Counter(claim['status'] for claim in new.values())), 'verified_clear': sum(claim['status'] == 'VERIFIED' and claim['review_state'] == 'CLEAR' for claim in new.values()), 'independent_literal_union': {'population': 792, 'unit': 'Distinct frozen literal representatives on one fixed support, counted by stable full-count-profile case ID', 'previous': 316, 'new': 64, 'current': 380, 'unresolved': 412, 'proof_bytes': proof_bytes, 'overlap': []}, 'rejected_corruption_controls': rejected, 'target_resolution': after['target']['status'], 'overall_search_coverage': 'UNKNOWN; no validated denominator.', 'new_solver_calls': 0, 'new_proof_replays': 0, 'mathematical_replays': 0, 'limitations': ['This is a read-only exact registry/evidence/union impact review, not new mathematical verification.', 'The underlying independent audit records supply proof/math checks; all historical proof bytes are not replayed again.', 'The finite literal union is not target-wide coverage and is not expanded to relabellings.', 'All new evidence remains LOCAL_ONLY; hashes do not establish public replay.', 'No registrar or schema validator implementation is imported/executed.']}
        with (args.out / 'summary.json').open('x', encoding='utf8') as stream:
            json.dump(summary, stream, indent=2)
            stream.write('\n')
        with (args.out / 'literal_union.json').open('x', encoding='utf8') as stream:
            json.dump(union, stream, indent=2)
            stream.write('\n')
        print(json.dumps({'status': summary['status'], 'claims': len(new), 'distinct_literal_exclusions': len(union)}))
    except BaseException as error:
        with (args.out / 'failure.json').open('x', encoding='utf8') as stream:
            json.dump({'error': repr(error), 'timestamp': datetime.now(timezone.utc).isoformat(), 'inputs_sha256': pins}, stream, indent=2)
        raise


if __name__ == '__main__':
    main()
