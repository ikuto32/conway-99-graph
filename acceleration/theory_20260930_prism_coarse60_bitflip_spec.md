# Fixed coarse60 component-bit normalization protocol

Question: does the fixed coarse60 bitlift formula have a satisfying assignment
if and only if it has one with all six coordinate bits of column zero equal to
zero? This is a candidate relabelling equivalence within the frozen six-prism,
60-distinct-coarse-column family, not a claim covering every prism factor.

Before execution, freeze these limits and checks: build-only, 120 seconds, no
solver or RNG. Pin the independent base encoding gate and all raw inputs. Leave
the old formula and pilot unchanged. For each of the 64 component-flip masks,
save the explicit 36-row permutation, 2,448-selector permutation and 360 signed
bit-literal images. Check core and Gram invariance and local-mask transport.
Check all 135 compatibility tables under the four possible endpoint-component
flips. Check column-equality invariance by exhaustive local Boolean controls.
Confirm all 64 possible first-column bit words have exactly one normalizing
action. Prefix auxiliary variables are recomputed as exact Boolean prefixes;
they are not asserted to admit a variable permutation.

Derive six negative unit literals by selecting column=0 records from raw_bits
metadata, one for each component. Append exactly these units to the unchanged
base clause body, changing only the DIMACS clause count (expected 85,704, with
5,238 variables). Save exact bytes, all maps, source/command/version/hash records,
lossless gzip companions, calibrated positive and deliberately corrupted local
controls. No known complete research factor is required or claimed by controls.

Success means only a fully recorded candidate equivalence for independent
review. Failure preserves the evidence and forbids promotion or solving. A
separate reviewer must approve coverage, full byte suffix and object checking
before any new research solve. The target remains UNKNOWN.
