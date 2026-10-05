# Fixed parity balanced-color lift, preregistered before building

The question is whether the first saved independently verified 20-pattern parity
assignment lifts to a binary 36 by 60 factor on the fixed Hadamard six-prism
support. The assignment is selected by first completed exact SAT outcome, not by
scores or subsequent feasibility tests. Its 16 mixed and four constant patterns
are frozen in decoded_projection.json, SHA256
0e80251a964330092d8da9030df2e2ee7f56476cee9e588be921dbe2f470e646.
The corrected actual-object audit d2536119... and its independent checker-delta
review 599b7b2f... must both pass and bind unchanged raw bytes before this build.
The original hex-format checker failure remains preserved. This new source does
not import any independent checker or change any previous artifact.

This is one parity branch of an additional balanced-triplet restriction on one
fixed support. Neither balancing nor the parity branch is without loss of
generality for arbitrary factors. The residual 60-vertex adjacency is absent.
No target automorphism is assumed. SAT would supply only a factor candidate;
UNSAT, with complete independently replayed proof, would exclude only this
branch. Target existence remains UNKNOWN.

For each of the 20 identical-support groups, independently enumerated increasing
triples of the 90 two-of-each-fibre words are filtered by their normalized S3
parity. All 150 balanced triples are considered. A mixed pattern retains 12 and
the constant pattern retains 30, for 312 selectors in total. The three increasing
words are placed in increasing raw column order. This is the independently
audited identical-support column relabelling; its normalization does not choose
a word or assume an automorphism. A common column permutation changes all six
S3 signs together, preserving their relative parity.

The CNF uses 20 exact-one constraints and all 666 upper-triangular Gram equations,
including diagonal and zero equations. A selected triple contributes zero or one
to every Gram entry because each core row appears in at most one of its three
columns. Therefore these equations are literal cardinalities of selector sets.
They use the frozen exact bidirectional threshold recurrence, with all state and
clause metadata saved. For each of 190 group pairs, every option pair is checked
against all nine lifted column overlaps; an overlap greater than two forbids
that selector pair. This covers 1,710 pairs of different-group columns. The
remaining 60 within-group pairs are disjoint by balancing. Mixed core/outside
caps follow from the previously audited identity-P lemma and are also tested by
the candidate raw decoder. These necessary caps are not called consequences of
an arbitrary abstract Gram factor outside the stated domain.

An additional exact_model.json is saved before CNF emission for a cheap separate
LP screen: 312 nonnegative columns, 560 equations consisting of 20 exact-one rows
then all 540 positive off-diagonal Gram rows. Keys are
columns_nonzero_row_indices, rhs, selectors, variables, equations and
binary_coefficients, with complete row metadata. Entries are exact integers
zero or one. This relaxation omits selector integrality and inter-group column
caps. Diagonal and zero Gram rows omitted from this matrix are automatic from
the balanced local options; the CNF retains them explicitly. No LP is run here.

Limits: one complete build, 120 seconds wall time and 8 GiB sampled process peak
working set, with zero solver calls. The inherited resource checker is called
throughout encoding and packaging. Preserve a failure.json and partial files if
any limit or assertion fails; do not reinterpret a failed build as an exclusion.
The acceptance criterion is an unchanged-input complete artifact with exact
metadata, 312 primary selectors and no omitted cap cases, pending separate
independent encoding and object audits. No floating arithmetic or numerical
acceptance threshold is used. No SAT run is authorized by this specification.

Controls exhaust all 150 local triples and all six common column permutations,
reject malformed local rows, and rerun the frozen threshold truth-table controls
including wrong auxiliary values. A full research factor is not supplied by
these local positives. Any future SAT assignment must independently pass every
raw clause and the full literal 36 by 60 Gram/margin/support/cap checks. The
producer decoder emits raw factor, selected word indices, matchings, identity P,
and an explicit column permutation to the canonical C0 edge catalogue. It does
not approve its own output.

The manifest records exact source commit, command, working directory, locked
environment versions and input hashes. The CNF, body and metadata are packaged
as gzip chunks below 10 MiB with exact reconstruction checks. No old file,
ledger, Git state, or publication catalog is changed.

Locked invocation from the repository root:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/theory_20260930_hadamard_parity_lift_cnf.py build --out acceleration/results/20260930_hadamard_parity_lift_cnf
```
