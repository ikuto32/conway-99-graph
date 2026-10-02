# Independent exact code-dual checker v1

Freeze this source and written derivation before any full producer-output
inspection. No producer imports, binomial alternating-sum routine, numerical
library or solver invocation is used. A separate recurrence reconstructs all
Krawtchouk coefficients and requires exact integer divisibility at every step.
The normalized operator uses K_j(0) from that recurrence, not floating values.

Calibration first: all character sums n0..6, complete length4 full code,
length3 even code, complete rook9 incidence kernel, two exact small duals and
seven strict syntax/coefficient/sign/inequality/linearity controls. Supported
60outer/40worker invocation is sufficient for tiny known populations and has
10seconds outer shutdown guard; code never invokes a numerical optimizer.

Full checking is separately authorized after calibration. Exact raw n99,
weights36,38,...60, all99 degrees and coordinates, every13x99 model coefficient,
all13 inequalities, rational sum bound and integral power-of-two consequence
are reconstructed. Actual negative-coordinate, zero-dual, changed bound and
changed model coefficient controls must fail at their precise stages. Pin all
producer/checker sources, raw model/certificate, report and actual receipt.

The written character/MacWilliams argument supplies a universal conditional
statement; finite controls alone do not prove it. The separately reviewed
incidence weight premise is explicit. A checked dual proves only its own exact
bound, not optimum, an incidence rank upper bound or target nonexistence.
