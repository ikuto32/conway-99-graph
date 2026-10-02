"""Dated progress from an exact ledger and saved runs; no live-process inference."""
import argparse,hashlib,json,subprocess,sys
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]
BASE='acceleration/results/20261002_wave33_registration02/CLAIMS.before.yaml'
PILOT='acceleration/results/20261002_independent_review/hypergraph_pilot_review01/best_object_evidence.json'
OBJECTS='acceleration/results/20261002_independent_review/hypergraph_pilot01/summary.json'
NATIVE='acceleration/results/20261002_hypergraph_pilot01/native/result.json'
PARITY='acceleration/results/20261002_rooted8_gf2_screen01/summary.json'
FULL='acceleration/results/20261002_rooted8_corner_certificates01/summary.json'
WEAKER='acceleration/results/20261002_rooted8_product_subset_v3_run01/summary.json'
UNION='acceleration/results/20261002_wave31_registration02/summary.json'

def need(ok,message):
 if not ok:raise ValueError(message)

def sha(path):
 with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--ledger-sha256',required=True)
 args=ap.parse_args();out=args.out.resolve();need(out.is_relative_to(ROOT),'workspace checkpoint');out.mkdir(parents=True,exist_ok=False)
 raw=(ROOT/'CLAIMS.yaml').read_bytes();need(hashlib.sha256(raw).hexdigest()==args.ledger_sha256,'exact frozen current ledger')
 ledger=yaml.safe_load(raw);before=yaml.safe_load((ROOT/BASE).read_bytes());old={c['id']:c for c in before['claims']};current={c['id']:c for c in ledger['claims']}
 need(len(old)==318 and all(current[cid]==claim for cid,claim in old.items()),'all318 previous material records unchanged')
 additions=[c for c in ledger['claims'] if c['id'] not in old]
 need(len(additions)==6 and all(c['status']=='VERIFIED' and c['review_state']=='CLEAR' and c['scope']['target_resolution']=='NONE' for c in additions),'six scoped independent claims only')
 paths=[PILOT,OBJECTS,NATIVE,PARITY,FULL,WEAKER,UNION]
 saved={name:json.loads((ROOT/name).read_bytes()) for name in paths}
 pilot=saved[PILOT];diagnostics=pilot['exact_diagnostics'];native=saved[NATIVE];full=saved[FULL];weaker=saved[WEAKER];parity=saved[PARITY];union=saved[UNION]
 need(pilot['status']=='INDEPENDENT_PILOT01_LITERAL_BEST_OBJECT_CHECKED' and diagnostics['exact_energy']==3034 and not pilot['target_resolution'],'independently checked finite graph only')
 need(native['stop_reason']=='REQUESTED_STEPS_COMPLETE' and native['proposals_this_invocation']==20000000,'native proposal counter scope')
 need(full['numerical_corner_attempts']==4 and full['exact_exclusions']==0 and full['exact_rational_primals']==0 and full['unknown']==210,'four full-model guides yield no exact verdict')
 need(weaker['numerical_corner_attempts']==4 and weaker['exact_corner_certificates']==0 and weaker['outcome_records_written']==210,'four weaker guides yield no exact verdict')
 need(parity['selected']==parity['completed']==parity['survivors']==210 and parity['rejected']==0,'producer parity result scope')
 counts=dict(Counter(c['status'] for c in ledger['claims']));review=dict(Counter(c['review_state'] for c in ledger['claims']))
 now=datetime.now(timezone.utc).isoformat();commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 checkpoint=dict(timestamp=now,source_commit=commit,command=[sys.executable,*sys.argv],cwd=str(ROOT),source_sha256=sha(Path(__file__)),registry_sha256=args.ledger_sha256,previous_report='docs/RESEARCH_20261002_THIRTYSECOND_WAVE.md',claim_records=len(ledger['claims']),status_counts=counts,review_counts=review,verified_changes=[dict(id=c['id'],revision=c['revision'],statement=c['statement'],scope=c['scope'],evidence=c['evidence']) for c in additions],target_resolution=ledger['target']['status'],external_review=ledger['target']['external_review'],literal_population=union['literal_population'],literal_exclusions=union['distinct_literal_exclusions'],unresolved_literal_cases=union['unresolved_literal_cases'],overall_search_coverage='UNKNOWN; no validated denominator.',pilot=dict(independent_exact_diagnostics=diagnostics,native_reported_proposals=native['proposals_this_invocation'],native_elapsed_seconds=native['elapsed_seconds'],full_trajectory_independently_replayed=False),numerical_runs=dict(full_model_corner_attempts=4,weaker_subset_corner_attempts=4,full_profile_records=210,weaker_profile_records=210,exact_certificates=0),parity=dict(producer_report=PARITY,status='CANDIDATE; independent primal/rank checking pending',producer_reported_rank=parity['exact_gf2_rank'],profiles=210,exclusions=0),current_execution_state='UNKNOWN; this generator does not observe live processes.',input_hashes={name:sha(ROOT/name) for name in [BASE,*paths]},skipped_checks=['No mathematical replay by this generator.','No full historical transitive artifact audit.','No whole20million-step independent trajectory replay.','No independent GF2 rank verification.'])
 (out/'CLAIMS.yaml').write_bytes(raw)
 with (out/'checkpoint.json').open('x',encoding='utf8',newline='\n') as stream:json.dump(checkpoint,stream,indent=2);stream.write('\n')
 rows='\n'.join(f"| {c['id']} r{c['revision']} | {c['scope']['description']} [Audit](../{c['verification'][0]['command_or_audit']}). |" for c in additions)
 text=f'''# Thirty-third research milestone, 2026-10-02

Since the [thirty-second milestone](RESEARCH_20261002_THIRTYSECOND_WAVE.md), six precise scoped revisions are newly VERIFIED/CLEAR. No target graph, general proof or new graph exclusion is added. The complete necessary root7/root8 operators and one saved non-SRG construction object now have independent checks.

**As of:** {now}; source commit `{commit}`; [checkpoint](../{out.relative_to(ROOT).as_posix()}/checkpoint.json); [frozen ledger](../{out.relative_to(ROOT).as_posix()}/CLAIMS.yaml). Prior published baseline:318 records at that source commit.

**Verdict:** target resolution UNKNOWN. No independently validated target99 graph or general nonexistence proof exists in this repository. No target-resolution artifact has been submitted for external review. This dated repository verdict is separate from literature coverage. [PR3](https://github.com/ikuto32/conway-99-graph/pull/3) remains draft; research authorization remains active.

**Verified changes:** all318 prior material records retain their statements and checks. New revisions are independently derived or checked within these exact scopes:

| Claim | Checked scope |
| --- | --- |
{rows}

**Work completed:** the root7 operator has2766 variables,11749 rows and86129 coefficients. Four exact nonnegative integer corners yield210 independently checked rational interpolation witnesses; exactly four supplied vectors are integral, and206 are nonintegral. That proves neither integer infeasibility nor graph realizability at the other points. The complete conditional root8 catalogue has20253 flag classes; every352000 parent augmentation and all free-label images were checked. All23019 variables,85874 rows and968172 coefficients of the necessary root8 operator were independently reconstructed. Global induced-prism absence remains UNKNOWN. Free-label normalization assumes no target automorphism.

The declared construction pilot completed a native-reported20,000,000 proposals in{native['elapsed_seconds']:.3f}s. Independent review checked22 saved states/44 current-best objects,2067 anchored sparse proposals and every final matrix entry.180 sparse gap records are unreplayed; the full native trajectory and20million counter are not independently certified. The missing producer current.adj was exactly reconstructed from final triples; the raw best.adj is available. All these scope limits remain in the claim.

**Coverage:** {len(ledger['claims'])} root claim records: {counts['VERIFIED']} VERIFIED/CLEAR, {counts['CANDIDATE']} CANDIDATE/CLEAR and {counts['REFUTED']} REFUTED/CLEAR. The frozen fixed-support campaign remains at{union['distinct_literal_exclusions']} independently checked literal cases among{union['literal_population']}, leaving{union['unresolved_literal_cases']} unresolved. These are representative cases, not graphs or equal work units. Overall search coverage: UNKNOWN; no validated denominator.

**Best result:** the pilot graph is99-vertex14-regular, the point graph of231 linear triples with point degree7. For objective `SRG_SQUARED_PAIR_RESIDUAL_V1`, defined by `sum_(i<j)(CN(i,j)+A[i,j]-2)^2`, exact residual E=3034=427 adjacent+2607 nonadjacent. Lower is better within this objective and domain; this graph fails the target identity at4820 ordered off-diagonal entries. It supplies no exclusion. Future weighted objectives must be compared separately.

**Problems:** four full-model numerical corner attempts produced zero exact primals or Farkas certificates and210 UNKNOWN outcome records. The old field `completed_certificate_evaluations:210` describes written outcomes, not210 solver attempts; its [interpretation](../acceleration/results/20261002_rooted8_corner_certificates01/interpretation.json) preserves the original report. Two numerically infeasible corners yielded no stored checkable ray. Native guide limits overshot and implicit dual-ray requests consumed additional phases; all were contained by the original invocation deadline. The new weaker15578-row diagnostic reached four numerical optima, but every frozen exact grid lift failed: zero exact certificates,210 UNKNOWN outcomes. Saved bases/supports permit exact reconstruction without rerunning those guides. The producer parity screen reports rank22044 and210 survivors; independent exact primal checking is pending, so no rank claim is promoted. Failed setup, numerical lifts and registrar versions remain evidence.

**Execution:** pilot, full-corner, parity and weaker-corner invocations are completed with saved artifacts and observed contained shutdown receipts. This milestone is not a live monitor. Other commands require fresh process observations, and reaching this checkpoint does not stop authorized research.

**Next experiment:** independently gate the changed weighted construction engine, then run a frozen weighted pilot from the saved best triple system. In parallel, use saved weaker-model supports/bases for exact sparse reconstruction and produce independently checkable binary primals for all affine RHS columns. Any exact structural certificate still needs complete literal checking and its declared conditional necessity.

**References:** [source commit](https://github.com/ikuto32/conway-99-graph/commit/{commit}), [draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3), [compute policy](COMPUTE_POLICY.md), [four-file lossless model manifest](../acceleration/results/20261002_wave33_model_package01/manifest.json), [full independent reconstruction manifest](../acceleration/results/20261002_wave33_reconstruction_package01/manifest.json). Package recovery and immutable public availability require separate receipts. Schema/CI checks are engineering controls, not mathematical verification.
'''
 with (ROOT/'docs/RESEARCH_20261002_THIRTYTHIRD_WAVE.md').open('x',encoding='utf8',newline='\n') as stream:stream.write(text)
 print(json.dumps(dict(status='DATED_WAVE33_MILESTONE_GENERATED',claims=len(ledger['claims']),new_claims=len(additions),target_resolution=ledger['target']['status'])))

if __name__=='__main__':main()
