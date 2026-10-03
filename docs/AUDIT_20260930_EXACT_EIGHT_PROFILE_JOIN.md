# Independent complete eight-profile census audit

Frozen question: enumerate the necessary count CSP on all 67 subsets retained
by the separately checked 4,184-subset reduction. No previously excluded
literal profiles or upper-envelope failures are removed from this population.

The verifier will enumerate every element of the saved Cartesian products
(sum 7,122,626) in mixed-radix batches. It will use unsigned 64-bit exact
integers to pack eighteen base-four digits into 36 bits, then test membership
in local signature sets. The producer instead uses recursive bitset joins.
No producer code is imported. The finite integer range precludes overflow.

Before research enumeration, compare mixed-radix batches with explicit Python
Cartesian products for every length vector in {1,2,3}^4; compare the actual
membership routine with every subset of eight tiny codes, including empty
sets; and test injective signature packing/unpacking and nonfree fibre orbits.
Reject missing/duplicate profiles, corrupted count tables, local signature IDs,
hashes, orbit members and closure claims.

For every accepted Cartesian assignment, compare the full coordinate IDs and
literal counts with the saved profile stream. Recompute all 20 signature IDs,
exception groups, byte hashes, six fibre images, canonicalizing permutation,
actual orbit size and the complete saved orbit membership records. Confirm
the three earlier count witnesses are present by literal counts, because their
historical profile digest convention differs from the new census byte hash.

Budget: 120 cooperative seconds, batches of 65,536, no solver or floating point.
Save per-subset completed checks and progress. If the limit is reached, preserve
the partial audit and do not approve complete coverage. Prior independent
domain/census coverage and NumPy's pinned integer operations are trusted.

The resulting count census is a finite necessary relaxation on one fixed
support. Neither a count profile nor a relabeling class asserts a Gram factor,
residual completion, graph automorphism, or target graph.
