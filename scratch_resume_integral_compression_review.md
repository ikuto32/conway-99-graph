# Independent review of the integral E0=0 compression control

The claimed necessary-condition counterexample is sound. The independent
exact auditor ran successfully against input SHA-256
`7b7ac3ad4d9f36beadcc62589b76f0bf95a13656516d1c7bb2d4af3aec37ee1e`.
The review inspected both the graph-to-compression derivation and the
auditor; no producer or solver execution was needed.

For a hypothetical graph let U be the 84-by-21 fiber indicator, B its
second-layer adjacency, N the 14-by-84 exact-label incidence, and L the
21-by-7 support incidence. Then U^T U=4I. The SRG block identity is

```text
B^2+B=12I+2J-N^T N,       (NU)^T(NU)=8LL^T.
```

With C=U^T B U and D=BU, this gives
`G=D^T D=48I+32J-C-8LL^T`. B has row sum 12, yielding C1=48 1.
The first-layer common-neighbor quotas give `BU L=4J-2UL`, and hence
`CL=16J-8L`. Symmetry, integrality, nonnegative entries, and
`tr(C)=2E0` also follow directly. In particular

```text
K4=4G-C^2=4D^T(I-UU^T/4)D >= 0.
```

This is a necessary matrix inequality, because UU^T/4 is an orthogonal
projection. The candidate satisfies it, not merely its trace inequality.

The audit checks exact rational projector identities and finds
`Delta=C-Cbar=Pi Delta Pi`, `tr(Delta)=0`, and
`||Delta||_F^2=84`, where Pi has rank 14 and is orthogonal to col(L).
For symmetric Delta every eigenvalue t satisfies t^2<=84<100. Therefore
`-10<t<10`, and `192-4t-t^2>52`. The exact identity
`K4=192Pi-4Delta-Delta^2` proves K4 is positive semidefinite, vanishes
on col(L), and has rank 14. It also proves the required cycle eigenvalue
interval [-16,12]. No floating-point spectral approximation is used.

Thus simultaneous symmetry, integer entries, these row identities, and
the full compression spectral/PSD condition admit E0=0. There is no
missing condition in this limited conclusion. Calling C an actual graph
compression would require further evidence: no integral D with
`U^T D=C` and `D^T D=G`, reciprocal adjacency B with D=BU, or 99-vertex
graph is supplied. Those omissions are explicitly acknowledged in the
original note. This review claims no positive E0 bound, macro exclusion,
graph construction, or nonexistence theorem.

Command:

```text
& 'C:/Users/ikuto/.local/bin/python3.12.exe' -B scratch_resume_integral_compression_audit.py
```

The existing exact validator at
`external_conway99_research/verification/check_srg.py` has a strict
zero-based JSON parser and both set-intersection and integer-matrix
checks. It cannot directly read the requested one-based `{u, v}` text
format. The existing Rust verifier is also JSON-oriented and scans
numbers permissively, so it is not a strict submission-format validator.
