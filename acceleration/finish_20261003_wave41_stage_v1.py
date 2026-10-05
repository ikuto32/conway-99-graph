"""Source-only Wave41 receipt appendix, adapted from preserved Wave40 V3."""
import argparse, ast, copy, hashlib, json, re, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
CONTEXT = '00ffb6fdd7d91bd38269e1cc5e6b214ebf7591c8'
LEDGER = '10b7636dafced40101ccf257d5f80468914f53aa2ee2d3c89db43be268bdcc09'
PARENT = 'acceleration/finish_20261003_wave40_stage_v3.py'
PARENT_SHA = 'd49507851370afe6875bc6712946f4102e07a24b3733b5d6d4bc784084064ad1'
PREPARE = 'acceleration/plan_20261003_wave41_milestone_prepare_v1.json'
PREPARE_SHA = '249ff67f1865c6abdc0b9188d01dd36b48caecd3d9f89eb11503f60080392f8c'
MILESTONE = 'acceleration/results/20261003_wave41_milestone01'
MANIFEST_SHA = '89b949f245f9d3bf9a8f48358a1f0d5f22b00b43c81f40382ee899b146f00936'
APPROVED_SHA = 'ae797ec99112804a2ce0f4c2f95367e6f26c6fb82a30d05c274a86eebde4fa47'
APPLY = 'acceleration/results/20261003_independent_review/wave41_index_apply01'
STAGE_SOURCE = '686e3c383447195e65e2f5c200ec751fe1e5ac498e159a47b8a2259aa45c7e88'
STAGE_SPEC = '5fc6bdf1616079833ed1211229a27741e8b2f627c14ae8ed43a5d23fac114851'
STAGE_CAL = '4f13d484c9167a757c80254f4c383ad05ecc055a76585bcc7bc203a7d0957574'
STAGE_OLD_INDEX = '8bcd46056145e09d225a01e553151abd1958364077a85b5c6d1bc33fe4f4cacd'
STANDARD_RECEIPTS = ('manifest.json', 'summary.json', 'stdout.log', 'stderr.log', 'progress.jsonl')
LATE_ROOTS = [
 'acceleration/results/20261003_wave41_milestone_calibration01',
 'acceleration/results/20261003_wave41_milestone_calibration_supervision01',
 'acceleration/results/20261003_wave41_milestone_calibration_admission_supervision01',
 'acceleration/results/20261003_wave41_milestone_calibration_admission_supervision02',
 'acceleration/results/20261003_wave41_milestone_windows_observation_supervision01']
LATE_FILES = [
 'acceleration/plan_20261003_wave41_milestone_author_calibration_v1.json', PREPARE,
 'acceleration/results/20261003_wave41_milestone_calibration_admission_correction01.json',
 'acceleration/results/20261003_wave41_milestone_calibration_admission02.json',
 'acceleration/results/20261003_wave41_milestone_windows_observation01.json']
FIXED_FILES = [
 'acceleration/stage_20261003_wave41_index_v1.py', 'acceleration/stage_20261003_wave41_index_v1_spec.md',
 'acceleration/stage_20261003_wave41_index_v2.py', 'acceleration/stage_20261003_wave41_index_v2_spec.md',
 'acceleration/audit_20261003_wave41_index_v1_review.md', 'acceleration/audit_20261003_wave41_index_v2_review.md',
 'acceleration/plan_20261003_wave41_index_calibration_v2.json', 'acceleration/plan_20261003_wave41_index_shadow_v2.json',
 'acceleration/plan_20261003_wave41_index_apply_v2.json', 'acceleration/plan_20261003_wave41_index_apply_v3.json',
 'acceleration/results/20261003_wave41_index_shadow_admission01.json',
 'acceleration/results/20261003_wave41_index_apply_admission01.json',
 'acceleration/results/20261003_independent_review/wave41_stage_calibration01/summary.json',
 'acceleration/results/20261003_independent_review/wave41_index_shadow01/summary.json',
 'acceleration/results/20261003_independent_review/wave41_index_shadow01/exact_stage_paths.nul',
 APPLY + '/summary.json', APPLY + '/exact_stage_paths.nul',
 'acceleration/results/20261003_wave41_registry_validation01.json',
 'acceleration/plan_20261003_wave41_registry_engineering_v1.json',
 'acceleration/results/20261003_wave41_finisher_calibration01/summary.json',
 'acceleration/results/20261003_wave41_finisher_calibration01/controls.json']
COMPLETED_SUPERVISORS = [
 'acceleration/results/20261003_wave41_milestone_supervision01',
 'acceleration/results/20261003_wave41_milestone_prepare_admission_supervision01',
 'acceleration/results/20261003_wave41_milestone_prepare_windows_observation_supervision01',
 'acceleration/results/20261003_independent_review/wave41_stage_calibration_supervision01',
 'acceleration/results/20261003_independent_review/wave41_index_shadow_supervision01',
 'acceleration/results/20261003_independent_review/wave41_index_apply_supervision01',
 'acceleration/results/20261003_wave41_registry_validation_supervision01',
 'acceleration/results/20261003_wave41_registry_tests_supervision01',
 'acceleration/results/20261003_wave41_finisher_calibration_supervision01']
EXTRA_COMPLETED_FILES = [
 'acceleration/results/20261003_wave41_index_apply_windows_observation01.json',
 'acceleration/plan_20261003_wave41_finisher_calibration_v1.json',
 'acceleration/plan_20261003_wave41_finisher_finish_v1.json',
 ]
DOCS = ['README.md', 'ACTIVE_RESEARCH.md', 'docs/RESEARCH_MAP.md', 'docs/REPRODUCING.md']
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
    need(path.is_relative_to(ROOT) and path.is_file() and not path.is_symlink(), 'PATH_FILE')
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
    need(len(values) == len(set(values)) == 466 and all(values), 'EXACT_DISTINCT_466_APPROVED_PATHS')
    need(hashlib.sha256(raw).hexdigest() == identity, 'EXACT_APPROVED_NUL_SHA256')
    return [name.decode() for name in values]

def apply_scope(report, applied_index):
    wanted = dict(status='WAVE41_EXACT358_APPLY_INDEX_RAW_BYTE_PASS', source_sha256=STAGE_SOURCE,
                  spec_sha256=STAGE_SPEC, ledger_sha256=LEDGER, index_before_sha256=STAGE_OLD_INDEX,
                  manifest_sha256=MANIFEST_SHA, calibration_sha256=STAGE_CAL, failures=[],
                  indexed_paths_checked=466, direct_bytes_checked=104861151, omitted_raw_count=8,
                  historical_external_sources_checked=1, document_historical_suffixes_checked=4,
                  unselected_entries_changed=[], submodule_entries_preserved=True, committed=False,
                  published=False, availability_changed=False)
    need(type(report) is dict and set(wanted) <= set(report) and 'index_after_sha256' in report, 'APPLY_REQUIRED_FIELDS')
    counts = ['indexed_paths_checked', 'direct_bytes_checked', 'omitted_raw_count',
              'historical_external_sources_checked', 'document_historical_suffixes_checked']
    need(all(type(report[key]) is int for key in counts), 'APPLY_INTEGER_COUNTS')
    need(all(type(report[key]) is type(value) and report[key] == value for key, value in wanted.items()), 'EXACT_APPLY_SCOPE')
    need(type(applied_index) is str and re.fullmatch('[0-9a-f]{64}', applied_index) is not None
         and report['index_after_sha256'] == applied_index, 'EXACT_APPLIED_INDEX')

def syntax(raw):
    try: ast.parse(raw.decode('utf8'))
    except (SyntaxError, UnicodeError): raise ValueError('PYTHON_SYNTAX') from None

def controls():
    records = []
    raw = b''.join(('fixture_' + str(i)).encode() + b'\0' for i in range(466))
    identity = hashlib.sha256(raw).hexdigest()
    need(len(approved_paths(raw, identity)) == 466, 'POSITIVE_NUL')
    synthetic = dict(status='WAVE41_EXACT358_APPLY_INDEX_RAW_BYTE_PASS', source_sha256=STAGE_SOURCE,
        spec_sha256=STAGE_SPEC, ledger_sha256=LEDGER, index_before_sha256=STAGE_OLD_INDEX,
        manifest_sha256=MANIFEST_SHA, calibration_sha256=STAGE_CAL, failures=[], indexed_paths_checked=466,
        direct_bytes_checked=104861151, omitted_raw_count=8, historical_external_sources_checked=1,
        document_historical_suffixes_checked=4, unselected_entries_changed=[], submodule_entries_preserved=True,
        committed=False, published=False, availability_changed=False, index_after_sha256='1'*64)
    apply_scope(synthetic, '1'*64)
    syntax(b'value = 1\n')
    records.extend(dict(label=name, outcome='PASS') for name in ('exact466_nul', 'exact_apply_scope', 'valid_python'))
    def reject(label, callback, stage):
        try: callback()
        except ValueError as error: need(str(error) == stage, 'WRONG_CONTROL_STAGE:' + label)
        else: raise ValueError('CONTROL_FALSE_ACCEPT:' + label)
        records.append(dict(label=label, stage=stage, outcome='REJECTED'))
    reject('nul_truncated', lambda: approved_paths(b'\0'.join(raw[:-1].split(b'\0')[:-1])+b'\0', identity), 'EXACT_DISTINCT_466_APPROVED_PATHS')
    reject('nul_duplicate', lambda: approved_paths(b'\0'.join([b'fixture_0', *raw[:-1].split(b'\0')[1:-1], b'fixture_0'])+b'\0', identity), 'EXACT_DISTINCT_466_APPROVED_PATHS')
    reject('nul_unterminated', lambda: approved_paths(raw[:-1], identity), 'APPROVED_TRAILING_NUL')
    reject('nul_changed_member', lambda: approved_paths(raw.replace(b'fixture_0\0', b'changed_0\0', 1), identity), 'EXACT_APPROVED_NUL_SHA256')
    for key, value, stage in [
        ('status', 'WRONG', 'EXACT_APPLY_SCOPE'), ('source_sha256', '0'*64, 'EXACT_APPLY_SCOPE'),
        ('ledger_sha256', '0'*64, 'EXACT_APPLY_SCOPE'), ('manifest_sha256', '0'*64, 'EXACT_APPLY_SCOPE'),
        ('indexed_paths_checked', 466.0, 'APPLY_INTEGER_COUNTS'), ('omitted_raw_count', True, 'APPLY_INTEGER_COUNTS'),
        ('indexed_paths_checked', 465, 'EXACT_APPLY_SCOPE'), ('failures', ['path'], 'EXACT_APPLY_SCOPE'),
        ('unselected_entries_changed', ['path'], 'EXACT_APPLY_SCOPE'), ('submodule_entries_preserved', False, 'EXACT_APPLY_SCOPE'),
        ('published', True, 'EXACT_APPLY_SCOPE'), ('index_after_sha256', '2'*64, 'EXACT_APPLIED_INDEX')]:
        corrupt = copy.deepcopy(synthetic); corrupt[key] = value
        reject('apply_' + key + '_' + str(type(value).__name__), lambda q=corrupt: apply_scope(q, '1'*64), stage)
    missing = copy.deepcopy(synthetic); del missing['indexed_paths_checked']
    reject('apply_missing_field', lambda: apply_scope(missing, '1'*64), 'APPLY_REQUIRED_FIELDS')
    reject('python_invalid', lambda: syntax(b'def:\n'), 'PYTHON_SYNTAX')
    markers = [b'ghp_'+b'A'*30, b'github_pat_'+b'A'*35, b'sk-proj-'+b'A'*30, b'AKIA'+b'A'*16]
    need(not PATTERN.search(b'benign fixture') and all(PATTERN.search(q) for q in markers), 'MARKER_CONTROLS')
    split = b'benign'+markers[0]; need(PATTERN.search(split[-256:]+b' tail'), 'CROSS_BLOCK_MARKER')
    records.extend(dict(label=name, outcome='PASS') for name in ('benign_marker', 'four_synthetic_markers', 'cross_block_marker'))
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
    p.add_argument('--extra-completed', action='append', choices=EXTRA_COMPLETED_FILES, default=[])
    a = p.parse_args()
    d = CommandDeadline(a.seconds, allocation_reason='Exact frozen358 Wave41 receipt appendix/raw-index engineering only; all setup, hashing, scans and Git share invocation;20second save reserve')
    out = a.out.resolve(); need(out.is_relative_to(ROOT) and not out.exists(), 'FRESH_OUTPUT'); out.mkdir(parents=True)
    source = Path(__file__); spec = source.with_name(source.stem + '_spec.md')
    need(sha(source) == a.source_sha256 and sha(spec) == a.spec_sha256 and sha(ROOT/PARENT) == PARENT_SHA, 'EXACT_SOURCE_SPEC_PARENT')
    def tick(): need(not d.status()['stop_required'] and d.status()['remaining_seconds'] > 20, 'DEADLINE_RESERVE')
    def git(words):
        tick()
        return subprocess.check_output(['git', *words], cwd=ROOT, stderr=subprocess.PIPE, timeout=max(1, d.status()['remaining_seconds']-15))
    index_name = Path(git(['rev-parse', '--git-path', 'index']).decode().strip())
    index = index_name if index_name.is_absolute() else ROOT/index_name
    need(sha(index) == a.protected_index_sha256 and sha(ROOT/'CLAIMS.yaml') == LEDGER
         and git(['rev-parse', 'HEAD']).decode().strip() == CONTEXT, 'PROTECTED_CONTEXT')
    before = entries(git(['ls-files', '--stage', '-z'])); started = False
    try:
        tested = controls()
        common = dict(timestamp=datetime.now(timezone.utc).isoformat(), source_sha256=a.source_sha256,
            spec_sha256=a.spec_sha256, parent_sha256=PARENT_SHA, command=[sys.executable, *sys.argv], cwd=str(ROOT),
            controls=tested, positive_controls=6, precise_negative_controls=18, mathematical_replays=0,
            ledger_sha256=LEDGER, index_before_sha256=a.protected_index_sha256, credential_values_printed=False)
        if a.mode == 'calibrate':
            need(not a.apply_report and not a.calibration and not a.applied_index_sha256 and not a.extra_completed
                 and not a.registry_report_sha256 and not a.registry_tests_summary_sha256, 'CALIBRATION_NO_ACTUAL')
            need(sha(index) == a.protected_index_sha256 and sha(ROOT/'CLAIMS.yaml') == LEDGER, 'PROTECTED_UNCHANGED')
            (out/'controls.json').write_text(json.dumps(tested, indent=2)+'\n', encoding='utf8', newline='\n')
            result = dict(**common, status='WAVE41_FINISHER_V1_CALIBRATION_PASS', actual_apply_inspected=False, live_index_mutated=False, deadline=d.status())
            (out/'summary.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf8', newline='\n'); return
        need(a.calibration and a.calibration_sha256 and sha(a.calibration) == a.calibration_sha256, 'EXACT_CALIBRATION')
        cal = read(a.calibration)
        need(cal['status'] == 'WAVE41_FINISHER_V1_CALIBRATION_PASS' and all(cal[key] == common[key] for key in ('source_sha256', 'spec_sha256', 'parent_sha256', 'controls')), 'APPLICABLE_CALIBRATION')
        need(a.apply_report and a.apply_report.resolve() == ROOT/APPLY/'summary.json' and a.apply_report_sha256
             and sha(a.apply_report) == a.apply_report_sha256 and a.applied_index_sha256 == a.protected_index_sha256, 'EXACT_APPLY_ARGUMENTS')
        apply = read(a.apply_report); apply_scope(apply, a.applied_index_sha256)
        approved_raw = bounded(APPLY+'/exact_stage_paths.nul').read_bytes(); approved = approved_paths(approved_raw, APPROVED_SHA)
        need(sha(ROOT/PREPARE) == PREPARE_SHA and sha(ROOT/MILESTONE/'manifest.json') == MANIFEST_SHA, 'EXACT_PREPARATION')
        prepare = read(ROOT/PREPARE); late = prepare['self_metadata_for_root_finalizer']
        need(late['explicit_roots'] == LATE_ROOTS and late['explicit_files'] == LATE_FILES
             and late['prospective_completed_preparation_roots'] == [MILESTONE, 'acceleration/results/20261003_wave41_milestone_supervision01'], 'EXACT_LATE_METADATA_SELECTION')
        names = list(FIXED_FILES) + LATE_FILES + [source.relative_to(ROOT).as_posix(), spec.relative_to(ROOT).as_posix()]
        names += ['acceleration/results/20261003_wave41_milestone_prepare_admission01.json', 'acceleration/results/20261003_wave41_milestone_prepare_windows_observation01.json']
        for prefix in LATE_ROOTS:
            files = ('summary.json', 'path_controls.json', 'selected_path_inventory.json') if prefix.endswith('milestone_calibration01') else STANDARD_RECEIPTS
            names += [prefix+'/'+name for name in files if (ROOT/prefix/name).is_file()]
        for prefix in COMPLETED_SUPERVISORS:
            s = read(ROOT/prefix/'summary.json')
            need(s['command_exit_code'] == 0 and s['cleanup']['reaped'] is True and s['cleanup']['job_active_zero_observed'] is True, 'COMPLETED_SUPERVISOR:'+prefix)
            names += [prefix+'/'+name for name in STANDARD_RECEIPTS if (ROOT/prefix/name).is_file()]
        registry_path = ROOT/'acceleration/results/20261003_wave41_registry_validation01.json'
        tests_summary = ROOT/'acceleration/results/20261003_wave41_registry_tests_supervision01/summary.json'
        need(a.registry_report_sha256 and a.registry_tests_summary_sha256 and sha(registry_path) == a.registry_report_sha256
             and sha(tests_summary) == a.registry_tests_summary_sha256, 'EXACT_REGISTRY_ARGUMENTS')
        valid = read(registry_path)
        need(valid['valid'] is True and valid['errors'] == [], 'REGISTRY_VALIDATION')
        stderr = (ROOT/'acceleration/results/20261003_wave41_registry_tests_supervision01/stderr.log').read_text()
        need('Ran 56 tests' in stderr and stderr.rstrip().endswith('OK'), 'REGISTRY_TESTS')
        names += a.extra_completed
        appendix = sorted(set(names)); selected = sorted(set(approved) | set(appendix))
        pins = {}; expected = {}; python_paths = []; document_checks = []
        for name in DOCS:
            key = name.replace('/', '_'); old = (ROOT/MILESTONE/(key+'.before')).read_bytes()
            prepared = (ROOT/MILESTONE/(key+'.prepared')).read_bytes()
            need(old == git(['show', CONTEXT+':'+name]) and prepared.endswith(old)
                 and (ROOT/name).read_bytes() == prepared, 'DOCUMENT_EXACT_GIT_SUFFIX:'+name)
            document_checks.append(dict(path=name, prepared_sha256=hashlib.sha256(prepared).hexdigest(), historical_suffix_byte_exact=True))
        need((ROOT/'docs/RESEARCH_20261003_FORTYFIRST_WAVE.md').read_bytes() == (ROOT/MILESTONE/'milestone.prepared.md').read_bytes(), 'MILESTONE_PREPARED_BYTES')
        for name in selected:
            tick(); path = bounded(name); expected[name] = blob(path)
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
        result = dict(**common, status='WAVE41_FINAL_DECLARED_RECEIPTS_RAW_INDEX_PASS', apply_report_sha256=a.apply_report_sha256,
            registry_report_sha256=a.registry_report_sha256, registry_tests_summary_sha256=a.registry_tests_summary_sha256,
            applied_index_sha256=a.applied_index_sha256, index_after_sha256=sha(index), approved_nul_sha256=APPROVED_SHA,
            approved_distinct_paths=466, appendix_paths=appendix, appendix_sha256=pins, selected_paths_scanned=len(selected),
            python_ast_checked_paths=python_paths, document_checks=document_checks, prepared_milestone_byte_exact=True,
            all_selected_raw_index_blobs_checked=True, original_index_entries_preserved=True, submodule_entries_preserved=True,
            ledger_unchanged=True, committed=False, published=False, availability_changed=False, deadline=d.status())
        (out/'summary.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf8', newline='\n')
        print(json.dumps(dict(status=result['status'], appendix_paths=len(appendix), selected_paths_scanned=len(selected))))
    except BaseException as error:
        (out/'failure.json').write_text(json.dumps(dict(error=str(error), index_operation_started=started,
            mode=a.mode, live_index_sha256=sha(index), deadline=d.status()), indent=2)+'\n', encoding='utf8', newline='\n')
        raise

if __name__ == '__main__': main()
