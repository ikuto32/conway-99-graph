# Independent restricted-design and complement-pairing audit

Let the 36 inner vertices be `(g,a,b)`, where `g` is one of three fibres,
`a` is one of six components, and `b` is a bit. Within each fibre the
matching flips b; between fibres identity matchings preserve `(a,b)`.
Thus the inner graph C is six triangular prisms. Put

`K = 12I - C - C^2 + 2J - diag(J12,J12,J12)`.

The statements here concern binary 36-by-60 incidence matrices F satisfying
the necessary target conditions `FF^T=K`, row sums ten and two ones per
fibre per column. They do not assert that every target contains this core.
No target automorphism is assumed.

## 1. Literal component and bit counts

For each component indicator u_a, a direct multiplication gives
`K(u_a-u_0)=0`. Consequently `FF^T=K` implies
`||F^T(u_a-u_0)||^2=0`: each column meets every component equally.
The column weight is six, so every column chooses exactly one of the six
vertices of each component. Its cell and bit labels are therefore defined.

For different components a,c, direct multiplication of C gives

`K[(g,a,b),(h,c,d)] = 1 if g=h, and 2 if g!=h`,

for every pair of bits b,d. Summing over the nine ordered fibre pairs gives
`3*1+6*2=15`. Because there is exactly one selected row in each component,
this is precisely the number of columns with component bits `(b,d)`.
Each of the four bit combinations therefore occurs fifteen times. Each
individual component bit is balanced thirty/thirty, also directly from the
three row sums ten for either bit.

## 2. The broader pairing obstruction

Suppose the sixty columns can be partitioned into thirty pairs preserving
the six selected cell labels and complementing all six component bits.
Choose either representative from every pair. For any distinct components,
their full-column Hamming distance is `15+15=30`. Complementing both bits
preserves their inequality, so their representative words of length thirty
have Hamming distance fifteen.

Take any three component words x,y,z. At each coordinate, either all three
bits agree or exactly two of the three pairs disagree. Hence

`d(x,y)+d(y,z)+d(z,x)` is even.

The required value is `15+15+15=45`, a contradiction. Thus no qualifying F
admits the stated pairing, regardless of its cell-pattern selection.
Cell preservation is not used in the final parity step; the reviewed claim
retains it as part of the proposed construction restriction. The argument
excludes a restriction on F, not the six-prism core or unrestricted target.

## 3. The narrower five-matching formula

The producer chooses the five round-robin perfect matchings partitioning
the edges of K6. Each is assigned all six orders of the three cell labels,
giving thirty patterns, each with two components in every cell. For each
pattern choose a bit vector and its full complement. Orienting the pair
so component zero has bit zero loses no paired design. There are 150 free
bits and 300 XOR extension variables, hence 450 variables in total.

Each component occurs in each cell ten times across the thirty patterns.
The complementary columns then make every row have sum ten and every
column contain two vertices in each cell. Within a component distinct rows
are disjoint, as prescribed by K. For different components and ordered
cells `(g,h)`, exactly two patterns occur if `g=h`, and four if `g!=h`.
One pattern pair contributes once to both entries of either equal-bit
parity or unequal-bit parity. Thus the four prescribed row-pair Gram entries
are equivalent to exactly half the applicable patterns having odd parity.

The independent encoder audit reconstructs all thirty labelled patterns and
135 component/cell constraints. It derives prime CNF clauses from the truth
sets of XOR, two-bit exactly-one and four-bit exactly-two, without importing
the producer. Every one of the 2,010 actual clauses is compared with that
independent relation expansion. This establishes equivalence to precisely
the frozen restricted designs, including the declared auxiliary meanings.
The broader parity proof independently implies that these designs cannot
exist, but is not used to bypass complete DRAT replay.

## 4. Checking boundary

The complete proof is checked by the authenticated drat-trim executable and
its pinned upstream source/build provenance. Its historical Windows patch
only changes header/time portability; checking logic is upstream-identical.
That shared checker implementation, compiler and standard-library helpers
are disclosed rather than described as a diverse formal verification.
Known UNSAT/SAT tiny formulas and corrupted proof/input controls calibrate
acceptance. Encoding controls exhaust the local truth relations and reject
removed clauses and changed auxiliary signs. The parity controls enumerate
all coordinate triples and include a six-bit complement-paired, pair-balanced
16-column positive fixture, where the representative distance is four.

Neither numerical scores nor agent agreement establish either exclusion.
The two exact claim revisions and all evidence hashes are bound in the
independent report. No complete F exists in the checked restricted formula,
and no complete target graph is produced or excluded by this audit.
