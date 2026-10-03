# Static falsification review of the C4 endpoint checker V2

Reviewer: `/root/checkpoint_audit`. This is a source and written-proof review,
not an executed calibration, producer-artifact approval, or ledger action.

Exact reviewed sources:

- `acceleration/audit_20261003_triangle_kernel_c4_endpoint_v2.py`, SHA256
  `4714c255caddc6840a210af1e0fd38e9b1eafb3f54418f2c24b36abe66dcf182`.
- V2 specification, SHA256
  `d678dcae0c8890cd797c656ec0404a61a2f82f849f6293aab0cacd43b6a9598c`.
- `acceleration/audit_20261003_triangle_kernel_c4_endpoint_v1.md`, SHA256
  `d464ee1b3522a0e61784031b2f47efcc4ecf84926dcc64e306f6f2855e384ea0`.

The preserved V1 specification and new producer V2 source were also read to
compare scope and independence. No producer endpoint output was read or
execution requested. The checker imports no mathematical discovery code.

No major static veto was found. The fresh calibration and subsequent complete
raw checking remain separate requirements. In particular this opinion does
not establish that the producer has supplied a valid endpoint certificate.

## Derivation and independent checking path

The written normalization includes the unique zero codeword: character
orthogonality gives sum over all kernel words of K_j(weight)=M*D_j, hence
sum over nonzero weights of A_w*(L_j-K_j(w))<=C(99,j)-L_j. Positive
denominators permit normalization. A nonnegative complete dual whose weighted
column sum is at least one at every permitted weight therefore bounds M-1,
so M<=1+sum(y). This allows the zero kernel; it assumes neither a nonzero
kernel nor an upper bound on rank. The exact threshold U<8192 implies a
linear-kernel dimension at most twelve and rank at least eighty-seven.

The independent coefficient path expands (1-z)^w(1+z)^(n-w) by integer
polynomial convolution. Its rational Gaussian elimination differs from the
producer's binomial character sum and closed two-by-two inversion. Full mode
checks all 13 by 99 literal coefficients, all 99 nonnegative dual entries,
all 13 inequalities, the reduced rational format, the complete endpoint
system, and the coordinate relation between normalized and unnormalized
duals. It does not infer feasibility merely from the two endpoint equalities.

The required N5 lower count is 22869, and old12474 mutations are rejected.
The conditional even36..60 interval, complete low-count derivations, and
their artifact closures remain explicit trusted prior dependencies. Their
universal truth is not proved by the new arithmetic fixtures.

## Controls and attempted failure cases

The source contains 23 certificate/model mutations, four tiny endpoint
mutations, one singular-system check, one zero-word-omission check, and three
producer metadata mutations: 32 total. The rejection harness requires the
exact ValueError type and diagnostic; a wrong-stage exception cannot satisfy
a control. The literal-character population through n=6 is
sum((n+1)^2,n=0..6)=140. The complete rook image and kernel counts are32
and16, and the target synthetic construction checks all1287 coefficients,
99 coordinates and13 inequalities without constructing the target endpoint.

The physical V2 tiny expectation z4=2/39 is consistent with the denominator
C(9,4)-9=117 and y4=6. Its normalized y5=9 likewise gives z5=1/13.
The original V1 expectation2/3 is preserved as an unexecuted calibration
error, not a mathematical refutation of the normalized dual.

Raw reduced rational values reject booleans, floats, nonpositive denominators
and unreduced pairs. Scope/metadata identity uses typed canonical JSON, and
boolean optimum/self-approval fields use explicit identity checks. Truncated
dual or coefficient rows, altered character signs, denominator drift,
fabricated bounds/ranks, old fifth-count assumptions, and wrong weight
domains are covered by the proposed exact-stage controls. These are static
coverage observations; the actual outcomes are not asserted here.

## Remaining requirements and limits

ROOT must execute and inspect the fresh V2 calibration before any separately
authorized producer run or complete checking invocation. Full checking must
authenticate actual calibration/producer/supervisor hashes, source pins,
all input/output closures, and observed contained termination. The raw
certificate is sufficient only within the written conditional target scope.
No optimizer optimum, graph construction, nonexistence, nonzero kernel,
rank upper bound, external review, novelty, or target-wide coverage follows
from this checker or this source-only review.
