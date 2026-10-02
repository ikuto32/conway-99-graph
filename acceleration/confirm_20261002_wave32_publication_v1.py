"""Confirm immutable published bytes and update availability metadata only.

No claim statement, revision, dependency, evidence binding or verification changes.
The direct raw payload is public; platform binaries and the historical transitive
checking closure remain separately disclosed. No proof is replayed here.
"""
import argparse,copy,hashlib,json,os,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
import yaml
import validate_claims as registry
from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
BASE='acceleration/results/20261002_wave31_registration02/CLAIMS.after.yaml'
MANIFEST='acceleration/results/20261002_batch05_publication01/manifest.json'
MANIFEST_SHA='4c68f6108a0327688c25d870a70497370b8924f787c335db87d38d09b7b28b19'
PACKAGE='acceleration/results/20261002_batch05_raw_package02/manifest.json'
PACKAGE_SHA='95307e8999e9f15880ca2d1f43370e215bc533b4eaa9e00ceca6c6b6b1be6329'


def need(ok,why):
    if not ok:raise ValueError(why)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--commit',required=True);ap.add_argument('--previous-sha256',required=True)
    ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    deadline=CommandDeadline(args.seconds,allocation_reason='Confirm exact immutable direct payload bytes and scoped evidence after public push')
    before=(ROOT/'CLAIMS.yaml').read_bytes()
    need(hashlib.sha256(before).hexdigest()==args.previous_sha256,'exact frozen318-claim ledger')
    old=registry.read_ledger(ROOT/'CLAIMS.yaml');data=copy.deepcopy(old)
    remote=subprocess.check_output(['git','ls-remote','origin','refs/heads/codex/eight-coordinate-continuation-20260930'],cwd=ROOT,text=True).strip()
    need(remote.split()[0]==args.commit,'expected commit advertised by remote branch')
    repo=json.loads(subprocess.check_output(['gh','repo','view','ikuto32/conway-99-graph','--json','isPrivate,url'],cwd=ROOT))
    need(repo['isPrivate'] is False,'confirmed public repository metadata')
    publication=json.loads((ROOT/MANIFEST).read_bytes())
    need(hashlib.sha256((ROOT/MANIFEST).read_bytes()).hexdigest()==MANIFEST_SHA,'exact independently staged payload manifest')
    needed={r['path'] for r in publication['records']}|{MANIFEST,PACKAGE}
    baseline=yaml.safe_load((ROOT/BASE).read_bytes());prior_ids={a['id'] for a in baseline['artifacts']}
    newartifacts=[a for a in data['artifacts'] if a['id'] not in prior_ids]
    needed.update(a['path'] for a in newartifacts if a['path'])
    process=subprocess.Popen(['git','cat-file','--batch'],cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
    blobs={};checked=[]
    try:
        for name in sorted(needed):
            need(not deadline.status()['stop_required'],'immutable byte checking deadline')
            need((ROOT/name).resolve().is_relative_to(ROOT) and '\n' not in name,'bounded literal object path')
            process.stdin.write((args.commit+':'+name+'\n').encode());process.stdin.flush()
            header=process.stdout.readline().split()
            if header[-1:]==[b'missing']:
                blobs[name]=None;continue
            need(len(header)==3 and header[1]==b'blob','literal published file object')
            size=int(header[2]);remaining=size;h=hashlib.sha256()
            while remaining:
                block=process.stdout.read(min(8*1024**2,remaining));need(bool(block),'complete git blob bytes')
                h.update(block);remaining-=len(block)
            need(process.stdout.read(1)==b'\n','complete git batch record')
            blobs[name]=dict(sha256=h.hexdigest(),bytes=size)
        process.stdin.close();need(process.wait(timeout=10)==0,'git object reader completed')
    finally:
        if process.poll() is None:process.kill();process.wait(timeout=5)
    for row in publication['records']:
        need(blobs[row['path']]==dict(sha256=row['sha256'],bytes=row['bytes']),'immutable staged member bytes '+row['path'])
        checked.append(dict(path=row['path'],**blobs[row['path']]))
    need(blobs[MANIFEST]['sha256']==MANIFEST_SHA and blobs[PACKAGE]['sha256']==PACKAGE_SHA,'published package anchor identities')
    package=json.loads((ROOT/PACKAGE).read_bytes())
    parts={p['path']:p for r in package['records'] for p in r['parts']}
    need(len(parts)==936 and len(package['records'])==934,'exact direct payload population')
    for name,p in parts.items():
        need(blobs[name]==dict(sha256=p['gzip_sha256'],bytes=p['gzip_bytes']),'every immutable gzip part')
    changed=[];retained=[]
    for a in newartifacts:
        item=blobs.get(a['path'])
        if item is None:
            retained.append(dict(id=a['id'],path=a['path'],availability=a['availability'],reason='Exact literal artifact not in this published commit; prior local availability retained.'))
            continue
        need(item['sha256']==a['sha256'],'exact published scoped artifact identity '+a['path'])
        a['availability']='PUBLIC';a['unavailable_reason']=None
        a['retrieval']='https://github.com/ikuto32/conway-99-graph/blob/'+args.commit+'/'+a['path']+'; exact artifact only. Large partial traces and complete historical transitive checking closure have separate availability.'
        changed.append(a['id'])
    for a in data['artifacts']:
        if a['id'].startswith('wave31-'):
            a['retrieval']=a['retrieval'].split(';')[0]+'; this exact artifact is public. Direct batch05 CNF/model/scope/proof recovery is public via https://github.com/ikuto32/conway-99-graph/blob/'+args.commit+'/'+PACKAGE+'. Complete historical transitive gate closure and platform binaries remain separate.'
    need(data['claims']==old['claims'] and data['target']==old['target'],'all318 material claim and target records unchanged')
    now=datetime.now(timezone.utc).isoformat();data['updated_at']=now
    validation=registry.validate(data,ROOT,json.loads((ROOT/'docs/claims.schema.json').read_bytes()),'public',old)
    need(validation['valid'],repr(validation['errors']))
    after=yaml.safe_dump(data,sort_keys=False,width=110).encode()
    (out/'CLAIMS.before.yaml').write_bytes(before);(out/'CLAIMS.after.yaml').write_bytes(after)
    report=dict(timestamp=now,status='IMMUTABLE_WAVE32_DIRECT_EVIDENCE_PUBLICATION_CONFIRMED',command=[sys.executable,*sys.argv],cwd=str(ROOT),
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),publication_commit=args.commit,remote_observation=remote,
        public_repository_observation=repo,before_ledger_sha256=args.previous_sha256,after_ledger_sha256=hashlib.sha256(after).hexdigest(),
        immutable_records=checked,changed_artifact_ids=changed,retained_local_artifacts=retained,
        direct_raw_population=dict(raw_members=934,gzip_parts=936,raw_bytes=package['raw_bytes'],gzip_bytes=package['gzip_bytes']),
        raw_manifest_path=PACKAGE,raw_manifest_sha256=PACKAGE_SHA,changed_material_claims=0,new_exclusions=0,mathematical_replay=False,
        limitations=['Remote branch advertises the locally byte-checked immutable commit; no second clean-clone transfer/recovery performed.',
            'Complete historical transitive gate closure is not repackaged.','Platform native/checker binaries remain separately local with pinned source provenance.',
            'Public raw recovery is not a new mathematical proof replay or target resolution.'],validation=validation)
    (out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8',newline='\n')
    need((ROOT/'CLAIMS.yaml').read_bytes()==before,'no concurrent ledger modification')
    pending=out/'CLAIMS.pending.yaml';pending.write_bytes(after);os.replace(pending,ROOT/'CLAIMS.yaml')
    print(json.dumps(dict(status=report['status'],public_scoped_artifacts=len(changed),raw_members=934,gzip_parts=936,changed_material_claims=0)))


if __name__=='__main__':main()
