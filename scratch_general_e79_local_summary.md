# Solver-free local obstruction at `E0=79`

The compression audit forces sixteen `C4` fibres and five `P4` fibres.  Let
`H` be the graph on the seven matched-pair groups whose five edges are the
five `P4` supports.

At an endpoint of a `P4`, each support coordinate has one missing BP symbol
quota.  Ordinary `C4` fibres cannot carry an overlap edge, because their own
two support-coordinate quotas are already saturated internally.  Therefore
every endpoint port must be paired to another exceptional fibre through its
shared group.  In particular, `H` cannot have a vertex of degree one.

There are exactly 20,349 five-edge support sets.  A direct enumeration gives:

| stage | labelled sets | `S7` orbits |
|---|---:|---:|
| all five-edge sets | 20,349 | 21 |
| no degree-one group | 462 | 2 |
| port-compatible | 0 | 0 |

The two intermediate orbits are `K4-e` (210 labelled copies, stabilizer 24)
and `C5` (252 copies, stabilizer 20).

To see the last obstruction analytically, at one support coordinate a `P4`
endpoint pair has opposite actual signs and needs the opposite signs (`T`
type).  At the other coordinate the two actual and needed signs are a common
fixed sign (`S_c` type).  Compatible overlap edges join only `T--T` ports or
`S_c--S_c` ports with the same `c`; `T--S` is impossible.  At every group of
degree two or three all incident port types must consequently agree.  Since
each `P4` support has one `T` end and one `S` end, `H` would have to be
bipartite.  But `K4-e` contains a triangle and `C5` is odd.

As an independent finite check, all `4^5=1024` labelled `P4` orientations
were enumerated for each of the two support representatives.  Both have
exactly zero overlap completions.  See
`scratch_general_e79_local_audit.py/.json`.

The local obstruction is analytic and solver-free once the five-`P4`
distribution is known.  The earlier compression step which forces that
distribution retains its stated lack of a formal proof certificate for its
bounded disjoint-integer exclusions.
