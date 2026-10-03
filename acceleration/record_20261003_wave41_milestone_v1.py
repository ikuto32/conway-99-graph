"""Unexecuted fixed358 milestone/explicit publication preparation; no Git staging."""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys

from command_deadline import CommandDeadline
import validate_claims as registry

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'acceleration/record_20261003_wave41_milestone_v1.py'
SPEC = 'acceleration/record_20261003_wave41_milestone_v1_spec.md'
BEFORE = 'acceleration/results/20261003_wave41_registration01/CLAIMS.before.yaml'
BEFORE_SHA = 'a4f2f5b2ff41ea7aebf99413cdc825fc1e08f5269079d43e305da713f4af29ef'
AFTER_SHA = '10b7636dafced40101ccf257d5f80468914f53aa2ee2d3c89db43be268bdcc09'
IMPACT = 'acceleration/results/20261003_independent_review/wave41_transition_full01/summary.json'
IMPACT_SHA = 'f5d604dfb1d227ea72d45a62738232c530fdafd9f78e2234bb79d535717e83a2'
IDS = ['C-UNRESTRICTED-TRIANGLE-INCIDENCE-WEIGHT5-C4-COLLISION-SUBTRACTION-LOWER-COUNT',
       'C-UNRESTRICTED-TRIANGLE-INCIDENCE-BINARY-RANK-LOWER87']
DOCS = ['README.md', 'ACTIVE_RESEARCH.md', 'docs/RESEARCH_MAP.md', 'docs/REPRODUCING.md']
MILESTONE = 'docs/RESEARCH_20261003_FORTYFIRST_WAVE.md'
REPORTS = {
 'c4': ('acceleration/results/20261003_independent_review/weight5_c4_raw_full02/summary.json', '75bf5f7adc8b082311b4ad786d46f53857960ea07c8cb58576c3a38d2bbce5a5'),
 'rank': ('acceleration/results/20261003_independent_review/c4_endpoint_full01/summary.json', '663c7fffc558e6a45232c08f272230970ff31bcc2d542e3f5c826aaa53dccbc9'),
 'public_receipt': ('acceleration/results/20261003_wave40_publication01/receipt.json', 'db46b1f1a3141242cb1a21e09091a4ba6922c43ce39464d3c03523bf4786ae3a'),
 'public_audit': ('acceleration/results/20261003_independent_review/wave40_availability_full01/summary.json', 'd50b56d9692f39f07e8f447ba3c7a52ee3ea180237e473ee8259ff0816cfc36e')}
ARCHIVE = 'external_conway99_research/attempts/wave102-prism-incidence-code/derivation.md'
ARCHIVE_SHA = 'df8841bee7f23b444186ab65947f77865ffb243363967dd56340207628f00c6f'
ARCHIVE_COMMIT = '85e705cc6c2a14d123120c93a847e30aaab1789e'
ARCHIVE_REPOSITORY = 'https://github.com/YesterdaysLemon/conway-99-research'
PACKAGES = {
 'acceleration/results/20261002_wave33_model_package01/manifest.json': 'c3efa198c5f48eddb5ead69a4bb130a3dc55567bb298856143c6fb62eb0e0145',
 'acceleration/results/20261002_wave33_reconstruction_package01/manifest.json': 'f639431b7ea9ce0f1500ea48b002629d2523271eead700217dd512e8ade66989',
 'acceleration/results/20261003_wave36_coupling_package01/manifest.json': '38f641ec21ec3d1d617515e8b3e578e098886863f7016ad640ac1906e8b0988f',
 'acceleration/results/20261003_wave37_rooted8_package01/manifest.json': 'ea48c30dfa68fe70bad17edbfd3697d8a2dcf28f9ab24b63d0d66895e7eb9b14'}
EXTRA_FILES = [
 '.gitattributes', 'docs/RESEARCH_20261003_FORTIETH_WAVE.md',
 'acceleration/record_20261003_wave40_milestone_v2.py', 'acceleration/record_20261003_wave40_milestone_v2_spec.md',
 'acceleration/register_20261003_bound_claims_v16.py', 'acceleration/register_20261003_bound_claims_v16_spec.md',
 'acceleration/prepare_20261003_registrar_v16_source_v1.py',
 'acceleration/calibrate_20261003_registrar_v16_helpers_v1.py', 'acceleration/calibrate_20261003_registrar_v16_helpers_v1_spec.md',
 'acceleration/audit_20261003_registrar_v16_engineering_v1.py', 'acceleration/audit_20261003_registrar_v16_engineering_v1_spec.md',
 'acceleration/audit_20261003_registrar_v16_engineering_v2.py', 'acceleration/audit_20261003_registrar_v16_engineering_v2_spec.md',
 'acceleration/audit_20261003_registrar_v16_engineering_v3.py', 'acceleration/audit_20261003_registrar_v16_engineering_v3_spec.md',
 'acceleration/audit_20261003_registrar_v16_engineering_v4.py', 'acceleration/audit_20261003_registrar_v16_engineering_v4_spec.md',
 'acceleration/audit_20261003_registrar_v16_engineering_v2_review.md', 'acceleration/audit_20261003_registrar_v16_engineering_v3_review.md',
 'acceleration/audit_20261003_registrar_v16_engineering_v4_review.md',
 'acceleration/plan_20261003_registrar_v16_independent_engineering_v1.json',
 'acceleration/plan_20261003_registrar_v16_independent_engineering_v2.json',
 'acceleration/plan_20261003_registrar_v16_independent_engineering_v3.json',
 'acceleration/audit_20261003_wave41_transition_v1.py', 'acceleration/audit_20261003_wave41_transition_v1_spec.md',
 'acceleration/audit_20261003_wave41_transition_v2.py', 'acceleration/audit_20261003_wave41_transition_v2_spec.md',
 'acceleration/audit_20261003_wave41_transition_v2_review.md',
 'acceleration/confirm_20261003_wave40_publication_v1.py', 'acceleration/confirm_20261003_wave40_publication_v1_spec.md',
 'acceleration/audit_20261003_wave40_publication_producer_v1_review.md',
 'acceleration/audit_20261003_wave40_availability_v1.py', 'acceleration/audit_20261003_wave40_availability_v1_spec.md',
 'acceleration/audit_20261003_wave40_availability_v1_preparation.md']
EXTRA_ROOTS = [
 'acceleration/results/20261003_registrar_v16_helpers01', 'acceleration/results/20261003_registrar_v16_helpers_supervision01',
 'acceleration/results/20261003_registrar_v16_helpers_launch01',
 'acceleration/results/20261003_independent_review/registrar_v16_engineering01',
 'acceleration/results/20261003_independent_review/registrar_v16_engineering_supervision01',
 'acceleration/results/20261003_independent_review/registrar_v16_engineering02',
 'acceleration/results/20261003_independent_review/registrar_v16_engineering_supervision02',
 'acceleration/results/20261003_registrar_v16_registration_prospective01', 'acceleration/results/20261003_registrar_v16_registration_prospective02',
 'acceleration/results/20261003_wave41_registration01', 'acceleration/results/20261003_wave41_registration_supervision01',
 'acceleration/results/20261003_wave41_registration_admission_supervision01', 'acceleration/results/20261003_wave41_registration_observation_supervision01',
 'acceleration/results/20261003_independent_review/wave41_transition_calibration01',
 'acceleration/results/20261003_independent_review/wave41_transition_calibration_supervision01',
 'acceleration/results/20261003_independent_review/wave41_transition_calibration_launch01',
 'acceleration/results/20261003_independent_review/wave41_transition_calibration_admission_supervision01',
 'acceleration/results/20261003_independent_review/wave41_transition_full01',
 'acceleration/results/20261003_independent_review/wave41_transition_full_supervision01',
 'acceleration/results/20261003_independent_review/wave41_transition_full_launch01',
 'acceleration/results/20261003_independent_review/wave41_transition_full_prospective01',
 'acceleration/results/20261003_independent_review/wave41_transition_full_admission_supervision01',
 'acceleration/results/20261003_independent_review/wave41_transition_full_observation_supervision01',
 'acceleration/results/20261003_wave40_publication01', 'acceleration/results/20261003_wave40_publication_supervision01',
 'acceleration/results/20261003_independent_review/wave40_availability_calibration01',
 'acceleration/results/20261003_independent_review/wave40_availability_calibration_supervision01',
 'acceleration/results/20261003_independent_review/wave40_availability_calibration_launch01',
 'acceleration/results/20261003_independent_review/wave40_availability_calibration_launch02',
 'acceleration/results/20261003_independent_review/wave40_availability_full01',
 'acceleration/results/20261003_independent_review/wave40_availability_full_supervision01',
 'acceleration/results/20261003_independent_review/wave40_availability_full_launch01']
DENY = ['ternary_degree14', 'ternary_residue', 'fixed_graph_diagnostics', 'incidence_gf3_rank', 'all_root',
        'strict_lex_step', 'root_focused_chain', 'selected_neighbor_census', 'root_focused_two_line_census',
        'root_focused_neighbor_projection', 'double_fibers_rook9']


class PreparationError(ValueError):
    def __init__(self, stage, detail=''):
        self.stage = stage
        super().__init__(stage + (': ' + detail if detail else ''))


def need(ok, stage, detail=''):
    if not ok:
        raise PreparationError(stage, detail)


def same(left, right):
    if type(left) is not type(right):
        return False
    if type(left) is dict:
        return set(left) == set(right) and all(same(left[k], right[k]) for k in left)
    if type(left) is list:
        return len(left) == len(right) and all(same(a, b) for a, b in zip(left, right))
    return left == right


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def identity(value):
    need(type(value) is str and re.fullmatch('[0-9a-f]{64}', value) is not None, 'LITERAL_SHA256')
    return value


def bounded(name):
    need(type(name) is str and name and not any(c in name for c in '\\\r\n\0'), 'LITERAL_PATH')
    path = PurePosixPath(name)
    need(not path.is_absolute() and '..' not in path.parts and not name.startswith('.git/'), 'RELATIVE_BOUNDARY')
    need(name == ARCHIVE or name.startswith(('acceleration/', 'docs/')) or name in DOCS + ['CLAIMS.yaml', 'pyproject.toml', 'uv.lock', '.gitattributes', '.github/workflows/claims.yml'], 'RESEARCH_NAMESPACE')
    need(not any(term in name.lower() for term in DENY), 'QUEUED_SCIENCE_EXCLUDED')
    need('/build/' not in name and '/recovered/' not in name, 'DUPLICATE_BUILD_EXCLUDED')
    resolved = (ROOT / name).resolve()
    need(resolved.is_relative_to(ROOT), 'RESOLVED_BOUNDARY')
    return resolved


def disposition(name, digest, index):
    if name == '.git/index':
        need(digest == index, 'HISTORICAL_INDEX_IDENTITY')
        return 'OMIT_READONLY_INDEX'
    if name == ARCHIVE:
        need(digest == ARCHIVE_SHA, 'PINNED_ARCHIVE_IDENTITY')
        return 'REFERENCE_PINNED_ARCHIVE'
    bounded(name)
    return 'DIRECT'


def controls(index):
    result = []
    for name, digest, expected in [('CLAIMS.yaml', 'f' * 64, 'DIRECT'), ('.gitattributes', 'f' * 64, 'DIRECT'),
                                 ('docs/REPRODUCING.md', 'f' * 64, 'DIRECT'), ('.git/index', index, 'OMIT_READONLY_INDEX'),
                                 (ARCHIVE, ARCHIVE_SHA, 'REFERENCE_PINNED_ARCHIVE')]:
        need(disposition(name, digest, index) == expected, 'POSITIVE_DISPOSITION')
        result.append(dict(path=name, outcome=expected))
    negative = [('.git/index', '0' * 64, 'HISTORICAL_INDEX_IDENTITY'), (ARCHIVE, 'f' * 64, 'PINNED_ARCHIVE_IDENTITY'),
                ('.git/config', 'f' * 64, 'RELATIVE_BOUNDARY'), ('../CLAIMS.yaml', 'f' * 64, 'RELATIVE_BOUNDARY'),
                ('docs/../a.md', 'f' * 64, 'RELATIVE_BOUNDARY'), ('/tmp/private', 'f' * 64, 'RELATIVE_BOUNDARY'),
                ('C:/private/file', 'f' * 64, 'RESEARCH_NAMESPACE'), ('docs\\a.md', 'f' * 64, 'LITERAL_PATH'),
                ('docs/a\n.md', 'f' * 64, 'LITERAL_PATH'), ('external_conway99_research/CLAIMS.yaml', 'f' * 64, 'RESEARCH_NAMESPACE'),
                ('acceleration/build/x', 'f' * 64, 'DUPLICATE_BUILD_EXCLUDED'), ('acceleration/recovered/x', 'f' * 64, 'DUPLICATE_BUILD_EXCLUDED')]
    negative += [('acceleration/' + token + '.json', 'f' * 64, 'QUEUED_SCIENCE_EXCLUDED') for token in DENY]
    for name, digest, stage in negative:
        try:
            disposition(name, digest, index)
        except PreparationError as error:
            need(error.stage == stage, 'PRECISE_NEGATIVE_STAGE')
            result.append(dict(path=name, outcome='REJECTED', diagnostic=stage))
        else:
            raise PreparationError('FALSE_ACCEPT', name)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['calibrate', 'prepare'], required=True)
    parser.add_argument('--seconds', type=float, required=True)
    parser.add_argument('--out', type=Path, required=True)
    for field in ('source', 'protocol', 'after-ledger', 'impact', 'protected-index'):
        parser.add_argument('--' + field + '-sha256', required=True)
    parser.add_argument('--calibration', type=Path)
    parser.add_argument('--calibration-sha256')
    parser.add_argument('--write-current-docs', action='store_true')
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='Exact fixed358 metadata/publication preparation only; prior9.063second impact plus367MB reused identity checks;20seconds save reserve')
    ledger = identity(args.after_ledger_sha256)
    index = identity(args.protected_index_sha256)
    need(ledger == AFTER_SHA and identity(args.impact_sha256) == IMPACT_SHA, 'FROZEN_ACCEPTED_CUTOFF')
    out = args.out.resolve()
    need(out.is_relative_to(ROOT) and not out.exists(), 'FRESH_OUTPUT')
    out.mkdir(parents=True)
    pins, expected, origins, docs_written = {}, {}, defaultdict(set), []

    def pin(name, wanted=None):
        need(deadline.status()['remaining_seconds'] > 20, 'NOT_COMPLETED_WITHIN_ALLOCATION')
        digest = sha(bounded(name))
        need(wanted is None or digest == wanted, 'INPUT_HASH', name)
        need(name not in pins or pins[name] == digest, 'INPUT_STABLE', name)
        pins[name] = digest
        return digest

    def read(name, wanted):
        pin(name, wanted)
        return json.loads(bounded(name).read_bytes())

    def add(name, origin, wanted=None):
        mode = disposition(name, wanted if wanted is not None else ARCHIVE_SHA if name == ARCHIVE else '', index)
        need(mode != 'OMIT_READONLY_INDEX', 'NO_INDEX_PAYLOAD')
        origins[name].add(origin)
        if wanted is not None:
            need(name not in expected or expected[name] == wanted, 'CONSISTENT_IDENTITY', name)
            expected[name] = wanted

    try:
        pin(SOURCE, identity(args.source_sha256)); pin(SPEC, identity(args.protocol_sha256))
        need(sha(ROOT / '.git/index') == index, 'LIVE_INDEX')
        pin('CLAIMS.yaml', ledger); pin(BEFORE, BEFORE_SHA)
        raw = (ROOT / 'CLAIMS.yaml').read_bytes()
        current, before = registry.read_ledger(ROOT / 'CLAIMS.yaml'), registry.read_ledger(ROOT / BEFORE)
        new = current['claims'][len(before['claims']):]
        need(len(before['claims']) == 356 and len(current['claims']) == 358 and same(current['claims'][:356], before['claims']) and [c['id'] for c in new] == IDS and same(current['target'], before['target']) and current['target']['status'] == 'UNKNOWN', 'EXACT356_TO358')
        counts = dict(Counter(c['status'] for c in current['claims']))
        review = dict(Counter(c['review_state'] for c in current['claims']))
        need(same(counts, {'VERIFIED': 350, 'CANDIDATE': 3, 'REFUTED': 5}) and same(review, {'CLEAR': 358}), 'EXACT_COUNTS')
        impact = read(IMPACT, IMPACT_SHA)
        need(same([impact['status'], impact['actual_transition_inspected'], impact['before_ledger_sha256'], impact['after_ledger_sha256'], impact['new_claim_ids'], impact['prior_claims_artifacts_target_unchanged'], impact['new_exclusions'], impact['new_unrestricted_exclusions']], ['INDEPENDENT_WAVE41_EXACT356_TO358_TRANSITION_V2_PASS', True, BEFORE_SHA, AFTER_SHA, IDS, True, 0, 0]), 'ACCEPTED_ACTUAL_IMPACT')
        artifacts = {a['id']: a for a in current['artifacts']}
        evidence = {}
        for claim in new:
            for aid in claim['evidence']:
                item = artifacts[aid]
                name, digest = item['path'], item['sha256']
                need(name is not None and (name not in evidence or evidence[name] == digest), 'BOUND_EVIDENCE_IDENTITY')
                evidence[name] = digest
        checked = controls(index)
        inventory = []
        for origin, records in [('two_claim_evidence', evidence), ('actual_impact_inputs', impact['inputs_sha256'])]:
            for name, digest in sorted(records.items()):
                mode = disposition(name, digest, index)
                need(mode == 'OMIT_READONLY_INDEX' or bounded(name).is_file(), 'INPUT_EXISTS', name)
                inventory.append(dict(origin=origin, path=name, sha256=digest, disposition=mode))
        for name in EXTRA_FILES:
            need(bounded(name).is_file(), 'EXTRA_FILE_EXISTS', name)
        for name in EXTRA_ROOTS:
            need(bounded(name).is_dir(), 'EXTRA_ROOT_EXISTS', name)
        save(out / 'path_controls.json', checked); save(out / 'selected_path_inventory.json', inventory)
        if args.mode == 'calibrate':
            need(not args.write_current_docs, 'CALIBRATION_CANNOT_WRITE_DOCS')
            need(sha(ROOT / '.git/index') == index and sha(ROOT / 'CLAIMS.yaml') == ledger, 'PROTECTED_UNCHANGED')
            save(out / 'summary.json', dict(status='AUTHOR_WAVE41_FIXED358_PATH_CONTROLS_PASS', timestamp=datetime.now(timezone.utc).isoformat(), inputs_sha256=pins, source_sha256=args.source_sha256, protocol_sha256=args.protocol_sha256, ledger_sha256=ledger, impact_sha256=IMPACT_SHA, index_sha256=index, positive_controls=5, strict_negative_controls=len(checked)-5, selected_unique_evidence_paths=len(evidence), selected_impact_paths=len(impact['inputs_sha256']), generator_prepare_called=False, current_docs_mutated=False, ledger_mutated=False, index_mutated=False, mathematical_replays=0, independent_approval=False))
            print('AUTHOR_WAVE41_FIXED358_PATH_CONTROLS_PASS')
            return
        need(args.calibration and args.calibration_sha256, 'APPLICABLE_AUTHOR_CALIBRATION')
        cal = read(args.calibration.resolve().relative_to(ROOT).as_posix(), identity(args.calibration_sha256))
        need(same([cal['status'], cal['source_sha256'], cal['protocol_sha256'], cal['ledger_sha256'], cal['impact_sha256'], cal['index_sha256'], cal['generator_prepare_called']], ['AUTHOR_WAVE41_FIXED358_PATH_CONTROLS_PASS', args.source_sha256, args.protocol_sha256, ledger, IMPACT_SHA, index, False]), 'EXACT_AUTHOR_CALIBRATION')
        for name, digest in evidence.items(): add(name, 'two exact registered claim evidence', digest)
        for name, digest in impact['inputs_sha256'].items():
            if disposition(name, digest, index) != 'OMIT_READONLY_INDEX': add(name, 'complete actual transition input', digest)
        reports = {key: read(*pair) for key, pair in REPORTS.items()}
        for key, (name, digest) in REPORTS.items(): add(name, 'exact saved ' + key + ' report', digest)
        need(same([reports['public_audit']['status'], reports['public_audit']['unchanged_claims'], reports['public_audit']['after_ledger_sha256'], reports['public_audit']['changed_public_artifact_records'], len(reports['public_audit']['retained_artifact_ids'])], ['INDEPENDENT_WAVE40_AVAILABILITY_V1_ONLY_PUBLIC_TRANSITION_PASS', 356, BEFORE_SHA, 1254, 0]), 'PRIOR_AVAILABILITY_ONLY')
        need(reports['c4']['target_weight5_lower_count'] == 22869 and reports['c4']['universal_derivation_checked'] is True and reports['rank']['conditional_incidence_rank_lower'] == 87 and reports['rank']['maximum_linear_dimension'] == 12 and reports['rank']['exact_size_upper'] == [12187808, 2723], 'EXACT_SAVED_MATHEMATICAL_SCOPE')
        packaged = {}
        for name, digest in PACKAGES.items():
            package = read(name, digest); add(name, 'existing public lossless manifest', digest)
            for row in package['records']:
                need(row['raw_path'] not in packaged, 'DISTINCT_OLD_RAW')
                packaged[row['raw_path']] = row; add(row['raw_path'], 'old raw identity only', row['raw_sha256'])
                offset = 0
                for part in row['parts']:
                    need(part['raw_offset'] == offset, 'LOSSLESS_OFFSETS')
                    offset += part['raw_bytes']; add(part['path'], 'existing public lossless part', part['gzip_sha256'])
                need(offset == row['raw_bytes'], 'LOSSLESS_RAW_LENGTH')
        need(len(packaged) == 8 and sum(row['raw_bytes'] for row in packaged.values()) == 367261301, 'EIGHT_OLD_RAW_IDENTITIES')
        for name in EXTRA_FILES: add(name, 'explicit completed metadata source/history')
        for name in EXTRA_ROOTS:
            for path in sorted(bounded(name).rglob('*')):
                if path.is_file(): add(path.relative_to(ROOT).as_posix(), 'explicit completed metadata root')
        for name in ['CLAIMS.yaml', BEFORE, SOURCE, SPEC, '.gitattributes', 'acceleration/command_deadline.py', 'acceleration/run_compute_command.py', 'acceleration/validate_claims.py', 'docs/claims.schema.json', 'pyproject.toml', 'uv.lock']:
            add(name, 'fixed runtime/current metadata')
        add(args.calibration.resolve().relative_to(ROOT).as_posix(), 'applicable author path calibration', args.calibration_sha256)
        now = datetime.now(timezone.utc).isoformat()
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        attributes = pin('.gitattributes')
        (out / 'CLAIMS.yaml').write_bytes(raw); (out / 'gitattributes.observed').write_bytes((ROOT / '.gitattributes').read_bytes())
        save(out / 'checkpoint.json', dict(timestamp=now, source_commit=commit, ledger_sha256=ledger, before_ledger_sha256=BEFORE_SHA, claim_records=len(current['claims']), status_counts=counts, review_state_counts=review, new_claim_revisions=[{key: claim[key] for key in ('id', 'revision', 'statement', 'scope', 'status')} for claim in new], impact_report=IMPACT, impact_sha256=IMPACT_SHA, new_finite_exclusions=0, new_unrestricted_exclusions=0, target_resolution='UNKNOWN', overall_search_coverage='UNKNOWN; no validated denominator.', prior_publication=REPORTS['public_receipt'], prior_publication_audit=REPORTS['public_audit'], attributes_sha256=attributes, execution_state=None, execution_state_null_reason='Metadata generator performs no live scientific process observation; completed receipts are separately recorded.', queued_results_excluded=DENY))
        rows = '\n'.join('| ' + claim['id'] + ' r1 | ' + claim['scope']['description'] + ' | [Audit](../' + claim['verification'][0]['command_or_audit'] + ') |' for claim in new)
        text = f'''# Forty-first research milestone, 2026-10-03

Since [wave40](RESEARCH_20261003_FORTIETH_WAVE.md), two exact revisions were
added: the universal weight-five C4 collision subtraction bound and the
conditional triangle-incidence binary rank lower bound87. No graph or exclusion
was added. All later graph diagnostics, censuses and ternary results are outside
this frozen358 cutoff.

**As of:** {now}, source commit `{commit}`, [checkpoint](../{out.relative_to(ROOT).as_posix()}/checkpoint.json),
[frozen358 ledger](../{out.relative_to(ROOT).as_posix()}/CLAIMS.yaml), previous
report wave40. Working bytes are separately pinned; the context commit is not
asserted to contain every new file.

**Verdict:** target resolution UNKNOWN; no independently validated target graph
or general nonexistence proof. External resolution review remains unrecorded.
[Draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3) is the review reference.

**Verified changes:** {counts['VERIFIED']} VERIFIED/CLEAR, {counts['CANDIDATE']}
CANDIDATE and {counts['REFUTED']} REFUTED; all{len(current['claims'])} CLEAR.
The [actual impact audit](../{IMPACT}) preserves every prior356 claim,
verification, artifact, PUBLIC field and target field. Both raw report headlines
are literal and nonnull. Two exact combined-method schema projections preserve
the original method; no generic statement or verifier exception is inferred.
Counts derive from the frozen ledger.

| New revision | Exact scope | Evidence |
| --- | --- | --- |
{rows}

**Work completed:** for every finite simple graph with exactly one common
neighbor per adjacent pair, the complete actual-triangle binary image contains
at least max(ceil(P/2), P-c4(G)) weight-five words. P counts unordered
three-triangle paths; c4(G) counts induced four-cycles. The independently written
inverse/injection proof is separate from finite controls. A hypothetical target
has P=24948 and c4=2079, hence N5>=22869 and exact shifted degree-five
character right-hand side71500275. The finite raw audit checks seven fixtures,
62 triangle trios,23 paths,14 separate-fixture supports,9 double fibers,
10 induced four-cycles and234 complete small-image masks, with paired relabel
mapping and100 literal character coefficients. No fixture count proves the
universal theorem.

The exact endpoint audit checks1287 coefficient cells,99 nonnegative rational
dual coordinates and13 even-weight inequalities. Its bound |ker(B^T)| <=
12187808/2723 <8192 forces dimension<=12 and rank(B)>=87 for every hypothetical
target, using the complete99-by231 triangle-incidence matrix. The zero kernel
remains allowed. No rank upper bound, nonzero kernel, divisible-four premise,
numerical optimum or target contradiction is asserted.

The actual metadata command completed in6.250 seconds and the separate typed
impact check in9.063 seconds, both reaped with empty Windows Jobs. Its one
positive and53 precise corruptions check bookkeeping; they do not reapprove
the mathematical proof or exact endpoint certificate.250 immutable checking
pins were authenticated inside the full checking invocation.

**Coverage:** zero new finite exclusions and zero unrestricted exclusions.
Earlier fixed-neighborhood and fixed-support branch records are preserved;
their populations are not added. Overall search coverage: UNKNOWN; no validated
denominator.

**Best result:** the conditional rank lower bound87 and N5>=22869 constrain
every hypothetical target. They provide no graph, exclusion or target-wide
search percentage. Previous finite construction objectives retain their own
definitions and are not rescored in this milestone.

**Problems:** preserved C4 producer controls01 and ROOT registrar engineering01
failed before promotion. The latter stopped on an optional rank87 metadata
field after seven precise controls; no main or live ledger was called. Corrected
versioned sources and fresh gates retain the failure. The earlier rook toy
degree4/5 endpoint was singular and its proposed dual invalid; the reviewer
correction and fresh degree4/6 toy controls remain explicit. The target exact
degree4/5 certificate was checked separately. Timeouts and implementation
failures are not mathematical refutations.

Prior wave40 availability is [independently checked](../{REPORTS['public_audit'][0]}):
1254 artifact records became PUBLIC with356 material claims unchanged. That
immutable confirmation used commit00ffb6fdd7d91bd38269e1cc5e6b214ebf7591c8.
New wave41 evidence remains LOCAL_ONLY pending separate publication checking.
The eight historical raw operators retain48 public lossless pieces; this
generator hashes identities only and does no new recovery or recompression.
The external85e705c source is an immutable historical reference, not a new
submodule verification or copied main-repository payload.

**Execution and next action:** completed receipts establish the saved outcomes;
no current worker is inferred here. Next concrete action is to independently
check the next admitted fixed-root census before using a selected graph as a
construction input. This is a separate queued wave and no automatic search or
ledger mutation is launched by this publication preparation.

**References:** [actual356-to358 impact](../{IMPACT}), [prior publication receipt](../{REPORTS['public_receipt'][0]}),
[prior independent availability](../{REPORTS['public_audit'][0]}), exact
two-claim evidence, versioned failures and completed control/registration/checker
receipts in the explicit manifest. No external acceptance or novelty is inferred.
'''
        notice = f'''# Latest verified continuation checkpoint — wave41, 2026-10-03 JST

The [forty-first milestone](docs/RESEARCH_20261003_FORTYFIRST_WAVE.md) freezes
{len(current['claims'])} claims: {counts['VERIFIED']} VERIFIED/CLEAR,
{counts['CANDIDATE']} CANDIDATE and {counts['REFUTED']} REFUTED. Two additions
establish the universal weight-five C4 collision subtraction bound and the
conditional incidence rank lower bound87. Target resolution remains UNKNOWN.
Zero new finite/unrestricted exclusions; prior scoped records remain unchanged.
Overall search coverage: UNKNOWN; no validated denominator. Wave40 evidence is
separately PUBLIC; new wave41 awaits immutable confirmation. Later queued
science is outside this cutoff. No live worker state is inferred.
Historical text follows unchanged.

'''
        need(not (ROOT / MILESTONE).exists(), 'NEW_MILESTONE_ONLY')
        (out / 'milestone.prepared.md').write_text(text, encoding='utf8', newline='\n')
        for name in DOCS:
            old = (ROOT / name).read_bytes()
            need(b'checkpoint \xe2\x80\x94 wave41' not in old, 'NO_DUPLICATE_NOTICE')
            (out / (name.replace('/', '_') + '.before')).write_bytes(old)
            adjusted = notice.replace('(docs/RESEARCH_', '(RESEARCH_') if name.startswith('docs/') else notice
            prepared = adjusted.encode('utf8') + old
            (out / (name.replace('/', '_') + '.prepared')).write_bytes(prepared)
            if args.write_current_docs:
                (ROOT / name).write_bytes(prepared); docs_written.append(name); add(name, 'notice preserving exact historical suffix')
        if args.write_current_docs:
            (ROOT / MILESTONE).write_text(text, encoding='utf8', newline='\n'); docs_written.append(MILESTONE); add(MILESTONE, 'new ledger-derived milestone')
        records, omitted, references = [], [], []
        for name in sorted(origins):
            path = bounded(name)
            need(path.is_file(), 'ALLOWLIST_FILE_EXISTS', name)
            if name in packaged:
                row = packaged[name]; digest = pin(name, row['raw_sha256'])
                need(path.stat().st_size == row['raw_bytes'], 'OLD_RAW_BYTES')
                omitted.append(dict(path=name, sha256=digest, bytes=row['raw_bytes'], reason='Existing independently confirmed public lossless package; no duplicate raw blob.'))
                continue
            if name == ARCHIVE:
                pin(name, ARCHIVE_SHA)
                actual = subprocess.check_output(['git', '-C', str(ROOT / 'external_conway99_research'), 'rev-parse', 'HEAD'], text=True).strip()
                need(actual == ARCHIVE_COMMIT, 'PINNED_SUBMODULE_COMMIT')
                blob = subprocess.check_output(['git', '-C', str(ROOT / 'external_conway99_research'), 'cat-file', 'blob', ARCHIVE_COMMIT + ':' + name.split('/', 1)[1]])
                need(hashlib.sha256(blob).hexdigest() == ARCHIVE_SHA and blob == path.read_bytes(), 'ARCHIVE_GIT_BLOB')
                references.append(dict(path=name, sha256=ARCHIVE_SHA, bytes=len(blob), repository=ARCHIVE_REPOSITORY, commit=ARCHIVE_COMMIT, external_path=name.split('/', 1)[1], retrieval=ARCHIVE_REPOSITORY + '/blob/' + ARCHIVE_COMMIT + '/' + name.split('/', 1)[1], reason='Immutable historical reference; no submodule payload staging or fresh mathematical verification.'))
                continue
            digest = pin(name, expected.get(name))
            need(path.stat().st_size < 50 * 1024 ** 2, 'DIRECT50MIB_BOUND', name)
            records.append(dict(path=name, sha256=digest, bytes=path.stat().st_size, origins=sorted(origins[name])))
        need(len(references) == 1 and sha(ROOT / '.git/index') == index and sha(ROOT / 'CLAIMS.yaml') == ledger, 'REFERENCE_AND_PROTECTED_UNCHANGED')
        self_names = [path.relative_to(ROOT).as_posix() for path in sorted(out.iterdir()) if path.is_file()] + [(out / 'manifest.json').relative_to(ROOT).as_posix(), (out / 'stage_paths.nul').relative_to(ROOT).as_posix()]
        names = sorted({row['path'] for row in records} | set(self_names))
        need(all(not name.startswith(('.git/', 'external_conway99_research/')) for name in names), 'NO_GIT_OR_SUBMODULE_PAYLOAD')
        (out / 'stage_paths.nul').write_bytes(b''.join(name.encode('utf8') + b'\0' for name in names))
        save(out / 'manifest.json', dict(schema='WAVE41_FIXED358_EXPLICIT_PUBLICATION_ALLOWLIST_V1', timestamp=now, source_commit=commit, ledger_sha256=ledger, before_ledger_sha256=BEFORE_SHA, current_claims=len(current['claims']), previous_claims=len(before['claims']), new_claim_ids=IDS, records=records, direct_record_count=len(records), direct_bytes=sum(row['bytes'] for row in records), omitted=omitted, historical_external_sources=references, old_lossless_packages=PACKAGES, stage_paths_count=len(names), stage_paths_sha256=sha(out / 'stage_paths.nul'), self_metadata_paths=self_names, inputs_sha256=pins, docs_written=docs_written, ledger_mutated=False, index_mutated=False, availability_changed=False, mathematical_replays=0, scientific_launched=False, later_results_excluded=DENY, deadline=deadline.status()))
        print(json.dumps(dict(status='WAVE41_FIXED358_MILESTONE_EXPLICIT_ALLOWLIST_PREPARED', manifest_sha256=sha(out / 'manifest.json'), direct_records=len(records), stage_paths=len(names))))
    except BaseException as error:
        save(out / 'failure.json', dict(exception=type(error).__name__, diagnostic=str(error), stage=getattr(error, 'stage', None), inputs_sha256=pins, docs_written=docs_written, ledger_mutated=False, index_mutated=False, scientific_launched=False, deadline=deadline.status()))
        raise


if __name__ == '__main__':
    main()
