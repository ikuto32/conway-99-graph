# Independent review of the uniform rounding/covariance bound

PASS. The audit imports no producer and performs no graph or layer search.
It checks the five stored integer row controls, all 85 scalar formulas,
the incidence and projection identities, and the defect-row values
`h(delta) = 0,10,28,58,100`. The convex lower bound is verified by supporting
lines, independently of the producer's 21-step dynamic program.

The graph-to-matrix proof in the producer note is valid. The SRG block
equations give the stated action on the lifted constant, pair-antisymmetric
and pair-symmetric zero-sum spaces. The remaining 70-dimensional kernel has
eigenvalues 3 and -4; trace zero gives multiplicities 40 and 30. Thus
`spec(B) = {12^1,3^40,0^7,(-2)^6,(-4)^30}`. Since `P/2` is an isometry and
`NP Pi=0`, the fourteen cycle-compression eigenvalues lie in `[-16,12]`.
These are mathematical implications under the assumed SRG, not a claim that
the audit constructs B or mechanically proves the SRG reduction.

The internal-edge range `0 <= e_F <= 4` needs no catalogue assumption:
`C_FF=2e_F` is even and nonnegative, and the ten nonnegative overlap entries
sum to `16-4e_F`. The triangle-free argument in the producer note is also
sound: any triple of the four square-corner labels contains a pair sharing
a root neighbour, so an internal triangle would violate lambda=1.

The five row controls do satisfy all seven support-incidence equations and
attain the stated minima. They establish sharpness for an isolated scalar
row relaxation only; edge constraints, symmetry between different rows,
and existence of a global compression remain additional requirements.
None of those additional constraints invalidates the necessary scalar
inequality, and no joint realization is inferred from the controls.

The covariance identity follows from the fixed seven-dimensional block and
the cycle trace, or equivalently orthogonal support-group averaging. Its
lower bound is 84 at E0=0. Comparing the main lower bound with
`5376-8E` excludes no integer E in 0,...,84. The inequalities add no
independent strength to a model already containing every integral C entry
and the exact row sums. No positive E0 lower bound is obtained.

## Optional finite-dimension sharpening, no new credit

For exactly fourteen eigenvalues in `[-16,12]` with total `2E`, convexity
maximizes the sum of squares at endpoints except possibly one entry. Put
`168-2E=28q+delta`, `0 <= delta < 28`. The maximizer has q entries -16,
one entry `12-delta` when delta is nonzero, and all others 12. Therefore

`tr(C^2) <= 5376-8E-delta(28-delta)`.

Together with the rounded lower bound, this is incompatible with E=82 and
83, and with no other integer E in the stated range. Those high layers were
already excluded by prior research; this separate observation receives no
new layer or inventory credit and does not improve the sought lower bound.

No inventory, solver, live runner or submission file was modified.
