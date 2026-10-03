"""SOURCE ONLY: explicit fixed371 byte inventory; no docs, tests, index or ledger writes."""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys

from command_deadline import CommandDeadline
import validate_claims as registry

ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()
SPEC = SELF.with_name(SELF.stem + '_spec.md')
CONFIG = 'acceleration/inventory_20261003_wave42_selection_v3.json'
CONFIG_SHA = '2de5cc7c62ae7562e8c56658532f3dd8824ff2c8850a33133ecfd2364f188368'


def need(ok, stage):
    if not ok:
        raise ValueError(stage)


def same(left, right):
    if type(left) is not type(right):
        return False
    if type(left) is dict:
        return left.keys() == right.keys() and all(same(left[k], right[k]) for k in left)
    if type(left) is list:
        return len(left) == len(right) and all(same(a, b) for a, b in zip(left, right))
    return left == right


def sha(path):
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def save(path, value):
    with path.open('x', encoding='utf8', newline='\n') as handle:
        json.dump(value, handle, indent=2, allow_nan=False)
        handle.write('\n')


def bounded(name):
    need(type(name) is str and name and not any(c in name for c in '\\\r\n\0'), 'LITERAL_PATH')
    path = PurePosixPath(name)
    need(not path.is_absolute() and '..' not in path.parts and not name.startswith('.git/'), 'PATH_BOUNDARY')
    need(name.startswith(('acceleration/', 'docs/')) or name in
         ['CLAIMS.yaml', 'README.md', 'ACTIVE_RESEARCH.md', 'pyproject.toml', 'uv.lock', '.gitattributes'], 'RESEARCH_NAMESPACE')
    need('/build/' not in name and '/recovered/' not in name, 'NO_DUPLICATE_BUILD')
    result = (ROOT/name).resolve()
    need(result.is_relative_to(ROOT), 'RESOLVED_BOUNDARY')
    return result


def raw_json(path):
    def pairs(items):
        value = {}
        for name, item in items:
            need(name not in value, 'JSON_DUPLICATE')
            value[name] = item
        return value
    return json.loads(path.read_bytes(), object_pairs_hook=pairs,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError('JSON_NONFINITE')))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seconds', type=float, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--self-sha256', required=True)
    parser.add_argument('--spec-sha256', required=True)
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='One explicit fixed371 inventory only; all source/input/raw hashes/child Git show/export share inclusive150 with20save; no mathematical replay or mutation')
    out = args.out.resolve()
    need(out.is_relative_to(ROOT) and not out.exists(), 'FRESH_OUTPUT')
    out.mkdir(parents=True)
    pins, expected, origins, historical_mutable = {}, {}, defaultdict(set), []
    records, omitted = [], []

    def pin(name, wanted=None):
        need(not deadline.status()['stop_required'] and deadline.status()['remaining_seconds'] > 20, 'NOT_COMPLETED_WITHIN_ALLOCATED_BUDGET')
        path = bounded(name)
        need(path.is_file(), 'INPUT_FILE')
        identity = sha(path)
        need(wanted is None or identity == wanted, 'INPUT_HASH')
        need(name not in pins or pins[name] == identity, 'INPUT_CHANGED')
        pins[name] = identity
        return identity

    def read(name, wanted):
        pin(name, wanted)
        return raw_json(bounded(name))

    def add(name, wanted, origin, explicit=False):
        if name == '.git/index':
            historical_mutable.append(dict(path=name, sha256=wanted, origin=origin, disposition='HISTORICAL_OBSERVATION_ONLY_NO_GIT_PAYLOAD'))
            return
        if name == 'CLAIMS.yaml' and wanted not in (None, config['current_ledger_sha256']):
            historical_mutable.append(dict(path=name, sha256=wanted, origin=origin, disposition='HISTORICAL_LEDGER_OBSERVATION_ONLY'))
            return
        if name == config['historical_external_reference']['path']:
            need(wanted == config['historical_external_reference']['sha256'], 'EXACT_EXTERNAL_REFERENCE')
            return
        bounded(name)
        if not explicit:
            need(not any(name.startswith(prefix) for prefix in config['excluded_queued_prefixes']), 'UNDECLARED_QUEUED_MEMBER')
        need(name not in expected or wanted is None or expected[name] in (None, wanted), 'CONFLICTING_INPUT_IDENTITY')
        if wanted is not None or name not in expected:
            expected[name] = wanted
        origins[name].add(origin)

    try:
        pin(SELF.relative_to(ROOT).as_posix(), args.self_sha256)
        pin(SPEC.relative_to(ROOT).as_posix(), args.spec_sha256)
        config = read(CONFIG, CONFIG_SHA)
        need(config['status'] == 'SOURCE_ONLY_NOT_EXECUTED' and len(config['bindings']) == 13
             and len(config['claim_ids']) == len(set(config['claim_ids'])) == 13, 'EXACT_THIRTEEN_SELECTION')
        pin('CLAIMS.yaml', config['current_ledger_sha256'])
        pin(config['previous_ledger'], config['previous_ledger_sha256'])
        original_index = sha(ROOT/'.git/index')
        need(original_index == config['protected_index_sha256'], 'PROTECTED_INDEX')
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT,
                                        timeout=deadline.child_seconds(10, reserve_seconds=20), text=True).strip()
        need(commit == config['source_context_commit'], 'SOURCE_CONTEXT')
        current = registry.read_ledger(ROOT/'CLAIMS.yaml')
        before = registry.read_ledger(ROOT/config['previous_ledger'])
        need(len(before['claims']) == 358 and len(current['claims']) == 371
             and same(current['claims'][:358], before['claims'])
             and [c['id'] for c in current['claims'][358:]] == config['claim_ids']
             and same(current['artifacts'][:len(before['artifacts'])], before['artifacts'])
             and same(current['target'], before['target']), 'EXACT_PRIOR_MATERIAL_AND_THIRTEEN')
        need(dict(Counter(c['status'] for c in current['claims'])) == {'VERIFIED':363, 'CANDIDATE':3, 'REFUTED':5}
             and dict(Counter(c['review_state'] for c in current['claims'])) == {'CLEAR':371}
             and current['target']['status'] == 'UNKNOWN', 'EXACT371_STATUS_SCOPE')
        artifacts = {a['id']: a for a in current['artifacts']}
        for claim in current['claims'][358:]:
            for aid in claim['evidence']:
                item = artifacts[aid]
                add(item['path'], item['sha256'], 'Exact registered thirteen-claim evidence', explicit=True)
        bindings_by_id = {}
        for row in config['bindings']:
            value = read(row['path'], row['sha256'])
            need(value['id'] == row['id'], 'EXACT_BINDING_ID')
            bindings_by_id[row['id']] = value
            add(row['path'], row['sha256'], 'Exact accepted frozen binding', explicit=True)
            for name, identity in value['inputs_sha256'].items():
                add(name, identity, 'Complete declared frozen binding closure '+row['id'], explicit=True)
        checking_maps = config['declared_checking_maps']
        need(type(checking_maps) is list and len(checking_maps) == 2
             and [row['immutable_members'] for row in checking_maps] == [2376, 3066], 'EXACT_TWO_CHECKING_MAPS')
        checking_map_records = []
        for row in checking_maps:
            descriptor = bindings_by_id[row['claim_id']]['complete_declared_historical_checking_closure']
            need(descriptor['path'] == row['path'] and descriptor['sha256'] == row['sha256']
                 and type(row['immutable_members']) is int
                 and type(descriptor['immutable_members']) is int
                 and descriptor['immutable_members'] == row['immutable_members'], 'EXACT_BINDING_CHECKING_MAP')
            value = read(row['path'], row['sha256'])
            members = value['inputs_sha256']
            need(type(members) is dict and len(members) == row['immutable_members'], 'EXACT_CHECKING_MAP_MEMBER_COUNT')
            add(row['path'], row['sha256'], 'Exact explicitly declared complete checking map', explicit=True)
            for member, identity in members.items():
                need(type(identity) is str and len(identity) == 64
                     and all(c in '0123456789abcdef' for c in identity), 'CHECKING_MAP_HASH_TYPE')
                add(member, identity, 'Complete literal checking map '+row['claim_id'], explicit=True)
            checking_map_records.append(dict(claim_id=row['claim_id'], path=row['path'],
                                              sha256=row['sha256'], declared_members=len(members)))
        for name, identity in config['accepted_actual_transition_reports'].items():
            value = read(name, identity)
            need(value['target_resolution'] in ('NONE', 'UNKNOWN'), 'TRANSITION_NO_TARGET_PROMOTION')
            add(name, identity, 'Accepted actual bookkeeping transition', explicit=True)
            for member, digest in value['inputs_sha256'].items():
                add(member, digest, 'Complete actual transition closure', explicit=True)
        packages = {}
        parts = []
        for name, identity in config['prior_lossless_packages'].items():
            package = read(name, identity)
            add(name, identity, 'Existing exact lossless manifest', explicit=True)
            for row in package['records']:
                need(row['raw_path'] not in packages, 'DISTINCT_OLD_RAW')
                packages[row['raw_path']] = row
                add(row['raw_path'], row['raw_sha256'], 'Old raw identity authenticated then omitted', explicit=True)
                offset = 0
                for part in row['parts']:
                    need(type(part['raw_offset']) is int and part['raw_offset'] == offset
                         and type(part['raw_bytes']) is int and part['raw_bytes'] > 0, 'LOSSLESS_PART_OFFSETS')
                    offset += part['raw_bytes']
                    add(part['path'], part['gzip_sha256'], 'Existing exact recoverable gzip member', explicit=True)
                    parts.append(part)
                need(offset == row['raw_bytes'], 'LOSSLESS_MEMBER_LENGTH')
        need(len(packages) == 8 and len(parts) == 48
             and sum(row['raw_bytes'] for row in packages.values()) == 367261301
             and sum(part['gzip_bytes'] for part in parts) == 11723542, 'EXACT_EIGHT_OLD_RAW_48_PARTS')
        for name in config['explicit_current_files']:
            add(name, config['current_ledger_sha256'] if name == 'CLAIMS.yaml' else None, 'Explicit current file', explicit=True)
        for name in config['explicit_metadata_roots']:
            path = bounded(name)
            need(path.is_file() or path.is_dir(), 'EXPLICIT_METADATA_ROOT_EXISTS')
            members = [path] if path.is_file() else sorted(p for p in path.rglob('*') if p.is_file())
            for member in members:
                add(member.relative_to(ROOT).as_posix(), None, 'Exact named closed metadata root '+name)
        for name in [CONFIG, 'acceleration/inventory_20261003_wave42_selection_v1.json',
                     SELF.relative_to(ROOT).as_posix(), SPEC.relative_to(ROOT).as_posix()]:
            add(name, pins.get(name), 'Inventory source/configuration history', explicit=True)
        for doc in ['README.md', 'ACTIVE_RESEARCH.md', 'docs/RESEARCH_MAP.md', 'docs/REPRODUCING.md']:
            history = subprocess.check_output(['git', 'show', commit+':'+doc], cwd=ROOT,
                                               timeout=deadline.child_seconds(10, reserve_seconds=20))
            need(bounded(doc).read_bytes().endswith(history), 'PRESERVED_PUBLISHED_NOTICE_SUFFIX')
        for position, name in enumerate(sorted(expected)):
            identity = pin(name, expected[name])
            size = bounded(name).stat().st_size
            if name in packages:
                row = packages[name]
                need(identity == row['raw_sha256'] and size == row['raw_bytes'], 'OMITTED_RAW_EXACT_IDENTITY')
                omitted.append(dict(path=name, sha256=identity, bytes=size,
                    reason='Exact previously independently recovered package-bound raw duplicate; no new recovery approval'))
            else:
                need(size <= config['direct_byte_limit'], 'UNDECLARED_MEMBER_ABOVE50MIB')
                records.append(dict(path=name, sha256=identity, bytes=size, origins=sorted(origins[name])))
            if position % 100 == 0:
                print(json.dumps(dict(hashed_unique_members=position+1, declared_unique_members=len(expected), deadline=deadline.status())), flush=True)
        need(sha(ROOT/'.git/index') == original_index and sha(ROOT/'CLAIMS.yaml') == config['current_ledger_sha256'], 'PROTECTED_STATE_UNCHANGED')
        for name, identity in sorted(pins.items()):
            need(deadline.status()['remaining_seconds'] > 20 and sha(bounded(name)) == identity, 'CLOSING_INPUT_STABILITY')
        raw_paths = ''.join(row['path']+'\0' for row in records).encode('utf8')
        (out/'selected_paths.nul').write_bytes(raw_paths)
        (out/'CLAIMS.yaml').write_bytes((ROOT/'CLAIMS.yaml').read_bytes())
        save(out/'manifest.json', dict(schema='WAVE42_FIXED371_EXPLICIT_BYTE_INVENTORY_V2', timestamp=datetime.now(timezone.utc).isoformat(),
            producer='/root/native_driver', command=[sys.executable,*sys.argv], cwd=str(ROOT), source_context_commit=commit,
            current_ledger_sha256=config['current_ledger_sha256'], previous_ledger_sha256=config['previous_ledger_sha256'],
            claim_ids=config['claim_ids'], records=records, direct_record_count=len(records), direct_bytes=sum(r['bytes'] for r in records),
            omitted=omitted, old_lossless_packages=config['prior_lossless_packages'],
            complete_declared_checking_maps=checking_map_records,
            historical_mutable_observations=historical_mutable, historical_external_reference=config['historical_external_reference'],
            selected_paths_sha256=sha(out/'selected_paths.nul'), inputs_sha256=pins, protected_index_observation=original_index,
            scientific_launched=False, mathematical_replays=0, current_docs_mutated=False, ledger_mutated=False,
            index_mutated=False, availability_changed=False, independent_approval=False,
            self_metadata_appendix_required=True, target_resolution='NONE', deadline=deadline.status()))
        print(json.dumps(dict(status='CANDIDATE_WAVE42_BYTE_INVENTORY_PENDING_SEPARATE_REVIEW',
                              manifest_sha256=sha(out/'manifest.json'), direct_record_count=len(records), omitted_raw=len(omitted))), flush=True)
    except BaseException as error:
        save(out/'failure.json', dict(error=repr(error), partial_inputs_sha256=pins, completed_direct_records=records,
            completed_omissions=omitted, deadline=deadline.status(), mathematical_replays=0, ledger_mutated=False,
            index_mutated=False, current_docs_mutated=False, scientific_launched=False, independent_approval=False))
        raise


if __name__ == '__main__':
    main()
