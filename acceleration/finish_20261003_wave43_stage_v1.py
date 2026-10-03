"""Source-only Wave43 receipt appendix, narrowly adapted from preserved Wave42 V1."""
import argparse, ast, copy, hashlib, json, re, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
CONTEXT = 'd0c0dd7db0d3de420b1d718b59122b069df01107'
LEDGER = 'b7d07a8be5cbbce8c2125e631d58f4035ed56a66c2b1e79db27cb56500859f8a'
PARENT = 'acceleration/finish_20261003_wave42_stage_v1.py'
PARENT_SHA = '30506ef337eecb323e45d0e57f9adce76bea3ba15f98f2806fc8407ffe05b32f'
INVENTORY = 'acceleration/results/20261003_wave43_inventory02'
MANIFEST_SHA = 'd6c8030a3dd0064c1a77477042746217822102929011d88f3b6536c446e2cb38'
APPROVED_SHA = '0a52fdfe092567dafe69a5e94dc1a1bc5c5ce27f739bb0640f45f25bc7325b78'
APPLY = 'acceleration/results/20261003_wave43_index_apply01'
APPLY_ROOT_REVIEW = 'acceleration/results/20261003_wave43_root_actual_apply_acceptance01.json'
STAGE_SOURCE = '63402d4a5d3c6978ca222eb37bce7e5875a8ec00efed6c539ea54e9c13d05252'
STAGE_SPEC = 'a259e855e937bb4eb194c837054ae0f1a5d730aa7d3796fda7e52e36061902e5'
STAGE_CAL = 'bac86fb8c463a584f7837b0a3f2112e8521e6f80a69245b48a1aa98f1db51e37'
STAGE_ROOT_REVIEW = 'fd57611700dfd82ac53368b0c1d95a510b9643b6c425687079f526435f53a778'
STAGE_OLD_INDEX = '618367410b57562be69a658a96c48f7dd1908bd3f58bac806d050cdab0c72632'
REGISTRY_PLAN = 'acceleration/plan_20261003_wave43_registry_checks_v1.json'
REGISTRY_ROOT_REVIEW = 'acceleration/results/20261003_wave43_registry_root_acceptance01.json'
STANDARD_RECEIPTS = ('manifest.json', 'summary.json', 'stdout.log', 'stderr.log', 'progress.jsonl')
FIXED_FILES = [
 'acceleration/stage_20261003_wave43_index_v1.py', 'acceleration/stage_20261003_wave43_index_v1_spec.md',
 'acceleration/proposal_20261003_wave43_stage_protocol_v1.json',
 'acceleration/diff_20261003_wave42_wave43_stage_v1.txt',
 'acceleration/plan_20261003_wave43_index_calibration_v1.json',
 'acceleration/plan_20261003_wave43_index_shadow_v1.json',
 'acceleration/plan_20261003_wave43_index_apply_v1.json',
 'acceleration/results/20261003_wave43_index_shadow_admission01.json',
 'acceleration/results/20261003_wave43_index_apply_admission01.json',
 'acceleration/results/20261003_independent_review/wave43_stage_calibration01/summary.json',
 'acceleration/results/20261003_independent_review/wave43_stage_calibration01/controls.json',
 'acceleration/results/20261003_wave43_index_shadow01/summary.json',
 'acceleration/results/20261003_wave43_index_shadow01/exact_stage_paths.nul',
 APPLY + '/summary.json', APPLY + '/exact_stage_paths.nul',
 'acceleration/results/20261003_wave43_root_engineering_review01.json',
 'acceleration/results/20261003_wave43_root_actual_shadow_acceptance01.json',
 'acceleration/results/20261003_wave43_shadow_root_git_row_observation01.json',
 APPLY_ROOT_REVIEW,
 REGISTRY_PLAN, REGISTRY_ROOT_REVIEW,
 'acceleration/results/20261003_wave43_registry_validation01.json',
 'acceleration/results/20261003_wave43_finisher_calibration01/summary.json',
 'acceleration/results/20261003_wave43_finisher_calibration01/controls.json']
COMPLETED_SUPERVISORS = [
 'acceleration/results/20261003_independent_review/wave43_stage_calibration_supervision01',
 'acceleration/results/20261003_wave43_index_shadow_supervision01',
 'acceleration/results/20261003_wave43_index_apply_supervision01',
 'acceleration/results/20261003_wave43_registry_validation_supervision01',
 'acceleration/results/20261003_wave43_registry_tests_supervision01',
 'acceleration/results/20261003_wave43_finisher_calibration_supervision01']
EXTRA_COMPLETED_FILES = [
 'acceleration/plan_20261003_wave43_finisher_calibration_v1.json',
 'acceleration/plan_20261003_wave43_finisher_finish_v1.json',
 'acceleration/plan_20261003_wave43_finisher_finish_v2.json',
 'acceleration/results/20261003_wave43_finisher_calibration_admission01.json',
 'acceleration/results/20261003_wave43_finisher_finish_admission01.json',
 'acceleration/results/20261003_wave43_finisher_calibration_windows_observation01.json',
 'acceleration/results/20261003_wave43_finisher_finish_windows_observation01.json']

DOCS = ['README.md', 'ACTIVE_RESEARCH.md', 'docs/RESEARCH_MAP.md', 'docs/REPRODUCING.md']
MILESTONE = 'docs/RESEARCH_20261003_FORTYTHIRD_WAVE.md'
PATTERN = re.compile(rb'(?:ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{35,}|sk-proj-[A-Za-z0-9_-]{30,}|AKIA[A-Z0-9]{16})')

def need(ok, stage):
    if not ok: raise ValueError(stage)

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, 'JSON_DUPLICATE_KEY')
            result[key] = value
        return result
    return json.loads(path.read_bytes(), object_pairs_hook=pairs)

def bounded(name):
    need(type(name) is str and '\\' not in name and ':' not in name, 'PATH_SYNTAX')
    parts = PurePosixPath(name)
    need(not parts.is_absolute() and not any(p in ('..', '.git') for p in parts.parts), 'PATH_BOUNDARY')
    path = (ROOT / name).resolve()
    need(path.is_relative_to(ROOT) and path.is_file() and not (ROOT/name).is_symlink(), 'PATH_FILE')
    need(path.stat().st_size < 50 * 1024**2, 'PATH_SIZE')
    return path

def entries(raw):
    result = {}
    for item in raw.split(b'\0'):
        if item:
            meta, name = item.split(b'\t', 1)
            mode, identity, stage = meta.decode().split()
            name = name.decode()
            need(stage == '0' and name not in result, 'INDEX_STAGE_OR_DUPLICATE')
            result[name] = (mode, identity)
    return result

def blob(path):
    h = hashlib.sha1(('blob ' + str(path.stat().st_size) + '\0').encode())
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024**2), b''): h.update(block)
    return h.hexdigest()

def approved_paths(raw, identity):
    need(raw.endswith(b'\0'), 'APPROVED_TRAILING_NUL')
    values = raw[:-1].split(b'\0')
    need(len(values) == len(set(values)) == 291 and all(values), 'EXACT_DISTINCT_291_APPROVED_PATHS')
    need(hashlib.sha256(raw).hexdigest() == identity, 'EXACT_APPROVED_NUL_SHA256')
    return [name.decode() for name in values]

def apply_scope(report, applied_index):
    wanted = dict(status='WAVE43_EXACT389_APPLY_INDEX_RAW_BYTE_PASS', source_sha256=STAGE_SOURCE,
                  spec_sha256=STAGE_SPEC, ledger_sha256=LEDGER, index_before_sha256=STAGE_OLD_INDEX,
                  manifest_sha256=MANIFEST_SHA, calibration_sha256=STAGE_CAL, root_review_sha256=STAGE_ROOT_REVIEW, failures=[],
                  indexed_paths_checked=291, direct_records_checked=262, direct_bytes_checked=147927260, prior_PUBLIC_artifact_entries=6054, last_Wave42_changed_subset=119,
                  new_archive_omissions=0, old_archive_rehashes=0, literal_math_map_members=70, literal_math_JSON_ancestors=38, live_index_mutated=True,
                  unselected_entries_changed=[], submodule_entries_preserved=True, committed=False,
                  published=False, availability_changed=False)
    need(type(report) is dict and set(wanted) <= set(report) and 'index_after_sha256' in report, 'APPLY_REQUIRED_FIELDS')
    counts = ['indexed_paths_checked', 'direct_records_checked', 'direct_bytes_checked', 'prior_PUBLIC_artifact_entries', 'last_Wave42_changed_subset', 'new_archive_omissions', 'old_archive_rehashes', 'literal_math_map_members', 'literal_math_JSON_ancestors']
    need(all(type(report[key]) is int for key in counts), 'APPLY_INTEGER_COUNTS')
    need(all(type(report[key]) is type(value) and report[key] == value for key, value in wanted.items()), 'EXACT_APPLY_SCOPE')
    need(type(applied_index) is str and re.fullmatch('[0-9a-f]{64}', applied_index) is not None
         and report['index_after_sha256'] == applied_index, 'EXACT_APPLIED_INDEX')

def blob_scope(report, approved):
    need(type(report.get('selected_paths')) is list and report['selected_paths'] == approved,
         'APPLY_SELECTED_PATHS')
    identities = report.get('expected_raw_blob_ids')
    need(type(identities) is dict and set(identities) == set(approved)
         and all(type(value) is str and re.fullmatch('[0-9a-f]{40}', value) is not None
                 for value in identities.values()), 'APPLY_BLOB_MAP')
    appendix = report.get('explicit_metadata_appendix'); pins = report.get('appendix_sha256')
    need(type(appendix) is list and all(type(name) is str for name in appendix)
         and len(appendix) == len(set(appendix)) == 29 and set(appendix) <= set(approved)
         and type(pins) is dict and set(pins) == set(appendix)
         and all(type(value) is str and re.fullmatch('[0-9a-f]{64}', value) is not None
                 for value in pins.values()), 'APPLY_PRIOR_APPENDIX')

def syntax(raw):
    try: ast.parse(raw.decode('utf8'))
    except (SyntaxError, UnicodeError): raise ValueError('PYTHON_SYNTAX') from None

def controls():
    records = []
    raw = b''.join(('fixture_' + str(i)).encode() + b'\0' for i in range(291))
    identity = hashlib.sha256(raw).hexdigest()
    need(len(approved_paths(raw, identity)) == 291, 'POSITIVE_NUL')
    synthetic = dict(status='WAVE43_EXACT389_APPLY_INDEX_RAW_BYTE_PASS', source_sha256=STAGE_SOURCE,
        spec_sha256=STAGE_SPEC, ledger_sha256=LEDGER, index_before_sha256=STAGE_OLD_INDEX,
        manifest_sha256=MANIFEST_SHA, calibration_sha256=STAGE_CAL, root_review_sha256=STAGE_ROOT_REVIEW, failures=[], indexed_paths_checked=291,
        direct_records_checked=262, direct_bytes_checked=147927260, prior_PUBLIC_artifact_entries=6054, last_Wave42_changed_subset=119, new_archive_omissions=0, old_archive_rehashes=0, literal_math_map_members=70, literal_math_JSON_ancestors=38,
        live_index_mutated=True, unselected_entries_changed=[], submodule_entries_preserved=True,
        committed=False, published=False, availability_changed=False, index_after_sha256='1'*64)
    apply_scope(synthetic, '1'*64)
    syntax(b'value = 1\n')
    records.extend(dict(label=name, outcome='PASS') for name in ('exact291_nul', 'exact_apply_scope', 'valid_python'))
    names = approved_paths(raw, identity)
    synthetic.update(selected_paths=names, expected_raw_blob_ids={name:'0'*40 for name in names},
        explicit_metadata_appendix=names[:29], appendix_sha256={name:'0'*64 for name in names[:29]})
    blob_scope(synthetic, names); records.append(dict(label='complete291_blob_map_and29_appendix', outcome='PASS'))
    def reject(label, callback, stage):
        try: callback()
        except ValueError as error: need(str(error) == stage, 'WRONG_CONTROL_STAGE:' + label)
        else: raise ValueError('CONTROL_FALSE_ACCEPT:' + label)
        records.append(dict(label=label, stage=stage, outcome='REJECTED'))
    reject('nul_truncated', lambda: approved_paths(b'\0'.join(raw[:-1].split(b'\0')[:-1])+b'\0', identity), 'EXACT_DISTINCT_291_APPROVED_PATHS')
    reject('nul_duplicate', lambda: approved_paths(b'\0'.join([b'fixture_0', *raw[:-1].split(b'\0')[1:-1], b'fixture_0'])+b'\0', identity), 'EXACT_DISTINCT_291_APPROVED_PATHS')
    reject('nul_unterminated', lambda: approved_paths(raw[:-1], identity), 'APPROVED_TRAILING_NUL')
    reject('nul_changed_member', lambda: approved_paths(raw.replace(b'fixture_0\0', b'changed_0\0', 1), identity), 'EXACT_APPROVED_NUL_SHA256')
    for key, value, stage in [
        ('status', 'WRONG', 'EXACT_APPLY_SCOPE'), ('source_sha256', '0'*64, 'EXACT_APPLY_SCOPE'),
        ('ledger_sha256', '0'*64, 'EXACT_APPLY_SCOPE'), ('manifest_sha256', '0'*64, 'EXACT_APPLY_SCOPE'),
        ('indexed_paths_checked', 291.0, 'APPLY_INTEGER_COUNTS'), ('prior_PUBLIC_artifact_entries', True, 'APPLY_INTEGER_COUNTS'),
        ('indexed_paths_checked', 290, 'EXACT_APPLY_SCOPE'), ('failures', ['path'], 'EXACT_APPLY_SCOPE'),
        ('unselected_entries_changed', ['path'], 'EXACT_APPLY_SCOPE'), ('submodule_entries_preserved', False, 'EXACT_APPLY_SCOPE'),
        ('published', True, 'EXACT_APPLY_SCOPE'), ('index_after_sha256', '2'*64, 'EXACT_APPLIED_INDEX')]:
        corrupt = copy.deepcopy(synthetic); corrupt[key] = value
        reject('apply_' + key + '_' + str(type(value).__name__), lambda q=corrupt: apply_scope(q, '1'*64), stage)
    missing = copy.deepcopy(synthetic); del missing['indexed_paths_checked']
    reject('apply_missing_field', lambda: apply_scope(missing, '1'*64), 'APPLY_REQUIRED_FIELDS')
    corrupt = copy.deepcopy(synthetic); corrupt['direct_records_checked'] = True
    reject('apply_bool_direct_count', lambda: apply_scope(corrupt, '1'*64), 'APPLY_INTEGER_COUNTS')
    corrupt = copy.deepcopy(synthetic); del corrupt['expected_raw_blob_ids'][names[0]]
    reject('apply_blob_missing', lambda: blob_scope(corrupt, names), 'APPLY_BLOB_MAP')
    corrupt = copy.deepcopy(synthetic); corrupt['expected_raw_blob_ids'][names[0]] = '0'*39
    reject('apply_blob_malformed', lambda: blob_scope(corrupt, names), 'APPLY_BLOB_MAP')
    corrupt = copy.deepcopy(synthetic); corrupt['selected_paths'] = list(reversed(names))
    reject('apply_selected_order', lambda: blob_scope(corrupt, names), 'APPLY_SELECTED_PATHS')
    corrupt = copy.deepcopy(synthetic); del corrupt['appendix_sha256'][names[0]]
    reject('apply_prior_appendix_missing_pin', lambda: blob_scope(corrupt, names), 'APPLY_PRIOR_APPENDIX')
    reject('python_invalid', lambda: syntax(b'def:\n'), 'PYTHON_SYNTAX')
    markers = [b'ghp_'+b'A'*30, b'github_pat_'+b'A'*35, b'sk-proj-'+b'A'*30, b'AKIA'+b'A'*16]
    need(not PATTERN.search(b'benign fixture') and all(PATTERN.search(q) for q in markers), 'MARKER_CONTROLS')
    split = b'benign'+markers[0]; need(PATTERN.search(split[-256:]+b' tail'), 'CROSS_BLOCK_MARKER')
    records.extend(dict(label=name, outcome='PASS') for name in ('benign_marker', 'four_synthetic_markers', 'cross_block_marker'))
    need(sum(r['outcome'] == 'PASS' for r in records) == 7
         and sum(r['outcome'] == 'REJECTED' for r in records) == 23, 'DECLARED_CONTROL_POPULATION')
    return records

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--mode', choices=['calibrate', 'finish'], required=True)
    p.add_argument('--seconds', type=float, required=True); p.add_argument('--out', type=Path, required=True)
    p.add_argument('--source-sha256', required=True); p.add_argument('--spec-sha256', required=True)
    p.add_argument('--protected-index-sha256', required=True)
    for name in ('calibration', 'apply-report'):
        p.add_argument('--' + name, type=Path); p.add_argument('--' + name + '-sha256')
    p.add_argument('--applied-index-sha256')
    p.add_argument('--registry-report-sha256'); p.add_argument('--registry-tests-summary-sha256')
    p.add_argument('--root-apply-review-sha256'); p.add_argument('--registry-plan-sha256'); p.add_argument('--registry-root-review-sha256')
    p.add_argument('--extra-completed', action='append', choices=EXTRA_COMPLETED_FILES, default=[])
    a = p.parse_args()
    d = CommandDeadline(a.seconds, allocation_reason='Exact frozen389 Wave43 receipt appendix/raw-index engineering only; all setup, hashing, scans and Git share invocation;20second save reserve')
    out = a.out.resolve(); need(out.is_relative_to(ROOT) and not out.exists(), 'FRESH_OUTPUT'); out.mkdir(parents=True)
    source = Path(__file__); spec = source.with_name(source.stem + '_spec.md')
    need(sha(source) == a.source_sha256 and sha(spec) == a.spec_sha256 and sha(ROOT/PARENT) == PARENT_SHA, 'EXACT_SOURCE_SPEC_PARENT')
    def tick():
        state = d.status(); need(not state['stop_required'] and state['remaining_seconds'] > 20, 'DEADLINE_RESERVE')
    def git(words):
        tick()
        value = subprocess.check_output(['git', *words], cwd=ROOT, stderr=subprocess.PIPE, timeout=max(1, d.status()['remaining_seconds']-20))
        tick(); return value
    index_name = Path(git(['rev-parse', '--git-path', 'index']).decode().strip())
    index = index_name if index_name.is_absolute() else ROOT/index_name
    need(sha(index) == a.protected_index_sha256 and sha(ROOT/'CLAIMS.yaml') == LEDGER
         and git(['rev-parse', 'HEAD']).decode().strip() == CONTEXT, 'PROTECTED_CONTEXT')
    before = entries(git(['ls-files', '--stage', '-z'])); started = False
    try:
        tested = controls()
        common = dict(timestamp=datetime.now(timezone.utc).isoformat(), source_sha256=a.source_sha256,
            spec_sha256=a.spec_sha256, parent_sha256=PARENT_SHA, command=[sys.executable, *sys.argv], cwd=str(ROOT),
            controls=tested, positive_controls=7, precise_negative_controls=23, mathematical_replays=0,
            source_author='/root/checkpoint_audit', intended_executor='/root', producer='/root',
            source_author_is_not_independent_of_this_implementation=True,
            ledger_sha256=LEDGER, index_before_sha256=a.protected_index_sha256, credential_values_printed=False)
        if a.mode == 'calibrate':
            need(not a.apply_report and not a.calibration and not a.applied_index_sha256 and not a.extra_completed
                 and not a.registry_report_sha256 and not a.registry_tests_summary_sha256
                 and not a.root_apply_review_sha256 and not a.registry_plan_sha256 and not a.registry_root_review_sha256, 'CALIBRATION_NO_ACTUAL')
            need(sha(index) == a.protected_index_sha256 and sha(ROOT/'CLAIMS.yaml') == LEDGER, 'PROTECTED_UNCHANGED')
            (out/'controls.json').write_text(json.dumps(tested, indent=2)+'\n', encoding='utf8', newline='\n')
            result = dict(**common, status='WAVE43_FINISHER_V1_CALIBRATION_PASS', actual_apply_inspected=False, live_index_mutated=False, deadline=d.status())
            tick(); (out/'summary.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf8', newline='\n'); tick(); return
        need(a.calibration and a.calibration_sha256 and sha(a.calibration) == a.calibration_sha256, 'EXACT_CALIBRATION')
        cal = read(a.calibration)
        need(cal['status'] == 'WAVE43_FINISHER_V1_CALIBRATION_PASS' and all(cal[key] == common[key] for key in ('source_sha256', 'spec_sha256', 'parent_sha256', 'controls')), 'APPLICABLE_CALIBRATION')
        need(a.apply_report and a.apply_report.resolve() == ROOT/APPLY/'summary.json' and a.apply_report_sha256
             and sha(a.apply_report) == a.apply_report_sha256 and a.applied_index_sha256 == a.protected_index_sha256, 'EXACT_APPLY_ARGUMENTS')
        apply = read(a.apply_report); apply_scope(apply, a.applied_index_sha256)
        approved_raw = bounded(APPLY+'/exact_stage_paths.nul').read_bytes(); approved = approved_paths(approved_raw, APPROVED_SHA)
        blob_scope(apply, approved)
        need(sha(ROOT/INVENTORY/'manifest.json') == MANIFEST_SHA, 'EXACT_INVENTORY')
        m = read(ROOT/INVENTORY/'manifest.json'); rows = {r['path']:r for r in m['records']}
        need(a.root_apply_review_sha256 and sha(ROOT/APPLY_ROOT_REVIEW) == a.root_apply_review_sha256, 'EXACT_ROOT_APPLY_REVIEW')
        review = read(ROOT/APPLY_ROOT_REVIEW)
        need(review['result'] == 'PASS' and review['apply_summary_sha256'] == a.apply_report_sha256
             and review['observed_index_sha256'] == a.applied_index_sha256
             and type(review['selected_distinct']) is int and review['selected_distinct'] == 291
             and type(review['appendix_count']) is int and review['appendix_count'] == 29
             and type(review['mathematical_replays']) is int and review['mathematical_replays'] == 0,
             'ROOT_APPLY_REVIEW_SCOPE')
        names = list(FIXED_FILES) + [source.relative_to(ROOT).as_posix(), spec.relative_to(ROOT).as_posix()]
        for prefix in COMPLETED_SUPERVISORS:
            s = read(ROOT/prefix/'summary.json')
            need(type(s['command_exit_code']) is int and s['command_exit_code'] == 0
                 and s['cleanup']['reaped'] is True and s['cleanup']['job_active_zero_observed'] is True,
                 'COMPLETED_SUPERVISOR:'+prefix)
            names += [prefix+'/'+name for name in STANDARD_RECEIPTS if (ROOT/prefix/name).is_file()]
        registry_path = ROOT/'acceleration/results/20261003_wave43_registry_validation01.json'
        tests_summary = ROOT/'acceleration/results/20261003_wave43_registry_tests_supervision01/summary.json'
        need(a.registry_plan_sha256 and a.registry_root_review_sha256
             and sha(ROOT/REGISTRY_PLAN) == a.registry_plan_sha256
             and sha(ROOT/REGISTRY_ROOT_REVIEW) == a.registry_root_review_sha256, 'EXACT_REGISTRY_PLAN_REVIEW')
        need(a.registry_report_sha256 and a.registry_tests_summary_sha256 and sha(registry_path) == a.registry_report_sha256
             and sha(tests_summary) == a.registry_tests_summary_sha256, 'EXACT_REGISTRY_ARGUMENTS')
        valid = read(registry_path)
        need(valid['valid'] is True and valid['errors'] == [], 'REGISTRY_VALIDATION')
        stderr = (ROOT/'acceleration/results/20261003_wave43_registry_tests_supervision01/stderr.log').read_text()
        need('Ran 56 tests' in stderr and stderr.rstrip().endswith('OK'), 'REGISTRY_TESTS')
        names += a.extra_completed
        appendix = sorted(set(names)); selected = sorted(set(approved) | set(appendix))
        pins = {}; expected = {}; python_paths = []; document_checks = []
        for name in DOCS:
            old = git(['show', CONTEXT+':'+name]); current = bounded(name).read_bytes()
            need(current.endswith(old) and (len(current), hashlib.sha256(current).hexdigest())
                 == (rows[name]['bytes'], rows[name]['sha256']), 'DOCUMENT_EXACT_GIT_SUFFIX:'+name)
            document_checks.append(dict(path=name, historical_git_commit=CONTEXT,
                historical_git_sha256=hashlib.sha256(old).hexdigest(), current_sha256=hashlib.sha256(current).hexdigest(), suffix_byte_exact=True))
        need(document_checks == apply['document_checks'], 'APPLIED_DOCUMENT_CHECKS')
        milestone = bounded(MILESTONE)
        need((milestone.stat().st_size,sha(milestone)) == (rows[MILESTONE]['bytes'],rows[MILESTONE]['sha256']), 'MILESTONE_FROZEN_INVENTORY_BYTES')
        for name in selected:
            tick(); path = bounded(name); expected[name] = blob(path)
            if name in approved: need(expected[name] == apply['expected_raw_blob_ids'][name], 'APPROVED_RAW_IDENTITY:'+name)
            if name in appendix: pins[name] = sha(path)
            if path.suffix == '.py': syntax(path.read_bytes()); python_paths.append(name)
            if path.suffix == '.gz': continue
            with path.open('rb') as handle:
                tail = b''
                for block in iter(lambda: handle.read(1024**2), b''):
                    tick(); need(not PATTERN.search(tail+block), 'CREDENTIAL_MARKER_VETO_PATH:'+name); tail = block[-256:]
        need(sha(index) == a.applied_index_sha256 and sha(ROOT/'CLAIMS.yaml') == LEDGER, 'UNCHANGED_BEFORE_APPENDIX')
        nul = out/'appendix_paths.nul'; nul.write_bytes(b''.join(name.encode()+b'\0' for name in appendix)); started = True
        git(['add', '-f', '--pathspec-from-file='+str(nul), '--pathspec-file-nul'])
        after = entries(git(['ls-files', '--stage', '-z']))
        need(all(after.get(name, (None, None))[1] == identity for name, identity in expected.items()), 'ALL_SELECTED_RAW_INDEX_BLOBS')
        need(all(after.get(name) == value for name, value in before.items() if name not in expected)
             and not any(name not in before and name not in expected for name in after), 'OUTSIDE_ENTRIES_UNCHANGED')
        need(all(after.get(name) == value for name, value in before.items() if value[0] == '160000')
             and sha(ROOT/'CLAIMS.yaml') == LEDGER, 'GITLINKS_LEDGER_UNCHANGED')
        result = dict(**common, status='WAVE43_FINAL_DECLARED_RECEIPTS_RAW_INDEX_PASS', apply_report_sha256=a.apply_report_sha256,
            registry_report_sha256=a.registry_report_sha256, registry_tests_summary_sha256=a.registry_tests_summary_sha256,
            applied_index_sha256=a.applied_index_sha256, index_after_sha256=sha(index), approved_nul_sha256=APPROVED_SHA,
            approved_distinct_paths=291, appendix_paths=appendix, appendix_sha256=pins, selected_paths_scanned=len(selected),
            python_ast_checked_paths=python_paths, document_checks=document_checks, frozen_inventory_milestone_byte_exact=True, root_apply_review_sha256=a.root_apply_review_sha256,
            registry_plan_sha256=a.registry_plan_sha256, registry_root_review_sha256=a.registry_root_review_sha256,
            all_selected_raw_index_blobs_checked=True, original_index_entries_preserved=True, submodule_entries_preserved=True,
            ledger_unchanged=True, committed=False, published=False, availability_changed=False, deadline=d.status())
        tick(); (out/'summary.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf8', newline='\n'); tick()
        print(json.dumps(dict(status=result['status'], appendix_paths=len(appendix), selected_paths_scanned=len(selected))))
    except BaseException as error:
        (out/'failure.json').write_text(json.dumps(dict(error=str(error), index_operation_started=started,
            mode=a.mode, live_index_sha256=sha(index), deadline=d.status()), indent=2)+'\n', encoding='utf8', newline='\n')
        raise

if __name__ == '__main__': main()
