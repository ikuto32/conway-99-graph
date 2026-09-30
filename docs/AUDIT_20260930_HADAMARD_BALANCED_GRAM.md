# Independent complete balanced Gram encoding review

This review concerns one frozen six-prism core and one frozen Hadamard support
L. It imposes the additional balance condition on each three-column group of
identical support. Neither the support nor balance is assumed universal for
Conway-99. All constant and mixed local options are included. No cyclic
exclusion, nonconstant-group clause, earlier sampled parity exclusion, or
outside-column cap is a premise of this encoding.

In a balanced group, each of its six coordinates occupies all three fibres
once, and each column uses two of each fibre. Permuting the three identical-
support columns makes the first coordinate's fibre sequence (0,1,2). This is
relabeling columns, preserving L and every Gram entry, not assuming an
automorphism. A normalized group is exactly an unordered triple from the
ninety length-six words having two copies of each fibre, with distinct fibre
values in every coordinate. Sorting its three words orders their distinct
first coordinates as (0,1,2). The independent checker enumerates all
binomial(90,3)=117480 triples and retains precisely 150, independently of the
producer's 6^5 permutation traversal. The order used for selector IDs is then
reconstructed by lexicographically sorting the coordinate permutation tuples.
All 150 choices, including 30 constant and 120 mixed parities, are retained.

Every coordinate is supported in ten groups. A balanced group contributes one
to each corresponding fibre-row's diagonal Gram entry and zero between two
different fibres of that coordinate. Matched coordinates never share support.
For every other coordinate pair a<b there are five shared groups. A group's
three columns contribute a permutation matrix: its entry (x,y) is one exactly
when the fibre at b, in the column where a has fibre x, is y. Thus each of
the sixty nonmatching coordinate pairs contributes the required block
2J-I precisely when all nine integer cell counts are enforced. These 540
equations, the local domains and support therefore give all 1296 entries of
the prescribed36-by36 Gram. Row and fibre-column margins also follow. The
checker independently derives the prescribed matrix from literal core
adjacencies and common-neighbor intersections.

The first 3000 variables select group choices. Each group has an exact-one
prefix encoding: the first prefix equals its first selector; each subsequent
prefix is equivalent to the OR of its predecessor and the next selector,
with their simultaneous truth forbidden; the last prefix and last selector
form XOR. Induction proves that the prefixes are the unique running-OR values
and exactly one selector is true. All 2980 prefix variables are thus defined.

For each pair/group, the six relative-permutation indicators are each
bidirectionally equivalent to the OR of their selector population. The local
one-hot makes exactly one of these six indicators true. A matrix-cell flag
is bidirectionally the OR of the two indicators whose permutation maps x to
y. For each cell, direct subset clauses enforce exactly one (diagonal) or
two (off diagonal) of its five flags. At-most k forbids every k+1 true subset;
at-least k forbids every 5-k+1 false subset. These are exact integer counts,
not relaxations. Every auxiliary is uniquely determined by the selectors.

The independent review reconstructs every selector and auxiliary ID, every
clause offset and all literal clauses. The expected populations are 3000
selectors, 2980 prefixes, 1800 relative indicators and 2700 flags; the four
clause populations are11920,46800,8100,7380, totaling74200. The model has10480
variables. Small prefix relations, ORs and five-bit counts receive exhaustive
truth-table controls, including auxiliary uniqueness. Complete literal
relative-permutation controls check orientation and avoid an inverse mistake.

The raw object checker independently builds F from the selected color words,
checks the complete integer Gram, binary shape, exact L, balance, margins and
normalization, and explicitly constructs and inversely checks the canonical
C0 column permutation. It computes all1770 outside-column intersections and
2160 mixed-cap entries as diagnostics; a Gram factor with a failed outside
cap is retained and labeled as such. No residual D is encoded or inferred.
Complete native/JSON10480-variable agreement and all74200 actual clauses are
required before accepting a research object.

Calibration uses the independently authenticated nonempty SRG243 factor as
a genuine positive of the generic integer Gram/margin/cap checker. It is not
a positive of the research support or balanced subfamily. Full-size synthetic
native/assignment/clause controls exercise the codec separately. Reversed
columns, altered entries, invalid dimensions, changed domains/channels/counts
and corrupt native models are checked. No complete research Gram factor is
invented for calibration. The current lack of such a control is explicit.

Shared code consists of the separately authored frozen oriented-model
assignment/native parsing and clause-format helpers, whose generic10480-ID
behavior is freshly calibrated. No producer module is imported. Mathematical
coverage is rederived directly and uses only the fixed support claim, not a
prior parity exclusion or cyclic branch result.

Use the locked research environment from the repository root:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_balanced_gram.py audit --out NEW_DIRECTORY
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_balanced_gram.py calibrate --encoding-gate PATH --encoding-gate-sha256 HASH --driver NATIVE_SOURCE --out NEW_DIRECTORY
```

Actual SAT checking uses `sat --encoding-gate PATH --encoding-gate-sha256 HASH
--assignment JSON --native-output LOG [--decoded JSON] --out NEW_DIRECTORY`.
No solver runs in any checker mode.
