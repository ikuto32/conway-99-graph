"""Independent Root engineering check of the frozen eleven-claim projection."""
import argparse
import copy
import hashlib
import importlib.util
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SUBJECT = 'acceleration/register_20261003_bound_claims_v20.py'
DESCRIPTOR = 'acceleration/proposal_20261003_wave44_claim_registry_descriptors_v3.json'
PINS = {
    SUBJECT: '58f4fd6fe5c69296a55cddf00e4a0185c21a13ef3d97c173984f030038d4f78b',
    DESCRIPTOR: 'da5e279d4e6157d69c73f325d91b73f084cde7761f070956e11f8bd28421f6da',
    'acceleration/validate_claims.py': 'a48f55b54918b0c494e6f06f80bdcdc52f304dfc370dd25842aeae3a0f861265',
    'docs/claims.schema.json': '0d752f62c7c9a43c7ddc5fbfe8d2c5644eec3d70d1baea236cb290d475aa5dac',
    'acceleration/command_deadline.py': '9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9',
    'pyproject.toml': '273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339',
    'uv.lock': 'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',
}


class CheckError(ValueError):
    pass


class InterceptedWrite(RuntimeError):
    pass


def require(condition, stage):
    if not condition:
        raise CheckError(stage)


def same(left, right):
    if type(left) is not type(right):
        return False
    if type(left) is dict:
        return set(left) == set(right) and all(same(left[k], right[k]) for k in left)
    if type(left) is list:
        return len(left) == len(right) and all(same(a, b) for a, b in zip(left, right))
    return left == right


def projection(before, after, records, bindings):
    count = len(before['claims'])
    require(count == 389 and len(after['claims']) == 400, 'CLAIM_POPULATION')
    require(same(after['claims'][:count], before['claims']), 'PRIOR_CLAIMS')
    require(same(after['artifacts'][:len(before['artifacts'])], before['artifacts']), 'PRIOR_ARTIFACTS')
    for key in set(before) | set(after):
        if key not in {'claims', 'artifacts', 'updated_at'}:
            require(key in before and key in after and same(before[key], after[key]), 'PRIOR_ROOT:' + key)
    artifacts = {a['id']: a for a in after['artifacts']}
    require(len(artifacts) == len(after['artifacts']), 'ARTIFACT_IDS')
    for claim, record, binding in zip(after['claims'][count:], records, bindings):
        for key in ['id', 'revision', 'statement', 'kind', 'basis', 'status', 'review_state', 'assumptions', 'limitations']:
            require(same(claim[key], binding[key]), 'NEW_CLAIM:' + key)
        require(same(claim['scope'], record['proposed_schema_scope']), 'NEW_SCOPE')
        require(same(claim['dependencies'], record['proposed_dependencies']), 'NEW_DEPENDENCIES')
        require(len(claim['verification']) == 1, 'VERIFICATION_POPULATION')
        check = claim['verification'][0]
        expected = {'claim_revision': 1, 'verifier': binding['verifier'], 'method': binding['method'],
                    'timestamp': binding['verification_timestamp'], 'outcome': 'PASS',
                    'command_or_audit': binding['report'], 'scope': record['proposed_schema_scope']['description']}
        for key, value in expected.items():
            require(same(check[key], value), 'VERIFICATION:' + key)
        expected_paths = {record['binding']['path']: record['binding']['sha256'],
                          binding['report']: binding['report_sha256'], **binding['inputs_sha256']}
        observed = {}
        for aid in claim['evidence']:
            artifact = artifacts[aid]
            require(artifact['availability'] == 'LOCAL_ONLY', 'NEW_AVAILABILITY')
            require(aid in check['artifact_hashes'] and check['artifact_hashes'][aid] == artifact['sha256'], 'VERIFICATION_HASH')
            require(artifact['path'] not in observed, 'DUPLICATE_EVIDENCE_PATH')
            observed[artifact['path']] = artifact['sha256']
        require(same(observed, expected_paths), 'EXACT_EVIDENCE_MAP')
    return {'before': count, 'after': len(after['claims']), 'added': 11,
            'ids': [c['id'] for c in after['claims'][count:]], 'prior_typed_content_preserved': True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--seconds', type=float, required=True)
    parser.add_argument('--out', required=True)
    for name in ['self-sha256', 'spec-sha256', 'author', 'author-sha256', 'author-terminal',
                 'author-terminal-sha256', 'expected-head', 'ledger-sha256', 'index-sha256']:
        parser.add_argument('--' + name, required=True)
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='Independent exact eleven metadata protected-copy check, 20 second save reserve, no raw mathematics')
    out = Path(args.out).resolve()
    require(out.is_relative_to(ROOT) and not out.exists(), 'FRESH_OUTPUT')
    out.mkdir(parents=True)
    inputs, controls, observed_hashes = {}, [], {}
    before_bytes = (ROOT / 'CLAIMS.yaml').read_bytes()
    before = yaml.safe_load(before_bytes)

    def reserve():
        state = deadline.status()
        require(not state['stop_required'] and state['remaining_seconds'] > 20, 'SAVE_RESERVE')

    def digest(path):
        reserve()
        path = Path(path).resolve()
        require(path.is_relative_to(ROOT) and path.is_file(), 'BOUNDED_INPUT')
        h = hashlib.sha256()
        with path.open('rb') as stream:
            while block := stream.read(1024 * 1024):
                reserve()
                h.update(block)
        result = h.hexdigest()
        name = path.relative_to(ROOT).as_posix()
        require(name not in observed_hashes or observed_hashes[name] == result, 'CHANGED_DURING_RUN')
        observed_hashes[name] = result
        return result

    def pin(path, identity):
        require(digest(ROOT / path) == identity, 'INPUT_IDENTITY:' + path)
        inputs[path] = identity

    def protected():
        require((ROOT / 'CLAIMS.yaml').read_bytes() == before_bytes and digest(ROOT / '.git/index') == args.index_sha256
                and subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() == args.expected_head, 'PROTECTED_CONTEXT')

    def save(name, value):
        with (out / name).open('x', encoding='utf8', newline='\n') as stream:
            json.dump(value, stream, indent=2, allow_nan=False)
            stream.write('\n')

    prior_replace, prior_argv = os.replace, sys.argv
    try:
        require(hashlib.sha256(before_bytes).hexdigest() == args.ledger_sha256, 'BASE_LEDGER')
        protected()
        pin(Path(__file__).relative_to(ROOT).as_posix(), args.self_sha256)
        pin(Path(__file__).with_name(Path(__file__).stem + '_spec.md').relative_to(ROOT).as_posix(), args.spec_sha256)
        for path, identity in PINS.items():
            pin(path, identity)
        for path, identity in [(args.author, args.author_sha256), (args.author_terminal, args.author_terminal_sha256)]:
            pin(path, identity)
        author = json.loads((ROOT / args.author).read_bytes())
        terminal = json.loads((ROOT / args.author_terminal).read_bytes())
        require(author['status'] == 'V20_AUTHOR_HELPER_CONTROLS_PASS_PENDING_INDEPENDENT_ENGINEERING_REVIEW'
                and same([author[k] for k in ['positive_controls', 'strict_negative_controls', 'harness_negative_controls', 'metadata_mappings', 'registrar_main_called', 'independent_approval']], [46, 335, 2, 9, False, False]), 'AUTHOR_SCOPE')
        require(type(terminal['command_exit_code']) is int and terminal['command_exit_code'] == 0
                and terminal['error'] is None and terminal['deadline_reached'] is False
                and terminal['cleanup']['reaped'] is True and terminal['cleanup']['job_active_zero_observed'] is True
                and terminal['cleanup']['cleanup_errors'] == [], 'AUTHOR_TERMINAL')
        for path, identity in author['inputs_sha256'].items():
            pin(path, identity)
        records = json.loads((ROOT / DESCRIPTOR).read_bytes())['records']
        require(len(records) == 11 and [r['order'] for r in records] == list(range(1, 12)), 'FROZEN_ORDER')
        bindings = []
        for record in records:
            pin(record['binding']['path'], record['binding']['sha256'])
            binding = json.loads((ROOT / record['binding']['path']).read_bytes())
            require(binding['id'] == record['id'] and type(binding['revision']) is int and binding['revision'] == 1, 'BOUND_ID')
            bindings.append(binding)
        spec = importlib.util.spec_from_file_location('root_v20_projection_subject', ROOT / SUBJECT)
        subject = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(subject)
        subject.digest = digest  # Independent deadline-aware hashing, no acceptance bypass.
        dest = out / 'eleven_protected_copy'

        def intercept(source, target):
            require(Path(target).resolve() == ROOT / 'CLAIMS.yaml' and Path(source).resolve() == dest / 'CLAIMS.pending.yaml', 'SOLE_WRITE_BARRIER')
            protected()
            save('intercepted_report.json', copy.deepcopy(sys._getframe(1).f_locals['report']))
            raise InterceptedWrite()

        os.replace = intercept
        sys.argv = [str(ROOT / SUBJECT), '--out', str(dest), '--previous-sha256', args.ledger_sha256]
        for record in records:
            sys.argv += ['--binding', str(ROOT / record['binding']['path']), '--binding-sha256', record['binding']['sha256']]
        try:
            subject.main()
        except InterceptedWrite:
            pass
        else:
            raise CheckError('WRITE_BARRIER_NOT_REACHED')
        os.replace, sys.argv = prior_replace, prior_argv
        reserve()
        after = yaml.safe_load((dest / 'CLAIMS.after.yaml').read_bytes())
        result = projection(before, after, records, bindings)
        for index in range(11):
            for field, value, stage in [('statement', 'Broader unsupported claim.', 'NEW_CLAIM:statement'),
                                        ('revision', True, 'NEW_CLAIM:revision'), ('status', 'UNKNOWN', 'NEW_CLAIM:status'),
                                        ('scope', {}, 'NEW_SCOPE'), ('dependencies', [{'id': 'C-FICTION'}], 'NEW_DEPENDENCIES')]:
                mutated = copy.deepcopy(after)
                mutated['claims'][389 + index][field] = value
                try:
                    projection(before, mutated, records, bindings)
                except CheckError as error:
                    require(str(error) == stage, 'WRONG_CONTROL_STAGE')
                    controls.append({'id': records[index]['id'], 'field': field, 'expected': stage, 'actual': str(error)})
                else:
                    raise CheckError('CORRUPTION_ACCEPTED')
                reserve()
        require(len(controls) == 55, 'CONTROL_POPULATION')
        protected()
        save('projection.json', result)
        save('controls.json', controls)
        save('summary.json', {'status': 'INDEPENDENT_REGISTRAR_V20_ELEVEN_PROTECTED_COPY_PASS', 'timestamp': datetime.now(timezone.utc).isoformat(),
                             'producer': '/root/checkpoint_audit', 'verifier': '/root', 'method': 'independent_engineering_artifact_check',
                             'command': [sys.executable, *prior_argv], 'cwd': str(ROOT), 'source_commit': args.expected_head,
                             'python': platform.python_version(), 'inputs_sha256': inputs, 'all_subject_hashes_observed': observed_hashes,
                             'projection': result, 'precise_corrupted_projection_controls': 55, 'write_barriers': 1,
                             'live_ledger_mutated': False, 'index_mutated': False, 'mathematical_replays': 0, 'target_resolution': 'UNKNOWN',
                             'shared_components': ['V20 main is the engineering subject; existing YAML/schema validation is trusted common code.', 'Separate Root typed YAML projection/evidence-map checks and deadline-aware hashing; no mathematical producer imported.'],
                             'limitations': ['Frozen eleven bindings and389 baseline only; no mathematical reapproval, external review, public availability promotion or live ledger registration.', '55 output-projection corruptions test this independent result predicate, not every source/filesystem/atomic-write failure.'],
                             'deadline': deadline.status()})
    except BaseException as error:
        save('failure.json', {'error': repr(error), 'controls_completed': len(controls), 'inputs_sha256': inputs, 'deadline': deadline.status()})
        raise
    finally:
        os.replace, sys.argv = prior_replace, prior_argv
        require((ROOT / 'CLAIMS.yaml').read_bytes() == before_bytes and hashlib.sha256((ROOT / '.git/index').read_bytes()).hexdigest() == args.index_sha256, 'FINAL_PROTECTED_CONTEXT')


if __name__ == '__main__':
    main()
