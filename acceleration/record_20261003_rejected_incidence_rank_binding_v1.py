"""Save a narrow REFUTED generic-lemma binding; never mutate the claim ledger."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'acceleration/results/20261003_independent_review/rejected_incidence_rank01'
SUP = ROOT/'acceleration/results/20261003_independent_review/rejected_incidence_rank_supervisor01'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    report_path=BASE/'summary.json'
    report=json.loads(report_path.read_bytes())
    receipt=json.loads((SUP/'summary.json').read_bytes())
    if report['status']!='INDEPENDENT_REJECTED_CODOMAIN_ISOTROPY_COUNTEREXAMPLE_PASS' or not (receipt['command_exit_code']==0 and receipt['cleanup']['reaped'] and receipt['cleanup']['job_active_zero_observed']):
        raise ValueError('Exact counterexample report and actual containment must pass')
    raw=BASE/'raw_counterexample.json'
    if sha(raw)!=report['counterexample_sha256']:
        raise ValueError('Frozen raw counterexample hash')
    paths=[report_path,raw,SUP/'manifest.json',SUP/'summary.json',SUP/'progress.jsonl',Path(__file__)]
    pins={**report['inputs_sha256'],**{p.relative_to(ROOT).as_posix():sha(p) for p in paths}}
    now=datetime.now(timezone.utc).isoformat()
    provenance=dict(original_proposal_sender='/root/structural',original_message_timestamp=None,original_message_timestamp_null_reason='The delivered collaboration text did not expose a timestamp; none is invented.',original_producer_source=None,original_producer_source_null_reason='No source, code-size experiment or target claim binding was produced before the parent veto.',original_proposal_verbatim='While GF2 awaits your scalarcheck, found a potentially different unrestricted coding route beyond archived wave102 (which only records45≤rank2B≤99): with M=BBᵀ=I+A overF2, rankM45 and P=I−M=A projects to54dim nondegenerate alternating kerM. C=PB satisfies CCᵀ=0, so rankC≤27 and rankB=45+rankC≤72. Thus K=kerBᵀ has dimension≥27, even nonzero weights36..60 by archived7-regular support/eigenbounds. Candidate necessary even binary[99,≥27,≥36]code, additionally coisotropic in ImA. No proof promotion/novelty claim; quick archive exact-term search found no72bound. A separately declared small exact Krawtchouk weight-enumerator LP (allunknown evenweights36..60, MacWilliams positivity) could cheap-falsify code feasibility, with exactdual certificates if negative. I can prepare candidate written derivation/controlprotocol without costlybuild while standing by weight60.',parent_counterexample_originator='/root',parent_veto='CC^T=0 bounds rowspace isotropy in the231-dimensional domain, not columnspace rank in the54-dimensional codomain. The generic projector/factor counterexample has rankC54,rankB99. It does not satisfy the actual linear3uniform7regular incidence constraints, so it does not refute a target-specific72bound.')
    binding=dict(id='C-GENERIC-BINARY-PROJECTION-CODOMAIN-ISOTROPY-RANK-LEMMA',revision=1,claim_revision=1,statement='For every binary99x231 matrix B and symmetric binary99x99 idempotent P of rank54 with zero diagonal, if M=I+P has rank45, BB^T=M, and C=PB, then CC^T=0 implies rank(C)<=27 and rank(B)<=72.',kind='mathematical result',basis=['DERIVED','COMPUTED'],status='REFUTED',review_state='CLEAR',scope=dict(description='Only this universal generic binary projection/factor implication. No incidence regularity, weight3 columns, target adjacency identity over the integers, or hypothetical graph is included in its assumptions.',unrestricted_target=False,target_resolution='NONE'),assumptions=['All displayed products and ranks are overGF(2).','The precise quantified generic matrix assumptions in the statement.'],dependencies=[],created_at=now,updated_at=now,producer='/root',original_false_argument_originator='/root/structural',verifier='/root/structural',method='independent_artifact_check',verification_timestamp=report['timestamp'],source_commit=report['source_commit'],command=report['command'],cwd=report['cwd'],python=report['python_version'],report=report_path.relative_to(ROOT).as_posix(),report_sha256=sha(report_path),inputs_sha256=pins,shared_components=['Standard-library exact scalar GF2 products and bitset elimination; only pinned command_deadline.py and run_compute_command.py provide execution containment. No producer checker/source is imported.'],refutation=dict(raw_artifact=raw.relative_to(ROOT).as_posix(),sha256=sha(raw),ranks=report['ranks'],exact_identities=report['exact_checked_identities'],controls=report['controls']),provenance=provenance,limitations=['Synthetic B contains columns of weights0,1,2,3 and is not a linear3uniform7regular target triangle-incidence matrix.','The proposed target-specific rank(B)<=72 statement remains UNKNOWN, rather than REFUTED.','The refuted inference was never used as a verified target premise or in a scientific code-feasibility run.','No novelty, literature completeness, graph existence or general nonexistence is asserted.'],availability='LOCAL_ONLY',retrieval='Raw counterexample, checker, report, written preserved argument and actual receipts are present at the pinned workspace paths; public replay availability follows publication separately.',ledger_mutations=0,writer_source_sha256=sha(Path(__file__)),writer_command=[sys.executable,*sys.argv])
    with args.out.resolve().open('x',encoding='utf8',newline='\n')as stream:
        json.dump(binding,stream,indent=2);stream.write('\n')
    design=ROOT/'docs/DESIGN_20261003_UNRESTRICTED_ROOTED8_V1.md'
    with args.out.resolve().with_name('binding_identity.json').open('x',encoding='utf8',newline='\n')as stream:
        json.dump(dict(binding_sha256=sha(args.out.resolve()),report_sha256=sha(report_path),prospective_unrestricted_root8_design=dict(path=design.relative_to(ROOT).as_posix(),sha256=sha(design),execution='DESIGN_ONLY; no new model build launched')),stream,indent=2);stream.write('\n')


if __name__=='__main__':
    main()
