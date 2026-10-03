# Independent complete phase enumeration for the saved case01 branch

The population is the kernel over GF(3) of the independently reconstructed
172-by-120 homogeneous matrix for one authenticated parity assignment. There
are twelve mixed and eight constant support groups. The checker derives the
matrix from the raw support and selected signs, and uses descending pivot
columns and reverse row selection, separately from the producer's leftmost
RREF. Rank113 gives dimension7. The seven saved independent basis vectors
satisfy every equation, and the free-coordinate argument establishes that they
span the entire kernel. All3^7 coefficient tuples, including zero, therefore
give exactly2187 distinct vectors. Their full120-coordinate vectors are matched
bijectively to every producer record; equality of vector hashes alone is not
used to assert coverage.

Why this kernel covers a balanced lift: in each group of three identical
supports, coordinatewise balance makes each coordinate's color map a
permutation of three colors. Every such permutation is uniquely affine,
pi_i(x)=s_i*x+t_i over GF(3), with s_i=1 or2. A common permutation of the three
identical-support columns fixes the first coordinate's map to the identity.
This preserves the Gram matrix and all column intersections; it is a
relabelling, not an assumed automorphism of a target graph. The authenticated
parity assignment fixes the signs in precisely this gauge. The independently
checked general phase-necessity theorem supplies the172 homogeneous equations.

The checker evaluates the actual three affine color columns for each local
group. Each must have two entries of each color. For a mixed group this is
equivalent to phases0,1,2 each occurring once on each sign class. For a constant
group it is equivalent to phase multiplicities2,2,2. This equivalence is also
calibrated exhaustively on all729 phase tuples for each of the two sign types;
there are36 valid mixed profiles and90 valid constant profiles. Constant groups
are not subjected to a mixed-group distinctness condition.

Every research vector fails one of these literal local conditions. No vector
reaches the pair-Gram, full-factor, or outside-column stages. Thus the exclusion
does not require an assertion about those unexecuted research stages. The
generic factor arithmetic is calibrated separately on the independently
checked SRG(243,22,1,2) fixture and deliberately corrupted copies; this is not a
positive Conway99 factor or a member of the fixed-support branch.

The result excludes only the exact saved case01 parity assignment within the
coordinatewise balanced fixed-support family. It does not exclude the full
Hadamard support, a core, or the unrestricted target. It is an exact finite
enumeration with all records preserved, not an UNSAT solver claim. The original
producer input-pin and raw-field mistakes stopped before enumeration; their
sources and failure records remain intact and are bound as historical evidence.

Shared checking code is the frozen independently authored parity-system and
linear-algebra checker. The new local color, literal factor, and complete
enumeration path imports no producer code.
