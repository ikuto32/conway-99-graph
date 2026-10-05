"""SOURCE ONLY: explicit Wave43 byte inventory; no staging or mathematical replay."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys

from command_deadline import CommandDeadline
import validate_claims as registry

ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()
SPEC = SELF.with_name(SELF.stem + '_spec.md')
PLAN = 'acceleration/plan_20261003_wave43_inventory_v1.json'
CONFIG = 'acceleration/proposal_20261003_wave43_publication_paths_v1.json'
CONFIG_SHA = 'e2caf73210d5db258380eabc394a8d756b601910441a4d3290fb00325d72cbef'
DESCRIPTOR = 'acceleration/proposal_20261003_wave43_eighteen_written_bindings_v2.json'
DESCRIPTOR_SHA = '3f29f453813459d18740e5fb70fb7adddf56fed513db84f7598d4e4aeb1b331c'
HEAD = 'd0c0dd7db0d3de420b1d718b59122b069df01107'
LEDGER = 'b7d07a8be5cbbce8c2125e631d58f4035ed56a66c2b1e79db27cb56500859f8a'
BEFORE = 'acceleration/results/20261003_wave43_registration01/CLAIMS.before.yaml'
BEFORE_SHA = '23ee170c0f7250843ec2852758f0dd7d1324e85647c44e1907a62f062db47da9'
INDEX = '618367410b57562be69a658a96c48f7dd1908bd3f58bac806d050cdab0c72632'
LIMIT = 50 * 1024 * 1024
SOFTWARE = {
    'acceleration/command_deadline.py': '9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9',
    'acceleration/validate_claims.py': 'a48f55b54918b0c494e6f06f80bdcdc52f304dfc370dd25842aeae3a0f861265',
    'acceleration/run_compute_command.py': '593a9feed6250739dc9672338df23ab171fc9a6a6db4196c1feb312efa33957a',
    'pyproject.toml': '273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339',
    'uv.lock': 'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',
}


def need(ok, stage):
    if not ok:
        raise ValueError(stage)


def same(a, b):
    if type(a) is not type(b):
        return False
    if type(a) is dict:
        return a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
    if type(a) is list:
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    return a == b


def literal(name):
    need(type(name) is str and name and not any(c in name for c in '\\\r\n\0'), 'LITERAL_PATH')
    p = PurePosixPath(name)
    need(not p.is_absolute() and '..' not in p.parts and str(p) == name, 'PATH_BOUNDARY')
    need(not any(part.lower() in {'.git', 'build', 'recovered', 'private', 'secrets', '.ssh', '.env'}
                 for part in p.parts), 'PRIVATE_OR_BUILD_PATH')
    need(name.startswith(('acceleration/', 'docs/')) or name in
         {'CLAIMS.yaml', 'README.md', 'ACTIVE_RESEARCH.md', 'pyproject.toml', 'uv.lock'}, 'RESEARCH_NAMESPACE')
    return p


def bounded(name):
    p = literal(name)
    path = ROOT
    for part in p.parts:
        path /= part
        if path.exists() or path.is_symlink():
            info = path.lstat()
            need(not stat.S_ISLNK(info.st_mode) and not
                 (getattr(info, 'st_file_attributes', 0) & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 1024)),
                 'SYMLINK_OR_REPARSE_POINT')
    need(path.resolve().is_relative_to(ROOT), 'RESOLVED_BOUNDARY')
    return path


def strict_json(raw):
    need(len(raw) <= LIMIT, 'JSON_MEMBER_SIZE')
    def pairs(items):
        result = {}
        for k, v in items:
            need(k not in result, 'JSON_DUPLICATE')
            result[k] = v
        return result
    return json.loads(raw, object_pairs_hook=pairs,
        parse_constant=lambda _: (_ for _ in ()).throw(ValueError('JSON_NONFINITE')))


def suffix(now, old):
    need(type(now) is bytes and type(old) is bytes and now.endswith(old), 'GIT_DOCUMENT_SUFFIX')


def own_controls():
    positives = [same({'n': 389}, {'n': 389}), str(literal('docs/claims.schema.json')) == 'docs/claims.schema.json']
    suffix(b'notice\nold', b'old')
    positives.extend([True, same(strict_json(b'{"n":389}'), {'n': 389})])
    rows = []
    for name, stage, fn in [
        ('parent_path', 'PATH_BOUNDARY', lambda: literal('docs/../x')),
        ('backslash', 'LITERAL_PATH', lambda: literal('docs\\x')),
        ('private_build', 'PRIVATE_OR_BUILD_PATH', lambda: literal('acceleration/build/x')),
        ('unrelated_instructions', 'RESEARCH_NAMESPACE', lambda: literal('AGENTS.md')),
        ('duplicate_json', 'JSON_DUPLICATE', lambda: strict_json(b'{"n":389,"n":389}')),
        ('nonfinite_json', 'JSON_NONFINITE', lambda: strict_json(b'{"n":NaN}')),
        ('wrong_suffix', 'GIT_DOCUMENT_SUFFIX', lambda: suffix(b'old\nchanged', b'old')),
        ('bool_count_alias', 'TYPED_ALIAS', lambda: need(same({'n': 1}, {'n': True}), 'TYPED_ALIAS')),
    ]:
        try:
            fn()
            raise RuntimeError('CONTROL_ACCEPTED_CORRUPTION')
        except ValueError as exc:
            actual = str(exc)
        need(actual == stage, 'CONTROL_STAGE')
        rows.append(dict(case=name, expected_stage=stage, actual_stage=actual))
    need(all(positives), 'CONTROL_POSITIVE')
    return dict(positive=4, strict_negative=8, records=rows, mathematical_replays=0,
                limitation='Synthetic literal/IO/type boundaries only; no generic filesystem/Git/cleanup guarantee')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--seconds', type=float, required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--self-sha256', required=True)
    ap.add_argument('--spec-sha256', required=True)
    args = ap.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='Exact258 Wave43 paths plus four explicit own metadata files; setup/hash/parse/Git/copies share150 inclusive with20save')
    out = bounded(args.out)
    need(not out.exists(), 'FRESH_OUTPUT')
    out.mkdir(parents=True)
    pins, records, origins, suffixes = {}, [], {}, []
    def tick():
        s = deadline.status()
        need(not s['stop_required'] and s['remaining_seconds'] > 20, 'NOT_COMPLETED_WITHIN_ALLOCATED_BUDGET')
        return s
    def sha_path(path):
        tick()
        h = hashlib.sha256()
        with path.open('rb') as handle:
            while chunk := handle.read(1024 * 1024):
                tick()
                h.update(chunk)
        tick()
        return h.hexdigest()
    def pin(name, expected=None):
        tick()
        path = bounded(name)
        need(path.is_file() and path.stat().st_size <= LIMIT, 'INPUT_MEMBER_SIZE')
        digest = sha_path(path)
        need(expected is None or digest == expected, 'INPUT_HASH')
        need(name not in pins or pins[name] == digest, 'INPUT_CHANGED')
        pins[name] = digest
        return digest
    def read(name, expected=None):
        pin(name, expected)
        value = strict_json(bounded(name).read_bytes())
        tick()
        return value
    def save(name, raw):
        tick()
        with (out / name).open('xb') as handle:
            handle.write(raw)
        tick()
    def save_json(name, value):
        save(name, (json.dumps(value, indent=2, allow_nan=False) + '\n').encode('utf8'))
    def git(argv):
        tick()
        data = subprocess.check_output(['git', *argv], cwd=ROOT,
             timeout=deadline.child_seconds(10, reserve_seconds=20))
        tick()
        return data
    try:
        pin(SELF.relative_to(ROOT).as_posix(), args.self_sha256)
        pin(SPEC.relative_to(ROOT).as_posix(), args.spec_sha256)
        for name, digest in SOFTWARE.items():
            pin(name, digest)
        controls = own_controls()
        tick()
        save_json('controls.json', controls)
        plan = read(PLAN)
        need(plan['worker_argv'][2:] == sys.argv and plan['allocation']['worker'] == args.seconds,
             'LITERAL_WORKER_PLAN')
        config = read(CONFIG, CONFIG_SHA)
        descriptor = read(DESCRIPTOR, DESCRIPTOR_SHA)
        base = config['selected_existing_paths']
        need(type(base) is list and len(base) == len(set(base)) == 258 and base == sorted(base), 'EXACT258_PATH_SET')
        need(same(config['accepted_cutoff'], dict(total=389, VERIFIED=381, CANDIDATE=3, REFUTED=5, CLEAR=389,
             new_claims=18, prior_PUBLIC_artifact_entries=6054, last_Wave42_changed_subset=119,
             target_resolution='UNKNOWN', general_target_exclusions=0, specified_configuration_exclusions=1)), 'EXACT389_CUTOFF')
        need(len(descriptor['records_in_dependency_order']) == 18 and
             len(descriptor['declared_binding_and_checking_closure']) == 70, 'EXACT18_70_DESCRIPTOR')
        ids = [r['binding_contract']['id'] for r in descriptor['records_in_dependency_order']]
        need(len(set(ids)) == 18 and same(ids, config['descriptor']['new_claim_ids']), 'EXACT18_IDS')
        pin('CLAIMS.yaml', LEDGER)
        pin(BEFORE, BEFORE_SHA)
        current = registry.read_ledger(ROOT / 'CLAIMS.yaml')
        before = registry.read_ledger(ROOT / BEFORE)
        tick()
        need(len(current['claims']) == 389 and len(before['claims']) == 371 and
             same(current['claims'][:371], before['claims']) and
             [c['id'] for c in current['claims'][371:]] == ids and
             same(current['artifacts'][:len(before['artifacts'])], before['artifacts']) and
             same(current['target'], before['target']), 'PRIOR371_AND_NEW18')
        need(dict(Counter(c['status'] for c in current['claims'])) == {'VERIFIED':381,'CANDIDATE':3,'REFUTED':5}
             and dict(Counter(c['review_state'] for c in current['claims'])) == {'CLEAR':389}
             and current['target']['status'] == 'UNKNOWN', 'LEDGER389_STATUS')
        need(sum(a['availability'] == 'PUBLIC' for a in current['artifacts']) == 6054, 'PUBLIC6054')
        index_before = sha_path(ROOT / '.git/index')
        need(index_before == INDEX and git(['rev-parse','HEAD']).decode().strip() == HEAD, 'PROTECTED_CONTEXT')
        rows = config['selected_existing_files']
        need(type(rows) is list and [r['path'] for r in rows] == base, 'EXACT258_RECORDS')
        expected = {}
        for row in rows:
            name, digest = row['path'], row['declared_sha256']
            literal(name)
            need(type(row['observed_bytes']) is int and 0 <= row['observed_bytes'] <= LIMIT, 'DECLARED_MEMBER_SIZE')
            need(digest is None or type(digest) is str and len(digest) == 64 and
                 all(c in '0123456789abcdef' for c in digest), 'HASH_FORMAT')
            expected[name] = digest
            origins[name] = row['reasons']
        for name, digest in descriptor['declared_binding_and_checking_closure'].items():
            need(name in expected and expected[name] == digest, 'ALL70_DECLARED_MEMBERS')
        todo = [n for n in descriptor['declared_binding_and_checking_closure'] if n.endswith('.json')]
        visited = set()
        while todo:
            name = todo.pop()
            if name in visited:
                continue
            visited.add(name)
            value = read(name, expected[name])
            for child, digest in value.get('inputs_sha256', {}).items():
                need(child in expected and expected[child] == digest, 'DECLARED_ANCESTOR_SELECTED')
                if child.endswith('.json'):
                    todo.append(child)
        need(len(visited) == config['literal_mathematical_JSON_ancestor_count'] == 38, 'EXACT38_ANCESTORS')
        own = [SELF.relative_to(ROOT).as_posix(), SPEC.relative_to(ROOT).as_posix(), PLAN, CONFIG]
        need(not any(n in expected for n in own), 'OWN_METADATA_DISJOINT')
        for name in own:
            expected[name] = pins[name]
            origins[name] = ['Explicit inventory own metadata appendix; no research claim']
        for doc in ['README.md','ACTIVE_RESEARCH.md','docs/RESEARCH_MAP.md','docs/REPRODUCING.md']:
            old = git(['show', HEAD + ':' + doc])
            now = bounded(doc).read_bytes()
            tick()
            suffix(now, old)
            suffixes.append(dict(path=doc, historical_commit=HEAD, historical_bytes=len(old),
                 historical_sha256=hashlib.sha256(old).hexdigest(), current_bytes=len(now), suffix_byte_equal=True))
        for i, name in enumerate(sorted(expected)):
            digest = pin(name, expected[name])
            records.append(dict(path=name, sha256=digest, bytes=bounded(name).stat().st_size, origins=origins[name]))
            if i % 25 == 0:
                print(json.dumps(dict(hashed=i+1, total=len(expected), deadline=tick())), flush=True)
        need(len(records) == 262, 'EXACT262_UNION')
        for name, digest in sorted(pins.items()):
            pin(name, digest)
        need(sha_path(ROOT / '.git/index') == index_before and sha_path(ROOT / 'CLAIMS.yaml') == LEDGER
             and git(['rev-parse','HEAD']).decode().strip() == HEAD, 'CLOSING_PROTECTED_STABILITY')
        raw = ''.join(r['path'] + '\0' for r in records).encode('utf8')
        save('selected_paths.nul', raw)
        ledger_bytes = (ROOT / 'CLAIMS.yaml').read_bytes()
        need(hashlib.sha256(ledger_bytes).hexdigest() == LEDGER, 'FROZEN_LEDGER_COPY')
        save('CLAIMS.yaml', ledger_bytes)
        save_json('manifest.json', dict(schema='WAVE43_FIXED389_EXPLICIT_BYTE_INVENTORY_V1',
            timestamp=datetime.now(timezone.utc).isoformat(), source_author='/root/checkpoint_audit',
            intended_executor='/root', producer='/root', command=[sys.executable,*sys.argv], cwd=str(ROOT),
            source_context_commit=HEAD, current_ledger_sha256=LEDGER, previous_ledger_sha256=BEFORE_SHA,
            base_selection_path=CONFIG, base_selection_sha256=CONFIG_SHA, base_record_count=258,
            own_metadata_paths=own, own_metadata_count=4, direct_record_count=len(records),
            direct_bytes=sum(r['bytes'] for r in records), records=records, inputs_sha256=pins,
            claim_ids=ids, total_claims=389, status_counts={'VERIFIED':381,'CANDIDATE':3,'REFUTED':5},
            review_state_counts={'CLEAR':389}, prior_PUBLIC_artifact_entries=6054,
            last_Wave42_changed_subset=119, literal_math_map_members=70, literal_math_JSON_ancestors=38,
            selected_paths_sha256=sha_path(out/'selected_paths.nul'), frozen_ledger_copy_sha256=LEDGER,
            document_suffixes=suffixes, protected_index_observation=index_before, controls=controls,
            old_archives_not_rehashed_or_recovered=True, no_new_archive_omissions=True,
            mathematical_replays=0, scientific_launched=False, current_docs_mutated=False,
            ledger_mutated=False, index_mutated=False, availability_changed=False, independent_approval=False,
            shared_components=['Preserved Wave42 inventory IO/type/registry/Git conventions; fresh scope/pins/control execution required',
                              'Common Python/SHA/deadline/YAML parser; authoring registrar does not establish mathematics'],
            target_resolution='NONE', deadline=tick()))
        tick()
        print(json.dumps(dict(status='CANDIDATE_WAVE43_BYTE_INVENTORY_PENDING_SEPARATE_REVIEW',
            manifest_sha256=sha_path(out/'manifest.json'), selected=len(records))), flush=True)
    except BaseException as exc:
        # Best-effort failure preservation; hard termination cannot guarantee this write.
        (out/'failure.json').write_text(json.dumps(dict(error=repr(exc), inputs_sha256=pins,
             completed_records=records, deadline=deadline.status(), mathematical_replays=0,
             ledger_index_docs_mutated=False, independent_approval=False), indent=2) + '\n', encoding='utf8')
        raise


if __name__ == '__main__':
    main()
