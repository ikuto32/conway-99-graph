# Dynamic exact residual60 screen

Freeze before calibration or research use. Accept a raw core C and incidence
factor F, without fixing historical matchings or a historical crossmatching.
The research CLI requires an independently accepted factor artifact, bound
by its exact bytes to an actual SAT-object gate. It does not treat a producer
check, calibration report, hypothetical matrix, or mere agent agreement as
an accepted factor. No research factor is assumed available during setup.

Pin the general residual-equivalence audit, claim
C-TRIANGLE-FACTOR-RESIDUAL60-COMPLETION-EQUIVALENCE r1, at
`independent_review/triangle_residual60/summary.json`, SHA256
16120b7fe6a2645b9de8cb81e4eb4c9a6852bad0c513e4978fb116effdab7a73.
The independent review applies to arbitrary cores of the stated three-fibre
type. It does not automatically approve this new implementation.

First validate C as binary, symmetric, zero diagonal,36by36, with exactly
one neighbor in each12vertex fibre for each row. Validate F as binary36by60,
row sums10, each fibre-column sum2, and exact
`FF^T=12I-C-C^2+2J-diag(J12,J12,J12)`.
Keep this factor validation separate from the necessary residual screen.
The screen never infers a factor's existence from the right-hand Gram.

Compute H=2J-F-CF and T=F^TF in integers. Record negative H and offdiagonal
T>2 as necessary-completion obstructions. For every unordered pair y,z,
allow a residual edge exactly when T_yz<=1 and both F[:,z]<=H[:,y] and
F[:,y]<=H[:,z]. Save all1,770 decisions and every failed coordinate test.
This is an undirected allowed-edge graph, not a completed residual graph.

Every true residual neighborhood has eight allowed members. Report a
shortage if its allowed degree is below8 or a coordinate's available ones
are below H. Also record the elementary fixed-cardinality lower bound:
among N allowed vertices with p ones at a coordinate, any8subset has
between max(0,8-(N-p)) and min(8,p) ones. A demand outside this interval is
another necessary shortage. Its proof is a direct subset count, not an
automatic consequence attributed to the existing theorem audit. Calibrate
that interval on complete small subset enumeration.

Calibration uses a literal valid rook9graph. Its triangle normalization has
empty Y and calibrates the generalized factor prerequisite validator only.
A different split into six known and three residual vertices gives a real
nonempty residual triangle of degree2; it calibrates H/T/allowed pairs and
capacities by direct adjacency counts, explicitly not as a36by60research
factor. Include corrupted shapes, binary values, symmetry, fibre degrees,
Gram/row margins, deficit and overlap values, allowed edges, and quota data.
Report the limits of each control, including the unavailable research-sized
positive factor.

Calibrate and screen are deterministic, bounded to120seconds/8GiB, with no
SAT call, no residual-row enumeration and no full residual completion.
Passing the screen is not feasibility; an obstruction is producer-candidate
evidence until another implementation checks the raw factor and witness.
Do not make target claims from one rejected factor. Future exact row-domain
searches require a separate protocol and scope review.

CLI with `UV_PROJECT_ENVIRONMENT=build/research-venv`:

`uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/theory_20260930_variable_core_residual_screen.py calibrate --out NEW_DIRECTORY`

Research CLI, only after a factor passes independent checking:

`...py screen --factor INPUT --factor-gate REPORT --factor-gate-sha256 EXACT_SHA --out NEW_DIRECTORY`
