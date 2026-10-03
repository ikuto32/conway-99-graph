"""Bind root's separate arithmetic and written review, without ledger mutation."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
REPORT='acceleration/results/20261001_independent_review/reimbayev_z82/summary.json'
AUDIT='docs/AUDIT_20261001_REIMBAYEV_Z82.md'
def h(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
    p=ROOT/REPORT;assert h(p)=='9f270d2792de23296d8348cf9911aaed7c24be12fc3535f0a3f0409e7cc35278'
    r=json.loads(p.read_bytes());assert r['status']=='INDEPENDENT_REIMBAYEV_Z82_ARITHMETIC_PASS' and r['verifier']=='/root'
    for name,digest in {**r['inputs_sha256'],**r['outputs_sha256']}.items():assert h(ROOT/name)==digest,name
    assert r['complete_archive_coefficients']==208 and r['complete_local_attachments']==64
    text=(ROOT/AUDIT).read_text(encoding='utf8');assert 'PASS within the exact scope' in text and 'panel 82 shows' in text
    statement='For every srg(n,k,1,2), with n3 counting induced copies of two disjoint triangles joined by exactly two matching cross edges and z82 counting that graph plus an isolated vertex, z82=(n-6k+18)n3. This identity is deletion minus the sum of vertex-orbit rows plus the sum of pair-orbit rows in the inspected archived extension-row definitions; its coefficient vector agrees on all208 saved seven-vertex class masks.'
    row=dict(id='C-REIMBAYEV-Z82-CONDITIONAL-IDENTITY-AND-ARCHIVE-OVERLAP',revision=1,statement=statement,kind='mathematical result',basis=['CITED','DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',scope='Universal conditional identity for srg(n,k,1,2), including target specialization z82=33n3, and one exact archived row redundancy. No existence premise is established and no exclusion is added.',unrestricted_target=True,assumptions=['The graph under the conditional implication is an srg(n,k,1,2).','n3 and z82 count induced vertex subsets, not labelled embeddings.'],dependencies=[],verifier='/root',claim_originator='/root/state_literature_audit',method='Independent local counting derivation; complete raw208 coefficient and64 attachment reconstruction with a separate adjacency-set recognizer; exact controls; written archive-normalization and primary-PDF panel review.',independent_report=dict(path=REPORT,sha256=h(p)),written_audit=dict(path=AUDIT,sha256=h(ROOT/AUDIT)),shared_components=r['shared_components'],limitations=r['limitations']+['Archive historical claim C-WAVE23-WEIGHTED-EXTENSIONS-020 is referenced for provenance, not imported as a freshly verified mathematical premise.'],created_at='2026-09-30T17:03:51+00:00',updated_at='2026-09-30T17:03:51+00:00',evidence_sha256={REPORT:h(p),AUDIT:h(ROOT/AUDIT),**r['inputs_sha256'],**r['outputs_sha256']},source_version='arXiv:2608.19410v1, Section2, z82 formula PDFp10; panel82 PDFp5; accessed2026-09-30UTC/2026-10-01JST.',archive_reference=dict(repository='YesterdaysLemon/conway-99-research',commit='85e705cc6c2a14d123120c93a847e30aaab1789e',path='CLAIMS.yaml',original_claim_id='C-WAVE23-WEIGHTED-EXTENSIONS-020'),binding_writer_sha256=h(Path(__file__)),binding_command=[sys.executable,*sys.argv],ledger_mutations=0,additional_literal_exclusions=0)
    dest=p.parent/'claim_binding.json'
    with dest.open('x',encoding='utf8',newline='\n') as f:json.dump(row,f,indent=2);f.write('\n')
    print(json.dumps(dict(id=row['id'],binding_sha256=h(dest),written_audit_sha256=h(ROOT/AUDIT),ledger_mutations=0)))
if __name__=='__main__':main()
