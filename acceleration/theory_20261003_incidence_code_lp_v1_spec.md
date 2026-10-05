# One exact-certificate coding bound guide V1

Question: can MacWilliams positivity sharpen the independently derived
conditional triangle-incidence rank>=67? Frozen universe: binary linear codes
of length99 with nonzero weights contained in the13 even values36..60. The
zero code is included. No minimum code dimension or incidence rank upper bound
is assumed. This is one continuous13-row99-column dual guide, not graph search.

For `K_j(w)=sum_s(-1)^s binom(w,s)binom(99-w,j-s)`, define
`G[w,j]=-K_j(w)/binom(99,j)` for j1..99. Find y>=0 with Gy>=1,
minimizing sum y. For a binary linear code, a direct character sum gives
`sum_w A_w K_j(w)=|C|*(number of dual words of weightj)>=0`.
Since A_0=1, these inequalities imply `sum_{w>0}A_w G[w,j]<=1`.
Any exact rational feasible y therefore proves `|C|<=1+sum y` by multiplying
and summing. This character proof and every coefficient must be independently
rederived by the verifier. No optimization status alone proves anything.

Before guide: positive length3 full-code dual with bound8 and four deliberately
corrupted duals, plus literal character-polynomial agreement for n1..6.
Only nonnegative rational vectors whose minimum exact Gy is positive are
lifted; divide by that exact minimum to ensure every inequality>=1. Freeze
rounding limits1000/1e6/1e9, record all attempts, and save complete99-coordinate
dual/raw exact model. Exact power-of-two comparison supplies dimension bound;
no floating acceptance threshold or claimed optimizer optimum.

One120outer/90worker allocation, numerical guide at most30seconds with30seconds
internal reserve for exact reconstruction/checkpoint; outer30shutdown reserve.
Justification: only1287 coefficients and99 variables, compared with completed
thousands-variable guides; this is a deliberately tiny experiment, not the old
60second solver default. Deadline includes controls/model/hash/checking. A failed
or stopped lift is UNKNOWN/not completed within allocated budget as applicable.
One thread, simplex, seed0, primal/dual tolerance1e-10 guide only; locked uv.

Independent verification must use raw certificate, a separate Krawtchouk
recurrence or literal polynomial implementation and exact rational arithmetic,
positive/corrupted controls, the code-character inequality and target incidence
weight proof. A checked bound may promote only its exact conditional statement.
No construction, nonexistence, target-wide coverage, or rank upper premise.

Literature provenance: Delsarte1973 dissertation catalog at
https://research.dial.uclouvain.be/entities/publication/7c6fb939-72d8-4dbd-a505-005a43543186
was inspected2026-10-03 JST; its full PDF was restricted/unavailable. No theorem
is attributed to an unread page. The complete character derivation is supplied
above and will be independently checked; novelty/peer review remain UNKNOWN.
