"""Bind the completed independent row audit to its precise claim revision."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_independent_review/triangle_capacity_q1_rows/'
REPORT=B+'summary.json'
EXPECTED='1116581ea1b789d8972ca569d87d1b60e54ef777bee26759b59dd9e53eed6c5e'
def h(p):return sha256((ROOT/p).read_bytes()).hexdigest()
assert h(REPORT)==EXPECTED
report=json.loads((ROOT/REPORT).read_bytes())
assert report['status']=='INDEPENDENT_TRIANGLE_CAPACITY_Q1_ROW_ARTIFACTS_PASS'
assert report['row_outcomes']=={'UNSAT':12}
assert [r['vertex']for r in report['rows']]==list(range(27,39))
assert sum(r['details']['nodes']for r in report['rows'])==2774
for p,digest in report['inputs_sha256'].items():assert h(p)==digest,(p,'changed input')
paths=[REPORT,'acceleration/audit_20260930_triangle_capacity_q1_rows.py','docs/AUDIT_20260930_TRIANGLE_CAPACITY_Q1_ROWS.md',
       'acceleration/results/20260930_independent_review/triangle_q1_capacity_sat_binding/summary.json',
       'acceleration/results/20260930_capacity_q1_rows/summary.json','acceleration/results/20260930_capacity_q1_rows/raw99.json',
       Path(__file__).relative_to(ROOT).as_posix()]
now=datetime.now(timezone.utc).isoformat()
record=dict(schema='INDEPENDENT_CLAIM_REVISION_BINDING_V1',claim_id='C-FIXED-TRIANGLE-CAPACITY-Q1-ROW-EXCLUSION',claim_revision=1,
 statement='For the exact fixed39 triangle core, canonical C0 and capacity-compatible Q1 in the hash-bound raw99 artifact, each of the twelve vertices27..38 has no binary60-entry B-neighbour row satisfying the independently necessary degree10,24 exact common-neighbour equations and108 pair-cap incompatibilities. Consequently no complete99-vertex graph extending this single fixed Q1 and core satisfies A^2=12I-A+2J.',
 kind='exclusion',basis=['DERIVED','COMPUTED'],recommendation='VERIFIED',review_state='CLEAR',
 scope='One exact fixed-Q1 configuration. Twelve independently checked empty necessary row domains are twelve explanations of the same exclusion, not twelve disjoint graph families.',
 assumptions=['Exact raw core/C0/Q1 fixed entries from the bound raw99 artifact.','Every target extension is symmetric binary with zero diagonal and satisfies the integer target identity.','No nontrivial target automorphism or universal containment of this core is assumed.'],
 dependencies=[dict(id='C-FIXED-TRIANGLE-CAPACITY-COMPATIBLE-Q1-CONSTRUCTION',revision=1,relation='uses_result')],
 mathematical_derivation=dict(path='docs/AUDIT_20260930_TRIANGLE_CAPACITY_Q1_ROWS.md',sha256=h('docs/AUDIT_20260930_TRIANGLE_CAPACITY_Q1_ROWS.md'),relation='derived_from',checked='Necessary constraints follow entrywise from the integer target identity; complete tree checking uses opposite-value entailment and both binary branches.'),
 verification=dict(claim_revision=1,verifier='/root/state_literature_audit',method='independent_artifact_check',timestamp=report['timestamp'],outcome='PASS',audit_path=REPORT,audit_sha256=EXPECTED,scope='All9801rawentries,576prescribedGram entries,all12constraint lists and every node/force/leaf in12complete UNSAT trees; calibrated positive and50fresh corruption controls.'),
 counts=dict(distinct_fixed_configurations_excluded=1,distinct_row_domains_checked=12,binary_variables_per_domain=60,complete_tree_nodes=2774,binary_splits=1381,contradiction_leaves=1393,forced_batches=9627,individually_checked_forced_bits=22560,fresh_corrupt_controls_rejected=50),
 limitations=['No exclusion of all capacity-compatible Q1 factors or of the whole core family.','The row proof uses only necessary target conditions; no claim that the constraints encode all completion conditions.','No satisfying-domain enumeration, target-wide denominator, novelty or external review claim.','No complete36factor or99graph is constructed.'],
 shared_components=report['shared_components'],inputs_sha256={p:h(p)for p in paths},artifact_availability='LOCAL_ONLY',target_resolution=False,external_review=False,
 created_at=now,updated_at=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version())
out=ROOT/(B+'claim_binding.json')
with out.open('x',encoding='utf-8',newline='\n')as f:json.dump(record,f,indent=2);f.write('\n')
print(json.dumps(dict(path=out.relative_to(ROOT).as_posix(),sha256=h(out.relative_to(ROOT).as_posix()))))
