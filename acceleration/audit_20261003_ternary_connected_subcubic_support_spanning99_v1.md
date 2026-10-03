# Independent written derivation: connected subcubic residual support spans99

Discovery producer: `/root/checkpoint_audit`. Independent verifier:
`/root/structural`. Written review timestamp:2026-10-03T05:08:28+00:00.
The discovery source is
`docs/CANDIDATE_20261003_TERNARY_CONNECTED_SUBCUBIC_SUPPORT_SPANNING99_V1.md`,
SHA256 `ae30674d5d024aef03da62bcfde3cb51d7aeb3aa0cd327b8827744f84d5c3668`.
This is an exact human-checkable written proof. No mathematical program,
fixture, exhaustive computation, engine or live claim-registry change was used.

## Exact statement checked

For every 99-by-99 symmetric binary zero-diagonal matrix A with exactly14 ones
in each integer row, put M=(A^2+A-12I-2J) modulo3 and let H be its simple
nonzero unordered off-diagonal support, with isolated vertices discarded.
If H is nonempty, connected and has maximum degree at most3, then H has
exactly99 vertices. No support with99 vertices is asserted realizable.
Disconnected and higher-degree supports are outside this claim, and it does
not resolve target existence or nonexistence.

Connectivity is a premise about the whole nonisolated residual support H,
not about A. No adjacent-common-neighbor1, incidence, fixed labelled graph,
automorphism, prescribed internal adjacency or floating-point assumption enters.

## Exact pinned prior result

The sole mathematical dependency is
`C-UNRESTRICTED-DEGREE14-TERNARY-CONNECTED-SUBCUBIC-SUPPORT-LOWER45 r1`,
used as a result, not an encoding or verification dependency. Its binding is
`acceleration/results/20261003_independent_review/ternary_connected_subcubic_support_lower45_01/claim_binding_schema2.json`,
SHA256 `44cf238643a09335d5af17be9161baf7f18afb4d1b6f60d61c4936cdbd685455`.
The independent report is SHA256
`baa69ead3f4a65902e9ef0d864a151e82017da0707a82337de359cdc7e846789`;
its complete written proof is
`acceleration/audit_20261003_ternary_connected_subcubic_support_lower45_v1.md`,
SHA256 `b51cf3d17586cad49a97ef7c369c4944964e2462c7c60e5ff15f9957b110a065`.
I read the full binding, report and proof. Their precise hypotheses match the
new statement. Only m>=45 (and the available m>=47 nonbipartite corollary) is
reused; the commutator, binary propagation and new cross-block contradiction
are independently rederived here. The prior producer ROOT and verifier
Checkpoint do not verify Checkpoint's new discovery.

## Independent propagation from the complete residual

Let D=A^2+A-12I-2J over the integers. Binary symmetry and degree14 give
D_uu=14-12-2=0. The whole D row sums to196+14-12-198=0.
Exact regularity and symmetry give AJ=JA=14J, so expanding both products
AD=A^3+A^2-12A-2AJ and DA=A^3+A^2-12A-2JA proves AD=DA.
Reduction modulo3 therefore gives AM=MA; it does not require target exactness.

All nonzero M entries are +1 or -1. A support row has sum0 modulo3.
Consequently no support vertex can have degree1. Under the nonisolated
subcubic premise its degree is2 or3. With two nonzero signs a zero sum forces
opposite signs. With three signs the possible integer sums are-3,-1,1,3;
only the two equal-sign configurations reduce to0.

Let S=V(H), |S|=m, and take any z outside S. Its entire M row is0, including
the diagonal. In the (z,v) entry of AM=MA, all terms outside S on the left
also vanish. Thus the binary vector x_u=A_zu, u in S, satisfies

  sum_[u in S] x_u M_uv=0 mod3, for every v in S.

At a support-degree2 column the two opposite coefficients force equality
modulo3 of its two neighbor coordinates; binary0/1 makes that integer equality.
At a degree3 column the equal nonzero coefficients force the three binary
coordinates to sum to0 modulo3. Such a sum is0,1,2 or3, hence it is0 or3;
all three coordinates are equal. It follows that coordinates at the two
ends of every length-two H walk agree, and then every even walk agrees.

For connected bipartite H, vertices in each part are joined by an even path,
so x is separately constant on each part. For connected nonbipartite H,
an odd cycle gives an odd closed walk based at any vertex by going to that
cycle and back. If a connecting path has odd length, prefix that odd closed
walk to make its length even. Hence x is constant on all of S. These are
binary equations, not an automorphism or a claim about uniform internal edges.

## Independent size-versus-degree contradiction

If H is bipartite, call the larger and smaller part sizes p and q. Every
vertex has support degree at least2 and at most3. Counting the same support
edges from the two sides gives

  2p <= |E(H)| <= 3q.

Since m=p+q, this implies2m<=5q. The pinned prior theorem gives m>=45,
so q>=18. Also p>=q>=18. For the particular outside vertex z, its binary
adjacency is constant on each part. Value1 on either part would give z at
least18 neighbors, contradicting its exact degree14. Both values must be0.

If H is nonbipartite, all m coordinates are equal and the prior theorem gives
m>=47 (even m>=45 would suffice). Value1 would give z at least47 neighbors,
again contradicting degree14. The common value is0.

The reasoning applies to every outside z, so A has an entirely zero block
between S and its complement. This conclusion does not merely exclude a
common outside neighborhood; it forbids each possible cross adjacency.

If the complement is nonempty, choose u in S and z outside S. Their adjacency
is0. Any common neighbor w in S would require a forbidden z--w cross edge;
any common neighbor w outside S would require a forbidden u--w cross edge.
The two possibilities exhaust all99 vertices, and zero diagonal prevents
an endpoint contribution. Therefore (A^2)_uz=0 and

  D_uz=0+0-2=-2=1 mod3.

It is a nonzero residual entry incident with z, contradicting z outside the
whole support S. The complement must be empty, proving m=99.

## Written falsification checks

1. The diagonal is exactly0 for D, so an outside vertex has no hidden residual
   diagonal that could invalidate the zero-row commutator inference.
2. Complete integer rows, including the diagonal before cancellation, sum0;
   the support is not defined from sampled residuals.
3. Both commutator products use AJ=JA=14J. Directed or irregular inputs lack
   this stated justification.
4. For outside z, the right commutator row is exactly0 and all left summands
   outside S vanish; no unproved internal spectral assertion is used.
5. Opposite degree2 signs and binary coordinates force integer equality.
6. Equal degree3 signs and a three-term binary sum force all0 or all1;
   degree4 cannot use this inference (binary sum3 can mix0 and1).
7. Even-walk propagation is shown in both connected cases, including how an
   odd closed walk reverses path parity. Disconnected components are not merged.
8. In an uneven bipartition, use degree>=2 on the larger side and degree<=3
   on the smaller side; the two incidences count the same support edges.
9. q>=2m/5>=18 and p>=q both exceed14. Merely having m>=45 is insufficient
   without the part-size bound in the bipartite case.
10. Binary constancy alone does not imply zero; the exact degree14 budget rules
    out value1 on either part, separately for every outside vertex.
11. The zero block is symmetric and covers every outside vertex. Both locations
    of a possible common neighbor are forbidden, establishing CN(u,z)=0.
12. The cross residual is-2=1 modulo3, a literal nonzero, not a floating score.
13. The proof permits m=99 and the empty support is outside its nonempty premise.
    It asserts no realization or impossibility for that boundary.
14. Support degree4+, disconnected support, target existence and new engine
    acceptance thresholds are not conclusions of this theorem.

## Verdict and limits

VERIFIED for the exact conditional spanning theorem by this independent
written derivation and its fourteen explicit falsification boundaries. Zero
mathematical computation commands, adjacency fixtures or exhaustive runs were
executed. Definitions, elementary exact arithmetic and the pinned prior size
result are shared; no producer code or agent agreement is proof.

The connected/nonempty/subcubic premise is explicit. This theorem does not
exclude a spanning connected support, classify its realizability, assert target
nonexistence, prove novelty, claim external review or approve any search engine.
It is outside the protected358-claim publication cutoff. Overall search coverage:
UNKNOWN; no validated denominator.
