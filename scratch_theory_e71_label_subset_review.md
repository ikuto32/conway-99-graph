# Independent review of exact-label neighbour-subset restrictions

The proposed restriction is a sound necessary condition. For a fixed
vertex `x` in source fibre `S`, a different target fibre `F`, and a chosen
subset `T` of its four vertices, expose the root, its fourteen neighbours,
all four vertices of `S`, all four of `F`, and exactly the adjacency row
`x--F=T`. Both internal fibre graphs and all root-label incidences are fixed.
This has 23 vertices and only 16 choices for the single selected row.

All other `S\{x}--F` edges remain unknown. Count common neighbours using
only exposed present edges. That count is a lower bound in every completion.
A known edge has cap1; a known nonedge has cap2. An unknown pair can safely
use cap2, because its eventual cap is either1 or2. Thus rejecting a row
that already exceeds one of these caps cannot discard a valid completion.
Accepting a row does not assert that its unknown edges can be completed.

## Which additional conditions the 23-vertex check captures

For a root-neighbour label `a`, the total number of second-layer neighbours
of `x` carrying `a` must be

```text
q_x(a)=1 if a or its matching partner a^1 belongs to label(x),
q_x(a)=2 otherwise.
```

If `a` is in the label of `x`, this is the adjacent-pair lambda count.
If `a^1` is in that label, the nonedge `a,x` already has common neighbour
`a^1`, leaving one additional neighbour. Otherwise it has no common
neighbour among the first-layer matching and needs two.

Known own-fibre neighbours consume this quota. The partial graph checks
the residual capacity at `x`, and also the corresponding residual capacity
at each target vertex `y`: a selected edge `xy` contributes to the
root-neighbour/target pair `(a,y)` whenever `a` is in `label(x)`. This
symmetric target restriction is missing if one checks only source quotas.

The target-pair condition has the explicit form

```text
|label(y) intersect label(z)|
 + |N_F(y) intersect N_F(z)| + [y,z both in T]
 <= 1 if yz is an internal edge, and <=2 otherwise.
```

For `(x,y)` it also checks the fixed root-label contribution plus
`|T intersect N_F(y)|`. Including the complete source fibre automatically
checks all additional common-neighbour lower bounds supplied by its known
edges. No unassigned cross edge is silently treated as a forced nonedge.

The positionwise moment relaxation is therefore sound: the actual degree
row at each of the 84 exact-label positions must have, for each target,
a degree realized by at least one admissible target subset. Taking those
conditions independently only weakens simultaneous completion requirements.

## Ordinary target fibres are already handled by the raw row space

A four-edge triangle-free internal graph on four vertices is a C4. Its
four corner labels force the unique side-square: either other C4 leaves
a nonedge sharing a root label and having two internal common neighbours,
which would exceed mu2.

In the side-square every pair is already saturated. A side edge has its
unique common root neighbour; an opposite nonedge has two internal common
neighbours. An outside vertex therefore has at most one neighbour in an
ordinary fibre. The raw row-space model already fixes that degree exactly:
the ordinary column of K4 is zero, so

```text
d_x,F = C[S,F]/4 = 1 for disjoint supports, 0 for overlapping supports.
```

For a disjoint support all four singleton choices pass the 23-vertex local
test; for overlapping supports the empty choice passes. The source's known
neighbours use only its own root support and hence cannot consume a target
label when the supports are disjoint. Remaining target/source pair caps
have at most the one newly exposed common neighbour. Thus ordinary targets
do not further prune raw degree rows. A small direct check over all 64
source internal graphs retained 19 locally admissible states and confirmed
all304 disjoint-singleton and76 overlapping-empty cases. This is a sanity
check of the preceding argument, not a local completion census.

## Optional stronger single-row condition

Individual target-subset tests do not impose the fourteen root-label quotas
simultaneously. This can be strengthened within one row, without enumerating
overlap matchings: select an admissible subset at each exceptional target
and require the summed label incidences to equal the residual quotas after
the known own-fibre neighbours are removed.

The raw degree row already fixes total incidence in each of the seven root
pairs:2 in the source's two groups,4 in the other five. It therefore suffices
to track the first label of each pair. Before subtracting known neighbours,
there are at most `2^2*3^5=972` bounded states. Ordinary singleton targets
have all four independent label choices, so they contribute only independent
per-group intervals at the end. Only exceptional targets need explicit
single-row state updates.

This last dynamic program is a proposed strengthening, not an implemented
or certified exclusion in this review. The current 23-vertex conditions
and their degree-moment certificates must be audited separately.
