# Exact C2 SAT experiment

Status: **UNKNOWN**.  No SAT witness and no UNSAT proof was obtained.  This
experiment does not justify either a Conway 99-graph submission or elimination
of the C2 branch.

## Model

- Source: `scratch_c2_exact_sat.py`
- DIMACS: `scratch_c2_exact.cnf`
- Build metadata: `scratch_c2_exact_build.json`
- Solver record: `scratch_c2_exact_portfolio.json`
- Solver: CaDiCaL 1.9.5 through PySAT
- Edge variables: 1,722 C2 orbits of outer edges
- Forced nonedges: the 42 pairs `u--tau(u)`
- Rooted `BP=P*A0` equalities: 1,176
- Outer-pair orbits constrained: 1,764 (42 fixed and 1,722 of size 2)
- Product variables: 141,204
- Total variables: 422,646
- Total clauses: 840,798

For each representative outer pair `(u,v)`, the CNF imposes

```
common_outer(u,v) + edge(u,v)
    <= 2 - |label(u) intersect label(v)|.
```

The product indicators use only the lower implication from the conjunction.
This is equisatisfiable because they occur positively only in at-most
constraints.  The inequalities are collectively exact: `BP=P*A0` fixes all
84 outer degrees at 12 and hence 504 outer edges, so their physical left-side
sum is

```
84*C(12,2) + 504 = 6048.
```

The physical right-side sum is

```
2*C(84,2) - 14*C(12,2) = 6048.
```

## Exhaustive symmetry split

For one outer vertex, let `a,s,d` count neighbours with the same two-coordinate
support, exactly one shared support coordinate, and disjoint support.  The four
on-support rooted equations and degree 12 give

```
2*a + s = 4,
a + s + d = 12,
d = 8 + a >= 8.
```

Thus a disjoint-support edge always exists.  The rooted coordinate group
`C2 wr S7` centralizes `tau` and is transitive on ordered disjoint-support
edges, so the model safely fixes `{0,2}--{4,6}` (edge-orbit variable 43).
The stabilizer swaps the two same-support alternatives of `{0,2}` (variables
1 and 12).  The exhaustive normalized assumptions are:

- `a0`: `43, -1, -12`
- `a1`: `43, 1, -12`
- `a2`: `43, 1, 12`

This argument was also checked independently by the separate C2 theory audit.

## Run

All three branches ran concurrently with an external wall limit of 600 seconds
per branch.  Each was still solving at the deadline and was terminated, so all
three records are `UNKNOWN`.  This represents roughly 1,800 single-core
solver-seconds, not an exhaustive search.

The restored generator reproduced the exact DIMACS after the run: its SHA-256
remained

```
52D0F6954E408D0A1E88B44F8E27FF8293BB3540932CAE60D0B6D528CF2548E6
```

Other SHA-256 values at handoff:

```
scratch_c2_exact_sat.py
50AF20D756D39231FD04972651E7E27A17149CD5F63A1D4DF53105B0CBC4A90D

scratch_c2_exact_build.json
AA1544F3F05AE68E3861BC9C5F3AAA108A16B8D533610F15731A37309308F35D

scratch_c2_exact_portfolio.json
6BAE612C49915EDAF6BB23A7D5E4456F4C279032ADA7CD02E2EBBA3E35566988
```

If a future run returns SAT, the source expands its 1,722 edge-orbit literals
to the full 99-vertex graph and invokes `scratch_bp_seed.expand_and_check` over
all 4,851 unordered vertex pairs before saving a solution artifact.  It never
writes `submission.txt` itself.
