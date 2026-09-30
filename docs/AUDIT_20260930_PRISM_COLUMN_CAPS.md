# Independent audit of the six-prism column-cap extension

Reviewer `/root/structural_attack` did not author the extension. The checker
imports only previously independent generic JSON/hash utilities, and no
producer implementation. The complete-domain and first-choice normalization
gates are explicit premises. Original producer v1/v2 failures remain intact.

Reconstruct the triangle plus three twelve-row fibres directly. Each prism
component consists of the two bit coordinates in each of the three fibres;
its edges are the three bit-flip edges and the two triangles of equal bits.
Compute prescribed factor Gram entries from literal common-neighbour counts
in this raw39 graph. Independently enumerate all 6^6 ways to select one row
in each component and retain exactly those with two rows in each fibre. This
gives all 5,760 column supports, grouped into all sixty canonical C0 pairs
with exactly 96 supports per pair. This enumeration differs from the
producer's per-column choice of two of four components and four bits.

For each unknown incidence x[r,d], its support is the set of choice variables
in column d whose raw support contains r. The forward clauses say every
selected choice sets each of its four unknown incidences. The reverse clause
says any true incidence has a selected supporting choice. With the already
audited exactly-one choice per column these are exactly equivalent to the
raw incidence. All 1,440 bits are retained: 960 have 24 supports and 480 have
none, hence are forced false. Their exact clause counts are 23,040 forward
binary clauses and 1,440 reverse clauses, including all 480 zero units.

Within any one fibre, a column selects two rows. Two distinct columns cannot
contain the same pair of rows, since their within-fibre Gram entry would then
be at least two, whereas the base prescribed off-diagonal Gram is at most
one. Thus each fibre contributes overlap at most one. The canonical C0
columns are distinct pairs as well. If their C0 overlap is zero, the total
overlap is automatically at most two. If it is one, the cap is equivalent to
forbidding a shared C1 row together with a shared C2 row. The four-negative
clauses encode all such pairs of shared rows. This is an equivalence under
the base exact Gram and column-domain conditions, not an assumption about
arbitrary binary matrices.

There are 540 C0-sharing column pairs and 144 choices of two shared row
coordinates, hence 77,760 templates. Exactly 56,640 have an incidence with
empty support and are tautologies under its channel unit. All such omissions
are checked with their first empty-support coordinate; all 21,120 remaining
quartics are kept. Therefore the extension adds 45,600 clauses and 1,440
variables, yielding 247,320 variables and 920,401 clauses. The entire frozen
first-choice base clause body is compared byte-for-byte, and every appended
clause is independently reconstructed. The raw factor and cap equivalence
does not claim literal permutation of base prefix auxiliaries.

For an actual target, two outside vertices have at most two common known
factor neighbours, so the caps are necessary. Simultaneous row and canonical
column relabellings used to fix choice1 preserve all overlaps. Thus the
prior normalization coverage applies to the factor-plus-caps problem too.
The scope is solely the fixed six-prism core; no general core containment,
target automorphism, residual D or complete graph is supplied.

The local witness is checked as a separate, strictly weaker statement. Keep
all C0 entries and fill the two specified full columns. Every known Gram
contribution remains at most the prescribed entry, but their column overlap
is three. This proves that these local domain and known-contribution tests
alone do not imply the cap. It is not a complete Gram factor and does not
refute automaticity for complete abstract factors.

For any allowed column v, literal calculation gives v^T G v=114 and v^T v=6.
If a full factor F exists, row sums ten and column sums six give each row of
T=F^TF sum60; its diagonal is six and squared row sum is114. Hence the 59
off-diagonal entries have sum54 and square sum78. Both saved integer
distributions have exactly these moments; one includes a value three. They
show only that those two moments do not imply the cap. Neither distribution
is asserted to arise from a factor. Full-factor automaticity remains UNKNOWN.

Calibration exhausts the channel truth value and its flipped-bit rejection
for every raw selected-choice/unknown-row pair, all sixteen quartic truth
assignments, and all eight per-fibre overlap triples. Corrupted channel,
template, omission, local witness, moment and byte-stream controls are also
rejected. No complete research-factor positive fixture is invented, and no
solver is run by this audit.
