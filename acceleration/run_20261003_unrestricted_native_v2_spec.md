# SAT launcher V2: foreground inner guard

SOURCE_ONLY. V1 `run_20261003_unrestricted_native_v1.sh` (SHA256
b6d3dbbb2ed567d35b4d99fe9d3ec90e0dbae5dabc4a764277b9e50686d72a6c)
and its actual invocation/incident remain byte preserved. The sole source change
is adding `--foreground` to the inner GNU timeout. Arguments, uid1000 check,
allowed10/3300 durations, exact checksum verification, resource limits and
CaDiCaL argv are unchanged. New source SHA256 is
309a36d272ce292dc4484bd25ee1cf9c9093a63d99eee12a1329fcb64f8f17f8.

GNU timeout's default inner process group escaped the supervisor group in the
saved901223 invocation. The proposed flag prevents that particular group creation.
It does not prove containment of arbitrary setsid/daemonized descendants. A finite
control must observe actual descendant groups while alive and exact identities
after the stop; the unchanged supervisor's original-group-empty field alone is
insufficient. No old normal-exit controls approve V2 active-stop behavior.

The separate `control_20261003_native_active_stop_v1.py`/spec/plan declare six
independent contained invocations, with live native and ordinary descendant
coverage under a hard boundary and missed short reassessment. These remain
unexecuted pending ROOT whole-source/array review, fresh resources/admission and
separate independent artifact checking. The actual SAT input is a generated
generic pigeonhole fixture, never the unrestricted99 formula. A fixture finishing
before active-stop observations fails that case; no size increase or retry occurs.

The mixed science wrapper6e293 already launches GNU timeout --foreground,
without start_new_session, and checks child PGID equals its own PGID. No change to
that source/spec is proposed. Its active binary-profile cases cover the timeout /
prlimit / binary shape on cube12 only; they do not exercise the actual scientific
wrapper's gates, selected graph or complete run path and cannot approve those
untested branches. All control source/output approval is finite and version bound.
