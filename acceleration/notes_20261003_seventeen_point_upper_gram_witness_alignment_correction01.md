# Written correction: alignment of the class-I short witness

This append-only note corrects the orientation of the short witness in
`docs/CANDIDATE_20261003_SEVENTEEN_POINT_FOUR_CLASS_UPPER_GRAM_V1.md`, SHA256
`1750e24a5d2a5664778efeaf9a86fa9d6774a8f7daee9d87e96c4e614f8dcf67`.
That frozen candidate is preserved. Its complete invariant-block inertia table
and the existence of a negative direction are unchanged by this correction.

For class I, label the common row pairs {1,2} and {3,4}, with ell adjacent to
F1,F2 and r adjacent to F3,F4. The displayed witness must use chi1=chi2=+1,
chi3=chi4=-1 together with w(ell)=+1 and w(r)=-1. Equivalently, the endpoint
signs must agree with their attached row signs. Then the four endpoint-free
edge products sum to +8, the total edge-product sum is 79, and w^T U w=-8.

If chi alone is reversed while those endpoint coordinates stay fixed, the
endpoint-free products sum to -8, the total edge-product sum is 63, and
w^T U w=150-126=24. Thus the frozen phrase "one common partition pair" did not
adequately specify its alignment. Reversing the entire vector, including both
endpoint coordinates, is harmless and retains the negative value.

Native's different-author written review identified this boundary, and Root
requested a new correction rather than alteration of the frozen paper. This
note is written arithmetic only: zero matrix programs, numerical eigensolvers,
formal proof executions or external verification. It approves no candidate,
extra-edge extension, target occurrence or ledger change.
