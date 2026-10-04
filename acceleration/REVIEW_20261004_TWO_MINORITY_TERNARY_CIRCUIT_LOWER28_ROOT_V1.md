# Independent written review of the two-minority circuit bound

Producer: `/root/checkpoint_audit`; verifier: `/root`. This checks the exact
revision1 statement in candidate908b557780a41326751acb905884d773228db4be8d49fb488c48889ac1acae63
and paper25cf4c68b70d29346fcbb76dd4cf6ed1e1baa2be359d90e7700c2a2581872c95.
Root suggested investigating this direction after the separate one-minority
argument, but Checkpoint supplied this new proof. The checks below reconstruct
the deductions and attempt to falsify the treatment of extra edges. They are
written exact arithmetic, with no program, solver, formal proof or external
review. The original candidate remains unchanged.

## Incidence and complete case coverage

The integer target identity gives degree14. At every vertex its neighborhood
is seven disjoint edges: an adjacent vertex has exactly one neighbor there.
Thus every point lies on seven actual triangles; distinct actual triangles
share no edge. A point's selected degree is twice its selected incidence.

For minus incidence m=0,1,2, the equation d_plus=m modulo3 and total incidence
at most7 give respectively d=3/6,2/5,4/7. Every selected triangle column has
coordinate sum zero over GF(3). Circuit rank w-1 on n used rows is therefore
at most n-1, giving w<=n. This uses a circuit, rather than an arbitrary kernel
word, and does not require coefficient-sum balance.

Two actual minus triangles are disjoint or share exactly one vertex. For
disjoint triangles, six low B incidences contribute12 rather than18, so
3w=3n-6+3h+3t and n=w+2-h-t, with h+t<=2. For meeting triangles the center
has baseline4 and four peripheral points baseline2: the B sum is12 rather
than15, giving n=w+1-h-t and h+t<=1. Consequently the recorded branches
n=w,w+1,w+2 (disjoint) and n=w,w+1 (meeting) are exhaustive.

In the disjoint case actual edges between the K3s form a matching. A point
adjacent to two points of the other K3 would give their already adjacent pair
a second common neighbor. If c denotes SELECTED cross edges, c<=3. Actual
additional cross edges may exist and are not assumed equal to c. Selected
degrees on B sum to24+6h; subtracting twice(6+c) gives selected BM=12+6h-2c.
Subtracting both B and BM edges from3w gives selected MM=3w-18-6h+c.
An incidence5 point has selected degree10, two neighbors in its own K3 and
at most one across, hence at least seven selected M neighbors. If c=0 it
has eight. Later extra edges cannot remove these existing neighbors.

For meeting triangles, their induced B graph is exactly the bowtie. All
peripheral vertices are neighbors of the center; an edge joining different
peripheral pairs contradicts its neighbor matching. A majority triangle
cannot reuse a bowtie edge or contain a nonexistent B edge, so it meets B
in at most one point. Six required majority incidences give w>=8. In the
baseline branch selected BM=12 and MM=3w-18. Each M point meets at most one
point of each minus K3, thus at most two B points; m=w-4>=6 gives w>=10.
The possible stronger restriction for a center neighbor is not needed.

## The full target norm and its integer outside bound

With G=27I-9A+J, the target identity and AJ=14J yield G squared=63G.
For a set X of m points, F=m squared+27m-18e(X), and the full norm equals
63F. Outside coordinates are m-9k. Since the full graph is degree14,
their integer k lie in0..14 and sum to K=14m-2e(X); there are N=99-m of them.

I expanded the proposed pointwise identity separately:

    (405-18m)k+m squared-486+81(k-2)(k-3)
      =81k squared-18mk+m squared=(m-9k) squared.

The consecutive integer roots2,3 leave no integer with a negative remainder.
It is valid even at k=0,1,4,14, not only at a putative optimal2/3 distribution.
Thus the entire outside norm is at least (405-18m)K+(m squared-486)N.
A particular k>=7 adds at least1620; k>=8 adds at least2430. The remainder
increases thereafter. These are lower bounds, not assertions that a cut
degree distribution can be realized. All B and unused vertices are included.

## Reconstruction of every weight exclusion

For n=w, actual e(S)=3w+E gives F=w(w-27)-18E. Positive possible w<=26 are
excluded by negativity. At27 it forces E=0 and F=0. There are at least four
low degree4 B vertices in the disjoint branch and at least three low peripheral
ones in the meeting branch. Their coordinate54-36=18 contradicts zero norm.

The maximal-support branches have m=w-4 and e(M)=3w-18+d, with d=c+a in
the disjoint case and d=a in the meeting case. Direct expansion gives
F=w squared-35w+232-18d. In the disjoint case12-2c<=2(w-4) gives c>=10-w
and w>=7. At w7, F<=36-54=-18; at w8, F<=16-36=-20. The polynomial has
value-2 at both9 and26; convexity bounds the full intervening interval by
that negative chord. Meeting baseline w>=10 is already in this interval.

At27, F=16-18d forces d=0. Then m23,e63,N76,K196. The independently
reconstructed outside lower bound is -9*196+43*76=1504, exceeding63*16=1008.
This includes every outside coordinate and depends on actual e(M) only.
Adding BM edges does not change m,e(M) or the total cut identity.

For the remaining disjoint branch n=w+1, F_S<=w squared-25w+28. Its values
at5 and23 are-72 and-18, so all5..23 are impossible. The initial w>=5 follows
because every B point needs a majority triangle, each meeting at most two B
points. At24..27, h=0,t=1 gives m=w-5,e(M)=3w-18+d and F=w squared-37w+214-18d.
Its endpoint values-98,-56 exclude that entire interval.

For h=1,t=0, m=w-5,e(M)=3w-24+d,F=w squared-37w+322-18d. I recomputed
the cut and norm table from these formulas, retaining the exceptional point's
1620 remainder:

| w | m,N | K | F | outside lower bound | budget63F | difference |
| --- | --- | --- | --- | --- | --- | --- |
|24|19,80|170-2d|10-18d|2330-126d|630-1134d|1700+1008d|
|25|20,79|178-2d|22-18d|2836-90d|1386-1134d|1450+1044d|
|26|21,78|186-2d|36-18d|3132-54d|2268-1134d|864+1080d|
|27|22,77|194-2d|52-18d|3212-18d|3276-1134d|-64+1116d|

For example the24 base outside value is63*170-125*80=710, then+1620;
the27 base value is9*194-2*77=1592. The first three differences are positive
for every d>=0, and the last is positive for integer d>=1. The remaining
27,d0 implies c=a=0, so the high B point has at least eight selected M
neighbors. Replace1620 by2430:1592+2430=4022>3276. Extra actual BB edges
do not change the absence of SELECTED cross edges or remove selected M
neighbors; extra BM edges can only increase the high-point remainder.

Every case through27 is therefore excluded. The coefficient sum is w-4;
at28 this is24=0 modulo3. An unbalanced circuit consequently has w>=29.

## Verdict and falsification limits

PASS for the exact recorded universal CONDITIONAL statement, including balanced
w>=28 and unbalanced w>=29. No material gap was found. The main falsification
attempts were confusing selected c with all actual BB edges, discarding added
BM edges, omitting unused outside vertices, applying real rather than integer
convexity to k, and applying the circuit rank to a nonminimal dependence.
The reconstructed proof withstands each of those within its explicit scope.

The only pinned claim dependency is the existing target Gram theorem r1.
No two-minority circuit is forced, weight28 is not constructed or classified,
and no circuit upper bound or unrestricted target exclusion follows. The old
lower23 statement remains true. This written review supplies zero mathematical
executions, formal checks or external reviews and changes no ledger status.
