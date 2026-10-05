# Independent written audit: the separate one-d3 R226/maxd3 b7 exclusion

Completed verification: 2026-10-04T22:45:34.5783846Z.
Producer /root/structural; verifier /root/native_driver;
method independent_derivation; computational executor null.

Paper docs/CANDIDATE_20261004_TARGET_ROOK_COUNT226_MAXD3_SINGLE_D3_NO_SEVEN_D2_V1.md
SHA256 8f4327d1cc0f1c122e361743fdfa17d3bc7764536d871d2e683bf52e11518c96.
Raw acceleration/results/20261004_target_rook_count226_maxd3_single_d3_no_seven_d2_candidate01.json
SHA256 05e12eaacdb9b83bb57c80a853ec088db7c95561805be954e7ef7ccd9b7431be.
Exact ID C-UNRESTRICTED-TARGET-ROOK-COUNT226-MAXD3-SINGLE-D3-NO-SEVEN-D2-BOUNDARY r1.

The new implication survives whole-source independent derivation and
attempted falsification. It receives its own written PASS; the predecessor
profile's approval is not transferred to this new claim. Only b7 under
the literal one-d3/R226/maxd3 hypotheses is excluded. R226 and the whole
one-d3 lane remain unexcluded by this statement.

## Literal statement and sole inherited result

For every complete finite simple SRG(99,14,1,2), let R count actual induced
rook-nine vertex sets once and put d_T=6-r_T for each actual triangle T.
Suppose R=226, every d_T belongs to {0,1,2,3}, and exactly one actual
triangle has deficiency three. The number b of actual deficiency-two
triangles is not seven.

Exactly one logical dependency is used, revision one, relation uses_result:
C-UNRESTRICTED-TARGET-ROOK-COUNT226-MAXD3-SINGLE-D3-SEVEN-D2-PROFILE.
Its exact theorem assumes the same complete target, actual subset count,
R226/maxd3/one-d3 hypotheses and the additional b7 contradiction supposition.
Its original paper/raw nulls and historical bytes remain unchanged.

The genuine independent report is
acceleration/results/20261004_independent_review/target_rook_count226_single_d3_seven_d2_profile_native01/summary.json,
SHA256 e5890cba825228a77e240312810b9d16fa4e2bf4852a557d29c076db6b0bc940.
Its canonical binding in the same directory has SHA256
bca709b2cb4e82c6920a2bf8f1a887fc0a1bbebb1dcd74daba79d093b0d36184.
Its authentic independent verification time is 2026-10-04T22:37:53.9644142Z.
The separate Root receipt is
acceleration/results/20261004_target_rook_count226_single_d3_seven_d2_profile_root_written_acceptance01.json,
SHA256 d205853c605fb6c55fbbc190de729bfd36fba4875eadd04d7d2c9f8790c3bbb3,
dated 2026-10-04T22:45:08.5654333+00:00. These times are inherited premise
history, not the present implication's verification time.

Root discovered the whole two-root fan injection. Structural produced and
challenged the frozen implication. Native independently verifies the
partner types, all point labels, the prohibition on cross-root reuse and
the exact population contradiction below. No independent-discovery or
archive-novelty claim is asserted; agreement is not the verification basis.

## New independent derivation

Assume b=7 for contradiction. Let T be the sole d3 triangle. Applying the
exact profile gives its bad point p, two attached d2 triangles A and B,
and selected support S of all d1 triangles together with T. Write

    A={p,x1,x2}, B={p,y1,y2}.

The four outer labels are distinct and outside S. Therefore none lies in
any d1 triangle or in T. Exactly five other d2 triangles are available.
Both optional 42/43-edge profiles are included; no information about their
extra internal edge is needed for the new implication.

For completeness, the local degree interpretation needed here follows
directly from the target, not an extra logical dependency. The fourteen
neighbors of a point are paired by their unique edge completions, so
exactly seven actual triangles pass through it. Two actual triangles in
a containing rook meet as a row and column. Their common point and four
outer points determine the remaining four by mu=2 on cross nonadjacent
pairs. Hence at most one actual induced rook contains that pair. Each
rook containing A supplies exactly one different covered partner at every
point of A. Among the six other incident triangles, the complement graph
of covered pairs thus has degree 6-r_A=d_A=2. The graph is simple and
symmetric. A zero-deficiency node has degree zero and cannot provide a
defect edge to A.

At x1, A therefore has two distinct uncovered partners. Neither is a d0
triangle. No d1 or d3 triangle occurs there, by x1 outside S and the sole
d3=T. B cannot occur there: A and B already meet at p, and sharing another
point would give an edge two triangle completions. Neither partner is A
itself, since there is no loop. Thus both partners are among exactly the
five unattached d2 triangles. The same argument holds at x2,y1,y2.
Four actual points each require two distinct partners, for eight partner
incidences.

Every unattached triangle U can serve at most one of these points.
Meeting x1 and x2 would intersect A twice; meeting y1 and y2 would intersect
B twice. Meeting x_i and y_j gives the three distinct intersections
p,x_i,y_j among A,B,U. Those points form a triangle: p-x_i lies in A,
p-y_j in B and x_i-y_j in U. The edge p-x_i then has both A's other outer
point and y_j as common neighbors. They are different because the four
outer labels are distinct. This contradicts lambda=1. This direct
actual-label proof does not identify F adjacency with actual intersection.
Even if U also contained p, it would already violate linearity with A;
there is no label collapse that evades the contradiction.

The two partners at each point are different by local graph simplicity,
and no partner can be used at two different points by the preceding target
geometry. All eight incidences therefore require eight distinct unattached
d2 roots. Only five exist. The contradiction 8<=5 rejects b7 and discharges
only that added supposition, establishing the precise new theorem.

## Written proof-check record: 15 checks, zero executions

1. Whole new paper/raw exact ID, revision, statement and literal hypotheses.
2. Exactly one ordered uses_result r1 dependency.
3. Genuine profile report/binding scope matches the b7 supposition.
4. Profile evidence gives the bad p and exactly two attached A/B roots.
5. Its four actual outer labels are distinct and outside all selected roots.
6. Exactly b-2=5 unattached d2 roots remain.
7. Target seven-root local graph has the stated covered-pair meaning.
8. Conditional intersecting-pair rook uniqueness prevents duplicate covered partners.
9. Every outer A/B node has exact local degree two.
10. Simple symmetric degree zero excludes all d0 partners.
11. Outside S excludes every d1/T partner and linearity excludes the other attachment.
12. Each point requires two distinct among the same five unattached roots.
13. Same-attachment outer reuse violates linearity.
14. Cross-attachment outer reuse gives two actual common neighbors to an edge.
15. Eight distinct required roots contradict five, excluding exactly b7.

## Written falsification/boundary record: 10 challenges

1. Without all four points outside S, d1 partners could occur and the d2 count fails.
2. A mere outside-point-to-unattached-pair injection would be weaker and is not used alone.
3. Covered actual intersections do not replace a required uncovered degree-two partner.
4. d0 partners are rejected by symmetry, not simply omitted from a population count.
5. A and B's shared point p is distinct from every outer point.
6. Repeated external U across A and B is tested using actual edges, not an abstract F cycle.
7. Multiple partner incidences at a single point cannot use the same simple node twice.
8. Both H0/H1 predecessor options are included; no induced-support assumption is added.
9. The profile's original null fields remain null and its own approval does not approve this implication.
10. No whole one-d3 lane, maxd3 inference, R226 or target exclusion is claimed.

There are 25 written checks, zero computational/formal/external checks and
zero solver calls. Nine selected documentary files are authenticated;
existing immutable reports carry their histories without a transitive
proof-map replay. No mathematical program/import, enumeration, worker,
ledger parse/write, protected/Git/index or publication mutation occurred.
Root-reported live467 is context only. Producer nulls and original dates
remain; new Root acceptance and registration are separate later actions.
