# Cycle and class-capacity projections: exact positive controls

All five saved overlap assignments pass the inexpensive tests below,
although stronger already checked inequalities exclude every one of them.
This records a limitation of these cycle/group capacity projections, not
a new exclusion. The whole calculation uses integer arithmetic and took
less than one second; no CP, LP, dual, or graph search was run.

Let K be a **complete** E0=0 overlap assignment. Every unlisted overlap
edge and every same-fiber edge is absent. Write X for unknown edges
between disjoint supports. Every vertex has K-degree 4 and X-degree 8.
For a root group g, let V_g be its 24 outer vertices. K[V_g] is a
2-factor. Its two exact root labels force the label-bit sequence around
each cycle to have period four, so each cycle length is a multiple of 4.

First remove every disjoint edge whose addition alone violates a partial
common-neighbor cap. Each removed edge has an explicit violating-pair
witness. The original K has 1,167 remaining possible edges (513 removed),
and alternatives r0,r1,r2,r3 have 1,116, 1,182, 1,219, and 1,125.

## Exact flow/Hall condition

For different root groups g,h, form the bipartite projection between
`V_g \ V_h` and `V_h \ V_g`, retaining the individually admissible edges.
The required degree of u on the left is

```text
d_h(u) = 4 - |K(u) intersect V_h|.
```

The analogous right degree is d_g(v). A completion must give an integral
bipartite flow realizing all these degrees. For every subset A of the
left side it consequently must satisfy the capacitated Hall inequality

```text
sum_(u in A) d_h(u)
  <= sum_(v on right) min(d_g(v), number of allowed edges from A to v).
```

This includes A equal to any union of g-star cycles after removing
vertices whose supports contain h. It also implies every two-sided
cycle-subset cut. Exact root-label classes give a stronger parallel
family with 10 vertices per side and quotas
`2 - |K(u) intersect label_class|`. Whole group-star and exact-label-star
projections use left degree 8 and the corresponding right label/group
quotas over vertices outside the root group.

For each input, 21 group-pair, 84 exact-label-pair, seven whole-group-star,
and fourteen whole-label-star projections pass: **126 integral flows**.
All 630 flow edge sets are saved. The separate auditor checks their
degrees and edge permissions without importing the max-flow algorithm.
The 798 explicitly tested cycle-union Hall inequalities also pass.

## Sum of pair caps over a cycle union

For a union T of cycles in K[V_g], put

```text
t_v = |K(v) intersect T|,
y_v = number of X edges from v to T,       v outside V_g,
c_v = min(4-|K(v) intersect V_g|, allowed neighbors of v in T),
R(T) = sum_(u<v in T) [2-|label(u) intersect label(v)|
                       -K_uv-|K(u) intersect K(v)|].
```

Summing the linear pair caps over all unordered pairs in T gives the
uniform necessary inequality

```text
sum_v t_v y_v <= R(T),     sum_v y_v=8|T|,     0<=y_v<=c_v.
```

There are no unknown edges inside T because every vertex of T contains
group g. Each unknown edge u-v with u in T occurs in exactly t_v of the
summed linear terms. Thus the displayed coefficient is exact. Dropping
all unknown-times-unknown terms only relaxes the necessary bounds.

The minimum possible left side under the displayed box and total-demand
constraints is obtained by filling capacities in increasing order of
t_v (values 0 through 4). If there is insufficient capacity, or this
minimum exceeds R(T), T is a certified obstruction. Here **all 133 tested
nonempty cycle unions pass**. This minimum ignores row-by-row incidence,
so passing it is only a necessary-condition control.

| Input | Integral flow witnesses | Cycle-union Hall checks | Weighted cycle-union checks |
|---|---:|---:|---:|
| original | 126 | 174 | 29 |
| r0 | 126 | 186 | 31 |
| r1 | 126 | 126 | 21 |
| r2 | 126 | 78 | 13 |
| r3 | 126 | 234 | 39 |

The separate projection flows can disagree on their shared edge variables.
They do not satisfy all positive-cap pair constraints simultaneously.
Their success therefore does not conflict with the previously checked
global capacity contradictions for these five fixed assignments.

Reproduction:

```text
& 'C:/Users/ikuto/.local/bin/python3.12.exe' -B scratch_follow_cycle_capacity.py
& 'C:/Users/ikuto/.local/bin/python3.12.exe' -B scratch_follow_cycle_capacity_audit.py
```

The independent audit returns
`INDEPENDENT_CYCLE_CAPACITY_CONTROLS_AUDIT_PASS`. No uniform positive E0
bound, new forbidden configuration, graph, or submission is claimed.
