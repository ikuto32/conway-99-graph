# Independent joint incidence-factor encoding review

The scope is one labelled 39-vertex core H: a triangle, three twelve-vertex
fibres, canonical mate i xor 1 within each fibre, identity matchings between
fibre 0 and fibres 1/2, and shift by six modulo twelve between fibres 1/2.
This does not assert that every target contains this core.

In any target extension, each triangle vertex already has degree fourteen
inside H, so the remaining sixty vertices have no triangle neighbor. Their
two common neighbors with each triangle vertex must be in its twelve-vertex
fibre. Consequently the outside incidence matrix C has exactly two ones in
each fibre of each column. Each fibre vertex has four neighbors inside H,
so its row in C has ten ones. Restricting the exact target identity to the
36 fibre vertices gives, entry by entry,

    G[a,b] = 12*[a=b] - H[3+a,3+b] + 2
             - sum(k=0..38) H[3+a,k]*H[3+b,k] = (C C^T)[a,b].

The checker constructs raw H and evaluates this integer expression. It does
not import the producer's formula for the Gram blocks.

For each fibre the Gram diagonal is ten, entries between matching partners
are zero, and other off-diagonal entries are one. A binary column with two
ones in fibre 0 names an unordered pair. No matching-partner pair occurs,
and every other pair occurs exactly once by its Gram entry. There are sixty
such pairs and sixty columns. A column permutation therefore places C0 in
the canonical lexicographic incidence order without losing a factor. This
is relabelling the sixty outside vertices, not assuming their permutations
are automorphisms of any target. C1 and C2 remain unrestricted.

If G[a,b]=0 with a in fibre 0, every nonnegative summand C0[a,d]*C[b,d]
vanishes. Thus C[b,d]=0 for every column containing a. The checker folds
exactly these zeros and checks all their raw witnesses. No other free
incidence is fixed. The resulting 1,200 primary variables are bijective
with the remaining positions of C1 and C2.

The 24 row margins impose ten ones, the 120 column margins impose two ones,
the 288 C0-cross equations impose both fixed/free Gram blocks, and the 276
unordered-pair equations between free rows impose all their off-diagonal
Gram entries. Binary diagonal Gram entries equal row sums. C0 is already
correct. Thus these 708 equations are exactly the specified factor problem.

Each product is bidirectionally equivalent to the conjunction of its two
specified primary entries. The separate, previously frozen independent
GateAudit helper derives each small gate CNF from its complete Boolean truth
relation. It is reused here; this is not a new independent implementation of
that helper. Its prefix states satisfy

    T(i,j) iff T(i-1,j) or (x_i and T(i-1,j-1)).

Induction gives T(i,j) iff the first i inputs contain at least j ones.
Boundary constants and aliases are checked explicitly; both T(n,k) and
not T(n,k+1) impose equality k. Every gate, state, row and raw clause is
reconstructed from the independent scope. Conversely, every factor gives
the unique product and threshold values, hence a satisfying assignment.

Therefore the exact saved CNF is satisfiable if and only if the specified
36-by-60 binary factor exists, allowing the proved column normalization.
A satisfying factor need not extend to a target: no residual sixty-vertex
graph D is encoded. A checked UNSAT proof would exclude this fixed core
only. No solver result, target-wide coverage, or target automorphism claim
is part of this encoding audit.

Object-checker calibration uses the two archived positive 24-row partial
factors against their exact required Gram entries, plus an explicitly
synthetic 36-row repeated-incidence factor against its own Gram. The latter
is not a research factor of G. Wrong entries, margins, Gram entries, shapes,
and types must be rejected. No known positive full factor of the research G
is available; this limitation is explicit.
