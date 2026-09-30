# Universal disjoint-cover redundancy in the fixed coarse60 template

This argument quantifies over every assignment of the 360 raw coordinate bits
of the exact saved 60 coarse words. It needs no Gram, margin or target-graph
assumption. It does not identify any triangle of an actual residual graph.

Independently group the words by the six-tuple obtained by subtracting the
first fibre label from every label modulo three. The raw words form exactly
20 classes of size three. In each class, every component uses all three
different fibres. The audit also verifies the producer's cyclic order and
complete rotation map against these independently formed classes.

A selected row has the uniquely decoded label (fibre, component, bit), encoded
as 12*fibre+2*component+bit. For two columns in one class, rows from different
components cannot coincide; rows from the same component have different
fibres and cannot coincide either. This is true for either bit value. The
checker verifies every one of the 8,640 local row-pair/bit possibilities across
all 60 within-class column pairs. Since any shared row would occur in one of
these possibilities, this finite local check establishes the universal claim
over all 2^360 global bit assignments. It is not a sampled assignment test.

The 20 classes cover all 60 columns once. The separate complete triple census
confirms that every selected triple has zero opposite-bit requirements. Thus
an existential triangle-cover extension containing only column exact-cover
constraints and conditional opposite-bit requirements always has a selector
extension: select these 20 triples and no others. Every original raw-bit
assignment survives. This proves that the proposed semantic condition is
redundant for this template, even before imposing Gram equations. No new
selector CNF implementation was built or approved by this result.

The actual residual graph still needs degree eight, mixed incidence equations,
its quadratic identity and triangle edges consistent with that graph. None
of those requirements is removed or implied by the coarse cover. The proof
does not construct a factor or an SRG99, apply to other templates, or assume
an automorphism of a hypothetical graph. The coordinate rotation is used
only to exhibit a partition of the fixed list of words.

The independent checker uses a quotient-class construction rather than the
producer's orbit walk. It imports no producer or prior checker code. It binds
all raw artifacts and the prior independent census/encoding gates, tests the
complete 1,296-case row-label injectivity table, and rejects eight corrupted
certificates. The proposed mathematical claim is
`C-SIX-PRISM-COARSE60-UNIVERSAL-DISJOINT-COVER-REDUNDANCY`, revision 1,
VERIFIED/CLEAR within this exact scope, with DERIVED and COMPUTED bases.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_coarse60_cyclic_cover.py --out build/coarse60-cyclic-cover-review-new
```
