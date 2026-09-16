# Solver-free compression and fibre-port audit at `E0=78`

Put `delta_F=4-e_F`.  At `E0=78`, `sum delta_F=6`.  The fixed
Ritz values of the fibre compression are `12,-2^6`; the other fourteen lie
in `[-4,3]` and sum to `39`.  Hence their maximum square sum is attained at
`3^13,0`, and

```
tr(D^2) <= 4560.
```

Writing `x_FG=4-D_FG` on disjoint support pairs gives
`sum_{F<G}x_FG=6`, so

```
tr(D^2)
 = sum_F (8-2 delta_F)^2 + 3264
   + 2 (sum_overlap D_FG^2 + sum_disjoint x_FG^2).
```

## Exact support enumeration

All 229,789 labelled weighted placements in the nine deficit partitions
were generated and quotiented by `S7`.  The overlap row equations were then
minimized by pure nonnegative-integer recursion.  The disjoint contribution
in this table uses only its exact real least-norm value, rounded upward; no
SAT or CP-SAT calculation occurs.

| deficit partition | labelled | `S7` orbits | overlap infeasible | spectral lower-bound excluded | survives lower bound |
|---|---:|---:|---:|---:|---:|
| `4+2` | 420 | 2 | 2 | 0 | 0 |
| `4+1+1` | 3,990 | 7 | 7 | 0 | 0 |
| `3+3` | 210 | 2 | 1 | 1 | 0 |
| `3+2+1` | 7,980 | 9 | 6 | 3 | 0 |
| `3+1+1+1` | 23,940 | 20 | 17 | 3 | 0 |
| `2+2+2` | 1,330 | 5 | 3 | 2 | 0 |
| `2+2+1+1` | 35,910 | 28 | 17 | 6 | 5 |
| `2+1+1+1+1` | 101,745 | 56 | 28 | 0 | 28 |
| `1+1+1+1+1+1` | 54,264 | 41 | 7 | 0 | 34 |
| **total** | **229,789** | **170** | **88** | **15** | **67** |

Thus only the last three partitions survive these compression lower bounds.
The 67 survivors are not assertions of integral disjoint-block feasibility.

## Exact exceptional-fibre port enumeration

A deficit-one fibre is a `P4`, with four labelled orientations.  A
deficit-two fibre has seven labelled possibilities: six two-side subsets of
the coordinate square and the pair of diagonals.  For every one of the 67
support orbits, all fibre-shape assignments were enumerated.  Each missing
root/inner BP symbol quota was represented as a port, and all simple
overlap-edge perfect matchings of the 24 ports were enumerated group by
group.

| partition | compression survivors | port-feasible support orbits | after induced pair upper bounds | after forced ordinary-`C4` support BP |
|---|---:|---:|---:|---:|
| `2+2+1+1` | 5 | 0 | 0 | 0 |
| `2+1+1+1+1` | 28 | 1 | 1 (48 graphs, 2 local orbits) | 0 |
| `1^6` | 34 | 3 | 3 | 2 |

For the all-`P4` partition, the three port-feasible support graphs are
`K2,3`, the bowtie (two triangles sharing their degree-four vertex), and
`C6`.  The bowtie fails the support-level BP equations forced by the
ordinary `C4` fibres.  The exact remaining bounded candidates are:

| support graph | labelled support orbit | stabilizer | P4 orientations | overlap graphs | local graph orbits | actual overlap square |
|---|---:|---:|---:|---:|---:|---:|
| `K2,3` | 210 | 24 | 12 | 512 | 8 | 18 |
| `C6` | 420 | 12 | 16 | 128 | 2 | 24 |

Here a local graph orbit is under the setwise support stabilizer together
with independent symbol flips.  All 640 graphs pass induced
common-neighbour upper bounds and the support-count BP completion test.
No disjoint exceptional block has yet been constructed, and symbol-level
completion outside the exceptional fibres remains unchecked.

Reproducible data and code are in
`scratch_general_e78_local_compression.py/.json` and
`scratch_general_e78_local_ports_all.py/.json`.
