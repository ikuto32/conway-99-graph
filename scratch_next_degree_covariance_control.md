# Exact conditional covariance boundary at a sharp E0=0 compression

The full global degree-Gram equation remains feasible at the level of an
explicit rational conditional PSD moment model, even after fixing the
parent's integral sharp compression C, every source mean, own-fibre zero,
the group quotas, and total outgoing square moment64 per source fibre.
This is not an integer D and is not a graph.

The result applies to any symmetric sharp E0=0 compression satisfying the
support equations and tr(C^2)=2772. The stored matrix is one exact instance.
Its covariance control has been checked independently using rational Schur
elimination, with no numerical eigenvalues or producer imports.

## 1. Fixed and cycle parts

Let L be the21-by-7 unsigned incidence of K7 and let

```text
Pi = I-L(5I+J)^(-1)L^T,
Cbar = 48 E1-8 E6,
T = C-Cbar,
G = 48I+32J-C-8LL^T.
```

Pi is the rank14 cycle projector, with diagonal2/3. The equal, overlapping,
and disjoint entries of Cbar are0,8/5,16/5. The fixed support equations give
T Pi=T, while sharpness gives, at every source F,

```text
T_FF=0,  (T^2)_FF=4,  tr(T^2)=84,
sum_G C_FG^2=132.                                    (1)
```

Indeed a sharp row has overlapping entries1 four times and2 six times, and
disjoint entries3 eight times and4 twice. The fixed and cycle parts are
orthogonal row by row; the Cbar row square is128.

For four hypothetical degree rows in source F, put mu_F=C_F/4. If their
centred aggregate covariance is Sigma_F, then the required full Gram is

```text
sum_F Sigma_F = G-C^2/4
              = 48 Pi-T-T^2/4.                       (2)
```

An actual single four-row population has Sigma_F>=0, rank at most3, and
Sigma_F L=0. Because own-fibre degrees vanish, its F coordinate also
vanishes. This rank statement applies before averaging populations.

## 2. A rational positive covariance in every source hyperplane

Define

```text
Delta = (3/2)Pi-T-T^2/4,
u_F = Pi e_F,
Q_F = Pi-(3/2)u_F u_F^T.
```

By (1), Delta has zero diagonal and trace and satisfies Delta Pi=Delta.
Q_F is the rank13 orthogonal projector onto the cycle space with coordinate
F zero. Direct multiplication gives

```text
sum_F Q_F = (39/2)Pi,
sum_F Q_F Delta Q_F = 18 Delta.                       (3)
```

For the second identity, expand the two factors Q_F. The first term is
21 Delta, the two cross terms total-3 Delta, and the final term is zero
because u_F^T Delta u_F=Delta_FF=0.

Now set

```text
Sigma_F = (31/13)Q_F+(1/18)Q_F Delta Q_F.              (4)
```

Every matrix in (4) has own coordinate zero, annihilates L, and has trace31.
Equations (3) give

```text
sum_F Sigma_F = (93/2)Pi+Delta
              = G-C^2/4.                             (5)
```

The source raw second moment therefore has trace
||C_F||^2/4+31=33+31=64. This is a chosen feature of the control, not a
claim that every actual graph must have total outgoing square64 in each
individual fibre. Likewise the full global equation is a moment equality;
it does not supply a simultaneous deterministic D.

Positivity is uniform and has substantial slack. On the cycle space,
||T||_F^2=84 implies T<=10I and T^2<=84I. Hence

```text
Delta >= -(59/2)Pi,
Sigma_F >= (31/13-59/36)Q_F
        = (349/468)Q_F.                              (6)
```

Thus each Sigma_F has rank13. In particular the displayed matrices cannot
be the centred covariance of one actual four-row population, whose rank
is at most3. They are PSD conditional moments.

## 3. The natural four-row incidence Schur bound has automatic slack

The exact binary incidence Gram for a zero-edge source fibre is

```text
K = [12  1  1  2]
    [ 1 12  2  1]
    [ 1  2 12  1]
    [ 2  1  1 12].
```

Let D_F be any real four-row degree matrix with sum C_F, the exact group
quotas, own coordinate zero, and sum of row square norms64. It need not be
an integer or a binary-incidence realization. Its common quota projection
is a=Cbar_F/4, of norm squared8. Writing

```text
D_F = 1 a+V,
```

gives V L=0, tr(VV^T)=32, and for e=1/2 the constant unit vector,
e^T VV^T e=||T_F||^2/4=1. The matrix 4K-8J has eigenvalues
32,40,40,48, with32 on e. For H=4K-8J-7I,

```text
tr(H^(-1) VV^T) <= 1/25+31/33 = 808/825 < 1.
```

Therefore VV^T<H and

```text
4K-D_F D_F^T > 7I.                                  (7)
```

The sharper universal constant from the same calculation is
20-2 sqrt(38). Thus adding just this necessary Schur PSD condition cannot
cut any such degree quartet. All21 previously audited integer quartets
also pass (7) by exact arithmetic.

## 4. A real incidence lift, and why it is still a relaxation

Let P be the80-by-21 target-fibre incidence, with the own-fibre column zero,
and N the14-by-80 target exact label incidence. The balanced real lift
X0=D_F P^T/4 has the required
fibre degrees and exact fourteen-label quotas. The latter follows because
each label occurs twice in its target fibre: the label quota is half its
group quota.

The20 fibre constants and seven group sign-difference vectors are
orthogonal, and the sign vectors have positive squared norms20 on the two
source groups and24 elsewhere. Their orthogonal complement has dimension
80-20-7=53 and is annihilated by both P^T and N. This leaves more than
enough space to factor the positive residual K-D_F D_F^T/4 from (7).
Adding such a factor to X0 yields a real4-by-80 matrix X satisfying

```text
XP=D_F,  XN^T=the exact label quotas,  XX^T=K.         (8)
```

No nonnegativity, upper bound, or binary alphabet is asserted for X.

There is even a finite real-quartet interpretation of (4). Spectrally
decompose Sigma_F=sum_i lambda_i v_i v_i^T, with unit v_i and
sum_i lambda_i=31. Assign probability lambda_i/31 to the quartet

```text
mu_F+w_i, mu_F-w_i, mu_F+w_i, mu_F-w_i,
w_i=(sqrt(31)/2)v_i.
```

Each such quartet has sum C_F, the quotas, own coordinate zero, total
square64, and centred covariance31 v_i v_i^T of rank1. Its expectation is
Sigma_F. Each quartet individually admits the real lift (8). This restores
the four-row rank condition inside the mixture, but still supplies only
averaged global degree moments and unrestricted real entries.

The missing conditions are the simultaneous pointwise global Gram, the
bounded integer degree alphabet, binary incidence, and edge reciprocity.
Consequently none of (4), (7), or (8) proves integral D feasibility,
an E0 lower bound, or existence/nonexistence of the99-vertex graph.

## 5. Files and bounded experiment

```text
scratch_next_degree_covariance_control.py/.json
scratch_next_degree_covariance_control_audit.py/.json
```

The independent checker reconstructs Pi from the incidence inverse, checks
all441 entries of the global Gram, verifies rank13 and (6) by exact Schur
elimination for all21 covariances, checks the real-lift residual dimensions,
and checks (7) on the21 existing degree quartets. It imports no producer
and uses no solver. Its status is
INDEPENDENT_EXACT_CONDITIONAL_COVARIANCE_CONTROL_AUDIT_PASS.

A separate bounded D-only CP-SAT experiment imposed all simultaneous C,
quota, and G constraints, with the extra constructive restrictions D<=2
and each row square16. It ended UNKNOWN after45 seconds with19,488
variables. That result has no exclusion force and was not lengthened:
`scratch_next_degree_gram.py/.json`. No B variables, lower-layer exhaustive
census, submission.txt, or root inventory mutation occurred in this lane.
