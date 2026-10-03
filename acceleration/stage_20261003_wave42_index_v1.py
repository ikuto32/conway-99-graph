"""SOURCE ONLY: exact371 inventory/raw-index adaptation; no producer imports."""
import argparse
import ast
import copy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
PARENT = 'acceleration/stage_20261003_wave40_index_v2.py'
PARENT_SHA = '11150733d86ee7154eab2c0cc98b239019fb625d0ff44ff16071218d270661f3'
ANCESTOR = 'acceleration/stage_20261003_wave41_index_v2.py'
ANCESTOR_SHA = '686e3c383447195e65e2f5c200ec751fe1e5ac498e159a47b8a2259aa45c7e88'
FINISHER = 'acceleration/finish_20261003_wave41_stage_v1.py'
FINISHER_SHA = 'da594101c452bab25117215cddbb94e18257bbff2d330d38c72dde8a92a998ff'
LEDGER = 'a0ed6dfb9716266e44dd8cdbef00620266190fa1bce0852a11bbabbf8d09416e'
BEFORE = '10b7636dafced40101ccf257d5f80468914f53aa2ee2d3c89db43be268bdcc09'
CONTEXT = '63437c9b9fc2dd58b3bdfb51fc347b880b397503'
INDEX = 'ee2362961d2d160c87ef07b3a0d2f3de4c1378301f561f69a8509e59c87fbf7d'
INVENTORY = 'acceleration/results/20261003_wave42_inventory02'
MANIFEST_SHA = 'bfa9d4fa7c75fc3c7ee3051dbdbda1fac214c897c949f4916892a56a315d16c4'
SELECTED_SHA = 'eb1fde243dbc2c69b21e9a7023d96ec57a3d3fe8f7c5ee9609f3ff1835dd7439'
DIRECT_COUNT, DIRECT_BYTES = 3477, 301664631
IDS = [
    'C-FIXED-LAMBDA1-REGULAR14-TRIANGLE-INCIDENCE-GF3-RANK98',
    'C-FIXED-ROOTFOCUSED-SELECTED45369-COMPLETE99-ROOT-RESIDUALS',
    'C-UNRESTRICTED-DEGREE14-TERNARY-RESIDUE-ENERGY-BOUNDS',
    'C-UNRESTRICTED-DEGREE14-TERNARY-ADJACENCY-EXACTNESS',
    'C-UNRESTRICTED-DEGREE14-TERNARY-SMALL-DEFECT-SUPPORT',
    'C-UNRESTRICTED-DEGREE14-TERNARY-FOUR-DEFECT-NONREALIZABILITY',
    'C-UNRESTRICTED-DEGREE14-TERNARY-SIX-DEFECT-NONREALIZABILITY',
    'C-UNRESTRICTED-DEGREE14-TERNARY-CONNECTED-SUBCUBIC-SUPPORT-RESTRICTION',
    'C-UNRESTRICTED-DEGREE14-TERNARY-CONNECTED-SUBCUBIC-SUPPORT-LOWER45',
    'C-UNRESTRICTED-DEGREE14-TERNARY-CONNECTED-SUBCUBIC-SUPPORT-SPANNING99',
    'C-UNRESTRICTED-DEGREE14-TERNARY-SEVEN-DEFECT-NONREALIZABILITY',
    'C-ROOTFOCUSED-STRICT-LEX-STEP1-FIXED-TWO-LINE-CENSUS',
    'C-ROOTFOCUSED-SELECTED145287-RESTRICTED-THREE-LINE-CENSUS',
]
DOCS = ['README.md', 'ACTIVE_RESEARCH.md', 'docs/RESEARCH_MAP.md', 'docs/REPRODUCING.md']
MILESTONE = 'docs/RESEARCH_20261003_FORTYSECOND_WAVE.md'
DENY = ('ternary_mixed', 'ternary_eight_defect', 'native_active_stop', 'unrestricted_native_full')
PACKAGES = {
    'acceleration/results/20261002_wave33_model_package01/manifest.json': 'c3efa198c5f48eddb5ead69a4bb130a3dc55567bb298856143c6fb62eb0e0145',
    'acceleration/results/20261002_wave33_reconstruction_package01/manifest.json': 'f639431b7ea9ce0f1500ea48b002629d2523271eead700217dd512e8ade66989',
    'acceleration/results/20261003_wave36_coupling_package01/manifest.json': '38f641ec21ec3d1d617515e8b3e578e098886863f7016ad640ac1906e8b0988f',
    'acceleration/results/20261003_wave37_rooted8_package01/manifest.json': 'ea48c30dfa68fe70bad17edbfd3697d8a2dcf28f9ab24b63d0d66895e7eb9b14',
}
MAPS = [
    dict(claim_id=IDS[-2], path='acceleration/results/20261003_fixed_move_census_binding_proposals01/step1/declared_checking_closure.json',
         sha256='11d37bd57a6fc8541f6a7575a0c21e5efb1ce159b4406c04ad2c3ca76b4dce7f', declared_members=2376),
    dict(claim_id=IDS[-1], path='acceleration/results/20261003_fixed_move_census_binding_proposals01/restricted_three_line/declared_checking_closure.json',
         sha256='b1e420b2dcb695a569482e6cb11374f3e24f29d2efffa7c63ff40867198d362c', declared_members=3066),
]
APPENDIX_FILES = [
    'acceleration/inventory_20261003_wave42_v1.py', 'acceleration/inventory_20261003_wave42_v1_spec.md',
    'acceleration/inventory_20261003_wave42_v2.py', 'acceleration/inventory_20261003_wave42_v2_spec.md',
    'acceleration/inventory_20261003_wave42_selection_v1.json',
    'acceleration/inventory_20261003_wave42_selection_v2.json',
    'acceleration/inventory_20261003_wave42_selection_v3.json',
    'acceleration/plan_20261003_wave42_inventory_v1.json',
    'acceleration/plan_20261003_wave42_inventory_v2.json',
    'acceleration/plan_20261003_wave42_inventory_v3.json',
    'acceleration/results/20261003_wave42_inventory_admission01.json',
    'acceleration/results/20261003_wave42_inventory_admission02.json',
    *[f'acceleration/results/20261003_wave42_inventory{number:02}/{name}'
      for number in (1, 2) for name in ('manifest.json', 'selected_paths.nul', 'CLAIMS.yaml')],
]
SUPERVISORS = [
    'acceleration/results/20261003_wave42_inventory_supervision01',
    'acceleration/results/20261003_wave42_inventory_supervision02',
    'acceleration/results/20261003_independent_review/wave42_stage_calibration_supervision01',
]
RECEIPTS = ('manifest.json', 'summary.json', 'stdout.log', 'stderr.log', 'progress.jsonl')
REVIEW_PATH = 'acceleration/results/20261003_wave42_root_engineering_review01.json'
EXTRA_COMPLETED_FILES = [
    'acceleration/plan_20261003_wave42_index_calibration_v1.json',
    'acceleration/plan_20261003_wave42_index_shadow_v1.json',
    'acceleration/plan_20261003_wave42_index_apply_v1.json',
    'acceleration/results/20261003_wave42_index_calibration_admission01.json',
    'acceleration/results/20261003_wave42_index_shadow_admission01.json',
    'acceleration/results/20261003_wave42_index_apply_admission01.json',
]
MARKERS = re.compile(rb'(?:ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{35,}|sk-proj-[A-Za-z0-9_-]{30,}|AKIA[A-Z0-9]{16})')


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


def unique(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, 'DUPLICATE_JSON_KEY')
        result[key] = value
    return result


def read(path):
    return json.loads(path.read_bytes(), object_pairs_hook=unique,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError('NONFINITE_JSON')))


def save(path, value):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def parent():
    for name, identity in ((PARENT, PARENT_SHA), (ANCESTOR, ANCESTOR_SHA), (FINISHER, FINISHER_SHA)):
        need(hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == identity, 'PINNED_SHARED_ENGINEERING')
    spec = importlib.util.spec_from_file_location('wave42_shared_index_helpers', ROOT/PARENT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def notice_suffix(before, prepared, current, git_blob):
    need(before == git_blob, 'BEFORE_DOCUMENT_GIT_BLOB')
    need(prepared.endswith(before), 'DOCUMENT_HISTORICAL_SUFFIX')
    need(current == prepared, 'CURRENT_DOCUMENT_APPROVED_BYTES')


def selected_nul(raw, identity, names):
    need(raw.endswith(b'\0'), 'SELECTED_TRAILING_NUL')
    values = raw[:-1].split(b'\0')
    need(len(values) == len(set(values)) == DIRECT_COUNT and all(values), 'SELECTED_DISTINCT_POPULATION')
    need(hashlib.sha256(raw).hexdigest() == identity
         and raw == b''.join(name.encode('utf8')+b'\0' for name in names), 'SELECTED_EXACT_BYTES')


def syntax(raw):
    try:
        ast.parse(raw.decode('utf8'))
    except (SyntaxError, UnicodeError):
        raise ValueError('PYTHON_SYNTAX') from None


def marker(raw):
    need(not MARKERS.search(raw), 'CREDENTIAL_MARKER')


def scope(m, attrs, lib):
    need([m.get(k) for k in ('schema', 'source_context_commit', 'current_ledger_sha256', 'previous_ledger_sha256', 'claim_ids')]
         == ['WAVE42_FIXED371_EXPLICIT_BYTE_INVENTORY_V2', CONTEXT, LEDGER, BEFORE, IDS], 'FROZEN371_SCOPE')
    need(all(type(m.get(k)) is int for k in ('direct_record_count', 'direct_bytes')), 'INTEGER_COUNTS')
    need((m['direct_record_count'], m['direct_bytes']) == (DIRECT_COUNT, DIRECT_BYTES), 'FROZEN_DIRECT_POPULATION')
    need(all(m.get(k) is False for k in ('ledger_mutated', 'index_mutated', 'availability_changed', 'scientific_launched', 'current_docs_mutated', 'independent_approval'))
         and type(m.get('mathematical_replays')) is int and m['mathematical_replays'] == 0
         and m.get('target_resolution') == 'NONE', 'METADATA_ONLY')
    pins = m.get('inputs_sha256')
    need(type(pins) is dict and pins.get('.gitattributes') == attrs, 'ATTRIBUTES')
    records = m.get('records')
    need(type(records) is list and all(type(row) is dict for row in records), 'DIRECT_RECORDS')
    names = [row.get('path') for row in records]
    need(all(type(name) is str for name in names) and len(names) == len(set(names)) == DIRECT_COUNT
         and names == sorted(names), 'UNIQUE_DIRECT')
    need(all(type(row.get('bytes')) is int and 0 <= row['bytes'] <= 50*1024**2 for row in records), 'DIRECT_SIZE')
    need(sum(row['bytes'] for row in records) == DIRECT_BYTES, 'DIRECT_TOTAL')
    for row in records:
        name = row['path']; lib.bounded(name)
        need(not any(word in name.lower() for word in DENY), 'QUEUED_SCIENCE')
        need(type(row.get('sha256')) is str and re.fullmatch('[0-9a-f]{64}', row['sha256']) is not None
             and pins.get(name) == row['sha256'], 'DIRECT_PINS')
    need(set(DOCS+[MILESTONE, '.gitattributes', 'CLAIMS.yaml']) <= set(names), 'CURRENT_DOCUMENT_MEMBERS')
    omitted_rows = m.get('omitted')
    need(type(omitted_rows) is list and all(type(row) is dict and type(row.get('path')) is str for row in omitted_rows), 'OMITTED_RECORDS')
    omitted = {row['path']: row for row in omitted_rows}
    need(len(omitted) == len(omitted_rows) == 8 and not set(names) & set(omitted), 'EIGHT_OMITTED')
    need(all(type(row.get('bytes')) is int and row['bytes'] > 0 for row in omitted.values())
         and sum(row['bytes'] for row in omitted.values()) == 367261301, 'OLD_RAW_TOTAL')
    need(all(pins.get(name) == row.get('sha256') for name, row in omitted.items())
         and set(pins) == set(names)|set(omitted), 'COMPLETE_INPUT_MAP')
    need(same(m.get('old_lossless_packages'), PACKAGES), 'FOUR_EXACT_PACKAGES')
    maps = m.get('complete_declared_checking_maps')
    need(type(maps) is list and all(type(row.get('declared_members')) is int for row in maps if type(row) is dict), 'CHECKING_MAP_COUNT_TYPES')
    need(same(maps, MAPS), 'TWO_EXACT_CHECKING_MAPS')
    ref = m.get('historical_external_reference')
    need(type(ref) is dict and [ref.get(k) for k in ('path', 'sha256', 'repository', 'commit')]
         == [lib.ARCHIVE, lib.ARCHIVE_SHA, lib.ARCHIVE_REPOSITORY, lib.ARCHIVE_COMMIT], 'ARCHIVE_IDENTITY')
    need(type(ref.get('bytes')) is int and ref['bytes'] == 6085, 'ARCHIVE_BYTES')
    return names, omitted


def fixture(attrs, lib):
    names = sorted(['.gitattributes', 'CLAIMS.yaml', *DOCS, MILESTONE]
                   + [f'acceleration/synthetic_wave42_{j:04}.json' for j in range(DIRECT_COUNT-7)])
    rows = [dict(path=name, bytes=80000, sha256=attrs if name == '.gitattributes' else 'a'*64) for name in names]
    rows[0]['bytes'] += DIRECT_BYTES-sum(row['bytes'] for row in rows)
    omitted = [dict(path=f'acceleration/synthetic_old_raw_{i}', bytes=1 if i else 367261294, sha256='f'*64) for i in range(8)]
    return dict(schema='WAVE42_FIXED371_EXPLICIT_BYTE_INVENTORY_V2', source_context_commit=CONTEXT,
                current_ledger_sha256=LEDGER, previous_ledger_sha256=BEFORE, claim_ids=IDS[:],
                direct_record_count=DIRECT_COUNT, direct_bytes=DIRECT_BYTES, records=rows, omitted=omitted,
                inputs_sha256={row['path']: row['sha256'] for row in rows+omitted}, old_lossless_packages=copy.deepcopy(PACKAGES),
                complete_declared_checking_maps=copy.deepcopy(MAPS), historical_external_reference=dict(path=lib.ARCHIVE,
                    sha256=lib.ARCHIVE_SHA, repository=lib.ARCHIVE_REPOSITORY, commit=lib.ARCHIVE_COMMIT, bytes=6085),
                ledger_mutated=False, index_mutated=False, availability_changed=False, scientific_launched=False,
                current_docs_mutated=False, independent_approval=False, mathematical_replays=0, target_resolution='NONE')


def controls(attrs, lib):
    good = fixture(attrs, lib); names, _ = scope(good, attrs, lib)
    raw = b''.join(name.encode()+b'\0' for name in names); selected_nul(raw, hashlib.sha256(raw).hexdigest(), names)
    original = b'historical document\n'; prepared = b'new notice\n'+original
    notice_suffix(original, prepared, prepared, original); syntax(b'value = 1\n'); marker(b'benign fixture')
    records = [dict(label=label, outcome='PASS') for label in ('synthetic_exact371_scope', 'complete_selected_nul',
                'git_bound_document_suffix', 'valid_python', 'benign_marker')]
    def reject(label, expected, callback):
        try:
            callback()
        except ValueError as error:
            need(str(error) == expected, 'WRONG_CONTROL_STAGE:'+label)
        else:
            raise ValueError('CONTROL_FALSE_ACCEPT:'+label)
        records.append(dict(label=label, expected_stage=expected, actual_stage=expected, outcome='REJECTED'))
    changes = [
        ('schema', 'FROZEN371_SCOPE', lambda m: m.update(schema='WRONG')),
        ('context', 'FROZEN371_SCOPE', lambda m: m.update(source_context_commit='0'*40)),
        ('ledger', 'FROZEN371_SCOPE', lambda m: m.update(current_ledger_sha256='0'*64)),
        ('baseline', 'FROZEN371_SCOPE', lambda m: m.update(previous_ledger_sha256='0'*64)),
        ('ids', 'FROZEN371_SCOPE', lambda m: m.update(claim_ids=IDS[::-1])),
        ('float_count', 'INTEGER_COUNTS', lambda m: m.update(direct_record_count=float(DIRECT_COUNT))),
        ('bool_count', 'INTEGER_COUNTS', lambda m: m.update(direct_record_count=True)),
        ('count', 'FROZEN_DIRECT_POPULATION', lambda m: m.update(direct_record_count=DIRECT_COUNT+1)),
        ('math_bool', 'METADATA_ONLY', lambda m: m.update(mathematical_replays=False)),
        ('science', 'METADATA_ONLY', lambda m: m.update(scientific_launched=True)),
        ('attributes', 'ATTRIBUTES', lambda m: m['inputs_sha256'].update({'.gitattributes':'0'*64})),
        ('duplicate_record', 'UNIQUE_DIRECT', lambda m: m['records'].__setitem__(1, copy.deepcopy(m['records'][0]))),
        ('oversize', 'DIRECT_SIZE', lambda m: m['records'][0].update(bytes=50*1024**2+1)),
        ('total', 'DIRECT_TOTAL', lambda m: m['records'][0].update(bytes=m['records'][0]['bytes']+1)),
        ('traversal', 'BOUNDED_PATH', lambda m: m['records'][0].update(path='../CLAIMS.yaml')),
        ('submodule', 'EXACT_NAMESPACE', lambda m: m['records'][-1].update(path=lib.ARCHIVE)),
        ('queued', 'QUEUED_SCIENCE', lambda m: m['records'][0].update(path='acceleration/ternary_mixed_unapproved.py')),
        ('direct_hash', 'DIRECT_PINS', lambda m: m['records'][0].update(sha256='0'*64)),
        ('omission', 'EIGHT_OMITTED', lambda m: m['omitted'].pop()),
        ('raw_total', 'OLD_RAW_TOTAL', lambda m: m['omitted'][0].update(bytes=1)),
        ('omitted_pin', 'COMPLETE_INPUT_MAP', lambda m: m['inputs_sha256'].update({m['omitted'][0]['path']:'0'*64})),
        ('package', 'FOUR_EXACT_PACKAGES', lambda m: m['old_lossless_packages'].pop(next(iter(PACKAGES)))),
        ('checking_map', 'TWO_EXACT_CHECKING_MAPS', lambda m: m['complete_declared_checking_maps'][0].update(sha256='0'*64)),
        ('map_bool', 'CHECKING_MAP_COUNT_TYPES', lambda m: m['complete_declared_checking_maps'][0].update(declared_members=True)),
        ('archive_hash', 'ARCHIVE_IDENTITY', lambda m: m['historical_external_reference'].update(sha256='0'*64)),
        ('archive_bytes', 'ARCHIVE_BYTES', lambda m: m['historical_external_reference'].update(bytes=6085.0)),
    ]
    for label, expected, mutate in changes:
        bad = copy.deepcopy(good); mutate(bad)
        if label in ('traversal', 'submodule', 'queued'):
            bad['records'].sort(key=lambda row: row['path'])
        reject(label, expected, lambda bad=bad: scope(bad, attrs, lib))
    reject('duplicate_json', 'DUPLICATE_JSON_KEY', lambda: json.loads('{"a":1,"a":2}', object_pairs_hook=unique))
    reject('nonfinite_json', 'NONFINITE_JSON', lambda: json.loads('{"a":NaN}', parse_constant=lambda _: (_ for _ in ()).throw(ValueError('NONFINITE_JSON'))))
    reject('nul_unterminated', 'SELECTED_TRAILING_NUL', lambda: selected_nul(raw[:-1], hashlib.sha256(raw).hexdigest(), names))
    reject('nul_duplicate', 'SELECTED_DISTINCT_POPULATION', lambda: selected_nul(raw+b'CLAIMS.yaml\0', hashlib.sha256(raw).hexdigest(), names))
    reject('nul_wrong_hash', 'SELECTED_EXACT_BYTES', lambda: selected_nul(raw, '0'*64, names))
    reject('malicious_before_and_notice', 'BEFORE_DOCUMENT_GIT_BLOB', lambda: notice_suffix(b'changed', b'noticechanged', b'noticechanged', original))
    reject('historical_suffix', 'DOCUMENT_HISTORICAL_SUFFIX', lambda: notice_suffix(original, b'wrong', b'wrong', original))
    reject('current_document', 'CURRENT_DOCUMENT_APPROVED_BYTES', lambda: notice_suffix(original, prepared, b'wrong', original))
    reject('invalid_python', 'PYTHON_SYNTAX', lambda: syntax(b'def:\n'))
    synthetic_marker = b'ghp_'+b'A'*30
    reject('credential_marker', 'CREDENTIAL_MARKER', lambda: marker(b'benign'+synthetic_marker))
    need(len(records) == 41, 'CONTROL_POPULATION')
    return records


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--mode', choices=['calibrate', 'shadow', 'apply'], required=True)
    p.add_argument('--seconds', type=float, required=True); p.add_argument('--out', type=Path, required=True)
    p.add_argument('--source-sha256', required=True); p.add_argument('--spec-sha256', required=True)
    for name in ('manifest', 'calibration', 'shadow-report', 'root-review'):
        p.add_argument('--'+name, type=Path); p.add_argument('--'+name+'-sha256')
    p.add_argument('--extra-completed', action='append', choices=EXTRA_COMPLETED_FILES, default=[])
    a = p.parse_args()
    d = CommandDeadline(a.seconds, allocation_reason='Exact371 publication raw-byte/index engineering only; all hashes/Git/scans within invocation with20save reserve, no mathematics')
    lib = parent(); out = a.out.resolve()
    need(out.is_relative_to(ROOT) and not out.exists(), 'FRESH_OUTPUT'); out.mkdir(parents=True)
    source = Path(__file__); spec = source.with_name(source.stem+'_spec.md')
    need(lib.ids(source)[1] == a.source_sha256 and lib.ids(spec)[1] == a.spec_sha256, 'EXACT_SOURCE_SPEC')
    def tick(): need(not d.status()['stop_required'] and d.status()['remaining_seconds'] > 20, 'DEADLINE_RESERVE')
    def git(words, env=None):
        tick()
        return subprocess.check_output(['git', *words], cwd=ROOT, env=env, stderr=subprocess.PIPE,
                                       timeout=max(1, d.status()['remaining_seconds']-15))
    index_name = Path(git(['rev-parse', '--git-path', 'index']).decode().strip())
    index = index_name if index_name.is_absolute() else ROOT/index_name
    need(lib.ids(index)[1] == INDEX and lib.ids(ROOT/'CLAIMS.yaml')[1] == LEDGER
         and git(['rev-parse', 'HEAD']).decode().strip() == CONTEXT, 'FROZEN_LEDGER_INDEX_HEAD')
    attrs = lib.ids(ROOT/'.gitattributes')[1]; original = lib.parse_index(git(['ls-files', '--stage', '-z'])); started = False
    try:
        tested = controls(attrs, lib)
        common = dict(timestamp=datetime.now(timezone.utc).isoformat(), source_sha256=a.source_sha256,
                      spec_sha256=a.spec_sha256, ledger_sha256=LEDGER, index_before_sha256=INDEX,
                      source_context_commit=CONTEXT, gitattributes_sha256=attrs, shared_engineering_source=PARENT,
                      shared_engineering_sha256=PARENT_SHA, ancestor_source_sha256=ANCESTOR_SHA,
                      finisher_convention_sha256=FINISHER_SHA, controls=tested, synthetic_positives=5,
                      precise_negatives=36, mathematical_replays=0, command=[sys.executable,*sys.argv], cwd=str(ROOT),
                      source_author='/root/checkpoint_audit', source_author_is_not_independent_of_this_implementation=True)
        if a.mode == 'calibrate':
            need(not a.extra_completed and not any(getattr(a, name) for name in ('manifest', 'calibration', 'shadow_report', 'root_review')), 'CALIBRATION_NO_ACTUAL')
            need(lib.ids(index)[1] == INDEX and lib.ids(ROOT/'CLAIMS.yaml')[1] == LEDGER, 'PROTECTED_UNCHANGED')
            save(out/'controls.json', tested)
            save(out/'summary.json', dict(**common, status='WAVE42_EXACT371_INDEX_CALIBRATION_PASS',
                 actual_manifest_inspected=False, live_index_mutated=False, deadline=d.status())); return
        need(a.calibration and a.calibration.resolve() == ROOT/'acceleration/results/20261003_independent_review/wave42_stage_calibration01/summary.json'
             and a.calibration_sha256 and lib.ids(a.calibration)[1] == a.calibration_sha256, 'EXACT_CALIBRATION')
        cal = read(a.calibration)
        need(cal.get('status') == 'WAVE42_EXACT371_INDEX_CALIBRATION_PASS'
             and all(same(cal.get(k), common[k]) for k in ('source_sha256', 'spec_sha256', 'ledger_sha256', 'index_before_sha256', 'gitattributes_sha256', 'controls')), 'APPLICABLE_CALIBRATION')
        need(a.manifest and a.manifest.resolve() == ROOT/INVENTORY/'manifest.json'
             and a.manifest_sha256 == MANIFEST_SHA and lib.ids(a.manifest)[1] == MANIFEST_SHA, 'EXACT_MANIFEST')
        m = read(a.manifest); names, omitted = scope(m, attrs, lib)
        selected_nul((ROOT/INVENTORY/'selected_paths.nul').read_bytes(), SELECTED_SHA, names)
        need(m.get('selected_paths_sha256') == SELECTED_SHA, 'MANIFEST_SELECTED_NUL')
        expected_pins = {row['path']:row['sha256'] for row in m['records']+m['omitted']}
        for row in MAPS:
            need(expected_pins.get(row['path']) == row['sha256'], 'CHECKING_MAP_SELECTED')
            need(lib.ids(lib.bounded(row['path']))[1] == row['sha256'], 'CHECKING_MAP_IDENTITY')
            members = read(lib.bounded(row['path'])).get('inputs_sha256')
            need(type(members) is dict and len(members) == row['declared_members'], 'CHECKING_MAP_FULL_POPULATION')
            for name, identity in members.items():
                tick()
                historical = name == '.git/index' or name == 'CLAIMS.yaml' and identity != LEDGER
                external = name == lib.ARCHIVE and identity == lib.ARCHIVE_SHA
                need(historical or external or expected_pins.get(name) == identity, 'COMPLETE_CHECKING_MEMBER:'+name)
        ref = m['historical_external_reference']
        need(git(['-C','external_conway99_research','rev-parse','HEAD']).decode().strip() == lib.ARCHIVE_COMMIT, 'ARCHIVE_HEAD')
        archive = git(['-C','external_conway99_research','cat-file','blob',lib.ARCHIVE_COMMIT+':'+lib.ARCHIVE.split('/',1)[1]])
        need(hashlib.sha256(archive).hexdigest() == lib.ARCHIVE_SHA and len(archive) == ref['bytes']
             and archive == (ROOT/lib.ARCHIVE).read_bytes(), 'ARCHIVE_RAW_BLOB')
        packages = {}; parts = []
        for name, identity in PACKAGES.items():
            need(lib.ids(lib.bounded(name))[1] == identity, 'PACKAGE_PIN')
            for row in read(lib.bounded(name))['records']:
                need(row['raw_path'] not in packages, 'UNIQUE_PACKAGE_RAW'); packages[row['raw_path']] = row
                parts += row['parts']
        need(set(packages) == set(omitted) and all((row['raw_sha256'],row['raw_bytes']) == (omitted[name]['sha256'],omitted[name]['bytes']) for name,row in packages.items()), 'EXACT_PACKAGE_OMISSIONS')
        need(len(parts) == 48 and sum(row['gzip_bytes'] for row in parts) == 11723542
             and all(expected_pins.get(row['path']) == row['gzip_sha256'] for row in parts), 'ALL48_PACKAGE_PARTS_SELECTED')
        appendix = list(APPENDIX_FILES)+[source.relative_to(ROOT).as_posix(), spec.relative_to(ROOT).as_posix(),
                                      a.calibration.resolve().relative_to(ROOT).as_posix(),
                                      a.calibration.resolve().parent.relative_to(ROOT).as_posix()+'/controls.json']
        for prefix in SUPERVISORS:
            summary = read(ROOT/prefix/'summary.json')
            need(summary['command_exit_code'] == 0 and summary['cleanup']['reaped'] is True
                 and summary['cleanup']['job_active_zero_observed'] is True, 'COMPLETED_SUPERVISOR:'+prefix)
            appendix += [prefix+'/'+name for name in RECEIPTS if (ROOT/prefix/name).is_file()]
        need(a.root_review and a.root_review.resolve() == ROOT/REVIEW_PATH and a.root_review_sha256
             and lib.ids(a.root_review)[1] == a.root_review_sha256, 'EXACT_ROOT_REVIEW')
        appendix += [REVIEW_PATH,*a.extra_completed]
        stage_names = sorted(set(names)|set(appendix)); expected = {}; appendix_pins = {}; python_paths = []; document_checks = []
        rows = {row['path']:row for row in m['records']}
        for name in DOCS:
            original_blob = git(['show',CONTEXT+':'+name]); current = (ROOT/name).read_bytes()
            notice_suffix(original_blob, current, current, original_blob)
            document_checks.append(dict(path=name, historical_git_commit=CONTEXT,
                historical_git_sha256=hashlib.sha256(original_blob).hexdigest(), current_sha256=hashlib.sha256(current).hexdigest(), suffix_byte_exact=True))
        for name in stage_names:
            tick(); file = lib.bounded(name)
            need(file.is_file() and not (ROOT/name).is_symlink(), 'RAW_MEMBER_FILE')
            size, digest, blob = lib.ids(file); need(size <= 50*1024**2, 'STAGE_SIZE')
            if name in rows: need((size,digest) == (rows[name]['bytes'],rows[name]['sha256']), 'RAW_MEMBER:'+name)
            expected[name] = blob
            if name in appendix: appendix_pins[name] = digest
            if file.suffix == '.py': syntax(file.read_bytes()); python_paths.append(name)
            if file.suffix != '.gz':
                with file.open('rb') as handle:
                    tail = b''
                    for block in iter(lambda:handle.read(1024**2),b''):
                        tick(); need(not MARKERS.search(tail+block), 'CREDENTIAL_MARKER_PATH:'+name); tail = block[-256:]
        for name, row in omitted.items():
            tick(); need(lib.ids(lib.bounded(name))[:2] == (row['bytes'],row['sha256']) and name not in original, 'OMITTED_RAW_IDENTITY')
        if a.mode == 'apply':
            need(a.shadow_report and a.shadow_report_sha256 and lib.ids(a.shadow_report)[1] == a.shadow_report_sha256, 'EXACT_SHADOW_ARGUMENTS')
            gate = read(a.shadow_report)
            need(gate.get('status') == 'WAVE42_EXACT371_SHADOW_INDEX_RAW_BYTE_PASS' and gate.get('failures') == []
                 and gate.get('manifest_sha256') == MANIFEST_SHA and gate.get('calibration_sha256') == a.calibration_sha256
                 and gate.get('selected_paths') == stage_names and same(gate.get('expected_raw_blob_ids'),expected)
                 and same(gate.get('appendix_sha256'),appendix_pins) and gate.get('root_review_sha256') == a.root_review_sha256
                 and all(same(gate.get(k),common[k]) for k in ('source_sha256','spec_sha256','ledger_sha256','index_before_sha256','gitattributes_sha256')), 'APPLICABLE_SHADOW')
        exact = out/'exact_stage_paths.nul'; exact.write_bytes(b''.join(name.encode()+b'\0' for name in stage_names))
        env = os.environ.copy(); shadow = None
        if a.mode == 'shadow':
            shadow = ROOT/'build'/('wave42_'+out.name+'.index'); need(not shadow.exists(), 'FRESH_SHADOW')
            shutil.copy2(index, shadow); env['GIT_INDEX_FILE'] = str(shadow)
        need(lib.ids(index)[1] == INDEX and lib.ids(ROOT/'CLAIMS.yaml')[1] == LEDGER, 'UNCHANGED_BEFORE_INDEX')
        started = True; git(['add','-f','--pathspec-from-file='+str(exact),'--pathspec-file-nul'],env)
        actual = lib.parse_index(git(['ls-files','--stage','-z'],env))
        failures = [name for name,blob in expected.items() if actual.get(name,(None,None))[1] != blob]
        outside = [name for name in set(original)|set(actual) if name not in expected and original.get(name) != actual.get(name)]
        need(not outside and all(actual.get(name) == entry for name,entry in original.items() if entry[0] == '160000'), 'UNSELECTED_AND_GITLINK_UNCHANGED')
        need(all(name not in actual for name in omitted), 'RAW_OMISSIONS_UNINDEXED')
        unchanged = lib.ids(index)[1] == INDEX; need(a.mode != 'shadow' or unchanged, 'LIVE_INDEX_UNCHANGED_SHADOW')
        need(lib.ids(ROOT/'CLAIMS.yaml')[1] == LEDGER, 'LEDGER_UNCHANGED')
        save(out/'summary.json',dict(**common,status='WAVE42_EXACT371_'+a.mode.upper()+'_INDEX_RAW_BYTE_PASS' if not failures else 'WAVE42_INDEX_RAW_BYTE_VETO',
            manifest_sha256=MANIFEST_SHA, calibration_sha256=a.calibration_sha256, failures=failures,
            direct_records_checked=DIRECT_COUNT,direct_bytes_checked=DIRECT_BYTES,selected_paths=stage_names,
            selected_nul_sha256=SELECTED_SHA,indexed_paths_checked=len(expected),explicit_metadata_appendix=sorted(set(appendix)),
            appendix_sha256=appendix_pins,expected_raw_blob_ids=expected,root_review_sha256=a.root_review_sha256,
            python_ast_paths=python_paths,document_checks=document_checks,credential_values_printed=False,
            complete_declared_checking_maps=MAPS,omitted_raw_count=8,omitted_raw_bytes=367261301,
            package_parts_checked=48,historical_external_sources_checked=1,unselected_entries_changed=outside,
            submodule_entries_preserved=True,live_index_mutated=not unchanged,index_after_sha256=lib.ids(index)[1],
            shadow_index_path=str(shadow) if shadow else None,committed=False,published=False,availability_changed=False,deadline=d.status()))
        need(not failures,'RAW_INDEX_VETO')
    except BaseException as error:
        save(out/'failure.json',dict(error=repr(error),index_operation_started=started,mode=a.mode,
             live_index_sha256=lib.ids(index)[1],deadline=d.status(),automatic_retry=False,mathematical_replays=0)); raise


if __name__ == '__main__':
    main()
