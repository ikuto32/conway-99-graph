# Five-matching cell design with independent column bits

Freeze before the single pilot. Question: does the fixed six-prism core
(all three standard matchings and all identity cross matchings) admit a
binary36x60 incidence factor within this cell-pattern family, after removing
the complement-pairing restriction refuted in the preceding experiment?

Retain the five round-robin perfect matchings partitioning K6 and all six
assignments of three cell labels to each matching. Repeat every resulting
cell pattern twice, giving60columns with two components in each cell.
The six bits in every column are independent:360primaryvariables, no fixed
bit normalization and no complement-pair equality. This is still one fixed
cell-pattern family, not an enumeration of all factors or target graphs.
No nontrivial target automorphism or universal core containment is assumed.

For each component pair and ordered cell pair, collect its4columns for equal
cells or8columns for distinct cells. With t=1 or2 respectively, constrain
the first bit sum and second bit sum to2t, and the bitwise-AND sum tot.
Then all four bit-pair counts are exactlyt. Allocate one AND variable per
column/component pair:900ANDvariables, total1260. Three clauses per AND and
direct subset clauses for each exact cardinality predict

`2700 + 45*23 + 90*288 = 29655 clauses`.

These relations give the full prescribed Gram: same-component distinct rows
never coincide; distinct-component row pairs meet once in equal cells and
twice in unequal cells. Row10 follows by summing any fixed component-pair's
bit margins across the three partner cells. Fibre-column2 is automatic.
Before launching, exhaustively calibrate AND and every cardinality shape
used, and all Boolean domain states for the three-count/four-cell-count
equivalence. Verify the predicted counts. Any mismatch stops the pilot and
is recorded as a deviation, never silently altering the declaration.

One native CaDiCaL1.9.5 invocation is authorized, using its authenticated
prior CLI calibration:5seconds,100000conflicts,256MiBaddress space,
128MiBtrace file, TERM/2second kill grace,15second outer guard. No retry,
default seed retained and explicitly recorded. Exact integer/Boolean tests
have no floating acceptance tolerance. Preserve all input,output,source,
command and tool hashes and actual resource outcome.

SAT: preserve every native assignment and raw decoded36x60F. Check all1296
integer Gram entries,36row sums,180fibre-column sums, and canonicalize the
60columns by their two C0 labels. Label only CANDIDATE pending a separate
raw-object checker. No residual60D is encoded or constructed by this pilot.
UNSAT: preserve complete rawtrace but make no exclusion before independent
encoding and proof checks. UNKNOWN/time/resource limits prove nothing about
feasibility. Earlier450variablecomplement-paired artifacts stay unchanged.

Execution uses the existing uv lock with no dependency changes:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/theory_20260930_prism_unpaired_design.py --out acceleration/results/20260930_prism_unpaired_design_pilot --research
```
