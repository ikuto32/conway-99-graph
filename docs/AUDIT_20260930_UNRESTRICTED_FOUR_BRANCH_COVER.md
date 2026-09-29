# Independent four-branch cover argument

This review concerns a new branch recipe for the freshly audited unrestricted
full99 CNF. It does not import a solver conclusion or silently broaden any
historical branch result. The premises are the exact target identity and the
independently established root-scaffold normalization.

Fix a root and label its seven neighborhood edges by groups 0 through 6,
with symbols `2g,2g+1` in group `g`. An outer vertex has a two-symbol label
from distinct groups and is adjacent to exactly those two inner vertices.
All its other twelve neighbors are outer vertices.

Let an outer vertex `u` have label `{a,b}`. For the inner vertex with symbol
`a`, the adjacent-pair common-neighbor equation has right side 1. There is
no common inner neighbor, so exactly one outer neighbor of `u` has a label
containing `a`. For the mate symbol `a xor 1`, the pair is nonadjacent and
has two common neighbors. One is the inner vertex with symbol `a`; the
remaining one must be outer. Thus exactly one outer neighbor of `u` has a
label containing `a xor 1`. The same argument applies to `b` and its mate.
These are four distinct symbols, each occurring once among outer-neighbor
labels.

Define `a_count`, `s_count`, and `d_count` as the numbers of outer neighbors
whose labels use respectively two, one, or zero of the two groups supporting
`u`. Each outer label uses distinct groups, so counting the four just-derived
symbol occurrences gives `2*a_count+s_count=4`. Outer degree twelve gives
`a_count+s_count+d_count=12`. Subtraction yields
`d_count=8+a_count>=8`. In particular a neighbor with disjoint group support
exists; this is a deduction for every outer vertex, not a heuristic choice.

Choose such an edge `uv`. Relabel the two groups of `u` as 0 and 1, the two
groups of `v` as 2 and 3, and the remaining three groups as 4 through 6.
Orient each used group so the selected symbol is even. The resulting labels
are `u={0,2}` and `v={4,6}` and the edge remains present. This is a relabeling
of a possible target, not an automorphism assumption. Every permutation and
orientation of root matching edges induces a permutation of all84 outer labels
and preserves the complete unrestricted fixed/free scaffold.

For this labeled `u`, write the adjacency bits from `u` to the other three
same-support vertices as

* `x`: label `{0,3}`;
* `y`: label `{1,2}`;
* `z`: label `{1,3}`.

The exact quota for symbol 3 gives `x+z<=1`, because these are two distinct
terms in a nonnegative Boolean sum equal to one. The symbol 1 quota similarly
gives `y+z<=1`. Exhausting the eight bit triples gives exactly
`000,001,010,100,110`. Exchanging root groups 0 and 1, preserving the side
within each pair, fixes the labels of `u` and `v`, exchanges `x` and `y`,
and fixes `z`. It preserves the unrestricted scaffold and the anchor edge.
Consequently `010` may be relabeled to `100`; the four triples
`000,001,100,110` cover every hypothetical target after these choices.

In the saved unrestricted variable order, `u` is full99 vertex 15, `v` is
vertex 59, and the anchor edge has primary variable 44. The `x,y,z` edges have
variables 1,2,3. The four unit sets are therefore
`[44,-1,-2,-3]`, `[44,-1,-2,3]`, `[44,1,-2,-3]`, and `[44,1,2,-3]`.
The artifact checker independently derives these indices from raw pairs and
checks the producer's exact branch recipes.

The disjunction of these four branches is complete only up to the proved
relabelings. It is not asserted to contain every assignment in its original
labels. Branch counts are not equal fractions of graphs, difficulty, or time.
To infer target nonexistence one would still need complete independently
checked UNSAT proofs for all four exact branch instances, with this coverage
argument and the unrestricted encoding equivalence intact.

The historical `scratch_general_exact_sat.py` already used the four named
cases `a0`, `a1_complement`, `a1_cross`, and `a2_crosses`, plus a nominal
`a2_mixed` case with `x,y,z=101`. That fifth bit triple violates `x+z<=1`.
This review gives a fresh exact coverage and literal binding for the new
unrestricted encoding. It makes no novelty claim and does not treat the old
proofless or resource-limited solver records as fresh exclusion evidence.
