# Eight-coordinate GPU retry after import guard failure

Preregistered 2026-09-30 JST, before the retry. Preserve run01, which returned
code 2 before producing any checkpoint because the frozen native input cap was
2 GiB. Its six missing-checkpoint records are skipped attempts, not bounds.

The exact audited binary remains unchanged: SHA256
`eab22693fbb961fda88bc0401e53f19b3976ecc539b9c1269ad95bfc647b6ea7`.
The necessary moment LP, its complete-domain and matching-filter dependencies,
and full export-mapping audit remain unchanged. No mathematical claim depends
on numerical trajectory agreement.

Only native admission guards change in a separate source/executable: file cap
2 to 8 GiB, variable cap 1 to 2 million, and per-model/aggregate nonzero cap
100 to 200 million. The generation receipt records exact byte substitutions;
all kernels, integer index types, transpose validation and acceptance thresholds
remain byte-identical. The new native executable must pass an independent
source-delta audit, parser boundary/corruption controls and the four original
CPU comparison cases before this run. That audit is engineering evidence for
those cases only, not a full-model numerical stability theorem.

The retry retains all original settings and limits: one cold run, checkpoints
1000, 5000, 10000; binary64, eta 0.9, theta 1, 60 projection bisections,
256 threads per simplex; 600 seconds for the native process. The original
fixed tolerances and six exact support attempts are unchanged. Every failed,
missing, nonpositive or positive attempt is saved. Any meaningful exact bound
requires independent evaluation from the raw neighborhood lists.

Resource observations must show at least 8 GiB host free, 8 GiB GPU free and
12 GiB disk free before launch. Observations are not reservations. The output
is a fresh `run02`; original run and audits remain intact. This is a conditional
family experiment and cannot by itself decide Conway-99.
