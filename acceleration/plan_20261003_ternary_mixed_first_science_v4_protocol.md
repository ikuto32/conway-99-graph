# Mixed F3/E pilot: separate invocation after setup allocation veto

This plan preserves the V3 plan and its failed invocation. Invocation
6f7990458c3e4c42ab033a460f8fb318 ended after 72.917606677 seconds with
`EXACT_NATIVE_ALLOCATION`. At the failed worker boundary, elapsed time was
72.45679008 seconds and remaining time was 1027.54320992 seconds. The unchanged
worker required the exact 1000-second native guard plus 30 seconds for
preservation. No native launch file, native directory, native state, or scientific
result was produced. This is an engineering setup outcome, not a negative graph
search result.

V4 proposes a separate command with 1400 seconds outer allowance and 1300
seconds inclusive wrapper allowance. The exact native guard remains 1000
seconds, with 995 seconds cooperative native time, 30 seconds preservation and
20 seconds outer shutdown. This permits at most 270 seconds of setup before the
worker's unchanged exact-allocation check. The measured authentication cost is
72.45679008 seconds; I/O variance remains uncertain. The allowance is a ceiling,
not a duration target. Prior command time is not subtracted from this invocation.

Only the two wrapper/outer allocation values, allocation rationale, output
generation 02 and append-only failure provenance change. SCI3, SUP2, binary,
build, gates, graph input, seed, proposal count, temperatures, cooling, trace,
checkpoint and resource limits remain byte-preserved. The expected native vector
changes only its output directory. No retries or automatic dispatch are enabled.

Paper inspection of Saved4 confirms that `run_options` reads literal runtime
limits, `native_receipt` binds the exact plan and actual command, and full mode
requires wrapper seconds plus 20 to be at most the observed outer allowance.
There is no fixed 1100/1200-second requirement in the applicable saved checker.
This is interface inspection only; the existing seven-positive/68-negative
calibration is preserved. Actual complete saved objects still require the
separate independent Saved4 full audit.

Launch requires ROOT review of all literal vectors and a fresh sanitized
both-host ownership/resource/default-UID1000 admission, current protected
context, small direct pins and absent output paths. Complete immutable gate
hashing remains inside the unchanged wrapper's 1300-second deadline. A failed
admission or allocation stops without retuning, source changes or automatic
retry. Any retained F3 zero requires prompt independent full integer target
validation. Sparse saved proposals do not imply a complete trajectory.
