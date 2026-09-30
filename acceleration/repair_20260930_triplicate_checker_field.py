"""Preserve the failed audit and correct its raw artifact field name."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,sys,subprocess
root=Path(__file__).resolve().parents[1]
old=root/'acceleration/audit_20260930_hadamard_triplicate_counts.py'
new=root/'acceleration/audit_20260930_hadamard_triplicate_counts_v2.py'
raw=old.read_bytes();updated=raw
replacements=[("C=raw['C36']","C=raw['core_adjacency']"),
              ('acceleration/audit_20260930_hadamard_triplicate_counts.py','acceleration/audit_20260930_hadamard_triplicate_counts_v2.py')]
for before,after in replacements:
    assert updated.count(before.encode())==1
    updated=updated.replace(before.encode(),after.encode())
with new.open('xb')as stream:stream.write(updated)
out=root/'acceleration/results/20260930_independent_review/hadamard_triplicate_counts'
with(out/'failed_source.py').open('xb')as stream:stream.write(raw)
receipt=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
             command=[sys.executable,*sys.argv],cwd=str(root),old_source_sha256=hashlib.sha256(raw).hexdigest(),
             new_source_sha256=hashlib.sha256(updated).hexdigest(),replacements=replacements,
             reason='The checker used C36 while the authenticated artifact names this field core_adjacency. Failure occurred before candidate math checks. Original checker and failure retained.',
             mathematical_claim_changed=False)
with(out/'correction.json').open('x',encoding='utf-8',newline='\n')as stream:json.dump(receipt,stream,indent=2);stream.write('\n')
print(json.dumps(receipt))
