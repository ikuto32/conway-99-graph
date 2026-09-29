"""Independently bind and replay a finite ordered collection of Boolean-box cuts."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import subprocess
import sys

import audit_20260930_gram_box_nogood_v1 as box

ROOT,need,digest,key = box.ROOT,box.need,box.digest,box.key


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ordered-cuts',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--claim-id')
    args = parser.parse_args()
    need(not args.out.exists(),'refuse overwrite')
    bindings = {}
    def bind(path,expected=None):
        name = key(path)
        if name not in bindings:
            bindings[name] = digest(path)
        need(expected is None or bindings[name] == expected,'artifact identity: '+name)
        return bindings[name]
    def read(path,expected=None):
        bind(path,expected)
        return json.loads(Path(path).read_bytes())
    base = ROOT/'acceleration/results/20260930_rook_free_internal_sat/instance.cnf'
    model_path = ROOT/'acceleration/results/20260930_rook_free_internal_sat/model.json'
    gate_path = ROOT/'acceleration/results/20260930_rook_free_internal_sat/independent_cnf_encoding.json'
    gate = read(gate_path,'a74e821f70680187e0ee14fb956d51928e6aa9517acc1bc0186448b32c985ba0')
    authenticated = {key(ROOT/name):value for name,value in gate['inputs_sha256'].items()}
    for p in (base,model_path): bind(p,authenticated[key(p)])
    model = read(model_path)
    mapping = box.support.reconstruct_mapping(model)
    star = read(box.support.STAR)
    collection = read(args.ordered_cuts)
    ordered = collection if type(collection) is list else collection['ordered_cuts']
    need(type(ordered) is list and ordered,'nonempty exact ordered cut collection')
    need(len({tuple(sorted(row['clause'])) for row in ordered}) == len(ordered),'distinct clauses')
    results = []
    for index,record in enumerate(ordered):
        cert_path,audit_path = ROOT/record['certificate'],ROOT/record['audit']
        cert = read(cert_path,record['certificate_sha256'])
        audit = read(audit_path,record['audit_sha256'])
        need(audit['status'] == 'INDEPENDENT_TARGET_GRAM_BOX_NOGOOD_PASS','independent exact box gate')
        for name,expected in audit['inputs_sha256'].items(): bind(ROOT/name,expected)
        need(audit['checker_sha256'] == bind(box.__file__),'frozen independently authored checker')
        need(audit['certificate_sha256'] == bind(cert_path) and audit['base_cnf_sha256'] == bind(base)
             and audit['encoding_model_sha256'] == bind(model_path),'audit family identity')
        need(cert['base_cnf_sha256'] == bind(base) and cert['encoding_model_sha256'] == bind(model_path),'certificate family identity')
        graph_paths = [ROOT/name for name,value in audit['inputs_sha256'].items() if value == cert['graph_sha256']]
        need(len(graph_paths) == 1,'unique raw graph identity')
        graph = read(graph_paths[0],cert['graph_sha256'])['adjacency_full59']
        box.support.window.validate_candidate(graph,star,True)
        for u in range(50):
            for v in range(u+1,50):
                if model['known_adjacency'][u][v] != -1:
                    need(graph[u+9][v+9] == model['known_adjacency'][u][v],'fixed graph/model bytes')
        calibration,checked = box.controls(cert,graph,mapping)
        need(record['clause'] == audit['verified_clause'] == checked['verified_clause'],'exact ordered clause binding')
        need(checked['global_boolean_box_upper_bound'] == audit['global_boolean_box_upper_bound'],'exact bound binding')
        parent_path = ROOT/cert['parent_certificate']
        parent = read(parent_path,cert['parent_certificate_sha256'])
        parent_checked = box.support.audit_certificate(parent,graph,mapping)
        need(cert['integer_negative_vector'] == parent['integer_negative_vector'],'same recorded parent vector')
        need(set(checked['verified_clause']) <= set(parent_checked['verified_clause']),'literal-subset strengthening')
        results.append(dict(index=index,certificate=key(cert_path),certificate_sha256=bind(cert_path),audit=key(audit_path),audit_sha256=bind(audit_path),
                            graph=key(graph_paths[0]),graph_sha256=bind(graph_paths[0]),clause=checked['verified_clause'],
                            parent_clause_length=checked['parent_clause_length'],clause_length=checked['clause_length'],
                            global_boolean_box_upper_bound=checked['global_boolean_box_upper_bound'],
                            fixed_nonzero_variables=checked['fixed_nonzero_variables'],freed_nonzero_variables=checked['freed_nonzero_variables'],
                            zero_coefficient_variables=checked['zero_coefficient_variables'],controls=calibration,
                            raw_graph_and_maximizing_corner_replayed=True))
    for p in (Path(__file__),box.__file__,box.support.__file__,ROOT/'uv.lock'):
        bind(p)
    need(all(digest(ROOT/name) == value for name,value in bindings.items()),'stable exact inputs')
    report = dict(status='INDEPENDENT_TARGET_GRAM_BOX_COLLECTION_PASS',claim_id=args.claim_id,claim_revision=1 if args.claim_id else None,
                  claim_id_null_reason=None if args.claim_id else 'Registrar must supply a precisely scoped collection claim',
                  timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                  command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),
                  verifier='/root/eight_domain_audit independent checking agent',verification_type='Every raw cut and maximizing corner independently replayed; exact ordered collection and source/audit hashes bound',
                  statement='Every listed clause in this finite frozen ordered collection is necessary for any target extension preserving this exact frozen central-factor scaffold. Each clause individually has a checked strictly negative exact Boolean-box Gram maximum.',
                  scope='The exact listed clauses only, in the single780edge family. The conjunction follows from their individual necessity; excluded populations are not summed.',
                  inputs_sha256=bindings,ordered_cuts_sha256=digest(args.ordered_cuts),ordered_cuts=ordered,
                  distinct_certificates=len({row['certificate_sha256'] for row in results}),distinct_clauses=len(results),independently_replayed_outcomes=len(results),results=results,
                  dependencies=[dict(id='C-TARGET-GRAM-BOOLEAN-BOX-NOGOODS',revision=1,relation='uses_result'),
                                dict(id='C-ROOK-FOUR-FACTOR-WINDOW-CNF-ENCODING',revision=1,relation='encoding_equivalence')],
                  producer_imported=False,shared_components=['Frozen independent box/support Gram checkers and raw59 validator','Python exact integer arithmetic'],
                  limitations=['No unrestricted or complete fixed-family exclusion; a solver is not run by this checker.',
                               'No disjointness, union size, graph coverage, or global minimality of clauses is claimed.',
                               'Collection evidence alone does not establish a future augmented SAT/UNSAT result.'],
                  recommendation='VERIFIED',target_resolution=False,external_review=False,artifact_availability='LOCAL_ONLY')
    args.out.parent.mkdir(parents=True,exist_ok=True)
    with args.out.open('x',encoding='utf-8') as stream:
        json.dump(report,stream,indent=2)
        stream.write('\n')
    print(json.dumps(dict(status=report['status'],distinct_clauses=len(results),sha256=digest(args.out))))


if __name__ == '__main__':
    main()
