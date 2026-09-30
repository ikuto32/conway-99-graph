# Independent raw-cell encoding and object audit

This checker imports no production encoder. It independently reconstructs the
literal six-prism core, its integer Gram target, all allowed labelled cells,
row counters or count links, all products and all column cap flags. It compares
every standalone clause and every appended coupled clause byte, the entire
authenticated master prefix, every recipe field affecting encoding, and every
section boundary. Scope checks reject omitted caps, extra normalization or a
different count restriction. Inputs and current source bytes are recorded.

The scope is one literal support. In the standalone formula, the primary bits
are exactly the allowed entries of a binary 36 by 60 matrix. One-hot clauses
give the support sums, and six-bit cardinalities give two entries in each
column fibre. Threshold variables satisfy the recurrence
`s(i,j) = s(i-1,j) OR (x(i) AND s(i-1,j-1))`; induction from its Boolean boundary
values proves exact row cardinality ten, with unique counter values.

The 540 positive off-diagonal Gram entries use exact AND products and exact
cardinalities. The remaining 90 upper-triangular entries are zero: different
fibres at the same coordinate cannot both be selected, and matched coordinates
never occur together in a support. Row sums supply the 36 diagonal entries.
Each shared-coordinate equality flag is equivalent to equality of the two
selected fibres under the already enforced one-hot triples. At-most-two flags
therefore imposes exactly the column overlap cap. Pairs with intersection at
most two satisfy it automatically. No original column labels are permuted.

The coupled variant retains the previously independently checked count master
and its explicit at-least-seven bound. Every selected incidence channel fixes
the actual three-column count by conditional truth-table clauses. The master
coordinate domains give row margins ten. For the converse, full Gram implies
the projected marginal identities by summing the three fibre rows at another
coordinate; within-group caps imply distinct local words. Sorting those three
words only witnesses membership in the complete local catalogue. It does not
normalize or restrict the raw labelled matrix. Completeness of the count master
is a pinned prior verification premise, not a new unrestricted coverage claim.

The literal six-prism core also makes every mixed cap automatic: a column
selects one vertex in each triangular-prism component. A closed neighborhood
contains at most the column's one selected vertex in that component. The SAT
object check nevertheless evaluates all 2,160 mixed entries explicitly.

Controls exhaust small cardinality and gadget truth tables, including arbitrary
auxiliary truth values, genuine SRG243 raw-factor checks and deliberate
corruptions. Complete local-support/fibre and synthetic assignment controls are
labelled separately. No full-Gram positive factor for the research support is
known, and none is invented. The raw SAT path independently evaluates all
actual clauses and all integer matrix/cap entries. Its native and JSON codecs
and genuine243 raw-factor control reuse earlier independent checker components;
this shared trust is explicit.

Modes `audit`, `calibrate` and `sat` use a 180-second cooperative allocation.
Calibration pins the separately frozen native driver/spec and recursively
identified local import sources; it does not launch or import that driver.
Any failure is saved in a fresh output directory; no prior evidence is replaced.
No solver, proof replay, ledger edit or publication occurs. An UNSAT result
requires a different verifier to replay its complete proof. A SAT result here
would be a factor only: residual D and the full 99-vertex target remain absent.
