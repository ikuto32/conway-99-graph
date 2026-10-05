# Universal min-count upper envelopes on the literal support

Status CANDIDATE; source produces an inventory only, not an approved encoding.

Fix one nonmatching coordinate pair a<b, fibres f,h, and the five support groups
that contain both coordinates. In a group let u and v be the counts, across its
three columns, of the two selected row vertices. Their overlap is at most min(u,v).
All other groups contribute zero. Hence the prescribed Gram entry K requires

    sum_g min(u_g,v_g) >= K.

This bound is valid for any binary columns. It does not assert that the upper
bound is attainable inside a constrained local catalogue. In particular it does
not contradict or reverse the independently refuted equality between elementary
Frechet bounds and exact class intervals. It remains only a necessary test for
the fixed-support full-Gram factor problem.

For any nonnegative integers u,v and K in{1,2}, let

    p_t = [u>=t] AND [v>=t], 1<=t<=K.

Then sum_t p_t=min(u,v,K). Because all group contributions are nonnegative,
sum_g min(u_g,v_g)>=K if and only if sum_g min(u_g,v_g,K)>=K. Thus truncation at
the target preserves precisely this scalar inequality, even if a count is3.
The existing exactly-one count channel expresses [u>=t] as an OR of precisely
those alternatives whose selected count is at least t. Bidirectional OR and AND
clauses uniquely determine the new auxiliaries.

At least one of five variables is their positive disjunction. At least two of
ten variables is the conjunction of the ten positive nine-variable disjunctions
obtained by omitting one variable: zero or one true variable falsifies a clause,
whereas two or more true variables satisfy every clause. Therefore the proposed
CNF extension is equivalent to all540 scalar upper inequalities, conditional on
the original count-channel meanings. This equivalence does not make the count
relaxation equivalent to a factor. Full exact Gram, cross-column caps, residual D
and target existence remain outside it. No target automorphism or normalization
is used beyond the literal fixed input support.

The earlier exact-interval model uses extrema over complete local count classes
and is generally stronger. The six earlier partial cuts isolate specific scalar
failure regions. This inventory assesses the cost of applying the elementary
upper inequality uniformly to every positive target cell; it makes no timing or
solver performance claim.
