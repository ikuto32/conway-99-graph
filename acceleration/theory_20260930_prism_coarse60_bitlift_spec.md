# Fixed coarse60 exact joint bit-lift encoding

Preregistered scope: the60 lexicographic coarse columns in the separately
audited `20260930_prism_coarse_complement/coarse_template.json`, each used once,
for the fixed six-prism core. Assign a coordinate bit to every selected
component/column position. Require full prescribed36x36 integer Gram and all
1770 distinct-column overlap caps. No complement pairing, target automorphism,
bit flips, first-column fix, or other symmetry normalization is imposed.
Coarse-word ordering merely names the60 columns; it does not cover every
coarse multiplicity template or every core. Residual D is absent.

Require independent local-domain gate `7087ce1ff80ffd93e186c2e0d642bb99b1b003262f79bb19862e05015a8c590d` before building. Its exact18 domains each contain136 masks over20 applicable columns, with weight10 and required half-marginals. For each domain allocate136 one-hot selectors. Allocate360 raw bits x[d,a] for columns d=0..59 and components a=0..5. No auxiliary bit stands for a free edge of a99-vertex adjacency matrix.

Exact-one semantics: let p0=s0. For each subsequent selector s_i create a
prefix p_i and emit the complete OR equivalence p_i iff p_(i-1) OR s_i,
plus not(p_(i-1) and s_i). Finally force the last prefix true. All135 prefixes
per domain are thus uniquely fixed and exactly one of136selectors is true.
Every selected mask implies all20 relevant raw bit literals. These forward
channel clauses suffice because exact-one chooses a mask and every raw bit
belongs to exactly one domain. There are2448selectors,360rawbits and2430prefix
variables, expected5238variables total.

For every unordered component pair a<b and every ordered fibre pair g,h,
there are135 pairs of domains. For each of136left selections, emit its
negation OR the complete list of right selectors whose selected bit1 support
intersection equals1 if g=h and2 otherwise. Under exact-one this is exactly
the binary compatibility relation. Save every136-bit allowed-neighbor mask
and every allowed/forbidden count. The local half-marginals and coarse quotas
then force all four coordinate-bit intersections to the same target, so these
constraints imply the entire off-component Gram, not merely bit11 counts.
Same-component distinct rows never share a column; each row has weight10.

For each distinct pair of coarse columns, find the components assigned to the
same fibre in both. Literal factor overlap counts precisely those components
whose two raw bits agree. For every triple of such components and each of
eight common-bit settings, emit the six-literal clause forbidding that
assignment. All such clauses are equivalent to overlap at most2; pairs with
fewer than three same-fibre components require no clause. Distinct balanced
coarse words cannot agree in five positions; explicitly verify the complete
pair population rather than relying on that bound.

Expected fixed clause sections before caps:9738exact-one,48960channel and
18360compatibility clauses. All dimensions, exact raw maps, clause ranges,
model/scope/source hashes and lossless gzip packages will be saved. Raw CNF
and body are retained even if oversized. New output directory only.

Limits: build and finite controls at most120seconds, no SAT/GPU invocation,
no floating arithmetic. Exact small one-hot controls check every assignment
through size7 and flipped auxiliaries; all64six-bit configurations calibrate
the eight equality-triple clauses. A separate auditor must reconstruct the
entire encoding and calibrate an independent complete raw-factor checker
before any research solve. Producer status remains CANDIDATE.

If SAT is later obtained, independently validate the complete assignment,
decoded36x60factor, prescribed Gram, one bit per component/column, all raw
caps and exact coarse scope. Canonical C0 column sorting may be performed
afterward using the factor's exact within-fibre Gram. A full factor is still
not a99-vertex graph. An independently checked UNSAT trace would exclude only
this fixed60-pattern template, with no claim against every six-prism factor.
