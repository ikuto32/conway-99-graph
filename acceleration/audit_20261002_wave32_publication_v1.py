"""Independent immutable-byte and availability-only publication audit."""
import argparse,copy,hashlib,json,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
import yaml
from command_deadline import CommandDeadline
from audit_20261002_wave31_transition_v1 import UniqueLoader,indexed,need

ROOT=Path(__file__).resolve().parents[1]
REG='acceleration/results/20261002_wave32_publication01'
COMMIT='5308d0d08085e71e1c3ace316e6e692d6b5c636a'
PACKAGE='acceleration/results/20261002_batch05_raw_package02/manifest.json'
PACKAGE_SHA='95307e8999e9f15880ca2d1f43370e215bc533b4eaa9e00ceca6c6b6b1be6329'
PUB='acceleration/results/20261002_batch05_publication01/manifest.json'
PUB_SHA='4c68f6108a0327688c25d870a70497370b8924f787c335db87d38d09b7b28b19'


def transition(before,after,changed):
    need(before['claims']==after['claims'] and len(after['claims'])==318,'all318 claims and verification records unchanged')
    for field in set(before)|set(after):
        if field not in ['artifacts','updated_at']:need(before[field]==after[field],'unchanged top-level semantic field '+field)
    old,new=indexed(before['artifacts']),indexed(after['artifacts']);need(set(old)==set(new),'no artifact record insertion/deletion')
    allowed={'availability','retrieval','unavailable_reason'}
    actual=[]
    for aid,record in old.items():
        need({k:v for k,v in record.items() if k not in allowed}=={k:v for k,v in new[aid].items() if k not in allowed},'all artifact identities unchanged')
        if record['availability']!=new[aid]['availability']:
            need(record['availability']=='LOCAL_ONLY' and new[aid]['availability']=='PUBLIC' and new[aid]['unavailable_reason'] is None,'availability-only publication')
            actual.append(aid)
        if aid not in changed and not aid.startswith('wave31-'):need(record==new[aid],'only named scoped/public pointers updated')
    need(set(actual)==set(changed) and len(actual)==75,'exact75 newlyPUBLIC individual evidence artifacts')
    return old,new


def main(args):
    start=time.monotonic();deadline=CommandDeadline(args.seconds,allocation_reason='Frozen availability metadata and about108MB direct gzip/public objects;20seconds reserve')
    out=args.out.resolve();out.mkdir(exist_ok=False);pins={}
    def tick():need(not deadline.status()['stop_required'] and deadline.status()['remaining_seconds']>20,'not completed within the allocated budget')
    def pin(name,wanted=None):
        tick();p=(ROOT/name).resolve();need(p.is_relative_to(ROOT),'repository literal input')
        with p.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
        need(wanted is None or digest==wanted,'frozen identity '+name);pins[name]=digest
    def read(name,wanted=None):pin(name,wanted);return json.loads((ROOT/name).read_bytes())
    try:
        receipt=read(REG+'/receipt.json');need(receipt['publication_commit']==COMMIT and receipt['changed_material_claims']==0 and receipt['new_exclusions']==0 and receipt['mathematical_replay'] is False,'publication-only receipt')
        need(receipt['before_ledger_sha256']=='b0210a82c6df9a3991246dc708ef8240f5fe47b4a470e8c467da910b3da6ed5b','exact318beforeledger')
        before_name=REG+'/CLAIMS.before.yaml';after_name=REG+'/CLAIMS.after.yaml'
        pin(before_name,receipt['before_ledger_sha256']);pin(after_name,receipt['after_ledger_sha256'])
        before=yaml.load((ROOT/before_name).read_text(encoding='utf8'),Loader=UniqueLoader);after=yaml.load((ROOT/after_name).read_text(encoding='utf8'),Loader=UniqueLoader)
        changed=receipt['changed_artifact_ids'];old,new=transition(before,after,changed)
        need(len(receipt['retained_local_artifacts'])==4,'four unavailable exact large raw artifacts')
        for record in receipt['retained_local_artifacts']:
            aid=record['id'];need(old[aid]==new[aid] and new[aid]['availability']=='LOCAL_ONLY' and record['availability']=='LOCAL_ONLY','large raw availability retained')
        package=read(PACKAGE,PACKAGE_SHA);publication=read(PUB,PUB_SHA)
        parts={}
        for record in package['records']:
            for part in record['parts']:
                if part['path'] in parts:need(parts[part['path']]==part,'shared payload identity')
                parts[part['path']]=part
        need(len(package['records'])==934 and len(parts)==936 and package['raw_bytes']==1127340761 and package['gzip_bytes']==108227430,'frozen normalized raw package counts')
        direct={record['path']:record for record in publication['records']};need(len(direct)==len(publication['records'])==2303,'distinct2303 immutable publication members')
        checked={record['path']:record for record in receipt['immutable_records']}
        need(len(checked)==len(receipt['immutable_records'])==2303 and checked=={name:{k:r[k] for k in ['path','sha256','bytes']} for name,r in direct.items()},'receipt exact immutable population')
        for name,part in parts.items():need(direct[name]['sha256']==part['gzip_sha256'] and direct[name]['bytes']==part['gzip_bytes'],'all936direct gzip identities')
        all_needed=set(direct)|{PUB,PACKAGE}|{new[aid]['path'] for aid in changed}|{r['path'] for r in receipt['retained_local_artifacts']}
        process=subprocess.Popen(['git','cat-file','--batch'],cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
        blobs={};gitbytes=0
        try:
            for name in sorted(all_needed):
                tick();need('\n' not in name and ':' not in name and (ROOT/name).resolve().is_relative_to(ROOT),'bounded literal git path')
                process.stdin.write((COMMIT+':'+name+'\n').encode());process.stdin.flush();header=process.stdout.readline().split()
                if header[-1:]==[b'missing']:blobs[name]=None;continue
                need(len(header)==3 and header[1]==b'blob','immutable literal git blob');length=int(header[2]);left=length;h=hashlib.sha256()
                while left:
                    tick();block=process.stdout.read(min(left,4*1024**2));need(bool(block),'complete immutable git bytes');h.update(block);left-=len(block)
                need(process.stdout.read(1)==b'\n','complete literal git record');blobs[name]={'sha256':h.hexdigest(),'bytes':length};gitbytes+=length
            process.stdin.close();need(process.wait(timeout=10)==0,'immutable object reader exit')
        finally:
            if process.poll() is None:process.kill();process.wait(timeout=5)
        for name,record in direct.items():need(blobs[name]=={k:record[k] for k in ['sha256','bytes']},'every immutable publication member '+name)
        need(blobs[PUB]['sha256']==PUB_SHA and blobs[PACKAGE]['sha256']==PACKAGE_SHA,'public anchor manifest bytes')
        prefix='https://github.com/ikuto32/conway-99-graph/blob/'+COMMIT+'/'
        for aid in changed:
            record=new[aid];need(blobs[record['path']]['sha256']==record['sha256'] and record['retrieval'].startswith(prefix+record['path']+';'),'individual public evidence byte/pointer')
        for record in receipt['retained_local_artifacts']:need(blobs[record['path']] is None,'large exact raw file absent from published commit')
        for aid,record in new.items():
            if aid.startswith('wave31-'):
                need(PACKAGE in record['retrieval'] and 'Complete historical transitive gate closure and platform binaries remain separate.' in record['retrieval'], 'direct recovery and unavailable separate closure caveat')
        remote=subprocess.run(['git','ls-remote','origin','refs/heads/codex/eight-coordinate-continuation-20260930'],cwd=ROOT,capture_output=True,text=True,check=True,timeout=30).stdout.strip()
        advertised=remote.split()[0]
        need(subprocess.run(['git','merge-base','--is-ancestor',COMMIT,advertised],cwd=ROOT).returncode==0,'immutable publication commit reachable from advertised branch')
        repo=json.loads(subprocess.run(['gh','repo','view','ikuto32/conway-99-graph','--json','isPrivate,url'],cwd=ROOT,capture_output=True,text=True,check=True,timeout=30).stdout)
        need(repo['isPrivate'] is False and repo['url']=='https://github.com/ikuto32/conway-99-graph','actual public repository metadata')
        rejected=[]
        for label,change in [('claim_change',lambda x:x['claims'][0].update(statement='changed')),
                             ('proof_identity_change',lambda x:x['artifacts'][0].update(sha256='0'*64)),
                             ('unavailable_raw_promoted',lambda x:indexed(x['artifacts'])[receipt['retained_local_artifacts'][0]['id']].update(availability='PUBLIC'))]:
            bad=copy.deepcopy(after);change(bad)
            try:transition(before,bad,changed)
            except ValueError:rejected.append(label)
            else:raise ValueError('corrupted publication transition accepted')
        for name in [Path(__file__).relative_to(ROOT).as_posix(),'acceleration/audit_20261002_wave31_transition_v1.py','uv.lock','pyproject.toml']:pin(name)
        summary=dict(status='INDEPENDENT_WAVE32_PUBLICATION_AVAILABILITY_ONLY_PASS',timestamp=datetime.now(timezone.utc).isoformat(),verifier='/root/checkpoint_audit',
            source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),exact_command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256=pins,
            publication_commit=COMMIT,all_material_claims_unchanged=318,new_individual_evidence_PUBLIC=75,retained_large_raw_LOCAL_ONLY=4,
            immutable_publication_members=2303,gzip_parts_in_direct_closure=936,direct_raw_members=934,direct_raw_bytes=1127340761,direct_gzip_bytes=108227430,
            complete_immutable_git_object_bytes_checked=gitbytes,raw_literal_platform_and_historical_transitive_closure_replayed=False,
            actual_remote_observation=remote,actual_public_repository_observation=repo,corrupted_controls_rejected=rejected,new_exclusions=0,target_resolution='UNKNOWN',
            scope='Immutable committed byte identities, public reachability and availability-only metadata transition. No mathematical or full recovery replay.',
            limitations=['Uses local immutable Git objects plus actual remote branch/public metadata observation; no new clean-clone transfer.','Complete historical transitive checking closure and platform binaries are not supplied by the direct payload.',
                         'Four exact large raw files remain LOCAL_ONLY; byte transform and partial traces are not certificates.','Previous independent complete raw recovery is not rerun by this publication metadata audit.'],
            overall_search_coverage='UNKNOWN; no validated denominator.',elapsed_seconds=time.monotonic()-start,deadline=deadline.status())
        with (out/'summary.json').open('x',encoding='utf8',newline='\n') as f:json.dump(summary,f,indent=2);f.write('\n')
        print(json.dumps({'path':(out/'summary.json').relative_to(ROOT).as_posix(),'sha256':hashlib.sha256((out/'summary.json').read_bytes()).hexdigest()}))
    except Exception as error:
        with (out/'failure.json').open('x',encoding='utf8',newline='\n') as f:json.dump({'error':repr(error),'inputs_sha256':pins,'timestamp':datetime.now(timezone.utc).isoformat()},f,indent=2);f.write('\n')
        raise


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True);main(ap.parse_args())
