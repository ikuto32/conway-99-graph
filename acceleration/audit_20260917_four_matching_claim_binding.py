"""Bind the independent exact four-coordinate bound to its precise exclusion statement."""
from datetime import datetime,timezone
import json
from pathlib import Path
import subprocess
import sys
import audit_20260917_partial_matching as h

root=h.ROOT
p=root/'acceleration/results/20260917_independent_review/four_matching_filtered_run01_bound.json'
h.require(h.digest(p)=='6d8bba20e6d71c5538ed46008ce2676f8c573740adc5512d86bea6b7c93c835a','independent audit pin')
a=json.loads(p.read_bytes());h.require(a['conditional_family_exclusion']is True and a['exact_bound']['numerator']==275944444 and a['exact_bound']['denominator']==1048576,'exact positive support bound')
doc=root/'acceleration/results/20260917_four_matching_filtered_solve2400/run01/CANDIDATE_FOUR_COORDINATE_EXCLUSION.md'
record=dict(status='INDEPENDENT_FOUR_COORDINATE_EXCLUSION_CLAIM_BINDING_PASS',claim_id='C-PARTIAL-K-FOUR-COORDINATE-EXCLUSION',claim_revision=1,recommendation='VERIFIED',statement='For every symmetric binary zero-diagonal 99-vertex adjacency matrix retaining the fixed189-edge root scaffold and144fixedK edges while respecting the prescribed absences in the frozen four-coordinate manifest, the equation A^2=12I-A+2J fails. Only the240freed same-sign-coordinate rootgroups0and1 edges and1680disjoint-support edges may vary.',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(root),inputs_sha256={h.key(v):h.digest(v)for v in(p,doc,Path(__file__),Path(h.__file__))},dependencies=[dict(id='C-PARTIAL-K-FOUR-COORDINATE-DOMAINS',revision=1,relation='coverage'),dict(id='C-PARTIAL-K-FOUR-COORDINATE-NEIGHBORHOOD-MATCHING-FILTER',revision=1,relation='uses_result'),dict(id='C-PARTIAL-K-FOUR-COORDINATE-MATCHING-FILTERED-MOMENT-ENCODING',revision=1,relation='uses_result')],written_review='Read frozen CANDIDATE_FOUR_COORDINATE_EXCLUSION.md in full. Its exact144fixedK/prescribedzero/four-sign rootgroups0and1 scope matches the independent complete-domain review. Every original290460choice is either among59581sound matching rejections or230879retained choices, with per-center exact original-ID complements freshly checked. Direct-neighborhood integer checking reproduced all84maxima over retained columns and positive275944444/1048576, so the necessary filtered zero-moment embedding contradicts the bound. No converse encoding or solver feasibility premise is used.',artifact_review_outcome='PASS',target_resolution='UNKNOWN',external_peer_review=False,limitations=['Conditional fixed-family exclusion, not an unrestricted nonexistence proof.','No matching-configuration count or target-wide coverage denominator is asserted in this approval.'])
out=root/'acceleration/results/20260917_independent_review/four_matching_exclusion_claim_binding.json'
with out.open('x')as f:json.dump(record,f,indent=2)
print(record['status'],h.digest(out))
