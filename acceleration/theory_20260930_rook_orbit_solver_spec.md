# Fixed-scaffold orbit SAT pilot

Question: does the frozen 780-edge local family remain satisfiable after all
352 independently checked images of eleven necessary Gram clauses?

Use every clause in the frozen cnfpart, without a symmetry assumption on any
target graph. Use CaDiCaL195 with proof logging, default options and no changed
seed. Run one call with a 300-second process budget and 1,000,000-conflict cap.
The budget includes parsing and loading. A cap is an UNKNOWN result; no retry is
part of this pilot. Source and inputs are hashed before launch.

Positive success is a complete assignment independently checked against every
raw clause, the fixed scaffold, all block degrees and all 59-vertex pair caps.
It remains only a local witness. A later negative Gram certificate requires a
separate exact checker. UNSAT success requires the complete saved proof and a
separate replay on these exact bytes, plus the existing scoped encoding and cut
gates. No result covers arbitrary central factors or the unrestricted target.

No numerical acceptance threshold enters SAT or proof claims. Raw artifacts and
actual worker exits are preserved, including failures after saving an object.
Post-solve independent checking is capped at 120 seconds and packaging at
120 seconds. Any incomplete check remains pending. Compressed parts are exact
byte concatenations; hashes do not substitute for proof checking.
