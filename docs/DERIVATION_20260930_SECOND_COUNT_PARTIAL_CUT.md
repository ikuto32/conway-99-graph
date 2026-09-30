# Candidate five-channel partial obstruction

Fix the saved six-prism support L, but do not fix a complete count profile. Consider rows (coordinate9,fibre2) and (coordinate11,fibre1), whose prescribed Gram entry is2. The only groups whose supports contain both coordinates are1,5,8,18,19, each with three columns. For each such group g, let A_g and B_g be the sets of its columns selecting those respective rows. If their counts are u_g and v_g, then

`(FF^T)[(9,2),(11,1)] = sum_g |A_g intersect B_g| <= sum_g min(u_g,v_g)`.

This elementary bound uses binary entries and literal support membership, not local Gram pruning, within-group caps, a local catalogue, cross-group caps or residual D. It also holds before any row or column margin equations are imposed.

The verified second count profile has count pairs, in the group order above, `(2,0),(0,2),(1,1),(2,0),(0,2)`. Its universal upper bound is therefore1. The exact catalogue maxima agree, but are unnecessary for this argument.

The following five partial scalar restrictions already force the contradiction:

* group1: coordinate11/fibre1 count is0;
* group5: coordinate9/fibre2 count is0;
* group8: coordinate9/fibre2 count is at most1;
* group18: coordinate11/fibre1 count is0;
* group19: coordinate9/fibre2 count is0.

All other counts are unrestricted. In particular, no signature or count choice for any of the other fifteen groups is fixed. Every binary F on this literal support having the required Gram entry must violate at least one of these five bounds. This is a necessary cut for full-Gram completions, not an implication of the weaker count-CSP alone. The saved count-CSP SAT witness is a concrete counterexample to that latter, incorrect interpretation.

In the frozen count-master, each coordinate/group incidence has an exactly-one family of channel selectors for its three-fibre count vector. There are two direct encodings of the partial obstruction. First, negate the five particular channel selectors chosen by the second count profile. Their simultaneous truth implies the five scalar restrictions; this gives a five-literal negative clause. Second, form the single positive clause containing every selector at each of these five incidences whose selected component exceeds the stated bound. Exactly-one channel semantics makes that clause equivalent to requiring a violation of at least one bound. It excludes a larger set of partial count assignments and implies the five-negative clause. The two emitted clauses are separately valid alternatives; the weaker one is redundant if the stronger one is used. No new variables are needed.

The broader positive clause ranges over the explicitly saved existing channel alternatives only. It does not claim coverage of an unspecified table universe. Its five-incidence truth table has 10*10*7*10*7=49,000 assignments. These are local channel choices, not globally feasible count-master assignments or factor witnesses. Likewise, binary-strip controls showing each removed bound permits overlap2 establish only local insufficiency of the weakened inequality; they do not construct a full factor.

Before source execution, the protocol was expanded to the six ordered distinct-fibre pairs (f,h). Each uses the same five groups: restrict the coordinate11/h counts in groups1 and18 to0, the coordinate9/f counts in groups5 and19 to0, and the coordinate9/f count in group8 to at most1. Each literal prescribed Gram entry is separately checked to be2, and the same sum-of-intersections argument applies directly. No symmetry or covariance premise is needed. The preferred proposed extension consists only of these six positive escape clauses; the original five-negative clause remains a comparison/control artifact. The six local truth tables comprise294,000 cases. No other coordinate pair or bound template is enumerated.

The production script authenticates the raw support and Gram, derives the complete five-group/15-column contribution set, enumerates all64 binary strip pairs and exact16 count maxima, compares the exact full-profile catalogue maxima diagnostically, maps every clause literal to the frozen count-master channel, checks the full local truth table, and confirms the authenticated actual count-CSP assignment falsifies both cuts. All new artifacts are candidates until independently checked. No formula is mutated, no solver is run, and no target-graph or automorphism claim is made.
