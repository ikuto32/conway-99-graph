"""Bind a written scope review; does not reapprove the author's enumeration."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys


def digest(p):
    return sha256(Path(p).read_bytes()).hexdigest()


def main():
    root=Path('acceleration/results/20260917_independent_review')
    universe=root/'coordinate_universe.json'
    exclusion=root/'moment_positive600.json'
    binding=root/'moment_positive600_claim_binding.json'
    manifest=Path('acceleration/results/20260917_partial_matching/manifest.json')
    raw=Path('acceleration/results/20260917_partial_coordinate_matchings/matchings.json')
    note=Path('docs/AUDIT_20260917_COORDINATE_FAMILY_COVERAGE.md')
    expected={universe:'d7284d73e75f3fe49160c1a2f8ba97eb0263424e727661db25ac1cf631ba8c57',
              exclusion:'d435c7789bd2f181e3a870b2019ae309cdbf2d9530bc21b2d987d40671444bc8',
              manifest:'dcc0118cc35993743e94bf7b548e6870526e33f3d4fe4015a48cdacb0c1fc05c',
              raw:'d0a306070044f2885df38d2abab264965e4f067873d8dfc13c8b8d0c41104734'}
    assert all(digest(p)==h for p,h in expected.items())
    u,e,b,m,r=[json.loads(p.read_bytes()) for p in (universe,exclusion,binding,manifest,raw)]
    assert u['status']=='INDEPENDENT_PARTIAL_COORDINATE_MATCHING_UNIVERSE_PASS'
    assert e['status']=='INDEPENDENT_PARTIAL_K_POSITIVE_MOMENT_EXCLUSION_PASS'
    assert b['status']=='INDEPENDENT_PARTIAL_K_POSITIVE_MOMENT_CLAIM_BINDING_PASS'
    assert u['inputs_sha256'][manifest.as_posix()]==e['scope_manifest_sha256']==digest(manifest)
    assert b['inputs_sha256'][exclusion.as_posix()]==digest(exclusion)
    legal={frozenset(x) for x in m['freed_legal_matching_edges_outer']}
    fixed={frozenset(x) for x in m['remaining_fixed_K_edges_outer']}
    affected=set(m['affected_outer_vertices'])
    assert len(legal)==60 and len(affected)==12 and not legal & fixed
    assert not any(edge <= affected for edge in fixed)
    # Only the new scope-inclusion test; list completeness belongs to root audit.
    assert all(all(frozenset(edge) in legal for edge in record['edges_outer']) for record in r['records'])
    result=dict(status='WRITTEN_COORDINATE_FAMILY_COVERAGE_PASS',
        timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        command=[sys.executable,*sys.argv],cwd=str(Path.cwd()),
        reviewer='Codex subagent /root/structural_continuation',
        review_kind='Scope inclusion and independent mathematical derivation from lambda=1; reused separate artifact audits',
        inputs_sha256={p.as_posix():digest(p) for p in (*expected,binding,note,Path(__file__),Path('uv.lock'))},
        exact_statement='Every listed matching M defines a subfamily F_M of the excluded fixed162 family F; every target completion in F would induce a legal perfect matching on the twelve freed-coordinate vertices.',
        count_authority='Separate root-agent inclusion-exclusion/list/dense99-matrix audit, not this reviewer',
        exclusion_authority='Independent verifier exact moment600 exclusion and corrected necessary-encoding dependency metadata',
        self_approval_disclosure='Reviewer produced the original matching list. This report does not independently reapprove that enumeration; it uses root independent audit as a premise.',
        scope_manifest_sha256=digest(manifest),listed_assignments=u['matching_count'],
        every_listed_assignment_scope_inclusion_checked=True,
        full_family_state_set_equals_matching_union=False,
        target_solution_set_equals_matching_subfamily_union=True,
        historical_exclusion_union_computed=False,unrestricted_target_coverage=False,
        target_resolution='UNKNOWN',ledger_edited=False,external_review=False,
        limitations=['Conditional fixed162 and prescribed-absence scope only',
                     'No target-wide matching-count denominator',
                     'No new certificate replay or independent enumeration approval in this written review'])
    out=root/'coordinate_coverage.json'
    with out.open('x',encoding='utf-8') as f:
        json.dump(result,f,indent=2); f.write('\n')
    print(json.dumps(dict(status=result['status'],path=out.as_posix(),sha256=digest(out))))


if __name__=='__main__': main()
