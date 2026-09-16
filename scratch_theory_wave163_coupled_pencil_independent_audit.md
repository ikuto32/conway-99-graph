# Wave163 compressed coupled pencil: source-independent exact audit

## Verdict

`VERIFIED_SCOPED_COMPRESSED_CONIC_NULL`.

The independent standard-library checker rebuilt all 57 compressed
four-root bilinear rows directly from induced embeddings and matched the
frozen coefficient payload exactly.  It then independently rebuilt the
universal endpoint row space, checked its ranks over two primes, checked the
stored rational quotient and 49-dimensional kernel exactly, and verified an
exact positive-definite separator in both PSD blocks.

Consequently, the frozen 49-dimensional compressed affine-identity kernel
contains no nonzero pair `(Y3,Y12)` with both matrices positive semidefinite.
This is only a null result for this compressed lane; it does not decide the
Conway 99-graph problem.

## Frozen binding

This audit binds to the current self-contained result note
`scratch_theory_wave163_coupled_conic_null.md`, whose SHA-256 at audit time is

```text
24a022047c26b6d9fec86bcfb9ef3df5cf12c93551af7461898db30d9071a701
```

The executable checker and its complete machine-readable result are:

```text
scratch_theory_wave163_coupled_pencil_independent_audit.py
sha256 c3f97919baa5e6b8b7d026ff36ac7297b69432bb7a2156d03d25cffa636cc589

scratch_theory_wave163_coupled_pencil_independent_audit.json
sha256 2c75d5206009f01c9b8ae61b55d0c91be1c2be628d151c8d59d404747eaf9232
```

The checker imports no Wave163 discovery, pencil, kernel, or PSD script.  It
uses only the Python standard library and consumes the frozen JSON/gzip
artifacts named and hashed in the result JSON.

## Exact checks

- Direct embeddings rebuilt and matched all `21 + 36 = 57` upper-triangle
  rows.  The SHA-256 of the ordered list of rebuilt row hashes is
  `e72ed914b4f062b148070164b7d13c5164aa00d4d13609c05328ef651b94273b`.
- The independently derived order-six density map has SHA-256
  `33bc63bd629e08dd4033e4ab3b123185b6215abee35c41836c7cabcf5dc3e313`.
- Over each of `1000000007` and `1000000009`, the reduced universal rank is
  `909`, the rank after adjoining the 57 compressed rows is `917`, the
  compressed quotient rank is `8`, and the full universal rank is `1117`.
- Eight stored rational universal-nullspace vectors and all 49 stored
  rational kernel vectors pass exact substitution.  The exact `57 x 8`
  quotient-map SHA-256 is
  `e489a6ada7ac2943a2d3d04b06b49ff3d4ff28770645fc4707cd2827d5146de5`.
- The rational quotient-equation combination
  `(1, 869823/1000000, 64241/1000000, 9553/1000000,
  58629/500000, 193079/500000, 121737/250000, 33021/500000)`
  produces exact positive-definite `6 x 6` and `8 x 8` matrices.  Their
  canonical SHA-256 values are respectively
  `b878d0ec9d692509681e98f5be0f756fb24efcc7786b532db93a89f01120a7db`
  and `10fd6a48cb2e7a6c3a01b0fae69415b4c61726c58fa78886307fc567b18fd5c7`.
  Fraction LDL elimination gives 6 and 8 strictly positive pivots.

The trace audit explicitly uses

```text
tr(Y H) = sum_i Y[i,i] H[i,i]
          + 2 sum_{i<j} Y[i,j] H[i,j],
```

and independently applies the exact direction-column normalization
`A[i,j] = Q[i,j] / (scale[i] scale[j])`.  Thus both the off-diagonal factor
of two and the direction scaling are included in the exact identity, not
absorbed by an unstated convention.

## Resource guard and replay

The run took `205.74029183387756` seconds.  The minimum sampled free physical
memory was `65.45054311425744%`, above the required `18%` gate.

Replay from the repository root with:

```powershell
& 'C:\Users\ikuto\.local\bin\python3.12.exe' -B `
  scratch_theory_wave163_coupled_pencil_independent_audit.py
```
