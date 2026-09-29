# Bounded independently gated exact Gram SAT loop

Status: preregistered CANDIDATE experiment. This supersedes the unexecuted
one-round plan in `theory_20260930_rook_lazy_cut_spec.md` for the next launch;
no past run or threshold is changed.

Scope remains the exact central matching and four incidence blocks in the
independently audited 780-edge model. Base CNF SHA-256 is
`ed9d0e102b16481fdbcecef34240b5be2b8a357af8c219606bb688dcb5fe9403`.
The first candidate added clause is the independently reviewed minimized
Gram certificate `255560186ad410e57582ab34c1b7cb90b899b4d9656ce37285bc06ce98b1145a`.
Every later clause must pass the same independent exact checker before use.

Each round materializes exactly the base CNF with its header count increased
by the number of ordered accepted cuts and those clauses appended verbatim.
It records the full augmented CNF hash. Public replay can recover the exact
input from the base gzip and the ordered clause record. Each fresh CaDiCaL195
invocation produces a complete model or raw DRAT trace. Solver-internal
learning is not reused across rounds, so proof replay binds one explicit
augmented instance without an incremental-proof bookkeeping assumption.

After SAT, the separate checker reads every raw augmented clause and
independently decodes and checks the full59 graph. Only a successful result
permits the rational Gram falsifier to run. A negative G=27I-9A+J direction
is reduced by the bounded greedy minimizer; its coefficient-based support
nogood then goes to the independent cut checker. A veto stops the run and
preserves the rejected artifact. Calling an independent checker from the
producer does not permit the discovery agent to promote its own claims or
assert external review.

Limits: at most **10 solver rounds**, at most **180 seconds cumulative solver
process wall time**, at most **60 seconds per solver invocation**, at most
1,000,000 conflicts per invocation, and **600 seconds overall wall time**.
Each minimization retains its 120-second/three-pass local limit but also
cannot justify extending the wave's overall budget. Save all completed
assignments, local graphs, Gram certificates, checker outputs, cut lists,
input hashes and process receipts. Checkpoint after each accepted cut and
before starting another solver.

Stop reasons are explicit: first UNKNOWN/error/cap; independent-check veto;
UNSAT awaiting independent proof replay; a full local Gram survivor; a Gram
obstruction needing a different cut kind (rank or A+4I alone); or the round/
resource budget. None is a Conway99 resolution or a genuine external blocker.
A stopped wave has no running search. A later wave can resume from the exact
ordered accepted-cut checkpoint in a new output directory with a separately
recorded resource budget. No recursive solver stack is claimed resumable.

An UNSAT result may only exclude this fixed-central-star family after an
independent complete proof replay and binding of all mathematical cuts to
their checked necessity. A SAT local Gram survivor is still only a necessary
59-vertex window, with 40 external vertices missing. Overall target-wide
coverage remains UNKNOWN; no validated denominator.
