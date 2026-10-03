# Twelfth milestone: unrestricted necessary factors and complete six-prism domains

This cohort adds four verified claims through the
[preparation registration](../acceleration/results/20260930_twelfth_preparation_registration/summary.json),
[six-prism registration](../acceleration/results/20260930_prism_all_columns_registration/summary.json)
and [linear-witness registration](../acceleration/results/20260930_prism_linear_witness_registration/summary.json).
The registered state contains126 claims,124 VERIFIED/CLEAR and2 CANDIDATE.
Target resolution remains UNKNOWN. No target-resolution artifact is submitted
for external review. Neither capped native attempt supplied a SAT object or
a complete checked UNSAT proof.

The [universal normalization proof](DERIVATION_20260930_UNRESTRICTED_TRIANGLE_FACTOR.md)
and [independent audit](AUDIT_20260930_UNRESTRICTED_TRIANGLE_FACTOR.md)
show that any target graph can be relabelled around a triangle with three
12-vertex cells and60 outside vertices. Only the first internal matching,
two cross matchings and the C0 column labels are normalized. M1, M2 and P
remain arbitrary. No nontrivial target automorphism, prism-free restriction,
commuting matchings or involutive P is assumed. The root triangle always
exists because each edge has exactly one common neighbour. This establishes
universal coverage of the necessary incidence-factor representation, not
existence of any factor or of a target graph.

The [variable-core encoding audit](../acceleration/results/20260930_independent_review/variable_core_factor_cnf_v2/summary.json)
checks all110904 variables and518160 clauses. Its1716 primary variables are
132 matching-edge choices,144 permutation entries and1440 incidence bits.
The formula includes the complete variable-core Gram equations, margins,
mixed caps and distinct-column caps. Residual D is unencoded. Every target
yields a primary solution, but a primary solution need not complete to a
target. The first checker failed on a missing metadata-key lookup before
approval; its [failure](../acceleration/results/20260930_independent_review/variable_core_factor_cnf/failure.json)
and original source are retained alongside the corrected v2 checker. The
[corruption addendum](../acceleration/results/20260930_independent_review/variable_core_factor_corruption_addendum/summary.json)
then checks seven fresh mutations of actual metadata. No frozen failed
record was overwritten.

The [six-prism encoding audit](AUDIT_20260930_PRISM_ALL_COLUMNS.md) concerns
one fixed core, with all three internal matchings standard and all cross
matchings identity. It includes every possible column support:96 per
canonical C0 label,5760 primary choices total. Its540 linear equalities are
encoded by245880 variables and874800 clauses. The complete abstract
Gram-factor problem is covered, with no earlier five-matching or complement
restriction. Its distinct-column caps and residual D are omitted. This
fixed-core equivalence must not be confused with the universal normalization
or with a proof that all target graphs contain the six-prism core.

The [exact witness audit](../acceleration/results/20260930_independent_review/prism_column_modular/summary.json)
checks a uniform rational weight1/96 for every primary choice and separate
solutions modulo2 and modulo3, each against all540 independently reconstructed
linear equations. These three relaxations are feasible. The modular
witnesses fail383 and278 integer equalities, respectively, so no integer
binary solution is inferred. Producer rank345 is not independently checked
or promoted. The audit performs no elimination and uses exact Fraction and
integer arithmetic with14 corrupted-witness controls.

Use the unchanged locked environment from the repository root (saved tools:
uv0.11.25 and Python3.12.10). Output directories below must be new. Recover
the public compressed input packages before running the auditors:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv sync --locked --cache-dir .uv-cache-20260917
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/recover_20260930_twelfth_inputs.py
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_unrestricted_triangle_factor.py --out build/twelfth-normalization
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_variable_core_factor_cnf_v2.py --summary-sha256 9a40501ab7848789ff859c2b1c29393b3df07e61e9dceee6908ebe4180a2ff19 --out build/twelfth-variable-encoding
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_variable_core_factor_corruption_addendum.py --out build/twelfth-variable-corruptions
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_variable_core_factor_object.py calibrate --out build/twelfth-variable-object-controls
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_prism_all_columns.py --out build/twelfth-prism-encoding
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_prism_all_columns_object.py calibrate --out build/twelfth-prism-object-controls
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_prism_column_modular.py --out build/twelfth-linear-witnesses
```

These commands replay exact artifact and calibration checks without launching
a research solver. The object-checker controls explicitly distinguish generic
positive fixtures from research factors. The variable-core checker includes
a known rook9 control whose outside set is empty. The six-prism checker has
a nonempty full-shape synthetic factor with its own declared Gram, which is
rejected against the research Gram. Neither calibration claims a positive
36-by-60 factor of the research instance. The later SRG243 fixture and
dynamic residual wrapper are outside this milestone.

The [variable-core native audit](../acceleration/results/20260930_independent_review/variable_core_factor_unknown/summary.json)
records one UNKNOWN conflict-capped attempt, native exit0, exactly1000000
observed conflicts,146.02 native real seconds and146.078 wrapper seconds.
The [six-prism native audit](../acceleration/results/20260930_independent_review/prism_all_columns_unknown/summary.json)
records one UNKNOWN wall-capped attempt, timeout exit124,817260 observed
conflicts,299.99 native wall seconds and300.047 wrapper seconds. Both original incomplete traces are retained locally and fully
hashed; neither was accepted as an UNSAT proof. These measured outcomes do
not establish a performance comparison between the different models.

Six raw files are LOCAL_ONLY and excluded from the public Git payload:

| Raw artifact under `acceleration/results/20260930_` | Bytes | Availability |
| --- | ---: | --- |
| `variable_core_factor_cnf/model.json` | 17,045,974 | Exact public gzip recovery. |
| `variable_core_factor_native_pilot/main/proof.drat` | 1,073,110,358 | Incomplete trace, local copy only. |
| `prism_all_columns/instance.cnf` | 17,046,975 | Exact public gzip recovery. |
| `prism_all_columns/model.json` | 17,872,207 | Exact public gzip recovery. |
| `prism_all_columns/clauses.body` | 17,046,955 | Exact recovered CNF after its20-byte header. |
| `prism_all_columns_native_pilot/main/proof.drat` | 720,744,448 | Incomplete trace, local copy only. |

The recovery helper verifies frozen package hashes, ordered compressed parts,
decompressed lengths and raw hashes. It writes only absent files and rejects
different existing bytes. `--destination-dir NEW_WORKSPACE_DIRECTORY` permits
a separate recovery check. Four gzip packages are checked, including the
smaller public variable-core CNF. The two trace hashes are identities, not
retrieval links. Their original ext4 paths, copy receipts and retained local
paths are in the native run records; another run may produce different
incomplete bytes. Full local outcome audits require these exact local traces:

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_variable_core_factor_unknown.py --out build/twelfth-variable-run-audit
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_prism_all_columns_unknown.py --out build/twelfth-prism-run-audit
```

Optional native replay uses the authenticated CaDiCaL1.9.5 executable, WSL
Ubuntu-24.04 and calibrated ext4 proof location described in the
[ninth guide](REPRODUCING_20260930_NINTH_WAVE.md). Both runners enforce300
native seconds,1000000 configured conflicts,4 GiB address space,10 GiB proof
file cap, five-second kill grace and320-second outer guard; they require
21 GiB host and11 GiB ext4 free space. Native defaults are preserved without
inventing a seed. There is no automatic retry. Preflight launches no research
solver; an optional new run must use its own output directory:

```powershell
$variableArgs=@('--out','build/twelfth-variable-preflight','--encoding-gate','acceleration/results/20260930_independent_review/variable_core_factor_cnf_v2/summary.json','--encoding-gate-sha256','ecc6c2ee488e68826e790360f3d47d6b029ac33953806bdab530ba50394a6ea0','--object-gate','acceleration/results/20260930_independent_review/variable_core_factor_object_calibration/summary.json','--object-gate-sha256','7577bbb79dfa5b334badc71cac820364d169edfe11f0eeaccd7eedbca9b1d40a')
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/native_20260930_variable_core_factor.py --preflight @variableArgs
$variableArgs[1]='build/twelfth-variable-research'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/native_20260930_variable_core_factor.py --research @variableArgs
$prismArgs=@('--out','build/twelfth-prism-preflight','--encoding-gate','acceleration/results/20260930_independent_review/prism_all_columns_cnf/summary.json','--encoding-gate-sha256','07c589160e930205bc7e42f9524846280b4a8f0573ca9e5dfa06b627a6d115c3','--object-gate','acceleration/results/20260930_independent_review/prism_all_columns_object_calibration/summary.json','--object-gate-sha256','433816d402860b3f1a0cda328a9930952077c113ef1b4c50af097529ed5a9078')
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/native_20260930_prism_all_columns.py --preflight @prismArgs
$prismArgs[1]='build/twelfth-prism-research'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/native_20260930_prism_all_columns.py --research @prismArgs
```

A future SAT assignment must pass the dedicated raw-object checker before
use. A future UNSAT claim requires the complete exact proof and independent
replay, plus the applicable encoding and coverage arguments. The scope of
the arbitrary-core model and the fixed six-prism model must stay separate.

The [publication catalog](../acceleration/results/20260930_twelfth_artifact_packaging/catalog.json)
uses explicit path allowlists, validates the three-registration chain and
stream-checks exact hash references and recoveries without editing the ledger
or index. The source `theory_20260930_variable_core_factor_preflight.py` is
included because the actual producer imports its calibration function; its
separate exploratory size-preflight result cohort is excluded. The later
first-choice normalization, SRG243 fixture, dynamic residual wrapper, identity
scope audit and unused proof-core work are also excluded. Catalog validity
and CI are bookkeeping checks, not mathematical verification.

At the registered twelfth ledger state, with the excluded local traces
available, the complete local inventory can be replayed with:

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/package_20260930_twelfth_catalog.py --out build/twelfth-catalog-recheck --pilot-summary-sha256 c38e623722896f64682c162d351287a555d5a4c49c460ef77684ee134662e167 --pilot-audit-sha256 3a5305e6986086b57e9945915711b5250b153e47152ea4608c855d659f49a4e5
```

Overall search coverage: UNKNOWN; no validated denominator.
