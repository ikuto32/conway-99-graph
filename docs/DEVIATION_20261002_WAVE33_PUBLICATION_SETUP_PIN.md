# Wave33 publication setup pin correction

The first publication confirmation invocation, `20261002_wave33_public_confirmation_supervision01`,
exited before remote/Git/package checking or ledger mutation. The root researcher
mistyped the `--previous-sha256` argument. The exact-input guard rejected it with
`ValueError: exact frozen324 ledger`. Its original argv, logs, supervisor receipt
and empty output directory are preserved.

The unchanged v1 source was invoked again in separate `...supervision02` and
`...confirmation02` directories. This invocation read the exact ledger hash from
the frozen `20261002_wave33_registration08/summary.json` field, rather than manually
transcribing it. It completed the declared public-byte/recovery checks and updated
availability only. The second command has its own per-invocation deadline.

These are two setup attempts for one publication confirmation, not two scientific
experiments. No proof was replayed, no claim statement changed and no exclusion
was added. Independent transition review remains separately required.
