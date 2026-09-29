# Candidate transport of the independently checked36-literal nogood

The source nogood is independently established by
`C-UNRESTRICTED-TWO-STAR-POSITIVE-EDGE-NOGOOD36` revision1 and its pinned
raw finite-domain audit. This new transport package remains CANDIDATE until
a different checker verifies the maps, input identities and complete clause
images. No CNF modification or solver call is part of production.

The specified population consists of a permutation of groups{0,1}, a
permutation of groups{2,3}, a permutation of groups{4,5,6}, and independent
sign flips only in the three latter groups. There are exactly
2*2*6*8=192 tuples. The old symbol2g+b is sent to
2*pi(g)+(b xor flip(g)). The root is fixed. Inner vertices follow this symbol
map, and every outer label{a,b} follows its unordered image. Distinct tuples
give distinct inner maps. The nested finite enumeration therefore covers
exactly this specified population; no census of all target automorphisms or
arbitrary99-vertex relabelings is asserted.

Each symbol map preserves the root-pair partition and the matching of inner
vertices. It preserves every root adjacency and every inner-to-outer
incidence. All outer pairs remain free. It thus maps the entire normalized
target family bijectively to itself. The ordered anchor u={0,2},v={4,6} is
fixed because groups0,1 may only exchange with each other, groups2,3 likewise,
and their signs do not flip. This is relabeling of possible graphs, not a
claim that a hypothetical target possesses a nonidentity automorphism.

For an outer-edge variable e={x,y}, let f(e)={pi(x),pi(y)}. This is a
bijection on all3486 primary variables. Transport a signed literal on e to
the same sign on f(e), and apply this to all36 literals. To see entailment,
take any normalized target A and relabel it by the inverse vertex map. The
source clause holds in that normalized target, so the transported clause
holds in A. The separately established encoding equivalence transfers this
entailment to every satisfying assignment of the exact unrestricted CNF.
No permutation of its auxiliary prefix variables or clauses is required.

The resulting clauses may be added to any of the four existing branch CNFs:
they are already entailed by the unrestricted base. A map need not preserve
the particular branch's three-bit pattern. The package does not itself
materialize any augmented CNF, and makes no SAT/UNSAT assertion.

All192 full99 vertex arrays, with the root explicitly fixed and the98 other
images retained, and all192 complete3486-entry edge-variable permutations
are preserved. Raw image clauses retain source-literal order. Deduplication
uses a separately saved canonical order by absolute variable ID; it removes
only identical signed clauses. Counts of map tuples, clause images and unique
clauses are different pipeline units and are not additive.

The source clause's original bytes, including its newline convention, are
only read and hashed. The new suffix uses ASCII and explicit LF bytes. Gzip
is an exact transport copy of the recorded mapping JSON, with its raw and
compressed SHA256 hashes saved. All artifacts remain local pending parent
publication. Positive and corrupted producer controls are calibration only;
they do not self-promote this transport claim.
