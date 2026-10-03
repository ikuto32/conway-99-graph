"""V2 metadata bindings with literal prior checker-output identities; no replay."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import platform
import subprocess
import sys
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
RANK = dict(id='C-FIXED-LAMBDA1-REGULAR14-TRIANGLE-INCIDENCE-GF3-RANK98',
    report='acceleration/results/20261003_independent_review/incidence_gf3_rank_full01/summary.json',
    report_sha256='c7a65c9a91599b83bee38f22d5031ae5ca7a357818efe1e40541ebf2afd3db02',
    terminal='acceleration/results/20261003_independent_review/incidence_gf3_rank_full_supervision01/summary.json',
    terminal_sha256='261e562a95e8f3bf06440a3bf7c3e0b70ff6f446e2b05b55afd4428546f4e44d',
    raw='acceleration/results/20261003_hypergraph_root_focused_pilot01/native/current.adj',
    raw_sha256='3f910d235e38191b5ac47523c22166f1abfc4d1f3ad285b60d4c684392a6670d',
    raw_audit='acceleration/results/20261003_independent_review/incidence_gf3_rank_full01/exact_rank_audit.json',
    raw_audit_sha256='122e8ec52759ccb43f84b68e47c97d3d2434cb7400bf0f66991ffad218451871',
    raw_audit_bytes=1223,
    graph_census='acceleration/results/20261003_incidence_gf3_rank01/integer_graph_census.json',
    graph_census_sha256='1e5f85e996d7abf6521d57af1533b726803522ef3fdac3d511801d5eb1d37dc2',
    calibration='acceleration/results/20261003_independent_review/incidence_gf3_rank_calibration01/summary.json',
    calibration_sha256='23b484d972726b661a2a3118987658b8339cd507e942eec9cedc23796394022f',
    status='INDEPENDENT_FIXED_NONSRG_INCIDENCE_GF3_COMPLETE_RANK_V4_PASS',
    producer='/root/structural', kind='construction',
    statement='The fixed graph with adjacency SHA256 3f910d235e38191b5ac47523c22166f1abfc4d1f3ad285b60d4c684392a6670d is a 99-vertex simple 14-regular graph in which every adjacent pair has exactly one common neighbor. Its complete 99-by-231 vertex-by-triangle incidence matrix has row weights 7, column weights 3, rank 98 over GF(3), and complete left kernel equal to the span of the constant vector. It fails the SRG99 integer identity at 5500 ordered entries and has unordered nonedge residual energy 5476. It is a counterexample only to an assertion that these incidence and adjacent-pair conditions alone force a nonconstant ternary left-kernel vector.',
    scope='One exact non-SRG graph and its complete triangle incidence. Rank and constant-only left kernel independently certified by modular products, invertible row transformations, complete RREF and an invertible 98-by-98 original minor. No implication using all SRG99 hypotheses is refuted.',
    recorded_validation=dict(rank=98, kernel_dimension=1, constant_only_kernel=True,
                             integer_identity_entries=9801, identity_mismatches=5500,
                             incidence_only_extra_kernel_refuted=True))
PROFILE = dict(id='C-FIXED-ROOTFOCUSED-SELECTED45369-COMPLETE99-ROOT-RESIDUALS',
    report='acceleration/results/20261003_independent_review/all_root_matrix_full01/summary.json',
    report_sha256='8171c054c3d392e4f3b7897575a5170aaf3876c55c1750f3b4083739c34a37d2',
    terminal='acceleration/results/20261003_independent_review/all_root_matrix_supervision01/summary.json',
    terminal_sha256='efe7864c83fa3f10dd8f6abca604981c4bd7f154e8ba602c597b711a6464f3a5',
    raw='acceleration/results/20261003_root_focused_selected_neighbor_census01/best_root_neighbor.adj',
    raw_sha256='928fb10c447a60cf3cc4edc89d95dfa35971ca60c76af5a37ef4685fadcb3131',
    raw_audit='acceleration/results/20261003_independent_review/all_root_matrix_full01/reconstructed_all_root_profile.json',
    raw_audit_sha256='84f378a4fb6befddb5428eb750d344df2413be1287d905ee85f459d3bdf5aa4e',
    raw_audit_bytes=481868,
    identity_audit='acceleration/results/20261003_independent_review/all_root_matrix_full01/ordered_identity_mismatches.json',
    identity_audit_sha256='c1f94924dac20c6ea8e0f8c88d9e4dfd6ed1a3844c98121e54f48432c69e71b2',
    identity_audit_bytes=85348,
    status='INDEPENDENT_FIXED_GRAPH_ALL_ROOT_INTEGER_MATRIX_V1_PASS',
    producer='/root/checkpoint_audit', kind='empirical/engineering result',
    statement='For the fixed 99-vertex adjacency SHA256 928fb10c447a60cf3cc4edc89d95dfa35971ca60c76af5a37ef4685fadcb3131, every vertex has degree 14 and every adjacent pair has exactly one common neighbor. All 99 labelled root residuals R(r)=sum over nonneighbors v of (CN(r,v)-2)^2 are strictly positive. The minimum is 10 uniquely at vertex 11, and their sum is 10688, twice the unordered nonedge residual energy 5344. The full SRG99 integer identity fails at 5404 ordered entries. Relabelling this exact graph cannot supply a zero-residual root.',
    scope='Complete all-99-root nonedge residual profile of one exact non-SRG graph, including all ordered common-neighbor counts and histograms. No plateau closure, neighboring-graph exclusion, global minimum, support uniqueness or target resolution is asserted.',
    recorded_validation=dict(complete_root_profiles=99, ordered_common_neighbor_entries=9801,
        unordered_nonedge_entries=4158, integer_identity_entries=9801, identity_mismatches=5404,
        minimum_root_residual=10, minimum_root_vertices=[11], root_zero_vertices=[],
        sum_root_residuals=10688, unordered_mu_energy=5344))

# These are the full literal metadata values from the prior exact audit output,
# not a new rank or graph calculation. Full byte hashes bind the remaining data.
RANK_AUDIT = dict(rank=98, kernel_dimension=1, transform_entries_checked=22869,
    both_row_inverse_entries_checked=19602, both_minor_inverse_entries_checked=19208,
    scalar=dict(integer_identity_entries=9801, identity_mismatches=5500,
        nonedge_cn_histogram={'0':370, '1':1064, '2':1408, '3':897, '4':357, '5':55, '6':7}),
    constant_only_kernel=True, actual_inverse_corruption_rejected=True,
    minor_row_labels=list(range(98)),
    minor_column_labels=list(range(90)) + [93,104,107,115,132,140,141,143])
RANK_REPORT_HEADLINES = dict(rank=98, kernel_dimension=1, transform_entries_checked=22869,
    both_row_inverse_entries_checked=19602, both_minor_inverse_entries_checked=19208,
    constant_only_kernel=True, incidence_only_extra_kernel_refuted=True,
    producer_outputs_checked=True, target_exclusions=0)
RANK_CENSUS_HEADLINES = dict(n=99, degree=14, triangle_count=231, point_triangle_degree=7,
    all_adjacent_pairs_lambda1=True, nonedge_mu2_wrong_unordered_pairs=2750,
    exact_mu_energy=5476, full_srg99_identity_passed=False, target_resolution='NONE')
PROFILE_AUDIT_HEADLINES = dict(schema='EXACT_ALL_VERTEX_NONEDGE_RESIDUAL_PROFILE_V1', n=99, degree=14,
    sum_root_residuals=10688, unordered_mu_energy=5344, minimum_root_residual=10,
    minimum_root_vertices=[11], root_zero_vertices=[], residual_population=[
        [10,1],[78,1],[84,2],[88,2],[92,4],[94,3],[96,3],[98,6],[100,6],
        [102,9],[104,4],[106,6],[108,9],[110,7],[114,7],[116,5],[118,4],
        [120,6],[122,2],[126,1],[128,3],[132,2],[136,2],[138,2],[140,1],[142,1]])
PROFILE_ROOT_RESIDUALS = [104,118,110,120,108,120,128,102,96,138,104,10,110,78,120,
    118,138,132,102,92,118,84,108,100,96,116,108,108,122,102,110,120,114,120,92,
    94,114,96,110,88,128,108,108,94,98,98,120,98,102,92,140,100,98,84,106,100,
    136,142,102,106,106,108,100,118,98,132,98,114,116,94,114,122,102,128,106,
    114,108,100,92,104,116,108,106,136,102,114,116,100,110,110,106,126,88,102,
    104,114,116,102,110]


def need(ok, stage):
    if not ok:
        raise ValueError(stage)


def same(a, b):
    return json.dumps(a, sort_keys=True, allow_nan=False) == json.dumps(b, sort_keys=True, allow_nan=False)


def loads(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, 'JSON_DUPLICATE_KEY')
            result[key] = value
        return result
    try:
        return json.loads(raw, object_pairs_hook=pairs,
            parse_constant=lambda value: (_ for _ in ()).throw(ValueError('JSON_NONFINITE')))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise ValueError('JSON_SYNTAX') from error


def headlines(value, expected, stage):
    need(type(value) is dict and all(key in value for key in expected), stage)
    need(same({key: value[key] for key in expected}, expected), stage)


def validate_rank_metadata(report, audit, census, calibration):
    headlines(report, RANK_REPORT_HEADLINES, 'EXACT_RANK_HEADLINES')
    need(same(audit, RANK_AUDIT), 'EXACT_RANK_RAW_AUDIT')
    headlines(census, RANK_CENSUS_HEADLINES, 'EXACT_RANK_GRAPH_CENSUS')
    need(type(census.get('nonedge_mu2_wrong_pairs')) is list
         and len(census['nonedge_mu2_wrong_pairs']) == 2750, 'EXACT_RANK_CENSUS_POPULATION')
    headlines(calibration, dict(status='INDEPENDENT_INCIDENCE_GF3_RANK_CHECKER_V1_CALIBRATION_PASS',
        hand_certificate_positives=5, known_valid_graph_controls=1,
        precise_certificate_negatives=15, precise_graph_negatives=4,
        precise_binding_negatives=2, synthetic_bound_output_positive=1,
        producer_outputs_checked=False), 'EXACT_RANK_CALIBRATION')
    need(type(calibration.get('controls')) is list and len(calibration['controls']) == 21
         and all(type(row) is dict and row.get('outcome') == 'REJECTED'
                 and type(row.get('label')) is str and type(row.get('stage')) is str
                 for row in calibration['controls']), 'EXACT_RANK_CALIBRATION_RECORDS')


def validate_profile_metadata(report, profile, mismatches):
    headlines(report, PROFILE['recorded_validation'], 'EXACT_PROFILE_HEADLINES')
    need(type(profile) is dict and set(profile) == set(PROFILE_AUDIT_HEADLINES) | {'rows'},
         'EXACT_PROFILE_RAW_SCHEMA')
    headlines(profile, PROFILE_AUDIT_HEADLINES, 'EXACT_PROFILE_RAW_HEADLINES')
    rows = profile['rows']
    need(type(rows) is list and len(rows) == 99, 'EXACT_PROFILE_RAW_ROWS')
    for root, row in enumerate(rows):
        need(type(row) is dict and set(row) == {'root','nonedge_residual',
            'adjacent_cn_histogram','nonadjacent_cn_histogram','nonadjacent_cn_records',
            'local_zero_details'}, 'EXACT_PROFILE_RAW_ROW_SCHEMA')
        need(same(row['root'], root) and same(row['nonedge_residual'], PROFILE_ROOT_RESIDUALS[root])
             and same(row['adjacent_cn_histogram'], [[1,14]])
             and row['local_zero_details'] is None, 'EXACT_PROFILE_RAW_ROOT_VALUES')
        records = row['nonadjacent_cn_records']
        need(type(records) is list and len(records) == 84
             and all(type(pair) is list and len(pair) == 2
                     and all(type(x) is int for x in pair)
                     and 0 <= pair[0] < 99 and pair[0] != root and 0 <= pair[1] <= 99
                     for pair in records), 'EXACT_PROFILE_RAW_NONEDGE_TYPES')
        need([pair[0] for pair in records] == sorted(set(pair[0] for pair in records)),
             'EXACT_PROFILE_RAW_NONEDGE_ORDER')
        histogram = row['nonadjacent_cn_histogram']
        need(type(histogram) is list and histogram
             and all(type(pair) is list and len(pair) == 2
                     and all(type(x) is int for x in pair)
                     and 0 <= pair[0] <= 99 and pair[1] > 0 for pair in histogram),
             'EXACT_PROFILE_RAW_HISTOGRAM_TYPES')
    need(type(mismatches) is list and len(mismatches) == 5404
         and all(type(row) is list and len(row) == 4 and all(type(x) is int for x in row)
                 and 0 <= row[0] < 99 and 0 <= row[1] < 99 and 0 <= row[2] <= 99
                 and row[2] != row[3] for row in mismatches), 'EXACT_PROFILE_IDENTITY_RECORDS')
    need(same(mismatches[0], [0,2,0,2]) and same(mismatches[-1], [98,97,3,2]),
         'EXACT_PROFILE_IDENTITY_BOUNDARIES')


def validate_output_review(review, own, own_sha, spec, spec_sha):
    expected = []
    for config in [RANK, PROFILE]:
        outputs = {config['raw_audit']: config['raw_audit_sha256']}
        if config is PROFILE:
            outputs[config['identity_audit']] = config['identity_audit_sha256']
        expected.append(dict(id=config['id'], revision=1, report=config['report'],
            report_sha256=config['report_sha256'], raw_graph=config['raw'],
            raw_graph_sha256=config['raw_sha256'], outputs_sha256=outputs))
    need(type(review) is dict and set(review) == {'schema','status','reviewer','method',
        'timestamp','mathematical_replays','target_resolution','writer_inputs_sha256',
        'records','scope'}, 'ROOT_OUTPUT_REVIEW_SCHEMA')
    headlines(review, dict(schema='ROOT_PRIOR_FIXED_GRAPH_DIAGNOSTIC_OUTPUT_IDENTITY_REVIEW_V1',
        status='ROOT_EXACT_PRIOR_FIXED_GRAPH_OUTPUT_IDENTITY_REVIEW_V1_PASS',
        reviewer='/root', method='written_identity_review', mathematical_replays=0,
        target_resolution='NONE'), 'ROOT_OUTPUT_REVIEW_ROLE')
    need(same(review['writer_inputs_sha256'], {own:own_sha, spec:spec_sha}),
         'ROOT_OUTPUT_REVIEW_WRITER_PINS')
    need(same(review['records'], expected), 'ROOT_OUTPUT_REVIEW_LITERAL_RECORDS')
    need(review['scope'] == 'Exact prior checker-output identities for these two fixed-graph claims only; original summaries and mathematical checks are unchanged.',
         'ROOT_OUTPUT_REVIEW_SCOPE')
    need(type(review['timestamp']) is str, 'ROOT_OUTPUT_REVIEW_TIMESTAMP')
    try:
        stamp = datetime.fromisoformat(review['timestamp'])
    except ValueError as error:
        raise ValueError('ROOT_OUTPUT_REVIEW_TIMESTAMP') from error
    need(stamp.tzinfo is not None, 'ROOT_OUTPUT_REVIEW_TIMESTAMP')


def save(path, obj):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(obj, stream, indent=2, allow_nan=False); stream.write('\n')


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--seconds', type=float, required=True)
    ap.add_argument('--out', type=Path, required=True); ap.add_argument('--source-sha256', required=True)
    ap.add_argument('--protocol-sha256', required=True)
    ap.add_argument('--raw-output-review', type=Path, required=True)
    ap.add_argument('--raw-output-review-sha256', required=True); a = ap.parse_args()
    d = CommandDeadline(a.seconds, allocation_reason='Metadata-only authentication and literal projection of two prior independent fixed-graph diagnostics;10second preservation reserve; no mathematical replay')
    out = a.out.resolve(); need(out.is_relative_to(ROOT) and not out.exists(), 'FRESH_OUTPUT'); out.mkdir(parents=True)
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    protected = {n: digest(ROOT / n) for n in ['CLAIMS.yaml', '.git/index']}
    all_pins = {}
    def pin(name, identity=None):
        need(d.status()['remaining_seconds'] > 10, 'SAVE_RESERVE')
        p = PurePosixPath(name)
        need(type(name) is str and not p.is_absolute() and '..' not in p.parts and ':' not in name
             and not any(c in name for c in '\\\n\r\0') and name not in protected, 'IMMUTABLE_PATH')
        path = (ROOT / name).resolve(); need(path.is_relative_to(ROOT) and path.is_file(), 'EXISTING_FILE')
        h = digest(path); need(identity is None or h == identity, 'EXACT_HASH:' + name)
        need(name not in all_pins or all_pins[name] == h, 'PIN_CONFLICT'); all_pins[name] = h
        return h
    try:
        own = Path(__file__).relative_to(ROOT).as_posix()
        spec = Path(__file__).with_name(Path(__file__).stem + '_spec.md').relative_to(ROOT).as_posix()
        pin(own, a.source_sha256); pin(spec, a.protocol_sha256)
        for name in ['pyproject.toml', 'uv.lock', 'acceleration/run_compute_command.py', 'acceleration/command_deadline.py']:
            pin(name)
        review_name = a.raw_output_review.resolve().relative_to(ROOT).as_posix()
        pin(review_name, a.raw_output_review_sha256)
        output_review = loads((ROOT / review_name).read_bytes())
        validate_output_review(output_review, own, a.source_sha256, spec, a.protocol_sha256)
        writer_pins = dict(all_pins)
        summaries = []
        for config in [RANK, PROFILE]:
            for path, expected in [(config['report'], config['report_sha256']),
                (config['terminal'], config['terminal_sha256']), (config['raw'], config['raw_sha256'])]:
                pin(path, expected)
            report = loads((ROOT / config['report']).read_bytes())
            terminal = loads((ROOT / config['terminal']).read_bytes())
            need(report['status'] == config['status'] and report['producer'] == config['producer']
                 and report['verifier'] == '/root' and report['method'] == 'independent_artifact_check'
                 and report['target_resolution'] == 'NONE', 'EXACT_INDEPENDENT_REPORT')
            need(same(terminal['command_exit_code'], 0) and terminal['cleanup']['reaped'] is True
                 and terminal['cleanup']['job_active_zero_observed'] is True
                 and same(terminal['cleanup']['cleanup_errors'], []), 'CONTAINED_TERMINAL')
            need(type(report.get('inputs_sha256')) is dict, 'CHECKING_INPUT_MAP')
            closure = dict(report['inputs_sha256'])
            for name, identity in closure.items():
                pin(name, identity)
            pin(config['raw_audit'], config['raw_audit_sha256'])
            need((ROOT / config['raw_audit']).stat().st_size == config['raw_audit_bytes'],
                 'EXACT_RAW_AUDIT_BYTES')
            raw_audit = loads((ROOT / config['raw_audit']).read_bytes())
            extra_direct = []
            if config is RANK:
                for field in ['graph_census', 'calibration']:
                    need(closure.get(config[field]) == config[field + '_sha256'],
                         'PRIOR_INPUT_IDENTITY:' + field)
                    pin(config[field], config[field + '_sha256'])
                    extra_direct.append(config[field])
                census = loads((ROOT / config['graph_census']).read_bytes())
                calibration = loads((ROOT / config['calibration']).read_bytes())
                validate_rank_metadata(report, raw_audit, census, calibration)
                recorded_controls = dict(calibration_path=config['calibration'],
                    calibration_sha256=config['calibration_sha256'],
                    hand_certificate_positives=calibration['hand_certificate_positives'],
                    known_valid_graph_controls=calibration['known_valid_graph_controls'],
                    synthetic_bound_output_positive=calibration['synthetic_bound_output_positive'],
                    precise_certificate_negatives=calibration['precise_certificate_negatives'],
                    precise_graph_negatives=calibration['precise_graph_negatives'],
                    precise_binding_negatives=calibration['precise_binding_negatives'],
                    negative_records=calibration['controls'],
                    actual_inverse_corruption_rejected=raw_audit['actual_inverse_corruption_rejected'])
                literal_metadata = dict(report_headlines=RANK_REPORT_HEADLINES,
                    complete_raw_rank_audit=RANK_AUDIT,
                    producer_graph_census_headlines=RANK_CENSUS_HEADLINES)
                output_pins = {config['raw_audit']: config['raw_audit_sha256']}
            else:
                pin(config['identity_audit'], config['identity_audit_sha256'])
                need((ROOT / config['identity_audit']).stat().st_size == config['identity_audit_bytes'],
                     'EXACT_IDENTITY_AUDIT_BYTES')
                mismatches = loads((ROOT / config['identity_audit']).read_bytes())
                validate_profile_metadata(report, raw_audit, mismatches)
                extra_direct.append(config['identity_audit'])
                recorded_controls = report['controls']
                literal_metadata = dict(report_headlines=config['recorded_validation'],
                    raw_profile_headlines=PROFILE_AUDIT_HEADLINES,
                    all99_literal_root_residuals=PROFILE_ROOT_RESIDUALS,
                    ordered_identity_record_count=5404, first_identity_record=[0,2,0,2],
                    last_identity_record=[98,97,3,2])
                output_pins = {config['raw_audit']: config['raw_audit_sha256'],
                               config['identity_audit']: config['identity_audit_sha256']}
            key = 'rank98' if config is RANK else 'all99roots'
            directory = out / key; directory.mkdir()
            # Preserve the complete checking closure once, rather than expanding
            # every transitive historical input into duplicate ledger records.
            save(directory / 'authenticated_checking_closure.json', dict(inputs_sha256=closure,
                direct_report=config['report'], direct_report_sha256=config['report_sha256'],
                availability='LOCAL_ONLY', limitation='Immutable publication of every new transitive artifact requires a separate complete payload/availability audit.'))
            closure_name = (directory / 'authenticated_checking_closure.json').relative_to(ROOT).as_posix()
            pin(closure_name)
            provenance_name = (directory / 'prior_raw_output_identity_provenance.json').relative_to(ROOT).as_posix()
            save(ROOT / provenance_name, dict(schema='LITERAL_PRIOR_CHECKER_OUTPUT_IDENTITY_V1',
                claim_id=config['id'], claim_revision=1, prior_report=config['report'],
                prior_report_sha256=config['report_sha256'], prior_report_verifier='/root',
                prior_report_timestamp=report['timestamp'], prior_terminal=config['terminal'],
                prior_terminal_sha256=config['terminal_sha256'], exact_raw_graph=config['raw'],
                exact_raw_graph_sha256=config['raw_sha256'], outputs_sha256=output_pins,
                original_summary_self_output_hashes_present=False,
                raw_output_identity_in_prior_report=None,
                raw_output_identity_in_prior_report_null_reason='The unchanged primary report inputs_sha256 records checking inputs, not these newly emitted checker-output bytes. This V2 literal identity binding and separate ROOT written review do not assert a retrospective output hash in the old report.',
                identity_binding_role='Exact prior-output SHA256 literals newly frozen in V2; old summaries intentionally do not bind their own output files. No old report or artifact is rewritten.',
                required_root_review='A separately pinned ROOT written output-identity review binds exactly these two claims, their unchanged original reports, all three raw checker-output identities, and this V2 writer/spec. It is an identity/metadata review, not a new mathematical replay.',
                root_review_evidence=dict(path=review_name, sha256=all_pins[review_name],
                    timestamp=output_review['timestamp'], reviewer=output_review['reviewer'],
                    method=output_review['method']),
                metadata_writer_author='/root/native_driver', metadata_only=True,
                mathematical_replays=0, availability='LOCAL_ONLY'))
            pin(provenance_name)
            direct = dict(writer_pins)
            for name in [config['report'], config['terminal'], config['raw'], config['raw_audit'],
                         closure_name, provenance_name, *extra_direct]:
                direct[name] = all_pins[name]
            now = datetime.now(timezone.utc).isoformat()
            binding = dict(id=config['id'], revision=1, claim_revision=1, statement=config['statement'],
                kind=config['kind'], basis=['COMPUTED'], status='VERIFIED', review_state='CLEAR',
                producer=config['producer'], verifier='/root', method='independent_artifact_check',
                scope=dict(description=config['scope'], unrestricted_target=False, target_resolution='NONE'),
                assumptions=['This claim concerns exactly the hashed complete raw graph and independently checked artifacts; it does not assume that graph is an SRG99 solution.',
                             'The locked integer/modular checking implementation and complete raw input bindings remain as disclosed by the independent report.'],
                dependencies=[], report=config['report'], report_sha256=config['report_sha256'],
                verification_timestamp=report['timestamp'], recorded_validation=config['recorded_validation'],
                authenticated_prior_literal_metadata=literal_metadata,
                controls=recorded_controls,
                inputs_sha256=direct, complete_transitive_checking_closure=dict(path=closure_name,
                    sha256=all_pins[closure_name], immutable_members=len(closure), role='Full prior independent checking inputs; authenticated here without mathematical replay.'),
                literal_prior_raw_output_identity=dict(path=provenance_name,
                    sha256=all_pins[provenance_name], outputs_sha256=output_pins,
                    scope='Exact new literal output-byte bindings; prior independent mathematics and timestamp remain in unchanged primary report.'),
                shared_components=report['shared_components'], command=report['command'], cwd=report['cwd'],
                tool_versions=dict(python=report['python'], numpy=report.get('numpy'),
                    numpy_null_reason=None if 'numpy' in report else 'GF3 checker uses Python scalar integer operations without numpy.'),
                source_commit=report.get('source_context_commit'),
                source_commit_null_reason=None if report.get('source_context_commit') else 'Independent report records exact working inputs but has no source-context-commit field; current metadata writer context is separately recorded.',
                source_commit_role='Checking context only; original producer command/source commit remain in the exact checking closure.',
                limitations=[config['scope'], 'All claim evidence is one finite exact artifact check; no unrestricted graph-space denominator or scientific search coverage.',
                    'Complete transitive hashes are retained in a separately bound closure record and the independent report; every new raw witness remains LOCAL_ONLY pending immutable publication.',
                    'Metadata writer authenticates prior checks and records their literal scope; it neither discovers nor mathematically approves the graph.',
                    'A fresh narrowly frozen registrar adapter and independently checked ledger transition are required before this claim enters current verified totals.',
                    'No peer review, novelty or external acceptance is asserted.'],
                availability='LOCAL_ONLY', retrieval='Saved raw workspace files; exact immutable publication pending.',
                premise_state='This is a fixed non-SRG artifact; unrestricted target existence remains UNKNOWN.',
                target_resolution='NONE', novelty=None, novelty_null_reason='No novelty audit.',
                external_review=None, external_review_null_reason='Internal independent artifact checking only.',
                created_at=now, updated_at=now, metadata_only=True, mathematical_replays=0,
                metadata_writer_author='/root/native_driver', metadata_writer_independent_approval=False,
                writer_command=[sys.executable, *sys.argv], writer_source_sha256=digest(Path(__file__)))
            save(directory / 'claim_binding_schema2.json', binding)
            summaries.append(dict(id=config['id'], binding=(directory / 'claim_binding_schema2.json').relative_to(ROOT).as_posix(),
                sha256=digest(directory / 'claim_binding_schema2.json'), transitive_members=len(closure), direct_members=len(direct)))
        need(protected == {n: digest(ROOT / n) for n in protected}, 'PROTECTED_STATE')
        save(out / 'summary.json', dict(status='METADATA_ONLY_TWO_FIXED_GRAPH_DIAGNOSTIC_BINDINGS_SAVED',
            timestamp=datetime.now(timezone.utc).isoformat(), bindings=summaries, inputs_sha256=all_pins,
            source_context_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            command=[sys.executable, *sys.argv], cwd=str(ROOT), python=platform.python_version(),
            historical_protected_execution_state=protected, mathematical_replays=0, ledger_mutations=0,
            index_mutations=0, deadline=d.status(), target_resolution='NONE'))
        print(json.dumps(summaries))
    except BaseException as error:
        save(out / 'failure.json', dict(error=repr(error), inputs_sha256=all_pins, outputs_preserved=True,
            mathematical_replays=0, ledger_mutations=0, index_mutations=0, deadline=d.status()))
        raise


if __name__ == '__main__':
    main()
