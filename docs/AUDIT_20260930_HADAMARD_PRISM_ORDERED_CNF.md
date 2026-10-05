# Independent ordered fixed-support encoding review

This audit covers every balanced colouring of each column of the one saved
six-prism Hadamard support. There is no cyclic relation between its columns.
Two nested two-element subset choices independently enumerate all90 options
per column. The exact cubic core and integer prescribed Gram are rebuilt from
the three standard matchings and identity cross matchings.

Sixty exact-one equations select columns. Each of666 upper-triangular Gram
entries is the sum of selectors whose six-row support contains that row pair;
diagonal entries are included. All1770 pairs of columns are tested against all
8100 pairs of their options, and precisely those with intersection greater
than two require a negative binary clause.

Within each group of three identical coordinate supports, two adjacent option
ranks must strictly increase. The checker derives all40 adjacency pairs from
the literal support and checks all4095 forbidden rank pairs per adjacency.
The separately pinned normalization proof explains coverage: repeated columns
cannot occur in a valid factor, and sorting distinct option ranks simply
relabels those outside vertices. It assumes no automorphism of a target.

The independent truth-relation checker checks every threshold state, fresh
auxiliary ID, gate clause, lower/upper unit and complete DIMACS stream. Its
small exhaustive controls and fresh changed-scope/domain/counter/order/cap
controls calibrate the checking path. No complete research factor is supplied
as a positive fixture. Residual D and other coordinate supports are outside
this encoding; even a factor is not a target graph.
