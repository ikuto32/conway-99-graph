# Independent fixed-Q1 partial99 propagation audit

This audit concerns two exact conditional starting matrices, not all possible
triangle-root configurations. Archive source identity is repository
`https://github.com/YesterdaysLemon/conway-99-research`, commit
`85e705cc6c2a14d123120c93a847e30aaab1789e`. Historical VERIFIED/UNSAT labels
are not used as fresh proof. The checker reads the specified JSON blobs with
`git show` at that immutable commit and authenticates the workspace copies.

Vertices0,1,2 form T. Vertices3+12i+u represent group A_i, and39+d represents
B_d. Only t_i is adjacent to A_i; T has no B neighbors. Within each A_i the
matching is u--(u xor1). Cross matchings are A0u--A1u, A0u--A2u, and
A1u--A2(u+6 mod12). These exact permutations are compared with Wave149's
saved `minimal_surviving_witness` fields. They are fixed-case assumptions.

Let E be the lexicographic list of nonmatching unordered pairs on0,...,11.
Its size is60. B_d has A0 neighbors E[d] and A1 neighbors E[Q1[d]]. The two
Q1 arrays come respectively from Wave151 `exact_partial_factor.Q1` and
Wave154 `second_exact_Q1_representative.Q1`; each is independently checked
to be a permutation of0,...,59. No inverse permutation is substituted.
All A2--B pairs and all off-diagonal B--B pairs are initially unknown.
All other entries are fixed by the above specification, including zeros.
The checker reconstructs every ordered99x99 entry independently with typed
vertex-pair cases and compares both saved initial matrices and both C01 arrays.

For a partial symmetric binary adjacency, write d_lo for a row's number of
known ones and d_hi for known ones plus unknown entries. For a pair x,y,
write c_lo for the number of vertices known adjacent to both, and c_hi for
the number at which neither incident entry is known zero. In any completion,
the exact degree/common-neighbor count lies in those integer intervals.
Possible shared variables or additional constraints can only narrow them.
For the target, every degree is14 and the required common count is1 for an
edge,2 for a nonedge. These are direct integer consequences of the defining
target identity and, with the symmetric binary zero-diagonal condition,
are equivalent to it.

Each logged force is checked against the exact preceding partial state.
The edge must still be unknown, the witness must name the affected constraint,
and the original interval must permit its target. The checker then assigns
the **opposite** of the proposed value in a temporary copy. It requires that
the named constraint's integer interval can no longer contain its target.
Thus no full target completion can use that opposite value. The force
preserves precisely the set of possible target completions.

The admitted rule vocabulary is separately checked:

- Degree bound: the forced edge touches the witness row; a tight lower bound
  forces0, and a tight upper bound forces1.
- Adjacency from common interval: the witness is the forced pair itself.
  Its common-count interval permits precisely one of the two adjacency values.
- Tight common lower bound: the witness pair is already fixed; the recorded
  intermediate vertex forms a one/unknown wedge. A saturated lower count
  forces the unknown leg0.
- Tight common upper bound: the pair is fixed, both legs remain possibly1,
  and its upper count equals the required count. Every such wedge must become
  present, so an unknown leg is1.

The counterfactual test supplies a second checking path to the explicit rule
preconditions; it does not reproduce the producer's scan or propagation code.
Induction over the complete saved ordered trace proves completion equivalence
between each starting matrix and its final matrix. All recorded forces in
these two runs happen to be zero assignments.

Finally the checker evaluates all row and pair intervals and independently
enumerates whether any of these four rules can still force an unknown entry.
This establishes a fixed point for this specific rule set, not a general
consistency decision, binary feasibility, or target construction. The trace
length/remaining-variable counts are finite run facts only. The old archive's
uncertified fixed-Q1 UNSAT observations are not promoted by this audit.

Known-valid C5, Petersen and rook9 fixtures are checked by exact degree and
common-neighbor counts, then masked entries provide calibrated positive
force checks. All rule types have positive C5 witnesses; deliberately wrong
values, already fixed edges, unrelated witnesses, missing steps and changed
matrices must fail. The checker imports no producer, archive solver, or prior
propagation implementation. Python integer arithmetic, JSON/SHA256 and Git's
immutable blob lookup are shared trusted components. No automorphism,
asymmetry, universal fixed-Q1 coverage, or universal triangle containment is
assumed. The statement is conditional on each explicitly displayed matrix.
