# Why all root group permutations give valid necessary cuts

Write a root-neighbor symbol as `(g,b)`, where `g` is one of seven matched root
groups and `b` is its sign. For any permutation `p` of the groups and sign vector
`m`, map `(g,b)` to `(p(g), b XOR m[p(g)])`. Fix the root and map every outer
vertex to the vertex labeled by the image of its unordered pair of symbols.
This is a bijection of all 99 vertices. It preserves the root matching, label
incidence, common-neighbor counts, and whether two outer supports intersect in
zero, one, or two groups. In particular it permutes the 1,680 disjoint unknown
edges and takes a completion to a completion of the relabeled overlap graph.

For each complete overlap graph, the semantic constraints used here are the
root-neighbor/outer common-neighbor equalities and the outer-pair inequalities
obtained by dropping nonnegative unknown-unknown products. Their constants and
coefficients are derived from actual adjacency. Consequently they remain valid
after every such relabeling. The multipliers `alpha` of equalities may have either
sign; the multipliers `beta` of inequalities are nonnegative. Summing them gives
`sum(c_e x_e) <= RHS`. Since every unknown satisfies `0 <= x_e <= 1`, every
completion necessarily satisfies

```
score = RHS - sum_e min(0, c_e) >= 0.
```

No fixed overlap or disjoint compression matrix enters this implication.
Relabeling may change a graph's compression coordinates, which does not affect
the cut's validity. Upper-bound certificate multipliers are omitted throughout.

`group_orbit.py` applies a group permutation first. The unchanged CUDA evaluator
then applies all 128 target-group sign masks. These enumerate the group of
`5040 * 128 = 645120` root relabelings when all group permutations are requested.
The script stores the actual selected permutations, tested counts, and each
minimum's permutation/cut/sign witness. It reconstructs that witness via a
separate symbol-level map and recomputes its score directly from all 99 vertices
using `graph_constraint`, independently of the expanded native score formula.
Only the tested minima/witnesses receive this semantic cross-check; all other
native scores inherit the previously audited evaluator's correctness.

A negative witness excludes its particular complete overlap assignment. Passing
sampled relabelings is weaker than passing the entire group; even a complete
group-orbit pass is only a necessary condition, not a completion witness.
