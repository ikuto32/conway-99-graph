# Focused primary-source refresh, 2026-10-02 JST

This is a dated, non-exhaustive literature observation. It is separate from
repository resolution status and from mathematical verification. No absence
of search hits is used as a proof that no resolution exists worldwide.
The searches and opened sources below did not supply a complete target graph
or general nonexistence certificate. No contacted-author or external review
is claimed.

## Sources inspected

1. [Andries Brouwer's maintained 51--100 vertex SRG table](https://aeb.win.tue.nl/graphs/srg/srgtab51-100.html),
   accessed 2026-10-02 JST. The exact row `99,14,1,2` visibly retains marker
   `?` and eigenvalue multiplicities `3^54,-4^44`. This verifies only what the
   accessed table states, not an exhaustive literature theorem.
2. Aalok Thakkar,
   [A Forced-Structure Reduction and Verifiable Bounds for Conway's 99-Graph, arXiv:2608.11211v1](https://arxiv.org/html/2608.11211v1),
   accessed 2026-10-02 JST. Sections 1, 4, and 7 explicitly disclaim an
   existence/nonexistence resolution. Section 4 uses the unrestricted rooted
   84-vertex remainder; section 5 imposes specified automorphisms. The reported
   heuristic artifact satisfies 3,437 of its 4,950 degree/pair constraints,
   and is not an SRG. The stated circulant ceiling is restricted. Its artifacts
   and exhaustive computation were not independently replayed here. Its HTML
   header displays 13 July 2026 although the arXiv identifier begins `2608`;
   search indexing also displays an August date. This refresh records that
   discrepancy rather than inventing a corrected publication date.
3. Reimbay Reimbayev,
   [Induced Subgraphs of Order Seven and Their Frequencies in srg(n,k,1,2), arXiv:2608.19410v1](https://arxiv.org/abs/2608.19410),
   abstract/version page accessed 2026-10-02 JST. The recorded paper concerns
   seven-vertex induced counts. Its selected `z82` identity is already audited
   locally in `docs/AUDIT_20261001_REIMBAYEV_Z82.md`; this refresh does not
   reapprove its other formulas or claim a new exclusion.
4. [Hebei Normal University official seminar announcement](https://www.hebtu.edu.cn/a/2026/06/24/AD3624B468444197AA2464C61CBDEE63.html),
   posted 2026-06-24 for Sergey Shpectorov's 2026-06-25 talk, accessed
   2026-10-02 JST. The abstract describes complete neighborhood enumeration
   for `srg(85,14,3,2)` and discusses a possible analogous Conway-99 approach
   with Tianxiao Zhao. It supplies no Conway-99 proof artifact. This motivates
   triangle-core methods, which are already represented in the repository.
5. [Reimbayev's six-vertex paper, arXiv:2508.03377v2](https://arxiv.org/abs/2508.03377),
   version page accessed 2026-10-02 JST, showing revision 2025-11-03. This
   confirms the source version, not a fresh mathematical audit of all formulas.

## Query coverage

The executed discovery queries were:

```text
Conway 99 graph srg 99 14 1 2 recent 2025 2026
Conway 99 graph Reimbayev strongly regular graph lambda 1 mu 2
Conway 99 graph primary paper triangle incidence binary code
"srg(99,14,1,2)" "2026" -site:wikipedia.org -site:github.com
"Conway" "99-graph" "2026" construction nonexistence -site:github.com -site:wikipedia.org
"2608.19410" graph Reimbayev
```

Secondary aggregators and agent project summaries surfaced during discovery
but were not treated as primary mathematical evidence. The maintained table
and selected primary texts support a limited current-status observation. This
coverage does not search every language, preprint server, private manuscript,
conference proceeding, or author repository.

The highest-information executed structural experiment in this wave is
instead the exact order-eight marked-extension/null-witness package documented
in `docs/DERIVATION_20261002_ORDER8_MARKED_ENDPOINT.md`. It continues an unused
archived coefficient layer and avoids repeating the paper's restricted
automorphism searches.
