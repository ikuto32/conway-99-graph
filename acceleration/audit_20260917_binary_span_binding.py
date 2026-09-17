"""Bind the checked affine membership witness without promoting producer rank metrics."""
from datetime import datetime,timezone
import json
from pathlib import Path
import subprocess
import sys
import audit_20260917_partial_matching as h

p=h.ROOT/'acceleration/results/20260917_independent_review/two_coordinate_binary_span.json'
h.require(h.digest(p)=='e503c548a9ba75799b7e94fe25bc6c5ab839fdd78c416676525daab5587b8a04','raw audit pin')
a=json.loads(p.read_bytes());h.require(a['status']=='INDEPENDENT_TWO_COORDINATE_BINARY_AFFINE_MEMBERSHIP_PASS'and a['witness_difference_columns_checked']==1837 and a['reference_columns_checked']==84,'membership review')
record=dict(status='INDEPENDENT_BINARY_AFFINE_MEMBERSHIP_CLAIM_BINDING_PASS',claim_id='C-PARTIAL-K-TWO-COORDINATE-BINARY-AFFINE-MEMBERSHIP',claim_revision=1,recommendation='VERIFIED',statement='Let b be the5370-row equality RHS and c_(u,i) the probability column of the frozen two-coordinate moment model over F2. Then r=b+sum_u c_(u,0) is in span{c_(u,i)+c_(u,0)}, witnessed by the1837 listed distinct global columns and their exact original IDs. All84 reference columns and1837 differences were independently checked.',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(h.ROOT),inputs_sha256={h.key(v):h.digest(v)for v in(p,Path(__file__),Path(h.__file__))},dependencies=[dict(id='C-PARTIAL-K-TWO-COORDINATE-DOMAINS',revision=1,relation='uses_result'),dict(id='C-PARTIAL-K-TWO-COORDINATE-FULL-MOMENT-ENCODING',revision=1,relation='uses_result')],review_method='Bind the exact independently reconstructed XOR witness, raw feature definition, failure controls and immutable input inventories in the reviewed report.',limitations=['No full basis rank or processed-column count is independently claimed.','Affine F2 membership does not produce one admissible star per center, a real nonnegative simplex solution, or a graph.','Compatible with positive real moment support bound excluding this exact family.'],target_resolution='UNKNOWN')
out=h.ROOT/'acceleration/results/20260917_independent_review/two_coordinate_binary_span_claim_binding.json'
with out.open('x')as f:json.dump(record,f,indent=2)
print(record['status'],h.digest(out))
