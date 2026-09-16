"""Stdlib-only RUP audit of the extracted fixed-lift UNSAT core.

No SAT solver, cardinality encoder, or DRAT checker is imported. This
checks proof validity relative to the hash-bound emitted CNF, including
that every core input clause occurs in that CNF. The mathematical mapping
of constraints to CNF remains a separately reviewed encoder obligation.
"""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import time


HERE = Path(__file__).resolve().parent


def read_cnf(path):
    raw = path.read_bytes()
    lines = [line for line in raw.decode('ascii').splitlines() if line and not line.startswith('c')]
    tag, kind, variables, expected = lines.pop(0).split()
    assert tag == 'p' and kind == 'cnf'
    variables, expected = int(variables), int(expected)
    clauses = []
    for line in lines:
        values = list(map(int, line.split()))
        assert values[-1] == 0 and all(0 < abs(x) <= variables for x in values[:-1])
        clauses.append(tuple(values[:-1]))
    assert len(clauses) == expected
    return variables, clauses


def addition_only(source, target, variables):
    additions = []
    deletions = 0
    for line in source.read_text(encoding='ascii').splitlines():
        if not line.strip():
            continue
        tokens = line.split()
        deletion = tokens[0] == 'd'
        if deletion:
            tokens = tokens[1:]
        values = list(map(int, tokens))
        assert values[-1] == 0 and all(0 < abs(x) <= variables for x in values[:-1])
        if deletion:
            deletions += 1
        else:
            additions.append(tuple(values[:-1]))
    assert additions[-1] == ()
    target.write_bytes(''.join(' '.join(map(str, clause)) + ' 0\n' for clause in additions).encode('ascii'))
    return additions, deletions


def is_rup(clauses, proposed):
    true_literals = set(-literal for literal in proposed)
    if any(-literal in true_literals for literal in true_literals):
        return True, 0
    propagated = 0
    while True:
        changed = False
        for clause in clauses:
            if any(literal in true_literals for literal in clause):
                continue
            unresolved = [literal for literal in clause if -literal not in true_literals]
            if not unresolved:
                return True, propagated
            if len(unresolved) == 1:
                true_literals.add(unresolved[0])
                propagated += 1
                changed = True
        if not changed:
            return False, propagated


def main():
    started = time.monotonic()
    full = HERE / 'scratch_resume_overlap_review.cnf'
    core = HERE / 'scratch_resume_overlap_review_core.cnf'
    raw_proof = HERE / 'scratch_resume_overlap_review.drat'
    core_proof = HERE / 'scratch_resume_overlap_review_core.drat'
    variables, full_clauses = read_cnf(full)
    core_variables, core_clauses = read_cnf(core)
    assert core_variables == variables
    full_multiset = Counter(tuple(sorted(c)) for c in full_clauses)
    core_multiset = Counter(tuple(sorted(c)) for c in core_clauses)
    assert not (core_multiset - full_multiset)
    full_rup = HERE / 'scratch_resume_overlap_review_additions.drat'
    core_rup = HERE / 'scratch_resume_overlap_review_core_additions.drat'
    full_additions, full_deletions = addition_only(raw_proof, full_rup, variables)
    additions, core_deletions = addition_only(core_proof, core_rup, variables)
    accepted = list(core_clauses)
    counts = []
    for index, clause in enumerate(additions):
        valid, propagated = is_rup(accepted, clause)
        assert valid, (index, clause)
        accepted.append(clause)
        counts.append(propagated)
    assert accepted[-1] == ()
    result = {
        'status': 'STDLIB_RUP_FIXED_OVERLAP_CORE_VERIFIED',
        'variables': variables, 'full_input_clauses': len(full_clauses),
        'core_input_clauses': len(core_clauses), 'checked_core_RUP_additions': len(additions),
        'core_is_multiset_subset_of_full_CNF': True,
        'all_proof_literals_within_declared_range': True,
        'full_proof_additions': len(full_additions), 'full_proof_deletions_removed': full_deletions,
        'core_proof_deletions_removed': core_deletions,
        'unit_propagations': sum(counts),
        'sha256': {path.name: sha256(path.read_bytes()).hexdigest()
                   for path in (full, core, raw_proof, core_proof, full_rup, core_rup, Path(__file__))},
        'elapsed_seconds': time.monotonic()-started,
        'scope': 'UNSAT proof for the emitted linear relaxation of one fixed overlap lift/C. Graph-to-CNF semantics require encoder review. No global E0 exclusion.'}
    (HERE / 'scratch_resume_overlap_review_rup.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
