# First and third literal profile obstruction analysis

No small complete mathematical contradiction was obtained. The two prior independently replayed UNSAT results remain the exclusions; the new records below are producer candidates awaiting separate review. No SAT call, ledger edit or publication mutation occurred.

The authenticated DRAT-trim core extraction reduced the first formula from167,416 to52,516 clauses (trimmed proof3,391,253 bytes), and the third to39,510 clauses (trimmed proof2,056,675 bytes). Both smaller formula/proof pairs replayed successfully and were checked as literal clause-multiset subsets of the originals. They still span all60 coordinate pairs, so these cores do not provide a small explanation. Neither core is claimed minimal.

Exact shared-block propagation removed192 original local options for the first profile and288 for the third. Both reached nonempty fixed points after two sweeps. In both profiles balanced group16, support[1,3,5,7,8,11], has just six remaining options54,55,56,90,91,92. Conditioning separately on each of these options gave twelve nonempty fixed points; no branch was excluded by this test. Nonempty necessary domains do not establish a joint choice.

A compact reusable restriction was isolated at coordinate pair(1,5). Its five contributions come from groups3,11,13,15,16. The exceptional populations alternate between two matrices of typeA and two of typeB; the balanced population is the six permutation matrices. With target2J-I, the only possible projected tuple uses the first matrix in every exceptional population and the identity permutation in group16. The full96-combination census, all raw local-choice projections and six simultaneous fibre relabellings are saved in `shared_block_identity`.

The short argument is: exceptional populations contribute zero to cell(1,1), so the permutation P fixes1. If P swaps0 and2, the two off-diagonal cells force exactly one second A choice and one second B choice, while cell(0,0) requires only one in total. Hence P=I; those off-diagonal cells then force no second choices. This rule applies to any independently established domains with these same five projection populations, including their common fibre relabellings. It is a necessary restriction, not a new profile exclusion. It removes144 of150 group16 choices and12 of48 choices in each of the four exceptional groups.

The continuous selector-equality relaxations, using all original2,184 options and560 integer equalities in each profile, returned numerical optimal status in0.046s and0.047s. Bounded rational reconstruction did not yield exact primal certificates. These are therefore numerical diagnostics only, with no claimed exact relaxation-feasibility result. No Farkas obstruction was obtained. The raw float solutions, exact matrices and controls are preserved.

Frozen output summaries:

- `acceleration/results/20260930_first_third_proof_obstructions/summary.json`: `018b134a4f6682e177ba4c95cb98a77036e4a05c42735608cd07dc53af2f1951`.
- `acceleration/results/20260930_first_third_block_singletons/summary.json`: `4f2ed4a015b8c587886507c90543a0a9b361483f520cf0aba706921bf37c2da2`.
- `acceleration/results/20260930_first_third_gram_lp/summary.json`: `1361651e3f1c705b4204c800d61b1f80e502681c2c85e872c58db192a31c0085`.
- `acceleration/results/20260930_shared_block_identity/summary.json`: `0983223571fb4d513917695c46b79b95ef93b04272308e10dad9f1c182bd858f`.

Each stage has a separate pre-execution spec and source, with preserved raw outputs and no source edits after execution. The first three stages took4.456s,1.720s and2.603s respectively; the finite96-case rule check was also subsecond. The first stage has900 Cartesian support controls and authenticated tiny proof extraction/replay controls. New block pruning and its short rule require a distinct reviewer before mathematical registration or reuse as an approved search premise.
