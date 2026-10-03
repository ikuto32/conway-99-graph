"""ROOT's independent frozen358 manifest/raw Git-index check; no producer imports."""
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
PARENT = 'acceleration/stage_20261003_wave40_index_v2.py'
PARENT_SHA = '11150733d86ee7154eab2c0cc98b239019fb625d0ff44ff16071218d270661f3'
LEDGER = '10b7636dafced40101ccf257d5f80468914f53aa2ee2d3c89db43be268bdcc09'
CONTEXT_COMMIT = '00ffb6fdd7d91bd38269e1cc5e6b214ebf7591c8'
BEFORE = 'a4f2f5b2ff41ea7aebf99413cdc825fc1e08f5269079d43e305da713f4af29ef'
INDEX = '8bcd46056145e09d225a01e553151abd1958364077a85b5c6d1bc33fe4f4cacd'
IDS = ['C-UNRESTRICTED-TRIANGLE-INCIDENCE-WEIGHT5-C4-COLLISION-SUBTRACTION-LOWER-COUNT',
       'C-UNRESTRICTED-TRIANGLE-INCIDENCE-BINARY-RANK-LOWER87']
DENY = ('ternary_degree14', 'ternary_residue', 'fixed_graph_diagnostics', 'incidence_gf3_rank',
        'all_root', 'strict_lex_step', 'root_focused_chain', 'selected_neighbor_census',
        'root_focused_two_line_census', 'root_focused_neighbor_projection', 'double_fibers_rook9')
DOCS = ['README.md', 'ACTIVE_RESEARCH.md', 'docs/RESEARCH_MAP.md', 'docs/REPRODUCING.md']
MILESTONE = 'docs/RESEARCH_20261003_FORTYFIRST_WAVE.md'


def need(ok, stage):
    if not ok:
        raise ValueError(stage)


def unique(pairs):
    value = {}
    for key, item in pairs:
        need(key not in value, 'DUPLICATE_JSON_KEY')
        value[key] = item
    return value


def read(path):
    return json.loads(path.read_bytes(), object_pairs_hook=unique)


def save(path, value):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def historical_suffix(before, prepared, current, original_git_blob):
    need(before == original_git_blob, 'BEFORE_DOCUMENT_GIT_BLOB')
    need(prepared.endswith(before), 'DOCUMENT_HISTORICAL_SUFFIX')
    need(current == prepared, 'CURRENT_DOCUMENT_PREPARED_BYTES')


def parent():
    need(hashlib.sha256((ROOT / PARENT).read_bytes()).hexdigest() == PARENT_SHA, 'PINNED_SHARED_ENGINEERING')
    spec = importlib.util.spec_from_file_location('wave41_shared_index_helpers', ROOT / PARENT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def scope(m, attrs, lib):
    need([m.get(k) for k in ('schema', 'current_claims', 'previous_claims', 'ledger_sha256', 'before_ledger_sha256', 'new_claim_ids')]
         == ['WAVE41_FIXED358_EXPLICIT_PUBLICATION_ALLOWLIST_V1', 358, 356, LEDGER, BEFORE, IDS], 'FROZEN358_SCOPE')
    need(all(type(m[k]) is int for k in ('current_claims', 'previous_claims', 'direct_record_count', 'direct_bytes', 'stage_paths_count')), 'INTEGER_COUNTS')
    need(all(m.get(k) is False for k in ('ledger_mutated', 'index_mutated', 'availability_changed', 'scientific_launched'))
         and type(m.get('mathematical_replays')) is int and m['mathematical_replays'] == 0, 'METADATA_ONLY')
    need(m['inputs_sha256'].get('.gitattributes') == attrs, 'ATTRIBUTES')
    need(m['docs_written'] == DOCS + [MILESTONE], 'FIVE_DOCUMENT_WRITES')
    records = m['records']
    names = [row['path'] for row in records]
    need(len(names) == len(set(names)) == m['direct_record_count'], 'UNIQUE_DIRECT')
    need(all(type(row['bytes']) is int and 0 <= row['bytes'] < 50 * 1024 ** 2 for row in records), 'DIRECT_SIZE')
    need(sum(row['bytes'] for row in records) == m['direct_bytes'], 'DIRECT_TOTAL')
    for name in names:
        lib.bounded(name)
        need(not any(word in name.lower() for word in DENY), 'QUEUED_SCIENCE')
    omitted = {row['path']: row for row in m['omitted']}
    need(len(omitted) == len(m['omitted']) == 8 and not set(names) & set(omitted), 'EIGHT_OMITTED')
    need(sum(row['bytes'] for row in omitted.values()) == 367261301, 'OLD_RAW_TOTAL')
    need(all(m['inputs_sha256'].get(name) == row['sha256'] for name, row in omitted.items()), 'OMITTED_PINS')
    refs = m['historical_external_sources']
    need(type(refs) is list and len(refs) == 1, 'ONE_ARCHIVE_REFERENCE')
    ref = refs[0]
    need([ref.get(k) for k in ('path', 'sha256', 'repository', 'commit', 'external_path')]
         == [lib.ARCHIVE, lib.ARCHIVE_SHA, lib.ARCHIVE_REPOSITORY, lib.ARCHIVE_COMMIT, lib.ARCHIVE.split('/', 1)[1]], 'ARCHIVE_IDENTITY')
    need(ref['retrieval'] == lib.ARCHIVE_REPOSITORY + '/blob/' + lib.ARCHIVE_COMMIT + '/' + lib.ARCHIVE.split('/', 1)[1], 'ARCHIVE_RETRIEVAL')
    return names, omitted


def fixture(attrs, lib):
    omitted = [dict(path='acceleration/synthetic_old_raw_' + str(i), bytes=1 if i else 367261294, sha256='f' * 64) for i in range(8)]
    ref = dict(path=lib.ARCHIVE, sha256=lib.ARCHIVE_SHA, repository=lib.ARCHIVE_REPOSITORY, commit=lib.ARCHIVE_COMMIT,
               external_path=lib.ARCHIVE.split('/', 1)[1], retrieval=lib.ARCHIVE_REPOSITORY + '/blob/' + lib.ARCHIVE_COMMIT + '/' + lib.ARCHIVE.split('/', 1)[1])
    return dict(schema='WAVE41_FIXED358_EXPLICIT_PUBLICATION_ALLOWLIST_V1', current_claims=358, previous_claims=356,
                ledger_sha256=LEDGER, before_ledger_sha256=BEFORE, new_claim_ids=IDS, ledger_mutated=False,
                index_mutated=False, availability_changed=False, scientific_launched=False, mathematical_replays=0,
                inputs_sha256={'.gitattributes': attrs, **{r['path']: r['sha256'] for r in omitted}},
                records=[dict(path='CLAIMS.yaml', bytes=1, sha256=LEDGER)], direct_record_count=1, direct_bytes=1,
                stage_paths_count=1, docs_written=DOCS + [MILESTONE], omitted=omitted, historical_external_sources=[ref])


def controls(attrs, lib):
    good = fixture(attrs, lib)
    scope(good, attrs, lib)
    records = [dict(label='synthetic_exact358', outcome='PASS')]
    changes = [('count', 'FROZEN358_SCOPE', lambda m: m.update(current_claims=359)),
               ('float_count', 'INTEGER_COUNTS', lambda m: m.update(current_claims=358.0)),
               ('ledger', 'FROZEN358_SCOPE', lambda m: m.update(ledger_sha256='0' * 64)),
               ('baseline', 'FROZEN358_SCOPE', lambda m: m.update(before_ledger_sha256='0' * 64)),
               ('ids', 'FROZEN358_SCOPE', lambda m: m.update(new_claim_ids=IDS[::-1])),
               ('math_replay_bool', 'METADATA_ONLY', lambda m: m.update(mathematical_replays=False)),
               ('availability', 'METADATA_ONLY', lambda m: m.update(availability_changed=True)),
               ('attributes', 'ATTRIBUTES', lambda m: m['inputs_sha256'].update({'.gitattributes': '0' * 64})),
               ('docs', 'FIVE_DOCUMENT_WRITES', lambda m: m['docs_written'].pop()),
               ('direct_count', 'UNIQUE_DIRECT', lambda m: m.update(direct_record_count=2)),
               ('size', 'DIRECT_SIZE', lambda m: m['records'][0].update(bytes=50 * 1024 ** 2)),
               ('total', 'DIRECT_TOTAL', lambda m: m.update(direct_bytes=2)),
               ('traversal', 'BOUNDED_PATH', lambda m: m['records'][0].update(path='../CLAIMS.yaml')),
               ('submodule', 'EXACT_NAMESPACE', lambda m: m['records'][0].update(path=lib.ARCHIVE)),
               ('queued', 'QUEUED_SCIENCE', lambda m: m['records'][0].update(path='acceleration/ternary_residue_unapproved.py')),
               ('omission', 'EIGHT_OMITTED', lambda m: m['omitted'].pop()),
               ('raw_total', 'OLD_RAW_TOTAL', lambda m: m['omitted'][0].update(bytes=1)),
               ('omitted_pin', 'OMITTED_PINS', lambda m: m['inputs_sha256'].update({m['omitted'][0]['path']: '0' * 64})),
               ('archive_missing', 'ONE_ARCHIVE_REFERENCE', lambda m: m.update(historical_external_sources=[])),
               ('archive_commit', 'ARCHIVE_IDENTITY', lambda m: m['historical_external_sources'][0].update(commit='0' * 40)),
               ('archive_retrieval', 'ARCHIVE_RETRIEVAL', lambda m: m['historical_external_sources'][0].update(retrieval='wrong'))]
    for label, stage, mutate in changes:
        bad = copy.deepcopy(good)
        mutate(bad)
        try:
            scope(bad, attrs, lib)
        except ValueError as error:
            need(str(error) == stage, 'WRONG_CONTROL_STAGE:' + label)
        else:
            raise ValueError('CONTROL_FALSE_ACCEPT:' + label)
        records.append(dict(label=label, stage=stage, outcome='REJECTED'))
    try:
        json.loads('{"a":1,"a":2}', object_pairs_hook=unique)
    except ValueError as error:
        need(str(error) == 'DUPLICATE_JSON_KEY', 'WRONG_JSON_CONTROL_STAGE')
    else:
        raise ValueError('CONTROL_FALSE_ACCEPT:duplicate_json')
    records.append(dict(label='duplicate_json', stage='DUPLICATE_JSON_KEY', outcome='REJECTED'))
    original = b'historical original document\n'
    prepared = b'new notice\n' + original
    historical_suffix(original, prepared, prepared, original)
    records.append(dict(label='synthetic_git_bound_document_suffix', outcome='PASS'))
    for label, stage, values in [
            ('before_and_prepared_changed_together', 'BEFORE_DOCUMENT_GIT_BLOB',
             (b'changed old bytes', b'noticechanged old bytes', b'noticechanged old bytes', original)),
            ('prepared_suffix_changed', 'DOCUMENT_HISTORICAL_SUFFIX',
             (original, b'wrong suffix', b'wrong suffix', original)),
            ('current_changed', 'CURRENT_DOCUMENT_PREPARED_BYTES',
             (original, prepared, b'wrong current', original))]:
        try:
            historical_suffix(*values)
        except ValueError as error:
            need(str(error) == stage, 'WRONG_DOCUMENT_CONTROL_STAGE:' + label)
        else:
            raise ValueError('CONTROL_FALSE_ACCEPT:' + label)
        records.append(dict(label=label, stage=stage, outcome='REJECTED'))
    return records


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--mode', choices=['calibrate', 'shadow', 'apply'], required=True)
    p.add_argument('--seconds', type=float, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--source-sha256', required=True)
    p.add_argument('--spec-sha256', required=True)
    for name in ('manifest', 'calibration', 'shadow-report'):
        p.add_argument('--' + name, type=Path)
        p.add_argument('--' + name + '-sha256')
    a = p.parse_args()
    d = CommandDeadline(a.seconds, allocation_reason='Frozen358 publication raw-byte/index engineering only; all hashes, Git and controls within command;20seconds save reserve')
    lib = parent()
    out = a.out.resolve()
    need(out.is_relative_to(ROOT) and not out.exists(), 'FRESH_OUTPUT')
    out.mkdir(parents=True)
    source, spec = Path(__file__), Path(__file__).with_name(Path(__file__).stem + '_spec.md')
    need(lib.ids(source)[1] == a.source_sha256 and lib.ids(spec)[1] == a.spec_sha256, 'EXACT_SOURCE_SPEC')
    def tick():
        need(not d.status()['stop_required'] and d.status()['remaining_seconds'] > 20, 'DEADLINE_RESERVE')
    def git(words, env=None):
        tick()
        return subprocess.check_output(['git', *words], cwd=ROOT, env=env, stderr=subprocess.PIPE, timeout=max(1, d.status()['remaining_seconds'] - 15))
    index = ROOT / '.git/index'
    need(lib.ids(index)[1] == INDEX and lib.ids(ROOT / 'CLAIMS.yaml')[1] == LEDGER, 'FROZEN_LEDGER_INDEX')
    attrs = lib.ids(ROOT / '.gitattributes')[1]
    original = lib.parse_index(git(['ls-files', '--stage', '-z']))
    started = False
    try:
        tested = controls(attrs, lib)
        common = dict(timestamp=datetime.now(timezone.utc).isoformat(), source_sha256=a.source_sha256,
                      spec_sha256=a.spec_sha256, ledger_sha256=LEDGER, index_before_sha256=INDEX,
                      gitattributes_sha256=attrs, shared_engineering_source=PARENT, shared_engineering_sha256=PARENT_SHA,
                      controls=tested, synthetic_positives=2, precise_negatives=25, mathematical_replays=0,
                      command=[sys.executable, *sys.argv], cwd=str(ROOT))
        if a.mode == 'calibrate':
            need(not any(getattr(a, n) for n in ('manifest', 'calibration', 'shadow_report')), 'CALIBRATION_NO_ACTUAL_MANIFEST')
            need(lib.ids(index)[1] == INDEX and lib.ids(ROOT / 'CLAIMS.yaml')[1] == LEDGER, 'PROTECTED_UNCHANGED')
            save(out / 'summary.json', dict(**common, status='WAVE41_EXACT358_INDEX_CALIBRATION_PASS', actual_manifest_inspected=False, live_index_mutated=False, deadline=d.status()))
            return
        need(a.calibration and a.calibration_sha256 and lib.ids(a.calibration)[1] == a.calibration_sha256, 'EXACT_CALIBRATION')
        cal = read(a.calibration)
        need(cal['status'] == 'WAVE41_EXACT358_INDEX_CALIBRATION_PASS' and all(cal[k] == common[k] for k in ('source_sha256', 'spec_sha256', 'ledger_sha256', 'index_before_sha256', 'gitattributes_sha256', 'controls')), 'APPLICABLE_CALIBRATION')
        need(a.manifest and a.manifest_sha256 and lib.ids(a.manifest)[1] == a.manifest_sha256, 'EXACT_MANIFEST')
        m = read(a.manifest)
        names, omitted = scope(m, attrs, lib)
        ref = m['historical_external_sources'][0]
        need(git(['-C', 'external_conway99_research', 'rev-parse', 'HEAD']).decode().strip() == lib.ARCHIVE_COMMIT, 'ARCHIVE_HEAD')
        raw_archive = git(['-C', 'external_conway99_research', 'cat-file', 'blob', lib.ARCHIVE_COMMIT + ':' + lib.ARCHIVE.split('/', 1)[1]])
        need(hashlib.sha256(raw_archive).hexdigest() == lib.ARCHIVE_SHA and len(raw_archive) == ref['bytes'] and raw_archive == (ROOT / lib.ARCHIVE).read_bytes(), 'ARCHIVE_RAW_BLOB')
        packages = {}
        for name, wanted in m['old_lossless_packages'].items():
            need(lib.ids(lib.bounded(name))[1] == wanted, 'PACKAGE_PIN')
            for row in read(lib.bounded(name))['records']:
                need(row['raw_path'] not in packages, 'UNIQUE_PACKAGE_RAW')
                packages[row['raw_path']] = row
        need(set(packages) == set(omitted) and all((row['raw_sha256'], row['raw_bytes']) == (omitted[name]['sha256'], omitted[name]['bytes']) for name, row in packages.items()), 'EXACT_PACKAGE_OMISSIONS')
        self_names = m['self_metadata_paths']
        need(len(self_names) == len(set(self_names)) and all(lib.bounded(name).parent == a.manifest.resolve().parent for name in self_names), 'SELF_METADATA_BOUNDARY')
        stage_names = sorted(set(names) | set(self_names))
        nul = a.manifest.parent / 'stage_paths.nul'
        need(len(stage_names) == m['stage_paths_count'] and lib.ids(nul)[1] == m['stage_paths_sha256'] and nul.read_bytes() == b''.join(name.encode() + b'\0' for name in stage_names), 'EXACT_NUL')
        for name in DOCS:
            key = name.replace('/', '_')
            old = (a.manifest.parent / (key + '.before')).read_bytes()
            prepared = (a.manifest.parent / (key + '.prepared')).read_bytes()
            original_git_blob = git(['show', CONTEXT_COMMIT + ':' + name])
            historical_suffix(old, prepared, (ROOT / name).read_bytes(), original_git_blob)
        need((ROOT / MILESTONE).read_bytes() == (a.manifest.parent / 'milestone.prepared.md').read_bytes(), 'MILESTONE_PREPARED_BYTES')
        expected = {}
        for row in m['records']:
            tick()
            size, digest, blob = lib.ids(lib.bounded(row['path']))
            need((size, digest) == (row['bytes'], row['sha256']), 'RAW_MEMBER:' + row['path'])
            expected[row['path']] = blob
        for name in self_names:
            tick()
            expected[name] = lib.ids(lib.bounded(name))[2]
        for name, row in omitted.items():
            tick()
            need(lib.ids(lib.bounded(name))[:2] == (row['bytes'], row['sha256']) and name not in original, 'OMITTED_RAW_IDENTITY')
        need(a.mode != 'apply' or (a.shadow_report and a.shadow_report_sha256 and lib.ids(a.shadow_report)[1] == a.shadow_report_sha256), 'EXACT_SHADOW_ARGUMENTS')
        if a.mode == 'apply':
            gate = read(a.shadow_report)
            need(gate['status'] == 'WAVE41_EXACT358_SHADOW_INDEX_RAW_BYTE_PASS' and not gate['failures'] and gate['manifest_sha256'] == a.manifest_sha256 and gate['calibration_sha256'] == a.calibration_sha256 and all(gate[k] == common[k] for k in ('source_sha256', 'spec_sha256', 'ledger_sha256', 'index_before_sha256', 'gitattributes_sha256')), 'APPLICABLE_SHADOW')
        exact = out / 'exact_stage_paths.nul'
        exact.write_bytes(b''.join(name.encode() + b'\0' for name in sorted(expected)))
        env = os.environ.copy()
        shadow = None
        if a.mode == 'shadow':
            shadow = ROOT / 'build' / ('wave41_' + out.name + '.index')
            need(not shadow.exists(), 'FRESH_SHADOW')
            shutil.copy2(index, shadow)
            env['GIT_INDEX_FILE'] = str(shadow)
        started = True
        git(['add', '-f', '--pathspec-from-file=' + str(exact), '--pathspec-file-nul'], env)
        actual = lib.parse_index(git(['ls-files', '--stage', '-z'], env))
        failures = [name for name, blob in expected.items() if actual.get(name, (None, None))[1] != blob]
        outside = [name for name in set(original) | set(actual) if name not in expected and original.get(name) != actual.get(name)]
        need(not outside and all(actual.get(name) == entry for name, entry in original.items() if entry[0] == '160000'), 'UNSELECTED_AND_GITLINK_UNCHANGED')
        need(all(name not in actual for name in omitted), 'RAW_OMISSIONS_UNINDEXED')
        unchanged = lib.ids(index)[1] == INDEX
        need(a.mode != 'shadow' or unchanged, 'LIVE_INDEX_UNCHANGED_SHADOW')
        need(lib.ids(ROOT / 'CLAIMS.yaml')[1] == LEDGER, 'LEDGER_UNCHANGED')
        save(out / 'summary.json', dict(**common, status='WAVE41_EXACT358_' + a.mode.upper() + '_INDEX_RAW_BYTE_PASS' if not failures else 'WAVE41_INDEX_RAW_BYTE_VETO',
             manifest_sha256=a.manifest_sha256, calibration_sha256=a.calibration_sha256, failures=failures, indexed_paths_checked=len(expected),
             direct_bytes_checked=m['direct_bytes'], omitted_raw_count=8, historical_external_sources_checked=1,
             document_historical_suffixes_checked=4, unselected_entries_changed=outside, submodule_entries_preserved=True,
             live_index_mutated=not unchanged, index_after_sha256=lib.ids(index)[1], shadow_index_path=str(shadow) if shadow else None,
             committed=False, published=False, availability_changed=False, deadline=d.status()))
        need(not failures, 'RAW_INDEX_VETO')
    except BaseException as error:
        save(out / 'failure.json', dict(error=repr(error), index_operation_started=started, mode=a.mode, live_index_sha256=lib.ids(index)[1], deadline=d.status()))
        raise


if __name__ == '__main__':
    main()
