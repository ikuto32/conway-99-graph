# Seventeenth milestone: a restricted exclusion and broader colouring search

The frozen ledger has 171 claims, comprising 169 VERIFIED/CLEAR and two
CANDIDATE/CLEAR. The [cyclic registration](../acceleration/results/20260930_seventeenth_cyclic_registration/summary.json)
and [model/projection registration](../acceleration/results/20260930_seventeenth_model_projection_registration/summary.json)
add six claims. One fixed-support cyclic-factor subclass is excluded by a
complete independently replayed DRAT proof. The broader fixed-support
colouring problem remains UNKNOWN. Neither result excludes the six-prism
core or resolves Conway99. Overall search coverage: UNKNOWN; no validated
denominator. There is no target graph or general nonexistence proof awaiting
external review. Direct binary MIP and coupled-count work belong to the next
cohort and are excluded from this publication.

Use the pinned root environment and fresh output directories. Prior raw
inputs and the new proof/large formula inputs can be reconstructed as follows:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv sync --locked --cache-dir .uv-cache-20260917
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/recover_20260930_twelfth_inputs.py
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/recover_20260930_thirteenth_inputs.py
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/recover_20260930_sixteenth_inputs.py --receipt build/seventeenth-prior16-recovery-new.json
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/recover_20260930_seventeenth_inputs.py --receipt build/seventeenth-recovery-new.json
```

The new helper verifies three package manifests and reconstructs six gzip
artifacts: the cyclic CNF/model, complete cyclic proof, and broader ordered
CNF/body/model. It also copies eight exact checker source/build records from
their prior public locations into the historical build paths. A fresh
destination replay completed for all 14 files, totalling 202,956,314 bytes.
It checks every part, full compressed stream and raw length/hash and refuses
to overwrite different bytes. It supplies no executable and does not
reconstruct the incomplete ordered-search trace. All newly public parts are
below 10 MiB. Recovery establishes byte identity, not proof validity.

The cyclic construction imposes an extra condition: each triple of identical
coordinate-support columns is coloured by c, c+1 and c+2 modulo three.
Phases can be normalized within this subclass, yielding 20 domains of 30
choices. This is not a normalization of arbitrary factors, and does not
assume an automorphism of any residual graph or target. The exact full Gram
is equivalent within the subclass to 180 coordinate-pair difference counts.
All 1,770 outside-column caps are retained. Independent reduction checking
includes the 90-to-30 phase mapping and the full lifted cap predicates.

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_cyclic_reduction.py --out build/seventeenth-cyclic-reduction
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_cyclic_factor_cnf.py --reduction-gate acceleration/results/20260930_independent_review/hadamard_six_prism_cyclic_reduction/summary.json --reduction-gate-sha256 7b9d988b946284d7a9fbcccccf1c2f32592dbdeb2e30cb6201e1565ea75d4de1 --out build/seventeenth-cyclic-cnf
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_cyclic_factor_object.py calibrate --out build/seventeenth-cyclic-object
```

The actual cyclic formula has 26,360 variables, 122,394 clauses and 600
primary selectors. Complete clause reconstruction and separate object
calibration precede the native attempt. Controls distinguish genuine
243-vertex raw-factor checks, local colour selection and synthetic full-size
assignment/CNF checks; no complete research factor is invented.

CaDiCaL 1.9.5 returned UNSAT with exit 20 after 55,028 conflicts, 5.40 native
wall seconds and 5.453 wrapper seconds. The complete 29,697,087-byte ASCII
trace has SHA256
51d67cf0f60365e01a744d2066e0999e944c27a56e3024a73dd5135b000e6ed9.
Its public gzip package is 6,957,691 bytes. The independent authenticated
DRAT checker accepted the whole trace in 8.859 seconds; a positive small
proof and four corrupted proof/formula controls were also checked. The
exact formula hash is
e0895d94060a8d8b25adb78cf298b4b6f6f94f8c89ac242c180c1e4b320580d8.
The [complete proof audit](../acceleration/results/20260930_independent_review/hadamard_cyclic_unsat/summary.json)
and its [named dependencies](../acceleration/results/20260930_independent_review/hadamard_cyclic_named_dependencies/summary.json)
bind the input, representation, scope, proof, solver and checker. This is a
VERIFIED exclusion of the cyclic subclass of one fixed support, not a
whole-support, whole-core or unrestricted exclusion.

With the exact historical native/checker tools present, replay the complete
authentication and proof-control path:

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_cyclic_unsat.py --out build/seventeenth-cyclic-proof
```

The saved checker binary is LOCAL_ONLY. The recovery helper supplies its
public source, portability patch, original build commands and records, not
the executable. The historical audit also authenticates compiler/environment
paths and native binary bytes. Therefore that exact wrapper cannot be
promised to run on a fresh machine. A separately rebuilt DRAT checker can
check the recovered mathematical input and trace directly; record its own
source/toolchain/hash and result rather than changing historical provenance.
The preserved source is pinned to upstream drat-trim commit
2e3b2dc0ecf938addbd779d42877b6ed69d9a985, with the disclosed Windows timing
portability patch. The dirty tools submodule was not rewritten. The
[original checker build records](../acceleration/results/20260930_rook_sat_independent_proof/checker_build/build_manifest.json)
and [native build records](../acceleration/results/20260930_native_cadical195_build/manifest.json)
provide exact build commands. Rebuilds on different toolchains require fresh
calibration and need not reproduce binary hashes.

The broader model keeps all 90 colourings in each of 60 columns. Its only
label normalization sorts the three selected option ranks within each of
the 20 identical-support groups, justified by the previous independent
relabelling proof. It has 5,400 selectors, all 60 one-hot and 666 Gram
equalities, all 1,770 column-cap relations, and 163,800 clauses for 40 adjacent
rank-order pairs. The resulting formula has 595,464 variables and 3,336,642
clauses. Every one of 14,337,000 option pairs was checked when constructing
the 930,798 cap clauses. No cyclic restriction is present and D is absent.

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_prism_ordered_cnf.py --out build/seventeenth-ordered-cnf
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_prism_ordered_object.py calibrate --out build/seventeenth-ordered-object
```

Independent checking reconstructs every actual clause and all rank segments,
and separately tests the entire native assignment/parser path and raw
factor validation. Its genuine 243-vertex positive control, local-codec
positive and synthetic full-size codec are explicitly separate. No positive
research factor follows from them. The earlier connected-01 fixed-support
checker preparation is retained as a dependency only; it is not retrospectively
promoted into a completed audit or a search result.

The broader native attempt ended UNKNOWN under the 300-second wall timeout:
GNU timeout returned 124, with no claimed native exit code, 525,037 observed
conflicts, 299.99 native wall seconds, 283.66 native CPU seconds and 300.047
wrapper seconds. Both attempts were limited to two million configured
conflicts, 4 GiB address space and a 10 GiB proof file, with a 320-second outer
guard and no automatic retry. These are configurations and observed values,
not performance guarantees. The broader 350,457,856-byte retained trace is
LOCAL_ONLY and incomplete, with no public recovery and no UNSAT proof.
Its SHA256 is
9f7182a2876e3381c888a3cf8f71baa59839828cd7790ed9da707c45ab5fb914.
No SAT object was produced. With that exact local trace, replay the outcome
audit without running a solver:

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_prism_ordered_outcome.py calibrate --out build/seventeenth-ordered-outcome-controls
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_prism_ordered_outcome.py audit --summary-sha256 df6925e7b7d7d5758633499df9690f51cf61b95fd2e5e878a9c004d3b7dcb7ef --out build/seventeenth-ordered-outcome
```

The exact triplicate-count study examines weaker projections independently
of both solver outcomes. For each coordinate/fibre in a full factor, its ten
group counts satisfy eleven saved integer marginal equations. All twelve
incidence matrices have rational rank six. Nonconstant bounded integer
count witnesses satisfy those equations and have 120 separate local group
realizations; no joint full-factor realization follows.

The complete local universe has 117,480 increasing triples of the 90 words.
Exactly 31,110 pass all local Gram upper bounds and the three column caps;
150 of those balance every coordinate as (1,1,1), and 30 are cyclic triples.
The local balanced-noncyclic witness refutes only a local implication from
balance/caps to cyclicity. The unbalanced witnesses do not decide whether
complete factors force balance. These are local counts, not fractions of
graphs or remaining target search coverage.

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_triplicate_counts_v2.py --out build/seventeenth-triplicate
```

The first independent checker read a wrong field name; its source/failure and
the explicit correction are preserved. The v2 checker used the unchanged
raw producer artifacts and independently enumerated all local triples.
No failed calculation or unavailable proof was treated as a refutation.

The [explicit publication catalog](../acceleration/results/20260930_seventeenth_artifact_packaging/catalog.json)
binds the two-step registration chain and the exact six new claims, verifies
recursive raw hashes and package reconstruction, and checks current Git
byte preservation for the selected public files. Its ignore proposal lists
three recoverable broader-formula inputs, the recoverable complete cyclic
trace, and the single unrecoverable partial trace. All source and failed
records are retained. Source/build record availability is distinguished from
executable availability. Prepared inventories do not themselves publish
artifacts or verify mathematics; publication receipts establish availability.
All research runs in this cohort have ended. Any saved process observation
is historical, not a claim that research is currently running.
