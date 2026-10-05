# Ternary incidence dependency: paper-only candidate continuation

Prepared by `/root/structural` at 2026-10-02T23:57:44.9742944Z, against
source context `16be41cee26421941eaecb615b64bd21095c5765`. This is a
candidate design and derivation, without an executable experiment,
independent mathematical approval, ledger change, or novelty claim.

## What has already been tried

For a hypothetical unrestricted target let B be the complete 99-by231
point/triangle incidence matrix, with each actual triangle included once.
The integer identity BB^T=7I+A is an essential premise.

The ternary ranks rank(A)=45 and rank(A+I)=55 are already documented in
`docs/DERIVATION_20260930_GF3_HOLLOW_RESIDUAL.md` (SHA256
`f8e52a669ed012a4d79e951e4ee52ea60d4d556ff16db893ff8e0508017f59ba`).
They are not new discoveries from this note. The pinned archive at
`https://github.com/YesterdaysLemon/conway-99-research`, commit
`85e705cc6c2a14d123120c93a847e30aaab1789e`, also gives the bounds
55<=rank_F3(B)<=98 in
`attempts/wave170-block-profile-ternary-code/derivation.md` (SHA256
`67c293ccdff944aeb59b44ad297b7db876a0ceb9df50c876f559cb63ef20123f`).

The archive's Wave171 identifies a nilpotent triangle code with the existing
centered code; its derivation has SHA256
`0ff4280e782acccfb76e2ca093291be3e3a1c4ca08225ccb763b113c5ac286e3`.
Wave191's bounds 66<=rank_F3(B)<=82 and 17<=dim ker(B^T)<=33 use the
additional centered-rank11 endpoint. Its derivation has SHA256
`5bf0758c7a4620364738225f6da1c27b428f82bd10274c9a9d21a015277e30db`.
Those endpoint assumptions cannot be silently imposed on the target.
Historical statuses in these files are provenance, not fresh verification.

## The immediate obstruction to a rank contradiction

In this section all matrices are over GF(3). Put M=A+I and P=M^2.
The target equations give M^2=M-J, MJ=JM=J^2=0. Consequently P is
a symmetric projection of rank54 and M=P+J has rank55. Column sums3
give B^T1=0, whereas row sums7 give B1=1. Thus the constant vertex
vector belongs to both ker(B^T) and im(B).

This forces a ternary dependency but only a one-dimensional constant
dependency. The elementary identities still permit rank_F3(B)=98.
They give no immediate conflict with the separately checked binary lower
bound rank_F2(B)>=87: ranks over different fields cannot be compared by
assuming equality. A forced additional ternary dependency remains UNKNOWN.
The earlier generic binary isotropy rank<=72 argument remains refuted and
is not used here.

A cheap decisive falsifier of an incidence-only extra-dependency argument
would be a ternary rank98 certificate for either already validated
degree14/lambda1 warm graph. Such a certificate should supply98 independent
incidence columns and an exact independently checked minor or left inverse
after deleting one redundant point row. The constant row relation then
establishes that the kernel consists of the three constant colorings.
These graphs fail the full target identity, so this could refute only an
argument using regular actual triangle incidence; it could not refute a
target-specific extra-dependency theorem. No rank calculation is launched.

## A necessary domain if a nonconstant ternary dependency is forced

The following derivation is CANDIDATE pending separate checking. It may
provide a finite prerequisite test for a future genuinely forced dependency.
It does not itself force one.

Let x be a nonconstant vector in ker_F3(B^T), and partition the vertices
by its three values into classes V0,V1,V2 of sizes s0,s1,s2. Every actual
triangle is monochromatic or has all three colors. The target is connected
(each nonedge has two common neighbors), so a nonconstant coloring uses
all three colors: with only two colors, every triangle and hence every edge
would be monochromatic. Therefore each si>0 and s0+s1+s2=99.

Let t count rainbow triangles. For v in Vi let rv be the number of incident
rainbow triangles, and define Zi=sum_(v in Vi) rv^2. Since each point lies
on seven triangles, 0<=rv<=7. Its numbers of neighbors in the three
classes are 14-2rv in its own class and rv in each other class. Thus

* sum_(v in Vi) rv=t for each i;
* every pair of distinct classes has exactly t edges;
* the number of monochromatic triangles in Vi is (7si-t)/3;
* si=t mod3, 0<=t<=7 min(si), and Zi=t mod2.

Write Q=s0s1+s0s2+s1s2. Applying the integer SRG identity to the
three class indicator vectors gives, for distinct i,j,k,

    4Zi+Zj+Zk = 2si^2-198si+58t,
    -2Zi-2Zj+Zk = 2sisj-29t.

For example the second equation follows because the scalar product
of A1_Vi and A1_Vj is 28t-2Zi-2Zj+Zk, while
1_Vi^T A^2 1_Vj=-t+2sisj. Summing the three cross equations yields

    Z0+Z1+Z2 = 29t-(2/3)Q,
    Zi = (29t+2 s_j s_k)/3-(4/9)Q.

All these are exact integer necessary equalities. In addition, for any
class of size s and total t write t=qs+r, 0<=r<s. The minimum possible
sum of squares of s integers in [0,7] with sum t is

    s q^2+r(2q+1).

Writing t=7h+u, 0<=u<7, its maximum is 49h+u^2. These follow by moving
one unit from the larger entry to the smaller to minimize, or concentrating
units to maximize; they do not assert graph realizability. Each displayed
Zi must be integral, congruent to t modulo2, and lie between these two
integer bounds. This gives a small exact potential screen of class sizes
and rainbow counts, without a numerical relaxation or automorphism.

The screen would describe nonconstant line-sum colorings only. If it has
survivors they are necessary parameter data, not realized colorings or
graphs. If it has no survivors it would exclude nonconstant ternary
dependencies, which remains compatible with a target having ternary
rank98. A nonexistence argument would still need an independently checked
reason that a nonconstant dependency must exist.

## Execution and review state

No source producer, solver, enumeration, fixture execution, or rank calculation
is attached. Proposed cheap tests require new exact sources, positive and
corrupted fixtures, contained allocation, and separately authored artifact
checking before any result is promoted. Overall search coverage remains
UNKNOWN; no validated denominator. The unrestricted target remains UNKNOWN.
