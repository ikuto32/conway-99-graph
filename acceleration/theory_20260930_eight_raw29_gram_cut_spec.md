# Preregistered w81 exact full99 Gram cut

Question: derive a necessary edge clause for target extensions in the frozen
120-fixed-K/2160-free-edge family from the independently checked w81 induced29
configuration, whose integer direction has quadratic-5868. Use only the second
record of the raw negative_candidates artifact. The w71 pattern is separately
retained as already failing a restored full99 common-neighbor cap; it is not
selected for this experiment.

Embed the raw29 vector in its declared full99 coordinate map, assigning zero
outside it. Reconstruct the affine expression
`q = 27*sum(v_i^2)+(sum(v_i))^2 -18*sum_known_edges(v_i*v_j)
     + sum_free_edges(-18*v_i*v_j)*x_ij`.
Record all2160coefficients, including zeros. For every nonzero coefficient,
both endpoints belong to the raw29 set and its raw adjacency supplies a Boolean
value. Record the initial support clause and full fixed assignment. Check its
exact q=-5868 by an independent algebraic form within the producer; this is a
calibration, not independent approval.

For each nonzero variable, calculate the maximum possible gain on freeing it:
`max(0, c*(1-2*a))`. Free variables in increasing-gain order, breaking ties by
variable ID, only while the accumulated upper bound stays strictly negative.
Zero-coefficient variables are always free. The remaining fixed variables give
a clause requiring at least one to change. Construct the complete Boolean
maximizing corner on all2160variables and evaluate its full99 integer matrix
quadratic directly. Exact zero does not establish a cut. No floating arithmetic,
random seed, automorphism or sampled validation is used.

Limit:120seconds, one selected negative direction, no solver invocation and no
research CNF alteration. Save immutable source/command/version/input hashes,
every coefficient and free/fixed choice, initial/final clauses, maximizing-corner
matrix/assignment, and exact controls. Positive/corrupt small Boolean-box controls
precede production. Any generated clause remains CANDIDATE until a separate
implementation checks the full99 model mapping, all coefficients, raw negative
direction and maximizing corner against the universal target Gram lemma.
