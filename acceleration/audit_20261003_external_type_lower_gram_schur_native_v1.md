# Independent written review of the corrected exterior Schur conditions

Reviewer: `/root/native_driver`. Discovery of the exterior-type direction was
`/root`; the corrected derivation and the separate one-type redundancy candidate
are by `/root/structural`. This review reconstructs both implications separately.
It finds no material mathematical veto within the stated hypotheses. It is a
written derivation, with no inverse calculation, type/pair enumeration, imported
producer, executed fixture, numerical spectrum, solver or formal proof checker.
It does not authorize a future computation or change a ledger entry.

The reviewed paper is
`docs/CANDIDATE_20261003_EXTERNAL_TYPE_LOWER_GRAM_SCHUR_V1.md`, SHA256
`44a382f4996d4887bed8d4eb8122dc8dee9876af55d267c1a84eaff85006cd04`.
Its complete candidate record is
`acceleration/results/20261003_external_type_lower_gram_schur_candidate01.json`,
SHA256 `9a8f2a2b50b8e409bda0147353514a32428fe8f40deb38b332564db572055dfb`.

## 1. Reconstruct the target Gram and the exact rank

In a hypothetical simple (99,14,1,2) graph, the diagonal of A squared is 14,
its entries on edges are 1, and its entries off edges and off the diagonal
are 2. Therefore A squared plus A equals 12I plus 2J. Regularity makes the
all-ones line invariant, with eigenvalue 14. Symmetry makes its orthogonal
complement invariant. On that complement the polynomial is x squared plus
x minus 12, so the only eigenvalues are 3 and minus 4. Their multiplicities
f,g satisfy f+g=98 and 14+3f-4g=0, giving f=54,g=44. This argument does not
assume connectedness or a target automorphism: another eigenvector of
eigenvalue 14 orthogonal to the all-ones vector would violate that polynomial.

Consequently A+4I is positive semidefinite of rank 55. The original shift
A+3I has 44 negative eigenvalues, each minus one. The erroneous full-target
shift-three proposal is preserved as an error; local positivity of some
selected H+3I cannot rescue it. This rank55 is over the real numbers for the
complete target Gram. It is not a rank55 assertion about a point-triangle
incidence matrix, a finite-field matrix, or a selected subgraph.

## 2. Independent block quadratic-form argument

Let U have m vertices, H be the complete induced adjacency A[U,U], and
K=H+4I be positive definite. Let T contain the literal binary neighborhood
columns of the vertices outside U, and put C=4I+A_out. For all real x,y,

    x^T K x + 2x^T T y + y^T C y
      = (x+K^-1 T y)^T K (x+K^-1 T y)
        + y^T (C-T^T K^-1 T) y.

The change of variables is invertible. Thus the full Gram is congruent to
diag(K,S), where S=C-T^T K^-1 T. Positive semidefiniteness of the full Gram
implies S positive semidefinite, and rank additivity gives rank(S)=55-m.
In particular the hypotheses cannot occur with m>55. For m=17, S has 82
rows and rank 38. This is a necessary consequence of a hypothetical target,
not a rank certificate for a saved relaxation or a partial exterior graph.

For one exterior vertex with type t, its diagonal entry in S is 4-q(t),
where q(t)=t^T K^-1 t. For two distinct exterior vertices with types t,u
and actual adjacency a in {0,1}, their principal block is

    [4-q(t),       a-t^T K^-1 u]
    [a-t^T K^-1 u, 4-q(u)      ].

A real symmetric two-by-two matrix is positive semidefinite exactly when
both diagonal entries and its determinant are nonnegative. This gives
the two individual q<=4 conditions and the stated squared inequality.
Two distinct vertices with the same type are included: equality of their
columns does not turn their off-diagonal entry into a diagonal entry. If
both choices of a fail they cannot coexist; if one passes, that adjacency
is forced conditionally. Equality is admissible, and a zero diagonal
slack forces the off-diagonal Schur entry to vanish.

These one- and two-vertex tests alone do not prove whole-matrix positivity.
For example, a three-by-three matrix with diagonal 1 and every off-diagonal
entry minus 9/10 has positive two-by-two determinants but has quadratic
form minus 12/5 on the all-ones vector. This is a written boundary example,
not an assertion that this matrix is a target Schur complement. Pair tests
also do not impose the global rank, binary exterior completion or integrality.

The induced and positive-definite hypotheses cannot be dropped. If edges
inside U are omitted, the displayed block is no longer the principal block
of A+4I. For singular positive semidefinite K, a full positive semidefinite
block first forces T into range(K): a vector in ker(K), paired with a
variable exterior coordinate, otherwise makes the quadratic form have both
signs. Only after that condition may a generalized inverse be used. That
case is outside this reviewed positive-definite statement.

## 3. A variational proof of the strict one-type redundancy

For the exact linear selected-triangle edge union, let B0 be the ordinary
binary point-by-triangle incidence. Linearity gives off-diagonal entries of
B0 B0^T equal to H, and its diagonal is the selected incidence degree d.
The two centers have d=3 and the other fifteen points have d=2; hence

    K = H+4I = B0 B0^T + D,
    D = diag(1 at the two centers, 2 elsewhere).

This immediately proves K positive definite. Independently of the paper's
Woodbury identity, completing a square gives, for any real t,

    t^T K^-1 t = max_y (2t^T y-y^T K y).

Removing the nonnegative term ||B0^T y|| squared bounds this maximum by
t^T D^-1 t. Equality could occur only at the unique maximizer of the
D-form, namely y=D^-1 t, and would additionally require B0^T D^-1 t=0.
Every point belongs to a selected triangle. Thus for nonempty nonnegative
binary t, some column of B0 has positive dot product with D^-1 t, so the
last requirement fails. The inequality is strict. If t has k ones and c
of them are centers, the upper bound is (k+c)/2. Empty t has q=0.

To obtain the target-type restrictions, suppose this exact H is induced
in the target. Every H edge already has its unique common neighbor in H;
an exterior vertex cannot be adjacent to both endpoints without giving
that edge a second common neighbor. Thus its type is independent in H.
The centers are adjacent, so c<=1. The target graph induced on the fourteen
neighbors of any vertex is one-regular: for each neighbor u, the degree
of u within that neighborhood is precisely CN(x,u)=1. It is therefore
seven disjoint edges. An independent subset has k<=7. Consequently

    nonempty t: q(t) < (k+c)/2 <= 4;
    empty t:    q(t) = 0.

More generally the strict inequality holds for every nonempty nonnegative
binary t under the incidence hypotheses, whether or not it is a valid
target type; the final <=4 uses the stated k,c bounds. Signed vectors may
have cancellation and are outside the strictness assertion. Nothing here
evaluates the saved 472 types or shows the pair-type test redundant. Added
induced edges change K and the incidence decomposition, so the argument
is not silently extended to an edge-added graph or an arbitrary 17-set.

## 4. Falsification boundaries, provenance and archive overlap

The independent checks were: the target polynomial and multiplicities;
the negative shift-three eigenspace; exclusion of an extra eigenvalue14;
real rank versus incidence/GF(3) rank; inducedness; positive definiteness
and m<=55; singular range requirement; distinct same-type vertices;
zero diagonal slack and equality; pairwise versus full positivity/rank;
empty type; nonempty variational strictness; need for nonnegative t;
adjacent centers; and the capacity bound from the actual matching.
These are fifteen written checks, with zero executable control cases.

The following complete archive sources were read as documents/source, not
imported or run: target modular-rank audit c819ec; triangle39 Gram/SOS
derivation 1dead1; closed28 Schur-redundancy theory 2b998e; rook-orbit Gram
checker 5c66e7; exterior-moment paper 70ef63; and the original seventeen-point
circuit note f6f9e8. Exact hashes are retained in the accompanying report.
The target shift4/rank55 and Schur mechanism overlap these archives; this
review does not claim they are novel or exhaustively search prior work.
The selected-base one-type redundancy is the separately stated consequence.

The paper's sentence about 5184 producer data awaiting full replay is a
historical status sentence. The later different-source full family check
has since completed, but no family data are needed by either derivation
above, and no paper bytes were edited to update that sentence. This review
does not establish the four isomorphism classes, target occurrence of a
base, an induced embedding, target feasibility or nonexistence. No fixed
type universe, inverse, pair population or new execution gate is approved.
