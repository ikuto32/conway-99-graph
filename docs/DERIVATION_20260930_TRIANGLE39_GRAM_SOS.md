# Candidate universal39-core Gram redundancy

Status: CANDIDATE until separate review. This producer does not approve its
own derivation. No novelty is claimed; see the immutable archive overlap
record, especially prior Wave40/41 cubic-core decomposition and Wave58's
restatement of the already known36-factor-Gram kernel.

## Arbitrary core and decomposition

Take a triangle T={t0,t1,t2}, three disjoint12-element cells Ai, all edges
from ti to Ai, a perfect matching Mi inside each Ai, and cross-cell perfect
matchings I,I,P between A0--A1, A0--A2, A1--A2 respectively. P is arbitrary.
No commutation, prism-free condition, graph feasibility or target
automorphism is assumed. Let A be its full39 by39 adjacency matrix. The
36 by36 inner adjacency C is cubic, symmetric, and has one neighbor in
each of the three cells. Thus it preserves the cell-constant subspace F
and its orthogonal complement W of zero sum on each cell.

For any real vector x, write its triangle coordinates as r_i and its
coordinates on Ai as b_i+z_x, where b_i is their mean and each z has
zero cell sum. Put R=sum_i r_i and B=sum_i b_i. There are no cross terms
between z and the six-dimensional space of triangle/cell constants in
either target Gram matrix G=27I-9A+J or Q=A+4I.

## Exact sum-of-squares identities

For unordered edges uv of C, direct expansion gives

    x^T Q x = sum_v z_v^2 + sum_uv (z_u+z_v)^2
              +3 sum_i (r_i+4b_i)^2 + R^2 +12B^2.

Indeed cubicity gives sum_uv(z_u+z_v)^2=z^T(3I+C)z. The constant part
expands to3 sum r_i^2+R^2+24 sum r_i b_i+48 sum b_i^2+12B^2,
which is the literal Q quadratic form on this subspace.

Similarly,

    x^T G x =9 sum_uv (z_u-z_v)^2
              +36 sum_i ((r_i-R/3)-3(b_i-B/3))^2
              +4(R-6B)^2.

On W the form is9(3I-C). The cell-constant form first expands to

    36 sum_i(r_i-3b_i)^2 -8R^2+24RB+36B^2.

Splitting each triple into its mean and mean-zero parts yields precisely
the displayed two square terms. All coefficients are positive. These
identities prove both forms positive semidefinite for every permitted
Mi and P, even if the core violates independent target pair constraints.

The producer checks the full matrix coefficient identities over the
integers. If S_i is the sum on Ai, S=sum S_i and Z_v=12x_v-S_i, multiply
both formulas by144. The integer linear forms are:

* Q: Z_v (weight1), Z_u+Z_v (weight1),12r_i+4S_i (weight3),
  12R (weight1), S (weight12).
* G: Z_u-Z_v (weight9),12r_i-4R-3S_i+S (weight36),
  12R-6S (weight4).

## Kernels and ranks over the reals

For Q all squares vanish only if z=0, r_i=-4b_i and B=R=0.
The two free cell-constant contrasts form its full kernel. Hence

    dim ker Q=2, rank Q=37.

For G, z must be constant on every connected component of C. Every such
component has the same number m of vertices in each cell, because each
cross-cell block is a perfect matching. Its internal perfect matchings
make m even, and m>=2. If C has c components,1<=c<=6. Component-constant
vectors have dimensionc, and imposing zero sum on every cell supplies
the same single weighted equation in all three cells, giving dimensionc-1.

The constant-part squares vanish exactly when r_i=3b_i+B, giving three
more kernel dimensions. Thus

    dim ker G=c+2, rank G=37-c.

The three constant-part kernel vectors are4e_ti+1_N(ti). An integer basis
for the remaining c-1 dimensions is obtained by contrasting component
indicators with weights equal to their per-cell sizes. The producer
exports these vectors and checks annihilation, basis independence and
full rational matrix ranks on all calibration fixtures.

## Related36-factor Gram: prior result, not a new discovery

Let U=diag(J12,J12,J12), T=I-U/12 and H=12I-C-C^2. The Gram expression
forced for a hypothetical36 by60 binary incidence factor is

    K=12I-C-C^2+2J-U = T H T +(5/3)J.

The identities CU=UC=J and C^2 U=UC^2=3J verify the equality. Also

    x^T H x = sum_uv (x_u-x_v)^2
               +sum_v sum_{j<k in N(v)}(x_j-x_k)^2.

The second sum equals x^T(9I-C^2)x by cubicity. Consequently K is PSD;
on W it equals(3I-C)(4I+C). Its fiber-constant action has eigenvalues
60,0,0, and its full kernel dimension is c+1, so rank K=35-c.

This mechanism and kernel formula already appear in the pinned archive:
attempts/wave58-cross-incidence-rank/derivation.md section2 explicitly
attributes them to prior Wave36. That archived package states additional
endpoint premises for its other results; the algebra above needs only
the explicitly described cubic equitable matching core. The present
record does not import the archive's other conclusions or relabel old
VERIFIED statuses as fresh independent verification.

## Interpretation and calibration

Both39-core PSD tests are automatic. Their ranks are at most36 and37,
below the global target Gram ranks44 and55, respectively. The global
ranks follow directly from the target eigenvalues14,3,-4 with
multiplicities1,54,44; no contradiction arises from these core ranks.
Binary incidence factors and simultaneous outside compatibility remain
additional constraints and are not certified by positive semidefiniteness.

The producer uses six explicit component-count controls, the archived
shift6 example, and eight seeded arbitrary matching/permutation examples.
For each, the full scaled integer coefficient identities, exact rational
ranks and explicit kernel bases are checked. Invalid matching/permutation
inputs and corrupted Gram coefficients, SOS weights and kernel vectors
are rejected. These finite controls calibrate the general written
derivation; they are not its universal coverage argument.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/theory_20260930_triangle39_gram_sos.py --out acceleration/results/20260930_triangle39_gram_sos
```

Use a new output directory. The unchanged locked environment is used, with
no floating-point calculations or solver calls. All artifacts stay CANDIDATE
until a different checking path reviews the theorem and raw coefficients.
