# Exact exterior-moment producer V1

Source-only implementation by ROOT. This is a discovery producer; Native must
independently rebuild and check raw artifacts before any result is promoted.
The derivation is Structural's 70ef6392 exterior-moment note. No source import,
calibration, type enumeration, LP, or target decision has run at source freeze.

For an ordered induced adjacency H of m<=17 vertices in an (n,k,1,2) graph,
N=n-m, b=k-degree(H), delta=2-H-H^2 on distinct pairs. Exact binary/symmetry/
diagonal/domain and nonnegative demand/deficit checks precede every model.
Rows are total, vertices in order, lexicographic pairs, including zero rows.
All masks 0..2^m-1 are classified once without symmetry quotient. Empty and
singleton types remain. A type must have size<=k, every pair delta>0, H[T]
a matching and |T|-e(H[T])<=k/2. Every eligible column stores literal 0/1
coefficients for every row. Universe decisions preserve the first veto reason.
No count is asserted before actual execution.

The exact integer Gram matrix Z=[[N,b^T],[b,D]], D diagonal b and off-diagonal
delta, is independently reconstructed with every model. Fraction congruence
uses original-coordinate basis vectors. Positive scalar pivots eliminate a
block; a negative diagonal or a nonzero off-diagonal in a zero-diagonal block
returns an exact negative vector q. Its quadratic form is checked literally.
Expansion gives y_total=q0^2, y_v=2q0*qv+qv^2, y_uv=2qu*qv. A purported Farkas
vector is checked against every column with >=0 and RHS<0. A PSD result remains
candidate exact congruence pending separate checking; it does not imply moments.

Optional SciPy locked HiGHS float64 feasibility has objective zero and retains
all rows/columns. Its time allocation is half the then-remaining deadline after
60 seconds for reconstruction/preservation. This is a pilot choice, not a cap on
future scientific methods. Raw solver status/message and returned floats are
saved as guidance only. Each float is reconstructed as a Fraction with denominator
at most 1,000,000; all nonnegativity and moments must hold exactly before a
candidate primal is saved. Failure/infeasibility/timeout without an exact dual
is UNKNOWN. An exact real/integer primal proves only necessary moment feasibility,
never graph completion. Numerical acceptance alone is never a certificate.

Raw contract: each case directory has model.json (EXTERIOR_NEIGHBOR_MOMENT_MODEL_V1,
target_order/target_degree/adjacent_cn/nonadjacent_cn/ordered_support_vertices,
induced_adjacency/H_squared/vertex_rhs/pair_deficits with null diagonal,
row_labels/right_hand_side/gram_matrix/universe_mask_range/eligible_type_count/
decision_counts), types.json (ordered records mask/coefficient), universe.json
(every ordered mask/decision), gram.json, optional primal.json (exact rational
string values aligned with types, integer Boolean) and numerical_guidance.json.
The summary binds all files separately from its own identity, all software pins,
actual command/context and honest execution status. No producer claim is VERIFIED.

Calibration builds the complete literal rook9 adjacency and checks all81 entries
of its SRG identity. Five ordered induced sets single[0], adjacent[0,1],
nonadjacent[0,4], row[0,1,2], diagonal[0,4,8] reconstruct exterior vertices and
the Structural handwritten counts, all masks/coefficients and exact integer
primal moments. Four Gram matrices exercise PSD, negative diagonal, indefinite
zero-diagonal block and all-zero matrix. Eight precise negatives are binary
bool/float, loop, asymmetry, negative/altered primal and wrong RHS/column Farkas
signs. These same-author controls do not independently validate their own model.
Native's separately authored checker needs genuine controls before expensive
scientific execution. Source-only scientific mode is the fixed seventeen-base
literal twelve triangles of f6f9e883, not combined-added-edge coverage.

Each invocation uses CommandDeadline before all source hashing/model arithmetic/
enumeration/LP/outputs, cooperative before/after 1MiB hashing and output saving,
and a 30 second preservation reserve. A final closing tick follows summary;
failure renames a provisional summary and preserves failure/raw artifacts.
This does not preempt blocking I/O or establish a realtime guarantee. Supported
Windows Job supervision before locked offline UV and an observed empty terminal
are required. New literal plans/source review/control outcomes are required;
this source authorizes no launch, ledger/index edit or target-level promotion.
