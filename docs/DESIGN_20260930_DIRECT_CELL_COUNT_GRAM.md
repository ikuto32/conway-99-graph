# Candidate direct-cell formulation on the literal support

The primary variables are the1,080 allowed entries of F, with the fixed support
L retained in its original60-column order. Exactly-one fibre per coordinate
and exactly-two coordinates per fibre/column give precisely binary36-by60
arrays with this L and the necessary per-column fibre margins. There is no
word catalogue selector, triple ordering, cyclic condition, global fibre
normalization, balance assumption or target automorphism assumption.

Each nonmatching coordinate pair occurs together in exactly15 columns. The
product of its two chosen fibre entries in each column is represented by an
exact AND gate. Their sum is the corresponding prescribed Gram entry:1 for
the same fibre,2 for different fibres. These540 equations cover all positive
off-diagonal Gram entries. The other90 upper-triangular entries vanish from
the fixed support and the exactly-one fibre constraints. Every diagonal is
the row sum10. Standalone prefix counters enforce those36 sums directly.

Alternatively, retain the verified count-master. Its existing incidence
channel fixes the three group-column counts for a coordinate. Conditional
three-bit cardinality maxterms force these counts to equal the raw F entries.
The master's complete coordinate domains imply every row sum10. Its group
signature membership is automatically necessary for a full-Gram F satisfying
within-group caps, since sorting the group's three distinct words places it
in the complete31,110 local catalogue. Hence count coupling preserves exactly
the same raw F solution set as the standalone within-cap formulation, subject
to the previously independently checked count-master coverage. This proposed
converse still needs independent review before an encoding claim.

For a pair of columns, a shared coordinate contributes1 to their overlap
exactly when the two chosen fibre labels agree. Under the two exactly-one
triples, the six clauses per equality flag are equivalent to this statement:
the three joint same-fibre selections imply the flag; the flag and the first
selected fibre imply the second selected fibre. Therefore an at-most-two
constraint on these flags is exactly the literal column-overlap cap. Supports
with at most two common coordinates require no cap clauses. This uses the
actual support intersections, not the refuted0-or3 premise. The within-group
and all-cross-group constraints are inventoried as separate extensions.

The ≥7 prefix imposes an additional count restriction proved necessary for
possible target factors with all column caps. It is not silently treated as
a consequence of full Gram and within-group caps alone. The all-caps baseline
has the same factor scope as the older ordered5,400-selector fixed-L model,
up to the latter's equal-support column permutation. Neither includes D.
The older direct Wave149/shift6 model and arbitrary-core models use different
core/support scopes; their existence is acknowledged, not a proof that this
literal count-coupled formulation was already built.

Only a streamed clause/ID/ASCII inventory is run. It retains compact cell,
product, prefix and cap recipes, never a research CNF or a global clause list.
All exact counts are candidate engineering evidence; lower size does not
establish faster solving. A future build requires fresh source, exact model
and object audits, and separate authorization for a native attempt.
