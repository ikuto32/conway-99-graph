# Three quota-rejected rows have direct lambda contradictions

Status: `INDEPENDENT_E71_THREE_REMOVED_ROOTLABEL_ROWS_AUDIT_PASS`.

All three rows removed by the single-row root-label quota probe have an
elementary obstruction. Each forces two distinct common neighbours for
an already adjacent pair. A dynamic program is unnecessary for these
specific negative controls.

| Macro | Exact position / label | Residual pivot | Two required target supports | Forced root label |
|---|---|---|---|---:|
| (1219,7,0) | 30 / (3,6) | (-2,2,1,-4) | (1,4), (1,5) | 3 |
| (1219,10,0) | 30 / (3,6) | (-2,2,1,-4) | (1,4), (1,5) | 3 |
| (1289,2,0) | 10 / (1,6) | (-4,3,3,2) | (0,4), (0,5) | 1 |

Positions and root-neighbour labels use the frozen zero-based convention.
Each listed degree row requires exactly one neighbour in each of the two
target fibres. For source1219, every admissible singleton in both targets
carries root label3. For source1289, every admissible singleton in both
targets carries root label1. The target fibres are distinct, so the two
chosen neighbours are distinct.

The source vertex also carries the indicated root label and is adjacent
to that first-layer vertex. Their two forced common neighbours violate
`lambda=1`. This rejects the particular degree row, independently of the
seven-coordinate quota DP or its state ordering.

The audit independently reconstructs each raw degree row using the prior
standalone principal-inverse audit routines. It then rebuilds the six
relevant 23-vertex partial graphs as explicit neighbour sets and checks
all sixteen target subsets: 96 small checks in total. No research producer,
quota DP or LP solver is imported.

The 20,759 retained-row decisions and the reduced LP certificates are not
independently audited here. These three macros were already excluded by
the exact-label subset moment certificates, so this check adds no macro
exclusion and does not establish an E0 lower bound. It supports stopping
this bounded quota branch while retaining its simple negative controls.

```text
python scratch_theory_e71_row_label_quota_removed_audit.py
```

The detailed row labels, degree vectors, allowed singleton choices and
input hashes are saved in the companion JSON.
