"""Bind the independent target-extension relabeling lemma and checked32maps."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def digest(path):return sha256(Path(path).read_bytes()).hexdigest()
def key(path):return Path(path).resolve().relative_to(ROOT).as_posix()


def main():
    report_path = ROOT/'acceleration/results/20260930_independent_review/rook_scaffold_relabelings32.json'
    derivation = ROOT/'docs/DERIVATION_20260930_SCAFFOLD_CUT_TRANSPORT.md'
    assert digest(report_path) == '897188e21828d946149dbeee503c1fd61b6946197810a11970b92f2a6bf1b282'
    report = json.loads(report_path.read_bytes())
    assert report['status'] == 'INDEPENDENT_ROOK_SCAFFOLD_RELABELINGS32_PASS' and report['maps_checked'] == 32
    bindings = dict(report['inputs_sha256'])
    for p in (Path(__file__),derivation,report_path,ROOT/'uv.lock'):bindings[key(p)] = digest(p)
    assert all(digest(ROOT/name) == value for name,value in bindings.items())
    record = dict(status='INDEPENDENT_FIXED_SCAFFOLD_CUT_TRANSPORT_LEMMA_PASS',claim_id='C-FIXED-SCAFFOLD-RELABELING-CUT-TRANSPORT',claim_revision=1,
                  timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                  command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),
                  verifier='/root/eight_domain_audit independent checking agent',verification_type='Independent exact change-of-labels proof and raw map artifact revision binding',
                  basis=['DERIVED'],kind='mathematical result',
                  statement='For every fixed/free59vertex adjacency specification S with distinct edge variables, every59vertex permutation p preserving S, and every edge-variable clause necessary for all99vertex target extensions of S, replacing each edge variable by its same-sign image under p gives another clause necessary for all target extensions of S.',
                  scope='Universal conditional transport theorem for exact target-extension clauses and specification-preserving permutations; no target automorphism, existence, or nonexistence assertion.',
                  assumptions=['The target is a symmetric binary99by99zero-diagonal adjacency satisfying A²=12I-A+2J.',
                               'The map is a genuine permutation of the designated59vertices preserving every fixed0/fixed1/free pair and the edge-variable bijection.',
                               'The source clause has an independent valid proof for every target extension of exactly this specification.',
                               'Only edge variables are transported; degree-group preservation is additionally required when claiming invariance of a specific local relaxation.'],
                  dependencies=[],dependency_null_reason='The proof uses only the explicit target identity and elementary simultaneous row/column permutation; no prior project result is needed.',
                  derivation=['Extend p to99vertices by fixing the other40labels. Given any target extension A of S, let B[i,j]=A[p(i),p(j)].',
                              'Simultaneous row/column permutation preserves symmetry, binary entries, zero diagonal and the target identity because it preserves I and J.',
                              'Specification preservation makes B another target extension of the same S. Apply the source necessary clause to B.',
                              'Each source edge literal in B equals its same-sign p-image edge literal in A. Since A was arbitrary, the transported clause is universally necessary for this family.',
                              'No step asserts A=B or requires an automorphism of a hypothetical target.'],
                  inputs_sha256=bindings,written_audit=key(derivation),
                  calibrated_instantiation=dict(report=key(report_path),sha256=digest(report_path),supplied_maps_checked=32,controls=report['controls'],
                                                role='Tests the concrete map implementation; these finite controls are not the proof of the universal conditional theorem'),
                  limitations=['This does not validate an unproved source clause.',
                               'The32map audit does not independently establish census completeness or all scaffold automorphisms.',
                               'Transported-clause deduplication does not count excluded graphs or justify target-wide coverage.',
                               'No auxiliary SAT-variable map, unrestricted solution, or external review is established.'],
                  producer_imported=False,recommendation='VERIFIED',target_resolution=False,external_review=False,artifact_availability='LOCAL_ONLY')
    path = ROOT/'acceleration/results/20260930_independent_review/scaffold_cut_transport_lemma.json'
    with path.open('x',encoding='utf-8') as stream:json.dump(record,stream,indent=2);stream.write('\n')
    print(json.dumps(dict(status=record['status'],sha256=digest(path))))


if __name__ == '__main__':main()
