"""Source-only fixed356 publication generator; no staging, registry or science."""
import argparse
from collections import Counter,defaultdict
from datetime import datetime,timezone
import hashlib,json,re,subprocess,sys
from pathlib import Path,PurePosixPath
from command_deadline import CommandDeadline
import validate_claims as registry

ROOT=Path(__file__).resolve().parents[1]
SOURCE='acceleration/record_20261003_wave40_milestone_v1.py'
SPEC='acceleration/record_20261003_wave40_milestone_v1_spec.md'
BEFORE='acceleration/results/20261003_wave40_registration01/CLAIMS.before.yaml'
BEFORE_SHA='4b64876083f128382f48335a9b7e3cec08c56e0c1eb90aa24461901860e848da'
IMPACT='acceleration/results/20261003_independent_review/wave40_transition01/summary.json'
IDS=['C-UNRESTRICTED-TRIANGLE-INCIDENCE-WEIGHT5-PATH-IMAGE-LOWER-COUNT','C-HYPERGRAPH-ROOT-FOCUSED-PILOT01-SAVED-OBJECTS','C-UNRESTRICTED-TRIANGLE-INCIDENCE-BINARY-RANK-LOWER86']
DOCS=['README.md','ACTIVE_RESEARCH.md','docs/RESEARCH_MAP.md','docs/REPRODUCING.md']
MILESTONE='docs/RESEARCH_20261003_FORTIETH_WAVE.md'
REPORTS={
 'weight5':('acceleration/results/20261003_independent_review/weight5_full02/summary.json','dedb5c3affcfd0edb98a1d97ebdc973290b53b67ecbb76f3d78135b2bea688f2'),
 'pilot':('acceleration/results/20261003_independent_review/root_focused_saved_pilot01/summary.json','7b54dfeb4d54c6a0cb99ab18a67bf2a5d0b263290e4a120cebc6d38a0d5af558'),
 'rank':('acceleration/results/20261003_independent_review/four_counts_lp_even13_full01/summary.json','3cc0ae7fbd0d340c00a4b1e3b00221ef70df6767812b846875a9483413745674'),
 'public_receipt':('acceleration/results/20261003_wave39_publication01/receipt.json','a55db368bccaec9161caac01486a40eff8a80c1bbb5bf2c52381c35971bdf376'),
 'public_audit':('acceleration/results/20261003_wave39_availability01/summary.json','32a88de77c7b71150bf524047f71117017a243775011811bece5a14f98af077b')}
ARCHIVE='external_conway99_research/attempts/wave102-prism-incidence-code/derivation.md'
ARCHIVE_SHA='df8841bee7f23b444186ab65947f77865ffb243363967dd56340207628f00c6f'
ARCHIVE_COMMIT='85e705cc6c2a14d123120c93a847e30aaab1789e'
ARCHIVE_REPOSITORY='https://github.com/YesterdaysLemon/conway-99-research'
PACKAGES={
 'acceleration/results/20261002_wave33_model_package01/manifest.json':'c3efa198c5f48eddb5ead69a4bb130a3dc55567bb298856143c6fb62eb0e0145',
 'acceleration/results/20261002_wave33_reconstruction_package01/manifest.json':'f639431b7ea9ce0f1500ea48b002629d2523271eead700217dd512e8ade66989',
 'acceleration/results/20261003_wave36_coupling_package01/manifest.json':'38f641ec21ec3d1d617515e8b3e578e098886863f7016ad640ac1906e8b0988f',
 'acceleration/results/20261003_wave37_rooted8_package01/manifest.json':'ea48c30dfa68fe70bad17edbfd3697d8a2dcf28f9ab24b63d0d66895e7eb9b14'}
EXTRA_FILES=['.gitattributes','docs/RESEARCH_20261003_THIRTYNINTH_WAVE.md',
 'acceleration/register_20261003_bound_claims_v15.py','acceleration/register_20261003_bound_claims_v15_spec.md',
 'acceleration/calibrate_20261003_registrar_v15_helpers_v1.py','acceleration/calibrate_20261003_registrar_v15_helpers_v1_spec.md',
 'acceleration/audit_20261003_registrar_v15_engineering_v1.py','acceleration/audit_20261003_registrar_v15_engineering_v1_spec.md',
 'acceleration/plan_20261003_registrar_v15_helpers_v1.json','acceleration/plan_20261003_registrar_v15_independent_engineering_v1.json',
 'acceleration/plan_20261003_wave40_registration_v15_v1.json','acceleration/plan_20261003_wave40_registration_v15_v2.json',
 'acceleration/audit_20261003_wave40_transition_v1.py','acceleration/audit_20261003_wave40_transition_v1_spec.md',
 'acceleration/confirm_20261003_wave39_publication_v1.py','acceleration/confirm_20261003_wave39_publication_v1_spec.md',
 'acceleration/audit_20261003_wave39_availability_v1.py','acceleration/audit_20261003_wave39_availability_v1_spec.md',
 'acceleration/audit_20261003_wave39_availability_v2.py','acceleration/audit_20261003_wave39_availability_v2_spec.md']
EXTRA_ROOTS=[
 'acceleration/results/20261003_registrar_v15_helpers01','acceleration/results/20261003_registrar_v15_helpers_supervision01',
 'acceleration/results/20261003_independent_review/registrar_v15_engineering01','acceleration/results/20261003_independent_review/registrar_v15_engineering_supervision01',
 'acceleration/results/20261003_wave40_registration01','acceleration/results/20261003_wave40_registration_supervision01',
 'acceleration/results/20261003_independent_review/wave40_transition_calibration01','acceleration/results/20261003_independent_review/wave40_transition_calibration_supervision01',
 'acceleration/results/20261003_independent_review/wave40_transition01','acceleration/results/20261003_independent_review/wave40_transition_supervision01',
 'acceleration/results/20261003_wave39_publication01','acceleration/results/20261003_wave39_publication_supervision01',
 'acceleration/results/20261003_wave39_availability01','acceleration/results/20261003_wave39_availability_supervision01',
 'acceleration/results/20261003_wave39_availability_calibration01','acceleration/results/20261003_wave39_availability_calibration_supervision01']
DENY=['weight5_c4','c4_endpoint','double_fibers_rook9','root_focused_census','root_focused_two_line','selected_neighbor','wave41','projection_hull','kernel_self_orthogonal','rooted8_unrestricted_lp','rooted8_unrestricted_corner']

def need(ok,stage):
 if not ok:raise ValueError(stage)
def sha(path):
 with path.open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def save(path,value):
 with path.open('x',encoding='utf8',newline='\n')as stream:json.dump(value,stream,indent=2,allow_nan=False);stream.write('\n')
def identity(value,stage):
 need(type(value)is str and re.fullmatch('[0-9a-f]{64}',value)is not None,stage);return value
def bounded(name):
 need(type(name)is str and name and not any(c in name for c in'\\\r\n\0'),'LITERAL_RELATIVE_PATH:'+repr(name));p=PurePosixPath(name)
 need(not p.is_absolute()and'..'not in p.parts and not name.startswith('.git/'),'WORKSPACE_RELATIVE_PATH:'+repr(name))
 need(name==ARCHIVE or name.startswith(('acceleration/','docs/'))or name in DOCS+['CLAIMS.yaml','pyproject.toml','uv.lock','.gitattributes','.github/workflows/claims.yml'],'RESEARCH_NAMESPACE:'+repr(name))
 need(not any(term in name.lower()for term in DENY),'EXCLUDED_LATER_SCIENCE:'+repr(name));need('/build/'not in name and'/recovered/'not in name,'EXCLUDED_DUPLICATE_BUILD:'+repr(name))
 path=(ROOT/name).resolve();need(path.is_relative_to(ROOT),'RESOLVED_BOUNDARY:'+repr(name));return path
def disposition(name,digest,index):
 if name=='.git/index':need(digest==index,'HISTORICAL_INDEX_OBSERVATION_HASH:'+repr(name));return'OMIT_READONLY_INDEX'
 if name==ARCHIVE:need(digest==ARCHIVE_SHA,'EXACT_PINNED_ARCHIVE_HASH:'+repr(name));return'REFERENCE_PINNED_ARCHIVE'
 bounded(name);return'DIRECT'
def archive_reference(repo,commit,path):
 need(repo==ARCHIVE_REPOSITORY and commit==ARCHIVE_COMMIT and path==ARCHIVE.split('/',1)[1],'EXACT_PINNED_ARCHIVE_REFERENCE')
 return dict(path=ARCHIVE,sha256=ARCHIVE_SHA,repository=repo,commit=commit,external_path=path,retrieval=repo+'/blob/'+commit+'/'+path,reason='Immutable historical source reference; no submodule payload staging or new historical verification.')
def path_controls(index):
 controls=[]
 for name,digest,wanted in [('CLAIMS.yaml','f'*64,'DIRECT'),('.gitattributes','f'*64,'DIRECT'),('docs/REPRODUCING.md','f'*64,'DIRECT'),('.git/index',index,'OMIT_READONLY_INDEX'),(ARCHIVE,ARCHIVE_SHA,'REFERENCE_PINNED_ARCHIVE')]:
  need(disposition(name,digest,index)==wanted,'POSITIVE_PATH_CONTROL');controls.append(dict(path=name,outcome=wanted))
 for name,digest,stage in [('.git/index','0'*64,'HISTORICAL_INDEX_OBSERVATION_HASH'),('.git/config','f'*64,'WORKSPACE_RELATIVE_PATH'),('../CLAIMS.yaml','f'*64,'WORKSPACE_RELATIVE_PATH'),('docs/../a.md','f'*64,'WORKSPACE_RELATIVE_PATH'),('/tmp/private','f'*64,'WORKSPACE_RELATIVE_PATH'),('C:/private/file','f'*64,'RESEARCH_NAMESPACE'),('docs\\a.md','f'*64,'LITERAL_RELATIVE_PATH'),('docs/a\n.md','f'*64,'LITERAL_RELATIVE_PATH'),(ARCHIVE,'f'*64,'EXACT_PINNED_ARCHIVE_HASH'),('external_conway99_research/CLAIMS.yaml','f'*64,'RESEARCH_NAMESPACE'),('acceleration/build/x','f'*64,'EXCLUDED_DUPLICATE_BUILD'),('acceleration/recovered/x','f'*64,'EXCLUDED_DUPLICATE_BUILD'),('acceleration/theory_20261003_triangle_kernel_c4_endpoint_v3.py','f'*64,'EXCLUDED_LATER_SCIENCE'),('docs/CANDIDATE_20261003_WEIGHT5_DOUBLE_FIBERS_ROOK9_V1.md','f'*64,'EXCLUDED_LATER_SCIENCE'),('acceleration/results/20261003_root_focused_two_line01/summary.json','f'*64,'EXCLUDED_LATER_SCIENCE'),('acceleration/results/20261003_selected_neighbor01/summary.json','f'*64,'EXCLUDED_LATER_SCIENCE')]:
  try:disposition(name,digest,index)
  except ValueError as error:need(str(error).startswith(stage+':')and repr(name)in str(error),'PRECISE_PATH_STAGE');controls.append(dict(path=name,outcome='REJECTED',diagnostic=str(error)))
  else:raise ValueError('FALSE_PATH_ACCEPT:'+name)
 archive_reference(ARCHIVE_REPOSITORY,ARCHIVE_COMMIT,ARCHIVE.split('/',1)[1])
 for repo,commit,path in [('https://github.com/untrusted/other',ARCHIVE_COMMIT,ARCHIVE.split('/',1)[1]),(ARCHIVE_REPOSITORY,'0'*40,ARCHIVE.split('/',1)[1]),(ARCHIVE_REPOSITORY,ARCHIVE_COMMIT,'CLAIMS.yaml')]:
  try:archive_reference(repo,commit,path)
  except ValueError as error:need(str(error)=='EXACT_PINNED_ARCHIVE_REFERENCE','PRECISE_ARCHIVE_STAGE');controls.append(dict(outcome='REJECTED',diagnostic=str(error)))
  else:raise ValueError('FALSE_ARCHIVE_ACCEPT')
 return controls

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['calibrate','prepare'],required=True);ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--source-sha256',required=True);ap.add_argument('--protocol-sha256',required=True)
 ap.add_argument('--after-ledger-sha256',required=True);ap.add_argument('--impact-sha256',required=True);ap.add_argument('--protected-index-sha256',required=True);ap.add_argument('--calibration',type=Path);ap.add_argument('--calibration-sha256');ap.add_argument('--write-current-docs',action='store_true');args=ap.parse_args()
 ledger=identity(args.after_ledger_sha256,'ACTUAL_AFTER_HASH_REQUIRED');impact_sha=identity(args.impact_sha256,'ACTUAL_IMPACT_HASH_REQUIRED');index=identity(args.protected_index_sha256,'ACTUAL_INDEX_HASH_REQUIRED')
 deadline=CommandDeadline(args.seconds,allocation_reason='Fixed356 metadata and explicit closure only; previouswave39 generation5.7s plus367MB reused exact identities support100worker20internal save; no science/index/packaging')
 out=args.out.resolve();need(out.is_relative_to(ROOT)and not out.exists(),'FRESH_WORKSPACE_OUTPUT');out.mkdir(parents=True);pins={};origins=defaultdict(set);expected={};omitted=[];docs_written=[]
 def pin(name,wanted=None):
  need(deadline.status()['remaining_seconds']>20,'NOT_COMPLETED_WITHIN_ALLOCATION');actual=sha(bounded(name));need(wanted is None or actual==wanted,'EXACT_INPUT_HASH:'+name);need(name not in pins or pins[name]==actual,'FROZEN_INPUT_CHANGED:'+name);pins[name]=actual;return actual
 def read(name,wanted):pin(name,wanted);return json.loads(bounded(name).read_bytes())
 def add(name,origin,wanted=None):
  mode=disposition(name,wanted if wanted is not None else ARCHIVE_SHA if name==ARCHIVE else'',index);need(mode!='OMIT_READONLY_INDEX','NO_INDEX_PAYLOAD');origins[name].add(origin)
  if wanted is not None:need(name not in expected or expected[name]==wanted,'CONSISTENT_EXPECTED_HASH');expected[name]=wanted
 try:
  pin(SOURCE,args.source_sha256);pin(SPEC,args.protocol_sha256);need(sha(ROOT/'.git/index')==index,'EXACT_LIVE_INDEX');raw=(ROOT/'CLAIMS.yaml').read_bytes();pin('CLAIMS.yaml',ledger);pin(BEFORE,BEFORE_SHA)
  current=registry.read_ledger(ROOT/'CLAIMS.yaml');before=registry.read_ledger(ROOT/BEFORE);new=current['claims'][353:]
  need(len(before['claims'])==353 and len(current['claims'])==356 and current['claims'][:353]==before['claims']and[c['id']for c in new]==IDS and current['target']==before['target']and current['target']['status']=='UNKNOWN','EXACT353_TO356_CUTOFF')
  counts=dict(Counter(c['status']for c in current['claims']));need(counts=={'VERIFIED':348,'CANDIDATE':3,'REFUTED':5}and all(c['review_state']=='CLEAR'for c in current['claims']),'EXACT356_COUNTS')
  impact=read(IMPACT,impact_sha);need(impact['status']=='INDEPENDENT_WAVE40_EXACT353_TO356_TRANSITION_V1_PASS'and impact['actual_transition_inspected']is True and impact['before_ledger_sha256']==BEFORE_SHA and impact['after_ledger_sha256']==ledger and impact['current_claims']==356 and impact['new_claim_ids']==IDS and impact['prior_claims_artifacts_target_unchanged']is True and impact['new_exclusions']==impact['new_unrestricted_exclusions']==0,'ACTUAL_INDEPENDENT_TRANSITION_REQUIRED')
  artifacts={a['id']:a for a in current['artifacts']};evidence={}
  for claim in new:
   for aid in claim['evidence']:
    item=artifacts[aid];name,digest=item['path'],item['sha256'];need(name is not None and(name not in evidence or evidence[name]==digest),'CONSISTENT_SELECTED_EVIDENCE');evidence[name]=digest
  controls=path_controls(index);inventory=[]
  for origin,records in [('three_claim_evidence',evidence),('actual_impact_inputs',impact['inputs_sha256'])]:
   for name,digest in sorted(records.items()):mode=disposition(name,digest,index);need(mode=='OMIT_READONLY_INDEX'or bounded(name).is_file(),'LITERAL_INPUT_EXISTS:'+name);inventory.append(dict(origin=origin,path=name,sha256=digest,disposition=mode))
  for name in EXTRA_FILES:need(bounded(name).is_file(),'EXPLICIT_EXTRA_FILE_EXISTS:'+name)
  for name in EXTRA_ROOTS:need(bounded(name).is_dir(),'EXPLICIT_EXTRA_ROOT_EXISTS:'+name)
  save(out/'path_controls.json',controls);save(out/'selected_path_inventory.json',inventory)
  if args.mode=='calibrate':
   need(not args.write_current_docs,'CALIBRATION_DOCS_FORBIDDEN');need(sha(ROOT/'.git/index')==index and sha(ROOT/'CLAIMS.yaml')==ledger,'PROTECTED_UNCHANGED')
   save(out/'summary.json',dict(status='AUTHOR_WAVE40_FIXED356_PATH_CONTROLS_PASS',timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=pins,source_sha256=args.source_sha256,protocol_sha256=args.protocol_sha256,ledger_sha256=ledger,impact_sha256=impact_sha,index_sha256=index,positive_controls=5,strict_negative_controls=19,selected_unique_evidence_paths=len(evidence),selected_impact_paths=len(impact['inputs_sha256']),index_payloads=0,generator_prepare_called=False,current_docs_mutated=False,ledger_mutated=False,index_mutated=False,scientific_launched=False,independent_approval=False));print('AUTHOR_WAVE40_FIXED356_PATH_CONTROLS_PASS');return
  need(args.calibration and args.calibration_sha256,'APPLICABLE_AUTHOR_CALIBRATION_REQUIRED');cal=read(args.calibration.resolve().relative_to(ROOT).as_posix(),args.calibration_sha256)
  need(cal['status']=='AUTHOR_WAVE40_FIXED356_PATH_CONTROLS_PASS'and cal['source_sha256']==args.source_sha256 and cal['protocol_sha256']==args.protocol_sha256 and cal['ledger_sha256']==ledger and cal['impact_sha256']==impact_sha and cal['index_sha256']==index and cal['generator_prepare_called']is False,'EXACT_APPLICABLE_CALIBRATION')
  for name,digest in evidence.items():add(name,'three exact registered claim evidence',digest)
  for name,digest in impact['inputs_sha256'].items():
   if disposition(name,digest,index)=='OMIT_READONLY_INDEX':omitted.append(dict(path=name,sha256=digest,reason='Historical read-only index observation stays in immutable impact report, never staged.'));continue
   add(name,'complete actual transition input',digest)
  reports={key:read(*pair)for key,pair in REPORTS.items()}
  for key,(name,digest)in REPORTS.items():add(name,'exact saved '+key+' report',digest)
  need(reports['public_audit']['status']=='INDEPENDENT_WAVE39_AVAILABILITY_V2_ONLY_PUBLIC_TRANSITION_PASS'and reports['public_audit']['unchanged_claims']==353 and reports['public_audit']['after_ledger_sha256']==BEFORE_SHA,'PRIOR_PUBLIC_AVAILABILITY_ONLY')
  packaged={}
  for name,digest in PACKAGES.items():
   package=read(name,digest);add(name,'existing public lossless manifest',digest)
   for row in package['records']:
    need(row['raw_path']not in packaged,'EIGHT_DISTINCT_OLD_RAW_PATHS');packaged[row['raw_path']]=row;add(row['raw_path'],'old raw identity',row['raw_sha256']);offset=0
    for part in row['parts']:need(part['raw_offset']==offset,'LOSSLESS_OFFSETS');offset+=part['raw_bytes'];add(part['path'],'existing public lossless payload',part['gzip_sha256'])
    need(offset==row['raw_bytes'],'LOSSLESS_RAW_LENGTH')
  need(len(packaged)==8 and sum(row['raw_bytes']for row in packaged.values())==367261301,'EXACT_EIGHT_OLD_RAW_IDENTITIES')
  for name in EXTRA_FILES:add(name,'explicit completed metadata source')
  for name in EXTRA_ROOTS:
   for path in sorted(bounded(name).rglob('*')):
    if path.is_file():need(path.suffix in('.json','.yaml','.log','.jsonl','.gz','.py','.md','.txt','.before','.observed')or path.name=='CLAIMS.pending.yaml','EXPLICIT_METADATA_EXTENSION:'+str(path));add(path.relative_to(ROOT).as_posix(),'explicit completed metadata root')
  for name in ['CLAIMS.yaml',BEFORE,SOURCE,SPEC,'.gitattributes','acceleration/command_deadline.py','acceleration/run_compute_command.py','acceleration/validate_claims.py','docs/claims.schema.json','pyproject.toml','uv.lock']:add(name,'fixed runtime/current metadata')
  add(args.calibration.resolve().relative_to(ROOT).as_posix(),'applicable author path calibration',args.calibration_sha256)
  rank=reports['rank'];pilot=reports['pilot'];need(rank['complete_exact_coefficients_checked']==1287 and rank['maximum_linear_dimension']==13 and rank['conditional_incidence_rank_lower']==86,'EXACT_RANK86_RECORDED_SCOPE')
  need(pilot['saved_states']==101 and pilot['saved_state_files']==102 and pilot['native_reported_proposals']==10000000 and pilot['saved_trace_records']==10099 and pilot['complete_trajectory_checked']is False and pilot['zero_target_candidates']==0,'EXACT_SAVED_PILOT_SCOPE')
  now=datetime.now(timezone.utc).isoformat();commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();attributes=pin('.gitattributes');(out/'gitattributes.observed').write_bytes((ROOT/'.gitattributes').read_bytes());(out/'CLAIMS.yaml').write_bytes(raw)
  save(out/'checkpoint.json',dict(timestamp=now,source_commit=commit,ledger_sha256=ledger,before_ledger_sha256=BEFORE_SHA,claim_records=356,status_counts=counts,review_state_counts={'CLEAR':356},new_claim_revisions=[{key:c[key]for key in('id','revision','statement','scope','status')}for c in new],impact_report=IMPACT,impact_sha256=impact_sha,new_finite_exclusions=0,new_unrestricted_exclusions=0,target_resolution='UNKNOWN',overall_search_coverage='UNKNOWN; no validated denominator.',attributes_sha256=attributes,execution_state=None,execution_state_null_reason='Metadata generator makes no live scientific process observation.',queued_results_excluded=DENY))
  rows='\n'.join('| '+c['id']+' r1 | '+c['scope']['description']+' | [Audit](../'+c['verification'][0]['command_or_audit']+') |'for c in new)
  text=f'''# Fortieth research milestone, 2026-10-03

Since [wave39](RESEARCH_20261003_THIRTYNINTH_WAVE.md), three independently checked
revisions were added: the universal triangle-path weight5 image lower bound,
the exact conditional incidence rank lower86, and finite saved objects from one
root-focused pilot. No graph or exclusion was added. Later C4 strengthening,
endpoint guides and root-focused census results are outside this356 cutoff.

**As of:** {now}, source commit `{commit}`, [checkpoint](../{out.relative_to(ROOT).as_posix()}/checkpoint.json),
[frozen356 ledger](../{out.relative_to(ROOT).as_posix()}/CLAIMS.yaml), previous353
report wave39. Working artifacts are separately hash-pinned; the context commit
is not asserted to contain every new file.

**Verdict:** target resolution UNKNOWN; no independently validated target graph
or general nonexistence proof. External resolution review is unrecorded. The
[draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3) is the review reference.

**Verified changes:**348 VERIFIED/CLEAR,3 CANDIDATE,5 REFUTED, all356 CLEAR.
The [actual impact audit](../{IMPACT}) preserves every old353 claim, artifact and
target field. Two exact missing-headline mappings are disclosed, never inferred
as universal permission for unreviewed statements. Counts derive from ledger.

| New revision | Exact scope | Evidence |
| --- | --- | --- |
{rows}

**Work completed:** the weight5 proof applies to every finite simple graph with
exactly one common neighbor per adjacent pair and its complete triangle family.
Its unordered three-triangle path count P yields at least ceil(P/2) distinct
weight5 image words. For a hypothetical target P=24948 and N5>=12474, giving
the exact shifted character row sum_(w>0) A_w(12474-K5(w))<=71510670. The
universal inverse proof is separate from its seven finite fixtures:62 trios,
23 paths,14 support words and234 complete small-image coefficient masks.

The even13 certificate independently checks1287 exact coefficients,99 rational
nonnegative dual coordinates and13 inequalities. Its kernel-size upper bound
97502464/9739 is below2^14, forcing dimension<=13 and incidence rank>=86 for
any hypothetical target. Only the earlier even36..60 interval and independently
proved3/4/5/6 image lower counts are required. No divisible-four premise,
optimum, upper rank, forced nonzero kernel or graph contradiction is used.

One fixed root-focused pilot reports10000000 proposals. Independent checking
covers106 saved native files,102 states at101 distinct saved steps,204 matrix
observations and all10099 stored proposals. The complete trajectory was not
checked. Current and best-root objects have E_lambda0/Rroot10/Froot10, with
E_mu5476 and5520 respectively; ordered identity failures5500 and5580. Their
root11 nonedge CN histograms are {{1:5,2:74,3:5}}. Both preserve seven literal
root triples and the231-linear-triple degree7 structure; neither is a target.
The root-local objective is distinct from ordinary E_mu and cannot establish
global improvement by comparing incompatible objective values.

**Coverage:** zero new finite exclusions and zero unrestricted exclusions.
The previous fixed239085-proposal strict-descent exclusion and frozen380of792
fixed-support branch union are unchanged, disjointness unestablished. Overall
search coverage: UNKNOWN; no validated denominator.

**Best result:** conditional incidence rank lower86 is a necessary algebraic
constraint, not a realized target graph. The pilot's observed minimum root
residual10 is only over recorded saved objects; no global minimum or runtime
performance assertion follows.

**Problems:** all preserved engineering failures remain in exact source/receipt
closures. Old N5 fullcheck01 rejected an incorrectly copied65hex summary hash;
full02 checked the actual64hex identity without artifact change. Rank86 metadata
writerV1 was vetoed before invocation for an incompatible verification-record
field; V2 and V3 preserve its history. The author character loop declared140
but executed139 cells; its immutable deviation is retained and the separate
pre-output ROOT calibration checked all140 including n0. Numerical rejected
certificate lifts remain preserved. No timeout or failed reproduction is a
mathematical refutation.

Prior wave39 availability is [independently checked](../{REPORTS['public_audit'][0]}):
373 artifact records became PUBLIC, with353 mathematical claims unchanged.
New wave40 evidence remains LOCAL_ONLY pending immutable confirmation. Existing
eight old raw operators retain their48 public lossless pieces; no raw duplicate
or heavy recompression is introduced. The pinned external85e705c source remains
a reference under the unchanged submodule, never copied into main Git payload.

**Execution and next action:** saved counted commands completed and were reaped.
No current process state is inferred by this generator. Next concrete action is
to verify a selected neighbor's exact graph-input projection before any admitted
root-focused construction from it. Later complete census, C4/rook collision,
endpoint and other queued mathematical work is excluded from this cutoff.

**References:** [actual353-to356 impact](../{IMPACT}), [wave39 publication receipt](../{REPORTS['public_receipt'][0]}),
[independent availability](../{REPORTS['public_audit'][0]}), exact registrar/finite
gate/failure records and complete three-claim evidence in the publication manifest.
'''
  need(not(ROOT/MILESTONE).exists(),'NEW_MILESTONE_ONLY');(out/'milestone.prepared.md').write_text(text,encoding='utf8',newline='\n')
  notice='''# Latest verified continuation checkpoint — wave40, 2026-10-03 JST

The [fortieth milestone](docs/RESEARCH_20261003_FORTIETH_WAVE.md) freezes356claims:
348VERIFIED/CLEAR,3CANDIDATE,5REFUTED. Three additions establish conditional
rankB>=86, the universal triangle-path weight5 image lower count, and finite
root-focused pilot saved objects. Target resolution remains UNKNOWN. Zero new
finite/unrestricted exclusions; prior fixed-neighborhood and380/792 branch
records are unchanged. Overall search coverage: UNKNOWN; no validated denominator.
Wave39 evidence is separately PUBLIC; newwave40 awaits immutable confirmation.
Later queued science lies outside this cutoff. No live worker state is inferred.
Historical text follows unchanged.

'''
  for name in DOCS:
   old=(ROOT/name).read_bytes();need(b'checkpoint \xe2\x80\x94 wave40'not in old,'NO_DUPLICATE_NOTICE');(out/(name.replace('/','_')+'.before')).write_bytes(old);adjusted=notice.replace('(docs/RESEARCH_','(RESEARCH_')if name.startswith('docs/')else notice;prepared=adjusted.encode('utf8')+old;(out/(name.replace('/','_')+'.prepared')).write_bytes(prepared)
   if args.write_current_docs:(ROOT/name).write_bytes(prepared);docs_written.append(name);add(name,'notice preserving exact historical suffix')
  if args.write_current_docs:(ROOT/MILESTONE).write_text(text,encoding='utf8',newline='\n');docs_written.append(MILESTONE);add(MILESTONE,'new ledger-derived milestone')
  records=[];archive_refs=[]
  for name in sorted(origins):
   path=bounded(name);need(path.is_file(),'EXPLICIT_ALLOWLIST_FILE_EXISTS:'+name)
   if name in packaged:
    row=packaged[name];digest=pin(name,row['raw_sha256']);need(path.stat().st_size==row['raw_bytes'],'OLD_RAW_BYTES');omitted.append(dict(path=name,sha256=digest,bytes=row['raw_bytes'],reason='Existing public lossless package; no duplicate raw blob.'));continue
   if name==ARCHIVE:
    pin(name,ARCHIVE_SHA);actual=subprocess.check_output(['git','-C',str(ROOT/'external_conway99_research'),'rev-parse','HEAD'],text=True).strip();need(actual==ARCHIVE_COMMIT,'PINNED_SUBMODULE_COMMIT');blob=subprocess.check_output(['git','-C',str(ROOT/'external_conway99_research'),'cat-file','blob',ARCHIVE_COMMIT+':'+name.split('/',1)[1]]);need(hashlib.sha256(blob).hexdigest()==ARCHIVE_SHA and blob==path.read_bytes(),'EXACT_ARCHIVE_GIT_BLOB');reference=archive_reference(ARCHIVE_REPOSITORY,ARCHIVE_COMMIT,name.split('/',1)[1]);reference.update(git_blob_sha256=ARCHIVE_SHA,git_blob_bytes=len(blob),git_blob_rehashed=True);archive_refs.append(reference);continue
   digest=pin(name,expected.get(name));need(path.stat().st_size<50*1024**2,'DIRECT50MIB_BOUND:'+name);records.append(dict(path=name,sha256=digest,bytes=path.stat().st_size,origins=sorted(origins[name])))
  need(len(archive_refs)==1 and sha(ROOT/'.git/index')==index and sha(ROOT/'CLAIMS.yaml')==ledger,'EXACT_REFERENCE_AND_PROTECTED_UNCHANGED')
  self_names=[path.relative_to(ROOT).as_posix()for path in sorted(out.iterdir())if path.is_file()]+[(out/'manifest.json').relative_to(ROOT).as_posix(),(out/'stage_paths.nul').relative_to(ROOT).as_posix()];names=sorted({row['path']for row in records}|set(self_names));need(all(not name.startswith(('.git/','external_conway99_research/'))for name in names),'NO_GIT_OR_SUBMODULE_PAYLOAD');(out/'stage_paths.nul').write_bytes(b''.join(name.encode('utf8')+b'\0'for name in names))
  save(out/'manifest.json',dict(schema='WAVE40_FIXED356_EXPLICIT_PUBLICATION_ALLOWLIST_V1',timestamp=now,source_commit=commit,ledger_sha256=ledger,before_ledger_sha256=BEFORE_SHA,current_claims=356,previous_claims=353,new_claim_ids=IDS,records=records,direct_record_count=len(records),direct_bytes=sum(row['bytes']for row in records),omitted=omitted,historical_external_sources=archive_refs,old_lossless_packages=PACKAGES,stage_paths_count=len(names),stage_paths_sha256=sha(out/'stage_paths.nul'),self_metadata_paths=self_names,inputs_sha256=pins,docs_written=docs_written,ledger_mutated=False,index_mutated=False,availability_changed=False,mathematical_replay=False,scientific_launched=False,later_results_excluded=DENY,deadline=deadline.status()));print(json.dumps(dict(status='WAVE40_FIXED356_MILESTONE_EXPLICIT_ALLOWLIST_PREPARED',manifest_sha256=sha(out/'manifest.json'),direct_records=len(records),stage_paths=len(names))))
 except BaseException as error:save(out/'failure.json',dict(exception=type(error).__name__,diagnostic=str(error),inputs_sha256=pins,docs_written=docs_written,ledger_mutated=False,index_mutated=False,scientific_launched=False,deadline=deadline.status()));raise
if __name__=='__main__':main()
