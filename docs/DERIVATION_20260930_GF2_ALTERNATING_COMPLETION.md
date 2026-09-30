# Binary alternating residual completion and a block-rank diagnostic

Status: CANDIDATE. These are written algebraic derivations with finite calibration,
not an independent review, a new target graph, or a nonexistence result.

## 1. Prior work and scope

The target binary identity A²=A and rank(A)=54 are already established in
`AUDIT_20260930_TARGET_MODULAR_RANKS.md`. The archive at commit
85e705cc6c2a14d123120c93a847e30aaab1789e contains the projection/code discussion in
Wave102 §1, Wave131 §1, Wave142 §§1–2, and Wave140 §3. Wave140 explicitly supplies
binary projection controls that are not adjacency matrices. None of those labels
is treated here as fresh independent approval.

The current triangle mixed-equation kernel criterion and its maximal-rank
sufficient case are in `AUDIT_20260930_TRIANGLE_GF2_MAXRANK.md` and
`AUDIT_20260930_FIVE_CORE_MODULAR_GRAM.md`. The complete integer residual equations
are in `AUDIT_20260930_TRIANGLE_RESIDUAL60.md`. The clarification below concerns
only the linear binary mixed equation. It does not classify idempotent completions.

## 2. Exact alternating-completion criterion

All algebra in this section is over F2. Let F,H be a-by-m matrices. There exists
an alternating m-by-m matrix D (symmetric and zero diagonal) with FD=H if and only
if

* ker(F^T) is contained in ker(H^T); and
* FH^T is symmetric and has zero diagonal.

Necessity follows by transposing FD=H and writing FH^T=FDF^T. For sufficiency,
put W=im(F^T). The first condition makes T(F^T x)=H^T x a well-defined map
W to F2^m. Prescribe b(u,w)=u^T T(w) for u in F2^m and w in W. On W-by-W this
is alternating and symmetric precisely by the second condition. Choose a basis
of W and extend it to a basis of F2^m. The prescribed columns determine their
transposed rows consistently; choose the remaining complementary block to be
zero. Transform this alternating bilinear form back to the standard basis. Its
matrix D satisfies DF^T=H^T, hence FD=H. This proves existence without any
generic-rank or unimodularity assumption.

To additionally require D j=0 for j the all-one m-vector, the exact extra
conditions are H j=0 and, if j=F^T x has a solution, H^T x=0. The latter is
independent of the chosen x by the kernel condition. Necessity is immediate.
For sufficiency, if j is already in W its prescribed image must vanish; otherwise
extend the prescription by T(j)=0. Its cross terms with W are consistent because
j^T H^T=0. Apply the same alternating-form extension to W+span(j).

This last condition can add information for generic matrices. For example,
F=H has rows 1100 and 0011. Alternating D exists (edges 01 and 23), but no such D
has D j=0: j is the sum of the two F rows and its prescribed image is j. This
example is not claimed to satisfy any triangle Gram identity.

## 3. Symmetry and zero diagonal add no linear obstruction for valid factors

Let n be even and C be a simple undirected cubic scaffold on three n-cells, with
exactly one neighbor in each cell. Let U be the block diagonal matrix of three
all-one n-by-n blocks. An actual triangle incidence factor satisfies, over the
integers,

    FF^T = G = nI - C - C² + 2J - U.

No special equality among the matchings or permutation P is assumed. Over F2,
G=C+C²+U and H=(I+C)F. Because CU=UC=J and CJ=JC=3J, C commutes with G.
Consequently FH^T=G(I+C) is symmetric. Its diagonal vanishes: diag(G)=0,
whereas GC=C²+C³+J has diagonal 1+0+1=0. Here each diagonal entry of C³ counts
twice the triangles through a vertex. Therefore an alternating binary residual
D solving FD=H exists exactly when the already known kernel condition holds.

For the intended factors F j=(n-2)j=0, so H j=0 automatically. Even residual
degree consequently reduces to the single well-defined test from §2 concerning
preimages of the all-one outside vector. It is not asserted here to be automatic
for all valid triangle factors or to yield an actual new target obstruction.
The integer D²+F^TF identity, exact degrees, and entrywise common-neighbor counts
remain additional requirements. No D completion is constructed for Conway99.

## 4. Symmetric block-rank lower bound

Let A=[[B,E],[E^T,D]], with B,D symmetric. Write r=rank(B), s=rank([B,E]),
q=s-r. By an invertible simultaneous row/column basis change, B becomes an
invertible r-block followed by zero. Eliminate the E part adjoining that block.
The remaining off-diagonal block adjoining ker(B) has rank q. Its row and column
spaces contribute a nonsingular 2q-by-2q block: after reducing that rectangular
block to an identity, the principal block has shape [[0,I],[I,X]], which is
nonsingular. Thus rank(A)>=r+2q=2s-r, irrespective of D. The contribution r is
separate because its block has already been eliminated. This yields the target
necessary inequality 2s-r<=54, without equating binary and real ranks.

For the triangle partition write

    B = [[J3-I3,R^T],[R,C]],   E = [[0],[F]],

where R has the three cell indicator columns. If n is even and every F column
meets each cell twice, the three independent vectors (j3,r_i) are annihilated by
B and by E^T. Indeed C r_i=j, R^T r_i=0, and F^T r_i=0. Hence s<=3n. When n=12
and r>=18 the lower-bound test is automatically satisfied, since 2s-r<=72-r<=54.
The hypothesis r>=18 has not been established for all admissible triangle cores.
The six-K3,3 scaffold is deliberately tested separately and fails local SRG pair
caps. It must not be used as an admissible-core example.

The positive243 control has its own parameters and binary target rank110. Saved
annealer objects fail full Gram and are only local-domain diagnostics. No finite
rank population in the accompanying run establishes a universal lower bound.
