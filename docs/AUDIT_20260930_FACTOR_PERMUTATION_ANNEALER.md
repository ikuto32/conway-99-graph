# Independent review scope for the factor-permutation annealer

This document specifies the exact reasoning and independent checks required
for the frozen calibration gate. Until the bound report passes, it records
a review in progress, not campaign approval or a mathematical construction.

The domain fixes a cubic triangle core C on3n vertices, with three even
n-vertex cells and one matching in every block. Let m=n(n-2)/2. C0 is the
canonical incidence matrix of all nonmatching pairs in the first cell.
In each other cell, a state is a permutation of its complete catalogue of
nonmatching pairs, placed in the m outside-column positions. Every state
therefore retains two entries per cell per column, row weight n-2 and the
exact prescribed within-cell Gram. The fixed raw core and target cross-Gram
must be independently bound; native catalogue degree checks alone do not
establish that an arbitrary supplied target matrix is the core's Gram.

The integer objective, TRIANGLE_FACTOR_CROSS_GRAM_SQUARED_V1, is

`E = sum_(g<h) sum_(r in cell g,s in cell h) (F_r dot F_s - K_rs)^2`.

It has432 terms at n=12 and1200 at n=20. Lower is better only within this
same objective and stated domain. E=0 supplies an abstract Gram factor for
the fixed core; it neither implies the omitted pair caps nor constructs the
residual adjacency D. Scores are not target-wide search coverage or bounds.

For a proposal swapping columns a,b in one cell g, only rows of that cell
whose two bits differ change. They are exactly the vertices in the symmetric
difference of the two catalogue edges, at most four rows. For each such r,
toggle its two bits and compare its old and new dot products with every row
s of both other cells. The difference of squared errors is added once for
each(r,s). No within-cell term occurs in E. No row outside g changes, so
every changed term has exactly one endpoint among these r and every other
term is unchanged. Summing these differences is therefore exactly the full
new objective minus the old objective, without a simultaneous-update error
or double counting. This is an algebraic argument for every permitted swap,
not an inference from sampled GPU agreement.

Masks use three64-bit words, enough for m<=180. A swap in the same word
still flips two distinct bits; a swap crossing63/64 or127/128 changes the
corresponding separate words. The independent checks must include both
boundaries, reconstruct masks from permutation data, and inspect all saved
proposal deltas and final/best objects. Scores and deltas are integral.
Under the native parser's n<=20, catalogue degree n-2 and target range[-3,n],
the full score is at most3*n*n*(n+1)^2<=529200, safely within signed32-bit
arithmetic. The raw objective verifier separately checks actual core/domain
conditions rather than relying on this loose numeric bound.

The producer CPU path rebuilds every mask and recomputes the whole score for
each proposal, while the GPU path uses the local delta. These are distinct
energy calculations but share RNG, proposal and acceptance helpers. Both
also use floating exponential acceptance at nonzero temperature. Saved
CPU/GPU trajectory equality is a finite calibration result only; it is not
a guarantee for every possible floating threshold or future trajectory.
Independent review reconstructs proposals/RNG state and scores from raw
artifacts, distinguishes forced moves, zero-temperature moves and positive
temperature cases, and checks split/resume against uninterrupted execution.

The separately calibrated integer reference
`audit_20260930_factor_annealing_objective.py` has a known nonempty positive
SRG243-derived factor with E=0 and no cap violations, a domain-preserving
single-cell column swap with E=24, and malformed controls. This establishes
the raw scoring path, not CUDA correctness. The243 fixture is from a different
parameter set and is never described as target99 evidence. The annealer
calibration must additionally bind compiler/source/binary identity, actual
device and launch settings, CPU/GPU outputs, all input hashes and corruption
outcomes. No producer import may supply the independent reference score.

Before a campaign, the exporter must preserve an exact integer raw object
`{core_adjacency, factor, claimed_score}` plus objective version, label maps,
state/permutation/RNG identity and provenance. Final and best states are
separate artifacts; shared labels must not be silently changed. Every useful
score-zero candidate still needs the independent raw Gram/margin/domain
check, exact caps, and ultimately an independently validated full99 graph.
