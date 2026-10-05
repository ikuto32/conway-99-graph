# Independent wave27 publication metadata audit

This protocol is frozen before executing its checker. It reviews publication
metadata and literal bytes only. It neither reapproves mathematical statements
nor runs a solver, proof checker, registrar, checkpoint writer, Git mutation,
or publication command. Wave27 is the immutable 286-claim cutoff, with 281
VERIFIED, three CANDIDATE and two REFUTED claims; eight additions are VERIFIED.

The source hard-pins the final catalog, stage inventory, multipart reference
manifest, ledger and checkpoint, completed checkpoint consistency gate, guide,
raw recovery manifest/helper, replay plan/receipt, stager and precommit receipt.
It authenticates all current bytes named in those inputs. Next32 and first12
union outputs, protected private logs, PROMPT.md and tools submodule contents
are outside its allowed reads. The two explicitly named local solver/checker
binaries are hash-only provenance dependencies, never executed.

The audit independently enumerates the explicit directory/file allowlist and
checks all 2,514 selected records, including 2,500 public payloads and 14 local
originals. It reconstructs the complete multiset of 319,663 reference bindings
from saved JSON and ledger evidence, compares all 13 compressed reference
parts, and checks 6,062 unique identities. The only historical ledger alias
allowed is an exact one of the six registrar validation.json origins resolving
its CLAIMS.yaml reference to its own immutable CLAIMS.after.yaml with the exact
expected hash. Inherited public/recoverable dependencies retain their prior
catalog scope. No unresolved references are ignored.

Publication research payloads remain at most 10 MiB each. Only the exact final
catalog/stage/reference-manifest metadata wrappers have a 32 MiB ceiling; all
other wrappers/parts remain at most 10 MiB. The stage list must equal the public
payload plus exactly the named wrappers, never the 14 raw originals. All Git
clean-filter hashes are checked against literal Git blob hashes for the staged
paths and explicit supplements; Git index and HEAD must remain unchanged.

All 14 gzip members are independently decompressed with zlib, checking one
complete member, offsets, sizes and part/whole hashes and literal equality to
the retained originals: 158,441,925 raw bytes. This is byte recovery, not proof
acceptance. Corrupted member tails, extra members, offsets and hashes must fail.

Guide commands are parsed and checked against static argparse declarations.
All ten replay commands are compared to their original saved commands, source
hashes and expected statuses, allowing only the documented output/interpreter
changes. The actual parent replay receipt's 33 copied logs/reports are checked
literally against its fresh local build outputs and ten exit-zero results.
Those build paths remain LOCAL_ONLY diagnostic references, not a new public
mathematical closure or a second independent implementation. The metadata
review does not launch the replay again. The 56 registry tests and timestamped
1,828-source syntax census are checked only as recorded engineering outcomes;
that census may include later local sources outside this publication selection.

Controls additionally delete a stage/reference entry, inject an excluded raw
original and add an unsupported CLI flag. Each must be rejected. The checker
uses only Python standard library, PyYAML and read-only Git commands; it does
not import producer or former audit modules. Its reference reconstruction and
zlib paths are separate from the catalog/restorer implementation. The general
metadata implementation is adapted from the previous independent wave26 audit,
disclosed in the report.

Run with locked offline uv and a fresh output directory:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_twentyseventh_publication_metadata.py --out acceleration/results/20260930_independent_review/twentyseventh_publication_metadata
```

The cooperative allocation is 300 seconds. Success requires all checks to pass
and emits INDEPENDENT_TWENTYSEVENTH_PUBLICATION_METADATA_PASS. Any failure is
saved without editing the source or input artifacts; a correction requires a
fresh version/output with an explicit failure binding. A successful gate is
publication metadata consistency only, never target resolution or proof scope
expansion. Audit artifacts and four entry documents are explicit staging
supplements, avoiding circular catalog references.
