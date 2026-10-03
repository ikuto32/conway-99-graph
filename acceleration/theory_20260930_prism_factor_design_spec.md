# Restricted six-prism factor construction pilot

Frozen question: can the following explicitly restricted binary design
produce a 36x60 incidence factor for M0=M1=M2=(01)(23)...(10 11), P=I?
This is a different fixed core from the preceding shift6 experiments.

Use six component labels, three cell labels and two bit labels in each
cell/component. Fix the five round-robin perfect matchings of K6, with
vertices F5 union {infinity}. For each matching use all six assignments of
the three cell labels to its three edges. For each of these 30 patterns,
choose a six-bit string with bit0=0 and include its complementary string
as a second column. Thus there are 60 columns, each with one vertex from
each component and two from each cell. The complementary pairing is a
construction restriction, not an assumed automorphism of a hypothetical
target graph. No claim of covering all factors or all cores is made.

For each component pair and same cell, the two relevant patterns must have
opposite endpoint-bit parities. For each component pair and ordered distinct
cell pair, exactly two of the four relevant patterns must have odd parity.
These finite conditions impose the desired cross-component intersections:
one in a common cell, two in different cells. Within a component all distinct
rows are disjoint. The row margins are ten automatically.

Question selection: the archived kappa<=3 argument assumes a triangle-free
inner graph and cannot exclude this six-prism core. This tiny construction
test explores the other local regime before any larger computation.

Protocol: construct the 450-variable 2,010-clause Boolean parity formula;
check all XOR truth assignments and all 16 four-bit exact-two assignments;
run the already calibrated and hash-authenticated native CaDiCaL 1.9.5 for
at most 5 seconds, 100,000 conflicts, 256 MiB address space and 128 MiB
trace, with TERM/2-second kill and a 15-second outer guard. One attempt,
default seed, no automatic retry. This is a cheap falsification pilot, not
an expensive search. Preserve exact input, source, commands, logs and trace.

Success requires a complete raw binary 36x60 factor satisfying all integer
Gram entries, row10 and cell-column2 margins. The producer only labels that
artifact CANDIDATE; a distinct reviewer must independently check the raw
matrix and exact core, with positive and corrupted controls. A SAT factor
does not construct a 99-vertex graph. UNSAT is merely unverified solver
output until a complete trace and this restricted encoding are independently
checked; even then it would exclude only the stated construction design.
Timeouts and incomplete traces give no mathematical exclusion.

No floating arithmetic or numerical acceptance threshold is used.
