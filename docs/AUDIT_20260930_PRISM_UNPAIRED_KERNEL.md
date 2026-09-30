# Independent review of the unpaired five-matching exclusion

This review addresses claim C-SIX-PRISM-FIVE-MATCHING-UNPAIRED-DESIGN-EXCLUSION,
revision1. The discovery involved root and state_literature_audit. The
separate reviewer is structural_attack. Its checking source imports no
producer code and does not replay or trust the producer's rational row
operations. Instead it reconstructs each matrix from the raw thirty patterns,
checks a proposed integer kernel vector directly, and supplies a nonzero
integer9by9minor. Python integer arithmetic and standard-library file/hash
handling are shared trusted infrastructure.

The scope fixes five explicit round-robin perfect matchings of six components,
all six assignments of their three edges to three cells, and two copies of
each resulting pattern. Each column picks one of two bit-labeled vertices
from each component in its prescribed cell. All360bits are independent.
This is a restriction on the incidence design, not an automorphism of any
hypothetical target. No statement about other cell patterns follows.

Label a core row by (cell g, component a, bit b), with index12g+2a+b.
The literal core has an edge between opposite bits in one cell and between
equal bits in different cells of the same component. These are six disjoint
triangular prisms. The factor Gram obtained from the target block identity
is12I-B-B²+2J minus the same-cell all-ones blocks. For distinct components,
B and B² have zero entries between them; hence their prescribed Gram entry
is1 in the same cell and2 in different cells, independently of both bits.
The audit recomputes this from the complete36by36 integer adjacency.

Fix component a and cell g. Exactly ten pattern indices t place a in g.
Define u_t as the sum of its two repeated-column bits minus1. For any other
component b and cell h, the Gram prescribes count c=1 or2 for each fixed
pair of bits, according as g=h or g differs from h. Summing the two joint
counts with a-bit1 gives2c occurrences. The raw pattern population in that
domain is also2c. Subtracting one per pattern gives the homogeneous equation
sum u_t=0. This proves the necessity of each row of the fifteen-by-ten
matrix without a SAT encoding premise.

For every one of the18(component,cell) choices, the independent checker
reconstructs every matrix entry, verifies a nonzero null vector with ten
entries in{−1,+1}, and produces a9by9minor with nonzero integer determinant.
The minor proves rank at least9; the null vector proves rank at most9.
Thus the rational kernel is exactly its span. Since u is an integer vector
whose entries lie in{−1,0,1}, any one unit coordinate of the generator shows
that its scalar is−1,0or1. Scalar0 means both copies have complementary bits
in every selected pattern. Either other scalar means both copies have
identical bits in every selected pattern. No partial mixture is possible
within this(component,cell) group.

For two distinct components in one cell, exactly two patterns put both in
that cell. If both groups had the identical type, each pattern's two copies
would contribute twice to one joint-bit category. All four joint counts
would be even. The prescribed four counts are each1, a contradiction.
Therefore at most one component has identical type in each cell. At most
three components have any identical-type cell, leaving at least three
components complementary in every pattern, regardless of its chosen cell.

For any two distinct components and fixed two bit values, the total across
all cell pairs is3*1+6*2=15. Their complete60-bit words consequently differ
at15+15=30positions. For two of the three fully complementary components,
both bits flip between the two copies of each pattern, preserving whether
they differ. Their first-copy30-bit words therefore have Hamming distance15.
For three binary words, every coordinate contributes zero or two to the sum
of the three pairwise distances; that sum is even. Here it would be45,
which is impossible. This proves the stated restricted-design exclusion.

Calibration includes exact determinant comparisons with literal2by2 and
3by3 formulas, a constructed rank9positive, false kernel/rank controls,
changed raw matrices and determinants for all18systems, all eight local
triple-bit parity cases and all sixteen two-pattern identical-bit cases.
The complete output records bind the exact claim revision and artifact hashes.
This review does not approve the native UNKNOWN run or its encoding, and
does not need that run. It makes no novelty or external-review claim.
