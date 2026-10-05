# Exact local-trade census after the seed61 warm result

Design only. No census, new solver or annealer has been launched by this note.

The independent warm saved-object report is
`acceleration/results/20261003_independent_review/weight60_warm01/summary.json`,
SHA256256c8277ab5c69e74f4c9725c4b42e96e31b4e546c490b8e231df4ed6831bf6c.
It checks the exact final graph with lambda residual0 and mu residual3480,
128 below the stepzero3608 input, but4764ordered SRG identity mismatches.
The final/current/best adjacency identity is
9d5b88ba2a2eb13d39d2a5edea1c25af9a9105c143c4297fe37e84f666a37a2d;
serialized final state is
c15b421468af173b6c2ee11e9bcb31d5abca586fcb47a7c7ee312f527b31979b.
Sparse trajectory gaps prevent a complete trajectory or global-best claim.

Concrete next action: enumerate the entire one-move neighborhood of this fixed
labelled hypergraph under the unchanged V2 exclusive two-line swap semantics.
The frozen proposal population is every unordered pair of its231 labelled
triples and each of their3-by3 selected point pairs: exactly239085 labelled
proposals. Shared-point pairs remain included; the same exclusivity, distinct
triple, linearity and degree tests decide validity. Reversing the ordered pair
duplicates the same swap, so orientation is normalized explicitly by i<j.
This is a finite proposal population, not a count of unique neighbor graphs or
any fraction of Conway-99 search space.

For every proposal, save its input labels/points, validity reason, exact changed
triples, lambda/mu/ordinary and weighted residual deltas, and neighbor identity
when valid. Classify all lambda-preserving moves by negative/zero/positive mu
delta. Preserve all minimum-delta ties and both labelled-proposal and unique
neighbor counts separately. No random selection or omitted unfavorable cases.

Independent checking must enumerate the same239085 proposals using a separate
adjacency-set implementation and compare every validity classification. It
must fully rescore every lambda0 neighbor with exact integer common-neighbor
counts, compare all retained raw neighbors, and verify the frozen universe and
orientation argument. Known-valid rook9, shared-point prism-to-rook/inverse,
rollback and corrupted score/cache/proposal-population controls precede use.
The existing V2 gate is source evidence only; new census code needs its own
source/spec/control gate and supported fresh resource/deadline preflight.

If a negative-delta lambda0 neighbor exists, retain an exact graph for independent
validation and use this evidence to design deterministic lambda0 descent or a
plateau-walk experiment. If none exists after the complete independent census,
the only established exclusion is an improving one-move V2 neighbor of this
one fixed graph. That would justify testing a separately gated three-line cyclic
trade kernel or a higher-temperature escape, without asserting disconnectedness,
ergodicity, a global minimum or target nonexistence. Neutral move population
also informs whether a plateau walk has concrete remaining choices.

A tentative supported allocation is300outer/270worker/20reserve, reassessed
after engineering enumeration timings. New code may use exact incremental
integer deltas to guide enumeration, but independent full rescoring is required.
The tiny frozen finite universe should be diagnosed before another100million
heuristic proposal run. No timing or success probability is asserted yet.
ROOT must choose and authorize the actual versioned computational protocol;
this design does not authorize execution.
