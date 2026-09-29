# Candidate bounded29vertex extension screen

Freeze the first four saved closed28 cases at each center0 through7, giving
32 matching-specific graphs, in saved order. For each, try all71 outer
vertices outside its28vertex set, in increasing full99vertex label order.
The population is2,272 graph/extra-vertex pairs; each pair may have a different
number of allowed assignments. No graph/count weighting is implied.

Use only the independently authenticated eight-coordinate domain family:
120fixed outer edges,2,160unknown outer pairs, and every other outer pair
fixed absent. Reconstruct these sets from the frozen baseline and released
coordinate rule and compare the saved domain manifest. The first15vertices
form the exact root/seven-triangle scaffold; outer-to-inner edges are fixed
by the outer label. The saved complete neighborhood of the second center u
forces `u-w=0` for an outside vertex w.

The only unsettled entries in the principal29matrix are w's edges to the
12outer neighbors of u. Include all required fixed-one edges, forbid all
fixed-zero edges, and enumerate all remaining subsets satisfying
`|N(u)∩N(w)|=2` after counting the known inner common neighbors. All other
global edges remain unspecified, not fixed absent.

For every assignment, check all induced pair caps exactly. For cap survivors,
screen both `27I-9A+J` and `A+4I` with float64 eigenvalues and threshold
`minimum < -1e-8`. Numerical values are guidance only. Attempt exact negative
integer vectors using rounding scales1,024;1,048,576;1,073,741,824. Accept an
exact negative quadratic only with literal Python-integer double summation.
Preserve raw29matrices/vertex labels and every assignment, including failures.

Stop at the first pair with no cap-and-numerical survivor, preserving its
entire finite assignment universe and exact/inexact rejection distinction.
This is at most a candidate exclusion of one matching-specific closed28
graph, pending independent coverage and certificate review. It cannot
exclude the star without covering its other possible matchings.

The wall limit is120seconds per invocation, checked between graph/w pairs.
Pairs are the resume unit; completed immutable pair files are reused only
under exact source/input identity. A partial run remains incomplete. Before
the loop, calibrate cap checks on rook9 and deliberately corrupted K4,
both numerical PSD screens on rook9, and exact negative directions for
the upper Gram matrix on K5 and lower Gram matrix on K5,5. Enumeration is
calibrated against all Boolean assignments of a six-variable fixture.
