"""Tiny-formula proof acceptance/rejection and bounded-worker controls only."""
import argparse
from itertools import combinations
import json
from pathlib import Path

from run_fixed_overlap_drat import produce_bounded
from audit_fixed_overlap_drat import check_drat, require, digest, key, ROOT, CHECKER, SOURCE


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    inputs = {key(p): digest(p) for p in (Path(__file__), ROOT/'acceleration/run_fixed_overlap_drat.py',
              ROOT/'acceleration/audit_fixed_overlap_drat.py', ROOT/'acceleration/run_fixed_overlap_sat.py',
              ROOT/'.deps/pysat/solvers.py', ROOT/'.deps/pysat/formula.py', CHECKER, SOURCE)}
    binaries = list((ROOT/'.deps').glob('pysolvers*.pyd'))
    require(len(binaries) == 1, 'Native solver module ambiguous')
    inputs[key(binaries[0])] = digest(binaries[0])
    def write(name, data):
        p = args.out/name
        with p.open('x', encoding='ascii', newline='\n') as stream:
            stream.write(data)
        return p
    unsat = write('tiny_unsat.cnf', 'p cnf 2 4\n1 2 0\n1 -2 0\n-1 2 0\n-1 -2 0\n')
    sat = write('tiny_sat.cnf', 'p cnf 2 1\n1 2 0\n')
    proof = args.out/'tiny.drat'
    production = produce_bounded(unsat, proof, 100, 10)
    require(production['solver_result'] == 'UNSAT_PROOF_UNCHECKED' and proof.exists(), 'Tiny UNSAT proof was not produced')
    positive = check_drat(unsat, proof, 10)
    require(positive['verified'], 'Genuine tiny DRAT proof rejected')
    controls = [dict(name='genuine_unsat', production=production, check=positive)]
    for name, formula, text in [('truncated_empty', unsat, ''), ('corrupted_empty_clause', unsat, '0\n'),
                                ('corrupted_fresh_unit', unsat, '3 0\n0\n'), ('wrong_sat_formula', sat, proof.read_text())]:
        wrong = write(name+'.drat', text)
        result = check_drat(formula, wrong, 10)
        require(not result['verified'], 'Invalid proof accepted: '+name)
        controls.append(dict(name=name, expected='NOT_VERIFIED', check=result))
    tiny_sat = produce_bounded(sat, args.out/'sat_must_not_produce.drat', 100, 10)
    require(tiny_sat['solver_result'] == 'SAT_MODEL_UNVALIDATED' and not (args.out/'sat_must_not_produce.drat').exists(),
            'SAT outcome was misclassified or published')
    controls.append(dict(name='sat_remains_unvalidated', production=tiny_sat))
    deadline = produce_bounded(unsat, args.out/'deadline.drat', 100, 1e-9)
    require(deadline['solver_result'] == 'UNKNOWN', 'Deadline credited a conclusion')
    controls.append(dict(name='wall_cap_unknown', production=deadline))
    # Pigeonhole6 into5 gives a tiny conflict-limited search without root units.
    clauses = [[p*5+h+1 for h in range(5)] for p in range(6)]
    clauses += [[-(p*5+h+1), -(q*5+h+1)] for h in range(5) for p,q in combinations(range(6), 2)]
    php = write('pigeonhole.cnf', f'p cnf 30 {len(clauses)}\n'+''.join(' '.join(map(str,c))+' 0\n' for c in clauses))
    capped = produce_bounded(php, args.out/'conflict_cap.drat', 1, 10)
    require(capped['solver_result'] == 'UNKNOWN', 'Conflict cap did not exercise unknown branch')
    controls.append(dict(name='conflict_cap_unknown', production=capped))
    checker_cap = check_drat(unsat, proof, 1e-9)
    require(checker_cap['status'] == 'UNKNOWN' and not checker_cap['verified'], 'Checker timeout became verified')
    controls.append(dict(name='checker_cap_unknown', check=checker_cap))
    require(all(digest(p) == h for p,h in inputs.items()), 'QA source/dependency changed')
    outputs = {key(p): digest(p) for p in sorted(args.out.iterdir()) if p.is_file()}
    report = dict(status='FIXED_OVERLAP_DRAT_TINY_PROOF_AND_CAP_CONTROLS_PASS', inputs_sha256=inputs,
                  outputs_sha256=outputs, controls=controls, research_CNF_solves=0,
                  unverified_results_exclude_nothing=True, graph_witness_created=False,
                  scope='Tiny formulas test proof generation/checking and caps; no actual fixed-K conclusion in this report.')
    with (args.out/'report.json').open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(report, indent=2, allow_nan=False)+'\n')
    print(json.dumps({'status':report['status'], 'controls':len(controls)}), flush=True)


if __name__ == '__main__':
    main()
