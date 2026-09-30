# Sixteenth milestone: conditional structure and fixed Hadamard supports

The frozen ledger contains 165 claims: 163 VERIFIED/CLEAR and two
CANDIDATE/CLEAR. Six registration records add 17 claims. A seventh record
updates the connected-01 fixed-support exclusion from revision 1 to 2 by
adding a compressed exact certificate and an independent impact review;
the statement, scope and original evidence are unchanged. Target resolution
remains UNKNOWN. There is no complete target graph or general nonexistence
proof awaiting external review. Overall search coverage: UNKNOWN; no
validated denominator.

The registration chain is
[preparation](../acceleration/results/20260930_sixteenth_preparation_registration/summary.json),
[cyclic-cover redundancy](../acceleration/results/20260930_sixteenth_cyclic_registration/summary.json),
[contraction](../acceleration/results/20260930_sixteenth_contraction_registration/summary.json),
[Hadamard supports](../acceleration/results/20260930_sixteenth_hadamard_registration/summary.json),
[Farkas exclusions](../acceleration/results/20260930_sixteenth_farkas_registration/summary.json),
[uniform relaxation and column order](../acceleration/results/20260930_sixteenth_prism_lp_order_registration/summary.json),
then the [evidence revision](../acceleration/results/20260930_sixteenth_compressed_registration/summary.json).
Schema validation and registration are not mathematical verification. This
cohort excludes the later Hadamard cyclic-factor construction, its CNF and
any native attempt. That construction differs from the coarse-template
cyclic-cover redundancy recorded here.

Use the locked environment and fresh output directories. The historical
commands, versions and input hashes remain in their original manifests.
Recover large mathematical inputs before running the independent checks:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv sync --locked --cache-dir .uv-cache-20260917
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/recover_20260930_twelfth_inputs.py
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/recover_20260930_thirteenth_inputs.py
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/recover_20260930_fourteenth_inputs.py --receipt build/sixteenth-prior14-recovery-new.json
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/recover_20260930_fifteenth_inputs.py --receipt build/sixteenth-prior15-recovery-new.json
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/recover_20260930_sixteenth_inputs.py --receipt build/sixteenth-recovery-new.json
```

The last helper reconstructs four raw files, totalling 133,500,003 bytes:
the compressed-certificate trial log and the unsearched connected-01 CNF,
clause body and model. It authenticates both package manifests, every gzip
part, compressed stream and decompressed length/hash; it refuses to
overwrite differing bytes. Every public part is below 10 MiB. The original
raw files remain locally available. An actual fresh-directory recovery of
all four was completed. Hash recovery establishes identity, not correctness.

For arbitrary internal matchings with identity cross-fibre matchings, the
exact factor Gram equations force every column's six entries to occupy
distinct coordinates. Its selected vertices are independent in the core,
and the mixed core/outside common-neighbour caps follow. These are
conditional identity-P results, not a normalization of arbitrary P. If such
a factor extends to an actual target graph, its residual 60 vertices split
into 20 disjoint triangles. Together with the root and coordinate triangles,
this gives a partition into 33 triangles; it does not count all triangles
of the graph or assert existence. The independent proof records the
overlap with the archived Wave39 argument.

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_identity_p_triangle_partition.py --out build/sixteenth-identity-p
```

The written arbitrary-matching proof is accompanied by 332,640 raw support
controls, a separate matching enumeration and deliberately corrupted
controls. The residual 60-vertex control is explicitly not an SRG99 graph.

For the previous fixed coarse-60 template, simultaneous coordinate-bit
flips in its six components form 64 relabellings. They allow the six bits of
the first column to be zero without assuming a target automorphism. The
exact extension adds six negative units to the original formula, yielding
5,238 variables and 85,704 clauses. Prefix auxiliary assignments are
regenerated; no auxiliary-variable permutation is asserted.

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_prism_coarse60_bitflip.py --out build/sixteenth-bitflip
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_prism_coarse60_bitflip_object.py calibrate --out build/sixteenth-bitflip-object
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_prism_coarse60_arc_v2.py --out build/sixteenth-arc
```

After this conditioning, six local domains have 68 values and twelve have
136: 2,040 surviving local values. Bidirectional arc consistency removes
none. Independent checking saves a direct support for every one of 30,600
directed live-value checks across the 135 binary relations. This is a
fixed-point result, not joint feasibility, and does not propagate outside
column caps. The initial audit's metadata-order assumption failed; its
source and failure are retained beside the corrected v2 audit.

The complete 34,220-triple coarse census finds 18,440 triples admitting
pairwise-disjoint lifted columns for some local bit assignments and 15,780
rejected triples. A saved 20-triple cover and local bits pass disjointness
but have 900 Gram mismatches, so they are not a factor. The later exact
cyclic-fibre argument is stronger: the fixed 60-word set partitions into
20 length-three orbits whose fibres differ in every component. These
columns are disjoint for every one of the 2^360 bit assignments. Thus a
cover-only constraint would be redundant for this template. These covers
are not asserted to be the triangles of any residual graph.

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_prism_coarse60_triangle_cover.py --out build/sixteenth-cover-census
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_coarse60_cyclic_cover.py --out build/sixteenth-cover-redundancy
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_triangle_contraction.py --out build/sixteenth-contraction
```

The contraction identities apply to an actual residual triangle partition
R and actual residual adjacency D. With W=DR-2R, B=R^T W and T=FR, they give
T^T T+5B+W^T W=18I+18J and FW=6J-(C+3I)T. No chosen cyclic partition is
assumed to be actual. The individual floor-capacity test is redundant:
for binary 36-by-20 T with row sums 10 and column sums 18, every capacity
sum is at least 21, already exceeding the required 18. The proof and finite
DP controls are saved in
[the independent floor audit](../acceleration/results/20260930_independent_review/triangle_capacity_floor/summary.json).
That original script has a fixed output directory; do not rerun it over
the frozen report. A genuine 243-vertex graph supplies a separate generalized
contraction control, not evidence for a 99-vertex graph.

The Paley order-20 construction supplies binary 12-by-60 supports L for
arbitrary three internal matchings. Exact aggregation of a hypothetical
identity-P factor gives LL^T=15I+15J-5(M0+M1+M2), row sums 30 and column
sums 6. The Hadamard construction satisfies these support equations only;
colouring each support into three fibres must still satisfy the full Gram
and cap constraints.

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard20_support_v2.py --out build/sixteenth-supports
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_support_farkas.py --out build/sixteenth-farkas
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_farkas_compressed.py --out build/sixteenth-compressed
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_prism_relaxation_and_order.py --mode lp --out build/sixteenth-uniform-lp
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_prism_relaxation_and_order.py --mode order --out build/sixteenth-column-order
```

Five frozen supports were tested: one for each of the four selected connected
cores and one for the six-prism core. Connected-00 is impossible because
column 41 has no permitted colouring, with a short pigeonhole certificate.
Connected-01/02/03 are excluded by exact integer Farkas vectors for their
continuous selector equalities. Independent reconstruction checks every
matrix column, nonnegative dual product and negative right-hand-side
product (-37,617,760, -7,174,717 and -863 respectively). Floating-point LP
infeasibility and the initial failed rational recovery are preserved as
discovery records, not proofs. These exclusions concern the three particular
supports, not the connected cores or all Hadamard choices.

The compressed connected-01 certificate has right-hand-side product -1 and
maximum absolute weight 50. All 4,067 dual column products are nonnegative.
It remains a substantial certificate, not a short human proof. Its 894
recorded exact simplification trials include 97 valid certificates. The
independent evidence-only revision review preserves both original and
compressed proofs and all unaffected claims. Its historical CLI expected
revision 1; inspect its saved snapshots and registration before/after
records instead of rerunning it on the revised ledger. The failed first
registrar is preserved and performed no ledger write.

The previously built connected-01 formula (443,143 variables, 2,168,486
clauses) remains CANDIDATE and unsearched. It has no independent encoding
gate. Its large raw inputs are recoverable, but the separate exact linear
exclusion made a SAT attempt unnecessary. The saved checker preparation
is not a successful whole-encoding audit.

For the six-prism support, every selector equal to 1/90 is an exact rational
solution of the 726 equality rows. This does not establish an integral
factor or satisfy the nonlinear pair constraints. Its 60 columns form
20 identical-support groups of size three with identical 90-option lists.
A genuine factor cannot choose the same option twice within a group, by
the within-fibre Gram entries (also by the outside cap). Relabelling those
three outside vertices therefore permits strictly increasing option ranks.
The independent review checks all groups and 704,880 ordered distinct-triple
sorting controls. This is a relabelling argument, not an automorphism
assumption or a further fixed-column choice. No ordered full-factor CNF was
searched in this cohort.

The normalized coarse-60 native attempt completed UNKNOWN with exit 0:
2,000,001 observed conflicts against a configured 2,000,000 limit, 153.47
native wall seconds and 153.516 wrapper seconds. The preregistered limits
were 300 seconds, 4 GiB address space and 10 GiB proof-file size, using one
ext4 native call with no retry. Its 2,055,785,844-byte retained trace is
LOCAL_ONLY, incomplete, and not an UNSAT certificate. No factor was decoded.
With that exact local trace available, the outcome audit can be replayed:

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_prism_coarse60_bitflip_native_outcome.py calibrate --out build/sixteenth-outcome-controls
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_prism_coarse60_bitflip_native_outcome.py audit --summary-sha256 3df3239ec412d9b56ea7168d6dd9fddd033d60e3666b181930a659d749ba2539 --out build/sixteenth-native-outcome
```

A public checkout lacks that trace and the local executable: full native
outcome replay is unavailable without them. The saved source/build records
for pristine CaDiCaL 1.9.5, official commit
146207318796f094dcded87349a64f0c6927309e, are in the earlier
[native build package](../acceleration/results/20260930_native_cadical195_build/manifest.json).
Its recorded binary hash is
021e58781c761296b436cfbdf49507ff290db175f67e5609bf6f41e4cc62d0b7.
The original Ubuntu 24.04, compiler, configure/make commands, GNU timeout
and prlimit settings remain in that package and the native manifests.
Rebuilding with another toolchain need not reproduce binary bytes and
requires fresh calibration. No new native build or speed comparison is
claimed here. All research attempts in this cohort have ended; saved
process observations are historical, not current liveness evidence.

The [publication catalog](../acceleration/results/20260930_sixteenth_artifact_packaging/catalog.json)
checks the seven-step ledger chain, exact 17-claim evidence scope, explicit
file/directory allowlist, recursive immutable input references, gzip
recovery and Git byte preservation. It provides exact raw-ignore proposals
for four recoverable raw files and one incomplete trace. Local native
tools are separately identified. It does not change the ledger or Git,
rerun mathematical checks, or claim that preparation itself makes files
public. Public availability is established by the subsequent publication
receipt. Registry/schema checks and a green CI badge are not mathematical
verification.
