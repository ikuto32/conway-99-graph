"""Author metadata controls only; never invoke registrar main or scientific code."""
import argparse, ast, copy, hashlib, importlib.util, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
OLD = 'acceleration/register_20261003_bound_claims_v20.py'
NEW = 'acceleration/register_20261004_bound_claims_v23.py'
SPEC = 'acceleration/calibrate_20261004_registrar_v23_helpers_v2_spec.md'
DESCRIPTOR = 'acceleration/proposal_20261004_wave45_eighteen_bound_claims_v3.json'
PINS = {
    OLD: '58f4fd6fe5c69296a55cddf00e4a0185c21a13ef3d97c173984f030038d4f78b',
    NEW: 'fb7c9ce93c15713086d4149f15afac6e8c6c4fec978dba180012b6664a0c434d',
    DESCRIPTOR: 'd80ebf22f6d0a9eea28b249568081bc9d1a16df3306aebbf5d2c4bcb268a6411',
    'acceleration/register_20261004_bound_claims_v23_spec.md': '36373eda9b64cdb7cfd51629215e1eb847007fc3370bc320ecfc0cf4d9c54630',
    'acceleration/register_20261004_bound_claims_v23_additions_v1.py.txt': '3817d874d1c18cc3087628e7726540485d5081eebb6c5a3a7f86f7b71cd9a818',
    'acceleration/register_20261004_bound_claims_v23_diff.txt': '616581e437262c69e3f146f3de2416da26d3f0083d6fa6734e7111961066886b',
    'acceleration/validate_claims.py': 'a48f55b54918b0c494e6f06f80bdcdc52f304dfc370dd25842aeae3a0f861265',
    'docs/claims.schema.json': '0d752f62c7c9a43c7ddc5fbfe8d2c5644eec3d70d1baea236cb290d475aa5dac',
    'acceleration/command_deadline.py': '9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9',
    'acceleration/run_compute_command_v2.py': '46410201dcad20eb056b8206a1b6687f9ac74f0f34e3cc66197eff5c59d55e17',
    'acceleration/run_compute_command.py': '593a9feed6250739dc9672338df23ab171fc9a6a6db4196c1feb312efa33957a',
    'pyproject.toml': '273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339',
    'uv.lock': 'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',
}

class ControlError(ValueError): pass
def need(ok, stage):
    if not ok: raise ControlError(stage)
def dump(node): return ast.dump(node, include_attributes=False)
def changed(value, key, replacement):
    result = copy.deepcopy(value); result[key] = replacement; return result

def restore_v20_ast(old_source, new_source):
    old = ast.parse(old_source); new = ast.parse(new_source)
    functions = {'v23_descriptor', 'v23_role', 'v23_verification_outcome',
                 'v23_scope', 'v23_dependencies', 'v23_evidence', 'v23_report'}
    constants = {'V23_REFUTED_ID', 'V23_DESCRIPTOR', 'V23_CAPACITY_METADATA',
                 'V23_SEVENTEEN_METADATA', 'V23_EXACT'}
    kept = []; removed = []
    for node in new.body:
        if isinstance(node, ast.FunctionDef) and node.name in functions:
            removed.append(node.name)
        elif isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and node.targets[0].id in constants:
            removed.append(node.targets[0].id)
        else: kept.append(node)
    need(len(removed) == 12 and set(removed) == functions | constants,
         'twelve exact V23 top-level nodes'); new.body = kept
    oldmain = next(n for n in old.body if isinstance(n, ast.FunctionDef) and n.name == 'main')
    newmain = next(n for n in new.body if isinstance(n, ast.FunctionDef) and n.name == 'main')
    def guard_in(tree, label):
        return next(n for n in ast.walk(tree) if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)
                    and len(n.value.args) > 1 and isinstance(n.value.args[1], ast.Constant) and n.value.args[1].value == label)
    old_role = guard_in(oldmain, 'separate checking identity for the exact recorded discovery')
    new_role = copy.deepcopy(old_role)
    new_role.value.args[0].values[-1].values.append(ast.Name(id='exact_v23', ctx=ast.Load()))
    old_status = guard_in(oldmain, 'independent exact-scope checking status')
    new_status = copy.deepcopy(old_status)
    new_status.value.args[0].values[0].values.append(ast.Name(id='exact_v23_refuted', ctx=ast.Load()))
    assignments = {
        'exact_v23': 'exact_v23 = v23_role(cid, expected, binding)',
        'exact_v23_refuted': 'exact_v23_refuted = exact_v23 and cid == V23_REFUTED_ID',
        'verification_outcome': "verification_outcome = v23_verification_outcome(cid, expected, binding) if exact_v23 else 'PASS'",
        'wave45_statement_mapping': 'wave45_statement_mapping = v23_report(cid, report_sha, binding, report)',
    }
    dispatcher = ast.parse("if wave45_statement_mapping is not None:\n need(editorial_statement_mapping is None, 'v23 disjoint exact eighteen metadata adapter')\n editorial_statement_mapping = wave45_statement_mapping").body[0]
    projection = ast.parse("if cid in V23_EXACT:\n original_scope = copy.deepcopy(binding['scope'])\n projected_scope = v23_scope(cid, expected, binding)\n projected_dependencies = v23_dependencies(cid, expected, binding, data['claims'])\n editorial_statement_mapping['schema_dependencies'] = copy.deepcopy(projected_dependencies)\n binding = copy.deepcopy(binding)\n binding['scope'] = projected_scope\n binding['dependencies'] = projected_dependencies").body[0]
    evidence = ast.parse("if cid in V23_EXACT:\n for evidence_path, evidence_sha in v23_evidence(cid).items():\n  need(evidence_path not in paths or paths[evidence_path] == evidence_sha, 'v23 consistent exact metadata evidence')\n  paths[evidence_path] = evidence_sha").body[0]
    old_verification = next(n for n in ast.walk(oldmain) if isinstance(n, ast.Assign)
                            and any(isinstance(t, ast.Name) and t.id == 'verification' for t in n.targets))
    expected_verification = copy.deepcopy(old_verification)
    next(k for k in expected_verification.value.keywords if k.arg == 'outcome').value = ast.Name(id='verification_outcome', ctx=ast.Load())
    edits = []
    class Restore(ast.NodeTransformer):
        def visit_Assign(self, node):
            names = {t.id for t in node.targets if isinstance(t, ast.Name)}
            for name, text in assignments.items():
                if name in names:
                    need(dump(node) == dump(ast.parse(text).body[0]), 'exact V23 assignment '+name)
                    edits.append(name); return None
            if 'verification' in names:
                need(dump(node) == dump(expected_verification), 'exact V23 theorem outcome keyword')
                edits.append('outcome_keyword'); return copy.deepcopy(old_verification)
            return self.generic_visit(node)
        def visit_If(self, node):
            if ast.unparse(node.test) == 'wave45_statement_mapping is not None':
                need(dump(node) == dump(dispatcher), 'exact V23 dispatcher'); edits.append('dispatcher'); return None
            if ast.unparse(node.test) == 'cid in V23_EXACT':
                label = 'scope_dependencies' if dump(node) == dump(projection) else 'metadata_evidence'
                need(dump(node) == dump(projection) or dump(node) == dump(evidence), 'exact V23 projection or evidence')
                edits.append(label); return None
            return self.generic_visit(node)
        def visit_Expr(self, node):
            if isinstance(node.value, ast.Call) and len(node.value.args) > 1 and isinstance(node.value.args[1], ast.Constant):
                if node.value.args[1].value == 'separate checking identity for the exact recorded discovery':
                    need(dump(node) == dump(new_role), 'exact V23 role alternative'); edits.append('role_guard'); return copy.deepcopy(old_role)
                if node.value.args[1].value == 'independent exact-scope checking status':
                    need(dump(node) == dump(new_status), 'exact V23 refuted-only status alternative'); edits.append('status_guard'); return copy.deepcopy(old_status)
            return self.generic_visit(node)
    Restore().visit(newmain)
    need(len(edits) == 10 and set(edits) == set(assignments) | {'outcome_keyword', 'dispatcher', 'scope_dependencies', 'metadata_evidence', 'role_guard', 'status_guard'},
         'ten exact V23 main insertion groups')
    need(dump(old) == dump(new), 'complete V20 AST restored')
    return dict(complete_V20_AST_restored=True, removed_top_level_nodes=removed, removed_main_groups=edits)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seconds', type=float, required=True); ap.add_argument('--out', required=True)
    for key in ('source-sha256', 'spec-sha256', 'protected-ledger-sha256', 'protected-index-sha256', 'expected-head'):
        ap.add_argument('--'+key, required=True)
    a = ap.parse_args(); deadline = CommandDeadline(a.seconds,
        allocation_reason='V23 exact eighteen metadata helpers; direct metadata/AST only,20 save reserve, no main')
    out = Path(a.out).resolve(); need(out.is_relative_to(ROOT) and not out.exists(), 'fresh output'); out.mkdir(parents=True)
    inputs = {}; positives = []; negatives = []; mappings = []; instructions = []
    before = (ROOT/'CLAIMS.yaml').read_bytes(); index_before = hashlib.sha256((ROOT/'.git/index').read_bytes()).hexdigest()
    def guard():
        status = deadline.status(); need(not status['stop_required'] and status['remaining_seconds'] > 20, 'SAVE_RESERVE')
    def sha(path):
        h = hashlib.sha256()
        with path.open('rb') as f:
            while block := f.read(1024**2): guard(); h.update(block)
        guard(); return h.hexdigest()
    def pin(path, identity):
        guard(); q = (ROOT/path).resolve()
        need(q.is_relative_to(ROOT) and not q.is_symlink() and q.is_file(), 'regular direct metadata input')
        need(sha(q) == identity, 'immutable direct input '+path)
        need(path not in inputs or inputs[path] == identity, 'consistent direct pin'); inputs[path] = identity
    def save(name, value):
        guard()
        with (out/name).open('x', encoding='utf8', newline='\n') as f:
            json.dump(value, f, indent=2, allow_nan=False); f.write('\n')
        guard()
    def protected():
        guard(); need((ROOT/'CLAIMS.yaml').read_bytes() == before and sha(ROOT/'.git/index') == index_before
             and subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() == a.expected_head,
             'protected HEAD ledger index unchanged'); guard()
    def positive(label, ok):
        guard(); need(ok, 'POSITIVE:'+label); positives.append(dict(label=label, outcome='PASS'))
    def reject(label, stage, callback, mutation=None):
        guard()
        try: callback()
        except Exception as e:
            if type(e) is not ValueError or str(e) != stage:
                raise ControlError('WRONG_STAGE:'+label+':'+type(e).__name__+':'+str(e)) from e
            negatives.append(dict(label=label, expected_stage=stage, actual_stage=str(e)))
            instructions.append(dict(label=label, operation=mutation, damaged_bytes_durable=False,
                 reason='Exact memory mutation is reproducible from this pinned control source and original direct metadata.'))
            return
        raise ControlError('CORRUPTION_ACCEPTED:'+label)
    try:
        need(hashlib.sha256(before).hexdigest() == a.protected_ledger_sha256
             and index_before == a.protected_index_sha256, 'protected input hashes'); protected()
        pin(Path(__file__).relative_to(ROOT).as_posix(), a.source_sha256); pin(SPEC, a.spec_sha256)
        for path, identity in PINS.items(): pin(path, identity)
        old_text = (ROOT/OLD).read_text(encoding='utf8'); new_text = (ROOT/NEW).read_text(encoding='utf8')
        ast_result = restore_v20_ast(old_text, new_text); positive('complete_V20_AST_restored', ast_result['complete_V20_AST_restored'])
        try: restore_v20_ast(old_text+'\npass\n', new_text)
        except ControlError as e:
            need(str(e) == 'complete V20 AST restored', 'AST corruption exact stage')
            negatives.append(dict(label='inherited_source_change', expected_stage=str(e), actual_stage=str(e)))
            instructions.append(dict(label='inherited_source_change', operation='append pass to old AST input', damaged_bytes_durable=False))
        else: raise ControlError('AST_CORRUPTION_ACCEPTED')
        descriptor = json.loads((ROOT/DESCRIPTOR).read_bytes()); records = descriptor['records']
        spec = importlib.util.spec_from_file_location('v23_author_metadata_subject', ROOT/NEW)
        subject = importlib.util.module_from_spec(spec); spec.loader.exec_module(subject); guard()
        ids = [r['id'] for r in records]; need(len(ids) == 18 and list(subject.V23_EXACT) == ids, 'exact eighteen-ID config')
        for path, identity in subject.v23_evidence(ids[0]).items(): pin(path, identity)
        present = [dict(id=e['dependency_id'], revision=1, status='VERIFIED', review_state='CLEAR')
                   for e in descriptor['proposed_dependency_topology']]
        present = list({c['id']:c for c in present}.values())
        bindings = {}; reports = {}
        for record in records:
            cid = record['id']; identity = record['binding']['sha256']; report_sha = record['bound_report']['declared_sha256']
            pin(record['binding']['path'], identity); pin(record['bound_report']['path'], report_sha)
            b = json.loads((ROOT/record['binding']['path']).read_bytes()); r = json.loads((ROOT/b['report']).read_bytes())
            bindings[cid] = b; reports[cid] = r
            positive(cid+':role', subject.v23_role(cid, identity, b) is True)
            mapping = subject.v23_report(cid, report_sha, b, r); mappings.append(mapping)
            positive(cid+':report', mapping['raw_statement_changed'] is False and mapping['generic_role_waiver'] is False
                     and subject.v15_same(mapping['original_dependencies'], b['dependencies']))
            positive(cid+':scope', subject.v15_same(subject.v23_scope(cid, identity, b), record['proposed_three_key_scope']))
            deps = subject.v23_dependencies(cid, identity, b, present)
            expected_deps = [dict(id=x['id'], revision=x['revision'], relation=x.get('relation', x.get('type')),
                                  **({'reason':x['reason']} if 'reason' in x else {})) for x in b['dependencies']]
            positive(cid+':dependencies', subject.v15_same(deps, expected_deps))
            positive(cid+':outcome', subject.v23_verification_outcome(cid, identity, b) == ('FAIL' if cid == subject.V23_REFUTED_ID else 'PASS'))
            reject(cid+':wrong_binding_hash', 'v23 exact frozen binding identity',
                   lambda cid=cid,b=b: subject.v23_role(cid, '0'*64, b), 'binding SHA -> zero')
            reject(cid+':wrong_report_hash', 'v23 exact original report bytes',
                   lambda cid=cid,b=b,r=r: subject.v23_report(cid, '0'*64, b, r), 'report SHA -> zero')
            for dep in b['dependencies']:
                bad = [c for c in present if c['id'] != dep['id']]
                reject(cid+':missing_dependency:'+dep['id'], 'v23 preceding exact verified dependency revision',
                       lambda cid=cid,b=b,identity=identity,bad=bad: subject.v23_dependencies(cid, identity, b, bad),
                       'remove exact preceding dependency '+dep['id'])
        for cid in ('C-SYNTHETIC-UNRELATED', 'C-TARGET-GRAM-PSD-AND-SUPPORT-NOGOODS'):
            positive(cid+':no_new_adapter', subject.v23_role(cid, '0'*64, {}) is False
                     and subject.v23_report(cid, '0'*64, {}, {}) is None
                     and subject.v23_verification_outcome(cid, '0'*64, {}) is None)
        positive('typed_equality_rejects_numeric_aliases', not subject.v15_same(True, 1) and not subject.v15_same(1, 1.0))
        for cid in (ids[0], ids[5], subject.V23_REFUTED_ID):
            b = bindings[cid]; identity = subject.V23_EXACT[cid][0]
            reject(cid+':bool_revision', 'v23 exact integer revision',
                   lambda cid=cid,b=b,identity=identity: subject.v23_role(cid, identity, changed(b, 'claim_revision', True)),
                   'claim_revision -> bool true')
        first = ids[0]; b = bindings[first]; identity, report_sha = subject.V23_EXACT[first]; r = reports[first]
        reject('binding_map_change', 'v23 complete original typed binding',
               lambda: subject.v23_role(first, identity, changed(b, 'inputs_sha256', {})), 'inputs_sha256 -> empty map')
        for cid in (first, subject.V23_REFUTED_ID):
            x = bindings[cid]; h = subject.V23_EXACT[cid][0]; status = 'VERIFIED' if x['status'] == 'REFUTED' else 'REFUTED'
            reject(cid+':status_swap', 'v23 literal binding core status',
                   lambda cid=cid,x=x,h=h,status=status: subject.v23_role(cid, h, changed(x, 'status', status)), 'swap theorem status')
        fields = [('id','C-UNRELATED','v23 literal binding core id'),
                  ('producer',b['verifier'],'v23 literal binding core producer'),
                  ('verifier','/root/unknown','v23 literal binding core verifier'),
                  ('method','UNKNOWN','v23 literal binding core method'),
                  ('kind','exclusion','v23 literal binding core kind'),
                  ('basis',[],'v23 literal binding core basis'),
                  ('statement','A broader statement.','v23 literal binding core statement'),
                  ('verification_timestamp','2000-01-01T00:00:00Z','v23 separate exact roles and timestamp'),
                  ('scope',{},'v23 original scope and dependencies'),
                  ('dependencies',[dict(id='C-UNRELATED')],'v23 original scope and dependencies')]
        for key, value, stage in fields:
            reject('binding_'+key, stage, lambda key=key,value=value: subject.v23_role(first, identity, changed(b, key, value)), 'replace '+key)
        refuted = subject.V23_REFUTED_ID; rb = bindings[refuted]; rr = reports[refuted]; rh, rreport = subject.V23_EXACT[refuted]
        qualified = 'C-FIXED-COUNT-NONTRIVIAL-LABELLED-SRG-CNF-COMPLETION-EQUIVALENCE'
        reject('refuted_statement_replaced_by_qualified', 'v23 literal binding core statement',
               lambda: subject.v23_role(refuted, rh, changed(rb, 'statement', bindings[qualified]['statement'])), 'original statement -> qualified statement')
        wrong_scope = copy.deepcopy(rb['scope']); wrong_scope['description'] += ' Conventional complete graphs included.'
        reject('refuted_convention_scope_change', 'v23 original scope and dependencies',
               lambda: subject.v23_role(refuted, rh, changed(rb, 'scope', wrong_scope)), 'change original recorded convention')
        for key, value in [('status','UNKNOWN'), ('statement','Broader.'), ('inputs_sha256',{})]:
            reject('report_'+key, 'v23 complete typed original report and literal statement',
                   lambda key=key,value=value: subject.v23_report(first, report_sha, b, changed(r,key,value)), 'replace report '+key)
        reject('extra_binding_field', 'v23 complete original typed binding',
               lambda: subject.v23_role(first, identity, changed(b,'unexpected',True)), 'extra field')
        missing = copy.deepcopy(b); del missing['scope']
        reject('missing_binding_scope', 'v23 required binding fields', lambda: subject.v23_role(first, identity, missing), 'remove scope')
        dependent = next(cid for cid in ids if bindings[cid]['dependencies']); db = bindings[dependent]; dh = subject.V23_EXACT[dependent][0]
        parent = db['dependencies'][0]['id']
        for label, key, value in [('bool_parent_revision','revision',True), ('float_parent_revision','revision',1.0),
                                  ('candidate_parent','status','CANDIDATE'), ('unchecked_parent','review_state','NEEDS_RECHECK'),
                                  ('refuted_parent','status','REFUTED')]:
            bad = [changed(c,key,value) if c['id'] == parent else copy.deepcopy(c) for c in present]
            reject(label, 'v23 preceding exact verified dependency revision',
                   lambda bad=bad: subject.v23_dependencies(dependent, dh, db, bad), 'parent '+key+' -> '+repr(value))
        duplicate = copy.deepcopy(present)+[copy.deepcopy(next(c for c in present if c['id'] == parent))]
        reject('duplicate_parent', 'v23 preceding exact verified dependency revision',
               lambda: subject.v23_dependencies(dependent, dh, db, duplicate), 'duplicate preceding exact ID')
        reject('refuted_theorem_outcome_PASS', 'v23 complete original typed binding',
               lambda: subject.v23_verification_outcome(refuted, rh, changed(rb,'verification_outcome','PASS')), 'FAIL -> PASS')
        bad_refutation = copy.deepcopy(rb['refutation']); bad_refutation['exact_statement_disproved'] = 1
        reject('refutation_boolean_alias', 'v23 complete original typed binding',
               lambda: subject.v23_verification_outcome(refuted, rh, changed(rb,'refutation',bad_refutation)), 'bool true -> integer1')
        bad_proof = copy.deepcopy(rb['refutation']); bad_proof['sha256'] = '0'*64
        reject('refutation_proof_identity', 'v23 complete original typed binding',
               lambda: subject.v23_verification_outcome(refuted, rh, changed(rb,'refutation',bad_proof)), 'proof SHA -> zero')
        reject('counterexample_audit_outcome_FAIL', 'v23 complete typed original report and literal statement',
               lambda: subject.v23_report(refuted, rreport, rb, changed(rr,'counterexample_audit_outcome','FAIL')), 'counterexample PASS -> FAIL')
        third = 'C-TARGET-DUAL-GRAM-EXTERIOR-TYPE-COMPATIBILITY'
        tb = bindings[third]; th = subject.V23_EXACT[third][0]
        positive('corrected_third_explicit_assumptions', len(tb['assumptions']) == 3
                 and subject.v23_role(third, th, tb) is True)
        absent_assumptions = copy.deepcopy(tb); del absent_assumptions['assumptions']
        reject('third_missing_assumptions', 'v23 required binding fields',
               lambda: subject.v23_role(third, th, absent_assumptions), 'remove corrected required assumptions key')
        for label, replacement in [('third_null_assumptions', None), ('third_boolean_assumptions', True),
                                   ('third_nonstring_assumption_member', [True])]:
            reject(label, 'v23 explicit assumption metadata',
                   lambda replacement=replacement: subject.v23_role(third, th, changed(tb, 'assumptions', replacement)),
                   'replace assumptions with '+repr(replacement))
        altered_assumptions = copy.deepcopy(tb['assumptions']); altered_assumptions[2] += ' Both must hold jointly.'
        reject('third_separate_PD_assumptions_changed', 'v23 complete original typed binding',
               lambda: subject.v23_role(third, th, changed(tb, 'assumptions', altered_assumptions)),
               'alter separate upper/lower positive-definite hypotheses')
        need(len(positives) == 95 and len(negatives) == 96 and len(mappings) == 18, 'declared95positive96negative18mappings')
        protected(); save('controls.json', dict(positive=positives, strict_negative=negatives))
        save('mappings.json', mappings); save('mutation_instructions.json', instructions); save('ast_restoration.json', ast_result)
        protected(); save('summary.json', dict(timestamp=datetime.now(timezone.utc).isoformat(),
            status='V23_AUTHOR_HELPER_CONTROLS_PASS_PENDING_INDEPENDENT_ENGINEERING_REVIEW',
            producer='/root/structural', verifier=None, verifier_null_reason='Author controls are not independent approval.',
            source_sha256=a.source_sha256, spec_sha256=a.spec_sha256, implementation_version=2, positive_controls=95, strict_negative_controls=96,
            metadata_mappings=18, VERIFIED_mappings=17, REFUTED_mappings=1, theorem_outcomes=dict(PASS=17, FAIL=1),
            exact_ids=ids, complete_V20_AST_restoration=ast_result, inputs_sha256=inputs,
            command=[sys.executable,*sys.argv], protected_HEAD=a.expected_head,
            protected_ledger_sha256=a.protected_ledger_sha256, protected_index_sha256=index_before,
            registrar_main_called=False, mathematical_replays=0, bulk_scientific_closure_rehashed=False,
            damaged_control_bytes_all_durable=False, damaged_control_limit='Memory mutations are source-reproducible; instructions and exact stages saved, not every mutated full JSON byte stream.',
            ledger_mutations=0, index_mutations=0, target_resolution='NONE', independent_approval=False,
            deadline=deadline.status())); guard(); protected()
    except BaseException as e:
        with (out/'failure.json').open('x',encoding='utf8',newline='\n') as f:
            json.dump(dict(timestamp=datetime.now(timezone.utc).isoformat(), error_type=type(e).__name__, message=str(e),
                positive_completed=len(positives), negative_completed=len(negatives),
                positive=positives, strict_negative=negatives, inputs_sha256=inputs, deadline=deadline.status()),f,indent=2,allow_nan=False);f.write('\n')
        raise
    finally:
        need((ROOT/'CLAIMS.yaml').read_bytes() == before and hashlib.sha256((ROOT/'.git/index').read_bytes()).hexdigest() == index_before
             and subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip() == a.expected_head,
             'protected state unchanged even on failure')

if __name__ == '__main__': main()
