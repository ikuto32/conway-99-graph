# Full-moment GPU PDHG calibration pilot

Question: does a separate float64 CUDA PDHG implementation reproduce the full
moment simplex saddle iteration with soft moment rows and hard reciprocity rows?
This is an engineering pilot, not a graph search or mathematical certificate.

The new protocol magic is C99MHP01. Its array layout follows the historical
C99SCP01 layout, but its mathematical semantics differ: first q duals clip to
[-1,1]; every remaining equality dual is unbounded. The original parser,
storage and diagonal-step derivation are visibly reused; the kernels and
checkpoint metrics are new. Existing CUDA files remain unchanged.

The audited two-coordinate augmented matrix is hash-bound to its independent
model and complete-domain gates. Drop84 simplex rows and6972 slack columns;
put3486 moment rows first, then1800 reciprocal rows. The89308 original
probabilities and84 domain offsets retain their identities. Check simplex
coefficients, slack signs and hard RHS before export. No enumeration or LP.

Freeze cold uniform probabilities, zero duals, pbar=p, eta=.9 and theta=1.
Row sigma=.9/max(1,row absolute sum); one tau per simplex equals
.9/max(1,maximum column absolute sum). Projection shifts by maximum, clips
inactive tails at-1 and uses60 bisections on[-1,0]. Each simplex gets256
threads and a fixed binary-tree reduction. Compile float64 with --fmad=false.
Strict dimensions: at most1,000,000 probabilities,100,000 per simplex,
10,000 rows,100,000,000 nonzeros and2GiB binary. Exact transpose, sorted unique
CSR and finite data are mandatory; malformed inputs must fail before kernels.

Run only three synthetic cases and the audited two-coordinate model, each at
checkpoints1,2,10,100; cap each process at120 seconds and preserve failures.
Controls: uniform exact feasible2-choice case; inconsistent singleton hard
row whose dual must exceed1;45,882-choice uniform projection. Save all five
vectors at each fresh checkpoint and progress immediately. Negative parser
controls: bad magic, bad transpose, trailing bytes and out-of-range domain.
No retries or six-coordinate GPU run in this protocol.

Independent CPU comparison must inspect all vectors and diagnostics for these
cases, without importing the CUDA producer. Preregister absolute tolerance
1e-8 per vector entry and1e-7 scalar diagnostics, simplex residual1e-9.
Report every failure. Shared floating arithmetic is disclosed; this establishes
numerical parity only. Root must receive independent PASS before larger runs.

Intermediate soft L1 is not a primal upper bound when reciprocity is violated.
Report it separately from hard L1/Linf residuals and numerical dual support
lower expression. Even positive floating lower scores are not certificates;
later exact integer support checking on every raw neighborhood is required.

Locked setup uses UV_PROJECT_ENVIRONMENT=build/research-venv and
`uv run --locked --offline --cache-dir .uv-cache-20260917 python -B`.
Build with `powershell -File acceleration/build_moment_pdhg_gpu.ps1`.
Exporter: `acceleration/export_20260917_moment_pdhg.py --out acceleration/results/20260917_moment_pdhg_gpu/export`.
Invocation receipts must bind source, build script, executable, export and
this protocol, with actual versions, hardware and complete commands.
