# Hadamard20 collapsed-support construction scout

Freeze before execution. Construct a literal20-by20 sign matrix with first
row/column all+1 and bottom19block chi(i-j)-I, where chi is the quadratic
character modulo19. Verify all400integer orthogonality entries and all19
nonconstant-column balances; the name Paley is descriptive, not a trusted
theorem dependency. Use its columns1,...,6 for each matching block.

For each of three arbitrary12-coordinate perfect matchings M_g, list its six
pairs lexicographically and put a chosen sign column on the lower endpoint,
its negative on the upper. Concatenate the three12-by20blocks into X and set
L=(X+J)/2. Check binary L, row sums30, column sums6,
XX^T=20(3I-M0-M1-M2) and LL^T=15I+15J-5(M0+M1+M2).

Frozen finite selections: the four already independently audited connected
identity-P cores, followed by the six-prism core with all three matchings
equal to the standard matching. This selects one support matrix per core,
not a complete census of Hadamard choices or graph/core families.

Cheap falsifiers for each of these five fixed support matrices:
1. Save duplicate support multiplicities and all sixty support sets.
2. Enumerate all90 assignments of each six-coordinate support to three labelled
   fibres with two coordinates per fibre. Retain only choices whose selected
   inner row pairs have positive prescribed Gram entry. Save every surviving
   choice and any empty-column witness.
3. For each required Gram entry count how many columns could contribute, and
   save any shortage witness. Counts are independent upper capacities only.
4. For each of the1,770column pairs seek a pair of retained choices having
   at most2common rows; save raw choices or an exhaustive empty compatibility.
5. For each fibre seek a perfect matching between the60columns and its60
   nonmatching coordinate pairs using available retained choices. Save a
   literal matching, or a Hall deficit with its complete neighbor set.

Bound120seconds, no SAT/MIP/search for a complete factor, no RNG, no CNF or
native launch. Calibrate sign corruption, support corruption, invalidmatching,
tiny bipartite positive/Hall-negative instances and bad matching witnesses.
Record exact commands/versions/hashes and a narrow archive keyword search.
No full-factor conclusion from passing necessary screens; independently review
all producer claims before encoding or searching this restricted support family.
