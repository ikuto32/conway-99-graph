"""SOURCE ONLY: exact389 raw-index derivative of preserved Wave42 stage."""
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
ANCESTOR = 'acceleration/stage_20261003_wave42_index_v1.py'
ANCESTOR_SHA = '601784ce04bd904aa74a0f4046aa0f562e755a322e2ed10c9bf1723c193cb24e'
FINISHER = 'acceleration/finish_20261003_wave42_stage_v1.py'
FINISHER_SHA = '30506ef337eecb323e45d0e57f9adce76bea3ba15f98f2806fc8407ffe05b32f'
LEDGER = 'b7d07a8be5cbbce8c2125e631d58f4035ed56a66c2b1e79db27cb56500859f8a'
BEFORE = '23ee170c0f7250843ec2852758f0dd7d1324e85647c44e1907a62f062db47da9'
CONTEXT = 'd0c0dd7db0d3de420b1d718b59122b069df01107'
INDEX = '618367410b57562be69a658a96c48f7dd1908bd3f58bac806d050cdab0c72632'
ATTRS = '10856c2a8bbdf8c06f7943aa64e3b5a119daab91c204cb4ac8b19ec1a7088763'
INVENTORY = 'acceleration/results/20261003_wave43_inventory02'
MANIFEST_SHA = 'd6c8030a3dd0064c1a77477042746217822102929011d88f3b6536c446e2cb38'
SELECTED_SHA = '5158db85d28410aeab59885c4180a892b6fb6dff4329d32a714781291337ef01'
PROPOSAL = 'acceleration/proposal_20261003_wave43_publication_paths_v1.json'
PROPOSAL_SHA = 'e2caf73210d5db258380eabc394a8d756b601910441a4d3290fb00325d72cbef'
INVENTORY_REVIEW = 'acceleration/results/20261003_wave43_inventory_v2_root_actual_review01.json'
INVENTORY_REVIEW_SHA = 'ab38803e86439e17ba855671ac73999fff9672c61822b428a5b6827d328a3f50'
DIRECT_COUNT, DIRECT_BYTES = 262, 147927260
IDS = [
  "C-UNRESTRICTED-DEGREE14-TERNARY-PROPER-SUPPORT-NULLITY-LOWER3",
  "C-UNRESTRICTED-DEGREE14-TERNARY-NULLITY2-PROPER-SUPPORT-EXCEPTION98",
  "C-UNRESTRICTED-DEGREE14-TERNARY-EQUAL-OUTSIDE-ROW-BUDGET-FILTER",
  "C-UNRESTRICTED-DEGREE14-TERNARY-NINE-DEFECT-NONREALIZABILITY",
  "C-UNRESTRICTED-DEGREE14-TERNARY-NONZERO-DEFECT-LOWER12",
  "C-UNRESTRICTED-DEGREE14-TERNARY-TWELVE-DEFECT-SUPPORT-CLASSIFICATION",
  "C-UNRESTRICTED-DEGREE14-TERNARY-RESIDUAL-LIFT-EIGEN1-PARITY",
  "C-UNRESTRICTED-DEGREE14-TERNARY-GLOBAL-SUBCUBIC-SUPPORT-LOWER24",
  "C-UNRESTRICTED-DEGREE14-TERNARY-EIGHT-DEFECT-NONREALIZABILITY",
  "C-UNRESTRICTED-DEGREE14-TERNARY-TEN-DEFECT-NONREALIZABILITY",
  "C-UNRESTRICTED-DEGREE14-TERNARY-WHOLE-K2-6-SUPPORT-NONREALIZABILITY",
  "C-UNRESTRICTED-DEGREE14-TERNARY-WHOLE-OCTAHEDRAL-SUPPORT-NONREALIZABILITY",
  "C-UNRESTRICTED-DEGREE14-TERNARY-NONZERO-DEFECT-LOWER13",
  "C-UNRESTRICTED-DEGREE14-TERNARY-THIRTEEN-DEFECT-NONREALIZABILITY",
  "C-UNRESTRICTED-DEGREE14-TERNARY-EQUAL-OUTSIDE-CLASS-LIFT-BUDGET",
  "C-UNRESTRICTED-DEGREE14-TERNARY-NONZERO-DEFECT-LOWER14",
  "C-TERNARY-TWELVE-LINE-CAP-CORE-UNBALANCED-DEPENDENCE",
  "C-TARGET99-TWELVE-LINE-CAP-CORE-COMPLETION-EXCLUSION"
]
DOCS = ['README.md', 'ACTIVE_RESEARCH.md', 'docs/RESEARCH_MAP.md', 'docs/REPRODUCING.md']
MILESTONE = 'docs/RESEARCH_20261003_FORTYTHIRD_WAVE.md'
OWN = ['acceleration/inventory_20261003_wave43_v2.py', 'acceleration/inventory_20261003_wave43_v2_spec.md',
       'acceleration/plan_20261003_wave43_inventory_v2.json', PROPOSAL]
DENY = ('ternary_mixed', 'external_moment', 'seventeen_point_triangle_family', 'unrestricted_native_full')
APPENDIX_FILES = [
    'acceleration/inventory_20261003_wave43_v1.py', 'acceleration/inventory_20261003_wave43_v1_spec.md',
    'acceleration/plan_20261003_wave43_inventory_v1.json',
    'acceleration/diff_20261003_wave43_inventory_v1_v2.txt',
    'acceleration/results/20261003_wave43_inventory_v1_root_static_veto01.json',
    *[INVENTORY+'/'+name for name in ('manifest.json', 'selected_paths.nul', 'CLAIMS.yaml', 'controls.json')],
    'acceleration/results/20261003_wave43_inventory_v2_root_one_authorization01.json', INVENTORY_REVIEW,
]
SUPERVISORS = [
    'acceleration/results/20261003_wave43_inventory_supervision02',
    'acceleration/results/20261003_independent_review/wave43_stage_calibration_supervision01',
]
RECEIPTS = ('manifest.json', 'summary.json', 'stdout.log', 'stderr.log', 'progress.jsonl')
REVIEW_PATH = 'acceleration/results/20261003_wave43_root_engineering_review01.json'
EXTRA_COMPLETED_FILES = [
    'acceleration/plan_20261003_wave43_index_calibration_v1.json',
    'acceleration/plan_20261003_wave43_index_shadow_v1.json',
    'acceleration/results/20261003_wave43_index_shadow_admission01.json',
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
    spec = importlib.util.spec_from_file_location('wave43_shared_index_helpers', ROOT/PARENT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def raw_member(name, lib):
    path = lib.bounded(name)
    cursor = ROOT
    for part in Path(name).parts:
        cursor = cursor/part
        need(not cursor.is_symlink() and not (getattr(os.lstat(cursor), 'st_file_attributes', 0) & 0x400),
             'RAW_MEMBER_REPARSE')
    need(path.is_file(), 'RAW_MEMBER_FILE')
    return path

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
    need(same([m.get(k) for k in ('schema', 'source_context_commit', 'current_ledger_sha256', 'previous_ledger_sha256', 'claim_ids')],
         ['WAVE43_FIXED389_EXPLICIT_BYTE_INVENTORY_V2', CONTEXT, LEDGER, BEFORE, IDS]), 'FROZEN389_SCOPE')
    need(all(type(m.get(k)) is int for k in ('direct_record_count', 'direct_bytes')), 'INTEGER_COUNTS')
    need((m['direct_record_count'], m['direct_bytes']) == (DIRECT_COUNT, DIRECT_BYTES), 'FROZEN_DIRECT_POPULATION')
    need(all(m.get(k) is False for k in ('ledger_mutated', 'index_mutated', 'availability_changed', 'scientific_launched', 'current_docs_mutated', 'independent_approval'))
         and type(m.get('mathematical_replays')) is int and m['mathematical_replays'] == 0
         and m.get('target_resolution') == 'NONE', 'METADATA_ONLY')
    expected = [('total_claims', 389, 'CLAIM_COUNT'), ('status_counts', dict(VERIFIED=381, CANDIDATE=3, REFUTED=5), 'CLAIM_STATUSES'),
                ('review_state_counts', dict(CLEAR=389), 'CLAIM_REVIEW_STATES'), ('prior_PUBLIC_artifact_entries', 6054, 'PRIOR_PUBLIC'),
                ('last_Wave42_changed_subset', 119, 'LAST_PUBLIC_SUBSET'), ('literal_math_map_members', 70, 'MATH_MAP_COUNT'),
                ('literal_math_JSON_ancestors', 38, 'MATH_ANCESTOR_COUNT'), ('base_record_count', 258, 'BASE_RECORD_COUNT')]
    for key, value, stage in expected:
        need(same(m.get(key), value), stage)
    need(same(m.get('own_metadata_paths'), OWN) and type(m.get('own_metadata_count')) is int
         and m['own_metadata_count'] == 4, 'OWN_METADATA')
    need(m.get('base_selection_path') == PROPOSAL and m.get('base_selection_sha256') == PROPOSAL_SHA
         and m.get('old_archives_not_rehashed_or_recovered') is True and m.get('no_new_archive_omissions') is True,
         'EXACT_SELECTION_HISTORY')
    pins = m.get('inputs_sha256'); need(type(pins) is dict, 'DIRECT_INPUT_MAP')
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
    need(set(DOCS+[MILESTONE, 'CLAIMS.yaml']+OWN) <= set(names), 'CURRENT_DOCUMENT_MEMBERS')
    need(set(pins) == set(names), 'COMPLETE_INPUT_MAP')
    return names


def fixture(attrs, lib):
    mandatory = DOCS+[MILESTONE, 'CLAIMS.yaml']+OWN
    names = sorted(mandatory+[f'acceleration/synthetic_wave43_{j:04}.json' for j in range(DIRECT_COUNT-len(mandatory))])
    rows = [dict(path=name, bytes=560000, sha256='a'*64) for name in names]
    rows[0]['bytes'] += DIRECT_BYTES-sum(row['bytes'] for row in rows)
    return dict(schema='WAVE43_FIXED389_EXPLICIT_BYTE_INVENTORY_V2', source_context_commit=CONTEXT,
                current_ledger_sha256=LEDGER, previous_ledger_sha256=BEFORE, claim_ids=IDS[:],
                direct_record_count=DIRECT_COUNT, direct_bytes=DIRECT_BYTES, records=rows,
                inputs_sha256={row['path']: row['sha256'] for row in rows}, total_claims=389,
                status_counts=dict(VERIFIED=381, CANDIDATE=3, REFUTED=5), review_state_counts=dict(CLEAR=389),
                prior_PUBLIC_artifact_entries=6054, last_Wave42_changed_subset=119,
                literal_math_map_members=70, literal_math_JSON_ancestors=38, base_record_count=258,
                own_metadata_count=4, own_metadata_paths=OWN[:], base_selection_path=PROPOSAL,
                base_selection_sha256=PROPOSAL_SHA, old_archives_not_rehashed_or_recovered=True, no_new_archive_omissions=True,
                ledger_mutated=False, index_mutated=False, availability_changed=False, scientific_launched=False,
                current_docs_mutated=False, independent_approval=False, mathematical_replays=0, target_resolution='NONE')

def controls(attrs, lib):
    good = fixture(attrs, lib); names = scope(good, attrs, lib)
    raw = b''.join(name.encode()+b'\0' for name in names); selected_nul(raw, hashlib.sha256(raw).hexdigest(), names)
    original = b'historical document\n'; prepared = b'new notice\n'+original
    notice_suffix(original, prepared, prepared, original); syntax(b'value = 1\n'); marker(b'benign fixture')
    records = [dict(label=label, outcome='PASS') for label in ('synthetic_exact389_scope', 'complete_selected_nul',
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
        ('schema', 'FROZEN389_SCOPE', lambda m: m.update(schema='WRONG')),
        ('context', 'FROZEN389_SCOPE', lambda m: m.update(source_context_commit='0'*40)),
        ('ledger', 'FROZEN389_SCOPE', lambda m: m.update(current_ledger_sha256='0'*64)),
        ('baseline', 'FROZEN389_SCOPE', lambda m: m.update(previous_ledger_sha256='0'*64)),
        ('ids', 'FROZEN389_SCOPE', lambda m: m.update(claim_ids=IDS[::-1])),
        ('float_count', 'INTEGER_COUNTS', lambda m: m.update(direct_record_count=float(DIRECT_COUNT))),
        ('bool_count', 'INTEGER_COUNTS', lambda m: m.update(direct_record_count=True)),
        ('count', 'FROZEN_DIRECT_POPULATION', lambda m: m.update(direct_record_count=DIRECT_COUNT+1)),
        ('math_bool', 'METADATA_ONLY', lambda m: m.update(mathematical_replays=False)),
        ('science', 'METADATA_ONLY', lambda m: m.update(scientific_launched=True)),
        ('duplicate_record', 'UNIQUE_DIRECT', lambda m: m['records'].__setitem__(1, copy.deepcopy(m['records'][0]))),
        ('oversize', 'DIRECT_SIZE', lambda m: m['records'][0].update(bytes=50*1024**2+1)),
        ('total', 'DIRECT_TOTAL', lambda m: m['records'][0].update(bytes=m['records'][0]['bytes']+1)),
        ('traversal', 'BOUNDED_PATH', lambda m: m['records'][0].update(path='../CLAIMS.yaml')),
        ('submodule', 'EXACT_NAMESPACE', lambda m: m['records'][-1].update(path=lib.ARCHIVE)),
        ('queued', 'QUEUED_SCIENCE', lambda m: m['records'][0].update(path='acceleration/external_moment_unapproved.py')),
        ('direct_hash', 'DIRECT_PINS', lambda m: m['records'][0].update(sha256='0'*64)),
        ('claims_bool', 'CLAIM_COUNT', lambda m: m.update(total_claims=True)),
        ('status_bool', 'CLAIM_STATUSES', lambda m: m['status_counts'].update(VERIFIED=True)),
        ('review_float', 'CLAIM_REVIEW_STATES', lambda m: m['review_state_counts'].update(CLEAR=389.0)),
        ('public_subset', 'PRIOR_PUBLIC', lambda m: m.update(prior_PUBLIC_artifact_entries=119)),
        ('last_subset_bool', 'LAST_PUBLIC_SUBSET', lambda m: m.update(last_Wave42_changed_subset=True)),
        ('math_members_float', 'MATH_MAP_COUNT', lambda m: m.update(literal_math_map_members=70.0)),
        ('ancestor_bool', 'MATH_ANCESTOR_COUNT', lambda m: m.update(literal_math_JSON_ancestors=True)),
        ('base_count', 'BASE_RECORD_COUNT', lambda m: m.update(base_record_count=257)),
        ('own_metadata', 'OWN_METADATA', lambda m: m.update(own_metadata_paths=OWN[::-1])),
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
    d = CommandDeadline(a.seconds, allocation_reason='Exact389 publication raw-byte/index engineering only; all hashes/Git/scans within invocation with20save reserve, no mathematics')
    lib = parent(); out = a.out.resolve()
    need(out.is_relative_to(ROOT) and not out.exists(), 'FRESH_OUTPUT'); out.mkdir(parents=True)
    source = Path(__file__); spec = source.with_name(source.stem+'_spec.md')
    need(lib.ids(source)[1] == a.source_sha256 and lib.ids(spec)[1] == a.spec_sha256, 'EXACT_SOURCE_SPEC')
    def tick(): need(not d.status()['stop_required'] and d.status()['remaining_seconds'] > 20, 'DEADLINE_RESERVE')
    def git(words, env=None):
        budget = d.status()
        need(not budget['stop_required'] and budget['remaining_seconds'] > 20, 'DEADLINE_RESERVE')
        return subprocess.check_output(['git', *words], cwd=ROOT, env=env, stderr=subprocess.PIPE,
                                       timeout=budget['remaining_seconds']-20)
    index_name = Path(git(['rev-parse', '--git-path', 'index']).decode().strip())
    index = index_name if index_name.is_absolute() else ROOT/index_name
    need(lib.ids(index)[1] == INDEX and lib.ids(ROOT/'CLAIMS.yaml')[1] == LEDGER
         and git(['rev-parse', 'HEAD']).decode().strip() == CONTEXT, 'FROZEN_LEDGER_INDEX_HEAD')
    attrs = lib.ids(ROOT/'.gitattributes')[1]; need(attrs == ATTRS, 'PINNED_ATTRIBUTES'); original = lib.parse_index(git(['ls-files', '--stage', '-z'])); started = False
    try:
        tested = controls(attrs, lib)
        common = dict(timestamp=datetime.now(timezone.utc).isoformat(), source_sha256=a.source_sha256,
                      spec_sha256=a.spec_sha256, ledger_sha256=LEDGER, index_before_sha256=INDEX,
                      source_context_commit=CONTEXT, gitattributes_sha256=attrs, shared_engineering_source=PARENT,
                      shared_engineering_sha256=PARENT_SHA, ancestor_source_sha256=ANCESTOR_SHA,
                      finisher_convention_sha256=FINISHER_SHA, controls=tested, synthetic_positives=5,
                      precise_negatives=36, mathematical_replays=0, command=[sys.executable,*sys.argv], cwd=str(ROOT),
                      source_author='/root/checkpoint_audit', intended_executor='/root', producer='/root',
                      source_author_is_not_independent_of_this_implementation=True)
        if a.mode == 'calibrate':
            need(not a.extra_completed and not any(getattr(a, name) for name in ('manifest', 'calibration', 'shadow_report', 'root_review')), 'CALIBRATION_NO_ACTUAL')
            need(lib.ids(index)[1] == INDEX and lib.ids(ROOT/'CLAIMS.yaml')[1] == LEDGER, 'PROTECTED_UNCHANGED')
            tick(); save(out/'controls.json', tested)
            save(out/'summary.json', dict(**common, status='WAVE43_EXACT389_INDEX_CALIBRATION_PASS',
                 actual_manifest_inspected=False, live_index_mutated=False, deadline=d.status())); return
        need(a.calibration and a.calibration.resolve() == ROOT/'acceleration/results/20261003_independent_review/wave43_stage_calibration01/summary.json'
             and a.calibration_sha256 and lib.ids(a.calibration)[1] == a.calibration_sha256, 'EXACT_CALIBRATION')
        cal = read(a.calibration)
        need(cal.get('status') == 'WAVE43_EXACT389_INDEX_CALIBRATION_PASS'
             and all(same(cal.get(k), common[k]) for k in ('source_sha256', 'spec_sha256', 'ledger_sha256', 'index_before_sha256', 'gitattributes_sha256', 'controls')), 'APPLICABLE_CALIBRATION')
        need(a.manifest and a.manifest.resolve() == ROOT/INVENTORY/'manifest.json'
             and a.manifest_sha256 == MANIFEST_SHA and lib.ids(a.manifest)[1] == MANIFEST_SHA, 'EXACT_MANIFEST')
        m = read(a.manifest); names = scope(m, attrs, lib)
        selected_nul((ROOT/INVENTORY/'selected_paths.nul').read_bytes(), SELECTED_SHA, names)
        need(m.get('selected_paths_sha256') == SELECTED_SHA, 'MANIFEST_SELECTED_NUL')
        need(lib.ids(ROOT/PROPOSAL)[1] == PROPOSAL_SHA and lib.ids(ROOT/INVENTORY_REVIEW)[1] == INVENTORY_REVIEW_SHA,
             'EXACT_INVENTORY_HISTORY')
        expected_pins = {row['path']: row['sha256'] for row in m['records']}
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
            snapshot = 'acceleration/results/20261003_wave43_documentation01/'+name.replace('/','_')
            before_bytes = raw_member(snapshot+'.before', lib).read_bytes()
            prepared_bytes = raw_member(snapshot+'.prepared', lib).read_bytes()
            notice_suffix(before_bytes, prepared_bytes, current, original_blob)
            document_checks.append(dict(path=name, historical_git_commit=CONTEXT,
                historical_git_sha256=hashlib.sha256(original_blob).hexdigest(), current_sha256=hashlib.sha256(current).hexdigest(), suffix_byte_exact=True))
        for name in stage_names:
            tick(); file = raw_member(name, lib)
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
        if a.mode == 'apply':
            need(a.shadow_report and a.shadow_report_sha256 and lib.ids(a.shadow_report)[1] == a.shadow_report_sha256, 'EXACT_SHADOW_ARGUMENTS')
            gate = read(a.shadow_report)
            need(gate.get('status') == 'WAVE43_EXACT389_SHADOW_INDEX_RAW_BYTE_PASS' and gate.get('failures') == []
                 and gate.get('manifest_sha256') == MANIFEST_SHA and gate.get('calibration_sha256') == a.calibration_sha256
                 and gate.get('selected_paths') == stage_names and same(gate.get('expected_raw_blob_ids'),expected)
                 and same(gate.get('appendix_sha256'),appendix_pins) and gate.get('root_review_sha256') == a.root_review_sha256
                 and all(same(gate.get(k),common[k]) for k in ('source_sha256','spec_sha256','ledger_sha256','index_before_sha256','gitattributes_sha256')), 'APPLICABLE_SHADOW')
        exact = out/'exact_stage_paths.nul'; exact.write_bytes(b''.join(name.encode()+b'\0' for name in stage_names))
        env = os.environ.copy(); shadow = None
        if a.mode == 'shadow':
            shadow = ROOT/'build'/('wave43_'+out.name+'.index'); need(not shadow.exists(), 'FRESH_SHADOW')
            shutil.copy2(index, shadow); env['GIT_INDEX_FILE'] = str(shadow)
        need(lib.ids(index)[1] == INDEX and lib.ids(ROOT/'CLAIMS.yaml')[1] == LEDGER, 'UNCHANGED_BEFORE_INDEX')
        started = True; git(['add','-f','--pathspec-from-file='+str(exact),'--pathspec-file-nul'],env)
        actual = lib.parse_index(git(['ls-files','--stage','-z'],env))
        failures = [name for name,blob in expected.items() if actual.get(name,(None,None))[1] != blob]
        outside = [name for name in set(original)|set(actual) if name not in expected and original.get(name) != actual.get(name)]
        need(not outside and all(actual.get(name) == entry for name,entry in original.items() if entry[0] == '160000'), 'UNSELECTED_AND_GITLINK_UNCHANGED')
        tick(); unchanged = lib.ids(index)[1] == INDEX; need(a.mode != 'shadow' or unchanged, 'LIVE_INDEX_UNCHANGED_SHADOW')
        need(lib.ids(ROOT/'CLAIMS.yaml')[1] == LEDGER and git(['rev-parse','HEAD']).decode().strip() == CONTEXT, 'LEDGER_HEAD_UNCHANGED')
        tick()
        save(out/'summary.json',dict(**common,status='WAVE43_EXACT389_'+a.mode.upper()+'_INDEX_RAW_BYTE_PASS' if not failures else 'WAVE43_INDEX_RAW_BYTE_VETO',
            manifest_sha256=MANIFEST_SHA, calibration_sha256=a.calibration_sha256, failures=failures,
            direct_records_checked=DIRECT_COUNT,direct_bytes_checked=DIRECT_BYTES,selected_paths=stage_names,
            selected_nul_sha256=SELECTED_SHA,indexed_paths_checked=len(expected),explicit_metadata_appendix=sorted(set(appendix)),
            appendix_sha256=appendix_pins,expected_raw_blob_ids=expected,root_review_sha256=a.root_review_sha256,
            python_ast_paths=python_paths,document_checks=document_checks,credential_values_printed=False,
            prior_PUBLIC_artifact_entries=6054,last_Wave42_changed_subset=119,new_archive_omissions=0,
            old_archive_rehashes=0,literal_math_map_members=70,literal_math_JSON_ancestors=38,unselected_entries_changed=outside,
            submodule_entries_preserved=True,live_index_mutated=not unchanged,index_after_sha256=lib.ids(index)[1],
            shadow_index_path=str(shadow) if shadow else None,committed=False,published=False,availability_changed=False,deadline=d.status()))
        need(not failures,'RAW_INDEX_VETO')
    except BaseException as error:
        save(out/'failure.json',dict(error=repr(error),index_operation_started=started,mode=a.mode,
             live_index_sha256=lib.ids(index)[1],deadline=d.status(),automatic_retry=False,mathematical_replays=0)); raise


if __name__ == '__main__':
    main()
