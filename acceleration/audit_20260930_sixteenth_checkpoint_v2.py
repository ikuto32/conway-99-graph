"""Independent sixteenth-cohort v2 consistency audit; preserved v1 plus two recorder prose changes."""
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import platform
import re
import subprocess
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
B = 'acceleration/results/20260930_'
I = B + 'independent_review/'
REGISTRARS = ['preparation', 'cyclic', 'contraction', 'hadamard', 'farkas', 'prism_lp_order', 'compressed']
REVISED = 'C-FIXED-HADAMARD-CONNECTED01-SUPPORT-EXCLUSION'


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def write(path, value):
    with Path(path).open('x', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, indent=2)
        f.write('\n')


class UniqueLoader(yaml.SafeLoader):
    pass


def unique_mapping(loader, node, deep=False):
    result = {}
    for keynode, valnode in node.value:
        key = loader.construct_object(keynode, deep=deep)
        require(key not in result, 'duplicate YAML key')
        result[key] = loader.construct_object(valnode, deep=deep)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def read_ledger(path):
    x = yaml.load(Path(path).read_bytes(), Loader=UniqueLoader)
    require(len({c['id'] for c in x['claims']}) == len(x['claims']), 'duplicate claim ID')
    require(len({a['id'] for a in x['artifacts']}) == len(x['artifacts']), 'duplicate artifact ID')
    return x


def check_numbers(cp, ledger, ids, raw):
    cs = ledger['claims']
    require(cp['claim_population'] == len(cs) == 165, 'claim population')
    require(cp['claim_status_counts'] == dict(Counter(c['status'] for c in cs)) == {'VERIFIED': 163, 'CANDIDATE': 2}, 'claim status counts')
    require(cp['claim_review_counts'] == dict(Counter(c['review_state'] for c in cs)) == {'CLEAR': 165}, 'claim review counts')
    require((cp['verified_clear'], cp['candidate_clear']) == (163, 2), 'verified and candidate clear counts')
    require(cp['new_verified_ids'] == ids and len(ids) == len(set(ids)) == 17, 'new seventeen claims')
    require(cp['evidence_only_revision_changes'] == [dict(id=REVISED, from_revision=1, to_revision=2)], 'one evidence-only revision')
    require(cp['target_resolution'] == 'UNKNOWN' and cp['external_review'] is None, 'target and external review')
    require(cp['external_review_null_reason'] and cp['coverage'] == 'Overall search coverage: UNKNOWN; no validated denominator.', 'unknown scope reasons')
    for key in ['complete99_graphs', 'new_full_factors', 'new_complete_UNSAT_proofs', 'new_unrestricted_exclusions']:
        require(cp[key] == 0, 'no target/factor/proof inflation: ' + key)
    n = cp['native']
    require([n[k] for k in ['completed_attempts', 'SAT', 'UNSAT', 'UNKNOWN']] == [1, 0, 0, 1], 'one native UNKNOWN')
    require(n['outcome'] == raw['outcome']['outcome'] and n['trace'] == raw['outcome']['trace'], 'native raw outcome and trace identity')
    require(cp['propagation'] == dict(initial_local_values=2448, unit_conditioned_values=2040, unit_removed_values=408, AC_removed_values=0), 'arc domains population')
    require(cp['coarse_triples'] == raw['cover']['counts'], 'coarse triple exact counts')
    h = cp['hadamard']
    expected = dict(selected_supports=5, local_pigeonhole_exclusions=1, integer_Farkas_exclusions=3,
                    distinct_fixed_supports_excluded=4, excluded_cores=0, remaining_supports=1,
                    exact_fractional_witnesses=1, full_integer_factors=0, completed_LP_attempts=4)
    require(all(h[k] == v for k, v in expected.items()), 'support population and mathematical scope')
    require(h['numerical_statuses'] == raw['lpstatuses'] and h['Farkas_cases'] == raw['farkas']['cases'], 'LP stages and certificates')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['precheck', 'final'])
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    pins = {}

    def pin(path, expected=None):
        p = ROOT / path
        value = sha(p)
        require(expected is None or value == expected, 'artifact hash: ' + str(path))
        pins[p.relative_to(ROOT).as_posix()] = value
        return value

    def load(path, expected=None):
        pin(path, expected)
        return json.loads((ROOT / path).read_bytes())

    try:
        ids, chain, previous_bytes = [], [], None
        for name in REGISTRARS:
            prefix = B + 'sixteenth_' + name + '_registration/'
            receipt = load(prefix + 'summary.json')
            before, after = prefix + 'CLAIMS.before.yaml', prefix + 'CLAIMS.after.yaml'
            pin(before, receipt['previous_ledger_sha256'])
            pin(after, receipt['ledger_sha256'])
            aa, bb = read_ledger(ROOT / before), read_ledger(ROOT / after)
            if previous_bytes is not None:
                require((ROOT / before).read_bytes() == previous_bytes, 'continuous registrar bytes')
            previous_bytes = (ROOT / after).read_bytes()
            old, new = ({c['id']: c for c in x['claims']} for x in [aa, bb])
            added = [c['id'] for c in bb['claims'] if c['id'] not in old]
            require(added == receipt['new_claim_ids'], 'exact registrar additions')
            changed = [k for k, v in old.items() if new.get(k) != v]
            if name != 'compressed':
                require(changed == [], 'no unintended existing claim change')
            else:
                require(changed == [REVISED] and added == [], 'only one evidence revision')
                a, b = old[REVISED], new[REVISED]
                allowed = {'revision', 'updated_at', 'evidence', 'verification'}
                require({k: v for k, v in a.items() if k not in allowed} == {k: v for k, v in b.items() if k not in allowed}, 'unchanged revised statement/scope/dependencies')
                require(a['revision'] == 1 and b['revision'] == 2, 'revision progression')
                require(b['evidence'][:len(a['evidence'])] == a['evidence'] and b['verification'][:len(a['verification'])] == a['verification'], 'old evidence and review preserved')
                require(any(v['claim_revision'] == 2 and v['outcome'] == 'PASS' for v in b['verification']), 'new revision independently checked')
            require(receipt['registrar_performs_mathematical_verification'] is False, 'registration not mathematical verification')
            ids.extend(added)
            chain.append(dict(registrar=name, added=added, changed=changed, before_sha256=sha(ROOT / before), after_sha256=sha(ROOT / after)))
        ledger = bb
        require(len(aa['claims']) == len(bb['claims']) == 165, 'final compressed population')
        claims = {c['id']: c for c in ledger['claims']}
        artifacts = {a['id']: a for a in ledger['artifacts']}
        for cid in ids:
            c = claims[cid]
            require(c['status'] == 'VERIFIED' and c['review_state'] == 'CLEAR', 'verified clear scoped claim')
            require(c['scope']['target_resolution'] == 'NONE', 'no new target resolution')
            require(c['revision'] == (2 if cid == REVISED else 1), 'exact new claim revision')
            for d in c['dependencies']:
                require(d['id'] in claims and claims[d['id']]['revision'] == d['revision'], 'active dependency revision')
            for eid in c['evidence']:
                a = artifacts[eid]
                pin(a['path'], a['sha256'])
            for v in c['verification']:
                require(v['outcome'] == 'PASS' and v['claim_revision'] in [1, c['revision']], 'recorded independent check')
                for eid, digest in v['artifact_hashes'].items():
                    require(artifacts[eid]['sha256'] == digest, 'exact verification artifact binding')
        require(not any('CYCLIC-FIBRE-REDUCTION' in cid for cid in ids), 'future cyclic-factor cohort excluded')
        impact = load(I + 'farkas_revision2_impact/summary.json', '59bde4c9988d41fc88153949909b93bff6518fed5b8002285b610ed4d0532fd5')
        require(impact['mathematical_statement_changed'] is False and impact['claim_revision'] == 2, 'independent impact scope')
        failure = load(B + 'sixteenth_compressed_registration_failure/failure.json')
        require(failure['actual_ledger_written'] is False and failure['exit_code'] != 0, 'failed registrar made no ledger write')
        raw = {}
        raw['outcome'] = load(I + 'prism_coarse60_bitflip_native_outcome/summary.json')
        run = load(B + 'prism_coarse60_bitflip_native_pilot/summary.json', '3df3239ec412d9b56ea7168d6dd9fddd033d60e3666b181930a659d749ba2539')
        outcome = raw['outcome']
        require(outcome['status'] == 'INDEPENDENT_PRISM_COARSE60_BITFLIP_NATIVE_OUTCOME_AUDIT_PASS', 'independent native outcome')
        require(run['research_calls'] == outcome['actual_attempts'] == 1 and run['actual_exit_code'] == 0, 'one completed native call')
        require(outcome['outcome']['recorded_outcome'] == 'UNKNOWN_NATIVE_CONFLICT_CAP' and outcome['outcome']['observed_final_conflicts'] == 2000001, 'observed UNKNOWN boundary')
        require(outcome['configured_limits']['conflicts'] == 2000000 and outcome['configured_limits']['native_seconds'] == 300, 'configured limits')
        require(outcome['checked_UNSAT_proofs'] == outcome['checked_SAT_objects'] == 0, 'no graph/proof result')
        require(outcome['trace']['availability'] == 'LOCAL_ONLY' and outcome['trace']['unsat_certificate'] is False, 'incomplete trace scope')
        receipt = run['receipt']
        for channel in ['stdout', 'stderr']:
            pin(receipt[channel], receipt[channel + '_sha256'])
        stdout = (ROOT / receipt['stdout']).read_text()
        require(not re.search(r'^s (SATISFIABLE|UNSATISFIABLE)$', stdout, re.M), 'no decisive native status')
        require(int(re.findall(r'^c conflicts:\s+(\d+)', stdout, re.M)[-1]) == 2000001 and 'conflict limit' in stdout, 'literal final conflict count')
        raw['support'] = load(I + 'hadamard20_support_v2/summary.json', 'a8477256446e3e402a2a21241dc383a515162dc9c8c07a9a8e26326c07b0f58f')
        raw['farkas'] = load(I + 'hadamard_support_farkas/summary.json', 'd5a5d63c81a099f49c635ad84861c72ca6aa0c96bea9415dfce188557a5196c1')
        raw['uniform'] = load(I + 'hadamard_six_prism_uniform_lp/summary.json', '6f6e5d601205f1789a3ed1f3128d3305043fc9e7504d63949427df6383cade26')
        raw['order'] = load(I + 'hadamard_six_prism_column_order/summary.json', '0ce1be9ca11a3e860aa97791cfb4f42c1660d937a69ac7a9b7d96ca37640c9d2')
        raw['arc'] = load(I + 'prism_coarse60_arc_v2/summary.json', '04d85bcd864d7586074a68fa8637ec917ce42c93af1fa995fb9e2b5cac86db38')
        raw['cover'] = load(I + 'prism_coarse60_triangle_cover/summary.json', '50add6b76aea5bade3d74cf56be71941aeed3587974efae2af8ebaf7db36754c')
        first = load(B + 'hadamard_support_lp/summary.json')
        rest = load(B + 'hadamard_support_remaining_lp/summary.json')
        require(first['research_calls'] == 1 and rest['attempted_cases'] == rest['completed_cases'] == 3, 'four finite LP attempts')
        raw['lpstatuses'] = [first['model_status']] + [c['model_status'] for c in rest['records']]
        require(Counter(raw['lpstatuses']) == {'HighsModelStatus.kInfeasible': 3, 'HighsModelStatus.kOptimal': 1}, 'LP status population')
        require(raw['support']['case_names'] == ['connected_00', 'connected_01', 'connected_02', 'connected_03', 'six_prism'], 'five frozen supports')
        require(raw['support']['excluded_fixed_support'] == 'connected_00', 'one local support exclusion')
        require([c['core'] for c in raw['farkas']['cases']] == ['connected_01', 'connected_02', 'connected_03'], 'three distinct other supports')
        require(raw['farkas']['excluded_cores'] == 0 and raw['uniform']['counts'] == dict(variables=5400, equations=726, denominator=90, raw_rational_checks=726), 'scope and exact continuous witness counts')
        require(raw['arc']['counts']['conditioned_values'] == 2040 and raw['arc']['counts']['AC_removed_values'] == 0, 'finite AC counts')
        generator = 'acceleration/record_20260930_sixteenth_checkpoint_v2.py'
        pin(generator)
        template = (ROOT / generator).read_text(encoding='utf-8')
        precheck = load(I + 'sixteenth_checkpoint_precheck/summary.json', '607f9e2e8d7274704fcbb62e9ef874c4f03e767cb5e0051e31557fb0821d8e7a')
        require(precheck['status'] == 'INDEPENDENT_SIXTEENTH_CHECKPOINT_PRECHECK_PASS', 'preserved preliminary audit')
        old_checker = 'acceleration/audit_20260930_sixteenth_checkpoint.py'
        pin(old_checker, precheck['inputs_sha256'][old_checker])
        update = load(B + 'sixteenth_checkpoint_preexecution_update/update.json')
        for role in ['original_source', 'updated_source']:
            pin(update[role]['path'], update[role]['sha256'])
        require(update['claim_changes'] is False and update['updated_source']['path'] == generator, 'scope-only recorder update')
        original_path = update['original_source']['path']
        require(precheck['inputs_sha256'][original_path] == update['original_source']['sha256'], 'original recorder precheck binding')
        before = (ROOT / original_path).read_text(encoding='utf-8')
        old_next = 'Independently gated native SAT attempt on the extra cyclic-fibre-triplet subfamily of the remaining fixed Hadamard six-prism support.'
        new_next = 'Independently replay the separately executed cyclic-subfamily UNSAT trace and prepare the broader ordered coloring model for the same fixed Hadamard support; both belong to the next cohort.'
        old_paragraph = '**Next experiment:** run the independently gated cyclic-fibre-triplet construction model for the remaining fixed Hadamard support. This imposes an extra partial-factor restriction, with no target automorphism assumed. A SAT factor still needs an independently checked residual graph and full99-vertex validation; UNSAT would concern only that encoded subfamily.'
        new_paragraph = "**Next experiment:** independently review the separately executed cyclic-subfamily UNSAT result, then test the broader coloring model on the same fixed Hadamard support with independently justified ordering of identical-support columns. The later run and its verification belong to the seventeenth cohort and do not alter this checkpoint's completed-work counts. Its restricted native outcome is not a target resolution. A future factor still needs residual completion and independent full99-vertex validation."
        require(before.count(old_next) == before.count(old_paragraph) == 1, 'two unique source edits')
        require(before.replace(old_next, new_next).replace(old_paragraph, new_paragraph) == template, 'only the two recorded next-action replacements')
        corrected = 'This fractional witness does not establish an integer factor or feasibility of the omitted column caps.'
        require(corrected in template and 'does not satisfy an integer-factor requirement or the omitted column caps' not in template, 'pre-execution fractional-scope clarification')
        expected = dict(claim_population=165, claim_status_counts={'VERIFIED': 163, 'CANDIDATE': 2}, claim_review_counts={'CLEAR': 165}, verified_clear=163, candidate_clear=2,
                        new_verified_ids=ids, evidence_only_revision_changes=[dict(id=REVISED, from_revision=1, to_revision=2)], target_resolution='UNKNOWN', external_review=None,
                        external_review_null_reason='No independently validated target resolution.', coverage='Overall search coverage: UNKNOWN; no validated denominator.',
                        complete99_graphs=0, new_full_factors=0, new_complete_UNSAT_proofs=0, new_unrestricted_exclusions=0,
                        native=dict(completed_attempts=1, SAT=0, UNSAT=0, UNKNOWN=1, outcome=outcome['outcome'], trace=outcome['trace']),
                        propagation=dict(initial_local_values=2448, unit_conditioned_values=2040, unit_removed_values=408, AC_removed_values=0), coarse_triples=raw['cover']['counts'],
                        hadamard=dict(selected_supports=5, local_pigeonhole_exclusions=1, integer_Farkas_exclusions=3, distinct_fixed_supports_excluded=4, excluded_cores=0, remaining_supports=1,
                                      exact_fractional_witnesses=1, full_integer_factors=0, completed_LP_attempts=4, numerical_statuses=raw['lpstatuses'], Farkas_cases=raw['farkas']['cases']))
        check_numbers(expected, ledger, ids, raw)
        controls = []
        mutations = [('claim_count', ['claim_population'], 166), ('verified_count', ['verified_clear'], 164), ('native_UNSAT', ['native', 'UNSAT'], 1),
                     ('core_exclusion', ['hadamard', 'excluded_cores'], 1), ('integer_factor', ['hadamard', 'full_integer_factors'], 1),
                     ('support_denominator', ['hadamard', 'selected_supports'], 3580), ('AC_removal', ['propagation', 'AC_removed_values'], 1), ('target', ['target_resolution'], 'VERIFIED')]
        for label, path, value in mutations:
            bad = deepcopy(expected)
            cursor = bad
            for key in path[:-1]:
                cursor = cursor[key]
            cursor[path[-1]] = value
            try:
                check_numbers(bad, ledger, ids, raw)
            except ValueError:
                controls.append(label)
            else:
                raise ValueError('accepted corruption ' + label)
        final_checks = None
        if args.mode == 'final':
            cp = load(B + 'resume/sixteenth_milestone_checkpoint.json')
            snapshot = B + 'resume/claims_at_sixteenth_milestone.yaml'
            pin(snapshot, cp['ledger_snapshot_sha256'])
            require((ROOT / snapshot).read_bytes() == previous_bytes, 'frozen ledger is exact final registrar')
            check_numbers(cp, ledger, ids, raw)
            for path, digest in cp['evidence_sha256'].items():
                pin(path, digest)
            prev = load(B + 'resume/fifteenth_milestone_checkpoint.json', cp['previous_checkpoint_sha256'])
            require(prev['claim_population'] == 148, 'previous population')
            report_path = 'docs/RESEARCH_20260930_SIXTEENTH_WAVE.md'
            pin(report_path)
            text = (ROOT / report_path).read_text(encoding='utf-8')
            for cid in ids:
                require(text.count('`' + cid + '`') == 1, 'each registered ID once in table')
                c = claims[cid]
                require('| `' + cid + '` r' + str(c['revision']) + ' | ' + c['scope']['description'] in text, 'exact table scope')
            for token in [corrected, '165 claims:163 VERIFIED/CLEAR and2 CANDIDATE/CLEAR', '2,000,001', '2,055,785,844', '2,040 of2,448', '34,220', '18,440', '15,780', '900 of1,296', '27,000', '8,850', '15 separate fibre', '5,400 selectors and726 equalities', 'uniform weights1/90', 'No core family or unrestricted branch was excluded.', 'No new full36x60 factor', 'later run and its verification belong to the seventeenth cohort', 'UNKNOWN; no validated denominator', 'LOCAL_ONLY']:
                require(token in text, 'exact report scope/count: ' + token)
            for name in ['C-FIXED-HADAMARD-SIX-PRISM-CYCLIC-FIBRE-REDUCTION', '122,394', '26,360']:
                require(name not in text, 'later cyclic research excluded from report')
            require(cp['timestamp'] in text and cp['source_commit'] in text, 'report checkpoint provenance')
            process = cp['execution']
            for channel in ['stdout', 'stderr']:
                pin(B + 'resume/sixteenth_process_snapshot.' + channel + '.log', process[channel + '_sha256'])
            lines = (ROOT / (B + 'resume/sixteenth_process_snapshot.stdout.log')).read_text().splitlines()
            if process['exit_code'] == 0:
                require(process['state'] == 'CADICAL_PROCESS_OBSERVED' and len(lines) > 1, 'saved live-process observation')
                require(not any('20260930_prism_coarse60_bitflip/instance.cnf' in s for s in lines[1:]), 'no completed cohort native remains running')
            elif process['exit_code'] == 1:
                require(process['state'] == 'NO_CADICAL_PROCESS_OBSERVED' and len(lines) <= 1, 'saved empty process observation')
            else:
                require(process['state'] == 'UNKNOWN_OBSERVATION_ERROR', 'honest observation error')
            require(process['observed_at'] in text and process['state'] in text, 'report historical process state')
            packaging = load(B + 'sixteenth_artifact_packaging/summary.json')
            require(packaging['status'].endswith('_PASS'), 'catalog gate status')
            catalog = load(B + 'sixteenth_artifact_packaging/catalog.json')
            final_checks = dict(checkpoint_sha256=sha(ROOT / (B + 'resume/sixteenth_milestone_checkpoint.json')), report_sha256=sha(ROOT / report_path),
                                ledger_snapshot_sha256=sha(ROOT / snapshot), process_observation=process, catalog_sha256=sha(ROOT / (B + 'sixteenth_artifact_packaging/catalog.json')))
        for path in ['acceleration/audit_20260930_sixteenth_checkpoint_v2.py', 'uv.lock', 'pyproject.toml']:
            pin(path)
        report = dict(status='INDEPENDENT_SIXTEENTH_CHECKPOINT_REPORT_CONSISTENCY_PASS' if args.mode == 'final' else 'INDEPENDENT_SIXTEENTH_CHECKPOINT_PRECHECK_PASS',
                      timestamp=datetime.now(timezone.utc).isoformat(), source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                      command=[sys.executable, *sys.argv], cwd=str(ROOT), python=platform.python_version(), yaml_version=yaml.__version__, inputs_sha256=pins,
                      recorder_source_update=update, mode=args.mode, counts=dict(claims=165, verified_clear=163, candidate_clear=2, new_claims=17, evidence_only_revisions=1, native_UNKNOWN_attempts=1,
                                                fixed_supports=5, excluded_fixed_supports=4, excluded_cores=0, full_factors=0),
                      registrar_chain=chain, new_claim_ids=ids, corruption_controls=controls, final_checks=final_checks,
                      verifier='/root/eight_domain_audit', method='independent_registration_snapshot_and_saved_report_consistency_check',
                      template_review='Before any report was written, ambiguous negative language about omitted LP caps was changed to an explicit absence-of-establishment statement.',
                      shared_components=['Python standard library and PyYAML. No recorder or registrar imports. This v2 preserves the frozen v1 consistency logic and independently checks the two recorder next-action prose changes.', 'Earlier independent mathematical audits and native outcome checks are authenticated and compared, not rerun. Some of those earlier audits were authored by this reviewer.'],
                      limitations=['No new mathematical verification or claim promotion.', 'The 2GB partial trace is not rehashed again; its completed independent full-hash receipt and native stdout are checked.',
                                   'Publication closure is not recomputed by this coherence audit.', 'Saved process observations are historical; this audit makes no current process-state assertion.'],
                      target_resolution='UNKNOWN', artifact_availability='LOCAL_ONLY', ledger_changed=False, git_changed=False)
        write(out / 'summary.json', report)
        print(json.dumps(dict(status=report['status'], sha256=sha(out / 'summary.json'))))
    except BaseException as exc:
        write(out / 'failure.json', dict(error=repr(exc)))
        raise


if __name__ == '__main__':
    main()
