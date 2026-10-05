# Independent eight-coordinate matching-filter argument

This written checking argument accompanies the independent checker; it is
not a completion receipt. The final `summary.json` is required to establish
which raw artifact records actually passed. No raw producer multiplicities
are certified by this argument.

Assume a target extends the frozen eight-coordinate family and contains
one of the independently complete center stars. The center has fourteen
neighbors. For each neighbor x, the pair (center,x) has exactly one common
neighbor, so x has exactly one neighbor inside the center's neighborhood.
Thus that induced neighborhood is seven disjoint edges.

All already present neighborhood edges are forced and must have disjoint
endpoints. The remaining free neighborhood vertices must be matched to
one another by edges in the declared family-unknown edge set. Any such
edge must, when inserted separately, preserve every common-neighbor
upper bound in the full known 99-vertex partial graph. If an existing
edge already has two common neighbors, or a nonedge already has three,
adding still more edges cannot repair that violation. Inserting a new
edge also changes its own upper bound from two to one; that pair is
explicitly tested.

The checker reconstructs the full known graph separately for every center
star. It inserts each prospective free edge into both symmetric rows,
checks all pairs incident to either changed row, and restores the rows.
Only common-neighbor products involving at least one changed row can
change, so these checks cover every affected pair. The original star's
other upper bounds and root quotas rely on the separately pinned complete
domain audit. This inserts no assumption about graph automorphisms.

Consequently, any target completion induces a perfect matching in the
graph of individually permitted free edges. Nonexistence of such a
matching is a sound rejection of that local star. A positive matching
witness is necessary evidence only: its edges might violate a cap when
inserted together, and the rest of the target may still be impossible.

For a producer rejection, the independent checker processes the allowed
edges one at a time, retaining the set of vertex subsets covered by
disjoint already processed edges. The initial reachable set is `{0}`.
For an edge mask E, adding `S union E` is allowed exactly when `S and E`
is empty. Induction on processed edges shows the reachable masks are
exactly all endpoints of matchings in that prefix. Therefore the full
vertex mask is reachable exactly when there is a perfect matching. This
is distinct from the producer's first-unmatched-vertex recurrence.

For positive producer records, each listed witness edge is checked to be
allowed and the flattened endpoints must be exactly the free vertices,
each once. The exact positive matching count is not recounted or claimed.
Negative and positive checks together establish the rejected/surviving
ID partition after every raw record and all 84 centers pass.

The frozen scope retains 120 K edges, the root scaffold and all recorded
absences. Exactly 2,160 pairs may vary: 480 freed same-sign pairs at root
groups 0–3 and 1,680 disjoint-support pairs. The complete input population
has 2,290,122 center-star choices, not that many distinct full graphs.
No target-wide coverage denominator, construction, general nonexistence
proof, or independently checked positive multiplicity is established.
