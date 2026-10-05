"""Check a complete SAT object against exact base plus audited orbit clauses.

Commands: calibrate --out NEWDIR; or check (see --help). Calibration deliberately
uses the original base with an empty extra-clause list and is not an orbit SAT
certificate. No solver or discovery implementation is imported.
"""
import argparse
import copy
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

import audit_20260930_rook_augmented_sat_v1 as streams

gram = streams.gram
ROOT, need, digest, key = gram.ROOT, gram.need, gram.digest, gram.key
ENCODING_SHA = 'a74e821f70680187e0ee14fb956d51928e6aa9517acc1bc0186448b32c985ba0'


def save(path, obj):
    with Path(path).open('x',encoding='utf-8') as stream:
        json.dump(obj,stream,indent=2)
        stream.write('\n')


def verify_object(base_path, augmented_path, model, signed, clauses, star):
    need(type(signed) is list and all(type(x) is int and x != 0 for x in signed), 'signed integers')
    assignment = {abs(x):x > 0 for x in signed}
    need(len(assignment) == len(signed) == model['variables'] and set(assignment) == set(range(1,model['variables']+1)), 'complete unique variable assignment')
    with Path(base_path).open('rb') as base,Path(augmented_path).open('rb') as augmented:
        count = streams.check_streams(base,augmented,assignment,clauses,model['variables'],model['clauses'])
    mapping = gram.reconstruct_mapping(model)
    adjacency = [row.copy() for row in model['known_adjacency']]
    for variable,(u,v) in mapping.items():
        adjacency[u-9][v-9] = adjacency[v-9][u-9] = int(assignment[variable])
    graph = gram.window.graphcheck.embed59(adjacency)
    graph_result = gram.window.validate_candidate(graph,star,True)
    for clause in clauses:
        need(any(bool(graph[mapping[abs(lit)][0]][mapping[abs(lit)][1]]) == (lit > 0) for lit in clause), 'decoded graph violates orbit clause')
    return dict(checked_clauses=count,graph_result=graph_result),graph


def code_paths():
    return [Path(__file__),Path(streams.__file__),Path(gram.__file__),Path(gram.window.__file__),
            Path(gram.window.symbolic.__file__),Path(gram.window.graphcheck.__file__),ROOT/'uv.lock']


def base_report():
    return dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),
                verifier='/root/state_literature_audit independent checking agent',producer_imported=False,
                shared_components=['Frozen independently authored exact SAT stream checker and raw59 graph validator','Python exact arithmetic'],
                solver_launched=False,target_resolution=False,external_review=False,artifact_availability='LOCAL_ONLY')


def calibrate(args):
    args.out.mkdir(parents=True,exist_ok=False)
    source = ROOT/'acceleration/results/20260930_rook_free_internal_sat'
    base,model_path,gate_path = source/'instance.cnf',source/'model.json',source/'independent_cnf_encoding.json'
    assignment_path = ROOT/'acceleration/results/20260930_rook_free_internal_pilot/main/model.json'
    prior_path = ROOT/'acceleration/results/20260930_rook_free_internal_independent_certificate/summary.json'
    graph_path = prior_path.with_name('independent_full59.json')
    need(digest(gate_path) == ENCODING_SHA,'encoding pin')
    prior = json.loads(prior_path.read_bytes())
    need(prior['status'] == 'INDEPENDENT_ROOK_FREE_INTERNAL_LOCAL_SAT_PASS','known SAT fixture provenance')
    for path in (base,model_path,assignment_path):
        need(prior['inputs_sha256'][key(path)] == digest(path),'known fixture artifact hash')
    model = json.loads(model_path.read_bytes())
    signed = json.loads(assignment_path.read_bytes())['assignment']
    star = json.loads(gram.STAR.read_bytes())
    controls = streams.controls()
    positive,graph = verify_object(base,base,model,signed,[],star)
    need(graph == json.loads(graph_path.read_bytes())['adjacency_full59'],'original independently reconstructed raw59 fixture')
    save(args.out/'positive_full59.json',dict(adjacency_full59=graph,target_graph=False,calibration_only=True))
    rejected = []
    cases = [('flipped_edge_assignment',[-lit if abs(lit)==1 else lit for lit in signed]),
             ('missing_variable_assignment',signed[:-1]),('duplicate_variable_assignment',signed+[signed[0]])]
    for name,wrong in cases:
        save(args.out/(name+'.json'),dict(assignment=wrong,deliberately_corrupted=True))
        try:
            verify_object(base,base,model,wrong,[],star)
        except ValueError as error:
            rejected.append(dict(case=name,error=str(error)))
        else:
            raise ValueError('calibration corruption accepted: '+name)
    for name,mutate in [('graph_loop',lambda a:a[0].__setitem__(0,1)),('deleted_fixed_edge',lambda a:(a[0].__setitem__(1,0),a[1].__setitem__(0,0)))]:
        bad = copy.deepcopy(graph); mutate(bad)
        try:
            gram.window.validate_candidate(bad,star,True)
        except ValueError as error:
            rejected.append(dict(case=name,error=str(error)))
        else:
            raise ValueError('graph corruption accepted: '+name)
    report = base_report()
    report.update(status='INDEPENDENT_ROOK_ORBIT_SAT_CHECKER_CALIBRATION_PASS',
                  scope='Calibration only: original full base SAT with zero added orbit clauses; exact stream controls additionally exercise appended clauses and corruption cases.',
                  positive_complete_base_artifacts=1,positive_record=positive,raw_graph_sha256=digest(args.out/'positive_full59.json'),
                  full_artifact_corruptions_rejected=rejected,stream_controls=controls,
                  inputs_sha256={key(p):digest(p) for p in [base,model_path,gate_path,assignment_path,prior_path,graph_path,gram.STAR,*code_paths()]},
                  limitations=['No orbit-augmented SAT assignment has been checked by this calibration.','The finite controls test the checker; they are not a completeness proof for this local encoding.'])
    save(args.out/'summary.json',report)
    print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))


def check(args):
    started = time.monotonic()
    args.out.mkdir(parents=True,exist_ok=False)
    bindings = {}
    def pin(path, expected=None):
        path = Path(path)
        if not path.is_absolute():
            path = ROOT/path
        observed = digest(path)
        need(expected is None or observed == expected,'input hash mismatch: '+key(path))
        bindings[key(path)] = observed
        return path
    def read(path,expected=None):
        return json.loads(pin(path,expected).read_bytes())
    gate = read(args.encoding_audit,args.encoding_audit_sha256)
    need(gate['status'] == 'INDEPENDENT_ROOK_FREE_INTERNAL_WINDOW_CNF_ENCODING_PASS','encoding gate')
    for path in (args.base_cnf,args.model):
        pin(path,gate['inputs_sha256'][key(path)])
    orbit = read(args.orbit_audit,args.orbit_audit_sha256)
    need(orbit['status'] == 'INDEPENDENT_ROOK_GRAM_CUT_ORBITS_PASS' and orbit['review_state']=='CLEAR','orbit gate')
    need(orbit['base_cnf_sha256'] == digest(args.base_cnf) and orbit['encoding_model_sha256'] == digest(args.model),'same exact model/CNF family')
    for path,expected in orbit['inputs_sha256'].items():
        pin(path,expected)
    unique = read(orbit['unique_clauses_path'],orbit['unique_clauses_sha256'])
    need([x['id'] for x in unique] == list(range(orbit['unique_clauses'])), 'ordered orbit clause IDs')
    clauses = [x['clause'] for x in unique]
    part_path = pin(orbit['clauses_path'],orbit['clauses_sha256'])
    need(part_path.read_bytes() == ''.join(' '.join(map(str,c))+' 0\n' for c in clauses).encode('ascii'),'exact certified CNF suffix')
    signed = read(args.assignment)['assignment']
    model = read(args.model); star = read(gram.STAR)
    pin(args.augmented_cnf)
    controls = streams.controls()
    result,graph = verify_object(args.base_cnf,args.augmented_cnf,model,signed,clauses,star)
    graph_path = args.out/'independent_full59.json'
    save(graph_path,dict(adjacency_full59=graph,scope=gate['scope'],ordered_orbit_cut_count=len(clauses),target_graph=False))
    for path in code_paths():
        pin(path)
    need(all(digest(ROOT/name) == value for name,value in bindings.items()),'stable input artifacts')
    report = base_report()
    report.update(status='INDEPENDENT_ORBIT_AUGMENTED_ROOK_WINDOW_SAT_PASS',inputs_sha256=bindings,
                  verification_type='Every raw exact base and appended clause, complete signed assignment and independently reconstructed59vertex graph',
                  base_cnf_sha256=digest(args.base_cnf),augmented_cnf_sha256=digest(args.augmented_cnf),model_sha256=digest(args.model),assignment_sha256=digest(args.assignment),
                  orbit_gate_sha256=digest(args.orbit_audit),variables=model['variables'],base_clauses=model['clauses'],appended_clauses=len(clauses),**result,
                  raw_graph_path=key(graph_path),raw_graph_sha256=digest(graph_path),controls=controls,
                  statement='The complete saved assignment satisfies the exact base CNF and every independently certified transported clause, and decodes to the saved locally valid59vertex window.',
                  scope=gate['scope'],limitations=['A local59vertex SAT witness is not a complete99vertex target or proof of extension.','No UNSAT claim is checked by this program.','Mathematical cut soundness uses the hash-bound independent orbit/source proof gates; optimization proofs are not rerun here.'],
                  elapsed_seconds=time.monotonic()-started)
    save(args.out/'summary.json',report)
    print(json.dumps(dict(status=report['status'],checked_clauses=result['checked_clauses'],sha256=digest(args.out/'summary.json'))))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command',required=True)
    calibration = sub.add_parser('calibrate'); calibration.add_argument('--out',type=Path,required=True)
    checking = sub.add_parser('check')
    for name in ('base-cnf','augmented-cnf','model','assignment','orbit-audit','encoding-audit','out'):
        checking.add_argument('--'+name,type=Path,required=True)
    checking.add_argument('--orbit-audit-sha256',required=True)
    checking.add_argument('--encoding-audit-sha256',required=True)
    args = parser.parse_args()
    (calibrate if args.command == 'calibrate' else check)(args)


if __name__ == '__main__':
    main()
