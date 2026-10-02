"""Draft narrow schema2 metadata from ROOT's complete fixed-graph census audit."""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
REPORT = 'acceleration/results/20261003_independent_review/two_line_full01/summary.json'
REPORT_SHA = '1d3cecc2fd8d3e689966a334af59a9af7d0a2e8c66b356b98484aef3ed79e589'
CAL = 'acceleration/results/20261003_independent_review/two_line_records_calibration01/summary.json'
CAL_SHA = 'ab51f23bbbd09e6d0b94ce861b391bb349cd583bc62f69439e2da1afb66af3b6'
MANIFEST = 'acceleration/results/20261003_weight60_two_line_census01/manifest.json'
MANIFEST_SHA = '70f4ec893d5ba443effdd29cd6e3d472d736e590af56691b751e822bbae49ffa'
PRODUCER_RECEIPT = 'acceleration/results/20261003_weight60_two_line_census01/run_receipt.json'
RECEIPT_SHA = '016f9eec71a409ccb17d0d849323d204efad3e1feae4a1f5da685201e768fc30'


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seconds', required=True, type=float)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='Metadata only: bind ROOT exact fixed239085 census/report/calibration and raw source/artifact closure; no mathematical replay or own approval')
    out = args.out.resolve()
    need(out.is_relative_to(ROOT) and not out.exists(), 'Fresh workspace metadata output')
    out.mkdir(parents=True)
    pins = {}

    def pin(name, wanted=None):
        need(not deadline.status()['stop_required'] and deadline.status()['remaining_seconds'] > 20, 'Not completed within allocated metadata budget')
        path = (ROOT/name).resolve()
        need(not Path(name).is_absolute() and path.is_relative_to(ROOT) and path.is_file(), 'Exact bounded local input '+name)
        identity = sha(path)
        need(wanted is None or identity == wanted, 'Exact pinned identity '+name)
        need(name not in pins or pins[name] == identity, 'Consistent repeated pin '+name)
        pins[name] = identity
        return json.loads(path.read_bytes()) if path.suffix == '.json' else None

    report = pin(REPORT, REPORT_SHA)
    calibration = pin(CAL, CAL_SHA)
    manifest = pin(MANIFEST, MANIFEST_SHA)
    receipt = pin(PRODUCER_RECEIPT, RECEIPT_SHA)
    need(report['status'] == 'INDEPENDENT_TWO_LINE_COMPLETE_FIXED_GRAPH_CENSUS_V2_PASS'
         and report['verifier'] == '/root' and report['producer'] == '/root/native_driver'
         and report['method'] == 'independent_artifact_check', 'Exact separate ROOT complete checking outcome')
    need(report['complete_proposals_checked'] == report['frozen_labelled_proposals'] == 239085
         and report['complete_universe'] is True and report['absence_of_descent_asserted'] is True
         and report['target_resolution'] == 'NONE', 'Exact finite absence statement only')
    expected = dict(counts=dict(invalid_linearity=87996, invalid_selection=10395,
        valid_lambda_changed=140507, valid_lambda_preserving_mu_equal=2,
        valid_lambda_preserving_mu_up=185), unique_valid_neighbor_graphs=136536,
        best_mu=3480, best_proposal_ids=[68908,68912])
    need(report['aggregate'] == manifest['aggregate'] == expected, 'All exact complete classifications/minima')
    need(manifest['population'] == manifest['completed_proposals'] == 239085
         and len(manifest['parts']) == len(manifest['checkpoints']) == 48
         and manifest['baseline'] == dict(lambda_energy=0,mu_energy=3480,root=11,root_residual=52), 'Frozen complete universe/initial domain')
    need(report['independently_checked_chosen_neighbor'] == dict(proposal_id=68908,lambda_energy=0,
        mu_energy=3480,root_residual=52,ordered_srg_identity_mismatches=4754), 'Exact saved chosen-object scope')
    need(calibration['status'] == 'INDEPENDENT_TWO_LINE_RECORDS_V2_PREOUTPUT_CALIBRATION_PASS'
         and calibration['complete_unique_tiny_records'] == 270
         and calibration['complete_records_including_split_replay'] == 540
         and len(calibration['strict_record_corruptions']) == 15
         and calibration['pre_full_scientific_output'] is True, 'Exact pre-output calibration scope')
    need(receipt['source_commit'] == 'e1691ed8cdab8e21b9038497c6ba109de7f781c8'
         and receipt['manifest_sha256'] == MANIFEST_SHA, 'Exact source/receipt identity')
    for record in [report, calibration]:
        for name, identity in record['inputs_sha256'].items():
            pin(name, identity)
    for name, identity in manifest['identity']['inputs_sha256'].items():
        pin(name, identity)
    for name, identity in manifest['identity']['software'].items():
        pin(name, identity)
    for part in manifest['parts']:
        pin(part['path'], part['gzip_sha256'])
    for checkpoint in manifest['checkpoints']:
        pin(checkpoint['path'], checkpoint['sha256'])
    for path in sorted((ROOT/'acceleration/results/20261003_weight60_two_line_census01').iterdir()):
        if path.is_file():
            pin(path.relative_to(ROOT).as_posix())
    for folder in ['acceleration/results/20261003_weight60_two_line_census_supervision01',
        'acceleration/results/20261003_two_line_records_calibration_supervision01',
        'acceleration/results/20261003_two_line_full_supervision01']:
        need((ROOT/folder).is_dir(), 'Exact actual supervisor folder '+folder)
        for path in sorted((ROOT/folder).iterdir()):
            if path.is_file():
                pin(path.relative_to(ROOT).as_posix())
    own = Path(__file__).relative_to(ROOT).as_posix()
    pin(own)
    pin(own.replace('.py','_spec.md'))
    now = datetime.now(timezone.utc).isoformat()
    statement = ('For the single labelled99-point linear hypergraph encoded by current triples in state '
        'SHA256c15b421468af173b6c2ee11e9bcb31d5abca586fcb47a7c7ee312f527b31979b, with adjacency '
        'SHA2569d5b88ba2a2eb13d39d2a5edea1c25af9a9105c143c4297fe37e84f666a37a2d, '
        'point degree7 and231 labelled triples, no admissible exclusive-point swap between two distinct triples '
        'preserving linearity has E_lambda=0 and E_mu<3480. This quantifies exactly all239085 proposals '
        '(i<j in lexicographic triple order, ix/jy in0..2, ID9*pair_index+3*ix+jy), including shared-point '
        'triple pairs; E_lambda=sum_{i<j,Aij=1}(CN(i,j)-1)^2 and E_mu=sum_{i<j,Aij=0}(CN(i,j)-2)^2 over '
        'the resulting14-regular point graph. Exactly two lambda-preserving proposals have E_mu=3480 '
        '(IDs68908,68912), and they have identical changed-edge sets, producing one identical labelled point graph.')
    binding = dict(binding_schema_version=2,id='C-HYPERGRAPH-WEIGHT60-WARM01-FIXED-V2-TWO-LINE-CENSUS',
        revision=1,claim_revision=1,kind='exclusion',basis=['COMPUTED'],status='VERIFIED',review_state='CLEAR',statement=statement,
        scope=dict(description='Complete labelled one-move neighborhood of one exact saved hypergraph under the stated V2 exclusive-point trade; no other starts/moves/global graph minimum/whole plateau/exhaustive target coverage.',
            unrestricted_target=False,target_resolution='NONE'),
        assumptions=['Use exactly the hashed ordered current triples and labelled point graph; retain original labels0..98.',
            'Admissible is the V2 distinct-triple exclusive selected-point swap, allowing one shared point while preserving complete linearity and point degree.',
            'The predicate E_mu<3480 is strict and additionally requires exact E_lambda=0; lambda-changing moves are not excluded from the original complete enumeration.',
            'VERIFIED cites the separately authored complete ROOT audit; this producer metadata draft does not approve itself.'],
        dependencies=[],dependency_reason='ROOT independently rebuilds the exact literal input graph and checks every proposal/delta/raw record. No annealer history, nontrivial automorphism, prior theorem or target encoding is a premise.',
        created_at=now,updated_at=now,producer='/root/native_driver',verifier='/root',method='independent_artifact_check',
        verification_timestamp=report['timestamp'],report=REPORT,report_sha256=REPORT_SHA,
        command=report['command'],cwd=report['cwd'],python=report['python'],numpy=report['numpy'],
        source_commit=receipt['source_commit'],producer_source_commit=receipt['source_commit'],
        source_commit_scope='Recorded producer BASEe169; new producer/checker/control/output bytes are separately hash-bound working closure and are not represented as Git members of BASE.',
        verifier_source_commit=None,verifier_source_commit_reason='The actual ROOT report has no verifier Git-commit field; exact source/spec hashes/command/runtime are preserved rather than inferred.',
        inputs_sha256=pins,
        independent_statement_binding=dict(report_hash_bound=True,complete_population_fields_bound=True,
            complete_raw_parts_bound=True,calibration_bound=True,exact_counts_ties_bound=True,self_approval=False,
            requires_ROOT_review_of_this_editorial_binding=True),
        pre_output_calibration=dict(path=CAL,sha256=CAL_SHA,known_fixtures=['rook9','prism9'],
            complete_unique_records=270,complete_split_stream_records=540,
            complete_fullmatrix_and_scalar_valid_comparisons=calibration['complete_new_fullmatrix_and_scalar_comparisons'],
            known_overlap_checked=calibration['known_overlap_checked'],
            strict_saved_stream_and_metadata_corruptions=calibration['strict_record_corruptions'],
            controls_preceded_full_scientific_output=True),
        computational_evidence=dict(producer_command=receipt['command'],producer_cwd=receipt['cwd'],
            python=receipt['python'],random_seed=None,random_seed_reason='Deterministic full enumeration; no RNG.',
            numerical_settings='Exact Python integer producer; independently bounded NumPy int64 matrix/delta arithmetic and scalar controls, no floating-point certificate.',
            graph_points=99,labelled_triples=231,labelled_proposals=239085,completed_labelled_proposals=239085,
            classifications=expected['counts'],unique_valid_labelled_point_graphs=136536,raw_gzip_parts=48,checkpoint_count=48,
            raw_jsonl_bytes=sum(part['raw_bytes'] for part in manifest['parts']),gzip_bytes=sum(part['gzip_bytes'] for part in manifest['parts']),
            coverage_argument='Every i<j pair and all9 selected-position pairs have contiguous IDs0..239084; all48parts/checkpoints/records independently checked. This is the frozen proposal universe only.',
            pruning='No unrecorded pruning or random sampling; each invalid proposal retains exact exclusion reason/conflict witness.',
            overlap_treatment='Labelled proposal counts overlap as point graphs; unique graph count uses exact net-toggle sets against fixed input, not isomorphism.',
            outcome='No strict lambda-preserving mu descent within this one fixed V2 neighborhood; chosen neutral raw neighbor is non-SRG with4754ordered identity mismatches.',
            full_global_search_coverage='UNKNOWN; no validated denominator.'),
        shared_components=report['shared_components']+['Producer and checker share raw graph/fixture definitions, Python JSON/gzip, and deadline/containment primitives; these are disclosed trusted components.',
            'ROOT checker imports its own calibrated dense V1 helper; no producer bitset/common-cache/scorer/enum code is imported.'],
        artifact_availability='LOCAL_ONLY',retrieval='Exact repository-relative files/hashes in closure.json; public availability requires separate immutable publication and recovery audit.',
        limitations=report['limitations']+['One-move local absence does not imply global minimality, closure of a plateau, connectedness/ergodicity or target nonexistence.',
            'Root11minimum diagnostics and target validation of other graphs are not broader conclusions of this exclusion statement.',
            'No complete annealer trajectory, performance guarantee or external peer review.',
            'Binding/registrar/schema checks are metadata, not new mathematical verification.'],
        target_resolution=False,ledger_edited=False,external_review='Internal independent ROOT audit only; no external mathematical review claimed.')
    save(out/'claim_binding_schema2_draft.json',binding)
    save(out/'closure.json',dict(schema='FIXED_TWO_LINE_CENSUS_BINDING_DIRECT_CLOSURE_V1',
        source_commit=receipt['source_commit'],records=[dict(path=name,sha256=identity,bytes=(ROOT/name).stat().st_size,availability='LOCAL_ONLY')
            for name,identity in sorted(pins.items())],claim_binding=dict(path=(out/'claim_binding_schema2_draft.json').relative_to(ROOT).as_posix(),
            sha256=sha(out/'claim_binding_schema2_draft.json')),mathematical_replay=False,ledger_edited=False))
    print(json.dumps(dict(binding_sha256=sha(out/'claim_binding_schema2_draft.json'),closure_sha256=sha(out/'closure.json'),records=len(pins),ledger_edited=False)))


if __name__ == '__main__':
    main()
