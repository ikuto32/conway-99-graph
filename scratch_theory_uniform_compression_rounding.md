# Uniform fibre-compression integrality and the loss under averaging

This is a necessary-condition derivation, not a positive lower bound on E0.
The companion script checks its finite arithmetic and explicit row controls.
It uses no graph search and regenerates no order-eight class.

## Graph identities and the outer spectrum

At a root let B be the outer 84-by-84 adjacency, N the 14-by-84 exact-label
incidence, P the 84-by-21 fibre incidence, L the 21-by-7 support incidence,
and M the matching on the fourteen root neighbours. The SRG block equations
give

```
B^2+B = 12I+2J-N^T N,
NB = 2J-(I+M)N,
P^T P=4I,                  (NP)^T(NP)=8LL^T.
```

Here NN^T has eigenvalues 24 on constants, 12 on the seven pair-antisymmetric
directions, and 10 on the six pair-constant zero-sum directions. Thus N has
rank 14. B acts on their lifted spaces by 12, 0, and -2, respectively.
On ker N the quadratic equation is B^2+B=12I, so the eigenvalues there are
3 and -4. Trace B=0 fixes their multiplicities at 40 and 30. In particular

```
spec(B) = {12^1, 3^40, 0^7, (-2)^6, (-4)^30}.
```

For C=P^T BP and the degree matrix D=BP this implies

```
C1=48 1,             CL=16J-8L,
D^T D=48I+32J-C-8LL^T.
```

The seven-dimensional col L has fixed C eigenvalues 48 and (-8)^6.
On its fourteen-dimensional orthogonal complement the compression C/4
is a compression of B restricted to ker N. Hence its eigenvalues t_i obey
-16 <= t_i <= 12. If E=sum_F e_F=E0, where C_FF=2e_F, then

```
sum_i t_i=2E,
tr(C^2)=2688+sum_i t_i^2 <= 5376-8E.             (1)
```

The last inequality follows by summing (t_i+16)(12-t_i)>=0.

## Integer entries give a sharper lower trace

Each fibre has four vertices and is triangle-free: a triangle would have
to give every edge its unique common neighbour internally, although among
three of the four square-corner labels some edge shares a root neighbour.
Thus its internal edge count e is in 0,...,4. Alternatively every locally
admissible internal state in the independently checked fibre catalogue has
at most four edges.

For a fixed source fibre F, CL=16J-8L and C1=48 imply

```
C_FF=2e,
sum_(G overlaps F) C_FG=16-4e,  ten entries,
sum_(G disjoint F) C_FG=32+2e,  ten entries.
```

For m integers with sum s=mq+r, 0<=r<m, the minimum sum of squares is
phi_m(s)=mq^2+r(2q+1). The pointwise proof is
(x-q)(x-q-1)>=0 for every integer x, followed by summation. Consequently

```
sum_G C_FG^2 >= g(e)=4e^2+phi_10(16-4e)+phi_10(32+2e),
g(0),...,g(4) = 132, 138, 156, 186, 224.          (2)
```

The successive slopes 6,18,30,38 are increasing. Summing (2) over 21
fibres with total e equal to E therefore gives tr(C^2)>=b(E), where

```
b(E) = 2772+ 6E     0<=E<=21,
       2520+18E    21<=E<=42,
       2016+30E    42<=E<=63,
       1512+38E    63<=E<=84.                    (3)
```

Each of the five row bounds is sharp even after imposing all seven
row equations CL=16J-8L. Explicit integer row controls are recorded in the
JSON. They are not claimed to fit together into a symmetric C or a graph.

Equivalently, for Z=C0-C, delta_F=4-e_F and tau=sum delta_F,

```
tr(Z^2) >= sum_F h(delta_F),
h(0),...,h(4) = 0,10,28,58,100,
tr(28Z-Z^2) <= 56tau - sum_F h(delta_F).
```

These are universal necessary inequalities, but are elementary consequences
of integer compression entries and their exact row sums. They must not be
counted as extra independent constraints when those entries are already
explicit in a model.

## Averaging loses a mandatory covariance term

Let H=L(L^T L)^(-1)L^T and Pi=I-H. Averaging a fixed C over the support
permutation group S7 gives

```
Cbar=(8/3)J-8H+(E/7)Pi,
tr(Cbar^2)=2688+2E^2/7,
||C-Cbar||_F^2=tr(C^2)-2688-2E^2/7
             >= b(E)-2688-2E^2/7.              (4)
```

The equal/overlap/disjoint entries of Cbar are respectively
2E/21, 8/5-2E/105, and 16/5+E/105. The Frobenius identity follows because
C has the same fixed col-L block as Cbar and its cycle block has trace 2E.

In particular at E=0 every integral compression must satisfy

```
tr(C^2)>=2772,       ||C-Cbar||_F^2>=84,
```

whereas the averaged matrix alone has square trace 2688. Thus a feasible
averaged degree-row moment model is missing at least this much compression
covariance. This does not invalidate its status as a relaxation control;
it specifies one limitation of that control.

For every integer E from 0 through 84 the lower bound (3) is at most the
spectral upper bound (1). These two scalar inequalities therefore exclude
no E layer. No simultaneous matrix realization is inferred from their
overlap. A useful further inequality would have to restrict the covariance
or couple the exact entries across fibres/roots; repeating the averaged
second-moment calculation alone does not do so.
