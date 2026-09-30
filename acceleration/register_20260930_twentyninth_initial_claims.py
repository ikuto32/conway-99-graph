"""Prepare three exact independently bound registrations; apply only when requested."""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import argparse, copy, hashlib, json, re, subprocess, sys, traceback, yaml
import validate_claims as registry

ROOT = Path(__file__).resolve().parents[1]
I = 'acceleration/results/20260930_independent_review/'
COHORTS = [
    ('exact_eight_next64_cnfs_v3',
     '517ac1c4d51a9eb5da4b6a3579bf5f6b23bfdb670bac5624da22414c3d24da6a',
     '547bee2b990e3d3e6b4a0848b9d44daacf733f08aecd6afcc3c0f5bc46a4ef48',
     'C-FIXED-HADAMARD-EXACT-EIGHT-NEXT64-GRAM-ENCODINGS',
     'INDEPENDENT_EXACT_EIGHT_EXPLICIT_BATCH_ENCODING_PASS', '/root/structural_attack'),
    ('exact_eight_next64_proofs',
     '7e2cab83b264a30e35a5797137b4948fb59d30e1b1b234ed5ab54e517c13881f',
     '623a3f0c1897ac1d15ea496fdcde8a61826961471b272d9a46472018c634ab50',
     'C-FIXED-HADAMARD-EXACT-EIGHT-NEXT64-LITERAL-PROFILE-EXCLUSIONS',
     'INDEPENDENT_EXACT_EIGHT_EXPLICIT_BATCH_LITERAL_PROOFS_PASS', '/root/structural_attack'),
    ('sizeclass16_gf3_affine_weights',
     '232a38f1a761915f1c5308a1597f9f7ba121dd9372198a7b5a0b6ff55b125834',
     '21533a9548158e5322e465dc834eb80acd45f137b94e728b96e1b3d44bdbbaf2',
     'C-FIXED-HADAMARD-SIZECLASS16-GF3-AFFINE-GRAM-WITNESSES',
     'INDEPENDENT_SIZECLASS16_GF3_AFFINE_WEIGHTS_PASS', '/root'),
]
INPUTS = {}
HASH_CACHE = {}


def need(value, message):
    if not value:
        raise ValueError(message)


def safe(name):
    p = Path(name)
    p = p.resolve() if p.is_absolute() else (ROOT / p).resolve()
    need(p.is_relative_to(ROOT), 'outside repository')
    rel = p.relative_to(ROOT).as_posix()
    need(not rel.startswith('tools/') and p.name != 'PROMPT.md'
         and rel != I + 'hadamard_oriented_unknown/process.stdout.log', 'protected path')
    return p


def h(name):
    name = str(name).replace('\\', '/')
    if name not in HASH_CACHE:
        p = safe(name)
        with p.open('rb') as stream:
            digest = hashlib.file_digest(stream, 'sha256').hexdigest()
        HASH_CACHE[name] = digest
        INPUTS[p.relative_to(ROOT).as_posix()] = digest
    return HASH_CACHE[name]


def read(name):
    h(name)
    return json.loads(safe(name).read_bytes())


def bind(name, digest):
    need(re.fullmatch('[0-9a-f]{64}', digest) is not None, 'malformed expected hash')
    need(h(name) == digest, 'input identity ' + str(name))


def save(path, value):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def validate_binding(row, audit, cohort):
    directory, sh, bh, cid, status, verifier = cohort
    need(audit['status'] == status, 'exact independent status')
    need(row['id'] == cid and row['revision'] == 1
         and row['status'] == 'VERIFIED' and row['review_state'] == 'CLEAR'
         and row['verifier'] == verifier, 'exact bound claim identity')
    need(bool(row['statement']) and bool(row['scope']) and bool(row['assumptions'])
         and bool(row['shared_components']) and bool(row['method']), 'complete exact binding')
    need(row['created_at'] and row['updated_at'] and audit['timestamp'], 'actual bound timestamps')
    if directory == 'sizeclass16_gf3_affine_weights':
        need('there exist GF(3) weights' in row['statement']
             and 'rank' not in row['statement'].lower(), 'GF3 witness-only statement')
        need('no rank' in row['scope'].lower()
             and 'No rank193 or basis-spanning claim is checked.' in row['limitations'],
             'unchecked rank explicitly excluded')
        need(row['independent_report'] == dict(path=I + directory + '/summary.json', sha256=sh),
             'GF3 exact independent report')


def check_populations(rows, audits):
    enc, proof, gf3 = audits
    erow, prow, grow = rows
    ec = enc['checked_cases']
    pc = proof['case_records']
    need(erow['checked_cases'] == ec and prow['case_records'] == pc,
         'binding and report literal populations equal')
    ids = [r['case_id'] for r in ec]
    need(len(ids) == len(set(ids)) == 64 and ids == enc['selected_case_ids']
         and ids == proof['selected_case_ids'] == [r['case_id'] for r in pc],
         'same ordered64 formulas/proofs')
    for a, b in zip(ec, pc):
        for field in ['case_id', 'case_index', 'subset_index', 'full_count_profile_sha256',
                      'cnf_path', 'cnf_sha256', 'scope_path', 'scope_sha256']:
            need(a[field] == b[field], 'literal formula/proof identity ' + field)
        need(a['all_initial_domains'] and a['complete_raw_clause_reconstruction'],
             'complete initial domains and clauses')
        need(b['outcome'] == 'UNSAT_VERIFIED' and b['trace']['complete_proof']
             and b['replay']['accepted'] and b['replay']['actual_exit_code'] == 0,
             'complete successful proof replay')
    need(enc['complete_formulas'] == proof['completed_attempts']
         == proof['completed_proof_replays'] == 64
         and proof['SAT_verified'] == proof['UNKNOWN'] == 0
         and proof['pending_case_ids'] == [], 'all64 completed')
    need(proof['encoding_gate_path'] == I + COHORTS[0][0] + '/summary.json'
         and proof['encoding_gate_sha256'] == COHORTS[0][1], 'same encoding premise')
    need(set(ids).isdisjoint(enc['skipped_verified_case_ids'])
         and prow['prior_literal_overlap'] == proof['prior_literal_overlap']
         and proof['prior_literal_overlap']['overlap_with_skipped_cases'] == [],
         'prior literal cases not recounted')
    need(gf3['cases'] == len(gf3['records']) == len({r['case_id'] for r in gf3['records']}) == 16
         and gf3['residue_entries'] == 16 * 36 * 36
         and gf3['affine_normalizations'] == 16 * 20, 'complete16 affine witness scope')
    return dict(encoding_profiles=64, complete_literal_proofs=64,
                proof_bytes=sum(r['trace']['bytes'] for r in pc), gf3_witness_profiles=16,
                new_orbit_or_population_union=False, gf3_rank_checked=False,
                no_mathematical_reexecution=True)


def convert(row, audit, evidence, hashes):
    limits = copy.deepcopy(row.get('limitations', [row['scope']]))
    verification = dict(claim_revision=1, verifier=row['verifier'],
                        method='independent_artifact_check', command_or_audit=evidence[0][1],
                        timestamp=audit['timestamp'], outcome='PASS', scope=row['scope'],
                        artifact_hashes=copy.deepcopy(hashes),
                        shared_components=copy.deepcopy(row['shared_components']),
                        controls=[row['method'], 'Exact controls and corruption outcomes are retained in the bound independent report; the registrar performs no new mathematical or native/proof execution.'],
                        limitations=copy.deepcopy(limits))
    return dict(id=row['id'], revision=1, statement=row['statement'], kind=row['kind'],
                basis=copy.deepcopy(row['basis']), status='VERIFIED', review_state='CLEAR',
                scope=dict(description=row['scope'], unrestricted_target=False, target_resolution='NONE'),
                assumptions=copy.deepcopy(row['assumptions']),
                dependencies=copy.deepcopy(row['dependencies']), evidence=[a for a, _ in evidence],
                verification=[verification], limitations=limits,
                created_at=row['created_at'], updated_at=row['updated_at'], external_source=None,
                unknowns=dict(external_source='Internal independent review; no external peer review asserted.'),
                reproducibility=dict(manifest=evidence[0][0]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--expected-ledger-sha256', required=True)
    ap.add_argument('--ledger', default='CLAIMS.yaml', help='Alternative immutable input is allowed only in dry-build mode.')
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--apply', action='store_true', help='Write live CLAIMS.yaml only after separate root authorization.')
    args = ap.parse_args()
    ledger_path = safe(args.ledger)
    need(not args.apply or ledger_path == ROOT / 'CLAIMS.yaml', 'apply requires live CLAIMS.yaml')
    out = args.out.resolve()
    need(out.is_relative_to(ROOT), 'output outside repository')
    out.mkdir(parents=True, exist_ok=False)
    before_live = (ROOT / 'CLAIMS.yaml').read_bytes()
    before = ledger_path.read_bytes()
    start_commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    try:
        bind(args.ledger, args.expected_ledger_sha256)
        for p in [Path(__file__), Path(__file__).with_name(Path(__file__).stem + '_spec.md'),
                  ROOT / 'acceleration/validate_claims.py', ROOT / 'docs/claims.schema.json']:
            h(p)
        old = registry.read_ledger(ledger_path)
        need(len(old['claims']) == 294 and Counter(c['status'] for c in old['claims'])
             == dict(VERIFIED=287, CANDIDATE=3, REFUTED=4), 'exact294 starting population')
        rows, audits = [], []
        for cohort in COHORTS:
            directory, sh, bh, cid, status, verifier = cohort
            sp, bp = I + directory + '/summary.json', I + directory + '/claim_binding.json'
            bind(sp, sh)
            bind(bp, bh)
            audit, row = read(sp), read(bp)
            validate_binding(row, audit, cohort)
            for obj in [audit, row]:
                for field in ['inputs_sha256', 'outputs_sha256', 'evidence_sha256', 'artifact_hashes']:
                    for ref, digest in obj.get(field, {}).items():
                        bind(ref, digest)
            rows.append(row)
            audits.append(audit)
        population_check = check_populations(rows, audits)
        corruptions = []

        def reject(name, fn):
            try:
                fn()
            except (ValueError, KeyError, TypeError):
                corruptions.append(name)
                return
            raise ValueError('corrupted registration accepted: ' + name)

        bad = copy.deepcopy(rows[2]); bad['statement'] += ' The rank is193.'
        reject('GF3 unreviewed rank statement', lambda: validate_binding(bad, audits[2], COHORTS[2]))
        bad = copy.deepcopy(rows[2]); bad['verifier'] = '/root/state_literature_audit'
        reject('substituted verifier', lambda: validate_binding(bad, audits[2], COHORTS[2]))
        bad = copy.deepcopy(audits); bad[1]['case_records'][0]['cnf_sha256'] = '0' * 64
        reject('mismatched proof formula', lambda: check_populations(rows, bad))
        bad = copy.deepcopy(audits); bad[1]['completed_proof_replays'] = 63
        reject('incomplete proof population', lambda: check_populations(rows, bad))
        bad = copy.deepcopy(audits); bad[2]['affine_normalizations'] = 319
        reject('incomplete affine witnesses', lambda: check_populations(rows, bad))
        reject('wrong expected binding hash', lambda: bind(I + COHORTS[2][0] + '/claim_binding.json', '0' * 64))
        data = copy.deepcopy(old)
        ids = []
        for index, (row, audit, cohort) in enumerate(zip(rows, audits, COHORTS)):
            folder = I + cohort[0] + '/'
            evidence = [(f'twentyninth-initial-{index}-evidence{j}', folder + name)
                        for j, name in enumerate(['summary.json', 'claim_binding.json'])]
            hashes = {aid: h(p) for aid, p in evidence}
            for aid, p in evidence:
                need(aid not in {a['id'] for a in data['artifacts']}, 'new evidence ID')
                data['artifacts'].append(dict(id=aid, path=p, sha256=hashes[aid], availability='LOCAL_ONLY',
                    retrieval='Exact workspace path; independent reports bind full raw evidence, source, commands and controls.',
                    unavailable_reason='Twenty-ninth immutable evidence publication not yet confirmed.'))
            need(row['id'] not in {c['id'] for c in data['claims']}, 'new claim ID')
            claim = convert(row, audit, evidence, hashes)
            need(claim['statement'] == row['statement'] and claim['scope']['description'] == row['scope']
                 and claim['dependencies'] == row['dependencies']
                 and claim['verification'][0]['shared_components'] == row['shared_components'],
                 'exact statement/scope/dependencies/shared components')
            for dep in claim['dependencies']:
                match = [c for c in data['claims'] if c['id'] == dep['id']]
                need(len(match) == 1 and match[0]['revision'] == dep['revision']
                     and match[0]['status'] == 'VERIFIED' and match[0]['review_state'] == 'CLEAR',
                     'current trusted dependency ' + dep['id'])
            data['claims'].append(claim)
            ids.append(claim['id'])
        need(data['claims'][:-3] == old['claims'] and data['artifacts'][:-6] == old['artifacts'],
             'all prior records unchanged')
        need(len(data['claims']) == 297 and Counter(c['status'] for c in data['claims'])
             == dict(VERIFIED=290, CANDIDATE=3, REFUTED=4), 'exact297 proposed population')
        now = datetime.now(timezone.utc).isoformat()
        data['updated_at'] = now
        validation = registry.validate(data, ROOT, read('docs/claims.schema.json'), 'available', old)
        save(out / 'validation.json', validation)
        need(validation['valid'], 'registry validation: ' + repr(validation['errors']))
        after = yaml.safe_dump(data, sort_keys=False, width=110).encode('utf8')
        (out / 'CLAIMS.before.yaml').write_bytes(before)
        (out / ('CLAIMS.after.yaml' if args.apply else 'CLAIMS.proposed.yaml')).write_bytes(after)
        save(out / 'controls.json', dict(rejected=corruptions))
        save(out / 'binding_review.json', population_check)
        result = dict(status='TWENTYNINTH_THREE_CLAIMS_REGISTERED' if args.apply else 'TWENTYNINTH_THREE_CLAIMS_DRY_BUILD_PASS',
            timestamp=now, source_commit=start_commit, command=[sys.executable, *sys.argv], cwd=str(ROOT),
            registrar_sha256=h(Path(__file__)), input_ledger_path=ledger_path.relative_to(ROOT).as_posix(),
            previous_ledger_sha256=hashlib.sha256(before).hexdigest(), proposed_ledger_sha256=hashlib.sha256(after).hexdigest(),
            ledger_sha256=hashlib.sha256(after).hexdigest() if args.apply else None,
            live_ledger_write_performed=args.apply, new_claim_ids=ids, previous_claim_count=294, claim_population=297,
            new_verified=3, status_counts=dict(VERIFIED=290, CANDIDATE=3, REFUTED=4),
            existing_claim_records_unchanged=True, existing_artifact_records_unchanged=True,
            checked_input_bindings=INPUTS, validation=validation, population_binding_review=population_check,
            binding_editorial_adaptations=['Exact bound statements, scope text, assumptions, dependency IDs/revisions/relations, timestamps and shared-component disclosures are copied unchanged.',
                'Registry verification method enum is independent_artifact_check; the verbatim independent checking method is retained in its controls.',
                'When the encoding binding omits a redundant limitations array, its exact scope is copied as the sole limitation.',
                'All six evidence records remain LOCAL_ONLY until actual immutable publication.'],
            registrar_performs_mathematical_verification=False, target_resolution='UNKNOWN')
        need(ledger_path.read_bytes() == before, 'input ledger changed during preparation')
        if args.apply:
            need((ROOT / 'CLAIMS.yaml').read_bytes() == before_live == before,
                 'live ledger changed before authorized write')
            (ROOT / 'CLAIMS.yaml').write_bytes(after)
        save(out / 'summary.json', result)
        if not args.apply:
            need((ROOT / 'CLAIMS.yaml').read_bytes() == before_live,
                 'live ledger changed concurrently; no registrar write occurred')
        print(json.dumps(dict(status=result['status'], proposed_claims=297,
                              new_verified=3, ledger_write_performed=args.apply)))
    except BaseException as ex:
        save(out / 'failure.json', dict(error=repr(ex), traceback=traceback.format_exc(),
                                       checked_input_bindings=INPUTS,
                                       apply_requested=args.apply))
        raise


if __name__ == '__main__':
    main()
