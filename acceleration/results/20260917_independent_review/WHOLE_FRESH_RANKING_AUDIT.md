# Independent balanced whole-family ranking review

The mapping check and numerical ranking check both pass for the frozen
balanced request. This is engineering verification, not an exact exclusion.

- Mapping report: `whole_fresh_balanced_mapping.json`, SHA256
  `62373d4c8607baf3103b5bb98ad59427e6e221833b3dba038259d38459ff0eb8`.
- Matrix calibration: `whole_ranking_model_controls.json`, SHA256
  `65668354fdbdb6cf816d845339cb3e6b2c0b901d11b11b4c486489de2145f19e`.
- Ranking report: `whole_fresh_ranking.json`, SHA256
  `34f72e00cf1b6e734b6be706c12ce414d8978a6f24803e648eefbc0d19bb8788`.

The mapping checker derives cycle components from actual changed edges and
reconstructs the 64 lowest historical refined-score choices followed by
64 choices balanced across all fourteen coordinates. Exact graph identities
remove 86 of 2,048 scored family members, leaving 1,962 eligible. The chosen
128 graphs are distinct and all their 4,851 partial common-neighbor caps
were checked. Seven independent controls comprise the real batch plus six
rejected corruptions. Fifteen producer control records were checked and
bound, not represented as independent re-execution. The superseded initial
selection is not approved.

The ranking checker reconstructs all 128 serialized matrices from the
unchanged original domain masks. The new independent builder constructs
the full 99 by 99 integer partial adjacency B and obtains the cap coefficient
of an unknown edge E from BE+EB+E. It imports no producer or producer model
builder. NumPy/SciPy store small integers exactly. Both CSR orientations,
targets, offsets, serialization hashes and execution mappings are compared;
536,548,931 array entries were compared across the complete batch.

Before the new ranking audit, one historical complete serialized model
passed the new reconstruction. A changed matrix coefficient, changed target,
changed offset and zero domain mask were all rejected. The raw control
report preserves its exact source bindings. The new 128-case run has no
unavailable cases or substituted domain tables.

The checker reuses the existing independent binary parser and scalar bound
routine. Its CPU recurrence shares the historical CPU simplex projection
helper, explicitly disclosed in the report. Cold CPU recurrence was checked
only on first, middle and last available candidates: indices 47816, 1736
and 42206, each for 500 iterations. All eleven compared scalars per control
agree within the fixed absolute tolerance 0.000002; maximum observed errors
are respectively approximately 5.40e-13, 5.12e-13 and 1.14e-13. These are
sampled numerical parity results, not exact feasibility or solver proofs.

The verified union shortlist is recorded in `evaluation_selections.union_16`:
51030, 49629, 71703, 74803, 50028, 65848, 1736, 55055, 77958, 25999,
10260, 80479, 46130, 47816, 41448, 50849. These are original zero-based
whole-family row indices. Independent exhaustive domain checking and exact
LP certificate review remain necessary for each subsequent exclusion.

Replay from the repository root with the locked Python environment:

```powershell
$env:UV_PROJECT_ENVIRONMENT = 'build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260917_whole_fresh_ranking.py --ranking acceleration/results/20260917_whole_fresh_v2_balanced/ranking/summary.json --out build/whole-ranking-replay.json --cpu-controls 3
```

Use an unused output path. The historical invocation used the environment's
`build/research-venv/Scripts/python.exe` directly with the same arguments,
writing `acceleration/results/20260917_independent_review/whole_fresh_ranking.json`.
No native domain producer, GPU executable, or LP solver is invoked by this
audit. Target resolution remains UNKNOWN; overall search coverage is UNKNOWN
because there is no validated target-wide denominator.
