"""Prepare, but do not execute, registration of three independently checked batches."""
from pathlib import Path
from datetime import datetime, timezone
import ast, hashlib, json, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]

def h(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    old=ROOT/'acceleration/register_20261001_twentyninth_followup_claims.py'
    assert h(old)=='397aa9450aaa2862df8f2f5301c31e0cbcc361c279559b09c91b0c37466f2eb5'
    text=old.read_text(encoding='utf8')
    def replace(a,b):
        nonlocal text
        assert text.count(a)==1,repr(a)
        text=text.replace(a,b)
    text=text.replace('"""Register only three explicitly pinned, independently bound wave29 followups."""',
                      '"""Register six explicitly pinned claims for prefix64 batches03,04,05."""')
    start=text.index('EXPECTED={');end=text.index("FORBIDDEN=",start)
    text=text[:start]+'''EXPECTED={}
REPORTS={}
for batch in (3,4,5):
    for suffix, folder, status in [
        ('GRAM-ENCODINGS','cnfs_v3','INDEPENDENT_EXACT_EIGHT_EXPLICIT_BATCH_ENCODING_PASS'),
        ('LITERAL-PROFILE-EXCLUSIONS','proofs','INDEPENDENT_EXACT_EIGHT_EXPLICIT_BATCH_LITERAL_PROOFS_PASS')]:
        cid=f'C-FIXED-HADAMARD-EXACT-EIGHT-PREFIX64-BATCH{batch:02d}-'+suffix
        EXPECTED[cid]='/root/structural_attack'
        REPORTS[cid]=(f'exact_eight_prefix64_batch{batch:02d}_'+folder,status)
'''+text[end:]
    start=text.index('def compare_batch(');end=text.index('\ndef main():',start)
    original=text[start:end]
    body=original[original.index('    erow,enc='):original.index('    uniform=')]
    body=body.replace("'C-FIXED-HADAMARD-EXACT-EIGHT-PREFIX64-BATCH02-GRAM-ENCODINGS'", "prefix+'GRAM-ENCODINGS'")
    body=body.replace("'C-FIXED-HADAMARD-EXACT-EIGHT-PREFIX64-BATCH02-LITERAL-PROFILE-EXCLUSIONS'", "prefix+'LITERAL-PROFILE-EXCLUSIONS'")
    replacement='''def compare_batch(rows,reports):
    byid={r['id']:(r,q) for r,q in zip(rows,reports,strict=True)}
    allids=[]
    for batch in (3,4,5):
        prefix=f'C-FIXED-HADAMARD-EXACT-EIGHT-PREFIX64-BATCH{batch:02d}-'
'''+''.join('    '+line+'\n' for line in body.splitlines())+'''        need(len(enc['skipped_verified_case_ids'])==60+64*(batch-1),'exact preceding literal count')
        need(set(allids)<=set(enc['skipped_verified_case_ids']),'new batches chained through authenticated prior cases')
        allids.extend(ids)
    need(len(allids)==len(set(allids))==192,'three disjoint64 populations')
'''
    text=text[:start]+replacement+text[end:]
    replace("        need(args.expected_ledger_sha256=='63f5b98e380fdaeedd5f9f5c53b87e6cfb2b4838a08e1fad3e80207e80d330f8','specific297 baseline')\n", '')
    replace("len(old['claims'])==297 and Counter(c['status'] for c in old['claims'])==dict(VERIFIED=290,CANDIDATE=3,REFUTED=4)",
            "len(old['claims'])==300 and Counter(c['status'] for c in old['claims'])==dict(VERIFIED=293,CANDIDATE=3,REFUTED=4)")
    replace("need(len(args.cohort)==3,'exact three followups')", "need(len(args.cohort)==6,'exact six bound additions')")
    replace("need(len({r['id'] for r in rows})==3 and set(r['id'] for r in rows)==set(EXPECTED),'exact followup identities')", "need([r['id'] for r in rows]==list(EXPECTED),'exact identities in dependency order')")
    replace("aid=f'twentyninth-followup-{index}-evidence{j}'", "aid=f'thirtieth-batches03-05-{index}-evidence{j}'")
    replace("Immutable wave29 evidence publication not yet confirmed.", "Immutable wave30 evidence publication not yet confirmed.")
    replace("data['claims'][:-3]==old['claims'] and data['artifacts'][:-6]==old['artifacts']", "data['claims'][:-6]==old['claims'] and data['artifacts'][:-12]==old['artifacts']")
    replace("need(len(data['claims'])==300,'ending population')", "need(len(data['claims'])==306,'ending population')")
    replace("status='TWENTYNINTH_FOLLOWUPS_REGISTERED'", "status='THIRTIETH_BATCHES03_05_REGISTERED'")
    replace("dict(claim_population=300,new_verified=3,", "dict(claim_population=306,new_verified=6,")
    ast.parse(text)
    target=ROOT/'acceleration/register_20261001_thirtieth_batches03_05.py'
    with target.open('x',encoding='utf8',newline='\n')as f:f.write(text)
    spec=target.with_name(target.stem+'_spec.md')
    with spec.open('x',encoding='utf8',newline='\n')as f:f.write('''# Wave30 batches03 through05 registration preparation

This unexecuted source admits exactly six independently bound revision1 claims:
encoding then complete literal exclusion for each of batch03,04,05 in that order.
Require the explicit CLI SHA of the current300-claim ledger (after publication
availability changes), six report/binding hash pairs, all raw input/output hashes,
the exact report paths and independent PASS statuses, and original verifier and
claim scopes. Preserve all prior claim/artifact objects. Before execution root
must review every actual independent report and binding; pending cases cannot be
registered. This program does no mathematical approval or replay.

Check every CNF/scope/count identity between each encoding and proof report,
complete64 outcomes per batch, disjoint192 new case IDs, and prior proof counts
188,252,316 respectively. Each later prior set must contain all earlier new IDs.
Every dependency must already be VERIFIED/CLEAR at its exact revision. Retain
original scopes, assumptions, shared components and timestamps. New evidence is
LOCAL_ONLY until immutable publication is confirmed. Preserve before/after
ledgers, validation, corruption controls and exact execution provenance.

Reject corrupted revision, status, review state, verifier, identity, independent
report status and formula/proof mismatches. Validate schema, available hashes and
impact before the live write. Output must be fresh. This is a narrowly scoped
extension of the preserved wave29 registrar, not evidence of target resolution.
''')
    out=ROOT/'acceleration/results/20261001_thirtieth_registrar_preparation';out.mkdir(exist_ok=False)
    result=dict(timestamp=datetime.now(timezone.utc).isoformat(),command=[sys.executable,*sys.argv],cwd=str(ROOT),
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        inputs_sha256={old.relative_to(ROOT).as_posix():h(old),Path(__file__).relative_to(ROOT).as_posix():h(Path(__file__))},
        outputs_sha256={target.relative_to(ROOT).as_posix():h(target),spec.relative_to(ROOT).as_posix():h(spec)},
        registrar_executed=False,ledger_mutations=0,mathematical_verification=False,validation='AST parse only; actual bound reports still required.')
    with(out/'summary.json').open('x',encoding='utf8',newline='\n')as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(result['outputs_sha256']))

if __name__=='__main__':main()
