# Wave163 controls in the full root-3 and root-12 blocks

Status:

```text
INDEPENDENT_EXACT_FULL_ROOT3_ROOT12_PSD_PASS
INDEPENDENT_EXACT_INTEGER_CONTROL_FULL_ROOT3_ROOT12_PSD_PASS
```

The rational count-slack control and its integral-lattice lift were both
evaluated in the **full** four-root covariance blocks for root masks 3 and
12.  Neither control yields a negative direction or a new scalar cut.

## Streaming evaluation

The evaluator reuses the frozen class streams

```text
order 6:  62 classes
order 7: 208 classes
order 8: 916 classes
```

and streams every rooted embedding directly.  It does not regenerate the
class catalogues and does not materialize a full coefficient tensor.  Only
the evaluated `155 x 155` and `178 x 178` matrices are held.  The memory
guard remains at 18 percent free physical memory.

For a common count denominator `d`, the archived integer matrix is

```text
C_d = d (R M - s s^T).
```

Here `d=40000` for the first rational control and `d=1` for the integral
control.

## Exact results

For both controls, exact pivoted rectangular `LDL^T` gives

| root mask | full flag size | exact rank | exact nullity |
|---:|---:|---:|---:|
| 3 | 155 | 15 | 140 |
| 12 | 178 | 16 | 162 |

Every retained diagonal pivot is strictly positive and every matrix entry is
reconstructed exactly.  Therefore both full matrices are PSD.  The apparent
minimum numerical eigenvalues, between `-1e-15` and `-3e-15` after maximum-
entry scaling, are roundoff on their large exact kernels.

The clean-room verifier imports no producer module.  It independently:

1. reconstructs the rational or integral `x7,x8` control;
2. reads the independently verified frozen order-six counts;
3. restreams all rooted embeddings;
4. compares all `24025+31684=55709` matrix entries with the archive;
5. replays the exact rectangular `LDL^T` factorization; and
6. checks all 57 projections onto the retained `U3,U12` directions.

The projection identity is

```text
u_i^T C_d u_j = (d/92) (q_ij . t).
```

This also audits a subtle normalization point: compressed rows are stored in
primitive form, but `row_maps()` restores each `raw_divisor` before deletion
and quotient formation.  Thus the exact quotient map already represents
coherent raw covariance entries.  The off-diagonal factor-two and subsequent
positive diagonal direction rescaling remain valid.

## Consequence and boundary

There is no negative root-3/root-12 direction at either control, so the
requested cutting-plane extension stops without adding an invalid or
numerically speculative cut.  In particular, the integral point

```text
t=(14401612,13247818,957378,134580,
   1801038,5687012,7458420,964656)
```

has nonnegative integral order-seven/eight pseudocounts, `sum E0=0`, and
passes both full blocks exactly.

This proves feasibility of these two blocks only at the displayed
pseudocount controls.  It does not prove that all nine four-root types pass,
does not provide a graph realization, and does not settle the endpoint or
the Conway 99-graph problem.

## Artifacts

Shared evaluators:

- `scratch_theory_wave163_count_slack_full_block.py`
- `scratch_theory_wave163_count_slack_full_block_exact_psd.py`
- `scratch_theory_wave163_count_slack_full_block_audit.py`

Rational control:

- `scratch_theory_wave163_count_slack_full_block.json`
- `scratch_theory_wave163_count_slack_full_block_matrices.json.gz`
- `scratch_theory_wave163_count_slack_full_block_exact_psd.json`
- `scratch_theory_wave163_count_slack_full_block_audit.json`

Integral control:

- `scratch_theory_wave163_integer_lattice_full_block.json`
- `scratch_theory_wave163_integer_lattice_full_block_matrices.json.gz`
- `scratch_theory_wave163_integer_lattice_full_block_exact_psd.json`
- `scratch_theory_wave163_integer_lattice_full_block_audit.json`

Replay:

```powershell
# rational control
.\.uv-cache-theory\archive-v0\deXFLNmNVXSaFnwr\Scripts\python.exe scratch_theory_wave163_count_slack_full_block.py
C:\Users\ikuto\.local\bin\python3.12.exe scratch_theory_wave163_count_slack_full_block_exact_psd.py
C:\Users\ikuto\.local\bin\python3.12.exe scratch_theory_wave163_count_slack_full_block_audit.py

# integral control
.\.uv-cache-theory\archive-v0\deXFLNmNVXSaFnwr\Scripts\python.exe scratch_theory_wave163_count_slack_full_block.py --integer-control
C:\Users\ikuto\.local\bin\python3.12.exe scratch_theory_wave163_count_slack_full_block_exact_psd.py --integer-control
C:\Users\ikuto\.local\bin\python3.12.exe scratch_theory_wave163_count_slack_full_block_audit.py --integer-control
```
