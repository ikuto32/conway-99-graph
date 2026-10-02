# Conditional rooted-eight model and universal rooted-five products

This is a producer derivation, pending independent complete review. The
mathematical premise is global absence of an induced triangular prism in a
hypothetical `srg(99,14,1,2)`. It concerns necessary local induced-subset counts
at a fixed ordered nonedge `(u,v)`, with no target automorphism assumption.
An exact infeasibility certificate would exclude only that conditional model
and its explicitly bound profile parameters after coverage and necessity audits.
An exact nonnegative primal is a local count relaxation witness, not a graph.

## Definitions and dependencies

For each finite rooted flag `H` of order `h`, the two roots are labelled `0,1`
and all other labels are free. Encode edges in the lexicographic pair order
`(0,1),(0,2),...,(h-2,h-1)`, with the first pair in bit zero. Canonicalize by
the minimum integer mask over every permutation of the free labels, fixing
both roots individually. `x_H` counts unordered `(h-2)`-subsets of the other
97 vertices which induce that rooted flag. No division by an automorphism-group
size occurs in `x_H` or in coefficients below.

Universal rooted-five actual counts `c_F` use
`C-UNRESTRICTED-ORDERED-PAIR-ROOTED5-RIGIDITY` revision 1. The conditional rooted-six
counts are the independently checked integer affine family
`x6_H = origin_H + a*basis0_H + b*basis1_H`, with
`a in {0,...,20}`, `b in {0,...,9}`, from
`C-PRISMFREE-ORDERED-NONEDGE-ROOTED6-INTEGER-DOMAIN` revision 1. The parameter
population consists of all 210 points, fixed before any guide results.

The root-seven universe is bound to the independent complete coverage record
`C-UNRESTRICTED-ROOTED7-NONEDGE-LOCAL-CATALOGUE-COVERAGE` revision 1. Its full
earlier marked/rerooted necessary model is retained. Its count variables remain
unknown: an arbitrary previously feasible root-seven vector is not fixed.
The root-seven model derivation is separately undergoing independent review.

## Catalogue coverage argument to audit

Every prism-free root-eight flag deletes any one of its six free vertices to
a prism-free root-seven flag with the same ordered nonedge roots. Generate every
one of the 2,750 covered root-seven flags with every new-vertex neighborhood
among its seven vertices, giving 352,000 labelled attempts. Reject only a
failure of the inherited exact local cap (at most one common neighbor for an
edge, at most two for a nonedge) or an induced prism on one of the six-subsets.
Keep the free-label canonical representative. A hypothetical target subset must
pass both tests. The v2 producer retained 20,253 classes; this cardinality and
the complete retained catalogue still require independent reconstruction.

## Marked extension equations

For each root-seven parent `H`, start with the deletion identity
`(99-7)*x_H = sum_K d(H,K)*x_K`, where `d(H,K)` is the number of free-vertex
deletions of root-eight `K` yielding `H`. Each actual parent subset has 92
external choices; each union subset contributes once for every corresponding
free deletion. The total equation is `sum_K x_K = binomial(97,6)`.

For marked degrees, partition all seven parent vertices into orbits of the
finite parent flag's automorphisms fixing its roots. For an orbit `O`, sum
`14-degree_H(z)` over `z in O` on the parent side. For each free deletion of `K`
yielding `H`, transport `O` by a canonical isomorphism to that undeleted copy;
the child coefficient is the number of incidences of the deleted vertex with
the transported `O`, summed over all such deletions. Every external actual
vertex incident with a marked parent vertex is thereby counted once.

For marked common neighbors, use orbits of unordered vertex pairs. Sum
`(1 if yz is an edge else 2) - |N_H(y) intersect N_H(z)|` over the orbit on the
parent side. The child coefficient counts deleted vertices adjacent to both
vertices of each transported pair, summed over all deletions. Different
canonical isomorphisms differ by a parent automorphism, so orbit sums are
unchanged. These finite-flag orbit sums do not assume any symmetry of the
hypothetical 99-vertex target.

In raw rows, move the parent term left: its coefficient is the negative
parent-side sum and all child coefficients are nonnegative integers. The RHS
is zero except for the total count equation. There are 70,297 new marked/total
rows. Independent review must check the complete orbit partitions, transports
and every coefficient, not only a subset of rows.

## Exact product equations

For each actual primary root, choose ordered pairs `(S,T)` of three-free-vertex
subsets. Their individual rooted-five flags have counts `c_F,c_G`, so the number
of ordered pairs of a particular type `(F,G)` is exactly `c_F*c_G`. Classify
each pair by its union, which has rooted order five through eight. For each
union representative `H`, enumerate every ordered pair of triples whose union
is the entire free vertex set of `H`, and count its induced flag types.
This gives a coefficient depending only on `H`, multiplied by its actual
unordered induced-union count `x_H`.

Storage has one row for each upper pair `F<=G`: diagonal counts both subsets
with the same type and has RHS `c_F^2`; off-diagonal aggregates the two ordered
orientations and has RHS `2*c_F*c_G`. There are `87*88/2 = 3,828` rows. Across
all stored upper types, each union flag contributes respectively 1, 12, 30 or
20 ordered triple pairs for orders 5, 6, 7 or 8. These cover intersections of
sizes three, two, one and zero, respectively.

The order-five contribution exists only on a diagonal and is exactly `c_F`,
because `S=T`. Write the order-six coefficients `q_FG,H`. Substituting the
known affine root-six family leaves the exact RHS triple

```
constant = c_F*c_G*(1 if F=G else 2) - (c_F if F=G else 0)
           - sum_H q_FG,H * origin_H
a_coefficient = -sum_H q_FG,H * basis0_H
b_coefficient = -sum_H q_FG,H * basis1_H
```

Unknown terms are only root-seven/root-eight counts with their nonnegative
integer union coefficients. All collision terms and overlaps are included;
there is no disjointness simplification or numerical identity assertion.

## Raw artifacts, indexing and actual controls

`acceleration/results/20261002_rooted8_universal5_product_model02/model.json`
has SHA256 `a2162b5edc4eb68952cc9887156c5d0cd731aaaf9a6b5f94f446174b9d10528b`.
Its first 2,766 variables are the unchanged raw root-seven model: 2,750
`[7,canonical_mask]` entries, eight reroot parameter aggregates and eight
nonnegative aggregate-bound slacks. The next 20,253 entries are
`[8,canonical_mask]`, ordered increasingly by mask. Every equation uses
`terms:[[variable_index,integer_coefficient],...]` and
`rhs_affine:[constant,a_coefficient,b_coefficient]`. No floating scaled matrix
is the mathematical input. It contains 85,874 rows and 968,172 nonzero terms.

The same directory contains descriptive `extension_rows.json`,
`product_rows.json` (SHA256
`ca205a283ef8ea39db79807444b06544e76fa4cf7b1032ba07d27e95bb3fcb9a`),
the complete catalogue, immutable prefix checkpoints, manifest, controls and
summary with actual command/source/tool/input pins. Stage counts do not measure
target-wide graph coverage.

The build controls check all new extension/product rows against directly
counted Petersen `srg(10,3,0,1)` flags, with its own parameters and rooted-five
counts. A later separate discovery-agent calibration reads raw product rows
and uses separately written adjacency sets and all free permutations, with no
producer imports. All 3,828 rows at every one of 60 ordered Petersen nonedges
pass, totaling 229,680 row calculations; actual altered coefficient/count
evaluations fail. Its report has SHA256
`d351ab8188861f0a847e0558345fb7b4f6e250e32533110dc6fdc73f6b8be95d`.
These are calibrated producer checks, not independent approval. Exact failure
preservation and the late pre-build control-gate instruction are disclosed in
`docs/DEVIATION_20261002_ROOTED8_BUILD_CONTROLS.md`.

Optimizer guides and any exact corner primals/Farkas certificates are separate
artifacts. An exact vector must pass every unscaled integer row/column. Claims
remain CANDIDATE until a separate agent reviews the raw artifact and exact
statement. Target resolution: UNKNOWN. Overall search coverage: UNKNOWN; no
validated denominator.
