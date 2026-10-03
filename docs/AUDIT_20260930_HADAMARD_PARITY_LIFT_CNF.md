# Independent CNF audit of one balanced parity lift

This audit concerns only the saved twenty-group parity assignment on the fixed six-prism Hadamard support. Coordinatewise balance of each three-column group and that particular parity assignment are additional restrictions. Neither follows from existence of an arbitrary target graph.

The checker enumerates all 6^6 arrays of six coordinate permutations in S3. Requiring two occurrences of each fibre in each column and identifying column permutations by sorting the three words gives all 150 balanced local triples. Their normalized sign vectors select exactly 312 options in the chosen twenty groups. This path does not import the producer's triple enumeration or classification.

A one-hot choice in each group expands to three literal binary columns. Balance makes each core row occur in at most one column of a group; consequently each Gram coefficient is exactly zero or one. The audit reconstructs all 666 upper Gram equations by integer set membership and independently checks every prefix threshold gate, fresh variable and actual DIMACS clause with the frozen truth-relation checker.

For every pair of distinct groups the audit checks all nine intersections of their selected raw column sets. A choice pair is forbidden exactly when one intersection exceeds two. Within a group the three columns are disjoint, so the 190 intergroup relations and sixty within-group pairs cover all 1,770 outside-column pairs.

Thus, under the explicit fixed support, balance, sorted local words and selected parity branch, the CNF is satisfiable exactly when a binary factor satisfies the complete prescribed Gram and all outside-column caps. A positive assignment still requires the separate complete-assignment, actual-clause and raw-factor checker. No residual adjacency D is encoded, and no target automorphism is assumed.

Controls include exhaustive threshold truth relations, independently reconstructed local triples and deliberately corrupted scope/domain/cap artifacts. Local positive controls are not claimed to be complete research factors. The accompanying LP relaxation is checked in a separate audit lane.
