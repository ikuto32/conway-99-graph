"""Read-only AST/text review; the registrar is never imported or executed."""
import ast, datetime, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE='acceleration/register_20261001_thirtieth_followup_claims.py'
SPEC='acceleration/register_20261001_thirtieth_followup_claims_spec.md'
OLD='acceleration/register_20261001_thirtieth_initial_claims.py'
I='acceleration/results/20261001_independent_review/'
PINS={SOURCE:'40a9cae1366798685c1cf3c9796a54ff0b36005213f4573709cf0639a1783354',
SPEC:'d597912552f4cc1d13f1e1172a4b6faebe5564ddbe1a0c56e154f98638d78077',
OLD:'8208ac246fff0d05cdcd7e5218a7927ac8b7502c117102e0757aa59d9268ab46',
'acceleration/results/20261001_thirtieth_initial_registration/CLAIMS.after.yaml':'0fd27c9fe019247eded6509f4c228141ce350e3cf387d98314742c89ecc1d56d',
I+'exact_eight_prefix64_batch04_cnfs_v4/summary.json':'71f88e1010a774bfd726a02e981facbf0b4b7ef8088af489d2dbfcfea877e8ea',
I+'exact_eight_prefix64_batch04_cnfs_v4/claim_binding.json':'f290505168b6b691aeaedc787cd8022b79322f40d25fdcd493a39b9965d020a2',
I+'reimbayev_z82/summary.json':'9f270d2792de23296d8348cf9911aaed7c24be12fc3535f0a3f0409e7cc35278',
I+'reimbayev_z82/claim_binding.json':'52ad25ef8c285db82a5ec329f3f28779e3bf7f35aaef8a8fa845b8e6caf0b5d3',
'docs/AUDIT_20261001_REIMBAYEV_Z82.md':'34257aea14c8b2fd21d8adef9aadfbfca925fa4bc8259053f714b0f708c9e60a'}
def need(q,m):
    if not q:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads((ROOT/p).read_text(encoding='utf8'))
def static_checks(text):
    tree=ast.parse(text)
    literals={n.targets[0].id:ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id in ('EXPECTED','REPORTS')}
    reports=literals['REPORTS'];expected=literals['EXPECTED']
    need(len(reports)==len(expected)==5 and list(reports)==list(expected),'five ordered IDs')
    for b,v in [(4,4),(5,3)]:
        key=f'C-FIXED-HADAMARD-EXACT-EIGHT-PREFIX64-BATCH{b:02d}-'
        need(reports[key+'GRAM-ENCODINGS']==(f'exact_eight_prefix64_batch{b:02d}_cnfs_v{v}','INDEPENDENT_EXACT_EIGHT_EXPLICIT_BATCH_ENCODING_PASS'),'encoding report path')
        need(reports[key+'LITERAL-PROFILE-EXCLUSIONS']==(f'exact_eight_prefix64_batch{b:02d}_proofs','INDEPENDENT_EXACT_EIGHT_EXPLICIT_BATCH_LITERAL_PROOFS_PASS'),'proof report path')
        need(expected[key+'GRAM-ENCODINGS']==expected[key+'LITERAL-PROFILE-EXCLUSIONS']=='/root/structural_attack','independent batch reviewer')
    key='C-REIMBAYEV-Z82-CONDITIONAL-IDENTITY-AND-ARCHIVE-OVERLAP'
    need(expected[key]=='/root' and reports[key]==('reimbayev_z82','INDEPENDENT_REIMBAYEV_Z82_ARITHMETIC_PASS'),'independent literature reviewer')
    markers=["len(args.cohort)==5","len(data['claims'])==308","len(old['claims'])==303",
      "len(enc['skipped_verified_case_ids'])==60+64*(batch-1)",
      "len(allids)==len(set(allids))==128", "data['claims'][:-5]==old['claims'] and data['artifacts'][:-10]==old['artifacts']",
      "premise['revision']==dep['revision'] and premise['status']=='VERIFIED' and premise['review_state']=='CLEAR'",
      "commit_state=('UNCHANGED_BEFORE' if observed==before_hash else",
      "'REPLACED_WITH_EXPECTED_AFTER' if after_hash is not None and observed==after_hash else",
      "recovery_required=commit_state!='UNCHANGED_BEFORE'", "rel!='PROMPT.md' and not rel.startswith('tools/')"]
    for m in markers:need(m in text,'reviewed invariant '+m)
    return reports
def main():
    out=ROOT/(I+'thirtieth_followup_registrar_source_review');out.mkdir(parents=True,exist_ok=False)
    for p,h in PINS.items():need(sha(ROOT/p)==h,'pin '+p)
    text=(ROOT/SOURCE).read_text();reports=static_checks(text)
    marker='        # Prepare every byte'
    old=(ROOT/OLD).read_text();tail=old[old.index(marker):].replace('THIRTIETH_INITIAL_REGISTRATION_PREPARED','THIRTIETH_FOLLOWUP_REGISTRATION_PREPARED').replace('claim_population=303,new_verified=3','claim_population=308,new_verified=5')
    need(tail==text[text.index(marker):],'transaction/failure tail unchanged after labels')
    rejected=[]
    for a,b in [('batch04_cnfs_v4','batch04_cnfs_v3'),('60+64*(batch-1)','60+64*batch'),("len(data['claims'])==308","len(data['claims'])==307"),("data['claims'][:-5]==old['claims']","True"),('observed==before_hash','ledger_replaced is False')]:
        need(a in text,'control mutation present')
        try:static_checks(text.replace(a,b))
        except ValueError:rejected.append(a)
        else:raise ValueError('negative source control accepted')
    z=read(I+'reimbayev_z82/claim_binding.json')
    need(z['verifier']=='/root' and z['claim_originator']=='/root/state_literature_audit' and z['additional_literal_exclusions']==0,'Z82 source separation and scope')
    e=read(I+'exact_eight_prefix64_batch04_cnfs_v4/summary.json')
    need(len(e['selected_case_ids'])==64 and len(e['skipped_verified_case_ids'])==252,'existing batch04 shape')
    missing=[I+folder+'/summary.json' for folder,_ in reports.values() if not (ROOT/(I+folder+'/summary.json')).exists()]
    inputs=dict(PINS)
    for p in [Path(__file__),Path(__file__).with_name(Path(__file__).stem+'_spec.md')]:inputs[p.relative_to(ROOT).as_posix()]=sha(p)
    record=dict(status='INDEPENDENT_THIRTIETH_FOLLOWUP_REGISTRAR_SOURCE_REVIEW_PASS',created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
      inputs_sha256=inputs,registrar_imported=False,registrar_executed=False,ledger_writes=0,git_writes=0,mathematical_verification=False,
      transaction_tail_unchanged_except_labels=True,source_corruptions_rejected=rejected,blocking_source_findings=[],
      missing_reports_observed=missing,execution_readiness='NOT_APPROVED; actual five authenticated gates and303 baseline remain mandatory',
      scope='Source-only association, fail-closed population/dependency checks, unchanged-record and transaction review; no future evidence preapproval',
      notes=['Five additions: four literal batch claims plus independently reviewed conditional Z82 identity, not five new literal exclusions.',
       'Fixed-support batches retain target_resolution NONE; Z82 unrestricted_target true denotes a conditional identity, not a resolution.',
       'No mathematical self-approval of the reviewer own Z82 producer work; root independent report and written audit are the premises.',
       'Filesystem and Python atomic rename semantics remain trusted; no universal power-loss durability assertion.'])
    (out/'summary.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(status=record['status'],summary_sha256=sha(out/'summary.json'),missing_reports=missing)))
if __name__=='__main__':main()
