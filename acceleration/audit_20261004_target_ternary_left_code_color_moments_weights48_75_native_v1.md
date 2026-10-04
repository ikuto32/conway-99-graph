# Independent written audit: target ternary left-code populations 24..51

Claim: C-UNRESTRICTED-TARGET-TERNARY-LEFT-CODE-COLOR-MOMENTS-WEIGHTS48-75,
revision 1. Discovery and mathematical producer: /root/structural. Independent
written verifier: /root/native_driver. The exact paper is
docs/CANDIDATE_20261004_TARGET_TERNARY_LEFT_CODE_COLOR_MOMENTS_WEIGHTS48_75_V1.md,
SHA256 1e3c651af04fe2c0986a168eff8df74a97e7778cb72f6460520aefbf98ebc0d7.
The exact raw candidate is
acceleration/results/20261004_target_ternary_left_code_color_moments_weights48_75_candidate01.json,
SHA256 74ee86ea15776413044dfabd4c998185b8ca68c8a03b07daabde6578b34e06c4.

Outcome: PASS for the precise universal conditional statement in that raw
candidate. I independently reconstructed the moment system, all seven
integer cases and the last pointwise obstruction, and tried the boundary
controls below. This is a written derivation. There was no mathematical
program, imported source, AST extraction, solver, numerical enumeration,
formal proof checker, external review or scientific worker. Candidate and
prior-result bytes remain unchanged. No ledger, index, Git or registration
operation is part of this review.

## Exact hypothesis and inherited revision

The domain is a complete simple SRG(99,14,1,2) and its complete incidence N
of all 231 actual triangles, once each. It is not an arbitrary regular
triangle graph, a fixed induced 17-point graph or a partial incidence matrix.
The necessary integer identity is A^2=12I-A+2J, with Aj=14j.

The exact prior logical result is
C-UNRESTRICTED-TARGET-TERNARY-LEFT-CODE-DOT-FORM-WEIGHTS42-78, revision 1.
Its independently written Checkpoint report
4bb906fbaa8ffc924047f636f56fcba310e61d542cf2a2975484dd957f88ed7f and
canonical binding 0caaf5c3c022362d70ec47a766f9e9f2b9abd672e1ae8bda4dc28d0821fbb3e5
establish positive color populations divisible by 3 between 21 and 57 for
every nonconstant word. I inherit that exact statement, including its
complete-target hypotheses; I do not reapprove its divided-form proof here.

For transparency, the local combinatorial ingredients can also be checked
directly. A triple over F3 has sum zero exactly when all its colors agree
or all three differ. Since lambda=1, each edge is in one actual triangle
and the fourteen neighbors of a vertex are partitioned into seven pairs.
Since mu=2, the graph is connected. A nonconstant two-color word would
make every triangle and every edge monochromatic, contradicting this
connectedness. Thus all three classes of a nonconstant word are positive.
The prior ordinary self-orthogonality and j in L imply the population
congruences: n1+2n2=0 and n1+n2=0 modulo 3 give n1=n2=0, and then n0=0.
Constants are outside the positive-class argument and remain allowed.

Root requested a strengthening of the older result, and Structural authored
the new discovery. I read those arguments but reconstructed the arithmetic
and walk counts independently. Agent agreement is not used as proof.

## Independent moment and spectral calculation

Call the three classes V_i, of sizes s_i, and let t count rainbow triangles.
For v in V_i let r_v be the number of its rainbow triangles. Its neighbor
counts in the three classes are 14-2r_v in V_i and r_v in each other class,
with integer 0<=r_v<=7. Each rainbow triangle meets every class once, so

    sum_(v in V_i) r_v=t,
    edges(V_i,V_j)=t,
    monochromatic triangles in V_i=(7s_i-t)/3.

The last equality and the population divisibility give t divisible by 3.
Also t<=7 min(s_i). None of these identities assumes equitability.

Put Z_i=sum_(v in V_i) r_v^2. For distinct i,j,k, the scalar product
(A chi_i)^T(A chi_j) has contributions 14t-2Z_i, 14t-2Z_j and Z_k
on the three classes. Conversely the integer target equation gives

    chi_i^T A^2 chi_j=2s_i s_j-t.

Consequently

    -2Z_i-2Z_j+Z_k=2s_i s_j-29t.

Summing all three cross equations gives
Z_total=29t-(2/3)Q, where Q=s_0s_1+s_0s_2+s_1s_2.
The complementary equation for Z_i is 3Z_i-2Z_total=2s_js_k-29t.
Solving it gives the exact rational identity

    Z_i=(29t+2s_js_k)/3-(4/9)Q.                 (A)

This solves the full three-equation system without numerical inversion.

For an s-entry integer sequence with total t, write t=qs+u, 0<=u<s.
If two entries differ by at least 2, moving one unit from the larger to the
smaller lowers the square sum by a positive even integer. Iteration leaves
only q and q+1, proving

    Z >= s q^2+u(2q+1),                        (B)
    Z <= 7t.                                  (C)

Equality in (B) requires exactly u entries q+1 and s-u entries q.
The upper bound (C) uses r^2<=7r pointwise and is necessary but generally
not the sharp concentrated square maximum.

The indicator spectral bound can be reconstructed separately. On j-perp
the symmetric adjacency has eigenvalues among 3 and -4, since its
polynomial is A^2+A-12I=0 there. For z=chi_i-(s_i/99)j,

    14s_i-2t-14s_i^2/99 <= 3(s_i-s_i^2/99),

hence

    t >= s_i(99-s_i)/18.                       (D)

No floating eigenvalue or rounding is used.

## Complete seven-case check, without numerical enumeration

Sort the populations a<=b<=c. The prior revision gives a>=21 with all
populations multiples of 3. To exclude the last old boundary, suppose a=21.
Then b+c=78 and 21<=b<=c, so the complete list of b is

    21,24,27,30,33,36,39.

In every row t<=147. Applying (D) to c gives raw lower bounds
133,135,136,136,135,133,130 respectively. The least multiples of 3 above
them are 135,135,138,138,135,135,132. It is legitimate to use just the
c-class bound: it is necessary even where another class gives a stronger
condition.

All surviving t lie between 132 and 147. For the 21-entry lower envelope,

    Z_A >= 13t-882.

The formula holds through t=147; at that endpoint the q=7 expression
agrees with the q=6 linear expression. Since Q=1638+bc, equation (A) gives

    Z_A=29t/3-D_A,  D_A=728-2bc/9.

Combining the two inequalities gives t<=3(882-D_A)/10. The complete
hand table includes the unrounded quantities so the rounding is auditable.

|b,c|raw c-Rayleigh lower|least 3-multiple|D_A|raw A-envelope upper|greatest 3-multiple|
|---|---:|---:|---:|---:|---:|
|21,57|133|135|462|126|126|
|24,54|135|135|440|663/5|132|
|27,51|136|138|422|138|138|
|30,48|136|138|408|711/5|141|
|33,45|135|135|398|726/5|144|
|36,42|133|135|392|147|147|
|39,39|130|132|390|738/5|147|

The first two rows have disjoint intervals. For the other five rows I
reconstructed the additional envelopes on their admitted t intervals:

* 27,51: Q=3015, so Z_C=29t/3-962. The 51-class q=2 lower bound is
  5t-306. Thus (14/3)t>=656, or t>=984/7, whose least 3-multiple is
  141. This exceeds the admitted upper 138.
* 30,48: Q=3078, so Z_B=29t/3-696. The 30-class q=4 bound is
  9t-600. Thus (2/3)t>=96, or t>=144, exceeding the admitted upper 141.
* 33,45: Q=3123, so Z_B=29t/3-758. The 33-class q=4 bound is
  9t-660. Thus (2/3)t>=98, or t>=147, exceeding the admitted upper 144.
* 36,42: Q=3150, so Z_C=29t/3-896. The 42-class q=3 bound is
  7t-504. Thus (8/3)t>=392, or t>=147. Only t=147 remains.
* 39,39: Q=3159, so Z_B=29t/3-858. The 39-class q=3 bound is
  7t-468. Thus (8/3)t>=390, or t>=585/4, forcing the 3-multiple t>=147.
  But Z_A<=7t gives (8/3)t<=390, so t<=585/4 and the 3-multiple
  t<=144. This interval is empty.

The listed q ranges hold on every admitted t interval, not only the final
selected values. In particular the 30/33 lower bounds use q=4, the 42/39
bounds use q=3, and the 51 bound uses q=2. No omitted b value or
approximate threshold is hidden in the table.

## Pointwise contradiction at the sole scalar boundary

Only a=21,b=36,c=42,t=147 survives the scalar reductions. Equation (A)
gives Z_A=1029,Z_B=609,Z_C=525. Since 21 entries at most 7 sum to 147,
every A-vertex has r=7 and has zero A-neighbors. The 42-class square
minimum at total 147 is 7*147-504=525. Its equality forces exactly
21 C-vertices with r=3 and 21 with r=4.

Take an arbitrary vertex v of B, and put r=r_v. Define R_B and R_C to
be the sums of r_w over its neighbors in B and C. There are r neighbors
of v in A, r in C and 14-2r in B.

Count walks from v to A by their middle vertex. An A-middle vertex
contributes zero A-neighbors; B and C middle vertices contribute R_B
and R_C. Exact common-neighbor counts, summed over all 21 vertices of
A, therefore give

    R_B+R_C=1*r+2*(21-r)=42-r.                 (E)

Count walks from v to C. Its A-neighbors each contribute 7 C-neighbors,
its B-neighbors contribute R_B, and its C-neighbors contribute their
own-color degrees, giving 14r-2R_C. Exact common-neighbor totals give

    7r+R_B+14r-2R_C=1*r+2*(42-r)=84-r.        (F)

There is no diagonal return term in either count: v lies in B, not A or C.
Subtracting (E) from (F) yields 21r-3R_C=42 and

    R_C=7r-14.

Each C-neighbor has r_w=3 or 4, so 3r<=R_C<=4r. Thus
4r>=14 and 3r<=14, that is 7/2<=r<=14/3. The sole integer is r=4.
The argument applied to an arbitrary B-vertex, so all 36 have r=4 and
their rainbow total is 144, contradicting the required total 147.

This derived common profile at one rejected boundary is not a prior
equitable-partition, graph automorphism or constant-profile assumption.

## Weight conclusion and hand falsification attempts

All a=21 cases are rejected. The prior divisibility now forces the minimum
population at least 24; each population is consequently at most 99-48=51.
For the class carrying color zero, wt(x)=99-s_0. Thus the exact allowed
nonconstant weights are 48,51,54,57,60,63,66,69,72,75.
The constant words keep weights 0,99,99. The argument does not require,
construct or force any nonconstant word.

I explicitly checked the following boundaries:

1. The scalar survivor is not incorrectly called scalar-infeasible. At
   (21,36,42),t=147, take A:21 entries 7; B:one 7 and 35 entries 4;
   C:21 entries 3 and 21 entries 4. Their totals are all 147 and
   squares 1029,609,525. Monochromatic counts are 0,35,49; together
   with 147 rainbow triangles they total 231. These necessary scalar
   data pass; equations (E),(F) are essential to their graph contradiction.
2. A damaged walk derivation using r_w rather than 14-2r_w for the
   C-middle vertices fails the actual own-color degree identity.
   Replacing 84-r by 84 or 84-2r likewise fails the separate adjacent
   and nonadjacent endpoint count. Adding a diagonal return term here
   is invalid because v is outside both endpoint classes.
3. At (33,33,33),t=132, eleven entries each 3,4,5 give total 132 and
   square sum 550 per class. Q=3267, so (A) gives
   1276+726-1452=550. The monochromatic totals are 33,33,33 and
   the largest-class Rayleigh bound is 121. This remains scalar-possible.
4. At (24,24,51),t=141, each 24-class can have 17 entries 6,
   5 entries 5 and 2 entries 7, giving sum 141 and square sum 835.
   The 51-class can have 35 entries 3,14 entries 2 and 2 entries 4,
   giving sum 141 and square sum 403. Q=3024 and 29t/3=1363, so
   (A) gives 1363+816-1344=835 and 1363+384-1344=403.
   The monochromatic totals 9,9,72 plus 141 give 231, and the
   largest-class Rayleigh bound is 136. This demonstrates that the
   stated scalar argument does not lower the endpoint 51; it does
   not claim an actual target graph or left word exists there.
5. Rook(9,4,1,2) colored by rows is a genuine different-parameter
   nonconstant left word. Its three row triangles are monochromatic
   and three column triangles are rainbow; every r=1. Its classes
   have size 3 and word weight 6. Its degree is 4 with two incident
   triangles, so it defeats parameter-free transfer of the new
   numeric interval and does not defeat the target-specific theorem.
6. Constants have two empty classes and fail the positive-class
   premise. They are retained, including the possibility L=span(j).
7. The integer square envelope and multiple-of-3 roundings cannot be
   imposed on arbitrary real class data. Neither an approximate
   moment fit nor a partial incidence supplies the stated hypotheses.

As an incidental hand check of the optional, unexecuted follow-up only,
divide potential sorted populations by 3. They are sorted integers
8<=x<=y<=z<=17 with sum 33. For x=8,9,10,11 respectively there are
5,4,2,1 pairs (y,z), hence twelve population triples. The possible
multiple-of-3 t labels from 0 through 7a number 7x+1 per triple,
giving 5*57+4*64+2*71+78=761. No scalar screen was run or approved.

## Archive overlap and actual verification limits

The complete October3 design45c27 was read; it already contains the
moment equalities and sharper integer square envelopes. The prior
dot/weight paper and complete Checkpoint written audit/report/binding
establish the exact 42..78 dependency. Their bytes and that claim ID
are preserved. Relevant passages of Wave174 and Wave191 were read:
Wave174 begins with a prism-free endpoint and a weight-three block-dual
premise; Wave191 uses an additional centered-rank11 endpoint. Neither
is imposed here. This bounded comparison provides no exhaustive archive
or external novelty assertion and promotes no historical program status.

The actual review is 36 written boundaries itemized in the report,
including all seven cases separately, the two pointwise equations and
the surviving and deliberately damaged controls. There were zero new
mathematical commands, numerical enumerations, imported algorithms,
formal checks, external checks or scientific artifact replays.
Small source/document reads and SHA256 identity checks are metadata
operations, not an executed color enumeration.

No material mathematical veto was found for the exact revision 1
statement. Recommended VERIFIED/CLEAR applies only to this conditional
written theorem. Target resolution remains NONE, extra left-word
existence remains unproved, no incidence-rank improvement follows, and
registration and any executable continuation remain separate.

