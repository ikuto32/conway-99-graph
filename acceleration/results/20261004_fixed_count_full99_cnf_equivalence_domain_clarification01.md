# Append-only nontrivial SRG domain clarification

This qualifies, without rewriting, the candidate paper
`docs/CANDIDATE_20261004_FIXED_COUNT_FULL99_CNF_EQUIVALENCE_V1.md`, SHA256
`950803fbbdda79e46f5680d18a9872132d1077b486d2adafc85b187ec6188c44`,
and its raw candidate SHA256
`6d7500129ce37ba26bd0d3ba87f8f9ec98ef689e053891c479a3812b6b98beb8`.
Claim ID and revision remain
`C-FIXED-COUNT-LABELLED-SRG-CNF-COMPLETION-EQUIVALENCE`, revision 1;
this is a required domain qualification of its still-unapproved candidate.

Native independently identified the literal boundary m=1, N=2, v=3, k=2,
H=[0], B=[1,1] and the singleton allowed exterior bit {1}. Its only completion
is K3. It satisfies all degree/block equations and the matrix identity, yet
the conventional nontrivial SRG definition excludes k=v-1. Thus the unqualified
generic use of the term SRG in the original candidate is too broad.

Whenever the original candidate's equivalence is stated using conventional
SRG(v,k,1,2) nomenclature, add the assumption

    0 < k < v-1.

Under that assumption the proof's matrix identity and binary simple k-regular
domain give exactly the asserted adjacent/nonadjacent common-neighbor
parameters, with both adjacency and nonadjacency classes nonempty. Without
that assumption the same construction remains equivalent to the explicitly
stated degree/common-neighbor matrix identity and pair restrictions, and
must be described in those terms rather than as a nontrivial SRG.

This qualification leaves the target v=99,k=14 and calibration rook v=9,k=4
unchanged. It changes no caller code, helper, specification, literal plan,
count vector, formula, gate, execution history or original candidate bytes.
It establishes no independent approval, graph, target exclusion or registered
status. Native's mathematical review remains distinct; no program or fixture
was executed to produce this clarification.
