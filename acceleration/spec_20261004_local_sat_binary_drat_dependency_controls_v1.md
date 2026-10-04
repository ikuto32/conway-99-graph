# Dependency-bearing binary DRAT controls

SOURCE_ONLY; no compiler, solver or proof checker was invoked for this packet.
This appendix corrects the finite proof-control design in the preserved native
V2 specification and controls plan V3. Native independently found that the old
CRLF lemma could be skipped by the default backward checker, and that the old
Ctrl-Z byte occurred after a unit already made the formula propagation-conflicting.
Neither old positive established the intended byte-sensitive coverage. Preserve
their exact bytes and the written veto. The launcher, Linux builder, their source
diffs, native five-case vectors and containment components do not change.

Use the proposed new Linux checker from the preserved upstream source. Every
proof-check vector remains null until Root authenticates its actual executable,
build acceptance and (where used) the fresh native proof. Each separate check
uses the supported Linux supervisor: 60 outer seconds, 30 internal checker
seconds and 20 shutdown seconds. No automatic chain or retry is authorized.
Keep default backward UNSAT checking; do not add a forward-mode or RUP-only flag
to make these tests pass. Different-author raw byte/record/EOF and RUP/RAT review
is required in addition to the authentic terminal and exact status line.

## Ctrl-Z must precede the necessary lemma

The preserved four clauses on variables 13 and 14 are
`(13,14),(13,-14),(-13,14),(-13,-14)`. The new five-byte proof is
`61 1a 00 61 00`, additions `(13),empty`. Testing `(13)` assumes `-13`;
the first two clauses force `14` and `-14`. After adding `(13)`, the last
two clauses force `14` and `-14`, validating empty. Both steps are necessary:
the initial formula has neither a unit nor a propagation conflict.

The explicit truncation file is just `61`. This is the byte prefix left before
the sensitive payload is read. In the pinned parser, `read_lit` receives EOF
at shift zero and returns EOF; no first lemma is inserted. With the original
nonunit formula the expected result is exit 1 and exactly `s NOT VERIFIED`.
Raw independent decoding must additionally reject its missing record terminator;
this is an intentionally incomplete record, not a well-formed empty proof.
Unexpected parser behavior is a preserved failure, not a waived negative.

## CRLF must occur in a necessary clause

The new six-clause formula is
`(-6,5,2),(-6,5,-2),(-5,3),(-5,-3),(6,1),(6,-1)`.
There is no initial unit or propagation conflict. The new nine-byte proof is
`61 0d 0a 00 61 0d 00 61 00`, additions `(-6,5),(-6),empty`.

* The first clause is RUP: assumptions `6,-5` make the first two clauses
  force `2,-2`.
* The next unit `-6` is RUP only after that lemma: assumption `6` makes
  the lemma force `5`, and the two `(-5,±3)` clauses force `3,-3`.
* With unit `-6`, the two `(6,±1)` clauses force `1,-1`, validating empty.

The translated eight-byte counterfactual deletes the `0d` immediately before
`0a`, so it is `61 0a 00 61 0d 00 61 00`, additions `(5),(-6),empty`.
Unit `(5)` is not RUP: assumption `-5` leaves the two split pairs `(-6,±2)`
and `(6,±1)`, with no unit. It is not RAT either: its opposite-pivot clauses
`(-5,3)` and `(-5,-3)` yield resolvents `(3)` and `(-3)`. Negating either
resolvent forces only `-5`, leaving the same two split pairs and no conflict.
In default backward checking `(5)` is marked: its addition immediately makes
the `(-5,±3)` clauses conflict, so it cannot be discarded as an unused lemma.
Expect exit 1 and exactly `s NOT VERIFIED`.

The five-byte missing-lemma counterfactual is `61 0d 00 61 00`, additions
`(-6),empty`. Unit `-6` is not RUP: assumption `6` leaves `(5,±2)` and
`(-5,±3)`, without any unit. It is not RAT: resolving with `(6,±1)` gives
the two units `±1`; negating either forces only `6` and leaves those same
split pairs without conflict. The invalid unit is marked because it makes
`(6,±1)` conflict. Expect exit 1 and exactly `s NOT VERIFIED`.

The two valid positives and all three counterfactuals therefore exercise
dependency-bearing bytes, rather than a disconnected syntactic decoration.
The earlier intermediate proposal rejected by Native because its translated
unit was RAT remains rejected; this appendix does not rehabilitate it.

## Complete finite qualification scope

The successor has the unchanged five native cases and nine proof-check cases:
three positive checks (fresh native, Ctrl-Z-first, CRLF-dependent), the three
preserved negatives (empty-only, fresh native proof on SAT, incomplete original
clause), and the three new counterfactual negatives above. Each expects the
literal child code and one exact `s VERIFIED` or `s NOT VERIFIED` line as
declared, null errors, no deadline, reaped and observed-empty original Linux
group, and no cleanup errors. SUP's nonzero-child status is preserved verbatim.

The old Windows text checker remains unchanged and unqualified for arbitrary
binary input. Actual new outcomes, binary identity and Root acceptance are
still null. No scientific formula is read, no mathematical result or claim
status changes, and no I/O performance improvement is asserted.
