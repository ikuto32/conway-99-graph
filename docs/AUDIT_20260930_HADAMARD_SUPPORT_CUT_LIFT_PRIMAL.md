# Independent selected-parity rational lift audit

This checks one saved twenty-pattern projection on the exact six-prism Hadamard
support. It does not assume that arbitrary factors are coordinatewise balanced.
The earlier failed selected branch and its exact zero-row exclusion remain intact.

The checker enumerates all 729 six-letter words, retains the 90 words with two
occurrences of each colour, and examines all 117,480 increasing word triples.
Coordinatewise distinct colours identify exactly the balanced triples. This is
a complete alternative to the producer's enumeration of 46,656 ordered S3 arrays:
transposing any balanced triple gives six permutations, and sorting its three
distinct columns loses exactly the six column orderings. Permutation signs are
computed from inversion counts and normalized against the first coordinate.
Filtering by the authenticated parity patterns fixes every option and its order.

The prescribed Gram is derived from the literal fixed core adjacency, not from
the producer's cached coefficients: its entries are
`G[a,b] = 12*delta[a,b] - C[a,b] + 2 - [same fibre] - sum_z C[a,z]C[b,z]`.
For every local triple, the checker builds the three occupied row sets and counts
all literal row-pair occurrences. It authenticates all selector mappings, sparse
coefficients and all 666 upper-triangular Gram rows. Omitted zero rows are
identically zero. Each diagonal equation is the sum of the ten group-normalization
equations for groups containing that coordinate.

The candidate rational point is checked by integer products after multiplying by
its positive denominator, then again by literal `Fraction` sums on all 666 Gram
entries. Before candidate checking, uniform 1/150 weights over the complete 3,000
unfiltered group options provide an exact positive control on the genuine fixed
geometry. A tiny feasible equality, malformed rational values, changed raw core,
missing options, altered words, matrix entries and right-hand sides calibrate
acceptance and rejection. No producer or previous checker implementation is
imported. No optimizer or SAT solver runs.

Feasibility here means only a nonnegative continuous selector solution. Integrality,
inter-group outside-column caps and the residual graph are absent. The result
does not construct a binary factor or resolve the whole fixed support or target.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_support_cut_lift_primal.py --out acceleration/results/20260930_independent_review/hadamard_support_cut_lift_primal
```
