# Four-coordinate domain pilot

Status at production: CANDIDATE complete domains, pending fresh independent enumeration. Domain label: `PARTIAL_K_FOUR_SAME_SIGN_COORDINATES_ROOT01_V1`.

Both same-sign coordinates at each of root groups 0 and 1 are free. The producer reconstructs the full root scaffold and baseline K, removes exactly the 24 edges in those four matching coordinates, and retains all 144 other K edges. These include all seven cross matchings and the ten other same-sign matchings. All same-fibre and unlisted other-coordinate absences remain prescribed. Unknown edges consist of 240 support-legal edges in the four freed coordinates plus 1,680 disjoint-support edges, totaling 1,920.

Four centers require ten added outer neighbors, forty centers require nine, and forty require eight. These counts were checked directly against the rebuilt partial graph. The pilot order was 0, 4, 24, 44, followed by other center labels in ascending order.

Preregistered limits were 180 seconds, twenty million search nodes, 100,000 domains per center, and 600,000 total completed domains. All 84 searches completed without a cap: 290,460 domain choices, largest center 23,680, 2,229,902 search nodes including controls, 8.235 measured seconds. Every completed center has a domain file and immutable checkpoint inventory.

All 89,308 choices from the preceding two-coordinate domain embed. For each old choice, precisely the removed formerly fixed neighbors are added to its mask; equality of the old and new full outer neighborhoods is checked. Explicit old-to-new domain-ID mappings are saved. This verifies that containment calculation, not completeness of the larger domain.

Four restricted candidate universes at centers 0, 4, 24, 44 agree with direct exhaustive subset insertion into the full partial graph, and four missing-edge corruptions are rejected. The optimized quota/conflict/resource-cap helper is shared with prior producers, so separate full-set verification is still required.

No LP was run. The positive two-coordinate certificate does not automatically exclude this broader family. Any transferred weights must be evaluated against every new star and the new RHS, and any new model requires independent necessity and coefficient checks. Scope remains conditional on the fixed K edges and prescribed absences; no unrestricted Conway-99 resolution or global coverage percentage is claimed.

The run is complete and no process remains active. Reproduction uses a fresh output directory:

```powershell
$env:UV_PROJECT_ENVIRONMENT = 'build/research-venv'
uv run --locked --cache-dir .uv-cache-20260917 python acceleration/theory_20260917_partial_four_matchings.py --out acceleration/results/FRESH_FOUR_COORDINATE_REPLAY
```
