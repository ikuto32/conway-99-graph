"""Save exact, versioned primary literature bytes; execute no downloaded code."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import urllib.request

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    records = []
    for name, url in [('abstract.html','https://arxiv.org/abs/2608.19410v1'),
                      ('fulltext.html','https://arxiv.org/html/2608.19410v1'),
                      ('source.tar.gz','https://arxiv.org/src/2608.19410v1')]:
        row = dict(url=url, accessed_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
        try:
            req = urllib.request.Request(url, headers={'User-Agent':'Conway99-literature-audit/1.0'})
            with urllib.request.urlopen(req, timeout=30) as response:
                data = response.read(20*1024*1024+1)
                if len(data)>20*1024*1024:
                    raise ValueError('response exceeds declared byte ceiling')
                row.update(status=response.status, final_url=response.url,
                           headers=dict(response.headers), bytes=len(data))
            p = out/name
            p.write_bytes(data)
            row.update(path=p.as_posix(), sha256=sha(p), outcome='SAVED')
        except Exception as exc:
            row.update(outcome='ACCESS_FAILED', error=repr(exc))
        records.append(row)
    source = Path(__file__)
    spec = source.with_name(source.stem+'_spec.md')
    summary = dict(schema='VERSIONED_REIMBAYEV_SEVEN_ACCESS_V1',
                   status='LITERATURE_ACCESS_RECORD_ONLY', records=records,
                   inputs_sha256={source.as_posix():sha(source),spec.as_posix():sha(spec)},
                   mathematical_approval=False)
    (out/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False))

if __name__=='__main__':
    main()
