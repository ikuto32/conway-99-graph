# Fifteenth milestone: four-core construction, modular constraints and coarse columns

The four registration records add ten revision-1 claims to the frozen ledger:
148 claims, comprising 146 VERIFIED/CLEAR and two CANDIDATE/CLEAR. The new
records concern exact scoped lemmas, finite calibration and saved-state
checks, four fixed-core encodings, and the fixed coarse-column model. They do
not establish target nonexistence. Target resolution remains UNKNOWN, with
no complete target graph or general nonexistence proof awaiting external
review. Overall search coverage: UNKNOWN; no validated denominator.

The exact claim bindings are in the
[preparation registration](../acceleration/results/20260930_fifteenth_preparation_registration/summary.json),
[modular registration](../acceleration/results/20260930_fifteenth_modular_registration/summary.json),
[coarse-domain registration](../acceleration/results/20260930_fifteenth_coarse_registration/summary.json)
and [bit-lift registration](../acceleration/results/20260930_fifteenth_bitlift_registration/summary.json).
Registration/schema checks do not replace mathematical verification. This
cohort excludes the later identity-P factor lemma and 64-bit-flip normalization.
Historical environment records and failed versions remain unchanged.

Use the locked repository environment and fresh replay output directories.
Recover prior authenticated dependencies and the new raw GPU records first:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv sync --locked --cache-dir .uv-cache-20260917
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/recover_20260930_twelfth_inputs.py
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/recover_20260930_thirteenth_inputs.py
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/recover_20260930_fourteenth_inputs.py --receipt build/fifteenth-prior-recovery-new.json
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/recover_20260930_fifteenth_inputs.py --receipt build/fifteenth-recovery-new.json
```

The final helper checks the authenticated
[192-file package manifest](../acceleration/results/20260930_fifteenth_gpu_trace_packages/artifact_packages.json):
230,795,348 raw bytes are represented by 15,655,596 gzip bytes. Each public
part is below 10 MiB. It checks compressed and raw hashes and lengths, confines
destinations to the workspace, and refuses to overwrite differing bytes.
The raw files remain available locally; public replay reconstructs them
losslessly from the packages. A fresh-directory recovery was also executed.
Hash/decompression success establishes artifact identity, not mathematical
correctness. The five native partial traces are separately LOCAL_ONLY, have
no public recovery package, and are not proof certificates.

The connected-core selection scans the frozen 3,580 ordered matching-pair
representatives with P=I. For each first-matching stage in increasing order,
it takes the first second-matching representative yielding a connected
36-vertex core, then selects the first four qualifying stages. All 3,580
eligibility decisions were independently checked; 2,806 are connected. The
selected (stage, second-orbit ordinal, global pair index) values are
(0,10,10), (1,42,53), (2,69,131), and (3,66,234). Literal 39-vertex local
pair caps, all selected prescribed Gram coefficients and canonical C0
catalogues were checked. P=I and these four cores are deliberate restrictions;
no target automorphism or exhaustive construction coverage is assumed.

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_connected_identity_cores.py --out build/fifteenth-core-selection
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_factor_portfolio_v4.py --out build/fifteenth-v4-calibration
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_connected_core_portfolio_states.py --out build/fifteenth-portfolio-states
```

The v4 wrapper enables only the four hash-bound new cores in addition to the
previous two domains. It preserves the v2 native algorithm and the v3 JSON
resume correction. Independent finite calibration checked 2,048 GPU proposal
occurrences across original and fresh two-chain 23+41 versus 64 step runs,
with CPU parity, raw-object checks, RNG/state carry and corrupted gate/resume
controls. That count includes repeated trajectories, not 2,048 distinct
factors. Floating-point annealing acceptance is heuristic.

The saved portfolio ran 64 continuing chains, 16 per core, through three
temperatures 1, 0.25 and 0. Its 12 completed phases and 96 chunks contain
1,572,864 new proposal records. Independent saved-state checking covers
96 chunk-best objects, 192 phase-final current objects, 192 phase-final best
objects, all 1,536 checkpoint-current scores and all 1,536 checkpoint-best
scores, plus exact inter-phase carry. It does not replay every research
transition. The 192 phase-chain endpoints represent the same 64 chains.

The exact objective is `TRIANGLE_FACTOR_CROSS_GRAM_SQUARED_V1`, the sum of
squared integer errors over the three 12-by-12 cross-fibre Gram blocks.
C0 stays canonical and each unknown fibre permutes its complete 60-column
nonmatching-pair catalogue, preserving within-fibre Grams and margins.
Lower scores are better within the same fixed-core domain. The phase minima
are 168→154→140, 170→134→132, 172→146→128 and 166→144→134 for cores 00–03,
respectively. No saved object has zero score. These values are heuristic
objective scores, not mathematical lower bounds or exclusions; comparisons
between different cores do not measure target-wide progress. Even zero would
require independent full-factor, outside-cap and residual-D checking.

The v4 calibration invokes the saved local CUDA binary. A checkout does not
provide that executable. Its exact source, original builder, toolchain and
hardware records are retained in the prior cohort. See the
[fourteenth replay guide](REPRODUCING_20260930_FOURTEENTH_WAVE.md) for the
explicit build procedure and binary-provenance limitations. Fresh builds
can differ in bytes and require fresh calibration; do not rewrite historical
hashes. Saved-state integer verification is distinct from repeating native
GPU computation. No performance guarantee is claimed.

The GF2 maximal-rank lemma establishes compatibility of the mixed *linear*
equation FD=H under its explicit maximal-rank and cell-kernel hypotheses.
D here is an arbitrary field matrix; it is not asserted symmetric, binary,
regular or compatible with the residual quadratic identity. The five-core
study uses the four selected cores and the known 243-vertex positive control.
Independent checking reconstructs raw prescribed Grams, replays exact
row-operation certificates and uses a separate pivot path for ranks and
kernel/action completeness. In that order, Gram ranks are 22,24,24,26,30 over
GF2 and 27,29,29,29,27 over GF3. These Gram ranks do not force the maximal
factor rank. The audited kernel-invariance criterion is conditional; the
three specified connected cores 01–03 have the recorded GF3 linear
compatibility consequence. No binary residual graph follows. The 243 control
is not evidence for a 99-vertex graph.

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_triangle_gf2_maxrank.py --out build/fifteenth-gf2-maxrank
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_five_core_modular_gram.py --out build/fifteenth-five-core-modular
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_connected_fixed_core_cnf.py --out build/fifteenth-fixed-core-encoding
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_connected_fixed_core_object.py calibrate --out build/fifteenth-fixed-core-object
```

Each of the four fixed-core formulas has 110,904 variables and 518,184 clauses:
the independently checked arbitrary-core factor formula plus 24 positive
matching/permutation units. These are necessary factor models with no
residual D. The preserved original encoding audit used a nonexistent shorthand
dependency ID; the separate
[claim-binding correction](../acceleration/results/20260930_independent_review/connected_fixed_core_claim_binding/claim_binding.json)
identifies the existing unrestricted factor-encoding claim and unchanged
premise gate. Its mathematical statement and formula bytes did not change.

The new coarse template comprises all 90 balanced assignments of six prism
components to three fibres, minus the exact prior 30-word template. All 60
remaining words occur once. For each of 18 component/fibre positions, the
complete domain of weight-10 words on its 20 columns was enumerated under
the exact marginal equations. Independent exhaustive checking finds 136
survivors per domain, after 184,756 candidates per domain. The 3,325,608
tested local words and 2,448 surviving local words are not full factors or
disjoint fractions of target graphs. The older doubled-30-pattern exclusion
does not exclude this new template.

The exact bit-lift model has 5,238 variables and 85,698 clauses: one selected
word per domain, 360 actual bit channels, all 135 inter-domain Gram relations
and all 1,770 outside-column overlap caps. The independent audit checks every
actual clause and all 2,496,960 compatibility pairs. No bit or symmetry
normalization is added. Its scope is precisely this fixed 60-word template;
it contains no residual D. Object calibration checks complete native/JSON
assignments, all raw clauses, the decoded factor and its bijective C0
reordering. Positive 243-vertex and synthetic codec controls are explicitly
separated from unavailable complete research factors.

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_prism_coarse_complement.py --out build/fifteenth-coarse-domains
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_prism_coarse60_bitlift_cnf.py --out build/fifteenth-coarse-cnf
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_prism_coarse60_bitlift_object.py calibrate --out build/fifteenth-coarse-object
```

All five native attempts finished UNKNOWN, with no SAT object or complete
UNSAT proof. Each allowed one native call, 300 seconds, two million configured
conflicts, 4 GiB address space and a 10 GiB proof-file limit, with five seconds
kill grace and a 320-second outer guard. Observed counters may slightly
exceed the configured conflict cap. Exact commands, versions and source/binary
identities remain in the manifests and independent outcome audits.

| Attempt | Observed conflicts | Native wall seconds | Retained partial-trace bytes |
| --- | ---: | ---: | ---: |
| Connected core 00 | 2,000,002 | 158.60 | 941,047,064 |
| Connected core 01 | 2,000,000 | 174.21 | 1,026,174,428 |
| Connected core 02 | 2,000,000 | 118.06 | 839,104,290 |
| Connected core 03 | 2,000,001 | 171.60 | 1,025,824,181 |
| Coarse 60 bit-lift | 2,000,000 | 139.90 | 2,330,193,949 |

Every retained trace was freshly hashed completely by its outcome auditor;
none was checked or accepted as an UNSAT certificate. The initial fixed-core
outcome parser rejected the native conflict-limit annotation. Its original
source, positive calibration and failed core-00 audit are preserved. The v2
parser accepts only the exact matching annotation and adds corrupted controls.
This corrected an engineering parser, not a mathematical claim. With the
exact local traces available, replay the outcome audits without any solver:

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_connected_fixed_core_native_outcome_v2.py calibrate --out build/fifteenth-fixed-outcome-controls
0..3 | ForEach-Object {
    $coreIndex = $_
    $runSummary = ('acceleration/results/20260930_connected_fixed_core_native_{0:D2}/summary.json' -f $coreIndex)
    $summaryHash = (Get-FileHash -LiteralPath $runSummary -Algorithm SHA256).Hash.ToLowerInvariant()
    uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_connected_fixed_core_native_outcome_v2.py audit --core-index $coreIndex --summary-sha256 $summaryHash --out ('build/fifteenth-fixed-outcome-{0:D2}' -f $coreIndex)
}
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_prism_coarse60_native_outcome.py calibrate --out build/fifteenth-coarse-outcome-controls
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_prism_coarse60_native_outcome.py audit --summary-sha256 3f2c14a040252a83b11c1f39bba522719c11391c65b618ac5e488203cc544047 --out build/fifteenth-coarse-outcome
```

The [explicit publication catalog](../acceleration/results/20260930_fifteenth_artifact_packaging/catalog.json)
authenticates the four-step registration chain, ten claim-evidence bindings,
exact file allowlist, recursive hash references and all new gzip recovery
streams. The preserved first inventory attempt reported missing explicit
links to already-published GPU recovery records and the deliberately false
hash in a rejected wrapper-gate control. The final catalog authenticates
those prior packages and permits only that exact control exception, bound
to its unchanged bytes and independent rejection report. It also checks
that current Git attributes preserve every selected public payload byte.
Its proposed exclusions name exactly 192 packaged raw GPU JSON files
and five local incomplete traces. Saved native executables are separately
marked LOCAL_ONLY, with prior source/build provenance rather than a promise
of byte-identical rebuilding. Newly public payloads are each at most 10 MiB.
The catalog does not mutate Git, the ledger, or historical artifacts and does
not rerun mathematical checks. Immutable public availability is established
by the later publication receipt, not by a prepared inventory alone.
