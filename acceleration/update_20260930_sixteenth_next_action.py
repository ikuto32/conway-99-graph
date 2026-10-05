"""Preserve both prechecked recorders; remove an action completed before freezing."""
from pathlib import Path
import hashlib, json
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
old = ROOT / 'acceleration/record_20260930_sixteenth_checkpoint_v2.py'
new = ROOT / 'acceleration/record_20260930_sixteenth_checkpoint_v3.py'
replacements = [
    ('Independently replay the separately executed cyclic-subfamily UNSAT trace and prepare the broader ordered coloring model for the same fixed Hadamard support; both belong to the next cohort.',
     'Prepare and independently audit the broader ordered coloring model for the remaining fixed Hadamard support, then run its exact factor search; this belongs to the next cohort.'),
    ('independently review the separately executed cyclic-subfamily UNSAT result, then test the broader coloring model on the same fixed Hadamard support with independently justified ordering of identical-support columns.',
     'prepare and independently audit the broader coloring model on the remaining fixed Hadamard support, then test it with independently justified ordering of identical-support columns.')
]
raw = old.read_bytes()
for before, after in replacements:
    assert raw.count(before.encode()) == 1
    raw = raw.replace(before.encode(), after.encode())
with new.open('xb') as stream: stream.write(raw)
out = ROOT / 'acceleration/results/20260930_sixteenth_checkpoint_preexecution_update_v3'
out.mkdir(exist_ok=False)
record = dict(timestamp=datetime.now(timezone.utc).isoformat(), old_path=old.relative_to(ROOT).as_posix(),
              old_sha256=hashlib.sha256(old.read_bytes()).hexdigest(), new_path=new.relative_to(ROOT).as_posix(),
              new_sha256=hashlib.sha256(raw).hexdigest(), replacements=replacements,
              reason='The future-cohort cyclic proof replay completed before the sixteenth checkpoint was generated. Only next-action prose changes; cohort claims and counts remain frozen.',
              completed_replay='acceleration/results/20260930_independent_review/hadamard_cyclic_unsat/summary.json',
              completed_replay_sha256='83029350b25523c015dfe916d8056324c0970021d2b024d68941dd41fb8c2b70')
with (out/'update.json').open('x',encoding='utf-8',newline='\n') as stream: json.dump(record,stream,indent=2);stream.write('\n')
print(json.dumps(record))
