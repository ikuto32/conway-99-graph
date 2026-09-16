# Outer-layer characteristic-two Artin--Schreier probe

Status: `INDEPENDENT_OUTER_F2_ARTIN_SCHREIER_AUDIT_PASS`; null for an
`E0` lower bound.

For every root, the 84-vertex outer adjacency matrix satisfies

```text
B^2+B=10I+2J-Q_line.
```

Modulo two this becomes `B^2+B=Q_line`.  A clean construction of the fixed
line graph of `K14-7K2` gives

```text
rank(Q)=12, rank(Q^2)=6, Q^3=0,
JCF(Q)=J3(0)^6 + J1(0)^66.
```

The target integer spectrum of `B` reduces to generalized eigenspace
dimensions 40 and 44 for eigenvalues one and zero.  Assigning the Jordan
blocks of `Q` to the two roots of `x^2+x` permits dimension 40 (indeed the
66 singleton blocks make every dimension possible), so no contradiction is
obtained.  More concretely,

```text
B0=Q+Q^2
```

is symmetric, zero-diagonal, has even row weight 22, and satisfies
`B0^2+B0=Q` over `GF(2)`.  It is only a modular control: it does not have the
target integer spectrum, target degree 12, or a graph lift.

Thus the characteristic-two Jordan data discard no `E0` layer.  Any useful
finite-field refinement must retain entrywise degree/support information or
an integral/2-adic lift; this bare route is stopped.

Artifacts:

```text
scratch_theory_outer_f2_artin_schreier_probe.py/.json
scratch_theory_outer_f2_artin_schreier_probe_audit.py/.json
```
