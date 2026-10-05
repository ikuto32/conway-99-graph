"""Independent SAT-object or fresh-checker DRAT validation of780edge window."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

import audit_20260930_rook_free_internal_cnf_v1 as local
import audit_20260930_rook_unsat_replay_v1 as proof_helpers

ROOT = Path(__file__).resolve().parents[1]
ENCODING = ROOT/'acceleration/results/20260930_rook_free_internal_sat'
GATE = ENCODING/'independent_cnf_encoding.json'
GATE_HASH = 'a74e821f70680187e0ee14fb956d51928e6aa9517acc1bc0186448b32c985ba0'
STAR = ROOT/'acceleration/results/20260930_rook_cell_factors/local_witness.json'
BUILD = ROOT/'build/rook-drat-checker'
BUILD_PIN = '219e14aeb9efb7df5629cb45405b08d45b2613133207e92bd4f7c09a5b2211b7'
need = local.need
digest = proof_helpers.digest
save = proof_helpers.save
key = proof_helpers.key


def check_all_clauses(path,assignment,expected_variables,expected_clauses):
    count = 0
    with Path(path).open('r',encoding='ascii') as stream:
        need(stream.readline().split() == ['p','cnf',str(expected_variables),str(expected_clauses)],'exact CNF header')
        for line in stream:
            values = list(map(int,line.split()))
            need(values and values[-1] == 0,'clause terminator')
            need(all(1 <= abs(lit) <= expected_variables for lit in values[:-1]),'literal bounds')
            need(any(assignment[abs(lit)] == (lit>0) for lit in values[:-1]),'false raw CNF clause')
            count += 1
    need(count == expected_clauses,'all raw clauses present')
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--solver-run',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=False)
    tick = time.monotonic()
    bindings = {}
    def read(path):
        bindings[key(path)] = digest(path)
        return json.loads(Path(path).read_bytes())
    need(digest(GATE) == GATE_HASH,'broader independent encoding gate identity')
    gate = read(GATE)
    need(gate['status'] == 'INDEPENDENT_ROOK_FREE_INTERNAL_WINDOW_CNF_ENCODING_PASS','broader gate status')
    solver = read(args.solver_run/'manifest.json')
    receipt = read(args.solver_run/'main/receipt.json')
    cnf = ENCODING/'instance.cnf'
    need(digest(cnf) == receipt['cnf_sha256'],'CNF identity')
    bindings[key(cnf)] = digest(cnf)
    need((receipt['variables'],receipt['clauses']) == (30420,3689820),'instance dimensions')
    for source,expected in solver['input_hashes'].items():
        path = Path(source) if Path(source).is_absolute() else ROOT/source
        need(digest(path) == expected,'solver input binding')
        bindings[key(path)] = expected
    native = Path(solver['native_module_path'])
    need(digest(native) == solver['native_module_sha256'],'native solver extension identity')
    bindings[key(native)] = digest(native)
    manifest = dict(timestamp=datetime.now(timezone.utc).isoformat(),
                    source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                    command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),
                    inputs_sha256=dict(bindings),scope=gate['scope'],
                    question='Does the saved solver conclusion have an independent raw object/proof certificate for the exact780edge model?',
                    declared_solver_answer=receipt['solver_answer'],
                    criteria='SAT: every CNF clause plus independently decoded full59graph. UNSAT: fresh source-authenticated DRAT replay with positive and invalid-proof controls.',
                    checker_seconds_per_call=60,target_resolution=False)
    save(args.out/'manifest.json',manifest)
    records = []
    conclusion = None
    claim_id = None
    statement = None
    if receipt['solver_answer'] == 'SAT_MODEL_UNCHECKED':
        model = read(ENCODING/'model.json')
        literals = read(args.solver_run/'main/model.json')['assignment']
        need(all(type(lit) is int and lit != 0 for lit in literals),'signed assignment literals')
        assignment = {abs(lit):lit>0 for lit in literals}
        need(len(assignment) == len(literals) == model['variables'] and set(assignment) == set(range(1,model['variables']+1)), 'complete unique assignment')
        count = check_all_clauses(cnf,assignment,model['variables'],model['clauses'])
        graph = [row.copy() for row in model['known_adjacency']]
        for entry in model['edge_variables']:
            u,v = entry['u'],entry['v']
            graph[u][v] = graph[v][u] = int(assignment[entry['id']])
        producer = read(args.solver_run/'main/decoded_local_adjacency.json')
        need(producer['adjacency'] == graph,'independent decoding equality')
        star = read(STAR)
        full59 = local.graphcheck.embed59(graph)
        checked = local.validate_candidate(full59,star,True)
        save(args.out/'independent_full59.json',dict(adjacency_full59=full59,scope=gate['scope'],target_graph=False))
        # Falsify the direct object validator with a loop and deleted center edge.
        rejected = []
        for kind in ('loop','central_edge_deleted'):
            bad = [row.copy() for row in full59]
            if kind == 'loop':
                bad[0][0] = 1
            else:
                bad[9][10] = bad[10][9] = 0
            try:
                local.validate_candidate(bad,star,True)
            except ValueError:
                rejected.append(kind)
            else:
                raise ValueError('corrupt SAT graph accepted')
        records.append(dict(method='all raw CNF clauses and full59 graph',clauses_checked=count,graph=checked,corruptions_rejected=rejected))
        conclusion = 'INDEPENDENT_ROOK_FREE_INTERNAL_LOCAL_SAT_PASS'
        claim_id = 'C-ROOK-FOUR-FACTOR-WINDOW-LOCAL-CONSTRUCTION'
        statement = 'A complete59vertex local window satisfying the exact780edge frozen-central-factor constraints exists; the saved raw59adjacency is a witness. This is not a99vertex target graph.'
    elif receipt['solver_answer'] == 'UNSAT_PROOF_UNCHECKED':
        need(digest(BUILD/'build_manifest.json') == BUILD_PIN,'fresh checker build provenance')
        build = read(BUILD/'build_manifest.json')
        build_receipt = read(BUILD/'build_receipt.json')
        checker = BUILD/'drat-trim.exe'
        need(build['upstream_commit'] == proof_helpers.PIN and build_receipt['exit_code'] == 0
             and digest(checker) == build_receipt['binary_sha256'],'fresh checker binary')
        for name in ('drat-trim.exe','drat-trim.c','windows-portability.patch','upstream-drat-trim.c'):
            bindings[key(BUILD/name)] = digest(BUILD/name)
        need(receipt['proof_stream_finalized'] and receipt['synthesized_empty_clause'] is False,'complete preserved proof stream')
        proof = args.solver_run/'main/proof.drat'
        need(digest(proof) == receipt['proof_sha256'],'raw proof identity')
        bindings[key(proof)] = digest(proof)
        invalid = args.out/'invalid_empty_only.drat'
        invalid.write_bytes(b'0\n')
        def replay(name,instance,trace,expected):
            command = [str(checker),str(instance.resolve()),str(trace.resolve())]
            started = time.monotonic()
            run = subprocess.run(command,cwd=ROOT,capture_output=True,timeout=60)
            log = args.out/(name+'.log')
            log.write_bytes(run.stdout+run.stderr)
            accepted = run.returncode == 0 and b's VERIFIED' in (run.stdout+run.stderr).splitlines()
            record = dict(name=name,command=command,working_directory=str(ROOT),exit_code=run.returncode,
                          accepted=accepted,expected=expected,cnf_sha256=digest(instance),proof_sha256=digest(trace),
                          log_path=key(log),log_sha256=digest(log),elapsed_seconds=time.monotonic()-started)
            save(args.out/(name+'.json'),record)
            need(accepted == expected,'DRAT result mismatch: '+name)
            records.append(record)
        sat = args.solver_run/'control_sat/instance.cnf'
        unsat = args.solver_run/'control_unsat/instance.cnf'
        tiny = args.solver_run/'control_unsat/proof.drat'
        need(proof_helpers.parse_small(sat) and not proof_helpers.parse_small(unsat),'small independent truth-table controls')
        for path in (sat,unsat,tiny):
            bindings[key(path)] = digest(path)
        replay('positive_small',unsat,tiny,True)
        replay('negative_small',unsat,invalid,False)
        replay('negative_sat',sat,invalid,False)
        replay('negative_main',cnf,invalid,False)
        replay('complete_main',cnf,proof,True)
        with proof.open('rb') as stream:
            need(sum(1 for _ in stream) == receipt['proof_lines'],'full proof line count')
        conclusion = 'INDEPENDENT_ROOK_FREE_INTERNAL_WINDOW_UNSAT_PASS'
        claim_id = 'C-ROOK-FOUR-FACTOR-WINDOW-EXCLUSION'
        statement = 'No assignment of the780arbitrary labelled right-cell edges, including arbitrary internal right-cell perfect matchings, extends the exact frozen central matching and four incidence blocks to the required local59vertex window. Therefore no target in this fixed-central-factor family exists.'
    else:
        raise ValueError('no completed SAT or UNSAT artifact to verify: '+receipt['solver_answer'])
    for path in (__file__,local.__file__,local.symbolic.__file__,local.graphcheck.__file__,proof_helpers.__file__,ROOT/'uv.lock'):
        bindings[key(path)] = digest(path)
    need(all(digest(ROOT/path) == value for path,value in bindings.items()),'input stability')
    result = dict(status=conclusion,claim_id=claim_id,claim_revision=1,recommendation='VERIFIED',statement=statement,
                  timestamp=datetime.now(timezone.utc).isoformat(),source_commit=manifest['source_commit'],command=manifest['command'],
                  working_directory=str(Path.cwd()),python=platform.python_version(),inputs_sha256=bindings,
                  scope=gate['scope'],variables=30420,edge_variables=780,clauses=3689820,records=records,
                  verifier='/root/eight_domain_audit independent checking agent',
                  verification_type='Raw SAT object or independent fresh-checker DRAT validation combined with separately checked exact encoding',
                  solver_engine=receipt['engine'],pysat_version=solver['pysat_version'],solver_native_sha256=solver['native_module_sha256'],
                  checker_provenance_manifest=key(BUILD/'build_manifest.json'),checker_provenance_manifest_sha256=BUILD_PIN,
                  checker_upstream_commit=proof_helpers.PIN,source_authenticated_checker_binary_sha256=digest(BUILD/'drat-trim.exe'),
                  dependencies=[dict(id='C-ROOK-FOUR-FACTOR-WINDOW-CNF-ENCODING',revision=1,relation='encoding_equivalence'),
                                dict(id='C-ROOK-NINE-REGULAR-SET-ENCODING',revision=1,relation='normalization')],
                  producer_imported=False,shared_components=['Python standard library','frozen independent graph and proof artifact helpers','source-authenticated DRAT checker'],
                  limitations=['One exact labelled central factor star only; no universal rook containment or unrestricted conclusion.',
                               'Windows portability shim, compiler, runtime, and proof checker remain trusted components.',
                               'No peer review or external review asserted.'],
                  artifact_availability='LOCAL_ONLY',elapsed_seconds=time.monotonic()-tick,target_resolution=False,external_review=False)
    save(args.out/'summary.json',result)
    print(json.dumps(dict(status=conclusion,sha256=digest(args.out/'summary.json'))))


if __name__ == '__main__':
    main()
