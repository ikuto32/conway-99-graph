# Independent triplicate-count PSD audit

Let the columns of a real matrix F be partitioned into triples. For a triple with vectors a,b,c, direct expansion gives

`(a-b)(a-b)^T+(a-c)(a-c)^T+(b-c)(b-c)^T = 3(aa^T+bb^T+cc^T)-(a+b+c)(a+b+c)^T`.

Let N collect the triple sums. Summing the identity proves `3FF^T-NN^T` is positive semidefinite. The three differences in a triple span at most two dimensions, so its rank is at most twice the number of triples. In this 36-row, 20-triple application the resulting bound40 adds no restriction. This proof is over real matrices and needs no binary, column-cap or graph assumption.

For the fixed triangle core, the 36 non-root core vertices have cubic adjacency C and each has one root neighbour. On a diagonal the outside Gram entry is 14-1-3=10. For distinct core vertices i,j the required total common-neighbour count is 2-C[i,j]; subtract the number `(C^2)[i,j]` of common neighbours within the cubic core and one more if i,j belong to the same fibre. Thus the prescribed outside Gram is `G=12I-C-C^2+2J-U`, where U has three all-ones diagonal blocks. This is a necessary target equation. The audit also reconstructs C literally as three standard matchings with identity cross-fibre matchings, so its arithmetic does not assume the producer's G is correct.

The count profiles used here are the three already authenticated raw count-CSP objects. Their 36 by 20 matrix N has rows ordered by fibre then coordinate. Each column is the sum of the three columns supported on its corresponding raw support group, if a factor realizing those counts exists. Therefore their necessary test is exactly `M=3G-NN^T`.

For each candidate congruence the audit checks every rational entry of `T^T M T=diag(d)` and requires d nonnegative. It obtains T inverse and determinant using a fresh exact elimination, then checks both inverse products; no producer shear operation establishes this premise. For any real x, write x=Ty. Then `x^T M x=sum d_i y_i^2>=0`. Invertibility also gives rank(M)=the number of positive diagonal entries. A separate reverse-column elimination of M and direct nullspace multiplication provide another exact rank check. The three saved matrices each have rank22 and nullity14 if the executable audit passes.

The generic factor controls, including the independently authenticated SRG243 factor partitioned into consecutive triples, use their own Grams. They do not exhibit a factor for any of the three research profiles. Passing the necessary PSD test does not assert that these count profiles have Gram lifts, cross-column compatibility or target completions. Prior exclusion results remain unaffected. This review makes no novelty claim and does not approve the producer's historical search as exhaustive.
