# Semiregular C11 encoder/WLOG structural audit

Status: **C11_SEMIREGULAR_STRUCTURAL_AUDIT_PASS**.

The base 99-vertex invariant encoder and current normalized CNF were rebuilt in memory without importing the producer. Their ordered clause lists match: base 234,612 variables / 511,119 clauses; normalized 235,279 variables / 512,750 clauses (hash `652C25...`).

All 4,851 unordered vertex pairs form 441 translation orbits of size 11. The nine weighted degree rows and all 441 common-neighbour rows therefore cover the full graph; product helpers satisfy the complete truth table for `p <-> (a and b)`.

The character argument gives quotient spectrum `14,3^4,(-4)^4` and nontrivial trace `-1`. Exact cyclotomic Fourier inversion forces every signed internal difference 1 through 5 to occur in exactly one fibre.

Independent subset-orbit and integer-partition enumeration first gives 321 raw degree/unit cases. The quotient diagonal identity `4t^2+2t+sum(c_j^2)=34`, together with choosing a fibre that has an internal edge, leaves four branches (two with t=1 and two with t=2). Fibre permutation, generator rescaling, and independent coordinate shifts put every semiregular-C11 candidate into at least one branch. This is a complete WLOG cover, not necessarily a disjoint isomorphism-orbit partition.

Boundary: solver statuses were intentionally not audited. The whole model concerns only the semiregular order-11 automorphism subclass.
