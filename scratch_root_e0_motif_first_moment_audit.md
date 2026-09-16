# E0 small-motif first-moment audit

Status: **E0_MOTIF_FIRST_MOMENT_AUDIT_PASS**.

This is a clean-room finite audit: it imports no project discovery code.  It
starts from explicit edge lists and enumerates every permutation of six or
seven vertices.  Frequencies count **unlabelled induced vertex subsets**.

## Conventions and graph identification

Edges are ordered lexicographically `(0,1),(0,2),...`; the canonical mask is
the least mask under all vertex permutations.  Three independent
transcriptions have the same canonical mask:

```text
diagonal flag HDelta     120568
all-seven panel Z2       120568
Hamiltonian panel H18    120568
```

Thus `HDelta = Z2 = H18`, with canonical mask **120568**.  It has 11 edges,
degree multiset `(3,3,3,3,3,3,4)`, and automorphism group order 4.  The unique
degree-4 vertex is the root, its two non-neighbours form the unique diagonal
edge, so every induced copy supplies exactly one `(root, diagonal)` flag.

## Side and diagonal coefficients

For a side edge `xy`, the supports of `x,y` at root `r` share one vertex; the
two remaining support vertices are the endpoints of one root-neighbourhood
matching edge.  The six forced vertices induce a triangular prism.  Conversely
every choice of one of a prism's six vertices as root recovers exactly one
side flag.  Exhaustive rooted-role checking gives

```text
sum_r S(r) = 6 P.
```

For a diagonal edge the two size-two supports are complementary and their
four root-neighbours induce a perfect matching.  Together with `r,x,y` this
is exactly HDelta, and the unique-root argument gives

```text
sum_r D(r) = z2.
```

In labelled-injective conventions these become `sum S=inj(prism)/2` and
`sum D=inj(HDelta)/4`, since the automorphism orders are 12 and 4.

## Independent origin of the quarter coefficient

Use the six-vertex type N4 of canonical mask 1916.  It has one triangle and
exactly two distinguished edges: an edge from a degree-2 vertex to a
degree-3 vertex in that triangle.  Such an edge has no common neighbour
inside N4, so lambda=1 supplies one unique external common neighbour.

For each distinguished edge, exhaustive checking of all 64 attachment
subsets under the induced lambda/mu upper bounds leaves exactly two patterns:
one Hamiltonian-H11 pattern and one Hamiltonian-H18 pattern.  Conversely H11
has one N4 deletion flag and H18 has four.  Double counting therefore gives

```text
2 n4 = h11 + 4 h18.                                 (1)
```

The standard six-vertex counts

```text
6 n1+n4 = n*k*(k-2)/2,
3 n1+n3 = n*k*(k-2)/4
```

give `n4=2n3` by doubling the second and subtracting the first.  Substitution
in (1) independently recovers the Hamiltonian-table relation

```text
h18 = n3-h11/4.
```

The all-seven table uses `Z` indices, not `H` indices.  Its hashed TeX input
independently states `z2=n3-z11/4`.  Since the graph transcriptions prove
`Z2=H18`, their frequencies satisfy `z2=h18`; comparison also yields the
numerical frequency equality `z11=h11`.  No assertion that the two graphs
indexed `Z11` and `H11` are isomorphic is used here.

## First moment

With the already established prism identity `P=(4158-n3)/3`, we obtain

```text
sum_r E0(r)
 = 6P+z2
 = 8316-n3-z11/4.                                  (2)
```

This corrects the old, quarantined `sum E0=6P` claim: the missing term is
precisely the induced-Z2 count.

## Second moment boundary

Writing `T` for (2), the exact flag expansion is

```text
sum_r E0(r)^2
 = T + 2 sum_r [C(S(r),2)+S(r)D(r)+C(D(r),2)].
```

Hence, if `T=99q+s`, `0<=s<99`, integrality gives the sharp mean-only bound

```text
sum_r E0(r)^2 >= (99-s)q^2+s(q+1)^2 = ceil(T^2/99).
```

The pair terms can span up to 13 vertices, so the direct square expansion does
not close using only six- and seven-vertex motif frequencies.  This does not
rule out a further indirect SRG identity; none is asserted here.

## Boundary

This is an executable finite audit, not a formal proof.  It neither constructs
nor excludes `srg(99,14,1,2)`; Conway's 99-graph problem remains **UNKNOWN**.
