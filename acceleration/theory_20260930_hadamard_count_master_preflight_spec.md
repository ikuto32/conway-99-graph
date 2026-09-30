# Preregistration: arbitrary-exception count-profile master preflight

Question: can the twelve complete individual coordinate marginal domains be coupled to all twenty group count-signature tables, without restricting the number of exceptional groups? This preflight computes the exact input domains and prospective encoding size. No native solver is called and no full factor is claimed.

Inputs: the independently checked complete coordinate domains (2,226 ordered choices in total), the literal fixed six-prism Hadamard support, and all 31,110 independently checked local triples. Each local triple consists of three distinct balanced six-coordinate words, with local Gram upper bounds and within-group outside-column caps. The master consequently inherits those within-group caps; it is not a Gram-only model. Cross-group caps and unsummed Gram equations are absent.

For each local triple, retain its labelled 6-by-3 count signature and exact catalogue rank. Deduplicate signatures by equality, lexicographically sorted. For each group and each incident coordinate, project the complete coordinate domain to its ordered three-fibre count. Remove a group signature only when one of its six coordinate counts is absent from that coordinate's complete projection. Save every first mismatch and every retained signature ID. This unary filtering preserves all joint count solutions, irrespective of exception count.

Prospective encoding: one-hot selectors for each of twelve coordinate choices and twenty group signatures, plus one-hot count-triple channels at each of the 120 coordinate/group incidences. A coordinate choice implies its ten channel values; a group signature implies its six channel values. Exactly-one channels enforce equality. Every retained group signature has fibre totals (6,6,6), so these tables imply all group/fibre quotas exactly. Complete coordinate domains imply every summed-Gram marginal. Conversely, any joint count solution with these tables assigns the selectors/channels and admits the standard sequential at-most-one auxiliaries. Do not assume this equivalence is independently approved until separately reviewed.

Use explicit sequential at-most-one with n-1 prefix variables and 3n-4 clauses for n>=2, plus one at-least-one clause. A singleton uses its unit clause and no auxiliary. Save deterministic domain sizes, resulting variable/clause estimates and channel populations before any research build. A later builder must separately freeze source/spec and authenticate this preflight.

Controls precede acceptance: the all-balanced count profile and the existing literal six-exception marginal profile rank4_00_profile_0000 must both pass all tables and exact marginals (neither is a full-Gram positive). Reject wrong bounds, wrong coordinate choice, group quota, absent local signature and inconsistent channels in appropriate small or literal controls. The valid local catalogue is also checked against all raw signatures/quotas, with no producer imports.

Resource limit: 60 seconds, 512 MiB approximate ordinary Python working memory, no native or mathematical solver. All 20 groups and all catalogue entries are selected; no heuristic ranking, orbit reduction, exception lower bound, retry, or sampled rejection. Failure preserves outputs and a failure record. Historical source inspection is limited to the named count/domain/profile sources, not an exhaustive literature claim.

Run with UV_PROJECT_ENVIRONMENT=build/research-venv:

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/theory_20260930_hadamard_count_master_preflight.py --out acceleration/results/20260930_hadamard_count_master_preflight
```
