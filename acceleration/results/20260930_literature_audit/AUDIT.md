# Dated primary-source and frozen-registry audit

Access date: **2026-09-30 Asia/Tokyo** (2026-09-29 UTC). Source repository
commit: `90f1a32de21faea3519c3635677d5739f86ad734`. Auditor:
`Codex subagent /root/state_literature_audit`. The exact receipt timestamp is
in [registry_pointer_audit.json](registry_pointer_audit.json). Previous report:
`docs/LITERATURE_20260917.md`, bound by its Git-blob hash in that receipt.

This is a source inspection and bookkeeping audit. Newly found literature
observations are **CANDIDATE** pending separate review. It does not promote
external mathematical theorems to freshly verified project claims.
The unrestricted target remains **UNKNOWN**. No target graph, general
nonexistence proof, or external target review was obtained in this lane.
Overall search coverage: UNKNOWN; no validated denominator.

## Changes and useful findings

The previous three-abstract inspection is no longer the latest source coverage.
[Thakkar–Severini, arXiv:2608.11211v2](https://arxiv.org/abs/2608.11211v2)
lists a revision on **2026-09-18 17:29:15 UTC**, after the repository stop.
[Full text](https://arxiv.org/html/2608.11211v2), sections 2.1–2.4, 3–5,
was inspected. Section 3 reports a four-vertex switch tabu search and a partial
artifact score of `3501/4950`, counting 99 degree and 4,851 unordered-pair
constraints. Its displayed partition is `99+549+2853=3501`. This is a reported
heuristic result, not an independently checked artifact in this audit, and
its score is not comparable to the repository's star-relaxation objective.
Sections 4–5 explicitly disclaim resolving existence. The 84-vertex root
reduction in section 2.3 overlaps the repository's existing scaffold work.
The score artifact and exhaustive circulant enumeration were not replayed.
The July v1 date despite the `2608` identifier remains an unresolved metadata
inconsistency; no deduction relies on that v1 date.

**Do not treat the paper's order-7 discussion as an established new open case.**
Section 2.4 calls that symmetry case open, conflicting with the older primary
sources below. This is a citation/scope warning, not a newly replayed exclusion.
No automorphism is assumed by this project's unrestricted target.

## Primary sources and exact inspection scope

| Source/version | Sections checked and result | Audit boundary |
|---|---|---|
| [Brouwer SRG parameter table, orders 51–100](https://aeb.win.tue.nl/graphs/srg/srgtab51-100.html), dynamic page accessed on the audit date | Exact `(99,14,1,2)` row carries `?`, with eigenvalue multiplicities `3^54,(-4)^44`. | Registry observation only; not proof of worldwide openness. No page version identifier was supplied by the source. |
| [Cesarz–Woldar, Algebraic Combinatorics 8(2), 379–398 (2025), DOI 10.5802/alco.418](https://alco.centre-mersenne.org/item/10.5802/alco.418.pdf) | Publisher PDF introduction pp.379–380; Corollaries 3.13 and 4.15. Their own results condition even group order on divisibility by 6, and divisibility by 7 on the group being cyclic of order 7. The introduction separately attributes exclusion of all prime orders except 2 and 3 to Behbahani–Lam, and exclusions of orders 6 and 9 to Crnkovic–Maksimovic. | Distinguish their computer-free conditional theorem from the stronger computational literature they cite. Full proof and earlier computation not independently replayed. |
| [Crnkovic–Maksimovic, Contributions to Discrete Mathematics 15(1), 22–41 (2020), DOI 10.55016/ojs/cdm.v15i1.62323](https://cdm.ucalgary.ca/article/view/62323) | Publisher abstract and indexed publisher PDF Theorem 7.3, p.40: possible group order has form `2^a*3^b`, `b in {0,1}`; order-3 automorphisms are fixed-point-free; order 6 is excluded. | Publisher PDF retrieval was intermittent: one successful open, subsequent text finds/access timed out. The exact theorem was corroborated through the search index of that primary PDF, not a new computational audit. |
| [Behbahani dissertation, Concordia University (2009), Theorem 4.14](https://spectrum.library.concordia.ca/id/eprint/976720/1/NR63369.pdf) | University-hosted indexed PDF states only primes 2 and 3 can divide the full automorphism group order, with no fixed points for order 3. | Direct legacy-URL fetch failed. This is an indexed-primary attribution supporting the above discrepancy, not an independently checked exclusion. The publisher abstract of the [2011 Behbahani–Lam article](https://www.sciencedirect.com/science/article/pii/S0012365X10003924) was also inspected. |
| [Keramatipour, arXiv:2604.23037v2](https://arxiv.org/html/2604.23037v2), 2026-04-28 | Abstract, contents, section 5.1.3 Conway case, and chapter 6 conclusions/future work. Reports SAT attempts and limitations, not an unrestricted UNSAT certificate. The future-work discussion treats noncontainment of Paley(9) as conjectural. | No new version shown; do not turn the conjectural rook exclusion into a pruning rule. Complete encoding and proofs not reaudited. |
| [Reimbayev, arXiv:2608.19410v1](https://arxiv.org/abs/2608.19410v1), 2026-08-19 | Abstract and submission/version section still show only v1, describing seven-vertex induced-subgraph classification/frequencies. | No full-paper proof audit or new mathematical verification; no target resolution claimed in inspected abstract. |
| [Petro–Phillips, arXiv:2502.17845v1](https://arxiv.org/html/2502.17845v1), 2025-02-25 | Corollary 4.9 and Example 4: the conditional 3-clique graph spectrum for the target is `18^1,7^54,0^44,(-3)^132`. The [journal version](https://www.sciencedirect.com/science/article/pii/S0012365X25004704) is Discrete Mathematics 349(3), 114862 (2026), DOI 10.1016/j.disc.2025.114862. | Exact formulas/source scope inspected; full proof not rederived. These are necessary conditional data, not a contradiction or construction. |

Source-byte hashes are **null**: this lane inspected text through the web
tool and did not archive complete source-response bytes. The immutable arXiv
versions and publisher identifiers are retrieval references, not fabricated
content hashes. The source availability observed above does not guarantee
future access. Search indexes and dynamic pages may change.

## Search coverage and failures

The actual queries below were issued via `web.run` on the audit date. Primary
pages were then opened and searched by section names, theorem numbers, `99`,
`Conway`, `score`, and `4-vertex`. Search results from this repository, its
external archive, Wikipedia, ProofAtlas and Prove2Me were discovery leads only;
they were not treated as independent evidence for resolution.

```text
"Conway" "99" graph 2026 existence strongly regular
"srg(99,14,1,2)"
"99-graph" automorphism group Makhnev
site:arxiv.org "Conway" "99" "2026" "September"
"Conway 99" "resolved" OR "nonexistence" September 2026
"Conway" "99" "clique" Petro Phillips
"Conway 99" September 2026 proof -site:github.com -site:prove2.me -site:proofatlas.ai -site:wikipedia.org
site:arxiv.org "99,14,1,2" 2026
"Strongly regular graphs with non-trivial automorphisms" Behbahani Lam pdf 99
"Crnković" "Maksimović" "99" automorphism group 2016 pdf
"On Clique Graphs and Clique Regular Graphs" "99" spectrum
site:cdm.ucalgary.ca/62323 "Theorem 7.3"
site:spectrum.library.concordia.ca "Theorem 4.14" "only possible"
```

Unrelated clothing, cycling, sports and business results were discarded.
Two mistyped/unconfirmed discovery URLs failed (`2502.012 clique graph` and
`2502.17845v3`); the correct version was located in the pinned repository
bibliography and checked as v1. An incidental PowerShell inspection with
`-First ninety` failed parsing and was not a successful audit command.
These failed accesses provide no mathematical evidence.

No resolution was identified in this limited search and source inspection.
Coverage excludes unindexed work, comprehensive non-English sources,
inaccessible full text, all equivalent terminology, and exhaustive citation
chaining. This does not establish absence of a resolution worldwide or novelty
of any repository theorem.

## Frozen registry and CI audit

The root entry point already exists, names the pinned historical ledger at
`85e705cc6c2a14d123120c93a847e30aaab1789e`, and does not silently import its
VERIFIED labels. The current literature claim
`C-LITERATURE-20260917-ABSTRACTS` revision 1 is correctly CANDIDATE and
limited to its three historical abstracts. A later source revision does not
invalidate that dated historical statement.

The independent, read-only [pointer checker](audit_frozen_registry.py) examined
all **228 PUBLIC artifact records** of the frozen ledger. Every pointer resolved
to a local immutable Git blob with the declared SHA-256 and path. Three pointer
controls passed. [Receipt](registry_pointer_audit.json), SHA-256
`ddd83e2e4b4cf1f291efc3fd4a0052e517186988bf578857b76edb202c6eb062`.
This establishes pointer-to-Git-byte consistency, not live remote accessibility,
public clone completeness, or mathematical validity. The frozen ledger contains
41 VERIFIED/CLEAR and 1 CANDIDATE/CLEAR claim records; these are recorded labels,
not 41 new theorem verifications.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/results/20260930_literature_audit/audit_frozen_registry.py --commit 90f1a32de21faea3519c3635677d5739f86ad734 --out acceleration/results/20260930_literature_audit/registry_pointer_audit.json
```

Replay must choose a new output filename; existing evidence is never overwritten.
The receipt records interpreter/dependency versions, exact command, working
directory, checker hash and all frozen audit-input hashes.

Read-only inspection of the schema, semantic checker, controls and CI found
explicit duplicate-key/ID, reference, cycle, revision, impact and promotion
gates. CI uses locked uv, runs adversarial controls, checks PUBLIC bytes,
compares the prior ledger, and uploads a report even after failure. Expensive
mathematical checks and reviewer independence are explicitly outside that gate.
Those tests were not redundantly rerun in this lane. No material active-claim
consistency defect was established by this bounded audit. The unread remainder
of mathematical proof/evidence content is not certified by this conclusion.

No shared ledger, documentation, submodule or preexisting user file was edited.
Execution state outside these completed read-only checks is **UNKNOWN** from
this report. A concrete useful follow-up is independent checking of the new
unrestricted switch-search method on controlled graph fixtures; it must not
reuse the literature's partial score as proof or assume order-7 symmetry.
