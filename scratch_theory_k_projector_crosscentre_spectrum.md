# Cross-centre residual identity for the endpoint signed projector

Assume `sum_r E0(r)=0`. Put `M=4I+P-K`, where the disjoint positive and
negative relations have valencies 32 and 36, and `M^2=21M`. The calculation
below uses the full projector equation, without assuming that `M` and `K`
commute. It yields an exact residual identity but no positive lower bound
on the number of `K` triangles.

## The missing residual

The orthogonal projectors

```text
E0=J/231, E=M/21, F=I-E0-E
```

have ranks 1, 44 and 186. Since `tr(MK)=-231*36=-8316`,
`tr(EK)=-396`. Define

```text
q = tr(EK^2),
eta = q-3564
    = ||EKE+9E||_F^2 + ||FKE||_F^2 >= 0.             (1)
```

The constant-space cross term vanishes because `K1=36*1` and `E1=0`.
Let `d=tr(K^3)=6*tau_K`. Expanding `P=M+K-4I`, reducing ordinary powers
with `M^2=21M`, and using cyclic invariance of trace gives

```text
tr(P^3)  = d+63q-219912,
tr(P^2K) = d+42q-174636,
tr(PK^2) = d+21q-33264.                              (2)
```

Thus the relevant nonnegative mixed count has the exact form

```text
tau_K+7eta = 4158+tr(P^2K)/6,
tau_K >= 4158-7eta.                                  (3)
```

Here `tr(P^2K)` is twice the number of relation triangles with two `P`
edges and one `K` edge. An upper bound `eta<594` would therefore force a
`K` triangle. Even that would not force its endpoint labels to be compatible:
the previous targeted lane permits zero, one or two equal-label corners.

## Full first Schur-projector conditions

The entry alphabet gives `S=M o M=M+12I+2K`. The nontrivial Schur products
of the three projectors are

```text
E o E = S/441,
E o F = (792I-12M-22K)/4851,
F o F = (34023I+143M+242K+J)/53361.                  (4)
```

Products involving `E0` are the corresponding projector divided by 231.
All six products are PSD. In particular the first two give operator bounds

```text
K >= -6I-M/2,
K <= 36I-(6/11)M.                                   (5)
```

These are valid even without commutation. The common first two trace
moments `tr(S)=3696` and `tr(S^2)=74844` are fixed by the entry alphabet.

## Exact scalar control with tau_K=0

The following abstract simultaneous spectral table satisfies the scalar
consequences just listed:

| Sector | Multiplicity | M eigenvalue | K eigenvalue |
|---|---:|---:|---:|
| constant | 1 | 0 | 36 |
| E | 9 | 21 | -15 |
| E | 26 | 21 | -9 |
| E | 9 | 21 | -3 |
| F | 22 | 0 | -6 |
| F | 10 | 0 | -3 |
| F | 134 | 0 | 3 |
| F | 20 | 0 | 6 |

It gives `tr(K)=0`, `tr(K^2)=8316`, `tr(K^3)=0`, `q=4212` and
`eta=648`. Every expression in (4), including the three constant-projector
products, has nonnegative eigenvalues. The mixed cubic traces are

```text
tr(P^3)=45444, tr(P^2K)=2268, tr(PK^2)=55188.
```

More strongly, all ten induced three-point relation-colour counts for
`P,K,Z=J-I-P-K` are nonnegative integers. In the order
`PPP,PPK,PKK,KKK,PPZ,KKZ,PKZ,PZZ,KZZ,ZZZ` they are

```text
7574,1134,27594,0,90720,117936,208656,403704,451332,719145.
```

They satisfy every edge-incidence and centred-wedge incidence equation for
valencies `32,36,162`. Thus adding those cubic counting inequalities and
all six first Schur-projector PSD expressions still permits `tau_K=0`
at the scalar level.

This table is not an entrywise matrix realization. In particular it does
not construct a signed integral `M`, a simple `K`, or actual Hadamard
products realizing the displayed spectra. It cannot refute an implication
of the complete entrywise projector constraints. It precisely shows the
limitation of the listed spectral/moment consequences. The bounded lane
stops here: a useful next theorem must control (1) using additional
entrywise cross-centre information, or couple endpoint partitions directly.

## Verification

```text
python scratch_theory_k_projector_crosscentre_spectrum.py
python scratch_theory_k_projector_crosscentre_spectrum_audit.py
```

The audit imports no producer code. It expands all 231 spectral slots,
independently expands the noncommutative cubics, checks six Schur expressions,
and reconstructs all ten relation-triangle counts directly from cubic trace
products. Status: `INDEPENDENT_K_PROJECTOR_CROSSCENTRE_SPECTRAL_AUDIT_PASS`.
No order-eight regeneration, ambient order-nine census, graph construction,
or positive `E0` bound is claimed.
