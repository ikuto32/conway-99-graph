# Independent component balance and fixed-factor overflow audit

The underlying scope is the single fixed 39-vertex triangle core and its
binary 36-by-60 incidence factor C already audited in the base joint-factor
encoding. No choice of Q1 or Q2 is fixed by that base problem.

Delete the triangle from the raw core. Its cubic 36-vertex induced graph
has three connected components S0,S1,S2, each of order twelve. Each component
meets each of the three fibres in four vertices. The independent checker
obtains these components by reachability in its own raw adjacency matrix.

Let K be the forced Gram matrix derived entrywise from the target identity.
Exact integer multiplication verifies K(1_S0-1_S1)=0 and
K(1_S0-1_S2)=0. For any real factor CC^T=K and either contrast v,

    sum_d ((C^T v)[d])^2 = v^T CC^T v = v^T K v = 0.

Every square is nonnegative, so every coordinate of C^T v vanishes. Thus
all three component sums are equal in each column. The base factor's three
fibre sums are two, so each column contains six ones altogether. Since the
three components partition the 36 rows, each component sum is exactly two.
This argument is over the real numbers but its concrete kernel certificate
is checked entirely with exact integers; it uses no floating-point bound.

The added 180 equations therefore hold for every factor in the unchanged
base family. Each equation includes the complete component's rows for one
column. The checker folds only fixed C0 entries and forced zeros from the
authenticated base scope, reconstructs the complete counter truth relations,
and compares every appended clause. It also compares the strengthened raw
CNF byte-for-byte with its changed header, unchanged complete base body,
and exact suffix. The new auxiliaries provide unique threshold extensions.
Consequently the strengthened and base formulas have the same primary
solutions; no factor family restriction has been added.

For each of five exact recorded Q1 permutations, independently reconstruct
C0 and C1 as edge-incidence matrices and verify all 24-row Gram entries and
margins. If a component already contains three ones in one column of these
24 fixed rows, no nonnegative C2 can reduce its sum to two. This is a direct
nonextension certificate for that exact Q1, regardless of any residual
60-vertex graph. The counts of overflowing (component,column) positions
are 3,1,1,1,1. These are five fixed-factor exclusions, not a census of all
Q1 choices or a general nonexistence proof.

The audit reuses its previously frozen independent raw-core/Gram builder
and truth-relation GateAudit helper. It imports no producer. Fresh malformed
kernel, partition, overflow and clause controls are retained. The base
encoding gate remains a declared dependency rather than being silently
reapproved by repeated execution.
