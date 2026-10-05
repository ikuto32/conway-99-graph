"""Bind independently reviewed finite GPU statements without editing the ledger."""
from datetime import datetime,timezone
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import yaml

ROOT=Path(__file__).resolve().parents[1]
AUDITS={
 'native':('acceleration/results/20260930_independent_review/factor_permutation_annealer_bound/summary.json','70c54735a3331f4bc9dff3ace2f5d1dd4bae49ec051f415a262538f9385b20b9'),
 'pilot':('acceleration/results/20260930_independent_review/factor_annealer_pilot/summary.json','97858230f5e777d601554e51184f0cb3b57ce6d39ed022a3850005b49c27fdd5'),
 'resume':('acceleration/results/20260930_independent_review/factor_resume_v3/summary.json','2c08fb8e4fb2c67179a9ad130cfe4109f43d4dd51719f3abd1e8694070d78ab6'),
 'availability':('acceleration/results/20260930_independent_review/factor_annealer_pilot_availability_correction/summary.json','7e70341364942f018684633a8ec4a032429e9c94ea2d7d1af4a2041f1896a634'),
}

def digest(p):
    with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False);timestamp=datetime.now(timezone.utc).isoformat();inputs={};reports={}
    for label,(path,h)in AUDITS.items():
        assert digest(ROOT/path)==h;inputs[path]=h;reports[label]=json.loads((ROOT/path).read_bytes())
    limitation_path='acceleration/results/20260930_independent_review/factor_resume_v3/v2_applicability_addendum.json';inputs[limitation_path]=digest(ROOT/limitation_path)
    limitation=json.loads((ROOT/limitation_path).read_bytes());assert limitation['status']=='INDEPENDENT_V2_PUBLIC_RESUME_LIMITATION_CHECKED'
    ledger=yaml.safe_load((ROOT/'CLAIMS.yaml').read_text(encoding='utf-8'));current={x['id']:x for x in ledger['claims']}
    fixture='C-SRG243-NONEMPTY-RESIDUAL-POSITIVE-CONTROL';shift='C-FIXED-TRIANGLE-JOINT-BINARY-FACTOR-CNF-ENCODING';prism='C-SIX-PRISM-COMPLETE-COLUMN-FACTOR-CNF'
    for name in(fixture,shift,prism):assert current[name]['revision']==1 and current[name]['status']=='VERIFIED'and current[name]['review_state']=='CLEAR'
    native='C-FACTOR-PERMUTATION-ANNEALER-CALIBRATION';pilot='C-FACTOR-PERMUTATION-ANNEALER-PILOT-SAVED-STATES';resume='C-FACTOR-PERMUTATION-PUBLIC-JSON-RESUME-CALIBRATION'
    def dep(name,relation):return dict(id=name,revision=1,relation=relation)
    def ref(label):path,h=AUDITS[label];return dict(path=path,sha256=h,availability='LOCAL_ONLY',retrieval='Existing local repository path; public immutable retrieval not yet confirmed.')
    def record(name,statement,scope,dependencies,labels,controls,limits,method):
        report=reports[labels[0]]
        return dict(id=name,revision=1,statement=statement,kind='empirical/engineering result',basis=['COMPUTED'],recommendation='VERIFIED',review_state='CLEAR',scope=dict(description=scope,unrestricted_target_applicability='No construction, exclusion or coverage conclusion for Conway99.'),assumptions=['No nontrivial target automorphism is assumed.','Exact frozen artifact identities and explicitly disclosed checking components.'],dependencies=dependencies,evidence=[ref(label)for label in labels],
          verification=[dict(claim_revision=1,verifier='/root/state_literature_audit independent checking path',method='independent_artifact_check',command_or_audit=AUDITS[labels[0]][0],timestamp=report['timestamp'],outcome='PASS',scope=scope,artifact_hashes={AUDITS[label][0]:AUDITS[label][1]for label in labels},checking_method=method,shared_components=['Independent Python column-accumulation trace checker and separately authored raw-factor bitset validator.','Python standard library; unchanged native CPU/GPU implementations share RNG/proposal/acceptance helpers, disclosed and checked independently on recorded controls.'])],controls=controls,limitations=limits,created_at=report['timestamp'],updated_at=timestamp,artifact_availability='LOCAL_ONLY',public_publication_confirmed=False,external_review=False,target_resolution=False)
    records=[]
    records.append(record(native,
      'On the frozen two n12 cores and known n20 fixture, the v2 native annealer passes all962 main/boundary proposal checks,320 additional native checkpoint replay checks and37 raw-object checks against the stated exact integer objective and saved finite acceptance decisions.',
      'Finite CPU/GPU/native split calibration only; this does not establish the v2 Python public --resume path, whose two subsequent attempts failed before native invocation.',
      [dep(fixture,'verification_dependency'),dep(shift,'uses_result'),dep(prism,'uses_result')],['native','resume'],
      dict(known_nonempty_SRG243=True,actual_native_bad_inputs=5,independent_corruptions=8,intended_core_corruptions=3,word_boundaries=[[63,64],[127,128]]),
      ['Finite floating-point acceptance agreement, no universal trajectory guarantee.','Authenticated build provenance is not a fresh diverse rebuild.','Native split replay did not test public Python disk-resume; the preserved v2 applicability addendum narrows the gate accordingly.','No performance, campaign, factor existence or target claim.'],
      'Independent full column-pair accumulation for every saved proposal, independent RNG/state reconstruction and separate literal raw-factor checks.'))
    records[-1]['evidence'].append(dict(path=limitation_path,sha256=inputs[limitation_path],availability='LOCAL_ONLY',retrieval='Existing local path; publication not yet confirmed.'))
    records.append(record(pilot,
      'For all six frozen pilot cases, the48 saved chunk-best factors and96 final-current plus96 final-best factors have valid declared permutation domains and exact recorded integer objective scores, with case minima164,282,390,184,310,444 and none zero.',
      'Saved-state correctness in two fixed n12 core domains;768 checkpoint-current and768 checkpoint-best scores also recomputed, while786432 saved proposal records are counted without campaign transition replay.',
      [dep(native,'verification_dependency'),dep(fixture,'verification_dependency'),dep(shift,'uses_result'),dep(prism,'uses_result')],['pilot','availability'],
      dict(known_nonempty_SRG243_score=0,valid_domain_corruption_score=24,malformed_controls=6),
      ['No campaign transition/RNG/acceptance replay; proposal record count is not a unique-factor count.','Caps are diagnostics and do not follow from the objective.','Positive scores establish no mathematical exclusion.','Original report PUBLIC metadata is superseded by the hash-bound LOCAL_ONLY correction; no public replay is claimed until a later publication binder.'],
      'Independent reconstruction from raw catalogs/permutations, full columnwise scores, separately authored bitset domain/Gram/cap checks, exact checkpoint and core bindings.'))
    records.append(record(resume,
      'The frozen v3 wrapper fixes the catalog tuple/list resume mismatch and passes fresh actual Python disk-resume23+41 versus64 controls on both two-chain cores, with all512 fresh transition checks and24 raw-object checks matching the independent references and the specified corruptions rejected.',
      'Exact source delta and bounded public calibration-mode disk-resume through the same run_chunks body; unchanged native algorithm retains its earlier finite gate, and future research outcomes require separate checks.',
      [dep(native,'verification_dependency'),dep(pilot,'verification_dependency'),dep(fixture,'verification_dependency')],['resume'],
      dict(actual_fresh_native_control_calls=6,actual_fresh_control_proposals=512,raw_final_best_objects=24,corrupted_public_resumes=5,additional_public_resource_or_gate_controls=3),
      ['Actual black-box CLI execution uses producer orchestration; independent expected scores/state checks import no producer implementation.','Two-chain finite calibration does not guarantee arbitrary future floating trajectories.','The old16-chain checkpoint domain/engine was checked; cooling results were not covered by this calibration.','No research retry was launched by this audit.'],
      'AST/source delta review, fresh actual CLI runs, independent exact proposal/state replay and literal raw-object validation; both successful split paths and actual malformed public paths checked.'))
    failure_id='C-FACTOR-PERMUTATION-V2-PUBLIC-RESUME-FAILURE'
    failure_record=record(failure_id,
      'Both saved v2 public-resume cooling attempts failed at exact problem equality because the live180 tuple catalog pairs per core differed in type from their JSON lists; neither attempt wrote a native chunk input or ran new GPU proposals, and both dependent stages were skipped.',
      'Exactly the two recorded v2 attempts and their two skipped dependent stages; a positive engineering failure finding, not a refutation of an unrecorded universal claim or the finite native calibration.',
      [dep(pilot,'verification_dependency')],['resume'],dict(exact_type_mismatches_each_core=180,changed_value_count=0,attempted_stages=2,failed_before_native=2,dependent_stages_skipped=2,new_native_proposals=0),
      ['No claim that native kernels or saved pilot scores were wrong.','No broader claim about all possible v2 inputs.'],
      'Independent source review and exact JSON/type comparison, raw failure/manifest inspection and proof that invoke follows the failing comparison.'))
    failure_record['evidence'].append(dict(path=limitation_path,sha256=inputs[limitation_path],availability='LOCAL_ONLY',retrieval='Existing local path; publication not yet confirmed.'));failure_record['optional_registration']=True;records.append(failure_record)
    path=Path(__file__).resolve();inputs[path.relative_to(ROOT).as_posix()]=digest(path)
    output=dict(status='INDEPENDENT_GPU_CLAIM_BINDINGS_PASS',timestamp=timestamp,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),records=records,inputs_sha256=inputs,ledger_changed=False,claim_recommendations=3,optional_exact_failure_claims=1,scope='This addendum supplies precise metadata for already completed independent checks. It does not broaden their statements or perform new research.')
    p=args.out/'summary.json'
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(output,f,indent=2);f.write('\n')
    print(json.dumps(dict(sha256=digest(p),claims=[r['id']for r in records])))

if __name__=='__main__':main()
