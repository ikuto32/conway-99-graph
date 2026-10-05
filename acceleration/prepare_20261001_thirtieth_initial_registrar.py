"""Prepare registration of the completed batch03 pair and independently checked core footprint."""
from pathlib import Path
from datetime import datetime,timezone
import ast,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    old=ROOT/'acceleration/register_20261001_thirtieth_batches03_05_v3.py'
    assert h(old)=='8ff7c5791c54c72f2c9c16a4237dd162480d63927e87f4d338ca032c79cc7b92'
    text=old.read_text(encoding='utf8')
    def replace(a,b):
        nonlocal text
        assert text.count(a)==1,repr(a);text=text.replace(a,b)
    replace('"""Register six explicitly pinned claims for prefix64 batches03,04,05."""','"""Register only the three completed, independently bound initial wave30 claims."""')
    start=text.index('EXPECTED={}');end=text.index('FORBIDDEN=',start)
    text=text[:start]+'''EXPECTED={
 'C-FIXED-HADAMARD-EXACT-EIGHT-PREFIX64-BATCH03-GRAM-ENCODINGS':'/root/structural_attack',
 'C-FIXED-HADAMARD-EXACT-EIGHT-PREFIX64-BATCH03-LITERAL-PROFILE-EXCLUSIONS':'/root/structural_attack',
 'C-FIXED-HADAMARD-EXACT-EIGHT-CASE0-CORE-FOOTPRINT':'/root',
}
REPORTS={
 'C-FIXED-HADAMARD-EXACT-EIGHT-PREFIX64-BATCH03-GRAM-ENCODINGS':('exact_eight_prefix64_batch03_cnfs_v3','INDEPENDENT_EXACT_EIGHT_EXPLICIT_BATCH_ENCODING_PASS'),
 'C-FIXED-HADAMARD-EXACT-EIGHT-PREFIX64-BATCH03-LITERAL-PROFILE-EXCLUSIONS':('exact_eight_prefix64_batch03_proofs','INDEPENDENT_EXACT_EIGHT_EXPLICIT_BATCH_LITERAL_PROOFS_PASS'),
 'C-FIXED-HADAMARD-EXACT-EIGHT-CASE0-CORE-FOOTPRINT':('exact_eight_case0_core','INDEPENDENT_EXACT_EIGHT_CASE0_CORE_PASS'),
}
'''+text[end:]
    replace('    for batch in (3,4,5):','    for batch in (3,):')
    replace("    need(len(allids)==len(set(allids))==192,'three disjoint64 populations')", '''    need(len(allids)==len(set(allids))==64,'one complete disjoint64 population')
    crow,core=byid['C-FIXED-HADAMARD-EXACT-EIGHT-CASE0-CORE-FOOTPRINT']
    stats=core['statistics']
    need((core['core_clauses'],core['original_clauses'],len(stats['semantic_support_groups']),len(stats['coordinate_pairs']),len(stats['gram_cells']))==(53914,167416,20,60,527),'exact core footprint')
    need(stats['duplicate_origin_clauses']==0 and stats['core_variables']==8507,'exact raw core counts')
    need([r['accepted']for r in core['checker_calls']]==[True,False,False,True],'independent positive/corrupt/complete core replay')
    need(crow['claim_originator']=='/root/state_literature_audit' and core['verifier']=='/root' and crow['additional_literal_exclusions']==0,'distinct core producer and verifier; no new exclusion')''')
    replace("        pin('CLAIMS.yaml',args.expected_ledger_sha256)", "        pin('CLAIMS.yaml',args.expected_ledger_sha256)\n        need(args.expected_ledger_sha256=='9d9d37c36a695bdfb4833311bdf649b4485ac87e6a185bf66790419afed3b3c2','exact published300 baseline')")
    replace("need(len(args.cohort)==6,'exact six bound additions')", "need(len(args.cohort)==3,'exact three completed bound additions')")
    replace("aid=f'thirtieth-batches03-05-{index}-evidence{j}'", "aid=f'thirtieth-initial-{index}-evidence{j}'")
    replace("data['claims'][:-6]==old['claims'] and data['artifacts'][:-12]==old['artifacts']", "data['claims'][:-3]==old['claims'] and data['artifacts'][:-6]==old['artifacts']")
    replace("need(len(data['claims'])==306,'ending population')", "need(len(data['claims'])==303,'ending population')")
    text=text.replace('THIRTIETH_BATCHES03_05','THIRTIETH_INITIAL')
    replace('dict(claim_population=306,new_verified=6,','dict(claim_population=303,new_verified=3,')
    ast.parse(text)
    new=ROOT/'acceleration/register_20261001_thirtieth_initial_claims.py'
    with new.open('x',encoding='utf8',newline='\n')as f:f.write(text)
    spec=new.with_name(new.stem+'_spec.md')
    with spec.open('x',encoding='utf8',newline='\n')as f:f.write('''# Initial wave30 registration

Register exactly three completed, independently bound revision1 claims from
the exact published300 ledger9d9d37c3...: batch03 encoding, batch03 complete64
proofs, and the case0 core footprint. This supersedes the *unexecuted* six-claim
registration plan as an implementation choice, not as a mathematical refutation.
Batch04/05 remain unapproved and absent from this registration.

Preserve v3's independently reviewed identity, report-association, dependency,
scope, old-object equality, validation, corruption controls and atomic commit/
observed-hash recovery logic. All three report/binding pairs are explicit CLI
SHA256 inputs. The original300 claim/artifact objects are unchanged. End at303
claims with six new LOCAL_ONLY evidence references. No mathematical replay is
performed by registration.

Compare every batch03 ordered case/count/CNF/scope and complete proof result,
with exactly188 prior checked literal IDs and64 disjoint new IDs. Independently
bound core statistics must be53914of167416 clauses,20groups,60pairs,527cells,
8507variables,0duplicate origins and calibrated positive/corrupt/complete replay.
The core producer is State; the independent verifier is root. It adds no new
literal exclusion and asserts neither minimality nor indispensability.

Live ledger writes use fully prepared temporary bytes and receipt, immutable
before/after snapshots and PREPARED journal, then same-volume atomic replacement.
Failures classify the actual observed ledger hash, not an in-memory Boolean.
Only exact unchanged-before state permits no recovery audit. Single root writer
and local atomic-rename semantics are explicit operational assumptions; no
universal power-loss guarantee is made. Fresh output only; preserve all failures.
''')
    out=ROOT/'acceleration/results/20261001_thirtieth_initial_registrar_preparation';out.mkdir(exist_ok=False)
    record=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256={old.relative_to(ROOT).as_posix():h(old),Path(__file__).relative_to(ROOT).as_posix():h(Path(__file__))},
        outputs_sha256={new.relative_to(ROOT).as_posix():h(new),spec.relative_to(ROOT).as_posix():h(spec)},registrar_executed=False,ledger_mutations=0,
        reason='Record the already independently checked initial results while batch04 checkpoint continuation and batch05 remain pending. All superseded registrar preparations are retained unexecuted.')
    with(out/'summary.json').open('x',encoding='utf8',newline='\n')as f:json.dump(record,f,indent=2);f.write('\n')
    print(json.dumps(record['outputs_sha256']))
if __name__=='__main__':main()
