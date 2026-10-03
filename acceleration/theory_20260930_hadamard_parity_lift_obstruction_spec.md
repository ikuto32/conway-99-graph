# Exact zero-row certificate after the selected lift build

Freeze this bounded extraction before running it. The original selected-branch
build remains unchanged and incomplete: the generic exact counter asserted when
the required cardinality was one but the input set was empty. No solver ran and
no complete CNF or encoding approval exists for that attempt.

The purpose is to preserve every positive Gram row with zero contributions from
all 312 saved options, its literal coefficient array, the corresponding row of
the saved exact 560-equation LP, and a single-row integer Farkas certificate.
Select all such rows in increasing raw core-row order. For the first one, use
dual weight minus one, and zero for every other equation. Check all 312 products
and the right-hand-side dot exactly. Do not numerically optimize or choose a
different parity branch. The root's continuous LP is unnecessary for this
specific exact obstruction and is not invoked by this producer.

Scope is only the selected parity assignment on one fixed support with the extra
balanced-triplet condition. Completeness of the 150 local triples, the filter,
column-order equivalence, and the exact Gram targets must be independently
checked before promotion. An assertion or failed build alone is not a proof.
No claim is made about all parity assignments, all balanced factors, this core,
or the unrestricted target.

Resource limit: ten seconds, zero solver calls. Preserve new raw coefficient
records, exact matrix and scope pins, source commit, command, and versions. Test
a valid zero-row obstruction, a corrupted column coefficient and a zero RHS
non-obstruction. Existing failed sources and artifacts are never overwritten.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/theory_20260930_hadamard_parity_lift_obstruction.py --out acceleration/results/20260930_hadamard_parity_lift_obstruction
```
