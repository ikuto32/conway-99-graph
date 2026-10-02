"""Ledger-derived six-claim milestone; no mathematical replay or live observation."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import validate_claims as registry

ROOT=Path(__file__).resolve().parents[1]
BASE='acceleration/results/20261003_wave37_registration01/CLAIMS.before.yaml'
EXPECTED={
 'C-HYPERGRAPH-WEIGHT60-V2-PILOT01-SAVED-OBJECTS',
 'C-UNRESTRICTED-ROOTED7-CONTENT-DIVIDED-GF2-FOUR-PRIMALS',
 'C-HYPERGRAPH-WEIGHT60-PILOT01-TWO-GRAPH-WARM-ROOT-CENSUS',
 'C-GENERIC-BINARY-PROJECTION-CODOMAIN-ISOTROPY-RANK-LEMMA',
 'C-UNRESTRICTED-ROOTED8-NONEDGE-LOCAL-CATALOGUE-COVERAGE',
 'C-UNRESTRICTED-ROOTED8-MARKED-UNIVERSAL5-PRODUCT-NECESSARY-ENCODING',
}
REPORTS={
 'impact':('acceleration/results/20261003_independent_review/wave37_transition01/summary.json','a1b95613e3ff5698f3220952607b2cb8d9a840498c216acb0df5c414b9f4e5d6'),
 'pilot':('acceleration/results/20261003_independent_review/weight60_pilot01/summary.json','a80ec86298ce13ae8fea44c118ebbe613dd4b55e4387ac49e39ec9b3d4cd40d2'),
 'gf2':('acceleration/results/20261003_independent_review/root7_mod2_full02/summary.json','2af2ec6f0c527c079249dede08cba32c2c403837390f46c4187ec972738a1f62'),
 'roots':('acceleration/results/20261003_independent_review/weight60_roots_dense01/summary.json','99a319ea75ca2984e3b5e85dcf42dff7e066cf8fef4d9e510d47479addf06a2f'),
 'catalogue':('acceleration/results/20261003_independent_review/rooted8_unrestricted_catalogue01/summary.json','1cf70d9caed5235bcce437fbc57280a0778c1f9a6cd9d628766de586516f9a6a'),
 'model':('acceleration/results/20261003_independent_review/rooted8_unrestricted_model01/summary.json','ec5073a22027c512e29dac1d49048a507f272cb8ce1a0a79d2ca1f663f1be974'),
}


def need(ok,why):
 if not ok:raise ValueError(why)


def sha(p):
 with p.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--ledger-sha256',required=True)
 ap.add_argument('--out',type=Path,required=True)
 args=ap.parse_args()
 raw=(ROOT/'CLAIMS.yaml').read_bytes()
 need(hashlib.sha256(raw).hexdigest()==args.ledger_sha256,'exact ledger')
 current=registry.read_ledger(ROOT/'CLAIMS.yaml');baseline=registry.read_ledger(ROOT/BASE)
 need(len(baseline['claims'])==337 and current['claims'][:337]==baseline['claims'],'unchanged337 baseline')
 new=current['claims'][337:]
 need(len(current['claims'])==343 and {c['id'] for c in new}==EXPECTED,'exact six additions')
 counts=dict(Counter(c['status'] for c in current['claims']))
 need(counts=={'VERIFIED':335,'CANDIDATE':3,'REFUTED':5} and all(c['review_state']=='CLEAR' for c in current['claims']),'exact ledger counts')
 reports={}
 for label,(p,h) in REPORTS.items():
  need(sha(ROOT/p)==h,'exact saved report')
  reports[label]=json.loads((ROOT/p).read_bytes())
 need(reports['impact']['current_claims']==343,'independent exact impact population')
 now=datetime.now(timezone.utc).isoformat();commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 out=args.out.resolve();need(out.is_relative_to(ROOT),'bounded checkpoint');out.mkdir(parents=True,exist_ok=False)
 checkpoint=dict(timestamp=now,source_commit=commit,source_sha256=sha(Path(__file__)),command=[sys.executable,*sys.argv],cwd=str(ROOT),
                 previous_report='docs/RESEARCH_20261003_THIRTYSIXTH_WAVE.md',ledger_sha256=args.ledger_sha256,
                 claim_records=343,status_counts=counts,review_state_counts={'CLEAR':343},
                 new_claim_revisions=[{k:c[k] for k in ('id','revision','status','statement','scope')} for c in new],
                 inputs_sha256={p:h for p,h in REPORTS.values()},target_resolution=current['target']['status'],
                 new_exclusions=0,overall_search_coverage='UNKNOWN; no validated denominator.',mathematical_replays=0,
                 execution_observation=None,execution_observation_reason='This generator does not observe processes. Actual live/terminal observations are separately pinned run records, not inferred from this ledger snapshot.')
 (out/'CLAIMS.yaml').write_bytes(raw)
 (out/'checkpoint.json').write_text(json.dumps(checkpoint,indent=2)+'\n',encoding='utf8',newline='\n')
 rows='\n'.join('| '+c['id']+' r1 | '+c['status']+' | '+c['scope']['description']+' | [Audit](../'+c['verification'][0]['command_or_audit']+') |' for c in new)
 text=f'''# Thirty-seventh research milestone, 2026-10-03

Since the [wave36 milestone](RESEARCH_20261003_THIRTYSIXTH_WAVE.md), five scoped
claims are newly VERIFIED/CLEAR and one generic rank lemma is REFUTED/CLEAR.
There is no new target graph, general nonexistence proof, or exclusion.

**As of:** {now}; source commit `{commit}`;
[checkpoint](../{out.relative_to(ROOT).as_posix()}/checkpoint.json) and
[frozen343-record ledger](../{out.relative_to(ROOT).as_posix()}/CLAIMS.yaml).
The previous report had337 material claims. Dates in evidence retain their
actual timezone; this title uses Japan time.

**Verdict:** target resolution UNKNOWN. No internally verified candidate target
resolution is pending external review. [PR3](https://github.com/ikuto32/conway-99-graph/pull/3)
remains draft. Repository state is separate from dated literature searches.

**Claim changes:** all337 prior claim/verification/artifact records are preserved.
The ledger has335 VERIFIED,3 CANDIDATE and5 REFUTED claims, all CLEAR.

| Claim | Status | Exact scope | Evidence |
| --- | --- | --- | --- |
{rows}

**Work completed:** the one frozen seed99032060 pilot has103 saved state files,
206 independently checked complete current/best graph objects and3 raw matrices.
The complete two-graph root census checked198 roots, with zero direct warm
roots. These populations overlap and are not summed. The unrestricted root7
GF2 screen checked11769 normalized rows and47076 scalar equations: all651
profiles compatible, zero excluded. The unrestricted root8 catalogue checked
all354560 augmentations,134594 local passes and20524 classes. Every coefficient
and four-RHS component of its23334-variable86434-row985893-term necessary
operator was independently reconstructed, including70837 marked and3828
product rows. No hypothetical target automorphism or prism absence was assumed.

**Coverage:** the frozen fixed-configuration proof union remains380 of792
literal branch configurations,412 unresolved. No new branch exclusion is added
here. This is branch count, not a fraction of all target graphs. Overall search
coverage: UNKNOWN; no validated denominator.

**Best result in the named pilot:** final current/best has exact edge residual
E_lambda=0 and nonedge residual E_mu=3608. F60=60E_lambda+E_mu and ordinary
E=E_lambda+E_mu both equal3608 for this object. All693 edges have one common
neighbor, but4934 ordered matrix entries fail the target identity. This is not
a global-best claim or a target graph. Its retained first lambda-zero snapshot
records step29380701 and E_mu4936; earliest selection over the entire sparse
history is UNKNOWN.

**Problems and limits:** rational/modular count feasibility is not graph
realization. The rejected generic codomain-isotropy inference has a complete
counterexample; a graph-specific rank<=72 bound remains UNKNOWN. The original
failed source/calibration versions and receipts are preserved. New evidence is
LOCAL_ONLY until separate immutable publication confirmation; wave36's937 new
artifact records have now separately passed PUBLIC confirmation, with no
material claim changes. See [publication addendum](AUDIT_20261003_WAVE36_PUBLICATION_CONFIRMED.md).

**Execution and next experiment:** this snapshot does not perform live process
observation. Completed pilot, catalogue, operator, parity and metadata receipts
are distinct from the new seed99032061 warm construction run. Consult its
actual process/terminal observations and frozen admission records. Finish the
authorized100million-proposal warm run and independently check every saved
object before promoting any improvement. The further unrestricted root8 GF2
raw endpoint has already passed its separate ROOT audit410e7e4d... with all651
profiles compatible/zero exclusions; its precise ledger binding is queued for
the next registration. No extra search is inferred from document editing.

**References:** [complete claim impact audit](../{REPORTS['impact'][0]}) preserves
all prior records and rejects21 strict corruptions without mathematical replay.
[Lossless model recovery](REPLAY_20261003_WAVE37_UNRESTRICTED_ROOTED8.md) documents
both large raw operators, independent streaming recovery and the new8-input
CI wrapper. Publication and external review remain separate.
'''
 (ROOT/'docs/RESEARCH_20261003_THIRTYSEVENTH_WAVE.md').write_text(text,encoding='utf8',newline='\n')
 print(json.dumps(dict(claim_records=343,status_counts=counts,checkpoint_sha256=sha(out/'checkpoint.json'))))


if __name__=='__main__':main()
