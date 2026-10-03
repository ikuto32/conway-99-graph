# Direct-cell native calibration supplement

The first independent encoding audit passed. Preserve its source and report.
The native preflight additionally needs exact identities of sibling native
specifications, the dynamically loaded direct-cell preflight source/spec, and
both local executables. A separate calibration-only wrapper adds those identities
to the original checker's pin map before invoking its unchanged calibration mode.
It binds its own source and this specification too. No encoder, model, equations,
thresholds or previous evidence are changed. This is source/protocol calibration,
not a second independent mathematical derivation or native solver call.

The wrapper refuses other modes. It parses the explicitly supplied driver path,
uses the independent checker's static local-import closure, and records existing
sibling specifications without importing or launching any native/producer code.
The tools are pinned to the already calibrated CaDiCaL1.9.5 and DRAT binaries.
All original positive/corrupted controls and full formula checks run again.
The original encoding-gate hash and new driver/spec hashes are mandatory on the
command line. Fresh output is exclusive and any failure is preserved.
