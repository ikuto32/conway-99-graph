"""Bind completed box-wave SAT/UNKNOWN records; UNSAT needs another checker."""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import platform
import subprocess
import sys

import audit_20260930_gram_box_nogood_v1 as box
import audit_20260930_rook_box_augmented_sat_v1 as sat

ROOT,need,digest,key = box.ROOT,box.need,box.digest,box.key


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('wave','collection-audit','out'):parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--collection-audit-sha256',required=True)
    args = parser.parse_args();need(not args.out.exists(),'refuse overwrite')
    bindings = {}
    def bind(path,expected=None):
        name = key(path)
        if name not in bindings:bindings[name] = digest(path)
        need(expected is None or expected == bindings[name],'artifact identity: '+name)
        return bindings[name]
    def read(path,expected=None):bind(path,expected);return json.loads(Path(path).read_bytes())
    collection = read(args.collection_audit,args.collection_audit_sha256)
    need(collection['status'] == 'INDEPENDENT_TARGET_GRAM_BOX_COLLECTION_PASS','independent cut collection gate')
    for name,value in collection['inputs_sha256'].items():bind(ROOT/name,value)
    final = read(args.wave/'final_checkpoint.json');summary = read(args.wave/'summary.json');manifest = read(args.wave/'manifest.json')
    need(summary['counts'] == final['counters'] and summary['stop_reason'] == final['state'],'final metadata consistency')
    need(collection['ordered_cuts'] == final['ordered_cuts'],'exact final ordered collection')
    for name,value in manifest['input_hashes'].items():bind(ROOT/name,value)
    base = ROOT/'acceleration/results/20260930_rook_free_internal_sat/instance.cnf'
    model_path = ROOT/'acceleration/results/20260930_rook_free_internal_sat/model.json'
    model = read(model_path,'26908e992235e307cfc6145275deb3d2765a930c7c59a774c9a7bc42f2f0f95e')
    bind(base,'ed9d0e102b16481fdbcecef34240b5be2b8a357af8c219606bb688dcb5fe9403')
    mapping = box.support.reconstruct_mapping(model);star = read(box.support.STAR)
    initial = read(args.wave/'checkpoint_00.json')
    initial_count = len(initial['ordered_cuts'])
    need(initial['ordered_cuts'] == final['ordered_cuts'][:initial_count] and initial_count == summary['initial_cuts'],'initial prefix')
    counts = dict(solver_rounds=0,proof_replay_calls=0,unproved_unsat_answers=0,independent_local_sat_passes=0,
                  negative_gram_windows=0,new_independently_checked_cuts=0,unchecked_unsat_proofs=0,unknown_solver_results=0)
    consumed,records,anomalies = 0.0,[],[]
    for number,record in enumerate(final['round_records'],1):
        need(record['round'] == number,'contiguous rounds')
        folder = args.wave/f'round_{number:02d}'
        bind(ROOT/record['cnf'],record['cnf_sha256'])
        prefix = read(ROOT/record['ordered_cuts'],record['ordered_cuts_sha256'])
        need(prefix == final['ordered_cuts'][:initial_count+counts['new_independently_checked_cuts']],'ordered cut prefix')
        need(len(prefix) == record['mathematical_cuts'] and record['clauses'] == model['clauses']+len(prefix),'exact instance counts')
        receipt = read(folder/'solver/receipt.json')
        need(receipt['solver_answer'] == record['solver_answer'] and receipt['cnf_sha256'] == record['cnf_sha256'],'solver instance identity')
        counts['solver_rounds'] += 1;consumed += receipt['wall_seconds']
        current = dict(round=number,cnf_sha256=record['cnf_sha256'],cuts_used=len(prefix),solver_answer=record['solver_answer'],
                       receipt=key(folder/'solver/receipt.json'),receipt_sha256=bind(folder/'solver/receipt.json'),worker_exit_code=receipt.get('worker_exit_code'))
        if receipt.get('worker_exit_code') not in (0,None):anomalies.append(dict(round=number,exit_code=receipt['worker_exit_code'],solver_answer=record['solver_answer']))
        if record['solver_answer'].startswith('UNKNOWN'):
            counts['unknown_solver_results'] += 1;records.append(current)
            need(number == len(final['round_records']),'UNKNOWN followed by more solver rounds')
            continue
        need(record['solver_answer'] == 'SAT_MODEL_UNCHECKED','UNSAT or unsupported outcome needs separate proof audit')
        audit = read(ROOT/record['sat_audit'],record['sat_audit_sha256'])
        need(audit['status'] == 'INDEPENDENT_BOX_AUGMENTED_ROOK_WINDOW_SAT_PASS','independent box SAT artifact gate')
        for name,value in audit['inputs_sha256'].items():bind(ROOT/name,value)
        need(audit['checker_sha256'] == bind(sat.__file__),'frozen independently authored SAT checker')
        need(audit['base_cnf_sha256'] == bind(base) and audit['augmented_cnf_sha256'] == record['cnf_sha256']
             and audit['model_sha256'] == bind(model_path) and audit['checked_clauses'] == record['clauses'],'complete saved raw SAT check identity')
        need([row['clause'] for row in audit['ordered_cuts']] == [row['clause'] for row in prefix],'SAT audit cut order')
        assignment = read(folder/'solver/model.json',audit['assignment_sha256'])['assignment']
        values = {abs(lit):lit > 0 for lit in assignment}
        need(all(type(lit) is int and lit != 0 for lit in assignment) and len(assignment) == len(values) == model['variables']
             and set(values) == set(range(1,model['variables']+1)),'complete signed assignment')
        external = [row.copy() for row in model['known_adjacency']]
        for variable,(u,v) in mapping.items():external[u-9][v-9] = external[v-9][u-9] = int(values[variable])
        graph = box.support.window.graphcheck.embed59(external)
        raw = read(ROOT/record['graph'],record['graph_sha256'])['adjacency_full59']
        need(graph == raw and audit['raw_graph_sha256'] == record['graph_sha256'],'fresh assignment/raw graph decode')
        box.support.window.validate_candidate(graph,star,True)
        need(all(any(values[abs(lit)] == (lit > 0) for lit in row['clause']) for row in prefix),'decoded prior box cuts')
        execution = read(folder/'sat_check.receipt.json');need(execution['exit_code'] == 0,'complete saved SAT checker execution')
        for stream in ('stdout','stderr'):bind(folder/f'sat_check.{stream}.log',execution[f'{stream}_sha256'])
        counts['independent_local_sat_passes'] += 1
        current.update(sat_audit=record['sat_audit'],sat_audit_sha256=record['sat_audit_sha256'],graph_sha256=record['graph_sha256'],
                       original_complete_clause_check=audit['checked_clauses'],fresh_raw_graph_decode=True)
        if 'next_cut_audit' in record:
            added = collection['results'][initial_count+counts['new_independently_checked_cuts']]
            need(added['audit'] == record['next_cut_audit'] and added['audit_sha256'] == record['next_cut_audit_sha256']
                 and added['graph_sha256'] == record['graph_sha256'],'new bound cut rejects exact completed SAT graph')
            counts['negative_gram_windows'] += 1;counts['new_independently_checked_cuts'] += 1
            current.update(new_cut_literals=added['clause_length'],new_cut_maximum=added['global_boolean_box_upper_bound'],new_cut_audit=added['audit'],new_cut_audit_sha256=added['audit_sha256'])
            checkpoint = read(args.wave/f'checkpoint_{number:02d}.json')
            need(checkpoint['counters'] == counts and checkpoint['ordered_cuts'] == final['ordered_cuts'][:initial_count+counts['new_independently_checked_cuts']],'restart checkpoint count/prefix chain')
        records.append(current)
    need(counts == final['counters'],'reconstructed stage populations')
    need(initial_count+counts['new_independently_checked_cuts'] == len(final['ordered_cuts']) == summary['accepted_cuts_at_end'],'final cut count')
    need(abs(consumed-summary['cumulative_solver_process_seconds']) < 1e-8 and abs(consumed-final['cumulative_solver_process_seconds']) < 1e-8,'recorded measured time sum')
    for path in (Path(__file__),sat.__file__,box.__file__,ROOT/'uv.lock'):bind(path)
    need(all(digest(ROOT/name) == value for name,value in bindings.items()),'stable artifact identities')
    report = dict(status='INDEPENDENT_ROOK_BOX_WAVE_ARTIFACT_BINDING_PASS',timestamp=datetime.now(timezone.utc).isoformat(),
                  source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),
                  verifier='/root/eight_domain_audit independent checking agent',verification_type='Exact binding of full independently authored SAT checks; fresh raw decode; independently replayed box collection and ordered checkpoint chain',
                  inputs_sha256=bindings,counts=counts,initial_cuts=initial_count,accepted_cuts_at_end=len(final['ordered_cuts']),rounds=records,
                  terminal_state=summary['stop_reason'],recorded_cumulative_solver_process_seconds=consumed,recorded_overall_seconds=summary['overall_seconds'],worker_exit_records=anomalies,
                  live_process_state='UNKNOWN',live_process_state_reason='Saved execution receipts are historical; this audit does not query live processes',
                  producer_imported=False,shared_components=['Earlier independent box collection and raw59 graph checkers','Original complete raw CNF checks are authenticated, not repeated in this binding pass'],
                  statement='The recorded finite box-cut wave has the independently reconstructed attempt/outcome counts and exact artifact chain. Each completed SAT assignment and new cut has the specified independent artifact checks.',
                  scope='One finite wave in one frozen780edge family; no target-wide coverage or complete-family exclusion',
                  limitations=['UNKNOWN carries no SAT/UNSAT conclusion.','No unrestricted resolution, external review, performance guarantee, or summed excluded population.'],
                  target_resolution=False,external_review=False,artifact_availability='LOCAL_ONLY')
    args.out.parent.mkdir(parents=True,exist_ok=True)
    with args.out.open('x',encoding='utf-8') as stream:json.dump(report,stream,indent=2);stream.write('\n')
    print(json.dumps(dict(status=report['status'],counts=counts,sha256=digest(args.out))))


if __name__ == '__main__':main()
