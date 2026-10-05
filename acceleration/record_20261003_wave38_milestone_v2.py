"""Fixed350 ledger-derived milestone/exact closure; no index or publication."""
import argparse
from collections import Counter,defaultdict
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path,PurePosixPath
import subprocess
import sys
from command_deadline import CommandDeadline
import validate_claims as registry

ROOT=Path(__file__).resolve().parents[1]
LEDGER='cc8184dbe3c0c1bc6d539e8925fc392b80a3a4344c29e051118af0157d948a2c'
BEFORE='acceleration/results/20261003_wave38_registration01/CLAIMS.before.yaml'
BEFORE_SHA='b2df016825e41180c2d22d04835ce3922d13384b4c3803e9adb39d56b204384d'
IMPACT='acceleration/results/20261003_independent_review/wave38_transition02/summary.json'
IMPACT_SHA='70a8adf03a941ca426033f56fd2f87632b0d6860c9ea217ddc3b2fe82f79f4db'
IDS=['C-UNRESTRICTED-ROOTED8-CONTENT-DIVIDED-GF2-FOUR-PRIMALS','C-HYPERGRAPH-WEIGHT60-V2-GRAPH-ONLY-SEED61-RESET','C-HYPERGRAPH-WEIGHT60-V2-WARM01-SAVED-OBJECTS','C-BINARY-CODE-LENGTH99-EVEN36TO60-RATIONAL-DUAL-SIZE-BOUND','C-UNRESTRICTED-TRIANGLE-INCIDENCE-BINARY-RANK-LOWER67','C-HYPERGRAPH-WEIGHT60-WARM01-TWO-GRAPH-WARM-ROOT-CENSUS','C-UNRESTRICTED-TRIANGLE-INCIDENCE-BINARY-RANK-LOWER76']
REPORTS={
 'gf2':('acceleration/results/20261003_independent_review/root8_mod2_full01/summary.json','410e7e4dd7f4e9caff1f9eb8b349a35afd24808e44826e7d1dc89d4a0b7249c2'),
 'warm':('acceleration/results/20261003_independent_review/weight60_warm01/summary.json','256c8277ab5c69e74f4c9725c4b42e96e31b4e546c490b8e231df4ed6831bf6c'),
 'roots':('acceleration/results/20261003_independent_review/weight60_warm_roots_dense01/summary.json','becf048cbb32ec577a78c7084fc949103af91f66c92c5936137a9740c5cdd35a'),
 'code':('acceleration/results/20261003_independent_review/incidence_code_dual_full01/summary.json','ca60194f888e4aa8f97792e26e7196b09ac720e4dd683c479a22faf8f4a8a816'),
 'public_receipt':('acceleration/results/20261003_wave37_public_confirmation01/receipt.json','786f1ee2c5715ceb41115e4412f47386273ea66191140271feed89a46873d72e'),
 'public_audit':('acceleration/results/20261003_independent_review/wave37_availability01/summary.json','b6b4fcd4531af9c366e98329e309e53be160bd9d07c1e4b003f0520bf2412d03'),
}
PACKAGES={
 'acceleration/results/20261002_wave33_model_package01/manifest.json':'c3efa198c5f48eddb5ead69a4bb130a3dc55567bb298856143c6fb62eb0e0145',
 'acceleration/results/20261002_wave33_reconstruction_package01/manifest.json':'f639431b7ea9ce0f1500ea48b002629d2523271eead700217dd512e8ade66989',
 'acceleration/results/20261003_wave36_coupling_package01/manifest.json':'38f641ec21ec3d1d617515e8b3e578e098886863f7016ad640ac1906e8b0988f',
 'acceleration/results/20261003_wave37_rooted8_package01/manifest.json':'ea48c30dfa68fe70bad17edbfd3697d8a2dcf28f9ab24b63d0d66895e7eb9b14',
}
DOCS=['README.md','ACTIVE_RESEARCH.md','docs/RESEARCH_MAP.md','docs/REPRODUCING.md']
MILESTONE='docs/RESEARCH_20261003_THIRTYEIGHTH_WAVE.md'
SPEC='acceleration/record_20261003_wave38_milestone_v2_spec.md'
EXTRA_FILES=[
 '.gitattributes',
 'docs/AUDIT_20261003_WAVE37_PUBLICATION_CONFIRMED.md',
 'acceleration/register_20261003_bound_claims_v11.py','acceleration/register_20261003_bound_claims_v11_spec.md','acceleration/register_20261003_bound_claims_v11_2.py','acceleration/register_20261003_bound_claims_v11_2_spec.md',
 'acceleration/register_20261003_bound_claims_v12.py','acceleration/register_20261003_bound_claims_v12_spec.md','acceleration/register_20261003_bound_claims_v12_adapter_block.txt',
 'acceleration/calibrate_20261003_registrar_v11_helpers_v1.py','acceleration/calibrate_20261003_registrar_v11_helpers_v1_spec.md','acceleration/calibrate_20261003_registrar_v11_helpers_v2.py','acceleration/calibrate_20261003_registrar_v11_helpers_v2_spec.md','acceleration/calibrate_20261003_registrar_v12_helpers_v1.py','acceleration/calibrate_20261003_registrar_v12_helpers_v1_spec.md',
 'acceleration/audit_20261003_registrar_v11_engineering_v1.py','acceleration/audit_20261003_registrar_v11_engineering_v1_spec.md','acceleration/audit_20261003_registrar_v12_engineering_v1.py','acceleration/audit_20261003_registrar_v12_engineering_v1_spec.md',
 'acceleration/audit_20261003_wave38_transition_v1.py','acceleration/audit_20261003_wave38_transition_v1_spec.md','acceleration/audit_20261003_wave38_transition_v2.py','acceleration/audit_20261003_wave38_transition_v2_spec.md',
 'acceleration/confirm_20261003_wave37_publication_v1.py','acceleration/confirm_20261003_wave37_publication_v1_spec.md','acceleration/audit_20261003_wave37_availability_v1.py','acceleration/audit_20261003_wave37_availability_v1_spec.md',
]
EXTRA_ROOTS=[
 'acceleration/results/20261003_wave38_registration01','acceleration/results/20261003_wave38_registration02','acceleration/results/20261003_wave38_registration03','acceleration/results/20261003_wave38_registration04',
 'acceleration/results/20261003_wave38_registration_supervision01','acceleration/results/20261003_wave38_registration_supervision02','acceleration/results/20261003_wave38_registration_supervision03','acceleration/results/20261003_wave38_registration_supervision04',
 'acceleration/results/20261003_registrar_v11_author_controls01','acceleration/results/20261003_registrar_v11_author_controls02','acceleration/results/20261003_registrar_v11_author_controls_supervision01','acceleration/results/20261003_registrar_v11_author_controls_supervision02',
 'acceleration/results/20261003_registrar_v12_author_controls01','acceleration/results/20261003_registrar_v12_author_controls_supervision01',
 'acceleration/results/20261003_independent_review/registrar_v11_engineering01','acceleration/results/20261003_independent_review/registrar_v11_engineering_supervision01','acceleration/results/20261003_independent_review/registrar_v12_engineering01','acceleration/results/20261003_independent_review/registrar_v12_engineering_supervision01',
 'acceleration/results/20261003_independent_review/wave38_transition01','acceleration/results/20261003_independent_review/wave38_transition02','acceleration/results/20261003_independent_review/wave38_transition_supervision01','acceleration/results/20261003_independent_review/wave38_transition_supervision02',
 'acceleration/results/20261003_wave37_public_confirmation01','acceleration/results/20261003_wave37_public_confirmation_supervision01',
 'acceleration/results/20261003_independent_review/wave37_availability01','acceleration/results/20261003_independent_review/wave37_availability_supervision01','acceleration/results/20261003_independent_review/wave37_availability_calibration01','acceleration/results/20261003_independent_review/wave37_availability_calibration_supervision01',
]
DENY=['incidence_low_weight','triangle_kernel_low_weight','rooted8_unrestricted_lp','rooted8_unrestricted_corner','wave39','local_trade_census','neighbor_census','incidence_kernel_nonzero']

def need(ok,why):
    if not ok:raise ValueError(why)
def sha(path):
    with path.open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def save(path,obj):
    with path.open('x',encoding='utf8',newline='\n')as stream:json.dump(obj,stream,indent=2);stream.write('\n')
def bounded(name):
    need(type(name)is str and name and not any(c in name for c in'\\\r\n\0'),'LITERAL_RELATIVE_PATH');p=PurePosixPath(name);need(not p.is_absolute()and'..'not in p.parts and not name.startswith('.git/'),'WORKSPACE_RELATIVE_PATH');need(name.startswith(('acceleration/','docs/'))or name in DOCS+['CLAIMS.yaml','pyproject.toml','uv.lock','.gitattributes','.github/workflows/claims.yml'],'RESEARCH_NAMESPACE');need(name=='docs/DESIGN_20261003_WEIGHT60_WARM_LOCAL_TRADE_CENSUS_V1.md'or not any(s in name.lower()for s in DENY),'EXCLUDED_QUEUED_WAVE39');need('/build/'not in name and'/recovered/'not in name,'EXCLUDED_BUILD_OR_DUPLICATE');r=(ROOT/name).resolve();need(r.is_relative_to(ROOT),'RESOLVED_BOUNDARY');return r
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--write-current-docs',action='store_true');args=ap.parse_args();deadline=CommandDeadline(args.seconds,allocation_reason='Fixed350 metadata/milestone/exact closure;120outer100worker20internal reserve; eight existing raw hashes, no science/package/index.');out=args.out.resolve();need(out.is_relative_to(ROOT),'OUTPUT_BOUNDARY');out.mkdir(parents=True,exist_ok=False);pins={};origins=defaultdict(set);expected={};omitted=[];docs_written=[]
    def tick():need(not deadline.status()['stop_required']and deadline.status()['remaining_seconds']>20,'NOT_COMPLETED_WITHIN_ALLOCATION')
    def pin(name,identity=None):
        tick();value=sha(bounded(name));need(identity is None or value==identity,'EXACT_INPUT_HASH:'+name);need(name not in pins or pins[name]==value,'UNCHANGED_FROZEN_INPUT:'+name);pins[name]=value;return value
    def add(name,origin,identity=None):
        bounded(name);origins[name].add(origin)
        if identity is not None:need(name not in expected or expected[name]==identity,'CONSISTENT_EXPECTED_HASH');expected[name]=identity
    def read(name,identity):pin(name,identity);add(name,'exact saved report',identity);return json.loads(bounded(name).read_bytes())
    try:
        raw=(ROOT/'CLAIMS.yaml').read_bytes();pin('CLAIMS.yaml',LEDGER);pin(BEFORE,BEFORE_SHA);current=registry.read_ledger(ROOT/'CLAIMS.yaml');before=registry.read_ledger(ROOT/BEFORE);new=current['claims'][343:];need(len(before['claims'])==343 and len(current['claims'])==350 and current['claims'][:343]==before['claims']and[c['id']for c in new]==IDS,'EXACT343_TO350_CLAIMS');counts=dict(Counter(c['status']for c in current['claims']));need(counts=={'VERIFIED':342,'CANDIDATE':3,'REFUTED':5}and all(c['review_state']=='CLEAR'for c in current['claims']),'EXACT_CURRENT_TOTALS');need(current['target']==before['target']and current['target']['status']=='UNKNOWN','TARGET_UNKNOWN_UNCHANGED')
        impact=read(IMPACT,IMPACT_SHA);need(impact['status']=='INDEPENDENT_WAVE38_EXACT343_TO350_TRANSITION_PASS'and impact['current_claims']==350 and impact['new_claim_ids']==IDS and impact['mathematical_replays']==0 and impact['new_exclusions']==0,'INDEPENDENT_IMPACT_SCOPE');reports={k:read(*v)for k,v in REPORTS.items()}
        artifact_ids={e for claim in new for e in claim['evidence']};artifacts={a['id']:a for a in current['artifacts']};need(artifact_ids<=set(artifacts),'COMPLETE_NEW_EVIDENCE_REFERENCES')
        for aid in artifact_ids:
            a=artifacts[aid]
            if a['path']is not None:add(a['path'],'seven registered exact claim evidence',a['sha256'])
        for name,identity in impact['inputs_sha256'].items():add(name,'independent complete350 impact input',identity)
        packaged={}
        for name,identity in PACKAGES.items():
            package=read(name,identity)
            for r in package['records']:
                need(r['raw_path']not in packaged,'EIGHT_DISTINCT_OLD_PACKAGE_INPUTS');packaged[r['raw_path']]=r;add(r['raw_path'],'old lossless raw input identity',r['raw_sha256']);offset=0
                for part in r['parts']:need(part['raw_offset']==offset,'LOSSLESS_PART_OFFSETS');offset+=part['raw_bytes'];add(part['path'],'existing exact lossless payload',part['gzip_sha256'])
                need(offset==r['raw_bytes'],'LOSSLESS_COMPLETE_RAW_BYTES')
        need(len(packaged)==8 and sum(r['raw_bytes']for r in packaged.values())==367261301,'EXACT_EIGHT_OLD_RAW_INPUTS')
        for name in EXTRA_FILES:add(name,'explicit metadata/publication source')
        for name in EXTRA_ROOTS:
            folder=bounded(name);need(folder.is_dir(),'EXPLICIT_COMPLETED_ROOT_EXISTS:'+name)
            for path in sorted(folder.rglob('*')):
                if path.is_file():add(path.relative_to(ROOT).as_posix(),'explicit completed metadata root')
        for name in['CLAIMS.yaml',BEFORE,Path(__file__).relative_to(ROOT).as_posix(),SPEC,'.gitattributes','acceleration/command_deadline.py','acceleration/run_compute_command.py','acceleration/validate_claims.py','docs/claims.schema.json','pyproject.toml','uv.lock']:add(name,'fixed metadata/runtime')
        gf=reports['gf2'];warm=reports['warm'];roots=reports['roots'];code=reports['code'];diag=warm['final_current_diagnostics'];need((gf['normalization_rows_checked'],gf['complete_scalar_primal_row_checks'],gf['profile_population'],gf['compatible_profiles'],gf['excluded_profiles'])==(86434,345736,651,651,0),'EXACT_GF2_RECORDED_POPULATIONS');need((warm['saved_state_files'],warm['complete_integer_saved_current_best_objects'],warm['first_lambda0_step'],diag['lambda_energy'],diag['mu_energy'],diag['identity_mismatches'])==(103,206,0,0,3480,4764),'EXACT_WARM_RECORDED_POPULATIONS');need((roots['raw_graphs'],roots['complete_roots'],roots['literal_triangle_population'])==(2,198,313698),'EXACT_ROOT_CENSUS_POPULATION');need(code['maximum_linear_dimension']==23 and code['conditional_incidence_rank_lower']==76,'EXACT_REGISTERED_CODE_BOUND')
        attributes_sha256=pin('.gitattributes');(out/'gitattributes.observed').write_bytes((ROOT/'.gitattributes').read_bytes())
        now=datetime.now(timezone.utc).isoformat();commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();checkpoint=dict(timestamp=now,source_commit=commit,previous_report='docs/RESEARCH_20261003_THIRTYSEVENTH_WAVE.md',ledger_sha256=LEDGER,before_ledger_sha256=BEFORE_SHA,attributes_sha256=attributes_sha256,attributes_observation='Post-append exact raw attributes; ROOT separately checks preserved prefix and narrow override suffix before publication.',claim_records=350,status_counts=counts,review_state_counts={'CLEAR':350},new_claim_revisions=[{k:c[k]for k in('id','revision','status','statement','scope')}for c in new],report_pins={k:dict(path=p,sha256=h)for k,(p,h)in REPORTS.items()},impact_report=IMPACT,impact_report_sha256=IMPACT_SHA,target_resolution='UNKNOWN',new_exclusions=0,overall_search_coverage='UNKNOWN; no validated denominator.',stage_populations=dict(gf2_profiles=651,gf2_exclusions=0,warm_state_files=103,warm_current_best_objects=206,root_census_graphs=2,root_census_roots=198),mathematical_replays=0,execution_observation=None,execution_observation_null_reason='This generator does not observe live workers; counted completed commands have separate actual terminal receipts.',queued_results_excluded='Later low-word/rank85, rooted8LP and next neighbor-census science are outside the350-claim cutoff.')
        (out/'CLAIMS.yaml').write_bytes(raw);save(out/'checkpoint.json',checkpoint)
        rows='\n'.join('| '+c['id']+' r1 | '+c['scope']['description']+' | [Audit](../'+c['verification'][0]['command_or_audit']+') |'for c in new)
        text=f'''# Thirty-eighth research milestone, 2026-10-03

Since [wave37](RESEARCH_20261003_THIRTYSEVENTH_WAVE.md), exactly seven scoped
revisions are added VERIFIED/CLEAR: unrestricted rooted8 parity, a graph-only
reset and checked warm objects/census, a generic exact code bound and two
conditional incidence rank lower bounds. No target graph, general proof or
new exclusion is added. Later queued records are outside this350-claim cutoff.

**As of:** {now}; source commit `{commit}`;
[checkpoint](../{out.relative_to(ROOT).as_posix()}/checkpoint.json),
[frozen350-record ledger](../{out.relative_to(ROOT).as_posix()}/CLAIMS.yaml),
previous343-record report. Source identity does not make later working artifacts
part of that commit.

**Verdict:** target resolution UNKNOWN; no independently validated target graph
or general nonexistence proof in this ledger. External candidate-resolution
review is not recorded. [PR3](https://github.com/ikuto32/conway-99-graph/pull/3)
is the review reference; no resolution merge is implied.

**Verified changes:**342VERIFIED/CLEAR,3CANDIDATE,5REFUTED;350CLEAR records.
All343 prior claims and artifact fields are preserved by the independent impact
audit. Generic code and target-conditional rank statements have distinct scopes.

| New revision | Exact scope | Evidence |
| --- | --- | --- |
{rows}

**Work completed:** rooted8 parity reconstructed86434primitive rows and checked
345736scalar components; all651 frozen profiles compatible, zero excluded.
The single seed61 warm invocation retained103state files,206complete checked
current/best objects and3literal matrices. Its complete two-graph census checked
198labelled roots; neither graph has a direct full-CN2 warm root. Final minima
are52at roots11,41,77; stepzero minimum50at81. These populations overlap and
are not summed. The exact generic13-weight code dual checked1287coefficients,
99rational coordinates and13inequalities, giving kernel dimension<=23 only
when its weight premise holds. Its target corollary is rankB>=76; the earlier
independent Griesmer argument gives>=67. Neither gives an upper rank.

**Coverage:** no new fixed-configuration branch exclusion. The prior frozen
branch union remains380of792literal configurations,412unresolved; branch count
does not measure all graphs or remaining effort. Overall search coverage:
UNKNOWN; no validated denominator.

**Best result in this named warm invocation:** E_lambda=0,E_mu=3480,
F60=60E_lambda+E_mu=3480 and ordinaryE=3480. This is128below its graph-only
stepzero input3608 for the same objective/domain. All693edges have one common
neighbor, but4764ordered integer identity entries fail. This is a non-SRG;
no global-best or performance claim. Seed/reset/counters differ from the old
pilot; the new first-lambda0 snapshot is step0, not the old step29380701.

**Problems and limits:** parity consistency is not integer count feasibility
or graph realization. The warm audit checks2147sparse anchored proposals and
retains900gaps; no complete trajectory/earliest-event claim. All original
failed guide/source/control/schema/impact records are retained. The generic
rank<=72 inference remains refuted; no graph-specific upper bound is supplied.
New wave38 evidence remains LOCAL_ONLY pending immutable publication checking.
Wave37's594artifact availability changes are separately confirmed PUBLIC by
[its addendum](AUDIT_20261003_WAVE37_PUBLICATION_CONFIRMED.md), preserving all343
material revisions. Older eight raw models remain retrievable through exact
lossless packages, without duplicate raw Git blobs; new normalized rows are
direct artifacts. Availability is separate from mathematical verification.

**Execution and next experiment:** counted runs have actual completed/reaped
receipts. This metadata generator makes no live process observation; current
live execution is UNKNOWN here. No continued search is inferred from edits.
The original fixed endpoint's239085labelled two-line proposal census has
completed and is queued outside this350-claim cutoff. Next concrete experiment
is a NEW, separately frozen complete proposal census of a retained neutral
neighbor, using a new raw input and independent validity/score reconstruction.
It must not repeat the original endpoint's completed census. The preserved
[design](DESIGN_20261003_WEIGHT60_WARM_LOCAL_TRADE_CENSUS_V1.md) supplies the
local-trade/neutral-walk context; this milestone launches no calculation.
Later rooted8LP/low-word/weightedcode and census outcomes are queued and
excluded from these seven revisions and publication core.

**References:** [complete350-impact audit](../{IMPACT}) and its saved four
registration/engineering receipts; [wave37 recovery](REPLAY_20261003_WAVE37_UNRESTRICTED_ROOTED8.md);
[publication receipt](../{REPORTS['public_receipt'][0]}) and
[independent availability audit](../{REPORTS['public_audit'][0]}).
'''
        need(not (ROOT/MILESTONE).exists(),'NEW_MILESTONE_ONLY');(ROOT/MILESTONE).write_text(text,encoding='utf8',newline='\n');docs_written.append(MILESTONE);add(MILESTONE,'new ledger-derived milestone')
        notice=f'''# Latest verified continuation checkpoint — wave38, 2026-10-03 JST

The [thirty-eighth milestone](docs/RESEARCH_20261003_THIRTYEIGHTH_WAVE.md) freezes350claims:
342VERIFIED/CLEAR,3CANDIDATE,5REFUTED. Seven exact additions retain UNKNOWN
target resolution and add no exclusion. The named seed61 warm graph has
E_lambda=0,E_mu=3480 and4764ordered identity failures; neither of its two
checked graphs supplies a direct warm root. All651rooted8 profiles survive
literal parity. Conditional incidence rank>=76 supplies no upper bound.
Overall search coverage: UNKNOWN; no validated denominator. Wave37 evidence
is separately PUBLIC; new wave38 evidence awaits immutable confirmation.
Later queued low-word/weightedcode/LP outcomes are outside this cutoff. This
notice makes no live process observation. Historical text follows unchanged.

'''
        for name in DOCS:
            path=ROOT/name;before_bytes=path.read_bytes();need(b'Latest verified continuation checkpoint \xe2\x80\x94 wave38'not in before_bytes,'NO_DUPLICATE_NOTICE');(out/(name.replace('/','_')+'.before')).write_bytes(before_bytes);adjusted=notice.replace('(docs/RESEARCH_','(RESEARCH_')if name.startswith('docs/')else notice;new_bytes=adjusted.encode('utf8')+before_bytes;(out/(name.replace('/','_')+'.prepared')).write_bytes(new_bytes)
            if args.write_current_docs:path.write_bytes(new_bytes);docs_written.append(name);add(name,'new notice with preserved historical suffix')
        # Design link is included as an explicit current frozen note only, with no
        # prospective census implementation or science output in this cutoff.
        add('docs/DESIGN_20261003_WEIGHT60_WARM_LOCAL_TRADE_CENSUS_V1.md','next experiment design only')
        index=Path(subprocess.check_output(['git','rev-parse','--git-path','index'],cwd=ROOT,text=True).strip());index=index if index.is_absolute()else ROOT/index;index_before=sha(index);records=[]
        for name in sorted(origins):
            tick();path=bounded(name);need(path.is_file(),'EXACT_ALLOWLIST_FILE_EXISTS:'+name)
            if name in packaged:r=packaged[name];identity=pin(name,r['raw_sha256']);need(path.stat().st_size==r['raw_bytes'],'EXACT_OLD_RAW_BYTE_LENGTH');omitted.append(dict(path=name,sha256=identity,bytes=r['raw_bytes'],fresh_hash_checked=True,reason='Previously published pinned lossless package; no duplicate raw blob.'));continue
            identity=pin(name,expected.get(name));need(path.stat().st_size<50*1024**2,'DIRECT50MIB_BOUND:'+name);records.append(dict(path=name,sha256=identity,bytes=path.stat().st_size,origins=sorted(origins[name])))
        need(sha(index)==index_before and sha(ROOT/'CLAIMS.yaml')==LEDGER,'LEDGER_INDEX_UNCHANGED');self_names=[p.relative_to(ROOT).as_posix()for p in sorted(out.iterdir())if p.is_file()]+[(out/'manifest.json').relative_to(ROOT).as_posix(),(out/'stage_paths.nul').relative_to(ROOT).as_posix()];names=sorted({r['path']for r in records}|set(self_names));(out/'stage_paths.nul').write_bytes(b''.join(n.encode('utf8')+b'\0'for n in names));save(out/'manifest.json',dict(schema='WAVE38_FIXED350_EXPLICIT_PUBLICATION_ALLOWLIST_V1',timestamp=now,source_commit=commit,ledger_sha256=LEDGER,before_ledger_sha256=BEFORE_SHA,current_claims=350,previous_claims=343,new_claim_ids=IDS,records=records,direct_record_count=len(records),direct_bytes=sum(r['bytes']for r in records),omitted=omitted,old_lossless_packages=PACKAGES,stage_paths_sha256=sha(out/'stage_paths.nul'),stage_paths_count=len(names),self_metadata_paths=self_names,inputs_sha256=pins,docs_written=docs_written,ledger_mutated=False,index_mutated=False,availability_changed=False,mathematical_replay=False,scientific_launched=False,queued_wave39_excluded=DENY,deadline=deadline.status(),limitations=['Exact closed350cutoff; no staging/publication or PUBLIC promotion.','Large existing raw identities hashed and lossless package pieces retained, not recompressed.','Current live worker state is not inferred; saved receipts determine completed counted work.']));print(json.dumps(dict(status='WAVE38_FIXED350_MILESTONE_EXPLICIT_ALLOWLIST_PREPARED',manifest_sha256=sha(out/'manifest.json'),direct_records=len(records),omitted_raw=len(omitted),stage_paths=len(names))))
    except BaseException as error:
        save(out/'failure.json',dict(exception=type(error).__name__,diagnostic=str(error),inputs_sha256=pins,docs_written=docs_written,ledger_mutated=False,index_mutated=False,mathematical_replay=False,scientific_launched=False,deadline=deadline.status(),restart='Preserve source/partial outputs; ROOT reviews correction/new version before a new contained invocation.'));raise
if __name__=='__main__':main()
