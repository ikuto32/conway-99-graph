# Independent written audit of the minority-sign circuit Gram bounds

The complete reviewed paper is `docs/CANDIDATE_20261004_TARGET_TERNARY_CIRCUIT_MINORITY_SIGN_GRAM_BOUNDS_V1.md`, SHA256 `7afdf20ef3eebc24b7d78bf965b2152bd2e45c75b695c42be03661f8d5971f53`. Structural is the discovery producer. Native independently reconstructs the argument and exact boundary table below. Root did not produce the sign-mass deduction. The historical Gram identity is a shared independently checked premise; the method is not claimed to be novel.

No mathematical command, symbolic or numerical program, enumeration, incidence decoder, solver, formal-proof checker, or external review was used. All arithmetic below was reconstructed by hand. This audit does not identify or construct a target or approve future computational sources.

## Hypotheses and the two support bounds

Assume a complete finite simple99-vertex degree14 graph A with adjacent common-neighbor count1 and nonadjacent count2. Select w distinct actual triangles whose incidence columns form a circuit over GF(3). Its nonzero dependence has coefficients in {+1,-1}. Reverse all signs if needed, and let q be the smaller population. Thus w>=2q, q>=0, and unbalancedness means w-2q is not divisible by3. No bound q<=3 is a premise or a conclusion.

Let S be all n points used by those triangles. Circuit minimality implies that any w-1 columns are independent and all w are dependent; the selected incidence matrix C has GF(3) rank exactly w-1. Each column sums to3=0 over GF(3). The nonzero all-one row on S therefore annihilates C, giving rank(C)<=n-1 and hence n>=w. This step is not available for an arbitrary nonminimal dependent word. No real-rank or binary-rank bound is substituted for GF(3) circuit rank.

At a used point v let d_v be its number of selected triangles and m_v its number of minority triangles. A point with d_v=1 contradicts the nonzero local dependence. If d_v=2, its two signs must be opposite, so m_v=1. For d_v>=3, d_v+m_v>=3 without further restrictions. Summing these exact local inequalities yields 3n<=3w+3q, so n<=w+q.

If n=w+q, every local inequality is equality. The only possibilities are (d_v,m_v)=(2,1) and (3,0). The total minority incidence count3q then gives exactly3q degree-two points and n-3q degree-three points. Each minority triangle uses only these degree-two points, each of which lies on exactly one minority triangle; the minority triangles are point-disjoint. With q=0, n=w follows and every used point has selected degree3. A generic one-sign dependent word could instead have degree6 points, which is why circuit minimality must remain explicit.

## Full Gram mass and genuine induced extra edges

An edge of the target lies on exactly one actual triangle because its common-neighbor count is1. The w distinct selected triangles thus contribute3w distinct edges. The actual induced graph H=A[S,S] has 3w+e edges for a nonnegative integer e; no selected-union inducedness is assumed. If a_v is the number of extra induced edge incidences at v, deg_H(v)=2d_v+a_v and the sum of a_v is2e.

The exact target identity is A squared =12I-A+2J. Degree14 gives AJ=JA=14J and J squared =99J. Expanding G=27I-9A+J gives G squared =1701I-567A+63J=63G. Symmetry implies ||Gx|| squared =63 x transpose G x for every real x, and x transpose G x>=0. This is the preserved historical Gram premise, independently read and reconstructed here.

For x equal to the full99-vector indicating S,

    F = x transpose G x = n squared +27n-54w-18e,
    (Gx)_v = n+27-9deg_H(v), for v in S.

Consequently F>=0 and the inside sum of these squared coordinates is at most63F. The latter is an inequality because outside coordinates were omitted, not an assertion that they vanish. Extra edges lower F by18 each but change the inside squared norm in either direction; monotonic norm reduction is not assumed.

Since n squared +27n is increasing on nonnegative n, n<=w+q and e>=0 imply the necessary coarse polynomial

    P_q(w) = w squared +(2q-27)w+q squared +27q >=0.

## Exact low-q polynomial intervals and balance exclusions

The endpoint calculations, with convexity placing every intervening value at most the larger negative endpoint, are:

| q | Definition lower bound | Excluded integer interval | Polynomial | Endpoint values |
|---|---|---|---|---|
| 0 | w>=1 | 1..26 | w(w-27) | factorization is negative throughout |
| 1 | w>=2 | 2..23 | w squared -25w+28 | P(2)=-18, P(23)=-18 |
| 2 | w>=4 | 4..20 | w squared -23w+58 | P(4)=-18, P(20)=-2 |
| 3 | w>=6 | 7..14 | w squared -21w+90 | P(7)=-8, P(14)=-8 |

For q=3,w=6 the sign sum is0. The further balanced boundary weights are (q,w)=(0,27),(2,22),(3,15),(3,18), since w-2q is respectively27,18,9,12. They are outside the unbalanced hypothesis, regardless of their Gram budgets.

The remaining small unbalanced boundaries require the following exact inside-norm tests. In every row the negative value at n_max-1 and monotonicity force n=n_max=w+q; e>=0 can only make smaller n worse.

| (q,w) | n_max | F(n_max,0) | F(n_max-1,0) | Degree2/degree3 points | Baseline coordinates | Inside norm | 63F |
|---|---|---|---|---|---|---|---|
| (1,24) | 25 | 625+675-1296=4 | 576+648-1296=-72 | 3,22 | 16,-2 | 3*256+22*4=856 | 252 |
| (2,21) | 23 | 529+621-1134=16 | 484+594-1134=-56 | 6,17 | 14,-4 | 6*196+17*16=1448 | 1008 |
| (3,16) | 19 | 361+513-864=10 | 324+486-864=-54 | 9,10 | 10,-8 | 9*100+10*64=1540 | 630 |
| (3,17) | 20 | 400+540-918=22 | 361+513-918=-44 | 9,11 | 11,-7 | 9*121+11*49=1628 | 1386 |

The first three rows have F<18, so e=0 is the only possible nonnegative extra-edge count; their inside norms exceed63F. In the last row e is0 or1. Zero is already impossible. With e=1, an endpoint on a degree-two point changes 11 to2, a square change of-117; an endpoint on a degree-three point changes-7 to-16, a square change of207. Even relaxing all geometry and allowing two degree-two endpoints gives a minimum inside norm1628-234=1394, exceeding63*(22-18)=252. This excludes every possible extra edge without assuming that the relaxed minimizing endpoint pair exists.

The intervals, four inside-budget tests, and balanced weights together prove precisely the necessary thresholds q=0:w>=28, q=1:w>=25, q=2:w>=23, q=3:w>=19. The next weights are not proved feasible, excluded, or sharp. Nothing forces an arbitrary target's unbalanced circuit to have q in this table.

## Independent reconstruction of the q=1,w=25 survivor boundary

At n=25,e=0, F=625+675-1350=-50, so n=26 is forced. At n=26,e=0, F=676+702-1350=28; thus e is0 or1. Equality n=w+q gives three selected-degree2 points, exactly the three vertices of the sole minority triangle, and23 selected-degree3 points. The baseline H degrees are4 and6, with Gx coordinates17 and-1. The inside norm is3*289+23=890.

All three degree-two points are already pairwise joined by the minority triangle, so an extra edge cannot use two of them. A degree-two endpoint has square change64-289=-225; a degree-three endpoint has square change100-1=99. The only endpoint classes for a new extra edge give norm764 or1088, each greater than63*(28-18)=630. Thus e=1 is impossible. The actual induced H is exactly the selected edge union, with75 edges, three degree4 points and23 degree6 points. This conclusion uses the actual minority triangle at this boundary and is not an inducedness assumption for the general theorem.

There are99-26=73 outside points. Their adjacency counts k into S have sum14*26-2*75=214. To independently reconstruct the second moment, use the projector identity rather than the paper's pair-count derivation. The full norm is63*28=1764 and the inside norm is890, leaving outside norm874. An outside coordinate is26-9k. Hence

    874 = sum (26-9k) squared
        = 73*676-468*214+81 sum k squared
        = -50804+81 sum k squared.

Thus81 sum k squared=51678, giving sum k squared=638. This agrees with the separate inside-pair count: total target common-neighbor incidence on S pairs is26*25-75=575, inside contribution is3*choose(4,2)+23*choose(6,2)=18+345=363, leaving212 outside pair incidences and638=2*212+214.

An abstract histogram with eight k=2 points,62 k=3 points and three k=4 points has population73, first moment16+186+12=214, second moment32+558+48=638, and outside Gram norm8*64+62*1+3*100=874. Therefore these scalar moments and this norm alone do not refute the boundary. The histogram supplies no exterior types, adjacency, circuit geometry, or target realization.

## Falsification outcome and retained limitations

The exact conditional statement survives this different-author written reconstruction. Its field rank, point/sign count, extra-edge signs, four q thresholds, and q=1,w=25 moments are consistent under the stated hypotheses. The review specifically rejects broadening circuit rank to a general dependent word, inferring one-signness or q<=3, omitting real extra edges, equating inside and full norms, treating the surviving histogram as a graph, or using any withdrawn real/binary/incidence rank bound. No affine existence or upper98 theorem is needed as a premise; the theorem remains conditional on the selected unbalanced circuit.

The input Gram report and its historical controls establish their previously stated scope; those controls were not rerun and do not qualify a new computational driver. Native's audit is an independent written derivation with shared historical Gram provenance, zero formal or external checking, and no novelty or unrestricted target-resolution claim.
