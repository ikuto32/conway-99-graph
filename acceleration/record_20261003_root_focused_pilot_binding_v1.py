"""Metadata-only binding of a separately checked finite saved-object population."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import sys
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'acceleration/record_20261003_root_focused_pilot_binding_v1.py'
SPEC = 'acceleration/record_20261003_root_focused_pilot_binding_v1_spec.md'
CLAIM = 'C-HYPERGRAPH-ROOT-FOCUSED-PILOT01-SAVED-OBJECTS'
REPORT = 'acceleration/results/20261003_independent_review/root_focused_saved_pilot01/summary.json'
REPORT_SHA = '7b54dfeb4d54c6a0cb99ab18a67bf2a5d0b263290e4a120cebc6d38a0d5af558'
CAL = 'acceleration/results/20261003_independent_review/root_focused_saved_calibration03/summary.json'
CAL_SHA = '328e3ee2d503ab4977b23f3fa9dd436109badcadfb1807543169081023c2bd8f'
RUN = 'acceleration/results/20261003_hypergraph_root_focused_pilot01/summary.json'
RUN_SHA = 'c9c17f0ab42d1d6a1d62f05d610d33761dc7099730d6185904f500e622945476'
OBJECTS = 'acceleration/results/20261003_independent_review/root_focused_saved_pilot01/object_audits.json'
OBJECTS_SHA = '7076894b5c64ef2b5f26f5ec038c32dfbf49159644a263a9273f0e44b701082b'
TRACE = 'acceleration/results/20261003_independent_review/root_focused_saved_pilot01/sparse_trace_audit.json'
TRACE_SHA = '955ea2de5c3babff8d6d3a249d178ba5aaabc075a6cba2024a0f5d00b8add2b1'
LOCAL = 'acceleration/results/20261003_independent_review/root_focused_saved_pilot01/localzero_population.json'
LOCAL_SHA = '37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570'
BASE = 'acceleration/results/20261003_hypergraph_root_focused_pilot01/native/'
CURRENT_SHA = '3f910d235e38191b5ac47523c22166f1abfc4d1f3ad285b60d4c684392a6670d'
BEST_SHA = '339086c8a1aaf1be2b4068d83945f4de4b1fc130f8ad8698708420ccc5d98467'
STATE_SHA = 'f38346ba0d3367acfc585854587e30bf5748ffe5ede658cd0055f41edd0f0bb3'
DIRECT_DIRS = [
    'acceleration/results/20261003_independent_review/root_focused_saved_calibration03',
    'acceleration/results/20261003_independent_review/root_focused_saved_calibration_supervision03',
    'acceleration/results/20261003_independent_review/root_focused_saved_pilot01',
    'acceleration/results/20261003_independent_review/root_focused_saved_pilot_supervision01',
    'acceleration/results/20261003_hypergraph_root_focused_pilot01',
    'acceleration/results/20261003_hypergraph_root_focused_pilot_supervision01',
]
STATEMENT = ('The exact root-focused pilot01 current.adj and best_root.adj, respectively SHA256 '
             + CURRENT_SHA + ' and ' + BEST_SHA + ', are symmetric binary zero-diagonal99-vertex14-regular '
             'point graphs of231linear triples with pointdegree7 and the same seven literal root11 triples. '
             'Their exact objective SRG_ROOT_LOCAL_PAIR_RESIDUAL_V1 is Froot=60E_lambda+Rroot=10 with '
             'E_lambda=0; current E_mu=5476 and best_root E_mu=5520. For each graph the root11 nonadjacent '
             'common-neighbor histogram is {1:5,2:74,3:5}; neither satisfies the target SRG identity. '
             'The106saved native files,102state files representing101distinct saved steps,204complete '
             'matrix observations and all10099stored proposals were independently checked. '
             'This is a finite saved-object and stored-trace result; the authenticated native counter '
             'reports10000000proposals, whose complete trajectory was not checked.')


def need(ok, diagnostic):
    if not ok:
        raise ValueError(diagnostic)


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--seconds', type=float, required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='Finite exact-r1 metadata binding from separately checked pilot files;20s save reserve;no graph/trace replay,ledger,index or native calls')
    out = (ROOT / args.out).resolve()
    need(out.is_relative_to(ROOT), 'Workspace output')
    out.mkdir(parents=True, exist_ok=False)
    pins = {}

    def pin(name, wanted=None):
        need(deadline.status()['remaining_seconds'] > 20, 'Metadata serialization reserve')
        path = (ROOT / name).resolve()
        need(path.is_relative_to(ROOT), 'Workspace evidence path')
        h = sha(path)
        need(wanted is None or h == wanted, 'Exact preserved identity ' + name)
        need(name not in pins or pins[name] == h, 'Consistent direct evidence closure')
        pins[name] = h
        return h

    try:
        protected = {name: sha(ROOT/name) for name in ['CLAIMS.yaml', '.git/index']}
        for path, identity in [(REPORT, REPORT_SHA), (CAL, CAL_SHA), (RUN, RUN_SHA),
                               (OBJECTS, OBJECTS_SHA), (TRACE, TRACE_SHA), (LOCAL, LOCAL_SHA),
                               (BASE+'current.adj', CURRENT_SHA), (BASE+'best_root.adj', BEST_SHA),
                               (BASE+'final.state', STATE_SHA)]:
            pin(path, identity)
        report = json.loads((ROOT/REPORT).read_bytes())
        cal = json.loads((ROOT/CAL).read_bytes())
        run = json.loads((ROOT/RUN).read_bytes())
        objects = json.loads((ROOT/OBJECTS).read_bytes())
        need(report['status'] == 'INDEPENDENT_ROOT_FOCUSED_SAVED_OBJECTS_V1_PASS'
             and report['producer'] == '/root/native_driver' and report['verifier'] == '/root/checkpoint_audit'
             and report['method'] == 'independent_artifact_check', 'Separate independent saved-object report')
        integer_fields = dict(saved_states=101, saved_state_files=102, saved_selected_object_files=0,
                              saved_localzero_object_observations=0, native_reported_proposals=10000000,
                              saved_trace_records=10099, complete_anchored_proposals=10099,
                              locally_checked_global_gaps=0, zero_target_candidates=0)
        need(all(type(report[key]) is int and report[key] == value for key,value in integer_fields.items()),
             'Exact literal checked populations')
        need(report['complete_trajectory_checked'] is False and report['target_resolution'] == 'NONE'
             and report['actual_retention_event_population'] == {}
             and report['minimum_mu_over_saved_localzero'] is None, 'No unobserved trajectory or target promotion')
        need(len(objects) == 102 and sum(len(record['full_scalar_objects']) for record in objects) == 204,
             'Exact scalar object observation population')
        need(sum(item['ordered_entries_checked'] for record in objects for item in record['full_scalar_objects'].values()) == 1999404,
             'Exact scalar ordered entry population')
        finals = [record for record in objects if record['path'] == BASE+'final.state']
        need(len(finals) == 1, 'One literal final-state audit')
        final = finals[0]['full_scalar_objects']
        for name, mu, mismatch in [('current',5476,5500), ('best_root',5520,5580)]:
            item = final[name]
            need((item['root_energy'],item['lambda_energy'],item['mu_energy'],item['root_residual']) == (10,0,mu,10)
                 and item['identity_mismatches'] == mismatch and item['srg_valid'] is False
                 and item['adjacent_cn_histogram'] == {'1':693}
                 and item['root_adjacent_cn_histogram'] == {'1':14}
                 and item['root_nonadjacent_cn_histogram'] == {'1':5,'2':74,'3':5},
                 'Exact saved final-object diagnostics ' + name)
        need(len(run['raw']['artifacts']) == 106 and run['raw']['actual_exit_code'] == 0,
             'Exact native output and receipt population')
        need(cal['status'] == 'INDEPENDENT_ROOT_FOCUSED_SAVED_OBJECTS_V1_CALIBRATION_PASS',
             'Changed saved-object checker calibration')
        for evidence in [cal, report]:
            for name,identity in evidence['inputs_sha256'].items():
                pin(name, identity)
        for name in [SOURCE, SPEC, 'docs/COMPUTE_POLICY.md', 'acceleration/compute_policy.json']:
            pin(name)
        for directory in DIRECT_DIRS:
            need((ROOT/directory).is_dir(), 'Exact saved direct receipt directory')
            for path in sorted((ROOT/directory).rglob('*')):
                if path.is_file():
                    pin(path.relative_to(ROOT).as_posix())
        protocol_path = 'acceleration/results/20261003_hypergraph_root_focused_pilot01/protocol.json'
        protocol = json.loads((ROOT/protocol_path).read_bytes())
        now = datetime.now(timezone.utc).isoformat()
        limitations = [
            'One fixed root11 start, fixed seed/configuration and restricted frozen-root move kernel; no automorphism assumption or exhaustive graph coverage.',
            'The10000000proposal count is an authenticated native counter; only10099stored proposals and saved anchors were replayed, not the complete trajectory.',
            '204scalar graph checks count current/best observations including duplicate matrices; they are not204distinct graphs.',
            'Root F/R improvement from50to10 accompanies a larger global E_mu; different objectives do not define target-wide progress.',
            'No saved root-localzero objects or full99SRG identity zeros; no earliest-attainment, unobserved minimum, global-minimum, performance or ergodicity claim.',
            'Rroot0 alone would not establish unique support pairs, and the actual final Rroot10 does not supply a full189-edge SRG root scaffold.',
            'The finite engine strict accepted_mu_improvement localzero-retention branch was unexercised; no absent scientific retained objects imply branch coverage.',
            'No exclusion, novelty, peer-review or target-resolution claim.'
        ]
        binding = dict(id=CLAIM,revision=1,claim_revision=1,kind='empirical/engineering result',basis=['COMPUTED'],
            status='VERIFIED',review_state='CLEAR',statement=STATEMENT,
            scope=dict(description='One authenticated fixed-root pilot and its exact saved current/best graphs, complete saved-file population and all anchored stored proposals. No whole trajectory or target-wide conclusion.',unrestricted_target=False,target_resolution='NONE'),
            assumptions=['Exact raw native file identities and changed independently calibrated scalar/set/RNG/state checking path.',
                         'The recorded original seven labelled root11 triples are fixed literal input rows; no target automorphism or support-pair uniqueness assumption.'],
            dependencies=[],producer='/root/native_driver',verifier='/root/checkpoint_audit',method='independent_artifact_check',
            verification_timestamp=report['timestamp'],report=REPORT,report_sha256=REPORT_SHA,
            created_at=now,updated_at=now,source_commit=protocol['source_commit'],
            source_commit_role='Actual native source context; direct local source/gate identities remain separately authenticated.',
            inputs_sha256=pins,command=report['command'],working_directory=report['cwd'],tool_versions=dict(python=report['python'],dependency_lock='uv.lock'),
            controls=dict(calibration=dict(path=CAL,sha256=CAL_SHA,positive_controls=5,strict_negative_controls=25),
                          full=dict(path=REPORT,sha256=REPORT_SHA,native_files=106,state_files=102,distinct_saved_steps=101,
                                    scalar_graph_observations=204,ordered_matrix_entries=1999404,anchored_stored_proposals=10099,unanchored_stored_proposals=0)),
            recorded_validation=dict(current_graph_sha256=CURRENT_SHA,best_root_graph_sha256=BEST_SHA,final_state_sha256=STATE_SHA,
                                     root=11,n=99,point_degree=7,graph_degree=14,linear_triples=231,frozen_literal_triples=7,
                                     current=dict(Froot=10,E_lambda=0,Rroot=10,E_mu=5476,identity_mismatches=5500),
                                     best_root=dict(Froot=10,E_lambda=0,Rroot=10,E_mu=5520,identity_mismatches=5580),
                                     root_nonadjacent_cn_histogram={'1':5,'2':74,'3':5},saved_localzero_objects=0,
                                     zero_target_object_observations=0,complete_trajectory_checked=False,new_exclusions=0),
            source_configuration=dict(objective=protocol['objective'],distribution=protocol['distribution'],options=protocol['options'],
                                      seed=99033011,reported_proposals=10000000,reported_counter_not_full_replay=True),
            supplemental_verification_records=[dict(claim_id=CLAIM,claim_revision=1,verifier='/root/checkpoint_audit',
                method='independent_artifact_check',audit_path=REPORT,audit_sha256=REPORT_SHA,timestamp=report['timestamp'],outcome='PASS',
                command=report['command'],cwd=report['cwd'],python=report['python'],artifact_hashes=report['inputs_sha256'],
                scope='Every saved file/state/matrix and every anchored stored proposal; not unrecorded steps',shared_components=report['shared_components'])],
            shared_components=report['shared_components'],limitations=limitations,target_resolution='NONE',
            availability='LOCAL_ONLY',retrieval='Exact workspace paths with locked checking commands; public replay requires a separate immutable publication check.',
            unavailable_information=dict(external_review=None,external_review_reason='No external review recorded',
                                         cpu_model=None,cpu_model_reason='No performance claim; runtime identity and receipts retained',
                                         unrecorded_trajectory=None,unrecorded_trajectory_reason='Only selected trace records/checkpoint anchors were saved'),
            historical_protected_execution_state=dict(observations_sha256=protected,unchanged_during_command=True,
                                                      role='Before/after metadata observations, not immutable scientific dependencies'),
            metadata_only=True,writer_source_sha256=pins[SOURCE],writer_command=[sys.executable,*sys.argv],
            ledger_mutations=0,index_mutations=0,mathematical_replays=0,scientific_invocations=0)
        save(out/'claim_binding_schema2.json',binding)
        need(all(sha(ROOT/name) == identity for name,identity in protected.items()), 'Protected ledger/index unchanged')
        save(out/'summary.json',dict(status='EXACT_ROOT_FOCUSED_PILOT01_SAVED_OBJECTS_R1_BINDING_RECORDED',timestamp=now,
                                     claim_id=CLAIM,claim_revision=1,binding_sha256=sha(out/'claim_binding_schema2.json'),
                                     report_sha256=REPORT_SHA,full_direct_input_records=len(pins),ledger_mutations=0,index_mutations=0,
                                     mathematical_replays=0,scientific_invocations=0,python=platform.python_version(),deadline=deadline.status()))
        print('EXACT_ROOT_FOCUSED_PILOT01_SAVED_OBJECTS_R1_BINDING_RECORDED')
    except BaseException as error:
        save(out/'failure.json',dict(error=repr(error),inputs_sha256=pins,outputs_preserved=True,
                                    mathematical_replays=0,ledger_mutations=0,index_mutations=0,deadline=deadline.status()))
        raise


if __name__ == '__main__':
    main()
