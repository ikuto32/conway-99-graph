"""Isolated synthetic controls only; never allocate a real campaign population."""
from pathlib import Path,PurePosixPath
from types import SimpleNamespace
import ast,copy,hashlib,json
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'acceleration/select_20260930_exact_eight_prefix64.py';SPEC=SOURCE.with_name(SOURCE.stem+'_spec.md')
PINS={SOURCE:'16807bb5e5a9bcdb4fbadaa5b0f0ee69e360df46ac60664c0980540e0a891ce8',SPEC:'fe04ab0a06577496ae024ec4102e0c6cc869e4bff58f0b3878b3375f3d7ddc27'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for p,h in PINS.items():assert sha(p)==h
tree=ast.parse(SOURCE.read_text(encoding='utf8'))
env={'hashlib':hashlib,'copy':copy,'path':lambda p:PurePosixPath(p),'key':str}
functions={'need','count_bytes','literal_proof_row','proof_skips','first64','selection_for','partition_for'}
constants={'MANIFEST','MANIFEST_SHA','PROOF_STATUSES','ENCODING_STATUSES'}
nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in functions or isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in constants for t in n.targets)]
assert {n.name for n in nodes if isinstance(n,ast.FunctionDef)}==functions
exec(compile(ast.Module(nodes,[]),str(SOURCE),'exec'),env)
good=[];bad=[]
def rejected(label,f):
    try:f()
    except(ValueError,KeyError):bad.append(label)
    else:raise AssertionError('accepted synthetic corruption '+label)
universe=['fixture_case_'+str(i)for i in range(792)]
for k in [0,1,12,32,60,124,500,728]:
    skipped=universe[:k];want=universe[k:k+64]
    assert env['first64'](universe,skipped)==want==env['first64'](universe,list(reversed(skipped)))
    good.append('exact64 synthetic prefix with '+str(k)+' prior literals')
for label,u,d in [('duplicate_universe',universe+[universe[0]],[]),('duplicate_skip',universe,[universe[0],universe[0]]),('unknown_skip',universe,['absent']),('fewer64',universe,universe[:729]),('empty_remaining',universe,universe),('string_universe','not-a-list',[]),('bool_id',universe+[True],[])]:rejected(label,lambda u=u,d=d:env['first64'](u,d))
rows=[dict(case_id=c)for c in universe];authority=dict(path='fixture/plan.md',sha256='a'*64);refs=[dict(path='fixture/proofs.json',sha256='b'*64,completed_cases=124)]
parent=env['selection_for'](rows,universe[:124],refs,'Synthetic control only',authority);pr=dict(path='fixture/selection.json',sha256='c'*64)
parts=[env['partition_for'](parent,pr,i)for i in range(4)]
assert [cid for p in parts for cid in p['ordered_case_ids']]==universe[124:188]
assert len({cid for p in parts for cid in p['ordered_case_ids']})==64
for i,p in enumerate(parts):
    changed={k for k in set(parent)|set(p)if parent.get(k)!=p.get(k)}
    assert changed=={'selection_policy','ordered_case_ids','selection_reason','selected_instances','parent_selection_path','parent_selection_sha256','partition_index','partition_offset'}
    assert p['partition_index']==i and p['partition_offset']==16*i and len(p['ordered_case_ids'])==16
good.append('four exact contiguous disjoint16 partitions with no extra schema fields')
for i in [-1,4,True]:rejected('invalid_partition_'+str(i),lambda i=i:env['partition_for'](parent,pr,i))
counts=[[[1,1,1]for g in range(20)]for a in range(12)];digest=hashlib.sha256(env['count_bytes'](counts)).hexdigest();cid='exact_eight_'+digest
original=dict(case_id=cid,case_index=0,full_count_profile_sha256=digest,raw_representative=dict(counts=counts))
encoded=dict(case_id=cid,case_index=0,full_count_profile_sha256=digest,profile_path='fixture/profile.json',profile_sha256='d'*64,cnf_path='fixture/instance.cnf',cnf_sha256='e'*64,scope_path='fixture/scope.json',scope_sha256='f'*64)
row=dict(case_id=cid,case_index=0,full_count_profile_sha256=digest,outcome='UNSAT_VERIFIED',cnf_path=encoded['cnf_path'],cnf_sha256=encoded['cnf_sha256'],scope_path=encoded['scope_path'],scope_sha256=encoded['scope_sha256'],trace=dict(path='fixture/proof.drat',sha256='1'*64,bytes=17,complete_proof=True),replay=dict(accepted=True,expected_acceptance=True,actual_exit_code=0,cnf_sha256='e'*64,proof_sha256='1'*64))
raw=dict(coordinate_group_fibre_counts=counts);env['literal_proof_row'](row,encoded,original,raw);good.append('complete synthetic literal raw-count/replay identity')
for label,mut in [('unknown_outcome',lambda r:r.update(outcome='UNKNOWN')),('unchecked_unsat',lambda r:r.update(outcome='UNSAT')),('wrong_index',lambda r:r.update(case_index=1)),('wrong_count_hash',lambda r:r.update(full_count_profile_sha256='0'*64)),('wrong_cnf',lambda r:r.update(cnf_sha256='0'*64)),('wrong_scope',lambda r:r.update(scope_path='fixture/other.json')),('partial_trace',lambda r:r['trace'].update(complete_proof=False)),('replay_nonzero',lambda r:r['replay'].update(actual_exit_code=1)),('replay_bool_zero',lambda r:r['replay'].update(actual_exit_code=False)),('not_accepted',lambda r:r['replay'].update(accepted=False)),('unexpected_acceptance',lambda r:r['replay'].update(expected_acceptance=False)),('wrong_replay_cnf',lambda r:r['replay'].update(cnf_sha256='0'*64)),('wrong_replay_trace',lambda r:r['replay'].update(proof_sha256='0'*64))]:
    changed=copy.deepcopy(row);mut(changed);rejected(label,lambda r=changed:env['literal_proof_row'](r,encoded,original,raw))
different=copy.deepcopy(raw);different['coordinate_group_fibre_counts'][0][0]=[0,1,2]
rejected('different_literal_counts',lambda:env['literal_proof_row'](row,encoded,original,different))
for label,mut in [('short_coordinate',lambda x:x.pop()),('short_group',lambda x:x[0].pop()),('short_fibre',lambda x:x[0][0].pop()),('bool_count',lambda x:x[0][0].__setitem__(0,True)),('out_of_range_count',lambda x:x[0][0].__setitem__(0,4))]:
    changed=copy.deepcopy(counts);mut(changed);rejected(label,lambda x=changed:env['count_bytes'](x))

class FakeStore:
    """In-memory schema fixture, explicitly no real SHA/filesystem authentication."""
    def __init__(self,objects):self.objects=objects
    def load(self,name,expected=None):return copy.deepcopy(self.objects[name])
    def maps(self,obj):assert type(obj['inputs_sha256'])is dict and type(obj['outputs_sha256'])is dict
    def pin(self,name,expected=None):return SimpleNamespace(stat=lambda:SimpleNamespace(st_size=17))

def gate_fixture(status):
    gate=dict(status=status,completed_proof_replays=1,UNKNOWN=0,pending_case_ids=[],selected_case_ids=[cid],case_records=[copy.deepcopy(row)],inputs_sha256={'fixture/encoding/summary.json':'2'*64},outputs_sha256={'fixture/claim_binding.json':'3'*64})
    gate[env['PROOF_STATUSES'][status]]=0
    objects={'fixture/summary.json':gate,'fixture/claim_binding.json':dict(revision=1,status='VERIFIED'),'fixture/encoding/summary.json':dict(status='INDEPENDENT_EXACT_EIGHT_EXPLICIT_BATCH_ENCODING_PASS',checked_cases=[copy.deepcopy(encoded)]),'fixture/profile.json':copy.deepcopy(raw)}
    return objects
gate_ref=dict(path='fixture/summary.json',sha256='4'*64,completed_cases=1)
for status in env['PROOF_STATUSES']:
    done,norm,review=env['proof_skips'](FakeStore(gate_fixture(status)),[gate_ref],{cid:original})
    assert done==[cid]and norm==[gate_ref]and len(review)==1;good.append('synthetic proof status schema '+status)
objects=gate_fixture('INDEPENDENT_EXACT_EIGHT_EXPLICIT_BATCH_LITERAL_PROOFS_PASS')
for label,mut in [('pending_literal',lambda x:x['fixture/summary.json'].update(pending_case_ids=['other'])),('unknown_literal',lambda x:x['fixture/summary.json'].update(UNKNOWN=1)),('sat_literal',lambda x:x['fixture/summary.json'].update(SAT_verified=1)),('zero_proofs',lambda x:x['fixture/summary.json'].update(completed_proof_replays=0)),('bool_count',lambda x:x['fixture/summary.json'].update(completed_proof_replays=True)),('unrecognized_status',lambda x:x['fixture/summary.json'].update(status='PRODUCER_UNSAT')),('unapproved_binding',lambda x:x['fixture/claim_binding.json'].update(status='CANDIDATE')),('no_case_row',lambda x:x['fixture/summary.json'].update(case_records=[])),('wrong_selected_id',lambda x:x['fixture/summary.json'].update(selected_case_ids=['other'])),('ambiguous_encoding',lambda x:x['fixture/encoding/summary.json']['checked_cases'].append(copy.deepcopy(encoded)))]:
    changed=copy.deepcopy(objects);mut(changed);rejected(label,lambda x=changed:env['proof_skips'](FakeStore(x),[gate_ref],{cid:original}))
rejected('duplicate_gate_path',lambda:env['proof_skips'](FakeStore(objects),[gate_ref,gate_ref],{cid:original}))
objects2=copy.deepcopy(objects);objects2['fixture2/summary.json']=copy.deepcopy(objects['fixture/summary.json']);objects2['fixture2/summary.json']['outputs_sha256']={'fixture2/claim_binding.json':'3'*64};objects2['fixture2/claim_binding.json']=copy.deepcopy(objects['fixture/claim_binding.json'])
rejected('duplicate_literal_across_gates',lambda:env['proof_skips'](FakeStore(objects2),[gate_ref,dict(path='fixture2/summary.json',sha256='5'*64)],{cid:original}))
rejected('wrong_declared_gate_count',lambda:env['proof_skips'](FakeStore(objects),[dict(gate_ref,completed_cases=2)],{cid:original}))
out=ROOT/'acceleration/results/20260930_exact_eight_prefix64_source_preparation';out.mkdir(exist_ok=False)
record=dict(status='CANDIDATE_EXACT_EIGHT_PREFIX64_SOURCE_CONTROLS_PASS',inputs_sha256={p.relative_to(ROOT).as_posix():sha(p)for p in [SOURCE,SPEC,Path(__file__)]},source_ast_checked=True,positive_controls=good,corruptions_rejected=bad,synthetic_only=True,real_proof_gates_read=0,real_selections_created=0,consolidations_executed=0,actual_filesystem_hash_contract_tested=False,actual_build_receipts_tested=False,producer_calls=0,native_calls=0,git_commands=0,independent_approval=False,limitations=['Pure functions were extracted by AST; main/select/consolidate/Store and real filesystem authentication were not executed.','In-memory proof fixtures calibrate schema and literal identity refusal only.','Future actual requests still require root authorization and independent full v3 encoding/object review.'])
with(out/'summary.json').open('x',encoding='utf8',newline='\n')as f:json.dump(record,f,indent=2);f.write('\n')
print(json.dumps(dict(summary=out.relative_to(ROOT).as_posix()+'/summary.json',sha256=sha(out/'summary.json'),positive_controls=len(good),corruptions_rejected=len(bad),real_selections_created=0)))
