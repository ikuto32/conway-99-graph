"""Register a written scope-inclusion derivation, separately from enumeration."""
from datetime import datetime,timezone
import json
from pathlib import Path
import sys
import yaml
import register_20260917_v3_calibration_partial_claims as shared
import validate_claims as registry


def main():
    ap='acceleration/results/20260917_independent_review/coordinate_coverage.json'
    assert shared.digest(ap)=='e2673661a74c7fec6e8f4cd7c30d7f340f69b7083942b707fcf757b99ccbb8c0'
    a=shared.load(ap);assert a['status']=='WRITTEN_COORDINATE_FAMILY_COVERAGE_PASS'
    assert a['every_listed_assignment_scope_inclusion_checked'] and a['target_solution_set_equals_matching_subfamily_union']
    assert not a['full_family_state_set_equals_matching_union'] and not a['unrestricted_target_coverage']
    for p,h in a['inputs_sha256'].items():assert shared.digest(p)==h
    root=shared.ROOT;lp=root/'CLAIMS.yaml';old=lp.read_bytes();ledger=registry.read_ledger(lp)
    resume=root/'acceleration/results/20260917_resume';snapshot=resume/'claims_before_coordinate_coverage.yaml'
    receipt=resume/'coordinate_coverage_registration.json';assert not snapshot.exists() and not receipt.exists()
    evidence={'coordinate-coverage-audit':ap,'coordinate-coverage-derivation':'docs/AUDIT_20260917_COORDINATE_FAMILY_COVERAGE.md'}
    artifacts=[dict(id=i,path=p,sha256=shared.digest(p),availability='LOCAL_ONLY',retrieval='Workspace relative path; exact prerequisite artifacts are pinned by the audit.',unavailable_reason='Not yet assigned a confirmed publication commit.') for i,p in evidence.items()]
    now=datetime.now(timezone.utc).isoformat()
    claim=dict(id='C-PARTIAL-K-MATCHING-SUBFAMILY-COVERAGE',revision=1,
        statement='For the frozen one-coordinate family F, every listed legal matching M defines a subfamily F_M obtained by fixing the freed coordinate exactly to M. Each F_M is excluded by the verified exclusion of F. Any target completion in F would choose exactly one of the 6040 listed matchings, so the target-solution set in F equals the union of the target-solution sets in those F_M; this does not assert equality of the arbitrary partial-state sets.',
        kind='mathematical result',basis=['DERIVED'],status='VERIFIED',review_state='CLEAR',
        scope=dict(description='Only the fixed162-edge family and its6040 labeled coordinate assignments, with the same prescribed absences. No union with historical exclusions.',unrestricted_target=False,target_resolution='NONE'),
        assumptions=['Identical frozen scope manifest dcc0118cc35993743e94bf7b548e6870526e33f3d4fe4015a48cdacb0c1fc05c for both prerequisite claims.',
            'For the necessity implication, assume a target completion; lambda=1 forces a perfect matching inside each14-neighborhood.'],
        dependencies=[dict(id='C-PARTIAL-K-ONE-COORDINATE-EXCLUSION',revision=1,relation='uses_result'),
            dict(id='C-PARTIAL-K-COORDINATE-MATCHING-UNIVERSE',revision=1,relation='coverage')],
        evidence=list(evidence),verification=[dict(claim_revision=1,verifier=a['reviewer'],method='independent_derivation',
            command_or_audit=ap,timestamp=a['timestamp'],outcome='PASS',scope=a['exact_statement'],
            artifact_hashes={x['id']:x['sha256'] for x in artifacts},
            shared_components=[a['self_approval_disclosure'],a['count_authority'],a['exclusion_authority']],
            controls=['Written set inclusion and lambda=1 neighborhood derivation; no new numerical experiment.'],limitations=a['limitations'])],
        limitations=a['limitations'],created_at=now,updated_at=now,external_source=None,
        unknowns={'external_source':'Current-project written scope review; no external peer review.',
            'reproducibility':'No new computation: written proof and pinned prerequisite audits are the evidence.'})
    merged=shared.merge(ledger,artifacts,[claim],now)
    v=registry.validate(merged,root,shared.load('docs/claims.schema.json'),'available',ledger);assert v['valid'],v['errors']
    assert lp.read_bytes()==old;snapshot.write_bytes(old);lp.write_text(yaml.safe_dump(merged,sort_keys=False,width=110),encoding='utf-8')
    shared.save(receipt,dict(timestamp=now,command=[sys.executable,*sys.argv],cwd=str(Path.cwd()),
        registrar_sha256=shared.digest(__file__),previous_ledger_sha256=shared.sha256(old).hexdigest(),ledger_sha256=shared.digest(lp),
        validation=v,status='WRITTEN_COORDINATE_COVERAGE_REGISTERED',claim_id=claim['id'],registrar_performs_mathematical_verification=False))
    print(json.dumps(dict(claim=claim['id'],ledger_sha256=shared.digest(lp))))


if __name__=='__main__':main()
