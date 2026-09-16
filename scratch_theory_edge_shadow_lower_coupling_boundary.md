# Selected edge roots versus the order-eight shadow: exact visibility boundary

Status: `EDGE_SHADOW_LOWER_COUPLING_INDEPENDENT_AUDIT_PASS`.

The producer is `scratch_theory_edge_shadow_lower_coupling_boundary.py` and
the separate replay is
`scratch_theory_edge_shadow_lower_coupling_boundary_audit.py`.  Both read
the frozen 916/208/944/4440/2414 resources; neither regenerates a graph
class or coefficient matrix.

## 1. What the missing selector is

Fix a target edge `e=xy`, let `u` be its unique triangle mate, and let

```text
y_r = Yhat[r,e] in {0,1,2},
m_r = 1[r~u].
```

The support-disjointness proved for the augmented relation leaves exactly
three nonzero states:

| `(m_r,y_r)` | meaning | `e` lies in an `r`-fibre |
|---|---|---:|
| `(0,1)` | good singleton `X` root | 0 |
| `(0,2)` | doubled `X`, hence diagonal root | 1 |
| `(1,1)` | prism `Pi`, hence side root | 1 |

Thus the required binary selector is exactly

```text
s[r,e]=m_r y_r+binom(y_r,2).                             (1)
```

The order-eight shadow uses only

```text
beta_rel=sum_(r rel s,e) y_r y_s.
```

By contrast, `K_edge` needs `s[r,e]s[s,e]`.  Expanding the product in (1)
requires mate-bit-weighted terms and doubled-entry mixed moments.  These are
not entries of the existing pair-root matrices.

## 2. Exact order-nine nonmeasurability witness

There is a labelled nine-vertex base with source triangles `012` and `345`,
target triangle `678`, and two-cross-edge matchings

```text
1-7, 2-8, 4-7, 5-8.
```

Vertices 0 and 3 are the source roots.  The optional edges `0-6` and `3-6`
are precisely the two mate bits.  Deleting mate vertex 6 leaves the same
labelled order-eight graph for all four choices `00,01,10,11`, whereas the
selected-root pair has values

```text
0,0,0,1.                                                (2)
```

All four completions satisfy every induced adjacent/nonadjacent
common-neighbour upper bound.  The same construction works with `0-3`
absent or present, so (2) applies to both the nonadjacent-root and
adjacent-root shadows.

This is an exact arity statement: no positive coefficientwise inequality

```text
s[r,e]s[s,e] >= c y_r y_s,  c>0,
```

can hold at the order-eight shadow level.  It is not a claim that every
local completion extends to a 99-vertex SRG; a genuinely global order-nine
identity could still correlate their totals.

## 3. Inspection of the frozen exact matrices

The audit reads the frozen Wave147 coefficient file directly.  It contains
1,207 class coefficient records for each ordered-root relation, hence 2,414
records total, with represented union orders exactly 5--8.  Wave148 has the
stated 944 marked-vertex and 4,440 marked-pair rows, and no order-nine
columns.

No individual matrix-entry coefficient vector is proportional to even the
coarser sparse `beta_e` or `beta_n` shadow.  The previously frozen modular
span calculation gives

| relation | entry-span rank mod 1,000,003 | after appending shadow |
|---|---:|---:|
| roots adjacent | 656 | 657 |
| roots nonadjacent | 985 | 986 |

This is a useful finite-field obstruction, but is deliberately **not**
promoted to a rational nonspan theorem: rank can drop modulo a prime.  The
decisive exact limitation for the selected statistic is instead (2).  It is
not a function on the order-eight class stream at all until the mate vertex
and doubled-root status are added.

Consequently no required exact linear combination was extractable from the
2,414 matrices.  An indirect conic consequence after introducing and then
eliminating order-nine variables remains a different, currently absent
certificate.

## 4. Nonedge collision double count

For each nonedge `f`, split its fibre codegree into side and diagonal roots,

```text
H_f=s_f+d_f.
```

The global position totals are exact:

```text
sum_f s_f = 99*84-sum_r S(r) = 2n3,
sum_f d_f = 99*42-D_*          = 4158-D_*,
sum_f H_f = 12474-T.                                   (3)
```

At the `T=0` endpoint, the completely integral marginal assignment

```text
s_f=2, d_f=1, H_f=3  for every one of the 4158 nonedges
```

meets (3).  Its collision split is

```text
sum binom(s_f,2) = 4158,
sum s_f d_f      = 8316,
sum binom(d_f,2) = 0,
K_nonedge         = 12474.                              (4)
```

It also satisfies the summed root-group categories from the global Gram:
for each nonedge, equal/overlapping/disjoint support roots are `3,36,32`.
Thus `2*3+36=42` and their total is 71.

A collision between two rooted side-membership flags has generic union
order 10; side--diagonal has order 11; diagonal--diagonal has order 12.
The two flags already share the target pair.  Hence the generic part of
`K_nonedge` also lies beyond products of order-five flags with union at most
eight.  Equation (4) is an exact integer first/second-moment control, not an
assignment of actual roots to binary fibre partitions.

## 5. The sharp boundary and what remains open

The frozen Wave159 rational point has

```text
n3=4158, z11=16632, q(T)=12 everywhere,
Q2=33264, D_*=0, T=0, K_edge=0,
beta_e+beta_n=45738.
```

It satisfies the frozen pair-root centered PSD system, all marked rows, and
the retained scalar cuts recorded by the boundary audit.  The integer PSD
Gram control

```text
H0=84I+3(J-I-A)
```

has eigenvalues `336,72,93` and combines with (4) to put all required
collision mass on nonedges.  Therefore the frozen pair-root order-eight
matrices plus the scalar identities in this lane cannot yield a positive
`T` lower bound or `n3<4158`.

The scope distinction is essential.  Wave159 is indefinite in the full
four-root covariance blocks, so it is not a feasible point of that stronger
system.  Wave161 independently replayed exact negative quadratic forms in
root masks 3 and 12, with scaled values

```text
-27011041286703517116394938226429083495309284913470656030516224,
-88438068438190522607991067007701768100527095926734078733792256.
```

These are exact inequalities excluding this particular rational point.
They are not a lower bound on `T`: no identity writes either quadratic form
as a nonnegative remainder plus a positive multiple of `T`.  In particular,
no exact coupled dual certificate currently proves that **every** `T=0`
point violates a full block.  The Wave162 stored-witness audit likewise
found no unconditional exposed face; endpoint `n3=4158` remains unknown.

The minimal missing data are now precise:

1. an order-eight-to-nine extension statistic carrying both mate bits and
   whether each augmented entry is doubled, together with an exact
   PSD/affine dual; or
2. a two-root fibre-membership lift of generic union orders 10--12 that
   controls (4) rather than only its first moments.

Without one of these lifts, the lower-coupling lane closes at the explicit
boundary above.  No `submission.txt` is produced.
