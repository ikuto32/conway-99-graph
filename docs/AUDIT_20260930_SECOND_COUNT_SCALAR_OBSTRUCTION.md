# Exact second-count-profile obstruction

This audit is limited to the literal count profile `086fc4155012236d30b13756b01e48ed2050db7cf028274b4aea533333ef0f17` on the saved six-prism Hadamard support. Local domains include the prescribed local Gram upper bounds and within-triplicate column overlap caps. Cross-group column caps and residual D are not used. This is not an exclusion of all eight-exception profiles, the entire support, the core or Conway99.

For a coordinate pair (a,b), only the five support groups containing both can contribute to `F_(a,f) · F_(b,h)`. Within each group its three columns form a complete local option in the count-compatible domain. Let M_g be the maximum overlap over every such local option. Then every possible completion satisfies the exact integer inequality

`F_(a,f) · F_(b,h) <= sum_g M_g`.

No choices across groups are assumed compatible in deriving this upper bound. Ignoring that coupling can only weaken an upper bound.

For (a,b)=(9,11) and (f,h)=(2,1), the required entry derived from the raw core is2. The five contributing groups are1,5,8,18,19. Complete initial domains have21,21,150,21,21 options, and their maxima are0,0,1,0,0. Thus the entry is at most1, a contradiction. The saved independent certificate includes every local option, its three words, its contribution and the bound-attaining indices. No SAT proof is needed for this particular inequality.

The companion checker independently regenerates all90 balanced words and all117,480 distinct word triples; it checks local Gram and within-group caps, reproducing the31,110 catalogue. It reconstructs all20 initial domains from the raw count table. Every one of540 scalar intervals and its producer-saved attaining witnesses is checked. A separate direct Cartesian-product computation verifies all prefix sum sets for the60 blocks; it does not import or reuse the producer's DP. Exactly one scalar cell and one block fail; the other59 block witnesses are separate choices, not a joint factor.

Known feasible five-permutation blocks and a genuine243 residual factor provide positive controls. Altered bounds, targets, memberships, groups and witnesses must reject. The reviewer previously produced the second lift CNF, but no part of that CNF or its producer is used here. The scalar obstruction was discovered by a different agent; this path uses only raw count/core/catalogue artifacts and standard-library arithmetic.
