"""Independent wave18 checkpoint/report and frozen catalog coherence review."""
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import platform
import re
import subprocess
import sys
from audit_20260930_sixteenth_checkpoint import read_ledger, require, sha, write

ROOT = Path(__file__).resolve().parents[1]
B = 'acceleration/results/20260930_'
I = B + 'independent_review/'
GEN = 'acceleration/record_20260930_eighteenth_checkpoint.py'


def check_counts(cp, ledger, ids, zero, mip, cancellation):
    require(cp['claim_population'] == len(ledger['claims']) == 178, 'claim population')
    require(cp['claim_status_counts'] == dict(Counter(c['status'] for c in ledger['claims'])) == {'VERIFIED': 176, 'CANDIDATE': 2}, 'status counts')
    require(cp['claim_review_counts'] == {'CLEAR': 178} and cp['verified_clear'] == 176 and cp['candidate_clear'] == 2, 'review counts')
    require(cp['new_verified_ids'] == ids and len(set(ids)) == len(ids) == 7 and cp['evidence_only_revision_changes'] == [], 'seven exact new claims')
    require(cp['target_resolution'] == 'UNKNOWN' and cp['external_review'] is None and cp['coverage'] == 'Overall search coverage: UNKNOWN; no validated denominator.', 'unresolved target')
    for key in ['new_full_factors', 'complete99_graphs', 'new_whole_support_exclusions', 'new_core_exclusions', 'new_unrestricted_exclusions']:
        require(cp[key] == 0, 'no inflation ' + key)
    require(cp['new_selected_parity_exclusions'] == cp['failed_cnf_builds'] == 1, 'separate branch exclusion and failed build')
    n = cp['native']
    require([n[k] for k in ['distinct_models', 'attempts', 'completed_attempts', 'SAT', 'UNSAT', 'UNKNOWN', 'checked_projection_objects', 'checked_full_factors']] == [2, 2, 2, 2, 0, 0, 2, 0], 'two parity-only SAT calls')
    require(cp['mip'] == dict(attempts=1, completed_attempts=1, UNKNOWN=1, result=mip['result'], exclusion=False), 'one inconclusive MIP call')
    z = cp['first_selected_lift']
    require(z['result'] == 'EXACT_NONNEGATIVE_INFEASIBILITY' and z['counts'] == zero['counts']
            and z['zero_rows'] == [139, 215, 399, 445, 539, 555] and z['scope'] == zero['claim']['scope'] and z['solver_calls'] == 0, 'exact narrow zero-row exclusion')
    require(cp['skipped_lp'] == cancellation and cancellation['actual_research_calls'] == cancellation['actual_control_solver_calls'] == 0, 'LP never executed')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    out = a.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    pins = {}

    def pin(p, expected=None):
        value = sha(ROOT / p)
        require(expected is None or value == expected, 'hash ' + p)
        pins[p] = value
        return value

    def load(p, expected=None):
        pin(p, expected)
        return json.loads((ROOT / p).read_bytes())

    try:
        ids, chain, last = [], [], None
        names = ['preparation', 'zero_row_and_constant', 'support_cut_parity']
        for name in names:
            prefix = B + 'eighteenth_' + name + '_registration/'
            receipt = load(prefix + 'summary.json')
            before, after = prefix + 'CLAIMS.before.yaml', prefix + 'CLAIMS.after.yaml'
            pin(before, receipt['previous_ledger_sha256'])
            pin(after, receipt['ledger_sha256'])
            old, new = read_ledger(ROOT / before), read_ledger(ROOT / after)
            if last is not None:
                require((ROOT / before).read_bytes() == last, 'continuous registrar chain')
            else:
                previous_snapshot = B + 'resume/claims_at_seventeenth_milestone.yaml'
                pin(previous_snapshot)
                published = load(B + 'resume/seventeenth_publication_pointer_receipt.json')
                prior = read_ledger(ROOT / previous_snapshot)
                pin(B + 'resume/claims_before_seventeenth_publication.yaml', published['previous_ledger_sha256'])
                require((ROOT / previous_snapshot).read_bytes() == (ROOT / (B + 'resume/claims_before_seventeenth_publication.yaml')).read_bytes(), 'publication starts at frozen seventeenth ledger')
                require(sha(ROOT / before) == published['ledger_sha256'], 'wave18 starts at authenticated publication ledger')
                committed = subprocess.check_output(['git', 'show', '81320d3cf74339d2ffb1e671f51f0865218ac161:CLAIMS.yaml'], cwd=ROOT)
                require(committed == (ROOT / before).read_bytes(), 'exact prior committed ledger bytes')
                require(prior['claims'] == old['claims'], 'publication preserved all semantic claim records')
                require(set(prior) == set(old), 'publication schema unchanged')
                require(all(prior[k] == old[k] for k in prior if k not in ['updated_at', 'artifacts']), 'only timestamp and artifact availability changed')
                pa, pb = {r['id']:r for r in prior['artifacts']}, {r['id']:r for r in old['artifacts']}
                require(set(pa) == set(pb), 'publication artifact population unchanged')
                changed = [key for key in pa if pa[key] != pb[key]]
                expected_changes = set(published['new_public_artifact_ids']) | {published['recoverable_raw_proof']['artifact_id']}
                require(set(changed) == expected_changes and len(changed) == 9, 'eight public pointers and one recoverable raw proof')
                for key in changed:
                    require(all(pa[key].get(k) == pb[key].get(k) for k in set(pa[key]) | set(pb[key]) if k not in ['availability', 'retrieval', 'unavailable_reason']), 'publication preserves artifact identities')
                    require(published['published_commit'] in pb[key]['retrieval'], 'pinned immutable publication pointer')
                    if key in published['new_public_artifact_ids']:
                        require(pa[key]['availability'] == 'LOCAL_ONLY' and pb[key]['availability'] == 'PUBLIC' and pb[key]['unavailable_reason'] is None, 'public pointer transition')
                    else:
                        require(pa[key]['availability'] == pb[key]['availability'] == 'LOCAL_ONLY', 'raw proof availability remains distinct')
                require(published['mathematical_claim_changes'] == [] and published['published_commit'] == published['confirmed_remote_ref'], 'saved availability-only publication receipt')
            aa, bb = {c['id']: c for c in old['claims']}, {c['id']: c for c in new['claims']}
            require(all(bb[k] == v for k, v in aa.items()), 'existing claim records preserved')
            added = [c['id'] for c in new['claims'] if c['id'] not in aa]
            require(added == receipt['new_claim_ids'] and not receipt['registrar_performs_mathematical_verification'], 'approved integration only')
            ids += added
            chain.append(dict(name=name, before_sha256=sha(ROOT / before), after_sha256=sha(ROOT / after), added=added))
            last = (ROOT / after).read_bytes()
        ledger = new
        claims = {c['id']: c for c in ledger['claims']}
        artifacts = {a['id']: a for a in ledger['artifacts']}
        for cid in ids:
            c = claims[cid]
            require(c['revision'] == 1 and c['status'] == 'VERIFIED' and c['review_state'] == 'CLEAR'
                    and c['scope']['target_resolution'] == 'NONE' and not c['scope']['unrestricted_target'], 'scoped registered claim')
            for d in c['dependencies']:
                require(d['id'] in claims and claims[d['id']]['revision'] == d['revision'], 'pinned dependency')
            for eid in c['evidence']:
                pin(artifacts[eid]['path'], artifacts[eid]['sha256'])
            for v in c['verification']:
                require(v['claim_revision'] == 1 and v['outcome'] == 'PASS', 'verification revision/outcome')
                for eid, value in v['artifact_hashes'].items():
                    require(artifacts[eid]['sha256'] == value, 'verification artifact binding')
        zero = load(I + 'balanced_lift_zero_rows/summary.json', 'a6b7b5fd408e694b12cc630cf0e53e89542b1fe304f2f9d23d94735abe45af7f')
        mip = load(I + 'hadamard_prism_binary_mip_execution/summary.json', 'd50203c013ad81f480317c9543d141a94ef43413f031cf4a8ccbb09973019654')
        cancellation = load(B + 'balanced_lift_lp_not_run/summary.json')
        cp_path = B + 'resume/eighteenth_milestone_checkpoint.json'
        cp = load(cp_path)
        check_counts(cp, ledger, ids, zero, mip, cancellation)
        snap = B + 'resume/claims_at_eighteenth_milestone.yaml'
        pin(snap, cp['ledger_snapshot_sha256'])
        require((ROOT / snap).read_bytes() == last, 'final immutable ledger snapshot')
        for p, value in cp['evidence_sha256'].items():
            pin(p, value)
        previous = load(B + 'resume/seventeenth_milestone_checkpoint.json', cp['previous_checkpoint_sha256'])
        require(previous['claim_population'] == 171, 'previous cohort boundary')
        for run, expected_name, expected_gate, conflicts in zip(cp['native']['runs'],
                ['hadamard_balanced_parity', 'hadamard_parity_support_cuts'],
                ['hadamard_balanced_parity_sat_v2', 'hadamard_parity_support_cuts_sat'], [8999, 11790], strict=True):
            saved = load(B + expected_name + '_native_pilot/summary.json')
            gate = I + expected_gate + '/summary.json'
            obj = load(gate, run['object_gate_sha256'])
            require(obj['status'].endswith('_PASS') and run['object_gate'] == gate, 'actual object gate')
            require(saved['actual_exit_code'] == 10 and saved['research_calls'] == 1, 'one actual native SAT call')
            receipt = saved['receipt']
            for channel in ['stdout', 'stderr']:
                pin(receipt[channel], receipt[channel + '_sha256'])
            log = (ROOT / receipt['stdout']).read_text(encoding='utf-8')
            require(re.search(r'^s SATISFIABLE$', log, re.M) is not None, 'native SAT text')
            got = re.search(r'^c conflicts:\s+(\d+)', log, re.M)
            require(got is not None and int(got[1]) == conflicts == run['conflicts'], 'recorded native conflicts')
            require(run['name'] == expected_name and run['attempts'] == 1 and run['exit_code'] == 10
                    and run['independently_checked_projection'] and not run['full_factor']
                    and run['wrapper_wall_seconds'] == receipt['wall_seconds'], 'native scope and telemetry')
        zcert = load(I + 'balanced_lift_zero_rows/zero_row_certificate.json')
        require(zcert['rhs_product'] == -1 and zcert['column_products'] == [0] * 312, 'bound exact certificate arithmetic record')
        require(mip['result']['valid_native_incumbent'] is False and mip['result']['saved_Gram_objects'] == mip['result']['saved_lazy_cuts'] == 0
                and mip['result']['wrapper_wall_seconds'] == 120.25 and mip['result']['cooperative_overrun_seconds'] == 0.25, 'MIP uncertainty and overrun explicit')
        failed = load(B + 'hadamard_parity_lift_cnf/failure.json')
        require(failed['mathematical_exclusion'] is False, 'failed builder is not proof')
        load(I + 'hadamard_balanced_parity_sat/failure.json')
        pin(GEN)
        require(cp['command'][1] == GEN and '--next-experiment' in cp['command'], 'actual recorder invocation')
        report_path = 'docs/RESEARCH_20260930_EIGHTEENTH_WAVE.md'
        pin(report_path)
        report = (ROOT / report_path).read_text(encoding='utf-8')
        for cid in ids:
            require(report.count('`' + cid + '`') == 1 and claims[cid]['scope']['description'] in report, 'exact claim table scope')
        for token in ['178 claims: 176 VERIFIED/CLEAR and two CANDIDATE/CLEAR', '520', '4,481', '4,541',
                      '312 variables and 560 equations', '5,400 variables and 766 rows', '120.25-second',
                      '0.25 seconds', 'zero new whole-support, core or unrestricted exclusions',
                      'balance remains an additional assumption', 'planned numerical LP was skipped before execution']:
            require(token in report, 'report token ' + token)
        require(cp['timestamp'] in report and cp['source_commit'] in report and cp['next_experiment'] in report, 'report provenance and next action')
        ex = cp['execution']
        for channel in ['stdout', 'stderr']:
            pin(B + 'resume/eighteenth_process_snapshot.' + channel + '.log', ex[channel + '_sha256'])
        text = (ROOT / (B + 'resume/eighteenth_process_snapshot.stdout.log')).read_text(encoding='utf-8')
        require(ex['exit_code'] == 1 and ex['state'] == 'NO_CADICAL_PROCESS_OBSERVED' and len(text.splitlines()) <= 1, 'saved no-native observation only')
        packdir = B + 'eighteenth_artifact_packaging/'
        pack = load(packdir + 'summary.json')
        require(pack['status'] == 'EIGHTEENTH_EXPLICIT_PUBLICATION_INVENTORY_PASS' and pack['claim_ids'] == ids, 'catalog cohort')
        for p, value in pack['output_hashes'].items():
            pin(p, value)
        catalog = load(packdir + 'catalog.json')
        entries = catalog['entries']
        require(len(entries) == len({e['path'] for e in entries}) == pack['selected_files'] == pack['public_research_files'] == 220, 'exact public payload population')
        require(sum(e['bytes'] for e in entries) == pack['public_research_bytes'] == 30245016, 'public payload bytes')
        for e in entries:
            pin(e['path'], e['sha256'])
            require((ROOT / e['path']).stat().st_size == e['bytes'] <= 10 * 1024 * 1024, 'actual published payload size')
            require(not any(s in e['path'] for s in ['hadamard_support_cut_lift_matrix', 'hadamard_f3_phases', 'hadamard_support_cut_lift_primal']), 'wave19 excluded')
        entry_paths = {e['path'] for e in entries}
        for p in [I + 'hadamard_balanced_parity_sat/failure.json', B + 'hadamard_parity_lift_cnf/failure.json',
                  B + 'eighteenth_packaging_preparation/failure.json', B + 'eighteenth_packaging_preparation_v2/failure.json']:
            require(p in entry_paths, 'failed record preserved')
        references = load(packdir + 'reference_checks.json')
        require(references['status'] == 'EXACT_HASH_CLOSURE_PASS' and len(references['records']) == pack['reference_bindings'] == 3216, 'saved reference binding population')
        require(len({r['path'] for r in references['records']}) == pack['unique_referenced_files'] == 347, 'saved unique reference population')
        require(load(packdir + 'reference_diagnostics.json') == {'errors': [], 'count': 0}, 'no unresolved saved reference diagnostics')
        inventory = load(packdir + 'stage_inventory.json')
        require(entry_paths <= set(inventory['paths']), 'explicit stage inventory includes payload')
        guide = 'docs/REPRODUCING_20260930_EIGHTEENTH_WAVE.md'
        pin(guide)
        guide_text = (ROOT / guide).read_text(encoding='utf-8')
        require('not a proved\nnormalization' in guide_text and 'UNKNOWN, not an infeasibility result.' in guide_text
                and 'SAT learned traces are retained, not presented as UNSAT' in guide_text, 'replay scope statements')
        for p in ['README.md', 'ACTIVE_RESEARCH.md', 'docs/RESEARCH_MAP.md', 'docs/REPRODUCING.md']:
            pin(p)
            require('EIGHTEENTH_WAVE' in (ROOT / p).read_text(encoding='utf-8'), 'entry point eighteenth continuation')
        corruptions = []
        for label, route, value in [('claim_count', ['claim_population'], 179), ('support_exclusion', ['new_whole_support_exclusions'], 1),
                ('full_factor', ['new_full_factors'], 1), ('UNSAT', ['native', 'UNSAT'], 1), ('third_SAT', ['native', 'SAT'], 3),
                ('extra_MIP', ['mip', 'attempts'], 2), ('missed_LP_cancellation', ['skipped_lp', 'actual_research_calls'], 1),
                ('zero_row_scope', ['first_selected_lift', 'scope'], 'All factors excluded')]:
            bad = deepcopy(cp)
            where = bad
            for key in route[:-1]:
                where = where[key]
            where[route[-1]] = value
            try:
                check_counts(bad, ledger, ids, zero, mip, cancellation)
            except ValueError:
                corruptions.append(label)
            else:
                raise ValueError('control accepted ' + label)
        for p in ['acceleration/audit_20260930_eighteenth_checkpoint.py', 'acceleration/audit_20260930_eighteenth_checkpoint_v2.py', 'acceleration/audit_20260930_eighteenth_checkpoint_v3.py', 'acceleration/results/20260930_independent_review/eighteenth_checkpoint_v2/failure.json', 'acceleration/results/20260930_independent_review/eighteenth_checkpoint/failure.json', 'acceleration/audit_20260930_sixteenth_checkpoint.py', 'uv.lock', 'pyproject.toml']:
            pin(p)
        summary = dict(status='INDEPENDENT_EIGHTEENTH_CHECKPOINT_REPORT_CONSISTENCY_PASS', timestamp=datetime.now(timezone.utc).isoformat(),
            source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            command=[sys.executable, *sys.argv], cwd=str(ROOT), python=platform.python_version(), inputs_sha256=pins,
            registrar_chain=chain, corrected_checker_assumption='The prior milestone snapshot precedes its nine artifact publication-pointer updates; all semantic claim records are equal, exact publication receipt and committed ledger authenticated. V3 additionally uses explicit UTF-8 decoding of repository text; v2 cp932 failure preserved.', new_claim_ids=ids, counts=dict(claims=178, verified_clear=176, candidate_clear=2,
                new_claims=7, native_SAT_projections=2, MIP_UNKNOWN=1, selected_branch_exclusions=1,
                failed_CNF_builds=1, actual_LP_calls=0, new_whole_support_exclusions=0,
                catalog_payloads=220, catalog_payload_bytes=30245016, reference_bindings=3216, referenced_files=347),
            corruptions=corruptions, final_checks=dict(checkpoint_sha256=sha(ROOT / cp_path),
                report_sha256=sha(ROOT / report_path), snapshot_sha256=sha(ROOT / snap), saved_execution=ex),
            verifier='/root/eight_domain_audit', scope='Registration/checkpoint/report/catalog coherence with authenticated intervening publication metadata; no new mathematical verification.',
            shared_components=['Frozen own sixteenth-checkpoint YAML/hash helpers reused; no recorder or registrar imports.',
                'This reviewer authored two approved-claim integration scripts; this check compares immutable snapshots and root-produced checkpoint/report independently.',
                'Earlier independent mathematical/native gates are authenticated, not rerun.'],
            limitations=['No new mathematical approval or complete target coverage.',
                'All220 current public payloads are freshly hashed; historical347-file closure is authenticated from saved records rather than rerun.',
                'Saved process observation is checked; no assertion about current running processes.'],
            ledger_changed=False, git_changed=False, target_resolution='UNKNOWN')
        write(out / 'summary.json', summary)
        print(json.dumps(dict(status=summary['status'], sha256=sha(out / 'summary.json'))))
    except BaseException as exc:
        write(out / 'failure.json', dict(error=repr(exc), source_sha256=sha(Path(__file__))))
        raise


if __name__ == '__main__':
    main()
