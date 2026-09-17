"""Read-only, streaming checkpoint identity audit; never mathematical replay."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
from tqdm import tqdm

ROOT=Path(__file__).resolve().parents[1]


def sha(path):
    result=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1<<20),b''):
            result.update(block)
    return result.hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--checkpoint',type=Path,required=True)
    parser.add_argument('--expected-sha256',required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    if args.out.exists():
        raise ValueError('Preserve previous audit')
    started=datetime.now(timezone.utc).isoformat()
    actual=sha(args.checkpoint)
    if actual!=args.expected_sha256:
        raise ValueError('Checkpoint identity differs')
    data=json.loads(args.checkpoint.read_bytes())
    refs=data['referenced_files_sha256']
    rows=[]
    for name,expected in tqdm(refs.items(),desc='Checkpoint hashes',unit='artifact'):
        path=Path(name)
        if not path.is_absolute():
            path=ROOT/path
        try:
            observed=sha(path)
            rows.append(dict(path=name,expected_sha256=expected,observed_sha256=observed,
                status='MATCH' if observed==expected else 'CHANGED',bytes=path.stat().st_size))
        except OSError as exc:
            rows.append(dict(path=name,expected_sha256=expected,observed_sha256=None,
                status='UNAVAILABLE',reason=str(exc)))
    counts={status:sum(r['status']==status for r in rows) for status in ('MATCH','CHANGED','UNAVAILABLE')}
    report=dict(schema_version=1,started_at=started,finished_at=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True,cwd=ROOT).strip(),
        command=[sys.executable,*sys.argv],cwd=str(ROOT),python=sys.version,platform=platform.platform(),
        checkpoint_path=args.checkpoint.as_posix(),checkpoint_sha256=actual,
        declared_count=data['verified_referenced_file_count'],actual_count=len(refs),counts=counts,
        all_identities_match=counts['MATCH']==len(refs)==data['verified_referenced_file_count'],
        records=rows,checking_method='repeated hash identity check; no solver or mathematical audit replay',
        historical_verified_labels_promoted=False,source_script_sha256=sha(Path(__file__)))
    with args.out.open('x',encoding='utf-8') as stream:
        json.dump(report,stream,indent=2)
        stream.write('\n')
    print(json.dumps(dict(counts=counts,all_identities_match=report['all_identities_match'])))
    if not report['all_identities_match']:
        raise SystemExit(1)


if __name__=='__main__':
    main()
