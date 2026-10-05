"""Exact343 allowlist raw-byte index check; shadow index by default, no commit."""
import argparse,copy,hashlib,json,os,shutil,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path,PurePosixPath
from command_deadline import CommandDeadline
ROOT=Path(__file__).resolve().parents[1]
LEDGER='af2af9811e0f701648095a31ebfeaad3cd956e2d332c09cc4344bdaa3f496a90'
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
    need(m['schema']=='WAVE37_INCREMENTAL_EXACT_EVIDENCE_ALLOWLIST_V2' and m['current_claims']==343 and m['previous_claims']==337 and m['ledger_sha256']==ledger==LEDGER and m['index_mutated'] is False and m['mathematical_replay'] is False,'EXACT343_SCOPE')
    need(m['gitattributes_sha256']==attrs,'EXACT_GIT_ATTRIBUTES')
    names=[r['path'] for r in m['records']];need(len(names)==len(set(names))==m['direct_record_count'] and sum(r['bytes'] for r in m['records'])==m['direct_bytes'],'UNIQUE_DIRECT_POPULATION')
    for r in m['records']:bounded(r['path']);need(r['bytes']<50*1024**2,'DIRECT50MIB_BOUND')
    omitted={r['path']:r for r in m['omitted']};need(len(omitted)==len(m['omitted'])==8 and not set(names)&set(omitted),'EXACT_EIGHT_OMISSIONS')
    need(all(r['fresh_hash_checked'] is True for r in omitted.values()),'OMITTED_IDENTITIES_CHECKED')
    return names,omitted
def parse_index(raw):
    out={}
    for q in raw.split(b'\0'):
        if q:
            meta,p=q.split(b'\t',1);mode,blob,stage=meta.decode().split();name=p.decode();need(stage=='0','NO_UNMERGED_INDEX');need(name not in out,'DUPLICATE_INDEX_ENTRY');out[name]=(mode,blob)
    return out
def save(p,v):
    with p.open('x',encoding='utf8',newline='\n') as f:json.dump(v,f,indent=2);f.write('\n')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--manifest',type=Path,required=True);ap.add_argument('--manifest-sha256',required=True);ap.add_argument('--ledger-sha256',required=True);ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--mode',choices=('shadow','apply'),default='shadow');args=ap.parse_args()
    d=CommandDeadline(args.seconds,allocation_reason='Exact343 evidence raw SHA256/Gitblob identities and isolated index control;240outer200worker20reserve no commit/publication')
    out=args.out.resolve();need(out.is_relative_to(ROOT),'OUTPUT_BOUNDARY');out.mkdir(parents=True,exist_ok=False)
    def tick():need(not d.status()['stop_required'] and d.status()['remaining_seconds']>20,'DEADLINE_RESERVE')
    def git(argv,env=None):tick();return subprocess.check_output(['git',*argv],cwd=ROOT,env=env,timeout=max(1,d.status()['remaining_seconds']-15),stderr=subprocess.PIPE)
    index=Path(git(['rev-parse','--git-path','index']).decode().strip());index=index if index.is_absolute() else ROOT/index;indexsha=ids(index)[1];original=parse_index(git(['ls-files','--stage','-z']));started=False
    try:
        mp=args.manifest.resolve();need(mp.is_relative_to(ROOT) and ids(mp)[1]==args.manifest_sha256,'EXACT_ALLOWLIST_MANIFEST');m=json.loads(mp.read_bytes());need(ids(ROOT/'CLAIMS.yaml')[1]==args.ledger_sha256,'LIVE_FROZEN_LEDGER')
        attrs=ids(ROOT/'.gitattributes')[1];names,omitted=validate_scope(m,args.ledger_sha256,attrs);packaged={}
        for p,h in m['packages'].items():
            need(ids(bounded(p))[1]==h,'EXACT_PACKAGE');pjson=json.loads(bounded(p).read_bytes())
            for r in pjson['records']:need(r['raw_path'] not in packaged,'DISTINCT_PACKAGE_RAW');packaged[r['raw_path']]=r
        need(set(packaged)==set(omitted) and all((r['raw_sha256'],r['raw_bytes'])==(omitted[p]['sha256'],omitted[p]['bytes']) for p,r in packaged.items()),'ALL_EXACT_PACKAGE_OMISSIONS')
        need(all(p not in original for p in omitted),'OMITTED_RAW_NOT_ALREADY_INDEXED')
        selfpaths=m['self_metadata_paths'];stages=sorted(set(names)|set(selfpaths));nul=mp.parent/'stage_paths.nul';need(ids(nul)[1]==m['stage_paths_sha256'] and nul.read_bytes()==b''.join(n.encode()+b'\0' for n in stages),'COMPLETE_EXACT_NUL')
        controls=[]
        for label,stage,change in [('wrong_claim_count','EXACT343_SCOPE',lambda x:x.update(current_claims=344)),('wrong_ledger','EXACT343_SCOPE',lambda x:x.update(ledger_sha256='0'*64)),('wrong_attribute','EXACT_GIT_ATTRIBUTES',lambda x:x.update(gitattributes_sha256='0'*64)),('large_direct','DIRECT50MIB_BOUND',lambda x:(x['records'][0].update(bytes=50*1024**2),x.update(direct_bytes=sum(r['bytes'] for r in x['records'])))),('duplicate_raw_stage','EXACT_EIGHT_OMISSIONS',lambda x:(x['records'][0].update(path=x['omitted'][0]['path']))),('unhashed_omission','OMITTED_IDENTITIES_CHECKED',lambda x:x['omitted'][0].update(fresh_hash_checked=False))]:
            bad=copy.deepcopy(m);change(bad)
            try:validate_scope(bad,args.ledger_sha256,attrs)
            except ValueError as e:need(str(e)==stage,'EXACT_CONTROL_STAGE:'+label);controls.append({'label':label,'stage':stage,'outcome':'REJECTED'})
            else:raise ValueError('CONTROL_FALSE_ACCEPT:'+label)
        expected={}
        for r in m['records']:
            tick();size,h,blob=ids(bounded(r['path']));need((size,h)==(r['bytes'],r['sha256']),'EXACT_RAW_MEMBER:'+r['path']);expected[r['path']]=blob
        for p in selfpaths:expected[p]=ids(bounded(p))[2]
        source=Path(__file__).relative_to(ROOT).as_posix();expected[source]=ids(Path(__file__))[2];spec=Path(__file__).with_name(Path(__file__).stem+'_spec.md').relative_to(ROOT).as_posix();expected[spec]=ids(ROOT/spec)[2]
        stages=sorted(expected);exact=out/'exact_stage_paths.nul';exact.write_bytes(b''.join(n.encode()+b'\0' for n in stages));env=os.environ.copy();shadow=None
        if args.mode=='shadow':
            shadow=ROOT/'build'/('wave37_'+out.name+'.index');need(not shadow.exists(),'FRESH_SHADOW_INDEX');shadow.parent.mkdir(exist_ok=True);shutil.copy2(index,shadow);env['GIT_INDEX_FILE']=str(shadow)
        started=True;git(['add','-f','--pathspec-from-file='+str(exact),'--pathspec-file-nul'],env);checked=parse_index(git(['ls-files','--stage','-z'],env))
        failures=[{'path':p,'expected_raw_blob':blob,'index_entry':checked.get(p)} for p,blob in expected.items() if checked.get(p,(None,None))[1]!=blob]
        outside=[p for p in set(original)|set(checked) if p not in expected and original.get(p)!=checked.get(p)];need(not outside,'ALL_UNSELECTED_INDEX_ENTRIES_UNCHANGED')
        need(all(p not in checked for p in omitted),'NO_LARGE_RAW_INDEX_BLOB')
        live_unchanged=ids(index)[1]==indexsha;need(args.mode!='shadow' or live_unchanged,'LIVE_INDEX_UNCHANGED_SHADOW');need(ids(ROOT/'CLAIMS.yaml')[1]==args.ledger_sha256,'LEDGER_UNCHANGED')
        report={'status':'WAVE37_EXACT343_'+args.mode.upper()+'_INDEX_RAW_BYTE_PASS' if not failures else 'WAVE37_INDEX_RAW_BYTE_VETO','timestamp':datetime.now(timezone.utc).isoformat(),'source_commit':git(['rev-parse','HEAD']).decode().strip(),'source_sha256':ids(Path(__file__))[1],'spec_sha256':ids(ROOT/spec)[1],'command':[sys.executable,*sys.argv],'cwd':str(ROOT),'manifest_sha256':args.manifest_sha256,'ledger_sha256':args.ledger_sha256,'gitattributes_sha256':attrs,'direct_records':len(m['records']),'indexed_paths_checked':len(expected),'raw_bytes_checked':m['direct_bytes'],'omitted_raw_count':len(omitted),'failures':failures,'controls':controls,'unselected_index_entries_changed':outside,'submodule_entries_preserved':all(checked.get(p)==q for p,q in original.items() if q[0]=='160000'),'live_index_mutated':not live_unchanged,'index_mode':args.mode,'index_before_sha256':indexsha,'index_after_sha256':ids(index)[1],'shadow_index_path':str(shadow) if shadow else None,'shadow_index_sha256':ids(shadow)[1] if shadow else None,'artifacts_changed':False,'mathematical_replay':False,'availability_changed':False,'committed':False,'published':False,'deadline':d.status()};save(out/'summary.json',report)
        need(not failures,'EXACT_INDEX_RAW_BYTES_VETO');print(json.dumps({'status':report['status'],'report_sha256':ids(out/'summary.json')[1],'indexed_paths':len(expected),'live_index_mutated':report['live_index_mutated']}),flush=True)
    except BaseException as e:
        save(out/'failure.json',{'error':repr(e),'index_operation_started':started,'mode':args.mode,'live_index_sha256':ids(index)[1],'index_before_sha256':indexsha,'deadline':d.status(),'no_commit_or_publication':True});raise
if __name__=='__main__':main()
