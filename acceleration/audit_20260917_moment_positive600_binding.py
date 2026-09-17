"""Preserve original audit and clarify its necessary-encoding dependency relation."""
from datetime import datetime,timezone
import json
from pathlib import Path
import subprocess
import sys
import audit_20260917_partial_matching as h

root=h.ROOT
report=root/'acceleration/results/20260917_independent_review/moment_positive600.json'
doc=root/'acceleration/results/20260917_partial_matching_moment_replay600/CANDIDATE_EXCLUSION.md'
h.require(h.digest(report)=='d435c7789bd2f181e3a870b2019ae309cdbf2d9530bc21b2d987d40671444bc8','audit pin')
a=json.loads(report.read_bytes())
h.require(a['status']=='INDEPENDENT_PARTIAL_K_POSITIVE_MOMENT_EXCLUSION_PASS'and a['exact_bound']['reduced']=='9227079/16384','exact audit')
record=dict(status='INDEPENDENT_PARTIAL_K_POSITIVE_MOMENT_CLAIM_BINDING_PASS',claim_id='C-PARTIAL-K-ONE-COORDINATE-EXCLUSION',claim_revision=1,recommendation='VERIFIED',statement=a['statement'],timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(root),inputs_sha256={h.key(p):h.digest(p)for p in(report,doc,Path(__file__),Path(h.__file__))},dependency_metadata_correction=dict(original_value='encoding_equivalence',correct_relation='uses_result',claim_id='C-PARTIAL-K-FULL-MOMENT-ENCODING',revision=1,reason='That dependency establishes a necessary zero-objective embedding, not an equivalence or converse. Original raw audit bytes preserved; its mathematical statement and derivation already used only necessity.'),dependencies=[dict(id='C-PARTIAL-K-ONE-COORDINATE-DOMAINS',revision=1,relation='coverage'),dict(id='C-PARTIAL-K-FULL-MOMENT-ENCODING',revision=1,relation='uses_result')],written_review='Read the frozen CANDIDATE_EXCLUSION.md in full. Its fixed162/prescribedabsence scope, 54478 original unfiltered stars, necessary zero-objective implication, arbitrary-weight support formula, exact fraction and target limitations agree with independent derivation and raw artifact check. Numerical objective is not used as proof.',artifact_review_outcome='PASS',mathematical_result_changed=False,target_resolution='UNKNOWN',external_peer_review=False)
out=root/'acceleration/results/20260917_independent_review/moment_positive600_claim_binding.json'
with out.open('x')as f:json.dump(record,f,indent=2)
print(record['status'],h.digest(out))
