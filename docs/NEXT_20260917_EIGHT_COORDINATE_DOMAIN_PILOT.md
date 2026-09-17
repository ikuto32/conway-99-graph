# Eight-coordinate complete local-domain pilot

Preregistered 2026-09-17 before execution. This conditional family frees both same-sign matching coordinates of root groups 0, 1, 2, 3 in baseline candidate 18481. All remaining baseline K edges, all same-fibre absences, and all unlisted other-coordinate absences remain fixed. No automorphism is assumed. Derive and check the expected 120 fixed K edges, 480 freed-coordinate legal edges, and 2160 unknown edges (including 1680 disjoint-support edges) from the raw baseline.

Question: can the complete locally admissible center-star domains for all 84 outer vertices be enumerated within the fixed pilot limits? A domain contains exactly the missing outer neighbors needed for degree 14, satisfies all full-99 upper common-neighbor caps, and all 14 exact root-neighbor quotas. This is a necessary local condition, not global graph feasibility.

Use deterministic center order 0, 4, 24, 8, 44, 60, followed by all remaining outer labels in ascending order. One invocation has a 300-second enumeration limit, 50,000,000 recursive-node limit, 250,000 accepted choices per center, and 5,000,000 accepted choices in total. Embedding checks and calibration precede that enumeration budget and are recorded separately. No automatic retry or LP/model construction is authorized by this protocol.

Before enumeration, convert all 879,449 six-coordinate stars by adding exactly the previously fixed center neighbors removed in the new family. Check injectivity, unchanged full center neighborhoods, degree and allowed edges. Once a new center domain completes, locate every converted old star by its exact mask and record its new ID. Reuse of the frozen retained-partial enumerator and original partial-graph helpers is disclosed; it is not independent verification.

Calibration checks the first six centers in the frozen order using small restricted candidate universes against direct full-graph brute force, rejects corrupted missing-edge stars, and checks that a zero-domain cap preserves its triggering leaf without labeling the domain complete. Record all failures. Save each completed center, immutable checkpoints, and any partially explored center and cap reason. Partial accepted masks are evidence, not an exact recursive-stack restart checkpoint. A future continuation must specify a fresh protocol and avoid treating incomplete domains as complete.

Success for this engineering pilot means all 84 domains complete and every prior star is located. Any cap, missing embedding, disagreement, or exception prevents that completion claim. Counts and completeness remain CANDIDATE until a separate enumeration/checking path verifies them. No exclusion, target graph, target-wide coverage fraction, or normalization count follows from completing the domains.

Locked execution from repository root:

```powershell
$env:UV_PROJECT_ENVIRONMENT = 'build/research-venv'
uv run --locked --cache-dir .uv-cache-20260917 python acceleration/theory_20260917_partial_eight_matchings.py --out acceleration/results/20260917_partial_eight_matchings
```

The saved manifest binds source commit, exact arguments and working directory, Python version, uv.lock, producer/helper/protocol hashes, independently checked prior-domain receipt, all old domain inputs, and the raw baseline. Positive and corrupted controls do not establish completeness of the large domains.
