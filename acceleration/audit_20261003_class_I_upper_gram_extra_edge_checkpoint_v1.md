# Independent written audit: class-I extra-edge boundaries

I, `/root/checkpoint_audit`, read the complete frozen candidate `docs/CANDIDATE_20261003_CLASS_I_UPPER_GRAM_EXTRA_EDGE_BOUNDARIES_V1.md` (5b126bf6b9ace4b0e570141e4cb26bbbc6e5dcea5ea0e57f735eee554df2fc37), its literal candidate record, the exact four-class construction, the historical upper-Gram derivation, the earlier four-class block paper, and the append-only witness-alignment correction. Structural produced the candidate after Root supplied the witness/repair ideas. Those shared origins are disclosed; this audit separately reconstructs the pair coverage, quadratic argument, cap checks, and congruences. Agreement among agents is not the checking method.

The exact three-part statement survives this written reconstruction. There is no assertion of target completion, of all larger extra-edge patterns, of induced family coverage, or of a global class-I exclusion. No graph enumeration, matrix arithmetic program, inverse calculation program, LP, eigensolver, mathematical fixture, formal checker, or external review was executed. Metadata reads and file identities are not mathematical executions. The frozen sources remain unchanged.

## Construction and all-pair coverage

Use the candidate's vertex labels and its complete neighbor sets, with pi=(12)(34), endpoint ell on rows1,2 and r on rows3,4. Every center s,t has degree6, and the other15 vertices have degree4, giving36 existing edges. Independently taking intersections of the written neighbor sets yields the following coverage of all136 unordered pairs. Here `own`, `pi`, and `opposite` describe row indices, not inferred adjacencies in an unknown target.

| Disjoint category | Number | Written intersection result |
| --- | ---: | --- |
| center-center within s,t,x | 3 | Existing edges, CN1 |
| centers versus A | 12 | s-A edges CN1; t-A CN2; x-A CN1 |
| centers versus B | 12 | t-B edges CN1; s-B CN2; x-B CN1 |
| centers versus F | 12 | CN1 via A, B, or endpoint respectively |
| centers versus endpoints | 6 | CN1; only x-endpoint pairs are edges |
| ell-r | 1 | Existing edge, CN1 via x |
| endpoints versus A | 8 | Own-side CN1, opposite-side CN0 |
| endpoints versus B | 8 | Own-side CN1, opposite-side CN0 |
| endpoints versus F | 8 | Own-side edges CN1 via pi partner; opposite-side CN1 via the other endpoint |
| A-A | 6 | CN1 via s, including pi edges |
| B-B | 6 | CN1 via t, including pi edges |
| F-F | 6 | Two pi edges CN1 via endpoint; four opposite-side nonedges CN0 |
| A-B | 16 | Four own edges CN1 via F; four pi nonedges CN2; eight opposite-side nonedges CN0 |
| A-F | 16 | Four own edges CN1 via B; four pi nonedges CN2; eight opposite-side nonedges CN0 |
| B-F | 16 | Four own edges CN1 via A; four pi nonedges CN2; eight opposite-side nonedges CN0 |

The category counts total136, and the edge counts total36. Thus every old edge has exactly one internal common neighbor and every old nonedge has at most two. Exactly36 pairs have CN0: 8AB+8AF+8BF+4FF+8 endpoint-row. This derives the candidate's universe afresh, rather than borrowing the class-IV optional24 universe.

For any added old nonedge uv with an old common neighbor z, uz is an old edge with one old common neighbor. The new uv gives uz an additional common neighbor v. Since v was not adjacent to u before, it was not the old common neighbor. All old neighbors remain in an extension, so the contradiction cannot be undone by other added edges. Therefore every admissible added edge belongs to the36 zero pairs. This argument uses only the partial adjacent cap at most1, not an erroneous requirement that a new edge already have its target triangle inside the17 vertices.

For an opposite-side Ai-Bj edge, the old nonedge s-Bj has old common neighbors t and Aj. The added edge supplies Ai as a third. If s-Bj remains a nonedge, the cap2 fails; if it is also added, its adjacent cap1 fails. Equivalently s-Bj is outside the zero universe already excluded above. Thus all eight AB pairs are individually impossible, including in simultaneous extensions. The other28 are not declared mutually compatible.

## Weighted necessity and the equality boundary

Take chi=(1,1,-1,-1) with endpoints ell=+1 and r=-1, and set the three center weights0 and all A/B/F weights2chi. These signs use the alignment addendum literally. The coordinate sum is0 and squared norm50. The six matching-edge groups contribute24+48 to the sum of edge products, endpoint-free edges contribute8, and ell-r contributes-1. Hence the total is79 and

`w^T U(H) w = 3*50 - 2*79 = -8`.

Direct row substitution gives Uw=0 at centers, A/B, and endpoints, and Uw(Fi)=-chi_i. For example the Fi neighbor weights sum to7chi_i, whereas3w(Fi)=6chi_i. Reversing chi alone changes the endpoint-free contribution to-8 and the quadratic to24; reversing the entire vector preserves-8. This falsifies the unaligned witness version while preserving the corrected candidate.

Every zero row-row pair crosses the signs and has weight product-4. Every zero endpoint-row pair joins an endpoint to an opposite-side A/B point, with product-2. There are no eligible endpoint-F or center pairs. Therefore all admissible extensions have

`w^T U(H+E) w = -8 + 8r_E + 4e_E`.

PSD gives2r_E+e_E>=2. Equality has only the integer cases(1,0) and(0,2). In the first case each A/B endpoint of the sole added row-row edge gains image2chi; a free endpoint changes from-chi to+chi. At least one image is nonzero, including the FF case. In the second case each added row endpoint is A/B and receives image chi from its opposite endpoint. A fixed row point has only one eligible endpoint, so two distinct simple added edges cannot cancel there or attach twice to that row point. Again Uw is nonzero.

For a symmetric PSD matrix, q(w)=0 implies Uw=0: otherwise choose v with w^TUv nonzero, and the linear term in q(w+tv) gives a negative value for one sufficiently small sign of t. Both equality cases are impossible. Thus the strict integer necessity is2r_E+e_E>=3. No sufficiency or exclusion for larger edge sets follows.

## The two-free-edge counterexample to a blanket Gram exclusion

Add mu=(13)(24) on the F vertices. Their four induced free edges form C4. There is no new triangle, so old edges retain CN1 and new mu edges have CN0. The following direct intersections exhaust every changed pair:

* Fi with its own endpoint keeps CN1; with the opposite endpoint its old common neighbor is the other endpoint, and Fmu(i) supplies one more, giving2.
* Fi with s,t,x keeps CN1 through Ai,Bi,E(i).
* Fi with its own A/B row keeps CN1, with its pi row keeps CN2, with its mu row rises from0 to1, and with the fourth row stays0.
* A pi-adjacent free pair has its endpoint as its sole common neighbor. A new mu-adjacent pair has none. The remaining free nonedge pair has exactly its two C4 neighbors in common.
* A pair with neither endpoint free has unchanged neighbor sets and hence unchanged common-neighbor count.

Thus all adjacent internal pairs have CN<=1 and all nonadjacent internal pairs CN<=2. Degrees are6 at s,t,5 at each F, and4 elsewhere. In a target the two new internal-CN0 edges would require their unique common neighbors outside this set. This is a necessary-cap example, not a target or a claim of exactly one internal triangle on every edge.

## Independent congruence reconstruction of positive definiteness

The four-row pi and mu permutations commute. Use their constant vector and three zero-sum sign characters, with normalized row character entries divided by2. The character with pi=+1 has mu=-1 and couples to the endpoint difference; the other two have pi=-1 and mu=+1 or-1. This is a basis of the explicitly defined17 matrix, not an automorphism assumption about a target. The dimensions are3+3+4+7=17.

On the endpoint-coupled character, A and B give leading U block[[2,-1],[-1,2]]. The two free matchings have H eigenvalue0, so the free U diagonal is3. Endpoint difference has U diagonal4 and squared free coupling2. Eliminating it leaves free diagonal3-2/4=5/2. The inverse-entry sum of the leading block is2, leaving scalar1/2>0. The full four-dimensional block is PD.

On the other characters, A/B leading block is[[4,-1],[-1,4]], with inverse-entry sum2/3. The free U diagonal is3 when mu=+1 and5 when mu=-1. The remaining pivots7/3 and13/3 are positive. Both three-dimensional blocks are PD.

The seven-dimensional constant part splits under s/A versus t/B exchange. The odd two-dimensional quadratic has matrix[[4,-2],[-2,3]], leading pivot4 and determinant8, hence PD. On the even part set s=t=c, x=z, ell=r=e, all A/B values p and all F values f. Counting the written edges gives the exact quadratic

`4c^2+3z^2+4e^2+8p^2+4f^2 -4cz-4ze-16cp-8ef-16pf + (2c+z+2e+8p+4f)^2/9`.

This reconstructs B' and j rather than assuming their signs. The extra two FF edges contribute-4f^2 relative to the old constant quadratic. Eliminating z with pivot3 leaves the c,e block(4/3)[[2,-1],[-1,2]], whose inverse is[[2,1],[1,2]]/4. The p/f coupling columns are(-8,0) and(0,-4). Their correction is[[32,8],[8,8]], giving remaining block[[-24,-16],[-16,-4]]. Its determinant96-256=-160 proves one positive and one negative direction. Therefore B' has inertia(4,1,0).

For v=(-1,-3/5,-2/5,-3/5,-3/5), the five direct row products B'v are

`-4+6/5+24/5=2; 2-9/5+4/5=1; 6/5-8/5+12/5=2; 8-24/5+24/5=8; 8/5+24/5-12/5=4`.

Thus B'v=j exactly. The scalar j^Tv=-2-3/5-4/5-24/5-12/5=-53/5. In the bordered matrix[[B',j],[j^T,-9]], eliminating B' adds positive pivot-9+53/5=8/5, giving inertia(5,1,0). Eliminating-9 instead gives B'+jj^T/9 plus one negative pivot. Hence that five-dimensional even quadratic has inertia(5,0,0). Along with the odd and character blocks, all17 directions are positive.

For the target consequence I separately rederive A^2=12I-A+2J, AJ=JA=14J, J^2=99J and G=27I-9A+J. Expansion yields G^2=1701I-567A+63J=63G; therefore G is PSD and every principal G/9 is PSD. This justifies the necessary premise for an actual target extension. It supplies no converse to the positive small Gram.

## Written falsification boundaries and verdict

The20 written checks are: exact class-I rather than class-IV labels; all136 unordered pairs covered;36 old edges all CN1;36 zero pairs count; monotonic old-edge saturation under simultaneous additions; eight AB vetoes; distinction between partial CN caps and completed target CN; endpoint sign alignment; norm50/product79/quadratic-8; Fi-only initial image; exact added-edge weight products; both equality integer cases; no cancellation for distinct endpoint-row edges; no new repair triangles; all free-incidence pair categories; new FF CN0 and exterior triangle need; all17 invariant dimensions; theta and both uncoupled positive scalars; common odd determinant8 and residual determinant-160; five exact substitution rows and bordered pivot8/5.

No material mathematical veto was found for the literal three-part candidate statement. The result covers only the specified small graph, necessary extension restrictions, and this explicit PD repair. Larger admissible edge sets, target occurrence, induced-family coverage, actual triangle completeness, and global class-I exclusion remain unresolved. Written agreement cannot replace any later executed full certificate or realization check.
