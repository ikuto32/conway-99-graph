"""Generate a bounded dated milestone from the ledger and frozen saved records.

This reports exact registered scopes and dated execution receipts. It is neither
mathematical verification nor a live process monitor.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib, json, subprocess, sys
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]
BASE='acceleration/results/20261002_wave31_registration02/CLAIMS.after.yaml'
NATIVE='acceleration/results/20261002_drat_derivative_native01/summary.json'
NATIVE_CASE='acceleration/results/20261002_drat_derivative_native01/instance/summary.json'
SUPERVISION='acceleration/results/20261002_drat_derivative_native_supervision01/summary.json'
OUTCOME='acceleration/results/20261002_independent_review/drat_derivative_outcome01/summary.json'
RECOVERY='acceleration/results/20261002_independent_review/batch05_recovery01/summary.json'
PACKAGE='acceleration/results/20261002_batch05_raw_package02/manifest.json'
UNION='acceleration/results/20261002_wave31_registration02/summary.json'


def need(ok,why):
    if not ok:raise ValueError(why)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--ledger-sha256',required=True)
    args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    raw=(ROOT/'CLAIMS.yaml').read_bytes()
    need(hashlib.sha256(raw).hexdigest()==args.ledger_sha256,'exact milestone ledger')
    ledger=yaml.safe_load(raw);old=yaml.safe_load((ROOT/BASE).read_bytes())
    oldclaims={c['id']:c for c in old['claims']}
    need(all(c==next(x for x in ledger['claims'] if x['id']==cid) for cid,c in oldclaims.items()),
         'all previous312 material claim records retained exactly')
    additions=[c for c in ledger['claims'] if c['id'] not in oldclaims]
    need(all(c['status']=='VERIFIED' and c['review_state']=='CLEAR' and c['scope']['target_resolution']=='NONE'
             for c in additions),'all additions are exact scoped checked revisions without resolution')
    saved={name:json.loads((ROOT/name).read_bytes()) for name in [NATIVE,NATIVE_CASE,SUPERVISION,OUTCOME,RECOVERY,PACKAGE,UNION]}
    native,case,supervisor=saved[NATIVE],saved[NATIVE_CASE],saved[SUPERVISION]
    need(native['execution_state']=='STOPPED' and case['raw_outcome']=='UNKNOWN'
         and case['raw_proof']['complete_proof'] is False,'preserved unfinished native result')
    need(supervisor['cleanup']['reaped'] and supervisor['cleanup']['job_active_zero_observed']
         and supervisor['cleanup']['process_group_live_pids']==[],'dated contained shutdown receipt')
    outcome=saved[OUTCOME];recovery=saved[RECOVERY];package=saved[PACKAGE]
    need(outcome['status']=='INDEPENDENT_POLICY_NATIVE_SINGLE_V2_OUTCOME_AUDIT_PASS'
         and outcome['case_records'][0]['verification_outcome']=='UNKNOWN_NO_EXCLUSION',
         'independently authenticated unfinished native outcome')
    need((recovery['raw_artifacts'],recovery['gzip_parts'],recovery['case_count'])==(934,936,64)
         and recovery['raw_artifacts']==package['raw_artifacts'] and recovery['gzip_parts']==package['gzip_parts'],
         'exact direct recovery populations')
    union=saved[UNION];counts=dict(Counter(c['status'] for c in ledger['claims']))
    now=datetime.now(timezone.utc).isoformat();commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    checkpoint=dict(timestamp=now,source_commit=commit,command=[sys.executable,*sys.argv],cwd=str(ROOT),
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),registry_sha256=args.ledger_sha256,
        previous_report='docs/RESEARCH_20261002_THIRTYFIRST_WAVE.md',claim_records=len(ledger['claims']),status_counts=counts,
        verified_changes=[dict(id=c['id'],revision=c['revision'],statement=c['statement'],scope=c['scope'],evidence=c['evidence']) for c in additions],
        target_resolution=ledger['target']['status'],external_review=ledger['target']['external_review'],
        literal_population=union['literal_population'],literal_exclusions=union['distinct_literal_exclusions'],
        unresolved_literal_cases=union['unresolved_literal_cases'],overall_search_coverage='UNKNOWN; no validated denominator.',
        completed_native=dict(raw_outcome='UNKNOWN',elapsed_seconds=native['producer_elapsed_seconds'],
             execution_state='STOPPED',raw_partial_proof=case['raw_proof'],unmet_requirements=case['unmet_requirements']),
        current_execution_state='UNKNOWN; this metadata generator is not a live process observer.',
        input_hashes={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in [BASE,*saved]},
        direct_batch05_recovery='Independently checked local direct closure; public availability must be confirmed separately.',
        skipped_checks=['No mathematical replay by this generator.','No fresh complete historical transitive artifact audit.'])
    (out/'CLAIMS.yaml').write_bytes(raw)
    (out/'checkpoint.json').write_text(json.dumps(checkpoint,indent=2)+'\n',encoding='utf8',newline='\n')
    rows=[]
    for c in additions:
        audit=c['verification'][0]['command_or_audit']
        rows.append(f"| {c['id']} r{c['revision']} | {c['scope']['description']} [Audit](../{audit}). |")
    text=f'''# Thirty-second research milestone, 2026-10-02

Since the [thirty-first milestone](RESEARCH_20261002_THIRTYFIRST_WAVE.md), {len(additions)} exact scoped revisions are newly VERIFIED/CLEAR. No new graph exclusion or target resolution is added. The batch05 direct raw package now has an independent byte-recovery check; immutable public availability is a separate publication step.

**As of:** {now}; source commit `{commit}`; [checkpoint](../{out.relative_to(ROOT).as_posix()}/checkpoint.json); [frozen ledger](../{out.relative_to(ROOT).as_posix()}/CLAIMS.yaml); previous report linked above.

**Verdict:** target resolution UNKNOWN. This repository has no independently validated 99-vertex target graph or general nonexistence proof. No target-resolution artifact has been submitted for external review. This is a dated repository verdict, not a claim about the world's literature. [PR3](https://github.com/ikuto32/conway-99-graph/pull/3) remains draft.

**Verified changes:** all additions below are revision 1; every preceding 312 claim record retains its exact statement and verification record.

| Claim | Exact checked scope |
| --- | --- |
{chr(10).join(rows)}

**Work completed:** complete ordered-pair rooted5 necessary identities and actual rank-one moment consequences; a conditional ordered-edge rooted6 rigidity derivation; exact unrestricted nonedge operator kernels and a conditional 210-profile integer domain; complete rooted7 catalogue coverage; complete literal partial-trace state transformation. Every scope remains separate. Prism absence is UNKNOWN. The state transform establishes bytes and active clauses only; its retained partial prefix has no complete RAT/equivalence certificate.

One declared native continuation attempted the derivative formula. The solver reached its 1,800-second wall allocation with exit 124 and raw UNKNOWN. The outer invocation completed in {supervisor['elapsed_seconds']:.3f} seconds including shutdown and transfer, with its Linux process group observed empty. The saved partial trace has {case['raw_proof']['bytes']:,} bytes and hash `{case['raw_proof']['sha256']}`. It is LOCAL_ONLY and incomplete. This work was **not completed within the allocated budget**; unmet requirements are a validated full graph or complete original-instance proof and coverage review. [Case record](../{NATIVE_CASE}), [independent outcome check](../{OUTCOME}), [outer shutdown receipt](../{SUPERVISION}).

The direct batch05 package contains {recovery['raw_artifacts']} raw members in {recovery['gzip_parts']} gzip parts. Independent recovery checks every raw byte against direct native/audit pins and every gzip identity. This includes all {recovery['case_count']} formulas, models, scopes and complete proofs plus direct metadata and sources; it does not include the entire 20,040-input historical transitive gate closure. [Recovery audit](../{RECOVERY}), [lossless manifest](../{PACKAGE}). Public replay instructions and availability must refer to an authenticated immutable commit; local recovery alone establishes no public availability.

**Coverage:** {len(ledger['claims'])} claim records: {counts['VERIFIED']} VERIFIED/CLEAR, {counts['CANDIDATE']} CANDIDATE/CLEAR and {counts['REFUTED']} REFUTED/CLEAR. The disjoint literal campaign union is unchanged at {union['distinct_literal_exclusions']} checked cases among {union['literal_population']} fixed-support representatives, leaving {union['unresolved_literal_cases']} unresolved. This counts literal cases, not graphs or runtime. Overall search coverage: UNKNOWN; no validated denominator.

**Best result:** no comparable target-graph metric is newly established in this cutoff. The exact necessary structural domains admit recorded profiles; they are not graph realizations. The previous selected order-eight endpoint witness and fixed-support bounds remain as scoped in their claims. Counts of verified engineering or mathematical identities measure ledger contents, not a fraction of Conway-99 solved.

**Problems:** the complete original-instance nonexistence certificate is absent. Global prism absence remains unestablished. Raw restart preprocessing uses a precisely checked syntactic profile but does not certify the old partial DRAT prefix or SAT model reconstruction. Numerical root7 LP guides and failed rational lifts remain CANDIDATE/UNKNOWN outside these claims. Failed producer/setup/checker versions remain preserved. The stored reports do not claim external peer review or independent compiler/formal proof verification.

**Execution:** the dated native continuation is STOPPED and its checkpoints are saved. This milestone is not a live monitor and does not stop the authorized research. Other processes require fresh observations.

**Next experiment:** scaled LP guides and exact sparse certificate reconstruction for all 210 conditional profiles, followed by independent marked-extension/reroot model verification for any meaningful exclusion. Exact modular consistency screens over GF2 and GF3 found no exclusion. In parallel, independently verify complete engineering move/scoring/resume controls for a 99-point, 7-regular linear triple-system construction search before its first scientific run. Such moves assume no target automorphism; move-space coverage remains UNKNOWN.

**References:** [source commit](https://github.com/ikuto32/conway-99-graph/commit/{commit}), [draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3), [compute policy](COMPUTE_POLICY.md), [rooted5 derivation](DERIVATION_20261002_ROOTED5_MOMENT_RIGIDITY.md), [dated literature search](LITERATURE_20261002_STRUCTURAL_REFRESH.md). Schema checks and metadata counts are engineering controls, not mathematical verification.
'''
    destination=ROOT/'docs/RESEARCH_20261002_THIRTYSECOND_WAVE.md'
    with destination.open('x',encoding='utf8',newline='\n') as stream:stream.write(text)
    print(json.dumps(dict(status='MILESTONE_METADATA_GENERATED',claims=len(ledger['claims']),new_claims=len(additions),target_resolution=ledger['target']['status'])))


if __name__=='__main__':main()
