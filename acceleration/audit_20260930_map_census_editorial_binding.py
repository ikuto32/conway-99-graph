"""Append-only dependency impact review; no mathematical replay or producer imports."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'acceleration/results/20260930_independent_review'

def digest(path):
    h = sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()

def load(path):
    return json.loads(path.read_text(encoding='utf-8'))

def main():
    original_path = BASE / 'eight_pair_relabelings01/summary.json'
    editorial_path = BASE / 'automorphism_assumption_editorial/summary.json'
    impact_path = BASE / 'editorial_dependent_impact/w81_nogood.json'
    original, editorial, impact = map(load, [original_path, editorial_path, impact_path])
    assert original['status'] == 'INDEPENDENT_EIGHT_FULL99_PAIR_RELABELING_TRANSPORT_PASS'
    assert editorial['status'] == 'INDEPENDENT_AUTOMORPHISM_ASSUMPTION_EDITORIAL_IMPACT_PASS'
    assert impact['status'] == 'INDEPENDENT_EDITORIAL_DEPENDENCY_IMPACT_PASS'
    encoding_id = 'C-PARTIAL-K-EIGHT-COORDINATE-FULL99-SAT-ENCODING'
    nogood_id = 'C-PARTIAL-K-EIGHT-FULL99-W81-GRAM-BOX-NOGOOD'
    encoding = next(r for r in editorial['records'] if r['claim_id'] == encoding_id)
    assert encoding['reviewed_revision'] == 1
    assert impact['claim_id'] == nogood_id and impact['claim_revision'] == 2
    assert impact['previous_revision'] == 1
    checked = {}
    for path, expected in original['inputs_sha256'].items():
        actual = digest(ROOT / path)
        assert actual == expected, (path, actual, expected)
        checked[path] = actual
    for path in [original_path, editorial_path, impact_path, Path(__file__).resolve()]:
        checked[path.relative_to(ROOT).as_posix()] = digest(path)
    dependencies = [dict(d, revision=2) for d in original['dependencies']]
    assert {d['id'] for d in dependencies} == {encoding_id, nogood_id}
    report = {
        'status': 'INDEPENDENT_MAP_CENSUS_EDITORIAL_DEPENDENCY_BINDING_PASS',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'command': [sys.executable, *sys.argv], 'working_directory': str(ROOT),
        'python': platform.python_version(),
        'verifier': '/root/eight_domain_audit original independent census reviewer',
        'verification_type': 'Append-only editorial dependency-impact review and complete original-input hash reauthentication; no mathematical rerun',
        'claim_id': original['claim_id'], 'claim_revision': 1,
        'statement': original['statement'], 'scope': original['scope'],
        'assumptions': original['assumptions'],
        'previous_dependencies': original['dependencies'],
        'approved_dependencies': dependencies,
        'recommendation': 'VERIFIED', 'review_state': 'CLEAR',
        'recommendation_condition': 'Only the approved no-assumed-automorphism editorial clarification and exact dependency revision2 migration are applied; unchanged premise statements, scopes and bound evidence remain VERIFIED/CLEAR. Unrelated edits require another impact review.',
        'independent_impact_reason': [
            'The census reconstructs an explicit finite population of signed pair relabelings and checks every fixed/free raw adjacency entry. This argument neither assumes nor asserts any automorphism of a hypothetical target.',
            'The encoding premise supplies the same raw fixed family and edge-variable map. Its editorial clarification changes no pair, clause, scope or equivalence argument.',
            'The source nogood premise supplies the same44 literals and exact box upper -5868. Its revision2 impact review preserves the statement, raw certificate and graph-scope dependencies.',
            'Every original audit input was rehashed successfully. The18432 proposal census, identity-only outcome and zero additional unique clauses retain their exact earlier verification; no finite enumeration is newly performed.'
        ],
        'inputs_sha256': checked,
        'original_inputs_reauthenticated': len(original['inputs_sha256']),
        'mathematical_rerun': False, 'solver_calls': 0,
        'controls': 'Original positive/corrupted controls remain bound through the unchanged original audit. This metadata impact review adds hash equality checks, not new mathematical controls.',
        'shared_components': ['Original independently authored census checker/report', 'Frozen independent encoding and nogood audits', 'Python standard library JSON and SHA256'],
        'limitations': ['No broader map census, new unique clause, SAT/UNSAT claim, target resolution or external review.', 'This addendum keeps original claim revision1 because it is not yet registered; if already registered with old pins, normal schema revision bookkeeping is required.', 'No original artifact or ledger modified.'],
        'artifact_availability': 'LOCAL_ONLY'
    }
    out = BASE / 'eight_pair_relabelings01/editorial_dependency_binding.json'
    assert not out.exists(), 'append-only output already exists'
    out.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'path': out.relative_to(ROOT).as_posix(), 'sha256': digest(out), 'inputs_reauthenticated': report['original_inputs_reauthenticated']}))

if __name__ == '__main__':
    main()
