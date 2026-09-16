# Source150 macro `(2,0)` exact shard audit

Status: `SOURCE150_M2_EXACT_SHARD_AUDIT_PASS` once the companion audit is
replayed.

The five nonoverlapping shards cover all 576 canonical local-graph orbits of
source150 macro `(2,0)`, with total labelled coverage 262,144.  Every branch
is UNSAT in the exact synchronized recurrence / ordinary-fibre pair local
CSP; no SAT or UNKNOWN branch is counted as excluded.

This is exact solver-free finite enumeration, not a DRAT certificate.  It
closes this one macro only and does not by itself close source150 or the full
`E0=72` layer.  The JSON audit binds every shard and the frozen producer
inputs by SHA-256 and records each canonical mask and orbit mass.
