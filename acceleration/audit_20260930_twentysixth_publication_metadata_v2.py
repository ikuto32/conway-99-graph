"""Read-only independent wave26 final catalog consistency and Git-byte audit."""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import argparse
import ast
import shlex
import copy
import hashlib
import json
import re
import subprocess
import sys
import time
import zlib
import yaml

ROOT = Path(__file__).resolve().parents[1]
B = 'acceleration/results/20260930_'
I = B + 'independent_review/'
OUTBASE = B + 'twentysixth_artifact_packaging/'
PRIVATE = I + 'hadamard_oriented_unknown/process.stdout.log'
HEX = re.compile(r'^[0-9a-f]{64}$')
MAPS = {'inputs_sha256','input_hashes','output_hashes','artifact_hashes','audit_artifact_hashes','checked_input_bindings','outputs_sha256','input_sha256'}
FUTURE = ('exact_eight_next_lift','triplicate_psd_kernel_options','exact_eight_campaign')
ENTRY_DOCS = ['ACTIVE_RESEARCH.md','README.md','docs/RESEARCH_MAP.md','docs/REPRODUCING.md']
PINS = {
    OUTBASE+'summary.json':'2f8bb00392e932dbef65adde85eab0075247731d987be14c0b36336234fbedfd',
    OUTBASE+'catalog.json':'d27a41ee61c1ed7453682ae69dd5a041e94e47e91d2aacaaf9b9c429619e27fb',
    OUTBASE+'stage_inventory.json':'a7e59efb22c3dec9a8ba25b013b86be2e4e6a89ff0662b66103ba931d85a0697',
    OUTBASE+'reference_checks.json.gz':'0017275bb9c6b66835d732438b1f56b721ff051070d025118a1be1d23a9c2fcb',
    I+'twentysixth_checkpoint/summary.json':'4d876dfc2732a0b35245a4014f8b20eec107372a5e8563a995cb6579566e343b',
    B+'resume/twentysixth_milestone_checkpoint.json':'8fc457eb11d2b8f836ff194dffcd5a1618119f66ee5e3a5626310d07a8be59a2',
    B+'resume/claims_at_twentysixth_milestone.yaml':'8bcdad8f4b2e871b6c0bdf6ef72736033a8d84624af029e1b01c2951bc4b8146',
    'CLAIMS.yaml':'8bcdad8f4b2e871b6c0bdf6ef72736033a8d84624af029e1b01c2951bc4b8146',
    B+'twentysixth_raw_recovery/manifest.json':'7f8f2c99a0ddd50fdb4fce9eaf4100240ecb19c4c6dbc6946b7e27cec29d6cd6',
    'acceleration/recover_20260930_twentysixth_raw_artifacts.py':'2fcb1bdb97ea9eb16c5db928fe0daac649a341cd8a4137e703d1109d02ce9141',
}
SUPPLEMENTS = [
 'acceleration/audit_20260930_twentysixth_checkpoint.py',
 'acceleration/audit_20260930_twentysixth_checkpoint_spec.md',
 I+'twentysixth_checkpoint/summary.json', I+'twentysixth_checkpoint/checked_records.json',
 B+'resume/twentysixth_precommit_validation.json',B+'resume/twentysixth_precommit_checks.json',
 'acceleration/stage_20260930_twentysixth_evidence.py',
]
REPLAY_DIR = B+'twentysixth_replay_validation/'
REPLAY_NAMES = ['third_count_profile_gram_diagnostic','eight_count_profile_lift_third','eight_count_profile_lift_third_object_calibration','third_eight_count_profile_unsat','count_min_upper_cnf','shared_block_identity','exact_eight_profile_preflight','exact_eight_profile_join','gf3_hollow_residual','triplicate_count_psd','exact_eight_scalar_screen','exact_eight_block_screen']
SUPPLEMENTS += [REPLAY_DIR+n for n in ['receipt.json','manifest.json','checkpoint.json','summary.json']]+[REPLAY_DIR+n+'.summary.json' for n in REPLAY_NAMES]
PINS.update({'acceleration/audit_20260930_twentysixth_publication_metadata.py': '09c3606342da22f3bb19db506281c3e8f3e378e469109609f409a10ce3a01ea5', 'acceleration/audit_20260930_twentysixth_publication_metadata_spec.md': '61aee17387bd42d01b1566dfa1ecf45b4145cc8b9494505ee95af4d3d76a58d2', 'acceleration/results/20260930_independent_review/twentysixth_publication_metadata/failure.json': '9ced89b1b00a2cf8c2880da37059120d7f81d710a38daf099733f0dfd49b4143'})
SUPPLEMENTS += list({'acceleration/audit_20260930_twentysixth_publication_metadata.py': '09c3606342da22f3bb19db506281c3e8f3e378e469109609f409a10ce3a01ea5', 'acceleration/audit_20260930_twentysixth_publication_metadata_spec.md': '61aee17387bd42d01b1566dfa1ecf45b4145cc8b9494505ee95af4d3d76a58d2', 'acceleration/results/20260930_independent_review/twentysixth_publication_metadata/failure.json': '9ced89b1b00a2cf8c2880da37059120d7f81d710a38daf099733f0dfd49b4143'})
INPUTS, INFO = {}, {}


def need(ok, msg):
    if not ok: raise ValueError(msg)


def safe(name):
    p = str(name).replace('\\','/')
    need(p != PRIVATE and Path(p).name != 'PROMPT.md' and not p.startswith('tools/'), 'protected path')
    q = Path(p)
    q = q.resolve() if q.is_absolute() else (ROOT/q).resolve()
    need(q.is_relative_to(ROOT), 'outside repository')
    need(q.relative_to(ROOT).as_posix() != PRIVATE, 'protected absolute path')
    return q


def key(q): return q.relative_to(ROOT).as_posix()


def info(name):
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
    guide='docs/REPRODUCING_20260930_TWENTYSIXTH_WAVE.md';info(guide);text=safe(guide).read_text(encoding='utf8')
    records=[]
    for line in text.splitlines():
        if not line.startswith('uv run '):continue
        tokens=shlex.split(line);idx=tokens.index('-B');script=tokens[idx+1];argv=tokens[idx+2:]
        records.append(check_cli(script,argv))
    need(len(records)==3,'guide exact CLI count')
    need(records[0]['script']=='acceleration/recover_20260930_twentysixth_raw_artifacts.py' and records[1]['script']==records[2]['script']=='acceleration/replay_20260930_twentysixth_audits.py','guide scripts')
    need(records[1]['argv']==records[2]['argv']+['--plan-only'],'plan/run difference')
    need(records[1]['argv']==['--out','build/research-local/wave26-audit-replay','--plan-only'],'fresh replay path')
    need(records[0]['argv'][-2:]==['--receipt','build/wave26-recovery.json'],'fresh recovery receipt')
    for marker in [PINS[B+'twentysixth_raw_recovery/manifest.json'],'17d87b5ef8724d70d7809d8f9cb581afe720272a1633fde261767f90b035340c','0f82ec4239be19f6ba3311b26a5d0f10b093c4aee0aff682dc68debe55d160a9','23,119,778','5,549,451','twelve original audit command vectors','only the three named historical profiles','no simultaneous factor follows']:
        need(marker in text,'guide scope/pin '+marker)
    info('uv.lock');need(info('uv.lock')['sha256']=='a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db','lock identity')
    plan=load(B+'resume/twentysixth_replay_plan.json');need(plan['status']=='TWENTYSIXTH_AUDIT_REPLAY_PLAN_CHECKED' and len(plan['commands'])==12,'saved replay plan count')
    names=[];root_script='acceleration/replay_20260930_twentysixth_audits.py';tree=ast.parse(safe(root_script).read_text(encoding='utf8'))
    expected_names=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='NAMES' for t in n.targets))
    for item in plan['commands']:
        names.append(item['name']);rp=item['saved_command_record'];saved=load(rp)
        need(info(rp)['sha256']==item['saved_command_record_sha256'] and item['saved_command']==saved['command'],'literal saved audit command')
        cmd=item['saved_command'];script=cmd[1];need(script.startswith('acceleration/audit_') and script.endswith('.py'),'only independent checker replays')
        report=load(I+item['name']+'/summary.json')
        pins=report.get('inputs_sha256',{})|saved.get('inputs_sha256',{})
        need(item['checker_sha256']==info(script)['sha256']==pins[script] and item['expected_status']==report['status'],'saved command source/report pins')
        expected=[cmd[0],'-B',*cmd[1:]];expected[expected.index('--out')+1]=str(ROOT/'build/research-local/wave26-audit-replay'/item['name'])
        need(item['command']==expected,'only interpreter/output replay changes')
        records.append(check_cli(script,cmd[2:]))
    need(names==expected_names and len(set(names))==12,'all named replay audits')
    return records


def check_actual_replay():
    receipt=load(REPLAY_DIR+'receipt.json');summary=load(REPLAY_DIR+'summary.json');manifest=load(REPLAY_DIR+'manifest.json');checkpoint=load(REPLAY_DIR+'checkpoint.json')
    need(receipt['completed']==receipt['expected']==summary['completed']==12 and receipt['tool_final_exit_code']==0,'actual replay count/exit')
    need(receipt['original_replay_tree_availability']=='LOCAL_ONLY','fresh replay local availability')
    need(receipt['wrapper_sha256']==manifest['wrapper_sha256']==info('acceleration/replay_20260930_twentysixth_audits.py')['sha256'],'executed wrapper bytes')
    need(summary['results']==checkpoint and [x['name'] for x in checkpoint]==REPLAY_NAMES and all(x['exit_code']==0 for x in checkpoint),'complete actual replay results')
    need([x['name'] for x in manifest['plan']]==REPLAY_NAMES,'actual replay plan')
    local_root=safe(receipt['source_directory']);need(local_root==ROOT/'build/research-local/wave26-audit-replay','literal local replay directory')
    copies=[]
    for item in receipt['reports']:
        need(item['audit'] in REPLAY_NAMES and item['path']==REPLAY_DIR+item['audit']+'.summary.json','explicit replay summary copy')
        need(info(item['path'])['sha256']==item['sha256'] and item['exit_code']==0,'replay copied receipt identity')
        copied=load(item['path']);original=local_root/item['audit']/'summary.json'
        need(safe(item['path']).read_bytes()==original.read_bytes() and copied['status']==item['status'],'literal fresh replay summary copy')
        need(item['status']==load(I+item['audit']+'/summary.json')['status'],'replay/historical status agreement')
        copies.append(dict(public_summary=item['path'],sha256=item['sha256'],original_local_path=key(original),original_availability='LOCAL_ONLY'))
    need(len(copies)==12 and len({x['public_summary'] for x in copies})==12,'all replay copies')
    for name in ['manifest.json','checkpoint.json','summary.json']:
        need(safe(REPLAY_DIR+name).read_bytes()==(local_root/name).read_bytes(),'literal replay wrapper copy')
    return dict(completed=12,solver_calls=0,new_independent_implementation=False,local_diagnostic_reference_closure_not_public=True,copied_summaries=copies)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);started=time.monotonic()
    try:
        before_index=git('ls-files','--stage','-z'); before_head=git('rev-parse','HEAD').decode().strip()
        bind(PINS)
        for p in [key(Path(__file__)),key(Path(__file__).with_name(Path(__file__).stem+'_spec.md'))]:info(p)
        cat=load(OUTBASE+'catalog.json');stage=load(OUTBASE+'stage_inventory.json');summary=load(OUTBASE+'summary.json');scope=load(OUTBASE+'scope.json')
        bind(summary['output_hashes'])
        cp_gate=load(I+'twentysixth_checkpoint/summary.json')
        need(cp_gate['status']=='INDEPENDENT_TWENTYSIXTH_CHECKPOINT_CONSISTENCY_PASS','checkpoint prerequisite')
        # Authenticate checkpoint-reviewed report/snapshot identities, then newly frozen guide.
        for p in ['docs/RESEARCH_20260930_TWENTYSIXTH_WAVE.md','docs/RESEARCH_20260930_TWENTYSIXTH_WAVE_CORRECTED.md',B+'twentysixth_report_scope_correction/summary.json','acceleration/record_20260930_twentysixth_checkpoint.py']:
            need(info(p)['sha256']==cp_gate['inputs_sha256'][p], 'checkpoint-reviewed current bytes')
        for p in SUPPLEMENTS: info(p)
        for p in ENTRY_DOCS:
            info(p);need('TWENTYSIXTH_WAVE_CORRECTED' in safe(p).read_text(encoding='utf8'),'current corrected entry doc link')
        ledger=yaml.safe_load(safe('CLAIMS.yaml').read_bytes()); claims={c['id']:c for c in ledger['claims']};artifacts={a['id']:a for a in ledger['artifacts']}
        need(len(claims)==278 and Counter(c['status'] for c in claims.values())==dict(VERIFIED=273,CANDIDATE=3,REFUTED=2),'ledger cutoff')
        need(set(scope['claim_ids'])==set(summary['claim_ids']) and len(scope['claim_ids'])==11,'catalog claim IDs')
        need(Counter(claims[k]['status'] for k in scope['claim_ids'])==dict(VERIFIED=11),'cohort claim statuses')
        entries=cat['entries'];selected={r['path'] for r in entries};need(len(selected)==len(entries)==4189,'selection unique')
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
        manifest=load(B+'twentysixth_raw_recovery/manifest.json')
        need(local=={r['path'] for r in manifest['records']} and len(local)==2,'exact local/recoverable set')
        need(sum(info(p)['bytes'] for p in public)==115560925 and len(public)==4187,'public payload counts')
        need(sum(info(p)['bytes'] for p in local)==23119778,'raw original total')
        for r in manifest['records']:
            need(r['path'] in local and all(t['path'] in public for t in r['parts']),'selected complete recovery parts')
        need(all(artifacts[e]['path'] in selected for c in scope['claim_ids'] for e in claims[c]['evidence']),'new claim evidence inclusion')
        raw_stage={x['path']:x for x in stage['entries']};need(stage['paths']==sorted(raw_stage) and len(raw_stage)==4195,'stage unique ordering')
        wrappers={OUTBASE+x for x in ['catalog.json','git_byte_checks.json','ignored_public_files.json','reference_checks.json.gz','reference_checks.part0000.json.gz','reference_checks.part0001.json.gz','reference_diagnostics.json','scope.json']}
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
        need(len(records)==refs['record_count']==summary['reference_bindings']==44334,'complete reference population')
        need(len({r['path'] for r in records})==refs['unique_referenced_files']==4298,'reference unique count')
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
        expected_refs=[]
        def resolve(name,sha,origin,archive=False):
            original=name
            if name in artifacts:
                need(artifacts[name]['sha256']==sha,'artifact-ID expected hash');name=artifacts[name]['path']
            if origin.endswith('_registration/validation.json') and name.replace('\\','/')=='CLAIMS.yaml':
                name=origin.rsplit('/',1)[0]+'/CLAIMS.after.yaml'
            name=name.replace('\\','/');q=Path(name)
            candidates=[q] if q.is_absolute() else ([ROOT/'external_conway99_research'/name] if archive else [ROOT/name,safe(origin).parent/name])
            matches=[p.resolve() for p in candidates if p.is_file()]
            need(matches,'unresolved original reference: '+origin+' '+original)
            p=key(safe(matches[0]));row=info(p)
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
        need(sum(r['bytes'] for r in recovery_rows)==23119778 and sum(r['gzip_parts'] for r in recovery_rows)==3,'complete fresh recovery totals')
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
        write(out/'git_byte_checks.json',gitrows)
        write(out/'recovery_and_cli.json',dict(recovery=recovery_rows,cli=cli_records,actual_parent_replay=replay_record,scope='Literal byte recovery and static command/source checking; no replays launched by this reviewer. Separate copied parent execution metadata retains explicitly LOCAL_ONLY diagnostic references.'))
        write(out/'controls.json',dict(rejected=controls,count=len(controls)))
        result=dict(status='INDEPENDENT_TWENTYSIXTH_PUBLICATION_METADATA_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=before_head,command=[sys.executable,*sys.argv],cwd=str(ROOT),selected_files=4189,public_research_files=4187,public_research_bytes=115560925,local_originals=2,raw_bytes=23119778,gzip_members=3,reference_bindings=44334,unique_reference_files=4298,reference_multiset_independently_reconstructed=True,stage_entries=4195,git_byte_paths_checked=len(checkpaths),checkpoint_gate=I+'twentysixth_checkpoint/summary.json',entry_documents=ENTRY_DOCS,reviewed_supplements=SUPPLEMENTS,controls_rejected=len(controls),inputs_sha256=INPUTS,outputs_sha256={key(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir()) if p.is_file()},shared_components=['Independent metadata checker adapted from prior wave25 checker, without importing it or any producer/catalog/restorer.', 'Frozen checkpoint consistency gate supplies the registration/statement/report audit; it is reauthenticated here.', 'Python standard library and PyYAML; complete reference multiset reconstruction, zlib literal recovery and Git blob hashes.'],limitations=['Metadata/byte consistency only; no new mathematical verification or target conclusion.', 'No Git index/staging/commit/remote publication performed by this read-only gate.', 'Candidate inventory is merely a selected artifact, never an approval premise.', 'Static argparse mode parsing v2 adds dict keyword declarations; v1 parser failure/source remain bound and preserved.', 'Guide command verification is static; mathematical audits were not rerun.', 'Four entry documents and reviewed supplements are outside the frozen catalog research payload.'],elapsed_seconds=time.monotonic()-started)
        write(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('inputs_sha256','outputs_sha256','shared_components','limitations')}))
    except Exception as e:
        write(out/'failure.json',dict(error=repr(e),inputs_sha256=INPUTS,elapsed_seconds=time.monotonic()-started));raise


if __name__=='__main__':main()
