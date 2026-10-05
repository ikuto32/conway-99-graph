# Candidate restart-state preparation from a preserved DRAT prefix

Scope: recover a candidate active clause multiset from the original unrestricted
CNF and complete records of the historical partial trace. Preserve all originals.
This producer parses syntax/state only and performs no RAT/RUP validation. Its
output must remain CANDIDATE; neither parser correctness nor a successful restart
alone establishes equivalence, an exclusion or a target resolution.

The historical original CNF is84,919,934 bytes,1,186,500 variables,4,136,454 clauses,
SHA7029f5c0965d0121aec6ce24db2b9a3d2e201e85b72c8ef51595c63bb62b2138.
The partial trace is346,616,832 bytes,
SHA11abdc29b502b8b09d4dc6ac3e9f03fa7ea8947496bc8e538a5043d113272f22,
at `20260930_unrestricted_native_pilot/main/proof.drat`. Its original300-second
attempt returnedUNKNOWN. Direct inspection of its last1,024 bytes finds a final
unterminated record ending `-94954 10828 583 114384 580 10920 -6`. The original
trace remains unchanged. A new retained-prefix derivative drops only an
unterminated final raw record; all prior record bytes and literal/pivot order
remain intact. A complete final record without LF receives one explicitly
recorded boundary LF. Internal malformed/incomplete records fail closed.

Checking profile: `PINNED_BACKWARD_UNSAT_SINGLE_COPY_IGNORE_SMALL_DELETE_V1`.
It refers to exact preserved `build/rook-drat-checker/drat-trim.c`,
SHA82835512d4eda7dee1e0e3f610a0672fa1d216ea91246bcb576022020fe18f4c,
defaultBACKWARD_UNSAT, deletions enabled. Normalize literal order and duplicate
literals for clause identity; preserve tautological clauses and repeated clause
occurrences. Delete one matching occurrence per nonunit deletion. Missing
deletions are no-ops. Ignore deletion of clauses of size<=1 as the pinned
backward checker does. Raw retained proof records are never sorted or rewritten:
RAT pivots remain the original first literals. An alternative checker mode or
profile needs a new applicable engineering/verification audit.

C++ representation: contiguous32-bit literal pool,64-bit multiplicities and
offsets, unique normalized clause records,64-bit hash buckets with exact
collision checking. Identical clauses share a record but preserve multiplicity.
The output repeats each live occurrence in a deterministic first-seen unique
clause order. It keeps the original variable count; fresh proof variables outside
that universe fail closed. The accepted input subset is canonical textual
DIMACS/DRAT with one clause per line, a single first DIMACS header and zero
terminators. No binary DRAT or arbitrary multiline DIMACS support is claimed.

The wrapper uses `command_deadline.py` and the Linux outer
`run_compute_command.py`. Build, parsing, input/output hashing and retained-prefix
copying all share the outer allowance and one shorter immutable preparation
deadline. No scientific solver runs in this workflow. The native parser receives
a remaining-time bound and inherits the outer process group. Explicit parser
address-space guard, no automatic retry/resume, immutable outputs and failure
records are required. Fresh independent semantic controls gate substantial
preparation; old solver/proof gates do not approve this changed transform.

Build uses observed pinned Ubuntu g++13.3.0-6ubuntu2~24.04.1,
`/usr/bin/g++` SHA1353e9bdd29a7295c7226bf6c63abccce056d8cac31f112e5cdbecc3f28c2769,
flags `-std=c++17 -O2 -Wall -Wextra -Werror`. Record source hash, exact compiler
command/version, compile stdout/stderr/receipt and new binary hash. No historical
120-second build default applies. Suggested first engineering allocation:
outer180s/producer150s, reflecting one small translation unit and tiny controls.

Suggested substantial preparation allocation, subject to independent controls:
outer960s/producer900s/parser800s,8 GiB address-space guard and fresh disk reserves.
The two inputs total431.5 MB; clauses/literals are parsed once. Memory is expected
to be hundreds of MB to a few GiB from the pool, clause/index records and bucket
allocation, but this has not been measured. No success likelihood or guaranteed
speedup is asserted. Stop and compare with a simple newly allocated1800-second
base run if actual parsing/resource costs make migration unhelpful. Six hours
is a ceiling and independent command allowances are not accumulated.

The preparation plan schema `DRAT_RESTART_PREPARATION_PLAN_V1` requires question,
scope, success_criterion, falsification_criterion, independent_verification_criterion,
baseline_and_uncertainty, source_commit and checker_profile, plus artifact
descriptors(path/sha256/bytes) for original_cnf, original_partial_proof,
historical_native_receipt and encoding_gate. Root freezes the plan before launch.
Modes: build,controls,preflight,prepare. `prepare` requires fresh gate status
`INDEPENDENT_DRAT_RESTART_PREPARATION_V1_PASS` binding all new/shared code/spec/env,
exact profile source and newly built parser binary. Preflight launches no parser.

Twelve controls cover deleteone versus deleteall, repeated clauses, duplicate literals,
missing deletions, ignored unit deletions, truncation, an EOF-terminated valid
clause, malformed internal records, extra variables and tokens after zero.
Independent reviewers use a different Counter-based implementation and complete
truth tables on tiny fixtures. They must reject corrupt derivative clauses,
changed profile/counts, wrong prefix boundaries and altered sources. Tiny
UNSAT original four-binary-clause fixture, prefix `-2 0\n`, and suffix
`1 0\n0\n` permit independent full DRAT replay of both suffix-on-restart and
combined-proof-on-original. Wrong suffix/input and missing reasoning must fail.
Producer controls are raw outputs pending independent approval.

After independently checking exact byte transformation, root may allocate a new
proof-producing solver on `restart.cnf`. Preserve its complete raw suffix trace.
Then create a NEW combined proof from the retained original prefix plus the new
suffix, with exact hashes/lengths and boundary accounting. A restart UNSAT result
counts only after complete independent replay of the entire combined proof
against the **original** CNF, with independently checked target encoding/coverage.
That final checker is authoritative even when prefix validity remains unknown.
For a restarted SAT result, independently check its raw assignment against the
original CNF and decode/check the complete99 graph. A plain DRAT prefix lacks
model reconstruction witnesses, so a model of the extracted state alone is
insufficient. Optional complete forward-prefix checking can establish a
DERIVATION in its explicitly tested checker mode; that is not a refutation.

Primary sources accessed2026-10-02: [DRAT-trim README](https://github.com/marijnheule/drat-trim)
documents multiset deletion and ignored unit deletions; the exact local pinned
source defines this project's checking profile. [Migrating Solver State,
SAT2022](https://doi.org/10.4230/LIPIcs.SAT.2022.27) distinguishes proof-state
migration from reconstructing original SAT assignments. Those sources guide
engineering; they do not establish correctness of this new implementation.
