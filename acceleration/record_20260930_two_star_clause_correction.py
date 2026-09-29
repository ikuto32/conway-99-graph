"""Preserve a line-ending audit failure and create a separate corrected checker."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json

ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'acceleration/audit_20260930_two_star_empty_domain_cut.py'
target=source.with_name('audit_20260930_two_star_empty_domain_cut_v2.py')
assert not target.exists()
raw=source.read_text(encoding='utf-8')
raw=raw.replace("/two_star_empty_domain_cut'","/two_star_empty_domain_cut_v2'")
old="need(clause==(' '.join(map(str,certificate['clause']))+' 0\\n').encode(),'raw clause bytes')"
new="need(len(clause.splitlines())==1 and [int(x) for x in clause.split()]==certificate['clause']+[0],'raw clause tokens and terminator')"
assert old in raw
target.write_text(raw.replace(old,new),encoding='utf-8',newline='\n')
report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),first_command='uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/audit_20260930_two_star_empty_domain_cut.py',first_result='ValueError: raw clause bytes',initial_verification_complete=False,reason='The producer wrote its single DIMACS clause with native CRLF. The initial checker incorrectly demanded LF-only. The original certificate and clause bytes remain unchanged.',original_checker_sha256=sha256(source.read_bytes()).hexdigest(),corrected_checker_sha256=sha256(target.read_bytes()).hexdigest(),clause_sha256='510a0ed62662f7d7ea9af420a29be6e52a2c43c1c6632e0f8a366453a40ea3a2',correction='Check exactly one line, all ordered signed literals and final zero using standard whitespace tokenization; preserve original raw byte hash.',development_execution_error='An attempted inline PowerShell correction command failed parsing before any file write; the immediate v2 launch therefore reported missing file. This recorder replaces that failed shell command; no mathematical evidence was changed.')
path=ROOT/'acceleration/results/20260930_independent_review/two_star_empty_domain_cut/failure_and_correction.json'
with path.open('x',encoding='utf-8',newline='\n') as stream:json.dump(report,stream,indent=2);stream.write('\n')
