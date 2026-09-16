# E71 equitability-defect rank and port audit

Status: exact finite calculations; source 2601 is excluded, while source 724
is an explicit boundary for the defect-only method.

## 1. The defect Gram

Let `B` be the adjacency matrix on the 84 vertices at distance two from a
root, `M` the `84 x 21` four-fibre incidence matrix, `Q=M/2`, `L` the
unsigned incidence matrix of the 21 supports in `K7`, and

```
C=M^T B M,
W=(I-QQ^T) B Q.
```

The SRG identity on the outer layer gives the exact integral matrix

```
K4 := 16 W^T W
   = 192 I + 128 J - 4C - 32 L L^T - C^2.              (1)
```

For the ordinary compression

```
C0=12I+4J-4LL^T
```

and the full Gram circulation `Z=C0-C`, we have `ZL=ZJ=0`.  Hence

```
K4=28Z-Z^2.                                             (2)
```

If `x` lies in source fibre `G`, its scaled row of `W` is

```
8 W[x,F] = 4 deg(x,F)-C[G,F].                           (3)
```

Consequently every `c in ker(K4)` gives the pointwise, not merely averaged,
degree equation

```
4 sum_F c_F deg(x,F) = (C c)_G.                         (4)
```

This is the reusable **kernel-port lemma**.  In particular, if
`e_A-e_D in ker(K4)` and `C[G,A]=C[G,D]`, every vertex of `G` must have equal
degrees into `A` and `D`.

## 2. The arithmetic-sharp source 2601 is impossible

Source 2601 has two canonical macros, both with `Q=2` and labelled coverage
`131072`.  Its nonzero spectra are exactly

```
spec(Z)  = {8,9,9},
spec(K4) = {160,171,171}.
```

Thus the earlier trace/rank/congruence bound is sharp, but the pointwise
factorization contains more information.  Put

```
A={0,2}, D={1,4}, B={0,4}, C={1,2}.
```

Direct exact multiplication gives

```
e_A-e_D in ker(K4),
C[B,A]=C[B,D]=C[C,A]=C[C,D]=2.
```

Equation (4) therefore forces `deg(x,A)=deg(x,D)` on every vertex of fibres
`B` and `C`.  The port stubs fixed by the two internal states instead give:

```
state 1, on B: A=(1,1,0,0), D=(1,0,1,0)
state 1, on C: A=(0,0,1,1), D=(0,1,0,1)

state 4, on B: A=(0,1,0,1), D=(0,0,1,1)
state 4, on C: A=(1,0,1,0), D=(1,1,0,0).
```

Changing a group matching changes the partner of a stub but never these
incidence vectors.  Hence every `8192` overlap completion of each state is
impossible.  The two macros, total labelled coverage `262144`, are excluded
without a numerical eigensolver or SAT.  The independent replay is
`scratch_theory_e71_source2601_kernel_port_audit.py/.json` with status
`INDEPENDENT_SOURCE2601_KERNEL_PORT_EXCLUSION_PASS`.

## 3. Full E71 kernel-port census

For every one of the 165 integral PSD full-Gram profiles, each exceptional
fibre `{g,h}` was compiled into a binary relation between the two matching
choices `X_g,X_h`:

1. enumerate all integral degree rows in `row(K4)`;
2. impose the four fixed internal degree rows and all port-incidence rows;
3. require the four residual rows to sum to zero (the prescribed block
   totals); and
4. solve the resulting seven-variable binary CSP by exact AC-3/backtracking.

From the 157 full-Gram-viable canonical macros (coverage `58556416`), the
filter rejects 25 macros from 15 source rows, coverage `9469952`, and leaves
132 macros, coverage `49086464`.  Sixteen rejected macros (coverage
`1212416`) admit the simple equal-degree form of the kernel-port lemma; nine
(coverage `8257536`) need a larger row-space relation.  This is a strict new
one-root filter, but it is not a proof that `tau>=13` is impossible.
In fact every one of the 25 rejected macros already has an empty relation
for at least one individual exceptional fibre, so none of these exclusions
depends on a delicate global CSP search.  The complete census and an
independent manifest/coverage replay are
`scratch_theory_e71_equitable_kernel_port_census.py/.json` and
`scratch_theory_e71_equitable_kernel_port_census_audit.py/.json`.

## 4. Source 724 is a sharp failure control

The `source724/state1/Q2` profile (catalogue key `(724,1,0)`, labelled
coverage `32768`) has

```
chi_Z^+(t)  =(t-9)(t^2-17t+48),
chi_K4^+(t) =(t-171)(t^2-283t+17088).
```

It has no kernel direction beyond the unsigned-incidence/ordinary-fibre
baseline.  Of its 1024 exact overlap products, the stronger rank-three
degree CSP leaves 128.  This stronger CSP enforces the full defect Gram,
all fibre block totals, the fixed internal and port degrees, and graphical
degree sequences for every unresolved exceptional `4 x 4` binary block.

One retained branch was materialized as an explicit binary 84-vertex,
504-edge graph.  Direct replay verifies:

```
all outer degrees = 12,
compression = C,
R^T R = 4K4 (equivalently 16W^TW=K4),
the materialized exceptional graph passes induced-pair upper,
the materialized exceptional graph passes forced-C4 BP.
```

The deterministic completion chosen for its still-free disjoint blocks is
not an SRG outer layer: it has 1025 positive pair-upper violations.  Thus it
is a witness only that rank, integrality, block totals, and existing local
port filters do not by themselves exclude `E0=71,Q=2`; the missing input is
the stronger pair/common-neighbour or cross-root compatibility.

The witness and direct checks are in
`scratch_theory_e71_source724_degree_witness.py/.json`.

## 5. Order-eight coefficient boundary

The existing order-eight package has 916 classes, 208 deletion rows, 944
marked-vertex rows, 4440 marked-pair rows, and 2414 exact pair-root
coefficient matrices.  It should not be regenerated.  More importantly,
the independently checked Wave159/161 rational pseudowitness satisfies that
base system and fifteen retained scalar cuts while having

```
n3=4158, z11=16632, N(H_delta)=P=sum_r E0(r)=0.
```

Therefore no positive `E0` lower bound can be a conic consequence of those
pair-root order-eight matrices and marked equations alone.  The source2601
certificate conditions on one complete root compression and compares four
root groups simultaneously; it is not a single one of the 2414 coefficient
matrices.  Its natural global home is a full four-root/root-compatibility
block.  This agrees with the pseudowitness's known negative directions in
the full four-root covariance blocks for root masks 3 and 12.

## Claim boundary

Source 2601 and the 25 census macros are rigorously excluded by necessary
one-root identities.  Source 724 is rigorously a feasible point of the
stated defect/block-degree relaxation, not a graph satisfying all SRG pair
equations.  Overall `E0>=72` or even `E0>=71` is not proved here.
