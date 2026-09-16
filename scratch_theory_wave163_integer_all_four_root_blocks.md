# Wave163 integer control: all nine Wave152 four-root blocks

## Result

The integral `T=0` pseudocount passes every one of the nine four-root
covariance blocks used by Wave152.  This is an exact positive-semidefinite
statement, not a floating-point inference.  No negative direction and hence
no new scalar cut is obtained at this control.

| root mask | block size | exact rank | nullity |
|---:|---:|---:|---:|
| 0 | 224 | 38 | 186 |
| 1 | 201 | 27 | 174 |
| 3 | 155 | 15 | 140 |
| 7 | 99 | 3 | 96 |
| 11 | 69 | 3 | 66 |
| 12 | 178 | 16 | 162 |
| 13 | 125 | 6 | 119 |
| 15 | 60 | 0 | 60 |
| 30 | 70 | 0 | 70 |

The root-15 and root-30 matrices are identically zero.  All other blocks
have the displayed positive rank.

## Exact object checked

For a root type `rho`, let `R_rho` be its ordered-root embedding count,
`s_f` the first moment of a six-vertex four-root flag `f`, and `M_fg` the
covering-pair second moment.  Because this control has integral counts, the
centered covariance matrix is the integer matrix

```text
C_rho[f,g] = R_rho M_fg - s_f s_g.
```

The frozen class streams contain 62 order-6, 208 order-7, and 916 order-8
classes.  Their nonzero counts at the control are respectively 61, 204, and
890.  Streaming all ordered four-root embeddings gives:

| order | matched rooted embeddings | covering products |
|---:|---:|---:|
| 6 | 5,028 | 5,028 |
| 7 | 38,586 | 231,516 |
| 8 | 337,362 | 2,024,172 |

Each matrix has an exact rectangular factorization `C=L diag(d) L^T` with
strictly positive rational entries in `d`; the full sparse factors are saved
in the LDL archive.  Across the nine blocks, 184,973 matrix entries were
reconstructed exactly.

## Independence and frozen-input boundary

The clean-room audit does not import the discovery/producer module.  It:

1. reads the existing Wave147 frozen class streams rather than regenerating
   graph classes;
2. independently reconstructs the 916 integral order-8 counts from the saved
   eight-dimensional affine-kernel coordinates;
3. obtains the 208 order-7 counts from the frozen deletion equations and the
   62 order-6 counts from the independently stored deck result;
4. restreams every ordered four-root embedding;
5. compares every entry with the deterministic matrix archive; and
6. independently recomputes and reconstructs every exact LDL factor.

The deterministic centered-matrix archive has SHA-256
`9e8e86b263be6cb6b37a72b7aafa7efc62d82ce6b493373b237397e3d29c17bd`.
The 18% free-physical-memory gate was checked throughout.

## Artifacts

- `scratch_theory_wave163_integer_all_four_root_blocks.py`
- `scratch_theory_wave163_integer_all_four_root_blocks.json`
- `scratch_theory_wave163_integer_all_four_root_blocks_matrices.json.gz`
- `scratch_theory_wave163_integer_all_four_root_blocks_ldl.json.gz`
- `scratch_theory_wave163_integer_all_four_root_blocks_audit.py`
- `scratch_theory_wave163_integer_all_four_root_blocks_audit.json`

## Scope

This closes the test of this explicit pseudocount against the complete set of
nine Wave152 order-at-most-8 four-root covariance blocks.  It does **not**
construct a graph, prove realizability of the pseudocount, or settle the
Conway 99-graph problem.  Instead it proves a boundary result: these current
four-root covariance constraints do not by themselves exclude the `T=0`
endpoint.
