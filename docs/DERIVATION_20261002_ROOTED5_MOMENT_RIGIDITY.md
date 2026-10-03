# Explicit rooted five-flag rigidity and moment identities

Discovery status: **CANDIDATE**, pending independent verification of the raw
small count systems and exact arithmetic. This records an explicit target
instance of an established structural theorem, with no novelty claim.

For every `srg(99,14,1,2)`, the proposed statement is that every ordered edge
has the same specified 66-component vector of rooted five-vertex flag counts,
and every ordered nonedge has the same specified 87-component vector. Roots
are fixed pointwise, while each extension is an unordered free triple. The
explicit integer vectors are in
`acceleration/results/20261002_rooted5_moment_identity_binding/`.
They each sum to `binomial(97,3)=147440`.

This makes the archived pair-root moment identities stronger than PSD:

```text
M_edge    = 1386*c_edge*c_edge^T,
M_nonedge = 8316*c_nonedge*c_nonedge^T.
```

The two root populations count ordered roots. This statement assumes no
target automorphism, prism-free endpoint, six-prism support, or N3 value.
The order-eight integer endpoint aggregate already satisfies these proposed
equalities. Thus these equality constraints cannot alone exclude that
specific null vector. They do not assert an actual graph has been constructed.

## Established mathematical context

[Christian Pech, On highly regular strongly regular graphs](https://numdam.org/articles/10.5802/alco.183/),
Algebraic Combinatorics 4(5) (2021), 843--878, DOI 10.5802/alco.183,
[versioned journal PDF](https://www.numdam.org/item/10.5802/alco.183.pdf),
accessed 2026-10-02 JST, gives this general regularity phenomenon for partial
quadrangles in Theorem 5.7, printed page 868. Theorem 5.5 on printed page 867
characterizes their SRG point graphs by excluding an induced `K4-e`.
For the target, `lambda=1` immediately excludes that induced configuration:
its middle edge would have two common neighbors. Equivalently, take the
graph-triangles as lines to obtain a partial quadrangle of parameters
`(s,t,mu)=(2,6,2)`.

This source supports root-independent five-vertex extension counts. It does
not supply the explicit 153 target-coordinate values computed here, and does
not resolve Conway-99. No full audit of all claims in Pech's paper is asserted.

## Complete finite model

The producer `acceleration/theory_20261002_rooted5_flag_rigidity.py` imports
neither archived discovery code nor class data. For each root relation it
enumerates every simple edge mask through order five with roots `0,1` fixed,
filters induced adjacent/common-neighbor caps one/two, and canonically identifies
only permutations of the free vertices. Bit positions enumerate increasing
unordered vertex pairs lexicographically. The smaller bases are complete by
direct exhaustion of all at most 1,024 labelled five-vertex masks.

The variable populations by order two through five are:

```text
ordered edge:    1,4,16,66, total87.
ordered nonedge: 1,4,19,87, total111.
```

At a fixed actual root, the variable for flagged class `H` counts unordered
`|H|-2` subsets of the remaining 97 vertices. Thus its total at each order is
`binomial(97,|H|-2)`.

For every flagged class of order two through four, use all vertex orbits and
unordered-pair orbits under automorphisms of that class fixing both roots
pointwise. Include the two root vertices as singleton marked orbits and their
pair as a pair mark. Count extensions by one outside vertex exactly as in the
unrooted marked-extension derivation:

- Deletion coefficient on `H` is `99-|H|`.
- A vertex-orbit coefficient on `H` sums `14-deg_H(u)` over its marks.
- A pair-orbit coefficient sums prescribed common neighbors minus those
  already inside `H`, using one on an edge and two on a nonedge.

On a larger flagged class `K`, delete only a free vertex. The coefficient is
one, the number of marked vertices adjacent to that deleted vertex, or the
number of marked pairs whose two vertices are both adjacent to it. Translating
the remainder to the canonical small flag changes an orbit only within the
allowed fixed-root automorphism group. Hence every actual target root supplies
a solution to these exact integer equations. No graph automorphism is assumed.

## Exact arithmetic candidate results

The raw models, complete sparse rows, variable/mask maps, and explicit rational
solutions are saved at `acceleration/results/20261002_rooted5_flag_rigidity/`.
The ordered-edge system has 194 rows and 87 columns; exact Fraction elimination
finds rank 87. The ordered-nonedge system has 224 rows and 111 columns; exact
elimination finds rank 111. Both are consistent and have unique solutions.
Every saved solution entry is replayed in every original row by the producer.
The extracted five-flag entries are nonnegative integers.

An independent reviewer can efficiently establish full rational rank by
computing full column rank modulo a prime, then verify the explicit rational
solution in every integer row. Modular rank equal to the number of columns
gives the rational full-rank lower bound; the independent reviewer must compute
it rather than trust the producer's rank field.

The basis-binding producer compares every one of the 153 raw flag masks and
values against the archived Wave147 bases and the endpoint rank-one certificate
vectors. All agree: `c_edge=2*u`, `c_nonedge=v`, with the endpoint certificates
`M_edge=5544*u*u^T` and `M_nonedge=8316*v*v^T`. The raw binding outputs include
the full proposed universal moment matrices for direct comparison.

At a fixed root theta let `c(theta)` count free triples. The archived exact
moment coefficient convention gives `M=sum_theta c(theta)c(theta)^T`. Unique
solutions make `c(theta)` constant for all ordered roots of a given relation.
There are `99*14=1386` ordered edges and `99*84=8316` ordered nonedges, producing
the stated exact moment equalities.

These calculations and their mathematical transport still require independent
checking before a root-ledger promotion. RREF files are raw outputs, not a
proof of correctness by themselves.

## Controls and implications

The producer directly counts all relevant flags in the known nine-vertex rook
SRG at one ordered edge and one ordered nonedge. Both corresponding `n=9,k=4`
models pass every equation. A deliberately changed root-count coordinate is
rejected for each relation. These are producer controls and do not approve the
new target claim.

The preceding exact local screen passed twenty selected elementary cardinality
tests on the two endpoint vectors. Passing those tests does not prove a local
root realization; the new complete linear systems explain why those particular
counts match necessary identities.

The smallest pair-root flags that can have genuinely variable counts therefore
need at least four free vertices, so their products may extend to order ten.
A three-root/three-free-vertex family reaches rooted order six and union order
nine. These are candidate next models, not executed completeness or exclusion
claims. Extra global compatibility is necessary: this wave's frozen order-eight
linear-plus-PSD relaxation has an exact feasible endpoint null vector.
