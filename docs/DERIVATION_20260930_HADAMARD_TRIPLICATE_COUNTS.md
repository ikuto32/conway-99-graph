# Triplicate-support counts: necessary projection and finite local census

**CANDIDATE — independent review required.** No full factor is constructed or
excluded, and the proposed balance implication for the full Gram system remains
UNKNOWN. These records concern the one saved six-prism Hadamard aggregate L.

Let S_p (p=0,...,19) be the distinct six-coordinate supports. Each occurs in
three raw columns. Each support chooses one endpoint from each of the six
standard matching pairs. A coordinate belongs to ten S_p, and two coordinates
from different matching pairs occur together in five S_p.

Write t[p,a,g] for the number of those three columns that assign coordinate a
to fibre g. It is an integer between zero and three, with sum over g equal to
three. A full prescribed-Gram factor necessarily satisfies

    sum_{p: a in S_p} t[p,a,g] = 10,
    sum_{p: a,b in S_p} t[p,a,g] = 5  (b not in {a, mate(a)}).

The second equation follows by summing the three Gram entries for rows (g,a)
and (h,b), h=0,1,2: their required values are 1,2,2. In each raw column whose
support contains b, exactly one of those three b-rows is occupied. No unknown
outside adjacency, cyclic assumption or automorphism is used.

For each a, the resulting eleven-by-ten matrix A_a has an all-one first row
and the ten raw support-incidence rows for b. The target is (10,5,...,5).
The all-one count vector solves it. Every matching pair among the b coordinates
gives complementary rows, so rank is at most six. The saved exact rational
eliminations have rank six, with literal left-transform matrices and every
operation. Thus the marginal projection has four free dimensions per fibre.

The experiment finds a nonzero v in {-1,0,1}^10 with A_a v=0 for every a.
The three count columns (1+v,1-v,1) are nonnegative integers summing to three
entrywise, and each satisfies the target equations. For a=0, on groups

    (0,2,5,6,7,8,10,12,17,18),

one saved vector is

    v=(-1,0,-1,1,0,1,1,-1,1,-1).

All 12 witnesses are retained, not just this example. Each of their ten
individual group-count requirements has a saved literal local triple obeying
all Gram upper bounds and its three outside-column caps. Those separate triples
need not agree with the other coordinates' witnesses or with cross-group Gram
equalities. This refutes uniqueness in the marginal projection only. It does
not refute the proposed implication from the full Gram system.

The second computation exhausts the 117,480 increasing triples of distinct
balanced six-coordinate colour words, chosen from the 90 lexicographic words
with two occurrences of each colour. Identical words cannot occur twice in a
full factor: they repeat a within-fibre nonmatching coordinate pair whose
required Gram entry is one. Increasing word order only removes permutations
of the three identical-support columns.

For each candidate triple, the checker retains it precisely when every local
row-pair contribution is at most its prescribed Gram entry (one for the same
fibre, two for different fibres, zero for two colours of one coordinate), and
each pair of its raw columns overlaps in at most two rows. All six coordinates
in a support lie in distinct matching pairs, so this same local census applies
to each of the 20 groups; no target-graph symmetry is assumed.

The producer census reports 31,110 survivors. Exactly 150 have colour counts
(1,1,1) at every coordinate, and 30 of those are cyclic colour-shift triples.
The entire survivor lists, balanced and cyclic sublists, and count-profile
histogram are saved. Independent review must establish these finite counts.

A first local unbalanced survivor is

    001122
    010212
    012021

Its first coordinate has counts (3,0,0), while its three column overlaps are
all two. It is a local witness only. A coordinatewise balanced but noncyclic
survivor is

    001122
    120201
    212010

Its three columns are pairwise disjoint. Therefore even a future proof of
coordinatewise balance would not by itself justify reducing every group to
the previously excluded cyclic subclass.

The rank and local-cap projections are necessary conditions, not an alternative
encoding of the complete Gram problem. A stronger relaxation could use all
31,110 unordered local triples per group and impose their exact global Gram
contributions. That construction would retain arbitrary local triples and
would need its own independently checked encoding and resource protocol.
No such solver or model is produced here.

Controls ran before enumeration: two exact rank fixtures, a literal nonzero
kernel vector, a cyclic local triple, and six deliberately corrupted kernel,
word, duplicate-word or pair-cap cases. The bitset census is a producer path;
an independent reviewer should reconstruct local integer adjacency overlaps
or another direct counting path rather than merely rerunning this script.

The bounded archive search found general triangle-incidence-code and split
moment work in waves 102 and 132. Those concern global codes and are not the
same saved-L marginal matrices. No exhaustive literature search or novelty
claim is made. The source, initial protocol, raw hash bindings, exact commands
and result metadata are preserved under `20260930_hadamard_triplicate_counts`.
