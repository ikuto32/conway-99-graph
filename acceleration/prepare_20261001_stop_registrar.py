"""Prepare only the completed five stop-checkpoint additions; no research launch."""
from pathlib import Path
from datetime import datetime,timezone
import ast,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    old=ROOT/'acceleration/register_20261001_thirtieth_followup_claims.py';assert h(old)=='40a9cae1366798685c1cf3c9796a54ff0b36005213f4573709cf0639a1783354'
    s=old.read_text(encoding='utf8');start=s.index('EXPECTED=');end=s.index('FORBIDDEN=',start)
    ids=['C-FIXED-HADAMARD-EXACT-EIGHT-PREFIX64-BATCH04-GRAM-ENCODINGS','C-FIXED-HADAMARD-EXACT-EIGHT-PREFIX64-BATCH04-LITERAL-PROFILE-EXCLUSIONS','C-FIXED-HADAMARD-EXACT-EIGHT-PREFIX64-BATCH05-GRAM-ENCODINGS','C-REIMBAYEV-Z82-CONDITIONAL-IDENTITY-AND-ARCHIVE-OVERLAP','C-WAVE205-LITERAL-T6H1-THIRD-STAR-EXCLUSION']
    expected={i:('/root/structural_attack'if j<3 else '/root')for j,i in enumerate(ids)}
    folders=['exact_eight_prefix64_batch04_cnfs_v4','exact_eight_prefix64_batch04_proofs','exact_eight_prefix64_batch05_cnfs_v3','reimbayev_z82','wave205_third_star']
    statuses=['INDEPENDENT_EXACT_EIGHT_EXPLICIT_BATCH_ENCODING_PASS','INDEPENDENT_EXACT_EIGHT_EXPLICIT_BATCH_LITERAL_PROOFS_PASS','INDEPENDENT_EXACT_EIGHT_EXPLICIT_BATCH_ENCODING_PASS','INDEPENDENT_REIMBAYEV_Z82_ARITHMETIC_PASS','INDEPENDENT_LITERAL_THIRD_STAR_FINITE_OBSTRUCTION_PASS']
    reports={i:(folder,status)for i,folder,status in zip(ids,folders,statuses,strict=True)}
    s=s[:start]+'EXPECTED='+repr(expected)+'\nREPORTS='+repr(reports)+'\n'+s[end:]
    s=s.replace('for batch in (4,5):','for batch in (4,):').replace("len(allids)==len(set(allids))==128,'two complete disjoint64 populations'","len(allids)==len(set(allids))==64,'one complete disjoint64 proof population'")
    marker="    row,report=byid['C-REIMBAYEV-Z82-CONDITIONAL-IDENTITY-AND-ARCHIVE-OVERLAP']"
    add='''    row,enc=byid['C-FIXED-HADAMARD-EXACT-EIGHT-PREFIX64-BATCH05-GRAM-ENCODINGS']
    need(row['checked_cases']==enc['checked_cases'] and enc['complete_formulas']==64,'batch05 encoding only')
    encoded=[r['case_id']for r in enc['checked_cases']]
    need(len(encoded)==len(set(encoded))==64 and encoded==enc['selected_case_ids'],'batch05 exact64 encoding IDs')
    need(len(enc['skipped_verified_case_ids'])==316 and set(allids)<=set(enc['skipped_verified_case_ids']) and set(encoded).isdisjoint(enc['skipped_verified_case_ids']),'batch05 prior316 and disjoint selection')
    need(all(r['all_initial_domains']and r['complete_raw_clause_reconstruction']for r in enc['checked_cases']),'batch05 complete encoding reconstruction')
    row,review=byid['C-WAVE205-LITERAL-T6H1-THIRD-STAR-EXCLUSION']
    need((review['triangle_candidates'],review['retained_triangle_options'],review['complete_nodes'],review['complete_leaves'],review['pair_rank_checks'])==(4050,296,17,0,192),'exact independently checked finite obstruction')
    need(row['claim_originator']=='/root/state_literature_audit' and row['verifier']=='/root' and row['dependencies']==[] and row['exact_eight_literal_exclusions']==0,'distinct literal-control review, no imported old premise or extra campaign case')
    need(row['written_audit']==dict(path='docs/AUDIT_20261001_WAVE205_LITERAL_THIRD_STAR.md',sha256='796912ae56358d4a248c1312b9ebef2caa16cc01ce1737bb8960aaaa3e0678e8'),'complete coverage written review')
    need(row['evidence_sha256'][row['written_audit']['path']]==row['written_audit']['sha256'],'coverage review authenticated')
'''
    assert marker in s;s=s.replace(marker,add+marker)
    s=s.replace("row['id']=='C-REIMBAYEV-Z82-CONDITIONAL-IDENTITY-AND-ARCHIVE-OVERLAP'","row['id'] in ('C-REIMBAYEV-Z82-CONDITIONAL-IDENTITY-AND-ARCHIVE-OVERLAP','C-WAVE205-LITERAL-T6H1-THIRD-STAR-EXCLUSION')")
    s=s.replace('THIRTIETH_FOLLOWUP_','STOP_20261001_').replace('thirtieth-followup-{index}','stop-20261001-{index}')
    s=s.replace('Register four later batch claims and the separately reviewed conditional identity.','Register completed stop-checkpoint claims only; batch05 has no solver result.')
    ast.parse(s);new=ROOT/'acceleration/register_20261001_stop_claims.py';spec=new.with_name(new.stem+'_spec.md')
    with new.open('x',encoding='utf8',newline='\n')as f:f.write(s)
    with spec.open('x',encoding='utf8',newline='\n')as f:f.write('''# User-stop claim registration

Start exact303 ledger0fd27c9fe019247eded6509f4c228141ce350e3cf387d98314742c89ecc1d56d. Register only five COMPLETED independently bound claims: batch04 full encoding and complete proof; batch05 full encoding WITHOUT solver/exclusion claim; Z82 conditional identity/archived row overlap; one literal t6_h1 third-star exclusion with written coverage review. Expected308 claims301VERIFIED3CANDIDATE4REFUTED. Literal campaign union remains316, not380. No native/build/selection/proof replay is authorized or performed by this registrar.

Retain reviewed fail-closed hash/status/verifier/dependency checks and malformed controls, preserve303 old claim records, validate the entire proposed ledger and available artifacts. Authenticate both root written reviews and distinct producer/verifier identities. Preserve atomic prepared ledger/receipt/journal and observed-hash recovery. The earlier five-claim followup and380-case checkpoint/inventory preparations remain unexecuted and superseded by this explicit stop scope, never silently reused.
''')
    out=ROOT/'acceleration/results/20261001_stop_registrar_preparation';out.mkdir(exist_ok=False)
    r=dict(timestamp=datetime.now(timezone.utc).isoformat(),command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256={old.relative_to(ROOT).as_posix():h(old),Path(__file__).relative_to(ROOT).as_posix():h(Path(__file__))},outputs_sha256={new.relative_to(ROOT).as_posix():h(new),spec.relative_to(ROOT).as_posix():h(spec)},registrar_executed=False,ledger_mutations=0,user_stop=True)
    with(out/'summary.json').open('x',encoding='utf8',newline='\n')as f:json.dump(r,f,indent=2);f.write('\n')
    print(json.dumps(r['outputs_sha256']))
if __name__=='__main__':main()
