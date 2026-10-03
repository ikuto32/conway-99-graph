# Correction and static veto of the physical V2 rook endpoint control

Reviewer: `/root/checkpoint_audit`. Preserve the earlier source-only review
`acceleration/audit_20261003_triangle_kernel_c4_endpoint_v2_review.md`,
SHA256 `c96332afedda33c6839ff8439ef31d982a3ec287d7c616a77e049803d63567ad`.
Its assertion that the proposed degree4/5 rook control has normalized
y4=6,y5=9 and a sharp U16 is wrong. The reviewer missed this substantive
control error. No execution or actual endpoint approval was performed by
this reviewer.

Affected exact sources:

- Physical checker V2, SHA256
  `4714c255caddc6840a210af1e0fd38e9b1eafb3f54418f2c24b36abe66dcf182`.
- Checker V2 specification, SHA256
  `d678dcae0c8890cd797c656ec0404a61a2f82f849f6293aab0cacd43b6a9598c`.
- Producer V2, SHA256
  `91df2f1b782f0e7b8d30478a1e338deab6fb8341ea686b50983acf5d2892a531`.
- Universal target normalization note, SHA256
  `d464ee1b3522a0e61784031b2f47efcc4ecf84926dcc64e306f6f2855e384ea0`.

## Independent exact falsification

At length nine, the character polynomial at weight four is

    (1-z)^4 (1+z)^5 = (1-z²)^4 (1+z).

Its degree4 and degree5 coefficients both equal6. At weight six,

    (1-z)^6 (1+z)^3 = (1-z²)^3 (1-z)^3,

whose degree4 and degree5 coefficients both equal -6. The rook image lower
counts L4=L5=9 therefore give the unnormalized endpoint matrix

    [[3,3],[15,15]].

Its determinant is exactly zero. Both the independent checker's Gaussian
elimination and the producer's closed inversion must reject this degree4/5
system before it could yield the advertised sharp rook certificate.

The degree4 and degree5 denominators both equal C(9,4)-9=C(9,5)-9=117.
For the asserted normalized y4=6,y5=9, the weight-four inequality is

    6*(3/117) + 9*(3/117) = 15/39 = 5/13 < 1.

Thus this literal dual is invalid. Merely correcting the proposed z4 from
2/3 to2/39 in physical V2 did not fix the control. These calculations use
small integer polynomial products and exact rational arithmetic by written
derivation; they do not rely on agreement with another agent or producer
execution.

## Correct separate rook control

Using degrees four and six gives K6(4)=-4 and K6(6)=8, so the normalized
columns are

    G4=[1/39,5/39],  G6=[5/39,-1/39].

The valid nonnegative dual y4=9,y6=6 gives both row sums exactly one and
U=1+9+6=16. The corresponding unnormalized values are
z4=9/117=1/13 and z6=6/78=1/13. These values describe a replacement
control; they do not approve changed producer/checker execution.

## Impact and unmet requirements

The exact proposed toy certificate is REFUTED by the failed inequality.
The physical V2 calibration design is vetoed and the earlier no-veto
review must not be used as an admissibility gate. Its unaffected statements
about character normalization, target scope, coefficient population and
independent algorithms are not thereby refuted.

The length99 degree4/5 endpoint candidate remains UNKNOWN. This length9
singularity neither proves nor disproves the target endpoint certificate,
the rank87 conditional theorem, or Conway-99. Preserve the old sources,
specifications, review and any actual receipts. New versioned producer and
checker sources, a newly calibrated nonsingular rook control, and separate
complete literal target artifact checking are required. No old gate transfers.
