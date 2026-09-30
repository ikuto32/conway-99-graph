# Independent complete-column encoding audit for the six-prism core

This review concerns the fixed39 core whose three inner12-cells all have
matching `(01)(23)...(10,11)` and whose three cross matchings are identity.
It makes no assertion that an arbitrary target contains this core and assumes
no nontrivial target automorphism. Let H be this full39 adjacency matrix,
including the root triangle and its three cell incidences. The required
36-row incidence Gram is the raw integer matrix

`K_ab = 12 delta_ab - H_(3+a,3+b) + 2 - sum_z H_(3+a,z) H_(3+b,z)`.

The independent checker reconstructs H literally. Direct multiplication gives
K diagonal10. Distinct rows in the same six-vertex prism have K entry0;
rows in different prisms have entry1 in the same cell and2 in different
cells. These identities are checked for all1296 ordered entries.

**Necessity and complete column universe.** Suppose a binary36-by-60 F has
`F F^T=K`. Each row has weight10 by the diagonal. Pairwise disjoint supports
of the six rows in each prism have total size60, so they partition all60
columns. Thus every column selects exactly one row in each prism. This
does not assume an automorphism or paired columns.

For a cell g let k_d be its number of selected rows in column d. The row
weights give `sum_d k_d=120`. Summing the cell's Gram block gives
`sum_d k_d^2=240` (12 diagonal entries10 and120 ordered off-diagonal
entries1). Consequently `sum_d (k_d-2)^2=0`; each k_d is exactly2.
The two C0 rows in a column lie in different prisms. Every such unordered
pair appears once because its Gram entry is1, and no same-prism pair can
appear. Relabelling the60 columns therefore fixes C0 to the60 lexicographic
nonmatching pairs. This column normalization is a relabelling, not a
symmetry premise on a target.

For one fixed C0 pair, the other four prisms each select one of their four
rows in cells1/2, with exactly two prisms in each cell. The full universe
has `binomial(4,2)*2^4=96` supports. The audit enumerates all `6^6=46656`
component choices independently of the producer's per-column construction,
retains exactly the5760 states with two rows per cell, and partitions them
by their C0 pair. It checks every supplied support and primary ID against
that complete universe. There is no complement constraint, orbit pruning,
fixed five-matching pattern or bit normalization.

**Exact equations and sufficiency.** Exactly one choice is required in each
canonical column. Of the row pairs in distinct prisms, remove the60 pairs
entirely in C0, which are already fixed. The other480 pairs have prescribed
counts:120 at1 and360 at2. Each choice contributes to14 of these equations
(all15 pairs of its six rows except its C0 pair), so the complete incidence
population is80640. Same-prism off-diagonal entries are zero by the domain.
For an arbitrary row r in cell1 or2, sum its ten same-cell, other-prism
overlaps. The480 equations make this sum10. Each column containing r has
exactly one other row in its cell and that row is in another prism. Therefore
the sum equals the weight of row r, establishing weight10 and all remaining
diagonal entries. C0 already has weight10. Thus the540 equations are
equivalent to the normalized binary Gram-factor problem, not merely a
necessary relaxation of that abstract factor problem.

Every vertex's closed neighbourhood in the cubic36 core lies within its own
prism, while each column selects one vertex of that prism. Therefore
`(I+C)F<=J`, which implies the target-necessary bound `<=2J`. This does not
imply the distinct-column bounds `F^T F<=2` off the diagonal, which are not
encoded. A factor still needs those bounds and a residual D before it could
give a target graph.

**Boolean encoding.** The audit does not import the producer. It uses the
previously frozen independent GateAudit to derive each gate relation by its
complete truth table and minimal implicates, then verifies every raw clause
segment, constant/alias fold, fresh auxiliary ID, threshold state, equality
unit and metadata offset. The induction invariant is: prefix state(i,j)
equals whether at least j of the first i primary inputs are true. Fresh
topological gates establish this invariant and provide a unique auxiliary
extension to any primary assignment. Equality assertions therefore impose
exactly the540 reconstructed equations. All874800 clauses and245880 IDs are
checked, including5760 primary choices; no SAT solver is used.

Positive controls include the complete small threshold relations, raw core
coefficient identities and the complete enumerated choice universe. Explicit
corruptions alter raw scope, choices, constants and equation metadata. The
separate raw-object checker and calibration must be bound before any research
SAT result is accepted. There is no known positive full36 factor of this
research Gram serving as a fixture; controls do not imply one exists.

The producer manifest omitted a transitive import of
`theory_20260930_full_srg_validator.py` by its shared Encoder module. The
independent audit binds that exact source as additional provenance and
discloses the omission; neither producer file nor old manifest is rewritten.
The checker shares Python integers/standard library, tqdm through the pinned
independent gate helper, and that helper's previously audited truth-relation
implementation. It shares no producer scoring, domain enumeration, graph
construction or clause-template implementation.

Only a separately replayed complete proof could establish UNSAT of these
bytes. Even then the conclusion would exclude this six-prism core's factor
family, not every possible triangle core or the unrestricted target.
