"""Register finite GPU/CPU numerical parity, not a mathematical certificate."""
from datetime import datetime, timezone
from pathlib import Path
import json
import sys
import yaml
import register_20260917_v3_calibration_partial_claims as shared
import validate_claims as registry


def main():
    audit='acceleration/results/20260917_independent_review/moment_pdhg_gpu_cpu_parity_v2/summary.json'
    assert shared.digest(audit)=='c0ae24550c1f33c1d808107f7aaa9bf49d83d968805f2691a26388b777e2aaf2'
    r=shared.load(audit)
    for p,h in r['inputs_sha256'].items():assert shared.digest(p)==h,p
    assert len(r['records'])==4 and r['all_serialized_coefficients_mapped_to_prior_audited_model']
    lp=shared.ROOT/'CLAIMS.yaml';old=lp.read_bytes();ledger=registry.read_ledger(lp);now=datetime.now(timezone.utc).isoformat()
    resume=shared.ROOT/'acceleration/results/20260917_resume';snapshot=resume/'claims_before_moment_gpu_parity.yaml';receipt=resume/'moment_gpu_parity_registration.json';assert not snapshot.exists() and not receipt.exists()
    evidence={'moment-gpu-parity-audit':audit,'moment-gpu-pilot-manifest':'acceleration/results/20260917_moment_pdhg_gpu/pilot/manifest.json','moment-gpu-pilot-summary':'acceleration/results/20260917_moment_pdhg_gpu/pilot/summary.json'}
    artifacts=[dict(id=i,path=p,sha256=shared.digest(p),availability='LOCAL_ONLY',retrieval='Workspace relative path; full checkpoint vectors and independent CPU comparison outputs retained.',unavailable_reason='No confirmed public commit assigned yet.')for i,p in evidence.items()]
    scope='Exactly four saved inputs at iterations 1, 2, 10 and 100, including the audited two-coordinate operator and a 45,882-variable simplex fixture; float64 and the frozen GPU/CPU numerical settings.'
    claim=dict(id='C-MOMENT-PDHG-GPU-CPU-PARITY',revision=1,
        statement='For each of the four frozen pilot inputs, all five saved GPU state vectors at iterations 1,2,10,100 agree with the independently implemented sort-projection CPU reference within the preregistered absolute vector tolerance 1e-8, and checked scalar diagnostics agree within 1e-7. The two-coordinate exporter coefficients and transpose match the audited operator; the four saved malformed inputs are rejected.',
        kind='empirical/engineering result',basis=['COMPUTED'],status='VERIFIED',review_state='CLEAR',scope=dict(description=scope,unrestricted_target=False,target_resolution='NONE'),
        assumptions=['Frozen four inputs, source/build, float64 settings and declared tolerances only.','Soft moment duals are clipped while hard reciprocity duals are unbounded; nonzero hard residual prevents interpreting soft L1 as a feasible primal upper bound.'],
        dependencies=[dict(id='C-PARTIAL-K-TWO-COORDINATE-FULL-MOMENT-ENCODING',revision=1,relation='verification_dependency')],evidence=list(evidence),
        verification=[dict(claim_revision=1,verifier='independent_verifier agent',method='independent_artifact_check',command_or_audit=audit,timestamp=r['timestamp'],outcome='PASS',scope=scope,artifact_hashes={a['id']:a['sha256']for a in artifacts},shared_components=r['shared_components'],controls=['Known positive uniform fixture, unbounded hard dual, large simplex, and two-coordinate operator; all vector checkpoints checked.','Four malformed binaries and independently injected vector corruptions; initial integer-decoding corruption-control failure retained before float64 correction.'],limitations=r['limitations'])],
        limitations=r['limitations'],created_at=now,updated_at=now,external_source=None,unknowns={'external_source':'Current-project numerical comparison; not an external review or certified error bound.'},reproducibility=dict(manifest='moment-gpu-pilot-manifest'))
    merged=shared.merge(ledger,artifacts,[claim],now);v=registry.validate(merged,shared.ROOT,shared.load('docs/claims.schema.json'),'available',ledger);assert v['valid'],v['errors']
    assert lp.read_bytes()==old;snapshot.write_bytes(old);lp.write_text(yaml.safe_dump(merged,sort_keys=False,width=110),encoding='utf-8')
    shared.save(receipt,dict(timestamp=now,command=[sys.executable,*sys.argv],cwd=str(Path.cwd()),source_sha256=shared.digest(__file__),previous_ledger_sha256=shared.sha256(old).hexdigest(),ledger_sha256=shared.digest(lp),claim_id=claim['id'],validation=v,registrar_performs_mathematical_verification=False));print(json.dumps(dict(claim_id=claim['id'],ledger_sha256=shared.digest(lp))))


if __name__=='__main__':main()
