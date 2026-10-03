# Exact Wave40 receipt finisher V3: frozen approved universe

Source SHA256: `d49507851370afe6875bc6712946f4102e07a24b3733b5d6d4bc784084064ad1`.
Preserved V2: `e87ef83fe8196027213cb891bc7226962a489c5c0c03dd58b44dc51a9c624d55`.
The inherited V2 scope and shared components are recorded in its unchanged spec.

Independent source review found that V2 accepted the current staging NUL without
binding its identity or population. ROOT had already executed V2 before that
review arrived. Its actual report and receipts remain preserved; this weakness
does not refute the exact initial apply check or change a mathematical claim.
V2's acceptance of an arbitrary staging-list universe must not authorize a
publication. V3 repeats the selected-byte and complete raw-index checks with
the exact immutable list bound explicitly.

V3 requires the apply report's population 1439, and the list must have a trailing
NUL, exactly 1439 nonempty distinct members, and SHA256
`13e31c3dc836a75940de14ca4667f83e53847c104ec53c621e6d0c82a262293b`.
The actual complete list is a positive control. Truncation, duplication, missing
trailing NUL and one altered member are rejected at their precise declared
checking stages before staging starts.

The current index after the completed V2 appendix is separately bound to
`96a3b9509e9c7f8d11ef98cff25d3ebba229755c0b28c234b91d44f4f8ec4508`.
That is a new reviewed starting index; it is not presented as the earlier
apply index. The exact ledger, apply report, prior source, registry checks,
document suffix checks and bounded marker controls retain their V2 conditions.
The selected list plus explicit completed receipt appendix are checked against
their raw Git blob identities, with outside entries and Gitlinks preserved.

Use the supported supervisor before locked/offline uv: 120 seconds outer,
100 worker, 20 shutdown, and at least 20 worker save reserve. Success requires
all four precise list-corruption controls, the 1439 bound universe, raw Git byte
checks, unchanged outside entries and a reaped empty Windows Job. This is
engineering verification only; no scientific work, ledger edit, commit, push,
artifact availability promotion or mathematical replay is performed.
