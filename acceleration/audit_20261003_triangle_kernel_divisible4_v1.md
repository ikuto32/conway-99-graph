# Independent triangle-kernel weight divisibility proof

As of: 2026-10-02 20:09:28 UTC (UTC). Source commit:2d578fa8171597d7a009f02f0d92ee987de24555.
Discovery:/root/structural. Independent derivation and checking:/root.
Artifact availability:LOCAL_ONLY pending immutable publication. External review:null;
reason:no external review requested or observed. Executable controls:null;
reason:this is a complete written integer argument, not a computational claim.

Exact statement: for every99-by99 symmetric binary zero-diagonal integer matrix
A satisfying A squared=12I-A+2J, let B contain all graph triangles as binary
incidence columns. Every u in ker_GF(2)(B transpose) has weight divisible by4.
The conclusion is conditional on the target identity. The zero kernel remains
allowed; neither existence nor nonexistence follows.

I independently recomputed the support moments rather than relying on the
discoverer's conclusion or historical VERIFIED label. Each diagonal identity
entry gives degree14; each edge has exactly one common neighbor. Thus each
vertex belongs to exactly seven distinct triangles and these triangles
partition its incident edges. Let S be the support of a kernel vector, with
s=|S|. Every triangle meets S in0 or2 vertices. Each vertex in S therefore
has exactly seven neighbors in S. The handshake lemma gives7s even, so s is
even. This applies also to the empty support.

For a vertex outside S, put d_v=|N(v) intersect S|. Each of its incident
triangles contributes either0 or2 neighbors in S, hence d_v is even.
Counting edges leaving S gives sum_outside d_v=14s-7s=7s.

Over the integers, write x for the0/1 indicator of S. Then
x transpose A x=7s and
x transpose A squared x=12s-7s+2s squared=5s+2s squared.
The left side is sum_all_vertices |N(v) intersect S| squared. Its contribution
inside S is49s. Consequently sum_outside d_v squared=2s(s-22).

For every even integer d=2r,
d squared-2d=4r(r-1) is divisible by8. Summing these exact congruences outside
S yields8 divides2s(s-22)-14s=2s(s-29). Therefore4 divides s(s-29).
Because s is even, s-29 is odd and invertible modulo4; hence4 divides s.
No spectral, numerical, symmetry or nonzero-kernel assumption enters this step.

The previously independently derived nonzero weight interval36 through60 is
a separate premise (written audit audit_20261003_incidence_griesmer_v1.md,
SHA25665d8eea3f4d72eb56391284f95eb43ad021e92a88a41fdcc2fe7a2e10f9dd92d).
Combining it with the proved divisibility restricts nonzero weights to
{36,40,44,48,52,56,60}. A new seven-weight encoding or dual needs new exact
artifact checking; the earlier13-weight gate does not approve changed input.

Failure challenges: the outside even-degree premise uses all actual graph
triangles and the exact edge condition. A merely linear hypergraph need not
partition actual graph edges into unique triangles. Replacing the target
identity by a different SRG changes the moments and cannot retain this
congruence without a separate derivation. Self-orthogonality alone gives even
weights, not divisibility by4. No such shortcut was used here.

Historical provenance, separately read: YesterdaysLemon/conway-99-research,
pinned commit85e705cc6c2a14d123120c93a847e30aaab1789e,
verification/wave102-prism-incidence-code/verification-report.md, section4,
SHA256a2cdab57ea3311e67a17f18bee6d332bfe5f6f6f0564873537295c27463077a8.
The archived argument already records this divisibility. This new written
review establishes the exact conditional statement above; it makes no novelty
claim and does not rename, rewrite or freshly endorse the entire archive.

Verdict:VERIFIED within the exact conditional scope by independent derivation.
Claim binding/ledger registration:pending. Target resolution:UNKNOWN.
Overall search coverage:UNKNOWN; no validated denominator.
