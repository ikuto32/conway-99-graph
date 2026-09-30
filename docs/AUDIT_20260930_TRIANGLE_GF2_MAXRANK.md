# Conditional binary-field mixed-equation redundancy

This independently reviews the root researcher's proposed conditional lemma.
It claims no novelty and uses no Gram, graph automorphism or prism-free
premise. The known243 fixture calibrates the checker; it is not a Conway99
candidate. The finite failed perturbation screen is motivation, not a premise.

Let F be a3n-by-m matrix over GF(2), with its rows partitioned into three
nonempty n-element cells. Let r_i be their three indicator vectors and j
the all-ones3n-vector. Assume

    r_i^T F=0 for i=0,1,2,
    rank(F)=3n-3,
    r_i^T C=j^T for i=0,1,2.

The last condition is a left-action condition. In the intended triangle-core
application, C is symmetric and C r_i=j, so it follows. A right-action
condition on a nonsymmetric matrix is not silently substituted for it.

Then there exists an m-by-m matrix D over GF(2) satisfying

    F D = 2J_(3n,m) - (I+C)F.

Proof: the three indicators are independent, since their nonempty supports
are disjoint. They lie in the left kernel of F. The rank premise makes that
kernel exactly their span. Write H=2J-(I+C)F. In GF(2),2J=0 and

    r_i^T H = -r_i^T F - r_i^T C F
             = -j^T F
             = -(r_0+r_1+r_2)^T F = 0.

Consequently every column of H is orthogonal to the left kernel of F. The
column space of F equals this orthogonal complement: it is contained there
and both spaces have dimension3n-3. Each column of H therefore has a
preimage under F. Choosing those preimages as the columns of D proves the
claim. This is a full linear-algebra proof for all stated matrices, not an
inference from samples.

No symmetry, zero diagonal, degree condition, integer mixed equality or
quadratic residual identity for D is established. In a valid triangle factor,
each column has two ones per cell, so the left-kernel premise holds modulo2;
the maximal-rank premise must still be independently checked. For the actual
known243 factor it holds at rank57. The same implication would apply to a
Conway99 factor at binary rank33. It says nothing about lower ranks and is
not a target existence/nonexistence result.

The lower-rank countercontrol uses n=4, three standard internal matchings and
identity cross matchings. Let u have local support{0,2} in every cell and let
all four columns of F be u. Then rank(F)=1, the three cell-parity conditions
hold, and Cu=j+u. Thus every column of H is j, which is outside span(u), so
FD=H has no solution over GF(2). This countercontrol satisfies the weakened
cell-margin assumptions only; it is explicitly not claimed to have the
prescribed incidence Gram or to be an actual graph factor.

The exact checker validates the independently approved243 raw fixture and
its actual D, recomputes binary rank using column XOR elimination, and saves
raw pivot columns and elimination identities. It checks the lower-rank
counterexample literally. Exhaustive2-by3 binary matrices calibrate rank
against complete column-span enumeration. Changed parity, left action, rank
and mixed RHS controls are rejected. These calibrations support the code;
the written proof above establishes the quantified theorem.
