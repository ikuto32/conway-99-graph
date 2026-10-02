"""Exact353 allowlist raw-byte index check; preserved wave38 predecessor."""
import argparse,copy,hashlib,json,os,shutil,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path,PurePosixPath
from command_deadline import CommandDeadline
ROOT=Path(__file__).resolve().parents[1]
LEDGER='b2796504a736ef16872ee36812d3b8ddb6446d0ea28d4883525f9ab9a3dd5679'
BEFORE='ff94b87187d712bc2fce166b8afffaa3e2155db9fbdf8a4b3179b1f3fe2e304a'
INDEX='68b695ba680915be542d08a9522a2a3acd329f8fd05e471b35ae27a9e0523152'
ARCHIVE='external_conway99_research/attempts/wave102-prism-incidence-code/derivation.md'
ARCHIVE_SHA='df8841bee7f23b444186ab65947f77865ffb243363967dd56340207628f00c6f'
ARCHIVE_COMMIT='85e705cc6c2a14d123120c93a847e30aaab1789e'
ARCHIVE_REPOSITORY='https://github.com/YesterdaysLemon/conway-99-research'
CLAIM_IDS=['C-UNRESTRICTED-TRIANGLE-INCIDENCE-LOW-WEIGHT-IMAGE-COUNTS','C-UNRESTRICTED-TRIANGLE-INCIDENCE-BINARY-RANK-LOWER85','C-HYPERGRAPH-WEIGHT60-WARM01-FIXED-V2-TWO-LINE-CENSUS']
DENY=('seven_weight','incidence_low_weight_lp_v2','triangle_kernel_low_weight_lp_v2','divisible4','kernel_containment','projection_hull','kernel_self_orthogonal','incidence_kernel_nonzero','two_line_neighbor','neutral_census','root_start','root_focused','rooted8_unrestricted_lp','rooted8_unrestricted_corner')
def need(ok,stage):
    if not ok:raise ValueError(stage)
def bounded(name):
    need(type(name) is str and name and not any(c in name for c in '\\\n\r\0'),'LITERAL_PATH')
    p=PurePosixPath(name);need(not p.is_absolute() and '..' not in p.parts and not name.startswith('.git/'),'BOUNDED_PATH')
    need(name.startswith(('acceleration/','docs/')) or name in ('CLAIMS.yaml','README.md','ACTIVE_RESEARCH.md','.gitattributes','.github/workflows/claims.yml','pyproject.toml','uv.lock'),'EXACT_NAMESPACE')
    result=(ROOT/name).resolve();need(result.is_relative_to(ROOT),'RESOLVED_BOUNDARY');return result
def ids(p):
    size=p.stat().st_size;s=hashlib.sha256();g=hashlib.sha1(('blob '+str(size)+'\0').encode())
    with p.open('rb') as f:
        for c in iter(lambda:f.read(1024*1024),b''):s.update(c);g.update(c)
    return size,s.hexdigest(),g.hexdigest()
def validate_scope(m,ledger,attrs):
    need(m['schema']=='WAVE39_FIXED353_EXPLICIT_PUBLICATION_ALLOWLIST_V1' and m['current_claims']==353 and m['previous_claims']==350 and m['ledger_sha256']==ledger==LEDGER and m['before_ledger_sha256']==BEFORE and m['new_claim_ids']==CLAIM_IDS and m['index_mutated'] is False and m['mathematical_replay'] is False and m['scientific_launched'] is False and m['availability_changed'] is False,'EXACT353_SCOPE')
    need(m['inputs_sha256'].get('.gitattributes')==attrs,'EXACT_GIT_ATTRIBUTES')
    need(all(type(m[k]) is int for k in ('current_claims','previous_claims','direct_record_count','direct_bytes')) and all(type(r['bytes']) is int for r in m['records']),'LITERAL_POPULATION_COUNTS')
    names=[r['path'] for r in m['records']];need(len(names)==len(set(names))==m['direct_record_count'] and sum(r['bytes'] for r in m['records'])==m['direct_bytes'],'UNIQUE_DIRECT_POPULATION')
    for r in m['records']:
        bounded(r['path']);need(r['bytes']<50*1024**2,'DIRECT50MIB_BOUND')
        need(not any(s in r['path'].lower() for s in DENY),'NO_LATER_SCIENCE_MEMBER')
    omitted={r['path']:r for r in m['omitted']};need(len(omitted)==len(m['omitted'])==9 and not set(names)&set(omitted) and '.git/index' in omitted,'EXACT_EIGHT_RAW_PLUS_INDEX_OMISSIONS')
    need(omitted.pop('.git/index')['sha256']==INDEX,'EXACT_HISTORICAL_INDEX_OMISSION')
    need(all(m['inputs_sha256'].get(p)==r['sha256'] for p,r in omitted.items()),'OMITTED_IDENTITIES_CHECKED')
    refs=m['historical_external_sources'];need(type(refs) is list and len(refs)==1,'EXACT_ONE_ARCHIVED_REFERENCE');r=refs[0]
    need([r.get(k) for k in ('path','sha256','repository','commit','external_path','git_blob_sha256')]==[ARCHIVE,ARCHIVE_SHA,ARCHIVE_REPOSITORY,ARCHIVE_COMMIT,ARCHIVE.split('/',1)[1],ARCHIVE_SHA] and r.get('git_blob_rehashed') is True and r.get('retrieval')==ARCHIVE_REPOSITORY+'/blob/'+ARCHIVE_COMMIT+'/'+ARCHIVE.split('/',1)[1],'EXACT_ARCHIVED_REFERENCE')
    return names,omitted

def controls(m,ledger,attrs):
    validate_scope(m,ledger,attrs);records=[dict(label='valid_exact353_scope',outcome='PASS')]
    changes=[('wrong_claim_count','EXACT353_SCOPE',lambda x:x.update(current_claims=354)),('wrong_ledger','EXACT353_SCOPE',lambda x:x.update(ledger_sha256='0'*64)),('wrong_baseline','EXACT353_SCOPE',lambda x:x.update(before_ledger_sha256='0'*64)),('wrong_ids','EXACT353_SCOPE',lambda x:x.update(new_claim_ids=CLAIM_IDS[:-1])),('wrong_attribute','EXACT_GIT_ATTRIBUTES',lambda x:x['inputs_sha256'].update({'.gitattributes':'0'*64})),('large_direct','DIRECT50MIB_BOUND',lambda x:(x['records'][0].update(bytes=50*1024**2),x.update(direct_bytes=sum(r['bytes'] for r in x['records'])))),('duplicate_raw_stage','EXACT_EIGHT_RAW_PLUS_INDEX_OMISSIONS',lambda x:x['records'][0].update(path=next(r['path'] for r in x['omitted'] if r['path']!='.git/index'))),('unhashed_omission','OMITTED_IDENTITIES_CHECKED',lambda x:x['inputs_sha256'].update({next(r['path'] for r in x['omitted'] if r['path']!='.git/index'):'0'*64})),('floating_count','LITERAL_POPULATION_COUNTS',lambda x:x.update(current_claims=353.0)),('wrong_index_omission','EXACT_HISTORICAL_INDEX_OMISSION',lambda x:next(r for r in x['omitted'] if r['path']=='.git/index').update(sha256='0'*64)),('missing_archive','EXACT_ONE_ARCHIVED_REFERENCE',lambda x:x.update(historical_external_sources=[])),('wrong_archive_commit','EXACT_ARCHIVED_REFERENCE',lambda x:x['historical_external_sources'][0].update(commit='0'*40)),('wrong_archive_repository','EXACT_ARCHIVED_REFERENCE',lambda x:x['historical_external_sources'][0].update(repository='https://github.com/other/other')),('wrong_archive_blob','EXACT_ARCHIVED_REFERENCE',lambda x:x['historical_external_sources'][0].update(git_blob_sha256='0'*64)),('later_science','NO_LATER_SCIENCE_MEMBER',lambda x:x['records'][0].update(path='acceleration/root_focused_unapproved.py')),('traversal','BOUNDED_PATH',lambda x:x['records'][0].update(path='../CLAIMS.yaml')),('submodule_payload','EXACT_NAMESPACE',lambda x:x['records'][0].update(path=ARCHIVE))]
    for label,stage,change in changes:
        bad=copy.deepcopy(m);change(bad)
        try:validate_scope(bad,ledger,attrs)
        except ValueError as e:need(str(e)==stage,'EXACT_CONTROL_STAGE:'+label);records.append(dict(label=label,stage=stage,outcome='REJECTED'))
        else:raise ValueError('CONTROL_FALSE_ACCEPT:'+label)
    return records
def parse_index(raw):
    out={}
    for q in raw.split(b'\0'):
        if q:
            meta,p=q.split(b'\t',1);mode,blob,stage=meta.decode().split();name=p.decode();need(stage=='0','NO_UNMERGED_INDEX');need(name not in out,'DUPLICATE_INDEX_ENTRY');out[name]=(mode,blob)
    return out
def save(p,v):
    with p.open('x',encoding='utf8',newline='\n') as f:json.dump(v,f,indent=2);f.write('\n')

def calibration_fixture(attrs):
    omissions=[dict(path='acceleration/calibration_raw_'+str(i)+'.json',sha256='f'*64,bytes=i+1) for i in range(8)]+[dict(path='.git/index',sha256=INDEX)]
    reference=dict(path=ARCHIVE,sha256=ARCHIVE_SHA,repository=ARCHIVE_REPOSITORY,commit=ARCHIVE_COMMIT,external_path=ARCHIVE.split('/',1)[1],git_blob_sha256=ARCHIVE_SHA,git_blob_rehashed=True,retrieval=ARCHIVE_REPOSITORY+'/blob/'+ARCHIVE_COMMIT+'/'+ARCHIVE.split('/',1)[1],git_blob_bytes=1)
    return dict(schema='WAVE39_FIXED353_EXPLICIT_PUBLICATION_ALLOWLIST_V1',current_claims=353,previous_claims=350,ledger_sha256=LEDGER,before_ledger_sha256=BEFORE,new_claim_ids=CLAIM_IDS,index_mutated=False,mathematical_replay=False,scientific_launched=False,availability_changed=False,inputs_sha256={'.gitattributes':attrs,**{r['path']:r['sha256'] for r in omissions if r['path']!='.git/index'}},records=[dict(path='CLAIMS.yaml',bytes=1,sha256=LEDGER)],direct_record_count=1,direct_bytes=1,omitted=omissions,historical_external_sources=[reference])
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--manifest',type=Path);ap.add_argument('--manifest-sha256');ap.add_argument('--ledger-sha256',required=True);ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--mode',choices=('calibrate','shadow','apply'),default='shadow');ap.add_argument('--shadow-report',type=Path);ap.add_argument('--shadow-report-sha256');ap.add_argument('--calibration',type=Path);ap.add_argument('--calibration-sha256');args=ap.parse_args()
    d=CommandDeadline(args.seconds,allocation_reason='Exact353 raw-byte/archived source controls;180outer150worker calibration or240outer200worker staging,20save reserve no commit/publication')
    out=args.out.resolve();need(out.is_relative_to(ROOT),'OUTPUT_BOUNDARY');out.mkdir(parents=True,exist_ok=False)
    def tick():need(not d.status()['stop_required'] and d.status()['remaining_seconds']>20,'DEADLINE_RESERVE')
    def git(argv,env=None):tick();return subprocess.check_output(['git',*argv],cwd=ROOT,env=env,timeout=max(1,d.status()['remaining_seconds']-15),stderr=subprocess.PIPE)
    index=Path(git(['rev-parse','--git-path','index']).decode().strip());index=index if index.is_absolute() else ROOT/index;indexsha=ids(index)[1];original=parse_index(git(['ls-files','--stage','-z']));started=False
    try:
        source=Path(__file__).relative_to(ROOT).as_posix();spec=Path(__file__).with_name(Path(__file__).stem+'_spec.md').relative_to(ROOT).as_posix();source_sha=ids(ROOT/source)[1];spec_sha=ids(ROOT/spec)[1];attrs=ids(ROOT/'.gitattributes')[1]
        need(ids(ROOT/'CLAIMS.yaml')[1]==args.ledger_sha256==LEDGER and indexsha==INDEX,'FROZEN353_LEDGER_AND_INDEX')
        if args.mode=='calibrate':
            tested=controls(calibration_fixture(attrs),LEDGER,attrs);need(ids(index)[1]==indexsha,'CALIBRATION_INDEX_UNCHANGED')
            save(out/'summary.json',dict(status='WAVE39_EXACT353_STAGING_CALIBRATION_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_sha256=source_sha,spec_sha256=spec_sha,gitattributes_sha256=attrs,ledger_sha256=LEDGER,index_before_sha256=indexsha,controls=tested,positive_scope_controls=1,strict_corruptions=17,producer_manifest_inspected=False,index_operation_started=False,mathematical_replay=False,command=[sys.executable,*sys.argv],cwd=str(ROOT),deadline=d.status()));return
        need(args.calibration and args.calibration_sha256 and ids(args.calibration)[1]==args.calibration_sha256,'EXACT_STAGING_CALIBRATION');cal=json.loads(args.calibration.read_bytes());need(cal['status']=='WAVE39_EXACT353_STAGING_CALIBRATION_PASS' and cal['source_sha256']==source_sha and cal['spec_sha256']==spec_sha and cal['gitattributes_sha256']==attrs and cal['ledger_sha256']==LEDGER and cal['index_before_sha256']==indexsha,'UNCHANGED_STAGING_CALIBRATION')
        need(args.manifest and args.manifest_sha256,'EXACT_MANIFEST_ARGUMENTS')
        mp=args.manifest.resolve();need(mp.is_relative_to(ROOT) and ids(mp)[1]==args.manifest_sha256,'EXACT_ALLOWLIST_MANIFEST');m=json.loads(mp.read_bytes());need(ids(ROOT/'CLAIMS.yaml')[1]==args.ledger_sha256,'LIVE_FROZEN_LEDGER')
        names,omitted=validate_scope(m,args.ledger_sha256,attrs);packaged={}
        reference=m['historical_external_sources'][0];need(git(['-C','external_conway99_research','rev-parse','HEAD']).decode().strip()==ARCHIVE_COMMIT,'PINNED_ARCHIVE_HEAD');external_bytes=git(['-C','external_conway99_research','cat-file','blob',ARCHIVE_COMMIT+':'+ARCHIVE.split('/',1)[1]]);need(hashlib.sha256(external_bytes).hexdigest()==ARCHIVE_SHA and len(external_bytes)==reference['git_blob_bytes'] and (ROOT/ARCHIVE).read_bytes()==external_bytes,'EXACT_EXTERNAL_GIT_BLOB_AND_WORKSPACE')
        for p,h in m['old_lossless_packages'].items():
            need(ids(bounded(p))[1]==h,'EXACT_PACKAGE');pjson=json.loads(bounded(p).read_bytes())
            for r in pjson['records']:need(r['raw_path'] not in packaged,'DISTINCT_PACKAGE_RAW');packaged[r['raw_path']]=r
        need(set(packaged)==set(omitted) and all((r['raw_sha256'],r['raw_bytes'])==(omitted[p]['sha256'],omitted[p]['bytes']) for p,r in packaged.items()),'ALL_EXACT_PACKAGE_OMISSIONS')
        need(all(p not in original for p in omitted),'OMITTED_RAW_NOT_ALREADY_INDEXED')
        selfpaths=m['self_metadata_paths'];need(type(selfpaths) is list and len(selfpaths)==len(set(selfpaths)) and all(bounded(p).parent==mp.parent for p in selfpaths),'EXACT_LOCAL_SELF_METADATA');stages=sorted(set(names)|set(selfpaths));nul=mp.parent/'stage_paths.nul';need(type(m['stage_paths_count']) is int and len(stages)==m['stage_paths_count'] and ids(nul)[1]==m['stage_paths_sha256'] and nul.read_bytes()==b''.join(n.encode()+b'\0' for n in stages),'COMPLETE_EXACT_NUL')
        tested_controls=controls(m,args.ledger_sha256,attrs)
        expected={}
        for r in m['records']:
            tick();size,h,blob=ids(bounded(r['path']));need((size,h)==(r['bytes'],r['sha256']),'EXACT_RAW_MEMBER:'+r['path']);expected[r['path']]=blob
        for p in selfpaths:expected[p]=ids(bounded(p))[2]
        extra_paths=[
            'acceleration/prepare_20261003_wave39_attributes_v1.py',
            'acceleration/results/20261003_wave39_attribute_plan01/proposal.json',
            'acceleration/results/20261003_wave39_attribute_plan01/gitattributes.before',
            'acceleration/results/20261003_wave39_attribute_plan01/proposed_suffix.txt',
            *['acceleration/results/20261003_wave39_milestone_supervision01/'+n for n in ('manifest.json','summary.json','stdout.log','stderr.log','progress.jsonl')],
            *['acceleration/results/20261003_wave39_milestone_controls_supervision01/'+n for n in ('manifest.json','summary.json','stdout.log','stderr.log','progress.jsonl')],
            *['acceleration/results/20261003_wave39_registry_validation_supervision01/'+n for n in ('manifest.json','summary.json','stdout.log','stderr.log','progress.jsonl')],
            *['acceleration/results/20261003_wave39_registry_controls_supervision01/'+n for n in ('manifest.json','summary.json','stdout.log','stderr.log','progress.jsonl')],
            'acceleration/results/20261003_wave39_registry_validation01.json',
            args.calibration.resolve().relative_to(ROOT).as_posix(),
            *[(args.calibration.parent.parent/'wave39_stage_calibration_supervision01'/n).relative_to(ROOT).as_posix() for n in ('manifest.json','summary.json','stdout.log','stderr.log','progress.jsonl')]]
        for name in extra_paths:expected[name]=ids(bounded(name))[2]
        source=Path(__file__).relative_to(ROOT).as_posix();expected[source]=ids(Path(__file__))[2];spec=Path(__file__).with_name(Path(__file__).stem+'_spec.md').relative_to(ROOT).as_posix();expected[spec]=ids(ROOT/spec)[2]
        if args.mode=='apply':
            need(args.shadow_report and args.shadow_report_sha256 and ids(args.shadow_report)[1]==args.shadow_report_sha256,'EXACT_PRIOR_SHADOW_GATE')
            gate=json.loads(args.shadow_report.read_bytes())
            need(gate['status']=='WAVE39_EXACT353_SHADOW_INDEX_RAW_BYTE_PASS' and gate['manifest_sha256']==args.manifest_sha256
                 and gate['ledger_sha256']==LEDGER and gate['source_sha256']==ids(Path(__file__))[1]
                 and gate['spec_sha256']==ids(ROOT/spec)[1] and gate['index_before_sha256']==indexsha
                 and gate['gitattributes_sha256']==attrs and gate['live_index_mutated'] is False and not gate['failures'] and gate['staging_calibration_sha256']==args.calibration_sha256,'APPLICABLE_UNCHANGED_SHADOW_GATE')
            for path in (args.shadow_report,args.shadow_report.parent/'exact_stage_paths.nul'):
                name=path.resolve().relative_to(ROOT).as_posix();bounded(name);expected[name]=ids(path)[2]
        stages=sorted(expected);exact=out/'exact_stage_paths.nul';exact.write_bytes(b''.join(n.encode()+b'\0' for n in stages));env=os.environ.copy();shadow=None
        if args.mode=='shadow':
            shadow=ROOT/'build'/('wave39_'+out.name+'.index');need(not shadow.exists(),'FRESH_SHADOW_INDEX');shadow.parent.mkdir(exist_ok=True);shutil.copy2(index,shadow);env['GIT_INDEX_FILE']=str(shadow)
        started=True;git(['add','-f','--pathspec-from-file='+str(exact),'--pathspec-file-nul'],env);checked=parse_index(git(['ls-files','--stage','-z'],env))
        failures=[{'path':p,'expected_raw_blob':blob,'index_entry':checked.get(p)} for p,blob in expected.items() if checked.get(p,(None,None))[1]!=blob]
        outside=[p for p in set(original)|set(checked) if p not in expected and original.get(p)!=checked.get(p)];need(not outside,'ALL_UNSELECTED_INDEX_ENTRIES_UNCHANGED')
        need(all(p not in checked for p in omitted),'NO_LARGE_RAW_INDEX_BLOB')
        live_unchanged=ids(index)[1]==indexsha;need(args.mode!='shadow' or live_unchanged,'LIVE_INDEX_UNCHANGED_SHADOW');need(ids(ROOT/'CLAIMS.yaml')[1]==args.ledger_sha256,'LEDGER_UNCHANGED')
        report={'status':'WAVE39_EXACT353_'+args.mode.upper()+'_INDEX_RAW_BYTE_PASS' if not failures else 'WAVE39_INDEX_RAW_BYTE_VETO','timestamp':datetime.now(timezone.utc).isoformat(),'source_commit':git(['rev-parse','HEAD']).decode().strip(),'staging_calibration_sha256':args.calibration_sha256,'source_sha256':ids(Path(__file__))[1],'spec_sha256':ids(ROOT/spec)[1],'command':[sys.executable,*sys.argv],'cwd':str(ROOT),'manifest_sha256':args.manifest_sha256,'ledger_sha256':args.ledger_sha256,'gitattributes_sha256':attrs,'direct_records':len(m['records']),'explicit_metadata_appendix_paths':extra_paths,'indexed_paths_checked':len(expected),'raw_bytes_checked':m['direct_bytes'],'omitted_raw_count':len(omitted),'failures':failures,'controls':tested_controls,'historical_external_sources_checked':m['historical_external_sources'],'historical_index_observations_omitted':1,'unselected_index_entries_changed':outside,'submodule_entries_preserved':all(checked.get(p)==q for p,q in original.items() if q[0]=='160000'),'live_index_mutated':not live_unchanged,'index_mode':args.mode,'index_before_sha256':indexsha,'index_after_sha256':ids(index)[1],'shadow_index_path':str(shadow) if shadow else None,'shadow_index_sha256':ids(shadow)[1] if shadow else None,'artifacts_changed':False,'mathematical_replay':False,'availability_changed':False,'committed':False,'published':False,'deadline':d.status()};save(out/'summary.json',report)
        need(not failures,'EXACT_INDEX_RAW_BYTES_VETO');print(json.dumps({'status':report['status'],'report_sha256':ids(out/'summary.json')[1],'indexed_paths':len(expected),'live_index_mutated':report['live_index_mutated']}),flush=True)
    except BaseException as e:
        save(out/'failure.json',{'error':repr(e),'index_operation_started':started,'mode':args.mode,'live_index_sha256':ids(index)[1],'index_before_sha256':indexsha,'deadline':d.status(),'no_commit_or_publication':True});raise
if __name__=='__main__':main()
