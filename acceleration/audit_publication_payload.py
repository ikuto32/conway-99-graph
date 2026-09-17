"""Inventory an exact proposed public commit; report matches without their values.

This is a disclosure review aid, not a guarantee or a credential detector with
perfect coverage. It never prints matching data and does not modify the commit.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import yaml


def git(*args):
    return subprocess.check_output(['git',*args])


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base',required=True);p.add_argument('--commit',required=True)
    p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    if a.out.exists():raise ValueError('Preserve prior review')
    base=git('rev-parse',a.base).decode().strip();commit=git('rev-parse',a.commit).decode().strip()
    paths=git('diff','--name-only',base,commit).decode().splitlines()
    patterns={
        'private_key':rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----',
        'github_token':rb'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})\b',
        'openai_token':rb'\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{32,}\b',
        'aws_access_key':rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b',
        'credential_url':rb'https?://[^/\s:@]+:[^/\s@]+@',
    }
    records=[]
    for path in paths:
        raw=git('show',f'{commit}:{path}')
        forbidden=any(part in ('.env','.deps','.ortools','.venv','.git','.codex','.agents') for part in Path(path).parts)
        forbidden|=Path(path).suffix.lower() in ('.exe','.dll','.pyd','.bin','.db','.sqlite')
        records.append(dict(path=path,bytes=len(raw),sha256=sha256(raw).hexdigest(),
            forbidden_path=forbidden,pattern_names=[name for name,pattern in patterns.items() if re.search(pattern,raw)]))
    ledger=yaml.safe_load(git('show',f'{commit}:CLAIMS.yaml'))
    local=[dict(id=x['id'],path=x['path'],reason=x['unavailable_reason'],retrieval=x['retrieval']) for x in ledger['artifacts'] if x['availability']=='LOCAL_ONLY']
    report=dict(timestamp=datetime.now(timezone.utc).isoformat(),base_commit=base,proposed_commit=commit,
        source_script_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        command=['python',*__import__('sys').argv],cwd=str(Path.cwd()),
        changed_file_count=len(records),changed_bytes=sum(r['bytes'] for r in records),
        extension_counts=dict(Counter(Path(r['path']).suffix for r in records)),
        findings=[r for r in records if r['forbidden_path'] or r['pattern_names']],records=records,
        local_only_ledger_records=local,
        availability_semantics='LOCAL_ONLY records in this initial ledger explicitly say new local artifact, not yet published; no privacy classification is inferred from the label.',
        authorization='User requested a codex branch, draft PR in existing public repository, and commits of useful independently verified negative research results.',
        scope_review='Only newly generated graph/math experiment artifacts, independent checker sources, claim registry/CI/uv setup, and current research documentation were staged. PROMPT.md, old local caches, binaries and preexisting DRAT submodule edits excluded.',
        limitations=['Pattern screening can miss secrets; explicit path/content provenance review is also necessary.','This report does not override automatic approval review.'])
    with a.out.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps({k:report[k] for k in ('proposed_commit','changed_file_count','changed_bytes','extension_counts','findings')}))


if __name__=='__main__':main()
