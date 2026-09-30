# Independent GF(3) obstruction review for the second parity branch

Reviewer: `/root/structural_attack`; producer: `/root/state_literature_audit`.
This review imports no producer code. It concerns only the second saved parity
assignment on one fixed six-prism Hadamard support, with the additional
coordinatewise-balanced triplet condition. It does not use the unsearched
240-option CNF as a premise. The live claim outcome is supplied by the exact
checker report; this written derivation alone does not assert that a run passed.
The audit is bounded to sixty seconds and zero solver calls.

For a group of three columns, coordinatewise balance means that the fiber
assigned to coordinate i is a permutation pi_i of the three column labels.
Every such permutation has a unique form pi_i(x)=s_i*x+t_i over GF(3), with
s_i=1 or−1. Its parity is even exactly when s_i=1. Replacing the column label
x by pi_0(x) is a permutation of the three physical outside vertices and sets
the first map to the identity. It preserves Gram, the repeated support, column
caps and any residual completion after the corresponding vertex relabelling.
This is not an automorphism assumption. The signs of the normalized maps are
exactly the relative parity bits in the authenticated projection; t_0=0.

Here is an independent entrywise argument for the essential local and pair
constraints. Write e_r for the multiplicity of translation x→x+r and o_s for
the multiplicity of reflection x→−x+s. Their permutation-matrix sum has entry

    M[x,y] = e_(y−x) + o_(y+x).

The map (x,y)→(y−x,y+x) is bijective over GF(3). In a locally balanced group,
the six coordinate maps sum to2J. Therefore e_r+o_s=2 for all r,s: all e_r
are equal and all o_s are equal. The selected pattern is mixed, containing
three signs of each kind. Thus each e_r and o_s is1. The three t-values in
each sign class are a bijection onto GF(3). Their sums are zero and every
same-sign difference is nonzero. This supplies forty local sums and120 local
nonzero conditions, alongside twenty gauge equations.

For a nonmatching pair of coordinates a,b, the raw core and root attachments
give the3×3 factor-Gram block2J−I. Exactly five support groups contain both
coordinates. The authenticated pattern has three sign disagreements and two
agreements. Their relative maps are pi_b∘pi_a^−1, with slope s_b*s_a and
intercept u=t_b−s_b*s_a*t_a. There are three reflections and two translations.
In the same entry transform, diagonal entries correspond to r=0. Hence

    e_0+o_s=1;  e_1+o_s=2;  e_2+o_s=2  for every s.

The total reflection count is3, so each o_s=1. It follows that e_0=0 and
e_1=e_2=1. Consequently the three reflection intercepts are0,1,2 and the two
translation intercepts are1,2. In particular, each set sums to zero. These are
120 further homogeneous equations. No full nonlinear feasibility is inferred
from these necessary sums. Their distinctness and nonzero conditions are
retained explicitly and checked when an obstruction is claimed.

The independent checker rebuilds the36-vertex core literally, derives its full
factor Gram using the three root attachments, extracts the twenty repeated
supports directly from L, and reconstructs all120 variables,180 equations,
420 nonzero functionals and60 relative-map records. It compares every raw entry
with the producer artifact. It checks every saved180-term row combination by
direct integer arithmetic modulo3. A single required nonzero local difference
equal to a combination of homogeneous rows is already a complete contradiction.
All420 saved identities are checked to make the producer's recorded counts
reviewable, but they are not counted as independent exclusions.

For a separate rank path, the checker eliminates columns right-to-left using
descending row pivots, rather than the producer's row RREF. It saves and checks
each column-combination identity and triangular pivot. A nonzero raw nullvector
gives the upper rank bound. The producer's full transformation identity and
kernel are also checked directly. Rank is supplementary: the first explicit
row-combination contradiction does not depend on trusting a rank routine.

Controls enumerate all117,480 triples of the90 balanced color words and retain
the150 coordinatewise-balanced triples. Literal inverse column permutations
validate the gauge and all120 mixed local positives. Every affine composition,
all243 phase assignments for a pair with three reflections/two translations,
and all729 two-by-three field matrices are checked, the latter against direct
minors. Twelve pair assignments are positive controls against the exact2J−I
block. Deliberate equation, sign, coordinate, parity, RHS, missing-row,
inequality, combination and kernel corruptions must be rejected. These are
local calibration objects, not claimed full research factors.

The exact claim, its revision, raw hashes, checking method, independent agent
identity and limitations are saved in a separate claim_binding.json. This lane
does not edit the ledger. Workspace checking does not itself establish public
artifact availability or external review. No conclusion is made about other
parity branches, all balanced factors on this support, the core, or Conway99.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_f3_phase_obstruction.py --out acceleration/results/20260930_independent_review/hadamard_f3_phase_obstruction
```
