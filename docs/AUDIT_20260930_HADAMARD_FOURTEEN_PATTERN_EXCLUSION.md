# Independent exclusion with fourteen fixed parity patterns

Producer `/root`; verifier `/root/structural_attack`. No discovery source is
imported. The checker reuses its own previously frozen independent raw-core
derivation and reverse-column rank helper, disclosing that reuse. This document
is the mathematical review; the separate exact run report records PASS or veto.
Audit allocation is sixty seconds, with no solver or SAT-clause application.

The claimed scope is deliberately larger than the earlier single branch.
Only groups0,3,4,6,7,8,9,10,11,12,13,14,15,16 have their normalized parity
patterns fixed to the literal saved values. Groups1,2,5,17,18,19 may take any
allowed constant or mixed normalized pattern. No full20pattern premise is used.
The fixed support, prescribed factor Gram and additional coordinatewise balance
within the three identical-support columns remain assumptions. D is unencoded.

Apply the independently verified general affine-phase necessity theorem. Each
group admits its own first-coordinate identity gauge regardless of its parity;
all twenty gauge equations are unconditional. A mixed local sum is available
only if its group's full pattern is retained. A pair-sign sum is used only if
every one of its five incident groups is retained, even those absent from its
visible nonzero coefficients. Its sign membership and relative-intercept
coefficients are then unchanged under every choice of the six free patterns.

The certificate expresses the first required local same-sign phase difference
in group0 as an exact GF(3) combination of these available homogeneous rows.
Group0 remains fixed and mixed, so that functional must be nonzero. Every used
row is valid for any hypothetical factor matching the fourteen patterns,
regardless of the other six. Their combination forces the functional to zero,
a contradiction. This proves the broader conditional exclusion directly; the
previous twenty-pattern exclusion is not invoked as a premise.

The checker rebuilds the literal core Gram, group ordering and original rows
from raw support/projection. It independently computes each row's full parity
dependency set and checks the exact180coefficient row combination. The dependency
union including the violated functional is exactly the fourteen retained groups.
This logical independence, not sampled free-pattern completions, establishes
universal coverage of the free groups. Additional controls change each free
group through all eleven patterns and check used-row invariance; they are
calibration checks and are not called exhaustive joint enumeration.

For completeness, all twenty saved greedy membership tests are independently
recomputed using rank(A)=rank([A;f]) via reverse-column elimination, rather than
the producer's incremental forward row-basis routine. Positive recorded
combinations are checked literally; the exact descending removal schedule is
replayed. This checks the finite recorded experiment. It does not establish
global minimum cardinality or compare all possible target functionals.

The independently reconstructed selector catalogue has twenty groups of eleven
patterns. The necessary clause is the disjunction of the negatives of the
fourteen retained pattern selectors. It is saved with every group/pattern/ID
mapping. A full Gram factor must satisfy this clause because matching all its
fourteen patterns is impossible. It can later be appended to an exact same-scope
parity formula after independent byte and object checks; this audit applies no
clause and launches no search. The earlier full parity witness violates it, as
expected, without invalidating that witness's weaker projection claim.

Controls include all729small two-row field-span cases against direct linear
combination enumeration; an exact positive raw certificate; all2^14Boolean
matching-predicate clause cases; and deliberate missing target/dependency
groups, changed patterns, wrong row coefficients, reversed inequalities,
invalid minimality flags and incorrect clause signs/IDs. The exact result
records which controls passed. No full factor positive is fabricated.

The new claim binds the general necessity theorem r1, the fixed support claim
r1, and the saved parity witness r1 as the source of the retained pattern values.
Raw references and hashes remain explicit evidence. It does not depend on the
earlier selected-branch exclusion, the rational relaxation, or the unsearched
240-option CNF. No all-balanced-support, whole-core or unrestricted target
exclusion is implied. Overall target search coverage remains UNKNOWN.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_phase_premise_subset.py --out acceleration/results/20260930_independent_review/hadamard_phase_premise_subset
```
