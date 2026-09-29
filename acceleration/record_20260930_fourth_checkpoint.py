"""Snapshot the fourteen reviewed claims and derive finite milestone counts."""
from collections import Counter
from datetime import datetime,timezone
from hashlib import sha256
import json,subprocess,sys
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'
def read(p):return json.loads((ROOT/p).read_bytes())
def h(p):return sha256((ROOT/p).read_bytes()).hexdigest()
def save(p,v):
    with (ROOT/p).open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,indent=2);f.write('\n')
def main():
    raw=(ROOT/'CLAIMS.yaml').read_bytes();ledger=yaml.safe_load(raw)
    snapshot=B+'resume/claims_at_fourth_milestone.yaml'
    with (ROOT/snapshot).open('xb') as f:f.write(raw)
    registration=read(B+'resume/fourth_milestone_registration.json');new=registration['new_claim_ids']
    claims=[c for c in ledger['claims'] if c['id'] in new];assert len(claims)==14
    artifacts={a['id']:a for a in ledger['artifacts']}
    paths=[snapshot,B+'resume/fourth_milestone_registration.json',B+'resume/fourth_artifact_catalog.json']
    paths+=list(dict.fromkeys(artifacts[e]['path'] for c in claims for e in c['evidence']))
    now=datetime.now(timezone.utc).isoformat()
    checkpoint=dict(timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),
        previous_report='docs/RESEARCH_20260930_THIRD_WAVE.md',previous_checkpoint_sha256=h(B+'resume/third_milestone_checkpoint.json'),
        target_resolution='UNKNOWN',external_review=None,external_review_reason='No candidate target resolution exists.',
        claim_population=len(ledger['claims']),claim_status_counts=dict(Counter(c['status'] for c in ledger['claims'])),claim_review_counts=dict(Counter(c['review_state'] for c in ledger['claims'])),
        verified_clear=sum(c['status']=='VERIFIED' and c['review_state']=='CLEAR' for c in ledger['claims']),new_verified_ids=new,
        box_wave02_counts=read(B+'independent_review/rook_box_wave02_binding.json')['counts'],
        orbit_counts={'source_clauses':11,'supplied_checked_maps':32,'transport_attempts':352,'unique_clauses':352},
        closed29_counts={'specific_induced_patterns_independently_excluded':2,'already_restored_cap_excluded':1,'passes_restored_partial_caps':1,'whole_stars_excluded':0},
        coverage='Overall search coverage: UNKNOWN; no validated denominator.',
        execution={'completed':['Box wave02 and complete independent finite-wave check','352-clause orbit audit','Two specific raw29 exact audits','Three conditional redundancy theorem audits'],
            'subsequent_work':'Orbit SAT pilot and full99 encoding/SAT work are separate subsequent records; this snapshot does not promote them.',
            'live_process_state':'UNKNOWN from this snapshot; use fresh process observations and actual run receipts.'},
        next_experiment='Use the independently gated complete full99 eight-family CNF for a bounded proof-enabled SAT attempt and independently check any result.',
        evidence_sha256={p:h(p) for p in paths})
    save(B+'resume/fourth_milestone_checkpoint.json',checkpoint)
    rows=[]
    for c in claims:
        audit=artifacts[c['evidence'][0]]['path']
        rows.append('| `'+c['id']+'` | '+c['scope']['description']+' [Audit](../'+audit+'). |')
    text=f'''# Fourth resumed milestone, 2026-09-30 JST

Fourteen independently checked claims were added since the [third milestone](RESEARCH_20260930_THIRD_WAVE.md). They certify conditional Gram cuts and show why three proposed local tests add no information under their hypotheses. Two specific induced29 patterns have exact extension obstructions. No whole eight-coordinate family or unrestricted target is excluded.

**As of:** {now}; source commit `{checkpoint['source_commit']}`. [Checkpoint](../{B}resume/fourth_milestone_checkpoint.json), [ledger snapshot](../{snapshot}). Previous report: [third milestone](RESEARCH_20260930_THIRD_WAVE.md).

**Verdict:** target resolution UNKNOWN. No independently validated target graph or general nonexistence proof; no candidate target resolution is under external review. [Draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3) remains a research review.

**Verified changes:** all revision 1; exact statements and dependencies are in the snapshot.

| Claim | Exact scope and evidence |
| --- | --- |
'''+ '\n'.join(rows)+f'''

**Work completed:** box wave02 made two solver attempts: one independently checked local59 object, one exact new23literal box clause, and one UNKNOWN result. The final ten-clause list includes its prior nine clauses. Eleven source clauses (those ten plus the degree-constrained12literal clause), under32 supplied checked maps, produce352 distinct necessary clauses. These overlapping stages are not summed. Registry population: {len(ledger['claims'])} claims, {checkpoint['verified_clear']} VERIFIED/CLEAR and2 CANDIDATE/CLEAR.

The matching-cap composition theorem and two closed-neighborhood Gram theorems are exact conditional results. The Gram fixture checks covered2,688 saved raw28 graphs; that finite population is not all local stars. The proofs, not numerical eigenvalues, establish the general implications.

**Coverage:** Overall search coverage: UNKNOWN; no validated denominator. No excluded-graph union size, fixed-family completion percentage or unrestricted branch fraction is available.

**Best result:** the12literal degree-constrained cut has exact upper bound `-176426969710399200` for its fixed integer vector over the larger degree-only relaxation. This forbids its falsifying pattern in one frozen rook scaffold. Shorter clause length is a syntactic metric; no increase in excluded degree-feasible assignments or solver speed is claimed. The two raw29 quadratics are `-64940` and `-5868` for different vectors and are not ranked against this objective.

**Problems:** of the two raw29 patterns, one already violates a restored full99 partial pair cap, while the other passes all4,851 restored partial caps. Both pass their406 induced29 caps. No sampled or complete star exclusion follows. Producer screen totals remain unapproved by these narrow audits. The local raw-matrix metadata correction, the scaffold checker convention correction and the raw29 checker's handwritten expected-list correction retain their original failures and source versions. No failed check was silently overwritten.

**Execution:** this milestone's named experiments and audits completed. Subsequent orbit-SAT and full99-SAT records are separate; this static checkpoint makes no live-process assertion. Saved solver timeouts are UNKNOWN, and post-model native cleanup errors remain visible.

**Next experiment:** a bounded proof-producing solve of the complete99vertex eight-coordinate encoding, after independent clause reconstruction and calibration, followed by independent full-object or proof checking. It still covers only the prescribed120fixed-K family. Broader normalization requires a separate coverage audit.

**References:** [source base](https://github.com/ikuto32/conway-99-graph/commit/{checkpoint['source_commit']}), [draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3), [fourth recovery guide](REPRODUCING_20260930_FOURTH_WAVE.md), [artifact catalog](../{B}resume/fourth_artifact_catalog.json). Ledger artifact availability is updated only after an immutable published commit is confirmed.
'''
    with (ROOT/'docs/RESEARCH_20260930_FOURTH_WAVE.md').open('x',encoding='utf-8',newline='\n') as f:f.write(text)
    print(json.dumps({k:checkpoint[k] for k in ['timestamp','claim_population','verified_clear']}))
if __name__=='__main__':main()
