# Independent audit of the E71 degree-moment certificates

Status: `INDEPENDENT_E71_DEGREE_MOMENT_LP_AUDIT_PASS`.

The audit checks all 140 selected frozen profiles and independently validates
68 integer Farkas certificates. They exclude 66 complete frozen macros with
labelled coverage 22,675,456. The input has 132 macros of total coverage
49,086,464; this certificate family alone leaves 66 macros of coverage
26,411,008. Previously proved exclusions, including source724, are not added
to those figures here. This is not a complete E0=71 exclusion or a pointwise
lower bound on E0.

## Necessary moment model and its normalization

Let `B` be the unknown adjacency matrix on the 84 second-neighbour vertices,
and `U` their 84-by-21 support-fibre incidence matrix. Each fibre has four
vertices, so `U^T U=4I`. Put

```text
C=U^T B U, R=4BU-UC.
```

For a vertex `x` in fibre `s`, write `d_x` for its 21 fibre-degree counts.
Its row in `R` is

```text
r_x=4d_x-C[s,*],  d_x in {0,1,2,3,4}^21, sum d_x=12.
```

If `L` is the 14-by-84 root-neighbour incidence matrix, the SRG block
equation is `B^2=12I-B+2J-L^T L`. The explicit four-corner labels give

```text
(LU)^T LU = 8 I_support,
(I_support)[s,t]=|s intersect t|.
```

Consequently

```text
U^T B^2 U = 48I-C+32J-8 I_support,
R^T R = 16 U^T B^2 U-4C^2
      = 4(192I-4C+128J-32 I_support-C^2)=4K4.       (1)
```

The compression reconstruction also checks
`K4=28Z-Z^2`, with `Z=C_baseline-C`. Both formulas agree entrywise.
Equation (1) proves that every `r_x` lies in the row space of `K4`.

For every fibre, `sum_{x in fibre} r_x=0`. The diagonal degree `d_x[s]`
is fixed by the frozen internal graph. Ordinary fibres have four internal
edges and no triangle, hence form a four-cycle with degrees `(2,2,2,2)`.
The small four-vertex assertion and its root-label triangle prohibition are
checked independently.

The linear relaxation groups vertices by `(source fibre, internal degree)`.
Each possible raw residual row gets a nonnegative real weight. Group counts
fix the four vertices in each fibre; the fibre first moments vanish; global
second moments equal the principal-coordinate restriction of `4K4`.
Every genuine completion supplies integral such weights. Thus infeasibility
of this relaxation excludes the profile.

## Independent reconstruction

The audit imports neither the LP producer nor its base helper and uses no
LP solver. It performs the following exact checks:

- Reconstructs all `C` and `K4` matrices from the frozen macro and full-Gram
  catalogues, with every input hash checked.
- Uses positive principal elimination and a principal inverse to certify
  the rank and complete row-space parametrization. This is independent of
  the producer's RREF domain construction.
- Enumerates all five-valued pivot-degree choices and checks every remaining
  degree coordinate and degree sum. All 23,137 raw degree rows across the
  140 profiles are reconstructed.
- Reconstructs every exact-label internal degree, group count, fibre first
  moment and global second-moment coefficient. Every emitted variable and
  every model hash agrees.
- For each integer multiplier `y`, checks every column of `A^T y` is
  nonnegative and `b^T y<0` using integer arithmetic alone.

The Farkas contradiction is immediate: if `Ax=b` and `x>=0`, then
`b^T y=x^T A^T y>=0`, contrary to the checked negative pairing. Floating
LP status, rationalization settings and producer assertions are not used
as proof.

The complete frozen manifest contains 165 full-Gram profiles on 157 viable
macros. The selected frontier contains 140 profiles on 132 macros. Before
crediting any of the 66 new macro exclusions, the audit requires that
**every full-Gram profile listed for that macro** has an independently
checked Farkas certificate. It does not credit a macro merely because all
selected LP tasks failed, nor rely on an earlier kernel-port status to fill
a missing profile.

Profiles without certificates remain unresolved; their LP statuses do not
assert that a graph exists. No local graph completions, matching products,
or new order-eight classes are enumerated.

## Reproduction

```text
python scratch_theory_e71_degree_moment_lp_audit.py
```

The machine-readable record is
`scratch_theory_e71_degree_moment_lp_audit.json`. It includes every profile
model/domain hash, the fully covered macro list, and the unresolved list.
The audited frontier input has SHA256
`9426BF822D34A47C928E838FB41276A62B7ED2300C9FC009D53D8D48BE5C77CD`.
