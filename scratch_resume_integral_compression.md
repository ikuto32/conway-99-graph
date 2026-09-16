# Exact integral compression control at E0=0

A symmetric integral 21 by 21 compression exists with E0=0, all the
root-group row identities, and the full spectral compression condition.
It attains the previously derived sharp bound tr(C^2)=2772. Consequently
these conditions, including their simultaneous symmetry and integrality,
cannot by themselves prove a positive lower bound for E0.

The explicit matrix is in `scratch_resume_integral_compression.json`.
Its support order is the lexicographic order of the 21 pairs of 0,...,6.
The diagonal is zero, overlap entries are 1 or 2, and disjoint entries are
3 or 4. Direct integer multiplication gives

```
C 1 = 48 1,
C L = 16 J - 8 L,
tr(C^2) = 2772.
```

Here L is the unsigned support incidence matrix and L^T L=5I+J.
Let H=L(L^T L)^(-1)L^T, Pi=I-H, and Cbar=(8/3)J-8H. The exact audit gives

```
Delta=C-Cbar=Pi Delta Pi,
tr(Delta)=0,        ||Delta||_F^2=84.
```

On im(L) the eigenvalues of C are 48 and six copies of -8. On its
14-dimensional orthogonal complement they are those of Delta. Every such
eigenvalue t has t^2<=84, in particular -10<t<10. This is strictly within
the required interval [-16,12]. There is no numerical eigensolver in this
certificate.

The full compression defect also passes, not only its trace. Define

```
G=48I+32J-C-8LL^T,
K4=4G-C^2=192Pi-4Delta-Delta^2.
```

K4 vanishes on im(L) and has eigenvalues 192-4t-t^2>52 on its complement.
Thus K4 is positive semidefinite, has rank14, and trace2604. G is positive
semidefinite because 4G=K4+C^2.

The producer solved a 210-Boolean linear model in about 0.02 seconds.
The separate audit imports no producer or solver, reconstructs all
incidences, and verifies the stated identities using exact fractions.

This is a control for a necessary-condition relaxation. It supplies no
84 by 21 integral degree matrix D, no reciprocal 84-vertex adjacency B,
and no 99-vertex graph. The unresolved next conditions include selecting
four compatible degree rows for every fibre, their six internal pair
common-neighbour counts, and reciprocal edges shared between fibres.

Reproduce the certificate audit with:

```
python scratch_resume_integral_compression_audit.py
```
