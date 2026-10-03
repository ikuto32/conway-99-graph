# Independent four-exception local-profile review

This review concerns only the frozen six-prism Hadamard coordinate support,
the prescribed full integer Gram, and all distinct outside-column overlap
caps of two. Exactly four triplicate-support groups are assumed unbalanced.
The prior circuit theorem leaves fourteen possible support quartets. It is
not a target-wide classification or an abstract Gram-only exclusion.

For a quartet with primitive circuit signs c_g in {+1,-1}, its deviations
are c_g d_a at a common coordinate a and zero elsewhere. Both signs occur.
Each count 1+c_g d_(a,f) must be between zero and three, so every d entry is
in {-1,0,1}. Coordinate fibre counts sum to three; thus d_a is either zero
or a permutation of (-1,0,1). The group's two-per-fibre column quotas imply
sum_a d_a=0. The all-zero profile is excluded. A common intersection of size
two has six opposite nonzero-vector profiles. Size three has eighteen
profiles with one zero and an opposite pair, and twelve with three nonzero
vectors. The thirteen size-two quartets and one size-three quartet therefore
give 13*6+30=108 labelled profiles, without a symmetry quotient.

The independent checker generates all ninety words assigning two of six
support coordinates to each fibre and all 117480 unordered triples. A
repeated word would repeat a within-fibre coordinate pair of prescribed Gram
one, so distinct word triples suffice for every actual factor. It uses
literal row sets and integer pair counts to reconstruct the complete 31110
local triples satisfying local Gram upper bounds and within-group column
caps. This cap premise is indispensable to the recorded scope. Local words
map to any saved support because each support contains one endpoint of each
of the six standard matched coordinate pairs.

For each profile the checker independently filters every catalogue triple
by all eighteen coordinate/fibre counts. It then evaluates every pair of
options in each of the six group pairs, using sparse integer Gram sums and
set intersections of all nine cross-group column pairs. This is separate
from the producer's target-one, occupied and doubled bit-mask optimization.
Every saved forward relation bit is checked and each reverse relation is
independently transposed. There are 1358856 option-pair evaluations.

Every saved arc-consistency deletion is checked against the exact current
right-hand domain and the complete authenticated relation. Deleting an
unsupported value preserves every possible joint solution. Final domain
bits, counts and empty flags are checked. For each remaining value and each
other group the checker saves a concrete surviving support, establishing a
fixed point. It does not infer a simultaneous choice from these individual
supports. Twelve profiles have complete empty-domain certificates and
ninety-six remain unresolved at nonempty fixed points. The two relation
stages start from the same original domains; their twelve exclusions overlap
and are not counted twice.

Controls include separately scoped genuine SRG243 factor pieces, corrupted
catalogues, profiles, relation bits, deletion states and final outcomes. A
two-colour triangle CSP is checked to be arc-consistent yet globally
infeasible, guarding the interpretation of the ninety-six surviving cases.
No solver or floating-point calculation is used, and no producer module is
imported. The exact source, inputs, command and output hashes are recorded.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_four_group_local_screen.py --out acceleration/results/20260930_independent_review/hadamard_four_group_local_screen
```
