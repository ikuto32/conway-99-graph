"""Independent full SAT certificate check for base plus ordered Boolean-box cuts.

This new checker preserves the earlier support-cut checker and its saved runs.
Only independently checked box cuts are accepted in this version's cut list.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

import audit_20260930_gram_box_nogood_v1 as box
import audit_20260930_rook_augmented_sat_v1 as previous

ROOT,need,digest,key = box.ROOT,box.need,box.digest,box.key
support = box.support


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('base-cnf','augmented-cnf','model','assignment','ordered-cuts','encoding-audit','out'):
        parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--encoding-audit-sha256',required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=False)
    started = time.monotonic()
    bindings = {}
    def read(path,expected=None):
        observed = digest(path)
        need(expected is None or observed == expected,'artifact hash mismatch: '+str(path))
        bindings[key(path)] = observed
        return json.loads(Path(path).read_bytes())
    stream_controls = previous.controls()
    gate = read(args.encoding_audit,args.encoding_audit_sha256)
    need(gate['status'] == 'INDEPENDENT_ROOK_FREE_INTERNAL_WINDOW_CNF_ENCODING_PASS','780edge encoding gate')
    authenticated = {key(ROOT/name):value for name,value in gate['inputs_sha256'].items()}
    for path in (args.base_cnf,args.model):
        need(digest(path) == authenticated[key(path)],'audited exact base model/CNF')
        bindings[key(path)] = digest(path)
    model = read(args.model)
    mapping = support.reconstruct_mapping(model)
    star = read(support.STAR)
    ordered = read(args.ordered_cuts)
    need(type(ordered) is list,'ordered cut list')
    clauses,cut_records = [],[]
    for record in ordered:
        cert_path,audit_path = ROOT/record['certificate'],ROOT/record['audit']
        certificate = read(cert_path,record['certificate_sha256'])
        audit = read(audit_path,record['audit_sha256'])
        need(audit['status'] == 'INDEPENDENT_TARGET_GRAM_BOX_NOGOOD_PASS' and audit['certificate_sha256'] == digest(cert_path),'prior box gate and exact certificate')
        need(audit['base_cnf_sha256'] == digest(args.base_cnf) and audit['encoding_model_sha256'] == digest(args.model)
             and certificate['base_cnf_sha256'] == digest(args.base_cnf) and certificate['encoding_model_sha256'] == digest(args.model),'same cut model family')
        graph_paths = [ROOT/name for name,value in audit['inputs_sha256'].items() if value == certificate['graph_sha256']]
        need(len(graph_paths) == 1,'unique raw box graph binding')
        graph = read(graph_paths[0],certificate['graph_sha256'])['adjacency_full59']
        support.window.validate_candidate(graph,star,True)
        for u in range(50):
            for v in range(u+1,50):
                if model['known_adjacency'][u][v] != -1:
                    need(graph[u+9][v+9] == model['known_adjacency'][u][v],'fixed model/box graph')
        checked = box.audit_certificate(certificate,graph,mapping)
        need(checked['verified_clause'] == record['clause'] == audit['verified_clause'],'ordered box clause identity')
        clauses.append(checked['verified_clause'])
        cut_records.append(dict(certificate=key(cert_path),certificate_sha256=digest(cert_path),audit=key(audit_path),audit_sha256=digest(audit_path),
                                clause=checked['verified_clause'],global_boolean_box_upper_bound=checked['global_boolean_box_upper_bound'],
                                mathematical_artifact_rechecked=True,raw_graph_sha256=digest(graph_paths[0])))
    need(support.product_basis((27,-9,1),(27,-9,1)) == (1701,-567,63),'universal exact PSD identity')
    signed = read(args.assignment)['assignment']
    need(all(type(lit) is int and lit != 0 for lit in signed),'signed integer assignment')
    assignment = {abs(lit):lit>0 for lit in signed}
    need(len(assignment) == len(signed) == model['variables'] and set(assignment) == set(range(1,model['variables']+1)),'complete assignment population')
    bindings[key(args.augmented_cnf)] = digest(args.augmented_cnf)
    with args.base_cnf.open('rb') as base,args.augmented_cnf.open('rb') as augmented:
        count = previous.check_streams(base,augmented,assignment,clauses,model['variables'],model['clauses'])
    adjacency = [row.copy() for row in model['known_adjacency']]
    for variable,(u,v) in mapping.items():
        adjacency[u-9][v-9] = adjacency[v-9][u-9] = int(assignment[variable])
    graph = support.window.graphcheck.embed59(adjacency)
    graph_check = support.window.validate_candidate(graph,star,True)
    for clause in clauses:
        need(any(bool(graph[mapping[abs(lit)][0]][mapping[abs(lit)][1]]) == (lit > 0) for lit in clause),'decoded graph violates box cut')
    graph_path = args.out/'independent_full59.json'
    with graph_path.open('x',encoding='utf-8') as stream:
        json.dump(dict(adjacency_full59=graph,scope=gate['scope'],ordered_box_cut_count=len(clauses),target_graph=False),stream,indent=2)
        stream.write('\n')
    for path in (__file__,previous.__file__,box.__file__,support.__file__,support.window.__file__,support.window.symbolic.__file__,support.window.graphcheck.__file__,ROOT/'uv.lock'):
        bindings[key(path)] = digest(path)
    need(all(digest(ROOT/name) == value for name,value in bindings.items()),'stable inputs')
    report = dict(status='INDEPENDENT_BOX_AUGMENTED_ROOK_WINDOW_SAT_PASS',
                  timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                  command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),inputs_sha256=bindings,
                  checker_path=key(__file__),checker_sha256=digest(__file__),
                  verifier='Independent checker authored by /root/eight_domain_audit; invocation provenance is the recorded command',
                  verification_type='Every exact raw augmented clause; ordered box certificate re-evaluation at maximizing corners; independently decoded full59graph',
                  base_cnf_sha256=digest(args.base_cnf),augmented_cnf_sha256=digest(args.augmented_cnf),model_sha256=digest(args.model),assignment_sha256=digest(args.assignment),
                  variables=model['variables'],base_clauses=model['clauses'],appended_clauses=len(clauses),checked_clauses=count,
                  ordered_cuts=cut_records,raw_graph_path=key(graph_path),raw_graph_sha256=digest(graph_path),graph_result=graph_check,
                  controls=stream_controls,producer_imported=False,shared_components=['Frozen independent support-cut SAT stream checker and controls','Independent raw59 and Boolean-box Gram checkers'],
                  statement='The saved complete assignment satisfies every clause of this exact base plus ordered independently checked Boolean-box target cuts and decodes to the saved valid local59window.',
                  limitations=['SAT only establishes this necessary local window, not a99vertex graph or target extension.',
                               'No UNSAT proof or target-family coverage follows from this SAT certificate.',
                               'Original support-cut checker is unchanged; box cuts use a distinct stricter checker gate.'],
                  target_resolution=False,external_review=False,artifact_availability='LOCAL_ONLY',elapsed_seconds=time.monotonic()-started)
    with (args.out/'summary.json').open('x',encoding='utf-8') as stream:
        json.dump(report,stream,indent=2)
        stream.write('\n')
    print(json.dumps(dict(status=report['status'],appended_clauses=len(clauses),sha256=digest(args.out/'summary.json'))))


if __name__ == '__main__':
    main()
