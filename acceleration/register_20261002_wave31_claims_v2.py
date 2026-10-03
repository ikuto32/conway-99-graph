"""Register four independently checked scoped claims and a disjoint literal union.

Bookkeeping only: no solver/proof/mathematical replay. Old ledger records and
archived IDs are preserved; frozen audit reports provide the checking evidence.
"""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import argparse
import copy
import hashlib
import json
import os
import subprocess
import sys
import yaml

import validate_claims as registry

ROOT = Path(__file__).resolve().parents[1]
OLD_SHA = '9e76cdb8efa4ee9fca25243b461002720b9d387acf00381f0893c01bb5655719'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(name):
    return json.loads((ROOT/name).read_bytes())


def save(path, obj):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(obj, stream, indent=2); stream.write('\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    out = args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    before = (ROOT/'CLAIMS.yaml').read_bytes()
    need(hashlib.sha256(before).hexdigest() == OLD_SHA, 'exact308-claim starting ledger')
    old = registry.read_ledger(ROOT/'CLAIMS.yaml')
    need(len(old['claims']) == 308, 'starting308 claim records')
    data = copy.deepcopy(old); now = datetime.now(timezone.utc).isoformat()
    paths = {
        'proof-audit':'acceleration/results/20261002_independent_review/batch05_proofs01/summary.json',
        'proof-binding':'acceleration/results/20261002_independent_review/batch05_proofs01/claim_binding.json',
        'native-run':'acceleration/results/20261002_batch05_native01/manifest.json',
        'native-supervision':'acceleration/results/20261002_batch05_native_supervision01/manifest.json',
        'count-model':'acceleration/results/20261002_order8_marked_extension_v4/model.json.gz',
        'count-witness':'acceleration/results/20261002_order8_psd_cuts/integer_null_witness.json',
        'null-audit':'acceleration/results/20261002_independent_review/order8_null01/summary.json',
        'null-supervision':'acceleration/results/20261002_order8_null_supervision01/manifest.json',
        'coefficient-audit':'acceleration/results/20261002_wave147_all_coefficients/summary.json',
        'coefficient-manifest':'acceleration/results/20261002_wave147_all_coefficients/manifest.json',
        'coefficient-input':'external_conway99_research/attempts/wave147-alternative-lane/coefficients.json.gz',
        'driver-audit':'acceleration/results/20261002_independent_review/policy_driver_calibration02/summary.json',
        'driver-controls':'acceleration/results/20261002_native_budget_controls02/manifest.json',
        'containment-audit':'acceleration/results/20261002_independent_review/linux_descendants_audit01/summary.json',
    }
    hashes = {}
    for alias,name in paths.items():
        aid = 'wave31-'+alias
        need(aid not in {a['id'] for a in data['artifacts']}, 'new unique artifact ID')
        hashes[aid] = sha(ROOT/name)
        data['artifacts'].append(dict(id=aid,path=name,sha256=hashes[aid],availability='LOCAL_ONLY',
            retrieval='Exact repository/workspace path; raw checking closure is identified in the report.',
            unavailable_reason='Immutable publication of the new evidence package has not yet been confirmed.'))
    proof, binding = read(paths['proof-audit']), read(paths['proof-binding'])
    null = read(paths['null-audit']); coefficients = read(paths['coefficient-audit'])
    coefficient_manifest = read(paths['coefficient-manifest']); driver = read(paths['driver-audit'])
    need(hashes['wave31-proof-audit'] == '1b94e67d00af2d1971074e121e245d392e9e3a49d540380fb476d634ed779d61', 'frozen independent proof audit')
    need(hashes['wave31-proof-binding'] == '0e6b7f6f69e241f24dbfbc239f97bba3ad0502c9a77462625579a8e74f6ec242', 'frozen independent proof binding')
    need(proof['status'] == 'INDEPENDENT_EXACT_EIGHT_POLICY_LITERAL_PROOFS_PASS' and proof['completed_proof_replays'] == 64 and proof['proof_bytes'] == 164530579, 'all64 complete exact proof replays')
    need(binding['id'] == 'C-FIXED-HADAMARD-EXACT-EIGHT-PREFIX64-BATCH05-LITERAL-PROFILE-EXCLUSIONS' and binding['revision'] == 1 and binding['verifier'] == '/root/checkpoint_audit', 'separate checker exact claim/revision')
    need(null['status'] == 'INDEPENDENT_ORDER8_SELECTED_RELAXATION_INTEGER_NULL_PASS' and null['verifier'] == '/root' and null['complete_reconstructed_equations'] == null['exact_zero_residuals'] == 4543 and null['exact_N3_count'] == 4158, 'separate exact null witness checking')
    need(sorted((v['dimension'],v['exact_rank'],v['PSD']) for v in null['moments'].values()) == [(66,1,True),(87,1,True)], 'both exact rank-one PSDs')
    need(coefficients['status'] == 'PASS_COMPLETE_STORED_COEFFICIENTS' and coefficients['all_records'] == 2414 and coefficients['all_nonzero_upper_entries'] == 272054, 'complete stored coefficient reconstruction')
    need(driver['status'] == 'INDEPENDENT_EXACT_EIGHT_POLICY_NATIVE_DRIVER_PASS' and driver['verifier'] == '/root/checkpoint_audit', 'new execution calibration independently passed')
    new_ids = []
    def add(cid,statement,kind,evidence,report,verifier,scope,assumptions,limitations,dependencies=None,controls=None):
        need(cid not in {c['id'] for c in data['claims']}, 'unique new claim ID')
        evidence = ['wave31-'+x for x in evidence]
        checked_at = report.get('timestamp')
        need(checked_at, 'actual checking timestamp')
        verification = dict(claim_revision=1,verifier=verifier,method='independent_artifact_check',
            command_or_audit=paths[next(x[7:] for x in evidence if x.endswith('audit'))],timestamp=checked_at,
            outcome='PASS',scope=scope,artifact_hashes={x:hashes[x] for x in evidence},
            shared_components=report.get('shared_components',['Pinned raw data, Python exact integers/standard library; details in audit sources and manifests.']),
            controls=controls or ['Exact positive and corrupted controls in bound audit records; registry registration does not replay mathematics.'],limitations=limitations)
        data['claims'].append(dict(id=cid,revision=1,statement=statement,kind=kind,basis=['DERIVED','COMPUTED'],
            status='VERIFIED',review_state='CLEAR',scope=dict(description=scope,unrestricted_target=False,target_resolution='NONE'),
            assumptions=assumptions,dependencies=dependencies or [],evidence=evidence,verification=[verification],
            limitations=limitations,created_at=now,updated_at=now,external_source=None,
            unknowns=dict(external_source='New scoped internal checking; archive raw-data provenance is in immutable manifests, no historical status imported.'),
            reproducibility=dict(manifest=evidence[0])))
        new_ids.append(cid)
    add(binding['id'],binding['statement'],'exclusion',['proof-audit','proof-binding','native-run','native-supervision'],proof,binding['verifier'],binding['scope']['description'],binding['assumptions'],binding.get('limitations',['Only64 specified literal cases on a fixed support; no target-wide coverage.']),binding['dependencies'])
    add('C-WAVE147-ALL-STORED-PAIR-ROOT-COEFFICIENT-RECONSTRUCTION',
        'Each of the2414 stored Wave147 ordered-edge/ordered-nonedge class coefficient matrices, comprising272054 nonzero upper entries, equals complete direct counting of ordered roots and ordered pairs of unordered free triples whose union exhausts the non-root vertices of that listed class.',
        'encoding',['coefficient-audit','coefficient-manifest','coefficient-input'],{**coefficients,'timestamp':coefficient_manifest['timestamp']},'/root/structural',
        'All2414 explicit stored records under the frozen66/87 flag bases; no class-catalogue completeness or unrestricted resolution statement.',
        ['Exact immutable archived graph masks and root/flag conventions, pinned archive commit85e705cc6c2a14d123120c93a847e30aaab1789e.'],coefficients['limitations'])
    add('C-ORDER8-MARKED-EXTENSION-SELECTED-RELAXATION-INTEGER-ENDPOINT-WITNESS',
        'The frozen explicit vector of1223 nonnegative integers satisfies all4543 independently reconstructed integer equations of the specified order-eight marked-extension system; its explicit N3 class count is4158, and its66x66 and87x87 frozen pair-root coefficient contractions are positive semidefinite of exact rank1.',
        'construction',['null-audit','null-supervision','count-model','count-witness','coefficient-input'],null,'/root',
        'One exact aggregate-count witness for the literal frozen equation system and two specified moment blocks; it shows this relaxation admits the endpoint, without constructing a graph.',
        ['Exact declared variable-to-mask indexing and explicit integer rows; root marks quotient only the automorphisms of small induced classes.'],null['limitations'],
        [dict(id='C-WAVE147-ALL-STORED-PAIR-ROOT-COEFFICIENT-RECONSTRUCTION',revision=1,relation='verification_dependency')])
    add('C-POLICY-AWARE-EXACT-EIGHT-NATIVE-DRIVER-CONTROLS',
        'The exact pinned v1 policy-aware native driver and receipt/checker path passed the recorded tiny SAT truth/assignment check, complete tiny UNSAT proof check, malformed proof/receipt controls, foreground timeout and enclosing local Linux spawned-descendant success/timeout cleanup observations.',
        'empirical/engineering result',['driver-audit','driver-controls','containment-audit'],driver,'/root/checkpoint_audit',
        'Only the explicit tiny fixture executions with frozen source/tool/environment bytes and recorded resource configuration; no absolute containment or solver-correctness theorem.',
        ['Supported local nonescaping Linux process group and the exact pinned CaDiCaL/DRAT checker binaries.'],driver['limitations'])
    # Exact disjoint union of authenticated saved literal reports, not a graph fraction.
    stop = read('acceleration/results/20261001_user_stop/checkpoint.json')
    prior = set(); proof_bytes = 0
    for entry in stop['completed_literal_batches']:
        need(sha(ROOT/entry['path']) == entry['sha256'], 'unchanged historical batch identity')
        report = read(entry['path'])
        ids = [r['case_id'] for r in report['case_records']]
        need(len(ids) == len(set(ids)) == entry['cases'] and prior.isdisjoint(ids), 'disjoint historical literal batches')
        prior.update(ids); proof_bytes += entry['proof_bytes']
    selected = [r['case_id'] for r in proof['case_records']]
    need(len(prior) == 316 and len(selected) == len(set(selected)) == 64 and prior.isdisjoint(selected), 'checked316plus64 distinct literal union')
    universe = {r['case_id'] for r in read('acceleration/results/20260930_exact_eight_campaign_preparation/campaign_manifest.json')['records']}
    need(len(universe) == 792 and (prior|set(selected)) <= universe, 'exact frozen792 population membership')
    need(len(data['claims']) == 312 and data['claims'][:-4] == old['claims'], 'preserve every old claim')
    data['updated_at'] = now
    validation = registry.validate(data,ROOT,read('docs/claims.schema.json'),'none',old)
    need(validation['valid'],repr(validation['errors']))
    after = yaml.safe_dump(data,sort_keys=False,width=110).encode()
    (out/'CLAIMS.before.yaml').write_bytes(before);(out/'CLAIMS.after.yaml').write_bytes(after)
    save(out/'validation.json',validation)
    summary = dict(status='WAVE31_SCOPED_CLAIMS_REGISTERED',timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv],cwd=str(ROOT),source_sha256=sha(Path(__file__)),
        previous_ledger_sha256=OLD_SHA,ledger_sha256=hashlib.sha256(after).hexdigest(),new_claim_ids=new_ids,
        claim_records=312,status_counts=dict(Counter(c['status'] for c in data['claims'])),review_state_counts=dict(Counter(c['review_state'] for c in data['claims'])),
        literal_population=792,distinct_literal_exclusions=380,unresolved_literal_cases=412,new_literal_exclusions=64,
        complete_proof_bytes=proof_bytes+proof['proof_bytes'],new_complete_proof_bytes=proof['proof_bytes'],
        target_resolution='UNKNOWN',overall_search_coverage='UNKNOWN; no validated denominator.',artifact_availability='LOCAL_ONLY',
        independent_checks_performed_by_registrar=0,limitations=['Counts are saved-report identity and disjoint-union checks, not fresh proof replay or target-wide coverage.','Registry hash mode none; individual newly used report artifacts were hashed, full historical closure remains explicitly skipped.'])
    need((ROOT/'CLAIMS.yaml').read_bytes() == before, 'ledger unchanged before atomic replacement')
    pending = out/'CLAIMS.pending.yaml';pending.write_bytes(after)
    os.replace(pending,ROOT/'CLAIMS.yaml')
    save(out/'summary.json',summary)
    print(json.dumps({k:summary[k] for k in ['status','claim_records','status_counts','distinct_literal_exclusions','unresolved_literal_cases','new_claim_ids']}))


if __name__ == '__main__':
    main()
