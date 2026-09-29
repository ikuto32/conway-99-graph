# Preregistered fixed-scaffold relabeling census

Frozen before execution. This census begins only after the bounded box-cut
wave02 ends; its timestamp and source hashes are recorded before enumeration.

Question: which relabelings among the 3,840 central perfect-matching-preserving
permutations, combined with the eight rook-core symmetries fixing (0,0), preserve
the exact known/free 59-vertex scaffold and block degree topology of the frozen
780-edge model? The universe consists of 30,720 explicitly tested pairs.
Central permutations are all 5! matching-pair permutations and 2^5 endpoint
flips. Rook-core maps are all independent swaps of row labels 1,2 and column
labels 1,2, followed optionally by transposition. No target automorphism is
assumed. This is a relabeling symmetry of a restricted encoding family.

For each pair, central incidence columns determine at most one permutation of
each right cell: each column is the unique two-element subset of central
vertices in the raw factor incidence block. Accept only when these subsets map
bijectively into the target block. Then construct the full59 vertex permutation,
induced permutation of the 780 free edge variables, and verify every known/free
adjacency entry, rook attachment and degree-row signature exactly.

Freeze every accepted map as raw integer arrays. Check identity, bijectivity,
and closure of the accepted maps, but do not treat producer tests as independent
verification. Preserve deliberately corrupted map failures as calibration.
No SAT run, transported research cut, or model restriction is performed by this
census. Transporting clauses is authorized only after independent checking of
the exact mapping records and their necessary-constraint interpretation.

Limits: all 30,720 pairs or 60 seconds, whichever comes first. A timeout yields
only a partial census, never completeness. No floating arithmetic or numerical
thresholds are used. Source commit, exact command, Python and lock versions,
input/output hashes, elapsed time and any incomplete status are saved.

The scope excludes arbitrary graph automorphisms that do not preserve this
designated rook core, central cell and induced cell labeling. It provides no
coverage or existence result about the unrestricted target.
