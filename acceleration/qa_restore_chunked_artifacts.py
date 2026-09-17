"""Positive and corrupted controls for the new chunk restoration implementation."""
from copy import deepcopy
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import restore_chunked_artifacts as restore


def main():
    root=Path(__file__).resolve().parents[1]
    folder=root/'build/replay_20260917/chunk_controls';folder.mkdir(parents=True,exist_ok=False)
    blobs=[b'alpha',b'bravo',b'charlie'];whole=b''.join(blobs)
    parts=[]
    for i,blob in enumerate(blobs):
        p=folder/f'part{i}'
        with p.open('xb') as f:f.write(blob)
        parts.append(dict(path=p.name,bytes=len(blob),sha256=hashlib.sha256(blob).hexdigest()))
    original=dict(schema_version=1,artifacts=[dict(source='restored.bin',source_bytes=len(whole),
                  source_sha256=hashlib.sha256(whole).hexdigest(),parts=parts)])
    def manifest(name,data):
        path=folder/(name+'.json')
        with path.open('x',encoding='utf-8') as f:json.dump(data,f)
        return path
    positive=manifest('positive',original)
    result=restore.restore(positive,root,folder/'positive')
    assert (folder/'positive/restored.bin').read_bytes()==whole
    controls=[dict(name='positive_ordered_parts',outcome='PASS')]
    try:restore.restore(positive,root,folder/'positive')
    except FileExistsError:controls.append(dict(name='overwrite',outcome='REJECT'))
    else:raise AssertionError('Overwrite accepted')
    for name,mutate in (
        ('wrong_part_hash',lambda a:a['parts'][0].update(sha256='0'*64)),
        ('wrong_part_size',lambda a:a['parts'][0].update(bytes=6)),
        ('wrong_whole_hash',lambda a:a.update(source_sha256='0'*64)),
        ('reversed_parts',lambda a:a['parts'].reverse()),
        ('missing_part',lambda a:a['parts'][0].update(path='absent')),
        ('duplicate_part',lambda a:a['parts'].append(a['parts'][0])),
        ('outside_destination',lambda a:a.update(source='../escape')),
        ('outside_input',lambda a:a['parts'][0].update(path='../escape')),
    ):
        data=deepcopy(original);mutate(data['artifacts'][0]);p=manifest(name,data)
        try:restore.restore(p,root,folder/name)
        except (ValueError,FileNotFoundError):controls.append(dict(name=name,outcome='REJECT'))
        else:raise AssertionError('Corrupted input accepted: '+name)
        assert not (folder/name/'restored.bin').exists()
    report=dict(status='CHUNK_RESTORE_PRODUCER_CONTROLS_PASS',timestamp=datetime.now(timezone.utc).isoformat(),
        source_sha256=restore.digest(root/'acceleration/restore_chunked_artifacts.py'),controls=controls,
        independent_verification=False,meaning='Imports restorer; engineering controls only')
    out=root/'acceleration/results/20260917_artifact_replay/chunk_controls.json';out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps(dict(status=report['status'],controls=len(controls))))


if __name__=='__main__':main()
