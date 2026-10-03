# Independent written audit of residue and energy bounds

Verifier: /root. Producer: /root/structural. Method: independent_derivation.
Written on 2026-10-03 UTC; this artifact is a human-checkable proof review,
not an executable calibration or a target resolution.

Exact discovery artifact:
`docs/CANDIDATE_20261003_TERNARY_RESIDUE_ENERGY_BOUNDS_V1.md`,
SHA256 `82f92749d30949fe0dcdcfcf3aab15256f90c31bfcbb1208350397870a123392`.
Revision 1 asserts, for every symmetric binary zero-diagonal order99 matrix
of exact integer row degree14, with sums over all4851 unordered pairs,
`r_uv=(A^2)_uv+A_uv-2`, `F3=sum 1[3 does not divide r_uv]`,
`E=sum r_uv^2`: `F3<=E<=28F3`. It also asserts the complete residue histogram
constraint `q1-q2=0 mod3`, including in each vertex row; hence F3=1 is
impossible and F3=2 requires q1=q2=1. These are metric necessities only.

## Separate counting path

Every vertex is the middle of exactly choose(14,2)=91 unordered two-step
paths with distinct endpoints. Counting middle vertices gives
`sum_[u<v] (A^2)_uv=99*91=9009`, independently of any incidence representation.
There are exactly `99*14/2=693` edges and `99*98/2=4851` unordered pairs.
Thus `sum r=9009+693-2*4851=0`.

At an edge, neither endpoint can be a common neighbor and the remaining
neighbor set has size13, so `0<=CN<=13` and `-1<=r<=12`.
At a nonedge, `0<=CN<=14` gives `-2<=r<=12`.
All residuals are integers. Write N for the absolute negative mass and P
for the positive mass. The preceding exact count implies P=N. Separately
bounding the two parts gives
`E<=12P+2N=14N`.
Each negative residual is either -1 or -2 and violates divisibility by3.
Consequently `N<=2F3` and `E<=28F3`. Conversely every violation has absolute
residual at least1, so its square contributes at least1 and `E>=F3`.
This establishes the exact universal statement within its declared domain.

For a fixed vertex, direct walk counting gives the complete off-diagonal
common-neighbor sum `14*14-14=182`. Its adjacency sum is14 and it has98
other vertices. Therefore its full residual row sum is `182+14-196=0`.
Reducing the global or row sum modulo3 gives `q1+2q2=0 mod3`, equivalently
`q1-q2=0 mod3`. If F3=1, the only two possible histogram vectors are(1,0)
and(0,1), both rejected. If F3=2, only(1,1) among(2,0),(1,1),(0,2) survives.
No realization of these histograms by a graph is asserted.

## Falsification and limits

The entire discovery paper was read. The global middle-vertex counting
path above is separate from its initial per-row derivation. Both use exact
integer arithmetic, rather than executable producer code or cached scores.

- Positive residuals divisible by3 can contribute to E without contributing
  to F3; the negative-mass argument still bounds them. The algebraic residual
  list(-2,-2,-2,6) has zero sum, F3=3 and E=48. It is a sign-control list,
  not a graph fixture or an executable check.
- The histogram is modulo3 with residues0,1,2, including negative residuals;
  -2 has residue1 and -1 has residue2. Signed-language remainder conventions
  must not replace this mathematical histogram.
- All pairs, or the full vertex row for the row claim, are required. A sampled
  or root-only sum need not have zero residual mass or the recorded bounds.
- Exact order99 and degree14 are used in the mass identity. Merely congruent
  degrees, a different domain, nonsymmetric or weighted matrices are outside
  this theorem. Generalized fixture scores need their own stated conditions.
- The inequalities and histogram relation do not validate a cache on their
  own, establish move-space coverage, force an incidence kernel, or prove
  target existence or nonexistence. No solver or optimizer has been approved.

Outcome: PASS for the exact revision1 statement and its histogram consequences.
Executable controls and software versions: null; this is a written derivation
with zero executed proof/fixture commands. Shared trusted components are exact
finite integer arithmetic, counting and the literal recorded matrix domain.
No discovery imports, numerical optimizer, software elimination or SAT checker
is used. Novelty, external review and formalization are unestablished.
Target resolution: NONE. Overall search coverage: UNKNOWN; no validated denominator.
