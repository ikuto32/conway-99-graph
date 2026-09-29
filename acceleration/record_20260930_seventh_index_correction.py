"""Preserve initial publication-byte veto; inspect every staged mismatch."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'acceleration/results/20260930_seventh_staging_correction'
out.mkdir(parents=True,exist_ok=False)
names=[p for p in subprocess.check_output(['git','diff','--cached','--name-only','-z'],cwd=ROOT).decode().split('\0') if p]
raw=subprocess.run(['git','cat-file','--batch'],input=''.join(':'+n+'\n' for n in names).encode(),cwd=ROOT,capture_output=True,check=True).stdout
offset=0; mismatches=[]
for name in names:
    end=raw.index(b'\n',offset);header=raw[offset:end].split();size=int(header[2]);blob=raw[end+1:end+1+size];offset=end+size+2
    original=(ROOT/name).read_bytes()
    if original!=blob:
        mismatches.append(dict(path=name,index_sha256=hashlib.sha256(blob).hexdigest(),original_sha256=hashlib.sha256(original).hexdigest(),only_crlf_normalization=original.replace(b'\r\n',b'\n')==blob))
        (out/(str(len(mismatches))+'_original_bytes.bin')).write_bytes(original)
assert offset==len(raw)
source=ROOT/'acceleration/stage_20260930_seventh_evidence.py'
(out/'stage_rejected_v1.py.txt').write_bytes(source.read_bytes())
report=dict(timestamp=datetime.now(timezone.utc).isoformat(),status='PUBLICATION_BYTE_CHECK_VETO',reason='Initial staging check rejected .gitignore Git newline normalization before any commit. Complete follow-up comparison is recorded here.',staged_paths_examined=len(names),mismatches=mismatches,rejected_source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),mathematical_claims_affected=False,correction_plan='Normalize only current .gitignore infrastructure; preserve frozen research Markdown bytes with exact-path -text overrides. Do not edit any bound source/proof/audit bytes. Recheck the complete index before commit.')
(out/'summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'mismatches':mismatches,'count':len(names)}))
