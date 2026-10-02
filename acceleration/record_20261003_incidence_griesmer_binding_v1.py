"""Metadata only: bind ROOT's accepted written derivation; pin new census output."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'acceleration/results/20261003_independent_review/incidence_griesmer01'
REPORT=BASE/'summary.json'
REPORT_SHA='f6d37038fa7f5969331e8d7ee9490bdcc6ebda09b3a0770b7a99dea298a9c59b'
CENSUS=ROOT/'acceleration/results/20261003_weight60_warm_root_census02'

def sha(path):
    with path.open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def need(ok,why):
    if not ok:raise ValueError(why)
def write(path,obj):
    with path.open('x',encoding='utf8',newline='\n')as stream:json.dump(obj,stream,indent=2);stream.write('\n')

def main():
    need(sha(REPORT)==REPORT_SHA,'Exact accepted ROOT derivation report')
    report=json.loads(REPORT.read_bytes())
    need(report['status']=='INDEPENDENT_CONDITIONAL_TRIANGLE_INCIDENCE_GRIESMER_DERIVATION_V1_PASS'and report['producer']=='/root/structural'and report['verifier']=='/root'and report['method']=='independent_derivation','Exact independent derivation identity')
    need(report['minimum_rank']==67 and report['maximum_kernel_dimension']==32 and report['controls']['total_subspaces']==3290,'Exact recorded scope')
    pins=dict(report['inputs_sha256'])
    for folder in [BASE,ROOT/'acceleration/results/20261003_independent_review/incidence_griesmer_supervision01']:
        need(folder.is_dir(),'Recorded evidence folder exists')
        for path in folder.rglob('*'):
            if path.is_file():pins[path.relative_to(ROOT).as_posix()]=sha(path)
    for path in [Path(__file__),ROOT/'acceleration/run_compute_command.py']:
        pins[path.relative_to(ROOT).as_posix()]=sha(path)
    for name,expected in pins.items():need(sha(ROOT/name)==expected,'Exact metadata identity '+name)
    now=datetime.now(timezone.utc).isoformat()
    binding=dict(id='C-UNRESTRICTED-TRIANGLE-INCIDENCE-BINARY-RANK-LOWER67',revision=1,claim_revision=1,
        statement='For every99x99 binary symmetric zero-diagonal matrix A satisfying A^2=12I-A+2J exactly over the integers, let B be its99x231 binary vertex-by-triangle incidence matrix with one column for every actual triangle. Then rank_GF(2)(B)>=67, equivalently dim_GF(2)ker(B^T)<=32. This is a conditional implication and establishes neither existence nor nonexistence of such A.',
        kind='mathematical result',basis=['DERIVED'],status='VERIFIED',review_state='CLEAR',
        scope=dict(description='Universal conditional necessary rank lower bound for the unrestricted target identity. Complete written independent derivation supplies the quantifiers; finite exact controls challenge critical steps only.',unrestricted_target=True,target_resolution='NONE'),
        assumptions=['A is binary, symmetric, zero diagonal and satisfies the full target integer identity. Its existence is UNKNOWN.','B contains exactly every actual triangle once, with ordinary vertex incidence entries. No automorphism, additional rank upper bound or prism-absence assumption is made.'],
        dependencies=[],created_at=now,updated_at=now,producer='/root/structural',verifier='/root',method='independent_derivation',verification_timestamp=report['timestamp'],
        source_commit=report['source_commit'],source_commit_role='Actual ROOT control invocation base commit; new discovery/audit source bytes are separately hash pinned, not inferred present in this commit.',
        command=report['command'],cwd=report['cwd'],tool_versions=dict(python=report['python']),
        report=REPORT.relative_to(ROOT).as_posix(),report_sha256=REPORT_SHA,written_audit=report['written_audit'],inputs_sha256=pins,
        shared_components=report['shared_components'],
        recorded_validation=dict(written_derivation='Complete incidence partition, exact integer moments/Cauchy, independent residual-code induction and rank-nullity.',positive_fixture='Rook9 complete16-word triangle kernel,15 nonzero words.',small_code_controls=dict(binary_subspaces=3290,lengths='0..6',minimum_word_residual_checks=5855),strict_negative_controls=5,finite_controls_are_general_proof=False),
        premise_state='UNKNOWN',rank_upper72_state='UNKNOWN; the separately refuted generic linear lemma is not a dependency or premise.',novelty=None,novelty_null_reason='No novelty audit was performed; archived weight-interval overlap is disclosed below.',
        external_review=None,external_review_null_reason='Internal independent written derivation only; no peer or external review is recorded.',
        formalization=None,formalization_null_reason=report['formalization_reason'],
        literature_context=dict(classical_source='J. H. Griesmer, A Bound for Error-Correcting Codes, IBM JRD4(5),1960,pp532-542,DOI10.1147/rd.45.0532,Section2 recurrence/Theorems1-2.',access_date='2026-10-03 Asia/Tokyo',source_url='https://bitsavers.trailing-edge.com/pdf/ibm/IBM_Journal_of_Research_and_Development/045/ibmrd0405M.pdf',basis_role='Context only; full independent proof does not depend on scan/OCR.'),
        historical_source=dict(repository='https://github.com/YesterdaysLemon/conway-99-research',commit='85e705cc6c2a14d123120c93a847e30aaab1789e',path='attempts/wave102-prism-incidence-code/derivation.md',section='1',original_claim_id=None,original_claim_id_null_reason='No corresponding exact historical claim ID was identified in the examined ledger; no ID is invented.',role='Immutable provenance for preexisting weight36..60 argument overlap only, not fresh verification or a material premise.'),
        limitations=report['limitations']+['The original candidate note is preserved byte-for-byte at06c72ef3...; its historical discovery wording is not rewritten by this binding.','This metadata writer performs no new mathematical checking or promotion beyond the accepted ROOT report and parent binding instruction.'],
        availability='LOCAL_ONLY',retrieval='Complete discovery note, independent written proof, exact finite controls/checker source and actual successful receipt are in the pinned repository paths; publication state is separately recorded.',
        metadata_only=True,writer_source_sha256=sha(Path(__file__)),writer_command=[sys.executable,*sys.argv],ledger_mutations=0)
    write(BASE/'claim_binding.json',binding)
    write(BASE/'binding_identity.json',dict(binding_sha256=sha(BASE/'claim_binding.json'),report_sha256=REPORT_SHA,metadata_only=True))
    census=json.loads((CENSUS/'summary.json').read_bytes())
    need(census['status']=='WARM_SCAFFOLD_ROOT_CENSUS_V2_OUTPUT_PENDING_INDEPENDENT_CHECK','New census output remains candidate')
    census_pins={**census['inputs_sha256'],**{name:rec['sha256']for name,rec in census['artifacts'].items()}}
    for folder in [CENSUS,ROOT/'acceleration/results/20261003_weight60_warm_root_census_supervision02']:
        for path in folder.rglob('*'):
            if path.is_file():census_pins[path.relative_to(ROOT).as_posix()]=sha(path)
    for name,expected in census_pins.items():need(sha(ROOT/name)==expected,'Census output identity only '+name)
    identity=dict(status='CANDIDATE_CENSUS_METADATA_IDENTITY_ONLY',timestamp=now,summary_sha256=sha(CENSUS/'summary.json'),inputs_sha256=census_pins,
        graph_results=[dict(label=g['label'],raw_sha256=g['raw_sha256'],direct_root_count=len(g['all84_cn2_eligible_roots']),minimum_row_mu=g['minimum_mu_row_residual'],minimum_root_ties=g['minimum_root_ties'],global_mu=g['global_unordered_mu_energy'])for g in census['graph_summaries']],
        independent_approval=False,mathematical_checks_performed=0,ledger_mutations=0)
    write(CENSUS/'candidate_identity_record.json',identity)
    print(json.dumps(dict(griesmer_binding_sha256=sha(BASE/'claim_binding.json'),census_summary_sha256=sha(CENSUS/'summary.json'),census_results=identity['graph_results'])))

if __name__=='__main__':main()
