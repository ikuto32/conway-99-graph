# Six triangle-rooted flags are universally constant

For every `srg(n,k,1,2)` and every ordered triangle, each of the rooted
six-vertex flags

```text
24699, 24939, 25147, 25507, 27179, 27299
```

occurs exactly `k-2` times.  In particular their full raw Gram matrix for
the Conway parameters is `199584 J6`, regardless of `E0` or the number of
prisms.  This explains the rank-one outcome of the preceding 41-column
calculation and closes that route to an `E0` bound.

## Bijection

Fix an ordered triangle `T={a,b,c}` and distinguish the ordered pair `(a,b)`.
Choose any of the `k-2` vertices `v` in `N(a)\T`.  No vertex outside `T`
can be adjacent to two vertices of `T`: the corresponding triangle edge
already has its unique common neighbour in `T`.  Thus `b-v` and `c-v` are
nonedges.

Let `u` be the unique common neighbour of the adjacent pair `a,v`.  Then
`u` is outside `T` and is adjacent to neither `b` nor `c`.  Let `w` be the
second common neighbour of the nonadjacent pair `b,v`; its first is `a`.
The vertex `w` is distinct from all of `a,b,c,u,v`.  In particular `w=u`
would give the forbidden edge `b-u`, and `w=c` would give `c-v`.

The only additional pairs to check are `a-w`, `u-w`, and `c-w`:

- `a-w` would give the edge `a-v` two common neighbours `u,w`;
- `u-w` would give the edge `u-v` two common neighbours `a,w`;
- `c-w` would give the edge `b-c` two common neighbours `a,w`.

All are absent.  Therefore the six vertices induce precisely the edges

```text
ab, ac, bc, au, av, uv, bw, vw.
```

The induced rooted flag identifies `v` uniquely, so this construction is a
bijection.  The six ordered pairs of distinct triangle vertices produce
the six listed rooted flag masks.  There are `nk` ordered triangles, hence
every raw Gram entry equals `nk(k-2)^2`; for `(n,k)=(99,14)` this is
`1386*144=199584`.

## Why the missing chords do not help here

For a PSD Gram matrix, a `2x2` block `c J2` forces the two represented
vectors to coincide.  Since the preceding six closed blocks form a
connected `C6`, every PSD completion of that partial matrix is necessarily
`c J6`.  Thus its missing nine entries were already forced at the abstract
PSD level.  The bijection above proves those entries directly for every
graph with the required parameters.

The previous statement that a closed `3x3` coefficient block requires
additional H9 masks remains a statement about explicit coefficient
representation.  It does not prevent the connected rank-one blocks from
forcing the remaining Gram entries.  Here the forced entries supply only
universal equalities, so extending this family would not itself establish
an `E0` lower bound.

## Checks

The producer checks all 128 supergraphs of each six-vertex template; only
the stated induced graph respects the local common-neighbour bounds.  It
also counts the flags independently in the `3x3` rook graph: all 36 ordered
triangles have count two for each flag, giving raw Gram `144 J6`.

An independent proof review confirmed the distinctness and nonedge steps.
The companion audit reconstructs the templates and rook-graph counts
without importing the producer or its graph-encoding helpers.
