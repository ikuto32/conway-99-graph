# E72 open-frontier equitability-defect exclusions

Status: `INDEPENDENT_E72_OPEN_DEFECT_RANK_EXCLUSIONS_PASS`.

For a root, let `B,M,Q,C,Z,W` have the meanings in
`scratch_theory_e71_source2601_kernel_port_proof.md`.  The exact identities

```
K4=16W^TW=28Z-Z^2,
8W[x,F]=4 deg(x,F)-C[G,F]       (x in fibre G)
```

imply that every scaled vertex-degree row lies in `row(K4)`.  Equivalently,
each `c in ker(K4)` imposes

```
4 sum_F c_F deg(x,F)=(Cc)_G
```

pointwise.  Applying this condition only to the 59 macros in the previously
audited open E72 frontier (coverage 2,236,416) excludes four macros.

## Source 171: rank-two internal parity

For macro `(171,0,0)`, exact `K4` has rank two.  On source fibre `01`, the
complete set of bounded integral degree rows in `row(K4)`, after imposing
degree 12 and the ordinary-fibre coordinates, is

```
(0,2,0,0,1,1,0,0)
(2,0,0,0,0,0,1,1)
```

in exceptional-fibre order

```
(01,02,03,04,13,14,23,24).
```

Thus an `01` vertex can have internal degree only 0 or 2.  The macro state
has internal degree vector `(1,1,1,1)`, an immediate contradiction.  This
excludes coverage 32,768 without enumerating group matchings.

## Sources 1095 and 1119: sparse kernel equalities

If `e_F-e_H in ker(K4)` and `C[G,F]=C[G,H]`, every vertex of `G` must have
equal degrees into `F` and `H`.  Exact matrix multiplication supplies this
condition for the following target pairs (all equal block totals are 2):

```
source1095, G=05: (01,25), (02,15)
source1095, G=34: (13,24), (14,23)

source1119, G=03: (04,35), (06,34)
source1119, G=12: (14,25), (16,24).
```

For each pair the source-side port incidence is independent of the selected
matching partner and is one of

```
(1,1,0,0) versus (0,1,0,1),
(0,0,1,1) versus (1,0,1,0),
(1,0,1,0) versus (0,0,1,1).
```

The vectors are unequal, so the pointwise kernel equality fails.  This
excludes both source1095 macros, coverage 8,192+16,384, and the source1119
macro, coverage 4,096.

## Coverage and boundary

The four exclusions total 61,440 labelled macro coverage, all at `Q=4`:

```
(171,0,0)     32,768
(1095,0,0)     8,192
(1095,0,1)    16,384
(1119,0,0)     4,096
```

The finite census is
`scratch_theory_e72_open_defect_rank_census.py/.json`; the independent exact
reconstruction is
`scratch_theory_e72_open_defect_rank_exclusion_audit.py/.json`.  Neither uses
SAT or floating-point linear algebra.

The two largest remaining individual macros, source150 `(4,0)` and `(7,0)`
(coverage 524,288 each), are a sharp boundary for this filter: both have
rank-three `K4`, seven bounded row patterns per exceptional fibre, and every
binary port relation is complete.  They remain open.  This negative control
is stored in `scratch_theory_e72_largest_open_defect_rank_probe.py/.json`.
