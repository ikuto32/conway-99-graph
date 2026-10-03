# Exact pair-cap permutation domains for normalized triangle cores

Preregistered discovery experiment. Inputs are the independently checked
3,580 ordered matching-pair representatives. Classify neither P-orbits nor
outside incidence factors: count every labelled permutation P that gives a
39-vertex core satisfying all principal pair common-neighbour caps.

## Exact derivation to be independently reviewed

Coordinates: a triangle t0,t1,t2 and fibres A0,A1,A2 of size12; each ti joins
its fibre, internal matchings are M0,M1,M2, the 01 and02 cross matchings are
identities, and A1(b) joins A2(P(b)). P is arbitrary. Named fibres are never
permuted, and no target automorphism is assumed.

For a pair of distinct vertices, the necessary cap is
`known_common_neighbours + adjacency <= 2`. Within fibres and for pairs
involving T this is automatic. The cross-fibre conditions are exactly

```
delta(a,b) + M0[a,b] + M1[a,b] + P[b,a] <= 2,
delta(a,c) + M0[a,c] + M2[a,c] + P[a,c] <= 2,
P[b,c] + delta(b,c) + P[M1(b),c] + P[b,M2(c)] <= 2.
```

The first two inequalities only prohibit `P(i)=M0(i)` when either
`M1(i)=M0(i)` or `M2(i)=M0(i)`. In the last inequality P[b,c] is mutually
exclusive with each of the other two P-entries. For b!=c the inequality is
therefore automatic. For b=c, its only forbidden case is
`P(M1(b))=b` together with `P(b)=M2(b)`.

These last constraints couple only two rows within one M1 matching pair.
Process the six M1 pairs in a fixed order. For a pair(r,s), and two distinct
columns(x,y), an orientation is allowed precisely when neither unary
prohibition holds and neither `(x=s and y=M2(s))` nor
`(y=r and x=M2(r))` holds. Give each unordered column pair weight0,1,or2,
the number of allowed orientations. The exact subset recurrence is

`D[k+1,S union {x,y}] += D[k,S] * weight[k,{x,y}]`,

starting at D[0,empty]=1 and using disjoint columns. It counts every
permutation exactly once. All operations are integers. This is a complete
labelled P-domain count per selected matching-pair representative if all
stages finish, not a canonical P-orbit census or graph-extension count.

## Frozen population, controls, limits

Population: all3,580 records bound by the matching-pair census independent
gate085748fd2ebb03bdb7ea6048d782be0c17ce8cadef4ea32028cb58ca6b0efb79.
For each completed case retain the input representatives, exact count, a
positive P witness when available, and its literal raw-core pair-cap check.
If the count is zero, retain every DP layer as an exhaustive certificate.
Sum only using the exact pair-orbit weight46080/joint_stabilizer_order;
this counts labelled (M1,M2,P), not target graphs or canonical core classes.

Before the research census, compare all3^2*4!=216 small n=4 cases against
literal induced15-vertex pair intersections, and nine deterministic n=6
matching pairs times720 permutations. Compare DP counts too. A repeated
permutation image and an extra cross-edge in an otherwise legal core must
be rejected. These are producer controls, not independent verification.

Limits:120 seconds total,8 GiB working set, no SAT, no floating arithmetic,
no random seed. Save one JSONL record per completed case and a checkpoint
every100 cases. A stopped prefix does not certify the unprocessed cases.
Progress uses pinned tqdm. After completion, independent raw-scope,
recurrence and full-count audit is required before promotion.

Command: `uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/theory_20260930_triangle_core_permutation.py --out acceleration/results/20260930_triangle_core_permutation`, with `UV_PROJECT_ENVIRONMENT=build/research-venv`.
