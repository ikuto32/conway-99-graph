"""Independent encoding audit with all four right-cell matchings free.

Reuses only the frozen independent symbolic-polynomial/clause checker. No
producer is imported, and neither fixed-star CNF nor its exclusion is used as
a premise for this broader780edge model.
"""
import argparse
from datetime import datetime, timezone
import gzip
from itertools import combinations
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

import audit_20260930_rook_window_cnf_v1 as symbolic
import audit_20260930_rook_window_graph_v1 as graphcheck

ROOT = Path(__file__).resolve().parents[1]
need = symbolic.need
digest = symbolic.digest


def fixed_and_unknown(star):
    # Retain only the central matching and four incidence blocks. The four
    # partner_matching records are deliberately not fixed graph constraints.
    fixed = {edge for edge in graphcheck.fixed_external(star) if edge[0] < 10}
    unknown = set(combinations(range(10,50),2))
    need(len(fixed) == 85 and len(unknown) == 780,'broader fixed/free universe')
    return fixed,unknown


def validate_candidate(matrix,star,complete=True):
    need(len(matrix) == 59 and all(len(row) == 59 and all(type(x) is int and x in (0,1) for x in row) for row in matrix),'binary59matrix')
    need(all(matrix[u][u] == 0 for u in range(59)) and all(matrix[u][v] == matrix[v][u] for u,v in combinations(range(59),2)),'simple59graph')
    sets = [{v for v,x in enumerate(row) if x} for row in matrix]
    need(all(len(row) <= 14 for row in sets),'known degrees')
    need(all(len(sets[u]&sets[v]) <= 2-matrix[u][v] for u,v in combinations(range(59),2)),'full59caps')
    for u,v in combinations(range(9),2):
        need(matrix[u][v] == int(u//3 == v//3 or u%3 == v%3),'rook core')
    for u in range(50):
        row,column = graphcheck.COORDINATES[u//10]
        owner = 3*row+column
        need(matrix[u+9][:9] == [int(v == owner) for v in range(9)],'owner-core attachments')
    fixed,unknown = fixed_and_unknown(star)
    for u,v in combinations(range(50),2):
        if (u,v) not in unknown:
            need(matrix[u+9][v+9] == int((u,v) in fixed),'frozen central graph/absences')
    if complete:
        for cell in range(1,5):
            for u in range(10*cell,10*cell+10):
                need(sum(matrix[u+9][v+9] for v in range(10*cell,10*cell+10)) == 1,'internal perfect matching degree')
        for ca,cb in combinations(range(1,5),2):
            target = 1 if any(a == b for a,b in zip(graphcheck.COORDINATES[ca],graphcheck.COORDINATES[cb])) else 2
            need(all(sum(matrix[u+9][v+9] for v in range(10*cb,10*cb+10)) == target for u in range(10*ca,10*ca+10)),'cross row degree')
            need(all(sum(matrix[u+9][v+9] for u in range(10*ca,10*ca+10)) == target for v in range(10*cb,10*cb+10)),'cross column degree')
    return dict(vertices=59,pair_caps_checked=1711,free_edges=780,complete_block_degrees_checked=complete,
                known_edges=sum(map(len,sets))//2,target_graph=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,required=True)
    parser.add_argument('--star',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args = parser.parse_args()
    need(not args.out.exists(),'preserve previous audit')
    tick = time.monotonic()
    bindings = {}
    def read(path):
        bindings[str(path)] = digest(path)
        return json.loads(Path(path).read_bytes())
    need(digest(args.star) == graphcheck.STAR_HASH,'frozen raw factor star')
    star = read(args.star)
    summary = read(args.run/'summary.json')
    manifest = read(args.run/'manifest.json')
    for path,expected in manifest['input_hashes'].items():
        need(digest(ROOT/path) == expected,'producer source binding')
        bindings[path] = expected
    for name,record in summary['outputs'].items():
        path = args.run/name
        need(digest(path) == record['sha256'] and path.stat().st_size == record['bytes'],'artifact binding')
        bindings[str(path)] = record['sha256']
    controls = symbolic.cardinal_controls()
    rook_model = read(args.run/'rook_control_model.json')
    payload = read(args.run/'rook_control_assignment.json')
    rook = [[int(u != v and (u//3 == v//3 or u%3 == v%3)) for v in range(9)] for u in range(9)]
    need(payload['adjacency'] == rook,'rook identity')
    def rook_degrees(ids):
        return [dict(variables=[ids[tuple(sorted((u,v)))] for v in range(9) if v != u],value=4,label=[u]) for u in range(9)]
    clauses,_,_ = symbolic.semantics(rook_model,[[0 if u == v else -1 for v in range(9)] for u in range(9)],[[0]*9 for _ in range(9)],rook_degrees)
    symbolic.check_dimacs(args.run/'rook_control.cnf',clauses,rook_model['variables'])
    positive,failed = symbolic.evaluate_graph(rook_model,clauses,rook)
    need(failed == 0 and positive == {int(k):v for k,v in payload['assignment'].items()},'positive rook assignment')
    damaged = [row.copy() for row in rook]
    damaged[0][1] ^= 1
    damaged[1][0] ^= 1
    _,failed = symbolic.evaluate_graph(rook_model,clauses,damaged)
    need(failed > 0,'damaged rook accepted')
    auxiliary = rook_model['products'][0]['id']
    positive[auxiliary] = not positive[auxiliary]
    need(not symbolic.truth(clauses,positive),'wrong AND value accepted')
    controls.update(rook_positive=False if failed == 0 else 'PASS',corrupted_rook_false_clauses=failed,wrong_AND_value_rejected=True)
    base = [[0]*50 for _ in range(50)]
    for u,v in graphcheck.fixed_external(star):
        base[u][v] = base[v][u] = 1
    full59 = graphcheck.embed59(base)
    controls['partial59'] = validate_candidate(full59,star,False)
    corruptions = []
    for name in ('loop','wrong_attachment','central_edge_deleted','false_complete_degree_claim'):
        bad = [row.copy() for row in full59]
        if name == 'loop':
            bad[0][0] = 1
        elif name == 'wrong_attachment':
            bad[9][1] = bad[1][9] = 1
        elif name == 'central_edge_deleted':
            bad[9][10] = bad[10][9] = 0
        try:
            validate_candidate(bad,star,name == 'false_complete_degree_claim')
        except ValueError:
            corruptions.append(name)
        else:
            raise ValueError('bad raw59 fixture accepted')
    controls['partial59_corruptions_rejected'] = corruptions
    controls['partial59_scope'] = 'Known-valid fixed partial graph only; no completed780edge local solution asserted.'
    fixed,unknown = fixed_and_unknown(star)
    known = [[0]*50 for _ in range(50)]
    for u,v in fixed:
        known[u][v] = known[v][u] = 1
    for u,v in unknown:
        known[u][v] = known[v][u] = -1
    shared = [[int(u != v and u//10 == v//10) for v in range(50)] for u in range(50)]
    def degrees(ids):
        rows = []
        for cell in range(1,5):
            for u in range(10*cell,10*cell+10):
                rows.append(dict(variables=[ids[tuple(sorted((u,v)))] for v in range(10*cell,10*cell+10) if v != u],value=1,label=[cell,'internal',u]))
        for ca,cb in combinations(range(1,5),2):
            target = 1 if any(a == b for a,b in zip(graphcheck.COORDINATES[ca],graphcheck.COORDINATES[cb])) else 2
            for u in range(10*ca,10*ca+10):
                rows.append(dict(variables=[ids[(u,v)] for v in range(10*cb,10*cb+10)],value=target,label=[ca,cb,'row',u]))
            for v in range(10*cb,10*cb+10):
                rows.append(dict(variables=[ids[(u,v)] for u in range(10*ca,10*ca+10)],value=target,label=[ca,cb,'column',v]))
        return rows
    model = read(args.run/'model.json')
    need(model['right_internal_matchings_free'] is True and model['cell_rook_coordinates'] == list(map(list,graphcheck.COORDINATES)),'broader model declaration')
    clauses,edge_ids,products = symbolic.semantics(model,known,shared,degrees)
    checked = symbolic.check_dimacs(args.run/'instance.cnf',clauses,model['variables'])
    for name in ('instance.cnf','model.json'):
        with gzip.open(args.run/(name+'.gz'),'rb') as stream:
            decoded = stream.read()
        need(decoded == (args.run/name).read_bytes(),'lossless publication bytes')
    for path in (__file__,symbolic.__file__,graphcheck.__file__,ROOT/'uv.lock'):
        bindings[str(path)] = digest(path)
    need(all(digest(Path(path) if Path(path).is_absolute() else ROOT/path) == value for path,value in bindings.items()),'input stability')
    report = dict(status='INDEPENDENT_ROOK_FREE_INTERNAL_WINDOW_CNF_ENCODING_PASS',
                  claim_id='C-ROOK-FOUR-FACTOR-WINDOW-CNF-ENCODING',claim_revision=1,recommendation='VERIFIED',
                  statement='The exact saved CNF is satisfiable if and only if the780arbitrary labelled right-cell edges complete the frozen central matching and four incidence blocks to the prescribed59vertex window, with arbitrary right internal perfect matchings, four cross perfect matchings, two cross2regular blocks, and all known common-neighbor upper caps.',
                  timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                  command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),inputs_sha256=bindings,
                  variables=model['variables'],edge_variables=len(edge_ids),product_variables=len(products),clauses=checked,
                  internal_degree_rows=40,cross_degree_rows=120,external_pair_constraints=1225,embedded_pair_count=1711,
                  controls=controls,producer_imported=False,solver_launched=False,
                  scope='Only central10vertex matching and four exact incidence blocks fixed. All780pairs among the40right vertices independently variable, constrained by their stated labelled block degrees; no nontrivial automorphism assumed.',
                  derivation='Independent polynomial reconstruction accounts for every external length-two path and its core-neighbor constant, with exact bidirectional AND clauses. All780edges and every block-degree equation are covered with no identifications. Core-core upper caps hold in rook9. Core-external caps follow from owner attachment, internal degree1 and cross degree1or2 exactly as required by whether owner cells are rook-adjacent; missing-cell cores contribute at most1. Thus all59pair caps are equivalent to the encoded external caps and degrees within the fixed family.',
                  verifier='/root/eight_domain_audit independent checking agent',verification_type='Independent symbolic encoding and full clause-multiset check',
                  shared_components=['Python standard library','frozen independent symbolic CNF checker','independent rook-core embedding helpers'],
                  limitations=['No solver conclusion or exclusion supplied by encoding audit.',
                               'Still freezes one labelled central factor star; no universal rook coverage or unrestricted target result.',
                               'The earlier600edge exclusion is not a premise for this broader encoding.'],
                  elapsed_seconds=time.monotonic()-tick,target_resolution=False,external_review=False,artifact_availability='LOCAL_ONLY')
    args.out.parent.mkdir(parents=True,exist_ok=True)
    with args.out.open('x',encoding='utf-8') as stream:
        json.dump(report,stream,indent=2)
        stream.write('\n')
    print(json.dumps(dict(status=report['status'],clauses=checked,sha256=digest(args.out))))


if __name__ == '__main__':
    main()
