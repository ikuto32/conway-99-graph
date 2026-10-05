# Five prescribed triangle Grams over GF(2) and GF(3)

Freeze this protocol before computation. The population is exactly connected_00,
connected_01, connected_02, connected_03 from the independently audited four-core
P=I portfolio, followed by the independently audited SRG(243,22,1,2) fixture.
Use both prime fields 2 and 3. Do not enumerate the 3,580 matching-pair catalog.
The preparation has a 60-second bound and no native/GPU/SAT calls.

For the raw symmetric 3n-by-3n core C (n=12 or20), independently form
G=nI-C-C^2+2J-blockdiag(J_n,J_n,J_n). Require exact integer CG=GC. For the four
cores compare G with the saved prescribed Gram. For the243 fixture also check
the actual F F^T=G, margins and actual F D=H where H=2J-(I+C)F.

For every field/matrix, save full row operations, row transformation, reduced
matrix, pivots, rank and nullspace basis. Exact operation replay checks the
certificate without floating point. Before research cases, compare elimination
with explicit row-span cardinalities for all64 binary and729 ternary2-by-3
matrices, and reject corrupted ranks, RREFs, transformations, operations and
kernel vectors. These producer checks do not independently approve this research.

Any candidate factor has the three cell indicators in its left kernel overGF2,
so rank(F)<=3n-3. OverGF3 the two cell-indicator differences are in its left
kernel, giving rank(F)<=3n-2. Also rank(G)<=rank(F). Record whether Gram rank
alone reaches that maximum. With even n the binary Gram is alternating and has
even rank, so it cannot equal the odd upper bound3n-3.

Additional candidate derivation, pending independent review: C commutes with G
because it has exactly one neighbor in every cell; both C*blockJ and blockJ*C
equal J, and C commutes with J. Thus kerG is C-invariant. OverGF2, write R for
the span of the three cell indicators and L=ker(F^T), so R<=L<=kerG. If
rankG>=3n-4, L is either R or all kerG and is therefore C-invariant. For every
x in L, x^T H=x^T(I+C)F=0. Columnwise linear algebra then supplies some field
matrix D with F D=H. The maximal-factor-rank assumption of the earlier verified
lemma is sufficient but need not be forced for this broader sufficient test.

Also compute the exact induced action of C on kerG/R. If it is scalar, every
intermediate L is invariant, giving the same GF2 consistency argument even at
lower ranks. Save a complete kernel basis beginning with the forced cell vectors,
the full core action matrix and quotient action. OverGF3 compute analogous data
but make no automatic inhomogeneous consistency claim from scalar action alone.

Neither a rank gap nor a nonscalar quotient proves that a feasible factor with
incompatible mixed equation exists. Conversely, field consistency does not give
a symmetric/binary/zero-diagonal D, its degree conditions, or the residual
quadratic identity. No target construction, exclusion, novelty, exhaustive core
coverage or target automorphism is assumed. All new outputs remain CANDIDATE.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/theory_20260930_five_core_modular_gram.py --out acceleration/results/20260930_five_core_modular_gram
```

The manifest is written before controls and research calculations. It records
exact inputs/gates, source commit, command, environment, population and limit.
Raw certificates and failures must be retained; use a new path for any corrected
execution rather than overwriting evidence.
