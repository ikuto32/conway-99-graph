# Exterior-neighborhood moments for a fixed seventeen-point induced base

Status: **CANDIDATE**, source-only derivation and finite-control design by
`/root/structural`, written 2026-10-03T15:20:29+00:00. The moment question
originated with `/root`; the neighborhood-matching refinement below is a
separately stated derivation. No type enumeration, solver, executable fixture,
formal checker or external review has run for this note. No result about
feasibility, extension, forced occurrence, target existence or nonexistence is
claimed. Novelty and historical overlap beyond the cited anchor budget are
UNKNOWN. No ledger, index, existing source or historical artifact is changed.

## 1. Exact hypothesis and the fixed finite input

Let G be a hypothetical simple graph with parameters (99,14,1,2): every vertex
has degree 14, adjacent pairs have one common neighbor and nonadjacent pairs
have two. Let S be a specified set of 17 vertices, and let H=G[S] be its
**complete induced adjacency** on those ordered vertices. Write d_v for its
ordinary graph degree and c_uv=(H^2)_uv for its integer internal common-neighbor
count. Define, for distinct u,v in S,

```
b_v = 14 - d_v,
delta_uv = 2 - H_uv - c_uv,
N = 99 - 17 = 82.
```

An input with a negative b_v or delta_uv cannot be this induced subgraph.
Symmetry, binary entries and zero diagonal must also be checked literally.
There is no GF(2)/GF(3) rank assumption, selected-word minimality assumption,
automorphism assumption or historical upper-rank premise in this implication.

The particular base is the graph containing exactly the edges of the twelve
triples in
`CANDIDATE_20261003_SEVENTEEN_POINT_UNBALANCED_TWELVE_TRIANGLE_CIRCUIT_V1.md`,
SHA256 `f6f9e883b577d6969eafaac9239c37d637804786a08a6b5e676cebe0208e576b`:

```
(0,1,2), (0,3,4), (0,5,6), (1,7,9), (1,8,10), (15,11,14), (16,12,13),
(2,15,16), (3,7,11), (4,8,12), (5,9,13), (6,10,14).
```

ROOT independently checked the finite graph, all 289 integer products and its
base/single-added-edge anchor budgets. Its written audit is
`acceleration/audit_20261003_seventeen_point_circuit_root_v1.md`, SHA256
`812b4a825941e952eaa8131072cb0d5a5fb2ae6ee52d0336f4683dce0c761e5e`;
the actual acceptance record is
`acceleration/results/20261003_seventeen_point_circuit_root_actual_acceptance01.json`,
SHA256 `0c2abf39f87d9eb02d853e2ea90ab2f0f2a031cb7818047c83d1b64cc6b4cc90`.
Those checks do not establish a 99-vertex completion or combined-added-edge
coverage. This new model has not been executed or independently verified.

## 2. Pair-type relaxation and its exact necessary moments

For an exterior vertex z, put T_z=N_G(z) intersect S. If u,v are both in T_z,
z is an exterior common neighbor of that pair. Therefore delta_uv>0. Define
U_pair to be **every** subset T of S for which each distinct pair in T has
delta_uv>0, also requiring |T|<=14. Empty and singleton types are retained.
For a target extension set

```
x_T = number of exterior vertices z with T_z = T.
```

Then x_T are nonnegative integers, with the complete equations

```
sum_T x_T = 82,
sum_{T containing v} x_T = b_v                 (each of 17 vertices),
sum_{T containing u,v} x_T = delta_uv           (each of 136 unordered pairs).
```

The first equation counts exterior vertices; the second counts edges from a
fixed vertex of S to the exterior; the third counts its pair's exterior common
neighbors. These arguments count all exterior vertices, including those with
no neighbors in S. Dropping the empty type or replacing 82 with the cut-edge
count changes the question.

This is a necessary relaxation. Pairwise eligibility does not prove that a
type occurs, and moment feasibility does not construct the exterior graph.
Edges among exterior vertices, their remaining degrees and their own pair and
cross-pair common-neighbor equations are absent.

For the particular base, d_0=d_1=6 and the other fifteen degrees are four.
Thus b_0=b_1=8 and the other demands are ten. Its exact aggregate budgets are

```
sum_v b_v = 166,
sum_{u<v} delta_uv = 116,
sum_T |T| x_T = 166,
sum_T binomial(|T|,2) x_T = 116.
```

The aggregate identities are consequences of the full 154-row moment system;
they are not replacements for its individual vertex/pair rows. In particular
the anchor budget already checked by ROOT can pass while the finer system
remains untested.

## 3. A separately declared stronger type restriction

For any vertex z of a (99,14,1,2) target, G[N_G(z)] is exactly seven disjoint
edges. Indeed, every v in N_G(z) has exactly one neighbor inside N_G(z), by
the common-neighbor requirement for the edge zv. Its fourteen vertices form
a simple 1-regular graph.

Consequently H[T_z] is a matching. If t=|T_z| and e is its edge count, it
occupies t-e distinct edges of that seven-edge neighborhood, so

```
maximum_degree(H[T_z]) <= 1,
|T_z| - edge_count(H[T_z]) <= 7.
```

Define U_match by these two additional exact conditions within U_pair. The
same 154 moment rows are necessary using U_match. This is still a relaxation,
not a sufficient characterization of exterior types or target completion.

In the original base every edge has its unique common neighbor already inside
S. Its delta is zero, so no pair-type T contains a base edge. Thus H[T] is
independent and the matching bound reduces to |T|<=7 for that base. This last
simplification must **not** be copied to arbitrary edge-added versions.

Pair positivity alone does not imply the matching bound: the three vertices
(0,0),(0,1),(1,1) in the 3 by 3 rook graph induce a path, with all three pair
deficits positive relative to that subgraph, but no exterior vertex can be
adjacent to all three. The middle vertex would give two common neighbors to
its edge with that exterior vertex. This is a written counterattack, not an
executed fixture.

## 4. Combined additions and scope

If some extra edges F on these 17 points are contemplated, the proposed
induced graph is H_F=H union F. Recompute **all** d_v, H_F^2 and delta_uv from
H_F, then construct its own U_pair or U_match and its own moment right-hand
side. A negative deficit rejects that exact H_F. A new edge with internal
CN zero can have delta one and need not prohibit its endpoints sharing an
exterior neighbor; original-base prohibitions cannot be carried over blindly.

ROOT's prior finite audit identified 24 original CN-zero possible individual
added edges, tested only the base and those single-edge cases, and disclosed
that all combined-addition cases were untested. This note does not enumerate
their subsets, assume independent compatibility, identify them up to symmetry
or exclude any of them. Any conclusion obtained for F=empty would concern
only the original induced base, not an arbitrary non-induced occurrence of
the twelve selected triangles. To cover that occurrence, every compatible
induced supergraph would need its own justified coverage.

## 5. Literal exact model and certificate contract for future implementation

Use masks 0 through 2^17-1 on the fixed point order, retaining each eligible
mask once in increasing order. Retain all 154 rows in order: total, vertices
0..16, then lexicographic unordered pairs. Matrix entries are literal 0 or 1:
the corresponding type contains the row's point(s). In particular all
zero-deficit pair rows remain explicit, with zero coefficients and RHS zero.
All masks, the exact induced matrix/product/deficit tables, eligibility
reasons, row/column labels, exact coefficient matrix and RHS must be saved.
No validated column count is asserted before such enumeration.

An infeasibility certificate may be a rational vector y of length 154 with

```
each type-column a_T satisfies a_T dot y >= 0,
right_hand_side dot y < 0.
```

If x>=0 solves Ax=r, these inequalities contradict y dot r=sum_T x_T(a_T dot
y)>=0. This exact sign convention must be independently checked against
every saved and independently rebuilt type, coefficient and right-hand-side
entry. Floating solver status or rounded dual agreement is insufficient.

A nonnegative exact rational primal x proves only feasibility of this real
relaxation. A nonnegative integer primal proves only this system's integer
moment feasibility; neither proves graph extension. No optimizer or solver
is authorized by this note. A future invocation needs a frozen source,
applicable positive/corrupt controls, independent verifier, evidence-based
allocation and supported inclusive supervisor.

There is also a source-only cheap Gram consequence. With b as a column and
D diagonal b_v and off-diagonal delta_uv,

```
D = 12I + 2J - H - H^2,
Z = [[82, b^T], [b, D]] = sum_T x_T [1;1_T][1;1_T]^T.
```

Hence Z must be positive semidefinite, even for real x>=0. A rational vector
q with q^T Z q<0 would give the displayed Farkas convention by expanding
(q_0+sum_{v in T}q_v)^2: y_total=q_0^2,
y_v=2q_0 q_v+q_v^2 and y_uv=2q_u q_v. This is an exact certificate design,
not an assertion that such a vector exists for the base. No eigenvalue or
congruence computation has been performed here.

## 6. Handwritten calibration population for a future source

Use the literal 3 by 3 rook graph on (row,column) in {0,1,2}^2, parameters
(9,4,1,2). For these generic controls replace 82 by 9-|S|, degree 14 by four,
and neighborhood capacity seven by two; keep the same counting derivation.
The following five positive moments are explicit source-only expectations.

| S | Nonzero type multiplicities |
| --- | --- |
| One vertex (0,0) | empty 4; its singleton 4 |
| Adjacent pair (0,0),(0,1) | empty 2; each singleton 2; the pair 1 |
| Nonadjacent pair (0,0),(1,1) | empty 1; each singleton 2; the pair 2 |
| Complete row (0,0),(0,1),(0,2) | each singleton 2 |
| Diagonal (0,0),(1,1),(2,2) | each of the three pairs 2 |

A separate implementation must reconstruct the full rook adjacency, induced
matrices and literal exterior subsets and verify every row, rather than
accepting these counts by agreement. Planned corrupt tests must include:
omitted empty type; omitted eligible pair type; duplicate mask; bool/float
mask or coefficient; wrong diagonal product; sign-swapped deficit; shifted
point ordering; missing zero-deficit row; negative or fractional purported
integer primal; one altered moment; wrong Farkas sign; missing type-column
inequality; and applying the independent-type |T|<=7 simplification to a
general incomplete-edge base. The path example in section 3 tests matching
eligibility separately from the intentionally weaker pair-type relaxation.

These are proposals, with zero actual executable positives or corrupt
controls completed. This note supplies no mathematical or engineering gate.
