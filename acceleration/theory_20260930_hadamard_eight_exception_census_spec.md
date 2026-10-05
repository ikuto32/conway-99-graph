# Eight exceptional groups: necessary-kernel census

Frozen question: which of all C(20,8)=125,970 eight-element subsets of the twenty
literal support groups can have nonzero deviations at every nominated group?
Selection is complete lexicographic enumeration. This is a necessary integer
marginal calculation for the prescribed full Gram on the literal support. No
automorphism assumption or column-overlap cap is used. Retained subsets are not
asserted feasible as factors or graphs.

The previously derived augmented incidence matrix H gives H delta=0. Every
deviation is integer, at least -1 on an incident coordinate and zero elsewhere;
the sum over three fibres and each group's coordinate sum vanish. Full column
rank forces balance. A coordinate vanishing throughout a complete kernel basis
forces that nominated group balanced. Both cases exclude the exact-eight family.

For a one-dimensional kernel, save primitive integer generator c and a Bezout
identity, so every integer solution is t c for integer t. If any |c_i|>=2, the
bound t c_i>=-1 forces every fibre's t to one side of zero. Their sum vanishes,
so all vanish. Otherwise every nonzero entry is +1 or -1. A nonzero deviation
can occur only at a coordinate common to all eight groups. At most one common
coordinate, together with the zero coordinate sum, again forces balance. Keep
all other subsets. Do not apply this one-dimensional reasoning to larger kernels.

Use exact Fraction/Bareiss rank certificates, nonzero rank-size minors, complete
independent integer null bases and all classification witnesses. Production
shares the pinned earlier six-group rank helper, which is not an independent
checking path. Before enumeration run its 512 binary 3x3 controls, then eight-
column full-rank, large-coefficient, forced-zero, retained higher-kernel and
alternating cycle sign-kernel controls. The latter checks common counts 0,1,2.
Reject corrupted null vectors and determinant claims. Any failure is preserved.

Resource limit: 240 enumeration seconds per invocation, checked after chunks
of at most 2,000 subsets. No native solver call. Save immutable chunk checkpoints
with input/output SHA256 identities and progress. Resume requires the exact
checkpoint hash, identical frozen sources, a checked contiguous prefix and a
fresh output directory. A timeout records only that prefix. No floating-point
threshold or numerical certificate is used. A complete enumeration is success
for this census, not for Conway-99; all conclusions remain CANDIDATE pending
independent derivation and raw-certificate review.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/theory_20260930_hadamard_eight_exception_census.py --out acceleration/results/20260930_hadamard_eight_exception_census
```

Resume uses --resume-checkpoint PATH --resume-checkpoint-sha256 SHA and a fresh
--out directory. Source commit, exact command/cwd, Python and pinned source
identities, raw artifacts and actual measured results are retained in manifests.
