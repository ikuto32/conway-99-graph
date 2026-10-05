# Frozen bounded joint two-star matching pilot

Status: producer protocol; all discoveries remain CANDIDATE pending independent
checking. No claim ledger changes or target solver launch are part of this run.

Fix the unrestricted scaffold and adjacent outer vertices u={0,2}, v={4,6}.
Take the first eight stored stars in each of the four first-level patterns
from the single-star run (32 total). For each, sample v's twelve-label star
by deterministic shuffled residual stubs, seed2026093002, requiring u in it,
all14 symbol quotas, and exactly one shared neighbor w whose label is disjoint
from both center labels. Freeze all32 raw star pairs before matching search.
The selection is a sampled labeled population, not an exhaustive universe.

Let A=N(u) minus {v,w}, B=N(v) minus {u,w}. Both have twelve vertices.
The target forces an internal perfect matching on each. For a in A, the
nonedge(a,v) has common neighbor u and exactly one further neighbor in B;
thus A--B is a perfect matching. Existing root edges force two internal edges
in each block and four cross edges. Enumerate the remaining two8-vertex
internal matchings and8-by8 cross matching jointly, retaining every edge
choice unless a literal integer known-neighbor cap rejects it. Each rejection
records the violated pair and all current known common neighbors.

The resulting relaxation enforces exact pair equalities involving u or v and
every vertex in the closed edge-neighborhood, as well as all their inner
symbol equalities. Pairs involving u/v and other outer vertices remain lower
counts; no claim that all99 centered equations have been solved is made.
All4851 known-edge pair caps and degree caps are required. Unknown entries
outside the designated matchings and full center stars are not fixed absent.

Before search: K4 matching and impossible singleton-matching controls, positive
scaffold, and deliberately corrupted cap and quota controls must pass. Stop
after at most60seconds of enumeration,32 completed cases or1,000,000 nodes,
whichever comes first. Save an explicit incomplete checkpoint on any cap;
never label incomplete trees exclusions. Complete unsuccessful enumeration
saves every branch and exact cap witness. Success saves a raw partial99
matrix, all three matchings and exact equality/cap checks. This is local
feasibility only. No numerical thresholds, optimization or SAT solver used.

Prior-work inspection: the20260917 matching-pair filter checks reciprocity
and intersection counts in a fixed-K family; archive wave151 fixes abstract
triangle matchings before incidence-factor search. This pilot instead couples
three still-variable matchings for sampled unrestricted root-scaffold stars.
No claim of novelty or exhaustive literature coverage is made.
