"""Independent base-plus-ordered-Gram-cuts SAT assignment and raw59 check."""
import argparse
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

import audit_20260930_gram_nogood_v1 as gram

ROOT = Path(__file__).resolve().parents[1]
need = gram.need
digest = gram.digest
key = gram.key


def check_streams(base,augmented,assignment,clauses,variables,base_count):
    need(base.readline().split() == [b'p',b'cnf',str(variables).encode(),str(base_count).encode()],'base header')
    need(augmented.readline().split() == [b'p',b'cnf',str(variables).encode(),str(base_count+len(clauses)).encode()],'augmented header')
    checked = 0
    def satisfied(line):
        values = list(map(int,line.split()))
        need(values and values[-1] == 0 and all(1 <= abs(lit) <= variables for lit in values[:-1]),'DIMACS row')
        need(any(assignment[abs(lit)] == (lit > 0) for lit in values[:-1]),'unsatisfied raw clause')
    for line in base:
        need(augmented.readline() == line,'augmented base body differs')
        satisfied(line)
        checked += 1
    need(checked == base_count,'base clause count')
    for clause in clauses:
        expected = (' '.join(map(str,clause))+' 0\n').encode('ascii')
        actual = augmented.readline()
        need(actual == expected,'ordered appended clause differs')
        satisfied(actual)
        checked += 1
    need(augmented.read() == b'','unexpected trailing augmented bytes')
    return checked


def controls():
    base = b'p cnf 2 2\n1 2 0\n-1 2 0\n'
    augmented = b'p cnf 2 3\n1 2 0\n-1 2 0\n1 0\n'
    need(check_streams(io.BytesIO(base),io.BytesIO(augmented),{1:True,2:True},[[1]],2,2) == 3,'positive stream fixture')
    rejected = []
    cases = [('wrong_assignment',augmented,{1:False,2:True},[[1]]),
             ('changed_base_clause',augmented.replace(b'1 2 0',b'1 -2 0',1),{1:True,2:True},[[1]]),
             ('wrong_appended_clause',augmented,{1:True,2:True},[[-1]]),
             ('missing_clause',augmented[:-4],{1:True,2:True},[[1]]),
             ('extra_clause',augmented+b'2 0\n',{1:True,2:True},[[1]]),
             ('wrong_header',augmented.replace(b'p cnf 2 3',b'p cnf 2 4'),{1:True,2:True},[[1]])]
    for name,raw,assignment,clauses in cases:
        try:
            check_streams(io.BytesIO(base),io.BytesIO(raw),assignment,clauses,2,2)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('corrupted stream fixture accepted: '+name)
    return dict(positive_base_plus_cut_passed=True,corruptions_rejected=rejected)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-cnf',type=Path,required=True)
    parser.add_argument('--augmented-cnf',type=Path,required=True)
    parser.add_argument('--model',type=Path,required=True)
    parser.add_argument('--assignment',type=Path,required=True)
    parser.add_argument('--ordered-cuts',type=Path,required=True)
    parser.add_argument('--encoding-audit',type=Path,required=True)
    parser.add_argument('--encoding-audit-sha256',required=True)
    parser.add_argument('--out',type=Path,required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=False)
    started = time.monotonic()
    bindings = {}
    def read(path):
        bindings[key(path)] = digest(path)
        return json.loads(Path(path).read_bytes())
    calibration = controls()
    need(digest(args.encoding_audit) == args.encoding_audit_sha256,'independent encoding audit pin')
    gate = read(args.encoding_audit)
    need(gate['status'] == 'INDEPENDENT_ROOK_FREE_INTERNAL_WINDOW_CNF_ENCODING_PASS','780edge gate status')
    authenticated = {str((Path(path) if Path(path).is_absolute() else ROOT/path).resolve()):value for path,value in gate['inputs_sha256'].items()}
    for path in (args.base_cnf,args.model):
        need(authenticated.get(str(path.resolve())) == digest(path),'audited exact base model/CNF')
        bindings[key(path)] = digest(path)
    model = read(args.model)
    mapping = gram.reconstruct_mapping(model)
    star = read(gram.STAR)
    ordered = read(args.ordered_cuts)
    need(type(ordered) is list,'ordered cuts must be a list')
    clauses = []
    cut_records = []
    for record in ordered:
        certificate_path = ROOT/record['certificate']
        audit_path = ROOT/record['audit']
        need(digest(certificate_path) == record['certificate_sha256'] and digest(audit_path) == record['audit_sha256'],'ordered cut artifact identities')
        certificate = read(certificate_path)
        audit = read(audit_path)
        need(audit['status'] == 'INDEPENDENT_TARGET_GRAM_NOGOOD_PASS' and audit['certificate_sha256'] == digest(certificate_path),'prior cut audit status and binding')
        need(audit['base_cnf_sha256'] == digest(args.base_cnf) and audit['encoding_model_sha256'] == digest(args.model)
             and certificate['base_cnf_sha256'] == digest(args.base_cnf) and certificate['encoding_model_sha256'] == digest(args.model),'cut family binding')
        # Recheck the mathematical artifact rather than trusting audit status.
        graph_paths = [ROOT/path for path,value in audit['inputs_sha256'].items() if value == certificate['graph_sha256']]
        need(graph_paths,'cut raw graph unavailable in audit bindings')
        graph_path = graph_paths[0]
        need(digest(graph_path) == certificate['graph_sha256'],'cut raw graph identity')
        raw = read(graph_path)['adjacency_full59']
        gram.window.validate_candidate(raw,star,True)
        checked = gram.audit_certificate(certificate,raw,mapping)
        need(checked['verified_clause'] == record['clause'] == audit['verified_clause'],'ordered validated clause identity')
        clauses.append(checked['verified_clause'])
        cut_records.append(dict(certificate=key(certificate_path),certificate_sha256=digest(certificate_path),
                                audit=key(audit_path),audit_sha256=digest(audit_path),
                                clause=checked['verified_clause'],quadratic_value=checked['quadratic_value'],
                                mathematical_artifact_rechecked=True))
    need(gram.product_basis((27,-9,1),(27,-9,1)) == (1701,-567,63),'universal exact PSD identity')
    signed = read(args.assignment)['assignment']
    need(all(type(lit) is int and lit != 0 for lit in signed),'signed complete assignment')
    assignment = {abs(lit):lit>0 for lit in signed}
    need(len(assignment) == len(signed) == model['variables'] and set(assignment) == set(range(1,model['variables']+1)),'unique complete variable population')
    bindings[key(args.augmented_cnf)] = digest(args.augmented_cnf)
    with args.base_cnf.open('rb') as base,args.augmented_cnf.open('rb') as augmented:
        count = check_streams(base,augmented,assignment,clauses,model['variables'],model['clauses'])
    adjacency = [row.copy() for row in model['known_adjacency']]
    for variable,(u,v) in mapping.items():
        adjacency[u-9][v-9] = adjacency[v-9][u-9] = int(assignment[variable])
    full59 = gram.window.graphcheck.embed59(adjacency)
    graph_result = gram.window.validate_candidate(full59,star,True)
    for clause in clauses:
        need(any(bool(full59[mapping[abs(lit)][0]][mapping[abs(lit)][1]]) == (lit>0) for lit in clause),'decoded graph violates ordered cut')
    graph_path = args.out/'independent_full59.json'
    with graph_path.open('x',encoding='utf-8') as stream:
        json.dump(dict(adjacency_full59=full59,scope=gate['scope'],ordered_cut_count=len(clauses),target_graph=False),stream,indent=2)
        stream.write('\n')
    for path in (__file__,gram.__file__,gram.window.__file__,gram.window.symbolic.__file__,gram.window.graphcheck.__file__,ROOT/'uv.lock'):
        bindings[key(path)] = digest(path)
    need(all(digest(ROOT/path) == value for path,value in bindings.items()),'input stability')
    report = dict(status='INDEPENDENT_AUGMENTED_ROOK_WINDOW_SAT_PASS',
                  timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                  command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),inputs_sha256=bindings,
                  checker_path=key(__file__),checker_sha256=digest(__file__),
                  verifier='Independent checker authored by /root/eight_domain_audit; invocation provenance is the recorded command',
                  verification_type='Every raw augmented clause, exact base-body and ordered-cut identity, independent replay of all cut quadratics, and decoded full59graph',
                  base_cnf_sha256=digest(args.base_cnf),augmented_cnf_sha256=digest(args.augmented_cnf),
                  model_sha256=digest(args.model),assignment_sha256=digest(args.assignment),
                  variables=model['variables'],base_clauses=model['clauses'],appended_clauses=len(clauses),checked_clauses=count,
                  ordered_cuts=cut_records,raw_graph_path=key(graph_path),raw_graph_sha256=digest(graph_path),
                  graph_result=graph_result,controls=calibration,producer_imported=False,
                  statement='The exact complete assignment satisfies every clause of the exact base CNF plus the listed independently replayed target-Gram cuts, and decodes to the saved valid59vertex local window. This does not establish a99vertex target extension.',
                  shared_components=['Python standard library','frozen independent Gram support-cut checker','independent raw59 graph validator'],
                  limitations=['The local window can still violate other target conditions.',
                               'Valid individual target cuts do not supply an unrestricted coverage argument.',
                               'This audit validates SAT objects only; augmented UNSAT needs separate complete proof replay and all cut premises.'],
                  target_resolution=False,external_review=False,artifact_availability='LOCAL_ONLY',elapsed_seconds=time.monotonic()-started)
    with (args.out/'summary.json').open('x',encoding='utf-8') as stream:
        json.dump(report,stream,indent=2)
        stream.write('\n')
    print(json.dumps(dict(status=report['status'],appended_clauses=len(clauses),sha256=digest(args.out/'summary.json'))))


if __name__ == '__main__':
    main()
