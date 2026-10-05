# Independent written audit of the dual-Gram exterior-type candidate

The reviewed candidate is `docs/CANDIDATE_20261003_DUAL_GRAM_EXTERIOR_TYPE_COMPATIBILITY_V1.md`, SHA256 `e07f78d1820d1fcedc87d859c3715c8e8321fa44e49fc9a1f06bf0ffe4814c05`, claim `C-TARGET-DUAL-GRAM-EXTERIOR-TYPE-COMPATIBILITY`, revision 1. Root proposed the direction and Structural wrote the candidate. Native independently reconstructs the identities and inequalities below. The earlier lower-Schur archive, including Native's own written derivation, is shared provenance; this audit is not a claim of independent discovery, external review, or novelty.

No mathematical program, matrix inversion, numerical spectrum, type enumeration, import, solver, formal proof, or actual 472-type inspection was used. File reading and saving this audit are metadata operations. There is no approval of a future implementation or of a target completion.

## Reconstruction of both complete target Grams

Assume the exact finite simple target has adjacency matrix A, with A squared equal to 12I minus A plus 2J and A times the all-one vector equal to 14 times that vector. Symmetry gives AJ=JA=14J; J squared is 99J.

Put G=27I-9A+J. Direct expansion gives

    G squared = 1701I - 567A + 63J = 63G.

In detail the I coefficient is 729+972=1701, the A coefficient is -486-81=-567, and the J coefficient is 162+54-252+99=63. Hence G/63 is a symmetric idempotent. It is an orthogonal projector, so G is PSD and its rank is its trace divided by 63: (27*99+99)/63=44. Therefore the upper Gram M=G/9=3I-A+J/9 is PSD of rank 44, with diagonal 28/9 and distinct-vertex entries 1/9-A_uv. Neither diagonal 3 nor shift A+3I can replace these expressions.

For L=A+4I, direct expansion gives L squared = 28I+7A+2J = 7L+2J, and L times the all-one vector equals 18 times that vector. Put R=L-(2/11)J. Then R annihilates the all-one vector. Its squared J correction is 2-72/11+36/11=-14/11, so R squared = 7R. The symmetric idempotent R/7 is PSD. Its trace is 396-18=378, so its rank is 54. The image of R is perpendicular to the all-one line. Adding (2/11)J supplies a positive rank-one operator on that line; L is consequently PSD of rank 55. This reconstructs the lower rank without using a withdrawn rank claim about incidence matrices.

## Exact Schur blocks and ranks

Let S be an arbitrary subset of m target vertices and H the literal induced adjacency A[S,S]. For an outside vertex x, let t be its binary adjacency column on S. The restricted upper Gram column is b_t=(1/9)1-t; the restricted lower column is t. These follow from the complete Gram entries, not from a triangle support encoding.

For a symmetric block matrix [U B; B transpose D] with U positive definite, invertible block elimination gives a congruence to diag(U,D-B transpose U inverse B). The exterior Schur block is therefore PSD and its rank is the full Gram rank minus m. Applied separately to the upper and lower Grams, the ranks are 44-m and 55-m. The assumptions already force m<=44 and m<=55 respectively; a negative claimed residual rank does not occur under the hypotheses. For m=17 the ranks are 27 and 38. These statements concern the entire exterior block, not a rank deduced from pair tests.

The upper diagonal for type t is r_t=28/9-b_t transpose U inverse b_t. For distinct outside vertices x and y with actual adjacency a=A_xy, the upper off-diagonal is 1/9-a-b_t transpose U inverse b_u. PSD of that 2-by-2 principal block gives r_t,r_u>=0 and the stated squared inequality. The lower diagonal is 4-t transpose K inverse t, with K=H+4I; its off-diagonal is a-t transpose K inverse u. The signs and the same literal bit a in both blocks are essential. Trying an upper bit and a different lower bit would not certify compatibility of one pair of vertices.

Each inverse is rational when its integer/rational matrix is invertible: the adjugate formula suffices. No floating threshold or numerical PD hypothesis is needed or accepted here. Singular principal blocks are outside this candidate; a pseudoinverse without a range condition is not an extension proved by this audit.

## Equal types refer to distinct exterior vertices

Writing q=b_t transpose U inverse b_t, a nonadjacent equal-type pair has determinant

    (28/9-q)^2 - (1/9-q)^2 = 29/3 - 6q.

Thus its condition is q<=29/18, together with the singleton diagonal condition. An adjacent equal-type pair has determinant

    (28/9-q)^2 - (8/9+q)^2 = 80/9 - 8q,

giving q<=10/9. The equality endpoints are included. Hence q>29/18 forbids two copies; 10/9<q<=29/18 leaves only the nonadjacent bit from the upper test. Values above pair thresholds can still permit a single vertex through q<=28/9; no diagonal entry is misidentified as a distinct equal-type pair.

For l=t transpose K inverse t, the lower equal-type determinants are 16-8l for a=0 and 15-6l for a=1. They give l<=2 and l<=5/2. Therefore l>5/2 forbids two copies and 2<l<=5/2 leaves only adjacency. Upper, lower, and target common-neighbor restrictions must all hold for the same pair. For example, an upper-forced nonedge combined with a lower-forced edge means no compatible pair, rather than permission to choose the bits independently.

If a residual diagonal is zero, the 2-by-2 determinant forces its off-diagonal with every other exterior vertex to vanish. This includes the exact boundary; an approximate zero does not establish that conclusion.

## Common neighbors, applicability, and sufficiency boundary

For two distinct outside vertices, the intersection of their literal types is a subset of their actual common neighbors. Thus its size is at most 1 if a=1 and at most 2 if a=0. There is no converse and no assumption that this inside-S count is the complete common-neighbor count. In the candidate's sentence about an empty or singleton intersection forcing compatibility, “intersection” must mean the intersection of allowed adjacency-bit sets. An empty intersection of the vertex supports themselves does not forbid coexistence.

The fixed17 application needs its exact authenticated induced H, plus both separate positive-definiteness hypotheses. It cannot borrow the PD of a repaired class-I graph for a class-IV base. For a literal edge union of selected distinct target triangles with selected point degrees 2 or 3, the selected incidence C satisfies C C transpose = H+diag(d_v), since the target adjacent-CN=1 condition prevents a selected edge from belonging to two different triangles. Consequently H+4I=C C transpose+diag(4-d_v) is positive definite. Extra edges break that literal off-diagonal identity and require a separate matrix argument. The candidate makes this limitation explicit.

Pairwise PSD is insufficient: a 3-by-3 matrix with diagonal 1 and every off-diagonal -3/4 has each pair determinant 1-9/16=7/16>0, yet its all-one quadratic is 3-6*(3/4)=-3/2. This generic matrix is not asserted to be a target Schur matrix or a graph countermodel. It demonstrates only why the full exterior PSD and rank remain necessary beyond pair predicates.

The formulas, four equality thresholds, ranks, and conditional scope survive this written falsification pass. No actual type, pair count, inverse, pruning rate, fixed-base identification, rational completion, or target result is established. Future artifact verification must independently check the actual authenticated matrices and types and expose any computational failure; this paper audit grants no old-gate transfer.
