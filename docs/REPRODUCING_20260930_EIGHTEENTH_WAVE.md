# Eighteenth milestone: exact parity projections and a rejected lift

This cohort adds seven scoped claims: the direct binary MIP encoding, two
necessary parity encodings, two parity witnesses, one selected-branch lift
exclusion and a general necessary cut for balanced factors on one fixed
support. Coordinatewise balance is an additional assumption, not a proved
normalization. No target automorphism is assumed. No full factor, graph or
general nonexistence proof was obtained. Overall search coverage: UNKNOWN;
no validated denominator. The second parity witness's subsequent lift work
belongs to the next cohort and is excluded from these counts.

All new cohort inputs are below 10 MiB individually and are included directly.
The catalog binds the exact source, run records, failures and audit artifacts.
Some older large inputs require the recovery commands in the
[seventeenth guide](REPRODUCING_20260930_SEVENTEENTH_WAVE.md). Historical native
tools retain their original provenance and LOCAL_ONLY binary availability;
public sources and build records do not guarantee identical rebuilt binaries.

Use the locked root environment, with fresh output paths:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv sync --locked --cache-dir .uv-cache-20260917
```

The lock pins Python dependencies, including NumPy 2.5.3, SciPy 1.18.1,
highspy 1.15.1, PyYAML 6.0.2 and jsonschema 4.23.0. Recorded runs used Python
3.12.10 and uv 0.11.25. Each manifest retains the exact executable, argument
array, working directory, source commit and artifact hashes. Replaying an
audit is repeated execution of that checking path, not a new derivation.
Do not rerun one-shot ledger registration or publication scripts.

The direct MIP model has 5,400 binary variables, 726 one-hot/Gram equalities
and 40 strict ordering inequalities. It omits outside-column caps initially;
the producer would add violated caps only after independently checkable
incumbents. Separate model and raw-object checks precede the run. The single
research call reached the cooperative 120-second allocation: 120.25 wrapper
seconds, explicitly including a 0.25-second overrun. Its saved vector was
invalid as an incumbent, with no Gram object and no added cuts. This is
UNKNOWN, not an infeasibility result.

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_prism_binary_mip.py audit --run acceleration/results/20260930_hadamard_prism_binary_mip_pilot --summary-sha256 081cce1e5126534eadd2a30d6813a85685b1f6caac052dabce71fe52c970635a --gate acceleration/results/20260930_independent_review/hadamard_prism_binary_mip_calibration/summary.json --gate-sha256 4c27ffee59dbfae792e6776cb5d6175750e31c7f65c9f5e14337d07b3acab6ca --out build/eighteenth-mip-outcome-new
```

The original parity projection has 520 variables and 4,481 clauses. Its
necessary implication includes full Gram, balanced triples and column caps;
the prior cyclic-factor exclusion supplies the nonconstant-group premise.
SAT provides only twenty parity patterns. The first witness has sixteen
mixed and four constant groups. Its original checker rejected a hexadecimal
metadata representation after the mathematical checks. The failed source
and receipt remain preserved. The corrected separate checker accepts both
representations and has an independently checked code delta and controls.
The original witness remains valid for its formula.

Its full balanced-lift relaxation has 312 variables and 560 equations.
Independent enumeration and direct integer checks found six identically
zero coefficient rows with required value one. The exact dual with only
row 139 weighted -1 has all 312 column products zero and right-hand-side
product -1. This excludes exactly that selected parity branch. The initial
CNF builder's empty-counter assertion is preserved as a failed build, not
as the proof. A planned numerical LP was explicitly cancelled before any
calibration or research solver call because the exact obstruction sufficed.

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_balanced_lift_zero_rows.py --out build/eighteenth-first-lift-exclusion-new
```

The independent checker reconstructs all 312 options and 560 equations;
its positive control is the full 3,000-variable balanced-domain relaxation
with exact weight 1/150. Eight corrupted controls are rejected. Integrality,
between-group column caps and residual D are omitted from an already
impossible nonnegative relaxation; the conclusion does not exclude other
parity assignments or arbitrary factors.

An independent permutation argument gives sixty general necessary cuts:
for each nonmatched coordinate pair, at least one of its five containing
groups must disagree in parity at that pair or have constant parity on all
six coordinates. This statement ranges over balanced factors on the frozen
support, independently of the first assignment. The proof checks the local
permutation classification and the exact support-to-literal mapping.

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_balanced_parity_cuts.py --out build/eighteenth-cut-lemma-new
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_parity_support_cuts.py audit --out build/eighteenth-cut-encoding-new
```

The strengthened formula preserves all 4,481 original clauses and appends
sixty ten-literal positive clauses. Its 520-variable, 4,541-clause CNF has
SHA256 db9816ddf037250efc04b1e093e407eac0ec2c4fadf2f24b5774fb3249eba07f.
All clauses and raw-pattern conditions were independently reconstructed
before execution. Both parity pilots used one native CaDiCaL 1.9.5 call each,
with 60 seconds WALL time, 100,000 configured conflicts, 4 GiB address space,
10 GiB trace limit and an 80-second outer guard. No CPU limit or automatic
retry was imposed. SAT learned traces are retained, not presented as UNSAT
certificates. Exact observed times and conflicts remain in the run records.

The strengthened attempt returned SAT after 11,790 conflicts, 0.17 displayed
CPU seconds, 0.20 displayed native wall seconds and 0.25 wrapper seconds.
An independent checker verified all 520 signed assignments, every actual
clause, all twenty decoded patterns, sixty disagreement counts and sixty
added conditions. All twenty patterns are mixed and all sixty disagreement
counts are three. The nine corrupted execution receipts are separate from
the mathematical object controls. No color-phase lift or residual D follows.

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_parity_support_cuts.py sat --encoding-gate acceleration/results/20260930_independent_review/hadamard_parity_support_cuts_encoding/summary.json --encoding-gate-sha256 7a9b76b9e139f065c850194b6968ebf4a98c0211668e1f824d2ac75640b7dd12 --assignment acceleration/results/20260930_hadamard_parity_support_cuts_native_pilot/main/parsed_model.json --native-output acceleration/results/20260930_hadamard_parity_support_cuts_native_pilot/main/solver.stdout.log --decoded acceleration/results/20260930_hadamard_parity_support_cuts_native_pilot/main/decoded_projection.json --out build/eighteenth-cut-witness-new
```

The [root ledger](../CLAIMS.yaml), frozen checkpoint and explicit artifact
catalog distinguish mathematical claims from engineering outcomes. Current
execution must be established from a fresh process observation; neither
this guide nor historical PIDs assert that a search is running.
