"""Bind already-completed independent checking during stop bookkeeping."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
REPORT='acceleration/results/20261001_independent_review/wave205_third_star/summary.json'
AUDIT='docs/AUDIT_20261001_WAVE205_LITERAL_THIRD_STAR.md'
PROVENANCE='acceleration/results/20261001_wave205_third_star_execution_provenance/receipt.json'
def h(p):
    with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
    p=ROOT/REPORT;assert h(p)=='36a4145f17112f6b40fb42a78af801cbce1ade3dcf497f1bd8d79bde11f5b92b'
    assert h(ROOT/AUDIT)=='796912ae56358d4a248c1312b9ebef2caa16cc01ce1737bb8960aaaa3e0678e8'
    assert h(ROOT/PROVENANCE)=='81d4e13236dd761239999058c8c20f66732eced176c1f79b4614c9bb4e8ad265'
    r=json.loads(p.read_bytes());assert r['status']=='INDEPENDENT_LITERAL_THIRD_STAR_FINITE_OBSTRUCTION_PASS' and r['verifier']=='/root'
    for name,digest in {**r['inputs_sha256'],**r['outputs_sha256']}.items():assert h(ROOT/name)==digest,name
    assert(r['triangle_candidates'],r['retained_triangle_options'],r['complete_nodes'],r['complete_leaves'],r['pair_rank_checks'])==(4050,296,17,0,192)
    row=dict(id='C-WAVE205-LITERAL-T6H1-THIRD-STAR-EXCLUSION',revision=1,statement='No srg(99,14,1,2) that contains no pair of disjoint triangles joined by three cross edges and whose full triangle-incidence Gram D=B^T A B over F3 has rank11 can contain the exact induced28-vertex t6_h1 graph in archived controls.json SHA256 e52c068f5fdba18110debdd1455195ec22145f07993437b5438e8f77ae03fdcf: completing its a-neighborhood would require a five-option cover, but complete checking of4050 options and17 search nodes gives none.',kind='exclusion',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',scope='Only the exact induced28-vertex t6_h1 configuration, conditional on prism-freeness and full ternary triangle-Gram rank11. No other integer lift, entire t6 population, rank11 branch, endpoint or target exclusion.',unrestricted_target=False,assumptions=['A hypothetical target retains every edge and nonedge of the authenticated literal induced28-vertex graph.','No two disjoint triangles have three cross edges.','For the full target triangle-incidence matrix B, rank over F3 of B^T A B is11.'],dependencies=[],verifier='/root',claim_originator='/root/state_literature_audit',method='Independent adjacency-set reconstruction of all4050 options; full rectangular/symmetric GF3 ranks instead of producer inverse coordinates; all192 considered pair ranks and complete17-node tree; separate written proof of exhaustive local-extension coverage.',independent_report=dict(path=REPORT,sha256=h(p)),written_audit=dict(path=AUDIT,sha256=h(ROOT/AUDIT)),shared_components=r['shared_components'],limitations=r['limitations']+['Original archived two-center control remains valid in its earlier scope.','Producer execution-time source commit and tool versions were unrecorded; provenance preserves explicit nulls and separate later observations, not invented historical values.'],created_at='2026-09-30T17:24:35+00:00',updated_at='2026-09-30T17:24:35+00:00',evidence_sha256={REPORT:h(p),AUDIT:h(ROOT/AUDIT),PROVENANCE:h(ROOT/PROVENANCE),**r['inputs_sha256'],**r['outputs_sha256']},binding_writer_sha256=h(Path(__file__)),binding_command=[sys.executable,*sys.argv],ledger_mutations=0,exact_eight_literal_exclusions=0)
    target=p.parent/'claim_binding.json'
    with target.open('x',encoding='utf8',newline='\n')as f:json.dump(row,f,indent=2);f.write('\n')
    print(json.dumps(dict(id=row['id'],binding_sha256=h(target),ledger_mutations=0)))
if __name__=='__main__':main()
