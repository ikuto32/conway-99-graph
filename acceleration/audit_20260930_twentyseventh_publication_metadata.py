"""Independent wave27 publication metadata; read-only, no producer imports."""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import argparse, ast, shlex, copy, hashlib, json, re, subprocess, sys, time, zlib, yaml
ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_';I=B+'independent_review/';OUTBASE=B+'twentyseventh_artifact_packaging/'
PRIVATE=I+'hadamard_oriented_unknown/process.stdout.log'
HEX=re.compile(r'^[0-9a-f]{64}$')
MAPS={'inputs_sha256','input_hashes','output_hashes','artifact_hashes','audit_artifact_hashes','checked_input_bindings','outputs_sha256','input_sha256','checked_artifact_hashes'}
FUTURE=('next32','NEXT32','first12_union','FIRST12_UNION','explicit_batch_v2','explicit_batch_preparation_v2')
ENTRY_DOCS=['ACTIVE_RESEARCH.md','README.md','docs/RESEARCH_MAP.md','docs/REPRODUCING.md']
REGISTRATIONS=[B+'twentyseventh_'+s for s in ['pilot_registration','psd_candidate_registration','campaign_gates_registration','psd_promotion','first12_proof_registration','inventory_registration']]
PINS={
 OUTBASE+'summary.json':'2466bb665490b601969f67cd01d4a29999d3855a78afdd899ada68b783f78d55',
 OUTBASE+'catalog.json':'fd10bd3872a7699f7ea80e1072c697b300cdb9d0cf7cdb19dd1a0c898e6565a8',
 OUTBASE+'stage_inventory.json':'3cc6ef8000b1357c50bf560383f2baa3f2c805000ffe7b86863598efe49c943f',
 OUTBASE+'reference_checks.json.gz':'967cfaff882fb5417b7cd526c6fc1e093fe6f9ef84008c0aab5b32abba0e9a08',
 I+'twentyseventh_checkpoint/summary.json':'37d7d478c356b38d92364dea0f2f1f146706da866749a0824b805e077cd89ed9',
 B+'resume/twentyseventh_milestone_checkpoint.json':'ee5fb89ff01a69d3c7e6cb61809906a5ef4804dedb5890c2469e2412b687991c',
 B+'resume/claims_at_twentyseventh_milestone.yaml':'5ea04f21e5964b6f987d00a600a69d4472bfebdd0fea7f564e4dfec1af5cb237',
 'CLAIMS.yaml':'5ea04f21e5964b6f987d00a600a69d4472bfebdd0fea7f564e4dfec1af5cb237',
 B+'twentyseventh_raw_recovery/manifest.json':'d6d5e3933cd8294b4f4119c6ba495780a77cf19833ecb056598a863bbef11958',
 'acceleration/recover_20260930_twentyseventh_raw_artifacts.py':'6d0721e1c25411e0d661e782fff19719a9a887bea8e019f5ec55536f373c4183',
 'docs/REPRODUCING_20260930_TWENTYSEVENTH_WAVE.md':'785cda16e5b4f66a5d5faed3e93a32ea50a35f79d82b7be62c0c73d58c17d915',
 B+'resume/twentyseventh_replay_plan.json':'4ef581a068c07d40a8b445d95bc847f009af4dbf54ed9fb0ec4025e6d5ee7981',
 B+'twentyseventh_replay_validation/receipt.json':'9b55a652cec4938451955630b60a85f13bbc665776ff68cb5a2739ce3f21a14e',
 'acceleration/stage_20260930_twentyseventh_evidence.py':'736e0f9848ed07cfbbae748698a43b9bde50046dfa6ab97c19e9ee9bb66f6da9',
 B+'resume/twentyseventh_precommit_checks.json':'6f54971e0bb980b3713b51b0df3e62aa036cb090301fe5789f31ce0a8212b1ce',
}
SUPPLEMENTS=['CLAIMS.yaml','.gitattributes','acceleration/audit_20260930_twentyseventh_checkpoint.py','acceleration/audit_20260930_twentyseventh_checkpoint_spec.md',I+'twentyseventh_checkpoint/summary.json',I+'twentyseventh_checkpoint/checked_records.json',B+'resume/twentyseventh_precommit_validation.json','acceleration/stage_20260930_twentyseventh_evidence.py','acceleration/record_20260930_twentyseventh_replay.py']
REPLAY_DIR=B+'twentyseventh_replay_validation/'
REPLAY_NAMES=['exact_eight_next_lift','exact_eight_next_lift_object_calibration','exact_eight_next_lift_unsat','triplicate_psd_kernel_options','exact_eight_psd_screen','exact_eight_campaign','exact_eight_campaign_object_calibration','exact_eight_campaign_coverage_v2','exact_eight_campaign_inventory','exact_eight_first12_proofs']
SUPPLEMENTS += [REPLAY_DIR+n for n in ['receipt.json','manifest.json','checkpoint.json','summary.json']]+[REPLAY_DIR+n+suffix for n in REPLAY_NAMES for suffix in ['.summary.json','.stdout.log','.stderr.log']]
SUPPLEMENTS += [B+'resume/twentyseventh_precommit_checks.json']
INPUTS,INFO={},{}

def need(ok, msg):
    if not ok: raise ValueError(msg)


def safe(name):
    p = str(name).replace('\\','/')
    need(p != PRIVATE and Path(p).name != 'PROMPT.md' and not p.startswith('tools/'), 'protected path')
    q = Path(p)
    q = q.resolve() if q.is_absolute() else (ROOT/q).resolve()
    need(q.is_relative_to(ROOT), 'outside repository')
    relative=q.relative_to(ROOT).as_posix()
    need(relative != PRIVATE and not relative.startswith('tools/') and not any(t in relative for t in FUTURE), 'protected or future absolute path')
    return q


def key(q): return q.relative_to(ROOT).as_posix()


def info(name):
    cached_name=str(name).replace('\\','/')
    if cached_name in INFO:return INFO[cached_name]
    q = safe(name); p = key(q)
    if p not in INFO:
        with q.open('rb') as f: h = hashlib.file_digest(f,'sha256').hexdigest()
        INFO[p] = dict(path=p, sha256=h, bytes=q.stat().st_size)
        INPUTS[p] = h
    return INFO[p]


def load(name):
    info(name)
    return json.loads(safe(name).read_bytes())


def bind(mapping):
    for p,h in mapping.items(): need(info(p)['sha256']==h, 'hash mismatch: '+p)


def gzip_json(p):
    info(p); raw=safe(p).read_bytes()
    need(raw[:3]==b'\x1f\x8b\x08' and raw[3]==0 and raw[4:8]==b'\0'*4, 'deterministic gzip header')
    d=zlib.decompressobj(31); unpacked=d.decompress(raw)+d.flush()
    need(d.eof and not d.unused_data and not d.unconsumed_tail, 'single complete gzip member')
    obj=json.loads(unpacked)
    need(unpacked == (json.dumps(obj,sort_keys=True,separators=(',',':'))+'\n').encode(), 'canonical reference JSON')
    return obj


def write(p,obj):
    with p.open('x',encoding='utf8',newline='\n') as f: json.dump(obj,f,indent=2);f.write('\n')


def git(*args, data=None):
    p=subprocess.run(['git',*args],cwd=ROOT,input=data,capture_output=True,check=True)
    return p.stdout


def decode_member(raw):
    d=zlib.decompressobj(31);data=d.decompress(raw)+d.flush()
    need(d.eof and not d.unused_data and not d.unconsumed_tail,'complete single gzip member')
    return data


def recover_record(r):
    total=hashlib.sha256();offset=0
    with safe(r['path']).open('rb') as original:
        for part in r['parts']:
            need(part['raw_offset']==offset,'recovery offset/order')
            need(info(part['path'])['sha256']==part['gzip_sha256'] and info(part['path'])['bytes']==part['gzip_bytes']<=10*1024**2,'recovery gzip identity')
            data=decode_member(safe(part['path']).read_bytes())
            need(len(data)==part['raw_bytes'] and hashlib.sha256(data).hexdigest()==part['raw_sha256'],'recovery raw part')
            need(original.read(len(data))==data,'literal recovered/original byte equality')
            offset+=len(data);total.update(data)
        need(not original.read(1),'unexpected original tail')
    need(offset==r['bytes'] and total.hexdigest()==r['sha256'],'whole recovered identity')
    return dict(path=r['path'],bytes=offset,sha256=total.hexdigest(),gzip_parts=len(r['parts']),literal_bytes_equal=True)


def check_cli(script,argv):
    info(script);tree=ast.parse(safe(script).read_text(encoding='utf8'));options=set();required=set();modes=set()
    for n in ast.walk(tree):
        if isinstance(n,(ast.Assign,ast.AnnAssign)) and isinstance(n.value,ast.Dict):
            modes.update(k.value for k in n.value.keys if isinstance(k,ast.Constant) and isinstance(k.value,str))
        if isinstance(n,(ast.Assign,ast.AnnAssign)) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name) and n.value.func.id=='dict':
            modes.update(k.arg for k in n.value.keywords if k.arg)
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='add_argument' and n.args:
            arg=n.args[0]
            if isinstance(arg,ast.Constant) and isinstance(arg.value,str):
                options.add(arg.value)
                if any(k.arg=='required' and isinstance(k.value,ast.Constant) and k.value.value is True for k in n.keywords):required.add(arg.value)
    actual={x for x in argv if x.startswith('--')}
    need(actual<=options and required<=actual,'static argparse ABI '+script)
    if 'mode' in options:need(argv and argv[0] in modes,'static argparse submode '+script)
    for ix,token in enumerate(argv):
        if token.endswith('-sha256') and token[:-7] in argv:
            companion=argv[argv.index(token[:-7])+1]
            need(info(companion)['sha256']==argv[ix+1],'CLI input SHA companion')
    return dict(script=script,argv=argv,static_argparse_match=True,executed=False)


def check_replay_guide():
    guide='docs/REPRODUCING_20260930_TWENTYSEVENTH_WAVE.md';info(guide);text=safe(guide).read_text(encoding='utf8');records=[]
    for line in text.splitlines():
        if not line.startswith('uv run '):continue
        tokens=shlex.split(line);idx=tokens.index('-B');records.append(check_cli(tokens[idx+1],tokens[idx+2:]))
    need(len(records)==3,'three literal guide commands')
    need(records[0]['script']=='acceleration/recover_20260930_twentyseventh_raw_artifacts.py' and records[1]['script']==records[2]['script']=='acceleration/replay_20260930_twentyseventh_audits.py','guide scripts')
    need(records[1]['argv']==records[2]['argv']+['--plan-only'] and records[2]['argv']==['--out','build/research-local/wave27-audit-replay'],'plan/actual output ABI')
    need(records[0]['argv'][-2:]==['--receipt','build/wave27-recovery.json'],'fresh recovery receipt')
    for marker in [PINS[B+'twentyseventh_raw_recovery/manifest.json'],'158,441,925','Thirteen are models','All13 complete solver traces','ten original checker command vectors','56,815,018','coverage by itself is not an exclusion','conditional','LOCAL_ONLY','256MiB proof-file limit']:
        need(marker in text,'guide assertion '+marker)
    need(info('uv.lock')['sha256']=='a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db','actual lock')
    plan=load(B+'resume/twentyseventh_replay_plan.json');need(plan['status']=='TWENTYSEVENTH_AUDIT_REPLAY_PLAN_CHECKED' and len(plan['commands'])==10,'plan population')
    script='acceleration/replay_20260930_twentyseventh_audits.py';tree=ast.parse(safe(script).read_text(encoding='utf8'))
    names=next(ast.literal_eval(n.value)for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='NAMES'for t in n.targets));need(names==REPLAY_NAMES,'wrapper frozen selection')
    for item,name in zip(plan['commands'],names):
        need(item['name']==name,'exact replay ordering');rp=item['saved_command_record'];saved=load(rp);cmd=saved['command'];need(info(rp)['sha256']==item['saved_command_record_sha256'] and cmd==item['saved_command'],'literal original command')
        script_indices=[i for i,t in enumerate(cmd)if t.startswith('acceleration/audit_')and t.endswith('.py')];need(len(script_indices)==1,'one independent script');ix=script_indices[0];checker=cmd[ix]
        if cmd[0]=='uv':need(cmd[:ix]==['uv','run','--locked','--offline','--cache-dir','.uv-cache-20260917','python','-B'],'explicit saved uv environment')
        else:need(ix==1 and Path(cmd[0]).name=='python.exe','saved locked interpreter command')
        report=load(I+name+'/summary.json');pins=report.get('inputs_sha256',{})|saved.get('inputs_sha256',{})
        need(info(checker)['sha256']==item['checker_sha256']==pins[checker]and item['expected_status']==report['status'],'actual checker source/report')
        expected=[str(ROOT/'build/research-venv/Scripts/python.exe'),'-B',*cmd[ix:]];expected[expected.index('--out')+1]=str(ROOT/'build/research-local/wave27-audit-replay'/name)
        # Windows receipts may spell separator bytes with doubled backslashes.
        norm=lambda xs:[str(Path(x)) if i==0 or(i>0 and xs[i-1]=='--out') else x for i,x in enumerate(xs)]
        need(norm(item['command'])==norm(expected),'only output/interpreter replay changes');records.append(check_cli(checker,cmd[ix+1:]))
    return records


def check_actual_replay():
    receipt=load(REPLAY_DIR+'receipt.json');summary=load(REPLAY_DIR+'summary.json');manifest=load(REPLAY_DIR+'manifest.json');checkpoint=load(REPLAY_DIR+'checkpoint.json')
    need(receipt['completed']==summary['completed']==10 and summary['status']=='TWENTYSEVENTH_AUDIT_REPLAY_PASS','actual ten completed')
    need(summary['results']==checkpoint and [r['name']for r in checkpoint]==REPLAY_NAMES and all(r['exit_code']==0 for r in checkpoint),'all actual replay exit codes')
    need(manifest['wrapper_sha256']==info('acceleration/replay_20260930_twentyseventh_audits.py')['sha256'],'executed wrapper identity')
    need(receipt['mathematical_claim_changes']==0 and any('LOCAL_ONLY'in s for s in receipt['limitations']),'local diagnostic availability')
    need(info(receipt['command'][1])['sha256']==receipt['source_sha256'],'receipt collector source')
    need([r['name']for r in manifest['plan']]==REPLAY_NAMES,'actual named plan');plan=load(B+'resume/twentyseventh_replay_plan.json');need(manifest['plan']==plan['commands'],'actual plan matches checked plan')
    copies=[];expected={REPLAY_DIR+x for x in ['manifest.json','checkpoint.json','summary.json']}|{REPLAY_DIR+n+suffix for n in REPLAY_NAMES for suffix in ['.summary.json','.stdout.log','.stderr.log']}
    need({r['path']for r in receipt['records']}==expected and len(receipt['records'])==33,'complete exact33-copy inventory')
    for item in receipt['records']:
        need(item['source'].startswith('build/research-local/wave27-audit-replay/'),'fresh original stays local');row=info(item['path']);need(row['sha256']==item['sha256']and row['bytes']==item['bytes'],'copied record identity')
        source=safe(item['source']);need(source.read_bytes()==safe(item['path']).read_bytes(),'literal local/public copy')
        if item['path'].endswith('.summary.json'):
            name=Path(item['path']).name[:-len('.summary.json')];copied=load(item['path']);need(copied['status']==load(I+name+'/summary.json')['status'],'same terminal audit status')
        copies.append(dict(public_path=item['path'],sha256=item['sha256'],local_source=item['source'],source_availability='LOCAL_ONLY'))
    return dict(completed=10,copies=copies,solver_calls=0,new_independent_implementation=False,local_diagnostic_reference_closure_not_public=True)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);started=time.monotonic()
    try:
        before_index=git('ls-files','--stage','-z'); before_head=git('rev-parse','HEAD').decode().strip()
        bind(PINS)
        for p in [key(Path(__file__)),key(Path(__file__).with_name(Path(__file__).stem+'_spec.md'))]:info(p)
        cat=load(OUTBASE+'catalog.json');stage=load(OUTBASE+'stage_inventory.json');summary=load(OUTBASE+'summary.json');scope=load(OUTBASE+'scope.json')
        bind(summary['output_hashes'])
        cp_gate=load(I+'twentyseventh_checkpoint/summary.json')
        need(cp_gate['status']=='INDEPENDENT_TWENTYSEVENTH_CHECKPOINT_CONSISTENCY_PASS','checkpoint prerequisite')
        # Authenticate checkpoint-reviewed report/snapshot identities, then newly frozen guide.
        for p in ['docs/RESEARCH_20260930_TWENTYSEVENTH_WAVE.md','acceleration/record_20260930_twentyseventh_checkpoint.py']:
            need(info(p)['sha256']==cp_gate['inputs_sha256'][p], 'checkpoint-reviewed current bytes')
        for p in SUPPLEMENTS: info(p)
        precommit=load(B+'resume/twentyseventh_precommit_checks.json');checks=precommit['checks']
        need(len(checks)==3 and all(c['exit_code']==0 for c in checks),'precommit terminal receipts')
        need(checks[1]['tests']==56 and checks[2]['selected_sources']==1828 and checks[2]['compiled_sources']==1827 and len(checks[2]['authenticated_preserved_failures'])==1,'precommit finite populations')
        need(info(checks[0]['output_path'])['sha256']==checks[0]['output_sha256'],'precommit validator receipt pin')
        for p in ENTRY_DOCS:
            info(p);need('TWENTYSEVENTH_WAVE' in safe(p).read_text(encoding='utf8'),'current corrected entry doc link')
        ledger=yaml.safe_load(safe('CLAIMS.yaml').read_bytes()); claims={c['id']:c for c in ledger['claims']};artifacts={a['id']:a for a in ledger['artifacts']}
        need(len(claims)==286 and Counter(c['status'] for c in claims.values())==dict(VERIFIED=281,CANDIDATE=3,REFUTED=2),'ledger cutoff')
        need(set(scope['claim_ids'])==set(summary['claim_ids']) and len(scope['claim_ids'])==8,'catalog claim IDs')
        need(Counter(claims[k]['status'] for k in scope['claim_ids'])==dict(VERIFIED=8),'cohort claim statuses')
        entries=cat['entries'];selected={r['path'] for r in entries};need(len(selected)==len(entries)==2514,'selection unique')
        local={r['path'] for r in entries if r['availability']=='LOCAL_ONLY'};public=selected-local
        expected=set(cat['exact_files'])
        for d in cat['exact_directories']:
            need(safe(d).is_dir(),'explicit directory')
            expected.update(key(p) for p in safe(d).rglob('*') if p.is_file())
        need(selected==expected,'literal allowlist coverage')
        for row in entries:
            p=row['path'];safe(p)
            need(not any(s in p for s in FUTURE),'future cohort included')
            need(Path(p).suffix.lower() not in ('.pem','.key') and Path(p).name.lower() not in ('.env','.env.local','credentials','credentials.json','id_rsa','id_ed25519'),'private file type')
            need(info(p)=={k:row[k] for k in ('path','sha256','bytes')},'catalog current bytes')
            need(row['availability'] in ('LOCAL_ONLY','READY_FOR_PUBLICATION'),'catalog publication state')
            need(p in local or row['bytes']<=10*1024**2,'research file size')
        manifest=load(B+'twentyseventh_raw_recovery/manifest.json')
        need(local=={r['path'] for r in manifest['records']} and len(local)==14,'exact local/recoverable set')
        need(sum(info(p)['bytes'] for p in public)==238167047 and len(public)==2500,'public payload counts')
        need(sum(info(p)['bytes'] for p in local)==158441925,'raw original total')
        for r in manifest['records']:
            need(r['path'] in local and all(t['path'] in public for t in r['parts']),'selected complete recovery parts')
        need(all(artifacts[e]['path'] in selected for c in scope['claim_ids'] for e in claims[c]['evidence']),'new claim evidence inclusion')
        raw_stage={x['path']:x for x in stage['entries']};need(stage['paths']==sorted(raw_stage) and len(raw_stage)==2519,'stage unique ordering')
        wrappers={OUTBASE+x for x in ['catalog.json','git_byte_checks.json','ignored_public_files.json','reference_checks.json.gz','reference_diagnostics.json','scope.json']+[f'reference_checks.part{i:04d}.json.gz' for i in range(13)]}
        need(set(raw_stage)==public|wrappers,'stage exact payload')
        need(stage['wrapper_paths_to_add_separately']==[OUTBASE+'stage_inventory.json',OUTBASE+'summary.json'],'separate stage wrappers')
        for p,row in raw_stage.items():need(info(p)==row,'stage current bytes')
        need(not (set(raw_stage)&local),'raw originals excluded from stage')
        for p in wrappers|set(stage['wrapper_paths_to_add_separately']):
            limit=32*1024**2 if Path(p).name in ('catalog.json','stage_inventory.json','reference_checks.json.gz') else 10*1024**2
            need(info(p)['bytes']<=limit,'wrapper ceiling')
        refs=gzip_json(OUTBASE+'reference_checks.json.gz');records=[]
        for ix,part in enumerate(refs['parts']):
            need(part['index']==ix and part['record_offset']==len(records),'reference part ordering')
            need(info(part['path'])['sha256']==part['sha256'] and info(part['path'])['bytes']==part['bytes']<=10*1024**2,'reference part identity')
            data=gzip_json(part['path']);need(data['index']==ix and len(data['records'])==part['records'],'reference record population')
            records.extend(data['records'])
        need(len(records)==refs['record_count']==summary['reference_bindings']==319663,'complete reference population')
        need(len({r['path'] for r in records})==refs['unique_referenced_files']==6062,'reference unique count')
        for row in records:
            need(info(row['path'])=={k:row[k] for k in ('path','sha256','bytes')},'reference current bytes')
        prior=load(cat['prior_catalog']['path']);need(info(cat['prior_catalog']['path'])['sha256']==cat['prior_catalog']['sha256'],'prior catalog identity')
        prior_recoverable=set(prior['prior_recoverable_dependencies'])|{r['path'] for r in prior['entries'] if r['availability']=='LOCAL_ONLY' and 'recovery available' in r['limitation']}
        need(prior_recoverable==set(cat['prior_recoverable_dependencies']),'inherited recoverable paths')
        tracked=set(git('ls-files','-z').decode().split('\0'));tools={r['path'] for r in cat['local_tools']}
        need(tools=={'build/research-cadical195/source/build/cadical','build/rook-drat-checker/drat-trim.exe'},'explicit local tools')
        for row in cat['local_tools']:need(info(row['path'])==row,'local tool identity')
        for row in records:
            p=row['path'];need(p in selected or p in tracked or p in prior_recoverable or p in tools or p.startswith('external_conway99_research/'),'publication reference unavailable')
        expected_refs=[];resolution_cache={}
        def resolve(name,sha,origin,archive=False):
            original=name
            if name in artifacts:
                need(artifacts[name]['sha256']==sha,'artifact-ID expected hash');name=artifacts[name]['path']
            if origin in {d+'/validation.json' for d in REGISTRATIONS} and name.replace('\\','/')=='CLAIMS.yaml':
                name=origin.rsplit('/',1)[0]+'/CLAIMS.after.yaml'
            name=name.replace('\\','/');cachekey=(name,archive,origin.rsplit('/',1)[0])
            if not archive and name in INFO:
                row=info(name)
            elif cachekey in resolution_cache:
                row=info(resolution_cache[cachekey])
            else:
                q=Path(name)
                candidates=[q] if q.is_absolute() else ([ROOT/'external_conway99_research'/name] if archive else [ROOT/name,safe(origin).parent/name])
                matches=[p.resolve() for p in candidates if p.is_file()]
                need(matches,'unresolved original reference: '+origin+' '+original)
                p=key(safe(matches[0]));row=info(p);resolution_cache[cachekey]=p
            need(row['sha256']==sha,'original reference hash: '+origin+' '+original)
            expected_refs.append(dict(origin=origin,**row))
        def walk(v,origin):
            if isinstance(v,list):
                for x in v:walk(x,origin)
            elif isinstance(v,dict):
                for k,x in v.items():
                    if k in MAPS and isinstance(x,dict):
                        for name,h in x.items():
                            if isinstance(h,str) and HEX.fullmatch(h):resolve(name,h,origin)
                    walk(x,origin)
                if isinstance(v.get('path'),str) and isinstance(v.get('sha256'),str) and HEX.fullmatch(v['sha256']):resolve(v['path'],v['sha256'],origin,'conway-99-research' in v.get('repository',''))
        for p in sorted(selected):
            if p.endswith('.json'):walk(load(p),p)
        for r in manifest['records']:
            for part in r['parts']:resolve(part['path'],part['gzip_sha256'],r['manifest'])
            resolve(r['path'],r['sha256'],r['manifest'])
        for cid in scope['claim_ids']:
            for eid in claims[cid]['evidence']:
                art=artifacts[eid];resolve(art['path'],art['sha256'],'CLAIMS.yaml')
        encode=lambda r:(r['origin'],r['path'],r['sha256'],r['bytes'])
        need(Counter(map(encode,records))==Counter(map(encode,expected_refs)),'independently reconstructed reference multiset')
        # Compare actual working tree bytes to Git's current clean-filter hashes.
        checkpaths=sorted(public|wrappers|set(stage['wrapper_paths_to_add_separately'])|set(ENTRY_DOCS)|set(SUPPLEMENTS)|{key(Path(__file__)),key(Path(__file__).with_name(Path(__file__).stem+'_spec.md'))})
        actual=git('hash-object','--stdin-paths',data=('\n'.join(checkpaths)+'\n').encode()).decode().splitlines()
        need(len(actual)==len(checkpaths),'Git record count')
        gitrows=[]
        for p,h in zip(checkpaths,actual):
            size=info(p)['bytes'];d=hashlib.sha1();d.update(b'blob '+str(size).encode()+b'\0')
            with safe(p).open('rb') as f:
                for block in iter(lambda:f.read(1024*1024),b''):d.update(block)
            need(d.hexdigest()==h,'Git clean filter changes bytes: '+p)
            gitrows.append(dict(path=p,sha256=info(p)['sha256'],git_blob_sha1=h))
        savedgit=load(OUTBASE+'git_byte_checks.json')['records'];actualmap={r['path']:r for r in gitrows}
        need({r['path'] for r in savedgit}==public and all(actualmap[r['path']]==r for r in savedgit),'saved Git checks agree')
        need(load(OUTBASE+'reference_diagnostics.json')==dict(errors=[],count=0),'no ignored closure errors')
        # Honest negative controls for closure and classification boundaries.
        controls=[]
        for name,mutator in [('missing_stage_entry',lambda s:s.pop(next(iter(s)))),('inject_local_raw',lambda s:s.update({next(iter(local)):info(next(iter(local)))}))]:
            bad=dict(raw_stage);mutator(bad)
            if set(bad)!=public|wrappers:controls.append(name)
            else:raise ValueError('stage corruption accepted')
        bad=list(records);bad.pop()
        need(Counter(map(encode,bad))!=Counter(map(encode,expected_refs)),'missing reference control');controls.append('missing_reference')
        recovery_rows = [recover_record(r) for r in manifest['records']]
        need(sum(r['bytes'] for r in recovery_rows)==158441925 and sum(r['gzip_parts'] for r in recovery_rows)==14,'complete fresh recovery totals')
        cli_records = check_replay_guide()
        replay_record = check_actual_replay()
        sample=manifest['records'][1];raw=safe(sample['parts'][0]['path']).read_bytes()
        for name,bad in [('truncated_gzip',raw[:-1]),('extra_gzip_member',raw+raw)]:
            try: decode_member(bad)
            except (ValueError,zlib.error): controls.append(name)
            else: raise ValueError('accepted gzip corruption')
        for name,field,value in [('wrong_offset','raw_offset',1),('wrong_hash','raw_sha256','0'*64)]:
            bad=copy.deepcopy(sample);bad['parts'][0][field]=value
            try: recover_record(bad)
            except ValueError: controls.append(name)
            else: raise ValueError('accepted recovery corruption')
        first=cli_records[0]
        try: check_cli(first['script'],first['argv']+['--invented-option'])
        except ValueError: controls.append('unknown_replay_option')
        else: raise ValueError('accepted CLI corruption')
        need(git('ls-files','--stage','-z')==before_index and git('rev-parse','HEAD').decode().strip()==before_head,'audit changed Git state')
        need(info('CLAIMS.yaml')['sha256']==hashlib.sha256(safe('CLAIMS.yaml').read_bytes()).hexdigest(),'concurrent ledger mutation')
        need(time.monotonic()-started<300,'300-second metadata allocation')
        write(out/'git_byte_checks.json',gitrows)
        write(out/'recovery_and_cli.json',dict(recovery=recovery_rows,cli=cli_records,actual_parent_replay=replay_record,scope='Literal byte recovery and static command/source checking; no replays launched by this reviewer. Separate copied parent execution metadata retains explicitly LOCAL_ONLY diagnostic references.'))
        write(out/'controls.json',dict(rejected=controls,count=len(controls)))
        result=dict(status='INDEPENDENT_TWENTYSEVENTH_PUBLICATION_METADATA_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=before_head,command=[sys.executable,*sys.argv],cwd=str(ROOT),selected_files=2514,public_research_files=2500,public_research_bytes=238167047,local_originals=14,raw_bytes=158441925,gzip_members=14,reference_bindings=319663,unique_reference_files=6062,reference_multiset_independently_reconstructed=True,stage_entries=2519,git_byte_paths_checked=len(checkpaths),checkpoint_gate=I+'twentyseventh_checkpoint/summary.json',entry_documents=ENTRY_DOCS,reviewed_supplements=SUPPLEMENTS,controls_rejected=len(controls),inputs_sha256=INPUTS,outputs_sha256={key(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir()) if p.is_file()},shared_components=['Independent metadata checker adapted from its prior wave26 implementation, without importing it or any producer/catalog/restorer.', 'Frozen checkpoint consistency gate supplies the registration/statement/report audit; it is reauthenticated here.', 'Python standard library and PyYAML; complete reference multiset reconstruction, zlib literal recovery and Git blob hashes.'],limitations=['Metadata/byte consistency only; no new mathematical verification or target conclusion.', 'No Git index/staging/commit/remote publication performed by this read-only gate.', 'Candidate inventory is merely a selected artifact, never an approval premise.', 'Static ABI checks handle literal/dict submode declarations and authenticated uv/interpreter command wrappers.', 'Guide command verification is static; mathematical audits were not rerun.', 'Four entry documents and reviewed supplements are outside the frozen catalog research payload.'],elapsed_seconds=time.monotonic()-started)
        write(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('inputs_sha256','outputs_sha256','shared_components','limitations')}))
    except Exception as e:
        write(out/'failure.json',dict(error=repr(e),inputs_sha256=INPUTS,elapsed_seconds=time.monotonic()-started));raise


if __name__=='__main__':main()
