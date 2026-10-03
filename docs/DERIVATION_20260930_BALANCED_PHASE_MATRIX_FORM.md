# Candidate matrix form and all-mixed signed-support identity

Write L for the 12 by 20 incidence matrix of the twenty distinct support groups (the 12 by 60 support has each of these columns three times). Put S_ag=L_ag*(-1)^p_ag and put T_ag equal to the coordinate phase when a is in group g, otherwise zero. Let U=S entrywise-multiplied by T. All phase matrix equations in this note are over GF(3).

For each ordered coordinate pair a,b, the (a,b) entry of L T-transpose - U S-transpose is the sum over shared groups of t_b-s_a*s_b*t_a. This is the sum of its odd and even relative phases. Reversing a,b gives the odd sum minus the even sum. Since two is invertible over GF(3), the two ordered matrix entries vanish exactly when both sign-class sums vanish. Diagonal entries and matched-coordinate entries are identically zero. Thus the candidate necessary phase system has the equivalent matrix form

`L T^T = (S ∘ T) S^T`, `1^T T = 0`, `1^T (S ∘ T) = 0`,

together with the twenty first-coordinate phase gauges. For mixed groups the two column-sum equations are an invertible change from the two sign-class sums. For a normalized constant group S agrees with L, so they are identical and give the single local phase-sum equation. The matrix form does not add phase distinctness, multiplicities or outside-column caps.

Now consider any all-mixed parity projection on this exact support satisfying the original zero-or-three disagreement condition. Each column of S has three positive and three negative entries, so S-transpose times the all-ones vector is zero over the integers. A row of S has squared norm ten; matched rows have dot product zero; every nonmatched pair has dot product 5-2d, with d either zero or three. The sum of row a of S S-transpose is therefore 10-10+6z_a=6z_a, where z_a counts its zero-disagreement nonmatched partners. The row sum is also zero. Hence z_a=0 for every a: all sixty pair disagreements equal three. Consequently

`S S^T = 11I + M - J`

over the integers, where M is the six-pair matching. This is a general implication within the all-mixed parity-projection domain, not a consequence of inspecting only one witness.

This identity alone has not been shown to force the phase-system rank to be 119 for every eligible S. The recorded rank119 calculation applies to the one independently checked second branch. The general phase system always contains the degenerate solution T=(L-S)/2 (the normalized parity indicator), which arises from a global fibre translation followed by the column gauges. If at least one group is mixed, this solution is nonzero. It makes all same-sign phases in a mixed group equal, so it is not a valid mixed coloring. If a future independently verified branch system has exactly this one-dimensional nullspace, it is excluded; the existence of the vector alone supplies no exclusion.

The executable check authenticates the known raw support/parity and prior exact system, verifies all integer signed-Gram entries, and compares every coefficient in the scalar-to-matrix transformation. These finite identities calibrate the notation. No all-branch rank computation, candidate generation, native solve or full factor construction is performed.
