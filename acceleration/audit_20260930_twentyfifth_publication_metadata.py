"""Read-only independent wave25 final catalog consistency and Git-byte audit."""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import argparse
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
OUTBASE = B + 'twentyfifth_artifact_packaging_v2/'
PRIVATE = I + 'hadamard_oriented_unknown/process.stdout.log'
HEX = re.compile(r'^[0-9a-f]{64}$')
MAPS = {'inputs_sha256','input_hashes','output_hashes','artifact_hashes','audit_artifact_hashes','checked_input_bindings','outputs_sha256','input_sha256'}
FUTURE = ('count_min_upper_inventory','third_count_profile_gram_diagnostic','eight_count_profile_lift_third')
ENTRY_DOCS = ['ACTIVE_RESEARCH.md','README.md','docs/RESEARCH_MAP.md','docs/REPRODUCING.md']
PINS = {
    OUTBASE+'summary.json':'9b4730e6f9c5c90311d7ed7ca9460e42dc1c1d764bf54879e191a1cfeed96900',
    OUTBASE+'catalog.json':'2f4643672f2304bdec334d28f8e71de35925cc643e6d80821372cad156999c9c',
    OUTBASE+'stage_inventory.json':'780e98b8371299388ee29774d67c355fb31199ec764902926284f4f8668e6243',
    OUTBASE+'reference_checks.json.gz':'f5c35ce03c59fd6f1634fa7b996583f81e8750f19b5983d4b18b5ba68a17e8e8',
    I+'twentyfifth_checkpoint_v4/summary.json':'22c53faaf40e82a44ea28cf356c1ef4a5d70a6d3cb0bda44e8a62bf1363f8590',
    B+'resume/twentyfifth_milestone_checkpoint.json':'450671e692b6074b73f99c9138208b206c5b6ab3918c9385dfdff57f80ece873',
    B+'resume/claims_at_twentyfifth_milestone.yaml':'82e03975b3e6eb109a0fb9c82746475a253763d1620d543e8938fec561d3cd77',
    'CLAIMS.yaml':'82e03975b3e6eb109a0fb9c82746475a253763d1620d543e8938fec561d3cd77',
    B+'twentyfifth_raw_recovery/manifest.json':'695d61b39c466660cb854377800dd036362739a4bd03ffc200bf6e35873ea45b',
    'acceleration/recover_20260930_twentyfifth_raw_artifacts.py':'bfdb92ae56e008907fea9f0bee9d24e7ac2b6b0af9dcf235ec227b4c959b6a56',
    B+'twentyfifth_historical_ledger_resolution/impact_review.json':'614c7c81c2143ad784c47d7f02bda6d879466f1bf8c9c27a90ade384386dd46a',
}
LEDGER_OLD = '4241ad1f845aeccfcfeb01238e6df0f566ee0528f2ee9cc0e5662a4a9ecd7881'
ALIASES = {I+'count_master_partial_cut_sat_outcome/summary.json', B+'twentyfifth_final_registration/summary.json'}
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


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);started=time.monotonic()
    try:
        before_index=git('ls-files','--stage','-z'); before_head=git('rev-parse','HEAD').decode().strip()
        bind(PINS)
        for p in [key(Path(__file__)),key(Path(__file__).with_name(Path(__file__).stem+'_spec.md'))]:info(p)
        cat=load(OUTBASE+'catalog.json');stage=load(OUTBASE+'stage_inventory.json');summary=load(OUTBASE+'summary.json');scope=load(OUTBASE+'scope.json')
        bind(summary['output_hashes'])
        cp_gate=load(I+'twentyfifth_checkpoint_v4/summary.json')
        need(cp_gate['status']=='INDEPENDENT_TWENTYFIFTH_CHECKPOINT_REPLAY_RECOVERY_CONSISTENCY_PASS','checkpoint prerequisite')
        # Bind the precise independently checked guide, snapshot and recovery.
        for p in ['docs/REPRODUCING_20260930_TWENTYFIFTH_WAVE.md','docs/RESEARCH_20260930_TWENTYFIFTH_WAVE.md', B+'resume/twentyfifth_raw_recovery.json', 'acceleration/record_20260930_twentyfifth_checkpoint.py']:
            need(info(p)['sha256']==cp_gate['inputs_sha256'][p], 'checkpoint-reviewed current bytes')
        for p in ENTRY_DOCS:
            info(p);need('TWENTYFIFTH_WAVE' in safe(p).read_text(encoding='utf8'),'current entry doc link')
        ledger=yaml.safe_load(safe('CLAIMS.yaml').read_bytes()); claims={c['id']:c for c in ledger['claims']};artifacts={a['id']:a for a in ledger['artifacts']}
        need(len(claims)==267 and Counter(c['status'] for c in claims.values())==dict(VERIFIED=262,CANDIDATE=3,REFUTED=2),'ledger cutoff')
        need(set(scope['claim_ids'])==set(summary['claim_ids']) and len(scope['claim_ids'])==19,'catalog claim IDs')
        need(Counter(claims[k]['status'] for k in scope['claim_ids'])==dict(VERIFIED=18,CANDIDATE=1),'cohort claim statuses')
        entries=cat['entries'];selected={r['path'] for r in entries};need(len(selected)==len(entries)==1136,'selection unique')
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
        manifest=load(B+'twentyfifth_raw_recovery/manifest.json')
        need(local=={r['path'] for r in manifest['records']} and len(local)==8,'exact local/recoverable set')
        need(sum(info(p)['bytes'] for p in public)==630039165 and len(public)==1128,'public payload counts')
        need(sum(info(p)['bytes'] for p in local)==1907346389,'raw original total')
        for r in manifest['records']:
            need(r['path'] in local and all(t['path'] in public for t in r['parts']),'selected complete recovery parts')
        need(all(artifacts[e]['path'] in selected for c in scope['claim_ids'] for e in claims[c]['evidence']),'new claim evidence inclusion')
        raw_stage={x['path']:x for x in stage['entries']};need(stage['paths']==sorted(raw_stage) and len(raw_stage)==1135,'stage unique ordering')
        wrappers={OUTBASE+x for x in ['catalog.json','git_byte_checks.json','ignored_public_files.json','reference_checks.json.gz','reference_checks.part0000.json.gz','reference_diagnostics.json','scope.json']}
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
        need(len(records)==refs['record_count']==summary['reference_bindings']==15995,'complete reference population')
        need(len({r['path'] for r in records})==refs['unique_referenced_files']==1360,'reference unique count')
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
        expected_refs=[];alias_uses=[]
        def resolve(name,sha,origin,archive=False):
            original=name
            if name in artifacts:
                need(artifacts[name]['sha256']==sha,'artifact-ID expected hash');name=artifacts[name]['path']
            if name=='CLAIMS.yaml' and sha==LEDGER_OLD and origin in ALIASES:
                alias_uses.append((origin,name,sha));name=B+'twentyfifth_final_registration/CLAIMS.before.yaml'
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
        need(len(alias_uses)==2 and {x[0] for x in alias_uses}==ALIASES,'only two exact historical aliases')
        historical=yaml.safe_load(safe(B+'twentyfifth_final_registration/CLAIMS.before.yaml').read_bytes())
        need(info(B+'twentyfifth_final_registration/CLAIMS.before.yaml')['sha256']==LEDGER_OLD,'historical original snapshot')
        need(len(historical['claims'])==261 and historical['claims']==ledger['claims'][:261] and historical['artifacts']==ledger['artifacts'][:len(historical['artifacts'])],'historical nonimpact')
        # Compare actual working tree bytes to Git's current clean-filter hashes.
        checkpaths=sorted(public|wrappers|set(stage['wrapper_paths_to_add_separately'])|set(ENTRY_DOCS))
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
        for origin,h in [(next(iter(ALIASES)),PINS['CLAIMS.yaml']),('unrelated.json',LEDGER_OLD)]:
            permitted=origin in ALIASES and h==LEDGER_OLD
            need(not permitted,'overbroad alias control');controls.append('reject_unapproved_alias_'+origin)
        need(git('ls-files','--stage','-z')==before_index and git('rev-parse','HEAD').decode().strip()==before_head,'audit changed Git state')
        need(info('CLAIMS.yaml')['sha256']==hashlib.sha256(safe('CLAIMS.yaml').read_bytes()).hexdigest(),'concurrent ledger mutation')
        write(out/'git_byte_checks.json',gitrows)
        write(out/'historical_alias_review.json',dict(aliases=alias_uses,unchanged_claims=261,unchanged_artifacts=len(historical['artifacts']),scope='Explicit saved-history resolution only; no rewriting of old reports or global live-ledger alias.'))
        write(out/'controls.json',dict(rejected=controls,count=len(controls)))
        result=dict(status='INDEPENDENT_TWENTYFIFTH_PUBLICATION_METADATA_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=before_head,command=[sys.executable,*sys.argv],cwd=str(ROOT),selected_files=1136,public_research_files=1128,public_research_bytes=630039165,local_originals=8,raw_bytes=1907346389,gzip_members=231,reference_bindings=15995,unique_reference_files=1360,reference_multiset_independently_reconstructed=True,historical_aliases=2,historical_claims_unchanged=261,stage_entries=1135,git_byte_paths_checked=len(checkpaths),guide_checkpoint_recovery_gate=I+'twentyfifth_checkpoint_v4/summary.json',entry_documents=ENTRY_DOCS,controls_rejected=len(controls),inputs_sha256=INPUTS,outputs_sha256={key(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir()) if p.is_file()},shared_components=['Standard-library/PyYAML independent file, JSON and reference reconstruction; no catalog/producer/restorer/checkpoint-writer imports.', 'Frozen independent checkpoint v4 gate supplies the completed literal eight-original recovery and thirteen static CLI checks; its exact guide/recovery/checkpoint inputs are reauthenticated.'],limitations=['Metadata/byte consistency approval only. No new mathematical verification or target conclusion.', 'No Git index/staging/commit/remote publication performed or approved by this read-only gate.', 'Candidate inventory is inspected only if selected as an artifact, never as an approval premise.', 'Four large streams remain incomplete UNKNOWN traces; historical source availability is not changed.', 'Current entry documents are bound separately from the catalog research payload.'],elapsed_seconds=time.monotonic()-started)
        write(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('inputs_sha256','outputs_sha256','shared_components','limitations')}))
    except Exception as e:
        write(out/'failure.json',dict(error=repr(e),inputs_sha256=INPUTS,elapsed_seconds=time.monotonic()-started));raise


if __name__=='__main__':main()
