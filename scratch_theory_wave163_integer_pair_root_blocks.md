# Wave163 integer control in all Wave147 pair-root coefficients

Status: `INDEPENDENT_EXACT_INTEGER_PAIR_ROOT_PSD_PASS`.

The exact integer `T=sum E0=0` pseudocount was evaluated against the complete
frozen Wave147 pair-root coefficient package:

```text
ordered-edge family:       1,207 class matrices, block size 66
ordered-nonedge family:    1,207 class matrices, block size 87
total:                     2,414 class matrices
nonzero upper coefficients: 272,054
```

Every frozen matrix record was consumed; no class or coefficient matrix was
regenerated.

## Evaluation

For each root relation `sigma`, the exact uncentered finite Gram block is

```text
M_sigma = sum_(h=5)^8 sum_H x_H C_H^sigma.
```

The order-five counts come from the fixed SRG formulas, the order-six counts
from the independently verified Wave43 endpoint package, and the order-seven
and order-eight counts from the integer Wave163 control

```text
t=(14401612,13247818,957378,134580,
   1801038,5687012,7458420,964656).
```

All arithmetic in the matrix aggregation is integral.  The global sums also
match the finite Gram identity:

```text
sum M_edge    = (99*14) * C(97,3)^2,
sum M_nonedge = (99*84) * C(97,3)^2.
```

## Exact PSD certificate

Both matrices have rank exactly one:

| root relation | size | rank | nullity | positive pivot `M[0,0]` |
|---|---:|---:|---:|---:|
| ordered edge | 66 | 1 | 65 | 1,928,327,940,000 |
| ordered nonedge | 87 | 1 | 86 | 10,350,745,574,400 |

The independent audit does not rely on floating eigenvalues.  For every
entry of each matrix it checks

```text
M[0,0] M[i,j] = M[i,0] M[0,j].
```

The pivot is strictly positive, so for every real vector `v`,

```text
v^T M v = (sum_i M[i,0] v_i)^2 / M[0,0] >= 0.
```

This verifies all `66^2+87^2=11,925` rank-one identities and proves exact
PSD.  There is no negative direction and hence no valid new scalar cut from
either Wave147 block at this control.

The floating eigenvalue scout saw minima only around `-5e-16` after scaling;
the exact rank-one identities show these are numerical zero.

## Boundary

The result strengthens the boundary for the integer pseudocount: in addition
to the universal endpoint equalities, count nonnegativity/integrality, the
57 compressed rows, and the full Wave152 root-3/root-12 blocks, it also
passes both original Wave147 pair-root Gram blocks exactly.

It remains a pseudocount, not a graph.  The result does not cover the other
seven Wave152 four-root types, higher-order constraints, factorization into
actual induced subgraphs, or the Conway 99-graph existence question.

## Artifacts

- `scratch_theory_wave163_integer_pair_root_blocks.py`
- `scratch_theory_wave163_integer_pair_root_blocks.json`
- `scratch_theory_wave163_integer_pair_root_blocks_matrices.json.gz`
- `scratch_theory_wave163_integer_pair_root_blocks_audit.py`
- `scratch_theory_wave163_integer_pair_root_blocks_audit.json`

Replay:

```powershell
.\.uv-cache-theory\archive-v0\deXFLNmNVXSaFnwr\Scripts\python.exe scratch_theory_wave163_integer_pair_root_blocks.py
C:\Users\ikuto\.local\bin\python3.12.exe scratch_theory_wave163_integer_pair_root_blocks_audit.py
```

Current SHA-256 bindings:

```text
integer_pair_root_blocks.py               49648249f5c87a35deb1d09756cea98304899db308959e229b145602e9d336bb
integer_pair_root_blocks.json             0f8e39223d788fad44e76c1b5b8f0c8f5de97a196cfbad55f6660874a9271b87
integer_pair_root_blocks_matrices.json.gz da3d62ae802723bdd809b7b5ae78abd03f0815ce60948d174245629a3a413511
integer_pair_root_blocks_audit.py         b06e380f3f880bb90705dac2f809a389f5d0b23ebb4ea90535a98e1e0db0a44a
integer_pair_root_blocks_audit.json       7eed8c8efaadd2b73ce360a09d69e81b62a24e1faad72a1c4fd6e2480155a932
```
