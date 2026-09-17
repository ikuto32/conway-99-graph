# Public-commit replay audit, 2026-09-17

Published input commit: `3daebfb05d39aa31afea6fdbb6b80d6b108f1262`.

The frozen fresh16 checker passed all sixteen exact rational case checks after
explicit relocation of four original-workspace paths. Its outputs for each case
and its one positive/six corrupted controls exactly match the published saved
report. This is repeated execution of an existing independent implementation,
not another independent mathematical derivation or claim promotion.

The unmodified checker invoked without relocation failed immediately under a
file-access guard because a historical input hash points to an absolute original
workspace source path. This is a portability defect, not a mathematical
refutation. `direct_controls_wrapper.json` preserves the exact rejected path and
failure. No inherited workspace input was read successfully through that path.

`replay_published_checker.py` imports the byte-identical checker extracted from
the published Git commit, changes only its `path` resolver when `--relocate` is
explicitly supplied, and guards file opens. It permits the isolated extracted
directory, exact output paths, and the installed Python environment. Paths from
other data roots and traversal components are rejected. Six mapping controls
exercise both accepted mappings and rejected traversal, other-root, and prefix
collision paths. Raw artifacts and mathematical checking functions are unchanged.
The wrapper records every opened isolated file's hash, mapped path, rejected
external access, and source/output digests.

## Availability and executed scope

The saved checker runtime inventories name 129 unique input paths for fresh16,
17 for the baseline matrix checker, and 99 for the triangle checker. These sets
overlap. Their union plus inventory/environment records comprises 230 extracted
paths and 67,052,947 bytes. Every required runtime inventory hash matches a blob
at the published commit; no required runtime path is missing. Extraction uses
`git show COMMIT:path` exclusively, without local-file fallback.

The fresh16 replay completed sixteen cases with zero denied external data reads
under the relocation wrapper. Every actually opened isolated input also matches
the extraction manifest. Existing complete-domain enumeration audits remain
hash-bound prerequisites; their exhaustive enumeration is not rerun here.

Triangle's five perfect-matching fixtures and the windmill edge/corruption
fixture passed under isolation. Its full 73-million-subset enumeration was not
rerun. For triangle this audit establishes availability of its saved 99-path
runtime input inventory and successful calibration only. It does not claim a
new full triangle mathematical check. The baseline inventory is hash-checked;
its full matrix checker is not rerun in this audit.

## Failed attempts and explicit scope adjustment

The first extraction rejected an absolute original-workspace hash path. The
second attempted to recurse through every historical producer provenance
inventory and reached its declared 300 MB limit after retaining 1,776 Git-only
files (299,843,010 bytes). These inputs led into unrelated prior GPU-ranking
histories, which the frozen checkers only hash or never open.

Both failed protocols and the partial extraction are preserved. `retry2` narrows
the extraction claim to actual saved checker runtime inventories. Deeper
producer-history references remain listed separately and are not claimed to be
replayable. The isolation directory retains extra byte-identical Git files from
the capped expansion; the successful checker's actual open-file inventory is
matched against the final runtime manifest, so those extra files are not silently
used as an unrecorded dependency.

Earlier uncommitted extractor source revisions were not snapshotted before
revision. Their hashes survive in the two failed protocols, but their exact
source artifacts are MISSING. This limitation is explicit in the receipt; final
successful extractor and wrapper sources are retained and hash-bound.

## Reproduction

Install the environment using the repository's committed `uv.lock`. From the
repository root, choose a new destination and output directory (existing evidence
is never overwritten):

```text
uv run --locked python acceleration/audit_public_replay.py --commit 3daebfb05d39aa31afea6fdbb6b80d6b108f1262 --destination build/public-replay-new --out acceleration/results/public-replay-new
uv run --locked python -I acceleration/replay_published_checker.py --root build/public-replay-new --original-root C:/Users/ikuto/projects/conway-99-graph --checker acceleration/audit_20260917_fresh_review.py --relocate --run acceleration/results/20260917_fresh_star_shortlist --report acceleration/results/public-replay-new/fresh16-wrapper.json --checker-out acceleration/results/public-replay-new/fresh16.json
uv run --locked python -I acceleration/replay_published_checker.py --root build/public-replay-new --original-root C:/Users/ikuto/projects/conway-99-graph --checker acceleration/audit_20260917_triangle_matching.py --relocate --controls-only --report acceleration/results/public-replay-new/triangle-controls.json --checker-out acceleration/results/public-replay-new/triangle-unused.json
```

The actual interpreter was the existing pinned research environment, Python
3.12.10. Fresh16 uses only the standard library; triangle calibration also uses
the locked tqdm installation. No network clone or fresh package installation was
tested. Exact actual commands, working directories, source hashes, output hashes,
and elapsed time are in wrapper reports and `replay_receipt.json`.

The frozen checker retains its historical source-commit and verifier strings.
The wrapper and receipt bind this run to the actual published commit and mark it
as repetition. No unrestricted graph, nonexistence proof, or overall search
coverage measure follows from this availability and replay audit.
