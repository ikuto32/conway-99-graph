# Independent audit of the first-matching normalization

Reviewer: `/root/structural_attack`. The producer is `/root`. The checker
imports no producer implementation. Frozen independent base encoding and
normalization gates are premises; this audit independently reconstructs the
new transport coverage and clause extension.

Let h be any permutation of the twelve coordinates commuting with the
standard matching M0. Apply h in each of the three fibres, and fix the three
vertices of the distinguished triangle. The two identity cross matchings
remain identity. Each remaining matching or cross permutation is conjugated
by h. Thus M2 and P still range over all matchings and all permutations; no
involution or commutation condition on P is introduced. Write R for the
induced 36-row permutation and Q for the permutation of the sixty canonical
C0 columns, sending {a,b} to {h(a),h(b)}. Commutation with M0 ensures these
are exactly the same nonmatching two-subsets. Relabel the factor by

    C'[R(i),R(j)] = C[i,j],    F'[R(i),Q(d)] = F[i,d].

The C0 block is again canonical. Every row margin and fibre-column margin
is unchanged. Renaming the summation index proves

    (F'F'^T)[R(i),R(j)] = (FF^T)[i,j],
    ((I+C')F')[R(i),Q(d)] = ((I+C)F)[i,d],
    (F'^TF')[Q(d),Q(e)] = (F^TF)[d,e].

The prescribed Gram matrix is
12I-C-C^2+2J-diag(J12,J12,J12). Each of its terms transforms by R because
R preserves fibres. This proves covariance of every Gram entry and every
mixed or distinct-column cap for arbitrary binary F, arbitrary M2, and
arbitrary P. The argument is a universally valid index substitution, not an
inference from sampled factors. Literal controls exercise it with arbitrary
cores and nonfeasible binary arrays; those arrays are not research witnesses.

The checker independently enumerates perfect matchings by pairing the least
remaining vertex recursively. This gives all 10,395 matchings exactly once.
For each raw saved record it checks h is a permutation, h commutes with M0,
and every edge of the source matching maps to the specified representative.
It also checks the complete induced C0 column permutation. Coverage is the
literal equality of the independently generated universe and the recorded
matching universe, together with exactly one valid transport per element.
The eleven representatives have different partitions of six given by the
component sizes of M0 union M1 divided by two. Those partitions are invariant
under the allowed relabellings, so the representatives are distinct orbits.
Coverage plus these distinct invariants gives eleven complete first-matching
orbits; no M2/P joint orbit classification is asserted.

The extension adds selector IDs 110905 through 110915. One clause requires
at least one selector. For each representative, six binary clauses make its
selector imply its six positive matching edges. The base exact matching
degree constraints force all other M1 edges to zero when those six are true.
Distinct perfect matchings cannot contain each other's six-edge sets, so two
different selectors cannot both hold. Thus the suffix expresses exactly the
union of the eleven specified matching cases. The source CNF's clause body
is compared byte-for-byte; the only changes are the new header and these 67
clauses. Counter auxiliaries are not claimed to undergo a literal variable
permutation. The audited equivalence of base encodings supplies their exact
values after the primary object is relabelled.

Every solution of the base necessary factor problem can therefore be
relabelled into an extended-formula solution; the reverse implication is
restriction to the base variables. Consequently the formulas are
equisatisfiable, but their primary assignment sets are not identical. This
is relabelling of a possible solution, not an assumption that the solution
admits its own nontrivial automorphism. By the separately audited universal
triangle normalization, every target graph supplies a solution of this
normalized necessary model. A SAT factor does not establish residual D or a
99-vertex graph. Any future UNSAT claim still needs complete proof replay.

The separate SAT wrapper checks all 110,915 native/JSON values and all
518,227 actual clauses before projecting to the 110,904-variable base model.
It reuses the pinned independently authored raw arbitrary-core decode and
integer checks, then verifies the selected representative and all six edges.
Calibration separates full-size codec controls from the known-valid small
rook9 raw control. No unavailable complete research factor is invented.
