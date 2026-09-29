# Scope clarification for the immutable candidate certificate

The certificate SHA256
`d08d8bc72221181aba7ce3e73374bf0a04c6c94ab925230890ced2020da9194b`
contains the phrase "not implied merely by the weaker CNF" in its scope text.
That wording belongs to the earlier local59 encoding and does not describe this
full99 encoding. The correct interpretation is:

The clause follows from the target Gram identity within the recorded fixed
family. Once the independent full99 encoding-equivalence gate passes, the clause
is also implied by that exact CNF. Adding a checked clause would be redundant
strengthening for solver guidance, not an additional graph assumption or a
restriction to a smaller target family.

This clarification changes no integer vector, coefficient, Boolean value,
maximizing corner, clause, quadratic, raw artifact or artifact hash. The original
certificate and producer are retained unchanged. Independent checking of the
candidate clause remains necessary before it is used.
