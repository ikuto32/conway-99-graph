# Warm01 final and step-zero complete root census v2

This is a new configuration of the native-authored v1 census implementation.
The old source/spec/results are immutable. The v2 changes frozen input/report
pins, source version, local environment evidence and budget description; the
exact parsing, bitset root calculation, triangle enumeration and controls are
unchanged. This producer cannot approve its own output. ROOT will independently
reconstruct every root using dense integer arithmetic without producer imports.

The frozen population is exactly two complete labelled 99-vertex matrices and
all 99 roots of each (198 records): warm01 native/best.adj at SHA256
`9d5b88ba2a2eb13d39d2a5edea1c25af9a9105c143c4297fe37e84f666a37a2d`
and warm01 native/first_lambda0.adj at
`818314b75fccfa0f3fe702602afb02b6415f3138a770ef15ed0621d189d88836`.
The latter is the retained new step-zero reset graph, not the prior pilot's
29,380,701-step snapshot. Independent warm saved-object report is
`acceleration/results/20261003_independent_review/weight60_warm01/summary.json`
at SHA256 `256c8277ab5c69e74f4c9725c4b42e96e31b4e546c490b8e231df4ed6831bf6c`.

Before launch freeze v2 source/spec. Use locked offline root uv environment and
the supported local Windows Job supervisor: 60 seconds outer, 40 seconds
worker, 20 seconds internal serialization reserve, 10 seconds outer shutdown
guard. The previous full two-graph census took 0.72 seconds; this deliberately
generous short allocation is evidence based. No native solver/search is launched.

Rerun all nine rook9 root controls and 11 strict corrupted controls before the
full calculation. Exact matrix domain is binary, symmetric, diagonal zero and
14 regular. For each graph enumerate all 156,849 vertex triples, every actual
triangle and every root's 14-neighbor induced matching, 84 outsider exact common
neighbor sets/counts, full histogram, CN2 eligible set/count and row residual
`sum_v outside (CN(root,v)-2)^2`. No floating point acceptance is involved.

Success for possible direct warm input is at least one root with all 84
outsiders having CN2 and a seven-edge perfect matching neighborhood. This is a
candidate scaffold only until the existing exact scaffold interface is separately
checked. Absence means only these two actual graphs provide no such direct root.
It is no graph exclusion or search coverage claim. Save every root, every tie
and minimum residual under the predeclared v1 minimum/smallest-label selection.
No favorable omissions, automorphism assumption, complete annealer trajectory,
target resolution or ledger/Git/index changes are authorized.
