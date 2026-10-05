"""Bind the root's independent core check to one narrow claim; no ledger write."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
REPORT='acceleration/results/20261001_independent_review/exact_eight_case0_core/summary.json'
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    path=ROOT/REPORT;assert h(path)=='802dabf3cdb8648b4da29eb390c20a472f32da09104b41717babb221774218b1'
    report=json.loads(path.read_bytes());assert report['status']=='INDEPENDENT_EXACT_EIGHT_CASE0_CORE_PASS'and report['verifier']=='/root'
    for p,digest in report['inputs_sha256'].items():assert h(ROOT/p)==digest,p
    for p,digest in report['outputs_sha256'].items():assert h(ROOT/p)==digest,p
    stats=report['statistics'];assert (report['core_clauses'],report['original_clauses'],len(stats['semantic_support_groups']),len(stats['coordinate_pairs']),len(stats['gram_cells']))==(53914,167416,20,60,527)
    assert stats['duplicate_origin_clauses']==0 and stats['core_variables']==8507
    assert [r['accepted']for r in report['checker_calls']]==[True,False,False,True]
    record=dict(id='C-FIXED-HADAMARD-EXACT-EIGHT-CASE0-CORE-FOOTPRINT',revision=1,
        statement='The raw case0 core with SHA256 900288a299800e4f322e0fd1e63c82c95dcedcec5c3e4ebe4fc29a42f77b313d is an UNSAT 53914-clause subset of the exact 167416-clause CNF 6fecea814c533a081ee0292087b1bf4cccb9cb132ea232b907acd227ba610962; its complete original-clause provenance has one origin per core clause and spans all20 support groups, all60 coordinate pairs and527 of540 Gram cells.',
        kind='empirical/engineering result',basis=['COMPUTED'],status='VERIFIED',review_state='CLEAR',
        scope='Only the named raw trimmed core, its complete proof and original-clause footprint for canonical exact-eight case0. This repeats an already excluded literal case; no additional case, whole-support or target exclusion.',
        assumptions=['The pinned complete original formula/model encoding gate supplies its literal fixed-support semantics.','Standard exact DIMACS clause semantics and the disclosed pinned DRAT checker are trusted components.'],
        dependencies=[dict(id='C-FIXED-HADAMARD-EXACT-EIGHT-CAMPAIGN-FIRST12-GRAM-ENCODINGS',revision=1,relation='encoding_equivalence'),dict(id='C-FIXED-HADAMARD-EXACT-EIGHT-FIRST12-LITERAL-PROFILE-EXCLUSIONS',revision=1,relation='verification_dependency')],
        verifier='/root',method='Independent raw DIMACS parsing, complete multiset-to-original matching and ownership-range partition, exact statistics, and complete fresh trimmed-DRAT replay after positive/corrupted calibration.',
        independent_report=dict(path=REPORT,sha256=h(path)),shared_components=report['shared_components'],limitations=report['limitations'],
        created_at=report['timestamp'],updated_at=report['timestamp'],
        evidence_sha256={REPORT:h(path),**report['inputs_sha256'],**report['outputs_sha256']},
        binding_writer_sha256=h(Path(__file__)),binding_command=[sys.executable,*sys.argv],
        ledger_mutations=0,claim_originator='/root/state_literature_audit',additional_literal_exclusions=0)
    out=path.parent/'claim_binding.json'
    with out.open('x',encoding='utf8',newline='\n')as f:json.dump(record,f,indent=2);f.write('\n')
    print(json.dumps(dict(id=record['id'],binding_sha256=h(out),ledger_mutations=0)))
if __name__=='__main__':main()
