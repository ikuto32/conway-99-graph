# Star-marginal PDHG: bounded CPU study and CUDA design

The CPU reference is ready; broad CUDA implementation is deferred. On the two
saved controls, 2,000 iterations reduce the objective substantially but leave
wide numerical primal/dual gaps. The requested transferred warm start worsens
the primal estimate on the second control. These measurements do not establish
candidate-ranking quality or a GPU speedup.

## Immutable artifacts

* Preferred reference: `star_marginal_cp_cpu_v2.py`, SHA256
  `6a2823692dfb0baab9b0fdb011f84c6fdda82361d9af01433260020cb19ae65d`.
* Control harness: `review_star_marginal_cp_cpu_v2.py`, SHA256
  `fb90c95c3767da7f7ad4994ed586f5b028a778322ca7adbd453886327589a994`.
* Report: `results/20260916_star_cp_cpu_v2_study/summary.json`, SHA256
  `228e5a5576fd43c4a384223089dde5dd0d61de45a774485ac4e4e40ced70f0be`.
* Original reference and report remain unchanged. Root review found that its
  unbounded negative prefix sum could overflow for `[0,-1e308,-1e308]`. V2
  fixes this using the exact inactive-coordinate clamp described below; the
  saved ordinary-magnitude graph controls give unchanged scalar results.

No new LP, GPU, family enumeration, or broad candidate search was run. Sources,
complete-domain audits, reference LP files and exact reference intervals are
hash-bound in the report. Reference imports no optimization producer.

## Saved LP cost

The 11 existing solves use 23,632–25,337 probability variables. Their matrices
including 84 hard normalizations contain 1,034,825–1,105,967 nonzeros. Recorded
assembly is 0.289–0.323 seconds; solve is 7.50–9.23 seconds (median 8.436), at
least 96.2% of assembly-plus-solve time. These are historical timings, not new
benchmarks. Some domains contain **1,053 choices**, so neither a 700-choice nor
a 1,024-choice hard limit is valid for existing inputs.

## Objective, rows, and updates

Each vertex has a complete domain table `D_u` and a probability vector `p_u`
on its simplex. For an unknown edge `u<v`, `E p` takes the marginal from the
smaller endpoint, and `R p` is smaller minus larger endpoint marginal.
The full99-derived linear pair caps are `C x <= b_cap`.

```
A = [R; C E]                       (5166 rows; N probability columns)
b = [0_1680; b_cap_3486]
F(p) = sum(abs((R p)_e)) + sum(max(0, (C E p - b_cap)_i))
y = [beta_1680; gamma_3486], beta in [-1,1], gamma in [0,1]
y_new = clip(y + Sigma (A pbar - b), dual boxes)
p_new = product_simplex_projection(p - T A^T y_new)
pbar_new = 2 p_new - p
```

Floating diagnostics are `F(p)` and
`sum_u min_{S in D_u} (A^T y)_(u,S) - b^T y`. They are not certificates.
The separate exact star-marginal auditor/replayer remains the proof path.

Do not reuse the old edge-variable step `.09`. Here the measured maximum
absolute row sums are 1,022 and 1,145; maximum column sum is 80. The respective
scalar squared-norm bounds are 81,760 and 91,600. A safe equal scalar step
using factor `.9` is only about `.00315` and `.00297`.

The reference instead sets `r_i=sum_j |A_ij|`,
`d_u=max_{j in D_u} sum_i |A_ij|`,
`sigma_i=.9/max(1,r_i)` and `tau_j=.9/d_u` for every `j in D_u`.
Weighted Cauchy–Schwarz gives

```
||sqrt(Sigma) A sqrt(T) z||^2
 <= .9 sum_j tau_j (sum_i |A_ij|) z_j^2
 <= .81 ||z||^2.
```

The primal step is constant within a vertex, so the weighted proximal operator
is the ordinary Euclidean simplex projection. Arbitrary different steps for
individual choices would require a different, weighted projection.

## Projection and controls

Subtract the maximum input, clamp the shifted entries below at `-1`, sort,
and find the usual active-prefix threshold. The threshold lies in `[-1,0]`,
so clamping values below `-1` changes no projected value. It prevents a large
negative tail from overflowing the prefix sum. Unrepresentable subtraction
differences are rejected explicitly; all results must be finite.

797 tiny projections agree with an independent exact-rational support
enumerator to `5.56e-17`. Ten exact-rational toy PDHG steps agree to `1.67e-16`.
The 1,053/2,049-entry controls check simplex KKT conditions, permutation and
translation; `[0,-1e308,-1e308]` returns exactly `[1,0,0]`. Empty, nonfinite,
nonvector and unrepresentable-difference inputs are rejected.

## Quality measurements

| Fixed K | Exact reference optimum interval, approximately | Uniform initial upper | Uniform 500 upper | Uniform 2000 upper / lower |
|---|---:|---:|---:|---:|
| 25496 | 8.113670982–8.113670991 | 202.2828 | 19.2040 | 14.7944 / 2.1661 |
| 26025 | 9.621845625–9.621845676 | 205.7462 | 21.4096 | 17.0315 / 2.9107 |

The first CPU run took 5.32/6.02 seconds for 2,000 iterations. Repeating under
the fixed projection gave 5.66/6.02 seconds. These are bounded CPU timings,
not estimates of CUDA throughput. Best statistics include initialization and
requested checkpoints; last and running-average values are both recorded.

The additional 25496→26025 warm transfer matches exact `(vertex, domain mask)`
identities, retains and renormalizes surviving probability mass, and uses a
uniform distribution only if that mass is zero. It reuses the baseline dual
in the unchanged 1,680-edge/3,486-pair coordinate order. There are 18,618 shared
choices and eight vertices with no common masks. Independent tiny cases cover
reordering, discarded mass, absent masks, and zero-mass fallback even when a
zero-probability mask survives. Warm initial upper is 147.1122; after 2,000
iterations upper/lower are **23.2178 / 6.3731**. The lower estimate improves,
but the upper is worse than uniform initialization. No improvement claim is
supported for this warm-start rule.

## Smallest prospective CUDA implementation

1. Keep float64 arithmetic and the above CPU control as the reference. Export
   complete domain offsets, CSR `A` and `A^T`, targets, per-row dual steps and
   per-vertex primal steps. Independently validate all indices, finite values,
   row/column coordinate bindings, and domain sizes before launching.
2. Store probabilities, extrapolated probabilities, duals and averages in
   global memory. Roughly 25,000 probabilities already make two double arrays
   about 400 KB; the former single-block shared-memory scheme cannot fit.
3. One dual-update kernel gathers CSR rows. A second kernel uses one block per
   `(candidate, vertex)`, gathers transpose rows for its choices, then sorts
   and projects that simplex. Kernel boundaries supply the global barrier.
   For a size-1,053 table, pad sort storage to 2,048 values; size limits must
   come from checked input metadata, with an explicit larger-size path or
   rejection. Do not silently truncate or assume 1,053 is a universal bound.
4. Start with small tiles and the two saved controls plus tiny rational cases.
   Only after full-iterate parity should a paired CPU/GPU timing study proceed.
   No performance guarantee follows from this design.

Explicit double CSR plus transpose costs about **25.8 MB per candidate** on
25496. Factoring `A=[R; CE]` uses approximately **7.9 MB** for both directions,
319,625 forward nonzeros instead of 1,070,151. CPU forward-plus-transpose is
about `.279 ms` factored versus `.809 ms` explicit on that control; projection
is about `1.21 ms`. The second control also benefits from factorization.
The measured bottleneck motivates parallel simplex projection, but factored
geometry should be considered before a large-batch CSR deployment.

A later factored implementation can gather endpoint marginals, update the
1,680 reciprocity and 3,486 cap duals, form nine-term cap costs per unknown
edge, and gather eight signed edge costs per star before projection. It needs
additional kernel synchronization, but avoids materializing the million-entry
matrix. This agrees with the separate fixed-dual Rust scorer's geometry.

The next quality question is whether approximate bounds preserve useful
ranking on a small independently solved shortlist. Cold and transferred
warm-start results here are insufficient evidence to replace exact LP ranking
or to launch a broad CUDA search.
