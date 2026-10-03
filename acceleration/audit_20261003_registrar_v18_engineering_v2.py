"""Independent ROOT metadata gate; intercepted copies, no live ledger write."""
import argparse
import ast
import copy
import hashlib
import importlib.util
import json
import os
import platform
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import yaml
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
OLD = 'acceleration/register_20261003_bound_claims_v17.py'
NEW = 'acceleration/register_20261003_bound_claims_v18.py'
DESCRIPTOR = 'acceleration/proposal_20261003_registrar_v18_exact_written_v1.json'
ADDITIONS = 'acceleration/register_20261003_bound_claims_v18_additions_v1.py.txt'
PINS = {OLD: '1ae20114929478bbfbcde7acdc42582453aefe003e76c801bd48353eb2a74e84',
        NEW: 'b310e6772f853af3e8faa867c3c60896b27234fe70b3e0c930f5bd46d1123207',
        DESCRIPTOR: '2692248d4274793d5fb162503d1eb3b9e5b02a517ef13f5fd6080ffc80f49629',
        ADDITIONS: '9890ee43b890977480e0e18c658b8969236b51737b2f5d9ff1986d0a3490296c',
        'acceleration/register_20261003_bound_claims_v18_spec.md': 'dfebe8d3f2e03bbec67d8d5e615f37082c0e7ba4a61c8c6dc698d29809e84bfc',
        'acceleration/calibrate_20261003_registrar_v18_helpers_v1.py': 'c28777fca791ce6b2013cdc762500a5e0eceb45f9f6d88ac21a45c4871d05dbb',
        'acceleration/calibrate_20261003_registrar_v18_helpers_v1_spec.md': '488fe3c3dd683d207e90e037cf744743ec1a32c74c9f26d61acbc36304303675'}
ORDINARY = [('ternary_eight_defect_nonrealizability01', '307fde2da899d96995f87103accacd66d886d27f987a262688248ca2968a6fdd'),
            ('ternary_ten_defect_nonrealizability01', 'c6abcea28dadf164c277f9100199ba02ef9cb66581fd36307fb632f8880742cd'),
            ('ternary_k2_6_integer_lift01', '47e5f29f45ffdc23a07c088a7dbb91657845064cfd1050a46ff0176c1250cb88'),
            ('ternary_octahedral_support01', 'e796ca1ec1dccb4014391966253a2d929fa4304f2954f9252d705ace9cc4fc4d'),
            ('ternary_nonzero_defect_lower13_01', 'd792f31eb80f3b7e5cc6620d8026ccb77444284f1abe7f6e4f3c59f7571e14ff')]


class GateError(ValueError): pass
class ProtectedWrite(RuntimeError): pass


def need(ok, stage):
    if not ok: raise GateError(stage)


def sha(path):
    with path.open('rb') as stream: return hashlib.file_digest(stream, 'sha256').hexdigest()


def write(path, value):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, indent=2, allow_nan=False); stream.write('\n')


def equal(x, y):
    if type(x) is not type(y): return False
    if type(x) is dict: return set(x) == set(y) and all(equal(x[k], y[k]) for k in x)
    if type(x) in (tuple, list): return len(x) == len(y) and all(equal(a, b) for a, b in zip(x, y))
    return x == y


def ast_restore(old_text, new_text, addition_text):
    old, new, additions = map(ast.parse, (old_text, new_text, addition_text))
    dump = lambda n: ast.dump(n, include_attributes=False)
    names = {'V18_DESCRIPTOR', 'V18_EXACT', 'v18_descriptor', 'v18_role', 'v18_report', 'v18_scope'}
    def name(n):
        if isinstance(n, ast.FunctionDef): return n.name
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name): return n.targets[0].id
    removed = [n for n in new.body if name(n) in names]
    need(len(removed) == 6 and [dump(n) for n in removed] == [dump(n) for n in additions.body], 'AST_SIX_LITERAL_NODES')
    new.body = [n for n in new.body if name(n) not in names]
    old_main = next(n for n in old.body if isinstance(n, ast.FunctionDef) and n.name == 'main')
    new_main = next(n for n in new.body if isinstance(n, ast.FunctionDef) and n.name == 'main')
    guard = next(n for n in ast.walk(old_main) if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)
                 and len(n.value.args) > 1 and isinstance(n.value.args[1], ast.Constant)
                 and n.value.args[1].value == 'separate checking identity for the exact recorded discovery')
    extended = copy.deepcopy(guard)
    extended.value.args[0].values[-1].values.append(ast.Name(id='exact_v18', ctx=ast.Load()))
    fragments = {
        'role': 'exact_v18 = v18_role(cid, expected, binding)',
        'report': 'wave43_statement_mapping = v18_report(cid, report_sha, binding, report)',
        'dispatcher': "if wave43_statement_mapping is not None:\n need(editorial_statement_mapping is None, 'v18 disjoint exact written metadata adapter')\n editorial_statement_mapping = wave43_statement_mapping",
        'scope': "if cid in V18_EXACT:\n original_scope = copy.deepcopy(binding['scope'])\n projected_scope = v18_scope(cid, expected, binding)\n binding = copy.deepcopy(binding)\n binding['scope'] = projected_scope"}
    expected = {dump(ast.parse(v).body[0]): k for k, v in fragments.items()}; found = []
    class Restore(ast.NodeTransformer):
        def visit(self, n):
            key = dump(n)
            if key in expected: found.append(expected[key]); return None
            if key == dump(extended): found.append('role_alternative'); return copy.deepcopy(guard)
            return super().visit(n)
    Restore().visit(new_main)
    need(sorted(found) == ['dispatcher', 'report', 'role', 'role_alternative', 'scope'], 'AST_FIVE_EXACT_GROUPS')
    need(dump(old) == dump(new), 'AST_COMPLETE_V17_RESTORED')
    return dict(complete_V17_AST_restored=True, removed_nodes=sorted(names), removed_groups=sorted(found))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seconds', type=float, required=True); ap.add_argument('--out', type=Path, required=True)
    for key in ('author', 'terminal', 'controls', 'mappings'):
        ap.add_argument('--' + key, required=True); ap.add_argument('--' + key + '-sha256', required=True)
    for key in ('self-sha256', 'spec-sha256', 'expected-head', 'protected-ledger-sha256', 'protected-index-sha256', 'ordinary-pins', 'ordinary-pins-sha256'):
        ap.add_argument('--' + key, required=True)
    a = ap.parse_args(); d = CommandDeadline(a.seconds, allocation_reason='Independent V18 exact metadata and protected copies;20save; no mathematics')
    out = a.out.resolve(); need(out.is_relative_to(ROOT) and not out.exists(), 'FRESH_OUTPUT'); out.mkdir(parents=True)
    before = (ROOT / 'CLAIMS.yaml').read_bytes(); pins = {}; controls = []; barriers = []
    def reserve(): need(not d.status()['stop_required'] and d.status()['remaining_seconds'] > 20, 'SAVE_RESERVE')
    def pin(path, wanted):
        reserve(); p = (ROOT / path).resolve(); need(p.is_relative_to(ROOT) and p.is_file(), 'INPUT_PATH')
        h = sha(p); need(h == wanted and (path not in pins or pins[path] == h), 'INPUT_HASH:' + path); pins[path] = h
    def reject(label, stage, call):
        try: call()
        except Exception as error:
            need(type(error) is ValueError and str(error) == stage, 'PRECISE_REJECTION:' + label)
            controls.append(dict(label=label, expected_diagnostic=stage, actual_diagnostic=str(error), outcome='REJECTED')); return
        raise GateError('ACCEPTED_CORRUPTION:' + label)
    def subject(label, path):
        spec = importlib.util.spec_from_file_location(label, ROOT / path); value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value); return value
    try:
        need(hashlib.sha256(before).hexdigest() == a.protected_ledger_sha256 and sha(ROOT / '.git/index') == a.protected_index_sha256
             and subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() == a.expected_head, 'PROTECTED_BASELINE')
        pin(Path(__file__).relative_to(ROOT).as_posix(), a.self_sha256)
        pin(Path(__file__).with_name(Path(__file__).stem + '_spec.md').relative_to(ROOT).as_posix(), a.spec_sha256)
        for k, h in PINS.items(): pin(k, h)
        for key in ('author', 'terminal', 'controls', 'mappings', 'ordinary_pins'): pin(getattr(a, key), getattr(a, key + '_sha256'))
        author, terminal, raw, mappings = [json.loads((ROOT / getattr(a, key)).read_bytes()) for key in ('author', 'terminal', 'controls', 'mappings')]
        need(author['status'] == 'V18_AUTHOR_HELPER_CONTROLS_PASS_PENDING_INDEPENDENT_ENGINEERING_REVIEW'
             and equal([author[k] for k in ('positive_controls', 'strict_negative_controls', 'harness_negative_controls', 'registrar_main_called', 'independent_approval')], [36, 432, 2, False, False]), 'AUTHOR_SCOPE')
        need(type(terminal['command_exit_code']) is int and terminal['command_exit_code'] == 0 and terminal['error'] is None
             and terminal['deadline_reached'] is False and terminal['cleanup']['reaped'] is True
             and terminal['cleanup']['job_active_zero_observed'] is True and terminal['cleanup']['cleanup_errors'] == [], 'AUTHOR_TERMINAL')
        for k, h in author['inputs_sha256'].items(): pin(k, h)
        need(len(raw['positive']) == 36 and len(raw['strict_negative']) == 432
             and len({x['label'] for x in raw['strict_negative']}) == 432
             and all(x['expected_diagnostic'] == x['actual_diagnostic'] and x['outcome'] == 'REJECTED' for x in raw['strict_negative'])
             and raw['harness_wrong_stage_and_type_rejected'] == 2, 'AUTHOR_RAW')
        texts = [(ROOT / k).read_text(encoding='utf8') for k in (OLD, NEW, ADDITIONS)]
        restored = ast_restore(*texts); old = subject('root_v18_old', OLD); new = subject('root_v18_new', NEW)
        rows = json.loads((ROOT / DESCRIPTOR).read_bytes())['adapters']; loaded = []; own_maps = []
        need(list(new.V18_EXACT) == [r['id'] for r in rows] and len(rows) == 8, 'EIGHT_ROUTED_IDS')
        for row in rows:
            p, h = row['binding']['path'], row['binding']['sha256']; pin(p, h)
            b = json.loads((ROOT / p).read_bytes()); pin(b['report'], b['report_sha256']); r = json.loads((ROOT / b['report']).read_bytes())
            for k, v in b['inputs_sha256'].items(): pin(k, v)
            need(all(equal(b[k], v) for k, v in row['binding_contract'].items()) and all(equal(r[k], v) for k, v in row['report_contract'].items()), 'FULL_DESCRIPTOR_CONTRACT')
            need(b['producer'] != b['verifier'] and b['verifier'] == '/root' and new.v18_role(b['id'], h, b) is True, 'DISTINCT_EXACT_ROLE')
            mapping = new.v18_report(b['id'], b['report_sha256'], b, r); own_maps.append(mapping)
            need(equal(mapping['original_report_scope'], r['scope']) and equal(mapping['original_binding_scope'], b['scope'])
                 and equal(mapping['schema_scope'], row['schema_scope']) and mapping['raw_statement_changed'] is False
                 and mapping['mathematical_replays'] == 0 and equal(new.v18_scope(b['id'], h, b), row['schema_scope']), 'ORIGINAL_SCOPES')
            for k, v, stage in [('revision', True, 'v18 exact typed revision status roles method kind basis'),
                                ('verifier', b['producer'], 'v18 exact typed revision status roles method kind basis'),
                                ('dependencies', b['dependencies'] + [dict(id='C-FICTION', revision=1, relation='premise')], 'v18 exact original scope dependencies and nonresolution'),
                                ('statement', b['statement'] + ' Therefore no target.', 'v18 exact literal statement report proof controls and no legacy fallback'),
                                ('limitations', [], 'v18 complete literal binding metadata')]:
                bad = copy.deepcopy(b); bad[k] = v
                reject(b['id'] + ':binding:' + k, stage, lambda bad=bad: new.v18_role(b['id'], h, bad))
            for k, v, stage in [('claim_revision', True, 'v18 exact typed independent report identity and method'),
                                ('statement', r['statement'] + ' Therefore no target.', 'v18 exact written statement original scope assumptions dependencies'),
                                ('command', [], 'v18 exact written command null and reason')]:
                bad = copy.deepcopy(r); bad[k] = v
                reject(b['id'] + ':report:' + k, stage, lambda bad=bad: new.v18_report(b['id'], b['report_sha256'], b, bad))
            loaded.append((p, h, b, row['schema_scope']))
        need(equal(own_maps, mappings), 'ALL_EIGHT_AUTHOR_MAPPINGS_RECONSTRUCTED')
        need(len(controls) == 64 and new.v18_role('C-UNRELATED', '0'*64, {}) is False and new.v18_report('C-UNRELATED', '0'*64, {}, {}) is None, '64_PREDECLARED_VETOES')
        ordinary_map = json.loads((ROOT / a.ordinary_pins).read_bytes()); ordinary = []
        for stem, expected in ORDINARY:
            p = 'acceleration/results/20261003_independent_review/' + stem + '/claim_binding_schema2.json'; h = ordinary_map[p]; pin(p, h)
            b = json.loads((ROOT / p).read_bytes()); pin(b['report'], b['report_sha256'])
            for k, v in b['inputs_sha256'].items(): pin(k, v)
            need(h == expected and new.v18_role(b['id'], h, b) is False and b['producer'] != b['verifier'], 'FIVE_UNCHANGED_ORDINARY_ROUTES')
            ordinary.append((p, h, b, b['scope']))
        def dry(value, label, batch):
            reserve(); dest = out / label; prior_argv, prior_replace = sys.argv, os.replace
            def barrier(source, target):
                need(Path(target).resolve() == ROOT / 'CLAIMS.yaml' and Path(source).resolve() == dest / 'CLAIMS.pending.yaml'
                     and (ROOT / 'CLAIMS.yaml').read_bytes() == before, 'INTERCEPTED_PROTECTED_WRITE')
                write(dest / 'protected_report.json', copy.deepcopy(sys._getframe(1).f_locals['report'])); barriers.append(label); raise ProtectedWrite()
            try:
                os.replace = barrier; sys.argv = [str(ROOT / NEW), '--out', str(dest), '--previous-sha256', a.protected_ledger_sha256]
                for p, h, b, scope in batch: sys.argv += ['--binding', str(ROOT / p), '--binding-sha256', h]
                try: value.main()
                except ProtectedWrite: pass
                else: raise GateError('NO_WRITE_INTERCEPTION')
            finally: os.replace, sys.argv = prior_replace, prior_argv
            need((ROOT / 'CLAIMS.yaml').read_bytes() == before, 'LIVE_LEDGER_UNCHANGED')
            return yaml.safe_load((dest / 'CLAIMS.after.yaml').read_text(encoding='utf8'))
        left, right = dry(old, 'ordinary_V17', ordinary[:1]), dry(new, 'ordinary_V18', ordinary[:1])
        for v in (left, right): v.pop('updated_at'); v['claims'][-1]['created_at'] = v['claims'][-1]['updated_at'] = None
        need(equal(left, right), 'ORDINARY_PROJECTION_IDENTICAL')
        batch = loaded + ordinary; after = dry(new, 'thirteen_V18', batch); base = yaml.safe_load(before)
        need(len(base['claims']) == 371 and len(after['claims']) == 384, 'EXACT_371_TO_384')
        need(equal(after['claims'][:371], base['claims']) and equal(after['artifacts'][:len(base['artifacts'])], base['artifacts'])
             and equal(after['target'], base['target']), 'PRIOR_TYPED_CONTENT_PRESERVED')
        for claim, (p, h, b, scope) in zip(after['claims'][371:], batch):
            need(all(equal(claim[k], b[k]) for k in ('id', 'revision', 'statement', 'kind', 'basis', 'status', 'review_state', 'assumptions', 'limitations'))
                 and equal(claim['scope'], scope), 'EXACT_NEW_CLAIM')
            projected_dependencies = [{k: dep[k] for k in ('id', 'revision', 'relation')} for dep in b['dependencies']]
            dependency_notes = [dict(id=dep['id'], revision=dep['revision'], reason=dep['reason']) for dep in b['dependencies'] if 'reason' in dep]
            need(equal(claim['dependencies'], projected_dependencies) and equal(json.loads(claim['unknowns']['dependency_notes']), dependency_notes), 'EXACT_DEPENDENCIES_AND_PRESERVED_REASONS')
            v = claim['verification'][0]
            need(v['verifier'] == b['verifier'] and v['method'] == b['method'] and type(v['claim_revision']) is int
                 and v['claim_revision'] == 1 and v['command_or_audit'] == b['report'], 'VERIFICATION_LITERAL')
        report = json.loads((out / 'thirteen_V18/protected_report.json').read_bytes())
        need(equal(report['editorial_statement_mappings'], own_maps) and report['claim_records'] == 384, 'EIGHT_COPIED_MAPPINGS')
        counts = Counter(c['status'] for c in base['claims']); counts['VERIFIED'] += 13
        need(Counter(c['status'] for c in after['claims']) == counts, 'STATUS_COUNTS')
        write(out / 'controls.json', controls); write(out / 'mappings.json', own_maps)
        write(out / 'summary.json', dict(status='INDEPENDENT_REGISTRAR_V18_ENGINEERING_V2_PASS', timestamp=datetime.now(timezone.utc).isoformat(),
              producer='/root/checkpoint_audit', verifier='/root', method='independent_engineering_artifact_check', source_commit=a.expected_head,
              inputs_sha256=pins, command=[sys.executable, *sys.argv], cwd=str(ROOT), python=platform.python_version(), AST_restoration=restored,
              author_subject_negatives=432, own_precise_negatives=64, protected_write_barriers=barriers, claims_before=371, claims_after=384,
              new_claim_ids=[b['id'] for p, h, b, scope in batch], status_counts=dict(counts), mathematical_replays=0, ledger_mutated=False,
              index_mutated=False, target_resolution='UNKNOWN', deadline=d.status(),
              shared_components=['V17/V18 are imported engineering subjects; independent ROOT AST subtraction, typed comparisons and protected write barrier.',
                                 'Python JSON/SHA/AST, YAML/schema, inherited registrar evidence and deadline helpers are trusted common components.'],
              limitations=['Finite metadata checks only; no mathematical reapproval, target resolution, public replay or live registration.',
                           '64 precise in-memory vetoes plus432saved author vetoes do not exhaust filesystem failures.',
                           'Frozen13claim copy only; additional bindings or changed baseline require separate exact transition review.']))
    except BaseException as error:
        write(out / 'failure.json', dict(error=repr(error), inputs_sha256=pins, controls=controls, deadline=d.status())); raise
    finally:
        need((ROOT / 'CLAIMS.yaml').read_bytes() == before and sha(ROOT / '.git/index') == a.protected_index_sha256, 'LIVE_LEDGER_INDEX_PRESERVED')


if __name__ == '__main__': main()
