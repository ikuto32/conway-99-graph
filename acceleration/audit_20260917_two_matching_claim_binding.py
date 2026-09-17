"""Bind the independent exact two-coordinate bound to its precise exclusion statement."""
from datetime import datetime,timezone
import json
from pathlib import Path
import subprocess
import sys
import audit_20260917_partial_matching as h

root=h.ROOT
p=root/'acceleration/results/20260917_independent_review/two_matching_solve_bound.json'
h.require(h.digest(p)=='adf254892686dab05f0317b9ecec963b1b98eee8f9f8ccee129b05ebf6145065','independent audit pin')
a=json.loads(p.read_bytes());h.require(a['conditional_family_exclusion']is True and a['exact_bound']['numerator']==469399553 and a['exact_bound']['denominator']==1048576,'exact positive support bound')
doc=root/'acceleration/results/20260917_two_matching_moments/CANDIDATE_TWO_COORDINATE_EXCLUSION.md'
record=dict(status='INDEPENDENT_TWO_COORDINATE_EXCLUSION_CLAIM_BINDING_PASS',claim_id='C-PARTIAL-K-TWO-COORDINATE-EXCLUSION',claim_revision=1,recommendation='VERIFIED',statement='For every symmetric binary zero-diagonal 99-vertex adjacency matrix retaining the fixed189-edge root scaffold and156fixedK edges while respecting the prescribed absences in the frozen two-coordinate manifest, the equation A^2=12I-A+2J fails. Only the120freed same-sign-coordinate rootgroup0 edges and1680disjoint-support edges may vary.',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(root),inputs_sha256={h.key(v):h.digest(v)for v in(p,doc,Path(__file__),Path(h.__file__))},dependencies=[dict(id='C-PARTIAL-K-TWO-COORDINATE-DOMAINS',revision=1,relation='coverage'),dict(id='C-PARTIAL-K-TWO-COORDINATE-FULL-MOMENT-ENCODING',revision=1,relation='uses_result')],written_review='Read frozen CANDIDATE_TWO_COORDINATE_EXCLUSION.md in full. Its exact156fixedK/prescribedzero/two-sign rootgroup0 scope and89308 original domain population match the independent scope and complete-model reviews. Direct-neighborhood integer checking reproduced all84maxima and positive469399553/1048576, so the necessary zero-moment embedding contradicts the bound. No converse encoding or solver feasibility premise is used.',artifact_review_outcome='PASS',target_resolution='UNKNOWN',external_peer_review=False,limitations=['Conditional fixed-family exclusion, not an unrestricted nonexistence proof.','No matching-configuration count or target-wide coverage denominator is asserted in this approval.'])
out=root/'acceleration/results/20260917_independent_review/two_matching_exclusion_claim_binding.json'
with out.open('x')as f:json.dump(record,f,indent=2)
print(record['status'],h.digest(out))
