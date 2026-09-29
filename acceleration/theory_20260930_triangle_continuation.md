# Triangle-root continuation, 2026-09-30

The selected next experiment is complete99vertex extension of the single displayed
Wave154 Q1 factor, with the residual60vertex adjacency blockD included. Its new
CNF has been built; no solver has been invoked. It remains a conditional candidate
encoding pending independent propagation, complete encoding and SAT-object gates.

## Pinned archive assessment

Archive repository: `https://github.com/YesterdaysLemon/conway-99-research`,
commit `85e705cc6c2a14d123120c93a847e30aaab1789e`.
The exact files read are hash-bound in the preflight manifest. No archive files
were edited and no historical VERIFIED label was adopted as fresh verification.

* Wave149 specifies a root triangleT, three12vertex groupsAi and60verticesB.
  For its displayed witness allMi are the standard matching, F01=F02=I and
  F12 is shift6. The archive's PSD projection is only a necessary local condition;
  this continuation does not freshly certify its PSD/rank argument.
* Wave151 provides one exact24by60 incidence factorC01, followed by a fixed-Q1
  Z3 UNSAT diagnostic taking40.46seconds without a proof trace.
* Wave154 provides another displayed Q1 outside the first's recorded local
  symmetry orbit, with another unproved Z3 diagnostic. Its portfolio explicitly
  includes a180second CaDiCaL195 proof-export attempt ending without a proof.
  Neither the two Q1 cases nor the fixed scaffold cover all hypothetical targets.

Source scope records:
`attempts/wave149-terwilliger-triple/derivation.md`,
`attempts/wave151-triangle-root-factor/{derivation.md,fixed_q1_q2_scout.py,fixed-q1-q2-scout.json}`,
`attempts/wave154-triangle-factor-portfolio/{derivation.md,exact-results.json}`,
and `verification/wave151-triangle-root-factor/derivation.md`.
These paths are relative to the pinned archive. The local384element symmetry
group in Wave154 is a symmetry of that frozen finite witness, not an assumed
automorphism group of a target graph.

## Cheap falsification actually run

`theory_20260930_triangle_factor_preflight.py` independently formed the60nonmatching
edges, rebuilt the displayed36by36 Gram entries from their formulas, and replayed
both rawC01 matrices. No archive producer code was imported.

For each Q1, twelve prospective C2 rows were tested against the24linear cross-Gram
equations over each of2,3,5,7,11,13. All144case/row/prime checks were consistent.
Each larger2088equation necessary joint C2/D system was also GF2-consistent, with
rank1621 in2490variables. These are failed falsifiers, not binary feasibility
certificates. The exact raw systems and controls are saved at
`results/20260930_triangle_factor_preflight/`.

`theory_20260930_triangle_partial99.py` then built the actual99vertex partial
adjacency and propagated exact degree/common-neighbor interval constraints.
All ordered forced-entry reasons and both initial/final matrices are saved.

| Fixed family | Forced entries | Remaining C2 entries | Remaining D edges | Outcome |
|---|---:|---:|---:|---|
| Wave151 Q1 | 562 | 459 | 1469 | Fixed point, UNKNOWN |
| Wave154 Q1 | 563 | 457 | 1470 | Fixed point, UNKNOWN |

Every forced entry is zero. Producer controls restored a masked edge in three
known SRGs and rejected a flipped edge in each complete fixture. An independent
agent is replaying the complete inference sequence; these counts are recorded
producer results until that gate is attached. The propagation run took0.203seconds.

## Why this differs from the existing searches

An unrestricted triangle relabeling by itself does not reduce the current3486
outer variables. Fix a root vertex and one of its seven neighborhood matching
edges as the root triangle. The remaining12neighbors formA0; the84outside vertices
split into12A1,12A2,60B. The unknown pairs are132withinA1/A2,144betweenA1/A2,
1440betweenA1/A2 andB, and1770withinB, totaling3486. This is a reorganization of
the present unrestricted root scaffold, not a new target-wide reduction.

The newly chosen fixed-Q1 full99 problem is different from the archive's C-only
factor task. It enforces residualD compatibility and every target equation.
Selection of Wave154 was made before building because its propagated family has
1927unknown graph entries versus1928for Wave151. No runtime advantage is claimed.

## Concrete prepared experiment

`theory_20260930_triangle_full99_cnf_spec.md` freezes the conditional scope and
build protocol. `theory_20260930_triangle_full99_cnf.py` has produced:

*1927 graph-edge variables,104024 exact AND variables and323525 exact prefix
variables, for429476total variables;
*1486729clauses, enforcing all99degree equalities and all4851pair equalities;
*raw CNF/model/scope plus replayed gzip companions smaller than10MiB.

The saved CNF SHA256 is
`4b9c05bb01ac76340c6f72e314c4ee84317facb687e9a32a79094f6fce85d8ea`;
the model SHA256 is
`983723dbb211fe02e805046fe2c7a6f5fbb9032eab8afe51edee21dc7b2efb79`.
Build time was12.5seconds with166776832bytes recorded peak working set.

After the independent gates, the intended first solver experiment is one native
300second proof-enabled CaDiCaL call, with4GiB address space and10GiB proof cap,
using the calibrated ext4 artifact path. Its exact command and new scope-specific
object checker must be frozen before launch. A positive decoded full99 graph
would require independent validation of `A²=12I−A+2J`. An independently replayed
UNSAT proof would exclude this single fixed family only. The target remains
UNKNOWN; overall search coverage has no validated denominator.

All new Python commands use the existing pinned environment, for example:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/theory_20260930_triangle_factor_preflight.py
uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/theory_20260930_triangle_partial99.py
uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/theory_20260930_triangle_cnf_census.py
uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/theory_20260930_triangle_full99_cnf.py --out acceleration/results/20260930_triangle_full99_cnf
```

These producers refuse to overwrite saved output directories. Replays must use
an isolated checkout or an explicitly new output revision; do not erase originals.
