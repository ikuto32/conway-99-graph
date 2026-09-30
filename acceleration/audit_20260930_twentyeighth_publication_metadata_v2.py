"""Independent explicit publication closure. No producer imports or Git writes."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import argparse,copy,hashlib,json,re,subprocess,sys,time,traceback,zlib,yaml
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';I=B+'independent_review/';OUTBASE=B+'twentyeighth_artifact_packaging/'
CPG=I+'twentyeighth_checkpoint_v2/summary.json';RPG=I+'twentyeighth_recovery_replay_v4/summary.json';INV=B+'twentyeighth_candidate_inventory/inventory.json';MAN=B+'twentyeighth_raw_recovery/manifest.json';UPDATE=B+'twentyeighth_guide_update/receipt.json';GUIDE='docs/REPRODUCING_20260930_TWENTYEIGHTH_WAVE.md';SNAP=B+'resume/claims_at_twentyeighth_milestone.yaml'
PINS={CPG:'d4b74354bc31774f538e2a82ee858611922593c3415f3281ccb233a25c53000d',RPG:'a1d29e63f1c92d4b38ed351cbf66b83319d24907ecaf455b199dbf278d877891',INV:'0057d4f0101eb1e56516ade234840defb4be5b17d2b0a2b5e35bd85491b48ce1',MAN:'33b00a791e57a732a27d18061c52f1ac6b3e71d964d9bf03c1e986ae12c82c89',UPDATE:'ee492b54647b4bbe842df774f336d9332034a7b6ee2953b362bd06b20e96be99',GUIDE:'95b76d5f21e15d90ebc036a36e7f47eabaec91c548015a42ebf0f56d87ecd779',SNAP:'c2889537ea68b90736a5d51e13b6aafd6163b9a1e98d2f05eb1bd6e4331cf441','CLAIMS.yaml':'c2889537ea68b90736a5d51e13b6aafd6163b9a1e98d2f05eb1bd6e4331cf441','acceleration/stage_20260930_twentyeighth_evidence.py':'f61b1c42dcfa835132f431188254904febe6dc4ce656e2fecca6e2a3e773004b'}
FUTURE=('next64','NEXT64','four_builds','FOUR_BUILDS','four_serial_build','sizeclass16_affine_gram_gf3','SIZECLASS16_AFFINE_GRAM_GF3','sizeclass16_gf3_affine_weights','exact_eight_explicit_batch_v3','exact_eight_explicit_batch_proofs_v2')
ENTRY=['ACTIVE_RESEARCH.md','README.md','docs/RESEARCH_MAP.md','docs/REPRODUCING.md'];REGS=[B+'twentyeighth_'+s for s in ['initial_registration','kernel_sizeclass_registration','sizeclass_proof_registration','launcher_refutation_registration']]
MAPS={'inputs_sha256','input_hashes','output_hashes','artifact_hashes','audit_artifact_hashes','checked_input_bindings','outputs_sha256','input_sha256','checked_artifact_hashes'};HEX=re.compile('^[0-9a-f]{64}$');INPUTS={};INFO={}
def need(x,m):
    if not x:raise ValueError(m)
def safe(p):
    q=Path(p);q=q.resolve()if q.is_absolute()else(ROOT/q).resolve();need(q.is_relative_to(ROOT),'path escape');r=q.relative_to(ROOT).as_posix();need(not r.startswith('tools/')and q.name!='PROMPT.md'and r!=I+'hadamard_oriented_unknown/process.stdout.log','protected path');need(not any(t in r for t in FUTURE),'future cohort');need(q.suffix.lower()not in ['.pem','.key']and q.name.lower()not in ['.env','.env.local','credentials','credentials.json','id_rsa','id_ed25519'],'private file pattern');return q
def key(p):return safe(p).relative_to(ROOT).as_posix()
def info(p):
    if isinstance(p,str) and p in INFO:return INFO[p]
    p=key(p)
    if p not in INFO:
        q=safe(p)
        with q.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
        INFO[p]=dict(path=p,sha256=h,bytes=q.stat().st_size);INPUTS[p]=h
    return INFO[p]
def load(p):info(p);return json.loads(safe(p).read_bytes())
def bind(d):
    for p,h in d.items():need(info(p)['sha256']==h,'identity '+p)
def save(p,x):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def git(*args,data=None):return subprocess.run(['git',*args],cwd=ROOT,input=data,capture_output=True,check=True).stdout
def gzip_json(p):
    info(p);raw=safe(p).read_bytes();need(raw[:4]==b'\x1f\x8b\x08\x00'and raw[4:8]==b'\0'*4,'deterministic gzip header');d=zlib.decompressobj(31);v=d.decompress(raw)+d.flush();need(d.eof and not d.unused_data and not d.unconsumed_tail,'one full gzip member');x=json.loads(v);need(v==(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode(),'canonical reference JSON');return x
def guide_delta(u):
    need(u['inventory_path']==INV and u['inventory_sha256']==PINS[INV]and u['path']==GUIDE and u['scientific_entry_overrides']==0 and u['metadata_entry_overrides']==1,'only guide metadata override');bind(u['outputs_sha256']);bind({u['command'][1]:u['recorder_sha256']});old=B+'twentyeighth_guide_update/previous_guide.md';new=B+'twentyeighth_guide_update/final_guide.md';add=B+'twentyeighth_guide_update/recovery_addition.md';oldbytes=safe(old).read_bytes();newbytes=safe(new).read_bytes();addition=safe(add).read_bytes();need(newbytes==safe(GUIDE).read_bytes()and newbytes.count(addition)==1 and newbytes.replace(addition,b'',1)==oldbytes,'exact additive guide delta');need((len(oldbytes),info(old)['sha256'])==(u['old_bytes'],u['old_sha256'])and (len(newbytes),info(new)['sha256'])==(u['new_bytes'],u['new_sha256']),'old/new byte identities');return old
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--catalog-summary-sha256',required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic();bad=[]
    def reject(n,f):
        try:f()
        except(ValueError,KeyError,TypeError):bad.append(n);return
        raise ValueError('accepted corrupted metadata '+n)
    try:
        before_head=git('rev-parse','HEAD').decode().strip();before_index=git('ls-files','--stage','-z');bind(PINS);bind({OUTBASE+'summary.json':args.catalog_summary_sha256});summary=load(OUTBASE+'summary.json');bind(summary['output_hashes']);need(summary['status']=='TWENTYEIGHTH_EXPLICIT_PUBLICATION_INVENTORY_PASS','completed catalog')
        for p in [Path(__file__),Path(__file__).with_name(Path(__file__).stem+'_spec.md')]:info(p)
        cpg=load(CPG);rpg=load(RPG);need(cpg['status']=='INDEPENDENT_TWENTYEIGHTH_CHECKPOINT_CONSISTENCY_PASS'and rpg['status']=='INDEPENDENT_TWENTYEIGHTH_RECOVERY_REPLAY_METADATA_PASS','independent prerequisites');bind(cpg['inputs_sha256']);bind(rpg['inputs_sha256']);bind(rpg['outputs_sha256']);need((rpg['raw_originals'],rpg['raw_bytes'],rpg['gzip_streams'],rpg['planned_mathematical_commands'],rpg['actual_mathematical_replays'])==(47,524689195,47,8,0),'recovery/replay exact scope')
        ledger=yaml.safe_load(safe(SNAP).read_bytes());claims={c['id']:c for c in ledger['claims']};arts={a['id']:a for a in ledger['artifacts']};need(len(claims)==294 and Counter(c['status']for c in claims.values())==dict(VERIFIED=287,CANDIDATE=3,REFUTED=4),'294 cutoff');need(safe(SNAP).read_bytes()==safe('CLAIMS.yaml').read_bytes(),'unchanged live cutoff')
        cat=load(OUTBASE+'catalog.json');scope=load(OUTBASE+'scope.json');stage=load(OUTBASE+'stage_inventory.json');inventory=load(INV);manifest=load(MAN);update=load(UPDATE);oldguide=guide_delta(update)
        need(scope['claim_ids']==summary['claim_ids']and len(scope['claim_ids'])==8 and Counter(claims[c]['status']for c in scope['claim_ids'])==dict(VERIFIED=6,REFUTED=2),'exact cohort');need(scope['ledger_sha256']==PINS[SNAP]and not scope['preparation_only'],'frozen ledger/final catalog');need(not cat['mathematical_verification_performed'],'packager no math approval')
        expected_override=[dict(receipt_path=UPDATE,receipt_sha256=PINS[UPDATE],path=GUIDE,old_sha256=update['old_sha256'],new_sha256=update['new_sha256'],historical_path=oldguide)];need(cat['metadata_overrides']==expected_override,'single explicit guide override')
        selected={r['path']for r in cat['entries']};need(len(selected)==len(cat['entries'])==summary['selected_files'],'unique selected files');initial={r['path']for r in inventory['entries']};need(len(initial)==len(inventory['entries']),'frozen inventory unique')
        for row in inventory['entries']:
            p=oldguide if row['path']==GUIDE else row['path'];need(info(p)['sha256']==row['sha256']and info(p)['bytes']==row['bytes'],'frozen initial entry identity')
        # Scientific selection is the frozen inventory. Directory additions are
        # explicitly named metadata roots; never walk scientific roots afresh.
        metadata_dirs=[d for d in cat['exact_directories']if d not in inventory['explicit_directories']];expected=initial|set(cat['exact_files'])
        for d in metadata_dirs:
            need('twentyeighth_'in d,'wave28 metadata root');expected.update(key(p)for p in safe(d).rglob('*')if p.is_file())
        need(selected==expected,'exact immutable inventory plus named extras')
        for r in cat['entries']:
            need(info(r['path'])=={k:r[k]for k in ['path','sha256','bytes']},'current catalog bytes');need(r['availability']in ['LOCAL_ONLY','READY_FOR_PUBLICATION'],'honest availability')
        local={r['path']for r in cat['entries']if r['availability']=='LOCAL_ONLY'};public=selected-local;need(local=={r['path']for r in manifest['records']}and len(local)==47,'exact47 recovery-only raws');need(sum(info(p)['bytes']for p in local)==524689195,'raw total');need(len(public)==summary['public_research_files']and sum(info(p)['bytes']for p in public)==summary['public_research_bytes'],'public size/count');need(all(info(p)['bytes']<=10*1024**2 for p in public),'research10MiB ceiling')
        for r in manifest['records']:need(all(p['path']in public for p in r['parts']),'all compressed recovery streams public')
        need(all(arts[e]['path']in selected for c in scope['claim_ids']for e in claims[c]['evidence']),'all cohort evidence selected')
        refs=gzip_json(OUTBASE+'reference_checks.json.gz');records=[]
        for i,p in enumerate(refs['parts']):
            need(p['index']==i and p['record_offset']==len(records),'ordered reference offsets');need(info(p['path'])['sha256']==p['sha256']and info(p['path'])['bytes']==p['bytes']<=10*1024**2,'reference part identity');x=gzip_json(p['path']);need(x['index']==i and len(x['records'])==p['records'],'reference part size');records.extend(x['records'])
        need(len(records)==refs['record_count']==summary['reference_bindings']and len({r['path']for r in records})==refs['unique_referenced_files']==summary['unique_referenced_files'],'whole reference populations')
        wrappers={OUTBASE+p for p in ['catalog.json','git_byte_checks.json','ignored_public_files.json','reference_checks.json.gz','reference_diagnostics.json','scope.json']}|{p['path']for p in refs['parts']};rawstage={r['path']:r for r in stage['entries']};need(stage['paths']==sorted(rawstage)and set(rawstage)==public|wrappers,'exact stage payload');need(stage['wrapper_paths_to_add_separately']==[OUTBASE+'stage_inventory.json',OUTBASE+'summary.json'],'only two separate wrappers');need(not local.intersection(rawstage),'no raw originals staged')
        for p,r in rawstage.items():need(info(p)==r,'stage bytes')
        for p in wrappers|set(stage['wrapper_paths_to_add_separately']):need(info(p)['bytes']<=(32 if Path(p).name in ['catalog.json','stage_inventory.json','reference_checks.json.gz']else 10)*1024**2,'metadata ceiling')
        prior=load(cat['prior_catalog']['path']);bind({cat['prior_catalog']['path']:cat['prior_catalog']['sha256']});recoverable=set(prior['prior_recoverable_dependencies'])|{r['path']for r in prior['entries']if r['availability']=='LOCAL_ONLY'and 'recovery available'in r['limitation']};need(recoverable==set(cat['prior_recoverable_dependencies']),'prior recovery closure');tracked=set(git('ls-files','-z').decode().split('\0'));tools={r['path']for r in cat['local_tools']};need(tools=={'build/research-cadical195/source/build/cadical','build/rook-drat-checker/drat-trim.exe'},'only explicit tools')
        available=selected|tracked|recoverable|tools
        for r in records:need(info(r['path'])=={k:r[k]for k in ['path','sha256','bytes']}and (r['path']in available or r['path'].startswith('external_conway99_research/')),'exact retrievable reference')
        expected_refs=[];cache={}
        def resolve(name,h,origin,archive=False):
            if name in arts:need(arts[name]['sha256']==h,'artifact-ID hash');name=arts[name]['path']
            if origin in {d+'/validation.json'for d in REGS}and name.replace('\\','/')=='CLAIMS.yaml':name=origin.rsplit('/',1)[0]+'/CLAIMS.after.yaml'
            if origin==INV and name==GUIDE and h==update['old_sha256']:name=oldguide
            name=name.replace('\\','/');ck=(name,archive,origin.rsplit('/',1)[0])
            if not archive and name in INFO:r=info(name)
            elif ck in cache:r=info(cache[ck])
            else:
                q=Path(name);candidates=[q]if q.is_absolute()else([ROOT/'external_conway99_research'/name]if archive else[ROOT/name,safe(origin).parent/name]);found=[p.resolve()for p in candidates if p.is_file()];need(found,'unresolved reference '+origin+' '+name);p=key(found[0]);cache[ck]=p;r=info(p)
            need(r['sha256']==h,'reference exact expected bytes '+origin+' '+name);expected_refs.append(dict(origin=origin,**r))
        def walk(v,origin):
            if isinstance(v,list):
                for x in v:walk(x,origin)
            elif isinstance(v,dict):
                for k,x in v.items():
                    if k in MAPS and isinstance(x,dict):
                        for n,h in x.items():
                            if isinstance(h,str)and HEX.fullmatch(h):resolve(n,h,origin)
                    walk(x,origin)
                if isinstance(v.get('path'),str)and isinstance(v.get('sha256'),str)and HEX.fullmatch(v['sha256']):resolve(v['path'],v['sha256'],origin,'conway-99-research'in v.get('repository',''))
        for p in sorted(selected):
            if p.endswith('.json'):walk(load(p),p)
        for r in manifest['records']:
            for p in r['parts']:resolve(p['path'],p['gzip_sha256'],r['manifest']or MAN)
            resolve(r['path'],r['sha256'],r['manifest']or MAN)
        for cid in scope['claim_ids']:
            for eid in claims[cid]['evidence']:a=arts[eid];resolve(a['path'],a['sha256'],'CLAIMS.yaml')
        enc=lambda r:(r['origin'],r['path'],r['sha256'],r['bytes']);need(Counter(map(enc,records))==Counter(map(enc,expected_refs)),'independent exact reference multiset');need(load(OUTBASE+'reference_diagnostics.json')==dict(errors=[],count=0),'zero unhandled reference failures')
        supplements=['CLAIMS.yaml','.gitattributes','acceleration/stage_20260930_twentyeighth_evidence.py',B+'resume/twentyeighth_precommit_validation.json',B+'resume/twentyeighth_precommit_checks.json','acceleration/record_20260930_twentyeighth_precommit.py',B+'resume/twentyeighth_syntax.stdout.log',B+'resume/twentyeighth_syntax.stderr.log','acceleration/audit_20260930_twentyeighth_publication_metadata.py','acceleration/audit_20260930_twentyeighth_publication_metadata_spec.md']+ENTRY
        for suffix in ['', '_v2','_v3','_v4']:
            supplements += ['acceleration/audit_20260930_twentyeighth_recovery_replay'+suffix+'.py','acceleration/audit_20260930_twentyeighth_recovery_replay'+suffix+'_spec.md'];supplements += [key(p)for p in safe(I+'twentyeighth_recovery_replay'+suffix).rglob('*')if p.is_file()]
        for p in supplements:info(p)
        for p in ENTRY:need('TWENTYEIGHTH_WAVE'in safe(p).read_text(encoding='utf8'),'current wave28 entry pointers')
        validation=load(B+'resume/twentyeighth_precommit_validation.json');need(validation['valid']and not validation['errors'],'precommit validation');pre=load(B+'resume/twentyeighth_precommit_checks.json');need(info(B+'resume/twentyeighth_precommit_checks.json')['sha256']=='8bd8cfdd88e851d72b8c6143d440d1049a5744e6d835ac0007c23eebc0b7bf61','frozen precommit receipt');need(pre['registry_validation']['valid'] and pre['syntax']['actual_exit_code']==0 and not pre['mathematical_verification'],'recorded checks only');bind({pre['registry_validation']['path']:pre['registry_validation']['sha256'],pre['command'][1]:pre['source_sha256']});bind(pre['syntax']['outputs_sha256']);need(pre['syntax']['result']==dict(compiled_sources=1896,authenticated_preserved_failures=['acceleration/theory_20260930_count_interval_frechet.py'],selected_sources=1897,source_execution=False),'timestamped syntax population');need(len(pre['skipped_checks'])==2 and 'no unobserved pass asserted' in pre['skipped_checks'][1],'pending CI explicitly not passed');need(json.loads(safe(B+'resume/twentyeighth_syntax.stdout.log').read_bytes())==pre['syntax']['result'],'literal syntax receipt');need('includes later untracked' in pre['syntax']['scope'],'syntax census separate from publication')
        checkpaths=sorted(public|wrappers|set(stage['wrapper_paths_to_add_separately'])|set(supplements)|{key(Path(__file__)),key(Path(__file__).with_name(Path(__file__).stem+'_spec.md'))});actual=git('hash-object','--stdin-paths',data=('\n'.join(checkpaths)+'\n').encode()).decode().splitlines();need(len(actual)==len(checkpaths),'Git hash count');gitrows=[]
        for p,h in zip(checkpaths,actual):
            row=info(p);d=hashlib.sha1();d.update(b'blob '+str(row['bytes']).encode()+b'\0')
            with safe(p).open('rb')as f:
                for block in iter(lambda:f.read(1048576),b''):d.update(block)
            need(d.hexdigest()==h,'Git clean filter byte change '+p);gitrows.append(dict(path=p,sha256=row['sha256'],git_blob_sha1=h))
        gm={r['path']:r for r in gitrows};savedgit=load(OUTBASE+'git_byte_checks.json')['records'];need({r['path']for r in savedgit}==public and all(gm[r['path']]==r for r in savedgit),'saved/current Git bytes agree')
        reject('future file',lambda:safe('acceleration/results/20260930_exact_eight_next64/summary.json'));reject('private file',lambda:safe(I+'hadamard_oriented_unknown/process.stdout.log'));reject('protected prompt',lambda:safe('PROMPT.md'))
        damaged=dict(rawstage);damaged.pop(next(iter(damaged)));reject('missing stage entry',lambda:need(set(damaged)==public|wrappers,'exact set'));damaged=dict(rawstage);damaged[next(iter(local))]=info(next(iter(local)));reject('raw original staged',lambda:need(set(damaged)==public|wrappers,'exact set'));reject('missing reference',lambda:need(Counter(map(enc,records[:-1]))==Counter(map(enc,expected_refs)),'exact multiset'));du=copy.deepcopy(update);du['scientific_entry_overrides']=1;reject('scientific override',lambda:guide_delta(du));reject('oversize research',lambda:need(10*1024**2+1<=10*1024**2,'research limit'))
        need(git('ls-files','--stage','-z')==before_index and git('rev-parse','HEAD').decode().strip()==before_head,'read-only Git state');need(hashlib.sha256(safe('CLAIMS.yaml').read_bytes()).hexdigest()==PINS['CLAIMS.yaml'],'ledger unchanged');need(time.monotonic()-start<300,'bounded allocation')
        save(out/'git_byte_checks.json',gitrows);save(out/'controls.json',dict(rejected=bad));save(out/'reviewed_supplements.json',dict(paths=sorted(set(supplements)),research_metadata_only=True))
        result=dict(status='INDEPENDENT_TWENTYEIGHTH_PUBLICATION_METADATA_PASS',created_at=datetime.now(timezone.utc).isoformat(),command=[sys.executable,*sys.argv],cwd=str(ROOT),source_commit=before_head,total_claims=294,new_verified=6,new_refuted=2,selected_files=len(selected),public_research_files=len(public),public_research_bytes=summary['public_research_bytes'],local_originals=47,raw_bytes=524689195,gzip_members=47,planned_replays=8,actual_new_mathematical_replays=0,precommit_checks_scope=pre,unexecuted_predecessor='acceleration/audit_20260930_twentyeighth_publication_metadata.py',reference_bindings=len(records),unique_reference_files=len({r['path']for r in records}),reference_multiset_independently_reconstructed=True,stage_entries=len(rawstage),git_byte_paths_checked=len(checkpaths),checkpoint_gate=CPG,recovery_replay_gate=RPG,reviewed_supplements=sorted(set(supplements)),entry_documents=ENTRY,controls_rejected=bad,inputs_sha256=INPUTS,outputs_sha256={key(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(out.iterdir())if p.is_file()},shared_components=['No producer/catalog/restorer imports. Standard library and PyYAML; independent reference multiset and Git blob identities.','Prior independently authored checkpoint/recovery/replay gates supply authenticated scopes and literal decompression controls; all direct input hashes rechecked.'],limitations=['Metadata only; no mathematical reapproval, new proof replay or target conclusion.','Eight planned command vectors were not executed during publication preparation.','No Git index/commit/publication or ledger writes.','Single guide-inventory metadata update preserves original bytes and admits no scientific override.'],elapsed_seconds=time.monotonic()-start);save(out/'summary.json',result);print(json.dumps({k:result[k]for k in ['status','selected_files','public_research_files','reference_bindings','git_byte_paths_checked','elapsed_seconds']}))
    except BaseException as ex:save(out/'failure.json',dict(error=repr(ex),traceback=traceback.format_exc(),inputs_sha256=INPUTS));raise
if __name__=='__main__':main()
