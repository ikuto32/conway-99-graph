# Second-order fibre-compression audit

Let the 21 support fibres be `F`, let `e_F` be the number of edges induced by
`F`, and put

```
E0 = sum_F e_F = C + Q,       delta_F = 4 - e_F.
```

The result here is unconditional:

```
E0 is not 81, 82, or 83.
```

Equivalently, `E0 <= 80` or `E0 = 84`.  The `E0=84` case is structurally
consistent with this argument and is exactly the all-`C4` fibre class tested
by the separate canonical SAT/CP-SAT computations.  Without a formal UNSAT
certificate for that computation, this note does **not** call `E0 <= 80` an
unconditional theorem.

## Compression proof

Normalize each fibre indicator by dividing it by two, and compress `B` to
their 21-dimensional span.  Call the resulting symmetric matrix `R`, and put
`D=4R`.  Its entries are

```
D_FF = 2 e_F,
D_FG = number of edges between F and G   (F != G).
```

The all-one direction gives eigenvalue 12.  The six centred group-incidence
directions give eigenvalue -2.  The orthogonal 14-dimensional fibre-constant
space lies in `ker(P^T)`, on which `B` has only eigenvalues 3 and -4.
Therefore the remaining 14 Ritz values of `R` lie in `[-4,3]`, and their sum
is `E0/2`.  Maximizing their squared sum over this interval gives an exact
upper bound for `tr(R^2)=tr(D^2)/16`.

For each fibre, BP gives the two off-diagonal block row sums

```
sum_{G sharing one support group} D_FG = 4 delta_F,
sum_{G disjoint from F}           D_FG = 40 - 2 delta_F.
```

Entries in the first line are nonnegative integers on the line graph of
`K7`.  For the second line write `D_FG=4-x_FG` on the Kneser graph `KG(7,2)`;
then its unsigned incidence matrix `H` obeys `H x = 2 delta`.  The exact real
least-norm relaxation is computable because

```
H H^T = 10 I + A(KG(7,2))
```

has eigenvalues 20, 6, and 11 with multiplicities 1, 6, and 14.  Exhausting
all partitions and placements of total deficit 1, 2, and 3 makes the lower
bound on `tr(D^2)` exceed its spectral upper bound (or leaves no nonnegative
overlap-block realization).  This excludes `E0=83,82,81`.  Deficit zero
attains equality, explaining why `E0=84` is not excluded.

## The extremal E0=80 branch

The same audit leaves only one fibre-size distribution at `E0=80`:
17 fibres are `C4` and four are `P4`.  A `C4` fibre has no edges to an
overlapping support and a perfect matching to every disjoint support fibre.
Consequently, among the four exceptional supports, both their overlap graph
and its complement must support fixed positive row sums.  Comparing their
integer square costs with the spectral bound leaves only

```
overlap graph on the four P4 supports = C4,
disjointness graph                    = 2K2.
```

Thus, after relabelling groups, the supports are the four edges of a group
cycle `(01,12,23,30)`.  Every adjacent pair of exceptional fibres has two
edges between it, and each opposite pair also has two.  The former match the
endpoints of the two `P4`s; the latter match their two internal-degree-two
vertices.  The compression is the all-`C4` compression plus a rank-one
perturbation, changing one Ritz value from 3 to 1, so it remains spectrally
feasible.

`scratch_general_e80_local_audit.py` exhausts the resulting
`4^4 * 2^6 = 16,384` induced 16-vertex choices.  BP rejects 16,256, but 128
survive BP and all induced common-neighbour upper bounds.  Hence this bounded
local test does not eliminate `E0=80`; extending it requires constraints from
the other 68 outer vertices.

## Other exact checks

For any fibre `F`, if `n_F(w)` is the number of neighbours of `w` in `F`,

```
sum_w C(n_F(w),2) = 8 - e_F.
```

Subtracting witnesses inside `F` leaves an external collision budget of
8, 7, 6/5, 3, or 0 for the eight possible fibre types.  The audit JSON lists
all resulting outside-degree distributions.  In particular a `C4` fibre has
exactly 40 outside vertices with one neighbour in it and 40 with none.

The spectrum of `B` also fixes `tr(B^3)=840`, `tr(B^4)=31752`, hence 140
triangles and 1,071 four-cycles.  These counts are checks rather than an
additional exclusion in the argument above.
