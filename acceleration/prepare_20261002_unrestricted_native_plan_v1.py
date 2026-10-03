"""Freeze an original unrestricted-instance plan; no solver launch or claim promotion."""
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    artifacts = [
        ('cnf', 'acceleration/results/20260930_unrestricted_full99_cnf/instance.cnf', '7029f5c0965d0121aec6ce24db2b9a3d2e201e85b72c8ef51595c63bb62b2138'),
        ('model', 'acceleration/results/20260930_unrestricted_full99_cnf/model.json', '77089d0a9dd94919bff62aa1e552b758eca061f980524131ad8d1861acce7a8e'),
        ('scope', 'acceleration/results/20260930_unrestricted_full99_preflight_v2/scope.json', '2359c7389b4bb23475cf9607a99c07060119976abff8bc70bbdb5d131ab1921d')]
    inputs = []
    for role, name, expected in artifacts:
        path = ROOT/name
        if digest(path) != expected:
            raise ValueError('Changed frozen unrestricted input '+name)
        inputs.append(dict(role=role, path=name, sha256=expected, bytes=path.stat().st_size))
    gates = []
    for name, expected, status in [
        ('acceleration/results/20260930_independent_review/unrestricted_full99_cnf/summary.json', '2d6702d0f60341378fcf6b5b0808e6c34ea6a1025775cfae60500626f199ef58', 'INDEPENDENT_UNRESTRICTED_FULL99_CNF_ENCODING_PASS'),
        ('acceleration/results/20260930_independent_review/unrestricted_full99_sat_object_calibration/summary.json', '1ae229a3a6a3d7dcf9cbc3c1c9a9a924facb2d5c343bbd683f838e27c8362a4f', 'INDEPENDENT_UNRESTRICTED_FULL99_SAT_OBJECT_CHECKER_CALIBRATION_PASS')]:
        path = ROOT/name
        if digest(path) != expected:
            raise ValueError('Changed historical unrestricted mathematical gate '+name)
        report = json.loads(path.read_bytes())
        required = {x['path']:x['sha256'] for x in inputs}
        if report['status'] != status or any(report['inputs_sha256'].get(k) != v for k,v in required.items()):
            raise ValueError('Mathematical gate input/scope mismatch')
        gates.append(dict(path=name,sha256=expected,expected_status=status,required_input_bindings=required))
    plan = dict(schema='POLICY_NATIVE_SINGLE_PLAN_V2', timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        question='Evaluate one exact unrestricted full99 CNF with a larger explicitly allocated proof-producing native run if proof-state continuation is not preferable.',
        scope='All hypothetical srg(99,14,1,2) graphs up to the proved root relabelling;3486 outer pairs remain independently free. No nontrivial target automorphism is assumed.',
        selection_rule='Unchanged complete unrestricted base input; no fixed support or branch literals. Prepared now for driver controls; scientific launch remains subject to comparison with saved-proof continuation.',
        success_criterion='Preserve exact complete assignment or full UNSAT proof, or a checkpointed partial trace and accurate unfinished outcome.',
        falsification_criterion='SAT is falsified by any original-CNF clause, symmetry/binary/zero-diagonal/degree/common-neighbor or exact matrix identity violation; UNSAT is rejected without complete independent proof replay.',
        independent_verification_criterion='Separate implementation checks complete raw assignment and decoded99 graph, or replays the full exact proof against original CNF with pinned checker provenance and encoding/coverage audits.',
        allocation_reason='Historical unrestricted run used300s and returned UNKNOWN with346616832 partial trace bytes. Initial native1800s within outer2100s allows a larger informative proof-producing experiment, contingent on better checkpoint reuse and observed resources.',
        baseline_and_uncertainty='No calibrated success probability; saved300s traces are incomplete. Previous conflict cap and whole-input restart may waste effort; proof-state continuation is being assessed before research launch.',
        numerical_acceptance='EXACT_INTEGER_CNF_AND_RAW_PROOF_OR_COMPLETE_ASSIGNMENT',
        variables=1186500, clauses=4136454, inputs=inputs, mathematical_gates=gates,
        configuration=dict(native_seconds=1800,producer_seconds=2050,shutdown_reserve_seconds=150,
            address_space_bytes=8*1024**3,proof_file_bytes=4*1024**3,seed=0,conflict_limit=None,
            conflict_limit_null_reason='Use observed wall/resource progress rather than inheriting the historical one-million-conflict cutoff.',
            host_free_reserve_bytes=32*1024**3,ext4_free_reserve_bytes=8*1024**3,
            aggregate_retained_artifact_bytes=12*1024**3),
        execution_status='PREPARED_ONLY_NOT_EXECUTED', automatic_resume=False, target_resolution=False)
    path = args.out/'plan.json'
    with path.open('x', encoding='utf8', newline='\n') as f:
        json.dump(plan,f,indent=2);f.write('\n')
    print(json.dumps(dict(path=path.as_posix(),sha256=digest(path),scientific_solver_calls=0)))


if __name__ == '__main__':
    main()
