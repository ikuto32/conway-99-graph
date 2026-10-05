"""Metadata-only schema2 binding to ROOT's already completed dense reset audit."""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
REPORT = 'acceleration/results/20261003_independent_review/weight60_reset_full01/summary.json'
REPORT_SHA = '23917a9077bbce46c0c1222403852cbf40925cf2749f333b0fd74e04bac45d21'
PRODUCER = 'acceleration/results/20261003_weight60_graph_reset01/summary.json'
PRODUCER_SHA = '983af04f99de4242d53ed6ca306770adfac8223c04d87c93777e3272f2b2b7b8'
CAL = 'acceleration/results/20261003_independent_review/weight60_reset_calibration01/summary.json'
CAL_SHA = '5e93291da1bf0b3acecc4549a8a631e682c2a6e835e695a42a0a40cd19a17d23'
CHECKER = 'acceleration/audit_20261003_weight60_reset_state_v1.py'
CHECKER_SHA = '078524dd42270f10ee7ea42616101dc9d2e1e09bdfabc2ff654a2ec78655f7c8'


def need(ok, why):
    if not ok:
        raise ValueError(why)


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, indent=2); stream.write('\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, required=True); ap.add_argument('--seconds', type=float, required=True)
    args = ap.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='Metadata-only binding of one alreadyROOT independently checked graph-only reset, no mathematical replay')
    out = args.out.resolve(); need(out.is_relative_to(ROOT), 'workspace output'); out.mkdir(parents=True, exist_ok=False)
    pins = {}
    def pin(name, identity=None):
        need(not deadline.status()['stop_required'] and deadline.status()['remaining_seconds'] > 20,
             'not completed within allocated metadata budget')
        path = (ROOT / name).resolve(); need(path.is_relative_to(ROOT) and path.is_file(), 'local exact artifact')
        digest = sha(path); need(identity is None or digest == identity, 'artifact identity: ' + name)
        need(name not in pins or pins[name] == digest, 'consistent repeated identity'); pins[name] = digest
        return json.loads(path.read_text(encoding='utf8')) if path.suffix == '.json' else None
    report = pin(REPORT, REPORT_SHA); producer = pin(PRODUCER, PRODUCER_SHA); cal = pin(CAL, CAL_SHA); pin(CHECKER, CHECKER_SHA)
    need(report['status'] == 'INDEPENDENT_WEIGHT60_GRAPH_ONLY_RESET_V1_PASS' and report['verifier'] == '/root'
         and report['producer'] == '/root/native_driver', 'exact ROOT verdict/roles')
    expected = dict(seed=99032061, mix_steps=0, schedule_steps=80000000, t_start=8.0, t_end=0.1,
                    forced=0, step=0, admissible=0, accepted=0, best_updates=0)
    need(report['parameters'] == expected and report['graphs_preserved'] == ['current', 'best', 'first_current', 'first_best'],
         'exact literal reset config/objects')
    need((report['lambda_energy'], report['mu_energy'], report['identity_mismatches'], report['complete_reset_scalar_entries'])
         == (0, 3608, 4934, 39204), 'literal graph components and complete checking')
    need(report['controls'] == cal['controls'] and cal['status'] == 'INDEPENDENT_WEIGHT60_GRAPH_ONLY_RESET_CALIBRATION_V1_PASS'
         and (cal['controls']['positive_controls'], cal['controls']['strict_negative_controls']) == (2, 15), 'pre-output independent calibration')
    for name, identity in report['inputs_sha256'].items():
        pin(name, identity)
    for name, identity in producer['inputs_sha256'].items():
        pin(name, identity)
    for name, descriptor in producer['artifacts'].items():
        pin(name, descriptor['sha256'])
    for name in ['acceleration/audit_20261003_weight60_reset_state_v1_spec.md',
                 'acceleration/prepare_20261003_weight60_graph_reset_v1.py',
                 'acceleration/prepare_20261003_weight60_graph_reset_v1_spec.md',
                 Path(__file__).relative_to(ROOT).as_posix(), 'acceleration/draft_20261003_weight60_reset_binding_v1_spec.md']:
        pin(name)
    for folder in ['acceleration/results/20261003_independent_review/weight60_reset_full_supervision01',
                   'acceleration/results/20261003_independent_review/weight60_reset_calibration_supervision01',
                   'acceleration/results/20261003_weight60_graph_reset_supervision01']:
        for leaf in ['manifest.json', 'summary.json', 'stdout.log', 'stderr.log', 'progress.jsonl']:
            pin(folder + '/' + leaf)
    now = datetime.now(timezone.utc).isoformat()
    statement = ('The exact V2 reset record SHA256f9cd59ab9d9bd3dcb89b6fab32784f17d3c744e047ebe23d212e2fd4f5bf6665 preserves, in exact original order, the labelled current triples of source record SHA2560dc37fdc2dd58fb78f55b88fd8e2ee7c43a83d32d1cc7897591151d5aca6a1bb in its current, best, first_current and first_best objects. It resets xoshiro256 RNG by seed99032061, step/admissible/accepted/best_updates to0, mixing to0 and T8 to0.1 over80000000 schedule steps, with first-lambda0 snapshot step0. All four serialized graph objects have lambda residual energy0, mu residual energy3608, F60=3608 and4934 ordered SRG99 identity mismatches, checked by complete literal integer adjacency products.')
    binding = dict(binding_schema_version=2, id='C-HYPERGRAPH-WEIGHT60-V2-GRAPH-ONLY-SEED61-RESET', revision=1,
        claim_revision=1, kind='empirical/engineering result', basis=['COMPUTED'], status='VERIFIED', review_state='CLEAR',
        statement=statement, scope=dict(description='One exact graph-only reset derivative and its four complete serialized objects/config/RNG. No old random-trajectory continuation, scientific outcome or graph search coverage.', unrestricted_target=False, target_resolution='NONE'),
        assumptions=['Use exactly the two pinned source/reset V2 records and native documented splitmix-to-xoshiro seed convention.',
                     'VERIFIED cites ROOT independent dense/raw-parser report; producer metadata author does not approve this transformation.'],
        dependencies=[], dependency_reason='Complete direct literal source/reset checking; no annealer history or earlier success premise is needed for this one-artifact statement.',
        created_at=now, updated_at=now, producer='/root/native_driver', verifier='/root', method='independent_artifact_check',
        verification_timestamp=report['timestamp'], report=REPORT, report_sha256=REPORT_SHA, command=report['command'],
        cwd=report['cwd'], python=report['python'], source_commit=producer['source_commit'], producer_source_commit=producer['source_commit'],
        verifier_source_commit=report['source_commit'],
        source_commit_scope='Published base43175e0a96ed4abbf6b03e16b67adff6f6f40b20; new adapter/checker/derivative/report source byte identities are separately pinned. No assertion new files belonged to this base.',
        inputs_sha256=pins, independent_statement_binding=dict(report_hash_bound=True, exact_parameters_bound=True, all_four_objects_bound=True, calibration_bound=True, self_approval=False, requires_ROOT_review_of_editorial_binding=True),
        pre_output_calibration=dict(path=CAL, sha256=CAL_SHA, positive_fixture='Known valid generic SRG(9,4,1,2) rook9 dense/serialized objects', positive_control_count=2, strict_negative_count=15, controls=cal['controls']),
        shared_components=report['shared_components'] + ['Both use Python integers/JSON and pinned deadline/containment; ROOT imports no producer serializer/scorer. Native seed specification and state format are shared explicitly.'],
        artifact_availability='LOCAL_ONLY', retrieval='Exact relative paths and hashes in closure.json; public availability requires separate immutable publication review.',
        limitations=report['limitations'] + ['New first-lambda0 snapshotstep0 is the reset input; no historical earliest selection claim.',
            'No scientific invocation has been launched by this binding and no integer SRG99 solution follows from lambda0/mu3608.',
            'Schema validation/registration is metadata, not another mathematical checking path.'],
        target_resolution=False, ledger_edited=False, external_review='Internal ROOT check; no external peer-review claim.')
    save(out / 'claim_binding_schema2_draft.json', binding)
    save(out / 'closure.json', dict(schema='WEIGHT60_RESET_DIRECT_BINDING_CLOSURE_V1',
        records=[dict(path=name, sha256=identity, bytes=(ROOT / name).stat().st_size, availability='LOCAL_ONLY') for name, identity in sorted(pins.items())],
        claim_binding=dict(path=(out / 'claim_binding_schema2_draft.json').relative_to(ROOT).as_posix(), sha256=sha(out / 'claim_binding_schema2_draft.json')),
        mathematical_replay=False, ledger_edited=False))
    print(json.dumps(dict(binding_sha256=sha(out / 'claim_binding_schema2_draft.json'), closure_sha256=sha(out / 'closure.json'), records=len(pins))))


if __name__ == '__main__':
    main()
