# Independent exact K3 counterexample to the original generic SRG wording

Reviewer: `/root`. Mathematical producer of the original claim: `/root/checkpoint_audit`. Native first identified this boundary. Root separately checks it here by direct three-vertex integer arithmetic and constant cardinality equalities, without running the producer or agreeing by authority. Root proposed the wider research direction but did not author the original universal statement.

This check concerns exactly C-FIXED-COUNT-LABELLED-SRG-CNF-COMPLETION-EQUIVALENCE revision 1 in raw6d750012 and paper950803fb. Conventional nontrivial SRG terminology means 0<k<v-1, as expressly recorded by the preserved clarification560f3342 and Native auditc4098eeb. The original supplied-profile hypotheses and actual source profile domain do not impose that condition.

Take m=1, N=2, v=3, k=2, H=[0], B=[1,1]. The two exterior copies are distinct copies of the sole mask1, with count2. The one extant exterior pair has allowed set {1}. All entries are exact binary integers, counts sum2, H is simple, and the source domain 0<=k<v<=99 is satisfied. The fixed support degree is 0+1+1=2. Its distinct support-pair moment condition has no pairs and is vacuously true.

Set D=[[0,1],[1,0]]. For each of the two exterior vertices the required outside degree is k-|T|=1 and its D degree is1. For each support/exterior pair the required cross count is 2-B-(HB)=2-1-0=1; its sole other exterior vertex has incidence1 and D edge1, so the actual cross count is1. For the one exterior pair there are no third exterior vertices and the support intersection is1. The outside equation therefore is 0+1=2-1, also true.

There are five equality groups: two degree, two cross and one exterior pair. Each consists only of a fixed true term with required sum1. Constant normalization leaves empty input sum0=0; all assertions are true. There are no free edges or required fresh gates. Thus the mathematical construction is satisfiable, independently of any solver or emitted byte formula.

The complete adjacency and its square are

    A  = [[0,1,1], [1,0,1], [1,1,0]],
    A2 = [[2,1,1], [1,2,1], [1,1,2]].

Every diagonal product is 1+1=2; every off-diagonal product is the single third-vertex product1. Consequently A2+A=2J, exactly (k-2)I+2J. The supplied H/B and forced D leave this K3 as the only possible completion. K3 has k=v-1=2, so it is outside the expressly stated conventional nontrivial SRG domain. The universal equivalence to a conventional SRG therefore has a true left side and a false right side on this admitted profile.

This is evidence against the exact original statement under its recorded convention, rather than merely a missing proof, timeout or failed reproduction. The original generic claim is REFUTED within this scope. Its degree/common-neighbor identity equivalence is not refuted. The separately qualified theorem with explicit 0<k<v-1 has a distinct claim ID; no proof or registration of that corrected theorem follows from this refutation alone.

The 99/14 scientific application and rook9/4 controls meet nontriviality and are unaffected. No target graph, target exclusion, actual CNF, numerical computation, formal proof or external review is established here. All original paper, raw claim, challenged review, clarification and qualified review bytes are preserved.