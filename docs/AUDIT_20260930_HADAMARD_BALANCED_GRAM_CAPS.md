# Independent complete outside-column cap extension

This extension retains the entire independently checked balanced-Gram base
formula and all150 choices in each of its twenty groups. It imposes one extra
condition on the decoded36-by60 binary factor: each pair of distinct columns
has intersection at most two. The fixed support and coordinatewise balance
remain additional construction restrictions. Neither is asserted without loss
of generality for Conway99, and no target automorphism is assumed.

The twenty support groups partition the sixty raw columns into triples. Within
one selected local option, each coordinate uses each fibre exactly once, so
the three columns are pairwise disjoint. This accounts for20 times3, or60,
column pairs. Two different groups give nine raw column pairs. There are190
group pairs, accounting for the other1710 pairs. These populations are disjoint
and total1770, the full binomial(60,2) column-pair population.

For every ordered choice pair from a fixed unordered pair of groups, compute
all nine intersections from the actual36 binary rows. Declare the choice pair
forbidden exactly when at least one intersection exceeds two, and add the
clause negating both selectors. Under the unchanged exact-one group relations,
the appended binary clauses hold if and only if every decoded outside-column
cap holds. There is no pruning of options, assumed symmetry, sampled coverage,
or extra residual-graph condition in this equivalence. The base auxiliary
variables retain their existing unique-extension interpretation.

The independent checking path reconstructs the150 local options using two
balanced six-color words and the forced third word. It derives the36-row
columns directly from their colorings and raw support. All450-by450 column
products for every group pair use exact signed16-bit integer arithmetic:
binary input entries and six ones per column bound each dot product by six,
far below the integer range. Reducing each three-by-three block yields every
one of the4,275,000 choice-pair decisions. Literal scalar controls calibrate
the array shape, ordering and arithmetic. This path does not use the producer's
profile masks or bitset intersection routine.

The raw SAT checker must inspect all10,480 native and JSON literals, every
clause in the actual appended formula, and then reconstruct all2160 factor
entries independently. It checks exact support, margins, all1296 Gram entries,
all1770 outside-column caps and all2160 mixed closed-neighborhood counts. In
this fixed six-prism support, each column selects exactly one vertex from each
six-vertex prism, while a row and all its core neighbors lie in that prism.
Thus the mixed counts are at most one automatically; checking them does not
silently strengthen the encoded class. The canonical C0 column order is
accepted only after checking the complete sixty nonmatching coordinate pairs.

Positive controls use genuine local options and the separately authenticated
SRG(243,22,1,2) factor for generic Gram/margin/cap arithmetic. Synthetic complete
assignment controls are labeled codec-only. No feasible factor in the present
research class is invented. A valid capped Gram factor would still require
residual completion before it could constitute a99-vertex target graph.
