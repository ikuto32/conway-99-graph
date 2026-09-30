# Fourteenth milestone: bounded factor search and exact local encodings

The three registration records add eight revision-1 claims to the frozen
138-record ledger (136 VERIFIED/CLEAR and two CANDIDATE/CLEAR): four GPU calibration/saved-state/resume records, the ordered
matching-pair normalization, one finite modular perturbation record, the
fixed-six-prism column-cap encoding and the cooling saved-state record. These
are registered results, not eight target exclusions. The target remains UNKNOWN;
there is no target graph or general nonexistence proof awaiting external review.
The later GF2 maximum-rank lemma, connected-core portfolio and v4 annealer are
excluded from this publication cohort.

The exact claim/evidence bindings are in
[GPU registration](../acceleration/results/20260930_fourteenth_gpu_registration/summary.json),
[pair/modular registration](../acceleration/results/20260930_fourteenth_pair_modular_registration/summary.json)
and [factor-results registration](../acceleration/results/20260930_fourteenth_factor_results_registration/summary.json).
The registrars record mappings and schema checks; they are not independent
mathematical verifiers. Historical sources, commands and failed versions are
preserved without rewriting their records.

Use the pinned repository environment and fresh output directories. Recover
the authenticated prior inputs and this cohort's exact raw inputs first:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv sync --locked --cache-dir .uv-cache-20260917
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/recover_20260930_twelfth_inputs.py
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/recover_20260930_thirteenth_inputs.py
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/recover_20260930_fourteenth_inputs.py --receipt build/fourteenth-recovery-new.json
```

The last helper verifies 227 packages and refuses to overwrite differing bytes.
Of these, 224 are raw GPU chunk/checkpoint JSON files:269,122,480 bytes are
represented losslessly by19,395,832 bytes of gzip. The originals remain local;
every compressed public part is below10MiB. The other packages cover the pair
formula and cap model/formula. Package manifests bind raw sizes, SHA256 values,
compressed identities and ordering. Hash identity and decompression are not
mathematical verification. Prior dependencies explicitly include four raw
inputs recovered by the twelfth guide and the first-choice formula recovered
by the thirteenth guide.

The v2 annealer operates on fixed-core factor permutations with the exact
integer objective `TRIANGLE_FACTOR_CROSS_GRAM_SQUARED_V1`:
`E = sum_(g<h) sum_(r in g,s in h) (F_r dot F_s - K_rs)^2`.
Each free fibre permutes its complete nonmatching-pair catalogue across the
60 outside columns; fixed C0, row/column margins and within-fibre Gram entries
are retained. There are 432 cross-fibre squared-error terms at n=12. Lower
values are better within this same objective and domain. Positive error is not a factor,
and zero would still require independent raw-factor and target-extension
checks. CPU/GPU finite controls, known SRG243 positives, corrupted fixtures and
native split/checkpoint controls are preserved. The failed v1 compile (one
missing closing parenthesis; no executable launched) is included, not silently
replaced by v2. Independent replay commands are:

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_factor_permutation_annealer.py --out build/fourteenth-native-calibration
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_factor_annealer_pilot.py --out build/fourteenth-pilot-states
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_factor_resume_v3.py --out build/fourteenth-resume-review
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_factor_cooling_v3.py --out build/fourteenth-cooling-states
```

These scripts bind the saved native executable hash. A checkout alone does
not supply that local binary. The saved CUDA source, builder and calibration
manifests record the original nvcc/MSVC/GPU details. On a compatible Windows
CUDA/MSVC installation, the explicit build command is:

```powershell
powershell -File acceleration/build_factor_permutation_anneal_20260930_v2.ps1 -Architecture sm_89
```

The builder refuses to overwrite an existing executable. A new toolchain may
produce a different binary; do not alter historical hashes or claim exact
historical binary replay. Fresh native runs then need their own provenance
and independently accepted calibration. The raw integer saved-state checking
path is distinct from rerunning the hardware computation. No native speedup
claim is made.

The original six-case pilot saved786,432 proposal records over96 chains in
two fixed cores. Independent checking covers48 chunk-best objects,192 final
current/best objects and all1,536 checkpoint scores, not every native transition.
The report's premature `PUBLIC` availability label is superseded by its
[explicit correction](../acceleration/results/20260930_independent_review/factor_annealer_pilot_availability_correction/summary.json);
the original report remains unchanged. Immutable publication is established
only by a later publication receipt.

The first cooling wrapper failed twice before native invocation: tuple-valued
edge pairs compared unequal to their JSON list representation. The failed
batch, diagnosis and v2-applicability addendum are retained. The narrow v3
wrapper canonicalizes that representation while preserving native algorithm,
binary and saved states. Its actual public resume calibration compares23+41
steps with64 steps, including permutations, RNG, current/best scores and
proposal counts, and rejects corrupted resumes.

The successful cooling continuation uses32 existing chains, sequential
temperatures0.25 then0,16 chunks of1,024 proposals per stage and four completed
stages, for1,048,576 additional saved proposals. Independent saved-state review
checks64 chunk-best objects,128 stage-final objects, all2,048 checkpoint scores
and continuity from the old T1 checkpoints. It does not replay all research
transitions. The minima are134 then124 for shift6 and146 then142 for six-prism.
There is no saved zero-error factor. Temperature changes and different cores
do not establish a runtime comparison or target-wide progress percentage.

The ordered-pair normalization preserves arbitrary M1/M2 choices up to harmless
simultaneous coordinate and canonical-C0-column relabelling. It composes10,395
first-stage transports with114,345 second-stage transports over the frozen
3,580 ordered representatives; P remains arbitrary. This covers all
108,056,025 ordered matching pairs without materializing that full product.
No automorphism of a hypothetical target is assumed. The extended formula
has114,484 variables and561,121 clauses and remains a necessary factor model,
with no residual adjacency D. The initial independent checker confused a
universe index with an orbit ordinal; its failure and v2 correction are both
preserved, with no producer artifact changes.

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_variable_core_pair_orbits_v2.py --out build/fourteenth-pair-encoding
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_variable_core_pair_object_wrapper.py --out build/fourteenth-pair-object
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_triangle_modular_kernel_finite.py --out build/fourteenth-modular
```

The finite modular route independently reconstructs128 deterministic trials
over GF2 and128 over GF3 on the243-vertex control. All retain compatibility
with their own mixed right-hand side. This is a saved finite outcome, not a
universal kernel theorem or a binary factor construction. The original
successful perturbation matrices were not saved; the independent audit
supplies reconstructed vectors/hashes and discloses that limitation. The
producer's post-run control timing is preserved.

The pair native attempt ended UNKNOWN at5,000,002 observed conflicts against
5,000,000 configured, native wall872.48 seconds and CPU870.15 seconds. Its
5,621,796,493-byte partial trace was independently authenticated locally and
is not an UNSAT proof. With that exact local trace available:

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_variable_core_pair_orbits_unknown.py --out build/fourteenth-pair-outcome
```

The cap extension retains all96 choices in each canonical column of the fixed
six-prism core and the prior first-choice normalization. It adds1,440 exact
incidence channels,24,480 channel clauses and21,120 nontrivial quartic clauses
after56,640 forced-zero omissions. The complete formula has247,320 variables
and920,401 clauses and is equivalent to the original normalized factor model
plus all1,770 distinct-column overlap caps. These caps are required for target
extensions; they are not claimed to follow from abstract Gram conditions
alone. The saved overlap3 example is a two-column partial witness, not a
complete Gram-factor counterexample. The v1 count failure and v2 source/spec
failure remain preserved.

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_prism_column_caps.py --out build/fourteenth-cap-encoding
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_prism_column_caps_object.py calibrate --out build/fourteenth-cap-object
```

The object checker requires every native literal and raw clause, projects the
first245,880 values into the independently checked base path, then requires
all1,440 channel equalities and all1,770 raw column caps. Generic own-Gram
factor, cap-only positive and full-size codec controls are separately labelled;
no known complete research36 positive is invented.

Both new native protocols allow one attempt,900seconds, five million configured
conflicts,4GiB address space and10GiB proof file, with5seconds kill grace and a
920second outer guard. The authenticated CaDiCaL1.9.5/native ext4 helper and
source/checker build records are prior pinned dependencies. Exact command and
build provenance remain in each manifest. Executables and incomplete native
traces are LOCAL_ONLY; sources/build instructions do not guarantee a
byte-identical binary on a different toolchain. Any SAT factor needs the full
independent object path; any UNSAT answer needs a complete checked proof.
Neither would supply an unrestricted target conclusion for the fixed prism
core without an independently justified coverage argument.

The prior [native build record](../acceleration/results/20260930_native_cadical195_build/manifest.json)
pins official source commit `146207318796f094dcded87349a64f0c6927309e`
and its public source archive. The saved build receipt records the exact
compiler, configure and `make -j4` commands. In a fresh WSL source directory
extracted from that authenticated archive, the original build steps are
`./configure` then `make -j4`. Do not rerun the historical builder into its
existing output directory or replace the saved native executable. New build
bytes need fresh calibration; historical native gates continue to identify
only the saved binary. The native CLI and ext4 calibration records also bind
the separately built DRAT checker and document its source/portability patch.
The dirty historical checker submodule is not a substitute for that identity.

The [cap outcome audit](../acceleration/results/20260930_independent_review/prism_column_caps_unknown/summary.json)
records UNKNOWN through GNU timeout exit124 and native SIGTERM. It checked
2,374,985 observed conflicts against the five-million configured limit,
899.99 seconds native wall,896.40 seconds CPU and900.031 seconds wrapper wall.
The complete1,406,574,592-byte retained partial trace has SHA256
`156dc9c2a188952827d6f498ef35d241a2d0fa9b7f62fd1fa621ad9b0539c432`.
It is LOCAL_ONLY and is not an UNSAT certificate. The audit authenticated its
entire byte stream but did not perform DRAT proof checking. It discloses that
the execution auditor authored the cap producer; mathematical encoding review
and the object checker used the separately authored checking path. Two parser
positives and ten corrupted outcomes were tested. No factor or exclusion was
obtained. With that exact local trace available:

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_prism_column_caps_unknown.py --out build/fourteenth-cap-outcome
```

The [explicit catalog](../acceleration/results/20260930_fourteenth_artifact_packaging/catalog.json)
checks the frozen registration chain, exact allowlist, recursive input/output
hashes and all lossless packages. Its first preparation attempt treated the
deliberately false model hash in the pair-wrapper corruption fixture as an
authentic evidence binding. The failed executing source and receipt are
preserved. The correction authenticates that exact control's bytes, real
model hash and independent rejection report; no generic zero-hash exception
is used. At the frozen138-claim registration state, replay with:

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/package_20260930_fourteenth_catalog.py --out build/fourteenth-catalog-recheck --caps-audit acceleration/results/20260930_independent_review/prism_column_caps_unknown/summary.json --caps-audit-sha256 fc1c8b926e62a2eae9e56b2507e772c8b6fc15d62a1b95d6735fa70701d03fdf --caps-audit-status INDEPENDENT_SIX_PRISM_COLUMN_CAP_UNKNOWN_RUN_AUDIT_PASS --caps-audit-source acceleration/audit_20260930_prism_column_caps_unknown.py
```

Catalog/schema checks are bookkeeping, not mathematical verification. They
also require the exact local native traces/tools identified by the catalog;
public package recovery cannot recreate an unavailable incomplete trace.
New checks must use fresh output directories; completed experiments,
registrars and frozen outputs must not be overwritten. No process is claimed
currently running from its historical checkpoint or receipt.

Overall search coverage: UNKNOWN; no validated denominator.
