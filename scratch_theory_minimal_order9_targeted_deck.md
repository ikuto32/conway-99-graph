# Targeted full deletion deck of the 19 visible order-nine masks

## Result

The 19 masks from `scratch_theory_minimal_order9_mate_lift` were treated as
frozen input.  No order-eight class and no ambient order-nine census was
regenerated.

The full targeted deck gives a sharper boundary than the mate-only lift:

- all (19\cdot9=171) unmarked vertex deletions land in exactly 39 of the
  frozen 916 order-eight classes;
- all 33 feasible labelled mate-bit templates were checked at all nine
  deletion positions: 33 mate deletions and 264 non-mate deletions;
- those 39 shadows touch 196 of the 944 frozen marked-vertex rows and 598 of
  the 4,440 frozen marked-pair rows, and every recomputed coefficient agrees
  exactly with the frozen row;
- no unmarked or vertex-rooted order-8-to-9 extension row closes on the 19
  visible masks;
- exactly 21 ordered-pair-rooted extension rows do close on the 19 masks.
  Eight of these 21 rows use a shadow absent from the mate-deletion list.

Thus non-mate deletion does produce genuine exact relations, but it does not
exclude the Wave163 integral (T=0) point.

## What “closed” means

For a canonical order-eight graph (K) and an ordered rooted-pair orbit
(\tau=(a,b)), let

\[
 q_\tau=(1_{ab\in E}+2\,1_{ab\notin E})
          -|N_K(a)\cap N_K(b)|.
\]

If (m_\tau) is the size of the ordered-pair orbit, the exact extension
identity is

\[
 m_\tau q_\tau x_8[K]
   =\sum_H e_\tau(K,H)x_9[H].
\]

For each rooted shadow in the targeted deck, the producer checks every
possible neighbourhood of the ninth vertex containing (a,b).  There are at
most (2^6=64) such neighbourhoods.  Pair-upper inadmissible choices are
discarded.  A row is called closed precisely when every remaining extension
is isomorphic to one of the 19 frozen masks.  This is a local completion check
for a fixed targeted shadow, not a census of graphs on nine vertices.

The 21 closed rows have 14 distinct coefficient vectors and rank 11 on the 19
unmarked (H_9) columns.  Restricted to the nine all-G columns they have rank
9.  The original 11-by-9 mate-deletion matrix already has rank 9, so adjoining
the new rows increases the all-G rank by zero.

## The eight non-mate-shadow rows

Write (q[M]) for the unmarked count of the visible order-nine mask (M).
The eight rows reduce to five distinct equations (three occur for two ordered
rooted keys):

\[
\begin{aligned}
x_8[110811716]
 &=4q[3669678280]+2q[3985958096]+4q[13904794306]\\
 &\quad+2q[14844285121]+q[16281591873],\\
x_8[116470352]
 &=2q[3985958096]+2q[14874613832]+2q[16260620944]\\
 &\quad+q[16281591873]+2q[16827884176],\\
x_8[148550240]
 &=2q[14337762352]+q[27134186696]+q[27220517280],\\
2x_8[149915713]
 &=2q[10040402400]+4q[13904794306]+2q[27134186696]\\
 &\quad+2q[36949028884]+12q[61357049490],\\
2x_8[189599968]
 &=2q[10040402400]+2q[27220517280]+4q[35795456704]\\
 &\quad+2q[36949028884]+4q[45743280832].
\end{aligned}
\]

These equations are exact: there is no omitted order-nine column in them.
The JSON certificate records all 21 rooted keys and coefficients, including
the 13 closed rows whose shadows also occur in the mate-deletion list.

## Wave163 boundary evaluation

Solving the original 11 mate-deletion rows against the Wave163 integral
order-eight point gives, in the published all-G mask order,

\[
(2335,7119,15108,19217,0,0,1197,762,0).
\]

These values are nonnegative integers.  Substitution into all 21 closed rows
is exact.  Nonnegativity then forces all ten visible mask columns outside the
nine all-G columns to zero.  Together with the three already-zero all-G
columns, the forced-zero visible indices are

\[
0,1,2,3,4,6,7,8,9,11,13,16,18.
\]

The eight non-mate-shadow rows alone force nine of the ten outside-all-G
columns to zero; the remaining mask `3669386708` is killed by a closed row on
a mate shadow.

This is a real zero-cell strengthening, but not a contradiction.  The nine
all-G values still solve the complete closed subsystem.  The open extension
rows have nonnegative integral projected slack.  Simultaneous realization of
all open-row slacks by ambient (H_9) counts is not asserted; proving that
would require the general order-nine layer that this targeted calculation was
designed to avoid.

The closed rows yield no new congruence.  Their only nontrivial modulus is
(x_8[110787152]\equiv0\pmod 2), already present in the mate-deletion lane.

## Role-preserving deletion boundary

The two source triangles and the target triangle partition the nine displayed
vertices.  Deleting the mate is the only deletion that retains both complete
source triangles, both roots, and the marked target edge.  Any other deletion
removes a required role.  Consequently the full original X-X flag closes only
through the 11 mate rows.  The non-mate information above arises after
forgetting down to a marked vertex or ordered pair, where the SRG degree or
common-neighbour capacity supplies a different exact extension identity.

## One-level outside-neighbourhood feasibility

For each of the 19 masks (H), nonnegative integers (n_S),
(S\subseteq V(H)), were constructed satisfying

\[
\sum_S n_S=90,
\qquad
\sum_{S\ni i}n_S=14-d_H(i),
\qquad
\sum_{S\supseteq\{i,j\}}n_S=
  \begin{cases}
  1-c_H(i,j),&ij\in E(H),\\
  2-c_H(i,j),&ij\notin E(H).
  \end{cases}
\]

All 19 systems are integrally feasible.  The certificate contains each full
sparse pattern multiset; the independent audit checked 396 nonzero pattern
entries.  This is exactly a first/second-moment external-neighbourhood test.
It does not complete the graph induced by the 90 external vertices.

## Artifacts and reproduction

- Producer: `scratch_theory_minimal_order9_targeted_deck.py`
- Exact certificate: `scratch_theory_minimal_order9_targeted_deck.json`
- Independent verifier: `scratch_theory_minimal_order9_targeted_deck_audit.py`
- Audit result: `scratch_theory_minimal_order9_targeted_deck_audit.json`

Run:

```text
python scratch_theory_minimal_order9_targeted_deck.py
python scratch_theory_minimal_order9_targeted_deck_audit.py
```

The independent audit imports none of the producer code.  It checked all 171
unmarked deletions, all 297 labelled role deletions, all 5,384 frozen marked
identities at the Wave163 point, all 573 targeted order-8-to-9 rows, exhaustive
local closure of the 21 exact pair rows, and all 19 outside-neighbourhood
witnesses.  No `submission.txt` was created.
