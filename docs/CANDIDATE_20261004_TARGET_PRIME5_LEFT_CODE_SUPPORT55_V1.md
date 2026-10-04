# Candidate: prime-five left-code support at least 55

This is a separate source-only written refinement of the frozen support54
candidate. Both prior support54 files remain unchanged. Every calculation below
is symbolic or a displayed finite hand table; no program or target input was
executed. Different-author review is required.

## Exact statement and boundary

For every complete finite simple SRG(99,14,1,2), let N be the99x231 binary
ordinary integer incidence matrix of all actual triangles, one column each.
Every nonzero x in ker(N^T mod5) has Hamming weight at least55.
This does not force a nonzero left word, lower the rank of N, construct a target,
exclude the target, or assume an automorphism or equitable color profile.

The argument is exact-target-specific: NN^T=H=A+7I is positive definite with
eigenvalues21,10^54,3^44. It is not applicable to a formal3-adic matrix, a bare
fixed17 count witness, or the singular incidence Gram of the rook9 graph.

## Common exact identities and the previously frozen first bound

The target has A^2=12I-A+2J, Aj=14j, Nq=7j and N^Tj=3q.
For an integer centered lift X with coordinates0,+/-1,+/-2, write its support
size s=p+q2, where p counts magnitude1 and q2 counts magnitude2. In the rest
of this note q2 is written q; the all-ones triangle vector is not used again.
Let X' be the centered lift of2x: magnitude1 becomes magnitude2 and conversely.
Every triangle sum is0,+/-5, and no triangle has exactly one support point.
The fully supported types are +/-(1,2,2) and +/-(1,1,-2). Multiplication by2
interchanges winding and zero-sum types. If t,t' count the respective winding
triangles and m3 counts fully supported triangles, then t+t'=m3.

The least Gram eigenvalue gives25t>=3(p+4q), and the same inequality for X'
gives25m3>=15s. If e is the induced support edge count, triangle incidence gives
2e=7s+3m3. The nonprincipal upper eigenvalue3 of A gives27m3<=s(s-36).
Thus s>=53. At s=53 the bounds and parity force m3=33 and e=235.
For Q=27I-9A+J, Qj=0 and Q^2=63Q. Writing Q chi=9a-j for the support
indicator chi gives sum(a)=11 and sum(a^2)=9, impossible for integer a.
This rederives the frozen support54 result; it is not silently strengthened
in its historical files.

## Divisibility and the stronger mean/residue conditions

For centered integer lifts X,Y of any two F5 left words, N^T X and N^T Y are
5-divisible. Hence X^T H Y and X^T H^2 Y are25-divisible. Also7 sum(X)
is5-divisible, so sum(X) and sum(Y) are5-divisible. The ordinary identity

    H^2-13H+30I-2J=0

implies25 divides30 X^T Y, whence5 divides X^T Y. In particular
p+4q=0 mod5. At s=54 this says q=2 mod5.

Put S=sum(X)=5k and S'=sum(X')=5l. The least-eigenvalue bound with the
principal direction retained is

    E :=25t-3(p+4q) >= (2/11)S^2,
    E':=25t'-3(4p+q) >= (2/11)S'^2.

Here E=X^T(A+4I)X. The identity (A+4I)^2=7(A+4I)+2J gives
||Y||^2=7E+2S^2 for Y=(A+4I)X. Since HX is5-divisible, Y=X'+5v
for an ordinary integer vector v, with sum(v)=18k-l. Similarly
Y'=(A+4I)X'=-X+5v' and sum(v')=18l+k.

For every integer v_i and m_i in{-2,-1,0,1,2},

    (m_i+5v_i)^2-m_i^2 >=5|v_i|.

Thus the residue-minimum differences are nonnegative multiples of5 and obey

    7E+50k^2-(4p+q) >=5|18k-l|,
    7E'+50l^2-(p+4q) >=5|18l+k|.

This inequality uses actual integer coordinates; a floating spectral energy
or unrestricted local-ring lift cannot replace it.

## Weight54 with m3=36

At s=54 the first two support bounds and parity permit only m3=34 or36.
For m3=36, chi^T Q chi=0; Q is positive semidefinite, so Q chi=0.
Consequently every support point has9 support neighbors and every outside
point has6. This equitable support partition is a conclusion, not a premise.

Every support point then lies in exactly2 fully supported triangles and5
two-support triangles. Each two-support triangle joins opposite centered
values of the same magnitude. The corresponding5-regular bipartite pair
graphs force equal +1/-1 populations and equal +2/-2 populations. Thus p,q
are even and S=S'=0. Full-triangle magnitude2 incidence gives2q=36+t,
so t=2q-36. Both E,E'>=0 give q,p>=26, leaving q=26 or28. Choose the
scalar orientation with q=26 and p=28. Then t=16 and E=4, hence
||(A+4I)X||^2=28. But its mod5 residues are those of X', whose minimum
possible integer squared norm is4p+q=138. This contradiction excludes m3=36.

## Weight54 with m3=34: complete mean table

Now t'=34-t and E+E'=25*34-15*54=40. The mean inequality gives
k^2+l^2<=8. Since S has parity p and S' has parity q, and p+q=54,
k+l is even. Therefore the following table covers all possible means.

|Mean magnitudes|Cases, up to scalar rotation and negation|Reason excluded|
|---|---|---|
|0,0|(k,l)=(0,0)|Residue slack table below; q must be2 mod5|
|1,1|Both choices of relative sign|Summed residue lower bound180 exceeds110|
|2,2|Both choices of relative sign|E=E'=20 conflicts with winding counts|
|2,0|(k,l)=(2,0)|Three energy cases below|

There are no other integer pairs with k^2+l^2<=8 and k+l even. The scalar2
operation sends(k,l) to(l,-k), and negation sends it to(-k,-l). These are
word scalar operations, not assumptions about graph automorphisms.

For magnitudes1,1, the sum of the two residue lower bounds is180; their
available total is10+50(k^2+l^2)=110, a contradiction.

For magnitudes2,2, each energy is at least200/11 and is a multiple of5,
forcing E=E'=20. Each winding signed count is7k or7l, so14<=t<=20.
The exact relation20=25t-162-9q, with q even, instead gives(q,t)=(2,8)
or(52,26); q=27 is odd. Neither is in that winding interval.

For zero means, q,p,t are even. Write

    u=(7E-(4p+q))/5=35t-270-12q.

The companion nonnegative integer u' satisfies u+u'=2. Since u is even,
u=0 or2. The complete small congruence table is

|u|35(t/2)-12(q/2)|Only solution with0<=t<=34,0<=q<=54|
|---|---|---|
|0|135|(q,t)=(30,18)|
|2|136|(q,t)=(24,16)|

Both contradict q=2 mod5. This excludes the zero means without an equitable
profile assumption.

Finally normalize the remaining means to(k,l)=(2,0). If a,b count +1,-1
and c,d count +2,-2, then a-b=k+2l=2 and c-d=2k-l=4.
Thus q>=4 and q is even. Winding signed count7k=14 gives t>=14.
Divisibility gives5|E and parity gives2|E; the mean inequality gives E>=20.
Since E<=40, only the following energies remain:

|E|Exact possible even q and t|Contradiction|
|---|---|---|
|20|(2,8) or(52,26)|q=2 violates c-d=4; q=52 leaves p=2 but requires42 full-triangle magnitude1 incidences, exceeding7p=14|
|30|(12,12)|t<14|
|40|(22,16)|E'=0 and S'=0 would give Y'=0, contradicting Y'=-X mod5|

The42 incidences in the first row are t+2t'=26+16. This count only uses
the7 actual triangles through each of the two magnitude1 support points.
All weight54 cases are excluded. Together with the unchanged first bound,
every nonzero prime-five left word therefore has support at least55.

## Provenance, overlap and unmet requirements

Root suggested retaining the principal mean term after the support54 freeze.
Structural derived the integer-residue slack inequality and the displayed
complete weight54 table. The historical Gram identities/projector and the
support54 argument are explicit shared ancestry. No rank improvement, exact
word population census, target realization or forced nonzero L5 follows.

Bounded prior comparison is the same named modular/Wave23/Wave168/mod9/
3-adic comparison as the frozen54 note. This is not exhaustive novelty
verification. The smaller rook9 example still marks the target-specific
boundary. Different-author written proof/table/typing and Root scope review
remain unmet; there is no executable proposal, ledger or Git change.
