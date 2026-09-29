"""Ledger-derived checkpoint for new full99 encodings and exact local cuts."""
from collections import Counter
from datetime import datetime,timezone
from hashlib import sha256
import json,subprocess,sys,yaml
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'
def read(p):return json.loads((ROOT/p).read_bytes())
def h(p):return sha256((ROOT/p).read_bytes()).hexdigest()
def save(p,v):
    with (ROOT/p).open('x',encoding='utf-8',newline='\n')as f:json.dump(v,f,indent=2);f.write('\n')
def main():
    raw=(ROOT/'CLAIMS.yaml').read_bytes();ledger=yaml.safe_load(raw)
    snapshot=B+'resume/claims_at_fifth_milestone.yaml'
    with (ROOT/snapshot).open('xb')as f:f.write(raw)
    ids=read(B+'resume/fifth_milestone_registration.json')['new_claim_ids'];claims=[c for c in ledger['claims'] if c['id'] in ids];assert len(claims)==6
    artifacts={a['id']:a for a in ledger['artifacts']}
    paths=list(dict.fromkeys(artifacts[e]['path'] for c in claims for e in c['evidence']))
    paths += [snapshot,B+'resume/fifth_artifact_catalog.json',B+'eight_full99_solver_pilot/main/receipt.json',B+'eight_full99_solver_pilot/summary.json',B+'native_cadical195_build/receipt.json']
    eight=read(B+'eight_full99_solver_pilot/main/receipt.json');assert eight['worker_observed_stopped']
    now=datetime.now(timezone.utc).isoformat();source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    out={'timestamp':now,'source_commit':source,'command':[sys.executable,*sys.argv],'cwd':str(ROOT),'previous_report':'docs/RESEARCH_20260930_FOURTH_WAVE.md',
        'previous_checkpoint_sha256':h(B+'resume/fourth_milestone_checkpoint.json'),'target_resolution':'UNKNOWN','external_review':None,'external_review_reason':'No target graph or general nonexistence proof has been established.',
        'claim_population':len(ledger['claims']),'claim_status_counts':dict(Counter(c['status'] for c in ledger['claims'])),'claim_review_counts':dict(Counter(c['review_state'] for c in ledger['claims'])),
        'verified_clear':sum(c['status']=='VERIFIED' and c['review_state']=='CLEAR' for c in ledger['claims']),'new_verified_ids':ids,
        'encoding_populations':{'conditional_eight':{'graph_variables':2160,'all_variables':485165,'clauses':1684724},'unrestricted':{'graph_variables':3486,'all_variables':1186500,'clauses':4136454}},
        'conditional_eight_solver':{'attempts':1,'answer':eight['solver_answer'],'conflicts':eight['stats']['conflicts'],'process_seconds':eight['wall_seconds'],'exit_code':eight['worker_exit_code'],'model_artifacts':0,'proof_artifacts':0},
        'local_orbit_sat':{'attempts':1,'independent_complete_assignments':1,'clauses_checked':3690172,'specific_graphs_gram_excluded':1,'new_box_clause_literals':43},
        'coverage':'Overall search coverage: UNKNOWN; no validated denominator. Encoding equivalence is not a search-coverage percentage.',
        'execution':'Recorded conditional pilot completed. No unrestricted research result is present in this checkpoint. Native and object checking gates are separate subsequent records; live process state is UNKNOWN from this static snapshot.',
        'next_experiment':'After both calibration gates, run one bounded native proof-producing solve of the independently equivalent unrestricted CNF and separately check any model or complete proof.',
        'evidence_sha256':{p:h(p) for p in paths}}
    save(B+'resume/fifth_milestone_checkpoint.json',out)
    rows=[]
    for c in claims:rows.append('| `'+c['id']+'` | '+c['scope']['description']+' [Audit](../'+artifacts[c['evidence'][0]]['path']+'). |')
    report=f'''# Fifth resumed milestone, 2026-09-30 JST

Six independently checked claims were added since the [fourth milestone](RESEARCH_20260930_FOURTH_WAVE.md). A complete raw CNF now has an independent unrestricted equivalence and coverage proof. This verifies the problem encoding, not its satisfiability. The earlier conditional full99 pilot ended UNKNOWN. A new local rook witness passed every clause but has two exact Gram obstructions.

**As of:** {now}; source commit `{source}`. [Checkpoint](../{B}resume/fifth_milestone_checkpoint.json), [ledger snapshot](../{snapshot}); previous report: [fourth milestone](RESEARCH_20260930_FOURTH_WAVE.md).

**Verdict:** target resolution UNKNOWN. No independently validated target graph or general nonexistence proof, and no candidate target resolution under external review. Draft [PR3](https://github.com/ikuto32/conway-99-graph/pull/3) remains unmerged by this agent.

**Verified changes:** all revision1.

| Claim | Scope and evidence |
| --- | --- |
'''+ '\n'.join(rows)+f'''

**Work completed:** the conditional encoding audit reconstructed all1,684,724 clauses and485,165 variables. The unrestricted audit reconstructed all4,136,454 clauses and1,186,500 variables, with all3,486 outer pairs free. It separately checked the universal root normalization and threshold semantics. These are two different encodings, not disjoint graph populations.

The orbit pilot produced one independently checked assignment satisfying3,690,172 clauses and its complete local59 conditions. Its two integer Gram quadratics are negative; the specific graph cannot extend to the target. A separately checked43literal box clause follows. The conditional full99 pilot made one attempt, returned UNKNOWN after1,000,001 conflicts and257.546 seconds including loading, and saved no model or proof. Its native wrapper cleanup exit3221226505 is preserved. Registry population: {len(ledger['claims'])} claims, {out['verified_clear']} VERIFIED/CLEAR and2 CANDIDATE/CLEAR.

**Coverage:** Overall search coverage: UNKNOWN; no validated denominator. The unrestricted equivalence covers the target definition, but there is no justified percentage of its search space exhausted.

**Best result:** an exact, independently checked unrestricted SAT equivalence with no fixed outer-edge pattern or automorphism premise. This is a logical equivalence, not a numerical bound or proof of either answer. The44literal eight-family Gram clause has exact maximum `-5868` for its own fixed vector; the43literal rook clause concerns a different vector and model, so their values are not compared.

**Problems:** the original orbit checker stopped on legacy path-separator metadata. Its source, failed log and correction are preserved; v2 checked the complete saved object without a solver retry. The w81 cut's original wording about a weaker CNF was corrected in a separate scope note: the clause is entailed by the exact conditional full99 encoding. Native Windows cleanup errors do not replace object/proof checks. The separate unrestricted preflight text-read correction is preserved.

**Execution:** the conditional solver and stated audits completed. The native Linux solver was built from pristine CaDiCaL1.9.5 commit `146207318796f094dcded87349a64f0c6927309e`; its calibration and unrestricted object-checker gates are subsequent work. This snapshot makes no persistent live-process assertion and records no unrestricted solver result.

**Next experiment:** one bounded native proof-producing solve of the unrestricted CNF after the two checking gates. SAT must pass a separate complete99 matrix identity check; UNSAT must have a complete proof replay on the exact CNF. Timeout or a resource limit remains UNKNOWN and triggers a new research choice.

**References:** [source base](https://github.com/ikuto32/conway-99-graph/commit/{source}), [draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3), [unrestricted derivation](AUDIT_20260930_UNRESTRICTED_FULL99_ENCODING_DERIVATION.md), [artifact catalog](../{B}resume/fifth_artifact_catalog.json), [prior recovery guide](REPRODUCING_20260930_FOURTH_WAVE.md). Ordered gzip parts recover the complete unrestricted input/model; the exact raw byte identities were independently checked. Claim artifact availability changes only after immutable publication is confirmed.
'''
    with (ROOT/'docs/RESEARCH_20260930_FIFTH_WAVE.md').open('x',encoding='utf-8',newline='\n')as f:f.write(report)
    print(json.dumps({k:out[k]for k in ['timestamp','claim_population','verified_clear']}))
if __name__=='__main__':main()
