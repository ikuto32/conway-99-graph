# Validated CUDA geometry-layout optimization

`overlap_cp_gpu_layout_v2.cu` is a new derivative of the frozen CP prototype.
On the measured 512-candidate, 500-iteration batch, it was 2.745 times faster
in the CUDA kernel interval. All compared scalar outputs were bitwise equal
to the original. The original source and executable remain unchanged.

The only implementation change is geometry storage: index and label table
contents move from constant memory to read-only global loads, and the fixed
quota-column table is transposed so neighboring threads access consecutive
entries for a given gather slot. Constant memory now holds nine uniform
pointers (72 bytes), rather than 54,516 bytes of tables. Matrix coefficients,
row and column order, accumulation order, float64 arithmetic, step sizes,
256-thread blocks, recurrence, barriers, shared-memory layout, parser, and
output schema are unchanged. The full CP kernel and graph-validation/RHS
source spans were compared after normalizing line endings and were identical.

Compiled resource inspection reported 56 registers per thread versus 60 in the
original, with zero local-memory or stack use in both versions. This change
does not address the shared-memory occupancy limit described in the previous
source review.

## Checks

- The frozen independent CPU-control checker passed all five graphs, both
  initial dual states, and checkpoints 1/2/10 and 500/2,000/10,000. Across
  720,720 vector entries, maximum discrepancy was 3.89e-15; across 620 scalar
  comparisons, it was 7.11e-14.
- The 257-candidate repeated dyadic control crossed the actual 256-candidate
  tile boundary. All 3,598 scalar comparisons passed against the independently
  validated Rust output. Repeated copies of each control were bitwise equal.
- The timing batch used 512 distinct, evenly spaced candidates from the
  independently enumerated 74,638-candidate family. All 512 graphs were also
  checked by the full99 Python validator. Both versions used exactly the same
  input and 500 iterations. Three runs per version were interleaved in the
  order old/new/new/old/old/new.

| Timing median | Original | Layout v2 | Old / new |
|---|---:|---:|---:|
| CUDA kernel interval | 0.294509 s | 0.107280 s | 2.745× |
| Device copies + kernel | 0.295769 s | 0.108532 s | 2.725× |
| Process wall time | 0.461952 s | 0.266831 s | 1.731× |

All 4,096 scalar outputs in each benchmark run were bitwise equal across both
versions. Clocks and power were not locked. These measurements establish the
improvement on this bounded batch; they do not predict full-family runtime or
change the numerical-only role of CP scores.

## Frozen artifacts

| Artifact | SHA256 |
|---|---|
| `overlap_cp_gpu_layout_v2.cu` | `43b1452adee28f01f90e227875f7d08bab6dad8141041c2036945fcd122cc389` |
| `build_overlap_cp_gpu_layout_v2.ps1` | `c5e778583dae0f10e4f3c8701bbe16013cac9ab52181c0310c1eeebd25c1ed59` |
| `build/overlap_cp_gpu_layout_v2.exe` | `42dbd7ea8f41d9b195d4bfb2c900e5edcd6feec8dd58b9d68f777bca889c065e` |
| `review_cp_gpu_layout_v2.py` | `9a551369ebcb33679119b49f2de6e7413f5806e66848823328d827370def9a74` |
| `results/20260916_cp_gpu_layout_v2_controls/audit.json` | `caa285833ab3ef523dda693607c37ed3d6c89c9355734bc65728c0cf2f2defed` |
| `results/20260916_cp_gpu_layout_v2_benchmark/report.json` | `2f8be8fc28e0ce43fb64eabd71cadc0efde514b12b31ef3183545e7d4c08043d` |

The new executable accepts the existing C99CP1 input and CLI, including
`--vectors`. Integration should bind this source, binary, and independent
audit explicitly. No production search driver was changed by this task.
