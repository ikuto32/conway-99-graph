# Every-root positive scaffold normalization

Status: **CANDIDATE derivation pending independent review**. Proposed claim
`C-ROOT-SCAFFOLD-NORMALIZATION`, revision 1. This is a fresh audit-ready statement
of a standard labeling argument already used in historical research, not a
novelty claim. Inspection of the current twelve-record root claim ledger found
the conditional positive-cut claim but no independently recorded standalone
normalization claim. Historical labels are not treated as fresh verification.

## Exact statement

Let `A` be any 99 by 99 symmetric binary integer matrix with zero diagonal and

```text
A² = 12I - A + 2J.
```

For **every** root vertex `r`, and for **every** ordering and orientation of the
seven matching edges in its neighborhood, there is a unique labeling of the
remaining vertices by the 84 unordered pairs of nonmatched root-neighbor
symbols. The resulting full-99 labeling sends `r` to 0, its ordered/oriented
matching pairs to `(1,2),(3,4),...,(13,14)`, and the remaining vertices to
15 through 98 in the repository's root-label order. Its adjacency contains
exactly the following prescribed 189 **positive scaffold edges**:

- Fourteen edges from vertex 0 to vertices 1 through 14.
- Seven matching edges `(1,2),(3,4),...,(13,14)`.
- For each of the 84 outer vertices, two edges to its distinct nonmatched
  root-neighbor labels, hence 168 incidence edges.

"Exactly" here counts the prescribed scaffold edge set, not all edges of the
target graph. Root and root-neighbor degrees are already saturated by this
scaffold. The normalization fixes **no edge or nonedge between two outer
vertices**. Those adjacencies must still satisfy the full target equation;
they are not assumed free of its consequences. No complete overlap assignment,
E0=0 restriction, automorphism, or symmetry of the hypothetical graph is assumed.

## Derivation from the matrix equation

1. Since `A` is symmetric and binary, `(A²)_vv` equals the degree of `v`.
   The diagonal of the displayed equation is 14, so every degree is fourteen.
   For distinct `u,v`, the entry `(A²)_uv` counts their common neighbors and
   equals `2-A_uv`. Adjacent vertices therefore have exactly one common
   neighbor; nonadjacent vertices have exactly two.

2. Fix an arbitrary root `r`. It has fourteen neighbors. If `u` is one of
   them, the neighbors of `u` lying in `N(r)` are precisely the common
   neighbors of `u` and `r`, so there is exactly one. Thus the subgraph
   induced on `N(r)` is a simple 1-regular graph: seven disjoint matching
   edges. Order these edges arbitrarily and orient each arbitrarily.

3. There are `99-1-14=84` vertices outside the closed neighborhood of `r`.
   Each such vertex `x` is nonadjacent to `r`, and so has exactly two
   neighbors in `N(r)`. Write this unordered pair as `p(x)`.
   Its two endpoints cannot be matched to one another: if they were adjacent,
   both `r` and `x` would be common neighbors of that adjacent pair, contrary
   to the required common-neighbor count one.

4. Conversely, let `a,b` be any two nonmatched vertices of `N(r)`. They are
   nonadjacent and have exactly two common neighbors. One is `r`.
   None lies in `N(r)`, because every vertex of its induced matching has
   only one neighbor there and therefore cannot be adjacent to both `a,b`.
   The second common neighbor is consequently one unique outside vertex `x`.
   Since `x` has exactly two neighbors in `N(r)`, its pair is precisely
   `p(x)={a,b}`.

5. The map `x -> p(x)` is therefore a bijection from the outside vertices
   to the unordered nonmatched pairs in `N(r)`. Their number is
   `binom(14,2)-7 = 84`. Label each outside vertex by its unique pair.
   Each root-neighbor symbol appears in twelve such pairs: all other
   root-neighbor symbols except itself and its mate. It therefore already
   has one edge to `r`, one edge to its mate, and twelve incidence edges,
   totaling fourteen. This also proves the stated degree saturation.

These steps apply to every root and every chosen ordering/orientation. Once
those choices are fixed, uniqueness of the outside common neighbor fixes the
outer labeling uniquely. They do not rely on the existence of an automorphism
carrying one root or one labeling to another.

## Exact repository labeling and use of conditional cuts

Write root symbols as `(g,b)` with `g=0,...,6` and `b=0,1`; symbol `(g,b)`
corresponds to full-99 vertex `1+2g+b`. Outer labels are enumerated in the
following nested-loop order, assigning consecutive vertices 15 through 98:

```text
for 0 <= g < h < 7:
    for b in (0,1):
        for c in (0,1):
            label = { (g,b), (h,c) }
```

If the lemma is independently approved, any hypothetical target graph can
therefore be represented in the positive-scaffold coordinates used by the
already checked positive-adjacency clauses. Each such normalized target must
satisfy those clauses. This connects the scope of their conditional statement
to every hypothetical target graph; it does **not** assert that the clauses
exclude every normalized graph, every root, or every possible outer adjacency.
No unrestricted nonexistence conclusion follows.

## Runtime calibration, separate from proof

`acceleration/theory_20260917_root_scaffold.py` uses only the Python standard
library. It constructs the nine-vertex 3 by 3 rook graph and checks, over
integers, its own equation

```text
B² = 2I - B + 2J,
```

corresponding to `srg(9,4,1,2)`. It then checks every root and every ordering/
orientation of its two neighborhood matching edges: nine roots and eight
labelings per root, 72 explicit full-nine bijections. The analogous scaffold
has 14 positive edges. It tests the unique outside-pair labeling, root-inner
degree saturation, and the exact scaffold edge set in each labeled graph.

Deliberately corrupted controls remove each original edge, add each original
nonedge, alter symmetry, introduce a diagonal loop, introduce a nonbinary
entry, and make a degree-preserving two-edge switch that fails the exact
common-neighbor equation. Corrupt label maps also fail independent map/scaffold
checks. These finite controls calibrate executable bookkeeping; they do not
prove the 99-vertex lemma and are not a target witness.

All statements and computed observations remain CANDIDATE until independent
derivation/artifact review. The script does not import a historical scaffold
builder or approve its own output. Its output records the exact command,
source commit, hashes, matrix fixture, label maps, and rejected controls.

```powershell
$env:UV_PROJECT_ENVIRONMENT = 'build/research-venv'
uv run --locked --cache-dir .uv-cache-20260917 python -B acceleration/theory_20260917_root_scaffold.py --out build/root-scaffold-new
```

Use a fresh output directory. No target graph, general nonexistence proof,
literature novelty, or target-wide search coverage is claimed.
