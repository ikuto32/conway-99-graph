# Clean-room audit of the integral order-8 boundary

## Verdict

`INDEPENDENT_INTEGRAL_ORDER8_BOUNDARY_BINDING_PASS`

The consolidated boundary is correctly bound to one and the same frozen
coefficient stream, affine kernel, and integral pseudocount.  No producer
module was imported, no graph class was regenerated, and no coefficient
matrix was regenerated.

## Checks performed

1. Every file hash recorded by the consolidated JSON was compared with the
   current file bytes.
2. The independent coupled-pencil, integral-lattice, Wave147 pair-root, and
   Wave152 four-root audit statuses were reread and their input-hash chains
   were checked.
3. The common Wave147 coefficient archive has the same SHA-256 in all four
   audit chains; it contains two identical class streams with the histogram
   `21,62,208,916`, hence 1,207 records per pair-root family and 2,414 total.
4. The marked-row archive was read directly and contains 944 vertex rows and
   4,440 ordered-pair rows.
5. From the frozen eight-dimensional affine kernel and

   ```text
   t=(14401612,13247818,957378,134580,
      1801038,5687012,7458420,964656)
   ```

   all 916 order-8 counts were reconstructed.  The frozen 208 deletion rows
   then reconstructed all 208 order-7 counts.  Every count is a nonnegative
   integer and every mask/count pair agrees entrywise with the consolidated
   JSON.
6. The endpoint checks give `n3=4158`, `P=0`, `N(H_delta)=0`, and therefore
   `sum E0=0`; nonnegativity gives pointwise `E0(r)=0` in this pseudocount.
7. The two saved Wave147 matrices were checked directly by the exact rank-one
   identity `Mpp*Mij=Mip*Mpj`: dimensions/ranks are `66/1` and `87/1`.
8. The nine saved Wave152 matrices were matched to their hashes and every one
   of their 184,973 entries was reconstructed from the full sparse rational
   LDL archives.  Their exact ranks are
   `38,27,15,3,3,16,6,0,0`.

Canonical count-vector hashes:

- order 7: `a1a33e0d1beddf2a56443a81f33fdf7d6f01e2c78a8f0a4cbc860a322122ed4e`
- order 8: `cf4c72694b56c16ea4db09320d958e66ac039dfe636e418daf64679209f468c7`

## Rigorous scope

The audit establishes that this particular nonnegative integral 208/916
pseudocount lies on the `T=0` face and passes the audited universal affine
rows, all 2,414 frozen Wave147 pair-root records, and all nine archived
Wave152 four-root covariance blocks.

It does not establish that the pseudocount is realizable by a graph, that it
satisfies every conceivable order-8 inequality, or that an
`srg(99,14,1,2)` exists or does not exist.  The precise boundary conclusion is
that the present frozen relaxation cannot exclude `T=0`; higher-order
synchronization or realizability constraints are required.

## Artifacts

- `scratch_theory_wave163_integral_order8_boundary_audit.py`
- `scratch_theory_wave163_integral_order8_boundary_audit.json`
- `scratch_theory_wave163_integral_order8_boundary_audit.md`
