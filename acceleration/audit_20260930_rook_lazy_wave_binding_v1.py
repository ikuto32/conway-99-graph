"""Independent finite-wave artifact binding and exact Gram-cut replay.

Does not launch a solver. Every original raw SAT clause check is authenticated
through its separately authored checker and saved raw input hashes; this pass
additionally decodes assignments and recalculates all raw Gram cuts itself.
An UNSAT terminal result is preserved as pending and is never promoted here.
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import platform
import subprocess
import sys

import audit_20260930_gram_nogood_v1 as gram
import audit_20260930_rook_augmented_sat_v1 as sat

ROOT = Path(__file__).resolve().parents[1]
need, digest, key = gram.need, gram.digest, gram.key
BASE = ROOT/'acceleration/results/20260930_rook_free_internal_sat/instance.cnf'
MODEL = ROOT/'acceleration/results/20260930_rook_free_internal_sat/model.json'
GATE = ROOT/'acceleration/results/20260930_rook_free_internal_sat/independent_cnf_encoding.json'
GATE_HASH = 'a74e821f70680187e0ee14fb956d51928e6aa9517acc1bc0186448b32c985ba0'
INITIAL_AUDIT_HASH = 'd0bdbc27029a4c6bf38199fc186afd031affefd2b4531413d83108c967d55ad8'
SAT_CONTROL = ROOT/'acceleration/results/20260930_rook_lazy_checker_controls/sat_control/summary.json'
SAT_CONTROL_HASH = '8bd319217edafa13d763a4e99612623d48c169b9c6dbf5da3ae78f301dc4d40e'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--wave',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args = parser.parse_args()
    need(not args.out.exists(),'refuse overwrite')
    bindings = {}
    # These are final immutable artifacts. Cache identities within this pass to
    # avoid hashing the same 78MB base CNF once per cut/round reference.
    identity_cache = {}
    stat_cache = {}
    def bind(path,expected=None):
        path = Path(path).resolve()
        name = key(path)
        if name not in identity_cache:
            identity_cache[name] = digest(path)
            stat = path.stat()
            stat_cache[name] = (stat.st_size,stat.st_mtime_ns)
        value = identity_cache[name]
        need(expected is None or value == expected,'artifact identity mismatch: '+name)
        bindings[name] = value
        return value
    def read(path,expected=None):
        bind(path,expected)
        return json.loads(Path(path).read_bytes())
    def authenticate(report):
        for name,expected in report['inputs_sha256'].items():
            bind(ROOT/name,expected)

    gate = read(GATE,GATE_HASH)
    need(gate['status'] == 'INDEPENDENT_ROOK_FREE_INTERNAL_WINDOW_CNF_ENCODING_PASS','encoding status')
    gate_inputs = {key(ROOT/name):value for name,value in gate['inputs_sha256'].items()}
    for p in (BASE,MODEL):
        bind(p,gate_inputs[key(p)])
    model = read(MODEL)
    star = read(gram.STAR)
    mapping = gram.reconstruct_mapping(model)
    control = read(SAT_CONTROL,SAT_CONTROL_HASH)
    authenticate(control)
    need(control['checker_sha256'] == bind(sat.__file__),'frozen independent SAT checker')
    stream_controls = sat.controls()
    manifest = read(args.wave/'manifest.json')
    summary = read(args.wave/'summary.json')
    final = read(args.wave/'final_checkpoint.json')
    need(summary['stop_reason'] == final['state'],'terminal state identity')
    need(summary['counts'] == final['counters'],'terminal counter identity')
    need(summary['target_graph'] is False and summary['target_nonexistence'] is False,'incorrect producer target claims')
    for name,expected in manifest['input_hashes'].items():
        # This includes producer/checker source, pinned environment and base
        # artifacts; native solver binary identity is separately retained in
        # the producer manifest and is not required for checking SAT objects.
        bind(ROOT/name,expected)
    need(manifest['limits'] == dict(solver_rounds=10,cumulative_solver_process_seconds=180,
                                   per_round_seconds=60,per_round_conflicts=1000000,overall_seconds=600),'preregistered resource limits')
    ordered = final['ordered_cuts']
    need(ordered and ordered[0]['audit_sha256'] == INITIAL_AUDIT_HASH,'initial independently verified cut')
    need(len({tuple(sorted(row['clause'])) for row in ordered}) == len(ordered),'duplicate cuts')
    cut_results = []
    for index,record in enumerate(ordered):
        cert_path,audit_path = ROOT/record['certificate'],ROOT/record['audit']
        cert = read(cert_path,record['certificate_sha256'])
        audit = read(audit_path,record['audit_sha256'])
        need(audit['status'] == 'INDEPENDENT_TARGET_GRAM_NOGOOD_PASS','cut checker status')
        authenticate(audit)
        need(audit['checker_sha256'] == bind(gram.__file__),'frozen independent cut checker')
        need(audit['certificate_sha256'] == bind(cert_path) and audit['base_cnf_sha256'] == bind(BASE)
             and audit['encoding_model_sha256'] == bind(MODEL),'cut model family identity')
        graph_paths = [ROOT/name for name,value in audit['inputs_sha256'].items() if value == cert['graph_sha256']]
        need(len(graph_paths) == 1,'unique raw cut graph binding')
        graph = read(graph_paths[0],cert['graph_sha256'])['adjacency_full59']
        gram.window.validate_candidate(graph,star,True)
        for u in range(50):
            for v in range(u+1,50):
                if model['known_adjacency'][u][v] != -1:
                    need(graph[u+9][v+9] == model['known_adjacency'][u][v],'raw graph fixed model edge')
        calibration,checked = gram.controls(cert,graph,mapping)
        need(checked['verified_clause'] == record['clause'] == audit['verified_clause'],'cut identity')
        need(checked['quadratic_value'] == audit['quadratic_value'],'exact quadratic identity')
        cut_results.append(dict(index=index,certificate=key(cert_path),certificate_sha256=bind(cert_path),
                                audit=key(audit_path),audit_sha256=bind(audit_path),graph=key(graph_paths[0]),
                                graph_sha256=bind(graph_paths[0]),clause=checked['verified_clause'],
                                clause_length=checked['clause_length'],support_size=checked['support_size'],
                                quadratic_value=checked['quadratic_value'],
                                exact_raw_quadratic_and_all_coefficients_replayed=True,controls=calibration))

    records = final['round_records']
    rounds = []
    anomalies = []
    graph_identities = set()
    consumed = 0.0
    actual = dict(solver_rounds=0,independent_local_sat_passes=0,negative_gram_windows=0,
                  new_independently_checked_cuts=0,unchecked_unsat_proofs=0,unknown_solver_results=0)
    for number,record in enumerate(records,1):
        need(record['round'] == number,'contiguous ordered round numbering')
        folder = args.wave/f'round_{number:02d}'
        bind(ROOT/record['cnf'],record['cnf_sha256'])
        prefix = read(ROOT/record['ordered_cuts'],record['ordered_cuts_sha256'])
        need(prefix == ordered[:len(prefix)] and len(prefix) == number,'exact sequential cut prefix')
        need(record['mathematical_cuts'] == len(prefix) and record['variables'] == model['variables']
             and record['clauses'] == model['clauses']+len(prefix),'instance counts')
        instance = read(folder/'instance_record.json')
        need(all(record[name] == value for name,value in instance.items()),'frozen pre-solver instance record')
        receipt = read(folder/'solver/receipt.json')
        need(receipt['cnf_sha256'] == record['cnf_sha256'] and receipt['solver_answer'] == record['solver_answer'],'solver receipt binding')
        actual['solver_rounds'] += 1
        consumed += receipt['wall_seconds']
        if receipt.get('worker_exit_code') not in (0,None):
            anomalies.append(dict(round=number,worker_exit_code=receipt['worker_exit_code'],
                                  solver_answer=receipt['solver_answer'],artifact_check_is_separate=True))
        entry = dict(round=number,instance_sha256=record['cnf_sha256'],cuts_used=len(prefix),solver_answer=record['solver_answer'],
                     solver_receipt=key(folder/'solver/receipt.json'),solver_receipt_sha256=bind(folder/'solver/receipt.json'))
        if record['solver_answer'] != 'SAT_MODEL_UNCHECKED':
            need(number == len(records),'terminal nonsat result followed by another round')
            if record['solver_answer'] == 'UNSAT_PROOF_UNCHECKED':
                actual['unchecked_unsat_proofs'] += 1
                entry['status'] = 'UNSAT_PENDING_SEPARATE_COMPLETE_PROOF_REPLAY'
            else:
                actual['unknown_solver_results'] += 1
                entry['status'] = 'UNKNOWN'
            rounds.append(entry)
            continue
        audit = read(ROOT/record['sat_audit'],record['sat_audit_sha256'])
        need(audit['status'] == 'INDEPENDENT_AUGMENTED_ROOK_WINDOW_SAT_PASS','SAT checker status')
        authenticate(audit)
        need(audit['checker_sha256'] == bind(sat.__file__),'SAT checker frozen identity')
        need(audit['augmented_cnf_sha256'] == record['cnf_sha256'] and audit['base_cnf_sha256'] == bind(BASE)
             and audit['model_sha256'] == bind(MODEL),'exact SAT instance binding')
        need(audit['checked_clauses'] == record['clauses'] and audit['appended_clauses'] == len(prefix)
             and audit['variables'] == model['variables'],'complete original SAT check population')
        need([row['clause'] for row in audit['ordered_cuts']] == [row['clause'] for row in prefix],'SAT audit ordered clauses')
        assignment = read(folder/'solver/model.json',audit['assignment_sha256'])['assignment']
        need(all(type(literal) is int and literal != 0 for literal in assignment),'integer signed assignment')
        values = {abs(literal):literal>0 for literal in assignment}
        need(len(assignment) == len(values) == model['variables'] and set(values) == set(range(1,model['variables']+1)),'complete unique assignment')
        external = [row.copy() for row in model['known_adjacency']]
        for variable,(u,v) in mapping.items():
            external[u-9][v-9] = external[v-9][u-9] = int(values[variable])
        decoded = gram.window.graphcheck.embed59(external)
        graph = read(ROOT/record['graph'],record['graph_sha256'])['adjacency_full59']
        need(decoded == graph and audit['raw_graph_sha256'] == record['graph_sha256'],'independent assignment/raw graph identity')
        gram.window.validate_candidate(graph,star,True)
        for cut in prefix:
            need(any(values[abs(literal)] == (literal > 0) for literal in cut['clause']),'assignment violates previously accepted cut')
        graph_identities.add(sha256(json.dumps(graph,separators=(',',':')).encode()).hexdigest())
        sat_receipt = read(folder/'sat_check.receipt.json')
        need(sat_receipt['exit_code'] == 0,'saved complete SAT audit execution')
        for which in ('stdout','stderr'):
            bind(folder/f'sat_check.{which}.log',sat_receipt[f'{which}_sha256'])
        actual['independent_local_sat_passes'] += 1
        entry.update(status='INDEPENDENT_LOCAL_SAT_ARTIFACT_BOUND',sat_audit=record['sat_audit'],
                     sat_audit_sha256=record['sat_audit_sha256'],complete_clauses_checked_by_original_audit=audit['checked_clauses'],
                     assignment_and_raw59_redecoded_in_this_pass=True,graph_sha256=record['graph_sha256'])
        if 'next_cut_audit' in record:
            need(number < len(ordered),'missing newly accepted cut')
            addition = ordered[number]
            need(addition['audit'] == record['next_cut_audit'] and addition['audit_sha256'] == record['next_cut_audit_sha256'],'next cut binding')
            need(cut_results[number]['graph_sha256'] == record['graph_sha256'],'new cut rejects this exact local graph')
            need(record['next_cut_literals'] == cut_results[number]['clause_length'],'cut literal population')
            actual['negative_gram_windows'] += 1
            actual['new_independently_checked_cuts'] += 1
            checkpoint = read(args.wave/f'checkpoint_{number:02d}.json')
            need(checkpoint['ordered_cuts'] == ordered[:number+1] and checkpoint['round_records'] == records[:number]
                 and checkpoint['counters'] == actual,'saved restart checkpoint chain')
            entry.update(new_cut_audit=record['next_cut_audit'],new_cut_audit_sha256=record['next_cut_audit_sha256'],
                         negative_quadratic=cut_results[number]['quadratic_value'],new_cut_literals=record['next_cut_literals'])
        else:
            need(number == len(records),'uncut SAT result followed by round')
            entry['no_new_cut_reason'] = summary['stop_reason']
        rounds.append(entry)
    need(actual == final['counters'],'independently reconstructed stage counts')
    need(len(ordered) == 1+actual['new_independently_checked_cuts'] == summary['accepted_cuts_at_end'],'accepted cut count')
    need(summary['initial_cuts'] == 1,'initial distinct cut population')
    need(abs(consumed-final['cumulative_solver_process_seconds']) < 1e-8
         and abs(consumed-summary['cumulative_solver_process_seconds']) < 1e-8,'recorded timing sum')
    for p in (__file__,gram.__file__,sat.__file__,ROOT/'uv.lock'):
        bind(p)
    for name,(size,mtime) in stat_cache.items():
        observed = (ROOT/name).stat()
        need((observed.st_size,observed.st_mtime_ns) == (size,mtime),'artifact changed during binding: '+name)
    report = dict(status='INDEPENDENT_ROOK_LAZY_WAVE_ARTIFACT_BINDING_PASS',
                  timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                  command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),
                  verifier='/root/eight_domain_audit independent checking agent',
                  verification_type='Authenticated complete independently authored SAT checks, raw assignment/graph replay, every exact cut polynomial and corrupted controls, and ordered checkpoint coverage',
                  claim_id=None,claim_id_null_reason='Registrar may bind this finite-wave collection to a new scoped claim; no individual cut is self-promoted by its producer',
                  inputs_sha256=bindings,counts=actual,distinct_new_raw59_graphs=len(graph_identities),initial_cuts=1,
                  accepted_cuts_at_end=len(ordered),cuts=cut_results,rounds=rounds,stream_controls=stream_controls,
                  terminal_state=summary['stop_reason'],recorded_cumulative_solver_process_seconds=consumed,
                  recorded_overall_seconds=summary['overall_seconds'],native_cleanup_anomalies=anomalies,
                  live_process_state='UNKNOWN',live_process_state_reason='This artifact audit does not inspect operating-system processes',
                  producer_imported=False,shared_components=['Previously frozen independent Gram checker, raw59 validator, and SAT checker stream calibration',
                                                             'Python standard library exact integers; complete raw SAT checks are original saved independent executions, not repeated here'],
                  target_resolution=False,external_review=False,artifact_availability='LOCAL_ONLY',
                  scope='Finite recorded rounds in one780edge frozen-central-factor family. All accepted cuts are necessary only for target extensions preserving that scaffold.',
                  limitations=['No unrestricted or full fixed-star exclusion follows from repeated SAT objects and valid cuts.',
                               'UNSAT results, if present, remain pending a separate complete exact proof replay.',
                               'No equality or disjointness of excluded pattern populations; no summed coverage fraction.',
                               'Timing observations are recorded measurements, not performance guarantees; nonzero worker exits do not invalidate separately verified artifacts.'])
    args.out.parent.mkdir(parents=True,exist_ok=True)
    with args.out.open('x',encoding='utf-8') as stream:
        json.dump(report,stream,indent=2)
        stream.write('\n')
    print(json.dumps(dict(status=report['status'],counts=actual,accepted_cuts=len(ordered),sha256=digest(args.out))))


if __name__ == '__main__':
    main()
