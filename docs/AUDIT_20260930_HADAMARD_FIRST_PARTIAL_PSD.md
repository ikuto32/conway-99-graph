# Independent residual PSD certificate review

The statement concerns only the exact saved case0 twelve-column partial
object. Its residual matrix R is reconstructed from the raw prescribed core
Gram minus the literal twelve-column product. Passing this necessary test
does not supply the remaining forty-eight binary columns or a residual graph.

The producer saves rational congruence basis rows, positive pivot values and
null-space rows. Instead of replaying its recursive Schur update, this
checker clears each row's denominators to obtain an integer matrix Z and
checks every entry of Z R Z^T directly. The result is exactly diagonal with
twenty-nine positive and seven zero integer entries. It proves Z is
invertible by exhibiting a nonzero determinant modulo a prime. If an integer
matrix were singular over the rationals, its integer determinant would be
zero modulo every prime; the nonzero residue is therefore sufficient.

Since the inverse change of basis exists over the rationals, the diagonal
identity proves positive semidefiniteness and exact rank29/nullity7. The
checker saves the complete integer basis, scales, diagonal and modular
determinants. Producer recursive coefficient metadata is unnecessary to this
independent sufficient certificate and is not described as replayed.

Controls include a singular positive3x3 matrix and the genuine SRG243
fixture's explicit remaining168-column Gram. Seven corruptions alter a
pivot, basis row, null vector, rank, basis independence, matrix definiteness
or symmetry. The implementation imports no producer code and uses no
floating-point arithmetic or numerical rank threshold.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_first_partial_psd.py --out acceleration/results/20260930_independent_review/first_partial12_psd
```
