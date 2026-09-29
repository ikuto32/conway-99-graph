# Independent fixed Wave154 row29 obstruction

This is a direct finite row obstruction for one labelled partial graph. The
only prior mathematical dependency is the independently checked propagation
of the frozen Wave154/Q1 partial graph. The complete SAT proof and its
extracted clause core are not premises. No nontrivial target automorphism
or universal containment of this fixed configuration is assumed.

## Necessary constraints reconstructed from the raw graph

Write u=29 and let x_b be the unknown adjacency of u to b. The propagated
row has four fixed neighbors and38 unknown entries, all in the outside
60-vertex cell. Since a target row has degree14, the unknown entries sum
to10. Every other entry of this row is already fixed.

For each v=3,...,26, its entire adjacency row is fixed. The target identity
requires |N(u) intersection N(v)|=2-A[u,v]. Split this sum into its known
terms and the unknown row29 entries whose endpoints are known neighbors of
v. This gives exactly the24 saved linear equations, including equations
with empty supports. No unknown product is assigned or dropped.

For two unknown endpoints b,c, let t be the number of already known common
neighbors other than u. If their mutual edge is fixed1, the target cap is1;
otherwise the safe cap is2, including when that edge remains unknown. In
the53 saved pairs, t already equals this cap. Thus x_b and x_c cannot both
be1, since that would add u as one more common neighbor. The checker
reconstructs the literal known-neighbor witness and edge state of every
pair, and every variable/equation from the raw99 partial matrix. Treating
an unknown b--c adjacency with cap2 is a safe relaxation, not an assertion
that the target edge is absent.

## Complete proof-tree checking

Every input constraint is an integer interval L <= sum(x_i) <= U. At a
tree node, let o be the already assigned ones in that constraint and f the
unassigned variables. Its possible sum lies between o and o+|f|.

For each reported forced bit, the independent checker gives that bit its
opposite value while leaving all other bits free. The resulting interval
must be disjoint from [L,U]. This establishes each individual implication
without relying on the producer's propagation implementation or search
order. The recorded before-state must also match exactly.

Every split must choose an unassigned bit and contain exactly the children
0 and1. All child references must be valid; every non-root node has exactly
one parent, all nodes are reachable, and cycles and unused nodes are rejected.
Every leaf must cite a constraint for which o>U or o+|f|<L, with exact
recorded counters. Induction from these impossible leaves through exhaustive
binary splits and entailed forces proves that no assignment exists.

The entire finite certificate is checked:139 nodes,69 splits and70 conflict
leaves. No sampling or search timeout is used as evidence. The certificate
proves infeasibility of necessary row conditions, hence excludes a target
row under this exact fixed configuration. It does not classify any other
triangle factor or establish unrestricted nonexistence.

## Controls and replay

Controls include a three-bit inconsistent system checked against all eight
assignments, a satisfiable system with directly validated complete leaves,
and a partially masked row of the known SRG(9,4,1,2) rook graph. Its actual
row must satisfy all reconstructed necessary constraints. Deliberately
corrupted real tree branches, force values, counters, leaf witnesses,
constraint bounds, variable endpoints and known-common witnesses are rejected.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_triangle_row29_obstruction.py --out acceleration/results/20260930_independent_review/triangle_wave154_row29_obstruction
```

The output directory must be new. The report binds source, raw matrix,
propagation gate, producer artifacts, controls, reconstructed constraints,
and every checked node's inherited and propagated assignments. Only Python
standard-library exact integers and collections are used; no producer code
is imported.
