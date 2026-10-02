"""Fixed353 claim milestone/explicit closure; no staging or science."""
import argparse,hashlib,json,subprocess,sys
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path,PurePosixPath
from command_deadline import CommandDeadline
import validate_claims as registry

ROOT=Path(__file__).resolve().parents[1]
LEDGER='b2796504a736ef16872ee36812d3b8ddb6446d0ea28d4883525f9ab9a3dd5679'
BEFORE='acceleration/results/20261003_wave39_registration01/CLAIMS.before.yaml'
BEFORE_SHA='ff94b87187d712bc2fce166b8afffaa3e2155db9fbdf8a4b3179b1f3fe2e304a'
IMPACT='acceleration/results/20261003_independent_review/wave39_transition02/summary.json'
IMPACT_SHA='22777593552926a6f50f8034cfbfd20191fe792990d02afba3c4c1b31e51ec07'
INDEX='68b695ba680915be542d08a9522a2a3acd329f8fd05e471b35ae27a9e0523152'
IDS=['C-UNRESTRICTED-TRIANGLE-INCIDENCE-LOW-WEIGHT-IMAGE-COUNTS','C-UNRESTRICTED-TRIANGLE-INCIDENCE-BINARY-RANK-LOWER85','C-HYPERGRAPH-WEIGHT60-WARM01-FIXED-V2-TWO-LINE-CENSUS']
SPEC='acceleration/record_20261003_wave39_milestone_v1_spec.md'
DOCS=['README.md','ACTIVE_RESEARCH.md','docs/RESEARCH_MAP.md','docs/REPRODUCING.md']
MILESTONE='docs/RESEARCH_20261003_THIRTYNINTH_WAVE.md'
REPORTS={
 'low':('acceleration/results/20261003_independent_review/incidence_low_weights01/summary.json','626e405502f6054483d7bc722610e83788c663d50d016f34a48b248edea4c2cd'),
 'rank':('acceleration/results/20261003_independent_review/triangle_kernel_low_weight_lp_full01/summary.json','1037b20164daf037c7544d316032b15b3fcdc6413ee3b8f7a7b4d10ad9e80fd6'),
 'census':('acceleration/results/20261003_independent_review/two_line_full01/summary.json','1d3cecc2fd8d3e689966a334af59a9af7d0a2e8c66b356b98484aef3ed79e589'),
 'public_receipt':('acceleration/results/20261003_wave38_public_confirmation01/receipt.json','86bf29a5baf14189f600e29065c2024d3ab92f9700c652b1d87b1048ccbb176b'),
 'public_audit':('acceleration/results/20261003_independent_review/wave38_availability01/summary.json','8202671a7c63b69fb5270a6a64904ffe606a346dcd65fb87cefa4b45472597a8')}
ARCHIVE='external_conway99_research/attempts/wave102-prism-incidence-code/derivation.md'
ARCHIVE_SHA='df8841bee7f23b444186ab65947f77865ffb243363967dd56340207628f00c6f'
ARCHIVE_COMMIT='85e705cc6c2a14d123120c93a847e30aaab1789e'
ARCHIVE_REPOSITORY='https://github.com/YesterdaysLemon/conway-99-research'
PACKAGES={
 'acceleration/results/20261002_wave33_model_package01/manifest.json':'c3efa198c5f48eddb5ead69a4bb130a3dc55567bb298856143c6fb62eb0e0145',
 'acceleration/results/20261002_wave33_reconstruction_package01/manifest.json':'f639431b7ea9ce0f1500ea48b002629d2523271eead700217dd512e8ade66989',
 'acceleration/results/20261003_wave36_coupling_package01/manifest.json':'38f641ec21ec3d1d617515e8b3e578e098886863f7016ad640ac1906e8b0988f',
 'acceleration/results/20261003_wave37_rooted8_package01/manifest.json':'ea48c30dfa68fe70bad17edbfd3697d8a2dcf28f9ab24b63d0d66895e7eb9b14'}
EXTRA_FILES=['.gitattributes','docs/RESEARCH_20261003_THIRTYEIGHTH_WAVE.md',
 'acceleration/register_20261003_bound_claims_v13.py','acceleration/register_20261003_bound_claims_v13_spec.md','acceleration/register_20261003_bound_claims_v14.py','acceleration/register_20261003_bound_claims_v14_spec.md',
 'acceleration/calibrate_20261003_registrar_v13_helpers_v1.py','acceleration/calibrate_20261003_registrar_v13_helpers_v1_spec.md','acceleration/calibrate_20261003_registrar_v13_helpers_v2.py','acceleration/calibrate_20261003_registrar_v13_helpers_v2_spec.md','acceleration/calibrate_20261003_registrar_v14_helpers_v1.py','acceleration/calibrate_20261003_registrar_v14_helpers_v1_spec.md',
 'acceleration/audit_20261003_registrar_v13_engineering_v1.py','acceleration/audit_20261003_registrar_v13_engineering_v1_spec.md','acceleration/audit_20261003_registrar_v14_engineering_v1.py','acceleration/audit_20261003_registrar_v14_engineering_v1_spec.md','acceleration/audit_20261003_registrar_v14_engineering_v2.py','acceleration/audit_20261003_registrar_v14_engineering_v2_spec.md',
 'acceleration/audit_20261003_wave39_transition_v1.py','acceleration/audit_20261003_wave39_transition_v1_spec.md','acceleration/audit_20261003_wave39_transition_v2.py','acceleration/audit_20261003_wave39_transition_v2_spec.md',
 'acceleration/confirm_20261003_wave38_publication_v1.py','acceleration/confirm_20261003_wave38_publication_v1_spec.md','acceleration/audit_20261003_wave38_availability_v1.py','acceleration/audit_20261003_wave38_availability_v1_spec.md']
EXTRA_ROOTS=[
 'acceleration/results/20261003_registrar_v13_prelaunch_veto01',
 'acceleration/results/20261003_registrar_v13_helpers01','acceleration/results/20261003_registrar_v13_helpers02','acceleration/results/20261003_registrar_v13_helpers_supervision01','acceleration/results/20261003_registrar_v13_helpers_supervision02',
 'acceleration/results/20261003_registrar_v14_helpers01','acceleration/results/20261003_registrar_v14_helpers_supervision01',
 'acceleration/results/20261003_independent_review/registrar_v14_engineering02','acceleration/results/20261003_independent_review/registrar_v14_engineering_supervision02',
 'acceleration/results/20261003_independent_review/wave39_transition_calibration01','acceleration/results/20261003_independent_review/wave39_transition_calibration_supervision01','acceleration/results/20261003_independent_review/wave39_transition_calibration02','acceleration/results/20261003_independent_review/wave39_transition_calibration_supervision02','acceleration/results/20261003_independent_review/wave39_transition02','acceleration/results/20261003_independent_review/wave39_transition_supervision02',
 'acceleration/results/20261003_wave39_registration01','acceleration/results/20261003_wave39_registration_supervision01',
 'acceleration/results/20261003_wave38_public_confirmation01','acceleration/results/20261003_wave38_public_confirmation_supervision01',
 'acceleration/results/20261003_independent_review/wave38_availability01','acceleration/results/20261003_independent_review/wave38_availability_supervision01','acceleration/results/20261003_independent_review/wave38_availability_calibration01','acceleration/results/20261003_independent_review/wave38_availability_calibration_supervision01']
DENY=['seven_weight','incidence_low_weight_lp_v2','divisible4','kernel_containment','projection_hull','kernel_self_orthogonal','incidence_kernel_nonzero','two_line_neighbor','neutral_census','root_start','root_focused','rooted8_unrestricted_lp','rooted8_unrestricted_corner']
def need(ok,why):
 if not ok:raise ValueError(why)
def sha(path):
 with path.open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def save(path,value):
 with path.open('x',encoding='utf8',newline='\n')as stream:json.dump(value,stream,indent=2);stream.write('\n')
def bounded(name):
 need(type(name)is str and name and not any(c in name for c in'\\\r\n\0'),'LITERAL_RELATIVE_PATH:'+repr(name));p=PurePosixPath(name);need(not p.is_absolute()and'..'not in p.parts and not name.startswith('.git/'),'WORKSPACE_RELATIVE_PATH:'+repr(name));need(name==ARCHIVE or name.startswith(('acceleration/','docs/'))or name in DOCS+['CLAIMS.yaml','pyproject.toml','uv.lock','.gitattributes','.github/workflows/claims.yml'],'RESEARCH_NAMESPACE:'+repr(name));need(not any(term in name.lower()for term in DENY),'EXCLUDED_LATER_SCIENCE:'+repr(name));need('/build/'not in name and'/recovered/'not in name,'EXCLUDED_DUPLICATE_BUILD:'+repr(name));path=(ROOT/name).resolve();need(path.is_relative_to(ROOT),'RESOLVED_BOUNDARY:'+repr(name));return path
def disposition(name,identity):
 if name=='.git/index':need(identity==INDEX,'HISTORICAL_INDEX_OBSERVATION_HASH:'+repr(name));return'OMIT_READONLY_INDEX'
 if name==ARCHIVE:need(identity==ARCHIVE_SHA,'EXACT_PINNED_ARCHIVE_HASH:'+repr(name));return'REFERENCE_PINNED_ARCHIVE'
 bounded(name);return'DIRECT'
def archive_metadata(name,identity,repository,commit,external_path):
 need(name==ARCHIVE and identity==ARCHIVE_SHA and repository==ARCHIVE_REPOSITORY and commit==ARCHIVE_COMMIT and external_path==ARCHIVE.split('/',1)[1],'EXACT_PINNED_ARCHIVE_REFERENCE')
 return dict(path=name,sha256=identity,repository=repository,commit=commit,external_path=external_path,retrieval=repository+'/blob/'+commit+'/'+external_path,reason='Exact historical source reference; no submodule-content staging or new historical verification.')
def calibrate_paths(evidence,impact):
 controls=[]
 for name,identity,expected in[('CLAIMS.yaml',LEDGER,'DIRECT'),('.gitattributes','f'*64,'DIRECT'),('docs/REPRODUCING.md','f'*64,'DIRECT'),('.git/index',INDEX,'OMIT_READONLY_INDEX'),(ARCHIVE,ARCHIVE_SHA,'REFERENCE_PINNED_ARCHIVE')]:need(disposition(name,identity)==expected,'POSITIVE_PATH_CONTROL');controls.append(dict(path=name,outcome=expected))
 for name,identity,stage in[('.git/index','0'*64,'HISTORICAL_INDEX_OBSERVATION_HASH'),('.git/config','f'*64,'WORKSPACE_RELATIVE_PATH'),('../CLAIMS.yaml','f'*64,'WORKSPACE_RELATIVE_PATH'),('docs/../a.md','f'*64,'WORKSPACE_RELATIVE_PATH'),('/tmp/private','f'*64,'WORKSPACE_RELATIVE_PATH'),('C:/private/file','f'*64,'RESEARCH_NAMESPACE'),('docs\\a.md','f'*64,'LITERAL_RELATIVE_PATH'),('docs/a\n.md','f'*64,'LITERAL_RELATIVE_PATH'),(ARCHIVE,'f'*64,'EXACT_PINNED_ARCHIVE_HASH'),('external_conway99_research/CLAIMS.yaml','f'*64,'RESEARCH_NAMESPACE'),('acceleration/build/x','f'*64,'EXCLUDED_DUPLICATE_BUILD'),('acceleration/recovered/x','f'*64,'EXCLUDED_DUPLICATE_BUILD'),('acceleration/theory_20261003_incidence_low_weight_lp_v2.py','f'*64,'EXCLUDED_LATER_SCIENCE'),('docs/CANDIDATE_20261003_TRIANGLE_KERNEL_SELF_ORTHOGONAL_V1.md','f'*64,'EXCLUDED_LATER_SCIENCE'),('acceleration/results/20261003_two_line_neighbor01/summary.json','f'*64,'EXCLUDED_LATER_SCIENCE'),('acceleration/hypergraph_root_focused_anneal_20261003_v1.cpp','f'*64,'EXCLUDED_LATER_SCIENCE')]:
  try:disposition(name,identity)
  except ValueError as error:need(str(error).startswith(stage+':')and repr(name)in str(error),'EXACT_REJECTION_STAGE');controls.append(dict(path=name,outcome='REJECTED',diagnostic=str(error)))
  else:raise ValueError('FALSE_PATH_ACCEPT:'+name)
 archive_metadata(ARCHIVE,ARCHIVE_SHA,ARCHIVE_REPOSITORY,ARCHIVE_COMMIT,ARCHIVE.split('/',1)[1])
 for label,repo,commit,path in[('repository','https://github.com/untrusted/other',ARCHIVE_COMMIT,ARCHIVE.split('/',1)[1]),('commit',ARCHIVE_REPOSITORY,'0'*40,ARCHIVE.split('/',1)[1]),('external_path',ARCHIVE_REPOSITORY,ARCHIVE_COMMIT,'CLAIMS.yaml')]:
  try:archive_metadata(ARCHIVE,ARCHIVE_SHA,repo,commit,path)
  except ValueError as error:need(str(error)=='EXACT_PINNED_ARCHIVE_REFERENCE','EXACT_ARCHIVE_CONTROL_STAGE');controls.append(dict(label='archive_'+label,outcome='REJECTED',diagnostic=str(error)))
  else:raise ValueError('FALSE_ARCHIVE_REFERENCE_ACCEPT')
 inventory=[]
 for origin,records in[('three_claim_evidence',evidence),('actual_impact_inputs',impact['inputs_sha256'])]:
  for name,identity in sorted(records.items()):outcome=disposition(name,identity);need(outcome=='OMIT_READONLY_INDEX'or bounded(name).is_file(),'LITERAL_INPUT_EXISTS:'+name);inventory.append(dict(origin=origin,path=name,sha256=identity,disposition=outcome))
 return controls,inventory
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['calibrate','prepare'],required=True);ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--source-sha256',required=True);ap.add_argument('--protocol-sha256',required=True);ap.add_argument('--calibration',type=Path);ap.add_argument('--calibration-sha256');ap.add_argument('--write-current-docs',action='store_true');args=ap.parse_args();deadline=CommandDeadline(args.seconds,allocation_reason='Fixed353 metadata/explicit closure; prior350 generation8.8s/eight367MB identities justify100worker20reserve; no science/index/packaging');out=args.out.resolve();need(out.is_relative_to(ROOT),'OUTPUT_BOUNDARY');out.mkdir(parents=True,exist_ok=False);pins={};origins=defaultdict(set);expected={};omitted=[];docs_written=[]
 def pin(name,identity=None):
  need(deadline.status()['remaining_seconds']>20,'NOT_COMPLETED_WITHIN_ALLOCATION');value=sha(bounded(name));need(identity is None or value==identity,'EXACT_INPUT_HASH:'+name);need(name not in pins or pins[name]==value,'FROZEN_INPUT_UNCHANGED:'+name);pins[name]=value;return value
 def add(name,origin,identity=None):
  mode=disposition(name,identity if identity is not None else ARCHIVE_SHA if name==ARCHIVE else'')
  need(mode!='OMIT_READONLY_INDEX','NO_INDEX_PAYLOAD');origins[name].add(origin)
  if identity is not None:need(name not in expected or expected[name]==identity,'CONSISTENT_EXPECTED_HASH');expected[name]=identity
 def read(name,identity):pin(name,identity);return json.loads(bounded(name).read_bytes())
 try:
  pin(Path(__file__).relative_to(ROOT).as_posix(),args.source_sha256);pin(SPEC,args.protocol_sha256);index_before=sha(ROOT/'.git/index');need(index_before==INDEX,'EXACT_LIVE_INDEX');raw=(ROOT/'CLAIMS.yaml').read_bytes();pin('CLAIMS.yaml',LEDGER);pin(BEFORE,BEFORE_SHA);current=registry.read_ledger(ROOT/'CLAIMS.yaml');before=registry.read_ledger(ROOT/BEFORE);new=current['claims'][350:];need(len(before['claims'])==350 and len(current['claims'])==353 and current['claims'][:350]==before['claims']and[c['id']for c in new]==IDS and current['target']==before['target']and current['target']['status']=='UNKNOWN','EXACT350_TO353_CUTOFF');counts=dict(Counter(c['status']for c in current['claims']));need(counts=={'VERIFIED':345,'CANDIDATE':3,'REFUTED':5}and all(c['review_state']=='CLEAR'for c in current['claims']),'EXACT353_COUNTS');impact=read(IMPACT,IMPACT_SHA);need(impact['status']=='INDEPENDENT_WAVE39_EXACT350_TO353_TRANSITION_V2_PASS'and impact['current_claims']==353 and impact['new_claim_ids']==IDS and impact['new_finite_exclusion_kind_claims']==1 and impact['new_unrestricted_exclusion_claims']==0,'EXACT_INDEPENDENT_IMPACT')
  artifacts={a['id']:a for a in current['artifacts']};evidence={}
  for claim in new:
   for aid in claim['evidence']:
    artifact=artifacts[aid];name,identity=artifact['path'],artifact['sha256'];need(name is not None and(name not in evidence or evidence[name]==identity),'CONSISTENT_CLAIM_EVIDENCE');evidence[name]=identity
  controls,inventory=calibrate_paths(evidence,impact)
  for name in EXTRA_FILES:need(bounded(name).is_file(),'EXPLICIT_EXTRA_FILE_EXISTS:'+name)
  for name in EXTRA_ROOTS:need(bounded(name).is_dir(),'EXPLICIT_EXTRA_ROOT_EXISTS:'+name)
  save(out/'path_controls.json',controls);save(out/'selected_path_inventory.json',inventory)
  if args.mode=='calibrate':need(not args.write_current_docs,'CALIBRATION_DOCS_FORBIDDEN');need(sha(ROOT/'.git/index')==INDEX and sha(ROOT/'CLAIMS.yaml')==LEDGER,'LIVE_UNCHANGED');save(out/'summary.json',dict(status='AUTHOR_WAVE39_FIXED353_PATH_CONTROLS_PASS',timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=pins,source_sha256=args.source_sha256,protocol_sha256=args.protocol_sha256,positive_controls=5,strict_negative_controls=19,selected_unique_evidence_paths=len(evidence),selected_impact_paths=len(impact['inputs_sha256']),index_payloads=0,exact_historical_external_source_paths=1,generator_prepare_called=False,current_docs_mutated=False,ledger_mutated=False,index_mutated=False,scientific_launched=False,independent_approval=False));print('AUTHOR_WAVE39_FIXED353_PATH_CONTROLS_PASS');return
  need(args.calibration is not None and args.calibration_sha256 is not None,'CALIBRATION_REQUIRED');cal=read(args.calibration.resolve().relative_to(ROOT).as_posix(),args.calibration_sha256);need(cal['status']=='AUTHOR_WAVE39_FIXED353_PATH_CONTROLS_PASS'and cal['source_sha256']==args.source_sha256 and cal['protocol_sha256']==args.protocol_sha256 and cal['generator_prepare_called']is False,'EXACT_APPLICABLE_CALIBRATION')
  for name,identity in evidence.items():add(name,'three exact registered claim evidence',identity)
  for name,identity in impact['inputs_sha256'].items():
   if disposition(name,identity)=='OMIT_READONLY_INDEX':omitted.append(dict(path=name,sha256=identity,reason='Historical read-only index observation stays in the immutable impact report; no Git metadata payload.'));continue
   add(name,'complete actual impact input',identity)
  reports={key:read(*pair)for key,pair in REPORTS.items()}
  for key,(name,identity)in REPORTS.items():add(name,'exact saved report '+key,identity)
  packaged={}
  for name,identity in PACKAGES.items():
   package=read(name,identity);add(name,'existing public lossless manifest',identity)
   for row in package['records']:
    need(row['raw_path']not in packaged,'EIGHT_DISTINCT_OLD_RAW_PATHS');packaged[row['raw_path']]=row;add(row['raw_path'],'old exact raw identity',row['raw_sha256']);offset=0
    for part in row['parts']:need(part['raw_offset']==offset,'LOSSLESS_OFFSETS');offset+=part['raw_bytes'];add(part['path'],'existing public lossless payload',part['gzip_sha256'])
    need(offset==row['raw_bytes'],'LOSSLESS_RAW_LENGTH')
  need(len(packaged)==8 and sum(row['raw_bytes']for row in packaged.values())==367261301,'EIGHT_OLD_RAW_IDENTITIES')
  for name in EXTRA_FILES:add(name,'explicit completed metadata source')
  for name in EXTRA_ROOTS:
   folder=bounded(name);need(folder.is_dir(),'EXACT_COMPLETED_ROOT_EXISTS:'+name)
   for path in sorted(folder.rglob('*')):
    if path.is_file():need(path.suffix in('.json','.yaml','.log','.jsonl','.gz','.py','.md','.txt','.before','.observed')or path.name=='CLAIMS.pending.yaml','EXPLICIT_METADATA_EXTENSION:'+str(path));add(path.relative_to(ROOT).as_posix(),'explicit completed metadata root')
  for name in['CLAIMS.yaml',BEFORE,Path(__file__).relative_to(ROOT).as_posix(),SPEC,'.gitattributes','acceleration/command_deadline.py','acceleration/run_compute_command.py','acceleration/validate_claims.py','docs/claims.schema.json','pyproject.toml','uv.lock']:add(name,'fixed runtime/current metadata')
  add(args.calibration.resolve().relative_to(ROOT).as_posix(),'applicable author prelaunch calibration',args.calibration_sha256)
  rank=reports['rank'];census=reports['census'];need(rank['complete_exact_coefficients_checked']==1287 and rank['maximum_linear_dimension']==14 and rank['conditional_incidence_rank_lower']==85,'EXACT_RANK85_RECORDED_SCOPE');need(census['complete_proposals_checked']==239085 and census['aggregate']['best_mu']==3480 and census['aggregate']['best_proposal_ids']==[68908,68912],'EXACT_FIXED_CENSUS_SCOPE')
  now=datetime.now(timezone.utc).isoformat();commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();attributes_hash=pin('.gitattributes');(out/'gitattributes.observed').write_bytes((ROOT/'.gitattributes').read_bytes());(out/'CLAIMS.yaml').write_bytes(raw);checkpoint=dict(timestamp=now,source_commit=commit,ledger_sha256=LEDGER,before_ledger_sha256=BEFORE_SHA,claim_records=353,status_counts=counts,review_state_counts={'CLEAR':353},new_claim_revisions=[{key:c[key]for key in('id','revision','statement','scope','status')}for c in new],impact_report=IMPACT,impact_sha256=IMPACT_SHA,new_finite_exclusion_kind_claims=1,new_unrestricted_exclusions=0,target_resolution='UNKNOWN',overall_search_coverage='UNKNOWN; no validated denominator.',attributes_sha256=attributes_hash,execution_state=None,execution_state_null_reason='Generator does not observe live scientific workers; only saved terminal records are counted.',queued_results_excluded=DENY);save(out/'checkpoint.json',checkpoint)
  rows='\n'.join('| '+c['id']+' r1 | '+c['scope']['description']+' | [Audit](../'+c['verification'][0]['command_or_audit']+') |'for c in new)
  text=f'''# Thirty-ninth research milestone, 2026-10-03

Since [wave38](RESEARCH_20261003_THIRTYEIGHTH_WAVE.md), three exact revisions
were added VERIFIED/CLEAR: universal triangle-image lower word counts, the
conditional triangle-incidence rank lower bound85, and one complete finite
two-line neighborhood exclusion at the retained warm endpoint. No unrestricted
target exclusion or graph was added. Later results are outside this353 cutoff.

**As of:** {now}; source commit `{commit}`; [checkpoint](../{out.relative_to(ROOT).as_posix()}/checkpoint.json)
and [frozen353 ledger](../{out.relative_to(ROOT).as_posix()}/CLAIMS.yaml).
New working artifacts are independently hash-pinned, not inferred part of the
source commit. Previous report:350 claims at wave38.

**Verdict:** repository target resolution UNKNOWN; no independently validated
target graph or general nonexistence proof. External resolution review is not
recorded. [Draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3) remains
the review reference; no claimed resolution is merged.

**Verified changes:**345VERIFIED/CLEAR,3CANDIDATE,5REFUTED, all353CLEAR.
The [actual impact audit](../{IMPACT}) preserves every old350 claim, artifact
and target field, exact dependency reasons and the one explicit raw-to-editorial
statement mapping. Status counts are ledger-derived, not file or agent totals.

| New revision | Exact scope | Evidence |
| --- | --- | --- |
{rows}

**Work completed:** the low-word proof supplies at least231 weight3,2079
weight4 and24486 weight6 words in the incidence image of any target graph.
Its independent audit derives collision-free inverse maps and exact character
inequalities; finite fixtures calibrate the checking path, not the universal
proof. The thirteen-weight rational certificate checks1287 exact coefficients,
99 nonnegative coordinates and13 inequalities. Its size upper bound is
216950223385397837448/11529151026462413, less than2^15, so the hypothetical
kernel dimension is at most14 and rankB is at least85. This supplies no upper
rank, forced nonzero kernel, construction or contradiction.

The fixed original warm graph's complete239085 labelled two-line proposals
classify as87996 invalid-linearity,10395 invalid-selection,140507 valid with
changed lambda residual,2 valid lambda-preserving equal-mu and185 valid
lambda-preserving increased-mu. Exactly zero lambda-preserving decreases occur.
There are136536 distinct labelled valid neighbor graphs; this is not an
isomorphism census. Ties68908 and68912 give one identical neutral graph. The
excluded set is only strict descent within this exact fixed V2 neighborhood;
neutral paths, longer trades and other starting graphs remain outside scope.

**Coverage:** one finite-neighborhood exclusion was added, zero unrestricted
exclusions. It is separate from the unchanged380of792 frozen fixed-support
branch union (412 unresolved), as recorded at wave38. These populations overlap
in unknown ways and cannot be summed. Overall search coverage: UNKNOWN; no
validated denominator.

**Best result:** conditional rank lower85 constrains a hypothetical incidence
matrix, not an observed target graph. The retained warm endpoint still has
E_lambda0/E_mu3480 and4764 ordered identity failures. The finite census supplies
no smaller same-scope lambda-preserving mu score. No global best or runtime
performance assertion is made.

**Problems:** V13's proposed ordinary literal statement mapping failed
prelaunch; V14 admits exactly the reviewed40022/626e/proof45e pair and retains
both raw strings. V14 checkerV1 was preserved unexecuted when an availability
update changed its ledger baseline. Actual impact checkerV1 then failed a
top-level-controls assumption; newV2 calibration and actual audit completed.
These are engineering failures, not mathematical refutations. Newly bound
evidence remains LOCAL_ONLY pending separate immutable publication. Wave38's
463 PUBLIC availability updates are independently checked by [its audit](../{REPORTS['public_audit'][0]});
availability and mathematical verification remain separate. Eight earlier raw
models retain their existing exact lossless packages; no new raw duplicates
or recompression are introduced. One exact archived derivation is referenced
through its immutable85e705c source, preserving the existing submodule.

**Execution and next action:** saved counted commands are completed/reaped.
This metadata generator makes no live process observation or ongoing-search
claim. Next concrete action is independent completion of the changed
root-focused kernel engineering gate before any search using that objective;
old weight60 gates cannot approve changed state or move semantics. Later
neutral-census, root-start/engine, projection/self-orthogonality/divisibility,
seven-weight/margin and rooted8-LP work is outside the353 cutoff and its
publication core. This milestone launches no scientific calculation.

**References:** [actual350-to353 impact](../{IMPACT}), [wave38 publication receipt](../{REPORTS['public_receipt'][0]}),
[independent availability check](../{REPORTS['public_audit'][0]}), and the exact
registration/finite-gate/failure records in the publication manifest.
'''
  need(not(ROOT/MILESTONE).exists(),'NEW_MILESTONE_ONLY');(out/'milestone.prepared.md').write_text(text,encoding='utf8',newline='\n')
  notice=f'''# Latest verified continuation checkpoint — wave39, 2026-10-03 JST

The [thirty-ninth milestone](docs/RESEARCH_20261003_THIRTYNINTH_WAVE.md) freezes353claims:
345VERIFIED/CLEAR,3CANDIDATE,5REFUTED. Three additions establish conditional
rankB>=85, triangle-image lower word counts, and absence of strict descent in
one complete239085-labelled-proposal fixed neighborhood. Target resolution
remains UNKNOWN. One finite exclusion is separate from zero unrestricted
exclusions; frozen branch380of792 is unchanged. Overall search coverage:
UNKNOWN; no validated denominator. Wave38 evidence is separately PUBLIC;
new wave39 evidence awaits immutable confirmation. Later queued computations
are outside this cutoff. No live process state is inferred. Historical text
follows unchanged.

'''
  for name in DOCS:
   old=(ROOT/name).read_bytes();need(b'checkpoint \xe2\x80\x94 wave39'not in old,'NO_DUPLICATE_NOTICE');(out/(name.replace('/','_')+'.before')).write_bytes(old);adjusted=notice.replace('(docs/RESEARCH_','(RESEARCH_')if name.startswith('docs/')else notice;prepared=adjusted.encode('utf8')+old;(out/(name.replace('/','_')+'.prepared')).write_bytes(prepared)
   if args.write_current_docs:(ROOT/name).write_bytes(prepared);docs_written.append(name);add(name,'notice preserving exact historical suffix')
  if args.write_current_docs:(ROOT/MILESTONE).write_text(text,encoding='utf8',newline='\n');docs_written.append(MILESTONE);add(MILESTONE,'new ledger-derived milestone')
  records=[];archive_refs=[]
  for name in sorted(origins):
   path=bounded(name);need(path.is_file(),'EXPLICIT_ALLOWLIST_FILE_EXISTS:'+name)
   if name in packaged:
    row=packaged[name];identity=pin(name,row['raw_sha256']);need(path.stat().st_size==row['raw_bytes'],'OLD_RAW_BYTES');omitted.append(dict(path=name,sha256=identity,bytes=row['raw_bytes'],reason='Existing public lossless package; no duplicate raw blob.'));continue
   if name==ARCHIVE:
    pin(name,ARCHIVE_SHA);actual=subprocess.check_output(['git','-C',str(ROOT/'external_conway99_research'),'rev-parse','HEAD'],text=True).strip();need(actual==ARCHIVE_COMMIT,'PINNED_SUBMODULE_COMMIT');blob=subprocess.check_output(['git','-C',str(ROOT/'external_conway99_research'),'cat-file','blob',ARCHIVE_COMMIT+':'+name.split('/',1)[1]]);need(hashlib.sha256(blob).hexdigest()==ARCHIVE_SHA and blob==path.read_bytes(),'EXACT_PINNED_ARCHIVE_GIT_BLOB');reference=archive_metadata(name,ARCHIVE_SHA,ARCHIVE_REPOSITORY,ARCHIVE_COMMIT,name.split('/',1)[1]);reference.update(git_blob_sha256=ARCHIVE_SHA,git_blob_bytes=len(blob),git_blob_rehashed=True);archive_refs.append(reference);continue
   identity=pin(name,expected.get(name));need(path.stat().st_size<50*1024**2,'DIRECT50MIB_BOUND:'+name);records.append(dict(path=name,sha256=identity,bytes=path.stat().st_size,origins=sorted(origins[name])))
  need(len(archive_refs)==1 and sha(ROOT/'.git/index')==INDEX and sha(ROOT/'CLAIMS.yaml')==LEDGER,'EXACT_REFERENCE_AND_LIVE_UNCHANGED');self_names=[path.relative_to(ROOT).as_posix()for path in sorted(out.iterdir())if path.is_file()]+[(out/'manifest.json').relative_to(ROOT).as_posix(),(out/'stage_paths.nul').relative_to(ROOT).as_posix()];names=sorted({row['path']for row in records}|set(self_names));need(all(not name.startswith(('.git/','external_conway99_research/'))for name in names),'NO_GIT_OR_SUBMODULE_PAYLOAD');(out/'stage_paths.nul').write_bytes(b''.join(name.encode('utf8')+b'\0'for name in names));save(out/'manifest.json',dict(schema='WAVE39_FIXED353_EXPLICIT_PUBLICATION_ALLOWLIST_V1',timestamp=now,source_commit=commit,ledger_sha256=LEDGER,before_ledger_sha256=BEFORE_SHA,current_claims=353,previous_claims=350,new_claim_ids=IDS,records=records,direct_record_count=len(records),direct_bytes=sum(row['bytes']for row in records),omitted=omitted,historical_external_sources=archive_refs,old_lossless_packages=PACKAGES,stage_paths_count=len(names),stage_paths_sha256=sha(out/'stage_paths.nul'),self_metadata_paths=self_names,inputs_sha256=pins,docs_written=docs_written,ledger_mutated=False,index_mutated=False,availability_changed=False,mathematical_replay=False,scientific_launched=False,later_results_excluded=DENY,deadline=deadline.status()));print(json.dumps(dict(status='WAVE39_FIXED353_MILESTONE_EXPLICIT_ALLOWLIST_PREPARED',manifest_sha256=sha(out/'manifest.json'),direct_records=len(records),stage_paths=len(names))))
 except BaseException as error:save(out/'failure.json',dict(exception=type(error).__name__,diagnostic=str(error),inputs_sha256=pins,docs_written=docs_written,ledger_mutated=False,index_mutated=False,scientific_launched=False,deadline=deadline.status()));raise
if __name__=='__main__':main()
