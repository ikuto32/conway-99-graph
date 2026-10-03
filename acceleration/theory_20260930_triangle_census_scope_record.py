"""Preserve the bounded archive scope inspection and census correction record."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / 'external_conway99_research'
PIN = '85e705cc6c2a14d123120c93a847e30aaab1789e'


def digest(b):
    return hashlib.sha256(b).hexdigest()


references = {
    'attempts/2026-07-22-eleven-branch-cover.md': 'Complete single-M1 census: eleven orbits covering10395 matchings; not (M1,M2,P).',
    'verification/2026-07-22-first-wave-audit.md': 'Historical audit of single matching orbits only; no fresh promotion here.',
    'verification/2026-07-22-wave2-audit.md': 'Historical scope guards for eleven single-fibre branches.',
    'verification/wave34-rootless-global/audit.md': 'Fixed one-factorization and holonomy scan, not arbitrary matching triples.',
    'agents/2026-07-24-wave34-rootless-global.md': '1331 ordered triples from eleven factors in one fixed factorization only.',
    'agents/2026-07-28-wave133-triangle-holonomy-topology.md': 'Two holonomy controls with fixed within-fibre factors, no complete census.',
    'attempts/wave40-exact-coupling-model/README.md': 'Complete minimum projected-rank argument after single-M1 normalization; full-block scout samples512 pairs per type.',
    'attempts/wave42-rank26-equality/proof.md': 'Complete implicit permutation/matching coverage for rank26 equality obstruction, not complete core orbit census.',
    'verification/wave41-allquotient-lifts/audit.md': 'Complete4050 quotient forms and selected lift scope under all222 and rankF3=12 assumptions.',
    'attempts/wave153-alternative-compatibility/README.md': '275 safe orbits on1140 triples of18 component types at conditional prism-free kappa3 endpoint.',
    'attempts/wave149-terwilliger-triple/derivation.md': 'General root triangle block derivation followed by fixed M0=M1=M2 and P=shift6 witness.',
    'attempts/wave154-triangle-factor-portfolio/README.md': 'Two Q1 incidence-factor orbits under fixed matching/shift centralizer; not general core orbits.'
}
out = ROOT / 'acceleration/results/20260930_triangle_matching_pair_census_v2/scope_and_correction.json'
assert not out.exists()
source_rows = []
for path, scope in references.items():
    blob = subprocess.check_output(['git', '-C', str(ARCHIVE), 'show', PIN + ':' + path])
    assert blob == (ARCHIVE / path).read_bytes(), path
    source_rows.append({'repository': 'https://github.com/YesterdaysLemon/conway-99-research', 'commit': PIN, 'path': path, 'sha256': digest(blob), 'inspected_scope': scope})
first = ROOT / 'acceleration/results/20260930_triangle_matching_pair_census'
second = out.parent
comparisons = []
for p in sorted(first.glob('stage_*.json')) + [first / 'controls.json', first / 'matchings.json']:
    q = second / p.name
    comparisons.append({'filename': p.name, 'failed_attempt_sha256': digest(p.read_bytes()), 'successful_attempt_sha256': digest(q.read_bytes()), 'byte_equal': p.read_bytes() == q.read_bytes()})
assert all(x['byte_equal'] for x in comparisons)
data = {'timestamp': datetime.now(timezone.utc).isoformat(), 'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(), 'command': [sys.executable, *sys.argv], 'working_directory': str(ROOT), 'producer_source_sha256': digest(Path(__file__).read_bytes()), 'basis': ['CITED', 'COMPUTED'], 'status': 'CANDIDATE', 'scope_finding': 'No complete arbitrary(M1,M2,P) core census was found in this explicitly inspected reference set. This is not an archive-wide or literature-wide absence theorem.', 'references': source_rows, 'correction': {'original_failure': 'ValueError while formatting relative output hashes after all mathematics/stages completed.', 'source_change': 'Only p.relative_to(ROOT) changed to p.resolve().relative_to(ROOT) in the output hash comprehension; original source and failure artifacts preserved.', 'retry_is_additional_attempt_not_additional_census': True, 'byte_comparisons': comparisons}, 'candidate_continuation': 'Use the complete ordered-pair representatives plus their actual joint stabilizers; search arbitrary P with proved exact principal-cap and Gram pruning, then necessary Q1 incidence domains. Complete P coverage remains a separate task and is not claimed.', 'negative_scaling_result': '1701 of3580 ordered-pair classes have trivial joint stabilizer, leaving479001600 labelled P choices each; direct complete P enumeration is not a cheap followup.', 'target_resolution': False, 'overall_search_coverage': 'UNKNOWN; no validated denominator.'}
out.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'path': out.relative_to(ROOT).as_posix(), 'sha256': digest(out.read_bytes()), 'unchanged_stage_files': len(comparisons)}))
