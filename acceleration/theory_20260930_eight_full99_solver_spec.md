# Preregistered full99 conditional SAT pilot orchestration

Preparation and tiny-control calibration only until an independently authored
complete encoding gate passes. The research input is exactly the full99
eight-coordinate CNF SHA256
`f247be8432d69f4feec037833a6923ef623e20c0aa0dbdea77fd13ec218d095b`,
with model SHA256
`f2b7a649e74aa476380e14066239a188a2d2122d2ba1cc6e330e9a094d2cc0ee`.
It has485165variables and1684724clauses and retains120fixedK edges,189fixed
scaffold edges,2160unknown edges and all recorded prescribed absences.

Question: does this exact conditional full99 model yield a complete graph
candidate or a complete proof artifact within300solver process seconds and
1000000conflicts? Use one proof-enabled CaDiCaL195 call, deterministic defaults,
through the already frozen worker. Parsing, loading and proof extraction count
within the300-second limit. No retry, altered thresholds or silent timeout
extension is allowed in this pilot. Bounded worker termination overhead is
measured separately through the actual returned process receipt.

The new orchestrator source, this protocol, raw CNF/model, encoder/decoder,
pure graph validator, pinned environment lock, PySAT Python source versions,
native module hash, authenticated checker build receipt and binary hash are
bound before a call. The research CLI requires the independently supplied gate
file and its exact expected hash. Tiny SAT and proof-producing UNSAT controls,
raw assignment corruption and invalid proof controls run first in a separate
calibration directory. Calibration does not resolve a research instance.

On SAT, save the complete assignment, explicit99-by99 adjacency matrix and
producer-side exact validation record. All remain CANDIDATE pending separately
authored assignment/CNF/scope/full99 checks. If a complete raw model exists after
a native cleanup failure or missing worker receipt, preserve and decode it
without changing the actual process outcome; independent raw artifact checks
determine its mathematical significance.

On UNSAT, preserve the exact complete native DRAT trace without manufacturing
an empty clause. A raw proof is retained even when cleanup failed. No exclusion
is promoted before independent encoding equivalence review and authenticated
proof replay. Any exclusion is limited to this120-fixed-K family. A timeout,
error or incomplete proof is UNKNOWN and does not refute feasibility.

Packaging receives a separate120-second/8GiB limit after the solver has stopped;
it cannot extend solver time. Preserve raw artifacts if packaging fails.
Lossless gzip stream parts remain individually below10MiB and include ordered
reassembly/decompression instructions and raw/compressed hashes. Record actual
worker exits and cleanup anomalies explicitly, with no claim they were fixed
by successful tiny controls. No process is described as running after exit.

Run `--calibrate --out FRESH_CALIBRATION` to exercise only tiny formulas. The
research command uses `--calibration FRESH_CALIBRATION/controls.json`,
`--encoding-audit AUDIT`, `--encoding-audit-sha256 HASH`, and `--out FRESH_RUN`.
Both commands use `uv run --project acceleration/environments/rook-sat --locked
--offline --cache-dir .uv-cache-20260917 python` from the repository root with
`UV_PROJECT_ENVIRONMENT` set to the absolute `build/rook-sat-venv` directory.
