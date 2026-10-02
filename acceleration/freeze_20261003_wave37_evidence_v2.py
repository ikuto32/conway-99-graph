"""Exact343 evidence freezer, new version preserving root's unexecuted V1."""
import argparse,hashlib,json,subprocess,sys
from collections import defaultdict
from datetime import datetime,timezone
from pathlib import Path,PurePosixPath
import yaml
from command_deadline import CommandDeadline
from audit_20261002_wave31_transition_v1 import UniqueLoader
ROOT=Path(__file__).resolve().parents[1]
LEDGER='af2af9811e0f701648095a31ebfeaad3cd956e2d332c09cc4344bdaa3f496a90'
BEFORE='5bd21f4126fea49e84e54b6d4bd63e4401b31d62727b72198d2c97c36c9e0ed3'
IDS=['C-HYPERGRAPH-WEIGHT60-V2-PILOT01-SAVED-OBJECTS','C-UNRESTRICTED-ROOTED7-CONTENT-DIVIDED-GF2-FOUR-PRIMALS','C-HYPERGRAPH-WEIGHT60-PILOT01-TWO-GRAPH-WARM-ROOT-CENSUS','C-GENERIC-BINARY-PROJECTION-CODOMAIN-ISOTROPY-RANK-LEMMA','C-UNRESTRICTED-ROOTED8-NONEDGE-LOCAL-CATALOGUE-COVERAGE','C-UNRESTRICTED-ROOTED8-MARKED-UNIVERSAL5-PRODUCT-NECESSARY-ENCODING']
PACKAGES={'acceleration/results/20261002_wave33_model_package01/manifest.json':'c3efa198c5f48eddb5ead69a4bb130a3dc55567bb298856143c6fb62eb0e0145','acceleration/results/20261002_wave33_reconstruction_package01/manifest.json':'f639431b7ea9ce0f1500ea48b002629d2523271eead700217dd512e8ade66989','acceleration/results/20261003_wave36_coupling_package01/manifest.json':'38f641ec21ec3d1d617515e8b3e578e098886863f7016ad640ac1906e8b0988f','acceleration/results/20261003_wave37_rooted8_package01/manifest.json':'ea48c30dfa68fe70bad17edbfd3697d8a2dcf28f9ab24b63d0d66895e7eb9b14'}
def need(ok,stage):
    if not ok:raise ValueError(stage)
def sha(p):
    with p.open('rb') as s:return hashlib.file_digest(s,'sha256').hexdigest()
def path(name):
    need(type(name) is str and name and not any(c in name for c in '\\\n\r\0'),'LITERAL_RELATIVE_PATH')
    p=PurePosixPath(name);need(not p.is_absolute() and '..' not in p.parts and not name.startswith('.git/'),'BOUNDED_PATH')
    need(name.startswith(('acceleration/','docs/')) or name in ('CLAIMS.yaml','README.md','ACTIVE_RESEARCH.md','.gitattributes','.github/workflows/claims.yml','pyproject.toml','uv.lock'),'RESEARCH_NAMESPACE')
    lower=name.lower()
    need('/recovered/' not in lower and '/build/' not in lower and '/wave38' not in lower and 'rooted8_unrestricted_gf2' not in lower and 'root8_mod2' not in lower and 'weight60_graph_reset' not in lower and 'weight60_reset_binding' not in lower,'EXCLUDED_QUEUED_OR_DUPLICATE_PATH')
    need('weight60_warm' not in lower or 'weight60_warm_root_census' in lower,'EXCLUDED_WARM_OUTPUT')
    result=(ROOT/name).resolve();need(result.is_relative_to(ROOT),'RESOLVED_BOUNDARY');return result
def save(p,v):
    with p.open('x',encoding='utf8',newline='\n') as s:json.dump(v,s,indent=2);s.write('\n')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--plan',required=True);ap.add_argument('--plan-sha256',required=True);args=ap.parse_args()
    d=CommandDeadline(args.seconds,allocation_reason='Exact343 metadata/source closure, eight raw omission hashes,48gzip parts;240outer200worker20reserve, no index/science')
    out=args.out.resolve();need(out.is_relative_to(ROOT),'OUTPUT_BOUNDARY');out.mkdir(parents=True,exist_ok=False);pins={};origins=defaultdict(set);expected={}
    def tick():need(not d.status()['stop_required'] and d.status()['remaining_seconds']>20,'DEADLINE_RESERVE')
    def pin(name,h=None):
        tick();a=sha(path(name));need(h is None or a==h,'EXACT_INPUT_HASH:'+name);need(name not in pins or pins[name]==a,'CONSISTENT_PIN');pins[name]=a;return a
    def add(name,origin,h=None):
        path(name);origins[name].add(origin)
        if h is not None:need(name not in expected or expected[name]==h,'CONSISTENT_EXPECTED_IDENTITY');expected[name]=h
    def read(name,h=None):pin(name,h);add(name,'authenticated manifest/receipt',pins[name]);return json.loads(path(name).read_bytes())
    try:
        plan=read(args.plan,args.plan_sha256);need(plan['schema']=='WAVE37_EXPLICIT_CLOSURE_PLAN_V2' and plan['ledger_sha256']==LEDGER and plan['before_sha256']==BEFORE and plan['packages']==PACKAGES,'EXACT_PLAN_SCOPE')
        pin('CLAIMS.yaml',LEDGER);pin(plan['before'],BEFORE);old=yaml.load(path(plan['before']).read_text(),Loader=UniqueLoader);current=yaml.load(path('CLAIMS.yaml').read_text(),Loader=UniqueLoader)
        need(len(old['claims'])==337 and len(current['claims'])==343 and current['claims'][:337]==old['claims'] and [c['id'] for c in current['claims'][337:]]==IDS,'EXACT337_TO343_CUTOFF')
        need(current['artifacts'][:len(old['artifacts'])]==old['artifacts'] and current['target']==old['target'],'ALL_PRIOR_AVAILABILITY_TARGET_UNCHANGED')
        for a in current['artifacts'][len(old['artifacts']):]:
            if a['path']:add(a['path'],'six exact claim evidence',a['sha256'])
        packaged={};part_count=0;gzip_bytes=0
        for name,h in PACKAGES.items():
            m=read(name,h)
            for r in m['records']:
                need(r['raw_path'] not in packaged,'DISTINCT_PACKAGED_RAW');packaged[r['raw_path']]=r;add(r['raw_path'],'package-backed CI original',r['raw_sha256']);offset=0
                for p in r['parts']:
                    need(p['raw_offset']==offset,'EXACT_PART_OFFSET');offset+=p['raw_bytes'];add(p['path'],'pinned lossless payload',p['gzip_sha256']);part_count+=1;gzip_bytes+=p['gzip_bytes']
                need(offset==r['raw_bytes'],'COMPLETE_RAW_PART_BYTES')
        need(len(packaged)==8 and part_count==48 and sum(r['raw_bytes'] for r in packaged.values())==367261301 and gzip_bytes==11723542,'EXACT_EIGHT_INPUT_PACKAGE_POPULATION')
        recovery=read(plan['recovery']['path'],plan['recovery']['sha256']);need(recovery['status']=='PASS' and recovery['producer']=='/root' and recovery['verifier']=='/root/native_driver' and recovery['producer_imports'] is False and recovery['mathematical_replay'] is False and (recovery['record_count'],recovery['gzip_parts'],recovery['raw_bytes'],recovery['gzip_bytes'],recovery['original_literal_bytes_compared'])==(2,16,124864726,4416662,124864726),'INDEPENDENT_NEW_RECOVERY_SCOPE')
        need(recovery['inputs_sha256']['acceleration/results/20261003_wave37_rooted8_package01/manifest.json']==PACKAGES['acceleration/results/20261003_wave37_rooted8_package01/manifest.json'],'EXACT_RECOVERY_PACKAGE')
        clean=read(plan['clean_restore']['path'],plan['clean_restore']['sha256']);need(clean['status']=='WAVE37_EIGHT_PUBLIC_INPUTS_RECOVERED' and (clean['raw_inputs'],clean['raw_bytes'],clean['gzip_parts'],clean['gzip_bytes'])==(8,367261301,48,11723542) and clean['child_action_counts']==[{'RESTORED_MISSING':4},{'RESTORED_MISSING':1},{'RESTORED_MISSING':1},{'RESTORED_MISSING':2}],'EXACT_CLEAN_EIGHT_RESTORE')
        controls=[]
        for bad,stage in [('../outside','BOUNDED_PATH'),('/absolute','BOUNDED_PATH'),('acceleration/../../outside','BOUNDED_PATH'),('acceleration\\mixed','LITERAL_RELATIVE_PATH'),('private.txt','RESEARCH_NAMESPACE'),('.git/config','BOUNDED_PATH'),('acceleration/results/x/recovered/raw.json','EXCLUDED_QUEUED_OR_DUPLICATE_PATH'),('acceleration/results/20261003_rooted8_unrestricted_gf2_screen01/x.json','EXCLUDED_QUEUED_OR_DUPLICATE_PATH'),('acceleration/results/20261003_weight60_graph_reset01/x.json','EXCLUDED_QUEUED_OR_DUPLICATE_PATH'),('acceleration/results/20261003_weight60_warm01/x.json','EXCLUDED_WARM_OUTPUT')]:
            try:path(bad)
            except ValueError as e:need(str(e)==stage,'PRECISE_PATH_CONTROL');controls.append({'path':bad,'stage':stage,'outcome':'REJECTED'})
            else:raise ValueError('PATH_CONTROL_FALSE_ACCEPT')
        for name in plan['extras']:
            p=path(name);need(p.exists(),'NAMED_EXTRA_EXISTS:'+name)
            if p.is_dir():
                for f in sorted(p.rglob('*')):
                    if f.is_file():add(f.relative_to(ROOT).as_posix(),'explicit completed root')
            else:add(name,'explicit source/document')
        for name in ('CLAIMS.yaml',Path(__file__).relative_to(ROOT).as_posix(),'acceleration/freeze_20261003_wave37_evidence_v2_spec.md'):add(name,'current metadata')
        index=Path(subprocess.check_output(['git','rev-parse','--git-path','index'],cwd=ROOT,text=True).strip());index=index if index.is_absolute() else ROOT/index;index_sha=sha(index)
        records=[];omitted=[]
        for name in sorted(origins):
            tick();p=path(name);need(p.is_file(),'EXACT_FILE_MEMBER');size=p.stat().st_size
            if name in packaged:
                r=packaged[name];need(size==r['raw_bytes'] and pin(name,r['raw_sha256'])==r['raw_sha256'] and (name not in expected or expected[name]==r['raw_sha256']),'EXACT_OMITTED_RAW_IDENTITY')
                omitted.append({'path':name,'sha256':r['raw_sha256'],'bytes':size,'reason':'Exact separately pinned lossless package; no duplicate raw Git blob.','fresh_hash_checked':True});continue
            need(size<50*1024**2,'DIRECT50MIB_BOUND:'+name);h=pin(name,expected.get(name));records.append({'path':name,'sha256':h,'bytes':size,'origins':sorted(origins[name])})
        need(sha(index)==index_sha and sha(ROOT/'CLAIMS.yaml')==LEDGER,'INDEX_LEDGER_UNCHANGED')
        selfpaths=[(out/'manifest.json').relative_to(ROOT).as_posix(),(out/'stage_paths.nul').relative_to(ROOT).as_posix()];names=sorted({r['path'] for r in records}|set(selfpaths));(out/'stage_paths.nul').write_bytes(b''.join(n.encode()+b'\0' for n in names))
        report={'schema':'WAVE37_INCREMENTAL_EXACT_EVIDENCE_ALLOWLIST_V2','timestamp':datetime.now(timezone.utc).isoformat(),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'command':[sys.executable,*sys.argv],'cwd':str(ROOT),'source_sha256':sha(Path(__file__)),'before_ledger_sha256':BEFORE,'ledger_sha256':LEDGER,'previous_claims':337,'current_claims':343,'new_claim_ids':IDS,'records':records,'direct_record_count':len(records),'direct_bytes':sum(r['bytes'] for r in records),'omitted':omitted,'packages':PACKAGES,'recovery':plan['recovery'],'clean_restore':plan['clean_restore'],'gitattributes_sha256':pin('.gitattributes'),'self_metadata_paths':selfpaths,'stage_paths_sha256':sha(out/'stage_paths.nul'),'stage_paths_count':len(names),'controls':controls,'inputs_sha256':pins,'index_mutated':False,'ledger_mutated':False,'scientific_launched':False,'mathematical_replay':False,'availability_changed':False,'deadline':d.status(),'limitations':['Explicit343 cutoff and named roots only, with queue/recovered duplicates rejected.','Full omitted original hashes authenticated; mathematical and recovery approval comes only from separate reports.','No index mutation, publication, PUBLIC promotion or mathematical replay.']}
        save(out/'manifest.json',report);print(json.dumps({'status':'WAVE37_EXACT343_ALLOWLIST_V2_FROZEN','manifest_sha256':sha(out/'manifest.json'),'direct_records':len(records),'direct_bytes':report['direct_bytes'],'omitted_raw':len(omitted),'stage_paths':len(names)}),flush=True)
    except BaseException as e:
        save(out/'failure.json',{'error':repr(e),'inputs_sha256':pins,'deadline':d.status(),'index_mutated':False,'ledger_mutated':False,'outputs_preserved':True});raise
if __name__=='__main__':main()
