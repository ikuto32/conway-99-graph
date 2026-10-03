"""One literal editorial attribute suffix; preserve the entire old prefix."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
out = root / 'acceleration/results/20261003_wave39_attribute_plan01'
out.mkdir(parents=True, exist_ok=False)
path = root / '.gitattributes'
before = path.read_bytes()
expected = '4c5232096640a5308943cb6f18d10402a0528102c5d0e96d09e662a290cad35a'
assert hashlib.sha256(before).hexdigest() == expected
names = ['docs/CANDIDATE_20261003_TRIANGLE_INCIDENCE_LOW_WEIGHTS_V1.md',
         'docs/RESEARCH_20261003_THIRTYNINTH_WAVE.md']
suffix = ('\n# Exact wave39 three-claim evidence and milestone bytes.\n'
          + ''.join('/' + name + ' -text\n' for name in names)).encode('utf8')
assert all(('/' + name + ' -text').encode() not in before for name in names)
(out / 'gitattributes.before').write_bytes(before)
(out / 'proposed_suffix.txt').write_bytes(suffix)
after = before + suffix
path.write_bytes(after)
assert path.read_bytes()[:len(before)] == before
record = dict(timestamp=datetime.now(timezone.utc).isoformat(),
              command=[sys.executable, *sys.argv], cwd=str(root),
              source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              before_sha256=expected, before_bytes=len(before),
              after_sha256=hashlib.sha256(after).hexdigest(),
              suffix_sha256=hashlib.sha256(suffix).hexdigest(),
              exact_overrides=names, preserved_entire_prefix=True,
              scientific_launched=False, ledger_changed=False, index_changed=False)
with (out / 'proposal.json').open('x', encoding='utf8', newline='\n') as stream:
    json.dump(record, stream, indent=2)
    stream.write('\n')
print(json.dumps(record))
