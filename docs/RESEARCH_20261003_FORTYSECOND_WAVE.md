# Forty-second research milestone, 2026-10-03

Since [wave41](RESEARCH_20261003_FORTYFIRST_WAVE.md), thirteen claim revisions
were added: four graph diagnostics or ternary results, seven written ternary
support results, and two exclusions of fixed move families. The accepted ledger
has 371 claims: 363 VERIFIED/CLEAR, three CANDIDATE/CLEAR and five REFUTED/CLEAR.
All earlier claim, artifact, target and availability records were preserved.

**As of:** accepted cutoff 2026-10-03T07:01:29.5527618+00:00, source context
`63437c9b9fc2dd58b3bdfb51fc347b880b397503`,
[frozen ledger](../acceleration/results/20261003_wave42_registration03/CLAIMS.after.yaml),
SHA256 `a0ed6dfb9716266e44dd8cdbef00620266190fa1bce0852a11bbabbf8d09416e`.
The context commit does not contain all new working files. The previous report
is wave41. This document prepares publication; new evidence remains LOCAL_ONLY
until immutable publication and availability checking are recorded.

**Verdict:** target resolution UNKNOWN. This repository has no independently
validated 99-vertex target graph or general nonexistence proof. No external
resolution review is recorded. [Draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3)
remains the review reference; no claimed resolution is merged.

**Verified changes:** every entry below is revision 1. Verification is limited
to the recorded statement and assumptions. The three separate bookkeeping
audits check the [first four](../acceleration/results/20261003_independent_review/wave42_four_transition_v2_actual01/summary.json),
[next seven](../acceleration/results/20261003_independent_review/wave42_seven_transition_v1_actual01/summary.json),
and [final two](../acceleration/results/20261003_independent_review/wave42_two_census_transition_v1_actual01/summary.json)
transitions. These audits preserve the mathematical verification records;
they do not repeat the mathematical calculations or proofs.

| Claim ID | Exact recorded scope |
| --- | --- |
| C-FIXED-LAMBDA1-REGULAR14-TRIANGLE-INCIDENCE-GF3-RANK98 | One fixed degree-14, lambda-one graph has triangle-incidence rank 98 over GF(3). The graph fails the target identity; this is not a target rank exclusion. |
| C-FIXED-ROOTFOCUSED-SELECTED45369-COMPLETE99-ROOT-RESIDUALS | One selected non-SRG graph has positive residual at every root, minimum 10 and sum 10688. No target or global root assertion. |
| C-UNRESTRICTED-DEGREE14-TERNARY-RESIDUE-ENERGY-BOUNDS | Every simple 99-vertex degree-14 graph satisfies F3 <= E <= 28 F3 and the stated exact residue constraints. |
| C-UNRESTRICTED-DEGREE14-TERNARY-ADJACENCY-EXACTNESS | For every such graph, F3=0 is equivalent to the complete integer target adjacency identity. |
| C-UNRESTRICTED-DEGREE14-TERNARY-SMALL-DEFECT-SUPPORT | Necessary signed-support constraints exclude F3=1,2,3,5; the four-edge support characterization alone asserts no realizability. |
| C-UNRESTRICTED-DEGREE14-TERNARY-FOUR-DEFECT-NONREALIZABILITY | F3 cannot equal 4 for any such graph. |
| C-UNRESTRICTED-DEGREE14-TERNARY-SIX-DEFECT-NONREALIZABILITY | F3 cannot equal 6 for any such graph. |
| C-UNRESTRICTED-DEGREE14-TERNARY-CONNECTED-SUBCUBIC-SUPPORT-RESTRICTION | The whole nonempty connected defect support cannot have at most 12 vertices and maximum degree at most 3. |
| C-UNRESTRICTED-DEGREE14-TERNARY-CONNECTED-SUBCUBIC-SUPPORT-LOWER45 | The whole connected subcubic support satisfies the stated exact part-size inequality; it has at least 45 vertices, or 47 when nonbipartite. |
| C-UNRESTRICTED-DEGREE14-TERNARY-CONNECTED-SUBCUBIC-SUPPORT-SPANNING99 | A whole nonempty connected subcubic support must span all 99 vertices. Spanning supports are not excluded. |
| C-UNRESTRICTED-DEGREE14-TERNARY-SEVEN-DEFECT-NONREALIZABILITY | F3 cannot equal 7 for any such graph. |
| C-ROOTFOCUSED-STRICT-LEX-STEP1-FIXED-TWO-LINE-CENSUS | One fixed input has no lambda-preserving strict root-residual descent in its complete 224784-label exclusive two-line family. |
| C-ROOTFOCUSED-SELECTED145287-RESTRICTED-THREE-LINE-CENSUS | One selected input has no lambda-preserving move in its complete 187650-label declared oriented three-line family. |

The root [claim ledger](../CLAIMS.yaml) and frozen ledger bind each exact
statement, dependency revision, raw artifact and independent verification.
The energy objective is the sum over unordered vertex pairs of squared
integer residuals CN(u,v)+A(u,v)-2. F3 counts those pairs with nonzero residual
modulo 3. Both are minimized; numerical or heuristic zero is not a certificate.

**Work completed:** the seven written support results, together with the
ternary constraints, establish F3=0 or F3>=8 for every simple 99-vertex
degree-14 graph. The eighth-defect paper and later construction experiments
are outside this frozen cutoff. The connected-support results concern the
whole support, not an arbitrary component inside a larger support.

The independently checked two-line family has 114 minimum-root ties and
selects proposal 145287 with lambda energy 0, mu energy 5292 and root residual
10. Its graph fails 5370 ordered entries of the integer identity. The
[complete raw census](../acceleration/results/20261003_independent_review/root_focused_strict_lex_step1_full01/summary.json)
and [selected-object check](../acceleration/results/20261003_independent_review/root_focused_selected145287_projection_full01/summary.json)
remain separate checking records.

The [restricted three-line check](../acceleration/results/20261003_independent_review/restricted_three_line_target_full01/summary.json)
covers exactly 187650 role labels: 78540 invalid-linearity labels, 13458
invalid-selection labels and 95652 valid labels, all changing lambda energy.
It checks all 38 parts and checkpoints. There is no selected or zero object.
This is one fixed oriented CN1/CN3 selection family, not all three-line moves.

**Coverage:** two new fixed-family exclusions and zero new general
nonexistence results. Their overlapping graph populations are not added.
The earlier 380/792 literal branch union and its 412 unresolved branches remain
unchanged. Overall search coverage: UNKNOWN; no validated denominator.

**Best result:** the exact F3=0 equivalence and F3>=8 lower restriction on
nonzero defects give necessary algebraic constraints. They do not establish
existence, nonexistence, an optimum, or a percentage of Conway-99 solved.
The fixed root-residual result is interpreted only under its own objective.

**Problems:** preserved source-only argument-array errors, rejected drafts,
earlier failed runs and corrected versioned sources remain evidence. The
registrar's historical `new_exclusions=0` engineering field is not used to
count the two exact new fixed-family exclusions. Missing headline fields in
older raw reports remain explicitly unavailable; the raw bytes were not
rewritten to create a statement. No timeout or failed implementation is
treated as mathematical refutation.

**Execution and next experiment:** saved terminal receipts establish the
completed cutoff; this milestone infers no live worker from a historical PID
or document. Later independently checked ternary-neighborhood and engineering
results, and the separately admitted unrestricted SAT run, have their own
records and lie outside these 371 claims. The next construction action is
to optimize from the independently checked complete-neighborhood selected
graph after its changed input and saved-output paths pass independent checks.
The next SAT action is to inspect the exact native outcome and independently
check any complete object or proof. A partial trace remains UNKNOWN.

**References:** [registration and validation](../acceleration/results/20261003_wave42_registration03/summary.json),
[ROOT cutoff acceptance](../acceleration/results/20261003_wave42_two_census_acceptance_record01/summary.json),
[previous checkpoint](RESEARCH_20261003_FORTYFIRST_WAVE.md), and
[explicit publication inventory proposal](../acceleration/proposal_20261003_wave42_milestone_inventory_v1.md).
The proposal predates completed registration03; its prospective wording is
historical and is superseded by the actual records above.
