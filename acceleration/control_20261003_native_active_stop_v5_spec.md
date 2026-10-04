# Active-stop current-snapshot correction V5

SOURCE_ONLY. Preserve Control V4 8bff71034ca219a846a2c0298b1d4c4cee89575815e6bd50cb499df9f7b8ac3f,
its spec, sat_hard04 native/readiness/terminal and failed post stderr unchanged.
ROOT observed a successful seven-second hard stop with a reaped empty original
group, but the separate post parser rejected legitimate unrelated WSL init rows
with PGID/SID zero before preserving its observation. The failed post remains
incomplete evidence; this is not a claim of a persistent native escape.

The only process-domain change is check_process(row, current=False). Default
False keeps saved guard, saved worker/children and readiness identities strictly
positive in PGID and SID. Only assessment's fresh current-row loop passes True,
allowing nonnegative PGID/SID for current snapshot rows. Exact int types continue
to reject bool/float, and negative identifiers remain invalid. Known selected
live objects still veto even if their current group/session is zero or changed;
the unchanged original guard must match its saved positive group/session.
Context, unknown proc objects and numeric group-generation logic remain fail
closed. No saved provenance is widened or relabelled.

The post path saves raw_snapshot.json before assessment with all literal rows,
unreadable PIDs and opening/closing/saved context. Schema or semantic assessment
failures save veto.json and retain the raw hash; semantic vetoes additionally
retain observation.json. A failure before a current snapshot can be collected
is not falsely represented as a collected snapshot. No retry, repair, new kill
or permission inference is added. Output generation05 and source hash disclose
this version; wire V3 saved-identity tags remain unchanged.

SUP V2 464102, SCI V3 d1e250, Bash foreground309a, fixtures, native vectors,
readiness interval, budgets and all six separate case/post shapes are unchanged.
Before any V5 native case, new same-author synthetic identity V2 must retain the
original six-positive48-negative population and exercise current PGID/SID zero,
strict saved zero rejection, bool/float/negative fields and exact-known live veto.
ROOT separately reads all fixtures/results and actual case receipts/context/
current-process objects. Old finite gates do not approve changed observation.
The trusted kernel assumption and finite scope in V3 spec remain explicit.
