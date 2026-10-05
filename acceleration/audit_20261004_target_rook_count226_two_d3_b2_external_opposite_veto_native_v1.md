# Independent written veto: an external high opposite was omitted

Completed source-only challenge 2026-10-04T21:47:58.6826968+00:00.
Producer /root/structural; independent written reviewer /root/native_driver.
No mathematical program, import, AST, worker, solver, census, formal or
external checker. Historical candidate bytes remain unchanged.

The complete original paper
docs/CANDIDATE_20261004_TARGET_ROOK_COUNT226_MAXD3_TWO_D3_B2_NO_INTERSECTION_V1.md
has SHA988a38515ef867625dd937df6bc475979b3da53b5fa1310a0cb6d13e08d87d50.
Its rawcandidate01 has SHAf1e74751281adfd10e87358e102fbfc05067cc416103751aa31bf36fe7188b36.
The exact proposed r1 ID is
C-UNRESTRICTED-TARGET-ROOK-COUNT226-MAXD3-TWO-D3-B2-NO-INTERSECTION.
The theorem statement itself is not refuted here. Its explicit proof bounds
c_C<=12/c_D<=12 and total162, plus 'no omitted high opposite', are wrong.
Root and Structural received the finding before this receipt; producer
acknowledgment and shared agreement are not the written proof of the veto.

Assuming the paper's valid common-point graph, let A,B be D3 roots and
C,D be D2 roots. The local high edges are AB,AC,AD,BC,BD, with CD absent.
Their degrees are3,3,2,2 at the common point. This is K4 minus CD, not a
nonexistent degree sequence. It contains the single collapsed cycle
A-C-B-D-A, whose four actual point labels all coincide.

For the global root C, N(C) is A,B and four low neighbors. The internal
edge AB indeed contributes no internal opposite with two edges. However,
D is not in N(C), because CD is absent. D is an EXTERNAL HIGH opposite,
and N(C) intersect N(D) contains exactly A,B among highs and no common
low: all four highs share the common actual point, and a low cannot be a
defect neighbor of two of them. Thus l(C,D)=2 and binom(l,2)=1.
The paper's analysis of external LOW opposites does not include this term.
Symmetrically, C contributes one external-high cycle through D.

The low stub pool calculation itself survives: each of the four C-neighbor
lows has exactly two low edges, their pool is independent, so sum x=8.
Each external low has I0/1 high neighbors within A,B and remaining degree
at most3-I. Therefore binom(I+x,2)<=3x/2; the low-opposite contribution
is at most12. Adding the omitted high gives c_C<=13 and c_D<=13.

For A, B is instead an INTERNAL opposite inside N(A), using BC and BD.
Its contribution one was already counted; no alteration to c_A<=19 or
c_B<=19 is needed. The same collapsed local cycle has incidence one at
each of A,B,C,D; its contribution is not 'two cycles' but four root
incidences of one cycle.

The complete corrected upper bound is20*5+19+19+13+13=164, still below
the independently justified actual-square injection lower bound180.
This demonstrates a viable narrow repair of the exact proposed theorem;
it is not approval of a not-yet-frozen successor or a transfer of a V1 gate.
No scientific failure, execution or refutation of the literal theorem is
claimed. V1 remains unapproved pending its disclosed corrected proof.

Eight written checks: valid K4-minus-CD edge list; absent CD makes D an
external opposite of C; common high pair A/B contributes one; symmetry at
D; internal B/A terms were already counted; low-stub12 bounds remain;
one collapsed cycle has four incidences; corrected164 still contradicts180.
Three counter-controls: deleting the high opposite falsely gives12;
counting it twice per root falsely gives14; treating the collapsed cycle
as an actual square confuses point labels. No computational test was run.

Scope is this exact proof-bound/interface between internal and external
opposites only. No broader R226/two-D3/disjoint-b2/target exclusion, source
modification, ledger parse, protected/Git/index/publication mutation occurs.
