# First-matching orbit normalization, version 1

Question: can the already verified arbitrary-core necessary factor model be
searched with M1 restricted, by relabelling, to its eleven previously audited
orbits under the centralizer of M0? This does not assume that a solution has
any automorphism. M2 and P remain arbitrary.

Use the complete eighth-wave matching census as an immutable premise. For
each of its 10,395 labelled matchings, save an explicit permutation h that
centralizes M0 and sends that matching to its saved first-stage representative.
Apply h simultaneously to coordinates in all three fibres. Cross blocks 01
and 02 remain identity; M1,M2,P conjugate by h. Relabel the canonical C0
columns by the induced permutation of the 60 nonmatching two-subsets. Rows
and columns of F are thereby permuted. All Gram identities, margins, mixed
caps and column-pair caps are preserved. Thus every target has a primary
solution whose M1 is one of the eleven representatives.

Append eleven selector variables to the frozen arbitrary-core formula. Add
one clause requiring a selector and, for each selector, six implications to
the matching-edge variables of its representative. The base matching degree
constraints then force exactly that matching. Distinct representatives cannot
both be selected, so an additional at-most-one selector constraint is needless.
This adds exactly 11 variables and 67 clauses. It restricts primary assignments
but is equisatisfiable up to the proved relabelling, not pointwise equivalent
to the unnormalized primary domain.

Preregistered build: 120s, 8GiB, no solver. Reuse only frozen census data and
base formula; do not rerun the census or overwrite any prior evidence. Emit
all 10,395 transports, independently checkable clauses and a written coverage
argument. Independent full transport, clause, scope and object gates remain
required before a later native run. A SAT factor still omits residual D; an
UNSAT claim requires complete independently replayed proof artifacts.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/theory_20260930_variable_core_m1_orbits.py --out acceleration/results/20260930_variable_core_m1_orbits
```
