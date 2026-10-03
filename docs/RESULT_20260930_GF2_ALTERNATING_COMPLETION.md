# Outcome of the binary residual-completion diagnostic

The frozen exact run completed in 1.5 seconds. Its status remains CANDIDATE,
pending independent review. No Conway99 factor or graph was produced or excluded.

The proposed algebraic clarification is that a valid even-cell triangle Gram
factor has an alternating binary solution of the linear mixed equation precisely
when it has any binary solution. Symmetry and zero diagonal therefore add no
linear obstruction in this domain. Requiring even residual row sums additionally
tests the image of the all-one vector when it belongs to the row space of F;
this condition is not claimed to be automatic for all valid factors. The quadratic
residual equation is still absent from this linear completion test.

Every one of the 4,096 pairs of binary 2-by-3 matrices F,H was compared with all
eight alternating D. The alternating and even-degree criteria agreed with the
complete populations. A generic 2-by-4 example separates those criteria; it is
not a triangle factor. All 512 small block-completion populations attained the
bound 2 rank([B,E])-rank(B), and 64 small rank controls agreed with complete spans.

For the genuine SRG243 fixture, full integer graph checking and the literal
triangle relabelling passed. Its binary ranks are rank(A)=110, rank(B)=42,
rank([B,E])=60 and rank(F)=57. The lower bound is only 78. Both linear completion
criteria pass and the saved actual residual D supplies a positive witness.

The four saved connected 36-vertex cores each have rank(B)=30; the six-prism core
has rank(B)=26. The three common kernel vectors give rank([B,E])<=36 for any
incidence matrix with the required even cell-column sums. The rank54 test is
therefore automatically satisfied on these five cores. This is a conditional
non-obstruction, not a general rank theorem for all matching/permutation cores.

The deliberately invalid six-K3,3 scaffold has rank(B)=16 and fails local
common-neighbor caps. Among the 64 fixed-seed scaffolds, 56 pass the local caps
and eight fail them; their rank(B) values are 32, 34 or 36. This finite population
is not exhaustive. Both saved annealer objects have lower bound46, but fail full
Gram in 442 and 402 ordered entries respectively; neither is treated as a factor.

The source, spec, proof and all raw controls are bound by
`acceleration/results/20260930_gf2_alternating_completion/summary.json`, SHA256
`8abffdf66cb15dbfca6e6d0f29adf2425a9975832aeac5f5187c2c4da901fe98`.
The prior archive discussion of binary projectors was checked at immutable
commit85e705cc6c2a14d123120c93a847e30aaab1789e. No novelty is asserted.
