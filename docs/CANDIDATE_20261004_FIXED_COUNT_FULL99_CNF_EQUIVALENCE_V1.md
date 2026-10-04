# Candidate: labelled fixed-count completion and the full99 CNF

Claim ID: `C-FIXED-COUNT-LABELLED-SRG-CNF-COMPLETION-EQUIVALENCE`, revision 1.
Discovery producer: `/root/checkpoint_audit`. Root proposed the graph-lift
direction; the construction and proof below are Checkpoint's new candidate.
There is no independent approval, executed formula, solver result or graph here.

## Precise statement

Let a supplied profile have a simple undirected induced support H on m labelled
vertices and N distinctly labelled exterior copies, so v=m+N. Each exterior
copy x has a fixed binary incidence column t_x, with support T_x. Its label
is `(type index, copy index)`; no equal-type copies are identified. Let B be the
m by N matrix of these columns. Suppose the fixed support data satisfy

    H 1 + B 1 = k 1,
    (H^2 + B B^T + H)[u,v] = 2 for every distinct support u,v.

For each pair of distinct exterior copies, supply a nonempty allowed set
L_xy contained in {0,1}. Fix D_xy to its singleton value when L_xy is a
singleton, and otherwise give it one Boolean variable; use D_yx=D_xy and
D_xx=0. Consider the exact CNF construction below, using fully equivalent
AND and prefix-threshold gates.

Its satisfying assignments, projected to the free D variables, correspond
bijectively to simple labelled strongly regular completions A of parameters
(v,k,1,2) with the supplied H, B and pair restrictions D_xy in L_xy. Each
accepted free assignment has exactly one extension to the fresh auxiliaries.
Thus a completed, correctly checked instance for v=99, k=14, m=17, N=82 is
satisfiable exactly when this one labelled count profile has such a completion
respecting those restrictions. This does not quantify over other count vectors,
other supports or all target graphs.

If the allowed sets are independently established necessary restrictions for
every target completion of this profile, they remove no such completion. The
equivalence without this additional premise remains equivalence to completions
respecting the supplied restrictions. An empty allowed set between two existing
copies makes that restricted completion family empty; rejecting the input is
not itself a separately verified CNF UNSAT proof.

The claim concerns the mathematical construction and its source correspondence.
No emitted formula is yet authenticated. A future byte-level equivalence check
must independently verify the completed DIMACS, mapping and counter inventory.

## Construction and proof

Write

    A = [ H   B ]
        [ B^T D ].

By construction A is symmetric, binary and has zero diagonal. The following
three families are imposed as exact equalities, with all copy indices retained:

    sum_{y != x} D_xy = k - |T_x|,                         (degree)
    sum_{y != x, u in T_y} D_xy = 2-B_ux-(HB)_ux,          (cross)
    sum_{z != x,y} (D_xz AND D_yz) + D_xy
        = 2-|T_x intersect T_y|, for x<y.                  (outside pair)

There is no equitable-profile assumption. Different copies of the same type
may have different exterior neighbors.

The degree equalities supply all exterior row degrees of A. The assumed fixed
support degrees supply every other row degree. As A is binary and symmetric,
(A^2)_aa is that row degree, so every diagonal entry of

    A^2 + A = (k-2) I + 2 J

is satisfied. Conversely the imposed exterior degree equations are necessary
for any k-regular completion.

The support-support off-diagonal block of the identity is the assumed
`H^2+B B^T+H=2`. The support-exterior block is
`HB+BD+B=2`, exactly the cross equalities above: D_xx is zero, so omitting x in
the sum loses no term. Symmetry supplies the transposed block. The exterior
off-diagonal block is `B^T B+D^2+D=2`. Here the fixed support contribution is
`|T_x intersect T_y|`, and the summands z=x,y vanish because D has zero
diagonal. This is exactly the outside-pair equality. Requiring only x<y covers
both ordered entries by symmetry.

For distinct vertices a,b, the identity gives `(A^2)_ab=2-A_ab`: adjacent
vertices have one common neighbor and nonadjacent vertices have two. Along with
the binary simple k-regular domain, this is the definition of the claimed SRG
parameters. This proves sufficiency of the three families and fixed support
checks. Necessity follows by taking each block of the same identity in any
completion. Neither direction uses a sampled row-capacity screen as a
sufficient graph condition.

### Exact gate semantics

The frozen logical ancestor uses a fresh z for nonconstant AND(a,b), with

    (a or not z), (b or not z), (not a or not b or z).

These clauses are equivalent to z=(a and b). In each of the four input cases
they force the same unique z. Boolean-constant branches return the equivalent
constant or existing reference and introduce no auxiliary.

OR(a,b) similarly uses

    (not a or z), (not b or z), (a or b or not z),

which is z=(a or b). The nonconstant recurrence z=(a or (b and c)) uses

    (not a or z), (not b or not c or z),
    (a or b or not z), (a or c or not z).

The first two clauses force z when a or b-and-c is true. If z is true, the last
two require a-or-b and a-or-c, equivalent to a-or-(b-and-c). All constant
folding branches of the frozen recurrence preserve this Boolean function.
Every newly allocated output has a larger index than its input references,
so the gate graph is acyclic and has a unique semantic extension from its
earlier inputs.

For distinct positive input variables l_1,...,l_q, the counter starts with
s_0,0=true and all other missing states false. It constructs, up to the needed
threshold r+1,

    s_i,j = s_{i-1,j} or (l_i and s_{i-1,j-1}).

Induction on i proves s_i,j is true exactly when at least j of the first i
inputs are true. Missing j>i states are correctly false; j=0 is true. Keeping
only j<=r+1 loses no predecessor needed for those thresholds. The final units
s_q,r and not s_q,r+1 therefore impose exactly sum l_i=r. The upper-bound-only
variant imposes just not s_q,r+1. The empty-input r=0 and endpoint r=q cases
follow from the same constant conventions; no artificial positive variable 0
is introduced.

The new equality wrapper discards false constants and subtracts the number of
true constants from its required integer value. This leaves an equivalent sum
of the remaining positive variables. If its adjusted bound is outside
0..q, the equality is impossible and one empty clause is the correct formula.
An impossible equality has no satisfying auxiliary assignment, rather than a
truncated or weakened bound.

The distinct-input requirement holds in each caller group. A degree or cross
group uses different edges incident with its focal copy. For an outside-pair
group, a conjunction with two variable operands obtains its own fresh output.
A conjunction folded because one operand is true returns one edge incident
with x or y and a third copy z. Such references cannot repeat for different z:
an equality of an x-z edge and a y-z' edge would require z=y and z'=x, both
excluded. They also cannot equal D_xy. True/false results are stripped as
constants. Thus no multiset coefficient is silently lost by a set-valued
counter interface.

Finally, clause normalization discards false disjuncts, duplicate literals and
tautological clauses, and discards a clause containing true. Each transformation
preserves the Boolean clause. A clause with no remaining disjuncts is false.
These facts prove the projection equivalence and unique auxiliary extension
for the completed logical formula, including justified fixed-bit folding.

## Exact source correspondence and verification boundary

The new caller is
`acceleration/encode_20261004_fixed17_count_full99_cnf_v1.py`, SHA256
`b98e2ec1620dcac245c71ab8f224b0e489eb810329384c47320ca2e71cb0e3e0`;
its specification is SHA256
`c836a9e4253afff09999833f74e0e229438e40f4fc3c0b165862cb7a074175ed`.
The unchanged ancestor is
`acceleration/theory_20260930_eight_full99_cnf.py`, SHA256
`21c357543c9397456a911175b277da6e6caa769be31d18c12e034cc76d99074c`.
The caller authenticates and selects only negate/Clauses/Encoder AST nodes;
the old imports, main, ResourceCap and historical deadline are outside this
reuse. This is shared logical-source ancestry, not new independent authorship
of those primitives or approval from an old runtime gate.

For the specified 17+82 profile the groups are 82 degrees, 17*82=1394 cross
entries and choose(82,2)=3321 outside-pair entries, totaling 4797. Before fixed
bits there are at most 3321 free exterior-edge variables. The scientific source
checks all support degree and off-diagonal moment equations before these groups.
This paper does not evaluate the actual count-vector entries or pair-bit
population; those are separately qualified immutable input premises.

No actual counter, fixture, CNF or solver was executed while preparing this
candidate. The planned rook(9,4,1,2) controls, all 1024 free-edge assignments,
complete tiny auxiliary truth tables and corrupted matrices remain unexecuted.
They provide finite engineering checks only after their genuine outcomes exist.
An independently authored complete formula/mapping checker is still required.

A later SAT assignment must be checked against the exact formula and decoded
by a distinct implementation into all 99 integer adjacency rows, with every
9801 product and exact SRG conditions verified. A later UNSAT claim requires
qualified complete proof replay tied to the exact checked formula. A timeout,
partial proof, solver string, hash, counter annotation or this discovery paper
alone supplies neither conclusion. Independent review of this mathematical
candidate remains pending; it changes no registered claim or target status.
