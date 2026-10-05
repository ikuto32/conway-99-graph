# Independent arbitrary-core necessary-factor encoding review

This encoding uses C-UNRESTRICTED-TRIANGLE-CORE-FACTOR-NORMALIZATION r1 as a
separately checked universal coverage premise. The independent audit rebuilds
the complete primary variable universe and every clause, without importing
producer code. Its threshold/AND helper is the previously frozen independent
truth-table GateAudit implementation; this reuse is explicit, not a claim of
another independent implementation of that helper.

There are 1,440 unrestricted C1/C2 entries, 66 undirected matching edges in
each of M1/M2, and all 144 directed matrix entries of P. These 1,716 primary
variables have no inherited fixed-zero, component or prism restrictions.
Symmetric matching references with zero diagonals and degree-one equations
describe exactly all two perfect matchings. Row and column degree-one
equations describe exactly all permutations P, including fixed points and
nonsymmetric permutations. All incidence row sums are ten and all fibre
column sums are two. C0 is the independently reconstructed canonical incidence.

Move every variable core term in the normalized Gram formulas to the left.
For C0 against fibre i, the input list is its ten selected incidence bits,
the relevant Mi[a,b] (omitting its false diagonal), and P[b,a] for i=1 or
P[a,b] for i=2; the right side is 2-delta[a,b]-M0[a,b]. For distinct rows
of a single unknown fibre the equation is the sum of 60 incidence products
plus Mi[a,b]=1. For cross rows a in C1,b in C2, it is their 60 incidence
products plus P[a,b], the eleven nonzero-diagonal candidates in M1P, and
the eleven candidates in PM2, equal to 2-delta[a,b]. Every product is an
exact bidirectional AND. Diagonal Gram entries follow from binary row sums;
the fixed C0 block follows from canonical incidence. Transposition supplies
the reversed blocks. No Gram entry is omitted without this justification.

Each prefix state is equivalent to its input-prefix sum reaching the stated
threshold, by induction in its prefix length. Both implications of each
Boolean gate are retained. Upper and equality terminal assertions therefore
implement exactly their cardinality equations, including folded constants.
The checker derives gate clauses from truth relations and compares every
raw clause and auxiliary offset. There are 756 exact equations before caps.

For variable Mi, two columns in a fibre cannot repeat an endpoint pair:
their row scalar product would be at least two, whereas the retained Gram
requires either zero or one. Each column has two endpoints, and matching
endpoints have required scalar product zero. Thus each fibre orders all 60
nonmatching endpoint pairs for its own matching, and two columns overlap at
most once in each fibre. The full overlap cap is therefore equivalent to
the 77,760 four-negative-literal clauses for every intersecting C0 column
pair and every pair of C1/C2 rows. There are no fixed-zero folds here. The
1,230 disjoint C0 column pairs are automatically at most two in the other
fibres. This proof remains valid for every M1/M2; it does not import a fixed
matching conclusion from earlier encodings.

Each channel output z[a,d] has selector entries S[a,k] whose row contains
exactly one true bit. For every k, the two clauses S[a,k] implies
(z[a,d] iff input[k,d]) enforce exactly the selected input. The other rows
cannot constrain z because their selector literal is false. Thus the four
channel arrays equal M1 C1, M2 C2, P C2 and P transpose C1, respectively.
The matching row equations and permutation column equations already checked
above supply the one-hot premise, including the transposed P channel. All
2,880 output variables and all 66,240 implication clauses are checked.
No selector is replaced by an unproved numerical or symmetry assumption.

The three mixed-cap input sums per coordinate and column are precisely the
three blocks of (I+C)F, after moving the fixed C0 terms to the right. All
2,160 such upper bounds are present. Hence the primary solutions are exactly
the arbitrary normalized matching/permutation/incidence objects satisfying
the full Gram, margins, mixed caps and distinct-column caps. Auxiliary
extensions are unique, since all gate definitions are exact and channel
selectors are one-hot.

Every hypothetical target supplies one such object by the independent
normalization theorem. Conversely these clauses only specify a partial
99-vertex graph whose Y--Y edges remain unknown. They do not encode D or
assert target existence. An UNSAT claim would need a complete independently
checked proof on these exact bytes and the recorded coverage/encoding
dependencies; a SAT factor is not a target graph.

Fresh controls exhaust one-hot channels through four possible input rows,
include the absent-selector counterexample, reject changed selector
directions, primary maps, scope restrictions and row metadata, and rerun the
independent complete small threshold truth controls. Fixed input hashes and
complete compressed-artifact reconstruction are authenticated separately.
