"""Root-owned explicit incremental evidence closure; no index or math mutation."""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
import yaml
from command_deadline import CommandDeadline
from audit_20261002_wave31_transition_v1 import UniqueLoader

ROOT = Path(__file__).resolve().parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def path(name):
    need(type(name) is str and name and not any(c in name for c in '\\\n\r\0'), 'literal relative path')
    p = PurePosixPath(name)
    need(not p.is_absolute() and '..' not in p.parts and not name.startswith('.git/'), 'bounded path')
    need(name.startswith(('acceleration/', 'docs/')) or name in
         ('CLAIMS.yaml','README.md','ACTIVE_RESEARCH.md','.gitattributes','.github/workflows/claims.yml','pyproject.toml','uv.lock'), 'research namespace')
    answer = (ROOT/name).resolve()
    need(answer.is_relative_to(ROOT), 'bounded resolved path')
    return answer


def sha(p):
    with p.open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--seconds',type=float,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--ledger-sha256',required=True)
    ap.add_argument('--before',required=True)
    ap.add_argument('--before-sha256',required=True)
    ap.add_argument('--extra',action='append',default=[])
    ap.add_argument('--package',action='append',default=[])
    ap.add_argument('--package-sha256',action='append',default=[])
    args = ap.parse_args()
    d = CommandDeadline(args.seconds,allocation_reason='Exact new ledger artifact closure and named completed roots;240outer200worker20reserve, no science/index mutation')
    out = args.out.resolve()
    need(out.is_relative_to(ROOT), 'bounded output')
    out.mkdir(parents=True,exist_ok=False)
    need(len(args.package)==len(args.package_sha256), 'paired package pins')
    origins = defaultdict(set)
    expected = {}
    def tick():
        need(not d.status()['stop_required'] and d.status()['remaining_seconds']>20,'not completed within the allocated budget')
    def add(name,origin,identity=None):
        path(name)
        origins[name].add(origin)
        if identity is not None:
            need(name not in expected or expected[name]==identity,'consistent exact identity')
            expected[name]=identity
    def read(name,identity):
        tick()
        need(sha(path(name))==identity,'exact pinned metadata')
        add(name,'pinned metadata',identity)
        return json.loads(path(name).read_bytes())
    def ledger(name,identity):
        tick()
        need(sha(path(name))==identity,'exact ledger identity')
        return yaml.load(path(name).read_text(encoding='utf8'),Loader=UniqueLoader)
    baseline = ledger(args.before,args.before_sha256)
    current = ledger('CLAIMS.yaml',args.ledger_sha256)
    need(len(baseline['claims'])==337 and current['claims'][:337]==baseline['claims'],'unchanged exact337 material baseline')
    need(current['artifacts'][:len(baseline['artifacts'])]==baseline['artifacts'],'unchanged baseline availability/evidence')
    need(len(current['claims'])>337,'actual new scoped claims')
    for artifact in current['artifacts'][len(baseline['artifacts']):]:
        if artifact['path']:
            add(artifact['path'],'new exact claim artifact',artifact['sha256'])
    packages = [read(name,identity) for name,identity in zip(args.package,args.package_sha256)]
    packaged = {}
    for package in packages:
        for record in package['records']:
            name=record['raw_path']
            need(name not in packaged,'distinct packaged originals')
            packaged[name]=record
            for part in record['parts']:
                add(part['path'],'lossless public payload',part['gzip_sha256'])
    controls=[]
    for bad in ('../outside','/absolute','acceleration/../../outside','acceleration\\mixed','private.txt','.git/config'):
        try:
            path(bad)
        except ValueError:
            controls.append(bad)
        else:
            raise ValueError('unbounded control accepted')
    for name in args.extra:
        member=path(name)
        need(member.exists(),'named extra exists')
        if member.is_dir():
            for item in member.rglob('*'):
                if item.is_file():
                    add(item.relative_to(ROOT).as_posix(),'named completed result root')
        else:
            add(name,'named preserved source/document')
    for name in ('CLAIMS.yaml',Path(__file__).relative_to(ROOT).as_posix(),
                 'acceleration/freeze_20261003_wave37_evidence_v1_spec.md'):
        add(name,'root metadata')
    index=Path(subprocess.check_output(['git','rev-parse','--git-path','index'],cwd=ROOT,text=True).strip())
    index=index if index.is_absolute() else ROOT/index
    index_sha=sha(index)
    records=[]
    omitted=[]
    for name in sorted(origins):
        tick()
        member=path(name)
        need(member.is_file(),'exact member exists')
        size=member.stat().st_size
        if name in packaged:
            p=packaged[name]
            need(size==p['raw_bytes'] and (name not in expected or expected[name]==p['raw_sha256']),'packaged original exact pin/size')
            omitted.append(dict(path=name,sha256=p['raw_sha256'],bytes=size,reason='Losslessly represented in separately pinned public package; no duplicate raw Git blob.',fresh_hash_checked=False))
            continue
        need(size<50*1024**2,'declared direct file bound; large artifact requires new lossless package')
        identity=sha(member)
        need(name not in expected or identity==expected[name],'exact bound member bytes '+name)
        records.append(dict(path=name,sha256=identity,bytes=size,origins=sorted(origins[name])))
    need(sha(index)==index_sha and sha(ROOT/'CLAIMS.yaml')==args.ledger_sha256,'no index/live ledger mutation')
    self_paths=[(out/'manifest.json').relative_to(ROOT).as_posix(),(out/'stage_paths.nul').relative_to(ROOT).as_posix()]
    names=sorted({r['path'] for r in records}|set(self_paths))
    (out/'stage_paths.nul').write_bytes(b''.join(name.encode('utf8')+b'\0' for name in names))
    report=dict(schema='WAVE37_INCREMENTAL_EXACT_EVIDENCE_ALLOWLIST_V1',timestamp=datetime.now(timezone.utc).isoformat(),
                source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                command=[sys.executable,*sys.argv],cwd=str(ROOT),source_sha256=sha(Path(__file__)),
                before_ledger_sha256=args.before_sha256,ledger_sha256=args.ledger_sha256,current_claims=len(current['claims']),
                previous_claims=337,records=records,direct_record_count=len(records),direct_bytes=sum(r['bytes'] for r in records),
                omitted=omitted,packages=dict(zip(args.package,args.package_sha256)),self_metadata_paths=self_paths,
                stage_paths_sha256=sha(out/'stage_paths.nul'),stage_paths_count=len(names),controls=controls,
                index_mutated=False,ledger_mutated=False,scientific_launched=False,mathematical_replay=False,
                availability_changed=False,deadline=d.status(),
                limitations=['Explicit new claim evidence and named completed roots only; no broad untracked scan.',
                             'Package omission reuses pinned identity/size, not a fresh original hash or independent byte recovery.',
                             'Separate exact mathematical/impact/recovery/publication reports are required; this is allowlisting only.'])
    with (out/'manifest.json').open('x',encoding='utf8',newline='\n') as stream:
        json.dump(report,stream,indent=2)
        stream.write('\n')
    print(json.dumps({key:report[key] for key in ('current_claims','direct_record_count','direct_bytes','stage_paths_count')}))


if __name__=='__main__':
    main()
