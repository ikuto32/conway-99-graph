# Twenty-fifth wave: count cuts, direct-cell attempts and binary completion

This wave excludes the second literal eight-count profile and verifies a third
count-relaxation witness. It does not exclude the whole support or construct a
Gram factor, residual graph or Conway-99 graph. Four broader direct-cell attempts
returned UNKNOWN. The algebraic results retain their field and conditional
triangle assumptions. No target automorphism is assumed.

Use the existing checkout and pinned environment:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv sync --locked --cache-dir .uv-cache-20260917
```

Python3.12.10 and uv0.11.25 were recorded; the lockfile is unchanged. Every completed
run keeps its actual source commit, source hashes, command and versions. Do not
rewrite historical commands or rerun one-shot registrars/checkpoint writers.
Fresh audit outputs must have new paths. New timestamps and source-commit metadata
mean newly generated reports need not hash-identically to historical reports.

Recover earlier dependencies using the [wave24 guide](REPRODUCING_20260930_TWENTYFOURTH_WAVE.md).
The [wave25 recovery manifest](../acceleration/results/20260930_twentyfifth_raw_recovery/manifest.json)
binds eight originals totaling1,907,346,389 bytes to231 gzip parts. It includes
three CNFs, one model and four partial UNKNOWN traces. The standalone restorer
verifies existing bytes, reconstructs missing files, and refuses to overwrite
different data:

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/recover_20260930_twentyfifth_raw_artifacts.py --manifest acceleration/results/20260930_twentyfifth_raw_recovery/manifest.json --manifest-sha256 695d61b39c466660cb854377800dd036362739a4bd03ffc200bf6e35873ea45b --receipt build/wave25-recovery.json
```

Use `--destination-dir build/fresh-wave25-recovery` for a separate tree or
`--verify-only` to check streams without writing originals. The saved development
[receipt](../acceleration/results/20260930_resume/twentyfifth_raw_recovery.json)
records all eight restored into a fresh tree. Recovery establishes identity only.
Local solver/checker executables retain their recorded build identities and are
not distributed as if portable across platforms.

The second count witness satisfies the previous six-profile-cut formula. Its
full-Gram lift has9,532 variables and162,124 clauses. Independently check its
encoding and full proof, then the separate scalar obstruction:

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_eight_count_profile_lift_second.py audit --out build/replay-wave25-second-encoding
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_second_eight_count_profile_unsat.py --out build/replay-wave25-second-proof
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_second_count_scalar_obstruction.py --out build/replay-wave25-second-scalar
```

The1,269,209-byte proof has SHA256
`4d22afafcd8f9ef6629319617c9f671c97a585a4deba8ecec2072e4c1f7ac2c8`.
Its exact input `eight_count_profile_lift_second/instance.cnf` has SHA256
`dbd7b51dca52b69877888f88addc111f93f02ef52ddd58efebdc5c67e746bc87`.
The historical audit authenticates the local Windows checker build. On another
platform independently rebuild and calibrate drat-trim, retain its source/version,
binary hash and controls, then run it directly on this exact CNF and the saved
`eight_count_profile_lift_second_native_pilot/main/proof.drat`. See the prior guide
for the checker build lineage. Changing historical pins is not a valid replay.
The saved independent unit-propagation trail is additional evidence; the recorded
promotion relies on the complete independently checked proof.

The scalar contradiction uses coordinates9,11 and fibres2,1. Only five support
groups can contribute. The count restrictions force their intersections to total
at most1, while the prescribed Gram entry is2. Six ordered distinct-fibre versions
yield six25-literal necessary clauses. They use the universal binary intersection
bound, without assuming local catalogue caps or a target symmetry. Replay both the
necessity proof and its exact CNF composition:

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_second_count_partial_cut.py --out build/replay-wave25-partial-cuts
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_count_master_partial_cut_cnf.py --out build/replay-wave25-partial-cnf
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_count_master_partial_cut_sat_outcome.py --out build/replay-wave25-third-count
```

The strengthened CNF has155,939 variables and705,845 clauses, SHA256
`baca89a7014e10e1fea9fd1873ef5dde4a090ab02dfe1791b4734a196677880b`.
The independent third count profile has SHA256
`03d68bdfff62aa6f73dd44d72eab80acfdb8d001bb1b504df7aa36707b8d695e`
and profile digest `3bc6ebf9444e7a2f15af1ac85c6164119333244ced5d6dbe83a6c6b367e533d5`.
The separate outcome checker reads all native assignment variables and clauses,
reconstructs the counts, checks all twelve cuts and all540 universal upper bounds.
These540 diagnostics are weaker than exact local interval bounds and simultaneous
Gram realization. The witness is a valid object of the count relaxation only.

The direct binary-cell encodings and equal-support lex normalization have separate
complete formula and semantic reviews. Their exact replay CLI is recorded in each
hash-bound report. The main checks are:

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_direct_cell_count_cnf.py audit --out build/replay-wave25-direct-encoding
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_direct_cell_semantics.py --out build/replay-wave25-direct-semantics
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_direct_cell_lex.py audit --out build/replay-wave25-lex-encoding
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_direct_cell_unknown_trace_transport.py --out build/replay-wave25-direct-trace-transport
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_lex_unknown_trace_transport.py --out build/replay-wave25-lex-trace-transport
```

There are two base variants, each searched with and without lex ordering. All four
attempts completed as UNKNOWN under one60-second/1,000,000-conflict call per input,
4GiB address-space and10GiB trace guards. One hit the conflict limit; the other
three timed out. No UNSAT or factor result follows. Reports distinguish retained
host traces and authenticated historical transfers from later missing ext4 files.
The two transport manifests cover138 and84 gzip parts respectively. They are
partial traces and must never be supplied as claimed complete nonexistence proofs.

The independent GF(2) review is both a written derivation and a finite calibration:

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_gf2_alternating_completion_v2.py --out build/replay-wave25-gf2
```

Read [the independent derivation](AUDIT_20260930_GF2_ALTERNATING_COMPLETION.md)
and the [append-only scope clarification](../acceleration/results/20260930_independent_review/gf2_alternating_completion_scope_addendum/claim_bindings.json).
The alternating-completion theorem concerns arbitrary equal-shape F,H overGF(2).
The triangle corollary explicitly sets H=(I+C)F and assumes the stated exact Gram
identity and even cell size. Even row sums of D add a further condition. The
symmetric block-rank inequality is valid over arbitrary fields; the triangle
rank calculation is overGF(2). Rank(B)>=18 is a conditional sufficient premise
for that necessary test to be vacuous at n12, not a universal assertion.

Preserve the initial failed GF(2) checker and its correction, the original outcome
reports and availability clarification, the all-triple design's failed/corrected
inventories, and CI's exactly authenticated historical syntax-failure fixture.
The all-triple proposal's31,254,053-clause inventory remains CANDIDATE; no research
CNF was built. Schema/CI, artifact transport and repeated execution do not replace
independent mathematical review.

The milestone freezes267 claims:262 VERIFIED/CLEAR, three CANDIDATE/CLEAR and two
REFUTED/CLEAR. New records are18 verified scoped claims and one candidate design
estimate. Third-profile full-Gram work and the shared-threshold upper-envelope
inventory are later-wave continuation. Overall search coverage: UNKNOWN; no
validated denominator.
