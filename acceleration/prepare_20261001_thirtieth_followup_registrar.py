"""Prepare the exact five-claim followup; never mutate the ledger here."""
from pathlib import Path
from datetime import datetime,timezone
import ast,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    old=ROOT/'acceleration/register_20261001_thirtieth_initial_claims.py'
    assert h(old)=='8208ac246fff0d05cdcd7e5218a7927ac8b7502c117102e0757aa59d9268ab46'
    s=old.read_text(encoding='utf8')
    start=s.index('EXPECTED={');end=s.index("FORBIDDEN=",start)
    pairs=[f'C-FIXED-HADAMARD-EXACT-EIGHT-PREFIX64-BATCH{b:02d}-{suffix}' for b in (4,5) for suffix in ('GRAM-ENCODINGS','LITERAL-PROFILE-EXCLUSIONS')]
    lid='C-REIMBAYEV-Z82-CONDITIONAL-IDENTITY-AND-ARCHIVE-OVERLAP'
    expected={k:'/root/structural_attack' for k in pairs};expected[lid]='/root'
    reports={}
    for b in (4,5):
        pre=f'C-FIXED-HADAMARD-EXACT-EIGHT-PREFIX64-BATCH{b:02d}-'
        reports[pre+'GRAM-ENCODINGS']=(f'exact_eight_prefix64_batch{b:02d}_cnfs_v'+('4' if b==4 else '3'),'INDEPENDENT_EXACT_EIGHT_EXPLICIT_BATCH_ENCODING_PASS')
        reports[pre+'LITERAL-PROFILE-EXCLUSIONS']=(f'exact_eight_prefix64_batch{b:02d}_proofs','INDEPENDENT_EXACT_EIGHT_EXPLICIT_BATCH_LITERAL_PROOFS_PASS')
    reports[lid]=('reimbayev_z82','INDEPENDENT_REIMBAYEV_Z82_ARITHMETIC_PASS')
    s=s[:start]+'EXPECTED='+repr(expected)+'\nREPORTS='+repr(reports)+'\n'+s[end:]
    substitutions={
        'Register only the three completed, independently bound initial wave30 claims.':'Register four later batch claims and the separately reviewed conditional identity.',
        "['statement','scope','assumptions','dependencies','method','shared_components','created_at','updated_at']":"['statement','scope','assumptions','method','shared_components','created_at','updated_at']",
        'for batch in (3,):':'for batch in (4,5):',
        "need(len(allids)==len(set(allids))==64,'one complete disjoint64 population')":"need(len(allids)==len(set(allids))==128,'two complete disjoint64 populations')",
        "'9d9d37c36a695bdfb4833311bdf649b4485ac87e6a185bf66790419afed3b3c2','exact published300 baseline'":"'0fd27c9fe019247eded6509f4c228141ce350e3cf387d98314742c89ecc1d56d','exact registered303 baseline'",
        "len(old['claims'])==300 and Counter(c['status'] for c in old['claims'])==dict(VERIFIED=293,CANDIDATE=3,REFUTED=4)":"len(old['claims'])==303 and Counter(c['status'] for c in old['claims'])==dict(VERIFIED=296,CANDIDATE=3,REFUTED=4)",
        "len(args.cohort)==3,'exact three completed bound additions'":"len(args.cohort)==5,'exact five completed bound additions'",
        "thirtieth-initial-{index}-evidence{j}":"thirtieth-followup-{index}-evidence{j}",
        "timestamp=report.get('timestamp',report.get('created_at'))":"timestamp=row['updated_at'] if row['id']=='C-REIMBAYEV-Z82-CONDITIONAL-IDENTITY-AND-ARCHIVE-OVERLAP' else report.get('timestamp',report.get('created_at'))",
        "unrestricted_target=False,target_resolution='NONE'":"unrestricted_target=row.get('unrestricted_target',False),target_resolution='NONE'",
        "data['claims'][:-3]==old['claims'] and data['artifacts'][:-6]==old['artifacts']":"data['claims'][:-5]==old['claims'] and data['artifacts'][:-10]==old['artifacts']",
        "len(data['claims'])==303":"len(data['claims'])==308",
        "THIRTIETH_INITIAL_":"THIRTIETH_FOLLOWUP_",
        "claim_population=303,new_verified=3":"claim_population=308,new_verified=5",
    }
    for a,b in substitutions.items():
        assert a in s,a;s=s.replace(a,b)
    start=s.index("    crow,core=byid[");end=s.index('\ndef main():',start)
    s=s[:start]+'''    row,report=byid['C-REIMBAYEV-Z82-CONDITIONAL-IDENTITY-AND-ARCHIVE-OVERLAP']
    need(report['complete_archive_coefficients']==208 and report['complete_local_attachments']==64,'complete bounded literature arithmetic')
    need(row['claim_originator']=='/root/state_literature_audit' and row['verifier']=='/root','separate literature producer and verifier')
    need(row['unrestricted_target'] is True and row['additional_literal_exclusions']==0 and row['dependencies']==[],'conditional implication without existence or imported historical premise')
    need(row['written_audit']==dict(path='docs/AUDIT_20261001_REIMBAYEV_Z82.md',sha256='34257aea14c8b2fd21d8adef9aadfbfca925fa4bc8259053f714b0f708c9e60a'),'completed written derivation/normalization/panel audit')
    need(row['evidence_sha256'][row['written_audit']['path']]==row['written_audit']['sha256'],'written audit bound in authenticated closure')
    need(row['independent_report']['sha256']=='9f270d2792de23296d8348cf9911aaed7c24be12fc3535f0a3f0409e7cc35278','exact separate arithmetic report')
''' +s[end:]
    ast.parse(s)
    new=ROOT/'acceleration/register_20261001_thirtieth_followup_claims.py';spec=new.with_name(new.stem+'_spec.md')
    with new.open('x',encoding='utf8',newline='\n')as f:f.write(s)
    with spec.open('x',encoding='utf8',newline='\n')as f:f.write('''# Wave30 followup registration, frozen before use

Start only from exact303 ledger0fd27c9fe019247eded6509f4c228141ce350e3cf387d98314742c89ecc1d56d. Register exactly batch04 encoding v4 and complete proof, batch05 encoding v3 and complete proof, and the independently derived Z82 conditional identity/one-row redundancy. Require all128 exact literal cases complete, disjoint, chained after252 then316 prior cases, same formula/hash populations, correct independent verifier, and actual complete DRAT PASS. For Z82 require the exact arithmetic report and completed written normalization/source-panel review; no imported historical premise and no exclusion.

Authenticate every bound artifact before editing. Preserve all303 prior claim and artifact records unchanged. Reject malformed status/revision/verifier/report/formula controls. Validate schema, current dependencies, promotions and available artifact hashes. Expected308 claims301VERIFIED3CANDIDATE4REFUTED. The universal conditional Z82 implication sets unrestricted_target true but target_resolution NONE; fixed-support batch claims remain false/NONE. This registrar does no mathematical replay.

Retain the previously reviewed same-volume temporary ledger, fsync, prepared receipt/journal, atomic rename, and observed-hash failure recovery. On interruption compare immutable before/after/live bytes; do not rerun or overwrite the transaction. Freeze source/spec and preserve source-only reviews. Preparation alone never executes this registrar.
''')
    out=ROOT/'acceleration/results/20261001_thirtieth_followup_registrar_preparation';out.mkdir(exist_ok=False)
    r=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256={old.relative_to(ROOT).as_posix():h(old),Path(__file__).relative_to(ROOT).as_posix():h(Path(__file__))},outputs_sha256={new.relative_to(ROOT).as_posix():h(new),spec.relative_to(ROOT).as_posix():h(spec)},registrar_executed=False,ledger_mutations=0,validation='AST parse only')
    with(out/'summary.json').open('x',encoding='utf8',newline='\n')as f:json.dump(r,f,indent=2);f.write('\n')
    print(json.dumps(r['outputs_sha256']))
if __name__=='__main__':main()
