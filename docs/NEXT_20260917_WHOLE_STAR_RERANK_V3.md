# Preregistration: same128 original-star models, cold5000 reranking

Question: does a longer cold PDHG run provide more useful numerical intervals and ordering on this fixed cohort, calibrated against its16 independently exact LP intervals? This experiment reranks128 existing candidates; it generates zero new candidates. No model, domain, graph, or mathematical objective changes. No automorphism is assumed. Overall search coverage: UNKNOWN; no validated denominator.

The frozen source is `acceleration/results/20260917_whole_fresh_v2_balanced/ranking/summary.json`, independently checked by `acceleration/results/20260917_independent_review/whole_fresh_ranking.json` (SHA256 `34f72e00cf1b6e734b6be706c12ce414d8978a6f24803e648eefbc0d19bb8788`). Calibration and the exclusion of the already LP-tested16 use `whole16_scope.json` (SHA256 `f023c28c8f82388c69ea56af5b91785853bb7519c51044371a957743fc6072d1`) in that independent-review directory. Every selection ID remains the actual zero-based whole-family row.

## Input and resource freeze

`acceleration/refine_whole_star_rank_v3.py` copies the four original32-case binary chunks into a fresh preparation directory. The CUDA parser at `star_pdhg_gpu.cu:251` reads eight magic bytes, count u32 at8, checkpoint-count u32 at12, then the sole checkpoint u32 at16. All integers are little endian. The binary model payload begins at20. The only permitted mutation is the four bytes `[16,20)`, changing500 to5000. The copy checker compares every payload byte, checks total length and all original per-record hashes/offsets. Original chunks, manifests, numerical outputs, domains, and previous evidence are retained unchanged. No domain enumeration, model reconstruction, or exporter is invoked by this producer.

The original objective is `ORIGINAL_STAR_SIMPLEX_PDHG_V1`, using original84-domain star simplexes and unchanged reciprocity/cap rows. It is distinct from the filtered-star LP experiment. The same GPU executable and CUDA source are pinned. Each chunk starts cold at uniform probability per simplex and zero dual, with float64, eta0.9 and theta1. The sole requested checkpoint is5000. Numerical best values include initialization and the5000 last/average iterates only: the earlier500 checkpoint is not merged. Therefore even numerical bracket monotonicity across the two separate outputs is not promised.

Run exactly four sequential GPU processes, each with600seconds wall limit, at most2400seconds aggregate process budget. Per-chunk outputs, logs, elapsed time/device and progress records are saved; failure or cap stops the batch and preserves partial evidence. No shortlist is emitted unless all128 outputs pass finite numerical sanity checks. Retrying requires a fresh execution attempt and an explicit deviation record; old artifacts may not be overwritten. Preparation and validation launch zero GPU processes. Execution additionally requires a genuine independently hash-bound input audit with status `INDEPENDENT_WHOLE_STAR_RERANK_V3_INPUT_PASS`. The producer controls are engineering checks only.

## Selection frozen before reranking

Exclude exactly the16 independently LP-evaluated IDs:

`51030,49629,71703,74803,50028,65848,1736,55055,77958,25999,10260,80479,46130,47816,41448,50849`.

Among the remaining112, sort ascending numerical upper bound and ascending numerical lower bound separately, breaking ties by original row ID. Select the union of the first8 of each list; preserve both roles on overlap; fill to16 using unused rows in upper-score order. No exact LP interval, calibration result, coordinate preference or retrospective threshold alters this rule. The proposed shortlist remains pending an independent ranking audit; this producer launches no LP.

All16 calibration cases are reported, whether favorable or unfavorable. For both500 and5000 outputs, save numerical lower/upper/gap, upper and lower ranks among the same128, exact rational LP interval, numerical-to-exact endpoint differences (display floats), and exact binary-float comparisons against the rational interval endpoints. These comparisons diagnose numerical calibration; they do not certify floating-point GPU arithmetic or a graph. No empirical success threshold is used to suppress a case. Numerical scores never establish exclusions or target feasibility. Meaningful success is a better calibrated ranking; failure includes loose bounds or unchanged ordering and remains reportable evidence.

## Reproduction

Use repository root and `UV_PROJECT_ENVIRONMENT=build/research-venv`. No new Python dependency is required; `uv.lock` and `pyproject.toml` are bound. Commands:

```powershell
$env:UV_PROJECT_ENVIRONMENT = 'build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/qa_refine_whole_star_rank_v3.py --out acceleration/results/20260917_whole_star_rerank_v3_controls
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/refine_whole_star_rank_v3.py --prepare --prepared acceleration/results/20260917_whole_star_rerank_v3/prepared --calibration-review acceleration/results/20260917_independent_review/whole16_scope.json
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/refine_whole_star_rank_v3.py --validate-only --prepared acceleration/results/20260917_whole_star_rerank_v3/prepared --report acceleration/results/20260917_whole_star_rerank_v3/preflight.json
```

After independent input review only, use the same source with `--execute --prepared` as above, a fresh `--out`, and the actual `--input-audit`, `--input-auditor`, `--input-auditor-sha256`. Source commit, exact invocation, model and artifact hashes are stored in prepared/execution manifests. This document preregisters the experiment; it does not assert execution has begun.
