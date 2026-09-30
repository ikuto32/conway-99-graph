# Independent balanced fixed-support exclusion

The complete 227,098,316-byte ASCII DRAT proof was independently replayed
against the exact 10,480-variable, 74,200-clause balanced Gram formula.
The source-authenticated checker returned exit0 and `s VERIFIED`.

The conclusion is narrow: no binary36-by60 factor on the frozen six-prism
Hadamard coordinate support satisfies both the prescribed integer Gram and
the extra coordinatewise balance of each three-column identical-support
group. All150 normalized local choices per group were included. Outside-
column caps were not needed for this exclusion. This is not an exclusion of
all factors on the support, the core, or the unrestricted target.

The mathematical bridge is the separately reviewed complete encoding at
`acceleration/results/20260930_independent_review/hadamard_balanced_gram_cnf_v2/summary.json`
(SHA256 `b63a4de43c1bcf4de56c52e4b4cc3ae8c697a3198654eb3f44d97bce7549ea7c`).
It includes the harmless independent relabeling of each equal-support triple,
the full150-choice enumeration and every clause. No target automorphism,
cyclic restriction, previous parity exclusion or cap hypothesis is added.

The proof input is
`acceleration/results/20260930_hadamard_balanced_gram_cnf/instance.cnf`
(SHA256 `c2d780f94dac4dda955743df03f8db2e8ec0f51217c671eb19fc5e42ed69ba37`).
The proof is
`acceleration/results/20260930_hadamard_balanced_gram_native_pilot/main/proof.drat`
(SHA256 `94d2ab35c76b61f3deb01ebfd9ca0dc70452bddf847383d5838b2b2ca902396b`).
The replay report is
`acceleration/results/20260930_independent_review/hadamard_balanced_gram_unsat_v2/summary.json`
(SHA256 `edbbda720ea38ca5c565837bc39b5083eb145a64386c9e070fe89dfe5d6cebc5`).
The raw trace remains LOCAL_ONLY until a public recovery package is recorded.

The checker executable is the preserved successful MSVC build with SHA256
`23d1613cb0b1ed491f4e723ff82492a8be6c349c2426d440412842c5246b90ac`.
The audit reauthenticated upstream commit
`2e3b2dc0ecf938addbd779d42877b6ed69d9a985` via immutable Git blobs, the exact
reviewed Windows portability patch, patched source, compiler/build records
and executable. The dirty tools submodule was neither read as source nor
modified. This is not a fresh compiler-diversity or formal checker result.
The checker implementation, compiler, runtime and reviewed portability shim
remain trusted; the SAT solver's UNSAT claim is not trusted on its own.

Before the research replay, an exhaustively checked two-variable formula with
a nonempty reasoning trace was accepted. The following were rejected: an
empty-only proof of that formula, a proof containing an unjustified fresh
unit, the valid tiny proof against a satisfiable changed formula, and an
empty-only proof against the actual research CNF. Six corrupt native-record
controls were also rejected. Every original input/output and command is
hash-bound in the report. No solver was rerun by the reviewer.

The first new verifier stopped during checker authentication because it
incorrectly interpreted the portability patch as replacing a deleted include
line. The immutable patch instead retains that include as context and inserts
the conditional block around it. The failed source and receipt are preserved.
The v2 verifier applies the full single context hunk and compares every byte
of the patched source with the authenticated successful build. No formula,
proof, producer artifact or checking algorithm was altered.

Reproduce from the repository root with a new output directory:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_balanced_gram_unsat_v2.py --out NEW_DIRECTORY
```

The script invokes only the checker and read-only provenance/process tools.
Each complete checker call has a180-second ceiling. A timeout is preserved
as a failed replay attempt and is never promoted to a proof.
